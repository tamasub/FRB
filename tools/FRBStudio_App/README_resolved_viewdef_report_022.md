# frb_studio_resolved_viewdef_report_022

## 変更内容

021 の Common FieldTypes 対応に対して、ViewDef Markdown レポートへ **解決済みViewDef確認メニュー** を追加した版。

### 追加

- `ViewDef Markdown→Viewer` のレポートに `解決サマリ` を追加
  - `fieldType` 参照件数
  - 読込済み共通Type namespace
  - `fieldType` ごとの解決結果
  - Common由来候補
  - ViewDef個別指定
- `解決済みViewDef概要` を追加
  - `extends` / `fieldType` 解決後の View / Section / Field 一覧
- `ViewDef JSON` セクションを折りたたみ表示に整理
  - `元ViewDef JSONを表示`
  - `解決済みViewDef JSONを表示`

## ねらい

管理用ViewDefは小さく保ちつつ、確認時にはベタ展開後の状態を見られるようにする。

```text
管理用ViewDef
  fieldType参照でコンパクト

確認用ViewDef Markdown
  解決サマリ + 解決済みJSONで全部見える
```

## 確認ポイント

1. `business_customers_fieldtype_sample_view_def_v0_1.json`
   - 元ViewDefの `customer_id / customer_name` は `fieldType` 参照のみ
   - 解決サマリで `business.customer_id / business.customer_name` が出る
   - 解決済みViewDef JSONでは caption / type / grid / edit / search が展開される

2. `relation_approval_view_def_v0_1.json`
   - `relation.status / coverage / confidence / priority` が解決サマリに出る
   - options 件数が表示される

3. 既存の `ViewDef Markdown→Viewer`
   - 元JSONと解決済みJSONの両方を確認できる

## 補足

現時点では差分の厳密な由来追跡ではなく、まず確認用の実用レポートとして実装している。

- `Common由来候補` : 元ViewDefにはなく、解決後に現れた項目
- `ViewDef個別指定` : 元ViewDef側に直接書かれている項目
