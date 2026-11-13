# FRB Launch：Exp / List コンテキストメニュー共通描画契約（2026-11-12再改訂）

## 実機で発見された回帰

修正前後のWindows比較画像（2026-11-12 12:38提供）で、**ExpとListのメニューに同じ余白規則が適用されていない**だけでなく、共通化後のアイコンが小さくなっていた。

原因は `src/context_menu_presentation.py` の旧 `_normalize_action_icons`。元アイコンを18pxに縮小して24px透明キャンバスに配置したが、Qt の `QMenu` は更に `PM_SmallIconSize`（Windows標準では多くの場合16px）でQIconを取得して描くため、**不要な二段階縮小**が発生した。

また、前の `QMenu::icon { margin-left:5px; margin-right:5px; }` はCSSの見た目の文字列が揃っていても、アイコン描画位置をメニュー項目の左端から一定にする保証にはならなかった。

## 正式な共通責務

1. **アイコン画像は加工しない**。Windows OSアイコン、自作FRBアイコン、無効表示やテーマ別アイコンの `QAction.icon()` を共通描画処理が置換・縮小しない。
2. **描画位置はQMenu項目の左端基準**。`QMenu::icon` の `subcontrol-origin: border; subcontrol-position: center left; position: relative; left:14px` を全Exp/Listの共通CSSに1か所だけ置く。`Qt.Popup` と `Qt.Tool`、通常 `QMenu` と `RemoteFolderActionsMenu` に別の左余白を指定しない。
3. **Qtの元のメニュー小アイコン規格で描画**。アイコン画像と表示サイズを混同しない。Qt内部がデバイスDPIを考慮する。前回の「18px glyph + 24px canvas」は廃止。
4. **メニューを開く共通入口を維持**。`Launcher._wire_hybrid_context_menu` → `style_context_menu`。サブメニューも同じ共通設定。メニューのアクション、フォルダー操作、ぐりぐりは変更しない。
5. **新たな局所CSS・アイコンリサイズを禁止**。`scripts/check_context_menu_contract.py` が独自CSSや`context_menu_presentation.py`内の縮小描画を検出する。

## テスト

- `tests/test_shared_context_menu_presentation_20261112.py`：ソースアイコン未変更、共通CSS、重複呼出でアイコンを加工しない、ビルド時ゲート。
- `tests/test_0269_context_icon_remote_optional_20261112.py`：以前の誤った「24px透明キャンバス」を期待値から除去。
- `tests/test_context_menu_icon_qt_geometry_20261112.py`：PySide6が使える環境では実際にQtでメニューを描画し、通常QMenu・Tool化QMenu・QMenu派生型のアイコン位置と描画幅をピクセル単位で比較。PySide6なし環境ではSKIPとなる。
- `python scripts/check_context_menu_contract.py`：共通描画チェック。

**Linuxの検証環境にはPySide6がない**ため、今回も実機ピクセルテストは未実行。Windowsで確認しなければ「余白・サイズともに実機で修正完了」と断定してはいけない。

## Windows受け入れ条件

- 同じ実フォルダーをExp・Listの双方で右クリック。各行のアイコンが左端から等距離で、画像提供時の「修正前のList列」程度の大きさである。
- 自作アイコン・OSフォルダーアイコン・通常/無効アイコン、Light/Dark、サブメニューで崩れない。
- ぐりぐり選択・通常マウスクリック・サブメニュー開閉が元どおり動く。

この回では右クリックアクション内容・列切り替え・ダイアログ入力の仕様には触らない。
