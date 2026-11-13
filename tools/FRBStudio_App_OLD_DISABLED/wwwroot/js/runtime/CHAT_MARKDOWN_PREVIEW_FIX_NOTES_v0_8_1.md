# CHAT_MARKDOWN_PREVIEW_FIX_NOTES_v0_8_1

## 目的

`v0.7-chat-input-mapping` 後に発生した、追加コメントのMarkdownプレビュー二重表示を修正する。

## 問題

`appendPosition=afterMessages` により `edit.input.userField` の保存済みコメントを会話末尾に表示した際、編集可能メッセージとして描画されていた。
そのため、Markdown画像/リンクを含むコメントでは以下のように二重表示になっていた。

- bubble本体: Markdown原文
- preview枠: Markdown変換後表示

## 方針

保存済みの末尾追加コメントは、入力欄や編集中UIではなく、会話タイムライン上の保存済みメッセージとして扱う。

- 保存値はMarkdown原文のまま保持する
- 表示時だけMarkdownリンク/画像に変換する
- 保存済みメッセージでは preview 枠を出さない
- `contenteditable=false` とし、F12反映時に表示HTMLを保存値へ逆流させない

## 変更

- `createChatMessageElement` に `renderMarkdownOnly` 表示モードを追加
- `appendPosition=afterMessages` の末尾追加コメントで `renderMarkdownOnly: true` を指定
- `chat-markdown-preview` は `options.showMarkdownPreview === true` の場合だけ表示

## 確認観点

- 追加コメント送信後、本文とMarkdown previewが二重表示されない
- `![alt](./images/chat/tamasub.png)` が画像として1回だけ表示される
- 保存値はMarkdown原文のまま残る
- F12反映/上書き保存/再読込でHTML化された文字列がJSONへ混入しない
