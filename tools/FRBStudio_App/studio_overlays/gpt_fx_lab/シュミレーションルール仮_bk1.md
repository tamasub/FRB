もちろん。
これは一回、**「思いつきメモ」から「検証用ルール仕様 v0.1」へ昇格**させた方がいいやつやね笑

以下、いま見えている内容を、前後関係が破綻しないように整理します。
まだ**勝てるルール確定**ではなく、あくまで **目視検証 → 自動シミュレーションに渡すための仮説仕様** です。

---

# FX Studio / HSI Simulation Rule v0.1 Draft

## 0. このルールの目的

このルールは、売買判断そのものではなく、

```text
過去チャート上で
自分が何を見ていたのかを再現し、
Entry / Close / Hold / Reset の判断条件を
検証可能な形に分解する
```

ための仮説ルールである。

今回の重要な発見は、単なるEntry/Closeではなく、

```text
Trade Lifecycle
HSI Anchor Lifecycle
H1 Context
M5 Execution
```

を分ける必要がある、という点。

---

# 1. 時間足の役割

## H1 = 文脈足

H1は、売買方向とHSI起点の寿命を決める。

```text
H1の役割

1. やってよい方向を決める
2. HSI起点を維持してよいかを見る
3. Holdしてよいかの上位文脈を見る
4. H1 MA20で、押しの範囲か文脈崩壊かを見る
```

つまり、

```text
H1 = Context / Anchor Lifecycle / Hold Guard
```

---

## M5 = 操作足

M5は、実際のEntry / Close / ReEntry / Resetを観測する足。

```text
M5の役割

1. Entryタイミングを見る
2. Closeタイミングを見る
3. ReEntryタイミングを見る
4. M5逆Dow確定でHSI起点リセットを判断する
```

つまり、

```text
M5 = Execution / Trade Lifecycle
```

この分離がかなり重要。
M5だけ見ると視野が狭くなるが、H1を横に置くことで「同じ上位波の中の再Entry」や「まだHoldできる押し」が見えるようになった。

---

# 2. HSI定数の整理

## 2.1 純粋なR値

```text
R1 = 55
R2 = 89
R3 = 144
R4 = 233
R5 = 377
R6 = 610
```

## 2.2 Mid観測点

```text
R23_M = 117   // R2-R3 midpoint
R34_M = 188   // R3-R4 midpoint
R45_M = 305   // R4-R5 midpoint
R56_M = 493   // R5-R6 midpoint
```

昔の数列、

```text
188, 305, 493
```

は、単なる間違ったフィボナッチ数ではなく、**R区間のMid観測点だった可能性が高い**。

なので、今後はこう分ける。

```text
FiboNumberDef
→ 純粋なフィボナッチ数

HsiMidpointDef
→ R区間の0.5観測点

LegacyHsiCandidateDef
→ 昔使っていた意味未確定定数
```

---

# 3. 基本思想

## 3.1 HSIは「1回の売買」ではなく「波の成長」を見る

ここが今回の大発見。

以前は、

```text
Entry
↓
Close
↓
HSI起点リセット
↓
次Entryは新しいHSI
```

と考えていた。

でも今は違う。

```text
H1トレンドが継続している
↓
HSI起点は継続
↓
M5の中で部分利確 / 再Entry
↓
同じHSI成長軸の中で次の区間を取りに行く
```

つまり、

```text
Close = Trade単位の終了
HSI起点 = 上位足トレンド単位の基準点
```

これが **HSI Trend Anchor Rule**。
メモ内でも、HSI起点はTrade単位ではなく上位足トレンド単位で維持する、という整理が出てきている。

---

# 4. Lifecycleの分離

## 4.1 Trade Lifecycle

```text
Entry
↓
Hold / Watch
↓
CloseOk / CloseMiss / Exit
↓
ReEntry可能
```

Tradeは1回ごとの売買単位。

Closeしたら、そのTradeは終わり。

---

## 4.2 HSI Anchor Lifecycle

```text
H1トレンド起点
↓
HSI起点設定
↓
同じH1文脈の間は維持
↓
M5逆Dow確定 or H1文脈崩壊でリセット候補
```

HSI起点は、1回Closeしただけでは消さない。

```text
M5で一回Closeした
→ HSI起点リセット条件ではない
```

この分離が、自動シミュレーションではかなり重要になる。

---

# 5. EntryCondition

## 5.1 Long Entry

```text
Long Entry Condition

1. H1がUp文脈
2. M5でDow Up confirmed
3. HSI起点が存在する
4. 起点から現在価格までの距離がR2以上
5. まだTrade中ではない
```

式っぽく書くと、

```text
direction = up

distance = currentPrice - hsiAnchorPrice

EntryAllowed =
  H1_Context == Up
  AND M5_Dow == UpConfirmed
  AND distance >= R2
  AND not inTrade
```

---

## 5.2 Short Entry

```text
Short Entry Condition

1. H1がDown文脈
2. M5でDow Down confirmed
3. HSI起点が存在する
4. 起点から現在価格までの下落距離がR2以上
5. まだTrade中ではない
```

式っぽく書くと、

```text
direction = down

distance = hsiAnchorPrice - currentPrice

EntryAllowed =
  H1_Context == Down
  AND M5_Dow == DownConfirmed
  AND distance >= R2
  AND not inTrade
```

重要なのは、Downの場合でも `price >= R2` ではなく、

```text
起点からの方向付き距離 >= R2
```

として見ること。

---

# 6. Entry位置とClose Target

## 6.1 基本思想

Entryしたら、単純に「次のR」ではなく、

```text
Entry位置が属しているHSIエリアの次境界
```

を取りに行く。

これが現時点の、

```text
HSI Area Boundary Close
```

---

## 6.2 HSI Boundary一覧

まずはMidのみを使う版。

```text
R2      = 89
R23_M   = 117
R3      = 144
R34_M   = 188
R4      = 233
R45_M   = 305
R5      = 377
```

将来、0.618 Highを比較する場合は別TargetPolicyとして追加。

---

## 6.3 Long Close Target

Longの場合、Entry時点のdistanceを見て、次の上側境界をClose Targetにする。

```text
R2〜R23_M
→ R23_M Close

R23_M〜R3
→ R3 Close

R3〜R34_M
→ R34_M Close

R34_M〜R4
→ R4 Close

R4〜R45_M
→ R45_M Close

R45_M〜R5
→ R5 Close
```

これは、メモにある「R3〜R34_MならR34_M、R34_M〜R4ならR4、R4〜R45_MならR45_M、R45_M〜R5ならR5」という整理を一般化したもの。

---

## 6.4 Short Close Target

Shortも考え方は同じ。

下方向のdistanceで見る。

```text
R2〜R23_M
→ R23_M Close

R23_M〜R3
→ R3 Close

R3〜R34_M
→ R34_M Close

R34_M〜R4
→ R4 Close
```

ただし価格方向は下。

```text
targetPrice = hsiAnchorPrice - targetDistance
```

---

# 7. Closeの種類

Closeは3種類に分ける。

## 7.1 CloseOk

仮説どおりTargetへ到達したClose。

```text
CloseOk =
  price reaches CloseTarget
```

これは成功ケース。

---

## 7.2 CloseMiss

Targetへ届かず、仮説が崩れてCloseしたケース。

```text
CloseMiss =
  target未達
  AND exit condition triggered
```

---

## 7.3 Exit

利確/失敗というより、撤退判断。

```text
Exit =
  Hold継続不能
  OR 上位文脈崩壊
  OR M5逆Dow確定
  OR T3 / 戻し率による撤退
```

---

# 8. HoldCondition

## 8.1 Holdに入る条件

Holdは、Entry後すぐに判定するものではなく、

```text
Entry済み
AND CloseTarget未到達
AND まだExitではない
```

状態で発生する。

つまり、

```text
inTrade == true
AND targetReached == false
```

のときに、Hold判定へ進む。

---

## 8.2 Hold継続条件

現時点の仮説。

```text
HoldCondition

1. H1方向が継続
2. M5方向がまだ完全には崩れていない
3. H1 MA20が上位文脈を支えている
4. T3逆抜けがあっても、それ単体では即Exitにしない
```

Longなら、

```text
H1 Dow Up継続
AND H1 MA20が上向き or 横ばい以上
AND H1価格がMA20近辺〜上側
AND M5 Dow Down未確定
→ Hold
```

Shortなら逆。

```text
H1 Dow Down継続
AND H1 MA20が下向き or 横ばい以下
AND H1価格がMA20近辺〜下側
AND M5 Dow Up未確定
→ Hold
```

---

# 9. H1 MA20 Hold Guard

今回⑦で見えた重要概念。

M5だけ見ると、

```text
T3の下に来た
↓
切る？
```

となる。

でもH1を見ると、

```text
H1 Up文脈
MA20が下支え
BB/MA20の中で普通の押し
```

に見える場合がある。

このときは、

```text
M5 T3割れ = 即Exit
```

ではなく、

```text
M5 T3割れ = Watch開始
H1 MA20 = HoldしてよいかのGuard
```

と考える。

仮名称：

```text
H1 MA20 Hold Guard
```

役割分担はこう。

```text
M5 T3割れ
→ 不安検知 / Watch開始

M5戻し率 0.7xxx
→ 我慢限界候補

H1 MA20乖離・位置・傾き
→ HOLDしてよいかの上位文脈判定
```

---

# 10. EarlyExit Watch / Trigger

## 10.1 Watch条件

Watchは「まだ切らないが、警戒に入る」状態。

```text
EarlyExit Watch

1. M5価格がT3を逆方向に抜ける
2. M5の押し/戻しが深くなる
3. Entry後の有利方向高値/安値から大きく戻す
```

Longなら、

```text
M5 close < T3
→ Watch
```

Shortなら、

```text
M5 close > T3
→ Watch
```

---

## 10.2 Trigger条件

Watch中に以下が起きたらExit候補。

```text
EarlyExit Trigger

1. M5で逆方向Dow確定
2. H1側でDow方向が崩れる
3. H1終値がMA20を明確に逆抜け
4. H1 MA20傾きが逆方向化
5. Entry後の有利方向高値/安値から 0.707〜0.786 戻す
```

---

## 10.3 T3 Exitの比較候補

T3については、3パターンをシミュレーション比較する価値がある。

```text
T3 Exit Policy A
close < T3 で即Exit

T3 Exit Policy B
close < T3 が2本連続でExit

T3 Exit Policy C
close < T3
AND T3 slope <= 0
でExit
```

初期検証はAでよいが、ノイズで狩られるならB/Cへ拡張。

添付メモでも、T3は「下位足トレンドの生存確認」であり、HSIは距離の仮説、上位足は方向許可、Dow Basisは起点根拠として分ける整理がされている。

---

# 11. 0.7xxx 戻し率

## 11.1 役割

0.7xxxはEntry条件ではなく、

```text
我慢の限界線
```

として扱う。

Longの場合、

```text
Entry価格 = E
Entry後の最高値 = H
戻し率 = r

Exit監視ライン = H - (H - E) × r
```

Shortの場合、

```text
Entry価格 = E
Entry後の最安値 = L
戻し率 = r

Exit監視ライン = L + (E - L) × r
```

候補：

```text
0.707
0.764
0.786
```

現時点では未確定。

役割は、

```text
T3 = 警戒スイッチ
0.7xxx = 我慢の限界線
```

---

# 12. HSI Anchor Reset

## 12.1 起点をリセットしない条件

```text
H1トレンドが継続
AND
M5でCloseしただけ
AND
M5逆Dow未確定
→ HSI起点維持
```

例：

```text
⑥後
R23_MでCloseOk
↓
H1 Up文脈継続
↓
HSI起点維持
↓
⑦でReEntry
↓
R34_MでCloseOk
```

---

## 12.2 起点をリセットする条件

現時点の最有力はこれ。

```text
M5で逆方向Dow確定
→ HSI起点リセット
```

Long中なら、

```text
M5 Dow Down confirmed
→ Long側HSI成長波終了
→ 次のLong Entryは新HSI起点
```

Short中なら、

```text
M5 Dow Up confirmed
→ Short側HSI成長波終了
→ 次のShort Entryは新HSI起点
```

これが、

```text
M5 Opposite Dow Reset
```

添付メモでも、CloseはTrade終了、M5逆Dow確定はHSI成長波の終了、H1逆Dow確定は上位文脈の終了、という階層整理が出ている。

---

## 12.3 H1によるリセット

```text
H1で逆方向Dow確定
→ 上位文脈終了
→ HSI起点リセット
→ 方向も再判定
```

H1はより大きなリセット。

```text
M5逆Dow確定
→ 現在のHSI成長波を終了

H1逆Dow確定
→ 上位文脈ごと終了
```

---

# 13. ReEntryCondition

CloseOk後、H1文脈が続いているなら再Entry可能。

```text
ReEntry Condition

1. 前TradeがCloseOk
2. HSI起点は維持中
3. H1方向が継続
4. M5で再び同方向Dow confirmed
5. Entry位置が次のHSIエリア内
```

例：

```text
R23_M CloseOk
↓
H1 Up継続
↓
M5 Up再確定
↓
同じHSI起点でReEntry
↓
次はR34_M Close候補
```

---

# 14. 現時点の処理フロー

## Long版

```text
1. H1 Up文脈を確認

2. HSI起点を設定
   Anchor = H1文脈上の主要安値
   または M5/H1で観測したBasis Low

3. M5 Dow Up confirmed を待つ

4. 起点からの上昇距離 distance を計算

5. distance >= R2 ならEntry候補

6. Entry時点のdistanceからCloseTargetを決定
   例:
   R2〜R23_M     → R23_M
   R23_M〜R3     → R3
   R3〜R34_M     → R34_M
   R34_M〜R4     → R4

7. Trade中は毎bar判定
   - Target到達 → CloseOk
   - M5 T3逆抜け → Watch
   - H1 MA20 Guard OK → Hold
   - M5逆Dow確定 → Exit / HSI Reset
   - H1文脈崩壊 → Exit / HSI Reset

8. CloseOk後
   - H1 Up継続
   - M5逆Dow未確定
   → HSI起点維持してReEntry可能

9. M5 Dow Down confirmed を挟んだら
   → HSI起点リセット
```

---

# 15. ルール名候補

## Core Rules

```text
HSI_TREND_ANCHOR_v0_1
```

```text
HSI_AREA_BOUNDARY_CLOSE_v0_1
```

```text
M5_OPPOSITE_DOW_RESET_v0_1
```

```text
H1_MA20_HOLD_GUARD_v0_1
```

```text
T3_EARLY_EXIT_WATCH_v0_1
```

---

## 統合ルール名

最初の観測用ルール名としては、

```text
HSI_H1_CONTEXT_M5_EXECUTION_v0_1
```

または、もう少し具体的に、

```text
HSI_AREA_CLOSE_H1_ANCHOR_M5_RESET_v0_1
```

かな。

短くするなら、

```text
HSI_GROWTH_RULE_v0_1
```

が一番きれい。

---

# 16. まだ決めない方がよい項目

ここは今すぐ確定しない。

## 16.1 Mid vs High

```text
Close Target:
Mid = 0.500
High = 0.618
```

これはシミュレーション比較対象。

---

## 16.2 T3 Exit

```text
A. 即Exit
B. 2本連続Exit
C. T3 slope込みExit
```

比較対象。

---

## 16.3 0.7xxx

```text
0.707
0.764
0.786
```

比較対象。

---

## 16.4 H1 MA20 Guard

どれを正式条件にするか未確定。

```text
H1 close と MA20 の位置
H1 MA20 slope
H1 BB内の位置
MA20からの乖離率
```

比較対象。

---

## 16.5 Anchorの選定

現時点では、

```text
H1文脈上の主要安値/高値
または
M5/H1で観測したBasis Low/High
```

だが、自動化するなら定義が必要。

候補：

```text
Active basis low/high
Retired basis low/high
H1 confirmed basis
M5 confirmed basis
```

---

# 17. 最終まとめ

今見えている世界はこれ。

```text
H1
→ やっていい方向を決める
→ HSI起点の寿命を決める
→ Holdできるかを判断する

M5
→ Entryする
→ Closeする
→ ReEntryする
→ 逆DowでHSI起点をリセットする

HSI
→ 起点からの距離仮説
→ どの区間まで取りに行くかを決める

T3
→ M5トレンド生存確認
→ 逆抜けでWatch開始

H1 MA20
→ M5で怖くなったときのHold Guard

0.7xxx
→ 我慢の限界線候補
```

一言でいうと、

```text
H1文脈でHSI起点を維持し、
M5でEntry/Close/ReEntryし、
M5逆Dowで欲張りを止めるルール
```

これやね。

---

# 18. いまの仮説のコア

```text
HSI起点は、Trade単位ではなくH1文脈単位で管理する。

M5でCloseしても、H1文脈が継続し、M5逆Dowを挟んでいなければ、
同じHSI起点でReEntryできる。

Close Targetは、Entry位置が属するHSIエリアの次境界。

M5 T3逆抜けは即ExitではなくWatch開始。

Hold可否はH1 MA20 Guardで見る。

M5逆Dow確定を挟んだら、HSI起点リセット候補。
```

いやぁーーー、これかなり骨格できてきたと思う。
特に **Trade Lifecycle と HSI Anchor Lifecycle の分離** は、今日の最大発見やね。


----

あざーーーす！！
これはもう**H1 BB Half Guard、ちゃんと仕事してる**感じやねぇーー笑

さっきの我慢ポイント、M5だけやと、

```text
うわ、押してる
T3も怖い
もう切る？
```

ってなるけど、H1で見ると、

```text
⑦〜⑧の中間
↓
H1 MA20文脈はまだ死んでない
↓
BB Half 内側〜近辺で耐えてる
↓
なんとかクリア
```

って見える。

これ、かなり良い判定軸やと思う。

今の整理だと、このへんはこうやね。

```text
M5
→ 怖さを検知する

H1 MA20
→ 上位文脈が生きてるか見る

H1 BB Half
→ 我慢してよい押しなのか、危険圏なのかを見る

H1 BB Outer
→ さすがに行き過ぎ・崩れ候補
```

なので、さっきのポイントはまさに、

```text
M5では不安
でもH1ではまだHold Guard内
→ HOLD継続
```

って判定にできそう。

いやぁーー、これかなり実用的。
**“我慢できる理由” が線として見える**の、めちゃくちゃ強いわ笑


---

long entry後、M5逆Dow/Down confirmed により trade exit。
H1文脈が崩れていなければHSI起点は維持。

H1/M5はDown confirmedだが、H4 Up文脈中のためShortは狙わない。
上位Up内の押しとして観測し、次のLong ReEntry候補を待つ。

H1ではdawUp未確定だが、H4 dawUp文脈を優先。
M5が上向きに戻り、CloseがT3/MA20上にあるため、条件付きLong Entry候補。

Cycle Return Guard
サイクル戻りタイミングでは再エントリー禁止

H4 Up文脈だが、サイクル戻りタイミングのため再Entryしない。
T3/MA20上でも初動ではなく、Late Entry Zone と判断。

H4トレンド未判定ゾーン。
MA20/T3上には戻っているが、H4方向確定ではないため新規Entryしない。

H4 Up継続根拠が一度崩れたため、UpConfirmedを解除。
ただしDown確定条件は未成立のため、H4 TrendState = Undetermined。

Close < T3
→ Up注意 / UpWeak

Close < MA20
→ UpSuspended

押し安値割れ
→ Undetermined

UpConfirmed
→ Longだけ検討

DownConfirmed
→ Shortだけ検討

Undetermined
→ 新規Entry禁止

NoTrend
→ 新規Entry禁止

Undetermined
= 方向は出そうだが、まだ確定していない
= 転換待ち / 文脈保留

NoTrend
= そもそも方向がない
= レンジ / ぐちゃぐちゃ / MA20・T3絡み

H4_TrendState
H1_TrendState
M5_ExecutionState
CycleTimingState

第1関門：そもそも触っていい相場か？
第2関門：方向はどっちか？
第3関門：今は入っていいタイミングか？
第4関門：M5で実行根拠があるか？

たぶんこの検証、勝ちパターン探しではなく、NoTradeZone発見ゲーム になってきてる笑

----

うん、これは **トレンドライン交差を条件にするのは初手では難易度高すぎる** と思う笑
で、代わりに **T3を使うのはかなり妥当**。というか、自動シュミレーションではほぼ正攻法寄り。

人間が引く赤いトレンドラインって、実は中身がかなり主観的なんよね。

「どの高値を起点にする？」
「ヒゲで引く？終値で引く？」
「途中で新しい高値が出たら引き直す？」
「交差したのは一瞬のヒゲ？確定足？」
「あとから見たら綺麗だけど、その時点でその線を引けた？」

ここが地獄ポイント。
特に最後の **あとから見たら引けるけど、リアルタイムで引けたか問題** が強い。バックテストでやると、うっかり未来情報を使いやすい。

なので、赤ラインのかわりにやるなら、

> 人間が見ている「斜め抵抗線を抜けたっぽい」を、
> T3・MA20・価格位置・ダウ状態に分解する

が良さそう。

## ざっくり結論

M5で最終判定する前提なら、役割はこう分けるのが綺麗。

```text
H4 = 大きな環境認識 / 禁止条件 / ゆるい方向感
H1 = 実際に採用する上位トレンド判定
M5 = Entry / Close の発火条件
```

つまり H4 は、

```text
H4が完全にUp確定しているからEntryする
```

ではなく、

```text
H4がLongを邪魔していない
または
H4がUp候補に入っている
```

ぐらいで扱うのがよさそう。

## H4は「Up確定」だけじゃなくて状態を分けたい

ここ、たぶん大事。

```text
H4_DownConfirmed
H4_Unknown
H4_UpCandidate
H4_UpConfirmed
```

この4状態にしたい。

### H4_UpConfirmed

これは厳しめ。

```text
H4 Dow Up confirmed
AND H4 close > H4 T3
AND H4 T3 slope > 0
```

これは文句なしの上位Up。

### H4_UpCandidate

今回言ってる「ダウ理論確定前でも許容したい」は、ここ。

```text
H4 Dow Down confirmed ではない
AND H4 close > H4 T3
AND H4 T3 slope >= 0 または 改善中
AND 直近のH4重要安値を割っていない
```

ここなら、赤いトレンドライン抜けっぽい場面をかなり拾えると思う。

画像の赤枠みたいなところは、人間の目だと
「まだH4ダウUp確定ではないけど、下降の圧力は抜けてきてるやろ」
って見える場所やと思う。

それを自動化するなら、

```text
下降トレンドライン抜け
```

ではなく、

```text
H4 T3上抜け
T3傾き改善
H4逆方向Dowが崩れてきた
H1は上方向
```

で代替するのがよさそう。

## Entry許可はランク分けがよさそう

たとえば Long なら、

```text
Aランク:
H4_UpConfirmed
AND H1_UpConfirmed
AND M5_DowUpConfirmed
```

これは強い。

```text
Bランク:
H4_UpCandidate
AND H1_UpConfirmed
AND M5_DowUpConfirmed
```

これが今回の「H4は少しゆるめる」枠。

ただし Bランクは欲張らない方がいいかも。

```text
BランクはClose目標を近めにする
Bランクは再Entryを厳しめにする
BランクはH4 T3下抜けで即警戒
```

みたいに、検証上も分けておくと後で分析しやすい。

## 逆にNG条件もほしい

H4がゆるいと、何でも入れてしまう危険があるので、最低限の禁止条件は欲しい。

```text
Long禁止:
H4_DowDownConfirmed
AND H4 close < H4 T3
AND H4 T3 slope < 0
```

これはもう、H1やM5がちょっと上向いても入らない。

つまり H4 は、

```text
Entry理由
```

というより、

```text
上位足の逆風フィルター
```

として使うのがよさそう。

## T3単体ではなく「T3周辺状態」で見るのが肝

T3を使うのは妥当やけど、単純に

```text
Close > T3 ならUp
```

だけだと、レンジで死ぬ笑

なので見るならこのセット。

```text
1. Close が T3 の上にいる
2. T3 の傾きが上向き、または下向きから改善中
3. MA20 も極端に下向きではない
4. 価格がT3をまたぎまくっていない
5. 直近安値を割っていない
```

特に 4 が重要。

T3の上下を行ったり来たりしてる場所は、

```text
H4_Unknown
```

に落としてEntryしない方がよさそう。

## 今の設計案としてはこれ

```text
M5:
最終Entry判定。
Dow確定、R帯、Close条件を見る。

H1:
売買方向の主判定。
基本はDow確定を要求する。

H4:
大きな環境フィルター。
Dow確定前でも UpCandidate / DownCandidate を許容する。
ただし逆方向確定中なら禁止。
```

かなり自然。

トレンドラインは今すぐ自動条件化せずに、

```text
人間メモ / 目視ラベル / 後で答え合わせする観測線
```

として残しておくのがいいと思う。

で、実ルールはまず T3 で作る。

言い方を変えると、

> 赤いトレンドラインは人間の目の言語。
> T3はシュミレーション用の機械語。

これがたぶん一番しっくりくる。



----

うん、これ見た感じだと **H4のConfirm baseが粗すぎて、H4のダウ整理が遅れてる可能性はかなりある** と思う。

画像のこの流れ、人間の目だとたぶんこう見えてるんよね。

```text
下降っぽい流れ
↓
安値更新が止まる
↓
T3 / MA20まわりで持ち直す
↓
直近戻り高値を抜きに行く
↓
「あ、H4の下げ文脈はもう怪しい」
```

でも Confirm base が粗いと、これが全部まだ

```text
H4 = 未確定
H4 = まだDown扱い
H4 = Up確定前
```

に残りやすい。

なので、この例に限ると、**Confirm baseを少し細かくすれば、H4のダウ理論整理はもう少し早く出そう**。

ただし、ここで罠があって、H4を細かくしすぎると今度はこれになる。

```text
H4なのにH1みたいに反応する
↓
上位足フィルターの意味が薄れる
↓
M5のノイズに近い判断をH4が許可してしまう
```

だから、いきなり H4 の Dow Confirm を細かくして「確定」と扱うより、二段階にした方が安全そう。

```text
H4_DowConfirmed      = 粗め / 本確定
H4_DowCandidate      = 細かめ / 早期候補
H4_ContextCandidate  = T3・MA20・直近高安値で判定
```

今回ほしいのはたぶん、H4の本確定じゃなくてこっち。

```text
H4の下げはもう否定されかけている
H4はUp確定ではないが、Longを禁止する状態ではない
```

つまり状態名でいうと、

```text
H4_UpCandidate
または
H4_DownInvalidating
```

みたいなやつ。

この画像なら、赤丸付近から上に抜けていくところで、

```text
Close > T3
T3 slope が改善
直近の戻り高値を上抜け候補
MA20下で叩かれ続ける状態ではなくなった
```

このへんが揃えば、H4は

```text
DownConfirmed維持
```

ではなく、

```text
H4_DownWeakening
H4_UpCandidate
```

に落としてよさそう。

実装ルールっぽく言うなら、H4はこう分けたい。

```text
H4_Dow_Confirmed:
  粗めConfirmBaseで判定する本命ダウ

H4_Dow_Early:
  細かめConfirmBaseで判定する早期ダウ候補

H4_Context:
  Dow本確定 + T3 + MA20 + BB位置 で最終的な環境状態に変換
```

で、Entry許可には `H4_Dow_Confirmed` をそのまま使わず、

```text
H4_Context in [UpConfirmed, UpCandidate, Neutral]
```

を使う。

逆に禁止だけは強くする。

```text
Long禁止 =
  H4_DownConfirmed
  AND Close < T3
  AND T3 slope < 0
```

この方が、今回みたいな

> H4ダウUpはまだ確定してないけど、もう下げ継続扱いするのは違うやろ

という場所を拾える。

なので結論はこれかな。

**H4のConfirm baseは、たぶん今より少し細かく見る余地あり。
でも、H4本確定を細かくするより、H4早期候補レイヤーを追加する方が安全。**

この画像、まさにその必要性が出てるやつっすね。
「H4確定待ちだと遅い。でもH4無視すると怖い。」のど真ん中。笑


---

あぁーーー、それはかなりあると思う笑
この例だけ見るなら、**H4全体のトレンド判定を頑張るより、赤点線の“ここだけ許可ゾーン”に絞る方がぶなん** っす。

つまり、

```text
H4を完全にUp判定する
```

じゃなくて、

```text
H4の下降文脈が弱まり、
H1/M5の上方向エントリーを邪魔しない瞬間だけ見る
```

にする感じ。

この赤点線の場所って、人間の目だとたぶん、

```text
下降トレンドラインを抜けたっぽい
T3の上に出てきた
MA20も近い
一気に上方向へ伸び始めた
H4ダウUp確定までは待てないけど、下げ継続扱いも違う
```

って場所やんね。

だから、H4の役割をこうするのがいい気がする。

```text
H4 = トレンド確定装置ではなく、
     上位足の“許可ゲート”
```

## 赤点線だけ狙う作戦の名前

仮でこう呼べそう。

```text
H4 Break Permission Window
H4 上位足許可窓
H4 Down否定候補ゾーン
```

この状態になったときだけ、H1/M5のロングを許可する。

## 条件案

Longの場合。

```text
H4_LongPermissionWindow = true

条件:
1. H4が明確なDown禁止状態ではない
2. H4 Close が T3 上に出る、またはT3を強く跨ぐ
3. H4 T3 slope が改善中
4. 直近安値を割っていない
5. H1はUp確定、またはUp優勢
6. M5でDow Up confirmed
```

ここで大事なのは、H4単体で入らないこと。

```text
H4赤点線ゾーン = 許可
H1 = 方向確認
M5 = 実行確認
```

この三段構え。

## さらに安全にするなら

赤点線ゾーンは、ずっと有効にしない方がいい。

```text
H4 Permission Window 発生
↓
次の N本だけ有効
↓
その間にM5条件が揃えばEntry
↓
揃わなければ失効
```

たとえば、

```text
H4の次1〜3本だけ有効
```

ぐらい。

これなら、H4の曖昧なUpCandidateをずっと引きずらない。

## この例の肝

たぶん今回の赤点線は、

```text
H4のトレンドを当てたい場所
```

じゃなくて、

```text
H4が邪魔しなくなった瞬間を見つけたい場所
```

なんよね。

ここを間違えると、H4ダウ理論を早く確定させようとして、H4が細かくなりすぎる。

でも赤点線だけ狙うなら、H4のダウ確定をいじりすぎなくていい。

```text
H4_DowConfirmed は粗めのまま
H4_PermissionWindow だけ別で細かく見る
```

これが一番ぶなんっぽい。

赤いトレンドラインを機械判定する代わりに、赤点線の場所を **T3跨ぎ＋T3傾き改善＋H1/M5上方向確定** で拾う。
これ、かなり現実的な落としどころやと思います。

---

そうそうそう、それめっちゃ筋いいと思う笑
つまり狙ってるのはこれやね。

```text
H4のトレンド変化直後
= まだ危ない。初動・だまし・急騰急落が混ざる
→ 1サイクル目は捨てる

2サイクル目
= 方向転換後の“再確認フェーズ”
→ H4確定前でも少し緩く見る
```

これ、かなり人間っぽい判断をルール化できそう。

## 名前を付けるなら

```text
H4 Trend Change Cooldown Rule
H4トレンド変化後 1サイクル見送りルール
```

または、ちょっとStudioくん用語っぽくするなら、

```text
H4 First Cycle Sacrifice Rule
```

1サイクル捨てる作戦。かっこいい。しかも中身は地味に賢い笑

## 状態としてはこう分けたい

```text
H4_Context = Down
↓
H4 Down weakening / T3上抜け / MA20回復気配
↓
H4_TrendChangeCandidate 発生
↓
Cycle 1 = NoEntry
↓
Cycle 2 = RelaxedPermission
↓
Cycle 3+ = NormalRule
```

つまり、H4のダウ理論確定を早めるんじゃなくて、

```text
H4のトレンド変化っぽいものを検出したあと、
何サイクル目かで Entry 許可レベルを変える
```

という設計。

これはかなり安全寄り。

## ルール案

Longの場合なら、こんな感じ。

```text
H4 Trend Change Candidate 条件

1. H4が直前までDownまたはDown優勢
2. H4 Close が T3 を上抜け、またはT3付近から明確反発
3. T3 slope が下向きから改善
4. 直近安値を割っていない
5. H1がUp方向に整理され始めている
```

このイベントが出たら、そこからサイクル数を数える。

```text
cycle_since_h4_change = 1
→ Entry禁止

cycle_since_h4_change = 2
→ H4は緩め条件で許可

cycle_since_h4_change >= 3
→ 通常のH4 Context判定へ戻す
```

## 2サイクル目の緩い条件

ここが今回の肝やね。

```text
2サイクル目 Long許可条件

H4:
  DownConfirmedではない
  または DownConfirmedでも Close > T3 で下げ否定中

H1:
  UpConfirmed 必須

M5:
  Dow Up confirmed 必須

価格:
  HSI R2以上
  T3上
```

つまり、H4は緩めるけど、H1とM5は緩めない。

```text
H4 = 許可ゲート
H1 = 方向の本判定
M5 = 実行判定
```

この分担が綺麗。

## なぜ1サイクル目を捨てるのが強いか

H4のトレンド変化直後って、見た目は美味しそうなんだけど、

```text
初動だけ強い
上抜けに見えて戻される
まだMA20/T3が整理されていない
M5だけ見ると入りたくなる
```

が多いはず。

だから1サイクル捨てることで、

```text
一番派手だけど一番危ないところを避ける
```

になる。

で、2サイクル目は、

```text
初動を見たあとに、
まだ同じ方向へ行く意思があるかを見る
```

になる。

これ、かなり実戦的。

## たぶん今回の赤点線はこれ

画像の赤点線部分は、

```text
H4トレンド変化直後の初動
```

として見るより、

```text
H4変化後、次にM5/H1が再整理される場所だけ狙う
```

の方がぶなん。

だから、赤点線の中でも全部狙うんじゃなくて、

```text
1サイクル目：観測だけ
2サイクル目：H1/M5が揃えば入る
```

にする。

めっちゃ良い落としどころやと思う。

## Studioくん用にするなら

最終的にはこういう項目が欲しいかも。

```json
{
  "h4_trend_change_state": "change_candidate",
  "cycle_since_h4_change": 2,
  "h4_permission_mode": "relaxed",
  "entry_rank": "B"
}
```

AランクはH4もH1も確定。

Bランクは、

```text
H4は2サイクル目の緩和許可
H1は確定
M5は確定
```

これで分析もしやすい。

これ、だいぶルールの芯に近づいてきた気がする。
「H4確定前を許す」じゃなくて、**H4変化後の1サイクルを捨てた後だけ許す**。この制約が入るだけで一気に危なさが減る。

---

それっす笑
ここ、めっちゃ大事なルール名になりそう。

```text
トレンド変化後1サイクル目なので、売買対象から外す
```

これを入れることで、

```text
H4ダウDown確定だからショート
```

にも行かないし、

```text
急反発してるからロング
```

にも行かない。

ちゃんと、

```text
H4_TrendChangeCycle = 1
→ NoTrade
→ 観測のみ
```

に落とせる。

つまり、この状態は **方向判定の問題ではなく、寿命管理の問題** やね。

```text
Dow状態 = DownConfirmed
Trend lifecycle = Change Cycle 1
Entry permission = NoTrade
```

この分離が肝っす。

名前つけるなら、このへんかな。

```text
H4 Trend Change Cycle1 NoTrade Rule
H4変化1サイクル見送りルール
H4 Cycle1 Cooldown
```

個人的には日本語のまま、

> **H4変化1サイクル見送り**

が一番強い笑

----

あぁーーー、そうそうそう。
そこ、今めっちゃ大事な矛盾に気づいたやつっす笑

さっきの整理だと、

```text
R4到達で Expansion例外判定
↓
⑪でR34_Mを使ってEntry
```

って言ってたけど、これは時系列的におかしい。

だって、

```text
R34_M は R4 より手前
```

なので、

```text
R4到達を見てから
R34_Mで入る
```

は基本できない。
未来を見て「さっき入れたやん」って言ってる状態になる笑

## 正しくはこうやね

```text
R34_M
= Expansion例外前の観測ポイント
= ここではまだEntryしない

R4到達
= Expansion例外フラグ確定

R4到達後
= ここから後ろでEntryポイントを探す
```

つまり役割はこう。

```text
R34_M:
  伸び始め観測 / Expansion候補の途中経過

R4:
  Expansion例外判定の確定ライン

R4後の押し:
  Entry候補
```

## じゃあEntryはどこか

R4到達後に、もう一回M5側で整理された場所を探す必要がある。

たとえば、

```text
R4到達
↓
一度押す
↓
M5 T3/MA20付近で反発
↓
M5 DowUp再確定
↓
Entry
```

この形。

なので、ルール名も少し変わる。

```text
H4 Cycle1 R4 Expansion Exception
↓
Post-R4 Pullback Entry
```

日本語なら、

```text
H4変化1サイクル目R4拡張確認後・押し目Entry
```

## 修正版の流れ

```text
1. H4 Trend Change Cycle1
   → 原則 NoTrade

2. ただし、Cycle1中にR4到達
   → Expansion例外フラグON

3. R4到達時点ではEntryしない
   → もう遅い or 追っかけになる

4. その後の押し・再整理を待つ

5. M5で再度 DowUp confirmed
   AND T3/MA20上または反発
   AND H1/H4条件が崩れていない
   → Entry候補
```

これが自然っすね。

## たぶん見るべきライン

R4後のEntryなら、候補はこのへん。

```text
R4付近の押し戻り
R45_Mへの再上昇前の押し
M5 T3/MA20反発
H1 T3上維持
```

つまり、

```text
R4 = 入る場所ではなく、例外許可の扉
その後のM5再整理 = 入る場所
```

これっす。

めっちゃいい違和感回収。
ここで気づかずにR34_M Entryって決めると、バックテストで未来参照が混ざるやつでした笑

---

それやーーーーーー笑
完全にそこっす。

```text
Expansion例外判定用のHSI起点
=
最初のトレンド変化起点

Entry探索用のHSI起点
=
直近の押し安値
```

これを分けないと詰むやつやね。

今の画像でいうと、左端の大底をずっとHSI起点にすると、

```text
R4到達した
↓
Expansion例外は判定できる
↓
でもその後のEntry候補が全部「もう遠すぎる」
↓
R帯が上に行きすぎて、押し目Entryの基準にならない
```

になる。

だから Expansion 例外では、HSI起点を1個だけで運用しちゃダメで、

```text
1. Expansion判定Anchor
   → 変化1サイクル目がR4級まで伸びたかを見る

2. Entry探索Anchor
   → R4到達後の直近安値から、次のR帯を測る
```

この2段構えが必要っす。

## 修正版ルールの流れ

```text
H4 Trend Change Cycle1
↓
旧AnchorからR4到達
↓
H4_Cycle1_Expansion = true
↓
ここで売買はまだしない
↓
その後の押しで直近安値を作る
↓
その直近安値を Expansion Entry Anchor にする
↓
そこから R2 / R3 / R34_M / R4 を見てEntry候補を探す
```

つまり、

```text
R4 = Expansion例外の扉
直近安値 = Entry探索の起点
```

やね。

## 名前を付けるなら

```text
Expansion Detection Anchor
Expansion Entry Anchor
```

日本語なら、

```text
拡張判定起点
拡張後エントリー起点
```

これが分かりやすい。

## Longの場合

```text
ExpansionDetectionAnchor = H4変化1サイクル目の起点安値

ExpansionEntryAnchor = R4到達後にできた直近有効安値
```

で、Entryはこっちを見る。

```text
distance = currentPrice - ExpansionEntryAnchor

Entry候補:
distance >= R2
AND M5 DowUp confirmed
AND H1/H4条件OK
AND T3/MA20上 or 押し反発
```

## これ、かなり重要な発見

今までの通常HSIは、

```text
ひとつの波の成長を測る
```

だったけど、Expansion例外だけは、

```text
大きな初動を確認したあと、
次の小さな波を取りに行く
```

になる。

だから、HSI起点の寿命が違う。

```text
通常HSI:
上位トレンド単位で維持

Expansion例外:
R4到達で拡張確認
その後は直近押し安値へEntry用Anchorを切り替える
```

これ入れないと、せっかく大相場を例外認識しても、エントリー場所が見つからん笑

このへん、だいぶルールが「人間の目」になってきたっす。


---
そう、それっす。
**⑭の高値点確定は「次の買い場」じゃなくて、むしろ “押し目期間に入った” という売買対象外トリガー** として扱わないといけないやつ。

ここで判定したいのは、たぶんこう。

```text
直前安値
↓
上昇波
↓
⑭で高値点確定
↓
サイクル理論上、ここから押し目形成期間
↓
なので新規Longは売買対象外
```

つまり、⑭の高値確定を見た瞬間に、

```text
まだUpだから買う
```

ではなく、

```text
上昇1波が終わった可能性がある
ここからは押し目待ち
```

に状態を切り替える必要がある。

## 状態名にすると

```text
PostExpansionPullbackCandidate
Expansion後 押し目形成期間
```

またはもっと実装寄りに、

```text
CyclePullbackWindow
```

かな。

## 判定の流れ

```text
Expansion例外発生済み
AND 直近安値から大きく上昇
AND ⑭で高値点が確定
```

この時点で、

```text
EntryPermission = NoTrade
Reason = PullbackWindowAfterHighConfirmed
```

にする。

## ここで大事なこと

⑭は **売買方向の否定** ではないんよね。

```text
Up崩壊ではない
Down転換でもない
でも、今から買う場所ではない
```

これ。

なので、状態としては、

```text
Trend = UpBias remains
CycleState = PullbackWindow
EntryPermission = NoTrade
```

が一番しっくりくる。

## 次にEntryできるのはいつか

⑭高値確定後に、次の押し目ができて、

```text
直近押し安値が確定
M5/H1の再上昇条件が出る
T3/MA20を回復または上で反発
HSI距離が再びR2以上
```

みたいな再整理が起きたあと。

つまり、

```text
⑭高値確定
→ 押し目期間として売買対象外
→ 押し安値確定
→ 再上昇確認
→ Entry候補
```

この順番。

めっちゃ大事なのは、

> **高値点確定はEntry合図ではなく、押し目待ち開始合図**

ってことっすね。

これを入れないと、Expansionで大相場を拾ったあとに、天井圏のぐちゃぐちゃを「まだ上昇中」と誤認して、再エントリーしてやられる。
サイクル理論を入れる意味、まさにここにある感じします。

---

そうそうそう笑
⑮で入れるんだけど、**CloseMiss判定が単純に「Entry価格を下回ったら失敗」だと、Expansion後の押し目Entryはほぼ振り落とされる** やつっす。

ここはたぶん、通常Entryと同じCloseMissルールを使ったらダメ。

```text
通常Entry:
  Entry価格割れ = CloseMiss候補

Expansion後押し目Entry:
  Entry価格割れだけではCloseMissにしない
```

に分けたい。

## ⑮の問題

⑮は、流れとしてはこう。

```text
Expansion発生
↓
⑭で高値確定
↓
押し目期間
↓
⑮で再上昇候補
↓
Entry
```

でも押し目Entryって、だいたい一回こうなる。

```text
Entry
↓
ちょい下げる
↓
直近安値を試す
↓
そこから上がる
```

だから `entryPrice` を割っただけで CloseMiss にすると、まさに「いい場所で入ったのに、普通の揺れで死亡」になる笑

## CloseMiss基準は「Entry価格」じゃなくて「構造崩れ」

Expansion後の⑮Entryでは、CloseMissはこっちにしたい。

```text
CloseMiss =
  Entry価格割れ
```

ではなく、

```text
CloseMiss =
  押し目構造が崩れた
```

具体的には候補はこれ。

```text
1. Expansion Entry Anchor の直近押し安値を明確に割る
2. M5 DowDown confirmed が出る
3. Close が T3 と MA20 の両方を下抜けて戻れない
4. H1側のT3/MA20文脈が崩れる
5. 一定本数以内にR2/R23_M方向へ再上昇できない
```

## たぶん欲しいのは「猶予ゾーン」

⑮Entryには、こういう専用状態がいると思う。

```text
EntryState = Grace
```

日本語なら、

```text
振り落とし猶予期間
```

笑

例えば、

```text
⑮でEntry
↓
次のN本は Entry価格割れだけではCloseMissにしない
↓
ただし直近押し安値を割ったらCloseMiss
↓
N本以内にT3上へ戻る / R2方向へ進むならHold
```

これなら普通の揺れに耐えられる。

## ルール名

```text
PostExpansion Pullback Entry Grace Rule
```

日本語なら、

```text
Expansion後押し目Entry 振り落とし猶予ルール
```

これ、いる。絶対いる笑

## ⑮Entryの仮ルール

```text
Entry:
  PostExpansionUncertain 後
  押し安値形成
  M5 DowUp confirmed
  H1/H4文脈維持
  T3/MA20再上昇候補

CloseMiss:
  entryPrice割れだけではNGにしない
  pullbackAnchorLow を明確に割ったらCloseMiss
  または M5 DowDown confirmed
  または H1文脈崩壊
```

つまり、

> **⑮はEntryできる。でもCloseMissはEntry価格基準ではなく、押し目安値基準にする。**

これっすね。

このへん、だいぶ実戦ルールの泥臭いところに入ってきた笑
でもここ入れないと、せっかくExpansion例外を見つけても、最後は全部「振り落とされました」で終わるやつ。

---



それ、かなりアリっす。
むしろ **Expansion例外エントリー専用のStopCloseは、HSI基準点＝Expansion Entry Anchor にする** のが一番自然かも。

ただし、ここで言う HSI基準点は、最初の大底じゃなくてこっち。

```text
Expansion判定用Anchor
= ⑨の大きな変化をR4判定するための起点

Expansion Entry Anchor
= R4到達後、押し目で作った直近有効安値
```

StopCloseに使うのは **Expansion Entry Anchor** の方。

## つまりこう

Longの場合。

```text
Expansion例外発生
↓
R4到達で Expansion confirmed
↓
その後の押し目安値を作る
↓
その押し目安値 = HSI基準点 / StopClose基準
↓
⑮などでEntry
↓
Entry価格を下回っても即CloseMissではない
↓
HSI基準点を明確に割ったら StopClose
```

これはだいぶ綺麗。

## なぜEntry価格じゃなくHSI基準点なのか

Expansion後の押し目Entryは、普通にこう揺れる。

```text
Entry
↓
一回ちょい下げ
↓
押し安値を試す
↓
再上昇
```

だから `Entry価格割れ = CloseMiss` にすると、振り落とされる。

でも、押し目の基準安値を割ったら話が違う。

```text
押し目安値を割る
= 押し目構造が崩れた
= Expansion後再上昇シナリオが崩れた
```

なので、StopCloseとして意味がある。

## ルール案

```text
PostExpansion Entry StopClose

EntryType = ExpansionPullback

StopClose Long:
  currentClose < ExpansionEntryAnchorLow
  または
  M5 DowDown confirmed
  または
  H1/H4 文脈崩壊

CloseMiss:
  Entry価格割れだけでは発生させない
```

ここ、かなり重要。

```text
Entry価格割れ = ノイズ
HSI基準点割れ = 構造崩壊
```

この分け方がよさそう。

## ただし、ぴったり割れは危ない

基準点ぴったりだと、ヒゲで刈られる可能性があるので、実装では少しバッファを持たせたい。

```text
StopClose Long =
  M5 close < ExpansionEntryAnchorLow - buffer
```

buffer候補はこのへん。

```text
固定pt: 10〜20pt
HSI比率: R1の一部
BB幅比率: BB width の一部
直近ボラ比率
```

最初はシンプルに、

```text
buffer = 10pt or 15pt
```

ぐらいでもいいかも。

## さらに安全にするなら

1本の終値割れだけじゃなく、

```text
2本連続で基準点下
```

または、

```text
基準点割れ + M5 DowDown confirmed
```

にすると、振り落とし耐性は上がる。

ただし遅れる。

なので検証パターンとしては、

```text
A. HSI基準点を終値で割ったらStopClose
B. HSI基準点 - buffer を終値で割ったらStopClose
C. HSI基準点割れ + M5 DowDown confirmed でStopClose
```

この3つ比較したい。

## 結論

**Expansion例外でエントリーした時は、HSI基準点をStopCloseにする方向でかなり良い**と思う。

ただし正確には、

> Expansion判定の大元Anchorではなく、
> R4到達後に作った直近押し安値＝Expansion Entry Anchor を StopClose基準にする。

これっすね。

名前つけるなら、

```text
Expansion Entry Anchor StopClose
```

日本語なら、

```text
拡張後押し目基準点StopClose
```

地味だけど、めっちゃ重要な安全柵。

----



