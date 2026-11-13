// v0.18.42-definition-verification-service
// UI-independent Composition root shared by future Preview Component and Definition Test Runner.

class DefinitionVerificationService {
  constructor({
    registry=null,
    fieldContractResolver=null,
    testPatternDeriver=null,
    expectedResolver=null
  }={}) {
    this.registry = registry;
    this.fieldContractResolver = fieldContractResolver ?? new FieldContractResolver(registry);
    this.testPatternDeriver = testPatternDeriver ?? new TestPatternDeriver();
    this.expectedResolver = expectedResolver ?? new ExpectedResolver();
  }

  derive(fieldDefinition={}, registryOverride=null) {
    const registry = registryOverride ?? this.registry;
    const fieldContract = this.fieldContractResolver.resolve(fieldDefinition, registry);
    const rawPatterns = this.testPatternDeriver.derive(fieldContract);
    const testPatterns = rawPatterns.map(pattern => ({
      ...definitionVerificationClone(pattern),
      expected: this.expectedResolver.resolve(fieldContract, pattern)
    }));

    const unresolvedExpectedCount = testPatterns.filter(pattern => pattern.expected?.outcome === 'UNRESOLVED').length;
    const status = fieldContract.resolution_status === 'INVALID'
      ? 'INVALID'
      : (fieldContract.resolution_status === 'PARTIAL' || unresolvedExpectedCount > 0 ? 'PARTIAL' : 'READY');

    return {
      schema_version: DEFINITION_VERIFICATION_SCHEMA_VERSION,
      status,
      field_path: fieldContract.field_path,
      validation_type_id: fieldContract.validation_type_id,
      field_contract: fieldContract,
      test_patterns: testPatterns,
      summary: {
        test_pattern_count: testPatterns.length,
        accept_count: testPatterns.filter(pattern => pattern.expected?.outcome === 'ACCEPT').length,
        reject_count: testPatterns.filter(pattern => pattern.expected?.outcome === 'REJECT').length,
        unresolved_expected_count: unresolvedExpectedCount,
        unresolved_constraint_count: fieldContract.unresolved_constraints?.length ?? 0,
        issue_count: fieldContract.issues?.length ?? 0
      },
      source: definitionVerificationClone(fieldContract.source ?? {})
    };
  }

  deriveForPreview(fieldDefinition={}, registryOverride=null) {
    return this.derive(fieldDefinition, registryOverride);
  }

  deriveForRunner(fieldDefinition={}, registryOverride=null) {
    return this.derive(fieldDefinition, registryOverride);
  }
}

globalThis.DefinitionVerificationService = DefinitionVerificationService;
