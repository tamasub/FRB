# frb_studio_mdviewer_font_003

Markdown Viewer の本文表示フォントを調整した版です。

## 変更点

- Markdown本文全体を少しだけ小さめに調整
  - `.markdown-body`: 16px → 15px
  - `p / li`: 14.5px
- Markdownの `####` / `#####` / `######` に明示スタイルを追加
  - h4: 16.5px
  - h5: 15px
  - h6: 14px
- テーブル内文字を少し抑制
  - th / td: 13.5px
- 印刷用CSSにも h4 / h5 / h6 を追加

## 狙い

制約JSONからMarkdown出力したときに、

- レビュー対象
- 集約サマリ
- 対象範囲
- 含まれる個別制約

などの小見出しが本文より小さく見えないようにする。

