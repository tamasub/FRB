// studio_work_0268: Regression for global Enter capture vs Smart Search completion.
// The keyboard standard listener runs on document in capture phase, before the
// Smart Search input's own keydown listener; it must yield while suggestions open.
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';

const source = fs.readFileSync('wwwroot/js/runtime/studio_keyboard_standard.js','utf8');

function fixture({ popupOpen = true, ariaExpanded = 'true', targetType = 'input' } = {}) {
  const listeners = new Map();
  let searchClicks = 0;
  class ElementMock {}
  const input = new ElementMock();
  input.getAttribute = (key) => key === 'aria-expanded' ? ariaExpanded : null;
  input.matches = () => true;
  const filter = new ElementMock();
  filter.matches = () => true;
  const formField = new ElementMock();
  formField.matches = () => true;
  const unrelated = new ElementMock();
  unrelated.matches = () => true;
  const popup = { hidden: !popupOpen, contains: target => target === filter };
  const form = {contains:target=>target===formField};
  const elements = {
    studioFullTextSearchInput:input,
    studioSmartSearchSuggestions:popup,
    searchForm:form,
    searchBtn:{disabled:false,click(){searchClicks++;}},
    detailDialog:{open:false}
  };
  const doc = {
    getElementById: key=>elements[key] ?? null,
    querySelectorAll:()=>[],
    addEventListener:(type, handler, capture)=>listeners.set(type,{handler,capture})
  };
  vm.runInNewContext(source,{document:doc,Element:ElementMock,window:{},console});
  const target = {input,filter,formField,unrelated}[targetType];
  const fire = (key='Enter', extra={}) => {
    const event={key,target,defaultPrevented:false,isComposing:false,keyCode:13,altKey:false,
      ctrlKey:false,shiftKey:false,metaKey:false,
      preventDefault(){this.defaultPrevented=true;},
      stopImmediatePropagation(){this.stopped=true;},...extra};
    listeners.get('keydown').handler(event);
    return event;
  };
  return {fire,get searchClicks(){return searchClicks;},listener:listeners.get('keydown')};
}

test('Global capture yields Enter to Smart Search while value candidates are open',()=>{
  const f=fixture({targetType:'input'});
  assert.equal(f.listener.capture,true);
  const event=f.fire();
  assert.equal(f.searchClicks,0);
  assert.equal(event.defaultPrevented,false);
  assert.equal(event.stopped,undefined);
});
test('Global capture yields Enter while candidate filter has focus',()=>{
  const f=fixture({targetType:'filter'});
  f.fire();
  assert.equal(f.searchClicks,0);
});
test('Closed popup: Enter still executes the existing full-text search',()=>{
  const f=fixture({popupOpen:false});
  const event=f.fire();
  assert.equal(f.searchClicks,1);
  assert.equal(event.defaultPrevented,true);
  assert.equal(event.stopped,true);
});
test('Other search inputs still submit even while Smart Search popup is open',()=>{
  const f=fixture({targetType:'formField'});
  f.fire();
  assert.equal(f.searchClicks,1);
});
test('The popup must be open AND aria-expanded before Enter is yielded',()=>{
  const f=fixture({ariaExpanded:'false',targetType:'input'});
  f.fire();
  assert.equal(f.searchClicks,1);
});
test('IME-composition Enter is ignored by the keyboard standard',()=>{
  const f=fixture({targetType:'input'});
  f.fire('Enter',{isComposing:true});
  assert.equal(f.searchClicks,0);
});
