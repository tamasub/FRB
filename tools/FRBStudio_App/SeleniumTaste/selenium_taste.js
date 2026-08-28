'use strict';

const fs = require('node:fs');
const path = require('node:path');
const readline = require('node:readline/promises');
const { stdin: input, stdout: output } = require('node:process');

const {
  Builder,
  Browser,
  By,
  Key,
  error,
} = require('selenium-webdriver');
const edge = require('selenium-webdriver/edge');

const APP_ROOT = path.resolve(__dirname, '..');
const NATIVE_SHELL = process.env.FRB_NATIVE_SHELL
  || path.join(APP_ROOT, 'NativeShell', '_publish', 'FRBStudio.NativeShell.exe');

const EDGE_DRIVER_CANDIDATES = [
  process.env.FRB_EDGE_DRIVER,
  path.join(__dirname, 'driver', 'edgedriver_win64', 'msedgedriver.exe'),
  path.join(__dirname, 'driver', 'msedgedriver.exe'),
].filter(Boolean);

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

function findExistingEdgeDriver() {
  return EDGE_DRIVER_CANDIDATES.find((candidate) => fs.existsSync(candidate)) || null;
}

function assertFileExists(filePath, label) {
  if (!fs.existsSync(filePath)) {
    throw new Error(`${label} が見つかりません: ${filePath}`);
  }
}

async function readControlValue(control) {
  const propertyValue = await control.getProperty('value');
  if (propertyValue !== null && propertyValue !== undefined) {
    return String(propertyValue);
  }

  const attributeValue = await control.getAttribute('value');
  if (attributeValue !== null && attributeValue !== undefined) {
    return String(attributeValue);
  }

  return control.getText();
}

function normalizeLineEndings(value) {
  return String(value ?? '').replace(/\r\n/g, '\n').replace(/\r/g, '\n');
}

function toSingleLineDisplay(value) {
  return normalizeLineEndings(value).replace(/\n/g, ' ');
}

function lineEndingLabel(value) {
  const text = String(value ?? '');
  if (text.includes('\r\n')) return 'CRLF';
  if (text.includes('\n')) return 'LF';
  if (text.includes('\r')) return 'CR';
  return 'NONE';
}

async function waitUntil(condition, timeoutMs = 5000, intervalMs = 100) {
  const started = Date.now();

  while (Date.now() - started < timeoutMs) {
    try {
      if (await condition()) {
        return true;
      }
    } catch (err) {
      if (!(err instanceof error.StaleElementReferenceError)
        && !(err instanceof error.NoSuchElementError)) {
        throw err;
      }
      // 再描画中は次のpollでDOMを取り直す。
    }

    await sleep(intervalMs);
  }

  return false;
}

function assertPass(passed, label, detail = null) {
  console.log(`${label}: ${passed ? 'PASS' : 'FAIL'}`);
  if (!passed) {
    throw new Error(detail ? `${label} failed: ${detail}` : `${label} failed`);
  }
}

async function createDriver() {
  assertFileExists(NATIVE_SHELL, 'NativeShell');

  const options = new edge.Options()
    .useWebView(true)
    .setEdgeChromiumBinaryPath(NATIVE_SHELL);

  const driverPath = findExistingEdgeDriver();
  let builder = new Builder()
    .forBrowser(Browser.EDGE)
    .setEdgeOptions(options);

  if (driverPath) {
    console.log(`EdgeDriver: ${driverPath}`);
    builder = builder.setEdgeService(new edge.ServiceBuilder(driverPath));
  } else {
    console.log('EdgeDriver: ローカル配置なし（Selenium Manager / PATH に委譲）');
  }

  console.log(`NativeShell: ${NATIVE_SHELL}`);
  return builder.build();
}

async function main() {
  const driver = await createDriver();

  async function isDetailDialogOpen() {
    const dialog = await driver.findElement(By.id('detailDialog'));
    return Boolean(await dialog.getProperty('open'));
  }

  async function closeDetailDialog() {
    if (await isDetailDialogOpen()) {
      const dialog = await driver.findElement(By.id('detailDialog'));
      const closeButton = await dialog.findElement(By.css("button[value='cancel']"));
      await closeButton.click();
      await waitUntil(async () => !(await isDetailDialogOpen()));
    }
  }

  async function openSecondRowAndVerifyWorkItem() {
    const rows = await driver.findElements(By.css('#dataGrid tbody tr'));
    console.log(`Grid行数: ${rows.length}`);

    if (rows.length < 2) {
      throw new Error('Gridが2行以上ありません');
    }

    await driver.actions().doubleClick(rows[1]).perform();
    console.log('2行目をダブルクリックしました');

    const opened = await waitUntil(isDetailDialogOpen);
    assertPass(opened, 'エディター表示');

    const detailDialog = await driver.findElement(By.id('detailDialog'));
    const workItemIdControl = await detailDialog.findElement(
      By.css("#detailForm [data-field='work_item_id']"),
    );

    const workItemId = await readControlValue(workItemIdControl);
    console.log(`work_item_id: ${workItemId}`);

    assertPass(
      workItemId === 'studio_work_0002',
      'work_item_id 読取',
      `Expected=studio_work_0002, Actual=${workItemId}`,
    );

    return detailDialog;
  }

  async function readTitleFromOpenDetail() {
    const detailDialog = await driver.findElement(By.id('detailDialog'));
    const titleControl = await detailDialog.findElement(
      By.css("#detailForm [data-field='title']"),
    );
    return readControlValue(titleControl);
  }

  async function setTitleAndApply(value) {
    const detailDialog = await driver.findElement(By.id('detailDialog'));
    const titleControl = await detailDialog.findElement(
      By.css("#detailForm [data-field='title']"),
    );

    await titleControl.clear();
    await titleControl.sendKeys(value);

    const draft = await readControlValue(titleControl);
    console.log(`title UI入力後: ${draft}`);
    assertPass(draft === value, 'title UI入力');

    await titleControl.sendKeys(Key.F12);
    console.log('F12を送信しました');

    const reflected = await waitUntil(async () => {
      const refreshedDialog = await driver.findElement(By.id('detailDialog'));
      const refreshedTitle = await refreshedDialog.findElement(
        By.css("#detailForm [data-field='title']"),
      );
      return (await readControlValue(refreshedTitle)) === value;
    });

    const titleAfter = await readTitleFromOpenDetail();
    console.log(`title F12反映後: ${titleAfter}`);
    assertPass(reflected && titleAfter === value, 'title F12反映');
  }

  async function findSubGridCard(fieldName) {
    const detailDialog = await driver.findElement(By.id('detailDialog'));
    return detailDialog.findElement(
      By.css(`.detail-subgrid-edit[data-subgrid-field="${fieldName}"]`),
    );
  }

  async function readSubGridCellValue(fieldName, rowIndex, columnName) {
    const card = await findSubGridCard(fieldName);
    const rows = await card.findElements(By.css('tbody tr'));

    if (rows.length <= rowIndex) {
      throw new Error(
        `${fieldName} の行数不足: RequiredIndex=${rowIndex}, ActualRows=${rows.length}`,
      );
    }

    const control = await rows[rowIndex].findElement(
      By.css(`.detail-subgrid-cell-input[data-column="${columnName}"]`),
    );
    return readControlValue(control);
  }


  async function findSubGridPreviewFieldBox(fieldName, rowIndex, columnName) {
    const card = await findSubGridCard(fieldName);
    const header = await card.findElement(
      By.css(`thead th[data-column="${columnName}"]`),
    );
    const columnCaption = (await header.getText()).trim();

    const editButtons = await card.findElements(By.xpath(
      ".//button[normalize-space()='プレビュー編集']",
    ));
    if (editButtons.length < 1) {
      throw new Error(`${fieldName} のプレビュー編集ボタンが見つかりません`);
    }

    await editButtons[0].click();

    const opened = await waitUntil(async () => {
      const overlays = await driver.findElements(
        By.css('dialog.detail-subgrid-card-editor-overlay[open]'),
      );
      return overlays.length > 0;
    });
    assertPass(opened, 'プレビュー編集 表示');

    const overlay = await driver.findElement(
      By.css('dialog.detail-subgrid-card-editor-overlay[open]'),
    );
    const cards = await overlay.findElements(
      By.css('.detail-subgrid-card-editor-card'),
    );

    if (cards.length <= rowIndex) {
      throw new Error(
        `プレビュー編集 ${fieldName} の行数不足: RequiredIndex=${rowIndex}, ActualRows=${cards.length}`,
      );
    }

    const fieldLines = await cards[rowIndex].findElements(
      By.css('.detail-subgrid-card-editor-field'),
    );

    for (const line of fieldLines) {
      const labels = await line.findElements(By.css('.detail-subgrid-preview-label'));
      if (labels.length < 1) continue;
      const label = (await labels[0].getText()).trim();
      if (label === columnCaption || label === columnName) {
        return line.findElement(
          By.css('.detail-subgrid-card-preview-edit-value'),
        );
      }
    }

    throw new Error(
      `プレビュー編集の列が見つかりません: ${fieldName}.${columnName} caption=${columnCaption}`,
    );
  }

  async function openSubGridPreviewTextarea(fieldName, rowIndex, columnName) {
    const box = await findSubGridPreviewFieldBox(fieldName, rowIndex, columnName);
    await box.click();

    const appeared = await waitUntil(async () => {
      const editors = await driver.findElements(
        By.css('dialog.detail-subgrid-card-editor-overlay[open] .detail-subgrid-card-preview-editor'),
      );
      return editors.length > 0;
    });
    assertPass(appeared, 'プレビュー編集 textarea表示');

    const editor = await driver.findElement(
      By.css('dialog.detail-subgrid-card-editor-overlay[open] .detail-subgrid-card-preview-editor'),
    );
    const tagName = String(await editor.getTagName()).toLowerCase();
    assertPass(
      tagName === 'textarea',
      'プレビュー編集 textarea種別',
      `Expected=textarea, Actual=${tagName}`,
    );
    return editor;
  }

  async function applyPreviewEditorToSubGridList() {
    const overlay = await driver.findElement(
      By.css('dialog.detail-subgrid-card-editor-overlay[open]'),
    );
    const applyButtons = await overlay.findElements(By.xpath(
      ".//button[normalize-space()='一覧へ反映']",
    ));
    if (applyButtons.length < 1) {
      throw new Error('プレビュー編集の「一覧へ反映」ボタンが見つかりません');
    }

    await applyButtons[0].click();
    const closed = await waitUntil(async () => {
      const overlays = await driver.findElements(
        By.css('dialog.detail-subgrid-card-editor-overlay[open]'),
      );
      return overlays.length === 0;
    });
    assertPass(closed, 'プレビュー編集 一覧へ反映');
  }

  async function applySubGridWithF12(fieldName, rowIndex, columnName, label='サブグリッド F12反映') {
    const card = await findSubGridCard(fieldName);
    const rows = await card.findElements(By.css('tbody tr'));
    if (rows.length <= rowIndex) {
      throw new Error(
        `${fieldName} の行数不足: RequiredIndex=${rowIndex}, ActualRows=${rows.length}`,
      );
    }

    const control = await rows[rowIndex].findElement(
      By.css(`.detail-subgrid-cell-input[data-column="${columnName}"]`),
    );

    await control.sendKeys(Key.F12);
    console.log('サブグリッド一覧からF12を送信しました');

    // E2Eでは内部propertyではなく、UI上の「未反映 -> 反映済み」契約だけを見る。
    const committed = await waitUntil(async () => {
      const refreshedCard = await findSubGridCard(fieldName);
      const className = await refreshedCard.getAttribute('class');
      return !String(className ?? '').includes('is-dirty');
    });
    assertPass(committed, label);
  }

  async function setSubGridCellAndApply(fieldName, rowIndex, columnName, value) {
    const card = await findSubGridCard(fieldName);
    const rows = await card.findElements(By.css('tbody tr'));
    console.log(`${fieldName} 行数: ${rows.length}`);

    if (rows.length <= rowIndex) {
      throw new Error(
        `${fieldName} の行数不足: RequiredIndex=${rowIndex}, ActualRows=${rows.length}`,
      );
    }

    const control = await rows[rowIndex].findElement(
      By.css(`.detail-subgrid-cell-input[data-column="${columnName}"]`),
    );

    await control.clear();
    await control.sendKeys(value);

    const draft = await readControlValue(control);
    console.log(`${fieldName}[${rowIndex}].${columnName} UI入力後: ${draft}`);
    assertPass(
      draft === value,
      'サブグリッド UI入力',
      `Expected=${value}, Actual=${draft}`,
    );

    const dirtyClass = await card.getAttribute('class');
    assertPass(
      dirtyClass.includes('is-dirty'),
      'サブグリッド 未反映状態',
      dirtyClass,
    );

    await control.sendKeys(Key.F12);
    console.log('サブグリッドからF12を送信しました');

    const reflected = await waitUntil(async () => (
      (await readSubGridCellValue(fieldName, rowIndex, columnName)) === value
    ));

    const after = await readSubGridCellValue(fieldName, rowIndex, columnName);
    console.log(`${fieldName}[${rowIndex}].${columnName} F12反映後: ${after}`);
    assertPass(
      reflected && after === value,
      'サブグリッド F12反映',
      `Expected=${value}, Actual=${after}`,
    );
  }

  async function saveAndVerifyStatus(label) {
    await closeDetailDialog();

    const saveBtn = await driver.findElement(By.id('saveBtn'));
    const enabled = await saveBtn.isEnabled();
    console.log(`保存ボタン Enabled: ${enabled}`);
    assertPass(enabled, `${label} 保存ボタン`);

    await saveBtn.click();
    console.log('保存ボタンをクリックしました');

    const saved = await waitUntil(async () => {
      const status = await driver.findElement(By.id('status')).getText();
      return status.includes('上書き保存しました');
    }, 8000);

    const statusText = await driver.findElement(By.id('status')).getText();
    console.log(`保存Status: ${statusText}`);
    assertPass(saved, `${label} 上書き保存`, statusText);
  }

  async function reloadCurrentData() {
    const loadBtn = await driver.findElement(By.id('loadBtn'));
    await loadBtn.click();
    console.log('再読込ボタンをクリックしました');

    const reloaded = await waitUntil(async () => {
      const status = await driver.findElement(By.id('status')).getText();
      const rows = await driver.findElements(By.css('#dataGrid tbody tr'));
      return !status.includes('上書き保存しました') && rows.length >= 2;
    }, 8000);

    assertPass(reloaded, '再読込');
  }

  try {
    // STEP 0: 対象JSONを選択してロード。
    await sleep(3000);

    const dataCombo = await driver.findElement(By.id('dataNameInput'));
    await dataCombo.click();
    await dataCombo.clear();
    await dataCombo.sendKeys('_studio_work_incident_data_v2.json');
    await sleep(500);
    await dataCombo.sendKeys(Key.ENTER);
    await sleep(300);

    console.log(`選択値: ${await dataCombo.getAttribute('value')}`);

    const loadBtn = await driver.findElement(By.id('loadBtn'));
    console.log(`読込ボタン Enabled: ${await loadBtn.isEnabled()}`);
    await loadBtn.click();
    console.log('読込ボタンをクリックしました');

    await sleep(2000);

    // STEP 1: Row Detail Editor の状態を読む。
    await openSecondRowAndVerifyWorkItem();
    const titleBefore = await readTitleFromOpenDetail();
    const marker = ' [SeleniumTaste]';
    const titleExpected = titleBefore + marker;
    console.log(`title 変更前: ${titleBefore}`);

    // STEP 2: UI入力 -> F12でcanonical Dataへ反映。
    await setTitleAndApply(titleExpected);

    // STEP 3: 実際の「保存」ボタンでファイルへ上書き保存。
    await saveAndVerifyStatus('変更値');

    // STEP 4: 同じJSONを再読込し、保存値が残っていることを確認。
    await reloadCurrentData();
    await openSecondRowAndVerifyWorkItem();
    const titleReloaded = await readTitleFromOpenDetail();
    console.log(`title 再読込後: ${titleReloaded}`);
    assertPass(
      titleReloaded === titleExpected,
      'title 保存・再読込',
      `Expected=${titleExpected}, Actual=${titleReloaded}`,
    );

    // STEP 5: テスト痕跡を残さないよう元タイトルへ戻して再保存。
    console.log('後始末: 元タイトルへ戻します');
    await setTitleAndApply(titleBefore);
    await saveAndVerifyStatus('後始末');

    // STEP 6: 最後に再読込し、元の状態へ戻ったことまで確認。
    await reloadCurrentData();
    await openSecondRowAndVerifyWorkItem();
    const titleRestored = await readTitleFromOpenDetail();
    console.log(`title 後始末再読込後: ${titleRestored}`);
    assertPass(
      titleRestored === titleBefore,
      '後始末',
      `Expected=${titleBefore}, Actual=${titleRestored}`,
    );

    console.log('基本項目 保存E2E: ALL PASS');

    // STEP 7: objectArrayサブグリッドを直接編集し、F12 -> 保存 -> 再読込まで確認。
    console.log('--- サブグリッドE2E: discussion_history[0].message ---');
    const subGridField = 'discussion_history';
    const subGridRowIndex = 0;
    const subGridColumn = 'message';
    const subGridMarker = ' [SubGridSeleniumTaste]';
    const subGridBefore = await readSubGridCellValue(
      subGridField,
      subGridRowIndex,
      subGridColumn,
    );
    const subGridExpected = subGridBefore + subGridMarker;
    console.log(`サブグリッド 変更前: ${subGridBefore}`);

    await setSubGridCellAndApply(
      subGridField,
      subGridRowIndex,
      subGridColumn,
      subGridExpected,
    );

    await saveAndVerifyStatus('サブグリッド変更値');

    // STEP 8: 再読込後もobjectArray内の変更値が残っていることを確認。
    await reloadCurrentData();
    await openSecondRowAndVerifyWorkItem();
    const subGridReloaded = await readSubGridCellValue(
      subGridField,
      subGridRowIndex,
      subGridColumn,
    );
    console.log(`サブグリッド 再読込後: ${subGridReloaded}`);
    assertPass(
      subGridReloaded === subGridExpected,
      'サブグリッド 保存・再読込',
      `Expected=${subGridExpected}, Actual=${subGridReloaded}`,
    );

    // STEP 9: テスト痕跡を残さないようサブグリッドも元値へ戻す。
    console.log('サブグリッド後始末: 元メッセージへ戻します');
    await setSubGridCellAndApply(
      subGridField,
      subGridRowIndex,
      subGridColumn,
      subGridBefore,
    );
    await saveAndVerifyStatus('サブグリッド後始末');

    // STEP 10: 最後に再読込し、サブグリッドの元値復元まで保証。
    await reloadCurrentData();
    await openSecondRowAndVerifyWorkItem();
    const subGridRestored = await readSubGridCellValue(
      subGridField,
      subGridRowIndex,
      subGridColumn,
    );
    console.log(`サブグリッド 後始末再読込後: ${subGridRestored}`);
    assertPass(
      subGridRestored === subGridBefore,
      'サブグリッド 後始末',
      `Expected=${subGridBefore}, Actual=${subGridRestored}`,
    );

    console.log('サブグリッド保存E2E: ALL PASS');

    // STEP 11: Preview EditのtextareaでEnter改行を入力し、
    // 一覧は1行表示、保存・再読込後のPreview原文は複数行保持、というUI契約を確認。
    console.log('--- サブグリッド複数行E2E: Preview Edit / Enter改行保持 ---');
    const multiLineMarker2 = '[SubGridMultiLineSeleniumTaste: Line 2]';
    const multiLineMarker3 = '[SubGridMultiLineSeleniumTaste: Line 3]';

    let previewTextarea = await openSubGridPreviewTextarea(
      subGridField,
      subGridRowIndex,
      subGridColumn,
    );
    const previewInitialRaw = await readControlValue(previewTextarea);
    const multiLineBefore = normalizeLineEndings(previewInitialRaw);
    const multiLineExpected = `${multiLineBefore}\n${multiLineMarker2}\n${multiLineMarker3}`;
    console.log(`複数行 変更前 (${lineEndingLabel(previewInitialRaw)}):\n${previewInitialRaw}`);
    assertPass(
      normalizeLineEndings(previewInitialRaw) === multiLineBefore,
      'プレビュー編集 初期原文保持',
    );

    await previewTextarea.sendKeys(Key.chord(Key.CONTROL, 'a'));
    await previewTextarea.sendKeys(multiLineBefore);
    await previewTextarea.sendKeys(Key.ENTER);
    await previewTextarea.sendKeys(multiLineMarker2);
    await previewTextarea.sendKeys(Key.ENTER);
    await previewTextarea.sendKeys(multiLineMarker3);

    const multiLineDraftRaw = await readControlValue(previewTextarea);
    const multiLineDraft = normalizeLineEndings(multiLineDraftRaw);
    console.log(`プレビュー編集 複数行UI入力後 (${lineEndingLabel(multiLineDraftRaw)}):\n${multiLineDraftRaw}`);
    assertPass(
      multiLineDraft === multiLineExpected,
      'プレビュー編集 Enter改行入力',
      `Expected=${multiLineExpected}, Actual=${multiLineDraft}`,
    );

    // Preview Edit内ではF12は明示機能ではないため無効。押しても編集状態と入力値を維持する。
    await previewTextarea.sendKeys(Key.F12);
    console.log('プレビュー編集textareaからF12を送信しました（無効確認）');
    const previewF12Ignored = await waitUntil(async () => {
      const editors = await driver.findElements(
        By.css('dialog.detail-subgrid-card-editor-overlay[open] .detail-subgrid-card-preview-editor'),
      );
      if (editors.length !== 1) return false;
      const current = normalizeLineEndings(await readControlValue(editors[0]));
      return current === multiLineExpected;
    });
    assertPass(previewF12Ignored, 'プレビュー編集 F12無効');

    // Preview内部の編集値は「一覧へ反映」でSubGrid一覧へ反映する。
    await applyPreviewEditorToSubGridList();

    // 一覧はレビュー用の1行表示。複数行原文は改行を空白へ変換して全文を1行化して表示する。
    const listDisplayAfterApply = await readSubGridCellValue(
      subGridField,
      subGridRowIndex,
      subGridColumn,
    );
    const singleLineExpected = toSingleLineDisplay(multiLineExpected);
    console.log(`一覧へ反映後 1行表示: ${listDisplayAfterApply}`);
    assertPass(
      !/[\r\n]/.test(listDisplayAfterApply)
        && listDisplayAfterApply === singleLineExpected,
      'プレビュー編集 一覧1行表示',
      `Expected=${singleLineExpected}, Actual=${listDisplayAfterApply}`,
    );

    // SubGrid一覧 -> 親JSONへF12反映。内部propertyではなくUIの反映状態を確認する。
    await applySubGridWithF12(
      subGridField,
      subGridRowIndex,
      subGridColumn,
      '複数行 親JSON F12反映',
    );

    await saveAndVerifyStatus('複数行変更値');

    // STEP 12: 再読込後にPreview Editを開き、原文の3行が保持されていることを最終Expectedとする。
    await reloadCurrentData();
    await openSecondRowAndVerifyWorkItem();

    previewTextarea = await openSubGridPreviewTextarea(
      subGridField,
      subGridRowIndex,
      subGridColumn,
    );
    const previewReloadedRaw = await readControlValue(previewTextarea);
    const previewReloaded = normalizeLineEndings(previewReloadedRaw);
    console.log(`プレビュー編集 再読込後原文 (${lineEndingLabel(previewReloadedRaw)}):\n${previewReloadedRaw}`);
    assertPass(
      previewReloaded === multiLineExpected,
      '複数行 保存・再読込 Preview原文保持',
      `Expected=${multiLineExpected}, Actual=${previewReloaded}`,
    );

    // STEP 13: Preview Edit経由で元値へ復元し、再保存・再読込まで確認。
    console.log('複数行後始末: Preview Editから元メッセージへ戻します');
    await previewTextarea.sendKeys(Key.chord(Key.CONTROL, 'a'));
    await previewTextarea.sendKeys(multiLineBefore);
    const restoreDraftRaw = await readControlValue(previewTextarea);
    const restoreDraft = normalizeLineEndings(restoreDraftRaw);
    assertPass(
      restoreDraft === multiLineBefore,
      '複数行後始末 UI入力',
      `Expected=${multiLineBefore}, Actual=${restoreDraft}`,
    );

    // 復元時もPreview内F12は使わず、「一覧へ反映」で確定する。
    await applyPreviewEditorToSubGridList();
    const restoredListDisplay = await readSubGridCellValue(
      subGridField,
      subGridRowIndex,
      subGridColumn,
    );
    assertPass(
      !/[\r\n]/.test(restoredListDisplay)
        && restoredListDisplay === toSingleLineDisplay(multiLineBefore),
      '複数行後始末 一覧1行表示',
      `Expected=${toSingleLineDisplay(multiLineBefore)}, Actual=${restoredListDisplay}`,
    );

    await applySubGridWithF12(
      subGridField,
      subGridRowIndex,
      subGridColumn,
      '複数行後始末 親JSON F12反映',
    );
    await saveAndVerifyStatus('複数行後始末');

    await reloadCurrentData();
    await openSecondRowAndVerifyWorkItem();
    previewTextarea = await openSubGridPreviewTextarea(
      subGridField,
      subGridRowIndex,
      subGridColumn,
    );
    const restoredPreviewRaw = await readControlValue(previewTextarea);
    const restoredPreview = normalizeLineEndings(restoredPreviewRaw);
    console.log(`複数行 後始末再読込後 (${lineEndingLabel(restoredPreviewRaw)}):\n${restoredPreviewRaw}`);
    assertPass(
      restoredPreview === multiLineBefore,
      '複数行 後始末',
      `Expected=${multiLineBefore}, Actual=${restoredPreview}`,
    );

    console.log('サブグリッド複数行保存E2E: ALL PASS');
    console.log('保存E2E: ALL PASS');
    console.log('画面確認中。Enterで終了します');

    const rl = readline.createInterface({ input, output });
    await rl.question('');
    rl.close();
  } finally {
    await driver.quit();
  }
}

async function runEntryPoint() {
  const responsibilityIndex = process.argv.indexOf('--responsibility');
  if (responsibilityIndex >= 0) {
    const responsibilityCd = process.argv[responsibilityIndex + 1] || 'data_update_persist';
    const planOnly = process.argv.includes('--plan-only');
    const { runResponsibilitySelenium } = require('./responsibility_selenium_runner');
    return runResponsibilitySelenium({ responsibilityCd, planOnly });
  }
  return main();
}

runEntryPoint().catch((err) => {
  console.error(err);
  process.exitCode = 1;
});
