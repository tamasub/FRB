# FRB かな v0.10.1 — 起動時 NameError 修正

対象: v0.10 の `experiments/frb_japanese_input/` へ上書き

## 修正

1. `frb_japanese_input.py` の `style_for_size()` 内で追加した CSS (`literalKey` / `modeButton`) の波括弧を f-string 用に `{{` / `}}` へ修正。
   - v0.10 起動時の `NameError: name 'color' is not defined` を防止。
2. モード切替ボタンの `clicked(bool)` を受け取っても、`mode` のキャプチャ値が上書きされないようラムダ引数を修正。
3. GUIを使わず `style_for_size()` を実行できる回帰テストと、モード切替コールバックの回帰テストを追加。

## 検証
- Python compileall: PASS
- unittest discover: 92 tests PASS
- Windows / PySide6 実GUI: 未検証（実行環境にPySide6なし）

## 適用
- 差分ZIPをFRB Launchルートに上書き展開。
- `experiments\frb_japanese_input\run_windows.bat` を実行。
- v0.10一式ZIPは、新規環境への配置用（同じ修正済みコード）。
