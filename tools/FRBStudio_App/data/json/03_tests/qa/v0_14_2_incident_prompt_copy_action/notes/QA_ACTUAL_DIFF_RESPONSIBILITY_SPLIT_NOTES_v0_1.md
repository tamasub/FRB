# QA Actual / Diff Responsibility Split Notes v0.1

## 目的

TP-IPC-001 の出力を、actual.json と diff.json に責務分離する。

## 責務

- `actual/TP-IPC-001.actual.json`
  - 実行によって観測した値のみを保持する。
  - `expected` / `pass` / `resultLabel` / `summary` は持たない。

- `diff/TP-IPC-001.diff.json`
  - Expected JSON と Actual Observation を比較した結果を保持する。
  - `expected` / `actual` / `pass` / `resultLabel` / `summary` / `failedCount` を持つ。

## テストコードの役割

テストコードは Expected JSON を正本として読み込み、Actual Observation を作成し、Diff Result を生成する仕掛けに留める。

## node --test の成否

`diff.failedCount` を正として判定する。

## Legacy folder cleanup

`tests_screen_state/` は旧独立Playwrightプロジェクト実験時代の名残である。
空フォルダーが存在する場合のみ、screen_state smoke test 実行時に削除する。
内容がある場合は削除しない。
