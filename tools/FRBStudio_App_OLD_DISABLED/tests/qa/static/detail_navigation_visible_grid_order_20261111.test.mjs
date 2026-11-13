import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import test from 'node:test';
import vm from 'node:vm';

const source = fs.readFileSync(path.join(process.cwd(), 'wwwroot/js/renderers/grid_detail.js'), 'utf8');

function setup({ shown=[2, 0, 3, 1], selected=2, allowCommit=true, editorMode='edit', hasGrid=true }={}) {
  const prev = { disabled: null };
  const next = { disabled: null };
  const opened = [];
  const calls = [];
  const listeners = new Map();
  const host = hasGrid ? {
    querySelectorAll(selector) {
      assert.match(selector, /tr\[data-source-index\]/);
      assert.match(selector, /document-grid-card\[data-source-index\]/);
      return shown.map(index => ({ dataset: { sourceIndex: String(index) } }));
    }
  } : null;
  const ctx = {
    console,
    currentRows: [{ id:'a' }, { id:'b' }, { id:'c' }, { id:'d' }],
    // The cached data source order may differ from what is actually rendered.
    filteredRows: [0, 1, 2, 3].map(index => ({ row:{}, index })),
    selectedIndex: selected,
    detailMode: editorMode,
    relatedGridChildRuntime: null,
    document: { addEventListener(name, handler) { listeners.set(name, handler); } },
    registerRenderer() {},
    $: name => ({ dataGrid:host, prevDetailBtn:prev, nextDetailBtn:next, detailDialog:{open:true} })[name] ?? null,
    tryCommitCurrentDetailEdits() { calls.push('commit'); return allowCommit; },
    renderGrid() { calls.push('render'); },
    openDetail(index, keepOpen) { opened.push({index, keepOpen}); },
  };
  vm.createContext(ctx);
  vm.runInContext(source, ctx, { filename:'grid_detail.js' });
  // Replace the renderer with a spy: this test exercises the original navigation
  // functions, without constructing the rest of Studio's UI.
  ctx.renderGrid = () => { calls.push('render'); };
  return {
    ctx, prev, next, opened, calls,
    position: () => vm.runInContext('currentFilteredPosition()', ctx),
    refresh: () => vm.runInContext('updateDetailNavButtons()', ctx),
    move: delta => vm.runInContext(`moveDetail(${delta})`, ctx),
    key: key => {
      let prevented = false;
      listeners.get('keydown')({ key, preventDefault() { prevented = true; } });
      return prevented;
    }
  };
}

test('Editor F8/F7 follows the visible sorted Grid order, not JSON array order', () => {
  const s = setup({shown:[2, 0, 3, 1], selected:2});
  assert.equal(s.position(), 0);
  s.refresh();
  assert.equal(s.prev.disabled, true);
  assert.equal(s.next.disabled, false);
  assert.equal(s.key('F8'), true);
  assert.equal(s.ctx.selectedIndex, 0);
  s.move(1);
  assert.equal(s.ctx.selectedIndex, 3);
  assert.equal(s.key('F7'), true);
  assert.equal(s.ctx.selectedIndex, 0);
  assert.deepEqual(s.opened.map(item=>item.index), [0,3,0]);
  assert.ok(s.opened.every(item=>item.keepOpen===true));
  assert.equal(s.calls.filter(x=>x==='commit').length, 3);
});

test('Filtered rows: navigation remains within the displayed subset and ends are disabled', () => {
  const s = setup({shown:[3, 1], selected:3});
  s.refresh();
  assert.equal(s.prev.disabled, true);
  assert.equal(s.next.disabled, false);
  s.move(1);
  assert.equal(s.ctx.selectedIndex, 1);
  s.refresh();
  assert.equal(s.prev.disabled, false);
  assert.equal(s.next.disabled, true);
  const committed = s.calls.length;
  s.move(1);
  assert.equal(s.ctx.selectedIndex, 1);
  assert.equal(s.calls.length, committed);
});

test('Tree view: group rows and collapsed (not rendered) members are never navigation targets', () => {
  const s = setup({shown:[-2,3,-3,1], selected:3});
  s.refresh();
  assert.equal(s.prev.disabled, true);
  s.move(1);
  assert.equal(s.ctx.selectedIndex, 1);
  s.move(-1);
  assert.equal(s.ctx.selectedIndex, 3);
  s.ctx.selectedIndex = 2; // collapsed, no longer in visible rows
  s.refresh();
  assert.equal(s.prev.disabled, true);
  assert.equal(s.next.disabled, true);
  s.move(1);
  assert.equal(s.ctx.selectedIndex, 2);
});

test('Document card Grid also follows the order of displayed cards', () => {
  const s = setup({shown:[1,3,0], selected:1});
  s.move(1);
  assert.equal(s.ctx.selectedIndex, 3);
  s.move(1);
  assert.equal(s.ctx.selectedIndex, 0);
});

test('Failed validation prevents navigation and preserves selection', () => {
  const s = setup({shown:[2,0,3,1], selected:2, allowCommit:false});
  s.move(1);
  assert.equal(s.ctx.selectedIndex, 2);
  assert.deepEqual(s.opened, []);
  assert.deepEqual(s.calls, ['commit']);
});

test('New-record editor disables prev/next, and no rendered Grid rows yield no navigation', () => {
  const fresh = setup({shown:[0,1], selected:-1, editorMode:'new'});
  fresh.refresh();
  assert.equal(fresh.prev.disabled, true);
  assert.equal(fresh.next.disabled, true);
  fresh.move(1);
  assert.equal(fresh.ctx.selectedIndex, -1);
  const hidden = setup({shown:[], selected:0});
  hidden.refresh();
  assert.equal(hidden.prev.disabled, true);
  assert.equal(hidden.next.disabled, true);
  hidden.move(1);
  assert.equal(hidden.ctx.selectedIndex, 0);
});

test('Fallback before Grid mounting remains compatible with filteredRows order', () => {
  const s = setup({hasGrid:false, selected:1});
  assert.equal(s.position(), 1);
  s.move(1);
  assert.equal(s.ctx.selectedIndex, 2);
});
