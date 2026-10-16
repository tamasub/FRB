// Generic objectArray card editor, enabled by edit.subGrid.layout="cards".
// Card Layout: multi-line controls grow with their text until a modest maximum height.
// The data remains untouched: only the TEXTAREA presentation is adjusted.
let studioCardTextareaResizeListenerAttached=false;
function fitStudioCardTextareaHeight(input, maxHeightPx=240) {
 if (!input || input.tagName !== 'TEXTAREA') return;
 const maxHeight=Math.max(80,Number(maxHeightPx)||240);
 const minHeight=46;
 input.style.boxSizing='border-box';
 input.style.minHeight=`${minHeight}px`;
 input.style.maxHeight=`${maxHeight}px`;
 input.style.resize='none';
 input.style.overflowX='hidden';
 input.style.overflowY='hidden';
 input.style.height='auto';
 // Before a card is attached scrollHeight can be 0; estimate briefly, then
 // measure again after attachment (and on each edit/width change).
 const rawHeight=input.scrollHeight;
 const lines=String(input.value??'').split(/\r?\n/).length;
 const estimatedHeight=Math.max(minHeight,lines*19+16);
 const naturalHeight=rawHeight>0?rawHeight+2:estimatedHeight;
 input.style.height=`${Math.max(minHeight,Math.min(maxHeight,naturalHeight))}px`;
 input.style.overflowY=naturalHeight>maxHeight?'auto':'hidden';
 input.style.scrollbarGutter=naturalHeight>maxHeight?'stable':'';
}

function enableStudioCardTextareaAutoHeight(input,column={}) {
 if (!input || input.tagName !== 'TEXTAREA') return;
 // ViewDef can override the default cap per subGrid column when necessary.
 const declaredMax=Number(column?.edit?.maxHeight??column?.maxHeight);
 const maxHeight=Number.isFinite(declaredMax)&&declaredMax>0?declaredMax:240;
 input.classList.add('studio-card-autoheight-textarea');
 input.dataset.autoHeightMax=String(maxHeight);
 const fit=()=>fitStudioCardTextareaHeight(input,maxHeight);
 fit();
 input.addEventListener('input',fit);
 if (!studioCardTextareaResizeListenerAttached && typeof window !== 'undefined') {
  studioCardTextareaResizeListenerAttached=true;
  window.addEventListener('resize',()=>{
   document.querySelectorAll('textarea.studio-card-autoheight-textarea').forEach(textarea=>{
    fitStudioCardTextareaHeight(textarea,Number(textarea.dataset.autoHeightMax));
   });
  });
 }
 if (typeof requestAnimationFrame === 'function') {
  requestAnimationFrame(()=>{if(input.isConnected)fit();});
 }
}

function createDetailSubGridCards({field,row,gd,data}) {
 const cfg=detailSubGridConfig(field),columns=objectArraySubGridColumns(field,data);
 const card=document.createElement('div');card.className='child-card detail-subgrid-edit';
 card.dataset.subgridRole='data';card.dataset.subgridField=field.field;card.dataset.subgridType=field.type;
 card.__studioCardRows=cloneSubGridCanonicalValue(data);
 const editable=isDetailSubGridEditable(field)&&!launchRuntime?.readonly;
 const dirty=()=>markDetailSubGridDirty(card);
 const render=()=>{
  card.replaceChildren();const header=document.createElement('div');header.className='detail-subgrid-header';
  const title=document.createElement('h3');title.textContent=field.caption??field.field;header.append(title);
  const badge=document.createElement('span');badge.className='detail-subgrid-dirty-badge';badge.textContent=card.classList.contains('is-dirty')?'編集中':'上から順に実行';header.append(badge);
  if(editable)header.append(createSubGridActionButton('＋処理を追加','末尾に追加',()=>{card.__studioCardRows.push(emptyObjectForColumns(columns));dirty();render();}));card.append(header);
  card.__studioCardRows.forEach((item,index)=>{
   const section=document.createElement('fieldset');section.style.cssText='margin:12px 0;padding:12px;border:1px solid #d7e2e8;border-radius:10px;min-width:0';
   const legend=document.createElement('legend');legend.textContent=`${cfg.rowCaption??'項目'} ${index+1}`;section.append(legend);
   if(editable){const ops=document.createElement('div');ops.style.textAlign='right';
    for(const [label,delta] of [['↑',-1],['↓',1]]){const b=createSubGridActionButton(label,'順序を変更',()=>{const j=index+delta;if(j<0||j>=card.__studioCardRows.length)return;[card.__studioCardRows[index],card.__studioCardRows[j]]=[card.__studioCardRows[j],card.__studioCardRows[index]];dirty();render();});b.disabled=index+delta<0||index+delta>=card.__studioCardRows.length;ops.append(b);}
    ops.append(createSubGridActionButton('削除','この処理を削除',()=>{card.__studioCardRows.splice(index,1);dirty();render();}));section.append(ops);
   }
   const details=document.createElement('details'),summary=document.createElement('summary');summary.textContent='詳細設定';details.append(summary);let advanced=0;
   columns.forEach(col=>{
    if(!fieldMatchesVisibleWhen(col,item))return;
    const line=document.createElement('label');line.style.cssText='display:block;margin:10px 0';const caption=document.createElement('span');caption.textContent=col.caption??col.field;caption.style.display='block';line.append(caption);
    let control;
    if(col.control==='lines'){
     control=document.createElement('textarea');control.rows=4;control.value=Array.isArray(item[col.field])?item[col.field].join('\n'):String(item[col.field]??'');control.disabled=!editable;control.dataset.column=col.field;
    } else control=createSubGridCellControl({value:item[col.field],column:col,editable,field,multilineEditor:['textarea','json'].includes(col.type)});
    control.style.cssText='box-sizing:border-box;width:100%;min-width:0;max-width:none';
    enableStudioCardTextareaAutoHeight(control,col);
    if(col.placeholder)control.placeholder=col.placeholder;
    const update=()=>{item[col.field]=col.control==='lines'?(control.value===''?[]:control.value.replace(/\r\n/g,'\n').split('\n')):readSubGridControlValue(control);dirty();};
    control.addEventListener('input',update);control.addEventListener('change',()=>{update();if(columns.some(c=>(c.visibleWhen?.field??c.visible_when?.field)===col.field))render();});line.append(control);
    if(col.help){const help=document.createElement('small');help.textContent=col.help;line.append(help);}
    if(col.advanced){details.append(line);advanced++;}else section.append(line);
   });
   if(advanced)section.append(details);card.append(section);
  });
  if(!card.__studioCardRows.length){const hint=document.createElement('p');hint.textContent='「＋処理を追加」から、実行したい処理を選びます。';card.append(hint);}
 };
 // A single window resize handler above handles responsive line wrapping.
 render();return card;
}
