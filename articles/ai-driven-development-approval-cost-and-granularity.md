---
title: "私が考えるAI駆動開発とは—— 承認コスト最小化と粒度設計"
emoji: "🧠"
type: "idea"
topics: ["ai", "development", "json", "architecture", "nocode"]
published: true
---

# 私が考えるAI駆動開発とは—— 承認コスト最小化と粒度設計

これは誰かに伝えるための記事というより、未来の自分のための思考ログである。

Playwrightの話から始まった雑談が、気が付けば「AI時代の承認設計理論」の話になっていた。

## スタート地点

最初の違和感は単純だった。

> HTML/Javascriptのテストって本当にPlaywrightで頑張るべきなのか？

レイアウト崩れは結局人間が見る。

ならば、本当に比較したいものは何なのだろう。

## HTMLではなく画面状態を見る

最初に見えたのは、

```text
HTML
↓
画面状態
```

という視点だった。

例えば、

```json
{
  "duration_sec": 30,
  "sample_rate": 500
}
```

が画面に表示されていることを確認したい。

確認したいのはHTML構造ではない。

画面状態である。

ここで「画面状態JSON」という概念が生まれた。

## テストコードよりテストパターンJSON

次に見えたのは、AI時代に価値があるのは

```text
テストコード生成
```

ではなく

```text
テストパターン生成
```

ではないかということ。

```text
AI
↓
test_patterns.json生成
↓
人間確認
↓
実行
```

の方が自然に感じた。

## テストとは差分観察である

ここでFRBの差分文化とつながった。

```text
Expected
↓
Actual
↓
Diff
```

テストとは差分観察である。

Gitも同じ。

FRBも同じ。

## AI差分物語からAIテスト物語へ

AI差分物語の本質は

```text
差分
↓
AI仮説
↓
違和感
↓
人間解釈
```

である。

ならば、テスト結果にも適用できる。

しかし途中で気付いた。

AIテスト物語の本質はExpectedとActualではなかった。

## AIテスト物語

本当に面白いのはこちらだった。

```text
テストコード
↓
AIが制約を推定
↓
AI制約設計書（仮説）
↓
正式制約設計書
↓
差分
↓
違和感
```

つまり、不具合を探す物語ではない。

設計思想のズレを発見する物語である。

## AI制約設計書

ここで発想が逆転した。

従来は、

```text
コード
↓
テスト生成
```

だった。

しかし、

```text
制約
↓
テスト生成
```

の方が本質的ではないか。

## 継承という発見

さらに思考は進んだ。

```text
NumericConstraint
↓
FrequencyConstraint
↓
peakAHz
```

継承。

そして必要な部分だけオーバーライド。

これはオブジェクト指向そのものだった。

## しかし継承しているのはコードではない

継承しているのはコードではない。

知識である。

```text
FrequencyConstraint
↓
peakAHz
inputHz
centerHz
```

承認済み知識を再利用している。

## 本当に重要なのは粒度

今日の最大の発見。

重要なのは

```text
継承できるか
```

ではない。

重要なのは

```text
どの粒度で継承するか
```

である。

候補として見えてきたのは、

```text
FieldType
↓
FieldGroup
↓
TableType
↓
FileType
↓
FileGroup
↓
ProjectType
```

である。

## AI時代の前提変更

昔は

```text
生成コストが高い
```

だった。

だから

```text
実装量削減
```

が重要だった。

しかし今は違う。

```text
生成量はAIが解決する
```

という前提がある。

すると問題は

```text
人間が何を確認するか
```

になる。

つまり承認コストがボトルネックになる。

## 今日の結論

今日生まれた一文。

> 粒度設計とは、どの単位で知識を継承すると最も承認コストを削減できるかを決めることである。

## 私の継承元概念

最近、自分の思考を振り返ると、多くの概念がここから派生しているように見える。

```text
見えないもの
↓
差分
↓
可視化
↓
構造化
↓
意味付け
↓
世界の解像度を上げる
↓
意味のある構造として未来へ継承
```

FRBも、AI差分物語も、No-Code JSON Studioも、AI制約設計書も、おそらくここから生まれている。

Playwrightの雑談から始まったはずなのに、気が付けば「AI時代の承認設計理論」の話になっていた。

思考拡張とは、こういうことなのかもしれない。


---


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


この思考拡張の実例として、私はFRB（Fishing Rod Benchmark）という個人研究を続けている。
釣り竿の感度を振動として比較・可視化しようとする、一見おかしな研究だが、そこで起きているのは「差分」「再現性」「制約」を使ったAI協働そのものである。
  
- [FRB（Fishing Rod Benchmark）釣り竿の「感度」を数値化する話 宣言](https://qiita.com/tamasub/items/2b6649748e1772b7eec1)
  


---

