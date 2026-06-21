# ViewDef定義レポート — Studioくん 改修インシデント管理

## 基本情報
- 出力日時: 2026/6/21 16:30:41
- 対象ViewDef: studio_work_incident_view_def_v0_1.json
- app.name: No-Code JSON Studio
- app.version: studio-work-incident-v0.1
- views: 1

## View / Section 概要
| View | View Caption | Section | Section Caption | Type | DataPath | KeyField | Fields |
| --- | --- | --- | --- | --- | --- | --- | ---: |
| studio_work_incident_v0_1 | Studioくん 改修インシデント管理 | header | 基本情報 | form | $ |  | 11 |
| studio_work_incident_v0_1 | Studioくん 改修インシデント管理 | work_items | 改修インシデント / 作業項目 | grid | $.work_items | work_item_id | 29 |

## 継承差分サマリ

このViewDefは extends を持たないため、継承差分はありません。

## 解決サマリ

- 読込済み共通Type namespace: qa / relation / business / core
- fieldType参照: 0件
- fieldType caption未指定: 0件
- extends / fieldType 解決による差分: なし

## Studioくん 改修インシデント管理

- view.id: studio_work_incident_v0_1
- layout: header-search-grid-detail
- markdown.type: generic_sections
- markdown.title: Studioくん 改修インシデント管理
- markdown.defaultFileName: studio_work_incident_export.md

### 基本情報

- section.id: header
- type: form
- dataPath: $
- fields: 11

| field | caption | type | grid.visible | width | edit.visible | readonly | search | options |
| --- | --- | --- | --- | ---: | --- | --- | --- | --- |
| title | タイトル | text | false |  | true | true |  |  |
| target | 対象 | text | false |  | true | true |  |  |
| schema_version | Schema Version | text | false |  | true | true |  |  |
| status | 状態 | select | false |  | true |  |  | draft:draft, active:active, closed:closed |
| created_at | 作成日 | datetime | false |  | true | true |  |  |
| updated_at | 更新日 | datetime | false |  | true |  |  |  |
| owner | Owner | text | false |  | true |  |  |  |
| items_count | 作業項目数 | number | false |  | true | true |  |  |
| purpose | 目的 | textarea | false |  | true | true |  |  |
| operation_policy | 運用方針 | textarea | false |  | true | true |  |  |
| standard_field_policy | 標準メタフィールド方針 | textarea | false |  | true | true |  |  |

### 改修インシデント / 作業項目

- section.id: work_items
- type: grid
- dataPath: $.work_items
- keyField: work_item_id
- fields: 29

| field | caption | type | grid.visible | width | edit.visible | readonly | search | options |
| --- | --- | --- | --- | ---: | --- | --- | --- | --- |
| work_item_id | 作業ID | text | true | 140 | true | true | true (contains) |  |
| phase | Phase | text | true | 180 | true |  | true (contains) |  |
| title | タイトル | text | true | 280 | true |  | true (contains) |  |
| incident_type | 種別 | select | true | 120 | true |  | true (equals) | refactoring:refactoring, architecture:architecture, feature:feature, bug:bug, design:design, documentation:documentation |
| category | 分類 | select | true | 130 | true |  | true (equals) | source_split:source_split, registry:registry, action:action, viewdef:viewdef, runtime:runtime, chat:chat, markdown:markdown, virtualData:virtualData ... +1 |
| priority | 優先度 | select | true | 90 | true |  | true (equals) | high:high, medium:medium, low:low |
| status | 状態 | select | true | 110 | true |  | true (equals) | 構想:構想, 未着手:未着手, 対応中:対応中, 確認中:確認中, 完了:完了, 保留:保留, 中止:中止 |
| owner | Owner | text | false |  | true |  | true (contains) |  |
| ai_owner | AI Owner | text | false |  | true |  | true (contains) |  |
| created_at | 作成日 | datetime | false | 130 | true |  |  |  |
| updated_at | 更新日 | datetime | false | 130 | true |  |  |  |
| target_files | 対象ファイル | textarea | true | 260 | true |  | true (contains) |  |
| objective | 目的 | textarea | true | 360 | true |  | true (contains) |  |
| background | 背景 | textarea | false |  | true |  | true (contains) |  |
| scope | 対象範囲 | textarea | false |  | true |  | true (contains) |  |
| out_of_scope | 対象外 | textarea | false |  | true |  | true (contains) |  |
| fixed_name_policy | 固定名方針 | textarea | false |  | true |  | true (contains) |  |
| module_policy | module化方針 | textarea | false |  | true |  | true (contains) |  |
| expected_outputs | 成果物 | textarea | false |  | true |  | true (contains) |  |
| risk | リスク | textarea | false |  | true |  | true (contains) |  |
| test_points | 確認観点 | textarea | false |  | true |  | true (contains) |  |
| __work_chat | 作業会話サマリ | chat | false |  | true |  | false |  |
| user_request | 依頼 / 方針 | textarea | false |  | false |  | true (contains) |  |
| ai_response | AI整理 | textarea | false |  | false | true | true (contains) |  |
| latest_user_comment | 追加コメント | textarea | false |  | false |  | true (contains) |  |
| latest_ai_response | AI追加回答 | textarea | false |  | false | true | true (contains) |  |
| discussion_history | 会話履歴 | objectArray | false |  | true |  |  |  |
| decision_log | 判断ログ | objectArray | false |  | true |  |  |  |
| change_history | 変更履歴 | objectArray | false |  | true |  |  |  |

---

## ViewDef JSON

<details>
<summary>元ViewDef JSONを表示</summary>

```json
{
  "app": {
    "name": "No-Code JSON Studio",
    "version": "studio-work-incident-v0.1"
  },
  "views": [
    {
      "id": "studio_work_incident_v0_1",
      "caption": "Studioくん 改修インシデント管理",
      "layout": "header-search-grid-detail",
      "sections": [
        {
          "id": "header",
          "caption": "基本情報",
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
              "field": "target",
              "caption": "対象",
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
              "caption": "Schema Version",
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
              "field": "status",
              "caption": "状態",
              "type": "select",
              "options": [
                "draft",
                "active",
                "closed"
              ],
              "grid": {
                "visible": false
              },
              "edit": {
                "visible": true
              }
            },
            {
              "field": "created_at",
              "caption": "作成日",
              "type": "datetime",
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
              "field": "updated_at",
              "caption": "更新日",
              "type": "datetime",
              "grid": {
                "visible": false
              },
              "edit": {
                "visible": true
              }
            },
            {
              "field": "owner",
              "caption": "Owner",
              "type": "text",
              "grid": {
                "visible": false
              },
              "edit": {
                "visible": true
              }
            },
            {
              "field": "items_count",
              "caption": "作業項目数",
              "type": "number",
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
              "field": "purpose",
              "caption": "目的",
              "type": "textarea",
              "readonly": true,
              "grid": {
                "visible": false
              },
              "edit": {
                "visible": true,
                "readonly": true,
                "height": 90
              }
            },
            {
              "field": "operation_policy",
              "caption": "運用方針",
              "type": "textarea",
              "readonly": true,
              "grid": {
                "visible": false
              },
              "edit": {
                "visible": true,
                "readonly": true,
                "height": 100
              }
            },
            {
              "field": "standard_field_policy",
              "caption": "標準メタフィールド方針",
              "type": "textarea",
              "readonly": true,
              "grid": {
                "visible": false
              },
              "edit": {
                "visible": true,
                "readonly": true,
                "height": 100
              }
            }
          ]
        },
        {
          "id": "work_items",
          "caption": "改修インシデント / 作業項目",
          "type": "grid",
          "dataPath": "$.work_items",
          "keyField": "work_item_id",
          "fields": [
            {
              "field": "work_item_id",
              "caption": "作業ID",
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
              "field": "phase",
              "caption": "Phase",
              "type": "text",
              "grid": {
                "visible": true,
                "width": 180
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
                "width": 280
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
              "field": "incident_type",
              "caption": "種別",
              "type": "select",
              "options": [
                "refactoring",
                "architecture",
                "feature",
                "bug",
                "design",
                "documentation"
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
              }
            },
            {
              "field": "category",
              "caption": "分類",
              "type": "select",
              "options": [
                "source_split",
                "registry",
                "action",
                "viewdef",
                "runtime",
                "chat",
                "markdown",
                "virtualData",
                "other"
              ],
              "grid": {
                "visible": true,
                "width": 130
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
              "caption": "優先度",
              "type": "select",
              "options": [
                "high",
                "medium",
                "low"
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
              }
            },
            {
              "field": "status",
              "caption": "状態",
              "type": "select",
              "options": [
                "構想",
                "未着手",
                "対応中",
                "確認中",
                "完了",
                "保留",
                "中止"
              ],
              "grid": {
                "visible": true,
                "width": 110
              },
              "edit": {
                "visible": true,
                "control": "radio"
              },
              "search": {
                "visible": true,
                "operator": "equals"
              }
            },
            {
              "field": "owner",
              "caption": "Owner",
              "type": "text",
              "grid": {
                "visible": false
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
              "field": "ai_owner",
              "caption": "AI Owner",
              "type": "text",
              "grid": {
                "visible": false
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
              "field": "created_at",
              "caption": "作成日",
              "type": "datetime",
              "grid": {
                "visible": false,
                "width": 130
              },
              "edit": {
                "visible": true
              }
            },
            {
              "field": "updated_at",
              "caption": "更新日",
              "type": "datetime",
              "grid": {
                "visible": false,
                "width": 130
              },
              "edit": {
                "visible": true
              }
            },
            {
              "field": "target_files",
              "caption": "対象ファイル",
              "type": "textarea",
              "grid": {
                "visible": true,
                "width": 260
              },
              "edit": {
                "visible": true,
                "height": 70
              },
              "search": {
                "visible": true,
                "operator": "contains"
              }
            },
            {
              "field": "objective",
              "caption": "目的",
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
              "field": "background",
              "caption": "背景",
              "type": "textarea",
              "grid": {
                "visible": false
              },
              "edit": {
                "visible": true,
                "height": 120
              },
              "search": {
                "visible": true,
                "operator": "contains"
              }
            },
            {
              "field": "scope",
              "caption": "対象範囲",
              "type": "textarea",
              "grid": {
                "visible": false
              },
              "edit": {
                "visible": true,
                "height": 120
              },
              "search": {
                "visible": true,
                "operator": "contains"
              }
            },
            {
              "field": "out_of_scope",
              "caption": "対象外",
              "type": "textarea",
              "grid": {
                "visible": false
              },
              "edit": {
                "visible": true,
                "height": 120
              },
              "search": {
                "visible": true,
                "operator": "contains"
              }
            },
            {
              "field": "fixed_name_policy",
              "caption": "固定名方針",
              "type": "textarea",
              "grid": {
                "visible": false
              },
              "edit": {
                "visible": true,
                "height": 120
              },
              "search": {
                "visible": true,
                "operator": "contains"
              }
            },
            {
              "field": "module_policy",
              "caption": "module化方針",
              "type": "textarea",
              "grid": {
                "visible": false
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
              "field": "expected_outputs",
              "caption": "成果物",
              "type": "textarea",
              "grid": {
                "visible": false
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
              "field": "risk",
              "caption": "リスク",
              "type": "textarea",
              "grid": {
                "visible": false
              },
              "edit": {
                "visible": true,
                "height": 110
              },
              "search": {
                "visible": true,
                "operator": "contains"
              }
            },
            {
              "field": "test_points",
              "caption": "確認観点",
              "type": "textarea",
              "grid": {
                "visible": false
              },
              "edit": {
                "visible": true,
                "height": 110
              },
              "search": {
                "visible": true,
                "operator": "contains"
              }
            },
            {
              "field": "__work_chat",
              "caption": "作業会話サマリ",
              "type": "chat",
              "grid": {
                "visible": false
              },
              "edit": {
                "visible": true,
                "messages": [
                  {
                    "role": "user",
                    "field": "user_request",
                    "label": "依頼 / 方針",
                    "height": 110
                  },
                  {
                    "role": "ai",
                    "field": "ai_response",
                    "label": "AI整理",
                    "readonly": true,
                    "height": 130
                  },
                  {
                    "role": "user",
                    "field": "latest_user_comment",
                    "label": "追加コメント",
                    "height": 90
                  },
                  {
                    "role": "ai",
                    "field": "latest_ai_response",
                    "label": "AI追加回答",
                    "readonly": true,
                    "height": 110
                  }
                ],
                "input": {
                  "enabled": true,
                  "placeholder": "この作業項目への会話メモを追加...",
                  "userField": "latest_user_comment",
                  "aiField": "latest_ai_response",
                  "sendLabel": "送信"
                }
              },
              "search": {
                "visible": false
              },
              "create": {
                "include": false
              },
              "layout": {
                "placement": "detailFooter",
                "order": 800
              }
            },
            {
              "field": "user_request",
              "caption": "依頼 / 方針",
              "type": "textarea",
              "grid": {
                "visible": false
              },
              "edit": {
                "visible": false,
                "height": 110
              },
              "search": {
                "visible": true,
                "operator": "contains"
              },
              "defaultValue": ""
            },
            {
              "field": "ai_response",
              "caption": "AI整理",
              "type": "textarea",
              "readonly": true,
              "grid": {
                "visible": false
              },
              "edit": {
                "visible": false,
                "readonly": true,
                "height": 120
              },
              "search": {
                "visible": true,
                "operator": "contains"
              },
              "defaultValue": ""
            },
            {
              "field": "latest_user_comment",
              "caption": "追加コメント",
              "type": "textarea",
              "grid": {
                "visible": false
              },
              "edit": {
                "visible": false,
                "height": 90
              },
              "search": {
                "visible": true,
                "operator": "contains"
              },
              "defaultValue": ""
            },
            {
              "field": "latest_ai_response",
              "caption": "AI追加回答",
              "type": "textarea",
              "readonly": true,
              "grid": {
                "visible": false
              },
              "edit": {
                "visible": false,
                "readonly": true,
                "height": 110
              },
              "search": {
                "visible": true,
                "operator": "contains"
              },
              "defaultValue": ""
            },
            {
              "field": "discussion_history",
              "caption": "会話履歴",
              "type": "objectArray",
              "grid": {
                "visible": false
              },
              "edit": {
                "visible": true
              },
              "defaultValue": []
            },
            {
              "field": "decision_log",
              "caption": "判断ログ",
              "type": "objectArray",
              "grid": {
                "visible": false
              },
              "edit": {
                "visible": true
              },
              "defaultValue": []
            },
            {
              "field": "change_history",
              "caption": "変更履歴",
              "type": "objectArray",
              "grid": {
                "visible": false
              },
              "edit": {
                "visible": true
              },
              "defaultValue": []
            }
          ],
          "markdown": {
            "aiPrompt": {
              "enabled": true,
              "title": "Studio改修インシデント レビュー / 次アクション生成プロンプト",
              "targetFile": "studio_work_incident_data_v0_1.json",
              "rowSource": "filtered",
              "visibleOnly": true,
              "includeGridJson": true,
              "template": [
                "以下は Studio改修インシデント管理のTSVです。",
                "この内容をもとに、未着手・対応中・保留の作業項目について、次にAIへ依頼すべき作業指示案を作成してください。",
                "",
                "条件:",
                "- 既存機能を壊さない",
                "- Studioくん憲法の Data / ViewDef / Action / Runtime 分離を守る",
                "- Runtime内のData固定名は原則NG",
                "- ただし、憲法・仕様に明記されたStudio標準メタフィールドは例外",
                "- v0.4 / v0.5 / v0.6 の作業範囲を混ぜない",
                "- 出力は作業項目ごとの依頼文候補だけにする",
                "",
                "TSV:"
              ]
            }
          }
        }
      ],
      "markdown": {
        "enabled": true,
        "type": "generic_sections",
        "title": "Studioくん 改修インシデント管理",
        "defaultFileName": "studio_work_incident_export.md",
        "sections": [
          {
            "title": "基本情報",
            "source": "root",
            "fields": [
              {
                "field": "title",
                "caption": "タイトル"
              },
              {
                "field": "target",
                "caption": "対象"
              },
              {
                "field": "schema_version",
                "caption": "Schema Version"
              },
              {
                "field": "status",
                "caption": "状態"
              },
              {
                "field": "purpose",
                "caption": "目的",
                "format": "paragraph"
              },
              {
                "field": "operation_policy",
                "caption": "運用方針",
                "format": "paragraph"
              },
              {
                "field": "standard_field_policy",
                "caption": "標準メタフィールド方針",
                "format": "paragraph"
              }
            ]
          },
          {
            "title": "作業項目一覧",
            "source": "rows",
            "format": "table",
            "fields": [
              {
                "field": "work_item_id",
                "caption": "作業ID"
              },
              {
                "field": "phase",
                "caption": "Phase"
              },
              {
                "field": "title",
                "caption": "タイトル"
              },
              {
                "field": "incident_type",
                "caption": "種別"
              },
              {
                "field": "category",
                "caption": "分類"
              },
              {
                "field": "priority",
                "caption": "優先度"
              },
              {
                "field": "status",
                "caption": "状態"
              },
              {
                "field": "objective",
                "caption": "目的"
              }
            ]
          },
          {
            "title": "作業項目詳細",
            "source": "rows",
            "format": "detail",
            "itemTitle": "{phase}: {title}",
            "fields": [
              {
                "field": "work_item_id",
                "caption": "作業ID"
              },
              {
                "field": "incident_type",
                "caption": "種別"
              },
              {
                "field": "category",
                "caption": "分類"
              },
              {
                "field": "priority",
                "caption": "優先度"
              },
              {
                "field": "status",
                "caption": "状態"
              },
              {
                "field": "target_files",
                "caption": "対象ファイル"
              },
              {
                "field": "objective",
                "caption": "目的",
                "format": "paragraph"
              },
              {
                "field": "background",
                "caption": "背景",
                "format": "paragraph"
              },
              {
                "field": "scope",
                "caption": "対象範囲",
                "format": "paragraph"
              },
              {
                "field": "out_of_scope",
                "caption": "対象外",
                "format": "paragraph"
              },
              {
                "field": "fixed_name_policy",
                "caption": "固定名方針",
                "format": "paragraph"
              },
              {
                "field": "module_policy",
                "caption": "module化方針",
                "format": "paragraph"
              },
              {
                "field": "risk",
                "caption": "リスク",
                "format": "paragraph"
              },
              {
                "field": "test_points",
                "caption": "確認観点",
                "format": "paragraph"
              }
            ],
            "sections": [
              {
                "title": "作業会話サマリ",
                "fields": [
                  {
                    "field": "user_request",
                    "caption": "依頼 / 方針",
                    "format": "paragraph"
                  },
                  {
                    "field": "ai_response",
                    "caption": "AI整理",
                    "format": "paragraph"
                  },
                  {
                    "field": "latest_user_comment",
                    "caption": "追加コメント",
                    "format": "paragraph"
                  },
                  {
                    "field": "latest_ai_response",
                    "caption": "AI追加回答",
                    "format": "paragraph"
                  }
                ]
              },
              {
                "title": "会話履歴",
                "arrayField": "discussion_history",
                "format": "table",
                "fields": [
                  {
                    "field": "history_id",
                    "caption": "History ID"
                  },
                  {
                    "field": "at",
                    "caption": "日時"
                  },
                  {
                    "field": "speaker",
                    "caption": "発言者"
                  },
                  {
                    "field": "topic",
                    "caption": "話題"
                  },
                  {
                    "field": "message",
                    "caption": "内容"
                  }
                ]
              },
              {
                "title": "判断ログ",
                "arrayField": "decision_log",
                "format": "table",
                "fields": [
                  {
                    "field": "decision_id",
                    "caption": "Decision ID"
                  },
                  {
                    "field": "at",
                    "caption": "日時"
                  },
                  {
                    "field": "decision",
                    "caption": "判断"
                  },
                  {
                    "field": "reason",
                    "caption": "理由"
                  }
                ]
              },
              {
                "title": "変更履歴",
                "arrayField": "change_history",
                "format": "table",
                "fields": [
                  {
                    "field": "history_id",
                    "caption": "History ID"
                  },
                  {
                    "field": "at",
                    "caption": "日時"
                  },
                  {
                    "field": "change_type",
                    "caption": "変更種別"
                  },
                  {
                    "field": "before",
                    "caption": "変更前"
                  },
                  {
                    "field": "after",
                    "caption": "変更後"
                  },
                  {
                    "field": "reason",
                    "caption": "理由"
                  }
                ]
              }
            ]
          }
        ]
      }
    }
  ],
  "layout_note": "作業項目ごとに discussion_history / decision_log / change_history を objectArray として保持する。会話サマリは chat 型で detailFooter に表示する。"
}
```

</details>