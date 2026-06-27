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

