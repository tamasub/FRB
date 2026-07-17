const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const assert = require('node:assert/strict');

const root = path.resolve(process.argv[2] || process.cwd());
function ap(...parts) {
  const p = path.join(root, ...parts);
  if (fs.existsSync(p)) return p;
  const w = path.join(root, parts.join('\\'));
  if (fs.existsSync(w)) return w;
  throw new Error(`missing ${parts.join('/')}`);
}

const pluginPath = ap('studio_overlays', 'gpt_fx_lab', 'plugins', 'fx_chart_viewer', 'plugin.js');
const profilePath = ap('studio_overlays', 'gpt_fx_lab', 'simulation', 'fx_simulation_run_profile_normal_plus_expansion_lite_v0_1.json');
const m5Path = ap('studio_overlays', 'gpt_fx_lab', 'data', 'fx_usdjpy_m5_t3_data_v0_1.json');
const d1Path = ap('studio_overlays', 'gpt_fx_lab', 'data', 'fx_usdjpy_d1_t3_data_v0_1.json');
const source = fs.readFileSync(pluginPath, 'utf8');
const idx = source.lastIndexOf('})();');
const hook = `window.__t={normalRuleLaneEntryDecision,normalizeAllRows,simulationRunDraftFromProfile,buildSimulationRunSnapshot,buildEmptySimulationTrace,compactSimulationContinuationSnapshot,validateSimulationRunDraft};`;
const ctx = { window: {}, console, setTimeout, clearTimeout, URL, structuredClone, Intl, Date, Math, JSON, Map, Set, Promise, requestAnimationFrame: cb => setTimeout(cb, 0) };
vm.runInNewContext(source.slice(0, idx) + hook + source.slice(idx), ctx, { filename: pluginPath });
const api = ctx.window.__t;
const profile = JSON.parse(fs.readFileSync(profilePath, 'utf8'));
assert.equal(api.validateSimulationRunDraft(profile).valid, true);
assert.equal(profile.m5_execution_policy.normal_entry_policy.same_direction_reconfirmation_policy, 'KEEP_ACTIVE_CONFIRMATION_UNTIL_BREAK_ENTRY_OR_MISS');

// Focused unit: a later same-direction confirmation must not replace the active WAITING_R2 anchor.
const oldConfirmation = { confirmation_id: 'up_first', direction: 'UP', confirmed_at: '2025-01-01 10:00', confirmed_at_ms: 1000, anchor_price: 100, breakout_threshold_price: 101 };
const newerConfirmation = { confirmation_id: 'up_later', direction: 'UP', confirmed_at: '2025-01-01 11:00', confirmed_at_ms: 2000, anchor_price: 105, breakout_threshold_price: 106 };
const portfolio = {
  trades: [], positions: [], used_dow_confirmation_ids: [],
  normal_entry_opportunities: [{
    opportunity_id: 'opp_first', dow_confirmation_id: 'up_first', direction: 'LONG',
    confirmed_at: '2025-01-01 10:00', confirmed_at_ms: 1000, created_at_reference_ms: 1000,
    anchor_id: 'low_first', anchor_price: 100, status: 'WAITING_R2'
  }],
  normal_anchor_lifecycle: {
    status: 'WAITING_R2', active_anchor_id: 'low_first', active_anchor_price: 100,
    active_confirmation_id: 'up_first', adopted_at_ms: 1000, last_retired_at_ms: null
  }
};
const focused = api.normalRuleLaneEntryDecision({
  portfolio, referenceMs: 3000, referenceTime: '2025-01-01 12:00', price: 100.7,
  direction: 'LONG', confirmationSide: 'LONG',
  normalFacts: { entry_direction_ready: true, cycle_guard_passed: true, h1_cycle_late: false, h4_t3_ready: true, h1_t3_ready: true, h4_h1_t3_aligned: true, m5_dow_aligned: true },
  m5State: { trend_detail: {} }, dowConfirmation: newerConfirmation,
  entryResolution: { status: 'RESOLVED_REFERENCE', anchor_id: 'low_later', anchor: { anchor_id: 'low_later', price: 105, dow_confirmation_id: 'up_later' } },
  entryAnchor: { anchor_id: 'low_later', price: 105, dow_confirmation_id: 'up_later' }, anchorPrice: 105,
  currentBar: { open: 100.5, high: 100.7, low: 100.4, close: 100.65 }, r2Touch: { touched: false },
  policy: profile.m5_execution_policy, minEntryLabel: 'R2', hsiNotReachedReasonCode: 'HSI_R2_NOT_REACHED',
  timeframeSnapshot: { timeframes: { H4: {}, H1: {} } }
});
assert.equal(focused.action, 'ENTRY');
assert.equal(focused.entry_opportunity.dow_confirmation_id, 'up_first');
assert.ok(Math.abs(focused.execution_candidate.entry_price - 100.534) < 1e-9);
assert.equal(focused.preserving_active_confirmation, true);
assert.equal(portfolio.normal_entry_opportunities.length, 1, '同方向後続Confirmationで新Opportunityを増やしてはいけません');

// Real-data integration: replay only the relevant M5 steps while keeping the full-history observation context.
(async () => {
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
    simulationRunReferenceSource: 'focused_real_data_step',
    hsiAnnotations: [],
    simulationTraceEvents: []
  };
  const from = rows.findIndex(row => row.datetime === '2025-11-17 12:50');
  const to = rows.findIndex(row => row.datetime === '2025-11-17 17:05');
  assert.ok(from >= 0 && to >= from);
  let finalSnapshot = null;
  for (let index = from; index <= to; index += 1) {
    const row = rows[index];
    state.simulationRunReferenceOverrideMs = new Date(row.datetime.replace(' ', 'T')).getTime() + 5 * 60 * 1000 - 1;
    const result = api.buildSimulationRunSnapshot(state, { skipTraceReplay: true });
    assert.ok(result.snapshot, `Snapshot作成失敗: ${row.datetime} ${(result.validation?.errors || []).join(' / ')}`);
    finalSnapshot = result.snapshot;
    const continuation = api.compactSimulationContinuationSnapshot(result.snapshot);
    state.simulationRunSnapshot = continuation;
    state.simulationTrace.run_snapshot = continuation;
  }
  const entry = (finalSnapshot.position_lifecycle.execution_events || []).find(event => event.rule_lane === 'NORMAL' && event.event_type === 'entry');
  assert.ok(entry, '対象範囲でNORMAL Entryがありません');
  assert.equal(entry.simulation_time, '2025-11-17 17:09');
  assert.ok(Math.abs(entry.execution.entry_anchor_price - 154.620) < 1e-9);
  assert.ok(Math.abs(entry.execution.entry_price - 155.154) < 1e-9);
  assert.ok(Math.abs(entry.execution.target_price - 155.322) < 1e-9);
  assert.equal(entry.execution.dow_confirmation_id, 'dow_confirm_m5_up_1763384399999_1b092549');
  assert.equal(entry.execution.entry_execution_mode, 'FIRST_R2_TOUCH_AFTER_CONFIRMATION');
  assert.ok(entry.reason_codes.includes('NORMAL_ACTIVE_CONFIRMATION_PRESERVED_UNTIL_BREAK_OR_ENTRY'));
  console.log('PASS normal_active_confirmation_r2_v0_24_1');
  console.log(`${entry.simulation_time} anchor=${entry.execution.entry_anchor_price} entry=${entry.execution.entry_price} target=${entry.execution.target_price}`);
})().catch(error => {
  console.error(error);
  process.exitCode = 1;
});
