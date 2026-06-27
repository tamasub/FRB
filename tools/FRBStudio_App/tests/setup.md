# Screen State Test Setup

## 初回セットアップ

```powershell
cd F:\FRB\tools\FRBStudio_App
npm init playwright@latest
```

## 実行

Studioくんを `http://localhost:5055/` で起動してから実行する。

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

旧 `tests_screen_state/` は独立Playwrightプロジェクト実験時代の名残。今後は `tests/screen_state/` を正本とする。
