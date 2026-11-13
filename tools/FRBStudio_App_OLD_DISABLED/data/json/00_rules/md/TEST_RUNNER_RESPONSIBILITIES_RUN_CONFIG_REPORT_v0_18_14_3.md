# Test Runner Responsibilities Run Config Report v0.18.14.3

## 目的

Studio Test Runner Run Config から responsibilities 系 mjs を実行できるようにする。

## 対応

- `tests/responsibilities/run_responsibility_expected_tests.mjs` を `tests/responsibilities/responsibility_expected_tests.mjs` へ名称寄せ
- TestRunner.ps1 の許可済み `TestRunnerId` に以下を追加
  - `responsibility_expected_tests`
  - `responsibility_refactor_first_step_smoke`
- Program.cs の CommandProfile 許可リストに同IDを追加
- `test_runner_run_config_data_v0_1.json` に Run Config 2件を追加

## 命名方針

`tests/responsibilities/` 配下の mjs は、責務領域のテストであることが一覧から分かるように `responsibility_` 先頭へ寄せる。

## 廃止対象

次の旧ファイルは互換目的で一時的に残っていてもよいが、active参照からは外す。

```text
tests/responsibilities/run_responsibility_expected_tests.mjs
```

## 確認

```text
node --check tests/responsibilities/responsibility_expected_tests.mjs
node tests/responsibilities/responsibility_refactor_first_step_smoke.mjs
node tests/responsibilities/responsibility_expected_tests.mjs
```

`responsibility_expected_tests.mjs` は既知の赤データ `title zzz` により 5/6。TestRunnerでは起動成功・テスト失敗として扱う。
