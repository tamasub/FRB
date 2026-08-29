# Thought Evolution Studio v0.3

外部ライブラリなしのSVG / CSS / JavaScriptで動く、Relation ApprovalとThought Difference Radarの汎用グラフOverlay。

## 起動

1. Studioで `overlay/thought_evolution/data/thought_evolution_graph_catalog_v0_1.json` を開く。
2. 対象グラフを選択する。
3. `Thought Evolution Studioを開く` を押す。
4. v0.3からThought Evolution Studioは新規ウィンドウで起動し、元のStudio画面を保持する。

## v0.3の主役

- Common / Asymmetry / Missing Link / Contradiction / Transfer Candidate / Concept Drift / Unexplained JumpをAnalysisProfileで定義する。
- DifferenceResult DataをAI提案として読み込み、該当ノードを発光し、Radar結果をInsightsへ表示する。
- Relation Proposalは直接正本化せず、`Relation Approvalへ送る` 操作でRelationDataへ移し、人間が承認・保留・却下する。
- Commonは差分を埋没させないため初期表示OFF。

## Relation Approval

- 線をクリックしてRelation Type・接続理由・根拠を確認・修正する。
- `AI_PROPOSED / HUMAN_APPROVED / PENDING / REJECTED` を色と線種で区別する。
- 承認・保留・却下は `data/json/01_main/thought_difference/thought_evolution_relation_approval_data_v0_1.json` へ保存する。
- ノード本文はOverlayへ複製せず、`resource_ref` からStudio標準エディターで開く。

## データ分離

- `graph_defs/`: ノード・エッジ・Relation Statusの表示契約。
- `graphs/`: 意味ノードとProjection。座標・承認状態の正本は持たない。
- `layouts/`: ノード座標とViewport。
- Core AnalysisProfile: Radarの分析観点・カテゴリ・表示規則。
- Core DifferenceResult: AIが生成した差分仮説とRelation Proposal。
- Core RelationData: 人間承認状態、理由、根拠、変更履歴の原本。
- Core Data/ViewDef: 制約・責務・TestPattern等の本文原本。

## v0.3の境界

Markdown全文解析や完全自動承認は行わない。分析結果は提案であり、Relation Approvalを経由する。判断ログから基準制約・判断軸・基準地形へ昇格するEvolution Engineはv0.4で扱う。


## v0.4 Evolution Engine

- DecisionLog / Relation Approval / Outcome / Difference をObservationとして正規化
- Profileの最低根拠数・成功結果・人間承認・理由・適用範囲でProposal候補を評価
- OBSERVATION / CANDIDATE / PROVISIONAL / APPROVED / VALIDATED / SUPERSEDED
- 反復回数だけでは自動昇格しない
- 人間承認前に元定義へ反映しない
- APPROVED / VALIDATED Proposalから、provenance付き次版Snapshotを別Dataへ生成

中心原則：

> 基準は設計するものではない。実践から蒸留する。
> ただし、反復は候補を生むだけで、正当性は人間が判断する。
