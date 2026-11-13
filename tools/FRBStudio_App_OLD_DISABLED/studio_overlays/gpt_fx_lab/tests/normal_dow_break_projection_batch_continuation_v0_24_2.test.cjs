const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const assert = require('node:assert/strict');

const root = path.resolve(process.argv[2] || process.cwd());
function artifactPath(...parts) {
  const p = path.join(root, ...parts);
  if (fs.existsSync(p)) return p;
  const w = path.join(root, parts.join('\\'));
  if (fs.existsSync(w)) return w;
  throw new Error(`missing ${parts.join('/')}`);
}

const pluginPath = artifactPath('studio_overlays', 'gpt_fx_lab', 'plugins', 'fx_chart_viewer', 'plugin.js');
const profilePath = artifactPath('studio_overlays', 'gpt_fx_lab', 'simulation', 'fx_simulation_run_profile_normal_plus_expansion_lite_v0_1.json');
const m5Path = artifactPath('studio_overlays', 'gpt_fx_lab', 'data', 'fx_usdjpy_m5_t3_data_v0_1.json');
const d1Path = artifactPath('studio_overlays', 'gpt_fx_lab', 'data', 'fx_usdjpy_d1_t3_data_v0_1.json');

const source = fs.readFileSync(pluginPath, 'utf8');
const idx = source.lastIndexOf('})();');
const hook = `window.__t={normalizeAllRows,simulationRunDraftFromProfile,buildSimulationRunSnapshot,buildEmptySimulationTrace,compactBatchSimulationContinuationSnapshot,validateSimulationRunDraft};`;
const ctx = { window: {}, console, setTimeout, clearTimeout, URL, structuredClone, Intl, Date, Math, JSON, Map, Set, Promise, requestAnimationFrame: cb => setTimeout(cb, 0) };
vm.runInNewContext(source.slice(0, idx) + hook + source.slice(idx), ctx, { filename: pluginPath });
const api = ctx.window.__t;

const profile = JSON.parse(fs.readFileSync(profilePath, 'utf8'));
assert.equal(api.validateSimulationRunDraft(profile).valid, true);

const m5 = JSON.parse(fs.readFileSync(m5Path, 'utf8'));
const d1 = JSON.parse(fs.readFileSync(d1Path, 'utf8'));
const rows = api.normalizeAllRows(m5);
const state = {
  simulationSource: m5,
  simulationAllRows: rows,
  upperMapSource: d1,
  upperMapAllRows: api.normalizeAllRows(d1),
  simulationRunDraft: api.simulationRunDraftFromProfile(profile),
  windowStart: 0,
  windowSize: rows.length,
  chartLayout: 'm5_execution',
  upperTimeframe: 'H1',
  upperConfirmBars: 7,
  dayConfirmBars: 45,
  weekConfirmBars: 20,
  confirmBars: 20,
  upperWarmupBars: 200,
  simulationTrace: api.buildEmptySimulationTrace(m5),
  simulationRunSnapshot: null,
  simulationRunReferenceOverrideMs: null,
  simulationRunReferenceSource: 'batch_continuation_regression',
  hsiAnnotations: [],
  simulationTraceEvents: []
};

const accumulatedEvents = [];
const accumulatedEventIds = new Set();

function step(index) {
  const row = rows[index];
  state.simulationRunReferenceOverrideMs = new Date(row.datetime.replace(' ', 'T')).getTime() + 5 * 60 * 1000 - 1;
  const result = api.buildSimulationRunSnapshot(state, { skipTraceReplay: true });
  assert.ok(result.snapshot, `snapshot failed ${index} ${row.datetime}: ${(result.validation?.errors || []).join(' / ')}`);
  for (const event of result.snapshot.position_lifecycle?.execution_events || []) {
    const eventId = String(event?.event_id || '');
    if (!eventId || accumulatedEventIds.has(eventId)) continue;
    accumulatedEventIds.add(eventId);
    accumulatedEvents.push(event);
  }
  const continuation = api.compactBatchSimulationContinuationSnapshot(result.snapshot);
  state.simulationRunSnapshot = continuation;
  state.simulationTrace.run_snapshot = continuation;
  return result.snapshot;
}

// Full Dataset開始直後に作られる最初のDown Confirmation / WAITING_R2を再現。
let snapshot = step(100); // 2025-10-28 14:30
let portfolio = snapshot.position_lifecycle.portfolio;
assert.equal(portfolio.normal_anchor_lifecycle.status, 'WAITING_R2');
const firstConfirmationId = portfolio.normal_anchor_lifecycle.active_confirmation_id;
assert.ok(firstConfirmationId);

// その後のREVERSAL_WATCHで、Dow Trend側の崩壊事実がTimeframe Stateへ投影され、
// Batch continuationの旧WAITING_R2が失効しなければならない。
snapshot = step(140); // 2025-10-28 17:50
portfolio = snapshot.position_lifecycle.portfolio;
const m5State = snapshot.timeframe_states.timeframes.M5;
assert.equal(m5State.trend_state, 'REVERSAL_WATCH');
assert.ok(m5State.trend_detail.normal_dow_structure_break, 'normal_dow_structure_breakがTimeframe Stateへ投影されていません');
const expired = (portfolio.normal_entry_opportunities || []).find(item => item.dow_confirmation_id === firstConfirmationId);
assert.equal(expired?.status, 'EXPIRED');
assert.equal(expired?.terminal_reason_code, 'NORMAL_DOW_STRUCTURE_BROKEN_BEFORE_ENTRY');
assert.equal(portfolio.normal_anchor_lifecycle.status, 'AWAITING_NEW_DOW_CONFIRMATION');
assert.equal(portfolio.normal_anchor_lifecycle.active_confirmation_id, null);

// 重要地点だけを進め、崩壊後の新ConfirmationからNORMAL / Expansion-Liteが復帰することを確認。
step(160); // 2025-10-28 19:30
for (let i = 455; i <= 472; i += 1) snapshot = step(i);
const events = accumulatedEvents;
const normalEntry = events.find(event => event.rule_lane === 'NORMAL' && event.event_type === 'entry');
const liteEntry = events.find(event => event.rule_lane === 'EXPANSION_LITE' && event.event_type === 'entry');
const liteAddOn = events.find(event => event.rule_lane === 'EXPANSION_LITE' && event.event_type === 'add_on');
assert.ok(normalEntry, 'Batch continuation後にNORMAL Entryが復帰していません');
assert.ok(liteEntry, 'Batch continuation後にEXPANSION_LITE Entryが復帰していません');
assert.ok(liteAddOn, 'Batch continuation後にEXPANSION_LITE Add-onが復帰していません');
assert.equal(normalEntry.simulation_time, '2025-10-29 21:04');
assert.equal(liteEntry.simulation_time, '2025-10-29 21:39');
assert.equal(liteAddOn.simulation_time, '2025-10-29 21:44');

console.log('PASS normal_dow_break_projection_batch_continuation_v0_24_2');
console.log(`expired=${firstConfirmationId} normal=${normalEntry.simulation_time} lite=${liteEntry.simulation_time} add_on=${liteAddOn.simulation_time}`);
