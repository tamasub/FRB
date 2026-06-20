# FRBStudio Expected Cross VirtualData 025

## 目的

観点分類入り Expected 定義をもとに、テストパターンを増やす前に不足観点を見つけるためのクロス集計 VirtualData を追加した版。

管理対象の Expected JSON はそのままに、ViewDef 側の `virtualData` で集計結果を一時生成する。

## 追加ファイル

### ViewDef

- `defs/qa_cross_quality_risk_view_def_v0_1.json`
  - 品質観点 × リスク
- `defs/qa_cross_check_risk_view_def_v0_1.json`
  - チェック観点 × リスク
- `defs/qa_cross_test_pattern_view_def_v0_1.json`
  - テストパターン別 Expected 件数
- `defs/qa_cross_constraint_view_def_v0_1.json`
  - 制約ID別 Expected 件数

### app.js

- `expected_check_cross_counts` builder を追加
- `virtualData` 配列から複数種類のクロス集計を生成可能
- `constraint_ids` のような配列項目は `explode: true` で1要素1行として集計可能
- `labelMap` と `labelSource` に対応

### common field types

`defs/common_types_v0_1.json` / `defs/common/common_types_v0_1.json` に、集計表示用 FieldType を追加。

- `qa.check_count`
- `qa.high_count`
- `qa.medium_count`
- `qa.low_count`
- `qa.risk_summary`
- `qa.quality_axis_name`
- `qa.check_axis_name`
- `qa.risk_name`
- `qa.test_pattern_title`
- `qa.constraint_id`
- `qa.check_ids`
- `qa.test_pattern_ids`

## 使い方

1. データJSONとして `qa_expected_checks_classified_v0_1.json` を読む
2. ViewDefコンボで以下のいずれかを選ぶ

```text
qa_cross_quality_risk_view_def_v0_1.json
qa_cross_check_risk_view_def_v0_1.json
qa_cross_test_pattern_view_def_v0_1.json
qa_cross_constraint_view_def_v0_1.json
```

## 今回の集計結果イメージ

元データ: `expected_checks` 18件

```text
TP-REL-STATUS-001 : 6件
TP-WB-001         : 5件
TP-MD-001         : 7件
```

品質観点別の傾向:

```text
evidence : 7件
safety   : 5件
display  : 3件
save     : 2件
operation: 1件
```

リスク別の傾向:

```text
high   : 5件
medium : 9件
low    : 4件
```

## 設計メモ

テストパターンは実行単位なので、まだ増やさない。

まず Expected / Check 側に観点分類を持たせ、VirtualData でクロス集計する。
これにより、以下のような不足が見える。

- 高リスクの保存系チェックが少ない
- エラー処理チェックが少ない
- 特定テストパターンにチェックが偏っている
- 制約IDに紐づくExpectedが足りない

## ViewDef例

```json
{
  "virtualData": [
    {
      "builder": "expected_check_cross_counts",
      "targetPath": "$.quality_risk_cross",
      "source": {
        "source": "$current",
        "path": "$.expected_checks"
      },
      "dimensions": [
        {
          "field": "quality_axis_cd",
          "outputField": "quality_axis_cd",
          "labelField": "quality_axis_name",
          "labelMap": {
            "display": "表示",
            "operation": "操作",
            "save": "保存",
            "evidence": "証跡",
            "safety": "安全性",
            "error": "エラー処理"
          }
        },
        {
          "field": "risk_cd",
          "outputField": "risk_cd",
          "labelField": "risk_name",
          "labelMap": {
            "high": "高",
            "medium": "中",
            "low": "低"
          }
        }
      ]
    }
  ]
}
```

## 注意

VirtualData は画面表示用の派生データなので、保存対象JSONには書き戻さない。

