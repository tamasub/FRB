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

---

# 8. 差分を部品として組み合わせる

Expected Diffを小さな部品として扱えれば、

```text
Expected Diff A
+
Expected Diff B
+
Expected Diff C
```

のように組み合わせて、大きなテストを表現できる可能性がある。

考え方の進化:

```text
差分を比較する
↓
差分を期待値にする
↓
差分を部品化する
↓
差分を組み合わせてテストする
```

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

# 13. APPとは独立した「検証用別観点」を持つ

Expected Diff方式の上位原理として重要なのは、

> **APPの実行経路とは独立した検証経路を持ち、両者が同じInputから同じ結果へ到達することを確認する。**

という考え方である。

```text
                    Input
                   /     \
                  /       \
                 ↓         ↓
          APP実行経路    検証用別経路
                 ↓         ↓
          Actual Output   仮Expected Output
                 ↓         ↓
            Actual Diff  Expected Diff
                  \       /
                   \     /
            品質保証済みDiff Tool
                     ↓
                   一致？
                     ↓
                   PASS
```

このとき重要なのは、

```text
APPの実装ロジック
≠
検証用別経路のロジック
```

である。

APP側の同じFunctionや同じ計算実装をExpected生成でも再利用すると、
同じ誤りを共有し、誤った結果でも一致してPASSする危険がある。

したがって、

> **APPとは別観点・別責務で構成された、品質保証済みの検証用部品によってExpected側を導出する。**

ことを基本原則とする。

## 13.1 検証用別観点の信頼条件

本方式では、

```text
APP実行結果
=
検証用別観点の実行結果
```

であれば無条件に正しい、と考えるわけではない。

成立条件は、

> **検証用別観点そのものが事前に十分な品質保証を受けていること。**

である。

つまり信頼の流れは、

```text
品質保証済みInput Generator
+
品質保証済みResolver
+
品質保証済みMutation Engine
+
品質保証済み固有計算部品
+
品質保証済みDiff Tool
↓
検証用別経路
↓
APP Actualとの一致
↓
PASS
```

となる。

個別テストでは検証用別経路そのものを毎回再承認せず、
保証済み部品として再利用する。

## 13.2 現時点ではAIをOracleにしない

AIは、

```text
不足しているTestPatternを提案する
Input生成規則を提案する
Expected生成規則を提案する
波及計算の必要性を発見する
検証用部品の候補を設計する
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
1. Inputを個別テストごとに人間が手作りしない。

2. Field Definition / Validation Type / TestPattern /
   Type Generator ConfigからInputを機械導出する。

3. 文字列は型共通の値生成テンプレート、
   数値は境界値・seed付き決定論的乱数、
   日付は基準日時 + Offset等で生成する。

4. 項目固有Templateは、
   機械導出だけでは成立しない場合の最終手段とする。

5. Expected Diffを人間が直接書かない。

6. Inputをコピーし、
   品質保証済みGeneric Mutation Engine等で
   期待する変更だけを仮Expected Outputへ適用する。

7. APP固有の同一ロジックをExpected生成へ流用しない。

8. APPとは独立した品質保証済みの検証用別経路で
   仮Expected Outputを導出する。

9. 品質保証済みのGit DiffのようなDiff Toolを、
   Expected / Actual共通の観測器として固定する。

10. Input vs 仮Expected OutputからExpected Diffを、
    Input vs Actual OutputからActual Diffを機械生成する。

11. Expected Diff vs Actual Diffが一致すればPASSとする。

12. 変更指定されていない箇所は
    Input継承とDiff比較によって不変を保証する。

13. 検証用別経路そのものは事前に品質保証する。

14. 現時点ではAIを最終Oracleにしない。
    AIはOracle候補を設計・提案し、
    承認後に決定論的な保証済み部品へ昇格させる。

15. 波及変更を導出できない場合は、
    「検証用別経路に何の知恵が足りないか？」を考える。

16. 必要ならAPP側も、
    責務単位で実行・観測可能な構造へ変更する。
```

---

# 16. 一文で言うなら

Expected Diffそのものの定義:

> **期待値差分（Expected Diff）とは、品質保証済みのGit DiffのようなDiff Toolを状態変化の共通観測器として固定し、そのツールがInputと仮Expected Outputから生成した差分出力を期待値として扱い、同じ観測器で生成したActual Diffとの一致によって保証する手法である。**

本方式をInput生成まで含めて一段上から定義すると、

> **Expected Diff方式とは、承認済みの項目定義・Validation Type・TestPattern・Generator規則からInputを機械導出し、APPとは独立した品質保証済みの検証経路によって期待状態を機械導出し、その状態変化を品質保証済みDiff Toolで観測して、APPが実際に起こした状態変化との一致を保証する方式である。**

Approval Engineeringの観点では、

> **個別のInput値やExpected Outputを毎回承認するのではなく、値を生む型・生成規則・検証用部品・Diff Toolを事前に保証し、人間の承認対象を上位の意図へ圧縮する。**

ことが重要な狙いである。

さらに短く言うなら、

> **値を承認するのではなく、値と期待差分を生む仕組みを承認する。**

現時点のAI境界:

> **AIはOracleを設計してよい。しかし、Oracleそのものにはしない。**

---

## Revision History

- 2026-08-24 / v0.3: Inputも機械導出する方針を明示。Field Definition / Validation Type / TestPattern / Type Generator ConfigからInputを生成し、文字列テンプレート、seed付き決定論的乱数、基準日時 + Offsetによる日付生成を整理。項目固有Templateは最終手段とした。品質保証済みGeneric Mutation Engineを追加し、APPとは独立した「検証用別観点」の品質保証済み経路とActualを比較する上位原理を追加。現時点ではAIを最終Oracleにしない境界を明記。
- 2026-08-24 / v0.2: 「品質保証済みのGit DiffのようなDiff ToolをExpected / Actual共通の観測器として固定し、その出力を期待値として扱う」という思想を主定義へ昇格。Diff Toolを事前保証し、個別テストでは差分生成方法を再承認しないというApproval Engineering上の位置づけを追記。
- 2026-08-24 / v0.1: Expected Diff方式の単独重要メモとして初版作成。基本概念、仮Expected Output生成、Runner保証、Actual Diff比較、波及変更とRunnerの知恵、APP構造との関係を整理。
