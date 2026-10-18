import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
const css = fs.readFileSync('wwwroot/css/studio-presentation.css', 'utf8');
const html = fs.readFileSync('wwwroot/index.html', 'utf8');

test('The dark canvas matches the FRB Launch base and retains selectable accent', () => {
  assert.match(css,/--bg:#202b29;--bg2:#202b29;/);
  assert.match(css,/--panel:#25343a;--panel-solid:#25343a;/);
  assert.match(css,/--accent:#6ba7ff/);
});
test('The Editor chrome has a 2px outline and a grey softened backdrop in both dark themes', () => {
  const both = 'body.frb-page-json-object:is([data-studio-theme="dark"],[data-studio-theme="launch-dark"])';
  assert.ok(css.includes(both+' #detailDialog {\n  border:2px solid'));
  assert.ok(css.includes(both+' #detailDialog::backdrop {'));
  assert.match(css,/background:rgba\(76,85,95,\.38\)/);
  assert.match(css,/backdrop-filter:blur\(3px\)/);
});
test('Header gradient is shared between the Editor title and Launch heading', () => {
  assert.match(css,/--studio-dark-header-gradient:linear-gradient/);
  assert.match(css,/\.studio-presentation-heading[^\{]+\{[\s\S]*?background:var\(--studio-dark-header-gradient\)/);
  assert.match(css,/#detailDialog \.dialog-title-row \{\n  background:var\(--studio-dark-header-gradient\)/);
  assert.match(html,/darkContrast=20261018/);
});
