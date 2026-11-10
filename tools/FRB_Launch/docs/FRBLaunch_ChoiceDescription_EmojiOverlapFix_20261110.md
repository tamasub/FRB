# FRB Launch — 選択グリッドの絵文字二重表示修正（2026-11-10）

- **改修起点**：ユーザー提供 `launch_app_20261110_091828.zip`
- **観測**：選択グリッドの説明列で、絵文字が重なって二重に見える。
- **原因**：`QTreeWidgetItem([title, desc])` によるQtの標準描画と、透過背景のReadOnly `QLineEdit(desc)` が同じ説明列を同時描画していた。
- **修正**：選択モードのみ、`QTreeWidgetItem` 側の説明列を空文字にする。ReadOnlyの `QLineEdit` が唯一の説明欄表示になる。非選択モードは従来の `desc` を表示。
- **維持する機能**：絵文字の部分選択、Ctrl+C、右クリックコピー、選択チェックボックス、F12送信、検索時のソート。選択値および設定JSONは変更しない。
- **修正範囲**：`src/app.py` と回帰テスト `tests/test_choice_description_single_paint_20261110.py`。

## 検証

- `python -m pytest -q tests/test_choice_description_single_paint_20261110.py tests/test_public_release_readonly_icons_studio_roots_20261110.py tests/test_main_grid_visual_state_20261020.py`
- PySide6未導入の検証環境ではQt GUIテストはスキップ。Windows GUIの実機表示は未確認。
- その他の古いテストは、設定JSONに追加されたメール宛先や別機能拡張を想定しておらず、独立に失敗するものがある。今回の原因とは区別する。
