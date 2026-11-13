# studio_work_0269 — Files List / Page直下の実ファイルDrop修正

## 変更

- `src/expanded_view.py` / `_middle_launch_drop_target`: 設定JSONのPageをFiles Listで表示している場合、余白へのファイル・フォルダー・HTTP(S) URLのCopy Dropを許可する。従来の「Page直下ではフォルダーのみ」制限を撤廃。
- `src/app.py` / `handle_launch_drop`: 同じPage直下のAdd処理側の種類制限を撤廃。既存の `eligible_parent` による登録先チェックは維持する。
- `tests/test_launch_0269_page_root_file_drop_20261111.py`: 新規回帰テスト。Page直下、カテゴリー配下、複数ファイル、Files Expルートの区別、実ファイルシステム由来ノードの拒否を確認する。

## 理由

設定JSON Page（例：testwk）直下のFiles List余白で、ExplorerからのファイルDropが、UIのDragMove段階と登録ハンドラーの2層で拒否されていた。配下のカテゴリーフォルダーへのDropは通るため、MIMEやファイル名の問題ではなく登録先制約が原因。

## 対象外・不変

- **Files Exp列のルート余白**は従来どおり「既存フォルダーだけ登録可」。Page直下とは別の場所。
- 登録先が実ファイルシステム由来のフォルダーやファイルの場合は、Studio JSONへの登録操作の対象にしない。
- 設定JSONのMoveは専用MIMEで処理し、ExplorerからのCopy Dropと混同しない。
- 物理ファイル・フォルダーを移動、削除、書き換えない。
- Pageルートの右クリックメニューやStudio Change Coreは変更しない。

## 検証

- 対象関連テスト：41 PASS（Move適用済みStudio検証環境と連携）
- Studio Change Core CLI: 一時Launch設定JSONへ `page_id=work, parent_item_id=""` のファイルAddを実行し `COMMITTED` を確認。元の設定JSONは変更なし。
- ソース構文チェック：PASS。

## 残課題

Windows 11 + PySide6での実際のExplorer→Files List余白Dropは未検証。実機で複数ファイルDrop、カテゴリーフォルダー配下Drop、およびFiles ExpルートでファイルDropが拒否されることを受入確認する。
