# SUBGRID_PREVIEW_EDIT_ACTION_COLUMN_POLISH_REPORT_v0_18_12

## 概要

v0.18.12 の再依頼として、前回対応で残っていた以下の問題を修正した。

- 文書Markdown出力が、タイトルだけで本文が出ない。
- 読取専用サブグリッドの左端に、操作しないのに空の操作列が残る。
- 読取専用サブグリッドの操作列を 34px に圧縮する判断は、UI意図と合わない。

## 修正内容

### 1. 文書Markdown出力のViewDef sections fallback

`document_rebuild` モードで `source` 未指定の場合、従来は暗黙に `$.rules` を見に行っていた。
責務ExpectedテストパターンDataには `$.rules` が無いため、結果としてタイトルだけのMarkdownになっていた。

修正後は、`source` 未指定の文書Markdownでは ViewDef の `sections` を読み直し、form / grid / objectArray サブグリッドを文書化する。

これにより、責務Expectedテストパターンでは以下がMarkdownへ出る。

- 基本情報
- テストパターン行
- Input: ViewDef Fields などのサブグリッド
- Input: Rows / Criteria / Base Fields / All Fields
- Expected 系の配列・値

### 2. 読取専用サブグリッドの操作列を非表示化

前回の「読取専用サブグリッドでは操作列を空見出し＋34px固定にする」判断は撤回した。

読取専用サブグリッドでは操作を行わないため、操作列そのものを生成しない。
旧DOMが残った場合の保険としてCSS側でも非表示にする。

### 3. 読取専用Previewを表示専用へ寄せる

読取専用サブグリッドでは、ボタン表記を `プレビュー` にし、Preview画面内の追加・移動・削除・一覧反映などの操作UIを出さない。
編集可能サブグリッドでは従来どおり `プレビュー編集` として動作する。

## 対象ファイル

- `wwwroot/js/markdown/data_markdown.js`
- `wwwroot/js/runtime/detail_subgrid_edit.js`
- `wwwroot/styles.css`
- `data/json/00_rules/md/SUBGRID_PREVIEW_EDIT_ACTION_COLUMN_POLISH_REPORT_v0_18_12.md`
- `data/json/01_main/studio_work_incident_data_v0_127_subgrid_preview_edit_action_column_polish_done.json`

## 確認

- `node --check wwwroot/js/markdown/data_markdown.js`
- `node --check wwwroot/js/runtime/detail_subgrid_edit.js`
- 文書Markdown生成の簡易VM確認で、タイトルだけではなく、基本情報・テストパターン・サブグリッド表が出力されることを確認。
