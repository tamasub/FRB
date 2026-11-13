// File paths are obtained from NativeShell's actual dropped DOM File objects.
function studioTreeDropDestination(element) {
 const c=studioTreeConfig();if(!c?.fileDrop?.enabled)throw Error('このグリッドはファイル登録に対応していません');
 if(studioTreeReadonly())throw Error('読み取り専用です');
 const tr=element?.closest?.('#dataGrid tr'),model=studioTreeModel(),state=studioTreeState();
 let group=tr?.dataset.groupId,entry;
 if(group==null&&tr?.dataset.sourceIndex!=null)entry=model.nodes[Number(tr.dataset.sourceIndex)];
 if(!tr){if(state.selectedGroup!=null)group=state.selectedGroup;else entry=model.nodes[selectedIndex];}
 if(group!=null)return {group,parent:null,after:null,label:studioTreeGroups(c).get(group)||group};
 if(!entry)throw Error('Pageまたはカテゴリーの行へドロップしてください');
 const isParent=c.parentKindField?c.parentKinds.includes(entry.row[c.parentKindField]):true;
 const parent=isParent?entry:entry.parent;
 return {group:entry.row[c.groupField],parent:parent?.row[c.idField]??'',after:isParent?null:entry.row[c.idField],label:parent?studioTreeLabel(parent,c):studioTreeGroups(c).get(String(entry.row[c.groupField]))};
}
function studioTreeDropTemplate(value,file){
 if(typeof value==='string')return value.replace(/\{(path|launchPath|name)\}/g,(_,key)=>key==='launchPath'?file.path.replace(/%/g,'%%'):file[key]);
 if(Array.isArray(value))return value.map(v=>studioTreeDropTemplate(v,file));
 if(value&&typeof value==='object')return Object.fromEntries(Object.entries(value).map(([k,v])=>[k,studioTreeDropTemplate(v,file)]));
 return value;
}
function studioTreeInsertDropped(files,destination){
 const c=studioTreeConfig(),cfg=c.fileDrop;if(studioTreeReadonly())throw Error('読み取り専用です');
 studioTreeModel();
 if(!Array.isArray(files)||!files.length)throw Error('ファイルがありません');
 const unique=new Map();files.forEach(f=>{if(!f.path||!f.name||!['file','directory'].includes(f.kind))throw Error('ファイルの種類またはパスを取得できません');unique.set(f.path.toLowerCase(),f);});
 if(!studioTreeGroups(c).has(String(destination.group)))throw Error('追加先Pageが見つかりません');
 if(destination.parent&&!currentRows.some(r=>r[c.idField]===destination.parent&&(!c.groupField||r[c.groupField]===destination.group)&&(!c.parentKindField||c.parentKinds.includes(r[c.parentKindField]))))throw Error('追加先が変更されました');
 const rows=[...unique.values()].map(f=>{const row=createDefaultRow();Object.assign(row,studioTreeDropTemplate(f.kind==='directory'?cfg.directoryTemplate:cfg.fileTemplate,f));row[c.parentField]=destination.parent||'';if(c.groupField)row[c.groupField]=destination.group;return row;});
 const peers=currentRows.filter(r=>String(r[c.parentField]??'')===String(destination.parent||'')&&(!c.groupField||r[c.groupField]===destination.group)).sort((a,b)=>(Number(a[c.orderField])||0)-(Number(b[c.orderField])||0));
 const at=destination.after?peers.findIndex(r=>r[c.idField]===destination.after)+1:peers.length;peers.splice(at,0,...rows);
 // All staging/validation above completes before any existing row changes.
 peers.forEach((r,i)=>r[c.orderField]=(i+1)*10);currentRows.push(...rows);
 const state=studioTreeState();state.collapsed.delete('group:'+destination.group);if(destination.parent)state.collapsed.delete(String(destination.parent));state.selectedGroup=null;
 selectedIndex=currentRows.length-rows.length;applySearch();
 setStatus(`${rows.length}件を ${destination.label} に追加しました。JSONを保存するとLaunchへ反映されます。`,{kind:'success',toast:false});return rows;
}
function studioTreeInstallFileDrop(){
 const grid=$('dataGrid');if(!grid||grid.dataset.fileDropBound==='true')return;grid.dataset.fileDropBound='true';
 let active;
 const clear=()=>{active?.style.removeProperty('outline');active=null;};
 const hasFiles=e=>[...(e.dataTransfer?.types??[])].includes('Files');
 grid.addEventListener('dragover',e=>{
  if(!hasFiles(e)||!studioTreeConfig()?.fileDrop?.enabled)return;e.preventDefault();e.stopPropagation();
  try{const dest=studioTreeDropDestination(e.target);e.dataTransfer.dropEffect='copy';clear();active=e.target.closest('tr')||grid;active.style.outline='2px solid #6ba7ff';active.title='追加先: '+dest.label;}catch{e.dataTransfer.dropEffect='none';clear();}
 });
 grid.addEventListener('dragleave',e=>{if(!grid.contains(e.relatedTarget))clear();});
 grid.addEventListener('drop',async e=>{
  if(!hasFiles(e)||!studioTreeConfig()?.fileDrop?.enabled)return;e.preventDefault();e.stopImmediatePropagation();clear();
  try{
   const destination=studioTreeDropDestination(e.target),rows=currentRows,documentData=sourceData;
   const files=[...(e.dataTransfer.files??[])];if(!files.length)throw Error('ドロップされたファイルを取得できません');
   const host=window.FRBStudioNativeHost;if(!host?.isAvailable()||!host.supportsFileDrop?.())throw Error('ファイル登録には更新したStudio NativeShellで起動してください');
   const result=await host.invoke('file.describeDrop',{}, {additionalObjects:files});
   if(currentRows!==rows||sourceData!==documentData)throw Error('画面が切り替わったため登録を中止しました');
   studioTreeInsertDropped(result.files,destination);
  }catch(error){setStatus(error.message,{kind:'error'});}
 });
}
