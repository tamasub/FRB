# MD Viewer v0.11.2 - Editor Layout / Click-to-Line

## 目的
Markdown Viewer / Editor のEditorモードにおいて、左側の目次・ドキュメントメタを維持したまま、右側の本文欄だけをViewerモードと同じ幅・位置で編集できるようにする。

## 対応内容

- Editorモードでも左側の目次・ドキュメントメタを表示したままにする。
- Editorモードの本文欄をViewerモードの文章欄と同じ右カラムに配置する。
- Editorモード中のMarkdownプレビューをクリックした場合、クリックしたMarkdownブロックに対応する原文行を推定し、textarea編集モードへ切り替えて該当行付近へカーソル移動する。
- Viewerモードでは本文クリックによるEditor切替を行わない。

## 方針

保存値はMarkdown原文のまま保持する。
HTMLはData/Markdown原文へ混入させない。
クリック行の対応は、見出し・段落・リスト・コードブロック・表などへ `data-md-line` を付与して行う。

## 注意

Markdown原文とHTMLプレビューは完全な1対1対応ではないため、クリック位置は文字単位ではなく、対象ブロックの先頭行付近へ移動する。
