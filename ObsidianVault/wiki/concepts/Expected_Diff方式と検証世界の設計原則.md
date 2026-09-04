---
address: c-000013
type: concept
title: "Expected Diff方式と検証世界の設計原則"
created: 2026-09-04
updated: 2026-09-04
status: developing
tags:
  - concept
  - expected-diff
  - test-runner
  - approval-engineering
related:
  - "[[責務定義駆動テスト設計]]"
  - "[[Approval_Engineeringと構造化された意図]]"
  - "[[再構築可能性という品質指標]]"
sources:
  - "[[AI協働036_Expected_Diff方式]]"
  - "[[AI協働034_責務Behavior_Pilot_Phase2]]"
claim_ids:
  - clm-expected-diff-shared-tool
  - clm-verification-world-simplification
  - clm-guarantee-inheritance
complexity: advanced
domain: "AI駆動開発・テスト設計・検証基盤"
aliases:
  - Expected Diff
  - Verification World
  - Generic Mutation Engine
  - Comparison Policy
---

# Expected Diff方式と検証世界の設計原則

## 要旨

Expected Output全体を人間が毎回書く代わりに、**品質保証済みのDiff Tool**がInputと仮Expected Outputから機械生成した差分を期待値として扱う方式。[[AI協働034_責務Behavior_Pilot_Phase2]]での「GitDiffの『変化だけを正解として持つ』思想」という気づきから発芽し、[[AI協働036_Expected_Diff方式]]で"v0.4"まで練り上げられた、この一連のAI協働ログの中でも最も実装に近いところまで踏み込んだ設計。[[責務定義駆動テスト設計]]・[[Approval_Engineeringと構造化された意図]]の「導出可能なExpectedはViewへ落とす」を、具体的な機構として実現しようとするもの。

## 基本定義

> Expected Diff = 品質保証済みDiff Toolが、Inputと仮Expected Outputを比較して生成した差分出力。

人間が手書きした期待差分ではない。

```text
Input
  vs
仮Expected Output
  ↓ 品質保証済みDiff Tool
Expected Diff

Input
  vs
Actual Output
  ↓ 同じDiff Tool
Actual Diff

Expected Diff vs Actual Diff → Final Diff
  0件 → PASS / 差分あり → FAIL
```

**Expected側とActual側で必ず同じDiff Toolを使う**のが肝。差分生成方法そのものを個別テストごとに再承認せず、Diff Toolを一度品質保証してから多数のテストで再利用する。Gitで人間が毎回Diffアルゴリズムを承認しないのと同じ考え方。

## InputからExpected Diffまでを機械導出する

Inputも個別テストごとに人間が手作業で用意することを基本にしない。

```text
Field Definition + Validation Type + TestPattern + Type Generator Config
  ↓ Input Generator
Input
  ↓ ①完全コピー ②テスト条件を適用 ③仮Expected Output
  ↓ Diff Tool (Input vs 仮Expected Output)
Expected Diff
```

型別のInput生成方針:

- **string**: 項目固有値ではなく型共通のテンプレート(`"テスト%テストID%－%項目名称%"`)
- **integer/decimal**: 境界値(`minimum`/`minimum_minus_1`等) + 必要なら**seed付き決定論的乱数**(`valid_random`)。seedは`test_id + field_path + test_pattern`から作り、再実行しても同じ値が出ることを保証する
- **date/datetime**: 実行時の「今日」に直接依存させず、Runnerが持つ`reference_datetime`を起点に境界値やOffsetで生成する
- **boolean/enum/null**: 型定義から機械的に列挙・選択

項目固有Templateは、①項目定義→②Validation Type/TestPattern→③型別Generator Config→④汎用Generator規則、のいずれからも導出できない場合の**最終手段**とする。

## Generic Mutation Engine

仮Expected Outputを作るための汎用変更部品。責務は「指定されたpathへ、指定された構造変更を正確に適用すること」までに限定し、**値を解釈しない・型変換や業務補正を行わない**。これによりInput生成とExpected生成の両方で同じEngineを再利用できる。

## 上位原理: APPとは独立した「単純化された、信頼できる検証世界」

Expected Diff方式の一番上位に置かれている原則:

> APPとは独立した「単純化された、信頼できる検証世界」を作る。同じInputに対して、APP世界のActualと検証世界のExpectedが一致するかを見る。検証世界は現実世界のコピーではなく、品質保証可能なところまで単純化された世界でなければならない。

複雑な料金計算のような業務ロジックを検証世界にそのまま再実装するのではなく、**前提条件で世界を分割し、各条件下では単純な検証規則として保証する**。

```text
前提条件A → 単純な検証世界A
前提条件B → 単純な検証世界B
前提条件C → 単純な検証世界C
```

単純化された検証世界の必要条件として、単純であること・決定論的であること・責務が限定されていること・Input/Outputが観測可能であること・APP実装と独立していること・前提条件が明示されていること・構成部品のVersion/Guaranteeを追跡できること、が挙げられている。判断軸: **検証世界を単純に作れないなら、責務の切り方を疑う。**

## 保証継承原則

> 保証は繰り返すものではない。継承するもの。ただし、継承条件と新しく生じるリスクは必ず評価する。

UTで十分に保証したGuaranteeを、CTや上位テストで毎回再実行しない。上位では「組み合わせたことで新しく生じたリスク」(インターフェース契約、結合固有の境界、状態遷移、副作用)だけを検証する。ただし無条件の継承ではなく、次を確認する:

```text
① 下位保証が現在も有効である
② 下位保証の前提条件が上位でも成立している
③ Interface契約が変わっていない
④ 上位結合で新しい相互作用・副作用が発生していないか評価済み
⑤ 保証元のGuarantee ID/Versionを追跡できる
```

## Comparison Policy — 「無視」ではなく「意味の定義」

`updated_at`のような正当な動的変更を単純に無視すると、余計な変更の検出が機能しなくなる。そこで項目ごとに差分の意味を型として持たせる案:

```text
STRICT / IGNORE / TOLERANCE / DERIVED / DYNAMIC
```

重要なのは「差分を無視する」のではなく「その差分をどう評価するか」を事前に定義すること。

## 現時点ではAIをOracleにしない

AIは、不足しているTestPatternの提案・Input生成規則の提案・波及計算の必要性の発見などには使えるが、「APP Actual vs AIがその場で生成したExpected」を最終的な品質保証Oracleにはしない、という明確な境界が置かれている。理由は非決定性・モデル更新による結果変化・APP側とExpected生成側が同じ誤解を共有するリスク。

> AIはOracleを設計してよい。しかし、Oracleそのものにはしない。

AIが提案した検証規則は、人間承認と実装・テストを経て決定論的な品質保証済み部品へ昇格させてから利用する。

## この設計に対して指摘された未解決論点(v0.4時点)

v0.4に対するレビューで、次が「思想としては筋が通っているが、まだ機構として空白」な論点として明示的に残されている(この会話時点ではまだ解決していない、今後詰める設計課題として記録):

- **DERIVED/DYNAMIC指定項目の抜け道**: 都合の悪い項目をDYNAMICにして検証をすり抜けられてしまう危険性。DERIVED項目は別のVerification Ruleで独立に検証すべきという指摘
- **前提条件の網羅性・排他性**: 前提条件A/B/CがInput空間を本当にカバーしているか、重複マッチしないか、を誰がどう保証するか
- **保証継承の前提条件再判定**: 「下位保証の前提条件が上位でも成立しているか」を、目視ではなく品質保証済みの確認手続きとしてどう機械化するか
- **Conflict Check後の挙動**: 複数のExpected Operationが同じpathへ競合したとき、検出した後にFAILにするのか自動解決するのか人間承認を求めるのかが未定義
- **Guaranteeのsemver化**: v3→v4が後方互換な拡張か破壊的変更かを区別する仕組みがまだない

## 関連

- [[責務定義駆動テスト設計]] — 責務側のBehavior Type/TestPattern Familyと対になる、値側の機械生成方式
- [[Approval_Engineeringと構造化された意図]] — 「導出可能なExpectedはViewへ落とす」という理論的裏付け
- [[再構築可能性という品質指標]] — 同じ「独立した検証経路との一致で保証する」という発想を、システム全体の再構築という粒度で扱ったもの
- 出典: [[AI協働036_Expected_Diff方式]]、[[AI協働034_責務Behavior_Pilot_Phase2]]（初出）
