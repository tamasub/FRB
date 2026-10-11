const {test}=require('node:test');const a=require('node:assert/strict');const fs=require('node:fs');const M=require('../../wwwroot/js/runtime/tree_model.js');
const c={idField:'id',parentField:'parent',labelField:'name',orderField:'order',groupField:'group',parentKindField:'kind',parentKinds:['folder']};
const fresh=()=>[{id:'a',parent:'',group:'one',order:10,kind:'folder'},{id:'b',parent:'a',group:'one',order:10,kind:'folder'},{id:'c',parent:'b',group:'one',order:10},{id:'d',parent:'a',group:'one',order:20},{id:'e',parent:'',group:'two',order:10,kind:'folder'}];
test('collapsed rows and search ancestors',()=>{const m=M.build(fresh(),c);a.deepEqual(M.project(m,[0,1,2,3,4],new Set(['a']),c).map(n=>n.index),[0,4]);a.deepEqual(M.project(m,[2],new Set(['a']),c).map(n=>n.index),[0,1,2]);});
test('move across pages propagates to descendants and preserves IDs',()=>{const r=fresh();M.move(r,c,1,4);a.equal(r[1].parent,'e');a.equal(r[2].parent,'b');a.equal(r[2].group,'two');a.deepEqual(r.map(x=>x.id),['a','b','c','d','e']);M.build(r,c);});
test('reject descendant target without mutations',()=>{const r=fresh(),old=JSON.stringify(r);a.throws(()=>M.move(r,c,0,1));a.equal(JSON.stringify(r),old);});
test('reorder siblings only',()=>{const r=fresh();a.equal(M.reorder(r,c,3,-1),true);a.ok(r[3].order<r[1].order);a.equal(r[2].order,10);a.equal(M.reorder(r,c,0,1),false);});
test('invalid hierarchies are reported without silent repair',()=>{for(const mutate of [r=>r[1].id='a',r=>r[0].parent='c',r=>r[1].parent='missing',r=>r[1].group='two']){const r=fresh();mutate(r);a.throws(()=>M.build(r,c));}});
test('ungrouped reusable contract',()=>{const cfg={...c,groupField:undefined};const r=fresh();M.move(r,cfg,3,null);a.equal(r[3].parent,'');M.build(r,cfg);});
