import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import test from 'node:test';

const root = process.cwd();
const readText = relativePath => fs.readFileSync(path.join(root, relativePath), 'utf8');

test('editable SubGrid action column shrinks to its content width while keeping table-cell semantics', () => {
  const css = readText('wwwroot/styles.css');

  assert.match(css, /\.detail-subgrid-action-th,\s*\.detail-subgrid-row-actions\s*\{[\s\S]*?width:\s*1%;[\s\S]*?min-width:\s*0;[\s\S]*?max-width:\s*none;[\s\S]*?white-space:\s*nowrap;/);
  assert.match(css, /\.detail-subgrid-row-actions\s*\{[\s\S]*?display:\s*table-cell;[\s\S]*?padding:\s*2px 6px 2px 3px;/);
  const start = css.indexOf('v0.18.92.1-subgrid-action-divider-left-correction');
  const end = css.indexOf('.detail-subgrid-cell-input', start);
  const fixBlock = css.slice(start, end);
  assert.doesNotMatch(fixBlock, /display:\s*flex;/);
  assert.doesNotMatch(fixBlock, /detail-subgrid-cell-input[\s\S]*?width:/);
});

test('SubGrid row number and buttons keep compact spacing without clipping delete label', () => {
  const css = readText('wwwroot/styles.css');

  assert.match(css, /\.detail-subgrid-row-actions > \* \+ \*\s*\{\s*margin-left:\s*3px;/);
  assert.match(css, /\.detail-subgrid-row-actions > \.detail-subgrid-row-no,[\s\S]*?vertical-align:\s*middle;/);
  assert.match(css, /\.detail-subgrid-row-no\s*\{[\s\S]*?display:\s*inline-block;[\s\S]*?min-width:\s*14px;/);
});

test('index cache-busts the shared stylesheet for the SubGrid layout fix', () => {
  const index = readText('wwwroot/index.html');
  assert.match(index, /styles\.css\?v=related-grid-modal-layer-018102/);
});
