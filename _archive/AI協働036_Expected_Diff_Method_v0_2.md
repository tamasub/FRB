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

# 3. 最重要 — 仮Expected Outputの生成方法

Expected Diffを直接組み立てるのではなく、まず**仮Expected Output**を生成する。

## 3.1 基本手順

```text
① Inputを完全コピーする
② テスト条件で指定された変更だけをコピーへ適用する
③ できあがったものを仮Expected Outputとする
④ Inputと仮Expected OutputのDiffを取る
⑤ Expected Diffを生成する
```

例:

```text
Input
0,1,2,3
```

### ① Inputをコピー

```text
仮Expected Output
0,1,2,3
```

### ② テスト条件だけを適用

```text
テスト条件
2項目目 = 9
```

```text
仮Expected Output
0,9,2,3
```

### ③ Inputとの差分を取る

```text
Input
0,1,2,3

仮Expected Output
0,9,2,3
```

### ④ Expected Diff生成

```text
Expected Diff
(-)1
(+)9
```

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

# 13. APP構造との関係

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

# 14. 要点

```text
1. Expected Diffを人間が直接全部書かない。

2. 品質保証済みのGit DiffのようなDiff Toolを、
   Expected / Actual共通の観測器として固定する。

3. Inputをコピーして仮Expected Outputを作る。

4. テスト条件で期待する変更だけを仮Expected Outputへ反映する。

5. Input vs 仮Expected Outputを品質保証済みDiff Toolへ渡し、
   Expected Diffを機械生成する。

6. APP実行後も同じDiff Toolで
   Input vs Actual OutputからActual Diffを生成する。

7. Expected Diff vs Actual Diffが一致すればPASS。

8. 変更指定されていない箇所はRunnerがInput値を継承して保証する。

9. Diff生成方法そのものは個別テストで再承認せず、
   共通基盤として事前に品質保証する。

10. 波及変更を生成できない場合は、
    「Runnerに何の知恵が足りないか？」を考える。

11. 必要ならAPP側を、責務単位で実行・観測可能な構造へ変更する。
```

---

# 15. 一文で言うなら

> **期待値差分（Expected Diff）とは、品質保証済みのGit DiffのようなDiff Toolを状態変化の共通観測器として固定し、そのツールがInputと仮Expected Outputから生成した差分出力を期待値として扱い、同じ観測器で生成したActual Diffとの一致によって保証する手法である。**

もう少し短く言うなら、

> **期待値差分とは、品質保証済みDiff Toolの出力を「期待値の共通言語」として扱う手法である。**

Approval Engineeringの観点では、

> **一度Diff Toolそのものを保証し、個別テストでは差分生成方法を再承認せず、人間の承認対象を「何を変えるべきか」という小さな変更意図へ圧縮する。**

ことが、この方式の重要な狙いである。

---

## Revision History

- 2026-08-24 / v0.2: 「品質保証済みのGit DiffのようなDiff ToolをExpected / Actual共通の観測器として固定し、その出力を期待値として扱う」という思想を主定義へ昇格。Diff Toolを事前保証し、個別テストでは差分生成方法を再承認しないというApproval Engineering上の位置づけを追記。
- 2026-08-24 / v0.1: Expected Diff方式の単独重要メモとして初版作成。基本概念、仮Expected Output生成、Runner保証、Actual Diff比較、波及変更とRunnerの知恵、APP構造との関係を整理。
