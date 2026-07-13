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

const pluginPath = artifactPath('studio_overlays', 'gpt_fx_lab', 'plugins', 'fx_chart_viewer', 'plugin.js');
const manifestPath = artifactPath('studio_overlays', 'gpt_fx_lab', 'plugins', 'fx_chart_viewer', 'plugin.json');
const profilePath = artifactPath('studio_overlays', 'gpt_fx_lab', 'simulation', 'fx_simulation_run_profile_normal_plus_expansion_lite_v0_1.json');
const source = fs.readFileSync(pluginPath, 'utf8');
const manifest = JSON.parse(fs.readFileSync(manifestPath, 'utf8'));
const profile = JSON.parse(fs.readFileSync(profilePath, 'utf8'));

assert.equal(manifest.version, '0.9.1.01');
assert.equal(manifest.display_policy.simulation_run_profile.default_file, 'fx_simulation_run_profile_normal_plus_expansion_lite_v0_1.json');
assert.equal(profile.m5_execution_policy.rule_lane_policy.active_entry_rule_lane, 'PARALLEL_RULE_LANES');
assert.equal(profile.m5_execution_policy.rule_lane_policy.lanes.NORMAL.enabled, true);
assert.equal(profile.m5_execution_policy.rule_lane_policy.lanes.EXPANSION_LITE.enabled, true);
assert.equal(profile.m5_execution_policy.rule_lane_policy.cross_lane_condition_sharing, 'FORBIDDEN');
assert.equal(profile.m5_execution_policy.rule_lane_policy.parallel_entry_enabled, true);
assert.equal(profile.m5_execution_policy.rule_lane_policy.simultaneous_entry_policy, 'ALLOW_ALL_MATCHED_LANES');

const hook = `
  window.__fxCombinedLaneTest = {
    validateSimulationRunDraft,
    normalizeSimulationRunProfile,
    m5RuleLanePolicy,
    evaluateEnabledEntryRuleLanes
  };
`;
const closeIndex = source.lastIndexOf('})();');
assert.ok(closeIndex > 0, 'Plugin IIFE終端を検出できません。');
const instrumented = source.slice(0, closeIndex) + hook + source.slice(closeIndex);
const context = { window: {}, console, setTimeout, clearTimeout, URL, structuredClone, Intl, Date, Math, JSON, Map, Set, Promise };
vm.runInNewContext(instrumented, context, { filename: pluginPath });
const api = context.window.__fxCombinedLaneTest;
const normalized = api.normalizeSimulationRunProfile(profile);
const validation = api.validateSimulationRunDraft(normalized);
assert.equal(validation.valid, true, `複合Profile検証失敗:\n${validation.errors.join('\n')}`);
const lanePolicy = api.m5RuleLanePolicy(normalized.m5_execution_policy);
assert.deepEqual(Array.from(lanePolicy.enabled_entry_rule_lanes), ['NORMAL', 'EXPANSION_LITE']);
assert.equal(lanePolicy.parallel_entry_enabled, true);

function normalPortfolio() {
  return {
    trades: [], positions: [], normal_entry_opportunities: [], used_dow_confirmation_ids: [],
    expansion_lite_entry_opportunities: [], used_expansion_lite_confirmation_ids: [],
    normal_anchor_lifecycle: { status: 'NONE', last_retired_at_ms: null }
  };
}
const confirmationMs = Date.parse('2025-10-30T09:44:00+09:00');
const dowConfirmation = {
  confirmation_id: 'combined_dow_001', direction: 'UP', confirmed_at: '2025-10-30 09:44',
  confirmed_at_ms: confirmationMs, breakout_threshold_price: 153.135,
  anchor_price: 152.164, anchor_point_id: 'combined_anchor_point'
};
const normalAnchor = {
  anchor_id: 'combined_normal_anchor', price: 152.164, direction: 'UP',
  dow_confirmation_id: 'combined_dow_001'
};
const portfolio = normalPortfolio();
const normalInput = {
  portfolio,
  referenceMs: confirmationMs,
  referenceTime: '2025-10-30 09:44',
  price: 153.498,
  direction: 'LONG',
  confirmationSide: 'LONG',
  normalFacts: {
    entry_direction_ready: true, cycle_guard_passed: true,
    h4_cycle_late: false, h1_cycle_late: false,
    h4_t3_ready: true, h1_t3_ready: true,
    h4_h1_t3_aligned: true, m5_dow_aligned: true
  },
  dowConfirmation,
  entryResolution: { status: 'RESOLVED_REFERENCE', anchor_id: normalAnchor.anchor_id, anchor: normalAnchor },
  entryAnchor: normalAnchor,
  anchorPrice: normalAnchor.price,
  r2Touch: { touched: true, entry_price: 152.698, passed_before_bar: true, open: 153.300 },
  r3Touch: { touched: true, price: 153.028 },
  policy: normalized.m5_execution_policy,
  minEntryLabel: 'R2',
  hsiNotReachedReasonCode: 'HSI_R2_NOT_REACHED'
};
const liteInputBlocked = {
  portfolio,
  referenceMs: confirmationMs,
  referenceTime: '2025-10-30 09:44',
  price: 153.498,
  currentBar: { open: 153.300, high: 153.520, low: 153.250, close: 153.498 },
  expansionLiteFacts: {
    direction: 'LONG', confirmation_side: 'LONG', entry_direction_ready: false,
    h4_t3_side_long: true, h1_t3_side_long: true, h4_t3_side_short: false, h1_t3_side_short: false,
    h1_cycle_front_half: false, h1_cycle_elapsed_bars: 4, h1_cycle_front_half_limit: 3.5
  },
  dowConfirmation,
  entryResolution: { status: 'RESOLVED_REFERENCE', anchor_id: 'combined_lite_anchor', anchor: { anchor_id: 'combined_lite_anchor', price: 152.164 } },
  entryAnchor: { anchor_id: 'combined_lite_anchor', price: 152.164 },
  anchorPrice: 152.164,
  distanceRaw: 222,
  r3Touch: { touched: true, price: 153.028, label: 'R3' },
  policy: normalized.m5_execution_policy
};
const normalFallback = api.evaluateEnabledEntryRuleLanes(lanePolicy, {
  EXPANSION_LITE: liteInputBlocked,
  NORMAL: normalInput
});
assert.equal(normalFallback.selected_lane, 'NORMAL', 'Expansion-Lite不成立時にNORMAL Entryへ到達できません。');
assert.equal(normalFallback.selected_decision.action, 'ENTRY');
assert.equal(normalFallback.selected_decision.action_label, '通常Entry');

const priorityPortfolio = normalPortfolio();
const liteInputReady = {
  ...liteInputBlocked,
  portfolio: priorityPortfolio,
  expansionLiteFacts: {
    ...liteInputBlocked.expansionLiteFacts,
    entry_direction_ready: true,
    h1_cycle_front_half: true,
    h1_cycle_elapsed_bars: 3
  }
};
const normalInputReady = { ...normalInput, portfolio: priorityPortfolio };
const parallelEntries = api.evaluateEnabledEntryRuleLanes(lanePolicy, {
  EXPANSION_LITE: liteInputReady,
  NORMAL: normalInputReady
});
assert.equal(parallelEntries.simultaneous_entry, true);
assert.equal(parallelEntries.simultaneous_entry_policy, 'ALLOW_ALL_MATCHED_LANES');
assert.deepEqual(Array.from(parallelEntries.entry_decisions, item => item.rule_lane).sort(), ['EXPANSION_LITE', 'NORMAL']);
assert.ok(parallelEntries.entry_decisions.every(item => item.action === 'ENTRY'));

assert.match(source, /cross_lane_condition_sharing/);
assert.match(source, /evaluateEnabledEntryRuleLanes/);
assert.match(source, /active_trade_ids_by_lane/);
console.log('PASS normal_plus_expansion_lite_orchestration_v0_1');
console.log(`fallback=${normalFallback.selected_decision.action_label}`);
console.log(`same_bar_entries=${parallelEntries.entry_decisions.map(item => item.action_label).join(',')}`);
