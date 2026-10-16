import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
const read = path => readFileSync(path, 'utf8');

const html = read('wwwroot/index.html');
const css = read('wwwroot/styles.css');
const runtime = read('wwwroot/js/runtime/detail_save.js');

function htmlSlice(start, end) {
  const begin = html.indexOf(start);
  assert.ok(begin >= 0, `missing ${start}`);
  const finish = html.indexOf(end, begin);
  assert.ok(finish > begin, `missing ${end}`);
  return html.slice(begin, finish);
}

test('Detail actions are outside the only scrolling region and retain canonical button IDs', () => {
  const modal = htmlSlice('<dialog id="detailDialog">', '</dialog>');
  assert.match(modal, /<div class="detail-scroll-content" id="detailScrollContent">/);
  assert.match(modal, /id="detailForm"/);
  assert.match(modal, /id="detailComponentBodyArea"/);
  assert.match(modal, /id="childArea"/);
  assert.match(modal, /id="detailComponentAfterChildArea"/);
  assert.match(modal, /id="detailComponentFooterArea"/);
  assert.match(modal, /<\/div>\s*<div class="button-row detail-footer">/);
  const beforeFooter = modal.slice(0, modal.indexOf('<div class="button-row detail-footer">'));
  assert.match(beforeFooter, /id="detailComponentFooterArea"[\s\S]*<\/div>\s*<\/div>\s*$/);
  const footer = modal.slice(modal.indexOf('<div class="button-row detail-footer">'));
  for (const id of ['copyDetailJsonBtn', 'pasteDetailJsonBtn', 'prevDetailBtn', 'nextDetailBtn', 'applyDetailBtn']) {
    assert.equal((footer.match(new RegExp(`id="${id}"`, 'g')) || []).length, 1, id);
  }
});

test('Header/footer are non-scrolling flex rows; only detail-scroll-content has vertical scroll', () => {
  assert.match(css, /#detailDialog \.dialog-body\s*\{[^}]*overflow:\s*hidden/s);
  assert.match(css, /#detailDialog \.detail-scroll-content\s*\{[^}]*flex:\s*1 1 auto;[^}]*overflow-y:\s*auto/s);
  assert.match(css, /#detailDialog \.detail-footer\s*\{[^}]*position:\s*relative;[^}]*flex:\s*0 0 auto;[^}]*overflow:\s*visible/s);
  assert.match(css, /#detailDialog \.detail-navigation-actions\s*\{\s*margin-left:\s*auto;\s*\}/);
  assert.doesNotMatch(css, /#detailDialog \.detail-footer\s*\{[^}]*overflow-x:\s*auto/s);
});

test('Detail rebind preserves scroll on new content scroller, not the action/footer container', () => {
  const fn = htmlSlice; // keep test declaration consistent across tooling
  assert.match(runtime, /function rebindDetailAfterCanonicalCommit\([^]*?const scrollArea = \$\('detailScrollContent'\)/);
  assert.match(runtime, /const restore = \(\) => \{ scrollArea\.scrollTop = scrollTop; \}/);
  assert.doesNotMatch(runtime, /const body = \$\('detailDialog'\)\?\.querySelector\?\.\('\.dialog-body'\)/);
});

test('Evidence review retains two-column layout inside the scroller, not on the modal flex body', () => {
  assert.match(css, /#detailDialog \.dialog-body\.definition-evidence-review-layout > \.detail-scroll-content\s*\{[^}]*display:\s*grid;[^}]*grid-template-columns:/s);
  assert.match(css, /#detailDialog \.dialog-body\.definition-evidence-review-layout > \.detail-scroll-content > #detailComponentBodyArea/);
});
