// v0.18.137 Readable Textarea / Read first, edit when needed
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(here, '../../..');
const controls = fs.readFileSync(path.join(root, 'wwwroot/js/renderers/field_controls.js'), 'utf8');
const css = fs.readFileSync(path.join(root, 'wwwroot/styles.css'), 'utf8');
const gridDetail = fs.readFileSync(path.join(root, 'wwwroot/js/renderers/grid_detail.js'), 'utf8');
const detailSave = fs.readFileSync(path.join(root, 'wwwroot/js/runtime/detail_save.js'), 'utf8');
const linksView = JSON.parse(fs.readFileSync(path.join(root, 'defs/common/studio_resource_links_view_def_v0_1.json'), 'utf8'));
const textareaStart = controls.indexOf('function createMarkdownTextareaDisplayElement');
const textareaEnd = controls.indexOf('function createTextareaControlElement', textareaStart);
const textareaControlSection = controls.slice(textareaStart, textareaEnd);
const textareaCssStart = css.indexOf('v0.18.137-readable-textarea');
const textareaCssEnd = css.indexOf('v0.10.1-markdown-block-preview-fix', textareaCssStart);
const textareaCssSection = css.slice(textareaCssStart, textareaCssEnd);

function findField(node, fieldName) {
  if (!node || typeof node !== 'object') return null;
  if (node.field === fieldName) return node;
  for (const value of Object.values(node)) {
    if (Array.isArray(value)) {
      for (const child of value) {
        const found = findField(child, fieldName);
        if (found) return found;
      }
    } else if (value && typeof value === 'object') {
      const found = findField(value, fieldName);
      if (found) return found;
    }
  }
  return null;
}

test('Detail and Header textarea default to Markdown Reading View while explicit markdown:false can opt out', () => {
  assert.match(controls, /else if \(field\?\.type === 'textarea'\) \{\s*result\.enabled = true;/);
  assert.match(controls, /configs\.some\(markdownConfigExplicitlyDisabled\)[\s\S]*?result\.enabled = false/);
  assert.match(controls, /\(prefix === 'detail' \|\| prefix === 'header'\) && mdCfg\.enabled[\s\S]*?createMarkdownTextareaDisplayElement/);
  assert.match(controls, /Searchは入力用途を優先して従来textareaのまま/);
});



test('Header Readable Textarea preserves raw Markdown when header edits are collected', () => {
  assert.match(detailSave, /headerForm[\s\S]*?data-markdown-display=\"true\"[\s\S]*?getControlValue/);
  assert.match(gridDetail, /dataset\?\.markdownDisplay === 'true'[\s\S]*?dataset\.rawValue/);
  assert.match(gridDetail, /dataset\.editMode === 'raw'[\s\S]*?markdownPreviewRawValue/);
  assert.match(controls, /dataset\?\.prefix[\s\S]*?!== 'detail'\) return/);
});

test('Readable textarea enters raw edit on click/focus and returns to preview on blur without helper badges', () => {
  assert.match(controls, /box\.tabIndex = 0/);
  assert.match(controls, /box\.addEventListener\('click',[\s\S]*?enterRawEditMode\(\)/);
  assert.match(controls, /box\.addEventListener\('focus', \(\) => enterRawEditMode\(\)\)/);
  assert.match(controls, /installMarkdownBlurPreview\(box, mdCfg/);
  assert.doesNotMatch(textareaControlSection, /クリックするとMarkdown原文を編集できます/);
  assert.doesNotMatch(textareaCssSection, /content:\s*'クリックで編集'/);
  assert.doesNotMatch(textareaCssSection, /content:\s*'Markdown原文を編集中'/);
});

test('Readable textarea has only a subtle visual hint and Studio resource note is back to textarea', () => {
  assert.match(css, /\.markdown-textarea-display \{[\s\S]*?box-shadow:\s*inset 3px 0 0/);
  assert.match(css, /\.markdown-textarea-display\.markdown-editable-display:hover \{[\s\S]*?border-color:/);
  assert.match(css, /\.markdown-textarea-display\.markdown-raw-editing \{[\s\S]*?outline:/);

  const note = findField(linksView, 'note');
  assert.ok(note, 'note field should exist');
  assert.equal(note.type, 'textarea');
  assert.equal(note.edit?.readonly, false);
});
