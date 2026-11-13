# FRB Launch 0273｜コンテキストメニューの文字・アイコン消失への修正

## 事象（Windows実機、ユーザー提供の画面）

Exp列とList列のコンテキストメニューが、広い灰色背景のままほぼ空白になった。
右側のサブメニュー矢印と最終行の「プロパティー」など、一部のみ表示された。

## 直接の問題箇所

0272で `FRBContextMenu.paintEvent()` を追加し、`QStyleOptionMenuItem.text` / `.icon`
を空にした後に `QPainter` で独自描画するよう変更していた。
この独自描画がWindowsで期待どおり完走せず、Qt本来の文字・アイコンが消失した。
独自描画が完走しなかった具体的なQt内部条件・例外の有無は、ログがないため未特定。

## 今回の修正

1. `FRBContextMenu.paintEvent` の**上書きを撤去**。`RemoteFolderActionsMenu` → `QMenu` のネイティブ描画に戻す。
2. `FRBContextMenu` ファクトリーと内蔵 `RemoteContextWheel` の所有権・ライフサイクルは保持。
3. Exp/List共通CSSゲートは維持。ただしアイコンや文字の独自描画・画像縮小は追加しない。
4. ソース検査で `FRBContextMenu.paintEvent` や QAction の文字・アイコン消去を禁止。
5. Windowsの `_build_windows.bat` に実描画スモークテストを追加：ExpとListの双方で「コピー」の**アイコンと文字**をピクセル確認できなければビルドを中断する。

## 受入期待値（Windows実機）

- ExpとList双方の全項目の文字とアイコンが見える。
- サブメニュー矢印・選択背景・クリック実行が維持される。
- リモコンを隠しても「右クリック→ぐりぐり選択→クリック実行」が成立。
- アイコン左右の余白とExp/List位置差は**別途実画面で再測定**する。0272の固定22px独自描画を正しい解として扱わない。

## 検証限界

このLinux環境にはPySide6がないので、Windowsの実描画・Runnerの実操作は未確認。
静的テストや疑似RunnerテストをGUI合格の根拠にしない。
なお、手元の広範囲テストで残った8件のFAILは、今回の修正前ZIPでも同じ8件が発生することを確認した。

## 追加した共通保証

- 新規Exp/Listメニューは `FRBContextMenu` で生成。
- Runnerはメニューの所有物。
- メニューの前景描画は Qt に一任し、手動消去・再描画の迂回を禁止。
- Windowsパッケージ作成前に実レンダリングを検査。
