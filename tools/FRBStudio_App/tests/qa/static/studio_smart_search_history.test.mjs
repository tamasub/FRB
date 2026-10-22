// studio_work_0268: history persistence, scoping, register/dedupe/order/remove.
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
const ctx={};vm.createContext(ctx);
vm.runInContext(fs.readFileSync('wwwroot/js/ui/studio_smart_search_history.js','utf8'),ctx);
const history=ctx.StudioSmartSearchHistory;
function memoryStorage() {
  const map=new Map(); return {
    getItem:k=>map.get(k)??null,
    setItem:(k,v)=>map.set(k,String(v)),
    map
  };
}
test('Registered search history is scoped per Data JSON, deduped and newest first',()=>{
  const store=memoryStorage();
  history.register(store,'DATA\\JSON\\foo.json','  status=完了 ');
  history.register(store,'data/json/foo.json','priority=高');
  history.register(store,'data/json/foo.json','status=完了');
  assert.deepEqual(Array.from(history.read(store,'data/json/foo.json')),['status=完了','priority=高']);
  assert.deepEqual(Array.from(history.read(store,'other.json')),[]);
});
test('History up/down movement and removal preserve other entries',()=>{
  assert.deepEqual(Array.from(history.move(['a','b','c'],1,-1)),['b','a','c']);
  assert.deepEqual(Array.from(history.move(['a','b','c'],2,1)),['a','b','c']);
  assert.deepEqual(Array.from(history.remove(['a','b','c'],1)),['a','c']);
});
test('Blank expression is ignored and quota/unavailable storage does not crash',()=>{
  const store=memoryStorage();
  assert.equal(history.register(store,'foo','').added,false);
  assert.deepEqual(Array.from(history.read(store,'foo')),[]);
  const denied={getItem(){throw Error('denied');},setItem(){throw Error('denied');}};
  assert.equal(history.register(denied,'foo','valid').persisted,false);
  assert.deepEqual(Array.from(history.read(denied,'foo')),[]);
});
test('UI ties history buttons into main Search and popup layering',()=>{
  const html=fs.readFileSync('wwwroot/index.html','utf8');
  const js=fs.readFileSync('wwwroot/app.js','utf8');
  const css=fs.readFileSync('wwwroot/styles.css','utf8');
  for(const id of ['studioSmartSearchHistoryRegister','studioSmartSearchHistoryOpen'])assert.ok(html.includes(id));
  assert.match(html,/js\/ui\/studio_smart_search_history\.js/);
  assert.match(js,/StudioSmartSearchHistory\.setup/);
  assert.match(js,/studioSmartSearchHistory\?\.close\(\)/);
  assert.match(css,/#searchSection\.studio-smart-history-popup-open\s*\{\s*z-index:12/);
});
