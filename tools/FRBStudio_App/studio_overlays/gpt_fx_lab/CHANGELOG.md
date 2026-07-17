## v0.9.1.13 - 2026-07-16

- NORMAL Entry Gate未成立時に、失敗Gate一覧と各Gateのtrue/false判定をEntry Opportunityへ保存。
- R2初回タッチとDow確定時R2到達済みの両Triggerを区別して記録。
- Batch Case結果へ `normal_entry_gate_failures` と集計を追加。
- Batch全体へ `normal_entry_gate_failures.rows / summary` を追加。
- `batch_*_normal_entry_gate_failures.json` をBatch結果と同時に自動保存。
- Batch画面へ「Gate失敗JSON」「Gate失敗CSV」ボタンを追加。
- 1 Opportunityで複数Gateが失敗した場合、Opportunity件数とGate違反延べ件数を分離集計。
- Simulation Ruleはv0.24のまま。App Versionだけをv0.9.1.13へ更新。

## v0.9.1.12 - 2026-07-16

### Batch Caseが現在チャート環境を継承してEntry 0件になる回帰を修正

- 添付された最新資材はv0.9.1.11を正しく含み、Focused/選択ステップテストではEntryが復帰していた。
- 一方、実際のBatch Caseは`Object.create(state)`で現在チャートの`windowStart / windowSize / UpperMap読込状態`を継承していた。
  - Swing Point分析の`period.from`がBatch対象期間ではなく現在チャート表示窓に依存した。
  - UpperMap DAYが画面側で未読込の場合、Snapshot評価が失敗しても進捗画面はEntry 0件だけを表示していた。
- Batch対象期間からCase専用の分析Windowを生成し、`windowStart / windowSize`を明示固定。
- Profileの`dataset.upper_map.path`からUpperMap DAYをCase単位で読込し、画面側の非同期状態から分離。
- Batch進捗へ`評価失敗 N件`を表示し、0件と評価エラーを区別可能にした。
- Simulation Ruleはv0.24のまま。App Versionだけをv0.9.1.12へ更新。

## v0.9.1.11 - 2026-07-16

### Full Dataset BatchでEntryが0件になる継続Snapshot回帰を修正

- v0.9.1.10適用後、Full Dataset Batchを先頭から実行すると、5,500 / 50,314足まで進んでもNORMAL / EXPANSION_LITEのEntry・Add-onが0件になる回帰を確認。
- 原因は、Dow Trend Snapshotでは`normal_dow_structure_break`を生成していた一方、Entry Evaluatorへ渡すTimeframe Stateの`trend_detail`へ投影していなかったこと。
  - Batch継続Snapshotでは、最初のDown Confirmationに属する`WAITING_R2`がDow崩壊を認識できず残留した。
  - v0.9.1.10の「Active ConfirmationをDow崩壊まで固定」が、崩壊事実欠落により古いConfirmationを固定し続ける結果になった。
- `buildTimeframeStateSnapshot()`で次を明示投影するよう修正。
  - `trend_detail.normal_dow_structure_break`
  - `trend_detail.directional_regime_reset`
- Full Dataset開始フローを模したBatch continuation回帰テストを追加。
  - 2025-10-28 14:30: 最初のDown Confirmation / WAITING_R2を生成。
  - 2025-10-28 17:50: REVERSAL_WATCHで旧Opportunityを`EXPIRED`、Anchor Lifecycleを`AWAITING_NEW_DOW_CONFIRMATION`へ遷移。
  - 2025-10-29 21:04: NORMAL Entry復帰。
  - 2025-10-29 21:39: EXPANSION_LITE Entry復帰。
  - 2025-10-29 21:44: EXPANSION_LITE Add-on復帰。
- Simulation Ruleはv0.24のまま。App Versionだけをv0.9.1.11へ更新。

## v0.9.1.10 - 2026-07-16

### WAITING_R2固定起点・Dow崩壊後Confirmation再検索の回帰修正

- `WAITING_R2`中のNORMAL Entry Opportunityは、最初に有効となったDow Confirmationとprevious Swing由来のNormal HSI Anchorを、Dow崩壊・Entry・Missまで固定する。
  - 後続の同方向Dow Confirmationは観測するが、進行中OpportunityのAnchor・R2・Targetを差し替えない。
  - Entry実行時も最新Contextではなく、固定OpportunityのConfirmation・Anchor・方向をTradeへ引き継ぐ。
- Dow崩壊Barrier後のConfirmation解決を修正。
  - Barrierより前の古いConfirmationをnullへ落とすだけで終了せず、Barrier以後に成立した最新の有効Dow Confirmationを再検索する。
  - 共有M5 Dow Confirmationが復元されるため、NORMALだけでなくEXPANSION_LITEの早期Entry / Add-onも回復する。
- 代表ケースを実データで固定。
  - 誤: Anchor `154.735` / R2 `155.269` / Entry Event `2025-11-17 17:14`。
  - 正: Anchor `154.620` / R2 `155.154` / Entry Event `2025-11-17 17:09`（R2初回タッチ足 17:05）/ Target R2.5 `155.322`。
- 同一処理範囲の回帰比較では、v0.23旧RunがEntry 17件・Add-on 4件・実現損益 +10,096円、誤ったv0.24 RunがEntry 9件・Add-on 0件・実現損益 -9,760円となっていた。ルール厳格化だけでなく、共有Dow Confirmation欠落の実装バグがEntry減少を生んでいた。
- Simulation Rule自体はv0.24のまま。App Versionだけをv0.9.1.10へ更新。

## v0.9.1.09 - 2026-07-16

- Simulation Rule v0.24 のNormal HSI Anchor Lifecycleへ対応。
  - Entry前にM5 Dowが `REVERSAL_WATCH / NO_TREND / UNDETERMINED` へ確定遷移した場合、旧Dow Confirmation・旧Normal HSI Anchor・WAITING_R2 Opportunity・旧R2履歴を一括終了。
  - Dow崩壊後は旧M5 breakout Confirmationを復活させず、新しいDow breakout Confirmation成立までNormal HSI Anchorなし。
  - 再確定後は、再確定点そのものではなく、新しいDow構造のprevious Low / previous Highを新しいNormal HSI Anchorへ採用。
  - 同一構造内の同方向継続だけではAnchorを乗り換えない。
- R2 Entry後のDow崩壊は観測のみ。
  - NORMAL Close EvaluatorはDow崩壊単独ではCloseしない。
  - Entry時のNormal HSI Anchor / Target / StopをTrade終了まで固定。
  - `NORMAL_POST_ENTRY_DOW_BREAKDOWN_OBSERVED_NO_CLOSE` を判断Traceへ記録。
- Profile / Reason Rule Catalog / Test / Incidentをv0.24へ更新。

## v0.9.1.08 - 2026-07-14

### 一括Simulation中のチャート描画停止・進捗UI間引き

- 一括Simulation実行中は、チャートCanvas・通常ヘッダー・凡例・Popover類を非表示にし、Batch Runnerだけを表示。
- Batch実行中に非同期読込などから`redraw()`が呼ばれても、チャート行抽出・候補点生成・`drawChart()`を実行しない。
- Batch進捗更新を50足ごとから250足ごとへ変更。売買Event発生時の進捗通知も500ms未満では再描画しない。
- 停止確認は従来どおり各足で行い、停止操作の応答性は維持。
- Batch終了後にチャートを1回だけ再描画して通常表示へ復帰。

## v0.9.1.07 - 2026-07-14

### Entry前Dow崩壊判定の過剰失効を修正

- `REVERSAL_WATCH / NO_TREND / UNDETERMINED` を `WAITING_R2` Opportunityの失効条件から除外。
- Entry前の失効は、元Opportunityより後に成立した**逆方向M5 Dow Confirmation Event**だけで確定する。
- v0.21/v0.22のH4 HSI Guardとv0.23の`max_loss_to_reward_ratio` Stopは変更しない。
- 回帰テストへ transient state継続、後発逆方向Confirmation失効、古いConfirmation無効を追加。

## v0.9.1.06 - 2026-07-13

- Simulation Rule v0.21〜v0.23の未実装分をFX Simulation Engineへ反映。
- v0.21: `Day Trend=UP`、`H4現在波=DOWN`、H4下降波がR5以上、Entry方向SHORTの場合、新規Short Entryを禁止。
  - NORMAL / EXPANSION_LITEが同じ上位足・HSI観測事実をLane内で独立評価する。
  - 既存PositionのHold / Close、Add-onには影響させない。
- v0.22: NORMAL Rule Laneで、Entry方向とH4現在波方向が一致し、H4波がR4以上進行済みの場合、新規Entryを禁止。
  - Long / Short対称。Day Trendは条件に使用しない。R4到達ちょうどからBLOCK。
- v0.23: NORMALの`WAITING_R2`中にM5 Dow構造が崩壊した場合、Dow Confirmation / 通常HSI起点 / Entry Opportunityを失効。
  - 失効後に同じConfirmationでR2へ到達してもEntryしない。
  - Entry後のDow崩壊は別問題とし、それだけでは自動Closeしない。
- v0.23: Normal CloseMiss StopをJSON設定`max_loss_to_reward_ratio`で計算可能にした。
  - `Reward Distance = |Target - Entry|`
  - `Max Loss Distance = Reward Distance × max_loss_to_reward_ratio`
  - Longは`Entry - Max Loss Distance`、Shortは`Entry + Max Loss Distance`。
  - HSI起点はHard Limitとして残し、倍率Stopが起点より遠い場合は起点側へ制限。
  - Stop価格はEntry時に固定し、勝率からの動的計算は将来対応のまま未実装。
- Run Profile / Plugin Manifest / Reason Rule Catalog / Trace・Execution EventへGuard・Stop計算根拠を追加。
- 回帰テスト`simulation_rule_v0_21_to_v0_23.test.cjs`を追加。既存を含む17テストPASS。

## v0.9.1.05 - 2026-07-13

- Entry成績表の「選択Entryをチャートで開く」を同一タブ遷移から新しいタブ起動へ変更。
  - 成績表を残したまま、チャートを別タブまたはユーザー操作で別ウィンドウ化できる。
- 遷移URLへ `chartLayout=M5_ENTRY` と `upperTf=BOTH` を明示。
  - 初期表示を「M5実行」+「H1+H4」に固定し、選択TradeのEntry/Add-on/Closeマーカーをモード切替なしで確認できる。
- `window.open(..., '_blank')` 後に `opener=null` とし、遷移元との不要な参照を切断。
- Simulation判定・Batch結果・Entry/Exit Event内容は変更していない。表示導線のみの改善。

# v0.9.1.04 — Entry成績表から選択Tradeの実行Eventをチャート投影

- Entry成績表の遷移URLへ、元Batch JSON・Entry Event ID・Exit Event ID・Row ID・売買方向を追加。
- 元 `batch_*.json` の `cases[].execution_events[]` から、選択した `trade_id + rule_lane` のEntry / Add-on / Close / Stop Closeを抽出。
- 抽出Eventを既存Simulation Trace表示へ合流し、Entry/Close実行ラベル・指示線・小型終点ドットをチャートへ表示。
- 選択Entryは黄色グローと「選択」表示で強調。Entry価格の固定十字も維持。
- Batch JSONを読めない場合でも、URLのEntry時刻・価格から最低限のEntryマーカーを生成するfallbackを追加。
- 同一 `trade_id` が別Laneに存在する場合の誤結合を防ぐため、Popover損益集計も `trade_id + rule_lane` で照合。
- 固定Simulation Trace Sidecarは従来どおり読み込み、選択Trade Eventだけを重ねる。

---

# v0.9.1.03 — Entry成績表から該当チャートへURL遷移

- `fx_batch_entry_results_view_def_v0_1.json` の主役ボタンを `OpenFxEntryChartUrl` へ変更。
- 選択行の `entry_time` / `entry_price` / `trade_id` / `rule_lane` をURLへ渡す。
- URL起動時にEntry時刻をM5 Window中央へ寄せ、Entry価格へ固定十字を表示。
- 遷移先Data/ViewDef・field mappingはViewDefの `chartNavigation` 宣言で管理。
- 選択行なし、Entry日時/価格なしは明示エラー。
- `entry_result_chart_url_navigation_v0_1.test.cjs` を追加。

---

# Changelog

## 2026-07-13 — Entry Results ViewDef v0.1

- `batch_*_entry_results.json` を1 Trade 1行で確認する `fx_batch_entry_results_view_def_v0_1.json` を追加。
- 一覧で結果、利益/損失、Lane、LONG/SHORT、Entry日時・価格・理由、終了種別・理由、損益、Add-on、保有時間を表示。
- Detailはwide表示とし、Entry/Exit理由を読み物カード、理由・ルール・Add-on履歴をobjectArrayで表示。
- 成功/失敗、Lane、売買方向、終了種別、Entry日時・Entry理由・終了理由で検索可能。
- 表示中のEntry成績をMarkdown出力し、AI分析用Prompt/Grid JSONを含められる。
- Sidecar生成スクリプトへ `view_def` 参照を追加し、今後生成する `*_entry_results.json` が本ViewDefを自動参照するようにした。
- ViewDef Schema v0.9検証、実データfield照合、Entry Result Rows Builder回帰テストを実行。

## 2026-07-13 — Entry Result Rows Builder v0.1

- Batch結果の `execution_events[]` を、Entry起点で1 Trade 1行へ再構成するNode.jsスクリプトを追加。
- 結合キーを `case_id + rule_lane + trade_id` とし、同一Trade IDを使うNORMAL / EXPANSION_LITEの誤結合を防止。
- Entry理由・使用ルールを理由カタログから日本語化し、Add-on履歴、平均Entry価格、終了理由、成功/失敗、利益/損失、損益、保有時間を `entry_result_rows[]` へ集約。
- 元のBatch JSONは変更せず、`*_entry_results.json` Sidecarを生成する方式を採用。Simulation正本の `result_hash` を壊さない。
- 既存の `batch_20260712_200928.json` と `batch_20260712_230503.json` からSidecarを生成。
- 回帰テスト `entry_result_rows_builder_v0_1.test.cjs` を追加し、Lane別Trade ID衝突、Add-on、未決済、損益分類、実データ115 Entryの結合を確認。

## v0.9.1.01 — Batch Safety / Real-time Event Metrics / Complete JSON Persistence

- Batch処理中のsticky表示を、評価損益合計・実現損益・含み損益・NORMAL評価・EXPANSION-LITE評価へ拡張。
- 実行Event、Entry、Add-on、決済、Exit、利益Close、損失Close、勝率、未決済数をリアルタイム表示。NORMAL / EXPANSION-LITEのLane別内訳とTarget/T3/Structural/Anchor/Stopの決済理由も表示。
- `CloseOK`集計を「すべてのclose Event」から「利益決済」に修正し、損失・建値決済、決済理由を別項目へ分離。
- 停止・完了時の自動保存を、ネスト6ファイル保存から完全版JSON単一ファイル保存へ変更。`simulation/results`を第一経路、`simulation`直下をfallbackとし、保存再試行とエラー詳細表示を追加。手動の結果JSON/CSVダウンロードは継続。
- Expansion-Lite Entry時に、Long Target > Entry / Short Target < Entryを必須化。利益方向にR5 Targetが存在しないEntryを拒否。
- Target / Stop / T3 / Anchorの約定判定へOHLC安全柵を追加。足内到達または寄付きGapとして説明可能な価格だけを約定し、足のHigh-Low外価格を損益へ混入させない。
- 各M5足後に増大していた`evaluated_reference_keys`履歴を、最終Key＋件数へ圧縮。Lane別の二重履歴保持も最終Keyへ限定。
- 進捗描画を「新Event発生時または50足ごと」へ間引き、最初のEvent後に毎足ダイアログを再描画していた性能劣化候補を解消。
- 将来作業として、軽量Mid-Case Checkpoint/真の途中再開、Web Worker化・性能計測、保存API対応後の成果物分割Indexをインシデントへ登録。

## v0.9.1.00 — Batch Simulation Runner / 累計実現損益の常時表示

- Dataset × 期間 × Run Profile Snapshot × Rule/App Version を1 Simulation Caseとして一括実行するBatch Runnerを追加。
- Case間は逐次実行、Case内部では NORMAL / EXPANSION / EXPANSION_LITE を独立Portfolioとしてパラレル評価。条件・HSI起点・建玉・Close条件は相互流用しない。
- CUSTOM期間ではH4/H1の必要文脈分を過去側Warmupとして処理し、集計は指定期間内Eventだけを対象化。Chunk/進捗更新境界でSimulation Stateを初期化しない。
- 処理中ダイアログ上部へ、COMBINED累計実現損益とRule Lane別損益をsticky表示。スクロール中も常時見えるため、途中停止の判断に利用可能。
- 停止要求、Case進捗、M5足進捗、処理フェーズ(WARMUP/TARGET)、実行Event件数を表示。
- Batch結果JSON、Case別集計CSVのダウンロード、Case結果から該当チャートを開く導線を追加。
- Overlay保存APIが利用可能な場合、batch_run_manifest / batch_summary / case_manifest / run_result / events / trace をsimulation/results配下へbest-effort保存。
- 累計損益は1単位=1,000通貨の表示用試算で、手数料・スリッページ・税・資金管理は含めない。

## v0.9.0.53 — Cycle Entry WindowをConfirm barsから分離

- Expansion-LiteのH1 Entry許可条件を、Confirm barsの50%から方向別H1 Cycle起点14本以内へ変更。
- 各時間足Profileへ `cycle.entry_allowed_max_bars` を追加。初期値は WEEK=20 / DAY=45 / H4=14 / H1=14 / M5=20。
- 現時点でExpansion-Liteが参照するのはH1=14だけ。H4/WEEK/DAY/M5は未確定のExpansion仕様へ自動適用しない。
- Confirm bars変更でEntry Windowが変化しない回帰テストを追加。

## v0.9.0.52 — NORMAL H1-only Cycle Late Guard

- NORMAL Rule Laneの新規Entry禁止条件からH4 Cycle Lateを除外。
- NORMALのCycle Late GuardをH1だけへ限定。
- H4 Cycle Lateは観測情報・Expansion判断用として保持し、通常Entry判定には使用しない。
- EXPANSION / EXPANSION_LITEの条件とLifecycleは変更しない。
- NORMAL / EXPANSION / EXPANSION_LITEのパラレル走行契約を維持。


## v0.9.0.51 — Parallel Rule Lane Portfolios

- NORMAL / EXPANSION / EXPANSION_LITEを排他的な選択肢ではなく、独立Portfolioとしてパラレル評価。
- 同一M5足で複数Rule LaneのEntry成立を許可。優先順位による片方の破棄を廃止。
- 各LaneのEntry Opportunity、HSI起点、Trade、Position、Close Evaluator、Exit理由を完全分離。
- 既存の単一`active_trade_id`依存をLane別`active_trade_ids_by_lane`へ拡張。
- EXPANSIONは条件未実装のためWAITを維持するが、並列Portfolio契約の対象として扱う。
# v0.9.0.50 — Expansion-Lite H1方向別サイクル前半判定（2026-07-12）

- ㉗→㉙の対象波で、Expansion-LiteがH1の古い反対方向Cycle起点を参照し、`H1_CYCLE_NOT_FRONT_HALF`でEntryを落としていた不具合を修正。
- Expansion-Lite専用のH1 Cycle Gateとして、Longは最新H1安値候補、Shortは最新H1高値候補を方向別に参照。候補がなければ同方向の最新確定Swingを使用。
- H1サイクル前半を「方向別起点からの経過本数 <= H1 confirm_bars × 50%」で判定。
- H1未確定候補の利用範囲を `EXPANSION_LITE_H1_CYCLE_GATE_ONLY` に限定し、NORMAL / EXPANSIONのDow・HSI起点・Entry判定へ流用しない。
- 実データの㉗→㉙範囲で、2025-10-30 09:44に `Expansion-Lite Entry LONG / R3 153.135`、09:49にR3.5 Add-onが発生する回帰テストを追加。
- NORMALとEXPANSION_LITEの独立評価、同一足のExpansion-Lite優先、建玉Lane専用Closeの契約は維持。

# v0.9.0.49 — NORMAL + Expansion-Lite Independent Rule Lanes

- Expansion-Lite既定ProfileでNORMAL Rule Laneまで無効化されていた不具合を修正。
- NORMALとEXPANSION_LITEを同じRange Simulation内で独立評価。
- 条件・HSI起点・Entry Opportunity・Close Evaluatorの相互流用は禁止。
- 同一足で両Entryが成立した場合のみExpansion-Liteを優先。
- 建玉後はOPEN_TRADE_RULE_LANEのClose条件だけを使用。

## v0.9.0.48 — Expansion-Lite v0.18 独立Rule Lane実装（2026-07-12）

- `EXPANSION_LITE` を `NORMAL` / `EXPANSION` から完全分離した独立Rule Laneとして実装。
- Entry: H4/H1終値がT3方向側、H1 CycleがConfirm基準の前半50%、M5 Dow確定、採用HSI起点からR3タッチ。
- Entry成立順は「Dow確定時にR3到達済み」と「Dow確定後のR3初回タッチ」の両方に対応。
- Add-on: R3.5 / R4 / R4.5の境界タッチごとに各1回。
- Exit: R5タッチ、M5 T3逆抜け、M5 Dow構造破綻、採用HSI起点逆抜けで全建玉Close。
- T3 Exitは Long=`M5 Low < M5 T3`、Short=`M5 High > M5 T3`。Anchor ExitもHigh/Lowタッチ判定。
- チャート表示を `Expansion-Lite Entry` / `Expansion-Lite Add-on` / `R5 Exit` / `T3 Exit` / `Structural Exit` / `Anchor Exit` として理由別に分離。
- Expansion-Lite Entry / Add-onマーカーを通常Entryと異なる紫系で表示。
- Day Cycle PositionはEntry条件へ使用せず、他Rule LaneへのFallbackを禁止。
- plugin versionを0.9.0.48へ更新。

## v0.9.0.47 — 実行コメントのチャート重なり回避（2026-07-12）

- Entry / CloseOK / CloseMiss ラベルの横幅に重なる範囲から、High / Low / Close / MA5 / MA20 / T3 / 表示中BBのローカル価格帯を算出。
- ラベルをその価格帯の外側へ配置し、価格チャート本体の上にラベルが乗る状態を回避。
- 基本は CloseOK=上、Entry / CloseMiss=下を維持し、余白不足時だけ反対側へ退避。
- 小型終点ドットと斜めの直線は維持。
- plugin version を 0.9.0.47 に更新。

## v0.9.0.46 — 実行コメントを近づけて角度調整（2026-07-12）

- Entry / CloseOK / CloseMiss ラベルを、上下端ベタ置きから **チャート近傍の退避位置** へ変更。
- 斜め線は維持しつつ、**遠すぎない距離** と **やや強めの角度** に再調整。
- CloseOK は点の少し上、Entry / CloseMiss は点の少し下を基準にし、近接ラベルのみ段積み回避。
- plugin version を 0.9.0.46 に更新。

## v0.9.0.45 — 実行コメントを斜め線へ変更（2026-07-12）

- Entry / CloseOK / CloseMiss ラベルの指示線を、折れ線から **斜めの直線** に変更。
- ラベルを少し横へずらし、縦線・横線と違う見た目で対象点を追いやすくした。
- 上下レーン配置と終点ドットは維持。
- plugin version を 0.9.0.45 に更新。

## v0.9.0.44 — 実行コメント退避レーン + 指示線整理（2026-07-12）

- Entry / CloseOK / CloseMiss の常時表示ラベルを、チャート内ベタ置きから上下の退避レーン配置へ変更。
- Entry / ReEntry / Add-on / CloseMiss は下側レーン、CloseOK は上側レーンへ寄せ、価格点からラベルまで折れ線の指示線で接続。
- ラベル同士が横に重なる場合はレーンを段積みして、なるべくチャート本体にかぶらないようにした。
- 終点ドットは継続して表示し、どの点を指しているかを維持。
- plugin version を 0.9.0.44 に更新。

## v0.9.0.43 — HSI起点色・十字同期・Entry/Close指示点（2026-07-12）

- HSI起点マーカーの白い外周リングを廃止し、同一起点のR横バー色へ統一。
- 十字カーソルの時刻・価格を、M5 / H1 / H4 / DAY / WEEKの全表示パネルへ同期表示。
- 同期先では時刻に対応する包含足・最寄り足へ縦線を合わせ、価格が表示範囲内なら横線も同期。
- Entry / CloseOK / CloseMissラベルから実際の価格・時刻点へ短い指示線を追加。
- 指示線の先端にDow丸より小さい終点ドットを置き、「どの点のコメントか」を明示。
- Simulation売買判定、HSI計算、Entry / Close Lifecycleは変更しないUI専用パッチ。

## v0.9.0.42 — Normal HSI起点をTrade Closeで破棄（2026-07-12）

- NORMAL TradeのCloseOK / CloseMiss時に、Entryで使用した通常HSI起点を即時破棄。
- 次回Normal Entryは、Close後の新しいM5 Dow Confirmationと新しいprevious Swingを必須化。
- `normal_anchor_lifecycle` をPortfolioへ追加し、ACTIVE → AWAITING_NEW_DOW_CONFIRMATIONをTraceへ記録。
- Simulation HSI線をClose時刻で終了させ、どのTradeまで有効だった起点かを可視化。
- HSI境界ちょうどのEntryでTargetが同一境界になる浮動小数点誤差を補正。
- Expansionの起点維持ルールは変更せず、NORMAL Laneから参照しない。

## v0.9.0.41 — Dow突破閾値での通常Entry価格修正（2026-07-12）

- M5 Dow突破確認時にR2到達済みの場合、確認足Closeではなく「Dow突破閾値とR2の双方を満たす最初の価格」で通常Entryするよう修正。
- LONGは `max(Dow突破閾値, R2)`、SHORTは `min(Dow突破閾値, R2)` を基本約定価格とし、ギャップ時だけ最初の利用可能Openを採用。
- Dow Trend Snapshotに存在していた `breakout_threshold_price` がM5 Executionへ渡る途中で欠落していたため、Confirmation Contextへ保持。
- Entry地点が早まることで、Targetも実Entry地点より先の次HSI境界へ再計算される。
- NORMAL Rule Lane分離、ReEntry/Add-on禁止、Normal Close Evaluator分離は維持。

## v0.9.0.40 — MT4風 十字カーソル＋クリック固定（2026-07-12）

- 既存のカレント縦線を、縦線＋横線の十字カーソルへ拡張。
- 十字カーソルは現在操作中のパネルだけに表示し、他時間足への同期表示は行わない。
- 現在日時をパネル下端、現在価格をパネル右端へ背景付きラベルで表示。
- 左クリックで十字カーソルを固定し、再クリックで解除。固定中はシアン強調と「固定」表示。
- 右クリック注釈、既存Tooltip、ダブルクリック時間同期、HSI/Simulation判定ロジックは変更しない。

## v0.9.0.39 — HSI起点別カラーローテーション（2026-07-12）

- HSI横線へ8色パレット（cyan / amber / violet / lime / rose / sky / orange / teal）を追加。
- 同一 `anchor_id` から描画されるR1〜R7・中間線・起点マーカーを同色で統一。
- HSI起点を時系列順に色ローテーションし、隣接する別起点が同色で重なり続けないよう改善。
- R2.5 / R3.5 / R4.5などの中間観測線も白固定をやめ、起点色を継承した薄色破線へ変更。
- Human Saved HSIとSimulation HSIを同じ色割当対象として扱い、表示範囲を移動しても色スロットが安定するよう全Annotationへ割当を保持。
- HSI色ローテーション回帰テストを追加し、8色・同一起点同色・隣接起点別色・9本目以降の安全な循環を確認。

## v0.9.0.38 — NORMAL Rule LaneからReEntry / Add-on語彙を分離（2026-07-12）

- NORMAL Rule Laneでは `ReEntry` を定義しない。前回Trade終了後に新しいM5 Dow Confirmation Eventで成立したTradeも、独立した `Normal Entry` として記録する。
- NORMAL Rule LaneのActionを `ENTRY / FULL_CLOSE / STOP_CLOSE` に限定し、`REENTRY / ADD_ON` を許可Actionから除外。
- 通常Entry Eventをすべて `event_type=entry / execution.action=ENTRY / entry_mode=NORMAL` に統一し、画面マーカー・Run集計もすべて `Entry` として表示。
- 各通常Entryに `normal_entry_sequence_no` を付与。回数識別はReEntryではなく `Entry #1 / #2 ...` で行う。
- 次の通常Entryには前回Trade終了後の新しいDow確認Eventを必須とする制約を、ReEntryルールではなくNormal Entry Lifecycleとして再定義。
- ReEntry / Add-onは将来のExpansion / Expansion-Lite Rule Lane専用語として予約。既存の古いNORMAL ReEntry Traceも表示・集計時にはEntryとして正規化。
- Normal Entry / Close EvaluatorのWEEK・DAY・Expansion非依存、㉘Entry、通常Close、Normal ReEntry 0件を実データ回帰テストで確認。

## v0.9.0.37 — Rule Lane別Entry / Close分離（2026-07-12）

- 共通観測処理（確定足、Swing、Dow、T3、Cycle、BB、HSI候補）と、売買ルール固有の判定を分離。
- 通常ルールを `NORMAL` Rule Laneとして独立し、`normal_m5_entry_evaluator_v0_1` と `normal_m5_close_evaluator_v0_1` を追加。
- Normal Entry EvaluatorはH4/H1 T3、H4/H1 Cycle、M5 Dow Confirmation、Normal HSI Anchorだけを使用し、WEEK / DAY / Expansion判定を参照しない。
- Normal Close Evaluatorは、Entry時に固定したStop / TargetとM5 High / Lowだけで判定し、Entry Rule Laneと同じLaneのClose Policyを適用。
- Expansion / Expansion-Liteは独立したRule Laneとして予約し、現時点では無効・未実装。Normal Laneへ条件が混入しない構造に変更。
- HSI ResolutionをTimeframeStateへ圧縮する際に `dow_confirmation_id` が欠落し、㉘のDow突破Entryが `HSI_ANCHOR_CONFIRMATION_MISMATCH` で止まる不具合を修正。
- 実データの表示範囲Simulationで、2025-10-30 09:44にNormal Entry 153.498、11:09にNormal Close 153.562が発生することを回帰テスト化。
- Expansion設定やWEEK / DAYの上位DecisionがBLOCKEDでも、Normal Entry / Close結果が変わらない分離テストを追加。

## v0.9.0.36 — Simulation Profile契約不一致修正（2026-07-12）

- `fx_simulation_run_profile_v0_1.json` の `upper_decision_reimplementation` と、Plugin側の許可値が別名になっていたため、表示範囲Simulationが開始前検証で停止する不具合を修正。
- 正式値を `normal_entry_v0_14_m5_dow_breakout_next_hsi_boundary_explicit_exception` に統一。
- Plugin内の初期値と許可リストを単一の定数から参照し、同一ファイル内で名称が再び分岐しにくい構造へ変更。
- 実際の `validateSimulationRunDraft` をNode上で呼び出し、同梱Run Profileが `valid=true / errors=0` になる回帰テストを追加。
- M5 Dow突破確認、R2以上で即Entry、次HSI境界Target、同一Confirmation ID再利用禁止のv0.14売買ロジックは変更しない。

## v0.9.0.35 — M5 Dow突破確認 / 次HSI境界Target（2026-07-12）

- M5 Dow Confirmation Eventを、High/Low比較ペア完成時ではなく、確定済み押し安値/戻り高値の後に直前構造高値/安値をM5確定足で突破した時点へ変更。
- Dow確認時点ですでにR2以上なら、その確認足の利用可能価格で即Entry。
- 新しいDow確認でEntryする場合、R2.5を通過済みでも見送りにせず、実Entry地点より先の次HSI境界をTargetとして固定。
- 1 Confirmation IDにつき最大1 Entry、同じ確認IDを使う階段ReEntry禁止、ReEntryは前Trade終了後の新しいDow突破確認Event必須を維持。
- Expansion Detection AnchorのLifecycleは変更しない。

## 2026-07-12 v0.9.0.34

- 通常Entryの判定順を修正。M5 Dow Confirmation Event成立時点でR2到達済みかを先に判定する。
- Dow確認時点でR2以上かつR2.5未到達なら、R2境界へ遡らず確認時点の利用可能価格で即Entryする。
- Dow確認時点でR2未到達なら、確認後のR2初回到達を待ってEntryする。
- Dow確認またはR2初回到達を確認したM5足でR2.5へ到達済みの場合は、Target消化済みとしてMISSEDにする。
- 1 Dow Confirmation IDにつき最大1 Entry、R2.5全Close、同一確認IDの階段ReEntry禁止、ReEntryには前Trade終了後の新Dow確認必須というv0.12の骨格は維持する。
- Simulation Rule v0.13、Run Profile、plugin.json、理由コード・ルールIDカタログを同期した。

## 2026-07-12 v0.9.0.33
- 通常M5 Entryを、`1 M5 Dow Confirmation ID = 最大1回のEntry機会`へ変更。
- High側・Low側の比較ペアが両方とも前回確認から進んだ完全な新Dow構造ごとに、方向Stateとは別の`dow_confirmation` Eventを発行。片側だけの更新ではReEntry切符を発行しない。
- 通常Entryは、Confirmationに紐づくprevious Low / previous High起点から`R2初回到達`した瞬間だけ許可。
- R2初回到達時にH4/H1 T3・Cycle・建玉条件が揃わない場合は`MISSED`とし、R2.5 / R3帯から遅れてEntryしない。
- 通常Targetを常に`R2.5`へ固定し、10単位を1回で全Close。
- 同じDow Confirmation IDを使った階段ReEntryを禁止。ReEntryには前Trade終了後に発生した新しいDow Confirmation Eventを必須化。
- Simulation Rule v0.12のEntry Opportunity状態（WAITING_R2 / USED / MISSED / EXPIRED）をPosition Lifecycleへ追加。

## 2026-07-11 v0.9.0.32
- `fx_simulation_run_profile_v0_1.json` と `plugin.json` の HSI Anchor Resolver契約を `normal_dow_reset_plus_expansion_detection_retain_resolver_v0_3` へ同期。
- 通常Laneは `REVERSAL_WATCH / NO_TREND / UNDETERMINED` で起点解除し、同方向Dow再成立時も新しい previous Swing を採用する契約へ統一。
- Expansion Detection Laneだけは非方向状態を挟んでも旧大起点を維持し、Entry用の押し戻り起点とは分離。
- 既知の旧Resolver `dow_regime_fixed_plus_expansion_dual_anchor_resolver_v0_2` を読込時にv0_3へ安全移行し、Profile更新漏れによるRange Simulation停止の再発を防止。

## 2026-07-11 v0.9.0.30
- 通常Dow起点をREVERSAL_WATCH / NO_TREND / UNDETERMINEDで解除。
- 同方向Dow再成立でも新しいprevious Swingを採用。
- Expansion Detection Anchorだけは非方向状態を挟んでも旧大起点を維持。
- Simulation Ruleをv0.11へ更新。

## v0.9.0.28 - 2026-07-11

- M5 Dow成立時に採用する通常HSI起点の選択を修正。
  - Dow UP: 比較した2つのLowのうち、波の始点側 `previous Low` を採用。
  - Dow DOWN: 比較した2つのHighのうち、波の始点側 `previous High` を採用。
- 従来の `current Low / current High`（成立直前のHigher Low / Lower High）採用を廃止。
- 同方向Dow継続中は採用起点を維持し、反対方向Dow成立時だけ再採用するv0.9の固定契約は維持。
- Expansionは元Dow起点をDetection Anchorとして保持し、Entry用の押し戻り起点を別管理する二重起点方式を維持。
- Simulation Ruleをv0.10へ更新し、旧v0.9 Trace/建玉はFlatから再評価。

## v0.9.0.25 - 2026-07-11

## v0.9.0.27 - 2026-07-11

- 通常HSI起点を「最新の有効Swing」から「M5 Dow directional regime成立時の構造起点」へ変更。
- 同方向Dow継続中は、後続の赤丸・緑丸が確定しても通常Entry用HSI起点を変更しない。
- 反対方向Dow成立時のみ、通常Entry用HSI起点を新しい方向の構造起点へ更新。
- Expansionでは元Dow起点をDetection Anchorとして残し、押し戻り起点をExpansion Entry Anchorとして別管理する二重起点構造を追加。
- Simulation Rule v0.9を同梱。


- ページ上部を「操作系ボタンだけ」の1段ツールバーへ再編。
  - 古い窓 / 新しい窓 / ランダム窓 / 最新窓
  - Expansion検討 / M5実行
  - URLコピー / 表示範囲Simulation / Run設定
  - 注釈操作 / 保存 / 100本移動 / 再抽出 / 閉じる
- Confirm bars、表示窓件数、上位足Confirm・余白、上位足表示、Basis表示、H/L・BB、HSI、注釈表示をモデルレスの「表示・解析設定」パネルへ移動。
- 設定パネル外のチャート操作を継続できるモデルレス表示とし、設定変更は即時再描画する。
- H4営業日境界線を白実線から細い点線へ変更。
  - Confirm stride線より太く・濃くして区別可能にする。
  - H4大局チャートを支配しない存在感へ抑制。
- Simulation Rule v0.8、Single Close、HSI起点Stop、Run累積損益ロジックは変更なし。

## v0.9.0.23 - 2026-07-11

- 通常M5 EntryをSimulation Rule v0.8へ緩和。
  - H1 Dow Trendを通常Entry条件から除外。
  - H1はH4と同様に、T3の傾きと確定足終値のT3上下位置だけで方向判定。
  - H4 T3とH1 T3が同方向で、M5 Dowが同方向へ確定した場合にEntry候補とする。
  - H4/H1 Cycle Late Guard、確定済みHSI起点、R2距離条件は維持。
- 「累積確定」をTrade単位ではなく、同一Simulation Run内の全終了Trade合算へ修正。
  - 既存Traceでも画面表示時にClose/Stop Eventを先頭から再集計して補正。
  - 「初期リスク比 / R」は従来どおり、現在Entryの初期リスクに対する現在Tradeの確定損益で計算。
- v0.8へRule Versionを更新し、旧v0.7建玉状態は引き継がずFlatから再評価。

## v0.9.0.22 - 2026-07-11

- Simulation Rule v0.7へ建玉管理を変更。
  - 1 Entry = 1 Position = 1 Stop = 1 Target = 1回の全Close。
  - 通常Entryは10単位を一括保有し、Partial Close / Scale-out / Runnerを廃止。
  - 通常Add-onを禁止。ReEntryは前Trade終了後に新しいTrade IDとして作成。
- StopをEntry時に使用したHSI起点へ固定。Entry後に新しいHSI起点が確定しても既存Stopを差し替えない。
- TargetをEntry位置の次HSI境界へ固定し、M5 High / LowがTargetへ到達した時点で全単位CloseOK。
- Stop判定もM5 High / Lowで行い、HSI起点へ到達した時点で全単位StopClose。
- 同一M5足でStopとTargetの両方へ到達した場合は `AMBIGUOUS_STOP_TARGET` を記録し、保守的にStopを優先。
- 通常Entry最小HSI距離を従来ルールのR2へ戻した。
- 円損益、初期リスク、R換算、Simulation HSI、営業日境界線は維持。

## v0.9.0.21 - 2026-07-11

- 最新1000足の診断で `HSI_R2_NOT_REACHED = 1000件` となり、Entry条件の最大ボトルネックがHSI距離であることを確認。
- 通常M5 Entryをv0.6.1実験版へ更新。
  - H4 T3方向、H1/M5 Dow一致、H4/H1 Cycle Late Guardは維持。
  - HSI最小Entry距離だけを `R2` から `R1` へ緩和。
  - H4 Dow、WEEK Season、DAY Expansion Grade、Expansion Confirmedは引き続き通常Entryに使用しない。
- HSI最小距離の理由コード・Rule IDを設定値から動的生成し、R1/R2切替時に表示文言が食い違わないよう修正。
- 既存の営業日境界線、COMMON_SCALE_OUT、HSI起点Stop、円損益、R換算、Simulation HSI描画は維持。

## v0.9.0.20 - 2026-07-11

- 通常M5 EntryルールをSimulation Rule v0.6へ改定。
  - H4 Dow判定を通常Entry条件から除外。
  - H4はT3の傾きと、確定足終値がT3のどちら側にあるかだけで方向を許可。
  - H1 DowとM5 Dowが同方向に一致した場合だけEntry / ReEntry / Add-onを許可。
  - H4またはH1がCycle LateならEntry / ReEntry / Add-onを禁止。
  - 確定済みM5 HSI起点からR2以上を必須条件として維持。
  - WEEK Season、DAY Expansion Grade、Expansion Confirmedは通常Entry条件に使用しない。
- H4/H1/M5の判定内容をTrigger Eventへ保存し、H4 T3方向、H1/M5 Dow、H4/H1 Cycle Phaseを理由表示で確認可能にした。
- M5 / H1 / H4チャートへ営業日切替縦線を追加。
  - `row.date`の変化点を営業日境界とし、datetimeの日付をフォールバックに使用。
  - Confirm stride線（1.1px）より一段太い2.1pxの白実線で表示。
  - サイクル縦線、保存縦線とは別の自動表示として扱う。
- 既存のCOMMON_SCALE_OUT、HSI起点Stop、円損益、R換算、Simulation HSI描画は維持。

## v0.9.0.16 - 2026-07-11

- Simulation判断ポップオーバーを完全ダーク表示へ固定し、白背景・白スクロール領域・横スクロールを抑制。
- 判断ポップオーバー右上へ常時表示の `×` を追加。下部の閉じるボタンも維持。
- 表示範囲Simulation開始時に既存の判断ポップオーバーを閉じ、ライブ中継中の自動起動を禁止。
- Human HSI（現在HSI / 保存HSI）とSimulation HSIを別state・別source_typeとして完全分離。
- Simulation開始時にHuman HSIとUserコメントを自動OFF。サイクル縦線は維持。
- Range Runnerが各時点で採用したM5 Entry用HSI起点を収集し、認定された瞬間に `SIM HSI NEW` とR1〜R7横線をライブ描画。
- Simulation HSI一覧をTrace Sidecarの `simulation_hsi_annotations` と `range_run.simulation_hsi_annotations` へ保存。
- 上部の設定値・状態Pill群をデフォルト非表示にし、`状態表示` ボタンで折りたたみを切り替え可能にした。
- Entry / Close / HSI認定ロジック自体は変更せず、表示責務とHuman/Simulation境界を整理。

## v0.9.0.15 - 2026-07-11

- Simulation Traceポップオーバーの「理由・使用ルール」を日本語中心へ変更。
  - Eventごとの日本語判断を最上部へ大きく表示。
  - 理由コードと日本語内容を対応表で表示。
  - ルールIDと日本語内容を対応表で表示。
- `simulation/fx_simulation_reason_rule_catalog_v0_1.json` を追加。
  - 理由コード、ルールID、日本語内容、Event別の判断文テンプレートを外部JSONで管理。
  - 未登録コードは隠さず「日本語説明未登録」と明示し、カタログへ追加できる。
- Entry / Close / Simulation判定ロジックは変更していない。表示と説明責務だけを追加。

# v0.9.0.14 — 表示範囲Simulation ライブ再生・ワクワク可視化 (2026-07-11)

- Simulation実行中の現在評価地点を、M5チャート上へ黄色の点線縦線と下向き▽カーソルで表示する。
- カーソル横へ `SIM 現在足 / 全足 / Event件数` を表示し、処理がどこまで進んでいるかをチャートだけで追えるようにする。
- 同じ基準時刻をH1/H4等の上位足パネルにも細い同期線として表示し、現在評価中の上位文脈を見渡せるようにする。
- Entry / ReEntry / Add-on / CloseOK / CloseMissが発生した時点で、Range完了を待たずにチャートへ逐次投影する。
- 新しく発生した実行Eventは `NEW` と発光表示し、次の進捗描画まで強調する。
- 大きな表示窓では10足ごと、小さな表示窓では5足ごとにライブ再描画し、Event発生時は即時再描画する。
- 実行開始時は前回のSimulationマーカーをいったん外し、今回生まれたEventだけをライブ表示する。完了時は正式なRange結果へ置き換える。
- Entry / Close判定、上位足Decision、HSI起点、R距離、建玉Lifecycleのルールは変更していない。今回の目的は「待ち時間を観測体験へ変える」こと。

---

# v0.9.0.13 — 表示範囲Simulation 0件結果の可視化 (2026-07-11)

- `表示範囲Simulation` 実行時、チャート上部へモデルレス結果パネルを表示する。実行中・成功・0件完了・例外を明確に区別する。
- 実行Eventが0件でも「何も起きなかった」ように見せず、評価済みM5足数と `Entry / Close` 0件を明示する。
- 各M5足のTrigger判定から、Action件数、未成立Reason Code、通常Entry Permission、上位足Entry禁止理由を集計する。
- 0件完了時は、`M5方向不一致`、`R2未到達`、`通常Entry禁止`、`H4反転監視` などの主因を件数付きで表示する。
- トップボタンの完了表示を `E0 / OK0 / Miss0` から `評価足数 / 実行Event件数` へ変更し、実行自体が完了したことを判別しやすくする。
- Entry / ReEntry / Add-on / CloseOK / CloseMiss が成立した場合のチャート直描画ロジックは変更しない。
- 判定ルールは緩和していない。今回の変更は「0件も検証結果である」ことを見える化する診断・UI追補。

---

# v0.9.0.12 — 表示範囲Simulation / Entry・CloseOK・CloseMiss直描画 (2026-07-11)

- トップメニューへ `表示範囲Simulation` ボタンを追加。現在表示中のM5窓だけを対象にする。
- 表示範囲の古い足から新しい足へ、既存の `reference_point_step` を自動で順番に実行するRange Runnerを追加。上位足DecisionやM5 Executionロジックは二重実装せず、既存一点診断を再利用する。
- 表示範囲開始時点は建玉なし（Flat）として開始し、Core / Add-on / RunnerのLifecycleを範囲内で前方向へ引き継ぐ。
- 実行Eventだけをチャートへ投影し、`Entry` / `ReEntry` / `Add-on` / `CloseOK` / `CloseMiss` の文字ラベルを常時表示する。
- `partial_close` と `close` は `CloseOK`、`stop_close` は `CloseMiss` として人間向け表示する。内部Event Typeと原因Traceは維持する。
- マーカーをクリックすると、既存Simulation Trace Popoverで判断理由・Rule ID・原因Eventを確認できる。
- Run設定パネルにも `表示範囲を実行` を追加し、一点保存は補助機能として残す。
- 実行進捗、Entry件数、CloseOK件数、CloseMiss件数をボタンとRun状態パネルに表示する。
- 結果はTrace Sidecarの `range_run` と最終 `run_snapshot` へ保存する。全地点の巨大Snapshotは保存せず、範囲実行Eventと最終状態だけを保持する。
- Range実行中は各足ごとのTrace Replay全再構築を省略し、実行EventとLifecycle継続に必要な状態だけを引き継ぐ。一点診断時のReplayは従来どおり維持する。
- M5基準足の再正規化をCandle Source Cacheへ統合し、Cycle経過本数計算を二分探索化。判定ルールを変えずに連続実行を軽量化する。
- 先生ガード: 過去チャート検証用の仮想表示であり、リアル注文、資金管理、手数料、スリッページ、売買推奨は対象外。

---

# v0.9.0.11.1 — Run設定モデルレス・可変幅化 (2026-07-11)

- Run設定 / 状態確認を、チャート全体を覆うモーダルから、チャート本体上に浮くモデルレスパネルへ変更。
- パネル表示中も、パネル外のチャートをスクロール・右クリック・同期操作できるようにした。
- パネル上部をドラッグすると位置を移動できる。
- パネル左端のシアン色ハンドルを左右へドラッグすると横幅を変更できる。
- `位置戻す` ボタンで右上の初期位置・初期幅へ戻せる。
- パネルはチャートBody内へ配置し、トップメニューや画面全体を暗転させない。
- M5仮想実行・建玉Lifecycle・Trace内容そのものは変更していない。UI操作性だけの追補修正。

---

# v0.9.0.11 — M5 Execution / Position Lifecycle (2026-07-11)

- Upper Context Decisionを入力にし、M5側ではWEEK / DAY / H4 / H1判断を再実装しない共通Execution Engineを追加。
- 初期実装は`reference_point_step`。M5右クリック等で選んだ基準地点を1点ずつ保存し、同じM5確定足の重複実行を防止する。
- 仮想実行Actionとして、新規Entry / 再Entry / 買い増し / 一部決済 / 全決済 / 損切り決済を定義。優先順位はStop → Full Close → Partial Close → Add-on → ReEntry → Entry。
- Entry初期条件は、上位足の通常探索許可、M5 Dow方向整合、確定済みHSI Entry起点、起点からR2以上。Expansion探索は明示的なExpansion確定条件が未実装のため通常Entryへ丸めずWAITとする。
- 10単位をCore 9 + Runner 1へ分離。Add-onは別Positionとして保持し、各PositionにEntry時間足、管理時間足、管理上限DAY、構造無効化価格、次HSI境界Target、Promotion Historyを保存する。
- 損失先送り目的の管理時間足昇格とWEEK昇格を禁止。通常CoreはH1、Expansion CoreはH4、RunnerはH4を初期管理時間足とする。
- Execution EventをTrace Replayへ統合し、M5 Trigger判断 → 上位Decision → Timeframe State → Swing / HSI起点まで逆追跡可能にした。過去SnapshotのTraceは基準時刻が前進する場合のみ引き継ぐ。
- Run設定画面へ「M5実行・建玉ライフサイクル」を追加し、現在の実行判断、Core/Add-on/Runner、残数、Entry価格、管理足、次Target、無効化価格、実行履歴を日本語表示。
- チャートには実行EventだけをSimulationコメントとして投影。Entry系は緑、決済系は青、Stopは赤で区別。
- 先生ガード: 過去チャート検証用の仮想売買であり、リアル注文、資金管理、手数料、スリッページ、売買推奨は対象外。

---

# v0.9.0.10 — Simulation Trace / Replay Log (2026-07-11)

- Swing観測、Dow / Cycle / HSI / Timeframe Stateの状態変化、Upper Context Decisionを、`観測 / 状態変化 / 判断 / 実行`の4区分へ統合。
- Eventを追記型で保持し、`sequence / event_class / domain / cause_event_ids / replay_patch`を追加。各Eventへの全State複製は行わない。
- 50Eventごとの定期Checkpointと最終Checkpointを生成し、任意sequenceを「最寄りCheckpoint + 後続差分」で復元可能にした。
- 原因参照をDAG検査し、Event ID重複、原因欠落、循環参照、結果より未来の原因参照を拒否。
- Run設定画面へ「判断履歴・再生ログ」を追加。前後移動、スライダー、復元State、選択Eventからの原因逆追跡、Event一覧を日本語中心で表示。
- Upper Context Decision表、Run設定タイトル、Simulation Trace Popoverの主要ラベルを日本語化。Rule ID / Event ID等の安定内部IDは維持。
- Run Snapshot schemaをv0.9へ更新し、`trace_replay`と`run_result`を保存。Run / Event / Resultを論理分離。
- M5 Trigger判定、Entry / Close実行は未実装。実Runの`execution_event_count`は0件を期待し、`NO_EXECUTION_YET`を明示。

---

# v0.9.0.09 — Upper Context Decision Engine (2026-07-11)

- WEEK / DAY / H4 / H1 TimeframeStateを、優先順位付きSpecification / Rule Registryで統合。
- NoTrade・Data不足・H4未判定を許可Ruleより先に評価し、後段Ruleによる危険条件の上書きを防止。
- Direction Bias、Normal / Expansion Entry探索、ReEntry、Add-on、Core Hold、Profit Take Armed、H1 Exit Trigger監視をDecision Context JSONへ追加。
- WEEK LateではExpansion Entry / ReEntry / Add-onを禁止し、WEEK自身は直接CloseせずH1 Exit監視を有効化。
- H4 Late + BB Contracting + HSI ConfluenceでProfit Take Armed。利益確定判断=H4、Exit Trigger=H1、Execution=M5の責務を明示。
- reason_codes / rule_ids / input_state_ids / Decision Change Traceを保持し、UIへDecision MatrixとMatched Rule表を追加。
- M5 Trigger判定、Position前提評価、Entry / Close実行は未実装。

---

# v0.9.0.08 — Timeframe State Builder (2026-07-11)

- WEEK / DAY / H4 / H1 / M5へ同一のTimeframe State Builderを適用。時間足別Stateクラスは作らず、時間足はデータとして扱う。
- 同一M5 Reference Closeを`state_as_of`として、確定足・Swing・Dow TrendState・Cycle Position・HSI Anchor・BB観測を時間足別State JSONへ統合。
- 各Stateに安定`state_id`、`latest_confirmed_bar`、`source_event_ids`、`source_bar_keys`を持たせ、元のSwing/Dow/Cycle/HSI Traceへ逆参照可能にした。
- `data_sufficiency`を市場状態と分離。履歴不足・起点不足・方向未解決と、相場自体の`UNDETERMINED`を別に読めるようにした。
- BBは確定済みCloseだけから共通計算し、`SQUEEZE / OPENING / EXPANSION / MATURE / CONTRACTING / STABLE / UNDETERMINED`を観測Phaseとして保持。売買判断には使用しない。
- 保存済み前回Snapshotがある場合、Trend / Cycle / BB / HSI起点 / Data Sufficiency / 最新確定足の差分を`comparison_to_previous_snapshot`へ記録。
- Run設定画面へ時間足別State表を追加。Snapshot保存後は、各時間足の現在State要約をSimulation Traceコメントとしてチャートへ投影。
- Run Snapshot schemaをv0.7へ更新し、`timeframe_states`を保存。
- 先生ガード: TimeframeStateは観測結果の集合であり、Entry / Add-on / Hold / Close PermissionやM5売買は未実装。

---

# v0.9.0.06 — Cycle Position Evaluator (2026-07-11)
## v0.9.0.07-hsi-anchor-registry-resolver — 2026-07-11

- 全時間足共通の HSI Anchor Registry / Resolver を追加。時間足別専用クラスは作らず、Swing Point / Dow / Cycle Snapshotを入力として使用。
- HSI Anchorを `CANDIDATE / CONFIRMED / RETIRED` のLifecycle、`NOT_ELIGIBLE / AVAILABLE / ADOPTED / RETIRED` の採用状態、複数Roleへ分離。
- Purpose Resolverとして Entry / Hold / Target / Thesis / Confluence の**構造参照候補**を生成。Action Permission・売買Signalは出力しない。
- Human Saved HSI (`human_hsi`) と Simulation Anchor (`simulation_hsi_anchor`) を分離し、Human HSIは比較導線のみで自動採用しない。
- M5右クリックメニューへ「この時点の状態を見る」を追加し、一点観測のReference Pointを固定してRun設定画面を開けるようにした。
- Simulation Trace Popoverを左右優先、収まらない場合は下/上へ逃がす自動配置へ変更し、トップメニューへのはみ出しを抑制。
- Entry / Close / Action Permissionは未実装。


- WEEK / DAY / H4 / H1 / M5へ同一のCycle Position Evaluatorを適用。時間足別Evaluatorクラスは作らず、時間足ごとの閾値・役割・状態マッピングをRun Profileから渡す。
- Cycle originは、各時間足の最新「Confirmed + usable Active Swing」とする。未確定Candidateと現在Retiredの点は現在起点に使用しない。過去にActiveだったRetired点は履歴再生のため保持する。
- 起点がSwing LowならUP_CYCLE、Swing HighならDOWN_CYCLEとして、起点足を0本目とし、その後に確定した足数をelapsed_barsとして算出。
- EARLY / MIDDLE / LATEの閾値は各時間足Profileへ明示。Confirm barsや他時間足から暗黙計算・継承しない。
- WEEKはOPEN / CAUTION / CLOSED、DAYはOK / WARNING / NOT_EXPANSION、H4はGROW / MANAGE / PROTECTへ状態を写像するが、Entry禁止・Add-on禁止・Exit許可はまだ出力しない。
- `cycle_origin_changed` / `cycle_phase_changed` Eventを生成し、origin Swing Confirm Event、明示閾値、経過本数、Before/Afterへ逆追跡可能にした。
- Run設定画面へ時間足別Cycle表を追加し、Origin、方向、経過本数、Phase、Context State、閾値、変更数を確認可能にした。
- Run Snapshot schemaをv0.5へ更新し、`cycle_position_evaluation`を保存。チャートには各時間足の最新Cycle State EventだけをSimulation Traceとして投影。
- 先生ガード: 今回はCycle Positionの観測まで。Cycle StateはAction Permissionではなく、HSI Anchor / Entry / Add-on / Hold / Close / M5売買は未実装。

---

# v0.9.0.05 — Dow Trend Evaluator (2026-07-11)

- Shared Swing Point Detectorの確定点を時系列で再生し、WEEK / DAY / H4 / H1 / M5へ同じDow Trend Evaluatorを適用。時間足別Evaluatorクラスは作らない。
- 構造上の直近2高値・直近2安値を比較し、`UP / DOWN / REVERSAL_WATCH / NO_TREND / UNDETERMINED` を算出。
- `UP = Higher High + Higher Low`、`DOWN = Lower High + Lower Low`。比較ペア不足はUNDETERMINED、同値はNO_TREND、方向不一致は過去方向があればREVERSAL_WATCH、なければNO_TRENDとする。
- 未確定CandidateはDow判定に使用しない。同種Swingが連続した場合は、より極端な確定点だけで構造を置換し、弱い同種点は無視する。
- TrendStateとEntry Permissionを分離。Dow Evaluatorは状態だけを返し、H4 Dow確定を発射ボタンにしない。
- TrendStateが変化した時だけ`trend_changed` Eventを生成し、使用したSwing Point ID / Swing Confirm Event / reason_codes / before-afterへ逆追跡可能にした。
- Run設定画面へ時間足別Dow表を追加し、現在State、前回State、高値/安値比較、使用Swing数、State Change数を確認可能にした。
- Run Snapshot schemaをv0.4へ更新し、`dow_trend_evaluation`を保存。チャートには各時間足の最新TrendState変更だけをSimulation Traceとして投影。
- 先生ガード: 今回はDow TrendStateの観測まで。Cycle / HSI Anchor / Entry Permission / Hold / Close / M5売買は未実装。

---

# v0.9.0.04 — Shared Swing Point Detector (2026-07-11)

- WEEK / DAY / H4 / H1 / M5へ、時間足別クラスを作らず同一のShared Swing Point Detector Coreを適用。
- Confirm barsはRun Profileの各時間足独立値を直接使用し、他時間足からの計算・継承・暗黙Fallbackは行わない。
- 確定足同期済みデータだけを入力し、中心窓の一意High/LowからSwing Pointを算出。確認窓未完成の点はCandidateとして保持し、後続根拠には使わない。
- Lifecycleを `Candidate → Confirmed → Retired` として記録。ConfirmedかつActive Basisの点だけを将来のDow/HSI起点候補にできる契約を追加。
- Point ID / Event IDを時刻・時間足・High/Low・Confirm barsから安定生成し、Candidate / Confirmed / Retired Eventを `cause_event_ids` で逆追跡可能にした。
- Run設定画面へSwing Point表を追加し、時間足別のInput bars / Pending / Confirmed / Active / Retired / 最新確定時刻 / Statusを確認可能にした。
- Run Snapshot schemaをv0.3へ更新し、`swing_point_detection.timeframes` と全 `observation_events` を保存。Previewでは大量配列を件数表示へ圧縮。
- チャート上には全Eventを出さず、各時間足の最新Active high/lowだけをSimulation Traceコメントへ投影。実データ保存後は説明用Fixture Markerを非表示化。
- 先生ガード: 今回は赤丸・緑丸材料点の観測まで。Dow / Cycle / HSI Anchor / Entry / Close / M5売買エンジンは未実装。

---

# v0.9.0.03 — Multi-Timeframe Candle Synchronizer (2026-07-11)

- M5の確定Close時刻を基準に、WEEK / DAY / H4 / H1 / M5 の `latest confirmed candle` を同期する基盤を追加。
- H1/H4はPrimary M5から集約、DAYは外部UpperMap D1、WEEKはDAYから集約するSource MappingをRun Profileどおりに使用。
- 判定条件を `bar_end_ms <= reference_close_ms` に固定し、未確定上位足・未来足は同期結果から除外。Lookaheadが見つかった場合はRun Snapshot作成を拒否する。
- `Run設定` 画面にConfirmed Candle Synchronizer表を追加し、各時間足の最新確定足、現在未確定足、除外件数、同期状態を確認可能にした。
- 参照M5は、チャート同期位置があればそのM5、なければ現在表示窓の最終M5を使用。Runtime timezone / UTC offsetと、Data timezone未宣言状態もSnapshotへ記録する。
- Run Snapshot schemaをv0.2へ更新し、`time_sync_policy` と `candle_sync` を保存。
- Run設定ダイアログの表・入力欄を黒背景 + 白系文字へ統一し、ブラウザ/共通CSS由来の白い縞表示を上書き。
- 先生ガード: 今回は確定足同期とLookahead防止のみ。Dow / Cycle / HSI Anchor / Entry / Close / M5売買エンジンは未実装。

---

# v0.9.0.02 — Simulation Run / Timeframe Profile (2026-07-10)

- `Run設定` ダイアログを追加し、WEEK / DAY / H4 / H1 / M5 のConfirm barsを独立した必須値として表示・編集可能にした。
- Confirm barsは他時間足から計算・継承せず、未設定・範囲外・重複がある場合はRun Snapshot作成を拒否する。暗黙default / fallbackも禁止。
- `simulation/fx_simulation_run_profile_v0_1.json` を追加し、Primary / UpperMap DataSource、SHA-256、Rule Version、時間足ごとのSource Mapping / Warmupを明示。
- 現在のM5表示窓をRun Periodとして取り込み、Validation通過時のみ `*.simulation_trace.json` の `run_snapshot` へ再現条件を保存できるようにした。
- Run Snapshotには profile_id / rule_version / dataset hash / period / 全時間足Confirm bars / chart_state を保存する。
- 先生ガード: 今回はRun条件の検証・Snapshot保存のみ。Dow / Cycle / HSI Anchor / Entry / Close / M5売買エンジンは未実装。

---

# v0.9.0.01 — Simulation Trace Annotation UI Foundation (2026-07-10)

- UserコメントとSimulationコメントを、独立した表示レイヤーとしてON/OFFできるUIを追加。
- Human Commentは既存 `*.chart_comments.json`、Simulation Traceは新規 `*.simulation_trace.json` を正本とし、保存ファイルを分離。
- Simulation Traceはチャート上でシアンの菱形 `S` バッジとして表示し、Human Commentの吹き出しアイコンと視覚的に区別。
- Traceクリック時に、summary / reason_codes / rule_ids / cause_event_ids / upper_state_summary / state_before / state_after を読み取り専用Popoverで表示。
- 実シミュレーター実装前にUI契約を確認するため、5件のFixture Traceを追加。Fixtureは説明用であり、売買判定・実行ロジックは未実装。
- `User全表示` / `Simulation全表示` / `注釈全閉じ` を追加し、画面だけで状態概要を確認できる基盤を整備。

---

# v0.8.3.32 — Expansion Review WEEK context / JSON confirmBars

- Expansion検討モードの右下窓を H1 から WEEK へ変更。
- WEEK足は外部DAY UpperMap DataSourceから週足へ集約。週の開始は月曜日。
- `plugins/fx_chart_viewer/plugin.json` の `display_policy.week_context_settings.confirm_bars_default` を追加。
- WEEK材料点はActive basis high/lowのみ表示し、値はJSONを手動変更して調整可能。

---

# gpt_fx_lab CHANGELOG

## v0.8.3.31 - 2026-07-09

- DAY UpperMapにDAY Confirm bars単位の縦点線を表示。
  - DAY Confirm=45 のような日足大局確認幅を、画面上でも縦点線として読めるようにした。
  - これは保存サイクル縦線や通常保存縦線ではなく、DAY Confirm barsに基づく表示補助線。
  - DAY UpperMapでは引き続き通常保存縦線・サイクル縦線・H/Lレンジ縦線は非表示。
- DAY UpperMap設定を追記。
  - `display_policy.day_upper_map_settings.show_confirm_stride_lines = true` を追加。
  - `confirm_bars_presets` を `[7, 20, 30, 45, 60, 90]` に整理。
- 先生ガード:
  - 今回はDAY UpperMapの視認性改善のみ。
  - Dow trend / Entry / Simulation の自動判定はまだ行わない。

## v0.8.3.30 - 2026-07-09

- D1 UpperMap用データを最新CSVで更新。
  - `USDJPY1440.csv` 最新版を取り込み、`fx_usdjpy_d1_t3_data_v0_1.json` を再生成。
  - 既存D1 JSONの2017-11-21〜2018-08-24は保持し、2018-08-27以降の重複期間は最新CSVで置換。
  - 最新日付は 2026-07-09 00:00 まで拡張。
  - MA5 / MA20 / T3(20,0.2) / T3 cross / display_sets を再計算。
- 先生ガード:
  - 今回はD1相場データ更新のみ。
  - DAY Confirm bars / marker policy は引き続き `plugin.json display_policy.day_upper_map_settings` が正本。
  - Dow trend / Entry / Simulation の自動判定はまだ行わない。

## v0.8.3.29 - 2026-07-09

- DAY UpperMap設定のゴミ掃除。
  - DAY Confirm bars / marker mode / default D1 data path の正本を `plugin.json display_policy.day_upper_map_settings` に一本化。
  - `chart_layout.layouts.EXPANSION_REVIEW` から重複していた `day_confirm_bars_default` / `day_point_marker_mode` / `upper_map_data_source` を削除。
  - `signal_policy` から設定値扱いになっていたDAY Confirm bars / point marker / data source defaultを削除し、機能宣言だけに戻した。
  - `plugin.js` はDAY設定値を `display_policy.day_upper_map_settings` から読む。`chart_layout` / `signal_policy` は設定正本として読まない。
- DAY UpperMapの責務を再整理。
  - `chart_layout` = どこに何を置くか。
  - `day_upper_map_settings` = DAY地図の動作設定。
  - `url_chart_state_policy` = URLとsidecarの責務説明。
  - D1 Data JSON = 差し替え可能な相場データ。
- 先生ガード:
  - 今回は設定正本の整理のみ。
  - Dow trend / Entry / Simulation の自動判定はまだ行わない。

## v0.8.3.28 - 2026-07-09

- DAY UpperMapのConfirm bars / marker設定の所有者を修正。
  - 誤って `fx_usdjpy_d1_t3_data_v0_1.json` 側へ持たせていたDAY用Confirm bars設定を、`plugin.json` 側へ移動。
  - D1 JSONはぽこぽこ差し替える相場データであり、UI改善の資産設定は持たせない方針に戻した。
  - `plugin.json display_policy.day_upper_map_settings` をDAY UpperMap設定の正本とする。※v0.8.3.29でsignal_policy側の重複設定は削除。
  - URLパラメータ `dayConfirmBars` による一時上書きは継続。
- D1 JSONから `chart_viewer_settings` / `dow_basis_point_settings` を削除。
  - データJSONはデータ、Plugin JSONは観測UIポリシーという責務分離を明確化。
- 先生ガード:
  - 今回は設定所有者の修正のみ。
  - Dow trend / Entry / Simulation の自動判定はまだ行わない。

## v0.8.3.27 - 2026-07-09

- DAY UpperMapに日足スケールのDow材料点を復活。
  - DAYは広域地図として扱う方針は維持しつつ、Expansion格付けに必要なActive basis high/lowだけを赤丸・緑丸で表示する。
  - Candidate / Retired 点はDAYでは表示しない。
  - 通常保存縦線、Confirm stride縦線、H/Lレンジ縦線、サイクル縦線は引き続きDAYでは非表示。
- DAY専用Confirm barsをJSON設定化。
  - 当初は `fx_usdjpy_d1_t3_data_v0_1.json` 側に設定を置いたが、v0.8.3.28以降はplugin.json側へ移動。
  - URLパラメータ `dayConfirmBars` でも一時上書き可能。
  - 既定値は 7。
- 先生ガード:
  - 今回はDAY UpperMapの観測補助表示のみ。
  - Dow trend / Entry / Simulation の自動判定はまだ行わない。

## v0.8.3.26 - 2026-07-09

- DAY UpperMapの広域地図方針に合わせて表示をさらに整理。
  - DAYパネルでは保存サイクル縦線も描画しないようにした。
  - DAYは全体の大きな流れを見る地図として扱い、サイクル縦線はH4/H1/M5側の観測レイヤーに寄せる。
- 既存方針は維持。
  - DAYではDow材料点、通常保存縦線、Confirm stride縦線、H/Lレンジ縦線を描画しない。
  - H4/H1/M5側のサイクル縦線表示は維持。
- 先生ガード:
  - 今回はDAY UpperMapの表示整理のみ。
  - Dow trend / Entry / Simulation の自動判定はまだ行わない。

## v0.8.3.25 - 2026-07-09

- DAY UpperMapの表示整理。
  - 外部D1データ側のDow Candidate / Active Basis / Retired Basis 点をDAYでは描画しないようにした。
  - DAYは「上位地図」として、価格・MA/T3/BB・サイクル縦線・同期位置を中心に見る方針へ寄せた。
- H1/H4/M5ダブルクリック同期のDAY側表示を改善。
  - Primary(M5)側に該当時刻がある場合は従来どおりM5窓を同期。
  - M5側に該当時刻がない場合でも `syncCenterTimeMs` を保持し、DAY側に同期位置を表示できるようにした。
  - DAYパネルでは同期位置を `SYNC` ラベル付きの強調縦線で描画する。
- 先生ガード:
  - 今回はDAY UpperMapの表示整理と同期表示改善のみ。
  - Dow trend / Entry / Simulation の自動判定はまだ行わない。

## v0.8.3.24 - 2026-07-09

- Expansion検討レイアウトのDAYパネルを、M5内部生成ではなく外部D1 DataSourceで表示できるようにした。
  - 既定: `overlay/gpt_fx_lab/data/fx_usdjpy_d1_t3_data_v0_1.json`。
  - URLパラメータ `dayData` / `upperMapData` で差し替え可能。
  - H4/H1/M5は既存どおりPrimary(M5)から生成し、DAYだけUpperMap DataSourceとして扱う。
- DAYパネルの表示範囲を広域化。
  - 通常時はM5表示窓の中央時刻、ダブルクリック同期時は同期時刻を中心にD1データを表示する。
  - これにより、Expansion検討時に日足の大きな流れを見やすくする。
- DAYパネルの細かい縦線を抑制。
  - 通常保存縦線、Confirm stride縦線、H/Lレンジ縦線はDAYでは描画しない。
  - サイクル縦線は要望どおりDAYにも残す。
- URLコピーの整理。
  - `hsi` / `hsiScale` / `hsiDir` / `hsiAnchor...` はURLコピーに出力しない。
  - 保存済みHSI・コメント・サイクル縦線は `chart_comments.json` を正本とする。
  - 旧URL互換として、URL読込側のHSIパラメータ解釈は残す。
- 先生ガード:
  - 今回はDataSource参照・表示範囲・URL整理のみ。
  - Dow trend / Entry / Simulation の自動判定はまだ行わない。

## v0.8.3.7 - 2026-07-06

- コメントエディターの上部かぶりを改善。
  - コメント点が画面上部メニュー/メタ領域に近い場合、エディターを点の下側へ自動配置する。
  - 上部にかぶって本文入力欄が押せないケースを避ける。
- 先生ガード:
  - 今回はUI操作性改善のみ。
  - Dow trend / Entry / Simulation の自動判定はまだ行わない。

## v0.8.3.6 - 2026-07-06

- 右クリックメニューの操作性を改善。
  - `HSI起点を追加` をクリックした時点でメニューを自動クローズする。
  - `コメントを追加` をクリックした時点でメニューを自動クローズする。
  - 併せて `保存HSI削除` / `このHSI仮説を保存` も同じ即時クローズ動作に統一。
- 先生ガード:
  - 今回はUI操作性改善のみ。
  - Dow trend / Entry / Simulation の自動判定はまだ行わない。

## v0.8.3.5 - 2026-07-06

- HSI R23_M単一点観測ラインを追加。
  - R2=89 と R3=144 の中間観測点として `R23_M = 117` を描画する。
  - 既存のHSI線より細く、白寄せの補助線として表示する。
  - 現在の手動HSI起点と、保存済みHSIの両方に表示する。
- 先生ガード:
  - 今回は観測補助線の追加のみ。
  - Dow trend / Entry / Simulation の自動判定はまだ行わない。

## v0.8.3 - 2026-07-05

- Upper Context Warmup Bars / 上位足文脈バー追加に対応。
  - `upperWarmupBars` を追加。
  - H1/H4などの上位足パネルだけ、M5表示開始時刻より過去側へ余白バーを追加表示できる。
  - M5表示窓の `windowStart` / `windowSize` は変更しない。
- UIを追加。
  - `上位余白` 入力欄。
  - `余白0` / `余白30` / `余白60` / `余白100` プリセット。
- URL再現に対応。
  - `upperWarmupBars` をURLコピーへ含める。
  - URL起動時に `upperWarmupBars` を復元する。
- 同期縦線の方針を維持。
  - x座標同期ではなく時刻同期。
  - 対象時刻がパネル表示範囲外の場合は、描画せずエラーにしない。
- 先生ガード:
  - 今回は上位足文脈表示のウォームアップのみ。
  - Dow trend / Entry / Simulation の自動判定はまだ行わない。
  - 未来側には拡張しない。

## v0.8.2 - 2026-07-05

- Saved HSI Annotation Sidecar / HSI仮説線保存を追加。
  - 未保存の現在HSI起点を右クリックすると、現在のHSI仮説をSidecar JSONへ保存できる。
  - 保存済みHSI起点を右クリックすると、保存HSIを削除できる。
  - `保存HSI表示ON/OFF` ボタンを追加。
- 保存先は既存のコメントSidecar JSON内の `hsi_annotations[]`。
  - 初期段階では `fx_usdjpy_m5_t3_data_v0_1.chart_comments.json` にコメントと言葉の仮説、保存HSIという図形の仮説を同居させる。
  - 将来は `chart_annotations.json` へ整理可能な構造に寄せる。
- 一時HSIと保存HSIの見た目を分離。
  - 一時HSI: 従来どおり強めの赤ライン。
  - 保存HSI: 薄めの黄色点線 + ◆/S マーカー。
- 先生ガード:
  - 保存HSIは人間が残した図形の仮説。
  - Dow trend / Entry / Simulation の自動判定はまだ行わない。

## v0.8.0.1 - 2026-07-05

- コメントSidecar JSONの実ファイル保存API連携を修正。
  - `POST /api/overlays/{overlayId}/sidecars/{file}` で `studio_overlays/gpt_fx_lab/sidecars/*.chart_comments.json` へ保存する前提にした。
  - `/api/data` へOverlay Sidecarを混ぜない。
  - 保存成功時はlocalStorage fallbackを削除し、次回以降は実ファイル側を正として読みやすくする。
- コメント作成時刻の `NaN-NaN-NaN NaN:NaN` 表示を修正。
  - `formatRowDateTime(row)` ではなく `formatRowDateTime(rowTimeMs(row))` を使う。
  - `formatRowDateTime` は無効値なら空文字を返す。
- 先生ガード:
  - 今回はコメント保存と表示の修正のみ。
  - Dow trend / Entry / Simulation の自動判定はまだ行わない。

## v0.8.0 - 2026-07-05

- Chart Comment Sidecar / 観測メモMVPを追加。
  - `コメント追加ON/OFF` を追加。
    - OFF時: 通常クリックは従来どおりHSI起点。
    - ON時: チャートクリックで人間コメントを追加。
  - `コメント表示ON/OFF` を追加。
  - `コメント全表示` / `コメント全閉じ` を追加。
  - `コメント保存` を追加。
- チャート上に小さい人間コメントアイコンを表示。
  - アイコンをクリックすると、Tooltip/Popover型でコメントを表示。
  - Popover内でコメント種別・タイトル・本文・タグを編集可能。
- コメントはデータJSON本体へ混ぜず、Sidecar JSONへ保存する方針にした。
  - 初期Sidecar: `studio_overlays/gpt_fx_lab/sidecars/fx_usdjpy_m5_t3_data_v0_1.chart_comments.json`
  - ブラウザ側はOverlay/API保存を試み、保存APIが使えない場合はlocalStorageへ一時保存する。
- コメントには、time / price / panel / x_index_hint / chart_state を保存する。
  - `x_index_hint` は表示補助であり、将来のデータ差し替えを考慮して time / price を主な文脈として残す。
- 先生ガード:
  - 今回は観測メモ・判断ログの保存UIのみ。
  - Dow trend / Entry / Simulation の自動判定はまだ行わない。

## v0.7.18 - 2026-07-05

- HSI起点ラベルの表示位置をライン方向に応じて調整。
  - 上向きラインの場合:
    - `HSI起点 / 倍率:X` をクリック起点の下側へ表示。
  - 下向きラインの場合:
    - `HSI起点 / 倍率:X` をクリック起点の上側へ表示。
- 目的:
  - ラベルがHSIラインや評価したい未来方向の値動きを隠さないようにする。
  - `倍率` 表示は維持しつつ、スクショ時の邪魔さを減らす。
- 先生ガード:
  - 今回はラベル位置のUI調整のみ。
  - Dow trend / Entry / Simulation の自動判定はまだ行わない。

## v0.7.17 - 2026-07-05

- HSI起点ラベルに倍率表示を追加。
  - 表示例:
    - `HSI起点`
    - `倍率: 6`
- 目的:
  - HSI定数だけでなく、何倍の倍率でHSIラインを引いて評価したかをスクショ上にも残す。
  - `HSI値 = 定数 / 倍率 = 観測スケール / 起点 = 人間の仮説` という整理を、画面上でも失わないようにする。
- 先生ガード:
  - 今回はラベル表示のみ。
  - Dow trend / Entry / Simulation の自動判定はまだ行わない。

## v0.7.16 - 2026-07-05

- URLコピーしたリンクから画面遷移できない問題を修正。
  - 原因1: コピーURLに `data` / `view` が含まれておらず、リロード後に対象JSONとViewDefを再ロードできなかった。
  - 原因2: Studio Core側は現時点で `action` クエリを自動実行しないため、`action=fx_chart` を付けてもチャートActionが起動しなかった。
- URLコピー時に以下を明示するように変更。
  - `data=overlay/gpt_fx_lab/data/fx_usdjpy_m5_t3_data_v0_1.json`
  - `view=overlay/gpt_fx_lab/view_defs/fx_usdjpy_t3_view_def_v0_1.json`
  - `action=fx_chart`
- Plugin側でURL起動を補完。
  - `action=fx_chart`
  - `action=OpenFxT3Chart`
  - `action=OpenFxChartViewer`
  - `action=FxT3Chart`
  - `action=gpt_fx_lab.fx_chart`
- 旧URLのように `data/view` が無い場合でも、FX Lab既定データを保険ロードしてチャートを開く。
- 先生ガード:
  - 今回はURL再現性の修正のみ。
  - Dow trend / Entry / Simulation の自動判定はまだ行わない。

## v0.7.15 - 2026-07-05

- 最大化時に右側の上位足パネルが見えなくなる問題を修正。
  - v0.7.14で2ペイン化した後も、旧来の `widthMultiplier` により canvas 幅が `可視幅 × 2.6` になっていた。
  - その結果、右側H1/H4パネルが横スクロール領域の奥へ押し出され、最大化時に消えたように見える場合があった。
- 2ペイン描画では、canvas幅を現在の可視幅に合わせるように変更。
  - 左M5と右H1/H4は「同時に見える」ことが価値なので、横方向の仮想拡大を使わない。
  - モーダル最大化状態は保持するが、2ペインの描画幅には `widthMultiplier` を掛けない。
- redraw後の横スクロール位置を `0` に戻すように変更。
- 先生ガード:
  - 今回はレイアウト修正のみ。
  - Dow trend / Entry / Simulation の自動判定はまだ行わない。

## v0.7.14 - 2026-07-05

- 右側に上位時間軸パネルを追加。
  - 左: M5 lower / entry observation
  - 右: H1/H4 upper / context observation
- M5データからH1/H4 OHLCを内部生成。
  - H1 = M5 12本相当
  - H4 = M5 48本相当
  - open/high/low/close/volume を集約し、上位足の MA20 / T3 / BB は上位足側で再計算する。
- 上位足にも材料点を表示。
  - Candidate
  - Active Basis
  - Retired Basis
  - M5の点をコピーせず、上位足OHLCに対して再抽出する。
- 左右パネルに共有縦線を追加。
  - x座標共有ではなく、時刻共有。
  - M5上の時刻が、右H1/H4では該当する上位足に対応する。
- 上位足切替を追加。
  - `H1`
  - `H4`
  - URLパラメータ: `upperTf`
- 上位足用Confirm barsを追加。
  - URLパラメータ: `upperConfirmBars`
  - 既定値: `7`
- 先生ガード:
  - 今回は上位文脈の観測パネル追加のみ。
  - Dow trend / Entry / Simulation の自動判定はまだ行わない。

## v0.7.13 - 2026-07-05

- 表示窓の移動に対応。
  - `窓` 入力で表示件数を指定できる。既定は `1000`。
  - `古い窓` / `新しい窓` で、表示範囲を前後へ移動できる。
  - `ランダム窓` で、全データ内のランダムな表示範囲を開ける。
  - `最新窓` で、最新側の表示範囲へ戻れる。
- URLコピーに表示窓状態を含める。
  - `windowStart`
  - `windowSize`
- 表示窓を変更した場合、HSI起点はクリアする。
  - 起点は表示窓内の仮説なので、窓が変わると別文脈になるため。
- 目的:
  - 最新1000件だけを見て「脳内シミュレーションが全部OK」に見える状態を避ける。
  - 見たい相場だけではなく、見えていない過去データを観測する。
  - HSIの当たりだけでなく、外れパターンも拾える研究装置へ進める。
- 先生ガード:
  - 今回も Dow trend / Entry / Simulation には進まない。
  - あくまで観測範囲の再現性・ランダム性を強化する。

## v0.7.11 - 2026-07-05

- HSI倍率欄の操作性を改善。
  - ブラウザ標準の number スピナーが押しづらいため、専用の `▲` / `▼` ボタンを追加。
  - `▲` は `scale_step` 分だけ倍率を増やす。
  - `▼` は `scale_step` 分だけ倍率を減らす。0未満にはしない。
  - 倍率入力欄は `type="text"` + `inputmode="decimal"` に変更し、手入力も継続可能。
- 先生ガード:
  - 今回はHSI倍率操作の人間フレンドリー化のみ。Dow trend / Entry / Simulation には進まない。

## v0.7.10 - 2026-07-05

- `confirmBars` URLパラメータ未指定時に、初期値が `3` になってしまう問題を修正。
  - 原因: URLパラメータが無い場合でも `Math.max(3, 0)` により `3` が採用されていた。
  - 修正後: `confirmBars` がURLに明示されている場合だけURL値を採用する。
  - URLに `confirmBars` が無い場合は、JSON設定の `confirm_bars_default` を使用する。
- HSI倍率入力欄を操作しやすいように調整。
  - `width: 86px`
  - `min-height: 26px`
  - number/text入力全体にも `min-height` と `box-sizing` を追加。
- 先生ガード:
  - 今回は初期値・操作性修正のみ。Dow trend / Entry / Simulation には進まない。

## v0.7.9 - 2026-07-05

- HSI初期値をJSONから設定できるようにした。
  - 既定値: `55,89,144,188`
  - `plugin.json display_policy.manual_hsi_lines.default_values`
  - Data JSON側では `hsi_settings` / `hsi_settings.manual_lines` / `strategy_settings.hsi` で上書き可能。
- HSI倍率の初期値とstepをJSONから設定できるようにした。
  - 既定値: `default_scale=1`
  - 既定step: `scale_step=1`
- HSI倍率欄の横幅を少し広げた。
- Confirm bars 初期値をJSONから設定できるようにした。
  - 既定値: `20`
  - `plugin.json signal_policy.confirm_bars_default`
  - Data JSON側では `dow_basis_point_settings.confirm_bars_default` / `chart_viewer_settings.confirm_bars_default` で上書き可能。
- URLパラメータ未指定時に `hsiAnchorPrice` が `0` と解釈され、初期表示が壊れる問題を修正。
  - `numberOrNull(null)` / `numberOrNull('')` は `null` を返すように変更。
- 先生ガード:
  - HSIラインは引き続き人間の仮説可視化であり、Dow材料点抽出・Trend判定・Entry判定には使わない。

## v0.7.8 - 2026-07-05

- 手動起点HSIラインを追加。
  - `HSI` 入力欄にカンマ区切りで値を指定する。初期値は `55,89,144`。
  - `倍率` 入力欄で `1 / 0.1 / 0.01` などを指定できる。初期値は `0.1`。
  - `HSI上` / `HSI下` で、起点から上へ引くか下へ引くかを切り替える。
  - チャートのプロット領域をクリックすると、その価格を手動起点として記録する。
  - 起点から `HSI値 × 倍率 × point_size` 分だけ離れた位置に、短い赤い横線を表示する。
  - `HSIクリア` で起点を解除する。
- URLコピーに HSI 状態を含める。
  - `hsi`, `hsiScale`, `hsiDir`, `hsiAnchorPrice`, `hsiAnchorIndex`。
- 先生ガード:
  - HSIラインは人間の仮説可視化であり、Dow材料点抽出・Trend判定・Entry判定には使わない。

## v0.7.7 - 2026-07-05

- `横幅拡大` ボタンを、右上固定の `□` ボタンへ変更。
  - 実質的に画面最大化操作になってきたため、ウィンドウ操作として認識しやすい位置へ移動。
  - ON時はボタンをアクティブ表示し、`▢` 表示へ切り替える。
- 既存の `wide=1/0` URLパラメータはそのまま継続。
- 先生ガード: 今回も Dow trend / Entry / Simulation へ進まない。観測UIの操作性改善のみ。

## v0.7.6 - 2026-07-05

- チャート右上に `URLコピー` ボタンを追加。
  - 現在の観測状態をURLとしてコピーできる。
  - 対象パラメータ: `action=fx_chart`, `confirmBars`, `viewMode`, `hlRange`, `bb`, `wide`。
  - コピー後は一時的に `URLコピー済` と表示する。
- 目的は、観測条件をブックマーク・共有しやすくすること。
- 先生ガード: 今回も Dow trend / Entry / Simulation へ進まない。観測状態の再現性を高めるだけ。

## v0.7.5 - 2026-07-05

- Bollinger Bands 表示ON/OFFを追加。
  - 設定は MT4の標準的な `Bands Period=20 / Shift=0 / Deviations=2.0` に合わせる。
  - sourceは `close`。
  - BB upper/lowerを点線、バンド内を薄い塗りで表示する。
  - BBは観測補助表示であり、Dow材料点抽出・Trend判定・Entry判定には使わない。
- チャート状態のURL起動に対応。
  - `action=fx_chart` でURL起動後にチャートを自動表示できる。
  - `confirmBars`, `viewMode`, `hlRange`, `bb`, `wide` をURLで指定できる。
- H/Lレンジ線について、ユーザー手調整後の見え方を維持。
  - `rgba(248,250,252,0.82)` / `lineDash [1.5, 2.0]` / `lineWidth 1.35`。
- 先生ガード: 今回も Dow trend / Entry / Simulation へ進まない。BBも材料点抽出には使わない。

## v0.7.4 - 2026-07-05

- High/Low レンジ線を白寄せ・細点線化。
  - 旧表示ではClose線の裏でほぼ見えなかったため、観測補助UIとして視認性を上げる。
  - `rgba(248,250,252,0.58)` / `lineDash [1, 2.4]` / `lineWidth 1.15`。
  - 判定ロジック、Candidate/Basis/Retired抽出ルールには触れない。
- URL起動は既存仕様で対応済みであることを確認。
  - `data=overlay/gpt_fx_lab/data/fx_usdjpy_m5_t3_data_v0_1.json`
  - 必要に応じて `view=overlay/gpt_fx_lab/view_defs/fx_usdjpy_t3_view_def_v0_1.json`
- 先生ガード: 今回も Dow trend / Entry / Simulation へ進まない。材料点の根拠を見やすくするだけ。

## v0.7.3 - 2026-07-05

- FX chart viewer に High/Low レンジ表示を追加。
  - Close線だけでは、High/Low判定点の根拠が直感的に見えにくかったため。
  - 各足の high-low 範囲を薄い縦線で表示する。
  - チャート密度が高い場合は間引き表示し、画面を潰しすぎないようにする。
- `H/LレンジON/OFF` ボタンを追加。
  - 初期値は ON。
  - 判定ロジックには影響しない観測補助UI。
- tooltip に `High` / `Low` を追加。
  - `Close`線と `high`/`low` 判定点の違いを確認しやすくする。
- メタ表示に `H/L range=on/off` を追加。
- 先生ガード: 今回は Dow trend / Entry / Simulation へ進まない。材料点の根拠を見やすくするだけ。

## 2026-07-10 v0.8.3.33 — WEEK文脈見直し
- Expansion検討モードの右下WEEK窓を、DAYに近すぎる窓切り出しから見直し、週足の広域履歴を優先表示するよう調整。
- WEEK窓では保存縦線・サイクル縦線を非表示化。DAY/H4/M5側の既存観測導線は維持。
- WEEK Confirm bars は引き続き plugin.json `display_policy.week_context_settings.confirm_bars_default` を正本として手動調整可能。
