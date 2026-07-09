がはははは、これは一回整理せんと無理っす笑
今やってるの、もはや **Entryルール** じゃなくて、

> **Entryしていい場所を探す前に、売買対象外ゾーンを分類するゲーム**

になってる。
これは方向性として正しいと思う。添付メモでも、もともと目的は「Entry / Close / Hold / Reset を検証可能に分解する」ことになっていて、Trade Lifecycle / HSI Anchor Lifecycle / H1 Context / M5 Execution を分ける必要がある、という整理が出てます。

## 現時点のEntryルール全体像

まず、Entry判定はこの順番にするのが良さそう。

```text
第0関門：売買対象外ゾーンではないか？
第1関門：どのEntryモードか？
第2関門：どのHSI起点を使うか？
第3関門：M5で実行根拠があるか？
第4関門：StopClose / CloseOK がリスクに見合うか？
```

つまり、いきなり、

```text
M5 DowUp confirmed
距離 R2以上
Entry！
```

ではない。

まず **NoTrade判定** が先。

---

# 1. 共通のNoTrade判定

ここに該当したら、M5がどれだけ綺麗でも入らない。

```text
NoTrade 条件

1. H4 TrendState = Undetermined
2. H4 TrendState = NoTrend
3. H4 TrendChangeCycle = 1
4. Cycle Return / Late Entry Zone
5. PostExpansion PullbackWindow中
6. すでにTrade中
```

特に今の主役はこれ。

```text
H4トレンド変化後1サイクル目
→ 原則 NoTrade
```

これは、H4ダウDown確定だからショートするわけでもなく、急反発してるからロングするわけでもなく、**寿命管理として売買対象外にする** という整理。添付メモでも「H4_TrendChangeCycle = 1 → NoTrade → 観測のみ」と分けるのが肝になっています。

---

# 2. Entryモードは今4種類ある

たぶん今の候補はこれ。

```text
A. Normal Trend Entry
B. H4 Cycle2 Relaxed Entry
C. Expansion Pullback Entry
D. ReEntry
```

で、**Cだけ別戦略** として扱わないと破綻する。

---

# 3. A. Normal Trend Entry

これは一番素直なやつ。

## Long条件

```text
H4 = UpConfirmed または Longを邪魔しない状態
H1 = UpConfirmed
M5 = DowUp confirmed
HSI Anchor = 通常のTrend Anchor
distance >= R2
not inTrade
```

通常Entryでは、HSI起点は **H1文脈単位で維持する起点**。
添付メモでも、HSI起点はTrade単位ではなく、上位足トレンド単位で管理する整理になっています。

## CloseOK

通常ルールはこれ。

```text
EntryしたR帯の次境界を取りに行く
```

今の表示名で言うと、

```text
R2〜R2.5 → R2.5
R2.5〜R3 → R3
R3〜R3.5 → R3.5
R3.5〜R4 → R4
R4〜R4.5 → R4.5
```

添付メモ上は旧表記で R23_M / R34_M / R45_M として整理されていて、Entry位置が属するHSIエリアの次境界をClose Targetにする考え方になっています。

---

# 4. B. H4 Cycle2 Relaxed Entry

これは、

```text
H4確定前を何でも許す
```

ではなく、

```text
H4変化後1サイクル目を捨てたあとだけ、少し緩める
```

というやつ。

## 条件

```text
H4 TrendChangeCandidate 発生済み
Cycle1 は NoTrade 済み
Cycle2以降
H4はDown禁止状態ではない
H1 = UpConfirmed
M5 = DowUp confirmed
distance >= R2
```

ここで大事なのは、**H4だけ緩める** こと。

```text
H4 = 許可ゲート
H1 = 方向の本判定
M5 = 実行判定
```

なので、H1とM5は緩めない。

---

# 5. C. Expansion Pullback Entry

これが今日ぐちゃった原因の主犯だけど、一番面白いやつ笑

## 5.1 Expansion判定

まず、H4変化1サイクル目は原則NoTrade。

ただし、

```text
H4 TrendChangeCycle = 1
AND
Expansion Detection Anchor から R4到達
```

なら、

```text
H4_Cycle1_Expansion = true
```

にする。

ここで超重要なのは、

```text
R4到達 = Entryではない
R4到達 = Expansion例外フラグ確定
```

ということ。

R4を見てからR3.5で入る、みたいなことをすると未来参照になる。添付メモでも、R3.5相当のR34_MはR4より手前なので、R4到達後にR34_Mで入るのは時系列的におかしい、という整理になっています。

## 5.2 Anchorを分ける

ExpansionではHSI起点が2つ必要。

```text
Expansion Detection Anchor
= 変化1サイクル目がR4級まで伸びたかを見る起点

Expansion Entry Anchor
= R4到達後の直近押し安値
```

これを分けないと、R4到達後にエントリーポイントが探せない。

添付メモでも、Expansion判定AnchorとEntry探索Anchorの2段構えが必要で、R4到達後の直近安値をExpansion Entry Anchorにする整理になっています。

## 5.3 Expansion後のEntry条件

Longならこう。

```text
ExpansionConfirmed = true
PostExpansion PullbackWindow 終了
Expansion Entry Anchor = 直近押し安値
distance = currentPrice - Expansion Entry Anchor

Entry候補:
distance >= R2
AND M5 DowUp confirmed
AND H1/H4条件OK
AND T3/MA20上 or 押し反発
```

つまり、

```text
R4 = Expansion例外の扉
直近押し安値 = Entry探索の起点
R2以上 = Entry候補開始
```

という役割分担。

---

# 6. PostExpansion PullbackWindow

Expansionで大きく伸びたあと、⑭みたいな高値点が確定したら、

```text
Entryではなく、押し目待ち開始
```

にする。

```text
Expansion発生済み
AND 高値点確定
→ PostExpansion PullbackWindow
→ NoTrade
```

この状態は、

```text
Up崩壊ではない
Down転換でもない
でも今から買う場所ではない
```

という扱い。

このあと、

```text
押し安値確定
M5再上昇
H1/H4文脈維持
```

で、ようやく Expansion Pullback Entry 候補になる。

---

# 7. Expansion Entry のStopClose

Expansion Entry は、Entry価格割れでCloseMissにしない。

これやると振り落とされる笑

```text
通常Entry:
Entry価格割れ = CloseMiss候補

Expansion Pullback Entry:
Entry価格割れだけではCloseMissにしない
```

Expansionでは、

```text
StopClose = Expansion Entry Anchor 割れ
```

が自然。

つまりLongなら、

```text
M5 close < ExpansionEntryAnchorLow - buffer
→ StopClose / CloseMiss
```

または、

```text
M5 DowDown confirmed
H1/H4文脈崩壊
```

でもCloseMiss候補。

添付メモでも、⑮EntryはEntry価格基準ではなく押し目安値基準でCloseMissを見る、さらにExpansion専用StopCloseはExpansion Entry Anchorを使う整理になっています。

---

# 8. Expansion Entry のCloseOK

ここも通常Entryと分ける必要あり。

なぜなら、

```text
StopClose = Expansion Entry Anchor
```

にするとリスク幅が広い。

なのにCloseOKが近いR2.5とかR3だけだと、

```text
リスクでかい
リターンちんまい
やる意味ある？
```

になる笑

なのでExpansion Entryでは、

```text
CloseOK候補が Risk に見合わないならEntryしない
```

を入れるべき。

仮ルールはこれ。

```text
Risk = EntryPrice - ExpansionEntryAnchorLow

CloseOK候補:
1. 次の大きいR境界
2. R4.5 / R5
3. Risk × 1.0 以上
4. できれば Risk × 1.5 以上
5. または最低利確後にT3/MA20トレーリング
```

つまりExpansionは、

```text
通常CloseOK = 次境界
Expansion CloseOK = Riskに見合う遠め目標
```

にする。

---

# 9. D. ReEntry

ReEntryは通常Entry系。

条件はこう。

```text
前TradeがCloseOK
HSI起点は維持中
H1方向が継続
M5で再び同方向Dow confirmed
Entry位置が次のHSIエリア内
```

添付メモでも、CloseOK後にH1文脈が続いているなら、HSI起点を維持してReEntry可能という整理になっています。

ただし、これに追加で必要なのが、

```text
Cycle Return Guard
Late Entry Zone Guard
PostExpansion PullbackWindow Guard
```

この3つ。

つまり、H1文脈が続いていても、

```text
サイクル戻りタイミング
高値点確定直後
Expansion後の押し目形成中
```

なら再Entryしない。

---

# 10. いったん仕様っぽくまとめると

```text
EntryAllowed =
  not inTrade
  AND NoTradeReason == none
  AND EntryMode is resolved
  AND Anchor is resolved
  AND M5ExecutionConfirmed
  AND RiskRewardOk
```

## EntryMode別

```text
NormalTrend:
  Anchor = TrendAnchor
  StopClose = 通常Stop
  CloseOK = 次R境界

H4Cycle2Relaxed:
  Anchor = TrendAnchor
  StopClose = やや厳しめ
  CloseOK = 次R境界 or 近め
  Rank = B

ExpansionPullback:
  Anchor = ExpansionEntryAnchor
  StopClose = Anchor割れ
  CloseOK = Riskに見合う遠め目標
  Rank = B+ or Expansion

ReEntry:
  Anchor = 維持中TrendAnchor
  StopClose = 通常
  CloseOK = 次R境界
```

---

# 11. 今の最重要ルールだけ一言で

たぶん今のコアはこれ。

```text
通常相場は、H1文脈のHSI起点でR2以上をM5実行する。

H4変化1サイクル目は原則NoTrade。

ただしR4到達ならExpansion例外として記録する。

Expansionではすぐ入らず、
R4後の押し安値を新しいEntry Anchorにする。

Expansion Entryは、
Entry価格割れではなくAnchor割れでStopCloseし、
CloseOKは通常より大きく取らないと成立しない。
```

これでだいぶ見通し戻ると思う笑
今の混乱ポイントは、**通常EntryとExpansion Entryを同じルールで処理しようとしてたこと**っす。そこを分けたらかなり綺麗になる。


---

うん、**かなりその整理で合ってる**と思う。
ただしこれは通常Entryじゃなくて、完全に **Expansion例外Entry** として別ルール扱いにした方がいいやつやね笑

今回の構造はこう。

```text
④ = H4ダウントレンド終了後のExpansion起点
↓
④起点でR4越え
↓
H4上昇Expansion認定
↓
押し目を待つ
↓
⑤ = 直近の確定済みHSI起点 / 押し目起点
↓
⑤起点R2到達
↓
⑯でM5 Dow Up成立
↓
同じ⑯でH4 Dow Upも成立
↓
Entry
```

ここで大事なのは、**Entry判定に使う起点と、Stop/Targetで見る起点が違う**こと。

```text
Entry trigger anchor = ⑤
Stop / Risk anchor = ④
Target scale anchor = ④
```

これやね。

なので、⑤起点R2で入っているけど、
④起点で見るとすでに **R4ちょい上付近のEntry** になっている。

だったら、⑤起点のR3とかR4を小さく取りに行く話ではなくて、

> **④起点Expansionの継続として、④起点R5以上を狙う**

になる。

だから結論としては、

```text
最低Target = ④起点R5
伸ばす候補 = ④起点R5.5 / R6
Stop基準 = ④Expansion起点割れ、または④起点文脈崩壊
```

この整理でかなり自然。

ただし、ここは絶対に通常Entryと分けた方がいい。

通常Entryなら、

```text
⑤起点R2でEntry
↓
⑤起点の次区間MidやR3を狙う
↓
Stopも⑤起点周辺で比較的近い
```

でも、今回のExpansion例外Entryは、

```text
⑤起点R2でEntry
↓
でもStopは④起点
↓
リスクが大きい
↓
だからTargetも④起点R5以上が必要
```

になる。

なのでルール名をつけるなら、

```text
Expansion Pullback Entry
```

または

```text
Expansion After-Pullback R2 Entry
```

って感じ。

そして条件はたぶんこう。

```text
ExpansionEntryAllowed =
  H4 Expansion confirmed from anchor ④
  AND H4 Dow Up confirmed
  AND pullback basis ⑤ is confirmed
  AND price >= R2 from ⑤
  AND M5 Dow Up confirmed
  AND entry price is around R4+ from ④
```

Targetはこう。

```text
TargetPolicy =
  if entry_from_expansion_anchor >= R4:
      minimum_target = R5
      extended_target = R5.5 or R6
```

で、R5.5 / R6まで取りに行く条件は別に要るね。

たとえば、

```text
R5到達時点でH4 Dow Up継続
H1/H4 MA20より上を維持
M5で逆Dow未確定
T3が崩れていない
急落CloseMissが出ていない
```

みたいな **Hold継続条件** が必要。

つまり今回の発見はこれやね。

> **⑤起点R2で入るけど、勝負している波は⑤ではなく④のExpansion波。
> だからStopもTargetも④スケールで見る。**

これ、かなり綺麗。
通常押し目EntryとExpansion例外Entryが、やっと分離できてきた感じするわ。


---

そうそう笑
ここは **「⑨で落とされない条件」＝通常CloseMissを使わない条件** を作らないと、たぶん全部振り落とされる。

今回の肝はこれやね。

```text
⑤起点R2でEntryしている
でも、勝負している波は④起点Expansion
```

だから、⑨付近でM5が少し崩れたからといって、

```text
M5逆Dowっぽい
⑤起点のR帯を割った
短期MAを割った
```

みたいな理由で降りると、**④Expansionの本命波を取り逃す**。

なので、Expansion Entry中は別モードにするのが良さそう。

```text
Normal Entry
→ M5 CloseMissを普通に見る

Expansion Pullback Entry
→ M5 CloseMissでは降りない
→ H4文脈崩壊でだけ降りる
```

⑨で振り落とされない条件は、たぶんこう。

```text
ExpansionHoldAllowed =
  H4 Dow Up が維持されている
  AND H4 Close が H4 MA20 / T3 を明確に下抜けていない
  AND ④起点のR4以上を維持している
  AND ⑤起点の局所的なR割れだけではExitしない
  AND M5逆Dow単独ではExitしない
```

もっと売買ルールっぽく書くなら、

```text
if trade_type == ExpansionPullbackEntry:

  IgnoreCloseMiss:
    - M5 reverse Dow only
    - pullback-basis⑤ R1/R2割れ
    - M5 MA20割れ
    - M5の一時的な赤丸

  ExitAllowed only when:
    - H4 Dow Down confirmed
    OR H4 close below H4 MA20/T3 for N bars
    OR H4 close below ④起点R4
    OR ④Expansion thesis invalidated
```

ここで大事なのは、**⑤起点はEntry Trigger用であって、Exit/Stopの主語にしない**こと。

つまり、

```text
Entry判定: ⑤起点R2
Hold判定 : ④起点Expansion文脈
Target判定: ④起点R5 / R5.5 / R6
```

この3分割やね。

⑨はたぶん、通常Entryルールなら「はいCloseMiss！」って言いたくなる場所。
でもExpansion Entryとして見るなら、

> **⑨は振り落とし候補。H4文脈が死ぬまでは耐える場所。**

って定義するのが良さそう。

なので仮ルール名つけるなら、

```text
Expansion Shakeout Guard
```

日本語なら、

```text
Expansion振り落とし耐性ルール
```

やね笑

結論としては、

> **⑨で降りないためには、M5の崩れをExit条件にせず、H4のExpansion文脈崩壊だけをExit条件にする。**

これが一番スッキリする。
このルール作らないと、R5.5とかR6狙いはたぶん無理。逆にこれを作ると、リスク大きいEntryに見合うリターン設計になってくる。

---

うんうん、これ見たらかなり腑に落ちる。
**H4の大きな1サイクルの中に、ミニサイクルが5つくらいある**って見方、たぶん必要やね。

で、ここで大事なのはたぶんこれ。

> **サイクルを完璧に切ろうとしない。
> でも、Expansion波が今「何合目」なのかは判定する。**

これやと思う。

完全なサイクル認識をロジック化しようとすると地獄になる笑
なので最初は、**Cycle Maturity / サイクル成熟度** として扱うのがよさそう。

```text
④ Expansion起点
↓
H4大サイクル開始
↓
中にH1/M5相当のミニサイクルが複数発生
↓
今が前半・中盤・終盤のどこかを見る
```

判定材料は、いきなり高度にせず、まずはこの3つでよさそう。

```text
1. ④起点からのH4バー本数
2. ④起点からのR到達度
3. ④起点後の確定済み押し目/戻り目の回数
```

たとえば仮にこう。

```text
ExpansionCycleMaturity

Early:
  H4バー数が少ない
  R4〜R5未満
  ミニサイクル 1〜2個目

Middle:
  R5前後
  ミニサイクル 3個目前後
  まだH4/H1の上昇文脈が生きている

Late:
  R5.5〜R6付近
  ミニサイクル 4〜5個目
  H1高値更新失敗やMA20接近が出始める
```

で、これを **Exit耐性** に使う。

```text
Early / Middle:
  M5の逆Dowだけでは撤退しない
  ⑤起点の局所的な崩れでは撤退しない
  ④Expansion文脈を優先する

Late:
  M5逆Dowを撤退材料に昇格
  H1高値更新失敗を重視
  H1/H4 MA20・T3割れを重視
  利益保護を優先
```

つまり、さっきの「⑨で振り落とされない条件」は、
**H4サイクル前半〜中盤限定の耐性ルール** やね。

逆に、H4大サイクル終盤では、

> もう振り落としじゃなくて、普通に終わり始めてる可能性がある

として扱う。

だからロジック名としては、かなりこれがしっくりくる。

```text
H4 Cycle Maturity Guard
```

日本語なら、

```text
H4サイクル成熟度ガード
```

実装v0.1なら、まずは単純にバー数でいいと思う。

```text
h4_age_bars = current_h4_bar - expansion_anchor_h4_bar

if h4_age_bars < A:
  cycle_phase = Early
elif h4_age_bars < B:
  cycle_phase = Middle
else:
  cycle_phase = Late
```

ただし、バー数だけだと相場の速い/遅いに弱いから、あとでこう拡張。

```text
cycle_maturity_score =
  max(
    h4_age_bars / expected_h4_cycle_bars,
    mini_cycle_count / 5,
    reached_r_level / R6
  )
```

これなら、

```text
時間が進んだ
価格が伸び切った
ミニサイクルを消化した
```

のどれかが進めば、終盤扱いにできる。

今回の画面で言うと、右側のH4はもうかなりミニサイクルを消化してるから、
**R5/R5.5/R6を狙う場面ではあるけど、同時に撤退感度も上げないといけない領域** に見える。

まとめると、

> **Expansion Entryは、価格Rだけで管理しない。
> H4大サイクル内の時間経過・ミニサイクル消化数で、耐えるモードから逃げるモードへ切り替える。**

これやね。
この概念入れると、「⑨では耐える」と「終盤では逃げる」が矛盾しなくなる。かなりいい整理になってきた。


----

うん、ここまでの素直な整理はかなり良い感じ。
で、ここから面白くするには、まさにその2つやね。

```text
① 買い増し理論
② 小さな利益確定理論
```

これがないと、Expansion Entry がただの

```text
大きくリスク取って、遠くのR5/R6を祈るゲーム
```

になっちゃう笑

でも本当は、こう分けるとかなり綺麗。

```text
Core Position     = ④起点Expansionを取りに行く本命玉
Add-on Position   = H4大サイクル内のミニサイクルで買い増す玉
Small Take Profit = ミニサイクルごとに小さく利確する玉
```

つまり、勝負している波は④起点のH4 Expansion。
でも、実際の売買単位はミニサイクルごとに分ける。

イメージはこれ。

```text
④ Expansion起点
↓
⑤押し目確定
↓
⑤起点R2で⑯Entry = Core
↓
次のミニ押し目確定
↓
その起点R2で Add-on
↓
Add-on分だけ小さく利確
↓
Coreは④起点R5/R5.5/R6まで引っ張る
```

ここで大事なのは、**買い増しはナンピンではない**ことやね。

買い増し条件はたぶんこう。

```text
Add-on Allowed =
  Core position が含み益
  AND H4 Expansion文脈が継続
  AND H4 Cycle Phase が Early or Middle
  AND 新しい確定済み押し目 basis がある
  AND その basis から R2 到達
  AND M5 Dow Up confirmed
```

逆に禁止条件。

```text
Add-on Blocked =
  H4 Cycle Late
  OR R5.5/R6付近
  OR H1高値更新失敗
  OR H4/H1 MA20接近・割れ
  OR Coreが含み損
```

ここを入れないと、終盤で買い増して天井掴みする笑

小さな利益確定は、さらに別レイヤー。

```text
Core:
  ④起点R5以上を狙う

Add-on:
  その買い増し起点の次区間Mid / 次Rで小さく利確

Profit Skim:
  R到達ごとに一部だけ回収
```

たとえば、

```text
Core 1枚
Add-on 1枚
```

で持った場合、

```text
Core      → ④起点R5/R5.5/R6狙い
Add-on    → 買い増し起点のR3 or R3.5で利確
```

みたいにする。

これなら、④起点の大波を狙いつつ、途中のミニサイクルからも利益を抜ける。

たぶん名前をつけるなら、

```text
Expansion Core & Satellite Rule
```

日本語なら、

```text
Expansion本玉・追撃玉分離ルール
```

がいいかも。

一番大事な思想はこれやね。

> **本玉は大波を見る。追撃玉は小波で回収する。**

これを入れると、かなり面白くなる。
しかも、さっきのH4サイクル成熟度とも相性がいい。

```text
Early:
  Core Entry 可
  Add-on 可
  小利確は控えめ

Middle:
  Add-on 可
  小利確開始

Late:
  Add-on 禁止
  小利確・利益保護優先
  CoreもExit感度を上げる
```

これで、

```text
前半は育てる
中盤は増やす
後半は刈り取る
```

になる。

おお……だいぶ昔の手動シミュレーションっぽい匂いが戻ってきたねぇ笑


----

うん、まさにその判断になりそう。
今回のケースは **④起点のR6.5** と **⑨起点のR6** がかなり近いので、ここはかなり強い **ターゲット密集帯** として扱えると思う。

言い換えると、

```text
④起点 = 大きなExpansion波のスケール
⑨起点 = 途中から生えた後続サイクルのスケール

④ R6.5
≒
⑨ R6
```

なので、ここは単なる一本の利確線じゃなくて、

> **複数起点のHSIターゲットが重なる決済ポイント**

やね。

ルール名を付けるなら、

```text
HSI Confluence Target
```

日本語なら、

```text
HSI重なりターゲット
```

がしっくりくる。

今回の利確方針としては、こんな感じが自然。

```text
Entry:
  ④Expansion後の押し目Entry

最低目標:
  ④起点 R5

伸ばす目標:
  ④起点 R6 / R6.5

本命利確:
  ④起点 R6.5 と ⑨起点 R6 の重なりゾーン
```

しかもここ、H4サイクル的にもだいぶ進行している場所に見えるから、
**到達したら「もっと上あるかも」より、まず利確優先** でよさそう。

なので実戦ルールに落とすなら、

```text
④ R6.5 と 後続起点 R6 が近接する場合、
その価格帯を Expansion Confluence Target として扱う。

到達時:
  Core玉は大部分利確
  残す場合も建値以上 or 直近H1押し目下へStop引き上げ
  新規買い増しは禁止
```

これやね。

特に最後が大事。

> **重なりターゲット到達後は、買い増しポイントではなく刈り取りポイント。**

ここを間違えると、せっかく大波を取ったあとに天井付近で増やして死ぬやつになる笑

今回のチャートはかなり教材っぽい。
**④の大波ターゲットと、⑨の後続波ターゲットが合流したから、そこを最終利確候補にする**。
めちゃくちゃ綺麗な整理やと思う。


----

うん、それはかなり利益確定条件に使えると思う。
むしろ、**⑨R6付近を本命利確にできる理由が、かなり揃ってきた**感じやね。

整理するとこう。

```text
⑨R5付近
= HSI重なりあり
= でもBBは開き始め
= MAから離れていく初動
= 利確よりHold / 加速確認

⑨R6付近
= HSI重なりあり
= BBが閉じ始める
= 価格がMA/T3へ近寄る
= H4大サイクルも後半
= 利益確定候補
```

つまり、同じHSI Confluenceでも、

> **BBが開く方向の重なりは継続理由。
> BBが閉じる方向の重なりは利確理由。**

これ、めちゃくちゃ綺麗。

ルール化するなら、こんな感じかな。

```text
TakeProfitAllowed =
  HSI Confluence reached
  AND H4 Cycle Phase is Middle/Late
  AND BB Expansion is slowing or contracting
  AND Close / T3 / MA20 distance is shrinking
```

もう少し状態名にすると、

```text
BBOpeningStart
  → 利確禁止 / Hold優先

BBExpansionMature
  → 一部利確候補

BBContractingToMA
  → 本命利確候補
```

今回の⑨R6付近は、まさにこの **BBContractingToMA**。

判定材料はこんな感じでいけそう。

```text
BBContractingToMA =
  BBWidth[0] < BBWidth[n本前]
  AND BBWidthの傾きがマイナス
  AND CloseとMA20の距離が縮小
  AND CloseとT3の距離が縮小
```

加えてH4時間軸。

```text
H4CycleLate =
  ④起点からのH4バー数が多い
  OR ミニサイクルを4〜5個消化
  OR ④起点R6以上に到達
```

この2つが重なると、

```text
HSI重なり
+ BB収縮
+ MA接近
+ H4サイクル後半
= 利益確定
```

になる。

なので、今回の判断はこう書けるね。

> **④R6.5 × ⑨R6 の重なりは、単なる価格ターゲットではなく、H4サイクル後半でBBが閉じ始め、価格がMAへ戻り始める局面と重なるため、本命利確条件として扱える。**

これはかなり実戦的。
「Rに到達したから利確」じゃなくて、

```text
価格目標に到達した
かつ
波の寿命が進んだ
かつ
勢いが収束し始めた
```

だから利確。

この3点セットにできるのがでかい。
HSIがだいぶ “線引き遊び” から “判断構造” に戻ってきたねぇ。

----

うん、考え方としてはかなり近い。
普通に整理するなら、**買い増し理論** と **細切れ利益確定理論** は、同じ「建玉管理」だけど役割が違う。

```text
買い増し = 波に乗れているときに、同じ方向へ追加する
細切れ利確 = 波が伸びたときに、少しずつ利益を現金化する
```

で、今回のHSI/Expansion文脈なら、たぶんこう分けるのが綺麗。

---

# 1. 買い増し理論

これは言ってる通り、

> **通常のM5エントリー理論で、Expansionと同じ方向だけ買い増す**

でかなり自然。

つまり、H4で大きなExpansion上昇文脈があるなら、買い増しはM5の通常Entry条件で見る。

```text
H4 Expansion Up 継続
AND H4 Cycle が Early / Middle
AND M5で押し目起点が確定
AND その起点からR2到達
AND M5 Dow Up confirmed
→ 買い増し可
```

ただし、買い増しで絶対に避けたいのは **ナンピン化** やね。

なので条件はこれ。

```text
買い増しOK:
  既存ポジションが含み益
  H4 Expansion方向と同じ
  M5通常Entry条件が再成立
  H4サイクル終盤ではない
  BBがOpening / Expansion中

買い増しNG:
  既存ポジションが含み損
  H4サイクルLate
  BBが閉じ始め
  H1高値更新失敗
  価格がMA/T3へ戻り始め
```

つまり買い増しは、

> **負けを取り返すためではなく、勝っている波に追加で乗るためのもの**

やね。

---

# 2. 細切れ利益確定理論

これもイメージは合ってる。

たとえば10単位でEntryしたなら、

```text
R4でEntry
R4.5で一部利確
R5で一部利確
R5.5で一部利確
R6で一部利確
残りはRunnerとして伸ばす
```

みたいな考え方は普通にあり。

ただし、ここで大事なのは、**全部を同じ目的で利確しないこと**。

たとえば、

```text
最初の一部利確 = リスク軽減
中盤の利確     = 利益確保
終盤の利確     = 本命利確
最後の残り     = 夢を見るRunner
```

みたいに役割を分ける。

---

# 3. 10単位Entryの例

たとえば④Expansion起点で、⑤起点R2から入ったけど、④起点ではR4付近Entryだったとする。

```text
Entry: 10単位
Stop: ④Expansion起点側
Target: ④起点R5以上
```

この場合、細切れ利確はこんな感じ。

```text
R4.5到達:
  2単位利確
  目的 = リスク軽減 / 建値化準備

R5到達:
  2単位利確
  目的 = 最低目標の回収

R5.5到達:
  2単位利確
  目的 = 中盤ターゲット回収

R6 / R6.5 Confluence到達:
  3単位利確
  目的 = 本命利確

残り1単位:
  Runner
  目的 = R7や異常伸び狙い
```

こんな感じ。

ただ、Expansion Entryの場合はStopが遠いから、**R4.5の利確だけで喜ぶとリスクリターンが悪い**。

なのでR4.5利確は、

> 利益を取るというより、以後のStopを上げるためのイベント

として見る方が自然かも。

```text
R4.5到達
→ 少し利確
→ 残りのStopを建値付近へ引き上げる準備

R5到達
→ 最低利益を確保

R5.5〜R6.5
→ 本命利確
```

---

# 4. 買い増し玉と本玉を分ける

一番綺麗なのはこれ。

```text
本玉 Core:
  ④Expansionの大波を取りに行く
  R5 / R5.5 / R6 / R6.5まで狙う

買い増し玉 Add-on:
  M5の小波で入る
  小さくR3 / R3.5 / R4などで利確してよい
```

つまり、

```text
本玉は大波
買い増し玉は小波
```

を取る。

これを混ぜるとぐちゃぐちゃになる笑

たとえば、

```text
Core 5単位:
  ④起点R6.5まで狙う

Add-on 3単位:
  買い増し起点のR3/R3.5で利確

Add-on 2単位:
  さらに伸びたらR4/R5まで持つ
```

みたいにする。

---

# 5. HSI的にはこう整理できそう

```text
Entry:
  確定済みHSI起点からR2

Add-on:
  新しい確定済み押し目起点からR2
  ただしH4 Expansion方向と同じ場合のみ

Small TP:
  Entry起点またはAdd-on起点の次区間Mid / 次R

Core TP:
  ④Expansion起点のR5以上
  複数起点のConfluenceを優先

Final TP:
  H4 Cycle Late
  AND HSI Confluence
  AND BB closing to MA
```

---

なので、質問の答えとしては、

> **細切れ利確は、R4で入ったらR4.5、R5、R5.5、R6で少しずつ利確する考え方でOK。
> ただし、本玉と買い増し玉で利確ルールを分けた方が綺麗。**

やね。

本玉は伸ばす。
買い増し玉は小さく回収する。
終盤Confluenceでは大きく刈り取る。

この3つを分けると、かなり面白くなる。


----

そうそう、それが肝やね笑
**「⑫後の反発失敗確認を、いつまで見るの？」** 問題。

で、結論から言うと、**サイクルの切れ目をロジックで完璧に当てに行かない方がいい**と思う。
難易度高すぎるし、たぶん沼る。

代わりに、こうするのが現実的。

```text
サイクルを切る
ではなく、

⑱以降を「期限付きの反発テスト期間」として扱う
```

つまり、ロジックはサイクル認識ではなく **状態管理** にする。

---

# 簡単仕分け仕様 v0.1

## 1. まず Short Watch に入る

開始条件はこれ。

```text
Long利確済み
AND H4 Cycle Late
AND H1/H4でDown寄りの材料が出た
```

ここでいきなりShortではなく、

```text
state = ShortWatch
```

にする。

意味は、

> 上昇Expansionは終わったかもしれない。
> でも下落開始とはまだ決めない。

---

# 2. 反発テスト期間を決める

ここをバー数で雑に区切る。

たとえば、

```text
ShortWatch開始から
H4で3〜6本
または
H1で12〜24本
```

この期間だけ、

```text
⑫後に跳ね返るのか？
それとも反発失敗するのか？
```

を見る。

これならサイクルの切れ目を当てなくていい。

```text
サイクル終了を検出する
↓
難しい

一定期間、反発テストを見る
↓
簡単
```

---

# 3. 反発失敗条件

反発失敗は、ざっくりこの3点でいいと思う。

```text
1. 前回高値を更新できない
2. MA20 / T3 / BB中央〜上側で失速
3. その後、M5またはH1でDow Down再確定
```

コードっぽくすると、

```text
ReboundFailed =
  high_after_watch_start < previous_expansion_high
  AND rebound_high_near_MA20_or_T3_or_BB_mid
  AND M5_Dow_Down_confirmed
```

もう少し安全にするなら、

```text
ReboundFailed =
  confirmed_basis_high_after_⑱ exists
  AND confirmed_basis_high_after_⑱ < previous_H1_or_H4_high
  AND Close < H1_MA20 or Close < H1_T3
  AND M5_Dow_Down_confirmed
```

これなら、目で見ている「戻したけど上に行けなかったね」をロジックにできる。

---

# 4. Short禁止条件も作る

逆に、これが出たらShort禁止。

```text
ShortBlocked =
  前回高値を更新
  OR H1/H4 Close が MA20/T3 上に復帰
  OR BB上側が再び開き始める
  OR H1でDow Up再確定
```

つまり、

```text
⑫後に強く跳ね返った
↓
やっぱり上昇トレンド継続かも
↓
Short禁止
```

にする。

---

# 5. 期限切れならノートレード

ここ大事。

反発テスト期間内に、

```text
反発失敗
```

も

```text
上昇復帰
```

も決まらなかった場合は、

```text
NoTrade
```

でいいと思う。

無理にShortしない。

```text
ShortWatch開始
↓
H4 3〜6本見る
↓
反発失敗しない
↓
上昇復帰もはっきりしない
↓
ノートレード
```

これでかなり事故が減る。

---

# 状態遷移で書くと綺麗

```text
Long TP
↓
ShortWatch
↓
ReboundTest
↓
分岐

A: ReboundFailed
   → ShortAllowed

B: TrendResumedUp
   → ShortBlocked / LongWatchへ戻る

C: Timeout
   → NoTrade
```

これが一番シンプル。

---

# たぶん使える名前

```text
Post Expansion Rebound Test
```

日本語なら、

```text
Expansion後反発テスト
```

仕様名としてはこれで良さそう。

---

# かなり重要な考え方

サイクルの切れ目を直接当てに行かない。

代わりに、

```text
⑱以降、一定期間だけ反発を観察する
↓
高値更新できない
↓
MA/T3で失速
↓
M5 Down再確定
↓
Short可
```

にする。

これなら、人間の目で見ている

> あ、戻したけど弱いな。これは下かも。

を、かなり単純なロジックに落とせる。

---

なので答えは、

> **サイクルの切れ目を判定する仕様ではなく、⑱後の期限付き反発テスト仕様にするのが簡単で現実的。**

これやと思う。

しかもこれ、昔うまくいかなかった「終わったっぽいから即Short」を防げる。
**終わり判定ではなく、反発失敗判定** に変えるのがミソやね。


----

---

うん、流れとしてはかなり自然。
ただ、状態名を分けるならこうやね。

```text
⑱ H4 Dow Down 確定
↓
Short Watch 開始
※まだShort Entryではない

⑱〜⑳
↓
反発テスト期間

⑳付近
↓
反発失敗確認
= Short狙いへ切り替え

その後
↓
M5でShort Entry条件を探す
```

なので、理解としてはほぼ合ってる。

ポイントは、**⑱は「Shortしてよい」ではなく「Short監視してよい」**。
⑳で「反発失敗」が見えて、ようやく **Short Bias** に切り替わる感じ。

---

⑳付近の反発失敗は、たぶんこう定義できる。

```text
ReboundFailed =
  ⑱後に戻した
  AND 直近高値を更新できない
  AND H4/H1のMA20 or T3付近で失速
  AND H4/H1が再び上昇Expansionへ戻らない
  AND H1またはM5でDow Downが再成立
```

この条件が出たら、

```text
state = ShortBias
```

に変更。

そのあと実際のEntryはM5で探す。

```text
Short Entry =
  ShortBias == true
  AND M5で戻り高値 basis high が確定
  AND その戻り高値から下方向R2到達
  AND M5 Dow Down confirmed
  AND H1/H4文脈がDown維持
```

---

なので、言い方としては、

> **⑱でShort様子見確定。⑳で反発失敗確認。そこからM5の通常Short理論でEntryを探す。**

これが一番綺麗。

ただし、⑲付近のDowDownを使う場合は、
**⑳の反発失敗確認より前の⑲をEntry根拠にしてしまうと少し危ない**かも。

安全にするなら、

```text
⑱ = Short Watch開始
⑳ = ReboundFailed確定
⑳以降のM5 Dow Down confirmed = Entry候補
```

が一番事故りにくい。

つまり、

```text
H4の終わりを見た
↓
反発失敗を見た
↓
M5で下方向Entryを探した
```

この3段階やね。

ここまで来ると、かなり仕様っぽくなってきた。
**Long Exit ≠ Short Entry** のあとに、
**Short Watch → ReboundFailed → M5 Short Entry** が生えた感じ。

---

うん、たぶんそのスタンスがかなり安全やね。

この⑭安値起点でHSIを引くと、たしかに上方向にR4越えっぽい形は出てる。
でも、問題はそこじゃなくて、

> **⑭起点が、T3・MA20の下側で整理された安値っぽい**

ところやね。

だからこの時点では、

```text
R4越えたからExpansion確定！！
```

ではなく、

```text
R4越えたけど、上位文脈がまだ弱い
→ Expansion Candidate
→ Confirm待ち
```

くらいが自然だと思う。

特に今回みたいに、H4でT3/MAの下にいる、またはT3/MAに抑えられている状態だと、⑭起点R4越えは **本格Expansion** というより、

> 下落後の戻り・調整上昇・MA回帰

の可能性が残る。

なので、ルールとしてはこうしたい。

```text
ExpansionConfirmed =
  HSI起点が確定済み
  AND 起点からR4以上到達
  AND H4 Close が MA20/T3 の上へ復帰
  AND H1/H4 Dow Up confirmed
  AND BBが上方向にOpening
```

逆に、今回のように、

```text
R4越えあり
BUT
Close が T3/MA20 下または絡み中
AND
H4 Dow Up が未確定
AND
上位足がまだ下落/調整文脈
```

なら、

```text
ExpansionCandidate止まり
Long Entry禁止
Short Bias解除は検討
次の押し目確認待ち
```

がよさそう。

つまり、⑭起点の扱いはこれ。

```text
⑭ = HSI起点候補として保存してよい
⑭起点R4越え = Expansion候補として観測してよい
ただし、T3/MA下で整理された起点なので、Expansion確定にはしない
```

これ、めっちゃ大事やね。
**HSI R4越え単独ではExpansion確定にしない**。
上位足のT3/MA位置とDow確定が必要。

今回の言葉にすると、

> **⑭起点は「反転Expansion候補」だけど、T3・MAの下で生えた安値なので、まだ正式Expansionには昇格しない。**

ここで飛び乗らずに、次に

```text
H4でMA/T3上に復帰
↓
押し目を作る
↓
その押し目が確定
↓
そこからR2
↓
M5 Dow Up
```

まで待つのが、かなり綺麗だと思う。

---

きたぁーーーーー笑
これはかなり気持ちいい答え合わせやね。

つまり今回の読みは、

```text
⑭起点R4越え
↓
一見 Expansionっぽい
↓
でも T3 / MA20 の下側で安値整理
↓
上位文脈がまだ弱い
↓
Expansion確定には昇格しない
↓
次窓で Dow Up すぐ崩壊
```

で、**判断として正解**やね。

これはめちゃ大事。

> **R4越え単独ではExpansion確定にしない。
> T3 / MA20 の上に復帰できていないR4越えは、Expansion Candidate止まり。**

この制約、かなり強い。

今回のケースはまさに、

```text
HSI的には伸びている
でも構造的には上昇トレンド復帰していない
```

ってやつ。

だからルール化するなら、

```text
ExpansionCandidate =
  確定済み起点からR4越え

ExpansionConfirmed =
  R4越え
  AND H4 Dow Up confirmed
  AND CloseがH4 MA20/T3上に復帰
  AND その後すぐ崩壊しない
```

さらに安全にするなら、

```text
R4越え後、H4で1〜2本は上位MA/T3上を維持
```

みたいな **Confirm Hold Bars** を入れてもいいかも。

これでかなり事故が減るね。

今回の名付けはこれやな。

```text
False Expansion Filter
```

日本語なら、

```text
偽Expansionフィルター
```

または、

```text
MA下R4越え無効ルール
```

笑。

いやーこれは良い。
**「HSIは見えてる。でもHSIだけ信じると騙される」** っていう最高の教材やね。


---

うん、その理解でいいと思う。
**㉑のH4 dawdown確定 = Short Entry OK ではなく、まずは Shortエントリー候補状態へチェンジ** やね。

今回みたいに、

```text
上方向Expansion候補
↓
でもMA/T3下 or MA/T3絡みで弱い
↓
dawUpすぐ崩壊
↓
㉑でH4 dawdown確定
```

という流れなら、㉑はこう扱うのが安全。

```text
state = ShortWatch / ShortCandidate
```

つまり、

> **上方向の物語は崩れた。
> でも、まだショートを撃つ場所ではない。
> ここからM5でShort Entryを探す。**

という状態。

---

エントリーOKにするなら、㉑のあとにもう一段必要。

```text
㉑ H4 Dow Down confirmed
↓
ShortCandidateへ移行
↓
H1もDown寄り / MA20・T3下側
↓
M5で戻り高値 basis high 確定
↓
その戻り高値から下方向R2到達
↓
M5 Dow Down confirmed
↓
Short Entry OK
```

なので、㉑は **上位足の許可証** であって、**発射ボタンではない**。

---

今回のケースで言うと、特に重要なのはここ。

```text
上昇Expansion崩壊
= Long禁止 / Short候補化

Short Entry
= M5で下方向の通常Entry条件が成立
```

この2つは分ける。

だからルール名で言うなら、

```text
Opposite Dow Confirmed
→ ShortCandidate
```

で、そのあとに、

```text
M5 Short Trigger Confirmed
→ ShortEntry
```

やね。

---

もし㉑時点で、

* H4/H1ともMA20・T3下
* BBが下方向に開き始め
* 直前の反発失敗も確認済み

まで揃っているなら、**ShortCandidateより一段強い ShortBias** にしてもいい。

でもそれでも、実際のエントリーはM5側。

```text
㉑ = ShortBias確定でもよい
ただし Entry は M5 trigger 待ち
```

ここが一番綺麗やと思う。



うん、その整理でOKやと思う。
**㉒付近で H4 dawUp 確定 = いきなり Long Entry OK ではなく、まずは Up候補 / LongWatch へモードチェンジ** やね。

この流れ。

```text
㉑ H4 dawDown 確定
↓
ShortWatch / ShortBias
↓
M5通常Shortで小さく取る区間
↓
㉒ H4 dawUp 確定
↓
Short物語いったん終了
↓
LongWatch / UpCandidate へ切替
```

なので㉒で起きることは、

```text
Short新規禁止
Short買い増し禁止
Short保有分は利確・撤退優先
Long候補として観察開始
```

くらい。

ただし、ここも前と同じで、**dawUp確定 = Long発射ボタンではない**。

Long Entryにするには、㉒のあとにもう一段ほしい。

```text
㉒ H4 dawUp confirmed
↓
LongWatch
↓
確定済み押し目 basis low を確認
↓
その起点からR2到達
↓
M5 Dow Up confirmed
↓
H1/H4がMA20/T3上に復帰、または上抜け方向
↓
Long Entry OK
```

特に今回みたいな反転直後は、

```text
H4 dawUpは出た
でもMA/T3の下 or 近辺で揉んでいる
```

なら、まだ **UpCandidate止まり**。

逆に、

```text
H4 dawUp
AND H1も上向き
AND CloseがMA20/T3上へ復帰
AND BBが上方向に開き始め
AND ㉒起点R4越え
```

まで来たら、**新しい上昇Expansion候補** として見てよさそう。

つまり今回の答えはこれやね。

> **㉒は Long Entry ではなく、Shortモード終了 + LongWatch開始。
> そこからM5通常Long条件、または新Expansion条件を待つ。**

これで、
**Long Exit ≠ Short Entry** と同じく、

```text
Short Exit ≠ Long Entry
```

も成立する笑

だいぶ状態遷移が綺麗になってきた。


----

うん、これはたぶん **今のルールでは入れない** と思う笑
そして、そこがめちゃくちゃ良い論点やね。

今まで整理してきたEntryは、基本こうだった。

```text
H4でExpansion確認
↓
押し目を待つ
↓
確定済み押し目起点からR2
↓
M5 Dow Up
↓
Entry
```

つまり、**Expansionが起きたあとに押し目を拾うルール**。

でも⑮からの波は、たぶん性質が違う。

```text
⑮付近で下げ止まり
↓
横ばい・底固め
↓
MA/T3付近で整理
↓
じわじわ上方向へ
↓
あとから見ると大きく伸びた
```

これ、**Expansion Pullback Entry** ではなくて、
どちらかというと **底練り後の初動Entry** なんよね。

だから今のルールだと、

```text
まだExpansion確定前
押し目後R2でもない
H4大波の継続Entryでもない
```

となって、Entryできない。

---

ここで必要になるのは、たぶん別ルール。

```text
Base Breakout Entry
```

日本語なら、

```text
底練りブレイクEntry
```

または、

```text
初動捕獲Entry
```

やね笑

条件イメージはこう。

```text
BaseBreakoutEntryAllowed =
  H4/H1で下落後の安値圏整理がある
  AND T3/MA20が横向き〜上向きに変化
  AND CloseがT3/MA20上へ復帰
  AND 確定済みbasis lowが存在
  AND そのbasis lowからR2以上
  AND M5 Dow Up confirmed
  AND BBがOpeningStart
```

これなら、⑮みたいな **Expansion前の立ち上がり** を拾える可能性が出る。

ただし、このルールはめちゃくちゃ危険でもある笑
なぜなら、さっきの⑭みたいな **偽Expansion** と紙一重だから。

なので、⑮ルールには必ずフィルターが要る。

```text
Entry禁止:
  H4 Close がまだMA20/T3下
  H4 Dow Upが即崩壊
  BBが開かない
  R4越え後にすぐ失速
```

つまり今回の整理は、

> **⑮からの波は、既存のExpansion押し目Entryでは取れない。
> 取るなら「底練りブレイクEntry」という別ルールが必要。**

これやね。

ここ、めちゃ面白い。
今のルール体系に足りないEntryタイプが見えた感じする。

```text
1. Normal Entry
   通常のM5 Dow + R2

2. Expansion Pullback Entry
   H4 Expansion後の押し目R2

3. Base Breakout Entry
   下落後・横ばい後の初動R2
```

⑮はたぶんこの **3番**。
ただし、偽Expansion対策として **MA/T3復帰 + BB OpeningStart + H4/H1維持確認** が必須、って感じやね。

---

うん、それは入れたい。
ここで **R4まで待つと遅すぎる** ね。BBが開き始めているのに、R4まで待つルールしかないと、初動の一番おいしいところを見送ることになる。

これは **Expansion確定Entry** ではなく、別枠で、

```text
Pre-Expansion Breakout Entry
```

または日本語で、

```text
Expansion前ブレイクEntry
R3.5高値群ブレイクEntry
```

として分けるのがよさそう。

## 考え方

今回の条件はこうやね。

```text
⑮起点の波
↓
BBが開き始める
↓
MA20 / T3 の上に復帰
↓
同じ高さの高値群がある
↓
R3.5付近でその高値群を上抜く
↓
R4まで待たずに Entry OK 状態へ
```

つまり、

> **R4越え = Expansion確定候補**
> **R3.5高値群ブレイク = Expansion前の初動捕獲候補**

として分ける。

これはめちゃ自然。

---

## ルール案

```text
PreExpansionBreakoutAllowed =
  confirmed_basis_low exists
  AND price >= R3.5 from basis low
  AND price breaks equal-high cluster
  AND Close > MA20
  AND Close > T3
  AND BBOpeningStart == true
  AND DowUp confirmed or M5 DowUp confirmed
```

この状態になったら、

```text
state = LongEarlyEntryAllowed
```

でよさそう。

ただし、この時点ではまだ正式なExpansionではない。

```text
R3.5高値群ブレイク
= 早乗りEntry候補

R4越え
= Expansion Candidate / Confirm候補
```

という扱い。

---

## 「同じ高さの高値」の定義

ここはロジック化するなら、こういう感じ。

```text
EqualHighCluster =
  直近N本の confirmed basis high が複数ある
  AND それらの価格差が許容範囲内
```

許容範囲は仮で、

```text
許容差 = 0.1R 〜 0.2R
または
許容差 = ATRの一部
または
許容差 = 固定pips
```

最初は雑に、

```text
直近2〜3個の高値がほぼ同じ価格帯
```

でいいと思う。

そして、

```text
Close > EqualHighClusterHigh
```

でブレイク判定。

---

## BB条件はかなり重要

ここでBB条件を入れるのが肝やね。

```text
BBOpeningStart =
  BBWidth が増加開始
  AND BB上限が上向き
  AND Close がMA20/T3上
  AND 価格がBB中央〜上側にいる
```

これがあるから、R3.5で入っても「ただの戻り売りポイントを買った」になりにくい。

逆に、

```text
R3.5突破しても
BBが開いてない
MA/T3の下
高値群を明確に抜けてない
```

ならEntry禁止。

---

## このルールの位置づけ

今の体系に追加するならこう。

```text
1. Normal Entry
   M5通常R2 + Dow

2. Expansion Pullback Entry
   H4 Expansion後の押し目R2

3. Pre-Expansion Breakout Entry
   R3.5高値群ブレイク + BB Opening + MA/T3上

4. Expansion Confirm
   R4越え + 上位足維持
```

今回の⑮波は、まさに **3番**。

---

## 利確・Stopの考え方

R3.5で早く入る分、最初はまだExpansion確定前なので、管理は少し軽め。

```text
初期Target:
  R4

R4到達後:
  Expansion Candidateへ昇格

R4越え後もBB Opening継続:
  R4.5 / R5 を狙う

R4前に失速:
  小利確 or 建値撤退
```

Stopは、

```text
⑮起点のbasis low割れ
または
MA20/T3下へ再沈没
または
BB Opening失敗
```

あたり。

---

結論としては、

> **R3.5付近で、同じ高さの高値群を上抜き、BBが開き始め、MA20/T3上にいるなら、R4を待たずにEntry OK状態へ昇格してよい。**

これかなり良いと思う。
「Expansion確定を待つルール」と「Expansion前の加速初動を拾うルール」を分けられる。
この分離ができると、⑮みたいな波を取り逃がしにくくなるね。





