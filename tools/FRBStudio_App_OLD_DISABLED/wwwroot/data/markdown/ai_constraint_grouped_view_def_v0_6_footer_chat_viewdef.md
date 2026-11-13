# ViewDef定義レポート — AI制約設計書 集約版 / Footer Chat

## 基本情報
- 出力日時: 2026/6/20 9:48:39
- 対象ViewDef: ai_constraint_grouped_view_def_v0_6_footer_chat.json
- app.name: No-Code JSON Studio
- app.version: 0.6-footer-chat
- views: 1

## View / Section 概要
| View | View Caption | Section | Section Caption | Type | DataPath | KeyField | Fields |
| --- | --- | --- | --- | --- | --- | --- | ---: |
| ai_constraint_grouped_v0_6_footer_chat | AI制約設計書 集約版 / Footer Chat | header | 制約設計書 集約版 / 基本情報 | form | $ |  | 7 |
| ai_constraint_grouped_v0_6_footer_chat | AI制約設計書 集約版 / Footer Chat | constraint_groups | 制約グループ一覧 / レビュー対象→個別制約→会話 | grid | $.constraint_groups | group_id | 18 |

## 継承差分サマリ

このViewDefは extends を持たないため、継承差分はありません。

## AI制約設計書 集約版 / Footer Chat

- view.id: ai_constraint_grouped_v0_6_footer_chat
- layout: header-search-grid-detail
- markdown.type: generic_sections
- markdown.title: AI制約設計書 集約版
- markdown.defaultFileName: ai_constraint_spec_aggregated_export.md

### 制約設計書 集約版 / 基本情報

- section.id: header
- type: form
- dataPath: $
- fields: 7

| field | caption | type | grid.visible | width | edit.visible | readonly | search | options |
| --- | --- | --- | --- | ---: | --- | --- | --- | --- |
| title | タイトル | text | false |  | true | true |  |  |
| target | 対象 | text | false |  | true | true |  |  |
| schema_version | Schema Version | text | false |  | true | true |  |  |
| status | 状態 | select | false |  | true |  |  | aggregated_chat_draft, aggregated_draft, reviewing, approved, needs_rework |
| source_constraint_count | 元制約数 | number | false |  | true | true |  |  |
| group_count | 集約グループ数 | number | false |  | true | true |  |  |
| aggregation_policy | 集約方針 | textarea | false |  | true | true |  |  |

### 制約グループ一覧 / レビュー対象→個別制約→会話

- section.id: constraint_groups
- type: grid
- dataPath: $.constraint_groups
- keyField: group_id
- fields: 18

| field | caption | type | grid.visible | width | edit.visible | readonly | search | options |
| --- | --- | --- | --- | ---: | --- | --- | --- | --- |
| no | No | number | true | 60 | true | true |  |  |
| group_id | Group ID | text | true | 150 | true | true | true (contains) |  |
| category | 分類 | select | true | 120 | true |  | true (equals) | アプリ構成, ファイル管理, 画面定義, Field, 一覧・検索, 編集・行操作, 子配列, 保存・関連 ... +4 |
| title | 制約グループ名 | text | true | 260 | true |  | true (contains) |  |
| priority | 優先度 | select | true | 90 | true |  | true (equals) | high, medium, low |
| review_status | レビュー状態 | select | true | 120 | true |  | true (equals) | 集約ドラフト, 確認中, 確認済み, 要再整理, 保留 |
| verification_status | 確認状態 | select | true | 110 | true |  | true (equals) | 未確認, 確認済み, 対象外 |
| constraint_count | 制約数 | number | true | 80 | true | true | true (gte) |  |
| summary | 集約サマリ | textarea | true | 380 | false |  | true (contains) |  |
| scope | 対象範囲 | textarea | false |  | false |  | true (contains) |  |
| __review_target_cards | レビュー対象 | chat | false |  | true |  | false |  |
| __group_chat | 制約グループ会話 | chat | false |  | true |  | false |  |
| constraints | 含まれる個別制約 | objectArray | false |  | true | true |  |  |
| notes | グループメモ | textarea | false |  | false |  | true (contains) |  |
| user_comment | 俺コメント | textarea | true | 260 | false |  | true (contains) |  |
| ai_response | AI回答 | textarea | true | 300 | false | true | true (contains) |  |
| user_reply | 俺追加回答 | textarea | false | 260 | false |  | true (contains) |  |
| ai_followup_response | AI再回答 | textarea | false |  | false | true | true (contains) |  |

---

## ViewDef JSON

<details>
<summary>元ViewDef JSONを表示</summary>

```json
{
  "app": {
    "name": "No-Code JSON Studio",
    "version": "0.6-footer-chat"
  },
  "views": [
    {
      "id": "ai_constraint_grouped_v0_6_footer_chat",
      "caption": "AI制約設計書 集約版 / Footer Chat",
      "layout": "header-search-grid-detail",
      "sections": [
        {
          "id": "header",
          "caption": "制約設計書 集約版 / 基本情報",
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
                "aggregated_chat_draft",
                "aggregated_draft",
                "reviewing",
                "approved",
                "needs_rework"
              ],
              "grid": {
                "visible": false
              },
              "edit": {
                "visible": true
              }
            },
            {
              "field": "source_constraint_count",
              "caption": "元制約数",
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
              "field": "group_count",
              "caption": "集約グループ数",
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
              "field": "aggregation_policy",
              "caption": "集約方針",
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
            }
          ]
        },
        {
          "id": "constraint_groups",
          "caption": "制約グループ一覧 / レビュー対象→個別制約→会話",
          "type": "grid",
          "dataPath": "$.constraint_groups",
          "keyField": "group_id",
          "fields": [
            {
              "field": "no",
              "caption": "No",
              "type": "number",
              "readonly": true,
              "grid": {
                "visible": true,
                "width": 60
              },
              "edit": {
                "visible": true,
                "readonly": true
              }
            },
            {
              "field": "group_id",
              "caption": "Group ID",
              "type": "text",
              "readonly": true,
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
              }
            },
            {
              "field": "category",
              "caption": "分類",
              "type": "select",
              "options": [
                "アプリ構成",
                "ファイル管理",
                "画面定義",
                "Field",
                "一覧・検索",
                "編集・行操作",
                "子配列",
                "保存・関連",
                "Markdown",
                "未実装",
                "追加候補",
                "レビュー"
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
              "field": "title",
              "caption": "制約グループ名",
              "type": "text",
              "grid": {
                "visible": true,
                "width": 260
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
              "field": "review_status",
              "caption": "レビュー状態",
              "type": "select",
              "options": [
                "集約ドラフト",
                "確認中",
                "確認済み",
                "要再整理",
                "保留"
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
              "defaultValue": "集約ドラフト"
            },
            {
              "field": "verification_status",
              "caption": "確認状態",
              "type": "select",
              "options": [
                "未確認",
                "確認済み",
                "対象外"
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
              },
              "defaultValue": "未確認"
            },
            {
              "field": "constraint_count",
              "caption": "制約数",
              "type": "number",
              "readonly": true,
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
                "operator": "gte"
              }
            },
            {
              "field": "summary",
              "caption": "集約サマリ",
              "type": "textarea",
              "grid": {
                "visible": true,
                "width": 380
              },
              "edit": {
                "visible": false,
                "height": 90
              },
              "search": {
                "visible": true,
                "operator": "contains"
              },
              "display_note": "詳細画面では __review_target_cards のconstraintカードとして表示する。"
            },
            {
              "field": "scope",
              "caption": "対象範囲",
              "type": "textarea",
              "grid": {
                "visible": false
              },
              "edit": {
                "visible": false,
                "height": 80
              },
              "search": {
                "visible": true,
                "operator": "contains"
              },
              "display_note": "詳細画面では __review_target_cards のconstraintカードとして表示する。"
            },
            {
              "field": "__review_target_cards",
              "caption": "レビュー対象",
              "type": "chat",
              "grid": {
                "visible": false
              },
              "edit": {
                "visible": true,
                "messages": [
                  {
                    "role": "constraint",
                    "field": "summary",
                    "label": "集約サマリ",
                    "readonly": true,
                    "height": 90
                  },
                  {
                    "role": "constraint",
                    "field": "scope",
                    "label": "対象範囲",
                    "readonly": true,
                    "height": 70
                  }
                ],
                "input": {
                  "enabled": false
                }
              },
              "search": {
                "visible": false
              },
              "create": {
                "include": false
              },
              "display_note": "レビュー対象カード。通常詳細フォーム側に表示し、個別制約と会話の前提として読ませる。",
              "layout": {
                "placement": "detailBody",
                "order": 100
              }
            },
            {
              "field": "__group_chat",
              "caption": "制約グループ会話",
              "type": "chat",
              "grid": {
                "visible": false
              },
              "edit": {
                "visible": true,
                "messages": [
                  {
                    "role": "user",
                    "field": "user_comment",
                    "label": "俺コメント",
                    "height": 110
                  },
                  {
                    "role": "ai",
                    "field": "ai_response",
                    "label": "AI回答",
                    "readonly": true,
                    "height": 110
                  },
                  {
                    "role": "user",
                    "field": "user_reply",
                    "label": "俺追加回答",
                    "height": 90
                  },
                  {
                    "role": "ai",
                    "field": "ai_followup_response",
                    "label": "AI再回答",
                    "readonly": true,
                    "height": 110
                  }
                ],
                "input": {
                  "enabled": true,
                  "placeholder": "この制約グループへのコメントを追加...",
                  "userField": "user_reply",
                  "aiField": "ai_followup_response",
                  "sendLabel": "送信"
                }
              },
              "search": {
                "visible": false
              },
              "create": {
                "include": false
              },
              "display_note": "layout.placement=detailFooter により、子配列（含まれる個別制約）の後ろに表示するコメント用チャット欄。",
              "layout": {
                "placement": "detailFooter",
                "order": 900
              }
            },
            {
              "field": "constraints",
              "caption": "含まれる個別制約",
              "type": "objectArray",
              "readonly": true,
              "grid": {
                "visible": false
              },
              "edit": {
                "visible": true,
                "readonly": true
              },
              "defaultValue": []
            },
            {
              "field": "notes",
              "caption": "グループメモ",
              "type": "textarea",
              "grid": {
                "visible": false
              },
              "edit": {
                "visible": false
              },
              "search": {
                "visible": true,
                "operator": "contains"
              },
              "defaultValue": ""
            },
            {
              "field": "user_comment",
              "caption": "俺コメント",
              "type": "textarea",
              "grid": {
                "visible": true,
                "width": 260
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
              "caption": "AI回答",
              "type": "textarea",
              "readonly": true,
              "grid": {
                "visible": true,
                "width": 300
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
              "field": "user_reply",
              "caption": "俺追加回答",
              "type": "textarea",
              "grid": {
                "visible": false,
                "width": 260
              },
              "edit": {
                "visible": false,
                "height": 100
              },
              "search": {
                "visible": true,
                "operator": "contains"
              },
              "defaultValue": ""
            },
            {
              "field": "ai_followup_response",
              "caption": "AI再回答",
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
            }
          ]
        }
      ],
      "markdown": {
        "enabled": true,
        "type": "generic_sections",
        "title": "AI制約設計書 集約版",
        "defaultFileName": "ai_constraint_spec_aggregated_export.md",
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
                "field": "document_type",
                "caption": "Document Type"
              },
              {
                "field": "status",
                "caption": "状態"
              },
              {
                "field": "source_document",
                "caption": "元ドキュメント"
              },
              {
                "field": "source_constraint_count",
                "caption": "元制約数"
              },
              {
                "field": "group_count",
                "caption": "集約グループ数"
              },
              {
                "field": "aggregation_policy",
                "caption": "集約方針",
                "format": "paragraph"
              }
            ]
          },
          {
            "title": "制約グループ一覧",
            "source": "rows",
            "format": "table",
            "fields": [
              {
                "field": "no",
                "caption": "No"
              },
              {
                "field": "group_id",
                "caption": "Group ID"
              },
              {
                "field": "category",
                "caption": "分類"
              },
              {
                "field": "title",
                "caption": "制約グループ名"
              },
              {
                "field": "priority",
                "caption": "優先度"
              },
              {
                "field": "review_status",
                "caption": "レビュー状態"
              },
              {
                "field": "verification_status",
                "caption": "確認状態"
              },
              {
                "field": "constraint_count",
                "caption": "制約数"
              },
              {
                "field": "summary",
                "caption": "集約サマリ"
              }
            ]
          },
          {
            "title": "制約グループ詳細",
            "source": "rows",
            "format": "detail",
            "itemTitle": "{no}. {group_id}：{title}",
            "fields": [
              {
                "field": "category",
                "caption": "分類"
              },
              {
                "field": "priority",
                "caption": "優先度"
              },
              {
                "field": "review_status",
                "caption": "レビュー状態"
              },
              {
                "field": "verification_status",
                "caption": "確認状態"
              },
              {
                "field": "constraint_count",
                "caption": "制約数"
              }
            ],
            "sections": [
              {
                "title": "レビュー対象",
                "fields": [
                  {
                    "field": "summary",
                    "caption": "集約サマリ",
                    "format": "paragraph"
                  },
                  {
                    "field": "scope",
                    "caption": "対象範囲",
                    "format": "paragraph"
                  },
                  {
                    "field": "notes",
                    "caption": "グループメモ",
                    "format": "paragraph"
                  }
                ]
              },
              {
                "title": "含まれる個別制約",
                "arrayField": "constraints",
                "format": "table",
                "fields": [
                  {
                    "field": "id",
                    "caption": "ID"
                  },
                  {
                    "field": "title",
                    "caption": "タイトル"
                  },
                  {
                    "field": "statement",
                    "caption": "制約本文"
                  }
                ],
                "display_note": "Markdown出力では個別制約を表形式で出す。詳細見出し列挙よりレビューしやすくするため。"
              },
              {
                "title": "制約グループ会話",
                "fields": [
                  {
                    "field": "user_comment",
                    "caption": "俺コメント",
                    "format": "paragraph"
                  },
                  {
                    "field": "ai_response",
                    "caption": "AI回答",
                    "format": "paragraph"
                  },
                  {
                    "field": "user_reply",
                    "caption": "俺追加回答",
                    "format": "paragraph"
                  },
                  {
                    "field": "ai_followup_response",
                    "caption": "AI再回答",
                    "format": "paragraph"
                  }
                ]
              }
            ]
          }
        ]
      }
    }
  ],
  "layout_note": "v0.5: app.js修正前の暫定対応として、レビュー対象カードと制約グループ会話を別々のchatフィールドに分離する。含まれる個別制約をチャットより上に出すには、app.js側のdetail描画順制御が必要。"
}
```

</details>