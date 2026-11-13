// v0.18.53-cross-field-test-pattern-generation
// UI-independent Cross Field Constraint derivation shared by Preview and Definition Test Runner.

const CROSS_FIELD_VERIFICATION_SCHEMA_VERSION = 'cross_field_verification_result_v0_2';
const CROSS_FIELD_COMPARE_CONSTRAINT_TYPE = 'studio.cross_field.compare';
const CROSS_FIELD_UNSET_POLICIES = ['ACCEPT_IF_EITHER_UNSET', 'REJECT_IF_EITHER_UNSET'];

class CrossFieldVerificationService {
  constructor({
    registry=null,
    fieldContractResolver=null,
    valueValidator=null
  }={}) {
    this.registry = registry;
    this.fieldContractResolver = fieldContractResolver ?? new FieldContractResolver(registry);
    this.valueValidator = valueValidator ?? new DefinitionValueValidator();
  }

  derive(constraint={}, fieldDefinitionDocument={}, registryOverride=null) {
    const registry = registryOverride ?? this.registry;
    const constraintId = String(constraint?.id ?? '').trim();
    const constraintType = String(constraint?.constraint_type ?? '').trim();
    const operator = String(constraint?.operator ?? '').trim().toUpperCase();
    const leftFieldPath = String(constraint?.left_field_path ?? '').trim();
    const rightFieldPath = String(constraint?.right_field_path ?? '').trim();
    const unsetPolicy = String(constraint?.unset_policy ?? 'REJECT_IF_EITHER_UNSET').trim().toUpperCase();
    const issues = [];

    if (!constraintId) issues.push(this.#issue('CROSS_FIELD_CONSTRAINT_ID_REQUIRED'));
    if (constraintType !== CROSS_FIELD_COMPARE_CONSTRAINT_TYPE) {
      issues.push(this.#issue(`CROSS_FIELD_CONSTRAINT_TYPE_UNSUPPORTED:${constraintType || 'EMPTY'}`));
    }
    if (!['LT', 'LTE', 'GT', 'GTE', 'EQ', 'NE'].includes(operator)) {
      issues.push(this.#issue(`CROSS_FIELD_OPERATOR_UNSUPPORTED:${operator || 'EMPTY'}`));
    }
    if (!leftFieldPath) issues.push(this.#issue('LEFT_FIELD_PATH_REQUIRED'));
    if (!rightFieldPath) issues.push(this.#issue('RIGHT_FIELD_PATH_REQUIRED'));
    if (!CROSS_FIELD_UNSET_POLICIES.includes(unsetPolicy)) {
      issues.push(this.#issue(`CROSS_FIELD_UNSET_POLICY_UNSUPPORTED:${unsetPolicy || 'EMPTY'}`));
    }
    if (definitionVerificationHasOwn(constraint, 'null_policy') && !definitionVerificationHasOwn(constraint, 'unset_policy')) {
      issues.push(this.#issue('CROSS_FIELD_LEGACY_NULL_POLICY_REQUIRES_MIGRATION'));
    }

    const definitions = Array.isArray(fieldDefinitionDocument?.field_definitions)
      ? fieldDefinitionDocument.field_definitions
      : [];
    const leftFieldDefinition = definitions.find(item => String(item?.field_path ?? '') === leftFieldPath) ?? null;
    const rightFieldDefinition = definitions.find(item => String(item?.field_path ?? '') === rightFieldPath) ?? null;

    if (!leftFieldDefinition) issues.push(this.#issue('LEFT_FIELD_DEFINITION_NOT_FOUND', leftFieldPath));
    if (!rightFieldDefinition) issues.push(this.#issue('RIGHT_FIELD_DEFINITION_NOT_FOUND', rightFieldPath));

    const leftContract = leftFieldDefinition ? this.fieldContractResolver.resolve(leftFieldDefinition, registry) : null;
    const rightContract = rightFieldDefinition ? this.fieldContractResolver.resolve(rightFieldDefinition, registry) : null;

    if (leftContract?.resolution_status === 'INVALID') issues.push(this.#issue('LEFT_FIELD_CONTRACT_INVALID', leftFieldPath));
    if (rightContract?.resolution_status === 'INVALID') issues.push(this.#issue('RIGHT_FIELD_CONTRACT_INVALID', rightFieldPath));

    const comparableFamily = this.#resolveComparableFamily(leftContract, rightContract);
    if (leftContract && rightContract && !comparableFamily) {
      issues.push(this.#issue(
        `CROSS_FIELD_VALUE_FAMILY_INCOMPATIBLE:${leftContract.value_family || 'EMPTY'}:${rightContract.value_family || 'EMPTY'}`
      ));
    }

    let values = null;
    if (issues.length === 0) {
      values = this.#deriveComparableTriplet(comparableFamily, leftContract, rightContract);
      if (!values) issues.push(this.#issue('CROSS_FIELD_COMPARABLE_TRIPLET_NOT_DERIVABLE'));
    }

    const testPatterns = values
      ? this.#buildComparePatterns({
          constraintId,
          constraintType,
          operator,
          unsetPolicy,
          leftFieldPath,
          rightFieldPath,
          leftContract,
          rightContract,
          values
        })
      : [];

    if (values && issues.length === 0) {
      testPatterns.push(...this.#buildUnsetPatterns({
        constraintId,
        constraintType,
        operator,
        unsetPolicy,
        leftFieldPath,
        rightFieldPath,
        leftContract,
        rightContract,
        values
      }));
    }

    const status = issues.length > 0
      ? 'INVALID'
      : ((leftContract?.resolution_status === 'PARTIAL' || rightContract?.resolution_status === 'PARTIAL') ? 'PARTIAL' : 'READY');

    return {
      schema_version: CROSS_FIELD_VERIFICATION_SCHEMA_VERSION,
      status,
      constraint_id: constraintId,
      constraint_type: constraintType,
      operator,
      unset_policy: unsetPolicy,
      left_field_path: leftFieldPath,
      right_field_path: rightFieldPath,
      left_contract: definitionVerificationClone(leftContract),
      right_contract: definitionVerificationClone(rightContract),
      representative_values: definitionVerificationClone(values),
      test_patterns: testPatterns,
      issues,
      summary: {
        test_pattern_count: testPatterns.length,
        compare_pattern_count: testPatterns.filter(pattern => pattern.category === 'cross_field_compare').length,
        unset_pattern_count: testPatterns.filter(pattern => pattern.category === 'cross_field_unset').length,
        accept_count: testPatterns.filter(pattern => pattern.expected?.outcome === 'ACCEPT').length,
        reject_count: testPatterns.filter(pattern => pattern.expected?.outcome === 'REJECT').length,
        issue_count: issues.length
      },
      source: {
        constraint_id: constraintId,
        constraint_type: constraintType,
        operator,
        unset_policy: unsetPolicy,
        left_field_path: leftFieldPath,
        right_field_path: rightFieldPath,
        left_validation_type_id: leftContract?.validation_type_id ?? '',
        right_validation_type_id: rightContract?.validation_type_id ?? '',
        registry_version: registry?.registry_version ?? '',
        registry_schema_version: registry?.schema_version ?? '',
        left_validation_type_contract_version: leftContract?.source?.validation_type_contract_version ?? '',
        right_validation_type_contract_version: rightContract?.source?.validation_type_contract_version ?? ''
      }
    };
  }

  deriveForPreview(constraint={}, fieldDefinitionDocument={}, registryOverride=null) {
    return this.derive(constraint, fieldDefinitionDocument, registryOverride);
  }

  deriveForRunner(constraint={}, fieldDefinitionDocument={}, registryOverride=null) {
    return this.derive(constraint, fieldDefinitionDocument, registryOverride);
  }

  #buildComparePatterns({
    constraintId,
    constraintType,
    operator,
    unsetPolicy,
    leftFieldPath,
    rightFieldPath,
    leftContract,
    rightContract,
    values
  }) {
    const shapes = [
      ['left_less_right', values.low, values.high, -1],
      ['left_equal_right', values.equal, values.equal, 0],
      ['left_greater_right', values.high, values.low, 1]
    ];

    return shapes.map(([patternKey, leftValue, rightValue, comparison]) => {
      const accepted = this.#operatorMatches(operator, comparison);
      return {
        pattern_id: `${constraintId}::${patternKey}`,
        pattern_key: patternKey,
        category: 'cross_field_compare',
        input: {
          left: { field_path: leftFieldPath, state: 'VALUE', value: definitionVerificationClone(leftValue) },
          right: { field_path: rightFieldPath, state: 'VALUE', value: definitionVerificationClone(rightValue) }
        },
        expected: {
          outcome: accepted ? 'ACCEPT' : 'REJECT',
          reason_code: accepted ? 'CROSS_FIELD_RELATION_ACCEPTED' : 'CROSS_FIELD_RELATION_REJECTED'
        },
        relation: {
          constraint_type: constraintType,
          operator,
          comparison_shape: comparison < 0 ? 'LT' : (comparison > 0 ? 'GT' : 'EQ'),
          unset_policy: unsetPolicy
        },
        source: this.#patternSource({ constraintId, leftFieldPath, rightFieldPath, leftContract, rightContract })
      };
    });
  }

  #buildUnsetPatterns({
    constraintId,
    constraintType,
    operator,
    unsetPolicy,
    leftFieldPath,
    rightFieldPath,
    leftContract,
    rightContract,
    values
  }) {
    const leftUnset = this.#representativeUnsetInput(leftContract);
    const rightUnset = this.#representativeUnsetInput(rightContract);
    const expectedOutcome = unsetPolicy === 'ACCEPT_IF_EITHER_UNSET' ? 'ACCEPT' : 'REJECT';
    const expectedReason = expectedOutcome === 'ACCEPT'
      ? 'CROSS_FIELD_RELATION_UNSET_ACCEPTED'
      : 'CROSS_FIELD_RELATION_UNSET_REJECTED';
    const patterns = [];
    const create = (patternKey, leftInput, rightInput) => ({
      pattern_id: `${constraintId}::${patternKey}`,
      pattern_key: patternKey,
      category: 'cross_field_unset',
      input: {
        left: { field_path: leftFieldPath, ...definitionVerificationClone(leftInput) },
        right: { field_path: rightFieldPath, ...definitionVerificationClone(rightInput) }
      },
      expected: {
        outcome: expectedOutcome,
        reason_code: expectedReason
      },
      relation: {
        constraint_type: constraintType,
        operator,
        comparison_shape: 'UNSET',
        unset_policy: unsetPolicy
      },
      source: this.#patternSource({ constraintId, leftFieldPath, rightFieldPath, leftContract, rightContract })
    });

    if (leftUnset) {
      patterns.push(create(
        'left_unset',
        leftUnset,
        { state: 'VALUE', value: definitionVerificationClone(values.equal) }
      ));
    }
    if (rightUnset) {
      patterns.push(create(
        'right_unset',
        { state: 'VALUE', value: definitionVerificationClone(values.equal) },
        rightUnset
      ));
    }
    if (leftUnset && rightUnset) {
      patterns.push(create('both_unset', leftUnset, rightUnset));
    }
    return patterns;
  }

  #representativeUnsetInput(contract) {
    const candidates = [
      { state: 'MISSING' },
      { state: 'VALUE', value: null },
      { state: 'VALUE', value: '' }
    ];
    return candidates.find(input => this.valueValidator.validate(contract, input).outcome === 'ACCEPT') ?? null;
  }

  #patternSource({ constraintId, leftFieldPath, rightFieldPath, leftContract, rightContract }) {
    return {
      constraint_id: constraintId,
      left_field_path: leftFieldPath,
      right_field_path: rightFieldPath,
      left_validation_type_id: leftContract?.validation_type_id ?? '',
      right_validation_type_id: rightContract?.validation_type_id ?? '',
      registry_version: leftContract?.source?.registry_version ?? rightContract?.source?.registry_version ?? '',
      left_validation_type_contract_version: leftContract?.source?.validation_type_contract_version ?? '',
      right_validation_type_contract_version: rightContract?.source?.validation_type_contract_version ?? ''
    };
  }

  #operatorMatches(operator, comparison) {
    switch (operator) {
      case 'LT': return comparison < 0;
      case 'LTE': return comparison <= 0;
      case 'GT': return comparison > 0;
      case 'GTE': return comparison >= 0;
      case 'EQ': return comparison === 0;
      case 'NE': return comparison !== 0;
      default: return false;
    }
  }

  #resolveComparableFamily(leftContract, rightContract) {
    const left = String(leftContract?.value_family ?? '');
    const right = String(rightContract?.value_family ?? '');
    if (!left || !right) return '';
    if (left === right && ['string', 'number', 'float', 'integer', 'date', 'datetime', 'instant'].includes(left)) return left;
    const numeric = new Set(['number', 'float', 'integer']);
    if (numeric.has(left) && numeric.has(right)) return 'number';
    const temporal = new Set(['date', 'datetime', 'instant']);
    if (temporal.has(left) && temporal.has(right)) return 'temporal';
    return '';
  }

  #deriveComparableTriplet(family, leftContract, rightContract) {
    const bounded = this.#deriveBoundedInteriorTriplet(family, leftContract, rightContract);
    if (bounded && this.#tripletAccepted(bounded, leftContract, rightContract)) return bounded;

    const candidates = this.#candidateValues(family, leftContract, rightContract)
      .filter((value, index, all) => all.findIndex(candidate => this.#valueKey(candidate) === this.#valueKey(value)) === index)
      .filter(value => this.#valueAccepted(leftContract, value) && this.#valueAccepted(rightContract, value))
      .sort((a, b) => this.#compareComparable(family, a, b));

    if (candidates.length < 2) return null;
    if (candidates.length === 2) {
      return {
        low: definitionVerificationClone(candidates[0]),
        equal: definitionVerificationClone(candidates[0]),
        high: definitionVerificationClone(candidates[1]),
        derivation: 'narrow_range_fallback'
      };
    }

    const last = candidates.length - 1;
    const lowIndex = Math.floor(last / 4);
    const midIndex = Math.floor(last / 2);
    const highIndex = Math.ceil((last * 3) / 4);
    const low = candidates[lowIndex];
    const equal = candidates[midIndex];
    const high = candidates[highIndex];
    if (this.#compareComparable(family, low, high) >= 0) return null;
    return {
      low: definitionVerificationClone(low),
      equal: definitionVerificationClone(equal),
      high: definitionVerificationClone(high),
      derivation: 'interior_candidate_fallback'
    };
  }

  #deriveBoundedInteriorTriplet(family, leftContract, rightContract) {
    const range = this.#commonExplicitRange(family, leftContract, rightContract);
    if (!range) return null;
    const mid = this.#midpointValue(family, range.minimum, range.maximum);
    if (mid === null || mid === undefined) return null;
    const low = this.#midpointValue(family, range.minimum, mid);
    const high = this.#midpointValue(family, mid, range.maximum);
    if (low === null || high === null) return null;
    if (this.#compareComparable(family, low, high) >= 0) return null;
    return {
      low,
      equal: mid,
      high,
      derivation: 'common_range_quartiles',
      common_minimum: definitionVerificationClone(range.minimum),
      common_maximum: definitionVerificationClone(range.maximum)
    };
  }

  #commonExplicitRange(family, leftContract, rightContract) {
    const keys = this.#boundaryKeysForFamily(family, leftContract, rightContract);
    if (!keys) return null;
    const [minimumKey, maximumKey] = keys;
    const minimums = [leftContract, rightContract]
      .map(contract => definitionVerificationBoundaryValue(contract?.resolved_constraints?.[minimumKey]))
      .filter(value => value !== null && value !== undefined);
    const maximums = [leftContract, rightContract]
      .map(contract => definitionVerificationBoundaryValue(contract?.resolved_constraints?.[maximumKey]))
      .filter(value => value !== null && value !== undefined);
    if (minimums.length !== 2 || maximums.length !== 2) return null;

    const minimum = minimums.reduce((current, value) => this.#compareComparable(family, current, value) >= 0 ? current : value);
    const maximum = maximums.reduce((current, value) => this.#compareComparable(family, current, value) <= 0 ? current : value);
    if (this.#compareComparable(family, minimum, maximum) >= 0) return null;
    return { minimum, maximum };
  }

  #boundaryKeysForFamily(family, leftContract, rightContract) {
    if (family === 'number' || family === 'integer' || family === 'float') return ['minimum', 'maximum'];
    if (family === 'date') return ['minimum_date', 'maximum_date'];
    if (family === 'datetime') return ['minimum_datetime', 'maximum_datetime'];
    if (family === 'instant') return ['minimum_instant', 'maximum_instant'];
    if (family === 'temporal') {
      const leftFamily = String(leftContract?.value_family ?? '');
      const rightFamily = String(rightContract?.value_family ?? '');
      if (leftFamily === rightFamily) return this.#boundaryKeysForFamily(leftFamily, leftContract, rightContract);
    }
    return null;
  }

  #midpointValue(family, minimum, maximum) {
    if (family === 'integer') return Math.trunc((Number(minimum) + Number(maximum)) / 2);
    if (family === 'number' || family === 'float') return (Number(minimum) + Number(maximum)) / 2;

    if (family === 'date') {
      const a = Date.parse(`${minimum}T00:00:00Z`);
      const b = Date.parse(`${maximum}T00:00:00Z`);
      if (Number.isNaN(a) || Number.isNaN(b)) return null;
      const dayMs = 24 * 60 * 60 * 1000;
      const days = Math.floor((b - a) / dayMs / 2);
      return new Date(a + days * dayMs).toISOString().slice(0, 10);
    }

    if (family === 'datetime') {
      const a = this.#localDateTimeEpoch(minimum);
      const b = this.#localDateTimeEpoch(maximum);
      if (a === null || b === null) return null;
      const midpoint = a + Math.floor((b - a) / 2);
      const includeSeconds = String(minimum).length >= 19 || String(maximum).length >= 19;
      return new Date(midpoint).toISOString().slice(0, includeSeconds ? 19 : 16);
    }

    if (family === 'instant' || family === 'temporal') {
      const a = Date.parse(String(minimum));
      const b = Date.parse(String(maximum));
      if (Number.isNaN(a) || Number.isNaN(b)) return null;
      return new Date(a + Math.floor((b - a) / 2)).toISOString();
    }

    return null;
  }

  #localDateTimeEpoch(value) {
    const match = /^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2})(?::(\d{2}))?$/.exec(String(value ?? ''));
    if (!match) return null;
    return Date.UTC(
      Number(match[1]), Number(match[2]) - 1, Number(match[3]),
      Number(match[4]), Number(match[5]), Number(match[6] ?? 0)
    );
  }

  #tripletAccepted(values, leftContract, rightContract) {
    const ordered = this.#compareComparable(
      this.#resolveComparableFamily(leftContract, rightContract),
      values.low,
      values.high
    ) < 0;
    if (!ordered) return false;
    return [values.low, values.equal, values.high].every(value =>
      this.#valueAccepted(leftContract, value) && this.#valueAccepted(rightContract, value)
    );
  }

  #candidateValues(family, leftContract, rightContract) {
    const values = [];
    const push = value => { if (value !== null && value !== undefined) values.push(value); };
    push(definitionVerificationSampleValue(leftContract?.value_family, leftContract?.value_contract, leftContract?.resolved_constraints));
    push(definitionVerificationSampleValue(rightContract?.value_family, rightContract?.value_contract, rightContract?.resolved_constraints));

    if (family === 'number' || family === 'integer' || family === 'float') {
      [-1000, -100, -10, -2, -1, 0, 1, 2, 10, 100, 1000, 10000].forEach(push);
      [leftContract, rightContract].forEach(contract => {
        ['minimum', 'maximum'].forEach(key => {
          const value = definitionVerificationBoundaryValue(contract?.resolved_constraints?.[key]);
          if (typeof value === 'number') [value - 2, value - 1, value, value + 1, value + 2].forEach(push);
        });
      });
      return values;
    }

    if (family === 'date') {
      ['2020-01-01', '2024-01-01', '2026-01-01', '2026-01-02', '2026-01-03', '2026-01-15', '2030-01-01', '2090-01-01'].forEach(push);
      [leftContract, rightContract].forEach(contract => {
        ['minimum_date', 'maximum_date'].forEach(key => {
          const value = definitionVerificationBoundaryValue(contract?.resolved_constraints?.[key]);
          if (value != null) [-2, -1, 0, 1, 2].forEach(shift => push(definitionVerificationShiftIsoDate(value, shift)));
        });
      });
      return values;
    }

    if (family === 'datetime') {
      ['2026-01-01T00:00', '2026-01-01T00:01', '2026-01-01T00:02', '2026-01-15T12:34', '2026-01-16T00:00', '2030-01-01T00:00'].forEach(push);
      [leftContract, rightContract].forEach(contract => {
        ['minimum_datetime', 'maximum_datetime'].forEach(key => {
          const value = definitionVerificationBoundaryValue(contract?.resolved_constraints?.[key]);
          if (value != null) [-2, -1, 0, 1, 2].forEach(shift => push(definitionVerificationShiftLocalDateTime(value, shift)));
        });
      });
      return values;
    }

    if (family === 'instant' || family === 'temporal') {
      ['2026-01-01T00:00:00+09:00', '2026-01-01T00:00:01+09:00', '2026-01-01T00:00:02+09:00', '2026-01-15T12:34:56+09:00', '2026-01-16T00:00:00+09:00', '2030-01-01T00:00:00+09:00'].forEach(push);
      [leftContract, rightContract].forEach(contract => {
        ['minimum_instant', 'maximum_instant'].forEach(key => {
          const value = definitionVerificationBoundaryValue(contract?.resolved_constraints?.[key]);
          if (value != null) [-2, -1, 0, 1, 2].forEach(shift => push(definitionVerificationShiftInstant(value, shift)));
        });
      });
      return values;
    }

    if (family === 'string') {
      ['1', '2', '3', 'A', 'B', 'C', 'a', 'b', 'c', 'A1', 'B1', 'C1', 'aa', 'ab', 'ac'].forEach(push);
      return values;
    }

    return values;
  }

  #valueAccepted(contract, value) {
    return this.valueValidator.validate(contract, { state: 'VALUE', value }).outcome === 'ACCEPT';
  }

  #compareComparable(family, left, right) {
    if (family === 'number' || family === 'integer' || family === 'float') {
      return Number(left) - Number(right);
    }
    if (family === 'instant' || family === 'temporal') {
      return Date.parse(String(left)) - Date.parse(String(right));
    }
    const a = String(left);
    const b = String(right);
    return a === b ? 0 : (a < b ? -1 : 1);
  }

  #valueKey(value) {
    return typeof value === 'object' ? JSON.stringify(value) : `${typeof value}:${String(value)}`;
  }

  #issue(code, target='') {
    return { code, target };
  }
}

globalThis.CROSS_FIELD_VERIFICATION_SCHEMA_VERSION = CROSS_FIELD_VERIFICATION_SCHEMA_VERSION;
globalThis.CROSS_FIELD_COMPARE_CONSTRAINT_TYPE = CROSS_FIELD_COMPARE_CONSTRAINT_TYPE;
globalThis.CROSS_FIELD_UNSET_POLICIES = CROSS_FIELD_UNSET_POLICIES;
globalThis.CrossFieldVerificationService = CrossFieldVerificationService;
