# Related Grid View Launch v0.18.28

## 目的

FRB Studio の「1画面 = 1メイングリッド」を維持したまま、ViewDefで宣言されたData root上の別配列を、別Studio画面の `grid_only` shellで編集する。

本機能は判断軸・制約専用ではない。ViewDefの `toolbar.relatedGridViews[]` に `dataPath` と `viewDef` または `viewId` を宣言すれば、任意のRoot配列へ再利用できる。`viewId`だけを指定した場合は同一ViewDefファイル内の `views[].id` を解決する。

## 初回利用例

- 親ViewDef: `defs/rules/rule_review_common_view_def_v0_3.json`
- 対象配列: `$.governance_items`
- 子ViewDef: `defs/rules/governance_items_common_view_def_v0_1.json`
- 代表Data: `data/json/00_rules/frb_coding_constraints_data_v0_3.json`

`governance_items[]` では、判断軸と制約を同一Gridで管理し、`item_type` の `DECISION_AXIS / CONSTRAINT` で区別する。

## データ同期契約

1. 親StudioがData JSON全体の所有者となる。
2. 子Studioは親から受信したDataのコピーを使い、宣言された配列だけを編集する。
3. 子StudioはData JSONファイルへ直接保存しない。
4. 「親画面へ反映」で、対象配列だけを `postMessage` で親へ返す。
5. 親側の対象配列が子画面を開いた後に変更されている場合、競合として反映を中断する。
6. 親へ反映後、最終的なファイル保存は親Studioで行う。

この方式により、親画面の主文脈編集と子画面のRoot配列編集を、後勝ちの全JSON保存で消し合う事故を避ける。

## ViewDef宣言例

```json
{
  "toolbar": {
    "relatedGridViews": [
      {
        "id": "document_governance_items",
        "caption": "判断軸・制約",
        "dataPath": "$.governance_items",
        "viewDef": "rules/governance_items_common_view_def_v0_1.json",
        "action": "OpenRelatedGridView",
        "launchMode": "new_window",
        "shellMode": "grid_only"
      }
    ]
  }
}
```

対象Dataに `dataPath` のArrayが存在しない場合、起動ボタンは表示しない。これにより、共通ViewDefを使う既存Dataへ空配列を一括追加せず、段階適用できる。

## 変更対象外

- インシデントData/ViewDefの構造
- 各ルール明細内の `decision_log[]`
- タブ型複数メイングリッド
- 他ルール系Data JSONへの一括展開
- `wwwroot/data` / `wwwroot/defs` の公開用コピー

## 確認

- `node --check` で変更JSの構文確認
- JSON全件parse確認
- `node --test tests/qa/static/related_grid_view_launch_static.test.mjs`
- ブラウザ実機では、ポップアップ起動、Detail編集、親反映、競合中断、親保存を確認する


## v0.18.34 同一ViewDef内View

同一Data JSONの複数Root配列を開くためだけに子ViewDefファイルを増やさないよう、`relatedGridViews.viewId`を追加した。

```json
{
  "relatedGridViews": [
    {
      "id": "sub_items",
      "caption": "Sub Items",
      "dataPath": "$.sub_items",
      "viewId": "sub_items_view",
      "action": "OpenRelatedGridView",
      "launchMode": "modal",
      "shellMode": "grid_only"
    }
  ]
}
```

解決規則:

- `viewDef`のみ: 外部ViewDefの先頭View。
- `viewId`のみ: 現在のViewDef内の指定View。
- `viewDef` + `viewId`: 外部ViewDef内の指定View。
- `viewId`未解決時は先頭Viewへfallbackせずエラー。
