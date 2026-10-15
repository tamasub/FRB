import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import test from 'node:test';

const root = process.cwd();
const text = relativePath => fs.readFileSync(path.join(root, relativePath), 'utf8');

test('basic-info card hides when no visible Header target field exists', () => {
  const source = text('wwwroot/js/renderers/field_controls.js');
  assert.match(source, /function renderHeader\(\)[\s\S]*const hasHeaderContent = form\.childElementCount > 0 \|\| Boolean\(section\.querySelector\('#mainContextHeaderPanel'\)\)/);
  assert.match(source, /section\.classList\.toggle\('hidden', !hasHeaderContent\)/);
});

test('Core full-text search stays visible with zero ViewDef or plugin search targets', () => {
  const source = text('wwwroot/js/renderers/field_controls.js');
  assert.match(source, /function renderSearch\(\)[\s\S]*searchSection\.classList\.remove\('hidden'\)/);
  assert.match(source, /form\.classList\.toggle\('hidden', form\.childElementCount === 0\)/);
  assert.doesNotMatch(source, /searchSection\.classList\.toggle\('hidden', !hasSearchTargets\)/);
});

test('field control cache key is advanced for empty primary section visibility change', () => {
  const index = text('wwwroot/index.html');
  assert.match(index, /js\/renderers\/field_controls\.js\?v=empty-primary-section-hide-01878/);
});
