# CHAT_MARKDOWN_EDITABLE_FIX_NOTES_v0_9_1

## 目的

`appendPosition=afterMessages` で末尾表示される保存済み追加コメントについて、Markdown二重表示を避けつつ、本文修正も可能にする。

## 背景

v0.9 では Markdown preview の二重表示を防ぐため、末尾表示コメントを表示専用に寄せた。
その結果、画像/リンクは1回だけ表示されるようになったが、本文を修正できなくなった。

## 修正方針

- 通常表示では Markdown をHTML表示する
- Markdown preview 枠は出さない
- クリックすると Markdown 原文編集モードへ切り替える
- 編集中は `contenteditable=true` にし、F12反映でMarkdown原文を保存する
- Ctrl/Cmd + クリック時はリンク遷移を優先できるようにする

## 確認観点

1. 末尾コメントの画像/リンクが1回だけ表示される
2. 末尾コメントをクリックするとMarkdown原文を修正できる
3. F12反映後、上書き保存・再読込して修正が残る
4. 保存値にHTMLが混入しない
