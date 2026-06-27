# v0.14.38 Test Runner CommandProfile 対応レポート

## 対象

- incident: `studio_work_0063`
- phase: `v0.14.38-test-runner-command-profile`

## 実装概要

StudioくんのCommandProfile Runnerに `test_runner` profileを追加した。
Data JSONの実行プリセット行を選択し、Grid上部の `Test Run` ボタンから `/api/actions/command/run` を呼び出す。

## 追加した初期プリセット

| run_config_id | test_runner_id | run_mode | command_preview |
|---|---|---|---|
| `test_run_001_playwright_ui` | `playwright_ui` | `launch` | `npx playwright test --ui` |
| `test_run_002_incident_prompt_copy_action_static` | `incident_prompt_copy_action_static` | `wait` | `node --test tests/qa/static/incident_prompt_copy_action_viewdef_static.test.mjs` |

## 重要な設計判断

- `command_preview` は画面表示専用。
- Data JSONに任意 `commandLine` / `scriptPath` / `test_file` は持たせない。
- Program.cs側の `test_runner` CommandProfileと、`TestRunner.ps1` 内の許可済み `test_runner_id` だけを実行する。
- Playwright UI は起動しっぱなしになる可能性が高いため `launch`。
- Node標準テストは終了まで待って結果を返せるため `wait`。

## .cs関連の更新場所

ユーザー指定に合わせ、.cs関連は `Program.cs/` フォルダー内で更新した。

- `Program.cs/Program.cs`
- `Program.cs/FRBStudio.csproj`
- `Program.cs/appsettings.json`
- `Program.cs/tools/test/TestRunner.ps1`

## 確認

- JSON parse OK
- `node --check wwwroot/js/actions/action_registry.js` OK
- `dotnet` / PowerShell 実行環境がこのsandboxに無いため、C#ビルドとTestRunner実機実行は未実施
