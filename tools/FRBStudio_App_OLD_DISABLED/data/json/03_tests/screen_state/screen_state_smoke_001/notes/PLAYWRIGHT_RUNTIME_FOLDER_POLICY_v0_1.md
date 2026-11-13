# Playwright Runtime Folder Policy v0.1

## 目的

`screen_state` スモークテスト実行時に、FRBStudio_App root直下へ不要な生成フォルダーが増殖しないようにする。

## 方針

- `playwright-report/` は作成しない
- `test-results/` はroot直下に作成しない
- `test_results/` は使用しない
- `tests_screen_state/` は旧実験フォルダーとして使用しない
- Playwrightの一時実行結果は `tests/.runtime/playwright-output/` に隔離する
- Studioくんで見るActual/Diff正本は `data/json/03_tests/...` に保存する

## 対応

- rootに `playwright.config.ts` を追加
- reporterを `list` に固定し、HTMLレポート生成を止めた
- outputDirを `tests/.runtime/playwright-output` に変更
- `testInfo.attach()` による長い添付ファイル名生成をやめた
- `.gitignore` に生成フォルダーを追加
