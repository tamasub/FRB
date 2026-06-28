# v0.15.5.3-target-context-detail-panel 作業報告

## 目的

Data明細オブジェクト内の `context_refs[]` を対象文脈として扱い、Detail画面の上部で要約・確認・編集できるようにする。

## 方針

- 主文脈は画面全体の入口としてヘッダーに表示する。
- 対象文脈は個別対象の入口としてDetail上部に表示する。
- ViewDefは文脈実データを持たず、Data上の場所と表示・編集方法だけを宣言する。
- Gridでは `context_refs[]` の生JSONを出さず、件数要約を表示する。
- 対象文脈は通常 `childArea` の末尾objectArray表示から除外し、専用パネルを正本表示にする。

## 更新内容

### Runtime / UI

- `wwwroot/js/core/state.js`
  - `targetContextDetailPanelExpanded` を追加。
- `wwwroot/js/core/viewdef_context_contract.js`
  - `context.target_context` のRuntime解釈を拡張。
  - 対象文脈件数要約を生成する `formatTargetContextValue` を追加。
  - Detail上部の `renderTargetContextDetailPanel` を追加。
  - 対象文脈の追加・削除・反映を追加。
- `wwwroot/js/renderers/field_controls.js`
  - `context_refs[]` のGrid表示を生JSONではなく件数要約に変更。
- `wwwroot/js/renderers/grid_detail.js`
  - Detail反映時に対象文脈パネルの編集値をData明細へ反映。
- `wwwroot/js/runtime/detail_save.js`
  - Detail上部に対象文脈パネルを描画。
  - 対象文脈フィールドは通常childArea末尾表示から除外。
- `wwwroot/styles.css`
  - 対象文脈パネル用CSSを追加。
- `wwwroot/index.html`
  - 関連JSのキャッシュバスターを v0.15.5.3 に更新。

### ViewDef / Data / Rules

- `defs/rules/context_refs_sample_view_def_v0_1.json`
  - `context.target_context.detail_panel` を追加。
  - `context_refs` Grid表示を件数要約方針へ更新。
- `data/json/00_rules/context_refs_sample_data_v0_1.json`
  - v0.15.5.3 の説明へ更新。
- `data/json/00_rules/frb_view_def_schema_v0_9.json`
  - `targetContextContract` に Detail上部パネル契約を追加。
- `data/json/00_rules/frb_viewdef_generation_rules_data_v0_1.json`
  - `viewdef_rule_27_03` を追加。

## 確認結果

- JSON parse: OK
- JS `node --check`: OK
- 対象文脈Detail上部パネル: 実装済み
- Grid件数要約: 実装済み
- 通常childArea末尾表示から対象文脈を除外: 実装済み
- ViewDefに文脈実データなし: 維持
- 更新済みIncident JSONのZIP内収録: OK
