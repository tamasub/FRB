/* Flat JSON hierarchy contract; independent of application field names. */
const StudioTreeModel = (() => {
  const value = (r, f) => f ? String(r[f] ?? '') : '';
  function build(rows, cfg) {
    const nodes = rows.map((row,index)=>({row,index,children:[],parent:null}));
    const ids = new Map();
    nodes.forEach(n=>{const id=value(n.row,cfg.idField);if(!id || ids.has(id)) throw Error('ツリーIDが空または重複しています: '+id);ids.set(id,n);});
    nodes.forEach(n=>{
      const p=ids.get(value(n.row,cfg.parentField));
      if(value(n.row,cfg.parentField) && !p) throw Error('親が見つかりません: '+value(n.row,cfg.parentField));
      if(p && cfg.groupField && value(p.row,cfg.groupField)!==value(n.row,cfg.groupField)) throw Error('親子のグループが異なります');
      n.parent=p||null;
    });
    nodes.forEach(n=>{const seen=new Set();for(let p=n;p;p=p.parent){if(seen.has(p))throw Error('親子関係が循環しています');seen.add(p);}});
    const roots=[]; nodes.forEach(n=>(n.parent?n.parent.children:roots).push(n));
    const sort=list=>{list.sort((a,b)=> (Number(a.row[cfg.orderField])||0)-(Number(b.row[cfg.orderField])||0)||a.index-b.index);list.forEach(n=>sort(n.children));};
    sort(roots);
    if(cfg.groupField){const groups=new Map();nodes.filter(n=>!n.parent).forEach(n=>{const g=value(n.row,cfg.groupField);if(!groups.has(g))groups.set(g,groups.size);});roots.sort((a,b)=>groups.get(value(a.row,cfg.groupField))-groups.get(value(b.row,cfg.groupField)));}
    return {nodes,roots,ids};
  }
  function project(model, matches, collapsed, cfg) {
    const keep=new Set(matches), searching=keep.size!==model.nodes.length;
    [...keep].forEach(i=>{for(let p=model.nodes[i]?.parent;p;p=p.parent)keep.add(p.index);});
    const out=[];
    function visit(n,depth){if(!keep.has(n.index))return;out.push({...n,depth});if(searching||!collapsed.has(value(n.row,cfg.idField)))n.children.forEach(x=>visit(x,depth+1));}
    model.roots.forEach(n=>visit(n,0));return out;
  }
  function siblings(model,node){return node.parent?node.parent.children:model.roots.filter(n=>value(n.row,model.cfg?.groupField)===value(node.row,model.cfg?.groupField));}
  function move(rows,cfg,index,parentIndex,group) {
    const model=build(rows,cfg),n=model.nodes[index],p=parentIndex==null?null:model.nodes[parentIndex];
    if(!n)throw Error('移動する項目を選択してください');
    for(let a=p;a;a=a.parent)if(a===n)throw Error('自分や子孫の下には移動できません');
    if(p && cfg.parentKindField && !cfg.parentKinds.includes(p.row[cfg.parentKindField]))throw Error('この項目には子を追加できません');
    n.row[cfg.parentField]=p?value(p.row,cfg.idField):'';
    if(cfg.groupField){const g=p?p.row[cfg.groupField]:group;const set=n=>{n.row[cfg.groupField]=g;n.children.forEach(set);};set(n);}
    const peers=rows.filter(r=>r!==n.row&&value(r,cfg.parentField)===value(n.row,cfg.parentField)&&value(r,cfg.groupField)===value(n.row,cfg.groupField));
    n.row[cfg.orderField]=Math.max(0,...peers.map(r=>Number(r[cfg.orderField])||0))+10;
  }
  function reorder(rows,cfg,index,delta){const m=build(rows,cfg),n=m.nodes[index];m.cfg=cfg;const peers=siblings(m,n);const pos=peers.indexOf(n),to=pos+delta;if(to<0||to>=peers.length)return false;[peers[pos],peers[to]]=[peers[to],peers[pos]];peers.forEach((x,i)=>x.row[cfg.orderField]=(i+1)*10);return true;}
  return {build,project,move,reorder};
})();
if(typeof module!=='undefined')module.exports=StudioTreeModel;
