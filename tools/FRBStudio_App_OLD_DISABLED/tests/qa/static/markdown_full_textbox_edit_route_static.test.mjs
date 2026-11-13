import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(here, '../../..');
const md = fs.readFileSync(path.join(root, 'wwwroot/mdViewer.html'), 'utf8');

test('Markdown Editor context menu keeps the whole-document textbox edit route beside raw block edit', () => {
  assert.match(md, /data-action="editRawBlock"[^>]*>✏ 行編集<\/button>[\s\S]{0,220}data-action="editTextBox"[^>]*>📝 テキストボックス編集<\/button>/);
  assert.match(md, /btn\.dataset\.action === "editTextBox"[\s\S]{0,420}enterInlineMarkdownEdit\(line, anchor\)/);
});

test('Whole-document textbox edit route still moves the canonical editor into the article lane and can restore preview', () => {
  assert.match(md, /function enterInlineMarkdownEdit\(lineNo, anchor = null\)[\s\S]*?classList\.add\("md-inline-editing"\)[\s\S]*?editorInlineHost\.appendChild\(editorEl\)[\s\S]*?moveCaretToLine\(line, "auto"\)/);
  assert.match(md, /body\.md-inline-editing #preview \{ display: none; \}/);
  assert.match(md, /body\.md-inline-editing #editorInlineHost \{ display: block; \}/);
  assert.match(md, /function leaveInlineMarkdownEdit\([\s\S]*?classList\.remove\("md-inline-editing"\)[\s\S]*?renderMarkdown\(editorEl\.value, "#", "Editor Blur Preview"\)/);
});
