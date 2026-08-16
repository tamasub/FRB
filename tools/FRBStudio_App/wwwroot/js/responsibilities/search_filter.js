// v0.18.66-standard-search-filter-operators-phase3
// ResponsibilityDef: search_filter
// Search Criteria と対象データから一致行だけを返す薄い責務Interface。
// DOM入力の読み取りは補助関数へ分離し、判定本体は rows / criteria だけで検証できる形を維持する。
// Phase 3/4: SearchOperatorRegistry v0.1 のactive operator
// contains / not_contains / equals / not_equals / gte / lte / between / blank / not_blank
// をDOM非依存で評価する。date / datetime / instant の比較もここで扱う。

var SearchFilter = (function () {
  const CANONICAL_OPERATOR_IDS = Object.freeze([
    'contains',
    'not_contains',
    'equals',
    'not_equals',
    'gte',
    'lte',
    'between',
    'blank',
    'not_blank'
  ]);

  const NO_VALUE_OPERATORS = new Set(['blank', 'not_blank']);
  const LEGACY_OPERATOR_ALIASES = Object.freeze({
    '>=': 'gte',
    '<=': 'lte',
    '=': 'equals',
    '==': 'equals',
    '!=': 'not_equals',
    '<>': 'not_equals'
  });

  function readByPath(obj, path) {
    if (typeof getByPath === 'function') return getByPath(obj, path);
    if (!path || path === '$') return obj;
    const normalized = String(path).startsWith('$.') ? String(path).slice(2) : String(path);
    return normalized.split('.').reduce((cur, key) => cur == null ? undefined : cur[key], obj);
  }

  function normalizeRawValue(input) {
    if (!input) return '';
    if (input.multiple) {
      return [...(input.selectedOptions ?? [])].map(opt => opt.value).filter(Boolean);
    }
    return input.value;
  }

  function isEmptyCriterionValue(raw) {
    if (Array.isArray(raw)) return raw.length === 0;
    return raw === '' || raw == null;
  }

  function isBlankValue(value) {
    if (value == null) return true;
    if (typeof value === 'string') return value.trim() === '';
    if (Array.isArray(value)) return value.length === 0;
    return false;
  }

  function normalizeOperator(operator, fallback='') {
    const raw = String(operator ?? '').trim();
    if (!raw) return fallback;
    return LEGACY_OPERATOR_ALIASES[raw] ?? raw;
  }

  function operatorFor(field) {
    // Phase 4でSearchCapabilityResolverの標準OperatorをUIへ接続するまでは、
    // 現行単一入力欄との互換を維持するため number の暗黙既定は gte のままにする。
    const configured = field?.search?.operator ?? field?.search?.match;
    return normalizeOperator(configured, field?.type === 'number' ? 'gte' : 'contains');
  }

  function criterionValue(criterion) {
    if (!criterion || typeof criterion !== 'object') return '';
    if (Object.prototype.hasOwnProperty.call(criterion, 'raw')) return criterion.raw;
    if (Object.prototype.hasOwnProperty.call(criterion, 'value')) return criterion.value;
    return '';
  }

  function criterionRange(criterion) {
    const raw = criterionValue(criterion);
    const rawObject = raw && typeof raw === 'object' && !Array.isArray(raw) ? raw : null;
    return {
      from: criterion?.from ?? criterion?.min ?? rawObject?.from ?? rawObject?.min ?? '',
      to: criterion?.to ?? criterion?.max ?? rawObject?.to ?? rawObject?.max ?? ''
    };
  }

  function criterionFamily(criterion) {
    const raw = String(
      criterion?.value_family ??
      criterion?.valueFamily ??
      criterion?.resolved_value_family ??
      criterion?.type ??
      ''
    ).trim().toLowerCase();

    if (['number', 'integer', 'float', 'decimal'].includes(raw)) return 'number';
    if (raw === 'date') return 'date';
    if (raw === 'datetime') return 'datetime';
    if (raw === 'instant') return 'instant';
    if (raw === 'boolean') return 'boolean';
    if (raw === 'select') return 'select';
    return 'string';
  }

  function criterionFromInput(input, fields = []) {
    const fieldName = input?.dataset?.field;
    const field = fields.find(f => f.field === fieldName);
    if (!field) return null;
    return {
      field: field.field,
      type: field.type,
      value_family: input?.dataset?.searchValueFamily || field.type,
      operator: normalizeOperator(input?.dataset?.searchOperator, operatorFor(field)),
      raw: normalizeRawValue(input),
      search_role: input?.dataset?.searchRole || 'value',
      fieldDef: field
    };
  }

  function criterionIsActive(criterion) {
    if (!criterion) return false;
    const op = normalizeOperator(criterion.operator, criterion.type === 'number' ? 'gte' : 'contains');
    if (NO_VALUE_OPERATORS.has(op)) return true;
    if (op === 'between') {
      const range = criterionRange(criterion);
      return !isEmptyCriterionValue(range.from) || !isEmptyCriterionValue(range.to);
    }
    return !isEmptyCriterionValue(criterionValue(criterion));
  }

  function criteriaFromInputs(inputs = [], fields = []) {
    // Phase 4: betweenのFrom/Toは同一Fieldの2入力から1 Criteriaへ集約する。
    // Legacy単一入力は従来どおり1入力=1 Criteriaとして扱う。
    const grouped = new Map();
    for (const input of [...inputs]) {
      const criterion = criterionFromInput(input, fields);
      if (!criterion) continue;
      const role = criterion.search_role || 'value';
      const key = `${criterion.field}::${criterion.operator}`;
      if (role === 'from' || role === 'to') {
        const current = grouped.get(key) ?? {
          field: criterion.field,
          type: criterion.type,
          value_family: criterion.value_family,
          operator: criterion.operator,
          from: '',
          to: '',
          fieldDef: criterion.fieldDef
        };
        current[role] = criterion.raw;
        grouped.set(key, current);
      } else {
        grouped.set(key, criterion);
      }
    }
    return [...grouped.values()].filter(criterionIsActive);
  }

  function toFiniteNumber(value) {
    if (isBlankValue(value)) return null;
    if (typeof value === 'number') return Number.isFinite(value) ? value : null;
    const normalized = String(value).trim().replace(/,/g, '');
    if (!normalized) return null;
    const number = Number(normalized);
    return Number.isFinite(number) ? number : null;
  }

  function validUtcParts(year, month, day, hour=0, minute=0, second=0, millisecond=0) {
    const d = new Date(Date.UTC(year, month - 1, day, hour, minute, second, millisecond));
    return d.getUTCFullYear() === year &&
      d.getUTCMonth() === month - 1 &&
      d.getUTCDate() === day &&
      d.getUTCHours() === hour &&
      d.getUTCMinutes() === minute &&
      d.getUTCSeconds() === second &&
      d.getUTCMilliseconds() === millisecond;
  }

  function parseDateValue(value) {
    const text = String(value ?? '').trim();
    const match = /^(\d{4})-(\d{2})-(\d{2})$/.exec(text);
    if (!match) return null;
    const [, y, m, d] = match;
    const year = Number(y), month = Number(m), day = Number(d);
    if (!validUtcParts(year, month, day)) return null;
    return Date.UTC(year, month - 1, day);
  }

  function parseLocalDateTimeValue(value) {
    const text = String(value ?? '').trim();
    const match = /^(\d{4})-(\d{2})-(\d{2})[T_ ](\d{2}):(\d{2})(?::(\d{2})(?:\.(\d{1,3}))?)?$/.exec(text);
    if (!match) return null;
    const [, y, m, d, hh, mm, ss='0', ms='0'] = match;
    const year = Number(y), month = Number(m), day = Number(d);
    const hour = Number(hh), minute = Number(mm), second = Number(ss);
    const millisecond = Number(String(ms).padEnd(3, '0'));
    if (!validUtcParts(year, month, day, hour, minute, second, millisecond)) return null;
    return Date.UTC(year, month - 1, day, hour, minute, second, millisecond);
  }

  function parseInstantValue(value) {
    const text = String(value ?? '').trim();
    if (!text || !/(Z|[+-]\d{2}:\d{2})$/i.test(text)) return null;
    const timestamp = Date.parse(text);
    return Number.isFinite(timestamp) ? timestamp : null;
  }

  function comparableValue(value, family) {
    if (family === 'number') return toFiniteNumber(value);
    if (family === 'date') return parseDateValue(value);
    if (family === 'datetime') return parseLocalDateTimeValue(value);
    if (family === 'instant') return parseInstantValue(value);
    return null;
  }

  function equalsScalar(actual, expected, family) {
    if (family === 'number' || family === 'date' || family === 'datetime' || family === 'instant') {
      const a = comparableValue(actual, family);
      const b = comparableValue(expected, family);
      return a != null && b != null && a === b;
    }
    if (family === 'boolean') {
      return String(actual ?? '').toLowerCase() === String(expected ?? '').toLowerCase();
    }
    return String(actual ?? '') === String(expected ?? '');
  }

  function matchesArrayCriterion(actual, expectedValues, operator) {
    const actualValues = Array.isArray(actual) ? actual.map(v => String(v)) : [String(actual ?? '')];
    const expected = expectedValues.map(v => String(v));
    const intersects = expected.some(value => actualValues.includes(value));
    if (operator === 'not_equals') return !intersects;
    return intersects;
  }

  function matchesContains(actual, expected) {
    return String(actual ?? '').toLowerCase().includes(String(expected ?? '').toLowerCase());
  }

  function matchesComparable(actual, expected, family, operator) {
    const a = comparableValue(actual, family);
    const b = comparableValue(expected, family);
    if (a == null || b == null) return false;
    if (operator === 'gte') return a >= b;
    if (operator === 'lte') return a <= b;
    return false;
  }

  function matchesBetween(actual, criterion, family) {
    const range = criterionRange(criterion);
    const hasFrom = !isEmptyCriterionValue(range.from);
    const hasTo = !isEmptyCriterionValue(range.to);
    if (!hasFrom && !hasTo) return true;

    const actualValue = comparableValue(actual, family);
    if (actualValue == null) return false;

    if (hasFrom) {
      const fromValue = comparableValue(range.from, family);
      if (fromValue == null || actualValue < fromValue) return false;
    }
    if (hasTo) {
      const toValue = comparableValue(range.to, family);
      if (toValue == null || actualValue > toValue) return false;
    }
    return true;
  }

  function matchesCriterion(row, criterion) {
    if (!criterion) return true;

    const family = criterionFamily(criterion);
    const op = normalizeOperator(criterion.operator, family === 'number' ? 'gte' : 'contains');
    if (!criterionIsActive({ ...criterion, operator: op })) return true;

    const val = readByPath(row, criterion.field);
    const raw = criterionValue(criterion);

    if (op === 'blank') return isBlankValue(val);
    if (op === 'not_blank') return !isBlankValue(val);

    if (op === 'between') {
      if (!['number', 'date', 'datetime', 'instant'].includes(family)) return false;
      return matchesBetween(val, criterion, family);
    }

    if (Array.isArray(raw)) {
      return matchesArrayCriterion(val, raw, op);
    }

    if (op === 'contains') return matchesContains(val, raw);
    if (op === 'not_contains') return !matchesContains(val, raw);
    if (op === 'equals') return equalsScalar(val, raw, family);
    if (op === 'not_equals') return !equalsScalar(val, raw, family);
    if (op === 'gte' || op === 'lte') {
      if (!['number', 'date', 'datetime', 'instant'].includes(family)) return false;
      return matchesComparable(val, raw, family, op);
    }

    // Resolver / Registryで検証済みCriteriaを前提とし、未知Operatorを別演算へ黙ってfallbackしない。
    return false;
  }

  function matchesRow(row, criteria = []) {
    return criteria.every(criterion => matchesCriterion(row, criterion));
  }

  function collectStringValues(value, output = [], seen = new Set()) {
    if (typeof value === 'string') {
      output.push(value);
      return output;
    }
    if (value == null || typeof value !== 'object') return output;
    if (seen.has(value)) return output;
    seen.add(value);

    if (Array.isArray(value)) {
      for (const item of value) collectStringValues(item, output, seen);
      return output;
    }

    for (const child of Object.values(value)) collectStringValues(child, output, seen);
    return output;
  }

  function buildFullText(row) {
    return collectStringValues(row).join('\n').toLowerCase();
  }

  function matchesFullText(row, rawQuery) {
    const query = String(rawQuery ?? '').trim().toLowerCase();
    if (!query) return true;
    return buildFullText(row).includes(query);
  }

  function normalizeRows(rows = []) {
    return rows.map((item, index) => {
      if (item && typeof item === 'object' && 'row' in item && 'index' in item) return item;
      return { row: item, index };
    });
  }

  function apply(rows = [], criteria = [], options = {}) {
    const entries = normalizeRows(rows);
    const effectiveCriteria = Array.isArray(criteria) ? criteria : [];
    const fullText = options.fullText ?? options.full_text ?? '';
    const filtered = entries.filter(({ row }) => (
      matchesRow(row, effectiveCriteria) && matchesFullText(row, fullText)
    ));
    return typeof options.afterFilter === 'function' ? options.afterFilter(filtered) : filtered;
  }

  function supportsOperator(operator) {
    return CANONICAL_OPERATOR_IDS.includes(normalizeOperator(operator));
  }

  return {
    apply,
    criteriaFromInputs,
    criterionFromInput,
    criterionIsActive,
    matchesCriterion,
    matchesRow,
    matchesFullText,
    collectStringValues,
    buildFullText,
    isEmptyCriterionValue,
    isBlankValue,
    normalizeOperator,
    supportsOperator,
    operatorIds: CANONICAL_OPERATOR_IDS,
    parseDateValue,
    parseLocalDateTimeValue,
    parseInstantValue
  };
})();
