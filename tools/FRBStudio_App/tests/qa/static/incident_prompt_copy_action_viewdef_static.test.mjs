import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const repoRoot = path.resolve(__dirname, "../../..");

const TEST_ID = "TP-IPC-001";
const EXPECTED_FILE = "data/json/03_tests/qa/v0_14_2_incident_prompt_copy_action/expected/qa_expected_checks_v0_14_2_incident_prompt_copy_action_expected_values_added.json";

const expectedPath = path.join(repoRoot, EXPECTED_FILE);

function readJson(filePath) {
  return JSON.parse(fs.readFileSync(filePath, "utf8"));
}

function writeJson(relativeFile, data) {
  const filePath = path.join(repoRoot, relativeFile);
  fs.mkdirSync(path.dirname(filePath), { recursive: true });
  fs.writeFileSync(filePath, `${JSON.stringify(data, null, 2)}\n`, "utf8");
  return filePath;
}

function getByPath(source, dotPath) {
  if (!dotPath) return source;
  return String(dotPath)
    .split(".")
    .filter(Boolean)
    .reduce((current, key) => current?.[key], source);
}

function findSubject(sourceJson, subjectContract) {
  if (!subjectContract) {
    return sourceJson;
  }

  // v0.1: ViewDef executeButton を探す小さな汎用ロケータ。
  // 期待値そのものではなく「どこからActualを取るか」だけを担当する。
  if (subjectContract.source_path === "views[].toolbar.executeButton") {
    const views = Array.isArray(sourceJson?.views) ? sourceJson.views : [];
    const find = subjectContract.find ?? {};

    for (const view of views) {
      const button = view?.toolbar?.executeButton;
      if (!button) continue;

      const matched = Object.entries(find).every(([field, expectedValue]) => {
        return button?.[field] === expectedValue;
      });

      if (matched) {
        return button;
      }
    }

    return null;
  }

  throw new Error(`未対応のsubject.source_pathです: ${subjectContract.source_path}`);
}

function getActualValue({ check, expectedSpec, targetJson }) {
  const subject = findSubject(targetJson, expectedSpec.execution_contract?.subject);
  const subjectId = expectedSpec.execution_contract?.subject?.id;
  const target = check.target ?? "";

  if (subjectId && target.startsWith(`${subjectId}.`)) {
    return getByPath(subject, target.slice(subjectId.length + 1)) ?? null;
  }

  return getByPath(targetJson, target) ?? null;
}

function formatValue(value) {
  if (value === undefined) return null;
  return value;
}

function displayValue(value) {
  if (value == null) return "";
  if (typeof value === "string") return value;
  return JSON.stringify(value);
}

function evaluateCheck(type, expected, actual) {
  if (type === "equals") {
    return {
      pass: Object.is(actual, expected),
      missing: [],
    };
  }

  if (type === "includesAll") {
    const expectedItems = Array.isArray(expected) ? expected : [expected];

    if (typeof actual === "string") {
      const missing = expectedItems.filter((item) => !actual.includes(String(item)));
      return {
        pass: missing.length === 0,
        missing,
      };
    }

    if (Array.isArray(actual)) {
      const missing = expectedItems.filter((item) => !actual.includes(item));
      return {
        pass: missing.length === 0,
        missing,
      };
    }

    return {
      pass: false,
      missing: expectedItems,
    };
  }

  throw new Error(`未対応のcheck typeです: ${type}`);
}

function getExpectedChecks(expectedSpec) {
  const includeIds = expectedSpec.execution_contract?.include_test_pattern_ids;
  const targetPatternIds = Array.isArray(includeIds) && includeIds.length > 0 ? includeIds : [TEST_ID];

  return (expectedSpec.expected_checks ?? [])
    .filter((check) => targetPatternIds.includes(check.test_pattern_id))
    .filter((check) => check.machine_check_ready === true);
}

function makeActualObservationCheck({ check, actual }) {
  return {
    check_id: check.check_id,
    test_pattern_id: check.test_pattern_id,
    title: check.title,
    name: check.name ?? check.source_check_name ?? check.check_id,
    target: check.target,
    actual: formatValue(actual),
    actual_display: displayValue(actual),
    source_check_name: check.source_check_name ?? null,
  };
}

function makeDiffCheck({ check, actual, evaluation }) {
  return {
    check_id: check.check_id,
    test_pattern_id: check.test_pattern_id,
    title: check.title,
    name: check.name ?? check.source_check_name ?? check.check_id,
    target: check.target,
    type: check.type,
    expected: formatValue(check.expected),
    actual: formatValue(actual),
    expected_display: displayValue(check.expected),
    actual_display: displayValue(actual),
    missing: evaluation.missing,
    pass: evaluation.pass,
    message: evaluation.pass
      ? "OK"
      : `${check.check_id} failed: expected ${displayValue(check.expected)}, actual ${displayValue(actual)}`,
    relation_refs: [
      check.test_pattern_id,
      ...(Array.isArray(check.constraint_ids) ? check.constraint_ids : []),
    ].filter(Boolean),
  };
}

function buildDiffSummary(diffChecks, status) {
  const failed = diffChecks.filter((check) => check.pass === false);
  const failedCheckIds = failed.map((check) => check.check_id).filter(Boolean);
  const failedChecks = failed.map((check) => check.name ?? check.check_id).filter(Boolean);
  const firstFailure = failed[0] ?? null;

  return {
    resultLabel: status === "pass" ? "✅ PASS" : "🚨 FAIL",
    failedCount: failed.length,
    failedChecks,
    failedCheckIds,
    summary: failed.length === 0
      ? "✅ 差分は検出されませんでした。"
      : `🚨 ${failed.length}件の差分を検出しました: ${failedCheckIds.join(", ")}`,
    firstFailure: firstFailure
      ? {
          check_id: firstFailure.check_id,
          name: firstFailure.name,
          type: firstFailure.type,
          target: firstFailure.target,
          expected: firstFailure.expected,
          actual: firstFailure.actual,
          missing: firstFailure.missing,
        }
      : null,
  };
}

function buildActualObservation({ expectedSpec, targetFile, targetJson, expectedChecks }) {
  const capturedAt = new Date().toISOString();
  const checks = expectedChecks.map((check) => {
    const actual = getActualValue({ check, expectedSpec, targetJson });
    return makeActualObservationCheck({ check, actual });
  });

  return {
    schema_version: "qa_actual_observation_v0_1",
    document_type: "qa_actual_observation",
    view_def: expectedSpec.execution_contract?.actual_view_def ?? "qa/qa_actual_observation_view_def_v0_1.json",
    test_id: expectedSpec.execution_contract?.test_id ?? TEST_ID,
    test_name: "インシデント管理ViewDefにAI依頼プロンプトコピーボタンが宣言されている",
    phase: expectedSpec.source_incident?.phase ?? null,
    incident_file: expectedSpec.source_incident?.incident_file ?? null,
    expected_file: EXPECTED_FILE,
    target_file: targetFile,
    capturedAt,
    result_summary: {
      total_count: checks.length,
    },
    checks,
  };
}

function buildDiffResult({ expectedSpec, targetFile, actualObservation, expectedChecks }) {
  const diffChecks = expectedChecks.map((check) => {
    const actualCheck = actualObservation.checks.find((item) => item.check_id === check.check_id);
    const actual = actualCheck?.actual ?? null;
    const evaluation = evaluateCheck(check.type, check.expected, actual);
    return makeDiffCheck({ check, actual, evaluation });
  });

  const total = diffChecks.length;
  const passCount = diffChecks.filter((check) => check.pass).length;
  const failCount = total - passCount;
  const status = failCount === 0 ? "pass" : "fail";
  const summary = buildDiffSummary(diffChecks, status);
  const generatedAt = new Date().toISOString();
  const actualFile = expectedSpec.execution_contract?.actual_file ?? expectedSpec.execution_contract?.actual_result_file;
  const diffFile = expectedSpec.execution_contract?.diff_file ?? expectedSpec.execution_contract?.diff_result_file;

  return {
    schema_version: "diff_result_v0_1",
    document_type: "diff_result",
    domain: "qa",
    diff_kind: "qa_static_viewdef",
    view_def: expectedSpec.execution_contract?.diff_view_def ?? "qa/qa_diff_result_view_def_v0_1.json",
    test_id: expectedSpec.execution_contract?.test_id ?? TEST_ID,
    testId: expectedSpec.execution_contract?.test_id ?? TEST_ID,
    test_name: actualObservation.test_name,
    title: actualObservation.test_name,
    phase: expectedSpec.source_incident?.phase ?? null,
    incident_file: expectedSpec.source_incident?.incident_file ?? null,
    expected_file: EXPECTED_FILE,
    actual_file: actualFile,
    diff_file: diffFile,
    target_file: targetFile,
    status,
    resultLabel: summary.resultLabel,
    summary: summary.summary,
    total,
    passCount,
    failCount,
    failedCount: summary.failedCount,
    failedChecks: summary.failedChecks,
    failedCheckIds: summary.failedCheckIds,
    firstFailure: summary.firstFailure,
    generated_at: generatedAt,
    capturedAt: generatedAt,
    result_summary: {
      total_count: total,
      pass_count: passCount,
      fail_count: failCount,
      total,
      passCount,
      failCount,
    },
    sourceFiles: {
      expectedFile: EXPECTED_FILE,
      actualFile,
      diffFile,
      targetFile,
    },
    checks: diffChecks,
  };
}

test("TP-IPC-001: Expected JSONからActual観測値とDiff結果を分離して出力する", () => {
  assert.ok(fs.existsSync(expectedPath), `Expected JSONが存在すること: ${EXPECTED_FILE}`);

  const expectedSpec = readJson(expectedPath);
  const targetFile = expectedSpec.execution_contract?.target_file;
  const actualFile = expectedSpec.execution_contract?.actual_file ?? expectedSpec.execution_contract?.actual_result_file;
  const diffFile = expectedSpec.execution_contract?.diff_file ?? expectedSpec.execution_contract?.diff_result_file;

  assert.ok(targetFile, "Expected JSONの execution_contract.target_file が定義されていること");
  assert.ok(actualFile, "Expected JSONの execution_contract.actual_file が定義されていること");
  assert.ok(diffFile, "Expected JSONの execution_contract.diff_file が定義されていること");

  const targetPath = path.join(repoRoot, targetFile);
  assert.ok(fs.existsSync(targetPath), `対象ViewDefが存在すること: ${targetFile}`);

  const targetJson = readJson(targetPath);
  const expectedChecks = getExpectedChecks(expectedSpec);

  assert.ok(expectedChecks.length > 0, `${TEST_ID} の machine_check_ready=true のExpected Checkが存在すること`);

  for (const check of expectedChecks) {
    assert.ok("expected" in check, `${check.check_id} に expected が明記されていること`);
    assert.ok(check.target, `${check.check_id} に target が明記されていること`);
    assert.ok(check.type, `${check.check_id} に type が明記されていること`);
  }

  const actualObservation = buildActualObservation({ expectedSpec, targetFile, targetJson, expectedChecks });
  const diffResult = buildDiffResult({ expectedSpec, targetFile, actualObservation, expectedChecks });

  // 重要: Expected差分でテストをfailにする場合でも、
  // Actual/Diff JSONは必ず先に書き出してから判定する。
  // これにより「failした理由」をStudioくんで確認できる。
  const actualOutputPath = writeJson(actualFile, actualObservation);
  const diffOutputPath = writeJson(diffFile, diffResult);

  assert.ok(fs.existsSync(actualOutputPath), `Actual Observation JSONが出力されていること: ${actualFile}`);
  assert.ok(fs.existsSync(diffOutputPath), `Diff Result JSONが出力されていること: ${diffFile}`);

  console.log(`[FRBStudio] Actual Observation JSON written: ${actualOutputPath}`);
  console.log(`[FRBStudio] Diff Result JSON written: ${diffOutputPath}`);

  if (diffResult.failedCount !== 0) {
    assert.fail(
      `Diff Result JSONを出力しました。Studioくんで確認してください: ${diffFile} ` +
      `(failedCount=${diffResult.failedCount}, failedCheckIds=${diffResult.failedCheckIds.join(", ")})`
    );
  }
});
