# FRBかな v0.7 / 2026-11-04

- 「IME」ONの送信先を外部アプリから **FRBかな自身のQLineEdit** へ変更。
- Windowsでは手元IMEモードをデフォルトONで起動（失敗時はローカルかなへフォールバック）。
- `QLineEdit` にフォーカスを保持し、Windows IMEによる未確定入力／候補表示ができるようにした。
- IME候補確定による文字列変化を一部検出し、かなの連続タップ状態をリセット。
- QtのIME合成中に `setText()` を行わない設計。
- FRB Launch本体と独立した固定フォルダー `experiments/frb_japanese_input` は維持。
- 変換エンジン・候補一覧は自作しない。外部アプリへの文字送信はスコープ外。
- Windows GUIでの実IME候補確認は未実施。手元IME実験版として配布。
