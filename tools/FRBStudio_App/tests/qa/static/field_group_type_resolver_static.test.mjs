// v0.18.14-fieldgroup-type-dynamic-switch-expecteddef-viewdef
// Static resolver test for FieldGroupType expansion.
// Run from FRBStudio_App root:
//   node tests/qa/static/field_group_type_resolver_static.test.mjs

import fs from 'node:fs';
import vm from 'node:vm';
import assert from 'node:assert/strict';

const context = {
  console,
  location: {
    protocol: 'http:',
    hostname: 'localhost',
    href: 'http://localhost:5055/myindex.html'
  },
  document: {
    getElementById() { return null; }
  }
};

context.cloneData = (value) => value == null ? value : JSON.parse(JSON.stringify(value));

vm.createContext(context);

for (const rel of [
  'wwwroot/js/core/state.js',
  'wwwroot/js/core/file_api.js',
  'wwwroot/js/core/field_types.js'
]) {
  vm.runInContext(fs.readFileSync(rel, 'utf8'), context, { filename: rel });
}

context.fetchJson = async function fetchJsonFromWorkspace(url) {
  const match = String(url).match(/^\/api\/(defs|data)\/(.+)$/);
  if (!match) throw new Error(`Unsupported test URL: ${url}`);
  const kind = match[1];
  const name = decodeURIComponent(match[2]);
  const candidates = kind === 'defs'
    ? [`defs/${name}`, `defs/common/${name}`]
    : [`data/json/${name}`];
  const found = candidates.find(candidate => fs.existsSync(candidate));
  if (!found) throw new Error(`Test fixture not found: ${candidates.join(' / ')}`);
  return JSON.parse(fs.readFileSync(found, 'utf8'));
};

const viewDef = JSON.parse(fs.readFileSync(
  'defs/qa/tests/responsibilities/responsibility_expected_test_patterns_view_def_v0_1.json',
  'utf8'
));

const resolved = await context.resolveFieldTypesForViewDef(viewDef);
const fields = resolved.views[0].sections.find(section => section.id === 'test_patterns').fields;
const names = fields.map(field => field.field);

assert.ok(!names.includes('__expected_def_fields'), 'FieldGroup placeholder should not remain after resolver expansion');
assert.ok(names.includes('expected.field_names'), 'RuleExpectedDef/ErrorExpectedDef should expand expected.field_names');
assert.ok(names.includes('expected.row_ids'), 'StateExpectedDef should expand expected.row_ids');
assert.ok(names.includes('expected.value'), 'ScalarExpectedDef should expand expected.value');
assert.ok(names.includes('expected.csv_without_bom'), 'CsvExpectedDef should expand CSV preview field');

const fieldNames = fields.find(field => field.field === 'expected.field_names');
const rowIds = fields.find(field => field.field === 'expected.row_ids');
const csvPreview = fields.find(field => field.field === 'expected.csv_without_bom');
const plainFieldNamesVisibleWhen = JSON.parse(JSON.stringify(fieldNames.visibleWhen));
const plainRowIdsVisibleWhen = JSON.parse(JSON.stringify(rowIds.visibleWhen));
const plainCsvPreviewVisibleWhen = JSON.parse(JSON.stringify(csvPreview.visibleWhen));
assert.deepEqual(plainFieldNamesVisibleWhen, {
  field: 'expected_def_type',
  in: ['RuleExpectedDef', 'ErrorExpectedDef', 'CsvExpectedDef']
});
assert.deepEqual(plainRowIdsVisibleWhen, {
  field: 'expected_def_type',
  equals: 'StateExpectedDef'
});
assert.deepEqual(plainCsvPreviewVisibleWhen, {
  field: 'expected_def_type',
  equals: 'CsvExpectedDef'
});

console.log('field_group_type_resolver_static: OK');
