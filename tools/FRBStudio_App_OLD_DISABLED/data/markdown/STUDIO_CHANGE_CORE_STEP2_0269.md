# Studio Change Core｜studio_work_0269 Step 2 実装・検証記録

- phase: `studio-external-changeset-core-v0_1`
- 基準ZIP: `FRBStudio_App20261101_205905.zip`
- 実装範囲: **外部CLIの複数Add最小経路**。Studio UI共通接続は**未完了**。
- 進捗判断: **Step 2 部分実装済み、統合受入は未達**。

## 1. 変更内容

1. `tools/change_core/change_core.mjs`
   - ViewDefの`view_id`・`section_id`・`dataPath`・`tree`を参照する汎用ChangeSetエンジン。
   - `operations[]`複数Add／`records[]`複数件を受理。v0.1では1文書、`position=end`のみ。
   - IDがない行は適用計画生成時にUUIDを確定。既存行の再採番をしない。
   - Expected Diffは追加計画から明示し、Actual Diffは適用後の文書全体から計算。想定外差分を保存前に拒否。
   - Tree整合性は既存`StudioTreeModel`を再利用。Launch固有IDは埋め込まず、同一パス重複禁止も追加しない。
2. `tools/change_core/field_validation.mjs`
   - 既存のDOM非依存のField Definition検証コードをNode VMから呼び出す。
   - `item_definition_ref`が指定されている場合だけチェック。未宣言時は検証省略を明示。
3. `tools/change_core/storage.mjs`
   - `.studio-changeset.lock`の排他的な作成で協調的に保存を直列化。
   - 生バイトのSHA-256を保存直前に再確認。変更済みなら`CONFLICT`。
   - 同ディレクトリ一時ファイルへの書込み＋sync＋rename。異常時は一時ファイルを削除。
4. `tools/change_core/cli.mjs` / `config.example.json` / `README.md`
   - stdinでJSON要求、stdoutでJSON結果。HTTP Port不要。
   - `--config`の明示的な許可済み`document_ref`・View・Sectionからだけ書込み可能。
   - `dry_run`と`commit`、成功時`PREVIEW`／`COMMITTED`、競合`CONFLICT`、拒否`REJECTED`を返す。
5. `tests/change_core/change_core.test.mjs`
   - 複数Add・既存行保護・拒否・競合・ロック・書込み障害・Expected/Actual不一致・既存Field Definition利用を確認。

## 2. 保証対象／対象外

- **対象**: CLIで単一JSONへAddし、1件でも異常なら保存しない。記録した許可対象以外のファイルを書かない。`base_sha256`競合時も保存しない。
- **対象**: 既存TreeのID・親子循環・グループ整合性・親の種類を検証する。
- **対象**: Field Definitionが明示されている場合はStudioの既存Serviceを使用。
- **対象外**: Field DefinitionのないViewDefでの業務値の完全検証。Studio UIとCLIで同じ保存APIの共用。外部の協調しない編集者まで含む完全な排他保証。
- **対象外**: 複数ファイルの原子性。Update／Delete／Move／前後への挿入。Python呼び出し、Nodeバンドル、Windows実機。
- **重要**: Linux/Node上の原子的`rename`テストはWindowsでの完全な原子性・ACL／共有ロック・電源断耐性の立証ではない。

## 3. 試験結果（2026-11-01）

- 実行環境：Linux、Node v22.16.0。
- コマンド：`node --test tests/change_core/change_core.test.mjs tests/tree/tree_model.test.cjs tests/definition/cross_field_definition_test.test.mjs`
- **25 PASS / 0 FAIL**（新規11件＋既存14件）。
- 複数Add `dry_run` は実ファイル無変更、`commit`は新SHAを返し2件保存。古いSHA再実行は競合で拒否。
- 不正な親・グループ・ID重複・未対応操作・未承認Sectionは拒否。途中失敗でも元文書無変更。
- 保存時ロック競合、保存直前の外部変更、人工的な一時ファイル書込み後エラーに対し、旧文書保持と一時ファイル後始末を確認。
- 既存Field Definitionの必須値欠損に対し`FIELD_DEFINITION_REJECTED / REQUIRED_MISSING`を確認。
- Studio画面からの利用・dotnet build・Windows実機での検証・Python連携・Node同梱は**未実施**。

## 4. 重要な判断と残リスク

1. **既存UI側の保存経路は変更しない**。現在のPOST→`file.writeText`は新しい協調ロック／CASを共有しない。誤ってUIを同一保証済みと主張しないため、統合方式が確立するまで既存操作の破壊を避けた。
2. **ロックとSHAを併用**。ロックは協調的な利用者同士だけを排他。協調しないサクラエディタ等が外部書込みできる場合の完全な競合防止は未達。
3. **Field Definition未設定**のLaunch用ViewDefでは現行UIと同様にField Definition検証がSKIPされる。Tree制約以外の業務整合性は保証しない。
4. **同一文書だけ原子的**。複数ファイル保存、ディレクトリfsyncが実行できないOS、権限・ACL、古いロックの復旧は未解決。
5. Expected Diffの期待行は計画から、Actual Diffは文書差分から独立して列挙しているが、計画器・適用器の仕様共有は残る。追加の定義駆動保証・Fault Injectionを増やす。

## 5. 次作業

1. **Step 2未完了**：Studio UIのJSON保存もCLIと同じ検証・CAS・原子的保存責務へ接続する。既存F12と保存を別物として責務分離し、NativeShell経由のNode呼び出し／保存アダプター接続方式を実証する。
2. 保存元のバージョン管理をUIのロード時に追加し、競合・再編集・再読込のUXを定義する。
3. Windows11で実ファイルロック・ファイル置換・共有違反・ACL・電源断時の限界を確認する。
4. Step 3：Python `subprocess`連携、Node.exe同梱、LaunchファイルDrop連携、Studio回帰を実証する。

## 6. 成果物

- 更新したファイルのみを格納した差分ZIP。
- `foundation_rule_019`に従い、インシデントJSONに更新ファイル・テスト結果・残課題・AI回答を記録。
