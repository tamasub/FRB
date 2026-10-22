// studio_work_0268: Smart Search Editor's DOM-independent candidate/trigger contract.
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
const context={console};vm.createContext(context);
for (const path of ['wwwroot/js/responsibilities/smart_search_engine.js','wwwroot/js/ui/studio_smart_search_editor.js']) {
  vm.runInContext(fs.readFileSync(path,'utf8'),context,{filename:path});
}
const editor=context.StudioSmartSearchEditor;
const defs=[
  {field:'title',caption:'タイトル',type:'text'},
  {field:'status',caption:'状態',type:'select',options:[{cd:'DONE',name:'完了'},{cd:'TODO',name:'未完了'}]},
  {field:'enabled',caption:'有効',type:'boolean'},
  {field:'status2',caption:'状態',type:'select',options:['A']},
  {field:'withSpace',caption:'作業 概要',type:'text'}
];
test('Slash is always a Smart Search completion command, including after text and across selections (except modifiers and IME)',()=>{
  const ev={key:'/',keyCode:191,isComposing:false,ctrlKey:false,metaKey:false,altKey:false};
  const input=(value,cursor=value.length)=>({value,selectionStart:cursor,selectionEnd:cursor,disabled:false,readOnly:false});
  assert.equal(editor.isSearchTrigger(ev,input('')),true);
  assert.equal(editor.isSearchTrigger(ev,input('SQLite ')),true);
  assert.equal(editor.isSearchTrigger(ev,input('(SQLite ')),true);
  assert.equal(editor.isSearchTrigger(ev,input('SQLite')),true);
  assert.equal(editor.isSearchTrigger(ev,input('https:')),true);
  assert.equal(editor.isSearchTrigger(ev,input('C:')),true);
  assert.equal(editor.isSearchTrigger({...ev,isComposing:true},input('')),false);
  assert.equal(editor.isSearchTrigger({...ev,keyCode:229},input('')),false);
  assert.equal(editor.isSearchTrigger({...ev,ctrlKey:true},input('')),false);
  assert.equal(editor.isSearchTrigger({...ev,metaKey:true},input('')),false);
  assert.equal(editor.isSearchTrigger({...ev,altKey:true},input('')),false);
  assert.equal(editor.isSearchTrigger({...ev,key:'?'},input('')),false);
  assert.equal(editor.isSearchTrigger(ev,{...input(''),disabled:true}),false);
  assert.equal(editor.isSearchTrigger(ev,{...input('abc',1),selectionEnd:2}),true);
});
test('Field suggestions use labels and IDs without hardcoding; duplicate captions use IDs',()=>{
  const choices=editor.fieldChoices(defs);
  assert.equal(choices.length,defs.length);
  assert.equal(choices.find(x=>x.id==='title').insertName,'タイトル');
  assert.equal(choices.find(x=>x.id==='status').insertName,'status');
  assert.equal(choices.find(x=>x.id==='status2').insertName,'status2');
  assert.equal(editor.quoteAtom('作業 概要'),'"作業 概要"');
  assert.equal(editor.quoteAtom('完了'),'完了');
  assert.equal(editor.quoteAtom('月次 (報告)'),'"月次 (報告)"');
});
test('Select display label is kept, Boolean is fixed true/false, free text offers no choices',()=>{
  const choices=editor.valueChoices(defs[1]);
  assert.equal(choices[0].label,'完了');
  assert.equal(choices[0].value,'DONE');
  assert.equal(choices[0].insertValue,'完了');
  assert.equal(editor.valueChoices(defs[2]).map(x=>x.value).join(','),'true,false');
  assert.equal(editor.valueChoices(defs[0]).length,0);
  // The canonical parser resolves the user-friendly option label to its stored value.
  const ast=context.StudioSmartSearch.parse('状態=完了',[defs[1]]);
  assert.equal(context.StudioSmartSearch.evaluate({status:'DONE'},ast),true);
});
test('Value completion supports edited =! / != operators, exact, and quoted captions',()=>{
  const cases=['状態=','状態=!','状態!=','"作業 概要"='];
  for (const expression of cases.slice(0,3)) {
    const ctx=editor.valueContext(expression,[defs[1]]);
    assert.equal(ctx?.field.field,'status');
    assert.equal(ctx.typed,'');
  }
  assert.equal(editor.valueContext('状態==完',[defs[1]])?.typed,'完');
  assert.equal(editor.valueContext('"作業 概要"=',defs),null);
  assert.equal(editor.valueContext('abc status=完',defs)?.field.field,'status');
  assert.equal(editor.valueContext('状態=',defs),null); // duplicate captions need an ID
  assert.equal(editor.valueContext('https://site/',defs),null);
});
test('Integration connects Script and Input; standard Enter/clear behavior remains',()=>{
  const html=fs.readFileSync('wwwroot/index.html','utf8');
  const app=fs.readFileSync('wwwroot/app.js','utf8');
  const css=fs.readFileSync('wwwroot/styles.css','utf8');
  assert.match(html,/js\/ui\/studio_smart_search_editor\.js/);
  assert.match(app,/StudioSmartSearchEditor\.setup/);
  assert.match(app,/studioSmartSearchEditor\?\.close\(\)/);
  assert.match(app,/\$\('searchBtn'\)\.addEventListener\('click', applySearch\)/);
  assert.match(css,/\.studio-smart-search-suggestions/);
});

// Regression: Grid is a following .card with its own backdrop-filter stacking context.
// Popup z-index alone cannot place it above the grid; its parent card must be elevated while open.
test('Suggestion popup raises the search card stacking context while open and resets on close',()=>{
  const js=fs.readFileSync('wwwroot/js/ui/studio_smart_search_editor.js','utf8');
  const css=fs.readFileSync('wwwroot/styles.css','utf8');
  assert.match(js,/section\.classList\.add\('studio-smart-search-popup-open'\)/);
  assert.match(js,/section\.classList\.remove\('studio-smart-search-popup-open'\)/);
  assert.match(css,/#searchSection\.studio-smart-search-popup-open\s*\{[^}]*z-index:\s*12;/);
  assert.match(css,/#searchSection \.studio-smart-search-suggestions\s*\{[^}]*position:\s*absolute;/s);
});

// Candidate search box & editor context-menu are distinct UI responsibilities.
test('Candidate popup has its own filter, editable query keeps focus behavior, right-click is equivalent to slash',()=>{
  const js=fs.readFileSync('wwwroot/js/ui/studio_smart_search_editor.js','utf8');
  const css=fs.readFileSync('wwwroot/styles.css','utf8');
  assert.match(js,/studio-smart-search-candidate-filter/);
  assert.match(js,/filterItems\(items, query\)/);
  assert.match(js,/filter\.addEventListener\('input',updateCandidateFilter\)/);
  assert.match(js,/input\.addEventListener\('contextmenu'/);
  assert.match(js,/event\.preventDefault\(\);\s*args\.onOpen\?\.\(\);\s*showFieldList\(\)/);
  assert.match(css,/\.studio-smart-search-option-list/);
});

// FRB Launch keyboard culture: Tab, Enter, and Right are equivalent only while
// a suggestion is active, whether focus is in the candidate filter or query input.
test('Suggestion confirmation uses Tab / Enter / ArrowRight in both focus contexts',()=>{
  const js=fs.readFileSync('wwwroot/js/ui/studio_smart_search_editor.js','utf8');
  assert.match(js,/function isConfirmKey\(key\)\s*\{\s*return key==='Tab' \|\| key==='Enter' \|\| key==='ArrowRight';\s*\}/);
  assert.equal((js.match(/if \(isConfirmKey\(event\.key\) && state\.items\.length\)/g) ?? []).length,2);
  assert.match(js,/Tab・Enter・→ 確定/g);
  // With no popup (or no candidates), the editor must not consume ArrowRight.
  assert.match(js,/if \(!state\) return;/);
  assert.match(js,/if \(isConfirmKey\(event\.key\) && state\.items\.length\)/);
});

// '/' never reaches the query as a literal character. Selection anchoring is
// preserved when the candidate filter receives focus; spacing is handled on choice.
test('Slash command consumes the key and field insertion handles required spacing',()=>{
  const js=fs.readFileSync('wwwroot/js/ui/studio_smart_search_editor.js','utf8');
  assert.match(js,/event\.preventDefault\(\); event\.stopImmediatePropagation\(\); args\.onOpen\?\.\(\); showFieldList\(\)/);
  assert.match(js,/caret:input\.selectionStart,selectionEnd:input\.selectionEnd/);
  assert.ok(js.includes(String.raw`const needsSpace=start>0 && !/[\s(]/u.test(input.value[start-1]);`));
  assert.ok(js.includes("const insertion=(needsSpace?' ':'')+quoteAtom(chosen.insertName)+'=';"));
  assert.ok(js.includes('close(); replace(start,end,insertion);'));
});
