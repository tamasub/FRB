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
  assert.match(md, /grid-template-columns:\s*280px minmax\(0, 1fr\) 300px/);
  assert.match(md, /\.workspace-sidebar \{ grid-column: 1; grid-row:1; \}/);
  assert.match(md, /\.article-card \{ grid-column: 2; grid-row:1; \}/);
  assert.match(md, /\.sidebar \{ grid-column: 3; grid-row:1; \}/);
});

test('URL flow and legacy data/markdown picker are removed from the primary visual flow', () => {
  assert.match(md, /md-managed-picker-wrap md-hidden-legacy/);
  assert.match(md, /control-group import-flow md-hidden-legacy/);
  assert.match(md, /class="md-drop-hint"[^>]*>MD Drop</);
});

test('Markdown Folder Grant is independent from App Root workspace', () => {
  assert.match(dispatcher, /Dictionary<string, WorkspacePolicy> _folderGrants/);
  assert.match(dispatcher, /case "folderGrant\.select"/);
  assert.match(dispatcher, /new WorkspacePolicy\(dialog\.SelectedPath\)/);
  assert.doesNotMatch(md, /FRBStudioNativeHost\.invoke\('workspace\.select'/);
  assert.match(shellForm, /\/ App Root: /);
});

test('opening a Markdown folder has no file-system creation side effect', () => {
  const selectStart = dispatcher.indexOf('private object SelectFolderGrant');
  const selectEnd = dispatcher.indexOf('private WorkspacePolicy RequiredFolderGrant', selectStart);
  const selectBody = dispatcher.slice(selectStart, selectEnd);
  assert.doesNotMatch(selectBody, /CreateDirectory|WriteAllText|File\.Copy|File\.Move/);
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

test('External Document comments force explicit import and _imports is created only after full-path confirmation', () => {
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

test('Save As does not export Sidecar outside Workspace and move follows Sidecar inside Workspace', () => {
  assert.match(bridge, /Save As はMarkdown本文の自由な保存\/Exportとして扱い/);
  assert.match(bridge, /companions:\s*\[\]/);
  assert.match(md, /Workspace外のためSidecarコメントは保存していません/);
  assert.match(md, /companion_suffixes:\s*source\.kind === 'file' \? \['\.comments\.json'\] : \[\]/);
});

test('Workspace move preflights Sidecar destination before moving Markdown', () => {
  const moveStart = dispatcher.indexOf('private object MoveFolderGrantEntry');
  const moveEnd = dispatcher.indexOf('private string RegisterDocumentGrant', moveStart);
  const moveBody = dispatcher.slice(moveStart, moveEnd);
  const preflight = moveBody.indexOf('companion destination already exists');
  const mainMove = moveBody.indexOf('File.Move(source, destination)');
  assert.ok(preflight >= 0 && mainMove > preflight, 'Sidecar destination collision must be checked before Markdown is moved');
});
