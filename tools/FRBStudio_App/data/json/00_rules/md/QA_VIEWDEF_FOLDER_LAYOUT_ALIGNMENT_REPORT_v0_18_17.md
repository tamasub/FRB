# QA ViewDef Folder Layout Alignment Report v0.18.17

## 目的

`defs/qa` 配下に直置きされていたQA系ViewDefを、Data JSON側の意味に合わせて整理した。

今回の重要方針は以下。

- `defs` 側のフォルダー名には数字プレフィックスを使わない。
- `defs/qa` はQA系ViewDefの意味的ルートとして残す。
- 画面選択順ではなく、意味の美しさと見通しを優先する。
- フォルダー移動を伴うため、返却ZIPは差分ではなく `data/` と `defs/` を全件返却する。

## 新しい配置

```text
defs/qa/
  review/
    qa_cross_check_risk_view_def_v0_1.json
    qa_cross_constraint_view_def_v0_1.json
    qa_cross_quality_risk_view_def_v0_1.json
    qa_cross_test_pattern_view_def_v0_1.json
    qa_expected_checks_candidate_review_view_def_v0_1.json
    qa_expected_checks_candidate_review_wrapped_view_def_v0_1.json
    qa_expected_checks_classified_view_def_v0_1.json
    qa_expected_checks_sample_view_def_v0_1.json
    qa_shortage_expected_findings_view_def_v0_1.json

  tests/
    qa_actual_observation_view_def_v0_1.json
    qa_actual_result_view_def_v0_1.json
    qa_diff_result_view_def_v0_1.json
    qa_test_patterns_sample_view_def_v0_1.json

  responsibility_def/
    expected_def_type_master_view_def_v0_1.json
    performance_limit_policy_view_def_v0_1.json
    responsibility_def_master_view_def_v0_1.json

  responsibilities/
    responsibility_expected_actual_view_def_v0_1.json
    responsibility_expected_diff_view_def_v0_1.json
    responsibility_expected_test_patterns_view_def_v0_1.json
```

## 移動方針

| 移動前 | 移動後 | 理由 |
|---|---|---|
| `defs/qa/qa_expected_checks_*.json` | `defs/qa/review/` | QAレビュー・期待値候補・分類系ViewDefとしてまとめるため |
| `defs/qa/qa_cross_*.json` | `defs/qa/review/` | Cross Check / Risk / Constraint はレビュー観点系としてまとめるため |
| `defs/qa/qa_shortage_expected_findings_*.json` | `defs/qa/review/` | 不足期待値の発見・レビュー系として扱うため |
| `defs/qa/qa_actual_*.json` | `defs/qa/tests/` | テスト証跡のActual表示系として扱うため |
| `defs/qa/qa_diff_result_*.json` | `defs/qa/tests/` | テスト証跡のDiff表示系として扱うため |
| `defs/qa/qa_test_patterns_*.json` | `defs/qa/tests/` | テストパターンサンプル表示系として扱うため |
| `defs/qa/responsibility/expected_def_type_master_*.json` | `defs/qa/responsibility_def/` | `data/json/03_tests/qa/responsibility_def/` に対応する定義マスタ系ViewDefとして扱うため |
| `defs/qa/responsibility/performance_limit_policy_*.json` | `defs/qa/responsibility_def/` | `data/json/03_tests/qa/responsibility_def/` に対応する定義マスタ系ViewDefとして扱うため |
| `defs/qa/responsibility/responsibility_def_master_*.json` | `defs/qa/responsibility_def/` | `data/json/03_tests/qa/responsibility_def/` に対応する定義マスタ系ViewDefとして扱うため |
| `defs/qa/responsibility/responsibility_expected_*.json` | `defs/qa/responsibilities/` | `data/json/03_tests/responsibilities/` に対応する責務Expected証跡系ViewDefとして扱うため |

## 参照修正

`data/` と `defs/` 配下のJSONについて、以下のような active 参照を新パスへ修正した。

- `view_def`
- `view_def_candidates`
- link inventory
- QAサンプルData
- テスト証跡Data
- 一部インシデントJSON内の最新参照

## 互換方針

今回はフォルダー整理を優先するため、旧 `defs/qa/qa_*.json` 直下や旧 `defs/qa/responsibility/` の互換コピーは残さない。

過去のMarkdownレポートや古い作業履歴に残る旧パス文字列は、履歴として残る場合がある。

## 確認結果

- `data/` 配下 JSON parse OK
- `defs/` 配下 JSON parse OK
- 移動後のViewDef 19件の存在確認 OK
- 旧 `defs/qa/*.json` 直下混在なし
- 旧 `defs/qa/responsibility/` フォルダーなし
- `defs` 配下に数字プレフィックスの新規フォルダーなし

## 注意

今回の返却ZIPは、Foundation Rulesの通常差分返却契約よりも、ユーザー明示依頼を優先し、`data/` と `defs/` を全件返却する。
