// v0.18.21-json-full-text-search
// Minimal smoke tests for ResponsibilityDef first-step interfaces.
// Run from FRBStudio_App root: node tests/responsibilities/responsibility_refactor_first_step_smoke.mjs

import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import assert from 'node:assert/strict';

const root = process.cwd();
const context = { console };
vm.createContext(context);

for (const rel of [
  'wwwroot/js/responsibilities/grid_column_builder.js',
  'wwwroot/js/responsibilities/search_filter.js',
  'wwwroot/js/responsibilities/csv_exporter.js',
  'wwwroot/js/responsibilities/grid_aggregator.js'
]) {
  const code = fs.readFileSync(path.join(root, rel), 'utf8');
  vm.runInContext(code, context, { filename: rel });
}

const { GridColumnBuilder, SearchFilter, CsvExporter, GridAggregator } = context;

const fields = [
  { field: 'id', caption: 'ID', type: 'text', grid: { visible: false } },
  { field: 'title', caption: 'タイトル', type: 'text', grid: { visible: true } },
  { field: 'score', caption: 'Score', type: 'number' }
];

assert.deepEqual(
  Array.from(GridColumnBuilder.build({ fields }).map(f => f.field)),
  ['title', 'score'],
  'grid_column_build should keep fields where grid.visible is not false'
);

const rows = [
  { id: 'a', title: 'Alpha', score: 3, tags: ['x', 'y'] },
  { id: 'b', title: 'Beta', score: 10, tags: ['z'] },
  { id: 'c', title: 'Gamma', score: 7, tags: ['y'] }
];

assert.deepEqual(
  Array.from(SearchFilter.apply(rows, [{ field: 'title', raw: 'a', type: 'text', operator: 'contains' }]).map(x => x.index)),
  [0, 1, 2],
  'search_filter contains should be case-insensitive and preserve source indexes'
);

assert.deepEqual(
  Array.from(SearchFilter.apply(rows, [{ field: 'score', raw: '7', type: 'number', operator: 'gte' }]).map(x => x.row.id)),
  ['b', 'c'],
  'search_filter number gte should match existing search semantics'
);

assert.deepEqual(
  Array.from(SearchFilter.apply(rows, [{ field: 'tags', raw: ['z'], type: 'select' }]).map(x => x.row.id)),
  ['b'],
  'search_filter multi values should match array cells'
);

const nestedRows = [
  { id: 'nested-a', title: 'Parent A', score: 123, detail: { memo: 'Visible parent only' } },
  { id: 'nested-b', title: 'Parent B', detail: { children: [{ memo: 'Needle in child grid' }] } },
  { id: 'nested-c', title: 'Parent C', hiddenKeyNeedle: { count: 123 } }
];

assert.deepEqual(
  Array.from(SearchFilter.apply(nestedRows, [], { fullText: 'needle in child' }).map(x => x.row.id)),
  ['nested-b'],
  'full-text search should recursively match nested string values and keep the parent row'
);

assert.deepEqual(
  Array.from(SearchFilter.apply(nestedRows, [{ field: 'title', raw: 'Parent B', type: 'text', operator: 'equals' }], { fullText: 'needle' }).map(x => x.row.id)),
  ['nested-b'],
  'full-text search should be AND-combined with existing field criteria'
);

assert.deepEqual(
  Array.from(SearchFilter.apply(nestedRows, [], { fullText: '123' }).map(x => x.row.id)),
  [],
  'full-text search should ignore numeric values'
);

assert.deepEqual(
  Array.from(SearchFilter.apply(nestedRows, [], { fullText: 'hiddenKeyNeedle' }).map(x => x.row.id)),
  [],
  'full-text search should ignore object key names'
);

const csvFields = CsvExporter.resolveFields({
  baseFields: fields.filter(f => f.grid?.visible !== false),
  allFields: fields,
  keyFieldName: 'id'
});
assert.deepEqual(Array.from(csvFields.map(f => f.field)), ['id', 'title', 'score'], 'csv_export should inject key field before visible fields');

const csv = CsvExporter.export({
  rows: [{ row: { id: 'a', title: 'A, quote "here"', score: 3 }, index: 0 }],
  fields: csvFields,
  valueForField: ({ row, field }) => row[field.field]
});
assert.equal(csv, 'id,title,score\r\na,"A, quote ""here""",3\r\n', 'csv_export should escape commas and quotes');

const aggregateFields = [
  { field: 'profit', caption: '損益', type: 'number', grid: { aggregate: { operator: 'sum', scope: 'filtered', label: '表示合計' } } },
  { field: 'units', caption: '数量', type: 'number', grid: { aggregate: { operator: 'sum', scope: 'all', label: '全件合計' } } },
  { field: 'memo', caption: 'メモ', type: 'text', grid: { aggregate: { operator: 'sum' } } }
];
const aggregateRows = [
  { profit: 1680, units: 10, memo: 'a' },
  { profit: '-1,534', units: 20, memo: 'b' },
  { profit: '', units: 30, memo: 'c' },
  { profit: Number.POSITIVE_INFINITY, units: 40, memo: 'd' }
];
const aggregateResult = GridAggregator.build({
  fields: aggregateFields,
  currentRows: aggregateRows,
  filteredRows: [
    { row: aggregateRows[0], index: 0 },
    { row: aggregateRows[1], index: 1 },
    { row: aggregateRows[2], index: 2 },
    { row: aggregateRows[3], index: 3 }
  ]
});
assert.equal(aggregateResult.has_aggregates, true, 'grid_aggregate should activate only for declared number fields');
assert.deepEqual(Array.from(aggregateResult.items.map(item => item.field)), ['profit', 'units'], 'grid_aggregate should ignore non-number fields');
assert.equal(aggregateResult.byField.profit.value, 146, 'filtered sum should include negative and comma-formatted numeric values');
assert.equal(aggregateResult.byField.profit.valid_count, 2, 'filtered sum should count finite numeric values');
assert.equal(aggregateResult.byField.profit.ignored_count, 2, 'filtered sum should ignore empty and non-finite values');
assert.equal(aggregateResult.byField.units.value, 100, 'all scope should aggregate currentRows');
assert.equal(GridAggregator.toFiniteNumber('1,234.5'), 1234.5, 'numeric strings with grouping commas should be accepted');
assert.equal(GridAggregator.toFiniteNumber('not-number'), null, 'invalid numeric strings should be ignored');
assert.equal(GridAggregator.build({ fields, currentRows: rows, filteredRows: [] }).has_aggregates, false, 'ViewDefs without aggregate declarations should remain unchanged');

console.log('responsibility_refactor_first_step_smoke: OK');
