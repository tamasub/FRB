import { test, expect } from '@playwright/test';
import fs from 'fs';
import path from 'path';

const BASE_URL = 'http://localhost:5055/';
const TEST_ID = 'screen_state_smoke_001';
const DIFF_VIEW_DEF = 'screen_state_diff_view_def_v0_1.json';

type ScreenState = {
  appTitle: string;
  url: string;
  headerText: boolean;
  buttons: string[];
  selects: Array<{ id: string; value: string; optionCount: number }>;
  inputs: Array<{ id: string; type: string; value: string }>;
};

type ExpectedPattern = {
  testId: string;
  title: string;
  expected: {
    appTitle: string;
    headerText: boolean;
    requiredButtons: string[];
    requiredInputIds: string[];
  };
};

function missingItems(required: string[], actual: string[]): string[] {
  return required.filter(item => !actual.includes(item));
}

test('画面状態JSONをExpectedと比較してDiffを保存できる', async ({ page }, testInfo) => {
  await page.goto(BASE_URL);

  const state = await page.evaluate(() => {
    return (window as any).__NCJS_exportScreenState();
  }) as ScreenState;

  const patternPath = path.join(
    process.cwd(),
    'test_patterns',
    `${TEST_ID}.expected.json`
  );

  const pattern = JSON.parse(
    fs.readFileSync(patternPath, 'utf8')
  ) as ExpectedPattern;

  const actualButtonLabels = state.buttons ?? [];
  const actualInputIds = (state.inputs ?? []).map(input => input.id);

  const diff = {
    view_def: DIFF_VIEW_DEF,
    testId: TEST_ID,
    title: pattern.title,
    capturedAt: new Date().toISOString(),
    url: BASE_URL,
    status: 'pass',
    checks: [
      {
        name: 'appTitle',
        expected: pattern.expected.appTitle,
        actual: state.appTitle,
        pass: state.appTitle === pattern.expected.appTitle
      },
      {
        name: 'headerText',
        expected: pattern.expected.headerText,
        actual: state.headerText,
        pass: state.headerText === pattern.expected.headerText
      },
      {
        name: 'requiredButtons',
        expected: pattern.expected.requiredButtons,
        actual: actualButtonLabels,
        missing: missingItems(pattern.expected.requiredButtons, actualButtonLabels),
        pass: missingItems(pattern.expected.requiredButtons, actualButtonLabels).length === 0
      },
      {
        name: 'requiredInputIds',
        expected: pattern.expected.requiredInputIds,
        actual: actualInputIds,
        missing: missingItems(pattern.expected.requiredInputIds, actualInputIds),
        pass: missingItems(pattern.expected.requiredInputIds, actualInputIds).length === 0
      }
    ],
    actualState: state
  };

  const failedChecks = diff.checks.filter(check => !check.pass);
  diff.status = failedChecks.length === 0 ? 'pass' : 'fail';

  const firstFailure = failedChecks[0] ?? null;

  const emphasizedDiff = {
    ...diff,
    resultLabel: diff.status === 'pass' ? '✅ PASS' : '🚨 FAIL',
    failedCount: failedChecks.length,
    failedChecks: failedChecks.map(check => check.name),
    summary: failedChecks.length === 0
      ? '✅ すべてのチェックに合格しました'
      : `🚨 ${failedChecks.length}件の差分を検出しました: ${failedChecks.map(check => check.name).join(', ')}`,
    firstFailure: firstFailure
      ? {
          name: firstFailure.name,
          expected: firstFailure.expected,
          actual: firstFailure.actual,
          missing: 'missing' in firstFailure ? firstFailure.missing : undefined
        }
      : null
  };

  const resultRoot = path.join(process.cwd(), 'tests_screen_state', 'test_results');

  const actualDir = path.join(resultRoot, 'actual');
  const diffDir = path.join(resultRoot, 'diff');

  fs.mkdirSync(actualDir, { recursive: true });
  fs.mkdirSync(diffDir, { recursive: true });

  const actualPath = path.join(actualDir, `${TEST_ID}.actual.json`);
  const diffPath = path.join(diffDir, `${TEST_ID}.diff.json`);

  fs.writeFileSync(actualPath, JSON.stringify({
    view_def: DIFF_VIEW_DEF,
    testId: TEST_ID,
    capturedAt: new Date().toISOString(),
    state
  }, null, 2), 'utf8');

  fs.writeFileSync(diffPath, JSON.stringify(emphasizedDiff, null, 2), 'utf8');

  await testInfo.attach(`${TEST_ID}.actual.json`, {
    path: actualPath,
    contentType: 'application/json'
  });

  await testInfo.attach(`${TEST_ID}.diff.json`, {
    path: diffPath,
    contentType: 'application/json'
  });

  expect(emphasizedDiff.status).toBe('pass');

});
