// studio_work_0269 / studio-external-changeset-core-v0_1
// Pure ChangeSet planner/executor: neither application-specific keys nor file IO.
import { randomUUID } from 'node:crypto';
import { createRequire } from 'node:module';
const require = createRequire(import.meta.url);
const StudioTreeModel = require('../../wwwroot/js/runtime/tree_model.js');

export class ChangeSetError extends Error {
  constructor(code, message) { super(message); this.code=code; }
}
const fail=(code,message)=>{throw new ChangeSetError(code,message);};
// One browser/Node diff contract; keep Expected/Actual comparison independent of the executor.
const { compareDiff } = require('../../wwwroot/js/services/changeset/change_diff.js');
const { assessExpectedActual } = require('../../wwwroot/js/services/changeset/change_gate.js');
const clone=value=>structuredClone(value);
const pointerPart=value=>String(value).replaceAll("~","~0").replaceAll("/","~1");
const object=value=>value && typeof value==='object' && !Array.isArray(value);
export { compareDiff };
function resolveArray(document,dataPath){
  if(!/^\$\.[a-zA-Z_][\w]*$/.test(dataPath||''))fail('UNSUPPORTED_DATA_PATH','v0.1 supports a top-level JSON array dataPath only');
  const key=dataPath.slice(2), rows=document?.[key];
  if(!Array.isArray(rows))fail('INVALID_DOCUMENT',`対象配列が存在しません: ${dataPath}`);
  return {key,rows};
}
function validateTree(rows,cfg){
  try {StudioTreeModel.build(rows,cfg);}catch(e){fail('TREE_INVALID',e.message);}
  if(cfg.parentKindField){
    const ids=new Map(rows.map(r=>[String(r[cfg.idField]??''),r]));
    for(const row of rows){const p=String(row[cfg.parentField]??'');if(p && !cfg.parentKinds?.includes(ids.get(p)?.[cfg.parentKindField]))fail('PARENT_KIND_INVALID',`親項目が子を持てません: ${p}`);}
  }
}
function getGroupIds(document, cfg){
  if(!cfg.groupField || !cfg.groupSource)return null;
  const {rows}=resolveArray(document,cfg.groupSource);
  return new Set(rows.map(r=>String(r[cfg.groupIdField]??'')));
}
const safeId=v=>typeof v==='string' && v.trim().length>0;
function planChangeSet(document, request, view, createId){
  if(!object(document))fail('INVALID_DOCUMENT','JSON文書はオブジェクトが必要です');
  if(request?.schema_version!=='studio_changeset_v0_1')fail('INVALID_SCHEMA','ChangeSet Schemaが不正です');
  if(!['dry_run','commit'].includes(request.mode))fail('INVALID_MODE','mode は dry_run または commit');
  if(!Array.isArray(request.operations)||!request.operations.length)fail('INVALID_OPERATIONS','operations[] が必要です');
  const sections=view.sections||[];
  const pending=new Map();
  const planned=[];
  for(const op of request.operations){
    if(op?.operation!=='add')fail('UNSUPPORTED_OPERATION',`v0.1ではaddだけをサポート: ${op?.operation}`);
    const section=sections.find(s=>s.id===op.section_id&&s.type==='grid');
    if(!section)fail('SECTION_NOT_FOUND',`Gridが見つかりません: ${op.section_id}`);
    const {key,rows}=resolveArray(document,section.dataPath);
    if(!pending.has(key))pending.set(key,clone(rows));
    const updated=pending.get(key), cfg=section.tree?.enabled?section.tree:null;
    if(!Array.isArray(op.records)||!op.records.length||!op.records.every(object))fail('INVALID_RECORDS','records[] は1件以上のJSONオブジェクトが必要です');
    const placement=op.placement??{};
    if(!object(placement) || (placement.position??'end')!=='end')fail('UNSUPPORTED_PLACEMENT','v0.1ではposition=endのみ対応');
    if(cfg){
      validateTree(updated,cfg);
      const parent=String(placement.parent_id??'');
      const nodes=new Map(updated.map(row=>[String(row[cfg.idField]),row]));
      const p=parent?nodes.get(parent):null;
      if(parent && !p)fail('PARENT_NOT_FOUND',`親が見つかりません: ${parent}`);
      if(p && cfg.parentKindField && !cfg.parentKinds?.includes(p[cfg.parentKindField]))fail('PARENT_KIND_INVALID',`子を追加できない親: ${parent}`);
      const group=p?String(p[cfg.groupField]??''):String(placement.group_id??'');
      if(cfg.groupField){
        if(!group)fail('GROUP_REQUIRED','group_idが必要です');
        if(placement.group_id!=null && String(placement.group_id)!==group)fail('GROUP_MISMATCH','指定したgroup_idと親グループが一致しません');
        const groups=getGroupIds(document,cfg);
        if(groups && !groups.has(group))fail('GROUP_NOT_FOUND',`指定グループが存在しません: ${group}`);
      }
      const peers=updated.filter(r=>String(r[cfg.parentField]??'')===parent && (!cfg.groupField || String(r[cfg.groupField]??'')===group));
      let nextOrder=peers.reduce((n,r)=>Math.max(n,Number(r[cfg.orderField])||0),0);
      const seen=new Set(updated.map(r=>String(r[cfg.idField])));
      for(const record of op.records){
        const row=clone(record);
        // Placement metadata is authoritative; reject ambiguous conflicting data.
        for(const [field,value] of [[cfg.parentField,parent],...(cfg.groupField?[[cfg.groupField,group]]:[])]){
          if(Object.hasOwn(row,field) && String(row[field]??'')!==String(value))fail('PLACEMENT_CONFLICT',`レコードの${field}がplacementと不一致`);
          row[field]=value;
        }
        if(!safeId(row[cfg.idField]))row[cfg.idField]=createId();
        if(seen.has(String(row[cfg.idField])))fail('DUPLICATE_ID',`ID重複: ${row[cfg.idField]}`);
        seen.add(String(row[cfg.idField]));
        nextOrder+=10;
        row[cfg.orderField]=nextOrder;
        planned.push({key,index:updated.length,row});
        updated.push(row);
      }
      validateTree(updated,cfg);
    }else{
      const seen=new Set(section.keyField?updated.map(r=>String(r[section.keyField])):[]);
      for(const record of op.records){
        const row=clone(record);
        if(section.keyField){
          if(!safeId(row[section.keyField]))row[section.keyField]=createId();
          if(seen.has(String(row[section.keyField])))fail('DUPLICATE_ID',`ID重複: ${row[section.keyField]}`);
          seen.add(String(row[section.keyField]));
        }
        planned.push({key,index:updated.length,row});updated.push(row);
      }
    }
  }
  return {planned,pending};
}
// The expectation is declared as an immutable append-only list of allowed changed paths.
function expectedFromPlan(planned){
  return planned.map(item=>({op:'add',path:`/${pointerPart(item.key)}/${item.index}`,value:clone(item.row)}));
}
function executePlan(before,planned){
  const after=clone(before);
  for(const item of planned){
    if(!Array.isArray(after[item.key]) || after[item.key].length!==item.index)fail('APPLY_MISMATCH','適用時の行位置が計画と一致しません');
    after[item.key].push(clone(item.row));
  }
  return after;
}
export function evaluateChangeSet(document,request,view,options={}) {
  const createId=options.createId??randomUUID;
  const plan=planChangeSet(document,request,view,createId);
  const expectedDiff=expectedFromPlan(plan.planned);
  // Actual is obtained from applying the planned operations to an independent deep copy.
  const after=(options.actualExecutor??executePlan)(document,plan.planned);
  const actualDiff=compareDiff(document,after);
  const { unexpected_diff: unexpectedDiff }=assessExpectedActual(expectedDiff,actualDiff);
  if(unexpectedDiff.length)fail('UNEXPECTED_DIFF','Expected DiffとActual Diffが一致しません');
  return {after,expected_diff:expectedDiff,actual_diff:actualDiff,unexpected_diff:[],summary:{added:plan.planned.length,changed_existing:0}};
}
