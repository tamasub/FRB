import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const root = path.resolve(__dirname, '../../..');
const readText = relative => fs.readFileSync(path.join(root, relative), 'utf8');

test('detail footer exposes Studio JSON Round Trip buttons and runtime', () => {
  const index = readText('wwwroot/index.html');
  assert.match(index, /id="copyDetailJsonBtn"/);
  assert.match(index, /id="pasteDetailJsonBtn"/);
  assert.match(index, /id="studioJsonRoundTripDiff"/);
  assert.match(index, /js\/runtime\/studio_json_round_trip\.js\?v=studio-json-round-trip-01835/);
});

test('Round Trip runtime covers partial JSON, readonly guard, F12 boundary, and subgrids', () => {
  const runtime = readText('wwwroot/js/runtime/studio_json_round_trip.js');
  assert.match(runtime, /contractsForGrid/);
  assert.match(runtime, /objectArray/);
  assert.match(runtime, /stringArray/);
  assert.match(runtime, /isDetailSubGridEditable/);
  assert.match(runtime, /hasByPath\(payload, contract\.path\)/);
  assert.match(runtime, /if \(!contract\.editable\)/);
  assert.match(runtime, /renderDetailForRow\(working\)/);
  assert.match(runtime, /F12で反映/);
  assert.match(runtime, /navigator\.clipboard\?\.readText/);
  assert.match(runtime, /showStudioPromptDialog/);
  assert.match(runtime, /```\(\?:json\)/);
});

test('app initializes Studio JSON Round Trip once', () => {
  const app = readText('wwwroot/app.js');
  assert.match(app, /setupStudioJsonRoundTrip/);
});

test('detail render clears stale Round Trip diff state before switching rows', () => {
  const detailSave = readText('wwwroot/js/runtime/detail_save.js');
  assert.match(detailSave, /clearStudioJsonRoundTripDiff/);
});
