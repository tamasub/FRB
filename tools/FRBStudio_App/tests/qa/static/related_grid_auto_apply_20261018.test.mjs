import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import vm from 'node:vm';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../../..');
const related = readFileSync(path.join(root, 'wwwroot/js/runtime/related_grid_view.js'), 'utf8');
const detail = readFileSync(path.join(root, 'wwwroot/js/runtime/detail_save.js'), 'utf8');
const grid = readFileSync(path.join(root, 'wwwroot/js/renderers/grid_detail.js'), 'utf8');
const clone = v => JSON.parse(JSON.stringify(v));

function context(rows) {
  const messages = [];
  const statuses = [];
  const window = {
    closed: false,
    setTimeout, clearTimeout,
    addEventListener() {},
    postMessage(message) { messages.push(clone(message)); },
    FrbJsonObjectUnsavedGuard: { refresh() {} }
  };
  const ctx = vm.createContext({
    window,
    document: { body: { classList: { add() {} } }, querySelectorAll: () => [], getElementById: () => null },
    location: { origin: 'http://studio.local', search: '', href: 'http://studio.local/index.html' },
    URL, URLSearchParams,
    sourceData: { governance_items: clone(rows) }, viewDef: null,
    currentRows: null, selectedIndex: -1,
    cloneData: clone,
    getByPath: (obj, path) => path.split('.').reduce((v, k) => v?.[k], obj),
    setByPath: (obj, path, value) => { obj[path] = value; },
    stableStringify: JSON.stringify,
    setStatus: (...v) => statuses.push(v),
    virtualDataArrayConfigOf: () => [], virtualDataTargetPath: () => '',
    registerStudioAction() {},
    renderGrid() {}, loadRows() {},
    gridDef: () => ({ dataPath: '' }),
    $: () => null,
    console
  });
  vm.runInContext(related, ctx, { filename: 'related_grid_view.js' });
  return { ctx, window, messages, statuses };
}

function setup() {
  const rows = [{ id: 1, title: 'A' }, { id: 2, title: 'B' }];
  const parent = context(rows);
  const child = context(rows);
  child.window.parent = parent.window;
  const baseline = JSON.stringify(rows);
  vm.runInContext(`relatedGridChildRuntime = {
    channel: 'channel1', dataPath: 'governance_items', baseline: ${JSON.stringify(baseline)},
    loaded: true, applyPending: false, syncBlocked: false
  }`, child.ctx);
  vm.runInContext(`relatedGridParentSessions.set('channel1', {
    channel: 'channel1', definition: { dataPath: 'governance_items', caption: '憲法' },
    child: window.childRef, sourceDataRef: sourceData, baseline: ${JSON.stringify(baseline)}
  })`, Object.assign(parent.ctx, { /* populated below */ }));
  // The parent compares event.source with the specific child window.
  parent.ctx.window.childRef = child.window;
  // Fix session child after window reference becomes available.
  vm.runInContext(`relatedGridParentSessions.get('channel1').child = window.childRef`, parent.ctx);
  return { parent, child };
}

function dispatchParent(parent, child) {
  const msg = parent.messages.shift();
  assert.ok(msg, 'child emitted APPLY');
  vm.runInContext('handleParentRelatedGridMessage(__event, __message)', Object.assign(parent.ctx, {
    __event: { source: child.window }, __message: msg
  }));
  return msg;
}
async function dispatchChild(parent, child) {
  const msg = child.messages.shift();
  assert.ok(msg, 'parent emitted APPLY_RESULT');
  await vm.runInContext('handleChildRelatedGridMessage(__event, __message)', Object.assign(child.ctx, {
    __event: { source: parent.window }, __message: msg
  }));
  return msg;
}

test('別Gridには手動の「親画面へ反映」ボタンを表示しない', () => {
  assert.doesNotMatch(related, /function ensureRelatedGridApplyButton\(/);
  assert.doesNotMatch(related, /textContent = '親画面へ反映'/);
  assert.match(related, /function queueRelatedGridAutoApply\(/);
});

test('F12, F7/F8 は検証成功後にのみ自動同期する', () => {
  assert.match(detail, /finalizeValidatedDetailCommit\(pending, selectedIndex\);\s*if \(typeof queueRelatedGridAutoApply/);
  assert.match(detail, /currentRows\.push\(pending\);\s*if \(typeof queueRelatedGridAutoApply/);
  assert.match(grid, /tryCommitCurrentDetailEdits\(\{ source: 'navigation' \}\)/);
  assert.match(grid, /nextPos < 0 \|\| nextPos >= filteredRows.length[\s\S]*?relatedGridChildRuntime/);
  assert.match(grid, /currentRows\.splice\(selectedIndex, 1\);[\s\S]*?if \(typeof queueRelatedGridAutoApply/);
});

test('高速連続確定は応答を待って最後の状態まで同期し、成功メッセージを表示しない', async () => {
  const { parent, child } = setup();
  child.ctx.sourceData.governance_items[0].title = 'A1';
  assert.equal(vm.runInContext('queueRelatedGridAutoApply()', child.ctx), true);
  assert.equal(parent.messages.length, 1);
  // F8 and then F12 while first APPLY is pending.
  child.ctx.sourceData.governance_items[1].title = 'B2';
  vm.runInContext('queueRelatedGridAutoApply()', child.ctx);
  assert.equal(parent.messages.length, 1, 'no parallel APPLY with stale baseline');
  dispatchParent(parent, child);
  await dispatchChild(parent, child);
  assert.equal(parent.messages.length, 1, 'latest revision sent after ACK');
  dispatchParent(parent, child);
  await dispatchChild(parent, child);
  assert.equal(parent.ctx.sourceData.governance_items[0].title, 'A1');
  assert.equal(parent.ctx.sourceData.governance_items[1].title, 'B2');
  assert.equal(parent.messages.filter(message => message.type === 'APPLY').length, 0);
  assert.ok(parent.messages.every(message => message.type === 'SYNC_IDLE'));
  assert.equal(child.statuses.length, 0);
  assert.equal(parent.statuses.length, 0);
  assert.equal(vm.runInContext('relatedGridChildIsDirty()', child.ctx), false);
});

test('別Gridの追加・削除も最後の配列だけを親へ反映する', async () => {
  const { parent, child } = setup();
  child.ctx.sourceData.governance_items.push({ id: 3, title: 'C' });
  vm.runInContext('queueRelatedGridAutoApply()', child.ctx);
  child.ctx.sourceData.governance_items.splice(0, 1);
  vm.runInContext('queueRelatedGridAutoApply()', child.ctx);
  dispatchParent(parent, child); await dispatchChild(parent, child);
  dispatchParent(parent, child); await dispatchChild(parent, child);
  assert.deepEqual(clone(parent.ctx.sourceData.governance_items).map(x => x.id), [2,3]);
});

test('競合時は上書きせず再送信を停止し、エラーだけ通知する', async () => {
  const { parent, child } = setup();
  child.ctx.sourceData.governance_items[0].title = 'child changed';
  vm.runInContext('queueRelatedGridAutoApply()', child.ctx);
  parent.ctx.sourceData.governance_items[0].title = 'parent changed';
  dispatchParent(parent, child);
  await dispatchChild(parent, child);
  assert.equal(parent.ctx.sourceData.governance_items[0].title, 'parent changed');
  assert.equal(vm.runInContext('relatedGridChildRuntime.syncBlocked', child.ctx), true);
  assert.equal(parent.messages.length, 0);
  assert.equal(child.statuses.length, 1);
  assert.equal(vm.runInContext('relatedGridChildIsDirty()', child.ctx), true);
});


test('モーダルは自動同期中に閉じず、ACK後に通知なしで閉じる', async () => {
  const { parent, child } = setup();
  // Mock the parent overlay and same-origin child helpers.
  parent.ctx.document.body.classList.remove = () => {};
  parent.ctx.document.querySelector = () => null;
  const overlay = { removed: false, remove() { this.removed = true; } };
  vm.runInContext('relatedGridParentSessions.get("channel1").modalOverlay = window.modalOverlay',
    Object.assign(parent.ctx, { window: Object.assign(parent.window, { modalOverlay: overlay }) }));
  child.window.relatedGridChildIsDirty = () => vm.runInContext('relatedGridChildIsDirty()', child.ctx);
  child.window.relatedGridChildApplyPending = () => vm.runInContext('relatedGridChildApplyPending()', child.ctx);
  child.window.queueRelatedGridAutoApply = () => vm.runInContext('queueRelatedGridAutoApply()', child.ctx);
  child.window.approveRelatedGridChildClose = () => vm.runInContext('approveRelatedGridChildClose()', child.ctx);
  child.ctx.sourceData.governance_items[0].title = 'changed';
  vm.runInContext('queueRelatedGridAutoApply()', child.ctx);
  assert.equal(vm.runInContext('closeRelatedGridModal("channel1")', parent.ctx), false);
  assert.equal(overlay.removed, false);
  dispatchParent(parent, child);
  await dispatchChild(parent, child);
  const idle = parent.messages.shift();
  assert.equal(idle.type, 'SYNC_IDLE');
  vm.runInContext('handleParentRelatedGridMessage(__event, __message)', Object.assign(parent.ctx, {
    __event: { source: child.window }, __message: idle
  }));
  assert.equal(overlay.removed, true);
  assert.equal(parent.statuses.length, 0);
});


test('親画面保存は子Gridの連続APPLYの最終ACKまで待機する', async () => {
  const { parent, child } = setup();
  child.ctx.sourceData.governance_items[0].title = '初回';
  vm.runInContext('queueRelatedGridAutoApply()', child.ctx);
  const wait = vm.runInContext('awaitRelatedGridSyncBeforeSave()', parent.ctx);
  const prepare = child.messages.shift();
  assert.equal(prepare.type, 'PREPARE_SAVE');
  await vm.runInContext('handleChildRelatedGridMessage(__event, __message)', Object.assign(child.ctx, {
    __event: { source: parent.window }, __message: prepare
  }));
  let ready = false;
  wait.then(() => { ready = true; });
  await Promise.resolve();
  assert.equal(ready, false);
  child.ctx.sourceData.governance_items[1].title = '後続';
  vm.runInContext('queueRelatedGridAutoApply()', child.ctx);
  // First APPLY, then its result, still waiting for second APPLY.
  dispatchParent(parent, child);
  await dispatchChild(parent, child);
  await Promise.resolve();
  assert.equal(ready, false);
  dispatchParent(parent, child);
  await dispatchChild(parent, child);
  const replies = parent.messages.splice(0);
  const readyReply = replies.find(x => x.type === 'SAVE_READY');
  assert.ok(readyReply?.ok);
  vm.runInContext('handleParentRelatedGridMessage(__event, __message)', Object.assign(parent.ctx, {
    __event: { source: child.window }, __message: readyReply
  }));
  await wait;
  assert.equal(ready, true);
  assert.equal(parent.ctx.sourceData.governance_items[0].title, '初回');
  assert.equal(parent.ctx.sourceData.governance_items[1].title, '後続');
});

test('子Grid競合時は保存バリアが拒否され古い状態での保存に進まない', async () => {
  const { parent, child } = setup();
  child.ctx.sourceData.governance_items[0].title = 'child';
  vm.runInContext('queueRelatedGridAutoApply()', child.ctx);
  const waiting = vm.runInContext('awaitRelatedGridSyncBeforeSave()', parent.ctx);
  const prep = child.messages.shift();
  await vm.runInContext('handleChildRelatedGridMessage(__event, __message)', Object.assign(child.ctx, {
    __event: { source: parent.window }, __message: prep
  }));
  parent.ctx.sourceData.governance_items[0].title = 'parent';
  dispatchParent(parent, child);
  await dispatchChild(parent, child);
  const failed = parent.messages.find(x => x.type === 'SAVE_READY');
  assert.equal(failed.ok, false);
  vm.runInContext('handleParentRelatedGridMessage(__event, __message)', Object.assign(parent.ctx, {
    __event: { source: child.window }, __message: failed
  }));
  await assert.rejects(waiting, /同期|保存/);
  assert.equal(parent.ctx.sourceData.governance_items[0].title, 'parent');
});
