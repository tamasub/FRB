import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import test from 'node:test';
import vm from 'node:vm';

const root = process.cwd();

function readText(relativePath) {
  return fs.readFileSync(path.join(root, relativePath), 'utf8');
}
function readJson(relativePath) {
  return JSON.parse(readText(relativePath));
}
function plain(value) {
  return JSON.parse(JSON.stringify(value));
}
function loadRuntime() {
  const sandbox = { console, Date, JSON, RegExp, Number, String, Boolean, Set, Map, Object, globalThis: null };
  sandbox.globalThis = sandbox;
  vm.createContext(sandbox);
  [
    'wwwroot/js/services/search_capability_resolver.js',
    'wwwroot/js/responsibilities/search_filter.js',
    'wwwroot/js/services/search_test_pattern_deriver.js',
    'wwwroot/js/services/search_definition_test_runner.js',
    'wwwroot/js/services/search_definition_test_evidence_builder.js'
  ].forEach(relativePath => vm.runInContext(readText(relativePath), sandbox, { filename: relativePath }));
  return sandbox;
}

function run() {
  const sandbox = loadRuntime();
  sandbox.__definitions = readJson('data/json/03_tests/contracts/definition_driven_search_v0_1/input/search_field_definitions.json');
  sandbox.__searchRegistry = readJson('data/json/config/search_operator_registry_v0_1.json');
  sandbox.__validationRegistry = readJson('data/json/config/validation_type_registry_v0_1.json');
  vm.runInContext(`
    globalThis.__result = new SearchDefinitionTestRunner({
      clock: () => '2026-08-16T16:30:00+09:00'
    }).runDocument(
      __definitions,
      {
        search_operator_registry: __searchRegistry,
        validation_type_registry: __validationRegistry
      },
      { definition_path: 'data/json/03_tests/contracts/definition_driven_search_v0_1/input/search_field_definitions.json' }
    );
  `, sandbox);
  return { sandbox, result: plain(sandbox.__result) };
}

test('SearchCapability derives Text / Number / Date patterns and all representative cases pass', () => {
  const { result } = run();
  assert.equal(result.status, 'PASSED');
  assert.equal(result.summary.field_count, 3);
  assert.equal(result.summary.failed_count, 0);
  assert.equal(result.summary.unresolved_count, 0);
  assert.ok(result.summary.pattern_count >= 35);

  const byField = Object.fromEntries(result.fields.map(field => [field.field, field]));
  assert.equal(byField.title.search_capability_snapshot.effective.operator_set_id, 'text_standard');
  assert.equal(byField.amount.search_capability_snapshot.effective.operator_set_id, 'numeric_standard');
  assert.equal(byField.updated_at.search_capability_snapshot.effective.operator_set_id, 'date_standard');
});

test('Text patterns include exclusion, blank, and case-insensitive contains', () => {
  const { result } = run();
  const field = result.fields.find(item => item.field === 'title');
  const cases = Object.fromEntries(field.test_cases.map(item => [item.pattern_key, item]));
  for (const key of ['contains_hit', 'contains_miss', 'not_contains_hit', 'not_contains_excluded', 'blank', 'not_blank', 'case_insensitive_contains']) {
    assert.ok(cases[key], key);
    assert.equal(cases[key].comparison.status, 'PASS', key);
  }
  assert.equal(cases.contains_miss.expected.outcome, 'NO_MATCH');
  assert.equal(cases.not_contains_excluded.actual.outcome, 'NO_MATCH');
});

test('Number patterns preserve inclusive boundaries, partial ranges, zero not-blank, and outside rejection', () => {
  const { result } = run();
  const field = result.fields.find(item => item.field === 'amount');
  const cases = Object.fromEntries(field.test_cases.map(item => [item.pattern_key, item]));
  for (const key of ['gte_boundary', 'gte_below', 'lte_boundary', 'lte_above', 'between_inside', 'between_min', 'between_max', 'between_outside', 'from_only', 'to_only', 'blank', 'not_blank_zero']) {
    assert.ok(cases[key], key);
    assert.equal(cases[key].comparison.status, 'PASS', key);
  }
  assert.equal(cases.between_min.actual.outcome, 'MATCH');
  assert.equal(cases.between_max.actual.outcome, 'MATCH');
  assert.equal(cases.between_outside.actual.outcome, 'NO_MATCH');
  assert.equal(cases.not_blank_zero.actual.outcome, 'MATCH');
});

test('Date patterns preserve inclusive range semantics and invalid dates do not match', () => {
  const { result } = run();
  const field = result.fields.find(item => item.field === 'updated_at');
  const cases = Object.fromEntries(field.test_cases.map(item => [item.pattern_key, item]));
  for (const key of ['between_inside', 'between_min', 'between_max', 'between_outside', 'from_only', 'to_only', 'invalid_date_input']) {
    assert.ok(cases[key], key);
    assert.equal(cases[key].comparison.status, 'PASS', key);
  }
  assert.equal(cases.between_min.actual.outcome, 'MATCH');
  assert.equal(cases.between_max.actual.outcome, 'MATCH');
  assert.equal(cases.invalid_date_input.actual.outcome, 'NO_MATCH');
});

test('Evidence builder creates explainable Expected / Actual / Diff with capability snapshots', () => {
  const { sandbox, result } = run();
  sandbox.__runnerResult = result;
  vm.runInContext(`
    globalThis.__evidence = new SearchDefinitionTestEvidenceBuilder().buildArtifacts(__runnerResult, {
      test_id: 'definition_driven_search_v0_1',
      title: 'Definition Driven Search — Text / Number / Date'
    });
  `, sandbox);
  const evidence = plain(sandbox.__evidence);

  assert.equal(evidence.diff.status, 'pass');
  assert.equal(evidence.diff.failCount, 0);
  assert.equal(evidence.diff.total, result.summary.pattern_count);
  assert.equal(evidence.expected.checks.length, result.summary.pattern_count);
  assert.equal(evidence.actual.checks.length, result.summary.pattern_count);
  assert.equal(evidence.diff.search_definition_snapshots.length, 3);
  assert.ok(evidence.diff.checks.every(item => item.pass === true));
});

test('Definition Driven Search services remain DOM-independent', () => {
  for (const relativePath of [
    'wwwroot/js/services/search_test_pattern_deriver.js',
    'wwwroot/js/services/search_definition_test_runner.js',
    'wwwroot/js/services/search_definition_test_evidence_builder.js'
  ]) {
    const source = readText(relativePath);
    assert.doesNotMatch(source, /\bdocument\b|querySelector|addEventListener|createElement/);
  }
});
