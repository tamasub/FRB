// No external packages: policy-level keyboard regression harness.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const source = fs.readFileSync('wwwroot/js/runtime/studio_keyboard_standard.js','utf8');
class El {
  constructor({tagName='INPUT', type='text', selectors=[], dataset={}}={}) { this.tagName=tagName;this.type=type;this.selectors=selectors;this.dataset=dataset;this.isContentEditable=selectors.includes('[contenteditable="true"]');this.value='abc';this.selectionStart=3;this.selectionEnd=3;this.dispatched=[]; }
  matches(s){return this.selectors.some(x=>s.includes(x)) || (this.tagName==='TEXTAREA' && s.includes('textarea')) || (this.tagName==='INPUT' && this.type==='text' && (s.includes('input:not') || s.includes('input,')));}
  closest(s){return this.selectors.some(x=>s.includes(x)) ? this : null;}
  dispatchEvent(e){this.dispatched.push(e.type);}
  setRangeText(t,start,end){this.value=this.value.slice(0,start)+t+this.value.slice(end);this.selectionStart=this.selectionEnd=start+t.length;}
}
const actions=[];
const buttons={
 searchBtn:{disabled:false,click(){actions.push('search');}},
 saveBtn:{disabled:false,click(){actions.push('save');}},
 applyDetailBtn:{disabled:false,click(){actions.push('apply');}}
};
let keyListener;
const detail={open:false,contains(x){return x.editor===true;}};
const search={contains(x){return x.search===true;}};
const fullText={};
const grid={contains(x){return x.grid===true;}};
const doc={getElementById(id){return {detailDialog:detail,searchForm:search,studioFullTextSearchInput:fullText,dataGrid:grid,...buttons}[id];},querySelectorAll(){return [];},addEventListener(type, cb, capture){if(type==='keydown'){assert.equal(capture,true);keyListener=cb;}}};
const ctx={document:doc,Element:El,Event:class{constructor(type){this.type=type}},console,selectedIndex:-1,openDetail(n){actions.push('detail:'+n)},studioTreeConfig:()=>null};
vm.createContext(ctx);vm.runInContext(source,ctx);
function key(target,k,flags={}){const e={target,key:k,isComposing:false,keyCode:0,altKey:false,ctrlKey:false,shiftKey:false,metaKey:false,defaultPrevented:false,preventDefault(){this.defaultPrevented=true},stopImmediatePropagation(){this.stopped=true},...flags};keyListener(e);return e;}
let input=new El();input.search=true;
assert.equal(key(input,'Enter').defaultPrevented,true);assert.equal(actions.pop(),'search');
detail.open=true;
let multi=new El({tagName:'TEXTAREA'});multi.editor=true;
key(multi,'Enter');assert.equal(actions.pop(),'apply');assert.equal(multi.value,'abc');
key(multi,'Enter',{ctrlKey:true});assert.equal(multi.value,'abc\n');assert.equal(actions.length,0);
key(multi,'Enter',{shiftKey:true});assert.equal(multi.value,'abc\n\n');assert.equal(actions.length,0);
assert.equal(key(multi,'Enter',{isComposing:true}).defaultPrevented,false);
let searchMulti=new El({tagName:'TEXTAREA'});searchMulti.search=true;
key(searchMulti,'Enter',{shiftKey:true});assert.equal(searchMulti.value,'abc\n');assert.equal(actions.length,0);
let editor=new El();editor.editor=true;
key(editor,'Enter');assert.equal(actions.pop(),'apply');
assert.equal(key(editor,'s',{ctrlKey:true}).defaultPrevented,true);assert.equal(actions.pop(),'save');
buttons.saveBtn.disabled=true;assert.equal(key(editor,'s',{ctrlKey:true}).defaultPrevented,true);assert.equal(actions.length,0);buttons.saveBtn.disabled=false;
detail.open=false;
let row=new El({tagName:'TR',dataset:{sourceIndex:'4'}});row.grid=true;row.closest=()=>row;row.hasAttribute=()=>false;
key(row,'ArrowRight');assert.equal(actions.pop(),'detail:4');assert.equal(ctx.selectedIndex,4);
key(row,'Enter');assert.equal(actions.pop(),'detail:4');
assert.equal(key(row,'ArrowRight',{ctrlKey:true}).defaultPrevented,false);

// A select/dropdown search field is also part of the standard search contract.
let pick=new El({tagName:'SELECT',selectors:['select']});pick.search=true;
key(pick,'Enter');assert.equal(actions.pop(),'search');
// Ctrl+Enter is never the implicit apply operation in single-line editors.
detail.open=true;
key(editor,'Enter',{ctrlKey:true});assert.equal(actions.length,0);
detail.open=false;
console.log('Studio keyboard standard policy: PASS (14 scenarios)');
