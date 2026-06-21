# 観点分類入りExpected定義 v0.1

- 出力日時: 2026/6/20 20:53:15
- schema_version: 0.1
- 件数: 28

## 基本情報
- view_def: qa_shortage_expected_findings_view_def_v0_1.json
- タイトル: 観点分類入りExpected定義 v0.1
- 説明: テストパターンは増やさず、既存TPにぶら下がるチェック項目を品質観点・チェック観点・リスクで分類するためのExpected定義。

---

## 不足検出一覧
| 不足ID | 重要度CD | 重要度 | 検出種別 | 対象種別 | 対象CD | 対象名 | リスク |
| --- | --- | --- | --- | --- | --- | --- | --- |
| GAP-001 | 高 | 高 | 観点×リスク不足 | 品質観点 | display | 表示 | 高 |
| GAP-002 | 高 | 高 | 観点×リスク不足 | 品質観点 | operation | 操作 | 高 |
| GAP-003 | 高 | 高 | 観点×リスク不足 | 品質観点 | error | エラー処理 | 高 |
| GAP-005 | 高 | 高 | 観点×リスク不足 | チェック観点 | structure | 構造線確認 | 高 |
| GAP-006 | 高 | 高 | 観点×リスク不足 | チェック観点 | display | 表示確認 | 高 |
| GAP-008 | 高 | 高 | 観点×リスク不足 | チェック観点 | error | エラー確認 | 高 |
| GAP-028 | 高 | 高 | TP Expected薄い | テストパターン | TP-MD-001 | Markdown出力がViewerで読める | 高 |
| GAP-004 | 中 | 中 | 観点×リスク不足 | 品質観点 | error | エラー処理 | 中 |
| GAP-007 | 中 | 中 | 観点×リスク不足 | チェック観点 | write | 書込確認 | 中 |
| GAP-009 | 中 | 中 | 観点×リスク不足 | チェック観点 | error | エラー確認 | 中 |
| GAP-010 | 中 | 中 | 制約Expected薄い | 制約 | REL-STATUS-001 | REL-STATUS-001 |  |
| GAP-011 | 中 | 中 | 制約Expected薄い | 制約 | REL-STATUS-002 | REL-STATUS-002 |  |
| GAP-012 | 中 | 中 | 制約Expected薄い | 制約 | REL-STATUS-004 | REL-STATUS-004 |  |
| GAP-013 | 中 | 中 | 制約Expected薄い | 制約 | REL-STATUS-003 | REL-STATUS-003 |  |
| GAP-014 | 中 | 中 | 制約Expected薄い | 制約 | REL-STATUS-005 | REL-STATUS-005 |  |
| GAP-015 | 中 | 中 | 制約Expected薄い | 制約 | REL-APPROVAL-001 | REL-APPROVAL-001 |  |
| GAP-016 | 中 | 中 | 制約Expected薄い | 制約 | WB-001 | WB-001 |  |
| GAP-017 | 中 | 中 | 制約Expected薄い | 制約 | WB-002 | WB-002 |  |
| GAP-018 | 中 | 中 | 制約Expected薄い | 制約 | WB-003 | WB-003 |  |
| GAP-019 | 中 | 中 | 制約Expected薄い | 制約 | WB-004 | WB-004 |  |
| GAP-020 | 中 | 中 | 制約Expected薄い | 制約 | FIELD-TYPE-001 | FIELD-TYPE-001 |  |
| GAP-021 | 中 | 中 | 制約Expected薄い | 制約 | MD-001 | MD-001 |  |
| GAP-022 | 中 | 中 | 制約Expected薄い | 制約 | VIEWDEF-REPORT-001 | VIEWDEF-REPORT-001 |  |
| GAP-023 | 中 | 中 | 制約Expected薄い | 制約 | VIEWDEF-REPORT-002 | VIEWDEF-REPORT-002 |  |
| GAP-024 | 中 | 中 | 制約Expected薄い | 制約 | FIELD-TYPE-CAPTION-001 | FIELD-TYPE-CAPTION-001 |  |
| GAP-025 | 中 | 中 | 制約Expected薄い | 制約 | FIELD-TYPE-CAPTION-002 | FIELD-TYPE-CAPTION-002 |  |
| GAP-026 | 中 | 中 | 制約Expected薄い | 制約 | FIELD-TYPE-OPTIONS-001 | FIELD-TYPE-OPTIONS-001 |  |
| GAP-027 | 中 | 中 | 制約Expected薄い | 制約 | FIELD-TYPE-CAPTION-003 | FIELD-TYPE-CAPTION-003 |  |

---

# AI貼り付け用

## Expected / Check 追加候補生成プロンプト

<details open>
<summary>プロンプト + 不足検出TSV を表示</summary>

```text
以下は不足検出一覧のTSVです。
この内容をもとに、qa_expected_checks_classified_v0_1.json に追加する Expected / Check 候補を作成してください。

条件:
- テストパターンIDは増やさない
- expected_checks の追加候補だけ作る
- 既存check_idと重複しない
- quality_axis_cd / check_axis_cd / risk_cd は既存CDを使う
- constraint_ids は不足検出一覧の関連制約IDを優先して使う
- expected_summary には何を確認するかを具体的に書く
- evidence_hint にはどこを見れば証跡になるかを書く
- 不足を無理に埋めるのではなく、不要と判断できるものは note に追加不要理由を書く
- 出力は追加候補だけのJSON配列にしてください

TSV:
不足ID	重要度CD	重要度	検出種別	対象種別	対象CD	対象名	リスク	チェック件数	リスク内訳	判定基準	検出メッセージ	推奨アクション	チェックID一覧	制約ID一覧	テストパターンID一覧
GAP-001	高	高	観点×リスク不足	品質観点	display	表示	高	0	高:0 / 中:0 / 低:0	品質観点=表示 / リスク=高 / 最低1件	品質観点「表示」× リスク「高」の Expected が 0件です。	この領域を確認する Expected / Check を追加するか、意図的に不要なら除外理由をメモに残す。	["CHK-WB-005","CHK-MD-001","CHK-MD-007"]	["FIELD-TYPE-001","MD-001","FIELD-TYPE-CAPTION-003"]	["TP-WB-001","TP-MD-001"]
GAP-002	高	高	観点×リスク不足	品質観点	operation	操作	高	0	高:0 / 中:0 / 低:0	品質観点=操作 / リスク=高 / 最低1件	品質観点「操作」× リスク「高」の Expected が 0件です。	この領域を確認する Expected / Check を追加するか、意図的に不要なら除外理由をメモに残す。	["CHK-REL-STATUS-006"]	["REL-APPROVAL-001"]	["TP-REL-STATUS-001"]
GAP-003	高	高	観点×リスク不足	品質観点	error	エラー処理	高	0	高:0 / 中:0 / 低:0	品質観点=エラー処理 / リスク=高 / 最低1件	品質観点「エラー処理」× リスク「高」の Expected が 0件です。	この領域を確認する Expected / Check を追加するか、意図的に不要なら除外理由をメモに残す。	[]	[]	[]
GAP-005	高	高	観点×リスク不足	チェック観点	structure	構造線確認	高	0	高:0 / 中:0 / 低:0	チェック観点=構造線確認 / リスク=高 / 最低1件	チェック観点「構造線確認」× リスク「高」の Expected が 0件です。	この領域を確認する Expected / Check を追加するか、意図的に不要なら除外理由をメモに残す。	["CHK-REL-STATUS-004"]	["REL-STATUS-003"]	["TP-REL-STATUS-001"]
GAP-006	高	高	観点×リスク不足	チェック観点	display	表示確認	高	0	高:0 / 中:0 / 低:0	チェック観点=表示確認 / リスク=高 / 最低1件	チェック観点「表示確認」× リスク「高」の Expected が 0件です。	この領域を確認する Expected / Check を追加するか、意図的に不要なら除外理由をメモに残す。	["CHK-REL-STATUS-006","CHK-WB-005","CHK-MD-001","CHK-MD-002","CHK-MD-003","CHK-MD-006","CHK-MD-007"]	["REL-APPROVAL-001","FIELD-TYPE-001","MD-001","VIEWDEF-REPORT-001","VIEWDEF-REPORT-002","FIELD-TYPE-OPTIONS-001","FIELD-TYPE-CAPTION-003"]	["TP-REL-STATUS-001","TP-WB-001","TP-MD-001"]
GAP-008	高	高	観点×リスク不足	チェック観点	error	エラー確認	高	0	高:0 / 中:0 / 低:0	チェック観点=エラー確認 / リスク=高 / 最低1件	チェック観点「エラー確認」× リスク「高」の Expected が 0件です。	この領域を確認する Expected / Check を追加するか、意図的に不要なら除外理由をメモに残す。	[]	[]	[]
GAP-028	高	高	TP Expected薄い	テストパターン	TP-MD-001	Markdown出力がViewerで読める	高	7	高:0 / 中:4 / 低:3	合計5件以上 / 高リスク1件以上	テストパターン「TP-MD-001」の Expected は 7件、高リスク 0件です。	このTP配下の確認観点を増やす。TPを増やす前に Expected / Check を追加する。	["CHK-MD-001","CHK-MD-002","CHK-MD-003","CHK-MD-004","CHK-MD-005","CHK-MD-006","CHK-MD-007"]	["MD-001","VIEWDEF-REPORT-001","VIEWDEF-REPORT-002","FIELD-TYPE-CAPTION-001","FIELD-TYPE-CAPTION-002","FIELD-TYPE-OPTIONS-001","FIELD-TYPE-CAPTION-003"]	["TP-MD-001"]
```

</details>

<details>
<summary>Grid JSON を表示</summary>

```json
{
  "view_def": "qa_shortage_expected_findings_view_def_v0_1.json",
  "data_file": "qa_expected_checks_classified_v0_1.json",
  "section": "不足検出一覧",
  "row_count": 7,
  "columns": [
    {
      "field": "finding_id",
      "caption": "不足ID",
      "type": "text"
    },
    {
      "field": "severity_cd",
      "caption": "重要度CD",
      "type": "select"
    },
    {
      "field": "severity_name",
      "caption": "重要度",
      "type": "text"
    },
    {
      "field": "finding_type_name",
      "caption": "検出種別",
      "type": "text"
    },
    {
      "field": "target_type_name",
      "caption": "対象種別",
      "type": "text"
    },
    {
      "field": "target_cd",
      "caption": "対象CD",
      "type": "text"
    },
    {
      "field": "target_name",
      "caption": "対象名",
      "type": "text"
    },
    {
      "field": "risk_name",
      "caption": "リスク",
      "type": "text"
    },
    {
      "field": "check_count",
      "caption": "チェック件数",
      "type": "number"
    },
    {
      "field": "risk_summary",
      "caption": "リスク内訳",
      "type": "text"
    },
    {
      "field": "threshold_summary",
      "caption": "判定基準",
      "type": "text"
    },
    {
      "field": "message",
      "caption": "検出メッセージ",
      "type": "text"
    },
    {
      "field": "suggested_action",
      "caption": "推奨アクション",
      "type": "textarea"
    },
    {
      "field": "check_ids",
      "caption": "チェックID一覧",
      "type": "stringArray"
    },
    {
      "field": "constraint_ids",
      "caption": "制約ID一覧",
      "type": "stringArray"
    },
    {
      "field": "test_pattern_ids",
      "caption": "テストパターンID一覧",
      "type": "stringArray"
    }
  ],
  "rows": [
    {
      "finding_id": "GAP-001",
      "severity_cd": "high",
      "severity_name": "高",
      "finding_type_name": "観点×リスク不足",
      "target_type_name": "品質観点",
      "target_cd": "display",
      "target_name": "表示",
      "risk_name": "高",
      "check_count": 0,
      "risk_summary": "高:0 / 中:0 / 低:0",
      "threshold_summary": "品質観点=表示 / リスク=高 / 最低1件",
      "message": "品質観点「表示」× リスク「高」の Expected が 0件です。",
      "suggested_action": "この領域を確認する Expected / Check を追加するか、意図的に不要なら除外理由をメモに残す。",
      "check_ids": [
        "CHK-WB-005",
        "CHK-MD-001",
        "CHK-MD-007"
      ],
      "constraint_ids": [
        "FIELD-TYPE-001",
        "MD-001",
        "FIELD-TYPE-CAPTION-003"
      ],
      "test_pattern_ids": [
        "TP-WB-001",
        "TP-MD-001"
      ]
    },
    {
      "finding_id": "GAP-002",
      "severity_cd": "high",
      "severity_name": "高",
      "finding_type_name": "観点×リスク不足",
      "target_type_name": "品質観点",
      "target_cd": "operation",
      "target_name": "操作",
      "risk_name": "高",
      "check_count": 0,
      "risk_summary": "高:0 / 中:0 / 低:0",
      "threshold_summary": "品質観点=操作 / リスク=高 / 最低1件",
      "message": "品質観点「操作」× リスク「高」の Expected が 0件です。",
      "suggested_action": "この領域を確認する Expected / Check を追加するか、意図的に不要なら除外理由をメモに残す。",
      "check_ids": [
        "CHK-REL-STATUS-006"
      ],
      "constraint_ids": [
        "REL-APPROVAL-001"
      ],
      "test_pattern_ids": [
        "TP-REL-STATUS-001"
      ]
    },
    {
      "finding_id": "GAP-003",
      "severity_cd": "high",
      "severity_name": "高",
      "finding_type_name": "観点×リスク不足",
      "target_type_name": "品質観点",
      "target_cd": "error",
      "target_name": "エラー処理",
      "risk_name": "高",
      "check_count": 0,
      "risk_summary": "高:0 / 中:0 / 低:0",
      "threshold_summary": "品質観点=エラー処理 / リスク=高 / 最低1件",
      "message": "品質観点「エラー処理」× リスク「高」の Expected が 0件です。",
      "suggested_action": "この領域を確認する Expected / Check を追加するか、意図的に不要なら除外理由をメモに残す。",
      "check_ids": [],
      "constraint_ids": [],
      "test_pattern_ids": []
    },
    {
      "finding_id": "GAP-005",
      "severity_cd": "high",
      "severity_name": "高",
      "finding_type_name": "観点×リスク不足",
      "target_type_name": "チェック観点",
      "target_cd": "structure",
      "target_name": "構造線確認",
      "risk_name": "高",
      "check_count": 0,
      "risk_summary": "高:0 / 中:0 / 低:0",
      "threshold_summary": "チェック観点=構造線確認 / リスク=高 / 最低1件",
      "message": "チェック観点「構造線確認」× リスク「高」の Expected が 0件です。",
      "suggested_action": "この領域を確認する Expected / Check を追加するか、意図的に不要なら除外理由をメモに残す。",
      "check_ids": [
        "CHK-REL-STATUS-004"
      ],
      "constraint_ids": [
        "REL-STATUS-003"
      ],
      "test_pattern_ids": [
        "TP-REL-STATUS-001"
      ]
    },
    {
      "finding_id": "GAP-006",
      "severity_cd": "high",
      "severity_name": "高",
      "finding_type_name": "観点×リスク不足",
      "target_type_name": "チェック観点",
      "target_cd": "display",
      "target_name": "表示確認",
      "risk_name": "高",
      "check_count": 0,
      "risk_summary": "高:0 / 中:0 / 低:0",
      "threshold_summary": "チェック観点=表示確認 / リスク=高 / 最低1件",
      "message": "チェック観点「表示確認」× リスク「高」の Expected が 0件です。",
      "suggested_action": "この領域を確認する Expected / Check を追加するか、意図的に不要なら除外理由をメモに残す。",
      "check_ids": [
        "CHK-REL-STATUS-006",
        "CHK-WB-005",
        "CHK-MD-001",
        "CHK-MD-002",
        "CHK-MD-003",
        "CHK-MD-006",
        "CHK-MD-007"
      ],
      "constraint_ids": [
        "REL-APPROVAL-001",
        "FIELD-TYPE-001",
        "MD-001",
        "VIEWDEF-REPORT-001",
        "VIEWDEF-REPORT-002",
        "FIELD-TYPE-OPTIONS-001",
        "FIELD-TYPE-CAPTION-003"
      ],
      "test_pattern_ids": [
        "TP-REL-STATUS-001",
        "TP-WB-001",
        "TP-MD-001"
      ]
    },
    {
      "finding_id": "GAP-008",
      "severity_cd": "high",
      "severity_name": "高",
      "finding_type_name": "観点×リスク不足",
      "target_type_name": "チェック観点",
      "target_cd": "error",
      "target_name": "エラー確認",
      "risk_name": "高",
      "check_count": 0,
      "risk_summary": "高:0 / 中:0 / 低:0",
      "threshold_summary": "チェック観点=エラー確認 / リスク=高 / 最低1件",
      "message": "チェック観点「エラー確認」× リスク「高」の Expected が 0件です。",
      "suggested_action": "この領域を確認する Expected / Check を追加するか、意図的に不要なら除外理由をメモに残す。",
      "check_ids": [],
      "constraint_ids": [],
      "test_pattern_ids": []
    },
    {
      "finding_id": "GAP-028",
      "severity_cd": "high",
      "severity_name": "高",
      "finding_type_name": "TP Expected薄い",
      "target_type_name": "テストパターン",
      "target_cd": "TP-MD-001",
      "target_name": "Markdown出力がViewerで読める",
      "risk_name": "高",
      "check_count": 7,
      "risk_summary": "高:0 / 中:4 / 低:3",
      "threshold_summary": "合計5件以上 / 高リスク1件以上",
      "message": "テストパターン「TP-MD-001」の Expected は 7件、高リスク 0件です。",
      "suggested_action": "このTP配下の確認観点を増やす。TPを増やす前に Expected / Check を追加する。",
      "check_ids": [
        "CHK-MD-001",
        "CHK-MD-002",
        "CHK-MD-003",
        "CHK-MD-004",
        "CHK-MD-005",
        "CHK-MD-006",
        "CHK-MD-007"
      ],
      "constraint_ids": [
        "MD-001",
        "VIEWDEF-REPORT-001",
        "VIEWDEF-REPORT-002",
        "FIELD-TYPE-CAPTION-001",
        "FIELD-TYPE-CAPTION-002",
        "FIELD-TYPE-OPTIONS-001",
        "FIELD-TYPE-CAPTION-003"
      ],
      "test_pattern_ids": [
        "TP-MD-001"
      ]
    }
  ]
}
```

</details>