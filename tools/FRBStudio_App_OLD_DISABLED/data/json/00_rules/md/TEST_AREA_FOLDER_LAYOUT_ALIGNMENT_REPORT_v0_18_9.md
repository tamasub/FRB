# Test Area Folder Layout Alignment Report v0.18.9

## 概要

Test Evidence Rules v0.2 で整理した `test_area / suite_id / artifact_kind` の配置方針を、責務 Expected 初期セットへ小さく適用した。

## 標準配置

```text
data/json/03_tests/responsibilities/responsibility_expected_first_set/
├─ test_patterns/
├─ expected/
├─ actual/
├─ diff/
├─ relations/
├─ summary/
└─ notes/
```

## 更新内容

- Node runner の既定読込パスを標準配置へ変更。
- 旧MVP直置きパス指定時は、新標準パスへfallbackする互換を追加。
- `responsibility_expected_tests_first_set_data_v0_1.json` に `test_area / suite_id / artifact_kind / canonical_path` を追加。
- Data JSON 内の `view_def` パスを Windows バックスラッシュから `/` 区切りへ変更。
- ViewDef の Header に test_area / suite_id / artifact_kind / canonical_path を表示できるように追加。
- expected / actual / diff / relations / summary / notes の標準フォルダーを追加。
- `qa` / `screen_state` 配下は移動しない。

## 確認結果

```text
node tests/responsibilities/run_responsibility_expected_tests.mjs
```

結果:

```text
PASS grid_column_build_visible_fields_basic
PASS grid_column_build_empty_fields_safe
PASS search_filter_contains_case_insensitive
PASS search_filter_number_gte_preserves_indexes
PASS csv_export_visible_fields_with_key_and_escape
PASS csv_export_utf8_bom_option

responsibility_expected_tests: 6/6 passed
```

旧MVPパス指定時のfallbackも確認済み。

```text
node tests/responsibilities/run_responsibility_expected_tests.mjs data/json/03_tests/responsibilities/responsibility_expected_tests_first_set_data_v0_1.json
```

## 未実施

- ブラウザ実機での ViewDef 読込確認は未実施。
- Actual / Diff の本格保存は未実施。
- `qa` / `screen_state` 配下の移行は未実施。
