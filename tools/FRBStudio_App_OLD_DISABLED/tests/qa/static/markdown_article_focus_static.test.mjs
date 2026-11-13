import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';

const ROOT = process.cwd();
const md = fs.readFileSync(path.join(ROOT, 'wwwroot/mdViewer.html'), 'utf8');

test('Markdown article focus action lives in the Common Pagebar, maximizes only the article lane, and restores with the same toggle', () => {
  assert.match(md, /button\.id = 'btnMarkdownFocusArticle'/);
  assert.match(md, /actions\.insertBefore\(button, actions\.firstChild\)/);
  assert.match(md, /data-md-focus-label>本文を最大化/);
  assert.match(md, /active \? '元に戻す' : '本文を最大化'/);

  assert.match(md, /body\.frb-page-markdown\.md-article-focus \.workspace-sidebar,[\s\S]*?body\.frb-page-markdown\.md-article-focus \.sidebar \{[\s\S]*?display: none !important;/);
  assert.match(md, /body\.frb-page-markdown\.md-article-focus \.layout,[\s\S]*?grid-template-columns: minmax\(0, 1fr\) !important;/);
  assert.match(md, /body\.frb-page-markdown\.md-article-focus \.article-card \{[\s\S]*?grid-column: 1 !important;[\s\S]*?width: 100%;/);

  assert.match(md, /function setMarkdownArticleFocus\(active\)[\s\S]*?classList\.toggle\('md-article-focus', Boolean\(active\)\)/);
  assert.match(md, /btnMarkdownFocusArticle\?\.addEventListener\('click',[\s\S]*?setMarkdownArticleFocus\(!isMarkdownArticleFocusActive\(\)\)/);
  assert.match(md, /event\.key !== 'Escape'[\s\S]*?isAnyMarkdownDialogOpen\(\)[\s\S]*?setMarkdownArticleFocus\(false\)/);
});

test('Markdown article focus keeps the Markdown operation toolbar available and does not rebuild the document DOM', () => {
  assert.doesNotMatch(md, /md-article-focus \.topbar\s*\{[^}]*display:\s*none/i);
  assert.doesNotMatch(md, /setMarkdownArticleFocus\(active\)[\s\S]{0,500}(?:renderMarkdown|innerHTML\s*=|location\.)/);
  assert.match(md, /body classだけを変更し、Markdown DOMや選択中ファイルを再生成しない/);
});
