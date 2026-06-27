# v0.14.17 ViewDef Generation Common ViewDef Policy Report

## Phase

`v0.14.17-viewdef-generation-common-viewdef-policy`

## 目的

ViewDef生成時の共通化判断を明文化し、Step 5 の Diff Result共通ViewDef化へ進む前に、以下をルール化した。

- 共通化できるViewDefは、個別ViewDefを増やす前に共通化を検討する。
- 共通化で将来苦しくなる場合は、人間へ相談する。
- 既存ViewDef修正時は、原則としてファイル名を変更しない。
- Diff系ViewDefの判定フィールドは `checks[].pass` を標準とする。

## 更新ファイル

```text
data/json/00_rules/frb_viewdef_generation_rules_data_v0_1.json
data/json/00_rules/_json_creation_prompt.md
data/json/01_main/studio_work_incident_data_v0_59_future_incident_filename_aligned.json
data/json/00_rules/VIEWDEF_GENERATION_COMMON_VIEWDEF_POLICY_REPORT_v0_14_17.md
```

## 追加したViewDef Generation Rules

```text
viewdef_rule_25    共通ViewDef生成ポリシー
viewdef_rule_25_01 共通ViewDefを優先する対象
viewdef_rule_25_02 既存ViewDef修正時は原則ファイル名を変更しない
viewdef_rule_25_03 Diff系ViewDefの判定フィールドはchecks[].passを標準とする
viewdef_rule_25_04 共通ViewDefとドメイン固有ViewDefの切り分け
```

## 対象外

今回の作業はルール化であり、以下は対象外とした。

```text
Step 5: Diff Result共通ViewDefの実作成
既存diff.json本体の再生成
既存ViewDefファイル名の変更
Foundation Rulesの新規追加
Test Evidence Rulesの変更
```

## 確認ポイント

- `frb_viewdef_generation_rules_data_v0_1.json` のファイル名は変更していない。
- `checks[].pass` を正本判定フィールドとして明記した。
- 過剰共通化時はAIが独断で進めず、人間へ相談する方針を明記した。
- 実装・ViewDef本体の変更はStep 5へ分離した。
