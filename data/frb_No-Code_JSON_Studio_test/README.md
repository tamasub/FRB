# No-Code JSON Studio v0.3-draft

1画面1グリッドのJSON Viewer / Light Editorプロトタイプです。

## 使い方

1. `index.html` をブラウザで開く
2. `画面定義JSON` に `defs/fft_log_view_def_v0_2.json` を読み込む
3. `対象JSON` に FFTログJSONを読み込む
4. Header / Search / Grid / Detail Dialog を確認
5. 編集後は `別名保存` ボタンでJSONを保存

## URL起動

ローカルサーバで開く場合、URLパラメータから自動読み込みできます。

```txt
index.html?view=defs/fft_log_view_def_v0_2.json&data=defs/fft_log_sample.json
```

※ `file://` で直接開いた場合、ブラウザ制約でURL自動読み込みできないことがあります。その場合はファイル選択/Dropで読み込んでください。

## v0.3-draft 追加内容

- グリッド列ヘッダークリックによるソート
  - 1回目: 昇順
  - 2回目: 降順
  - 3回目: ソート解除
- 件数表示の左側にカレント行表示
- 行右クリックメニュー
  - この行をコピー
  - コピー行から新規追加
- 詳細ダイアログでコピー行の貼り付けサポート

## v0.2-draft 追加内容

- グリッド行の新規登録
- グリッド行の物理削除（確認ダイアログあり）
- 列定義の `defaultValue` による行追加時の初期値設定
- 数値列の表示専用フォーマット `format` / `grid.format`
- 数値入力パラメータ `edit.step` / `edit.min` / `edit.max`
- URLパラメータ `view` / `data` による自動読み込み

## 設計メモ

- `format` は表示専用です。保存JSONの数値は丸めません。
- 未定義JSON項目は読み込んだまま保持し、別名保存時にも削除しません。
- 元JSONは上書きしません。
- 日付カレンダー対応は今回対象外です。

## 注意

これはプロトタイプです。巨大JSONでは表示が重くなる可能性があります。
