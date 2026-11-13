# FRB Studio — Editor「前へ/次へ」を現在Gridの表示順に合わせる（2026-11-11）

## 依頼
Editor画面の「前へ (F7)」「次へ (F8)」を、現在のGridの並び順で移動させる。

## 変更
- Editorナビゲーションの順序を `filteredRows` の内部順序から、実際に描画されているGrid行のDOM順へ変更。
- 通常Gridの列ソート（昇順・降順）、検索による絞り込み、カードGrid、Tree表示の階層順・折りたたみを同じルールで処理。
- Treeの仮想グループ見出し（sourceIndexが負数）は移動対象外。
- Editorの前後ボタン有効/無効も、同じ表示行順に基づき判定。
- Grid未描画の場合のみ、従来の `filteredRows` にフォールバック。
- 編集内容のコミット・検証、関連Gridの端点動作、新規Editorでの移動禁止は従来動作を維持。

## 変更ファイル
1. `wwwroot/js/renderers/grid_detail.js`
2. `tests/qa/static/detail_navigation_visible_grid_order_20261111.test.mjs`（新規）
3. `reports/EDITOR_NAV_VISIBLE_ORDER_CHANGELOG_20261111.md`（本書）

## テスト
- Node単体テスト: 7/7 PASS（新規）
- 既存関連テスト込み: 29/29 PASS
- Windows / Edge WebView2上での操作確認は未実施。

## 手動確認
1. 一覧Gridで列見出しを押して降順等に並び替え、任意の行をダブルクリック。
2. Editorの「次へ」/F8、「前へ」/F7で画面上の順序に沿って移動するか確認。
3. 検索で数件に絞り込み、表示対象だけで前後移動することを確認。
4. Tree利用時は展開行のみを順番に巡り、折りたたんだ行とグループ見出しに移動しないことを確認。
5. 最初・最後の行で移動ボタンが無効になること、編集のValidationエラー時に移動しないことを確認。
