'use strict';

const fs = require('node:fs');
const path = require('node:path');
const {
  Builder,
  Browser,
  By,
  Key,
  error,
} = require('selenium-webdriver');
const edge = require('selenium-webdriver/edge');
const { pathToFileURL } = require('node:url');

const {
  APP_ROOT,
  buildResponsibilityExecutionPlan,
  assertExecutionApproved,
  diffJson,
  formatPlanSummary,
  getByActualPath,
} = require('./responsibility_test_plan');

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
  if (!fs.existsSync(filePath)) throw new Error(`${label} が見つかりません: ${filePath}`);
}

function assertPass(passed, label, detail=null) {
  console.log(`${label}: ${passed ? 'PASS' : 'FAIL'}`);
  if (!passed) throw new Error(detail ? `${label} failed: ${detail}` : `${label} failed`);
}

async function waitUntil(condition, timeoutMs=8000, intervalMs=100) {
  const started = Date.now();
  while (Date.now() - started < timeoutMs) {
    try {
      if (await condition()) return true;
    } catch (err) {
      if (!(err instanceof error.StaleElementReferenceError)
        && !(err instanceof error.NoSuchElementError)) throw err;
    }
    await sleep(intervalMs);
  }
  return false;
}

async function createDriver() {
  assertFileExists(NATIVE_SHELL, 'NativeShell');
  const options = new edge.Options().useWebView(true).setEdgeChromiumBinaryPath(NATIVE_SHELL);
  const driverPath = findExistingEdgeDriver();
  let builder = new Builder().forBrowser(Browser.EDGE).setEdgeOptions(options);
  if (driverPath) {
    console.log(`EdgeDriver: ${driverPath}`);
    builder = builder.setEdgeService(new edge.ServiceBuilder(driverPath));
  } else {
    console.log('EdgeDriver: ローカル配置なし（Selenium Manager / PATH に委譲）');
  }
  console.log(`NativeShell: ${NATIVE_SHELL}`);
  return builder.build();
}

function normalizeLineEndings(value) {
  return String(value ?? '').replace(/\r\n/g, '\n').replace(/\r/g, '\n');
}

function normalizeUiValue(value) {
  if (typeof value === 'boolean') return value ? 'true' : 'false';
  if (value === null || value === undefined) return '';
  return normalizeLineEndings(String(value));
}

async function readControlValue(control) {
  const propertyValue = await control.getProperty('value');
  if (propertyValue !== null && propertyValue !== undefined) return String(propertyValue);
  const attributeValue = await control.getAttribute('value');
  if (attributeValue !== null && attributeValue !== undefined) return String(attributeValue);
  return control.getText();
}

async function isDetailDialogOpen(driver) {
  const dialog = await driver.findElement(By.id('detailDialog'));
  return Boolean(await dialog.getProperty('open'));
}

async function closeDetailDialog(driver) {
  if (!(await isDetailDialogOpen(driver))) return;
  const dialog = await driver.findElement(By.id('detailDialog'));
  const closeButton = await dialog.findElement(By.css("button[value='cancel']"));
  await closeButton.click();
  const closed = await waitUntil(async () => !(await isDetailDialogOpen(driver)));
  assertPass(closed, 'Detail close');
}

async function waitForGridStable(driver, minimumRows=1, stablePolls=3, timeoutMs=12000) {
  let previousSignature = null;
  let stableCount = 0;
  const stable = await waitUntil(async () => {
    const rows = await driver.findElements(By.css('#dataGrid tbody tr'));
    if (rows.length < minimumRows) {
      previousSignature = null;
      stableCount = 0;
      return false;
    }

    const signatureParts = [];
    for (const row of rows) {
      signatureParts.push(await row.getText());
    }
    const signature = `${rows.length}|${signatureParts.join('\u241e')}`;
    if (signature === previousSignature) {
      stableCount += 1;
    } else {
      previousSignature = signature;
      stableCount = 1;
    }
    return stableCount >= stablePolls;
  }, timeoutMs, 120);

  assertPass(stable, `Grid stable (${minimumRows}+)`);
}

async function openGridRow(driver, rowIndex, maxAttempts=4) {
  await closeDetailDialog(driver).catch(() => {});
  await waitForGridStable(driver, rowIndex + 1);

  let lastError = null;
  for (let attempt = 1; attempt <= maxAttempts; attempt += 1) {
    try {
      // Re-acquire the row on every attempt. Reload/redraw may replace the entire tbody.
      const rows = await driver.findElements(By.css('#dataGrid tbody tr'));
      if (rows.length <= rowIndex) {
        throw new Error(`Grid row is missing: index=${rowIndex}, rows=${rows.length}`);
      }
      const row = rows[rowIndex];
      await driver.executeScript('arguments[0].scrollIntoView({block: "center", inline: "nearest"});', row);
      await driver.actions().doubleClick(row).perform();
      const opened = await waitUntil(() => isDetailDialogOpen(driver), 5000, 100);
      if (opened) {
        assertPass(true, `Row Detail open [${rowIndex}]`);
        return;
      }
      lastError = new Error(`Detail dialog did not open: row=${rowIndex}, attempt=${attempt}`);
    } catch (err) {
      lastError = err;
      const retryable = err instanceof error.StaleElementReferenceError
        || err instanceof error.NoSuchElementError;
      if (!retryable) throw err;
    }

    await sleep(150);
    await waitForGridStable(driver, rowIndex + 1);
  }

  throw lastError ?? new Error(`Row Detail open failed: row=${rowIndex}`);
}

async function findDetailControl(driver, fieldName) {
  const dialog = await driver.findElement(By.id('detailDialog'));
  return dialog.findElement(By.css(`#detailForm [data-field="${fieldName}"]`));
}

async function setControlValue(driver, control, value) {
  await driver.executeScript((element, nextValue) => {
    const normalized = nextValue === null || nextValue === undefined ? '' : String(nextValue);
    if (element.tagName === 'SELECT') {
      element.value = normalized;
    } else if (element.type === 'checkbox') {
      element.checked = normalized === 'true';
    } else {
      element.value = normalized;
    }
    element.dispatchEvent(new Event('input', { bubbles: true }));
    element.dispatchEvent(new Event('change', { bubbles: true }));
  }, control, normalizeUiValue(value));
}

async function editDetailRow(driver, rowIndex, mutations, labelPrefix='Main') {
  await openGridRow(driver, rowIndex);
  const controls = [];
  for (const mutation of mutations) {
    const control = await findDetailControl(driver, mutation.field);
    const beforeUi = normalizeLineEndings(await readControlValue(control));
    assertPass(
      beforeUi === normalizeUiValue(mutation.before),
      `${labelPrefix} Before ${mutation.actual_path}`,
      `Expected=${normalizeUiValue(mutation.before)}, Actual=${beforeUi}`,
    );
    await setControlValue(driver, control, mutation.after);
    const draftUi = normalizeLineEndings(await readControlValue(control));
    assertPass(
      draftUi === normalizeUiValue(mutation.after),
      `${labelPrefix} Draft ${mutation.actual_path}`,
      `Expected=${normalizeUiValue(mutation.after)}, Actual=${draftUi}`,
    );
    controls.push(control);
  }

  if (!controls.length) throw new Error(`No mutations for row ${rowIndex}`);
  await controls.at(-1).sendKeys(Key.F12);
  const reflected = await waitUntil(async () => {
    for (const mutation of mutations) {
      const control = await findDetailControl(driver, mutation.field);
      const actual = normalizeLineEndings(await readControlValue(control));
      if (actual !== normalizeUiValue(mutation.after)) return false;
    }
    return true;
  });
  assertPass(reflected, `${labelPrefix} F12 apply [${rowIndex}]`);
  await closeDetailDialog(driver);
}

async function verifyDetailRow(driver, rowIndex, mutations, labelPrefix='Main') {
  await openGridRow(driver, rowIndex);
  for (const mutation of mutations) {
    const control = await findDetailControl(driver, mutation.field);
    const actual = normalizeLineEndings(await readControlValue(control));
    assertPass(
      actual === normalizeUiValue(mutation.after),
      `${labelPrefix} Reload ${mutation.actual_path}`,
      `Expected=${normalizeUiValue(mutation.after)}, Actual=${actual}`,
    );
  }
  await closeDetailDialog(driver);
}

function groupPlanRows(plan, mode) {
  const map = new Map();
  for (const pattern of plan.patterns ?? []) {
    if (pattern.ui_target?.mode !== mode) continue;
    const key = [pattern.target_data_path, pattern.row_index, pattern.ui_target?.related_grid_id ?? ''].join('|');
    if (!map.has(key)) {
      map.set(key, {
        target_data_path: pattern.target_data_path,
        row_index: pattern.row_index,
        ui_target: pattern.ui_target,
        mutations: [],
      });
    }
    const group = map.get(key);
    for (const mutation of pattern.mutations ?? []) {
      if (!group.mutations.some((item) => item.actual_path === mutation.actual_path)) group.mutations.push(mutation);
    }
  }
  return [...map.values()].sort((a, b) => a.row_index - b.row_index);
}

async function waitForMainGrid(driver, minimumRows=1) {
  const loaded = await waitUntil(async () => {
    const rows = await driver.findElements(By.css('#dataGrid tbody tr'));
    return rows.length >= minimumRows;
  }, 12000);
  assertPass(loaded, `Grid loaded (${minimumRows}+)`);
  await waitForGridStable(driver, minimumRows);
}

async function loadDataByName(driver, dataName) {
  const dataCombo = await driver.findElement(By.id('dataNameInput'));
  await dataCombo.click();
  await dataCombo.clear();
  await dataCombo.sendKeys(dataName);
  await sleep(300);
  await dataCombo.sendKeys(Key.ENTER);
  await sleep(300);
  const loadBtn = await driver.findElement(By.id('loadBtn'));
  assertPass(await loadBtn.isEnabled(), 'LOAD button enabled');
  await loadBtn.click();
  await waitForMainGrid(driver, 1);
}

async function saveOnce(driver) {
  const saveBtn = await driver.findElement(By.id('saveBtn'));
  assertPass(await saveBtn.isEnabled(), 'SAVE button enabled');
  await saveBtn.click();
  const saved = await waitUntil(async () => {
    const status = await driver.findElement(By.id('status')).getText();
    return status.includes('上書き保存しました');
  }, 10000);
  assertPass(saved, 'SAVE_ONCE');
}

async function reloadOnce(driver) {
  const loadBtn = await driver.findElement(By.id('loadBtn'));
  await loadBtn.click();
  await waitForMainGrid(driver, 1);
  assertPass(true, 'RELOAD_ONCE');
}

async function openRelatedGrid(driver, relatedGridId) {
  const button = await driver.findElement(By.css(`.related-grid-launch-button[data-related-grid-id="${relatedGridId}"]`));
  await button.click();
  const frameReady = await waitUntil(async () => {
    const frames = await driver.findElements(By.css('.related-grid-modal-frame'));
    return frames.length === 1;
  }, 10000);
  assertPass(frameReady, `Related Grid modal open: ${relatedGridId}`);
  const frame = await driver.findElement(By.css('.related-grid-modal-frame'));
  await driver.switchTo().frame(frame);
  await waitForMainGrid(driver, 1);
}

async function applyRelatedGridAndClose(driver, relatedGridId) {
  const applyButton = await driver.findElement(By.id('relatedGridApplyToParentBtn'));
  await applyButton.click();
  const applied = await waitUntil(async () => {
    const statuses = await driver.findElements(By.id('relatedGridShellStatus'));
    if (!statuses.length) return false;
    const text = await statuses[0].getText();
    return text.includes('反映しました');
  }, 10000);
  assertPass(applied, `Related Grid apply: ${relatedGridId}`);
  await driver.switchTo().defaultContent();
  const close = await driver.findElement(By.css('.related-grid-modal-close'));
  await close.click();
  const closed = await waitUntil(async () => (await driver.findElements(By.css('.related-grid-modal-frame'))).length === 0);
  assertPass(closed, `Related Grid close: ${relatedGridId}`);
}

async function closeRelatedGridWithoutApply(driver, relatedGridId) {
  await driver.switchTo().defaultContent();
  const close = await driver.findElement(By.css('.related-grid-modal-close'));
  await close.click();
  const closed = await waitUntil(async () => (await driver.findElements(By.css('.related-grid-modal-frame'))).length === 0);
  assertPass(closed, `Related Grid verify close: ${relatedGridId}`);
}

async function editRelatedGroups(driver, groups) {
  const byGrid = new Map();
  for (const group of groups) {
    const id = group.ui_target?.related_grid_id;
    if (!byGrid.has(id)) byGrid.set(id, []);
    byGrid.get(id).push(group);
  }
  for (const [relatedGridId, rows] of byGrid.entries()) {
    await openRelatedGrid(driver, relatedGridId);
    for (const group of rows) {
      await editDetailRow(driver, group.row_index, group.mutations, `Related:${relatedGridId}`);
    }
    await applyRelatedGridAndClose(driver, relatedGridId);
  }
}

async function verifyRelatedGroups(driver, groups) {
  const byGrid = new Map();
  for (const group of groups) {
    const id = group.ui_target?.related_grid_id;
    if (!byGrid.has(id)) byGrid.set(id, []);
    byGrid.get(id).push(group);
  }
  for (const [relatedGridId, rows] of byGrid.entries()) {
    await openRelatedGrid(driver, relatedGridId);
    for (const group of rows) {
      await verifyDetailRow(driver, group.row_index, group.mutations, `Related:${relatedGridId}`);
    }
    await closeRelatedGridWithoutApply(driver, relatedGridId);
  }
}


function arraysEqual(left=[], right=[]) {
  return left.length === right.length && left.every((value, index) => Object.is(value, right[index]));
}

async function waitForGridExactCount(driver, expectedCount, timeoutMs=10000) {
  const ready = await waitUntil(async () => {
    const rows = await driver.findElements(By.css('#dataGrid tbody tr'));
    return rows.length === expectedCount;
  }, timeoutMs, 100);
  const actualCount = (await driver.findElements(By.css('#dataGrid tbody tr'))).length;
  assertPass(ready && actualCount === expectedCount, `Grid result count = ${expectedCount}`, `Expected=${expectedCount}, Actual=${actualCount}`);
  await waitForGridStable(driver, expectedCount, 3, timeoutMs);
}

async function findStandardSearchField(driver, fieldName) {
  const selector = `.standard-search-field[data-search-field="${fieldName}"]`;
  const ready = await waitUntil(async () => (await driver.findElements(By.css(selector))).length === 1, 10000, 100);
  assertPass(ready, `Search Field ready: ${fieldName}`);
  return driver.findElement(By.css(selector));
}

async function selectSearchOperator(driver, fieldName, operatorId) {
  let wrap = await findStandardSearchField(driver, fieldName);
  await driver.executeScript('arguments[0].scrollIntoView({block: "center", inline: "nearest"});', wrap);
  await driver.actions().contextClick(wrap).perform();
  const selector = `.standard-search-context-menu button[data-search-operator-id="${operatorId}"]`;
  const menuReady = await waitUntil(async () => (await driver.findElements(By.css(selector))).length === 1, 5000, 80);
  assertPass(menuReady, `Search Operator menu: ${fieldName} / ${operatorId}`);
  const button = await driver.findElement(By.css(selector));
  await button.click();
  const applied = await waitUntil(async () => {
    wrap = await findStandardSearchField(driver, fieldName);
    const controls = await wrap.findElements(By.css('[data-search-operator]'));
    if (!controls.length) return false;
    return (await controls[0].getAttribute('data-search-operator')) === operatorId;
  }, 5000, 80);
  assertPass(applied, `Search Operator apply: ${fieldName} / ${operatorId}`);
  return wrap;
}

async function setSearchCriteria(driver, generatedCase) {
  const fieldName = String(generatedCase?.target_field ?? '');
  const operatorId = String(generatedCase?.operator_id ?? generatedCase?.criteria?.operator ?? '');
  const criteria = generatedCase?.criteria ?? {};
  const wrap = await selectSearchOperator(driver, fieldName, operatorId);

  const setRole = async (role, value) => {
    const controls = await wrap.findElements(By.css(`[data-search-role="${role}"]`));
    if (controls.length !== 1) throw new Error(`Search criteria control not found: field=${fieldName}, operator=${operatorId}, role=${role}, count=${controls.length}`);
    await setControlValue(driver, controls[0], value);
    const actual = normalizeLineEndings(await readControlValue(controls[0]));
    assertPass(actual === normalizeUiValue(value), `Search Criteria ${fieldName}.${role}`, `Expected=${normalizeUiValue(value)}, Actual=${actual}`);
  };

  if (operatorId === 'between') {
    await setRole('from', criteria.from ?? '');
    await setRole('to', criteria.to ?? '');
  } else if (!['blank', 'not_blank'].includes(operatorId)) {
    await setRole('value', criteria.value ?? '');
  }
}

async function readSearchGridResult(driver) {
  const rows = await driver.findElements(By.css('#dataGrid tbody tr'));
  const indexes = [];
  const rowIds = [];
  for (const row of rows) {
    const sourceIndex = await row.getAttribute('data-source-index');
    const rowKey = await row.getAttribute('data-row-key');
    indexes.push(Number(sourceIndex));
    rowIds.push(String(rowKey ?? ''));
  }
  return { indexes, row_ids: rowIds, match_count: rows.length };
}

async function resetSearchAfterCase(driver, baselineCount) {
  const button = await driver.findElement(By.id('clearSearchBtn'));
  await button.click();
  await waitForGridExactCount(driver, baselineCount);
  assertPass(true, 'RESET_AFTER_EACH');
}

async function executeSearchCase(driver, generatedCase) {
  if (generatedCase?.ui_target?.mode !== 'MAIN_GRID') {
    throw new Error(`Search Selenium currently supports MAIN_GRID only: ${generatedCase?.case_id ?? ''} / ${generatedCase?.ui_target?.mode ?? ''}`);
  }
  console.log(`Search Case: ${generatedCase.pattern_id} / ${generatedCase.case_id}`);
  await setSearchCriteria(driver, generatedCase);
  const searchButton = await driver.findElement(By.id('searchBtn'));
  await searchButton.click();
  const expected = generatedCase?.expected ?? { row_ids: [], indexes: [], match_count: 0 };
  await waitForGridExactCount(driver, Number(expected.match_count ?? 0));
  const actual = await readSearchGridResult(driver);
  assertPass(actual.match_count === expected.match_count, 'StateExpectedDef / Match Count', `Expected=${expected.match_count}, Actual=${actual.match_count}`);
  assertPass(arraysEqual(actual.indexes, expected.indexes ?? []), 'StateExpectedDef / Indexes', `Expected=${JSON.stringify(expected.indexes)}, Actual=${JSON.stringify(actual.indexes)}`);
  assertPass(arraysEqual(actual.row_ids, expected.row_ids ?? []), 'StateExpectedDef / Row IDs', `Expected=${JSON.stringify(expected.row_ids)}, Actual=${JSON.stringify(actual.row_ids)}`);
}

async function runSearchResponsibilitySelenium(plan) {
  assertExecutionApproved(plan);
  const unsupported = (plan.search_cases ?? []).filter(item => item.ui_target?.mode !== 'MAIN_GRID');
  if (unsupported.length) throw new Error(`Unsupported Search UI targets: ${unsupported.map(item => `${item.case_id}:${item.ui_target?.mode}`).join(', ')}`);
  if (!(plan.search_cases ?? []).length) throw new Error('No Generated Search Cases.');

  let driver = null;
  try {
    driver = await createDriver();
    await sleep(2500);
    await loadDataByName(driver, plan.setup.input_file.replace(/^data\/json\//, ''));
    const baselineCount = Number(plan.search_cases[0]?.input_snapshot?.length ?? 0);
    await waitForGridExactCount(driver, baselineCount);

    for (const generatedCase of plan.search_cases) {
      await executeSearchCase(driver, generatedCase);
      await resetSearchAfterCase(driver, baselineCount);
    }

    console.log(`Responsibility E2E: ${plan.responsibility_cd} ALL PASS`);
    return { plan, executed: true };
  } finally {
    if (driver) await driver.quit().catch(() => {});
  }
}

async function loadExpectedCompareStrategies() {
  const modulePath = path.resolve(
    APP_ROOT,
    'tests/responsibilities/lib/responsibility_expected_compare_strategies.mjs',
  );
  assertFileExists(modulePath, 'ExpectedDef CompareStrategy');
  return import(pathToFileURL(modulePath).href);
}

function parseAggregateDisplayValue(text) {
  const normalized = String(text ?? '').trim().replace(/,/g, '');
  if (!normalized) return null;
  const value = Number(normalized);
  return Number.isFinite(value) ? value : normalized;
}

async function applyAggregateUiFilter(driver, filterPlan) {
  if (!filterPlan?.required) {
    console.log('Aggregate UI Filter: NONE');
    return;
  }
  const generatedCase = {
    target_field: filterPlan.field,
    operator_id: filterPlan.operator_id,
    criteria: filterPlan.criteria ?? {},
  };
  console.log(`Aggregate UI Filter: ${filterPlan.field} / ${filterPlan.operator_id} / ${JSON.stringify(filterPlan.criteria ?? {})}`);
  await setSearchCriteria(driver, generatedCase);
  const searchButton = await driver.findElement(By.id('searchBtn'));
  await searchButton.click();
  await waitForGridExactCount(driver, Number(filterPlan.expected_count ?? 0));
  const actualRows = await readSearchGridResult(driver);
  assertPass(
    arraysEqual(actualRows.indexes, filterPlan.expected_indexes ?? []),
    'Aggregate Precondition / Filtered Indexes',
    `Expected=${JSON.stringify(filterPlan.expected_indexes ?? [])}, Actual=${JSON.stringify(actualRows.indexes)}`,
  );
}

async function readAggregateMetricFromUi(driver, generatedCase) {
  const fieldName = String(generatedCase?.target_field ?? '');
  const metric = String(generatedCase?.metric ?? '');
  const selector = `.grid-aggregate-cell[data-aggregate-field="${fieldName}"]`;
  const cells = await driver.findElements(By.css(selector));

  if (metric === 'has_aggregates') return cells.length > 0;
  if (cells.length !== 1) {
    throw new Error(`Aggregate UI cell not found: field=${fieldName}, metric=${metric}, count=${cells.length}`);
  }

  const cell = cells[0];
  if (metric === 'value') {
    const valueElement = await cell.findElement(By.css('.grid-aggregate-value'));
    return parseAggregateDisplayValue(await valueElement.getText());
  }
  if (metric === 'source_count') return Number(await cell.getAttribute('data-aggregate-source-count'));
  if (metric === 'valid_count') return Number(await cell.getAttribute('data-aggregate-valid-count'));
  if (metric === 'ignored_count') return Number(await cell.getAttribute('data-aggregate-ignored-count'));
  throw new Error(`Unsupported aggregate UI metric: ${metric}`);
}

async function compareAggregateCaseFromUi({ driver, generatedCase, buildExpectedChecks }) {
  const expectedDef = String(generatedCase?.expected_def_type ?? '');
  if (expectedDef !== 'ScalarExpectedDef') {
    throw new Error(`GRID_AGGREGATE UI requires ScalarExpectedDef: ${generatedCase?.case_id ?? ''} / ${expectedDef}`);
  }
  const actualValue = await readAggregateMetricFromUi(driver, generatedCase);
  const comparePattern = {
    test_pattern_id: generatedCase.case_id,
    expected_def_type: expectedDef,
    expected: generatedCase.expected,
  };
  const checks = buildExpectedChecks(comparePattern, { value: actualValue });
  if (checks.length !== 1) throw new Error(`ScalarExpectedDef must produce one check: ${generatedCase.case_id}`);
  const check = checks[0];
  const label = `${expectedDef} / Grid Header ${generatedCase.target_field}.${generatedCase.metric}`;
  assertPass(
    check.pass === true,
    label,
    `${check.message}; Expected=${JSON.stringify(check.expected)}, Actual=${JSON.stringify(check.actual)}`,
  );
}

async function runAggregateResponsibilitySelenium(plan) {
  assertExecutionApproved(plan);
  if (!(plan.aggregate_cases ?? []).length) throw new Error('No Generated Aggregate Cases.');
  const unsupported = (plan.patterns ?? []).filter(pattern => pattern.ui_target?.mode !== 'MAIN_GRID');
  if (unsupported.length) {
    throw new Error(`Aggregate Selenium currently supports MAIN_GRID only: ${unsupported.map(item => `${item.pattern_id}:${item.ui_target?.mode}`).join(', ')}`);
  }

  let driver = null;
  try {
    driver = await createDriver();
    await sleep(2500);
    await loadDataByName(driver, plan.setup.input_file.replace(/^data\/json\//, ''));

    const targetPath = String(plan.patterns?.[0]?.target_data_path ?? '');
    const rows = getByActualPath(plan.baseline_document, targetPath);
    const baselineCount = Array.isArray(rows) ? rows.length : 0;
    await waitForGridExactCount(driver, baselineCount);

    await applyAggregateUiFilter(driver, plan.aggregate_ui_filter);
    const { buildExpectedChecks } = await loadExpectedCompareStrategies();

    for (const pattern of plan.patterns ?? []) {
      console.log(`Aggregate Pattern: ${pattern.pattern_id} / field=${pattern.target_field} / scope=${pattern.aggregate_scope || 'none'}`);
      for (const generatedCase of pattern.generated_cases ?? []) {
        await compareAggregateCaseFromUi({ driver, generatedCase, buildExpectedChecks });
      }
    }

    console.log(`Responsibility E2E: ${plan.responsibility_cd} ALL PASS`);
    return { plan, executed: true };
  } finally {
    if (driver) await driver.quit().catch(() => {});
  }
}

function createWorkingCopy(plan) {
  const sourcePath = path.resolve(APP_ROOT, plan.setup.input_file);
  assertFileExists(sourcePath, 'Approved Test Input JSON');
  const relativeDir = plan.setup.working_copy_directory || 'data/json/99_test_runtime';
  const workingDir = path.resolve(APP_ROOT, relativeDir);
  fs.mkdirSync(workingDir, { recursive: true });
  const fileName = `__selenium_${plan.responsibility_cd}_${Date.now()}.json`;
  const workingPath = path.join(workingDir, fileName);
  fs.copyFileSync(sourcePath, workingPath);

  const dataRoot = path.resolve(APP_ROOT, 'data/json');
  const dataName = path.relative(dataRoot, workingPath).replace(/\\/g, '/');
  if (dataName.startsWith('..')) throw new Error(`Working copy must be under data/json: ${workingPath}`);
  return { workingPath, dataName };
}

function verifyPhysicalJson(plan, workingPath) {
  const actual = JSON.parse(fs.readFileSync(workingPath, 'utf8'));
  const unexpected = diffJson(plan.expected.document, actual);
  assertPass(
    unexpected.length === plan.expected.unexpected_diff_count,
    'JsonDiffExpectedDef / Unexpected Diff Count',
    unexpected.slice(0, 10).map((item) => `${item.path}: expected=${JSON.stringify(item.expected)} actual=${JSON.stringify(item.actual)}`).join('\n'),
  );

  const actualChanges = diffJson(plan.baseline_document, actual);
  const expectedPaths = new Set(plan.mutations.map((item) => item.actual_path));
  const actualPaths = new Set(actualChanges.map((item) => item.path));
  const missing = [...expectedPaths].filter((item) => !actualPaths.has(item));
  const extra = [...actualPaths].filter((item) => !expectedPaths.has(item));
  assertPass(missing.length === 0 && extra.length === 0, 'JsonDiffExpectedDef / Expected Diff Paths', `Missing=${missing.join(', ')} Extra=${extra.join(', ')}`);
  assertPass(actualChanges.length === plan.mutations.length, 'JsonDiffExpectedDef / Expected Diff Count', `Expected=${plan.mutations.length}, Actual=${actualChanges.length}`);
}

async function runResponsibilitySelenium({ responsibilityCd='data_update_persist', planOnly=false }={}) {
  const plan = buildResponsibilityExecutionPlan({ responsibilityCd });
  console.log(formatPlanSummary(plan));
  if (planOnly) return { plan, executed: false };

  // Aggregate responsibility observes the externally visible Grid Header through NativeShell/Selenium.
  if (plan.execution_kind === 'GRID_AGGREGATE') return runAggregateResponsibilitySelenium(plan);

  // Search responsibility has a different lifecycle: LOAD_ONCE -> SEARCH/VERIFY -> RESET_AFTER_EACH.
  if (plan.execution_kind === 'SEARCH_FILTER') return runSearchResponsibilitySelenium(plan);

  // Human approval is a hard execution gate. No NativeShell launch before this check.
  assertExecutionApproved(plan);

  let working = null;
  let driver = null;
  let executionCompleted = false;
  try {
    working = createWorkingCopy(plan);
    console.log(`Working Copy: ${working.workingPath}`);
    driver = await createDriver();
    await sleep(2500);
    await loadDataByName(driver, working.dataName);

    const mainGroups = groupPlanRows(plan, 'MAIN_GRID');
    const relatedGroups = groupPlanRows(plan, 'RELATED_GRID');
    const unsupported = (plan.patterns ?? []).filter((item) => !['MAIN_GRID', 'RELATED_GRID'].includes(item.ui_target?.mode));
    if (unsupported.length) throw new Error(`Unsupported UI targets: ${unsupported.map((item) => `${item.pattern_id}:${item.ui_target?.mode}`).join(', ')}`);

    for (const group of mainGroups) {
      await editDetailRow(driver, group.row_index, group.mutations, 'Main');
    }
    await editRelatedGroups(driver, relatedGroups);

    await saveOnce(driver);
    await reloadOnce(driver);

    for (const group of mainGroups) {
      await verifyDetailRow(driver, group.row_index, group.mutations, 'Main');
    }
    await verifyRelatedGroups(driver, relatedGroups);

    verifyPhysicalJson(plan, working.workingPath);
    executionCompleted = true;
    console.log(`Responsibility E2E: ${responsibilityCd} ALL PASS`);
    return { plan, executed: true, workingPath: working.workingPath };
  } finally {
    if (driver) await driver.quit().catch(() => {});
    if (working && plan.setup.cleanup_policy === 'DELETE_AFTER_EXECUTION') {
      if (!executionCompleted) {
        console.warn(`Working Copy preserved for failure analysis: ${working.workingPath}`);
      } else {
        try {
          fs.unlinkSync(working.workingPath);
          console.log(`Working Copy deleted: ${working.workingPath}`);
        } catch (err) {
          console.warn(`Working Copy cleanup failed: ${err.message}`);
        }
      }
    }
  }
}

module.exports = {
  runResponsibilitySelenium,
  groupPlanRows,
  normalizeUiValue,
  waitForGridStable,
  openGridRow,
  arraysEqual,
  readSearchGridResult,
  parseAggregateDisplayValue,
  readAggregateMetricFromUi,
  runAggregateResponsibilitySelenium,
};
