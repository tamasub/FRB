# TEST_FOLDER_ARCHIVE_RUNTIME_POLICY_NOTES_v0_1

導入: v0.14.15-test-folder-archive-runtime-policy

## 目的

Test Evidence の正本、テストコード、一時生成物、archive退避の置き場所を分離する。

```text
data/json/03_tests/ = Studioくんで見るテスト証跡の正本
tests/              = テストを実行するコード
tests/.runtime/     = Playwright / Node test などの一時生成物
_archive/           = activeから外した旧データ・不要データの退避先
```

## 標準構成

```text
data/json/03_tests/{domain}/{suite_id}/
├─ test_patterns/
├─ expected/
├─ actual/
├─ diff/
├─ relations/
├─ summary/
└─ notes/
```

## テストコード共通化方針

テストコードは、コード実行言語ごとに1つの共通ランナーへ寄せることを基本とする。

- Node.js系: 共通 `.mjs` ランナーへ寄せる
- Playwright系: 共通 `.spec.ts` ランナーへ寄せる
- 新規テストケースは、まず Test Pattern JSON / Expected JSON の追加で対応する
- 過剰共通化で将来苦しくなる場合は人間へ相談する

## ZIP返却時の除外対象

```text
node_modules/
playwright-report/
test-results/
test_results/
tests/.runtime/
tests_screen_state/
```

## cleanup

runtime生成物は以下で掃除できる。

```powershell
.	ests	ools\cleanup_runtime_artifacts.ps1
```

このスクリプトは再生成可能な一時生成物のみを削除し、`data/json/03_tests/**` の証跡正本は削除しない。
