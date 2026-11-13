# FRB Launch 公開版 UI 整理（2026-11-09）

## 基準

- 唯一の変更元: `launch_app_20261109_105041.zip`
- 新規の配布物は **差分ZIP / FULL ZIP**、パスはすべてLaunchルート相対。
- 既存のDataJSONとユーザー設定を上書きする運用はしない。
- 変更は公開版の5項目に限定。手裏剣の加減速係数・自動起動閾値は変更しない。

## 1. Pageタイトルとアイコン（Studio）

- `pages_view` に `icon_key`（Pageアイコン）選択フィールド追加。選択肢は「なし／💼／🎣／🪟／📁／⭐／🚀／🧰／🖥️／🌐／📝／📌／🎯／⚙️／📚／✨」。
- Page名は Launch JSON `pages[].title` を正とし、Expの仮想 `My Work` 等に固定名を使用しない。
- 既存のタイトルが絵文字付きでも、アイコン選択時は古い先頭絵文字を表示上だけ置換する。元のDataJSONを勝手に変更しない。`icon_key` を持たない既存Pageは従来の表示を維持。
- CompactのPageタブ／ExpのPageショートカット／Files Exp仮想Page／グローバル検索のPage名を共通化。
- Launchに戻るときの設定再読込、およびデスクトップから呼び出すときの再読込を補強。

## 2. Filesをシステム専用の常設Exp/Listとして扱う

- `config/expanded_view_options.json` の `files_item_id` に対応するJSON行は**Filesシステム枠**。
- `enabled=false` でもExpandedのFilesルートとして採用。**他の通常項目の enabled は引き続き尊重**。
- Files行をMy Work等の仮想Pageツリーから除外し、二重表示を防止。
- **新規利用の起動モードはExpanded（Files Exp/List）**。以前ユーザーが明示したCompactモードは保持可能。
- Compact表示への明示切替、検索結果、選択中表示は従来の操作を残す。Filesのシステム扱いはDataJSONの物理削除や自動追加を意味しない（Files行の実在は引き続き前提）。

## 3. Pageボタン（初期OFF）

- 設定にチェック式 `Pageボタンを非表示` を追加。QSettings `hide_page_buttons`、未設定時 `true`。
- Files / Browser右横のPageショートカットを初期非表示。チェック解除で再表示できる。
- Pageそのもの、ショートカットキー、スタジオ編集は削除しない。
- 非表示時のPage方向へのキーボードフォーカスは、隠れたPageではなくFiles/Browserへ逃がす。

## 4. デスクトップ最初のダブルクリックでRemoteが表示されない件

- 仮説：既にLaunchが表示されていると、ダブルクリックの**最初のMouseDownがLaunch外クリックとして処理され、閉じたあと次のクリックのペアが拒否されていた**。
- Remote表示設定ON時のみ、デスクトップ上の外クリックをOSのダブルクリック時間だけ保留。**背景ダブルクリック確定→保留中の閉じをキャンセルしRemoteを開く**。単一クリック→従来どおり閉じる。デスクトップ以外の外クリック→即座に閉じる。
- ホイール操作やWindowsのフォーカス仕様は触らない。OS実機・Explorer/MSAAの確定的な再現確認はまだ。

## 5. 専用「手裏剣スクロール」ボタンを非表示

- Remoteの専用 `ShurikenScrollPad` をレイアウトから取り除き、非表示の自動滑走エンジンとして保持。
- `ぐりぐり` の高速連続回転での手裏剣自動起動／加速／減速／停止、Files Listのスクロールと終了処理は維持。
- `ShurikenButton`（「1の手」実行ボタン）は別機能のため維持。

## テスト結果と実機確認

- `tests/test_public_release_polish_20261109.py` を追加（Page名とアイコン、Filesシステム枠、UI静的配線、ダブルクリック保留のモデルテスト）。
- 変更により無効化された旧ボタン表示位置テスト2件は、**専用ボタン非表示＋エンジン継続保証**へ改定。
- Python AST構文、JSON読込確認。PySide6 / Windowsの実機GUI、ホイール、Explorer UI Automation はこの環境で実行できない。
- 添付元ZIPと同じテストで失敗する既知の旧仕様テストがあり、全件PASSとは記載しない。新しい正しい失敗は元ZIPとの差分で判断する。

### Windowsでの重点試験（公開前）

1. StudioのPage編集画面でPage名・アイコンを保存 → Launchを開き直さず復帰 → コンパクトのタブとFiles Expの仮想Page名称が一致するか。
2. Files行 `enabled=false` の状態でLaunchを起動 → Files Exp/Listが表示され、My WorkのFiles重複がないか。`enabled=true` に戻しても同じ表示か。
3. `Pageボタンを非表示` のチェックが初期ONか。OFFでPageボタンが戻り、再起動後も状態保持されるか。
4. Remote設定ON・Launch表示中/非表示中・外クリックで隠すON/OFFで、**デスクトップ背景を1回ダブルクリック** → リモコンが必ず1回で開くか。背景を1回クリック→規定の遅延後に閉じるか。Chromeクリック→即時で閉じるか。
5. 専用スクロールボタンが出ず、**Files List中間・末尾・300行/4700行**でも「ぐりぐり」の連続回転で自動手裏剣が走り、逆回転で減速、クリックで停止するか。

**留意**：手裏剣の位置依存の過去不調はPC再起動で消失したが根本原因未解明。今回のUI整理でその現象を直したとは主張しない。
