# Defs/Data ViewDef 紐づけ救出レポート v0.1

## 作業概要

添付 `defs (3).zip` の `data/` と `defs/` を対象に、Data JSON 側の `view_def` / `view_def_candidates` を補完・正規化しました。
既存ViewDefファイル名は変更していません。defs本体も変更していません。

## 集計

| 指標 | 作業前 | 作業後 |
|---|---:|---:|
| defs JSON数 | 37 | 37 |
| data JSON数 | 41 | 41 |
| Data→ViewDef参照数 | 38 | 76 |
| Dataに紐づいたdefs数 | 16 | 31 |
| defs_only数 | 19 | 6 |
| ViewDefからのみ参照数 | 2 | 0 |
| 参照先なしViewDef数 | 1 | 1 |
| JSON parse error数 | 0 | 0 |

## 紐づけ救出できたViewDef

| ViewDef | 作業前 | 作業後Data参照数 | 用途 |
|---|---|---:|---|
| `qa/qa_cross_check_risk_view_def_v0_1.json` | defs_only | 2 | チェック観点 × リスク |
| `qa/qa_cross_constraint_view_def_v0_1.json` | defs_only | 2 | 制約ID別 Expected 件数 |
| `qa/qa_cross_quality_risk_view_def_v0_1.json` | defs_only | 2 | 品質観点 × リスク |
| `qa/qa_cross_test_pattern_view_def_v0_1.json` | defs_only | 2 | テストパターン別 Expected 件数 |
| `qa/qa_shortage_expected_findings_view_def_v0_1.json` | defs_only | 2 | Expected 不足検出 |
| `relation/relation_approval_view_def_v0_1.json` | defs_only | 1 | Relation承認レビュー / AI候補線→人間承認線 |
| `relation/relation_axis_business_customer_view_def_v0_1.json` | defs_only | 3 | relation_axis_business_customer / 顧客軸 |
| `relation/relation_axis_business_employee_view_def_v0_1.json` | defs_only | 3 | relation_axis_business_employee / 担当者軸 |
| `relation/relation_axis_business_project_view_def_v0_1.json` | defs_only | 3 | relation_axis_business_project / 案件軸 |
| `rules/chatgpt/chatgpt_context_relation_graph_view_def_v0_1.json` | defs_only | 1 | キーワード関係性 |
| `rules/chatgpt/chatgpt_raw_keyword_activation_view_def_v0_1.json` | defs_only | 1 | 生キーワード |
| `rules/chatgpt/chatgpt_sentence_prime_map_view_def_v0_1.json` | defs_only | 1 | センテンス一覧 |
| `rules/tmp/rule_review_common_view_def_v0_1.json` | defs_only | 3 | ルールレビュー（共通） |
| `rules/tmp/rule_review_common_view_def_v0_2_editable_review_target.json` | defs_only | 3 | ルールレビュー（共通）/ レビュー対象編集対応 |
| `screen_state/screen_state_diff_view_def_child_v0_3_failure_focus.json` | viewdef_linked_only | 1 | 【継承先CHILD】Screen State Diff Failure Focus View |
| `screen_state/screen_state_diff_view_def_child_v0_3_summary.json` | viewdef_linked_only | 1 | 【継承先CHILD】Screen State Diff Summary View |

## 更新したData JSON

| Data JSON | 変更内容 |
|---|---|
| `data/json/00_rules/frb_coding_constraints_review_data_v0_3.json` | `view_def`: `rules/rule_review_common_view_def_v0_3.json` / `view_def_candidates`: 3件 |
| `data/json/00_rules/frb_studio_foundation_review_data_v0_1_github_fetch_urls_added_viewdef_candidates_rule_added.json` | `view_def`: `rules/rule_review_common_view_def_v0_3.json` / `view_def_candidates`: 3件 |
| `data/json/00_rules/frb_viewdef_generation_rules_review_data_v0_1.json` | `view_def`: `rules/rule_review_common_view_def_v0_3.json` / `view_def_candidates`: 3件 |
| `data/json/01_main/chatgpt_context_relation_graph_data_v0_1.json` | `view_def`: `rules/chatgpt/chatgpt_context_relation_graph_view_def_v0_1.json` |
| `data/json/01_main/chatgpt_raw_keyword_activation_data_v0_1.json` | `view_def`: `rules/chatgpt/chatgpt_raw_keyword_activation_view_def_v0_1.json` |
| `data/json/01_main/chatgpt_sentence_prime_map_data_v0_1.json` | `view_def`: `rules/chatgpt/chatgpt_sentence_prime_map_view_def_v0_1.json` |
| `data/json/01_main/chatgpt_shared_context_data_v0_1.json` | `view_def`: `rules/chatgpt/chatgpt_shared_context_view_def_v0_1.json` |
| `data/json/01_main/qa_expected_checks_add_candidates_v0_1.json` | `view_def`: `qa/qa_expected_checks_candidate_review_wrapped_view_def_v0_1.json` / `view_def_candidates`: 1件 |
| `data/json/01_main/qa_expected_checks_sample_v0_1.json` | `view_def`: `qa/qa_expected_checks_sample_view_def_v0_1.json` / `view_def_candidates`: 7件 |
| `data/json/01_main/qa_test_patterns_sample_v0_1.json` | `view_def`: `qa/qa_test_patterns_sample_view_def_v0_1.json` |
| `data/json/02_business/business_customers_v0_1.json` | `view_def`: `relation/relation_axis_business_customer_view_def_v0_1.json` / `view_def_candidates`: 1件 |
| `data/json/02_business/business_employees_v0_1.json` | `view_def`: `relation/relation_axis_business_employee_view_def_v0_1.json` / `view_def_candidates`: 1件 |
| `data/json/02_business/business_projects_v0_1.json` | `view_def`: `relation/relation_axis_business_project_view_def_v0_1.json` / `view_def_candidates`: 1件 |
| `data/json/02_business/business_relations_v0_1.json` | `view_def`: `relation/relation_edit_view_def_v0_1.json` / `view_def_candidates`: 5件 |
| `data/json/03_screen_state/screen_state_smoke_001.diff.json` | `view_def`: `screen_state/screen_state_diff_view_def_base_v0_2_checks.json` / `view_def_candidates`: 3件 |
| `data/json/04_qa/qa_expected_checks_classified_v0_1.json` | `view_def`: `qa/qa_expected_checks_classified_view_def_v0_1.json` / `view_def_candidates`: 7件 |

## 残った defs_only / 保留判断

| ViewDef / JSON | 判定 | 理由 |
|---|---|---|
| `common/common_types_v0_1.json` | KEEP | support_json。Data JSONに直接紐づけるものではなく、fieldTypeSources等の支援定義。 |
| `common/view_def_maint_fields_v0_2.json` | KEEP/保留 | ViewDef JSON自身をメンテするためのViewDef。通常Data JSONへ直接紐づける対象ではない。 |
| `qa/qa_expected_checks_candidate_review_view_def_v0_1.json` | 保留 | root配列 `$` 用ViewDef。対象候補 `data/json/01_main/qa_expected_checks_classified_v0_1.json` はtop-level配列のため view_def を埋め込めない。objectへwrapする別作業が必要。 |
| `relation/relation_axis_constraint_view_def_v0_1.json` | ERROR/保留 | `constraint_trace_relations_v0_1.json` が添付data内に無いため、Relation証跡カード生成が成立しない。 |
| `relation/relation_axis_diff_check_view_def_v0_1.json` | ERROR/保留 | `constraint_trace_relations_v0_1.json` が添付data内に無いため、Diff Check証跡カード生成が成立しない。 |
| `relation/relation_axis_test_pattern_view_def_v0_1.json` | ERROR/保留 | `constraint_trace_relations_v0_1.json` が添付data内に無いため、TestPattern証跡カード生成が成立しない。 |

## 現時点でエラーになる/不足している参照

| Data JSON | 参照 | 理由 |
|---|---|---|
| `data/json/80_frb/fft_data_実験条件プロファイル.json` | `frb/fft_view_def_実験条件プロファイル.json` | 添付defs内に実体なし。読み込み時にViewDef未存在エラーになる可能性あり。 |

## 補足

- `view_def_candidates[].view_def` は `defs/` 配下からの相対パスで統一しました。
- `status=deprecated` の候補は旧版比較用です。通常利用は `active` の候補を想定しています。
- Relation系の一部ViewDefは `virtualData` / `dataSources` を使うため、静的JSON上に表示用配列が無くても、必要なsource dataがあれば候補に入れています。
- `constraint_trace_relations_v0_1.json` が無い3つのRelation証跡ViewDefは、今回はData JSONへ紐づけていません。