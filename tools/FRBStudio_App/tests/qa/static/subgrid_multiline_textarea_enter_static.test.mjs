import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import test from 'node:test';

const root = process.cwd();
const readText = relativePath => fs.readFileSync(path.join(root, relativePath), 'utf8');

const runtime = readText('wwwroot/js/runtime/detail_subgrid_edit.js');
const styles = readText('wwwroot/styles.css');
const index = readText('wwwroot/index.html');

test('SubGrid Preview Edit uses a real textarea for long/multiline editor fields', () => {
  assert.match(runtime, /function createSubGridCellControl\(\{ value, column, editable, field, multilineEditor=false \}\)/);
  assert.match(runtime, /else if \(multilineEditor\) \{[\s\S]{0,700}document\.createElement\('textarea'\)[\s\S]{0,700}input\.dataset\.multilineEditor = 'true'/);
  assert.match(runtime, /createSubGridCellControl\(\{[\s\S]{0,260}multilineEditor: true[\s\S]{0,80}\}\)/);
});

test('multiline textarea keeps Enter and Shift+Enter as newline while Ctrl/Cmd+Enter remains apply', () => {
  const previewStart = runtime.indexOf('function createDetailSubGridPreviewEditValue');
  const previewEnd = runtime.indexOf('function showDetailSubGridCardEditor', previewStart);
  const previewBlock = runtime.slice(previewStart, previewEnd);

  assert.match(previewBlock, /if \(e\.key === 'F12' \|\| \(\(e\.ctrlKey \|\| e\.metaKey\) && e\.key === 'Enter'\)\) \{/);
  assert.doesNotMatch(previewBlock, /if \(e\.key === 'Enter'\)\s*\{[\s\S]{0,120}e\.preventDefault\(\)/);
  assert.doesNotMatch(previewBlock, /e\.shiftKey[\s\S]{0,100}e\.key === 'Enter'[\s\S]{0,100}preventDefault/);
});

test('SubGrid list view stays visually single-line but preserves canonical multiline raw value', () => {
  const controlStart = runtime.indexOf('function createSubGridCellControl');
  const controlEnd = runtime.indexOf('function createSubGridActionButton', controlStart);
  const controlBlock = runtime.slice(controlStart, controlEnd);
  const readStart = runtime.indexOf('function readSubGridControlValue');
  const readEnd = runtime.indexOf('function collectDetailSubGridValue', readStart);
  const readBlock = runtime.slice(readStart, readEnd);

  assert.match(controlBlock, /input = document\.createElement\('input'\);\s*input\.type = 'text';/);
  assert.match(controlBlock, /input\.__studioSubGridRawValue = rawText;/);
  assert.match(controlBlock, /if \(input\.dataset\.singleLineLongValue === 'true'\) \{[\s\S]{0,220}input\.__studioSubGridRawValue = input\.value \?\? '';/);
  assert.match(readBlock, /input\.dataset\.singleLineLongValue === 'true'[\s\S]{0,220}input\.__studioSubGridRawValue/);
  assert.match(index, /js\/runtime\/detail_subgrid_edit\.js\?v=subgrid-collapse-018107/);
});

test('Preview Edit textarea inherits preview height and opens at document start', () => {
  const previewStart = runtime.indexOf('function createDetailSubGridPreviewEditValue');
  const previewEnd = runtime.indexOf('function showDetailSubGridCardEditor', previewStart);
  const previewBlock = runtime.slice(previewStart, previewEnd);

  assert.match(previewBlock, /const previewHeight = Math\.max\(72,[\s\S]{0,180}getBoundingClientRect/);
  assert.match(previewBlock, /input\.style\.minHeight = `\$\{previewHeight\}px`;/);
  assert.match(previewBlock, /input\.style\.height = `\$\{previewHeight\}px`;/);
  assert.match(previewBlock, /input\.focus\(\{ preventScroll: true \}\)/);
  assert.match(previewBlock, /input\.setSelectionRange\(0, 0\)/);
  assert.match(previewBlock, /input\.scrollTop = 0;/);
  assert.match(styles, /\.detail-subgrid-card-preview-editor[\s\S]{0,260}height: auto;/);
});
