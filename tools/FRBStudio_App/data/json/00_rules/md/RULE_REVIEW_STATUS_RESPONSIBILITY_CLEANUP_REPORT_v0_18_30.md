# Rule Review 状態責務・データクリーニング報告 v0.18.30

- 実施日: 2026-07-25
- 対象ViewDef: `defs/rules/rule_review_common_view_def_v0_3.json`
- 対象Data JSON: 8ファイル
- 移行対象既存Rule: 245件

## 結論

一括移行を止める重大なデータ障害はなかった。
ただし、状態項目の責務混在と集計不整合があったため、意味を推測しない安全な正規化だけを行った。

## 状態契約

```text
verification_status = AI確認状態
approval_decision   = 人間承認
```

- `review_status` は廃止した。
- 人間承認の編集操作は確認メッセージカード内の一か所だけにした。
- AI確認状態は人間向けDetailではreadonly表示とした。
- AIが承認対象の意味を変更した場合は、未確認・未承認へ戻す。

## 正規化実績

- `review_status` 削除: 245件
- `approval_decision: 未判断 → 未承認`: 39件
- `approval_decision: 承認待ち → 未承認`: 1件
- `verification_status: 実装済み → 確認済み`: 1件
- `approved_count` は各Dataの `approval_decision == 承認する` から再計算した。
- 既存の `approved_by / approved_at` 欠落は推測補完していない。

## ファイル別監査

| Data | Rule数 | 旧review_status | 旧verification_status | 旧approval_decision | 移行後承認数 |
|---|---:|---|---|---|---:|
| `data/json/00_rules/frb_coding_constraints_data_v0_3.json` | 28 | 建国レビュー:21 / :2 / 追加レビュー:5 | 確認済み:27 / 実装済み:1 | 承認する:27 / 承認待ち:1 | 27 |
| `data/json/00_rules/frb_diff_result_format_rules_data_v0_1.json` | 11 | 未レビュー:11 | 確認済み:11 | 承認する:11 | 11 |
| `data/json/00_rules/frb_foundation_rules_data_v0_1.json` | 23 | 未レビュー:23 | 確認済み:23 | 承認する:23 | 23 |
| `data/json/00_rules/frb_test_evidence_rules_data_v0_2.json` | 20 | 要再整理:4 / 未レビュー:16 | 確認済み:20 | 承認する:20 | 20 |
| `data/json/00_rules/frb_viewdef_generation_rules_data_v0_1.json` | 85 | 未レビュー:77 / draft:2 / レビュー済み:6 | 確認済み:83 / 未確認:2 | 承認する:83 / 未承認:2 | 83 |
| `data/json/00_rules/studio-overlay-manifest_rules_data_v0_1.json` | 24 | 確認済み:24 | 確認済み:24 | 未承認:24 | 0 |
| `data/json/00_rules/studio_context_engineer_wannabe_foundation_rules_data_v0_1_draft.json` | 15 | 未レビュー:15 | 確認済み:15 | 承認する:15 | 15 |
| `data/json/00_rules/studio_test_plan_responsibility_scope_md_data_v0_1.json` | 39 | 未レビュー:39 | 未確認:39 | 未判断:39 | 0 |

## 追加・改定ルール

- `foundation_rule_024`: 人間承認の意味同一性とAI変更時の承認失効
- `foundation_rule_025`: Rule Review状態はAI確認と人間承認の二項目に限定
- `viewdef_rule_31`: Rule Reviewの承認操作を一か所へ限定

## 未実装の後続

承認対象Hashによる自動失効検知、およびStudio Runtimeでの自動リセットは今回の対象外。
現時点ではFoundation RuleとAI作業手順で運用し、後続で機械強制を検討する。

## 確認結果

- 更新JSONはすべてparse成功。
- 対象8 Dataで `review_status` 行0件、状態値不正0件、`approved_count`整合を確認。
- 共通ViewDefは人間承認の編集UIが1か所、AI確認の人間編集UIが0か所。
- `node --test tests/qa/static/*.test.mjs`: 7件成功、4件失敗。失敗は添付ZIPに `studio_overlays/thought_evolution` 資材が存在しないENOENTで、本変更とは無関係。
