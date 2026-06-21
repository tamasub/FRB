# FRB ViewDef Generation Rules v0.10 — FieldType Caption Required

## 目的

Common FieldTypes によって ViewDef を小さくしつつ、元ViewDefを人間が読める状態に保つ。

## 基本方針

- `fieldType` を使う field でも、ViewDef側に `caption` を明示する。
- ViewDef側の `caption` は、その画面における表示名として最優先する。
- Common FieldType側の `caption` は fallback / 標準名として扱う。
- `caption` がない場合でも実行時は Common 側 caption に fallback するが、生成ルール上は警告対象とする。

## 推奨形

```json
{
  "field": "quality_axis_cd",
  "caption": "品質観点",
  "fieldType": "qa.quality_axis"
}
```

## 非推奨形

```json
{
  "field": "quality_axis_cd",
  "fieldType": "qa.quality_axis"
}
```

## 解決優先順位

```text
ViewDef.caption
  ↓ 最優先
Common FieldType.caption
  ↓ fallback
field名
  ↓ 最後のfallback
```

## なぜ caption を残すか

`fieldType` によって `type / options / grid / edit / search` は共通化できる。
一方で、`caption` は元ViewDefを読む人間にとっての最低限の意味ラベルである。

そのため、共通化しても `field / caption / fieldType` の3点は残す。

```text
field      = データ上のキー
caption    = 人間が読む意味ラベル
fieldType  = 共通定義への参照
```

## ViewDef Markdown レポート

`ViewDef Markdown→Viewer` の解決サマリでは、以下を表示する。

- fieldType参照件数
- fieldType caption未指定件数
- 未指定がある場合の警告テーブル
- Common由来候補
- ViewDef個別指定

## 互換性

- caption未指定でも実行は継続する。
- ただし、生成ルール上は caption 必須として扱う。
- 将来の strict mode ではエラー化可能。
