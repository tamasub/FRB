# FRB Launch 0271 — コンテキストメニューとぐりぐりRunnerの一体化

日付：2026-11-12
基準：`launch_app_20261112_125203.zip`

## 課題

Expでは `RemoteFolderActionsMenu(CascadeMenu)`、Listでは `QMenu` と、コンテキストメニューの生成クラスが異なっていた。
スタイル調整だけでは描画上の差が残り、ぐりぐり操作も呼び出し側でRunnerを後付けする構造のため抜けやすかった。

## 採用する共通責務

- ExpとListのコンテキストメニューは、同じ **`FRBContextMenu`** を生成する。
- `FRBContextMenu` は QAction と **`RemoteContextWheel` (ぐりぐりクリックRunner)** を一つのUI部品として所有する。
- メニュー表示に伴いRunnerが自動起動、メニューを閉じると自動停止する。
- RunnerのQt `QObject` 親は **メニュー自身**。Launch本体の `_remote_context_wheel` は既存リモコンへの互換参照であり、Runnerの有効化条件ではない。
- リモコン表示／非表示で機能の有効性を変えない。
- 既存のホイールによるアクション選択・クリック実行・submenu処理は `RemoteContextWheel` の既存ロジックを再利用し、個別実装しない。
- フォルダー展開 (`Filesリスト`)、列切替、ファイル操作などの **項目内容** は従来どおり対象によって変える。共通化するのはメニュー部品とRunnerの所有権。
- 設定メニュー・Browserメニュー等の、Exp/List外のレガシーQMenuは互換経路で稼働。今回の一体化保証の範囲はExp/Listのすべてのコンテキストメニュー。

## 実装

1. `src/app.py`：`FRBContextMenu(RemoteFolderActionsMenu)` を定義し、`aboutToShow / aboutToHide` でRunnerライフサイクルを自己管理。
2. `src/app.py`：`_create_files_context_menu` を単一ファクトリーとして、Exp/Listの右クリック入口を同一生成ロジックに接続。
3. `src/app.py`：通常の `_wire_hybrid_context_menu` はExp/List用Runnerの後付けを行わない。既存Settings等だけ互換処理。
4. `src/remote_context_wheel.py`：RunnerのQt所有親をメニュー自身に変更。
5. `scripts/check_context_menu_contract.py`：今後Files Exp/Listから `QMenu` / `RemoteFolderActionsMenu` を直接生成したらビルドで検出。
6. `tests/test_frb_context_menu_owns_runner_20261112.py`：ファクトリー共通、Remote非表示でも起動、二重起動なし、閉じて停止、即閉じした場合は未起動、全入口の確認。

## 検証

- 構文検査 PASS。
- コンテキストメニュー契約検査 PASS。
- ダイアログ契約検査 PASS。
- 重点テスト 38件 PASS。
- 既存の旧メニュー試験群（13ファイル）は元ZIP・今回版ともに `53 PASS / 20 FAIL`。古いモック／旧文字列仕様に依存する失敗が多数残るため、Windows GUIでの受入確認は未完了。
- この環境には PySide6 がなく、Qt実描画や実際のクリック位置の実機検証はできていない。

## Windows 受入チェック

1. Expの登録フォルダー・実フォルダー・余白で右クリックし、アイコン・文字の配置が一致。
2. Listのフォルダー・ファイル・余白で右クリックし、Expと同じアイコン・文字配置。
3. リモコン非表示の状態で、ExpおよびListのそれぞれで **右クリック → ホイールで項目選択 → クリック実行** ができ、対象の操作が**1回だけ**実行。
4. リモコン表示時も同じ操作ができる。
5. `List列へ進む` / `Exp列へ戻る` で操作列だけが切り替わり、表示フォルダーは変わらない。
6. Filesリストのホバー展開、新規作成のサブメニュー、通常マウスの直接クリックが従来どおり。
7. メニューを閉じる・Escする・別メニューを開く場合もRunnerの操作対象が残らない。
