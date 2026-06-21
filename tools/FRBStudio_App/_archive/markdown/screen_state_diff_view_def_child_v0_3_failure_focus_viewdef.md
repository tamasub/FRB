# ViewDef定義レポート — 【継承先CHILD】Screen State Diff Failure Focus View

## 基本情報
- 出力日時: 2026/6/20 9:54:37
- 対象ViewDef: screen_state_diff_view_def_child_v0_3_failure_focus.json
- app.name: No-Code JSON Studio
- app.version: 0.3-draft-child-failure-focus
- extends(raw): screen_state_diff_view_def_base_v0_2_checks.json
- extends(resolved): screen_state_diff_view_def_base_v0_2_checks.json
- views: 1

## View / Section 概要
| View | View Caption | Section | Section Caption | Type | DataPath | KeyField | Fields |
| --- | --- | --- | --- | --- | --- | --- | ---: |
| screen_state_diff_main | 【継承先CHILD】Screen State Diff Failure Focus View | header | 【継承先CHILD】🚨 テスト結果サマリ / Failure Focus |  |  |  | 0 |
| screen_state_diff_main | 【継承先CHILD】Screen State Diff Failure Focus View | checks | 【継承先CHILD】失敗原因確認 / Failure Focus View |  |  |  | 8 |

## 継承差分サマリ

- 継承元: screen_state_diff_view_def_base_v0_2_checks.json
- 差分件数: 13
- 内訳: 変更 13 / 追加 0 / 削除 0

### View差分
| 種別 | 対象 | 項目 | 親BASE | 子CHILD / 解決済み |
| --- | --- | --- | --- | --- |
| 変更 | view:screen_state_diff_main | caption | 【継承元BASE】Screen State Diff Viewer / Full Checks | 【継承先CHILD】Screen State Diff Failure Focus View |
| 変更 | view:screen_state_diff_main | markdown.title | 【継承元BASE】画面状態JSON 差分結果 | 【継承先CHILD】画面状態JSON 差分失敗原因 |
| 変更 | view:screen_state_diff_main | markdown.defaultFileName | screen_state_diff_base_export.md | screen_state_diff_child_failure_focus_export.md |

### Section差分
| 種別 | 対象 | 項目 | 親BASE | 子CHILD / 解決済み |
| --- | --- | --- | --- | --- |
| 変更 | screen_state_diff_main / section:header | caption | 【継承元BASE】🔥 テスト結果サマリ / 差分強調 | 【継承先CHILD】🚨 テスト結果サマリ / Failure Focus |
| 変更 | screen_state_diff_main / section:checks | caption | 【継承元BASE】チェッカー一覧 / Full Checks | 【継承先CHILD】失敗原因確認 / Failure Focus View |

### Field差分
| 種別 | 対象 | 項目 | 親BASE | 子CHILD / 解決済み |
| --- | --- | --- | --- | --- |
| 変更 | screen_state_diff_main / checks / field:name | grid.width | 190 | 220 |
| 変更 | screen_state_diff_main / checks / field:type | grid.visible | true | false |
| 変更 | screen_state_diff_main / checks / field:target | grid.width | 180 | 190 |
| 変更 | screen_state_diff_main / checks / field:missing | grid.width | 210 | 240 |
| 変更 | screen_state_diff_main / checks / field:expected | grid.width | 360 | 420 |
| 変更 | screen_state_diff_main / checks / field:actual | grid.width | 360 | 420 |
| 変更 | screen_state_diff_main / checks / field:message | grid.visible | false | true |
| 変更 | screen_state_diff_main / checks / field:message | grid.width | （未定義） | 520 |

## 【継承先CHILD】Screen State Diff Failure Focus View

- view.id: screen_state_diff_main
- markdown.type: screen_state_diff
- markdown.title: 【継承先CHILD】画面状態JSON 差分失敗原因
- markdown.defaultFileName: screen_state_diff_child_failure_focus_export.md

### 【継承先CHILD】🚨 テスト結果サマリ / Failure Focus

- section.id: header
- fields: 0

### 【継承先CHILD】失敗原因確認 / Failure Focus View

- section.id: checks
- fields: 8

| field | caption | type | grid.visible | width | edit.visible | readonly | search | options |
| --- | --- | --- | --- | ---: | --- | --- | --- | --- |
| pass | 判定 | text | true | 72 |  |  |  |  |
| name | Check | text | true | 220 |  |  |  |  |
| type |  | text | false |  |  |  |  |  |
| target | Target | text | true | 190 |  |  |  |  |
| missing | Missing | text | true | 240 |  |  |  |  |
| expected | Expected | text | true | 420 |  |  |  |  |
| actual | Actual | text | true | 420 |  |  |  |  |
| message | Message | text | true | 520 |  |  |  |  |

---

## 解決済みViewDef概要

このViewDefは extends を持つため、現在画面描画に使っている解決済みViewDefの概要も併記します。

| View | View Caption | Section | Section Caption | Type | DataPath | KeyField | Fields |
| --- | --- | --- | --- | --- | --- | --- | ---: |
| screen_state_diff_main | 【継承先CHILD】Screen State Diff Failure Focus View | header | 【継承先CHILD】🚨 テスト結果サマリ / Failure Focus | form | $ |  | 16 |
| screen_state_diff_main | 【継承先CHILD】Screen State Diff Failure Focus View | checks | 【継承先CHILD】失敗原因確認 / Failure Focus View | grid | $.checks | name | 8 |

## Resolved: 【継承先CHILD】Screen State Diff Failure Focus View

- view.id: screen_state_diff_main
- layout: header-search-grid-detail
- markdown.type: screen_state_diff
- markdown.title: 【継承先CHILD】画面状態JSON 差分失敗原因
- markdown.defaultFileName: screen_state_diff_child_failure_focus_export.md

### 【継承先CHILD】🚨 テスト結果サマリ / Failure Focus

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

### 【継承先CHILD】失敗原因確認 / Failure Focus View

- section.id: checks
- type: grid
- dataPath: $.checks
- keyField: name
- fields: 8

| field | caption | type | grid.visible | width | edit.visible | readonly | search | options |
| --- | --- | --- | --- | ---: | --- | --- | --- | --- |
| pass | 判定 | boolean | true | 72 | true | true | true (equals) |  |
| name | Check | text | true | 220 | true | true | true (contains) |  |
| type | Type | select | false | 110 | true | true | true (equals) | equals, includesAll, contains, exists |
| target | Target | text | true | 190 | true | true | true (contains) |  |
| missing | Missing | stringArray | true | 240 | true | true |  |  |
| expected | Expected | textarea | true | 420 | true | true | true (contains) |  |
| actual | Actual | textarea | true | 420 | true | true | true (contains) |  |
| message | Message | textarea | true | 520 | true | true |  |  |

---

## ViewDef JSON

<details>
<summary>元ViewDef JSONを表示</summary>

```json
{
  "app": {
    "name": "No-Code JSON Studio",
    "version": "0.3-draft-child-failure-focus"
  },
  "extends": "screen_state_diff_view_def_base_v0_2_checks.json",
  "views": [
    {
      "id": "screen_state_diff_main",
      "caption": "【継承先CHILD】Screen State Diff Failure Focus View",
      "sections": [
        {
          "id": "header",
          "caption": "【継承先CHILD】🚨 テスト結果サマリ / Failure Focus"
        },
        {
          "id": "checks",
          "caption": "【継承先CHILD】失敗原因確認 / Failure Focus View",
          "fields": [
            {
              "field": "pass",
              "caption": "判定",
              "grid": {
                "visible": true,
                "width": 72
              }
            },
            {
              "field": "name",
              "caption": "Check",
              "grid": {
                "visible": true,
                "width": 220
              }
            },
            {
              "field": "type",
              "grid": {
                "visible": false
              }
            },
            {
              "field": "target",
              "caption": "Target",
              "grid": {
                "visible": true,
                "width": 190
              }
            },
            {
              "field": "missing",
              "caption": "Missing",
              "grid": {
                "visible": true,
                "width": 240
              }
            },
            {
              "field": "expected",
              "caption": "Expected",
              "grid": {
                "visible": true,
                "width": 420
              }
            },
            {
              "field": "actual",
              "caption": "Actual",
              "grid": {
                "visible": true,
                "width": 420
              }
            },
            {
              "field": "message",
              "caption": "Message",
              "grid": {
                "visible": true,
                "width": 520
              }
            }
          ]
        }
      ],
      "markdown": {
        "enabled": true,
        "type": "screen_state_diff",
        "title": "【継承先CHILD】画面状態JSON 差分失敗原因",
        "defaultFileName": "screen_state_diff_child_failure_focus_export.md"
      }
    }
  ]
}
```

</details>

<details>
<summary>解決済みViewDef JSONを表示</summary>

```json
{
  "app": {
    "name": "No-Code JSON Studio",
    "version": "0.3-draft-child-failure-focus"
  },
  "views": [
    {
      "id": "screen_state_diff_main",
      "caption": "【継承先CHILD】Screen State Diff Failure Focus View",
      "layout": "header-search-grid-detail",
      "sections": [
        {
          "id": "header",
          "caption": "【継承先CHILD】🚨 テスト結果サマリ / Failure Focus",
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
          "caption": "【継承先CHILD】失敗原因確認 / Failure Focus View",
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
                "width": 220
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
                "visible": false,
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
              "field": "missing",
              "caption": "Missing",
              "type": "stringArray",
              "grid": {
                "visible": true,
                "width": 240
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
                "width": 420
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
                "width": 420
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
                "visible": true,
                "width": 520
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
        "title": "【継承先CHILD】画面状態JSON 差分失敗原因",
        "defaultFileName": "screen_state_diff_child_failure_focus_export.md"
      }
    }
  ],
  "_resolved_extends": [
    "screen_state_diff_view_def_base_v0_2_checks.json"
  ]
}
```

</details>