# frb_studio_common_field_types_021

## 変更内容

020のCommon FieldTypesに対して、意味のある通常項目FieldTypeを追加した版。

### 追加・拡張

- `relation.status` 周辺を拡張
  - `relation.status`
  - `relation.coverage`
  - `relation.confidence`
  - `relation.priority`
  - `relation.relation_type`
  - `relation.node_type`
  - `relation.relation_id / from_id / to_id`
- optionなしの通常項目FieldTypeを追加
  - `business.customer_id`
  - `business.customer_name`
  - `business.project_id`
  - `business.project_name`
  - `business.employee_id`
  - `business.employee_name`
- Business Relation系ViewDefに `fieldTypeSources` と `fieldType` を適用
- Relation承認/編集/デバッグ系ViewDefにRelation系FieldTypeを適用
- 通常項目確認用に `business_customers_fieldtype_sample_view_def_v0_1.json` を追加

## 確認ポイント

1. `relation_approval_view_def_v0_1.json`
   - status / coverage / confidence / priority が日本語表示になる
   - 保存値は cd のまま

2. `relation_axis_business_customer_view_def_v0_1.json`
   - customer_id / customer_name が共通FieldTypeで表示される

3. `business_customers_fieldtype_sample_view_def_v0_1.json`
   - optionなしの普通項目FieldTypeだけで、顧客ID/顧客名が表示・編集・検索できる
