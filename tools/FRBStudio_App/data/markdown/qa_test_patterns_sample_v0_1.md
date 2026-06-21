# テストパターン分類サンプル

- 出力日時: 2026/6/21 17:13:26
- 件数: 3

## 基本情報
- view_def: qa_test_patterns_sample_view_def_v0_1.json

---

## テストパターン
| テストパターンID | タイトル | 機能領域 | テスト観点 | シナリオ種別 | リスク | メモ |
| --- | --- | --- | --- | --- | --- | --- |
| TP-REL-STATUS-001 | Relation status filter の基本動作確認 | Relation | statusFilter | 正常系 | 高 | approvedだけ正式証跡に採用されるかを見る |
| TP-WB-001 | WriteBackで主対象JSONだけ更新される | WriteBack | WriteBack | 正常系 | 高 | VirtualData表示からsource側へ書き戻す |
| TP-MD-001 | Markdown出力がViewerで読める | Markdown | Markdown出力 | 正常系 | 中 | Markdown出力ボタンとViewer連携の確認 |