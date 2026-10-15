// Virtual group roots: group records remain in their original collection.
function studioTreeGroupEntries(entries,c){
 if(!c.groupRoots||studioTreeState().flat)return entries;
 const s=studioTreeState(),searching=filteredRows.length!==currentRows.length,result=[];
 let position=0;
 for(const [id,label] of studioTreeGroups(c)){
  const children=entries.filter(n=>String(n.row[c.groupField])===id);
  if(searching&&!children.length)continue;
  const root={groupId:id,groupLabel:label,index:-2-position++,depth:0,children,row:{[c.labelField]:label}};result.push(root);
  if(searching||!s.collapsed.has('group:'+id))result.push(...children.map(n=>({...n,depth:n.depth+1,groupRoot:root})));
 }
 return result;
}
function studioTreeGroupRow(entry,fields){
 const s=studioTreeState(),tr=document.createElement('tr');tr.dataset.sourceIndex=String(entry.index);tr.dataset.groupId=entry.groupId;tr.tabIndex=0;
 if(s.selectedGroup===entry.groupId)tr.classList.add('selected');
 const td=document.createElement('td');td.colSpan=fields.length;td.style.cssText='font-weight:700;background:#edf3ff;padding:8px';
 const button=document.createElement('button');button.textContent=s.collapsed.has('group:'+entry.groupId)?'▸':'▾';button.setAttribute('aria-label',studioTreeCaption('rootToggle',studioTreeConfig()));button.onclick=e=>{e.stopPropagation();toggle();};
 const toggle=()=>{const key='group:'+entry.groupId;s.collapsed.has(key)?s.collapsed.delete(key):s.collapsed.add(key);renderGrid();};
 td.append(button,document.createTextNode(' '+entry.groupLabel));tr.append(td);
 const select=()=>{selectedIndex=-1;s.selectedGroup=entry.groupId;};
 tr.onclick=()=>{select();renderGrid();studioTreeFocusGroup(entry.groupId);};
 tr.ondblclick=()=>{select();studioTreeRun(()=>studioTreeEditGroup(false));};
 tr.onkeydown=e=>{if(!['ArrowUp','ArrowDown','ArrowLeft','ArrowRight','Enter'].includes(e.key))return;e.preventDefault();e.stopPropagation();select();
  if(e.key==='Enter'){studioTreeRun(()=>studioTreeEditGroup(false));return;}
  const key='group:'+entry.groupId;
  if(e.key==='ArrowLeft')s.collapsed.add(key);
  else if(e.key==='ArrowRight'){if(s.collapsed.has(key))s.collapsed.delete(key);else {const next=studioTreeVisible.find(n=>n.groupRoot?.groupId===entry.groupId);if(next){selectedIndex=next.index;s.selectedGroup=null;}}}
  else {const pos=studioTreeVisible.findIndex(n=>n.index===entry.index),n=studioTreeVisible[Math.max(0,Math.min(studioTreeVisible.length-1,pos+(e.key==='ArrowDown'?1:-1)))];if(n.groupId!=null)s.selectedGroup=n.groupId;else {selectedIndex=n.index;s.selectedGroup=null;}}
  renderGrid();if(s.selectedGroup!=null)studioTreeFocusGroup(s.selectedGroup);else document.querySelector('#dataGrid tr[data-source-index="'+selectedIndex+'"]')?.focus();
 };return tr;
}
function studioTreeFocusGroup(id){[...document.querySelectorAll('#dataGrid tr[data-group-id]')].find(tr=>tr.dataset.groupId===id)?.focus();}
function studioTreeEditGroup(isNew){
 if(studioTreeReadonly())throw Error('読み取り専用です');
 const c=studioTreeConfig(),rows=getByPath(sourceData,c.groupSource),s=studioTreeState();if(!Array.isArray(rows))throw Error(studioTreeCaption('rootMissing',c));
 const existing=rows.find(r=>String(r[c.groupIdField])===s.selectedGroup);if(!isNew&&!existing)throw Error(studioTreeCaption('rootSelect',c));
 const d=document.createElement('dialog'),title=document.createElement('h3'),input=document.createElement('input'),enabled=document.createElement('input'),enabledLabel=document.createElement('label');title.textContent=studioTreeCaption(isNew?'rootAdd':'rootEdit',c);input.value=existing?.[c.groupLabelField]??'';input.placeholder=studioTreeCaption('rootName',c);input.setAttribute('aria-label',studioTreeCaption('rootName',c));enabled.type='checkbox';enabled.checked=existing?.[c.groupEnabledField]!==false;enabledLabel.append(enabled,document.createTextNode('有効'));
 const ok=document.createElement('button');ok.textContent='反映';ok.onclick=()=>{if(!input.value.trim()){input.focus();return;}const row=existing??{[c.groupIdField]:crypto.randomUUID(),[c.groupOrderField]:Math.max(0,...rows.map(r=>Number(r[c.groupOrderField])||0))+10};row[c.groupLabelField]=input.value.trim();if(c.groupEnabledField)row[c.groupEnabledField]=enabled.checked;if(isNew)rows.push(row);s.selectedGroup=String(row[c.groupIdField]);d.close();applySearch();};
 const cancel=document.createElement('button');cancel.textContent='キャンセル';cancel.onclick=()=>d.close();d.append(title,input,enabledLabel,ok,cancel);d.onclose=()=>d.remove();document.body.append(d);d.showModal();input.focus();
}
function studioTreeMoveSelected(delta){
 if(studioTreeReadonly())return;const c=studioTreeConfig(),s=studioTreeState();
 if(c.groupRoots&&s.selectedGroup!=null){const rows=getByPath(sourceData,c.groupSource),sorted=[...rows].sort((a,b)=>(Number(a[c.groupOrderField])||0)-(Number(b[c.groupOrderField])||0)),i=sorted.findIndex(r=>String(r[c.groupIdField])===s.selectedGroup),j=i+delta;if(i<0||j<0||j>=sorted.length)return;[sorted[i],sorted[j]]=[sorted[j],sorted[i]];sorted.forEach((r,i)=>r[c.groupOrderField]=(i+1)*10);}
 else StudioTreeModel.reorder(currentRows,c,selectedIndex,delta);applySearch();
}
