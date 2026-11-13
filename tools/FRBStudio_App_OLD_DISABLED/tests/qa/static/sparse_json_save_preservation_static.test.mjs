import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';

const dataUtilsPath = new URL('../../../wwwroot/js/core/data_utils.js', import.meta.url);
const detailSavePath = new URL('../../../wwwroot/js/runtime/detail_save.js', import.meta.url);
const gridDetailPath = new URL('../../../wwwroot/js/renderers/grid_detail.js', import.meta.url);

function loadDataUtils() {
  const source = fs.readFileSync(dataUtilsPath, 'utf8');
  const context = vm.createContext({ structuredClone: globalThis.structuredClone });
  vm.runInContext(source, context);
  return context;
}

test('sparse JSON helper preserves absent + blank fields', () => {
  const ctx = loadDataUtils();
  const data = { status: 'draft' };
  assert.equal(ctx.hasOwnByPath(data, '$.analysis_start_date'), false);
  assert.equal(ctx.shouldSkipAbsentBlankWrite(data, '$.analysis_start_date', ''), true);
  assert.equal(ctx.shouldSkipAbsentBlankWrite(data, '$.analysis_start_date', '2026-08-28'), false);
});

test('existing explicit empty field remains writable/present', () => {
  const ctx = loadDataUtils();
  const data = { analysis_start_date: '' };
  assert.equal(ctx.hasOwnByPath(data, '$.analysis_start_date'), true);
  assert.equal(ctx.shouldSkipAbsentBlankWrite(data, '$.analysis_start_date', ''), false);
});

test('header/detail save paths use sparse-preservation guard', () => {
  const detailSave = fs.readFileSync(detailSavePath, 'utf8');
  const gridDetail = fs.readFileSync(gridDetailPath, 'utf8');
  assert.match(detailSave, /shouldSkipAbsentBlankWrite\(sourceData, fullPath, rawValue\)/);
  assert.match(gridDetail, /detailMode !== 'new'.*shouldSkipAbsentBlankWrite\(row, field\.field, rawValue\)/s);
});
