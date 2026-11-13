# FRB Studio — Launch Page追加時の既存Page上書き修正（2026-11-10）

## 症状
Launch設定メンテナンスの「Pageを追加」で、選択中のPageの名前が編集されてしまい、新しいPageが増えない。

## 原因と修正
`wwwroot/js/runtime/tree_groups.js` 内 `studioTreeEditGroup(isNew)` の新規作成経路で、選択済みの既存Pageレコードを流用していた。
新規作成では `existing = null` とし、UUIDによる新しい `page_id` と末尾 `sort_order` を持つPageレコードを作る。編集経路は従来通り選択Pageを更新する。既存の「Pageを追加」「Pageを編集」ボタンはそのまま使う（ボタン追加なし）。

## テスト
- `node --test tests/qa/static/launch_page_creation_20261110.test.cjs` — 新規追加時の既存Page非変更／ID新規採番／編集／キャンセル・空入力を確認（3 PASS）。
- `node --test tests/qa/static/studio_presentation_profile.test.mjs tests/qa/static/launch_context_page_group_focus.test.mjs` — Launch表示とPage選択周辺の既存静的テスト（12 PASS）。
- Windows/NativeShell実機でのUI操作・保存・再起動は未確認。

## Windowsでの確認手順
1. Launchから「設定メンテナンス」を開く。
2. 既存Pageを選択して「Pageを追加」を押す。入力は空欄で表示されること。
3. 新しい名前を入力 →「反映」。既存Pageの名前を変えずにPageが増えること。
4. 「保存」→ Launch再読み込み。Pageが継続表示されること。
5. 「Pageを編集」では既存Pageの名前だけ更新されること。

※既に誤って保存したPage名称は本改修では自動復元しない。
