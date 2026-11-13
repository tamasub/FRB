# Studio Change Core | Step 4：共有Diff契約・Windows検証準備

- **Incident**：`studio_work_0269`
- **Phase**：`studio-external-changeset-core-v0_1`
- **基準**：`FRBStudio_App20261101_214530.zip`（最新添付）
- **方針**：既存StudioのF12/保存動作は変更せず、共通Diff責務を段階的に抽出する。

## 1. Windows実機の確認（ユーザー申告）

- ユーザーが `studio_work_0269` の編集・保存成功を報告した。
- Studioで読み込んだJSONをサクラエディタから変更・保存後、Studio保存で `409 CONFLICT: The JSON file has changed since loading.` を確認した。
- **確認できた保証**：別アプリによる更新をSHA競合として拒否すること。
- **未確認**：排他的ハンドル・Node CLIのWindows置換・NativeShellとCLIの同時書込・Nodeランタイム同梱。

## 2. Step 4の実装

1. `wwwroot/js/services/changeset/change_diff.js` を新設。
   - `compareDiff(before, after)`：JSON全体の差分抽出。
   - `compareExpectedActual(expected, actual)`：同一パス・操作・値の照合、期待欠落の検出。
   - DOM/IO非依存。Node CommonJSおよびブラウザGlobalから同じソースを使用。
2. `tools/change_core/change_core.mjs` は、共有Diff部品を使用するよう変更。
   - 初回の複数Add・Expected生成・Actual適用は従来動作を維持。
3. `wwwroot/index.html` でブラウザにも共有Diff部品をロード。
   - **注意**：画面のF12／保存処理はまだこの部品を実行していない。
   - UI・CLI完全共通の検証／Expected Diff受入条件は**未達**。
4. `tools/change_core/prepare_portable.ps1` の配布対象に共有Diff部品を追加。
5. `tests/change_core/windows_changeset_smoke.ps1` を追加。
   - 必ず一時JSONを生成。実データは一切変更しない。
   - dry_run／複数Add／古いSHA／専用ロック／Windows OSハンドル排他／外部書込／一時ファイル掃除を検査する。

## 3. 実行結果

- Linux / Node.js v22.16.0：**40 PASS / 0 FAIL**。
  - 実行：`node --test tests/change_core/change_core.test.mjs tests/change_core/native_bridge_cas.test.mjs tests/tree/tree_model.test.cjs tests/definition/cross_field_definition_test.test.mjs tests/qa/studio_ctrl_q_close.test.cjs`
  - 共有DiffのブラウザVMとNodeの結果一致／JSON Pointer／想定外変更検出／配布参照を追加。
- Linux / Python：**2 PASS / 0 FAIL**。
  - 実行：`python -m unittest discover -s tests/change_core -p 'test_*.py' -v`
- JS構文確認：`node --check` PASS。
- **未実施**：Windows専用PowerShellスモーク、C#実機ビルド、Node同梱実行。

## 4. Windowsでの次の検証

```powershell
# 最新差分ZIPをStudioへ上書き展開した状態で、Windows PowerShellから実行。
# node はPATH上にあるもの、またはフルパスを渡す。
powershell -NoProfile -ExecutionPolicy Bypass -File tests/change_core/windows_changeset_smoke.ps1 -NodeExecutable C:\nodejs\node.exe
```

- `SUCCESS` と全PASSが表示されることを確認する。
- 失敗した場合も元のインシデントJSONはテスト対象にならない。
- プロセス強制終了を伴う耐障害性（stale lock／クラッシュ耐性）は別検証。
- `prepare_portable.ps1`で正規Nodeバイナリから組み立てた配布物でも別途実行確認する。

## 5. 共通化の残り

1. Studio画面の編集操作を、明示されたChangeSet要求／Expected Diffへ変換する契約。
2. F12とCLIの共通Field Definition評価境界を整理し、**同じ保証経路**に接続する。
3. Windows上でのNativeShell `File.Replace` とNode `fs.rename`、他アプリの排他共有違反を検証する。
4. Windows配布（node.exeの同梱／利用者Node導入不要）、Launch Drop→Python→Node実運用接続。

## 6. 判断とリスク

- **判断**：既存UIを強制置換しない。使用中の編集・保存経路を維持し、Diffの純粋関数のみ共有へ昇格。
- **保証範囲**：同一のDiff計算コードをブラウザとNodeで利用可能。業務検証・Expected生成・保存保証全体を共有済みとは主張しない。
- **注意**：ユーザーのサクラエディタ409実績はSHA競合の成功であり、OSレベル排他ロック自体の実証ではない。
- **非協調書込**：外部アプリがロックに従わない場合のレースは、保存直前SHAだけでは完全排除できない。

## 7. Windows PowerShell 5.1 スモーク修正（2026-11-01 追加）

### ユーザー実機の結果（修正前）

- `powershell -NoProfile -ExecutionPolicy Bypass -File tests/change_core/windows_changeset_smoke.ps1 -NodeExecutable node` を実行。
- `dry_run`、dry_runでの元JSON維持、複数Addのcommit、保存行数の4項目がPASS。
- 古いSHAでの競合テスト結果を解析する際に `ConvertFrom-Json : 未終了の文字列が渡されました。` が発生し、後続の排他テストは未到達。
- 表示された日本語メッセージが文字化けしており、Windows PowerShell 5.1のネイティブパイプ文字コード依存と一致。
- **重要**：このログだけでは競合拒否／OS排他／Windows上の置換確認が成功したとはいえない。

### 修正内容

1. `tests/change_core/windows_changeset_smoke.ps1` のNode CLI呼び出しを、ネイティブの`$json | & node`から、`.NET ProcessStartInfo`に変更。
   - `stdin` はUTF-8（BOMなし）のバイト列を書き込む。
   - `stdout` / `stderr` はUTF-8で復号する。
   - 両出力を並行読取し、JSON応答は文字列のまま`ConvertFrom-Json`で解析する。
   - CLI終了コード・エラー応答は従来どおり評価する。
2. 同スモークに文字コード回帰確認を追加。
   - 日本語を含むAddレコード名が保存後も一致すること。
   - `CONFLICT`の日本語メッセージに「競合」が残ること。
   - ソースはASCII互換を維持し、Windows PowerShell 5.1のUTF-8 BOMなしソースの誤認を回避。
3. **変更なし**：Node Change Core本体、保存方式、NativeShell、実データ。

### 検証と残課題

- Linux環境ではWindows PowerShell 5.1を実行できないため、修正後スモークのWindows受入結果は**未確認**。
- Windowsで再度同じコマンドを実行し、すべてPASS・末尾`SUCCESS`を確認する。
- 以後も検証対象はスクリプトで作る一時JSONのみ。本番インシデントJSONは触らない。
