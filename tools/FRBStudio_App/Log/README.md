# FRB Studio Log

PowerShellバッチ処理の共通ログ出力先です。

- 既定ファイル名: `Log_yyyyMMdd.log`
- 既定出力先: `FRBStudio_App/Log/`
- 共通部品: `tools/common/StudioLog.ps1`
- 初期対象: `tools/test/TestRunner.ps1`, `tools/git/Export-DiffToJson.ps1`

ログファイル本体は `.gitignore` の `*.log` によりGit管理対象外です。
新しいPowerShellバッチ処理を追加する場合は、個別ログ実装を作らず `tools/common/StudioLog.ps1` をdot-sourceして使用してください。
