import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import { fileURLToPath } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(here, '../../..');
const mdViewer = fs.readFileSync(path.join(root, 'wwwroot/mdViewer.html'), 'utf8');

function loadMarkdownBlockParser() {
  const start = mdViewer.indexOf('function padBlockNo');
  const end = mdViewer.indexOf('function setMarkdownBlockModel');
  assert.ok(start >= 0 && end > start, 'Markdown Block Model parser source must exist');

  const parserSource = mdViewer.slice(start, end);
  const sandbox = {
    headingContextForLine: () => ({
      headingLine: 0,
      headingText: '',
      headingNorm: '',
      headingOccurrence: 0,
      offset: 0
    }),
    stripMarkdownBlockPrefix: line => String(line || '').trim()
  };
  vm.createContext(sandbox);
  vm.runInContext(`${parserSource}\nthis.__parseMarkdownBlocks = parseMarkdownBlocks;\nthis.__isMarkdownListItemLine = isMarkdownListItemLine;`, sandbox);
  return sandbox;
}

test('Markdown Block Model recognizes bare Markdown list markers as list items', () => {
  const runtime = loadMarkdownBlockParser();
  for (const sample of ['-', '+', '*', '1.', '-  ', '1.  ', '- value', '1. value', '・ 項目', '・項目']) {
    assert.equal(runtime.__isMarkdownListItemLine(sample), true, `expected list marker: ${sample}`);
  }
  for (const sample of ['- ', '+ ', '* ', '1. ', '・', '・ ']) {
    assert.equal(runtime.__isMarkdownListItemLine(sample), false, `marked.js renders this as paragraph: ${JSON.stringify(sample)}`);
  }
  assert.equal(runtime.__isMarkdownListItemLine('---'), false, 'horizontal rule must not become a list item');
});

test('Empty template list items do not consume later heading/block anchors', () => {
  const runtime = loadMarkdownBlockParser();
  const sample = [
    '# 5. 追加責務記入テンプレート',
    '',
    '### Summary',
    '',
    '-',
    '',
    '### Purpose',
    '',
    '- ',
    '',
    '---',
    '',
    '## Revision History',
    '',
    '- 2026-08-22 / v0.4: sample',
    '',
    '----',
    '',
    'ほんまそれ🤣'
  ].join('\n');

  const blocks = runtime.__parseMarkdownBlocks(sample);
  assert.deepEqual(
    JSON.parse(JSON.stringify(blocks.map(block => [block.type, block.start_line]))),
    [
      ['heading', 1],
      ['heading', 3],
      ['list_item', 5],
      ['heading', 7],
      ['paragraph', 9],
      ['horizontal_rule', 11],
      ['heading', 13],
      ['list_item', 15],
      ['horizontal_rule', 17],
      ['paragraph', 19]
    ]
  );
});

test('Empty list item insertion keeps a valid Markdown marker plus one space', () => {
  assert.match(mdViewer, /const gap = listMatch\.spacing \|\| " ";[\s\S]{0,160}return `\$\{listMatch\.indent\}\$\{listMatch\.marker\}\$\{gap\}新しい項目`;/);
});
