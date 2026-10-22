// studio_work_0268: field/value completion + candidate filtering + context-menu trigger.
// '/' is an editor command, never part of the query. The Parser remains independent.
var StudioSmartSearchEditor = (function () {
  'use strict';
  const OPERATORS = ['==', '!=', '=!', '>=', '=>', '<=', '=<', '=', '>', '<'];

  function isSearchTrigger(event, input) {
    // '/' is reserved as a command anywhere in the Smart Search input, even
    // immediately after a value (or with text selected). It is never inserted.
    // Let IME composition, modifier shortcuts and disabled/read-only inputs alone.
    return Boolean(event && input && event.key === '/' && !event.isComposing && event.keyCode !== 229 &&
      !event.ctrlKey && !event.metaKey && !event.altKey && !input.disabled && !input.readOnly);
  }

  function fieldChoices(fields) {
    const list = (Array.isArray(fields) ? fields : []).filter(f => f && f.field);
    const counts = new Map();
    for (const f of list) {
      const name = String(f.caption ?? f.label ?? f.field).trim().toLowerCase();
      counts.set(name,(counts.get(name) ?? 0) + 1);
    }
    const seen = new Set();
    return list.filter(f => {
      const id=String(f.field);
      if (seen.has(id)) return false;
      seen.add(id);
      return true;
    }).map(f => {
      const label = String(f.caption ?? f.label ?? f.field);
      const ambiguous = counts.get(label.trim().toLowerCase()) > 1;
      return {field:f, label, id:String(f.field), insertName:ambiguous?String(f.field):label};
    });
  }

  function quoteAtom(text) {
    const value = String(text ?? '');
    if (!/[\s()"'!=<>]/u.test(value) && !/^(and|or)$/i.test(value)) return value;
    const quote = value.includes('"') && !value.includes("'") ? "'" : '"';
    return quote + value.replaceAll('\\','\\\\').replaceAll(quote, '\\'+quote) + quote;
  }

  function valueChoices(field) {
    const family = typeof StudioSmartSearch !== 'undefined' ? StudioSmartSearch.familyFor(field) : String(field?.type ?? '');
    if (family === 'boolean') return [
      {label:'はい（true）',value:'true'}, {label:'いいえ（false）',value:'false'}
    ];
    if (family !== 'select' && !Array.isArray(field?.options)) return [];
    const result = [];
    const ids = new Set();
    for (const option of Array.isArray(field?.options) ? field.options : []) {
      const value = typeof optionValue === 'function' ? optionValue(option,field) :
        (option && typeof option==='object' ? option[field.valueField ?? 'cd'] ?? option.cd ?? option.value ?? option.id ?? option.key : option);
      const label = typeof optionLabel === 'function' ? optionLabel(option,field) :
        (option && typeof option==='object' ? option[field.labelField ?? 'name'] ?? option.name ?? option.label ?? option.caption ?? option.text ?? value : option);
      if (value == null || label == null || ids.has(String(value))) continue;
      ids.add(String(value));
      result.push({label:String(label), value:String(value), insertValue:String(label)});
    }
    return result;
  }

  // Detect a candidate value immediately before caret; no SQL parsing or changes to existing expressions.
  function valueContext(prefix, fields) {
    const match = /(?:^|[\s(])("(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*'|[^\s()=!<>]+)(==|!=|=!|>=|=>|<=|=<|=|>|<)([^\s()]*)$/u.exec(prefix);
    if (!match) return null;
    const name = match[1];
    const unquoted = ((name[0] === '"' && name.at(-1) === '"') || (name[0] === "'" && name.at(-1) === "'"))
      ? name.slice(1,-1).replace(/\\([\\"'])/g,'$1') : name;
    const exactId = fields.find(f => String(f.field).toLowerCase()===unquoted.toLowerCase());
    const byCaption = fields.filter(f => String(f.caption ?? f.label ?? '').toLowerCase()===unquoted.toLowerCase());
    const field = exactId ?? (byCaption.length===1 ? byCaption[0] : null);
    if (!field || !valueChoices(field).length) return null;
    return {field, valueStart:prefix.length - match[3].length, typed:match[3]};
  }

  function setup(args={}) {
    const input = args.input, section = args.section;
    if (!input || !section) return null;
    const getFields = typeof args.getFields === 'function' ? args.getFields : () => [];
    const popup = document.createElement('div');
    popup.id = 'studioSmartSearchSuggestions';
    popup.className = 'studio-smart-search-suggestions';
    popup.setAttribute('role','listbox');
    popup.setAttribute('aria-label','Smart Search 補完候補');
    popup.hidden = true;
    section.appendChild(popup);
    input.setAttribute('aria-controls',popup.id);
    input.setAttribute('aria-autocomplete','list');
    let state=null;
    let internalChange=false;
    const hint=document.createElement('div');
    hint.className='studio-smart-search-hint';
    const filter=document.createElement('input');
    filter.type='text';
    filter.className='studio-smart-search-candidate-filter';
    filter.autocomplete='off';
    filter.setAttribute('aria-label','補完候補を絞り込む');
    filter.placeholder='候補を検索…';
    const list=document.createElement('div');
    list.className='studio-smart-search-option-list';
    popup.append(hint,filter,list);
    function filterItems(items, query) {
      const needle=String(query??'').trim().toLocaleLowerCase();
      return needle ? items.filter(x=>[x.label,x.id,x.value].some(v=>String(v??'').toLocaleLowerCase().includes(needle))) : [...items];
    }
    function updateCandidateFilter() {
      if (!state) return;
      state.filter=filter.value;
      state.items=filterItems(state.allItems,state.filter);
      state.index=0;
      draw();
    }
    // FRB Launch navigation contract: Tab / Enter / Right confirm the active suggestion.
    function isConfirmKey(key) {
      return key==='Tab' || key==='Enter' || key==='ArrowRight';
    }
    filter.addEventListener('input',updateCandidateFilter);
    filter.addEventListener('keydown',event=>{
      if (!state || event.isComposing || event.keyCode===229) return;
      if (event.key==='Escape') {event.preventDefault();event.stopPropagation();close();input.focus();return;}
      if ((event.key==='ArrowDown'||event.key==='ArrowUp') && state.items.length) {
        event.preventDefault(); event.stopPropagation();
        state.index=(state.index+(event.key==='ArrowDown'?1:-1)+state.items.length)%state.items.length;
        highlight(); return;
      }
      if (isConfirmKey(event.key) && state.items.length) {
        event.preventDefault();event.stopPropagation();choose(state.index);
      }
    });

    function close() {
      state=null;
      popup.hidden=true;
      section.classList.remove('studio-smart-search-popup-open');
      list.replaceChildren();
      filter.value='';
      input.setAttribute('aria-expanded','false');
      input.removeAttribute('aria-activedescendant');
    }
    function place() {
      const i=input.getBoundingClientRect(), s=section.getBoundingClientRect();
      const width=Math.min(Math.max(i.width,300),520);
      popup.style.width=`${width}px`;
      popup.style.left=`${Math.max(4,Math.min(i.left-s.left, s.width-width-4))}px`;
      popup.style.top=`${i.bottom-s.top+4}px`;
    }
    function draw() {
      if (!state) return;
      list.replaceChildren();
      hint.textContent=state.mode==='field' ? '検索項目を選択  ·  ↑↓ 移動 / Tab・Enter・→ 確定 / Esc 閉じる' :
        `${state.field.caption ?? state.field.field} の値  ·  ↑↓ 移動 / Tab・Enter・→ 確定 / Esc 閉じる`;
      if (!state.items.length) {
        const empty=document.createElement('div');empty.className='studio-smart-search-empty';
        empty.textContent='候補はありません（自由入力も可能）'; list.appendChild(empty);
      }
      state.items.forEach((item,i)=>{
        const button=document.createElement('div');
        button.className='studio-smart-search-option' + (i===state.index?' is-active':'');
        button.id=`studioSmartSearchOption${i}`;
        button.setAttribute('role','option');
        button.setAttribute('aria-selected',i===state.index?'true':'false');
        const title=document.createElement('span');title.textContent=item.label;
        const detail=document.createElement('small');detail.textContent=state.mode==='field'?item.id:(item.value===item.label?'':item.value);
        button.append(title,detail);
        button.addEventListener('mousedown',e=>e.preventDefault());
        button.addEventListener('click',()=>choose(i));
        button.addEventListener('mousemove',()=>{if (state && state.index!==i){state.index=i;highlight();}});
        list.appendChild(button);
      });
      popup.hidden=false;
      // The search card and grid card each create a stacking context (backdrop-filter).
      // Elevate the card while suggestions are open; a large z-index on the child alone is insufficient.
      section.classList.add('studio-smart-search-popup-open');
      input.setAttribute('aria-expanded','true');
      highlight(); place();
    }
    function highlight() {
      list.querySelectorAll('[role="option"]').forEach((el,i)=>{
        el.classList.toggle('is-active',i===state.index);
        el.setAttribute('aria-selected',i===state.index?'true':'false');
      });
      const el=list.querySelectorAll('[role="option"]')[state.index];
      if (el) { input.setAttribute('aria-activedescendant',el.id); el.scrollIntoView?.({block:'nearest'}); }
      else input.removeAttribute('aria-activedescendant');
    }
    function replace(start,end,text) {
      input.value=input.value.slice(0,start)+text+input.value.slice(end);
      input.setSelectionRange(start+text.length,start+text.length);
      input.focus();
      internalChange=true;
      try { input.dispatchEvent(new Event('input',{bubbles:true})); } finally { internalChange=false; }
    }
    function showFieldList() {
      if (input.disabled) return;
      if (input.disabled || input.readOnly) return;
      close();
      const allItems=fieldChoices(getFields());
      state={mode:'field', allItems,items:allItems,index:0,caret:input.selectionStart,selectionEnd:input.selectionEnd,filter:''};
      draw();
      // Slash/right-click are explicit completion commands: focus its dedicated filter.
      filter.focus();
    }
    function showValueList(ctx) {
      const all=valueChoices(ctx.field);
      const needle=ctx.typed.toLocaleLowerCase();
      const items=all.filter(x=>x.label.toLocaleLowerCase().includes(needle) || x.value.toLocaleLowerCase().includes(needle));
      state={mode:'value',field:ctx.field, allItems:items,items,index:0,valueStart:ctx.valueStart,typed:ctx.typed,filter:''};
      filter.value='';
      draw();
    }
    function choose(i) {
      if (!state || !state.items[i]) return;
      const chosen=state.items[i];
      if (state.mode==='field') {
        const start=state.caret, end=state.selectionEnd;
        const needsSpace=start>0 && !/[\s(]/u.test(input.value[start-1]);
        const insertion=(needsSpace?' ':'')+quoteAtom(chosen.insertName)+'=';
        close(); replace(start,end,insertion);
        const field=chosen.field;
        if (valueChoices(field).length) showValueList({field,valueStart:input.selectionStart,typed:''});
      } else {
        const end=input.selectionStart, start=state.valueStart;
        const value=quoteAtom(chosen.insertValue ?? chosen.value);
        close(); replace(start,end,value);
      }
    }
    function onKeydown(event) {
      if (event.isComposing || event.keyCode===229) return;
      if (isSearchTrigger(event,input)) {
        event.preventDefault(); event.stopImmediatePropagation(); args.onOpen?.(); showFieldList(); return;
      }
      if (!state) return;
      if (event.key==='Escape') {
        event.preventDefault(); event.stopImmediatePropagation(); close(); return;
      }
      if ((event.key==='ArrowDown' || event.key==='ArrowUp') && state.items.length) {
        event.preventDefault(); event.stopImmediatePropagation();
        state.index=(state.index+(event.key==='ArrowDown'?1:-1)+state.items.length)%state.items.length;
        highlight(); return;
      }
      if (isConfirmKey(event.key) && state.items.length) {
        event.preventDefault(); event.stopImmediatePropagation(); choose(state.index); return;
      }
      // Normal user input is never swallowed by the completer.
      if (state.mode==='field' && (event.key==='Backspace' || event.key==='Delete')) close();
    }
    input.addEventListener('keydown',onKeydown,true); // capture before the existing Enter→Search handler
    input.addEventListener('input',()=>{
      if (internalChange) return;
      if (state?.mode==='field') {close();return;}
      const ctx=valueContext(input.value.slice(0,input.selectionStart),getFields());
      if (ctx) showValueList(ctx);
      else close();
    });
    input.addEventListener('blur',event=>{
      if (popup.contains(event.relatedTarget) || popup.contains(document.activeElement)) return;
      close();
    });
    // Right-click is the same explicit completion command as '/'. No slash is inserted.
    input.addEventListener('contextmenu',event=>{
      if (input.disabled || input.readOnly) return;
      event.preventDefault();
      args.onOpen?.();
      showFieldList();
    });
    input.addEventListener('compositionstart',close);
    window.addEventListener('resize',()=>{if(state)place();});
    document.addEventListener('pointerdown',event=>{
      if(state && event.target!==input && !popup.contains(event.target)) close();
    });
    close();
    return Object.freeze({close,showFieldList,isOpen:()=>Boolean(state)});
  }
  return Object.freeze({setup,isSearchTrigger,fieldChoices,valueChoices,valueContext,quoteAtom});
})();
