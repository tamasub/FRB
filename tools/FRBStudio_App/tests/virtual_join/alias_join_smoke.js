'use strict';
const fs=require('fs'),vm=require('vm'),assert=require('assert'),path=require('path');
const root=path.resolve(__dirname,'../..');
const globalObj={console,structuredClone, Map, Set, Object, String, JSON};
vm.createContext(globalObj);
function load(rel){ vm.runInContext(fs.readFileSync(path.join(root,'wwwroot/js',rel),'utf8'),globalObj,{filename:rel}); }
load('core/data_utils.js');
// VirtualData builder registry uses a standalone mocked registry primitive.
vm.runInContext(`function createNamedRegistry(){const m=new Map();return {register:(name,fn)=>m.set(name,fn),get:(name)=>m.get(name)}}`,globalObj);
load('virtualData/virtual_data_registry.js');
load('virtualData/join_builders.js');
load('virtualData/join_writeback.js');
const catalog=JSON.parse(fs.readFileSync('/mnt/data/apps_cache.json','utf-8'));
const config=JSON.parse(fs.readFileSync(path.join(root,'defs/launch/frb_launch_maintenance_view_def_v0_1.json'),'utf8'));
const s={app_aliases:[{kind:'aumid',target:'Microsoft.Office.EXCEL.EXE.15',alias:'エクセル'}]};
function build(){return globalObj.buildVirtualDatasetByConfig({config:config.virtualData,dataObj:s,sources:{apps_cache:catalog}})}
let rows=build();assert(rows.length>=150);
const virtualHolder={items:[]};
globalObj.setVirtualByPath(virtualHolder,'$.app_alias_catalog_view',rows);
assert.equal(globalObj.getByPath(virtualHolder,'$.app_alias_catalog_view').length, rows.length);
assert(!JSON.stringify(virtualHolder).includes('app_alias_catalog_view'), 'virtual grid must not leak into saved document');
assert(rows.find(r=>r.name==='Excel').alias==='エクセル');
const baseline=JSON.parse(JSON.stringify(rows));
// New alias insertion + update Excel + deletion removing existing row
rows.find(r=>r.name==='Excel').alias='表計算 エクセル';
rows.find(r=>r.name==='Arduino IDE').alias='アルドゥイーノ';
let plan=globalObj.planVirtualJoinWriteBack(config.virtualData,rows,baseline,k=>k==='$current'?s:null);
assert(plan.operations.some(o=>o.op==='insert'));assert(plan.operations.some(o=>o.op==='update'));
assert(globalObj.applyVirtualJoinWriteBackPlan(plan,k=>s)>0);
assert(s.app_aliases.length===2);assert(s.app_aliases.some(x=>x.alias==='アルドゥイーノ'));
rows=build();const baseline2=JSON.parse(JSON.stringify(rows));
rows.find(r=>r.name==='Excel').alias='';
plan=globalObj.planVirtualJoinWriteBack(config.virtualData,rows,baseline2,k=>s);
assert(plan.operations.some(o=>o.op==='delete'));
globalObj.applyVirtualJoinWriteBackPlan(plan,k=>s);
assert(s.app_aliases.length===1);
rows=build();let baseline3=JSON.parse(JSON.stringify(rows));
assert.equal(globalObj.planVirtualJoinWriteBack(config.virtualData,rows,baseline3,k=>s).operations.length,0);
// Orphan alias preserved while absent from catalog
const orphan={kind:'aumid',target:'removed.app',alias:'孤立'};
s.app_aliases.push(orphan); rows=build();baseline3=JSON.parse(JSON.stringify(rows));
assert(!rows.some(x=>x.target==='removed.app'));
assert(globalObj.planVirtualJoinWriteBack(config.virtualData,rows,baseline3,k=>s).operations.length===0);
assert(s.app_aliases.includes(orphan));
// Detect edited row identity / duplicate rows
const bad=JSON.parse(JSON.stringify(rows));bad[0].target='forged.app';
assert.throws(()=>globalObj.planVirtualJoinWriteBack(config.virtualData,bad,baseline3,k=>s));
assert.deepEqual(Object.keys(s.app_aliases[0]).sort(),['kind','target','alias'].sort());
console.log('JOIN/WriteBack tests PASS, catalog rows:',rows.length,'alias rows:',s.app_aliases.length);

// Verify the external JSON adapter passes exactly the configured path to the native bridge.
(async()=>{
 const doc={};
 let invoked;
 globalObj.window={FRBStudioNativeHost:{isAvailable:()=>true,invoke:async (cmd,args)=>{invoked={cmd,args};return {document:catalog};}}};
 const result=await globalObj.loadDataSourceJson(config.dataSources.apps_cache,'apps_cache',doc);
 assert.equal(result.apps.length,catalog.apps.length);
 assert.equal(invoked.cmd,'dataSource.readOnlyJson');
 assert.equal(doc.app_catalog.cache_path,config.dataSources.apps_cache.defaultPath);
 assert.equal(invoked.args.path,doc.app_catalog.cache_path);
 console.log('Native read-only adapter contract PASS');
})().catch(error=>{console.error(error);process.exitCode=1});
