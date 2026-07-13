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

const pluginPath = artifactPath('studio_overlays','gpt_fx_lab','plugins','fx_chart_viewer','plugin.js');
const manifestPath = artifactPath('studio_overlays','gpt_fx_lab','plugins','fx_chart_viewer','plugin.json');
const source = fs.readFileSync(pluginPath, 'utf8');
const manifest = JSON.parse(fs.readFileSync(manifestPath, 'utf8'));

assert.equal(manifest.version, '0.9.1.05');
assert.equal(manifest.display_policy.batch_simulation_runner.enabled, true);
assert.equal(manifest.display_policy.batch_simulation_runner.execution_mode, 'SEQUENTIAL_CASES');
assert.equal(manifest.display_policy.batch_simulation_runner.show_cumulative_realized_profit, true);
assert.equal(manifest.display_policy.batch_simulation_runner.show_unrealized_profit, true);
assert.equal(manifest.display_policy.batch_simulation_runner.result_persistence_mode, 'FULL_JSON_SINGLE_FILE_WITH_FALLBACK');
assert.equal(manifest.display_policy.batch_simulation_runner.progress_yield_every_bars, 50);
assert.equal(manifest.chart_viewer_policy.batch_simulation_cumulative_realized_profit_always_visible, true);

const hook = `window.__batchSimulationTest={
  batchSimulationRowPlan,
  batchSimulationPrimaryWarmupBars,
  batchSimulationLaneSummaries,
  batchSimulationSummaryWithState,
  rangeExecutionSummary,
  mergeBatchSimulationSummaries,
  m5ExecutionTargetDirectionValid,
  m5ExecutionBarFill,
  combineBatchSimulationResults,
  batchSimulationCsv,
  batchSimulationShouldExecuteCase,
  batchSimulationExistingCaseByPath,
  validateBatchSimulationDraft,
  batchSimulationFormatJpy
};`;
const closeIndex = source.lastIndexOf('})();');
assert.ok(closeIndex > 0, 'Plugin IIFE終端を検出できません。');
const instrumented = source.slice(0, closeIndex) + hook + source.slice(closeIndex);
const context = {
  window: {}, console, setTimeout, clearTimeout, URL, structuredClone, Intl, Date, Math, JSON, Map, Set, Promise,
  globalThis: {},
};
vm.runInNewContext(instrumented, context, { filename: pluginPath });
const api = context.window.__batchSimulationTest;

const profile = {
  timeframe_profiles: [
    { timeframe: 'H4', source_mapping: { source_dataset_role: 'primary' }, warmup: { bars: 100 } },
    { timeframe: 'H1', source_mapping: { source_dataset_role: 'primary' }, warmup: { bars: 100 } },
    { timeframe: 'M5', source_mapping: { source_dataset_role: 'primary' }, warmup: { bars: 20 } }
  ]
};
assert.equal(api.batchSimulationPrimaryWarmupBars(profile), 4800, 'H4 100本をM5換算した4800本が最大Warmup');

const bars = [];
for (let i = 0; i < 6000; i += 1) {
  const ms = Date.parse('2025-01-01T00:00:00Z') + i * 5 * 60 * 1000;
  const d = new Date(ms);
  bars.push({
    datetime: d.toISOString().slice(0, 16).replace('T', ' '),
    open: 150, high: 151, low: 149, close: 150.5
  });
}
const sourceData = { bars, row_count: bars.length, date_from: bars[0].datetime, date_to: bars[bars.length - 1].datetime };
const rowPlan = api.batchSimulationRowPlan(sourceData, {
  period_mode: 'CUSTOM',
  period_from: bars[5000].datetime,
  period_to: bars[5010].datetime
}, profile);
assert.equal(rowPlan.valid, true);
assert.equal(rowPlan.warmup_bar_count, 4800);
assert.equal(rowPlan.target_bar_count, 11);
assert.equal(rowPlan.process_rows.length, 4811);

const events = [
  { event_type: 'close', rule_lane: 'NORMAL', execution: { realized_profit_jpy: 1200, exit_type: 'TARGET_EXIT' } },
  { event_type: 'close', rule_lane: 'EXPANSION_LITE', execution: { realized_profit_jpy: 3500, exit_type: 'T3_EXIT' } },
  { event_type: 'stop_close', rule_lane: 'NORMAL', execution: { realized_profit_jpy: -400, exit_type: 'STOP_EXIT' } }
];
const lanes = api.batchSimulationLaneSummaries(events);
assert.equal(lanes.NORMAL.realized_profit_jpy, 800);
assert.equal(lanes.EXPANSION_LITE.realized_profit_jpy, 3500);
assert.equal(lanes.EXPANSION.realized_profit_jpy, 0);
assert.equal(lanes.NORMAL.close_event_count, 2);
assert.equal(lanes.NORMAL.profit_close_count, 1);
assert.equal(lanes.NORMAL.loss_close_count, 1);
assert.equal(lanes.NORMAL.close_ok_count, 1, 'CloseOK互換項目は利益決済だけ');
assert.equal(lanes.NORMAL.close_miss_count, 1, 'CloseMiss互換項目は損失決済だけ');
assert.equal(lanes.NORMAL.win_rate_pct, 50);
assert.equal(lanes.EXPANSION_LITE.t3_exit_count, 1);

const snapshotWithOpenPosition = {
  position_lifecycle: { portfolio: { positions: [
    { trade_id: 't1', rule_lane: 'EXPANSION_LITE', status: 'OPEN', side: 'SHORT', units_open: 10, entry_price: 153.654, risk_profile: { unit_base_currency_amount: 1000 } },
    { trade_id: 't1', rule_lane: 'EXPANSION_LITE', status: 'OPEN', side: 'SHORT', units_open: 2, entry_price: 153.390, risk_profile: { unit_base_currency_amount: 1000 } }
  ] } }
};
const marked = api.batchSimulationSummaryWithState(events, snapshotWithOpenPosition, 153.30);
assert.equal(Math.round(marked.unrealized_profit_jpy), 3720);
assert.equal(marked.open_position_count, 2);
assert.equal(marked.open_trade_count, 1);
assert.equal(Math.round(marked.total_profit_jpy), 8020);

assert.equal(api.m5ExecutionTargetDirectionValid('SHORT', 154.140, 156.077), false, 'SHORTのTargetがEntryより上なら拒否');
assert.equal(api.m5ExecutionTargetDirectionValid('SHORT', 154.140, 152.077), true);
const impossibleFill = api.m5ExecutionBarFill('SHORT', { open: 154.10, high: 154.176, low: 153.980 }, 153.500, 'TARGET');
assert.equal(impossibleFill.touched, false, 'OHLC外Targetは約定しない');
assert.equal(impossibleFill.execution_price, null);
const validFill = api.m5ExecutionBarFill('SHORT', { open: 154.10, high: 154.176, low: 153.980 }, 154.00, 'TARGET');
assert.equal(validFill.touched, true);
assert.equal(validFill.execution_price, 154.00);

const combined = api.combineBatchSimulationResults([
  { status: 'completed', execution_events: events.slice(0, 2) },
  { status: 'completed', execution_events: events.slice(2) }
]);
assert.equal(combined.realized_profit_jpy, 4300);
assert.equal(combined.case_count, 2);
assert.equal(combined.completed_case_count, 2);
assert.equal(api.batchSimulationFormatJpy(4300), '+4,300円');

const csv = api.batchSimulationCsv({
  cases: [{
    case_id: 'case_001', status: 'completed', dataset: { path: 'studio_overlays/gpt_fx_lab/data/sample.json' },
    period: { from: '2025-01-01', to: '2025-01-31' },
    summary: { execution_event_count: 4, entry_count: 1, reentry_count: 0, add_on_count: 2, close_event_count: 1, exit_count: 0, profit_close_count: 1, loss_close_count: 0, break_even_close_count: 0, win_rate_pct: 100, target_exit_count: 1, t3_exit_count: 0, structural_exit_count: 0, anchor_exit_count: 0, stop_exit_count: 0, realized_profit_jpy: 4300, unrealized_profit_jpy: 700, total_profit_jpy: 5000, open_position_count: 1 },
    lane_summaries: lanes,
    result_hash: 'abc123'
  }]
});
assert.match(csv, /realized_profit_jpy/);
assert.match(csv, /unrealized_profit_jpy/);
assert.match(csv, /win_rate_pct/);
assert.match(csv, /4300/);

const previousBatch = {
  cases: [
    { status: 'completed', dataset: { path: 'studio_overlays/gpt_fx_lab/data/a.json' } },
    { status: 'stopped', dataset: { path: 'studio_overlays/gpt_fx_lab/data/b.json' } },
    { status: 'failed', dataset: { path: 'studio_overlays/gpt_fx_lab/data/c.json' } }
  ]
};
assert.equal(api.batchSimulationShouldExecuteCase(api.batchSimulationExistingCaseByPath(previousBatch, 'overlay/gpt_fx_lab/data/a.json'), 'resume'), false, '完了Caseは再開時に再実行しない');
assert.equal(api.batchSimulationShouldExecuteCase(api.batchSimulationExistingCaseByPath(previousBatch, 'overlay/gpt_fx_lab/data/b.json'), 'resume'), true, '停止Caseは再開対象');
assert.equal(api.batchSimulationShouldExecuteCase(api.batchSimulationExistingCaseByPath(previousBatch, 'overlay/gpt_fx_lab/data/c.json'), 'retry_failed'), true, '失敗Caseは再実行対象');
assert.equal(api.batchSimulationShouldExecuteCase(api.batchSimulationExistingCaseByPath(previousBatch, 'overlay/gpt_fx_lab/data/a.json'), 'retry_failed'), false, '完了Caseは失敗再実行対象外');
assert.match(source, /gpt-fx-chart-batch-pnl-board/);
assert.match(source, /評価損益合計/);
assert.match(source, /利益Close/);
assert.match(source, /損失Close/);
assert.match(source, /保存再試行/);
assert.match(source, /TARGET_DIRECTION_INVALID/);
assert.match(source, /evaluated_reference_keys = \[referenceKey\]/, '評価済み参照は最終Keyだけを保持');
assert.match(source, /fallback_result_api_root/, '完全版JSONのfallback保存経路が必要');
assert.match(source, /const fileName = `\$\{batchRun\.batch_run_id\}\.json`/, 'Batch自動保存は完全版JSON単一ファイル');
assert.doesNotMatch(source, /cases\/\$\{item\.case_id\}\/events\.json/, 'ネスト6分割保存を第一保存経路に残さない');
assert.match(source, /batchSimulationStopRequested/);
assert.match(source, /未完了から再開/);
assert.match(source, /失敗Case再実行/);
assert.match(source, /SEQUENTIAL_CASES/);
assert.equal(manifest.display_policy.batch_simulation_runner.case_internal_rule_lane_mode, 'PARALLEL_INDEPENDENT_PORTFOLIOS');

console.log('PASS batch_simulation_runner_v0_1');
console.log(`warmup=${rowPlan.warmup_bar_count}, target=${rowPlan.target_bar_count}, pnl=${combined.realized_profit_jpy}`);
