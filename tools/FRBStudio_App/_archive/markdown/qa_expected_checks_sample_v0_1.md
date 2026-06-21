# 期待値チェック分類サンプル

- 出力日時: 2026/6/21 17:11:41
- 件数: 5

## 基本情報
- view_def: qa_expected_checks_sample_view_def_v0_1.json

---

## 期待値チェック
| チェックID | テストパターンID | タイトル | 品質観点 | チェック観点 | リスク | 期待値概要 | 制約ID |
| --- | --- | --- | --- | --- | --- | --- | --- |
| CHK-REL-STATUS-001 | TP-REL-STATUS-001 | approved の Relation は証跡に採用される | 証跡 | 採用確認 | 高 | linked_constraints_count に approved の線だけが反映される | ["REL-STATUS-001"] |
| CHK-REL-STATUS-002 | TP-REL-STATUS-001 | candidate の Relation は正式証跡から除外される | 証跡 | 除外確認 | 高 | candidate の線は approved-only ビューに出ない | ["REL-STATUS-002"] |
| CHK-REL-STATUS-003 | TP-REL-STATUS-001 | derived の contains_check は構造線として採用される | 証跡 | 構造線確認 | 中 | contains_check は structureStatusFilter で通る | ["REL-STATUS-003"] |
| CHK-WB-001 | TP-WB-001 | 顧客名の編集は business_customers に書き戻される | 保存 | 書込確認 | 高 | VirtualData上の編集がsource customersに反映される | ["WB-001"] |
| CHK-MD-001 | TP-MD-001 | Markdown出力ボタンが表示される | 表示 | 表示確認 | 中 | Markdown→Viewer ボタンが利用可能になる | ["MD-001"] |