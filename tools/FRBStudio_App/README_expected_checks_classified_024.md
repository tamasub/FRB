# frb_studio_expected_checks_classified_024

## 概要

観点分類入り Expected 定義の初期版です。

今回の方針は、**テストパターンは増やさず、Expected / Check を増やす** です。

```text
TestPattern
  実行単位・シナリオ単位

Expected / Check
  確認項目単位
  品質観点 / チェック観点 / リスクで分類
```

## 追加・更新ファイル

### 追加

- `data/json/qa_expected_checks_classified_v0_1.json`
- `defs/qa_expected_checks_classified_view_def_v0_1.json`
- `schema_RULES/FRB_VIEW_DEF_GENERATION_RULES_v0_11_expected_checks_classification.md`
- `schema_RULES/README_viewdef_rules_v0_11.md`

### 更新

- `defs/common_types_v0_1.json`
- `defs/common/common_types_v0_1.json`

Expected / Check 用の意味FieldTypeを追加しました。

```text
qa.check_id
qa.test_pattern_id
qa.source_check_name
qa.expected_summary
qa.constraint_ids
qa.evidence_hint
```

## まず見るファイル

```text
data/json/qa_expected_checks_classified_v0_1.json
```

このデータは、既存の `qa_test_patterns_sample_v0_1.json` の3件のテストパターンを増やさず、Expected / Check を18件に増やしています。

## 確認ポイント

- `quality_axis_cd` で品質観点を分類できる
- `check_axis_cd` でチェック観点を分類できる
- `risk_cd` でリスク分類できる
- `test_pattern_id` で既存テストパターンにぶら下げられる
- `constraint_ids` で制約との接続候補を持てる
- `source_check_name` でテストコード・diff内のチェック名とつなぐ準備ができる

## 次の候補

次は、この Expected / Check 定義を使って、VirtualDataで観点クロス集計を作るとよいです。

```text
品質観点 × リスク
チェック観点 × リスク
テストパターン × チェック件数
制約ID × チェック件数
```
