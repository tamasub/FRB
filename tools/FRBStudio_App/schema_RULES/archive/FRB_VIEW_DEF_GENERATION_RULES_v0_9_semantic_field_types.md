# FRB ViewDef Generation Rules v0.9 — Semantic FieldTypes

## 目的

大量のExpected定義やRelation定義を作る前に、項目の意味単位でFieldTypeを共通化する。

## 基本方針

- `fieldType` は項目の意味を表す。
- 選択肢あり項目は `cd/name` で、素データはCD保存・画面は名称表示する。
- 選択肢なし項目も `caption / baseType / grid / edit / search / readonly` を共通定義できる。
- ViewDef側は `field` と `fieldType` を基本とし、必要な差分だけ上書きする。

## 例

```json
{
  "field": "customer_name",
  "fieldType": "business.customer_name"
}
```

幅だけ変える場合。

```json
{
  "field": "customer_name",
  "fieldType": "business.customer_name",
  "grid": { "width": 240 }
}
```

## Namespace

- `qa.*` : テスト観点分類
- `relation.*` : Relation台帳・承認項目
- `business.*` : 業務サンプル項目
- `core.*` : 汎用メタ項目

## マージ規則

1. Common FieldType を読み込む。
2. `baseType` を内部の `type` として扱う。
3. ViewDef側の個別指定を深いマージで上書きする。
4. `options` が文字列配列の場合は旧方式、`{cd,name}` 配列の場合は cd保存/name表示とする。
