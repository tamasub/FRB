# Studio Change Core｜studio_work_0269 Step 1 調査・契約案

- phase: `studio-external-changeset-core-v0_1`
- 対象ソース: `FRBStudio_App20261101_185136.zip`（2026-11-01 添付）
- 確認種別: 静的コード調査／Node.js実行確認／既存Nodeテスト
- 今回の範囲: Step 1 の調査・契約整理。Core・CLI・保存方式の**実装は未着手**。

## 1. 確認できた既存責務

| 責務 | ソース／証拠 | 現状 | Step 2 での扱い |
|---|---|---|---|
| 単一Field検証 | `wwwroot/js/services/definition/definition_value_validator.js` | DOM不要、グローバル公開 | 既存ロジック再利用候補 |
| 定義から契約導出 | `wwwroot/js/services/definition/field_contract_resolver.js` | DOM不要、グローバル公開 | 再利用候補 |
| 行のField Definition検証 | `wwwroot/js/services/definition/runtime_field_definition_validation.js` | ViewDefと定義・Registryを引数で受理 | 再利用候補 |
| Cross Field検証 | `cross_field_verification_service.js`、`cross_field_relation_evaluator.js`（ともに`wwwroot/js/services/definition/`） | 主にDefinition検証の資産 | 実行時の適用範囲は要確認 |
| Tree整合性・順序 | `wwwroot/js/runtime/tree_model.js` | `build`/`move`/`place`/`reorder`。CommonJSでテスト可能 | Tree全体検証の再利用候補 |
| Tree Drop・Add | `wwwroot/js/runtime/tree_file_drop.js` 21–35行 | 完成レコードを画面`currentRows`へ追加。位置指定で既存行も並べ替え | 要求生成の参考。Coreへの直接移植はしない |
| ID採番 | `wwwroot/js/renderers/grid_detail.js` 950–957、1141–1151行 | Treeは`crypto.randomUUID()`。一般Gridは`no`や`keyField`を処理 | ID規則の共通化が必要 |
| F12／詳細反映 | `wwwroot/js/runtime/detail_save.js` 397–408、467–509行 | Field Definition検証後に`currentRows`へ反映。画面依存 | UI連携は入口を分離する |
| UI保存 | `wwwroot/js/runtime/detail_save.js` 746–861行 | `sourceData`をJSON化し、`currentDataApiUrl`へPOST。VirtualData更新では別POSTもある | 既存画面から共通の保存保証へ接続する必要 |
| WebView2のAPIアダプター | `wwwroot/js/core/native_host_bridge.js` 483–508行 | `/api/data/...` GETはテキスト読込、POSTはJSON整形→`file.writeText` | 共通保存・競合制御の接続点 |
| NativeShell保存 | `NativeShell/NativeCommandDispatcher.cs` 847–861行 | 許可されたWorkspaceパスに`File.WriteAllText` | CAS・原子的保存を別途設計 |
| Path許可 | `NativeShell/WorkspacePolicy.cs` 28–65行 | Workspace内パス＋許可ルート／ファイルで制限 | CLIでも同等の許可境界が必要 |

## 2. 実証したこと

- Node.js v22.16.0 で既存の定義系JSを**ソース変更なしで順序付きdynamic import**できた。
  - `definition_verification_common.js`、`field_contract_resolver.js`、`definition_value_validator.js`、`runtime_field_definition_validation.js`。
  - `FieldContractResolver`で既存Field Definitionを解決し、`DefinitionValueValidator`が必須項目の欠損を`REJECT / REQUIRED_MISSING`と判定。
  - この確認は**既存Service単体のNode利用可能性のみ**。End-to-endのChangeSet検証ではない。
- 既存テスト（`node --test tests/tree/tree_model.test.cjs tests/definition/cross_field_definition_test.test.mjs`）：**14/14 PASS**。
- `defs/launch/frb_launch_maintenance_view_def_v0_1.json`の`items_view`に`$.items`、`item_id`、`parent_item_id`、`page_id`、`sort_order`が`tree`定義として存在。
- **注意**：このLaunch ViewDefには`item_definition_ref`がない。現行`RuntimeFieldDefinitionValidationService`はField Definition未指定時に`SKIPPED`を返す。したがって「Nodeで既存検証を呼べる」だけではLaunchの全制約保証にならない。
- ZIP内には`NativeShell`はあるが、独立した.NET Minimal APIサーバー本体のソースは含まれない。そちらの実際の保存保証は未確認。
- ZIPに`node.exe`同梱はない。配布確認は未実施。

## 3. 現行実装と受入条件の差分

- **保存原子性**：`File.WriteAllText`は一時ファイル作成→同一ディレクトリ内置換を使っていない。途中失敗時の旧ファイル保持を保証できない。
- **競合検出**：POST JSON保存は読込時の版・ハッシュを送らず、保存直前の一致確認もない。同時変更の安全性を保証できない。
- **共通責務**：F12検証、Tree編集、UI保存、Native書込は分かれている。現状そのままではCLIとUIの同一保証を満たさない。
- **複数文書原子性**：VirtualDataのwriteBackは対象ごとにPOSTしている。複数ファイルの一括コミット保証は存在しない。
- **Expected Diff**：責務テストのExpected/Actual/Diff生成資産は存在するが、通常のJSON書込前の変更保証として共有されているわけではない。
- **外部ファイル**：Launch自身の設定JSONはStudio Workspace外に配置され得る。既存Workspace制限の無効化ではなく、明示的な許可対象の設計が必要。

## 4. ChangeSet v0.1 契約案（提案／未承認・未実装）

- `document_ref`：信頼済み設定で許可された対象ファイルの参照名。生の任意パスをCoreが自由に書かない。
- `base_sha256`：呼び出し元が読み取った基準文書の生バイトSHA-256。保存時に比較し、競合時は保存しない。
- `view_def`／`view_id`／`section_id`：読み込む承認済みViewDef、ビュー、対象Gridの識別子。
- `operations[]`：1つ以上の操作。初回は`add`のみ実行。
- `records[]`：呼び出し元が完成させたレコード（操作・配置メタ情報と分離）。
- `placement`：`group_id`／`parent_id`／`position`などの**汎用的な意味**。実フィールド名は`section.tree`から解決。
- `mode`：`dry_run`または`commit`。先に評価し、明示commitで保存する。
- `request_id`：同一要求の追跡・エラー対応用。冪等性保証は別途設計。

```json
{
  "schema_version": "studio_changeset_v0_1",
  "request_id": "external-add-001",
  "mode": "commit",
  "document_ref": "approved_launch_config",
  "base_sha256": "<呼び出し元が取得した基準文書のSHA-256>",
  "view_def": "launch/frb_launch_maintenance_view_def_v0_1.json",
  "view_id": "items_view",
  "operations": [
    {
      "operation": "add",
      "section_id": "items",
      "placement": { "group_id": "work", "parent_id": "folders", "position": "end" },
      "records": [
        { "title": "sample.txt", "item_kind": "command", "launch_actions": [{ "launch_action_type": "Open", "launch_target": "F:\\sample.txt" }] },
        { "title": "sample2.txt", "item_kind": "command", "launch_actions": [{ "launch_action_type": "Open", "launch_target": "F:\\sample2.txt" }] }
      ]
    }
  ]
}
```

- 上記の`group_id`／`parent_id`は契約の汎用名。値の例はLaunchが決めるもので、Coreの定数にはしない。
- `document_ref`の解決方法、入力レコードにIDがある場合の優先順位、配置指定の正式な表記はStep 2開始前に確定する。
- Update／Delete／Moveの操作名は予約候補。v0.1で要求された場合は**非対応として明示的に失敗**させる。
- 1 ChangeSetは**1文書だけ**をv0.1の保存単位とする。メイン＋明細が同一JSON内なら同じ文書に含められる。複数ファイル一括原子性は未対応と明記。

## 5. 期待する応答（案）

```json
{
  "schema_version": "studio_changeset_result_v0_1",
  "request_id": "external-add-001",
  "status": "COMMITTED",
  "saved": true,
  "base_sha256": "<旧文書SHA-256>",
  "new_sha256": "<保存後文書SHA-256>",
  "summary": { "added": 2, "changed_existing": 0 },
  "expected_diff": [],
  "actual_diff": [],
  "unexpected_diff": [],
  "errors": []
}
```

- 応答例のDiff配列は**書式未確定**。正常時もExpected/Actualは観測可能な変更内容を返し、常に空になるという意味ではない。
- ステータス候補：`PREVIEW`／`COMMITTED`／`REJECTED`／`CONFLICT`／`ERROR`。
- `REJECTED`、`CONFLICT`、`ERROR`の`commit`応答は`status`と`errors[]`を明示し、`saved=false`とする。
- Expectedには追加件数・対象パス・追加行の期待値と、許可する既存行順序変更のみを含める。
- 採番が必要なUUIDは、**適用前にCoreが採番し操作計画へ固定**。そのIDをExpectedとActualの双方で参照する。Actualの結果から事後注入してExpectedを捏造しない。

## 6. Step 2 の実装境界案

1. **受理**：CLIまたはStudio UIから同じChangeSet／文書Commit要求を受ける。
2. **安全な文書取得**：許可済み対象を取得し、基準ハッシュを確定する。
3. **定義解決**：`view_id`→Grid `section_id`→`dataPath`・`keyField`・`tree`を特定。必要なField Definition／Registryを明示的に読み込む。
4. **予定変更（Expected）**：変更要求・配置・採番済みIDから、変更を許可する箇所を宣言。
5. **Actualの作成**：元Dataの深いコピーへ複数Addを実行。Tree全体・関連定義を検証。未定義の業務制約は追加しない。
6. **Diff検証**：Before→Afterの全差分を算出し、Expectedと比較。不一致は保存禁止。
7. **Commit**：共同利用する保存アダプターでハッシュ再確認→同一対象への排他→一時ファイル作成→置換。どの失敗でも旧文書を残す。
8. **結果返却**：成功／拒否／競合、期待・実際・想定外差分、保存先とハッシュを構造化返却。

### 既存Studioとの統合について

- `Node CLI`だけに上記を実装しても、UIが従来の`/api/data` POST→`File.WriteAllText`を使い続ければ**共通保証にはならない**。
- Node CLIを共通実行体として、NativeShellからも同じCore・Commitアダプターを呼び出す案を優先調査する。
- 別の.NET Minimal APIサーバーはソース未提示のため、同一処理への接続は未確認。既存UIへの段階適用と回帰確認が必要。
- 既存UIの保存操作を無検証で一括置換せず、JSON Dataを対象とするスモールスコープから試す。
- 旧UIを残したまま外部CLIだけを完成と扱うことは**受入不可**。移行中は共通化未完了として記録する。

## 7. 未決・次の作業

1. `document_ref`の登録方法、Studio Workspace外へのアクセス許可、ファイル共有・排他方法。
2. 使用中のNativeShell以外の.NET Minimal API実装確認（必要ならソース取得）。
3. 現行UIと同一検証範囲の明確化。Field Definition未指定時の扱い、Tree検証、ViewDef由来の必須／型チェック。
4. `group_id`／`parent_id`と`tree`定義の対応、ID採番時点、既存行の`sort_order`変更の許可範囲。
5. Expected Diffの独立性・UUID固定と、実際に通すDiff形式の確定。
6. ファイルロック／CAS／一時ファイル置換のWindows実機テスト。GitHub Pagesの読み取り専用動作との分離。
7. Python `subprocess`、`node.exe`同梱、Windows実行制限・ランタイム更新・配布ライセンスの確認。
8. Step 2：複数件Add、異常時無変更、競合、UI経由とCLI経由の共通保証を実コードで実証する。

## 8. 確認状態

- **済**：指定ZIP解析／実コード静的確認／JS ServiceのNode読み込み実証／既存テスト14件。
- **未実施**：ChangeSet実装／Expected–Actual照合／原子的保存／UI接続／Python呼び出し／Node同梱／dotnetビルド／Windows実機確認。
- **判断**：Step 1は調査完了。Step 2以降は未着手。契約はレビュー候補であって承認済み仕様ではない。
