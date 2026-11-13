# FIELDGROUP TYPE DYNAMIC SWITCH / EXPECTEDDEF VIEWDEF REPORT v0.18.14

## Phase

`v0.18.14-fieldgroup-type-dynamic-switch-expecteddef-viewdef`

## 目的

ExpectedDefをViewDef本体へ直書きし続けるのではなく、`FieldGroupType` として `defs/config` 配下へ切り出し、ViewDef側では拡張ポイントだけを宣言する。

これにより、ViewDef本体を太らせず、`expected_def_type` などData側の値に応じて期待値表示パターンを動的に切り替えられるようにする。

## 実装方針

```text
ViewDef
  ↓
FieldGroupType Resolver
  ↓
展開済み fields
  ↓
既存 Renderer
```

Rendererは `RuleExpectedDef` / `StateExpectedDef` などの個別ExpectedDefを知らない。  
読み込み時にResolverがFieldGroupTypeを通常のfieldsへ展開し、既存Rendererへ渡す。

## 追加した概念

### FieldGroupType

複数のFieldを意味あるまとまりとして扱うViewDef拡張単位。

初期実装では以下を `defs/config/field_group_types_config_data_v0_1.json` へ追加した。

- `studio.ExpectedDef`
- `studio.RuleExpectedDef`
- `studio.StateExpectedDef`
- `studio.ErrorExpectedDef`
- `studio.InterfaceExpectedDef`
- `studio.EventExpectedDef`
- `studio.PerformanceExpectedDef`
- `studio.VisualEvidenceExpectedDef`
- `studio.CsvExpectedDef`

### 動的切替

`studio.ExpectedDef` は `expected_def_type` を見て、対象FieldGroupTypeを切り替える。

例:

```text
expected_def_type = RuleExpectedDef
  → expected.field_names / expected.has_bom / expected.csv_text など

expected_def_type = StateExpectedDef
  → expected.row_ids / expected.indexes
```

同じfieldが複数FieldGroupTypeに出る場合は、`visibleWhen.in` として統合する。

## 変更内容

- `state.js`
  - `DEFAULT_FIELD_GROUP_TYPES_FILE` と `fieldGroupRegistryCache` を追加。

- `field_types.js`
  - FieldGroupType定義の読み込みを追加。
  - `fieldGroupSources` / `field_group_sources` を追加。
  - FieldGroupTypeの静的展開・動的展開を追加。
  - `visibleWhen` 条件を付与してDetail表示時に動的に切り替えられるようにした。

- `field_controls.js`
  - `visibleWhen` 条件の評価を追加。
  - Detail表示時に現在行の値を見て表示対象Fieldを絞るようにした。

- `detail_save.js`
  - Detail通常Field / childArea側で行コンテキスト付きのField表示判定を使うようにした。

- `defs/config/field_group_types_config_data_v0_1.json`
  - FieldGroupType設定の正本ファイルを追加。

- `defs/qa/responsibilities/responsibility_expected_test_patterns_view_def_v0_1.json`
  - ExpectedDef個別項目の直書きをやめ、`studio.ExpectedDef` のFieldGroup宣言へ置換。

- `data/json/00_rules/frb_view_def_schema_v0_9.json`
  - `fieldGroup` / `fieldGroupType` / `fieldGroupSources` / `visibleWhen` をSchemaへ追加。

- `tests/qa/static/field_group_type_resolver_static.test.mjs`
  - FieldGroupType Resolverの静的テストを追加。

## 確認結果

OK:

```text
node --check wwwroot/js/core/state.js
node --check wwwroot/js/core/field_types.js
node --check wwwroot/js/renderers/field_controls.js
node --check wwwroot/js/runtime/detail_save.js
node tests/qa/static/field_group_type_resolver_static.test.mjs
node tests/responsibilities/responsibility_refactor_first_step_smoke.mjs
```

注意:

```text
node tests/responsibilities/run_responsibility_expected_tests.mjs
```

は、既存テストデータ側の期待値 `title zzz` と実Actual `title` の不一致により `grid_column_build_visible_fields_basic` が失敗した。  
今回のFieldGroupType実装起因ではなく、既存の赤データによる失敗として扱う。

## 判断ログ

- FieldGroupTypeはRenderer内部ではなく、ViewDef読み込み後・Renderer前の正規化段階で展開する。
- ExpectedDefは比較アルゴリズムではなく、期待値表示パターンのViewDef拡張として扱う。
- Static / Dynamic の両方を許容する。
- 今回はFieldType Strategy化までは行わない。Custom FieldType / lookup対応前の別インシデントで扱う。

