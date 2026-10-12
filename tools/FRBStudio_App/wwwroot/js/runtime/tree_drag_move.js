// Internal tree moves use an in-memory session, never external path/text payloads.
let studioTreeDragSession = null;
const studioTreeDragType = 'application/x-frb-studio-tree';
function studioTreeMoveDestination(tr, event) {
 const c=studioTreeConfig(),m=studioTreeModel(),group=tr.dataset.groupId;
 if(group!=null) {
  if(!studioTreeGroups(c).has(group))throw Error('移動先Pageが見つかりません');
  if(studioTreeDragSession.group!=null){
   const rect=tr.getBoundingClientRect();return {group,mode:event.clientY<rect.top+rect.height/2?'before':'after'};
  }
  return {group,parent:null,before:null,mode:'inside'};
 }
 if(studioTreeDragSession.group!=null)throw Error('PageはPageの行へ移動してください');
 const n=m.nodes[Number(tr.dataset.sourceIndex)];if(!n)throw Error('移動先が見つかりません');
 const rect=tr.getBoundingClientRect(),ratio=rect.height?(event.clientY-rect.top)/rect.height:0.5;
 const parentKind=!c.parentKindField||c.parentKinds.includes(n.row[c.parentKindField]);
 if(parentKind&&ratio>=0.25&&ratio<=0.75)return {group:n.row[c.groupField],parent:n.index,before:null,mode:'inside'};
 const peers=n.parent?n.parent.children:m.roots.filter(x=>!c.groupField||x.row[c.groupField]===n.row[c.groupField]);
 const before=ratio<0.5?n:peers[peers.indexOf(n)+1];
 return {group:n.row[c.groupField],parent:n.parent?.index??null,before:before?.index??null,mode:ratio<0.5?'before':'after'};
}
function studioTreeCommitMove(destination) {
 const c=studioTreeConfig(),s=studioTreeDragSession;
 if(studioTreeReadonly())throw Error('読み取り専用です');
 if(!s||s.rows!==currentRows||s.data!==sourceData)throw Error('画面が変わったため移動を中止しました');
 if(s.group!=null){
  const groups=getByPath(sourceData,c.groupSource),sorted=[...groups].sort((a,b)=>(Number(a[c.groupOrderField])||0)-(Number(b[c.groupOrderField])||0));
  const source=sorted.find(r=>String(r[c.groupIdField])===s.group),target=sorted.find(r=>String(r[c.groupIdField])===String(destination.group));
  if(!source||!target)throw Error('Pageが見つかりません');
  if(source!==target){sorted.splice(sorted.indexOf(source),1);sorted.splice(sorted.indexOf(target)+(destination.mode==='after'?1:0),0,source);sorted.forEach((r,i)=>r[c.groupOrderField]=(i+1)*10);}
  selectedIndex=-1;studioTreeState().selectedGroup=s.group;
 }else{
  const m=studioTreeModel(),n=m.ids.get(s.id);if(!n)throw Error('移動する項目が見つかりません');
  StudioTreeModel.place(currentRows,c,n.index,destination.parent,destination.group,destination.before);
  const state=studioTreeState();state.collapsed.delete('group:'+destination.group);
  if(destination.parent!=null)state.collapsed.delete(String(m.nodes[destination.parent].row[c.idField]));
  selectedIndex=n.index;state.selectedGroup=null;
 }
 applySearch();setStatus('配置を変更しました。JSONを保存するとLaunchへ反映されます。',{kind:'success',toast:false});
}
function studioTreeInstallDragMove(){
 const grid=$('dataGrid'),c=studioTreeConfig();if(!grid||!c?.dragMove)return;
 grid.querySelectorAll('tbody tr').forEach(tr=>{
  tr.draggable=!studioTreeReadonly();
  tr.addEventListener('dragstart',e=>{
   if(studioTreeReadonly()||e.target.closest('button,input,select,textarea')){e.preventDefault();return;}
   const cfg=studioTreeConfig(),n=studioTreeModel().nodes[Number(tr.dataset.sourceIndex)];
   studioTreeDragSession={rows:currentRows,data:sourceData,group:tr.dataset.groupId??null,id:n?String(n.row[cfg.idField]):null};
   e.dataTransfer.setData(studioTreeDragType,'move');e.dataTransfer.effectAllowed='move';
  });
 });
 if(grid.dataset.treeMoveBound==='true')return;grid.dataset.treeMoveBound='true';
 let marked;const clear=()=>{if(marked){marked.style.removeProperty('outline');marked.style.removeProperty('box-shadow');marked=null;}};
 const internal=e=>studioTreeConfig()?.dragMove&&studioTreeDragSession&&[...(e.dataTransfer?.types??[])].includes(studioTreeDragType)&&![...(e.dataTransfer?.types??[])].includes('Files');
 grid.addEventListener('dragover',e=>{
  if(!internal(e))return;e.preventDefault();e.stopPropagation();clear();
  try{
   if(studioTreeReadonly())throw Error('読み取り専用です');
   const tr=e.target.closest('tbody tr');if(!tr)throw Error('移動先の行へドロップしてください');
   const d=studioTreeMoveDestination(tr,e);e.dataTransfer.dropEffect='move';marked=tr;
   if(d.mode==='inside')tr.style.outline='2px solid #6ba7ff';else tr.style.boxShadow=d.mode==='before'?'inset 0 3px #6ba7ff':'inset 0 -3px #6ba7ff';
  }catch{e.dataTransfer.dropEffect='none';}
 });
 grid.addEventListener('dragleave',e=>{if(!grid.contains(e.relatedTarget))clear();});
 grid.addEventListener('dragend',()=>{clear();studioTreeDragSession=null;});
 grid.addEventListener('drop',e=>{
  if(!internal(e))return;e.preventDefault();e.stopImmediatePropagation();clear();
  try{const tr=e.target.closest('tbody tr');if(!tr)throw Error('移動先の行へドロップしてください');studioTreeCommitMove(studioTreeMoveDestination(tr,e));}
  catch(error){setStatus(error.message,{kind:'error'});}finally{studioTreeDragSession=null;}
 });
}
