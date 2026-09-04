---
address: c-000011
type: concept
title: "Approval Engineeringと構造化された意図 (Structured Intent)"
created: 2026-09-04
updated: 2026-09-04
status: developing
tags:
  - concept
  - approval-engineering
  - structured-intent
  - test-code-culture
related:
  - "[[400KS人月仮説と承認単位のシフト]]"
  - "[[責務定義駆動テスト設計]]"
  - "[[再構築可能性という品質指標]]"
  - "[[Expected_Diff方式と検証世界の設計原則]]"
sources:
  - "[[AI協働035_構造化された意図とApprovalEngineering]]"
claim_ids:
  - clm-code-as-view
  - clm-approval-engineering-def
  - clm-type-hierarchy-distillation
complexity: advanced
domain: "AI駆動開発・ソフトウェア資産論"
aliases:
  - Approval Engineering
  - Structured Intent
  - Code as View
  - Type Catalog
---

# Approval Engineeringと構造化された意図 (Structured Intent)

## 要旨

「人間の承認対象はコードから徐々に上位へ移っていく」という観察を起点に、**コードは意図を実行環境へ投影したViewである**という中心的な言葉へたどり着き、そこから「Approval Engineering」という工学領域を定義した回。[[400KS人月仮説と承認単位のシフト]]をさらに理論化したもので、[[責務定義駆動テスト設計]]のBehavior Type/TestPattern Familyとも同じ「型に承認を圧縮する」構造でつながっている。

## 承認対象の階段

```text
コード → テストコード → テストケース → 責務 → 保証 → 制約 → 判断軸 → 意図
```

上位に行くほど、下位の大量成果物を毎回承認し直す必要がなくなる、という前提。

## コードはViewである

> コードは、意図を実行環境へ投影したViewである。

この言葉は比喩ではなく、`Intent = Source` / `Code = Projection / View` という関係の反転として提示されている。実装言語(JavaScript/C#/Python等)は「その時代の実行環境に合わせた投影先」に過ぎず、意図さえ残っていれば別の実行環境へ再投影できる、という主張。

## Approval Engineeringの定義（会話内での発展形）

初期定義:

> 人間がどこを承認すれば、下位の大量成果物を再承認しなくてよい構造になるかを設計すること。

会話の終盤で、再構築可能性の議論（[[再構築可能性という品質指標]]）を経て、より深い定義へ発展している:

> Approval Engineeringとは、ソフトウェアを再生成可能なほど十分に「人間の意図」を構造化し、その構造化された意図のうち、人間にしか決められない部分だけを承認対象にする工学である。

さらに短い形:

> 人間の意図を構造化し、機械展開可能な部分を増やし、人間承認を本当に必要な判断へ圧縮する工学。

## TestPattern/Expectedも「View」になり得る

`{"validation_type": "integer", "minimum": 0, "maximum": 100}` という契約さえ承認されれば、`minimum_minus_1` 等のTestPatternや、その`Expected`(REJECT等)まで機械的に導出できる。ここから、Expectedを2種類に分ける整理が生まれている。

- **導出可能なExpected**: 上位のType/Constraintから一意に導出できるもの(保存不要、再生成できる)
- **固有のExpected**: 業務責務そのものに由来し、上位Typeから導出できないもの(Source Dataとして残す必要がある)

原則: **再生成できるものはViewへ落とし、再生成できない人間の判断だけをDataとして残す。**

## Type階層と項目辞書によるProject Type育成

Typeを一枚のラベルではなく階層として扱うことで再利用性が上がる、という発展:

```text
number → integer → non_negative_integer → percentage → discount_rate / progress_rate / quality_rate
```

下位Typeは上位Typeの契約を継承し、固有の値だけ末端に残す(例: `discount_rate` は `percentage` を継承しつつ `maximum_override: 30` だけ持つ)。

この考え方の核心は、Type Catalogを最初から完成品として設計するのではなく、**項目辞書(実際の管理項目一覧)から繰り返しパターンを発見し、徐々に上位Typeへ昇格させていく**という育て方にある。これは[[責務定義駆動テスト設計]]で「まず10個前後のBehavior Type候補を洗い出し、他画面でも使えると分かったものだけ標準へ昇格させる」としている進め方と、値の型・責務の型という対象は違うが同じ構造を持つ。

さらに、AIへ「似たものをまとめて」と頼むだけでは弱く、**何を同じものと判断するのか、その「グルーピング観点」自体をJSON等でData化する**ことが重要だと指摘されている。これは「人間は何を見て、同じと判断したのか」という判断軸そのものを外部化する試みであり、会話の中で「FRBは人間が『何を違うと感じるのか』をData化する研究、AI協働は人間が『何を同じだと判断するのか』をData化する研究」という強い対比が生まれている。

## レガシーシステムの再定義

> レガシー化とは、コードが古くなること以上に、意図がコードの中に閉じ込められることである。

レガシー解消は「古いコードを新しいコードへ置換すること」ではなく、「古いコードだけが知っていることを無くすこと」と再定義されている。レガシーコードから責務・保証・Type・Constraint候補をAIで逆抽出し、人間が承認したものだけを「Approved Structured Intent」として救出する、という手順がここから導かれる（詳細は[[再構築可能性という品質指標]]）。

## JSON化は目的ではなく結果

抽象化・共通化・標準化を突き詰めると「プログラムは薄い共通Runtime + 大量の構造化された意図」という形へ近づく、という観察。ここでJSONそのものが目的化しないよう釘が刺されている:

> JSON化は目的ではなく、構造化された意図を外部化した結果である。

原則として次のように整理されている。

```text
What / Why / Constraint / Expected → Data
How / Execution                    → Code / Runtime
```

FFT計算や画像処理のような実行アルゴリズムそのものはコードとして残るが、そこに個別業務の意味をなるべく持たせない、という方向性。

## オープンクエスチョン

- Type階層・項目辞書からの「Project Type育成」を、実際にFRBStudio_Appのどの画面で最初に試すか（この会話時点では未着手）
- 「グルーピング観点のData化」を、AIとの協働作業フローの中でどう具体的に運用するか

## 関連

- [[400KS人月仮説と承認単位のシフト]] — この理論の前段にあたる、より素朴な仮説
- [[責務定義駆動テスト設計]] — 同じ「型への承認圧縮」構造を、値の型ではなく責務の型として実践している
- [[再構築可能性という品質指標]] — Approval Engineeringの定義がここからさらに深化する
- [[Expected_Diff方式と検証世界の設計原則]] — 「導出可能なExpected」を実際に機械生成する具体的方式
- 出典: [[AI協働035_構造化された意図とApprovalEngineering]]
