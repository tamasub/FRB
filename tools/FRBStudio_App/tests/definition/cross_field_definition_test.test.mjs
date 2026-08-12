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

function plain(value) {
  return JSON.parse(JSON.stringify(value));
}

test('Cross Field LT derives A<B OK, A=B NG, A>B NG with interior representative values', () => {
  const sandbox = loadRuntime();
  sandbox.__registry = readJson('data/json/config/validation_type_registry_v0_1.json');
  sandbox.__document = readJson('fielddefs/samples/frb_fft_measurement_field_definitions_v0_2.json');
  sandbox.__constraint = sandbox.__document.cross_field_constraints[0];
  vm.runInContext(`
    globalThis.__preview = new CrossFieldVerificationService({ registry: __registry })
      .deriveForPreview(__constraint, __document);
  `, sandbox);
  const preview = plain(sandbox.__preview);
  const patterns = Object.fromEntries(preview.test_patterns.map(item => [item.pattern_key, item]));

  assert.equal(preview.status, 'PARTIAL');
  assert.equal(preview.constraint_id, 'analysis_start_date_before_end_date');
  assert.equal(preview.operator, 'LT');
  assert.equal(preview.unset_policy, 'REJECT_IF_EITHER_UNSET');
  assert.equal(preview.test_patterns.length, 3);
  assert.equal(preview.summary.compare_pattern_count, 3);
  assert.equal(preview.summary.unset_pattern_count, 0);
  assert.equal(patterns.left_less_right.expected.outcome, 'ACCEPT');
  assert.equal(patterns.left_equal_right.expected.outcome, 'REJECT');
  assert.equal(patterns.left_greater_right.expected.outcome, 'REJECT');
  assert.ok(patterns.left_less_right.input.left.value < patterns.left_less_right.input.right.value);
  assert.equal(patterns.left_equal_right.input.left.value, patterns.left_equal_right.input.right.value);
  assert.ok(patterns.left_greater_right.input.left.value > patterns.left_greater_right.input.right.value);
  assert.equal(preview.representative_values.derivation, 'interior_candidate_fallback');
  assert.notEqual(patterns.left_less_right.input.left.value, '2020-01-01');
  assert.notEqual(patterns.left_less_right.input.right.value, '2090-01-01');
});

test('Cross Field 6 Operator Matrix uses the same LOW/MID/HIGH=25/50/75 and only Expected changes', () => {
  const sandbox = loadRuntime();
  sandbox.__registry = readJson('data/json/config/validation_type_registry_v0_1.json');
  sandbox.__document = readJson('fielddefs/samples/cross_field_compare_operator_matrix_v0_1.json');
  vm.runInContext(`
    globalThis.__service = new CrossFieldVerificationService({ registry: __registry });
    globalThis.__matrix = __document.cross_field_constraints.map(constraint =>
      __service.deriveForRunner(constraint, __document)
    );
    globalThis.__matrixRun = new DefinitionTestRunnerCore({ crossFieldVerificationService: __service })
      .runDocument(__document, __registry);
  `, sandbox);
  const matrix = plain(sandbox.__matrix);
  const matrixRun = plain(sandbox.__matrixRun);
  const expected = {
    LT:  ['ACCEPT', 'REJECT', 'REJECT'],
    LTE: ['ACCEPT', 'ACCEPT', 'REJECT'],
    EQ:  ['REJECT', 'ACCEPT', 'REJECT'],
    NE:  ['ACCEPT', 'REJECT', 'ACCEPT'],
    GTE: ['REJECT', 'ACCEPT', 'ACCEPT'],
    GT:  ['REJECT', 'REJECT', 'ACCEPT']
  };

  assert.equal(matrix.length, 6);
  matrix.forEach(result => {
    assert.equal(result.status, 'READY');
    assert.deepEqual(
      [result.representative_values.low, result.representative_values.equal, result.representative_values.high],
      [25, 50, 75]
    );
    assert.equal(result.representative_values.derivation, 'common_range_quartiles');
    assert.deepEqual(result.test_patterns.map(item => item.expected.outcome), expected[result.operator]);
    assert.deepEqual(
      result.test_patterns.map(item => [item.input.left.value, item.input.right.value]),
      [[25, 75], [50, 50], [75, 25]]
    );
  });
  assert.equal(matrixRun.summary.cross_field_constraint_count, 6);
  assert.equal(matrixRun.summary.cross_field_pattern_count, 18);
  assert.equal(matrixRun.summary.cross_field_passed_count, 18);
  assert.equal(matrixRun.summary.cross_field_failed_count, 0);
  assert.equal(matrixRun.summary.cross_field_unresolved_count, 0);
  assert.ok(matrixRun.cross_field_constraints.every(item => item.test_cases.every(testCase => testCase.comparison.status === 'PASS')));
});

test('Cross Field Preview and Runner execute exactly the same derived TestPattern / Expected', () => {
  const sandbox = loadRuntime();
  sandbox.__registry = readJson('data/json/config/validation_type_registry_v0_1.json');
  sandbox.__document = readJson('fielddefs/samples/frb_fft_measurement_field_definitions_v0_2.json');
  sandbox.__constraint = sandbox.__document.cross_field_constraints[0];
  vm.runInContext(`
    globalThis.__service = new CrossFieldVerificationService({ registry: __registry });
    globalThis.__preview = __service.deriveForPreview(__constraint, __document);
    globalThis.__run = new DefinitionTestRunnerCore({ crossFieldVerificationService: __service })
      .runCrossFieldConstraint(__constraint, __document, __registry);
  `, sandbox);
  const preview = plain(sandbox.__preview);
  const run = plain(sandbox.__run);

  assert.deepEqual(
    run.test_cases.map(item => ({ pattern_id: item.pattern_id, input: item.input, expected: item.expected })),
    preview.test_patterns.map(item => ({ pattern_id: item.pattern_id, input: item.input, expected: item.expected }))
  );
  assert.equal(run.summary.pattern_count, 3);
  assert.equal(run.summary.passed_count, 3);
  assert.equal(run.summary.failed_count, 0);
  assert.ok(run.test_cases.every(item => item.comparison.status === 'PASS'));
});

test('FRB FFT Definition Runner connects 126 single-field cases + 3 Cross Field cases in one Result', () => {
  const sandbox = loadRuntime();
  sandbox.__registry = readJson('data/json/config/validation_type_registry_v0_1.json');
  sandbox.__document = readJson('fielddefs/samples/frb_fft_measurement_field_definitions_v0_2.json');
  sandbox.__meta = {
    field_definition_path: 'fielddefs/samples/frb_fft_measurement_field_definitions_v0_2.json',
    field_definition_sha256: 'field-hash',
    registry_path: 'data/json/config/validation_type_registry_v0_1.json',
    registry_sha256: 'registry-hash'
  };
  vm.runInContext(`
    globalThis.__run = new DefinitionTestRunnerCore().runDocument(__document, __registry, { source_metadata: __meta });
  `, sandbox);
  const run = plain(sandbox.__run);

  assert.equal(run.schema_version, 'definition_test_runner_result_v0_2');
  assert.equal(run.runner.version, '0.3.0');
  assert.equal(run.summary.field_pattern_count, 126);
  assert.equal(run.summary.cross_field_constraint_count, 1);
  assert.equal(run.summary.cross_field_pattern_count, 3);
  assert.equal(run.summary.pattern_count, 129);
  assert.equal(run.summary.passed_count, 129);
  assert.equal(run.summary.failed_count, 0);
  assert.equal(run.cross_field_constraints[0].constraint_id, 'analysis_start_date_before_end_date');
  assert.equal(run.cross_field_constraints[0].unset_policy, 'REJECT_IF_EITHER_UNSET');
  assert.equal(run.cross_field_constraints[0].source.field_definition_sha256, 'field-hash');
  assert.equal(run.cross_field_constraints[0].source.registry_sha256, 'registry-hash');
});

test('Evidence Builder separates Resolved Expected Snapshot / Actual / Diff and keeps trace relations', () => {
  const sandbox = loadRuntime();
  sandbox.__registry = readJson('data/json/config/validation_type_registry_v0_1.json');
  sandbox.__document = readJson('fielddefs/samples/frb_fft_measurement_field_definitions_v0_2.json');
  vm.runInContext(`
    globalThis.__run = new DefinitionTestRunnerCore({ clock: () => '2026-08-12T20:13:00+09:00' })
      .runDocument(__document, __registry);
    globalThis.__evidence = new DefinitionTestEvidenceBuilder().buildArtifacts(__run, {
      source_files: {
        expectedFile: 'expected.json',
        actualFile: 'actual.json',
        diffFile: 'diff.json'
      }
    });
  `, sandbox);
  const evidence = plain(sandbox.__evidence);

  assert.equal(evidence.expected.document_type, 'definition_test_resolved_snapshot');
  assert.equal(evidence.expected.checks.length, 129);
  assert.equal(evidence.actual.document_type, 'definition_test_actual');
  assert.equal(evidence.actual.checks.length, 129);
  assert.ok(evidence.actual.checks.every(item => !Object.hasOwn(item, 'expected') && !Object.hasOwn(item, 'pass')));
  assert.equal(evidence.diff.schema_version, 'diff_result_v0_1');
  assert.equal(evidence.diff.document_type, 'diff_result');
  assert.equal(evidence.diff.domain, 'contracts');
  assert.equal(evidence.diff.total, 129);
  assert.equal(evidence.diff.failedCount, 0);
  assert.ok(evidence.diff.checks.every(item => item.pass === true));
  assert.equal(evidence.relations.relations.length, 129);
  assert.ok(evidence.relations.relations.some(item => item.scope === 'cross_field' && item.constraint_id === 'analysis_start_date_before_end_date'));
});

test('Cross Field verification never guesses missing referenced Field Definitions', () => {
  const sandbox = loadRuntime();
  sandbox.__registry = readJson('data/json/config/validation_type_registry_v0_1.json');
  sandbox.__document = readJson('fielddefs/samples/frb_fft_measurement_field_definitions_v0_2.json');
  sandbox.__constraint = {
    id: 'missing_reference_sample',
    constraint_type: 'studio.cross_field.compare',
    left_field_path: '$.analysis_start_date',
    operator: 'LT',
    right_field_path: '$.does_not_exist',
    unset_policy: 'REJECT_IF_EITHER_UNSET'
  };
  vm.runInContext(`
    globalThis.__verification = new CrossFieldVerificationService({ registry: __registry })
      .deriveForRunner(__constraint, __document);
  `, sandbox);
  const verification = plain(sandbox.__verification);

  assert.equal(verification.status, 'INVALID');
  assert.equal(verification.test_patterns.length, 0);
  assert.ok(verification.issues.some(item => item.code === 'RIGHT_FIELD_DEFINITION_NOT_FOUND'));
});

test('Cross Field treats accepted null / empty string as semantic unset and applies only OK/NG policy', () => {
  const sandbox = loadRuntime();
  sandbox.__registry = readJson('data/json/config/validation_type_registry_v0_1.json');
  sandbox.__document = {
    field_definitions: [
      {
        field_path: '$.left',
        validation_type: 'studio.string.single_line',
        constraint_overrides: { required: true, nullable: true, empty_string_allowed: false, minimum_length: 1, maximum_length: 10 }
      },
      {
        field_path: '$.right',
        validation_type: 'studio.string.single_line',
        constraint_overrides: { required: true, nullable: false, empty_string_allowed: true, minimum_length: 0, maximum_length: 10 }
      }
    ]
  };
  sandbox.__constraintOk = {
    id: 'unset_policy_ok',
    constraint_type: 'studio.cross_field.compare',
    left_field_path: '$.left',
    operator: 'LT',
    right_field_path: '$.right',
    unset_policy: 'ACCEPT_IF_EITHER_UNSET'
  };
  sandbox.__constraintNg = { ...sandbox.__constraintOk, id: 'unset_policy_ng', unset_policy: 'REJECT_IF_EITHER_UNSET' };
  vm.runInContext(`
    globalThis.__service = new CrossFieldVerificationService({ registry: __registry });
    globalThis.__ok = __service.deriveForRunner(__constraintOk, __document);
    globalThis.__ng = __service.deriveForRunner(__constraintNg, __document);
    globalThis.__okRun = new DefinitionTestRunnerCore({ crossFieldVerificationService: __service })
      .runCrossFieldConstraint(__constraintOk, __document, __registry);
    globalThis.__ngRun = new DefinitionTestRunnerCore({ crossFieldVerificationService: __service })
      .runCrossFieldConstraint(__constraintNg, __document, __registry);
  `, sandbox);
  const ok = plain(sandbox.__ok);
  const ng = plain(sandbox.__ng);
  const okRun = plain(sandbox.__okRun);
  const ngRun = plain(sandbox.__ngRun);

  const okUnset = ok.test_patterns.filter(item => item.category === 'cross_field_unset');
  const ngUnset = ng.test_patterns.filter(item => item.category === 'cross_field_unset');
  assert.deepEqual(okUnset.map(item => item.pattern_key), ['left_unset', 'right_unset', 'both_unset']);
  assert.equal(okUnset[0].input.left.value, null);
  assert.equal(okUnset[1].input.right.value, '');
  assert.ok(okUnset.every(item => item.expected.outcome === 'ACCEPT'));
  assert.ok(ngUnset.every(item => item.expected.outcome === 'REJECT'));
  assert.equal(okRun.summary.failed_count, 0);
  assert.equal(ngRun.summary.failed_count, 0);
  assert.ok(okRun.test_cases.filter(item => item.category === 'cross_field_unset').every(item => item.actual.outcome === 'ACCEPT'));
  assert.ok(ngRun.test_cases.filter(item => item.category === 'cross_field_unset').every(item => item.actual.outcome === 'REJECT'));
});

test('Legacy null_policy is not silently treated as PASS and requires migration to unset_policy', () => {
  const sandbox = loadRuntime();
  sandbox.__registry = readJson('data/json/config/validation_type_registry_v0_1.json');
  sandbox.__document = readJson('fielddefs/samples/frb_fft_measurement_field_definitions_v0_2.json');
  sandbox.__constraint = {
    id: 'legacy_null_policy',
    constraint_type: 'studio.cross_field.compare',
    left_field_path: '$.analysis_start_date',
    operator: 'LT',
    right_field_path: '$.analysis_end_date',
    null_policy: 'DEFER_TO_FIELD_CONTRACTS'
  };
  vm.runInContext(`
    globalThis.__verification = new CrossFieldVerificationService({ registry: __registry })
      .deriveForRunner(__constraint, __document);
  `, sandbox);
  const verification = plain(sandbox.__verification);

  assert.equal(verification.status, 'INVALID');
  assert.equal(verification.test_patterns.length, 0);
  assert.ok(verification.issues.some(item => item.code === 'CROSS_FIELD_LEGACY_NULL_POLICY_REQUIRES_MIGRATION'));
});
