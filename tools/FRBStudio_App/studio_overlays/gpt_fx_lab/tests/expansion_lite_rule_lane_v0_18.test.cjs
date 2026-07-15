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
const profilePath = artifactPath('studio_overlays', 'gpt_fx_lab', 'simulation', 'fx_simulation_run_profile_expansion_lite_v0_1.json');
const source = fs.readFileSync(pluginPath, 'utf8');
const manifest = JSON.parse(fs.readFileSync(manifestPath, 'utf8'));
const profile = JSON.parse(fs.readFileSync(profilePath, 'utf8'));

assert.equal(manifest.version, '0.9.1.08');
assert.equal(manifest.display_policy.simulation_run_profile.default_file, 'fx_simulation_run_profile_normal_plus_expansion_lite_v0_1.json');
assert.equal(profile.m5_execution_policy.rule_lane_policy.active_entry_rule_lane, 'EXPANSION_LITE');
assert.equal(profile.m5_execution_policy.rule_lane_policy.lanes.NORMAL.enabled, false);
assert.equal(profile.m5_execution_policy.rule_lane_policy.lanes.EXPANSION.enabled, false);
assert.equal(profile.m5_execution_policy.rule_lane_policy.lanes.EXPANSION_LITE.enabled, true);
assert.equal(profile.m5_execution_policy.expansion_lite_policy.day_cycle_position_required, false);
assert.equal(profile.m5_execution_policy.expansion_lite_policy.entry_label, 'R3');
assert.deepEqual(profile.m5_execution_policy.expansion_lite_policy.add_on_levels.map(x => x.label), ['R3.5', 'R4', 'R4.5']);
assert.equal(profile.m5_execution_policy.expansion_lite_policy.target_label, 'R5');
assert.equal(profile.m5_execution_policy.expansion_lite_policy.t3_exit_long, 'M5_LOW_LT_M5_T3');
assert.equal(profile.m5_execution_policy.expansion_lite_policy.t3_exit_short, 'M5_HIGH_GT_M5_T3');
assert.equal(profile.m5_execution_policy.expansion_lite_policy.anchor_exit_long, 'M5_LOW_LT_ADOPTED_HSI_ANCHOR');
assert.equal(profile.m5_execution_policy.expansion_lite_policy.anchor_exit_short, 'M5_HIGH_GT_ADOPTED_HSI_ANCHOR');
assert.equal(profile.m5_execution_policy.expansion_lite_policy.other_rule_lane_fallback, 'FORBIDDEN');

const hook = `
  window.__fxExpansionLiteTest = {
    normalizeSimulationRunProfile,
    validateSimulationRunDraft,
    m5ExecutionExpansionLiteFacts,
    m5ExecutionExpansionLiteAnchorResolution,
    m5ExecutionLevelTouch,
    expansionLiteRuleLaneEntryDecision,
    expansionLiteRuleLaneCloseDecision,
    simulationExecutionMarkerLabel
  };
`;
const closeIndex = source.lastIndexOf('})();');
assert.ok(closeIndex > 0, 'Plugin IIFE終端を検出できません。');
const instrumented = source.slice(0, closeIndex) + hook + source.slice(closeIndex);
const context = {
  window: {}, console, setTimeout, clearTimeout, URL, structuredClone,
  Intl, Date, Math, JSON, Map, Set, Promise
};
vm.runInNewContext(instrumented, context, { filename: pluginPath });
const api = context.window.__fxExpansionLiteTest;
assert.ok(api, 'Expansion-LiteテストAPI公開に失敗しました。');

const normalized = api.normalizeSimulationRunProfile(profile);
const validation = api.validateSimulationRunDraft(normalized);
assert.equal(validation.valid, true, `Expansion-Lite Profile検証失敗:\n${validation.errors.join('\n')}`);

const confirmationMs = Date.parse('2025-11-03T10:00:00+09:00');
const dowUp = {
  confirmation_id: 'exp_lite_dow_up_001', direction: 'UP',
  confirmed_at: '2025-11-03 10:00', confirmed_at_ms: confirmationMs,
  anchor_price: 150.000, anchor_time: '2025-11-03 08:00',
  anchor_point_id: 'low_001', breakout_threshold_price: 150.700
};
const snapshotLong = {
  timeframes: {
    H4: { latest_confirmed_bar: { close: 151.000, t3_20_0_2: 150.500 } },
    H1: {
      latest_confirmed_bar: { close: 150.900, t3_20_0_2: 150.600 },
      cycle_state: { origin: { point_id: 'h1_low', confirm_bars: 7 }, elapsed_bars: 3 }
    },
    M5: { trend_state: 'UP', trend_detail: { high_relation: 'HIGHER', low_relation: 'HIGHER' } }
  }
};
const factsLong = api.m5ExecutionExpansionLiteFacts(snapshotLong, normalized, dowUp);
assert.equal(factsLong.direction, 'LONG');
assert.equal(factsLong.h1_cycle_entry_allowed, true);
assert.equal(factsLong.h1_cycle_entry_allowed_max_bars, 14);
assert.equal(factsLong.h1_cycle_front_half, true);
assert.equal(factsLong.h1_cycle_front_half_limit, 14);
assert.equal(factsLong.day_cycle_position_used, false);

// ㉗→㉙ target regression: generic CycleがMIDDLE/DOWN_CYCLEでも、
// Longは最新H1安値候補からH1 ProfileのEntry許可14本以内ならExpansion-Lite Entry Window内と判定する。
const targetDirectionalCandidateSnapshot = {
  timeframes: {
    H4: { latest_confirmed_bar: { close: 152.767, t3_20_0_2: 151.920 } },
    H1: {
      latest_confirmed_bar: { index: 50, close: 153.037, t3_20_0_2: 152.227 },
      swing_state: {
        latest_pending_low: {
          point_id: 'swing_h1_low_target_27', type: 'swing_low', source_index: 48,
          pivot_time: '2025-10-30 06:00', pivot_price: 152.164,
          confirm_bars: 7, lifecycle_status: 'candidate', basis_role: 'candidate_pending'
        },
        latest_active_low: {
          point_id: 'swing_h1_low_old', type: 'swing_low', source_index: 34,
          pivot_time: '2025-10-29 16:00', pivot_price: 151.857,
          confirm_bars: 7, lifecycle_status: 'confirmed', basis_role: 'basis_active'
        }
      },
      cycle_state: {
        phase: 'MIDDLE', direction: 'DOWN_CYCLE', elapsed_bars: 10,
        origin: { point_id: 'old_high', type: 'swing_high', source_index: 40, confirm_bars: 7 }
      }
    },
    M5: { trend_state: 'UP', trend_detail: { high_relation: 'HIGHER', low_relation: 'HIGHER' } }
  }
};
const targetDirectionalFacts = api.m5ExecutionExpansionLiteFacts(targetDirectionalCandidateSnapshot, normalized, dowUp);
assert.equal(targetDirectionalFacts.direction, 'LONG');
assert.equal(targetDirectionalFacts.h1_cycle_entry_allowed, true);
assert.equal(targetDirectionalFacts.h1_cycle_elapsed_bars, 2);
assert.equal(targetDirectionalFacts.h1_cycle_entry_allowed_max_bars, 14);
assert.equal(targetDirectionalFacts.h1_cycle_front_half_limit, 14);
assert.equal(targetDirectionalFacts.h1_cycle_origin_source, 'DIRECTIONAL_PENDING_SWING');
assert.equal(targetDirectionalFacts.h1_cycle_origin.point_id, 'swing_h1_low_target_27');

const resolutionLong = api.m5ExecutionExpansionLiteAnchorResolution(dowUp);
assert.equal(resolutionLong.status, 'RESOLVED_REFERENCE');
const r3Long = api.m5ExecutionLevelTouch({ open: 150.800, high: 151.000, low: 150.700 }, 150, 'LONG', 144, 'R3', normalized.m5_execution_policy);
assert.equal(r3Long.touched, true);

function emptyPortfolio() {
  return { trades: [], positions: [], expansion_lite_entry_opportunities: [], used_expansion_lite_confirmation_ids: [] };
}
const entryAtConfirmation = api.expansionLiteRuleLaneEntryDecision({
  portfolio: emptyPortfolio(), referenceMs: confirmationMs, referenceTime: '2025-11-03 10:00',
  price: 150.900, currentBar: { open: 150.800, high: 151.000, low: 150.700, close: 150.900 },
  expansionLiteFacts: factsLong, dowConfirmation: dowUp,
  entryResolution: resolutionLong, entryAnchor: resolutionLong.anchor,
  anchorPrice: 150, distanceRaw: 150, r3Touch: r3Long, policy: normalized.m5_execution_policy
});
assert.equal(entryAtConfirmation.action, 'ENTRY');
assert.equal(entryAtConfirmation.action_label, 'Expansion-Lite Entry');
assert.equal(entryAtConfirmation.execution_candidate.entry_level, 'R3');
assert.equal(entryAtConfirmation.rule_lane, 'EXPANSION_LITE');

const dowUpEarlier = { ...dowUp, confirmation_id: 'exp_lite_dow_up_002', confirmed_at_ms: confirmationMs - 600000 };
const resolutionEarlier = api.m5ExecutionExpansionLiteAnchorResolution(dowUpEarlier);
const portfolioAfterConfirmation = emptyPortfolio();
const r3Waiting = api.m5ExecutionLevelTouch({ open: 150.300, high: 150.500, low: 150.200 }, 150, 'LONG', 144, 'R3', normalized.m5_execution_policy);
const waitAfterDow = api.expansionLiteRuleLaneEntryDecision({
  portfolio: portfolioAfterConfirmation, referenceMs: confirmationMs - 600000, referenceTime: '2025-11-03 09:50',
  price: 150.400, currentBar: { open: 150.300, high: 150.500, low: 150.200, close: 150.400 },
  expansionLiteFacts: factsLong, dowConfirmation: dowUpEarlier,
  entryResolution: resolutionEarlier, entryAnchor: resolutionEarlier.anchor,
  anchorPrice: 150, distanceRaw: 80, r3Touch: r3Waiting, policy: normalized.m5_execution_policy
});
assert.equal(waitAfterDow.action, 'WAIT');
const entryAfterConfirmation = api.expansionLiteRuleLaneEntryDecision({
  portfolio: portfolioAfterConfirmation, referenceMs: confirmationMs, referenceTime: '2025-11-03 10:00',
  price: 150.900, currentBar: { open: 150.700, high: 150.900, low: 150.650, close: 150.850 },
  expansionLiteFacts: factsLong, dowConfirmation: dowUpEarlier,
  entryResolution: resolutionEarlier, entryAnchor: resolutionEarlier.anchor,
  anchorPrice: 150, distanceRaw: 150, r3Touch: r3Long, policy: normalized.m5_execution_policy
});
assert.equal(entryAfterConfirmation.action, 'ENTRY');
assert.equal(entryAfterConfirmation.entry_opportunity.entry_execution_mode, 'FIRST_R3_TOUCH_AFTER_DOW_CONFIRMATION');

const activeTradeLong = {
  trade_id: 'trade_lite_long', rule_lane: 'EXPANSION_LITE', side: 'LONG',
  entry_anchor_id: resolutionLong.anchor_id, entry_anchor_price: 150, entry_price: 150.900,
  target_price: 152.262, consumed_add_on_levels: []
};
const activePositionLong = { position_id: 'pos_lite_long', trade_id: 'trade_lite_long', side: 'LONG', units_open: 10, entry_anchor_price: 150, entry_price: 150.900 };
const addOn = api.expansionLiteRuleLaneCloseDecision({
  activeTrade: structuredClone(activeTradeLong), activePosition: structuredClone(activePositionLong),
  currentBar: { open: 150.900, high: 151.450, low: 150.800, close: 151.300, t3_20_0_2: 150.600 },
  m5State: { trend_state: 'UP', trend_detail: { high_relation: 'HIGHER', low_relation: 'HIGHER' } },
  policy: normalized.m5_execution_policy
});
assert.equal(addOn.action, 'ADD_ON');
assert.equal(addOn.action_label, 'Expansion-Lite Add-on');
assert.deepEqual(Array.from(addOn.add_on_levels, x => x.label), ['R3.5', 'R4']);

const targetExit = api.expansionLiteRuleLaneCloseDecision({
  activeTrade: structuredClone(activeTradeLong), activePosition: structuredClone(activePositionLong),
  currentBar: { high: 152.300, low: 151.000, close: 152.100, t3_20_0_2: 150.600 },
  m5State: { trend_state: 'UP', trend_detail: { high_relation: 'HIGHER', low_relation: 'HIGHER' } },
  policy: normalized.m5_execution_policy
});
assert.equal(targetExit.exit_type, 'TARGET_EXIT');
assert.equal(targetExit.action_label, 'R5 Exit');

const t3ExitLong = api.expansionLiteRuleLaneCloseDecision({
  activeTrade: structuredClone(activeTradeLong), activePosition: structuredClone(activePositionLong),
  currentBar: { high: 151.000, low: 150.550, close: 150.800, t3_20_0_2: 150.600 },
  m5State: { trend_state: 'UP', trend_detail: { high_relation: 'HIGHER', low_relation: 'HIGHER' } },
  policy: normalized.m5_execution_policy
});
assert.equal(t3ExitLong.exit_type, 'T3_EXIT');
assert.equal(t3ExitLong.action_label, 'T3 Exit');

const anchorExitLong = api.expansionLiteRuleLaneCloseDecision({
  activeTrade: structuredClone(activeTradeLong), activePosition: structuredClone(activePositionLong),
  currentBar: { high: 150.500, low: 149.990, close: 150.100, t3_20_0_2: 149.900 },
  m5State: { trend_state: 'UP', trend_detail: { high_relation: 'HIGHER', low_relation: 'HIGHER' } },
  policy: normalized.m5_execution_policy
});
assert.equal(anchorExitLong.exit_type, 'ANCHOR_EXIT');
assert.equal(anchorExitLong.action_label, 'Anchor Exit');

const structuralExit = api.expansionLiteRuleLaneCloseDecision({
  activeTrade: structuredClone(activeTradeLong), activePosition: structuredClone(activePositionLong),
  currentBar: { high: 151.000, low: 150.700, close: 150.800, t3_20_0_2: 150.600 },
  m5State: { trend_state: 'UP', trend_detail: { high_relation: 'HIGHER', low_relation: 'LOWER' } },
  policy: normalized.m5_execution_policy
});
assert.equal(structuralExit.exit_type, 'STRUCTURAL_EXIT');
assert.equal(structuralExit.action_label, 'Structural Exit');

const activeTradeShort = {
  trade_id: 'trade_lite_short', rule_lane: 'EXPANSION_LITE', side: 'SHORT',
  entry_anchor_id: 'short_anchor', entry_anchor_price: 155,
  target_price: 152.738, consumed_add_on_levels: []
};
const activePositionShort = { position_id: 'pos_lite_short', trade_id: 'trade_lite_short', side: 'SHORT', units_open: 10, entry_anchor_price: 155 };
const t3ExitShort = api.expansionLiteRuleLaneCloseDecision({
  activeTrade: activeTradeShort, activePosition: activePositionShort,
  currentBar: { high: 154.050, low: 153.500, close: 153.700, t3_20_0_2: 154.000 },
  m5State: { trend_state: 'DOWN', trend_detail: { high_relation: 'LOWER', low_relation: 'LOWER' } },
  policy: normalized.m5_execution_policy
});
assert.equal(t3ExitShort.exit_type, 'T3_EXIT');

const markerEntry = api.simulationExecutionMarkerLabel({ rule_lane: 'EXPANSION_LITE', event_type: 'entry', execution: { rule_lane: 'EXPANSION_LITE' } });
const markerExit = api.simulationExecutionMarkerLabel({ rule_lane: 'EXPANSION_LITE', event_type: 'close', execution: { rule_lane: 'EXPANSION_LITE', exit_type: 'STRUCTURAL_EXIT' } });
assert.equal(markerEntry, 'Expansion-Lite Entry');
assert.equal(markerExit, 'Structural Exit');
assert.match(source, /const isExpansionLiteEntry = lane === RULE_LANE_EXPANSION_LITE/);
assert.match(source, /rgba\(196, 181, 253, 0\.98\)/);
assert.match(source, /if \(lane === RULE_LANE_EXPANSION_LITE && usageEventType === 'add_on'\) return null;/);

console.log('PASS expansion_lite_rule_lane_v0_18');
console.log(`profile=${profile.profile_id}`);
console.log(`entry=${entryAtConfirmation.action_label}`);
console.log(`add_on=${addOn.add_on_levels.map(x => x.label).join(',')}`);
console.log(`exits=${[targetExit.action_label,t3ExitLong.action_label,structuralExit.action_label,anchorExitLong.action_label].join(',')}`);
