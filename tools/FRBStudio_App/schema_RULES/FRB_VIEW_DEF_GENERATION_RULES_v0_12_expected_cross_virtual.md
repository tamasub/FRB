# FRB ViewDef Generation Rules v0.12 — Expected Cross VirtualData

## 追加概念

`expected_check_cross_counts` は、Expected / Check 定義を観点分類で集計する VirtualData builder である。

## 目的

テストパターンを増やす前に、Expected / Check の観点分類から不足観点を発見する。

## 基本方針

- TestPattern は実行単位
- Expected / Check は確認単位
- 観点分類は Expected / Check 側に持つ
- クロス集計は VirtualData として生成する
- 集計結果は保存対象JSONへ書き戻さない

## builder

```json
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
        "evidence": "証跡"
      }
    },
    {
      "field": "risk_cd",
      "outputField": "risk_cd",
      "labelField": "risk_name",
      "labelMap": {
        "high": "高"
      }
    }
  ]
}
```

## dimensions

| key | meaning |
| --- | --- |
| field | 元Expectedの項目名 |
| outputField | VirtualData出力先の項目名 |
| labelField | 表示名出力先の項目名 |
| labelMap | CDから表示名への変換表 |
| labelSource | dataSourcesから表示名を取得する設定 |
| explode | 配列を1要素1行に展開して集計する |

## explode

`constraint_ids` のような配列項目は、`explode: true` を指定する。

```json
{
  "field": "constraint_ids",
  "outputField": "constraint_id",
  "explode": true
}
```

## outputs

既定出力:

| field | meaning |
| --- | --- |
| check_count | チェック件数 |
| high_count | high risk 件数 |
| medium_count | medium risk 件数 |
| low_count | low risk 件数 |
| risk_summary | リスク内訳 |
| check_ids | 該当チェックID一覧 |
| test_pattern_ids | 該当テストパターンID一覧 |
| constraint_ids | 該当制約ID一覧 |

