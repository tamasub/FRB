# FRB Launch: Studioアイコン表示一致修正（2026-11-10）

## 発生現象

Studioの「アイコン（絵柄で選択）」で `🗜️ ZIP` を選択して保存すると、
LaunchのFiles Expでは緑の `Z` が表示された。

## 原因

設定JSON `icon_key` は正しく `archive` だった。Launchの既存描画関数
`src/app.py:icon()` が `archive` を緑の `Z`、`mail` を `@`、
`wifi` を `W`、`calendar` を `D` として独自変換していた。
Studioの選択肢に表示する絵文字と、実際のLaunchの描画内容が違っていた。

## 対応

- 新設 `src/launch_icon_palette.py` にStudio選択肢と同じ絵文字を定義。
- `src/app.py:icon()` を更新し、該当する `icon_key` は同じ絵文字を描画。
- `category.blue` と `folder.yellow` は、従来どおり青・黄色のフォルダーを描画。
- Files ExpのJSON登録フォルダーと仮想カテゴリーは、既存の `row_icon` 経由で反映。
- 設定JSON、Page/Item ID、Studioデータ・UI、既存のファイル操作機能は変更しない。

## 確認

`python -m pytest tests/test_studio_icon_exact_preview_20261110.py -q`

- ソース単体テスト：Studioで表示するアイコン候補の各絵文字への一致を検証。
- Windows実機で確認すること：Studioで `🗜️ ZIP` を指定して保存 → Launch再読込 →
  Files Expの「FRB Launch Logフォルダー」表示が `🗜️` になる。
- カラー絵文字はWindows 11のSegoe UI EmojiとQt描画に依存。実機での色調・サイズ差は未確認。

## 注意

差分ZIPはコードとテスト・資料のみであり、個人の設定JSONは上書きしない。
FULL ZIPは個人設定を含むので一般公開前に必ず整理する。
