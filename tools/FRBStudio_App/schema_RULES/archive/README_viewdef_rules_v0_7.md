# FRB ViewDef Rules v0.7

このZIPには、ViewDef生成ルールとJSON Schemaの v0.7 更新版を含めています。

## 追加内容

- Relation Status Filter
- `statusFilter`: 証拠線として採用する status
- `structureStatusFilter`: `contains_check` など構造線として採用する status
- `excludeStatus`: 明示的に除外する status
- AI候補線 `candidate` と人間承認済み線 `approved` の分離
- `relation_axis_cards` / `relation_diff_check_cards` で承認済みRelationだけを証跡に効かせる方針

## ファイル

- `FRB_VIEW_DEF_GENERATION_RULES_v0_7_relation_status_filter.md`
- `frb_view_def_schema_v0_7_relation_status_filter.json`

## 推奨設定

```json
"statusFilter": ["approved"],
"structureStatusFilter": ["derived", "approved"],
"excludeStatus": ["rejected"]
```
