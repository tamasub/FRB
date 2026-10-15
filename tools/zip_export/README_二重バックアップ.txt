FRB / FRB_docsExcel 二重ZIPバックアップ (2026-10-15)
=================================================

【使い方】
1. この zip_export フォルダーを今の F:\FRB\tools\zip_export\ に上書き配置。
   （既存の Export-FrbZip.log は残すこと。差分 ZIP にはログを含めていません）
2. FRB Studio、Excel、JSON編集など、対象ファイルを編集中なら保存して閉じる。
3. Export-FrbZip.bat をダブルクリック。

【通常の出力】
F:\FRB_backups\FRB_backup_yyyyMMdd_HHmmss_fff.zip
F:\FRB_backups\FRB_docsExcel_backup_yyyyMMdd_HHmmss_fff.zip

D: ドライブが使える場合には、同名の2 ZIPを D:\FRB_backups\ にもコピーします。
D: ドライブが無い場合は「D: 未接続、スキップ」と表示して正常終了します。
コピー先 D: に同名ファイルがあれば上書きせずに警告します。

ZIP はそれぞれ個別。ZIP内は元の各フォルダー直下からの相対パスです。
既存の exclude_patterns.txt の内容は一切変更していません。
対象から外れる例: .git, bin, obj, node_modules, Mermaid実体, Studio内のzip 等。
（F:\FRB_docsExcel にも共通の名前除外パターンを適用します。）

【安全策】
・ローカルZIPは「.partial」に一旦作り、内容を再読み取りして確認後、正式名に確定。
・Dへのコピーも一時ファイルを使い、SHA256が一致した場合だけ正式名にします。
・D未接続時でもFへのZIP作成は続行。
・対象フォルダーが見つからない／読み取りに失敗した場合はエラーを表示。
・ログは以前と同じ Export-FrbZip.log に追記（ZIPにログを含めない）。
・隠しファイルも除外対象以外は対象。リンク先のフォルダーは安全のため走査しません。

【事前確認（作成せずに一覧だけ表示）】
PowerShell で F:\FRB\tools\zip_export\ に移動し、次を実行:
  powershell -NoProfile -ExecutionPolicy Bypass -File .\Export-FrbZip.ps1 -DryRun

【旧オプションとの互換性】
  -SourcePath "F:\FRB"             1つだけバックアップ
  -SourcePaths "F:\FRB","F:\FRB_docsExcel"    複数対象
  -OutputDir "F:\FRB_backups"
  -MirrorDir "D:\FRB_backups"
  -AdditionalExclude "任意の除外パターン"

【注意】
・F: 保存先とD: 保存先は、別々の物理ディスクであることを確認してください。
・F: が消失した場合に備えるにはD:側を常に定期的に接続し、結果画面の「D: コピー OK」を確認。
・FRB Studioなどに未保存データがある場合はZIP化前に保存して閉じてください。
・ZIPは変更時点の静的なコピーではありません。コピー中に編集すると不整合になることがあります。
・本ツールは実機のWindows PowerShell上での操作確認は未実施です。
