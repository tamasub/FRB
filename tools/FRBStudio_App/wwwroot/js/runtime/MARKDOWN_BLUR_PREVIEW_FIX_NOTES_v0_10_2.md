# v0.10.2 Markdown blur preview refresh

## 目的

v0.10 / v0.10.1 で、Markdown許可済みの本文・チャット・detailBodyカードは表示モードでMarkdownプレビュー、クリック後はMarkdown原文編集に切り替わるようになった。

ただし、編集後にプレビュー状態へ戻すには、前へ/次へで別行へ移動して再描画する必要があった。

v0.10.2 では、Markdown原文編集欄からフォーカスが外れたタイミングで、自動的にMarkdownプレビューへ戻す。

## 方針

- 表示モード: Markdownプレビュー
- クリック: Markdown原文編集
- blur: Markdown原文を行データへ反映し、同じ場所でプレビューへ戻す
- 保存値: Markdown原文のまま保持
- HTML: Data JSONへ混入させない

## 対象

- Markdown許可済み textarea
- Markdown許可済み chat message
- detailBodyカード内のMarkdown本文
- 追加コメント末尾表示のMarkdown本文

## 注意

blur時に行データへ反映するため、上書き保存ボタンを押す前にプレビューへ戻っても、保存対象はMarkdown原文のまま保持される。
