// studio_work_0268: Smart Search help is grounded in the parser grammar, with
// hover and keyboard-focus access, without stealing focus from the query field.
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
const html=fs.readFileSync('wwwroot/index.html','utf8');
const css=fs.readFileSync('wwwroot/styles.css','utf8');
const js=fs.readFileSync('wwwroot/js/ui/studio_smart_search_help.js','utf8');
const engine=fs.readFileSync('wwwroot/js/responsibilities/smart_search_engine.js','utf8');
const context={document:{addEventListener(){}}}; vm.createContext(context);
vm.runInContext(js,context);

test('Help icon is embedded at the right edge of the query, independent of the label/input',()=>{
  assert.match(html, /studio-full-text-search-input-wrap/);
  assert.match(html, /id="studioSmartSearchHelpButton"/);
  assert.match(html, /aria-label="Smart Search の検索記号ヘルプ"/);
  assert.match(html, /id="studioSmartSearchHelpTooltip"[^>]*role="tooltip" hidden/);
  assert.match(html, /js\/ui\/studio_smart_search_help\.js/);
  assert.match(css, /#searchSection \.studio-smart-search-help-holder\s*\{[^}]*position:\s*absolute;/);
  assert.match(css, /#searchSection \.studio-full-text-search-input-wrap > #studioFullTextSearchInput\s*\{[^}]*padding-right:\s*34px;/);
});

test('Help is Markdown and describes the actually supported grammar',()=>{
  const md=context.StudioSmartSearchHelp.markdown;
  for(const token of ['AND', 'or', '(', '==', '!=', '=!', '>=', '<=', '=>', '=<', '..', '"Flux A"', '/', 'Tab', 'Enter', '→']) {
    assert.ok(md.includes(token),`missing help token: ${token}`);
  }
  for(const operator of ['==','!=','=!','>=','=>','<=','=<','=','>','<']){
    assert.ok(engine.includes(`'${operator}':`),`engine missing help operator: ${operator}`);
  }
  assert.match(js,/renderMarkdownContent\(markdown,\{enabled:true\}\)/);
  assert.match(css,/\.studio-smart-search-help-panel\[hidden\] \{ display: none !important; \}/);
});

test('Help opens on hover or keyboard focus and closes on escape, while lifting card above grid',()=>{
  assert.match(js,/holder\.addEventListener\('pointerenter',open\)/);
  assert.match(js,/holder\.addEventListener\('pointerleave'/);
  assert.match(js,/holder\.addEventListener\('focusin',open\)/);
  assert.match(js,/holder\.addEventListener\('focusout'/);
  assert.match(js,/event\.key==='Escape'/);
  assert.match(js,/section\.classList\.add\('studio-smart-search-help-open'\)/);
  assert.match(js,/section\.classList\.remove\('studio-smart-search-help-open'\)/);
  assert.match(css,/#searchSection\.studio-smart-search-help-open \{ z-index: 12; \}/);
});

test('Pointer can cross the gap into the Markdown help panel without closing it',()=>{
  assert.match(css, /#searchSection\.studio-smart-search-help-open \.studio-smart-search-help-holder::after\s*\{[^}]*height:\s*8px/s);
  assert.match(js, /tooltip\.addEventListener\('pointerenter',open\)/);
  assert.match(js, /holder\.addEventListener\('pointerleave',schedulePointerClose\)/);

  // Use a fake clock to verify the event order at the hover boundary without
  // depending on a particular browser's event dispatch timing.
  const pending=new Map(); let nextId=1;
  const listeners={};
  const document={
    activeElement:null,
    addEventListener(name,fn){listeners[name]=fn;}
  };
  const state=new Set();
  function element(){
    const map={};
    return {
      on:map,
      addEventListener(name,fn){map[name]=fn;},
      setAttribute(name,value){this[name]=value;},
      classList:{add(key){state.add(key)},remove(key){state.delete(key)}},
      blur(){document.activeElement=null}
    };
  }
  const holder=element(), button=element(), tooltip=element(), section=element();
  holder.contains=target=>target===holder||target===button||target===tooltip;
  tooltip.hidden=true;
  const stub={
    document,
    setTimeout(fn){const id=nextId++;pending.set(id,fn);return id;},
    clearTimeout(id){pending.delete(id);},
    renderMarkdownContent:()=>'<h3>help</h3>'
  };
  vm.createContext(stub);vm.runInContext(js,stub);
  const help=stub.StudioSmartSearchHelp.setup({holder,button,tooltip,section});
  holder.on.pointerenter();
  assert.equal(help.isOpen(),true);
  holder.on.pointerleave();
  assert.equal(help.isOpen(),true,'moving through the gap must not close synchronously');
  assert.equal(pending.size,1,'close is deferred during the visual gap');
  tooltip.on.pointerenter();
  assert.equal(pending.size,0,'entering the tooltip cancels the deferred close');
  assert.equal(tooltip.hidden,false);
  assert.equal(help.isOpen(),true);
  holder.on.pointerleave();
  assert.equal(pending.size,1);
  for(const fn of [...pending.values()])fn();
  assert.equal(help.isOpen(),false,'leaving both trigger and tooltip still closes');
  assert.equal(tooltip.hidden,true);
  assert.equal(state.has('studio-smart-search-help-open'),false);
});


test('Help uses readable Markdown comparison tables, rendered by the existing Studio renderer',()=>{
  const md=context.StudioSmartSearchHelp.markdown;
  assert.match(md,/\| 入力① \| 入力② \| 意味 \|/);
  assert.match(md,/\| 検索式 \| 意味 \|/);
  assert.match(md,/\| 操作・入力例 \| 動作 \|/);
  const count=md.split('\n').filter(line=>/^\| --- \|/.test(line)).length;
  assert.ok(count>=4,'basic, operators, nesting and completion must each have a table');
  const renderer={registerFieldControl(){},registerRenderer(){}};
  vm.createContext(renderer);
  vm.runInContext(fs.readFileSync('wwwroot/js/renderers/field_controls.js','utf8'),renderer);
  const html=renderer.renderMarkdownContent(md,{enabled:true});
  assert.equal((html.match(/<table>/g)||[]).length,5,'all Markdown tables must become HTML tables');
  assert.match(html,/<th[^>]*>入力①<\/th>/);
  assert.match(html,/<code class="md-inline-code">A=&gt;2<\/code>/);
  assert.match(css,/#searchSection \.studio-smart-search-help-panel \.md-table-scroll th/);
  assert.match(css,/#searchSection \.studio-smart-search-help-panel \.md-table-scroll table\s*\{[^}]*min-width:\s*0;/s, 'help table must override global 980px Grid minimum');
});
