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
import vm from 'node:vm';
import {createRequire} from 'node:module';
const require = createRequire(import.meta.url);
const sharedDiff = require('../../wwwroot/js/services/changeset/change_diff.js');
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
  [r=>{r.operations[0].operation='update';},'UNSUPPORTED_OPERATION'],
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

// Step 4 - Browser/Node parity and non-mutating diff contract.
test('共有Diff: ブラウザとNodeで同一のExpected／Actual結果', async()=>{
 const browser={structuredClone};
 vm.runInNewContext(await fs.readFile(path.join(root,'wwwroot/js/services/changeset/change_diff.js'),'utf8'),{window:browser,structuredClone});
 const before={title:'demo',items:[{item_id:'one',title:'old'}]};
 const after={title:'demo',items:[{item_id:'one',title:'new'},{item_id:'two',title:'追加'}]};
 const original=structuredClone(before);
 const expected=[{op:'add',path:'/items/1',value:after.items[1]}];
 const nodeActual=sharedDiff.compareDiff(before,after);
 const browserActual=browser.FrbStudioChangeDiff.compareDiff(before,after);
 assert.deepEqual(JSON.parse(JSON.stringify(browserActual)),nodeActual);
 assert.deepEqual(JSON.parse(JSON.stringify(browser.FrbStudioChangeDiff.compareExpectedActual(expected,browserActual))),sharedDiff.compareExpectedActual(expected,nodeActual));
 assert.deepEqual(sharedDiff.compareExpectedActual(expected,nodeActual).map(d=>d.path),['/items/0/title']);
 assert.deepEqual(before,original);
});
test('共有Diff: 不足Expected、変更の種別、キー順序、JSON Pointer',()=>{
 assert.deepEqual(sharedDiff.compareExpectedActual([{op:'add',path:'/items/1',value:{a:1}}],[]).map(d=>d.op),['missing_expected']);
 assert.equal(sharedDiff.compareExpectedActual([{op:'add',path:'/x',value:{a:1,b:2}}],[{op:'add',path:'/x',value:{b:2,a:1}}]).length,0);
 assert.equal(sharedDiff.compareExpectedActual([{op:'add',path:'/x',value:1}],[{op:'replace',path:'/x',value:1}]).length,2);
 assert.deepEqual(sharedDiff.compareDiff({'a/b~c':1},{'a/b~c':2}).map(x=>x.path),['/a~1b~0c']);
});
test('ブラウザ／ポータブル配布双方が共有Diffを参照する', async()=>{
 const page=await fs.readFile(path.join(root,'wwwroot/index.html'),'utf8');
 const portable=await fs.readFile(path.join(root,'tools/change_core/prepare_portable.ps1'),'utf8');
 const bridge=page.indexOf('js/services/changeset/change_diff.js?');
 const detailSave=page.indexOf('js/runtime/detail_save.js?');
 assert.ok(bridge>=0&&detailSave>bridge,'ブラウザは保存処理より前に共通Diffライブラリをロードする');
 assert.ok(portable.includes("'wwwroot/js/services/changeset/change_diff.js'"));
});

// Step 5 - same acceptance decision for UI F12 and external CLI.
const sharedGate = require('../../wwwroot/js/services/changeset/change_gate.js');
test('共通Gate: ACCEPTと未宣言のみ許容／REJECT・UNRESOLVED・service不在を拒否',()=>{
 assert.equal(sharedGate.assessFieldValidation({status:'ACCEPT'}).accepted,true);
 assert.equal(sharedGate.assessFieldValidation({status:'SKIPPED',reason_code:'FIELD_DEFINITION_NOT_DECLARED'}).accepted,true);
 for(const x of [null,{}, {status:'REJECT'}, {status:'UNRESOLVED'}, {status:'SKIPPED',reason_code:'RUNTIME_VALIDATION_SERVICE_UNAVAILABLE'}]) {
  assert.equal(sharedGate.assessFieldValidation(x).accepted,false);
 }
});
test('共通Gate: ブラウザ/NodeでField Definition判定と差分判定が一致',async()=>{
 const win={FrbStudioChangeDiff:sharedDiff};
 vm.runInNewContext(await fs.readFile(path.join(root,'wwwroot/js/services/changeset/change_gate.js'),'utf8'),{window:win,structuredClone});
 for(const result of [
  {status:'ACCEPT'}, {status:'REJECT',blocking_checks:[{field_name:'title'}]},
  {status:'SKIPPED',reason_code:'FIELD_DEFINITION_NOT_DECLARED'},
  {status:'UNRESOLVED',reason_code:'MISSING_REGISTRY'}
 ]){
  assert.deepEqual(JSON.parse(JSON.stringify(win.FrbStudioChangeGate.assessFieldValidation(result))),sharedGate.assessFieldValidation(result));
 }
 const before={x:1,y:0},pending={x:2,y:0};
 assert.equal(sharedGate.assessRowCommit(before,pending,pending).accepted,true);
 const mismatch=sharedGate.assessRowCommit(before,pending,{x:2,y:99});
 assert.equal(mismatch.accepted,false);
 assert.deepEqual(mismatch.unexpected_diff.map(x=>x.path),['/row/y']);
 assert.deepEqual(JSON.parse(JSON.stringify(win.FrbStudioChangeGate.assessRowCommit(before,pending,{x:2,y:99}).unexpected_diff)),mismatch.unexpected_diff);
});
test('F12実経路: 共通Gateに従い正本反映／Field Definition拒否／Diff不一致でロールバック',async()=>{
 const statuses=[];
 const win={FrbStudioChangeGate:sharedGate};
 const context={
  window:win,document:{querySelectorAll:()=>[]},structuredClone,
  registerRenderer:()=>{},$ :()=>null,cloneData:structuredClone,
  setStatus:(message)=>statuses.push(message),
  studioTreeProtect:()=>{},studioTreeValidateKind:()=>true,
  gridDef:()=>({fields:[]}),queueRelatedGridAutoApply:()=>{},
  currentRows:[{title:'before',memo:'unchanged'}],selectedIndex:0,detailMode:'edit'
 };
 vm.createContext(context);
 vm.runInContext(await fs.readFile(path.join(root,'wwwroot/js/runtime/detail_save.js'),'utf8'),context,{filename:'detail_save.js'});
 // Mock only editor DOM draft collection and evaluator results; execute real F12 commit code.
 context.buildPendingDetailApplyRow=()=>({title:'after',memo:'unchanged'});
 context.validatePendingDetailApplyRow=()=>({status:'ACCEPT'});
 const original=context.currentRows[0];
 assert.equal(vm.runInContext('tryCommitCurrentDetailEdits()',context),true);
 assert.equal(context.currentRows[0],original,'canonical row identity must be retained');
 assert.equal(original.title,'after');
 context.buildPendingDetailApplyRow=()=>({title:'invalid',memo:'unchanged'});
 context.validatePendingDetailApplyRow=()=>({status:'REJECT',blocking_checks:[{field_name:'title'}]});
 context.reportRuntimeFieldDefinitionValidationFailure=()=>statuses.push('validation rejected');
 assert.equal(vm.runInContext('tryCommitCurrentDetailEdits()',context),false);
 assert.equal(original.title,'after');
 assert.ok(statuses.includes('validation rejected'));
 context.validatePendingDetailApplyRow=()=>({status:'ACCEPT'});
 win.FrbStudioChangeGate={...sharedGate,assessRowCommit:()=>({accepted:false})};
 assert.equal(vm.runInContext('tryCommitCurrentDetailEdits()',context),false);
 assert.equal(context.currentRows[0],original);
 assert.equal(original.title,'after');
 assert.ok(statuses.some(s=>s.includes('Expected / Actual Diff')));
});
test('F12新規追加: 不一致なら行数を戻し、既存行は残す',async()=>{
 const win={FrbStudioChangeGate:sharedGate};
 const ctx={window:win,document:{querySelectorAll:()=>[]},structuredClone,
  registerRenderer:()=>{},$ :()=>null,cloneData:structuredClone,
  setStatus:()=>{},studioTreeProtect:()=>{},assignNewRowKeys:()=>{},
  gridDef:()=>({fields:[]}),queueRelatedGridAutoApply:()=>{},
  currentRows:[{title:'existing'}],selectedIndex:0,detailMode:'new',draftRow:{title:'new'},
  applySearch:()=>{},renderGrid:()=>{},updateDetailNavButtons:()=>{},openDetail:()=>{}};
 vm.createContext(ctx);
 vm.runInContext(await fs.readFile(path.join(root,'wwwroot/js/runtime/detail_save.js'),'utf8'),ctx);
 ctx.openDetail=()=>{}; // do not render DOM in the isolated F12 harness
 ctx.buildPendingDetailApplyRow=()=>({title:'new'});
 ctx.validatePendingDetailApplyRow=()=>({status:'SKIPPED',reason_code:'FIELD_DEFINITION_NOT_DECLARED'});
 vm.runInContext('applyDetail()',ctx);
 assert.equal(ctx.currentRows.length,2);
 assert.equal(ctx.currentRows[1].title,'new');
 ctx.detailMode='new';ctx.draftRow={title:'another'};
 win.FrbStudioChangeGate={...sharedGate,assessRowCommit:()=>({accepted:false})};
 vm.runInContext('applyDetail()',ctx);
 assert.equal(ctx.currentRows.length,2);
 assert.equal(ctx.currentRows[0].title,'existing');
});
test('ブラウザ・ポータブル双方が共通Gateを読込／保存前',async()=>{
 const page=await fs.readFile(path.join(root,'wwwroot/index.html'),'utf8');
 const portable=await fs.readFile(path.join(root,'tools/change_core/prepare_portable.ps1'),'utf8');
 const diffIndex=page.indexOf('js/services/changeset/change_diff.js?');
 const gateIndex=page.indexOf('js/services/changeset/change_gate.js?');
 const detailIndex=page.indexOf('js/runtime/detail_save.js?');
 assert.ok(diffIndex>=0&&gateIndex>diffIndex&&detailIndex>gateIndex);
 assert.ok(portable.includes("'wwwroot/js/services/changeset/change_gate.js'"));
 const fieldSource=await fs.readFile(path.join(root,'tools/change_core/field_validation.mjs'),'utf8');
 assert.ok(fieldSource.includes('assessFieldValidation(result)'));
});

// studio_work_0269 Step 6 - Delete / cascade support.
const deleteRequest=(id,group='work',cascade=true,mode='dry_run')=>({
  ...request([record('unused')],mode),
  operations:[{operation:'delete',section_id:'items',targets:[{id,group_id:group}],cascade}]
});
const treeDocument=()=>({title:'tree',pages:[{page_id:'work',title:'work'},{page_id:'other',title:'other'}],
  items:[
    {item_id:'folders',parent_item_id:'',page_id:'work',sort_order:10,title:'Files',item_kind:'category'},
    {item_id:'cat',parent_item_id:'folders',page_id:'work',sort_order:10,title:'カテゴリ',item_kind:'category'},
    {item_id:'sub',parent_item_id:'cat',page_id:'work',sort_order:10,title:'下位',item_kind:'category'},
    {item_id:'leaf',parent_item_id:'sub',page_id:'work',sort_order:10,title:'日本語',item_kind:'command'},
    {item_id:'dir',parent_item_id:'cat',page_id:'work',sort_order:20,title:'実フォルダー',item_kind:'directory'},
    {item_id:'other',parent_item_id:'folders',page_id:'work',sort_order:20,title:'生存',item_kind:'command'},
    {item_id:'other-group',parent_item_id:'',page_id:'other',sort_order:10,title:'別Page',item_kind:'category'}
  ],unrelated:{note:'変更禁止'}});
test('Delete cascade: descendants only, sibling and unrelated fields unchanged',()=>{
 const before=treeDocument();const copy=structuredClone(before);
 const ret=evaluateChangeSet(before,deleteRequest('cat'),view);
 assert.equal(ret.summary.deleted,4);assert.equal(ret.summary.added,0);
 assert.deepEqual(ret.after.items.map(r=>r.item_id),['folders','other','other-group']);
 assert.deepEqual(ret.after.unrelated,before.unrelated);
 assert.deepEqual(before,copy);
 assert.deepEqual(ret.expected_diff,ret.actual_diff);
 assert.deepEqual(ret.unexpected_diff,[]);
});
test('Delete one leaf; only the specified record disappears',()=>{
 const ret=evaluateChangeSet(treeDocument(),deleteRequest('leaf'),view);
 assert.equal(ret.summary.deleted,1);
 assert.ok(ret.after.items.some(r=>r.item_id==='sub'));
 assert.ok(!ret.after.items.some(r=>r.item_id==='leaf'));
});
test('Delete rejects ambiguous, missing, wrong-group, and non-cascade parent targets',()=>{
 for(const [mutation,code] of [
  [r=>{r.operations[0].cascade=false;},'CHILDREN_EXIST'],
  [r=>{r.operations[0].targets[0].id='missing';},'TARGET_NOT_FOUND'],
  [r=>{r.operations[0].targets[0].group_id='other';},'GROUP_MISMATCH'],
  [r=>{r.operations[0].targets[0].group_id='';},'GROUP_REQUIRED'],
  [r=>{r.operations[0].targets.push(r.operations[0].targets[0]);},'DUPLICATE_TARGET']
 ]){const r=deleteRequest('cat');mutation(r);assert.throws(()=>evaluateChangeSet(treeDocument(),r,view),e=>e.code===code,code);}
});
test('Delete CLI: dry_run unchanged, cascade commit, stale SHA rejects repeat',async t=>{
 const {doc,config}=await sandbox(t);
 const before=treeDocument();await fs.writeFile(doc,JSON.stringify(before,null,2),'utf8');
 const snapshot=await readSnapshot(doc);
 const r=deleteRequest('cat');r.base_sha256=snapshot.sha256;
 const preview=cli(config,r);assert.equal(preview.code,0);
 assert.equal(preview.result.status,'PREVIEW');assert.equal(preview.result.summary.deleted,4);
 assert.equal((await readSnapshot(doc)).sha256,snapshot.sha256);
 r.mode='commit';const committed=cli(config,r);assert.equal(committed.code,0);
 assert.equal(committed.result.status,'COMMITTED');assert.equal(committed.result.saved,true);
 assert.equal((await readSnapshot(doc)).document.items.length,3);
 assert.deepEqual(committed.result.expected_diff,preview.result.expected_diff);
 assert.equal(cli(config,r).result.status,'CONFLICT');
});
test('Delete multiple target roots in same operation is atomic',()=>{
 const r=deleteRequest('cat');r.operations[0].targets.push({id:'other',group_id:'work'});
 const ret=evaluateChangeSet(treeDocument(),r,view);
 assert.equal(ret.summary.deleted,5);
 assert.deepEqual(ret.after.items.map(x=>x.item_id),['folders','other-group']);
});
test('Delete Actual/Expected mismatch is rejected',()=>{
 const r=deleteRequest('cat');
 assert.throws(()=>evaluateChangeSet(treeDocument(),r,view,{actualExecutor:before=>before}),e=>e.code==='UNEXPECTED_DIFF');
});
