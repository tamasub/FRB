qa_expected_checks_classified_v0_1.json を読み、
ncjs-screen-state-compare.checks.spec.ts に追加可能なテストを追記してください。

条件:
- 既存テストの構造・命名規則に合わせる
- Expected定義の check_id を必ずテスト結果に残す
- ncjs-screen-state-compare.checks.spec.ts で確認できるものだけ実装する
- 実装できない Expected はコメントまたは TODO として理由を残す
- test_pattern_id は増やさない
- 既存テストを壊さない
- 追加対象は high risk を優先する

