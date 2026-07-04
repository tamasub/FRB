// v0.18.7-responsibility-refactor-first-step
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
  'wwwroot/js/responsibilities/csv_exporter.js'
]) {
  const code = fs.readFileSync(path.join(root, rel), 'utf8');
  vm.runInContext(code, context, { filename: rel });
}

const { GridColumnBuilder, SearchFilter, CsvExporter } = context;

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

console.log('responsibility_refactor_first_step_smoke: OK');
