# FRB ViewDef Rules v0.6

このZIPには、ViewDef生成ルールとJSON Schemaの v0.6 更新版を含めています。

## 追加内容

v0.5の Relation / VirtualData ルールを引き継ぎ、以下を追加しました。

- `virtualData.writeBack` による主対象JSONへの単一ソース書き戻し
- 仮想ビューからの更新は、許可フィールドだけに限定
- 複数JSON同時更新は対象外
- 業務データサンプルでの `customer_name` / `project_name` / `employee_name` 更新パターン

## 基本思想

```text
Data
  事実JSON

Relation
  データ同士のコネクト線JSON

VirtualData
  複数JSONとRelationから、その場で生成する表示用データ

WriteBack
  仮想行から主対象JSONの許可フィールドだけを書き戻す

View
  表示定義
```

## ファイル

- `FRB_VIEW_DEF_GENERATION_RULES_v0_6_relation_virtual_writeback.md`
- `frb_view_def_schema_v0_6_relation_virtual_writeback.json`
- `README_viewdef_rules_v0_6.md`
