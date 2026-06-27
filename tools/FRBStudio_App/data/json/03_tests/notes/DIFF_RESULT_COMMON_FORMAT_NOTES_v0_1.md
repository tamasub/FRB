# Diff Result Common Format Notes v0.1

## 目的

QA Diff と Screen State Diff を、同じViewDefで見られる方向へ寄せるため、diff.json の上部サマリ項目を共通化する。

## 共通フィールド

- `schema_version`: `diff_result_v0_1`
- `document_type`: `diff_result`
- `domain`: `qa` / `screen_state` など
- `diff_kind`: Diffの種類
- `test_id`: 共通のテストID
- `testId`: 互換用エイリアス
- `test_name`: 共通のテスト名
- `title`: 互換用タイトル
- `status`: `pass` / `fail`
- `resultLabel`: 表示用判定
- `summary`: 表示用サマリ
- `total`
- `passCount`
- `failCount`
- `failedCount`
- `failedChecks`
- `failedCheckIds`
- `firstFailure`
- `result_summary`
- `sourceFiles`
- `checks[]`

## checks[] の共通フィールド

- `check_id`
- `name`
- `target`
- `type`
- `expected`
- `actual`
- `missing`
- `pass`
- `message`

## 責務

- `actual.json` は観測値のみを保持する。
- `diff.json` は expected / actual / pass / summary を保持する。
- 判定フィールドの正本は `checks[].pass` とする。
- 上部サマリの正本は `status`, `resultLabel`, `summary`, `failedCount`, `failedCheckIds`, `firstFailure` とする。

## Step 4-B の対象

- `data/json/03_tests/qa/v0_14_2_incident_prompt_copy_action/diff/TP-IPC-001.diff.json`
- `data/json/03_tests/screen_state/screen_state_smoke_001/diff/screen_state_smoke_001.diff.json`
- `tests/qa/static/incident_prompt_copy_action_viewdef_static.test.mjs`
- `tests/screen_state/ncjs-screen-state-compare.checks.spec.ts`

## 注意

このStepでは `actual.json` のフォーマットは変更しない。
