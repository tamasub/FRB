import test from 'node:test';
import assert from 'node:assert/strict';
import vm from 'node:vm';
import fs from 'node:fs';
const root = new URL('./',import.meta.url);
const ctx = {console,Date,Set,Map,Error,TypeError};
vm.createContext(ctx);
for (const f of ['js/smart_search_engine.js','js/frb_smart_search_api.js']) {
  vm.runInContext(fs.readFileSync(new URL(f,root),'utf8'),ctx);
}
const api=ctx.FRBSmartSearch;
const fields=[{field:'title',caption:'タイトル',type:'string'},
  {field:'priority',caption:'優先度',type:'select',options:[{value:'high',label:'高'},{value:'low',label:'低'}]},
  {field:'count',caption:'件数',type:'number'},{field:'enabled',caption:'有効',type:'boolean'}];
const rows=[{title:'FRB Launch',priority:'high',count:3,enabled:true},{title:'Studio',priority:'low',count:5,enabled:false},{title:'Other',priority:'high',count:7,enabled:true}];
const engine=api.create({fields});
test('host-independent API provides parse, match and filter',()=>{
  assert.equal(engine.parse('件数=2..5').kind,'range');
  assert.deepEqual(engine.filter(rows,'優先度=高 件数=2..5').map(x=>x.title),['FRB Launch']);
  assert.deepEqual(engine.filter(rows,'タイトル=Studio or 件数>=7').map(x=>x.title),['Studio','Other']);
  assert.deepEqual(engine.filter(rows,'有効=true').map(x=>x.title),['FRB Launch','Other']);
  assert.equal(engine.match(rows[0],'count>2'),true);
});
test('options normalize display and stored values',()=>{
  const f=engine.getFields()[1];
  assert.equal(f.field,'priority'); assert.equal(f.options[0].label,'高');
  assert.equal(f.options[0].value,'high');
});
test('contract stays independent of ViewDef; explicit errors',()=>{
  assert.equal(api.normalizeFields([{id:'x',label:'項目',type:'enum',options:['A','B']}])[0].type,'select');
  assert.throws(()=>api.normalizeFields([{field:'x'},{field:'x'}]), /duplicate field/);
  assert.throws(()=>api.normalizeFields([{field:'x',type:'no-such-type'}]),/unsupported field type/);
  assert.throws(()=>engine.parse('不明=1'), e=>e.code==='UNKNOWN_FIELD');
  assert.throws(()=>engine.parse('件数=9..2'), e=>e.code==='REVERSED_RANGE');
});
test('one public script contains no ViewDef, SQLite or NativeShell calls',()=>{
  const t=fs.readFileSync(new URL('js/frb_smart_search_api.js',root),'utf8');
  assert.doesNotMatch(t.replace(/^\s*\/\/.*$/gm,''),/gridDef\(|viewDef\(|SQLITE|exec\(|NativeShell/);
});
