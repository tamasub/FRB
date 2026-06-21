# 📄 FRB_ARCHITECTURE
*(source: `FRB_ARCHITECTURE.md`)*

## FRB Architecture (Draft)

FRB（Fishing Rod Benchmark）の全体構造を定義する。

---

### Overview

FRBは、
感度（振動体験）を

**構造化・再現・共有するためのシステム**

である。

---

### Structure

FRBは以下の層で構成される。

#### 1. Experience Layer

人間が感じる感度。

* コツン
* ぬぅ
* モゾ

👉 すべての出発点

---

#### 2. Input Layer

再現可能な入力。

* 床擦り（Phase1）
* 擬似バイト（Phase2）

👉 感度を発生させる条件

---

#### 3. Measurement Layer

振動の観測。

* 加速度
* 音
* FFT解析

👉 振動を可視化

---

#### 4. Data Layer

測定結果の構造化。

* FRB Score
* JSONフォーマット

👉 データとして記録

---

#### 5. Specification Layer

定義とルール。

* FRB_SPEC.md
* FRB_DATA_SPEC.md
* FRB_VERSIONING.md

👉 比較可能性を担保

---

#### 6. Application Layer

活用。

* ロッド比較
* 選択支援
* データ共有

👉 FRBの目的

---

### Flow

```mermaid
flowchart TD

A[Experience]
→ B[Input]
→ C[Measurement]
→ D[Data]
→ E[Specification]
→ F[Application]
```

---

### Key Concept

FRBは、

**体験 → 構造 → データ**

へと変換する仕組みである。

---

### Position

FRBは、

単なる測定手法ではない。

**文化と規格を接続する構造である。**

---

### Status

Draft / evolving

---

### Summary

* 感度は体験から始まる
* 入力で再現する
* 測定で観測する
* データで記録する
* 規格で共有する

---

**FRBは、体験を構造に変えるアーキテクチャである。**



### Revision History

- 2026-03-26 : v0.1-draft 初版


---

# 📄 FRB_DATA
*(source: `FRB_DATA.md`)*

## FRB Data

FRBは、
人が感じている振動を
データとして扱うための試みである。

---

### なぜデータ化するのか

感度はこれまで、

- 主観
- 感覚
- 経験

で語られてきた。

しかしそれは、

比較できない  
共有できない  

---

### FRBの考え方

FRBでは、

感度 = 振動の特徴

と定義する。

つまり、

感覚はデータに変換できる。

---

### データとして扱う対象

- 振動量
- 周波数特性
- 伝達特性

---

### データ構造

FRBでは、

入力条件と結果をセットで扱う。

→ 詳細は FRB_DATA_SPEC.md を参照

---

### 目的

データ化の目的は評価ではない。

選択である。

---

感度は分かち合って初めて本物になる。




### Revision History

- 2026-03-14 : v0.1-draft 初版


---

# 📄 FRB_DATA_SPEC
*(source: `FRB_DATA_SPEC.md`)*

## FRB Data Specification (Draft)

Fishing Rod Benchmark (FRB) の測定結果を、
再現可能・比較可能・共有可能な形で記録するための
データ仕様（Draft）を定義する。

---

### Status

**Draft**

本仕様は初期ドラフトであり、
今後の実験・検証に応じて変更される可能性がある。

特に以下は将来的に変化しうる。

* Phase1 の代表素材および識別子
* Phase2 の指標名称
* 各 Phase の入力条件
* 補助メタデータ項目

FRBでは、
**意味のある比較構造を維持しながら、項目の進化を許容すること**
を重視する。

---

### 1. Purpose

FRB_DATA_SPEC は、
FRB測定結果を機械可読な形で記録・共有するための
共通フォーマットである。

目的は以下の通り。

* 測定結果を記録できること
* 入力条件と結果をセットで保持できること
* 比較・集計・可視化に利用できること
* 指標の追加・削除・名称変更に耐えられること

---

### 2. Design Principle

FRB_DATA_SPEC は、以下の設計思想に基づく。

#### 2.1 固定するもの

以下は基本的に固定構造として扱う。

* schema_version
* frb_version
* phase
* test
* metrics
* notes

---

#### 2.2 固定しないもの

以下は将来的な変更を許容する。

* 指標キー（例: J / F / S / Impulse / Suction / Weed）
* 素材名
* 入力方式
* 補助説明
* メタ情報の追加

---

#### 2.3 基本方針

FRBでは、

**項目名を固定しない。枠だけを固定する。**

このため、
スコアは固定カラムではなく、
**可変指標の集合（metrics）** として保持する。

---

### 3. Top-Level Structure

FRBデータは、以下のトップレベル構造を持つ。

```json
{
  "schema_version": "0.1-draft",
  "frb_version": "draft",
  "phase": 1,
  "test": {},
  "metrics": [],
  "notes": []
}
```

---

### 4. Field Definitions

#### 4.1 schema_version

このデータ仕様自体のバージョン。

```json
"schema_version": "0.1-draft"
```

---

#### 4.2 frb_version

FRB規格・定義側のバージョン。

```json
"frb_version": "draft"
```

---

#### 4.3 phase

測定対象のフェーズ番号。

```json
"phase": 1
```

---

#### 4.4 test

入力条件・環境条件・試験条件を格納するオブジェクト。

```json
"test": {
  "type": "surface_response",
  "environment": "indoor",
  "angle_deg": 45
}
```

---

#### 4.5 metrics

測定結果本体（可変指標）。

```json
"metrics": [
  {
    "key": "J",
    "label": "絨毯",
    "score": 99,
    "description": "low_band_response"
```



### Revision History

- 2026-03-14 : v0.1-draft 初版


---

# 📄 FRB_EXPERIMENTS
*(source: `FRB_EXPERIMENTS.md`)*

## FRB Experiments

FRBに関する実験ログを記録する。

---

### 2026-02-10 miniリング

- 海の中が見えた気がした
- 感度変化が大きかった

---

### 2026-02-11 ダイソースイベル

- 振り抜きが軽い
- 糸擦れ振動を強く感じた
- ロッドがブルンブルン震える感覚があった

---

### 2026-02-15〜17 トップガイド交換

- チタンフレーム
- TORZITEリング
- #6Mで床擦り時の振動変化を強く感じた

---

### 2026-02-20〜22 EVAグリップ除去

- リールシートが震え始めた
- 手元感度の変化を感じた

---

### Notes

- 周波数比率だけでは説明できない違和感あり
- 倍音構造の観察が必要
- 数値と体感の対応づけが重要


### Revision History

- 2026-03-14 : v0.1-draft 初版


---

# 📄 FRB_MANIFESTO
*(source: `FRB_MANIFESTO.md`)*

## FRB Manifesto

Fishing Rod Benchmark (FRB) は  
ロッドの「感度」を共有する文化を作るプロジェクトである。

Fishing Rod Benchmark は、
釣り人が知覚する振動を基準として
ロッド感度を数値化する
人間中心の測定規格である。

---

### Problem

ロッド感度は長い間

<<<<<<< HEAD
=======

>>>>>>> 889a3cb (FRB Manifesto New)
- 主観
- 感覚
- 言葉

で語られてきた。

しかしそれは

共有できない。

比較できない。

議論できない。

---

### Discovery

床擦りという発見。

同じ床を擦れば  
同じ振動が出る。

つまり

ロッド感度は  
再現可能な現象である。

---

### Vision

FRBは

ロッド感度を

- 再現可能
- 測定可能
- 共有可能

にする。

---

### Philosophy

感度は分かち合って初めて本物になる。

---

### Method

FRBは

- 床擦り
- 振動測定
- FFT解析
- AI解析

を用いて

ロッド振動特性を記録する。

---

### Culture

FRBは

技術だけではない。

釣り文化である。

---

### Declaration

2026/3/11

FRBプロジェクト開始。

---

### Current Status

釣果  
ボラ１匹



### Revision History

- 2026-03-14 : v0.1-draft 初版


---

# 📄 FRB_METHOD
*(source: `FRB_METHOD.md`)*

**Note: This specification is currently in an experimental and validation phase.**

---

### What is FRB?

FRB (Fishing Rod Benchmark) is

a **proposed common metric and measurement framework**  
for capturing and comparing fishing rod “sensitivity” as vibration.

Traditionally, “sensitivity” has been described as human experience:

- bite detection  
- environmental awareness  
- lure control  

FRB introduces a different perspective:

**Sensitivity is redefined as a structure of vibration.**

---

### Background

Rod sensitivity has historically been described using vague terms such as:

- high sensitivity  
- low sensitivity  
- rich information  

However,

even when people say “high sensitivity,”  
the actual experience differs from person to person.

---

### A Shift in Perspective

In the PC world, storage performance is evaluated using metrics such as:

- Sequential Read  
- Sequential Write  
- IOPS (random access performance)

In contrast, in the fishing rod world,

only subjective expressions exist:

- “sensitive”  
- “not sensitive”  

FRB introduces a new idea:

**to measure sensitivity itself.**

In other words,

FRB transforms  
**experienced sensation into a measurable phenomenon.**

---

### Relationship to SSD Benchmarking

FRB applies the concept of performance benchmarking to fishing rods.

| Category | FRB | Target User | SSD Benchmark | Target User |
|--------|-----|------------|--------------|------------|
| Phase 1 | Surface Response (frequency-based score) | Beginners | Sequential (Read / Write) | General users |
| Phase 2 | Simulated Bite Response | Intermediate+ | IOPS (I/O per second) | Advanced users |

---

### Definition

In FRB,

**Sensitivity = characteristics of vibration**

---

### FRB Architecture

A structural overview of FRB:

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/3069714/cb5ebf64-b8b4-494f-83d9-a9934100dd84.png)

---

### Relationship to Traditional “Sensitivity”

Traditional classifications:

- Bite sensitivity  
- Environmental sensitivity  
- Operational sensitivity  

These are all based on human perception.

---

FRB redefines them as vibration structures:

- Bite sensitivity → **Input Response (Phase 2)**  
- Environmental sensitivity → **Low–Mid frequency response (Phase 1)**  
- Operational sensitivity → **Frequency + Input response (Phase 1 + Phase 2)**  

---

FRB decomposes and reconstructs  
the ambiguous concept of sensitivity.

---

### Measurement Targets

FRB focuses on:

- vibration magnitude  
- frequency characteristics  
- transmission characteristics  

These represent

**what humans are actually perceiving.**

---

## Phase Structure (Draft Definition)

FRB separates:

- evaluation (Score)  
- input (Test)

---

### Phase 1 (Fundamental Metrics)

#### Overview

Continuous contact input generates vibration,  
allowing evaluation of

**vibration characteristics (magnitude and frequency)**

---

#### Phase1 Score

Evaluates vibration magnitude and frequency distribution:

**“How much vibration is present”**

##### Example:

:::note info
Phase1 Score (Surface Response)

J: 99 (Carpet: low-frequency response)  
F: 85 (Flooring: mid-frequency response)  
S: 72 (Stainless: high-frequency response)
:::

---

#### Phase1 Input (Test)

Vibration is generated by rubbing the rod against materials.

This method is called:

**FRB Surface Response Test**

---

### Phase 2 (Applied Metrics)

#### Overview

Input is defined as changes in tension along the line,  
evaluating the rod’s

**response characteristics (transmission and perception)**

---

#### Phase2 Score

Evaluates transmission efficiency and response characteristics:

**“How the rod responds to changes in load”**

---

Fish bites, physically, are changes in force:

- instantaneous impact (Impulse)  
- sustained pull (Suction)  
- interference (Weed)  

All of these can be observed as

**changes in line tension (load variation).**

---

##### Example:

:::note info
FRB Phase2 Score (Simulated Bite Response)

Impulse: 92 (impact response)  
Suction: 78 (pull-in response)  
Weed: 65 (interference response)
:::

---

#### Phase2 Input (Test)

Simulated load changes equivalent to fish bites are applied  
to the rod under controlled conditions.

This method is called:

**FRB Phase2 Bite Simulator**

(e.g., rubber bands, springs, controlled tension release)

*Input methods are currently under validation.*

---

### Design Philosophy

FRB is based on the following principles:

---

#### Scalability and Simplicity

Each phase is limited to:

- maximum 3 evaluation metrics  

While allowing expansion through additional phases.

- 1 phase = up to 3 metrics  
- phases = extendable  

Complexity is absorbed by structure,  
while keeping interpretation simple.

---

FRB is not designed for evaluation,

but for **selection.**

---

#### Reproducibility

FRB prioritizes not absolute precision, but:

**reproducibility under consistent conditions**

- executable indoors  
- no specialized equipment required  
- comparable under controlled conditions  

---

### Key Point

FRB does NOT measure catch results.

It measures:

**the structure of what is being perceived.**

---

### Vision

Instead of saying:

“This rod is sensitive”

we aim to say:

“This rod has these vibration characteristics”

---

### Current Status

This definition is still in the draft stage.

However, at least one thing can be stated:

---

Rod differences can be captured  
as vibration.

---

(Next)  
[Why has rod sensitivity never been quantified? — FRB Motivation](https://qiita.com/tamasub364/items/662889a02a8db24ef742)

---

**FRB is not a metric for evaluation,  
but a metric designed for selection.**


### Revision History

- 2026-03-14 : 初版


---

# 📄 FRB_SPEC
*(source: `FRB_SPEC.md`)*

## FRB Data Specification (Draft)

Fishing Rod Benchmark (FRB) の測定結果を、
再現可能・比較可能・共有可能な形で記録するための
データ仕様（Draft）を定義する。

---

### Status

**Draft**

本仕様は初期ドラフトであり、
今後の実験・検証に応じて変更される可能性がある。

特に以下は将来的に変化しうる。

* Phase1 の代表素材および識別子
* Phase2 の指標名称
* 各 Phase の入力条件
* スコア項目の追加・削除

FRBでは、
**比較構造を維持しながら、スコアの進化を許容すること**
を重視する。

---

### 1. Purpose

FRB_DATA_SPEC は、
FRB測定結果を機械可読な形で記録・共有するための
共通フォーマットである。

目的は以下の通り。

* 測定結果を記録できること
* 入力条件と結果をセットで保持できること
* 比較・集計・可視化に利用できること
* スコア項目の変化に耐えられること

---

### 2. Design Principle

FRB_DATA_SPEC は、以下の設計思想に基づく。

#### 2.1 固定するもの

* schema_version
* frb_version
* phase
* test
* scores
* notes

---

#### 2.2 固定しないもの

* スコアキー（J / F / S / Impulse / Suction / Weed など）
* 素材名
* 入力方式
* スコア項目の構成

---

#### 2.3 基本方針

FRBでは、

**スコア項目は固定しない。構造のみ固定する。**

このため、
スコアは固定カラムではなく、
**可変スコア集合（scores）** として保持する。

---

### 3. Top-Level Structure

```json
{
  "schema_version": "0.1-draft",
  "frb_version": "draft",
  "phase": 1,
  "test": {},
  "scores": [],
  "notes": []
}
```

---

### 4. Field Definitions

#### 4.1 schema_version

データ仕様のバージョン。

```json
"schema_version": "0.1-draft"
```

---

#### 4.2 frb_version

FRB規格側のバージョン。

```json
"frb_version": "draft"
```

---

#### 4.3 phase

測定フェーズ。

```json
"phase": 1
```

---

#### 4.4 test

入力条件・環境条件。

```json
"test": {
  "type": "surface_response",
  "environment": "indoor",
  "angle_deg": 45
}
```

---

#### 4.5 scores

FRB Score を可変形式で保持する。

```json
"scores": [
  {
    "key": "J",
    "label": "絨毯",
    "score": 99,
    "description": "low_band_response"
  }
]
```

##### 各項目

* `key` : 識別子（変更可能）
* `label` : 表示名
* `score` : 数値
* `description` : 補足説明

---

#### 4.6 notes

体感メモ。

```json
"notes": [
  "ジンジン感あり"
]
```

---

### 5. Phase-Specific Structure

#### 5.1 Phase1（Surface Response）

```json
{
  "schema_version": "0.1-draft",
  "frb_version": "draft",
  "phase": 1,
  "test": {
    "type": "surface_response",
    "environment": "indoor",
    "surface_set": "default_v1",
    "angle_deg": 45,
    "operator": "manual"
  },
  "scores": [
    { "key": "J", "label": "絨毯", "score": 99 },
    { "key": "F", "label": "フローリング", "score": 85 },
    { "key": "S", "label": "ステンレス", "score": 72 }
  ],
  "notes": [
    "高域強め"
  ]
}
```

---

#### 5.2 Phase2（Simulated Bite Response）

```json
{
  "schema_version": "0.1-draft",
  "frb_version": "draft",
  "phase": 2,
  "test": {
    "type": "bite_simulator",
    "environment": "indoor",
    "input_method": "rubber_impulse_3stage",
    "input_version": "draft_v1"
  },
  "scores": [
    { "key": "Impulse", "label": "コツン", "score": 92 },
    { "key": "Suction", "label": "ぬっ", "score": 78 },
    { "key": "Weed", "label": "モゾ", "score": 65 }
  ],
  "notes": [
    "コツン強い"
  ]
}
```

---

### 6. Why scores is Array

* スコアの追加・削除に強い
* 順序を保持できる
* UI / DB と相性が良い
* 将来の拡張に強い

---

### 7. Extension Policy

拡張可能：

* test項目追加
* scores属性追加
* top-level項目追加

---

### 8. Minimal Example

```json
{
  "schema_version": "0.1-draft",
  "frb_version": "draft",
  "phase": 1,
  "test": { "type": "surface_response" },
  "scores": [
    { "key": "J", "score": 99 }
  ],
  "notes": []
}
```

---

### 9. Summary

* 構造は固定
* スコアは可変
* scoresで表現
* Draft前提

---

**FRBは、体験から生まれ、スコアとして共有される。**


### Revision History

- 2026-03-14 : 初版
- 2026-03-26 : 概念整理更新


---

# 📄 FRB_STORY
*(source: `FRB_STORY.md`)*

## FRB Story

これは、ロッド感度を数値化しようとしている人間の記録である。

しかし本当は、
ただ魚のアタリを感じたかっただけなのかもしれない。

---

### Prologue — 2013

メンタル不良。
2年半休職、離婚。

それでも「鼻歌ToMIDI」は
窓の杜、Yahoo、紙雑誌に掲載された。

技術は、人を救うのかもしれない。

---

### Prelude — 2023

ルアーニスト購入。

しかし、ほとんど使われなかった。

まだ釣りも、
ロッド感度も、
深く考えていなかった。

---

### Collapse — 2025

メンタル不良。

2025年11月、休職。

---

### The Discovery

床擦りという発見。

「これ、みんな知ってるの？」

その瞬間、
ロッド感度の世界が開けた。

---

### AI Era

AIとESP32で、
振動測定装置が立ち上がる。

AIは謝らない。
それでも神に一番近い。

---

### Epilogue

「俺はただ海を感じることで満足できる人間になったんだ」

なお、この時点の釣果はボラ１匹である。




### Revision History

- 2026-03-14 : v0.1-draft 初版


---

# 📄 FRB_TERMS
*(source: `FRB_TERMS.md`)*

## FRB Terms

FRBで使う用語を定義する。

---

### 感度

ロッドを通じて伝わる振動・変化を、人が感じ取れる性質。

FRBでは単なる主観ではなく、  
再現可能な現象として扱うことを目指す。

---

### 床擦り

ロッド先端側のルアーまたは治具を床に接触させ、  
一定条件で擦ることで振動を発生させるテスト手法。

FRBの原点。

---

### 手元感度

振動がグリップ、リールシート、手元にどれだけ伝わるかという感覚。

---

### 音が太い

低域が豊かで、密度感のある振動・音の印象。

ただし、周波数比率だけでは説明できない可能性がある。

---

### シャープ

立ち上がりが速く、輪郭が明瞭な振動の印象。

---

### 高級感がある

単なる強さではなく、  
振動のまとまり、雑味の少なさ、心地よさを含んだ主観表現。

---

### 倍音構造

主ピーク以外の周波数成分を含めた全体構造。

FRBでは重要な研究対象。

---

### 共振棒鳥肌

ロッドや構造物が強く共振した時に、  
感覚的に「鳥肌が立つ」と表現したくなる現象。

---

### 室内再現性

屋外の実釣ではなく、  
室内で同じ条件を再現して比較できる性質。

FRBの重要原則のひとつ。

---

### 擬似魚アタック

魚のアタリに似た入力を人工的に与える試験構想。

将来的なFRB第2層テスト候補。

### 脳がバグる問題

耳から聞こえる音が
手で感じる振動の認識を
乱してしまう現象

### 対話思考拡張（Dialogic Cognitive Expansion）

対話を通じて、  
自分では気づけなかった思考構造が露出し、  
思考が再構築・拡張される現象。

FRBにおける「体験の構造露出」と同様に、  
思考もまた対話によって構造が露出することで、  
初めて理解・更新される対象である。

本プロジェクトにおいては、  
人間とAIの対話を通じて発生する思考変化を指す。

---

### 思考デバッグ（Thinking Debugging）

対話思考拡張の一形態。

AIとの対話によって、  
自分の前提・矛盾・思考の癖が露出し、  
まるでデバッグのように思考が修正されていく現象。

主に、思考のズレや違和感に気づく過程を強調する表現として用いる。

---

※使い分け：

- Qiita（技術・概念説明） → 対話思考拡張  
- はてなブログ（物語・感情） → 思考デバッグ


### Revision History

- 2026-03-14 : v0.1-draft 初版
- 2026-04-03 : v0.2-draft 対話思考拡張 追加
-


---

# 📄 FRB_VERSIONING
*(source: `FRB_VERSIONING.md`)*

## FRB Versioning Policy (Draft)

FRB（Fishing Rod Benchmark）の仕様・データ定義のバージョン管理ルールを定義する。

---

### 1. Purpose

FRBは進化する規格である。

そのため、

* どの定義に基づくものか
* どの時点の仕様か

を明確にする必要がある。

本ポリシーは、
FRBの進化を整理し、
比較可能性と拡張性を両立することを目的とする。

---

### 2. Version Structure

FRBでは以下の形式でバージョンを表現する。

```
<major>.<minor>-<status>
```

例：

* 0.1-draft
* 0.2-beta
* 1.0
* 1.1

---

### 3. Status Definition

#### 3.1 draft

* 検証段階
* 仕様が頻繁に変わる
* 後方互換性は保証しない

例：

```
0.1-draft
```

---

#### 3.2 beta

* 基本構造が安定
* 実用テスト段階
* 大きな変更は減るが、まだ調整あり

例：

```
0.5-beta
```

---

#### 3.3 stable（表記なし）

* 安定版
* 比較基準として使用可能
* 後方互換性を意識

例：

```
1.0
```

---

### 4. Version Increment Rules

#### 4.1 major（X.0）

以下の場合に変更する。

* スコア構造の根本変更
* Phase構造の変更
* 比較互換性が失われる変更

例：

```
0.x → 1.0
```

---

#### 4.2 minor（0.X）

以下の場合に変更する。

* スコア項目の追加・削除
* test条件の拡張
* descriptionの強化

例：

```
0.1 → 0.2
```

---

#### 4.3 status変更

* draft → beta → stable

例：

```
0.2-draft → 0.2-beta → 1.0
```

---

### 5. Scope of Versioning

FRBでは以下を個別に管理する。

#### 5.1 FRB Specification

* FRB_SPEC.md
* 概念・定義

例：

```
frb_version: 0.1-draft
```

---

#### 5.2 Data Specification

* FRB_DATA_SPEC.md
* データ構造

例：

```
schema_version: 0.1-draft
```

---

#### 5.3 Measurement Data

実験データは、
どのバージョンの仕様に基づくかを明示する。

```json
{
  "schema_version": "0.1-draft",
  "frb_version": "0.1-draft"
}
```

---

### 6. Compatibility Policy

#### 6.1 draft

* 互換性を保証しない
* 自由に変更可能

---

#### 6.2 beta

* できるだけ互換性を維持
* 破壊的変更は最小限

---

#### 6.3 stable

* 後方互換性を重視
* 破壊的変更はmajor更新のみ

---

### 7. Tagging (Git)

FRBではGitタグを使用して
バージョンを固定する。

例：

```
v0.1-draft
v0.2-beta
v1.0
```

---

### 8. Practical Rule

FRBの現時点の運用ルール：

* 今はすべて **draft**
* 気にせず変更してよい
* ただしバージョンは必ず上げる

---

### 9. Summary

* FRBは進化する規格である
* バージョンで状態を表す
* draft → beta → stable の流れを持つ
* 互換性は段階的に強化する

---

**FRBは完成するものではなく、更新され続けるものである。**


### Revision History

- 2026-03-26 : 初版


---

# 📄 README
*(source: `README.md`)*

## FRB — Fishing Rod Benchmark

*Sensitivity becomes real when it can be shared.*

～　[感覚は分かち合って初めて本物になる](https://qiita.com/tamasub364/items/2b6649748e1772b7eec1)　～

*Turning fishing rod vibration into shareable sensitivity metrics.*

![status](https://img.shields.io/badge/status-research-blue)
![platform](https://img.shields.io/badge/platform-ESP32-green)
![analysis](https://img.shields.io/badge/analysis-FFT-orange)

---

### 🎯 Overview

**FRB (Fishing Rod Benchmark)** is a project to create a shared language for **fishing rod sensitivity**.

Fishing rod sensitivity has traditionally been subjective and difficult to describe.  
FRB aims to make it **observable, measurable, and shareable**.

The goal is **not replacing human feeling**.  
The goal is making **human perception shareable**.

---

### 🔍 Concept

FRB transforms:

- human experience  
→ into  
- measurable and comparable data  

This allows rod performance to be discussed in a structured way.

> **Sensitivity = characteristics of vibration**

---

### 🧱 Architecture

FRB is composed of two main phases:

#### Phase 1 — Surface Response

- Measures vibration characteristics (magnitude + frequency)  
- Input: continuous contact (rubbing test)  
- Purpose: understand frequency response  

👉 Comparable to **Sequential Read/Write** in SSD benchmarks

---

#### Phase 2 — Simulated Bite Response

- Measures response to load changes (tension variation)  
- Input: simulated bite (controlled impulse / pull)  
- Purpose: evaluate transmission characteristics  

👉 Comparable to **IOPS (random access)** in SSD benchmarks

---

### 📊 Structure

| Category | FRB | SSD Benchmark |
|--------|-----|--------------|
| Phase 1 | Surface Response | Sequential |
| Phase 2 | Bite Response | IOPS |

---

### 🧪 Example Scores

#### Phase 1

:::note info
Phase1 Score (Surface Response)

J: 99 (Carpet / Low frequency)  
F: 85 (Flooring / Mid frequency)  
S: 72 (Stainless / High frequency)
:::

---

#### Phase 2

:::note info
FRB Phase2 Score (Simulated Bite Response)

Impulse: 92   (impact response)  
Suction: 78   (pull response)  
Weed: 65      (interference response)
:::

---

### 🧠 Key Idea

Fish bites are not “mysterious signals.”

They are:

> **changes in force (tension variation)**

FRB treats all bite sensations as:

- Impulse (impact)  
- Suction (pull)  
- Weed (interference)  

→ All observable as **load changes on the line**

---

### 🎯 Design Philosophy

#### 1. Reproducibility

- Indoor testing possible  
- No special equipment required  
- Comparable under consistent conditions  

---

#### 2. Simplicity

- Max 3 metrics per phase  
- Expandable via additional phases  

---

#### 3. Purpose

FRB is not designed for evaluation.

> **FRB is a metric for selection.**

---

### 🌍 Vision

Instead of:

> “This rod is sensitive”

We aim for:

> “This rod has these vibration characteristics”

---

### 📚 Repository Structure

This repository contains the following core documents:

* **FRB Method** — measurement framework
  → [FRB Method](./docs/FRB_METHOD.md)

* **FRB Spec** — formal definitions
  → [FRB Spec](./docs/FRB_SPEC.md)

* **FRB Data Spec** — data structure (Draft)
  → [FRB Data Spec](./docs/FRB_DATA_SPEC.md)

* **FRB Versioning** — versioning rules
  → [FRB Versioning](./docs/FRB_VERSIONING.md)

* **FRB Terms** — terminology
  → [FRB Terms](./docs/FRB_TERMS.md)

* **FRB Experiments** — experimental logs
  → [FRB Experiments](./docs/FRB_EXPERIMENTS.md)

* **FRB Story** — origin and background
  → [FRB Story](./docs/FRB_STORY.md)

* **FRB Blog** — origin and background
  → [FRB Blog](./FRB_Blog/README.md)

* **FRB Tools** — origin and background
  → [FRB Tools](./tools/README.md)


---


### 🧭 Where to Start

👉 If you're new:

- Read: `FRB_METHOD.md`

👉 If you're technical:

- Check: `FRB_EXPERIMENTS.md`

👉 If you're curious about the origin:

- Read: `FRB_STORY.md`

---

### ⚠️ Status

FRB is currently in:

> **Draft / Experimental phase**

The methodology is under continuous validation.

---

### ✨ Final Note

FRB does not measure:

- catch rate  
- fishing skill  

FRB measures:

> **the structure of what you feel**

---

### 🚀 Future

- Standardization of input methods  
- Sensor-based validation (ESP32 / FFT)  
- Open benchmark dataset  

---

### 🧩 Philosophy

> Sensitivity becomes real only when it can be shared.


### Revision History

- 2026-03-14 : 初版
- 2026-03-26 : ファイル構造見直し

