# v0.10 Markdown Preview Display Mode

## 目的

ViewDefでMarkdownを許可した textarea / chat / detailBodyカードについて、表示モードではMarkdownプレビューとして表示し、編集時はMarkdown原文を編集する。

## 方針

- 保存値はMarkdown原文のまま保持する。
- HTMLはData JSONへ混入させない。
- Markdown化の対象はViewDefの `markdown` 設定がある欄に限定する。
- 通常textarea・検索欄・ヘッダー欄は従来表示のままにする。
- chat欄は既存のMarkdown二重表示対策を維持しつつ、Markdown許可された通常メッセージにも表示モードを適用する。

## 操作

表示中のMarkdownプレビューをクリックすると、Markdown原文編集モードへ切り替わる。
Ctrl+Enter / Cmd+Enter で反映できる。
F12 / F7 / F8 は従来どおり詳細操作へ渡す。
