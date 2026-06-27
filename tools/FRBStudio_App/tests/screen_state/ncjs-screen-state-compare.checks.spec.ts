import { test, expect } from '@playwright/test';
import fs from 'fs';
import path from 'path';

const BASE_URL = 'http://localhost:5055/';
const TEST_ID = 'screen_state_smoke_001';
const DIFF_VIEW_DEF = 'screen_state/screen_state_diff_view_def_base_v0_2_checks.json';
const SCREEN_STATE_TEST_ROOT = path.join('data', 'json', '03_tests', 'screen_state', TEST_ID);
const TEST_PATTERN_REGISTRY_FILE = path.join(
  SCREEN_STATE_TEST_ROOT,
  'test_patterns',
  'screen_state_test_patterns_data_v0_2_chat.json'
);

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

type ScreenStateTestPattern = {
  enabled?: boolean;
  patternId: string;
  title?: string;
  expectedFile?: string;
  outputActualFile?: string;
  outputDiffFile?: string;
  expectedViewDef?: string;
  diffViewDef?: string;
};

type ScreenStateTestPatternRegistry = {
  suiteId?: string;
  canonicalRoot?: string;
  patterns: ScreenStateTestPattern[];
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

function readJsonFile<T>(relativeFile: string): T {
  const filePath = path.join(process.cwd(), relativeFile);
  return JSON.parse(fs.readFileSync(filePath, 'utf8')) as T;
}

function readTestPatternRegistry(): ScreenStateTestPatternRegistry {
  return readJsonFile<ScreenStateTestPatternRegistry>(TEST_PATTERN_REGISTRY_FILE);
}

function findTestPattern(registry: ScreenStateTestPatternRegistry): ScreenStateTestPattern {
  if (!Array.isArray(registry.patterns)) {
    throw new Error(`test pattern registry の patterns が Array ではありません: ${TEST_PATTERN_REGISTRY_FILE}`);
  }

  const pattern = registry.patterns.find(item => item.patternId === TEST_ID);
  if (!pattern) {
    throw new Error(`test pattern registry に ${TEST_ID} が見つかりません: ${TEST_PATTERN_REGISTRY_FILE}`);
  }

  return pattern;
}

function requireRelativeFile(value: string | undefined, fieldName: string): string {
  if (!value || !value.trim()) {
    throw new Error(`${fieldName} が test pattern に定義されていません: ${TEST_PATTERN_REGISTRY_FILE}`);
  }
  return value;
}

function resolveProjectFile(relativeFile: string): string {
  return path.join(process.cwd(), relativeFile);
}

function readExpectedPattern(testPattern: ScreenStateTestPattern): ExpectedPattern {
  const expectedFile = requireRelativeFile(testPattern.expectedFile, 'expectedFile');
  return readJsonFile<ExpectedPattern>(expectedFile);
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

  const registry = readTestPatternRegistry();
  const testPattern = findTestPattern(registry);
  const pattern = readExpectedPattern(testPattern);

  if (!Array.isArray(pattern.checks)) {
    throw new Error('expected.json の checks が Array ではありません');
  }

  const checks = pattern.checks.map(check => evaluateCheck(check, state));
  const failedChecks = checks.filter(check => !check.pass);
  const status = failedChecks.length === 0 ? 'pass' : 'fail';
  const firstFailure = failedChecks[0] ?? null;
  const capturedAt = new Date().toISOString();

  const expectedFile = requireRelativeFile(testPattern.expectedFile, 'expectedFile');
  const outputActualFile = requireRelativeFile(testPattern.outputActualFile, 'outputActualFile');
  const outputDiffFile = requireRelativeFile(testPattern.outputDiffFile, 'outputDiffFile');

  const emphasizedDiff = {
    view_def: testPattern.diffViewDef || DIFF_VIEW_DEF,
    schema_version: 'screen_state_diff_v0_2',
    document_type: 'screen_state_diff',
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
    sourceFiles: {
      testPatternFile: TEST_PATTERN_REGISTRY_FILE,
      expectedFile,
      outputActualFile,
      outputDiffFile
    },
    actualState: state
  };

  const actualPath = resolveProjectFile(outputActualFile);
  const diffPath = resolveProjectFile(outputDiffFile);

  fs.mkdirSync(path.dirname(actualPath), { recursive: true });
  fs.mkdirSync(path.dirname(diffPath), { recursive: true });

  fs.writeFileSync(actualPath, JSON.stringify({
    view_def: pattern.view_def || testPattern.expectedViewDef || 'screen_state/screen_state_expected_view_def_v0_1.json',
    schema_version: 'screen_state_actual_v0_1',
    document_type: 'screen_state_actual',
    testId: pattern.testId || TEST_ID,
    title: pattern.title,
    capturedAt,
    sourceFiles: {
      testPatternFile: TEST_PATTERN_REGISTRY_FILE,
      expectedFile,
      outputActualFile,
      outputDiffFile
    },
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
