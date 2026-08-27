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

    console.log('保存E2E: ALL PASS');
    console.log('画面確認中。Enterで終了します');

    const rl = readline.createInterface({ input, output });
    await rl.question('');
    rl.close();
  } finally {
    await driver.quit();
  }
}

main().catch((err) => {
  console.error(err);
  process.exitCode = 1;
});
