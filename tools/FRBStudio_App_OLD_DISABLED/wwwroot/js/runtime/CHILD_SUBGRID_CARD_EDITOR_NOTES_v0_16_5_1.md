# v0.16.5.1 Child SubGrid Card Editor / Renderer Scope Fix

## 目的

v0.16.5 で追加した Card(Document) Grid を削除せず、適用先を正しい粒度へ戻す。

- メイン一覧 Grid は従来 Table Grid を標準維持する。
- `discussion_history` / `decision_log` / `change_history` などの detail 内 objectArray サブグリッドは、まず従来 Table 表示に戻す。
- サブグリッドには `編集` / `プレビュー` ボタンを置き、Card 表示は dialog 上の読み物・編集UIとして使う。
- Card Grid Renderer 自体は温存し、少数行・設定系・実行系のメインGridで明示指定された場合には引き続き利用可能にする。

## 仕様判断

今回のズレは、Card Renderer が不要だったのではなく、適用先が粗すぎたことが原因。

- NG: 82件の work_items メイン一覧を Card 化する
- OK: 1作業項目内の履歴配列を Card プレビュー/編集する
- OK: Git Diff Run Config のような少数行・項目少なめ・即編集/実行型の画面で Card Grid を明示指定する

## 変更内容

- `studio_work_incident_view_def_v0_5.json` の work_items メインGridから `grid.renderer=document` 指定を撤回。
- detail サブグリッドのヘッダーに `編集` ボタンを追加。
- `編集` ボタンで Card形式の編集dialogを開く。
- Card編集dialog内で以下を実行可能にした。
  - 末尾追加
  - 上挿入
  - 下挿入
  - 複製
  - 上下移動
  - 削除
  - 各セル値のカード内編集
- `一覧へ反映` でサブグリッドTableへ反映し、その後 F12 / 反映ボタンで親JSONへ同期する。
- `プレビュー` は引き続き Card形式の読み物dialogとして利用する。

## 確認観点

- インシデント管理のメイン一覧が従来 Table Grid に戻ること。
- 判断ログ / 会話履歴 / 変更履歴のサブグリッドが Table 表示されること。
- サブグリッドの `編集` ボタンで Card編集dialogが開くこと。
- Card編集dialogで行追加・挿入・削除・複製・上下移動ができること。
- `一覧へ反映` 後、サブグリッドTableへ変更が戻ること。
- F12 / 反映ボタンで親行JSONへ同期されること。
- `grid.renderer: "document"` を明示指定した少数行画面では、v0.16.5のCard Gridが引き続き使えること。

## 構文確認

- `wwwroot/js` 配下の全JSに対して `node --check` を実施。
