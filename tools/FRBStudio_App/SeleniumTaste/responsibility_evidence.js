'use strict';

const fs = require('node:fs');
const path = require('node:path');

const RESULTS_DIR = 'data/json/03_tests/responsibilities/results';

function pad(value, length=2) {
  return String(value).padStart(length, '0');
}

function studioDateTimeJst(date=new Date()) {
  const d = date instanceof Date ? date : new Date(date);
  const parts = new Intl.DateTimeFormat('en-CA', {
    timeZone: 'Asia/Tokyo',
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false,
  }).formatToParts(d).reduce((acc, part) => {
    if (part.type !== 'literal') acc[part.type] = part.value;
    return acc;
  }, {});
  return `${parts.year}-${parts.month}-${parts.day}_${parts.hour}:${parts.minute}:${parts.second}`;
}

function studioRunId(responsibilityCd, date=new Date()) {
  const d = date instanceof Date ? date : new Date(date);
  const parts = new Intl.DateTimeFormat('en-CA', {
    timeZone: 'Asia/Tokyo',
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false,
  }).formatToParts(d).reduce((acc, part) => {
    if (part.type !== 'literal') acc[part.type] = part.value;
    return acc;
  }, {});
  return `${responsibilityCd}_${parts.year}${parts.month}${parts.day}_${parts.hour}${parts.minute}${parts.second}`;
}

function normalizeResponsibilityCd(value) {
  const cd = String(value ?? '').trim();
  if (!/^[a-z0-9_]+$/i.test(cd)) throw new Error(`Invalid responsibility_cd for evidence path: ${cd}`);
  return cd;
}

function evidencePaths(responsibilityCd) {
  const cd = normalizeResponsibilityCd(responsibilityCd);
  return {
    actual: `${RESULTS_DIR}/${cd}.actual.json`,
    diff: `${RESULTS_DIR}/${cd}.diff.json`,
  };
}

function groupDiffByGuarantee(checks=[]) {
  const groups = new Map();
  for (const check of checks) {
    const guaranteeId = String(check?.guarantee_id ?? '').trim() || 'UNASSIGNED';
    if (!groups.has(guaranteeId)) groups.set(guaranteeId, []);
    groups.get(guaranteeId).push(check);
  }
  return [...groups.entries()].map(([guarantee_id, items]) => {
    const failed = items.filter(item => item?.pass !== true);
    return {
      guarantee_id,
      status: failed.length ? 'fail' : 'pass',
      total: items.length,
      passCount: items.length - failed.length,
      failCount: failed.length,
      failedCount: failed.length,
      check_ids: items.map(item => item?.check_id).filter(Boolean),
      failedCheckIds: failed.map(item => item?.check_id).filter(Boolean),
    };
  });
}

function groupDiffByTestPattern(checks=[], observations=[]) {
  const observationMap = new Map();
  for (const observation of observations ?? []) {
    const key = `${String(observation?.test_pattern_id ?? '')}\u0000${String(observation?.case_id ?? '')}\u0000${String(observation?.metric ?? '')}`;
    observationMap.set(key, observation);
  }

  const groups = new Map();
  for (const check of checks ?? []) {
    const patternId = String(check?.test_pattern_id ?? '').trim() || 'UNASSIGNED';
    if (!groups.has(patternId)) groups.set(patternId, []);
    groups.get(patternId).push(check);
  }

  return [...groups.entries()].map(([test_pattern_id, items]) => {
    const failed = items.filter(item => item?.pass !== true);
    const guaranteeIds = [...new Set(items.map(item => String(item?.guarantee_id ?? '').trim()).filter(Boolean))];
    const caseIds = [...new Set(items.map(item => String(item?.case_id ?? '').trim()).filter(Boolean))];
    const evidenceChecks = items.map(item => {
      const key = `${test_pattern_id}\u0000${String(item?.case_id ?? '')}\u0000${String(item?.metric ?? '')}`;
      const observation = observationMap.get(key) ?? null;
      return {
        ...item,
        observed_at: observation?.observed_at ?? '',
        source: observation?.source ?? '',
        actual_display: observation?.actual_display ?? '',
      };
    });

    return {
      result_label: failed.length ? 'FAIL' : 'PASS',
      pass: failed.length === 0,
      status: failed.length ? 'fail' : 'pass',
      guarantee_id: guaranteeIds.length === 1 ? guaranteeIds[0] : guaranteeIds.join(', '),
      guarantee_ids: guaranteeIds,
      test_pattern_id,
      case_count: caseIds.length,
      check_count: items.length,
      diff_count: failed.length,
      case_ids: caseIds,
      check_ids: items.map(item => item?.check_id).filter(Boolean),
      failed_check_ids: failed.map(item => item?.check_id).filter(Boolean),
      observed_at: evidenceChecks.map(item => item.observed_at).find(Boolean) ?? '',
      sources: [...new Set(evidenceChecks.map(item => item.source).filter(Boolean))],
      checks: evidenceChecks,
    };
  });
}

function buildActualDocument({ plan, observations=[], observedAt, runId, sourceRunner }) {
  const responsibilityCd = normalizeResponsibilityCd(plan?.responsibility_cd);
  return {
    view_def: 'qa/tests/responsibilities/responsibility_expected_actual_view_def_v0_1.json',
    schema_version: 'responsibility_actual_v0_2',
    document_type: 'responsibility_actual',
    test_area: 'responsibilities',
    artifact_kind: 'actual',
    responsibility_cd: responsibilityCd,
    responsibility_name: String(plan?.responsibility_name ?? ''),
    run_id: runId,
    observed_at: observedAt,
    guarantee_ids: Array.from(plan?.guarantee_ids ?? []),
    source_responsibility_file: String(plan?.responsibility_document ?? ''),
    source_input_file: String(plan?.setup?.input_file ?? ''),
    runner: sourceRunner,
    observations,
  };
}

function buildDiffDocument({ plan, checks=[], observations=[], observedAt, runId, sourceRunner, actualFile, diffFile }) {
  const responsibilityCd = normalizeResponsibilityCd(plan?.responsibility_cd);
  const failedChecks = checks.filter(check => check?.pass !== true);
  const firstFailure = failedChecks[0] ?? null;
  const status = failedChecks.length ? 'fail' : 'pass';
  const resultLabel = failedChecks.length ? '🚨 FAIL' : '✅ PASS';
  const guaranteeResults = groupDiffByGuarantee(checks);
  const testPatternResults = groupDiffByTestPattern(checks, observations);
  const failedTestPatterns = testPatternResults.filter(item => item?.pass !== true);
  return {
    view_def: 'qa/tests/responsibilities/responsibility_expected_diff_view_def_v0_1.json',
    schema_version: 'diff_result_v0_1',
    document_type: 'diff_result',
    domain: 'responsibilities',
    test_area: 'responsibilities',
    artifact_kind: 'diff',
    diff_kind: 'responsibility_expected',
    test_id: responsibilityCd,
    responsibility_cd: responsibilityCd,
    responsibility_name: String(plan?.responsibility_name ?? ''),
    run_id: runId,
    generated_at: observedAt,
    status,
    resultLabel,
    summary: failedChecks.length
      ? `🚨 TestPattern ${failedTestPatterns.length}/${testPatternResults.length}件で差分を検出 / Check ${failedChecks.length}/${checks.length}件FAIL`
      : `✅ TestPattern ${testPatternResults.length}件 / Check ${checks.length}件すべてPASSしました`,
    test_pattern_total: testPatternResults.length,
    test_pattern_pass_count: testPatternResults.length - failedTestPatterns.length,
    test_pattern_fail_count: failedTestPatterns.length,
    total: checks.length,
    passCount: checks.length - failedChecks.length,
    failCount: failedChecks.length,
    failedCount: failedChecks.length,
    failedCheckIds: failedChecks.map(check => check?.check_id).filter(Boolean),
    firstFailure,
    guarantee_results: guaranteeResults,
    test_pattern_results: testPatternResults.map(item => ({
      ...item,
      source_runner: sourceRunner,
      actual_file: actualFile,
      diff_file: diffFile,
    })),
    sourceFiles: {
      responsibilityFile: String(plan?.responsibility_document ?? ''),
      inputFile: String(plan?.setup?.input_file ?? ''),
      actualFile,
      diffFile,
      runner: sourceRunner,
    },
    checks,
  };
}

function writeJson(appRoot, relativePath, value) {
  const abs = path.resolve(appRoot, relativePath);
  fs.mkdirSync(path.dirname(abs), { recursive: true });
  fs.writeFileSync(abs, `${JSON.stringify(value, null, 2)}\n`, 'utf8');
}

function writeResponsibilityEvidence({ appRoot, plan, observations=[], checks=[], observedAt=null, runId=null, sourceRunner }) {
  const when = observedAt || studioDateTimeJst();
  const actualRunId = runId || studioRunId(plan?.responsibility_cd);
  const paths = evidencePaths(plan?.responsibility_cd);
  const actualDoc = buildActualDocument({ plan, observations, observedAt: when, runId: actualRunId, sourceRunner });
  const diffDoc = buildDiffDocument({
    plan,
    checks,
    observations,
    observedAt: when,
    runId: actualRunId,
    sourceRunner,
    actualFile: paths.actual,
    diffFile: paths.diff,
  });
  writeJson(appRoot, paths.actual, actualDoc);
  writeJson(appRoot, paths.diff, diffDoc);
  return { paths, actualDoc, diffDoc };
}

module.exports = {
  RESULTS_DIR,
  studioDateTimeJst,
  studioRunId,
  evidencePaths,
  groupDiffByGuarantee,
  groupDiffByTestPattern,
  buildActualDocument,
  buildDiffDocument,
  writeResponsibilityEvidence,
};
