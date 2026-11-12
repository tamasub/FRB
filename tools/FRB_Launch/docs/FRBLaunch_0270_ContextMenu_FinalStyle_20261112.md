# FRB Launch 0270｜Exp/List コンテキストメニュー最終スタイルの共通化

## 受入画像と不具合

2026-11-12 12:52 JST 時点の最新 `launch_app_20261112_125203.zip` で、
同じ「コピー」「切り取り」「新規作成」等のメニューでも、Exp/List/フォルダーメニューごとに
アイコンの左余白・サイズ・位置が異なる。

## 原因（コードにより特定）

1. `Launcher._wire_hybrid_context_menu()` は `style_context_menu()` を通じて共通QSSを適用していた。
2. しかし Exp 系の `RemoteFolderActionsMenu` は `CascadeMenu.popup()` を経由し、その内部で再度 `Launcher.style_cascade_menu()` を呼ぶ。
3. `style_cascade_menu()` は無条件で `menu.setStyleSheet(LIGHT_MENU_QSS)` により共通QSSを上書きしていた。
4. List 系の通常の `QMenu` は同じ後処理を通らないため、最終的な描画契約が異なっていた。
5. さらに、共通QSSに入っていた `QMenu::icon ... left:14px` は、普通のListメニューだけを右に押し出す要因になっていた。
6. 旧テストは `style_context_menu()` の直後しか検査せず、`CascadeMenu.popup()` の最終上書きを検査していなかった。

## 修正

- `style_context_menu()` がコンテキストメニューの意図と追加スタイルをマークする。
- `style_cascade_menu()` の最終パスではマーク付きメニューだけ同じ共通関数を再適用する。
- 通常の CascadeMenu は既存スタイルのまま（変更対象外）。
- `QMenu::icon` の14px強制右移動を撤去し、ネイティブの QAction アイコン配置へ戻す。
- アイコン素材には一切加工・縮小処理をしない。
- チェックツールに最終スタイル上書き検出・アイコン手動オフセットの禁止を追加する。
- 単体テストは初期スタイル→CascadeMenu最終スタイル→Dark切替を実行検査。
- PySide6がある実機用GUIテストは最終スタイルを再適用してから描画ピクセルを比較。

## 保証の境界

Linux環境の静的テストと擬似Qtメニューテストでは、最終QSSが一致することを検証できる。
Qt/Windows実画面の描画ピクセルそのものはPySide6がない環境では確認できない。
そのためこのパッチの実機見た目を PASS と主張しない。

Windowsでは **同じ実フォルダー** をExp列、List列、フォルダー展開メニューから右クリックし、
「コピー」のアイコンについて、表示サイズとアイコン左端位置を比較する。

この変更で「余白が揃った」と言うためには、共通関数が存在するだけでなく、
**最終的に表示されるQMenuスタイルとQt実描画の比較まで必要**である。
