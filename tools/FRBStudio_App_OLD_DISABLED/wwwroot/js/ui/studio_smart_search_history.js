// studio_work_0268: Launch-inspired, explicitly registered search expressions.
// History is stored locally per selected Data JSON. It is not uploaded or written into Data JSON.
var StudioSmartSearchHistory = (function () {
  'use strict';
  const KEY='frbStudio.smartSearchHistory.v1';
  const MAX_ITEMS=60;
  function normalizeScope(key) {return String(key??'').replaceAll('\\','/').trim().toLocaleLowerCase()||'__default__';}
  function read(storage,scope) {
    try {
      const raw=JSON.parse(storage?.getItem(KEY)||'{}');
      const list=raw && typeof raw==='object' ? raw[normalizeScope(scope)] : null;
      return Array.isArray(list)?list.filter(v=>typeof v==='string'&&v.trim()).slice(0,MAX_ITEMS):[];
    } catch {return [];}
  }
  function save(storage,scope,items) {
    try {
      const previous=JSON.parse(storage?.getItem(KEY)||'{}');
      const all=previous && typeof previous==='object' && !Array.isArray(previous)?previous:{};
      all[normalizeScope(scope)]=items.slice(0,MAX_ITEMS);
      storage?.setItem(KEY,JSON.stringify(all));
      return true;
    } catch {return false;}
  }
  function register(storage,scope,query) {
    const text=String(query??'').trim();
    if (!text)return {items:read(storage,scope),added:false};
    const before=read(storage,scope);
    const items=[text,...before.filter(v=>v!==text)].slice(0,MAX_ITEMS);
    return {items,added:true,persisted:save(storage,scope,items)};
  }
  function move(items,index,delta) {
    const copy=[...items],dest=index+delta;
    if(index<0||dest<0||dest>=copy.length)return copy;
    [copy[index],copy[dest]]=[copy[dest],copy[index]];
    return copy;
  }
  function remove(items,index){return items.filter((_,i)=>i!==index);}
  function setup(args={}) {
    const input=args.input,section=args.section,registerBtn=args.registerBtn,dropdownBtn=args.dropdownBtn;
    if (!input||!section||!registerBtn||!dropdownBtn)return null;
    const storage=args.storage??(typeof localStorage!=='undefined'?localStorage:null);
    const scope=()=>normalizeScope(args.getDataKey?.());
    const popup=document.createElement('div');
    popup.id='studioSmartSearchHistoryPopup';
    popup.className='studio-smart-search-history';
    popup.hidden=true;
    popup.setAttribute('role','dialog');
    popup.setAttribute('aria-label','登録済み検索履歴');
    dropdownBtn.setAttribute('aria-controls',popup.id);
    dropdownBtn.setAttribute('aria-expanded','false');
    section.appendChild(popup);
    let open=false;
    function close() {
      open=false;popup.hidden=true;
      section.classList.remove('studio-smart-history-popup-open');
      dropdownBtn.setAttribute('aria-expanded','false');
    }
    function place() {
      const b=dropdownBtn.getBoundingClientRect(),s=section.getBoundingClientRect();
      const width=Math.min(Math.max(360,b.width+290),Math.max(280,s.width-8));
      popup.style.width=`${width}px`;
      popup.style.left=`${Math.max(4,Math.min(b.right-s.left-width,s.width-width-4))}px`;
      popup.style.top=`${b.bottom-s.top+5}px`;
    }
    function button(text,title,handler,disabled=false) {
      const el=document.createElement('button'); el.type='button';el.className='studio-smart-history-action';
      el.textContent=text;el.title=title;el.setAttribute('aria-label',title);el.disabled=disabled;
      el.addEventListener('click',e=>{e.stopPropagation();handler();});return el;
    }
    function rowView(text,index,items) {
      const row=document.createElement('div');row.className='studio-smart-history-row';
      const recall=button(text,'この検索式を呼び出して検索',()=>{
        input.value=text;input.dispatchEvent(new Event('input',{bubbles:true}));
        close(); input.focus();
        if (!args.searchBtn?.disabled) args.searchBtn?.click();
      });
      recall.className='studio-smart-history-recall';
      const controls=document.createElement('div');controls.className='studio-smart-history-controls';
      controls.append(button('▲','履歴を上へ',()=>{save(storage,scope(),move(items,index,-1));draw();},index===0),
        button('▼','履歴を下へ',()=>{save(storage,scope(),move(items,index,1));draw();},index===items.length-1),
        button('×','履歴を削除',()=>{save(storage,scope(),remove(items,index));draw();}));
      row.append(recall,controls);return row;
    }
    function draw() {
      popup.replaceChildren();
      const head=document.createElement('div');head.className='studio-smart-history-heading';
      head.textContent='登録した検索式（選択すると検索）';popup.appendChild(head);
      const items=read(storage,scope());
      if (!items.length) {
        const empty=document.createElement('div');empty.className='studio-smart-history-empty';
        empty.textContent='まだ履歴はありません。検索式を入力して「履歴登録」を押してください。';popup.appendChild(empty);
      } else items.forEach((item,index)=>popup.appendChild(rowView(item,index,items)));
      place();
    }
    function toggle() {
      if (open) {close();return;}
      args.onOpen?.();
      open=true;draw();popup.hidden=false;
      section.classList.add('studio-smart-history-popup-open');
      dropdownBtn.setAttribute('aria-expanded','true');
    }
    registerBtn.addEventListener('click',()=>{
      if(input.disabled||input.readOnly||!input.value.trim())return;
      // Validate through the standard search action before registering.
      if (!args.searchBtn || args.searchBtn.disabled) return;
      args.onOpen?.();
      args.searchBtn.click();
      if (input.getAttribute('aria-invalid')==='true') return;
      const outcome=register(storage,scope(),input.value);
      if (!outcome.persisted) return; // storage might be disabled by policy/browser settings
      args.onOpen?.();
      open=true;draw();popup.hidden=false;
      section.classList.add('studio-smart-history-popup-open');
      dropdownBtn.setAttribute('aria-expanded','true');
    });
    dropdownBtn.addEventListener('click',toggle);
    document.addEventListener('pointerdown',e=>{
      if (open&&!popup.contains(e.target)&&e.target!==registerBtn&&e.target!==dropdownBtn)close();
    });
    window.addEventListener('resize',()=>{if(open)place();});
    input.addEventListener('keydown',e=>{if(open&&e.key==='Escape'){close();}});
    return Object.freeze({close,isOpen:()=>open,read:()=>read(storage,scope())});
  }
  return Object.freeze({setup,read,save,register,move,remove,normalizeScope});
})();
