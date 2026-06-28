# v0.15.3 context-enums-added 作業レポート

## 対象phase

- `v0.15.3-context-enums-added`
- work_item_id: `studio_work_0067`

## 目的

AI文脈制御で使う「いつ文脈を読むか」を、ViewDefやData行のローカル文字列ではなく、共通Enumとして管理する。

## 追加したEnum

`common_enums_v0_1.json` に `context` namespace を追加し、`context.read_timing` を定義した。

候補値:

- `before_load`
- `after_load`
- `on_row_select`
- `before_edit`
- `before_save`
- `before_review`
- `before_diff_story`
- `before_code_update`
- `before_zip_return`

## 追加したFieldType

`defs/common/common_types_v0_1.json` に `context.context_read_timing` を追加した。

```json
{
  "baseType": "select",
  "enumRef": "context.read_timing",
  "valueField": "cd",
  "labelField": "name"
}
```

## サンプル

- Data: `data/json/00_rules/context_refs_sample_data_v0_1.json`
- ViewDef: `defs/rules/context_refs_sample_view_def_v0_1.json`

このサンプルは `context_refs[].read_timing` に `context.context_read_timing` FieldTypeを使う例である。

## スコープ外

- ViewDef `read_contract` の実行制御
- Data行 `context_refs` のRuntime解釈
- `context.purpose / context.failure_policy / context.trust` の正本Enum化

これらは後続インシデントで扱う。


## v0.15.3.1 追加補修 / commonEnumSources API相対パス補正

画面確認で `共通Enum定義JSON[json/00_rules/common_enums_v0_1.json]` が `/api/data/json/00_rules/common_enums_v0_1.json` として読まれ、404になる問題を確認した。

FRBStudio の `/api/data` は `data/json` を起点にするため、Enum正本のRuntime既定パスを `00_rules/common_enums_v0_1.json` に補正した。あわせて、過去互換として `data/json/...` または `json/...` が指定された場合もAPI相対パスへ正規化する。

確認対象:

- `DEFAULT_COMMON_ENUMS_FILE = '00_rules/common_enums_v0_1.json'`
- `commonEnumSources = ['00_rules/common_enums_v0_1.json']`
- `context.read_timing`
- `context.context_read_timing`
