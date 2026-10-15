import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';

const read = name => fs.readFileSync(name,'utf8');
const css = read('wwwroot/css/studio-presentation.css');
const originalCss = read('wwwroot/styles.css');

test('Related Grid modal and iframe frame are themed at the shared presentation layer', () => {
  for (const selector of [
    '.related-grid-modal-panel',
    '.related-grid-modal-header',
    '.related-grid-modal-body',
    '.related-grid-modal-frame',
    '.related-grid-modal-close',
  ]) {
    assert.ok(css.includes(selector), `${selector}: missing theme rules`);
  }
  assert.match(css,/body\.frb-page-json-object:is\(\[data-studio-theme="dark"\],\[data-studio-theme="launch-dark"\]\) \.related-grid-modal-panel/);
});

test('Child related grid banner and status are themed, including semantic statuses', () => {
  assert.match(css,/body\.frb-page-json-object:is\(\[data-studio-theme="dark"\],\[data-studio-theme="launch-dark"\]\) \.related-grid-shell-banner \{/);
  for (const kind of ['success','warn','error']) {
    assert.ok(css.includes(`.related-grid-shell-status[data-kind="${kind}"]`), `missing ${kind} status`);
  }
});

test('Standard theme retains existing related-grid light defaults', () => {
  assert.match(originalCss,/\.related-grid-modal-panel \{[\s\S]*?background: #f5f8ff;/);
  assert.match(originalCss,/\.related-grid-shell-banner \{[\s\S]*?background: linear-gradient/);
  assert.doesNotMatch(css,/body\.frb-page-json-object\[data-studio-theme="light"\] \.related-grid-modal-header/);
});

test('CSS cache key is bumped so desktop NativeShell loads the new theme', () => {
  assert.match(read('wwwroot/index.html'),/studio-presentation-004-related-grid-theme/);
});
