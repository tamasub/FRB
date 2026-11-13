import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';

const ROOT = process.cwd();

function readJson(rel) {
  return JSON.parse(fs.readFileSync(path.join(ROOT, rel), 'utf8'));
}

test('Responsibility Diff grid is TestPattern summary with quantity columns only', () => {
  const view = readJson('defs/qa/tests/responsibilities/responsibility_expected_diff_view_def_v0_1.json');
  const sections = view.views?.[0]?.sections ?? [];
  const grid = sections.find(section => section.id === 'test_pattern_results');
  assert.ok(grid);
  assert.equal(grid.dataPath, '$.test_pattern_results');
  assert.equal(grid.keyField, 'test_pattern_id');

  const visible = (grid.fields ?? [])
    .filter(field => field?.grid?.visible === true)
    .map(field => field.field);
  assert.deepEqual(visible, [
    'result_label',
    'guarantee_id',
    'test_pattern_id',
    'case_count',
    'check_count',
    'diff_count',
  ]);
  assert.equal(visible.includes('expected'), false);
  assert.equal(visible.includes('actual'), false);

  const component = (grid.editorComponents ?? []).find(item => item.type === 'responsibility_diff_result_preview');
  assert.ok(component);
  assert.equal(component.caption, 'TestPattern / Result Evidence Preview');
});

test('Saved GRID_AGGREGATE Diff keeps raw checks but exposes 5 TestPattern summaries', () => {
  const diff = readJson('data/json/03_tests/responsibilities/results/grid_aggregate.diff.json');
  assert.equal(diff.checks.length, 9);
  assert.equal(diff.test_pattern_results.length, 5);
  assert.deepEqual(
    diff.test_pattern_results.map(item => [item.test_pattern_id, item.case_count, item.check_count, item.diff_count]),
    [
      ['grid_aggregate_sum_filtered', 2, 2, 0],
      ['grid_aggregate_sum_all', 2, 2, 0],
      ['grid_aggregate_comma_numeric', 1, 1, 0],
      ['grid_aggregate_invalid_exclusion', 3, 3, 0],
      ['grid_aggregate_no_declaration', 1, 1, 0],
    ],
  );
  assert.equal(diff.test_pattern_results[0].checks[0].expected_raw, 146);
  assert.equal(diff.test_pattern_results[0].checks[0].actual_raw, 146);
  assert.match(diff.test_pattern_results[0].checks[0].source, /Grid Header/);
  assert.equal(diff.test_pattern_results[0].planned_pattern.generation_mode, 'AGGREGATE_SCALAR_CASE');
  assert.equal(diff.test_pattern_results[0].planned_pattern.generated_cases[0].expected.value, 146);
});

test('Result Evidence Preview renders only persisted facts and is loaded by index', () => {
  const component = fs.readFileSync(
    path.join(ROOT, 'wwwroot/js/components/responsibility/responsibility_diff_result_preview_component.js'),
    'utf8',
  );
  const index = fs.readFileSync(path.join(ROOT, 'wwwroot/index.html'), 'utf8');

  assert.match(component, /EXECUTION EVIDENCE/);
  assert.match(component, /① 対象値の入力状況/);
  assert.match(component, /② 集計へ投入/);
  assert.match(component, /③ Expected Result/);
  assert.match(component, /④ Actual/);
  assert.match(component, /⑤ Diff/);
  assert.match(component, /const checks = Array\.isArray\(row\.checks\)/);
  assert.doesNotMatch(component, /responsibility_test_preview_service/);
  assert.match(index, /responsibility_diff_result_preview_component\.js/);
});

test('Responsibility Diff summary exposes execution error separately from TestPattern results', () => {
  const view = readJson('defs/qa/tests/responsibilities/responsibility_expected_diff_view_def_v0_1.json');
  const summary = view.views?.[0]?.sections?.find(section => section.id === 'summary');
  const fields = (summary?.fields ?? []).map(field => field.field);
  assert.ok(fields.includes('execution_status'));
  assert.ok(fields.includes('execution_error_count'));
  assert.ok(fields.includes('firstExecutionError.execution_phase'));
  assert.ok(fields.includes('firstExecutionError.actual'));
});
