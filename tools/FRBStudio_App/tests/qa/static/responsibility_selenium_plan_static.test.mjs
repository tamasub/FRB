import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { createRequire } from 'node:module';

const ROOT = process.cwd();
const require = createRequire(import.meta.url);
const {
  buildResponsibilityExecutionPlan,
  assertExecutionApproved,
  diffJson,
} = require(path.join(ROOT, 'SeleniumTaste/responsibility_test_plan.js'));

const readJson = rel => JSON.parse(fs.readFileSync(path.join(ROOT, rel), 'utf8'));
const readText = rel => fs.readFileSync(path.join(ROOT, rel), 'utf8');

test('Responsibility Generated Preview is converted to one Selenium document execution plan', () => {
  const plan = buildResponsibilityExecutionPlan({ responsibilityCd: 'data_update_persist' });

  assert.equal(plan.schema_version, 'responsibility_selenium_execution_plan_v0_1');
  assert.equal(plan.expected_def_type, 'JsonDiffExpectedDef');
  assert.equal(plan.summary.test_pattern_count, 6);
  assert.equal(plan.summary.mutation_count, 30);
  assert.equal(plan.summary.invalid_mutation_count, 0);
  assert.equal(plan.summary.main_grid_pattern_count, 4);
  assert.equal(plan.summary.related_grid_pattern_count, 2);
  assert.equal(new Set(plan.mutations.map(item => item.actual_path)).size, 30);
  assert.equal(plan.setup.load_policy, 'LOAD_ONCE');
  assert.equal(plan.setup.save_policy, 'SAVE_ONCE');
  assert.equal(plan.setup.reload_policy, 'RELOAD_ONCE');
  assert.equal(plan.setup.working_copy_policy, 'COPY_BEFORE_EXECUTION');
  assert.equal(plan.setup.cleanup_policy, 'DELETE_AFTER_EXECUTION');
  assert.equal(plan.setup.runner_type, 'SELENIUM_NATIVE_SHELL');

  assert.ok(plan.patterns.some(item => item.ui_target.mode === 'MAIN_GRID' && item.target_data_path === '$.measurement_sessions'));
  assert.ok(plan.patterns.some(item => item.ui_target.mode === 'RELATED_GRID' && item.ui_target.related_grid_id === 'acceptance_thresholds'));
  assert.equal(diffJson(plan.baseline_document, plan.expected.document).length, 30);
});

test('draft Test Input is a hard gate before NativeShell execution', () => {
  const approvedPlan = buildResponsibilityExecutionPlan({ responsibilityCd: 'data_update_persist' });
  const draftPlan = {
    ...approvedPlan,
    execution_ready: false,
    setup: { ...approvedPlan.setup, input_approval_status: 'draft' },
  };
  assert.throws(
    () => assertExecutionApproved(draftPlan),
    /approval_status=draft/,
  );
});

test('Responsibility Test Setup owns Working Copy / Runner policy while Generated Plan stays virtual', () => {
  const document = readJson('data/json/03_tests/responsibilities/responsibility_data_v0_2.json');
  const responsibility = document.responsibilities.find(item => item.responsibility_cd === 'data_update_persist');
  const setup = responsibility.test_setup[0];

  assert.equal(setup.working_copy_policy, 'COPY_BEFORE_EXECUTION');
  assert.equal(setup.working_copy_directory, 'data/json/99_test_runtime');
  assert.equal(setup.cleanup_policy, 'DELETE_AFTER_EXECUTION');
  assert.equal(setup.runner_type, 'SELENIUM_NATIVE_SHELL');
  assert.equal(Object.hasOwn(responsibility, 'generated_execution_plan'), false);
  assert.equal(Object.hasOwn(responsibility, 'generated_test_patterns'), false);
});

test('SeleniumTaste exposes plan-only and approved execution routes without replacing legacy npm test', () => {
  const packageJson = readJson('SeleniumTaste/package.json');
  const taste = readText('SeleniumTaste/selenium_taste.js');
  const runner = readText('SeleniumTaste/responsibility_selenium_runner.js');
  const planSource = readText('SeleniumTaste/responsibility_test_plan.js');

  assert.equal(packageJson.scripts.test, 'node selenium_taste.js');
  assert.equal(packageJson.scripts['test:responsibility:plan'], 'node responsibility_test_plan.js data_update_persist');
  assert.match(packageJson.scripts['test:responsibility'], /--responsibility data_update_persist/);
  assert.match(taste, /--responsibility/);
  assert.match(taste, /--plan-only/);
  assert.match(runner, /assertExecutionApproved\(plan\)/);
  assert.match(planSource, /COPY_BEFORE_EXECUTION/);
  assert.match(runner, /Unexpected Diff Count/);
});

test('Responsibility Selenium Runner re-acquires Grid rows after redraw and preserves failed Working Copy', () => {
  const runner = readText('SeleniumTaste/responsibility_selenium_runner.js');

  assert.match(runner, /async function waitForGridStable\(/);
  assert.match(runner, /Re-acquire the row on every attempt/);
  assert.match(runner, /err instanceof error\.StaleElementReferenceError/);
  assert.match(runner, /await waitForGridStable\(driver, rowIndex \+ 1\)/);
  assert.match(runner, /let executionCompleted = false/);
  assert.match(runner, /executionCompleted = true/);
  assert.match(runner, /Working Copy preserved for failure analysis/);
});
