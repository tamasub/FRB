import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(here, '../../..');
const read = rel => fs.readFileSync(path.join(root, rel), 'utf8');

test('Diff JSON Viewer saves loaded Diff JSON only by explicit Save As action', () => {
  const viewer = read('wwwroot/DiffJsonViewer.html');
  const bridge = read('wwwroot/js/core/native_host_bridge.js');

  assert.match(viewer, /js\/core\/native_host_bridge\.js/);
  assert.match(viewer, /id="saveAsBtn"[^>]*disabled/);
  assert.match(viewer, />名前を付けて保存<\/button>/);
  assert.match(viewer, /function saveDiffJsonAs\(\)/);
  assert.match(viewer, /fetch\("\/api\/diff\/save-as-dialog"/);
  assert.match(viewer, /JSON\.stringify\(diffJson, null, 2\)/);
  assert.match(viewer, /button\.disabled = !diffJson/);
  assert.match(viewer, /function downloadDiffJson\(/);
  assert.match(viewer, /a\.download = fileName/);

  assert.match(bridge, /path === '\/api\/diff\/save-as-dialog'/);
  assert.match(bridge, /invoke\('dialog\.saveText'/);
  assert.match(bridge, /Diff JSONを名前を付けて保存/);
  assert.match(bridge, /default_extension: 'json'/);
});

test('Diff JSON Viewer suggests a timestamped formal filename for DiffToJson_current.json', () => {
  const viewer = read('wwwroot/DiffJsonViewer.html');

  assert.match(viewer, /sourceName\.toLowerCase\(\) !== "difftojson_current\.json"/);
  assert.match(viewer, /data\?\.generated_at/);
  assert.match(viewer, /DiffToJson_\$\{match\[1\]\}\$\{match\[2\]\}\$\{match\[3\]\}_\$\{match\[4\]\}\$\{match\[5\]\}\$\{match\[6\]\}\.json/);
});


test('Diff JSON Viewerは読込元を表示中ソースとして統一し長い名前は省略・Tooltipで完全値を残す', () => {
  const viewer = read('wwwroot/DiffJsonViewer.html');

  assert.match(viewer, /id="currentSource"/);
  assert.match(viewer, /id="currentSourceText"/);
  assert.match(viewer, /function middleEllipsis\(/);
  assert.match(viewer, /function setCurrentSource\(/);
  assert.match(viewer, /\$\("currentSource"\)\.title = source \|\| fileName/);
  assert.match(viewer, /applyDiffJson\(JSON\.parse\(text\), file\.name, file\.name\)/);
  assert.match(viewer, /applyDiffJson\(JSON\.parse\(text\), fileName, url\)/);
  assert.doesNotMatch(viewer, /ファイルが選択されていません/);
});

test('Diff JSON ViewerのSave As結果はツールバー幅を消費せず表示中ソースを変更しない', () => {
  const viewer = read('wwwroot/DiffJsonViewer.html');

  assert.match(viewer, /id="saveAsStatus" class="visually-hidden"/);
  assert.match(viewer, /function setSaveAsStatus\(/);
  assert.match(viewer, /setSaveAsStatus\(`保存しました:/);
  assert.doesNotMatch(viewer, /setCurrentSource\([^)]*result\?\.path/);
});

test('Git warningsは固定高の枠内で全件スクロール表示する', () => {
  const viewer = read('wwwroot/DiffJsonViewer.html');

  assert.match(viewer, /\.git-warnings\{height:164px;overflow:hidden;display:flex;flex-direction:column\}/);
  assert.match(viewer, /\.git-warnings-scroll\{[^}]*overflow:auto;[^}]*overflow-wrap:anywhere;[^}]*word-break:break-word/);
  assert.match(viewer, /uniqueWarnings\.map\(w => `<div class="git-warning-item">/);
  assert.doesNotMatch(viewer, /uniqueWarnings\.slice\(0,3\)/);
});

test('Difference details右端の中途半端な件数表示は廃止する', () => {
  const viewer = read('wwwroot/DiffJsonViewer.html');

  assert.doesNotMatch(viewer, /id="detailStatus"/);
  assert.doesNotMatch(viewer, /\$\("detailStatus"\)/);
});


test('Difference details検索操作はスクロール本文の外へ固定し常時操作可能にする', () => {
  const viewer = read('wwwroot/DiffJsonViewer.html');

  assert.match(viewer, /<main class="panel">[\s\S]*<h2><span>Difference details<\/span><\/h2>[\s\S]*<div class="main-controls"[^>]*>[\s\S]*<div class="body">/);
  assert.match(viewer, /main\.panel > \.main-controls\{[\s\S]*flex:0 0 auto;[\s\S]*border-bottom:1px solid var\(--border\);[\s\S]*background:#fff/);
  assert.match(viewer, /id="diffSearch"[\s\S]*id="viewMode"[\s\S]*id="lineTypeFilter"[\s\S]*id="clearSearchBtn"/);
});
