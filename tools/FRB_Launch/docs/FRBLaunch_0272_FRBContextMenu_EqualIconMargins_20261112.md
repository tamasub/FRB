# FRB Launch｜0272：Exp / List コンテキストメニューの本当の共通化

基準：`launch_app_20261112_131341.zip`（2026-11-12）

## 原因と変更

- 従来は `RemoteFolderActionsMenu` と `QMenu` を使い分け、後から共通 CSS を指定していた。前回の `FRBContextMenu` 導入だけでは不十分で、Qt 内部の `CE_MenuItem` が QAction の構成やウィジェット状態に応じてアイコン列・文字列を別々の位置に描いていた。
- Exp・List の全入口で、同じ `FRBContextMenu` を生成するファクトリーを利用する。`FRBContextMenu` 自身が `RemoteContextWheel`（ぐりぐりクリックRunner）を生成・停止する。リモコン表示状態は起動条件にしない。
- メニュー項目の背景・選択表示・区切り・サブメニューの動作は Qt/QStyle に任せ、**アイコンと文字だけ**は `FRBContextMenu.paintEvent()` で共通の配置規則を使用する。描画する QAction のアイコン画像を透明キャンバスへ再縮小することは禁止。
- アイコンの配置基準は **メニューの左端**。左余白22px＋アイコン16px＋右余白22px。文字開始位置は60px。設定を変える場所は `src/context_menu_presentation.py` の `CONTEXT_ICON_SIDE_GAP` と `CONTEXT_ICON_DRAW_SIZE` のみ。
- Exp専用／List専用の QSS は廃止し、共通レイアウト計算を検査。右クリック地点やメニューの QAction 内容に依存してアイコン列幅が変わらない。

## テスト

- `python scripts/check_context_menu_contract.py`：共通生成・内蔵Runner・描画契約・入口を静的検査。
- `python -m pytest -q tests/test_frb_context_icon_equal_margins_20261112.py tests/test_frb_context_menu_owns_runner_20261112.py`：共通部品・ランナーの接続と寿命・左右余白等幅を確認。
- Windows／PySide6環境（グラフィック動作テスト）:
  `python -m pytest -q tests/test_frb_context_icon_equal_margins_qt_20261112.py tests/test_frb_context_menu_text_lane_qt_20261112.py tests/test_context_menu_icon_qt_geometry_20261112.py`

## Windows実機受け入れ（必須）

1. 同じ実フォルダーを **Exp列**と**List列**でそれぞれ右クリックし、「コピー」のアイコンと文字の開始位置がそろっていること。
2. どちらも **アイコン左の空白とアイコン右～文字開始の空白が同じ程度**であり、元のアイコンサイズが維持されること。ホバー／選択・disabled項目・サブメニュー矢印も確認。
3. **リモコン非表示**で、Exp・Listいずれも「右クリック→ホイールで項目選択→クリックでその項目を一回だけ実行」が可能なこと。
4. メニューを閉じるとRunnerが停止し、連続ポップアップでRunnerを重複起動しないこと。
5. Light / Dark それぞれで上記を確認すること。

このLinux実行環境にPySide6はない。**Windows実画面での描画・ホイール操作は未検証**。静的テスト成功だけで実機合格としない。
