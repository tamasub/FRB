// studio_work_0268 / Step 2: keyboard-only field/value completion for Smart Search.
// '/' is an editor command, never part of the query. The Parser remains independent.
var StudioSmartSearchEditor = (function () {
  'use strict';
  const OPERATORS = ['==', '!=', '=!', '>=', '=>', '<=', '=<', '=', '>', '<'];

  function isSearchTrigger(event, input) {
    if (!event || !input || event.key !== '/' || event.isComposing || event.keyCode === 229 ||
        event.ctrlKey || event.metaKey || event.altKey || input.disabled || input.readOnly) return false;
    const start = input.selectionStart, end = input.selectionEnd;
    if (typeof start !== 'number' || start !== end) return false;
    // A slash inside a path/URL or other search token stays an ordinary character.
    return start === 0 || /[\s(]/u.test(input.value[start - 1]);
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

    function close() {
      state=null;
      popup.hidden=true;
      popup.replaceChildren();
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
      popup.replaceChildren();
      const hint=document.createElement('div');
      hint.className='studio-smart-search-hint';
      hint.textContent=state.mode==='field' ? '検索項目を選択  ·  ↑↓ 移動 / Tab 確定 / Esc 閉じる' :
        `${state.field.caption ?? state.field.field} の値  ·  ↑↓ 移動 / Tab 確定 / Esc 閉じる`;
      popup.appendChild(hint);
      if (!state.items.length) {
        const empty=document.createElement('div');empty.className='studio-smart-search-empty';
        empty.textContent='候補はありません（自由入力も可能）'; popup.appendChild(empty);
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
        popup.appendChild(button);
      });
      popup.hidden=false;
      input.setAttribute('aria-expanded','true');
      highlight(); place();
    }
    function highlight() {
      popup.querySelectorAll('[role="option"]').forEach((el,i)=>{
        el.classList.toggle('is-active',i===state.index);
        el.setAttribute('aria-selected',i===state.index?'true':'false');
      });
      const el=popup.querySelectorAll('[role="option"]')[state.index];
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
      state={mode:'field', items:fieldChoices(getFields()),index:0,caret:input.selectionStart};
      draw();
    }
    function showValueList(ctx) {
      const all=valueChoices(ctx.field);
      const needle=ctx.typed.toLocaleLowerCase();
      const items=all.filter(x=>x.label.toLocaleLowerCase().includes(needle) || x.value.toLocaleLowerCase().includes(needle));
      state={mode:'value',field:ctx.field, items, index:0,valueStart:ctx.valueStart, typed:ctx.typed};
      draw();
    }
    function choose(i) {
      if (!state || !state.items[i]) return;
      const chosen=state.items[i];
      if (state.mode==='field') {
        const caret=input.selectionStart;
        const needsSpace=caret>0 && !/[\s(]/u.test(input.value[caret-1]);
        const insertion=(needsSpace?' ':'')+quoteAtom(chosen.insertName)+'=';
        close(); replace(caret,caret,insertion);
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
        event.preventDefault(); event.stopImmediatePropagation(); showFieldList(); return;
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
      if ((event.key==='Tab' || event.key==='Enter') && state.items.length) {
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
    input.addEventListener('blur',()=>{close();});
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
