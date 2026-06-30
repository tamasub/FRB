# v0.17.2 Git Diff Run / AppRoot Path Contract

`toolbar.executeButton.action = RunCommandProfile` から、選択行の Git Diff 実行設定を Program.cs の `/api/actions/command/run` へ渡す。

- Data JSONには任意の `commandLine` / `scriptPath` を持たせない
- Program.cs側の `git_diff_export` CommandProfileだけを実行する
- 実行パス正本は `Program.cs/appsettings.json` の CommandProfile とし、FRBStudio_App root からの相対パスで定義する
- `OutputPath` は `wwwroot/diff/DiffToJson.json` を標準とし、実出力は日時付き `DiffToJson_yyyyMMdd_HHmmss.json` になる
- Run Config明細には `output_path_display` を持たせない
- 出力先は基本情報メモまたは `/api/actions/command/profiles` / `/api/actions/command/diagnostics` 由来の参考表示で確認する
- `F:\FRB\...` や `F:\FRB_Diff\...` など、FRBStudio_Appより上位のPC固有絶対パスへ依存しない
- 静的ホスティングでは実行しない
