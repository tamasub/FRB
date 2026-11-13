import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(here, '../../..');
const md = fs.readFileSync(path.join(root, 'wwwroot/mdViewer.html'), 'utf8');

test('Markdown Workspace and INDEX boundary both have draggable resizers centered in the inter-column gap', () => {
  assert.match(md, /id="mdWorkspaceResizer"[^>]*class="md-workspace-resizer"[^>]*role="separator"/);
  assert.match(md, /id="mdSidebarResizer"[^>]*class="md-sidebar-resizer"[^>]*role="separator"/);
  assert.match(md, /\.md-workspace-resizer,\s*\.md-sidebar-resizer\s*\{[\s\S]*?cursor:\s*col-resize/);
  assert.match(md, /\.md-workspace-resizer \{ right:\s*-1px; \}/);
  assert.match(md, /\.md-workspace-resizer::after,[\s\S]*?left:\s*50%;[\s\S]*?transform:\s*translateX\(-50%\)/);
  assert.match(md, /function syncMarkdownColumnResizerPositions\(\)[\s\S]*?mdWorkspaceResizer\.style\.left =/);
  assert.match(md, /function syncMarkdownColumnResizerPositions\(\)[\s\S]*?mdSidebarResizer\.style\.left =/);
});

test('Workspace width adjustment still changes only workspace/article allocation while keeping right sidebar width fixed', () => {
  assert.match(md, /body\.frb-page-markdown\.md-workspace-width-adjusted \.layout,[\s\S]*?grid-template-columns:\s*var\(--md-workspace-width\) minmax\(0, 1fr\) var\(--md-right-sidebar-width\) !important;/);
  assert.match(md, /const rightRect = rightSidebar\?\.getBoundingClientRect\(\)/);
  assert.match(md, /document\.documentElement\.style\.setProperty\('--md-right-sidebar-width', `\$\{Math\.round\(rightWidth\)\}px`\)/);
  assert.match(md, /const rawWidth = event\.clientX - workspaceDrag\.layoutLeft - workspaceDrag\.gapHalf/);
  assert.match(md, /document\.documentElement\.style\.setProperty\('--md-workspace-width', `\$\{Math\.round\(nextWidth\)\}px`\)/);
});

test('Right resizer adjusts article/sidebar allocation and both resizers reset to standard width on file open or double click', () => {
  assert.match(md, /window\.innerWidth <= 1180 \|\| isMarkdownArticleFocusActive\(\)/);
  assert.match(md, /const rawWidth = sidebarDrag\.layoutRight - event\.clientX - sidebarDrag\.gapHalf/);
  assert.match(md, /document\.documentElement\.style\.setProperty\('--md-right-sidebar-width', `\$\{Math\.round\(nextWidth\)\}px`\)/);
  assert.match(md, /mdSidebarResizer\.addEventListener\('dblclick', \(\) => resetMarkdownWorkspaceColumnWidth\(\)\)/);
  assert.match(md, /mdWorkspaceResizer\.addEventListener\('dblclick', \(\) => resetMarkdownWorkspaceColumnWidth\(\)\)/);
  assert.match(md, /function resetMarkdownWorkspaceColumnWidth\(\)[\s\S]*?removeProperty\('--md-workspace-width'\)[\s\S]*?removeProperty\('--md-right-sidebar-width'\)/);

  const loadStart = md.indexOf('async function loadWorkspaceMarkdown(relativePath)');
  const loadEnd = md.indexOf('async function saveWorkspaceMarkdown', loadStart);
  const loadBody = md.slice(loadStart, loadEnd);
  const dirtyGuard = loadBody.indexOf('if (isManagedMarkdownDirty');
  const reset = loadBody.indexOf('resetMarkdownWorkspaceColumnWidth()');
  const read = loadBody.indexOf('folderGrant.readText');
  assert.ok(dirtyGuard >= 0 && reset > dirtyGuard && read > reset,
    'column widths must reset after open guards pass and before Markdown is read/displayed');
});

test('Both resizers stay out of article focus and narrow single-column layouts', () => {
  assert.match(md, /body\.frb-page-markdown\.md-article-focus \.md-workspace-resizer,\s*body\.frb-page-markdown\.md-article-focus \.md-sidebar-resizer \{ display:none !important; \}/);
  assert.match(md, /@media \(max-width: 760px\)[\s\S]*?\.md-workspace-resizer,\s*\.md-sidebar-resizer \{ display:none; \}/);
});
