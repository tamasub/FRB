# FRB ViewDef Generation Rules v0.8 — Common FieldTypes / cd-name options

## 目的

大量の Expected 定義・テストパターン定義を作る前に、観点分類の語彙を共通化する。

- 素データには `*_cd` を保存する
- 画面には `name` を表示する
- 集計・JOIN・クロス表は `cd` をキーにする
- 表示名の変更で素データを壊さない

## 共通Type定義ファイル

既定の共通Type定義ファイルは次の1つ。

```text
common/common_types_v0_1.json
```

ViewDefから明示する場合は以下を使う。

```json
{
  "fieldTypeSources": ["common/common_types_v0_1.json"]
}
```

## FieldType参照

ViewDefの field は、共通Typeを `fieldType` で参照できる。

```json
{
  "field": "feature_area_cd",
  "fieldType": "qa.feature_area"
}
```

共通Type側では以下を定義する。

```json
{
  "caption": "機能領域",
  "baseType": "select",
  "valueField": "cd",
  "labelField": "name",
  "options": [
    { "cd": "relation", "name": "Relation" },
    { "cd": "writeback", "name": "WriteBack" }
  ]
}
```

解決後は、内部的に次のような field として扱われる。

```json
{
  "field": "feature_area_cd",
  "caption": "機能領域",
  "type": "select",
  "options": [
    { "cd": "relation", "name": "Relation" },
    { "cd": "writeback", "name": "WriteBack" }
  ]
}
```

## cd/name options

`options` は従来の文字列配列も使用できる。

```json
"options": ["approved", "candidate", "rejected"]
```

新形式では `cd/name` を使用できる。

```json
"options": [
  { "cd": "approved", "name": "承認済み" },
  { "cd": "candidate", "name": "候補" },
  { "cd": "rejected", "name": "却下" }
]
```

この場合、画面表示は `name`、保存値は `cd` になる。

## 観点分類の推奨配置

### テストパターンJSON

テストパターンは大分類を持つ。

```json
{
  "test_pattern_id": "TP-REL-STATUS-001",
  "title": "Relation status filter の基本動作確認",
  "feature_area_cd": "relation",
  "test_axis_cd": "status_filter",
  "scenario_type_cd": "normal",
  "risk_cd": "high"
}
```

### Expected JSON

Expected は小分類を持つ。

```json
{
  "check_id": "CHK-REL-STATUS-001",
  "test_pattern_id": "TP-REL-STATUS-001",
  "title": "approved の Relation は証跡に採用される",
  "quality_axis_cd": "evidence",
  "check_axis_cd": "include",
  "risk_cd": "high"
}
```

`feature_area_cd` や `test_axis_cd` は、原則として `test_pattern_id` からテストパターン側をJOINして取得する。

## スモールスタート対象

今回の最小対象は以下。

```text
qa.feature_area
qa.test_axis
qa.quality_axis
qa.check_axis
qa.scenario_type
qa.risk
relation.status
relation.coverage
```

## 設計方針

```text
大量Expectedを作る前に、分類語彙を固定する。
クロス表を作る前に、クロス表の軸を固定する。
```
