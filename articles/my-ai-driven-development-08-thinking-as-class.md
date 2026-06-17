---
title: "思考をクラス化してしまった話"
emoji: "🧠"
type: "idea"
topics: ["ai", "json", "thought", "nocode", "design"]
published: false
---


# 思考をクラス化してしまった話

私は何を言っているのだろう。

数日前まで、

No-Code JSON Studio という JSON 編集ツールを作っていた。

いや、正確には FFT ログを管理したかっただけである。

しかし気付いたら、

AI 制約設計書をレビューするために、

`type: "chat"`

という FieldType を追加していた。

---

## 最初はただのチャットUIだった

最初は本当に単純な話だった。

AIが生成した制約に対して、

人間がコメントを書き、

AIが回答する。

そのやり取りを見やすくしたかった。

だから、

```json
{
  "field": "__review_chat",
  "type": "chat"
}
```

を追加した。

それだけだった。

---

## 違和感

しかし画面が動き始めた瞬間、

妙な違和感が生まれた。

これはチャットUIではない。

レビューという抽象概念が、

データ構造になっていた。

---

例えば、

```json
{
  "statement": "...",
  "user_comment": "...",
  "ai_response": "...",
  "user_reply": "...",
  "ai_followup_response": "...",
  "decision": "採用"
}
```

これは単なるデータだろうか。

私はそう思えなかった。

---

## Reviewというクラス

むしろ、

頭の中ではこう見えた。

```csharp
class Review
{
    string Statement;
    string UserComment;
    string AiResponse;
    string UserReply;
    string AiFollowupResponse;
    string Decision;
}
```

レビューという概念そのものが、

クラスになっている。

そんな感覚だった。

---

## 継承

さらに奇妙なことが起きた。

Reviewはレビューだけではない。

```csharp
class ConstraintReview : Review
{
    Constraint Constraint;
}

class DiffReview : Review
{
    GitDiff Diff;
}

class TestReview : Review
{
    TestPattern Pattern;
}

class ObservationReview : Review
{
    Observation Observation;
}
```

同じ構造が見え始めた。

対象が違うだけで、

議論し、

判断し、

承認する。

構造が同じなのである。

---

## 意味のグループ化

ここでようやく言葉が見つかった。

FieldGroupではない。

FieldGroupTypeでもない。

私が見ていたものは、

**意味のグループ化**

だった。

---

対話。

レビュー。

仮説。

観測。

差分。

これらは単なる文字列ではない。

意味のまとまりである。

そして、

意味のまとまりは、

構造化できるかもしれない。

---

## AI時代の承認技術

この発見は、

AI生成コードの承認コスト問題にも繋がる。

人間はコードを承認したいのだろうか。

違う気がする。

人間が承認したいのは、

意図であり、

制約であり、

判断理由である。

もしそれらが構造化できるなら、

人間はコードではなく、

思考を承認できるのかもしれない。

---

## 思考拡張の継承技術

そしてもう一つ。

私は長い間、

思考拡張をどう継承するかを考えていた。

結論だけを渡しても意味がない。

大切なのは、

そこへ至る思考経路である。

もし、

レビュー、

仮説、

観測、

差分、

そういったものを構造化できるなら、

思考経路そのものを継承できるかもしれない。

---

## 問い


> 思考をクラス化できるのだろうか。

分からない。

ただ、

私は気付いたら、

レビューをJSONにしていた。

そして、

AIとの対話をチャットUIで眺めながら、

これは設計書ではなく、

思考の構造なのではないかと考え始めていた。

私は何を言っているのだろう。

---

2026年6月16日

No-Code JSON Studio v0.3-draft を改造しながら。

---

追伸：
ChatGPTと会話しずぎで、頭がだんだんとおかしくなっていっているのかもしれない笑

---

## 本当の問い

最近、

AIが生成した40万ステップ規模のシステムを、

**1人月**で構築したというニュースに出会った。

実施に正常稼働しているかどうかはどうでもいい。


私はこのニュースを切っ掛けとして、

> 「AIが生成した40万ステップ規模のシステムを、1か月で承認しろ」と、もし言われたら？

という、思考が勝手に立ち上がってしまっただけの話である。

---

私は今、

コードではなく、

その手前にある何かを構造化しようとしている。

それが制約なのか。

テストなのか。

レビューなのか。

対話なのか。

まだ分からない。

ただ、

今日見つけた

「意味のグループ化」

という考え方は、

その問いに繋がっている気がしている。

気のせいかもしれない。

しかし、

もし気のせいではなかったとしたら、

AI時代の人間の承認技術は、

コードレビューやテスト結果レビューとは全く違う場所にあるのかもしれない。


400人月の承認を

1人月に圧縮する方法を

探している。

---


補足： 

- （私の頭の中）通常の生産性・・・ 1人月  1KS 笑
-  AI駆動開発の生産性 　　　・・・ 1人月400KS？？？　400倍？？？笑　ありえるのか？？？どうなんだ？？？笑

----

■関連記事

- [思考拡張の5つのレベル——AIと共に、発見し続ける人になるために](https://zenn.dev/frb_tamasub/articles/e45f0039aaa7b1)
- [思考拡張の大前提——「AIとの対話は、人間との対話と同じである」](https://zenn.dev/frb_tamasub/articles/fab815f72f9968)
- [思考拡張の設計理論（Draft）——違和感・体験・制約の三つの軸](https://zenn.dev/frb_tamasub/articles/196760f899a922)
- [思考拡張は、設計できる。 ～AIと話していたら、脳の使い方が変わってきた話～](https://zenn.dev/frb_tamasub/articles/aa2c08d08bafa9)
- [思考拡張の実践理論（Draft） ～AIと話していたら、脳の使い方が変わってきた話～](https://zenn.dev/frb_tamasub/articles/8893402839db17)
- [私が考えるAI駆動開発とは——差分・再現性・制約の三つの文化(Draft版)](https://zenn.dev/frb_tamasub/articles/6c075a9d23b247)
- [思考拡張・ＡＩ駆動開発の免罪符戦術～一度戦闘機に乗ったものは竹槍に戻れない！！～](https://zenn.dev/frb_tamasub/articles/35a14399295c8c)
- [思考拡張派生理論：設計未提示駆動開発〜設計を渡すな、違和感を渡せ〜](https://zenn.dev/frb_tamasub/articles/8d12318725309e)
- [思考拡張派生理論：AIにレビューさせるのではなく、AIの仮説で人間の思考を再起動する](https://zenn.dev/frb_tamasub/articles/744060659c21f0)
- [思考拡張したければ、まず文脈を育てる —— 「AI差分物語」という小さな実験](https://zenn.dev/frb_tamasub/articles/17da326e608795)
- [最大構成からミニマム構成へ——思考は、削ったときに立ち上がる](https://zenn.dev/frb_tamasub/articles/3654a9bbcca652)
- [AI協働とは、優秀だけど忘れっぽいチームメンバーと働くことである](https://zenn.dev/frb_tamasub/articles/84d81cb2c735f2)
  
- [ChatGPTに「次これ」と言われ続けた90日間 〜気が付いたらQiitaとZennで100本を超えていた〜](https://zenn.dev/articles/8023bd6f3ef039/edit)
- [私が考えるAI駆動開発とは——レビュー差分でAIとの信頼を観測する](https://zenn.dev/frb_tamasub/articles/ai-driven-development-trust-by-review-diff)
- [私が考えるAI駆動開発とは — AIテスト物語があるなら設計書は必要ですか？](https://zenn.dev/frb_tamasub/articles/ai-driven-development-ai-test-story)
- [『見えないものを可視化し、構造化する文化』という考え方にたどり着いた話](https://zenn.dev/frb_tamasub/articles/invisible-visualization-structuring-culture)
- [私が考えるAI駆動開発とは—— 承認コスト最小化と粒度設計](https://zenn.dev/frb_tamasub/articles/approval-cost-and-granularity)
  
- [【竹槍焼却の狼煙】AIに承認を求めるな、仮説を渡せ。コックピットの鍵はここに置いていく。](https://zenn.dev/frb_tamasub/articles/takeyari-shokyaku-noroshi)
  

  

この思考拡張の実例として、私はFRB（Fishing Rod Benchmark）という個人研究を続けている。
釣り竿の感度を振動として比較・可視化しようとする、一見おかしな研究だが、そこで起きているのは「差分」「再現性」「制約」を使ったAI協働そのものである。
  
- [FRB（Fishing Rod Benchmark）釣り竿の「感度」を数値化する話 宣言](https://qiita.com/tamasub/items/2b6649748e1772b7eec1)
  
- 

---