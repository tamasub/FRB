# 📄 責務定義とテスト設計
*(source: `AI協働031_責務定義とテスト設計_20260818_204902.md`)*

## 責務定義とテスト設計

### 001 User

画像がアップロードされました

ふんわり質問。今は細かく詰めるつもりはなし。
Diff JSON Viewer の責務定義、テストパターンを　JSON STUDIOの考え方を継承しようとしたときにどうにかなる案ある？💦

### 002 Assistant

あぁーーー、そこね（笑）
今の補足で気にしてるポイント分かった。

JSON Studioでやったのは、雑に言うとこうやったよね。

項目定義
  minimum = 0
  maximum = 100
  required = true

  ↓

テストパターン略語
  minimum
  minimum_minus_1
  maximum
  maximum_plus_1
  null

つまり、

項目が持っている契約から、どのTestPatternを実行するかを項目定義側に紐づける

という構造。

Diff JSON Viewerの「責務定義」でこれをやろうとすると、確かにそのままではイメージしにくい。
でもたぶん、一段だけ概念を足すと綺麗にハマる。

項目定義の validation_type に相当するものを、責務側にも作る

例えばこの責務。

検索語を入力してファイルを抽出する

これをただの文章として持つんじゃなくて、

JSON
{
  "responsibility_id": "diff_file_filter",
  "caption": "検索語を入力してファイル抽出",
  "responsibility_type": "collection_filter"
}

みたいにする。

この

collection_filter

が、JSON Studioにおける

integer
string
date

みたいなテストパターン生成元になるイメージ。

すると collection_filter 用の標準TestPatternを用意できる。

EMP    空条件
ONE    1件ヒット
MULTI  複数件ヒット
NONE   0件ヒット
DUP    同一対象内で複数ヒット
SCOPE  対象範囲外にヒットあり
RESET  条件解除

責務定義には、

JSON
{
  "responsibility_id": "diff_file_filter",
  "responsibility_type": "collection_filter",
  "test_patterns": [
    "EMP",
    "ONE",
    "MULTI",
    "NONE",
    "DUP",
    "RESET"
  ]
}

みたいに書ける。

これならJSON Studioでやったことと、ほぼ同じ構造になる。

しかも右側の

選択ファイル内を検索

も同じ collection_filter を使えるけど、ちょっと性質が違う。

JSON
{
  "responsibility_id": "selected_file_diff_filter",
  "responsibility_type": "scoped_collection_filter",
  "test_patterns": [
    "EMP",
    "ONE",
    "MULTI",
    "NONE",
    "SCOPE",
    "RESET"
  ]
}

ここで SCOPE が効く。

例えば、

選択ファイル A
検索語 caption

A → 2件ヒット
B → 10件ヒット

なら、

SCOPE
Expected:
Aの2件だけ表示
Bは表示されない

となる。

これ、かなり気持ちいい（笑）

要するに対応関係を作るとこうやと思う。

JSON Studio	Diff Viewer
Field Definition	Responsibility Definition
validation_type	responsibility_type
minimum / maximum / required	Guarantee / Behavior Rule
minimum_minus_1 等	EMP / ONE / MULTI / NONE / SCOPE 等
Definition Test Runner	Responsibility Test Runner

で、俺が特に大事やと思うのは、

テストパターン略語を「Diff Viewer専用語」にしすぎないこと。

例えば、

DIFF_FILE_SEARCH_EMPTY
DIFF_FILE_SEARCH_ONE
DIFF_FILE_SEARCH_MULTI

と作ったら、また画面ごとのテスト定義になる。

そうじゃなくて、

Collection Filter
  EMP
  ONE
  MULTI
  NONE
  SCOPE
  RESET

としておけば、将来、

インシデント一覧検索

Markdownファイル検索

JSON一覧検索

Diff一覧検索

全部に同じパターンを使える。

これ、Validation Type Catalog とほぼ同じ思想なんよ。

だから俺なら今の段階では、

Responsibility Type Catalog

みたいなものが将来生える、と考えるかな。

collection_filter
selection
load
reset
status_filter
detail_projection

とか。

その型ごとに、

標準TestPattern略語

を持たせる。

ただし、ここで一個だけJSON Studioとの違いがある。

数値項目なら、

minimum
↓
minimum_minus_1

はほぼ自動でExpectedまで出せる。

一方、

collection_filter
↓
MULTI

だけでは、

何を検索対象にするのか
何件返るべきなのか

までは分からない。

なので責務テスト側では、

TestPattern略語
+
Fixture
+
Guarantee

の3つがセットになると思う。

つまり、

JSON Studio

FieldDef
    ↓
TestPattern
    ↓
Expectedをほぼ自動生成

に対して、

Responsibility

ResponsibilityDef
    ↓
TestPattern略語
    ↓
Fixtureを当てる
    ↓
GuaranteeからExpected生成

になる。

たぶんここが、今イメージしづらかった正体やと思う。

責務は値そのものじゃないから、TestPatternだけではExpectedが決まらない。
でも、

責務の「型」を定義して、その型に標準TestPattern略語をぶら下げる

ところまでは、JSON Studioの思想をかなり素直に継承できる。

これ、思ったより綺麗につながると思う（笑）
しかも「項目定義駆動テスト」から、ほんまに一段上の**「責務定義駆動テスト」**に進んでる感じがする。

### 003 User

JSON Studioで言うところの、Validation Type に相当するものをどれだけ考えることができるか？って話よね。
Validation Type＝テストパターンの集合体やもんね

### 004 Assistant

そうそうそう。そこが本丸やと思う。（笑）

JSON Studioでいう、

Validation Type
= その種類の値に対して
  実施すべき標準TestPatternの集合

やもんね。

だから Diff JSON Viewer 側で考えるべき問いは、

「画面の責務には、どんな“標準的な振る舞いの型”が存在するのか？」

になる。

で、ここ考えてみると結構出せそう。

たとえば最初の候補だけでも、

仮のType	対象責務	TestPatternの例
LOAD	ファイル読込	正常／空／不正形式／対象外形式
FILTER	一覧絞り込み	0件／1件／複数件／全件
SCOPED_FILTER	選択範囲内検索	範囲内Hit／範囲外Hit／混在／0件
SELECTION	ファイル選択	未選択／1件選択／選択変更
STATUS_FILTER	Status絞り込み	各Status／該当なし／全Status
PROJECTION	詳細表示	1件／複数情報／欠損項目
RESET	初期状態へ戻す	条件あり→解除／選択あり→解除
EXPAND_COLLAPSE	Raw JSON等	閉→開／開→閉
ENCODING	UTF-8等	標準／指定変更／不正文字
SAVE_AS	別名保存があるなら	正常／キャンセル／既存名等

みたいな感じ。

ただ、ここで一個JSON Studioとは違う面白い問題が出ると思う。

1責務 = 1 Type では足りないかもしれない

たとえば右側の、

選択ファイル内を検索

は、

FILTER
+
SCOPE
+
SELECTION_REQUIRED

という3つの性質を持ってる。

なので、

JSON
{
  "responsibility_id": "search_selected_file",
  "test_types": [
    "FILTER",
    "SCOPED",
    "SELECTION_REQUIRED"
  ]
}

みたいにした方が美しい可能性がある。

これ、かなり重要。

JSON Studioの場合は、

integer
date
string

みたいに値の型が比較的ひとつに決まりやすい。

でも責務は、

検索する
かつ
選択範囲に限定する
かつ
未選択時には実行できない

という複数の振る舞いを合成している。

だから責務側では、

Validation Type相当を一個巨大な型として作るのではなく、TestPattern Familyを合成する

方が伸びる気がする。

たとえば、

FILTER
  EMPTY_QUERY
  ZERO_HIT
  ONE_HIT
  MULTI_HIT
  CLEAR_QUERY

SCOPED
  HIT_IN_SCOPE
  HIT_OUT_OF_SCOPE
  HIT_MIXED

SELECTION_REQUIRED
  NO_SELECTION
  VALID_SELECTION
  CHANGE_SELECTION

右検索の責務なら、この3集合を参照する。

つまり、

Responsibility Definition
       ↓
TestPattern Families
       ↓
必要な標準TestPattern集合を合成
       ↓
具体的TestPattern生成

になる。

これ、俺はかなり好き（笑）

そしてこの考え方まで行くと、名称もひょっとすると Responsibility Type より、

Behavior Type
または
Test Pattern Family

の方が正確かもしれん。

なぜなら欲しいのは責務の分類そのものじゃなくて、

「この責務には、どんな標準テスト群を当てるべきか」を決める分類

だから。

JSON Studioで、

Validation Type
= テストパターン集合を選ぶキー

だったのと完全に同じで、

Behavior Type
= 責務テストパターン集合を選ぶキー

になる。

ここ、かなり掘る価値あると思う。

最初にDiff Viewerを教材にして Behavior Typeを10個前後洗い出す。
そのあとMarkdown Studioや設定画面を眺めて、

「これ他画面でも使えるやん」

となったものだけ標準Typeへ昇格させる。

このやり方なら、いきなり巨大な体系を設計せず、JSON Studioでやった Validation Type Catalog育成の再演 ができる（笑）

### 005 User

JSON studioとかでも同じだけど、

RESET
初期状態へ戻す
って話を　どうにか汎用的な流れをつくろうとしたときにどう考える？

### 006 Assistant

あぁー、RESETを「初期状態へ戻すボタンのテスト」と考えた瞬間に専用化するんよね。
汎用化するなら、もっと上に上げて、

「現在状態を、定義済みの基準状態へ遷移させる責務」

として扱うのが綺麗やと思う。

つまり RESET そのものを最上位Typeにせず、

STATE_TRANSITION
  └─ RESTORE_TO_BASELINE
        └─ target = INITIAL_STATE

くらいに考える。

「初期状態」をコードに持たない

例えば Diff Viewer の初期状態が、

JSON
{
  "selected_file": null,
  "file_search": "",
  "detail_search": "",
  "status_filter": "all",
  "detail_line_filter": "all"
}

だったとする。

一方 JSON Studioなら、

JSON
{
  "selected_row": null,
  "search_text": "",
  "detail_mode": "view",
  "dialog_open": false
}

みたいになる。

値は全然違う。

でもRESETの責務はどちらも、

Current State
    ↓
RESET
    ↓
Defined Baseline State

で同じ。

ここで大事なのは、

RESETが何を初期化するかをRESET自身に知識として持たせない

ことやと思う。

RESETは、

「この画面に定義された baseline_state に戻せ」

しか知らない。

するとテストパターンも汎用化できる。

例えば RESTORE_TO_BASELINE の標準TestPattern集合として、

略語（仮）	意味
BASE	既に基準状態からRESET
ONE	1状態だけ変更してRESET
MULTI	複数状態を変更してRESET
KEEP	RESET対象外の状態を保持
REPEAT	RESETを繰り返しても同じ
SCOPE	指定された範囲だけRESET

みたいにできる。

例えば Diff Viewerなら、

Fixture:
file_search = "caption"
selected_file = "app.js"
status_filter = "modified"

Action:
RESET

Expected:
file_search = ""
selected_file = null
status_filter = "all"

JSON Studioなら同じ MULTI で、

Fixture:
search_text = "customer"
selected_row = 5
dialog_open = true

Action:
RESET

Expected:
search_text = ""
selected_row = null
dialog_open = false

になる。

TestPatternは完全に同じ。FixtureとBaseline定義だけが違う。

これやと思う。

さらに、ここでめちゃくちゃ重要なのが 「戻さないもの」 も定義すること。

たとえば、

Diff ViewerのRESET

戻す
- 検索語
- 選択ファイル
- Status filter

戻さない
- 読み込んだDiffToJson
- UTF-8指定

かもしれない。

あるいはJSON Studioで、

戻す
- 選択行
- 検索条件
- 編集ダイアログ状態

戻さない
- 読み込んだData JSON
- ViewDef
- Workspace

かもしれない。

なのでBaseline定義は、

JSON
{
  "state_contract": {
    "reset_scope": [
      "selected_file",
      "file_search",
      "detail_search",
      "status_filter"
    ],
    "preserve": [
      "loaded_document",
      "encoding"
    ]
  }
}

みたいになってもいい。

すると KEEP パターンが自動的に生える。

RESET後

reset_scope
→ baselineと一致すること

preserve
→ RESET前と一致すること

おお、これ結構強い（笑）

で、もっと抽象化すると、RESETだけの話じゃなくなってくる。

State Transition

Current State
      ↓
    Action
      ↓
Target State
      ↓
Expected State Contract

になる。

例えば、

RESET
→ INITIAL_STATEへ

CANCEL
→ BEFORE_EDIT_STATEへ

RELOAD
→ LOADED_STATEへ

CLEAR_SEARCH
→ SEARCH_EMPTY_STATEへ

全部同じ構造。

つまり、汎用Test Runner側は、

① Fixtureで事前状態を作る
② Actionを実行する
③ Target State Contractを取得
④ Actual Stateを取得
⑤ Expectedとの差分を見る

だけになる。

これ、JSON Studioの思想にかなり近い

JSON Studioでは、

Validation Type
↓
TestPattern集合
↓
値を作る
↓
Validator実行
↓
Expected比較

だった。

状態責務なら、

State Transition Type
↓
TestPattern集合
↓
事前Stateを作る
↓
Action実行
↓
Target State Contractと比較

になる。

なのでRESETに相当するTypeを考えるというより、

「状態遷移」というValidation Type相当を作って、その一種としてRestore-to-Baselineを置く

のが一番汎用的な気がする。

これならDiff Viewerだけじゃなく、JSON Studio、Markdown Studio、設定画面まで普通に食える。

そして個人的には、ここで Initial StateそのものがExpectedになる のがかなり面白いと思う。

Initial State Definition
= RESETテストのExpected生成元

になるから。

つまりまた、期待値をテストコードに書かず、定義側から引っ張れる。
たぶん狙ってる方向はこっちやと思う（笑）


---

I said:

雑談。添付の会話についていけてないところあるけど、ばっくり今の状態を整理すると、 AIは俺の想像を超えた共通化・標準化を徹底的することができる存在。 AIが作り出すプログラムのソースを追いかえることを本気であきらめて、 人間が承認する為に十分なネタ＝「責務定義とテストパターン、expected、Diff　の　各種データ」の見やすさだけに執着してＵＩを整えてスムーズに承認できるようにしていけば、400KS/人月の承認ができてしまうのではないか疑惑・・・・。

---

うん。**かなりその整理で合ってると思う。**
しかも、今日の「責務定義 → Behavior Type / TestPattern Family → Expected → Diff」の話まで来て、400KS/人月の話が前よりずっと現実的な構造に見えてきた。添付の会話でも、責務を個別テストケースとして抱えるのではなく、責務の「型」から標準TestPatternを合成する方向へ進んでる。

ただ、一か所だけ言い換えると、もっと強い気がする。

**「ソースを追いかけることを諦める」ではなく、
「ソースコードを、人間の主たる承認対象から降ろす」**。

これやと思う。

今までの開発は、

```text
AIがコードを作る
↓
人間がコードを読む
↓
テスト結果を見る
↓
承認
```

だった。

これを本気で捨てて、

```text
人間
  ↓ 承認
責務定義
  ↓
標準TestPattern
  ↓
Expected
  ↓
汎用Runner
  ↓
Actual
  ↓
Diff
```

にする。

**コードはこの裏側にいる。**

```text
責務定義
   ↓
AI
   ↓
┌──────────────┐
│ 大量の実装コード │ ← 基本、人間は追わない
└──────────────┘
   ↓
Actual
   ↓
Expectedとの差分
```

ここが、とんでもなく大きな転換なんよね。

そして今日の話で、さらに一段進んだと思う。

AIに毎回、

「この検索機能には何をテストしましょう？」

と考えさせる必要すらなくなり始めている。

```text
FILTER
SCOPED
SELECTION_REQUIRED
RESET
LOAD
...
```

みたいな**標準的な振る舞いの型**を人間が一度承認してしまえば、

```text
責務
↓
Behavior Type
↓
標準TestPattern集合
↓
Fixture
↓
Expected
```

まで相当部分が機械的に落ちる。

つまりAIの「恐ろしいほどの共通化能力」の本当の使い道って、**400KSのコードを速く書かせることじゃない**のかもしれん。

**400KSの中から、人間が新しく判断しなければならない部分だけを徹底的に消していく。**

こっち。

だから極端に言えば、

```text
400KS
```

という数字そのものが、だんだん意味を失う。

人間にとって重要なのは、

```text
400KS中、

新しい責務はいくつ？
新しいBehavior Typeはいくつ？
既存標準から外れたTestPatternはいくつ？
Expectedから外れたDiffはいくつ？
人間の新規判断はいくつ？
```

になる。

**承認量の単位が「KS」から「新規判断数」に変わる。**

ここ、かなりデカいと思う（笑）

そして、そう考えると今Studioくんで一生懸命やっているUI改善も、単なる「見やすいツールを作っています」じゃなくなる。

むしろ400KS構想の**ど真ん中**。

```text
AIの生成能力
       ↑
       │ ほぼ際限なく上がる
       │
──────────────
       人間の認知帯域 ← ボトルネック
──────────────
       │
       ↓
責務 / TestPattern / Expected / Diff
をどれだけ高速に認識・承認できるか
```

だから、

**責務定義を一瞬で読めるUI。
TestPatternの網羅性を一瞬で把握できるUI。
Expectedの根拠へすぐ飛べるUI。
Diffの異常だけ目に飛び込んでくるUI。**

ここへの異常なまでの執着は、かなり筋が通ってる。

むしろ最終的には、

> **コード品質を上げるUIではなく、人間の承認帯域を広げるUI**

を作ってる、と言った方が近いかもしれん。

ただし、400KS/人月が成立するための条件が一個ある。

**標準化したものまで毎回人間が読み直したら負け。**

一度、

```text
FILTERという型はこれでよい
RESETという型はこれでよい
このExpected生成規則でよい
このRunnerの検証方法でよい
```

と承認したら、それは資産にして次から人間の判断対象から外す。

そして人間が見るのは、

```text
新しいもの
標準から外れたもの
Diffが出たもの
AIが判断できなかったもの
```

だけ。

これなら、前から言ってた**「人間判断数ミニマム化」**と完全につながる。

なので今の仮説を一文にすると、俺ならこう整理する。

> **AIに400KSを書かせ、人間が400KSをレビューするのではない。
> AIに共通化・標準化を徹底させ、400KSの中から「人間が新しく判断すべき差分」だけを露出させる。
> 人間はその差分を、責務・TestPattern・Expected・Diffとして承認する。**

これなら「400KS/人月」は、無茶なコードレビュー速度の話じゃなくなる。

**400KSを、数十個とか数百個の「人間が意味を理解できる判断単位」へ圧縮できるか？**

という研究になる。

……だいぶヤバいところまで来てると思うで、これ（笑）
しかも今日やってたDiff JSON Viewerの「RESETをどう汎用化する？」みたいな、一見ちっちゃい話が、実は**その圧縮率を上げる研究そのもの**なんよ。


----

I said:

01b_axis_commonize_priority　の　抽象化概念を俺が理解しないといけない時がきたよや爆笑
例えばの例として、抽象化することで、こういう共通化を実現できるって話を簡単な例で理解しておきたい💦
これをわかってないと、抽象化を語れないって話になってもうた爆笑

---

そうそうそう（笑）
**これ、今読み直すとかなり良いところまで行ってる。** むしろ今日の議論で、「このサンプルの何が良かったのか」が後から説明できるようになった感じやね。

一番いいのは、最初からちゃんと

```text
1 Responsibility
    ↓
複数 Guarantee
    ↓
Guaranteeごとに
TestPattern Seed
Expected Type
```

になってるところ。

`grid_column_build` という責務ひとつに対して、

```text
g001 非表示を除外する
g002 順序を維持する
g003 空入力でも安全
g004 呼出側方針を適用する
g005 入力を破壊しない
```

と、**複数の期待される振る舞い**がぶら下がってる。

これ、今話してる構造そのもの。

---

ただ、今日の話を踏まえると、次の進化ポイントがものすごくはっきりする。

今のJSONでは、この5個を人間またはAIがかなり具体的に書いてる。

```json
"guarantee": "当該項目をGrid列へ含めない。",
"observable_result": "...",
"expected_def_type": "RuleExpectedDef",
"test_pattern_seed": "visible=false除外パターン"
```

未来は、ここをもっと**キーワードへ圧縮できないか？**なんよね。

例えばこの5保証、抽象化すると実はこう見える。

```text
g001 → FILTER
g002 → ORDER_PRESERVE
g003 → EMPTY_SAFE
g004 → POLICY_INJECTION
g005 → NO_MUTATION
```

うわ、かなり普通の標準Behaviorに見える（笑）

つまり将来的には責務定義が、

```json
{
  "responsibility_cd": "grid_column_build",

  "behaviors": [
    {
      "type": "FILTER",
      "condition": "grid.visible != false"
    },
    {
      "type": "ORDER_PRESERVE"
    },
    {
      "type": "EMPTY_SAFE",
      "empty_result": []
    },
    {
      "type": "POLICY_INJECTION",
      "policy": "includeField"
    },
    {
      "type": "NO_MUTATION",
      "target": "fields"
    }
  ]
}
```

くらいまで圧縮できる可能性がある。

そしてプログラムが、

```text
FILTER
↓
対象あり
対象なし
全対象除外
一部除外
...
↓
Expected生成
```

とか、

```text
ORDER_PRESERVE
↓
1件
複数件
途中除外あり
...
↓
Expected = 入力相対順序と一致
```

とか、

```text
NO_MUTATION
↓
実行前Snapshot
実行
実行後比較
↓
Expected = Diff 0
```

を勝手に作る。

---

なので、今のサンプルを評価すると、

**責務の粒度はかなりいい。**

なぜなら、

> `GridColumnBuilder.build` に入力を与えれば、
> 複数の振る舞いについて独立してTestPattern＋Expectedを作れる

から。

逆に今日見えてきた「まだ手作業な部分」は、

> **Guaranteeの内容そのもの。**

今は、

```text
人間/AI
↓
Guaranteeを5個具体的に考える
↓
TestPattern Seedを書く
```

だけど、目指してるのは、

```text
人間
↓
FILTER
ORDER_PRESERVE
EMPTY_SAFE
POLICY_INJECTION
NO_MUTATION
を承認
↓
プログラム
↓
Guarantee
TestPattern
Expected
を生成
```

なんやと思う。

これ、かなりデカい違い。

そしてもう一個大事なのは、

**`grid_column_build` 自体を標準責務Patternにする必要はないかもしれない。**

これはStudio固有の「具体的責務」。

その下に、

```text
FILTER
ORDER_PRESERVE
EMPTY_SAFE
POLICY_INJECTION
NO_MUTATION
```

という**汎用Behavior Patternを合成している**と見る方が綺麗。

つまり、

```text
Responsibility
grid_column_build
       ↓
Behavior Pattern集合
       ├ FILTER
       ├ ORDER_PRESERVE
       ├ EMPTY_SAFE
       ├ POLICY_INJECTION
       └ NO_MUTATION
       ↓
TestPattern集合
       ↓
Expected
```

これやね。

昨日話してた、

> Validation Type ＝ TestPattern集合を呼び出すキー

から、さらに一段進んで、

> **Responsibility ＝ Behavior Patternの合成**
>
> **Behavior Pattern ＝ TestPattern＋Expected生成規則**

という構造が見えてきた。

なのでこの昔のサンプル、かなり惜しいところまで既に来てるわ（笑）

**今まではGuaranteeを「書く」設計だった。
これからはGuaranteeを「生成する」設計へ行けるかもしれない。**

たぶん今日の議論の進歩はここやと思う。


---

# 📄 AI協働032_ループ_Claude Code責任者のBorisが「もうエージェント（AIの作業役）に指示は出してない」
*(source: `AI協働032_ループ_Claude Code責任者のBorisが「もうエージェント（AIの作業役）に指示は出してない」.md`)*

I said:この時期解説してぇーー https://x.com/ClaudeCode_love/status/2089115750279856242

----

うん、これかなり面白いやつやで笑
リンク先はスレッドの途中で、起点の投稿はこれ。

> Claude Code責任者 Boris Cherny が、**「もうエージェントへ逐一指示を出すのではなく、エージェントを動かす“ループ”を書く側になった」**という話。投稿者はそこから、Claude Codeでそのループをどう作るかを解説している。 ([X (formerly Twitter)][1])

#### まず「ループ」って何やねん

これ、単純な

```text
AIに仕事を頼む
↓
終わる
↓
また人間が指示する
```

じゃない。

こうなる。

```text
           ┌──────────────┐
           │   目的・ゴール   │
           └──────┬───────┘
                  ↓
             AIが作業する
                  ↓
              結果を見る
                  ↓
              検証する
                  ↓
          まだダメ？ ── Yes ─┐
             ↓ No            │
             完了             │
                              │
             修正・再計画 ←───┘
```

Anthropic自身もClaude Codeの **agentic loop** を、「コンテキストを集め、行動し、結果を検証し、完了するまで繰り返すサイクル」と定義している。つまりこの考え方自体は、Claude Codeの中核構造そのもの。 ([Claude][2])

ここでBorisの話が一段上なのよ。

**「AIに何をさせるか」を毎回考えるのではなく、
「AIが次に何をすべきか判断できる環境」を作る。**

人間の仕事が、

```text
プロンプトを書く
```

から、

```text
ループの構造を書く
```

へ上がる。

これが今言われている **Loop Engineering** の一番大事なところ。 ([Zenn][3])

#### で、このXスレッドが紹介している部品が面白い

投稿では、Claude Codeにすでに存在する仕組みを組み合わせて、このループを作ろうとしている。

たとえば **Skills**。これは「毎回同じ手順をプロンプトに書く」のをやめて、手順そのものを `SKILL.md` に外出しする仕組み。Anthropic公式も、繰り返し貼っている手順やチェックリストはSkill化する用途を明示している。 ([Claude][4])

そして **Hooks**。これはさらに重要で、

```text
AI：
「テストしようかな？」
```

ではなく、

```text
コード変更
↓
必ずテスト実行
```

のように、LLMの判断ではなく**決定論的なルール**を挿し込める。AnthropicもHooksを「プロジェクトルールの強制」「反復作業の自動化」に使う仕組みとしている。 ([Claude][5])

さらに **Subagents** を使えば、

```text
実装AI
↓
レビューAI
↓
テストAI
```

みたいに役割を分けられる。個々のサブエージェントには別プロンプト、別ツール、別Skill、別Hookまで持たせられる。 ([Claude][6])

そしてスレッド後半に出てくる **Auto Mode**。

投稿者が言ってるのは、

> 毎回「はい」を押していたらループにならない

という話。実際、現在のClaude CodeではPro/Max/TeamでAuto Modeが使われ、許可確認の多くを分類器側へ任せられる。投稿では同時に、暴走対策として「5回試したら止まる」のような上限も入れるべきだとしている。 ([X (formerly Twitter)][7])

要するにこう。

```text
Skill
= AIが何を知っているか・どう作業するか

Hooks
= 絶対守らせるルール

Subagent
= 誰に何を担当させるか

Auto Mode
= 人間の承認待ちを減らす

Loop
= それらを循環させる構造
```

これ、けっこう大きな思想転換やと思う。

---

### でな。

ここからが、うちら的にはめちゃくちゃ面白い。笑

前にループエンジニアリングの話をしたとき、あなたが引っ掛かったのは、

> **「何を正しいとするの？」**

だったやん。

今回の投稿を見ても、やっぱりそこは消えてない。

AIが

```text
作る
↓
確認する
↓
直す
↓
確認する
```

を無限に高速化できても、

**「確認するときの正しさ」**

は別問題なんよ。

ここで、今やってるAI承認駆動開発が綺麗に刺さる。

うちらの構造なら、

```text
人間
↓
目的
判断軸
制約
責務
Expected
↓
──────────────
      AI Loop
──────────────
実装
↓
TestPattern
↓
Runner実行
↓
Actual
↓
Diff
↓
修正
↓
再実行
──────────────
↓
人間承認
```

になる。

つまり、

**ループそのものを否定してるんじゃない。**

むしろ、

> **「ループの外側に、誰が正しさを定義するのかを置こう」**

って話なんよ。

ここ、かなり重要。

---

そしてExpectedの話まで入れると、さらに綺麗。

普通のAIループは、

```text
AI
↓
「これが正しいと思う」
↓
実装
↓
AI
↓
「うん、正しいと思う」
```

になり得る。

これが前から気持ち悪かったところ。

うちらは、

```text
Expected Terrain
        ↓
Actual Terrain
        ↓
      Diff
```

を**ループより先に置こうとしてる**。

だからAIは、

```text
正しさを発明しながら走る
```

のではなく、

```text
承認済みの地形へ近づくように走る
```

になる。

これ、めちゃくちゃ違う。

---

さらにもう一段ある。

今あなたがやってる

```text
違和感
↓
判断
↓
判断ログ
↓
昇格・蒸留
↓
判断軸・制約・責務・Expected
```

まで入れると、

**ループ自身が次回のループの品質を上げる。**

```text
      ┌──────── Human Approval ────────┐
      │                                │
目的・判断軸・制約・Expected             │
      ↓                                │
 AI Loop                              │
      ↓                                │
 Actual / Diff                         │
      ↓                                │
 違和感                                │
      ↓                                │
 判断ログ                               │
      ↓                                │
 昇格・蒸留 ───────────────────────────┘
```

これよ。

だから今回の投稿を、うちらの文脈に翻訳すると、

> **「AIをどう賢く使うか」の時代から、
> 「AIが自分で回れる環境をどう設計するか」の時代へ移っている。**

で、さらにうちらが考えてるのはその一段先で、

> **「そのループが、何を正しいとして回るのかを、人間がどう外部化・承認・育成するか」**

なんやと思う。

なので俺は今回の投稿を見てむしろ、

**「あーー、AI承認駆動開発の外側の箱が世の中から生えてきた」**

って感じる笑

Loop Engineeringが **実行循環** を作っていて、
今考えているやつは **正しさの循環** を作ろうとしてる。

この2個、競合しない。

**めちゃくちゃ綺麗に合体する。**

そして最終形はたぶん、

> **人間はAIへ仕事を指示する人ではなく、
> AIが判断し続けられる「地形・境界・停止点」を設計し、最後に承認する人になる。**

ここやと思う。これ、400KS/人月の話にもそのまま繋がるやつやで笑 ([anthropic.com][8])

[1]: https://x.com/ClaudeCode_love/status/2089115738154147955?utm_source=chatgpt.com "えええ？？発想が違いすぎる…！ Claude Code責任者の ..."
[2]: https://code.claude.com/docs/ja/glossary?utm_source=chatgpt.com "用語集 - Claude Code Docs"
[3]: https://zenn.dev/helloworld/articles/6c7de76320b6d2?utm_source=chatgpt.com "Context Engineeringの次が来た——Loop Engineering"
[4]: https://code.claude.com/docs/en/skills?utm_source=chatgpt.com "Extend Claude with skills - Claude Code Docs"
[5]: https://code.claude.com/docs/en/hooks-guide?utm_source=chatgpt.com "Automate actions with hooks - Claude Code Docs"
[6]: https://code.claude.com/docs/en/sub-agents?utm_source=chatgpt.com "Create custom subagents - Claude Code Docs"
[7]: https://x.com/ClaudeCode_love/status/2089115785461715026?utm_source=chatgpt.com "返信する 暴走対策は「5回試したら止まる」と回数の上限 ..."
[8]: https://www.anthropic.com/research/claude-code-expertise?utm_source=chatgpt.com "How Claude Code is used in practice"


---

# 📄 AI協働033_FRB_Responsibility_Inventory_Phase1_v0_1
*(source: `AI協働033_FRB_Responsibility_Inventory_Phase1_v0_1.md`)*

## 責務棚卸し Phase 1 — 既存責務を「今の粒度のまま」並べる

作成日: 2026-08-19  
ステータス: Draft / Phase 1  
対象: FRB Studio / AI承認駆動開発  
目的: 責務の粒度標準化・Behavior Pattern化・TestPattern / Expected自動生成を検討する前段として、既存責務を現在の粒度のまま棚卸しする。

---

### 0. 今回の研究目的

最終的に目指すのは、次の状態である。

```text
人間が少数の意味あるキーワードを承認
        ↓
標準Behavior / Optionを解決
        ↓
TestPatternをプログラム生成
        ↓
Expectedをプログラム生成
        ↓
Actual
        ↓
Diff
        ↓
人間承認
```

今回のPhase 1では、まだこの共通化を行わない。

まず、

> **現在、Studioくんの中で「責務」として何を、どの粒度で切っているか**

をそのまま見える状態にする。

---

### 1. Phase 1でやること

既存責務について、以下を可能な限りそのまま収集する。

- `responsibility_cd`
- `name`
- `test_level`
- `summary`
- `purpose`
- `source_file`
- `interface_name`
- `in_scope`
- `out_of_scope`
- `constraint_ids`
- `guarantees`
- 既存テスト
- 備考

#### このPhaseではやらないこと

以下はPhase 2以降で行う。

- 責務名の統合
- 責務粒度の変更
- SAVE / LOAD / RESET 等への標準Pattern化
- GuaranteeのBehavior Pattern化
- TestPatternの自動生成
- Expectedの自動生成
- JSON Schemaの確定
- Runtime実装
- Test Runner実装

**Phase 1では「今あるものを、そのまま並べる」。**

---

### 2. 棚卸し時の重要ルール

#### Rule 1 — 先に抽象化しない

たとえば既存責務が、

```text
grid_column_build
```

なら、そのまま記録する。

この段階で、

```text
FILTER
BUILD
PROJECTION
```

などへ置き換えない。

---

#### Rule 2 — 粒度が変でも直さない

Phase 1の目的は、責務粒度の現状把握である。

```text
責務Aは細かすぎる
責務Bは大きすぎる
責務CとDはほぼ同じ
```

と思っても、まずそのまま記録する。

違和感は `phase1_notes` に残す。

---

#### Rule 3 — Guaranteeも原文を優先する

Guaranteeについても、先に共通Behaviorへ変換しない。

```text
visible=falseを除外する
入力順を維持する
空入力でも例外停止しない
入力を変更しない
```

など、現在定義されている意味をそのまま保持する。

---

#### Rule 4 — 「機械生成できそう」はまだ判定しない

Phase 1では、

```text
このGuaranteeはNO_MUTATIONにできそう
この責務はRESET Patternになりそう
```

といった判断は確定しない。

気づいた場合はメモだけ残す。

---

### 3. 責務一覧

Phase 1完了時には、まずこの一覧を埋める。

| No | responsibility_cd | 責務名 | Test Level | Source / Interface | Guarantee数 | 既存Test | Phase1 Notes |
|---:|---|---|---|---|---:|---|---|
| 1 | `grid_column_build` | Grid列生成責務 | UT | `GridColumnBuilder.build` | 5 | あり | 現時点の代表サンプル |
| 2 |  |  |  |  |  |  |  |
| 3 |  |  |  |  |  |  |  |
| 4 |  |  |  |  |  |  |  |
| 5 |  |  |  |  |  |  |  |
| 6 |  |  |  |  |  |  |  |
| 7 |  |  |  |  |  |  |  |
| 8 |  |  |  |  |  |  |  |
| 9 |  |  |  |  |  |  |  |
| 10 |  |  |  |  |  |  |  |
| 11 |  |  |  |  |  |  |  |
| 12 |  |  |  |  |  |  |  |
| 13 |  |  |  |  |  |  |  |
| 14 |  |  |  |  |  |  |  |
| 15 |  |  |  |  |  |  |  |
| 16 |  |  |  |  |  |  |  |
| 17 |  |  |  |  |  |  |  |
| 18 |  |  |  |  |  |  |  |
| 19 |  |  |  |  |  |  |  |
| 20 |  |  |  |  |  |  |  |

---

## 4. 責務詳細

### 4.1 `grid_column_build` — Grid列生成責務

#### 基本情報

```yaml
responsibility_cd: grid_column_build
name: Grid列生成責務
test_level: UT
approval_status: draft
enabled: true
source_file: wwwroot/js/responsibilities/grid_column_builder.js
interface_name: GridColumnBuilder.build
```

#### Summary

`grid.visible=false` を除外し、ViewDef上の列順を維持したGrid列配列を返す。

#### Purpose

ViewDefのfields定義から、Grid表示に利用する列配列を確定する。

#### In Scope

- `grid.visible` の解釈
- 表示列の抽出
- 列順の維持
- 呼出側 `includeField` 方針の適用

#### Out of Scope

- DOM描画
- 列幅計算
- Gridイベント処理
- CSV出力

#### Constraints

- `constitution_11`
- `constitution_12`

#### Guarantees

##### `grid_column_build_g001`

- guarantee_type: `rule`
- condition: fieldsに`grid.visible=false`の項目が含まれる場合
- guarantee: 当該項目をGrid列へ含めない。
- observable_result: 返却列のfield一覧に非表示項目が存在しない。
- expected_def_type: `RuleExpectedDef`
- test_pattern_seed: `visible=false除外パターン`
- priority: high

##### `grid_column_build_g002`

- guarantee_type: `state`
- condition: 表示対象フィールドが複数ある場合
- guarantee: 返却列の順序はViewDef fieldsの順序を維持する。
- observable_result: 返却field一覧が入力順と一致する。
- expected_def_type: `StateExpectedDef`
- test_pattern_seed: `表示列の順序維持パターン`
- priority: medium

##### `grid_column_build_g003`

- guarantee_type: `rule`
- condition: fieldsが未指定または空配列の場合
- guarantee: 例外で停止せず空配列を返す。
- observable_result: 返却値が空配列である。
- expected_def_type: `RuleExpectedDef`
- test_pattern_seed: `fields未指定安全パターン`
- priority: medium

##### `grid_column_build_g004`

- guarantee_type: `interface`
- condition: includeField方針が呼出側から指定された場合
- guarantee: 指定された方針による列採用結果を返す。
- observable_result: includeFieldの判定結果と返却列が一致する。
- expected_def_type: `InterfaceExpectedDef`
- test_pattern_seed: `カスタムincludeField適用パターン`
- priority: medium

##### `grid_column_build_g005`

- guarantee_type: `no_side_effect`
- condition: Grid列を生成した場合
- guarantee: 入力されたfields定義を変更しない。
- observable_result: 処理前後のfieldsが同一である。
- expected_def_type: `StateExpectedDef`
- test_pattern_seed: `ViewDef fields非破壊パターン`
- priority: medium

#### 既存テスト

- `grid_column_build_visible_fields_basic`
- `grid_column_build_empty_fields_safe`

#### Phase 1 Notes

現時点では責務・Guaranteeともに変更しない。

Phase 2では、このGuarantee群について、

```text
他責務にも同じGuarantee構造が存在するか？
同じ意味を持つGuaranteeを共通Behaviorとして扱えるか？
```

を横断比較する予定。

---

## 5. 追加責務記入テンプレート

以下を責務ごとにコピーして使用する。

### X.X `<responsibility_cd>` — `<責務名>`

#### 基本情報

```yaml
responsibility_cd:
name:
test_level:
approval_status:
enabled:
source_file:
interface_name:
```

#### Summary

-

#### Purpose

-

#### In Scope

- 

#### Out of Scope

- 

#### Constraints

- 

#### Guarantees

##### `<guarantee_id>`

- guarantee_type:
- condition:
- guarantee:
- observable_result:
- expected_def_type:
- test_pattern_seed:
- priority:
- enabled:

#### 既存テスト

- 

#### Phase 1 Notes

- 粒度に関する違和感:
- 他責務との類似:
- 保証の重複候補:
- その他:

---

## 6. Phase 1 完了条件

次を満たしたらPhase 1完了とする。

- 主要な既存責務が一覧化されている
- 各責務の現在の粒度が保持されている
- 各責務のGuaranteeが可能な範囲で収集されている
- Source / Interfaceが追跡可能になっている
- 既存Testとの対応が確認できる
- 共通化・Pattern化はまだ実施していない
- 粒度や重複への違和感だけがNotesとして残っている

---

## 7. Phase 2への引継ぎ

Phase 2では、Phase 1で集めたGuaranteeを横断して比較する。

想定する流れ:

```text
既存Responsibility
        ↓
Guaranteeを横断比較
        ↓
同じ意味を持つGuaranteeを発見
        ↓
Behavior Pattern候補
        ↓
TestPattern生成可能性を評価
        ↓
Expected生成可能性を評価
```

Phase 2の主要な問いは次の一つとする。

> **このBehaviorキーワードを人間が1つ承認すると、何個のTestPattern + Expectedを安全にプログラム生成できるか？**

---

### 現時点の研究上の仮説

```text
Responsibility
  = 1つのExpectedではない

Responsibility
  ↓
複数Guarantee
  ↓
複数TestPattern
  ↓
TestPatternごとのExpected
```

さらに将来的には、

```text
具体Responsibility
        ↓
複数Behavior Pattern
        ↓
各Behavior Patternから
TestPattern + Expectedをプログラム生成
```

という構造へ昇格できる可能性がある。

ただし、この仮説を先に既存責務へ押し付けない。

**まずPhase 1では、現物を見る。**


---

# 📄 AI協働033_FRB_Responsibility_Inventory_Phase1_v0_2
*(source: `AI協働033_FRB_Responsibility_Inventory_Phase1_v0_2.md`)*

## 責務棚卸し Phase 1 — 既存責務を「今の粒度のまま」並べる

作成日: 2026-08-19  
ステータス: Draft / Phase 1  
対象: FRB Studio / AI承認駆動開発  
目的: 責務の粒度標準化・Behavior Pattern化・TestPattern / Expected自動生成を検討する前段として、既存責務を現在の粒度のまま棚卸しする。

---

### 0. 今回の研究目的

最終的に目指すのは、次の状態である。

```text
人間が少数の意味あるキーワードを承認
        ↓
標準Behavior / Optionを解決
        ↓
TestPatternをプログラム生成
        ↓
Expectedをプログラム生成
        ↓
Actual
        ↓
Diff
        ↓
人間承認
```

今回のPhase 1では、まだこの共通化を行わない。

まず、

> **現在、Studioくんの中で「責務」として何を、どの粒度で切っているか**

をそのまま見える状態にする。

---

### 1. Phase 1でやること

既存責務について、以下を可能な限りそのまま収集する。

- `responsibility_cd`
- `name`
- `test_level`
- `summary`
- `purpose`
- `source_file`
- `interface_name`
- `in_scope`
- `out_of_scope`
- `constraint_ids`
- `guarantees`
- 既存テスト
- 備考

#### このPhaseではやらないこと

以下はPhase 2以降で行う。

- 責務名の統合
- 責務粒度の変更
- SAVE / LOAD / RESET 等への標準Pattern化
- GuaranteeのBehavior Pattern化
- TestPatternの自動生成
- Expectedの自動生成
- JSON Schemaの確定
- Runtime実装
- Test Runner実装

**Phase 1では「今あるものを、そのまま並べる」。**

---

### 2. 棚卸し時の重要ルール

#### Rule 1 — 先に抽象化しない

たとえば既存責務が、

```text
grid_column_build
```

なら、そのまま記録する。

この段階で、

```text
FILTER
BUILD
PROJECTION
```

などへ置き換えない。

---

#### Rule 2 — 粒度が変でも直さない

Phase 1の目的は、責務粒度の現状把握である。

```text
責務Aは細かすぎる
責務Bは大きすぎる
責務CとDはほぼ同じ
```

と思っても、まずそのまま記録する。

違和感は `phase1_notes` に残す。

---

#### Rule 3 — Guaranteeも原文を優先する

Guaranteeについても、先に共通Behaviorへ変換しない。

```text
visible=falseを除外する
入力順を維持する
空入力でも例外停止しない
入力を変更しない
```

など、現在定義されている意味をそのまま保持する。

---

#### Rule 4 — 「機械生成できそう」はまだ判定しない

Phase 1では、

```text
このGuaranteeはNO_MUTATIONにできそう
この責務はRESET Patternになりそう
```

といった判断は確定しない。

気づいた場合はメモだけ残す。

---

### 3. 責務一覧

Phase 1完了時には、まずこの一覧を埋める。

> 抽出方針:
> - **JSON Object Studio** は、既存の Responsibility Master / ResponsibilityDef Draft を優先して採用する。
> - **Markdown Studio / Diff JSON / MetaDiff** は、現時点で責務JSONとして明示定義されていないものが多いため、実装上の関数境界から「責務候補」として拾う。
> - Phase 1では責務粒度の統合・分割・Behavior Pattern化は行わない。
> - `Guarantee数=未定義` は「保証が存在しない」ではなく、現時点で責務定義JSONとしてGuarantee配列が定義されていないことを示す。

| No | responsibility_cd | 責務名 | Test Level | Source / Interface | Guarantee数 | 既存Test | Phase1 Notes |
|---:|---|---|---|---|---:|---|---|
| 1 | `grid_column_build` | Grid列生成責務 | UT | `wwwroot/js/responsibilities/grid_column_builder.js` / `GridColumnBuilder.build` | 5 | あり | **[JSON] 既存責務定義**。Responsibility Master登録済み。 |
| 2 | `search_filter` | 検索条件評価責務 | UT | `wwwroot/js/responsibilities/search_filter.js` / `SearchFilter.apply` | 8 | あり | **[JSON] 既存責務定義**。Expected Test 4件＋Smoke/検索Operator系Testあり。 |
| 3 | `csv_export` | CSV出力責務 | UT | `wwwroot/js/responsibilities/csv_exporter.js` / `CsvExporter.resolveFields / CsvExporter.export` | 6 | あり | **[JSON] 既存責務定義**。Expected Test 2件＋Smokeあり。 |
| 4 | `grid_aggregate` | Grid数値集計責務 | UT | `wwwroot/js/responsibilities/grid_aggregator.js` / `GridAggregator.build` | 6 | あり | **[JSON] 既存責務定義**。Responsibility Smokeで集計・非数値除外等を確認。 |
| 5 | `viewdef_parse` | ViewDef解釈責務 | UT | ResponsibilityDef Draft / `ViewDefParser.parse` | 未定義 | 専用Test未確認 | **[JSON] 既存Draft責務**。Active ViewDefを後続責務向けに解釈する契約として定義済み。 |
| 6 | `editor_field_build` | Editor項目生成責務 | UT | ResponsibilityDef Draft / `EditorFieldBuilder.build` | 未定義 | 専用Test未確認 | **[JSON] 既存Draft責務**。ViewDef fieldsからEditor項目定義を生成する契約。 |
| 7 | `search_state` | 検索状態管理責務 | UT/CT | `wwwroot/js/runtime/search_state.js` / Draft `SearchStateManager.update` | 未定義 | 関連Testあり | **[JSON] 既存Draft責務**。検索条件・結果・現在行・UI stateの管理境界。 |
| 8 | `renderer_display` | Renderer表示責務 | UT/CT | ResponsibilityDef Draft / `Renderer.render` | 未定義 | 専用Test未確認 | **[JSON] 既存Draft責務**。判断済みViewModel/StateをDOMへ反映する責務として定義済み。 |
| 9 | `markdown_document_load` | Markdown文書読込責務 | 未定義 | `wwwroot/mdViewer.html` / `loadWorkspaceMarkdown / loadManagedMarkdown / loadLocalFile / loadMarkdown` | 未定義 | 関連静的Testあり | **[Markdown] 実装から抽出候補**。Workspace / managed / externalの読込経路が存在。仮CD。 |
| 10 | `markdown_document_save` | Markdown文書保存責務 | 未定義 | `wwwroot/mdViewer.html` / `saveWorkspaceMarkdown / saveManagedMarkdown / saveMarkdownWithNativeDialog` | 未定義 | 関連静的Testあり | **[Markdown] 実装から抽出候補**。Front Matter materialize・Save Safetyを経由して保存。仮CD。 |
| 11 | `markdown_mode_transition` | Markdownモード遷移責務 | 未定義 | `wwwroot/mdViewer.html` / `setMarkdownMode` | 未定義 | 関連静的Testあり | **[Markdown] 実装から抽出候補**。Viewer / Editor / Review切替とReadOnly・表示状態を管理。仮CD。 |
| 12 | `markdown_review_session` | Markdown Review開始・再開責務 | 未定義 | `wwwroot/mdViewer.html` / `openExistingMarkdownReviewMode / startNewMarkdownReview` | 未定義 | 関連静的Testあり | **[Markdown] 実装から抽出候補**。既存Review再開とNEW Review開始が独立関数として存在。仮CD。 |
| 13 | `markdown_review_sidecar` | Markdown Review JSON永続化責務 | 未定義 | `wwwroot/mdViewer.html` / `saveMarkdownCommentSidecar / persistMarkdownCommentReviewMutation` | 未定義 | 関連静的Testあり | **[Markdown] 実装から抽出候補**。コメント・判定・ハイライトをReview JSONへ保持。仮CD。 |
| 14 | `diff_json_load` | Diff JSON読込責務 | 未定義 | `wwwroot/DiffJsonViewer.html` / `loadJsonFile / loadJsonUrl / applyDiffJson` | 未定義 | 関連静的Testあり | **[Diff JSON] 実装から抽出候補**。File/URL読込後に正規化・初期選択・各View更新を実施。仮CD。 |
| 15 | `diff_file_filter` | Diff対象ファイル抽出責務 | 未定義 | `wwwroot/DiffJsonViewer.html` / `fileMatches / renderFileList` | 未定義 | UI静的確認あり | **[Diff JSON] 実装から抽出候補**。左側検索語＋Statusで対象ファイルを抽出。仮CD。 |
| 16 | `diff_detail_filter` | 選択ファイル内差分抽出責務 | 未定義 | `wwwroot/DiffJsonViewer.html` / `hunkMatches / lineTypeMatches / renderDetail` | 未定義 | UI静的確認あり | **[Diff JSON] 実装から抽出候補**。選択範囲・検索語・行種別でDifference detailsを抽出。仮CD。 |
| 17 | `diff_json_save_as` | Diff JSON別名保存責務 | 未定義 | `wwwroot/DiffJsonViewer.html` / `saveDiffJsonAs` | 未定義 | あり | **[Diff JSON] 実装から抽出候補**。Native Save Asを優先し、利用不可時はbrowser downloadへfallback。仮CD。 |
| 18 | `metadiff_markdown_load` | MetaDiff Markdown読込責務 | 未定義 | `wwwroot/MetaDiff_HypothesisViewer.html` / `loadMarkdownFile` | 未定義 | 専用Test未確認 | **[MetaDiff] 実装から抽出候補**。Markdown Preview生成と埋込JSON抽出の起点。仮CD。 |
| 19 | `metadiff_evidence_extract` | MetaDiff根拠JSON抽出・正規化責務 | 未定義 | `wwwroot/MetaDiff_HypothesisViewer.html` / `extractJsonBlocks / normalizeEvidence` | 未定義 | 専用Test未確認 | **[MetaDiff] 実装から抽出候補**。`json` / `diff_hypothesis.json` blockを抽出しEvidence行へ正規化。仮CD。 |
| 20 | `metadiff_evidence_filter` | MetaDiff根拠差分絞り込み責務 | 未定義 | `wwwroot/MetaDiff_HypothesisViewer.html` / `rowMatches / renderEvidence` | 未定義 | 専用Test未確認 | **[MetaDiff] 実装から抽出候補**。検索語・ファイル・カテゴリ・Evidence ID focusをAND評価。仮CD。 |

#### Phase 1 一覧時点のメモ

```text
JSON Object Studio
  既にResponsibility Master / ResponsibilityDef Draftが存在する。
  → 既存定義を起点にできる。

Markdown Studio
  責務JSONとしての明示定義は未確認。
  ただし Load / Save / Mode / Review / Review JSON persistence は
  関数境界と静的テストから比較的はっきり拾える。

Diff JSON
  Load / 左ファイル抽出 / 選択ファイル内差分抽出 / Save As が
  独立した操作・関数境界として拾える。

MetaDiff
  Markdown Load / Embedded JSON Extraction+Normalization /
  Evidence Filter が実装上のまとまりとして拾える。
```

**この段階では、上記20件を同じ粒度だとはみなさない。**

Phase 2で初めて、

```text
大きすぎる責務
小さすぎる責務
他画面と同じ構造を持つ責務
複数Guaranteeへ分解できる責務
```

を横断比較する。

---

## 4. 責務詳細

### 4.1 `grid_column_build` — Grid列生成責務

#### 基本情報

```yaml
responsibility_cd: grid_column_build
name: Grid列生成責務
test_level: UT
approval_status: draft
enabled: true
source_file: wwwroot/js/responsibilities/grid_column_builder.js
interface_name: GridColumnBuilder.build
```

#### Summary

`grid.visible=false` を除外し、ViewDef上の列順を維持したGrid列配列を返す。

#### Purpose

ViewDefのfields定義から、Grid表示に利用する列配列を確定する。

#### In Scope

- `grid.visible` の解釈
- 表示列の抽出
- 列順の維持
- 呼出側 `includeField` 方針の適用

#### Out of Scope

- DOM描画
- 列幅計算
- Gridイベント処理
- CSV出力

#### Constraints

- `constitution_11`
- `constitution_12`

#### Guarantees

##### `grid_column_build_g001`

- guarantee_type: `rule`
- condition: fieldsに`grid.visible=false`の項目が含まれる場合
- guarantee: 当該項目をGrid列へ含めない。
- observable_result: 返却列のfield一覧に非表示項目が存在しない。
- expected_def_type: `RuleExpectedDef`
- test_pattern_seed: `visible=false除外パターン`
- priority: high

##### `grid_column_build_g002`

- guarantee_type: `state`
- condition: 表示対象フィールドが複数ある場合
- guarantee: 返却列の順序はViewDef fieldsの順序を維持する。
- observable_result: 返却field一覧が入力順と一致する。
- expected_def_type: `StateExpectedDef`
- test_pattern_seed: `表示列の順序維持パターン`
- priority: medium

##### `grid_column_build_g003`

- guarantee_type: `rule`
- condition: fieldsが未指定または空配列の場合
- guarantee: 例外で停止せず空配列を返す。
- observable_result: 返却値が空配列である。
- expected_def_type: `RuleExpectedDef`
- test_pattern_seed: `fields未指定安全パターン`
- priority: medium

##### `grid_column_build_g004`

- guarantee_type: `interface`
- condition: includeField方針が呼出側から指定された場合
- guarantee: 指定された方針による列採用結果を返す。
- observable_result: includeFieldの判定結果と返却列が一致する。
- expected_def_type: `InterfaceExpectedDef`
- test_pattern_seed: `カスタムincludeField適用パターン`
- priority: medium

##### `grid_column_build_g005`

- guarantee_type: `no_side_effect`
- condition: Grid列を生成した場合
- guarantee: 入力されたfields定義を変更しない。
- observable_result: 処理前後のfieldsが同一である。
- expected_def_type: `StateExpectedDef`
- test_pattern_seed: `ViewDef fields非破壊パターン`
- priority: medium

#### 既存テスト

- `grid_column_build_visible_fields_basic`
- `grid_column_build_empty_fields_safe`

#### Phase 1 Notes

現時点では責務・Guaranteeともに変更しない。

Phase 2では、このGuarantee群について、

```text
他責務にも同じGuarantee構造が存在するか？
同じ意味を持つGuaranteeを共通Behaviorとして扱えるか？
```

を横断比較する予定。

---

## 5. 追加責務記入テンプレート

以下を責務ごとにコピーして使用する。

### X.X `<responsibility_cd>` — `<責務名>`

#### 基本情報

```yaml
responsibility_cd:
name:
test_level:
approval_status:
enabled:
source_file:
interface_name:
```

#### Summary

-

#### Purpose

-

#### In Scope

- 

#### Out of Scope

- 

#### Constraints

- 

#### Guarantees

##### `<guarantee_id>`

- guarantee_type:
- condition:
- guarantee:
- observable_result:
- expected_def_type:
- test_pattern_seed:
- priority:
- enabled:

#### 既存テスト

- 

#### Phase 1 Notes

- 粒度に関する違和感:
- 他責務との類似:
- 保証の重複候補:
- その他:

---

## 6. Phase 1 完了条件

次を満たしたらPhase 1完了とする。

- 主要な既存責務が一覧化されている
- 各責務の現在の粒度が保持されている
- 各責務のGuaranteeが可能な範囲で収集されている
- Source / Interfaceが追跡可能になっている
- 既存Testとの対応が確認できる
- 共通化・Pattern化はまだ実施していない
- 粒度や重複への違和感だけがNotesとして残っている

---

## 7. Phase 2への引継ぎ

Phase 2では、Phase 1で集めたGuaranteeを横断して比較する。

想定する流れ:

```text
既存Responsibility
        ↓
Guaranteeを横断比較
        ↓
同じ意味を持つGuaranteeを発見
        ↓
Behavior Pattern候補
        ↓
TestPattern生成可能性を評価
        ↓
Expected生成可能性を評価
```

Phase 2の主要な問いは次の一つとする。

> **このBehaviorキーワードを人間が1つ承認すると、何個のTestPattern + Expectedを安全にプログラム生成できるか？**

---

### 現時点の研究上の仮説

```text
Responsibility
  = 1つのExpectedではない

Responsibility
  ↓
複数Guarantee
  ↓
複数TestPattern
  ↓
TestPatternごとのExpected
```

さらに将来的には、

```text
具体Responsibility
        ↓
複数Behavior Pattern
        ↓
各Behavior Patternから
TestPattern + Expectedをプログラム生成
```

という構造へ昇格できる可能性がある。

ただし、この仮説を先に既存責務へ押し付けない。

**まずPhase 1では、現物を見る。**


---

# 📄 AI協働033_FRB_Responsibility_Inventory_Phase1_v0_3
*(source: `AI協働033_FRB_Responsibility_Inventory_Phase1_v0_3.md`)*

## 責務棚卸し Phase 1 — 既存責務を「今の粒度のまま」並べる

作成日: 2026-08-19  
ステータス: Draft / Phase 1  
対象: FRB Studio / AI承認駆動開発  
目的: 責務の粒度標準化・Behavior Pattern化・TestPattern / Expected自動生成を検討する前段として、既存責務を現在の粒度のまま棚卸しする。

---

### 0. 今回の研究目的

最終的に目指すのは、次の状態である。

```text
人間が少数の意味あるキーワードを承認
        ↓
標準Behavior / Optionを解決
        ↓
TestPatternをプログラム生成
        ↓
Expectedをプログラム生成
        ↓
Actual
        ↓
Diff
        ↓
人間承認
```

今回のPhase 1では、まだこの共通化を行わない。

まず、

> **現在、Studioくんの中で「責務」として何を、どの粒度で切っているか**

をそのまま見える状態にする。

---

### 1. Phase 1でやること

既存責務について、以下を可能な限りそのまま収集する。

- `responsibility_cd`
- `name`
- `test_level`
- `summary`
- `purpose`
- `source_file`
- `interface_name`
- `in_scope`
- `out_of_scope`
- `constraint_ids`
- `guarantees`
- 既存テスト
- 備考

#### このPhaseではやらないこと

以下はPhase 2以降で行う。

- 責務名の統合
- 責務粒度の変更
- SAVE / LOAD / RESET 等への標準Pattern化
- GuaranteeのBehavior Pattern化
- TestPatternの自動生成
- Expectedの自動生成
- JSON Schemaの確定
- Runtime実装
- Test Runner実装

**Phase 1では「今あるものを、そのまま並べる」。**

---

### 2. 棚卸し時の重要ルール

#### Rule 1 — 先に抽象化しない

たとえば既存責務が、

```text
grid_column_build
```

なら、そのまま記録する。

この段階で、

```text
FILTER
BUILD
PROJECTION
```

などへ置き換えない。

---

#### Rule 2 — 粒度が変でも直さない

Phase 1の目的は、責務粒度の現状把握である。

```text
責務Aは細かすぎる
責務Bは大きすぎる
責務CとDはほぼ同じ
```

と思っても、まずそのまま記録する。

違和感は `phase1_notes` に残す。

---

#### Rule 3 — Guaranteeも原文を優先する

Guaranteeについても、先に共通Behaviorへ変換しない。

```text
visible=falseを除外する
入力順を維持する
空入力でも例外停止しない
入力を変更しない
```

など、現在定義されている意味をそのまま保持する。

---

#### Rule 4 — 「機械生成できそう」はまだ判定しない

Phase 1では、

```text
このGuaranteeはNO_MUTATIONにできそう
この責務はRESET Patternになりそう
```

といった判断は確定しない。

気づいた場合はメモだけ残す。

---

### 3. 責務一覧

Phase 1完了時には、まずこの一覧を埋める。

> 抽出方針:
> - **JSON Object Studio** は、既存の Responsibility Master / ResponsibilityDef Draft を優先して採用する。
> - **Markdown Studio / Diff JSON / MetaDiff** は、現時点で責務JSONとして明示定義されていないものが多いため、実装上の関数境界から「責務候補」として拾う。
> - Phase 1では責務粒度の統合・分割・Behavior Pattern化は行わない。
> - `Guarantee数=未定義` は「保証が存在しない」ではなく、現時点で責務定義JSONとしてGuarantee配列が定義されていないことを示す。

| No | responsibility_cd | 責務名 | Test Level | Source / Interface | Guarantee数 | 既存Test | Phase1 Notes |
|---:|---|---|---|---|---:|---|---|
| 1 | `grid_column_build` | Grid列生成責務 | UT | `wwwroot/js/responsibilities/grid_column_builder.js` / `GridColumnBuilder.build` | 5 | あり | **[JSON] 既存責務定義**。Responsibility Master登録済み。 |
| 2 | `search_filter` | 検索条件評価責務 | UT | `wwwroot/js/responsibilities/search_filter.js` / `SearchFilter.apply` | 8 | あり | **[JSON] 既存責務定義**。Expected Test 4件＋Smoke/検索Operator系Testあり。 |
| 3 | `csv_export` | CSV出力責務 | UT | `wwwroot/js/responsibilities/csv_exporter.js` / `CsvExporter.resolveFields / CsvExporter.export` | 6 | あり | **[JSON] 既存責務定義**。Expected Test 2件＋Smokeあり。 |
| 4 | `grid_aggregate` | Grid数値集計責務 | UT | `wwwroot/js/responsibilities/grid_aggregator.js` / `GridAggregator.build` | 6 | あり | **[JSON] 既存責務定義**。Responsibility Smokeで集計・非数値除外等を確認。 |
| 5 | `viewdef_parse` | ViewDef解釈責務 | UT | ResponsibilityDef Draft / `ViewDefParser.parse` | 未定義 | 専用Test未確認 | **[JSON] 既存Draft責務**。Active ViewDefを後続責務向けに解釈する契約として定義済み。 |
| 6 | `editor_field_build` | Editor項目生成責務 | UT | ResponsibilityDef Draft / `EditorFieldBuilder.build` | 未定義 | 専用Test未確認 | **[JSON] 既存Draft責務**。ViewDef fieldsからEditor項目定義を生成する契約。 |
| 7 | `search_state` | 検索状態管理責務 | UT/CT | `wwwroot/js/runtime/search_state.js` / Draft `SearchStateManager.update` | 未定義 | 関連Testあり | **[JSON] 既存Draft責務**。検索条件・結果・現在行・UI stateの管理境界。 |
| 8 | `renderer_display` | Renderer表示責務 | UT/CT | ResponsibilityDef Draft / `Renderer.render` | 未定義 | 専用Test未確認 | **[JSON] 既存Draft責務**。判断済みViewModel/StateをDOMへ反映する責務として定義済み。 |
| 9 | `markdown_document_load` | Markdown文書読込責務 | 未定義 | `wwwroot/mdViewer.html` / `loadWorkspaceMarkdown / loadManagedMarkdown / loadLocalFile / loadMarkdown` | 未定義 | 関連静的Testあり | **[Markdown] 実装から抽出候補**。Workspace / managed / externalの読込経路が存在。仮CD。 |
| 10 | `markdown_document_save` | Markdown文書保存責務 | 未定義 | `wwwroot/mdViewer.html` / `saveWorkspaceMarkdown / saveManagedMarkdown / saveMarkdownWithNativeDialog` | 未定義 | 関連静的Testあり | **[Markdown] 実装から抽出候補**。Front Matter materialize・Save Safetyを経由して保存。仮CD。 |
| 11 | `markdown_mode_transition` | Markdownモード遷移責務 | 未定義 | `wwwroot/mdViewer.html` / `setMarkdownMode` | 未定義 | 関連静的Testあり | **[Markdown] 実装から抽出候補**。Viewer / Editor / Review切替とReadOnly・表示状態を管理。仮CD。 |
| 12 | `markdown_review_session` | Markdown Review開始・再開責務 | 未定義 | `wwwroot/mdViewer.html` / `openExistingMarkdownReviewMode / startNewMarkdownReview` | 未定義 | 関連静的Testあり | **[Markdown] 実装から抽出候補**。既存Review再開とNEW Review開始が独立関数として存在。仮CD。 |
| 13 | `markdown_review_sidecar` | Markdown Review JSON永続化責務 | 未定義 | `wwwroot/mdViewer.html` / `saveMarkdownCommentSidecar / persistMarkdownCommentReviewMutation` | 未定義 | 関連静的Testあり | **[Markdown] 実装から抽出候補**。コメント・判定・ハイライトをReview JSONへ保持。仮CD。 |
| 14 | `diff_json_load` | Diff JSON読込責務 | 未定義 | `wwwroot/DiffJsonViewer.html` / `loadJsonFile / loadJsonUrl / applyDiffJson` | 未定義 | 関連静的Testあり | **[Diff JSON] 実装から抽出候補**。File/URL読込後に正規化・初期選択・各View更新を実施。仮CD。 |
| 15 | `diff_file_filter` | Diff対象ファイル抽出責務 | 未定義 | `wwwroot/DiffJsonViewer.html` / `fileMatches / renderFileList` | 未定義 | UI静的確認あり | **[Diff JSON] 実装から抽出候補**。左側検索語＋Statusで対象ファイルを抽出。仮CD。 |
| 16 | `diff_detail_filter` | 選択ファイル内差分抽出責務 | 未定義 | `wwwroot/DiffJsonViewer.html` / `hunkMatches / lineTypeMatches / renderDetail` | 未定義 | UI静的確認あり | **[Diff JSON] 実装から抽出候補**。選択範囲・検索語・行種別でDifference detailsを抽出。仮CD。 |
| 17 | `diff_json_save_as` | Diff JSON別名保存責務 | 未定義 | `wwwroot/DiffJsonViewer.html` / `saveDiffJsonAs` | 未定義 | あり | **[Diff JSON] 実装から抽出候補**。Native Save Asを優先し、利用不可時はbrowser downloadへfallback。仮CD。 |
| 18 | `metadiff_markdown_load` | MetaDiff Markdown読込責務 | 未定義 | `wwwroot/MetaDiff_HypothesisViewer.html` / `loadMarkdownFile` | 未定義 | 専用Test未確認 | **[MetaDiff] 実装から抽出候補**。Markdown Preview生成と埋込JSON抽出の起点。仮CD。 |
| 19 | `metadiff_evidence_extract` | MetaDiff根拠JSON抽出・正規化責務 | 未定義 | `wwwroot/MetaDiff_HypothesisViewer.html` / `extractJsonBlocks / normalizeEvidence` | 未定義 | 専用Test未確認 | **[MetaDiff] 実装から抽出候補**。`json` / `diff_hypothesis.json` blockを抽出しEvidence行へ正規化。仮CD。 |
| 20 | `metadiff_evidence_filter` | MetaDiff根拠差分絞り込み責務 | 未定義 | `wwwroot/MetaDiff_HypothesisViewer.html` / `rowMatches / renderEvidence` | 未定義 | 専用Test未確認 | **[MetaDiff] 実装から抽出候補**。検索語・ファイル・カテゴリ・Evidence ID focusをAND評価。仮CD。 |

#### Phase 1 一覧時点のメモ

```text
JSON Object Studio
  既にResponsibility Master / ResponsibilityDef Draftが存在する。
  → 既存定義を起点にできる。

Markdown Studio
  責務JSONとしての明示定義は未確認。
  ただし Load / Save / Mode / Review / Review JSON persistence は
  関数境界と静的テストから比較的はっきり拾える。

Diff JSON
  Load / 左ファイル抽出 / 選択ファイル内差分抽出 / Save As が
  独立した操作・関数境界として拾える。

MetaDiff
  Markdown Load / Embedded JSON Extraction+Normalization /
  Evidence Filter が実装上のまとまりとして拾える。
```

**この段階では、上記20件を同じ粒度だとはみなさない。**

Phase 2で初めて、

```text
大きすぎる責務
小さすぎる責務
他画面と同じ構造を持つ責務
複数Guaranteeへ分解できる責務
```

を横断比較する。

---

## 4. 責務詳細

### 4.1 `grid_column_build` — Grid列生成責務

#### 基本情報

```yaml
responsibility_cd: grid_column_build
name: Grid列生成責務
test_level: UT
approval_status: draft
enabled: true
source_file: wwwroot/js/responsibilities/grid_column_builder.js
interface_name: GridColumnBuilder.build
```

#### Summary

`grid.visible=false` を除外し、ViewDef上の列順を維持したGrid列配列を返す。

#### Purpose

ViewDefのfields定義から、Grid表示に利用する列配列を確定する。

#### In Scope

- `grid.visible` の解釈
- 表示列の抽出
- 列順の維持
- 呼出側 `includeField` 方針の適用

#### Out of Scope

- DOM描画
- 列幅計算
- Gridイベント処理
- CSV出力

#### Constraints

- `constitution_11`
- `constitution_12`

#### Guarantees

##### `grid_column_build_g001`

概要：非表示指定された項目をGrid列へ含めないことを保証する。

- guarantee_type: `rule`
- condition: fieldsに`grid.visible=false`の項目が含まれる場合
- guarantee: 当該項目をGrid列へ含めない。
- observable_result: 返却列のfield一覧に非表示項目が存在しない。
- expected_def_type: `RuleExpectedDef`
- test_pattern_seed: `visible=false除外パターン`
- priority: high

##### `grid_column_build_g002`

概要：表示対象フィールドの列順がViewDefの定義順を維持することを保証する。

- guarantee_type: `state`
- condition: 表示対象フィールドが複数ある場合
- guarantee: 返却列の順序はViewDef fieldsの順序を維持する。
- observable_result: 返却field一覧が入力順と一致する。
- expected_def_type: `StateExpectedDef`
- test_pattern_seed: `表示列の順序維持パターン`
- priority: medium

##### `grid_column_build_g003`

概要：fieldsが未指定または空でも安全に空配列を返すことを保証する。

- guarantee_type: `rule`
- condition: fieldsが未指定または空配列の場合
- guarantee: 例外で停止せず空配列を返す。
- observable_result: 返却値が空配列である。
- expected_def_type: `RuleExpectedDef`
- test_pattern_seed: `fields未指定安全パターン`
- priority: medium

##### `grid_column_build_g004`

概要：呼出側から指定されたincludeField方針に従って列を採用することを保証する。

- guarantee_type: `interface`
- condition: includeField方針が呼出側から指定された場合
- guarantee: 指定された方針による列採用結果を返す。
- observable_result: includeFieldの判定結果と返却列が一致する。
- expected_def_type: `InterfaceExpectedDef`
- test_pattern_seed: `カスタムincludeField適用パターン`
- priority: medium

##### `grid_column_build_g005`

概要：Grid列生成によって入力されたfields定義を変更しないことを保証する。

- guarantee_type: `no_side_effect`
- condition: Grid列を生成した場合
- guarantee: 入力されたfields定義を変更しない。
- observable_result: 処理前後のfieldsが同一である。
- expected_def_type: `StateExpectedDef`
- test_pattern_seed: `ViewDef fields非破壊パターン`
- priority: medium

#### 既存テスト

- `grid_column_build_visible_fields_basic`
- `grid_column_build_empty_fields_safe`

#### Phase 1 Notes

現時点では責務・Guaranteeともに変更しない。

Phase 2では、このGuarantee群について、

```text
他責務にも同じGuarantee構造が存在するか？
同じ意味を持つGuaranteeを共通Behaviorとして扱えるか？
```

を横断比較する予定。

---

## 5. 追加責務記入テンプレート

以下を責務ごとにコピーして使用する。

### X.X `<responsibility_cd>` — `<責務名>`

#### 基本情報

```yaml
responsibility_cd:
name:
test_level:
approval_status:
enabled:
source_file:
interface_name:
```

#### Summary

-

#### Purpose

-

#### In Scope

- 

#### Out of Scope

- 

#### Constraints

- 

#### Guarantees

##### `<guarantee_id>`

- guarantee_type:
- condition:
- guarantee:
- observable_result:
- expected_def_type:
- test_pattern_seed:
- priority:
- enabled:

#### 既存テスト

- 

#### Phase 1 Notes

- 粒度に関する違和感:
- 他責務との類似:
- 保証の重複候補:
- その他:

---

## 6. Phase 1 完了条件

次を満たしたらPhase 1完了とする。

- 主要な既存責務が一覧化されている
- 各責務の現在の粒度が保持されている
- 各責務のGuaranteeが可能な範囲で収集されている
- Source / Interfaceが追跡可能になっている
- 既存Testとの対応が確認できる
- 共通化・Pattern化はまだ実施していない
- 粒度や重複への違和感だけがNotesとして残っている

---

## 7. Phase 2への引継ぎ

Phase 2では、Phase 1で集めたGuaranteeを横断して比較する。

想定する流れ:

```text
既存Responsibility
        ↓
Guaranteeを横断比較
        ↓
同じ意味を持つGuaranteeを発見
        ↓
Behavior Pattern候補
        ↓
TestPattern生成可能性を評価
        ↓
Expected生成可能性を評価
```

Phase 2の主要な問いは次の一つとする。

> **このBehaviorキーワードを人間が1つ承認すると、何個のTestPattern + Expectedを安全にプログラム生成できるか？**

---

### 現時点の研究上の仮説

```text
Responsibility
  = 1つのExpectedではない

Responsibility
  ↓
複数Guarantee
  ↓
複数TestPattern
  ↓
TestPatternごとのExpected
```

さらに将来的には、

```text
具体Responsibility
        ↓
複数Behavior Pattern
        ↓
各Behavior Patternから
TestPattern + Expectedをプログラム生成
```

という構造へ昇格できる可能性がある。

ただし、この仮説を先に既存責務へ押し付けない。

**まずPhase 1では、現物を見る。**


---

# 📄 日本企業AI利益事例
*(source: `AI協働034_調査_日本企業AI利益事例20260819_212011.md`)*

## 日本企業AI利益事例

### 001 User

日本の大手企業でAIによる利益を伸ばしたっていう情報があればしらべておしえて

### 002 Assistant

あります。しかも調べてみると、2026年に入って「AIが利益に効いた」とかなり明確に言える日本企業が出てきています。
ただし、ここは2種類に分けた方がいいです。

① AI需要そのものが利益を押し上げた企業

アドバンテストはかなり強烈です。2026年4〜6月期は、売上高が前年同期比 +39.3%の3,675億円、営業利益が +53.3%の1,900億円、純利益が +93.8%の1,748億円。会社自身が、AI/HPC向け半導体の生産増加・複雑化によって半導体テスター需要が大きく伸びたことを主要因として説明しています。つまりこれは、かなり素直に 「AI投資拡大 → 製品需要増 → 利益増」 と読めます。
アドバンテスト

さらに面白いのがパナソニックです。2026年度1Qは営業利益 1,825億円で41年ぶりの過去最高。会社は「AIインフラ関連事業とその周辺事業が想定以上に伸長」と説明しています。インダストリー部門のAI関連売上だけでも1Q 749億円、前年同期比1.4倍。年間見通しも 2,700億円→3,100億円へ400億円上方修正しています。データセンター向け電源関連も1Q 1,130億円、1.9倍まで伸びています。
Panasonic Newsroom Global

フジクラもかなり分かりやすいです。同社は、生成AIの普及・拡大によるデータセンター投資が通信事業の利益を「significantly boosted（大幅に押し上げた）」と明記。上期は売上・営業利益・経常利益が過去最高となり、通期予想を 売上1兆1,090億円、営業利益1,790億円、純利益1,320億円へ引き上げています。
フジクラ

要するにこの3社は、

AI → 何となく生産性が上がりました

ではなく、

AI市場の拡大 → 受注・販売増 → 営業利益増

まで財務数字として見えています。

② AIを「社内で使って」経済効果を出した企業

こっちは、むしろユーザーさんの関心にはこっちの方が面白いと思う。

パナソニック コネクトが2026年7月にかなり衝撃的な数字を出しています。

2025年度に社内生成AI「ConnectAI」を約11,800人へ展開した結果、

年間78.8万時間を削減。総労働時間の3.4%。

前年比では削減時間が2倍になっています。用途も単なるチャットではなく、議事録、コード生成、ログ分析、提案書、設計書・仕様書作成などです。
Panasonic Newsroom Global

これは会社が「利益○億円増」とまでは換算していないので、利益増と断言するのはダメです。ただ、78.8万時間というのは相当デカい。

単純に年間1,800時間/人くらいで割れば、

約438人年分の時間です。

しかもパナソニック コネクトは次の段階として、AIを「聞く」から**「頼む」へ進化させ、SFA・ERPなど業務システムとAIエージェントを接続し、2030年には総労働時間10%削減**を目標にしています。
Panasonic Newsroom Global

これ、かなり重要な変化やと思います。

もう一つはNTTデータグループ。2025年10月時点で実践的な生成AI人材を 7万人まで育成し、社内で数百件のユースケースを創出。その知見を顧客向けビジネスに転換して、生成AI関連ビジネスで世界2,000件超の受注まで到達しています。こちらも生成AIだけの利益額は公表していませんが、

社内AI活用 → ノウハウ蓄積 → 顧客向けサービス → 受注

という経路が見えるのが面白いところです。
NTT DATA

で、ここからがちょっと面白い。

日本企業について「AIで利益上がった会社ある？」と調べると、現状はかなり二極化しています。

型	企業例	数字
AI需要で儲ける	アドバンテスト	営業利益 +53.3%
	パナソニック	1Q営業利益 過去最高
	フジクラ	AIデータセンター需要で利益大幅増
AIを使って儲ける	パナソニック コネクト	78.8万時間削減
	NTTデータ	生成AI関連2,000件超受注

そして、「AIを社員が使った結果、営業利益が○○億円増えました」まで因果を数字で公開している大手日本企業は、まだかなり少ないです。

ここ、めちゃくちゃ大事です。

パナソニック コネクトですら、

AIを使った
↓
78.8万時間減った
↓
その結果、利益はいくら増えた？

の最後の矢印は公開していません。
Panasonic Newsroom Global

これって、今考えている AI承認・生産性の話にもかなり刺さると思うんよ。

「AI導入しました」「○万時間削減しました」ではなく、

AI → 作業削減 → 処理量増加 → 売上/コスト → 営業利益

までExpected/Actualでつなげないと、本当の経営効果を承認できない。

むしろ今回調べていて、「AIのROIをどう承認するのか」自体が一個のテーマになるなと思いました（笑）。

もし興味あれば次、日本の大企業だけ10〜15社くらい掘って、「AI導入→工数削減→売上/利益」までどこまで数字を公開しているかランキングにしてみると、かなり面白いと思います。

Reuters
Advantest hikes profit forecast by 25% on AI boost
2025/10/28

この手の数字は今後どんどん増えるはずなので、定期的に「日本企業のAI利益事例」を拾うこともできます。

日本企業のAI利益事例を追跡

### 003 Assistant

設定しました！
毎週月曜に、日本の大手企業で AI活用／AI需要が売上・利益・コスト削減に結びついた新しい事例をチェックします。

特に 「AI導入 → 工数削減 → 売上・利益」まで数字でつながっている事例を優先して、新しい有力事例が見つかったときだけ通知します。

### 004 User

日本の大企業だけ10〜15社くらい掘って、「AI導入→工数削減→売上/利益」までどこまで数字を公開しているかランキングにして

### 005 Assistant
うん、掘ってみたらかなり面白かった（笑）。

結論から言うと、**2026年8月時点で、日本の大企業は「AI → 工数削減」まではかなり数字を出し始めている。でも「その削減が売上・営業利益を○億円押し上げた」まで一本の因果線で公開している企業は、今回見た12社ではゼロ**でした。

なので今回は、単純なAI活用度ではなく、**「経営効果をどこまで数字で公開したか」ランキング**にしました。

#### 判定基準

公開到達レベルをこう置きます。

* **Lv.5** = AI導入 → 工数/コスト削減 → 売上/利益増まで金額で因果を公開
* **Lv.4** = 工数削減を数値化 ＋ AI事業の受注/売上も数値化。ただし両者の因果は未接続
* **Lv.3** = 全社・大規模な工数削減を実績値で公開
* **Lv.2** = 部門・個別業務の工数削減を定量公開
* **Lv.1** = AI導入規模や活用事例のみ。経済効果は未数値化

これは**企業のAI能力ランキングではなく「開示の深さランキング」**です。

### 1位　NTT DATA — Lv.4

ここが一番「利益の手前」まで来ています。

社内のソフトウェア開発では、FY2023に生成AIを140件へ適用して**生産性7%向上**。その後FY2024は200プロジェクト、FY2025は500件超へ拡大し、従来の自動化と生成AIの組み合わせで**最大70%の生産効率向上**を目指しています。 ([NTT DATA][1])

さらに重要なのがここ。

生成AI関連ビジネスはグローバルで**2,000件超の受注**に到達。加えて、AIエージェント関連事業について**FY2027売上3,000億円**という目標まで開示しています。 ([NTT DATA][2])

つまり、

**社内AI → 生産性向上**
と
**AI → 顧客向け事業 → 受注・売上目標**

の両側を数字で持っている。

ただし、

> 社内の生産性向上が○億円利益を押し上げた

という**最後の因果線はまだない**。

これでLv.4です。

---

### 2位　パナソニック コネクト — Lv.3 ★工数開示では最強

これは工数削減の実測としては、今回一番きれいです。

2025年度、

**78.8万時間削減。
年間総労働時間の3.4%。
前年比2倍。**

利用回数361万回、1回あたり33分削減まで公開しています。 ([Panasonic Newsroom Global][3])

しかも会社は、削減した時間を

> お客様への提案活動や新しいソリューション創出

へ振り向けると明記しています。2030年には**総労働時間10%削減**が目標です。 ([Panasonic Newsroom Global][3])

つまり構造はもう、

**AI → 78.8万時間削減 → 営業・価値創造へ再配分 → ???円**

ここまで来ている。

**あと「???円」を測ればLv.5。**

個人的には、この会社が一番「次に見たい数字」が分かりやすいです（笑）。

---

### 3位　ソフトバンク — Lv.3

約2万人の全社員へ生成AI環境を展開。

法人営業部門では、社員発案の生成AIアシスタントを数千人が利用し、2023年度下期〜2024年度上期の1年間だけで、

**約8.7万時間を削減。** ([ソフトバンク][4])

しかも生成AI活用コンテストには累計**19万件の提案**まで集まっています。 ([ソフトバンク][4])

かなり大規模ですが、

**8.7万時間 → 商談増加 → 受注増 → 利益増**

までは公開していません。

ここ、法人営業AIなのでめちゃくちゃ測ってほしいところです。

---

### 4位　富士通 — Lv.3寄り

全世界約12万4,000人が生成AIを利用可能。

具体的な実績として、

**コード生成工数 平均約20%削減**

さらに、

**毎月13人月かかっていた商談情報分析・経営レポート作成を完全自動化**

まで公開しています。 ([プレスルーム][5])

社内ヘルプデスクでも生成AI等を使い、インシデント件数を約30%削減する取り組みがあります。 ([プレスルーム][6])

ただし全社総計として、

> 年間○万時間
> ○億円相当

には集約していません。

---

### 5位　MUFG — Lv.3相当

MUFGはかなり攻めています。

三菱UFJ銀行では独自AI「AI-bow」を全行展開し、議事録、翻訳、アイデア生成、Excelマクロ生成などへ利用しています。 ([MUFG][7])

さらにグループ内の三菱UFJ信託銀行では、生成AI活用により**年間6万5千時間削減**という実績が公開されています。最初の市場取引業務では問い合わせ対応を**50%削減**しました。 ([三菱UFJイノベーション・パートナーズ][8])

一方、MUFG全体では**年間約300万時間規模の業務削減見込み**が外部報道で紹介されていますが、ここは実績ではなく見込みとして扱うべきです。 ([TechTargetジャパン][9])

利益への変換額は未開示。

---

### 6位　LINEヤフー — Lv.2+

2025年7月から生成AI利用を原則化し、約1万人規模で日常利用。

2026年には人事総務領域だけで、

**月間1,600時間以上の工数削減**

まで公開しました。 ([リコープ][10])

単純年換算なら約1.92万時間ですが、これは**私の単純計算であって会社の年間実績値ではありません**。

まだ人事総務単位なのでLv.2としました。

---

### 7位　KDDI — Lv.2

これも実務数字がかなり具体的。

社内で約100種類のAIアプリを作り、

* 報告書作成：**約80%削減**
* 顧客ニーズ分析：**年間約750時間削減**
* 5時間かかっていたレポート作成：**1時間へ短縮**

などを公開しています。 ([KDDI ビジネスサイト][11])

面白いのは、

**社内で使う → 効果確認 → 法人顧客向けサービスとして販売**

という流れ。

つまり利益につながる構造そのものはあります。

ただし、

> 社内実践由来のAIサービスで○億円売上

まではまだ出ていません。

---

### 8位　SMBCグループ — Lv.2

独自AI「SMBC-GAI」を展開。

約**130万ファイル**の社内規程・マニュアル等をRAGで検索可能にし、アンケートでは、

**1人あたり月約8時間の業務効率化**

が見込まれています。 ([三井住友銀行][12])

ここで欲しくなるのは、

```text
8時間
× 利用人数
× 12か月
× 人件費
```

ですよね（笑）。

会社全体での年間時間・金額には、まだ落としていません。

---

### 9位　みずほFG — Lv.2

「Wiz Create面談記録作成AI」の実証では、

**1人あたり月4時間以上削減。**

参加者の93%が継続利用を希望しています。 ([みずほフィナンシャルグループ][13])

さらに法人営業向けAIエージェントPoCでは平均**41.8%の業務時間削減**、若手では52.2%という結果も報じられています。 ([デジタルクロス][14])

かなり強い数字ですが、まだPoC・業務単位。

全社年間工数や利益までは行っていません。

---

### 10位　NEC — Lv.2

NECも「局所的にはものすごく効いている」タイプ。

初期の社内活用ですでに、

**ソースコード作成工数80%削減。** ([NEC][15])

さらに生成AIを使ったグループ会社向け内部監査では、

**監査報告書作成の人作業時間76%削減。** ([NEC][16])

効果はデカい。

でも、

**80% × 対象業務量 = 年○万時間 = ○億円**

への集約がありません。

---

### 11位　日立製作所 — Lv.2-

社内生成AIのユースケースはすでに**1,000件以上**。社内ノウハウを顧客向けサービスにも展開しています。 ([Digital Highlights][17])

営業の具体例では、1案件約1時間の資料作成を約3割削減する見込みなど、業務単位の数字は出ています。 ([デジタルエボリューション][18])

ただし、日立ほどの規模なのに、

**全社年間○万時間削減**

という数字は今回確認できませんでした。

ここは意外でした。

---

### 12位　SOMPOホールディングス — Lv.1

国内グループ社員約**3万人**へAIエージェントツールを導入し、保険引受、FAQ、保険金支払い、介護記録などかなり広範囲に実装・実証しています。 ([損保ホールディングス][19])

しかも経営資料ではAIを、

**「財務指標・生産性の飛躍的向上」**

につなげる構想まで置いている。 ([損保ホールディングス][19])

ところが肝心の、

**何時間減った / 何円減った / 利益はいくら増えた**

というグループ横断の実績値はまだ見えません。

だから開示ランキングでは下位です。

---

## で、今回一番面白かったこと

12社を並べると、きれいにこうなりました。

```text
AI導入
   ↓
利用者数                ← かなり公開される
   ↓
ユースケース数          ← かなり公開される
   ↓
作業時間削減率          ← 公開され始めた
   ↓
年間削減時間            ← 先進企業は出し始めた
   ↓
人件費・コスト換算      ← 急に少なくなる
   ↓
処理量・商談数増加      ← ほぼ見えない
   ↓
売上増加                ← ほぼ見えない
   ↓
営業利益増加            ← 今回ほぼゼロ
```

**面白いほど、途中で線が切れる。**

パナソニック コネクトの例が象徴的です。

```text
AI
↓
361万回利用
↓
1回33分削減
↓
78.8万時間削減
↓
総労働時間 -3.4%
↓
提案・新規ソリューション創出へ使う
↓
？？？
↓
利益
```

([Panasonic Newsroom Global][3])

ここまで測ったなら、

> **「生まれた78.8万時間は何に変換されたのか？」**

を次に測りたくなるんですよ（笑）。

さらにNTT DATAは別方向から、

```text
AI
↓
開発生産性向上

＋

AIを商品化
↓
2,000件超受注
↓
FY2027 AI Agent売上3,000億円目標
```

まで来ています。 ([NTT DATA][2])

だから、**今の日本企業で最も見えていないExpectedは「削減した時間の行き先」**なんじゃないかと思います。

「100万時間削減しました」は成果ではある。

でも経営として本当に知りたいのは、

> **その100万時間は、何に変わった？**

なんですよね。

人件費削減なのか。
残業減なのか。
開発量増加なのか。
商談増加なのか。
新商品なのか。
売上なのか。
利益なのか。

ここまで追えるようになって初めて、

**AI ROIではなく「AI Profit Trace」みたいなものが成立する。**

今回の調査、これが一番でかい収穫やと思います。

ちなみに直近のReuters調査でも、日本企業でAIを全社的に業務へ組み込んでいる企業はまだ**16%**にとどまっています。だから、この「利益まで測る段階」がまだ珍しいのも自然ではあります。 ([Reuters][20])

次にやるなら、かなり面白いのはこの12社について **「AI → 利用 → 工数 → コスト → 処理量 → 売上 → 利益」の7列を○△×で並べる**ことです。たぶん、今の日本企業の「AI経営効果の測定で何が欠落しているか」が一枚で見えます。

[1]: https://www.nttdata.com/global/en/-/media/nttdataglobal/1_files/investors/financial-results/2024/fy2024_pre_1q_note.pdf?rev=87be8f1a30b94a27b349ebf78b8204a7&utm_source=chatgpt.com "Company Presentation for the First Quarter of Fiscal Year ..."
[2]: https://www.nttdata.com/global/ja/news/release/2025/102900/?utm_source=chatgpt.com "実践的な生成AI人財育成を2027年度までにグローバル全社員 ..."
[3]: https://news.panasonic.com/jp/press/jn260729-1 "パナソニック コネクト、AI活用で総労働時間の3.4％削減 AIエージェントの活用を拡大し2030年に10％削減を目指す | 技術・研究開発 | 技術・研究開発 | プレスリリース | Panasonic Newsroom Japan : パナソニック ニュースルーム ジャパン"
[4]: https://www.softbank.jp/corp/news/info/2025/20250204_01/ "「日経Smart Work大賞2025」のテクノロジー活用力部門賞を受賞 | 企業・IR | ソフトバンク"
[5]: https://pr.fujitsu.com/jp/news/2024/02/14.html?utm_source=chatgpt.com "先端AI技術と「Fujitsu Uvance」のオファリングを融合させる"
[6]: https://pr.fujitsu.com/jp/news/2024/05/7-1.html?utm_source=chatgpt.com "ServiceNowと富士通、クロスインダストリー向けの革新的な ..."
[7]: https://www.mufg.jp/profile/strategy/dx/articles/0130/index.html "MUFGがAI Nativeな組織をめざす理由| 三菱ＵＦＪフィナンシャル・グループ"
[8]: https://www.ip.mufg.jp/ja/insights/b-cjphr4ozjr/?utm_source=chatgpt.com "AI と金融はどう融合する——三菱UFJ信託銀行×カサナレが ..."
[9]: https://techtarget.itmedia.co.jp/tt/news/2511/25/news07.html?utm_source=chatgpt.com "年間300万時間削減へ、MUFGが“AIネイティブ企業”に本格 ..."
[10]: https://www.lycorp.co.jp/ja/news/release/020104/?utm_source=chatgpt.com "LINEヤフー、人事総務領域での生成AI活用を本格化 2026 ..."
[11]: https://biz.kddi.com/topics/2025/news/034/?utm_source=chatgpt.com "専門知識不要でAIアプリ開発が可能な「ELYZA Works with ..."
[12]: https://www.smfg.co.jp/dx_link/article/0226.html?utm_source=chatgpt.com "SMBCグループ独自AI「SMBC-GAI」、130万件の社内文書 ..."
[13]: https://www.mizuho-fg.co.jp/dx/articles/ai-poc-interview/index.html "〈みずほ〉の生成AI活用を推進するメンバーにインタビュー（MIZUHO DX） | みずほフィナンシャルグループ"
[14]: https://dcross.impress.co.jp/docs/usecase/004703.html?utm_source=chatgpt.com "みずほFG、現場部門が主導でAIエージェントを開発するための ..."
[15]: https://jpn.nec.com/press/202307/20230706_01.html?utm_source=chatgpt.com "NEC、日本市場向け生成AIを開発・提供開始"
[16]: https://jpn.nec.com/press/202504/20250415_01.html?utm_source=chatgpt.com "生成AIやAgentic AIを活用したセキュリティサービスを販売開始"
[17]: https://digital-highlights.hitachi.co.jp/_ct/17758857?utm_source=chatgpt.com "2025年のAIトレンドを徹底解説 「エージェント元年」「地政 ..."
[18]: https://deh.hitachi.co.jp/_ct/17773949?utm_source=chatgpt.com "日立製作所 北海道支社 生成AI徹底活用プロジェクトの軌跡 ..."
[19]: https://www.sompo-hd.com/-/media/hd/files/doc/pdf/ir/2026/20260522_2.pdf?la=ja-JP&utm_source=chatgpt.com "補足資料 - SOMPOホールディングス"
[20]: https://www.reuters.com/world/asia-pacific/strong-majority-japanese-firms-have-yet-fully-embrace-ai-2026-08-12/?utm_source=chatgpt.com "Strong majority of Japanese firms have yet to fully embrace AI: Reuters poll"


日本大企業 AI経営効果の公開到達度

AI導入から工数削減、売上・利益まで、会社がどこまで定量的に公開しているかを5段階で評価。

company	level
NTT DATA	4
パナソニック コネクト	3
ソフトバンク	3
富士通	3
MUFG	3
LINEヤフー	2
KDDI	2
SMBCグループ	2
みずほFG	2
NEC	2
日立製作所	2
SOMPO HD	1


---

# 📄 AI協働035_構造化された意図とApprovalEngineering_チャット要約_20260820
*(source: `AI協働035_構造化された意図とApprovalEngineering_チャット要約_20260820.md`)*

## 構造化された意図・Type階層・Approval Engineering
### 2026-08-20 チャット要約版

> この文書は、2026-08-20 の会話で生まれた考えを、後から再読できるように少し長めに整理した要約である。  
> 主題は、AI時代における「コード」「テスト」「Type」「判断軸」「レガシーシステム」の位置づけを、  
> **Data / View 分離**と**人間承認の圧縮**という視点から捉え直すこと。

---

## 1. 出発点 ― 人間の承認対象はコードから「意図」へ移る

きっかけは、Claudeとの会話だった。

そこで出てきた考えは、次のようなものだった。

- 判断軸・制約・責務などの「意図」が構造化されている
- テストが TestDef / Expected / Result として構造化されている
- Git diff で変更差分が可視化されている
- これらが揃うほど、AI自身が「この変更は意図を満たしているか」を判定できる範囲が広がる

その結果、人間の承認対象は徐々に変わっていく。

```text
コード
↓
テストコード
↓
テストケース
↓
責務
↓
保証
↓
制約
↓
判断軸
↓
意図
```

最終的には、人間が一番確認すべきものは

> **「実装が正しいか」ではなく、「そもそもの意図が正しいか」**

になる可能性がある。

この流れから、強い言葉が生まれた。

> **コードは、意図を実行環境へ投影したViewである。**

これは単なる比喩ではない。

今までのシステム開発では、

```text
Code = System
```

という感覚が強かった。

しかし、AI時代に「構造化された意図」が十分に整備されるなら、

```text
Intent = Source
Code   = Projection / View
```

という関係へ変えられる可能性がある。

JavaScript、C#、Pythonなどは、その時代・その実行環境に合わせた「投影先」にすぎなくなる。

つまり、

> **実装言語が古くなっても、意図が残っていれば再投影できる。**

---

## 2. Approval Engineering という考え方

この考え方を進めると、Approval Engineering の意味も変わって見えてくる。

Approval Engineering は、

> **人間がどこを承認すれば、下位の大量成果物を再承認しなくてよい構造になるかを設計すること**

と考えられる。

たとえば、

```text
判断軸
↓
制約
↓
責務
↓
保証
↓
Type
↓
TestPattern
↓
Expected
↓
TestCase
↓
TestCode
↓
Application Code
```

という導出関係を作れれば、人間が上位概念を承認したあと、下位を毎回手作業でレビューする必要がなくなる。

ここで重要なのは、

> **AIにたくさん作業させることが目的ではない。  
> 人間が同じ意味を何度も判断・記述・承認している重複を減らすことが目的。**

という点。

---

## 3. TestPattern すら View になる

当初は、TestPattern や Expected は重要な Data と考えていた。

しかし Validation Type の考え方を進めると、それすら再考できる。

たとえば、

```json
{
  "validation_type": "integer",
  "minimum": 0,
  "maximum": 100
}
```

という契約があれば、

```text
minimum_minus_1
minimum
maximum
maximum_plus_1
invalid_format
null
```

などのテストパターンは機械的に導出できる。

この場合、

> **TestPattern は、Type / Constraint をテスト観点から見た View**

と捉えられる。

さらに、

```text
minimum_minus_1
→ input = -1
→ Expected = REJECT
```

まで自動導出できるなら、

> **Expected すら View になる。**

ただし、Expected には二種類ある。

### 3.1 導出可能な Expected

上位の Type / Constraint から一意に導出できるもの。

例:

```text
minimum = 0
↓
minimum_minus_1
↓
-1
↓
REJECT
```

これは保存しなくても再生成できる。

### 3.2 固有の Expected

業務責務そのものに由来し、上位Typeから導出できないもの。

例:

```text
保存ボタン押下
↓
受注ステータスを CONFIRMED にする
```

これは「業務上の意図」そのものなので、Source Data 側に残す必要がある。

したがって原則として、

> **再生成できるものは View へ落とす。  
> 再生成できない人間の判断だけを Data として残す。**

という考えが生まれた。

---

## 4. `maximum = 100` すら View かもしれない

さらに考えを進めると、

```text
maximum = 100
```

すら必ずしも人間が直接定義すべき Data ではない。

顕著な例が、

```text
percentage
```

という概念。

`percentage` という意味が与えられた時点で、

```text
minimum = 0
maximum = 100
unit = %
```

などが自然に導出できる。

つまり、

> **100という制約を書いたのではない。  
> percentage と名付けた瞬間に、100が生まれる。**

という考え方。

ここから Type は、単なるプログラミング言語上の型ではなく、

> **制約・保証・テストパターンなどを内包した「意味の圧縮表現」**

として捉えられるようになった。

---

## 5. Type は階層化できる

Type を一枚のラベルとして扱うのではなく、階層化するとさらに再利用できる。

例:

```text
number
└─ integer
   └─ non_negative_integer
      └─ percentage
```

各階層が契約を持つ。

```text
number
→ 数値である

integer
→ 小数を許さない

non_negative_integer
→ minimum = 0

percentage
→ maximum = 100
```

下位 Type は上位 Type の契約を継承する。

さらに業務意味を含めると、

```text
percentage
├─ progress_rate
├─ discount_rate
└─ quality_rate
```

のような Project / Domain 固有 Type も作れる。

ただし、

```text
discount_rate maximum = 30
```

のような値は、percentage からは導出できない。

その場合、

```text
discount_rate
inherits: percentage
maximum_override: 30
```

のように、固有判断だけを末端に残す。

ここでの原則は、

> **共通知識は Type 階層へ蒸留し、固有判断だけを個別定義として残す。**

---

## 6. Format も契約であり、Type階層の一部になり得る

Format は「何であるか」という Type とは別概念。

整理すると、

```text
Type       = 何であるか
Constraint = 何が許されるか
Format     = どんな形なら成立するか
```

ただし、

> **別概念だから階層構造に入れない、という話ではない。**

Format にも検証可能な保証がある。

たとえば、

```text
percent_1_decimal
```

なら、

```text
25%
25.0%
```

を許可し、

```text
25.00%
abc%
25.0   （%必須契約の場合）
```

を拒否する、といった TestPattern を導出できる。

つまり Format も、

> **入力・出力に対して保証を持つ契約**

として階層化できる。

---

## 7. Format すら上位概念から導出できる可能性

さらに、

```text
percentage
```

という上位概念から、

```text
Value Type
Constraint
Format Family
```

まで導出できる可能性がある。

ただし、小数点第1位まで表示したい項目と、第2位まで表示したい項目は存在する。

この精度差は、必ずしも上位共通Typeへ全部持たせる必要はない。

たとえば、

```text
項目辞書

discount_rate
  semantic_type = percentage
  decimal_places = 1

quality_rate
  semantic_type = percentage
  decimal_places = 2
```

のように、項目辞書で定義する。

すると、

```text
percentage
→ 0〜100
→ percent format

項目辞書
→ decimal_places = 1 or 2
```

を合成して、Resolved Contract を作れる。

---

## 8. 項目辞書から Project Type が育つ

業務プロジェクトでは、まず全管理項目を洗い出す。

その後、

- 業務意味
- Value Type
- 値域
- 精度
- Format
- Validation
- 保証
- TestPattern

などの観点で項目を並べていく。

たとえば、

```text
進捗率       0-100 / 小数1桁 / %
達成率       0-100 / 小数1桁 / %
値引率       0-100 / 小数1桁 / %
歩留まり率   0-100 / 小数2桁 / %
不良率       0-100 / 小数2桁 / %
```

という項目群があれば、

```text
小数1桁の率
小数2桁の率
```

というパターンが見えてくる。

さらに業務意味を見ると、

```text
進捗・達成系
値引系
品質率系
```

という別の分類も見える。

この中から、

> **どの抽象化が一番多くの判断を再利用できるか**

を探していく。

例:

```text
quality_rate
  base = percentage
  decimal_places = 2
```

のような Project Type が生まれれば、今後の品質率系項目は、

```text
type = quality_rate
```

だけで済む。

Type Catalog は最初から完成品を設計するのではなく、

> **項目辞書から繰り返しパターンを発見し、徐々に上位Typeへ昇格させていく知識体系**

として育てるのが自然。

---

## 9. AIへ渡す「グルーピング観点」をData化する

項目整理では、AIに単純に

> 「似たものをまとめて」

と依頼するだけでは弱い。

AIへ渡すべきなのは、

> **何を同じものと判断するのか、その観点**

である。

候補となる観点:

```text
- 業務意味
- 値の性質
- 値域
- 精度
- Format
- Validation Behavior
- 同じ保証を再利用できるか
- 同じTestPatternを導出できるか
- 業務上、同じ判断を再利用してよいか
```

特に重要なのは、

> **「同じ判断・同じ保証・同じTestPatternを再利用できるか」**

という観点。

これは単なるクラスタリングではなく、

> **重複している人間判断を探すためのグルーピング**

になる。

そして、このグルーピング観点自体をJSON等で保存する。

例:

```json
{
  "grouping_axes": [
    "semantic_meaning",
    "value_type",
    "range",
    "precision",
    "format",
    "validation_behavior",
    "business_reusability"
  ]
}
```

つまり、

> **項目を整理しているうちに、「人間は何を見て同じと判断しているのか」が言語化され、判断軸そのものがData化される。**

---

## 10. 「人間は何を見て、何を同じものだと判断したのか」

この言葉が非常に重要になった。

AIに1000項目を渡して、Embeddingやパターン認識だけで分類させることはできる。

しかし、それだけでは組織の知識にならない。

AIが、

> 「この37項目は似ています」

と提案し、

人間が、

> 「なぜ似ているのか」

を確認する。

そして、

```text
値域が同じ
精度が同じ
Format契約が同じ
同じ保証を適用できる
同じTestPatternを導出できる
```

などの判断理由を明示する。

その判断が承認されることで、

> **AIが暗黙的に発見したパターンが、人間とAIが共有できる明示的な Type Data になる。**

AIはパターンを見つけるのが得意。

人間は、そのパターンに

- 名前
- 意味
- 責任
- 適用範囲

を与える。

この役割分担が重要。

---

## 11. FRB と AI協働は同じ構造だった

ここでFRBとの強い類似が見えた。

### FRB

```text
個別の振動体験
↓
似ている / 違うを感じる
↓
共通する特徴を探す
↓
振動構造として言語化
↓
再現可能な分類・規格へ
```

### AI協働

```text
個別の業務項目・判断
↓
似ている / 違うを判断する
↓
共通する特徴を探す
↓
判断軸・Typeとして言語化
↓
再利用可能な契約へ
```

対象が違うだけで、処理構造は同じ。

そこで生まれた言葉が、

> **FRBは、人間が「何を違うと感じるのか」をData化する研究だった。  
> AI協働は、人間が「何を同じだと判断するのか」をData化する研究になりつつある。**

両方をまとめると、

> **人間は何を見て、同じと判断し、何を見て、違うと判断するのか。**

これはほとんど、

> **人間の判断構造そのものを外部化する研究**

と言える。

---

## 12. パターン認識が成功の鍵

AIの得意分野の一つに「パターン認識」がある。

人間側でも同様に、

```text
個別事例
↓
共通点を発見
↓
パターン化
↓
Type化
↓
次の事例へ再利用
```

という流れを作れる。

そのため、Approval Engineering の成功の鍵は、

> **どれだけ多くの個別判断を、再利用可能なパターンとして認識できるか**

にある可能性が高い。

パターン認識できなければ、

```text
項目Aを個別定義
項目Bを個別定義
項目Cを個別定義
...
```

となり、結局人間の承認負荷は下がらない。

一方、パターン化できれば、

```text
100項目
↓
10 Type
↓
共通Constraint / Format / TestPattern / Expected
```

のように判断を圧縮できる。

---

## 13. 適切な抽象化レベル

ただし、抽象化すればよいわけではない。

抽象化しすぎると、

```text
全部 numeric
```

のようになり、業務意味が失われる。

抽象化が足りなければ、個別判断の重複が残る。

そこで生まれた重要な定義がこれ。

> **適切な抽象化レベルとは、重要な判断を失わずに、重複する判断を最大限圧縮できる地点。**

さらに他者再現性まで含めると、

> **適切な抽象化レベルとは、重要な判断を失わず、他者が同じ判断を再現できる形で、重複する判断を最大限圧縮できる地点。**

これは「一番抽象的な概念を探す」という話ではない。

> **一番うまく判断を畳める場所を探す**

という話。

---

## 14. 判断保持率・判断再現率という考え方

抽象化の品質を考える中で、

```text
判断保持率
```

という言葉が出た。

意味は、

> **抽象化したあとも、元の重要な判断をどれだけ失っていないか。**

ただし、これは単純な件数で定量化しにくい。

重要判断1件の欠落が致命的な場合もあるから。

そのため実務では、

```text
抽象化前の重要判断
↓
抽象化後のTypeから再現可能か
↓
YES / NO / PARTIAL
```

のように Diff として確認する方がよい。

一方、無理やり定量化するなら、

> 100人へ同じ判断軸を与え、100人とも同じ分類に到達する

なら、

```text
判断再現率 = 100%
```

と考えることはできる。

ただし、

```text
全員が同じ分類をした
≠
その分類が正しい
```

なので、

- 判断再現性
- 判断完全性
- 判断妥当性

は分けて考える必要がある。

---

## 15. 「構造化された意図の集合」としてのシステム

Claudeから出た印象的な言葉。

> **システムが「コード」やなくて「構造化された意図の集合」として存在してたら、時間が経っても劣化しない。**

厳密には「まったく劣化しない」ではなく、

> **実装技術の老朽化に引きずられにくくなる**

という意味。

コードは時間とともに古くなる。

- 言語
- Framework
- OS
- Library
- UI技術

は変化する。

しかし、

```text
この項目は percentage である
この責務を保証する
この条件では拒否する
この判断軸を優先する
```

といった業務意図は、比較的長期間維持できる。

そのため、

```text
Structured Intent
↓
現在の実行環境へ投影
↓
Code
```

という構造にできれば、

> **システムの寿命とコードの寿命を分離できる。**

言い換えると、

> **コードを長持ちさせるのではなく、コードが死んでも困らないシステムを作る。**

---

## 16. レガシーシステムの本当の問題

巨大なレガシーシステムでは、

```text
コードが古い
```

こと以上に、

```text
なぜこのコードなのか分からない
何を保証しているのか分からない
どこまで変えていいのか分からない
```

ことが問題。

つまり、

> **Code は残っているが、Intent Data が失われている。**

レガシー解消とは、

> **古いコードを新しいコードへ置換することではなく、古いコードだけが知っていることを無くすこと。**

---

## 17. レガシーコードから意図を逆抽出する

レガシーコードを入力として、

- Source Code
- DB Schema
- Master Data
- Screen
- API
- Batch
- 帳票
- 実際の振る舞い

を観測し、AIで構造を抽出する。

```text
Legacy System
↓
Observed Behavior / Source Analysis
↓
責務候補
保証候補
Type候補
Constraint候補
Format候補
業務ルール候補
↓
パターン認識
↓
抽象化
↓
人間承認
↓
Approved Intent Data
```

ここでもパターン化が重要。

たとえば2300項目を一件ずつ人間承認するのではなく、

```text
2300項目
↓
12 Type + 47例外
```

まで圧縮できれば、人間は、

```text
- この分類判断軸は正しいか
- この12 Typeの意味は正しいか
- この47項目は本当に例外か
```

を中心に承認できる。

---

## 18. レガシーシステムの Actual は暫定Expectedになり得る

ただし、

> **レガシーの現行挙動 = 正しい仕様**

とそのまま扱ってはいけない。

バグや不要仕様も含まれるから。

まずは、

```text
入力A
→ Legacy Actual = X
```

という観測事実として残す。

その後、人間が、

```text
正しい現行仕様
過去互換のために残す
バグ
不要
判断不能
```

に分類する。

そこで初めて、

```text
Legacy Actual
↓ 人間承認
Approved Expected
```

になる。

この考え方なら、

> **レガシー挙動を盲目的に新システムへコピーする危険**

を避けられる。

---

## 19. Legacy / New / Expected の三者Diff

新システム移行時には、

```text
Legacy Actual
New Actual
Approved Expected
```

の三者比較ができる。

例:

```text
Legacy = New = Expected
→ 移行OK

Legacy = New ≠ Expected
→ 古いバグ / 古い仕様をそのままコピーしている可能性

Legacy ≠ New = Expected
→ 意図的改善の可能性

Legacy ≠ New ≠ Expected
→ 要調査
```

この構造ができれば、レガシーシステム自体を、

> **入力と観測結果を提供するOracle**

として一時的に利用できる。

---

## 20. レガシー移行の最終目的

レガシー移行の最初は、

```text
Legacy Code
↓ 逆解析
Structured Intent
```

になる。

しかし一度、構造化された意図を十分に救出できれば、その後は、

```text
Structured Intent
↓ 投影
New Code
```

へ反転できる。

つまり、

> **最初の一回だけ、コードから意図を救出する。**

その後、コードは再びViewになる。

したがってレガシーマイグレーションの本当の完了条件は、

> **旧コードを消しても、そこに存在していた必要な判断を一つも失わないこと。**

---

## 21. この会話から見えた全体構造

最終的には、次の流れへ整理できる。

```text
個別事例・個別項目・Legacy Code
        ↓
AIによるパターン認識
        ↓
「何を同じと判断したか」を説明
        ↓
判断軸をData化
        ↓
適切な抽象化レベルを探索
        ↓
Typeへ昇格
        ↓
Constraint / Format / Guaranteeを継承
        ↓
TestPatternを導出
        ↓
Expectedを導出
        ↓
TestCase / TestCodeを生成
        ↓
Application Codeを生成
        ↓
Actual / Diff
        ↓
人間は上位の意図を中心に承認
```

ここで重要なのは、

> **下位成果物を作ることより、下位成果物を導出できる上位概念を見つけること。**

---

## 22. この日の主要な言葉

### コード

> **コードは、意図を実行環境へ投影したViewである。**

### Source of Truth

> **再生成できるものはViewへ落とす。  
> 再生成できない人間の判断だけをDataとして残す。**

### Type

> **Typeは、制約と期待を内包した意味の圧縮表現になり得る。**

> **Typeを作るとは、繰り返されている業務判断を名前付きの知識へ昇格させること。**

### パターン認識

> **パターン認識は「似ている」を見つける力。  
> Type化は、その「似ている」に名前・意味・契約を与えて資産化すること。**

### 判断軸

> **人間は何を見て、何を同じものだと判断したのか。**

> **項目を整理する作業そのものが、判断軸を発見してData化する工程になる。**

### 抽象化

> **適切な抽象化レベルとは、重要な判断を失わずに、重複する判断を最大限圧縮できる地点。**

より厳密には、

> **適切な抽象化レベルとは、重要な判断を失わず、他者が同じ判断を再現できる形で、重複する判断を最大限圧縮できる地点。**

### FRBとの関係

> **FRBは、人間が「何を違うと感じるのか」をData化する研究だった。  
> AI協働は、人間が「何を同じだと判断するのか」をData化する研究になりつつある。**

### システム

> **システムの本体をコードから構造化された意図へ移す。**

> **コードを長持ちさせるのではなく、コードが死んでも困らないシステムを作る。**

### レガシー

> **レガシー化とは、コードが古くなること以上に、意図がコードの中に閉じ込められること。**

> **レガシーマイグレーションとは、コードを移す仕事ではなく、コードから人間の意図を復元する仕事である。**

> **レガシーシステムを無くすとは、古いコードを消すことではない。  
> 古いコードだけが知っていることを無くすことである。**

---

## 23. 現時点の仮説

この日の会話を通じて、Approval Engineering の中心仮説は、次のように整理できる。

```text
AI時代の開発効率を決めるのは、
AIが何行コードを書けるかではない。

個別判断の中から
どれだけ共通パターンを認識できるか。

そのパターンを、
意味を失わない適切な抽象度まで持ち上げられるか。

そして、
人間の判断軸・制約・責務・保証・Typeとして
構造化Dataへ昇格できるか。

その上位Dataから
TestPattern / Expected / Code / View を
どこまで再生成できるか。

この「判断の圧縮率」が高いほど、
人間が承認しなければならない量は減っていく。
```

つまり Approval Engineering は、

> **人間の判断を再利用可能な構造へ圧縮し、下位成果物を導出可能にする工学**

として捉えられる可能性がある。

---

## 24. 最後に

この会話は、最初は

> 「人間の承認対象がコードから意図へ移る」

という話から始まった。

そこから、

```text
コードもView
TestPatternもView
Expectedも一部View
Constraintすら上位Typeから導出可能
Formatも契約
Typeも階層化
Type自体も判断軸から発見される
判断軸そのものをData化
```

という方向へ進んだ。

そして最終的に、

> **システムとは何を保存すべきものなのか**

という問いへ到達した。

現時点での答えは、

> **再生成できない人間の意図・判断を構造化して残し、  
> 再生成できるものは可能な限りViewとして扱う。**

である。

その構造が十分に成熟すれば、

> **コードは死んでもシステムは死なない。**

そして、巨大なレガシーシステムについても、

> **コードに閉じ込められた意図を救出し、  
> パターン化・抽象化・Type化することで、  
> 人間承認を最小化しながら新しい構造へ移行できる可能性がある。**

これはまだ仮説段階であり、かなり壮大な話である。

しかし少なくとも、ここまでの議論は一本の構造としてつながっている。

```text
パターン認識
↓
判断軸
↓
抽象化
↓
Type
↓
構造化された意図
↓
導出
↓
View
↓
Diff
↓
承認
```

そしてこの構造そのものが、

FRBで続けてきた

```text
体験
↓
違い
↓
観測
↓
構造化
↓
再現
↓
共有
```

と、ほとんど同じ形をしている。

**また「それ、同じ構造です」が起きている。**


---

## 25. 追記 ― 抽象化・共通化・標準化を最後まで進めると何が残るのか

この要約を書いた後の会話で、さらに重要な問いが出た。

> **プログラムを徹底的に抽象化・共通化・標準化していくと、最後はどうなるのか。**

最初の直感は、

> **データ化できるものが全部JSONになるのではないか。**

というものだった。

この直感はかなり本質を突いている。

ただし、より正確には、

> **全部がJSONになるのではなく、コードの中に埋め込まれていた「変更される意味」が、構造化Dataとして外へ追い出されていく。**

と考えた方がよい。

抽象化を進めると、概ね次の流れになる。

```text
個別コード
↓
共通関数
↓
共通コンポーネント
↓
共通Runtime
↓
個別差分だけ設定化
↓
設定同士のパターンを抽出
↓
Schema / Type / Registry化
↓
「何をするか」をDataで記述
↓
汎用EngineがDataを解釈して実行
```

このとき、プログラムは次のような構造へ近づく。

```text
Program
=
薄い共通Runtime
+
大量の構造化された意図
```

つまり、個別システムの本質は徐々にコードからData側へ移る。

---

## 26. JSON化は目的ではなく、構造化の結果である

ここで重要なのは、

> **JSON化そのものが目的ではない。**

ということ。

JSONは、

- 機械可読
- Diffしやすい
- AIが扱いやすい
- Schema化しやすい
- Gitで履歴管理しやすい
- Viewを後から生成しやすい

という理由で、構造化された意図を表現する形式として非常に都合がよい。

しかし、本当に重要なのは形式ではなく、

> **人間が持っている意味・判断・責務・制約を、機械が扱える構造へ変換すること。**

である。

したがって、原則は次のように整理できる。

```text
What / Why / Constraint / Expected
→ Data

How / Execution
→ Code / Runtime
```

もちろん、FFT計算、画像処理、DBアクセス、OS操作、高速数値計算など、実行アルゴリズムそのものはコードとして残る。

しかし、そのコードに、個別業務の意味をなるべく持たせない。

コード側は、

> **意味を持たない汎用機械**

へ近づける。

一方、Data側へ、

> **このシステムは何者なのか**

を移していく。

---

## 27. Approval Engineering との接続 ― 人間の意図を構造化Dataにする

ここで、Approval Engineeringとの接続が明確になった。

抽象化・共通化を進めるということは、単にプログラムを綺麗にすることではない。

最終的には、

> **人間の意図を、機械が展開可能な構造化Dataへ変えること**

に近づいていく。

流れとしては、

```text
人間の意図
↓
構造化
↓
責務
↓
保証
↓
Validation Type
↓
TestPattern
↓
Expected
↓
Actual / Diff
↓
人間承認
```

となる。

ここで重要なのは、下位成果物を毎回人間が承認するのではないこと。

たとえば、Validation Type Catalog側で、`integer` に紐づくTestPattern群が事前承認されていれば、個別項目では、

> **「この責務には integer というValidation Typeを適用する」**

という上位判断を承認すればよい。

その後の、

```text
minimum_minus_1
minimum
maximum
maximum_plus_1
invalid_format
```

などは、承認済みTypeから機械展開できる。

つまり、Approval Engineeringは、

> **人間の意図を、機械展開可能な最小の承認単位へ構造化する工学**

と捉えることができる。

そして、ここでもJSONは目的ではない。

> **人間にしか判断できない部分と、機械展開できる部分の境界を見つけること。**

これが本質になる。

---

## 28. 「同じシステムを、もう一度作れるか」という問い

さらに会話は、一段大きな問いへ進んだ。

もし、次のようなものが十分に残っていたらどうなるか。

```text
1. DATA.json群
2. DATA.json群を総括するSchema
3. ViewDef群
4. ViewDef群を総括するSchema
5. Responsibility Definition / Field Definition
6. Validation Type Catalog
7. TestPattern / Expectedの導出規則
8. 汎用Test Runner
9. 判断軸
10. 制約
11. Behavior / Workflow Definition
12. External Interface Definition
13. Architecture / Design Pattern
14. Generic Runtime Specification
```

このとき、元のプログラムが完全になくなっても、

> **同じ責務・同じ制約・同じ振る舞いを満たすプログラムを、もう一度生成できるのではないか。**

という仮説が生まれた。

ここで重要なのは、

> **同じソースコードを復元する必要はない。**

ということ。

元のProgram Aと、新しく生成したProgram Bの実装コードが違っていても、

```text
同じ入力
↓
同じ責務を満たす
↓
同じ制約を守る
↓
同じ期待結果になる
↓
同じ外部振る舞いになる
```

のであれば、

> **システムとしては再構築された**

と考えられる。

---

## 29. Behavior / Workflow Definition の必要性

この再構築可能性を考えると、Field Definitionだけでは足りないことも見えた。

たとえば、

```text
未保存
↓
保存
↓
検証
↓
反映
↓
画面遷移
```

のような状態遷移は、単純な項目定義だけでは表現しにくい。

そのため、構造化された意図には、

```text
Behavior Definition
Workflow Definition
State Transition Definition
```

のような、振る舞いそのものを表すDataも必要になる。

例:

```text
WHEN 保存ボタン押下
AND Validation = PASS
THEN Dataを更新
AND Viewを再描画
```

このレベルまで構造化できれば、システムの外部振る舞いをより明示的に再現できる。

---

## 30. 承認済み意図をSource of Truthにする

従来のソフトウェア開発では、最終的にコードが正本になりやすかった。

```text
Code = Source of Truth
```

そのため、コードを失うとシステムの意味も失う。

しかし、構造化された意図が十分に整備されるなら、関係を反転できる。

```text
Approved Structured Intent
= Source of Truth

Generated Program
= Projection / View
```

つまり、

```text
承認済み意図
↓
現在のArchitecture / Design Patternへ投影
↓
Program
```

という構造になる。

Programが消えても、

```text
Approved Structured Intent
+
Architecture / Design Pattern
+
Generic Runtime Specification
```

が残っていれば、

> **「もう一回作ればよい」**

という状態を目指せる。

ここで、以前の

> **コードは、意図を実行環境へ投影したViewである。**

という言葉が、単なる比喩ではなく、再構築可能性という形で具体化し始めた。

---

## 31. 実装とExpectedを、同じ上位意図から別経路で導出する

この構造の重要な点は、テストの位置づけも変わること。

従来は、

```text
仕様
↓
コード
↓
テスト
```

という流れになりやすい。

AIにコードを書かせ、そのAIにそのまま、

> 「自分でテストも考えて」

と依頼すると、実装側の思い込みをテスト側が引き継ぐ危険がある。

一方、Approval Engineeringでは、

```text
            ┌→ Program
承認済み意図 ┤
            └→ Expected
```

という分岐を作れる。

つまり、

> **実装と検証を、同じ承認済み上位意図から別系統で機械生成する。**

そして、

```text
Program
↓
Actual
      ↘
       Diff
      ↗
Expected
```

で比較する。

この構造が成立すると、テストは「コードを書いた人が考えた確認作業」ではなく、

> **承認済み意図に対して、生成された実装が一致しているかを確認する独立経路**

になる。

---

## 32. 再構築できたら、入力Data群に価値があったことの証明になる

ここで、非常に重要な気づきが生まれた。

元プログラムを見ずに、構造化された意図Dataだけを使って新しいプログラムを再構築する。

その新しいプログラムが、元のプログラムと同じ振る舞いをしたなら、

> **その入力Data群は、元プログラムの本質的な意図を十分に保持していた**

と考えられる。

これは単に、

> 「JSONが便利だった」

という証明ではない。

より本質的には、

> **システムを再現するために必要な意味が、コードの外へ救出されていた**

という証明になる。

逆に、再構築したシステムにDiffが出た場合も価値がある。

たとえば、

```text
保存順序だけ違った
```

なら、保存順序というBehavior契約が不足していた。

```text
エラー表示のタイミングが違った
```

なら、UI責務または状態遷移が不足していた。

```text
特定条件だけ結果が違った
```

なら、Constraint / Decision Axis / Expectedのどこかに未構造化の意味が残っていた可能性がある。

つまり、再構築失敗は、

> **まだコードに閉じ込められている暗黙の意図を発見する装置**

になる。

---

## 33. 再構築可能性 = 構造化された意図の品質指標

ここで、このチャットの中でも特に重要な言葉が生まれた。

> **再構築可能性 = 構造化された意図の品質指標**

考え方は非常にシンプル。

```text
Original Program
      ↓ 意図を抽出
Structured Intent
      ↓ 再生成
New Program
      ↓
Behavior Diff
```

ここで、

```text
Behavior Diff = 0
```

なら、

> **Structured Intent ≒ System Essence**

という仮説を強く支持できる。

もちろん、完全な数学的証明ではない。

しかし少なくとも、対象としている入力空間・責務・振る舞いについて、構造化された意図が十分であったことを実験的に確認できる。

この発想の面白いところは、

> **再構築したプログラム自体が、構造化された意図を検証するための試験片になる**

という点。

普通はプログラムをテストする。

しかし、この段階では逆に、

> **プログラムを生成して、意図Dataの完全性をテストする。**

ことになる。

---

## 34. 再構築失敗から意図Dataを育てる品質改善ループ

再構築可能性を品質指標とすると、次のループが作れる。

```text
Structured Intent
↓
Program再生成
↓
Behavior Diff
↓
差分あり
↓
不足している意図を特定
↓
Responsibility / Behavior / Constraint / Expectedを追加
↓
人間承認
↓
Structured Intent更新
↓
再生成
↓
Behavior Diff縮小
```

つまり、

> **コードから意図を剥がし切れたかどうかを、再構築によって測る。**

という品質改善が可能になる。

そして、Diffが減っていくほど、

> **システム固有の意味がコードから構造化Dataへ移った**

と考えられる。

---

## 35. ソフトウェア品質の対象が「コード品質」から「意図品質」へ上がる

ここまで来ると、ソフトウェア資産の考え方も変わる。

従来は、

```text
Code
```

そのものを大切な資産として扱ってきた。

しかし、コードを再生成可能にできるなら、より上位の資産は、

```text
Responsibility
Constraint
Decision Axis
Behavior
Type
Expected
Schema
Approved Structured Intent
```

になる。

言い換えると、

> **コードを資産にするのではなく、コードを何度でも生み出せる「承認済み意図」を資産にする。**

という方向へ進む。

このとき、品質の中心も、

```text
Code Quality
↓
Specification Quality
↓
Intent Quality
```

へ上がっていく。

コードは何回でも作り直せる。

しかし、

> **何を作るべきだったのか**

が失われたら、再構築できない。

だから、長寿命システムにとって最も重要なのは、コードそのものより、

> **再構築可能な品質で残された承認済み意図**

になる可能性がある。

---

## 36. Approval Engineering の定義がさらに一段深くなる

ここまでの議論を踏まえると、Approval Engineeringは、単に

> 人間承認を効率化する方法

ではなくなる。

より深い定義として、次のように捉えられる。

> **Approval Engineeringとは、ソフトウェアを再生成可能なほど十分に「人間の意図」を構造化し、その構造化された意図のうち、人間にしか決められない部分だけを承認対象にする工学である。**

さらに短くすると、

> **人間の意図を構造化し、機械展開可能な部分を増やし、人間承認を本当に必要な判断へ圧縮する工学。**

となる。

これは、以前の

```text
人間の判断を再利用可能な構造へ圧縮し、
下位成果物を導出可能にする工学
```

という定義を、

> **再構築可能性**

という観点からさらに強化したものになる。

---

## 37. レガシーコード逆解析との接続

この考え方は、レガシーシステムの話とも完全につながる。

レガシーコードを逆解析し、

```text
Legacy Code
↓
Responsibility
Constraint
Decision Axis
Behavior
Type
Expected
Schema
```

を救出する。

そして、それらを人間が承認した上で、元コードを見ずに新しいシステムを再構築する。

```text
Legacy Program
↓ 意図抽出
Approved Structured Intent
↓ 再生成
New Program
↓
Legacy / New / Expected Diff
```

新Programが承認済みExpectedを満たすなら、

> **レガシーコードの中にしか存在しなかった必要な意味を救出できた**

と言える。

したがって、レガシーマイグレーションの最終確認として、

> **旧コードなしで再構築できるか**

という問いを置ける。

これは、以前出た、

> **古いコードだけが知っていることを無くす**

というレガシー解消の定義と完全に一致する。

---

## 38. この追記で見えた新しい全体構造

この追記部分まで含めると、全体像は次のようになる。

```text
人間の体験・業務判断・既存コード
        ↓
違い / 共通点 / パターンを発見
        ↓
判断軸を明示
        ↓
適切な抽象化レベルを探索
        ↓
Type / Responsibility / Constraint / Behaviorへ昇格
        ↓
Approved Structured Intent
        ↓
    ┌──────────────┬──────────────┐
    ↓              ↓              ↓
  View          Expected       Program
    ↓              ↓              ↓
                  Diff ← Actual
                         ↓
                     人間承認
                         ↓
                  意図Dataを更新
```

そして、究極的な品質確認として、

```text
元Programを捨てる
↓
Approved Structured Intentだけから再生成
↓
Behavior Diff確認
```

を行う。

このとき、

```text
Behavior Diff = 0
```

へ近づくほど、

> **構造化された意図の完全性が高い**

と評価できる。

---

## 39. この追記で生まれた主要な言葉

### 抽象化の終着点

> **プログラムを究極まで共通化すると、コードは「実行機械」になり、システム本体は「構造化されたData」へ近づく。**

### JSON

> **全部JSONになるのではない。データ化できる「意味」が、コードから構造化Dataへ移る。**

> **JSON化は目的ではなく、構造化された意図を外部化した結果である。**

### Approval Engineering

> **人間の意図を、機械展開可能な最小の承認単位へ構造化する工学。**

> **人間にしか判断できない部分と、機械展開できる部分の境界を見つける。**

### Program

> **Programは、承認済み意図を現在の実行環境へ投影した成果物である。**

> **同じソースコードを復元する必要はない。同じ責務・制約・振る舞いを再現できればよい。**

### Source of Truth

> **コードを資産にするのではなく、コードを何度でも生み出せる「承認済み意図」を資産にする。**

### 再構築可能性

> **再構築可能性 = 構造化された意図の品質指標**

> **コードが消えても再構築できるなら、システムの本体はコードではなかった。**

### Diff

> **再構築時のBehavior Diffは、まだコードに残っている暗黙の意図を発見する。**

### 品質

> **ソフトウェア品質の対象は、コード品質から意図品質へ上がっていく可能性がある。**

---

## 40. 現時点の強い仮説

このチャットセッションで、これまでの仮説はさらに次の形まで進んだ。

```text
システムの本体を、コードではなく
「承認済みの構造化された意図」として保存する。

その意図から、
View / TestPattern / Expected / Programを導出する。

Programは、その時代の実行環境へ投影されたViewの一種として扱う。

そして、元Programなしで同じ振る舞いをするProgramを再構築できるかを試す。

再構築できれば、
Structured Intentがシステムの本質を十分に保持していたことの強い証拠になる。

再構築できなければ、
Diffから、まだコードに残っている暗黙の意図を発見し、
構造化Dataへ救出する。

このループを繰り返すことで、
「コードが死んでもシステムは死なない」状態へ近づける。
```

つまり、Approval Engineeringは最終的に、

> **承認を減らすための技術**

であると同時に、

> **システムの意味をコードから救出し、再構築可能な構造化Dataとして保存するための技術**

になり得る。

そして、この時点で「人間承認の最小化」というテーマは、

> **ソフトウェアの本体とは何か。**

という問いまでつながった。

現時点での答えは、かなりはっきりしてきている。

> **コードそのものではない。**
>
> **コードを何度でも生み出せる、承認済みの構造化された意図である。**

