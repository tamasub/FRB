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
const profilePath = artifactPath('studio_overlays', 'gpt_fx_lab', 'simulation', 'fx_simulation_run_profile_v0_1.json');
const m5Path = artifactPath('studio_overlays', 'gpt_fx_lab', 'data', 'fx_usdjpy_m5_t3_data_v0_1.json');
const d1Path = artifactPath('studio_overlays', 'gpt_fx_lab', 'data', 'fx_usdjpy_d1_t3_data_v0_1.json');

const sourceText = fs.readFileSync(pluginPath, 'utf8');
function functionSource(name, nextName) {
  const start = sourceText.indexOf(`  function ${name}(`);
  const end = sourceText.indexOf(`  function ${nextName}(`, start + 1);
  assert.ok(start >= 0, `${name}を検出できません。`);
  assert.ok(end > start, `${name}の終端を検出できません。`);
  return sourceText.slice(start, end);
}

const normalEntrySource = functionSource('normalRuleLaneEntryDecision', 'normalRuleLaneCloseDecision');
const normalCloseSource = functionSource('normalRuleLaneCloseDecision', 'expansionRuleLaneEntryDecision');
assert.doesNotMatch(normalEntrySource, /\b(?:WEEK|DAY|EXPANSION|EXPANSION_LITE)\b/i,
  'Normal Entry EvaluatorがWEEK/DAY/Expansion固有判定を参照しています。');
assert.doesNotMatch(normalEntrySource, /REENTRY|再Entry|rule_reentry/i,
  'Normal Entry EvaluatorへReEntry概念が混入しています。');
assert.doesNotMatch(normalCloseSource, /\b(?:WEEK|DAY|EXPANSION|EXPANSION_LITE)\b/i,
  'Normal Close EvaluatorがWEEK/DAY/Expansion固有判定を参照しています。');
assert.match(sourceText, /dow_confirmation_id: anchor\.dow_confirmation_id \|\| null/,
  'TimeframeStateへ圧縮する際にHSI AnchorのDow Confirmation IDが保持されていません。');
assert.match(sourceText, /hsi_anchor_state\?\.rule_lanes\?\.NORMAL\?\.entry_anchor/,
  '通常実行側が明示的なNORMAL Rule Lane Anchorを参照していません。');

const hook = `
  window.__fxNormalRuleLaneTest = {
    normalizeAllRows,
    simulationRunDraftFromProfile,
    buildVisibleRangeSimulationRun,
    buildEmptySimulationTrace,
    validateSimulationRunDraft,
    normalRuleLaneEntryDecision,
    normalRuleLaneCloseDecision,
    m5RuleLanePolicy
  };
`;
const closeIndex = sourceText.lastIndexOf('})();');
assert.ok(closeIndex > 0, 'Plugin IIFE終端を検出できません。');
const instrumented = sourceText.slice(0, closeIndex) + hook + sourceText.slice(closeIndex);
const context = {
  window: {},
  console,
  setTimeout,
  clearTimeout,
  URL,
  structuredClone,
  Intl,
  Date,
  Math,
  JSON,
  Map,
  Set,
  Promise,
  requestAnimationFrame: callback => setTimeout(callback, 0)
};
vm.runInNewContext(instrumented, context, { filename: pluginPath });
const api = context.window.__fxNormalRuleLaneTest;
assert.ok(api, 'Rule Laneテスト用API公開に失敗しました。');

const m5Source = JSON.parse(fs.readFileSync(m5Path, 'utf8'));
const d1Source = JSON.parse(fs.readFileSync(d1Path, 'utf8'));
const profile = JSON.parse(fs.readFileSync(profilePath, 'utf8'));
const validation = api.validateSimulationRunDraft(profile);
assert.equal(validation.valid, true, `Run Profileが無効です:\n${validation.errors.join('\n')}`);

const lanePolicy = api.m5RuleLanePolicy(profile.m5_execution_policy);
assert.equal(lanePolicy.active_entry_rule_lane, 'NORMAL');
assert.equal(lanePolicy.shared_fact_source, 'TIMEFRAME_STATE_SNAPSHOT');
assert.equal(lanePolicy.close_lane_source, 'OPEN_TRADE_RULE_LANE');
assert.deepEqual(Array.from(lanePolicy.lanes.NORMAL.allowed_actions), ['ENTRY', 'FULL_CLOSE', 'STOP_CLOSE']);
assert.ok(!lanePolicy.lanes.NORMAL.allowed_actions.includes('REENTRY'));
assert.ok(!lanePolicy.lanes.NORMAL.allowed_actions.includes('ADD_ON'));

// Pure evaluator isolation: upper/Expansion factsを渡してもNormal Entry結果は変わらない。
function makeEntryInput(extra = {}) {
  return {
    portfolio: { trades: [], positions: [], normal_entry_opportunities: [], used_dow_confirmation_ids: [] },
    referenceMs: Date.parse('2025-10-30T09:44:00+09:00'),
    referenceTime: '2025-10-30 09:44',
    price: 153.498,
    direction: 'LONG',
    confirmationSide: 'LONG',
    normalFacts: {
      entry_direction_ready: true,
      cycle_guard_passed: true,
      h4_cycle_late: false,
      h1_cycle_late: false,
      h4_t3_ready: true,
      h1_t3_ready: true,
      h4_h1_t3_aligned: true,
      m5_dow_aligned: true
    },
    dowConfirmation: {
      confirmation_id: 'normal_dow_confirmation_test_001',
      direction: 'UP',
      confirmed_at: '2025-10-30 09:44',
      confirmed_at_ms: Date.parse('2025-10-30T09:44:00+09:00'),
      breakout_threshold_point_id: 'swing_high_threshold_test_001',
      breakout_threshold_price: 153.135
    },
    entryResolution: {
      status: 'RESOLVED_REFERENCE',
      anchor_id: 'normal_anchor_test_001',
      anchor: {
        anchor_id: 'normal_anchor_test_001',
        price: 152.164,
        direction: 'UP',
        dow_confirmation_id: 'normal_dow_confirmation_test_001'
      }
    },
    entryAnchor: {
      anchor_id: 'normal_anchor_test_001',
      price: 152.164,
      direction: 'UP',
      dow_confirmation_id: 'normal_dow_confirmation_test_001'
    },
    anchorPrice: 152.164,
    r2Touch: {
      touched: true,
      entry_price: 152.698,
      passed_before_bar: true,
      open: 153.300
    },
    policy: profile.m5_execution_policy,
    minEntryLabel: 'R2',
    hsiNotReachedReasonCode: 'HSI_R2_NOT_REACHED',
    ...extra
  };
}
const normalOnlyDecision = api.normalRuleLaneEntryDecision(makeEntryInput());
const noisyUpperDecision = api.normalRuleLaneEntryDecision(makeEntryInput({
  upperDecision: {
    no_trade: { active: true },
    entry_policy: { normal_entry: { status: 'BLOCKED' }, expansion_entry: { status: 'ALLOW_SEARCH' } },
    WEEK: { status: 'NO_TRADE' },
    DAY: { status: 'NO_TRADE' },
    expansion: { confirmed: true }
  }
}));
assert.equal(normalOnlyDecision.action, 'ENTRY', 'Normal Entry Evaluatorの基準ケースがENTRYになりません。');
assert.equal(noisyUpperDecision.action, 'ENTRY', 'WEEK/DAY/Expansion情報がNormal Entry結果へ混入しています。');
assert.equal(noisyUpperDecision.rule_lane, 'NORMAL');
assert.equal(noisyUpperDecision.evaluator_id, 'normal_m5_entry_evaluator_v0_1');

// Close evaluator isolation: Entry時固定Stop/Target + M5 High/Lowだけで判定する。
const normalPosition = {
  position_id: 'position_test_001',
  rule_lane: 'NORMAL',
  side: 'LONG',
  units_open: 10,
  entry_price: 153.498,
  invalidation_rule: { invalidation_price: 152.164 },
  target_plan: { next_target_label: 'R4', next_target_price: 153.562 }
};
const closeBase = api.normalRuleLaneCloseDecision({
  activePosition: structuredClone(normalPosition),
  currentBar: { high: 153.600, low: 153.490 }
});
const closeWithNoise = api.normalRuleLaneCloseDecision({
  activePosition: structuredClone(normalPosition),
  currentBar: { high: 153.600, low: 153.490 },
  WEEK: { status: 'NO_TRADE' },
  DAY: { status: 'NO_TRADE' },
  expansion: { close_now: false }
});
assert.equal(closeBase.action, 'FULL_CLOSE');
assert.equal(closeWithNoise.action, 'FULL_CLOSE');
assert.equal(closeWithNoise.rule_lane, 'NORMAL');
assert.equal(closeWithNoise.evaluator_id, 'normal_m5_close_evaluator_v0_1');

async function runActualRangeScenario() {
  const allRows = api.normalizeAllRows(m5Source);
  const state = {
    simulationSource: m5Source,
    simulationAllRows: allRows,
    upperMapSource: d1Source,
    upperMapAllRows: api.normalizeAllRows(d1Source),
    simulationRunDraft: api.simulationRunDraftFromProfile(profile),
    windowStart: 560,
    windowSize: 100,
    chartLayout: 'm5_execution',
    upperTimeframe: 'H1',
    upperConfirmBars: 7,
    dayConfirmBars: 45,
    weekConfirmBars: 20,
    confirmBars: 20,
    upperWarmupBars: 200,
    simulationTrace: api.buildEmptySimulationTrace(m5Source),
    simulationRunSnapshot: null,
    simulationRunReferenceOverrideMs: null,
    simulationRunReferenceSource: 'visible_range_step',
    hsiAnnotations: [],
    simulationTraceEvents: []
  };
  const result = await api.buildVisibleRangeSimulationRun(state);
  assert.equal(result.validation.valid, true, `表示範囲Simulation失敗: ${(result.validation.errors || []).join(' / ')}`);
  const run = result.rangeRun;
  assert.ok(run, '表示範囲Simulation結果がありません。');
  const events = run.execution_events || [];
  const firstEntry = events.find(event => event.event_type === 'entry');
  const firstClose = events.find(event => event.event_type === 'close');
  assert.ok(firstEntry, '㉘相当の最初のEntryが発生していません。');
  assert.equal(firstEntry.simulation_time, '2025-10-30 09:44');
  assert.ok(Math.abs(Number(firstEntry.price) - 153.135) < 1e-9, `㉘Entry価格がDow突破閾値と一致しません: ${firstEntry.price}`);
  assert.equal(firstEntry.rule_lane, 'NORMAL');
  assert.equal(firstEntry.evaluator_id, 'normal_m5_entry_evaluator_v0_1');
  assert.equal(firstEntry.execution?.rule_lane, 'NORMAL');
  assert.equal(firstEntry.execution?.close_evaluator_id, 'normal_m5_close_evaluator_v0_1');
  assert.ok(firstEntry.reason_codes.includes('R2_ALREADY_REACHED_AT_DOW_CONFIRMATION'));
  assert.ok(firstEntry.reason_codes.includes('ENTRY_AT_DOW_BREAKOUT_THRESHOLD_AND_R2'));
  assert.ok(Math.abs(Number(firstEntry.execution?.dow_breakout_threshold_price) - 153.135) < 1e-9, 'ExecutionへDow突破閾値が保持されていません。');
  assert.ok(!firstEntry.reason_codes.includes('HSI_ANCHOR_CONFIRMATION_MISMATCH'));

  assert.ok(firstClose, '㉘Entryに対応する通常Closeが発生していません。');
  assert.equal(firstClose.simulation_time, '2025-10-30 09:49');
  assert.ok(Math.abs(Number(firstClose.price) - 153.292) < 1e-9, `通常Close価格が不一致です: ${firstClose.price}`);
  assert.equal(firstClose.rule_lane, 'NORMAL');
  assert.equal(firstClose.evaluator_id, 'normal_m5_close_evaluator_v0_1');
  assert.equal(firstClose.execution?.rule_lane, 'NORMAL');
  assert.equal(firstClose.execution?.close_class, 'CLOSE_OK');

  const normalLaneEntries = events.filter(event => String(event?.rule_lane || event?.execution?.rule_lane || '').toUpperCase() === 'NORMAL' && event.event_type === 'entry');
  const normalLaneReentries = events.filter(event => String(event?.rule_lane || event?.execution?.rule_lane || '').toUpperCase() === 'NORMAL' && event.event_type === 'reentry');
  assert.ok(normalLaneEntries.length >= 2, '複数の独立Normal Entryを確認できません。');
  assert.equal(normalLaneReentries.length, 0, 'NORMAL Rule LaneにReEntry Eventが残っています。');
  assert.equal(Number(run.summary?.reentry_count || 0), 0, '表示範囲集計でNormal EntryがReEntryに分類されています。');
  assert.equal(Number(run.summary?.entry_count || 0), normalLaneEntries.length, 'Normal Entry件数がEntry集計と一致しません。');
  normalLaneEntries.forEach((event, index) => {
    assert.equal(event.execution?.action, 'ENTRY');
    assert.equal(Number(event.execution?.normal_entry_sequence_no || 0), index + 1);
  });

  const diagnostics = run.decision_diagnostics || {};
  assert.equal(diagnostics.upper_context_affects_normal_rule_lane, false);
  assert.ok(Number(diagnostics.rule_lane_counts?.NORMAL || 0) > 0);
  assert.ok(Number(diagnostics.evaluator_counts?.normal_m5_entry_evaluator_v0_1 || 0) > 0);
  assert.ok(Number(diagnostics.evaluator_counts?.normal_m5_close_evaluator_v0_1 || 0) > 0);
  assert.equal(Number(diagnostics.trigger_reason_counts?.HSI_ANCHOR_CONFIRMATION_MISMATCH || 0), 0,
    '㉘シナリオでHSI AnchorとDow Confirmation IDの不一致が残っています。');

  console.log('PASS normal_rule_lane_separation_v0_2_normal_no_reentry');
  console.log(`entry=${firstEntry.simulation_time} ${firstEntry.price} lane=${firstEntry.rule_lane} evaluator=${firstEntry.evaluator_id}`);
  console.log(`close=${firstClose.simulation_time} ${firstClose.price} lane=${firstClose.rule_lane} evaluator=${firstClose.evaluator_id}`);
  console.log(`events=${events.length}`);
  console.log(`normal_lane_steps=${diagnostics.rule_lane_counts.NORMAL}`);
}

runActualRangeScenario().catch(error => {
  console.error(error);
  process.exitCode = 1;
});
