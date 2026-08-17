import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(here, '../../..');
const read = rel => fs.readFileSync(path.join(root, rel), 'utf8');

test('Diff JSON Viewer saves loaded Diff JSON only by explicit Save As action', () => {
  const viewer = read('wwwroot/DiffJsonViewer.html');
  const bridge = read('wwwroot/js/core/native_host_bridge.js');

  assert.match(viewer, /js\/core\/native_host_bridge\.js/);
  assert.match(viewer, /id="saveAsBtn"[^>]*disabled/);
  assert.match(viewer, />名前を付けて保存<\/button>/);
  assert.match(viewer, /function saveDiffJsonAs\(\)/);
  assert.match(viewer, /fetch\("\/api\/diff\/save-as-dialog"/);
  assert.match(viewer, /JSON\.stringify\(diffJson, null, 2\)/);
  assert.match(viewer, /button\.disabled = !diffJson/);
  assert.match(viewer, /function downloadDiffJson\(/);
  assert.match(viewer, /a\.download = fileName/);

  assert.match(bridge, /path === '\/api\/diff\/save-as-dialog'/);
  assert.match(bridge, /invoke\('dialog\.saveText'/);
  assert.match(bridge, /Diff JSONを名前を付けて保存/);
  assert.match(bridge, /default_extension: 'json'/);
});

test('Diff JSON Viewer suggests a timestamped formal filename for DiffToJson_current.json', () => {
  const viewer = read('wwwroot/DiffJsonViewer.html');

  assert.match(viewer, /sourceName\.toLowerCase\(\) !== "difftojson_current\.json"/);
  assert.match(viewer, /data\?\.generated_at/);
  assert.match(viewer, /DiffToJson_\$\{match\[1\]\}\$\{match\[2\]\}\$\{match\[3\]\}_\$\{match\[4\]\}\$\{match\[5\]\}\$\{match\[6\]\}\.json/);
});
