# CHAT_INPUT_MAPPING_NOTES_v0_7

## 目的

chat型の送信欄を、Runtime固定フィールド名ではなくViewDef宣言で制御する。

対象:

- `edit.input.userField`
- `edit.input.aiField`
- `edit.input.appendPosition`
- `edit.input.markdown`

## 変更点

### 1. 送信欄の保存先明示

送信欄の入力は `edit.input.userField` に保存する。
AI側の回答受け皿は `edit.input.aiField` として初期化・保持する。

```json
{
  "edit": {
    "input": {
      "enabled": true,
      "userField": "latest_user_comment",
      "aiField": "latest_ai_response"
    }
  }
}
```

### 2. 送信メッセージの末尾表示

`appendPosition: "afterMessages"` の場合、`userField` と同じフィールドが `messages` に定義されていても、通常のmessages表示からは除外し、会話の末尾に表示する。

これにより、送信したコメントが最後のAI回答の直前に割り込む時系列崩れを防ぐ。

```json
{
  "edit": {
    "input": {
      "userField": "latest_user_comment",
      "appendPosition": "afterMessages"
    }
  }
}
```

### 3. chat本文のMarkdownリンク/画像表示

`edit.input.markdown` または `message.markdown` で許可されたchat本文だけ、Markdownリンク/画像を表示変換する。

保存値はMarkdown原文のまま保持する。

```markdown
[関連資料](./docs/sample.md)
![エラー画面](./png/error_001.png)
```

許可例:

```json
{
  "markdown": {
    "enabled": true,
    "allowLinks": true,
    "allowImages": true
  }
}
```

## 実装上の注意

- 編集可能なchat本文は、保存値を壊さないため本文はMarkdown原文のまま表示する。
- 編集可能なchat本文では、Markdownプレビューを本文下に表示する。
- readonlyなchat本文は、本文そのものをMarkdown表示に変換する。
- `javascript:` / `vbscript:` / `data:` URLは表示変換しない。

## 確認観点

- 送信欄の入力が `edit.input.userField` へ保存される。
- 送信後の追加コメントが最後のAI回答の後ろに表示される。
- `input.userField` と同じfieldがmessagesに存在しても二重表示されない。
- Markdownリンク/画像がViewDef許可時だけ表示される。
- 保存値はMarkdown原文のまま残る。
