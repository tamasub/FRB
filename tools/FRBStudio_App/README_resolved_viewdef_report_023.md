# frb_studio_resolved_viewdef_report_023

## 変更内容

022 の Resolved ViewDef Report に対して、`fieldType` 使用時の `caption` 明示ルールに対応した版。

### 追加

- ViewDef Markdown レポートの `解決サマリ` に `fieldType caption未指定` 件数を追加
- caption未指定がある場合、警告テーブルを出力
- `fieldType` を使う既存ViewDefに `caption` を明示
- 生成ルール `v0.10 — FieldType Caption Required` を追加

## 方針

```text
fieldType を使う場合でも、caption は ViewDef側に明示する。
ViewDef側 caption が Common側 caption より優先される。
Common側 caption は fallback として扱う。
```

## 推奨形

```json
{
  "field": "quality_axis_cd",
  "caption": "品質観点",
  "fieldType": "qa.quality_axis"
}
```

## 非推奨形

```json
{
  "field": "quality_axis_cd",
  "fieldType": "qa.quality_axis"
}
```

## 確認ポイント

1. `qa_expected_checks_sample_view_def_v0_1.json`
   - 元ViewDef JSON側で `quality_axis_cd / check_axis_cd / risk_cd` に caption がある
   - 解決サマリの `fieldType caption未指定` が 0件

2. `business_customers_fieldtype_sample_view_def_v0_1.json`
   - 元ViewDef JSON側で `customer_id / customer_name` に caption がある
   - 解決済みViewDef JSONでは Common FieldType の詳細が展開される

3. `relation_approval_view_def_v0_1.json`
   - relation系 fieldType に caption が明示されている
   - status / coverage / confidence / priority の options が展開される

## 補足

caption未指定でも実行時は Common側 caption に fallback するため既存互換性は維持する。
ただし、今後のViewDef生成では `field / caption / fieldType` の3点セットを基本形とする。
