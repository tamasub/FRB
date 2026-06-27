# v0.14.38 Test Run / CommandProfile連携メモ

Studioくんからテストコマンドを直接任意commandLineとして実行するのではなく、Program.cs側の許可済み `test_runner` CommandProfile と `TestRunner.ps1` 内の許可済み `test_runner_id` だけを実行する。

## 実行できる初期プリセット

| test_runner_id | run_mode | command_preview |
|---|---|---|
| `playwright_ui` | `launch` | `npx playwright test --ui` |
| `incident_prompt_copy_action_static` | `wait` | `node --test tests/qa/static/incident_prompt_copy_action_viewdef_static.test.mjs` |

## 責務分離

```text
Data JSON:
  人間が選ぶプリセット
  test_runner_id / run_mode / command_preview

Program.cs:
  許可済みCommandProfileの解決
  TestRunner.ps1の実体パス管理
  run_modeごとのlaunch/wait制御
  timeout / stdout / stderr / exit_code返却

TestRunner.ps1:
  許可済みtest_runner_idだけを分岐実行
```

## セキュリティ方針

Data JSONには任意の `commandLine` / `scriptPath` / `test_file` を持たせない。
`command_preview` は画面表示専用であり、実行正本ではない。
