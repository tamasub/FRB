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
  assert.match(index, /js\/runtime\/studio_json_round_trip\.js\?v=studio-json-round-trip-018353/);
});

test('Round Trip runtime covers partial JSON, readonly guard, F12 boundary, and subgrids', () => {
  const runtime = readText('wwwroot/js/runtime/studio_json_round_trip.js');
  assert.match(runtime, /contractsForGrid/);
  assert.match(runtime, /objectArray/);
  assert.match(runtime, /stringArray/);
  assert.match(runtime, /isDetailSubGridEditable/);
  assert.match(runtime, /hasByPath\(payload, contract\.path\)/);
  assert.match(runtime, /if \(!contract\.editable\)/);
  assert.match(runtime, /setPendingDraft\(working\)/);
  assert.match(runtime, /renderDetailForRow\(working\)/);
  assert.match(runtime, /consumePendingDraft/);
  assert.match(runtime, /allowedOptionValues/);
  assert.match(runtime, /subGrid\.columns契約/);
  assert.match(runtime, /edit\.visible=false.*共通サブグリッド/s);
  assert.match(runtime, /chat composer.*userField/s);
  assert.match(runtime, /target-context/);
  assert.match(runtime, /F12で反映/);
  assert.match(runtime, /navigator\.clipboard\?\.readText/);
  assert.match(runtime, /showStudioPromptDialog/);
  assert.match(runtime, /```\(\?:json\)/);
});

test('app initializes Studio JSON Round Trip once', () => {
  const app = readText('wwwroot/app.js');
  assert.match(app, /setupStudioJsonRoundTrip/);
});

test('detail editing and save lifecycle use the Round Trip pending draft', () => {
  const fieldControls = readText('wwwroot/js/renderers/field_controls.js');
  const gridDetail = readText('wwwroot/js/renderers/grid_detail.js');
  const detailSave = readText('wwwroot/js/runtime/detail_save.js');
  assert.match(fieldControls, /getStudioJsonRoundTripDraftRow/);
  assert.match(gridDetail, /consumeStudioJsonRoundTripDraft/);
  assert.match(detailSave, /consumeStudioJsonRoundTripDraft/);
  assert.match(detailSave, /discardStudioJsonRoundTripDraft/);
});

test('detail render clears stale Round Trip diff state before switching rows', () => {
  const detailSave = readText('wwwroot/js/runtime/detail_save.js');
  assert.match(detailSave, /clearStudioJsonRoundTripDiff/);
});


test('Studio common dialog uses the browser top layer so it appears above the detail editor dialog', () => {
  const index = readText('wwwroot/index.html');
  const dialog = readText('wwwroot/js/ui/studio_dialog.js');
  assert.match(index, /js\/ui\/studio_dialog\.js\?v=studio-dialog-top-layer-018352/);
  assert.match(dialog, /document\.createElement\('dialog'\)/);
  assert.match(dialog, /backdrop\.showModal\(\)/);
  assert.match(dialog, /runtime\.backdrop\?\.open/);
  assert.match(dialog, /\.studio-dialog-backdrop\[open\]/);
});

test('Round Trip working row explicitly preserves edits made after paste until F12', () => {
  const runtime = readText('wwwroot/js/runtime/studio_json_round_trip.js');
  assert.match(runtime, /貼り付け時点の固定スナップショット.*ではなく/);
  assert.match(runtime, /applyDetailInputsToRow\(pendingDraftRow\)/);
  assert.match(runtime, /貼り付け後の手修正も含めてF12で反映/);
});


test('detail editor exposes a single maximize/restore toggle and a sticky title header', () => {
  const index = readText('wwwroot/index.html');
  const app = readText('wwwroot/app.js');
  const styles = readText('wwwroot/styles.css');

  assert.match(index, /id="detailDialogSizeToggleBtn"/);
  assert.match(index, /type="button"[\s\S]*aria-label="詳細画面を最大化"/);
  assert.match(index, /app\.js\?v=detail-dialog-expand-01836/);
  assert.match(index, /styles\.css\?v=field-definition-caption-header-01848/);

  assert.match(app, /function setDetailDialogExpanded/);
  assert.match(app, /detail-dialog-expanded/);
  assert.match(app, /詳細画面を元のサイズに戻す/);
  assert.match(app, /setupDetailDialogSizeToggle\(\)/);

  assert.match(styles, /#detailDialog\.detail-dialog-expanded/);
  assert.match(styles, /width:\s*calc\(100vw - var\(--detail-dialog-expanded-gap\) - var\(--detail-dialog-expanded-gap\)\)/);
  assert.match(styles, /height:\s*calc\(100vh - var\(--detail-dialog-expanded-gap\) - var\(--detail-dialog-expanded-gap\)\)/);
  assert.match(styles, /detail-window-icon::after/);
  assert.match(styles, /#detailDialog \.dialog-title-row\s*\{[\s\S]*position:\s*sticky/);
  assert.match(styles, /#detailDialog \.dialog-title-row\s*\{[\s\S]*top:\s*0/);
  assert.match(styles, /#detailDialog \.dialog-title-row\s*\{[\s\S]*z-index:\s*8/);
});
