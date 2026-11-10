# FRB Launch｜公開準備：System Page / Browser カテゴリー

## 変更目的

My Workの直下にあった「Files」と「ブックマーク」を、Studioで編集できる独立Page「⚙️ System」へ移動する。ブックマーク用のカテゴリーは「Browser」に改称する。

## 設定変更

- `config/frb_launch_sample_data_v0_1.json`
  - `pages`：`page_id=system`、`title=⚙️ System` のPageを追加（表示順50、既存Pageは変更しない）。
  - `items`：`item_id=folders`（Files）、子11件、`item_id=__browser_bookmarks_root`（Browser）の `page_id` を `work` から `system` へ移動。
  - ブックマークルートの `title` だけを `ブックマーク` → `Browser` に変更。
  - **Item ID・親ID・アクション・ホットキー・フォルダー参照先・有効状態・表示順は維持**。
- `config/expanded_view_options.json`：Files Exp/Listの起点Pageを `system` へ変更。
- `src/expanded_view_model.py`：設定ファイルが欠けた場合の起点Pageデフォルトも `system` に一致させる。
- `src/app.py`：起点Pageが仕事Pageだと誤解させるツールチップを、設定Pageを示す表現に訂正。

## 注意点

- Expanded起動時に内部選択されるPageは `System` になる（Files Exp/List表示は維持）。
- Compact起動時の既定Page（`work`）は変更しない。
- My WorkのZIP、Quick、日付、メール、選択肢データはそのまま。
- `__browser_bookmarks_root` と `launch_source=browser_bookmarks` は不変。Chrome/Edgeの自動取得は従来の方式を使う。
- 適用する設定ZIPには**個人設定が含まれる**。バックアップした上でLaunchを終了して適用する。公開配布する前に個人情報・ローカルパス等の除去が必要。
- Windows/PySide6実機の外観確認、Studio画面での再保存確認は別途必要。

## テスト

`pytest -q tests/test_system_page_browser_restructure_20261110.py tests/test_expanded_view_20261024.py tests/test_expanded_root_wheel_20261024.py tests/test_page_root_hotkeys_20261023.py tests/test_public_release_polish_20261109.py tests/test_browser_bookmarks.py`
