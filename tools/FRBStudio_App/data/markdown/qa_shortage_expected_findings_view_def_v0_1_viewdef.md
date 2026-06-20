# ViewDef定義レポート — Expected 不足検出

## 基本情報
- 出力日時: 2026/6/20 20:35:25
- 対象ViewDef: qa_shortage_expected_findings_view_def_v0_1.json
- views: 1

## View / Section 概要
| View | View Caption | Section | Section Caption | Type | DataPath | KeyField | Fields |
| --- | --- | --- | --- | --- | --- | --- | ---: |
| main | Expected 不足検出 | summary | 概要 | form | $ |  | 3 |
| main | Expected 不足検出 | mainGrid | 不足検出一覧 | grid | $.expected_shortage_findings |  | 16 |

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
| main | summary | title | core.title | タイトル | text | 360 |  | type=text / readonly=false / edit.visible=true / edit.readonly=false / search.visible=true / search.operator=contains | caption=タイトル / grid.visible=false / grid.width=360 |
| main | summary | description | core.note | 説明 | textarea | 420 |  | type=textarea / readonly=false / edit.visible=true / edit.readonly=false / search.visible=true / search.operator=contains | caption=説明 / grid.visible=false / grid.width=420 |
| main | mainGrid | finding_id | qa.finding_id | 不足ID | text | 100 |  | type=text / grid.visible=true / grid.width=100 / edit.visible=true / edit.readonly=true / search.visible=true / ... +1 | caption=不足ID |
| main | mainGrid | severity_cd | qa.severity | 重要度CD | select | 90 | 4件 | type=select / grid.visible=true / edit.visible=true / search.visible=true / search.operator=equals / options=[4件] | caption=重要度CD / grid.width=90 |
| main | mainGrid | severity_name | qa.severity_name | 重要度 | text | 80 |  | type=text / grid.visible=true / edit.visible=true / edit.readonly=false / search.visible=true / search.operator=contains | caption=重要度 / grid.width=80 |
| main | mainGrid | finding_type_name | qa.finding_type_name | 検出種別 | text | 150 |  | type=text / grid.visible=true / edit.visible=true / edit.readonly=false / search.visible=true / search.operator=contains | caption=検出種別 / grid.width=150 |
| main | mainGrid | target_type_name | qa.target_type_name | 対象種別 | text | 120 |  | type=text / grid.visible=true / edit.visible=true / edit.readonly=false / search.visible=true / search.operator=contains | caption=対象種別 / grid.width=120 |
| main | mainGrid | target_cd | qa.target_cd | 対象CD | text | 170 |  | type=text / grid.visible=true / edit.visible=true / edit.readonly=false / search.visible=true / search.operator=contains | caption=対象CD / grid.width=170 |
| main | mainGrid | target_name | qa.target_name | 対象名 | text | 180 |  | type=text / grid.visible=true / edit.visible=true / edit.readonly=false / search.visible=true / search.operator=contains | caption=対象名 / grid.width=180 |
| main | mainGrid | risk_name | qa.risk_name | リスク | text | 80 |  | type=text / grid.visible=true / edit.visible=true / edit.readonly=true / search.visible=true / search.operator=contains | caption=リスク / grid.width=80 |
| main | mainGrid | check_count | qa.check_count | チェック件数 | number | 90 |  | type=number / grid.visible=true / grid.width=90 / edit.visible=true / search.visible=true / search.operator=>= | caption=チェック件数 |
| main | mainGrid | risk_summary | qa.risk_summary | リスク内訳 | text | 140 |  | type=text / grid.visible=true / grid.width=140 / edit.visible=true / edit.readonly=false | caption=リスク内訳 |
| main | mainGrid | threshold_summary | qa.threshold_summary | 判定基準 | text | 260 |  | type=text / grid.visible=true / edit.visible=true / edit.readonly=false / search.visible=true / search.operator=contains | caption=判定基準 / grid.width=260 |
| main | mainGrid | message | qa.shortage_message | 検出メッセージ | text | 420 |  | type=text / grid.visible=true / edit.visible=true / edit.readonly=false / search.visible=true / search.operator=contains | caption=検出メッセージ / grid.width=420 |
| main | mainGrid | suggested_action | qa.suggested_action | 推奨アクション | textarea | 420 |  | type=textarea / grid.visible=true / edit.visible=true / search.visible=true / search.operator=contains | caption=推奨アクション / grid.width=420 |
| main | mainGrid | check_ids | qa.check_ids | チェックID一覧 | stringArray | 280 |  | type=stringArray / grid.visible=true / grid.width=280 / edit.visible=true | caption=チェックID一覧 |
| main | mainGrid | constraint_ids | qa.constraint_ids | 制約ID一覧 | stringArray | 260 |  | type=stringArray / grid.visible=true / grid.width=260 / edit.visible=true | caption=制約ID一覧 |
| main | mainGrid | test_pattern_ids | qa.test_pattern_ids | テストパターンID一覧 | stringArray | 260 |  | type=stringArray / grid.visible=true / grid.width=260 / edit.visible=true | caption=テストパターンID一覧 |

## Expected 不足検出

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

### 不足検出一覧

- section.id: mainGrid
- type: grid
- dataPath: $.expected_shortage_findings
- fields: 16

| field | caption | type | grid.visible | width | edit.visible | readonly | search | options |
| --- | --- | --- | --- | ---: | --- | --- | --- | --- |
| finding_id | 不足ID | text |  |  |  |  |  |  |
| severity_cd | 重要度CD | text |  | 90 |  |  |  |  |
| severity_name | 重要度 | text |  | 80 |  |  |  |  |
| finding_type_name | 検出種別 | text |  | 150 |  |  |  |  |
| target_type_name | 対象種別 | text |  | 120 |  |  |  |  |
| target_cd | 対象CD | text |  | 170 |  |  |  |  |
| target_name | 対象名 | text |  | 180 |  |  |  |  |
| risk_name | リスク | text |  | 80 |  |  |  |  |
| check_count | チェック件数 | text |  |  |  |  |  |  |
| risk_summary | リスク内訳 | text |  |  |  |  |  |  |
| threshold_summary | 判定基準 | text |  | 260 |  |  |  |  |
| message | 検出メッセージ | text |  | 420 |  |  |  |  |
| suggested_action | 推奨アクション | text |  | 420 |  |  |  |  |
| check_ids | チェックID一覧 | text |  |  |  |  |  |  |
| constraint_ids | 制約ID一覧 | text |  |  |  |  |  |  |
| test_pattern_ids | テストパターンID一覧 | text |  |  |  |  |  |  |

---

## 解決済みViewDef概要

extends / fieldType を解決した、現在画面描画に使っているViewDefの概要です。

| View | View Caption | Section | Section Caption | Type | DataPath | KeyField | Fields |
| --- | --- | --- | --- | --- | --- | --- | ---: |
| main | Expected 不足検出 | summary | 概要 | form | $ |  | 3 |
| main | Expected 不足検出 | mainGrid | 不足検出一覧 | grid | $.expected_shortage_findings |  | 16 |

## Resolved: Expected 不足検出

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

### 不足検出一覧

- section.id: mainGrid
- type: grid
- dataPath: $.expected_shortage_findings
- fields: 16

| field | caption | type | grid.visible | width | edit.visible | readonly | search | options |
| --- | --- | --- | --- | ---: | --- | --- | --- | --- |
| finding_id | 不足ID | text | true | 100 | true | true | true (contains) |  |
| severity_cd | 重要度CD | select | true | 90 | true |  | true (equals) | high:高, medium:中, low:低, info:情報 |
| severity_name | 重要度 | text | true | 80 | true | false | true (contains) |  |
| finding_type_name | 検出種別 | text | true | 150 | true | false | true (contains) |  |
| target_type_name | 対象種別 | text | true | 120 | true | false | true (contains) |  |
| target_cd | 対象CD | text | true | 170 | true | false | true (contains) |  |
| target_name | 対象名 | text | true | 180 | true | false | true (contains) |  |
| risk_name | リスク | text | true | 80 | true | true | true (contains) |  |
| check_count | チェック件数 | number | true | 90 | true |  | true (>=) |  |
| risk_summary | リスク内訳 | text | true | 140 | true | false |  |  |
| threshold_summary | 判定基準 | text | true | 260 | true | false | true (contains) |  |
| message | 検出メッセージ | text | true | 420 | true | false | true (contains) |  |
| suggested_action | 推奨アクション | textarea | true | 420 | true |  | true (contains) |  |
| check_ids | チェックID一覧 | stringArray | true | 280 | true |  |  |  |
| constraint_ids | 制約ID一覧 | stringArray | true | 260 | true |  |  |  |
| test_pattern_ids | テストパターンID一覧 | stringArray | true | 260 | true |  |  |  |

---

## ViewDef JSON

<details>
<summary>元ViewDef JSONを表示</summary>

```json
{
  "app": {
    "title": "QA Expected Shortage Findings"
  },
  "fieldTypeSources": [
    "common_types_v0_1.json"
  ],
  "dataSources": {
    "test_patterns": "qa_test_patterns_sample_v0_1.json"
  },
  "virtualData": [
    {
      "builder": "expected_check_shortage_findings",
      "targetPath": "$.expected_shortage_findings",
      "source": {
        "source": "$current",
        "path": "$.expected_checks"
      },
      "rules": {
        "axisRisk": [
          {
            "axisType": "quality_axis",
            "axisLabel": "品質観点",
            "field": "quality_axis_cd",
            "values": [
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
            "risks": [
              {
                "cd": "high",
                "name": "高",
                "minCount": 1,
                "severity": "high"
              },
              {
                "cd": "medium",
                "name": "中",
                "minCount": 1,
                "severity": "medium"
              }
            ]
          },
          {
            "axisType": "check_axis",
            "axisLabel": "チェック観点",
            "field": "check_axis_cd",
            "values": [
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
            "risks": [
              {
                "cd": "high",
                "name": "高",
                "minCount": 1,
                "severity": "high"
              },
              {
                "cd": "medium",
                "name": "中",
                "minCount": 1,
                "severity": "medium"
              }
            ]
          }
        ],
        "constraintCoverage": {
          "enabled": true,
          "field": "constraint_ids",
          "minTotal": 2,
          "minHigh": 0
        },
        "testPatternCoverage": {
          "enabled": true,
          "source": {
            "source": "test_patterns",
            "path": "$.test_patterns"
          },
          "idField": "test_pattern_id",
          "titleField": "title",
          "minTotal": 5,
          "minHigh": 1
        },
        "requiredFields": [
          {
            "field": "check_id",
            "caption": "チェックID",
            "severity": "high"
          },
          {
            "field": "test_pattern_id",
            "caption": "テストパターンID",
            "severity": "high"
          },
          {
            "field": "title",
            "caption": "タイトル",
            "severity": "medium"
          },
          {
            "field": "quality_axis_cd",
            "caption": "品質観点",
            "severity": "high"
          },
          {
            "field": "check_axis_cd",
            "caption": "チェック観点",
            "severity": "high"
          },
          {
            "field": "risk_cd",
            "caption": "リスク",
            "severity": "high"
          },
          {
            "field": "expected_summary",
            "caption": "期待値概要",
            "severity": "medium"
          },
          {
            "field": "constraint_ids",
            "caption": "制約ID",
            "severity": "medium"
          }
        ]
      },
      "outputs": {
        "findingIdField": "finding_id",
        "findingTypeField": "finding_type_cd",
        "findingTypeNameField": "finding_type_name",
        "severityField": "severity_cd",
        "severityNameField": "severity_name",
        "targetTypeField": "target_type_cd",
        "targetTypeNameField": "target_type_name",
        "targetIdField": "target_cd",
        "targetNameField": "target_name",
        "riskField": "risk_cd",
        "riskNameField": "risk_name",
        "countField": "check_count",
        "highCountField": "high_count",
        "mediumCountField": "medium_count",
        "lowCountField": "low_count",
        "thresholdField": "threshold_summary",
        "messageField": "message",
        "suggestedActionField": "suggested_action",
        "checkIdsField": "check_ids",
        "testPatternIdsField": "test_pattern_ids",
        "constraintIdsField": "constraint_ids",
        "riskSummaryField": "risk_summary"
      },
      "sort": []
    }
  ],
  "views": [
    {
      "id": "main",
      "caption": "Expected 不足検出",
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
          "caption": "不足検出一覧",
          "dataPath": "$.expected_shortage_findings",
          "fields": [
            {
              "field": "finding_id",
              "caption": "不足ID",
              "fieldType": "qa.finding_id"
            },
            {
              "field": "severity_cd",
              "caption": "重要度CD",
              "fieldType": "qa.severity",
              "grid": {
                "width": 90
              }
            },
            {
              "field": "severity_name",
              "caption": "重要度",
              "fieldType": "qa.severity_name",
              "grid": {
                "width": 80
              }
            },
            {
              "field": "finding_type_name",
              "caption": "検出種別",
              "fieldType": "qa.finding_type_name",
              "grid": {
                "width": 150
              }
            },
            {
              "field": "target_type_name",
              "caption": "対象種別",
              "fieldType": "qa.target_type_name",
              "grid": {
                "width": 120
              }
            },
            {
              "field": "target_cd",
              "caption": "対象CD",
              "fieldType": "qa.target_cd",
              "grid": {
                "width": 170
              }
            },
            {
              "field": "target_name",
              "caption": "対象名",
              "fieldType": "qa.target_name",
              "grid": {
                "width": 180
              }
            },
            {
              "field": "risk_name",
              "caption": "リスク",
              "fieldType": "qa.risk_name",
              "grid": {
                "width": 80
              }
            },
            {
              "field": "check_count",
              "caption": "チェック件数",
              "fieldType": "qa.check_count"
            },
            {
              "field": "risk_summary",
              "caption": "リスク内訳",
              "fieldType": "qa.risk_summary"
            },
            {
              "field": "threshold_summary",
              "caption": "判定基準",
              "fieldType": "qa.threshold_summary",
              "grid": {
                "width": 260
              }
            },
            {
              "field": "message",
              "caption": "検出メッセージ",
              "fieldType": "qa.shortage_message",
              "grid": {
                "width": 420
              }
            },
            {
              "field": "suggested_action",
              "caption": "推奨アクション",
              "fieldType": "qa.suggested_action",
              "grid": {
                "width": 420
              }
            },
            {
              "field": "check_ids",
              "caption": "チェックID一覧",
              "fieldType": "qa.check_ids"
            },
            {
              "field": "constraint_ids",
              "caption": "制約ID一覧",
              "fieldType": "qa.constraint_ids"
            },
            {
              "field": "test_pattern_ids",
              "caption": "テストパターンID一覧",
              "fieldType": "qa.test_pattern_ids"
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
    "title": "QA Expected Shortage Findings"
  },
  "fieldTypeSources": [
    "common_types_v0_1.json"
  ],
  "dataSources": {
    "test_patterns": "qa_test_patterns_sample_v0_1.json"
  },
  "virtualData": [
    {
      "builder": "expected_check_shortage_findings",
      "targetPath": "$.expected_shortage_findings",
      "source": {
        "source": "$current",
        "path": "$.expected_checks"
      },
      "rules": {
        "axisRisk": [
          {
            "axisType": "quality_axis",
            "axisLabel": "品質観点",
            "field": "quality_axis_cd",
            "values": [
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
            "risks": [
              {
                "cd": "high",
                "name": "高",
                "minCount": 1,
                "severity": "high"
              },
              {
                "cd": "medium",
                "name": "中",
                "minCount": 1,
                "severity": "medium"
              }
            ]
          },
          {
            "axisType": "check_axis",
            "axisLabel": "チェック観点",
            "field": "check_axis_cd",
            "values": [
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
            "risks": [
              {
                "cd": "high",
                "name": "高",
                "minCount": 1,
                "severity": "high"
              },
              {
                "cd": "medium",
                "name": "中",
                "minCount": 1,
                "severity": "medium"
              }
            ]
          }
        ],
        "constraintCoverage": {
          "enabled": true,
          "field": "constraint_ids",
          "minTotal": 2,
          "minHigh": 0
        },
        "testPatternCoverage": {
          "enabled": true,
          "source": {
            "source": "test_patterns",
            "path": "$.test_patterns"
          },
          "idField": "test_pattern_id",
          "titleField": "title",
          "minTotal": 5,
          "minHigh": 1
        },
        "requiredFields": [
          {
            "field": "check_id",
            "caption": "チェックID",
            "severity": "high"
          },
          {
            "field": "test_pattern_id",
            "caption": "テストパターンID",
            "severity": "high"
          },
          {
            "field": "title",
            "caption": "タイトル",
            "severity": "medium"
          },
          {
            "field": "quality_axis_cd",
            "caption": "品質観点",
            "severity": "high"
          },
          {
            "field": "check_axis_cd",
            "caption": "チェック観点",
            "severity": "high"
          },
          {
            "field": "risk_cd",
            "caption": "リスク",
            "severity": "high"
          },
          {
            "field": "expected_summary",
            "caption": "期待値概要",
            "severity": "medium"
          },
          {
            "field": "constraint_ids",
            "caption": "制約ID",
            "severity": "medium"
          }
        ]
      },
      "outputs": {
        "findingIdField": "finding_id",
        "findingTypeField": "finding_type_cd",
        "findingTypeNameField": "finding_type_name",
        "severityField": "severity_cd",
        "severityNameField": "severity_name",
        "targetTypeField": "target_type_cd",
        "targetTypeNameField": "target_type_name",
        "targetIdField": "target_cd",
        "targetNameField": "target_name",
        "riskField": "risk_cd",
        "riskNameField": "risk_name",
        "countField": "check_count",
        "highCountField": "high_count",
        "mediumCountField": "medium_count",
        "lowCountField": "low_count",
        "thresholdField": "threshold_summary",
        "messageField": "message",
        "suggestedActionField": "suggested_action",
        "checkIdsField": "check_ids",
        "testPatternIdsField": "test_pattern_ids",
        "constraintIdsField": "constraint_ids",
        "riskSummaryField": "risk_summary"
      },
      "sort": []
    }
  ],
  "views": [
    {
      "id": "main",
      "caption": "Expected 不足検出",
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
          "caption": "不足検出一覧",
          "dataPath": "$.expected_shortage_findings",
          "fields": [
            {
              "caption": "不足ID",
              "grid": {
                "visible": true,
                "width": 100
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
              "field": "finding_id",
              "fieldType": "qa.finding_id"
            },
            {
              "caption": "重要度CD",
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
                },
                {
                  "cd": "info",
                  "name": "情報"
                }
              ],
              "grid": {
                "visible": true,
                "width": 90
              },
              "edit": {
                "visible": true
              },
              "search": {
                "visible": true,
                "operator": "equals"
              },
              "type": "select",
              "field": "severity_cd",
              "fieldType": "qa.severity"
            },
            {
              "caption": "重要度",
              "grid": {
                "visible": true,
                "width": 80
              },
              "edit": {
                "visible": true,
                "readonly": false
              },
              "search": {
                "visible": true,
                "operator": "contains"
              },
              "type": "text",
              "field": "severity_name",
              "fieldType": "qa.severity_name"
            },
            {
              "caption": "検出種別",
              "grid": {
                "visible": true,
                "width": 150
              },
              "edit": {
                "visible": true,
                "readonly": false
              },
              "search": {
                "visible": true,
                "operator": "contains"
              },
              "type": "text",
              "field": "finding_type_name",
              "fieldType": "qa.finding_type_name"
            },
            {
              "caption": "対象種別",
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
              "type": "text",
              "field": "target_type_name",
              "fieldType": "qa.target_type_name"
            },
            {
              "caption": "対象CD",
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
              "type": "text",
              "field": "target_cd",
              "fieldType": "qa.target_cd"
            },
            {
              "caption": "対象名",
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
              "type": "text",
              "field": "target_name",
              "fieldType": "qa.target_name"
            },
            {
              "caption": "リスク",
              "grid": {
                "visible": true,
                "width": 80
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
                "visible": true
              },
              "search": {
                "visible": true,
                "operator": ">="
              },
              "type": "number",
              "field": "check_count",
              "fieldType": "qa.check_count"
            },
            {
              "caption": "リスク内訳",
              "grid": {
                "visible": true,
                "width": 140
              },
              "edit": {
                "visible": true,
                "readonly": false
              },
              "type": "text",
              "field": "risk_summary",
              "fieldType": "qa.risk_summary"
            },
            {
              "caption": "判定基準",
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
              "type": "text",
              "field": "threshold_summary",
              "fieldType": "qa.threshold_summary"
            },
            {
              "caption": "検出メッセージ",
              "grid": {
                "visible": true,
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
              "type": "text",
              "field": "message",
              "fieldType": "qa.shortage_message"
            },
            {
              "caption": "推奨アクション",
              "grid": {
                "visible": true,
                "width": 420
              },
              "edit": {
                "visible": true,
                "height": 90
              },
              "search": {
                "visible": true,
                "operator": "contains"
              },
              "type": "textarea",
              "field": "suggested_action",
              "fieldType": "qa.suggested_action"
            },
            {
              "caption": "チェックID一覧",
              "grid": {
                "visible": true,
                "width": 280
              },
              "edit": {
                "visible": true
              },
              "type": "stringArray",
              "field": "check_ids",
              "fieldType": "qa.check_ids"
            },
            {
              "caption": "制約ID一覧",
              "grid": {
                "visible": true,
                "width": 260
              },
              "edit": {
                "visible": true
              },
              "type": "stringArray",
              "field": "constraint_ids",
              "fieldType": "qa.constraint_ids"
            },
            {
              "caption": "テストパターンID一覧",
              "grid": {
                "visible": true,
                "width": 260
              },
              "edit": {
                "visible": true
              },
              "type": "stringArray",
              "field": "test_pattern_ids",
              "fieldType": "qa.test_pattern_ids"
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