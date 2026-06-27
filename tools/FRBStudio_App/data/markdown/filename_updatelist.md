# 00_rules JSONファイル名 変更対比一覧

対象フォルダー:

```text
data/json/00_rules/
```

## 変更対比

| No. | 変更前ファイル名                                                              | 変更後ファイル名                                      | 変更内容                                              |
| --: | --------------------------------------------------------------------- | --------------------------------------------- | ------------------------------------------------- |
|   1 | `_frb_view_def_schema_v0_9.json`                                      | `frb_view_def_schema_v0_9.json`               | 先頭 `_` を外し、通常のルール系JSONと並ぶ名前へ変更                    |
|   2 | `_json_creation_prompt.md`                                            | `_json_creation_prompt.md`                    | 変更なし                                              |
|   3 | `ai_constraint_spec_aggregated_v0_6_footer_chat.json`                 | `frb_constraint_spec_v0_6.json`               | 長い派生名をやめ、FRB制約仕様データとして短く整理                        |
|   4 | `frb_coding_constraints_review_data_v0_3.json`                        | `frb_coding_constraints_data_v0_3.json`       | `review_data` を外し、Coding Constraints のデータ本体として整理  |
|   5 | `frb_studio_foundation_review_data_v0_1_github_fetch_urls_added.json` | `frb_foundation_rules_data_v0_1.json`         | 長い派生名をやめ、Foundation Rules のデータ本体として整理             |
|   6 | `frb_test_evidence_rules_review_data_v0_1.json`                       | `frb_test_evidence_rules_data_v0_1.json`      | `review_data` を外し、Test Evidence Rules のデータ本体として整理 |
|   7 | `frb_view_def_schema_review_data_v0_1.json`                           | `frb_view_def_schema_review_data_v0_1.json`   | 変更なし                                              |
|   8 | `frb_viewdef_generation_rules_review_data_v0_1.json`                  | `frb_viewdef_generation_rules_data_v0_1.json` | `review_data` を外し、ViewDef生成ルールのデータ本体として整理         |

## 変更後の 00_rules 構成

```text
data/json/00_rules/
├─ _json_creation_prompt.md
├─ frb_coding_constraints_data_v0_3.json
├─ frb_constraint_spec_v0_6.json
├─ frb_foundation_rules_data_v0_1.json
├─ frb_test_evidence_rules_data_v0_1.json
├─ frb_view_def_schema_review_data_v0_1.json
├─ frb_view_def_schema_v0_9.json
└─ frb_viewdef_generation_rules_data_v0_1.json
```

## 命名整理の意図

今回の変更では、`review_data` や `github_fetch_urls_added` のような派生・用途寄りの語を減らし、ファイル名を **ルールデータ本体として読みやすい名前** に整理した。

変更方針は以下。

```text
長すぎる派生名を短縮する
review_data という中間用途名を外す
*_rules_data_v*_*.json へ寄せる
Foundation / Test Evidence / ViewDef Generation などの責務をファイル名で見えるようにする
```

## 分類

```text
AI作業用プロンプト:
  _json_creation_prompt.md

制約仕様:
  frb_constraint_spec_v0_6.json

憲法・ルール系データ:
  frb_coding_constraints_data_v0_3.json
  frb_foundation_rules_data_v0_1.json
  frb_test_evidence_rules_data_v0_1.json
  frb_viewdef_generation_rules_data_v0_1.json

ViewDef Schema:
  frb_view_def_schema_v0_9.json

ViewDef Schemaレビュー:
  frb_view_def_schema_review_data_v0_1.json


```

## 注意点

`frb_studio_foundation_review_data_v0_1_github_fetch_urls_added.json` から `frb_foundation_rules_data_v0_1.json` へ変更したため、Foundation Rules raw URL 契約も合わせて見直しが必要。

旧URL:

```text
data/json/00_rules/frb_studio_foundation_review_data_v0_1_github_fetch_urls_added.json
```

新URL候補:

```text
data/json/00_rules/frb_foundation_rules_data_v0_1.json
```

今後、AI作業依頼テンプレートや foundation_rule_019 が旧ファイル名を参照している場合は、新ファイル名へ更新する。
