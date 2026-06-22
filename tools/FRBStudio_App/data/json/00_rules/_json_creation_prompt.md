添付のData JSONから、FRB Studio / No-Code JSON Studio用のViewDef JSONを作成してください。


条件:

* frb_viewdef_generation_rules_review_data_v0_1.json に従う
* schema は _frb_view_def_schema_v0_9_chat_input_mapping.json を前提にする
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
* 詳細な思想は `frb_coding_constraints_review_data_v0_3.json` と `frb_studio_foundation_review_data_v0_1.json` を参照する。

<!-- change_history: 2026-06-22 v0.12-rules-update-reporting-policy-redo / AI更新ファイル記録・インシデント回答記録を、専用項目追加ではなくテキスト文章中心で残す実務指示へ修正 -->

