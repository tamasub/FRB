# ExpectedDef CompareStrategy Pattern Report v0.18.18

## 概要

`ExpectedDef` を mjs 側の比較戦略キーとして扱えるようにし、`responsibility_expected_tests.mjs` の比較ロジックを Strategy Pattern へ分離した。

## 対応方針

`ExpectedDef` はテストパターン設計データ上のキーであり、2つの責務を持つ。

- Editor側: FieldGroupStrategy を選ぶキー
- mjs TestRunner側: CompareStrategy を選ぶキー

今回の対応では、mjs側に限定して次の構造へ整理した。

```text
TestPattern.expected_def_type
        ↓
CompareStrategy Resolver
        ↓
ArrayEquals / ValueEquals / CsvEquals / JsonEquals / MarkdownEquals / ImageEquals
        ↓
strategy.compare(...)
```

## 更新ファイル

```text
tests/responsibilities/lib/responsibility_expected_compare_strategies.mjs
tests/responsibilities/lib/responsibility_datetime_utils.mjs
tests/responsibilities/responsibility_expected_tests.mjs
data/json/03_tests/responsibilities/responsibility_expected_first_set/actual/responsibility_expected_first_set_actual_data_v0_1.json
data/json/03_tests/responsibilities/responsibility_expected_first_set/diff/responsibility_expected_first_set_diff_data_v0_1.json
data/json/00_rules/md/EXPECTEDDEF_COMPARE_STRATEGY_PATTERN_REPORT_v0_18_18.md
data/json/01_main/studio_work_incident_data_v0_140_expecteddef_compare_strategy_pattern_jst_done.json
```

## 設計メモ

### CompareStrategy部品

比較処理は `tests/responsibilities/lib/responsibility_expected_compare_strategies.mjs` へ分離した。

`lib` 配下に置く理由は、このファイルが直接実行するRunnerではなく、Runnerから呼ばれる部品だからである。

### 共通メソッド名

各Strategyは共通で `compare(...)` メソッドを持つ。

```text
strategy.compare({ expected, actual, key })
```

この `compare` はJavaScript標準コマンドではなく、StudioくんのCompareStrategy共通メソッドである。

### JST時刻出力

`new Date().toISOString()` はUTCの `Z` 表記になるため、9:34に実行しても `00:34Z` のように保存される。

テスト証跡は人間が読むData JSONであるため、`tests/responsibilities/lib/responsibility_datetime_utils.mjs` を追加し、Responsibility Expected runner の `generated_at / observed_at` は次の形式へ統一した。

```text
YYYY-MM-DDTHH:mm:ss.SSS+09:00
```

例:

```text
2026-07-05T09:37:30.273+09:00
```

## CompareStrategy候補

```text
ArrayEquals
ValueEquals
JsonEquals
CsvEquals
MarkdownEquals
ImageEquals
BooleanEquals
```

現時点では `ImageEquals` は未実装で、呼ばれた場合は明示的にNGを返す。

## 確認結果

```text
node --check tests/responsibilities/lib/responsibility_expected_compare_strategies.mjs
node --check tests/responsibilities/lib/responsibility_datetime_utils.mjs
node --check tests/responsibilities/responsibility_expected_tests.mjs
```

OK。

```text
node tests/responsibilities/responsibility_expected_tests.mjs
```

結果:

```text
5/6 passed
exit code: 1
```

`grid_column_build_visible_fields_basic` は、期待値側が意図的に `title zzz` になっているためFAILする。これは `ArrayEquals` により差分検出できている状態であり、今回のStrategy Patternの動作確認として妥当である。

生成された `actual/diff` の `generated_at` はJST `+09:00` 表記になったことを確認済み。

## 判断ログ

- CompareStrategyは実行Runnerではなく部品なので `tests/responsibilities/lib/` 配下へ配置する。
- Runnerは `responsibility_expected_tests.mjs` のまま維持する。
- `ExpectedDef` はEditor表示戦略キーであると同時に、mjs側比較戦略キーとして扱う。
- UTC `Z` 時刻は人間が見る証跡では混乱を生むため、少なくともResponsibility Expected runnerの出力はJST `+09:00` へ寄せる。
- 既存の過去証跡JSONは履歴として残し、今回再生成したactual/diffのみ更新する。


### ValueEquals追加メモ（2026-08-29）

`ScalarExpectedDef` の `expected.value` はJSON構造ではなく単一Scalar値を比較するため、
CompareStrategyを `JsonEquals` から `ValueEquals` へ変更した。

```text
ScalarExpectedDef
  ↓
expected.value
  ↓
ValueEquals
```

`ValueEquals` は `string / number / boolean / null` を対象に型を保った単純一致で比較し、
object / array は対象外とする。単一値を「JSONとして比較する」意味のズレを避けるための整理である。
