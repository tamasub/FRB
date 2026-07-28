# Studio JSON Round Trip v0.18.35

## Purpose

詳細エディターの現在値を、AIと往復できるRow JSONとして扱う。

```text
Detail Editor
  -> Copy JSON
  -> AI
  -> Paste JSON
  -> 差分確認
  -> 反映(F12)
```

## Contract

- Copy JSONはViewDef上の詳細項目をJSON化する。
- objectArray / stringArray のサブグリッドを含む。
- 新規画面では未設定項目を `null`、配列を `[]` として出力する。
- Paste JSONは全項目JSONと部分JSONの両方を受け付ける。
- JSONに存在しない項目は現在の画面値を維持する。
- 読取専用項目はCopy対象だがPaste更新対象外。
- サブグリッド配列は、JSONにキーがある場合に配列全体を置換する。
- Paste直後は画面Draftだけを変更し、Data JSONへは保存しない。
- 既存の反映(F12)を人間の確定境界として維持する。
- Clipboard APIが使えない場合はStudio共通入力ダイアログへフォールバックする。
- MarkdownのJSONコードフェンスを受け付ける。

## Future boundary

API経由の追加・更新は本版の対象外。将来は、同じRow JSON契約をAPI Request Bodyへ接続できる構造を想定する。
