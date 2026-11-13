# Screen State Test Setup

## 実行前提

Studioくんを `http://localhost:5055/` で起動してから実行する。

## 実行

```powershell
cd F:\FRB\tools\FRBStudio_App
npx playwright test tests/screen_state/ncjs-screen-state-compare.checks.spec.ts
```

## 出力先

`screen_state_smoke_001` のActual/Diffは、テストパターンJSONの `outputActualFile` / `outputDiffFile` を正とする。

```text
data/json/03_tests/screen_state/screen_state_smoke_001/actual/screen_state_smoke_001.actual.json
data/json/03_tests/screen_state/screen_state_smoke_001/diff/screen_state_smoke_001.diff.json
```

## 生成フォルダーの方針

Playwright の一時実行結果は root 直下に出さない。

```text
OK: tests/.runtime/playwright-output/
NG: playwright-report/
NG: test-results/
NG: test_results/
NG: tests_screen_state/
```

`tests_screen_state/` は旧独立Playwrightプロジェクト実験時代の名残。今後は `tests/screen_state/` を正本とする。

## 既に生えた古いフォルダーの削除

Windowsで既存フォルダーにZIPを上書き展開した場合、ZIPに含まれない古いフォルダーは自動削除されない。
一度だけ下記を実行して掃除する。

```powershell
Remove-Item -Recurse -Force .\playwright-report, .\test-results, .\test_results, .\tests_screen_state -ErrorAction SilentlyContinue
```
