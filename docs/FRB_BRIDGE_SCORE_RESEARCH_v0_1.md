# FRB BridgeScore Research v0.1

Date: 2026-08-23  
Status: Research / observation-first

## 1. Purpose

現行 BridgeScore を捨てず **BridgeScore v1 (Legacy)** として固定し、
体感と一致している可能性がある「帯域間のつながり」と「時間安定性」を分解観測する。

この段階では新しい総合スコアを確定しない。

## 2. BridgeScore v1 (Legacy)

Legacy bands:

- Low = 0-80Hz (`b0`)
- Mid = 80-160Hz (`b1`)
- High = 160-250Hz (`b2`)

Formula:

```text
r1 = Mid / (Low + eps)
r2 = High / (Mid + eps)
gap = abs(r1 - r2)
BridgeScore v1 = 1 / (1 + gap)
```

意味は「振動量が大きいか」ではなく、Low→Mid と Mid→High の比率がどれだけ連続しているか。

## 3. Bridge Stability (Research)

BridgeScore v1 の**高さ**とは別責務として、時間方向の安定性を観測する。

```text
rolling window = 1.0 sec
SD = rolling BridgeScore v1 の population standard deviation
Stability = clamp01(1 - 2 * SD)
```

BridgeScoreは0〜1なので、理論上の最大population SD=0.5を使って0〜1へ正規化する。

### 注意

Stabilityが高いだけでは良いとは判断しない。
低いBridgeScoreが一定でもStabilityは高くなる。

したがって以下を分離表示する。

- Legacy Mean（レベル）
- Stability / SD（安定性）

## 4. Research Summary

観測対象:

- Legacy Mean
- Legacy SD
- Legacy P10
- `BridgeScore >= 0.80` 滞在率
- Low / Mid / High 平均
- r1 / r2 平均

## 5. Bridge v1 Breakdown

Legacy Scoreが変化した理由を追えるよう、次を時系列表示する。

```text
Low  0-80Hz
Mid  80-160Hz
High 160-250Hz
```

FRB Compareでは左右で同じY軸最大値を共有し、実値の差を直接比較する。

## 6. Shared implementation contract

Bridgeの計算ロジックは `frb_bridge_metrics.js` に集約する。

```text
Realtime Monitor (app.js)
        ↓
frb_bridge_metrics.js
        ↑
FRB Compare (compare.js)
```

FRB Compareは `bandA` が存在するログでは、保存済み `stairError` をそのまま信頼せず、
共有ロジックからLegacy Scoreを再計算する。

古いログで `bandA` が存在しない場合だけ、互換表示として保存済み `bridgeLegacyScore / stairError` を使用する。

## 7. Log additions

新規ログは次を追加保存する。

Frame:

- `bridgeLegacyScore`
- `bridgeLow`
- `bridgeMid`
- `bridgeHigh`
- `bridgeRatioLowMid`
- `bridgeRatioMidHigh`
- `bridgeRatioGap`
- `bridgeRollingMean`
- `bridgeRollingSd`
- `bridgeStability`

Session metadata:

- `bridgeMetricMeta`

旧 `stairError` は互換性維持のため残す。

## 8. Next question

今回のResearch v0.1では「新しい正解」を作らない。

次に確認する問いは、

> 体感で「凹凸がリアル」「情報が分かる」と感じる状態は、
> BridgeScoreの高さなのか、時間安定性なのか、Low/Mid/Highの特定構造なのか。

である。
