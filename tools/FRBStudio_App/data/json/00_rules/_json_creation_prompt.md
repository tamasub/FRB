添付のData JSONから、FRB Studio / No-Code JSON Studio用のViewDef JSONを作成してください。


条件:

* frb_viewdef_generation_rules_data_v0_1.json に従う
* schema は frb_view_def_schema_v0_9.json を前提にする
* Runtime内のData固定名を前提にしない
* field / caption / type を必ず入れる
* ルートのメタ情報は header form
* 主配列は main grid
* 配列履歴は objectArray
* 会話表示が必要な場合は chat + edit.messages
* Markdown AI貼り付け用が必要な場合は section.markdown.aiPrompt
* 主役Actionが必要な場合は toolbar.executeButton
* 出力は JSON ファイルとしてそのまま保存できる完全なJSONのみ

---

## v0.12 追加ルール: AI作業対象ファイル記録 / インシデント回答記録

ルール更新・Data更新を伴う作業の場合は、次を守る。

* 対象インシデントの `target_files` を確認し、予定外のファイルへ作業範囲を広げない。
* root `data/` / `defs/` は一律変更禁止ではない。作業目的に必要な場合は更新してよい。
* AIが更新したファイル、変更理由、対応結果は、該当インシデントJSONの `latest_ai_response` / `discussion_history` / `change_history` などへ、まずはテキスト文章で残す。
* `wwwroot/data` / `wwwroot/defs` は公開用静的領域として扱うため、明示依頼がない限り更新しない。
* 完了報告は会話上だけで終わらせず、該当インシデントJSONにも残す。
* 詳細な思想は `frb_coding_constraints_data_v0_3.json` と `frb_foundation_rules_data_v0_1.json` を参照する。

<!-- change_history: 2026-06-22 v0.12-rules-update-reporting-policy-redo / AI更新ファイル記録・インシデント回答記録を、専用項目追加ではなくテキスト文章中心で残す実務指示へ修正 -->

---
<!-- change_history: 2026-06-26 v0.14.0 / ViewDef安定ファイル名、確認種別明示、最新ソース確認の実務指示を追加 -->

## v0.14.0 AI作業チェック

- 既存ViewDef / DefView を改善する場合、原則としてファイル名を変更せず、同じ相対パス・同じファイル名で更新する。
- 新しいViewDefファイル名を作成する場合は、ユーザーの明示指示、互換性を切る理由、または並行運用理由をインシデントへ記録し、Data JSON側の `view_def` 参照更新も確認する。
- AIが「確認した」と報告する場合は、JSON parse / 静的確認 / build / run / スクショ / Playwright / 推定確認 / ユーザー実機確認待ちを区別する。
- C# / .NET の実行確認は必須ではないが、実施有無と未実施理由を作業記録へ残す。
- 最新ソースを実ファイルとして確認できない場合、会話文脈だけで実装修正しない。

## v0.14.1 Data JSON内ViewDef候補

Data JSONに `view_def_candidates` がある場合、AIはそのDataで利用可能なViewDef候補として扱う。通常改修でViewDefファイル名を勝手に変えない。複数ViewDefを許可したい場合は、Data JSON側に `view_def_candidates` を明示し、既定ViewDefは `view_def` として残す。

<!-- change_history: 2026-06-26 v0.14.1 / Data JSON内ViewDef候補契約を追加 -->


---
<!-- change_history: 2026-06-27 v0.14.13 / 共通化優先・archive退避・ルール/ViewDefファイル名維持の実務指示を追加 -->

## v0.14.13 共通化・archive・ファイル名維持チェック

- 共通化できる構造・ViewDef・Diff形式・出力形式は、まず共通化を検討する。
- ただし、共通化により将来の拡張性・可読性・保守性が苦しくなる場合は、AIが独断せず人間へ相談する。
- 古いデータ・不要データ・移行済み旧パスはactive領域から外し、ルート `_archive/{削除日時}/` へ元の相対パスが追える形で退避する。
- ルール系ファイルおよびViewDefファイルを修正する場合は、原則として同じファイル名で更新する。
- 新しい正本名を作る必要がある場合は、人間へ確認し、理由・影響範囲・参照更新をインシデントJSONに残す。

---
<!-- change_history: 2026-06-27 v0.14.15 / Test Folder・Archive・Runtime生成物隔離と、実行言語ごとのテストコード共通化方針を追加 -->

## v0.14.15 Test Folder / Archive / Runtime生成物チェック

- テスト証跡の正本は `data/json/03_tests/{domain}/{suite_id}/` 配下へ置く。
- 標準サブフォルダーは `test_patterns/`, `expected/`, `actual/`, `diff/`, `relations/`, `summary/`, `notes/` とする。
- テストコードは `tests/` 配下へ置き、Expected / Actual / Diff の正本を `tests/` に置かない。
- テストコードは、Node.js / Playwright などコード実行言語ごとに1つの共通ランナーへ寄せることを基本とする。
- 新しいテストケースは、まず Test Pattern JSON / Expected JSON の追加で対応し、ケースごとにテストコードファイルを増やさない。
- 過剰共通化により将来苦しくなる場合は、人間へ相談する。
- runtime一時生成物は `tests/.runtime/` 配下へ隔離し、root直下に `playwright-report/`, `test-results/`, `test_results/`, `tests_screen_state/` を生やさない。
- 成果物ZIPには `node_modules/`, `playwright-report/`, `test-results/`, `test_results/`, `tests/.runtime/`, `tests_screen_state/` を含めない。
- 旧パス・移行済みデータはactiveから削除し、必要に応じて `_archive/{削除日時}/` へ退避する。ただしruntime生成物は再生成可能なので原則archive対象外とする。


---
<!-- change_history: 2026-06-27 v0.14.16 / Diff Result共通フォーマット生成チェックを追加 -->

## v0.14.16 Diff Result Common Formatチェック

- diff.jsonを生成・修正する場合は、`schema_version: diff_result_v0_1` / `document_type: diff_result` を標準とする。
- 上部サマリは `domain`, `diff_kind`, `test_id`, `status`, `resultLabel`, `summary`, `total`, `passCount`, `failCount`, `failedCount`, `failedCheckIds`, `firstFailure` を基本とする。
- 明細判定フィールドは `checks[].pass` を正本とし、`passed` / `ok` / `result` を新規標準化しない。
- ドメイン固有情報は追加項目として保持してよいが、共通項目の意味を壊さない。過剰共通化で苦しくなる場合は人間へ相談する。
- 詳細ルールは `frb_diff_result_format_rules_data_v0_1.json` を参照する。
---

## v0.14.17 追加ルール: 共通ViewDef優先・同名更新・pass標準化

ViewDef JSONを生成・修正する場合は、次を守る。

* 複数ドメインで同じ構造を持てるものは、個別ViewDefを増やす前に共通ViewDef化を検討する。
* 共通化で読みづらくなる、ドメイン固有の意味が薄まる、将来苦しくなると判断される場合は、人間に相談する。
* 既存ViewDefを修正する場合は、原則としてファイル名を変更しない。Data JSONの `view_def` 参照、URL起動、インベントリ、過去インシデントを壊さないため。
* 新しい正本世代や非互換ViewDefを作る必要がある場合は、人間確認後に行い、影響範囲をインシデントJSONへ記録する。
* Diff Result系ViewDefでは、明細判定フィールドは `checks[].pass` を標準とする。`passed` / `ok` / `result` を新規標準化しない。
* 詳細な思想は `frb_viewdef_generation_rules_data_v0_1.json` の `viewdef_rule_25` 系を参照する。

<!-- change_history: 2026-06-27 v0.14.17 / 共通ViewDef優先・既存ViewDefファイル名維持・Diff系checks[].pass標準化の実務指示を追加 -->


---

## v0.14.18 追加ルール: Delivery / Cleanup / ZIP安全返却チェック

AIが成果物ZIPを返却する場合は、返却前に次を確認する。

* `node_modules/`, `playwright-report/`, `test-results/`, `test_results/`, `tests/.runtime/`, `tests_screen_state/` をZIPへ含めない。
* `tests/tools/cleanup_runtime_artifacts.ps1` がある場合は、必要に応じてruntime生成物の掃除に使う。
* runtime生成物は再生成可能なため、原則として `_archive` へ退避せず、削除・除外する。
* Expected / Actual / Diff / Test Patternなどの証跡正本は `data/json/03_tests/` に置き、runtime生成物と混同しない。
* ZIP作成後、生成物除外リストが混入していないこと、Windowsで問題になりやすい長大パスがないことを確認する。
* 更新済みインシデントJSONを `data/json/01_main/` に含め、`latest_ai_response` / `discussion_history` / `change_history` / `actual_updated_files` に作業結果を残す。

ZIP作成時の除外例:

```bash
zip -qr OUT.zip . \
  -x 'node_modules/*' 'playwright-report/*' 'test-results/*' 'test_results/*' 'tests/.runtime/*' 'tests_screen_state/*'
```

<!-- change_history: 2026-06-27 v0.14.18 / 成果物ZIP安全返却・runtime生成物除外・Windows長大パス確認の実務指示を追加 -->

---

## v0.14.32 追加ルール: ヘッダー基本情報・検索項目コンパクト表示チェック

ViewDef JSONを生成・修正する場合は、次を守る。

* ヘッダー部・基本情報は、1行に収まる範囲の短い識別情報・状態・分類項目に絞る。
* ヘッダー部・基本情報のマルチテキストボックス、長文textarea、Markdown本文欄は、原則として画面表示オフにする。
* `Owner` / `owner` 相当項目は、ヘッダー部・基本情報では表示オフを基本とする。ただしRuntime固定名として特別扱いしない。
* 長文の目的・背景・対象範囲・リスク・確認観点・AI回答などは、必要に応じて `detailBody` readable card、Markdown表示、chat、objectArray 側へ寄せる。
* 画面検索項目部分は、必要項目に絞り、縦マージンを調整して、Grid表示領域を過度に圧迫しない。
* 詳細な思想は `frb_viewdef_generation_rules_data_v0_1.json` の `viewdef_rule_26` 系を参照する。

<!-- change_history: 2026-06-27 v0.14.32 / ヘッダー基本情報を1行・短文中心にし、長文欄/Owner非表示、検索項目コンパクト表示の実務指示を追加 -->

---

## v0.18.68 追加ルール: 標準検索ViewDef / Canonical Search Projection

ViewDef JSONを新規生成・修正する場合、検索Fieldを独立したSearch Sectionへ複製しない。

* 検索対象は、Main Grid側のCanonical Field Definitionに `search.visible=true` を設定する。
* 標準OperatorはField type / Validation Typeから導出するため、通常は `search.operator` を書かない。
* `id: search` のSectionを検索Field定義の置き場として新規生成しない。
* Fieldを持たない空のSearch Sectionも新規生成しない。
* Legacy Search Sectionを移行する場合は、同一 `dataPath` / 同一 `field` のCanonical Fieldへ検索意図を転記してから重複定義を削除する。
* LegacyとCanonicalの設定が食い違う場合は全件自動変換せず、人間確認または代表ViewDefによる段階移行を優先する。
* 詳細契約は `frb_viewdef_generation_rules_data_v0_1.json` の `viewdef_rule_36` を参照する。

標準例:

```json
{
  "field": "updated_at",
  "type": "datetime",
  "grid": { "visible": true },
  "edit": { "visible": true },
  "search": { "visible": true }
}
```

<!-- change_history: 2026-08-16 v0.18.68 / Search Section二重Field定義を新規生成せず、Canonical Fieldのsearch.visibleから検索UIをProjectionする実務指示を追加 -->

