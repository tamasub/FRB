# JSON Master Editor v0.1-draft

1画面1グリッドのJSON Viewer / Light Editorプロトタイプです。

## 使い方

1. `index.html` をブラウザで開く
2. `画面定義JSON` に `defs/fft_log_view_def_v0_1.json` を読み込む
3. `対象JSON` に FFTログJSONを読み込む
4. Header / Search / Grid / Detail Dialog を確認
5. 編集後は `別名保存` ボタンでJSONを保存

## v0.1 方針

- 1画面1メイングリッド
- Array = Table
- Object = Form
- Child Object = Flatten
- 定義されていない項目は表示しない
- 定義されていない項目は保存時も保持する
- 元JSONは上書きしない

## 注意

これはプロトタイプです。巨大JSONでは表示が重くなる可能性があります。


## v0.1 elegant update

- 黒ヘッダ内に定義JSON/対象JSONのDropエリアを配置
- ファイル選択とDropの両対応
- ボタン・グリッド・カード配色をエレガント寄せに調整
- 未定義JSON項目は読み込んだまま保持し、別名保存時にも削除しない
