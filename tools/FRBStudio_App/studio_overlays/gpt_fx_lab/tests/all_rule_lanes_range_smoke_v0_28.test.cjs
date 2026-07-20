const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const assert = require('node:assert/strict');

const root = path.resolve(process.argv[2] || process.cwd());
function artifactPath(...parts) {
  const normalized = path.join(root, ...parts);
  if (fs.existsSync(normalized)) return normalized;
  const windowsEntry = path.join(root, parts.join('\\'));
  if (fs.existsSync(windowsEntry)) return windowsEntry;
  throw new Error(`テスト対象ファイルが見つかりません: ${parts.join('/')}`);
}

const baseParts = ['studio_overlays', 'gpt_fx_lab'];
const pluginPath = artifactPath(...baseParts, 'plugins', 'fx_chart_viewer', 'plugin.js');
const profilePath = artifactPath(...baseParts, 'simulation', 'fx_simulation_run_profile_all_rule_lanes_v0_1.json');
const m5Path = artifactPath(...baseParts, 'data', 'fx_usdjpy_m5_t3_data_v0_1.json');
const d1Path = artifactPath(...baseParts, 'data', 'fx_usdjpy_d1_t3_data_v0_1.json');
const source = fs.readFileSync(pluginPath, 'utf8');
const hook = `window.__fxAllLaneSmoke = { normalizeAllRows, simulationRunDraftFromProfile, buildVisibleRangeSimulationRun, buildEmptySimulationTrace, validateSimulationRunDraft };`;
const closeIndex = source.lastIndexOf('})();');
assert.ok(closeIndex > 0, 'Plugin IIFE終端を検出できません。');
const context = {
  window: {}, console, setTimeout, clearTimeout, URL, structuredClone,
  Intl, Date, Math, JSON, Map, Set, Promise,
  requestAnimationFrame: callback => setTimeout(callback, 0)
};
vm.runInNewContext(source.slice(0, closeIndex) + hook + source.slice(closeIndex), context, { filename: pluginPath });
const api = context.window.__fxAllLaneSmoke;

(async () => {
  const profile = JSON.parse(fs.readFileSync(profilePath, 'utf8'));
  const validation = api.validateSimulationRunDraft(profile);
  assert.equal(validation.valid, true, validation.errors.join('\n'));
  const m5 = JSON.parse(fs.readFileSync(m5Path, 'utf8'));
  const d1 = JSON.parse(fs.readFileSync(d1Path, 'utf8'));
  const state = {
    simulationSource: m5,
    simulationAllRows: api.normalizeAllRows(m5),
    upperMapSource: d1,
    upperMapAllRows: api.normalizeAllRows(d1),
    simulationRunDraft: api.simulationRunDraftFromProfile(profile),
    windowStart: 500,
    windowSize: 40,
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
    simulationRunReferenceSource: 'visible_range_step',
    hsiAnnotations: [],
    simulationTraceEvents: []
  };
  const result = await api.buildVisibleRangeSimulationRun(state);
  assert.equal(result.validation.valid, true, (result.validation.errors || []).join(' / '));
  const engine = result.rangeRun?.final_snapshot?.position_lifecycle?.engine;
  assert.ok(engine, '全Lane実行後のEngine Snapshotがありません。');
  assert.equal(engine.parallel_entry_enabled, true);
  assert.deepEqual(Array.from(engine.enabled_entry_rule_lanes), ['NORMAL', 'EXPANSION', 'EXPANSION_LITE']);
  assert.equal(engine.cross_lane_condition_sharing, 'FORBIDDEN');
  const expansionEntry = (result.rangeRun?.execution_events || []).find(event =>
    event.event_type === 'entry' && String(event.rule_lane || event.execution?.rule_lane).toUpperCase() === 'EXPANSION'
  );
  assert.ok(expansionEntry, '実データ40本SmokeでExpansion Entryが発生していません。');
  assert.equal(expansionEntry.simulation_time, '2025-10-30 07:04');
  assert.equal(expansionEntry.execution?.entry_level, 'H1_R2');
  assert.equal(expansionEntry.execution?.management_timeframe, 'H1');
  console.log('PASS all_rule_lanes_range_smoke_v0_28');
  console.log(`expansion_entry=${expansionEntry.simulation_time} ${expansionEntry.summary}`);
  process.exit(0);
})().catch(error => {
  console.error(error);
  process.exit(1);
});
