FRB Launch - メール宛先候補 CSV全件取込（2026-10-16）

■ 適用手順
1. FRB Launch / Studioくんを終了する。
2. この ZIP を F:\FRB\tools\ に上書き展開する。
   重要：FRB_Launch/ と FRBStudio_App/ の2つのディレクトリーが配置されます。
   設定JSON(config/*.json)は一切含めていません。
3. F:\FRB\tools\apply_email_csv_viewdef.bat を実行する。
   ・現在のStudio側/Launch側 ViewDef に csvImport 定義だけを追記します。
   ・現在の画面カスタマイズを残します。
   ・変更前のViewDefは *.csvimport_backup_YYYYMMDD_HHMMSS.bak に保存します。
   ・何回実行しても同じ設定ならスキップします。
4. F:\FRB\tools\FRBStudio_App\cmd_compile_NativeShell.bat を実行する。
5. F:\FRB\tools\FRB_Launch\build_windows.bat を実行する。

■ 使い方
1. FRB Launch → 設定（Studioくん）→「選択候補」を開く。
2. 「CSV取込」を押して CSV を選ぶ。
3. 「既存N件をすべて削除し、CSVのM件を取り込みます」と警告表示。
   キャンセルなら元データはそのまま。
4. OKすると選択候補 Grid の配列だけ全件置換（まだ親画面へ未反映）。
5. 必ず「親画面へ反映」→ 親画面の「保存」を押す。
6. 新しい候補の「グループID」は空欄です。Studioくんで手動設定してから活用してください。

■ CSV形式（UTF-8 BOMつき/Shift-JIS/UTF-16）
最も簡単な形式：
    氏名,メールアドレス
    田中太郎,tanaka@example.com
    佐藤花子,sato@example.com

対応する主な別名：
    title / Name / 氏名 / 名前 / 表示名 → タイトル
    value / Email / E-mail Address / E-mail 1 - Value / メールアドレス / 値 → 値
    description / 説明 / 備考 / 部署 → 説明

・既存 launch_choices 配列の全候補が入替対象。他の items/pages は変更しません。
・候補ID(import_mail_000001...)、表示順(10,20...)は自動採番。
・有効=true、グループID=""、説明未指定ならメールアドレスを設定。
・空メール列、ヘッダー不足、不正引用符、0件、10MB超、10000件超は事前拒否します。
・CSVのgroup_id列は意図的に読み込みません。
・別GridにCSVボタンは出ず、ViewDefでcsvImportを宣言した選択候補だけに表示します。
・更新したFRB Launchでは、候補が未割当でも設定ロードを拒否しません。

■ チェック
新規CSVインポーターの Node.jsテスト9件 PASS。
Chromiumで無効CSV、キャンセル、取込成功、再描画、未反映状態を確認済み。
Studio静的テストは527件中518件PASS（元資材でも9件失敗）。
FRB Launch全体テストは173件中PySide6未導入等の既存エラー・失敗あり（元資材と同数）。
Windows実機の操作・ビルドは未検証。
