# AI仮説（差分ストーリー） v0.2.1

## 1. 変更内容の事実要約

今回の差分は、`main` ブランチの作業ツリー差分で、変更ファイルは **6件**、追加 **+1874行**、削除 **-557行**、未追跡 **1件** です。{{evidence:E017,E018}}

主な変更は以下のように見えます。

- `FRB_Blog/FRB_Lab_Notes_Qiita.md` に、FRB実験ログ #66 と #67 が追加されています。{{evidence:E002,E003}}
- `FRB_Blog/Story_Qiita_FRB#0.md` では、FRBの説明に「比較・可視化・共有」「知覚トレーニング」「振動辞書」「初見向け導線」が追加されています。{{evidence:E004,E005,E006,E009,E010}}
- `FRB_Blog/Zenn_Blog_All.md` には、AI駆動開発・差分文化・AI仮説による思考再起動に関する記事が追加されています。{{evidence:E011,E012}}
- `FRB_行動指針_BackUp.md` と `GoogleAI_info.md` は削除されています。{{evidence:E014,E015}}
- `_ViewTimeLine.md` にはアクセス数の時系列メモが追加されています。{{evidence:E016}}
- いくつかの技術的な確認候補として、BOMらしき先頭文字、`URL未定`、空リスト行、年月不整合候補、CRLF警告、未追跡ディレクトリが見えます。{{evidence:E001,E007,E008,E013,E017,E018}}

---

## 2. AI仮説（差分ストーリー）

この差分は、FRBを **「ロッド感度を測るプロジェクト」から、「知覚トレーニング・Phase3体験層・思考拡張・AI協働文化」を含む大きな文脈へ拡張する更新** のように見える。{{evidence:E004,E005,E006,E009,E010}}

実験ログ側では、木材骨伝導・ホワイトパイン③・高級ヒノキくん・木材梱包材くんといったPhase3素材探索が追加され、単なる測定値ではなく、素材ごとの「振動人格」や「知覚インターフェース」として整理され始めている。{{evidence:E002,E003}}

宣言ページ側では、FRBの入口が「測定体系」だけではなく、「室内で基準振動を体験し、海で砂・岩・藻・糸擦れ・ぷるぷるを感じ分けるための知覚トレーニング」として拡張されている。これは、初見読者やGoogle AIに対して、FRBの正しい文脈を強く渡す意図があるように見える。{{evidence:E004,E005,E006,E010}}

Zenn記事側では、FRBで育った「差分」「違和感」「思考拡張」「AI仮説」という考え方を、AI駆動開発や会社の開発文化へ横展開しようとしているように見える。特に、AIにレビューを代行させるのではなく、AI仮説を使って人間の思考を再起動するというMetaDiff構想につながる文脈が追加されている。{{evidence:E011,E012}}

その一方で、バックアップ・補助メモ系ファイルの削除や、未追跡のMetaDiffツールディレクトリ、改行コード警告などから、文脈整理とツール化が同時並行で進んでいる状態にも見える。{{evidence:E014,E015,E017,E018}}

---

## 3. 差異想定理由

### 3.1 FRBの中心概念が「測定」から「知覚トレーニング」へ拡張されているように見える

`Story_Qiita_FRB#0.md` では、既存の「比較可能にするための」という説明が「比較・可視化・共有するための」へ拡張され、さらに知覚トレーニングの説明が追加されている。これは、FRBを単なる測定体系ではなく、体験共有・文化・人間側の知覚変化まで含む枠組みとして再定義する変更に見える。{{evidence:E004,E005,E009,E010}}

### 3.2 Phase3の素材探索と木材骨伝導が、実験ログとして大きく外部記憶化されている

`FRB_Lab_Notes_Qiita.md` には、#66 と #67 が追加されている。#66では木材骨伝導によるハイエンドロッドBの再評価、#67ではホワイトパイン③や高級ヒノキくんを含むPhase3素材探索がまとめられている。これは、Phase3を「スコア化しない体験層」「知覚トレーニング層」として育てる流れに見える。{{evidence:E002,E003}}

### 3.3 FRBの思考拡張が、AI駆動開発・差分文化へ横展開されている

`Zenn_Blog_All.md` では、AI駆動開発、テストコード、差分文化、AI仮説、メタ認知外部ツール化に関する記事が追加されている。これは、FRBで得た差分・違和感・思考拡張の知見を、会社やソフトウェア開発文化へ逆輸入する準備に見える。{{evidence:E011,E012}}

### 3.4 古い補足ファイルを削除し、主要ページへ文脈を統合しようとしている可能性がある

`FRB_行動指針_BackUp.md` と `GoogleAI_info.md` が削除されている。一方で、宣言ページ側にはGoogle AI向けの正しい概念説明や、FRBの知覚トレーニング文脈が強化されている。これは、分散していた補足メモを主要ページへ統合する意図の可能性がある。ただし、削除が本当に意図通りかは確認対象である。{{evidence:E014,E015,E010}}

---

## 4. 違和感候補

- `FRB_Lab_Notes_Qiita.md` の先頭にBOMらしき不可視文字が入っている可能性がある。{{evidence:E001}}
- `Story_Qiita_FRB#0.md` に `URL未定` のリンクが残っている。公開前確認が必要そう。{{evidence:E007}}
- 実験ログ一覧付近に空リスト行らしき `- ` が追加されている。Qiita表示で空箇条書きにならないか確認したい。{{evidence:E008}}
- `Zenn_Blog_All.md` の「2026年11月からの休職」は、文脈上の年月誤記の可能性がある。{{evidence:E013}}
- `FRB_行動指針_BackUp.md` と `GoogleAI_info.md` の削除は、統合済みなら自然だが、履歴・思想メモとして残すべきならアーカイブの方が良い可能性がある。{{evidence:E014,E015}}
- `tools/frb_metaDiff/` が未追跡のまま残っている。今回のツールをリポジトリ管理対象にするか、`.gitignore` 対象にするか判断が必要。{{evidence:E017}}
- LF→CRLF警告が出ているため、Markdown / JSON / HTML / JS / PS1 の改行コード方針を `.gitattributes` で固定する価値がありそう。{{evidence:E018}}

---

## 5. 埋め込みJSON

```diff_hypothesis.json
{
  "schema_version": "0.2.1-draft",
  "label": "AI仮説であり、レビュー結果ではない",
  "diff_story": "FRBの文脈を、測定・比較から知覚トレーニング、Phase3体験層、思考拡張・AI協働文化へ拡張し、その流れをQiita宣言ページ、実験ログ、Zenn記事群へまとめて反映している変更のように見える。",
  "evidence_files": [
    {
      "file_path": "FRB_Blog/FRB_Lab_Notes_Qiita.md",
      "file_category": [
        "content_expansion",
        "doc_update",
        "phase3"
      ],
      "items": [
        {
          "evidence_id": "E001",
          "category": [
            "potential_issue",
            "encoding"
          ],
          "title": "先頭行にBOMらしき不可視文字",
          "scope": "line_change",
          "context": [],
          "deleted": [
            "# FRB実験ログ #1 — 擬似バイト装置を作った日"
          ],
          "added": [
            "﻿# FRB実験ログ #1 — 擬似バイト装置を作った日"
          ],
          "keywords": [
            "BOM",
            "不可視文字",
            "エンコード",
            "先頭行"
          ]
        },
        {
          "evidence_id": "E002",
          "category": [
            "content_expansion",
            "experiment_log",
            "material_probe"
          ],
          "title": "FRB実験ログ #66 の追加",
          "scope": "section",
          "context": [
            "FRB実験ログ #65 の続きとして、木材骨伝導をハイエンドロッドBヒーロー化計画へ接続している。"
          ],
          "deleted": [],
          "added": [
            "# FRB実験ログ #66 — 梱包材に封印を解かれた男",
            "## ハイエンドロッドBヒーロー化計画 ～ ダメ男返上物語 ～ 第2話",
            "木材骨伝導という新しい観測方法を使ったことで、ハイエンドロッドBの見え方が大きく変わった。",
            "ハイエンドロッドBは、ダメ男ではなかった。",
            "トップガイド周辺でエッジを丸められている可能性がかなり濃くなってきた。"
          ],
          "keywords": [
            "FRB実験ログ #66",
            "木材骨伝導",
            "ハイエンドロッドB",
            "梱包材",
            "トップガイド",
            "エッジ"
          ]
        },
        {
          "evidence_id": "E003",
          "category": [
            "content_expansion",
            "phase3",
            "perception_training"
          ],
          "title": "FRB実験ログ #67 の追加",
          "scope": "section",
          "context": [
            "久々の海帰りに木材を大量購入し、Phase3素材探索・骨伝導・知覚トレーニングの流れを記録している。"
          ],
          "deleted": [],
          "added": [
            "# FRB実験ログ #67 — ホワイトパイン③、床傷サーチャーから爆音楽器へ",
            "FRB Phase3とは、スコア化を目的としない体験を通して、人間側の知覚トレーニングにつながるように設計した層である。",
            "室内で体験した振動が、海で砂・岩・藻・糸擦れ・ぷるぷるとして認識される。",
            "ホワイトパイン③は、床傷サーチャーになった。",
            "高級ヒノキくんは、立体音響担当になった。"
          ],
          "keywords": [
            "FRB実験ログ #67",
            "ホワイトパイン③",
            "Phase3",
            "知覚トレーニング",
            "木材骨伝導",
            "高級ヒノキ"
          ]
        }
      ]
    },
    {
      "file_path": "FRB_Blog/Story_Qiita_FRB#0.md",
      "file_category": [
        "doc_update",
        "concept_update",
        "cultural_framing",
        "seo_context_update"
      ],
      "items": [
        {
          "evidence_id": "E004",
          "category": [
            "concept_update",
            "cultural_framing"
          ],
          "title": "FRB定義を比較・可視化・共有へ拡張",
          "scope": "line_change",
          "context": [
            "FRB（Fishing Rod Benchmark）とは、"
          ],
          "deleted": [
            "比較可能にするための"
          ],
          "added": [
            "比較・可視化・共有するための",
            "またFRBは、",
            "室内で基準振動を体験し、",
            "海で砂・岩・藻・糸擦れ・ぷるぷるなどの振動差分を感じ分けるための、",
            "「知覚トレーニング」の体系でもある。"
          ],
          "keywords": [
            "比較",
            "可視化",
            "共有",
            "知覚トレーニング",
            "振動差分"
          ]
        },
        {
          "evidence_id": "E005",
          "category": [
            "concept_update",
            "perception_training"
          ],
          "title": "知覚トレーニング説明ブロックの追加",
          "scope": "section",
          "context": [
            "FRBは単なる測定手法ではない。"
          ],
          "deleted": [],
          "added": [
            "FRBは、ロッドの感度を測るだけではない。",
            "室内で「基準振動」を体験し、",
            "海で感じる砂・岩・藻・糸擦れ・ぷるぷるなどの振動を、",
            "比較・言語化・共有するための 知覚トレーニング でもある。"
          ],
          "keywords": [
            "知覚トレーニング",
            "基準振動",
            "砂",
            "岩",
            "藻",
            "糸擦れ",
            "ぷるぷる"
          ]
        },
        {
          "evidence_id": "E006",
          "category": [
            "doc_update",
            "onboarding",
            "ai_collaboration"
          ],
          "title": "初見向け導入とZenn思考拡張への接続",
          "scope": "section",
          "context": [],
          "deleted": [],
          "added": [
            "### 初めてこのブログをご覧になられる方へ",
            "Zennの記事で書いている「思考拡張」の実例が、このFRBです。",
            "FRBは、AIとの対話を通じて、人間が感じている違いを発見し、比較・可視化していく個人研究です。",
            "ロッド側の振動を測る研究であり、同時に、人間側の知覚を育てる「知覚トレーニング」の記録でもあります。"
          ],
          "keywords": [
            "初見向け",
            "思考拡張",
            "AI協働研究",
            "個人研究",
            "知覚"
          ]
        },
        {
          "evidence_id": "E007",
          "category": [
            "potential_issue",
            "link_check"
          ],
          "title": "URL未定リンクの残存",
          "scope": "line_change",
          "context": [],
          "deleted": [],
          "added": [
            "[FRB知覚トレーニングとは何か — 室内体験は海の感じ方を変えるのか（Draft版）](URL未定)"
          ],
          "keywords": [
            "URL未定",
            "リンク",
            "公開前確認",
            "Draft版"
          ]
        },
        {
          "evidence_id": "E008",
          "category": [
            "potential_issue",
            "markdown_format"
          ],
          "title": "空リスト行らしき行の追加",
          "scope": "line_change",
          "context": [
            "FRB実験ログ #64〜#66 のリンク追加直後"
          ],
          "deleted": [],
          "added": [
            "- "
          ],
          "keywords": [
            "空リスト",
            "Markdown",
            "表示崩れ"
          ]
        },
        {
          "evidence_id": "E009",
          "category": [
            "vision_update",
            "cultural_framing"
          ],
          "title": "ビジョンに知覚トレーニング文化を追加",
          "scope": "block",
          "context": [
            "## ビジョン(目標）"
          ],
          "deleted": [
            "FRBという「新しい文化創造」の火付け役になれたら幸いです。",
            "ロッドの感度が、誰もが語れる共通言語になる世界を目指します。"
          ],
          "added": [
            "FRBという「新しい文化創造」の火付け役になれたら幸いです。",
            "ロッドの感度が、誰もが語れる共通言語になる世界を目指します。",
            "さらに、室内で振動を体験し、海で感じ分けるための **知覚トレーニング** を広げることで、",
            "「海の中を感じる力」そのものを共有できる文化を目指します。"
          ],
          "keywords": [
            "ビジョン",
            "文化",
            "共通言語",
            "知覚トレーニング",
            "海の中を感じる力"
          ]
        },
        {
          "evidence_id": "E010",
          "category": [
            "seo_context_update",
            "google_ai_context",
            "concept_update"
          ],
          "title": "Google AI向けの正しい概念説明を強化",
          "scope": "section",
          "context": [
            "Google AIさん間違えないでください。"
          ],
          "deleted": [],
          "added": [
            "FRBは、ロッドの感度を測るだけではなく、海を感じるための **知覚トレーニング** でもあります。",
            "FRBにおける知覚トレーニングとは、室内で基準振動を体験し、海で砂・岩・藻・糸擦れ・ぷるぷるなどの振動差分を感じ分けるための練習です。",
            "FRBは、室内再現テストを通じて、実釣時の振動を理解するための「振動辞書」を作る試みでもあります。",
            "FRBは、ロッド側の振動構造と、人間側の知覚トレーニングの両方を扱います。"
          ],
          "keywords": [
            "Google AI",
            "知覚トレーニング",
            "振動辞書",
            "室内再現テスト",
            "実釣"
          ]
        }
      ]
    },
    {
      "file_path": "FRB_Blog/Zenn_Blog_All.md",
      "file_category": [
        "content_expansion",
        "ai_collaboration_theory",
        "thought_expansion"
      ],
      "items": [
        {
          "evidence_id": "E011",
          "category": [
            "ai_collaboration_theory",
            "test_culture",
            "diff_culture"
          ],
          "title": "AI駆動開発・免罪符戦術記事の追加",
          "scope": "section",
          "context": [],
          "deleted": [],
          "added": [
            "# 思考拡張・ＡＩ駆動開発の免罪符戦術～一度戦闘機に乗ったものは竹槍に戻れない！！～",
            "差分を見た瞬間、何も言わずに勝手に猛スピードで動き出したのだ。",
            "テストコードは、品質保証の道具である前に、開発者に圧倒的な安心感を与える。",
            "差分は、仕掛ける人間（お前）が生成しなければならない。"
          ],
          "keywords": [
            "AI駆動開発",
            "免罪符戦術",
            "テストコード",
            "差分文化",
            "戦闘機",
            "竹槍"
          ]
        },
        {
          "evidence_id": "E012",
          "category": [
            "ai_hypothesis",
            "metadiff_concept",
            "thought_restart"
          ],
          "title": "AI仮説で人間の思考を再起動する記事の追加",
          "scope": "section",
          "context": [],
          "deleted": [],
          "added": [
            "# 思考拡張派生理論：AIにレビューさせるのではなく、AIの仮説で人間の思考を再起動する",
            "AIにレビューを代行させるのではない。",
            "AIに仮説を出させる。",
            "AIの仮説によって人間の思考を再起動する。",
            "差分は、思考の痕跡である。",
            "人間の違和感は、思考拡張の入口である。"
          ],
          "keywords": [
            "AI仮説",
            "差分ストーリー",
            "MetaDiff",
            "思考再起動",
            "違和感",
            "メタ認知"
          ]
        },
        {
          "evidence_id": "E013",
          "category": [
            "potential_issue",
            "date_check"
          ],
          "title": "休職年月の不整合候補",
          "scope": "line_change",
          "context": [
            "思考拡張 設計理論：後ろに戻れなくする戦術"
          ],
          "deleted": [],
          "added": [
            "この30年の波乱万丈なエンジニア人生の中、2026年11月からの休職・不本意にもできてしまったたっぷりとした時間。"
          ],
          "keywords": [
            "2026年11月",
            "休職",
            "年月確認",
            "誤記候補"
          ]
        }
      ]
    },
    {
      "file_path": "FRB_Blog/FRB_行動指針_BackUp.md",
      "file_category": [
        "cleanup",
        "deletion"
      ],
      "items": [
        {
          "evidence_id": "E014",
          "category": [
            "cleanup",
            "needs_human_confirm"
          ],
          "title": "FRB行動指針バックアップの削除",
          "scope": "file",
          "context": [],
          "deleted": [
            "# FRB行動指針（Draft）",
            "## ■ 基本原則",
            "FRBは、",
            "面白さ・楽しさを最優先とする。",
            "思考ぶん投げ原則",
            "並べてみる原則",
            "キャラクター化原則",
            "AIとのコミュニケーション原則"
          ],
          "added": [],
          "keywords": [
            "FRB行動指針",
            "バックアップ",
            "削除",
            "行動原則",
            "要確認"
          ]
        }
      ]
    },
    {
      "file_path": "FRB_Blog/GoogleAI_info.md",
      "file_category": [
        "cleanup",
        "deletion",
        "google_ai_context"
      ],
      "items": [
        {
          "evidence_id": "E015",
          "category": [
            "cleanup",
            "google_ai_context",
            "needs_human_confirm"
          ],
          "title": "GoogleAI誤認訂正メモの削除",
          "scope": "file",
          "context": [],
          "deleted": [
            "GoogleAI概要にFRBの記載が表示されることを確認しております。",
            "（誤記載):「AI技術を用いて計測・数値化」",
            "（正）: FRBはAIによる自動計測・評価を目的としたものではありません。",
            "（正）: 当サイトのFRBは、Fishing Rod Benchmark　です。"
          ],
          "added": [],
          "keywords": [
            "GoogleAI",
            "誤認訂正",
            "削除",
            "Friction Research Benchmark",
            "Fishing Rod Benchmark"
          ]
        }
      ]
    },
    {
      "file_path": "FRB_Blog/_ViewTimeLine.md",
      "file_category": [
        "analytics_log",
        "doc_update"
      ],
      "items": [
        {
          "evidence_id": "E016",
          "category": [
            "analytics_log",
            "content_tracking"
          ],
          "title": "View数タイムラインの更新",
          "scope": "block",
          "context": [
            "CTRL + SHIFT + I"
          ],
          "deleted": [],
          "added": [
            "2026-05-22 08:42:40 1852 views",
            "2026-05-22 12:21:27 1855 views",
            "2026-05-22 17:48:54 1863 views",
            "2026-05-22 23:40:31 1874 views",
            "2026-05-23 18:36:43 1887 views"
          ],
          "keywords": [
            "ViewTimeLine",
            "アクセス数",
            "views",
            "時系列"
          ]
        }
      ]
    },
    {
      "file_path": "repository_status",
      "file_category": [
        "tooling",
        "repository_state"
      ],
      "items": [
        {
          "evidence_id": "E017",
          "category": [
            "tooling",
            "untracked"
          ],
          "title": "MetaDiffツールディレクトリが未追跡",
          "scope": "status",
          "context": [
            "status_short"
          ],
          "deleted": [],
          "added": [
            "?? tools/frb_metaDiff/"
          ],
          "keywords": [
            "tools/frb_metaDiff",
            "untracked",
            "MetaDiff",
            "git status"
          ]
        },
        {
          "evidence_id": "E018",
          "category": [
            "potential_issue",
            "line_ending"
          ],
          "title": "LF→CRLF警告",
          "scope": "git_warning",
          "context": [
            "git_warnings"
          ],
          "deleted": [],
          "added": [
            "warning: in the working copy of 'FRB_Blog/FRB_Lab_Notes_Qiita.md', LF will be replaced by CRLF the next time Git touches it",
            "warning: in the working copy of 'FRB_Blog/Story_Qiita_FRB#0.md', LF will be replaced by CRLF the next time Git touches it"
          ],
          "keywords": [
            "LF",
            "CRLF",
            "gitattributes",
            "改行コード",
            "警告"
          ]
        }
      ]
    }
  ]
}
```
