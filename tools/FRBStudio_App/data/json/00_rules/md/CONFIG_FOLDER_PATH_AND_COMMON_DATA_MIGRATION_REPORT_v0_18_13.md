# Configフォルダーパス設計 / 共通設定データ移行レポート v0.18.13

## 対応フェーズ

- phase: `v0.18.13-config-folder-path-and-common-data-migration`

## 結論

`common_enums_v0_1.json` は Rules ではなく、Studio Core の値語彙Configとして扱う。

そのため正本位置を以下に整理した。

```text
data/json/config/common_enums_v0_1.json
```

Runtimeから読むAPI相対パスは以下。

```text
config/common_enums_v0_1.json
```

## フォルダー責務

```text
defs/config/
  ViewDefを拡張するStudio Core設定
  例: FieldGroupType / FieldType / Renderer Registry

data/json/config/
  RuntimeがData JSONとして読む共通設定・値語彙
  例: common_enums_v0_1.json

data/json/00_rules/
  ルール本文・制約・レビュー対象のData JSON
  例: Foundation Rules / Coding Constraints
```

## 旧パス互換

旧指定は互換AliasとしてRuntimeで新パスへ寄せる。

```text
00_rules/common_enums_v0_1.json
  -> config/common_enums_v0_1.json
```

`data/json/00_rules/...` や `json/00_rules/...` と書かれていた場合も、API相対パスへ正規化した後に同じAliasを適用する。

## 更新内容

- `wwwroot/js/core/state.js`
  - `DEFAULT_COMMON_ENUMS_FILE` を `config/common_enums_v0_1.json` へ変更。
- `wwwroot/js/core/field_types.js`
  - `normalizeDataJsonApiPath` に旧 `00_rules/common_enums_v0_1.json` 互換Aliasを追加。
- `defs/rules/context_refs_sample_view_def_v0_1.json`
  - `commonEnumSources` を `config/common_enums_v0_1.json` へ更新。
- `data/json/config/common_enums_v0_1.json`
  - 正本パス・API相対パス・旧パスAlias・移行メモを追加。
- `defs/config/config_folder_policy_v0_1.json`
  - Configフォルダー責務の方針ファイルを追加。
- `data/json/00_rules/studio-overlay-manifest_rules_data_v0_1.json`
  - Core標準ValueSetの参照先を `data/json/config/common_enums_v0_1.json` へ更新。

## 対象外

FieldGroupType本体、ExpectedDef表示生成、FieldType Strategy Pattern本体は未対応。

このフェーズでは、後続の FieldGroupType / FieldType Strategy 化の前提となるConfig置き場と旧パス互換だけを整えた。
