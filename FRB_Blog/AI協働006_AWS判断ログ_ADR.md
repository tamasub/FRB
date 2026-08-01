おお、ここは大事。
結論から言うと、ADRは――

> **ISOやIEEEの委員会が作った正式規格ではない。**
> **実務家が提案し、世界の開発コミュニティや大手企業・政府機関へ広がったデファクト・プラクティス。**

という立ち位置やね。

「世界の勇者たちが現場で育てた作法」という表現は、かなり近い笑

## ADRの立ち位置

ざっくり分類するとこう。

| 分類               | ADR |
| ---------------- | --- |
| ISO・JISなどの正式規格   | 違う  |
| 特定企業の製品仕様        | 違う  |
| 学会だけの研究理論        | 違う  |
| 法的・業界的な義務        | 違う  |
| 実務家が提案した設計プラクティス | これ  |
| 世界的に普及したデファクト手法  | これ  |

つまり、

```text
公式な標準規格
ではない

しかし

国際的に広く認知され、
有力企業や政府機関も採用・推奨している
実務上の標準的プラクティス
```

という位置。

Git、アジャイル、デザインパターンなどと同じで、最初から国際委員会が規格として制定したというより、**有効だった現場の方法が広がって定着したもの**やね。

## 誰が作ったのか

現在よく使われる軽量ADRの形を広めた中心人物は、ソフトウェアアーキテクトの **Michael Nygard（マイケル・ナイガード）**。

2011年11月15日に、Cognitectのブログで
**“Documenting Architecture Decisions”** という記事を公開した。

そこで彼は、

* Title
* Status
* Context
* Decision
* Consequences

という短い形式で、アーキテクチャ上の重要な判断をMarkdownなどのテキストとしてリポジトリへ保存する方法を提示した。古い判断を消さず、変更時には「superseded（置き換え済み）」として履歴を残す考え方も示している。([Cognitect.com][1])

面白いことに、この記事自体がADR形式で書かれている。

```text
Context
なぜ判断理由が失われると困るのか

Decision
ADRを記録する

Status
Accepted

Consequences
将来の開発者が理由を理解できる
```

完全に「自分で実演してみました」方式やね笑

## ただし、突然ゼロから発明されたわけではない

Michael Nygardが2011年にADRという軽量な形式を広める以前から、ソフトウェアアーキテクチャ研究では、

> アーキテクチャは完成した構成図だけではなく、積み重ねられた設計判断として捉えるべきではないか

という議論があった。

特に2005年には、Jeff TyreeとArt Akermanが、主要なアーキテクチャ判断を明示的に記録することで、設計の理由をステークホルダーへ説明できると論じた論文を発表している。([ACM Digital Library][2])

同じ2005年には、Anton JansenとJan Boschも、ソフトウェアアーキテクチャを「明示的な設計判断の集合」として捉える研究を発表した。完成した構造だけでは「なぜそうなったのか」が失われるため、判断自体をアーキテクチャの第一級情報として扱おう、という方向性だった。([ResearchGate][3])

流れとしては、こんな感じ。

```text
2000年代前半
アーキテクチャの「判断理由が消える問題」が研究される
        ↓
2005年
設計判断を明示的に記録する研究・テンプレートが登場
        ↓
2011年
Michael Nygardが軽量なADR形式として整理・公開
        ↓
2016年以降
ThoughtWorksなどを通じて実務コミュニティへ急速に普及
        ↓
現在
AWS、Microsoft、英国政府なども公式ガイダンスで採用
```

なので、正確には、

> Michael Nygardが「判断理由を残す思想そのもの」を一人で発明したのではない。
> 既存の研究や実務上の問題意識を、現場で使いやすい軽量なADR形式として整理し、普及させた中心人物。

という理解がよい。

## いつ「広く使われるもの」になったのか

大きかったのが、世界的な技術コンサルティング会社ThoughtWorksの **Technology Radar**。

ThoughtWorksは2016年11月、Lightweight Architecture Decision Recordsを「Trial」、つまり実案件で試す価値がある技法として掲載した。2017年11月には「Adopt」に昇格させ、「業界が採用すべきであり、自社プロジェクトでも適切な場合に利用する」という評価にしている。2018年にもAdoptを維持し、多くのプロジェクトで使わない理由はほぼないという強い評価を示した。([Thoughtworks][4])

ここから「一人のブログ記事」ではなく、

> **世界的なソフトウェア開発プラクティス**

として認知が広がっていったと見てよいと思う。

## 今はどの程度の扱いなのか

かなり強い。

AWSはPrescriptive Guidanceで、ADRを「ソフトウェアアーキテクチャ上の重要な選択、その文脈、結果を記録する文書」と定義し、複数のADRの集合を **decision log** と呼んでいる。承認済みADRは原則として変更せず、新しい判断が出たら新しいADRを作って旧ADRを置き換える運用まで体系化している。([AWS ドキュメント][5])

MicrosoftのAzure Well-Architected Frameworkも、ADRを「ソリューションアーキテクトの最も重要な成果物の一つ」と位置づけ、アーキテクチャを判断の蓄積として捉えている。コンテキスト、選択肢、トレードオフ、状態、信頼度などを記録し、追加型のログとして維持するよう勧めている。([Microsoft Learn][6])

英国政府のGovernment Digital Serviceも、アーキテクチャ判断をバージョン管理下へ保存する方法としてADRを推奨し、Michael Nygardが提案して以降、広く採用されている形式だと説明している。([The GDS Way][7])

つまり現在は、

```text
個人ブログのアイデア
        ↓
コミュニティのプラクティス
        ↓
大手技術企業の推奨手法
        ↓
クラウド公式設計ガイド
        ↓
政府デジタル部門の開発ガイド
```

まで育っている。

これは、かなり立派な「デファクト標準」やと思う。

## ただし「正式な国際規格」とは言わない方がよい

ここは会社説明で注意。

ADRそのものについて、

> ISOで決められた正式規格です

とは言えない。

アーキテクチャ記述全般には、ISO/IEC/IEEE 42010という正式な国際規格が存在する。ただし、これはアーキテクチャ記述、ビュー、ビューポイントなどの要求を定める規格であって、Michael Nygard形式のADRそのものを必須フォーマットとして定めた規格ではない。([ISO][8])

ADRには複数のテンプレートや派生形があり、絶対にこの項目で書かなければならない、という中央管理された単一仕様もない。

だから会社では、こう説明するのが一番正確。

> **ADRはISOなどの正式規格ではありませんが、2011年にMichael Nygardが整理・公開した軽量な設計判断記録の手法です。その後、ThoughtWorksのTechnology RadarでAdoptに分類され、AWS、Microsoft、英国政府などの公式技術ガイダンスでも採用されている、国際的に定着した実務プラクティスです。**

これはかなり強く、しかも盛ってない。

## 判断ログとの関係で言うと

ここ、玉井さんにとって結構でかい。

AWSが明確に、

```text
1件の記録
= Architecture Decision Record

ADRの集合
= Decision Log
```

と整理している。([AWS ドキュメント][5])

つまり、

> **「判断を記録し、その集合を判断ログとして管理する」こと自体は、玉井さん独自の奇妙な主張ではない。**

これは既に、AWSの公式アーキテクチャガイダンスにも出てくる考え方。

ただし、ADRが主に扱うのは「アーキテクチャ上の重要判断」。

玉井さんが考えている判断ログは、

```text
アーキテクチャ判断
＋
制約判断
＋
責務判断
＋
テスト判断
＋
AIの出力補正
＋
判断軸や制約への昇格
```

まで対象を広げている。

したがって会社では、

> ADRという、設計判断・文脈・結果を記録する国際的に普及したプラクティスがあります。
> 今回の判断ログは、この考え方をAI協働開発の日常的な判断まで拡張して扱うものです。

と言える。

これならもう、

**「俺が判断ログが大事だと思うんですぅぅぅ！」**

と全身全霊で訴えなくていい爆笑

> 「AWSさんがDecision Logと呼んでます。うちもやりましょう」

このくらいの温度で机に資料を置けるやつやね。

[1]: https://www.cognitect.com/blog/2011/11/15/documenting-architecture-decisions "Documenting Architecture Decisions"
[2]: https://dl.acm.org/doi/10.1109/MS.2005.27?utm_source=chatgpt.com "Demystifying Architecture: IEEE Software: Vol 22, No 2"
[3]: https://www.researchgate.net/publication/220864796_Software_Architecture_as_a_Set_of_Architectural_Design_Decisions?utm_source=chatgpt.com "Software Architecture as a Set of Architectural Design ..."
[4]: https://www.thoughtworks.com/radar/techniques/lightweight-architecture-decision-records "Lightweight Architecture Decision Records | Technology Radar | Thoughtworks"
[5]: https://docs.aws.amazon.com/prescriptive-guidance/latest/architectural-decision-records/adr-process.html "ADR process - AWS Prescriptive Guidance"
[6]: https://learn.microsoft.com/ja-jp/azure/well-architected/architect-role/architecture-decision-record "アーキテクチャデシジョン レコード (ADR) を維持する - Microsoft Azure Well-Architected Framework | Microsoft Learn"
[7]: https://gds-way.digital.cabinet-office.gov.uk/standards/architecture-decisions.html "Documenting architecture decisions - The GDS Way"
[8]: https://www.iso.org/standard/74393.html?utm_source=chatgpt.com "ISO/IEC/IEEE 42010:2022 - Software, systems and enterprise — Architecture description"
