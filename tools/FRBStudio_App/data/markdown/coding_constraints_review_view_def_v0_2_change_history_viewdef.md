# ViewDef定義レポート — Studioくん憲法レビュー / 承認セレモニー

## 基本情報
- 出力日時: 2026/6/21 16:31:36
- 対象ViewDef: coding_constraints_review_view_def_v0_2_change_history.json
- app.name: No-Code JSON Studio
- app.version: coding-constraints-review-v0.2-change-history
- views: 1

## View / Section 概要
| View | View Caption | Section | Section Caption | Type | DataPath | KeyField | Fields |
| --- | --- | --- | --- | --- | --- | --- | ---: |
| coding_constraints_review_v0_1 | Studioくん憲法レビュー / 承認セレモニー | header | Studioくん憲法 / 基本情報 | form | $ |  | 10 |
| coding_constraints_review_v0_1 | Studioくん憲法レビュー / 承認セレモニー | constitution_sections | Studioくん憲法 条文レビュー / 承認セレモニー | grid | $.constitution_sections | section_id | 22 |

## 継承差分サマリ

このViewDefは extends を持たないため、継承差分はありません。

## 解決サマリ

- 読込済み共通Type namespace: qa / relation / business / core
- fieldType参照: 0件
- fieldType caption未指定: 0件
- extends / fieldType 解決による差分: なし

## Studioくん憲法レビュー / 承認セレモニー

- view.id: coding_constraints_review_v0_1
- layout: header-search-grid-detail
- markdown.type: generic_sections
- markdown.title: Studioくん憲法 レビュー記録
- markdown.defaultFileName: coding_constraints_review_export.md

### Studioくん憲法 / 基本情報

- section.id: header
- type: form
- dataPath: $
- fields: 10

| field | caption | type | grid.visible | width | edit.visible | readonly | search | options |
| --- | --- | --- | --- | ---: | --- | --- | --- | --- |
| title | タイトル | text | false |  | true | true |  |  |
| target | 対象 | text | false |  | true | true |  |  |
| schema_version | Schema Version | text | false |  | true | true |  |  |
| status | 状態 | select | false |  | true |  |  | ceremony_review_draft:ceremony_review_draft, reviewing:reviewing, approved:approved, needs_rework:needs_rework, ceremony_review_draft_with_change_history:ceremony_review_draft_with_change_history |
| source_version | Source Version | text | false |  | true | true |  |  |
| section_count | レビュー条文数 | number | false |  | true | true |  |  |
| approved_count | 承認済み数 | number | false |  | true | true |  |  |
| approval_policy | 承認方針 | textarea | false |  | true | true |  |  |
| preamble | 前文 / この文書の目的 | textarea | false |  | true | true |  |  |
| change_history_policy | 変更履歴方針 | textarea | false |  | true | true |  |  |

### Studioくん憲法 条文レビュー / 承認セレモニー

- section.id: constitution_sections
- type: grid
- dataPath: $.constitution_sections
- keyField: section_id
- fields: 22

| field | caption | type | grid.visible | width | edit.visible | readonly | search | options |
| --- | --- | --- | --- | ---: | --- | --- | --- | --- |
| no | 条 | number | true | 60 | true | true | true (gte) |  |
| section_id | Section ID | text | true | 150 | true | true | true (contains) |  |
| category | 分類 | select | true | 140 | true |  | true (equals) | 理念:理念, アーキテクチャ:アーキテクチャ, 設計パターン:設計パターン, Data:Data, ViewDef:ViewDef, Action:Action, Replay:Replay, Diff:Diff ... +15 |
| title | 条文名 | text | true | 260 | true |  | true (contains) |  |
| priority | 優先度 | select | true | 90 | true |  | true (equals) | high:high, medium:medium, low:low |
| review_status | レビュー状態 | select | true | 120 | true |  | true (equals) | 建国レビュー:建国レビュー, 確認中:確認中, 確認済み:確認済み, 要再整理:要再整理, 保留:保留 |
| verification_status | 確認状態 | select | true | 110 | true |  | true (equals) | 未確認:未確認, 確認済み:確認済み, 対象外:対象外 |
| approval_decision | 承認 | select | true | 120 | true |  | true (equals) | 未承認:未承認, 承認する:承認する, 差戻し:差戻し, 保留:保留 |
| summary | 要約 | textarea | true | 420 | false | true | true (contains) |  |
| body | 条文本文 | textarea | false |  | false | true | true (contains) |  |
| ceremony_phrase | 承認セレモニー文 | textarea | false |  | false | true | true (contains) |  |
| __review_target_cards | レビュー対象 | chat | false |  | true |  | false |  |
| __section_chat | 条文レビュー会話 | chat | false |  | true |  | false |  |
| user_comment | 俺コメント | textarea | true | 260 | false |  | true (contains) |  |
| ai_response | AI回答 | textarea | true | 300 | false | true | true (contains) |  |
| user_reply | 俺追加回答 | textarea | false | 260 | false |  | true (contains) |  |
| ai_followup_response | AI再回答 | textarea | false |  | false | true | true (contains) |  |
| approved_by | 承認者 | text | false | 120 | true |  | true (contains) |  |
| approved_at | 承認日時 | datetime | false | 160 | true |  | true (contains) |  |
| approval_stamp | 承認印 | text | false |  | true |  | false |  |
| notes | メモ | textarea | false |  | true |  | true (contains) |  |
| change_history | 仕様変更履歴 | objectArray | false |  | true | true |  |  |

---

## ViewDef JSON

<details>
<summary>元ViewDef JSONを表示</summary>

```json
{
  "app": {
    "name": "No-Code JSON Studio",
    "version": "coding-constraints-review-v0.2-change-history"
  },
  "views": [
    {
      "id": "coding_constraints_review_v0_1",
      "caption": "Studioくん憲法レビュー / 承認セレモニー",
      "layout": "header-search-grid-detail",
      "sections": [
        {
          "id": "header",
          "caption": "Studioくん憲法 / 基本情報",
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
                "ceremony_review_draft",
                "reviewing",
                "approved",
                "needs_rework",
                "ceremony_review_draft_with_change_history"
              ],
              "grid": {
                "visible": false
              },
              "edit": {
                "visible": true
              }
            },
            {
              "field": "source_version",
              "caption": "Source Version",
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
              "field": "section_count",
              "caption": "レビュー条文数",
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
              "field": "approved_count",
              "caption": "承認済み数",
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
              "field": "approval_policy",
              "caption": "承認方針",
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
              "field": "preamble",
              "caption": "前文 / この文書の目的",
              "type": "textarea",
              "readonly": true,
              "grid": {
                "visible": false
              },
              "edit": {
                "visible": true,
                "readonly": true,
                "height": 160
              }
            },
            {
              "field": "change_history_policy",
              "caption": "変更履歴方針",
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
          "id": "constitution_sections",
          "caption": "Studioくん憲法 条文レビュー / 承認セレモニー",
          "type": "grid",
          "dataPath": "$.constitution_sections",
          "keyField": "section_id",
          "fields": [
            {
              "field": "no",
              "caption": "条",
              "type": "number",
              "readonly": true,
              "grid": {
                "visible": true,
                "width": 60
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
              "field": "section_id",
              "caption": "Section ID",
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
                "理念",
                "アーキテクチャ",
                "設計パターン",
                "Data",
                "ViewDef",
                "Action",
                "Replay",
                "Diff",
                "Constraint",
                "変更管理",
                "品質保護",
                "Chat",
                "ReadOnly",
                "URL",
                "AIテスト物語",
                "認知支援",
                "命名",
                "ファイル構成",
                "AI協働",
                "人間協働",
                "憲法",
                "まとめ",
                "未分類"
              ],
              "grid": {
                "visible": true,
                "width": 140
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
              "caption": "条文名",
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
                "建国レビュー",
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
              "defaultValue": "建国レビュー"
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
              "field": "approval_decision",
              "caption": "承認",
              "type": "select",
              "options": [
                "未承認",
                "承認する",
                "差戻し",
                "保留"
              ],
              "grid": {
                "visible": true,
                "width": 120
              },
              "edit": {
                "visible": true,
                "control": "radio"
              },
              "search": {
                "visible": true,
                "operator": "equals"
              },
              "defaultValue": "未承認"
            },
            {
              "field": "summary",
              "caption": "要約",
              "type": "textarea",
              "readonly": true,
              "grid": {
                "visible": true,
                "width": 420
              },
              "edit": {
                "visible": false,
                "readonly": true,
                "height": 90
              },
              "search": {
                "visible": true,
                "operator": "contains"
              },
              "display_note": "詳細画面では __review_target_cards の条文カードとして表示する。"
            },
            {
              "field": "body",
              "caption": "条文本文",
              "type": "textarea",
              "readonly": true,
              "grid": {
                "visible": false
              },
              "edit": {
                "visible": false,
                "readonly": true,
                "height": 260
              },
              "search": {
                "visible": true,
                "operator": "contains"
              },
              "display_note": "詳細画面では __review_target_cards の条文本文として表示する。"
            },
            {
              "field": "ceremony_phrase",
              "caption": "承認セレモニー文",
              "type": "textarea",
              "readonly": true,
              "grid": {
                "visible": false
              },
              "edit": {
                "visible": false,
                "readonly": true,
                "height": 70
              },
              "search": {
                "visible": true,
                "operator": "contains"
              }
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
                    "label": "条文要約",
                    "readonly": true,
                    "height": 90
                  },
                  {
                    "role": "constraint",
                    "field": "body",
                    "label": "条文本文",
                    "readonly": true,
                    "height": 260
                  },
                  {
                    "role": "system",
                    "field": "ceremony_phrase",
                    "label": "承認セレモニー",
                    "readonly": true,
                    "height": 70,
                    "embeddedFields": [
                      {
                        "field": "approval_decision",
                        "label": "この条文を",
                        "type": "select",
                        "control": "radio",
                        "options": [
                          "未承認",
                          "承認する",
                          "差戻し",
                          "保留"
                        ]
                      },
                      {
                        "field": "verification_status",
                        "label": "確認状態",
                        "type": "select",
                        "control": "radio",
                        "options": [
                          "未確認",
                          "確認済み",
                          "対象外"
                        ]
                      }
                    ]
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
              "display_note": "レビュー対象カード。条文要約・本文・承認セレモニーを詳細画面上部に表示する。",
              "layout": {
                "placement": "detailBody",
                "order": 100
              }
            },
            {
              "field": "__section_chat",
              "caption": "条文レビュー会話",
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
                    "height": 120
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
                    "height": 120
                  }
                ],
                "input": {
                  "enabled": true,
                  "placeholder": "この条文へのレビューコメントを追加...",
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
              "display_note": "layout.placement=detailFooter により、詳細画面下部に表示する条文レビュー会話欄。",
              "layout": {
                "placement": "detailFooter",
                "order": 900
              }
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
            },
            {
              "field": "approved_by",
              "caption": "承認者",
              "type": "text",
              "grid": {
                "visible": false,
                "width": 120
              },
              "edit": {
                "visible": true
              },
              "search": {
                "visible": true,
                "operator": "contains"
              },
              "defaultValue": ""
            },
            {
              "field": "approved_at",
              "caption": "承認日時",
              "type": "datetime",
              "grid": {
                "visible": false,
                "width": 160
              },
              "edit": {
                "visible": true
              },
              "search": {
                "visible": true,
                "operator": "contains"
              },
              "defaultValue": ""
            },
            {
              "field": "approval_stamp",
              "caption": "承認印",
              "type": "text",
              "grid": {
                "visible": false
              },
              "edit": {
                "visible": true
              },
              "search": {
                "visible": false
              },
              "defaultValue": ""
            },
            {
              "field": "notes",
              "caption": "メモ",
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
              },
              "defaultValue": ""
            },
            {
              "field": "change_history",
              "caption": "仕様変更履歴",
              "type": "objectArray",
              "readonly": true,
              "grid": {
                "visible": false
              },
              "edit": {
                "visible": true,
                "readonly": true
              },
              "defaultValue": [],
              "display_note": "レビューで条文・仕様を変更した場合、変更前後・理由・会話を残すサブグリッド。"
            }
          ],
          "markdown": {
            "aiPrompt": {
              "enabled": true,
              "title": "Studioくん憲法レビュー コメント生成プロンプト",
              "targetFile": "coding_constraints_review_data_v0_1.json",
              "rowSource": "filtered",
              "visibleOnly": true,
              "includeGridJson": true,
              "template": [
                "以下は Studioくん憲法レビュー一覧のTSVです。",
                "この内容をもとに、未承認または差戻しの条文について、レビューコメント案を作成してください。",
                "",
                "条件:",
                "- 条文の思想を壊さない",
                "- 修正が必要な場合のみ提案する",
                "- 出力はコメント候補だけにする",
                "- approval_decision を勝手に承認する値へ変更しない",
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
        "title": "Studioくん憲法 レビュー記録",
        "defaultFileName": "coding_constraints_review_export.md",
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
                "field": "source_version",
                "caption": "Source Version"
              },
              {
                "field": "section_count",
                "caption": "レビュー条文数"
              },
              {
                "field": "approved_count",
                "caption": "承認済み数"
              },
              {
                "field": "approval_policy",
                "caption": "承認方針",
                "format": "paragraph"
              },
              {
                "field": "preamble",
                "caption": "前文",
                "format": "paragraph"
              },
              {
                "field": "change_history_policy",
                "caption": "変更履歴方針",
                "format": "paragraph"
              }
            ]
          },
          {
            "title": "条文レビュー一覧",
            "source": "rows",
            "format": "table",
            "fields": [
              {
                "field": "no",
                "caption": "条"
              },
              {
                "field": "section_id",
                "caption": "Section ID"
              },
              {
                "field": "category",
                "caption": "分類"
              },
              {
                "field": "title",
                "caption": "条文名"
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
                "field": "approval_decision",
                "caption": "承認"
              },
              {
                "field": "summary",
                "caption": "要約"
              }
            ]
          },
          {
            "title": "条文レビュー詳細",
            "source": "rows",
            "format": "detail",
            "itemTitle": "第{no}条：{title}",
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
                "field": "approval_decision",
                "caption": "承認"
              },
              {
                "field": "approved_by",
                "caption": "承認者"
              },
              {
                "field": "approved_at",
                "caption": "承認日時"
              }
            ],
            "sections": [
              {
                "title": "レビュー対象",
                "fields": [
                  {
                    "field": "summary",
                    "caption": "要約",
                    "format": "paragraph"
                  },
                  {
                    "field": "body",
                    "caption": "条文本文",
                    "format": "paragraph"
                  },
                  {
                    "field": "ceremony_phrase",
                    "caption": "承認セレモニー",
                    "format": "paragraph"
                  },
                  {
                    "field": "notes",
                    "caption": "メモ",
                    "format": "paragraph"
                  }
                ]
              },
              {
                "title": "条文レビュー会話",
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
              },
              {
                "title": "仕様変更履歴",
                "arrayField": "change_history",
                "format": "table",
                "fields": [
                  {
                    "field": "history_id",
                    "caption": "History ID"
                  },
                  {
                    "field": "revision",
                    "caption": "Revision"
                  },
                  {
                    "field": "changed_at",
                    "caption": "変更日"
                  },
                  {
                    "field": "changed_by",
                    "caption": "変更者"
                  },
                  {
                    "field": "change_type",
                    "caption": "変更種別"
                  },
                  {
                    "field": "target_fields",
                    "caption": "対象フィールド"
                  },
                  {
                    "field": "before_title",
                    "caption": "変更前タイトル"
                  },
                  {
                    "field": "after_title",
                    "caption": "変更後タイトル"
                  },
                  {
                    "field": "reason",
                    "caption": "変更理由"
                  }
                ]
              }
            ]
          }
        ]
      }
    }
  ],
  "layout_note": "ai_constraint_grouped_view_def_v0_6_footer_chat.json の構成に寄せ、レビュー対象カードを detailBody、条文レビュー会話を detailFooter に配置する。承認セレモニー用に approval_decision を radio 表示できるようにした。"
}
```

</details>