# README v0.8 — Common FieldTypes

v0.8では、チェック観点分類をスモールスタートで共通Type化した。

## 追加ファイル

- `defs/common/common_types_v0_1.json`
- `schema_RULES/FRB_VIEW_DEF_GENERATION_RULES_v0_8_common_field_types.md`
- `schema_RULES/README_viewdef_rules_v0_8.md`

## 追加サンプル

- `data/json/qa_test_patterns_sample_v0_1.json`
- `defs/qa_test_patterns_sample_view_def_v0_1.json`
- `data/json/qa_expected_checks_sample_v0_1.json`
- `defs/qa_expected_checks_sample_view_def_v0_1.json`

## 確認ポイント

1. サンプルデータを読み込む
2. `feature_area_cd` / `quality_axis_cd` / `risk_cd` が日本語ラベルで表示される
3. 編集画面ではコンボになる
4. 保存される値は `cd` のまま
5. 既存の文字列 `options` はそのまま動く
