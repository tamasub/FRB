# FRB Launch v0.1 — 操作確認用初版

Python / PySide6によるWindows 11向けランチャーです。ソースとWindows EXEビルド用バッチを同梱しています。完成済みWindows EXEはこのZIPに含まれていません。

## 起動

1. WindowsにPython 3.11または3.12（64bit、pyコマンド利用可）を用意。
2. ZIPを編集可能な場所へ展開。
3. build_windows.batを実行。初回はインターネットから依存ライブラリを取得します。
4. dist/FRBLaunch/FRBLaunch.exeを起動。画面は出さずトレイへ常駐します。
5. 入力先を選んでCtrl+Shift+;で呼び出してください。

EXEはonedir形式です。dist/FRBLaunchフォルダー全体を保持してください。Windows起動時の自動起動登録は任意で、初版は自動登録しません。

## 実装した機能

- トレイ常駐、右クリックの開く・再読込・設定フォルダー・終了。
- ユーザー単位の二重起動防止。2回目の起動は既存画面を表示。
- Windowsグローバルホットキー。競合は通知。
- 検索欄、Pageタブ、アイコン・タイトル・説明の縦一覧。
- 全Pageの登録項目を検索。タイトル・説明・親カテゴリー・実行定義などを照合。appdataでRoaming/Localを表示。
- カテゴリー/実フォルダーの横展開。標準QMenuによるマウスホバーと矢印操作。
- 複数選択・チェック、F12で値を結合して送信。
- 各ITEM内のlaunch_actionsを順次実行。
- SendKey（クリップボード貼り付け方式）、ClipboardCopy、Open、Run。
- %today:yyyyMMdd%、%yesterday:yyyy/MM/dd%、%now:yyyy/MM/dd HH:mm:ss%、%clipboard%、固定値変数。
- 未知の変数は停止。置換結果の再展開は行わない。%%は文字通りの%。
- 呼び出し時の設定再読込。構造不正時は前回正常設定を維持。
- 外部処理の非同期待機。失敗・タイムアウト時は後続中止。

## 操作

- 文字を入力：検索（一覧フォーカスからも入力可）。IME候補操作はIME優先。
- ↑↓：項目選択。
- →：子メニューを横に表示。子メニューは←/Escで戻ります。
- Enter：カテゴリー内一覧へ移動、選択一覧を開く、または実行。
- 左矢印：通常一覧の親へ戻る。検索欄内ではカーソル移動。
- Ctrl+PageUp/PageDown：Page切替。
- Space：宛先選択時のチェック。F12：確定。
- Esc：検索クリア → 選択画面/階層から戻る → 非表示。
- 外部アプリへフォーカスが移ると非表示。

## 設定

EXEの隣のconfig/frb_launch_sample_data_v0_1.jsonを編集します。添付のdefs/launch/frb_launch_maintenance_view_def_v0_1.jsonはStudio用です。Studioで管理する際はdefsとDataをStudio側へ配置して編集し、保存済みDataをLaunchのconfigへコピーしてください。Studio側とLaunch側のコピーは自動同期しません。

メニュー詳細のlaunch_actions子配列にlaunch_action_typeとlaunch_text等を登録します。Studio固有のActionとLaunchの実行処理は別です。

SendKeyは文字列をクリップボードに設定してCtrl+Vを送ります。クリップボードは送信文字列に置き換わります。呼び出し元ウィンドウへの復帰を確認できない場合は送信を中止します。元の入力欄が引き続き有効であることが前提です。管理者権限アプリへの入力、貼り付け禁止欄などは対応保証がありません。

外部プログラムはlaunch_program、launch_arguments配列、launch_working_directoryで指定。launch_wait_for_exit=trueでは終了コード0を成功とします。タイムアウトでは後続を中止しますが実行中の処理を強制終了せず、処理が終わるまで新規実行を待ちます。

## 初版の範囲と実機確認

- Wi-Fi切替・音声切替の項目は外部スクリプト呼出しの設定例です。Connect-Wifi.ps1 / Set-AudioOutput.ps1は未同梱のため、現時点ではこの2系統は動きません。既存の動くバッチ等があればRunで登録できます。
- StudioのEXE/バッチパスやREPLACE_...値は実際の環境へ変更してください。
- 実フォルダーの一覧は展開時に取得。全ディスク横断検索ではありません。大量ファイル/ネットワークフォルダーは初版では同期取得のため待ちが発生します。
- 作業画面に応じた候補表示・Web画面クリック・外部処理の結果変数受取・直接Unicodeキー送信は未実装です。
- カテゴリーアイコンは青、実フォルダーは黄。初版は簡易アイコンです。
- 検索解除時は現在の階層へ戻りますが、選択行の復元は未実装です。
- 画面位置とPageは保存します。サイズ調整とドラッグによる移動は未実装です。

Linux上のQtオフスクリーン環境で画面起動、全Page検索、選択一覧を確認。日付年跨ぎ・変数・階層検証など7テストがPASSしています。WindowsのEXEビルド、トレイ、ホットキー、フォーカス復帰、貼り付け、二重起動連携はWindows実機で未検証です。

最初の確認はメモ帳の入力欄で「昨日の日付」、次に「文章レビュー」、その後にappdata検索→Roamingをお試しください。終了はトレイから行います。

エラーは%LOCALAPPDATA%/FRBLaunch/error.log、位置等は同フォルダーのstate.iniに保存します。

## 参照

- Qt for Python: https://doc.qt.io/qtforpython-6/PySide6/QtWidgets/QSystemTrayIcon.html
- PyInstaller: https://pyinstaller.org/en/stable/

PySide6/QtにはLGPL等のライセンスがあります。再配布時は採用ライブラリのライセンス条件も確認してください。
