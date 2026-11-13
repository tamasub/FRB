# FRB Launch — 今日の日時ショートカット追加（2026-11-10）

## 追加
`config/frb_launch_sample_data_v0_1.json` の「My Work → 日付・定型文」に以下を追加。

- タイトル: `今日の日時 yyyyMMdd_hhmmss`
- Item ID: `today_datetime`
- 動作: `ClipboardCopy`（既存の今日・昨日の日付と同じ）
- テキスト定義: `%now:yyyyMMdd_HHmmss%`（24時間形式）
- 例: 2026-11-10 07:23:03 → `20261110_072303`
- 並び順: `今日の日付` の直後

既存の `Expander.format_date` で対応済みの `HH`（24時間表記）を使うため、プログラム本体への変更は不要。

## テスト
`PYTHONPATH=src python -m unittest discover -s tests -p 'test_release_datetime_clipboard_20261110.py' -v` — 2 PASS。
`PYTHONPATH=src python -m unittest discover -s tests -p 'test_core.py' -v` — 14 PASS。

Windows上の実際のクリップボード操作は未確認。

## 備考
この設定JSONにはユーザー個人用の項目が含まれ得る。外部公開版の配布前に、個人情報や端末固有のパス／登録値を点検すること。
