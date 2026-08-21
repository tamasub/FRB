---
title: "AI承認駆動開発 #5｜ソースコードがViewになった日——構造化された意図からシステムを再構築できるか"
emoji: "🧩"
type: "idea"
topics: ["ai", "development", "testing", "legacy", "approval"]
published: false
---

:::message
**これは、あくまでも今までの体験から生まれた思考ログである。**

**人間の意図を十分な粒度で構造化Dataにできたら、そこから同じ振る舞いをするシステムを再生成できるのではないか。**
:::

:::message
**「テストコードが無かった」という歴史そのものを飛び越えて、テストコードより上位のSourceを作る。**
:::

# 前回は、minimum_minus_1からApproval Engineeringが生まれた

前回の **AI承認駆動開発 #4** では、

```text
minimum_minus_1
minimum
maximum
maximum_plus_1
invalid_format
```

という、小さなテストパターンの話から始まった。

そして、

```text
Validation Type
        ↓
複数のTestPattern
        ↓
具体値
        ↓
Expected
```

という構造を見ながら、

> **同じ意味の判断を、人間に何度もさせる必要はないのではないか。**

と考えた。

さらに、

```text
判断軸・制約
= 大きな意味

Validation Type
= 小さな見る型
```

と整理し、

> **人間・AI・プログラムが何を見るべきかを設計し、人間が承認しやすい構造を作る。**

という考え方を、**Approval Engineering（承認工学）** と呼んでみることにした。

前回の記事の最後では、

> 始まりは、`minimum_minus_1` だった。

と書いた。

今回の話も、そこから続いている。

ただし今回は、少しだけ話が大きくなってしまった。

いや。

かなり大きくなってしまった。

---

# そもそもStudioくんは、一枚の画像から始まった

今作っているStudioくんの原型には、昔の記憶がある。

私は2017年頃、休日を使って、**ノーコードもどきのマルチマスタメンテナンス画面** を作っていた。

DBのテーブル情報を元に、

- 一覧Grid
- 編集Dialog
- 検索
- ComboBox
- ReadOnly
- 表示／非表示
- Caption
- 列幅
- Editor種別

などを、できるだけ定義側へ寄せる仕組みだった。

その画面の画像が、一枚だけ残っていた。

正確には、**ソースコードもちゃんと探せばあった。**

でも私は、探さなかった。

理由は単純である。

> **「まぁ、この画像一枚でどうにかなるやろぉ〜」**

と思ったからである。

かなり適当だった。

---

# 発端は「AI協働ではJSONが大事らしい」

この少し前、私はAIとの協働について考えていた。

その中で、

> MarkdownやJSONのような、AIが扱いやすい形式で情報を残しておくことが大切。

という話をAIから聞いた。

その頃の私のJSONに対する認識は、正直に言えば、

> **「JSONってなんやっけ？」**

くらいだった。

使ったことはある。見たこともある。でも、日常的にJSONを書く人間ではなかった。

ただ、

> **AI協働ではJSONが大事らしい。**

ということだけは頭に残った。

一方で、JSONを眺めていて思った。

> **これ、人間フレンドリーじゃないな。**

AIには扱いやすい。プログラムにも扱いやすい。でも、人間が大量のJSONを直接編集するのは、あまり楽しくない。

だったら、

> **JSONを人間フレンドリーなViewへ変換すればいいのではないか。**

そう考えた。

そこで思い出したのが、昔作ったあの画面だった。

私はその画像をAIへ渡して、だいたいこんな話をした。

```text
この画像みたいに、
GridとDialogを組み合わせて、
JSONをメンテナンスできる画面を作れない？

対象JSONの構造や、
CaptionやTypeや列幅などは、
外部定義JSONに持たせたい。
```

昔のソースコードは渡していない。

一枚の画像と、何回かの会話だけだった。

そして、**Studioくんのプロトタイプが生まれた。**

---

# 作ってから思い出した

ここには、少しだけオチがある。

Studioくんのプロトタイプができてから、私は昔の画面について、あることを思い出した。

> **あれ？**

昔のノーコードもどきマスタメンテナンス画面も、DBのテーブル情報をAPIから受け取るとき、**JSONフォーマットで受け取っていた。**

つまり、よく考えると昔の私は、

```text
Database
↓
API
↓
JSON
↓
汎用画面
```

というものを作っていた。

そして何年も経って、

```text
AI協働ではJSONが大事らしい
↓
でもJSONは人間フレンドリーじゃない
↓
人間フレンドリーな画面を作ろう
↓
昔の画像をAIへ渡す
↓
Studioくん誕生
```

となった。

結果として、**JSONから始まり、昔のJSONへ戻ってきた。**

最初からそんな壮大な思想があったわけではない。

かなり偶然である。

---

# でも、一つだけ不思議なことが残った

Studioくんは、昔のソースコードをAIへ渡して復元したものではない。

渡したものは、

```text
一枚の画像
+
私の記憶
+
チャットで補った要望・制約
```

だった。

もちろん、一枚の画像だけですべてが復元できたわけではない。

画面を見ながら、

- 何をしたかったのか
- どこまで汎用化したかったのか
- 何を定義側へ出したかったのか
- どこは対象外にしたかったのか

を、私は会話の中で補っていった。

つまり、AIが再構築したのは、**昔のコードそのものではない。**

もっと近い言い方をするなら、

> **昔の私がやりたかったことを、別の実装として再構築した。**

という方が近い。

ここで、少し引っかかった。

> **再構築に必要だったのは、昔のソースコードではなく、昔の意図だったのではないか。**

---

# ViewDefは、画面コードではなく「人間の意図」を外へ出していた

Studioくんを作り続ける中で、画面に関する情報は、少しずつViewDefへ移っていった。

例えば、

```json
{
  "caption": "数量",
  "field": "quantity",
  "editor": "number",
  "readonly": false,
  "visible_grid": true
}
```

のような情報である。

これは、単なる画面設定値にも見える。

しかし、別の見方をすると、

```text
この項目を一覧へ出したい
このCaptionで見せたい
このEditorで編集させたい
ここはReadOnlyではない
```

という、**人間の意図をコードの外へ出したData** でもある。

すると、

```text
ViewDef
↓
Runtime
↓
Grid / Detail / Editor / Search
```

という関係になる。

この場合、画面コードそのものより、

> **どんな画面にしたいのか。**

を持っているViewDefの方が上位にいる。

画面は、**ViewDefを実行環境へ投影したView** と考えることもできる。

この時点では、まだ画面の話だった。

---

# そして、またminimum_minus_1へ戻る

StudioくんでField DefinitionやValidationを考えていたとき、前回の記事で書いた、

```text
minimum_minus_1
minimum
maximum
maximum_plus_1
invalid_format
```

というTestPatternが出てきた。

例えば、

```json
{
  "validation_type": "integer",
  "minimum": 1,
  "maximum": 100,
  "nullable": false
}
```

という項目定義がある。

ここから、

```text
minimum_minus_1
→ 0
→ REJECT

minimum
→ 1
→ ACCEPT

maximum
→ 100
→ ACCEPT

maximum_plus_1
→ 101
→ REJECT
```

を導出できる。

すると、

> **TestPatternを保存する必要すらないのではないか。**

と思い始めた。

さらに、

> **Expectedも保存しなくてよいものがあるのではないか。**

となった。

上位の定義から一意に導出できるなら、

```text
TestPattern
Expected
```

は、Sourceではない。

**生成可能なView**

として扱える。

---

# さらに上へ登ってみる

例えば、

```text
semantic_type = percentage
```

という意味があれば、

```text
minimum = 0
maximum = 100
unit = %
```

の一部は導出できるかもしれない。

すると、

```text
percentage
↓
Constraint
↓
Validation Type
↓
TestPattern
↓
Expected
```

という構造が見えてくる。

ここで、考え方が少し変わった。

> **再生成できるものは、できるだけViewへ落とせないか。**

という問いである。

そして、

> **では、人間が本当に残すべきDataは何なのか。**

を考え始めた。

---

# 最大のSource候補は「責務定義・項目定義」ではないか

今のところ、私が一番重要だと思っているのは、**責務定義・項目定義** である。

例えば、そこに、

```text
この項目は何を意味するのか
どのTypeに属するのか
どんなConstraintがあるのか
何を保証する責務なのか
どのBehaviorを持つのか
どのExpectedが固有判断なのか
```

を構造化して持つ。

さらに、

> **TestPatternとExpectedを導出できる元情報**

まで持たせる。

すると、

```text
Responsibility / Field Definition
        ↓
Validation Type
        ↓
Constraint
        ↓
TestPattern
        ↓
Expected
        ↓
Test Definition
        ↓
Test Code
```

のかなりの部分を、プログラムで展開できる可能性がある。

ここで人間が一件ずつ承認するのは、

```text
minimum_minus_1
maximum_plus_1
```

ではない。

もっと上位の、

```text
この責務でよいか
このTypeでよいか
このConstraintでよいか
この固有Expectedでよいか
```

である。

そこを人間が承認したら、下流はできるだけ機械へ倒す。

これが、今回考えているApproval Engineeringの一つの方向である。

---

# すると、テストコードまでViewに見えてくる

ここまで行くと、テストコードの位置づけも変わって見える。

これまでは、

```text
Source Code
+
Test Code
```

が、大切な成果物に見えていた。

もちろん、今でもテストコードには大きな価値がある。

しかし、

もし、

```text
Approved Structured Intent
↓
TestPattern
↓
Expected
↓
Test Code
```

を再生成できるなら、

テストコードそのものは、

> **承認済みの意図を、特定のテスト実行環境へ投影したView**

とも考えられる。

そして、ここで一つの妄想が出てきた。

> **では、Application Codeも同じではないか。**

---

# ソースコードが、Sourceではなくなった

例えば、

```text
責務
Constraint
Validation Type
Business Rule
State Transition
Behavior
固有Expected
```

まで十分な粒度で構造化できたとする。

そこから、

```text
Application Code
Test Code
Document
UI
```

を生成できるなら、構造としてはこうなる。

```text
Approved Structured Intent
        │
        ├─→ Application Code
        ├─→ Test Code
        ├─→ Expected
        ├─→ Documentation
        └─→ UI / View
```

ここで突然、**ソースコードまでViewに見えてきた。**

従来の感覚では、

```text
Source Code = Source of Truth
```

だった。

しかし、この仮説では、

```text
Structured Intent Data = Source of Truth

Application Code = Generated View
Test Code        = Generated View
Document         = Generated View
UI               = Generated View
```

になる。

もちろん、現時点では妄想である。

すべてのシステムを、このように完全記述できると言っているわけではない。

でも、問いとしては成立する。

> **人間の意図を十分な粒度で構造化Dataにできたら、同じ振る舞いをするコードを再生成できるのではないか。**

---

# 同じ「コード」を作る必要はない

ここでいう再生成は、昔と同じソースコードを復元することではない。

例えば、

```text
Legacy
COBOL
Oracle
独自画面
```

だったものが、

```text
New
Java / C#
PostgreSQL
Web UI
```

になってもよい。

重要なのは、**コードが同じことではなく、必要なBehaviorが同じこと** である。

```text
同じ入力
↓
同じ意味上の判断
↓
同じ必要な状態遷移
↓
同じ期待される出力
```

を再現できるなら、実装言語や内部構造は変わっていてもよい。

つまり比較対象は、**Code DiffではなくBehavior Diff** になる。

---

# 再構築可能性を、Structured Intentの品質指標にできないか

ここまで考えると、Structured Intentの品質をどう評価するか、という問いも出てくる。

その一つの答えが、

> **再構築可能性**

ではないかと思っている。

例えば、

```text
Structured Intent v1
↓
New System生成
↓
Behavior Diff = 120件
```

だった。

不足している責務やConstraintを追加する。

```text
Structured Intent v2
↓
New System生成
↓
Behavior Diff = 19件
```

さらに補う。

```text
Structured Intent v3
↓
New System生成
↓
Behavior Diff = 0件
```

もし、このようなことができたとしたら、

> **Structured Intentの中に、システムを再構築するために必要な意味が十分保存されていた。**

と考えられる。

つまり、

> **再構築可能性 = 構造化された意図の品質指標**

として扱える可能性がある。

これは、コードの品質を測る話とは少し違う。

> **どこまで意味をコードの外へ救出できたか。**

を測る話である。

---

# ここで、巨大レガシーシステムという大妄想へ飛んでしまった

ここまで考えていると、急に一つの妄想が出てきた。

> **これ、巨大レガシーシステムにも使えないか？**

である。

テストコードをほとんど装備していない、長年運用されてきた巨大システム。

こうしたシステムを変えようとすると、従来は、

```text
Legacy Code
↓
Characterization Testを作る
↓
安全網を作る
↓
Refactoring
```

という方向を考えたくなる。

しかし、今回の妄想は少し違う。

私は、これを「リファクタリング」と呼びたいわけではない。

むしろ、

> **構造化された意図による再構築**

と考えている。

---

# テストコードが無かった歴史を、埋める必要はあるのか

巨大なLegacy SourceをAIへ渡して、

> テストコードを大量生成してください。

と頼むことはできるかもしれない。

でも、すぐに変な問題が出てくる。

```text
巨大Legacy
↓
AI
↓
100万件のTest Code
↓
その100万件の品質を、
誰が保証するの？
```

である。

AIを使って人間の仕事を減らしたはずなのに、100万件のAI生成テストを人間がレビューする。

意味が分からない。

そこで、

> **Legacyから生成したテストコードの品質を保証することを、最初から諦めたらどうだろう。**

と考えてみた。

すると、そのテストコードの役割が変わる。

---

# Legacy由来テストは「正解」にしない

Legacy SourceやLegacy BehaviorからAIが生成したテストを、正式なExpectedとして扱わない。

あくまでも、

> **旧システムをこう解釈すると、こういう振る舞いだったらしい。**

というReferenceにする。

```text
Legacy System
↓
AI解析
↓
Legacy Reference Test
↓
新システム環境向けへ変換
↓
Reference
```

一方、正式なテストは、

```text
Human Approved Structured Intent
↓
Validation Type
↓
TestPattern
↓
Expected
↓
Canonical Test
```

から生成する。

この二つを比較する。

```text
Legacy由来 Reference Test

        VS

Structured Intent由来 Canonical Test
```

ここで重要なのは、**Reference Testを信頼しないこと** である。

---

# 一致しているときは、あまり面白くない

例えば、

```text
Legacy Reference : REJECT
Canonical        : REJECT
```

なら、

> 旧挙動と現在承認した意図は、少なくともこの点では一致していそう。

という参考情報になる。

大量に一致しているなら、機械的に通過候補として扱えるかもしれない。

しかし、本当に価値が出るのは、**ズレたとき** である。

---

# ズレた瞬間、参考程度のテストコードに価値が生まれる

例えば、

```text
Legacy Reference : ACCEPT
Canonical        : REJECT
```

となった。

ここで、

> **なんで？**

が生まれる。

可能性はいくつもある。

```text
Legacyのバグ
Legacyに隠れた例外仕様
Structured Intentの抽出漏れ
Validation Typeの不足
Constraintの不足
業務仕様変更
Legacy Reference Test生成AIの誤読
新環境向け変換時の誤り
```

どれかは、まだ分からない。

しかし、**調べるべき場所が光った。**

ここが重要である。

Reference Testは正解ではない。

でも、

> **正式なExpectedとのズレを発生させる観測装置**

として使える。

言い換えるなら、

> **信頼できないから価値がないのではない。信頼しないという契約にした瞬間、違和感検出器として価値が生まれる。**

という、少し不思議な構造である。

---

# 品質保証を諦めたら、品質改善に使えるかもしれない

最初は、

```text
AI生成Test
↓
品質を保証しなければならない
↓
大量レビュー
↓
人間が死ぬ
```

だった。

しかし、Referenceとして扱うなら、

```text
AI生成Reference Test
↓
品質保証しない
↓
Canonical Testと機械比較
↓
ズレだけ抽出
↓
人間が意味を見る
```

に変わる。

極端な話、100万件のReference Testが生成されても、人間は100万件を見ない。

```text
1,000,000 Reference Tests
        ↓
Canonical Testsと機械Diff
        ↓
8,000 mismatch
        ↓
AIでType / Responsibility単位にCluster
        ↓
37種類の意味的Diff
        ↓
人間が37個を見る
```

ということができれば、人間の承認量は、システム規模と単純比例しなくなる可能性がある。

ここで、Approval Engineeringの話へ戻ってくる。

> **大量に作る技術ではなく、大量に見なくて済む構造を作る。**

そのために、

- Type
- Constraint
- Responsibility
- Expected導出
- Diff
- Cluster

を使う。

---

# Legacy由来情報は「観測」、Structured Intent由来は「承認済み期待」

この二つは、最初から分けておいた方がよいと思っている。

```text
Legacy由来
= Observed / Reference

Structured Intent由来
= Approved / Canonical
```

さらにNew SystemのActualを加えると、三者比較になる。

```text
Legacy Observed
        │
        ▼
Reference Test ─────┐
                    │
Approved Intent     │
        │           │
        ▼           │
Canonical Test ─────┤ 比較
                    │
New System          │
        │           │
        ▼           │
New Actual ─────────┘
```

例えば、

```text
Legacy = Canonical = New
```

なら、旧挙動・承認意図・新実装が一致している。

```text
Legacy ≠ Canonical = New
```

なら、旧システムから意図的に改善した可能性がある。

```text
Legacy = New ≠ Canonical
```

なら、旧システムの古い挙動やバグまで、新システムへコピーしてしまった可能性がある。

```text
Legacy = Canonical ≠ New
```

なら、新実装側の問題を疑いやすい。

この三者比較は、Legacyを正解にしないためにも重要だと思っている。

---

# これは「レガシーからテストコードを作る話」ではない

今回の妄想を一番誤解されたくないのは、ここである。

これは、

> **Legacy SourceからAIに正しいテストコードを生成させる。**

という話ではない。

それをやろうとすると、

> **その膨大なテストコードの品質を、誰が保証するのか。**

という問題へ戻ってしまう。

今回考えているのは、

```text
Legacy System
↓
Behavior / Rule / Constraint候補を観測
↓
Structured Intent候補へ整理
↓
人間が意味を承認
↓
Approved Structured Intent
↓
正式なTestPattern / Expected / Test Codeを生成
```

という流れである。

Legacy由来のテストコードは、その横に置く。

```text
Legacy
↓
Reference Test

Approved Structured Intent
↓
Canonical Test
```

そして、**ズレだけを見る。**

つまり、

> **「テストコードが無かった」という歴史を埋めるために、膨大なテストコードを後付けするのではない。**

> **テストコードより上位にあるStructured Intentを新しく作る。**

これが、この妄想の中心にある。

---

# Legacy Codeは「最後のSource」ではなく「意図を掘る遺跡」になるかもしれない

今までは、巨大Legacy Codeを見ると、

```text
古い
怖い
触れない
負債
```

と考えたくなる。

しかし、もしAIによって、

```text
if
switch
magic number
DB constraint
画面制御
例外処理
Batch条件
State Transition
```

を大量に観測し、

```text
Responsibility
Validation Type
Constraint
Business Rule
Behavior
Exception
```

へ圧縮できるなら、Legacy Codeの見え方は変わるかもしれない。

それは、

> **何十年もの業務知識が埋まった遺跡**

になる。

その遺跡から、コードをそのまま移植するのではなく、**意図を救出する。**

そして、救出したStructured Intentから、新しいシステムを再構築する。

---

# 構造化された意図による再構築

今のところ、この妄想には、**「構造化された意図による再構築」** という言葉が一番しっくりきている。

```text
Legacy System
        ↓
Behavior Observation
        ↓
Responsibility / Rule / Constraint抽出
        ↓
Type化・構造化
        ↓
Human Approval
        ↓
Approved Structured Intent
        ↓
TestPattern / Expected導出
        ↓
Application / Test生成
        ↓
Legacy / Canonical / New のDiff
        ↓
不足Intentを補正
        ↓
再生成
```

これは、単純なコード変換でもない。

テストコード生成でもない。

そして、私はあえて、**リファクタリングという言葉も使いたくない。**

同じ内部構造をきれいにするというより、

> **旧システムに閉じ込められた意味を救出し、その意味から別のシステムを作り直す。**

というイメージだからである。

---

# もしかすると、コードは長期保存すべき本体ではないのかもしれない

ここまで来ると、少し怖い問いが出てくる。

> **ソースコードは、本当にSourceなのだろうか。**

もちろん、現在の開発ではSource Codeは極めて重要である。

Gitで管理する。レビューする。テストする。保守する。

それを否定する話ではない。

でも、長期的に残したいものを考えたとき、本当に重要なのは、

```text
このシステムは何をするのか
なぜそうするのか
何を保証するのか
どこまで許すのか
何を禁止するのか
どんな例外があるのか
```

という、**人間の意図** ではないだろうか。

コードは時代とともに変わる。

言語も変わる。Frameworkも変わる。Runtimeも変わる。

しかし、意図が十分な粒度でDataとして残っていれば、その時代の実行環境へ再投影できる可能性がある。

---

# Code is Viewという妄想

今の私の頭の中では、こうなっている。

```text
Structured Intent Data
        │
        ├─→ Application Code
        ├─→ Test Code
        ├─→ Document
        ├─→ UI
        └─→ Other Views
```

この仮説が成立するなら、

> **Code is View.**

ということになる。

昔から、

```text
Data
↓
View
```

を分けることは考えてきた。

Studioくんでも、

```text
JSON / ViewDef
↓
Grid / Editor / Search
```

ということをしている。

しかし、その考えを突き詰めていった結果、**ソースコードまでViewになってしまった。**

これは、さすがに少し妄想が過ぎる気もする。

でも、一枚の画像と数回の会話からStudioくんの原型が生まれた経験を振り返ると、完全に笑い飛ばす気にもなれない。

---

# この妄想の始まりを振り返る

改めて順番を並べてみる。

```text
AI協働ではJSONが大事らしい
↓
「JSONってなんやっけ？」
↓
でもJSONは人間フレンドリーじゃない
↓
昔の画面画像を一枚AIへ渡す
↓
「これみたいなの作って」
↓
Studioくんのプロトタイプ誕生
↓
ViewDef
↓
Field Definition
↓
Validation Type
↓
minimum_minus_1
↓
「これ、毎回人間が考えなくてよくない？」
↓
TestPatternを導出
↓
Expectedも導出
↓
責務定義に元情報だけ置けばよくない？
↓
Test CodeもViewでは？
↓
Application CodeもViewでは？
↓
Structured IntentがSourceでは？
↓
巨大Legacyも、
Structured Intentへ救出できれば
再構築できるんじゃない？
```

始まりは、**JSONってなんやっけ？** だった。

途中で、**minimum_minus_1** が出てきた。

そして今、**巨大レガシーシステムをどうにかできるんじゃないか** というところまで来てしまった。

話が大きすぎる。

---

# これは、まだ妄想である

ここまで書いたことは、現時点では仮説である。

特に巨大システムでは、

- 非機能要件
- 性能
- 同時実行
- Transaction
- 障害復旧
- Security
- 運用
- 外部システム依存
- 暗黙の業務判断
- 歴史的例外

など、単純なField DefinitionやValidation Typeでは表現できないものが大量にある。

Structured Intentをどこまで記述すれば、本当に同じBehaviorを再構築できるのか。

まだ全く分からない。

しかし、だからこそ、**再構築してみればよい。**

再構築できなければ、何が足りなかったのかを見る。

```text
Responsibility不足？
Constraint不足？
Type不足？
Behavior不足？
State Transition不足？
Expected不足？
非機能要件不足？
```

その不足をStructured Intentへ戻す。

そしてまた生成する。

この繰り返し自体が、Structured Intentを育てる方法になるかもしれない。

---

# 最後に

私は最初から、

> ソースコードはViewである。

などと考えていたわけではない。

JSONを人間フレンドリーにしたかっただけである。

昔作った画面の画像を一枚、AIへ渡した。

ソースコードは探せばあった。

でも、

> **「まぁ、この画像でどうにかなるやろぉ〜」**

と思った。

それでStudioくんが生まれた。

その後、

`minimum_minus_1`

を見ながら、

> **これ、毎回考えなくていいやん。**

と思った。

そこから、TestPatternが生成物になった。

Expectedも生成物になった。

Test Codeも生成物に見え始めた。

そして最後には、Application Codeまで生成物に見えてきた。

---

:::message
**人間の意図を十分な粒度で構造化Dataとして残すことができれば、ソースコードは再生成可能なViewになるのではないか。**

**そして、Legacy Systemに閉じ込められた意図をそこまで救出できれば、「テストコードが無かった」という歴史そのものを飛び越えて、Structured Intentからシステムを再構築できるのではないか。**
:::

もちろん、まだ妄想である。

でも、もし本当に、Structured Intentだけから、元システムと同じ必要なBehaviorを持つシステムを再生成できたとしたら。

そのとき、

**何をSourceと呼ぶのか。**

少しだけ、変わるのかもしれない。

---

[AI駆動開発研究日誌や、思考拡張・AI承認駆動開発の記事はこちら](https://zenn.dev/frb_tamasub)

この思考拡張・AI駆動開発の実例として、私はFRB（Fishing Rod Benchmark）という個人研究を続けている。  
釣り竿の感度を振動として比較・可視化しようとする個人研究だが、そこで繰り返してきたのは「差分」「再現性」「違和感」「構造化」であり、今回の思考にもその影響がかなり入っている。

- [FRB（Fishing Rod Benchmark）釣り竿の「感度」を数値化する話 宣言](https://qiita.com/tamasub/items/2b6649748e1772b7eec1)
