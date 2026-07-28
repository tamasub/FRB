import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const root = path.resolve(__dirname, '../../..');
const runtimeCode = fs.readFileSync(path.join(root, 'wwwroot/js/runtime/studio_json_round_trip.js'), 'utf8');

function getByPath(obj, pathName) {
  if (!pathName || pathName === '$') return obj;
  const normalized = String(pathName).replace(/^\$\.?/, '');
  return normalized.split('.').reduce((cur, key) => cur == null ? undefined : cur[key], obj);
}
function setByPath(obj, pathName, value) {
  const normalized = String(pathName).replace(/^\$\.?/, '');
  const parts = normalized.split('.');
  let cur = obj;
  for (let i = 0; i < parts.length - 1; i++) {
    if (!cur[parts[i]] || typeof cur[parts[i]] !== 'object') cur[parts[i]] = {};
    cur = cur[parts[i]];
  }
  cur[parts.at(-1)] = value;
}

function createRuntime() {
  const grid = {
    fields: [
      { field: 'id', type: 'text', readonly: true, edit: { visible: true, readonly: true } },
      { field: 'title', type: 'text', edit: { visible: true } },
      { field: 'memo', type: 'textarea', edit: { visible: true } },
      { field: 'tags', type: 'stringArray', edit: { visible: true, readonly: false } },
      { field: 'children', type: 'objectArray', edit: { visible: true, readonly: false } },
      { field: 'hidden_source', type: 'textarea', edit: { visible: false } },
      {
        field: '__chat', type: 'chat', edit: { visible: true, messages: [
          { field: 'hidden_source', readonly: false },
          { field: 'ai_note', readonly: true }
        ] }
      }
    ]
  };
  const detailDialog = {
    querySelectorAll: () => [],
    querySelector: () => null
  };
  const diffBadge = {
    textContent: '', title: '', classList: { add(){}, remove(){} }, removeAttribute(){}
  };
  const context = {
    console,
    window: {},
    document: { querySelectorAll: () => [] },
    navigator: {},
    detailMode: 'edit',
    draftRow: null,
    selectedIndex: 0,
    currentRows: [{
      id: 'r1', title: 'Before', memo: 'old', tags: ['a'],
      children: [{ name: 'one', score: 1 }], hidden_source: 'chat value', ai_note: 'readonly ai'
    }],
    gridDef: () => grid,
    cloneData: value => value == null ? value : JSON.parse(JSON.stringify(value)),
    getByPath,
    setByPath,
    isDetailSubGridEditable: field => !field.readonly && !field.edit?.readonly,
    applyDetailInputsToRow: () => {},
    renderDetailForRow: row => { context.lastRenderedRow = JSON.parse(JSON.stringify(row)); },
    setStatus: message => { context.lastStatus = message; },
    $: id => id === 'detailDialog' ? detailDialog : id === 'studioJsonRoundTripDiff' ? diffBadge : null,
    CSS: { escape: value => String(value) },
    setTimeout,
    structuredClone
  };
  context.window = context;
  vm.createContext(context);
  vm.runInContext(runtimeCode, context, { filename: 'studio_json_round_trip.js' });
  return context;
}

test('Copy JSON emits ViewDef detail fields, chat source fields, and subgrids', () => {
  const runtime = createRuntime();
  const copied = runtime.buildStudioDetailRoundTripJson();
  assert.deepEqual(JSON.parse(JSON.stringify(copied)), {
    id: 'r1',
    title: 'Before',
    memo: 'old',
    tags: ['a'],
    children: [{ name: 'one', score: 1 }],
    hidden_source: 'chat value',
    ai_note: 'readonly ai'
  });
});

test('Paste JSON applies partial editable fields and subgrids but skips readonly fields', () => {
  const runtime = createRuntime();
  const result = runtime.applyStudioDetailRoundTripObject({
    id: 'blocked',
    title: 'After',
    tags: ['x', 'y'],
    children: [{ name: 'two', score: 2 }],
    ai_note: 'blocked ai'
  });
  assert.deepEqual(JSON.parse(JSON.stringify(result.changes)), ['title', 'tags', 'children']);
  assert.deepEqual(JSON.parse(JSON.stringify(result.readonlyPaths)), ['id', 'ai_note']);
  assert.equal(runtime.lastRenderedRow.id, 'r1');
  assert.equal(runtime.lastRenderedRow.title, 'After');
  assert.deepEqual(runtime.lastRenderedRow.tags, ['x', 'y']);
  assert.deepEqual(runtime.lastRenderedRow.children, [{ name: 'two', score: 2 }]);
  assert.equal(runtime.lastRenderedRow.ai_note, 'readonly ai');
  assert.match(runtime.lastStatus, /F12/);
});

test('Paste JSON rejects invalid subgrid shapes atomically', () => {
  const runtime = createRuntime();
  assert.throws(
    () => runtime.applyStudioDetailRoundTripObject({ children: ['not-object'] }),
    /children\[0\]: オブジェクト/
  );
  assert.equal(runtime.lastRenderedRow, undefined);
});
