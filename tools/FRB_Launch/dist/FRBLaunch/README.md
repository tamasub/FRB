FRB Launch diff 2026-10-25

変更内容
1. 展開ビュー3列のカレント表示を改善
   - フォーカス列: 薄緑塗りつぶし
   - 非フォーカス列: カレント行を薄緑枠線のみで表示
2. 右上のビュー切替ボタンをサンプル風アイコンに変更
   - 従来ビュー: compact風アイコン
   - 3階層ビュー: three-layer風アイコン
3. Files見出し横の3本線アイコン位置を微調整
   - 少し右、少し下へ移動

変更ファイル
- src/app.py
- src/expanded_view.py

確認
- python -m py_compile src/app.py src/expanded_view.py
