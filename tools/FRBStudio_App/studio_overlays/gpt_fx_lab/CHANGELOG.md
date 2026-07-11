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
