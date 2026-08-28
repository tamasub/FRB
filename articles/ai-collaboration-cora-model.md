---
title: "AI協働 判断構造モデル — CORA Model — AI協働に必要な判断構造！！"
emoji: "🧭"
type: "idea"
topics: ["ai", "promptengineering", "decisionmaking", "aicollaboration", "cora"]
published: true
---


## CORA Modelとは

**CORA Model** は、人間とAIが判断を共有するために必要な情報を整理するためのモデルである。


CORAは、次の4つの要素から構成される。

- **C = Context**
- **O = Orientation**
- **R = Restrictions**
- **A = Accountability**

日本語では、次のように対応する。


```text

C : Context
    文脈

O : Orientation
    判断軸

R : Restrictions
    制約

A : Accountability
    責務

```

さらに、CORAそのものには分類しにくい補助情報を扱うために、

```text
Optional
```

を設ける。

CORA Modelを短く表すと、次のようになる。

```text
C — なぜやる？
O — 何を重視する？
R — 何を守る？
A — 何を担う？
+ Optional — その他の判断材料
```

---

# C — Context　～文脈～

**「なぜ・何のために・どんな状況でやるのか」**

Contextは、判断の前提となる世界を表す。

現在のCORA Modelでは、特に次の3つを中心要素として扱う。

```text
目的
背景
方針
```

一般的なフレームワークや設計で使われる言葉を含めると、例えば次のようなものがContextに入る。


```text

凡例) ※：よく使う項目

Context　～文脈～
├─ Purpose               目的 ※
├─ Objective             目標
├─ Goal                  ゴール ※
├─ Background            背景 ※
├─ Situation             状況
├─ Problem               問題
├─ Issue                 課題
├─ Motivation            動機
├─ Policy                方針 ※
├─ Strategy              戦略
├─ Vision                将来像 ※
├─ Mission               ミッション
├─ Intent                意図
├─ Objective Function    目的関数 ※
├─ Scope                 対象範囲 ※
├─ In Scope              対象 ※
├─ Out of Scope          対象外 ※
├─ Stakeholder           関係者
├─ Audience              読み手・利用者
├─ Environment           環境
├─ Current State         現状
├─ Desired State         あるべき姿 ※
├─ History               経緯
├─ Assumption            前提・仮定 ※
├─ Terminology / Definitions  用語定義
└─ Knowledge             背景知識



```

---

# O — Orientation　～判断軸～

**「何を重視して、どう判断するのか」**

Orientation（**判断軸**）は、CORA Modelの中でも特に**重要な要素**である。

多くのプロンプトフレームワークでは、

- Context
- Objective
- Constraints
- Role

などは明示されるが、

**「何を基準に判断するのか」**

が独立した情報として扱われないことがある。

CORAでは、この部分を **Orientation（判断軸）** として明示する。

```text

凡例) ※：よく使う項目

Orientation　～判断軸～
├─ Judgment Criteria     判断基準 ※
├─ Evaluation Criteria   評価基準
├─ Decision Criteria     意思決定基準
├─ Priority              優先順位 ※
├─ Value                 価値
├─ Principle             原則
├─ Preference            選好
├─ Trade-off             トレードオフ
├─ Weight                重み
├─ Importance            重要度 ※
├─ Optimization Target   最適化対象
├─ Success Criteria      成功基準 ※
├─ Quality Attribute     品質特性
├─ KPI                   評価指標
├─ Metric                指標
├─ Risk Appetite         リスク許容姿勢
├─ Selection Criteria    選択基準
├─ Ranking Criteria      順位付け基準
├─ Definition of Good    良さの定義
└─ Decision Policy       判断方針

```

判断軸と制約は似ているが、役割は異なる。

```text
何を優先する？
    → Orientation

何を守らなければならない？
    → Restrictions
```

例えば、

```text
機械的に保証できる設計を最優先する
```

はOrientationである。

一方、

```text
既存データ構造を壊してはならない
```

はRestrictionsである。

---

# R — Restrictions　～制約～

**「何を守る必要があるのか／何をしてはいけないのか」**

Restrictionsは、判断や実行に対する境界を表す。

```text

凡例) ※：よく使う項目


Restrictions　～制約～
├─ Constraint            制約 ※
├─ Rule                  ルール
├─ Must                  必須 ※
├─ Must Not              禁止 ※
├─ Requirement           要件
├─ Limitation            限界 ※
├─ Boundary              境界 ※
├─ Condition             条件
├─ Precondition          前提条件 ※
├─ Guard                 ガード条件 ※
├─ Compliance            準拠事項
├─ Regulation            規制
├─ Policy Rule           規定
├─ Standard              標準
├─ Security Rule         セキュリティ制約
├─ Privacy Rule          プライバシー制約
├─ Resource Limit        リソース制限
├─ Time Limit            時間制限
├─ Budget Limit          予算制約
├─ Technical Limit       技術的制約
├─ Compatibility         互換性制約
├─ Dependency Rule       依存条件
├─ Validation Rule       検証ルール
├─ Acceptance Rule       受入条件
└─ Invariant             不変条件

```

ソフトウェア設計でよく使われる、

```text
Validation
Guard
Invariant
Boundary
Contract
```

なども、Restrictionsと強く関係する。

ただし、例えばContractのように、

- 責務
- 制約

の両方を含む概念も存在する。

CORAでは、無理に一つのカテゴリへ押し込まず、複数要素との関係を許容する。

---

# A — Accountability　～責務～

**「誰・何が、何を担い、何を保証するのか」**

Accountabilityは、単なるRoleより広い。

「あなたはシステム設計者です」というだけならRoleだが、

```text
既存動作を維持しながら責務境界を整理し、
変更理由を説明する
```

まで含めると、より明確なAccountabilityになる。

```text

凡例) ※：よく使う項目


Accountability　～責務～
├─ Responsibility        責務 ※
├─ Role                  役割 ※
├─ Guarantee             保証 ※
├─ Expected              期待される結果 ※
├─ Duty                  義務
├─ Ownership             所有責任
├─ Accountability        説明責任
├─ Authority             権限 ※
├─ Decision Right        決定権
├─ Task                  実行事項
├─ Action                行為
├─ Behavior              振る舞い ※
├─ Function              機能
├─ Capability            能力
├─ Deliverable           成果物
├─ Output                出力 ※
├─ Interface             インターフェース ※
├─ Input Responsibility  入力責務
├─ Output Responsibility 出力責務
├─ Owner                 担当
├─ Reviewer              レビュー責務
├─ Approver              承認責務
└─ Executor              実行責務

```

---

# Optional — その他の判断支援情報

CORAの4分類に、すべての情報を無理やり押し込む必要はない。

そのため、CORAでは補助領域として **Optional** を設ける。

Optionalは、

**重要ではない情報**

という意味ではない。

CORAの判断構造そのものではないが、

**判断・実行・検証を支えるために必要となる追加情報**

を置く領域である。

```text

凡例) ※：よく使う項目

Optional
├─ Example        例
├─ Sample         サンプル
├─ Few-shot       Few-shot例
├─ Reference      参考情報
├─ Evidence       根拠・証跡
├─ Source         情報源
├─ Format         出力形式 ※
├─ Tone           トーン
├─ Style          文体 ※
├─ Language       言語
├─ Template       テンプレート
├─ Schema         スキーマ ※
├─ Tool           使用ツール
├─ Method         手法
├─ Procedure      手順 ※
├─ Workflow       ワークフロー
├─ Data           データ
├─ Input          入力値
├─ Expected       期待値 ※
├─ Actual         実績 ※
├─ Diff           差分 ※
├─ TestPattern    テストパターン ※
├─ Fixture        テストデータ
├─ Metadata       メタデータ
├─ Note           補足
└─ Reference URL  参考URL

```

Optionalを設ける理由は、CORAを閉じた分類体系にしないためでもある。

まずは分類できない情報をOptionalへ置く。

その後、同じ性質を持つ情報が増えてきた場合は、

```text
Optionalに同種の情報が集まる
        ↓
独立した意味を持つことに気づく
        ↓
必要なら将来CORA Modelを拡張する
```

という進化を許容する。

---

# 一般的なフレームワークの言葉をCORAへ対応させる

プロンプトエンジニアリングなどで使われる一般的な要素も、CORAへ整理できる。

例えば、

```text
Role
Objective
Context
Knowledge
Constraints
Success Criteria
Priorities
Examples
Output Format
Tone
```

をCORAへ対応させると、次のようになる。

| 一般的な用語 | CORA |
|---|---|
| Role | A : Accountability |
| Objective | C : Context |
| Context | C : Context |
| Knowledge | C : Context |
| Constraints | R : Restrictions |
| Success Criteria | O : Orientation |
| Priorities | O : Orientation |
| Trade-offs | O : Orientation |
| Rules | R : Restrictions |
| Responsibilities | A : Accountability |
| Examples | Optional |
| Output Format | Optional |
| Tone | Optional |
| Reference | Optional |

---

# ROCK FrameworkをCORAで見る

例えば、プロンプト設計で使われるROCKという整理が、

```text
R = Role
O = Objective
C = Context
K = Knowledge / Constraints
```

だとすると、CORAでは次のように整理できる。

```text
Role
→ A : Accountability

Objective
→ C : Context

Context
→ C : Context

Knowledge
→ C : Context

Constraints
→ R : Restrictions
```

この整理を見ると、ROCKには、

```text
O : Orientation
判断軸
```

に相当する情報が独立していない。

CORAでは、

**「AIに何をしてほしいか」だけではなく、
「何を重視して判断してほしいか」まで共有する**

ことを重視する。

---

# CORAはプロンプトテンプレートではない

CORAは、単に「良いプロンプトを書くための順番」を定義するものではない。

目的は、

**人間とAIが判断を共有するために必要な情報を構造化すること**

にある。

そのため、対象はプロンプトエンジニアリングだけに限定されない。

例えば、

```text
Prompt Engineering
AI Collaboration
Decision Making
Project Management
Requirements Engineering
Software Design
Testing
Approval Engineering
```

などで使われている言葉も、

一度、

```text
C
O
R
A
Optional
```

のどこに属するのかを考えることができる。

---

# CORA Modelの現在の定義

現時点では、CORA Modelを次のように定義する。

> **CORA Modelは、人間とAIが判断を共有するために必要な情報を、Context / Orientation / Restrictions / Accountability の4領域へ整理するモデルである。**
>
> **それ以外の判断支援情報はOptionalとして保持する。**

短く言えば、

```text
C — なぜやる？
O — 何を重視する？
R — 何を守る？
A — 何を担う？
+ Optional — その他の材料
```

である。

CORAは完成した分類体系を目指すものではない。

実際に使いながら、

- 足りない要素
- 重複する要素
- 境界が曖昧な要素
- Optionalから独立させるべき要素

を発見し、更新していく。

**CORA自体も、AI協働の中で育てていくモデルである。**


---

[AI駆動開発研究日誌や、思考拡張・AI承認駆動開発の記事はこちら](https://zenn.dev/frb_tamasub)

この思考拡張・AI駆動開発の実例として、私はFRB（Fishing Rod Benchmark）という個人研究を続けている。  
釣り竿の感度を振動として比較・可視化しようとする個人研究だが、そこで繰り返してきたのは「差分」「再現性」「違和感」「構造化」であり、今回の思考にもその影響がかなり入っている。

- [FRB（Fishing Rod Benchmark）釣り竿の「感度」を数値化する話 宣言](https://qiita.com/tamasub/items/2b6649748e1772b7eec1)
