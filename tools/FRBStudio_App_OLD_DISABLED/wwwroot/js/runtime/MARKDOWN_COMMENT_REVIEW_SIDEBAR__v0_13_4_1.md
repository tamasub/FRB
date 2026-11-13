# MARKDOWN_COMMENT_REVIEW_SIDEBAR_COMPACT_LAYOUT_NOTES_v0_13_4_1

## Purpose

`v0.13.4-md-comment-review-ui` で左サイドバーにコメントレビュー一覧を追加した結果、100%表示時に左バー全体が縦方向へ収まりにくくなった。

本対応では、コメントレビューUIを右バーへ逃がす前に、左バー内で以下の3領域を縦方向に圧縮・分割し、各領域内スクロールで操作できるようにする。

- 目次
- ドキュメントメタ
- コメントレビュー

## Policy

右バー化は保留。

まずは現在の「左＝ナビ・メタ・レビュー / 中央＝本文」の構造を維持する。

```text
left sidebar
  toc panel             internal scroll
  document meta         compact display
  comment review panel  internal scroll

main content
  markdown preview/editor
```

## Changes

- `.sidebar` を画面高に収める固定グリッドへ変更
- 目次パネルに `md-toc-panel` を追加
- ドキュメントメタパネルに `md-meta-panel` を追加
- コメントレビュー一覧を `minmax(0, 1fr)` の内部スクロールに変更
- コメントカードの本文表示を2行程度へ圧縮
- 低めの画面高向けに `max-height: 820px` の追加圧縮ルールを追加
- 狭幅画面では従来どおり縦積み・通常スクロールへ戻す

## Scope

Changed:

- `wwwroot/mdViewer.html`
- `wwwroot/js/runtime/MARKDOWN_COMMENT_REVIEW_SIDEBAR_COMPACT_LAYOUT_NOTES_v0_13_4_1.md`

Not changed:

- `wwwroot/data/**`
- `wwwroot/defs/**`
- Sidecar comment JSON format
- Comment review runtime logic

## Verification points

1. Browser zoom 100% で左バーが画面内に収まること
2. 目次が左バー内でスクロールできること
3. コメントレビュー一覧が左バー内でスクロールできること
4. ドキュメントメタが過度に高さを取らないこと
5. コメントのジャンプ・解決・編集・削除操作が従来どおり動くこと

