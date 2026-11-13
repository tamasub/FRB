# FRB Launch 0281 — 初期表示 My Work / Exp・List の論理位置整合

## 対象

入力: `launch_app_20261112_195818.zip`（0280 適用済み相当）

- 初起動: Files Exp の `My Work` をカレントにし、Files List には My Work の直下（例: ZIP / Quick / 日付・定型文）を表示する。
- 履歴「←」「→」: 保存した論理位置を復元した後、同じ位置の Exp ノードを選択する。Files List と Exp が食い違わないこと。
- 設定 JSON の仮想 Page / 登録フォルダー / 登録ルート / 直接パス入力 / PC は、0277〜0278 の論理パス仕様を維持する。
- Home の既存契約（Exp 全枝を閉じ、先頭ルートに移動）は変更しない。

## 修正箇所

`src/expanded_view.py`

1. 初回 Files 起動時のみ `work` Page (`My Work`) の論理ノードを選択してから Files List と履歴を構築。旧来の `PC` の物理リストで初期化しない。`work` Page がない設定では有効な先頭 Page、さらに必要な場合は従来の物理ルートへフォールバック。
2. Exp ツリー再構築時の保存済み選択状態は現在地の権威ではない。ツリー状態の復元後に、現在の論理位置から選択ノードを同期。
3. 履歴復元時にも同期を適用。仮想ノードだけでなく、PC、JSONマウント、直接パス、登録済みルート、その他の物理パスに対応。
4. 仮想Pageの履歴レコードには、無関係な旧第1列の `root_id` を記録しない。

## テスト

Linux ヘッドレス環境（PySide6なし）で既存コードのメソッドを AST 抽出して検証。

- `tests/test_launch_files_startup_history_sync_0281.py`: 5件 PASS
- 関連テスト合計: 45件 PASS / 1件（既存の古いRemoteボタン固定文字列アサーション）除外
- `python -m compileall -q src`: PASS

上記は Windows GUI実機テストではない。実機では以下を確認すること:

1. Launch を完全終了→再起動。Exp の My Work が選択され、パンくず My Work、List に ZIP / Quick 等が表示される。
2. `PC` へ移動 → Home → 履歴「←」。PC の内容へ戻るときは Exp も PC、My Work の内容へ戻るときは Exp も My Work となる。
3. `testwk > zz > サウンド レコーディング` から開く → 履歴Back/Forward。JSON側の入口を維持する。
4. `FRB Root` / `FRB_docsExcel > 設計書` / 直接パス入力 → 履歴Back/Forward。それぞれの論理起点を維持する。

この差分ZIPには設定JSONやユーザーの操作履歴を入れない。
