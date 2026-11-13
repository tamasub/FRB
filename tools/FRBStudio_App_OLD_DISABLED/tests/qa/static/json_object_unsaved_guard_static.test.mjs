import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';

const root = path.resolve(import.meta.dirname, '../../..');
const read = rel => fs.readFileSync(path.join(root, rel), 'utf8');

test('Core state explicitly loads JSON unsaved guard runtime with cache-busting version', () => {
  const state = read('wwwroot/js/core/state.js');
  assert.match(state, /ensureJsonObjectUnsavedGuardRuntime/);
  assert.match(state, /json_unsaved_guard\.js\?v=json-unsaved-guard-018127-fix/);
  assert.match(state, /window\.__frbJsonUnsavedGuardInstalled = true/);
});

test('JSON unsaved guard boots after all scripts are defined', () => {
  const js = read('wwwroot/js/runtime/json_unsaved_guard.js');
  assert.match(js, /DOMContentLoaded', bootstrap/);
  assert.match(js, /__frbJsonObjectUnsavedGuardRuntimeLoaded/);
  assert.match(js, /__frbJsonObjectUnsavedGuardActive/);
});

test('JSON unsaved guard visualizes unsaved state on Save button', () => {
  const js = read('wwwroot/js/runtime/json_unsaved_guard.js');
  assert.match(js, /#saveBtn\.is-unsaved/);
  assert.match(js, /`● \$\{label\}`/);
  assert.match(js, /未保存の変更があります。保存してください。/);
});

test('JSON unsaved guard protects navigation like Markdown Studio', () => {
  const js = read('wwwroot/js/runtime/json_unsaved_guard.js');
  assert.match(js, /現在のJSONに未保存の変更があります。保存せずに別の画面へ移動しますか？/);
  assert.match(js, /okText: '移動する'/);
  assert.match(js, /#loadBtn, #maintainViewDefBtn, \[data-frb-home\], \[data-frb-reset\]/);
  assert.match(js, /target\.closest\('a\[href\]'\)/);
  assert.match(js, /window\.addEventListener\('beforeunload'/);
  assert.match(js, /event\.returnValue = ''/);
});

test('JSON unsaved guard has load/save fallback paths', () => {
  const js = read('wwwroot/js/runtime/json_unsaved_guard.js');
  assert.match(js, /wrapGlobalFunction\('loadFromObjects'/);
  assert.match(js, /wrapGlobalFunction\('saveOverwriteJson'/);
  assert.match(js, /watchSaveButtonFallback/);
  assert.match(js, /installSourceReplacementFallback/);
  assert.match(js, /nowRef !== lastSourceDataRef/);
});

test('Search inputs are not marked dirty; only Header and Detail edit areas are observed', () => {
  const js = read('wwwroot/js/runtime/json_unsaved_guard.js');
  assert.match(js, /#headerForm, #headerSection/);
  assert.match(js, /#detailDialog/);
  assert.doesNotMatch(js, /#searchForm/);
});
