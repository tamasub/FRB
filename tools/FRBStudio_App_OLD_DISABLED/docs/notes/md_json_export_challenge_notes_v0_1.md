# MD JSON化・ViewDef同名調整メモ v0.1

## 目的

`TEST_PLAN_RESPONSIBILITY_SCOPE_v0_18_5.md` を、Studioくんでレビュー・編集・Markdown再出力できるようにする。

## 今回の方針

- MD本文を章単位で `rules[]` に構造化した。
- 既存の `rule_review_common_view_def_v0_3.json` はファイル名を変更せず、中身だけを調整した。
- 原文に近いMarkdown出力を狙うため、Data JSON root に `markdown_export_body` として元MD全文を保持した。
- 章単位レビュー用に `rules[].body` / `rules[].original_markdown_block` も保持した。

## 現行APPでできそうなこと

- `rules[]` を一覧・詳細でレビューする。
- `body` を編集して章単位の内容を育てる。
- `ExportMarkdown` で `markdown_export_body` を出力対象にする。

## 現行APPで怪しいこと

`generic_sections` が、セクション見出しやfield captionを必ず付ける実装の場合、元MDと完全一致するMarkdown再出力は難しい。

## APP改善候補

次のどちらかがあると、MD原文再出力がかなり強くなる。

1. `markdown.sections[].format = "raw"` を追加し、指定fieldの文字列を見出し・captionなしでそのまま出力する。
2. `markdown.rawField = "markdown_export_body"` のようなトップレベル指定を追加し、ExportMarkdown時にそのfieldをそのまま保存する。

## 判断

今回のViewDefだけで「かなり近い」出力は狙える。
ただし、完全なMD原文再現を標準機能にするなら、APP側に raw Markdown export mode を足す方向がよい。
