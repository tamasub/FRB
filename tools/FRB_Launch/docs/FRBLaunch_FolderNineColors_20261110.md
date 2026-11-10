# FRB Launch: フォルダー9色対応（2026-11-10）

## 対応範囲

- Studioの `launch.icon_key` 選択肢と、Launchの `folder_icon_color()` を同じ値で接続。
- 新しい保存値: `folder.blue`, `folder.green`, `folder.red`, `folder.purple`, `folder.orange`, `folder.cyan`, `folder.pink`, `folder.gray`。
- 既存値: `folder.yellow`, `category.blue`, `folder`, `category` を維持。
- Files ExpのJSON仮想フォルダー／登録ルート、Files List／Launch内の通常の設定項目は同じ `row_icon()` 経由で表示。
- ローカルの通常の実フォルダーは従来色。ページ名の絵文字、ZIP等の非フォルダーアイコンは変更しない。
- **個人設定JSONは変更しない**。各項目の `icon_key` をStudioで選び直した場合のみ色が変わる。

## 色と保存キー

| 色 | キー | 色コード |
|---|---|---|
| 黄 | `folder.yellow` | #e9bb61 |
| 青 | `folder.blue` | #599de5 |
| 緑 | `folder.green` | #57ad82 |
| 赤 | `folder.red` | #e47575 |
| 紫 | `folder.purple` | #a388df |
| 橙 | `folder.orange` | #e99a5f |
| 水 | `folder.cyan` | #57baca |
| 桃 | `folder.pink` | #e78cbe |
| 灰 | `folder.gray` | #9aa3ad |

旧 `category.blue` は歴史的な色 #6ba7ff のまま。ユーザー設定由来でない物理フォルダーには色設定を継承しない。

## 適用手順

1. LaunchとStudioを終了する。
2. 両アプリの作業フォルダー・設定ファイルをバックアップする。
3. `FRBLaunch_FolderNineColors_20261110_DIFF.zip` をLaunchルートへ上書き。
4. `FRBStudio_FolderNineColors_20261110_DIFF.zip` をStudioルートへ上書き。
5. Studioを再起動し、アイテムの「アイコン（絵柄で選択）」で新しいフォルダー色を選ぶ。
6. 保存してLaunchを再読み込みし、Files ExpやFiles Listの色を確認する。

## テストと留意点

`pytest -q tests/test_folder_nine_color_palette_20261110.py tests/test_studio_icon_exact_preview_20261110.py`

色の描画ロジックは純Python検査。Windows実機の画面表示は要確認。
Studioでは**ドロップダウンの色見本絵文字**を使う。9枚タイル画像を並べる専用ピッカーUIは今回の改修範囲外。
