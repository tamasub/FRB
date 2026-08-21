---
title: "AI承認駆動開発 #5｜ソースコードがViewになった日——構造化された意図からシステムを再構築できるか"
emoji: "🧩"
type: "idea"
topics: ["ai", "development", "testing", "legacy", "approval"]
published: true
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

---
■ノーコード擬き マスタメンテナンス画面（2017年作成）
![alt text](/images/ai-approval-driven-development-05-legacy/non-code.png)

---

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
■今のStudioくん（プロトタイプ時の画像なし💦）

![alt text](/images/ai-approval-driven-development-05-legacy/studio.png)

---

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

# Studioくんを成立させた、最初の明示的な制約

昔のノーコードもどき画面から、JSON EditorとしてStudioくんを作り直すとき、
昔にはなかった機能を一つ追加した。

**SubGrid** である。

JSONを扱う以上、

```text
親
└ 子
   └ 孫
      └ ひ孫
         └ ...
```

のように、技術的にはもっと深いネストへ対応していくこともできる。

しかし、その頃の私はAI協働を始めたばかりで、
ちょうど **「制約」** という言葉を意識し始めていた。

そこで、Studioくんに最初の明示的な制約を置いた。

> **意味階層は2階層まで。**

である。

これは単なる実装都合ではなかった。

```text
何階層でも扱えるJSON Editorを目指す
```

のではなく、

```text
Studioくんが責任を持って扱う世界は、
意味階層2階層まで
```

と決めた。

今振り返ると、

**機能を追加したからStudioくんが成立しただけではない。**

**「やらないこと」を決めたから、Studioくんが成立した。**

そして、この経験も今回の話へつながっている。

```text
ViewDef
→ どう見せたいかを外へ出す

Constraint
「意味階層は2階層まで」
→ どこまで許すかを外へ出す

Responsibility / Field Definition
→ 何を保証するかを外へ出す
```

つまり、Structured Intentという言葉を思いつくより前から、

**人間の意図・制約・責務を、少しずつコードの外へ出していた**

ことになる。

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

上位の定義から**一意に導出できるなら**、

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

# Structured Intentには、すでに「手持ちの武器」があった

ここで、もう一つ気づいた。

Structured Intentを新しく考えようとしていたが、
その材料になりそうなものは、すでにAI協働の中で使っていた。

それが、

> **判断軸・制約・責務という、手持ちの武器**

である。

私の中では、今のところ次のように整理している。

```text
判断軸
= 複数の成立する案から、
  何を優先して選ぶか

制約
= 何を越えてはいけないか
  どこまでを責任範囲とするか

責務
= システムとして何を保証するか
```

Studioくんを振り返ると、
これらは後から急に作った理屈でもない。

例えば、

```text
ViewDef
→ どう見せたいか

「意味階層は2階層まで」
→ どこまで許すかという制約

責務定義・項目定義
→ 何を保証するか
```

という形で、少しずつコードの外へ出してきた。

だから今は、

> **Structured Intentの中核には、判断軸・制約・責務が来るのではないか。**

と考えている。

項目定義は、その中でも特に扱いやすい
**責務の具体的な表現の一つ**
として見えている。

例えば、

```text
Structured Intent
│
├─ 判断軸
│   └─ 何を優先するか
│
├─ 制約
│   └─ 何を越えてはいけないか
│
├─ 責務
│   ├─ 項目定義
│   ├─ Behavior
│   ├─ State Transition
│   ├─ Business Rule
│   └─ 固有Expected
│
└─ Type
    ├─ Semantic Type
    └─ Validation Type
```

そして、その下流に、

```text
Validation Type / Constraint
        ↓
TestPattern
        ↓
具体値
        ↓
Expected
        ↓
Test Definition
        ↓
Test Code
```

を置く。

ここで大切なのは、

**人間が下流の一件一件を承認しないこと**

である。

例えば、

```text
minimum_minus_1
maximum_plus_1
```

を一件ずつ承認するのではない。

人間が見るのは、もっと上位の、

```text
この判断軸でよいか
この制約でよいか
この責務でよいか
このTypeでよいか
この固有Expectedでよいか
```

である。

そして、そこから一意に導出できるものは、
できるだけプログラムへ倒す。

つまり今回の話は、

> **責務定義・項目定義をSourceにする**

というより、

> **判断軸・制約・責務を中心としたStructured IntentをSourceにし、項目定義・Type・TestPattern・Expected・Test Codeへ投影していく**

という方が、今のところしっくりきている。


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

:::message
**ここまでは、Studioくんを作る中で実際に起きたことを整理している。**

**ここから先は、その体験を巨大レガシーシステムまで拡張して考えた「大妄想」である。**
:::

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
不足Intent（制約・判断軸・責務）を補正
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
        ├─ 判断軸
        ├─ 制約
        ├─ 責務
        ├─ Type
        ├─ Behavior / State Transition
        └─ 固有Expected
                │
                ├─→ Application Code
                ├─→ Test Code
                ├─→ Document
                ├─→ UI
                └─→ Other Views
```

今の私の頭の中では、Structured Intent Dataは単なる仕様書ではない。　　

そこには、これまでAI協働の中で使ってきた 判断軸・制約・責務 が入り、　　　

さらにType、Behavior、State Transition、固有Expectedなどがぶら下がる。


この整理を突き詰めていくと、

> Code is View.

というところまで来てしまう。

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
SubGrid
↓
最初の明示的な制約
「意味階層は2階層まで」
↓
判断軸・制約・責務という
手持ちの武器
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
単純なField DefinitionやValidation Typeだけでは表現しきれないものが大量にある。

例えば、

- 性能や同時実行性などの非機能要件
- Transaction境界や障害復旧
- Securityや運用上の制約
- 外部システムとの依存関係
- 文書化されていない暗黙知
- 長年の運用で積み上がった歴史的例外

である。

ここは、この仮説の弱点として隠すより、

> **Structured Intentには、何を積めば本当に再構築可能になるのか。**

という研究課題として扱った方が面白いと思っている。

例えば、機能要件だけで再構築してBehavior Diffが残ったとする。

そのとき、

```text
Responsibility不足？
Constraint不足？
判断軸不足？
Type不足？
Behavior不足？
State Transition不足？
固有Expected不足？
非機能要件不足？
暗黙知の救出漏れ？
歴史的例外の未記述？
```

と調べる。

不足していた意味をStructured Intentへ戻す。

そして、また生成する。

```text
Structured Intent v1
↓
再生成
↓
Behavior Diff

不足Intent(暗黙知)を発見
↓
Structured Intent v2
↓
再生成
↓
Behavior Diff
```

この繰り返し自体が、

> **システムを再構築するために必要な「意図の必要十分条件」を発見する実験**

になるかもしれない。

つまり、

非機能要件、暗黙知、歴史的例外は、
単なる注意書きではない。

**Structured IntentというDataに、いったい何を残す必要があるのかを炙り出す未解決テーマ**

である。

---

# そして、この妄想はStudioくん自身で実験できるのではないか

ここまで書いて、もう一つ気づいた。

巨大レガシーシステムを用意しなくても、

**この仮説は、Studioくん自身で小さく実験できるのではないか。**

例えば、Studioくんの一つの責務を選ぶ。

その責務について、

```text
判断軸
制約
責務
項目定義
Validation Type
固有Expected
```

をStructured Intentとして外へ出す。

そして、

**現在の実装コードを見せずに**

そのStructured Intentだけから、
同じ責務を持つ実装を再生成してみる。

さらに、

```text
既存StudioのBehavior
        ↓
Legacy / Reference側の観測

Structured Intent
        ↓
Canonical Test生成

再生成した新実装
        ↓
New Actual
```

を比較する。

もしBehavior Diffが出たら、

```text
実装生成側の問題？
Structured Intentの不足？
制約の記述漏れ？
責務の粒度不足？
Expectedの不足？
```

を調べる。

そして、Structured Intentへ戻す。

これは巨大レガシー再構築そのものではない。

でも、

> **Structured Intentだけから、元コードを見ずに同じ必要なBehaviorを再構築できるか。**

という今回の仮説を、
最小サイズで確かめることはできる。

もし成功すれば、

今回の記事に初めて、

**「妄想ではなく、観測できた現象」**

が一つ増える。

逆に失敗しても、

> **何がDataとして足りなかったのか。**

が分かる。

それ自体が、Structured Intentの設計材料になる。

巨大レガシーシステムを救えるかどうかは、まだ分からない。

でも、

**この仮説を試すための最初のシステムなら、もう手元にある。**

Studioくんである。

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
追伸：
負の遺産 レガシーシステム を、現在のAIでどうにかしようとした時、どんなシナリオが描けるのか？  
そんな空想を記事にしてみた。


---

[AI駆動開発研究日誌や、思考拡張・AI承認駆動開発の記事はこちら](https://zenn.dev/frb_tamasub)

この思考拡張・AI駆動開発の実例として、私はFRB（Fishing Rod Benchmark）という個人研究を続けている。  
釣り竿の感度を振動として比較・可視化しようとする個人研究だが、そこで繰り返してきたのは「差分」「再現性」「違和感」「構造化」であり、今回の思考にもその影響がかなり入っている。

- [FRB（Fishing Rod Benchmark）釣り竿の「感度」を数値化する話 宣言](https://qiita.com/tamasub/items/2b6649748e1772b7eec1)
