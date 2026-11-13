// v0.18.46-definition-review-evidence-and-fielddefs-access
// Converts Definition Test Runner Result into Expected Snapshot / Actual / Diff / trace evidence artifacts.
// Evidence must preserve the execution-time contract used to explain each Diff later.

const DEFINITION_TEST_EVIDENCE_TEST_ID = 'definition_test_runner_frb_fft_v0_1';
const DEFINITION_TEST_DIFF_VIEW_DEF = 'fielddefs/definition_test_diff_view_def_v0_1.json';

class DefinitionTestEvidenceBuilder {
  buildArtifacts(runnerResult={}, options={}) {
    const testId = String(options.test_id ?? DEFINITION_TEST_EVIDENCE_TEST_ID);
    const title = String(options.title ?? 'FRB FFT Field Definition — Definition Driven Test E2E');
    const generatedAt = String(runnerResult?.executed_at ?? new Date().toISOString());
    const flattened = this.#flattenCases(runnerResult);
    const sourceFiles = definitionVerificationClone(options.source_files ?? {});
    const reviewSnapshots = this.#buildDefinitionReviewSnapshots(runnerResult, generatedAt);

    const expected = {
      schema_version: 'definition_test_resolved_snapshot_v0_2',
      document_type: 'definition_test_resolved_snapshot',
      test_id: testId,
      testId,
      title,
      resolved_at: generatedAt,
      source: definitionVerificationClone(runnerResult?.source ?? {}),
      runner: definitionVerificationClone(runnerResult?.runner ?? {}),
      definition_review_snapshots: definitionVerificationClone(reviewSnapshots),
      checks: flattened.map(item => ({
        check_id: item.check_id,
        name: item.name,
        pattern_id: item.pattern_id,
        category: item.category,
        target: item.target,
        field_path: item.field_path,
        constraint_id: item.constraint_id,
        validation_type_id: item.validation_type_id,
        constraint_ref: item.constraint_ref,
        type: 'outcome_equals',
        input: definitionVerificationClone(item.input),
        expected: item.expected?.outcome ?? 'UNRESOLVED',
        expected_reason_code: item.expected?.reason_code ?? '',
        source: definitionVerificationClone(item.source)
      }))
    };

    const actual = {
      schema_version: 'definition_test_actual_v0_2',
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
        pattern_id: item.pattern_id,
        category: item.category,
        target: item.target,
        field_path: item.field_path,
        constraint_id: item.constraint_id,
        validation_type_id: item.validation_type_id,
        constraint_ref: item.constraint_ref,
        input: definitionVerificationClone(item.input),
        actual: item.actual?.outcome ?? 'UNRESOLVED',
        actual_reason_code: item.actual?.reason_code ?? '',
        actual_violations: definitionVerificationClone(item.actual?.violations ?? []),
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
        pattern_id: item.pattern_id,
        category: item.category,
        target: item.target,
        field_path: item.field_path,
        constraint_id: item.constraint_id,
        validation_type_id: item.validation_type_id,
        constraint_ref: item.constraint_ref,
        definition_review_ref: item.field_path || item.constraint_id || '',
        type: 'outcome_equals',
        expected: expectedOutcome,
        actual: actualOutcome,
        missing: [],
        pass,
        result: pass ? 'PASS' : 'FAIL',
        message: pass ? '差分なし' : `${item.check_id} failed: expected ${expectedOutcome}, actual ${actualOutcome}`,
        input: definitionVerificationClone(item.input),
        expected_reason_code: item.expected?.reason_code ?? '',
        actual_reason_code: item.actual?.reason_code ?? '',
        actual_violations: definitionVerificationClone(item.actual?.violations ?? []),
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
      view_def: DEFINITION_TEST_DIFF_VIEW_DEF,
      view_def_candidates: [
        {
          view_def: DEFINITION_TEST_DIFF_VIEW_DEF,
          label: 'Definition Test Diff / Evidence Review',
          role: 'default',
          status: 'active',
          note: 'Execution Evidenceと実行時Field Definition Snapshotを同一Detailで確認する。'
        }
      ],
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
      definition_review_snapshots: reviewSnapshots,
      checks: diffChecks
    };

    const relations = {
      schema_version: 'definition_test_trace_relations_v0_2',
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
        constraint_ref: item.constraint_ref,
        definition_review_ref: item.field_path || item.constraint_id || '',
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

  #buildDefinitionReviewSnapshots(runnerResult, generatedAt) {
    return {
      schema_version: 'definition_review_snapshot_v0_1',
      captured_at: generatedAt,
      field_definition_source: definitionVerificationClone(runnerResult?.source?.field_definition_document ?? {}),
      validation_type_registry_source: definitionVerificationClone(runnerResult?.source?.validation_type_registry ?? {}),
      fields: (runnerResult?.fields ?? []).map(field => ({
        field_path: String(field?.field_path ?? ''),
        validation_type_id: String(field?.validation_type_id ?? ''),
        field_definition: definitionVerificationClone(field?.field_definition_snapshot ?? {}),
        verification_result: definitionVerificationClone(field?.verification_snapshot ?? {}),
        source: definitionVerificationClone(field?.source ?? {})
      }))
    };
  }

  #flattenCases(runnerResult) {
    const items = [];
    (runnerResult?.fields ?? []).forEach(field => {
      (field?.test_cases ?? []).forEach(testCase => {
        const constraintRef = String(
          testCase?.expected?.source?.constraint_ref
            ?? testCase?.actual?.violations?.find?.(item => item?.constraint)?.constraint
            ?? ''
        );
        items.push({
          scope: 'field',
          check_id: `field::${field.field_path}::${testCase.pattern_key}`,
          name: testCase.pattern_key,
          pattern_id: testCase.pattern_id,
          category: testCase.category,
          target: field.field_path,
          field_path: field.field_path,
          constraint_id: '',
          validation_type_id: field.validation_type_id,
          constraint_ref: constraintRef,
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
          pattern_id: testCase.pattern_id,
          category: testCase.category,
          target: `${constraint.left_field_path} ${constraint.operator} ${constraint.right_field_path}`,
          field_path: '',
          constraint_id: constraint.constraint_id,
          validation_type_id: '',
          constraint_ref: constraint.constraint_id,
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
globalThis.DEFINITION_TEST_DIFF_VIEW_DEF = DEFINITION_TEST_DIFF_VIEW_DEF;
globalThis.DefinitionTestEvidenceBuilder = DefinitionTestEvidenceBuilder;
