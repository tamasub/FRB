const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');

const runtime = fs.readFileSync('wwwroot/js/runtime/load_runtime.js', 'utf8');
const options = fs.readFileSync('NativeShell/NativeLaunchOptions.cs', 'utf8');
const css = fs.readFileSync('wwwroot/styles.css', 'utf8');

function setup({ tree = true } = {}) {
  let closeCallback;
  const calls = [];
  const rowElement = {
    getBoundingClientRect: () => ({ top: 520 - viewport.scrollTop }),
    closest(selector) { assert.equal(selector, '.table-wrap'); return viewport; },
    focus(options) { calls.push(['focus', options.preventScroll]); }
  };
  const viewport = {
    scrollTop: 0, scrollHeight: 1200, clientHeight: 400,
    getBoundingClientRect: () => ({ top: 100 })
  };
  const document = {
    querySelector(selector) {
      if (selector === '#dataGrid thead') return { getBoundingClientRect: () => ({ height: 32 }) };
      if (/^#dataGrid tr\[data-source-index="\d+"\]$/.test(selector)) return rowElement;
      return null;
    }
  };
  const dialog = { addEventListener(type, fn, options) {
    assert.equal(type, 'close'); assert.equal(options.once, true); closeCallback = fn;
  } };
  const treeState = { collapsed: new Set(['group:work', 'folder', 'parent']), selectedGroup: 'other' };
  const context = {
    console,
    Map,
    URLSearchParams,
    document,
    requestAnimationFrame: fn => fn(),
    currentRows: [
      { item_id: 'folder', parent_item_id: '', page_id: 'work' },
      { item_id: 'parent', parent_item_id: 'folder', page_id: 'work' },
      { item_id: 'target', parent_item_id: 'parent', page_id: 'work' },
      { item_id: 'other', parent_item_id: '', page_id: 'work' }
    ],
    getByPath: (row, key) => row[key],
    $: key => key === 'detailDialog' ? dialog : null,
    setDetailDialogExpanded: value => calls.push(['expand', value]),
    openDetail: index => calls.push(['openDetail', index]),
    renderByKey: key => calls.push(['renderByKey', key]),
    renderGrid: () => calls.push(['renderGrid']),
    studioTreeConfig: () => tree ? { enabled: true, idField:'item_id', parentField:'parent_item_id', groupRoots: true, groupField:'page_id' } : null,
    studioTreeState: () => treeState,
    setStatus: () => {}
  };
  vm.runInNewContext(runtime, context, { filename: 'load_runtime.js' });
  return { context, treeState, calls, viewport, close: () => { assert.ok(closeCallback); closeCallback(); } };
}

test('Native Launch item-properties URL marks only item launches', () => {
  assert.match(options, /options\.LaunchItemId\s*!=\s*null[\s\S]*?launchItemProperties=1/);
  const pageBlock = options.slice(options.indexOf('if (options.LaunchPageId != null)'));
  assert.doesNotMatch(pageBlock, /launchItemProperties=1/);
});

test('Properties start expanded; parent categories and page are revealed', () => {
  const ui = setup();
  assert.equal(ui.context.applyLaunchFocusFromQuery(new URLSearchParams('focusField=item_id&focusValue=target&openDetail=true&launchItemProperties=1')), true);
  assert.deepEqual(ui.calls.slice(0, 3), [['renderByKey','grid'],['openDetail',2],['expand',true]]);
  for (const id of ['group:work','folder','parent']) assert.equal(ui.treeState.collapsed.has(id), false);
});

test('Closing the initial launch Editor returns to original row, selected and at the viewport top', () => {
  const ui = setup();
  ui.context.applyLaunchFocusFromQuery(new URLSearchParams('focusField=item_id&focusValue=target&openDetail=true&launchItemProperties=1'));
  // Navigation or reordering while the dialog is open must not change the original target.
  ui.context.selectedIndex = 3;
  ui.context.currentRows.unshift(ui.context.currentRows.pop());
  ui.close();
  assert.equal(ui.context.currentRows[ui.context.selectedIndex].item_id, 'target');
  assert.equal(ui.viewport.scrollTop, 388); // 520 - 100 - fixed Grid header 32
  assert.ok(ui.calls.find(call => call[0] === 'renderGrid'));
  assert.ok(ui.calls.find(call => call[0] === 'focus' && call[1] === true));
});

test('Ordinary URL focus does not maximize or install close behavior', () => {
  const ui = setup();
  ui.context.applyLaunchFocusFromQuery(new URLSearchParams('focusField=item_id&focusValue=target&openDetail=true'));
  assert.equal(ui.calls.some(call => call[0] === 'expand'), false);
  assert.throws(() => ui.close());
});

test('Page-property focus and non-open requests do not maximize', () => {
  const ui = setup({ tree: false });
  ui.context.applyLaunchFocusFromQuery(new URLSearchParams('focusField=item_id&focusValue=target&openDetail=false&launchItemProperties=1'));
  assert.equal(ui.calls.some(call => call[0] === 'openDetail'), false);
  assert.equal(ui.calls.some(call => call[0] === 'expand'), false);
});

test('Closing a deleted item does not select a different row', () => {
  const ui = setup();
  ui.context.applyLaunchFocusFromQuery(new URLSearchParams('focusField=item_id&focusValue=target&openDetail=true&launchItemProperties=1'));
  ui.context.currentRows.splice(2, 1);
  const count = ui.calls.length;
  ui.close();
  assert.equal(ui.calls.length, count);
});

test('Expanded Editor hides only the underlying page scrollbars and keeps inner scroll available', () => {
  assert.match(css, /html:has\(#detailDialog\[open\]\.detail-dialog-expanded\),\s*body:has\(#detailDialog\[open\]\.detail-dialog-expanded\)\s*\{\s*overflow-y: hidden/);
  assert.match(css, /#detailDialog \.detail-scroll-content\s*\{[^}]*overflow-y: auto;/);
  assert.match(css, /#detailDialog\.detail-dialog-expanded \.dialog-body\s*\{[^}]*max-height: 100%/);
});
