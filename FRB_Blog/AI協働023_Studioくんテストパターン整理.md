うん、66件ぜんぶ仕分けしてみた。かなり見えたわ。笑
Catalogには66 Conditionあり、Registry側では型契約・標準Constraint・Override可能Constraintが定義されているので、それを突き合わせて分類した。 

まず分類は **5種類** にすると綺麗だった。

| 分類               |     件数 | 意味                                                        |
| ---------------- | -----: | --------------------------------------------------------- |
| **DERIVE**       |     16 | Resolved Contractからそのまま機械生成できる                            |
| **TYPE + GUARD** |     18 | 型固有の観点。ただしResolved Contractを見て生成可能なデータを機械選択し、無理ならSUPPRESS |
| **TYPE FIXED**   |     28 | 型そのものの性質を確認する固定テスト                                        |
| **DEPRECATED候補** |      3 | 他のDERIVEテストで十分カバーできる                                      |
| **USAGE SPLIT**  |      1 | Condition自体は必要だが、Validation Typeによって意味が違う                 |
| **合計**           | **66** | 全件仕分け済み                                                   |

### ① DERIVE：16件

これはかなり気持ちいい領域。**人間判断ゼロでいける。**

```text
EMPTY_STRING_POLICY
MINIMUM_LENGTH_BOUNDARY
MAXIMUM_LENGTH_BOUNDARY
MAXIMUM_LINES_BOUNDARY
LENGTH_BOUNDARY

MINIMUM_BOUNDARY
MAXIMUM_BOUNDARY

EXACT_SCALE_ACCEPTED
SCALE_OVER_REJECTED
PRECISION_OVER_REJECTED

MINIMUM_DATE_BOUNDARY
MAXIMUM_DATE_BOUNDARY

MINIMUM_DATETIME_BOUNDARY
MAXIMUM_DATETIME_BOUNDARY

MINIMUM_INSTANT_BOUNDARY
MAXIMUM_INSTANT_BOUNDARY
```

たとえば、

```text
minimum = 100
maximum = 200
```

なら、

```text
100 → ACCEPT
 99 → REJECT

200 → ACCEPT
201 → REJECT
```

を機械生成。

`scale=2` なら、

```text
12.34  → ACCEPT
12.345 → REJECT
```

みたいに生成できる。

ここに今後、さっき発見した **中央値／代表正常値** が加わる感じやね。

---

### ② TYPE + GUARD：18件

ここが今回いちばん面白かった。

```text
STRING_VALUE_ACCEPTED
SINGLE_LINE_ACCEPTED
MULTI_LINE_ACCEPTED
ALPHABET_START_ACCEPTED
UNDERSCORE_START_ACCEPTED
DIGITS_ACCEPTED
LEADING_ZERO_ACCEPTED
ALPHANUMERIC_ACCEPTED

INTEGER_ACCEPTED
DECIMAL_ACCEPTED
NEGATIVE_VALUE_ACCEPTED
ZERO_ACCEPTED
NEGATIVE_INTEGER_ACCEPTED
POSITIVE_INTEGER_ACCEPTED

VALID_DATE_ACCEPTED
VALID_LOCAL_DATETIME_ACCEPTED

UTC_INSTANT_ACCEPTED
OFFSET_INSTANT_ACCEPTED
```

これは**型固有の観点は残す**。

ただし、TestPattern生成時にResolved Contractを見る。

たとえば、

```text
DECIMAL_ACCEPTED
```

という観点があっても、

```text
minimum = 0
maximum = 0
```

だったら、この範囲内には小数のテストデータを作れない。

だから、

```text
DECIMAL_ACCEPTED
        ↓
Resolved Contract確認
        ↓
有効な小数を作れる？
  YES → GENERATE
  NO  → SUPPRESS
```

になる。

ここに**人間判断はいらない**。

これ、以前の `TRANSFORM` の話がいらなくなった理由でもある。

> Conditionは型から決まる。
> 実際のテスト値を作れるかはResolved Contractを見て機械判断する。

で済む。

---

### ③ TYPE FIXED：28件

これはConstraint値から作るんじゃなく、**その型である以上確認したい性質**。

```text
文字列
LINE_BREAK_REJECTED
NON_STRING_REJECTED
DIGIT_START_REJECTED
SPACE_REJECTED
NON_ASCII_REJECTED
ALPHABET_REJECTED
SIGN_REJECTED
DECIMAL_POINT_REJECTED
SYMBOL_REJECTED

数値
NAN_REJECTED
INFINITY_REJECTED
DECIMAL_REJECTED
IMPLICIT_ROUNDING_REJECTED

boolean
TRUE_ACCEPTED
FALSE_ACCEPTED
STRING_TRUE_REJECTED
STRING_FALSE_REJECTED
ONE_REJECTED

日付
LEAP_DAY_VALID_ACCEPTED
INVALID_LEAP_DAY_REJECTED
INVALID_MONTH_REJECTED
INVALID_DAY_REJECTED
DATETIME_VALUE_REJECTED

日時
TIMEZONE_SUFFIX_REJECTED
INVALID_DATE_REJECTED
INVALID_TIME_REJECTED

Instant
TIMEZONE_MISSING_REJECTED
INVALID_OFFSET_REJECTED
```

booleanなんか典型。

```text
true    → ACCEPT
false   → ACCEPT
1       → REJECT
0       → REJECT
"true"  → REJECT
```

これはminimum/maximumからは出ないので型固有。

うるう年も同じ。

```text
2024-02-29 → ACCEPT
2025-02-29 → REJECT
```

ここもStudio標準として固定してしまえば、人間判断はいらない。

---

### ④ DEPRECATED候補：3件

これはかなり強く落としてよさそう。

```text
ONE_ACCEPTED
NEGATIVE_INTEGER_REJECTED
UNSAFE_INTEGER_REJECTED
```

`ONE_ACCEPTED` は、`studio.integer.positive` の標準minimumが1なので、

```text
MINIMUM_BOUNDARY

1 → ACCEPT
0 → REJECT
```

で終わる。Registryにも実際に `minimum=1` が定義されている。

`NEGATIVE_INTEGER_REJECTED` も、

```text
non_negative → minimum = 0
positive     → minimum = 1
```

なのでminimum判定で十分。

そして意外だったのが、

```text
UNSAFE_INTEGER_REJECTED
```

もかなり不要。

Registryのinteger系は安全整数範囲そのものを、

```text
-9007199254740991
～
 9007199254740991
```

というminimum / maximumで既に持っている。

だから、

```text
MAXIMUM_BOUNDARY
9007199254740991 → ACCEPT
9007199254740992 → REJECT
```

で安全整数範囲外もテストできる。

つまり**同じことを別名でテストしている**状態。

これはdeprecated候補にしてよさそう。

---

### ⑤ `ZERO_REJECTED` だけ特殊

これだけはやっぱり変。笑

現在、

```text
ZERO_REJECTED

studio.integer.positive
studio.boolean.standard
```

の両方から使われている。

でも意味は、

```text
integer.positive
0 → minimum=1未満だからREJECT

boolean.standard
0 → numberをbooleanへ暗黙変換しないからREJECT
```

で全然違う。

だから結論は、

```text
ZERO_REJECTED
Catalog → 残す

studio.integer.positive
→ standard_test_conditionsから外す
→ MINIMUM_BOUNDARYへ任せる

studio.boolean.standard
→ 残す
```

が綺麗。

そうすると `ZERO_REJECTED` のカテゴリーも、

```text
複合
↓
boolean
```

へ戻せる。

---

で、今回の全件仕分けをやった結果、**人間が本当に判断しないといけない話がかなり減った。**

現時点で残った大きな判断案件はこのへん。

1. **文字列のUnicode／日本語標準テストをどこまで持つか**

   * ひらがな
   * 漢字
   * 全角／半角
   * 絵文字
   * 結合文字
   * 外字

2. **文字数をgrapheme単位＝人間認識文字数に正式決定するか**

3. **`LENGTH_BOUNDARY` と `MINIMUM_LENGTH_BOUNDARY / MAXIMUM_LENGTH_BOUNDARY` を統一するか**

   * 今ちょっと命名体系が二重になってる。

4. **NaN / Infinityテストをどの層で保証するか**

   * JSON原本ではそもそも通常のJSON値として表現できないので、Runtime Validationとしてどこまで必要かは一度判断したい。

5. **decimal.fixed_scale**

   * Registry自身がまだ `draft` で、storage_policyも未確定。
   * これは仕分け以前に型自体がHOLD。

6. **Instant**

   * これもRegistryでは `draft` / normalization_policy unresolved。
   * ただしUTC/JST方針はさっきの0173でかなり方向が決まった。

なので、かなり成果出たと思う。

**66件を眺める必要がある話から、実質「人間が考えるべき数件」にまで圧縮できた。**

これ、まさに今回やりたかったことやと思う。笑
次はこの結果をCatalogへ `generation_class` みたいな列として入れる前に、**deprecated 3件とZERO_REJECTEDの整理を先に確定**させるのが綺麗そう。

----

うん、**その見立てでかなり大丈夫そう**やと思う。笑

今回やって見えたのは、単項目チェックの大半が、

```text
Validation Type
＋
Resolved Contract
↓
TestPattern自動生成
↓
Expected自動生成
↓
実データへ適用
↓
PASS / REJECT
```

まで機械で流せる構造になってるってこと。

しかも懸案も、「自動化できるか分からない」系じゃなくて、だいたい **Studio標準ルールをあと数個決めれば済む** 話に寄ってる。

たとえば、

* 中央値の作り方 → 固定ルールでいける
* 文字列代表値 → Studio標準を決めればいける
* Unicode文字数 → 共通カウンターを決めればいける
* minimum / maximum境界 → 完全機械化できる
* boolean / うるう年 / NaN等 → 型固有パターンとして固定できる
* Override → Resolved Contractを見て生成・抑止すればいい

なので、「人間が毎項目ごとにテストケース考えないと無理」って世界では全然ない。

むしろ今回の結論は、

> **単項目チェックは、かなり高い割合で「定義を承認したらテストが勝手に生える」世界に持っていける**

やと思う。

もちろん100%ではない。日本語文字列をどこまで保証するかとか、特殊な業務形式を標準に入れるかとか、まだ人間が決めるところは残る。

でもそれも、

> テストケースそのものを人間が作る
> ではなく
> **「Studioの標準ルールを一度決める」**

に圧縮できそうなのが大きい。

なので現時点の評価を言葉にするなら、

**「単項目Validationの自動テストは、研究課題というより実装課題の領域に入りつつある」**

くらいまで来たと思う。笑

あとは実際に `Resolved Contract → Generated TestPattern → F12実Data拒否` を一本通して、「ほら動いた」を見せれば、一気に現実味が出るやつやね。


