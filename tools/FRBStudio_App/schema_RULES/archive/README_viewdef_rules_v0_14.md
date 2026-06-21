# README — ViewDef Rules v0.14

## 追加内容

Markdown出力時に AI貼り付け用ブロックを末尾へ出力できるようにした。

主な対象:

- 不足検出 VirtualData
- クロス集計 VirtualData
- AIに追加候補JSONを作らせたいグリッド

## 代表ViewDef

```text
defs/qa_shortage_expected_findings_view_def_v0_1.json
```

## 使い方

1. 不足検出ViewDefで対象JSONを開く
2. 必要なら検索で行を絞り込む
3. `Markdown出力→Viewer`
4. Markdown末尾の `AI貼り付け用` をコピーしてAIに渡す

## 出力されるもの

- プロンプト
- 現在表示中グリッドのTSV
- Grid JSON（field/caption/rows）

## 重要な考え方

```text
不足検出 VirtualData
  ↓
AI貼り付け用Markdown
  ↓
追加候補JSON生成
  ↓
人間レビュー
  ↓
Expected定義へ追記
  ↓
再度、不足検出
```

このループをViewDefから生成する。
