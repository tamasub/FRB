# COMMON_ENUMS_DEFINITION_REPORT_v0_15_1

## 対応概要

`v0.15.1-common-enums-definition` として、EnumをStudioくんの値語彙の正本として扱うための最小構造を追加した。

## 追加ファイル

- `data/json/00_rules/common_enums_v0_1.json`
- `defs/common/common_enums_view_def_v0_1.json`

## 設計方針

- Enum参照形式は `{namespace_id}.{enum_id}` とする。
- 値候補の基本項目は `cd / name / description / sort_order / deprecated` とする。
- `risk.high`、`priority.high`、`confidence.high` のようにcdが似ていても、意味が違うものは雑に統合しない。
- `common_types_v0_1.json` は既存互換のため今回は変更しない。
- FieldType側の `enumRef` 解決と既存options移行は後続インシデントへ分離する。

## 代表Enumサンプル

- `studio.lifecycle_status`
- `qa.risk_level`
- `qa.severity_level`
- `relation.status`
- `relation.confidence`
- `relation.priority`

## 非対応

- RuntimeのenumRef解決実装
- 既存common_types内optionsの一括移行
- context.read_timingの本追加

上記は `v0.15.2` 以降のインシデントで扱う。
