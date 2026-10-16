import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';

const html = fs.readFileSync('wwwroot/index.html', 'utf8');
const shared = fs.readFileSync('wwwroot/styles.css', 'utf8');
const presentation = fs.readFileSync('wwwroot/css/studio-presentation.css', 'utf8');
const selectSection = (text, start, end) => text.slice(text.indexOf(start), text.indexOf(end, text.indexOf(start)));

test('standard and launch settings use the same full-text search and action buttons', () => {
  const section = selectSection(html, '<section id="searchSection"', '<section id="gridSection"');
  for (const id of ['studioFullTextSearchInput', 'searchBtn', 'clearSearchBtn']) {
    assert.match(section, new RegExp(`id="${id}"`));
  }
  assert.match(section, /class="section-title-row studio-search-title-row"/);
  assert.match(section, /class="button-row compact"/);
});

test('common search CSS keeps labels, variable-width input, and action buttons in a single row', () => {
  const css = selectSection(shared, '/* ===== 全Studio共通: 全文検索', '/* v0.18.28-related-grid-view-launch:');
  assert.match(css, /grid-template-columns:\s*minmax\(0,\s*1fr\)\s+max-content/);
  assert.match(css, /\.studio-full-text-search-control\s*\{[^}]*display:\s*flex;[^}]*flex-wrap:\s*nowrap;/);
  assert.match(css, /#studioFullTextSearchInput\s*\{[^}]*flex:\s*1 1 0%;[^}]*width:\s*0;[^}]*min-width:\s*0;/);
  assert.match(css, /\.studio-search-title-row\s*>\s*\.button-row\s*\{[^}]*flex-wrap:\s*nowrap;/);
  assert.doesNotMatch(css, /@media\s*\(max-width:\s*720px\)/);
});

test('minimal presentation never returns to 2-row layout at <=700px', () => {
  const css = selectSection(presentation, 'body.frb-page-json-object[data-studio-shell="minimal"] #searchSection {', '/* v0.2: complete detail-editor');
  assert.match(css, /#searchSection \.studio-search-title-row\s*\{\s*grid-template-columns:minmax\(0,1fr\) max-content;/);
  assert.doesNotMatch(css, /#searchSection \.studio-search-title-row\s*\{\s*grid-template-columns:\s*1fr;/);
  assert.doesNotMatch(css, /#searchSection \.button-row\.compact\s*\{\s*justify-content:flex-end;/);
});

test('webview stylesheet query versions change so the layout is not stale from cache', () => {
  assert.match(html, /styles\.css\?[^"]*fullSearchRow=20261016/);
  assert.match(html, /studio-presentation\.css\?[^"]*fullSearchRow=20261016/);
});
