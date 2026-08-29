'use strict';

// Internal diagnostic runner for Responsibility Generated Cases -> GridAggregator.
// This is intentionally NOT the acceptance boundary for grid_aggregate.
// The canonical acceptance runner observes the Grid Header through NativeShell/Selenium.

const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const { pathToFileURL } = require('node:url');

const {
  APP_ROOT,
  buildResponsibilityExecutionPlan,
  formatPlanSummary,
  getByActualPath,
} = require('./responsibility_test_plan');

function assertFileExists(filePath, label) {
  if (!fs.existsSync(filePath)) throw new Error(`${label} が見つかりません: ${filePath}`);
}

function assertPass(passed, label, detail=null) {
  console.log(`${label}: ${passed ? 'PASS' : 'FAIL'}`);
  if (!passed) throw new Error(detail ? `${label} failed: ${detail}` : `${label} failed`);
}

function loadGridAggregator(sourceFile) {
  const absolute = path.resolve(APP_ROOT, sourceFile);
  assertFileExists(absolute, 'GridAggregator source');
  const source = fs.readFileSync(absolute, 'utf8');
  const sandbox = {
    console,
    Object,
    Array,
    Set,
    Map,
    Number,
    String,
    Boolean,
    Math,
  };
  sandbox.globalThis = sandbox;
  vm.createContext(sandbox);
  vm.runInContext(source, sandbox, { filename: sourceFile });
  if (!sandbox.GridAggregator || typeof sandbox.GridAggregator.build !== 'function') {
    throw new Error(`GridAggregator.build could not be loaded from ${sourceFile}`);
  }
  return sandbox.GridAggregator;
}

async function loadExpectedCompare() {
  const modulePath = path.resolve(
    APP_ROOT,
    'tests/responsibilities/lib/responsibility_expected_compare_strategies.mjs',
  );
  assertFileExists(modulePath, 'ExpectedDef CompareStrategy');
  return import(pathToFileURL(modulePath).href);
}

function assertScalarExpectedCase(generatedCase) {
  const expectedDef = String(generatedCase?.expected_def_type ?? '');
  if (expectedDef !== 'ScalarExpectedDef') {
    throw new Error(`GRID_AGGREGATE requires ScalarExpectedDef: ${generatedCase?.case_id ?? ''} / ${expectedDef}`);
  }
  const keys = Object.keys(generatedCase?.expected ?? {});
  if (keys.length !== 1 || keys[0] !== 'value') {
    throw new Error(`ScalarExpectedDef shape mismatch: ${generatedCase?.case_id ?? ''} / keys=${keys.join(',')}`);
  }
}

async function compareGeneratedCase({ plan, pattern, generatedCase, actualResult, buildExpectedChecks }) {
  assertScalarExpectedCase(generatedCase);
  const actualValue = getByActualPath(actualResult, generatedCase.actual_path);
  const comparePattern = {
    responsibility_cd: plan.responsibility_cd,
    test_pattern_id: generatedCase.case_id,
    expected_def_type: generatedCase.expected_def_type,
    expected: generatedCase.expected,
  };
  const checks = buildExpectedChecks(comparePattern, { value: actualValue });
  if (checks.length !== 1) {
    throw new Error(`ScalarExpectedDef must produce exactly one check: ${generatedCase.case_id}`);
  }
  const check = checks[0];
  const label = `${check.expected_def_type} / ${pattern.target_field}.${generatedCase.metric}`;
  assertPass(
    check.pass === true,
    label,
    `${check.message}; Expected=${check.expected}, Actual=${check.actual}`,
  );
}

async function runAggregateResponsibility({ responsibilityCd='grid_aggregate', planOnly=false }={}) {
  const plan = buildResponsibilityExecutionPlan({ responsibilityCd });
  console.log(formatPlanSummary(plan));
  if (plan.execution_kind !== 'GRID_AGGREGATE') {
    throw new Error(`Not a GRID_AGGREGATE execution plan: ${plan.execution_kind}`);
  }
  if (planOnly) return { plan, executed: false };

  if (!plan?.execution_ready) throw new Error(`Responsibility execution is blocked: Test Input approval_status=${plan?.setup?.input_approval_status ?? 'unknown'}`);
  const GridAggregator = loadGridAggregator('wwwroot/js/responsibilities/grid_aggregator.js');
  const { buildExpectedChecks } = await loadExpectedCompare();

  for (const pattern of plan.patterns ?? []) {
    const runtimeInput = pattern.runtime_input ?? {};
    console.log(`Aggregate Pattern: ${pattern.pattern_id} / field=${pattern.target_field} / scope=${pattern.aggregate_scope || 'none'}`);

    // Actual side: call only the production responsibility implementation.
    // Expected values were already derived independently in the execution plan.
    const actualResult = GridAggregator.build({
      fields: [runtimeInput.field],
      currentRows: runtimeInput.current_rows,
      filteredRows: runtimeInput.filtered_rows,
    });

    for (const generatedCase of pattern.generated_cases ?? []) {
      await compareGeneratedCase({
        plan,
        pattern,
        generatedCase,
        actualResult,
        buildExpectedChecks,
      });
    }
  }

  console.log(`Internal Pure Function Runner: ${plan.responsibility_cd} ALL PASS`);
  return { plan, executed: true };
}

if (require.main === module) {
  const responsibilityCd = process.argv[2] || 'grid_aggregate';
  const planOnly = process.argv.includes('--plan-only');
  runAggregateResponsibility({ responsibilityCd, planOnly }).catch((err) => {
    console.error(err);
    process.exitCode = 1;
  });
}

module.exports = {
  runAggregateResponsibility,
  loadGridAggregator,
  assertScalarExpectedCase,
};
