# MARKDOWN_COMMENT_SIDECAR_JSON_NOTES_v0_13_3

## 目的

Markdown本文を汚さず、SentenceBlock / TableCell に対するコメントを sidecar JSON として保持する。

## 対応内容

- `article.md` に対して `article.md.comments.json` を sidecar 名として扱う
- コメント本文は Markdown 本文へ挿入しない
- 右クリックメニューのコメント操作を sidecar コメント追加へ変更
- TableCell 上で右クリックした場合は `target_type: table_cell` として記録
- SentenceBlock 上で右クリックした場合は `target_type: block` として記録
- コメント追加後、Preview 上に小さなバッジを表示
- Sidecar JSON は `/api/markdown/{sidecarName}` へ保存を試みる
- API保存に失敗した場合は localStorage にフォールバックする
- メニューから Sidecar JSON の保存 / コピーが可能

## sidecar JSON 形式

```json
{
  "schema_version": "md_comment_sidecar_v0_1",
  "document_type": "markdown_comment_sidecar",
  "target_file": "article.md",
  "sidecar_name": "article.md.comments.json",
  "updated_at": "2026-06-24T00:00:00.000Z",
  "comments": []
}
```

## コメント対象

### SentenceBlock

- `target_type: block`
- `block_id`
- `block_type`
- `line`
- `start_line`
- `end_line`
- `target_excerpt`

### TableCell

- `target_type: table_cell`
- `table_id`
- `cell_id`
- `row_index`
- `column_index`
- `line`
- `target_excerpt`

## 注意

現時点ではコメント解決、一覧表示、フィルタ、コメント編集は未実装。
それらは `v0.13.4-md-comment-review-ui` の範囲とする。

