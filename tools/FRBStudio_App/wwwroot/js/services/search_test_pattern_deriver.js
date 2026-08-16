// v0.18.69-definition-driven-search-test-phase6
// Resolved Search Capability から代表Search TestPatternを機械導出する。
// TestPattern JSONを正本として手作成せず、Field Definition + Search Capabilityを正本とする。

class SearchTestPatternDeriver {
  derive(fieldDefinition={}, capability={}) {
    const field = String(fieldDefinition?.field ?? fieldDefinition?.field_path ?? '').trim();
    const family = this.#normalizeFamily(capability?.value_family ?? fieldDefinition?.type ?? 'string');
    const operatorIds = Array.isArray(capability?.effective?.operator_ids)
      ? capability.effective.operator_ids.map(String)
      : [];
    const patterns = [];

    if (capability?.resolution_status !== 'RESOLVED') {
      return {
        schema_version: 'search_test_pattern_set_v0_1',
        field,
        value_family: family,
        operator_set_id: String(capability?.effective?.operator_set_id ?? ''),
        status: 'UNRESOLVED',
        issues: this.#clone(capability?.issues ?? []),
        patterns: []
      };
    }

    const add = (operator, patternKey, category, rowValue, criterion, expectedMatched) => {
      if (!operatorIds.includes(operator)) return;
      patterns.push({
        pattern_id: `search::${field}::${patternKey}`,
        pattern_key: patternKey,
        category,
        operator,
        input: {
          row: { [field]: this.#clone(rowValue) },
          criterion: {
            field,
            value_family: family,
            operator,
            ...this.#clone(criterion)
          }
        },
        expected: {
          matched: expectedMatched,
          outcome: expectedMatched ? 'MATCH' : 'NO_MATCH'
        },
        source: {
          field,
          validation_type_id: String(capability?.validation_type_id ?? ''),
          value_family: family,
          operator_set_id: String(capability?.effective?.operator_set_id ?? ''),
          operator
        }
      });
    };

    if (family === 'string') {
      add('contains', 'contains_hit', 'text', 'Alpha Beta', { value: 'beta' }, true);
      add('contains', 'contains_miss', 'text', 'Alpha Beta', { value: 'gamma' }, false);
      add('contains', 'case_insensitive_contains', 'text', 'Alpha Beta', { value: 'ALPHA' }, true);
      add('not_contains', 'not_contains_hit', 'text', 'Alpha Beta', { value: 'gamma' }, true);
      add('not_contains', 'not_contains_excluded', 'text', 'Alpha Beta', { value: 'alpha' }, false);
      add('equals', 'equals', 'text', 'Alpha Beta', { value: 'Alpha Beta' }, true);
      add('not_equals', 'not_equals', 'text', 'Alpha Beta', { value: 'Gamma' }, true);
      add('blank', 'blank', 'blank', '   ', {}, true);
      add('not_blank', 'not_blank', 'blank', 'Alpha Beta', {}, true);
    } else if (family === 'number') {
      add('equals', 'equals', 'numeric', 20, { value: 20 }, true);
      add('not_equals', 'not_equals', 'numeric', 20, { value: 21 }, true);
      add('gte', 'gte_boundary', 'boundary', 20, { value: 20 }, true);
      add('gte', 'gte_below', 'boundary', 19, { value: 20 }, false);
      add('lte', 'lte_boundary', 'boundary', 20, { value: 20 }, true);
      add('lte', 'lte_above', 'boundary', 21, { value: 20 }, false);
      add('between', 'between_inside', 'range', 20, { from: 10, to: 30 }, true);
      add('between', 'between_min', 'range', 10, { from: 10, to: 30 }, true);
      add('between', 'between_max', 'range', 30, { from: 10, to: 30 }, true);
      add('between', 'between_outside', 'range', 31, { from: 10, to: 30 }, false);
      add('between', 'from_only', 'range', 20, { from: 20, to: '' }, true);
      add('between', 'to_only', 'range', 20, { from: '', to: 20 }, true);
      add('blank', 'blank', 'blank', null, {}, true);
      add('not_blank', 'not_blank_zero', 'blank', 0, {}, true);
    } else if (family === 'date') {
      add('equals', 'equals', 'date', '2026-08-16', { value: '2026-08-16' }, true);
      add('not_equals', 'not_equals', 'date', '2026-08-16', { value: '2026-08-17' }, true);
      add('gte', 'gte_boundary', 'boundary', '2026-08-16', { value: '2026-08-16' }, true);
      add('gte', 'gte_below', 'boundary', '2026-08-15', { value: '2026-08-16' }, false);
      add('lte', 'lte_boundary', 'boundary', '2026-08-16', { value: '2026-08-16' }, true);
      add('lte', 'lte_above', 'boundary', '2026-08-17', { value: '2026-08-16' }, false);
      add('between', 'between_inside', 'range', '2026-08-16', { from: '2026-08-01', to: '2026-08-31' }, true);
      add('between', 'between_min', 'range', '2026-08-01', { from: '2026-08-01', to: '2026-08-31' }, true);
      add('between', 'between_max', 'range', '2026-08-31', { from: '2026-08-01', to: '2026-08-31' }, true);
      add('between', 'between_outside', 'range', '2026-09-01', { from: '2026-08-01', to: '2026-08-31' }, false);
      add('between', 'from_only', 'range', '2026-08-16', { from: '2026-08-16', to: '' }, true);
      add('between', 'to_only', 'range', '2026-08-16', { from: '', to: '2026-08-16' }, true);
      add('blank', 'blank', 'blank', '', {}, true);
      add('not_blank', 'not_blank', 'blank', '2026-08-16', {}, true);
      add('equals', 'invalid_date_input', 'invalid_input', '2026-02-30', { value: '2026-02-30' }, false);
    }

    return {
      schema_version: 'search_test_pattern_set_v0_1',
      field,
      value_family: family,
      operator_set_id: String(capability?.effective?.operator_set_id ?? ''),
      status: 'DERIVED',
      issues: [],
      patterns
    };
  }

  #normalizeFamily(value) {
    const raw = String(value ?? '').trim().toLowerCase();
    if (['number', 'integer', 'float', 'decimal'].includes(raw)) return 'number';
    if (raw === 'date') return 'date';
    if (['datetime', 'instant'].includes(raw)) return raw;
    if (raw === 'boolean') return 'boolean';
    if (raw === 'select') return 'select';
    return 'string';
  }

  #clone(value) {
    if (value === undefined) return undefined;
    return JSON.parse(JSON.stringify(value));
  }
}

globalThis.SearchTestPatternDeriver = SearchTestPatternDeriver;
