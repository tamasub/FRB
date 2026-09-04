---
address: c-000006
type: source
title: "AI協働034 責務Behavior Pilot Phase2 (v0.2)"
created: 2026-09-04
updated: 2026-09-04
status: developing
tags:
  - source
  - document
  - responsibility-inventory
  - frb-studio
source_type: document
author: "user / Claude"
date_published: "2026-08-22"
url: ""
source_id: "src-925051dee60d4648daa9"
sha256: "2f9def38686fbe06f6bf7907ac14ec6e144945e280300ce73fef40b2f71f6a52"
authority: primary
independence_key: ""
review_state: active
key_claims:
  - "Guaranteeの文言一致だけでは共通化できない。対象・条件・保証・観測結果・Expected生成方法まで見る必要がある ([[責務定義駆動テスト設計]])"
related:
  - "[[責務定義駆動テスト設計]]"
  - "[[AI協働033_責務棚卸しPhase1]]"
  - "[[Expected_Diff方式と検証世界の設計原則]]"
---

# AI協働034 責務Behavior Pilot Phase2 (v0.2)

Phase 1で棚卸しした4責務・25Guarantee(`grid_column_build` / `search_filter` / `csv_export` / `grid_aggregate`)を、Behavior Pattern名を先に付けずに横断比較したPilot記録。v0.2は人間レビュー後の思考拡張メモ（Expected Diff仮説の初出）を追記した版で、v0.1（+review.json）を置き換える。

## メタデータ

- 元ファイル: `.raw/AI協働034_FRB_Responsibility_Behavior_Pilot_Phase2_v0_2.md`
- 置き換えたドラフト: v0.1（+ v0.1のreview.json）

## 内容の要約

- 25Guaranteeの原文一覧を横断配置し、類似候補A(入力非破壊)・B(順序維持)・C(空/なし安全)・D(除外)を観察。Dは「動詞が同じだけで対象・判定タイミング・出力契約が違う」危険な候補として明示的に保留
- 「Guaranteeの文言一致だけでは共通化できない」「対象・条件・保証・観測結果・Expected生成方法まで一緒に見る必要がある」という安全弁を明文化
- 人間レビュー後の追記として、**Expected Diff（期待値差分）**の初期仮説が生まれる: InputからOutputへの変化だけをExpectedとして定義し、指定されていない部分はInputから継承する
- Test Runner側の共通保証候補、「Runnerがまだ知らない知恵は何か？」という中心問い、複雑な責務をInput/Outputまで平たく分解する基本姿勢を整理

## 派生ページ

- [[責務定義駆動テスト設計]] (Phase1/2実践セクションを追記)
- [[Expected_Diff方式と検証世界の設計原則]] (この文書がExpected Diffの初出)
