import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const appRoot = path.resolve(here, '../../..');
const shellCssPath = path.join(appRoot, 'wwwroot/css/frb-studio-shell.css');

function read(file) {
  return fs.readFileSync(file, 'utf8');
}

test('Overlay modal layer is above every numeric FRB Studio app z-index and below CSS max', () => {
  const shellCss = read(shellCssPath);
  const match = shellCss.match(/--frb-overlay-modal-z:\s*(\d+)\s*;/);
  assert.ok(match, 'common shell must expose --frb-overlay-modal-z');
  const overlayZ = Number(match[1]);
  assert.equal(overlayZ, 2147483600);

  const wwwroot = path.join(appRoot, 'wwwroot');
  let maxNumericZ = -Infinity;
  const stack = [wwwroot];
  while (stack.length) {
    const dir = stack.pop();
    for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
      const full = path.join(dir, entry.name);
      if (entry.isDirectory()) {
        stack.push(full);
        continue;
      }
      if (!/\.(css|js|html)$/i.test(entry.name)) continue;
      const text = read(full);
      for (const m of text.matchAll(/z-index\s*:\s*(\d+)/g)) {
        const value = Number(m[1]);
        if (value !== overlayZ) maxNumericZ = Math.max(maxNumericZ, value);
      }
    }
  }

  assert.ok(Number.isFinite(maxNumericZ));
  assert.ok(overlayZ > maxNumericZ, `overlay ${overlayZ} must be above app max ${maxNumericZ}`);
  assert.ok(overlayZ < 2147483647, 'overlay z-index must remain below CSS signed-int max');
});



test('Core package keeps external default / gpt_fx_lab overlay payloads outside FRBStudio_App ZIP', () => {
  const packScript = read(path.join(appRoot, 'tools/zip/make_FRBStudio_App_zip_v2.ps1'));
  assert.match(packScript, /studio_overlays\\default/);
  assert.match(packScript, /studio_overlays\\gpt_fx_lab/);
});
