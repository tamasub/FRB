// FRB Smart Search v0.1 — opt-in, host-agnostic public interface.
// Depends on the existing StudioSmartSearch and optional StudioSmartSearchEditor/History scripts.
// No ViewDef, SQLite, window.fs, server or NativeShell dependency in this adapter.
var FRBSmartSearch = (function () {
  'use strict';

  const TYPES = new Set(['string','text','textarea','markdown','number','integer','float','decimal','date','datetime','instant','boolean','select','enum']);
  const canonType = type => ({string:'text',textarea:'text',markdown:'text',enum:'select'})[type] || type;

  function normalizeFields(input) {
    if (!Array.isArray(input)) throw new TypeError('fields must be an array');
    const ids = new Set();
    return input.map((entry,i) => {
      if (!entry || typeof entry !== 'object') throw new TypeError(`fields[${i}] must be an object`);
      const field = String(entry.field ?? entry.id ?? '').trim();
      if (!field) throw new TypeError(`fields[${i}].field is required`);
      if (ids.has(field)) throw new TypeError(`duplicate field: ${field}`);
      ids.add(field);
      const rawType = String(entry.type ?? 'string').toLowerCase();
      if (!TYPES.has(rawType)) throw new TypeError(`unsupported field type: ${rawType}`);
      const caption = String(entry.caption ?? entry.label ?? field);
      const options = entry.options ?? [];
      if (!Array.isArray(options)) throw new TypeError(`fields[${i}].options must be an array`);
      // The original parser/evaluator and completion engine operate on these minimal keys.
      return Object.freeze({
        field, caption, type:canonType(rawType), options:options.map(v =>
          v != null && typeof v === 'object'
            ? {value:String(v.value ?? v.cd ?? v.id ?? ''),label:String(v.label ?? v.name ?? v.value ?? v.cd ?? '')}
            : {value:String(v),label:String(v)}
        ),
        // Advanced resolver compatibility. Optional; not required by a consumer app.
        ...(entry.value_family ? {value_family:entry.value_family} : {}),
        ...(entry.validation_type ? {validation_type:entry.validation_type} : {})
      });
    });
  }

  function defaultStorage() {
    try { if (typeof localStorage !== 'undefined') return localStorage; } catch { /* disabled by host */ }
    // In a restricted WebView the history UI may still work for this session.
    // This fallback is deliberately NOT claimed to persist across restarts.
    const values=new Map();
    return {getItem:key=>values.get(key)??null,setItem:(key,value)=>{values.set(key,String(value));}};
  }

  function create(options={}) {
    if (typeof StudioSmartSearch === 'undefined') throw new Error('load smart_search_engine.js before frb_smart_search_api.js');
    const getFields = typeof options.getFields === 'function'
      ? () => normalizeFields(options.getFields())
      : () => normalizedFields;
    const normalizedFields = options.getFields ? [] : normalizeFields(options.fields ?? []);
    const parse = query => StudioSmartSearch.parse(String(query ?? ''),getFields());
    const match = (row,queryOrAst) => StudioSmartSearch.evaluate(row,
      typeof queryOrAst === 'string' || queryOrAst == null ? parse(queryOrAst) : queryOrAst);
    const filter = (rows,query) => {
      if (!Array.isArray(rows)) throw new TypeError('rows must be an array');
      const ast=parse(query);
      return rows.filter(row => StudioSmartSearch.evaluate(row,ast));
    };
    let editor=null,history=null;
    // Optional browser UI. The host owns markup, search buttons, dataset load and persistence.
    function attach(ui={}) {
      if (editor) return {editor,history};
      const input=ui.input, host=ui.host;
      if (!input || !host) throw new TypeError('attach requires input and host elements');
      if (typeof StudioSmartSearchEditor==='undefined') throw new Error('load studio_smart_search_editor.js before attach()');
      host.classList.add('frb-smart-search-host');
      editor=StudioSmartSearchEditor.setup({
        input, section:host, getFields,
        onOpen:()=>history?.close()
      });
      if (ui.historyRegisterButton && ui.historyOpenButton && ui.searchButton) {
        if (typeof StudioSmartSearchHistory==='undefined') throw new Error('load studio_smart_search_history.js for optional history');
        history=StudioSmartSearchHistory.setup({
          input,section:host,registerBtn:ui.historyRegisterButton,
          dropdownBtn:ui.historyOpenButton,searchBtn:ui.searchButton,
          getDataKey:ui.getDataKey ?? (()=>'default'),
          storage:ui.storage ?? defaultStorage(),
          onOpen:()=>editor?.close()
        });
      }
      // Don't automatically bind Enter -> search. The consumer app must invoke its own
      // search action on ordinary Enter, and preserve the completer's capture handlers.
      return {editor,history};
    }
    return Object.freeze({getFields,parse,match,filter,attach});
  }

  return Object.freeze({create,normalizeFields});
})();
