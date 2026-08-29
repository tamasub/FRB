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
