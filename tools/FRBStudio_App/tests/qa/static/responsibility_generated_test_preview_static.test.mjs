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

test('DATA_UPDATE_PERSIST preview derives 6 patterns and JsonDiff Expected from Responsibility definition', () => {
  const sandbox = loadServiceSandbox();
  const responsibilityDocument = readJson('data/json/03_tests/responsibilities/responsibility_data_v0_2.json');
  const responsibility = responsibilityDocument.responsibilities.find(item => item.responsibility_cd === 'data_update_persist');
  const inputData = readJson('data/json/80_frb/frb_fft_field_definition_sample_data_v0_1.json');
  const viewDef = readJson('defs/frb/frb_fft_field_definition_sample_view_def_v0_1.json');
  const fieldDefinitionDocument = readJson('fielddefs/samples/frb_fft_measurement_field_definitions_v0_2.json');
  const registry = readJson('data/json/config/validation_type_registry_v0_1.json');

  const service = new sandbox.ResponsibilityTestPreviewService({ registry });
  const result = service.derive({ responsibility, rootDocument: responsibilityDocument, inputData, viewDef, fieldDefinitionDocument, registry });
  const plain = JSON.parse(JSON.stringify(result));

  assert.equal(plain.status, 'READY');
  assert.equal(plain.execution_ready, false, 'draft Input is previewable but not execution ready');
  assert.equal(plain.input_approval_status, 'draft');
  assert.equal(plain.expected_def_type, 'JsonDiffExpectedDef');
  assert.equal(plain.summary.test_pattern_count, 6);
  assert.equal(plain.summary.mutation_count, 30);
  assert.equal(plain.summary.invalid_mutation_count, 0);
  assert.equal(plain.summary.issue_count, 0);

  assert.deepEqual(plain.test_patterns.map(p => p.mutations.length), [10, 10, 4, 4, 1, 1]);
  assert.deepEqual(
    plain.test_patterns.map(p => p.expected.unexpected_diff_count),
    [0, 0, 0, 0, 0, 0]
  );
  assert.ok(plain.test_patterns.every(p => p.expected.diff.includes('(-) ') && p.expected.diff.includes('(+) ')));
  assert.ok(plain.test_patterns.flatMap(p => p.mutations).every(m => m.validation_outcome === 'ACCEPT'));

  const firstSingle = plain.test_patterns[0];
  assert.equal(firstSingle.target_data_path, '$.measurement_sessions');
  assert.equal(firstSingle.row_index, 0);
  assert.equal(firstSingle.mutations.some(m => m.field === 'session_id'), false, 'key field is excluded');
  assert.equal(firstSingle.mutations.some(m => m.field === 'note'), false, 'multiline is excluded from standard pattern');
  assert.equal(firstSingle.mutations.some(m => m.field === 'rod_code'), true);
  assert.match(firstSingle.mutations.find(m => m.field === 'rod_code').after, /TEST$/);

  const firstMultiline = plain.test_patterns[4];
  assert.equal(firstMultiline.mutations.length, 1);
  assert.equal(firstMultiline.mutations[0].field, 'note');
  assert.match(firstMultiline.mutations[0].after, /\nTEST$/);
});

test('Responsibility ViewDef mounts Generated TestPattern / Expected Preview as initial CLOSED derived component', () => {
  const viewDef = readJson('defs/qa/tests/responsibilities/responsibility_view_def_v0_2.json');
  const section = viewDef.views.flatMap(view => view.sections ?? []).find(item => item.id === 'responsibilities');
  const component = (section.editorComponents ?? []).find(item => item.id === 'responsibility_generated_test_preview');

  assert.ok(component);
  assert.equal(component.type, 'responsibility_test_preview');
  assert.equal(component.readonly, true);
  assert.equal(component.config.initialExpanded, false);
  assert.equal(component.caption, 'Generated TestPattern / Expected Preview');
});

test('Generated Responsibility preview stays outside canonical Responsibility JSON', () => {
  const document = readJson('data/json/03_tests/responsibilities/responsibility_data_v0_2.json');
  const responsibility = document.responsibilities.find(item => item.responsibility_cd === 'data_update_persist');

  assert.equal(Object.hasOwn(responsibility, 'generated_test_patterns'), false);
  assert.equal(Object.hasOwn(responsibility, 'generated_expected'), false);
  assert.equal(Object.hasOwn(responsibility, 'expected'), false);
  assert.ok(Array.isArray(responsibility.test_pattern_definitions));
  assert.ok(Array.isArray(responsibility.test_setup));
});

test('index loads Responsibility preview Service/Component before generic Detail runtime', () => {
  const index = readText('wwwroot/index.html');
  const service = index.indexOf('js/services/responsibility/responsibility_test_preview_service.js');
  const component = index.indexOf('js/components/responsibility/responsibility_test_preview_component.js');
  const host = index.indexOf('js/components/editor_component_host.js');
  const detail = index.indexOf('js/runtime/detail_save.js');

  assert.ok(service >= 0);
  assert.ok(component > service);
  assert.ok(host > component);
  assert.ok(detail > host);
});
