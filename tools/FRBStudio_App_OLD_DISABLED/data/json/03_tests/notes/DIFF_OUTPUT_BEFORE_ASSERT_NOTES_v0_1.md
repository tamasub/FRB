# DIFF_OUTPUT_BEFORE_ASSERT_NOTES_v0_1

## 目的

`node --test` が Expected 差分により fail する場合でも、Studioくんで原因確認できるように、
`actual.json` と `diff.json` を必ず先に出力してから fail 判定する。

## 対象

- `tests/qa/static/incident_prompt_copy_action_viewdef_static.test.mjs`

## 方針

- `actual.json` は観測値のみを保持する。
- `diff.json` は expected / actual / pass / summary を保持する。
- Expected差分がある場合、テストは fail してよい。
- ただし、fail の前に `diff.json` が出力済みであることを保証する。

## 出力確認

テスト実行時に標準出力へ以下を表示する。

```text
[FRBStudio] Actual Observation JSON written: ...
[FRBStudio] Diff Result JSON written: ...
```

## 重要

Diffは人間が違和感を確認するための正本である。
そのため、テストが fail しても Diff JSON は残す。
