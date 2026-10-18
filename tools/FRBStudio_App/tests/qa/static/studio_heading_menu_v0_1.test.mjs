import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';

const read=path=>fs.readFileSync(path,'utf8');
const viewdef=JSON.parse(read('defs/launch/frb_launch_maintenance_view_def_v0_1.json'));
const schema=JSON.parse(read('data/json/00_rules/frb_view_def_schema_v0_9.json'));
function loadProfile(search='') {
  const host={location:{search}};
  vm.runInNewContext(read('wwwroot/js/ui/studio_presentation_profile.js'),{window:host,console,URLSearchParams});
  return { host,profile:host.StudioPresentationProfile };
}

test('only ViewDef-declared header menu shows in launcher presentation',()=>{
  const {profile}=loadProfile();
  assert.equal(profile.resolve({app:{presentation:{preset:'launcher'}}}).headingMenuItems,undefined);
  assert.equal(profile.resolve({app:{presentation:{preset:'standard'}}}).headingMenuItems,undefined);
  const actual=profile.resolve(viewdef);
  assert.equal(actual.savePlacement,'heading');
  assert.equal(actual.headingMenuItems.length,1);
  assert.equal(actual.headingMenuItems[0].actionId,'MaintainCurrentViewDef');
  assert.equal(actual.headingMenuItems[0].label,'ViewDefをメンテナンス');
  assert.equal(schema.properties.app.properties.presentation.properties.headingMenu.additionalProperties,false);
});

test('header menu allows multiple ViewDef-specified actions with stable order and hidden skip',()=>{
  const {profile}=loadProfile();
  const cfg=profile.resolve({app:{presentation:{savePlacement:'heading',headingMenu:{items:[
    {id:'a',label:'one',actionId:'Action1'},
    {id:'b',label:'invisible',actionId:'Action2',visible:false},
    {id:'c',label:'three',actionId:'Action3'}
  ]}}}});
  assert.deepEqual([...cfg.headingMenuItems].map(x=>x.id),['a','c']);
  assert.equal(cfg.headingMenuItems[1].label,'three');
});

class El {
  constructor(doc,tag='div') {this.doc=doc;this.tagName=tag;this.children=[];this.listeners={};this.dataset={};this.attrs={};this.hidden=false;this.disabled=false;this.textContent='';this.id='';this.className='';this.parent=null;}
  setAttribute(k,v){this.attrs[k]=String(v);}
  getAttribute(k){return this.attrs[k]||null;}
  append(...items){for(const el of items){if(el.parent)el.parent.children=el.parent.children.filter(x=>x!==el);this.children.push(el);el.parent=this;}}
  prepend(...items){for(const el of [...items].reverse()){if(el.parent)el.parent.children=el.parent.children.filter(x=>x!==el);this.children.unshift(el);el.parent=this;}}
  replaceChildren(...items){for(const old of this.children)old.parent=null;this.children=[];this.append(...items);}
  querySelector(sel){if(sel==='.studio-viewer-dock')return null;return null;}
  querySelectorAll(sel){if(sel==='button[role="menuitem"]:not(:disabled)')return this.children.filter(x=>x.attrs.role==='menuitem'&&!x.disabled);return [];}
  addEventListener(event,fn){(this.listeners[event] ||= []).push(fn);}
  fire(event,extra={}){for(const fn of this.listeners[event]||[])fn({key:'',preventDefault(){},...extra});}
  click(){this.fire('click');}
  focus(){this.doc.activeElement=this;}
  contains(target){return target===this||this.children.some(x=>x.contains(target));}
}
function fakeDoc(){
  const ids=new Map();const doc={listeners:{},activeElement:null,body:{dataset:{}},title:'',createElement:tag=>new El(doc,tag),
    getElementById(id){return ids.get(id)||null;},
    querySelector(sel){return sel==='.json-studio-main-pane'?pane:sel==='.json-studio-workspace'?workspace:sel==='.loader-panel'?loader:null;},
    addEventListener(event,fn){(doc.listeners[event] ||= []).push(fn);}
  };
  const origCreate=doc.createElement;
  doc.createElement=tag=>{const el=origCreate(tag);Object.defineProperty(el,'id',{get(){return this._id;},set(id){this._id=id;if(id)ids.set(id,this);}});return el;};
  const workspace=doc.createElement('div'),pane=doc.createElement('div'),loader=doc.createElement('div'),save=doc.createElement('button'),maintenance=doc.createElement('button');
  save.id='saveBtn';loader.append(save);maintenance.id='maintainViewDefBtn';loader.append(maintenance);
  return {doc,save,maintenance};
}
test('render: one Save followed by one overflow; reuse same elements across applies',()=>{
  const {profile,host}=loadProfile(),{doc,save,maintenance}=fakeDoc();
  host.document=doc;
  let calls=0;maintenance.click=()=>calls++;
  profile.apply(viewdef,doc);
  const actions=doc.getElementById('studioPresentationHeadingActions');
  const trigger=doc.getElementById('studioHeadingMenuButton');
  const wrap=doc.getElementById('studioHeadingMenuWrap');
  const menu=doc.getElementById('studioHeadingMenu');
  assert.deepEqual(actions.children.map(x=>x.id),['saveBtn','studioHeadingMenuWrap']);
  assert.equal(wrap.hidden,false);
  assert.equal(menu.children.length,1);
  trigger.click();
  assert.equal(menu.hidden,false);
  menu.children[0].click();
  assert.equal(calls,1,'must forward via existing guarded maintenance button');
  assert.equal(menu.hidden,true);
  // A disabled canonical action must stay disabled from the new entry point.
  maintenance.disabled=true;
  trigger.click();
  menu.children[0].click();
  assert.equal(calls,1,'disabled maintenance must not bypass existing policy');
  maintenance.disabled=false;
  profile.apply(viewdef,doc);
  assert.deepEqual(actions.children.map(x=>x.id),['saveBtn','studioHeadingMenuWrap']);
  assert.equal(doc.getElementById('saveBtn'),save);
  assert.equal(menu.children.length,1);
  profile.apply({app:{name:'Plain'}},doc);
  assert.equal(wrap.hidden,true);
  assert.equal(doc.getElementById('saveBtn'),save);
});

test('menu close on Escape and click outside; keyboard access for menu items',()=>{
  const {profile,host}=loadProfile(),{doc}=fakeDoc();
  host.document=doc;
  profile.apply(viewdef,doc);
  const trigger=doc.getElementById('studioHeadingMenuButton');
  const menu=doc.getElementById('studioHeadingMenu');
  trigger.fire('keydown',{key:'ArrowDown'});
  assert.equal(menu.hidden,false);
  assert.equal(doc.activeElement,menu.children[0]);
  menu.fire('keydown',{key:'Escape'});
  assert.equal(menu.hidden,true);
  assert.equal(doc.activeElement,trigger);
  trigger.click();
  for(const fn of doc.listeners.pointerdown)fn({target:doc.createElement('div')});
  assert.equal(menu.hidden,true);
});

test('CSS is scoped and HTML caches new presentation assets',()=>{
  const css=read('wwwroot/css/studio-presentation.css');
  const index=read('wwwroot/index.html');
  assert.match(css,/\.studio-heading-menu-item:focus-visible/);
  assert.match(css,/\.studio-heading-menu-wrap\[hidden\]/);
  assert.match(index,/heading=007/);
  assert.equal((index.match(/id="saveBtn"/g)||[]).length,1);
});


test('launcher light session toggles only the palette and not ViewDef, density, or Save',()=>{
  const {profile,host}=loadProfile('?startupJson=1&studioTheme=light');
  const {doc,save}=fakeDoc();
  const sent=[];
  host.document=doc;
  host.chrome={webview:{postMessage:message=>sent.push(message.studio_presentation)}};
  profile.apply(viewdef,doc);
  const menu=doc.getElementById('studioHeadingMenu');
  assert.equal(doc.body.dataset.studioTheme,'launch-light');
  assert.equal(doc.body.dataset.studioDensity,'compact');
  assert.equal(doc.body.dataset.studioShell,'minimal');
  assert.equal(menu.children.length,2);
  assert.equal(menu.children[1].textContent,'☾ ダークモードに切替');
  menu.children[1].click();
  assert.equal(doc.body.dataset.studioTheme,'launch-dark');
  assert.equal(doc.body.dataset.studioDensity,'compact');
  assert.equal(doc.getElementById('saveBtn'),save);
  assert.equal(menu.children[1].textContent,'☀ ライトモードに切替');
  menu.children[1].click();
  assert.equal(doc.body.dataset.studioTheme,'launch-light');
  assert.equal(profile.resolve(viewdef).theme,'launch-dark', 'authored ViewDef must not be changed');
  assert.deepEqual(sent.map(x=>x.theme),['launch-light','launch-dark','launch-light']);
});
