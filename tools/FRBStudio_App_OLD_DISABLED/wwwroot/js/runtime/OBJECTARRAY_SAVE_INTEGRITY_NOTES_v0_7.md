# OBJECTARRAY_SAVE_INTEGRITY_NOTES_v0_7

## 目的

v0.7-objectarray-save-integrity は、Studioくんの作業履歴・判断ログ・変更履歴を壊さないための保存健全性対応である。

対象は主に以下。

- objectArray / stringArray が表示用文字列で上書きされないこと
- detailFooter / chat 欄の編集・削除が F12 反映および上書き保存へ反映されること
- discussion_history / decision_log / change_history が Array のまま保存されること

## 変更点

### 1. objectArray / stringArray を通常Detail Formから除外

`detailVisibleFields()` で `objectArray` / `stringArray` を通常の入力欄表示から除外した。

理由:

- `2 items` のような表示専用文字列が入力欄として出る
- その値を反映すると配列本体を文字列で上書きする危険がある
- 配列は childArea のサブグリッド表示を正本にする

### 2. detailFooter / chat の編集値を保存対象に含める

`detailEditableControls()` の探索範囲を `detailForm` から `detailDialog` 全体へ拡張した。

理由:

- `layout.placement = detailFooter` の chat は `childArea` 側に描画される
- detailFormだけを見ると `latest_user_comment` の編集・削除を回収できない
- その結果、F12反映後に上書き保存しても保存されない、または削除文言が復活する

### 3. 配列フィールドの保存保護

`applyDetailInputsToRow()` で `objectArray` / `stringArray` は上書き対象から除外した。

理由:

- 表示用DOMから配列を直接復元しない
- 配列編集は将来の専用サブグリッド編集仕様で扱う

## 確認観点

- 追加コメント欄に入力 → F12 → 上書き保存 → 再読込して残ること
- 追加コメント欄の一部削除 → F12 → 上書き保存 → 再読込して復活しないこと
- `discussion_history` / `decision_log` / `change_history` が保存後もArrayであること
- objectArray欄に `2 items` のような文字列が保存されないこと
- 通常text / textarea / select / radio の保存が壊れていないこと

## スコープ外

- objectArray の高度な編集UI
- サブグリッド行追加・削除の強化
- chat本文のMarkdown画像表示
- chat input mappingの完全整理

これらは後続インシデントで扱う。
