const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const assert = require('node:assert/strict');

const root = path.resolve(process.argv[2] || process.cwd());
function artifactPath(...parts) {
  const normalized = path.join(root, ...parts);
  if (fs.existsSync(normalized)) return normalized;
  const windowsEntry = path.join(root, parts.join('\\'));
  if (fs.existsSync(windowsEntry)) return windowsEntry;
  throw new Error(`テスト対象ファイルが見つかりません: ${parts.join('/')}`);
}

const builderPath = artifactPath('studio_overlays', 'gpt_fx_lab', 'simulation', 'tools', 'build_entry_result_rows_v0_1.cjs');
const catalogPath = artifactPath('studio_overlays', 'gpt_fx_lab', 'simulation', 'fx_simulation_reason_rule_catalog_v0_1.json');
const builder = require(builderPath);
const catalog = JSON.parse(fs.readFileSync(catalogPath, 'utf8'));

assert.equal(builder.SCHEMA_VERSION, 'fx_batch_entry_result_rows_v0_1');

const fixture = {
  schema_version: 'fx_batch_simulation_run_v0_1',
  kind: 'fx_batch_simulation_run',
  batch_run_id: 'batch_test',
  status: 'stopped',
  rule_version: 'rule_test',
  app_version: 'app_test',
  result_hash: 'source_hash',
  cases: [{
    case_id: 'case_001',
    execution_events: [
      {
        event_id: 'normal_entry', event_type: 'entry', case_step_no: 10,
        simulation_time: '2026-01-01 10:00', trade_id: 'trade_0001', rule_lane: 'NORMAL',
        summary: '通常Entry',
        reason_codes: ['M5_DOW_CONFIRMATION_EVENT_AVAILABLE', 'HSI_R2_FIRST_TOUCH', 'POSITION_LIFECYCLE_OPENED'],
        rule_ids: ['rule_normal_entry_first_r2_touch_after_confirmation'],
        execution: { side: 'LONG', units: 10, entry_price: 150, entry_level: 'R2', target_label: 'R2.5', target_price: 151, stop_price: 149, initial_risk_jpy: 10000 }
      },
      {
        event_id: 'lite_entry', event_type: 'entry', case_step_no: 11,
        simulation_time: '2026-01-01 10:05', trade_id: 'trade_0001', rule_lane: 'EXPANSION_LITE',
        summary: 'Lite Entry',
        reason_codes: ['EXPANSION_LITE_ENTRY_EXECUTED', 'EXPANSION_LITE_H4_H1_T3_SIDE_ALIGNED'],
        rule_ids: [],
        execution: { side: 'LONG', units: 10, entry_price: 200, entry_level: 'R3', target_label: 'R5', target_price: 205, stop_price: 198, initial_risk_jpy: 20000 }
      },
      {
        event_id: 'lite_add', event_type: 'add_on', case_step_no: 12,
        simulation_time: '2026-01-01 10:10', trade_id: 'trade_0001', rule_lane: 'EXPANSION_LITE',
        summary: 'Lite Add-on', reason_codes: ['EXPANSION_LITE_ADD_ON_LEVEL_TOUCHED'], rule_ids: [],
        execution: { side: 'LONG', units: 2, price: 202, add_on_levels: ['R3.5'] }
      },
      {
        event_id: 'normal_close', event_type: 'close', case_step_no: 16,
        simulation_time: '2026-01-01 10:30', trade_id: 'trade_0001', rule_lane: 'NORMAL',
        summary: 'R2.5到達', reason_codes: ['CLOSE_OK_NEXT_HSI_BOUNDARY'], rule_ids: [],
        execution: { units: 10, price: 151, close_class: 'CLOSE_OK', realized_profit_jpy: 10000, risk_multiple: 1, profit_vs_initial_risk_pct: 100 }
      },
      {
        event_id: 'lite_close', event_type: 'close', case_step_no: 20,
        simulation_time: '2026-01-01 10:50', trade_id: 'trade_0001', rule_lane: 'EXPANSION_LITE',
        summary: 'T3 Exit', reason_codes: ['EXPANSION_LITE_T3_EXIT'], rule_ids: [],
        execution: { units: 12, price: 199, close_class: 'T3_EXIT', exit_type: 'T3_EXIT', exit_reason_code: 'EXPANSION_LITE_T3_EXIT', realized_profit_jpy: -14000, risk_multiple: -0.7, profit_vs_initial_risk_pct: -70 }
      },
      {
        event_id: 'open_entry', event_type: 'entry', case_step_no: 30,
        simulation_time: '2026-01-01 11:40', trade_id: 'trade_0002', rule_lane: 'NORMAL',
        summary: '未決済Entry', reason_codes: ['M5_DOW_CONFIRMATION_EVENT_AVAILABLE'], rule_ids: [],
        execution: { side: 'SHORT', units: 10, entry_price: 155, entry_level: 'R2', target_price: 154, stop_price: 156 }
      }
    ]
  }]
};

const projection = builder.buildEntryResultProjection(fixture, catalog, 'batch_test.json', '2026-01-01T00:00:00.000Z');
assert.equal(projection.entry_result_rows.length, 3, 'Lane+Trade ID単位で3行になる');
assert.equal(projection.view_def, 'overlay/gpt_fx_lab/view_defs/fx_batch_entry_results_view_def_v0_1.json');
assert.equal(projection.summary.closed_trade_count, 2);
assert.equal(projection.summary.open_trade_count, 1);
assert.equal(projection.summary.success_count, 1);
assert.equal(projection.summary.failure_count, 1);
assert.equal(projection.summary.realized_profit_jpy, -4000);

const normal = projection.entry_result_rows.find((row) => row.rule_lane === 'NORMAL' && row.trade_id === 'trade_0001');
assert.equal(normal.result_code, 'SUCCESS');
assert.equal(normal.result_label, '成功');
assert.equal(normal.profit_loss_label, '利益');
assert.equal(normal.holding_minutes, 30);
assert.equal(normal.holding_step_count, 6);
assert.match(normal.entry_reason_summary, /M5/);

const lite = projection.entry_result_rows.find((row) => row.rule_lane === 'EXPANSION_LITE');
assert.equal(lite.result_code, 'FAILURE');
assert.equal(lite.add_on_count, 1);
assert.equal(lite.add_on_units, 2);
assert.equal(lite.total_units, 12);
assert.equal(lite.average_entry_price, 200.333333);
assert.equal(lite.exit_type, 'T3_EXIT');
assert.match(lite.add_on_prices_text, /R3\.5/);

const open = projection.entry_result_rows.find((row) => row.trade_id === 'trade_0002');
assert.equal(open.result_code, 'OPEN');
assert.equal(open.success, null);
assert.equal(open.realized_profit_jpy, null);

const historicalBatchCandidates = [
  path.join(root, 'studio_overlays', 'gpt_fx_lab', 'simulattion_集計', 'batch_20260712_230503.json'),
  path.join(root, ['studio_overlays', 'gpt_fx_lab', 'simulattion_集計', 'batch_20260712_230503.json'].join('\\'))
];
const actualBatchPath = historicalBatchCandidates.find(candidate => fs.existsSync(candidate)) || null;
let actual = null;
if (actualBatchPath) {
  const actualBatch = JSON.parse(fs.readFileSync(actualBatchPath, 'utf8'));
  actual = builder.buildEntryResultProjection(actualBatch, catalog, path.basename(actualBatchPath), '2026-01-01T00:00:00.000Z');
  assert.equal(actual.entry_result_rows.length, actualBatch.cases[0].summary.entry_count);
  assert.equal(actual.entry_result_rows.length, 115, '実データはEntry 115件 = 115行');
  assert.equal(actual.summary.closed_trade_count, 115);
  assert.equal(actual.summary.open_trade_count, 0);
  assert.equal(actual.summary.success_count, 70);
  assert.equal(actual.summary.failure_count, 45);
  assert.equal(Math.round(actual.summary.realized_profit_jpy), 27772);
  assert.equal(actual.summary.lane_summaries.NORMAL.entry_count, 61);
  assert.equal(actual.summary.lane_summaries.EXPANSION_LITE.entry_count, 54);
} else {
  console.log('INFO historical batch_20260712_230503.json is not included; fixed historical projection assertions were skipped.');
}

const tempDir = fs.mkdtempSync(path.join(os.tmpdir(), 'entry-result-rows-'));
const cliInput = path.join(tempDir, 'batch_20260101_000000.json');
fs.writeFileSync(cliInput, JSON.stringify(fixture), 'utf8');
const exitCode = builder.runCli([cliInput, '--catalog', catalogPath, '--output-dir', tempDir]);
assert.equal(exitCode, 0);
const outputPath = path.join(tempDir, 'batch_20260101_000000_entry_results.json');
assert.equal(fs.existsSync(outputPath), true, 'CLIでsidecar JSONが生成される');
const cliOutput = JSON.parse(fs.readFileSync(outputPath, 'utf8'));
assert.equal(cliOutput.entry_result_rows.length, 3);
assert.equal(cliOutput.source_batch_file, 'batch_20260101_000000.json');
assert.equal(cliOutput.view_def, 'overlay/gpt_fx_lab/view_defs/fx_batch_entry_results_view_def_v0_1.json');

console.log('PASS entry_result_rows_builder_v0_1');
console.log(actual
  ? `rows=${actual.summary.entry_result_row_count}, success=${actual.summary.success_count}, failure=${actual.summary.failure_count}, pnl=${actual.summary.realized_profit_jpy}`
  : `synthetic_rows=${projection.entry_result_rows.length}, historical_fixture=not_included`);
