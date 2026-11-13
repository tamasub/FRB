import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';

const ROOT = process.cwd();
const readText = rel => fs.readFileSync(path.join(ROOT, rel), 'utf8');
const readJson = rel => JSON.parse(readText(rel));

function loadServiceSandbox() {
  const sandbox = { console, structuredClone, Date, JSON, Object, Array, Map, Set, Number, String, Boolean, Math, RegExp };
  sandbox.globalThis = sandbox;
  vm.createContext(sandbox);
  [
    'wwwroot/js/services/definition/definition_verification_common.js',
    'wwwroot/js/services/definition/field_contract_resolver.js',
    'wwwroot/js/services/definition/definition_value_validator.js',
    'wwwroot/js/services/responsibility/responsibility_test_preview_service.js'
  ].forEach(rel => vm.runInContext(readText(rel), sandbox, { filename: rel }));
  return sandbox;
}

function deriveSearchPreview() {
  const sandbox = loadServiceSandbox();
  const responsibilityDocument = readJson('data/json/03_tests/responsibilities/responsibility_data_v0_2.json');
  const responsibility = responsibilityDocument.responsibilities.find(item => item.responsibility_cd === 'search_filter');
  const inputData = readJson('data/json/80_frb/frb_fft_search_test_data_v0_1.json');
  const viewDef = readJson('defs/frb/frb_fft_field_definition_sample_view_def_v0_1.json');
  const fieldDefinitionDocument = readJson('fielddefs/samples/frb_fft_measurement_field_definitions_v0_2.json');
  const registry = readJson('data/json/config/validation_type_registry_v0_1.json');
  const searchOperatorRegistry = readJson('data/json/config/search_operator_registry_v0_1.json');

  const service = new sandbox.ResponsibilityTestPreviewService({ registry });
  return JSON.parse(JSON.stringify(service.derive({
    responsibility,
    rootDocument: responsibilityDocument,
    inputData,
    viewDef,
    fieldDefinitionDocument,
    registry,
    searchOperatorRegistry
  })));
}

test('SEARCH_FILTER uses dedicated JSON fixture and two generator definitions, not hand-written operator patterns', () => {
  const document = readJson('data/json/03_tests/responsibilities/responsibility_data_v0_2.json');
  const responsibility = document.responsibilities.find(item => item.responsibility_cd === 'search_filter');
  const setup = responsibility.test_setup[0];

  assert.equal(setup.input_file, 'data/json/80_frb/frb_fft_search_test_data_v0_1.json');
  assert.equal(setup.input_approval_status, 'approved');
  assert.equal(setup.pattern_isolation_policy, 'RESET_AFTER_EACH');
  assert.equal(setup.search_operator_registry_file, 'data/json/config/search_operator_registry_v0_1.json');
  assert.equal(responsibility.test_pattern_definitions.length, 2);
  assert.ok(responsibility.test_pattern_definitions.every(item => item.generation_mode === 'SEARCH_OPERATOR_MATRIX'));
  assert.deepEqual(responsibility.test_pattern_definitions.map(item => item.target_field), ['note', 'amplitude_g']);
});

test('SEARCH_FILTER preview expands String 6 + Number 7 operators into 13 TestPatterns / 13 Generated Cases', () => {
  const result = deriveSearchPreview();
  assert.equal(result.status, 'READY');
  assert.equal(result.execution_ready, true, 'approved Input is execution ready');
  assert.equal(result.summary.test_pattern_count, 13);
  assert.equal(result.summary.generated_case_count, 13);
  assert.equal(result.summary.issue_count, 0);
  assert.ok(result.test_patterns.every(pattern => pattern.generated_cases.length === 1));

  const stringPatterns = result.test_patterns.filter(pattern => pattern.value_family === 'string');
  const numberPatterns = result.test_patterns.filter(pattern => pattern.value_family === 'number');
  assert.deepEqual(stringPatterns.map(pattern => pattern.operator_id), ['contains','not_contains','equals','not_equals','blank','not_blank']);
  assert.deepEqual(numberPatterns.map(pattern => pattern.operator_id), ['between','equals','not_equals','gte','lte','blank','not_blank']);
});

test('SEARCH_FILTER Generated Cases expose Input Snapshot / Criteria / Expected with deterministic representative results', () => {
  const result = deriveSearchPreview();
  const byId = new Map(result.test_patterns.map(pattern => [pattern.pattern_id, pattern.generated_cases[0]]));

  const contains = byId.get('search_filter_string_contains');
  assert.equal(contains.target_field, 'note');
  assert.equal(contains.input_snapshot.length, 6);
  assert.deepEqual(contains.criteria, { operator: 'contains', value: 'Alpha' });
  assert.deepEqual(contains.expected.indexes, [0,2,5]);

  const equalsText = byId.get('search_filter_string_equals');
  assert.deepEqual(equalsText.expected.indexes, [0,2]);
  const blankText = byId.get('search_filter_string_blank');
  assert.deepEqual(blankText.expected.indexes, [3]);
  const notBlankText = byId.get('search_filter_string_not_blank');
  assert.deepEqual(notBlankText.expected.indexes, [0,1,2,4,5]);

  const between = byId.get('search_filter_number_between');
  assert.deepEqual(between.criteria, { operator: 'between', from: 0.5, to: 0.9 });
  assert.deepEqual(between.expected.indexes, [1,2,3]);
  const equalsNumber = byId.get('search_filter_number_equals');
  assert.deepEqual(equalsNumber.criteria, { operator: 'equals', value: 0.5 });
  assert.deepEqual(equalsNumber.expected.indexes, [1,2]);
  const gte = byId.get('search_filter_number_gte');
  assert.deepEqual(gte.expected.indexes, [1,2,3,4]);
  const lte = byId.get('search_filter_number_lte');
  assert.deepEqual(lte.expected.indexes, [0,1,2,5]);
});

test('Search Fixture data remains pure input and Generated artifacts are not persisted in Responsibility JSON', () => {
  const fixture = readJson('data/json/80_frb/frb_fft_search_test_data_v0_1.json');
  const document = readJson('data/json/03_tests/responsibilities/responsibility_data_v0_2.json');
  const responsibility = document.responsibilities.find(item => item.responsibility_cd === 'search_filter');

  assert.equal(fixture.measurement_sessions.length, 6);
  assert.equal(Object.hasOwn(fixture, 'expected'), false);
  assert.equal(Object.hasOwn(fixture, 'test_patterns'), false);
  assert.equal(Object.hasOwn(responsibility, 'generated_test_patterns'), false);
  assert.equal(Object.hasOwn(responsibility, 'generated_expected'), false);
});

test('Responsibility ViewDef includes search generation fields without adding a third ViewDef hierarchy', () => {
  const viewDef = readJson('defs/qa/tests/responsibilities/responsibility_view_def_v0_2.json');
  const section = viewDef.views.flatMap(view => view.sections ?? []).find(item => item.id === 'responsibilities');
  const setup = section.fields.find(item => item.field === 'test_setup').edit.subGrid;
  const defs = section.fields.find(item => item.field === 'test_pattern_definitions').edit.subGrid;
  const component = section.editorComponents.find(item => item.id === 'responsibility_generated_test_preview');

  assert.ok(setup.columns.some(item => item.field === 'search_operator_registry_file'));
  assert.ok(setup.columns.some(item => item.field === 'pattern_isolation_policy'));
  assert.ok(defs.columns.some(item => item.field === 'generation_mode'));
  assert.ok(defs.columns.some(item => item.field === 'target_field'));
  assert.ok(defs.columns.some(item => item.field === 'operator_source'));
  assert.equal(component.config.initialExpanded, false);
  assert.equal(component.config.searchOperatorRegistryDataPath, 'config/search_operator_registry_v0_1.json');
});
