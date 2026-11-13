import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(here, '../../..');
const read = rel => fs.readFileSync(path.join(root, rel), 'utf8');
const readJson = rel => JSON.parse(read(rel));

const md = read('wwwroot/mdViewer.html');
const bridge = read('wwwroot/js/core/native_host_bridge.js');
const dispatcher = read('NativeShell/NativeCommandDispatcher.cs');
const shellForm = read('NativeShell/NativeShellForm.cs');
const nativeConfig = readJson('NativeShell/native_shell.config.json');

test('Markdown UI promotes Folder Open + Workspace Tree and keeps INDEX on right column', () => {
  assert.match(md, /id="localFileBtn"[^>]*>📁 フォルダーを開く</);
  assert.match(md, /id="mdWorkspaceTree"/);
  assert.match(md, /<h2>INDEX \/ 目次<\/h2>/);
  assert.match(md, /grid-template-columns:\s*minmax\(280px, 1\.15fr\) minmax\(680px, 800px\) minmax\(300px, \.85fr\)/);
  assert.match(md, /\.workspace-sidebar \{ grid-column: 1; grid-row:1; \}/);
  assert.match(md, /\.article-card \{ grid-column: 2; grid-row:1; \}/);
  assert.match(md, /\.sidebar \{ grid-column: 3; grid-row:1; \}/);
});

test('URL flow and legacy data/markdown picker are removed from the primary visual flow', () => {
  assert.match(md, /md-managed-picker-wrap md-hidden-legacy/);
  assert.match(md, /control-group import-flow md-hidden-legacy/);
  assert.match(md, /class="md-drop-hint md-drop-wide"[^>]*>MarkdownをここへDrop</);
});

test('Markdown Folder Grant is independent from App Root workspace', () => {
  assert.match(dispatcher, /Dictionary<string, WorkspacePolicy> _folderGrants/);
  assert.match(dispatcher, /case "folderGrant\.select"/);
  assert.match(dispatcher, /new WorkspacePolicy\(dialog\.SelectedPath\)/);
  assert.doesNotMatch(md, /FRBStudioNativeHost\.invoke\('workspace\.select'/);
  assert.match(shellForm, /\/ App Root: /);
});

test('opening a Markdown folder has no side effect inside the selected Workspace', () => {
  const selectStart = dispatcher.indexOf('private object SelectFolderGrant');
  const selectEnd = dispatcher.indexOf('private object RestoreFolderGrant', selectStart);
  const selectBody = dispatcher.slice(selectStart, selectEnd);
  assert.doesNotMatch(selectBody, /File\.Copy|File\.Move/);
  assert.match(dispatcher, /LocalApplicationData/);
  const jsStart = md.indexOf('async function selectMarkdownWorkspaceFolder');
  const jsEnd = md.indexOf('async function loadMarkdownWorkspaceChildren', jsStart);
  assert.doesNotMatch(md.slice(jsStart, jsEnd), /folderGrant\.createDirectory|folderGrant\.writeText/);
});

test('new Markdown and folder creation require an active Markdown Workspace', () => {
  assert.match(md, /新規Markdownは、先に「フォルダーを開く」/);
  assert.match(md, /新規フォルダーは、先に「フォルダーを開く」/);
  assert.match(md, /folderGrant\.writeText/);
  assert.match(md, /folderGrant\.createDirectory/);
});

test('External Document Review forces explicit import and _imports is created only after full-path confirmation', () => {
  assert.match(md, /async function importCurrentDocumentIntoWorkspaceForComments/);
  assert.match(md, /const importFolder = '_imports'/);
  assert.match(md, /folderGrant\.describePath/);
  assert.match(md, /次のフォルダーはまだ存在しません/);
  const confirmIndex = md.indexOf("const ok = await showMarkdownConfirmDialog({ title:'Workspaceへ取り込み'");
  const createIndex = md.indexOf("folderGrant.createDirectory", confirmIndex);
  assert.ok(confirmIndex >= 0 && createIndex > confirmIndex, 'confirmation must happen before _imports creation');
  assert.match(md, /const ready = await importCurrentDocumentIntoWorkspaceForComments\(\)/);
});

test('External Open gets a document grant and overwrite uses only that grant', () => {
  assert.match(dispatcher, /var documentId = RegisterDocumentGrant\(selected\)/);
  assert.match(dispatcher, /private object WriteGrantedDocument/);
  assert.match(md, /document\.writeText/);
  for (const command of ['folderGrant.select','folderGrant.list','folderGrant.readText','folderGrant.writeText','folderGrant.exists','folderGrant.createDirectory','folderGrant.move','folderGrant.describePath','document.writeText']) {
    assert.ok(nativeConfig.allowed_commands.includes(command), `missing allowed command: ${command}`);
  }
});

test('Markdown Save As does not export Review JSON and move follows Review JSON inside Workspace', () => {
  assert.match(bridge, /Save As はMarkdown本文の自由な保存\/Exportとして扱い/);
  assert.match(bridge, /companions:\s*\[\]/);
  assert.match(md, /Markdownのみ保存しました。Review JSONは保存していません/);
  assert.match(md, /companion_suffixes:\s*source\.kind === 'file' \? \['\.review\.json'\] : \[\]/);
});

test('Workspace move preflights Review JSON destination before moving Markdown', () => {
  const moveStart = dispatcher.indexOf('private object MoveFolderGrantEntry');
  const moveEnd = dispatcher.indexOf('private string RegisterDocumentGrant', moveStart);
  const moveBody = dispatcher.slice(moveStart, moveEnd);
  const preflight = moveBody.indexOf('companion destination already exists');
  const mainMove = moveBody.indexOf('File.Move(source, destination)');
  assert.ok(preflight >= 0 && mainMove > preflight, 'Review JSON destination collision must be checked before Markdown is moved');
});

test('Front Matter is part of Canonical Markdown and no Apply button/state exists', () => {
  assert.doesNotMatch(md, /id="btnApplyFrontMatter"/);
  assert.doesNotMatch(md, /btnApplyFrontMatter/);
  assert.doesNotMatch(md, />本文へ反映</);
  assert.match(md, /function syncFrontMatterEditorToCanonicalMarkdown\(\)/);

  const syncStart = md.indexOf('function syncFrontMatterEditorToCanonicalMarkdown');
  const syncEnd = md.indexOf('// Front MatterフォームはCanonical Markdownへ即時同期する。', syncStart);
  const syncBody = md.slice(syncStart, syncEnd);
  assert.match(syncBody, /frontMatterDataFromEditor\(parsed\.data\)/);
  assert.match(syncBody, /replaceFrontMatter\(editorEl\.value, next\)/);
  assert.match(syncBody, /editorEl\.value = canonical/);
  assert.match(syncBody, /isManagedMarkdownDirty = true/);

  const fieldListenerStart = md.indexOf('[fmTitleInput, fmEmojiInput, fmTypeInput, fmTopicsInput, fmPublishedInput].forEach');
  const fieldListenerEnd = md.indexOf('// フロントマターの自動挿入', fieldListenerStart);
  assert.match(md.slice(fieldListenerStart, fieldListenerEnd), /syncFrontMatterEditorToCanonicalMarkdown\(\)/);
});

test('Front Matter generation immediately becomes Canonical Markdown and first body edit preserves it', () => {
  assert.match(md, /window\.insertSuggestedFrontMatter = function\(\)/);
  assert.match(md, /editorEl\.value = generatedFM \+ rawText;/);
  assert.match(md, /Markdown本文の一部として保存対象になりました/);

  assert.match(md, /function replaceMarkdownBodyPreservingFrontMatter\(rawMd, nextBody\)/);
  assert.match(md, /editorEl\.value = replaceMarkdownBodyPreservingFrontMatter\(editorEl\.value, insertText\)/,
    'Sentence insert into Front-Matter-only document must preserve Front Matter');
  assert.match(md, /editorEl\.value = replaceMarkdownBodyPreservingFrontMatter\(editorEl\.value, String\(newSource \|\| ""\)\)/,
    'Raw edit of empty body must preserve Front Matter');
});

test('Front Matter save materialization remains only as a final consistency guard', () => {
  assert.match(md, /function materializeFrontMatterForSave\(rawMd = editorEl\.value\)/);
  const materializeStart = md.indexOf('function materializeFrontMatterForSave');
  const materializeEnd = md.indexOf('// 保存ファイル名の入力欄同期', materializeStart);
  const materializeBody = md.slice(materializeStart, materializeEnd);
  assert.match(materializeBody, /if \(!parsed\.data\) return raw;/, 'no Front Matter must stay no Front Matter');
  assert.match(materializeBody, /frontMatterDataFromEditor\(parsed\.data\)/);
  assert.match(materializeBody, /replaceFrontMatter\(raw, next\)/);

  assert.match(md, /async function saveWorkspaceMarkdown[\s\S]*?const content = materializeFrontMatterForSave\(editorEl\.value \|\| ''\);/);
  assert.match(md, /async function saveExternalMarkdownOverwrite[\s\S]*?const content = materializeFrontMatterForSave\(editorEl\.value \|\| ''\);/);
  assert.match(md, /async function saveManagedMarkdown[\s\S]*?const saveContent = materializeFrontMatterForSave\(content\);/);
  assert.match(md, /async function saveMarkdownWithNativeDialog[\s\S]*?const content = materializeFrontMatterForSave\(editorEl\.value \|\| ""\);/);
});

test('NativeShell binds window.open to one child WebView2 instead of leaving an orphan blank window', () => {
  assert.match(shellForm, /var deferral = e\.GetDeferral\(\)/);
  assert.match(shellForm, /sharedEnvironment:\s*_environment/);
  assert.match(shellForm, /deferInitialNavigation:\s*true/);
  assert.match(shellForm, /e\.NewWindow = await child\.EnsureCoreWebViewReadyAsync\(\)/);
  assert.match(shellForm, /_environment = _sharedEnvironment \?\? await CoreWebView2Environment\.CreateAsync/);
  assert.match(shellForm, /if \(!_deferInitialNavigation\)[\s\S]*?_webView\.Source = new Uri\(startUri\)/);
  assert.match(shellForm, /finally[\s\S]*deferral\.Complete\(\)/);
});


test('Markdown Studio has explicit Review Mode as Human to AI structured feedback interface', () => {
  assert.match(md, /id="btnReviewMode"[^>]*>Review</);
  assert.match(md, /id="btnNewReview"[^>]*>＋ NEW Review</);
  assert.match(md, /document_type:\s*"markdown_review"/);
  assert.match(md, /return `\$\{base\}\.review\.json`/);
  assert.match(md, /snapshot:\s*\{[\s\S]*markdown:\s*snapshotMarkdown/);
  assert.match(md, /highlights:\s*mdCommentSidecarRuntime\.highlights/);
  assert.match(md, /保存対象：Review JSON/);
  assert.match(md, /data-status="APPROVED"[^>]*>✅ 承認</);
  assert.match(md, /data-status="REVISION_REQUIRED"[^>]*>🛠 要修正</);
  assert.match(md, /data-status="CHECK_REQUIRED"[^>]*>❓ 要確認</);
  assert.doesNotMatch(md, />🚫 Sidecar NG</);
  assert.doesNotMatch(md, />💾 Sidecar JSON保存</);
  assert.match(md, />🔎 段落情報</);
});

test('Review Mode freezes Markdown Snapshot and review actions are Review-only', () => {
  assert.match(md, /現在のMarkdownをレビュー用に固定してReview JSONへ保存します/);
  assert.match(md, /元のMarkdownはViewer \/ Editorで引き続き編集できます/);
  assert.match(md, /Review Modeでは固定文章へのコメント・判定・ハイライトのみ行えます/);
  assert.match(md, /editorEl\.readOnly = true/);
  assert.match(md, /if \(getMode\(\) !== "review"\) return;/);
  assert.match(md, /group === "all" \|\| group === mode/);
  assert.match(md, /getMode\(\) !== "review"/);
  assert.match(md, /setCurrentMarkdownBlockElement\(block\)/);
  assert.match(md, /mode === "viewer"[\s\S]*?clearCurrentPreviewBlock\(\)[\s\S]*?return;/);
  assert.match(md, /mode === "review"[\s\S]*?先に左クリックでレビュー対象の段落を選択してください/);
  assert.match(md, /applyMarkdownReviewHighlights\(\)/);
  assert.match(md, /captureMarkdownSourceBeforeReview\(\)/);
  assert.match(md, /if \(previousMode === "review"\) \{\s*restoreMarkdownSourceAfterReview\(\)/,
    'Markdown source must only be restored when actually leaving Review Mode');
});

test('NEW Review is always available for an opened Markdown while Review requires existing Review JSON', () => {
  assert.match(md, /btnNewReview\.disabled = !canReview/);
  assert.match(md, /btnReviewMode\.disabled = !canReview \|\| !markdownReviewAvailabilityRuntime\.exists/);
  assert.match(md, /btnReviewMode\?\.addEventListener\("click", \(\) => openExistingMarkdownReviewMode\(\)\)/);
  assert.match(md, /btnNewReview\?\.addEventListener\("click", \(\) => startNewMarkdownReview\(\)\)/);
  assert.match(md, /既存のReviewデータがあります/);
  assert.match(md, /現在のReview JSONを置き換えます/);
  assert.match(md, /先に「名前を付けて保存」してください/);
  assert.match(md, /okLabel: "新規レビュー開始"/);
  assert.match(md, /現在のMarkdownに未保存の変更があります/);
  assert.match(md, /保存してからNEW Reviewを開始します/);
  assert.match(md, /okLabel: "OK"/);
  assert.match(md, /saveCurrentMarkdownSourceForNewReview\(\)/);
  assert.match(md, /mdCommentSidecarRuntime\.comments = \[\]/);
  assert.match(md, /mdCommentSidecarRuntime\.highlights = \[\]/);
});

test('large Markdown warning is driven by app_settings before Workspace read', () => {
  const appSettings = readJson('wwwroot/config/app_settings.json');
  assert.equal(appSettings.markdown.large_file_warning_enabled, true);
  assert.ok(appSettings.markdown.large_file_warning_bytes > 0);
  const confirmPos = md.indexOf('const openOk = await confirmLargeMarkdownOpen(item)');
  const readPos = md.indexOf("await loadWorkspaceMarkdown(path)", confirmPos);
  assert.ok(confirmPos >= 0 && readPos > confirmPos);
});

test('JSON Object Studio primary save label is 保存 instead of 上書き保存', () => {
  const runtime = read('wwwroot/js/runtime/load_runtime.js');
  assert.match(runtime, /currentDataApiUrl \? '保　存' : '別名保存'/);
  assert.doesNotMatch(runtime, /currentDataApiUrl \? '上書き保存'/);
});


test('Markdown Save Safety does not persist unused localStorage backups', () => {
  const backupStart = md.indexOf('function createMarkdownSaveSafetyBackup');
  const backupEnd = md.indexOf('async function runMarkdownSaveSafetyBeforeSave', backupStart);
  const backupBody = md.slice(backupStart, backupEnd);
  assert.doesNotMatch(backupBody, /localStorage\.setItem/);
  assert.match(md, /function clearLegacyMarkdownSaveSafetyBackups\(\)/);
  assert.match(md, /key\.startsWith\(prefix\)/);
  assert.match(md, /window\.addEventListener\("beforeunload", clearLegacyMarkdownSaveSafetyBackups\)/);
  assert.doesNotMatch(md, /直前バックアップはlocalStorageに残しています/);
  assert.doesNotMatch(md, /直前バックアップ: localStorage/);
});

test('Markdown comment review action buttons stay horizontal', () => {
  assert.match(md, /\.md-comment-review-actions\s*\{[\s\S]*?flex-wrap:\s*nowrap/);
  assert.match(md, /\.md-comment-review-actions button\s*\{[\s\S]*?white-space:\s*nowrap/);
  assert.match(md, /\.md-comment-review-actions button\s*\{[\s\S]*?writing-mode:\s*horizontal-tb/);
});


test('Markdown Studio warns before Common Shell navigation when Markdown or Review changes are unsaved', () => {
  assert.match(md, /function hasUnsavedMarkdownNavigationState\(\)[\s\S]*?isManagedMarkdownDirty \|\| mdCommentSidecarRuntime\.dirty/);
  assert.match(md, /function installMarkdownUnsavedNavigationGuard\(\)/);
  assert.match(md, /\.frb-app-shell a\[href\], \.frb-pagebar a\[href\]/);
  assert.match(md, /\.frb-pagebar \[data-frb-home\]/);
  assert.match(md, /現在のMarkdownに未保存の変更があります。保存せずに別の画面へ移動しますか/);
  assert.match(md, /okLabel:'移動する'/);
  assert.match(md, /window\.addEventListener\('beforeunload'/);
  assert.match(md, /event\.returnValue = ''/);
});

test('Markdown Folder Open is the single Workspace entry and opens the explicit full-path NativeShell dialog', () => {
  assert.match(md, /id="localFileBtn"[^>]*>📁 フォルダーを開く<\/button>/);
  assert.match(md, /id="localFileBtn"[^>]*フルパスの貼り付け[^>]*Windows標準の「参照\.\.\.」/);
  assert.doesNotMatch(md, /id="btnWorkspacePathOpen"/);
  assert.doesNotMatch(md, /📋 フルパスを貼り付けて開く/);
  assert.match(md, /async function selectMarkdownWorkspaceFolder\(\)/);
  assert.match(md, /localFileBtn\.addEventListener\(\"click\",[\s\S]*?selectMarkdownWorkspaceFolder\(\)/);
  assert.match(md, /FRBStudioNativeHost\.invoke\('folderGrant\.promptPath'/);
  assert.match(md, /initial_path:\s*markdownWorkspaceRuntime\.rootPath \|\| ''/);
  assert.doesNotMatch(md, /FRBStudioNativeHost\.invoke\('folderGrant\.select'/);
  assert.doesNotMatch(md, /folderGrant\.openPath/);

  assert.ok(nativeConfig.allowed_commands.includes('folderGrant.promptPath'));
  assert.match(dispatcher, /case "folderGrant\.promptPath"/);
  assert.match(dispatcher, /private object PromptFolderGrantPath/);
  assert.match(dispatcher, /new TextBox/);
  assert.match(dispatcher, /Explorerのアドレスバーからコピーしたフォルダーのフルパス/);
  assert.match(dispatcher, /Path\.IsPathRooted\(rawPath\)/);
  assert.match(dispatcher, /Directory\.Exists\(fullPath\)/);
  assert.match(dispatcher, /pathBox\.SelectAll\(\)/);
  assert.match(dispatcher, /ActivateFolderGrant\(policy, persistKey, restored: false\)/);
});

test('Markdown Folder Open keeps the full-path keyboard shortcut and never lets JS grant an arbitrary absolute path silently', () => {
  assert.match(md, /event\.ctrlKey/);
  assert.match(md, /event\.shiftKey/);
  assert.match(md, /toLowerCase\(\) !== 'o'/);
  assert.match(md, /selectMarkdownWorkspaceFolder\(\)/);
  assert.doesNotMatch(md, /selectMarkdownWorkspaceFolderByPath/);
  assert.doesNotMatch(nativeConfig.allowed_commands.join('\n'), /folderGrant\.openPath/);
  assert.doesNotMatch(dispatcher, /case "folderGrant\.openPath"/);
  assert.match(dispatcher, /dialog\.ShowDialog\(\) != DialogResult\.OK/);
});

test('Markdown primary toolbar keeps save actions on one line when Display Profile is visible', () => {
  assert.match(md, /\.frb-page-markdown \.topbar \.control-group\.primary-flow > button,[\s\S]*?flex: 0 0 auto;[\s\S]*?white-space: nowrap;/);
  assert.match(md, /#btnOverwriteManagedMd \{ min-width: 68px; \}/);
  assert.match(md, /#btnMarkdownSaveSafety \{ min-width: 84px; \}/);
  assert.match(md, /#btnSaveFile \{ min-width: 132px; \}/);
});

test('Markdown display profile changes heading presentation without rewriting Markdown heading levels', () => {
  assert.match(md, /id="mdDisplayProfile"/);
  assert.match(md, /<option value="standard">標準<\/option>/);
  assert.match(md, /<option value="compact">コンパクト<\/option>/);
  assert.match(md, /data-md-display-profile="compact"/);
  assert.match(md, /html\[data-md-display-profile="compact"\] \.markdown-body h1 \{ font-size: 24px;/);
  assert.match(md, /html\[data-md-display-profile="compact"\] \.markdown-body h2 \{ font-size: 20px;/);
  assert.match(md, /MARKDOWN_DISPLAY_PROFILE_STORAGE_KEY = 'frb\.markdown\.displayProfile'/);
  assert.match(md, /applyMarkdownDisplayProfile\(mdDisplayProfile\.value, \{ persist: true \}\)/);

  const start = md.indexOf('function applyMarkdownDisplayProfile');
  const end = md.indexOf('function loadMarkdownDisplayProfile', start);
  const body = md.slice(start, end);
  assert.doesNotMatch(body, /editorEl\.value|replaceFrontMatter|#{1,6}/,
    'display profile must not modify canonical Markdown or heading syntax');
});
