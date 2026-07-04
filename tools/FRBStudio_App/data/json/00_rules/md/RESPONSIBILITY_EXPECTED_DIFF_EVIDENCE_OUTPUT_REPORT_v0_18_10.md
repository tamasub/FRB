# Responsibility Expected Diff Evidence Output Report v0.18.10

- incident: `studio_work_0114`
- phase: `v0.18.10-responsibility-expected-diff-evidence-output`
- date: 2026-07-04

## 目的

`responsibility_expected` のテストパターン画面だけでは、実行後に何が観測され、Expected と Actual がどう一致したかを判断しにくい。

そのため、Node runner から Studioくんで読める Actual JSON と Diff JSON を出力し、Diff画面で `checks[]` を確認できるようにした。

## 追加した証跡

```text
data/json/03_tests/responsibilities/responsibility_expected_first_set/actual/responsibility_expected_first_set_actual_data_v0_1.json
data/json/03_tests/responsibilities/responsibility_expected_first_set/diff/responsibility_expected_first_set_diff_data_v0_1.json
```

## 追加したViewDef

```text
defs/qa/responsibility/responsibility_expected_actual_view_def_v0_1.json
defs/qa/responsibility/responsibility_expected_diff_view_def_v0_1.json
```

## 責務分離

```text
TestPattern JSON = 入力とExpectedを持つテストパターン定義
Actual JSON      = runnerが観測したActualのみ
Diff JSON        = ExpectedとActualの比較結果
Test Code        = 実行・観測・比較・証跡出力の仕掛け
```

Actual JSON には pass / failedCount / summary などの判定結果を置かない。
判定結果は diff_result_v0_1 の Diff JSON に置く。

## 確認結果

```text
node tests/responsibilities/run_responsibility_expected_tests.mjs

PASS grid_column_build_visible_fields_basic
PASS grid_column_build_empty_fields_safe
PASS search_filter_contains_case_insensitive
PASS search_filter_number_gte_preserves_indexes
PASS csv_export_visible_fields_with_key_and_escape
PASS csv_export_utf8_bom_option

responsibility_expected_tests: 6/6 passed
actual: data/json/03_tests/responsibilities/responsibility_expected_first_set/actual/responsibility_expected_first_set_actual_data_v0_1.json
diff:   data/json/03_tests/responsibilities/responsibility_expected_first_set/diff/responsibility_expected_first_set_diff_data_v0_1.json
```

## 未実施

ブラウザ実機でのDiff画面読込確認は未実施。
ただし、Diff JSONには `view_def` を付与済み。

```text
qa/responsibility/responsibility_expected_diff_view_def_v0_1.json
```
