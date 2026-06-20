# README — ViewDef Rules v0.10

## 追加内容

v0.10 では、`fieldType` 使用時の `caption` 明示ルールを追加した。

## ねらい

Common FieldTypes によって ViewDef を小さくしつつ、元ViewDefだけを見ても人間が意味を読めるようにする。

## 基本ルール

```json
{
  "field": "quality_axis_cd",
  "caption": "品質観点",
  "fieldType": "qa.quality_axis"
}
```

- `caption` は ViewDef側が優先
- Common側 `caption` は fallback
- caption未指定は警告対象

## 関連

- `FRB_VIEW_DEF_GENERATION_RULES_v0_8_common_field_types.md`
- `FRB_VIEW_DEF_GENERATION_RULES_v0_9_semantic_field_types.md`
