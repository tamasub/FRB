// studio_work_0268 Step 1 — parser/evaluator contract and SearchFilter integration.
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
const context={console,Date};vm.createContext(context);
for (const file of ['wwwroot/js/responsibilities/smart_search_engine.js','wwwroot/js/responsibilities/search_filter.js']) {
  vm.runInContext(fs.readFileSync(file,'utf8'),context,{filename:file});
}
const engine=context.StudioSmartSearch, filter=context.SearchFilter;
const fields=[
  {field:'title',caption:'タイトル',type:'text'},
  {field:'score',caption:'数値項目A',type:'number'},
  {field:'date',caption:'更新日',type:'date'},
  {field:'status',caption:'状態',type:'select',options:[{value:'DONE',label:'完了'},{value:'PENDING',label:'未完了'}]},
  {field:'enabled',caption:'有効',type:'boolean'},
  {field:'owner.name',caption:'担当者',type:'text'}
];
const rows=[
  {id:'1',title:'SQLite 完全版',score:2,date:'2026-10-01',status:'DONE',enabled:true,owner:{name:'田中'},detail:{memo:'aAA cCc'}},
  {id:'2',title:'SQLite',score:5,date:'2026-10-22',status:'PENDING',enabled:false,owner:{name:'佐藤'},detail:{memo:'bbb ddd'}},
  {id:'3',title:'Python',score:6,date:'2026-10-31',status:'DONE',enabled:true,owner:{name:'田中'},children:[{memo:'ccc bbb'}]},
  {id:'4',title:'月次 報告',score:0,date:'2026-09-30',status:null,enabled:null,owner:{name:'山田'},detail:{memo:'aAA ddd'}},
];
const ids=(q,criteria=[])=>Array.from(filter.apply(rows,criteria,{fullText:q,fields}),entry=>entry.row.id);
const issue=(q,code)=>assert.throws(()=>engine.parse(q,fields),e=>e.name==='StudioSmartSearchError'&&e.code===code);

test('all-field AND, OR, explicit AND, nested parentheses, precedence and descendant texts',()=>{
  assert.deepEqual(ids('sqlite'),['1','2']);
  assert.deepEqual(ids('sqlite 田中'),['1']);
  assert.deepEqual(ids('SQLite or Python'),['1','2','3']);
  assert.deepEqual(ids('(aaa or bbb) (ccc or ddd)'),['1','2','3','4']);
  assert.deepEqual(ids('((aaa or bbb) or (ccc or ddd))'),['1','2','3','4']);
  assert.deepEqual(ids('Python OR SQLite AND 佐藤'),['2','3']);
  assert.deepEqual(ids('SQLite AND 佐藤'),['2']);
  assert.deepEqual(ids('(Python or SQLite) 田中'),['1','3']);
});
test('field names use IDs or captions; string default contains and exact matches',()=>{
  assert.deepEqual(ids('タイトル=SQLite'),['1','2']);
  assert.deepEqual(ids('title==SQLite'),['2']);
  assert.deepEqual(ids('タイトル=!SQLite'),['3','4']);
  assert.deepEqual(ids('title!=SQLite'),['3','4']);
  assert.deepEqual(ids('担当者=田中'),['1','3']);
  assert.deepEqual(ids('title="月次 報告"'),['4']);
  assert.equal(engine.evaluate({title:'Hello'}, engine.parse('"タイトル"=Hello',fields)),true);
  assert.deepEqual(ids('"月次 報告"'),['4']);
  assert.deepEqual(ids("title='月次 報告'"),['4']);
});
test('number, date, Boolean, select lookup and ranges are typed',()=>{
  assert.deepEqual(ids('数値項目A=2'),['1']);
  assert.deepEqual(ids('score==2'),['1']);
  assert.deepEqual(ids('score=2..5'),['1','2']);
  assert.deepEqual(ids('score=2..'),['1','2','3']);
  assert.deepEqual(ids('score=..5'),['1','2','4']);
  assert.deepEqual(ids('score>=5'),['2','3']);
  assert.deepEqual(ids('score=>5'),['2','3']);
  assert.deepEqual(ids('score<=2'),['1','4']);
  assert.deepEqual(ids('score=<2'),['1','4']);
  assert.deepEqual(ids('score>5'),['3']);
  assert.deepEqual(ids('score<2'),['4']);
  assert.deepEqual(ids('score=!5'),['1','3','4']);
  assert.deepEqual(ids('score!=5'),['1','3','4']);
  assert.deepEqual(ids('date=2026-10-01..2026-10-22'),['1','2']);
  assert.deepEqual(ids('更新日=2026-10-01..'),['1','2','3']);
  assert.deepEqual(ids('状態=完了'),['1','3']);
  assert.deepEqual(ids('status=DONE'),['1','3']);
  assert.equal(engine.evaluate({status:'DONE'},engine.parse('状態=完了',[{field:'status',caption:'状態',type:'select',options:[{cd:'DONE',name:'完了'}]}])),true);
  assert.equal(engine.familyFor({type:'text',validation_type:'studio.date.ymd'}),'date');
  assert.deepEqual(ids('状態!=完了'),['2']);
  assert.deepEqual(ids('有効=true'),['1','3']);
  assert.deepEqual(ids('enabled=いいえ'),['2']);
});
test('legacy individual SearchFilter criteria AND SmartSearch without affecting plugin pipeline',()=>{
  assert.deepEqual(ids('(SQLite or Python)',[{field:'score',type:'number',operator:'gte',value:5}]),['2','3']);
  assert.deepEqual(ids('',[{field:'score',type:'number',operator:'gte',value:5}]),['2','3']);
});
test('fail closed for malformed, ambiguous and unknown field names',()=>{
  issue('title=','MISSING_VALUE');
  issue('score=5..2','REVERSED_RANGE');
  issue('score=abc','INVALID_VALUE');
  issue('date=2026-02-30','INVALID_VALUE');
  issue('state=完了','UNKNOWN_FIELD');
  issue('title="not closed','UNCLOSED_QUOTE');
  issue('((sqlite or Python)','UNCLOSED_PAREN');
  issue('sqlite or','MISSING_OPERAND');
  issue('sqlite)','UNEXPECTED_TOKEN');
  issue('title>aaa','INCOMPATIBLE_OPERATOR');
  const conflict=[{field:'a',caption:'重複',type:'text'},{field:'b',caption:'重複',type:'text'}];
  assert.throws(()=>engine.parse('重複=foo',conflict),e=>e.code==='AMBIGUOUS_FIELD');
  assert.equal(engine.parse('a=foo',conflict).field,'a');
});
test('text search retains literal apostrophes and standalone URL slash without command semantics',()=>{
  const sample=[{title:"O'Reilly",note:'https://example.org/a/b?c=2'}];
  assert.equal(engine.evaluate(sample[0],engine.parse("title=O'Reilly",fields)),true);
  assert.equal(engine.evaluate(sample[0],engine.parse('https://example.org/a/b',fields)),true);
  assert.equal(engine.evaluate({memo:'x=y'},engine.parse('\"x=y\"',fields)),true);
});
test('browser script integration order and UI error guard are present',()=>{
  const html=fs.readFileSync('wwwroot/index.html','utf8');
  assert.ok(html.indexOf('responsibilities/smart_search_engine.js')<html.indexOf('responsibilities/search_filter.js'));
  assert.match(html,/studioSmartSearchError/);
  assert.match(html,/app\.js\?[^"\n]*smart=20261022/);
  const grid=fs.readFileSync('wwwroot/js/renderers/grid_detail.js','utf8');
  assert.match(grid,/fullText, fields: gd\.fields/);
  assert.match(grid,/StudioSmartSearchError/);
  assert.doesNotMatch(fs.readFileSync('wwwroot/js/responsibilities/smart_search_engine.js','utf8'),/document\.|querySelector|addEventListener/);
});
