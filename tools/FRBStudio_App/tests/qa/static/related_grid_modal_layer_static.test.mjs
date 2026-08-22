import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const appRoot = path.resolve(here, '../../..');

function read(relative) {
  return fs.readFileSync(path.join(appRoot, relative), 'utf8');
}

test('Related Grid modal uses the common overlay layer so its close header stays above the sticky shell', () => {
  const styles = read('wwwroot/styles.css');
  const shellCss = read('wwwroot/css/frb-studio-shell.css');

  assert.match(shellCss, /--frb-overlay-modal-z:\s*2147483600\s*;/);
  assert.match(
    styles,
    /\.related-grid-modal-overlay\s*\{[\s\S]*?z-index:\s*var\(--frb-overlay-modal-z,\s*2147483600\)\s*;/
  );
  assert.doesNotMatch(
    styles,
    /\.related-grid-modal-overlay\s*\{[\s\S]*?z-index:\s*12000\s*;/
  );
});

test('index.html refreshes the main stylesheet after the Related Grid modal layer fix', () => {
  const index = read('wwwroot/index.html');
  assert.match(index, /styles\.css\?v=related-grid-modal-layer-018102/);
});
