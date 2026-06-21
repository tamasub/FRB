# ViewDef定義レポート — 期待値チェック分類サンプル

## 基本情報
- 出力日時: 2026/6/20 19:42:06
- 対象ViewDef: qa_expected_checks_sample_view_def_v0_1.json
- views: 1

## View / Section 概要
| View | View Caption | Section | Section Caption | Type | DataPath | KeyField | Fields |
| --- | --- | --- | --- | --- | --- | --- | ---: |
| main | 期待値チェック分類サンプル | summary | 概要 | form | $ |  | 1 |
| main | 期待値チェック分類サンプル | mainGrid | 期待値チェック | grid | $.expected_checks |  | 8 |

## 継承差分サマリ

このViewDefは extends を持たないため、継承差分はありません。

## 解決サマリ

- 読込済み共通Type namespace: qa / relation / business / core
- fieldType参照: 3件
- fieldType caption未指定: 0件
- 制約: fieldType を使う field でも、元ViewDef側に caption を明示することを推奨します。ViewDef側 caption が Common 側 caption より優先されます。
- 見方: 「Common由来候補」は元ViewDefに書かれておらず、解決後に現れた項目です。

| View | Section | field | fieldType | caption | type | width | options | Common由来候補 | ViewDef個別指定 |
| --- | --- | --- | --- | --- | --- | ---: | --- | --- | --- |
| main | mainGrid | quality_axis_cd | qa.quality_axis | 品質観点 | select | 120 | 6件 | type=select / grid.visible=true / grid.width=120 / edit.visible=true / search.visible=true / search.operator=equals / ... +1 | caption=品質観点 |
| main | mainGrid | check_axis_cd | qa.check_axis | チェック観点 | select | 120 | 7件 | type=select / grid.visible=true / grid.width=120 / edit.visible=true / search.visible=true / search.operator=equals / ... +1 | caption=チェック観点 |
| main | mainGrid | risk_cd | qa.risk | リスク | select | 80 | 3件 | type=select / grid.visible=true / grid.width=80 / edit.visible=true / search.visible=true / search.operator=equals / ... +1 | caption=リスク |

## 期待値チェック分類サンプル

- view.id: main

### 概要

- section.id: summary
- type: form
- dataPath: $
- fields: 1

| field | caption | type | grid.visible | width | edit.visible | readonly | search | options |
| --- | --- | --- | --- | ---: | --- | --- | --- | --- |
| view_def | view_def | text | false |  | true | true |  |  |

### 期待値チェック

- section.id: mainGrid
- type: grid
- dataPath: $.expected_checks
- fields: 8

| field | caption | type | grid.visible | width | edit.visible | readonly | search | options |
| --- | --- | --- | --- | ---: | --- | --- | --- | --- |
| check_id | チェックID | text | true | 170 | true |  | true (contains) |  |
| test_pattern_id | テストパターンID | text | true | 170 | true |  | true (contains) |  |
| title | タイトル | text | true | 360 | true |  | true (contains) |  |
| quality_axis_cd | 品質観点 | text |  |  |  |  |  |  |
| check_axis_cd | チェック観点 | text |  |  |  |  |  |  |
| risk_cd | リスク | text |  |  |  |  |  |  |
| expected_summary | 期待値概要 | textarea | true | 360 | true |  | true (contains) |  |
| constraint_ids | 制約ID | stringArray | true | 180 | true |  |  |  |

---

## 解決済みViewDef概要

extends / fieldType を解決した、現在画面描画に使っているViewDefの概要です。

| View | View Caption | Section | Section Caption | Type | DataPath | KeyField | Fields |
| --- | --- | --- | --- | --- | --- | --- | ---: |
| main | 期待値チェック分類サンプル | summary | 概要 | form | $ |  | 1 |
| main | 期待値チェック分類サンプル | mainGrid | 期待値チェック | grid | $.expected_checks |  | 8 |

## Resolved: 期待値チェック分類サンプル

- view.id: main

### 概要

- section.id: summary
- type: form
- dataPath: $
- fields: 1

| field | caption | type | grid.visible | width | edit.visible | readonly | search | options |
| --- | --- | --- | --- | ---: | --- | --- | --- | --- |
| view_def | view_def | text | false |  | true | true |  |  |

### 期待値チェック

- section.id: mainGrid
- type: grid
- dataPath: $.expected_checks
- fields: 8

| field | caption | type | grid.visible | width | edit.visible | readonly | search | options |
| --- | --- | --- | --- | ---: | --- | --- | --- | --- |
| check_id | チェックID | text | true | 170 | true |  | true (contains) |  |
| test_pattern_id | テストパターンID | text | true | 170 | true |  | true (contains) |  |
| title | タイトル | text | true | 360 | true |  | true (contains) |  |
| quality_axis_cd | 品質観点 | select | true | 120 | true |  | true (equals) | display:表示, operation:操作, save:保存, evidence:証跡, safety:安全性, error:エラー処理 |
| check_axis_cd | チェック観点 | select | true | 120 | true |  | true (equals) | include:採用確認, exclude:除外確認, structure:構造線確認, display:表示確認, write:書込確認, not_write:非書込確認, error:エラー確認 |
| risk_cd | リスク | select | true | 80 | true |  | true (equals) | high:高, medium:中, low:低 |
| expected_summary | 期待値概要 | textarea | true | 360 | true |  | true (contains) |  |
| constraint_ids | 制約ID | stringArray | true | 180 | true |  |  |  |

---

## ViewDef JSON

<details>
<summary>元ViewDef JSONを表示</summary>

```json
{
  "app": {
    "title": "QA Expected Checks Sample"
  },
  "fieldTypeSources": [
    "common_types_v0_1.json"
  ],
  "views": [
    {
      "id": "main",
      "caption": "期待値チェック分類サンプル",
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
            }
          ]
        },
        {
          "id": "mainGrid",
          "type": "grid",
          "caption": "期待値チェック",
          "dataPath": "$.expected_checks",
          "fields": [
            {
              "field": "check_id",
              "caption": "チェックID",
              "type": "text",
              "grid": {
                "visible": true,
                "width": 170
              },
              "edit": {
                "visible": true
              },
              "search": {
                "visible": true,
                "operator": "contains"
              }
            },
            {
              "field": "test_pattern_id",
              "caption": "テストパターンID",
              "type": "text",
              "grid": {
                "visible": true,
                "width": 170
              },
              "edit": {
                "visible": true
              },
              "search": {
                "visible": true,
                "operator": "contains"
              }
            },
            {
              "field": "title",
              "caption": "タイトル",
              "type": "text",
              "grid": {
                "visible": true,
                "width": 360
              },
              "edit": {
                "visible": true
              },
              "search": {
                "visible": true,
                "operator": "contains"
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
              "field": "expected_summary",
              "caption": "期待値概要",
              "type": "textarea",
              "grid": {
                "visible": true,
                "width": 360
              },
              "edit": {
                "visible": true,
                "height": 90
              },
              "search": {
                "visible": true,
                "operator": "contains"
              }
            },
            {
              "field": "constraint_ids",
              "caption": "制約ID",
              "type": "stringArray",
              "grid": {
                "visible": true,
                "width": 180
              },
              "edit": {
                "visible": true
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
    "title": "QA Expected Checks Sample"
  },
  "fieldTypeSources": [
    "common_types_v0_1.json"
  ],
  "views": [
    {
      "id": "main",
      "caption": "期待値チェック分類サンプル",
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
            }
          ]
        },
        {
          "id": "mainGrid",
          "type": "grid",
          "caption": "期待値チェック",
          "dataPath": "$.expected_checks",
          "fields": [
            {
              "field": "check_id",
              "caption": "チェックID",
              "type": "text",
              "grid": {
                "visible": true,
                "width": 170
              },
              "edit": {
                "visible": true
              },
              "search": {
                "visible": true,
                "operator": "contains"
              }
            },
            {
              "field": "test_pattern_id",
              "caption": "テストパターンID",
              "type": "text",
              "grid": {
                "visible": true,
                "width": 170
              },
              "edit": {
                "visible": true
              },
              "search": {
                "visible": true,
                "operator": "contains"
              }
            },
            {
              "field": "title",
              "caption": "タイトル",
              "type": "text",
              "grid": {
                "visible": true,
                "width": 360
              },
              "edit": {
                "visible": true
              },
              "search": {
                "visible": true,
                "operator": "contains"
              }
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
              "field": "expected_summary",
              "caption": "期待値概要",
              "type": "textarea",
              "grid": {
                "visible": true,
                "width": 360
              },
              "edit": {
                "visible": true,
                "height": 90
              },
              "search": {
                "visible": true,
                "operator": "contains"
              }
            },
            {
              "field": "constraint_ids",
              "caption": "制約ID",
              "type": "stringArray",
              "grid": {
                "visible": true,
                "width": 180
              },
              "edit": {
                "visible": true
              }
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