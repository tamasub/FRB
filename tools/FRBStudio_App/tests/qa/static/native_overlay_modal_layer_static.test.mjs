import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const appRoot = path.resolve(here, '../../..');
const shellCssPath = path.join(appRoot, 'wwwroot/css/frb-studio-shell.css');
const pluginJsPath = path.join(appRoot, 'studio_overlays/gpt_fx_lab/plugins/fx_chart_viewer/plugin.js');
const pluginJsonPath = path.join(appRoot, 'studio_overlays/gpt_fx_lab/plugins/fx_chart_viewer/plugin.json');
const overlayManifestPath = path.join(appRoot, 'studio_overlays/gpt_fx_lab/studio_manifest.json');

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

test('GPT FX Chart backdrop uses common Overlay modal layer instead of legacy 9999', () => {
  const pluginJs = read(pluginJsPath);
  assert.match(pluginJs, /\.gpt-fx-chart-backdrop\s*\{[\s\S]*?z-index:\s*var\(--frb-overlay-modal-z,\s*2147483600\)/);
  assert.doesNotMatch(pluginJs, /\.gpt-fx-chart-backdrop\s*\{[\s\S]*?z-index:\s*9999\s*;/);
});

test('GPT FX plugin metadata is synchronized to v0.9.1.24', () => {
  const pluginJs = read(pluginJsPath);
  const pluginJson = JSON.parse(read(pluginJsonPath));
  const overlayManifest = JSON.parse(read(overlayManifestPath));
  assert.match(pluginJs, /gpt_fx_lab\.fx_chart_viewer v0\.9\.1\.24/);
  assert.equal(pluginJson.version, '0.9.1.24');
  assert.match(String(overlayManifest.notes || ''), /v0\.9\.1\.24/);
});
