import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';

const ROOT = path.resolve(import.meta.dirname, '../../..');

test('objectArray SubGrid preserves absent keys unless user explicitly edits them', () => {
  const source = fs.readFileSync(path.join(ROOT, 'wwwroot/js/runtime/detail_subgrid_edit.js'), 'utf8');
  assert.match(source, /dataset\.originalPresent/);
  assert.match(source, /dataset\.userEdited/);
  assert.match(source, /originalPresent === 'false'.*userEdited !== 'true'/s);
});

test('filtered_row_indexes is a json field so array values round-trip as arrays', () => {
  const viewDef = JSON.parse(fs.readFileSync(path.join(ROOT, 'defs/qa/tests/responsibilities/responsibility_view_def_v0_2.json'), 'utf8'));
  const fields = viewDef.views.flatMap(view => view.sections ?? []).flatMap(section => section.fields ?? []);
  const patternField = fields.find(field => field.field === 'test_pattern_definitions');
  const column = patternField.edit.subGrid.columns.find(item => item.field === 'filtered_row_indexes');
  assert.equal(column.type, 'json');
  assert.equal(column.control, 'textarea');
});


test('objectArray SubGrid returns untouched canonical values instead of rebuilding them from DOM text', () => {
  const source = fs.readFileSync(path.join(ROOT, 'wwwroot/js/runtime/detail_subgrid_edit.js'), 'utf8');
  assert.match(source, /function cloneSubGridCanonicalValue/);
  assert.match(source, /__studioSubGridOriginalValue/);
  assert.match(source, /originalPresent === 'true'.*userEdited !== 'true'.*__studioSubGridOriginalValue/s);
  assert.match(source, /Array→String.*Object→String.*Number→String.*Boolean→String.*null→""/s);
});

test('SubGrid cell type inference prioritizes actual JSON value type over presentation-oriented ViewDef types', () => {
  const source = fs.readFileSync(path.join(ROOT, 'wwwroot/js/runtime/detail_subgrid_edit.js'), 'utf8');
  const start = source.indexOf('function inferSubGridCellType');
  const end = source.indexOf('function objectArraySubGridColumns', start);
  const block = source.slice(start, end);
  assert.ok(start >= 0 && end > start);
  assert.match(block, /value && typeof value === 'object'.*return 'json'/s);
  assert.match(block, /typeof value === 'boolean'.*return 'boolean'/s);
  assert.match(block, /typeof value === 'number'.*return 'number'/s);
  assert.match(block, /type はデータ契約、control は操作部品/);
});

test('Preview Edit also keeps a runtime composite value on the json path even if ViewDef presentation type is wrong', () => {
  const source = fs.readFileSync(path.join(ROOT, 'wwwroot/js/runtime/detail_subgrid_edit.js'), 'utf8');
  assert.match(source, /resolvedCellType = inferSubGridCellType\(itemRow\?\.\[column\.field\], column\)/);
  assert.match(source, /type: resolvedCellType === 'json' \? 'json'/);
});
