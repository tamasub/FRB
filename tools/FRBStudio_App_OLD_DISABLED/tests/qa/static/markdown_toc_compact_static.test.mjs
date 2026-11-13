import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(here, '../../..');
const md = fs.readFileSync(path.join(root, 'wwwroot/mdViewer.html'), 'utf8');

test('Markdown INDEX keeps sparse H2 headings packed at the top of its scrollable panel', () => {
  const tocCss = md.match(/\.toc\s*\{([^}]*)\}/)?.[1];
  assert.ok(tocCss, 'INDEX navigation has a CSS rule');
  assert.match(tocCss, /display:\s*grid\s*;/);
  assert.match(tocCss, /align-content:\s*start\s*;/, 'grid rows must not stretch over the whole sidebar');
  assert.match(tocCss, /grid-auto-rows:\s*max-content\s*;/, 'each row should use the title height');
  assert.match(tocCss, /overflow:\s*auto\s*;/, 'long outlines retain scrolling');
  assert.match(md, /<nav id="toc" class="toc"><\/nav>/);
  assert.match(md, /function buildToc\(\)[\s\S]*?tocEl\.appendChild\(a\)/);
});
