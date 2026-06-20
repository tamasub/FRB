# screen_state_expected_checkid_031

## 変更内容

- `screen_state_smoke_001.expected.json` の既存 `checks` に `check_id` を追加しました。
- `ncjs-screen-state-compare.checks.spec.ts` 側で `check_id` を読み取り、diff結果JSONの各checkに `check_id` を残すようにしました。
- 失敗一覧にも `failedCheckIds` を追加しました。

## 追加Expectedの扱い

`qa_expected_checks_classified_v0_1.json` の high risk 追加Expectedを確認しましたが、今回の `screen_state_smoke_001` が取得している画面状態は、`appTitle / headerText / buttons / selects / inputs` の初期表示スモーク範囲です。

そのため、以下の追加Expectedはこの `screen_state_smoke_001.expected.json` では直接確認しない方針にしました。

- `CHK-MD-008` / `TP-MD-001`: Markdown出力にAI貼り付け用ブロックが表示される
- `CHK-REL-STATUS-007` / `TP-REL-STATUS-001`: Relation承認ビューで候補線の承認対象を操作観点で確認できる
- `CHK-REL-STATUS-008` / `TP-REL-STATUS-001`: contains_check 構造線が高リスク観点で採用確認できる
- `CHK-MD-009` / `TP-MD-001`: Markdown AI Prompt 出力で対象行が欠落した場合に検出できる
- `CHK-WB-006` / `TP-WB-001`: FieldType表示項目の高リスク表示確認
- `CHK-MD-010` / `TP-MD-001`: ViewDef Markdownレポートで元ViewDefと解決済みViewDefを確認できる
- `CHK-REL-STATUS-009` / `TP-REL-STATUS-001`: Relation status filter の異常系を確認できる

理由:

- Markdown出力、ViewDef Markdownレポート、Relation承認ビュー、Relation status filter、FieldType詳細表示は、初期表示スモークの `ScreenState` だけでは確認できません。
- 無理に `screen_state_smoke_001.expected.json` に入れると、期待値JSONが実際の画面状態と対応しなくなります。

## 次の候補

これらを自動化する場合は、別の `test_pattern_id` ではなく、既存の `TP-MD-001 / TP-REL-STATUS-001 / TP-WB-001` に対応する expected JSON と spec を分けて作るのが安全です。

今回の成果は、まず `screen_state_smoke_001` のテスト結果に `check_id` を残せるようにしたことです。
