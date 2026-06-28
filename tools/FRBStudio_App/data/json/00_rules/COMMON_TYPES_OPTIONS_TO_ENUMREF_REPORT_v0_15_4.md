# COMMON_TYPES_OPTIONS_TO_ENUMREF_REPORT_v0_15_4

- phase: v0.15.4-common-types-options-to-enumref
- date: 2026-06-28
- objective: common_types_v0_1.json の既存 select options を棚卸しし、共通Enum正本 common_enums_v0_1.json へ段階的に寄せる。

## 方針

- `enumRef` を値語彙の正本として扱う。
- 既存 `options` はこの段階では削除せず、互換用スナップショットとして残す。
- `risk.high` / `confidence.high` / `priority.high` / `severity.high` は意味が違うため統合しない。
- `00_rules/common_enums_v0_1.json` のパスは変更しない。

## 移行対象

| FieldType | enumRef | options | 方針 |
|---|---:|---:|---|
| `qa.feature_area` | `qa.feature_area` | 7 | migrated_enumRef_with_options_snapshot |
| `qa.test_axis` | `qa.test_axis` | 7 | migrated_enumRef_with_options_snapshot |
| `qa.quality_axis` | `qa.quality_axis` | 6 | migrated_enumRef_with_options_snapshot |
| `qa.check_axis` | `qa.check_axis` | 7 | migrated_enumRef_with_options_snapshot |
| `qa.scenario_type` | `qa.scenario_type` | 6 | migrated_enumRef_with_options_snapshot |
| `qa.finding_type` | `qa.finding_type` | 4 | migrated_enumRef_with_options_snapshot |
| `qa.severity` | `qa.severity_level` | 4 | migrated_enumRef_with_options_snapshot |
| `relation.status` | `relation.status` | 6 | migrated_enumRef_with_options_snapshot |
| `relation.coverage` | `relation.coverage` | 3 | migrated_enumRef_with_options_snapshot |
| `relation.node_type` | `relation.node_type` | 8 | migrated_enumRef_with_options_snapshot |
| `relation.relation_type` | `relation.relation_type` | 7 | migrated_enumRef_with_options_snapshot |
| `relation.confidence` | `relation.confidence` | 3 | migrated_enumRef_with_options_snapshot |
| `relation.priority` | `relation.priority` | 3 | migrated_enumRef_with_options_snapshot |

## 保留・注意

- 今回は一気に options を削除しない。
- `common_enums_v0_1.json` の配置変更は行わない。過去に `00_rules/common_enums_v0_1.json` 参照が多く、移動は別設計課題とする。
- RuntimeのenumRef解決は v0.15.2 の仕組みを使い、今回の主目的は値語彙正本への整理。
