import { readFileSync } from 'node:fs';
import { test } from 'node:test';
import assert from 'node:assert/strict';
import vm from 'node:vm';

const code = readFileSync(new URL('../../../wwwroot/js/runtime/load_runtime.js', import.meta.url), 'utf8');

function createContext({dataPath='$.items'}={}) {
  const calls = [];
  const rows = [
    {page_id: 'work', parent_item_id: '', sort_order: 10},
    {page_id: 'windows', parent_item_id: '', sort_order: 20},
    {page_id: 'windows', parent_item_id: '', sort_order: 50}
  ];
  const sandbox = {
    URLSearchParams,
    currentRows: rows,
    gridDef: () => ({dataPath}),
    createDefaultRow: () => ({item_id: 'row_copy_1', launch_actions: [1]}),
    openNewDetail: row => calls.push(row),
    setStatus: (...args) => calls.push(args),
    crypto: {randomUUID: () => 'uuid-test'},
  };
  vm.createContext(sandbox);
  vm.runInContext(code, sandbox);
  return {sandbox, calls};
}

test('Launch new-category goes straight to the existing Studio new-detail path', () => {
  const {sandbox,calls} = createContext();
  const params = new URLSearchParams('launchNewCategory=1&newCategoryPage=windows');
  assert.equal(sandbox.applyLaunchNewCategoryFromQuery(params), true);
  assert.equal(calls.length, 1);
  assert.equal(calls[0].page_id, 'windows');
  assert.equal(calls[0].item_kind, 'category');
  assert.equal(calls[0].sort_order, 60);
  assert.equal(calls[0].parent_item_id, '');
  assert.equal(calls[0].item_id, 'uuid-test');
  assert.equal(calls[0].launch_actions.length, 0);
});

test('unknown or unsuitable Launch context does not create a row', () => {
  const {sandbox,calls} = createContext({dataPath:'$.other'});
  assert.equal(sandbox.applyLaunchNewCategoryFromQuery(new URLSearchParams('launchNewCategory=1&newCategoryPage=work')), false);
  assert.equal(calls.some(x=>!Array.isArray(x)), false);
});

test('ordinary startup does not invoke new-category', () => {
  const {sandbox,calls} = createContext();
  assert.equal(sandbox.applyLaunchNewCategoryFromQuery(new URLSearchParams('startupJson=1')), false);
  assert.equal(calls.length, 0);
});

test('startupJson reload applies existing focus and the new-category route', () => {
  assert.match(code, /if \(!applyLaunchNewCategoryFromQuery\(params\) && !applyLaunchPageFromQuery\(params\)\)/);
  assert.match(code, /applyLaunchFocusFromQuery\(params\)/);
  assert.match(code, /await loadFromObjects\(resolved\.defObj, dataObj, '起動指定JSONを読み込みました'/);
});
