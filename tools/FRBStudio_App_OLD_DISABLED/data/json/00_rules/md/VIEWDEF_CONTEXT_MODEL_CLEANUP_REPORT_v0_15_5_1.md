# VIEWDEF_CONTEXT_MODEL_CLEANUP_REPORT v0.15.5.1

## 補修理由

v0.15.5.1初回整理では、主文脈を `context.main_context.refs[]` としてViewDef側に実データ配置していた。
しかしViewDefは画面定義であり、文脈の内容データを持つべきではない。

## 補修後の正本モデル

### 主文脈

- 表示名: 主文脈
- スコープ: ViewDef / 画面全体
- 実データ: Data root `main_context_refs[]`
- ViewDef側: `context.main_context.data_path` でDataパスを宣言するだけ

### 対象文脈

- 表示名: 対象文脈
- スコープ: 個別対象（インシデント1件、テストパターン1件、ルール1件など）
- 実データ: Data明細オブジェクト内 `context_refs[]`
- ViewDef側: `context.target_context.field` / `data_path` でData明細内の場所を宣言するだけ

## 共通Context Ref明細

主文脈でも対象文脈でも、Context Ref明細1件の構造は共通。

- `context_ref_id`
- `title`
- `read_timing`
- `target_path`
- `purpose`
- `failure_policy`
- `trust_category`
- `required`
- `enabled`
- `sort_order`
- `note`

## 更新方針

- ViewDefから `context.main_context.refs[]` の具体データを撤去。
- ViewDefから `context.read_contract.required_refs[]` の具体データを撤去。
- Data rootに `main_context_refs[]` を追加。
- Data明細側の `context_refs[]` は対象文脈として維持。
- Rules/Schemaに「ViewDefは文脈データを持たない」を明記。

## 確認結果

- JSON parse: OK
- JS変更: なし
- 更新済みIncident JSON: ZIP内 `data/json/01_main/` に収録
- runtime生成物除外: OK
