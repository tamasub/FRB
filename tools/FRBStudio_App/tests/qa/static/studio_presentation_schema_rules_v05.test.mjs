import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';

const read=(path)=>fs.readFileSync(path,'utf8');
const json=(path)=>JSON.parse(read(path));
const rules=json('data/json/00_rules/frb_viewdef_generation_rules_data_v0_1.json');
const schema=json('data/json/00_rules/frb_view_def_schema_v0_9.json');
const viewdef=json('defs/launch/frb_launch_maintenance_view_def_v0_1.json');

// The new top-level app profile must remain declarative: no domain-specific new runtime branch.
test('Studio standard presentation options remain typed and ViewDef-driven',()=>{
  const p=schema.properties.app.properties.presentation;
  assert.equal(p.additionalProperties,false);
  for(const [key,expected] of Object.entries({
    preset:['standard','compact','launcher'],density:['standard','compact'],
    theme:['light','dark','launch-dark'],shell:['standard','minimal'],
    savePlacement:['sidebar','footer','heading']
  })) assert.deepEqual(p.properties[key].enum,expected);
  for(const item of Object.values(p.properties))assert.ok(item.description?.length>25);
  assert.ok(p.description.includes('実行中'));
});

test('tree captions are a validated part of generic treeOptions',()=>{
 const captions=schema.$defs.treeOptions.properties.captions;
 assert.equal(captions.type,'object');
 assert.equal(captions.additionalProperties,false);
 const tree=viewdef.views.flatMap(v=>v.sections).find(s=>s.tree?.groupRoots).tree;
 for(const [key,value] of Object.entries(tree.captions)){
    assert.equal(captions.properties[key].type,'string',`missing ${key}`);
    assert.ok(value.length);
 }
 const runtime=read('wwwroot/js/runtime/tree_grid.js');
 assert.match(runtime,/c\?\.captions\?\.\[key\]/);
});

test('Generation rules include presentation + tree vocabulary without creating approvals',()=>{
 const r39=rules.rules.find(r=>r.rule_id==='viewdef_rule_39');
 const r40=rules.rules.find(r=>r.rule_id==='viewdef_rule_40');
 assert.ok(r39?.body.includes('app.presentation'));
 assert.ok(r39.body.includes('実行中'));
 assert.ok(r40?.body.includes('tree.captions'));
 assert.equal(r39.approval_decision,'未承認');
 assert.equal(r40.approval_decision,'未承認');
 assert.equal(rules.rule_count,rules.rules.length);
 assert.equal(rules.approved_count,90);
});

test('field-specific search is independent from the always-on full-text search',()=>{
 const r36=rules.rules.find(r=>r.rule_id==='viewdef_rule_36');
 assert.match(r36.body,/全文検索UIの独立契約/);
 assert.match(r36.body,/IME変換/);
 assert.match(read('wwwroot/js/renderers/field_controls.js'),/searchSection\.classList\.remove\('hidden'\)/);
});

test('Native Shell matches the launcher gray title bar only in launch-dark theme',()=>{
 const native=read('NativeShell/NativeShellForm.cs');
 assert.match(native,/Color\.FromArgb\(85, 97, 90\)/);
 assert.match(native,/Color\.FromArgb\(32, 43, 41\)/);
 assert.match(native,/_nativeTitleBarLaunchPalette = dark && string\.Equals\(theme, "launch-dark"/);
 assert.match(native,/SetNativeTitleBarDark\(_nativeTitleBarDark, _nativeTitleBarLaunchPalette\)/);
 assert.match(native,/DwmSetWindowAttribute\(Handle, 35, ref caption/);
});
