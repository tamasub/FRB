import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { runInNewContext } from 'node:vm';
const runtime = readFileSync(new URL('../../../wwwroot/js/runtime/load_runtime.js', import.meta.url), 'utf8');
const start = runtime.indexOf('function applyLaunchPageFromQuery(params) {');
const end = runtime.indexOf('// Launch context-menu creation:', start);
assert.ok(start > 0 && end > start);
const source = runtime.slice(start, end);

function setup() {
  let rendered = 0, focused = 0, scrolled = 0;
  const viewport = { scrollTop: 30, scrollHeight: 1000, clientHeight: 400, getBoundingClientRect: () => ({top: 100}) };
  const row = {
    dataset: {groupId:'windows'},
    getBoundingClientRect: () => ({top: 275 - (viewport.scrollTop - 30)}),
    closest: key => key === '.table-wrap' ? viewport : null,
    focus: () => { focused++; }
  };
  const state = {flat: true, collapsed: new Set(['group:windows']), selectedGroup: null};
  const statuses=[];
  const context = {
    sourceData:{pages:[{page_id:'windows',title:'Windows'}]},
    currentRows:[{item_id:'abc',page_id:'windows'}],
    selectedIndex:0,
    gridDef:()=>({dataPath:'$.items'}),
    studioTreeConfig:()=>({groupRoots:true}),
    studioTreeState:()=>state,
    renderGrid:()=>{rendered++;},
    setStatus:(...args)=>{statuses.push(args)},
    document: {
      querySelectorAll:()=>[row],
      querySelector:()=>({getBoundingClientRect:()=>({height:35})})
    }
  };
  runInNewContext(`${source}\nthis.applyPage = applyLaunchPageFromQuery;`, context);
  return {context, state, viewport, statuses, stats:()=>({rendered, focused, scrolled})};
}

test('Page property targets the virtual group header, scrolls it to first visible row, and does not open details',()=>{
  const {context, state, viewport, stats} = setup();
  assert.equal(context.applyPage(new URLSearchParams('launchPageId=windows')), true);
  assert.equal(state.selectedGroup, 'windows');
  assert.equal(state.flat, false);
  assert.equal(state.collapsed.has('group:windows'), false);
  assert.equal(context.selectedIndex, -1);
  assert.equal(viewport.scrollTop, 30+275-100-35);
  assert.equal(stats().rendered, 1);
  assert.equal(stats().focused, 1);
});

test('invalid Page ID is not mistaken for a menu item',()=>{
  const {context, statuses, stats} = setup();
  assert.equal(context.applyPage(new URLSearchParams('launchPageId=bad-page')), false);
  assert.equal(stats().rendered, 0);
  assert.equal(statuses.length, 1);
});


test('last Page is bottom-aligned when there is insufficient content to put its header on top',()=>{
  const {context, viewport} = setup();
  // Page heading is at document position 250 but scrolling ends at 70px.
  viewport.scrollHeight = 470;
  viewport.clientHeight = 400;
  assert.equal(context.applyPage(new URLSearchParams('launchPageId=windows')), true);
  assert.equal(viewport.scrollTop, 70);
});

test('Page scroll alignment is adjusted once layout has settled',()=>{
  const {context, viewport} = setup();
  const callbacks = [];
  context.requestAnimationFrame = fn => callbacks.push(fn);
  viewport.scrollHeight = 470;
  viewport.clientHeight = 400;
  assert.equal(context.applyPage(new URLSearchParams('launchPageId=windows')), true);
  assert.equal(viewport.scrollTop, 70);
  viewport.scrollHeight = 1050;
  callbacks.shift()();
  callbacks.shift()();
  assert.equal(viewport.scrollTop, 30 + 275 - 100 - 35);
});
