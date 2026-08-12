// v0.18.42-definition-verification-service
// Resolves a single Field Definition against Validation Type Registry defaults + overrides.

class FieldContractResolver {
  constructor(registry=null) {
    this.registry = registry;
  }

  resolve(fieldDefinition={}, registryOverride=null) {
    const registry = registryOverride ?? this.registry;
    const fieldPath = String(fieldDefinition?.field_path ?? '').trim();
    const validationTypeId = String(fieldDefinition?.validation_type ?? '').trim();
    const issues = [];

    if (!registry || typeof registry !== 'object') {
      return this.#invalidResult(fieldPath, validationTypeId, issues, 'REGISTRY_REQUIRED', 'Validation Type Registry is required.');
    }
    if (!fieldPath) {
      issues.push({ severity: 'ERROR', code: 'FIELD_PATH_REQUIRED', message: 'field_path is required.' });
    }
    if (!validationTypeId) {
      issues.push({ severity: 'ERROR', code: 'VALIDATION_TYPE_REQUIRED', message: 'validation_type is required.' });
    }

    const definitions = Array.isArray(registry.validation_type_definitions)
      ? registry.validation_type_definitions
      : [];
    const matches = definitions.filter(item => item?.id === validationTypeId);
    if (matches.length !== 1) {
      const code = matches.length === 0 ? 'VALIDATION_TYPE_NOT_FOUND' : 'VALIDATION_TYPE_NOT_UNIQUE';
      const message = matches.length === 0
        ? `Validation Type not found: ${validationTypeId}`
        : `Validation Type must be unique: ${validationTypeId}`;
      issues.push({ severity: 'ERROR', code, message });
      return this.#buildResult({ registry, fieldPath, validationTypeId, definition: matches[0] ?? null, resolutions: [], issues });
    }

    const definition = matches[0];
    const defaults = definition.default_constraints ?? {};
    const overrides = fieldDefinition.constraint_overrides ?? {};
    const overridable = new Set(definition.overridable_constraints ?? []);
    const keys = definitionVerificationConstraintKeys(definition);

    Object.keys(overrides).forEach(key => {
      if (!overridable.has(key)) {
        issues.push({
          severity: 'ERROR',
          code: 'CONSTRAINT_OVERRIDE_NOT_ALLOWED',
          constraint: key,
          message: `Constraint override is not allowed for ${validationTypeId}: ${key}`
        });
      }
    });

    const resolutions = keys.map(key => {
      const defaultDefined = definitionVerificationHasOwn(defaults, key);
      const overrideDefined = definitionVerificationHasOwn(overrides, key);
      const defaultValue = defaultDefined ? definitionVerificationClone(defaults[key]) : undefined;
      const overrideValue = overrideDefined ? definitionVerificationClone(overrides[key]) : undefined;
      const requiredByValidationType = (definition.required_constraints ?? []).includes(key);

      if (defaultDefined && overrideDefined && !definitionVerificationIsNarrowerBoundary(key, defaultValue, overrideValue)) {
        issues.push({
          severity: 'ERROR',
          code: 'CONSTRAINT_OVERRIDE_LOOSENS_DEFAULT',
          constraint: key,
          message: `Override must not loosen Validation Type default constraint: ${key}`
        });
      }

      const resolved = overrideDefined || defaultDefined;
      if (!resolved) {
        issues.push({
          severity: requiredByValidationType ? 'ERROR' : 'UNRESOLVED',
          code: requiredByValidationType ? 'REQUIRED_CONSTRAINT_UNRESOLVED' : 'CONSTRAINT_UNRESOLVED',
          constraint: key,
          message: `Registry default and Field Definition override are both undefined: ${key}`
        });
      }

      return {
        constraint: key,
        status: resolved ? 'RESOLVED' : 'UNRESOLVED',
        source: overrideDefined ? 'override' : (defaultDefined ? 'registry_default' : 'unresolved'),
        required_by_validation_type: requiredByValidationType,
        default_defined: defaultDefined,
        default_value: defaultDefined ? defaultValue : null,
        override_defined: overrideDefined,
        override_value: overrideDefined ? overrideValue : null,
        resolved_value: resolved ? definitionVerificationClone(overrideDefined ? overrideValue : defaultValue) : null
      };
    });

    this.#validateResolvedRanges(resolutions, issues);
    return this.#buildResult({ registry, fieldPath, validationTypeId, definition, resolutions, issues });
  }

  #validateResolvedRanges(resolutions, issues) {
    const byKey = Object.fromEntries(resolutions.map(item => [item.constraint, item]));
    const pairs = [
      ['minimum', 'maximum'],
      ['minimum_length', 'maximum_length'],
      ['minimum_date', 'maximum_date'],
      ['minimum_datetime', 'maximum_datetime'],
      ['minimum_instant', 'maximum_instant']
    ];

    pairs.forEach(([minimumKey, maximumKey]) => {
      const minimum = byKey[minimumKey];
      const maximum = byKey[maximumKey];
      if (minimum?.status !== 'RESOLVED' || maximum?.status !== 'RESOLVED') return;

      const minimumValue = definitionVerificationBoundaryValue(minimum.resolved_value);
      const maximumValue = definitionVerificationBoundaryValue(maximum.resolved_value);
      const comparison = definitionVerificationCompareValues(minimumValue, maximumValue);
      const noValueAtEqualBoundary = comparison === 0 && (
        definitionVerificationBoundaryInclusive(minimum.resolved_value) === false ||
        definitionVerificationBoundaryInclusive(maximum.resolved_value) === false
      );
      if (comparison > 0 || noValueAtEqualBoundary) {
        issues.push({
          severity: 'ERROR',
          code: 'CONSTRAINT_RANGE_INVALID',
          constraints: [minimumKey, maximumKey],
          message: `Resolved constraint range is invalid: ${minimumKey} / ${maximumKey}`
        });
      }
    });
  }

  #invalidResult(fieldPath, validationTypeId, issues, code, message) {
    issues.push({ severity: 'ERROR', code, message });
    return {
      schema_version: RESOLVED_FIELD_CONTRACT_SCHEMA_VERSION,
      field_path: fieldPath,
      validation_type_id: validationTypeId,
      resolution_status: 'INVALID',
      value_family: '',
      value_contract: {},
      constraint_resolutions: [],
      resolved_constraints: {},
      unresolved_constraints: [],
      issues,
      source: {}
    };
  }

  #buildResult({ registry, fieldPath, validationTypeId, definition, resolutions, issues }) {
    const hasError = issues.some(issue => issue.severity === 'ERROR');
    const unresolved = resolutions.filter(item => item.status === 'UNRESOLVED').map(item => item.constraint);
    const resolvedConstraints = {};
    resolutions.filter(item => item.status === 'RESOLVED').forEach(item => {
      resolvedConstraints[item.constraint] = definitionVerificationClone(item.resolved_value);
    });

    return {
      schema_version: RESOLVED_FIELD_CONTRACT_SCHEMA_VERSION,
      field_path: fieldPath,
      validation_type_id: validationTypeId,
      resolution_status: hasError ? 'INVALID' : (unresolved.length ? 'PARTIAL' : 'RESOLVED'),
      value_family: String(definition?.value_family ?? ''),
      value_contract: definitionVerificationClone(definition?.value_contract ?? {}),
      constraint_resolutions: resolutions,
      resolved_constraints: resolvedConstraints,
      unresolved_constraints: unresolved,
      issues,
      source: {
        registry_schema_version: String(registry?.schema_version ?? ''),
        registry_version: String(registry?.registry_version ?? ''),
        registry_document_type: String(registry?.document_type ?? ''),
        validation_type_id: validationTypeId,
        validation_type_contract_version: String(definition?.contract_version ?? ''),
        validation_type_status: String(definition?.status ?? '')
      }
    };
  }
}

globalThis.FieldContractResolver = FieldContractResolver;
