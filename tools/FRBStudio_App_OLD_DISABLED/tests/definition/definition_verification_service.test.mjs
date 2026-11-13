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
  const sandbox = { console, Date, JSON, globalThis: null };
  sandbox.globalThis = sandbox;
  vm.createContext(sandbox);
  [
    'wwwroot/js/services/definition/definition_verification_common.js',
    'wwwroot/js/services/definition/field_contract_resolver.js',
    'wwwroot/js/services/definition/test_pattern_deriver.js',
    'wwwroot/js/services/definition/expected_resolver.js',
    'wwwroot/js/services/definition/definition_verification_service.js'
  ].forEach(relativePath => vm.runInContext(readText(relativePath), sandbox, { filename: relativePath }));
  return sandbox;
}

function plain(value) {
  return JSON.parse(JSON.stringify(value));
}

test('FieldContractResolver distinguishes registry default, override, and unresolved constraints', () => {
  const sandbox = loadRuntime();
  const registry = readJson('data/json/config/validation_type_registry_v0_1.json');
  sandbox.__registry = registry;
  sandbox.__field = {
    field_path: '$.value',
    validation_type: 'studio.integer.positive',
    constraint_overrides: {
      required: true,
      nullable: false,
      minimum: { value: 100, inclusive: true }
    }
  };

  vm.runInContext(`
    globalThis.__contract = new FieldContractResolver(__registry).resolve(__field);
  `, sandbox);
  const contract = plain(sandbox.__contract);
  const byKey = Object.fromEntries(contract.constraint_resolutions.map(item => [item.constraint, item]));

  assert.equal(contract.resolution_status, 'RESOLVED');
  assert.equal(byKey.required.source, 'override');
  assert.equal(byKey.required.resolved_value, true);
  assert.equal(byKey.minimum.default_value.value, 1);
  assert.equal(byKey.minimum.override_value.value, 100);
  assert.equal(byKey.minimum.resolved_value.value, 100);
  assert.equal(byKey.maximum.source, 'registry_default');
  assert.equal(byKey.maximum.resolved_value.value, Number.MAX_SAFE_INTEGER);
  assert.deepEqual(contract.unresolved_constraints, []);
  assert.equal(contract.source.registry_version, '0.1.0');
  assert.equal(contract.source.validation_type_contract_version, '0.1.0');
});

test('missing registry default + missing override is explicitly UNRESOLVED and never treated as PASS', () => {
  const sandbox = loadRuntime();
  const registry = readJson('data/json/config/validation_type_registry_v0_1.json');
  sandbox.__registry = registry;
  sandbox.__field = {
    field_path: '$.value',
    validation_type: 'studio.number.standard',
    constraint_overrides: { required: true }
  };

  vm.runInContext(`
    globalThis.__service = new DefinitionVerificationService({ registry: __registry });
    globalThis.__result = __service.derive(__field);
  `, sandbox);
  const result = plain(sandbox.__result);
  const nullable = result.field_contract.constraint_resolutions.find(item => item.constraint === 'nullable');
  const nullPattern = result.test_patterns.find(item => item.pattern_key === 'null');

  assert.equal(result.status, 'PARTIAL');
  assert.equal(nullable.status, 'UNRESOLVED');
  assert.ok(result.field_contract.unresolved_constraints.includes('nullable'));
  assert.equal(nullPattern.expected.outcome, 'UNRESOLVED');
  assert.equal(nullPattern.expected.reason_code, 'CONSTRAINT_UNRESOLVED:nullable');
  assert.ok(result.summary.unresolved_expected_count >= 1);
});

test('representative numeric TestPatterns derive minimum/minimum_minus_1, maximum/maximum_plus_1, null and invalid_format with Expected', () => {
  const sandbox = loadRuntime();
  const registry = readJson('data/json/config/validation_type_registry_v0_1.json');
  const definitions = readJson('fielddefs/samples/frb_fft_measurement_field_definitions_v0_2.json');
  const field = definitions.field_definitions.find(item => item.field_path === '$.measurement_sessions[].sample_rate_hz');
  sandbox.__registry = registry;
  sandbox.__field = field;

  vm.runInContext(`
    globalThis.__result = new DefinitionVerificationService({ registry: __registry }).derive(__field);
  `, sandbox);
  const result = plain(sandbox.__result);
  const patterns = Object.fromEntries(result.test_patterns.map(item => [item.pattern_key, item]));

  assert.equal(patterns.valid_value.input.value, 100);
  assert.equal(patterns.minimum.input.value, 100);
  assert.equal(patterns.minimum.expected.outcome, 'ACCEPT');
  assert.equal(patterns.minimum_minus_1.input.value, 99);
  assert.equal(patterns.minimum_minus_1.expected.outcome, 'REJECT');
  assert.equal(patterns.maximum.input.value, 200000);
  assert.equal(patterns.maximum.expected.outcome, 'ACCEPT');
  assert.equal(patterns.maximum_plus_1.input.value, 200001);
  assert.equal(patterns.maximum_plus_1.expected.outcome, 'REJECT');
  assert.equal(patterns.null.expected.outcome, 'REJECT');
  assert.equal(patterns.invalid_format.expected.outcome, 'REJECT');
  assert.equal(patterns.required_missing.expected.outcome, 'REJECT');
});

test('Preview and Runner entry points are identical views of the same pure derivation service', () => {
  const sandbox = loadRuntime();
  const registry = readJson('data/json/config/validation_type_registry_v0_1.json');
  const definitions = readJson('fielddefs/samples/frb_fft_measurement_field_definitions_v0_2.json');
  const field = definitions.field_definitions.find(item => item.field_path === '$.measurement_sessions[].peak_frequency_hz');
  sandbox.__registry = registry;
  sandbox.__field = field;

  vm.runInContext(`
    globalThis.__service = new DefinitionVerificationService({ registry: __registry });
    globalThis.__preview = __service.deriveForPreview(__field);
    globalThis.__runner = __service.deriveForRunner(__field);
  `, sandbox);

  assert.deepEqual(plain(sandbox.__preview), plain(sandbox.__runner));
  assert.equal(sandbox.__preview.source.registry_version, '0.1.0');
  assert.equal(sandbox.__preview.field_contract.source.validation_type_id, 'studio.float.measurement');
});

test('Registry default bounds cannot be loosened by Field Definition overrides', () => {
  const sandbox = loadRuntime();
  const registry = readJson('data/json/config/validation_type_registry_v0_1.json');
  sandbox.__registry = registry;
  sandbox.__field = {
    field_path: '$.score',
    validation_type: 'studio.integer.non_negative',
    constraint_overrides: {
      required: true,
      nullable: false,
      minimum: { value: -1, inclusive: true }
    }
  };

  vm.runInContext(`globalThis.__contract = new FieldContractResolver(__registry).resolve(__field);`, sandbox);
  const contract = plain(sandbox.__contract);
  assert.equal(contract.resolution_status, 'INVALID');
  assert.ok(contract.issues.some(issue => issue.code === 'CONSTRAINT_OVERRIDE_LOOSENS_DEFAULT' && issue.constraint === 'minimum'));
});


test('valid_value / invalid_format honor string Validation Type pattern semantics', () => {
  const sandbox = loadRuntime();
  const registry = readJson('data/json/config/validation_type_registry_v0_1.json');
  sandbox.__registry = registry;
  sandbox.__field = {
    field_path: '$.code',
    validation_type: 'studio.string.numeric',
    constraint_overrides: { required: true, nullable: false, empty_string_allowed: false }
  };

  vm.runInContext(`globalThis.__result = new DefinitionVerificationService({ registry: __registry }).derive(__field);`, sandbox);
  const result = plain(sandbox.__result);
  const patterns = Object.fromEntries(result.test_patterns.map(item => [item.pattern_key, item]));
  assert.match(patterns.valid_value.input.value, /^[0-9]+$/);
  assert.equal(patterns.valid_value.expected.outcome, 'ACCEPT');
  assert.equal(typeof patterns.invalid_format.input.value, 'string');
  assert.doesNotMatch(patterns.invalid_format.input.value, /^[0-9]+$/);
  assert.equal(patterns.invalid_format.expected.outcome, 'REJECT');
});



test('resolved minimum/maximum range contradictions are INVALID instead of generating misleading Expected', () => {
  const sandbox = loadRuntime();
  const registry = readJson('data/json/config/validation_type_registry_v0_1.json');
  sandbox.__registry = registry;
  sandbox.__field = {
    field_path: '$.score',
    validation_type: 'studio.integer.non_negative',
    constraint_overrides: {
      required: true,
      nullable: false,
      minimum: { value: 90, inclusive: true },
      maximum: { value: 10, inclusive: true }
    }
  };

  vm.runInContext(`globalThis.__result = new DefinitionVerificationService({ registry: __registry }).derive(__field);`, sandbox);
  const result = plain(sandbox.__result);
  assert.equal(result.status, 'INVALID');
  assert.equal(result.test_patterns.length, 0);
  assert.ok(result.field_contract.issues.some(issue => issue.code === 'CONSTRAINT_RANGE_INVALID'));
});

test('all current FRB FFT sample Field Definitions can be derived without DOM or persistence state', () => {
  const sandbox = loadRuntime();
  const registry = readJson('data/json/config/validation_type_registry_v0_1.json');
  const definitions = readJson('fielddefs/samples/frb_fft_measurement_field_definitions_v0_2.json');
  sandbox.__registry = registry;
  sandbox.__fields = definitions.field_definitions;

  vm.runInContext(`
    globalThis.__service = new DefinitionVerificationService({ registry: __registry });
    globalThis.__results = __fields.map(field => __service.derive(field));
  `, sandbox);
  const results = plain(sandbox.__results);
  assert.equal(results.length, definitions.field_definition_count);
  assert.ok(results.every(result => result.status === 'READY' || result.status === 'PARTIAL'));
  assert.ok(results.every(result => result.test_patterns.length >= 4));
  assert.ok(results.every(result => result.source.registry_version === registry.registry_version));
});

test('Service output remains JSON-serializable Plain Data and contains no DOM dependency', () => {
  const sandbox = loadRuntime();
  const registry = readJson('data/json/config/validation_type_registry_v0_1.json');
  const definitions = readJson('fielddefs/samples/frb_fft_measurement_field_definitions_v0_2.json');
  sandbox.__registry = registry;
  sandbox.__field = definitions.field_definitions[0];

  vm.runInContext(`globalThis.__result = new DefinitionVerificationService({ registry: __registry }).derive(__field);`, sandbox);
  const serialized = JSON.stringify(sandbox.__result);
  assert.ok(serialized.includes('definition_verification_result_v0_1'));

  for (const relativePath of [
    'wwwroot/js/services/definition/definition_verification_common.js',
    'wwwroot/js/services/definition/field_contract_resolver.js',
    'wwwroot/js/services/definition/test_pattern_deriver.js',
    'wwwroot/js/services/definition/expected_resolver.js',
    'wwwroot/js/services/definition/definition_verification_service.js'
  ]) {
    const source = readText(relativePath);
    assert.doesNotMatch(source, /\bdocument\b|querySelector|EditorComponent|SubGridComponent/);
  }
});
