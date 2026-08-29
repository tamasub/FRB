import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { createRequire } from 'node:module';

const ROOT = process.cwd();
const require = createRequire(import.meta.url);
const { buildResponsibilityExecutionPlan, assertExecutionApproved } = require(path.join(ROOT, 'SeleniumTaste/responsibility_test_plan.js'));
const readJson = rel => JSON.parse(fs.readFileSync(path.join(ROOT, rel), 'utf8'));
const readText = rel => fs.readFileSync(path.join(ROOT, rel), 'utf8');

test('SEARCH_FILTER Generated Cases are converted to a Selenium search execution plan', () => {
  const plan = buildResponsibilityExecutionPlan({ responsibilityCd: 'search_filter' });
  assert.equal(plan.schema_version, 'responsibility_selenium_execution_plan_v0_2');
  assert.equal(plan.execution_kind, 'SEARCH_FILTER');
  assert.equal(plan.expected_def_type, 'StateExpectedDef');
  assert.equal(plan.summary.test_pattern_count, 13);
  assert.equal(plan.summary.generated_case_count, 13);
  assert.equal(plan.search_cases.length, 13);
  assert.equal(plan.summary.main_grid_case_count, 13);
  assert.equal(plan.summary.related_grid_case_count, 0);
  assert.ok(plan.search_cases.every(item => item.target_data_path === '$.measurement_sessions'));
  assert.ok(plan.search_cases.every(item => item.ui_target.mode === 'MAIN_GRID'));

  const contains = plan.search_cases.find(item => item.pattern_id === 'search_filter_string_contains');
  assert.deepEqual(contains.criteria, { operator: 'contains', value: 'Alpha' });
  assert.deepEqual(contains.expected.indexes, [0,2,5]);
  assert.deepEqual(contains.expected.row_ids, ['frb_search_20260829_001','frb_search_20260829_003','frb_search_20260829_006']);
});

test('SEARCH_FILTER Selenium lifecycle is LOAD_ONCE + RESET_AFTER_EACH and approved input is executable', () => {
  const plan = buildResponsibilityExecutionPlan({ responsibilityCd: 'search_filter' });
  assert.equal(plan.setup.load_policy, 'LOAD_ONCE');
  assert.equal(plan.setup.pattern_isolation_policy, 'RESET_AFTER_EACH');
  assert.equal(plan.setup.save_policy, 'NONE');
  assert.equal(plan.setup.reload_policy, 'NONE');
  assert.equal(plan.setup.working_copy_policy, 'NONE');
  assert.equal(plan.setup.runner_type, 'SELENIUM_NATIVE_SHELL');
  assert.equal(plan.execution_ready, true);
  assert.doesNotThrow(() => assertExecutionApproved(plan));
});

test('Search UI exposes semantic operator and result observation hooks without caption coupling', () => {
  const ui = readText('wwwroot/js/services/search_ui_controller.js');
  const grid = readText('wwwroot/js/renderers/grid_detail.js');
  const runner = readText('SeleniumTaste/responsibility_selenium_runner.js');
  const pkg = readJson('SeleniumTaste/package.json');

  assert.match(ui, /dataset\.searchOperatorId = id/);
  assert.match(grid, /dataset\.sourceIndex = String\(index\)/);
  assert.match(grid, /dataset\.rowKey = String\(row\[rowKeyField\]\)/);
  assert.match(runner, /runSearchResponsibilitySelenium/);
  assert.match(runner, /RESET_AFTER_EACH/);
  assert.match(runner, /StateExpectedDef \/ Row IDs/);
  assert.match(runner, /StateExpectedDef \/ Indexes/);
  assert.equal(pkg.scripts['test:responsibility:search:plan'], 'node responsibility_test_plan.js search_filter');
  assert.equal(pkg.scripts['test:responsibility:search'], 'node selenium_taste.js --responsibility search_filter');
});

test('Responsibility Search Setup keeps the explicitly approved human gate', () => {
  const document = readJson('data/json/03_tests/responsibilities/responsibility_data_v0_2.json');
  const responsibility = document.responsibilities.find(item => item.responsibility_cd === 'search_filter');
  const setup = responsibility.test_setup[0];
  assert.equal(setup.input_approval_status, 'approved');
  assert.equal(setup.runner_type, 'SELENIUM_NATIVE_SHELL');
  assert.ok(responsibility.in_scope.includes('Generated Caseを標準検索UIへ投入するSelenium NativeShell E2E'));
  assert.ok(responsibility.out_of_scope.includes('Date / Datetime検索のGenerated Case E2E（Phase 2）'));
});
