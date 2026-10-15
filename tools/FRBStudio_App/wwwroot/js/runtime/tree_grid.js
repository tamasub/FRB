// ViewDef-driven tree operations. Source data remains a flat array.
const studioTreeStates = new WeakMap();
let studioTreeVisible = [];
function studioTreeConfig(gd=gridDef()) {const c=gd?.tree;return c?.enabled && c.idField && c.parentField && c.labelField ? c : null;}
function studioTreeState(){let s=studioTreeStates.get(currentRows);if(!s){s={collapsed:new Set(),flat:false};studioTreeStates.set(currentRows,s);}if(studioTreeConfig()?.treeOnly)s.flat=false;return s;}
function studioTreeCaption(key, c=studioTreeConfig()) {
 const defaults = {
  rootAdd: '最上位に追加', rootEdit: '最上位を編集', rootName: '最上位の名称',
  rootSelect: '最上位項目を選択してください', rootMissing: '最上位項目の配列が見つかりません',
  rootChoose: '追加先の最上位項目', rootToggle: '最上位項目を展開・折りたたみ'
 };
 return String(c?.captions?.[key] || defaults[key] || key);
}
function studioTreeReadonly(){return Boolean(launchRuntime?.readonly);}
function studioTreeRun(fn){try{fn();}catch(e){setStatus(e.message,{kind:'error'});}}
function studioTreeModel(){return StudioTreeModel.build(currentRows,studioTreeConfig());}
function studioTreeRows(){
 const c=studioTreeConfig();if(!c)return filteredRows;
 try {const s=studioTreeState();studioTreeVisible=studioTreeGroupEntries(StudioTreeModel.project(studioTreeModel(),filteredRows.map(x=>x.index),s.flat?new Set():s.collapsed,c),c);return s.flat?filteredRows:studioTreeVisible;}
 catch(e){setStatus(e.message,{kind:'error'});return filteredRows;}
}
function studioTreeGroups(c){const raw=c.groupSource?getByPath(sourceData,c.groupSource):[];const groups=new Map();(Array.isArray(raw)?[...raw].sort((a,b)=>(Number(a[c.groupOrderField])||0)-(Number(b[c.groupOrderField])||0)):[]).forEach(r=>groups.set(String(r[c.groupIdField]),String(r[c.groupLabelField]??r[c.groupIdField])));currentRows.forEach(r=>{const g=String(r[c.groupField]??'');if(!groups.has(g))groups.set(g,g||'未分類');});return groups;}
function studioTreeLabel(n,c){const a=[];for(let p=n;p;p=p.parent)a.unshift(p.row[c.labelField]||'(名称なし)');return a.join(' › ');}
function studioTreeToolbar(){
 let bar=$('studioTreeToolbar');const c=studioTreeConfig();if(!c){bar?.remove();return;}
 if(!bar){bar=document.createElement('div');bar.id='studioTreeToolbar';$('dataGrid').parentElement.before(bar);}bar.replaceChildren();
 const button=(text,fn,edit=false)=>{const b=document.createElement('button');b.textContent=text;b.type='button';b.disabled=edit&&studioTreeReadonly();b.onclick=()=>studioTreeRun(fn);bar.append(b);};
 if(!c.treeOnly)button(studioTreeState().flat?'ツリー表示':'一覧表示',()=>{studioTreeState().flat=!studioTreeState().flat;renderGrid();});
 if(c.groupRoots){button(studioTreeCaption('rootAdd',c),()=>studioTreeEditGroup(true),true);button(studioTreeCaption('rootEdit',c),()=>studioTreeEditGroup(false),true);}
 button('子を追加',()=>studioTreeAdd('child'),true);button('同じ階層に追加',()=>studioTreeAdd('sibling'),true);if(!c.treeOnly)button('最上位に追加',()=>studioTreeAdd('root'),true);
 if(!c.treeOnly)button('↑ 上へ',()=>{studioTreeMoveSelected(-1);},true);
 if(!c.treeOnly)button('↓ 下へ',()=>{studioTreeMoveSelected(1);},true);
 if(!c.treeOnly)button('移動…',()=>studioTreeMoveDialog(),true);
 button('すべて展開',()=>{studioTreeState().collapsed.clear();renderGrid();});
 button('すべて折りたたむ',()=>{studioTreeState().collapsed=new Set([...currentRows.map(r=>String(r[c.idField])),...[...studioTreeGroups(c).keys()].map(g=>'group:'+g)]);renderGrid();});
}
function studioTreeChoose(title,choices,done){
 const dialog=document.createElement('dialog'),label=document.createElement('h3'),select=document.createElement('select');label.textContent=title;select.style.minWidth='320px';select.setAttribute('aria-label',title);
 choices.forEach(([v,t])=>{const o=document.createElement('option');o.value=v;o.textContent=t;select.append(o);});
 const ok=document.createElement('button'),cancel=document.createElement('button');ok.textContent='決定';cancel.textContent='キャンセル';ok.onclick=()=>{const v=select.value;dialog.close();studioTreeRun(()=>done(v));};cancel.onclick=()=>dialog.close();dialog.append(label,select,ok,cancel);dialog.onclose=()=>dialog.remove();document.body.append(dialog);dialog.showModal();select.focus();
}
function studioTreeAdd(mode,group,preset){
 if(studioTreeReadonly())throw Error("読み取り専用です");
 const c=studioTreeConfig(),m=studioTreeModel(),n=m.nodes[selectedIndex];
 if(c.groupRoots&&studioTreeState().selectedGroup!=null&&!n){group=studioTreeState().selectedGroup;mode='root';}
 if(mode!=='root'&&!n)throw Error('親または同じ階層の項目を選択してください');
 const p=mode==='child'?n:mode==='sibling'?n.parent:null;
 if(p&&c.parentKindField&&!c.parentKinds.includes(p.row[c.parentKindField]))throw Error('カテゴリーを選択してください');
 if(mode==='root'&&c.groupField&&group===undefined){studioTreeChoose(studioTreeCaption('rootChoose',c), [...studioTreeGroups(c)],g=>studioTreeAdd(mode,g,preset));return;}
 if(preset===undefined && c.createPresets?.length){studioTreeChoose('追加する項目の種類',c.createPresets.map((p,i)=>[String(i),p.caption]),i=>studioTreeAdd(mode,group,c.createPresets[Number(i)].values));return;}
 const row=createDefaultRow();Object.assign(row,cloneData(preset||{}));row[c.parentField]=p?String(p.row[c.idField]):'';
 if(c.groupField)row[c.groupField]=mode==='root'?group:n.row[c.groupField];
 const peers=currentRows.filter(r=>String(r[c.parentField]??'')===row[c.parentField]&&(!c.groupField||r[c.groupField]===row[c.groupField]));
 row[c.orderField]=mode==='sibling'?studioTreeOrderAfter(n.row):Math.max(0,...peers.map(r=>Number(r[c.orderField])||0))+10;
 if(c.groupRoots)studioTreeState().collapsed.delete('group:'+row[c.groupField]);
 if(p)studioTreeState().collapsed.delete(String(p.row[c.idField]));
 applyHeaderEdits();openNewDetail(row,'追加先: '+(p?studioTreeLabel(p,c):studioTreeGroups(c).get(String(row[c.groupField]))||'最上位')+'（F12で反映）');
}
function studioTreeMoveDialog(){
 if(studioTreeReadonly())throw Error("読み取り専用です");
 const c=studioTreeConfig(),m=studioTreeModel(),n=m.nodes[selectedIndex];if(!n)throw Error('移動する項目を選択してください');const index=selectedIndex;
 const options=[...studioTreeGroups(c)].map(([g,t])=>['g:'+g,t+' / 最上位']);
 m.nodes.forEach(p=>{for(let x=p;x;x=x.parent)if(x===n)return;if(c.parentKindField&&!c.parentKinds.includes(p.row[c.parentKindField]))return;options.push(['p:'+p.index,studioTreeLabel(p,c)]);});
 studioTreeChoose('移動先を選択',options,v=>{StudioTreeModel.move(currentRows,c,index,v.startsWith('p:')?Number(v.slice(2)):null,v.slice(2));studioTreeState().collapsed.clear();applySearch();});
}
function studioTreeDecorate(tr,entry,fields){
 const c=studioTreeConfig();if(!c)return;
 const groupCell=tr.children[fields.findIndex(f=>f.field===c.groupField)];if(groupCell)groupCell.textContent=studioTreeGroups(c).get(String(entry.row[c.groupField]))||entry.row[c.groupField];
 if(studioTreeState().flat||entry.depth===undefined)return;
 const td=tr.children[fields.findIndex(f=>f.field===c.labelField)];if(!td)return;
 td.style.paddingLeft=(8+entry.depth*22)+'px';const b=document.createElement('button');b.type='button';b.textContent=entry.children.length?(studioTreeState().collapsed.has(String(entry.row[c.idField]))?'▸':'▾'):'·';b.disabled=!entry.children.length;b.setAttribute('aria-label','展開・折りたたみ');b.onclick=e=>{e.stopPropagation();studioTreeToggle(entry);};td.prepend(b);
 tr.tabIndex=(entry.index===selectedIndex||selectedIndex<0&&entry===studioTreeVisible[0])?0:-1;tr.setAttribute('aria-level',entry.depth+1);if(entry.children.length)tr.setAttribute('aria-expanded',!studioTreeState().collapsed.has(String(entry.row[c.idField])));
 tr.addEventListener('keydown',e=>{
 if(!['ArrowUp','ArrowDown','ArrowLeft','ArrowRight','Enter'].includes(e.key))return;e.preventDefault();e.stopPropagation();selectedIndex=entry.index;studioTreeState().selectedGroup=null;
 const s=studioTreeState(),id=String(entry.row[c.idField]),pos=studioTreeVisible.findIndex(n=>n.index===entry.index);
 if(e.key==='Enter'){openDetail(entry.index);return;}
 if(e.key==='ArrowUp'||e.key==='ArrowDown'){const next=studioTreeVisible[Math.max(0,Math.min(studioTreeVisible.length-1,pos+(e.key==='ArrowDown'?1:-1)))];selectedIndex=next.groupId!=null?-1:next.index;s.selectedGroup=next.groupId??null;}
 if(e.key==='ArrowLeft'){if(entry.children.length&&!s.collapsed.has(id))s.collapsed.add(id);else if(entry.parent)selectedIndex=entry.parent.index;else if(entry.groupRoot){selectedIndex=-1;s.selectedGroup=entry.groupRoot.groupId;}}
 if(e.key==='ArrowRight'&&entry.children.length){if(s.collapsed.has(id))s.collapsed.delete(id);else selectedIndex=entry.children[0].index;}
 renderGrid();if(s.selectedGroup!=null)studioTreeFocusGroup(s.selectedGroup);else document.querySelector('#dataGrid tr[data-source-index="'+selectedIndex+'"]')?.focus();
 });
 tr.addEventListener('click',()=>document.querySelector('#dataGrid tr[data-source-index="'+selectedIndex+'"]')?.focus());
}
function studioTreeToggle(entry){const s=studioTreeState(),id=String(entry.row[studioTreeConfig().idField]);s.collapsed.has(id)?s.collapsed.delete(id):s.collapsed.add(id);renderGrid();}
function studioTreeProtect(pending,original){const c=studioTreeConfig();if(c&&original)[c.idField,c.parentField,c.groupField,c.orderField].filter(Boolean).forEach(f=>pending[f]=original[f]);return pending;}
function studioTreeDetailContext(form,row){
 const c=studioTreeConfig();if(!c)return;
 const line=document.createElement('p');line.style.gridColumn='1 / -1';
 try{const m=studioTreeModel(),p=m.ids.get(String(row[c.parentField]??''));line.textContent='配置先: '+(studioTreeGroups(c).get(String(row[c.groupField]))||'最上位')+(p?' › '+studioTreeLabel(p,c):'');}catch(e){line.textContent=e.message;}
 form.append(line);
}
function studioTreeValidateKind(row,index){
 const c=studioTreeConfig();if(!c||!c.parentKindField)return true;
 try{const n=studioTreeModel().nodes[index];if(n?.children.length&&!c.parentKinds.includes(row[c.parentKindField])){setStatus('子がある項目はカテゴリーのままにしてください。種別変更前に子を移動してください。',{kind:'error'});return false;}return true;}catch(e){setStatus(e.message,{kind:'error'});return false;}
}
function studioTreeOrderAfter(row){
 const c=studioTreeConfig(),base=Number(row[c.orderField])||0;
 const next=currentRows.filter(r=>r!==row&&String(r[c.parentField]??'')===String(row[c.parentField]??'')&&(!c.groupField||r[c.groupField]===row[c.groupField])).map(r=>Number(r[c.orderField])||0).filter(n=>n>base).sort((a,b)=>a-b)[0];
 return next===undefined?base+10:(base+next)/2;
}
