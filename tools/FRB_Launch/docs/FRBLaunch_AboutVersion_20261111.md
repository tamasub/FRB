# FRB Launch / バージョン情報（2026-11-11）

## 変更
- 設定メニューの最下部に区切り線と「バージョン情報...」を追加。
- 内容は `FRB Launch` / `Version 0.9.0` / `FRB Project` のみ。
- 「バージョンをコピー」「閉じる」の2ボタンを既存 `RemoteConfirmation` で操作（ぐりぐり対応）。
- ダイアログのアイコンは情報アイコンとし、通常の確認ダイアログを変更しない。
- `src/app_version.py` をアプリ本体バージョンの唯一の定義場所とする。

## 対象
- `src/app.py`
- `src/remote_confirmation.py`
- `src/app_version.py`（追加）
- `tests/test_version_about_menu_20261111.py`（追加）

## 制約
- 設定JSONにバージョンを保存しない。ユーザー登録データ・Studio Change Coreを変更しない。
- 説明文「Keyboard-first」などの未合意テキストは追加しない。

## 確認
- Python構文チェックと静的/モックテスト。
- Windows/PySide6実画面の表示・リモコンホイール操作は未受入。

## 次作業
- Windows実機で設定→バージョン情報を開き、閉じる／コピーのホイール切替と中央決定、Esc・マウス操作を確認する。
