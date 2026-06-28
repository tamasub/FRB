# v0.15.5 ViewDef Context Read Contract Report

## 目的

ViewDefに、AI作業前・コード更新前・ZIP返却前などに読むべき文脈を宣言できる `context.read_contract` 契約を追加した。

## 設計方針

- ViewDef全体にかかる文脈は `context.read_contract` または `read_contract` に置く。
- Data行単位にかかる文脈は Data JSON側の `context_refs` に置く。
- ViewDef側の `read_contract.row_context` は、Data行側の `context_refs` をどう読むかを示す接続設定として扱う。
- `read_timing` は `context.read_timing` Enumを使う。
- `failure_policy` は `context.failure_policy` Enumを使う。
- `trust` は `context.trust_category` Enumを使う。
- v0.15.5ではRuntimeが契約を認識する入口まで。実際の外部文脈ファイル自動読込・LLM投入は後続で扱う。

## 追加・更新

- `data/json/00_rules/common_enums_v0_1.json`
  - `context.failure_policy`
  - `context.trust_category`
- `defs/common/common_types_v0_1.json`
  - `context.failure_policy`
  - `context.trust_category`
- `data/json/00_rules/frb_view_def_schema_v0_9.json`
  - `context`
  - `read_contract`
  - `$defs.readContract`
  - `$defs.contextRef`
  - `$defs.rowContextContract`
- `data/json/00_rules/frb_viewdef_generation_rules_data_v0_1.json`
  - `viewdef_rule_27` 追加
- `data/json/00_rules/context_refs_sample_data_v0_1.json`
  - v0.15.5用メモ追加
- `defs/rules/context_refs_sample_view_def_v0_1.json`
  - `context.read_contract` サンプル追加
  - `failure_policy` / `trust` をFieldType化
- `wwwroot/js/core/viewdef_context_contract.js`
  - ViewDef read_contract のRuntime認識・正規化入口を追加
- `wwwroot/js/core/state.js`
  - `currentViewDefReadContract` 追加
- `wwwroot/js/runtime/load_runtime.js`
  - ViewDef読込時に read_contract を抽出
- `wwwroot/index.html`
  - `viewdef_context_contract.js` 読込追加

## 非対象

- required_refs の実ファイル自動読込
- 外部LLMへの自動投入
- 作業停止ワークフローの完全実行制御

## 確認

- JSON parse
- JS構文チェック
- context Enum存在
- FieldType enumRef参照存在
- ViewDef sample の read_contract 定義存在
- runtime生成物除外
