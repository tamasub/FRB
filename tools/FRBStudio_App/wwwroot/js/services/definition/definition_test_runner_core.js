// v0.18.44-definition-test-runner-core
// Executes Definition-derived TestPatterns without persisting TestPattern as canonical data.

const DEFINITION_TEST_RUNNER_RESULT_SCHEMA_VERSION = 'definition_test_runner_result_v0_1';
const DEFINITION_TEST_RUNNER_ID = 'studio.definition_test_runner.core';
const DEFINITION_TEST_RUNNER_VERSION = '0.1.0';

class DefinitionTestRunnerCore {
  constructor({ verificationService=null, valueValidator=null, clock=null }={}) {
    this.verificationService = verificationService;
    this.valueValidator = valueValidator ?? new DefinitionValueValidator();
    this.clock = clock ?? (() => new Date().toISOString());
  }

  runDocument(fieldDefinitionDocument={}, registry={}, options={}) {
    const definitions = Array.isArray(fieldDefinitionDocument?.field_definitions)
      ? fieldDefinitionDocument.field_definitions
      : [];
    const sourceMetadata = options.source_metadata ?? {};
    const fieldResults = definitions.map(fieldDefinition => this.runField(fieldDefinition, registry, { source_metadata: sourceMetadata }));

    const totals = fieldResults.reduce((summary, field) => {
      summary.field_count += 1;
      summary.pattern_count += field.summary.pattern_count;
      summary.passed_count += field.summary.passed_count;
      summary.failed_count += field.summary.failed_count;
      summary.unresolved_count += field.summary.unresolved_count;
      if (field.status === 'INVALID') summary.invalid_field_count += 1;
      if (field.status === 'PARTIAL') summary.partial_field_count += 1;
      return summary;
    }, {
      field_count: 0,
      pattern_count: 0,
      passed_count: 0,
      failed_count: 0,
      unresolved_count: 0,
      invalid_field_count: 0,
      partial_field_count: 0
    });

    return {
      schema_version: DEFINITION_TEST_RUNNER_RESULT_SCHEMA_VERSION,
      runner: this.#runnerMetadata(),
      status: this.#documentStatus(totals),
      executed_at: this.clock(),
      source: {
        field_definition_document: {
          definition_id: String(fieldDefinitionDocument?.definition_id ?? ''),
          schema_version: String(fieldDefinitionDocument?.schema_version ?? ''),
          document_type: String(fieldDefinitionDocument?.document_type ?? ''),
          updated_at: String(fieldDefinitionDocument?.updated_at ?? ''),
          sha256: String(sourceMetadata.field_definition_sha256 ?? ''),
          path: String(sourceMetadata.field_definition_path ?? '')
        },
        validation_type_registry: {
          schema_version: String(registry?.schema_version ?? ''),
          registry_version: String(registry?.registry_version ?? ''),
          document_type: String(registry?.document_type ?? ''),
          sha256: String(sourceMetadata.registry_sha256 ?? ''),
          path: String(sourceMetadata.registry_path ?? '')
        },
        verification_schema_version: String(globalThis.DEFINITION_VERIFICATION_SCHEMA_VERSION ?? '')
      },
      summary: totals,
      fields: fieldResults
    };
  }

  runField(fieldDefinition={}, registry={}, options={}) {
    const service = this.verificationService ?? new DefinitionVerificationService({ registry });
    const verification = service.deriveForRunner(fieldDefinition, registry);
    const cases = verification.test_patterns.map(pattern => this.#runPattern(verification.field_contract, pattern));
    const summary = {
      pattern_count: cases.length,
      passed_count: cases.filter(item => item.comparison.status === 'PASS').length,
      failed_count: cases.filter(item => item.comparison.status === 'FAIL').length,
      unresolved_count: cases.filter(item => item.comparison.status === 'UNRESOLVED').length
    };

    return {
      field_path: verification.field_path,
      validation_type_id: verification.validation_type_id,
      status: this.#fieldStatus(verification, summary),
      verification_status: verification.status,
      source: {
        ...definitionVerificationClone(verification.source ?? {}),
        field_definition_sha256: String(options.source_metadata?.field_definition_sha256 ?? ''),
        registry_sha256: String(options.source_metadata?.registry_sha256 ?? '')
      },
      summary,
      issues: definitionVerificationClone(verification.field_contract?.issues ?? []),
      test_cases: cases
    };
  }

  #runPattern(contract, pattern) {
    const expected = definitionVerificationClone(pattern.expected ?? {});
    const actual = this.valueValidator.validate(contract, pattern.input);
    return {
      pattern_id: pattern.pattern_id,
      pattern_key: pattern.pattern_key,
      category: pattern.category,
      input: definitionVerificationClone(pattern.input),
      expected,
      actual,
      comparison: this.#compare(expected, actual),
      source: definitionVerificationClone(pattern.source ?? {})
    };
  }

  #compare(expected, actual) {
    if (expected?.outcome === 'UNRESOLVED') {
      return {
        status: 'UNRESOLVED',
        reason_code: 'EXPECTED_UNRESOLVED'
      };
    }
    if (actual?.outcome === 'UNRESOLVED') {
      return {
        status: 'FAIL',
        reason_code: 'ACTUAL_UNRESOLVED'
      };
    }
    const matched = expected?.outcome === actual?.outcome;
    return {
      status: matched ? 'PASS' : 'FAIL',
      reason_code: matched ? 'OUTCOME_MATCH' : 'OUTCOME_MISMATCH'
    };
  }

  #fieldStatus(verification, summary) {
    if (verification.status === 'INVALID') return 'INVALID';
    if (summary.failed_count > 0) return 'FAILED';
    if (verification.status === 'PARTIAL' || summary.unresolved_count > 0) return 'PARTIAL';
    return 'PASSED';
  }

  #documentStatus(summary) {
    if (summary.invalid_field_count > 0) return 'INVALID';
    if (summary.failed_count > 0) return 'FAILED';
    if (summary.partial_field_count > 0 || summary.unresolved_count > 0) return 'PARTIAL';
    return 'PASSED';
  }

  #runnerMetadata() {
    return {
      id: DEFINITION_TEST_RUNNER_ID,
      version: DEFINITION_TEST_RUNNER_VERSION
    };
  }
}

globalThis.DEFINITION_TEST_RUNNER_RESULT_SCHEMA_VERSION = DEFINITION_TEST_RUNNER_RESULT_SCHEMA_VERSION;
globalThis.DEFINITION_TEST_RUNNER_ID = DEFINITION_TEST_RUNNER_ID;
globalThis.DEFINITION_TEST_RUNNER_VERSION = DEFINITION_TEST_RUNNER_VERSION;
globalThis.DefinitionTestRunnerCore = DefinitionTestRunnerCore;
