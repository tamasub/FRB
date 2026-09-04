---
address: c-000004
type: source
title: "AI協働032 ループ・Claude Code責任者Borisの発言から"
created: 2026-09-04
updated: 2026-09-04
status: developing
tags:
  - source
  - conversation
  - chatgpt
  - loop-engineering
source_type: conversation
author: "ChatGPT(先生) / user"
date_published: "2026-08-19"
url: ""
source_id: "src-9770773650939e8df3d9"
sha256: "88a75d2db6e26ea7e16a1b43c03e5df603e828ec7e52e8488c75cb8102b3ec41"
authority: primary
independence_key: ""
review_state: active
key_claims:
  - "Loop Engineeringの「実行循環」とAI承認駆動開発の「正しさの循環」は競合せず合成できる ([[Loop_Engineeringと正しさの外部化]])"
related:
  - "[[Loop_Engineeringと正しさの外部化]]"
  - "[[400KS人月仮説と承認単位のシフト]]"
---

# AI協働032 ループ・Claude Code責任者Borisの発言から

X(Twitter)で見たポスト（Claude Code責任者 Boris Chernyの「もうエージェントへ逐一指示を出すのではなく、エージェントを動かす“ループ”を書く側になった」という趣旨の発言）の解説から始まり、Skill/Hooks/Subagent/Auto Modeを組み合わせた「Loop Engineering」を、自分たちが進めている「AI承認駆動開発」の文脈へ接続した会話。

## メタデータ

- 元ファイル: `.raw/AI協働032_ループ_Claude Code責任者のBorisが「もうエージェント（AIの作業役）に指示は出してない」.md`
- 参照元ポスト: Claude Code責任者 Boris Chernyに関するXスレッド（解説記事経由）

## 会話の流れ（要約）

1. Loop Engineeringの解説: Skill(手順の外出し) / Hooks(決定論的ルールの強制) / Subagents(役割分担) / Auto Mode(承認待ち削減) を組み合わせて「AIが次に何をすべきか判断できる環境」を作る、という思想
2. 「何を正しいとするの？」という以前からの疑問がここでも消えていない、という指摘
3. AI承認駆動開発の構造（判断軸・制約・責務・Expected → AI Loop → Diff → 人間承認）を、Loop Engineeringの「ループの外側」として位置づける
4. Expected Terrain（承認済みの地形）を先に置くことで、AIが「正しさを発明しながら走る」のではなく「承認済みの地形へ近づくように走る」構図になるという整理
5. 「違和感→判断→判断ログ→昇格・蒸留→判断軸/制約/責務/Expected」のループが、次回のループ品質を上げるという着地

## 派生ページ

- [[Loop_Engineeringと正しさの外部化]]
