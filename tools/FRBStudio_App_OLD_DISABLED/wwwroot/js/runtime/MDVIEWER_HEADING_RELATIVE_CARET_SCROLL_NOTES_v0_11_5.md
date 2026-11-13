# MDViewer Heading Relative Caret Scroll Notes v0.11.5

目的: Markdown Viewer / Editor のEditorモードで、長文後半ほどクリック位置・復帰位置がズレる問題を抑える。

対応内容:

- EditorプレビューのMarkdownブロックに、原文行番号だけでなく直前見出しからの相対位置を保持する。
- プレビュークリック時は、全文先頭からの行番号だけでなく、直前見出し + 相対行数を使ってtextarea側のカーソル位置を推定する。
- textareaからblurでプレビューへ戻る時も、カーソル行の直前見出し + 相対行数を保存し、再レンダリング後に近いブロックへ復帰する。
- textarea側のスクロールは、単純な lineHeight 計算ではなく、同じフォント・幅・padding のhidden mirrorを使ってカーソルY座標を測定し、表示中央より少し上に寄せる。
- preview側のスクロールも、対象ブロックを画面中央より少し上へ寄せる。

制約:

- MarkdownプレビューHTMLとtextarea原文は完全な1対1対応ではないため、文字単位の完全一致は狙わない。
- クリックした見出し・段落・箇条書き・コードブロック・表・引用の「近く」へ戻すことを優先する。
- wwwroot/data と wwwroot/defs はGitHub専用公開エリアのため、この対応では更新しない。
