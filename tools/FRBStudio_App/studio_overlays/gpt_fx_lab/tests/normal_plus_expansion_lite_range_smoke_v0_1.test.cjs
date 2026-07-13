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
const source = fs.readFileSync(pluginPath, 'utf8');
const profile = JSON.parse(fs.readFileSync(profilePath, 'utf8'));
const hook = `window.__fxCombinedNormalSmoke = { normalizeSimulationRunProfile, validateSimulationRunDraft, m5RuleLanePolicy, evaluateEnabledEntryRuleLanes };`;
const closeIndex = source.lastIndexOf('})();');
assert.ok(closeIndex > 0, 'Plugin IIFE終端を検出できません。');
const context = {
  window: {}, console, setTimeout, clearTimeout, URL, structuredClone,
  Intl, Date, Math, JSON, Map, Set, Promise
};
vm.runInNewContext(source.slice(0, closeIndex) + hook + source.slice(closeIndex), context, { filename: pluginPath });
const api = context.window.__fxCombinedNormalSmoke;
const normalized = api.normalizeSimulationRunProfile(profile);
const validation = api.validateSimulationRunDraft(normalized);
assert.equal(validation.valid, true, validation.errors.join('\n'));
const lanePolicy = api.m5RuleLanePolicy(normalized.m5_execution_policy);

const confirmationMs = Date.parse('2025-10-30T09:44:00+09:00');
const portfolio = {
  trades: [], positions: [], normal_entry_opportunities: [], used_dow_confirmation_ids: [],
  expansion_lite_entry_opportunities: [], used_expansion_lite_confirmation_ids: [],
  normal_anchor_lifecycle: { status: 'NONE', last_retired_at_ms: null }
};
const dowConfirmation = {
  confirmation_id: 'range_smoke_dow_001', direction: 'UP', confirmed_at: '2025-10-30 09:44',
  confirmed_at_ms: confirmationMs, breakout_threshold_price: 153.135,
  anchor_price: 152.164, anchor_point_id: 'range_smoke_anchor_point'
};
const normalAnchor = {
  anchor_id: 'range_smoke_normal_anchor', price: 152.164, direction: 'UP',
  dow_confirmation_id: dowConfirmation.confirmation_id
};
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
const liteInputNotReady = {
  portfolio,
  referenceMs: confirmationMs,
  referenceTime: '2025-10-30 09:44',
  price: 153.498,
  currentBar: { open: 153.300, high: 153.520, low: 153.250, close: 153.498 },
  expansionLiteFacts: {
    direction: 'UNDETERMINED', confirmation_side: 'LONG', entry_direction_ready: false,
    h4_t3_side_long: true, h1_t3_side_long: true,
    h4_t3_side_short: false, h1_t3_side_short: false,
    h1_cycle_front_half: false, h1_cycle_elapsed_bars: 4,
    h1_cycle_front_half_limit: 3.5
  },
  dowConfirmation,
  entryResolution: {
    status: 'RESOLVED_REFERENCE', anchor_id: 'range_smoke_lite_anchor',
    anchor: { anchor_id: 'range_smoke_lite_anchor', price: 152.164 }
  },
  entryAnchor: { anchor_id: 'range_smoke_lite_anchor', price: 152.164 },
  anchorPrice: 152.164,
  distanceRaw: 222,
  r3Touch: { touched: true, price: 153.028, label: 'R3' },
  policy: normalized.m5_execution_policy
};

const result = api.evaluateEnabledEntryRuleLanes(lanePolicy, {
  EXPANSION_LITE: liteInputNotReady,
  NORMAL: normalInput
});
assert.equal(result.selected_lane, 'NORMAL', 'Expansion-Lite不成立時にNORMAL Rule Laneへ到達できません。');
assert.equal(result.simultaneous_entry, false);
assert.equal(result.selected_decision.action, 'ENTRY');
assert.equal(result.selected_decision.action_label, '通常Entry');
assert.equal(profile.m5_execution_policy.rule_lane_policy.cross_lane_condition_sharing, 'FORBIDDEN');
console.log('PASS normal_plus_expansion_lite_range_smoke_v0_1');
console.log(`normal_fallback_entry=${result.selected_decision.action_label}`);
