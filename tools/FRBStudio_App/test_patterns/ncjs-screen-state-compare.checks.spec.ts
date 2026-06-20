import { test, expect } from '@playwright/test';
import fs from 'fs';
import path from 'path';

const BASE_URL = 'http://localhost:5055/';
const TEST_ID = 'screen_state_smoke_001';
const DIFF_VIEW_DEF = 'screen_state_diff_view_def_v0_2_checks.json';

type ScreenState = {
  appTitle: string;
  url: string;
  headerText: boolean;
  buttons: string[];
  selects: Array<{ id: string; value: string; optionCount: number }>;
  inputs: Array<{ id: string; type: string; value: string }>;
};

type CheckType = 'equals' | 'includesAll' | 'contains' | 'exists';

type CheckPattern = {
  check_id?: string;
  name: string;
  type: CheckType;
  target: string;
  expected?: unknown;
  description?: string;
};

type ExpectedPattern = {
  testId: string;
  title: string;
  view_def?: string;
  checks: CheckPattern[];
};

type DiffCheck = {
  check_id: string;
  name: string;
  type: CheckType;
  target: string;
  expected: string;
  actual: string;
  missing: string[];
  pass: boolean;
  message: string;
};

function readExpectedPattern(): ExpectedPattern {
  const patternPath = path.join(
    process.cwd(),
    'test_patterns',
    `${TEST_ID}.expected.json`
  );

  return JSON.parse(fs.readFileSync(patternPath, 'utf8')) as ExpectedPattern;
}

function getByDotPath(obj: unknown, dotPath: string): unknown {
  if (!dotPath || dotPath === '$') return obj;

  const normalized = dotPath.startsWith('$.') ? dotPath.slice(2) : dotPath;
  const parts = normalized.split('.').filter(Boolean);

  let current: unknown = obj;
  for (const part of parts) {
    if (Array.isArray(current)) {
      current = current.map(item => {
        if (item == null || typeof item !== 'object') return undefined;
        return (item as Record<string, unknown>)[part];
      }).filter(value => value !== undefined);
      continue;
    }

    if (current == null || typeof current !== 'object') return undefined;
    current = (current as Record<string, unknown>)[part];
  }

  return current;
}

function toStringArray(value: unknown): string[] {
  if (Array.isArray(value)) return value.map(v => String(v));
  if (value == null) return [];
  return [String(value)];
}

function normalizeForCompare(value: unknown): unknown {
  if (Array.isArray(value)) return value.map(normalizeForCompare);
  if (value && typeof value === 'object') {
    const sorted: Record<string, unknown> = {};
    Object.keys(value as Record<string, unknown>)
      .sort()
      .forEach(key => {
        sorted[key] = normalizeForCompare((value as Record<string, unknown>)[key]);
      });
    return sorted;
  }
  return value;
}

function deepEqual(a: unknown, b: unknown): boolean {
  return JSON.stringify(normalizeForCompare(a)) === JSON.stringify(normalizeForCompare(b));
}

function displayValue(value: unknown): string {
  if (value == null) return '';
  if (typeof value === 'string') return value;
  return JSON.stringify(value);
}


function parseMaybeJson(value: unknown): unknown {
  if (typeof value !== 'string') return value;

  const text = value.trim();
  if (!text) return value;

  // No-Code JSON Studioのtextarea編集後は、配列・boolean・numberが文字列化されることがある。
  // JSONとして読めるものだけ元の型へ戻す。
  if (
    text === 'true' ||
    text === 'false' ||
    text === 'null' ||
    /^-?\d+(\.\d+)?$/.test(text) ||
    text.startsWith('[') ||
    text.startsWith('{') ||
    (text.startsWith('"') && text.endsWith('"'))
  ) {
    try {
      return JSON.parse(text);
    } catch {
      return value;
    }
  }

  return value;
}

function missingItems(required: string[], actual: string[]): string[] {
  return required.filter(item => !actual.includes(item));
}

function evaluateCheck(check: CheckPattern, state: ScreenState): DiffCheck {
  const actualValue = getByDotPath(state, check.target);
  const expectedValue = parseMaybeJson(check.expected);

  let pass = false;
  let missing: string[] = [];

  switch (check.type) {
    case 'equals':
      pass = deepEqual(actualValue, expectedValue);
      break;

    case 'includesAll': {
      const required = toStringArray(expectedValue);
      const actual = toStringArray(actualValue);
      missing = missingItems(required, actual);
      pass = missing.length === 0;
      break;
    }

    case 'contains': {
      const actualText = displayValue(actualValue);
      const required = toStringArray(expectedValue);
      missing = required.filter(item => !actualText.includes(item));
      pass = missing.length === 0;
      break;
    }

    case 'exists':
      pass = actualValue !== undefined && actualValue !== null && displayValue(actualValue) !== '';
      break;

    default:
      throw new Error(`未対応のcheck.typeです: ${(check as { type: string }).type}`);
  }

  return {
    check_id: check.check_id ?? check.name,
    name: check.name,
    type: check.type,
    target: check.target,
    expected: displayValue(expectedValue),
    actual: displayValue(actualValue),
    missing,
    pass,
    message: pass
      ? 'OK'
      : `${check.name} failed: expected ${displayValue(expectedValue)}, actual ${displayValue(actualValue)}`
  };
}

test('画面状態JSONをExpectedと比較してDiffを保存できる', async ({ page }, testInfo) => {
  await page.goto(BASE_URL);

  const state = await page.evaluate(() => {
    return (window as any).__NCJS_exportScreenState();
  }) as ScreenState;

  const pattern = readExpectedPattern();

  if (!Array.isArray(pattern.checks)) {
    throw new Error('expected.json の checks が Array ではありません');
  }

  const checks = pattern.checks.map(check => evaluateCheck(check, state));
  const failedChecks = checks.filter(check => !check.pass);
  const status = failedChecks.length === 0 ? 'pass' : 'fail';
  const firstFailure = failedChecks[0] ?? null;
  const capturedAt = new Date().toISOString();

  const emphasizedDiff = {
    view_def: DIFF_VIEW_DEF,
    testId: pattern.testId || TEST_ID,
    title: pattern.title,
    capturedAt,
    url: BASE_URL,
    status,
    checks,
    resultLabel: status === 'pass' ? '✅ PASS' : '🚨 FAIL',
    failedCount: failedChecks.length,
    failedChecks: failedChecks.map(check => check.name),
    failedCheckIds: failedChecks.map(check => check.check_id),
    summary: failedChecks.length === 0
      ? '✅ すべてのチェックに合格しました'
      : `🚨 ${failedChecks.length}件の差分を検出しました: ${failedChecks.map(check => check.name).join(', ')}`,
    firstFailure: firstFailure
      ? {
          check_id: firstFailure.check_id,
          name: firstFailure.name,
          type: firstFailure.type,
          target: firstFailure.target,
          expected: firstFailure.expected,
          actual: firstFailure.actual,
          missing: firstFailure.missing
        }
      : null,
    actualState: state
  };

  const resultRoot = path.join(process.cwd(), 'tests_screen_state', 'test_results');

  const actualDir = path.join(resultRoot, 'actual');
  const diffDir = path.join(resultRoot, 'diff');

  fs.mkdirSync(actualDir, { recursive: true });
  fs.mkdirSync(diffDir, { recursive: true });

  const actualPath = path.join(actualDir, `${TEST_ID}.actual.json`);
  const diffPath = path.join(diffDir, `${TEST_ID}.diff.json`);

  fs.writeFileSync(actualPath, JSON.stringify({
    testId: pattern.testId || TEST_ID,
    title: pattern.title,
    capturedAt,
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

//zzz

