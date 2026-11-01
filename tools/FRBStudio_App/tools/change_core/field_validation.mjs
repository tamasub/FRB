// Load the existing DOM-free Studio Definition services unchanged into a Node VM.
// Runs source from the installed Studio app, never source from a ChangeSet request.
import fs from 'node:fs/promises';
import path from 'node:path';
import vm from 'node:vm';
import {ChangeSetError} from './change_core.mjs';
export async function buildFieldValidator(appRoot, viewDef){
  const ref=viewDef.item_definition_ref??viewDef.itemDefinitionRef;
  if(!ref)return {validate:()=>{},mode:'SKIPPED_FIELD_DEFINITION_NOT_DECLARED'};
  if(!/^[\w\-/]+\.json$/.test(ref) || ref.split('/').includes('..'))throw new ChangeSetError('INVALID_FIELDDEF_REF','Field Definition参照が不正です');
  const doc=JSON.parse(await fs.readFile(path.join(appRoot,'fielddefs',ref),'utf8'));
  const registry=JSON.parse(await fs.readFile(path.join(appRoot,'data/json/config/validation_type_registry_v0_1.json'),'utf8'));
  if(doc.document_type!=='field_definition'||!Array.isArray(doc.field_definitions)||registry.document_type!=='validation_type_registry')throw new ChangeSetError('INVALID_FIELD_DEFINITION','Field Definition/Registry契約が不正です');
  const context=vm.createContext({});
  for(const file of ['definition_verification_common.js','field_contract_resolver.js','definition_value_validator.js','runtime_field_definition_validation.js']){
    const src=await fs.readFile(path.join(appRoot,'wwwroot/js/services/definition',file),'utf8');
    vm.runInContext(src,context,{filename:file,timeout:3000});
  }
  const service=vm.runInContext('new RuntimeFieldDefinitionValidationService()',context);
  return {
    mode:'STUDIO_RUNTIME_FIELD_DEFINITION',
    validate:(record,section)=>{
      const result=service.validateRow({row:record,gridDef:section,fieldDefinitionDocument:doc,registry});
      if(result.status!=='ACCEPT')throw new ChangeSetError('FIELD_DEFINITION_REJECTED',`Field Definition検証が失敗: ${JSON.stringify(result.blocking_checks.map(c=>({field:c.field_name,reason:c.validation?.reason_code})))}`);
    }
  };
}
