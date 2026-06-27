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

function evaluateCheck(type, expected, actual) {
  if (type === "equals") {
    return Object.is(actual, expected);
  }

  if (type === "includesAll") {
    const expectedItems = Array.isArray(expected) ? expected : [expected];

    if (typeof actual === "string") {
      return expectedItems.every((item) => actual.includes(String(item)));
    }

    if (Array.isArray(actual)) {
      return expectedItems.every((item) => actual.includes(item));
    }

    return false;
  }

  throw new Error(`未対応のcheck typeです: ${type}`);
}

function makeActualCheck({ check, actual, pass }) {
  return {
    check_id: check.check_id,
    test_pattern_id: check.test_pattern_id,
    title: check.title,
    target: check.target,
    type: check.type,
    expected: check.expected,
    actual,
    pass,
    relation_refs: [
      check.test_pattern_id,
      ...(Array.isArray(check.constraint_ids) ? check.constraint_ids : []),
    ].filter(Boolean),
  };
}

function buildSharedResultSummary(checks, status) {
  const failedChecks = checks.filter((check) => check.pass === false);
  const failedIds = failedChecks.map((check) => check.check_id ?? check.name).filter(Boolean);
  const firstFailureCheck = failedChecks[0] ?? null;

  return {
    resultLabel: status === "pass" ? "✅ PASS" : "🚨 FAIL",
    failedCount: failedChecks.length,
    failedChecks: failedIds,
    summary: failedChecks.length === 0
      ? "✅ 差分は検出されませんでした。"
      : `🚨 ${failedChecks.length}件の差分を検出しました: ${failedIds.join(", ")}`,
    firstFailure: firstFailureCheck
      ? {
          name: firstFailureCheck.check_id ?? firstFailureCheck.name ?? "",
          type: firstFailureCheck.type ?? "",
          target: firstFailureCheck.target ?? "",
          expected: firstFailureCheck.expected ?? null,
          actual: firstFailureCheck.actual ?? null,
          missing: firstFailureCheck.missing ?? [],
        }
      : null,
  };
}

function writeActualResult({ expectedSpec, targetFile, checks }) {
  const passCount = checks.filter((check) => check.pass).length;
  const failCount = checks.length - passCount;
  const status = failCount === 0 ? "pass" : "fail";
  const sharedSummary = buildSharedResultSummary(checks, status);
  const resultFile = expectedSpec.execution_contract?.actual_result_file;

  if (!resultFile) {
    throw new Error("Expected JSONの execution_contract.actual_result_file が未定義です。");
  }

  const resultPath = path.join(repoRoot, resultFile);
  const result = {
    schema_version: "qa_actual_result_v0_1",
    document_type: "qa_actual_result",
    view_def: expectedSpec.execution_contract?.actual_result_view_def ?? "qa/qa_actual_result_view_def_v0_1.json",
    test_id: TEST_ID,
    test_name: "インシデント管理ViewDefにAI依頼プロンプトコピーボタンが宣言されている",
    phase: expectedSpec.source_incident?.phase ?? null,
    incident_file: expectedSpec.source_incident?.incident_file ?? null,
    expected_file: EXPECTED_FILE,
    target_file: targetFile,
    status,
    resultLabel: sharedSummary.resultLabel,
    summary: sharedSummary.summary,
    failedCount: sharedSummary.failedCount,
    failedChecks: sharedSummary.failedChecks,
    firstFailure: sharedSummary.firstFailure,
    generated_at: new Date().toISOString(),
    result_summary: {
      total_count: checks.length,
      pass_count: passCount,
      fail_count: failCount,
    },
    checks,
  };

  fs.mkdirSync(path.dirname(resultPath), { recursive: true });
  fs.writeFileSync(resultPath, `${JSON.stringify(result, null, 2)}
`, "utf8");
  return result;
}

test("TP-IPC-001: Expected JSONに記載された期待値でViewDef静的チェックを実行する", () => {
  assert.ok(fs.existsSync(expectedPath), `Expected JSONが存在すること: ${EXPECTED_FILE}`);

  const expectedSpec = readJson(expectedPath);
  const targetFile = expectedSpec.execution_contract?.target_file;

  assert.ok(targetFile, "Expected JSONの execution_contract.target_file が定義されていること");

  const targetPath = path.join(repoRoot, targetFile);
  assert.ok(fs.existsSync(targetPath), `対象ViewDefが存在すること: ${targetFile}`);

  const targetJson = readJson(targetPath);
  const expectedChecks = (expectedSpec.expected_checks ?? [])
    .filter((check) => check.test_pattern_id === TEST_ID)
    .filter((check) => check.machine_check_ready === true);

  assert.ok(expectedChecks.length > 0, `${TEST_ID} の machine_check_ready=true のExpected Checkが存在すること`);

  const checks = expectedChecks.map((check) => {
    assert.ok("expected" in check, `${check.check_id} に expected が明記されていること`);
    assert.ok(check.target, `${check.check_id} に target が明記されていること`);
    assert.ok(check.type, `${check.check_id} に type が明記されていること`);

    const actual = getActualValue({ check, expectedSpec, targetJson });
    const pass = evaluateCheck(check.type, check.expected, actual);

    return makeActualCheck({ check, actual, pass });
  });

  const actualResult = writeActualResult({ expectedSpec, targetFile, checks });

  assert.equal(actualResult.status, "pass", `Actual Result JSONを確認してください: ${expectedSpec.execution_contract.actual_result_file}`);
});
