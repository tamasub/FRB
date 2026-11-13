# Studio Change Core｜studio_work_0269 タイムアウト修正・次ステージ進捗

- **phase**: `studio-external-changeset-core-v0_1`
- **基準**: `FRBStudio_App20261101_211842.zip`（最新添付）
- **対応範囲**: NativeShell大容量JSONタイムアウト修正 → UI保存CAS接続 → Python/Node連携実証。
- **進捗判断**: 一部達成。Windows実機・完全共通検証・Node同梱配布は未受入。

## 1. 事象・原因・修正

- **症状**: 約3.9MBの `_studio_work_incident_data_v2.json` をStudioから更新するとタイムアウト。
- **原因特定（コード上）**:
  - `NativeShellForm.OnWebMessageReceived` が、処理前に `new JavaScriptSerializer()` で全メッセージを解析。
  - 既定 `MaxJsonLength` は約2MB。大きな保存要求を解析しようとすると例外。
  - 外側のcatchがステータスを更新するだけで要求応答を返さず、JS側30秒 `NATIVE_TIMEOUT`。
  - 後段Dispatcherは `MaxJsonLength = int.MaxValue` を既に設定済み。
- **修正**:
  - 32KB以下のUI制御メッセージだけ前段で検査。
  - 大容量コマンドは前段で二重解析せずDispatcherへ渡す。
  - **大容量の保存可能性を改善**。Windows実機でタイムアウト消滅の最終確認が必要。
- **既存データ**: 内容・ID・行の削除、分割や軽量化は行っていない。

## 2. UI保存と外部CLIの保存保証を接続

- `file.readText`は同一バイト列から本文とSHA-256を返却。
- Native browser bridgeは `GET /api/data/..` 時点のSHAを保持。
- `POST /api/data/..` は `file.writeTextCas` に変更。
- CAS保存は次の順序:
  1. 書込み許可パスの検証（`data/json/*.json`、`fielddefs/*.json`）。
  2. 同じ `.studio-changeset.lock` の協調ロック取得。
  3. 保存元SHAを確認。
  4. JSON構文とトップレベルObjectを検査。
  5. 同フォルダへ書込み、ファイル内容をFlush。
  6. 保存直前にSHAを再確認。
  7. Windows `File.Replace` で既存ファイルを置換。
  8. ロックと一時ファイルを後始末。
- 競合／ロック中は HTTP 409（ブラウザ内のFetch API互換応答）。
- 保存成功後は最新SHAを基準値に更新。失敗時は古い基準値を維持。
- **共通になった部分**: 保存先ファイルに対する協調ロック名、CAS条件、置換方式、保存前の競合拒否という**プロトコル**。
- **まだ共通でない部分**: Node ChangeSetとStudio UIの業務検証・Expected Diffの実行コード。UIは既存F12/保存経路を使用する。
- **未改修の保存経路**: `/api/defs`、`/api/markdown`、起動時ファイル、その他独立の書込みAPI。全画面が共通保存に移行したわけではない。

## 3. Python・配布ステージ

- `tools/change_core/python_client.py` を追加:
  - Python標準ライブラリ `subprocess` で Node CLI 起動。
  - JSON stdin/stdout。Port・HTTP常駐不要。
  - エラーや競合も構造化された戻り値として扱う。
  - SHA-256の初回スナップショット計算関数を提供。
- `tools/change_core/prepare_portable.ps1` を追加:
  - 手元にある正規の `node.exe` とライセンスを明示的に渡してCLIフォルダを構築する補助スクリプト。
  - 外部接続・自動ダウンロードなし。
  - **Windows上では未実行**、実際のNode同梱ZIPは未作成。
  - Node.exeやライセンスをこの差分ZIPに含めない。

## 4. 検証結果

- Linux Node.js v22.16.0:
  - `node --test tests/change_core/change_core.test.mjs tests/change_core/native_bridge_cas.test.mjs tests/tree/tree_model.test.cjs tests/definition/cross_field_definition_test.test.mjs tests/qa/studio_ctrl_q_close.test.cjs`
  - **37 PASS / 0 FAIL**。既存テスト＋追加4件。
  - 追加テストは257行目ではなく**257件のインシデント／約3.9MBの実JSON**をVMのブラウザBridgeでロード・CAS保存し、次回保存の基準SHA更新を確認。
  - 競合時409・初回GETなし拒否・C#修正箇所の静的検査を確認。
- Python 3:
  - `python -m unittest discover -s tests/change_core -p 'test_*.py' -v`
  - **2 PASS / 0 FAIL**。Node subprocessの `dry_run → commit → conflict`、不正な親での無変更。
- `node --check wwwroot/js/core/native_host_bridge.js`: PASS。
- JSONインシデント：Parse確認、他256件に変更がないことを確認予定（ZIP生成時に比較）。

## 5. 残課題・リスク

1. **Windows NativeShellビルド・実機保存**: このLinux環境に.NET Framework 4.8 SDK/Windows/WebView2なし。C#は静的検査のみ。**タイムアウト修正も最終受入前**。
2. **UIとCLIの完全共通責務**: 現在はストレージの協調プロトコルを共有するが、両者のField Definition・Expected／Actual保証を一か所のCoreコードに統合していない。Step 2統合受入は未達。
3. **Windows原子的置換**: C#の`File.Replace`、Nodeの`fs.rename`について、Windows上のエディタ排他・共有違反・ACL・ロック競合を実地に確認する必要がある。
4. **協調しない外部書込**: `.studio-changeset.lock`を見ない他アプリとの完全な同時更新排他は保証しない。
5. **他の保存経路**: 依然として従来保存を使用するため、同一保証と主張しない。
6. **配布**: 正規のNodeランタイム・ライセンスを準備し、ポータブルビルダー実行、Windows Python連携を確認する。

## 6. 次に行うこと

1. 最新資材をWindowsに展開し、`studio_work_0269`をStudio UIで更新・保存・再読込してタイムアウト消滅を確認。
2. 同じJSONをStudio/Node CLI双方で同時に編集し、競合拒否・ロック解除・再読込を確認（バックアップを取得）。
3. 外部ChangeSet AddをStudio UIの共通検証／差分保証へ統合できる境界を設計・実装する。
4. Portなし・ローカルnode.exe同梱の配布をWindowsで確認する。

## 7. 更新ファイル

- `NativeShell/NativeShellForm.cs`
- `NativeShell/NativeCommandDispatcher.cs`
- `NativeShell/native_shell.config.json`
- `wwwroot/js/core/native_host_bridge.js`
- `tools/change_core/python_client.py`
- `tools/change_core/prepare_portable.ps1`
- `tools/change_core/README.md`
- `tests/change_core/native_bridge_cas.test.mjs`
- `tests/change_core/test_python_client.py`
- `data/markdown/STUDIO_CHANGE_CORE_STEP3_0269.md`
- `data/json/01_main/_studio_work_incident_data_v2.json`
