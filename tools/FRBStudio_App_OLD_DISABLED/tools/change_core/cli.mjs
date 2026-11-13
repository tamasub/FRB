#!/usr/bin/env node
// Invocation: node tools/change_core/cli.mjs --config <trusted-config.json> < request.json
// stdout is a single result JSON; stderr is reserved for unexpected runtime diagnostics.
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {evaluateChangeSet,ChangeSetError} from './change_core.mjs';
import {sha256,readSnapshot,commitDocument} from './storage.mjs';
import {buildFieldValidator} from './field_validation.mjs';
const root=fileURLToPath(new URL('../../',import.meta.url));
const isObject=v=>v!==null&&typeof v==='object'&&!Array.isArray(v);
async function stdinText(){let str='';for await(const chunk of process.stdin){str+=chunk;if(str.length>8*1024*1024)throw new ChangeSetError('REQUEST_TOO_LARGE','Request exceeds 8MiB');}return str;}
function errorResult(request,code,message){return {schema_version:'studio_changeset_result_v0_1',request_id:request?.request_id??null,status:['CONFLICT','LOCKED'].includes(code)?'CONFLICT':(['ERROR','EACCES','EPERM','ENOENT','EISDIR','INVALID_JSON'].includes(code)?'ERROR':'REJECTED'),saved:false,summary:{added:0,deleted:0,changed_existing:0,moved:0},expected_diff:[],actual_diff:[],unexpected_diff:[],errors:[{code,message}]};}
async function run(){
  const request=JSON.parse(await stdinText());
  try{
    const index=process.argv.indexOf('--config');
    if(index<0||!process.argv[index+1])throw new ChangeSetError('CONFIG_REQUIRED','信頼済みconfigの--config指定が必要です');
    const config=JSON.parse(await fs.readFile(path.resolve(process.argv[index+1]),'utf8'));
    if(config.schema_version!=='studio_change_core_config_v0_1'||!isObject(config.documents))throw new ChangeSetError('INVALID_CONFIG','Config契約が不正です');
    if(typeof request.document_ref!=='string'||!Object.hasOwn(config.documents,request.document_ref))throw new ChangeSetError('DOCUMENT_NOT_ALLOWED','未登録document_refへの書き込みは許可しません');
    const documentConfig=config.documents[request.document_ref];
    if(!isObject(documentConfig)||typeof documentConfig.path!=='string'||!path.isAbsolute(documentConfig.path))throw new ChangeSetError('INVALID_CONFIG','対象ファイルは絶対パスで明示してください');
    const viewRef=String(documentConfig.view_def??'').replaceAll('\\','/');
    if(!/^[\w\-/]+\.json$/.test(viewRef) || viewRef.split('/').includes('..'))throw new ChangeSetError('INVALID_VIEW_DEF','信頼済みViewDef参照が不正です');
    for(const [field,v] of [['view_def',viewRef],['view_id',documentConfig.view_id]]){
      if(request[field]!==v)throw new ChangeSetError('VIEW_MISMATCH',`${field}は許可済み設定と一致する必要があります`);
    }
    const viewDef=JSON.parse(await fs.readFile(path.join(root,'defs',viewRef),'utf8'));
    const view=viewDef.views?.find(v=>v.id===request.view_id);
    if(!view)throw new ChangeSetError('VIEW_NOT_FOUND','Viewがありません');
    const sections=new Set(documentConfig.section_ids??[]);
    if(!sections.size||request.operations?.some(op=>!sections.has(op?.section_id)))throw new ChangeSetError('SECTION_NOT_ALLOWED','操作対象Sectionが許可されていません');
    if(typeof request.base_sha256!=='string'||!/^[a-f0-9]{64}$/.test(request.base_sha256))throw new ChangeSetError('BASE_SHA_REQUIRED','基準SHA-256が必要です');
    const filename=path.resolve(documentConfig.path);
    const snapshot=await readSnapshot(filename);
    if(snapshot.sha256!==request.base_sha256)throw new ChangeSetError('CONFLICT','読込時点ですでに競合しています');
    const field=await buildFieldValidator(root,viewDef);
    const evaluation=evaluateChangeSet(snapshot.document,request,view);
    // Validate complete post-change records for both Add and Update. A diff
    // fragment is NOT a record and must never be passed to Field Definition.
    for(const target of evaluation.validation_rows){
      const section=view.sections.find(s=>s.id===target.section_id&&s.type==='grid');
      if(!section)throw new ChangeSetError('SECTION_NOT_FOUND','検証対象Sectionがありません');
      field.validate(target.row,section);
    }
    const result={schema_version:'studio_changeset_result_v0_1',request_id:request.request_id??null,status:'PREVIEW',saved:false,base_sha256:snapshot.sha256,new_sha256:null,validation_mode:field.mode,summary:evaluation.summary,expected_diff:evaluation.expected_diff,actual_diff:evaluation.actual_diff,unexpected_diff:evaluation.unexpected_diff,errors:[]};
    if(request.mode==='commit'){
      const json=JSON.stringify(evaluation.after,null,2)+'\n';
      const saved=await commitDocument(filename,snapshot.sha256,json);
      result.status='COMMITTED';result.saved=true;result.new_sha256=saved.sha256;
    }
    return result;
  }catch(e){if(e instanceof SyntaxError)throw e;return errorResult(request,e?.code??'ERROR',e.message);}
}
let result;
try{result=await run();}catch(e){result=errorResult(null,e instanceof SyntaxError?'INVALID_JSON':(e?.code??'ERROR'),e.message);}
process.stdout.write(JSON.stringify(result,null,2)+'\n');
if(result.errors.length)process.exitCode=1;
