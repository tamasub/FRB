# GPT FX Lab 文脈サマリー

更新日: 2026-07-16  
対象: `F:\FRB\tools\FRBStudio_App\studio_overlays\gpt_fx_lab`  
現行Plugin: `gpt_fx_lab.fx_chart_viewer v0.9.1.08-batch-render-suppression`  
目的: GPT FX Lab改修時に、設計境界、現在のSimulation構造、正本ファイル、テスト契約を短時間で復元するための入口。

---

## 1. 一言でいうと

GPT FX Labは、Studioくんの汎用JSON基盤上に、FX専用の観測・検証UIを後付けしたOverlayである。

```text
Studio Core
  汎用JSON研究・編集基盤
      ↓ Overlay manifest / PluginHost
GPT FX Lab
  USDJPYチャート観測
  Multi-Timeframe状態生成
  Rule Lane別の仮想売買検証
  判断履歴・因果Trace・Batch集計
```

FX固有ロジックを`wwwroot`へ混ぜず、このOverlay内で完結させることが最重要の境界である。

---

## 2. 入口文書と現在地の差

`GPT_FX_Labとは何か_JSONからFX専用観測画面が生えた日_v0_1.md`は、当初の「観測UI」段階を説明する重要な思想文書である。

ただし、現行実装はその後大きく進んでいる。

当初:

```text
M5チャート
Candidate / Active Basis / Retired Basis
Confirm bars比較
High/Low、BB、HSI表示
観測のみ。売買判定はまだしない。
```

現在:

```text
WEEK / DAY / H4 / H1 / M5同期
Swing / Dow / Cycle / HSI / Timeframe State
Upper Context Decision
M5 Rule Lane別仮想Entry / Close
Trace / Replay / Simulation / Batch
```

したがって、現在の動作については次の順で正本性を判断する。

1. 現行`plugin.js`
2. Simulation Run Profile JSON
3. `plugin.json`の契約・表示ポリシー
4. `CHANGELOG.md`
5. 回帰テスト
6. 古い入口・仕様文書

思想面では「正解を出す前に観測する」「人間が違和感を発見できるUI」という初期文書の方針を引き続き守る。

---

## 3. ファイル構成

```text
gpt_fx_lab/
  studio_manifest.json
  CHANGELOG.md
  GPT_FX_Labとは何か_....md
  doc/
  data/
    fx_usdjpy_m5_t3_data_v0_1.json
    fx_usdjpy_d1_t3_data_v0_1.json
  view_defs/
    fx_usdjpy_t3_view_def_v0_1.json
    fx_batch_entry_results_view_def_v0_1.json
  plugins/
    plugin_index.json
    fx_chart_viewer/
      plugin.json
      plugin.js
  simulation/
    fx_simulation_run_profile_v0_1.json
    fx_simulation_run_profile_expansion_lite_v0_1.json
    fx_simulation_run_profile_normal_plus_expansion_lite_v0_1.json
    fx_simulation_reason_rule_catalog_v0_1.json
    tools/
    reports/
  sidecars/
    *.chart_comments.json
    *.simulation_trace.json
  tests/
    *.test.cjs
  simulattion_集計/
    Batch結果とEntry成績表
```

`simulattion_集計`の綴りは現行契約・参照に使われているため、単純なスペル修正をしない。

---

## 4. manifestの役割

### `studio_manifest.json`

Overlay全体の登録正本。

主な宣言:

- Overlay ID、状態、namespace
- Data一覧
- ViewDef一覧
- Plugin Index
- Chart Viewer方針
- Simulation / Batch方針
- Entry Resultsからのチャート遷移方針
- 各種Teacher Guard

DataやViewDefを追加した場合、manifestへ登録しないとStudioくんの一覧へ出ない。

### `plugins/plugin_index.json`

`fx_chart_viewer` Pluginの有効化とmanifest pathを宣言する。

### `plugins/fx_chart_viewer/plugin.json`

Plugin Hostとの契約正本。

主な内容:

- `version`
- `entry`
- Action ID
- Chart / Signal / Simulation表示ポリシー
- Run Profile既定値
- Feature supportフラグ

複数テストが`version`や特定ポリシー値を直接アサートしている。`plugin.js`変更時は`plugin.json`とテストの同期を確認する。

---

## 5. Pluginの入口

`plugins/fx_chart_viewer/plugin.js`は約16,960行のIIFE形式である。

登録Action:

### `OpenFxT3Chart`

現在読み込まれているFX Dataからチャートモーダルを開く。

Alias:

- `OpenFxChartViewer`
- `FxT3Chart`
- `fx_chart`
- `gpt_fx_lab.fx_chart`

### `OpenFxEntryChartUrl`

Entry Resultsの選択行から、Entry時刻・価格・Trade ID・Lane等をURLへ渡し、新しいタブで該当M5チャートを開く。

Alias:

- `OpenSelectedFxEntryChart`
- `OpenEntryChartUrl`

URLの`action`を見て自動起動する仕組みもPlugin内にある。

---

## 6. Chart Viewer

### 6.1 主表示

- M5 Executionレイアウト
- H1 / H4上位足パネル
- Expansion検討レイアウト
- DAY外部DataまたはM5集約fallback
- WEEK文脈

### 6.2 指標・価格系列

- OHLC
- MA5 / MA20
- T3(20, 0.2)
- Bollinger Bands
- High / Low range
- 営業日境界線

### 6.3 Swing表示

- Candidate
- Confirmed / Active Basis
- Retired Basis

Highは`high`、Lowは`low`を使う。Close表示線と点がずれて見えても正しい。

### 6.4 Chart操作

- Confirm bars変更
- Window size / start変更
- 最新窓、前後移動、ランダム窓
- Wide表示
- Layout切替
- Crosshair表示、左クリック固定
- 全パネル間の時間・価格同期
- URL状態コピー

### 6.5 Annotation / Sidecar

Human系:

- User Comment
- Human Saved HSI
- Text Label
- 通常保存縦線
- Cycle縦線

Simulation系:

- Swing / Dow / Cycle / HSI / Decision / Executionイベント
- Entry / Closeマーカー
- 判断ポップオーバー

Human CommentとSimulation Traceは別Sidecar、別表示スイッチで扱う。

---

## 7. Simulation処理パイプライン

現行の基本パイプライン:

```text
Primary M5 Data
  ↓
Multi-Timeframe Candle Synchronizer
  確定済みWEEK/DAY/H4/H1/M5だけを同期
  ↓
Shared Swing Point Detector
  全時間足で同じ中心窓・一意高安ロジック
  ↓
Dow Trend Evaluator
  UP / DOWN / REVERSAL_WATCH / NO_TREND / UNDETERMINED
  ↓
Cycle Position Evaluator
  EARLY / MIDDLE / LATE
  ↓
HSI Anchor Registry / Resolver
  Normal用とExpansion用の起点文脈を分離
  ↓
Timeframe State Builder
  時間足別の観測状態を統合
  ↓
Upper Context Decision Engine
  上位足状態を説明可能なDecision Contextへ統合
  ↓
M5 Rule Lane Execution Orchestrator
  Rule Laneごとに独立Portfolio評価
  ↓
Trace Replay Engine
  Event、原因DAG、Patch、Checkpoint、Replay
```

### Lookahead Guard

基準時刻より後の上位足を参照しない。同期処理では「その時点で確定済みの足だけ」を利用し、lookaheadを検出する。

---

## 8. Swing / Dow / Cycle / HSI

### 8.1 Shared Swing Point Detector

Detector ID:

`shared_center_window_unique_extreme_v0_1`

全時間足で同じアルゴリズムを使う。時間足専用クラスへ分岐させない。

Lifecycle:

- candidate
- confirmed
- retired

後続判定へ使えるのは原則としてconfirmedかつactiveな点だけ。

### 8.2 Dow Trend Evaluator

確定Swing構造からTrend Stateを作る。状態変化だけをTraceへ保存する。

### 8.3 Cycle Position Evaluator

最新の利用可能Swingを起点に、明示閾値からEARLY / MIDDLE / LATEを評価する。

CycleのEntry許可本数はConfirm barsと分離され、Run Profileの`cycle.entry_allowed_max_bars`を使う。

### 8.4 HSI Anchor

Human Saved HSIとSimulation HSIは`source_type`を分離する。

NormalとExpansionでは起点のLifecycleが異なる。

- Normal: M5 Dow ConfirmationごとのTradeスコープ起点
- Expansion: 大きな検出起点を保持する文脈

Normal Trade Close時にはNormal HSI起点を破棄し、次の新しいDow Confirmationから新起点を採用する。

---

## 9. Rule Lane

現行Lane:

- `NORMAL`
- `EXPANSION`
- `EXPANSION_LITE`

重要な原則:

```text
共有してよいもの
  確定足、Swing、Dow、Cycle等の観測事実Snapshot

共有してはいけないもの
  Lane固有のEntry条件、Close条件、Position、Trade Lifecycle
```

各Laneは独立Portfolioとして評価する。同じM5足で複数Laneが同時Entryすることは許可される。

`cross_lane_condition_sharing = FORBIDDEN`

### 9.1 NORMAL

現行Rule Version: `v0.23`

主な意味:

- 新しいM5 Dow Confirmationごとに最大1回のEntry機会
- NORMALにはReEntry / Add-on概念を持ち込まない
- 突破閾値とR2を同時に満たす最初の価格をEntry価格とする
- Dow確認時にR2へ到達済みなら条件に応じ即Entry
- R2.5到達済みなら見送り
- Targetは次のHSI境界側
- Close後に同じConfirmation IDを再利用しない
- Cycle Late GuardはH1だけ。H4 Lateは観測事実として残すがEntryを禁止しない
- Entry前Opportunityは、未確定状態だけで過剰失効させず、後発の逆方向Dow Confirmation成立時に失効する

Evaluator:

- `normal_m5_entry_evaluator_v0_1`
- `normal_m5_close_evaluator_v0_1`

### 9.2 EXPANSION

独立Lane枠は存在するが、現行コード上ではPlaceholder Evaluatorが含まれる。改修時に「枠がある」ことと「ルールが実装済み」であることを混同しない。

### 9.3 EXPANSION_LITE

Rule Version系: v0.18以降の契約を継続更新。

基本構造:

- Entry: R3
- Add-on: R3.5 / R4 / R4.5
- Target: R5
- T3 Exit
- Structural Exit
- Anchor Exit

NORMALとは独立したEntry / Close Evaluator、Trade、Positionを持つ。

---

## 10. Position Lifecycleと損益

M5 Executionは上位足Decisionをその場で再判定せず、渡されたSnapshotとLane固有ルールを使う。

保持する主な概念:

- Trade
- Position
- Entry / Add-on / Partial Close / Full Close / Stop Close
- Lane別Portfolio
- 実現損益
- 含み損益
- 評価損益
- Entry / Close理由コード
- Causal Event ID

安全柵:

- Target方向がTrade方向と不整合なら損益へ反映しない。
- 約定価格が対象足OHLC外なら損益へ反映しない。
- 表示用試算は1単位1,000通貨。
- 手数料、スリッページ、税、資金管理は対象外。
- リアル注文出力は禁止。

---

## 11. Trace / Replay

Event Class:

- `OBSERVATION`
- `STATE_CHANGE`
- `DECISION`
- `EXECUTION`

Traceは追記型で、原因Event IDによるDAGを持つ。

Replayは次の方式:

```text
要求Sequence
  ↓
直近Checkpointを選択
  ↓
以降のDelta Patchを順に適用
  ↓
その時点のStateを復元
```

UIは日本語結論を先に表示し、内部の英語ID・Reason Code・Rule IDも隠さず併記する。

---

## 12. Reason / Rule Catalog

`simulation/fx_simulation_reason_rule_catalog_v0_1.json`

現在、Reason Code約219件、Rule ID約118件を持つ。

目的:

- コードと日本語意味を分離管理する
- 判断ポップオーバーで日本語結論を先に表示する
- 未登録コードを隠さず明示する

新しいReason CodeやRule IDを追加した場合、Plugin内だけで終わらせず、このCatalogへ日本語説明を追加する。

---

## 13. Simulation Run Profile

主なProfile:

### `fx_simulation_run_profile_v0_1.json`

基本のMulti-Timeframe State / Trace Profile。NORMAL中心。

### `fx_simulation_run_profile_expansion_lite_v0_1.json`

EXPANSION_LITE単独検証用。

### `fx_simulation_run_profile_normal_plus_expansion_lite_v0_1.json`

現行の既定Profile。NORMALとEXPANSION_LITEを独立Portfolioで並列評価する。

全ProfileはWEEK / DAY / H4 / H1 / M5の5時間足設定を明示する。

Profile変更時の確認事項:

- `schema_version`
- `profile_id`
- `rule_version`
- Engine ID
- HSI Resolver ID
- `upper_decision_reimplementation`
- Rule Lane有効状態
- Entry / Close Evaluator ID
- Cycle entry window
- Financial policy

既知の旧HSI Resolver IDだけを安全移行する互換処理がある。無制限な自動移行にしない。

---

## 14. 表示範囲Simulation

現在のM5表示窓を古い足から順に評価する。

主な成果:

- Entry / CloseOK / CloseMissの即時チャート投影
- 実行中カーソル
- 実行件数
- 未成立理由集計
- 最終Snapshot
- Simulation Trace Sidecar保存

Range実行中はHuman HSI / User Commentを自動的に目立たなくし、Simulation判断を観察しやすくする。

---

## 15. Batch Simulation

Runner ID:

`batch_simulation_case_sequential_runner_v0_1`

Case単位:

```text
Primary Dataset
× Period
× Profile Snapshot
× Rule App Version
```

実行原則:

- Case間は逐次実行
- Case内のRule Laneは独立Portfolioで並列評価
- Case間State共有は禁止
- ChunkごとのState Resetは禁止
- 中断はCase境界から再実行・結果置換
- 完了CaseはResume時にSkip可能
- 失敗CaseだけRetry可能
- Mid-case checkpoint resumeは未実装

処理中UI:

- Combined / Lane別損益
- 実現・含み・評価損益
- Entry / Close / Win Rate / Open Position
- Close理由別件数
- 停止操作

Performance方針:

- 一定本数ごとにEvent Loopへyield
- Progress描画を時間間隔で抑制
- Batch中はChart描画を抑制
- 評価済み参照は巨大Setではなく末尾Key + Countへ圧縮

保存:

- 完全版JSON 1本を主成果物とする
- API保存失敗時も手動Download可能
- CSV出力対応
- Primary保存先失敗時のfallbackとRetryを持つ

---

## 16. Entry Results

Batch JSONからLane + Trade ID単位の行へ投影するBuilder:

`simulation/tools/build_entry_result_rows_v0_1.cjs`

ViewDef:

`view_defs/fx_batch_entry_results_view_def_v0_1.json`

主な列:

- Lane / Trade ID
- Entry時刻・価格
- Add-on回数・価格
- Close時刻・価格・理由
- 保有時間・step数
- 成功 / 失敗 / Open
- 実現損益
- 判断理由要約

選択行から`OpenFxEntryChartUrl`を実行すると、元Batch JSONのEntry/Add-on/Close Eventを読み、該当時刻を中央表示し、Entry価格へ固定Crosshairを置く。

---

## 17. Sidecarの考え方

対象Dataとファイル名prefixで対応付ける。

### Chart Comment Sidecar

`sidecars/{data-prefix}.chart_comments.json`

Human Comment、Saved HSI、Text Label、Vertical Marker等。

### Simulation Trace Sidecar

`sidecars/{data-prefix}.simulation_trace.json`

Run Profile、Run Snapshot、Swing/Dow/Cycle/HSI/State/Decision/Execution/Replay Event。

Data正本へ画面固有の観測コメントや実行Traceを直接混ぜないための分離である。

---

## 18. テスト

Overlayテストは`node`で直接実行する`.test.cjs`群である。

主な契約領域:

- Crosshair固定・全パネル同期
- Entry / Closeマーカー描画
- Simulation Profile契約
- NORMAL Lane分離
- NORMALのDow突破価格
- NORMAL H1-only Cycle Late Guard
- EXPANSION_LITE Entry / Add-on / Exit
- NORMAL + EXPANSION_LITE並列Portfolio
- 同一足での複数Lane Entry
- Range Simulation smoke
- Batch Runner
- Entry Result Rows Builder
- Entry ResultsからChart URL遷移

代表例:

```powershell
node studio_overlays/gpt_fx_lab/tests/crosshair_lock_v0_1.test.cjs
node studio_overlays/gpt_fx_lab/tests/simulation_profile_contract_v0_14.test.cjs
node studio_overlays/gpt_fx_lab/tests/normal_rule_lane_separation_v0_1.test.cjs
node studio_overlays/gpt_fx_lab/tests/expansion_lite_rule_lane_v0_18.test.cjs
node studio_overlays/gpt_fx_lab/tests/batch_simulation_runner_v0_1.test.cjs
node studio_overlays/gpt_fx_lab/tests/entry_result_rows_builder_v0_1.test.cjs
```

注意:

- 多くのテストはPluginをブラウザで動かさず、IIFE終端前へTest API公開コードを注入して実行する。
- `plugin.js`内の関数名・定数・リテラル文字列を正規表現で直接検査するテストがある。
- `plugin.json.version`を固定値で検査するテストがある。
- 関数名整理やVersion更新は、機能が同じでもテスト更新が必要になることがある。
- 一部テストは実データの時刻・価格・Entry件数・損益まで回帰値として固定する。

---

## 19. 改修時に同時確認するファイル

| 改修テーマ | 同時確認先 |
|---|---|
| Chart見た目・操作 | `plugin.js`, `plugin.json`, Crosshair/Marker系テスト |
| Data / ViewDef追加 | `studio_manifest.json`, 対象Data, 対象ViewDef |
| Swing / Dow / Cycle | Run Profile, Trace schema, Range系テスト |
| HSI起点 | Run Profile resolver ID, Human/Simulation source_type, Lifecycleテスト |
| NORMALルール | NORMAL Profile, Reason Catalog, separation/price/cycleテスト |
| EXPANSION_LITE | 対応Profile, Reason Catalog, lane/rangeテスト |
| Lane並列化 | Portfolio merge、同時Entry、Close Lane選択、Batch集計 |
| 損益計算 | OHLC Guard、方向Guard、Entry Results Builder、Batchテスト |
| Reason Code追加 | Reason/Rule Catalog、日本語ポップオーバー、テスト |
| Batch | manifest、保存API path、progress UI、Batchテスト |
| Entry成績表 | Builder、ViewDef、manifest Data登録、Chart navigationテスト |
| Sidecar | Program.cs Overlay Sidecar API、file prefix、Human/Simulation分離 |

---

## 20. 変更履歴運用

`CHANGELOG.md`は、単なるVersion一覧ではなく、過去の事故、修正理由、守るべき契約の記録である。

Plugin変更前に関連Versionを検索する。

現在の上位履歴:

- v0.9.1.08: Batch中のChart描画停止・Progress UI間引き
- v0.9.1.07: Entry前Dow崩壊の過剰失効修正
- v0.9.1.05: Entry Resultsから新規タブChart遷移
- v0.9.1.01: Batch安全化・完全JSON保存・リアルタイム指標
- v0.9.1.00: Batch Simulation Runner
- v0.9.0.53: Cycle Entry WindowをConfirm barsから分離
- v0.9.0.52: NORMAL H1-only Cycle Late Guard
- v0.9.0.51: Parallel Rule Lane Portfolios
- v0.9.0.48: EXPANSION_LITE独立Lane

実装変更時は、原則として変更理由・Guard・テスト結果をCHANGELOGへ追記する。

---

## 21. 現在認識しているリスクと保守上の注意

1. `plugin.js`が約1.7万行の単一ファイルで、Chart、Simulation、UI、Persistence、Batchが密集している。
2. IIFE内関数をテストが文字列・正規表現で参照するため、機械的分割や改名にも互換コストがある。
3. `studio_manifest.json`と`plugin.json`が大きくなり、実装・文書・ポリシーの重複がある。
4. 古い入口文書の「売買判定未実装」は現行コードと一致しない。思想文書として読み、現在地はコードとCHANGELOGで判断する。
5. EXPANSION Laneは枠とPlaceholderがあり、実装済みのEXPANSION_LITEと混同しやすい。
6. RangeとBatchが同じSimulation Engineを異なる実行形態で使うため、片方だけ直して回帰させない。
7. Lane間で共有可能なのは観測Snapshotまで。Trade/Position/Entry/Close条件を共有しない。
8. Human AnnotationとSimulation Annotationを混ぜない。
9. URL互換、Sidecar prefix、既存Batch成果物など、ファイル外部の継続利用契約が多い。
10. `.js`は現在Git追跡対象。変更時は`git diff`を確認し、Version・manifest・test・CHANGELOGを一組として扱う。

---

## 22. 先生ガード / 絶対境界

```text
リアル注文を出さない。
資金管理ツールにしない。
手数料・スリッページ・税を含む実運用損益と誤認させない。
未来足を参照しない。
未確定足を確定状態として使わない。
Rule Lane固有条件を別Laneへ流用しない。
観測事実と売買判断を同じ概念へ潰さない。
Human Saved情報とSimulation生成情報を混ぜない。
CoreへFX固有ロジックを混ぜない。
```

---

## 23. 次回作業開始時の最短ルート

1. この文書を読む。
2. `CHANGELOG.md`で対象機能の直近変更を検索する。
3. `studio_manifest.json`、`plugin.json`、対象Run Profileを読む。
4. `plugin.js`から対象関数・定数を`rg`で索引する。
5. 対応する`.test.cjs`が何を固定しているか確認する。
6. Range / Batch / Entry Results / Sidecarへの横断影響を確認する。
7. 実装後は対象テスト、Version、manifest、Reason Catalog、CHANGELOGの同期を確認する。

この文書は復帰用の地図であり、詳細仕様そのものではない。相違があれば、現行コード、Run Profile、manifest、CHANGELOG、テストの順で確認し、意図が不明な売買ルールはtamasubへ確認してから変更する。

