import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import path from 'node:path';
import vm from 'node:vm';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../../..');
const read = relative => readFileSync(path.join(root, relative), 'utf8');

function guardContext() {
  const nodes = new Map();
  const saveBtn = {
    disabled: false, textContent: '', dataset: {}, title: '',
    classList: { toggle() {} },
    setAttribute() {}, addEventListener() {}
  };
  nodes.set('saveBtn', saveBtn);
  const document = {
    readyState: 'complete', scripts: [],
    head: { appendChild(node) { if (node?.id) nodes.set(node.id, node); } },
    createElement() { return { id: '', style: {}, textContent: '' }; },
    getElementById(id) { return nodes.get(id) || null; },
    addEventListener() {},
  };
  const window = {
    setTimeout() {}, setInterval() {},
    addEventListener() {}, confirm() { return true; }
  };
  const ctx = vm.createContext({
    window, document, sourceData: { rows: [{ id: 1 }] },
    launchRuntime: { readonly: false }, currentDataApiUrl: '/api/data/test.json',
    console
  });
  vm.runInContext(read('wwwroot/js/runtime/json_unsaved_guard.js'), ctx);
  return { ctx, saveBtn, guard: window.FrbJsonObjectUnsavedGuard };
}

test('非同期の保存応答が返っても、保存開始後の変更は未保存●として残る', () => {
  const { ctx, guard, saveBtn } = guardContext();
  ctx.sourceData.rows[0].id = 2;
  guard.refresh();
  assert.match(saveBtn.textContent, /^●/);
  const sent = guard.captureSaveState();
  ctx.sourceData.rows[0].id = 3;
  guard.markSavedState(sent);
  assert.equal(guard.hasUnsavedChanges(), true);
  assert.match(saveBtn.textContent, /^●/);
  const latest = guard.captureSaveState();
  guard.markSavedState(latest);
  assert.equal(guard.hasUnsavedChanges(), false);
  assert.doesNotMatch(saveBtn.textContent, /^●/);
});

test('保存要求が失敗した場合は保存済みとしてマークされない', () => {
  const { ctx, guard, saveBtn } = guardContext();
  ctx.sourceData.rows.pop(); // confirmed Grid deletion is a canonical mutation
  guard.refresh();
  assert.equal(guard.hasUnsavedChanges(), true);
  assert.match(saveBtn.textContent, /^●/);
  assert.match(read('wwwroot/js/renderers/grid_detail.js'),
    /currentRows\.splice\(selectedIndex, 1\);[\s\S]*?FrbJsonObjectUnsavedGuard\?\.refresh\?\.\(\)/);
});

test('Save Coordinatorは子Grid同期を先に待ち、同時Saveは直列化する', async () => {
  const ctx = vm.createContext({
    window: { FrbJsonObjectUnsavedGuard: null },
    sourceData: { items: [{ id: 1 }] },
    selectedIndex: -1, detailMode: 'edit',
    currentDataApiUrl: '/api/data/test.json',
    currentDataSourceKind: 'data', lastLoadedDefName: '',
    viewDef: {}, currentDataSources: {}, currentDataSourceSpecs: {},
    virtualDataJoinBaselines: new Map(),
    headerDef() { return null; },
    applyHeaderEdits() {},
    awaitRelatedGridSyncBeforeSave() { return ctx.barrier; },
    writeBackVirtualDataEdits: async () => [],
    ensureViewDefNameInData() {}, selectedDefName() { return ''; },
    virtualDataArrayConfigOf() { return []; },
    getByPath() {}, setStatus() {},
    registerRenderer() {},
    $() { return { open: false }; },
    fetch(url, request) { ctx.saves.push({ url, request }); return Promise.resolve({ ok: true }); },
    saves: [],
    console
  });
  vm.runInContext(read('wwwroot/js/runtime/detail_save.js'), ctx);
  let release;
  ctx.barrier = new Promise(resolve => { release = resolve; });
  const first = vm.runInContext('saveOverwriteJson()', ctx);
  const second = vm.runInContext('saveOverwriteJson()', ctx);
  await Promise.resolve();
  assert.equal(ctx.saves.length, 0, 'no POST before child sync');
  release();
  await Promise.all([first, second]);
  assert.equal(ctx.saves.length, 1, 'no concurrent duplicate saves');
});
