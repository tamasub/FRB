import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';

const ROOT = process.cwd();
const readJson = rel => JSON.parse(fs.readFileSync(path.join(ROOT, rel), 'utf8'));
const readText = rel => fs.readFileSync(path.join(ROOT, rel), 'utf8');

test('ViewDef schema separates search initialValue/applyOnLoad from field defaultValue', () => {
  const schema = readJson('data/json/00_rules/frb_view_def_schema_v0_9.json');
  const search = schema.$defs.searchOptions.properties;
  assert.ok(search.initialValue);
  assert.equal(search.applyOnLoad.type, 'boolean');
  assert.ok(schema.$defs.field.properties.defaultValue);
});

test('ViewDef maintenance can edit search initial value and load-time apply flag', () => {
  const maint = readJson('defs/common/view_def_maint_fields_v0_2.json');
  const fields = maint.views[0].sections.find(section => section.id === 'fields').fields;
  assert.ok(fields.find(field => field.field === 'search.initialValue'));
  const apply = fields.find(field => field.field === 'search.applyOnLoad');
  assert.ok(apply);
  assert.equal(apply.type, 'boolean');
});

test('Studio Resource Links starts with artifact_kind=diff and applies it on load', () => {
  const view = readJson('defs/common/studio_resource_links_view_def_v0_1.json');
  const grid = view.views[0].sections.find(section => section.id === 'links');
  const kind = grid.fields.find(field => field.field === 'artifact_kind');
  assert.equal(kind.search.operator, 'equals');
  assert.equal(kind.search.initialValue, 'diff');
  assert.equal(kind.search.applyOnLoad, true);
});

test('ViewDef initial search descriptor reuses Studio Search State shape without hardcoded business fields', () => {
  const source = readText('wwwroot/js/runtime/search_state.js');
  const sandbox = { console, structuredClone, localStorage: { getItem(){return null;}, setItem(){} } };
  sandbox.globalThis = sandbox;
  vm.createContext(sandbox);
  vm.runInContext(source, sandbox, { filename: 'search_state.js' });
  const descriptor = sandbox.viewDefInitialSearchDescriptor({
    fields: [
      { field: 'artifact_kind', search: { visible: true, operator: 'equals', initialValue: 'diff', applyOnLoad: true } },
      { field: 'caption', search: { visible: true } },
    ],
  });
  assert.equal(descriptor.apply_on_load, true);
  assert.equal(descriptor.ui_state.core.artifact_kind, 'diff');
  assert.deepEqual([...descriptor.configured_fields], ['artifact_kind']);
  assert.doesNotMatch(source, /artifact_kind\s*===/);
});

test('Load runtime invokes ViewDef initial search after normal initial rendering and cache keys are advanced', () => {
  const source = readText('wwwroot/js/runtime/load_runtime.js');
  const index = readText('wwwroot/index.html');
  assert.match(source, /applyViewDefInitialSearch\(gridDef\(\), \{ runSearch: true \}\)/);
  assert.match(index, /load_runtime\.js\?v=viewdef-search-initial-018125/);
  assert.match(index, /search_state\.js\?v=viewdef-search-initial-018125/);
});

test('Generation Rule 38 documents Search Initial Value contract', () => {
  const rules = readJson('data/json/00_rules/frb_viewdef_generation_rules_data_v0_1.json');
  const rule = rules.rules.find(item => item.rule_id === 'viewdef_rule_38');
  assert.ok(rule);
  assert.match(rule.body, /search\.initialValue/);
  assert.match(rule.body, /search\.applyOnLoad/);
  assert.match(rule.body, /field\.defaultValue/);
  assert.equal(rule.approval_decision, '未承認');
});
