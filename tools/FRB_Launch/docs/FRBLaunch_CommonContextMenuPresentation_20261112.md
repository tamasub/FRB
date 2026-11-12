# FRB Launch：Exp / List 共通コンテキストメニュー表示契約

## 背景・不具合

同じ実フォルダーを右クリックしても、入口によってアイコン位置・左右余白が異なっていた。

- Exp のフォルダー・リモコン経由では `RemoteFolderActionsMenu(CascadeMenu)` を使用。
- List の背景・選択行では通常の `QMenu` を使用。
- メニューごとに `LIGHT_MENU_QSS` と `context_menu_spacing_qss()` を個別結合し、一部は別の `QMenu` スタイルだけで表示。
- Windows の `QFileIconProvider` と FRB 手描きアイコンでは、返すアイコンの元サイズや透明画素が違う。
- 既存の `QMenu::icon { margin-left:5px; margin-right:5px; }` という文字列の存在だけをテストしていた。**実画面の左右余白・描画領域は保証されていなかった**。

## 共通責務と実装

1. **すべての Exp / List コンテキストメニューの表示経路は、`Launcher._wire_hybrid_context_menu` を通る。** 設定メニューのみ `context=False` とする。
2. `_wire_hybrid_context_menu` から `context_menu_presentation.style_context_menu` を1回呼び、通常 `QMenu` と `RemoteFolderActionsMenu` に同じ行レイアウト・テーマを適用する。
3. `QMenu::item` は `padding:7px 9px`、`QMenu::icon` は24px枠・左右各5pxの固定値。アイコン自体は、元の画像を18pxにした上で24pxの中央に描く。OSアイコンとFRBアイコンが同じ中心を利用する。
4. アイコンの正規化は QAction の動的プロパティで1回だけ実施する。テーマ変更やサブメニュー表示で繰り返し縮小しない。
5. 「新規作成」サブメニューは専用スタイルではなく同じ `style_context_menu` を呼ぶ。ツールメニュー固有の矢印画像は `extra_qss` で追加し、共通ジオメトリ定義を上書きしない。
6. **新規メニューの実装者は**個別スタイルを書かず、`_wire_hybrid_context_menu` に接続する。メニューがどの操作対象のために出たか（Exp/List）は、ナビゲーション項目の追加にだけ使う。

## 再発防止・品質ゲート

- `python scripts/check_context_menu_contract.py`：標準表示ゲート、現在のメニュー入口、アイコン規格、サブメニューの適用を静的検査。
- `tests/test_shared_context_menu_presentation_20261112.py`：実際のスタイル共通性・異なる元アイコンのキャンバス位置・二重縮小防止・ゲート検査を検証。
- `src/make_launch_zip.py` と `_build_windows.bat` の作成前検査へ追加。既存 `check_dialog_contract.py` とともに、不適合時はビルド/バックアップZIP生成を拒否する。
- 今回の差分は共通ダイアログ（ぐりぐりボタンセレクター）の作業途中ソースに適用済み。そのため両共通化の変更を一つの差分に含めている。

## Windows実機で必ず確認すること（未実施）

1. **同じ実フォルダー**を Exp と List の双方で右クリックし、アイコン中心・左右余白・文字開始位置を比較する。
2. リモコン表示・非表示、Light・Dark、通常アイコン・Windows OS アイコン、新規作成/Launch Menu サブメニューで揃っていること。
3. メニューのぐりぐり操作・選択・実行・閉じる操作が以前通りであること。
4. Gitコミットメッセージを含む、新しい/既存のLaunchダイアログはリモコン非表示でもホイール選択＋Launchの余白クリックで選択ボタンを実行できること。**実Cancel/OKを直接クリックした場合は直接クリックが優先**されること。
5. Windowsで `src/make_launch_zip.py` と `_build_windows.bat` を実行し、二つの共通契約ゲートが通過すること。

Linux検証環境にPySide6がないため、Qt/Windowsの実画面上の余白をピクセル比較したとは扱わない。静的検査が成功しても、そのことと実画面の完全な保証は分けて報告する。
