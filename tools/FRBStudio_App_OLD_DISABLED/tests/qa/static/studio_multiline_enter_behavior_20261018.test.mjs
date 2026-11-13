// Multiline keyboard contract (2026-10-18):
// Enter = apply; Ctrl/Cmd+Enter = newline; editable subgrid textarea never applies on Ctrl+Enter.
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';

const read = path => fs.readFileSync(path, 'utf8');

function textarea(value='ABC') {
  const listeners = new Map();
  return {
    tagName: 'TEXTAREA', value, selectionStart: value.length, selectionEnd: value.length,
    dataset: {}, style: {},
    addEventListener(type, fn) { listeners.set(type, fn); },
    setRangeText(text, start, end) {
      this.value = this.value.slice(0, start) + text + this.value.slice(end);
      this.selectionStart = this.selectionEnd = start + text.length;
    },
    dispatchEvent(event) { listeners.get(event.type)?.(event); },
    closest() { return null; },
    fire(type, event) { listeners.get(type)?.(event); }
  };
}
function key(key, modifiers={}) {
  return {
    key, ctrlKey:false, metaKey:false, shiftKey:false, altKey:false, keyCode:13,
    defaultPrevented:false, stopped:false, ...modifiers,
    preventDefault() { this.defaultPrevented=true; },
    stopPropagation() { this.stopped=true; },
    stopImmediatePropagation() { this.stopped=true; }
  };
}

test('SubGrid multiline Ctrl/Cmd+Enter inserts exactly one newline without applying Detail', () => {
  const source = read('wwwroot/js/runtime/detail_subgrid_edit.js');
  const block = source.slice(source.indexOf('function createSubGridCellControl'), source.indexOf('function createSubGridActionButton'));
  const input = textarea();
  let applied=0, inputEvents=0;
  const context = {
    document:{createElement(tag){assert.equal(tag,'textarea');return input;}},
    Event:class {constructor(type,options){this.type=type;this.bubbles=options.bubbles;}},
    inferSubGridCellType:()=> 'text', subGridCellText:v=>String(v??''),
    detailSubGridCssSize:()=>'',
    markDetailSubGridDirty:()=>{}, applyDetail:()=>{applied++;}
  };
  vm.createContext(context);
  vm.runInContext(block,context);
  const field={field:'note',type:'text'};
  const result=context.createSubGridCellControl({value:'ABC',column:field,editable:true,field,multilineEditor:true});
  assert.equal(result,input);
  input.addEventListener('input',()=>inputEvents++); // observe edit event
  for (const mod of [{ctrlKey:true},{metaKey:true}]) {
    const e=key('Enter',mod);
    input.fire('keydown',e);
    assert.equal(e.defaultPrevented,true);
    assert.equal(e.stopped,true);
  }
  assert.equal(input.value,'ABC\n\n');
  assert.equal(inputEvents,2);
  assert.equal(applied,0);
});

test('Main Detail Enter applies, Ctrl+Enter inserts newline without applying', () => {
  const handlers=new Map();
  let applied=0;
  const input=textarea('ABC');
  input.matches=selector=>selector.includes('textarea');
  const detail={open:true,contains:node=>node===input};
  const doc={
    addEventListener(type,fn){handlers.set(type,fn);},
    getElementById(id){
      if(id==='detailDialog')return detail;
      if(id==='applyDetailBtn')return {disabled:false,click(){applied++;}};
      return null;
    },
    querySelectorAll(){return []},
    execCommand(){return false}
  };
  const context={document:doc,window:{},Element:class {},Event:class{constructor(type,opts){this.type=type;this.bubbles=opts?.bubbles;}}};
  Object.setPrototypeOf(input,context.Element.prototype);
  vm.createContext(context);
  vm.runInContext(read('wwwroot/js/runtime/studio_keyboard_standard.js'),context);
  const handle=handlers.get('keydown');
  assert.equal(typeof handle,'function');
  const ctrl=Object.assign(key('Enter',{ctrlKey:true}),{target:input});
  handle(ctrl);
  assert.equal(ctrl.defaultPrevented,true);
  assert.equal(input.value,'ABC\n');
  assert.equal(applied,0);
  for (const modifiers of [{metaKey:true}, {shiftKey:true}]) {
    const modified=Object.assign(key('Enter',modifiers),{target:input});
    handle(modified);
    assert.equal(modified.defaultPrevented,true);
    assert.equal(applied,0);
  }
  assert.equal(input.value,'ABC\n\n\n');
  const plain=Object.assign(key('Enter'),{target:input});
  handle(plain);
  assert.equal(plain.defaultPrevented,true);
  assert.equal(applied,1);
});
