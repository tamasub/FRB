# FRB かな v0.5 変更メモ (2026-11-04)

- フォルダー固定: experiments/frb_japanese_input/
- 暗黙確定のタイマー/900msルールを削除
- 未確定文字列と確定済み文字列の境界 (committed_length) を導入
- 濁点・半濁点・小文字変更も未確定を維持
- 記号キー中央連打を `、 → 。 → ？ → ！ → …` に変更（置換・非追記）
- Enterボタンと物理Enterキーで明示確定
- コピーでは未確定を確定させない
- 現状の未確定表示は簡易なローカル表示でWindows IME連携ではない
- Python単体テスト52件 PASS。WindowsのGUI実機未検証
