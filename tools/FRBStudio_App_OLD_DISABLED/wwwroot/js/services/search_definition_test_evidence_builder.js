// v0.18.69-definition-driven-search-test-phase6
// Search Definition Test Runner Result を Expected / Actual / Diff / Summary へ変換する。

const SEARCH_DEFINITION_TEST_DIFF_VIEW_DEF = 'search/search_definition_test_diff_view_def_v0_1.json';

class SearchDefinitionTestEvidenceBuilder {
  buildArtifacts(runnerResult={}, options={}) {
    const testId = String(options.test_id ?? 'definition_driven_search_v0_1');
    const title = String(options.title ?? 'Definition Driven Search Test');
    const generatedAt = String(runnerResult?.executed_at ?? new Date().toISOString());
    const checks = this.#flatten(runnerResult);
    const sourceFiles = this.#clone(options.source_files ?? {});

    const expected = {
      schema_version: 'search_definition_test_expected_v0_1',
      document_type: 'search_definition_test_expected',
      test_id: testId,
      title,
      resolved_at: generatedAt,
      source: this.#clone(runnerResult.source ?? {}),
      checks: checks.map(item => ({
        check_id: item.check_id,
        field: item.field,
        validation_type_id: item.validation_type_id,
        value_family: item.value_family,
        operator_set_id: item.operator_set_id,
        operator: item.operator,
        pattern_id: item.pattern_id,
        pattern_key: item.pattern_key,
        category: item.category,
        input: this.#clone(item.input),
        expected: item.expected.outcome,
        source: this.#clone(item.source)
      }))
    };

    const actual = {
      schema_version: 'search_definition_test_actual_v0_1',
      document_type: 'search_definition_test_actual',
      test_id: testId,
      title,
      observed_at: generatedAt,
      source: this.#clone(runnerResult.source ?? {}),
      checks: checks.map(item => ({
        check_id: item.check_id,
        field: item.field,
        operator: item.operator,
        pattern_id: item.pattern_id,
        input: this.#clone(item.input),
        actual: item.actual.outcome,
        comparison: item.comparison.status,
        source: this.#clone(item.source)
      }))
    };

    const diffChecks = checks.map(item => {
      const pass = item.comparison.status === 'PASS';
      return {
        check_id: item.check_id,
        name: item.pattern_key,
        pattern_id: item.pattern_id,
        category: item.category,
        target: item.field,
        field: item.field,
        validation_type_id: item.validation_type_id,
        value_family: item.value_family,
        operator_set_id: item.operator_set_id,
        operator: item.operator,
        type: 'search_match_outcome_equals',
        input: this.#clone(item.input),
        expected: item.expected.outcome,
        actual: item.actual.outcome,
        pass,
        result: pass ? 'PASS' : 'FAIL',
        message: pass
          ? '差分なし'
          : `${item.check_id} failed: expected ${item.expected.outcome}, actual ${item.actual.outcome}`,
        comparison_reason_code: item.comparison.reason_code,
        source: this.#clone(item.source)
      };
    });
    const failed = diffChecks.filter(item => !item.pass);
    const passCount = diffChecks.length - failed.length;

    const diff = {
      view_def: SEARCH_DEFINITION_TEST_DIFF_VIEW_DEF,
      view_def_candidates: [{
        view_def: SEARCH_DEFINITION_TEST_DIFF_VIEW_DEF,
        label: 'Definition Driven Search Test Diff',
        role: 'default',
        status: 'active'
      }],
      schema_version: 'diff_result_v0_1',
      document_type: 'diff_result',
      domain: 'contracts',
      diff_kind: 'definition_driven_search',
      test_id: testId,
      testId: testId,
      test_name: title,
      title,
      generated_at: generatedAt,
      status: failed.length === 0 ? 'pass' : 'fail',
      resultLabel: failed.length === 0 ? '✅ PASS' : '🚨 FAIL',
      summary: failed.length === 0
        ? `✅ ${diffChecks.length}件のSearch TestがExpectedと一致しました。`
        : `🚨 ${failed.length}件の差分を検出しました。`,
      total: diffChecks.length,
      passCount,
      failCount: failed.length,
      failedCount: failed.length,
      failedChecks: failed.map(item => item.name),
      failedCheckIds: failed.map(item => item.check_id),
      firstFailure: failed.length ? this.#clone(failed[0]) : null,
      result_summary: {
        total_count: diffChecks.length,
        pass_count: passCount,
        fail_count: failed.length,
        field_count: Number(runnerResult?.summary?.field_count ?? 0),
        pattern_count: Number(runnerResult?.summary?.pattern_count ?? 0),
        runner_result_status: String(runnerResult?.status ?? '')
      },
      sourceFiles,
      source: this.#clone(runnerResult.source ?? {}),
      runner: this.#clone(runnerResult.runner ?? {}),
      search_definition_snapshots: (runnerResult.fields ?? []).map(field => ({
        field: field.field,
        field_definition: this.#clone(field.field_definition_snapshot ?? {}),
        search_capability: this.#clone(field.search_capability_snapshot ?? {}),
        test_patterns: this.#clone(field.test_pattern_snapshot ?? {})
      })),
      checks: diffChecks
    };

    return {
      expected,
      actual,
      diff,
      summary: this.#clone(runnerResult)
    };
  }

  #flatten(runnerResult) {
    const items = [];
    for (const field of runnerResult?.fields ?? []) {
      for (const testCase of field?.test_cases ?? []) {
        items.push({
          check_id: `search::${field.field}::${testCase.pattern_key}`,
          field: field.field,
          validation_type_id: field.validation_type_id,
          value_family: field.value_family,
          operator_set_id: String(field?.search_capability_snapshot?.effective?.operator_set_id ?? ''),
          operator: testCase.operator,
          pattern_id: testCase.pattern_id,
          pattern_key: testCase.pattern_key,
          category: testCase.category,
          input: testCase.input,
          expected: testCase.expected,
          actual: testCase.actual,
          comparison: testCase.comparison,
          source: testCase.source ?? {}
        });
      }
    }
    return items;
  }

  #clone(value) {
    if (value === undefined) return undefined;
    return JSON.parse(JSON.stringify(value));
  }
}

globalThis.SEARCH_DEFINITION_TEST_DIFF_VIEW_DEF = SEARCH_DEFINITION_TEST_DIFF_VIEW_DEF;
globalThis.SearchDefinitionTestEvidenceBuilder = SearchDefinitionTestEvidenceBuilder;
