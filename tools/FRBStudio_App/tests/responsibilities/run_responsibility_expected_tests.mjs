// v0.18.9.1-test-area-folder-layout-runner-path-guard
// JSON-driven minimal Expected tests for ResponsibilityDef interfaces.
// Run from FRBStudio_App root:
//   node tests/responsibilities/run_responsibility_expected_tests.mjs
// Optional: pass a test data JSON path explicitly as argv[2].

import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import assert from 'node:assert/strict';

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
  const result = api.SearchFilter.apply(pattern.input?.rows ?? [], pattern.input?.criteria ?? []);
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

function assertExpected(pattern, actual) {
  const expected = pattern.expected ?? {};
  for (const [key, expectedValue] of Object.entries(expected)) {
    assert.deepEqual(
      actual[key],
      expectedValue,
      `${pattern.test_pattern_id}: expected ${key}`
    );
  }
}

function main() {
  const data = readJson(testDataPath);
  const api = loadResponsibilities();
  const patterns = (data.test_patterns ?? []).filter(pattern => pattern.enabled !== false);

  let passed = 0;
  const failures = [];

  for (const pattern of patterns) {
    try {
      const actual = runPattern(pattern, api);
      assertExpected(pattern, actual);
      passed += 1;
      console.log(`PASS ${pattern.test_pattern_id}`);
    } catch (err) {
      failures.push({ pattern, error: err });
      console.error(`FAIL ${pattern.test_pattern_id}`);
      console.error(err?.stack || err);
    }
  }

  console.log(`\nresponsibility_expected_tests: ${passed}/${patterns.length} passed`);

  if (failures.length) {
    process.exitCode = 1;
  }
}

main();
