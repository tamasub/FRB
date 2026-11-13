# FRB Launch / Files List JSONメニュー表示列切替（2026-11-11）

## 要望
Files Listを実フォルダー参照（Files）に使用するときは従来どおり、設定JSONのメニューを表示するときは更新日・サイズではなく説明と項目の種類を表示する。

## 実装
- **Files（物理ファイル）**: `名前 | 更新日 | サイズ | 種類`（変更なし）。既存のWindowsファイル種類表示、更新日時、サイズとソート条件を保持。
- **設定JSON（仮想メニュー）**: `名前 | 説明 | 項目の種類`。`description` と **元のJSONの** `item_kind`（category / command / selection / directory 等）を表示。説明には全文ツールチップを付加。
- 仮想メニューにファイル用の「更新日」「サイズ」「種類」は表示しない。列見出しクリックでは説明／項目の種類の昇降順をソートし、初期状態のJSON項目順は維持。
- 物理ファイル用のユーザー設定済み列幅・列順は、一時的にJSON用の列幅へ変えた後で復元する。JSON表示時の列幅操作は物理ファイル用の永続設定へ書き込まない。
- メニューのデータ、元のitem_kind、実行動作、ファイル操作は変更しない。

## 確認
- `pytest -q tests/test_middle_virtual_json_columns_20261111.py tests/test_middle_explorer_columns_v50_20261031.py tests/test_middle_explorer_sort_arrow_direction_20261101.py tests/test_middle_metadata_readonly_20261101.py tests/test_middle_folder_filter_v35_20261030.py`
- 自動テストはPySide6を使わないユニットテストで実施。実画面のWindows起動確認は未実施。
- 既存のテスト群には旧UIの期待を固定したテストも含まれ、また実行環境にPySide6/Studio依存ファイルがないため全件PASSとはしていない。

## 差分ファイル
- `src/expanded_view.py`
- `src/middle_folder_filter.py`
- `src/middle_column_presentation.py`（新規）
- `tests/test_middle_virtual_json_columns_20261111.py`（新規）
- `docs/FRBLaunch_FilesList_JSON_MenuColumns_20261111.md`（新規）
