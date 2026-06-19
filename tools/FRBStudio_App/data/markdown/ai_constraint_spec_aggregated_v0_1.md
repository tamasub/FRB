# No-Code JSON Studio v0.3-draft AI制約設計書 集約版 v0.5-split-review-chat

- 出力日時: 2026/6/20 7:42:35
- 対象: No-Code JSON Studio v0.3-draft
- schema_version: 0.6-footer-chat
- 件数: 12

## 基本情報
- タイトル: No-Code JSON Studio v0.3-draft AI制約設計書 集約版 v0.5-split-review-chat
- 対象: No-Code JSON Studio v0.3-draft
- Schema Version: 0.6-footer-chat
- 元制約数: 84
- 集約グループ数: 12
- 集約方針: 原子制約をカテゴリ単位に集約し、個別制約はサブグリッドで確認する。詳細画面では、レビュー対象（集約サマリ・対象範囲）と制約グループ会話を分離して表示する。

---

## 制約グループ一覧 / レビュー対象→個別制約→会話
| No | Group ID | 分類 | 制約グループ名 | 優先度 | レビュー状態 | 確認状態 | 制約数 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | APP_RUNTIME | アプリ構成 | アプリ実行・起動・常駐 | high | 集約ドラフト | 未確認 | 3 |
| 2 | FILE_SECURITY | ファイル管理 | ファイル配置・安全制約 | high | 集約ドラフト | 未確認 | 9 |
| 3 | VIEW_PATH | 画面定義 | View構造・JSONパス | high | 集約ドラフト | 未確認 | 10 |
| 4 | FIELD_INPUT | Field | Field Type・入力変換 | high | 集約ドラフト | 未確認 | 5 |
| 5 | GRID_SEARCH_SORT | 一覧・検索 | Grid表示・検索・ソート | high | 集約ドラフト | 未確認 | 10 |
| 6 | EDIT_ROW_COPY | 編集・行操作 | 編集・新規・削除・コピー | high | 集約ドラフト | 未確認 | 14 |
| 7 | CHILD_ARRAY | 子配列 | 子配列表示・編集候補 | high | 集約ドラフト | 未確認 | 4 |
| 8 | SAVE_DROP_REL | 保存・関連 | 保存・Drop・view_def関連付け | high | 集約ドラフト | 未確認 | 10 |
| 9 | MARKDOWN | Markdown | Markdown入出力 | medium | 集約ドラフト | 未確認 | 4 |
| 10 | KNOWN_GAPS | 未実装 | 現時点の未実装・弱い制約 | high | 集約ドラフト | 未確認 | 7 |
| 11 | FUTURE_ADD | 追加候補 | 次に追加候補となる制約 | medium | 集約ドラフト | 未確認 | 5 |
| 12 | REVIEW_POLICY | レビュー | 人間レビュー観点 | medium | 集約ドラフト | 未確認 | 3 |