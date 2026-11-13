# v0.14.20 rules filename reference migration report

## 目的
00_rules の正本ファイル名変更に伴い、現行運用で参照される旧ファイル名を新ファイル名へ移行した。

## 変更対比

| 旧ファイル名 | 新ファイル名 |
|---|---|
| `_frb_view_def_schema_v0_9.json` | `frb_view_def_schema_v0_9.json` |
| `ai_constraint_spec_aggregated_v0_6_footer_chat.json` | `frb_constraint_spec_v0_6.json` |
| `frb_coding_constraints_review_data_v0_3.json` | `frb_coding_constraints_data_v0_3.json` |
| `frb_studio_foundation_review_data_v0_1_github_fetch_urls_added.json` | `frb_foundation_rules_data_v0_1.json` |
| `frb_studio_foundation_review_data_v0_1.json` | `frb_foundation_rules_data_v0_1.json` |
| `frb_test_evidence_rules_review_data_v0_1.json` | `frb_test_evidence_rules_data_v0_1.json` |
| `frb_viewdef_generation_rules_review_data_v0_1.json` | `frb_viewdef_generation_rules_data_v0_1.json` |

## 更新した active ファイル

- `data/json/00_rules/_json_creation_prompt.md`
- `data/json/00_rules/frb_foundation_rules_data_v0_1.json`
- `data/json/01_main/00_do_incident_prompt_temple.md`
- `data/json/05_inventory/defs_data_link_inventory_v0_1.json`
- `data/json/05_inventory/defs_data_link_inventory_v0_2_repaired.json`
- `defs/rules/studio_work_incident_view_def_v0_4_readable_cards_confirm_status_markdown_preview.json`
- `defs/rules/tmp/rule_review_common_view_def_v0_1.json`
- `defs/rules/tmp/rule_review_common_view_def_v0_2_editable_review_target.json`
- `defs/relation/relation_axis_constraint_view_def_v0_1.json`
- `defs/relation/relation_axis_test_pattern_view_def_v0_1.json`


## 追加検出した派生旧名の補正

以下の派生旧名も、現行参照としては新ファイル名へ補正した。

| 旧参照 | 新参照 |
|---|---|
| `_frb_view_def_schema_v0_9_chat_input_mapping.json` | `frb_view_def_schema_v0_9.json` |
| `frb_view_def_schema_v0_9_chat_input_mapping.json` | `frb_view_def_schema_v0_9.json` |
| `coding_constraints_review_data_v0_3.json` | `frb_coding_constraints_data_v0_3.json` |

- `data/json/00_rules/frb_viewdef_generation_rules_data_v0_1.json`

- `data/json/00_rules/frb_view_def_schema_review_data_v0_1.json`

- `data/json/00_rules/frb_view_def_schema_v0_9.json`

- `defs/rules/chatgpt/chatgpt_shared_context_view_def_v0_1.json`

## 意図的に旧名を残した場所

- `data/json/00_rules/filename_updatelist.md` : 変更対比の正本メモであり、旧名を残す。
- `data/markdown/filename_updatelist.md` : 変更対比のMarkdownコピーであり、旧名を残す。
- 過去インシデントJSON / data/markdown の生成済みExport / test evidence actual-diff : 当時の履歴・証跡として旧名を残す。

## 確認観点

- active参照は新ファイル名へ寄せた。
- Foundation Rules raw URL契約は `frb_foundation_rules_data_v0_1.json` を指す。
- 変更対比・履歴・証跡は一律置換しない。

## 作業日
2026-06-27
