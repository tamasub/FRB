// v0.18.69-definition-driven-search-test-phase6
// Field Definition -> SearchCapability -> Search TestPattern -> SearchFilter Actual を接続する。
// UI/DOMに依存せず、Search契約そのものをDefinition Driven Testとして実行する。

const SEARCH_DEFINITION_TEST_RUNNER_ID = 'studio.search_definition_test_runner';
const SEARCH_DEFINITION_TEST_RUNNER_VERSION = '0.1.0';

class SearchDefinitionTestRunner {
  constructor({ capabilityResolver=null, patternDeriver=null, searchFilter=null, clock=null }={}) {
    this.capabilityResolver = capabilityResolver;
    this.patternDeriver = patternDeriver ?? new SearchTestPatternDeriver();
    this.searchFilter = searchFilter ?? globalThis.SearchFilter;
    this.clock = clock ?? (() => new Date().toISOString());
  }

  runDocument(definitionDocument={}, registries={}, options={}) {
    const fields = Array.isArray(definitionDocument?.field_definitions)
      ? definitionDocument.field_definitions
      : [];
    const resolver = this.capabilityResolver ?? new SearchCapabilityResolver({
      searchOperatorRegistry: registries.search_operator_registry,
      validationTypeRegistry: registries.validation_type_registry
    });
    const fieldResults = fields.map(field => this.#runField(field, resolver, registries));
    const summary = fieldResults.reduce((acc, field) => {
      acc.field_count += 1;
      acc.pattern_count += field.summary.pattern_count;
      acc.passed_count += field.summary.passed_count;
      acc.failed_count += field.summary.failed_count;
      acc.unresolved_count += field.summary.unresolved_count;
      if (field.status === 'INVALID') acc.invalid_field_count += 1;
      return acc;
    }, {
      field_count: 0,
      pattern_count: 0,
      passed_count: 0,
      failed_count: 0,
      unresolved_count: 0,
      invalid_field_count: 0
    });

    return {
      schema_version: 'search_definition_test_runner_result_v0_1',
      document_type: 'search_definition_test_runner_result',
      runner: {
        id: SEARCH_DEFINITION_TEST_RUNNER_ID,
        version: SEARCH_DEFINITION_TEST_RUNNER_VERSION
      },
      status: summary.invalid_field_count > 0
        ? 'INVALID'
        : summary.failed_count > 0
          ? 'FAILED'
          : summary.unresolved_count > 0
            ? 'PARTIAL'
            : 'PASSED',
      executed_at: this.clock(),
      source: {
        definition_id: String(definitionDocument?.definition_id ?? ''),
        schema_version: String(definitionDocument?.schema_version ?? ''),
        definition_path: String(options.definition_path ?? ''),
        search_operator_registry_version: String(registries?.search_operator_registry?.registry_version ?? ''),
        validation_type_registry_version: String(registries?.validation_type_registry?.registry_version ?? '')
      },
      summary,
      fields: fieldResults
    };
  }

  #runField(fieldDefinition, resolver, registries) {
    const capability = resolver.resolve(fieldDefinition, {
      searchOperatorRegistry: registries.search_operator_registry,
      validationTypeRegistry: registries.validation_type_registry
    });
    const derived = this.patternDeriver.derive(fieldDefinition, capability);
    const testCases = derived.patterns.map(pattern => this.#runPattern(pattern));
    const summary = {
      pattern_count: testCases.length,
      passed_count: testCases.filter(item => item.comparison.status === 'PASS').length,
      failed_count: testCases.filter(item => item.comparison.status === 'FAIL').length,
      unresolved_count: derived.status === 'UNRESOLVED' ? 1 : 0
    };
    const invalid = capability.resolution_status === 'INVALID';

    return {
      field: String(fieldDefinition?.field ?? fieldDefinition?.field_path ?? ''),
      caption: String(fieldDefinition?.caption ?? ''),
      type: String(fieldDefinition?.type ?? ''),
      validation_type_id: String(fieldDefinition?.validation_type ?? ''),
      value_family: String(capability?.value_family ?? ''),
      status: invalid ? 'INVALID' : summary.failed_count > 0 ? 'FAILED' : derived.status === 'UNRESOLVED' ? 'PARTIAL' : 'PASSED',
      field_definition_snapshot: this.#clone(fieldDefinition),
      search_capability_snapshot: this.#clone(capability),
      test_pattern_snapshot: this.#clone(derived),
      issues: this.#clone(capability?.issues ?? []),
      summary,
      test_cases: testCases
    };
  }

  #runPattern(pattern) {
    const row = pattern?.input?.row ?? {};
    const criterion = pattern?.input?.criterion ?? {};
    const matched = Boolean(this.searchFilter?.matchesCriterion?.(row, criterion));
    const actual = {
      matched,
      outcome: matched ? 'MATCH' : 'NO_MATCH'
    };
    const expected = this.#clone(pattern?.expected ?? {});
    const pass = expected.matched === actual.matched;
    return {
      pattern_id: pattern.pattern_id,
      pattern_key: pattern.pattern_key,
      category: pattern.category,
      operator: pattern.operator,
      input: this.#clone(pattern.input),
      expected,
      actual,
      comparison: {
        status: pass ? 'PASS' : 'FAIL',
        reason_code: pass ? 'MATCH_RESULT_EQUAL' : 'MATCH_RESULT_MISMATCH'
      },
      source: this.#clone(pattern.source ?? {})
    };
  }

  #clone(value) {
    if (value === undefined) return undefined;
    return JSON.parse(JSON.stringify(value));
  }
}

globalThis.SEARCH_DEFINITION_TEST_RUNNER_ID = SEARCH_DEFINITION_TEST_RUNNER_ID;
globalThis.SEARCH_DEFINITION_TEST_RUNNER_VERSION = SEARCH_DEFINITION_TEST_RUNNER_VERSION;
globalThis.SearchDefinitionTestRunner = SearchDefinitionTestRunner;
