// v0.18.20-grid-numeric-aggregate-header-row
// ResponsibilityDef: grid_aggregate
// ViewDef field.grid.aggregate 宣言からGrid数値列の派生集計を生成する純粋責務。
// DOM描画・Data保存・CSV出力は担当しない。

var GridAggregator = (function () {
  const SUPPORTED_OPERATORS = new Set(['sum']);
  const SUPPORTED_SCOPES = new Set(['filtered', 'all']);

  function normalizeAggregate(field) {
    const raw = field?.grid?.aggregate;
    if (!raw || typeof raw !== 'object' || Array.isArray(raw)) return null;
    if (String(field?.type ?? '').toLowerCase() !== 'number') return null;

    const operator = String(raw.operator ?? '').trim().toLowerCase();
    if (!SUPPORTED_OPERATORS.has(operator)) return null;

    const requestedScope = String(raw.scope ?? 'filtered').trim().toLowerCase();
    const scope = SUPPORTED_SCOPES.has(requestedScope) ? requestedScope : 'filtered';
    const defaultLabel = scope === 'all' ? '全件合計' : '表示合計';
    const label = String(raw.label ?? defaultLabel).trim() || defaultLabel;

    return { operator, scope, label };
  }

  function getByDotPath(source, path) {
    if (!path) return source;
    return String(path)
      .split('.')
      .filter(Boolean)
      .reduce((current, key) => current == null ? undefined : current[key], source);
  }

  function unwrapRow(item) {
    if (item && typeof item === 'object' && Object.prototype.hasOwnProperty.call(item, 'row')) {
      return item.row;
    }
    return item;
  }

  function sourceRows(scope, currentRows, filteredRows) {
    const source = scope === 'all' ? currentRows : filteredRows;
    return (Array.isArray(source) ? source : []).map(unwrapRow);
  }

  function toFiniteNumber(value) {
    if (typeof value === 'number') return Number.isFinite(value) ? value : null;
    if (typeof value !== 'string') return null;
    const text = value.trim();
    if (!text) return null;
    const parsed = Number(text.replace(/,/g, ''));
    return Number.isFinite(parsed) ? parsed : null;
  }

  function sumField(field, config, rows, getValue) {
    let value = 0;
    let validCount = 0;
    let ignoredCount = 0;

    rows.forEach(row => {
      const rawValue = getValue(row, field.field);
      const numberValue = toFiniteNumber(rawValue);
      if (numberValue == null) {
        ignoredCount += 1;
        return;
      }
      value += numberValue;
      validCount += 1;
    });

    return {
      field: field.field,
      operator: config.operator,
      scope: config.scope,
      label: config.label,
      value,
      source_count: rows.length,
      valid_count: validCount,
      ignored_count: ignoredCount
    };
  }

  function build(options = {}) {
    const fields = Array.isArray(options.fields) ? options.fields : [];
    const currentRows = Array.isArray(options.currentRows) ? options.currentRows : [];
    const filteredRows = Array.isArray(options.filteredRows) ? options.filteredRows : [];
    const getValue = typeof options.getValue === 'function' ? options.getValue : getByDotPath;

    const items = fields.flatMap(field => {
      const config = normalizeAggregate(field);
      if (!config) return [];
      const rows = sourceRows(config.scope, currentRows, filteredRows);
      if (config.operator === 'sum') return [sumField(field, config, rows, getValue)];
      return [];
    });

    const byField = Object.create(null);
    items.forEach(item => { byField[item.field] = item; });
    return { items, byField, has_aggregates: items.length > 0 };
  }

  return {
    build,
    normalizeAggregate,
    toFiniteNumber
  };
})();

