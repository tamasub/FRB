---
address: c-000005
type: source
title: "AI協働033 責務棚卸しPhase1 (v0.4)"
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
date_published: "2026-08-19"
url: ""
source_id: "src-ccdb98b7c27f6a3a72f5"
sha256: "b0a8fb748702261c20506c707abb9f52af7cbb7c3faeaea7f2862c0757a12c50"
authority: primary
independence_key: ""
review_state: active
key_claims:
  - "動詞の一致だけでBehavior Patternを共通化するのは危険 ([[責務定義駆動テスト設計]])"
related:
  - "[[責務定義駆動テスト設計]]"
  - "[[AI協働034_責務Behavior_Pilot_Phase2]]"
---

# AI協働033 責務棚卸しPhase1 (v0.4)

FRB Studio(FRBStudio_App)の既存責務を、粒度を変えずにそのまま棚卸しした作業ドキュメント。v0.4は`grid_column_build`責務へのレビューコメントを反映した最終版で、v0.1〜v0.3は同一ドキュメントの初期ドラフト（本ソースが正本として置き換え、supersede関係にある）。

## メタデータ

- 元ファイル: `.raw/AI協働033_FRB_Responsibility_Inventory_Phase1_v0_4.md`
- 種別: 作業ドキュメント（チャット要約ではなく、直接執筆されたPhase1棚卸し資料）
- 置き換えたドラフト: v0.1, v0.2, v0.3（+ v0.3のreview.json）

## 内容の要約

- Phase 1の目的: 責務粒度の標準化・Behavior Pattern化を検討する**前段**として、既存責務を「今の粒度のまま」20件棚卸しする（先に抽象化しない・粒度を直さない・Guaranteeも原文優先・「機械生成できそう」は判定しない、の4ルール）
- JSON Object Studio / Markdown Studio / Diff JSON / MetaDiff の4画面から20責務を一覧化
- `grid_column_build`責務を基準サンプルとして詳細化: 5つのGuarantee(g001〜g005)、既存テストとの対応関係(7/8 passed、g004/g005は未接続)まで実在確認
- Phase 2 Pilotとして、Guaranteeが揃っている4責務・25 Guaranteeを対象に選定
- 末尾に「GitDiffの思想」に関する会話が付記されており、Expected Diff方式の初期着想（[[Expected_Diff方式と検証世界の設計原則]]）につながっている

## 派生ページ

- [[責務定義駆動テスト設計]] (Phase1/2実践セクションを追記)
