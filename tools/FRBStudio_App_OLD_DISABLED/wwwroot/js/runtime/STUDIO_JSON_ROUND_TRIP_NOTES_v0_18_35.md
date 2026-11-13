# Studio JSON Round Trip v0.18.35.3

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

- Copy JSONは、詳細画面で入力・確認できる保存対象項目をJSON化する。
- 通常の詳細入力欄だけでなく、次の画面入力経路を対象にする。
  - `objectArray` / `stringArray` の共通サブグリッド
  - `edit.visible=false` でもDetail下部へ表示される編集可能サブグリッド
  - 対象文脈の専用Grid
  - Chat message / embedded field
  - Chat composerの `userField`
- `decision_log` / `discussion_history` / `change_history` のような表示位置がDetail下部の配列も、画面で編集可能ならPaste対象にする。
- 画面入力経路を持たない `edit.visible=false` の通常項目は同期対象外とする。
- 新規画面では未設定項目を `null`、配列を `[]` として出力する。
- Paste JSONは全項目JSONと部分JSONの両方を受け付ける。
- JSONに存在しない項目は現在の画面値を維持する。
- 読取専用項目はCopy対象だがPaste更新対象外。
- サブグリッド配列は、JSONにキーがある場合に配列全体を置換する。
- Paste直後は画面上の作業行だけを変更し、Data JSONへは保存しない。
- Paste後に人間が画面修正した最新値を、反映(F12)時に再回収する。
- 既存の反映(F12)を人間の確定境界として維持する。
- Clipboard APIが使えない場合はStudio共通入力ダイアログへフォールバックする。
- MarkdownのJSONコードフェンスを受け付ける。

## Boundary

Round Tripは「ViewDefに存在する全Data項目の無条件Import」ではない。
今回の同期対象は、少なくとも詳細画面上に入力経路が存在する項目とする。
画面非表示かつ他UIにも接続されていない内部項目は、誤更新防止のため無視する。

## Future boundary

API経由の追加・更新は本版の対象外。将来は、同じRow JSON契約をAPI Request Bodyへ接続できる構造を想定する。
