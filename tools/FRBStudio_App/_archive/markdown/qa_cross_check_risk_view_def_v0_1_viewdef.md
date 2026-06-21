# ViewDef定義レポート — チェック観点 × リスク

## 基本情報
- 出力日時: 2026/6/20 20:12:44
- 対象ViewDef: qa_cross_check_risk_view_def_v0_1.json
- views: 1

## View / Section 概要
| View | View Caption | Section | Section Caption | Type | DataPath | KeyField | Fields |
| --- | --- | --- | --- | --- | --- | --- | ---: |
| main | チェック観点 × リスク | summary | 概要 | form | $ |  | 3 |
| main | チェック観点 × リスク | mainGrid | チェック観点 × リスク | grid | $.check_risk_cross |  | 10 |

## 継承差分サマリ

このViewDefは extends を持たないため、継承差分はありません。

## 解決サマリ

- 読込済み共通Type namespace: qa / relation / business / core
- fieldType参照: 12件
- fieldType caption未指定: 0件
- 制約: fieldType を使う field でも、元ViewDef側に caption を明示することを推奨します。ViewDef側 caption が Common 側 caption より優先されます。
- 見方: 「Common由来候補」は元ViewDefに書かれておらず、解決後に現れた項目です。

| View | Section | field | fieldType | caption | type | width | options | Common由来候補 | ViewDef個別指定 |
| --- | --- | --- | --- | --- | --- | ---: | --- | --- | --- |
| main | summary | title | core.title | タイトル | text | 360 |  | type=text / readonly=false / edit.visible=true / edit.readonly=false / search.visible=true / search.operator=contains | caption=タイトル / grid.visible=false / grid.width=360 |
| main | summary | description | core.note | 説明 | textarea | 420 |  | type=textarea / readonly=false / edit.visible=true / edit.readonly=false / search.visible=true / search.operator=contains | caption=説明 / grid.visible=false / grid.width=420 |
| main | mainGrid | check_axis_cd | qa.check_axis | チェック観点CD | select | 120 | 7件 | type=select / grid.visible=true / edit.visible=true / search.visible=true / search.operator=equals / options=[7件] | caption=チェック観点CD / grid.width=120 |
| main | mainGrid | check_axis_name | qa.check_axis_name | チェック観点名 | text | 130 |  | type=text / grid.visible=true / grid.width=130 / edit.visible=true / edit.readonly=true / search.visible=true / ... +1 | caption=チェック観点名 |
| main | mainGrid | risk_cd | qa.risk | リスクCD | select | 80 | 3件 | type=select / grid.visible=true / edit.visible=true / search.visible=true / search.operator=equals / options=[3件] | caption=リスクCD / grid.width=80 |
| main | mainGrid | risk_name | qa.risk_name | リスク名 | text | 90 |  | type=text / grid.visible=true / grid.width=90 / edit.visible=true / edit.readonly=true / search.visible=true / ... +1 | caption=リスク名 |
| main | mainGrid | check_count | qa.check_count | チェック件数 | number | 90 |  | type=number / grid.visible=true / grid.width=90 / edit.visible=true / edit.readonly=true / search.visible=true / ... +1 | caption=チェック件数 |
| main | mainGrid | high_count | qa.high_count | 高リスク件数 | number | 110 |  | type=number / grid.visible=true / grid.width=110 / edit.visible=true / edit.readonly=true / search.visible=true / ... +1 | caption=高リスク件数 |
| main | mainGrid | medium_count | qa.medium_count | 中リスク件数 | number | 110 |  | type=number / grid.visible=true / grid.width=110 / edit.visible=true / edit.readonly=true / search.visible=true / ... +1 | caption=中リスク件数 |
| main | mainGrid | low_count | qa.low_count | 低リスク件数 | number | 110 |  | type=number / grid.visible=true / grid.width=110 / edit.visible=true / edit.readonly=true / search.visible=true / ... +1 | caption=低リスク件数 |
| main | mainGrid | risk_summary | qa.risk_summary | リスク内訳 | text | 150 |  | type=text / grid.visible=true / grid.width=150 / edit.visible=true / edit.readonly=true / search.visible=true / ... +1 | caption=リスク内訳 |
| main | mainGrid | check_ids | qa.check_ids | チェックID一覧 | stringArray | 260 |  | type=stringArray / grid.visible=true / grid.width=260 / edit.visible=true / edit.readonly=true / search.visible=true / ... +1 | caption=チェックID一覧 |

## チェック観点 × リスク

- view.id: main

### 概要

- section.id: summary
- type: form
- dataPath: $
- fields: 3

| field | caption | type | grid.visible | width | edit.visible | readonly | search | options |
| --- | --- | --- | --- | ---: | --- | --- | --- | --- |
| view_def | view_def | text | false |  | true | true |  |  |
| title | タイトル | text | false | 360 |  |  |  |  |
| description | 説明 | text | false | 420 |  |  |  |  |

### チェック観点 × リスク

- section.id: mainGrid
- type: grid
- dataPath: $.check_risk_cross
- fields: 10

| field | caption | type | grid.visible | width | edit.visible | readonly | search | options |
| --- | --- | --- | --- | ---: | --- | --- | --- | --- |
| check_axis_cd | チェック観点CD | text |  | 120 |  |  |  |  |
| check_axis_name | チェック観点名 | text |  |  |  |  |  |  |
| risk_cd | リスクCD | text |  | 80 |  |  |  |  |
| risk_name | リスク名 | text |  |  |  |  |  |  |
| check_count | チェック件数 | text |  |  |  |  |  |  |
| high_count | 高リスク件数 | text |  |  |  |  |  |  |
| medium_count | 中リスク件数 | text |  |  |  |  |  |  |
| low_count | 低リスク件数 | text |  |  |  |  |  |  |
| risk_summary | リスク内訳 | text |  |  |  |  |  |  |
| check_ids | チェックID一覧 | text |  |  |  |  |  |  |

---

## 解決済みViewDef概要

extends / fieldType を解決した、現在画面描画に使っているViewDefの概要です。

| View | View Caption | Section | Section Caption | Type | DataPath | KeyField | Fields |
| --- | --- | --- | --- | --- | --- | --- | ---: |
| main | チェック観点 × リスク | summary | 概要 | form | $ |  | 3 |
| main | チェック観点 × リスク | mainGrid | チェック観点 × リスク | grid | $.check_risk_cross |  | 10 |

## Resolved: チェック観点 × リスク

- view.id: main

### 概要

- section.id: summary
- type: form
- dataPath: $
- fields: 3

| field | caption | type | grid.visible | width | edit.visible | readonly | search | options |
| --- | --- | --- | --- | ---: | --- | --- | --- | --- |
| view_def | view_def | text | false |  | true | true |  |  |
| title | タイトル | text | false | 360 | true | false | true (contains) |  |
| description | 説明 | textarea | false | 420 | true | false | true (contains) |  |

### チェック観点 × リスク

- section.id: mainGrid
- type: grid
- dataPath: $.check_risk_cross
- fields: 10

| field | caption | type | grid.visible | width | edit.visible | readonly | search | options |
| --- | --- | --- | --- | ---: | --- | --- | --- | --- |
| check_axis_cd | チェック観点CD | select | true | 120 | true |  | true (equals) | include:採用確認, exclude:除外確認, structure:構造線確認, display:表示確認, write:書込確認, not_write:非書込確認, error:エラー確認 |
| check_axis_name | チェック観点名 | text | true | 130 | true | true | true (contains) |  |
| risk_cd | リスクCD | select | true | 80 | true |  | true (equals) | high:高, medium:中, low:低 |
| risk_name | リスク名 | text | true | 90 | true | true | true (contains) |  |
| check_count | チェック件数 | number | true | 90 | true | true | true (gte) |  |
| high_count | 高リスク件数 | number | true | 110 | true | true | true (gte) |  |
| medium_count | 中リスク件数 | number | true | 110 | true | true | true (gte) |  |
| low_count | 低リスク件数 | number | true | 110 | true | true | true (gte) |  |
| risk_summary | リスク内訳 | text | true | 150 | true | true | true (contains) |  |
| check_ids | チェックID一覧 | stringArray | true | 260 | true | true | true (contains) |  |

---

## ViewDef JSON

<details>
<summary>元ViewDef JSONを表示</summary>

```json
{
  "app": {
    "title": "QA Cross CheckAxis x Risk"
  },
  "fieldTypeSources": [
    "common_types_v0_1.json"
  ],
  "virtualData": [
    {
      "builder": "expected_check_cross_counts",
      "targetPath": "$.check_risk_cross",
      "source": {
        "source": "$current",
        "path": "$.expected_checks"
      },
      "dimensions": [
        {
          "field": "check_axis_cd",
          "outputField": "check_axis_cd",
          "labelField": "check_axis_name",
          "labelMap": {
            "include": "採用確認",
            "exclude": "除外確認",
            "structure": "構造線確認",
            "display": "表示確認",
            "write": "書込確認",
            "not_write": "非書込確認",
            "error": "エラー確認"
          }
        },
        {
          "field": "risk_cd",
          "outputField": "risk_cd",
          "labelField": "risk_name",
          "labelMap": {
            "high": "高",
            "medium": "中",
            "low": "低"
          }
        }
      ],
      "outputs": {
        "countField": "check_count",
        "highCountField": "high_count",
        "mediumCountField": "medium_count",
        "lowCountField": "low_count",
        "checkIdsField": "check_ids",
        "testPatternIdsField": "test_pattern_ids",
        "constraintIdsField": "constraint_ids",
        "riskSummaryField": "risk_summary"
      },
      "sort": [
        {
          "field": "check_axis_cd",
          "direction": "asc"
        },
        {
          "field": "risk_cd",
          "direction": "asc"
        }
      ]
    }
  ],
  "views": [
    {
      "id": "main",
      "caption": "チェック観点 × リスク",
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
          "caption": "チェック観点 × リスク",
          "dataPath": "$.check_risk_cross",
          "fields": [
            {
              "field": "check_axis_cd",
              "caption": "チェック観点CD",
              "fieldType": "qa.check_axis",
              "grid": {
                "width": 120
              }
            },
            {
              "field": "check_axis_name",
              "caption": "チェック観点名",
              "fieldType": "qa.check_axis_name"
            },
            {
              "field": "risk_cd",
              "caption": "リスクCD",
              "fieldType": "qa.risk",
              "grid": {
                "width": 80
              }
            },
            {
              "field": "risk_name",
              "caption": "リスク名",
              "fieldType": "qa.risk_name"
            },
            {
              "field": "check_count",
              "caption": "チェック件数",
              "fieldType": "qa.check_count"
            },
            {
              "field": "high_count",
              "caption": "高リスク件数",
              "fieldType": "qa.high_count"
            },
            {
              "field": "medium_count",
              "caption": "中リスク件数",
              "fieldType": "qa.medium_count"
            },
            {
              "field": "low_count",
              "caption": "低リスク件数",
              "fieldType": "qa.low_count"
            },
            {
              "field": "risk_summary",
              "caption": "リスク内訳",
              "fieldType": "qa.risk_summary"
            },
            {
              "field": "check_ids",
              "caption": "チェックID一覧",
              "fieldType": "qa.check_ids"
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
    "title": "QA Cross CheckAxis x Risk"
  },
  "fieldTypeSources": [
    "common_types_v0_1.json"
  ],
  "virtualData": [
    {
      "builder": "expected_check_cross_counts",
      "targetPath": "$.check_risk_cross",
      "source": {
        "source": "$current",
        "path": "$.expected_checks"
      },
      "dimensions": [
        {
          "field": "check_axis_cd",
          "outputField": "check_axis_cd",
          "labelField": "check_axis_name",
          "labelMap": {
            "include": "採用確認",
            "exclude": "除外確認",
            "structure": "構造線確認",
            "display": "表示確認",
            "write": "書込確認",
            "not_write": "非書込確認",
            "error": "エラー確認"
          }
        },
        {
          "field": "risk_cd",
          "outputField": "risk_cd",
          "labelField": "risk_name",
          "labelMap": {
            "high": "高",
            "medium": "中",
            "low": "低"
          }
        }
      ],
      "outputs": {
        "countField": "check_count",
        "highCountField": "high_count",
        "mediumCountField": "medium_count",
        "lowCountField": "low_count",
        "checkIdsField": "check_ids",
        "testPatternIdsField": "test_pattern_ids",
        "constraintIdsField": "constraint_ids",
        "riskSummaryField": "risk_summary"
      },
      "sort": [
        {
          "field": "check_axis_cd",
          "direction": "asc"
        },
        {
          "field": "risk_cd",
          "direction": "asc"
        }
      ]
    }
  ],
  "views": [
    {
      "id": "main",
      "caption": "チェック観点 × リスク",
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
          "caption": "チェック観点 × リスク",
          "dataPath": "$.check_risk_cross",
          "fields": [
            {
              "caption": "チェック観点CD",
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
              "caption": "チェック観点名",
              "grid": {
                "visible": true,
                "width": 130
              },
              "edit": {
                "visible": true,
                "readonly": true
              },
              "search": {
                "visible": true,
                "operator": "contains"
              },
              "type": "text",
              "field": "check_axis_name",
              "fieldType": "qa.check_axis_name"
            },
            {
              "caption": "リスクCD",
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
              "caption": "リスク名",
              "grid": {
                "visible": true,
                "width": 90
              },
              "edit": {
                "visible": true,
                "readonly": true
              },
              "search": {
                "visible": true,
                "operator": "contains"
              },
              "type": "text",
              "field": "risk_name",
              "fieldType": "qa.risk_name"
            },
            {
              "caption": "チェック件数",
              "grid": {
                "visible": true,
                "width": 90
              },
              "edit": {
                "visible": true,
                "readonly": true
              },
              "search": {
                "visible": true,
                "operator": "gte"
              },
              "type": "number",
              "field": "check_count",
              "fieldType": "qa.check_count"
            },
            {
              "caption": "高リスク件数",
              "grid": {
                "visible": true,
                "width": 110
              },
              "edit": {
                "visible": true,
                "readonly": true
              },
              "search": {
                "visible": true,
                "operator": "gte"
              },
              "type": "number",
              "field": "high_count",
              "fieldType": "qa.high_count"
            },
            {
              "caption": "中リスク件数",
              "grid": {
                "visible": true,
                "width": 110
              },
              "edit": {
                "visible": true,
                "readonly": true
              },
              "search": {
                "visible": true,
                "operator": "gte"
              },
              "type": "number",
              "field": "medium_count",
              "fieldType": "qa.medium_count"
            },
            {
              "caption": "低リスク件数",
              "grid": {
                "visible": true,
                "width": 110
              },
              "edit": {
                "visible": true,
                "readonly": true
              },
              "search": {
                "visible": true,
                "operator": "gte"
              },
              "type": "number",
              "field": "low_count",
              "fieldType": "qa.low_count"
            },
            {
              "caption": "リスク内訳",
              "grid": {
                "visible": true,
                "width": 150
              },
              "edit": {
                "visible": true,
                "readonly": true
              },
              "search": {
                "visible": true,
                "operator": "contains"
              },
              "type": "text",
              "field": "risk_summary",
              "fieldType": "qa.risk_summary"
            },
            {
              "caption": "チェックID一覧",
              "grid": {
                "visible": true,
                "width": 260
              },
              "edit": {
                "visible": true,
                "readonly": true
              },
              "search": {
                "visible": true,
                "operator": "contains"
              },
              "type": "stringArray",
              "field": "check_ids",
              "fieldType": "qa.check_ids"
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