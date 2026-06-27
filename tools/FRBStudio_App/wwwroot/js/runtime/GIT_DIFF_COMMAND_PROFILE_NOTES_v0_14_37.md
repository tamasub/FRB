# v0.14.37 Git Diff Run / CommandProfile連携

`toolbar.executeButton.action = RunCommandProfile` から、選択行の Git Diff 実行設定を Program.cs の `/api/actions/command/run` へ渡す。

- Data JSONには任意の `commandLine` / `scriptPath` を持たせない
- Program.cs側の `git_diff_export` CommandProfileだけを実行する
- `output_path_display` は画面表示・照合用で、実行正本はProgram.cs側
- 静的ホスティングでは実行しない
