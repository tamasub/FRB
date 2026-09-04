---
address: c-000010
type: concept
title: "Loop Engineeringと正しさの外部化"
created: 2026-09-04
updated: 2026-09-04
status: developing
tags:
  - concept
  - ai-driven-development
  - loop-engineering
related:
  - "[[400KS人月仮説と承認単位のシフト]]"
  - "[[Approval_Engineeringと構造化された意図]]"
sources:
  - "[[AI協働032_ループEngineeringと正しさの外部化]]"
claim_ids:
  - clm-loop-correctness-external
complexity: intermediate
domain: "AI駆動開発・エージェント運用"
aliases:
  - Loop Engineering
  - Expected Terrain
---

# Loop Engineeringと正しさの外部化

## 要旨

外部で語られている「Loop Engineering」（Claude CodeのSkill / Hooks / Subagents / Auto Modeを組み合わせ、AIへ毎回指示するのではなく「AIが次に何をすべきか判断できる環境=ループ」を書く、という思想）を観察し、それが自分たちの「AI承認駆動開発」とどう関係するかを整理した回。結論は「競合しない、むしろ綺麗に合体する」というもので、Loop Engineeringが**実行循環**を作るのに対し、AI承認駆動開発は**正しさの循環**を作る、という役割分担に落ち着いている。

## Loop Engineeringの要素分解（外部知見の要約）

会話内で紹介された対応関係:

```text
Skill    = AIが何を知っているか・どう作業するか
Hooks    = 絶対守らせるルール（決定論的、LLMの判断に依存しない）
Subagent = 誰に何を担当させるか
Auto Mode = 人間の承認待ちを減らす
Loop     = それらを循環させる構造
```

## 「何を正しいとするの？」という以前からの疑問

Loop Engineeringはループを速く・自律的に回す技術だが、「確認するときの正しさは何か」という問いには答えない。これは以前から引っかかっていた点で、この会話でも解消されていない、という自己認識が明示されている。

## 正しさをループの外側に置く

AI承認駆動開発の構造をLoop Engineeringへ重ねると、次のようになる。

```text
人間
↓
目的・判断軸・制約・責務・Expected
──────────────
      AI Loop
──────────────
実装 → TestPattern → Runner実行 → Actual → Diff → 修正 → 再実行
──────────────
↓
人間承認
```

つまり「ループそのものを否定する」のではなく、**「ループの外側に、誰が正しさを定義するのかを置く」**という位置づけ。Expected Terrain(承認済みの地形)を先に置くことで、AIは「正しさを発明しながら走る」のではなく「承認済みの地形へ近づくように走る」構図になる、という比喩が使われている。

## ループ自身がループの品質を上げる

「違和感 → 判断 → 判断ログ → 昇格・蒸留 → 判断軸/制約/責務/Expected」という、[[400KS人月仮説と承認単位のシフト]]や[[Approval_Engineeringと構造化された意図]]でも繰り返し現れる蒸留サイクルを、Loop Engineeringのループ自体に組み込むことで「ループが次回のループの品質を上げる」という二重ループ構造が示唆されている。

## オープンクエスチョン

- 「正しさをループの外側に置く」という設計を、実際のClaude Code運用（Hooks/Skills/Subagents）へどう具体的に落とし込むかは、この会話ではまだ検討されていない
- Auto Modeの「暴走対策として回数上限を入れる」という外部知見と、AI承認駆動開発のExpected/Diffベースの停止条件をどう統合するか

## 関連

- [[400KS人月仮説と承認単位のシフト]] — 承認単位のシフトという観点で同じ方向を向いている
- [[Approval_Engineeringと構造化された意図]] — 「正しさ」を構造化された意図として外部化する、より詳細な理論
- 出典: [[AI協働032_ループEngineeringと正しさの外部化]]
