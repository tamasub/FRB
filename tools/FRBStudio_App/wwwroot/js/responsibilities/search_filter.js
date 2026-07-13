// v0.18.7-responsibility-refactor-first-step
// ResponsibilityDef: search_filter
// 検索条件と対象データから、条件に一致する行だけを返す薄い責務Interface。
// DOM入力の読み取りは補助関数に分離し、判定本体は rows/fields/criteria だけで検証できる形にする。

var SearchFilter = (function () {
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

  function operatorFor(field) {
    return field?.search?.operator ?? field?.search?.match ?? (field?.type === 'number' ? 'gte' : 'contains');
  }

  function criterionFromInput(input, fields = []) {
    const fieldName = input?.dataset?.field;
    const field = fields.find(f => f.field === fieldName);
    if (!field) return null;
    return {
      field: field.field,
      type: field.type,
      operator: operatorFor(field),
      raw: normalizeRawValue(input),
      fieldDef: field
    };
  }

  function criteriaFromInputs(inputs = [], fields = []) {
    return [...inputs]
      .map(input => criterionFromInput(input, fields))
      .filter(Boolean)
      .filter(criterion => !isEmptyCriterionValue(criterion.raw));
  }

  function matchesCriterion(row, criterion) {
    if (!criterion || isEmptyCriterionValue(criterion.raw)) return true;
    const val = readByPath(row, criterion.field);
    const raw = criterion.raw;
    const op = criterion.operator ?? (criterion.type === 'number' ? 'gte' : 'contains');

    if (Array.isArray(raw)) {
      const values = Array.isArray(val) ? val.map(v => String(v)) : [String(val ?? '')];
      return raw.some(x => values.includes(String(x)));
    }

    if (criterion.type === 'number') {
      const n = Number(raw);
      if (op === 'gte') return Number(val) >= n;
      if (op === 'lte') return Number(val) <= n;
      return Number(val) === n;
    }

    if (criterion.type === 'boolean') return String(val) === String(raw);
    if (op === 'equals') return String(val ?? '') === String(raw);
    return String(val ?? '').toLowerCase().includes(String(raw).toLowerCase());
  }

  function matchesRow(row, criteria = []) {
    return criteria.every(criterion => matchesCriterion(row, criterion));
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
    const filtered = entries.filter(({ row }) => matchesRow(row, effectiveCriteria));
    return typeof options.afterFilter === 'function' ? options.afterFilter(filtered) : filtered;
  }

  return {
    apply,
    criteriaFromInputs,
    matchesCriterion,
    matchesRow,
    isEmptyCriterionValue
  };
})();
