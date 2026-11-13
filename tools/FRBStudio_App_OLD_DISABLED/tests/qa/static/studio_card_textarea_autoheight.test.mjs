import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import path from 'node:path';
import {fileURLToPath} from 'node:url';

const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../../..');
const source=fs.readFileSync(path.join(root,'wwwroot/js/runtime/subgrid_cards.js'),'utf8');
function harness() {
  const listeners={};
  const textarea={
    tagName:'TEXTAREA',value:'',style:{},dataset:{},isConnected:true,
    classList:{add(){}},events:{},
    addEventListener(name,fn){this.events[name]=fn},
    get scrollHeight(){return this.value.split('\n').length*19+14;}
  };
  const context=vm.createContext({
    window:{addEventListener:(name,fn)=>{listeners[name]=fn;}},
    document:{querySelectorAll:()=>[textarea]},
    requestAnimationFrame:(fn)=>fn()
  });
  vm.runInContext(source,context);
  return {textarea,listeners,context};
}

test('card textarea auto-fits short and medium text, clamps long text to 240px',()=>{
  const {textarea:t,context}=harness();
  t.value='short';
  vm.runInContext('enableStudioCardTextareaAutoHeight',context)(t,{});
  const one=parseInt(t.style.height);
  assert.ok(one>=46&&one<65);
  assert.equal(t.style.overflowY,'hidden');
  t.value=Array(8).fill('one line').join('\n');t.events.input();
  assert.ok(parseInt(t.style.height)>one);
  assert.equal(t.style.overflowY,'hidden');
  t.value=Array(40).fill('another line').join('\n');t.events.input();
  assert.equal(t.style.height,'240px');
  assert.equal(t.style.overflowY,'auto');
  assert.equal(t.style.scrollbarGutter,'stable');
  t.value='short';t.events.input();
  assert.equal(t.style.overflowY,'hidden');
  assert.equal(parseInt(t.style.height),one);
});

test('card auto-height accepts per-column maximum without modifying the data',()=>{
  const {textarea:t,context,listeners}=harness();
  const value=Array(25).fill('%USERPROFILE%\\Documents').join('\n');
  t.value=value;
  vm.runInContext('enableStudioCardTextareaAutoHeight',context)(t,{maxHeight:180});
  assert.equal(t.style.height,'180px');
  assert.equal(t.value,value);
  listeners.resize();
  assert.equal(t.style.height,'180px');
  assert.equal(t.dataset.autoHeightMax,'180');
});

test('only multiline card controls receive dynamic sizing',()=>{
 const src=source;
 assert.match(src,/enableStudioCardTextareaAutoHeight\(control,col\)/);
 assert.match(src,/if \(!input \|\| input\.tagName !== 'TEXTAREA'\) return;/);
 assert.match(src,/input\.addEventListener\('input',fit\)/);
});
