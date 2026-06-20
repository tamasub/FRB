# ViewDef定義レポート — 【継承元BASE】Screen State Diff Viewer / Full Checks

## 基本情報
- 出力日時: 2026/6/20 8:32:17
- 対象ViewDef: screen_state_diff_view_def_base_v0_2_checks.json
- app.name: No-Code JSON Studio
- app.version: 0.3-draft-base-screen-state-diff
- views: 1

## View / Section 概要
| View | View Caption | Section | Section Caption | Type | DataPath | KeyField | Fields |
| --- | --- | --- | --- | --- | --- | --- | ---: |
| screen_state_diff_main | 【継承元BASE】Screen State Diff Viewer / Full Checks | header | 【継承元BASE】🔥 テスト結果サマリ / 差分強調 | form | $ |  | 16 |
| screen_state_diff_main | 【継承元BASE】Screen State Diff Viewer / Full Checks | checks | 【継承元BASE】チェッカー一覧 / Full Checks | grid | $.checks | name | 8 |

## 継承差分サマリ

このViewDefは extends を持たないため、継承差分はありません。

## 【継承元BASE】Screen State Diff Viewer / Full Checks

- view.id: screen_state_diff_main
- layout: header-search-grid-detail
- markdown.type: screen_state_diff
- markdown.title: 【継承元BASE】画面状態JSON 差分結果
- markdown.defaultFileName: screen_state_diff_base_export.md

### 【継承元BASE】🔥 テスト結果サマリ / 差分強調

- section.id: header
- type: form
- dataPath: $
- fields: 16

| field | caption | type | grid.visible | width | edit.visible | readonly | search | options |
| --- | --- | --- | --- | ---: | --- | --- | --- | --- |
| resultLabel | 判定 | text | false |  | true | true |  |  |
| summary | 差分サマリ | textarea | false |  | true | true |  |  |
| failedCount | 失敗件数 | number | false |  | true | true |  |  |
| failedChecks | 失敗チェッカー一覧 | stringArray | false |  | true | true |  |  |
| firstFailure.name | 初回失敗 Check | text | false |  | true | true |  |  |
| firstFailure.expected | 初回失敗 Expected | textarea | false |  | true | true |  |  |
| firstFailure.actual | 初回失敗 Actual | textarea | false |  | true | true |  |  |
| testId | Test ID | text | false |  | true | true |  |  |
| title | テスト名 | text | false |  | true | true |  |  |
| capturedAt | 取得日時 | datetime | false |  | true | true |  |  |
| url | URL | text | false |  | true | true |  |  |
| status | Status(raw) | select | false |  | true | true | true (equals) | pass, fail |
| actualState.appTitle | 画面タイトル | text | false |  | true | true |  |  |
| actualState.headerText | ヘッダー検出 | boolean | false |  | true | true |  |  |
| actualState.buttons | 検出ボタン一覧 | stringArray | false |  | true | true |  |  |
| actualState.inputs | 検出入力一覧 | objectArray | false |  | true | true |  |  |

### 【継承元BASE】チェッカー一覧 / Full Checks

- section.id: checks
- type: grid
- dataPath: $.checks
- keyField: name
- fields: 8

| field | caption | type | grid.visible | width | edit.visible | readonly | search | options |
| --- | --- | --- | --- | ---: | --- | --- | --- | --- |
| pass | 判定 | boolean | true | 72 | true | true | true (equals) |  |
| name | Check | text | true | 190 | true | true | true (contains) |  |
| type | Type | select | true | 110 | true | true | true (equals) | equals, includesAll, contains, exists |
| target | Target | text | true | 180 | true | true | true (contains) |  |
| missing | Missing | stringArray | true | 210 | true | true |  |  |
| expected | Expected | textarea | true | 360 | true | true | true (contains) |  |
| actual | Actual | textarea | true | 360 | true | true | true (contains) |  |
| message | Message | textarea | false |  | true | true |  |  |

---

## ViewDef JSON

<details>
<summary>元ViewDef JSONを表示</summary>

```json
{
  "app": {
    "name": "No-Code JSON Studio",
    "version": "0.3-draft-base-screen-state-diff"
  },
  "views": [
    {
      "id": "screen_state_diff_main",
      "caption": "【継承元BASE】Screen State Diff Viewer / Full Checks",
      "layout": "header-search-grid-detail",
      "sections": [
        {
          "id": "header",
          "caption": "【継承元BASE】🔥 テスト結果サマリ / 差分強調",
          "type": "form",
          "dataPath": "$",
          "fields": [
            {
              "field": "resultLabel",
              "caption": "判定",
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
              "field": "summary",
              "caption": "差分サマリ",
              "type": "textarea",
              "readonly": true,
              "grid": {
                "visible": false
              },
              "edit": {
                "visible": true,
                "readonly": true,
                "height": 74
              }
            },
            {
              "field": "failedCount",
              "caption": "失敗件数",
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
              "field": "failedChecks",
              "caption": "失敗チェッカー一覧",
              "type": "stringArray",
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
              "field": "firstFailure.name",
              "caption": "初回失敗 Check",
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
              "field": "firstFailure.expected",
              "caption": "初回失敗 Expected",
              "type": "textarea",
              "readonly": true,
              "grid": {
                "visible": false
              },
              "edit": {
                "visible": true,
                "readonly": true,
                "height": 84
              }
            },
            {
              "field": "firstFailure.actual",
              "caption": "初回失敗 Actual",
              "type": "textarea",
              "readonly": true,
              "grid": {
                "visible": false
              },
              "edit": {
                "visible": true,
                "readonly": true,
                "height": 84
              }
            },
            {
              "field": "testId",
              "caption": "Test ID",
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
              "field": "title",
              "caption": "テスト名",
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
              "field": "capturedAt",
              "caption": "取得日時",
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
              "field": "url",
              "caption": "URL",
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
              "caption": "Status(raw)",
              "type": "select",
              "options": [
                "pass",
                "fail"
              ],
              "readonly": true,
              "grid": {
                "visible": false
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
              "field": "actualState.appTitle",
              "caption": "画面タイトル",
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
              "field": "actualState.headerText",
              "caption": "ヘッダー検出",
              "type": "boolean",
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
              "field": "actualState.buttons",
              "caption": "検出ボタン一覧",
              "type": "stringArray",
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
              "field": "actualState.inputs",
              "caption": "検出入力一覧",
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
        },
        {
          "id": "checks",
          "caption": "【継承元BASE】チェッカー一覧 / Full Checks",
          "type": "grid",
          "dataPath": "$.checks",
          "keyField": "name",
          "fields": [
            {
              "field": "pass",
              "caption": "判定",
              "type": "boolean",
              "grid": {
                "visible": true,
                "width": 72
              },
              "edit": {
                "visible": true,
                "readonly": true
              },
              "search": {
                "visible": true,
                "operator": "equals"
              },
              "readonly": true
            },
            {
              "field": "name",
              "caption": "Check",
              "type": "text",
              "grid": {
                "visible": true,
                "width": 190
              },
              "edit": {
                "visible": true,
                "readonly": true
              },
              "search": {
                "visible": true,
                "operator": "contains"
              },
              "readonly": true
            },
            {
              "field": "type",
              "caption": "Type",
              "type": "select",
              "options": [
                "equals",
                "includesAll",
                "contains",
                "exists"
              ],
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
                "operator": "equals"
              },
              "readonly": true
            },
            {
              "field": "target",
              "caption": "Target",
              "type": "text",
              "grid": {
                "visible": true,
                "width": 180
              },
              "edit": {
                "visible": true,
                "readonly": true
              },
              "search": {
                "visible": true,
                "operator": "contains"
              },
              "readonly": true
            },
            {
              "field": "missing",
              "caption": "Missing",
              "type": "stringArray",
              "grid": {
                "visible": true,
                "width": 210
              },
              "edit": {
                "visible": true,
                "readonly": true
              },
              "readonly": true
            },
            {
              "field": "expected",
              "caption": "Expected",
              "type": "textarea",
              "grid": {
                "visible": true,
                "width": 360
              },
              "edit": {
                "visible": true,
                "readonly": true,
                "height": 96
              },
              "search": {
                "visible": true,
                "operator": "contains"
              },
              "readonly": true
            },
            {
              "field": "actual",
              "caption": "Actual",
              "type": "textarea",
              "grid": {
                "visible": true,
                "width": 360
              },
              "edit": {
                "visible": true,
                "readonly": true,
                "height": 96
              },
              "search": {
                "visible": true,
                "operator": "contains"
              },
              "readonly": true
            },
            {
              "field": "message",
              "caption": "Message",
              "type": "textarea",
              "grid": {
                "visible": false
              },
              "edit": {
                "visible": true,
                "readonly": true,
                "height": 80
              },
              "readonly": true
            }
          ]
        }
      ],
      "markdown": {
        "enabled": true,
        "type": "screen_state_diff",
        "title": "【継承元BASE】画面状態JSON 差分結果",
        "defaultFileName": "screen_state_diff_base_export.md"
      }
    }
  ]
}
```

</details>