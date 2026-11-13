// v0.18.21-json-full-text-search
// JSON-driven minimal Expected tests for ResponsibilityDef interfaces.
// Run from FRBStudio_App root:
//   node tests/responsibilities/responsibility_expected_tests.mjs
// Optional: pass a test data JSON path explicitly as argv[2].

import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import { buildExpectedChecks, toDisplayValue } from './lib/responsibility_expected_compare_strategies.mjs';
import { toStudioDateTime } from './lib/responsibility_datetime_utils.mjs';

const root = process.cwd();
const standardTestDataPath = 'data/json/03_tests/responsibilities/responsibility_expected_first_set/test_patterns/responsibility_expected_test_patterns_data_v0_1.json';
const legacyTestDataPath = 'data/json/03_tests/responsibilities/responsibility_expected_tests_first_set_data_v0_1.json';

function rootPath(relOrAbsPath) {
  return path.isAbsolute(relOrAbsPath) ? relOrAbsPath : path.join(root, relOrAbsPath);
}

function exists(relOrAbsPath) {
  return fs.existsSync(rootPath(relOrAbsPath));
}

function resolveTestDataPath(requestedPath) {
  if (requestedPath) {
    if (exists(requestedPath)) return requestedPath;

    // Compatibility: if old MVP path was passed after v0.18.9 migration,
    // run against the new standard test_area/suite_id/artifact_kind path.
    if (requestedPath === legacyTestDataPath && exists(standardTestDataPath)) {
      console.warn(`[compat] ${legacyTestDataPath} was not found. Using ${standardTestDataPath}`);
      return standardTestDataPath;
    }

    throw new Error(`Test data JSON not found: ${requestedPath}`);
  }

  // Default run should prefer the v0.18.9 standard layout, but also tolerate
  // a workspace where only the v0.18.8 MVP file exists.
  if (exists(standardTestDataPath)) return standardTestDataPath;
  if (exists(legacyTestDataPath)) {
    console.warn(`[compat] ${standardTestDataPath} was not found. Using legacy ${legacyTestDataPath}`);
    return legacyTestDataPath;
  }

  throw new Error([
    'Test data JSON not found.',
    `  standard: ${standardTestDataPath}`,
    `  legacy:   ${legacyTestDataPath}`
  ].join('\n'));
}

const testDataPath = resolveTestDataPath(process.argv[2]);
const suiteBasePath = 'data/json/03_tests/responsibilities/responsibility_expected_first_set';
const actualOutputPath = `${suiteBasePath}/actual/responsibility_expected_first_set_actual_data_v0_1.json`;
const diffOutputPath = `${suiteBasePath}/diff/responsibility_expected_first_set_diff_data_v0_1.json`;


function readJson(relOrAbsPath) {
  return JSON.parse(fs.readFileSync(rootPath(relOrAbsPath), 'utf8'));
}

function loadResponsibilities() {
  const context = { console };
  vm.createContext(context);

  for (const rel of [
    'wwwroot/js/responsibilities/grid_column_builder.js',
    'wwwroot/js/responsibilities/search_filter.js',
    'wwwroot/js/responsibilities/csv_exporter.js'
  ]) {
    const code = fs.readFileSync(path.join(root, rel), 'utf8');
    vm.runInContext(code, context, { filename: rel });
  }

  return {
    GridColumnBuilder: context.GridColumnBuilder,
    SearchFilter: context.SearchFilter,
    CsvExporter: context.CsvExporter
  };
}

function fieldNames(fields = []) {
  return Array.from(fields, field => field?.field);
}

function runGridColumnBuild(pattern, api) {
  const actualFields = api.GridColumnBuilder.build(pattern.input?.view_def ?? {});
  return {
    field_names: fieldNames(actualFields),
    count: actualFields.length
  };
}

function runSearchFilter(pattern, api) {
  const result = api.SearchFilter.apply(
    pattern.input?.rows ?? [],
    pattern.input?.criteria ?? [],
    pattern.input?.options ?? {}
  );
  return {
    row_ids: Array.from(result, entry => entry?.row?.id),
    indexes: Array.from(result, entry => entry?.index),
    count: result.length
  };
}

function runCsvExport(pattern, api) {
  const input = pattern.input ?? {};
  const fields = input.resolve_fields
    ? api.CsvExporter.resolveFields({
        baseFields: input.base_fields ?? [],
        allFields: input.all_fields ?? [],
        keyFieldName: input.key_field_name ?? ''
      })
    : (input.fields ?? []);

  const csvText = api.CsvExporter.export({
    rows: input.rows ?? [],
    fields,
    includeBom: input.include_bom === true,
    valueForField: ({ row, field }) => row?.[field?.field]
  });

  const hasBom = csvText.startsWith('\ufeff');
  return {
    field_names: fieldNames(fields),
    has_bom: hasBom,
    csv_text: csvText,
    csv_without_bom: hasBom ? csvText.slice(1) : csvText
  };
}

function runPattern(pattern, api) {
  switch (pattern.responsibility_cd) {
    case 'grid_column_build':
      return runGridColumnBuild(pattern, api);
    case 'search_filter':
      return runSearchFilter(pattern, api);
    case 'csv_export':
      return runCsvExport(pattern, api);
    default:
      throw new Error(`Unsupported responsibility_cd: ${pattern.responsibility_cd}`);
  }
}


function ensureDirFor(relOrAbsPath) {
  fs.mkdirSync(path.dirname(rootPath(relOrAbsPath)), { recursive: true });
}

function writeJson(relOrAbsPath, value) {
  ensureDirFor(relOrAbsPath);
  fs.writeFileSync(rootPath(relOrAbsPath), `${JSON.stringify(value, null, 2)}
`, 'utf8');
}

function main() {
  const data = readJson(testDataPath);
  const api = loadResponsibilities();
  const patterns = (data.test_patterns ?? []).filter(pattern => pattern.enabled !== false);
  const generatedAt = toStudioDateTime();

  let passed = 0;
  const failures = [];
  const observations = [];
  const checks = [];

  for (const pattern of patterns) {
    try {
      const actual = runPattern(pattern, api);
      observations.push({
        test_pattern_id: pattern.test_pattern_id,
        responsibility_cd: pattern.responsibility_cd,
        title: pattern.title,
        actual,
        actual_display: toDisplayValue(actual),
        observed_at: generatedAt,
        source: 'tests/responsibilities/responsibility_expected_tests.mjs'
      });

      const patternChecks = buildExpectedChecks(pattern, actual);
      checks.push(...patternChecks);

      const failedPatternChecks = patternChecks.filter(check => check.pass !== true);
      if (failedPatternChecks.length) {
        failures.push({ pattern, failedChecks: failedPatternChecks });
        console.error(`FAIL ${pattern.test_pattern_id}`);
        for (const check of failedPatternChecks) {
          console.error(`  - ${check.check_id}: ${check.message}`);
        }
      } else {
        passed += 1;
        console.log(`PASS ${pattern.test_pattern_id}`);
      }
    } catch (err) {
      const errorActual = {
        error_name: err?.name ?? 'Error',
        error_message: err?.message ?? String(err)
      };
      observations.push({
        test_pattern_id: pattern.test_pattern_id,
        responsibility_cd: pattern.responsibility_cd,
        title: pattern.title,
        actual: errorActual,
        actual_display: toDisplayValue(errorActual),
        observed_at: generatedAt,
        source: 'tests/responsibilities/responsibility_expected_tests.mjs'
      });
      checks.push({
        check_id: `${pattern.test_pattern_id}.__runner_error`,
        name: 'runner_error',
        target: pattern.test_pattern_id,
        type: 'runnerError',
        responsibility_cd: pattern.responsibility_cd,
        test_pattern_id: pattern.test_pattern_id,
        expected: 'no error',
        actual: errorActual.error_message,
        expected_raw: 'no error',
        actual_raw: errorActual,
        pass: false,
        message: errorActual.error_message
      });
      failures.push({ pattern, error: err });
      console.error(`FAIL ${pattern.test_pattern_id}`);
      console.error(err?.stack || err);
    }
  }

  const failedChecks = checks.filter(check => check.pass !== true);
  const firstFailure = failedChecks[0] ?? null;
  const status = failedChecks.length ? 'fail' : 'pass';
  const resultLabel = failedChecks.length ? '🚨 FAIL' : '✅ PASS';

  const actualDoc = {
    view_def: 'qa/tests/responsibilities/responsibility_expected_actual_view_def_v0_1.json',
    schema_version: 'responsibility_expected_actual_v0_1',
    document_type: 'responsibility_expected_actual',
    test_area: data.test_area ?? 'responsibilities',
    suite_id: data.suite_id ?? 'responsibility_expected_first_set',
    artifact_kind: 'actual',
    test_id: data.suite_id ?? 'responsibility_expected_first_set',
    title: `${data.title ?? 'Responsibility Expected Tests'} Actual`,
    generated_at: generatedAt,
    source_test_patterns_file: testDataPath,
    runner: 'tests/responsibilities/responsibility_expected_tests.mjs',
    observations
  };

  const diffDoc = {
    view_def: 'qa/tests/responsibilities/responsibility_expected_diff_view_def_v0_1.json',
    schema_version: 'diff_result_v0_1',
    document_type: 'diff_result',
    domain: 'responsibilities',
    test_area: data.test_area ?? 'responsibilities',
    suite_id: data.suite_id ?? 'responsibility_expected_first_set',
    artifact_kind: 'diff',
    diff_kind: 'responsibility_expected',
    test_id: data.suite_id ?? 'responsibility_expected_first_set',
    title: `${data.title ?? 'Responsibility Expected Tests'} Diff`,
    generated_at: generatedAt,
    status,
    resultLabel,
    summary: failedChecks.length
      ? `🚨 ${failedChecks.length}件の差分を検出しました: ${failedChecks.map(check => check.check_id).join(', ')}`
      : `✅ ${checks.length}件すべてPASSしました`,
    total: checks.length,
    passCount: checks.length - failedChecks.length,
    failCount: failedChecks.length,
    failedCount: failedChecks.length,
    failedCheckIds: failedChecks.map(check => check.check_id),
    firstFailure,
    sourceFiles: {
      testPatternFile: testDataPath,
      actualFile: actualOutputPath,
      diffFile: diffOutputPath
    },
    checks
  };

  writeJson(actualOutputPath, actualDoc);
  writeJson(diffOutputPath, diffDoc);

  console.log(`\nresponsibility_expected_tests: ${passed}/${patterns.length} passed`);
  console.log(`actual: ${actualOutputPath}`);
  console.log(`diff:   ${diffOutputPath}`);

  if (failedChecks.length) {
    process.exitCode = 1;
  }
}
main();
