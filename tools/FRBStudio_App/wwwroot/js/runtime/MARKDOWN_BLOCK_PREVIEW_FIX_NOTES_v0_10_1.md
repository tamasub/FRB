# MARKDOWN_BLOCK_PREVIEW_FIX_NOTES_v0_10_1

## 目的

v0.10-markdown-preview-display-mode では、Markdownリンク/画像のインライン表示には対応したが、`# 見出し` や `- 箇条書き` などのブロックMarkdownがプレーンテキストのまま残っていた。

v0.10.1では、表示モードMarkdownプレビューを「読み物」として成立させるため、簡易Markdownブロックレンダリングを追加する。

## 対応内容

- `#`〜`######` 見出し表示
- `-` / `*` / `+` 箇条書き表示
- `1.` / `1)` 番号付きリスト表示
- `>` 引用表示
- ``` fenced code block 表示
- `inline code` / `**bold**` / `*em*` の簡易表示
- Markdownリンク / 画像表示は従来どおりViewDef許可時のみ

## 原則

- 保存値はMarkdown原文のまま保持する
- HTMLはData JSONへ混入させない
- ViewDefで `markdown.enabled` 等が指定された欄だけを対象にする
- 全textareaの自動Markdown化は行わない
