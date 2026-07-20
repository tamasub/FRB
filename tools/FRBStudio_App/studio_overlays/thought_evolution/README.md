# Thought Evolution Studio v0.1

外部ライブラリなしのSVG / CSS / JavaScriptで動く、汎用グラフOverlay。

## 起動

1. Studioで `overlay/thought_evolution/data/thought_evolution_graph_catalog_v0_1.json` を開く。
2. 一覧でグラフを選択する。
3. `Thought Evolution Studioを開く` を押す。

## データ分離

- `graph_defs/`: ノード種別・エッジ種別・色・形・フィルター等の表示契約。
- `graphs/`: ノード・エッジ・プリセット・Insight等の意味データ。座標は持たない。
- `layouts/`: ノード座標とViewport。意味データから分離。
- `sidecars/`: 画面から保存したレイアウト。API不可時はlocalStorageへ退避。

## v0.1の境界

Relation Approval、Thought Difference Radar、Evolution Engineは未実装。
