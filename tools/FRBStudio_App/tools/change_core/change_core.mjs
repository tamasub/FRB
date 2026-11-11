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
    if(!['add','delete'].includes(op?.operation))fail('UNSUPPORTED_OPERATION',`未対応の操作: ${op?.operation}`);
    const section=sections.find(s=>s.id===op.section_id&&s.type==='grid');
    if(!section)fail('SECTION_NOT_FOUND',`Gridが見つかりません: ${op.section_id}`);
    const {key,rows}=resolveArray(document,section.dataPath);
    if(!pending.has(key))pending.set(key,clone(rows));
    const updated=pending.get(key), cfg=section.tree?.enabled?section.tree:null;
    if(op.operation==='delete'){
      if(!Array.isArray(op.targets)||!op.targets.length||!op.targets.every(object))
        fail('INVALID_TARGETS','delete.targets[] は1件以上の対象指定が必要です');
      const idField=cfg?.idField??section.keyField;
      if(!idField)fail('DELETE_KEY_REQUIRED','削除対象の一意ID定義が必要です');
      if(cfg)validateTree(updated,cfg);
      const selected=new Set();
      const rowsById=new Map(updated.map(row=>[String(row[idField]??''),row]));
      for(const target of op.targets){
        const id=target.id;
        if(!safeId(id))fail('INVALID_TARGETS','削除対象idが不正です');
        const row=rowsById.get(id);
        if(!row)fail('TARGET_NOT_FOUND',`削除対象が見つかりません: ${id}`);
        if(cfg?.groupField){
          if(!safeId(target.group_id))fail('GROUP_REQUIRED','削除対象のgroup_idが必要です');
          if(String(row[cfg.groupField]??'')!==target.group_id)
            fail('GROUP_MISMATCH',`指定されたgroup_idが対象と一致しません: ${id}`);
        }
        if(selected.has(id))fail('DUPLICATE_TARGET',`削除対象の重複: ${id}`);
        selected.add(id);
      }
      const toDelete=new Set(selected);
      if(cfg){
        // Descendants are resolved only from the canonical JSON tree, never
        // from displayed filesystem children or runtime-generated menu rows.
        let changed=true;
        while(changed){
          changed=false;
          for(const row of updated){
            const id=String(row[idField]??'');
            if(toDelete.has(String(row[cfg.parentField]??'')) && !toDelete.has(id)){
              toDelete.add(id);changed=true;
            }
          }
        }
        if(op.cascade!==true && toDelete.size!==selected.size)
          fail('CHILDREN_EXIST','子アイテムが存在します。配下一括削除にはcascade=trueが必要です');
      }else if(op.cascade===true){
        fail('CASCADE_REQUIRES_TREE','cascade=trueはTree定義のあるSectionのみ利用できます');
      }
      const ids=[...toDelete];
      pending.set(key,updated.filter(row=>!toDelete.has(String(row[idField]??''))));
      planned.push({kind:'delete',key,idField,ids});
      if(cfg)validateTree(pending.get(key),cfg);
      continue;
    }
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
        planned.push({kind:'add',key,index:updated.length,row});
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
        planned.push({kind:'add',key,index:updated.length,row});updated.push(row);
      }
    }
  }
  return {planned,pending};
}
// The expected document is built solely from validated planned rows. For
// deletions, JSON array compaction produces indexed replace/remove diffs;
// that is an array representation effect, not an edit of surviving records.
function expectedFromPlan(before,pending){
  const expected=clone(before);
  for(const [key,rows] of pending)expected[key]=clone(rows);
  return compareDiff(before,expected);
}
function executePlan(before,planned){
  const after=clone(before);
  for(const item of planned){
    if(item.kind==='delete'){
      const ids=new Set(item.ids);
      const original=after[item.key];
      if(!Array.isArray(original))fail('APPLY_MISMATCH','適用対象配列が存在しません');
      after[item.key]=original.filter(row=>!ids.has(String(row[item.idField]??'')));
      if(original.length-after[item.key].length!==ids.size)
        fail('APPLY_MISMATCH','削除対象の件数が計画と一致しません');
    }else{
      if(!Array.isArray(after[item.key]) || after[item.key].length!==item.index)
        fail('APPLY_MISMATCH','適用時の行位置が計画と一致しません');
      after[item.key].push(clone(item.row));
    }
  }
  return after;
}
export function evaluateChangeSet(document,request,view,options={}) {
  const createId=options.createId??randomUUID;
  const plan=planChangeSet(document,request,view,createId);
  const expectedDiff=expectedFromPlan(document,plan.pending);
  // Actual is obtained from applying the planned operations to an independent deep copy.
  const after=(options.actualExecutor??executePlan)(document,plan.planned);
  const actualDiff=compareDiff(document,after);
  const { unexpected_diff: unexpectedDiff }=assessExpectedActual(expectedDiff,actualDiff);
  if(unexpectedDiff.length)fail('UNEXPECTED_DIFF','Expected DiffとActual Diffが一致しません');
  return {after,expected_diff:expectedDiff,actual_diff:actualDiff,unexpected_diff:[],summary:{added:plan.planned.filter(p=>p.kind==='add').length,deleted:plan.planned.filter(p=>p.kind==='delete').reduce((n,p)=>n+p.ids.length,0),changed_existing:0}};
}
