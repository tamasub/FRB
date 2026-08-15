import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';

const ROOT = process.cwd();
const read = rel => fs.readFileSync(path.join(ROOT, rel), 'utf8');

const shellCss = read('wwwroot/css/frb-studio-shell.css');
const shellJs = read('wwwroot/js/ui/frb_studio_shell.js');
const indexHtml = read('wwwroot/index.html');
const mdHtml = read('wwwroot/mdViewer.html');
const diffHtml = read('wwwroot/DiffJsonViewer.html');
const metaHtml = read('wwwroot/MetaDiff_HypothesisViewer.html');
const homeHtml = read('wwwroot/home.html');
const nativeDispatcher = read('NativeShell/NativeCommandDispatcher.cs');
const nativeConfig = read('NativeShell/native_shell.config.json');
const loadRuntime = read('wwwroot/js/runtime/load_runtime.js');
const fileApi = read('wwwroot/js/core/file_api.js');

test('Common Shell is shared by the four Studio/Viewer pages without iframe composition', () => {
  for (const html of [indexHtml, mdHtml, diffHtml, metaHtml]) {
    assert.match(html, /css\/frb-studio-shell\.css/);
    assert.match(html, /js\/ui\/frb_studio_shell\.js/);
    assert.match(html, /FrbStudioShell\.mount\(/);
    assert.doesNotMatch(html, /<iframe\b/i);
  }
});

test('Common Shell keeps the stable module URLs and unified display names', () => {
  assert.match(shellJs, /JSON Object Studio/);
  assert.match(shellJs, /Markdown Studio/);
  assert.match(shellJs, /Diff JSON Viewer/);
  assert.match(shellJs, /MetaDiff Viewer/);
  assert.match(shellJs, /href: 'index\.html'/);
  assert.match(shellJs, /href: 'mdViewer\.html'/);
  assert.match(shellJs, /href: 'DiffJsonViewer\.html'/);
  assert.match(shellJs, /href: 'MetaDiff_HypothesisViewer\.html'/);
});

test('Home is a real page with direct entry points to all four modules', () => {
  for (const href of ['index.html', 'mdViewer.html', 'DiffJsonViewer.html', 'MetaDiff_HypothesisViewer.html']) {
    assert.ok(homeHtml.includes(`href="${href}"`), `${href} should be linked from home`);
  }
  assert.match(homeHtml, /FRB Studio Home/);
});

test('Home navigation and current-page reset are separate Common Shell actions', () => {
  assert.match(shellJs, /data-frb-home/);
  assert.match(shellJs, /data-frb-reset/);
  assert.match(shellJs, /location\.assign\('home\.html'\)/);
  assert.match(shellJs, /frb-studio:reset-request/);
});

test('JSON Object Studio uses the agreed left-thin + right-wide two-column workspace', () => {
  assert.match(indexHtml, /class="json-studio-workspace"/);
  assert.match(indexHtml, /class="json-studio-source-pane"/);
  assert.match(indexHtml, /class="json-studio-main-pane"/);
  assert.match(shellCss, /grid-template-columns:minmax\(220px, 250px\) minmax\(0, 1fr\)/);
});

test('Markdown Studio keeps its responsibility-driven three-column layout', () => {
  assert.match(mdHtml, /class="workspace-sidebar"/);
  assert.match(mdHtml, /class="article-card/);
  assert.match(mdHtml, /class="sidebar"/);
  assert.match(shellCss, /grid-template-columns:minmax\(235px, 270px\) minmax\(0,1fr\) minmax\(265px,300px\)/);
});

test('Diff JSON and MetaDiff retain two-column responsibility while joining the Common Shell', () => {
  assert.match(diffHtml, /pageId: 'diff-json'/);
  assert.match(metaHtml, /pageId: 'meta-diff'/);
  assert.match(diffHtml, /class="legacy-page-header"/);
  assert.match(metaHtml, /class="legacy-page-header"/);
  assert.match(shellCss, /\.frb-page-diff-json \.layout \{ grid-template-columns:/);
  assert.match(shellCss, /\.frb-page-meta-diff \.layout \{ grid-template-columns:/);
});

test('Visual Foundation uses shared tokens and pale-green supplemental panes', () => {
  assert.match(shellCss, /--frb-shell-navy:/);
  assert.match(shellCss, /--frb-green-surface:/);
  assert.match(shellCss, /--frb-green-line:/);
  assert.match(shellCss, /workspace-sidebar \.side-card/);
  assert.match(shellCss, /sidebar \.side-card/);
});

test('Related/SubGrid compact launch mode is not forced into the full Common Shell layout', () => {
  assert.match(shellCss, /body\.studio-grid-only-shell \.frb-app-shell/);
  assert.match(shellCss, /body\.studio-grid-only-shell \.json-studio-source-pane/);
});


test('Common Shell uses colored module icon tiles instead of monochrome placeholder badges', () => {
  assert.match(shellJs, /iconClass: 'json'/);
  assert.match(shellJs, /iconClass: 'markdown'/);
  assert.match(shellJs, /iconClass: 'diff'/);
  assert.match(shellJs, /iconClass: 'meta'/);
  assert.match(shellCss, /\.frb-icon-json \{ background:linear-gradient/);
  assert.match(shellCss, /\.frb-icon-markdown \{ background:linear-gradient/);
  assert.match(shellCss, /\.frb-icon-diff \{ background:linear-gradient/);
  assert.match(shellCss, /\.frb-icon-meta \{ background:linear-gradient/);
});

test('Markdown Studio keeps Viewer and Editor but removes the Qiita Zenn theme selector from the toolbar', () => {
  assert.match(mdHtml, /id="btnViewerMode"/);
  assert.match(mdHtml, /id="btnEditorMode"/);
  assert.doesNotMatch(mdHtml, /id="themeSelect"/);
  assert.doesNotMatch(mdHtml, /<option value="zenn">/);
  assert.doesNotMatch(mdHtml, /themeSelect\.addEventListener/);
});

test('JSON Object Studio main pane is forced to consume the available right-column width', () => {
  assert.match(shellCss, /\.frb-page-json-object \.json-studio-workspace \{[\s\S]*width:100%;[\s\S]*max-width:none;/);
  assert.match(shellCss, /\.frb-page-json-object \.json-studio-main-pane \{[\s\S]*justify-self:stretch;/);
  assert.match(shellCss, /\.frb-page-json-object \.json-studio-main-pane > main \{[\s\S]*width:100%;[\s\S]*max-width:none;/);
  assert.match(shellCss, /#gridSection \{[\s\S]*width:100%;[\s\S]*max-width:none;/);
});

test('JSON Object Studio left source pane is a fixed full-height rail below the common fixed headers', () => {
  assert.match(shellCss, /\.frb-page-json-object \.json-studio-workspace \{[\s\S]*width:100%;[\s\S]*margin:0;[\s\S]*align-items:stretch;/);
  assert.match(shellCss, /\.frb-page-json-object \.json-studio-source-pane \{[\s\S]*position:sticky;[\s\S]*top:var\(--frb-fixed-header-height,[\s\S]*height:calc\(100dvh - var\(--frb-fixed-header-height,/);
  assert.match(shellCss, /\.frb-page-json-object \.app-header \{[\s\S]*min-height:100%;/);
});

test('Common page title bar remains fixed below the module navigation on every screen', () => {
  assert.match(shellCss, /\.frb-pagebar \{[\s\S]*position: sticky;[\s\S]*top: var\(--frb-shell-height,/);
  assert.match(shellJs, /function syncStickyOffsets\(shell, pagebar\)/);
  assert.match(shellJs, /--frb-fixed-header-height/);
  assert.match(shellJs, /syncStickyOffsets\(shell, pagebar\)/);
});

test('JSON Object Studio treats DATA JSON as the primary source and places it before ViewDef', () => {
  const dataInput = indexHtml.indexOf('id="dataNameInput"');
  const defInput = indexHtml.indexOf('id="defNameInput"');
  const dataDrop = indexHtml.indexOf('data-input="dataFile"');
  const defDrop = indexHtml.indexOf('data-input="defFile"');
  assert.ok(dataInput >= 0 && defInput >= 0 && dataInput < defInput);
  assert.ok(dataDrop >= 0 && defDrop >= 0 && dataDrop < defDrop);
  assert.match(indexHtml, /<span class="drop-label">DATA JSON<\/span>/);
  assert.doesNotMatch(indexHtml, />対象JSON</);
  assert.doesNotMatch(indexHtml, />対象Drop</);
});

test('JSON file tree picker can escape the fixed left rail without being clipped', () => {
  assert.match(shellCss, /\.frb-page-json-object \.json-studio-source-pane \{[\s\S]*overflow:visible;/);
  assert.match(shellCss, /\.frb-page-json-object \.json-studio-source-pane \.file-tree-picker \{[\s\S]*z-index:/);
});

test('Markdown workspace drag indicators are cleared after internal move completion', () => {
  assert.match(mdHtml, /function clearMarkdownDragIndicators\(\)/);
  assert.match(mdHtml, /document\.body\.classList\.remove\('drag-over'\)/);
  assert.match(mdHtml, /finally \{\s*clearMarkdownDragIndicators\(\);\s*\}/);
});

test('Diff viewers use Markdown-like rounded soft buttons while only Diff JSON gets pale-green left panel', () => {
  for (const html of [diffHtml, metaHtml]) {
    assert.match(html, /input\[type="file"\]::file-selector-button/);
    assert.match(html, /border-radius:14px/);
    assert.match(html, /background:rgba\(105,120,160,\.12\)/);
  }
  assert.match(diffHtml, /\.layout > aside\.panel\{[\s\S]*#f4faef/);
  assert.doesNotMatch(metaHtml, /\.layout > aside\.panel\{/);
});

test('Markdown front-matter missing notice is muted gray with a pale-pink generation action', () => {
  assert.match(mdHtml, /\.fm-suggest-card \{[\s\S]*rgba\(100,116,139,0\.075\)/);
  assert.match(mdHtml, /\.fm-suggest-action \{[\s\S]*background:#fbe7ec;[\s\S]*color:#9f5367;/);
  assert.match(mdHtml, /class="fm-suggest-action"[^>]*>設定ヘッダーを自動生成<\/button>/);
  assert.doesNotMatch(mdHtml, /background:linear-gradient\(135deg, #f59e0b, #d97706\)/);
});


test('Markdown toolbar moves open actions into Workspace and reserves a wide central drop area', () => {
  const workspaceIndex = mdHtml.indexOf('class="md-workspace-actions md-workspace-open-actions"');
  const folderButtonIndex = mdHtml.indexOf('id="localFileBtn"');
  const externalButtonIndex = mdHtml.indexOf('id="btnExternalOpen"');
  assert.ok(workspaceIndex >= 0 && folderButtonIndex > workspaceIndex && externalButtonIndex > workspaceIndex);
  assert.match(mdHtml, /class="md-drop-hint md-drop-wide"[^>]*>MarkdownをここへDrop<\/span>/);
  assert.match(mdHtml, /\.md-drop-hint\.md-drop-wide \{[\s\S]*flex: 1 1 360px;/);
});

test('Markdown workspace restores the last explicitly selected folder through a persisted Native folder grant', () => {
  assert.match(mdHtml, /MARKDOWN_WORKSPACE_PERSIST_KEY = 'markdown\.workspace'/);
  assert.match(mdHtml, /folderGrant\.select[\s\S]*persist_key: MARKDOWN_WORKSPACE_PERSIST_KEY/);
  assert.match(mdHtml, /folderGrant\.restore[\s\S]*persist_key: MARKDOWN_WORKSPACE_PERSIST_KEY/);
  assert.match(mdHtml, /await restoreLastMarkdownWorkspaceFolder\(\)/);
  assert.match(nativeConfig, /"folderGrant\.restore"/);
  assert.match(nativeDispatcher, /case "folderGrant\.restore"/);
  assert.match(nativeDispatcher, /LocalApplicationData/);
  assert.match(nativeDispatcher, /NormalizePersistKey/);
});

test('JSON loaded documents always resynchronize the primary save button after render and readonly checks', () => {
  assert.match(loadRuntime, /function syncLoadedDocumentSaveButtonState\(\)/);
  assert.match(loadRuntime, /saveBtn\.disabled = readonly/);
  assert.match(loadRuntime, /currentDataApiUrl \? '上書き保存' : '別名保存'/);
  assert.match(loadRuntime, /updateReadonlyLaunchControls\(\);\s*syncLoadedDocumentSaveButtonState\(\);/);
});

test('JSON title toolbar is compact and document path metadata moves to the fixed left rail', () => {
  assert.match(indexHtml, /class="json-document-meta"/);
  assert.match(indexHtml, /id="jsonMetaFileName"/);
  assert.match(indexHtml, /id="jsonMetaCharCount"/);
  assert.doesNotMatch(indexHtml, /class="status current-data-path"/);
  assert.match(indexHtml, />MD 出力→Viewer<\/button>/);
  assert.match(indexHtml, />ViewDef 出力→Viewer<\/button>/);
  assert.match(shellCss, /\.frb-page-json-object \.json-document-meta \{[\s\S]*margin-top: auto;/);
  assert.match(fileApi, /metaFileEl\.title = path/);
  assert.match(fileApi, /JSON\.stringify\(sourceData, null, 2\)\.length/);
});

test('Markdown document metadata keeps filename and character count only, with filename tooltip sync', () => {
  assert.match(mdHtml, /id="metaFileName"[^>]*title=""/);
  assert.match(mdHtml, /id="charCount"/);
  assert.doesNotMatch(mdHtml, /<b>読了目安<\/b>/);
  assert.doesNotMatch(mdHtml, /<b>Block Model<\/b>/);
  assert.match(mdHtml, /metaFileName\.title = value/);
  assert.match(mdHtml, /if \(readTimeEl\) readTimeEl\.textContent/);
});
