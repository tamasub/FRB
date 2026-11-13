# FRB Launch Files Exp — System非表示・Browserのブックマーク昇格

## 起点

- ユーザー最新ソース：`launch_app_20261110_102500.zip`（10:22版ではなく10:25版）
- 対象：Files Exp / Files List の表示投影のみ

## 変更

- Studio／設定JSONでは `System` Page と `Browser` アイテムをそのまま維持する。
- Files Exp では `System` Pageを表示しない。
- `Browser`（`item_id=__browser_bookmarks_root`）を最上位の `🔖 ブックマーク` として表示（Pageと同じ、余分なフォルダーアイコンなし）。
- Bookmark配下の枝・URL、選択・右クリック・Studioプロパティを従来の `page_id/item_id/node_id` で扱う。
- Files Listでブックマーク内へ遷移した場合も、パンくず／Exp再選択から `System › Browser` を除去する。
- 既存の `Files` 仮想アンカー非表示と、登録済み実フォルダーの別表示は維持する。
- My Work / Windows / FRB実験 / お気に入り等のPage表示は変えない。

## 変更ファイル

- `src/launch_virtual_tree.py`：表示用投影とroot一覧
- `src/remote_files_explorer.py`：Expの投影root読み込み
- `src/expanded_view.py`：List/Exp選択・パンくずの表示用投影
- `tests/test_system_bookmark_exp_presentation_20261110.py`：新規回帰テスト
- `tests/test_virtual_launch_exp_git_remote_20261103.py`：表示root API名の変更に合わせて既存静的テストを更新

## 設定／互換性

- `config/frb_launch_sample_data_v0_1.json`：変更なし
- `config/expanded_view_options.json`：変更なし
- Studioからの編集対象やbookmark自動取込・ホットキー：変更なし
- Windows / PySide6 の実機GUI操作は未確認。実機での最終確認が必要。
