# FRB Launch v75 差分パッチ（2026-11-01）

## 基準
`launch_app_20261101_074547.zip` を基準に修正しています。

## 変更内容

### Remote の Browser ボタン右クリック
- ブックマーク第1列の検索ボックス**直下**に「新規タブ」「カレントタブ」のラジオボタンを追加。
- **初期値は「新規タブ」**。メニューを開き直すたび新規タブが初期値。
- 第1列のラジオボタンで選んだ開き先を、右に階層展開したフォルダー内のURLにも適用。
- URL選択時に Browser ワークスペースへ自動切替して開く。
  - 新規タブ: 現在のWebタブを残し、新しいタブを作ってURLを開く。
  - カレントタブ: 今表示しているタブのURLを差し替える。
  - タブが存在しない場合は、どちらでも新しいタブを作成。
- ブックマークフォルダーの階層展開と検索機能は維持。
- Browser画面の左ブックマーク欄など、Remote以外の通常ブックマーク操作は変更なし。
- `webview_settings.mode != 'embedded'`（外部ブラウザ運用）では、従来の外部ブラウザ実行にフォールバック。タブ指定は埋め込みBrowser時のみ対象。

## 変更ファイル
- `src/app.py`: Remote用のラジオボタンUI、およびURL実行時の開き先の分岐
- `src/expanded_view.py`: `show_web_url(url, *, new_tab=False)` を追加（従来呼び出しはカレントタブのまま）
- `tests/test_remote_browser_bookmark_tab_target_v75_20261101.py`: 新規/カレント/通常操作の回帰テスト

## 確認
- 関連テスト: **42件PASS、2件SKIP**
- `python -m py_compile src/app.py src/expanded_view.py`: OK
- Windows / PySide6 実機のGUI表示は未確認（この環境ではPySide6なし）
- 別範囲の古いテストには既知の仕様差が残っていますが、今回確認した3失敗は元ZIPでも同様に再現。

## 手動確認手順
1. Remoteの「Browser」を右クリック。
2. 検索欄の下に「● 新規タブ / ○ カレントタブ」が表示されること。
3. 新規タブのままブックマークURLを選択 → 別タブで開き、元タブが残ること。
4. もう一度Browser右クリック、「カレントタブ」を選択 → 選んだURLに既存タブ内で移動すること。
5. フォルダーを右へ展開して深い階層のURLでも同様に動くこと。
6. Browser画面左側での通常のブックマーククリックは従来どおりであること。

※ v74までのFiles/Browser右クリック機能、お気に入り登録、黒い残像の保留状態には手を加えていません。


## ワープ差し棒 ～ぐりぐりスピナー～（上下追従）
設定メニューの「ワープ差し棒 ～ぐりぐりスピナー～（上下追従）▶」から「使用しない」「Files List / Exp を直接選択」「Windowsマウス方式」の3択で選びます。有効にすると、上下追従も自動的に有効になります。旧「純粋なマウス差し棒」は設定メニューから廃止しました（内部処理は互換性のため残しています）。既存の保存設定も読み替えます。


## 手動登録URLの標準動作
Launchに登録したHTTP(S) URL（単一の `Open` アクション）は、ブラウザー未指定ならLaunch内Browserの**新規タブ**で開きます。実行元が別のPageやCompact表示でも、Files/Browser表示へ切り替えて開きます。Chrome/Edgeやプロフィールを明示した場合、WebViewを外部ブラウザー方式に設定した場合は、従来の外部起動を維持します。複数アクションのコマンド、ファイルや `shell:` は従来どおりです。

## Compact表示
Compact/Files切替は画面の切替ボタンから従来どおり使えます。配布版では、コンテキストメニューから重複した「Compact表示へ切り替え」項目を非表示にしました。


## 公開版のPageとFiles設定（2026-11-09）

FRB Launchは、初期状態で**Files Exp / Files List**を備えます。
Studioの「Page」編集画面で**タイトル／Pageアイコン**を変更でき、Launch側のタブやFiles ExpのPage表示に反映されます。
設定メニューの **「Pageボタンを非表示」** は初期ONです。必要な場合だけチェックを外すとFiles / Browserの右横にPageボタンを再表示できます。
設定JSONのFiles行はシステム用のExp/List枠として扱い、`enabled=false` にしてもFiles画面は消えません。My Work配下への二重表示もしません。
専用「手裏剣スクロール」ボタンは表示しませんが、**ぐりぐり高速回転から起動する自動手裏剣**は引き続き利用できます。
詳しい互換・実機確認事項は `docs/FRBLaunch_PublicReleasePolish_20261109.md` を参照してください。

## FRB Launch 0279 — 運用設定JSONの固定名

運用設定は `config/frb_launch_data.json` に統一しました。形式バージョンはファイル内部の `launch_format_version` で管理します。
旧 `frb_launch_sample_data_v0_1.json` を編集している環境では、初回起動・ビルド時にバックアップを作成して新名へ移行します。Launch/Studioを閉じてから適用してください。
**既存環境には差分ZIPを適用し、完全版ZIPの初期JSONを上書きしないでください。**
詳細：`docs/FRBLaunch_0279_ConfigFilenameStable_20261112.md`
