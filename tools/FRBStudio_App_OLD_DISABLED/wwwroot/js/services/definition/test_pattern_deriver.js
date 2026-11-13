// v0.18.42-definition-verification-service
// Derives executable-preview TestPattern candidates from one ResolvedFieldContract.
// Expected outcome is intentionally resolved by ExpectedResolver, not here.

class TestPatternDeriver {
  derive(contract={}) {
    if (!contract || contract.resolution_status === 'INVALID') return [];

    const patterns = [];
    const add = (patternKey, category, input, expectationRule, constraintRef='') => {
      patterns.push({
        pattern_id: `${contract.field_path}::${patternKey}`,
        pattern_key: patternKey,
        category,
        input: definitionVerificationClone(input),
        constraint_ref: constraintRef,
        expectation_rule: definitionVerificationClone(expectationRule),
        source: {
          field_path: contract.field_path,
          validation_type_id: contract.validation_type_id,
          registry_version: contract.source?.registry_version ?? '',
          validation_type_contract_version: contract.source?.validation_type_contract_version ?? ''
        }
      });
    };

    add('required_missing', 'presence', { state: 'MISSING' }, { type: 'required_policy' }, 'required');
    add('null', 'nullability', { state: 'VALUE', value: null }, { type: 'nullable_policy' }, 'nullable');
    add(
      'valid_value',
      'value_contract',
      { state: 'VALUE', value: definitionVerificationSampleValue(contract.value_family, contract.value_contract, contract.resolved_constraints) },
      { type: 'valid_value_contract' }
    );
    add(
      'invalid_format',
      'value_contract',
      { state: 'VALUE', value: definitionVerificationInvalidValue(contract.value_family, contract.value_contract) },
      { type: 'invalid_value_contract' }
    );

    this.#addBoundaryPatterns(contract, patterns, add);
    this.#addLengthPatterns(contract, add);

    return patterns;
  }

  #addBoundaryPatterns(contract, _patterns, add) {
    const keys = [
      ['minimum', 'minimum', 'minimum_minus_1', -1],
      ['maximum', 'maximum', 'maximum_plus_1', 1],
      ['minimum_date', 'minimum_date', 'minimum_date_minus_1_day', -1],
      ['maximum_date', 'maximum_date', 'maximum_date_plus_1_day', 1],
      ['minimum_datetime', 'minimum_datetime', 'minimum_datetime_minus_1_minute', -1],
      ['maximum_datetime', 'maximum_datetime', 'maximum_datetime_plus_1_minute', 1],
      ['minimum_instant', 'minimum_instant', 'minimum_instant_minus_1_second', -1],
      ['maximum_instant', 'maximum_instant', 'maximum_instant_plus_1_second', 1]
    ];

    keys.forEach(([constraintKey, atKey, outsideKey, direction]) => {
      const resolution = contract.constraint_resolutions?.find(item => item.constraint === constraintKey);
      if (!resolution || resolution.status !== 'RESOLVED') return;
      const boundary = resolution.resolved_value;
      const value = definitionVerificationBoundaryValue(boundary);
      add(
        atKey,
        'boundary',
        { state: 'VALUE', value },
        { type: 'boundary_at', constraint: constraintKey, inclusive: definitionVerificationBoundaryInclusive(boundary) },
        constraintKey
      );
      const outside = definitionVerificationShiftBoundary(contract.value_family, value, direction);
      if (outside !== null) {
        add(
          outsideKey,
          'boundary',
          { state: 'VALUE', value: outside },
          { type: 'boundary_outside', constraint: constraintKey },
          constraintKey
        );
      }
    });
  }

  #addLengthPatterns(contract, add) {
    if (contract.value_family !== 'string') return;
    const minimum = contract.constraint_resolutions?.find(item => item.constraint === 'minimum_length');
    if (minimum?.status === 'RESOLVED' && Number.isInteger(minimum.resolved_value) && minimum.resolved_value >= 0) {
      const seed = definitionVerificationStringSeed(contract.value_contract);
      const buildValue = length => seed.repeat(Math.ceil(Math.max(1, length) / seed.length)).slice(0, length);
      add('minimum_length', 'length_boundary', { state: 'VALUE', value: buildValue(minimum.resolved_value) }, { type: 'length_at', constraint: 'minimum_length' }, 'minimum_length');
      if (minimum.resolved_value > 0) {
        add('minimum_length_minus_1', 'length_boundary', { state: 'VALUE', value: buildValue(minimum.resolved_value - 1) }, { type: 'length_outside', constraint: 'minimum_length' }, 'minimum_length');
      }
    }
    const maximum = contract.constraint_resolutions?.find(item => item.constraint === 'maximum_length');
    if (maximum?.status === 'RESOLVED' && Number.isInteger(maximum.resolved_value) && maximum.resolved_value >= 0) {
      const seed = definitionVerificationStringSeed(contract.value_contract);
      const buildValue = length => seed.repeat(Math.ceil(Math.max(1, length) / seed.length)).slice(0, length);
      add('maximum_length', 'length_boundary', { state: 'VALUE', value: buildValue(maximum.resolved_value) }, { type: 'length_at', constraint: 'maximum_length' }, 'maximum_length');
      add('maximum_length_plus_1', 'length_boundary', { state: 'VALUE', value: buildValue(maximum.resolved_value + 1) }, { type: 'length_outside', constraint: 'maximum_length' }, 'maximum_length');
    }
  }
}

globalThis.TestPatternDeriver = TestPatternDeriver;
