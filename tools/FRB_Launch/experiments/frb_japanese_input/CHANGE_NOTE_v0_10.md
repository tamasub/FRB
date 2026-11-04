# v0.10 4モード入力 + Windows IME自動切替

- 変更: `frb_japanese_input.py` — 4つのモード切替ボタン、モード別盤面、英字・記号・数字の直接入力、モード別の幅調整。
- 変更: `ime_bridge.py` — `IME_ON` (VK 0x16), `IME_OFF` (VK 0x1A) を Win32 SendInput トークンに追加。
- 新規: `keyboard_modes.py` — QWERTY・数字記号・テンキー定義とWin32 IME切替の小さな抽象化。
- 新規: `tests/test_keyboard_modes.py` — 10件のモード・配列・IME切替契約テスト。
- 変更: `README_JA.md` — Windows動作、フォルダーと使用方法を説明。

不変: `frb_kana_core.py` のかな・フリック定義、漢字変換ロジック、外部送信なし、フォルダー名固定。

テスト: 既存80 + 追加10 = 90 PASS（Pythonユニットテスト）。
Windows 11 + PySide6 の実画面と Microsoft IME のON/OFFは実機確認が必要。
