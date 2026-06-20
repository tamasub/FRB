# FRB ViewDef Rules v0.5

このZIPには、ViewDef生成ルールとJSON Schemaの v0.5 更新版を含めています。

## 追加内容

v0.4の内容を引き継ぎ、以下を追加しました。

- `dataSources` による複数JSON参照
- Relation JSON（コネクト線定義JSON）のルール
- `virtualData` による仮想データ生成定義
- 汎用 builder `relation_axis_cards`
- diffチェック軸 builder `relation_diff_check_cards`
- `diffViewDefs.base` / `diffViewDefs.children` による BASE / CHILD 継承概念の保持
- Relation系ViewDefの命名規則
  - `relation_edit_view_def_v0_1.json`
  - `relation_axis_constraint_view_def_v0_1.json`
  - `relation_axis_test_pattern_view_def_v0_1.json`
  - `relation_axis_diff_check_view_def_v0_1.json`
  - `relation_rows_debug_view_def_v0_1.json`
- `writePolicy` による「読みは複数JSON、書きは主対象JSONのみ」のスモールスタート方針

## 基本思想

```text
Data
  事実JSON

Relation
  データ同士のコネクト線JSON

VirtualData
  複数JSONとRelationから、その場で生成する表示用データ

View
  表示定義
```

## ファイル

- `FRB_VIEW_DEF_GENERATION_RULES_v0_5_relation_virtual_data.md`
- `frb_view_def_schema_v0_5_relation_virtual_data.json`
- `README_viewdef_rules_v0_5.md`

## 注意

`virtualData` は表示用に生成される派生データであり、原則として保存対象JSONには書き戻しません。
現時点の更新方針は `writePolicy.mode = singleSource` を基本とします。
