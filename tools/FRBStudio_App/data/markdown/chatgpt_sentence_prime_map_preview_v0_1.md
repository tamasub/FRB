# Sentence Prime Map Preview v0.1

文脈.mdのセンテンスごとに、Anchor Wordから発火した候補を 1位（採用）/ 2位（不採用）/ 3位（不採用）で眺める。

## sent_001 — FRB

### 元センテンス
FRBは、ロッドの優劣を決めるランキングではない。ロッドごとの違いを観測し、比較し、選択し、共有するための共通言語を作る試みである。

### Anchor: FRB

- 共通言語 -- 1位（採用）
  - relation: `creates`
  - prime: 0.96
  - treasure_score: 5
- ランキング否定 -- 2位（不採用）
  - relation: `rejects`
  - prime: 0.91
  - treasure_score: 5
  - discarded_reason: 結論を共通言語に寄せたため、否定側は前置きとして圧縮された。
  - おん？候補: FRBを誤解させないためには、ランキング否定をもっと前面に出すべきでは？
- 選択支援 -- 3位（不採用）
  - relation: `supports`
  - prime: 0.84
  - treasure_score: 4
  - discarded_reason: 共通言語の内側に吸収された。
  - おん？候補: FRBは比較文化だけでなく、初心者の選択支援として語る方が刺さる場面があるのでは？

---

## sent_002 — 感度

### 元センテンス
感度は単純な振動量ではない。感度は、人間が認識可能な振動構造である。

### Anchor: 感度

- 振動構造 -- 1位（採用）
  - relation: `is_redefined_as`
  - prime: 0.97
  - treasure_score: 5
- 単純な振動量ではない -- 2位（不採用）
  - relation: `is_not`
  - prime: 0.93
  - treasure_score: 5
  - discarded_reason: 主張を肯定形にまとめたため、否定側は補助に回った。
  - おん？候補: 『振動が強い＝高感度ではない』をもっと強く出すべきでは？
- 人間が認識可能 -- 3位（不採用）
  - relation: `depends_on`
  - prime: 0.89
  - treasure_score: 5
  - discarded_reason: 振動構造という語に吸収された。
  - おん？候補: FRBの本質は『振動を測る』ではなく『人間が認識できる構造を扱う』では？

---

## sent_003 — 室内再現テスト

### 元センテンス
室内再現テストは、海の代替ではなく、海で感じるための振動辞書を作る行為である。

### Anchor: 室内再現テスト

- 振動辞書 -- 1位（採用）
  - relation: `builds`
  - prime: 0.95
  - treasure_score: 5
- 海の代替ではない -- 2位（不採用）
  - relation: `is_not`
  - prime: 0.88
  - treasure_score: 5
  - discarded_reason: 文全体では振動辞書の方を結論にした。
  - おん？候補: 『室内で海を再現する』と誤解されないために、否定側を残すべきでは？
- 海で感じるため -- 3位（不採用）
  - relation: `prepares_for`
  - prime: 0.86
  - treasure_score: 5
  - discarded_reason: 振動辞書に意味が吸収された。
  - おん？候補: 室内テストは測定ではなく、身体を海へ接続する訓練では？

---

## sent_004 — 違和感

### 元センテンス
AIに答えを求めるだけでは弱い。違和感を流さない。違和感を問いに変える。

### Anchor: 違和感

- 問い -- 1位（採用）
  - relation: `becomes`
  - prime: 0.96
  - treasure_score: 5
- 流さない -- 2位（不採用）
  - relation: `requires`
  - prime: 0.93
  - treasure_score: 5
  - discarded_reason: 問いへの変換を主プロセスとして採用したため。
  - おん？候補: 実は一番大事なのは、問いに変える前の『流さない』という態度では？
- 答えを求めるだけでは弱い -- 3位（不採用）
  - relation: `rejects`
  - prime: 0.88
  - treasure_score: 4
  - discarded_reason: 否定的導入として圧縮された。
  - おん？候補: AI活用の入り口として、まず『答えを求めるだけでは弱い』を置くべきでは？

---

## sent_005 — AIとの対話

### 元センテンス
AIとの対話は、人間との対話と同じである。深く理解してほしければ、途中経過・感情・判断軸・失敗・違和感を渡す必要がある。

### Anchor: AIとの対話

- 人間との対話と同じ -- 1位（採用）
  - relation: `is_like`
  - prime: 0.94
  - treasure_score: 5
- 判断軸 -- 2位（不採用）
  - relation: `requires`
  - prime: 0.86
  - treasure_score: 5
  - discarded_reason: 途中経過・感情・失敗と並列化され、単独主役にはしなかった。
  - おん？候補: AI協働で本当に重要なのは、情報量より『判断軸』では？
- 感情 -- 3位（不採用）
  - relation: `requires`
  - prime: 0.82
  - treasure_score: 5
  - discarded_reason: 文脈要素の一つとして処理された。
  - おん？候補: AIに感情フィードバックを渡すことが、思考拡張の燃料では？

---

## sent_006 — AI駆動開発

### 元センテンス
AI駆動開発は、AIにコードを書かせる話ではなく、差分・再現性・制約を大切にする文化の話である。

### Anchor: AI駆動開発

- 文化 -- 1位（採用）
  - relation: `is`
  - prime: 0.95
  - treasure_score: 5
- 差分 -- 2位（不採用）
  - relation: `depends_on`
  - prime: 0.91
  - treasure_score: 5
  - discarded_reason: 三要素の一つとして並列化された。
  - おん？候補: AI駆動開発の入口は、実は『差分を渡す』だけで十分なのでは？
- 制約 -- 3位（不採用）
  - relation: `depends_on`
  - prime: 0.88
  - treasure_score: 5
  - discarded_reason: 文化という大枠に吸収された。
  - おん？候補: 人間が本当にレビューすべき対象は、コードではなく制約では？

---

## sent_007 — Data/View分離

### 元センテンス
Markdownは文書のData。JSONは構造化データのData。Viewは後から生成できる。DataとViewを分離する。

### Anchor: Data/View分離

- Viewは後から生成できる -- 1位（採用）
  - relation: `enables`
  - prime: 0.93
  - treasure_score: 5
- Markdownは文書のData -- 2位（不採用）
  - relation: `classifies`
  - prime: 0.87
  - treasure_score: 5
  - discarded_reason: View生成の話を主役にしたため、Markdownの位置づけは素材化された。
  - おん？候補: Markdownを文書ではなくDataとして扱う発想が、もっと本質では？
- JSONは構造化データのData -- 3位（不採用）
  - relation: `classifies`
  - prime: 0.86
  - treasure_score: 5
  - discarded_reason: Data/View分離に吸収された。
  - おん？候補: JSONを『ファイル形式』ではなく『AIに渡す構造』として語るべきでは？

---

## sent_008 — ContextDef

### 元センテンス
ContextDefも育てる必要がある。

### Anchor: ContextDef

- 育てる -- 1位（採用）
  - relation: `must_be_grown`
  - prime: 0.96
  - treasure_score: 5
- 人間がメンテする文脈 -- 2位（不採用）
  - relation: `is_maintained_by`
  - prime: 0.91
  - treasure_score: 5
  - discarded_reason: 元センテンスには明示されていないが、会話文脈から強く発火。
  - おん？候補: ContextDefはAI用ではなく、人間がメンテする対象では？
- ViewDefの中に置く -- 3位（不採用）
  - relation: `is_edited_through`
  - prime: 0.86
  - treasure_score: 5
  - discarded_reason: 実装寄りに脱線するため本文には出ない。
  - おん？候補: ContextDefは独立ファイルではなく、ViewDefから編集されるAI向けViewなのでは？

---

## sent_009 — AI差分物語

### 元センテンス
差分からAI差分物語を作る。

### Anchor: AI差分物語

- 差分 -- 1位（採用）
  - relation: `is_generated_from`
  - prime: 0.94
  - treasure_score: 5
- 仮説根拠トレース -- 2位（不採用）
  - relation: `should_include`
  - prime: 0.88
  - treasure_score: 5
  - discarded_reason: 差分物語の機能拡張として、元文にはまだ出ていない。
  - おん？候補: AI差分物語には、採用仮説の根拠エッジを残すべきでは？
- 捨て仮説ランキング -- 3位（不採用）
  - relation: `should_include`
  - prime: 0.86
  - treasure_score: 5
  - discarded_reason: 今回の会話で新しく生まれた派生概念。
  - おん？候補: 採用しなかった2位・3位を見せることが、違和感生成の本体では？

---

## sent_010 — ChatGPT

### 元センテンス
こちらの言葉をそのまま整えるだけではなく、違和感、構造、次の問いを一緒に見つけてほしい。

### Anchor: ChatGPT

- 思考の相棒 -- 1位（採用）
  - relation: `acts_as`
  - prime: 0.91
  - treasure_score: 5
- 違和感発見 -- 2位（不採用）
  - relation: `finds`
  - prime: 0.89
  - treasure_score: 5
  - discarded_reason: 相棒という上位ロールに吸収された。
  - おん？候補: ChatGPTの役割は、文章整形ではなく『違和感発見』に寄せるべきでは？
- 次の問い -- 3位（不採用）
  - relation: `finds`
  - prime: 0.84
  - treasure_score: 4
  - discarded_reason: 違和感・構造と並列で処理された。
  - おん？候補: 成果物よりも、次の問いを残すことが一番価値では？

---

## sent_011 — 記事

### 元センテンス
記事をきれいにまとめすぎない。きれいにまとめすぎると、違和感や熱量が消える。

### Anchor: 記事

- きれいにまとめすぎない -- 1位（採用）
  - relation: `must_not`
  - prime: 0.95
  - treasure_score: 5
- 違和感が消える -- 2位（不採用）
  - relation: `risk`
  - prime: 0.91
  - treasure_score: 5
  - discarded_reason: スタイル制約の理由として圧縮された。
  - おん？候補: 綺麗にすること自体が、思考拡張の敵になる場面があるのでは？
- 熱量が消える -- 3位（不採用）
  - relation: `risk`
  - prime: 0.88
  - treasure_score: 5
  - discarded_reason: 違和感と並列で扱われた。
  - おん？候補: 熱量はノイズではなく、文脈を伝える信号では？

---

## sent_012 — 見えないもの

### 元センテンス
全部、見えないものを、可視化し、構造化し、共有する文化につながっている。

### Anchor: 見えないもの

- 可視化・構造化・共有 -- 1位（採用）
  - relation: `is_transformed_by`
  - prime: 0.97
  - treasure_score: 5
- FRB / 思考拡張 / JSON Studio の統合 -- 2位（不採用）
  - relation: `unifies`
  - prime: 0.92
  - treasure_score: 5
  - discarded_reason: 『全部』という語に吸収され、具体名は出なかった。
  - おん？候補: この一文が、3テーマ統合の憲法では？
- 人生の再構築 -- 3位（不採用）
  - relation: `implies`
  - prime: 0.78
  - treasure_score: 5
  - discarded_reason: 文脈.mdでは明示しすぎると重くなるため表に出ない。
  - おん？候補: 見えないものを構造化して共有する行為は、研究ではなく自己再構築では？

---
