# frb_constraint_trace_graph_001

制約・テストパターン・期待状態・actual・diff・check を、ノードとエッジで接続する最小証跡グラフです。

## 生成物

### data
- `constraint_trace_graph_v0_1.json`  
  正規形に近いノード・エッジ形式。
- `constraint_trace_cards_v0_1.json`  
  FRBStudioで見やすい制約中心のカード形式。
- `constraint_trace_edges_v0_1.json`  
  エッジ一覧確認用。

### def
- `constraint_trace_cards_view_def_v0_1.json`
- `constraint_trace_edges_view_def_v0_1.json`
- `constraint_trace_graph_nodes_view_def_v0_1.json`

## v0.1 の考え方

既存の制約JSON・テストパターンJSON・diff JSONは壊さず、関係だけを外側に作っています。

```text
制約
  ↓ verified_by / partially_verified_by / presence_checked_by
テストパターン
  ↓ expects / produces_actual / produces_diff
期待状態 / actual / diff
  ↓ has_check / has_failed_check
diff check
```

## 注意

制約とテストパターンの紐づけは、初期 seed/inferred です。  
`confidence: low/medium` を入れているので、次のステップでは人間レビューで確定させます。

## 現時点の集計

- 制約数: 84
- テストパターン数: 3
- ノード数: 108
- エッジ数: 135
- 紐づいた制約数: 8
- 未テスト制約数: 76
- 失敗diffに接続された制約数: 8

## まず見るなら

`constraint_trace_cards_v0_1.json` を `constraint_trace_cards_view_def_v0_1.json` で開くのがおすすめです。
