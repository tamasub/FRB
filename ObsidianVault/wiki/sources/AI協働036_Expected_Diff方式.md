---
address: c-000009
type: source
title: "AI協働036 Expected Diff Method (v0.4)"
created: 2026-09-04
updated: 2026-09-04
status: developing
tags:
  - source
  - document
  - expected-diff
  - test-runner
source_type: document
author: "user / Claude / GPT先生"
date_published: "2026-08-24"
url: ""
source_id: "src-be3ed2d1482d701b042c"
sha256: "3bd7c6bcff4a8b145c289b50ee793f0c4e82d825a4b8c22cb186926054cd137e"
authority: primary
independence_key: ""
review_state: active
key_claims:
  - "Expected Diffは品質保証済みDiff ToolがInputと仮Expected Outputから機械生成する差分である ([[Expected_Diff方式と検証世界の設計原則]])"
  - "検証世界は前提条件で分割された単純な世界の集合であり、APP世界の複雑なコピーであってはならない ([[Expected_Diff方式と検証世界の設計原則]])"
related:
  - "[[Expected_Diff方式と検証世界の設計原則]]"
  - "[[責務定義駆動テスト設計]]"
  - "[[AI協働034_責務Behavior_Pilot_Phase2]]"
---

# AI協働036 Expected Diff Method (v0.4)

Expected Diff（期待値差分）方式を単独の重要検討メモとして詳細化したドキュメント。v0.1〜v0.4まで版を重ねており、v0.4はClaudeによる2回目のレビューコメントをほぼ全て反映した最終版（v0.3を置き換える）。文末にClaudeとGPT先生のコメントもそのまま保存されている。

## メタデータ

- 元ファイル: `.raw/AI協働036_Expected_Diff_Method_v0_4.md`
- 置き換えたドラフト: v0.3

## 内容の要約

- Expected Diffの基本定義: 人間が手書きする期待差分ではなく、**品質保証済みDiff Tool**がInputと仮Expected Outputを比較して機械生成する差分出力
- Diff Toolを「共通の観測器」として固定し、Expected側・Actual側の両方で同じToolを使うことで、差分生成の承認自体を個別テストから外す
- InputもField Definition/Validation Type/TestPattern/Type Generator Configから機械導出する方針（文字列テンプレート、境界値+seed付き決定論的乱数、基準日時+Offset等）。項目固有Templateは最終手段
- Generic Mutation Engine（指定pathへ指定した変更だけを忠実に適用し、値を解釈・型変換しない汎用部品）
- 上位原理: **APPとは独立した「単純化された、信頼できる検証世界」**を作ること。検証世界はAPP世界の複雑なコピーではなく、前提条件で分割した小さなVerification Ruleの集合とする
- 保証継承原則（下位で保証済みの責務を上位で再検証しない。ただし前提条件・Interface・Versionは要確認）
- 「現時点ではAIをOracleにしない」という境界（AIはOracleを設計してよいが、Oracleそのものにはしない）
- Claudeレビューが指摘した未解決論点（DERIVED/DYNAMIC項目の抜け道対策、前提条件の網羅性・排他性、Conflict Check後の挙動など）

## 派生ページ

- [[Expected_Diff方式と検証世界の設計原則]]
