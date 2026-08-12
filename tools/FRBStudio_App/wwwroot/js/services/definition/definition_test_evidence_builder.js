// v0.18.45-definition-test-runner-diff-crossfield-e2e
// Converts Definition Test Runner Result into Expected Snapshot / Actual / Diff / trace evidence artifacts.

const DEFINITION_TEST_EVIDENCE_TEST_ID = 'definition_test_runner_frb_fft_v0_1';

class DefinitionTestEvidenceBuilder {
  buildArtifacts(runnerResult={}, options={}) {
    const testId = String(options.test_id ?? DEFINITION_TEST_EVIDENCE_TEST_ID);
    const title = String(options.title ?? 'FRB FFT Field Definition — Definition Driven Test E2E');
    const generatedAt = String(runnerResult?.executed_at ?? new Date().toISOString());
    const flattened = this.#flattenCases(runnerResult);
    const failed = flattened.filter(item => item.comparison?.status !== 'PASS');
    const sourceFiles = definitionVerificationClone(options.source_files ?? {});

    const expected = {
      schema_version: 'definition_test_resolved_snapshot_v0_1',
      document_type: 'definition_test_resolved_snapshot',
      test_id: testId,
      testId,
      title,
      resolved_at: generatedAt,
      source: definitionVerificationClone(runnerResult?.source ?? {}),
      runner: definitionVerificationClone(runnerResult?.runner ?? {}),
      checks: flattened.map(item => ({
        check_id: item.check_id,
        name: item.name,
        target: item.target,
        type: 'outcome_equals',
        input: definitionVerificationClone(item.input),
        expected: item.expected?.outcome ?? 'UNRESOLVED',
        expected_reason_code: item.expected?.reason_code ?? '',
        source: definitionVerificationClone(item.source)
      }))
    };

    const actual = {
      schema_version: 'definition_test_actual_v0_1',
      document_type: 'definition_test_actual',
      test_id: testId,
      testId,
      title,
      observed_at: generatedAt,
      source: definitionVerificationClone(runnerResult?.source ?? {}),
      runner: definitionVerificationClone(runnerResult?.runner ?? {}),
      checks: flattened.map(item => ({
        check_id: item.check_id,
        name: item.name,
        target: item.target,
        actual: item.actual?.outcome ?? 'UNRESOLVED',
        actual_reason_code: item.actual?.reason_code ?? '',
        observed_at: generatedAt,
        source: definitionVerificationClone(item.source)
      }))
    };

    const diffChecks = flattened.map(item => {
      const pass = item.comparison?.status === 'PASS';
      const expectedOutcome = item.expected?.outcome ?? 'UNRESOLVED';
      const actualOutcome = item.actual?.outcome ?? 'UNRESOLVED';
      return {
        check_id: item.check_id,
        name: item.name,
        target: item.target,
        type: 'outcome_equals',
        expected: expectedOutcome,
        actual: actualOutcome,
        missing: [],
        pass,
        message: pass ? 'OK' : `${item.check_id} failed: expected ${expectedOutcome}, actual ${actualOutcome}`,
        input: definitionVerificationClone(item.input),
        expected_reason_code: item.expected?.reason_code ?? '',
        actual_reason_code: item.actual?.reason_code ?? '',
        comparison_reason_code: item.comparison?.reason_code ?? '',
        source: definitionVerificationClone(item.source)
      };
    });
    const failedChecks = diffChecks.filter(item => !item.pass);
    const firstFailure = failedChecks.length > 0
      ? {
          check_id: failedChecks[0].check_id,
          name: failedChecks[0].name,
          target: failedChecks[0].target,
          type: failedChecks[0].type,
          expected: failedChecks[0].expected,
          actual: failedChecks[0].actual,
          missing: []
        }
      : null;
    const passCount = diffChecks.length - failedChecks.length;
    const diff = {
      schema_version: 'diff_result_v0_1',
      document_type: 'diff_result',
      domain: 'contracts',
      diff_kind: 'definition_verification',
      test_id: testId,
      testId,
      test_name: title,
      title,
      generated_at: generatedAt,
      status: failedChecks.length === 0 ? 'pass' : 'fail',
      resultLabel: failedChecks.length === 0 ? '✅ PASS' : '🚨 FAIL',
      summary: failedChecks.length === 0
        ? `✅ ${diffChecks.length}件のDefinition TestがExpectedと一致しました。`
        : `🚨 ${failedChecks.length}件の差分を検出しました: ${failedChecks.map(item => item.check_id).join(', ')}`,
      total: diffChecks.length,
      passCount,
      failCount: failedChecks.length,
      failedCount: failedChecks.length,
      failedChecks: failedChecks.map(item => item.name),
      failedCheckIds: failedChecks.map(item => item.check_id),
      firstFailure,
      result_summary: {
        total_count: diffChecks.length,
        pass_count: passCount,
        fail_count: failedChecks.length,
        total: diffChecks.length,
        passCount,
        failCount: failedChecks.length,
        field_pattern_count: Number(runnerResult?.summary?.field_pattern_count ?? 0),
        cross_field_pattern_count: Number(runnerResult?.summary?.cross_field_pattern_count ?? 0),
        runner_result_status: String(runnerResult?.status ?? '')
      },
      sourceFiles,
      source: definitionVerificationClone(runnerResult?.source ?? {}),
      runner: definitionVerificationClone(runnerResult?.runner ?? {}),
      checks: diffChecks
    };

    const relations = {
      schema_version: 'definition_test_trace_relations_v0_1',
      document_type: 'definition_test_trace_relations',
      test_id: testId,
      title,
      generated_at: generatedAt,
      source: definitionVerificationClone(runnerResult?.source ?? {}),
      relations: flattened.map(item => ({
        check_id: item.check_id,
        scope: item.scope,
        field_path: item.field_path ?? '',
        constraint_id: item.constraint_id ?? '',
        validation_type_id: item.validation_type_id ?? '',
        pattern_id: item.pattern_id,
        source: definitionVerificationClone(item.source)
      }))
    };

    return {
      expected,
      actual,
      diff,
      relations,
      summary: definitionVerificationClone(runnerResult)
    };
  }

  #flattenCases(runnerResult) {
    const items = [];
    (runnerResult?.fields ?? []).forEach(field => {
      (field?.test_cases ?? []).forEach(testCase => {
        items.push({
          scope: 'field',
          check_id: `field::${field.field_path}::${testCase.pattern_key}`,
          name: testCase.pattern_key,
          target: field.field_path,
          field_path: field.field_path,
          constraint_id: '',
          validation_type_id: field.validation_type_id,
          pattern_id: testCase.pattern_id,
          input: testCase.input,
          expected: testCase.expected,
          actual: testCase.actual,
          comparison: testCase.comparison,
          source: testCase.source ?? field.source ?? {}
        });
      });
    });
    (runnerResult?.cross_field_constraints ?? []).forEach(constraint => {
      (constraint?.test_cases ?? []).forEach(testCase => {
        items.push({
          scope: 'cross_field',
          check_id: `cross::${constraint.constraint_id}::${testCase.pattern_key}`,
          name: testCase.pattern_key,
          target: `${constraint.left_field_path} ${constraint.operator} ${constraint.right_field_path}`,
          field_path: '',
          constraint_id: constraint.constraint_id,
          validation_type_id: '',
          pattern_id: testCase.pattern_id,
          input: testCase.input,
          expected: testCase.expected,
          actual: testCase.actual,
          comparison: testCase.comparison,
          source: testCase.source ?? constraint.source ?? {}
        });
      });
    });
    return items;
  }
}

globalThis.DEFINITION_TEST_EVIDENCE_TEST_ID = DEFINITION_TEST_EVIDENCE_TEST_ID;
globalThis.DefinitionTestEvidenceBuilder = DefinitionTestEvidenceBuilder;
