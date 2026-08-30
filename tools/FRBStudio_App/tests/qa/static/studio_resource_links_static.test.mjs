import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';

const ROOT = process.cwd();
const readJson = rel => JSON.parse(fs.readFileSync(path.join(ROOT, rel), 'utf8'));
const readText = rel => fs.readFileSync(path.join(ROOT, rel), 'utf8');

test('Common Studio Resource Links Data uses common ViewDef and shallow managed JSON paths', () => {
  const data = readJson('data/json/00_common/studio_resource_links_data_v0_1.json');
  assert.equal(data.view_def, 'common/studio_resource_links_view_def_v0_1.json');
  assert.equal(data.links.length, 8);
  for (const row of data.links) {
    assert.match(row.path, /^data\/json\//);
    assert.match(row.path, /\.json$/);
    assert.equal(row.path.includes('..'), false);
  }
});

test('Common Resource Link ViewDef keeps path editable and declares OpenStudioJson on caption', () => {
  const view = readJson('defs/common/studio_resource_links_view_def_v0_1.json');
  const grid = view.views[0].sections.find(section => section.id === 'links');
  assert.ok(grid);
  const caption = grid.fields.find(field => field.field === 'caption');
  const pathField = grid.fields.find(field => field.field === 'path');
  assert.equal(caption.grid.action.action, 'OpenStudioJson');
  assert.equal(caption.grid.action.sourceField, 'path');
  assert.equal(caption.grid.action.openMode, 'new_studio');
  assert.equal(pathField.edit.readonly, false);
});

test('ViewDef schema declares grid.action as behavior and no new resource field type is needed', () => {
  const schema = readJson('data/json/00_rules/frb_view_def_schema_v0_9.json');
  assert.equal(schema.$defs.gridOptions.properties.action.$ref, '#/$defs/gridFieldActionOptions');
  const action = schema.$defs.gridFieldActionOptions;
  assert.ok(action.properties.sourceField);
  assert.deepEqual(action.properties.openMode.enum, ['new_studio', 'same_studio']);
  assert.ok(action.anyOf.some(item => item.required?.includes('action')));
});

test('Runtime dispatches grid action through ActionRegistry and OpenStudioJson launches another Studio window', () => {
  const grid = readText('wwwroot/js/renderers/grid_detail.js');
  const actions = readText('wwwroot/js/actions/action_registry.js');
  assert.match(grid, /field\?\.grid\?\.action/);
  assert.match(grid, /executeStudioAction\(action\.action/);
  assert.match(grid, /source: 'grid\.field\.action'/);
  assert.match(actions, /registerStudioAction\('OpenStudioJson'/);
  assert.match(actions, /window\.open\(url, '_blank'\)/);
  assert.match(actions, /data\/json\//);
  assert.match(actions, /\.json/);
});

test('ViewDef generation rule records Resource Link as Data string + View behavior', () => {
  const rules = readJson('data/json/00_rules/frb_viewdef_generation_rules_data_v0_1.json');
  const rule = rules.rules.find(item => item.rule_id === 'viewdef_rule_37');
  assert.ok(rule);
  assert.match(rule.body, /新しいField typeを増やさず/);
  assert.match(rule.body, /field\.grid\.action/);
  assert.match(rule.body, /data\/json\/00_common\//);
  assert.match(rule.body, /defs\/common\//);
  assert.equal(rule.approval_decision, '未承認');
});
