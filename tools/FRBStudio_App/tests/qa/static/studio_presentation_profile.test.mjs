import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';

const read = rel => fs.readFileSync(path.join(process.cwd(),rel),'utf8');
const readJson = rel => JSON.parse(read(rel));
function profileApi() {
 const host = {};
 vm.runInNewContext(read('wwwroot/js/ui/studio_presentation_profile.js'), {window:host}, {filename:'studio_presentation_profile.js'});
 return host.StudioPresentationProfile;
}
test('unset presentation keeps Standard behavior and no runtime switch UI', () => {
 const cfg = profileApi().resolve({app:{name:'Plain'}});
 assert.deepEqual(JSON.parse(JSON.stringify(cfg)), {preset:'standard',density:'standard',theme:'light',shell:'standard',savePlacement:'sidebar'});
 assert.doesNotMatch(read('wwwroot/index.html'), /通常表示に戻す/);
});
test('compact density is independent of theme and shell', () => {
 const c = profileApi().resolve({app:{presentation:{preset:'compact',theme:'dark'}}});
 assert.equal(c.density,'compact');assert.equal(c.theme,'dark');assert.equal(c.shell,'standard');
});
test('minimal shell forces canonical footer Save, even if sidebar is explicitly requested', () => {
 const c=profileApi().resolve({app:{presentation:{preset:'launcher',savePlacement:'sidebar'}}});
 assert.equal(c.shell,'minimal');assert.equal(c.savePlacement,'footer');assert.equal(c.theme,'launch-dark');
});
test('invalid profile values fallback without introducing implicit runtime modes', () => {
 const cfg=profileApi().resolve({app:{presentation:{preset:'invalid',theme:'system',shell:'fullscreen'}}});
 assert.equal(cfg.preset,'standard');assert.equal(cfg.theme,'light');assert.equal(cfg.shell,'standard');
});
test('Launch ViewDef declares presentation and tree captions, not specialized operations', () => {
 const viewDef=readJson('defs/launch/frb_launch_maintenance_view_def_v0_1.json');
 const cfg=profileApi().resolve(viewDef);
 assert.equal(cfg.preset,'launcher');
 const tree=viewDef.views.flatMap(v=>v.sections).find(s=>s.tree?.groupRoots).tree;
 assert.equal(tree.captions.rootAdd,'Pageを追加');
 assert.equal(tree.captions.rootEdit,'Pageを編集');
 const grid=read('wwwroot/js/runtime/tree_grid.js');
 const groups=read('wwwroot/js/runtime/tree_groups.js');
 assert.doesNotMatch(grid,/button\('Pageを追加'/);
 assert.doesNotMatch(groups,/title\.textContent=isNew\?'Page/);
});
test('ViewDef presentation schema enum is explicit and extends app only', () => {
 const schema=readJson('data/json/00_rules/frb_view_def_schema_v0_9.json');
 assert.deepEqual(schema.properties.app.properties.presentation.properties.preset.enum,['standard','compact','launcher']);
 assert.equal(schema.properties.app.properties.presentation.additionalProperties,false);
});
test('canonical saveBtn is moved rather than copied or rebound', () => {
 const js=read('wwwroot/js/ui/studio_presentation_profile.js');
 const load=read('wwwroot/js/runtime/load_runtime.js');
 const index=read('wwwroot/index.html');
 assert.match(js,/widgets\.actions\.append\(save\)/);
 assert.match(load,/StudioPresentationProfile\.apply\(defObj\)/);
 assert.equal([...index.matchAll(/id="saveBtn"/g)].length,1);
 assert.ok(index.indexOf('studio_presentation_profile.js')<index.indexOf('js/runtime/load_runtime.js'));
});
test('always-on full-text search independent of optional search form', () => {
 const render=read('wwwroot/js/renderers/field_controls.js');
 const index=read('wwwroot/index.html');
 assert.match(render,/searchSection\.classList\.remove\('hidden'\)/);
 assert.match(render,/form\.classList\.toggle\('hidden', form\.childElementCount === 0\)/);
 assert.match(render,/fullText\.disabled = !activeGrid/);
 assert.match(index,/<section id="searchSection" class="card"/);
 assert.match(read('wwwroot/js/ui/section_group_navigation.js'), /renderByKey\('search'\);\n  if \(gd\)/);
});
