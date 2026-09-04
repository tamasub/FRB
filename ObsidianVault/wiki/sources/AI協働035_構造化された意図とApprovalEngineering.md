---
address: c-000008
type: source
title: "AI協働035 構造化された意図とApproval Engineering"
created: 2026-09-04
updated: 2026-09-04
status: developing
tags:
  - source
  - document
  - approval-engineering
  - structured-intent
source_type: document
author: "user / Claude"
date_published: "2026-08-20"
url: ""
source_id: "src-5c3ec9aa6ecf44f46d33"
sha256: "03aaef2d7425b1d91829ee5244edce4a07b4de708ba7cc7318ef6c9255ad7aef"
authority: primary
independence_key: ""
review_state: active
key_claims:
  - "コードは意図を実行環境へ投影したViewである ([[Approval_Engineeringと構造化された意図]])"
  - "再構築可能性は構造化された意図の品質指標になり得る ([[再構築可能性という品質指標]])"
related:
  - "[[Approval_Engineeringと構造化された意図]]"
  - "[[再構築可能性という品質指標]]"
  - "[[400KS人月仮説と承認単位のシフト]]"
---

# AI協働035 構造化された意図とApproval Engineering

2026-08-20の会話を後から再読できるように整理した、かなり長い要約ドキュメント。人間の承認対象がコードから「意図」へ移るという出発点から、Type階層、Approval Engineeringの定義、レガシーマイグレーション論、そして「再構築可能性=構造化された意図の品質指標」という中心仮説まで、この一連のAI協働ログの中でも特に理論的な密度が高い一本。

## メタデータ

- 元ファイル: `.raw/AI協働035_構造化された意図とApprovalEngineering_チャット要約_20260820.md`
- 種別: チャット要約版（会話後に整理し直したドキュメント。#25以降は追記）

## 内容の要約（大項目）

1. 人間の承認対象が「コード→テストコード→テストケース→責務→保証→制約→判断軸→意図」の順で上位へ移っていく、という出発点
2. **コードは、意図を実行環境へ投影したViewである** という中心的な言葉
3. Approval Engineering = 「人間がどこを承認すれば、下位の大量成果物を再承認しなくてよい構造になるかを設計すること」という初期定義
4. TestPattern/Expectedすら「上位Typeから導出できるView」であるという再考、および「導出可能なExpected」と「固有のExpected」の区別
5. Type階層（number→integer→non_negative_integer→percentage→discount_rate等）と、項目辞書からProject Typeを育てる手法
6. 「人間は何を見て同じと判断したのか」という判断軸の言語化、FRBとAI協働の構造的な同型性
7. レガシーシステムの本当の問題は「コードが古いこと」ではなく「意図がコードに閉じ込められていること」という再定義
8. 追記(#25〜): 抽象化・共通化・標準化を突き詰めた先の姿、JSON化は目的ではなく結果であるという整理、**再構築可能性=構造化された意図の品質指標**という仮説、保証継承原則、AIをOracleにしない境界

## 派生ページ

- [[Approval_Engineeringと構造化された意図]]
- [[再構築可能性という品質指標]]
