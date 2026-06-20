# ViewDef定義レポート — 観点分類入りExpected定義

## 基本情報
- 出力日時: 2026/6/20 20:00:42
- 対象ViewDef: qa_expected_checks_classified_view_def_v0_1.json
- views: 1

## View / Section 概要
| View | View Caption | Section | Section Caption | Type | DataPath | KeyField | Fields |
| --- | --- | --- | --- | --- | --- | --- | ---: |
| main | 観点分類入りExpected定義 | summary | 概要 | form | $ |  | 5 |
| main | 観点分類入りExpected定義 | mainGrid | Expected / Check 一覧 | grid | $.expected_checks |  | 11 |
| main | 観点分類入りExpected定義 | policy | 運用方針 | form | $.policy |  | 3 |

## 継承差分サマリ

このViewDefは extends を持たないため、継承差分はありません。

## 解決サマリ

- 読込済み共通Type namespace: qa / relation / business / core
- fieldType参照: 18件
- fieldType caption未指定: 0件
- 制約: fieldType を使う field でも、元ViewDef側に caption を明示することを推奨します。ViewDef側 caption が Common 側 caption より優先されます。
- 見方: 「Common由来候補」は元ViewDefに書かれておらず、解決後に現れた項目です。

| View | Section | field | fieldType | caption | type | width | options | Common由来候補 | ViewDef個別指定 |
| --- | --- | --- | --- | --- | --- | ---: | --- | --- | --- |
| main | summary | schema_version | core.schema_version | Schema | text | 120 |  | type=text / readonly=false / grid.visible=true / grid.width=120 / edit.visible=true / edit.readonly=false / ... +2 | caption=Schema |
| main | summary | document_type | core.document_type | 文書種別 | text | 170 |  | type=text / readonly=false / grid.visible=true / grid.width=170 / edit.visible=true / edit.readonly=false / ... +2 | caption=文書種別 |
| main | summary | title | core.title | タイトル | text | 360 |  | type=text / readonly=false / edit.visible=true / edit.readonly=false / search.visible=true / search.operator=contains | caption=タイトル / grid.visible=false / grid.width=360 |
| main | summary | description | core.note | 説明 | textarea | 420 |  | type=textarea / readonly=false / edit.visible=true / edit.readonly=false / search.visible=true / search.operator=contains | caption=説明 / grid.visible=false / grid.width=420 |
| main | mainGrid | check_id | qa.check_id | チェックID | text | 170 |  | type=text / readonly=false / grid.visible=true / grid.width=170 / edit.visible=true / edit.readonly=false / ... +2 | caption=チェックID |
| main | mainGrid | test_pattern_id | qa.test_pattern_id | テストパターンID | text | 170 |  | type=text / readonly=false / grid.visible=true / grid.width=170 / edit.visible=true / edit.readonly=false / ... +2 | caption=テストパターンID |
| main | mainGrid | title | core.title | タイトル | text | 360 |  | type=text / readonly=false / grid.visible=true / edit.visible=true / edit.readonly=false / search.visible=true / ... +1 | caption=タイトル / grid.width=360 |
| main | mainGrid | quality_axis_cd | qa.quality_axis | 品質観点 | select | 120 | 6件 | type=select / grid.visible=true / grid.width=120 / edit.visible=true / search.visible=true / search.operator=equals / ... +1 | caption=品質観点 |
| main | mainGrid | check_axis_cd | qa.check_axis | チェック観点 | select | 120 | 7件 | type=select / grid.visible=true / grid.width=120 / edit.visible=true / search.visible=true / search.operator=equals / ... +1 | caption=チェック観点 |
| main | mainGrid | risk_cd | qa.risk | リスク | select | 80 | 3件 | type=select / grid.visible=true / grid.width=80 / edit.visible=true / search.visible=true / search.operator=equals / ... +1 | caption=リスク |
| main | mainGrid | source_check_name | qa.source_check_name | 実チェック名 | text | 180 |  | type=text / readonly=false / grid.visible=true / grid.width=180 / edit.visible=true / edit.readonly=false / ... +2 | caption=実チェック名 |
| main | mainGrid | expected_summary | qa.expected_summary | 期待値概要 | textarea | 380 |  | type=textarea / readonly=false / grid.visible=true / grid.width=380 / edit.visible=true / edit.readonly=false / ... +2 | caption=期待値概要 |
| main | mainGrid | constraint_ids | qa.constraint_ids | 制約ID | stringArray | 180 |  | type=stringArray / readonly=false / grid.visible=true / grid.width=180 / edit.visible=true / edit.readonly=false | caption=制約ID |
| main | mainGrid | evidence_hint | qa.evidence_hint | 証跡ヒント | textarea | 320 |  | type=textarea / readonly=false / grid.visible=true / grid.width=320 / edit.visible=true / edit.readonly=false / ... +2 | caption=証跡ヒント |
| main | mainGrid | note | core.note | メモ | textarea | 260 |  | type=textarea / readonly=false / grid.visible=true / edit.visible=true / edit.readonly=false / search.visible=true / ... +1 | caption=メモ / grid.width=260 |
| main | policy | test_pattern_policy | core.note | テストパターン方針 | textarea | 520 |  | type=textarea / readonly=false / edit.visible=true / edit.readonly=false / search.visible=true / search.operator=contains | caption=テストパターン方針 / grid.visible=false / grid.width=520 |
| main | policy | classification_policy | core.note | 分類方針 | textarea | 520 |  | type=textarea / readonly=false / edit.visible=true / edit.readonly=false / search.visible=true / search.operator=contains | caption=分類方針 / grid.visible=false / grid.width=520 |
| main | policy | caption_policy | core.note | caption方針 | textarea | 520 |  | type=textarea / readonly=false / edit.visible=true / edit.readonly=false / search.visible=true / search.operator=contains | caption=caption方針 / grid.visible=false / grid.width=520 |

## 観点分類入りExpected定義

- view.id: main

### 概要

- section.id: summary
- type: form
- dataPath: $
- fields: 5

| field | caption | type | grid.visible | width | edit.visible | readonly | search | options |
| --- | --- | --- | --- | ---: | --- | --- | --- | --- |
| view_def | view_def | text | false |  | true | true |  |  |
| schema_version | Schema | text |  |  |  |  |  |  |
| document_type | 文書種別 | text |  |  |  |  |  |  |
| title | タイトル | text | false | 360 |  |  |  |  |
| description | 説明 | text | false | 420 |  |  |  |  |

### Expected / Check 一覧

- section.id: mainGrid
- type: grid
- dataPath: $.expected_checks
- fields: 11

| field | caption | type | grid.visible | width | edit.visible | readonly | search | options |
| --- | --- | --- | --- | ---: | --- | --- | --- | --- |
| check_id | チェックID | text |  |  |  |  |  |  |
| test_pattern_id | テストパターンID | text |  |  |  |  |  |  |
| title | タイトル | text |  | 360 |  |  |  |  |
| quality_axis_cd | 品質観点 | text |  |  |  |  |  |  |
| check_axis_cd | チェック観点 | text |  |  |  |  |  |  |
| risk_cd | リスク | text |  |  |  |  |  |  |
| source_check_name | 実チェック名 | text |  |  |  |  |  |  |
| expected_summary | 期待値概要 | text |  |  |  |  |  |  |
| constraint_ids | 制約ID | text |  |  |  |  |  |  |
| evidence_hint | 証跡ヒント | text |  |  |  |  |  |  |
| note | メモ | text |  | 260 |  |  |  |  |

### 運用方針

- section.id: policy
- type: form
- dataPath: $.policy
- fields: 3

| field | caption | type | grid.visible | width | edit.visible | readonly | search | options |
| --- | --- | --- | --- | ---: | --- | --- | --- | --- |
| test_pattern_policy | テストパターン方針 | text | false | 520 |  |  |  |  |
| classification_policy | 分類方針 | text | false | 520 |  |  |  |  |
| caption_policy | caption方針 | text | false | 520 |  |  |  |  |

---

## 解決済みViewDef概要

extends / fieldType を解決した、現在画面描画に使っているViewDefの概要です。

| View | View Caption | Section | Section Caption | Type | DataPath | KeyField | Fields |
| --- | --- | --- | --- | --- | --- | --- | ---: |
| main | 観点分類入りExpected定義 | summary | 概要 | form | $ |  | 5 |
| main | 観点分類入りExpected定義 | mainGrid | Expected / Check 一覧 | grid | $.expected_checks |  | 11 |
| main | 観点分類入りExpected定義 | policy | 運用方針 | form | $.policy |  | 3 |

## Resolved: 観点分類入りExpected定義

- view.id: main

### 概要

- section.id: summary
- type: form
- dataPath: $
- fields: 5

| field | caption | type | grid.visible | width | edit.visible | readonly | search | options |
| --- | --- | --- | --- | ---: | --- | --- | --- | --- |
| view_def | view_def | text | false |  | true | true |  |  |
| schema_version | Schema | text | true | 120 | true | false | true (contains) |  |
| document_type | 文書種別 | text | true | 170 | true | false | true (contains) |  |
| title | タイトル | text | false | 360 | true | false | true (contains) |  |
| description | 説明 | textarea | false | 420 | true | false | true (contains) |  |

### Expected / Check 一覧

- section.id: mainGrid
- type: grid
- dataPath: $.expected_checks
- fields: 11

| field | caption | type | grid.visible | width | edit.visible | readonly | search | options |
| --- | --- | --- | --- | ---: | --- | --- | --- | --- |
| check_id | チェックID | text | true | 170 | true | false | true (contains) |  |
| test_pattern_id | テストパターンID | text | true | 170 | true | false | true (contains) |  |
| title | タイトル | text | true | 360 | true | false | true (contains) |  |
| quality_axis_cd | 品質観点 | select | true | 120 | true |  | true (equals) | display:表示, operation:操作, save:保存, evidence:証跡, safety:安全性, error:エラー処理 |
| check_axis_cd | チェック観点 | select | true | 120 | true |  | true (equals) | include:採用確認, exclude:除外確認, structure:構造線確認, display:表示確認, write:書込確認, not_write:非書込確認, error:エラー確認 |
| risk_cd | リスク | select | true | 80 | true |  | true (equals) | high:高, medium:中, low:低 |
| source_check_name | 実チェック名 | text | true | 180 | true | false | true (contains) |  |
| expected_summary | 期待値概要 | textarea | true | 380 | true | false | true (contains) |  |
| constraint_ids | 制約ID | stringArray | true | 180 | true | false |  |  |
| evidence_hint | 証跡ヒント | textarea | true | 320 | true | false | true (contains) |  |
| note | メモ | textarea | true | 260 | true | false | true (contains) |  |

### 運用方針

- section.id: policy
- type: form
- dataPath: $.policy
- fields: 3

| field | caption | type | grid.visible | width | edit.visible | readonly | search | options |
| --- | --- | --- | --- | ---: | --- | --- | --- | --- |
| test_pattern_policy | テストパターン方針 | textarea | false | 520 | true | false | true (contains) |  |
| classification_policy | 分類方針 | textarea | false | 520 | true | false | true (contains) |  |
| caption_policy | caption方針 | textarea | false | 520 | true | false | true (contains) |  |

---

## ViewDef JSON

<details>
<summary>元ViewDef JSONを表示</summary>

```json
{
  "app": {
    "title": "QA Expected Checks Classified"
  },
  "fieldTypeSources": [
    "common_types_v0_1.json"
  ],
  "views": [
    {
      "id": "main",
      "caption": "観点分類入りExpected定義",
      "sections": [
        {
          "id": "summary",
          "type": "form",
          "caption": "概要",
          "dataPath": "$",
          "fields": [
            {
              "field": "view_def",
              "caption": "view_def",
              "type": "text",
              "grid": {
                "visible": false
              },
              "edit": {
                "visible": true,
                "readonly": true
              }
            },
            {
              "field": "schema_version",
              "caption": "Schema",
              "fieldType": "core.schema_version"
            },
            {
              "field": "document_type",
              "caption": "文書種別",
              "fieldType": "core.document_type"
            },
            {
              "field": "title",
              "caption": "タイトル",
              "fieldType": "core.title",
              "grid": {
                "visible": false,
                "width": 360
              }
            },
            {
              "field": "description",
              "caption": "説明",
              "fieldType": "core.note",
              "grid": {
                "visible": false,
                "width": 420
              }
            }
          ]
        },
        {
          "id": "mainGrid",
          "type": "grid",
          "caption": "Expected / Check 一覧",
          "dataPath": "$.expected_checks",
          "fields": [
            {
              "field": "check_id",
              "caption": "チェックID",
              "fieldType": "qa.check_id"
            },
            {
              "field": "test_pattern_id",
              "caption": "テストパターンID",
              "fieldType": "qa.test_pattern_id"
            },
            {
              "field": "title",
              "caption": "タイトル",
              "fieldType": "core.title",
              "grid": {
                "width": 360
              }
            },
            {
              "field": "quality_axis_cd",
              "caption": "品質観点",
              "fieldType": "qa.quality_axis"
            },
            {
              "field": "check_axis_cd",
              "caption": "チェック観点",
              "fieldType": "qa.check_axis"
            },
            {
              "field": "risk_cd",
              "caption": "リスク",
              "fieldType": "qa.risk"
            },
            {
              "field": "source_check_name",
              "caption": "実チェック名",
              "fieldType": "qa.source_check_name"
            },
            {
              "field": "expected_summary",
              "caption": "期待値概要",
              "fieldType": "qa.expected_summary"
            },
            {
              "field": "constraint_ids",
              "caption": "制約ID",
              "fieldType": "qa.constraint_ids"
            },
            {
              "field": "evidence_hint",
              "caption": "証跡ヒント",
              "fieldType": "qa.evidence_hint"
            },
            {
              "field": "note",
              "caption": "メモ",
              "fieldType": "core.note",
              "grid": {
                "width": 260
              }
            }
          ]
        },
        {
          "id": "policy",
          "type": "form",
          "caption": "運用方針",
          "dataPath": "$.policy",
          "fields": [
            {
              "field": "test_pattern_policy",
              "caption": "テストパターン方針",
              "fieldType": "core.note",
              "grid": {
                "visible": false,
                "width": 520
              }
            },
            {
              "field": "classification_policy",
              "caption": "分類方針",
              "fieldType": "core.note",
              "grid": {
                "visible": false,
                "width": 520
              }
            },
            {
              "field": "caption_policy",
              "caption": "caption方針",
              "fieldType": "core.note",
              "grid": {
                "visible": false,
                "width": 520
              }
            }
          ]
        }
      ]
    }
  ]
}
```

</details>

<details open>
<summary>解決済みViewDef JSONを表示</summary>

```json
{
  "app": {
    "title": "QA Expected Checks Classified"
  },
  "fieldTypeSources": [
    "common_types_v0_1.json"
  ],
  "views": [
    {
      "id": "main",
      "caption": "観点分類入りExpected定義",
      "sections": [
        {
          "id": "summary",
          "type": "form",
          "caption": "概要",
          "dataPath": "$",
          "fields": [
            {
              "field": "view_def",
              "caption": "view_def",
              "type": "text",
              "grid": {
                "visible": false
              },
              "edit": {
                "visible": true,
                "readonly": true
              }
            },
            {
              "caption": "Schema",
              "grid": {
                "visible": true,
                "width": 120
              },
              "edit": {
                "visible": true,
                "readonly": false
              },
              "search": {
                "visible": true,
                "operator": "contains"
              },
              "readonly": false,
              "type": "text",
              "field": "schema_version",
              "fieldType": "core.schema_version"
            },
            {
              "caption": "文書種別",
              "grid": {
                "visible": true,
                "width": 170
              },
              "edit": {
                "visible": true,
                "readonly": false
              },
              "search": {
                "visible": true,
                "operator": "contains"
              },
              "readonly": false,
              "type": "text",
              "field": "document_type",
              "fieldType": "core.document_type"
            },
            {
              "caption": "タイトル",
              "grid": {
                "visible": false,
                "width": 360
              },
              "edit": {
                "visible": true,
                "readonly": false
              },
              "search": {
                "visible": true,
                "operator": "contains"
              },
              "readonly": false,
              "type": "text",
              "field": "title",
              "fieldType": "core.title"
            },
            {
              "caption": "説明",
              "grid": {
                "visible": false,
                "width": 420
              },
              "edit": {
                "visible": true,
                "readonly": false
              },
              "search": {
                "visible": true,
                "operator": "contains"
              },
              "readonly": false,
              "type": "textarea",
              "field": "description",
              "fieldType": "core.note"
            }
          ]
        },
        {
          "id": "mainGrid",
          "type": "grid",
          "caption": "Expected / Check 一覧",
          "dataPath": "$.expected_checks",
          "fields": [
            {
              "caption": "チェックID",
              "grid": {
                "visible": true,
                "width": 170
              },
              "edit": {
                "visible": true,
                "readonly": false
              },
              "search": {
                "visible": true,
                "operator": "contains"
              },
              "readonly": false,
              "type": "text",
              "field": "check_id",
              "fieldType": "qa.check_id"
            },
            {
              "caption": "テストパターンID",
              "grid": {
                "visible": true,
                "width": 170
              },
              "edit": {
                "visible": true,
                "readonly": false
              },
              "search": {
                "visible": true,
                "operator": "contains"
              },
              "readonly": false,
              "type": "text",
              "field": "test_pattern_id",
              "fieldType": "qa.test_pattern_id"
            },
            {
              "caption": "タイトル",
              "grid": {
                "visible": true,
                "width": 360
              },
              "edit": {
                "visible": true,
                "readonly": false
              },
              "search": {
                "visible": true,
                "operator": "contains"
              },
              "readonly": false,
              "type": "text",
              "field": "title",
              "fieldType": "core.title"
            },
            {
              "caption": "品質観点",
              "valueField": "cd",
              "labelField": "name",
              "options": [
                {
                  "cd": "display",
                  "name": "表示"
                },
                {
                  "cd": "operation",
                  "name": "操作"
                },
                {
                  "cd": "save",
                  "name": "保存"
                },
                {
                  "cd": "evidence",
                  "name": "証跡"
                },
                {
                  "cd": "safety",
                  "name": "安全性"
                },
                {
                  "cd": "error",
                  "name": "エラー処理"
                }
              ],
              "grid": {
                "visible": true,
                "width": 120
              },
              "edit": {
                "visible": true
              },
              "search": {
                "visible": true,
                "operator": "equals"
              },
              "type": "select",
              "field": "quality_axis_cd",
              "fieldType": "qa.quality_axis"
            },
            {
              "caption": "チェック観点",
              "valueField": "cd",
              "labelField": "name",
              "options": [
                {
                  "cd": "include",
                  "name": "採用確認"
                },
                {
                  "cd": "exclude",
                  "name": "除外確認"
                },
                {
                  "cd": "structure",
                  "name": "構造線確認"
                },
                {
                  "cd": "display",
                  "name": "表示確認"
                },
                {
                  "cd": "write",
                  "name": "書込確認"
                },
                {
                  "cd": "not_write",
                  "name": "非書込確認"
                },
                {
                  "cd": "error",
                  "name": "エラー確認"
                }
              ],
              "grid": {
                "visible": true,
                "width": 120
              },
              "edit": {
                "visible": true
              },
              "search": {
                "visible": true,
                "operator": "equals"
              },
              "type": "select",
              "field": "check_axis_cd",
              "fieldType": "qa.check_axis"
            },
            {
              "caption": "リスク",
              "valueField": "cd",
              "labelField": "name",
              "options": [
                {
                  "cd": "high",
                  "name": "高"
                },
                {
                  "cd": "medium",
                  "name": "中"
                },
                {
                  "cd": "low",
                  "name": "低"
                }
              ],
              "grid": {
                "visible": true,
                "width": 80
              },
              "edit": {
                "visible": true
              },
              "search": {
                "visible": true,
                "operator": "equals"
              },
              "type": "select",
              "field": "risk_cd",
              "fieldType": "qa.risk"
            },
            {
              "caption": "実チェック名",
              "grid": {
                "visible": true,
                "width": 180
              },
              "edit": {
                "visible": true,
                "readonly": false
              },
              "search": {
                "visible": true,
                "operator": "contains"
              },
              "readonly": false,
              "type": "text",
              "field": "source_check_name",
              "fieldType": "qa.source_check_name"
            },
            {
              "caption": "期待値概要",
              "grid": {
                "visible": true,
                "width": 380
              },
              "edit": {
                "visible": true,
                "readonly": false,
                "height": 90
              },
              "search": {
                "visible": true,
                "operator": "contains"
              },
              "readonly": false,
              "type": "textarea",
              "field": "expected_summary",
              "fieldType": "qa.expected_summary"
            },
            {
              "caption": "制約ID",
              "grid": {
                "visible": true,
                "width": 180
              },
              "edit": {
                "visible": true,
                "readonly": false
              },
              "readonly": false,
              "type": "stringArray",
              "field": "constraint_ids",
              "fieldType": "qa.constraint_ids"
            },
            {
              "caption": "証跡ヒント",
              "grid": {
                "visible": true,
                "width": 320
              },
              "edit": {
                "visible": true,
                "readonly": false,
                "height": 90
              },
              "search": {
                "visible": true,
                "operator": "contains"
              },
              "readonly": false,
              "type": "textarea",
              "field": "evidence_hint",
              "fieldType": "qa.evidence_hint"
            },
            {
              "caption": "メモ",
              "grid": {
                "visible": true,
                "width": 260
              },
              "edit": {
                "visible": true,
                "readonly": false
              },
              "search": {
                "visible": true,
                "operator": "contains"
              },
              "readonly": false,
              "type": "textarea",
              "field": "note",
              "fieldType": "core.note"
            }
          ]
        },
        {
          "id": "policy",
          "type": "form",
          "caption": "運用方針",
          "dataPath": "$.policy",
          "fields": [
            {
              "caption": "テストパターン方針",
              "grid": {
                "visible": false,
                "width": 520
              },
              "edit": {
                "visible": true,
                "readonly": false
              },
              "search": {
                "visible": true,
                "operator": "contains"
              },
              "readonly": false,
              "type": "textarea",
              "field": "test_pattern_policy",
              "fieldType": "core.note"
            },
            {
              "caption": "分類方針",
              "grid": {
                "visible": false,
                "width": 520
              },
              "edit": {
                "visible": true,
                "readonly": false
              },
              "search": {
                "visible": true,
                "operator": "contains"
              },
              "readonly": false,
              "type": "textarea",
              "field": "classification_policy",
              "fieldType": "core.note"
            },
            {
              "caption": "caption方針",
              "grid": {
                "visible": false,
                "width": 520
              },
              "edit": {
                "visible": true,
                "readonly": false
              },
              "search": {
                "visible": true,
                "operator": "contains"
              },
              "readonly": false,
              "type": "textarea",
              "field": "caption_policy",
              "fieldType": "core.note"
            }
          ]
        }
      ]
    }
  ],
  "_resolved_common_types": [
    "qa",
    "relation",
    "business",
    "core"
  ]
}
```

</details>