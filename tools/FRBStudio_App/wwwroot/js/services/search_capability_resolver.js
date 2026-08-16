// v0.18.65-standard-search-capability-resolver-phase2
// SearchOperatorRegistry + Validation Type / Field type / ViewDef search override から
// UI非依存の実効Search Capabilityを解決する。

class SearchCapabilityResolver {
  constructor({ searchOperatorRegistry=null, validationTypeRegistry=null }={}) {
    this.searchOperatorRegistry = searchOperatorRegistry;
    this.validationTypeRegistry = validationTypeRegistry;
  }

  resolve(fieldDefinition={}, options={}) {
    const searchRegistry = options.searchOperatorRegistry ?? this.searchOperatorRegistry;
    const validationRegistry = options.validationTypeRegistry ?? this.validationTypeRegistry;
    const resolvedFieldContract = options.resolvedFieldContract ?? null;
    const fieldKey = String(fieldDefinition?.field_path ?? fieldDefinition?.field ?? '').trim();
    const fieldType = String(fieldDefinition?.type ?? 'text').trim() || 'text';
    const validationTypeId = String(
      fieldDefinition?.validation_type ?? resolvedFieldContract?.validation_type_id ?? ''
    ).trim();
    const search = fieldDefinition?.search && typeof fieldDefinition.search === 'object'
      ? fieldDefinition.search
      : {};
    const issues = [];

    if (!searchRegistry || typeof searchRegistry !== 'object') {
      return this.#invalidResult({
        fieldKey, fieldType, validationTypeId, search, issues,
        code: 'SEARCH_OPERATOR_REGISTRY_REQUIRED',
        message: 'SearchOperatorRegistry is required.'
      });
    }

    const activeOperators = this.#activeById(searchRegistry.operators);
    const activeSets = this.#activeById(searchRegistry.operator_sets);
    if (activeOperators.size === 0 || activeSets.size === 0) {
      return this.#invalidResult({
        fieldKey, fieldType, validationTypeId, search, issues,
        code: 'SEARCH_OPERATOR_REGISTRY_EMPTY',
        message: 'SearchOperatorRegistry must contain active operators and operator sets.'
      });
    }

    const familyResolution = this.#resolveValueFamily({
      fieldType,
      validationTypeId,
      resolvedFieldContract,
      validationRegistry,
      issues
    });
    if (familyResolution.invalid) {
      return this.#buildResult({
        searchRegistry, fieldKey, fieldType, validationTypeId, search, issues,
        valueFamily: familyResolution.valueFamily,
        familySource: familyResolution.source,
        derivedSet: null,
        derivedSetSource: '',
        effectiveSet: null,
        effectiveOperatorIds: [],
        effectiveDefaultOperator: '',
        overrides: this.#overrideState(search),
        status: 'INVALID',
        validationRegistry
      });
    }

    const derivedResolution = this.#resolveDerivedSet({
      searchRegistry,
      activeSets,
      fieldType,
      valueFamily: familyResolution.valueFamily,
      issues
    });
    if (!derivedResolution.set) {
      return this.#buildResult({
        searchRegistry, fieldKey, fieldType, validationTypeId, search, issues,
        valueFamily: familyResolution.valueFamily,
        familySource: familyResolution.source,
        derivedSet: null,
        derivedSetSource: derivedResolution.source,
        effectiveSet: null,
        effectiveOperatorIds: [],
        effectiveDefaultOperator: '',
        overrides: this.#overrideState(search),
        status: issues.some(issue => issue.severity === 'ERROR') ? 'INVALID' : 'UNSUPPORTED',
        validationRegistry
      });
    }

    const derivedSet = derivedResolution.set;
    let effectiveSet = derivedSet;
    const overrides = this.#overrideState(search);

    if (overrides.operator_set.defined) {
      const overrideSet = activeSets.get(overrides.operator_set.value);
      if (!overrideSet) {
        issues.push(this.#issue('ERROR', 'SEARCH_OPERATOR_SET_NOT_FOUND', `Active Search Operator Set not found: ${overrides.operator_set.value}`));
      } else if (!this.#isSetCompatible(overrideSet, familyResolution.valueFamily, fieldType)) {
        issues.push(this.#issue('ERROR', 'SEARCH_OPERATOR_SET_INCOMPATIBLE', `Search Operator Set is incompatible with field: ${overrides.operator_set.value}`));
      } else {
        effectiveSet = overrideSet;
        overrides.operator_set.applied = true;
      }
    }

    let effectiveOperatorIds = Array.isArray(effectiveSet?.operator_ids)
      ? [...effectiveSet.operator_ids]
      : [];
    this.#validateSetOperators(effectiveSet, effectiveOperatorIds, activeOperators, familyResolution.valueFamily, fieldType, issues);

    if (overrides.operators.defined) {
      const requested = overrides.operators.value;
      if (!Array.isArray(requested) || requested.length === 0) {
        issues.push(this.#issue('ERROR', 'SEARCH_OPERATORS_OVERRIDE_EMPTY', 'search.operators must contain at least one Operator ID when defined.'));
      } else if (new Set(requested).size !== requested.length) {
        issues.push(this.#issue('ERROR', 'SEARCH_OPERATORS_OVERRIDE_DUPLICATE', 'search.operators must not contain duplicate Operator IDs.'));
      } else {
        const baseSetIds = new Set(effectiveOperatorIds);
        let valid = true;
        for (const operatorId of requested) {
          const operator = activeOperators.get(operatorId);
          if (!operator) {
            issues.push(this.#issue('ERROR', 'SEARCH_OPERATOR_NOT_FOUND', `Active Search Operator not found: ${operatorId}`, operatorId));
            valid = false;
            continue;
          }
          if (!baseSetIds.has(operatorId)) {
            issues.push(this.#issue('ERROR', 'SEARCH_OPERATORS_OVERRIDE_NOT_NARROWING', `search.operators may only narrow the effective Operator Set: ${operatorId}`, operatorId));
            valid = false;
          }
          if (!this.#isOperatorCompatible(operator, familyResolution.valueFamily, fieldType)) {
            issues.push(this.#issue('ERROR', 'SEARCH_OPERATOR_INCOMPATIBLE', `Search Operator is incompatible with field: ${operatorId}`, operatorId));
            valid = false;
          }
        }
        if (valid) {
          effectiveOperatorIds = [...requested];
          overrides.operators.applied = true;
        }
      }
    }

    let effectiveDefaultOperator = String(effectiveSet?.default_operator ?? '').trim();
    if (overrides.operator.defined) {
      const operatorId = overrides.operator.value;
      if (!activeOperators.has(operatorId)) {
        issues.push(this.#issue('ERROR', 'SEARCH_OPERATOR_NOT_FOUND', `Active Search Operator not found: ${operatorId}`, operatorId));
      } else if (!effectiveOperatorIds.includes(operatorId)) {
        issues.push(this.#issue('ERROR', 'SEARCH_OPERATOR_OUTSIDE_EFFECTIVE_SET', `search.operator must exist in the effective Operator list: ${operatorId}`, operatorId));
      } else if (!this.#isOperatorCompatible(activeOperators.get(operatorId), familyResolution.valueFamily, fieldType)) {
        issues.push(this.#issue('ERROR', 'SEARCH_OPERATOR_INCOMPATIBLE', `Search Operator is incompatible with field: ${operatorId}`, operatorId));
      } else {
        effectiveDefaultOperator = operatorId;
        overrides.operator.applied = true;
      }
    } else if (!effectiveOperatorIds.includes(effectiveDefaultOperator)) {
      issues.push(this.#issue(
        'ERROR',
        'SEARCH_DEFAULT_OPERATOR_REMOVED_BY_OVERRIDE',
        `search.operators removed the Operator Set default (${effectiveDefaultOperator}); search.operator must explicitly select a remaining default.`
      ));
    }

    const status = issues.some(issue => issue.severity === 'ERROR') ? 'INVALID' : 'RESOLVED';
    return this.#buildResult({
      searchRegistry, fieldKey, fieldType, validationTypeId, search, issues,
      valueFamily: familyResolution.valueFamily,
      familySource: familyResolution.source,
      derivedSet,
      derivedSetSource: derivedResolution.source,
      effectiveSet,
      effectiveOperatorIds,
      effectiveDefaultOperator,
      overrides,
      status,
      activeOperators,
      validationRegistry
    });
  }

  #resolveValueFamily({ fieldType, validationTypeId, resolvedFieldContract, validationRegistry, issues }) {
    const contractFamily = String(resolvedFieldContract?.value_family ?? '').trim();
    if (contractFamily && resolvedFieldContract?.resolution_status !== 'INVALID') {
      return { valueFamily: contractFamily, source: 'resolved_field_contract', invalid: false };
    }

    if (!validationTypeId) {
      return { valueFamily: '', source: 'field_type_fallback', invalid: false };
    }

    if (!validationRegistry || typeof validationRegistry !== 'object') {
      issues.push(this.#issue('ERROR', 'VALIDATION_TYPE_REGISTRY_REQUIRED', `Validation Type Registry is required to resolve: ${validationTypeId}`));
      return { valueFamily: '', source: 'validation_type_registry', invalid: true };
    }

    const definitions = Array.isArray(validationRegistry.validation_type_definitions)
      ? validationRegistry.validation_type_definitions
      : [];
    const matches = definitions.filter(item => String(item?.id ?? '') === validationTypeId);
    if (matches.length !== 1) {
      const code = matches.length === 0 ? 'VALIDATION_TYPE_NOT_FOUND' : 'VALIDATION_TYPE_NOT_UNIQUE';
      issues.push(this.#issue('ERROR', code, `Validation Type resolution failed: ${validationTypeId}`));
      return { valueFamily: '', source: 'validation_type_registry', invalid: true };
    }

    const family = String(matches[0]?.value_family ?? '').trim();
    if (!family) {
      issues.push(this.#issue('ERROR', 'VALIDATION_VALUE_FAMILY_REQUIRED', `Validation Type has no value_family: ${validationTypeId}`));
      return { valueFamily: '', source: 'validation_type_registry', invalid: true };
    }
    return { valueFamily: family, source: 'validation_type_registry', invalid: false };
  }

  #resolveDerivedSet({ searchRegistry, activeSets, fieldType, valueFamily, issues }) {
    const familyMappings = Array.isArray(searchRegistry.validation_value_family_mappings)
      ? searchRegistry.validation_value_family_mappings
      : [];
    const fieldMappings = Array.isArray(searchRegistry.field_type_fallbacks)
      ? searchRegistry.field_type_fallbacks
      : [];

    let mapping = null;
    let source = '';
    if (valueFamily) {
      mapping = familyMappings.find(item => String(item?.value_family ?? '') === valueFamily) ?? null;
      source = 'validation_value_family';
    }
    if (!mapping) {
      mapping = fieldMappings.find(item => String(item?.field_type ?? '') === fieldType) ?? null;
      source = 'field_type_fallback';
    }
    if (!mapping) {
      issues.push(this.#issue('WARNING', 'SEARCH_OPERATOR_SET_UNSUPPORTED', `No Search Operator Set mapping for value_family=${valueFamily || '(none)'} / field_type=${fieldType}`));
      return { set: null, source };
    }

    const setId = String(mapping?.operator_set_id ?? '').trim();
    const set = activeSets.get(setId) ?? null;
    if (!set) {
      issues.push(this.#issue('ERROR', 'SEARCH_OPERATOR_SET_MAPPING_INVALID', `Mapped Search Operator Set is missing/inactive: ${setId}`));
      return { set: null, source };
    }
    return { set, source };
  }

  #validateSetOperators(set, operatorIds, activeOperators, valueFamily, fieldType, issues) {
    if (!set) return;
    if (!operatorIds.length) {
      issues.push(this.#issue('ERROR', 'SEARCH_OPERATOR_SET_EMPTY', `Search Operator Set has no operators: ${set.id}`));
      return;
    }
    const defaultOperator = String(set.default_operator ?? '').trim();
    if (!operatorIds.includes(defaultOperator)) {
      issues.push(this.#issue('ERROR', 'SEARCH_OPERATOR_SET_DEFAULT_INVALID', `Operator Set default is outside operator_ids: ${set.id}`));
    }
    for (const operatorId of operatorIds) {
      const operator = activeOperators.get(operatorId);
      if (!operator) {
        issues.push(this.#issue('ERROR', 'SEARCH_OPERATOR_SET_REFERENCE_INVALID', `Operator Set references missing/inactive Operator: ${operatorId}`, operatorId));
      } else if (!this.#isOperatorCompatible(operator, valueFamily, fieldType)) {
        issues.push(this.#issue('ERROR', 'SEARCH_OPERATOR_INCOMPATIBLE', `Search Operator is incompatible with field: ${operatorId}`, operatorId));
      }
    }
  }

  #isSetCompatible(set, valueFamily, fieldType) {
    const families = Array.isArray(set?.value_families) ? set.value_families.map(String) : [];
    const fieldTypes = Array.isArray(set?.field_types) ? set.field_types.map(String) : [];
    if (valueFamily) return families.includes(valueFamily);
    return fieldTypes.includes(fieldType);
  }

  #isOperatorCompatible(operator, valueFamily, fieldType) {
    const families = Array.isArray(operator?.supported_value_families)
      ? operator.supported_value_families.map(String)
      : [];
    if (valueFamily) return families.includes(valueFamily);
    if (fieldType === 'select') return families.includes('select');
    return true;
  }

  #overrideState(search) {
    const operatorSet = String(search?.operator_set ?? '').trim();
    const operator = String(search?.operator ?? '').trim();
    const operatorsDefined = Array.isArray(search?.operators);
    return {
      operator_set: { defined: operatorSet !== '', value: operatorSet, applied: false },
      operators: { defined: operatorsDefined, value: operatorsDefined ? [...search.operators] : [], applied: false },
      operator: { defined: operator !== '', value: operator, applied: false }
    };
  }

  #activeById(items) {
    const map = new Map();
    for (const item of Array.isArray(items) ? items : []) {
      const id = String(item?.id ?? '').trim();
      if (id && item?.status === 'active') map.set(id, item);
    }
    return map;
  }

  #issue(severity, code, message, operator='') {
    const issue = { severity, code, message };
    if (operator) issue.operator = operator;
    return issue;
  }

  #invalidResult({ fieldKey, fieldType, validationTypeId, search, issues, code, message }) {
    issues.push(this.#issue('ERROR', code, message));
    return this.#buildResult({
      searchRegistry: null,
      fieldKey,
      fieldType,
      validationTypeId,
      search,
      issues,
      valueFamily: '',
      familySource: '',
      derivedSet: null,
      derivedSetSource: '',
      effectiveSet: null,
      effectiveOperatorIds: [],
      effectiveDefaultOperator: '',
      overrides: this.#overrideState(search),
      status: 'INVALID'
    });
  }

  #buildResult({
    searchRegistry,
    fieldKey,
    fieldType,
    validationTypeId,
    search,
    issues,
    valueFamily,
    familySource,
    derivedSet,
    derivedSetSource='',
    effectiveSet,
    effectiveOperatorIds,
    effectiveDefaultOperator,
    overrides,
    status,
    activeOperators=null,
    validationRegistry=null
  }) {
    const operatorMap = activeOperators ?? this.#activeById(searchRegistry?.operators);
    const availableOperators = effectiveOperatorIds
      .map(id => operatorMap.get(id))
      .filter(Boolean)
      .map(item => this.#clone(item));

    return {
      schema_version: 'resolved_search_capability_v0_1',
      field: fieldKey,
      field_type: fieldType,
      validation_type_id: validationTypeId,
      value_family: valueFamily,
      value_family_source: familySource,
      search_visible: search?.visible === true,
      resolution_status: status,
      derived: {
        operator_set_id: String(derivedSet?.id ?? ''),
        default_operator: String(derivedSet?.default_operator ?? ''),
        source: String(derivedSetSource ?? '')
      },
      effective: {
        operator_set_id: String(effectiveSet?.id ?? ''),
        operator_ids: [...effectiveOperatorIds],
        default_operator: effectiveDefaultOperator,
        operators: availableOperators
      },
      overrides: this.#clone(overrides),
      issues: this.#clone(issues),
      source: {
        search_registry_schema_version: String(searchRegistry?.schema_version ?? ''),
        search_registry_version: String(searchRegistry?.registry_version ?? ''),
        validation_registry_schema_version: String(validationRegistry?.schema_version ?? this.validationTypeRegistry?.schema_version ?? ''),
        validation_registry_version: String(validationRegistry?.registry_version ?? this.validationTypeRegistry?.registry_version ?? '')
      }
    };
  }

  #clone(value) {
    if (value === undefined) return undefined;
    return JSON.parse(JSON.stringify(value));
  }
}

globalThis.SearchCapabilityResolver = SearchCapabilityResolver;
