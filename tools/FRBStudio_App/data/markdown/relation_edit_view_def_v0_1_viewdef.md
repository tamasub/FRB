# ViewDef定義レポート — 制約証跡リレーション編集 / コネクト線定義

## 基本情報
- 出力日時: 2026/6/21 16:12:37
- 対象ViewDef: relation_edit_view_def_v0_1.json
- app.name: No-Code JSON Studio
- app.version: 0.3-draft-relation-edit-010
- views: 1

## View / Section 概要
| View | View Caption | Section | Section Caption | Type | DataPath | KeyField | Fields |
| --- | --- | --- | --- | --- | --- | --- | ---: |
| constraint_trace_relations_edit | 制約証跡リレーション編集 / コネクト線定義 | header | Relation JSON / 基本情報 | form | $ |  | 3 |
| constraint_trace_relations_edit | 制約証跡リレーション編集 / コネクト線定義 | relations | コネクト線一覧 / 人間承認対象 | grid | $.relations | relation_id | 13 |

## 継承差分サマリ

このViewDefは extends を持たないため、継承差分はありません。

## 解決サマリ

- 読込済み共通Type namespace: qa / relation / business / core
- fieldType参照: 13件
- fieldType caption未指定: 0件
- 制約: fieldType を使う field でも、元ViewDef側に caption を明示することを推奨します。ViewDef側 caption が Common 側 caption より優先されます。
- 見方: 「Common由来候補」は元ViewDefに書かれておらず、解決後に現れた項目です。

| View | Section | field | fieldType | caption | type | width | options | Common由来候補 | ViewDef個別指定 |
| --- | --- | --- | --- | --- | --- | ---: | --- | --- | --- |
| constraint_trace_relations_edit | header | title | core.title | タイトル | text | 260 |  | type=text / readonly=false / grid.visible=true / grid.width=260 / edit.visible=true / edit.readonly=false / ... +2 | caption=タイトル |
| constraint_trace_relations_edit | header | schema_version | core.schema_version | Schema | text | 120 |  | type=text / readonly=false / grid.visible=true / grid.width=120 / edit.visible=true / edit.readonly=false / ... +2 | caption=Schema |
| constraint_trace_relations_edit | relations | relation_id | relation.relation_id | Relation ID | text | 210 |  | type=text / readonly=true / edit.visible=true / edit.readonly=true / search.visible=true / search.operator=contains | caption=Relation ID / grid.visible=true / grid.width=210 |
| constraint_trace_relations_edit | relations | from_type | relation.node_type | Node Type | select | 120 | 8件 | type=select / readonly=false / edit.visible=true / edit.readonly=false / search.visible=true / search.operator=equals / ... +1 | caption=Node Type / grid.visible=true / grid.width=120 |
| constraint_trace_relations_edit | relations | from_id | relation.from_id | From ID | text | 170 |  | type=text / readonly=false / edit.visible=true / edit.readonly=false / search.visible=true / search.operator=contains | caption=From ID / grid.visible=true / grid.width=170 |
| constraint_trace_relations_edit | relations | relation | relation.relation_type | Relation | select | 140 | 7件 | type=select / readonly=false / edit.visible=true / edit.readonly=false / search.visible=true / search.operator=equals / ... +1 | caption=Relation / grid.visible=true / grid.width=140 |
| constraint_trace_relations_edit | relations | to_type | relation.node_type | Node Type | select | 120 | 8件 | type=select / readonly=false / edit.visible=true / edit.readonly=false / search.visible=true / search.operator=equals / ... +1 | caption=Node Type / grid.visible=true / grid.width=120 |
| constraint_trace_relations_edit | relations | to_id | relation.to_id | To ID | text | 180 |  | type=text / readonly=false / edit.visible=true / edit.readonly=false / search.visible=true / search.operator=contains | caption=To ID / grid.visible=true / grid.width=180 |
| constraint_trace_relations_edit | relations | status | relation.status | 承認状態 | select | 110 | 6件 | type=select / edit.visible=true / search.visible=true / search.operator=equals / options=[6件] | caption=承認状態 / grid.visible=true / grid.width=110 |
| constraint_trace_relations_edit | relations | coverage | relation.coverage | Coverage | select | 110 | 3件 | type=select / readonly=false / edit.visible=true / edit.readonly=false / search.visible=true / search.operator=equals / ... +1 | caption=Coverage / grid.visible=true / grid.width=110 |
| constraint_trace_relations_edit | relations | confidence | relation.confidence | Confidence | select | 110 | 3件 | type=select / readonly=false / edit.visible=true / edit.readonly=false / search.visible=true / search.operator=equals / ... +1 | caption=Confidence / grid.visible=true / grid.width=110 |
| constraint_trace_relations_edit | relations | priority | relation.priority | Priority | select | 90 | 3件 | type=select / readonly=false / edit.visible=true / edit.readonly=false / search.visible=true / search.operator=equals / ... +1 | caption=Priority / grid.visible=true / grid.width=90 |
| constraint_trace_relations_edit | relations | note | relation.approval_note | 承認メモ | textarea | 360 |  | type=textarea / readonly=false / grid.width=360 / edit.visible=true / edit.readonly=false / search.visible=true / ... +1 | caption=承認メモ / grid.visible=false |

## 制約証跡リレーション編集 / コネクト線定義

- view.id: constraint_trace_relations_edit
- layout: {"detailDialog":"wide"}
- markdown.type: generic_sections
- markdown.title: 制約証跡リレーション
- markdown.defaultFileName: constraint_trace_relations_report.md

### Relation JSON / 基本情報

- section.id: header
- type: form
- dataPath: $
- fields: 3

| field | caption | type | grid.visible | width | edit.visible | readonly | search | options |
| --- | --- | --- | --- | ---: | --- | --- | --- | --- |
| title | タイトル | text |  |  |  |  |  |  |
| schema_version | Schema | text |  |  |  |  |  |  |
| policy | 設計方針 | textarea | false |  | true | true |  |  |

### コネクト線一覧 / 人間承認対象

- section.id: relations
- type: grid
- dataPath: $.relations
- keyField: relation_id
- fields: 13

| field | caption | type | grid.visible | width | edit.visible | readonly | search | options |
| --- | --- | --- | --- | ---: | --- | --- | --- | --- |
| relation_id | Relation ID | text | true | 210 |  |  |  |  |
| from_type | Node Type | text | true | 120 |  |  |  |  |
| from_id | From ID | text | true | 170 |  |  |  |  |
| relation | Relation | text | true | 140 |  |  |  |  |
| to_type | Node Type | text | true | 120 |  |  |  |  |
| to_id | To ID | text | true | 180 |  |  |  |  |
| status | 承認状態 | text | true | 110 |  |  |  |  |
| coverage | Coverage | text | true | 110 |  |  |  |  |
| confidence | Confidence | text | true | 110 |  |  |  |  |
| required | Required | boolean | true | 90 | true |  | true (equals) |  |
| enabled | Enabled | boolean | true | 90 | true |  | true (equals) |  |
| priority | Priority | text | true | 90 |  |  |  |  |
| note | 承認メモ | text | false |  |  |  |  |  |

---

## 解決済みViewDef概要

extends / fieldType を解決した、現在画面描画に使っているViewDefの概要です。

| View | View Caption | Section | Section Caption | Type | DataPath | KeyField | Fields |
| --- | --- | --- | --- | --- | --- | --- | ---: |
| constraint_trace_relations_edit | 制約証跡リレーション編集 / コネクト線定義 | header | Relation JSON / 基本情報 | form | $ |  | 3 |
| constraint_trace_relations_edit | 制約証跡リレーション編集 / コネクト線定義 | relations | コネクト線一覧 / 人間承認対象 | grid | $.relations | relation_id | 13 |

## Resolved: 制約証跡リレーション編集 / コネクト線定義

- view.id: constraint_trace_relations_edit
- layout: {"detailDialog":"wide"}
- markdown.type: generic_sections
- markdown.title: 制約証跡リレーション
- markdown.defaultFileName: constraint_trace_relations_report.md

### Relation JSON / 基本情報

- section.id: header
- type: form
- dataPath: $
- fields: 3

| field | caption | type | grid.visible | width | edit.visible | readonly | search | options |
| --- | --- | --- | --- | ---: | --- | --- | --- | --- |
| title | タイトル | text | true | 260 | true | false | true (contains) |  |
| schema_version | Schema | text | true | 120 | true | false | true (contains) |  |
| policy | 設計方針 | textarea | false |  | true | true |  |  |

### コネクト線一覧 / 人間承認対象

- section.id: relations
- type: grid
- dataPath: $.relations
- keyField: relation_id
- fields: 13

| field | caption | type | grid.visible | width | edit.visible | readonly | search | options |
| --- | --- | --- | --- | ---: | --- | --- | --- | --- |
| relation_id | Relation ID | text | true | 210 | true | true | true (contains) |  |
| from_type | Node Type | select | true | 120 | true | false | true (equals) | constraint:制約, test_pattern:テストパターン, check:チェック, diff:Diff, customer:顧客, project:案件, task:タスク, employee:担当者 |
| from_id | From ID | text | true | 170 | true | false | true (contains) |  |
| relation | Relation | select | true | 140 | true | false | true (equals) | verified_by:verified_by, contains_check:contains_check, has_project:has_project, has_task:has_task, assigned_to:assigned_to, related_to:related_to, depends_on:depends_on |
| to_type | Node Type | select | true | 120 | true | false | true (equals) | constraint:制約, test_pattern:テストパターン, check:チェック, diff:Diff, customer:顧客, project:案件, task:タスク, employee:担当者 |
| to_id | To ID | text | true | 180 | true | false | true (contains) |  |
| status | 承認状態 | select | true | 110 | true |  | true (equals) | candidate:候補, approved:承認済み, rejected:却下, derived:自動生成, needs_review:要確認, deprecated:廃止 |
| coverage | Coverage | select | true | 110 | true | false | true (equals) | primary:主証拠, secondary:補助, structure:構造線 |
| confidence | Confidence | select | true | 110 | true | false | true (equals) | high:高, medium:中, low:低 |
| required | Required | boolean | true | 90 | true |  | true (equals) |  |
| enabled | Enabled | boolean | true | 90 | true |  | true (equals) |  |
| priority | Priority | select | true | 90 | true | false | true (equals) | high:高, medium:中, low:低 |
| note | 承認メモ | textarea | false | 360 | true | false | true (contains) |  |

---

## ViewDef JSON

<details>
<summary>元ViewDef JSONを表示</summary>

```json
{
  "app": {
    "name": "No-Code JSON Studio",
    "version": "0.3-draft-relation-edit-010"
  },
  "views": [
    {
      "id": "constraint_trace_relations_edit",
      "caption": "制約証跡リレーション編集 / コネクト線定義",
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
              "fieldType": "core.title"
            },
            {
              "field": "schema_version",
              "caption": "Schema",
              "fieldType": "core.schema_version"
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
                "height": 86
              }
            }
          ]
        },
        {
          "id": "relations",
          "caption": "コネクト線一覧 / 人間承認対象",
          "type": "grid",
          "dataPath": "$.relations",
          "keyField": "relation_id",
          "fields": [
            {
              "field": "relation_id",
              "caption": "Relation ID",
              "fieldType": "relation.relation_id",
              "grid": {
                "visible": true,
                "width": 210
              }
            },
            {
              "field": "from_type",
              "caption": "Node Type",
              "fieldType": "relation.node_type",
              "grid": {
                "visible": true,
                "width": 120
              }
            },
            {
              "field": "from_id",
              "caption": "From ID",
              "fieldType": "relation.from_id",
              "grid": {
                "visible": true,
                "width": 170
              }
            },
            {
              "field": "relation",
              "caption": "Relation",
              "fieldType": "relation.relation_type",
              "grid": {
                "visible": true,
                "width": 140
              }
            },
            {
              "field": "to_type",
              "caption": "Node Type",
              "fieldType": "relation.node_type",
              "grid": {
                "visible": true,
                "width": 120
              }
            },
            {
              "field": "to_id",
              "caption": "To ID",
              "fieldType": "relation.to_id",
              "grid": {
                "visible": true,
                "width": 180
              }
            },
            {
              "field": "status",
              "caption": "承認状態",
              "fieldType": "relation.status",
              "grid": {
                "visible": true,
                "width": 110
              }
            },
            {
              "field": "coverage",
              "caption": "Coverage",
              "fieldType": "relation.coverage",
              "grid": {
                "visible": true,
                "width": 110
              }
            },
            {
              "field": "confidence",
              "caption": "Confidence",
              "fieldType": "relation.confidence",
              "grid": {
                "visible": true,
                "width": 110
              }
            },
            {
              "field": "required",
              "caption": "Required",
              "type": "boolean",
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
              }
            },
            {
              "field": "enabled",
              "caption": "Enabled",
              "type": "boolean",
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
              }
            },
            {
              "field": "priority",
              "caption": "Priority",
              "fieldType": "relation.priority",
              "grid": {
                "visible": true,
                "width": 90
              }
            },
            {
              "field": "note",
              "caption": "承認メモ",
              "fieldType": "relation.approval_note",
              "grid": {
                "visible": false
              }
            }
          ]
        }
      ],
      "markdown": {
        "enabled": true,
        "type": "generic_sections",
        "title": "制約証跡リレーション",
        "defaultFileName": "constraint_trace_relations_report.md",
        "sections": [
          {
            "title": "コネクト線一覧",
            "dataPath": "$.relations",
            "format": "table",
            "fields": [
              "relation_id",
              "from_type",
              "from_id",
              "relation",
              "to_type",
              "to_id",
              "status",
              "coverage",
              "confidence"
            ]
          }
        ]
      }
    }
  ],
  "fieldTypeSources": [
    "common_types_v0_1.json"
  ]
}
```

</details>

<details open>
<summary>解決済みViewDef JSONを表示</summary>

```json
{
  "app": {
    "name": "No-Code JSON Studio",
    "version": "0.3-draft-relation-edit-010"
  },
  "views": [
    {
      "id": "constraint_trace_relations_edit",
      "caption": "制約証跡リレーション編集 / コネクト線定義",
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
              "caption": "タイトル",
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
              "type": "text",
              "field": "title",
              "fieldType": "core.title"
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
                "height": 86
              }
            }
          ]
        },
        {
          "id": "relations",
          "caption": "コネクト線一覧 / 人間承認対象",
          "type": "grid",
          "dataPath": "$.relations",
          "keyField": "relation_id",
          "fields": [
            {
              "caption": "Relation ID",
              "grid": {
                "visible": true,
                "width": 210
              },
              "edit": {
                "visible": true,
                "readonly": true
              },
              "search": {
                "visible": true,
                "operator": "contains"
              },
              "readonly": true,
              "type": "text",
              "field": "relation_id",
              "fieldType": "relation.relation_id"
            },
            {
              "caption": "Node Type",
              "valueField": "cd",
              "labelField": "name",
              "options": [
                {
                  "cd": "constraint",
                  "name": "制約"
                },
                {
                  "cd": "test_pattern",
                  "name": "テストパターン"
                },
                {
                  "cd": "check",
                  "name": "チェック"
                },
                {
                  "cd": "diff",
                  "name": "Diff"
                },
                {
                  "cd": "customer",
                  "name": "顧客"
                },
                {
                  "cd": "project",
                  "name": "案件"
                },
                {
                  "cd": "task",
                  "name": "タスク"
                },
                {
                  "cd": "employee",
                  "name": "担当者"
                }
              ],
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
                "operator": "equals"
              },
              "readonly": false,
              "type": "select",
              "field": "from_type",
              "fieldType": "relation.node_type"
            },
            {
              "caption": "From ID",
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
              "field": "from_id",
              "fieldType": "relation.from_id"
            },
            {
              "caption": "Relation",
              "valueField": "cd",
              "labelField": "name",
              "options": [
                {
                  "cd": "verified_by",
                  "name": "verified_by"
                },
                {
                  "cd": "contains_check",
                  "name": "contains_check"
                },
                {
                  "cd": "has_project",
                  "name": "has_project"
                },
                {
                  "cd": "has_task",
                  "name": "has_task"
                },
                {
                  "cd": "assigned_to",
                  "name": "assigned_to"
                },
                {
                  "cd": "related_to",
                  "name": "related_to"
                },
                {
                  "cd": "depends_on",
                  "name": "depends_on"
                }
              ],
              "grid": {
                "visible": true,
                "width": 140
              },
              "edit": {
                "visible": true,
                "readonly": false
              },
              "search": {
                "visible": true,
                "operator": "equals"
              },
              "readonly": false,
              "type": "select",
              "field": "relation",
              "fieldType": "relation.relation_type"
            },
            {
              "caption": "Node Type",
              "valueField": "cd",
              "labelField": "name",
              "options": [
                {
                  "cd": "constraint",
                  "name": "制約"
                },
                {
                  "cd": "test_pattern",
                  "name": "テストパターン"
                },
                {
                  "cd": "check",
                  "name": "チェック"
                },
                {
                  "cd": "diff",
                  "name": "Diff"
                },
                {
                  "cd": "customer",
                  "name": "顧客"
                },
                {
                  "cd": "project",
                  "name": "案件"
                },
                {
                  "cd": "task",
                  "name": "タスク"
                },
                {
                  "cd": "employee",
                  "name": "担当者"
                }
              ],
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
                "operator": "equals"
              },
              "readonly": false,
              "type": "select",
              "field": "to_type",
              "fieldType": "relation.node_type"
            },
            {
              "caption": "To ID",
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
              "field": "to_id",
              "fieldType": "relation.to_id"
            },
            {
              "caption": "承認状態",
              "valueField": "cd",
              "labelField": "name",
              "options": [
                {
                  "cd": "candidate",
                  "name": "候補"
                },
                {
                  "cd": "approved",
                  "name": "承認済み"
                },
                {
                  "cd": "rejected",
                  "name": "却下"
                },
                {
                  "cd": "derived",
                  "name": "自動生成"
                },
                {
                  "cd": "needs_review",
                  "name": "要確認"
                },
                {
                  "cd": "deprecated",
                  "name": "廃止"
                }
              ],
              "grid": {
                "visible": true,
                "width": 110
              },
              "edit": {
                "visible": true
              },
              "search": {
                "visible": true,
                "operator": "equals"
              },
              "defaultValue": "candidate",
              "type": "select",
              "field": "status",
              "fieldType": "relation.status"
            },
            {
              "caption": "Coverage",
              "valueField": "cd",
              "labelField": "name",
              "options": [
                {
                  "cd": "primary",
                  "name": "主証拠"
                },
                {
                  "cd": "secondary",
                  "name": "補助"
                },
                {
                  "cd": "structure",
                  "name": "構造線"
                }
              ],
              "grid": {
                "visible": true,
                "width": 110
              },
              "edit": {
                "visible": true,
                "readonly": false
              },
              "search": {
                "visible": true,
                "operator": "equals"
              },
              "readonly": false,
              "type": "select",
              "field": "coverage",
              "fieldType": "relation.coverage"
            },
            {
              "caption": "Confidence",
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
                "width": 110
              },
              "edit": {
                "visible": true,
                "readonly": false
              },
              "search": {
                "visible": true,
                "operator": "equals"
              },
              "readonly": false,
              "type": "select",
              "field": "confidence",
              "fieldType": "relation.confidence"
            },
            {
              "field": "required",
              "caption": "Required",
              "type": "boolean",
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
              }
            },
            {
              "field": "enabled",
              "caption": "Enabled",
              "type": "boolean",
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
              }
            },
            {
              "caption": "Priority",
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
                "width": 90
              },
              "edit": {
                "visible": true,
                "readonly": false
              },
              "search": {
                "visible": true,
                "operator": "equals"
              },
              "readonly": false,
              "type": "select",
              "field": "priority",
              "fieldType": "relation.priority"
            },
            {
              "caption": "承認メモ",
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
              "type": "textarea",
              "field": "note",
              "fieldType": "relation.approval_note"
            }
          ]
        }
      ],
      "markdown": {
        "enabled": true,
        "type": "generic_sections",
        "title": "制約証跡リレーション",
        "defaultFileName": "constraint_trace_relations_report.md",
        "sections": [
          {
            "title": "コネクト線一覧",
            "dataPath": "$.relations",
            "format": "table",
            "fields": [
              "relation_id",
              "from_type",
              "from_id",
              "relation",
              "to_type",
              "to_id",
              "status",
              "coverage",
              "confidence"
            ]
          }
        ]
      }
    }
  ],
  "fieldTypeSources": [
    "common_types_v0_1.json"
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