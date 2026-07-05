# ExpectedDef CompareStrategy Pattern Report v0.18.18

## 概要

`ExpectedDef` を mjs TestRunner 側の CompareStrategy 選択キーとして扱う初期実装を追加した。

`ExpectedDef` は比較処理そのものではなく、テストパターンData上の設計キーである。
Editor側では FieldGroupStrategy を選び、mjs側では CompareStrategy を選ぶ。

```text
TestPattern.expected_def_type
  ├─ Editor側: FieldGroupStrategy
  └─ mjs側: CompareStrategy
```

## 追加・変更内容

### 1. CompareStrategy Resolver 追加

追加ファイル:

```text
tests/responsibilities/responsibility_expected_compare_strategies.mjs
```

このファイルに以下を定義した。

- `CompareStrategies`
- `ExpectedDefCompareStrategyRegistry`
- `resolveExpectedDefStrategy()`
- `buildExpectedChecks()`

### 2. responsibility_expected_tests.mjs の責務整理

既存の `expected` 全項目 deepEqual 方式をやめ、`expected_def_type` を見て CompareStrategy を解決する方式へ変更した。

これにより、TestRunner本体が ExpectedDef ごとの巨大 if 文を持たず、Strategy Registry 経由で比較できる。

## ExpectedDef → CompareStrategy 初期対応表

| ExpectedDef | expected key | CompareStrategy |
|---|---|---|
| RuleExpectedDef | field_names | ArrayEquals |
| StateExpectedDef | row_ids | ArrayEquals |
| StateExpectedDef | indexes | ArrayEquals |
| CsvExpectedDef | field_names | ArrayEquals |
| CsvExpectedDef | has_bom | BooleanEquals |
| CsvExpectedDef | csv_text | CsvEquals |
| CsvExpectedDef | csv_without_bom | CsvEquals |
| CsvExpectedDef | csv_preview | CsvEquals |
| ErrorExpectedDef | field_names | ArrayEquals |
| ErrorExpectedDef | error_name | StringEquals |
| ErrorExpectedDef | error_message | StringEquals |
| ErrorExpectedDef | error_code | StringEquals |
| ErrorExpectedDef | path | StringEquals |
| ErrorExpectedDef | message | StringEquals |

## CompareStrategy 初期候補

初期実装として以下を登録した。

- ArrayEquals
- JsonEquals
- CsvEquals
- MarkdownEquals
- ImageEquals
- BooleanEquals
- StringEquals

`MarkdownEquals` / `ImageEquals` は将来拡張候補として登録した。
`ImageEquals` は v0.18.18 時点では未実装として明示的に fail する。

## 未対応時の扱い

未知の `expected_def_type` は暗黙スキップしない。
以下のように明示的なRunner Errorとして扱う。

```text
Unsupported expected_def_type: XxxExpectedDef
```

既知の ExpectedDef でも、対応表にない expected key が来た場合は明示的にエラーにする。

```text
Unsupported expected key for StateExpectedDef: xxx
```

## 確認結果

実行コマンド:

```text
node --check tests/responsibilities/responsibility_expected_compare_strategies.mjs
node --check tests/responsibilities/responsibility_expected_tests.mjs
node tests/responsibilities/responsibility_expected_tests.mjs
```

結果:

```text
5/6 passed
exit code: 1
```

`grid_column_build_visible_fields_basic` は、期待値側に意図的な `title zzz` が残っているため fail する。
これは CompareStrategy 導入後も差分検出が機能していることの確認になる。

Diff出力には、各checkへ以下が記録されるようになった。

- `type: compareStrategy`
- `expected_def_type`
- `expected_def_type_source`
- `compare_strategy`

## 判断ログ

- ExpectedDef は CompareStrategy そのものの名前にしない。
- ExpectedDef は Editor表示戦略キーと TestRunner比較戦略キーをつなぐ設計キーとして扱う。
- Editor側の FieldGroupStrategy と mjs側の CompareStrategy は別レイヤーとして分離する。
- Unknown ExpectedDef / Unknown expected key は暗黙スキップせず、明示エラーにする。

