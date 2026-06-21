# FRB ViewDef Generation Rules v0.11 — Expected Checks Classification

## 目的

テストパターンをむやみに増やさず、確認粒度は Expected / Check 定義で増やす。

## 基本方針

- TestPattern は実行単位・シナリオ単位。
- Expected / Check は確認項目単位。
- TestPattern を増やす前に、Expected / Check の観点分類を増やす。

## Expected / Check 推奨フィールド

| field | 役割 |
| --- | --- |
| check_id | チェック項目の一意ID |
| test_pattern_id | 紐づくテストパターンID |
| title | 人間が読むチェック名 |
| quality_axis_cd | 品質観点。表示・操作・保存・証跡・安全性・エラー処理など |
| check_axis_cd | チェック観点。採用確認・除外確認・構造線確認・表示確認・書込確認など |
| risk_cd | リスク。high / medium / low |
| source_check_name | テストコードやdiff内の実チェック名との接続候補 |
| expected_summary | 期待する状態の説明 |
| constraint_ids | 証拠になる制約ID |
| evidence_hint | どこを見れば証跡になるか |
| note | 補足 |

## fieldType と caption

fieldType を使う場合でも、ViewDef側 caption は原則必須。

```json
{
  "field": "quality_axis_cd",
  "caption": "品質観点",
  "fieldType": "qa.quality_axis"
}
```

## 分類の持ち方

- feature_area / test_axis / scenario_type は原則 TestPattern 側。
- quality_axis / check_axis / risk は Expected / Check 側。
- ただし、JOINまたはVirtualDataが未整備の場合は、一時的にExpected側へ冗長保持してもよい。

## 今回のサンプル

- `data/json/qa_expected_checks_classified_v0_1.json`
- `defs/qa_expected_checks_classified_view_def_v0_1.json`

このサンプルは、既存の `qa_test_patterns_sample_v0_1.json` の3件のTestPatternを増やさず、Expected / Checkだけを18件に増やしている。
