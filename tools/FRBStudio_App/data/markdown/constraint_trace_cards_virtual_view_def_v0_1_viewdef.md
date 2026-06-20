# ViewDef定義レポート — 制約証跡カード / Relation JSON × 最新diff

## 基本情報
- 出力日時: 2026/6/20 13:19:06
- 対象ViewDef: constraint_trace_cards_virtual_view_def_v0_1.json
- app.name: No-Code JSON Studio
- app.version: 0.3-draft-relation-generic-012
- views: 1

## View / Section 概要
| View | View Caption | Section | Section Caption | Type | DataPath | KeyField | Fields |
| --- | --- | --- | --- | --- | --- | --- | ---: |
| constraint_trace_cards_view | 制約証跡カード / Relation JSON × 最新diff | header | Relation JSON / 基本情報 | form | $ |  | 5 |
| constraint_trace_cards_view | 制約証跡カード / Relation JSON × 最新diff | constraint_trace_cards | 制約一覧 / 証拠保管庫入口 | grid | $.constraint_trace_cards | constraint_id | 17 |

## 継承差分サマリ

このViewDefは extends を持たないため、継承差分はありません。

## 制約証跡カード / Relation JSON × 最新diff

- view.id: constraint_trace_cards_view
- layout: {"detailDialog":"wide"}
- markdown.type: generic_sections
- markdown.title: 制約証跡カード
- markdown.defaultFileName: constraint_trace_cards_report.md

### Relation JSON / 基本情報

- section.id: header
- type: form
- dataPath: $
- fields: 5

| field | caption | type | grid.visible | width | edit.visible | readonly | search | options |
| --- | --- | --- | --- | ---: | --- | --- | --- | --- |
| title | タイトル | text | false |  | true | true |  |  |
| schema_version | Schema | text | false |  | true | true |  |  |
| document_type | Document Type | text | false |  | true | true |  |  |
| policy | 設計方針 | textarea | false |  | true | true |  |  |
| source_note | メモ | textarea | false |  | true | true |  |  |

### 制約一覧 / 証拠保管庫入口

- section.id: constraint_trace_cards
- type: grid
- dataPath: $.constraint_trace_cards
- keyField: constraint_id
- fields: 17

| field | caption | type | grid.visible | width | edit.visible | readonly | search | options |
| --- | --- | --- | --- | ---: | --- | --- | --- | --- |
| constraint_id | 制約ID | text | true | 95 | true | true | true (contains) |  |
| constraint_title | 制約名 | text | true | 260 | true | true | true (contains) |  |
| group_id | Group | text | true | 130 | true | true | true (contains) |  |
| category | 分類 | text | true | 110 | true | true | true (contains) |  |
| trace_label | 証跡状態 | text | true | 140 | true | true | true (contains) |  |
| latest_result | 最新結果 | select | true | 90 | true | true | true (equals) | fail, pass, linked, unverified |
| coverage | Coverage | text | true | 110 | true | true | true (contains) |  |
| tests_count | Tests | number | true | 70 | true | true | true (gte) |  |
| fail_count | Fail | number | true | 70 | true | true | true (gte) |  |
| last_checked_at | 最終確認日時 | datetime | true | 190 | true | true |  |  |
| review_status | レビュー状態 | text | false |  | true | true |  |  |
| verification_status | 確認状態 | text | false |  | true | true |  |  |
| constraint_text | 制約本文 | textarea | false |  | true | true |  |  |
| linked_tests | 紐づくテストパターン | objectArray | false |  | true | true |  |  |
| related_diffs | 根拠diff | objectArray | false |  | true | true |  |  |
| failed_checks | 失敗チェック | objectArray | false |  | true | true |  |  |
| evidence_edges | 証跡エッジ | objectArray | false |  | true | true |  |  |

---

## ViewDef JSON

<details>
<summary>元ViewDef JSONを表示</summary>

```json
{
  "app": {
    "name": "No-Code JSON Studio",
    "version": "0.3-draft-relation-generic-012"
  },
  "dataSources": {
    "constraints": "ai_constraint_spec_aggregated_v0_6_footer_chat.json",
    "tests": "screen_state_test_patterns_data_v0_2_chat.json",
    "diff": "screen_state_smoke_001.diff.json",
    "relations": "constraint_trace_relations_v0_1.json"
  },
  "virtualData": {
    "builder": "relation_axis_cards",
    "targetPath": "$.constraint_trace_cards",
    "axis": {
      "source": "constraints",
      "adapter": "constraints",
      "nodeType": "constraint",
      "idField": "constraint_id",
      "titleField": "constraint_title"
    },
    "linked": {
      "source": "tests",
      "adapter": "testPatterns",
      "nodeType": "test_pattern",
      "idField": "test_pattern_id",
      "titleField": "title"
    },
    "relation": {
      "source": "relations",
      "path": "$.relations",
      "name": "verified_by",
      "direction": "outgoing",
      "includeViaCheck": true,
      "containsCheckRelation": "contains_check"
    },
    "diff": {
      "source": "diff",
      "testNodeType": "test_pattern"
    },
    "outputs": {
      "idField": "constraint_id",
      "titleField": "constraint_title",
      "linkedItemsField": "linked_tests",
      "linkedCountField": "tests_count",
      "coverageField": "coverage",
      "relatedDiffsField": "related_diffs",
      "failedChecksField": "failed_checks",
      "evidenceEdgesField": "evidence_edges"
    },
    "note": "汎用 relation_axis_cards によって、制約を軸に relation JSON と最新diff JSON から表示用カードを保存せず一時生成する。"
  },
  "views": [
    {
      "id": "constraint_trace_cards_view",
      "caption": "制約証跡カード / Relation JSON × 最新diff",
      "layout": {
        "detailDialog": "wide"
      },
      "sections": [
        {
          "id": "header",
          "caption": "Relation JSON / 基本情報",
          "type": "form",
          "dataPath": "$",
          "fields": [
            {
              "field": "title",
              "caption": "タイトル",
              "type": "text",
              "readonly": true,
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
              "type": "text",
              "readonly": true,
              "grid": {
                "visible": false
              },
              "edit": {
                "visible": true,
                "readonly": true
              }
            },
            {
              "field": "document_type",
              "caption": "Document Type",
              "type": "text",
              "readonly": true,
              "grid": {
                "visible": false
              },
              "edit": {
                "visible": true,
                "readonly": true
              }
            },
            {
              "field": "policy",
              "caption": "設計方針",
              "type": "textarea",
              "readonly": true,
              "grid": {
                "visible": false
              },
              "edit": {
                "visible": true,
                "readonly": true,
                "height": 76
              }
            },
            {
              "field": "source_note",
              "caption": "メモ",
              "type": "textarea",
              "readonly": true,
              "grid": {
                "visible": false
              },
              "edit": {
                "visible": true,
                "readonly": true,
                "height": 70
              }
            }
          ]
        },
        {
          "id": "constraint_trace_cards",
          "caption": "制約一覧 / 証拠保管庫入口",
          "type": "grid",
          "dataPath": "$.constraint_trace_cards",
          "keyField": "constraint_id",
          "fields": [
            {
              "field": "constraint_id",
              "caption": "制約ID",
              "type": "text",
              "readonly": true,
              "grid": {
                "visible": true,
                "width": 95
              },
              "edit": {
                "visible": true,
                "readonly": true
              },
              "search": {
                "visible": true,
                "operator": "contains"
              }
            },
            {
              "field": "constraint_title",
              "caption": "制約名",
              "type": "text",
              "readonly": true,
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
              }
            },
            {
              "field": "group_id",
              "caption": "Group",
              "type": "text",
              "readonly": true,
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
              }
            },
            {
              "field": "category",
              "caption": "分類",
              "type": "text",
              "readonly": true,
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
                "operator": "contains"
              }
            },
            {
              "field": "trace_label",
              "caption": "証跡状態",
              "type": "text",
              "readonly": true,
              "grid": {
                "visible": true,
                "width": 140
              },
              "edit": {
                "visible": true,
                "readonly": true
              },
              "search": {
                "visible": true,
                "operator": "contains"
              }
            },
            {
              "field": "latest_result",
              "caption": "最新結果",
              "type": "select",
              "options": [
                "fail",
                "pass",
                "linked",
                "unverified"
              ],
              "readonly": true,
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
                "operator": "equals"
              }
            },
            {
              "field": "coverage",
              "caption": "Coverage",
              "type": "text",
              "readonly": true,
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
                "operator": "contains"
              }
            },
            {
              "field": "tests_count",
              "caption": "Tests",
              "type": "number",
              "readonly": true,
              "grid": {
                "visible": true,
                "width": 70
              },
              "edit": {
                "visible": true,
                "readonly": true
              },
              "search": {
                "visible": true,
                "operator": "gte"
              }
            },
            {
              "field": "fail_count",
              "caption": "Fail",
              "type": "number",
              "readonly": true,
              "grid": {
                "visible": true,
                "width": 70
              },
              "edit": {
                "visible": true,
                "readonly": true
              },
              "search": {
                "visible": true,
                "operator": "gte"
              }
            },
            {
              "field": "last_checked_at",
              "caption": "最終確認日時",
              "type": "datetime",
              "readonly": true,
              "grid": {
                "visible": true,
                "width": 190
              },
              "edit": {
                "visible": true,
                "readonly": true
              }
            },
            {
              "field": "review_status",
              "caption": "レビュー状態",
              "type": "text",
              "readonly": true,
              "grid": {
                "visible": false
              },
              "edit": {
                "visible": true,
                "readonly": true
              }
            },
            {
              "field": "verification_status",
              "caption": "確認状態",
              "type": "text",
              "readonly": true,
              "grid": {
                "visible": false
              },
              "edit": {
                "visible": true,
                "readonly": true
              }
            },
            {
              "field": "constraint_text",
              "caption": "制約本文",
              "type": "textarea",
              "readonly": true,
              "grid": {
                "visible": false
              },
              "edit": {
                "visible": true,
                "readonly": true,
                "height": 76
              }
            },
            {
              "field": "linked_tests",
              "caption": "紐づくテストパターン",
              "type": "objectArray",
              "readonly": true,
              "grid": {
                "visible": false
              },
              "edit": {
                "visible": true,
                "readonly": true
              }
            },
            {
              "field": "related_diffs",
              "caption": "根拠diff",
              "type": "objectArray",
              "readonly": true,
              "grid": {
                "visible": false
              },
              "edit": {
                "visible": true,
                "readonly": true
              }
            },
            {
              "field": "failed_checks",
              "caption": "失敗チェック",
              "type": "objectArray",
              "readonly": true,
              "grid": {
                "visible": false
              },
              "edit": {
                "visible": true,
                "readonly": true
              }
            },
            {
              "field": "evidence_edges",
              "caption": "証跡エッジ",
              "type": "objectArray",
              "readonly": true,
              "grid": {
                "visible": false
              },
              "edit": {
                "visible": true,
                "readonly": true
              }
            }
          ]
        }
      ],
      "markdown": {
        "enabled": true,
        "type": "generic_sections",
        "title": "制約証跡カード",
        "defaultFileName": "constraint_trace_cards_report.md",
        "sections": [
          {
            "title": "基本情報",
            "dataPath": "$",
            "fields": [
              "title",
              "schema_version",
              "policy"
            ]
          },
          {
            "title": "制約証跡カード",
            "dataPath": "$.constraint_trace_cards",
            "format": "table",
            "fields": [
              "constraint_id",
              "constraint_title",
              "trace_label",
              "latest_result",
              "tests_count",
              "fail_count",
              "last_checked_at"
            ]
          }
        ]
      }
    }
  ]
}
```

</details>