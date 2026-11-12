# FRB Launch 0280 — Files / Browser右側の空白をダブルクリックで最大化・復元

## 変更内容

- Files / Browser タブの右側に広がる空白エリア（`expandedWorkspaceDragHandle`）だけ、左ダブルクリックでメインウィンドウを最大化／元のサイズへ復元する。
- 既存の「最大化ボタン」に使われている `Launcher.toggle_maximize_restore()` を再利用する。最大化前のサイズと位置を保存する既存仕様を維持する。
- 空白部分のドラッグによるウィンドウ移動は維持。ただし最初のクリックだけでは OS にドラッグ開始を渡さず、一定量以上動いたときに移動を開始する。これにより Windows のネイティブ移動開始がダブルクリック認識を妨害するリスクを避ける。
- Files・Browser のタブ本体、Pageボタン、検索欄、パンくず、一覧にはダブルクリック最大化を割り当てない。

## 変更ファイル

- `src/passive_header_drag.py`
- `tests/test_workspace_blank_doubleclick_maximize_20261112.py`（追加）
- `tests/test_browser_resize_and_workspace_drag_v70_20261101.py`（既存 UI の `addWidget` 引数変更に追従するテスト期待値の更新）

## 確認事項

- 通常サイズ → 赤丸空白の左ダブルクリック → 最大化
- 最大化 → 同じ場所の左ダブルクリック → 元のサイズ・位置に復元
- 空白をドラッグ → ウィンドウ移動
- Files / Browserタブをダブルクリックしても最大化しない
- 最大化ボタンでも従来どおり切り替えできる

## 制約

QtのWindowsネイティブイベントとウィンドウマネージャーの動作は本実行環境で再現できない。Windows実機GUIで最終確認すること。
