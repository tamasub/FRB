# v0.14.35 defs/rules ViewDef Visible調整レポート

## 目的

`frb_viewdef_generation_rules_data_v0_1.json` の `viewdef_rule_26` 系に基づき、`defs/rules` 配下のViewDefについて、ヘッダー基本情報と検索項目の visible を調整した。

## 適用方針

- ヘッダー部・基本情報は、短い名札として1行に収まる範囲へ絞る。
- ヘッダー部・基本情報の textarea / 長文欄は `edit.visible=false` を基本とする。
- ヘッダー部・基本情報の Owner は `edit.visible=false` を基本とする。
- 検索項目は、長文textarea検索欄や過剰な検索項目を `search.visible=false` にしてコンパクト化する。
- `wwwroot/defs` は更新していない。今回の対象は root `defs/rules` のみ。

## 更新ファイル

- `defs/rules/ai_constraint_grouped_view_def_v0_6_footer_chat.json`
- `defs/rules/chatgpt/chatgpt_context_relation_graph_view_def_v0_1.json`
- `defs/rules/chatgpt/chatgpt_raw_keyword_activation_view_def_v0_1.json`
- `defs/rules/chatgpt/chatgpt_sentence_prime_map_view_def_v0_1.json`
- `defs/rules/chatgpt/chatgpt_shared_context_view_def_v0_1.json`
- `defs/rules/frb_view_def_schema_review_view_def_v0_1.json`
- `defs/rules/rule_review_common_view_def_v0_3.json`
- `defs/rules/studio_work_incident_view_def_v0_4_readable_cards_confirm_status_markdown_preview.json`
- `defs/rules/tmp/rule_review_common_view_def_v0_1.json`
- `defs/rules/tmp/rule_review_common_view_def_v0_2_editable_review_target.json`

## 変更詳細

| file | section | field | caption | area | before | after | reason |
|---|---|---|---|---|---:|---:|---|
| `defs/rules/ai_constraint_grouped_view_def_v0_6_footer_chat.json` | `header` | `aggregation_policy` | 集約方針 | `edit` | `True` | `False` | `header_textarea_hidden_by_rule_26_02` |
| `defs/rules/ai_constraint_grouped_view_def_v0_6_footer_chat.json` | `constraint_groups` | `summary` | 集約サマリ | `search` | `True` | `False` | `search_visible_reduced_by_rule_26_04` |
| `defs/rules/ai_constraint_grouped_view_def_v0_6_footer_chat.json` | `constraint_groups` | `scope` | 対象範囲 | `search` | `True` | `False` | `search_visible_reduced_by_rule_26_04` |
| `defs/rules/ai_constraint_grouped_view_def_v0_6_footer_chat.json` | `constraint_groups` | `notes` | グループメモ | `search` | `True` | `False` | `search_visible_reduced_by_rule_26_04` |
| `defs/rules/ai_constraint_grouped_view_def_v0_6_footer_chat.json` | `constraint_groups` | `user_comment` | 俺コメント | `search` | `True` | `False` | `search_visible_reduced_by_rule_26_04` |
| `defs/rules/ai_constraint_grouped_view_def_v0_6_footer_chat.json` | `constraint_groups` | `ai_response` | AI回答 | `search` | `True` | `False` | `search_visible_reduced_by_rule_26_04` |
| `defs/rules/ai_constraint_grouped_view_def_v0_6_footer_chat.json` | `constraint_groups` | `user_reply` | 俺追加回答 | `search` | `True` | `False` | `search_visible_reduced_by_rule_26_04` |
| `defs/rules/ai_constraint_grouped_view_def_v0_6_footer_chat.json` | `constraint_groups` | `ai_followup_response` | AI再回答 | `search` | `True` | `False` | `search_visible_reduced_by_rule_26_04` |
| `defs/rules/chatgpt/chatgpt_context_relation_graph_view_def_v0_1.json` | `meta` | `purpose` | 目的 | `edit` | `True` | `False` | `header_textarea_hidden_by_rule_26_02` |
| `defs/rules/chatgpt/chatgpt_context_relation_graph_view_def_v0_1.json` | `meta` | `main_question` | 主問い | `edit` | `True` | `False` | `header_textarea_hidden_by_rule_26_02` |
| `defs/rules/chatgpt/chatgpt_context_relation_graph_view_def_v0_1.json` | `meta` | `design_note` | 設計メモ | `edit` | `True` | `False` | `header_textarea_hidden_by_rule_26_02` |
| `defs/rules/chatgpt/chatgpt_raw_keyword_activation_view_def_v0_1.json` | `meta` | `purpose` | Purpose | `edit` | `True` | `False` | `header_textarea_hidden_by_rule_26_02` |
| `defs/rules/chatgpt/chatgpt_raw_keyword_activation_view_def_v0_1.json` | `meta` | `constraint` | Constraint | `edit` | `True` | `False` | `header_textarea_hidden_by_rule_26_02` |
| `defs/rules/chatgpt/chatgpt_sentence_prime_map_view_def_v0_1.json` | `meta` | `purpose` | Purpose | `edit` | `True` | `False` | `header_textarea_hidden_by_rule_26_02` |
| `defs/rules/chatgpt/chatgpt_sentence_prime_map_view_def_v0_1.json` | `meta` | `expected_win_condition` | 勝ち条件 | `edit` | `True` | `False` | `header_textarea_hidden_by_rule_26_02` |
| `defs/rules/chatgpt/chatgpt_sentence_prime_map_view_def_v0_1.json` | `meta` | `warning` | Warning | `edit` | `True` | `False` | `header_textarea_hidden_by_rule_26_02` |
| `defs/rules/chatgpt/chatgpt_sentence_prime_map_view_def_v0_1.json` | `markdown_preview` | `markdown_preview` | Markdown Preview | `edit` | `True` | `False` | `header_textarea_hidden_by_rule_26_02` |
| `defs/rules/chatgpt/chatgpt_shared_context_view_def_v0_1.json` | `context_meta` | `purpose` | 目的 | `edit` | `True` | `False` | `header_textarea_hidden_by_rule_26_02` |
| `defs/rules/chatgpt/chatgpt_shared_context_view_def_v0_1.json` | `context_meta` | `current_one_line_summary` | 一言まとめ | `edit` | `True` | `False` | `header_textarea_hidden_by_rule_26_02` |
| `defs/rules/chatgpt/chatgpt_shared_context_view_def_v0_1.json` | `core_themes` | `summary` | 要約 | `search` | `True` | `False` | `textarea_search_hidden_by_rule_26_04` |
| `defs/rules/chatgpt/chatgpt_shared_context_view_def_v0_1.json` | `assistant_expectations` | `summary` | 要約 | `search` | `True` | `False` | `textarea_search_hidden_by_rule_26_04` |
| `defs/rules/chatgpt/chatgpt_shared_context_view_def_v0_1.json` | `cultures` | `summary` | 要約 | `search` | `True` | `False` | `textarea_search_hidden_by_rule_26_04` |
| `defs/rules/chatgpt/chatgpt_shared_context_view_def_v0_1.json` | `avoid_misalignments` | `misalignment` | ズレ | `search` | `True` | `False` | `textarea_search_hidden_by_rule_26_04` |
| `defs/rules/chatgpt/chatgpt_shared_context_view_def_v0_1.json` | `avoid_misalignments` | `better_direction` | より良い方向 | `search` | `True` | `False` | `textarea_search_hidden_by_rule_26_04` |
| `defs/rules/chatgpt/chatgpt_shared_context_view_def_v0_1.json` | `relations` | `note` | メモ | `search` | `True` | `False` | `textarea_search_hidden_by_rule_26_04` |
| `defs/rules/chatgpt/chatgpt_shared_context_view_def_v0_1.json` | `contextdef_candidates` | `reason` | 理由 | `search` | `True` | `False` | `textarea_search_hidden_by_rule_26_04` |
| `defs/rules/frb_view_def_schema_review_view_def_v0_1.json` | `header` | `document_type` | Document Type | `edit` | `True` | `False` | `header_one_line_policy` |
| `defs/rules/frb_view_def_schema_review_view_def_v0_1.json` | `header` | `source_schema_id` | Schema ID | `edit` | `True` | `False` | `header_one_line_policy` |
| `defs/rules/frb_view_def_schema_review_view_def_v0_1.json` | `header` | `source_schema_title` | Schema Title | `edit` | `True` | `False` | `header_one_line_policy` |
| `defs/rules/frb_view_def_schema_review_view_def_v0_1.json` | `header` | `source_schema_draft` | JSON Schema Draft | `edit` | `True` | `False` | `header_one_line_policy` |
| `defs/rules/frb_view_def_schema_review_view_def_v0_1.json` | `header` | `generated_at` | 生成日時 | `edit` | `True` | `False` | `header_one_line_policy` |
| `defs/rules/frb_view_def_schema_review_view_def_v0_1.json` | `header` | `defs_count` | $defs数 | `edit` | `True` | `False` | `header_one_line_policy` |
| `defs/rules/frb_view_def_schema_review_view_def_v0_1.json` | `header` | `root_properties_count` | Root properties数 | `edit` | `True` | `False` | `header_one_line_policy` |
| `defs/rules/frb_view_def_schema_review_view_def_v0_1.json` | `header` | `definition_property_count` | Def property数 | `edit` | `True` | `False` | `header_one_line_policy` |
| `defs/rules/frb_view_def_schema_review_view_def_v0_1.json` | `header` | `source_schema_description` | Schema説明 | `edit` | `True` | `False` | `header_textarea_hidden_by_rule_26_02` |
| `defs/rules/frb_view_def_schema_review_view_def_v0_1.json` | `header` | `conversion_note` | 変換メモ | `edit` | `True` | `False` | `header_textarea_hidden_by_rule_26_02` |
| `defs/rules/frb_view_def_schema_review_view_def_v0_1.json` | `header` | `review_policy` | レビュー方針 | `edit` | `True` | `False` | `header_textarea_hidden_by_rule_26_02` |
| `defs/rules/frb_view_def_schema_review_view_def_v0_1.json` | `header` | `viewing_policy.data_json_role` | Data JSONの役割 | `edit` | `True` | `False` | `header_one_line_policy` |
| `defs/rules/frb_view_def_schema_review_view_def_v0_1.json` | `header` | `viewing_policy.view_def_role` | ViewDefの役割 | `edit` | `True` | `False` | `header_one_line_policy` |
| `defs/rules/frb_view_def_schema_review_view_def_v0_1.json` | `header` | `viewing_policy.source_schema_role` | Source Schemaの役割 | `edit` | `True` | `False` | `header_one_line_policy` |
| `defs/rules/frb_view_def_schema_review_view_def_v0_1.json` | `schema_items` | `type_summary` | 型概要 | `search` | `True` | `False` | `search_visible_reduced_by_rule_26_04` |
| `defs/rules/frb_view_def_schema_review_view_def_v0_1.json` | `schema_items` | `ref` | 参照 | `search` | `True` | `False` | `search_visible_reduced_by_rule_26_04` |
| `defs/rules/frb_view_def_schema_review_view_def_v0_1.json` | `schema_items` | `enum_summary` | Enum | `search` | `True` | `False` | `search_visible_reduced_by_rule_26_04` |
| `defs/rules/frb_view_def_schema_review_view_def_v0_1.json` | `schema_items` | `description` | 説明 | `search` | `True` | `False` | `search_visible_reduced_by_rule_26_04` |
| `defs/rules/frb_view_def_schema_review_view_def_v0_1.json` | `schema_items` | `raw_schema_json` | Raw Schema JSON | `search` | `True` | `False` | `search_visible_reduced_by_rule_26_04` |
| `defs/rules/frb_view_def_schema_review_view_def_v0_1.json` | `schema_items` | `user_comment` | 人間コメント | `search` | `True` | `False` | `search_visible_reduced_by_rule_26_04` |
| `defs/rules/frb_view_def_schema_review_view_def_v0_1.json` | `schema_items` | `ai_response` | AI回答 | `search` | `True` | `False` | `search_visible_reduced_by_rule_26_04` |
| `defs/rules/frb_view_def_schema_review_view_def_v0_1.json` | `schema_items` | `user_reply` | 人間追加コメント | `search` | `True` | `False` | `search_visible_reduced_by_rule_26_04` |
| `defs/rules/frb_view_def_schema_review_view_def_v0_1.json` | `schema_items` | `ai_followup_response` | AI再回答 | `search` | `True` | `False` | `search_visible_reduced_by_rule_26_04` |
| `defs/rules/frb_view_def_schema_review_view_def_v0_1.json` | `schema_items` | `notes` | メモ | `search` | `True` | `False` | `search_visible_reduced_by_rule_26_04` |
| `defs/rules/rule_review_common_view_def_v0_3.json` | `header` | `document_type` | Document Type | `edit` | `True` | `False` | `header_one_line_policy` |
| `defs/rules/rule_review_common_view_def_v0_3.json` | `header` | `source_version` | Source Version | `edit` | `True` | `False` | `header_one_line_policy` |
| `defs/rules/rule_review_common_view_def_v0_3.json` | `header` | `introduced_in` | Introduced In | `edit` | `True` | `False` | `header_one_line_policy` |
| `defs/rules/rule_review_common_view_def_v0_3.json` | `header` | `generated_at` | 生成日時 | `edit` | `True` | `False` | `header_one_line_policy` |
| `defs/rules/rule_review_common_view_def_v0_3.json` | `header` | `approved_count` | 承認済み数 | `edit` | `True` | `False` | `header_one_line_policy` |
| `defs/rules/rule_review_common_view_def_v0_3.json` | `header` | `source_declared_view_def_schema` | 元MD記載Schema | `edit` | `True` | `False` | `header_one_line_policy` |
| `defs/rules/rule_review_common_view_def_v0_3.json` | `header` | `source_schema_snapshot.title` | 添付Schema Snapshot | `edit` | `True` | `False` | `header_one_line_policy` |
| `defs/rules/rule_review_common_view_def_v0_3.json` | `header` | `viewing_policy.data_json_role` | Data JSONの役割 | `edit` | `True` | `False` | `header_one_line_policy` |
| `defs/rules/rule_review_common_view_def_v0_3.json` | `header` | `viewing_policy.view_def_role` | ViewDefの役割 | `edit` | `True` | `False` | `header_one_line_policy` |
| `defs/rules/rule_review_common_view_def_v0_3.json` | `header` | `viewing_policy.markdown_role` | Markdownの役割 | `edit` | `True` | `False` | `header_one_line_policy` |
| `defs/rules/rule_review_common_view_def_v0_3.json` | `header` | `approval_policy` | 承認方針 | `edit` | `True` | `False` | `header_textarea_hidden_by_rule_26_02` |
| `defs/rules/rule_review_common_view_def_v0_3.json` | `header` | `conversion_note` | 変換メモ | `edit` | `True` | `False` | `header_textarea_hidden_by_rule_26_02` |
| `defs/rules/rule_review_common_view_def_v0_3.json` | `header` | `preamble` | 前文 / この文書の目的 | `edit` | `True` | `False` | `header_textarea_hidden_by_rule_26_02` |
| `defs/rules/rule_review_common_view_def_v0_3.json` | `header` | `change_history_policy` | 変更履歴方針 | `edit` | `True` | `False` | `header_textarea_hidden_by_rule_26_02` |
| `defs/rules/rule_review_common_view_def_v0_3.json` | `rules` | `summary` | 要約 | `search` | `True` | `False` | `search_visible_reduced_by_rule_26_04` |
| `defs/rules/rule_review_common_view_def_v0_3.json` | `rules` | `body` | ルール本文 | `search` | `True` | `False` | `search_visible_reduced_by_rule_26_04` |
| `defs/rules/rule_review_common_view_def_v0_3.json` | `rules` | `source_heading` | 見出し | `search` | `True` | `False` | `search_visible_reduced_by_rule_26_04` |
| `defs/rules/rule_review_common_view_def_v0_3.json` | `rules` | `source_line_start` | 元行 | `search` | `True` | `False` | `search_visible_reduced_by_rule_26_04` |
| `defs/rules/rule_review_common_view_def_v0_3.json` | `rules` | `source_md_file` | 元MD | `search` | `True` | `False` | `search_visible_reduced_by_rule_26_04` |
| `defs/rules/rule_review_common_view_def_v0_3.json` | `rules` | `introduced_in` | 導入Ver. | `search` | `True` | `False` | `search_visible_reduced_by_rule_26_04` |
| `defs/rules/rule_review_common_view_def_v0_3.json` | `rules` | `ceremony_phrase` | 確認メッセージ | `search` | `True` | `False` | `search_visible_reduced_by_rule_26_04` |
| `defs/rules/rule_review_common_view_def_v0_3.json` | `rules` | `user_comment` | 人間コメント | `search` | `True` | `False` | `search_visible_reduced_by_rule_26_04` |
| `defs/rules/rule_review_common_view_def_v0_3.json` | `rules` | `ai_response` | AI回答 | `search` | `True` | `False` | `search_visible_reduced_by_rule_26_04` |
| `defs/rules/rule_review_common_view_def_v0_3.json` | `rules` | `user_reply` | 人間追加コメント | `search` | `True` | `False` | `search_visible_reduced_by_rule_26_04` |
| `defs/rules/rule_review_common_view_def_v0_3.json` | `rules` | `ai_followup_response` | AI再回答 | `search` | `True` | `False` | `search_visible_reduced_by_rule_26_04` |
| `defs/rules/rule_review_common_view_def_v0_3.json` | `rules` | `approved_by` | 承認者 | `search` | `True` | `False` | `search_visible_reduced_by_rule_26_04` |
| `defs/rules/rule_review_common_view_def_v0_3.json` | `rules` | `approved_at` | 承認日時 | `search` | `True` | `False` | `search_visible_reduced_by_rule_26_04` |
| `defs/rules/rule_review_common_view_def_v0_3.json` | `rules` | `notes` | メモ | `search` | `True` | `False` | `search_visible_reduced_by_rule_26_04` |
| `defs/rules/studio_work_incident_view_def_v0_4_readable_cards_confirm_status_markdown_preview.json` | `header` | `owner` | Owner | `edit` | `True` | `False` | `header_owner_hidden_by_rule_26_03` |
| `defs/rules/studio_work_incident_view_def_v0_4_readable_cards_confirm_status_markdown_preview.json` | `header` | `purpose` | 目的 | `edit` | `True` | `False` | `header_textarea_hidden_by_rule_26_02` |
| `defs/rules/studio_work_incident_view_def_v0_4_readable_cards_confirm_status_markdown_preview.json` | `header` | `operation_policy` | 運用方針 | `edit` | `True` | `False` | `header_textarea_hidden_by_rule_26_02` |
| `defs/rules/studio_work_incident_view_def_v0_4_readable_cards_confirm_status_markdown_preview.json` | `header` | `standard_field_policy` | 標準メタフィールド方針 | `edit` | `True` | `False` | `header_textarea_hidden_by_rule_26_02` |
| `defs/rules/studio_work_incident_view_def_v0_4_readable_cards_confirm_status_markdown_preview.json` | `work_items` | `target_files` | 対象ファイル | `search` | `True` | `False` | `search_visible_reduced_by_rule_26_04` |
| `defs/rules/studio_work_incident_view_def_v0_4_readable_cards_confirm_status_markdown_preview.json` | `work_items` | `objective` | 目的 | `search` | `True` | `False` | `search_visible_reduced_by_rule_26_04` |
| `defs/rules/studio_work_incident_view_def_v0_4_readable_cards_confirm_status_markdown_preview.json` | `work_items` | `background` | 背景 | `search` | `True` | `False` | `search_visible_reduced_by_rule_26_04` |
| `defs/rules/studio_work_incident_view_def_v0_4_readable_cards_confirm_status_markdown_preview.json` | `work_items` | `scope` | 対象範囲 | `search` | `True` | `False` | `search_visible_reduced_by_rule_26_04` |
| `defs/rules/studio_work_incident_view_def_v0_4_readable_cards_confirm_status_markdown_preview.json` | `work_items` | `out_of_scope` | 対象外 | `search` | `True` | `False` | `search_visible_reduced_by_rule_26_04` |
| `defs/rules/studio_work_incident_view_def_v0_4_readable_cards_confirm_status_markdown_preview.json` | `work_items` | `fixed_name_policy` | 固定名方針 | `search` | `True` | `False` | `search_visible_reduced_by_rule_26_04` |
| `defs/rules/studio_work_incident_view_def_v0_4_readable_cards_confirm_status_markdown_preview.json` | `work_items` | `module_policy` | module化方針 | `search` | `True` | `False` | `search_visible_reduced_by_rule_26_04` |
| `defs/rules/studio_work_incident_view_def_v0_4_readable_cards_confirm_status_markdown_preview.json` | `work_items` | `expected_outputs` | 成果物 | `search` | `True` | `False` | `search_visible_reduced_by_rule_26_04` |
| `defs/rules/studio_work_incident_view_def_v0_4_readable_cards_confirm_status_markdown_preview.json` | `work_items` | `risk` | リスク | `search` | `True` | `False` | `search_visible_reduced_by_rule_26_04` |
| `defs/rules/studio_work_incident_view_def_v0_4_readable_cards_confirm_status_markdown_preview.json` | `work_items` | `test_points` | 確認観点 | `search` | `True` | `False` | `search_visible_reduced_by_rule_26_04` |
| `defs/rules/studio_work_incident_view_def_v0_4_readable_cards_confirm_status_markdown_preview.json` | `work_items` | `user_request` | 依頼 / 方針 | `search` | `True` | `False` | `search_visible_reduced_by_rule_26_04` |
| `defs/rules/studio_work_incident_view_def_v0_4_readable_cards_confirm_status_markdown_preview.json` | `work_items` | `ai_response` | AI整理 | `search` | `True` | `False` | `search_visible_reduced_by_rule_26_04` |
| `defs/rules/studio_work_incident_view_def_v0_4_readable_cards_confirm_status_markdown_preview.json` | `work_items` | `latest_user_comment` | 追加コメント | `search` | `True` | `False` | `search_visible_reduced_by_rule_26_04` |
| `defs/rules/studio_work_incident_view_def_v0_4_readable_cards_confirm_status_markdown_preview.json` | `work_items` | `latest_ai_response` | AI追加回答 | `search` | `True` | `False` | `search_visible_reduced_by_rule_26_04` |
| `defs/rules/tmp/rule_review_common_view_def_v0_1.json` | `header` | `document_type` | Document Type | `edit` | `True` | `False` | `header_one_line_policy` |
| `defs/rules/tmp/rule_review_common_view_def_v0_1.json` | `header` | `source_version` | Source Version | `edit` | `True` | `False` | `header_one_line_policy` |
| `defs/rules/tmp/rule_review_common_view_def_v0_1.json` | `header` | `introduced_in` | Introduced In | `edit` | `True` | `False` | `header_one_line_policy` |
| `defs/rules/tmp/rule_review_common_view_def_v0_1.json` | `header` | `generated_at` | 生成日時 | `edit` | `True` | `False` | `header_one_line_policy` |
| `defs/rules/tmp/rule_review_common_view_def_v0_1.json` | `header` | `approved_count` | 承認済み数 | `edit` | `True` | `False` | `header_one_line_policy` |
| `defs/rules/tmp/rule_review_common_view_def_v0_1.json` | `header` | `source_declared_view_def_schema` | 元MD記載Schema | `edit` | `True` | `False` | `header_one_line_policy` |
| `defs/rules/tmp/rule_review_common_view_def_v0_1.json` | `header` | `source_schema_snapshot.title` | 添付Schema Snapshot | `edit` | `True` | `False` | `header_one_line_policy` |
| `defs/rules/tmp/rule_review_common_view_def_v0_1.json` | `header` | `viewing_policy.data_json_role` | Data JSONの役割 | `edit` | `True` | `False` | `header_one_line_policy` |
| `defs/rules/tmp/rule_review_common_view_def_v0_1.json` | `header` | `viewing_policy.view_def_role` | ViewDefの役割 | `edit` | `True` | `False` | `header_one_line_policy` |
| `defs/rules/tmp/rule_review_common_view_def_v0_1.json` | `header` | `viewing_policy.markdown_role` | Markdownの役割 | `edit` | `True` | `False` | `header_one_line_policy` |
| `defs/rules/tmp/rule_review_common_view_def_v0_1.json` | `header` | `approval_policy` | 承認方針 | `edit` | `True` | `False` | `header_textarea_hidden_by_rule_26_02` |
| `defs/rules/tmp/rule_review_common_view_def_v0_1.json` | `header` | `conversion_note` | 変換メモ | `edit` | `True` | `False` | `header_textarea_hidden_by_rule_26_02` |
| `defs/rules/tmp/rule_review_common_view_def_v0_1.json` | `header` | `preamble` | 前文 / この文書の目的 | `edit` | `True` | `False` | `header_textarea_hidden_by_rule_26_02` |
| `defs/rules/tmp/rule_review_common_view_def_v0_1.json` | `header` | `change_history_policy` | 変更履歴方針 | `edit` | `True` | `False` | `header_textarea_hidden_by_rule_26_02` |
| `defs/rules/tmp/rule_review_common_view_def_v0_1.json` | `rules` | `summary` | 要約 | `search` | `True` | `False` | `search_visible_reduced_by_rule_26_04` |
| `defs/rules/tmp/rule_review_common_view_def_v0_1.json` | `rules` | `body` | ルール本文 | `search` | `True` | `False` | `search_visible_reduced_by_rule_26_04` |
| `defs/rules/tmp/rule_review_common_view_def_v0_1.json` | `rules` | `source_heading` | 見出し | `search` | `True` | `False` | `search_visible_reduced_by_rule_26_04` |
| `defs/rules/tmp/rule_review_common_view_def_v0_1.json` | `rules` | `source_line_start` | 元行 | `search` | `True` | `False` | `search_visible_reduced_by_rule_26_04` |
| `defs/rules/tmp/rule_review_common_view_def_v0_1.json` | `rules` | `source_md_file` | 元MD | `search` | `True` | `False` | `search_visible_reduced_by_rule_26_04` |
| `defs/rules/tmp/rule_review_common_view_def_v0_1.json` | `rules` | `introduced_in` | 導入Ver. | `search` | `True` | `False` | `search_visible_reduced_by_rule_26_04` |
| `defs/rules/tmp/rule_review_common_view_def_v0_1.json` | `rules` | `ceremony_phrase` | 確認メッセージ | `search` | `True` | `False` | `search_visible_reduced_by_rule_26_04` |
| `defs/rules/tmp/rule_review_common_view_def_v0_1.json` | `rules` | `user_comment` | 人間コメント | `search` | `True` | `False` | `search_visible_reduced_by_rule_26_04` |
| `defs/rules/tmp/rule_review_common_view_def_v0_1.json` | `rules` | `ai_response` | AI回答 | `search` | `True` | `False` | `search_visible_reduced_by_rule_26_04` |
| `defs/rules/tmp/rule_review_common_view_def_v0_1.json` | `rules` | `user_reply` | 人間追加コメント | `search` | `True` | `False` | `search_visible_reduced_by_rule_26_04` |
| `defs/rules/tmp/rule_review_common_view_def_v0_1.json` | `rules` | `ai_followup_response` | AI再回答 | `search` | `True` | `False` | `search_visible_reduced_by_rule_26_04` |
| `defs/rules/tmp/rule_review_common_view_def_v0_1.json` | `rules` | `approved_by` | 承認者 | `search` | `True` | `False` | `search_visible_reduced_by_rule_26_04` |
| `defs/rules/tmp/rule_review_common_view_def_v0_1.json` | `rules` | `approved_at` | 承認日時 | `search` | `True` | `False` | `search_visible_reduced_by_rule_26_04` |
| `defs/rules/tmp/rule_review_common_view_def_v0_1.json` | `rules` | `notes` | メモ | `search` | `True` | `False` | `search_visible_reduced_by_rule_26_04` |
| `defs/rules/tmp/rule_review_common_view_def_v0_2_editable_review_target.json` | `header` | `document_type` | Document Type | `edit` | `True` | `False` | `header_one_line_policy` |
| `defs/rules/tmp/rule_review_common_view_def_v0_2_editable_review_target.json` | `header` | `source_version` | Source Version | `edit` | `True` | `False` | `header_one_line_policy` |
| `defs/rules/tmp/rule_review_common_view_def_v0_2_editable_review_target.json` | `header` | `introduced_in` | Introduced In | `edit` | `True` | `False` | `header_one_line_policy` |
| `defs/rules/tmp/rule_review_common_view_def_v0_2_editable_review_target.json` | `header` | `generated_at` | 生成日時 | `edit` | `True` | `False` | `header_one_line_policy` |
| `defs/rules/tmp/rule_review_common_view_def_v0_2_editable_review_target.json` | `header` | `approved_count` | 承認済み数 | `edit` | `True` | `False` | `header_one_line_policy` |
| `defs/rules/tmp/rule_review_common_view_def_v0_2_editable_review_target.json` | `header` | `source_declared_view_def_schema` | 元MD記載Schema | `edit` | `True` | `False` | `header_one_line_policy` |
| `defs/rules/tmp/rule_review_common_view_def_v0_2_editable_review_target.json` | `header` | `source_schema_snapshot.title` | 添付Schema Snapshot | `edit` | `True` | `False` | `header_one_line_policy` |
| `defs/rules/tmp/rule_review_common_view_def_v0_2_editable_review_target.json` | `header` | `viewing_policy.data_json_role` | Data JSONの役割 | `edit` | `True` | `False` | `header_one_line_policy` |
| `defs/rules/tmp/rule_review_common_view_def_v0_2_editable_review_target.json` | `header` | `viewing_policy.view_def_role` | ViewDefの役割 | `edit` | `True` | `False` | `header_one_line_policy` |
| `defs/rules/tmp/rule_review_common_view_def_v0_2_editable_review_target.json` | `header` | `viewing_policy.markdown_role` | Markdownの役割 | `edit` | `True` | `False` | `header_one_line_policy` |
| `defs/rules/tmp/rule_review_common_view_def_v0_2_editable_review_target.json` | `header` | `approval_policy` | 承認方針 | `edit` | `True` | `False` | `header_textarea_hidden_by_rule_26_02` |
| `defs/rules/tmp/rule_review_common_view_def_v0_2_editable_review_target.json` | `header` | `conversion_note` | 変換メモ | `edit` | `True` | `False` | `header_textarea_hidden_by_rule_26_02` |
| `defs/rules/tmp/rule_review_common_view_def_v0_2_editable_review_target.json` | `header` | `preamble` | 前文 / この文書の目的 | `edit` | `True` | `False` | `header_textarea_hidden_by_rule_26_02` |
| `defs/rules/tmp/rule_review_common_view_def_v0_2_editable_review_target.json` | `header` | `change_history_policy` | 変更履歴方針 | `edit` | `True` | `False` | `header_textarea_hidden_by_rule_26_02` |
| `defs/rules/tmp/rule_review_common_view_def_v0_2_editable_review_target.json` | `rules` | `summary` | 要約 | `search` | `True` | `False` | `search_visible_reduced_by_rule_26_04` |
| `defs/rules/tmp/rule_review_common_view_def_v0_2_editable_review_target.json` | `rules` | `body` | ルール本文 | `search` | `True` | `False` | `search_visible_reduced_by_rule_26_04` |
| `defs/rules/tmp/rule_review_common_view_def_v0_2_editable_review_target.json` | `rules` | `source_heading` | 見出し | `search` | `True` | `False` | `search_visible_reduced_by_rule_26_04` |
| `defs/rules/tmp/rule_review_common_view_def_v0_2_editable_review_target.json` | `rules` | `source_line_start` | 元行 | `search` | `True` | `False` | `search_visible_reduced_by_rule_26_04` |
| `defs/rules/tmp/rule_review_common_view_def_v0_2_editable_review_target.json` | `rules` | `source_md_file` | 元MD | `search` | `True` | `False` | `search_visible_reduced_by_rule_26_04` |
| `defs/rules/tmp/rule_review_common_view_def_v0_2_editable_review_target.json` | `rules` | `introduced_in` | 導入Ver. | `search` | `True` | `False` | `search_visible_reduced_by_rule_26_04` |
| `defs/rules/tmp/rule_review_common_view_def_v0_2_editable_review_target.json` | `rules` | `ceremony_phrase` | 確認メッセージ | `search` | `True` | `False` | `search_visible_reduced_by_rule_26_04` |
| `defs/rules/tmp/rule_review_common_view_def_v0_2_editable_review_target.json` | `rules` | `user_comment` | 人間コメント | `search` | `True` | `False` | `search_visible_reduced_by_rule_26_04` |
| `defs/rules/tmp/rule_review_common_view_def_v0_2_editable_review_target.json` | `rules` | `ai_response` | AI回答 | `search` | `True` | `False` | `search_visible_reduced_by_rule_26_04` |
| `defs/rules/tmp/rule_review_common_view_def_v0_2_editable_review_target.json` | `rules` | `user_reply` | 人間追加コメント | `search` | `True` | `False` | `search_visible_reduced_by_rule_26_04` |
| `defs/rules/tmp/rule_review_common_view_def_v0_2_editable_review_target.json` | `rules` | `ai_followup_response` | AI再回答 | `search` | `True` | `False` | `search_visible_reduced_by_rule_26_04` |
| `defs/rules/tmp/rule_review_common_view_def_v0_2_editable_review_target.json` | `rules` | `approved_by` | 承認者 | `search` | `True` | `False` | `search_visible_reduced_by_rule_26_04` |
| `defs/rules/tmp/rule_review_common_view_def_v0_2_editable_review_target.json` | `rules` | `approved_at` | 承認日時 | `search` | `True` | `False` | `search_visible_reduced_by_rule_26_04` |
| `defs/rules/tmp/rule_review_common_view_def_v0_2_editable_review_target.json` | `rules` | `notes` | メモ | `search` | `True` | `False` | `search_visible_reduced_by_rule_26_04` |
