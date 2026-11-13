# VALUE_VOCABULARY_REGISTRY_DIET_REPORT_v0_17_7

## 目的

common_enums と value_sets が別系統で肥大化する前に、値候補マスタの論理スキーマを **Value Vocabulary Registry Schema** へ寄せる。

## 今回の対応

- `frb_coding_constraints_data_v0_3.json` に constitution_25 を追加。
- `common_enums_v0_1.json` に `logical_schema_version`, `registry_scope=core`, 統一契約を追加。
- `company_value_sets.json` を `registry_scope=overlay` の Value Vocabulary Registry 実体へ寄せた。
- `company_value_sets.json` の `caption` を `name` へ寄せ、各 enum に `enum_ref` を付与。
- `valueVocabularySources` を ViewDef の新しい論理名として扱えるようにした。
- `enumRef / valueSet / valueVocabularyRef` を同じ options 解決系へ入れる方針へ寄せた。
- 配列値のGrid表示で `field.options` がある場合、`["PM"]` ではなく `プロジェクトマネージャ` のような表示名を出せるようにした。

## 残した互換

- `enumRef` は Core語彙参照の互換名として残す。
- `valueSet` は Overlay語彙参照の互換名として残す。
- `caption` は読み取り互換aliasとしてRuntime側で許容する。
- `value_set_files` は manifest の互換フィールド名として残す。

## 合言葉

```text
スキーマは一つ。
レジストリはスコープ別。
Coreは構造を知る。
Overlayは語彙を持つ。
Pluginは語彙を触る。
```
