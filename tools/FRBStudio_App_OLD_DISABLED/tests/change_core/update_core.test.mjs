// studio_work_0269 / generic Update acceptance and safety checks
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
const view=def.views.find(v=>v.id==='items_view');
const doc=()=>({title:'Do not touch',pages:[{page_id:'system',title:'System'}],items:[
 {item_id:'folders',page_id:'system',parent_item_id:'',sort_order:10,item_kind:'category',title:'Files'},
 {item_id:'it1',page_id:'system',parent_item_id:'folders',sort_order:10,item_kind:'command',title:'Before',icon_key:'file',description:'Before description',launch_actions:[{launch_action_type:'Open',launch_target:'C:\\keep.txt',meta:{note:'old'}}]},
 {item_id:'it2',page_id:'system',parent_item_id:'folders',sort_order:20,item_kind:'directory',title:'Folder',launch_browse_target:'C:\\keep-folder'}
],untouched:{japanese:'残す'}});
const update=(targets,mode='dry_run')=>({schema_version:'studio_changeset_v0_1',request_id:'update-1',mode,
 document_ref:'approved_launch_config',view_def:'launch/frb_launch_maintenance_view_def_v0_1.json',view_id:'items_view',
 operations:[{operation:'update',section_id:'items',targets}]});
const one=(changes,id='it1',group_id='system')=>({id,group_id,changes});
const change=(path,value)=>({path,value});
const run=(config,input)=>{const r=spawnSync(process.execPath,[path.join(root,'tools/change_core/cli.mjs'),'--config',config],{input:JSON.stringify(input),encoding:'utf8'});return {code:r.status,reply:JSON.parse(r.stdout)};};
async function setup(t){const dir=await fs.mkdtemp(path.join(os.tmpdir(),'frb-update-'));t.after(()=>fs.rm(dir,{recursive:true,force:true}));const file=path.join(dir,'document.json');await fs.writeFile(file,JSON.stringify(doc(),null,2));const cfg=path.join(dir,'approved.json');await fs.writeFile(cfg,JSON.stringify({schema_version:'studio_change_core_config_v0_1',documents:{approved_launch_config:{path:file,view_def:'launch/frb_launch_maintenance_view_def_v0_1.json',view_id:'items_view',section_ids:['items']}}}));return {file,cfg};}
test('Update: multiple fields, multiple rows, nested array/object, no path change',()=>{
 const before=doc();const saved=structuredClone(before);
 const req=update([
  one([change('title','日本語の新名称'),change('description','更新された説明'),change('icon_key','globe'),change('/launch_actions/0/meta/note','新しいノート')]),
  one([change('title','Folder 2')],'it2')
 ]);
 const result=evaluateChangeSet(before,req,view);
 assert.equal(result.summary.changed_existing,2);
 assert.equal(result.summary.added,0);assert.equal(result.summary.deleted,0);
 assert.equal(result.after.items[1].title,'日本語の新名称');
 assert.equal(result.after.items[1].launch_actions[0].launch_target,'C:\\keep.txt');
 assert.equal(result.after.items[1].launch_actions[0].meta.note,'新しいノート');
 assert.equal(result.after.items[2].launch_browse_target,'C:\\keep-folder');
 assert.deepEqual(result.after.untouched,before.untouched);
 assert.deepEqual(result.validation_rows.map(x=>x.row.title),['日本語の新名称','Folder 2']);
 assert.deepEqual(result.expected_diff,result.actual_diff);
 assert.deepEqual(before,saved);
});
test('Update rejects identity/group/order mutation and dangerous property paths',()=>{
 for(const value of ['item_id','page_id','parent_item_id','sort_order']){
  assert.throws(()=>evaluateChangeSet(doc(),update([one([change(value,'tamper')])]),view),e=>e.code==='PROTECTED_FIELD',value);
 }
 for(const value of ['/launch_actions/1/launch_target','/__proto__/foo','/launch_actions/-1/launch_target','launch_actions.0']){
  assert.throws(()=>evaluateChangeSet(doc(),update([one([change(value,'tamper')])]),view),e=>e.code==='INVALID_FIELD_PATH',value);
 }
 for(const target of [one([change('title','x')],'none'),one([change('title','x')],'it1','work'),one([])]){
  assert.throws(()=>evaluateChangeSet(doc(),update([target]),view));
 }
});
test('Update and Add in one ChangeSet are atomic; invalid second target prevents any application',()=>{
 const before=doc();const r=update([one([change('title','new')]),one([change('item_id','tamper')],'it2')]);
 assert.throws(()=>evaluateChangeSet(before,r,view),e=>e.code==='PROTECTED_FIELD');
 assert.equal(before.items[1].title,'Before');
});
test('CLI Update: dry_run/commit/SHA conflict/whole-row validation mode',async t=>{
 const {file,cfg}=await setup(t);const snap=await readSnapshot(file);
 const r=update([one([change('title','改訂'),change('icon_key','globe')])]);r.base_sha256=snap.sha256;
 let x=run(cfg,r);assert.equal(x.reply.status,'PREVIEW');assert.equal(x.reply.validation_mode,'SKIPPED_FIELD_DEFINITION_NOT_DECLARED');assert.equal(x.reply.summary.changed_existing,1);assert.equal((await readSnapshot(file)).sha256,snap.sha256);
 r.mode='commit';x=run(cfg,r);assert.equal(x.reply.status,'COMMITTED');assert.equal(x.reply.saved,true);
 const saved=await readSnapshot(file);assert.equal(saved.document.items[1].title,'改訂');assert.equal(saved.document.items[1].launch_actions[0].launch_target,'C:\\keep.txt');
 x=run(cfg,r);assert.equal(x.reply.status,'CONFLICT');assert.equal((await readSnapshot(file)).sha256,saved.sha256);
});
