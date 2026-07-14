const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const assert = require('node:assert/strict');

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
const sourceText = fs.readFileSync(pluginPath, 'utf8');
const manifest = JSON.parse(fs.readFileSync(manifestPath, 'utf8'));

assert.equal(manifest.version, '0.9.1.07');
assert.equal(manifest.signal_policy?.hsi_line_color_rotation?.enabled, true);
assert.equal(manifest.signal_policy?.hsi_line_color_rotation?.palette_size, 8);
assert.equal(manifest.signal_policy?.hsi_line_color_rotation?.same_anchor_same_color, true);
assert.equal(manifest.signal_policy?.hsi_line_color_rotation?.adjacent_anchor_different_color, true);
assert.equal(manifest.signal_policy?.hsi_line_color_rotation?.anchor_marker_stroke_inherits_line_color, true);
assert.match(sourceText, /const HSI_LINE_COLOR_PALETTE = \[/);
assert.match(sourceText, /assignHsiAnnotationColorSlots\(\[\.\.\.\(state\.hsiAnnotations \|\| \[\]\), \.\.\.\(state\.simulationHsiAnnotations \|\| \[\]\)\]\)/);
assert.match(sourceText, /ctx\.strokeStyle = observation \? palette\.observationLine : palette\.line/);
assert.match(sourceText, /ctx\.fillStyle = palette\.anchorFill/);
assert.match(sourceText, /ctx\.strokeStyle = palette\.savedLine/);
assert.match(sourceText, /ctx\.strokeStyle = palette\.line/);

const hook = `
  window.__fxHsiColorRotationTest = {
    HSI_LINE_COLOR_PALETTE,
    assignHsiAnnotationColorSlots,
    assignHsiRenderPaletteSlots,
    hsiPaletteForSlot,
    hsiRenderItemIdentity
  };
`;
const closeIndex = sourceText.lastIndexOf('})();');
assert.ok(closeIndex > 0, 'Plugin IIFE終端を検出できません。');
const instrumented = sourceText.slice(0, closeIndex) + hook + sourceText.slice(closeIndex);
const context = {
  window: {},
  console,
  setTimeout,
  clearTimeout,
  URL,
  structuredClone,
  Intl,
  Date,
  Math,
  JSON,
  Map,
  Set,
  Promise,
  requestAnimationFrame: callback => setTimeout(callback, 0)
};
vm.runInNewContext(instrumented, context, { filename: pluginPath });
const api = context.window.__fxHsiColorRotationTest;
assert.ok(api, 'HSI色ローテーションのテスト用API公開に失敗しました。');
assert.equal(api.HSI_LINE_COLOR_PALETTE.length, 8, 'HSI色パレットは8色必要です。');
assert.equal(new Set(Array.from(api.HSI_LINE_COLOR_PALETTE, item => item.id)).size, 8, 'HSI色パレットIDが重複しています。');

const annotations = [
  { id: 'ann-c', anchor_id: 'anchor-c', recognized_time: '2025-10-30 13:34', display: {} },
  { id: 'ann-a2', anchor_id: 'anchor-a', recognized_time: '2025-10-30 12:00', display: {} },
  { id: 'ann-b', anchor_id: 'anchor-b', recognized_time: '2025-10-30 09:44', display: {} },
  { id: 'ann-a1', anchor_id: 'anchor-a', recognized_time: '2025-10-29 21:04', display: {} }
];
api.assignHsiAnnotationColorSlots(annotations);
const slotA = annotations.find(item => item.id === 'ann-a1').hsi_color_slot;
assert.equal(annotations.find(item => item.id === 'ann-a2').hsi_color_slot, slotA, '同一起点が別色になっています。');
const slotB = annotations.find(item => item.id === 'ann-b').hsi_color_slot;
const slotC = annotations.find(item => item.id === 'ann-c').hsi_color_slot;
assert.notEqual(slotA, slotB, '隣接する別起点が同色です。');
assert.notEqual(slotB, slotC, '隣接する別起点が同色です。');
annotations.forEach(item => {
  assert.equal(item.display.hsi_color_slot, item.hsi_color_slot, '表示用色スロットが同期されていません。');
});

const renderItems = [
  { idx: 30, annotation: annotations.find(item => item.id === 'ann-c') },
  { idx: 10, annotation: annotations.find(item => item.id === 'ann-a1') },
  { idx: 20, annotation: annotations.find(item => item.id === 'ann-b') },
  { idx: 25, annotation: annotations.find(item => item.id === 'ann-a2') }
];
api.assignHsiRenderPaletteSlots(renderItems);
const renderA = renderItems.filter(item => item.annotation.anchor_id === 'anchor-a');
assert.equal(renderA[0].hsiPaletteSlot, renderA[1].hsiPaletteSlot, '同一起点の描画色が一致していません。');
assert.equal(renderA[0].hsiPalette.id, renderA[1].hsiPalette.id, '同一起点の描画パレットが一致していません。');
const orderedUnique = renderItems
  .slice()
  .sort((a, b) => a.idx - b.idx)
  .filter((item, index, array) => index === array.findIndex(other => other.annotation.anchor_id === item.annotation.anchor_id));
for (let i = 1; i < orderedUnique.length; i += 1) {
  assert.notEqual(orderedUnique[i - 1].hsiPaletteSlot, orderedUnique[i].hsiPaletteSlot,
    '時系列で隣接する別HSI起点が同色になっています。');
}

// 8色を超えた場合も直前起点と同色にはならず、9番目から安全にローテーションする。
const many = Array.from({ length: 10 }, (_, index) => ({
  id: `ann-${index}`,
  anchor_id: `anchor-${index}`,
  recognized_time: `2025-10-${String(20 + index).padStart(2, '0')} 09:00`,
  display: {}
}));
api.assignHsiAnnotationColorSlots(many);
assert.deepEqual(Array.from(many, item => item.hsi_color_slot), [0,1,2,3,4,5,6,7,0,1]);
for (let i = 1; i < many.length; i += 1) {
  assert.notEqual(many[i - 1].hsi_color_slot, many[i].hsi_color_slot);
}

console.log('PASS hsi_line_color_rotation_v0_1');
console.log(`palette=${api.HSI_LINE_COLOR_PALETTE.map(item => item.id).join(',')}`);
console.log(`slots=${many.map(item => item.hsi_color_slot).join(',')}`);
