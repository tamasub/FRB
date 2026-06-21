# 画面状態JSONテストパターン一覧

- 出力日時: 2026/6/20 0:45:27
- schema_version: 0.2-draft
- 件数: 3

## 基本情報
- 画面定義: screen_state_test_patterns_view_def_v0_2_chat.json
- Schema: 0.2-draft
- Suite ID: screen_state_suite_v0_1
- タイトル: 画面状態JSONテストパターン一覧
- 対象アプリ: No-Code JSON Studio v0.3-draft
- Base URL: http://localhost:5055/
- Expected Dir: test_patterns
- Actual Dir: tests_screen_state/test_results/actual
- Diff Dir: tests_screen_state/test_results/diff
- Expected ViewDef: screen_state_expected_view_def_v0_1.json
- Diff ViewDef: screen_state_diff_view_def_v0_2_checks.json
- メモ: v0.2-chat。テストパターン台帳にチャット欄と俺の確認状態を追加した初期版。

---

## テストパターン一覧
| 有効 | Pattern ID | テスト名 | Category | Kind | URL | Expected JSON | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| true | screen_state_smoke_001 | 初期表示の画面状態JSONを検証する | smoke | screen_state | / | test_patterns/screen_state_smoke_001.expected.json | active |
| false | screen_state_expected_editor_001 | Expected定義JSONを画面で確認する | smoke | manual_seed | / | test_patterns/screen_state_smoke_001.expected.json | draft |
| false | screen_state_diff_view_001 | Diff結果JSONを画面で確認する | regression | manual_seed | / |  | draft |