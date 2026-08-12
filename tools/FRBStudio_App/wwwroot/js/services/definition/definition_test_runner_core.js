// v0.18.45-definition-test-runner-diff-crossfield-e2e
// Executes Definition-derived single-field and Cross Field TestPatterns without persisting TestPattern as canonical data.

const DEFINITION_TEST_RUNNER_RESULT_SCHEMA_VERSION = 'definition_test_runner_result_v0_2';
const DEFINITION_TEST_RUNNER_ID = 'studio.definition_test_runner.core';
const DEFINITION_TEST_RUNNER_VERSION = '0.2.0';

class DefinitionTestRunnerCore {
  constructor({
    verificationService=null,
    valueValidator=null,
    crossFieldVerificationService=null,
    crossFieldEvaluator=null,
    clock=null
  }={}) {
    this.verificationService = verificationService;
    this.valueValidator = valueValidator ?? new DefinitionValueValidator();
    this.crossFieldVerificationService = crossFieldVerificationService;
    this.crossFieldEvaluator = crossFieldEvaluator ?? new CrossFieldRelationEvaluator({ valueValidator: this.valueValidator });
    this.clock = clock ?? (() => new Date().toISOString());
  }

  runDocument(fieldDefinitionDocument={}, registry={}, options={}) {
    const definitions = Array.isArray(fieldDefinitionDocument?.field_definitions)
      ? fieldDefinitionDocument.field_definitions
      : [];
    const constraints = Array.isArray(fieldDefinitionDocument?.cross_field_constraints)
      ? fieldDefinitionDocument.cross_field_constraints
      : [];
    const sourceMetadata = options.source_metadata ?? {};
    const fieldResults = definitions.map(fieldDefinition => this.runField(fieldDefinition, registry, { source_metadata: sourceMetadata }));
    const crossFieldResults = constraints.map(constraint => this.runCrossFieldConstraint(
      constraint,
      fieldDefinitionDocument,
      registry,
      { source_metadata: sourceMetadata }
    ));

    const fieldTotals = fieldResults.reduce((summary, field) => {
      summary.field_count += 1;
      summary.field_pattern_count += field.summary.pattern_count;
      summary.field_passed_count += field.summary.passed_count;
      summary.field_failed_count += field.summary.failed_count;
      summary.field_unresolved_count += field.summary.unresolved_count;
      if (field.status === 'INVALID') summary.invalid_field_count += 1;
      if (field.status === 'PARTIAL') summary.partial_field_count += 1;
      return summary;
    }, {
      field_count: 0,
      field_pattern_count: 0,
      field_passed_count: 0,
      field_failed_count: 0,
      field_unresolved_count: 0,
      invalid_field_count: 0,
      partial_field_count: 0
    });

    const crossFieldTotals = crossFieldResults.reduce((summary, constraint) => {
      summary.cross_field_constraint_count += 1;
      summary.cross_field_pattern_count += constraint.summary.pattern_count;
      summary.cross_field_passed_count += constraint.summary.passed_count;
      summary.cross_field_failed_count += constraint.summary.failed_count;
      summary.cross_field_unresolved_count += constraint.summary.unresolved_count;
      if (constraint.status === 'INVALID') summary.invalid_cross_field_constraint_count += 1;
      if (constraint.status === 'PARTIAL') summary.partial_cross_field_constraint_count += 1;
      return summary;
    }, {
      cross_field_constraint_count: 0,
      cross_field_pattern_count: 0,
      cross_field_passed_count: 0,
      cross_field_failed_count: 0,
      cross_field_unresolved_count: 0,
      invalid_cross_field_constraint_count: 0,
      partial_cross_field_constraint_count: 0
    });

    const totals = {
      ...fieldTotals,
      ...crossFieldTotals,
      pattern_count: fieldTotals.field_pattern_count + crossFieldTotals.cross_field_pattern_count,
      passed_count: fieldTotals.field_passed_count + crossFieldTotals.cross_field_passed_count,
      failed_count: fieldTotals.field_failed_count + crossFieldTotals.cross_field_failed_count,
      unresolved_count: fieldTotals.field_unresolved_count + crossFieldTotals.cross_field_unresolved_count
    };

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
        verification_schema_version: String(globalThis.DEFINITION_VERIFICATION_SCHEMA_VERSION ?? ''),
        cross_field_verification_schema_version: String(globalThis.CROSS_FIELD_VERIFICATION_SCHEMA_VERSION ?? '')
      },
      summary: totals,
      fields: fieldResults,
      cross_field_constraints: crossFieldResults
    };
  }

  runField(fieldDefinition={}, registry={}, options={}) {
    const service = this.verificationService ?? new DefinitionVerificationService({ registry });
    const verification = service.deriveForRunner(fieldDefinition, registry);
    const cases = verification.test_patterns.map(pattern => this.#runPattern(verification.field_contract, pattern));
    const summary = this.#caseSummary(cases);

    return {
      field_path: verification.field_path,
      validation_type_id: verification.validation_type_id,
      status: this.#fieldStatus(verification, summary),
      verification_status: verification.status,
      // v0.18.46-definition-review-evidence:
      // Freeze the exact definition + derived verification result used by this execution.
      // Diff review must remain explainable even after the current Field Definition changes.
      field_definition_snapshot: definitionVerificationClone(fieldDefinition),
      verification_snapshot: definitionVerificationClone(verification),
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

  runCrossFieldConstraint(constraint={}, fieldDefinitionDocument={}, registry={}, options={}) {
    const service = this.crossFieldVerificationService ?? new CrossFieldVerificationService({
      registry,
      valueValidator: this.valueValidator
    });
    const verification = service.deriveForRunner(constraint, fieldDefinitionDocument, registry);
    const cases = verification.test_patterns.map(pattern => this.#runCrossFieldPattern(verification, pattern));
    const summary = this.#caseSummary(cases);

    return {
      constraint_id: verification.constraint_id,
      constraint_type: verification.constraint_type,
      operator: verification.operator,
      null_policy: verification.null_policy,
      left_field_path: verification.left_field_path,
      right_field_path: verification.right_field_path,
      status: this.#crossFieldStatus(verification, summary),
      verification_status: verification.status,
      source: {
        ...definitionVerificationClone(verification.source ?? {}),
        field_definition_sha256: String(options.source_metadata?.field_definition_sha256 ?? ''),
        registry_sha256: String(options.source_metadata?.registry_sha256 ?? '')
      },
      summary,
      issues: definitionVerificationClone(verification.issues ?? []),
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

  #runCrossFieldPattern(verification, pattern) {
    const expected = definitionVerificationClone(pattern.expected ?? {});
    const actual = this.crossFieldEvaluator.evaluate(verification, pattern);
    return {
      pattern_id: pattern.pattern_id,
      pattern_key: pattern.pattern_key,
      category: pattern.category,
      input: definitionVerificationClone(pattern.input),
      expected,
      actual,
      comparison: this.#compare(expected, actual),
      relation: definitionVerificationClone(pattern.relation ?? {}),
      source: definitionVerificationClone(pattern.source ?? {})
    };
  }

  #caseSummary(cases) {
    return {
      pattern_count: cases.length,
      passed_count: cases.filter(item => item.comparison.status === 'PASS').length,
      failed_count: cases.filter(item => item.comparison.status === 'FAIL').length,
      unresolved_count: cases.filter(item => item.comparison.status === 'UNRESOLVED').length
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

  #crossFieldStatus(verification, summary) {
    if (verification.status === 'INVALID') return 'INVALID';
    if (summary.failed_count > 0) return 'FAILED';
    if (verification.status === 'PARTIAL' || summary.unresolved_count > 0) return 'PARTIAL';
    return 'PASSED';
  }

  #documentStatus(summary) {
    if (summary.invalid_field_count > 0 || summary.invalid_cross_field_constraint_count > 0) return 'INVALID';
    if (summary.failed_count > 0) return 'FAILED';
    if (
      summary.partial_field_count > 0 ||
      summary.partial_cross_field_constraint_count > 0 ||
      summary.unresolved_count > 0
    ) return 'PARTIAL';
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
