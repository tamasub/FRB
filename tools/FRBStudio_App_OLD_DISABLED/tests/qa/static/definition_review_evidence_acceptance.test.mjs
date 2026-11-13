import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import test from 'node:test';
import vm from 'node:vm';

const root = process.cwd();
const readText = relativePath => fs.readFileSync(path.join(root, relativePath), 'utf8');
const readJson = relativePath => JSON.parse(readText(relativePath));
const plain = value => JSON.parse(JSON.stringify(value));

function loadDefinitionRuntime() {
  const sandbox = { console, Date, JSON, RegExp, Number, String, Set, globalThis: null };
  sandbox.globalThis = sandbox;
  vm.createContext(sandbox);
  [
    'wwwroot/js/services/definition/definition_verification_common.js',
    'wwwroot/js/services/definition/field_contract_resolver.js',
    'wwwroot/js/services/definition/test_pattern_deriver.js',
    'wwwroot/js/services/definition/expected_resolver.js',
    'wwwroot/js/services/definition/definition_verification_service.js',
    'wwwroot/js/services/definition/definition_value_validator.js',
    'wwwroot/js/services/definition/cross_field_verification_service.js',
    'wwwroot/js/services/definition/cross_field_relation_evaluator.js',
    'wwwroot/js/services/definition/definition_test_runner_core.js',
    'wwwroot/js/services/definition/definition_test_evidence_builder.js'
  ].forEach(relativePath => vm.runInContext(readText(relativePath), sandbox, { filename: relativePath }));
  return sandbox;
}

function buildEvidence() {
  const sandbox = loadDefinitionRuntime();
  sandbox.__fieldDefs = readJson('fielddefs/samples/frb_fft_measurement_field_definitions_v0_2.json');
  sandbox.__registry = readJson('data/json/config/validation_type_registry_v0_1.json');
  sandbox.__metadata = {
    field_definition_path: 'fielddefs/samples/frb_fft_measurement_field_definitions_v0_2.json',
    field_definition_sha256: 'field-definition-hash',
    registry_path: 'data/json/config/validation_type_registry_v0_1.json',
    registry_sha256: 'registry-hash'
  };
  vm.runInContext(`
    globalThis.__runner = new DefinitionTestRunnerCore().runDocument(__fieldDefs, __registry, { source_metadata: __metadata });
    globalThis.__evidence = new DefinitionTestEvidenceBuilder().buildArtifacts(__runner);
  `, sandbox);
  return plain(sandbox.__evidence);
}

test('Diff evidence freezes Field Definition + verification snapshots and exposes the dedicated review ViewDef', () => {
  const evidence = buildEvidence();
  const diff = evidence.diff;

  assert.equal(diff.view_def, 'fielddefs/definition_test_diff_view_def_v0_1.json');
  assert.equal(diff.definition_review_snapshots.schema_version, 'definition_review_snapshot_v0_1');
  assert.equal(diff.definition_review_snapshots.fields.length, 20);

  const measurementDate = diff.definition_review_snapshots.fields.find(
    item => item.field_path === '$.measurement_sessions[].measurement_date'
  );
  assert.ok(measurementDate);
  assert.equal(measurementDate.field_definition.validation_type, 'studio.date.ymd');
  assert.equal(measurementDate.field_definition.constraint_overrides.minimum_date.value, '2020-01-01');
  assert.ok(Array.isArray(measurementDate.verification_result.field_contract.constraint_resolutions));
  assert.ok(Array.isArray(measurementDate.verification_result.test_patterns));
});

test('Diff check preserves the actual executed Input and the constraint source used for explanation', () => {
  const evidence = buildEvidence();
  const check = evidence.diff.checks.find(
    item => item.check_id === 'field::$.measurement_sessions[].measurement_date::minimum_date_minus_1_day'
  );

  assert.ok(check);
  assert.equal(check.input.value, '2019-12-31');
  assert.equal(check.expected, 'REJECT');
  assert.equal(check.actual, 'REJECT');
  assert.equal(check.result, 'PASS');
  assert.equal(check.constraint_ref, 'minimum_date');
  assert.equal(check.expected_reason_code, 'OUTSIDE_BOUNDARY_REJECTED');
  assert.equal(check.actual_reason_code, 'MINIMUM_BOUNDARY_VIOLATION');
  assert.equal(check.message, '差分なし');
});

test('Definition Test Diff ViewDef declares the linked review Component and shows execution evidence fields', () => {
  const viewDef = readJson('defs/fielddefs/definition_test_diff_view_def_v0_1.json');
  const grid = viewDef.views[0].sections.find(section => section.id === 'checks');
  const fields = Object.fromEntries(grid.fields.map(field => [field.field, field]));
  const component = grid.editorComponents.find(item => item.type === 'definition_evidence_review');

  assert.ok(component);
  assert.equal(component.placement, 'detailBody');
  assert.equal(component.config.targetViewDefPath, 'frb/frb_fft_field_definition_sample_view_def_v0_1.json');
  for (const name of ['result', 'name', 'target', 'input', 'expected', 'actual', 'expected_reason_code', 'actual_reason_code']) {
    assert.ok(fields[name], name);
    assert.equal(fields[name].edit.readonly, true, name);
  }
});

test('Linked Definition review reuses the same approved Components instead of reimplementing Constraint/TestPattern projection', () => {
  const source = readText('wwwroot/js/components/definition/definition_evidence_review_component.js');
  assert.match(source, /type:\s*'definition_target_caption'/);
  assert.match(source, /type:\s*'definition_constraint_diff'/);
  assert.match(source, /type:\s*'definition_test_preview'/);
  assert.match(source, /verificationResult:\s*snapshot\.verification_result/);
  assert.doesNotMatch(source, /new\s+FieldContractResolver\s*\(/);
  assert.doesNotMatch(source, /new\s+TestPatternDeriver\s*\(/);
  assert.doesNotMatch(source, /new\s+ExpectedResolver\s*\(/);
});

test('Generated TestPattern Component highlights the Diff pattern and substitutes execution evidence for the selected row', () => {
  const source = readText('wwwroot/js/components/definition/definition_test_preview_component.js');
  assert.match(source, /evidenceCheck/);
  assert.match(source, /is_evidence_target/);
  assert.match(source, /evidence\.input/);
  assert.match(source, /evidence\.expected/);
  assert.match(source, /evidence\.actual/);
  assert.match(source, /is-evidence-target/);
});

test('F12 performs full Detail rebind from canonical Data and Raw Constraint Overrides is removed from normal Field Definition UI', () => {
  const detailSave = readText('wwwroot/js/runtime/detail_save.js');
  assert.match(detailSave, /rebindDetailAfterCanonicalCommit\(currentRows\[selectedIndex\]/);
  assert.match(detailSave, /renderDetailForRow\(row\)/);

  const viewDef = readJson('defs/fielddefs/frb_fft_measurement_field_definitions_view_def_v0_1.json');
  const grid = viewDef.views[0].sections.find(section => section.id === 'field_definitions');
  const raw = grid.fields.find(field => field.field === 'constraint_overrides');
  assert.equal(raw.grid.visible, false);
  assert.equal(raw.edit.visible, false);
});
