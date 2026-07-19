const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const assert = require('node:assert/strict');

const root = path.resolve(process.argv[2] || process.cwd());
const base = path.join(root, 'studio_overlays', 'gpt_fx_lab');
const pluginPath = path.join(base, 'plugins', 'fx_chart_viewer', 'plugin.js');
const profilePath = path.join(base, 'simulation', 'fx_simulation_run_profile_expansion_lite_v0_1.json');
const source = fs.readFileSync(pluginPath, 'utf8');
const hook = `window.__fxV027 = {
  validateSimulationRunDraft,
  m5ExecutionObserveExpansionLiteH4CandidateLow,
  m5ExecutionExpansionLiteCandidateLowGuard,
  m5ExecutionApplyExpansionLiteCloseToEpisode,
  expansionLiteRuleLaneEntryDecision,
  m5ExecutionNewExpansionLiteTrade,
  m5ExecutionExpansionLiteEpisodeTerminalStatus
};`;
const closeIndex = source.lastIndexOf('})();');
assert.ok(closeIndex > 0, 'Plugin IIFE終端を検出できません。');
const context = {
  window: {}, console, setTimeout, clearTimeout, URL, structuredClone,
  Intl, Date, Math, JSON, Map, Set, Promise,
  requestAnimationFrame: callback => setTimeout(callback, 0)
};
vm.runInNewContext(source.slice(0, closeIndex) + hook + source.slice(closeIndex), context, { filename: pluginPath });
const api = context.window.__fxV027;
const profile = JSON.parse(fs.readFileSync(profilePath, 'utf8'));
const policy = profile.m5_execution_policy;

// Profile / upper-timeframe ceiling / Day guard separation.
const validation = api.validateSimulationRunDraft(profile);
assert.equal(validation.valid, true, validation.errors.join('\n'));
assert.equal(profile.rule_version, 'simulation_rule_v0_24_normal_plus_v0_27_expansion_lite');
assert.equal(profile.app_integration_version, '0.9.1.22');
assert.equal(policy.expansion_lite_policy.upper_timeframe_ceiling, 'H4');
assert.equal(policy.expansion_lite_policy.day_entry_context_used, false);
assert.equal(policy.expansion_lite_policy.week_entry_context_used, false);
assert.deepEqual(policy.entry_guard_policy.day_up_h4_down_r5_short.applies_to_rule_lanes, ['EXPANSION']);
assert.equal(policy.expansion_lite_policy.max_reentry_count_per_episode, 1);
assert.equal(policy.expansion_lite_policy.reentry_add_on_allowed, false);

// H4 Candidate Low Guard: same candidate update counts once, second distinct candidate blocks Short.
const shortEpisode = {
  episode_id: 'lite_ep_short_1', direction: 'SHORT', status: 'ACTIVE',
  h4_candidate_low_ids: [], h4_candidate_low_observations: [], h4_candidate_low_distinct_count: 0
};
const factBase = {
  h4_trend_state: 'DOWN', h4_wave_id: 'h4_down_wave_1', h4_candidate_low_history_resolved: true
};
api.m5ExecutionObserveExpansionLiteH4CandidateLow(shortEpisode, {
  ...factBase,
  h4_pending_low_candidates: [{ point_id: 'low_candidate_1', type: 'swing_low', pivot_time: '2025-12-01 04:00', pivot_price: 154.5 }]
}, 1, '2025-12-01 04:00');
api.m5ExecutionObserveExpansionLiteH4CandidateLow(shortEpisode, {
  ...factBase,
  h4_pending_low_candidates: [{ point_id: 'low_candidate_1', type: 'swing_low', pivot_time: '2025-12-01 04:00', pivot_price: 154.4 }]
}, 2, '2025-12-01 08:00');
assert.equal(shortEpisode.h4_candidate_low_distinct_count, 1, '同じCandidate更新を重複カウントしています。');
let guard = api.m5ExecutionExpansionLiteCandidateLowGuard(shortEpisode, factBase, policy, 'INITIAL_ENTRY');
assert.equal(guard.blocked, false);
api.m5ExecutionObserveExpansionLiteH4CandidateLow(shortEpisode, {
  ...factBase,
  h4_pending_low_candidates: [{ point_id: 'low_candidate_2', type: 'swing_low', pivot_time: '2025-12-02 00:00', pivot_price: 154.2 }]
}, 3, '2025-12-02 00:00');
assert.equal(shortEpisode.h4_candidate_low_distinct_count, 2);
guard = api.m5ExecutionExpansionLiteCandidateLowGuard(shortEpisode, factBase, policy, 'INITIAL_ENTRY');
assert.equal(guard.blocked, true);
assert.equal(guard.primary_reason_code, 'EXPANSION_LITE_H4_MULTIPLE_CANDIDATE_LOWS_SHORT_ENTRY_BLOCKED');
const longEpisodeForGuard = { ...shortEpisode, direction: 'LONG' };
assert.equal(api.m5ExecutionExpansionLiteCandidateLowGuard(longEpisodeForGuard, factBase, policy, 'INITIAL_ENTRY').blocked, false, 'Candidate Low GuardをLongへ誤適用しています。');

// T3 Exit closes only the trade and retains Episode/HSI for ReEntry watching.
const retainedEpisode = {
  episode_id: 'lite_ep_long_1', direction: 'LONG', status: 'ACTIVE',
  detection_anchor_id: 'anchor_1', entry_anchor_id: 'anchor_1',
  detection_anchor_price: 100, entry_anchor_price: 100,
  r3_price: 101, target_price: 110,
  initial_entry_status: 'USED', reentry_count: 0,
  anchor_status: 'ACTIVE', reentry_opportunity_status: 'NOT_CREATED',
  h4_candidate_low_history_resolved: true
};
const portfolio = {
  expansion_lite_episodes: [retainedEpisode],
  expansion_lite_entry_opportunities: [retainedEpisode],
  active_expansion_lite_episode_id: retainedEpisode.episode_id
};
const initialTrade = {
  trade_id: 'lite_trade_1', rule_lane: 'EXPANSION_LITE',
  expansion_lite_episode_id: retainedEpisode.episode_id,
  entry_action: 'ENTRY', is_reentry: false
};
const transition = api.m5ExecutionApplyExpansionLiteCloseToEpisode(
  portfolio, initialTrade, { exit_type: 'T3_EXIT' },
  { referenceTime: '2025-10-29 09:49', referenceMs: 1000, price: 100.8 }
);
assert.equal(transition.status, 'WATCHING');
assert.equal(retainedEpisode.status, 'ACTIVE');
assert.equal(retainedEpisode.anchor_status, 'RETAINED_FOR_REENTRY');
assert.equal(retainedEpisode.reentry_opportunity_status, 'WATCHING');
assert.equal(retainedEpisode.entry_anchor_price, 100);
assert.equal(retainedEpisode.r3_price, 101);
assert.equal(retainedEpisode.target_price, 110);

function liteInput(currentBar, facts, ms, time) {
  return {
    portfolio,
    referenceMs: ms,
    referenceTime: time,
    price: currentBar.close,
    currentBar,
    expansionLiteFacts: {
      episode_side: 'LONG', confirmation_side: 'LONG', entry_direction_ready: true,
      h4_t3_side_long: true, h1_t3_side_long: true,
      h4_t3_side_short: false, h1_t3_side_short: false,
      h1_cycle_entry_allowed: true, h1_cycle_elapsed_bars: 5,
      h1_cycle_entry_allowed_max_bars: 14,
      h4_trend_state: 'UP', h4_wave_id: 'h4_up_wave_1',
      h4_candidate_low_history_resolved: true,
      h4_pending_low_candidates: [],
      m5_bb_upper: facts.bbUpper,
      m5_bb_lower: facts.bbLower,
      m5_bb_width: facts.bbWidth,
      m5_bb_previous_width: facts.bbPreviousWidth,
      m5_bb_width_expanding: facts.bbExpanding
    },
    entryResolution: { status: 'UNRESOLVED' },
    entryAnchor: { anchor_id: 'anchor_1', price: 100, pivot_time: '2025-10-29 04:00' },
    anchorPrice: 100,
    distanceRaw: 0,
    r3Touch: {},
    policy,
    timeframeSnapshot: { timeframes: {} }
  };
}

// Outside R3 immediately after T3 Exit: no chase and not armed.
let decision = api.expansionLiteRuleLaneEntryDecision(liteInput(
  { open: 101.05, high: 101.3, low: 101.0, close: 101.2, t3_20_0_2: 101.0 },
  { bbUpper: 101.1, bbLower: 100.0, bbWidth: 1.1, bbPreviousWidth: 1.0, bbExpanding: true },
  2000, '2025-10-29 20:55'
));
assert.equal(decision.action, 'WAIT');
assert.equal(retainedEpisode.reentry_trigger_armed, false);
assert.ok(decision.reason_codes.includes('EXPANSION_LITE_REENTRY_WAIT_R3_INSIDE_RETURN'));

// Close returns inside retained R3: rearm only, still no ReEntry.
decision = api.expansionLiteRuleLaneEntryDecision(liteInput(
  { open: 101.0, high: 101.05, low: 100.7, close: 100.9, t3_20_0_2: 100.8 },
  { bbUpper: 101.0, bbLower: 100.0, bbWidth: 1.0, bbPreviousWidth: 1.05, bbExpanding: false },
  3000, '2025-10-29 21:05'
));
assert.equal(decision.action, 'WAIT');
assert.equal(retainedEpisode.reentry_trigger_armed, true);
assert.equal(retainedEpisode.reentry_r3_inside_return_at, '2025-10-29 21:05');

// Retained R3 Close reclaim + T3 restoration + BB outer Close + width expansion => ReEntry.
decision = api.expansionLiteRuleLaneEntryDecision(liteInput(
  { open: 100.9, high: 101.25, low: 100.88, close: 101.2, t3_20_0_2: 101.0 },
  { bbUpper: 101.1, bbLower: 99.9, bbWidth: 1.2, bbPreviousWidth: 1.0, bbExpanding: true },
  4000, '2025-10-29 21:10'
));
assert.equal(decision.action, 'REENTRY');
assert.equal(decision.execution_candidate.price, 101.2);
assert.equal(decision.execution_candidate.entry_level, 'R3_RECLAIM');
assert.equal(retainedEpisode.reentry_count, 1);
assert.equal(retainedEpisode.reentry_opportunity_status, 'CONSUMED');

// ReEntry trade is created as a distinct Lite trade, keeps old anchor/R5, and disables Add-on.
const executionPortfolio = { positions: [], trades: [], status: 'FLAT', active_trade_id: null };
const createdReentry = api.m5ExecutionNewExpansionLiteTrade(executionPortfolio, {
  entryAction: 'REENTRY', direction: 'LONG', referenceTime: '2025-10-29 21:10', referenceMs: 4000,
  currentBar: { index: 465 }, price: 101.2, anchorPrice: 100, distanceRaw: 144,
  entryAnchor: { anchor_id: 'anchor_1' }, entryOpportunity: retainedEpisode
}, { event_id: 'trigger_reentry_1' }, policy);
assert.equal(createdReentry.trade.entry_action, 'REENTRY');
assert.equal(createdReentry.trade.is_reentry, true);
assert.equal(createdReentry.trade.add_on_allowed, false);
assert.equal(createdReentry.positions[0].role, 'EXPANSION_LITE_REENTRY_CORE');
assert.equal(createdReentry.positions[0].add_on_allowed, false);
assert.equal(createdReentry.trade.entry_anchor_price, 100);
assert.equal(createdReentry.trade.target_price, 102.262); // profile HSI scale: R5 = 377 * 0.006

// Max one ReEntry. Subsequent evaluation cannot emit another ReEntry.
decision = api.expansionLiteRuleLaneEntryDecision(liteInput(
  { open: 101.0, high: 101.4, low: 100.9, close: 101.3, t3_20_0_2: 101.0 },
  { bbUpper: 101.2, bbLower: 99.8, bbWidth: 1.4, bbPreviousWidth: 1.2, bbExpanding: true },
  5000, '2025-10-29 21:15'
));
assert.notEqual(decision.action, 'REENTRY');
assert.ok(decision.reason_codes.includes('EXPANSION_LITE_REENTRY_MAX_COUNT_CONSUMED'));

// T3 Exit of ReEntry terminates automatic ReEntry and retains anchor only for trace.
const reentryTrade = {
  trade_id: 'lite_trade_reentry_1', rule_lane: 'EXPANSION_LITE',
  expansion_lite_episode_id: retainedEpisode.episode_id,
  entry_action: 'REENTRY', is_reentry: true
};
const secondTransition = api.m5ExecutionApplyExpansionLiteCloseToEpisode(
  portfolio, reentryTrade, { exit_type: 'T3_EXIT' },
  { referenceTime: '2025-10-29 22:00', referenceMs: 6000, price: 101.0 }
);
assert.equal(secondTransition.status, 'CONSUMED');
assert.equal(retainedEpisode.status, 'OBSERVATION_ONLY');
assert.equal(retainedEpisode.anchor_status, 'RETAINED_FOR_TRACE');
assert.equal(retainedEpisode.reentry_opportunity_status, 'CONSUMED');
assert.equal(api.m5ExecutionExpansionLiteEpisodeTerminalStatus(retainedEpisode.status), true);

console.log('PASS expansion_lite_hsi_retention_bb_reentry_h4_candidate_v0_27');
