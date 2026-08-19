import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(here, '../../..');
const md = fs.readFileSync(path.join(root, 'wwwroot/mdViewer.html'), 'utf8');

test('Markdown Workspace tree has a draggable right-edge resizer that changes only workspace/article allocation', () => {
  assert.match(md, /id="mdWorkspaceResizer"[^>]*class="md-workspace-resizer"[^>]*role="separator"/);
  assert.match(md, /\.md-workspace-resizer\s*\{[\s\S]*?right:\s*-10px;[\s\S]*?cursor:\s*col-resize/);
  assert.match(md, /body\.frb-page-markdown\.md-workspace-width-adjusted \.layout,[\s\S]*?grid-template-columns:\s*var\(--md-workspace-width\) minmax\(0, 1fr\) var\(--md-right-sidebar-width\) !important;/);
  assert.match(md, /const rightRect = rightSidebar\?\.getBoundingClientRect\(\)/);
  assert.match(md, /document\.documentElement\.style\.setProperty\('--md-right-sidebar-width', `\$\{Math\.round\(rightWidth\)\}px`\)/);
  assert.match(md, /document\.documentElement\.style\.setProperty\('--md-workspace-width', `\$\{Math\.round\(nextWidth\)\}px`\)/);
});

test('Workspace width adjustment is temporary and resets when a workspace Markdown is actually opened', () => {
  assert.match(md, /function resetMarkdownWorkspaceColumnWidth\(\)[\s\S]*?classList\.remove\('md-workspace-width-adjusted', 'md-workspace-resizing'\)/);
  assert.match(md, /removeProperty\('--md-workspace-width'\)/);
  assert.match(md, /removeProperty\('--md-right-sidebar-width'\)/);

  const loadStart = md.indexOf('async function loadWorkspaceMarkdown(relativePath)');
  const loadEnd = md.indexOf('async function saveWorkspaceMarkdown', loadStart);
  const loadBody = md.slice(loadStart, loadEnd);
  const dirtyGuard = loadBody.indexOf("if (isManagedMarkdownDirty");
  const reset = loadBody.indexOf('resetMarkdownWorkspaceColumnWidth()');
  const read = loadBody.indexOf("folderGrant.readText");
  assert.ok(dirtyGuard >= 0 && reset > dirtyGuard && read > reset,
    'tree width must reset after open guards pass and before Markdown is read/displayed');

  assert.match(md, /mdWorkspaceResizer\.addEventListener\('dblclick', \(\) => resetMarkdownWorkspaceColumnWidth\(\)\)/);
  assert.match(md, /installMarkdownWorkspaceColumnResizer\(\);/);
});

test('Workspace resizer stays out of article focus and narrow single-column layouts', () => {
  assert.match(md, /body\.frb-page-markdown\.md-article-focus \.md-workspace-resizer \{ display:none !important; \}/);
  assert.match(md, /@media \(max-width: 760px\)[\s\S]*?\.md-workspace-resizer \{ display:none; \}/);
  assert.match(md, /window\.innerWidth <= 760 \|\| isMarkdownArticleFocusActive\(\)/);
});
