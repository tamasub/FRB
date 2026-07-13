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
const profilePath = artifactPath(...baseParts, 'simulation', 'fx_simulation_run_profile_normal_plus_expansion_lite_v0_1.json');
const m5Path = artifactPath(...baseParts, 'data', 'fx_usdjpy_m5_t3_data_v0_1.json');
const d1Path = artifactPath(...baseParts, 'data', 'fx_usdjpy_d1_t3_data_v0_1.json');
const source = fs.readFileSync(pluginPath, 'utf8');
const hook = `window.__fxLiteTargetSmoke = { normalizeAllRows, simulationRunDraftFromProfile, buildVisibleRangeSimulationRun, buildEmptySimulationTrace, validateSimulationRunDraft };`;
const closeIndex = source.lastIndexOf('})();');
assert.ok(closeIndex > 0, 'Plugin IIFE終端を検出できません。');
const context = {
  window: {}, console, setTimeout, clearTimeout, URL, structuredClone,
  Intl, Date, Math, JSON, Map, Set, Promise,
  requestAnimationFrame: callback => setTimeout(callback, 0)
};
vm.runInNewContext(source.slice(0, closeIndex) + hook + source.slice(closeIndex), context, { filename: pluginPath });
const api = context.window.__fxLiteTargetSmoke;

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
    windowSize: 120,
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
  const events = result.rangeRun?.execution_events || [];
  const liteEntry = events.find(event => event.event_type === 'entry' && String(event.rule_lane || event.execution?.rule_lane).toUpperCase() === 'EXPANSION_LITE');
  assert.ok(liteEntry, '㉗→㉙範囲でExpansion-Lite Entryが発生していません。');
  assert.equal(liteEntry.simulation_time, '2025-10-30 09:44');
  assert.equal(liteEntry.chart_marker_label, 'Expansion-Lite Entry');
  assert.equal(liteEntry.execution?.entry_anchor_price, 152.164);
  assert.equal(liteEntry.execution?.entry_level, 'R3');
  const liteAddOn = events.find(event => event.event_type === 'add_on' && String(event.rule_lane || event.execution?.rule_lane).toUpperCase() === 'EXPANSION_LITE');
  assert.ok(liteAddOn, 'Expansion-Lite Entry後のR3.5 Add-onが発生していません。');
  assert.equal(liteAddOn.chart_marker_label, 'Expansion-Lite Add-on R3.5');
  const normalAtTarget = events.find(event => event.event_type === 'entry' && event.simulation_time === liteEntry.simulation_time && String(event.rule_lane).toUpperCase() === 'NORMAL');
  assert.ok(normalAtTarget, '同一M5足で成立した通常EntryがExpansion-Lite Entryに消されています。');
  assert.equal(normalAtTarget.simulation_time, '2025-10-30 09:44');
  const simultaneousEntries = events.filter(event => event.event_type === 'entry' && event.simulation_time === liteEntry.simulation_time);
  assert.deepEqual(Array.from(simultaneousEntries, event => String(event.rule_lane).toUpperCase()).sort(), ['EXPANSION_LITE', 'NORMAL']);
  assert.equal(result.rangeRun?.final_snapshot?.position_lifecycle?.engine?.parallel_entry_enabled, true);
  console.log('PASS expansion_lite_target_27_29_range_smoke_v0_1');
  console.log(`normal_entry=${normalAtTarget.simulation_time} ${normalAtTarget.summary}`);
  console.log(`lite_entry=${liteEntry.simulation_time} ${liteEntry.summary}`);
  console.log(`lite_add_on=${liteAddOn.simulation_time} ${liteAddOn.summary}`);
  process.exit(0);
})().catch(error => {
  console.error(error);
  process.exit(1);
});
