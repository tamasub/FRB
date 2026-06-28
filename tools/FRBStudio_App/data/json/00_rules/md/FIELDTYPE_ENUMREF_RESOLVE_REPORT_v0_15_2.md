# FIELDTYPE_ENUMREF_RESOLVE_REPORT_v0_15_2

## Phase

v0.15.2-fieldtype-enumref-resolve

## 実施内容

FieldType が `enumRef` を持てるようにし、`baseType=select` / `type=select` / radio系 control の場合に、`common_enums_v0_1.json` の `items` を `options` として解決するRuntimeを追加した。

## 設計方針

- Enum: 値候補そのものの正本
- FieldType: 画面項目としての使い方
- ViewDef: 配置と上書き
- Data: 実値

`enumRef` と `options` が両方ある場合は、`enumRef` 側を正本として扱う。
既存 `options` は互換用・キャッシュ・展開結果として残せるが、Runtime表示ではEnumから取得した選択肢を優先する。

## 実装概要

- `wwwroot/js/core/state.js`
  - `DEFAULT_COMMON_ENUMS_FILE`
  - `enumRegistryCache`
- `wwwroot/js/core/field_types.js`
  - common enum source 読み込み
  - `common_enums_v0_1.json` の namespace / enum / items 正規化
  - `enumRef` 解決
  - `enumRef + options` 併用時の enumRef 優先
  - Enum未存在時の警告と互換継続
- `defs/common/common_types_v0_1.json`
  - `qa.risk` に `enumRef=qa.risk_level` を追加
  - `qa.risk_enumref_only_sample` を追加
- `data/json/00_rules/common_enums_v0_1.json`
  - Runtime方針を v0.15.2 の解決済み方針へ更新

## 互換方針

既存 `options` 直書きFieldTypeは従来どおり動作する。
`enumRef` を持つFieldTypeだけがEnum解決対象になる。
Enumが見つからない場合は `console.warn` で警告し、既存 `options` があれば表示を継続する。

## 確認結果

- enumRefのみFieldType: `qa.risk_enumref_only_sample` → `qa.risk_level` itemsをoptionsとして解決
- enumRef+options併用FieldType: `qa.risk` → enumRef側を優先し、`_options_source=enumRef` を付与
- 既存options直書きFieldType: 従来互換を維持
- Enum未存在: 警告扱いで既存optionsがあれば互換継続

## 後続へ残すこと

既存optionsの全面棚卸し・enumRef移行は v0.15.4 側で扱う。
