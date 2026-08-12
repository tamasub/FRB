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

function loadRuntime() {
  const sandbox = { console, Date, JSON, RegExp, Number, String, globalThis: null };
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

function plain(value) {
  return JSON.parse(JSON.stringify(value));
}

function runField(field) {
  const sandbox = loadRuntime();
  sandbox.__registry = readJson('data/json/config/validation_type_registry_v0_1.json');
  sandbox.__field = field;
  vm.runInContext(`globalThis.__result = new DefinitionTestRunnerCore().runField(__field, __registry);`, sandbox);
  return plain(sandbox.__result);
}

test('Runner executes exactly the TestPattern / Expected derived by DefinitionVerificationService', () => {
  const sandbox = loadRuntime();
  const registry = readJson('data/json/config/validation_type_registry_v0_1.json');
  const definitions = readJson('fielddefs/samples/frb_fft_measurement_field_definitions_v0_2.json');
  const field = definitions.field_definitions.find(item => item.field_path === '$.measurement_sessions[].sample_rate_hz');
  sandbox.__registry = registry;
  sandbox.__field = field;
  vm.runInContext(`
    globalThis.__service = new DefinitionVerificationService({ registry: __registry });
    globalThis.__preview = __service.deriveForPreview(__field);
    globalThis.__run = new DefinitionTestRunnerCore({ verificationService: __service }).runField(__field, __registry);
  `, sandbox);
  const preview = plain(sandbox.__preview);
  const run = plain(sandbox.__run);

  assert.equal(run.test_cases.length, preview.test_patterns.length);
  assert.deepEqual(
    run.test_cases.map(item => ({ pattern_id: item.pattern_id, input: item.input, expected: item.expected })),
    preview.test_patterns.map(item => ({ pattern_id: item.pattern_id, input: item.input, expected: item.expected }))
  );
  assert.equal(run.status, 'PASSED');
  assert.equal(run.summary.failed_count, 0);
  assert.ok(run.test_cases.every(item => item.comparison.status === 'PASS'));
});

test('representative numeric boundaries execute ACCEPT / REJECT as previewed', () => {
  const definitions = readJson('fielddefs/samples/frb_fft_measurement_field_definitions_v0_2.json');
  const field = definitions.field_definitions.find(item => item.field_path === '$.measurement_sessions[].sample_rate_hz');
  const run = runField(field);
  const cases = Object.fromEntries(run.test_cases.map(item => [item.pattern_key, item]));

  assert.equal(cases.minimum.input.value, 100);
  assert.equal(cases.minimum.expected.outcome, 'ACCEPT');
  assert.equal(cases.minimum.actual.outcome, 'ACCEPT');
  assert.equal(cases.minimum_minus_1.input.value, 99);
  assert.equal(cases.minimum_minus_1.actual.outcome, 'REJECT');
  assert.equal(cases.maximum.actual.outcome, 'ACCEPT');
  assert.equal(cases.maximum_plus_1.actual.outcome, 'REJECT');
  assert.equal(cases.invalid_format.actual.outcome, 'REJECT');
  assert.equal(cases.null.actual.outcome, 'REJECT');
  assert.equal(cases.required_missing.actual.outcome, 'REJECT');
});

test('representative string, boolean, date, datetime, and instant Validation Types execute without mismatch', () => {
  const definitions = readJson('fielddefs/samples/frb_fft_measurement_field_definitions_v0_2.json');
  const paths = [
    '$.measurement_sessions[].session_id',
    '$.measurement_sessions[].enabled',
    '$.measurement_sessions[].measurement_date',
    '$.measurement_sessions[].captured_at',
    '$.measurement_sessions[].received_at'
  ];
  for (const fieldPath of paths) {
    const field = definitions.field_definitions.find(item => item.field_path === fieldPath);
    const run = runField(field);
    assert.notEqual(run.status, 'FAILED', fieldPath);
    assert.notEqual(run.status, 'INVALID', fieldPath);
    assert.equal(run.summary.failed_count, 0, fieldPath);
  }
});

test('string length boundary generator keeps values valid for numeric-string Validation Type', () => {
  const run = runField({
    field_path: '$.numeric_code',
    validation_type: 'studio.string.numeric',
    constraint_overrides: {
      required: true,
      nullable: false,
      empty_string_allowed: false,
      minimum_length: 3,
      maximum_length: 5
    }
  });
  const cases = Object.fromEntries(run.test_cases.map(item => [item.pattern_key, item]));

  assert.match(cases.minimum_length.input.value, /^[0-9]+$/);
  assert.match(cases.maximum_length.input.value, /^[0-9]+$/);
  assert.equal(cases.minimum_length.actual.outcome, 'ACCEPT');
  assert.equal(cases.minimum_length_minus_1.actual.outcome, 'REJECT');
  assert.equal(cases.maximum_length.actual.outcome, 'ACCEPT');
  assert.equal(cases.maximum_length_plus_1.actual.outcome, 'REJECT');
  assert.equal(run.summary.failed_count, 0);
});

test('all FRB FFT Field Definitions run without saved TestPattern JSON and retain source trace metadata', () => {
  const sandbox = loadRuntime();
  const registry = readJson('data/json/config/validation_type_registry_v0_1.json');
  const definitions = readJson('fielddefs/samples/frb_fft_measurement_field_definitions_v0_2.json');
  sandbox.__registry = registry;
  sandbox.__definitions = definitions;
  sandbox.__meta = {
    field_definition_path: 'fielddefs/samples/frb_fft_measurement_field_definitions_v0_2.json',
    field_definition_sha256: 'field-hash',
    registry_path: 'data/json/config/validation_type_registry_v0_1.json',
    registry_sha256: 'registry-hash'
  };
  vm.runInContext(`globalThis.__result = new DefinitionTestRunnerCore().runDocument(__definitions, __registry, { source_metadata: __meta });`, sandbox);
  const result = plain(sandbox.__result);

  assert.equal(result.schema_version, 'definition_test_runner_result_v0_2');
  assert.equal(result.runner.id, 'studio.definition_test_runner.core');
  assert.equal(result.runner.version, '0.3.0');
  assert.equal(result.summary.field_count, definitions.field_definition_count);
  assert.equal(result.summary.failed_count, 0);
  assert.equal(result.summary.invalid_field_count, 0);
  assert.ok(result.summary.pattern_count >= definitions.field_definition_count * 4);
  assert.equal(result.source.validation_type_registry.registry_version, registry.registry_version);
  assert.equal(result.source.field_definition_document.definition_id, definitions.definition_id);
  assert.equal(result.source.field_definition_document.sha256, 'field-hash');
  assert.equal(result.source.validation_type_registry.sha256, 'registry-hash');
  assert.ok(result.fields.every(field => field.source.registry_version === registry.registry_version));
});

test('Runner records Expected / Actual mismatch as FAIL instead of changing Expected', () => {
  const sandbox = loadRuntime();
  sandbox.__registry = readJson('data/json/config/validation_type_registry_v0_1.json');
  sandbox.__field = {
    field_path: '$.enabled',
    validation_type: 'studio.boolean.standard',
    constraint_overrides: { required: true, nullable: false }
  };
  vm.runInContext(`
    globalThis.__fakeValidator = { validate(){ return { outcome: 'ACCEPT', reason_code: 'FAKE_ACCEPT', violations: [] }; } };
    globalThis.__run = new DefinitionTestRunnerCore({ valueValidator: __fakeValidator }).runField(__field, __registry);
  `, sandbox);
  const run = plain(sandbox.__run);
  const missing = run.test_cases.find(item => item.pattern_key === 'required_missing');

  assert.equal(missing.expected.outcome, 'REJECT');
  assert.equal(missing.actual.outcome, 'ACCEPT');
  assert.equal(missing.comparison.status, 'FAIL');
  assert.equal(run.status, 'FAILED');
  assert.ok(run.summary.failed_count >= 1);
});

test('Definition Test Runner stays UI-independent and TestRunner.ps1 exposes a whitelisted minimal entry', () => {
  for (const relativePath of [
    'wwwroot/js/services/definition/definition_value_validator.js',
    'wwwroot/js/services/definition/cross_field_verification_service.js',
    'wwwroot/js/services/definition/cross_field_relation_evaluator.js',
    'wwwroot/js/services/definition/definition_test_runner_core.js',
    'wwwroot/js/services/definition/definition_test_evidence_builder.js'
  ]) {
    const source = readText(relativePath);
    assert.doesNotMatch(source, /\bdocument\b|querySelector|EditorComponent|SubGridComponent/);
  }
  const ps1 = readText('tools/test/TestRunner.ps1');
  assert.match(ps1, /definition_test_runner/);
  assert.match(ps1, /definition_test_runner_cli\.mjs/);
  assert.match(ps1, /definition_test_runner_cross_field_operator_matrix/);
  assert.match(ps1, /fielddefs\/samples\/cross_field_compare_operator_matrix_v0_1\.json/);
  assert.match(ps1, /data\/json\/03_tests\/contracts\/definition_test_runner_cross_field_operator_matrix_v0_1/);

  const runConfig = readJson('data/json/04_tools/test_runner_run_config_data_v0_1.json');
  const frbConfig = runConfig.run_configs.find(item => item.test_runner_id === 'definition_test_runner');
  const matrixConfig = runConfig.run_configs.find(item => item.test_runner_id === 'definition_test_runner_cross_field_operator_matrix');
  assert.ok(frbConfig);
  assert.ok(matrixConfig);
  assert.equal(matrixConfig.run_mode, 'wait');
  assert.equal(
    matrixConfig.output_artifact_path,
    'data/json/03_tests/contracts/definition_test_runner_cross_field_operator_matrix_v0_1/diff/definition_test_runner.diff.json'
  );

  const program = readText('Program.cs/Program.cs');
  assert.match(program, /"definition_test_runner"/);
  assert.match(program, /"definition_test_runner_cross_field_operator_matrix"/);
  assert.match(program, /definition_test_runner_cross_field_operator_matrix_v0_1\/diff\/definition_test_runner\.diff\.json/);
});
