# FRB Studio — ViewDef 明示選択優先修正 026

## 目的

観点クロス集計 VirtualData ViewDef を選択して読み込んだ際に、対象JSON内の `view_def` に戻されてしまう問題を修正。

## 問題

`virtualData` が配列形式の ViewDef で、互換性判定が単体 object しか見ていなかったため、

- `qa_cross_quality_risk_view_def_v0_1.json`
- `qa_cross_check_risk_view_def_v0_1.json`
- `qa_cross_test_pattern_view_def_v0_1.json`
- `qa_cross_constraint_view_def_v0_1.json`

などを明示選択しても、互換なしと誤判定される場合がありました。
その結果、対象JSON内の `view_def` に自動補正され、元の Expected 一覧 ViewDef に戻るように見えていました。

## 修正内容

### 1. virtualData 配列の互換性判定に対応

`isVirtualDataCompatible()` を修正し、`virtualData` が配列の場合でも、
`mainGrid.dataPath` と一致する `targetPath` が1件でもあれば互換ありと判定します。

### 2. 画面定義JSONの明示選択を最優先

画面定義JSONコンボに値がある場合は、その ViewDef を最優先します。
明示選択した ViewDef が互換なしの場合でも、対象JSON内の `view_def` へ黙って戻さず、エラーで知らせます。

## 期待動作

対象JSON:

```text
qa_expected_checks_classified_v0_1.json
```

画面定義JSON:

```text
qa_cross_quality_risk_view_def_v0_1.json
qa_cross_check_risk_view_def_v0_1.json
qa_cross_test_pattern_view_def_v0_1.json
qa_cross_constraint_view_def_v0_1.json
```

を選択して「読み込み」すると、対象JSON内の `view_def` ではなく、選択したクロス集計 ViewDef が表示されます。

## 変更ファイル

```text
wwwroot/app.js
README_viewdef_explicit_selection_fix_026.md
```
