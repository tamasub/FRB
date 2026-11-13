# BLOCK_MODEL_NOTES_v0_13

## 目的

`v0.13-md-block-model-foundation` では、Markdown本文を単なる1本の文字列ではなく、AI協働で扱える `Block` / `SentenceBlock` の土台として分解する。

今回の目的は、表セル編集やコメント永続化まで一気に作り込むことではない。まず、プレビュー上の要素とMarkdown原文上の位置を、`block_id` / `type` / `source_range` で対応付ける。

## 追加した基盤

- `parseMarkdownBlocks(rawMd)`
  - Markdown原文をBlock配列へ分解する。
  - MVP対象は front_matter / heading / paragraph / list_item / table / code_block / blockquote / horizontal_rule。
- `markdownBlockModelRuntime`
  - 現在のBlock配列、block_id Map、currentBlockId、sourceHashを保持する。
- Preview DOMへの属性付与
  - `data-md-block-id`
  - `data-md-block-type`
  - `data-md-table-id`
  - `data-md-line`
  - `data-md-end-line`
- Block Modelメタ表示
  - サイドバーにBlock数、current block、type別件数を表示する。
- 右クリックメニュー
  - `Block情報` を追加し、選択中Blockのid/type/line/table情報を確認できるようにした。

## Table Blockの扱い

表は `table` Blockとして扱い、内部に `rows` と `cells` を持たせる。

```json
{
  "block_id": "mdblk_0004_table_12",
  "type": "table",
  "table_id": "tbl_0001_12",
  "source_range": { "start_line": 12, "end_line": 16 },
  "rows": [
    {
      "row_index": 0,
      "line": 12,
      "cells": [
        { "cell_id": "mdblk_0004_table_12_r0_c0", "column_index": 0, "text": "項目" }
      ]
    }
  ]
}
```

今回の段階では、セル編集UIやセルコメント永続化は行わない。後続の `v0.13.2-md-table-cell-editor` と `v0.13.3-md-comment-sidecar-json` で扱う。

## MVP制約

- 完全なMarkdown AST互換は目指さない。
- コードブロック内部は分解しない。
- Markdown表は、ヘッダー行 + セパレーター行を持つ標準的なGFM表を対象にする。
- 保存値はMarkdown原文のまま保持し、HTMLやBlock JSONをMarkdown本文へ混入しない。
- `block_id` は編集セッション内の内部識別子であり、永続IDではない。

## 次の作業候補

- `v0.13.1-md-sentence-insert-delete`
  - 現在Blockの直後にSentenceBlockを追加する。
  - 現在Blockを削除し、Markdownを再生成する。
- `v0.13.2-md-table-cell-editor`
  - Table Blockのセル単位編集UIを追加する。
- `v0.13.3-md-comment-sidecar-json`
  - Block / TableCellに対するコメントをsidecar JSONへ保存する。

## 確認観点

- 見出し、段落、箇条書き、表、コードブロック、引用がBlock化されること。
- コードブロック内部の `|` や `#` を表・見出しとして誤分解しないこと。
- EditorモードのPreview上でBlockに点線枠が出ること。
- Blockをクリックまたは右クリックした時にcurrent blockとして管理されること。
- 右クリックメニューからBlock情報を確認できること。
