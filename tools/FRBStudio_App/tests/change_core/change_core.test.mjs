import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import {spawnSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import {evaluateChangeSet,compareDiff,ChangeSetError} from '../../tools/change_core/change_core.mjs';
import {sha256,readSnapshot,commitDocument} from '../../tools/change_core/storage.mjs';
import {buildFieldValidator} from '../../tools/change_core/field_validation.mjs';
const root=fileURLToPath(new URL('../../',import.meta.url));
const def=JSON.parse(await fs.readFile(path.join(root,'defs/launch/frb_launch_maintenance_view_def_v0_1.json'),'utf8'));
const view=def.views.find(v=>v.id==='items_view');
const document=()=>({title:'test',pages:[{page_id:'work',title:'work'}],items:[{item_id:'folders',parent_item_id:'',page_id:'work',sort_order:10,title:'Folder',item_kind:'category'}]});
const request=(records,mode='commit')=>({schema_version:'studio_changeset_v0_1',request_id:'test-1',mode,document_ref:'approved_launch_config',view_def:'launch/frb_launch_maintenance_view_def_v0_1.json',view_id:'items_view',operations:[{operation:'add',section_id:'items',placement:{group_id:'work',parent_id:'folders',position:'end'},records}]});
const record=(title)=>({title,item_kind:'command',launch_actions:[{launch_action_type:'Open',launch_target:'C:\\same.txt'}]});
async function sandbox(t){const dir=await fs.mkdtemp(path.join(os.tmpdir(),'studio-changeset-'));t.after(async()=>fs.rm(dir,{recursive:true,force:true}));const doc=path.join(dir,'doc.json');await fs.writeFile(doc,JSON.stringify(document(),null,2));const config=path.join(dir,'config.json');await fs.writeFile(config,JSON.stringify({schema_version:'studio_change_core_config_v0_1',documents:{approved_launch_config:{path:doc,view_def:'launch/frb_launch_maintenance_view_def_v0_1.json',view_id:'items_view',section_ids:['items']}}}));return {doc,config};}
function cli(config,input){const c=spawnSync(process.execPath,[path.join(root,'tools/change_core/cli.mjs'),'--config',config],{input:JSON.stringify(input),encoding:'utf8'});assert.ok(c.stdout,`stderr=${c.stderr}`);return {code:c.status,result:JSON.parse(c.stdout)};}
test('複数Add: Expected=Actual, ID固定, 既存行無変更, 同一Path許容',()=>{
 const before=document(),req=request([record('A'),record('B')]);const ret=evaluateChangeSet(before,req,view,{createId:(()=>{let n=0;return()=>`new-${++n}`;})()});
 assert.equal(ret.summary.added,2);assert.equal(ret.summary.changed_existing,0);assert.deepEqual(ret.expected_diff,ret.actual_diff);assert.equal(ret.after.items[0].title,'Folder');assert.deepEqual(ret.after.items.slice(1).map(r=>r.item_id),['new-1','new-2']);assert.deepEqual(ret.after.items.slice(1).map(r=>r.sort_order),[10,20]);assert.equal(before.items.length,1);assert.equal(ret.unexpected_diff.length,0);
});
test('不正な親・グループ・ID重複・未対応操作を保存前に拒否',()=>{
 for(const [change,code] of [
  [r=>{r.operations[0].placement.parent_id='missing';},'PARENT_NOT_FOUND'],
  [r=>{r.operations[0].placement.group_id='wrong';},'GROUP_MISMATCH'],
  [r=>{r.operations[0].records[0].item_id='folders';},'DUPLICATE_ID'],
  [r=>{r.operations[0].operation='delete';},'UNSUPPORTED_OPERATION'],
  [r=>{r.operations[0].placement.position='before';},'UNSUPPORTED_PLACEMENT']
 ]){const r=request([record('A')]);change(r);assert.throws(()=>evaluateChangeSet(document(),r,view),e=>e.code===code,code);}
});
test('plain array requires only explicit configured section; append can be non-tree',()=>{
 const v={sections:[{id:'entries',type:'grid',dataPath:'$.entries',keyField:'id'}]};const d={entries:[{id:'one',n:1}]};const r=request([{n:2}]);r.operations=[{operation:'add',section_id:'entries',records:[{n:2}]}];const result=evaluateChangeSet(d,r,v,{createId:()=> 'two'});assert.equal(result.after.entries[1].id,'two');
});
test('1件異常でChangeSet全体無変更',()=>{
 const before=document();const r=request([record('A'),{...record('B'),item_id:'folders'}]);assert.throws(()=>evaluateChangeSet(before,r,view),e=>e.code==='DUPLICATE_ID');assert.equal(before.items.length,1);
});
test('CLI: dry_run→commit→stale SHA conflict→no unintended change',async t=>{
 const {doc,config}=await sandbox(t);const base=await readSnapshot(doc);
 let r=request([record('A'),record('B')],'dry_run');r.base_sha256=base.sha256;
 let run=cli(config,r);assert.equal(run.code,0);assert.equal(run.result.status,'PREVIEW');assert.equal(run.result.validation_mode,'SKIPPED_FIELD_DEFINITION_NOT_DECLARED');assert.equal((await readSnapshot(doc)).sha256,base.sha256);
 r.mode='commit';run=cli(config,r);assert.equal(run.code,0);assert.equal(run.result.status,'COMMITTED');assert.equal(run.result.saved,true);assert.equal((await readSnapshot(doc)).document.items.length,3);
 const saved=await readSnapshot(doc);run=cli(config,r);assert.equal(run.code,1);assert.equal(run.result.status,'CONFLICT');assert.equal((await readSnapshot(doc)).sha256,saved.sha256);
});
test('CLI: unapproved document and section rejected; content unchanged',async t=>{
 const {doc,config}=await sandbox(t);const baseline=await readSnapshot(doc);const r=request([record('A')]);r.base_sha256=baseline.sha256;r.document_ref='other';let x=cli(config,r);assert.equal(x.code,1);assert.equal(x.result.errors[0].code,'DOCUMENT_NOT_ALLOWED');
 r.document_ref='approved_launch_config';r.operations[0].section_id='other';x=cli(config,r);assert.equal(x.result.errors[0].code,'SECTION_NOT_ALLOWED');assert.equal((await readSnapshot(doc)).sha256,baseline.sha256);
});
test('Lock busy and competing data changes fail before rename',async t=>{
 const {doc}=await sandbox(t);const snap=await readSnapshot(doc);const lock=`${doc}.studio-changeset.lock`;
 await fs.writeFile(lock,'busy');
 await assert.rejects(()=>commitDocument(doc,snap.sha256,'{}\n'),e=>e.code==='LOCKED');
 await fs.unlink(lock);
 await assert.rejects(()=>commitDocument(doc,snap.sha256,'{}\n',{beforeReplace:async()=>{await fs.writeFile(doc,'{"external":true}\n');}}),e=>e.code==='CONFLICT');
 assert.deepEqual((await readSnapshot(doc)).document,{external:true});
 assert.equal((await fs.readdir(path.dirname(doc))).filter(f=>f.endsWith('.tmp')||f.endsWith('.lock')).length,0);
});
test('Injected pre-rename failure retains original and deletes temporary files',async t=>{
 const {doc}=await sandbox(t);const snap=await readSnapshot(doc);
 await assert.rejects(()=>commitDocument(doc,snap.sha256,'{}\n',{beforeReplace:()=>{throw Error('simulated disk failure');}}),/simulated/);
 assert.equal((await readSnapshot(doc)).sha256,snap.sha256);
 const files=await fs.readdir(path.dirname(doc));assert.ok(!files.some(f=>f.endsWith('.tmp')||f.endsWith('.lock')));
});
test('Diff lists unexpected modifications outside allowed additions',()=>{
 const a=document(),b=structuredClone(a);b.items[0].title='MODIFIED';b.items.push({...record('A'),item_id:'id'});
 const actual=compareDiff(a,b);assert.ok(actual.some(d=>d.path==='/items/0/title'));assert.ok(actual.some(d=>d.path==='/items/1'));
});

test('Expected and Actual mismatch is rejected even if the operation planner succeeds',()=>{
 const r=request([record('A')]);
 assert.throws(()=>evaluateChangeSet(document(),r,view,{createId:()=> 'fixed',actualExecutor:(before)=>({...structuredClone(before),title:'unexpected'})}),e=>e.code==='UNEXPECTED_DIFF');
});
test('Existing Studio Field Definition service blocks required missing fields',async()=>{
 const v=JSON.parse(await fs.readFile(path.join(root,'defs/frb/frb_fft_field_definition_sample_view_def_v0_1.json'),'utf8'));
 const validate=await buildFieldValidator(root,v);
 const section=v.views[0].sections.find(s=>s.id==='measurement_sessions');
 assert.equal(validate.mode,'STUDIO_RUNTIME_FIELD_DEFINITION');
 assert.throws(()=>validate.validate({},section),e=>e.code==='FIELD_DEFINITION_REJECTED'&&/REQUIRED_MISSING/.test(e.message));
});
