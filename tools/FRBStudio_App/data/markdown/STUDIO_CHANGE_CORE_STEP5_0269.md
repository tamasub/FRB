# Studio Change Core｜Step 5：Studio F12 と外部ChangeSetの共通受入判定

- **work_item_id**：`studio_work_0269`
- **phase**：`studio-external-changeset-core-v0_1`
- **基準ZIP**：`FRBStudio_App20261101_220836.zip`
- **適用方法**：差分ZIPをStudioアプリルートへ上書き展開。
- **対象**：F12正本反映、Field Definitionの受入判定、Expected／Actual Diffの一致判定。
- **非対象**：FRB Launch UI／Drop連携、NativeShell C#コード、保存API・ファイル置換方式の変更。

## 1. 背景と今回の判断

- 前段までに、Node CLIの複数Add、保存CAS、共有Diff計算が実装された。
- Windows実機では、ユーザー報告のPowerShellスモーク **16/16 PASS**。
  - dry_run、複数Add、日本語保存、古いSHA競合、協調ロック、Windows OS排他、非協調外部書込、未変更保持、一時ファイル掃除を確認。
  - **これはStep 4の実機受入結果**。Step 5のブラウザF12変更のWindows受入ではない。
- Step 5は「外からつまめ原則」に従い、既存F12の操作順序と保存経路を全面置換しない。
- **新しい共通部品は受入判定のみ**。操作要求の構築、Expected生成、全ドキュメント保存までの完全共通化は未達。

## 2. 変更内容

1. **共通Change Gate追加**：`wwwroot/js/services/changeset/change_gate.js`
   - `assessFieldValidation(result)`：既存Field Definition検証結果を受入／拒否へ変換。
   - `assessExpectedActual(expectedDiff, actualDiff)`：Step 4の共通Diffに基づく一致判定。
   - `assessRowCommit(before, proposed, committed)`：F12行反映のExpected／Actualの一致を照合。
   - `ACCEPT` または Field Definition未宣言を明示する `SKIPPED` 以外は拒否。
   - **Nodeとブラウザで同じJavaScriptを使用**。DOM／File I/Oには依存しない。
2. **Studio画面 F12**：`wwwroot/js/runtime/detail_save.js`
   - 既存 `RuntimeFieldDefinitionValidationService` の結果を共通Gateへ渡す。
   - 編集行の反映前後を比較し、不一致なら正本行をロールバック。
   - 新規行も追加前後を照合し、不一致なら追加を取り消す。
   - 拒否時は関連Gridの自動同期を呼ばず、画面エラーを表示する。
   - F12／F7/F8の既存呼び出しと行オブジェクト同一性を維持。
3. **外部ChangeSet CLI**：`tools/change_core/change_core.mjs`、`field_validation.mjs`
   - 既存Diff計算・既存Field Definition検証器は維持。
   - 差分一致と検証結果の承認／拒否を共通Gateへ接続。
4. **読込・配布**：`wwwroot/index.html`、`tools/change_core/prepare_portable.ps1`
   - ブラウザでは共通Diff→Gate→F12の順序で読込。
   - F12 JSのキャッシュバージョンを更新。
   - ポータブルNode媒体にGateを収録する設定を追加。
5. **回帰テスト**
   - 共通Gateの受入／拒否、ブラウザとNodeの判定一致、実F12反映・ロールバック、新規行撤回を追加。
   - 旧F12テスト用VMにも共通部品を読込・注入し、既存の振る舞いを引き続き検証。

## 3. テスト結果

- **Linux / Node.js**：`node --test tests/change_core/change_core.test.mjs tests/change_core/native_bridge_cas.test.mjs tests/tree/tree_model.test.cjs tests/definition/cross_field_definition_test.test.mjs tests/qa/studio_ctrl_q_close.test.cjs` → **45 PASS / 0 FAIL**。
- **Studio static**：`node --test tests/qa/static/*.test.mjs` → **630 PASS / 0 FAIL**。
  - 途中で発見した旧テストVMのGate未読込、F12実装に依存する静的断言を新契約に合わせて更新済み。
- **Python**：`python -m unittest discover -s tests/change_core -p 'test_*.py' -v` → **2 PASS / 0 FAIL**。
- **Windows 11・ユーザー報告（Step 4）**：PowerShellファイルシステムスモーク **16/16 PASS**（本文は会話ログ）。
- **未実施**：Step 5のWindows NativeShell＋WebView2でのF12画面実操作、同梱Node媒体の実機配布・起動。

## 4. 保証できること／まだ保証できないこと

### 今回確認できたこと
- F12の検証結果の採否判定がNode CLIと同じGateに到達する。
- F12正本行のExpected／Actual不一致は、新規／既存行いずれも保存前の反映を拒否する（Node VM）。
- F12の正常系、バリデーション拒否、Markdown編集、関連Grid同期など既存静的回帰を維持。
- CLIの既存複数Add・差分照合・競合・Python連携テストを維持。

### 残課題・リスク
1. **完全共通化ではない**：画面はF12の行単位反映、CLIはChangeSetによる文書単位Add。ChangeSet要求構築、Expected生成、全体業務検証／保存ワークフローは別。
2. **今回のF12 Diffは「反映した行」だけをチェック**：画面UIからの読取の正しさや、別Grid・Document全体の変更を独立に保証するものではない。
3. **Windows画面の受入未実施**：Studio実機でF12・新規行・既存行・Field Definition違反・Markdown・再保存を確認する。
4. **Pythonポータブル配布未検証**：node.exe/ライセンス同梱の動作と企業PCの実行制限を確認する。
5. **原子性の限界**：電源断耐性、協調しないアプリによる保存直前の割り込みは別途検証／設計が必要。

## 5. 次ステップ

1. Windows Studio実機で、今回のF12動作と既存保存を受入検証する。
2. Studio画面側の編集要求を純粋なChangeSet契約へ接続する境界を、単一レコードから設計・実装する。
3. Document全体のExpected／Actualと保存前制約を共通にして、業務検証経路の二重化を減らす。
4. その後、FRB Launch Python→Node CLIの実運用接続とポータブル配布を検証する。

## 6. 変更ファイル一覧

- `wwwroot/js/services/changeset/change_gate.js`
- `wwwroot/js/runtime/detail_save.js`
- `wwwroot/index.html`
- `tools/change_core/change_core.mjs`
- `tools/change_core/field_validation.mjs`
- `tools/change_core/prepare_portable.ps1`
- `tests/change_core/change_core.test.mjs`
- `tests/qa/static/field_definition_runtime_validation_acceptance.test.mjs`
- `tests/qa/static/related_grid_auto_apply_20261018.test.mjs`
- `tests/qa/static/related_grid_markdown_f12_loss_regression_20261018.test.mjs`
- `data/markdown/STUDIO_CHANGE_CORE_STEP5_0269.md`
- `data/json/01_main/_studio_work_incident_data_v2.json`
