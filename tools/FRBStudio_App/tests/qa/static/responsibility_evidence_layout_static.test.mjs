import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { createRequire } from 'node:module';

const ROOT = process.cwd();
const require = createRequire(import.meta.url);
const evidence = require(path.join(ROOT, 'SeleniumTaste/responsibility_evidence.js'));

function readJson(rel) {
  return JSON.parse(fs.readFileSync(path.join(ROOT, rel), 'utf8'));
}

const plan = {
  responsibility_cd: 'grid_aggregate',
  responsibility_name: 'Grid数値集計表示責務',
  responsibility_document: 'data/json/03_tests/responsibilities/responsibility_data_v0_2.json',
  guarantee_ids: ['grid_aggregate_g001', 'grid_aggregate_g002'],
  setup: { input_file: 'data/json/80_frb/frb_grid_aggregate_test_data_v0_1.json' },
};

const observations = [
  {
    guarantee_id: 'grid_aggregate_g001',
    responsibility_cd: 'grid_aggregate',
    test_pattern_id: 'pattern_a',
    case_id: 'case_a',
    actual: 146,
    actual_display: '146',
    observed_at: '2026-08-30_12:00:00',
    source: 'Grid Header profit.value',
  },
  {
    guarantee_id: 'grid_aggregate_g002',
    responsibility_cd: 'grid_aggregate',
    test_pattern_id: 'pattern_b',
    case_id: 'case_b',
    actual: 10,
    actual_display: '10',
    observed_at: '2026-08-30_12:00:00',
    source: 'Grid Header units.value',
  },
];

const checks = [
  { check_id: 'case_a.value', guarantee_id: 'grid_aggregate_g001', test_pattern_id: 'pattern_a', case_id: 'case_a', expected: '146', actual: '146', pass: true },
  { check_id: 'case_b.value', guarantee_id: 'grid_aggregate_g002', test_pattern_id: 'pattern_b', case_id: 'case_b', expected: '9', actual: '10', pass: false },
];

test('Responsibility evidence physical files are shallow and responsibility-scoped', () => {
  assert.deepEqual(evidence.evidencePaths('grid_aggregate'), {
    actual: 'data/json/03_tests/responsibilities/results/grid_aggregate.actual.json',
    diff: 'data/json/03_tests/responsibilities/results/grid_aggregate.diff.json',
  });
});

test('Actual evidence contains observations and guarantee IDs but no Expected/pass judgment', () => {
  const doc = evidence.buildActualDocument({
    plan,
    observations,
    observedAt: '2026-08-30_12:00:00',
    runId: 'grid_aggregate_20260830_120000',
    sourceRunner: 'runner.js',
  });
  assert.equal(doc.responsibility_cd, 'grid_aggregate');
  assert.equal(doc.observations[0].guarantee_id, 'grid_aggregate_g001');
  const raw = JSON.stringify(doc);
  assert.equal(raw.includes('"expected"'), false);
  assert.equal(raw.includes('"pass"'), false);
});

test('Diff evidence keeps flat checks, Guarantee grouping, and TestPattern summary projection', () => {
  const doc = evidence.buildDiffDocument({
    plan,
    checks,
    observations,
    observedAt: '2026-08-30_12:00:00',
    runId: 'grid_aggregate_20260830_120000',
    sourceRunner: 'runner.js',
    actualFile: 'data/json/03_tests/responsibilities/results/grid_aggregate.actual.json',
    diffFile: 'data/json/03_tests/responsibilities/results/grid_aggregate.diff.json',
  });
  assert.equal(doc.status, 'fail');
  assert.equal(doc.failedCount, 1);
  assert.deepEqual(doc.guarantee_results.map(item => item.guarantee_id), ['grid_aggregate_g001', 'grid_aggregate_g002']);
  assert.equal(doc.guarantee_results[0].status, 'pass');
  assert.equal(doc.guarantee_results[1].status, 'fail');
  assert.equal(doc.checks[1].guarantee_id, 'grid_aggregate_g002');

  assert.equal(doc.test_pattern_total, 2);
  assert.equal(doc.test_pattern_pass_count, 1);
  assert.equal(doc.test_pattern_fail_count, 1);
  assert.deepEqual(
    doc.test_pattern_results.map(item => ({
      pattern: item.test_pattern_id,
      cases: item.case_count,
      checks: item.check_count,
      diff: item.diff_count,
    })),
    [
      { pattern: 'pattern_a', cases: 1, checks: 1, diff: 0 },
      { pattern: 'pattern_b', cases: 1, checks: 1, diff: 1 },
    ],
  );
  assert.equal(doc.test_pattern_results[0].checks[0].source, 'Grid Header profit.value');
});

test('Test Evidence Rule 10 declares responsibility-file physical unit and Guarantee logical unit', () => {
  const rules = readJson('data/json/00_rules/frb_test_evidence_rules_data_v0_2.json');
  const rule = rules.rules.find(item => item.rule_id === 'test_evidence_rule_010');
  assert.match(rule.body, /Physical File = Responsibility単位/);
  assert.match(rule.body, /Logical Evidence = Guarantee ID単位/);
  assert.match(rule.body, /data\/json\/03_tests\/responsibilities/);
  assert.equal(rule.approval_decision, '未承認');
});

test('GRID_AGGREGATE Selenium runner writes Actual/Diff evidence before final fail assertion', () => {
  const source = fs.readFileSync(path.join(ROOT, 'SeleniumTaste/responsibility_selenium_runner.js'), 'utf8');
  const writeIndex = source.indexOf('writeResponsibilityEvidence({');
  const finalFailIndex = source.indexOf('GRID_AGGREGATE diff failed');
  assert.ok(writeIndex >= 0);
  assert.ok(finalFailIndex > writeIndex);
  assert.match(source, /guarantee_id: guaranteeId/);
});
