# SUBGRID_SINGLE_LINE_TEST_PATTERN_VIEWDEF_REPORT v0.18.11

## 目的

サブグリッド一覧で object / json / 長文が textarea として低身長セルに押し込まれ、内容が読めない問題を解消する。

## 対応方針

- サブグリッド一覧の textarea を廃止する。
- object / json / 長文は1行表示にする。
- 折り返しはしない。
- 長い値は右端で clip する。
- 本格編集は既存の Preview Edit に寄せる。
- 右側に余白がある場合、longText/json列へ余白を寄せる。

## 追加したViewDef方針

`responsibility_expected_test_patterns_view_def_v0_1.json` で、以下の主要フィールドをグリッド表示へ追加した。

- `input.view_def.fields`
- `input.rows`
- `input.criteria`
- `input.base_fields`
- `input.all_fields`
- `expected.field_names`
- `expected.row_ids`
- `expected.indexes`
- `expected.csv_without_bom`

これにより、TestPatternを「実行するためのデータ」ではなく「レビューできる設計書」として読む入口を増やした。

## 検証メモ

`node tests/responsibilities/run_responsibility_expected_tests.mjs` は 5/6。

失敗は、ユーザーが赤表示確認用に `grid_column_build_visible_fields_basic` の期待値を `title zzz` に変更しているためであり、今回のUI/ViewDef修正とは別要因。
