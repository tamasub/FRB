# v0.14.18 Delivery / Cleanup / ZIP Safety Policy Report

## Phase

`v0.14.18-delivery-cleanup-zip-safety-policy`

## Summary

成果物ZIP返却時の安全契約を整理した。
既に `v0.14.15` で Test Folder / Runtime生成物隔離の方針は入っていたため、今回は **返却前チェック・ZIP除外・Windows長大パス安全性・cleanup運用** を中心に補強した。

## Updated files

- `data/json/00_rules/frb_foundation_rules_data_v0_1.json`
- `data/json/00_rules/frb_coding_constraints_data_v0_3.json`
- `data/json/00_rules/_json_creation_prompt.md`
- `.gitignore`
- `tests/tools/cleanup_runtime_artifacts.ps1`
- `data/json/01_main/studio_work_incident_data_v0_59_future_incident_filename_aligned.json`
- `data/json/00_rules/DELIVERY_CLEANUP_ZIP_SAFETY_POLICY_REPORT_v0_14_18.md`

## ZIP exclusion policy

成果物ZIPには次を含めない。

```text
node_modules/
playwright-report/
test-results/
test_results/
tests/.runtime/
tests_screen_state/
```

## Archive policy

- 旧パス・不要データのうち、判断履歴として残すべきものは `_archive/{削除日時}/` へ退避する。
- runtime生成物は再生成可能なため、原則としてarchiveせず削除・除外する。
- Expected / Actual / Diff / Test Patternは `data/json/03_tests/` 配下の証跡正本として扱い、cleanup対象にしない。

## Delivery checklist

1. JSON parseが通る。
2. runtime生成物除外リストがZIPに含まれていない。
3. Windows解凍で問題になりやすい長大パスを含めない。
4. 旧パス罠フォルダーをactiveに残さない。
5. 更新済みインシデントJSONを `data/json/01_main/` に含める。
6. `latest_ai_response`, `discussion_history`, `change_history`, `actual_updated_files` に作業結果を残す。

## Note

今回のZIPには、作業開始時点でruntime生成物は含まれていなかったため、archive退避対象はなし。
`.gitignore` と `cleanup_runtime_artifacts.ps1` により、今後の混入を抑止する。
