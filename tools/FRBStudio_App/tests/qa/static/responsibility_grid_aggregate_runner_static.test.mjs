import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { execFileSync } from 'node:child_process';
import { createRequire } from 'node:module';

const ROOT = process.cwd();
const require = createRequire(import.meta.url);
const { buildResponsibilityExecutionPlan } = require(path.join(ROOT, 'SeleniumTaste/responsibility_test_plan.js'));

test('GRID_AGGREGATE execution plan is 5 Pattern / 9 Case and targets Selenium Grid Header boundary', () => {
  const plan = buildResponsibilityExecutionPlan({ responsibilityCd: 'grid_aggregate' });
  assert.equal(plan.execution_kind, 'GRID_AGGREGATE');
  assert.equal(plan.expected_def_type, 'ScalarExpectedDef');
  assert.equal(plan.setup.runner_type, 'SELENIUM_NATIVE_SHELL');
  assert.equal(plan.setup.pattern_isolation_policy, 'UI_FILTER_ONCE');
  assert.equal(plan.execution_ready, true);
  assert.equal(plan.summary.test_pattern_count, 5);
  assert.equal(plan.summary.generated_case_count, 9);
  assert.equal(plan.interface_name, 'Grid Aggregate Header observable boundary');
  assert.ok(plan.patterns.every(pattern => pattern.guarantee_id === 'grid_aggregate_g001'));
  assert.ok(plan.patterns.every(pattern => pattern.ui_target?.mode === 'MAIN_GRID'));
  assert.ok(plan.aggregate_cases.every(item => item.expected_def_type === 'ScalarExpectedDef'));
  assert.ok(plan.aggregate_cases.every(item => Object.keys(item.expected ?? {}).join(',') === 'value'));
});

test('GRID_AGGREGATE filtered indexes stay typed and derive one visible UI filter precondition', () => {
  const document = JSON.parse(fs.readFileSync(path.join(ROOT, 'data/json/03_tests/responsibilities/responsibility_data_v0_2.json'), 'utf8'));
  const responsibility = document.responsibilities.find(item => item.responsibility_cd === 'grid_aggregate');
  const filtered = responsibility.test_pattern_definitions.find(item => item.pattern_def_id === 'grid_aggregate_sum_filtered');
  assert.deepEqual(filtered.filtered_row_indexes, [0, 1, 2]);

  const plan = buildResponsibilityExecutionPlan({ responsibilityCd: 'grid_aggregate' });
  assert.deepEqual(plan.aggregate_ui_filter, {
    required: true,
    target_data_path: '$.aggregate_rows',
    field: 'row_id',
    operator_id: 'not_equals',
    criteria: { value: 'agg_004' },
    expected_indexes: [0, 1, 2],
    expected_count: 3,
    derivation: 'EXCLUDE_SINGLE_ROW_BY_KEY',
  });
});

test('Aggregate Grid Header exposes observable metric hooks and human-readable counts', () => {
  const source = fs.readFileSync(path.join(ROOT, 'wwwroot/js/renderers/grid_detail.js'), 'utf8');
  assert.match(source, /dataset\.aggregateSourceCount/);
  assert.match(source, /dataset\.aggregateValidCount/);
  assert.match(source, /dataset\.aggregateIgnoredCount/);
  assert.match(source, /有効 \$\{aggregate\.valid_count\}件/);
  assert.match(source, /数値対象外 \$\{aggregate\.ignored_count\}件/);
});

test('Aggregate Selenium runner contains scalar display normalization and Grid Header observation', () => {
  const source = fs.readFileSync(path.join(ROOT, 'SeleniumTaste/responsibility_selenium_runner.js'), 'utf8');
  assert.match(source, /function parseAggregateDisplayValue/);
  assert.match(source, /grid-aggregate-cell\[data-aggregate-field/);
  assert.match(source, /data-aggregate-source-count/);
  assert.match(source, /data-aggregate-valid-count/);
  assert.match(source, /data-aggregate-ignored-count/);
  assert.match(source, /Responsibility E2E: \$\{plan\.responsibility_cd\} ALL PASS/);
});


test('GRID_AGGREGATE canonical command uses Selenium and fixture exposes the generated filter key', () => {
  const pkg = JSON.parse(fs.readFileSync(path.join(ROOT, 'SeleniumTaste/package.json'), 'utf8'));
  assert.equal(pkg.scripts['test:responsibility:aggregate'], 'node selenium_taste.js --responsibility grid_aggregate');
  assert.equal(pkg.scripts['test:responsibility:aggregate:internal'], 'node responsibility_aggregate_runner.js grid_aggregate');

  const document = JSON.parse(fs.readFileSync(path.join(ROOT, 'data/json/03_tests/responsibilities/responsibility_data_v0_2.json'), 'utf8'));
  const responsibility = document.responsibilities.find(item => item.responsibility_cd === 'grid_aggregate');
  assert.equal(responsibility.test_level, 'E2E');
  assert.equal(responsibility.interface_name, 'Grid Aggregate Header observable boundary');

  const viewDef = JSON.parse(fs.readFileSync(path.join(ROOT, 'defs/frb/frb_grid_aggregate_test_view_def_v0_1.json'), 'utf8'));
  const grid = viewDef.views[0].sections[0];
  const rowId = grid.fields.find(item => item.field === grid.keyField);
  assert.equal(rowId.search?.visible, true);
  assert.equal(rowId.search?.operator, 'equals');
});

test('GRID_AGGREGATE pure function runner remains an internal diagnostic, not the acceptance boundary', () => {
  const output = execFileSync(
    process.execPath,
    ['SeleniumTaste/responsibility_aggregate_runner.js', 'grid_aggregate'],
    { cwd: ROOT, encoding: 'utf8' },
  );
  assert.match(output, /ScalarExpectedDef \/ profit\.value: PASS/);
  assert.match(output, /ScalarExpectedDef \/ dirty_amount\.ignored_count: PASS/);
  assert.match(output, /Internal Pure Function Runner: grid_aggregate ALL PASS/);
});
