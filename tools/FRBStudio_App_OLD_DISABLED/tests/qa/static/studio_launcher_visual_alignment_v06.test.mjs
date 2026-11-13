import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';

const read = path => fs.readFileSync(path, 'utf8');
const profileSource = read('wwwroot/js/ui/studio_presentation_profile.js');

function mockPage() {
  const all = [];
  class E {
    constructor(tag='div') { this.tagName=tag; this.children=[]; this.parent=null; this.id=''; this.dataset={}; this.attributes={}; this.textContent=''; }
    append(...nodes) {for (const item of nodes) { if (item.parent) item.parent.children=item.parent.children.filter(x=>x!==item); this.children.push(item); item.parent=this; } }
    prepend(item) { if (item.parent) item.parent.children=item.parent.children.filter(x=>x!==item); this.children.unshift(item); item.parent=this; }
    setAttribute(name,value) {this.attributes[name]=value;}
    addEventListener(name,callback) { (this.listeners ||= {})[name]=callback; }
    querySelectorAll() { return []; }
    replaceChildren(...nodes) { for (const item of this.children) item.parent=null; this.children=[]; this.append(...nodes); }
    contains(target) { return target===this || this.children.some(e=>e.contains(target)); }
    focus() {}
    querySelector(selector) { return selector==='.studio-viewer-dock' ? null : null; }
  }
  function make(id) { const e = new E(); e.id=id; all.push(e); return e; }
  const pane=make('pane');const workspace=make('workspace');const loader=make('loader');
  const save=make('saveBtn');loader.append(save);
  const status=make('status');status.textContent='OK';
  const count=make('gridCount');count.textContent='54件';
  const body=new E('body');
  const doc={body,title:'',createElement:t=>{const e=new E(t);all.push(e);return e;},
    getElementById:id=>all.find(e=>e.id===id)||null,
    addEventListener() {},
    querySelector:selector=>({'.json-studio-main-pane':pane,'.json-studio-workspace':workspace,'.loader-panel':loader})[selector]||null};
  return {doc,pane,loader,save,all};
}
function api(){const window={};vm.runInNewContext(profileSource,{window},{filename:'studio_presentation_profile.js'});return window.StudioPresentationProfile;}
test('Launcher schema / ViewDef select Save in the right end of the heading',()=>{
  const view=JSON.parse(read('defs/launch/frb_launch_maintenance_view_def_v0_1.json'));
  const schema=JSON.parse(read('data/json/00_rules/frb_view_def_schema_v0_9.json'));
  assert.equal(view.app.presentation.savePlacement,'heading');
  assert.deepEqual(schema.properties.app.properties.presentation.properties.savePlacement.enum,['sidebar','footer','heading']);
  assert.equal(api().resolve(view).savePlacement,'heading');
  assert.equal(api().resolve({app:{presentation:{preset:'launcher',savePlacement:'footer'}}}).savePlacement,'footer');
});
test('Save is moved, not cloned; repeated apply preserves button and heading title',()=>{
  const {doc,save,loader,all}=mockPage();
  const p=api();
  const launcher={app:{name:'FRB Launch 設定メンテナンス',presentation:{preset:'launcher',savePlacement:'heading'}}};
  p.apply(launcher,doc);
  const headingActions=doc.getElementById('studioPresentationHeadingActions');
  assert.equal(save.parent,headingActions);
  assert.equal(doc.getElementById('studioPresentationTitle').textContent,'FRB Launch 設定メンテナンス');
  assert.equal(doc.body.dataset.studioSavePlacement,'heading');
  assert.equal(headingActions.children.length,2, 'Save and appearance overflow');
  p.apply(launcher,doc);
  assert.equal(headingActions.children.length,2, 'Save and appearance overflow');
  assert.equal(all.filter(e=>e.id==='saveBtn').length,1);
  p.apply({app:{name:'Ordinary Studio'}},doc);
  assert.equal(save.parent,loader);
  assert.equal(doc.getElementById('studioPresentationTitle').textContent,'Ordinary Studio');
  assert.equal(headingActions.children.filter(e=>!e.hidden).length,0, 'ordinary Studio hides the launcher overflow');
});
test('Launcher-only chrome, native outer border and dark root scrollbar',()=>{
 const css=read('wwwroot/css/studio-presentation.css');
 const native=read('NativeShell/NativeShellForm.cs');
 const html=read('wwwroot/index.html');
 assert.match(css,/\.studio-presentation-heading-actions/);
 assert.match(css,/#studioPresentationHeading #saveBtn/);
 assert.match(css,/html:has\(> body\.frb-page-json-object/);
 assert.match(css,/::-webkit-scrollbar-thumb/);
 assert.match(native,/DwmSetWindowAttribute\(Handle, 34, ref border/);
 assert.match(native,/Padding = new Padding\(1\)/);
 assert.match(native,/_nativeTitleBarLaunchPalette/);
 assert.match(html,/studio-presentation-005-launcher-chrome/);
 assert.match(html,/studio-presentation-006-launcher-save-top/);
});
