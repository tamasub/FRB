# v0.18.8 Responsibility Expected Tests First Set Report

- work_item_id: `studio_work_0112`
- phase: `v0.18.8-responsibility-expected-tests-first-set`
- date: `2026-07-04`

## 目的

v0.18.7で追加した責務Interfaceに対して、まず小さく動くJSON駆動のExpectedテストを作る。

対象責務は以下の3つに限定した。

- `grid_column_build`
- `search_filter`
- `csv_export`

## 方針

- UI / DOM / Playwright / Visual Evidence は対象外。
- `studio_overlays` は直接テスト対象にしない。
- 既存APP構造や会社Copilotくん成果物を壊さず、責務Interfaceの入力→出力だけを確認する。
- Expectedはテストコードへ直書きしすぎず、まず `responsibility_expected_tests_first_set_data_v0_1.json` に寄せる。

## 追加ファイル

- `data/json/03_tests/responsibilities/responsibility_expected_tests_first_set_data_v0_1.json`
- `tests/responsibilities/run_responsibility_expected_tests.mjs`

## テストパターン

| test_pattern_id | responsibility_cd | expected_def_type |
| --- | --- | --- |
| grid_column_build_visible_fields_basic | grid_column_build | RuleExpectedDef |
| grid_column_build_empty_fields_safe | grid_column_build | ErrorExpectedDef |
| search_filter_contains_case_insensitive | search_filter | RuleExpectedDef |
| search_filter_number_gte_preserves_indexes | search_filter | StateExpectedDef |
| csv_export_visible_fields_with_key_and_escape | csv_export | RuleExpectedDef |
| csv_export_utf8_bom_option | csv_export | RuleExpectedDef |

## 実行方法

FRBStudio_App ルートで実行する。

```bash
node tests/responsibilities/run_responsibility_expected_tests.mjs
```

任意のテストデータJSONを渡す場合は、第一引数にパスを指定する。

```bash
node tests/responsibilities/run_responsibility_expected_tests.mjs data/json/03_tests/responsibilities/responsibility_expected_tests_first_set_data_v0_1.json
```

## 確認結果

```text
PASS grid_column_build_visible_fields_basic
PASS grid_column_build_empty_fields_safe
PASS search_filter_contains_case_insensitive
PASS search_filter_number_gte_preserves_indexes
PASS csv_export_visible_fields_with_key_and_escape
PASS csv_export_utf8_bom_option

responsibility_expected_tests: 6/6 passed
```

既存の v0.18.7 smoke test も継続確認した。

```text
responsibility_refactor_first_step_smoke: OK
```

## 判断ログ

今回の第一歩では、巨大なテスト基盤やスクショ証跡には進まない。
まずは小さく、責務Interface単位でExpectedを確認できる線を作る。

これにより、今後は責務を増やす前に、責務ごとのTestPattern / ExpectedDefを育てられる。
