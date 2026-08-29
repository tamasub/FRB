import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import test from 'node:test';
import vm from 'node:vm';

const root = process.cwd();
const readText = relative => fs.readFileSync(path.join(root, relative), 'utf8');

test('ViewDef can declare initialSort and incident grid defaults to work_item_id desc', () => {
  const viewDef = JSON.parse(readText('defs/rules/studio_work_incident_view_def_v0_5.json'));
  const grid = viewDef.views.flatMap(view => view.sections ?? []).find(section => section.id === 'work_items');
  assert.deepEqual(grid.initialSort, { field: 'work_item_id', direction: 'desc' });
});

test('gridInitialSortState accepts a valid field/direction and rejects invalid declarations', () => {
  const sandbox = { console, sortState: { field: null, direction: null }, registerFieldControl() {}, registerRenderer() {}, globalThis: null };
  sandbox.globalThis = sandbox;
  vm.createContext(sandbox);
  vm.runInContext(readText('wwwroot/js/renderers/field_controls.js'), sandbox, { filename: 'field_controls.js' });

  const valid = vm.runInContext(`gridInitialSortState({ fields:[{field:'work_item_id',type:'text'}], initialSort:{field:'work_item_id',direction:'desc'} })`, sandbox);
  assert.equal(valid.field, 'work_item_id');
  assert.equal(valid.direction, 'desc');

  const invalidField = vm.runInContext(`gridInitialSortState({ fields:[{field:'title'}], initialSort:{field:'missing',direction:'desc'} })`, sandbox);
  assert.equal(invalidField.field, null);
  assert.equal(invalidField.direction, null);

  const invalidDirection = vm.runInContext(`gridInitialSortState({ fields:[{field:'title'}], initialSort:{field:'title',direction:'sideways'} })`, sandbox);
  assert.equal(invalidDirection.field, null);
  assert.equal(invalidDirection.direction, null);
});

test('runtime applies ViewDef initial sort on document load and section-group activation', () => {
  const loadRuntime = readText('wwwroot/js/runtime/load_runtime.js');
  const navigation = readText('wwwroot/js/ui/section_group_navigation.js');
  assert.match(loadRuntime, /gridInitialSortState/);
  assert.match(navigation, /gridInitialSortState/);
});

test('ViewDef schema explicitly defines initialSort field/direction contract', () => {
  const schema = JSON.parse(readText('data/json/00_rules/frb_view_def_schema_v0_9.json'));
  assert.equal(schema.$defs.section.properties.initialSort.$ref, '#/$defs/gridInitialSort');
  assert.deepEqual(schema.$defs.gridInitialSort.properties.direction.enum, ['asc', 'desc']);
  assert.deepEqual(schema.$defs.gridInitialSort.required, ['field', 'direction']);
});
