const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');

const root = path.resolve(process.argv[2] || process.cwd());
function artifactPath(...parts) {
  const normalized = path.join(root, ...parts);
  if (fs.existsSync(normalized)) return normalized;
  const windowsEntry = path.join(root, parts.join('\\'));
  if (fs.existsSync(windowsEntry)) return windowsEntry;
  throw new Error(`テスト対象ファイルが見つかりません: ${parts.join('/')}`);
}

const pluginPath = artifactPath('studio_overlays', 'gpt_fx_lab', 'plugins', 'fx_chart_viewer', 'plugin.js');
const manifestPath = artifactPath('studio_overlays', 'gpt_fx_lab', 'plugins', 'fx_chart_viewer', 'plugin.json');
const source = fs.readFileSync(pluginPath, 'utf8');
const manifest = JSON.parse(fs.readFileSync(manifestPath, 'utf8'));

assert.equal(manifest.version, '0.9.1.23');
assert.equal(manifest.signal_policy.panel_local_crosshair_support, true);
assert.equal(manifest.signal_policy.crosshair_click_lock_support, true);
assert.equal(manifest.signal_policy.crosshair_cross_panel_sync, true);
assert.equal(manifest.signal_policy.crosshair_horizontal_price_sync, true);
assert.equal(manifest.signal_policy.crosshair_vertical_time_sync, true);
assert.equal(manifest.signal_policy.crosshair_used_for_entry_decision, false);
assert.match(source, /function drawCrosshairForPanel\(/);
assert.match(source, /function setCrosshairFromPanelPoint\(/);
assert.match(source, /crosshair\.locked === true/);
assert.match(source, /const timeText = locked \? `固定 \$\{timeTextBase\}` : timeTextBase;/);
assert.match(source, /const priceText = Number\(price\)\.toFixed\(3\);/);
assert.match(source, /drawCrosshairForPanel\(ctx, \{ state, panelKind: rect\.kind/);
assert.match(source, /const isSourcePanel = crosshair\.panelKind === panelKind;/);
assert.match(source, /function crosshairCanRender\(/);
assert.doesNotMatch(source, /crosshair\.panelKind === panelKind\s*&&/);
assert.match(source, /cursor: crosshair;/);
console.log('PASS crosshair_lock_v0_1');
