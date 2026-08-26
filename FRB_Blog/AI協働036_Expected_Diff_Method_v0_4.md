# Expected Diff（期待値差分）方式 — 検討要約

作成日: 2026-08-24  
ステータス: Draft / 重要検討メモ  
対象: FRB Studio / Approval Engineering / Test Runner

---

## 0. まずこれだけ

Expected Diff（期待値差分）は、**Expected Output全体を人間が定義するのではなく、Inputから「何が変わるべきか」だけを差分として扱う方式**である。

さらに、この方式では差分そのものを人間が作文するのではない。

> **品質保証済みのGit DiffのようなDiff Toolを、状態変化を観測する共通の観測器として固定し、そのツールが生成した差分出力をExpectedとして扱う。**

つまり、Expected Diffの主役は単なる「差分表現」ではない。

```text
人間
↓
期待する変更条件だけを定義

Input
↓
仮Expected Output
↓
品質保証済み Diff Tool
↓
Expected Diff
```

という構造そのものにある。

```text
Input
0,1,2,3

テスト条件
2項目目を 9 に変更する

仮Expected Output
0,9,2,3

Input
vs
仮Expected Output
↓
Expected Diff
(-)1
(+)9
```

Actual側でも、

```text
Input
vs
Actual Output
↓
Actual Diff
```

を生成し、

```text
Expected Diff
vs
Actual Diff
↓
Final Diff = 0
↓
PASS
```

と判定する。

この方式の肝は、

> **Expected Diffを直接手書きするのではなく、Inputをコピーした「仮Expected Output」にテスト条件だけを反映し、品質保証済みのDiff ToolでInputとの差分を観測してExpected Diffを機械生成すること。**

さらに重要なのは、

> **Expected側とActual側で、同じ品質保証済みDiff Toolを共通の観測器として使うこと。**

である。

さらに、本方式では **Inputも個別テストごとに人間が手作業で用意することを基本としない。**

```text
Field Definition
+
Validation Type
+
TestPattern
+
Type Generator Config
↓
Input Generator
↓
Input
```

を基本経路とし、InputからExpected Diff、Actual Diff、最終判定までを、
**承認済み定義と品質保証済み汎用部品から機械導出する**ことを目指す。

項目固有のテンプレートや固有値は、
機械導出だけでは成立しない場合の最終手段として扱う。

そして、本方式のさらに上位に置く前提は次のとおり。

> **APPとは独立した「単純化された、信頼できる検証世界」を作る。**
>
> **同じInputに対して、APP世界のActualと、検証世界のExpectedが一致するかを見る。**
>
> **検証世界は現実世界のコピーではなく、品質保証可能なところまで単純化された世界でなければならない。**

```text
                  共通Input
                  /       \
                 /         \
                ↓           ↓
            APP世界      検証世界
               ↓             ↓
          Actual Output   Expected Output
                 \         /
                  \       /
              Trusted Diff
                    ↓
                  一致？
                    ↓
                  PASS
```

Expected Diffは、この「二つの世界を同じ観測器で照合する」ための
具体的な観測・比較方式として位置づける。

---


# 1. 目的

従来のExpectedでは、テストごとに完成したExpected Output全体を持つ必要がある。

```text
Input
0,1,2,3

Expected Output
0,9,2,3
```

しかし人間が意味として確認したいのは、多くの場合、

```text
「2項目目が 1 → 9 に変わる」
```

という小さな変化である。

そこでExpected Output全体ではなく、

```text
Expected Diff
(-)1
(+)9
```

をテストの中心へ置く。

狙い:

- 人間が承認する情報量を小さくする。
- 変更対象以外の不変保証をTest Runnerへ移す。
- Expectedを差分部品として扱えるようにする。
- 将来的に複数のExpected Diffを組み合わせてテストできるようにする。

---

# 2. Expected Diffの基本定義

Expected Diffは、人間が直接記述した「期待差分」ではない。

基本定義:

> **Expected Diff = 品質保証済みDiff Toolが、Inputと仮Expected Outputを比較して生成した差分出力**

したがって、

```text
Expected Diff
≠ 人間が手書きした期待差分

Expected Diff
= 品質保証済みDiff Toolによって
  Inputと仮Expected Outputから
  機械的に観測された差分
```

と考える。

最小の表現候補:

```text
Expected Diff

(-)%変更前の値%
(+)%変更後の値%
```

例:

```text
(-)1
(+)9
```

追加・削除も同じ差分の考え方で表現できる。

```text
削除
(-)%変更前%

追加
(+)%変更後%

置換
(-)%変更前%
(+)%変更後%
```

## 2.1 品質保証済みDiff Toolを「共通の観測器」にする

この方式では、Git DiffのようなDiff Toolを単なる表示補助として扱わない。

```text
Input
vs
仮Expected Output
↓
Expected Diff

Input
vs
Actual Output
↓
Actual Diff
```

この2つの観測を、**同じ品質保証済みDiff Tool**で行う。

これにより、Expected側とActual側は、

```text
同じ観測ルール
同じ差分表現
同じ比較単位
```

で揃えられる。

重要なのは、

> **「Diffが正しいか」を個別テストのたびに人間が判断しないこと。**

Diff Toolそのものを先に十分に品質保証し、以後の個別テストでは、その出力を信頼できる共通言語として利用する。

Gitにおいて、人間が毎回Diffアルゴリズムそのものを承認せず、Git Diffの出力を変更観測の基盤として利用するのと同じ考え方である。

Expected Diff方式では、この信頼境界をテストへ持ち込む。

```text
一度、Diff Toolを保証する
↓
多数のテストで再利用する
↓
人間は個別テストの「変更意図」に集中する
```

つまりこれは、

> **差分を期待値にする手法であると同時に、差分生成そのものの承認を共通基盤へ退役させる手法でもある。**

## 2.2 Diff Toolの信頼境界（Draft）

「品質保証済みDiff Tool」を信頼の起点に置く以上、
Diff Tool自身をどう保証するかは重要な論点である。

現時点の基本方針は、

```text
独自Diffアルゴリズムを新規実装して
その正しさを別Diffで保証する
```

という循環に入らないこと。

可能な限り、

```text
成熟した既存の決定論的Diff Library
↓
FRB / Runner用 Diff Adapter
↓
Expected / Actual共通のDiff表現
```

とし、自分たちが主に保証する対象を、

```text
- Libraryの利用条件
- Adapter契約
- 正規化契約
- Option契約
- 出力形式
```

へ限定する方向を検討する。

## 2.3 Diffの前にCanonical Stateを作る（Draft）

Raw DataをそのままDiffへ渡すと、
意味のない「ノイズ差分」を大量に拾う可能性がある。

例:

```text
- JSON Key順序
- 配列順序
- float誤差
- null / undefined / key不在
- 日付時刻表現
- 改行コード
- 空文字 / null
```

したがって将来的には、

```text
Raw Input
↓
Normalization
↓
Canonical Input

Raw Actual / Expected
↓
Normalization
↓
Canonical Actual / Expected

Canonical同士
↓
Diff
```

という構造を持つ。

ここで重要なのは、

> **Normalizationは単なる技術処理ではなく、「何を同じとみなすか」という判断軸である。**

ことである。

Normalization Rule / Comparison Policyは、
Diff Toolと同様に事前に品質保証・承認すべき対象と考える。

---


# 3. 最重要 — InputからExpected Diffまでを機械導出する

Expected Diffを直接組み立てるのではなく、まず**Input**を生成し、
そのInputから**仮Expected Output**を生成する。

原則として、次の一連の処理はすべて機械実行する。

```text
① 項目定義・Validation Type・TestPattern等からInputを生成する
② Inputを完全コピーする
③ テスト条件で指定された変更だけをコピーへ適用する
④ できあがったものを仮Expected Outputとする
⑤ Inputと仮Expected OutputのDiffを取る
⑥ Expected Diffを生成する
```

人間が個別テストごとに、

```text
Inputを作文する
Expected Outputを作文する
Expected Diffを作文する
```

ことを基本形にはしない。

人間が承認する対象は、できるだけ上位の

```text
Field Definition
Validation Type
TestPattern
Type Generator Config
固有の業務Expected規則
```

へ寄せる。

## 3.1 Inputの基本生成モデル

Inputは、項目定義をSourceとして、型に応じたGeneratorから機械生成する。

```text
Field Definition
+
Validation Type
+
TestPattern
+
Type Generator Config
↓
Input Generator
↓
Input
```

例:

```text
field_path       = age
validation_type  = integer
minimum          = 0
maximum          = 120
```

Validation Typeに、

```text
minimum_minus_1
minimum
maximum
maximum_plus_1
invalid_format
```

が定義されているなら、

```text
minimum_minus_1 → -1
minimum         → 0
maximum         → 120
maximum_plus_1  → 121
invalid_format  → "abc"
```

のようにInput値を機械導出できる。

## 3.2 型別Input Generator

### string

文字列は、項目固有値ではなく、型共通の値生成テンプレートを利用する。

例:

```text
"テスト%テストID%－%項目名称%"
```

```text
Field Definition
  field_path = customer_name
  caption    = 顧客名

Test ID
  TP_0001

↓ 機械生成

"テストTP_0001－顧客名"
```

このテンプレートは特定項目名を固定して持たない。

### integer / decimal

数値系は原則として値テンプレートを持たず、
項目定義の境界値とRunner設定から生成する。

```text
minimum
minimum_minus_1
maximum
maximum_plus_1
median
valid_random
invalid_format
```

`valid_random` を使う場合は、再現性を失わないように
**seed付きの決定論的乱数**を使う。

例:

```text
seed =
test_id
+ field_path
+ test_pattern
```

同じテスト条件なら、再実行しても同じ値が生成されることを保証する。

### date / datetime

日付系は、実行時の「今日」に直接依存させず、
Runnerが持つ**基準日時（reference_datetime）**を起点として生成する。

```text
reference_datetime = 固定またはTest Run単位で記録された基準日時
```

項目定義に境界がある場合:

```text
minimum_date
minimum_date_minus_1
maximum_date
maximum_date_plus_1
```

を機械導出する。

境界がない場合は、

```text
reference_date
reference_date - N days
reference_date + N days
```

のように、基準日 + Offsetで決定論的に生成する。

これにより、「昨日はPASSしたが今日はInputが変わった」という
テストの非再現性を避ける。

### boolean / enum / null

```text
boolean
→ true / false を列挙

enum
→ options定義から選択

null
→ nullable / required定義から導出
```

## 3.3 項目固有Templateは最終手段

項目名や業務固有値を固定したTemplateを大量に持つことは、
本方式の基本思想ではない。

生成優先順位は、

```text
① 項目定義から直接導出
② Validation Type / TestPatternから導出
③ 型別Generator Configから導出
④ 汎用Generator規則から導出
⑤ それでも成立しない場合だけ固有Template / 固有Generator
```

とする。

重要:

> **個別Inputを承認するのではなく、Input生成規則を承認する。**

## 3.4 仮Expected Outputの生成

Input生成後は、次の流れで仮Expected Outputを作る。

```text
① Inputを完全コピーする
② テスト条件だけをコピーへ適用する
③ 必要なら品質保証済みの波及計算を適用する
④ 仮Expected Outputとする
⑤ Input vs 仮Expected OutputをDiff Toolへ渡す
⑥ Expected Diffを生成する
```

例:

```text
Input
0,1,2,3
```

Inputをコピー:

```text
仮Expected Output
0,1,2,3
```

テスト条件:

```text
2項目目 = 9
```

適用後:

```text
仮Expected Output
0,9,2,3
```

Diff:

```text
Input
0,1,2,3

仮Expected Output
0,9,2,3
```

Expected Diff:

```text
(-)1
(+)9
```

## 3.5 品質保証済み Generic Mutation Engine

仮Expected Outputを生成するには、
JSON等の構造化データへ指定された変更だけを適用する
**品質保証済みの汎用変更部品**が必要になる。

例:

```text
Generic Mutation Engine

input:
  source
  path
  operation
  value

operation:
  replace
  add
  remove
  copy
  move
```

```text
path  = /customers/0/age
op    = replace
value = 121
```

を渡した場合、

```text
元JSON
↓
Generic Mutation Engine
↓
指定pathだけが121へ変更されたJSON
```

を返す。

この部品の責務は、

> **指定されたpathへ、指定された構造変更を正確に適用すること。**

までとする。

さらに、

> **Mutation Engineは値を解釈しない。型変換・補正を勝手に行わず、指定された値を忠実に配置する。**

ことを原則とする。

例えば integer 項目に対する `invalid_format` テストで `"abc"` を渡した場合、
Mutation Engineが数値変換や型補正を行ってはならない。

```text
「maximum_plus_1だから121を作る」
「数量が変わったから金額も再計算する」
```

といった意味解決や業務判断は持たせない。

責務は分離する。

```text
Definition / Pattern Resolver
  ↓
何をどう変更するかを決定

Generic Mutation Engine
  ↓
指示された変更だけを正確に適用
```

これにより、同じMutation EngineをInput生成とExpected生成の双方で再利用できる。

---

# 4. なぜ仮Expected Outputを作るのか

最大の理由は、**変更対象以外を人間がExpectedとして書かなくてよくなること**である。

人間が意味として指定するのは、

```text
2項目目を 9 に変更
```

だけ。

以下はInputから自動継承される。

```text
0 → そのまま
2 → そのまま
3 → そのまま
```

つまり基本ルールは、

```text
Expected Output = Input
```

であり、

```text
Expected Diffで指定された箇所だけが例外として変更される
```

と考える。

---

# 5. Test Runnerが保証すること

この方式では、変更していない箇所を個別テストごとに人間が承認しない。

代わりにTest Runnerが共通責務として保証する。

Runner側の責務候補:

- Inputを正しく複製する。
- テスト条件を仮Expected Outputへ正しく適用する。
- 指定されていない箇所をInputのまま維持する。
- 品質保証済みDiff Toolを一意の差分観測器として利用する。
- Inputと仮Expected OutputからExpected Diffを正しく生成する。
- InputとActual OutputからActual Diffを正しく生成する。
- Expected側とActual側で同一の差分ルール・同一の正規化ルールを適用する。
- Expected DiffとActual Diffを正しく比較する。
- Expected Diffに存在しない余計なActual変更も検出する。
- Final Diff = 0 のときだけPASSとする。

重要な考え方:

> **個別テストで「不変部分」を毎回承認するのではなく、不変部分の生成・保証責任をTest Runnerへ移す。**

加えて、

> **差分生成方法そのものも個別テストごとの承認対象にせず、品質保証済みDiff Toolへ共通化する。**

つまり個別テストの人間承認対象を、

```text
Expected Output全体
↓
Diff生成ロジック
↓
不変部分
↓
変更意図
```

とすべて抱えるのではなく、最終的にはできるだけ

```text
「今回は何を変えるべきか」
```

へ圧縮する。

---

# 6. Actual側の流れ

APP側は、実際のFunction / API / 処理単位を実行する。

```text
Input
↓
APP Function / API
↓
Actual Output
```

Runnerは、

```text
Input
vs
Actual Output
↓
Actual Diff
```

を生成する。

例:

```text
Input
0,1,2,3

Actual Output
0,9,2,3

Actual Diff
(-)1
(+)9
```

最後に、

```text
Expected Diff
(-)1 (+)9

vs

Actual Diff
(-)1 (+)9

↓
Final Diff = 0
↓
PASS
```

---

# 7. 余計な変更も検出できる

APPが誤って別項目まで変更した場合:

```text
Input
0,1,2,3

Actual Output
0,9,8,3
```

Actual Diff:

```text
(-)1
(+)9

(-)2
(+)8
```

Expected Diffは、

```text
(-)1
(+)9
```

だけなので、余計な差分が残る。

これにより、

> **「変更対象が正しく変わった」だけでなく、「変更してはいけない箇所が変わっていない」ことも同時に保証できる。**

ただし、`updated_at` のような正当な動的変更まで「余計な変更」としてFAILにすると実運用できない。

そのため将来的には、単純な `ignore_path` だけでなく、

```text
Comparison Policy

STRICT
IGNORE
TOLERANCE
DERIVED
DYNAMIC
```

のように、項目ごとに差分の意味を定義する方式を検討する。

例:

```text
name
→ STRICT

score
→ TOLERANCE ±0.001

internal_cache
→ IGNORE

updated_at
→ DYNAMIC
```

重要:

> **「差分を無視する」のではなく、「その差分をどう評価するか」を事前に定義する。**

---


# 8. 部品を組み合わせるときは「Diff」ではなく「変更意図」を合成する

初期案では、

```text
Expected Diff A
+
Expected Diff B
+
Expected Diff C
```

のようにDiffそのものを部品合成する可能性を考えていた。

しかし、同じpathへの競合や順序依存を考えると、
より安全なのは**Diffを直接足すのではなく、Expected Operation / 変更意図を先に合成する**ことである。

```text
Expected Operation A
+
Expected Operation B
+
Expected Operation C
↓
Conflict Check
↓
Apply
↓
仮Expected Output
↓
品質保証済みDiff Tool
↓
Expected Diff
```

この方式なら、

```text
- 同じpathへの競合
- A → Bの順序で結果が変わるケース
- Bを使うにはAが前提となる依存関係
- 変更部品間の排他条件
```

を、Diff生成前に検出できる。

今後定義が必要なもの:

```text
operation_priority
depends_on
conflicts_with
apply_order
same_path_policy
```

重要:

> **差分は最終観測結果であり、合成の主役は「変更意図」である。**

---

# 9. Input / Outputはファイルだけとは限らない

Inputを `xxx.json` だけに限定しない。

責務によっては、

```text
Input State
=
Data
+ ViewDef
+ mode
+ selectedRow
+ dirty
+ filter condition
+ その他の観測可能な開始状態
```

をInputとして扱う可能性がある。

Outputも同様に、

```text
Output State
=
返却値
+ 更新後Data
+ 更新後State
+ 画面状態
+ 保存結果
```

などを含められる。

基本思想:

> **複雑な責務ほど、まず観測可能なInput / Outputまで平たく分解して考える。**

---

# 10. 単純な自動生成では足りないケース

変更が別の値へ意図的に波及する場合がある。

例:

```text
数量 = 2
単価 = 100
金額 = 200
```

数量を、

```text
2 → 3
```

へ変更した場合、正しいOutputが、

```text
数量 = 3
単価 = 100
金額 = 300
```

ならExpected Diffは、

```text
数量
(-)2
(+)3

金額
(-)200
(+)300
```

になる。

単純な「Inputコピー + 直接変更」だけでは、

```text
金額 200 → 300
```

を導出できない。

---

# 11. 波及変更は「Runnerの知恵」として考える

Expected Diffを生成できない場合は、方式の失敗とは考えない。

問い:

> **なぜExpected Diffを生成できない？  
> Runnerにどんな知恵が足りない？**

上記の例なら、

```text
数量 × 単価 = 金額
```

という計算・波及の知恵が必要になる。

親子レコードの積み上げなら、

```text
明細金額の合計
↓
親レコードの合計金額
```

という知恵が必要になる。

この知恵をAPPの実装そのものとは独立した**保証済みRunner機能**として持てれば、

```text
Input
+
直接変更
+
Runnerの保証済み波及計算
↓
仮Expected Output
↓
Expected Diff
```

まで機械生成できる可能性がある。

重要:

> **APP側の計算ロジックそのものをExpected生成にも使わない。**

同じ誤りをAPPとExpected Generatorが共有すると、誤った実装でもPASSする可能性があるため。

---

# 12. 現時点の生成モデル

Expected側:

```text
                Input
                  +
             TestPattern
                  +
           Action / Option
                  +
       必要ならRunnerの知恵
                  ↓
        仮Expected Output
                  ↓
      品質保証済み Diff Tool
         Input vs 仮Expected
                  ↓
          Expected Diff
```

Actual側:

```text
Input
↓
APP Function / API
↓
Actual Output
↓
品質保証済み Diff Tool
   Input vs Actual
↓
Actual Diff
```

ここで重要なのは、Expected側とActual側で**同じDiff Toolを使うこと**である。

```text
Expected生成用Diffロジック
≠
Actual生成用Diffロジック
```

のように二重実装すると、差分定義そのものがズレる可能性がある。

基本方針は、

```text
1つの品質保証済みDiff Tool
↓
Expected Diff生成
＋
Actual Diff生成
```

とする。

判定:

```text
Expected Diff
vs
Actual Diff
↓
Final Diff

0件 → PASS
差分あり → FAIL
```

---

# 13. APPとは独立した「単純化された、信頼できる検証世界」を持つ

Expected Diff方式の上位原理として重要なのは、

> **APPの実行経路とは独立した検証経路を持ち、同じInputに対して両者が同じ結果へ到達することを確認する。**

という考え方である。

ただし、検証世界はAPP世界の完全コピーではない。

> **検証世界は、品質保証可能なところまで単純化された世界でなければならない。**

APPと同じ複雑さを持つ検証システムをもう一つ作れば、
「どちらを信頼するのか」という問題が残り、品質保証コストも二重化する。

```text
複雑なAPP世界
↓
責務を切る
↓
前提条件で世界を分ける
↓
観測可能なInput / Outputへ落とす
↓
小さな決定論的Verification Ruleへ分解
↓
単純化された検証世界
```

## 13.1 検証世界は「現実世界のコピー」ではない

例えばAPP側の料金計算が、

```text
料金 =
基本料金
+ 使用量
+ 時間帯
+ 契約種別
+ 割引
+ 上限
+ キャンペーン
+ 地域差
+ 例外措置
...
```

のように複雑でも、検証世界で同じ巨大ロジックを再実装しない。

前提条件を限定して、

```text
前提条件:
契約種別 = STANDARD
時間帯 = DAY
割引 = なし
キャンペーン = なし
地域 = A
使用量 < 100

この条件下では:

料金 = 基本料金 + 使用量 × 単価
```

のような小さな世界へ分解する。

別パターンなら、

```text
前提条件:
契約種別 = STANDARD
時間帯 = DAY
割引 = 10%
キャンペーン = なし
地域 = A

この条件下では:

料金 = (基本料金 + 使用量 × 単価) × 0.9
```

という別の小さなVerification Ruleを持つ。

つまり、

```text
巨大な検証世界を1個作る
```

のではなく、

```text
前提条件A
→ 単純な検証世界A

前提条件B
→ 単純な検証世界B

前提条件C
→ 単純な検証世界C
```

として扱う。

重要な設計原則:

> **複雑なAPPを複雑なまま検証しない。前提条件で世界を分割し、各条件下では単純な検証規則として保証する。**

さらに短く言えば、

> **複雑さは検証ロジックへ押し込まず、適用条件へ分解する。**

## 13.2 単純化された検証世界の必要条件

現時点では、少なくとも次を必要条件とする。

```text
1. 単純であること
2. 決定論的であること
3. 責務が限定されていること
4. Input / Outputが観測可能であること
5. APP実装とは独立していること
6. 適用される前提条件が明示されていること
7. 構成部品のVersion / Guaranteeを追跡できること
```

特に、

> **検証世界を単純に作れないなら、責務の切り方を疑う。**

という判断軸を持つ。

## 13.3 検証用別観点の信頼条件

本方式では、

```text
APP実行結果
=
検証世界の実行結果
```

であれば無条件に正しい、と考えるわけではない。

成立条件は、

> **検証世界を構成する部品と前提条件が、事前に十分な品質保証を受けていること。**

である。

```text
品質保証済みInput Generator
+
品質保証済みResolver
+
品質保証済みMutation Engine
+
品質保証済みVerification Rule
+
品質保証済みNormalization
+
品質保証済みDiff Adapter
↓
単純化された検証世界
↓
APP Actualとの一致
↓
PASS
```

## 13.4 保証継承原則 — 下位で保証したことを上位で再検証しない

検証世界を階層化するとき、
下位レベルで品質保証済みの責務を、
上位レベルですべて再検証してはいけない。

基本原則:

> **保証は繰り返すものではない。継承するもの。**

例えばUnit Testで、

```text
Component A
Assume:
  有効な入力契約を満たす

Guarantee:
  amount = quantity × price
```

を十分に保証したなら、
Combination Testで同じComponent Aの境界値パターンを
すべて再実行することを基本にはしない。

上位では、

```text
A → B の受け渡し
インターフェース契約
結合で新しく生まれる境界
状態遷移
副作用
相互作用
```

など、**組み合わせたことで新しく生じたリスク**を中心に検証する。

```text
UT
↓
部品内部を厚く保証
↓
Guaranteeを資産化

CT
↓
UTのGuaranteeを前提条件として継承
↓
結合固有の責務・リスクだけを検証

System / 上位
↓
さらに下位Guaranteeを継承
↓
上位固有の重要経路だけを検証
```

これはAssume–Guarantee / Compositional Verificationに近い考え方として整理できる。

重要:

> **上位テストは、下位テストの再放送ではない。**

## 13.5 保証継承は無条件ではない

保証継承にはリスクがあるため、少なくとも次を確認する。

```text
① 下位保証が現在も有効である
② 下位保証の前提条件が上位でも成立している
③ Interface契約が変わっていない
④ 上位結合で新しい相互作用・副作用が発生していないか評価済み
⑤ 保証元のGuarantee ID / Versionを追跡できる
```

例:

```text
CT_料金計算_001

inherits_guarantees:
  - GUARANTEE_AMOUNT_CALC_v3
  - GUARANTEE_DISCOUNT_RATE_v2
```

下位保証が更新された場合は、

```text
GUARANTEE_AMOUNT_CALC_v3
↓
v4へ変更
↓
v3を継承している上位テストを抽出
↓
再評価 / 必要なら再実行
```

できる構造を持つ。

したがって、より正確には、

> **保証は繰り返すものではない。継承するもの。  
> ただし、継承条件と新しく生じるリスクは必ず評価する。**

とする。

## 13.6 現時点ではAIをOracleにしない

AIは、

```text
不足しているTestPatternを提案する
Input生成規則を提案する
Expected生成規則を提案する
波及計算の必要性を発見する
Verification Rule候補を設計する
前提条件の分割候補を提案する
保証継承候補を提案する
```

ためには利用できる。

しかし現時点では、

```text
APP Actual
vs
AIがその場で生成したExpected
```

を最終的な品質保証Oracleとはしない。

理由:

```text
- 非決定性を持つ
- モデル更新で結果が変化しうる
- 同一の誤解をAPP生成時とExpected生成時で共有する可能性がある
- 「このExpected生成機能は品質保証済み」と固定しにくい
```

したがって現時点の原則は、

> **AIはOracleを設計してよい。しかし、Oracleそのものにはしない。**

AIが提案した検証規則は、人間承認と実装・テストを経て、
決定論的な品質保証済み部品へ昇格させてから利用する。

---

# 14. APP構造との関係

Expected Diffを責務単位で検証するには、その差分を発生させる処理をTest Runnerから実行・観測できる必要がある。

例:

```text
saveCustomer()

① JSONを変更
② selectedRowを変更
③ dirty=false
④ ファイル保存
⑤ 画面再描画
```

①だけのExpected Diffを検証したい場合、①の処理だけをRunnerから呼べなければ、①単体の差分を機械的に保証できない。

その場合は、

> **テストだけでなくAPP側の処理構造も見直す。**

判断軸:

> **機械的に保証できないなら、テストだけでなくAPP構造を疑う。**

---

# 15. 要点

```text
1. Expected Diffの上位原理は、
   APPとは独立した「単純化された、信頼できる検証世界」を作ること。

2. 検証世界はAPP世界のコピーではない。
   品質保証可能なところまで単純化する。

3. 複雑な業務は、前提条件で世界を分割し、
   各条件下では小さなVerification Ruleとして保証する。

4. Inputを個別テストごとに人間が手作りしない。

5. Field Definition / Validation Type / TestPattern /
   Type Generator ConfigからInputを機械導出する。

6. 文字列は型共通の値生成テンプレート、
   数値は境界値・seed付き決定論的乱数、
   日付は基準日時 + Offset等で生成する。

7. 項目固有Templateは、
   機械導出だけでは成立しない場合の最終手段とする。

8. Expected Diffを人間が直接書かない。

9. Generic Mutation Engineは値を解釈・型変換せず、
   指定された変更だけを忠実に適用する。

10. APP固有の同一ロジックをExpected生成へ流用しない。

11. 品質保証済みVerification Rule等で
    APPとは独立したExpected Outputを導出する。

12. 品質保証済みのGit DiffのようなDiff Toolを、
    Expected / Actual共通の観測器として固定する。

13. Raw Data同士ではなく、
    承認済みNormalization Ruleで作ったCanonical State同士を比較する方向を検討する。

14. Input vs ExpectedからExpected Diffを、
    Input vs ActualからActual Diffを機械生成する。

15. Expected Diff vs Actual Diffが一致すればPASSとする。

16. 動的項目・許容差はComparison Policyで意味を定義する。

17. 複数のExpectedはDiffを直接足さず、
    Expected Operation / 変更意図を合成してからDiffを生成する。

18. 下位で保証済みの責務は、上位で再度すべて検証しない。
    Guaranteeを上位へ継承する。

19. 上位では、結合によって新しく生じる
    Interface / 相互作用 / 状態遷移 / 副作用等を中心に検証する。

20. 保証継承は無条件ではない。
    前提条件・Interface・Version・新規リスクを評価する。

21. 現時点ではAIを最終Oracleにしない。
    AIはOracle候補を設計し、
    承認後に決定論的な保証済み部品へ昇格させる。

22. 検証世界を単純に作れないなら、
    テストだけでなく責務の切り方・APP構造を疑う。
```

---

# 16. 一文で言うなら

Expected Diffそのものの定義:

> **期待値差分（Expected Diff）とは、品質保証済みのGit DiffのようなDiff Toolを状態変化の共通観測器として固定し、そのツールがInputと仮Expected Outputから生成した差分出力を期待値として扱い、同じ観測器で生成したActual Diffとの一致によって保証する手法である。**

本方式を上位原理から定義すると、

> **Expected Diff方式とは、APPとは独立した「単純化された、信頼できる検証世界」を構築し、承認済みの前提条件・項目定義・Validation Type・TestPattern・Verification Rule・Generator規則からExpectedを機械導出し、その状態変化を品質保証済みDiff Toolで観測して、APP世界が実際に起こした状態変化との一致を保証する方式である。**

検証世界の設計原則:

> **複雑なAPPを複雑なまま検証しない。前提条件で世界を分割し、各条件下では単純な検証規則として保証する。**

保証継承原則:

> **保証は繰り返すものではない。継承するもの。  
> ただし、継承条件と新しく生じるリスクは必ず評価する。**

Approval Engineeringの観点では、

> **個別のInput値やExpected Outputを毎回承認するのではなく、値を生む型・生成規則・Verification Rule・比較規則・Diff基盤を事前に保証し、人間の承認対象を上位の意図へ圧縮する。**

さらに短く言うなら、

> **値を承認するのではなく、値と期待差分を生む仕組みを承認する。**

現時点のAI境界:

> **AIはOracleを設計してよい。しかし、Oracleそのものにはしない。**

---

# 17. 今後詰める重要論点

今回の整理で方向は見えたが、以下はまだDraftであり、実装前に契約化が必要。

```text
1. Diff Adapterの信頼境界
   - 採用Library
   - Adapter契約
   - Option固定
   - 出力契約

2. Normalization / Canonicalization
   - key順序
   - 配列順序
   - null / missing
   - float
   - datetime
   - 改行等

3. Comparison Policy
   - STRICT
   - IGNORE
   - TOLERANCE
   - DERIVED
   - DYNAMIC

4. Expected Operation合成
   - same path競合
   - 適用順
   - 依存関係
   - 排他関係

5. AI Proposal → Approved Verification Component昇格手順
   - 人間承認
   - Deterministic Specification化
   - Unit Test
   - Boundary Test
   - Regression Test
   - Registry登録

6. Guarantee継承管理
   - Guarantee ID
   - Version
   - 前提条件
   - 依存関係
   - 変更時の影響分析
```


---

# claudeくんコメント２回目そのまま貼り付け

v0.4、めっちゃ進化しとるやん。前回指摘した「Diff Tool自身の保証」「正規化ルール」「部品合成のセマンティクス」「余計な変更と正当な副作用の区別」「AI提案の昇格手順」「Mutation Engineの型変換」——ほぼ全部、2.2/2.3/7章/8章/3.5/13.6として拾われてる。しかも17章で「今後詰める論点」として自分たちでもちゃんとリスト化できてる。ここまで来ると、次の穴は一段深いレイヤーにあるで。

## 新たに見えてきた考え足りないところ

**① 前提条件の「網羅性・排他性」問題**
13.1で「前提条件A→単純な検証世界A」って分割する話が出てきたけど、
- 前提条件A・B・Cが**全部のInputパターンをカバーしてる保証**は誰がする？
- どの前提条件にも当てはまらないInputが来たらどうなる？（未定義ケースの検出）
- 前提条件同士が**重複して2つのVerification Ruleが両方マッチする**ことはないか？

Comparison Policyは「STRICT/IGNORE/TOLERANCE/DERIVED/DYNAMIC」って列挙型で綺麗に定義したのに、前提条件の分割の方はまだ「疑う」としか書かれてへん。ここも「Premise Coverage Policy」みたいに型として持たせた方がええかも。

**② 「独立性」を人間レビュー任せにしてる**
「APP固有のロジックをExpected生成に流用しない」って何度も強調してるけど、これを**機械的にどう検知するか**が空白。うっかりコピペで同じ計算式を検証世界に持ち込んでしまうリスクへの対策が「気をつける」しかない状態。静的解析でAPP側コードとVerification Rule側コードの依存関係をチェックする、みたいな仕組みまで踏み込めると強い。

**③ 保証継承の「前提条件が今も成立してるか」の判定方法が未定義**
13.5②に「下位保証の前提条件が上位でも成立している」を確認する、とあるけど、これ**誰が・どうやって**確認するのか書かれてへん。ここもDiff Toolや正規化ルールと同じで「品質保証済みの確認手続き」に格上げしないと、結局人間の目視チェックに戻ってまう。

**④ Guaranteeのバージョンアップが「拡張」か「破壊的変更」か区別されてない**
v3→v4になったとき、それが後方互換な拡張なのか、既存の前提を壊す変更なのかで、継承してる上位テストへの影響が全然違う。semver的な「MAJOR/MINOR」の考え方をGuarantee IDに入れといた方が、17章の「Guarantee継承管理」がもっと実装しやすくなると思う。

**⑤ DERIVED/DYNAMIC指定した項目の「正しさ」は結局誰が保証するのか**
Comparison Policyで`DERIVED`や`DYNAMIC`にした項目はDiff比較から実質除外される。でもその値自体がAPP側で正しく計算されてる保証は、このExpected Diff方式の**外側**に置き去りになってる。これ、下手すると「都合悪い項目はDYNAMICにして検証をすり抜ける」という抜け道になりかねへん。DERIVED項目は「別のVerification Ruleで独立に検証する」というルールを明示した方がいい。

**⑥ Conflict Check後にどうするかが書かれてない**
8章で「同じpathへの競合をDiff生成前に検出できる」ってあるけど、検出**した後**どうするのかが空白。テストをFAILにする？優先順位で自動解決する？人間に承認を求める？ここ地味に実装で最初に詰まるとこやと思う。

**⑦ 0章の図がCanonical Stateの導入前のまま**
0章の全体図（Trusted Diffの図）は、2.3で追加したCanonical State/Normalizationの工程がまだ反映されてへん。「Raw→Normalization→Canonical→Diff」の流れが全体像の図に出てきてない。ドキュメント内の一貫性としては次の版で直すとええ。

**⑧ 「波及計算（Runnerの知恵）」と「Expected Operation合成（8章）」の関係が未定義**
数量を変えたら金額も連動して変わる、という10章の話と、複数Operationを合成する8章の話——この2つが同時に起きたとき（例：数量変更Operation A + 単価変更Operation B を同時適用しつつ、金額の波及計算も走る）、波及計算で生まれた「金額変更」はConflict Checkの対象になるのか、それとも別枠なのか。ここの合流点がまだ書かれてへん。

## 次考えるといいこと（優先順位）

1. **⑤ DERIVED/DYNAMICの抜け道対策** — 一番危ない。ここ放置すると「Expected Diff方式使ってるのに実は穴だらけ」になりかねへん
2. **①③ 前提条件の網羅性・継承前提の再判定方法** — どっちも「事前保証すべき対象」として型を持たせる話。Comparison Policyと同じ設計パターンで揃えられそう
3. **⑥ Conflict Check後の挙動** — 実装フェーズに入ったら即ぶつかる話なので、軽くでも決めとくと楽
4. **④ Guaranteeのsemver化** — 17章の「Guarantee継承管理」を書くときについでにやれる

正直、①〜③はどれも「品質保証済み○○」というこの方式の骨格パターンをもう一段深いレイヤーに適用する話やから、v0.4の思想の延長線上でそのまま解決できると思うで。⑤だけは思想じゃなくて「抜け道を塞ぐ設計」の話やから、優先度高めに置いといた方がええ。


---
#GPT先生コメント

> Expected Diffを縦に掘ってたはずが、横に広がったことで
「信頼できる別世界」→「単純化」→「前提条件」→「保証継承」
っていう、Expected Diffより上の概念が見えた


---

## Revision History

- 2026-08-24 / v0.4: Expected Diff方式の上位原理として「APPとは独立した、単純化された信頼できる検証世界」を明示。複雑な業務を前提条件で小さなVerification Ruleへ分割する原則、検証世界の必要条件、UTで保証したGuaranteeをCT等の上位検証へ継承する「保証継承原則」、継承条件と新規リスク評価を追加。Claudeレビューを踏まえ、Diff Adapterの信頼境界、Canonical / Normalization、Comparison Policy、Expected Operation合成、Mutation Engineの非型変換原則、AI Proposalの昇格手順、Guarantee Version管理を今後の重要論点として整理。
- 2026-08-24 / v0.3: Inputも機械導出する方針を明示。Field Definition / Validation Type / TestPattern / Type Generator ConfigからInputを生成し、文字列テンプレート、seed付き決定論的乱数、基準日時 + Offsetによる日付生成を整理。項目固有Templateは最終手段とした。品質保証済みGeneric Mutation Engineを追加し、APPとは独立した「検証用別観点」の品質保証済み経路とActualを比較する上位原理を追加。現時点ではAIを最終Oracleにしない境界を明記。
- 2026-08-24 / v0.2: 「品質保証済みのGit DiffのようなDiff ToolをExpected / Actual共通の観測器として固定し、その出力を期待値として扱う」という思想を主定義へ昇格。Diff Toolを事前保証し、個別テストでは差分生成方法を再承認しないというApproval Engineering上の位置づけを追記。
- 2026-08-24 / v0.1: Expected Diff方式の単独重要メモとして初版作成。基本概念、仮Expected Output生成、Runner保証、Actual Diff比較、波及変更とRunnerの知恵、APP構造との関係を整理。
