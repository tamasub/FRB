# v0.14.37 Git Diff Run / CommandProfile連携メモ

Studioくんから `Export-DiffToJson.ps1` を直接任意コマンドとして実行するのではなく、Program.cs側の許可済み `CommandProfile` として `git_diff_export` だけを実行する。

## 責務分離

```text
Data JSON:
  Mode / From / To / Unified / MaxPatchChars / NoPatch / output_path_display

Program.cs:
  scriptPath / OutputPath / workingDirectory / allowed mode / timeout / 引数検証

Export-DiffToJson.ps1:
  Git DiffをDiffToJson.jsonへ変換する実体
```

## OutputPath方針

`DiffToJson.json` をGit管理配下へ出力すると、差分出力ファイル自身がGit差分になり、差分が差分を生む再帰事故が起きる。

そのため、初期値は Git管理外の以下とする。

```text
F:\FRB_Diff\DiffToJson.json
```

Data JSONにも `output_path_display` として保持するが、実行時の正本はProgram.cs側のCommandProfile設定とし、不一致時は実行を拒否する。
