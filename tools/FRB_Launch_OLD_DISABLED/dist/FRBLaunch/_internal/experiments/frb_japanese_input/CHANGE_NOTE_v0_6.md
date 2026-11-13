# v0.6 差分

- 実験モード「IME送信」を上部に追加（既定OFF）
- Win32 `SendInput`、非アクティブ操作窓 `WS_EX_NOACTIVATE` を使う補助層 `ime_bridge.py` を追加
- 未確定かなの差し替え → Backspace + ローマ字キー入力 / 確定↵ → Enter
- 送信先ウィンドウ固定 / 他ウィンドウへの誤送信抑止 / 未対応文字の送信拒否
- 既存の小型UI・10pxフリック・特殊キー・ローカル未確定操作を維持
- Git管理用フォルダー `experiments/frb_japanese_input/` 固定
- 自動テスト: 65件PASS。実機IME候補表示・変換確定は未確認。
