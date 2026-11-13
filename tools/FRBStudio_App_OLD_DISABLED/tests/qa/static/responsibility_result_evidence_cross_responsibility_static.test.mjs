import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { createRequire } from 'node:module';

const ROOT = process.cwd();
const require = createRequire(import.meta.url);
const evidence = require(path.join(ROOT, 'SeleniumTaste/responsibility_evidence.js'));

function makeDiff(plan, check) {
  const observation = {
    guarantee_id: check.guarantee_id,
    responsibility_cd: plan.responsibility_cd,
    test_pattern_id: check.test_pattern_id,
    case_id: check.case_id,
    metric: check.metric,
    actual: check.actual_raw,
    actual_display: String(check.actual ?? ''),
    observed_at: '2026-08-30_13:00:00',
    source: 'synthetic observation',
  };
  return evidence.buildDiffDocument({
    plan,
    checks: [check],
    observations: [observation],
    observedAt: '2026-08-30_13:00:00',
    runId: `${plan.responsibility_cd}_20260830_130000`,
    sourceRunner: 'runner.js',
    actualFile: `data/json/03_tests/responsibilities/results/${plan.responsibility_cd}.actual.json`,
    diffFile: `data/json/03_tests/responsibilities/results/${plan.responsibility_cd}.diff.json`,
  });
}

test('Diff TestPattern summary persists planned_pattern for Search/CSV/Data Update rendering', () => {
  const plans = [
    {
      responsibility_cd: 'search_filter', responsibility_name: 'search', responsibility_document: 'r.json', guarantee_ids: ['g1'], setup: { input_file: 'i.json' },
      patterns: [{ pattern_id: 'search_p1', generation_mode: 'SEARCH_OPERATOR_MATRIX', generated_cases: [{ case_id: 'search_c1', input_snapshot: [], criteria: { value: 'Alpha' }, expected: { match_count: 1, row_ids: ['a'], indexes: [0] } }] }],
    },
    {
      responsibility_cd: 'csv_export', responsibility_name: 'csv', responsibility_document: 'r.json', guarantee_ids: ['g1'], setup: { input_file: 'i.json' },
      patterns: [{ pattern_id: 'csv_p1', generation_mode: 'CSV_EXPORT_CASE', generated_cases: [{ case_id: 'csv_c1', input_snapshot: [], expected: { field_names: ['id'], has_bom: true, csv_text: 'x', csv_without_bom: 'x' } }] }],
    },
    {
      responsibility_cd: 'data_update_persist', responsibility_name: 'persist', responsibility_document: 'r.json', guarantee_ids: ['g1'], setup: { input_file: 'i.json' },
      patterns: [{ pattern_id: 'persist_p1', pattern_cd: 'DATA_UPDATE_PERSIST', mutations: [{ field: 'name', before: 'AAA', after: 'BBB', actual_path: '$.rows[0].name' }] }],
    },
  ];

  for (const plan of plans) {
    const patternId = plan.patterns[0].pattern_id;
    const check = {
      check_id: `${patternId}.value`, guarantee_id: 'g1', responsibility_cd: plan.responsibility_cd,
      test_pattern_id: patternId, case_id: `${patternId}_case`, metric: 'value', expected: '1', actual: '1', expected_raw: 1, actual_raw: 1, pass: true, message: 'OK',
    };
    const diff = makeDiff(plan, check);
    assert.deepEqual(diff.test_pattern_results[0].planned_pattern, plan.patterns[0]);
  }
});

test('Result Evidence component has fact-detail renderers for all runnable responsibilities', () => {
  const source = fs.readFileSync(path.join(ROOT, 'wwwroot/js/components/responsibility/responsibility_diff_result_preview_component.js'), 'utf8');
  assert.match(source, /renderAggregateFactSections/);
  assert.match(source, /renderCsvFactSections/);
  assert.match(source, /renderSearchFactSections/);
  assert.match(source, /renderDataUpdatePersistFactSections/);
  assert.match(source, /① 対象値の入力状況/);
  assert.match(source, /② 集計へ投入/);
  assert.match(source, /② 検索へ投入/);
  assert.match(source, /② CSV出力へ投入/);
  assert.match(source, /② 操作へ投入/);
  assert.match(source, /③ Expected Result/);
  assert.match(source, /④ Actual/);
  assert.match(source, /⑤ Diff/);
});

test('Search/CSV/Data Update runners persist Actual/Diff evidence before final responsibility diff failure', () => {
  const source = fs.readFileSync(path.join(ROOT, 'SeleniumTaste/responsibility_selenium_runner.js'), 'utf8');
  for (const label of ['SEARCH_FILTER diff failed', 'CSV_EXPORT diff failed', 'DATA_UPDATE_PERSIST diff failed']) {
    const failIndex = source.indexOf(label);
    assert.ok(failIndex > 0, `${label} exists`);
    const writeIndex = source.lastIndexOf('writeResponsibilityEvidence({', failIndex);
    assert.ok(writeIndex >= 0 && writeIndex < failIndex, `${label} is after evidence write`);
  }
  assert.match(source, /searchCaseEvidence/);
  assert.match(source, /csvPatternEvidence/);
  assert.match(source, /dataUpdatePhysicalEvidence/);
});

test('DATA_UPDATE_PERSIST batch integrity does not count sibling TestPattern mutations as unexpected', () => {
  const source = fs.readFileSync(path.join(ROOT, 'SeleniumTaste/responsibility_selenium_runner.js'), 'utf8');
  assert.match(source, /LOAD_ONCE -> SAVE_ONCE -> RELOAD_ONCE/);
  assert.match(source, /!allExpectedPaths\.has\(actualPath\)/);
  assert.doesNotMatch(source, /!patternPaths\.has\(String\(item\?\.path/);
});
