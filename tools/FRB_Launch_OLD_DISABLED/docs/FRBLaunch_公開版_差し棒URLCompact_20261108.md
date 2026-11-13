# FRB Launch 公開版メニュー・URL動作整理（2026-11-08）

## ベース
`launch_app_20261108_205020.zip`（ユーザー提供）

## 1. ワープ差し棒：公開設定を3択へ一本化

設定メニューの親項目：

`ワープ差し棒 ～ぐりぐりスピナー～（上下追従） ▶`

子項目（QActionGroupにより択一）：

- 使用しない
- Files List / Exp を直接選択
- Windowsマウス方式

従来の `マウス差し棒 ▶` と独立した `上下追従` チェック項目は公開メニューから廃止。
内部の `experiment_mouse_pointer_rod` / `experiment_mouse_pointer_rod_windows` /
`experiment_mouse_pointer_rod_smart` は変更しない（既存設定・エンジン互換）。

- 有効な2方式を選ぶと、上下追従も自動ON。
- 過去の設定で差し棒ON＋上下追従OFFのときは起動時に上下追従ONへ移行。
- 「使用しない」選択時は表示を無効化し、上下追従の内部設定は保存したまま。
- Windowsマウス方式が保存済みならその選択にチェックが付く。利用者の既存選択を勝手に変更しない。

## 2. 手動登録URLは標準でLaunch内Browserの新規タブ

次の条件を満たす単一 `Open` アクションを、Launch内部Browserの新規タブへ。

- `launch_target`: `http://` または `https://` の有効なURL
- `launch_browser` と `launch_browser_profile` を明示していない
- `webview_settings.mode`: `embedded`

実行元のPageが別、もしくはCompact表示ならFiles/Browser画面へ切り替える。
Launchを実行直前に非表示にしないので、タブが画面に表示される。

互換性：

- Chrome/Edgeまたはプロフィール指定：従来どおり外部起動。
- `webview_settings.mode=external`：従来どおり外部起動。
- WebViewが利用できないとき：従来のURLオープナーへフォールバック。
- ファイル、`shell:`、`Run`、複数アクションのコマンド：従来動作。
- Browserブックマークで明示された新規／カレントタブ選択：既存挙動維持。

## 3. Compact切替：コンテキストメニュー項目のみ削除

設定メニューから `Compact表示へ切り替え` を出さない。切替処理・
ヘッダーボタンは存続する。内部アクションは互換性のため保持。

## テスト

- 今回のURLルーティング、メニューUI契約、差し棒設定切替および周辺テスト：47件PASS。
- 別の旧UI仕様に依存するテスト5件は元ZIPでも同じ失敗を確認。
- Windows / PySide6 の描画・クリック操作はこの環境では未検証。

## Windows実機での確認

1. 設定メニューにワープ差し棒の親項目だけが出ること。子3択のいずれか一つにチェックが付くこと。
2. それぞれの選択後にRemoteを操作し、上下追従が有効であること。
3. Launchに新規登録したURL（外部ブラウザー未指定）を、別PageとCompact表示から実行する。Browser新規タブにURLが開くこと。
4. 明示的にChrome / Edgeで登録したURLは外部に開くこと。
5. 設定メニューにCompact表示切替は出ないが、画面の切替ボタンは操作できること。
