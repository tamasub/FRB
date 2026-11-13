// Regression: Launch Page追加 used to modify/duplicate the selected Page.
const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const {randomUUID} = require('node:crypto');
const ROOT = path.resolve(__dirname, '../../..');
const JS = fs.readFileSync(path.join(ROOT, 'wwwroot/js/runtime/tree_groups.js'), 'utf8');
const VIEW = JSON.parse(fs.readFileSync(path.join(ROOT, 'defs/launch/frb_launch_maintenance_view_def_v0_1.json'), 'utf8'));
const TREE = VIEW.views.flatMap(v => v.sections).find(section => section.tree?.groupRoots).tree;

function fixture() {
  const pages = [
    {page_id:'work', title:'My Work', enabled:false, sort_order:10},
    {page_id:'frb', title:'FRB', enabled:true, sort_order:30},
  ];
  const state = {selectedGroup:'work'};
  const dialogs = [];
  let refreshed = 0;
  function node(tag) {
    return {
      tag, children:[], textContent:'', value:'', checked:false, focused:false,
      append(...children) {this.children.push(...children);},
      showModal() {this.open = true;},
      close() {this.open = false;this.onclose?.();},
      remove() {this.removed = true;},
      focus() {this.focused = true;},
      setAttribute() {},
    };
  }
  const context = {
    document: {
      createElement:node, createTextNode:text=>({textContent:text}),
      body:{append:dialog=>dialogs.push(dialog)},
    },
    sourceData:{pages},
    studioTreeReadonly:()=>false,
    studioTreeConfig:()=>TREE,
    studioTreeState:()=>state,
    studioTreeCaption:(key, cfg)=>cfg.captions[key] || key,
    getByPath:(data, p)=>p==='$.pages'?data.pages:undefined,
    crypto:{randomUUID},
    applySearch:()=>refreshed++,
  };
  vm.createContext(context);
  vm.runInContext(JS, context, {filename:'tree_groups.js'});
  function edit(isNew) {
    context.studioTreeEditGroup(isNew);
    const dialog = dialogs.at(-1);
    const [title,input,enabled,ok,cancel] = dialog.children;
    return {dialog,title,input,enabled,ok,cancel};
  }
  return {pages,state,edit,get refreshed(){return refreshed;}};
}

test('Pageを追加 creates a new ID; selected Page stays unchanged',()=>{
  const f = fixture();
  const original = JSON.stringify(f.pages[0]);
  const d = f.edit(true);
  assert.equal(d.title.textContent, 'Pageを追加');
  assert.equal(d.input.value, '');
  assert.equal(d.enabled.children[0].checked, true);
  d.input.value = '新しいPage';
  d.ok.onclick();
  assert.equal(f.pages.length, 3);
  assert.equal(JSON.stringify(f.pages[0]), original);
  assert.equal(f.pages[2].title, '新しいPage');
  assert.match(f.pages[2].page_id, /^[0-9a-f-]{36}$/);
  assert.notEqual(f.pages[2].page_id, 'work');
  assert.equal(f.pages[2].sort_order, 40);
  assert.equal(f.pages[2].enabled, true);
  assert.equal(f.state.selectedGroup, f.pages[2].page_id);
  assert.equal(f.refreshed, 1);
});

test('Pageを編集 updates selected Page without adding a record',()=>{
  const f = fixture();
  const d = f.edit(false);
  assert.equal(d.title.textContent, 'Pageを編集');
  assert.equal(d.input.value, 'My Work');
  assert.equal(d.enabled.children[0].checked, false);
  d.input.value = 'My Work 改';
  d.ok.onclick();
  assert.equal(f.pages.length, 2);
  assert.equal(f.pages[0].page_id, 'work');
  assert.equal(f.pages[0].title, 'My Work 改');
  assert.equal(f.pages[0].enabled, false);
  assert.equal(f.pages[1].title, 'FRB');
});

test('Page追加 cancel or blank name does not modify data',()=>{
  const f = fixture(), before = JSON.stringify(f.pages);
  const d = f.edit(true);
  d.ok.onclick();
  assert.equal(JSON.stringify(f.pages),before);
  assert.equal(d.input.focused,true);
  d.cancel.onclick();
  assert.equal(JSON.stringify(f.pages),before);
  assert.equal(f.refreshed,0);
});
