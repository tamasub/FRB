# v0.13.6 Markdown Copilot Table Review Fixture Notes

## 目的

v0.13系で追加した Markdown Block Model / SentenceBlock操作 / Markdown表セル編集 / Sidecarコメント / コメントレビューUI / Save Safety を、1つの架空Copilot表形式計画案でまとめて確認するためのfixtureを追加した。

## 追加ファイル

- `wwwroot/data/markdown/copilot_table_review_fixture_v0_13_6.md`
- `wwwroot/data/markdown/copilot_table_review_fixture_v0_13_6.md.comments.json`
- `wwwroot/js/runtime/MARKDOWN_COPILOT_TABLE_REVIEW_FIXTURE_NOTES_v0_13_6.md`

## 検証観点

1. Markdown表セルをクリックして編集できること。
2. TableCellコメントが本文を汚さず sidecar JSON に保持されること。
3. コメントレビュー一覧から対象Block / TableCellへジャンプできること。
4. 上書き保存時に Save Safety が通ること。
5. fixtureが実会社情報を含まず、架空の計画案として安全に共有できること。

## スコープ外

この対応では `mdViewer.html` のRuntime実装は変更しない。v0.13.6は実戦確認用fixtureの追加であり、機能追加ではなく検証用データの整備を目的とする。
