// v0.18.7-responsibility-refactor-first-step
// ResponsibilityDef: csv_export
// 行・列・値取得関数からCSV文字列を生成する薄い責務Interface。
// ダウンロードやBlob生成は既存UI側に残し、UT可能なCSV生成だけを分離する。

var CsvExporter = (function () {
  function escapeCell(value) {
    const text = String(value ?? '');
    if (/[",\r\n]/.test(text)) return '"' + text.replace(/"/g, '""') + '"';
    return text;
  }

  function headerForField(field) {
    return String(field?.field ?? field?.caption ?? '');
  }

  function normalizeRows(rows = []) {
    return rows.map((item, index) => {
      if (item && typeof item === 'object' && 'row' in item && 'index' in item) return item;
      return { row: item, index };
    });
  }

  function uniqueFields(fields = []) {
    const out = [];
    const seen = new Set();
    fields.forEach(field => {
      if (!field?.field) return;
      const key = String(field.field);
      if (seen.has(key)) return;
      seen.add(key);
      out.push(field);
    });
    return out;
  }

  function resolveFields({ baseFields = [], allFields = [], keyFieldName = '', fallbackField = null } = {}) {
    const out = [];
    const key = String(keyFieldName ?? '').trim();
    if (key && !baseFields.some(f => f?.field === key)) {
      out.push(allFields.find(f => f.field === key) ?? { field: key, caption: key, type: 'text' });
    }
    out.push(...baseFields);
    const unique = uniqueFields(out);
    if (!unique.length && fallbackField) unique.push(fallbackField);
    return unique;
  }

  function exportText({ rows = [], fields = [], valueForField, includeBom = false, lineBreak = '\r\n' } = {}) {
    const rowEntries = normalizeRows(rows);
    const valueGetter = typeof valueForField === 'function'
      ? valueForField
      : ({ row, field }) => row?.[field?.field];

    const header = fields.map(field => escapeCell(headerForField(field))).join(',');
    const body = rowEntries.map(({ row, index }) => {
      return fields.map(field => escapeCell(valueGetter({ row, index, field }))).join(',');
    });
    const csv = [header, ...body].join(lineBreak) + lineBreak;
    return includeBom ? '\ufeff' + csv : csv;
  }

  return {
    escapeCell,
    headerForField,
    resolveFields,
    export: exportText,
    exportText
  };
})();
