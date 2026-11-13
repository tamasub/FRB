# v0.14.1 Data JSON内ViewDef候補

## 目的

Data JSON側に、そのDataで利用可能なViewDef候補を明示できるようにする。
これにより、ViewDefを大量に作成した後でも、Dataから参照されているViewDefと未参照ViewDefを棚卸ししやすくする。

## Data契約

既定ViewDefは従来どおり top-level `view_def` に保持する。
複数候補を持たせる場合は top-level `view_def_candidates` を追加する。

```json
{
  "view_def": "rules/main_view_def.json",
  "view_def_candidates": [
    {
      "view_def": "rules/main_view_def.json",
      "label": "標準表示",
      "role": "default",
      "status": "active",
      "note": "通常利用するViewDef"
    },
    {
      "view_def": "rules/relation_view_def.json",
      "label": "リレーション確認",
      "role": "relation",
      "status": "active",
      "note": "関連データ確認用"
    }
  ]
}
```

`view_def_candidates` は文字列配列でも利用可能。

```json
{
  "view_def_candidates": [
    "rules/main_view_def.json",
    "rules/relation_view_def.json"
  ]
}
```

## Runtime方針

- Data JSONを選択・読込した時点で `view_def` / `view_def_candidates` を読み取る。
- ViewDef手動切替UIには、そのDataに明示された候補だけを表示する。
- `view_def` のみを持つ既存Dataでは、`view_def` を単一候補として扱う。
- `view_def` も `view_def_candidates` もないDataでは、従来の互換ViewDef自動探索を利用する。
- 手動切替で候補外のViewDefが指定された場合はエラーにする。
- 手動切替しても、保存時に既定 `view_def` を勝手に書き換えない。

## 変更ファイル

- `wwwroot/js/core/state.js`
- `wwwroot/js/core/viewdef_resolver.js`
- `wwwroot/js/core/loaders.js`
- `wwwroot/js/runtime/load_runtime.js`
- `wwwroot/js/ui/file_tree_picker.js`
- `wwwroot/js/ui/page_setup.js`
- `wwwroot/app.js`
- `wwwroot/index.html`
