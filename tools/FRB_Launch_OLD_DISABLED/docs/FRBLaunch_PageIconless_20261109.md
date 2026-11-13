# FRB Launch Page行のフォルダーアイコン非表示（試行）

- 基準ソース: `launch_app_20261109_112239.zip`
- 変更対象: Files → Exp に表示する **Pageルート行のみ**
- 変更内容: 黄色いフォルダーアイコンを非表示にする。Studioで設定したPageアイコン（タイトル文字列中の絵文字）をそのまま表示する。
- 対象例: `> 📁 💼 My Work` → `> 💼 My Work`（表示例）。
- 維持: Pageの展開用矢印、クリック・ホイール・選択・階層構造、Page内の通常フォルダーアイコン、PC/実フォルダーアイコン、設定JSONの構造。
- 戻し方: 差分ZIPの `src/remote_files_explorer.py` を適用前のものに戻せば元の表示に戻る。

## 変更ファイル

- `src/remote_files_explorer.py`：`_append_virtual()` 内で `node['kind'] == 'page'` の場合だけ空の `QIcon()` を使用。
- `tests/test_page_root_iconless_20261109.py`：Page/通常仮想フォルダー/実行ファイル行の表示契約をQt非依存でテスト。
- 本メモ。

## 検証

- 関連テスト32件 PASS（Page投影・公開版固定名の整理・Exp既存ルート関連含む）。
- 広域の旧テスト群には12件の失敗があるが、修正前ソースでも**同じ12件が失敗**したことを確認。今回の差分による新規失敗は確認されていない。
- Linux環境にPySide6がないため、Windows GUI上の実表示・描画位置は未確認。特に行の余白と矢印との距離を確認してほしい。
