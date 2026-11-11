// studio_work_0269 / Move via the exact canonical Studio TreeModel.
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {spawnSync} from 'node:child_process';
import {evaluateChangeSet} from '../../tools/change_core/change_core.mjs';
import {readSnapshot} from '../../tools/change_core/storage.mjs';
const root=fileURLToPath(new URL('../../',import.meta.url));
const def=JSON.parse(await fs.readFile(path.join(root,'defs/launch/frb_launch_maintenance_view_def_v0_1.json'),'utf8'));
const view=def.views.find(x=>x.id==='items_view');
const row=(id,p='',g='work',order=10,kind='command')=>({item_id:id,parent_item_id:p,page_id:g,sort_order:order,item_kind:kind,title:id,launch_actions:[]});
const doc=()=>({pages:[{page_id:'work'},{page_id:'frb'}],items:[
 row('root','','work',10,'category'),row('a','root','work',10),row('b','root','work',20),row('cat','root','work',30,'category'),
 row('sub','cat','work',10),row('root2','','frb',10,'category'),row('x','root2','frb',10)
],metadata:{japanese:'触らない'}});
function req(id, placement,group='work',mode='dry_run') {return {schema_version:'studio_changeset_v0_1',request_id:'move',mode,document_ref:'approved_launch_config',view_def:'launch/frb_launch_maintenance_view_def_v0_1.json',view_id:'items_view',operations:[{operation:'move',section_id:'items',targets:[{id,group_id:group}],placement}]};}
function children(d,p,g) {return d.items.filter(x=>x.parent_item_id===p&&x.page_id===g).sort((x,y)=>x.sort_order-y.sort_order).map(x=>x.item_id);}
test('Move: before/after/end reorder siblings; no filesystem modification',()=>{
 const before=doc();const baseline=structuredClone(before);
 const r=evaluateChangeSet(before,req('b',{parent_id:'root',group_id:'work',position:'before',anchor_id:'a'}),view);
 assert.equal(r.summary.moved,1);assert.deepEqual(children(r.after,'root','work'),['b','a','cat']);
 assert.equal(r.after.metadata.japanese,'触らない');assert.deepEqual(before,baseline);
 assert.deepEqual(r.expected_diff,r.actual_diff);
 const after=evaluateChangeSet(r.after,req('b',{parent_id:'root',group_id:'work',position:'after',anchor_id:'a'}),view);
 assert.deepEqual(children(after.after,'root','work'),['a','b','cat']);
 const last=evaluateChangeSet(after.after,req('a',{parent_id:'root',group_id:'work',position:'end'}),view);
 assert.deepEqual(children(last.after,'root','work'),['b','cat','a']);
});
test('Move: folder subtree changes Page together; unrelated siblings retained',()=>{
 const r=evaluateChangeSet(doc(),req('cat',{parent_id:'root2',group_id:'frb',position:'end'}),view);
 assert.equal(r.summary.moved,1);
 assert.deepEqual(children(r.after,'root','work'),['a','b']);
 assert.deepEqual(children(r.after,'root2','frb'),['x','cat']);
 assert.equal(r.after.items.find(x=>x.item_id==='sub').page_id,'frb');
 assert.equal(r.after.items.find(x=>x.item_id==='sub').parent_item_id,'cat');
 assert.deepEqual(r.expected_diff,r.actual_diff);
});
test('Move: rejects cycles, command parents, mismatched groups, anchor from another folder, missing IDs',()=>{
 for(const [change,code] of [
  [req('cat',{parent_id:'cat',group_id:'work',position:'end'}),'MOVE_INVALID'],
  [req('cat',{parent_id:'sub',group_id:'work',position:'end'}),'PARENT_KIND_INVALID'],
  [req('cat',{parent_id:'a',group_id:'work',position:'end'}),'PARENT_KIND_INVALID'],
  [req('cat',{parent_id:'root2',group_id:'work',position:'end'}),'GROUP_MISMATCH'],
  [req('a',{parent_id:'root',group_id:'work',position:'before',anchor_id:'x'}),'ANCHOR_NOT_SIBLING'],
  [req('absent',{parent_id:'root',group_id:'work',position:'end'}),'TARGET_NOT_FOUND'],
  [req('cat',{parent_id:'root',group_id:'frb',position:'end'}),'GROUP_MISMATCH'],
 ]) assert.throws(()=>evaluateChangeSet(doc(),change,view),e=>e.code===code,code);
});
test('CLI Move: preview/commit/SHA race; leaves original JSON alone in preview',async t=>{
 const folder=await fs.mkdtemp(path.join(os.tmpdir(),'frb-move-'));
 t.after(()=>fs.rm(folder,{recursive:true,force:true}));
 const filename=path.join(folder,'config.json'),trusted=path.join(folder,'trusted.json');
 await fs.writeFile(filename,JSON.stringify(doc(),null,2));
 await fs.writeFile(trusted,JSON.stringify({schema_version:'studio_change_core_config_v0_1',documents:{approved_launch_config:{path:filename,view_def:'launch/frb_launch_maintenance_view_def_v0_1.json',view_id:'items_view',section_ids:['items']}}}));
 const snap=await readSnapshot(filename);
 const input=req('a',{parent_id:'root',group_id:'work',position:'after',anchor_id:'b'});input.base_sha256=snap.sha256;
 const run=()=>{const result=spawnSync(process.execPath,[path.join(root,'tools/change_core/cli.mjs'),'--config',trusted],{input:JSON.stringify(input),encoding:'utf8'});return JSON.parse(result.stdout);};
 let out=run();assert.equal(out.status,'PREVIEW');assert.equal(out.summary.moved,1);assert.equal((await readSnapshot(filename)).sha256,snap.sha256);
 input.mode='commit';out=run();assert.equal(out.status,'COMMITTED');assert.equal(out.saved,true);assert.deepEqual(children((await readSnapshot(filename)).document,'root','work'),['b','a','cat']);
 out=run();assert.equal(out.status,'CONFLICT');
});
