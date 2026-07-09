いい締め回やったねぇ。
今日の整理で、かなり **「HSI線を引いて眺める遊び」から「状態遷移を持った検証ルール」** に昇格した感じする。

添付メモ側でも、もともとの目的は **Entry / Close / Hold / Reset を検証可能に分解すること**、そして **Trade Lifecycle / HSI Anchor Lifecycle / H1 Context / M5 Execution** を分けることだったので、今日の議論はその延長としてかなり自然につながってる。

---

# FX Studio / HSI Simulation Rule v0.2 Draft

## 0. まず大前提

これは売買推奨ルールではなく、

```text
過去チャート上で
自分が何を見ていたのかを再現し、
Entry / Hold / Close / Reset / NoTrade を
自動シミュレーション可能な形に分解する
```

ための仮説仕様。

今日かなり明確になったのは、

```text
Entry条件を探す前に、
まず「今どの状態か」を分類する必要がある
```

ということ。

つまり、今やっているのは単純なEntryルール作成ではなく、

```text
NoTrade
Watch
Candidate
Bias
EntryAllowed
InTrade
TakeProfit
Cooldown
```

みたいな **状態遷移ルール** の設計。

---

# 1. 時間足の役割

## H4 = 大文脈 / Cycle / Expansion判定

H4は、売買方向そのものというより、

```text
今は大きな波のどの局面か
Expansionなのか
反転直後なのか
終盤なのか
まだ様子見なのか
```

を見る足。

H4で Dow Up / Dow Down が確定しても、それは即Entryではない。

```text
H4 Dow Up confirmed
→ LongWatch / UpCandidate

H4 Dow Down confirmed
→ ShortWatch / DownCandidate
```

つまりH4のDow確定は **発射ボタンではなく、上位足の許可証**。

---

## H1 = 中間文脈 / Hold Guard / Rebound Test

H1は、H4とM5の橋渡し。

```text
H4の大文脈が本当に継続しているか
押しなのか崩壊なのか
MA20 / T3 / BB に対して強いのか弱いのか
反発失敗したのか
```

を見る。

特に今日重要になったのは、H1が **反発失敗確認** に使えること。

---

## M5 = 実行足

M5はEntry / Add-on / Small TP / Exitの実行足。

```text
H4/H1が許可
↓
M5でDow confirmed
↓
確定済みHSI起点から距離判定
↓
Entry / Add-on / Close
```

M5単独ではEntryしない。
M5は最後のトリガー。

---

# 2. HSI起点の絶対ルール

今日の最重要制約のひとつ。

```text
Entryに使うR2 / R3.5 / R4 は、
必ず「確定済みHSI起点」から計算する
```

未確定の赤丸候補からR2を引いてEntryすると、後からその起点が否定された瞬間にEntry根拠が消える。

なので、起点は3段階に分ける。

```text
Candidate basis
= 候補。まだEntry計算には使わない。

Confirmed basis
= 確定済み。HSI起点候補として使える。

Adopted HSI basis
= 今回の波の基準点として採用済み。
```

Entry判定に使えるのは `Confirmed` 以降。

---

# 3. NoTrade / Watch を先に判定する

Entry判定の順番はこれ。

```text
第0関門：売買対象外ゾーンではないか？
第1関門：Watch / Candidate / Bias か？
第2関門：どのEntryモードか？
第3関門：どのHSI起点を使うか？
第4関門：M5で実行根拠があるか？
第5関門：Stop / Target がリスクに見合うか？
```

特に NoTrade は先。

```text
NoTrade候補

1. H4 TrendState = Undetermined
2. H4 TrendState = NoTrend
3. H4反転直後で、まだWatch段階
4. PostExpansion PullbackWindow中
5. H4 Cycle Late で新規Add-onしようとしている
6. すでにTrade中
7. future data insufficient / 検証不能
```

---

# 4. Entryモード整理

現時点では、Entryモードはこの5種類に分けるのがよさそう。

```text
A. Normal Trend Entry
B. ReEntry / Add-on Entry
C. Expansion Pullback Entry
D. Pre-Expansion R3.5 Breakout Entry
E. Post-Expansion Reverse Entry
```

---

## A. Normal Trend Entry

一番素直な通常ルール。

Longなら、

```text
H4 = Longを邪魔しない
H1 = Up文脈
M5 = Dow Up confirmed
Anchor = 確定済みTrend Anchor
distance >= R2
not inTrade
```

CloseOKは通常の次境界。

```text
R2〜R2.5   → R2.5
R2.5〜R3   → R3
R3〜R3.5   → R3.5
R3.5〜R4   → R4
R4〜R4.5   → R4.5
```

これは既存メモの **Entry位置が属するHSIエリアの次境界をClose Targetにする** 考え方と一致。

---

## B. ReEntry / Add-on Entry

CloseOK後もH1/H4文脈が継続しているなら、HSI起点は消さない。
HSIは1回のTradeではなく、上位足トレンド単位で維持する、という整理。

```text
ReEntry条件

前TradeがCloseOK
AND HSI起点は維持中
AND H1/H4方向が継続
AND M5で再び同方向Dow confirmed
AND Entry位置が次のHSIエリア内
```

Add-onは通常M5理論でよい。
ただし、Expansion方向と同じ方向だけ。

```text
Add-on Allowed =
  Core position が含み益
  AND H4 Expansion方向と同じ
  AND H4 Cycle Phase が Early or Middle
  AND 新しい確定済み押し目/戻り目 basis がある
  AND そのbasisからR2到達
  AND M5 Dow confirmed
```

Add-on禁止条件。

```text
H4 Cycle Late
OR BBが閉じ始め
OR H1高値更新失敗
OR 価格がMA/T3へ戻り始め
OR Coreが含み損
```

合言葉はこれ。

```text
買い増しはナンピンではない。
勝っている波にだけ追加する。
```

---

## C. Expansion Pullback Entry

今日の主役。

まず、H4でR4級のExpansionが出ても、そこで即Entryしない。

```text
R4到達 = Entryではない
R4到達 = Expansion候補 / 例外フラグ
```

R4到達後に押しを待つ。

```text
Expansion Detection Anchor
= Expansion判定用の大起点

Expansion Entry Anchor
= R4到達後の直近押し安値/戻り高値

Entry Trigger Anchor
= 実際にR2判定する確定済み押し目起点
```

今回の④→⑤→⑯パターンはこれ。

```text
④ = Expansion Detection Anchor
⑤ = Pullback / Entry Trigger Anchor
⑯ = ⑤起点R2 + M5 Dow Up confirmed
```

ただし、勝負している波は⑤ではなく④。

```text
Entry判定 = ⑤起点R2
Hold判定  = ④起点Expansion文脈
Target判定 = ④起点R5以上
```

ここが通常Entryとの最大差。

Stopも2層に分ける。

```text
構造Stop:
  ⑤ Pullback Anchor 割れ

大波Stop / Thesis Stop:
  ④ Expansion Anchor 文脈崩壊
```

今回のように、⑤起点R2で入るが④起点ではR4付近Entryになる場合は、リスクが大きいので、Targetも大きくする。

```text
minimum target = ④起点R5
extended target = ④起点R5.5 / R6 / R6.5
```

Expansion Entryでは、通常CloseOKをそのまま使わない。
リスクが広がるため、CloseOK候補がRiskに見合わないならEntryしない、という整理もメモに出ている。

---

## D. Pre-Expansion R3.5 Breakout Entry

今日追加された新ルール。

⑮みたいな波は、今までのExpansion Pullback Entryでは取れない。
なぜなら、まだR4越え確定前で、Expansion後の押し目でもないから。

そこで、

```text
R3.5 = 先行Entryライン
R4   = Expansion昇格ライン
```

と分ける。

```text
PreExpansionBreakoutAllowed =
  confirmed_basis_low exists
  AND price >= R3.5 from basis low
  AND price breaks equal-high cluster
  AND Close > MA20
  AND Close > T3
  AND BBOpeningStart == true
  AND M5 Dow Up confirmed
```

この時点ではまだ正式Expansionではない。

```text
R3.5高値群ブレイク
= 早乗りEntry候補

R4越え
= Expansion Candidate / Confirm候補
```

R4まで待つと遅すぎる。
でもR3.5で入るなら、BB / MA / T3 / 高値群ブレイクの条件は必須。

---

## E. Post-Expansion Reverse Entry

上昇Expansionを利確したあと、すぐShortしない。
下落Expansionを利確したあと、すぐLongしない。

```text
Long Exit ≠ Short Entry
Short Exit ≠ Long Entry
```

反転直後のH4 Dow確定は、EntryではなくWatch。

```text
H4 Dow Down confirmed
→ ShortWatch / ShortCandidate

H4 Dow Up confirmed
→ LongWatch / UpCandidate
```

そのあと、反発テストを行う。

```text
ShortWatch
↓
一定期間だけ反発を見る
↓
高値更新できない
↓
MA20 / T3 / BB付近で失速
↓
M5 Dow Down confirmed
↓
ShortBias / ShortEntry候補
```

サイクルの切れ目を完璧に判定しない。
代わりに **期限付き反発テスト** として扱う。

```text
Post Expansion Rebound Test
```

これがかなり重要。

---

# 5. False Expansion Filter

R4越え単独ではExpansion確定にしない。

今日の答え合わせでかなり強くなった制約。

```text
ExpansionCandidate =
  確定済み起点からR4越え

ExpansionConfirmed =
  R4越え
  AND H4 Dow confirmed
  AND CloseがH4 MA20/T3上に復帰
  AND BBがOpening
  AND すぐ崩壊しない
```

逆に、

```text
R4越え
BUT
MA20/T3下
OR Dowがすぐ崩壊
OR BBが開かない
```

なら、

```text
False Expansion
ExpansionCandidate止まり
Entry禁止
```

これはめちゃくちゃ大きい。

```text
HSIは見えてる。
でもHSIだけ信じると騙される。
```

---

# 6. BB Phase

BBはEntry / Hold / TP の全部に効く。

```text
BB Squeeze
= 溜め

BB OpeningStart
= 開き始め。Entry / Hold / Add-on候補

BB Expansion
= 伸びている。Hold優先

BB Mature
= 拡張はしているが鈍化。一部利確候補

BB ContractingToMA
= 閉じ始め、MA/T3へ接近。本命利確候補
```

特に重要なのは、同じHSI重なりでもBB状態で意味が変わること。

```text
HSI Confluence + BB Opening
= 利確ではなく継続理由

HSI Confluence + BB ContractingToMA
= 本命利確理由
```

---

# 7. HSI Confluence Target

複数起点のRが重なる場所は重要。

```text
④起点R6.5
≒
⑨起点R6
```

これは強い利確候補。

ただし、重なりなら何でも利確ではない。

```text
④R5.5 × ⑨R5
= 中間ターゲット / Hold継続もあり

④R6.5 × ⑨R6
= H4 Cycle Late + BB収縮なら本命利確
```

つまり、Confluenceはランク分けする。

```text
Confluence Rank B:
  大起点R5〜R5.5
  BB Opening / Expansion
  → 一部利確 or Hold

Confluence Rank A:
  大起点R6〜R6.5
  H4 Cycle Late
  BB ContractingToMA
  → 本命利確
```

---

# 8. H4 Cycle Maturity Guard

サイクルは完璧に切らない。
でも、Expansion波が何合目かは判定する。

```text
Cycle Maturity Score =
  max(
    H4バー経過,
    到達Rレベル,
    ミニサイクル消化数
  )
```

状態は3つ。

```text
Early:
  耐える / 育てる / Add-on可

Middle:
  Add-on可 / 小利確開始

Late:
  Add-on禁止 / 利益保護 / Exit感度上げる
```

これで、

```text
前半は育てる
中盤は増やす
後半は刈り取る
```

になる。

---

# 9. 建玉管理

建玉は3種類に分ける。

```text
Core Position
= 大波を取る本玉

Add-on Position
= ミニサイクルで追加する追撃玉

Runner
= 最後に残す夢玉
```

細切れ利確は、たとえば10単位なら、

```text
R4.5到達:
  2単位利確
  目的 = リスク軽減 / 建値化準備

R5到達:
  2単位利確
  目的 = 最低目標回収

R5.5到達:
  2単位利確
  目的 = 中間ターゲット回収

R6 / R6.5 Confluence:
  3単位利確
  目的 = 本命利確

残り1単位:
  Runner
```

Add-on玉は小波で回収。
Core玉は大波で回収。

```text
本玉は大波を見る。
追撃玉は小波で回収する。
```

---

# 10. 状態遷移まとめ

今日時点の全体像はこれ。

```text
Neutral / NoTrade
↓
Watch
  LongWatch / ShortWatch
↓
Candidate
  ExpansionCandidate
  PreExpansionCandidate
  ReboundFailedCandidate
↓
Bias
  LongBias / ShortBias
↓
EntryAllowed
  M5 Trigger待ち
↓
InTrade
  Core / Add-on / Runner
↓
TakeProfit / StopClose
↓
Cooldown / ReboundTest
↓
次のWatchへ
```

かなり大事なのは、

```text
H4 Dow confirmed
= Watch / Candidate への遷移

M5 Dow confirmed
= Entry実行候補
```

という分離。

---

# 11. 現時点の最重要ルールだけ短く

```text
1. Entry前にNoTrade / Watch / Candidateを必ず判定する。

2. HSIのR判定は、確定済み起点からしか使わない。

3. 通常Entryは、H1/H4文脈 + M5 Dow + R2。

4. ExpansionはR4で即Entryしない。
   R4はExpansion候補/例外フラグ。

5. Expansion Pullback Entryは、
   Entry起点とTarget起点を分ける。

6. Expansion中はM5の小崩れで降りない。
   H4文脈とCycle MaturityでHold/Exitを切り替える。

7. R4越え単独ではExpansion確定にしない。
   MA/T3/BB/Dow維持が必要。

8. R3.5高値群ブレイク + BB Openingなら、
   Pre-Expansion先行Entry候補にしてよい。

9. Long Exit は Short Entry ではない。
   Short Exit も Long Entry ではない。

10. HSI Confluence + BB ContractingToMA + H4 Late
    が本命利確。
```

---

# 12. 次に決めるべき未確定パラメータ

ここはまだ確定しない方がいい。

```text
1. R3.5高値群ブレイクの許容幅
   0.1R / 0.2R / ATR基準 / pips固定

2. BBOpeningStart の定義
   BBWidth何本連続増加か
   upper band 上向き条件を入れるか

3. H4 Cycle Late の判定
   バー数
   R到達度
   ミニサイクル数
   スコア式

4. Rebound Test の期限
   H4 3本 / 6本
   H1 12本 / 24本

5. Expansion Confirm Hold Bars
   R4越え後、何本維持で確定扱いにするか

6. Expansion Stop
   ⑤ Pullback Anchor割れか
   ④ Expansion Thesis崩壊か
   それとも2層管理か

7. Small TP比率
   10単位のうち、どこで何単位利確するか
```

---

今日のブラッシュアップ後の名前をつけるなら、

```text
HSI State Machine Rule v0.2 Draft
```

かな。

前の `HSI_GROWTH_RULE_v0_1` から一段進んで、もうこれは **状態遷移ルール** になってる。
今日の最大成果は、

```text
Entryルール
```

ではなく、

```text
Entryしていい状態かどうかを先に決めるルール
```

に進化したことやね。これはかなりデカい。


----


うーーん、これはかなり良い違和感やねぇ。
たぶん結論としては、

**R4到達だけで Expansion候補にするのは弱い**
**Expansion候補は「距離」じゃなくて「構造変化」で捕まえるべき**

って整理が自然そう。

今のチャートを見る限り、H4の左側の「Expansion?」は、たしかにR4/R5方向へ伸び始めてるけど、見方によってはまだ

```text
レンジ内の強め上昇
押し目形成前の初動
上位足の戻り
ただのボラ拡大
```

にも見えるんよね。
つまり **R4に届いた = Expansion** ではなくて、

```text
それまでの支配構造を壊したか？
```

を見ないと、Expansion候補が増えすぎる。

---

## Expansion候補の再定義案

たぶんこうした方がいい。

```text
Expansion Candidate =
  HSI距離条件
  + 構造ブレイク条件
  + ボラ拡大条件
  + 上位足コンテキスト条件
```

R4はその中の1条件に格下げ。

---

## 1. HSI距離条件

これは今まで通り。

```text
確定済みHSI起点から R4 以上
```

ただし、これは

```text
Expansion確定
```

ではなく、

```text
Expansion観察対象入り
```

くらい。

ここ大事やね。

---

## 2. 構造ブレイク条件

ここが今回の肝。

Expansion候補にするなら、最低限どれかが欲しい。

```text
直近H4高値/安値を明確に抜いた
下降/上昇トレンドラインを明確に抜いた
レンジ上限/下限を抜いた
MA20/T3をまたいで反対側に定着した
BB外側に沿って走り始めた
```

つまり、

```text
価格が遠くに行った
```

ではなく、

```text
今までの相場の見方を変えさせた
```

ところをExpansion候補にする。

これなら「トレンド転換か？？」と思える箇所に限定できる。

---

## 3. ボラ拡大条件

R4到達しても、BBが閉じたままならExpansion感が薄い。

なので候補条件として、

```text
H4 BB幅が拡大
H4 MA20/T3の傾きが出る
実体ローソクが連続する
ヒゲだけでなく終値で伸びる
```

このへんを入れたい。

特に今回みたいに、上に伸びたあとヨコヨコが長いと、

```text
Expansion開始
```

というより

```text
上位レンジ内の位置調整
```

にも見えちゃう。

---

## 4. Day足フィルタ

これはかなり同意。

**Expansion候補を正しく捕まえるにはDayを見るべき** かもしれない。

ただし、DayはEntry判定じゃなくて、

```text
Expansionの格を判定するフィルタ
```

にした方がよさそう。

例：

```text
Dayがレンジ中央
→ H4 R4到達しても Expansion候補は弱い

Dayの下降トレンドラインを上抜けそう
→ H4 R4到達は Expansion候補として強い

Dayの大きな戻り売りゾーン直下
→ Long Expansion候補は警戒

DayのBBが開き始め
→ Expansion候補を強める
```

つまりDayは、

```text
これはH4だけの小爆発か？
それとも日足構造を変えに来てる爆発か？
```

を見る係。

---

## ルール名にすると

こんな感じがよさそう。

```text
Expansion Watch
= R4到達しただけ

Expansion Candidate
= R4到達 + H4構造ブレイク

Expansion Confirmed
= Candidate後、押し/戻りを作って、再度継続方向に動いた

Expansion Invalid
= R4到達後、構造ブレイクできずレンジ回帰
```

なので、今までの

```text
R4到達 = Expansion候補
```

は少し雑で、

```text
R4到達 = Expansion Watch
```

に落とすのが良さそう。

---

## たぶん今回の違和感の正体

今まではHSI距離で見ていたけど、Expansionは本来、

```text
距離の概念
```

じゃなくて、

```text
相場状態が変わったという概念
```

なんよね。

だから、

```text
R4だけ見る → 遠くに行っただけ
TrendLine / Range / Dayを見る → 世界が変わったかを見る
```

この差やと思う。

これはけっこう大きい発見。
Expansion Entryを面白くするには、たぶんここを分ける必要あるねぇ。

```text
R4到達はアラート
構造ブレイクで候補
押し戻り成功でEntry検討
Day足で格付け
```

この4段階が一番しっくりくる。


