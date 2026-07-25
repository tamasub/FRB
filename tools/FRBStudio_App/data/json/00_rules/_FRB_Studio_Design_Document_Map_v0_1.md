# FRB Studio 設計文書体系・配置方針 v0.1

- 記録日: 2026-07-25
- 対象Phase: `v0.18.27-document-architecture-policy-record`
- 対象Incident: `studio_work_0144`
- 状態: 暫定方針を記録済み。v0.18.29でFieldDef・ValidationPolicy・共通TestPattern導出方針を接続。v0.18.31で実証なき抽象化の禁止を憲法へ追加し、専用ルールファイルを新設しない配置方針を実適用した。実Data/Schema/Runner実装と全件仕分けは後続作業とする。

> このMarkdownは、人間が設計文書体系を一枚で確認するための説明用記録である。  
> 判断の正本は `data/json/01_main/_studio_work_incident_data_v2.json` の `studio_work_0144.decision_log` とし、既存のルール・責務・TestPatternの正本Data JSONを置き換えない。

## 1. 今回確定する基本方針

FRB Studioの設計文書体系は、次の二つの軸を分けて考える。

### 1.1 適用範囲・権威の軸

```text
憲法
  ↓
Foundation
  ↓
製品・責務
  ↓
機能・具体仕様
```

### 1.2 設計情報の種類の軸

```text
思想
判断軸
制約
ルール
責務・契約
保証
具体仕様
判断ログ
```

この二軸は交差する。

- 憲法にも判断軸・制約・ルールが存在し得る。
- Foundationにも判断軸・制約・ルールが存在し得る。
- 責務定義にも責務固有の判断軸・関連制約・ルール・保証が存在し得る。
- 情報種別ごとに専用ファイルを一律新設する必要はない。
- 配置先は、情報の名前ではなく「どの範囲へ効くか」と「どの正本が責任を持つか」で決める。

## 2. 用語の役割

| 情報種別 | 一言定義 | 主な問い |
|---|---|---|
| 判断軸 | 複数案から選ぶときの優先基準 | 何を優先するか |
| 制約 | 選択肢から除外する境界 | 何をしてはいけないか |
| ルール | 条件に応じた選択規則 | この条件ならどうするか |
| 責務・契約 | 対象が外部へ約束すること | 何を保証するか |
| 保証 | 責務を検証可能な約束へ分解したもの | 何を観測できれば守ったと言えるか |
| 仕様 | 採用した結果を具体的に成立・観測させる定義 | 画面・Interface・Schema上でどう見えるか |
| 判断ログ | 採用・補正・例外の理由 | なぜその判断になったか |

## 3. 適用範囲ごとの配置方針

| 適用範囲 | 主な役割 | 判断軸・制約・ルールの扱い | 仕様・契約の扱い |
|---|---|---|---|
| 憲法 | 正しさ、正本、人間承認、変更統治を定める | 最上位の判断軸・制約・統治ルールを置く | 承認状態、変更履歴、追跡可能性など統治上の契約を置く |
| Foundation | Studio製品群の共通アーキテクチャ土台を定める | Data/View/Runtime分離、Core/Overlay分離、正本一意性など共通判断を置く | 共通データ構造、共通運用、共通Adapter等の契約を置く |
| 責務定義 | 製品・機能が何を保証するかを定める | 責務固有の判断軸、関連制約ID、責務固有ルールを持てる | 入出力、状態、異常時動作、副作用、性能、保証IDを持つ |
| ViewDef / Schema | 表示・入力・構造の機械可読契約を定める | 原則として判断軸の正本にはしない。構造制約や表示ルールは表現できる | 具体的な表示・入力・構造仕様を定義する |
| TestPattern | 保証を実行可能な検証へ具体化する | 制約・ルールを検証条件へ展開するが、上位判断資産の正本にはしない | `Input + ExpectedDef + Expected` で保証を検証する |
| Incident | 作業起点、差分、判断経緯、後続作業を記録する | 適用候補・昇格候補・今回採用した判断を記録する | 作業結果、差分、確認結果を記録する |

## 3.1 v0.18.31 実証なき抽象化ガードの配置

共通化・汎用化・抽象化のガードは、専用ファイルを新設せず、次の既存正本へ配置する。

```text
frb_coding_constraints_data_v0_3.json
  ├─ governance_items[]
  │    └─ 判断軸「責務分離を共通化より先に行う」
  ├─ constitution_20
  │    └─ AI協働時の共通化優先を撤回し、constitution_29へ接続
  └─ constitution_29
       └─ 実証なき抽象化の禁止、禁止3条件、実施4条件

frb_foundation_rules_data_v0_1.json
  └─ foundation_rule_020
       └─ 詳細条件を重複せずconstitution_29を参照
```

この配置により、設計統治の正本を増やさず、憲法で発火条件を定義し、FoundationでStudio製品群へ適用する。条件不明時は個別実装を維持し、将来候補は判断ログまたはインシデントへ記録する。

## 4. 現在の正本ファイル実態

| 役割 | 現在の主なファイル | 確認した実態 | 現時点の扱い |
|---|---|---|---|
| Studioくん憲法 | `data/json/00_rules/frb_coding_constraints_data_v0_3.json` | `document_type: studio_constitution_review`、`rules[]` 29件。憲法原則とFoundation級アーキテクチャ制約が同居する | 現行正本を維持する。Foundation移管候補は後続で分類する |
| Foundation | `data/json/00_rules/frb_foundation_rules_data_v0_1.json` | `rules[]` 25件。Studio共通の命名、正本、承認、GitHub/ZIP、運用原則を保持する | Studio製品群の共通土台の正本として維持する |
| 責務マスター | `data/json/03_tests/responsibilities/responsibility_data_v0_1.json` | 責務、関連制約、`guarantees[]`、観測可能結果を保持する | 現行の責務・保証実態として参照する。正式な配置・Schemaは後続で整理する |
| 責務定義ドラフト | `data/json/03_tests/qa/responsibility_def/responsibility_def_master_draft_v0_1.json` | 公開Interface、入力・出力・エラー・防衛・性能契約を持つ8件のドラフト | 責務マスターとの役割重複を後続で整理する |
| TestPattern | `data/json/03_tests/responsibilities/responsibility_expected_first_set/test_patterns/responsibility_expected_test_patterns_data_v0_1.json` | `responsibility_cd`、`guarantee_ids`、`input`、`expected`を持つ8件の初期セット | 責務・保証とID接続する検証資産として維持する |
| 制約レビュー材料 | `data/json/00_rules/frb_constraint_spec_v0_6.json` | 12グループ・84明細。制約だけでなく仕様、現行制限、GAP、将来候補、レビュー方針が混在する | 純粋な制約正本とは認定せず、仕分け前レビュー材料として扱う |
| ViewDef Schema | `data/json/00_rules/frb_view_def_schema_v0_9.json` | ViewDefの許可構造を定義するJSON Schema | 機械可読な構造契約として維持する |

## 5. 責務・保証・TestPatternの接続方針

```text
憲法 / Foundation
  └─ 判断軸・制約・共通ルール
           ↓ 関連ID・適用範囲
責務定義
  ├─ responsibility_cd
  ├─ 責務固有の判断軸
  ├─ related_constraint_ids
  ├─ 仕様的契約
  └─ guarantees[].guarantee_id
           ↓ responsibility_cd + guarantee_ids
TestPattern
  ├─ Input
  ├─ ExpectedDef
  └─ Expected
           ↓ 品質保証済みRunner / Adapter
Actual
           ↓ CompareStrategy
Diff
           ↓
人間承認・判断ログ・改定候補
```

### 5.1 Expectedの配置

- Expected契約の正本は一つにする。
- 小さな責務UTでは、TestPattern内の `Input / ExpectedDef / Expected` を一体で保持してよい。
- 大きなExpected、再利用するExpected、巨大な構造Expectedは、`expected/` 配下の外部Expected正本を参照する。
- 同じExpectedをTestPattern内と外部Expectedへ重複保存しない。
- Expected、Actual、Diffの証跡フォルダーを持つ既存テストスイート構造と、TestPattern内の期待値定義は矛盾しない。
  - TestPattern内または外部Expected: 何を期待するかを定義する正本。
  - Resolved Snapshot / expected証跡: 導出元の版・Hashを固定し、Runnerへ渡した具体値とExpectedを保存する派生証跡。
- 責務定義とTestPatternは更新ライフサイクルが異なるため別正本とし、IDで接続する。

### 5.2 FieldDefから具体TestCaseを導出する接続

v0.18.29では、単項目Validationの具体値を項目ごとに重複記載せず、次の構造で導出する方針を `frb_test_evidence_rules_data_v0_2.json` へ記録した。

```text
FieldDef
  = field_id / path / data_type / required / minimum / maximum /
    integer_only / format / allowed_values

ValidationPolicy
  = missing / null / type / integer / range / format等の判定方針

Common SingleFieldValidation TestPattern
  = minimum_minus_step / range_midpoint等の意味Pattern

Resolved TestCase Snapshot
  = 具体Input / Expected / 導出元version・hashを版固定した承認・実行単位

品質保証済みRunner / Adapter / CompareStrategy
  = 承認済みSnapshotを実行しActual / Diffを出す
```

初期標準のinclusive整数範囲では、次を導出する。

```text
minimum - 1
minimum
minimum + 1
range_midpoint = trunc_toward_zero((minimum + maximum) / 2)
maximum - 1
maximum
maximum + 1
```

例: `minimum=1 / maximum=100` なら `0 / 1 / 2 / 50 / 99 / 100 / 101`。
`range_midpoint` は統計medianではなく、許容範囲の代表正常値を意味する。
狭い範囲で複数Patternが同じ具体値へ収束した場合は、重複TestCaseを増やさず `collapsed` / `not_applicable` と理由を残す。

導出元が変わった場合は、Resolved Snapshotを再生成し、具体値・Expected・差分を人間が再承認する。
Runnerは実行時に独自判断で具体値やExpectedを変更しない。

## 6. 判断ログから正式資産へ昇格するルール

```text
判断ログ
  ↓ 適用範囲を確認
責務固有
  → 責務定義へ昇格

複数責務・複数製品で共通
  → Foundationへ昇格

正本・承認・人間とAIの関係を統治
  → 憲法へ昇格
```

- 昇格時は、元の判断ログIDを残す。
- 既存定義との重複、適用範囲、例外条件を確認する。
- AIは昇格候補を提示できるが、正式採用は人間が承認する。
- 運用で違和感が出た場合は、判断ログを追加し、この配置方針自体を改定する。

## 7. JSON構造の共通化方針

概念は共有するが、すべてのJSONを同じ形へ強制しない。

例:

```json
{
  "decision_axes": [],
  "constraints": [],
  "rules": []
}
```

責務定義では、次の方が自然な場合がある。

```json
{
  "responsibility_cd": "...",
  "decision_axes": [],
  "related_constraint_ids": [],
  "responsibility_rules": [],
  "guarantees": []
}
```

共通化の対象は、意味、ID接続、承認・変更履歴、検索可能性である。ドメイン固有の自然な構造まで無理に平坦化しない。

## 8. 今回実施しないこと

このPhaseでは、次を実施しない。

- 憲法からFoundationへの実データ移動
- `frb_constraint_spec_v0_6.json` 84明細の全件仕分け
- 責務定義の正式Schema・配置先の確定
- 既存ViewDef / Schemaの改定
- 判断軸ID体系の全面確定
- 独立Expected正本の新設
- 概念名ごとの新規Data JSON大量作成
- Runtimeの変更

## 9. 後続作業

1. 憲法29件を確認し、Foundationへ寄せる候補を分類する。
2. `frb_constraint_spec_v0_6.json` の84明細を、制約・仕様・GAP・将来候補・レビュー方針へ分類する。
3. `responsibility_data_v0_1.json` と `responsibility_def_master_draft_v0_1.json` の責務を整理し、正式正本・Schema・配置を決める。
4. 責務・保証・TestPatternの未接続、存在しないID参照、保証未検証をRelation/Absence検査で検出する。
5. `studio_work_0146` で、FieldDef・ValidationPolicy・共通単項目TestPatternから具体ケースを導出する規則を `frb_test_evidence_rules_data_v0_2.json` へ接続済み。後続で実Data / Schema / 承認View / 導出エンジン / Runner連携を実装する。

## 10. 結論

```text
憲法 / Foundation / 責務定義
= どの高さ・範囲へ効くか

判断軸 / 制約 / ルール / 仕様
= その設計情報が何を表すか
```

制約・判断軸・ルールは各設計書に存在し得る。配置先は情報種別だけで決めず、適用範囲と正本責務で決める。

今回の完成物は「棚の中身の一括移動」ではなく、今後の仕分けで迷わないための棚名・収納規則・接続方針の記録である。
