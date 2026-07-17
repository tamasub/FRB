// gpt_fx_lab.fx_chart_viewer v0.9.1.13-normal-entry-gate-failure-log
// Coreを変更せず、Overlay Plugin ActionとしてUSDJPY M5 + T3 + Dow candidate/basis/history静的チャートを表示する。
// 上位足Decisionを入力にM5確定足で仮想Entry/保有/決済を実行し、1 Entry / 1 Position / 1 Stop / 1 TargetのLifecycleを原因Traceへ接続する。
// Confirm bars を変えながら、Candidate / Active Basis / Retired Basis の違いを見える化する。
// v0.7.3: high/lowレンジ表示を追加。判定ロジックには触れず、点の根拠を見やすくする。
// v0.7.4: high/lowレンジ線を白寄せ・細点線化。URL起動は既存の data/view パラメータで確認。
// v0.7.5: Bollinger Bands表示ON/OFFとチャート状態URL起動パラメータに対応。判定ロジックには触れない。
// v0.7.6: 現在のチャート状態をURLとしてコピーするボタンを追加。
// v0.7.7: 横幅拡大を右上固定の□ボタンへ変更。
// v0.7.8: 手動起点HSIラインを追加。クリック起点から任意HSI値×倍率の短い横線を表示する。
// v0.7.9: HSI/Confirm初期値をJSON設定化し、URLパラメータ未指定時の0誤解釈を修正。
// v0.7.10: confirmBars URL未指定時に3扱いになる問題を修正し、HSI倍率入力の高さを調整。
// v0.7.11: HSI倍率の操作性改善として、専用の▲/▼ボタンを追加。
// v0.7.13: 表示窓の移動・ランダム窓・最新窓に対応。見たい相場だけを見る錯覚を避ける。
// v0.7.14: M5からH1/H4上位足を内部生成し、右側パネルに材料点と時刻同期縦線を表示。
// v0.7.15: 最大化時に横スクロール幅へ右側上位足パネルが押し出される問題を修正。
// v0.7.16: URLコピーにdata/viewを含め、action=fx_chart/OpenFxT3ChartからのURL起動をPlugin側で補完。
// v0.7.17: HSI起点ラベルに倍率を表示し、スクショ上にも観測スケール条件を残す。
// v0.7.18: HSI起点ラベルを、上向きライン時は起点下、下向きライン時は起点上へ表示する。
// v0.8.0: チャート上コメントをSidecar JSONへ保存する観測メモMVPを追加。
// v0.8.0.1: コメントSidecarの実ファイル保存API連携と、コメント時刻NaN表示を修正。
// v0.8.2: HSI仮説線を右クリックでSidecar保存し、保存済みHSIを削除・再表示できるようにする。
// v0.8.3: 上位足パネルに過去文脈用upperWarmupBarsを追加し、M5前半の上位文脈不足を減らす。
// v0.8.3.1: FXコメント削除確認をブラウザ標準confirmから画面内カスタムダイアログへ置換。
// v0.8.3.2: 上位足パネルでも手動HSI起点・保存HSIの保存/削除を利用可能にする。
// v0.8.3.3: 右クリック起点メニューでHSI/コメント追加を選べるようにし、注釈アイコンの視認性を改善。
// v0.8.3.4: HSI/コメント追加を右クリックメニューへ統一し、通常左クリックで注釈追加・HSI起点変更しないように修正。
// v0.8.3.11: 右クリックメニューでHSI上下を選択して即保存し、コメントクリックは閲覧画面を挟まず直接編集する。
// v0.8.3.12: HSI上下の追加操作を右クリックメニューへ集約し、上部のHSI上下ボタンを廃止する。
// v0.8.3.13: 右クリックHSI追加後に一時HSI仮説を残さず、保存HSI削除時は画面から即時消えるようにする。
// v0.8.3.14: コメントラベルから種類名フォールバックを外し、コメント編集ボタン順を「削除・閉じる・保存」に整理。
// v0.8.3.5: HSIのR2-R3中間観測点としてR23_M=117を細い白寄せラインで追加。
// v0.8.3.6: HSI/コメント追加などの右クリックメニュー操作後に、メニューを即時自動クローズする。
// v0.8.3.7: 現在の同期縦線を保存し、左右パネルに番号付き保存縦線として表示・削除できるようにする。
// v0.8.3.8: サイクル確認用の別系統縦線を追加。通常保存縦線とは独立番号・黄色太線・一段下ラベルで表示する。
// v0.8.3.9: 通常保存縦線を白系・少し細めへ変更し、サイクル縦線との視覚差を明確化する。
// v0.8.3.10: カレント同期縦線を黄色から白系の細線へ変更し、サイクル縦線との差を明確化する。
// v0.8.3.18: M5+H1+H4の3ペイン同時表示と、上位足HSIの下位足継承表示に対応。
// v0.8.3.16: HSIラインラベルをRange表記へ統一し、pt数値とSaved接頭辞を非表示化。中間観測点はR2.5/R3.5/R4.5表記に変更。
// v0.8.3.18: 右クリックメニューにExpansionラベル追加ボタンが表示されない問題を修正。
// v0.8.3.23: Expansion検討レイアウトを追加。H4メイン + DAY/H1サブ表示と、既存M5実行レイアウト切替に対応。
// v0.8.3.24: Expansion検討レイアウトのDAYパネルを外部D1 DataSource対応へ拡張。URLコピーのHSI一時パラメータ出力を停止し、Sidecar正本方針へ寄せる。
// v0.9.0.01: Simulation Trace Annotation UI基盤を追加。UserコメントとSimulationコメントを別Sidecar・別ON/OFFで表示する。
// v0.9.0.02: Simulation Run / Timeframe Profileを追加。WEEK/DAY/H4/H1/M5のConfirm barsを独立必須値として検証し、Run SnapshotをTrace Sidecarへ保存する。
// v0.9.0.03: Multi-Timeframe Candle Synchronizerを追加。M5 Closeを基準に、確定済みWEEK/DAY/H4/H1/M5だけを同期し、Lookaheadを検出する。
// v0.9.0.04: Shared Swing Point Detectorを追加。全時間足へ同じ中心窓・一意高安ロジックを適用し、Candidate / Confirmed / RetiredとObservation EventをRun Snapshotへ保存する。
// v0.9.0.05: Dow Trend Evaluatorを追加。確定Swing構造からUP / DOWN / REVERSAL_WATCH / NO_TREND / UNDETERMINEDを共通評価し、TrendState変更だけをTraceへ保存する。
// v0.9.0.06: Cycle Position Evaluatorを追加。最新の利用可能Swingを起点に、明示閾値からEARLY / MIDDLE / LATEを共通評価し、起点変更とPhase変更をTraceへ保存する。
// v0.9.0.07: HSI Anchor Registry / Resolverを追加。時間足内の複数起点をLifecycle・Role・Purpose別に管理し、Human Saved HSIとはsource_typeを分離する。M5右クリックからReference Point Analysisを開けるようにし、Simulation Trace Popoverを左右優先の自動配置へ改善する。
// v0.9.0.08: Timeframe State Builderを追加。確定足・Swing・Dow・Cycle・HSI・BB観測を時間足別State JSONへ統合し、同一Reference Pointで説明可能な要約Traceを生成する。
// v0.9.0.09: Upper Context Decision Engineを追加。WEEK/DAY/H4/H1 Stateを優先順位付きRule Registryで統合し、M5へEntry探索・Hold・Exit監視の許可/禁止を説明可能なDecision Contextとして渡す。
// v0.9.0.10: Simulation Trace / Replay Logを追加。Observation / State Change / Decision / Executionを追記型Eventへ統合し、原因DAG・差分Patch・定期Checkpointから任意時点の状態を復元する。UI表示は日本語中心へ整理する。
// v0.9.0.11: M5 Execution / Position Lifecycleを追加。上位足Decisionを再判定せず、M5 Dow・確定HSI起点・R距離・H1離脱監視に従って仮想Entry / Add-on / Partial Close / Full Close / StopCloseを実行し、Core / Add-on / Runnerを別Lifecycleで保持する。
// v0.9.0.11.1: Run設定をチャート上のモデルレス・移動可能・横幅変更可能なフローティングパネルへ変更する。
// v0.9.0.12: 現在のM5表示範囲を古い足から順に自動評価し、Entry / CloseOK / CloseMissをチャートへ直接表示する。
// v0.9.0.13: 0件完了を無反応に見せず、判定本数・実行件数・主な未成立理由をチャート上へ明示する。
// v0.9.0.14: 表示範囲Simulation中の現在位置を▽付き縦線でライブ表示し、Entry / Closeを発生直後にチャートへ逐次投影する。
// v0.9.0.15: 理由コード・ルールIDを外部日本語カタログで管理し、判断ポップオーバーへ日本語結論とコード対応表を表示する。
// v0.9.0.16: Simulation判断画面を完全ダーク化し右上×を追加。Range実行中の自動ポップアップを禁止し、Human HSI/Userコメントを自動OFF。Simulation専用HSI起点とR線をライブ描画し、上部状態表示を既定折りたたみに変更。
// v0.9.0.26: 上部を操作ボタン中心の1段ツールバーへ整理した構成を維持しつつ、営業日境界線を全窓で共通の特徴的な縦破線へ統一。
// v0.9.0.27: 通常HSI起点をM5 Dow成立時の起点へ固定。後続Swingでは更新せず、Expansion専用に最新押し戻り起点を別解決する二重起点構造を追加。
// v0.9.0.28: M5 Dow成立時の通常HSI起点を、成立直前のHigher Low/Lower Highではなく、比較ペア先頭のprevious Low/High（ダウ波の始点）へ修正。
// v0.9.0.30: 通常Dow起点はREVERSAL_WATCH / NO_TREND / UNDETERMINEDで解除し、同方向再成立でも新しいprevious Swingを採用。Expansion Detection Anchorだけは旧大起点を維持する。
// v0.9.0.29: Dow評価Snapshot生成時に未定義変数regimeを参照してRange Simulationが停止する実行時エラーを修正。
// v0.9.0.31: HSI Anchor Registryの通常/Expansion方向文脈分離後に残った未定義directionContext参照を修正。legacy direction_contextは通常Dow文脈を指し、Expansion文脈を別項目で保持する。
// v0.9.0.32: Run Profile / plugin.jsonのHSI Resolver契約をv0_3へ同期し、既知のv0_2 Profileだけを読込時に安全移行する。
// v0.9.0.38: NORMAL Rule LaneからReEntry / Add-on概念を除外。新しいDow確認ごとの独立Tradeはすべて通常Entryとして記録する。
// v0.9.0.39: HSI起点ごとに8色パレットを順次割り当て、同一起点のR線群は同色、隣接起点は別色として重複時の識別性を改善。中間線も起点色を継承する。
// v0.9.0.40: MT4風の十字カーソルを追加。アクティブパネル内だけに縦横線を表示し、下端へ日時、右端へ価格を表示。左クリックで固定/解除する。
// v0.9.0.41: Dow突破確認時の通常Entry価格を確認足Closeではなく、突破閾値とR2の双方を満たす最初の価格へ修正。
// v0.9.0.42: NORMAL TradeのClose時に通常HSI起点を即破棄し、次回EntryはClose後の新しいM5 Dow Confirmationから新起点を採用する。
// v0.9.0.43: HSI起点リングを横線色へ統一し、十字カーソルを全表示パネルへ同期。Entry / Closeマーカーへ短い指示線と小型終点ドットを追加する。
// v0.9.0.44: Entry / CloseOK / CloseMiss ラベルをチャート外寄りの上下レーンへ退避し、衝突を避けながら小型終点ドットと指示線で対象点へ接続する。
// v0.9.0.45: 実行ラベルを少し横へずらし、終点ドットへ斜めの直線で接続して、縦線・横線との視認差を強める。
// v0.9.0.46: 実行ラベルを上下端から離し、対象点の近くへ適度に寄せつつ、やや角度のついた斜め線で接続する。
// v0.9.0.47: 実行ラベルの横幅に重なるローカル価格帯（High/Low/Close/MA/T3/BB）を計算し、その外側へ配置してチャート本体との重なりを避ける。
// v0.9.0.48: EXPANSION_LITE Rule Lane v0.18を独立実装。R3 Entry、R3.5/R4/R4.5 Add-on、R5/T3/Structural/Anchor Exitを他Laneと混ぜずに評価する。
// v0.9.0.51: NORMAL / EXPANSION / EXPANSION_LITEを独立Portfolioとしてパラレル評価。同一M5足で複数LaneのEntryを許可し、各Lane専用Closeだけで管理する。
// v0.9.0.52: NORMALのCycle Late GuardをH1だけへ限定。H4 Cycle Lateは観測情報として保持するが、通常Entryを禁止しない。
// v0.9.0.53: Cycle Entry許可本数をConfirm barsから完全分離。時間足Profileのcycle.entry_allowed_max_barsを明示値として使用し、Expansion-Lite H1 Entry Windowは14本までとする。
// v0.9.1.00: Batch Simulation Runnerを追加。Dataset×期間×Profile SnapshotをCase単位として逐次実行し、Case内Rule Laneは独立Portfolioでパラレル評価する。処理中画面には累計実現損益とLane別損益を常時表示し、中断判断を可能にする。
// v0.9.1.01: Batch安全化。停止/完了結果を完全版JSON 1本で保存・再試行可能化し、Entry/決済/利益/損失/勝率/含み損益をリアルタイム表示。Target方向・OHLC約定安全柵、Close集計意味修正、進捗描画間引き、評価済みキー圧縮を追加。
// v0.9.1.03: Entry成績表の選択行から、Entry時刻・価格をURLへ渡して該当M5付近を中央表示し、Entry位置へ固定十字を置くチャート遷移Actionを追加。
// v0.9.1.04: Entry Resultsの元Batch JSONから選択TradeのEntry/Add-on/Close Eventを読み込み、該当チャートへ実行マーカーとして投影する。
// v0.9.1.05: Entry成績表からのチャート遷移を新しいタブへ変更し、初期レイアウトをM5実行 + H1+H4へ固定する。
// v0.9.1.09: Simulation Rule v0.24。確定Dow崩壊でEntry前Confirmation/Anchor/Opportunity/R2履歴を終了し、再確定後のprevious Swingを新起点へ採用。Entry後Dow崩壊は観測のみでCloseしない。
// v0.9.1.10: NORMALのWAITING_R2中は、崩壊またはEntry/Missまで最初の有効ConfirmationとHSI起点を固定。同方向の後続Confirmationで起点を乗り換えず、固定起点のR2初回タッチを評価する。
// v0.9.1.11: Dow Trend Snapshotのnormal_dow_structure_breakをTimeframe Stateへ投影し、Batch継続Snapshotでも旧WAITING_R2を確実に失効する。
// v0.9.1.13: NORMAL Entry Gate未成立時の個別Gate判定・事実・時刻を保存し、Batch結果JSON/CSVとして出力する。
// v0.9.1.12: Batch Caseが現在のチャート表示窓・UpperMap非同期読込状態を継承しないよう、対象期間の分析窓と上位足DataSourceをCase単位で固定する.
// v0.9.0.33: 通常Entryを「1 Dow Confirmation ID = 最大1回のR2初回到達Entry = R2.5全Close」へ変更。同じ確認IDによる階段ReEntryを禁止。
// v0.9.0.34: Dow確認時点ですでにR2へ到達済みなら、その確認EventをEntry Triggerとして即Entryする。R2.5到達済みなら見送り、未到達なら従来どおりR2初回到達を待つ。
// v0.9.0.35: M5 Dow確認を「確定済み押し安値/戻り高値の後、直前構造高値/安値をM5確定足で突破した瞬間」へ変更。新しいDow確認Eventごとに1回だけEntryし、Entry地点より先の次HSI境界で全Closeする。
// v0.9.0.36: Run Profileのupper_decision_reimplementationとPlugin許可値の名称不一致を修正。許可値を単一定数化し、Profile検証の回帰テストを追加。
// v0.9.0.37: 共通観測Stateと売買ルール判定を分離。通常Entry/Closeを独立Rule Lane Evaluatorへ切り出し、Normal判定からExpansion/WEEK/DAY依存を除去。HSI圧縮時のDow Confirmation ID欠落も修正。
(function () {
  // v0.8.3.25: DAY UpperMapではDow材料点を非表示化し、H1/H4ダブルクリック同期をDAY側にも明示表示する。
  // v0.8.3.26: DAY UpperMapを広域地図として扱うため、保存サイクル縦線もDAYでは非表示にする。
  // v0.8.3.27: DAY UpperMap専用Confirm barsをJSON設定化し、日足Dow材料点(Active high/low)を表示する。
  // v0.8.3.28: DAY UpperMapのConfirm bars/marker設定の所有者をD1 Data JSONからplugin.jsonへ移動。D1 JSONは差し替え可能な相場データに戻す。
  // v0.8.3.29: DAY UpperMap設定の正本をdisplay_policy.day_upper_map_settingsへ一本化し、chart_layout/signal_policy側の重複設定を読まないように整理。
  // v0.8.3.31: DAY UpperMapにもDAY Confirm bars単位の縦点線を表示。設定はplugin.json day_upper_map_settings.show_confirm_stride_linesを正本にする。
  const PLUGIN_ID = 'gpt_fx_lab.fx_chart_viewer';
  const ACTION_ID = 'OpenFxT3Chart';
  const ENTRY_CHART_URL_ACTION_ID = 'OpenFxEntryChartUrl';
  const URL_ACTION_ALIASES = ['fx_chart', 'openfxt3chart', 'openfxchartviewer', 'fxt3chart', 'gpt_fx_lab.fx_chart'];
  const DEFAULT_URL_DATA = 'overlay/gpt_fx_lab/data/fx_usdjpy_m5_t3_data_v0_1.json';
  const DEFAULT_URL_VIEW = 'overlay/gpt_fx_lab/view_defs/fx_usdjpy_t3_view_def_v0_1.json';
  const DEFAULT_UPPER_MAP_DATA = 'overlay/gpt_fx_lab/data/fx_usdjpy_d1_t3_data_v0_1.json';
  const DEFAULT_COMMENT_SIDECAR_FILE = 'fx_usdjpy_m5_t3_data_v0_1.chart_comments.json';
  const DEFAULT_SIMULATION_TRACE_FILE = 'fx_usdjpy_m5_t3_data_v0_1.simulation_trace.json';
  const DEFAULT_SIMULATION_RUN_PROFILE_FILE = 'fx_simulation_run_profile_normal_plus_expansion_lite_v0_1.json';
  const DEFAULT_SIMULATION_REASON_RULE_CATALOG_FILE = 'fx_simulation_reason_rule_catalog_v0_1.json';
  const REQUIRED_SIMULATION_TIMEFRAMES = ['WEEK', 'DAY', 'H4', 'H1', 'M5'];
  const COMMENT_LOCAL_STORAGE_PREFIX = 'gpt_fx_lab.fx_chart_viewer.comment_sidecar:';
  const SIMULATION_TRACE_SOURCE_TYPE = 'simulation_trace';
  const SHARED_SWING_POINT_DETECTOR_ID = 'shared_center_window_unique_extreme_v0_1';
  const SHARED_SWING_POINT_GENERATOR = 'shared_swing_point_detector';
  const DOW_TREND_EVALUATOR_ID = 'shared_confirmed_swing_structure_v0_1';
  const DOW_TREND_GENERATOR = 'dow_trend_evaluator';
  const CYCLE_POSITION_EVALUATOR_ID = 'shared_latest_usable_swing_origin_v0_1';
  const CYCLE_POSITION_GENERATOR = 'cycle_position_evaluator';
  const HSI_ANCHOR_REGISTRY_ID = 'shared_multi_role_hsi_anchor_registry_v0_1';
  const HSI_ANCHOR_RESOLVER_ID = 'normal_dow_confirmation_opportunity_plus_expansion_detection_retain_resolver_v0_4';
  const LEGACY_HSI_ANCHOR_RESOLVER_IDS = new Set([
    'dow_regime_fixed_plus_expansion_dual_anchor_resolver_v0_2',
    'normal_dow_reset_plus_expansion_detection_retain_resolver_v0_3'
  ]);
  const HSI_ANCHOR_GENERATOR = 'hsi_anchor_registry_resolver';
  const TIMEFRAME_STATE_BUILDER_ID = 'shared_timeframe_state_builder_v0_1';
  const TIMEFRAME_STATE_GENERATOR = 'timeframe_state_builder';
  const UPPER_CONTEXT_DECISION_ENGINE_ID = 'priority_specification_upper_context_v0_1';
  const UPPER_CONTEXT_DECISION_GENERATOR = 'upper_context_decision_engine';
  const TRACE_REPLAY_ENGINE_ID = 'append_only_causal_trace_replay_v0_1';
  const M5_EXECUTION_ENGINE_ID = 'm5_rule_lane_execution_orchestrator_v0_2';
  const M5_EXECUTION_GENERATOR = 'm5_execution_position_lifecycle';
  const RULE_LANE_NORMAL = 'NORMAL';
  const RULE_LANE_EXPANSION = 'EXPANSION';
  const RULE_LANE_EXPANSION_LITE = 'EXPANSION_LITE';
  const ENTRY_LANE_MODE_NORMAL_AND_EXPANSION_LITE = 'NORMAL_AND_EXPANSION_LITE';
  const ENTRY_LANE_MODE_PARALLEL_RULE_LANES = 'PARALLEL_RULE_LANES';
  const NORMAL_ENTRY_EVALUATOR_ID = 'normal_m5_entry_evaluator_v0_1';
  const NORMAL_CLOSE_EVALUATOR_ID = 'normal_m5_close_evaluator_v0_1';
  const EXPANSION_ENTRY_EVALUATOR_ID = 'expansion_entry_evaluator_placeholder_v0_1';
  const EXPANSION_CLOSE_EVALUATOR_ID = 'expansion_close_evaluator_placeholder_v0_1';
  const EXPANSION_LITE_ENTRY_EVALUATOR_ID = 'expansion_lite_entry_evaluator_v0_1';
  const EXPANSION_LITE_CLOSE_EVALUATOR_ID = 'expansion_lite_close_evaluator_v0_1';
  const NORMAL_RULE_VERSION = 'v0.24';
  const EXPANSION_LITE_RULE_VERSION = 'v0.18';
  const EXPANSION_LITE_ENTRY_GUARD_RULE_VERSION = 'v0.21';
  const NORMAL_ENTRY_V0_14_UPPER_DECISION_EXCEPTION = 'normal_entry_v0_14_m5_dow_breakout_next_hsi_boundary_explicit_exception';
  const NORMAL_ENTRY_V0_15_UPPER_DECISION_EXCEPTION = 'normal_entry_v0_15_normal_entry_only_no_reentry_explicit_exception';
  const NORMAL_ENTRY_V0_16_UPPER_DECISION_EXCEPTION = 'normal_entry_v0_16_dow_breakout_threshold_entry_explicit_exception';
  const NORMAL_ENTRY_V0_17_UPPER_DECISION_EXCEPTION = 'normal_entry_v0_17_trade_scoped_hsi_anchor_explicit_exception';
  const ALLOWED_UPPER_DECISION_REIMPLEMENTATIONS = new Set([
    'forbidden',
    'normal_entry_v0_6_explicit_exception',
    'normal_entry_v0_7_explicit_exception',
    'normal_entry_v0_8_explicit_exception',
    'normal_entry_v0_10_dow_origin_previous_swing_explicit_exception',
    'normal_entry_v0_11_normal_reset_expansion_retain_explicit_exception',
    'normal_entry_v0_12_dow_confirmation_r2_r25_explicit_exception',
    'normal_entry_v0_13_dow_confirmation_r2_state_explicit_exception',
    NORMAL_ENTRY_V0_14_UPPER_DECISION_EXCEPTION,
    NORMAL_ENTRY_V0_15_UPPER_DECISION_EXCEPTION,
    NORMAL_ENTRY_V0_16_UPPER_DECISION_EXCEPTION,
    NORMAL_ENTRY_V0_17_UPPER_DECISION_EXCEPTION
  ]);
  const VISIBLE_RANGE_SIMULATION_RUNNER_ID = 'visible_m5_window_reference_step_runner_v0_1';
  const BATCH_SIMULATION_RUNNER_ID = 'batch_simulation_case_sequential_runner_v0_1';
  const BATCH_SIMULATION_SCHEMA_VERSION = 'fx_batch_simulation_run_v0_1';
  const BATCH_SIMULATION_MANIFEST_PATH = 'studio_overlays/gpt_fx_lab/studio_manifest.json';
  const TRACE_EVENT_CLASSES = ['OBSERVATION', 'STATE_CHANGE', 'DECISION', 'EXECUTION'];
  const SIMULATION_HSI_ANCHOR_SOURCE_TYPE = 'simulation_hsi_anchor';
  const SAVED_HSI_SOURCE_TYPE = 'human_hsi';
  const SAVED_HSI_EVENT_TYPE = 'hsi_anchor';
  const HSI_RANGE_LEVELS = [
    { raw: 55, label: 'R1' },
    { raw: 89, label: 'R2' },
    { raw: 117, label: 'R2.5' },
    { raw: 144, label: 'R3' },
    { raw: 188, label: 'R3.5' },
    { raw: 233, label: 'R4' },
    { raw: 305, label: 'R4.5' },
    { raw: 377, label: 'R5' },
    { raw: 493, label: 'R5.5' },
    { raw: 610, label: 'R6' },
    { raw: 798, label: 'R6.5' },
    { raw: 987, label: 'R7' }
  ];
  const HSI_LINE_COLOR_PALETTE = [
    {
      id: 'cyan',
      line: 'rgba(34, 211, 238, 0.90)',
      savedLine: 'rgba(34, 211, 238, 0.68)',
      observationLine: 'rgba(165, 243, 252, 0.74)',
      label: 'rgba(207, 250, 254, 0.98)',
      observationLabel: 'rgba(207, 250, 254, 0.88)',
      anchorFill: 'rgba(34, 211, 238, 0.94)',
      anchorStroke: 'rgba(236, 254, 255, 0.98)',
      glow: 'rgba(34, 211, 238, 0.72)'
    },
    {
      id: 'amber',
      line: 'rgba(251, 191, 36, 0.92)',
      savedLine: 'rgba(251, 191, 36, 0.70)',
      observationLine: 'rgba(253, 230, 138, 0.76)',
      label: 'rgba(254, 243, 199, 0.98)',
      observationLabel: 'rgba(254, 243, 199, 0.88)',
      anchorFill: 'rgba(251, 191, 36, 0.95)',
      anchorStroke: 'rgba(255, 251, 235, 0.98)',
      glow: 'rgba(251, 191, 36, 0.72)'
    },
    {
      id: 'violet',
      line: 'rgba(192, 132, 252, 0.92)',
      savedLine: 'rgba(192, 132, 252, 0.70)',
      observationLine: 'rgba(221, 214, 254, 0.76)',
      label: 'rgba(237, 233, 254, 0.98)',
      observationLabel: 'rgba(237, 233, 254, 0.88)',
      anchorFill: 'rgba(192, 132, 252, 0.95)',
      anchorStroke: 'rgba(245, 243, 255, 0.98)',
      glow: 'rgba(192, 132, 252, 0.72)'
    },
    {
      id: 'lime',
      line: 'rgba(163, 230, 53, 0.90)',
      savedLine: 'rgba(163, 230, 53, 0.68)',
      observationLine: 'rgba(217, 249, 157, 0.74)',
      label: 'rgba(236, 252, 203, 0.98)',
      observationLabel: 'rgba(236, 252, 203, 0.88)',
      anchorFill: 'rgba(163, 230, 53, 0.94)',
      anchorStroke: 'rgba(247, 254, 231, 0.98)',
      glow: 'rgba(163, 230, 53, 0.70)'
    },
    {
      id: 'rose',
      line: 'rgba(251, 113, 133, 0.92)',
      savedLine: 'rgba(251, 113, 133, 0.70)',
      observationLine: 'rgba(254, 205, 211, 0.76)',
      label: 'rgba(255, 228, 230, 0.98)',
      observationLabel: 'rgba(255, 228, 230, 0.88)',
      anchorFill: 'rgba(251, 113, 133, 0.95)',
      anchorStroke: 'rgba(255, 241, 242, 0.98)',
      glow: 'rgba(251, 113, 133, 0.72)'
    },
    {
      id: 'sky',
      line: 'rgba(96, 165, 250, 0.92)',
      savedLine: 'rgba(96, 165, 250, 0.70)',
      observationLine: 'rgba(191, 219, 254, 0.76)',
      label: 'rgba(219, 234, 254, 0.98)',
      observationLabel: 'rgba(219, 234, 254, 0.88)',
      anchorFill: 'rgba(96, 165, 250, 0.95)',
      anchorStroke: 'rgba(239, 246, 255, 0.98)',
      glow: 'rgba(96, 165, 250, 0.72)'
    },
    {
      id: 'orange',
      line: 'rgba(251, 146, 60, 0.92)',
      savedLine: 'rgba(251, 146, 60, 0.70)',
      observationLine: 'rgba(254, 215, 170, 0.76)',
      label: 'rgba(255, 237, 213, 0.98)',
      observationLabel: 'rgba(255, 237, 213, 0.88)',
      anchorFill: 'rgba(251, 146, 60, 0.95)',
      anchorStroke: 'rgba(255, 247, 237, 0.98)',
      glow: 'rgba(251, 146, 60, 0.72)'
    },
    {
      id: 'teal',
      line: 'rgba(45, 212, 191, 0.92)',
      savedLine: 'rgba(45, 212, 191, 0.70)',
      observationLine: 'rgba(153, 246, 228, 0.76)',
      label: 'rgba(204, 251, 241, 0.98)',
      observationLabel: 'rgba(204, 251, 241, 0.88)',
      anchorFill: 'rgba(45, 212, 191, 0.95)',
      anchorStroke: 'rgba(240, 253, 250, 0.98)',
      glow: 'rgba(45, 212, 191, 0.72)'
    }
  ];
  const HSI_MIDPOINT_OBSERVATIONS = [
    { raw: 117, label: 'R2.5' },
    { raw: 188, label: 'R3.5' },
    { raw: 305, label: 'R4.5' }
  ];
  const HSI_R23_M_RAW_VALUE = 117;
  const HSI_R23_M_LABEL = 'R2.5';
  const SAVED_VERTICAL_SOURCE_TYPE = 'human_vertical_marker';
  const SAVED_VERTICAL_EVENT_TYPE = 'vertical_marker';
  const SAVED_CYCLE_VERTICAL_SOURCE_TYPE = 'human_cycle_vertical_marker';
  const SAVED_CYCLE_VERTICAL_EVENT_TYPE = 'cycle_vertical_marker';
  const SAVED_TEXT_LABEL_SOURCE_TYPE = 'human_text_label';
  const SAVED_TEXT_LABEL_EVENT_TYPE = 'chart_text_label';
  let pluginManifest = null;
  let defaultUrlLaunchSourcePromise = null;

  function ensureStyle() {
    if (document.getElementById('gptFxLabChartViewerStyle')) return;
    const style = document.createElement('style');
    style.id = 'gptFxLabChartViewerStyle';
    style.textContent = `
      .gpt-fx-chart-backdrop {
        position: fixed;
        inset: 0;
        z-index: 9999;
        display: flex;
        align-items: center;
        justify-content: center;
        background: rgba(15, 23, 42, 0.56);
        backdrop-filter: blur(4px);
      }
      .gpt-fx-chart-modal {
        position: relative;
        width: min(1440px, calc(100vw - 24px));
        height: min(860px, calc(100vh - 20px));
        display: grid;
        grid-template-rows: auto auto 1fr auto;
        overflow: hidden;
        border: 1px solid rgba(148, 163, 184, 0.42);
        border-radius: 18px;
        background: linear-gradient(180deg, #0f172a 0%, #111827 46%, #0b1120 100%);
        color: #e5e7eb;
        box-shadow: 0 30px 80px rgba(0, 0, 0, 0.42);
        transition: width .16s ease, height .16s ease, border-radius .16s ease;
      }
      .gpt-fx-chart-modal.is-wide {
        width: calc(100vw - 20px);
        height: calc(100vh - 20px);
        border-radius: 14px;
      }
      /* Batch実行中は、画面上で見えていないチャート系UIを完全停止・非表示にする。 */
      .gpt-fx-chart-backdrop.is-batch-running .gpt-fx-chart-modal {
        grid-template-rows: 1fr;
      }
      .gpt-fx-chart-backdrop.is-batch-running .gpt-fx-chart-window-btn,
      .gpt-fx-chart-backdrop.is-batch-running .gpt-fx-chart-header,
      .gpt-fx-chart-backdrop.is-batch-running .gpt-fx-chart-meta,
      .gpt-fx-chart-backdrop.is-batch-running .gpt-fx-chart-scroll,
      .gpt-fx-chart-backdrop.is-batch-running .gpt-fx-chart-settings-panel,
      .gpt-fx-chart-backdrop.is-batch-running .gpt-fx-chart-range-result,
      .gpt-fx-chart-backdrop.is-batch-running .gpt-fx-chart-tooltip,
      .gpt-fx-chart-backdrop.is-batch-running .gpt-fx-chart-comment-popover,
      .gpt-fx-chart-backdrop.is-batch-running .gpt-fx-chart-simulation-popover,
      .gpt-fx-chart-backdrop.is-batch-running .gpt-fx-chart-text-label-popover,
      .gpt-fx-chart-backdrop.is-batch-running .gpt-fx-chart-context-menu,
      .gpt-fx-chart-backdrop.is-batch-running .gpt-fx-chart-footer {
        display: none !important;
      }
      .gpt-fx-chart-backdrop.is-batch-running .gpt-fx-chart-body {
        padding: 0;
      }
      .gpt-fx-chart-header {
        display: grid;
        grid-template-columns: minmax(250px, 320px) minmax(0, 1fr);
        align-items: start;
        gap: 10px;
        min-height: 0;
        padding: 10px 48px 8px 14px;
        border-bottom: 1px solid rgba(148, 163, 184, 0.22);
      }
      .gpt-fx-chart-header > div:first-child {
        min-width: 0;
      }
      .gpt-fx-chart-window-btn {
        position: absolute;
        top: 10px;
        right: 10px;
        z-index: 2;
        width: 30px;
        height: 30px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        padding: 0;
        border-radius: 8px;
        border: 1px solid rgba(148, 163, 184, 0.56);
        background: rgba(15, 23, 42, 0.72);
        color: #e5e7eb;
        font-size: 15px;
        font-weight: 900;
        line-height: 1;
        cursor: pointer;
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.22);
      }
      .gpt-fx-chart-window-btn:hover {
        background: rgba(30, 41, 59, 0.92);
        border-color: rgba(226, 232, 240, 0.74);
      }
      .gpt-fx-chart-window-btn.is-active {
        background: linear-gradient(135deg, rgba(6, 182, 212, 0.82), rgba(37, 99, 235, 0.82));
        border-color: rgba(125, 211, 252, 0.92);
      }
      .gpt-fx-chart-title {
        margin: 0;
        font-size: 16px;
        line-height: 1.28;
        font-weight: 800;
        letter-spacing: 0.01em;
        display: -webkit-box;
        -webkit-box-orient: vertical;
        -webkit-line-clamp: 3;
        overflow: hidden;
      }
      .gpt-fx-chart-subtitle {
        margin-top: 4px;
        color: #94a3b8;
        font-size: 10px;
        line-height: 1.35;
        display: -webkit-box;
        -webkit-box-orient: vertical;
        -webkit-line-clamp: 3;
        overflow: hidden;
      }
      .gpt-fx-chart-actions {
        min-width: 0;
        display: grid;
        grid-auto-flow: column;
        grid-template-rows: minmax(30px, auto);
        grid-auto-columns: max-content;
        align-items: center;
        justify-content: start;
        gap: 6px;
        overflow-x: auto;
        overflow-y: hidden;
        overscroll-behavior-x: contain;
        padding: 0 2px 6px;
        scrollbar-width: thin;
        scrollbar-color: rgba(148, 163, 184, 0.58) rgba(15, 23, 42, 0.28);
      }
      .gpt-fx-chart-actions::-webkit-scrollbar { height: 7px; }
      .gpt-fx-chart-actions::-webkit-scrollbar-track {
        background: rgba(15, 23, 42, 0.32);
        border-radius: 999px;
      }
      .gpt-fx-chart-actions::-webkit-scrollbar-thumb {
        background: rgba(148, 163, 184, 0.56);
        border-radius: 999px;
      }
      .gpt-fx-chart-settings-panel {
        position: absolute;
        z-index: 13;
        top: 12px;
        right: 12px;
        width: min(640px, calc(100% - 24px));
        max-height: calc(100% - 24px);
        display: none;
        overflow: auto;
        border: 1px solid rgba(56, 189, 248, 0.58);
        border-radius: 15px;
        background: rgba(8, 20, 35, 0.985);
        color: #e5e7eb;
        box-shadow: 0 24px 60px rgba(0, 0, 0, 0.46);
        backdrop-filter: blur(10px);
      }
      .gpt-fx-chart-settings-panel.is-open { display: block; }
      .gpt-fx-chart-settings-header {
        position: sticky;
        top: 0;
        z-index: 2;
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 12px;
        padding: 11px 13px;
        border-bottom: 1px solid rgba(148, 163, 184, 0.20);
        background: rgba(8, 20, 35, 0.98);
      }
      .gpt-fx-chart-settings-title {
        margin: 0;
        font-size: 14px;
        font-weight: 900;
        color: #e0f2fe;
      }
      .gpt-fx-chart-settings-subtitle {
        margin-top: 2px;
        color: #94a3b8;
        font-size: 10px;
      }
      .gpt-fx-chart-settings-body {
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 10px;
        padding: 12px;
      }
      .gpt-fx-chart-settings-section {
        min-width: 0;
        padding: 10px;
        border: 1px solid rgba(148, 163, 184, 0.20);
        border-radius: 12px;
        background: rgba(15, 23, 42, 0.58);
      }
      .gpt-fx-chart-settings-section.is-wide { grid-column: 1 / -1; }
      .gpt-fx-chart-settings-section-title {
        margin: 0 0 8px;
        color: #7dd3fc;
        font-size: 11px;
        font-weight: 900;
        letter-spacing: 0.04em;
      }
      .gpt-fx-chart-settings-controls {
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        gap: 6px;
      }
      .gpt-fx-chart-settings-close {
        width: 30px;
        height: 30px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        border: 1px solid rgba(148, 163, 184, 0.42);
        border-radius: 9px;
        background: rgba(30, 41, 59, 0.76);
        color: #e5e7eb;
        font-size: 18px;
        line-height: 1;
        cursor: pointer;
      }
      .gpt-fx-chart-settings-close:hover {
        border-color: rgba(125, 211, 252, 0.78);
        background: rgba(14, 116, 144, 0.48);
      }
      @media (max-width: 760px) {
        .gpt-fx-chart-settings-body { grid-template-columns: 1fr; }
        .gpt-fx-chart-settings-section.is-wide { grid-column: auto; }
      }
      .gpt-fx-chart-btn {
        border: 1px solid rgba(148, 163, 184, 0.32);
        border-radius: 999px;
        background: rgba(30, 41, 59, 0.72);
        color: #e5e7eb;
        padding: 7px 12px;
        font-size: 12px;
        cursor: pointer;
      }
      .gpt-fx-chart-btn:hover { background: rgba(51, 65, 85, 0.9); }
      .gpt-fx-chart-btn.is-active {
        border-color: rgba(125, 211, 252, 0.72);
        background: rgba(14, 116, 144, 0.46);
        color: #e0f2fe;
      }
      .gpt-fx-chart-btn.is-muted {
        opacity: 0.58;
      }
      .gpt-fx-chart-control {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        border: 1px solid rgba(148, 163, 184, 0.30);
        border-radius: 999px;
        background: rgba(15, 23, 42, 0.54);
        color: #cbd5e1;
        padding: 5px 10px;
        font-size: 12px;
      }
      .gpt-fx-chart-number {
        width: 58px;
        min-height: 24px;
        box-sizing: border-box;
        border: 1px solid rgba(148, 163, 184, 0.34);
        border-radius: 9px;
        background: rgba(2, 6, 23, 0.48);
        color: #e5e7eb;
        padding: 4px 7px;
        font-size: 12px;
        line-height: 1.25;
      }
      .gpt-fx-chart-text {
        width: 96px;
        min-height: 24px;
        box-sizing: border-box;
        border: 1px solid rgba(148, 163, 184, 0.34);
        border-radius: 9px;
        background: rgba(2, 6, 23, 0.48);
        color: #e5e7eb;
        padding: 4px 8px;
        font-size: 12px;
        line-height: 1.25;
      }
      .gpt-fx-chart-number.is-scale {
        width: 68px;
        height: 30px;
        min-height: 30px;
        padding: 4px 8px;
        line-height: 1.3;
      }
      .gpt-fx-chart-scale-wrap {
        display: inline-flex;
        align-items: stretch;
        gap: 4px;
      }
      .gpt-fx-chart-scale-buttons {
        display: inline-grid;
        grid-template-rows: 1fr 1fr;
        gap: 3px;
      }
      .gpt-fx-chart-scale-step-btn {
        width: 30px;
        height: 18px;
        min-height: 18px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        border: 1px solid rgba(148, 163, 184, 0.44);
        border-radius: 7px;
        background: rgba(30, 41, 59, 0.72);
        color: #e5e7eb;
        font-size: 11px;
        font-weight: 900;
        line-height: 1;
        cursor: pointer;
        padding: 0;
      }
      .gpt-fx-chart-scale-step-btn:hover {
        background: rgba(14, 116, 144, 0.68);
        border-color: rgba(125, 211, 252, 0.82);
      }
      .gpt-fx-chart-scale-step-btn:active {
        transform: translateY(1px);
      }
      .gpt-fx-chart-meta {
        display: flex;
        gap: 8px;
        padding: 10px 18px;
        flex-wrap: wrap;
        border-bottom: 1px solid rgba(148, 163, 184, 0.16);
      }
      .gpt-fx-chart-meta.is-collapsed {
        display: none;
      }
      .gpt-fx-chart-pill {
        border: 1px solid rgba(148, 163, 184, 0.24);
        border-radius: 999px;
        padding: 5px 9px;
        background: rgba(15, 23, 42, 0.5);
        color: #cbd5e1;
        font-size: 12px;
      }
      .gpt-fx-chart-body {
        position: relative;
        min-height: 0;
        padding: 8px 12px 4px;
        overflow: hidden;
      }
      .gpt-fx-chart-scroll {
        position: relative;
        width: 100%;
        height: 100%;
        overflow-x: auto;
        overflow-y: hidden;
        overscroll-behavior: contain;
        scrollbar-color: rgba(148, 163, 184, 0.62) rgba(15, 23, 42, 0.36);
        scrollbar-width: thin;
      }
      .gpt-fx-chart-scroll::-webkit-scrollbar { height: 10px; }
      .gpt-fx-chart-scroll::-webkit-scrollbar-track {
        background: rgba(15, 23, 42, 0.42);
        border-radius: 999px;
      }
      .gpt-fx-chart-scroll::-webkit-scrollbar-thumb {
        background: rgba(148, 163, 184, 0.58);
        border-radius: 999px;
      }
      .gpt-fx-chart-canvas {
        width: 100%;
        height: 100%;
        display: block;
        cursor: crosshair;
        border-radius: 14px;
        background: linear-gradient(180deg, rgba(15, 23, 42, 0.72), rgba(2, 6, 23, 0.72));
      }
      @media (max-width: 980px) {
        .gpt-fx-chart-header {
          grid-template-columns: minmax(220px, 280px) minmax(0, 1fr);
          padding-left: 10px;
        }
        .gpt-fx-chart-title {
          font-size: 14px;
          -webkit-line-clamp: 3;
        }
        .gpt-fx-chart-subtitle {
          -webkit-line-clamp: 2;
        }
      }
      @media (max-width: 720px) {
        .gpt-fx-chart-header {
          grid-template-columns: 1fr;
        }
        .gpt-fx-chart-header > div:first-child {
          display: none;
        }
      }
      .gpt-fx-chart-range-result {
        position: absolute;
        z-index: 8;
        top: 20px;
        left: 50%;
        width: min(680px, calc(100% - 64px));
        transform: translateX(-50%);
        display: none;
        align-items: flex-start;
        gap: 12px;
        padding: 11px 13px;
        border: 1px solid rgba(56, 189, 248, 0.54);
        border-radius: 12px;
        background: rgba(8, 20, 35, 0.96);
        color: #e2e8f0;
        box-shadow: 0 18px 48px rgba(0,0,0,.42);
        pointer-events: auto;
      }
      .gpt-fx-chart-range-result.is-visible { display: flex; }
      .gpt-fx-chart-range-result.is-running { border-color: rgba(34, 211, 238, 0.72); }
      .gpt-fx-chart-range-result.is-zero { border-color: rgba(250, 204, 21, 0.70); background: rgba(42, 31, 8, 0.96); }
      .gpt-fx-chart-range-result.is-success { border-color: rgba(74, 222, 128, 0.66); background: rgba(7, 31, 22, 0.96); }
      .gpt-fx-chart-range-result.is-error { border-color: rgba(248, 113, 113, 0.76); background: rgba(45, 13, 18, 0.97); }
      .gpt-fx-chart-range-result-main { flex: 1 1 auto; min-width: 0; }
      .gpt-fx-chart-range-result-title { font-size: 13px; font-weight: 900; line-height: 1.4; }
      .gpt-fx-chart-range-result-body { margin-top: 3px; font-size: 11px; line-height: 1.5; color: rgba(226,232,240,.92); overflow-wrap: anywhere; }
      .gpt-fx-chart-range-result-close {
        flex: 0 0 auto;
        width: 26px;
        height: 26px;
        border: 1px solid rgba(148,163,184,.42);
        border-radius: 8px;
        background: rgba(15,23,42,.72);
        color: #e2e8f0;
        cursor: pointer;
        font-weight: 900;
      }
      .gpt-fx-chart-tooltip {
        position: absolute;
        pointer-events: none;
        min-width: 178px;
        max-width: 420px;
        padding: 8px 10px;
        border: 1px solid rgba(148, 163, 184, 0.36);
        border-radius: 10px;
        background: rgba(15, 23, 42, 0.93);
        color: #e5e7eb;
        font-size: 12px;
        line-height: 1.48;
        box-shadow: 0 14px 36px rgba(0,0,0,.34);
        opacity: 0;
        transform: translate(-50%, calc(-100% - 12px));
        transition: opacity .08s ease;
        white-space: nowrap;
        z-index: 3;
      }
      .gpt-fx-chart-comment-popover {
        position: absolute;
        z-index: 4;
        min-width: 230px;
        max-width: min(360px, calc(100% - 32px));
        padding: 10px 11px;
        border: 1px solid rgba(250, 204, 21, 0.42);
        border-radius: 12px;
        background: rgba(15, 23, 42, 0.96);
        color: #e5e7eb;
        box-shadow: 0 18px 44px rgba(0,0,0,.40);
        opacity: 0;
        pointer-events: none;
        transform: translate(8px, calc(-100% - 10px));
        transition: opacity .08s ease;
      }
      .gpt-fx-chart-comment-popover.is-open {
        opacity: 1;
        pointer-events: auto;
      }
      .gpt-fx-chart-comment-popover.is-below {
        transform: translate(8px, 10px);
      }
      .gpt-fx-chart-simulation-popover {
        position: absolute;
        z-index: 5;
        width: min(780px, calc(100% - 32px));
        min-width: min(520px, calc(100% - 32px));
        max-width: calc(100% - 20px);
        min-height: 220px;
        max-height: min(620px, calc(100% - 20px));
        overflow: auto;
        resize: both;
        padding: 11px 12px;
        border: 1px solid rgba(34, 211, 238, 0.58);
        border-radius: 12px;
        background: #081423 !important;
        color: #e5e7eb !important;
        color-scheme: dark;
        scrollbar-color: rgba(71, 85, 105, 0.95) #07111f;
        scrollbar-width: thin;
        box-shadow: 0 18px 48px rgba(0,0,0,.46);
        opacity: 0;
        pointer-events: none;
        transform: none;
        transition: opacity .08s ease;
      }
      .gpt-fx-chart-simulation-popover * {
        box-sizing: border-box;
      }
      .gpt-fx-chart-simulation-popover::-webkit-scrollbar {
        width: 10px;
        height: 10px;
      }
      .gpt-fx-chart-simulation-popover::-webkit-scrollbar-track {
        background: #07111f;
      }
      .gpt-fx-chart-simulation-popover::-webkit-scrollbar-thumb {
        border: 2px solid #07111f;
        border-radius: 999px;
        background: rgba(71, 85, 105, 0.95);
      }
      .gpt-fx-chart-simulation-popover-close {
        position: sticky;
        top: 0;
        float: right;
        z-index: 3;
        width: 28px;
        height: 28px;
        margin: -3px -3px 2px 8px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        border: 1px solid rgba(148, 163, 184, 0.42);
        border-radius: 8px;
        background: #111c2c;
        color: #f8fafc;
        font-size: 16px;
        font-weight: 900;
        line-height: 1;
        cursor: pointer;
      }
      .gpt-fx-chart-simulation-popover-close:hover {
        border-color: rgba(103, 232, 249, 0.82);
        background: #173047;
      }
      .gpt-fx-chart-simulation-popover.is-open {
        opacity: 1;
        pointer-events: auto;
      }
      .gpt-fx-chart-simulation-popover.is-below { transform: none; }
      .gpt-fx-chart-simulation-popover[data-placement="left"],
      .gpt-fx-chart-simulation-popover[data-placement="right"] {
        max-height: min(520px, calc(100% - 20px));
      }
      .gpt-fx-chart-simulation-title {
        margin: 0 0 5px;
        color: #a5f3fc;
        font-size: 12px;
        font-weight: 900;
      }
      .gpt-fx-chart-simulation-section {
        margin-top: 8px;
        padding-top: 7px;
        border-top: 1px solid rgba(34, 211, 238, 0.20);
      }
      .gpt-fx-chart-simulation-section-title {
        margin-bottom: 4px;
        color: #67e8f9;
        font-size: 10px;
        font-weight: 800;
        letter-spacing: .04em;
        text-transform: uppercase;
      }
      .gpt-fx-chart-simulation-code {
        margin: 0;
        padding: 7px 8px;
        border-radius: 8px;
        background: rgba(2, 6, 23, 0.58);
        color: #cbd5e1;
        font: 10px/1.42 ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
        white-space: pre-wrap;
        word-break: break-word;
      }
      .gpt-fx-chart-simulation-judgment {
        margin: 7px 0 2px;
        padding: 9px 10px;
        border: 1px solid rgba(34, 197, 94, 0.42);
        border-radius: 9px;
        background: rgba(20, 83, 45, 0.22);
      }
      .gpt-fx-chart-simulation-judgment-title {
        color: #bbf7d0;
        font-size: 12px;
        font-weight: 900;
        line-height: 1.45;
      }
      .gpt-fx-chart-simulation-judgment-body {
        margin-top: 4px;
        color: #dcfce7;
        font-size: 11px;
        font-weight: 650;
        line-height: 1.55;
      }
      .gpt-fx-chart-simulation-risk-card {
        margin: 8px 0 2px;
        padding: 10px 11px;
        border: 1px solid rgba(250, 204, 21, 0.48);
        border-radius: 10px;
        background: rgba(113, 63, 18, 0.18);
      }
      .gpt-fx-chart-simulation-risk-main {
        display: grid;
        grid-template-columns: minmax(180px, 1.2fr) minmax(160px, 1fr);
        gap: 8px 14px;
        align-items: start;
      }
      .gpt-fx-chart-simulation-risk-stop {
        color: #fde68a;
        font-size: 15px;
        font-weight: 950;
        line-height: 1.4;
      }
      .gpt-fx-chart-simulation-risk-target {
        color: #e0f2fe;
        font-size: 12px;
        font-weight: 850;
        line-height: 1.45;
      }
      .gpt-fx-chart-simulation-risk-metrics {
        display: grid;
        grid-template-columns: repeat(4, minmax(120px, 1fr));
        gap: 6px;
        margin-top: 9px;
      }
      .gpt-fx-chart-simulation-risk-metric {
        padding: 7px 8px;
        border: 1px solid rgba(148, 163, 184, 0.18);
        border-radius: 8px;
        background: rgba(2, 6, 23, 0.44);
      }
      .gpt-fx-chart-simulation-risk-metric-label {
        color: #94a3b8;
        font-size: 9px;
        font-weight: 800;
      }
      .gpt-fx-chart-simulation-risk-metric-value {
        margin-top: 2px;
        color: #f8fafc;
        font-size: 12px;
        font-weight: 950;
      }
      .gpt-fx-chart-simulation-risk-metric-value.is-positive { color: #86efac; }
      .gpt-fx-chart-simulation-risk-metric-value.is-negative { color: #fca5a5; }
      .gpt-fx-chart-simulation-risk-note {
        margin-top: 7px;
        color: #94a3b8;
        font-size: 9px;
        line-height: 1.45;
      }
      @media (max-width: 760px) {
        .gpt-fx-chart-simulation-risk-main { grid-template-columns: 1fr; }
        .gpt-fx-chart-simulation-risk-metrics { grid-template-columns: repeat(2, minmax(120px, 1fr)); }
      }
      .gpt-fx-chart-simulation-table-scroll {
        width: 100%;
        overflow-x: auto;
        border-radius: 8px;
        scrollbar-color: rgba(71, 85, 105, 0.95) #07111f;
      }
      .gpt-fx-chart-simulation-code-table {
        width: 100%;
        min-width: 700px;
        table-layout: fixed;
        border-collapse: collapse;
        background: #07111f !important;
        color: #e5e7eb !important;
        font-size: 10px;
        line-height: 1.45;
      }
      .gpt-fx-chart-simulation-code-table tbody,
      .gpt-fx-chart-simulation-code-table tr {
        background: #07111f !important;
        color: #e5e7eb !important;
      }
      .gpt-fx-chart-simulation-code-table th,
      .gpt-fx-chart-simulation-code-table td {
        padding: 6px 8px;
        border: 1px solid rgba(148, 163, 184, 0.18);
        vertical-align: top;
        text-align: left;
      }
      .gpt-fx-chart-simulation-code-table th {
        color: #a5f3fc !important;
        background: #0b2638 !important;
        font-weight: 800;
      }
      .gpt-fx-chart-simulation-code-table th:first-child,
      .gpt-fx-chart-simulation-code-table td:first-child {
        width: 66%;
      }
      .gpt-fx-chart-simulation-code-table td:first-child {
        color: #f1f5f9 !important;
        background: #07111f !important;
        font-weight: 700;
        white-space: normal;
        overflow-wrap: anywhere;
      }
      .gpt-fx-chart-simulation-code-table th:last-child,
      .gpt-fx-chart-simulation-code-table td:last-child {
        width: 34%;
      }
      .gpt-fx-chart-simulation-code-table td:last-child {
        color: #94a3b8 !important;
        background: #07111f !important;
        font: 9px/1.45 ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
        overflow-wrap: anywhere;
      }
      .gpt-fx-chart-batch-overlay {
        position: absolute;
        inset: 12px 16px 6px;
        z-index: 34;
        display: none;
        pointer-events: none;
      }
      .gpt-fx-chart-batch-overlay.is-open { display: block; }
      .gpt-fx-chart-batch-dialog {
        position: absolute;
        top: 8px;
        left: 50%;
        transform: translateX(-50%);
        width: min(920px, calc(100% - 16px));
        max-height: calc(100% - 16px);
        overflow: auto;
        pointer-events: auto;
        border: 1px solid rgba(168, 85, 247, 0.62);
        border-radius: 14px;
        background: rgba(5, 11, 20, 0.985);
        color: #e5e7eb;
        color-scheme: dark;
        box-shadow: 0 22px 62px rgba(0,0,0,.62);
      }
      .gpt-fx-chart-batch-header {
        position: sticky;
        top: 0;
        z-index: 5;
        display: flex;
        align-items: flex-start;
        justify-content: space-between;
        gap: 14px;
        padding: 12px 14px;
        border-bottom: 1px solid rgba(168, 85, 247, 0.28);
        background: rgba(5, 11, 20, 0.99);
      }
      .gpt-fx-chart-batch-title { margin: 0; color: #faf5ff; font-size: 16px; font-weight: 900; }
      .gpt-fx-chart-batch-subtitle { margin-top: 4px; color: #cbd5e1; font-size: 11px; line-height: 1.45; }
      .gpt-fx-chart-batch-actions { display: flex; flex-wrap: wrap; justify-content: flex-end; gap: 7px; }
      .gpt-fx-chart-batch-body { display: grid; gap: 12px; padding: 12px 14px 16px; }
      .gpt-fx-chart-batch-live-stack {
        position: sticky;
        top: 68px;
        z-index: 4;
        display: grid;
        gap: 7px;
        padding: 9px;
        border: 1px solid rgba(34, 211, 238, 0.42);
        border-radius: 12px;
        background: rgba(3, 12, 23, 0.97);
        box-shadow: 0 10px 30px rgba(0,0,0,.38);
      }
      .gpt-fx-chart-batch-pnl-board {
        display: grid;
        grid-template-columns: repeat(5, minmax(0, 1fr));
        gap: 7px;
      }
      .gpt-fx-chart-batch-pnl-card { min-width: 0; padding: 7px 8px; border-radius: 9px; background: rgba(15,23,42,.88); border: 1px solid rgba(148,163,184,.18); }
      .gpt-fx-chart-batch-pnl-label { color: #94a3b8; font-size: 9px; font-weight: 800; letter-spacing: .04em; text-transform: uppercase; }
      .gpt-fx-chart-batch-pnl-value { margin-top: 3px; color: #f8fafc; font-size: 15px; font-weight: 900; line-height: 1.2; overflow-wrap: anywhere; }
      .gpt-fx-chart-batch-pnl-value.is-positive { color: #86efac; }
      .gpt-fx-chart-batch-pnl-value.is-negative { color: #fca5a5; }
      .gpt-fx-chart-batch-metric-board { display: grid; grid-template-columns: repeat(9, minmax(0, 1fr)); gap: 6px; }
      .gpt-fx-chart-batch-metric-card { min-width: 0; padding: 6px 7px; border-radius: 8px; background: rgba(15,23,42,.72); border: 1px solid rgba(148,163,184,.14); }
      .gpt-fx-chart-batch-metric-label { color: #94a3b8; font-size: 8px; font-weight: 800; letter-spacing: .03em; }
      .gpt-fx-chart-batch-metric-value { margin-top: 2px; color: #f8fafc; font-size: 13px; font-weight: 900; }
      .gpt-fx-chart-batch-metric-value.is-positive { color: #86efac; }
      .gpt-fx-chart-batch-metric-value.is-negative { color: #fca5a5; }
      .gpt-fx-chart-batch-lane-live { display: grid; gap: 2px; color: #cbd5e1; font-size: 9px; line-height: 1.35; }
      .gpt-fx-chart-batch-persist-errors { margin-top: 6px; color: #fca5a5; }
      .gpt-fx-chart-batch-persist-errors summary { cursor: pointer; font-weight: 800; }
      .gpt-fx-chart-batch-persist-errors ul { margin: 5px 0 0; padding-left: 18px; }
      .gpt-fx-chart-batch-section { padding: 10px; border: 1px solid rgba(148,163,184,.20); border-radius: 11px; background: #07111f; }
      .gpt-fx-chart-batch-section-title { margin: 0 0 8px; color: #f8fafc; font-size: 12px; font-weight: 900; }
      .gpt-fx-chart-batch-datasets { display: grid; gap: 6px; max-height: 150px; overflow: auto; }
      .gpt-fx-chart-batch-dataset { display: flex; align-items: flex-start; gap: 8px; padding: 7px 8px; border-radius: 8px; background: rgba(15,23,42,.72); font-size: 11px; line-height: 1.4; }
      .gpt-fx-chart-batch-dataset input { margin-top: 2px; }
      .gpt-fx-chart-batch-controls { display: flex; flex-wrap: wrap; align-items: center; gap: 8px; }
      .gpt-fx-chart-batch-input, .gpt-fx-chart-batch-select {
        box-sizing: border-box;
        min-width: 170px;
        border: 1px solid rgba(168, 85, 247, 0.42);
        border-radius: 8px;
        background: #020617;
        color: #f8fafc;
        padding: 7px 8px;
        font-size: 11px;
      }
      .gpt-fx-chart-batch-progress-track { height: 9px; overflow: hidden; border-radius: 999px; background: rgba(30,41,59,.92); }
      .gpt-fx-chart-batch-progress-bar { height: 100%; width: 0; border-radius: inherit; background: linear-gradient(90deg, #22d3ee, #a855f7); transition: width .12s linear; }
      .gpt-fx-chart-batch-status { margin-top: 8px; color: #cbd5e1; font-size: 11px; line-height: 1.5; overflow-wrap: anywhere; }
      .gpt-fx-chart-batch-table-wrap { overflow: auto; max-height: 270px; }
      .gpt-fx-chart-batch-table { width: 100%; border-collapse: collapse; font-size: 10px; color: #e5e7eb; }
      .gpt-fx-chart-batch-table th, .gpt-fx-chart-batch-table td { padding: 6px 7px; border-bottom: 1px solid rgba(148,163,184,.15); text-align: left; white-space: nowrap; }
      .gpt-fx-chart-batch-table th { position: sticky; top: 0; background: #0f172a; color: #f8fafc; z-index: 1; }
      .gpt-fx-chart-batch-note { color: #94a3b8; font-size: 10px; line-height: 1.45; }
      @media (max-width: 820px) {
        .gpt-fx-chart-batch-pnl-board { grid-template-columns: repeat(2, minmax(0, 1fr)); }
        .gpt-fx-chart-batch-metric-board { grid-template-columns: repeat(3, minmax(0, 1fr)); }
      }
      .gpt-fx-chart-run-overlay {
        position: absolute;
        inset: 12px 16px 6px;
        z-index: 30;
        display: none;
        pointer-events: none;
      }
      .gpt-fx-chart-run-overlay.is-open { display: block; }
      .gpt-fx-chart-run-dialog {
        position: absolute;
        width: min(760px, calc(100% - 16px));
        min-width: min(440px, calc(100% - 16px));
        max-width: calc(100% - 16px);
        max-height: calc(100% - 16px);
        overflow: auto;
        pointer-events: auto;
        border: 1px solid rgba(56, 189, 248, 0.58);
        border-radius: 14px;
        background: rgba(5, 11, 20, 0.97);
        color: #e5e7eb;
        color-scheme: dark;
        box-shadow: 0 18px 52px rgba(0,0,0,.58);
      }
      .gpt-fx-chart-run-resize-handle {
        position: absolute;
        top: 0;
        bottom: 0;
        left: 0;
        z-index: 3;
        width: 12px;
        cursor: ew-resize;
        touch-action: none;
      }
      .gpt-fx-chart-run-resize-handle::after {
        content: '';
        position: absolute;
        top: 42%;
        bottom: 42%;
        left: 4px;
        width: 2px;
        min-height: 40px;
        border-radius: 999px;
        background: rgba(103, 232, 249, 0.72);
        box-shadow: 0 0 10px rgba(34, 211, 238, 0.35);
      }
      .gpt-fx-chart-run-header {
        position: sticky;
        top: 0;
        z-index: 4;
        display: flex;
        align-items: flex-start;
        justify-content: space-between;
        gap: 16px;
        padding: 12px 14px 10px 20px;
        border-bottom: 1px solid rgba(56, 189, 248, 0.24);
        background: rgba(5, 11, 20, 0.985);
        cursor: move;
        user-select: none;
        touch-action: none;
      }
      .gpt-fx-chart-run-header button,
      .gpt-fx-chart-run-header input,
      .gpt-fx-chart-run-header select,
      .gpt-fx-chart-run-header textarea { cursor: pointer; user-select: auto; }
      .gpt-fx-chart-run-header-actions { display: flex; gap: 7px; flex-wrap: wrap; justify-content: flex-end; }
      .gpt-fx-chart-run-title { margin: 0; color: #f8fafc; font-size: 16px; font-weight: 900; }
      .gpt-fx-chart-run-subtitle { margin-top: 4px; color: #cbd5e1; font-size: 11px; line-height: 1.45; }
      .gpt-fx-chart-run-body { display: grid; gap: 12px; padding: 13px 17px 16px; }
      .gpt-fx-chart-run-summary-grid {
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 8px;
      }
      .gpt-fx-chart-run-summary-card {
        min-width: 0;
        padding: 8px 10px;
        border: 1px solid rgba(148, 163, 184, 0.22);
        border-radius: 10px;
        background: #07111f;
      }
      .gpt-fx-chart-run-label { color: #e2e8f0; font-size: 10px; font-weight: 800; text-transform: uppercase; letter-spacing: .04em; }
      .gpt-fx-chart-run-value { margin-top: 3px; color: #f8fafc; font-size: 11px; line-height: 1.42; word-break: break-all; }
      .gpt-fx-chart-run-table { width: 100%; border-collapse: collapse; font-size: 11px; background: #050b14 !important; color: #e5e7eb !important; }
      .gpt-fx-chart-run-table thead,
      .gpt-fx-chart-run-table tbody,
      .gpt-fx-chart-run-table tr,
      .gpt-fx-chart-run-table tr:nth-child(odd),
      .gpt-fx-chart-run-table tr:nth-child(even),
      .gpt-fx-chart-run-table th,
      .gpt-fx-chart-run-table td {
        background: #07111f !important;
        color: #e5e7eb !important;
      }
      .gpt-fx-chart-run-table th,
      .gpt-fx-chart-run-table td { padding: 7px 8px; border-bottom: 1px solid rgba(148, 163, 184, 0.16); text-align: left; vertical-align: middle; }
      .gpt-fx-chart-run-table th { color: #f8fafc !important; font-weight: 800; }
      .gpt-fx-chart-run-table td:first-child { color: #f8fafc !important; font-weight: 900; }
      .gpt-fx-chart-run-confirm-input {
        width: 78px;
        box-sizing: border-box;
        border: 1px solid rgba(125, 211, 252, 0.42);
        border-radius: 8px;
        background: #020617 !important;
        color: #f8fafc !important;
        padding: 6px 8px;
        font-size: 12px;
      }
      .gpt-fx-chart-run-status {
        padding: 8px 10px;
        border-radius: 10px;
        border: 1px solid rgba(34, 197, 94, 0.32);
        background: rgba(22, 101, 52, 0.18);
        color: #bbf7d0;
        font-size: 11px;
        line-height: 1.45;
      }
      .gpt-fx-chart-run-status.is-error {
        border-color: rgba(248, 113, 113, 0.42);
        background: rgba(127, 29, 29, 0.24);
        color: #fecaca;
      }
      .gpt-fx-chart-run-errors { margin: 5px 0 0 18px; padding: 0; }
      .gpt-fx-chart-run-actions { display: flex; justify-content: flex-end; gap: 8px; flex-wrap: wrap; }
      .gpt-fx-chart-run-preview {
        max-height: 210px;
        overflow: auto;
        margin: 0;
        padding: 9px 10px;
        border-radius: 10px;
        background: rgba(2, 6, 23, 0.62);
        color: #cbd5e1;
        font: 10px/1.45 ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
        white-space: pre-wrap;
        word-break: break-word;
      }
      .gpt-fx-chart-sync-status {
        padding: 8px 10px;
        border: 1px solid rgba(56, 189, 248, 0.34);
        border-radius: 10px;
        background: #07111f;
        color: #f8fafc;
        font-size: 11px;
        line-height: 1.45;
      }
      .gpt-fx-chart-sync-status.is-error {
        border-color: rgba(248, 113, 113, 0.56);
        color: #fecaca;
      }
      .gpt-fx-chart-sync-note { color: #cbd5e1; font-size: 10px; }
      .gpt-fx-chart-trend-up { color: #86efac !important; font-weight: 900; }
      .gpt-fx-chart-trend-down { color: #fca5a5 !important; font-weight: 900; }
      .gpt-fx-chart-trend-watch { color: #fde68a !important; font-weight: 900; }
      .gpt-fx-chart-trend-neutral { color: #cbd5e1 !important; font-weight: 800; }
      .gpt-fx-chart-cycle-early { color: #86efac !important; font-weight: 900; }
      .gpt-fx-chart-cycle-middle { color: #7dd3fc !important; font-weight: 900; }
      .gpt-fx-chart-cycle-late { color: #fca5a5 !important; font-weight: 900; }
      .gpt-fx-chart-cycle-neutral { color: #cbd5e1 !important; font-weight: 800; }
      .gpt-fx-chart-decision-allow { color: #86efac !important; font-weight: 900; }
      .gpt-fx-chart-decision-conditional { color: #7dd3fc !important; font-weight: 900; }
      .gpt-fx-chart-decision-wait { color: #fde68a !important; font-weight: 900; }
      .gpt-fx-chart-decision-blocked { color: #fca5a5 !important; font-weight: 900; }
      .gpt-fx-chart-decision-neutral { color: #cbd5e1 !important; font-weight: 800; }
      .gpt-fx-chart-replay-grid {
        display: grid;
        grid-template-columns: minmax(0, 1.15fr) minmax(280px, .85fr);
        gap: 10px;
      }
      .gpt-fx-chart-replay-controls {
        display: grid;
        grid-template-columns: auto minmax(120px, 1fr) auto;
        align-items: center;
        gap: 8px;
        padding: 8px 10px;
        border: 1px solid rgba(56, 189, 248, 0.28);
        border-radius: 10px;
        background: #07111f;
      }
      .gpt-fx-chart-replay-range { width: 100%; accent-color: #22d3ee; }
      .gpt-fx-chart-replay-panel {
        min-width: 0;
        padding: 9px 10px;
        border: 1px solid rgba(148, 163, 184, 0.22);
        border-radius: 10px;
        background: #07111f;
      }
      .gpt-fx-chart-replay-title { color: #a5f3fc; font-size: 11px; font-weight: 900; }
      .gpt-fx-chart-replay-meta { margin-top: 3px; color: #cbd5e1; font-size: 10px; line-height: 1.45; }
      .gpt-fx-chart-replay-chain { margin: 6px 0 0 17px; padding: 0; color: #e2e8f0; font-size: 10px; line-height: 1.5; }
      .gpt-fx-chart-replay-event-btn {
        border: 1px solid rgba(56, 189, 248, 0.32);
        border-radius: 7px;
        background: rgba(8, 47, 73, 0.48);
        color: #bae6fd;
        padding: 3px 7px;
        font-size: 10px;
        cursor: pointer;
      }
      .gpt-fx-chart-replay-event-btn:hover { background: rgba(14, 116, 144, 0.62); }
      .gpt-fx-chart-trace-observation { color: #a5f3fc !important; font-weight: 800; }
      .gpt-fx-chart-trace-state { color: #c4b5fd !important; font-weight: 800; }
      .gpt-fx-chart-trace-decision { color: #fde68a !important; font-weight: 800; }
      .gpt-fx-chart-trace-execution { color: #86efac !important; font-weight: 900; }
      .gpt-fx-chart-sync-ok { color: #bbf7d0 !important; font-weight: 800; }
      .gpt-fx-chart-sync-warn { color: #fde68a !important; font-weight: 800; }
      .gpt-fx-chart-sync-error { color: #fecaca !important; font-weight: 800; }
      @media (max-width: 760px) {
        .gpt-fx-chart-run-summary-grid, .gpt-fx-chart-replay-grid { grid-template-columns: 1fr; }
      }
      .gpt-fx-chart-comment-title {
        margin: 0 0 4px;
        font-size: 12px;
        font-weight: 800;
        color: #fef3c7;
      }
      .gpt-fx-chart-comment-meta {
        margin: 0 0 7px;
        color: #94a3b8;
        font-size: 11px;
        line-height: 1.35;
      }
      .gpt-fx-chart-comment-text {
        margin: 0 0 8px;
        color: #e5e7eb;
        font-size: 12px;
        line-height: 1.45;
        white-space: pre-wrap;
        word-break: break-word;
      }
      .gpt-fx-chart-comment-form {
        display: grid;
        gap: 7px;
      }
      .gpt-fx-chart-comment-input,
      .gpt-fx-chart-comment-select,
      .gpt-fx-chart-comment-textarea {
        width: 100%;
        box-sizing: border-box;
        border: 1px solid rgba(148, 163, 184, 0.36);
        border-radius: 9px;
        background: rgba(2, 6, 23, 0.64);
        color: #e5e7eb;
        padding: 6px 8px;
        font-size: 12px;
      }
      .gpt-fx-chart-comment-textarea {
        min-height: 72px;
        resize: vertical;
        line-height: 1.45;
      }
      .gpt-fx-chart-comment-buttons {
        display: flex;
        flex-wrap: wrap;
        gap: 6px;
        justify-content: flex-end;
      }
      .gpt-fx-chart-comment-mini-btn {
        border: 1px solid rgba(148, 163, 184, 0.34);
        border-radius: 999px;
        background: rgba(30, 41, 59, 0.82);
        color: #e5e7eb;
        padding: 5px 9px;
        font-size: 11px;
        cursor: pointer;
      }
      .gpt-fx-chart-comment-mini-btn:hover { background: rgba(51, 65, 85, 0.96); }
      .gpt-fx-chart-comment-mini-btn.is-danger {
        border-color: rgba(248, 113, 113, 0.58);
        color: #fecaca;
      }
      .gpt-fx-chart-text-label-popover {
        position: absolute;
        z-index: 4;
        min-width: 240px;
        max-width: min(380px, calc(100% - 32px));
        padding: 10px 11px;
        border: 1px solid rgba(250, 204, 21, 0.48);
        border-radius: 12px;
        background: rgba(15, 23, 42, 0.97);
        color: #e5e7eb;
        box-shadow: 0 18px 44px rgba(0,0,0,.42);
        opacity: 0;
        pointer-events: none;
        transform: translate(8px, calc(-100% - 10px));
        transition: opacity .08s ease;
      }
      .gpt-fx-chart-text-label-popover.is-open {
        opacity: 1;
        pointer-events: auto;
      }
      .gpt-fx-chart-text-label-popover.is-below {
        transform: translate(8px, 10px);
      }

      .gpt-fx-chart-dialog-backdrop {
        position: fixed;
        inset: 0;
        z-index: 2147483400;
        display: none;
        place-items: center;
        padding: 18px;
        background: rgba(15, 23, 42, 0.34);
        backdrop-filter: blur(2px);
      }
      .gpt-fx-chart-dialog-backdrop.is-open { display: grid; }
      .gpt-fx-chart-dialog-panel {
        width: min(520px, calc(100vw - 36px));
        max-height: min(78vh, 640px);
        overflow: auto;
        border: 1px solid rgba(250, 204, 21, 0.34);
        border-radius: 18px;
        background: rgba(15, 23, 42, 0.98);
        color: #e5e7eb;
        box-shadow: 0 26px 80px rgba(0,0,0,.44);
        padding: 18px;
        display: grid;
        gap: 12px;
      }
      .gpt-fx-chart-dialog-title {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 15px;
        font-weight: 900;
        line-height: 1.45;
        color: #fef3c7;
      }
      .gpt-fx-chart-dialog-title::before { content: "⚠"; color: #fb7185; }
      .gpt-fx-chart-dialog-message {
        font-size: 13px;
        line-height: 1.7;
        color: #e5e7eb;
        white-space: pre-wrap;
        word-break: break-word;
      }
      .gpt-fx-chart-dialog-detail {
        border: 1px solid rgba(148, 163, 184, 0.28);
        border-radius: 12px;
        padding: 10px 11px;
        background: rgba(2, 6, 23, 0.58);
        color: #cbd5e1;
        font-size: 12px;
        line-height: 1.65;
        white-space: pre-wrap;
        word-break: break-word;
        max-height: 180px;
        overflow: auto;
      }
      .gpt-fx-chart-dialog-actions {
        display: flex;
        justify-content: flex-end;
        gap: 10px;
        flex-wrap: wrap;
      }
      .gpt-fx-chart-dialog-actions button {
        min-width: 92px;
        border: 0;
        border-radius: 999px;
        padding: 9px 16px;
        font-size: 13px;
        font-weight: 900;
        cursor: pointer;
      }
      .gpt-fx-chart-dialog-actions [data-action="cancel"] {
        background: rgba(226, 232, 240, 0.96);
        color: #0f172a;
      }
      .gpt-fx-chart-dialog-actions [data-action="ok"] {
        background: linear-gradient(135deg, #ef4444, #f97316);
        color: #fff;
      }
      .gpt-fx-chart-context-menu {
        position: absolute;
        z-index: 5;
        min-width: 210px;
        padding: 8px;
        border: 1px solid rgba(250, 204, 21, 0.44);
        border-radius: 12px;
        background: rgba(15, 23, 42, 0.97);
        color: #e5e7eb;
        box-shadow: 0 18px 44px rgba(0,0,0,.42);
        opacity: 0;
        pointer-events: none;
        transform: translate(8px, -8px);
      }
      .gpt-fx-chart-context-menu.is-open {
        opacity: 1;
        pointer-events: auto;
      }
      .gpt-fx-chart-context-menu-title {
        color: #fef3c7;
        font-size: 12px;
        font-weight: 800;
        margin: 0 0 4px;
      }
      .gpt-fx-chart-context-menu-meta {
        color: #94a3b8;
        font-size: 11px;
        line-height: 1.35;
        margin: 0 0 8px;
      }
      .gpt-fx-chart-context-menu-actions {
        display: grid;
        gap: 6px;
      }
      .gpt-fx-chart-context-menu-btn {
        width: 100%;
        border: 1px solid rgba(148, 163, 184, 0.34);
        border-radius: 999px;
        background: rgba(30, 41, 59, 0.84);
        color: #e5e7eb;
        padding: 6px 10px;
        font-size: 12px;
        text-align: left;
        cursor: pointer;
      }
      .gpt-fx-chart-context-menu-btn:hover { background: rgba(51, 65, 85, 0.96); }
      .gpt-fx-chart-context-menu-btn.is-danger {
        border-color: rgba(248, 113, 113, 0.58);
        color: #fecaca;
      }
      .gpt-fx-chart-footer {
        display: flex;
        gap: 12px;
        align-items: center;
        justify-content: space-between;
        padding: 9px 18px 13px;
        color: #94a3b8;
        font-size: 12px;
        border-top: 1px solid rgba(148, 163, 184, 0.15);
      }
      .gpt-fx-chart-legend {
        display: flex;
        flex-wrap: wrap;
        gap: 12px;
        align-items: center;
      }
      .gpt-fx-chart-legend-item { display: inline-flex; align-items: center; gap: 6px; }
      .gpt-fx-chart-swatch { width: 18px; height: 3px; border-radius: 999px; display: inline-block; }
    `;
    document.head.appendChild(style);
  }

  function getPath(obj, path) {
    const clean = String(path ?? '').trim().replace(/^\$\.?/, '');
    if (!clean) return obj;
    return clean.split('.').reduce((cur, key) => cur == null ? undefined : cur[key], obj);
  }

  function numberOrNull(value) {
    if (value == null) return null;
    if (typeof value === 'string' && value.trim() === '') return null;
    const n = Number(value);
    return Number.isFinite(n) ? n : null;
  }

  function round3(value) {
    const n = numberOrNull(value);
    return n == null ? '' : n.toFixed(3);
  }

  function ensureCrosshairState(state) {
    if (!state.crosshair || typeof state.crosshair !== 'object') {
      state.crosshair = {
        visible: false,
        locked: false,
        panelKind: '',
        timeMs: null,
        rowIndex: null,
        price: null
      };
    }
    return state.crosshair;
  }

  function setCrosshairFromPanelPoint(state, panel, idx, py, locked = false) {
    if (!state || !panel || idx == null || !panel.rows?.[idx]) return false;
    const row = panel.rows[idx];
    const timeMs = panelRowTimeMs(row);
    if (timeMs == null) return false;
    const ratio = Math.max(0, Math.min(1, (py - panel.pad.top) / Math.max(1, panel.plotH)));
    const price = panel.max - ratio * (panel.max - panel.min);
    state.crosshair = {
      visible: true,
      locked: locked === true,
      panelKind: panel.rect.kind,
      timeMs,
      rowIndex: idx,
      price
    };
    state.hoverTimeMs = timeMs;
    return true;
  }

  function crosshairCanRender(crosshair) {
    return Boolean(
      crosshair?.visible === true
      && crosshair.panelKind
      && numberOrNull(crosshair.timeMs) != null
      && numberOrNull(crosshair.price) != null
    );
  }

  function drawCrosshairForPanel(ctx, options) {
    const { state, panelKind, rows, x, y, min, max, pad, rect } = options || {};
    const crosshair = ensureCrosshairState(state);
    if (!crosshairCanRender(crosshair) || !Array.isArray(rows) || !rows.length) return;

    const isSourcePanel = crosshair.panelKind === panelKind;
    let idx = isSourcePanel && Number.isInteger(crosshair.rowIndex) ? crosshair.rowIndex : null;
    if (idx == null || !rows[idx] || Math.abs(Number(panelRowTimeMs(rows[idx])) - Number(crosshair.timeMs)) > 1) {
      idx = findIndexForTime(rows, crosshair.timeMs);
    }
    if (idx == null || !rows[idx]) return;

    const price = numberOrNull(crosshair.price);
    const priceInRange = price != null && price >= min && price <= max;
    const xx = x(idx);
    const yy = priceInRange ? y(price) : null;
    if (!Number.isFinite(xx) || (yy != null && !Number.isFinite(yy))) return;

    const locked = crosshair.locked === true;
    const syncedOpacity = isSourcePanel ? 1 : 0.72;
    const lineColor = locked
      ? `rgba(34, 211, 238, ${0.96 * syncedOpacity})`
      : `rgba(226, 232, 240, ${0.80 * syncedOpacity})`;
    const labelBorder = locked
      ? `rgba(34, 211, 238, ${0.92 * syncedOpacity})`
      : `rgba(148, 163, 184, ${0.86 * syncedOpacity})`;
    const labelBg = locked
      ? `rgba(8, 47, 73, ${0.98 * syncedOpacity})`
      : `rgba(15, 23, 42, ${0.98 * syncedOpacity})`;

    ctx.save();
    ctx.strokeStyle = lineColor;
    ctx.lineWidth = locked ? (isSourcePanel ? 1.35 : 1.1) : (isSourcePanel ? 1.0 : 0.9);
    ctx.setLineDash(locked ? [] : [4, 4]);
    ctx.beginPath();
    ctx.moveTo(xx, pad.top);
    ctx.lineTo(xx, pad.bottom);
    if (yy != null) {
      ctx.moveTo(pad.left, yy);
      ctx.lineTo(pad.right, yy);
    }
    ctx.stroke();
    ctx.setLineDash([]);

    ctx.font = '700 11px system-ui, sans-serif';
    ctx.textBaseline = 'middle';

    const row = rows[idx] || {};
    const timeTextBase = formatRowDateTime(crosshair.timeMs) || row.datetime || '-';
    const timeText = locked ? `固定 ${timeTextBase}` : timeTextBase;
    const timePadX = 7;
    const timeHeight = 21;
    const timeWidth = Math.ceil(ctx.measureText(timeText).width) + timePadX * 2;
    const timeX = Math.max(pad.left, Math.min(pad.right - timeWidth, xx - timeWidth / 2));
    const timeY = pad.bottom + 3;
    ctx.fillStyle = labelBg;
    ctx.strokeStyle = labelBorder;
    ctx.lineWidth = 1;
    ctx.fillRect(timeX, timeY, timeWidth, timeHeight);
    ctx.strokeRect(timeX + 0.5, timeY + 0.5, timeWidth - 1, timeHeight - 1);
    ctx.fillStyle = '#f8fafc';
    ctx.textAlign = 'center';
    ctx.fillText(timeText, timeX + timeWidth / 2, timeY + timeHeight / 2 + 0.5);

    if (yy != null) {
      const priceText = Number(price).toFixed(3);
      const pricePadX = 7;
      const priceHeight = 21;
      const priceWidth = Math.max(58, Math.ceil(ctx.measureText(priceText).width) + pricePadX * 2);
      const rectRight = numberOrNull(rect?.x) != null && numberOrNull(rect?.w) != null
        ? rect.x + rect.w
        : pad.right + 42;
      const priceX = Math.max(pad.left, rectRight - priceWidth - 4);
      const priceY = Math.max(pad.top, Math.min(pad.bottom - priceHeight, yy - priceHeight / 2));
      ctx.fillStyle = labelBg;
      ctx.strokeStyle = labelBorder;
      ctx.fillRect(priceX, priceY, priceWidth, priceHeight);
      ctx.strokeRect(priceX + 0.5, priceY + 0.5, priceWidth - 1, priceHeight - 1);
      ctx.fillStyle = '#f8fafc';
      ctx.textAlign = 'center';
      ctx.fillText(priceText, priceX + priceWidth / 2, priceY + priceHeight / 2 + 0.5);
    }
    ctx.restore();
  }

  function normalizeRows(source) {
    const rows = getPath(source, '$.display_sets.chart_latest_1000')
      || getPath(source, '$.display_sets.chart_ready_points')
      || getPath(source, '$.bars')
      || [];
    return Array.isArray(rows) ? rows.filter(row => numberOrNull(row?.close) != null) : [];
  }

  function normalizeAllRows(source) {
    const rows = getPath(source, '$.bars') || normalizeRows(source) || [];
    return Array.isArray(rows) ? rows.filter(row => numberOrNull(row?.close) != null) : [];
  }

  function getBollingerSettings(source) {
    const raw = source?.indicator_settings?.bollinger
      || source?.indicator_settings?.bollinger_bands
      || source?.indicator_settings?.bands
      || {};
    const period = Math.max(2, Math.floor(numberOrNull(raw.periods ?? raw.period ?? raw.bands_period ?? 20) ?? 20));
    const deviations = Math.max(0.1, numberOrNull(raw.deviations ?? raw.deviation ?? raw.bands_deviations ?? 2.0) ?? 2.0);
    const shift = Math.floor(numberOrNull(raw.shift ?? raw.bands_shift ?? 0) ?? 0);
    const sourceField = String(raw.source ?? raw.applied_price ?? 'close').trim() || 'close';
    return {
      period,
      deviations,
      shift,
      source: sourceField,
      method: raw.method || 'SMA + standard deviation',
      note: 'Bollinger Bandsは観測補助の表示系列であり、Dow材料点抽出には使わない。'
    };
  }

  function rowIdentity(row) {
    return String(row?.row_no ?? row?.datetime ?? [row?.date, row?.time].filter(Boolean).join(' ') ?? '');
  }

  function buildBollingerBands(source, chartRows, settings = getBollingerSettings(source)) {
    const allRows = normalizeAllRows(source);
    const byKey = new Map();
    const values = allRows.map(row => numberOrNull(row?.[settings.source]) ?? numberOrNull(row?.close));
    const period = settings.period;
    const dev = settings.deviations;
    for (let i = 0; i < allRows.length; i++) {
      if (i < period - 1) continue;
      let sum = 0;
      let valid = true;
      for (let j = i - period + 1; j <= i; j++) {
        const n = values[j];
        if (n == null) { valid = false; break; }
        sum += n;
      }
      if (!valid) continue;
      const middle = sum / period;
      let variance = 0;
      for (let j = i - period + 1; j <= i; j++) {
        const d = values[j] - middle;
        variance += d * d;
      }
      const sd = Math.sqrt(variance / period);
      const targetIndex = i + settings.shift;
      const targetRow = allRows[targetIndex];
      if (!targetRow) continue;
      byKey.set(rowIdentity(targetRow), {
        upper: middle + dev * sd,
        middle,
        lower: middle - dev * sd,
        width: dev * sd * 2
      });
    }
    return chartRows.map(row => byKey.get(rowIdentity(row)) || null);
  }

  function paramValue(params, names) {
    for (const name of names) {
      if (params instanceof URLSearchParams && params.has(name)) return params.get(name);
      if (params && typeof params === 'object' && Object.prototype.hasOwnProperty.call(params, name)) return params[name];
    }
    return null;
  }

  function boolFromParam(value, fallback) {
    if (value == null || value === '') return fallback;
    const v = String(value).trim().toLowerCase();
    if (['1', 'true', 'yes', 'on', 'y'].includes(v)) return true;
    if (['0', 'false', 'no', 'off', 'n'].includes(v)) return false;
    return fallback;
  }

  function viewModeFromParam(value, fallback = 'all') {
    const v = String(value ?? '').trim().toLowerCase();
    if (!v) return fallback;
    if (['basis', 'basis_only', 'basisonly'].includes(v)) return 'basis_only';
    if (['history', 'basis_history', 'basis+history', 'basis_history_only'].includes(v)) return 'basis_history';
    if (['all', 'full', 'debug'].includes(v)) return 'all';
    return fallback;
  }

  function normalizePanelTimeframe(value, fallback = 'M5') {
    const v = String(value ?? '').trim().toUpperCase().replace(/\s+/g, '');
    if (['WEEK', 'W1', '1W', 'WEEKLY', '10080', 'M10080'].includes(v)) return 'WEEK';
    if (['DAY', 'D1', '1D', 'DAILY', '1440', 'M1440'].includes(v)) return 'DAY';
    if (['H4', '4H', '240', 'M240'].includes(v)) return 'H4';
    if (['H1', '1H', '60', 'M60'].includes(v)) return 'H1';
    if (['M5', '5M', '5', 'M05', 'LOWER'].includes(v)) return 'M5';
    return fallback;
  }

  function normalizeUpperTimeframe(value) {
    const tf = normalizePanelTimeframe(value, 'H1');
    return tf === 'M5' ? 'H1' : tf;
  }

  function normalizeUpperDisplayMode(value) {
    const v = String(value ?? '').trim().toUpperCase().replace(/\s+/g, '');
    if (['BOTH', 'H1H4', 'H1+H4', 'H1/H4', 'H1,H4', 'ALLUPPER', 'UPPERBOTH'].includes(v)) return 'BOTH';
    return normalizeUpperTimeframe(value);
  }

  function normalizeChartLayout(value) {
    const v = String(value ?? '').trim().toUpperCase().replace(/[\s_\-\/]+/g, '');
    if (['ENTRY', 'M5', 'M5ENTRY', 'M5H1H4', 'LOWERENTRY', 'LEGACY', 'DEFAULT'].includes(v)) return 'M5_ENTRY';
    if (['EXPANSION', 'EXPANSIONREVIEW', 'H4FOCUS', 'H4DAYH1', 'DAYH4H1', 'H4DAYWEEK', 'DAYH4WEEK', 'H4CONTEXT', 'EXPANSIONWINDOWSET'].includes(v)) return 'EXPANSION_REVIEW';
    return 'EXPANSION_REVIEW';
  }

  function chartLayoutLabel(state) {
    return normalizeChartLayout(state?.chartLayout) === 'M5_ENTRY'
      ? 'M5 Entry Layout'
      : 'Expansion Review Layout';
  }

  function isExpansionReviewLayout(state) {
    return normalizeChartLayout(state?.chartLayout) === 'EXPANSION_REVIEW';
  }

  function isUpperBothMode(state) {
    return normalizeUpperDisplayMode(state?.upperTimeframe) === 'BOTH';
  }

  function isUpperPanelKind(panelKind) {
    return ['upper', 'h1', 'h4', 'day', 'd1', 'week', 'w1'].includes(String(panelKind || '').toLowerCase());
  }

  function panelKindToTimeframe(panelKind, state) {
    const kind = String(panelKind || '').toLowerCase();
    if (kind === 'm5' || kind === 'lower') return 'M5';
    if (kind === 'h1') return 'H1';
    if (kind === 'h4') return 'H4';
    if (kind === 'week' || kind === 'w1') return 'WEEK';
    if (kind === 'day' || kind === 'd1') return 'DAY';
    if (kind === 'upper') return normalizeUpperTimeframe(state?.upperTimeframe);
    return 'M5';
  }

  function panelTimeframeLabel(panel, state) {
    if (!panel) return 'M5';
    if (panel.rect?.timeframe) return normalizePanelTimeframe(panel.rect.timeframe, String(panel.rect.timeframe).toUpperCase());
    return panelKindToTimeframe(panel.rect?.kind, state);
  }

  function panelRank(label) {
    const v = normalizePanelTimeframe(label, String(label || '').toUpperCase());
    if (v === 'WEEK') return 5;
    if (v === 'DAY') return 4;
    if (v === 'H4') return 3;
    if (v === 'H1') return 2;
    if (v === 'M5' || v === 'LOWER') return 1;
    return 0;
  }

  function shouldRenderHsiOnPanel(annotationPanel, panelKind, state) {
    const rawSourcePanel = String(annotationPanel || '').toUpperCase();
    const sourcePanel = rawSourcePanel === 'LOWER' ? 'M5' : normalizePanelTimeframe(rawSourcePanel, rawSourcePanel);
    const targetPanel = panelKindToTimeframe(panelKind, state);
    if (rawSourcePanel === 'UPPER') return isUpperPanelKind(panelKind);
    if (sourcePanel === targetPanel) return true;
    const sourceRank = panelRank(sourcePanel);
    const targetRank = panelRank(targetPanel);
    // 上位足に保存したHSI仮説は、同じ時刻範囲の下位足にも観測補助として降ろす。
    // 既存の H4 -> H1/M5, H1 -> M5 挙動を、DAY -> H4/H1/M5 まで自然拡張する。
    return sourceRank > 0 && targetRank > 0 && sourceRank >= targetRank;
  }

  function panelTimeframeMinutes(value) {
    const tf = normalizePanelTimeframe(value, 'M5');
    if (tf === 'WEEK') return 10080;
    if (tf === 'DAY') return 1440;
    if (tf === 'H4') return 240;
    if (tf === 'H1') return 60;
    return 5;
  }

  function upperTimeframeMinutes(value) {
    return panelTimeframeMinutes(normalizeUpperTimeframe(value));
  }

  function normalizeUpperWarmupBars(value, fallback = 30) {
    const n = Math.floor(numberOrNull(value) ?? fallback ?? 30);
    return Math.max(0, Math.min(300, n));
  }

  function chartOptionsFromLocation() {
    try {
      return chartOptionsFromParams(new URLSearchParams(location.search));
    } catch {
      return {};
    }
  }

  function chartOptionsFromParams(params) {
    const confirmRaw = paramValue(params, ['confirmBars', 'confirm_bars', 'confirm', 'bars']);
    const opts = {};
    const confirmNumber = numberOrNull(confirmRaw);
    if (confirmNumber != null) {
      opts.confirmBars = Math.max(3, Math.floor(confirmNumber));
    }
    const modeRaw = paramValue(params, ['viewMode', 'view_mode', 'chartMode', 'mode']);
    if (modeRaw) opts.viewMode = viewModeFromParam(modeRaw, undefined);
    const hlRaw = paramValue(params, ['hlRange', 'highLowRange', 'high_low_range']);
    if (hlRaw != null) opts.showHighLowRange = boolFromParam(hlRaw, true);
    const bbRaw = paramValue(params, ['bb', 'bollinger', 'showBollinger', 'bollingerBands']);
    if (bbRaw != null) opts.showBollinger = boolFromParam(bbRaw, false);
    const wideRaw = paramValue(params, ['wide', 'chartWide', 'wideMode']);
    if (wideRaw != null) opts.widthMultiplier = boolFromParam(wideRaw, false) ? 2.6 : 1;
    const windowSizeRaw = paramValue(params, ['windowSize', 'window_size', 'winSize']);
    const windowSize = numberOrNull(windowSizeRaw);
    if (windowSize != null) opts.windowSize = Math.max(10, Math.floor(windowSize));
    const windowStartRaw = paramValue(params, ['windowStart', 'window_start', 'winStart']);
    const windowStart = numberOrNull(windowStartRaw);
    if (windowStart != null) opts.windowStart = Math.max(0, Math.floor(windowStart));
    const layoutRaw = paramValue(params, ['chartLayout', 'chart_layout', 'layout', 'panelLayout', 'panel_layout']);
    if (layoutRaw != null) opts.chartLayout = normalizeChartLayout(layoutRaw);
    const upperTfRaw = paramValue(params, ['upperTf', 'upperTF', 'upper_timeframe', 'contextTf']);
    if (upperTfRaw != null) opts.upperTimeframe = normalizeUpperDisplayMode(upperTfRaw);
    const upperConfirmRaw = paramValue(params, ['upperConfirmBars', 'upper_confirm_bars', 'upperConfirm']);
    const upperConfirm = numberOrNull(upperConfirmRaw);
    if (upperConfirm != null) opts.upperConfirmBars = Math.max(3, Math.floor(upperConfirm));
    const upperWarmupRaw = paramValue(params, ['upperWarmupBars', 'upper_warmup_bars', 'upperContextBarsBefore', 'upper_context_bars_before', 'upperWarmup']);
    const upperWarmup = numberOrNull(upperWarmupRaw);
    if (upperWarmup != null) opts.upperWarmupBars = normalizeUpperWarmupBars(upperWarmup, 30);
    const upperMapDataRaw = paramValue(params, ['dayData', 'day_data', 'upperMapData', 'upper_map_data', 'upperData', 'upper_data']);
    if (upperMapDataRaw != null) opts.upperMapDataPath = normalizeUpperMapDataPath(upperMapDataRaw);
    const dayConfirmRaw = paramValue(params, ['dayConfirmBars', 'day_confirm_bars', 'dayConfirm', 'day_confirm']);
    const dayConfirm = numberOrNull(dayConfirmRaw);
    if (dayConfirm != null) opts.dayConfirmBars = Math.max(3, Math.floor(dayConfirm));

    const hsiRaw = paramValue(params, ['hsi', 'hsiValues', 'hsi_values']);
    if (hsiRaw != null) opts.hsiValuesText = String(hsiRaw);
    const hsiScaleRaw = paramValue(params, ['hsiScale', 'hsi_scale']);
    if (hsiScaleRaw != null) opts.hsiScale = numberOrNull(hsiScaleRaw);
    const hsiDirRaw = paramValue(params, ['hsiDir', 'hsiDirection', 'hsi_direction']);
    if (hsiDirRaw != null) opts.hsiDirection = normalizeHsiDirection(hsiDirRaw);
    const hsiAnchorPriceRaw = paramValue(params, ['hsiAnchorPrice', 'hsi_anchor_price']);
    const hsiAnchorIndexRaw = paramValue(params, ['hsiAnchorIndex', 'hsi_anchor_index']);
    const hsiAnchorPrice = numberOrNull(hsiAnchorPriceRaw);
    if (hsiAnchorPrice != null) {
      opts.hsiAnchor = {
        price: hsiAnchorPrice,
        index: Math.max(0, Math.floor(numberOrNull(hsiAnchorIndexRaw) ?? 0)),
        panel: String(paramValue(params, ['hsiAnchorPanel', 'hsi_anchor_panel']) || 'M5').toUpperCase(),
        timeframe: String(paramValue(params, ['hsiAnchorPanel', 'hsi_anchor_panel']) || 'M5').toUpperCase(),
        panelKind: String(paramValue(params, ['hsiAnchorPanel', 'hsi_anchor_panel']) || 'M5').toUpperCase() === 'M5' ? 'm5' : 'upper'
      };
    }
    const focusTimeRaw = paramValue(params, ['focusTime', 'focus_time', 'entryTime', 'entry_time']);
    if (focusTimeRaw != null && String(focusTimeRaw).trim()) opts.focusTime = String(focusTimeRaw).trim();
    const focusPriceRaw = paramValue(params, ['focusPrice', 'focus_price', 'entryPrice', 'entry_price']);
    const focusPrice = numberOrNull(focusPriceRaw);
    if (focusPrice != null) opts.focusPrice = focusPrice;
    const focusTradeIdRaw = paramValue(params, ['focusTradeId', 'focus_trade_id', 'tradeId', 'trade_id']);
    if (focusTradeIdRaw != null && String(focusTradeIdRaw).trim()) opts.focusTradeId = String(focusTradeIdRaw).trim();
    const focusLaneRaw = paramValue(params, ['focusLane', 'focus_lane', 'ruleLane', 'rule_lane']);
    if (focusLaneRaw != null && String(focusLaneRaw).trim()) opts.focusLane = String(focusLaneRaw).trim();
    const focusBatchDataRaw = paramValue(params, ['focusBatchData', 'focus_batch_data', 'batchData', 'batch_data']);
    const focusBatchData = validJsonParam(focusBatchDataRaw);
    if (focusBatchData) opts.focusBatchData = focusBatchData;
    const focusEntryEventIdRaw = paramValue(params, ['focusEntryEventId', 'focus_entry_event_id', 'entryEventId', 'entry_event_id']);
    if (focusEntryEventIdRaw != null && String(focusEntryEventIdRaw).trim()) opts.focusEntryEventId = String(focusEntryEventIdRaw).trim();
    const focusExitEventIdRaw = paramValue(params, ['focusExitEventId', 'focus_exit_event_id', 'exitEventId', 'exit_event_id']);
    if (focusExitEventIdRaw != null && String(focusExitEventIdRaw).trim()) opts.focusExitEventId = String(focusExitEventIdRaw).trim();
    const focusRowIdRaw = paramValue(params, ['focusRowId', 'focus_row_id', 'rowId', 'row_id']);
    if (focusRowIdRaw != null && String(focusRowIdRaw).trim()) opts.focusRowId = String(focusRowIdRaw).trim();
    const focusSideRaw = paramValue(params, ['focusSide', 'focus_side', 'side']);
    if (focusSideRaw != null && String(focusSideRaw).trim()) opts.focusSide = String(focusSideRaw).trim().toUpperCase();
    return opts;
  }

  function chartOptionsFromContext(context = {}) {
    const raw = context.launchParams || context.urlParams || {};
    return { ...chartOptionsFromLocation(), ...chartOptionsFromParams(raw), ...(context.chartOptions || {}) };
  }

  function entryChartNavigationConfig(context = {}) {
    const executeButton = context.executeButton || {};
    const raw = executeButton.chartNavigation || executeButton.chart_navigation || {};
    return {
      data: String(raw.data || raw.targetData || raw.target_data || DEFAULT_URL_DATA).trim(),
      view: String(raw.view || raw.targetView || raw.target_view || DEFAULT_URL_VIEW).trim(),
      action: String(raw.action || raw.urlAction || raw.url_action || 'fx_chart').trim(),
      timeField: String(raw.timeField || raw.time_field || 'entry_time').trim(),
      priceField: String(raw.priceField || raw.price_field || 'entry_price').trim(),
      tradeIdField: String(raw.tradeIdField || raw.trade_id_field || 'trade_id').trim(),
      laneField: String(raw.laneField || raw.lane_field || 'rule_lane').trim(),
      sideField: String(raw.sideField || raw.side_field || 'side').trim(),
      rowIdField: String(raw.rowIdField || raw.row_id_field || 'row_id').trim(),
      entryEventIdField: String(raw.entryEventIdField || raw.entry_event_id_field || 'entry_event_id').trim(),
      exitEventIdField: String(raw.exitEventIdField || raw.exit_event_id_field || 'exit_event_id').trim(),
      batchFileField: String(raw.batchFileField || raw.batch_file_field || 'source_batch_file').trim(),
      batchDataDirectory: String(raw.batchDataDirectory || raw.batch_data_directory || 'overlay/gpt_fx_lab/simulattion_集計/').trim(),
      windowSize: Math.max(10, Math.floor(numberOrNull(raw.windowSize ?? raw.window_size) ?? 1000)),
      wide: raw.wide === true,
      chartLayout: normalizeChartLayout(raw.chartLayout || raw.chart_layout || 'M5_ENTRY'),
      upperTimeframe: normalizeUpperDisplayMode(raw.upperTimeframe || raw.upper_timeframe || raw.upperTf || raw.upper_tf || 'BOTH'),
      target: String(raw.target || raw.openTarget || raw.open_target || 'new_tab').trim().toLowerCase()
    };
  }

  function entryChartRowValue(row, field) {
    if (!row || !field) return null;
    return getPath(row, field);
  }

  function entryChartSourceData(context = {}) {
    return context.sourceData
      || context.getSourceData?.()
      || (typeof window !== 'undefined' ? window.sourceData : null)
      || null;
  }

  function joinEntryChartJsonPath(directory, fileName) {
    const file = String(fileName || '').trim().replace(/\\/g, '/').replace(/^\/+/, '');
    if (!file || !file.toLowerCase().endsWith('.json')) return '';
    if (file.includes('/')) return validJsonParam(file);
    const dir = String(directory || '').trim().replace(/\\/g, '/').replace(/\/+$/, '');
    return validJsonParam(`${dir}/${file}`);
  }

  function entryChartBatchDataPath(context, config) {
    const sourceData = entryChartSourceData(context);
    const sourceBatchFile = String(getPath(sourceData, config.batchFileField) || '').trim();
    return joinEntryChartJsonPath(config.batchDataDirectory, sourceBatchFile);
  }

  function buildEntryChartNavigationUrl(row, context = {}) {
    if (!row || typeof row !== 'object') throw new Error('先にEntry成績表の行を選択してください。');
    const config = entryChartNavigationConfig(context);
    const entryTime = String(entryChartRowValue(row, config.timeField) ?? '').trim();
    const entryPrice = numberOrNull(entryChartRowValue(row, config.priceField));
    if (!entryTime) throw new Error(`選択行にEntry日時がありません: ${config.timeField}`);
    if (entryPrice == null) throw new Error(`選択行にEntry価格がありません: ${config.priceField}`);

    const url = new URL(location.href);
    const versionParam = url.searchParams.get('ver');
    url.search = '';
    if (versionParam) url.searchParams.set('ver', versionParam);
    url.searchParams.set('data', config.data);
    url.searchParams.set('view', config.view);
    url.searchParams.set('action', config.action);
    url.searchParams.set('focusTime', entryTime);
    url.searchParams.set('focusPrice', String(entryPrice));
    url.searchParams.set('windowSize', String(config.windowSize));
    url.searchParams.set('chartLayout', config.chartLayout);
    url.searchParams.set('upperTf', config.upperTimeframe);
    if (config.wide) url.searchParams.set('wide', '1');

    const tradeId = String(entryChartRowValue(row, config.tradeIdField) ?? '').trim();
    const lane = String(entryChartRowValue(row, config.laneField) ?? '').trim();
    const side = String(entryChartRowValue(row, config.sideField) ?? '').trim().toUpperCase();
    const rowId = String(entryChartRowValue(row, config.rowIdField) ?? '').trim();
    const entryEventId = String(entryChartRowValue(row, config.entryEventIdField) ?? '').trim();
    const exitEventId = String(entryChartRowValue(row, config.exitEventIdField) ?? '').trim();
    const batchData = entryChartBatchDataPath(context, config);
    if (tradeId) url.searchParams.set('focusTradeId', tradeId);
    if (lane) url.searchParams.set('focusLane', lane);
    if (side) url.searchParams.set('focusSide', side);
    if (rowId) url.searchParams.set('focusRowId', rowId);
    if (entryEventId) url.searchParams.set('focusEntryEventId', entryEventId);
    if (exitEventId) url.searchParams.set('focusExitEventId', exitEventId);
    if (batchData) url.searchParams.set('focusBatchData', batchData);
    return { url, config, entryTime, entryPrice, tradeId, lane, side, rowId, entryEventId, exitEventId, batchData };
  }

  function navigateToEntryChart(row, context = {}) {
    const navigation = buildEntryChartNavigationUrl(row, context);
    if (navigation.config.target === 'new_tab' || navigation.config.target === '_blank') {
      const opened = window.open(navigation.url.toString(), '_blank');
      if (!opened) throw new Error('チャート画面を開けませんでした。ブラウザのポップアップ設定を確認してください。');
      try { opened.opener = null; } catch { /* browser security policy */ }
    } else {
      location.href = navigation.url.toString();
    }
    return navigation;
  }

  function normalizeHsiDirection(value) {
    const v = String(value ?? '').trim().toLowerCase();
    return ['down', 'dn', '-', 'lower', 'sell'].includes(v) ? 'down' : 'up';
  }

  const COMMENT_TYPE_OPTIONS = ['note', 'dawUp', 'dawDown', 'dawNone', 'entry', 'closeOk', 'closeMiss', 'exit'];

  function normalizeCommentType(value) {
    const raw = String(value || 'note');
    if (raw === 'dawDowe') return 'dawDown';
    return COMMENT_TYPE_OPTIONS.includes(raw) ? raw : 'note';
  }

  function hsiValuesEqual(list, expected) {
    return Array.isArray(list)
      && list.length === expected.length
      && expected.every((value, index) => Math.abs((Number(list[index]) || 0) - value) < 0.000001);
  }

  function normalizeLegacyHsiValues(values) {
    const list = Array.isArray(values) ? values.filter(n => Number.isFinite(n) && n > 0).slice(0, 12) : [];
    if (hsiValuesEqual(list, [55, 89, 144, 188])) {
      return [55, 89, 144, 233];
    }
    if (hsiValuesEqual(list, [55, 89, 144, 188, 233, 305, 377])
      || hsiValuesEqual(list, [55, 89, 144, 188, 233, 305, 377, 610, 798, 987])) {
      return [55, 89, 144, 188, 233, 305, 377, 493, 610, 798, 987];
    }
    return list;
  }

  function normalizeHsiValuesText(text) {
    const values = String(text ?? '')
      .split(/[，,\s]+/)
      .map(x => Number(String(x).trim()))
      .filter(n => Number.isFinite(n) && n > 0)
      .slice(0, 12);
    return normalizeLegacyHsiValues(values).join(',');
  }

  function parseHsiValues(text) {
    const values = String(text ?? '')
      .split(/[，,\s]+/)
      .map(x => Number(String(x).trim()))
      .filter(n => Number.isFinite(n) && n > 0)
      .slice(0, 12);
    return normalizeLegacyHsiValues(values);
  }

  function formatHsiNumber(value, digits = 2) {
    const n = numberOrNull(value);
    if (n == null) return '';
    if (Math.abs(n) >= 100) return n.toFixed(0);
    if (Math.abs(n) >= 10) return n.toFixed(1);
    return n.toFixed(digits).replace(/0+$/, '').replace(/\.$/, '');
  }

  function hsiPointSize(source) {
    const raw = source?.hsi_settings?.point_size
      ?? source?.strategy_settings?.hsi?.point_size
      ?? source?.point_size;
    const explicit = numberOrNull(raw);
    if (explicit != null && explicit > 0) return explicit;
    const symbol = String(source?.symbol ?? '').toUpperCase();
    return symbol.includes('JPY') ? 0.001 : 0.0001;
  }

  function createHsiTarget(anchorPrice, raw, scale, pointSize, direction, options = {}) {
    const sign = normalizeHsiDirection(direction) === 'down' ? -1 : 1;
    const effectivePoints = raw * scale;
    const price = anchorPrice + sign * effectivePoints * pointSize;
    return {
      raw,
      scale,
      effectivePoints,
      price,
      pips: effectivePoints / 10,
      direction: normalizeHsiDirection(direction),
      sign,
      ...options
    };
  }

  function findHsiMidpointObservation(raw) {
    const value = numberOrNull(raw);
    if (value == null) return null;
    return HSI_MIDPOINT_OBSERVATIONS.find(item => Math.abs(value - item.raw) < 0.000001) || null;
  }

  function hsiRangeLabel(raw) {
    const value = numberOrNull(raw);
    if (value == null) return 'R?';
    const range = HSI_RANGE_LEVELS.find(item => Math.abs(value - item.raw) < 0.000001);
    if (range) return range.label;
    const observation = findHsiMidpointObservation(value);
    if (observation) return observation.label;
    return `R${formatHsiNumber(value, 0)}`;
  }

  function appendHsiMidpointObservationTargets(targets, anchorPrice, scale, pointSize, direction) {
    if (anchorPrice == null) return targets;
    HSI_MIDPOINT_OBSERVATIONS.forEach(observationDef => {
      const existingIndex = targets.findIndex(target => Math.abs(numberOrNull(target.raw) - observationDef.raw) < 0.000001);
      if (existingIndex >= 0) {
        targets[existingIndex] = {
          ...targets[existingIndex],
          observation: true,
          observation_key: observationDef.label,
          label: observationDef.label,
          style: 'hsi_midpoint_observation'
        };
        return;
      }
      const target = createHsiTarget(anchorPrice, observationDef.raw, scale, pointSize, direction, {
        observation: true,
        observation_key: observationDef.label,
        label: observationDef.label,
        style: 'hsi_midpoint_observation'
      });
      if (Number.isFinite(target.price)) targets.push(target);
    });
    return targets;
  }

  function buildManualHsiTargets(source, state) {
    const anchor = state?.hsiAnchor;
    const anchorPrice = numberOrNull(anchor?.price);
    if (anchorPrice == null) return [];
    const rawValues = parseHsiValues(state?.hsiValuesText);
    const scale = numberOrNull(state?.hsiScale) ?? getManualHsiSettings(source).scale;
    const pointSize = hsiPointSize(source);
    const direction = normalizeHsiDirection(state?.hsiDirection);
    const targets = rawValues.map(raw => createHsiTarget(anchorPrice, raw, scale, pointSize, direction))
      .filter(x => Number.isFinite(x.price));
    return appendHsiMidpointObservationTargets(targets, anchorPrice, scale, pointSize, direction);
  }


  function hsiAnchorPanelLabel(anchor, state) {
    if (!anchor) return '';
    const explicit = anchor.panel || anchor.timeframe;
    if (explicit) return String(explicit).toUpperCase();
    return panelKindToTimeframe(anchor.panelKind, state);
  }

  function hsiAnchorMatchesPanel(anchor, panelKind, state) {
    if (!anchor) return false;
    const panel = hsiAnchorPanelLabel(anchor, state);
    const targetPanel = panelKindToTimeframe(panelKind, state);
    if (targetPanel === 'M5') return ['M5', 'LOWER'].includes(panel) || anchor.panelKind === 'm5';
    return panel === targetPanel || (panel === 'UPPER' && isUpperPanelKind(panelKind));
  }

  function clearCurrentHsiAnchor(state) {
    if (!state) return;
    state.hsiAnchor = null;
    state.currentHsiAnchorHitBox = null;
  }

  function savedHsiAnnotationMatchesCurrentAnchor(source, state, annotation) {
    const anchor = state?.hsiAnchor;
    if (!anchor || !annotation) return false;
    const anchorPrice = numberOrNull(anchor.price);
    const annotationPrice = numberOrNull(annotation.price);
    if (anchorPrice == null || annotationPrice == null) return false;
    const priceTolerance = Math.max(0.0000001, hsiPointSize(source) * 0.5);
    if (Math.abs(anchorPrice - annotationPrice) > priceTolerance) return false;

    const anchorDirection = normalizeHsiDirection(state.hsiDirection);
    const annotationDirection = normalizeHsiDirection(annotation.hsi?.direction);
    if (anchorDirection !== annotationDirection) return false;

    const anchorPanel = hsiAnchorPanelLabel(anchor, state);
    const annotationPanel = String(annotation.panel || annotation.timeframe || 'M5').toUpperCase();
    return anchorPanel === annotationPanel
      || (anchorPanel === 'LOWER' && annotationPanel === 'M5')
      || (anchorPanel === 'M5' && annotationPanel === 'LOWER');
  }



  function hsiValuesFromAnnotation(annotation) {
    const raw = annotation?.hsi?.values ?? annotation?.hsi_values ?? annotation?.values;
    if (Array.isArray(raw)) {
      return raw.map(value => Number(value)).filter(n => Number.isFinite(n) && n > 0).slice(0, 12);
    }
    return parseHsiValues(annotation?.hsi?.values_text ?? annotation?.hsi_values_text ?? raw ?? '');
  }

  function buildHsiTargetsFromAnnotation(source, annotation) {
    const anchorPrice = numberOrNull(annotation?.price ?? annotation?.anchor?.price);
    if (anchorPrice == null) return [];
    const values = hsiValuesFromAnnotation(annotation);
    const scale = numberOrNull(annotation?.hsi?.scale ?? annotation?.scale) ?? 1;
    const pointSize = numberOrNull(annotation?.hsi?.point_size ?? annotation?.point_size) ?? hsiPointSize(source);
    const direction = normalizeHsiDirection(annotation?.hsi?.direction ?? annotation?.direction);
    const targets = values.map(raw => createHsiTarget(anchorPrice, raw, scale, pointSize, direction))
      .filter(x => Number.isFinite(x.price));
    return appendHsiMidpointObservationTargets(targets, anchorPrice, scale, pointSize, direction);
  }

  function hsiAnnotationPanelLabel(annotation) {
    return String(annotation?.panel || annotation?.timeframe || 'M5').toUpperCase();
  }

  function hsiAnnotationMatchesPanel(annotation, panelKind, state) {
    return shouldRenderHsiOnPanel(hsiAnnotationPanelLabel(annotation), panelKind, state);
  }

  function hsiAnnotationIndexForRows(annotation, rows) {
    if (!rows?.length) return null;
    const ms = parseDateTimeMs(annotation?.time);
    if (ms != null) {
      const first = numberOrNull(rows[0]?.start_ms) ?? rowTimeMs(rows[0]);
      const lastRow = rows[rows.length - 1];
      const last = numberOrNull(lastRow?.end_ms) ?? numberOrNull(lastRow?.start_ms) ?? rowTimeMs(lastRow);
      if (first != null && last != null && (ms < first || ms > last)) return null;
      return findIndexForTime(rows, ms);
    }
    const hint = numberOrNull(annotation?.x_index_hint ?? annotation?.x_index);
    if (hint != null) return Math.max(0, Math.min(rows.length - 1, Math.floor(hint)));
    return null;
  }

  function buildVisibleSavedHsiRenderItems(source, state, rows, panelKind) {
    if (state.showSavedHsi === false) return [];
    return (state.hsiAnnotations || [])
      .filter(annotation => (annotation.source_type || SAVED_HSI_SOURCE_TYPE) === SAVED_HSI_SOURCE_TYPE)
      .filter(annotation => (annotation.event_type || SAVED_HSI_EVENT_TYPE) === SAVED_HSI_EVENT_TYPE)
      .filter(annotation => annotation.display?.visible !== false)
      .filter(annotation => hsiAnnotationMatchesPanel(annotation, panelKind, state))
      .map(annotation => {
        const idx = hsiAnnotationIndexForRows(annotation, rows);
        const anchorPrice = numberOrNull(annotation?.price ?? annotation?.anchor?.price);
        if (idx == null || !rows[idx] || anchorPrice == null) return null;
        return { annotation, idx, anchorPrice, targets: buildHsiTargetsFromAnnotation(source, annotation) };
      })
      .filter(Boolean);
  }


  function simulationEntryHsiAnnotationFromSnapshot(snapshot, source, runDraft, executionEvent) {
    const usageEventType = String(executionEvent?.event_type || '').toLowerCase();
    if (!['entry', 'reentry', 'add_on'].includes(usageEventType)) return null;
    const lane = String(executionEvent?.rule_lane || executionEvent?.execution?.rule_lane || '').toUpperCase();
    // Expansion-LiteのHSI線は初回Entryで1本だけ生成し、Add-onでは同一起点を重複生成しない。
    if (lane === RULE_LANE_EXPANSION_LITE && usageEventType === 'add_on') return null;
    const execution = executionEvent?.execution || {};
    const timeframe = snapshot?.hsi_anchor_registry?.timeframes?.M5;
    const resolution = timeframe?.resolutions?.entry;
    const compactAnchor = resolution?.anchor;
    let anchorId = String(resolution?.anchor_id || compactAnchor?.anchor_id || '');
    let fullAnchor = null;
    if (lane === RULE_LANE_EXPANSION_LITE) {
      anchorId = String(execution.entry_anchor_id || '');
      fullAnchor = {
        anchor_id: anchorId,
        price: numberOrNull(execution.entry_anchor_price),
        pivot_time: execution.entry_anchor_time || executionEvent?.simulation_time || '',
        direction: String(execution.side || '').toUpperCase() === 'SHORT' ? 'DOWN' : 'UP',
        adoption_status: 'EXPANSION_LITE_TRADE_FIXED',
        roles: ['EXPANSION_LITE_ENTRY', 'EXPANSION_LITE_TARGET', 'EXPANSION_LITE_EXIT']
      };
    } else {
      if (!anchorId || resolution?.status !== 'RESOLVED_REFERENCE') return null;
      fullAnchor = (timeframe?.anchors || []).find(item => String(item?.anchor_id || '') === anchorId) || compactAnchor || {};
    }
    if (!anchorId) return null;
    const price = numberOrNull(fullAnchor?.price);
    if (price == null) return null;
    const executionPolicy = runDraft?.m5_execution_policy || snapshot?.policy?.m5_execution_policy || snapshot?.profile?.m5_execution_policy || {};
    const hsiDistance = executionPolicy?.hsi_distance || {};
    const values = (Array.isArray(hsiDistance.levels) ? hsiDistance.levels : HSI_RANGE_LEVELS)
      .map(item => numberOrNull(item?.raw ?? item))
      .filter(value => value != null && value > 0);
    const direction = normalizeHsiDirection(fullAnchor.direction === 'DOWN' ? 'down' : 'up');
    const usageEventId = String(executionEvent?.event_id || '');
    const usageTime = String(executionEvent?.simulation_time || snapshot?.period?.reference_time || snapshot?.created_at || '');
    const usageMs = numberOrNull(executionEvent?.simulation_ms ?? snapshot?.period?.reference_ms);
    const annotationId = usageEventId ? `${anchorId}__${usageEventId}` : anchorId;
    return {
      id: annotationId,
      annotation_id: annotationId,
      anchor_id: anchorId,
      usage_event_id: usageEventId || null,
      usage_event_type: usageEventType.toUpperCase(),
      trade_id: executionEvent?.trade_id || executionEvent?.execution?.trade_id || null,
      rule_lane: lane || RULE_LANE_NORMAL,
      source_type: SIMULATION_HSI_ANCHOR_SOURCE_TYPE,
      event_type: SAVED_HSI_EVENT_TYPE,
      timeframe: 'M5',
      panel: 'M5',
      time: String(fullAnchor.pivot_time || compactAnchor?.pivot_time || ''),
      recognized_time: usageTime,
      recognized_ms: usageMs,
      used_at_time: usageTime,
      used_at_ms: usageMs,
      price,
      direction,
      scale: numberOrNull(hsiDistance.scale) ?? 1,
      point_size: numberOrNull(hsiDistance.point_size) ?? hsiPointSize(source),
      hsi: {
        direction,
        scale: numberOrNull(hsiDistance.scale) ?? 1,
        point_size: numberOrNull(hsiDistance.point_size) ?? hsiPointSize(source),
        values,
        values_text: values.join(',')
      },
      lifecycle_status: lane === RULE_LANE_EXPANSION_LITE ? 'ACTIVE_FOR_EXPANSION_LITE_TRADE' : 'ACTIVE_FOR_NORMAL_TRADE',
      retired_at_time: null,
      retired_at_ms: null,
      retired_reason: null,
      adoption_status: String(fullAnchor.adoption_status || ''),
      roles: Array.isArray(fullAnchor.roles) ? [...fullAnchor.roles] : [],
      display: { visible: true, live_flash: false }
    };
  }

  function retireSimulationHsiAnnotationForExecutionEvent(annotations, executionEvent) {
    const type = String(executionEvent?.event_type || '').toLowerCase();
    const lane = String(executionEvent?.rule_lane || executionEvent?.execution?.rule_lane || '').toUpperCase();
    if (!['close', 'stop_close'].includes(type) || ![RULE_LANE_NORMAL, RULE_LANE_EXPANSION_LITE].includes(lane)) return null;
    const retiredAnchorId = String(executionEvent?.execution?.normal_hsi_anchor_retired_anchor_id || executionEvent?.execution?.entry_anchor_id || '');
    const tradeId = String(executionEvent?.trade_id || '');
    const candidates = (annotations || []).filter(item => {
      if (tradeId && String(item?.trade_id || '') === tradeId) return true;
      return retiredAnchorId && String(item?.anchor_id || '') === retiredAnchorId && !item?.retired_at_time;
    });
    const annotation = candidates[candidates.length - 1] || null;
    if (!annotation) return null;
    annotation.lifecycle_status = lane === RULE_LANE_EXPANSION_LITE ? 'RETIRED_ON_EXPANSION_LITE_CLOSE' : 'RETIRED_ON_NORMAL_CLOSE';
    annotation.retired_at_time = String(executionEvent?.execution?.normal_hsi_anchor_retired_at || executionEvent?.simulation_time || '');
    annotation.retired_at_ms = numberOrNull(executionEvent?.execution?.normal_hsi_anchor_retired_at_ms) ?? parseDateTimeMs(annotation.retired_at_time);
    annotation.retired_reason = String(executionEvent?.execution?.close_class || type).toUpperCase();
    annotation.display = { ...(annotation.display || {}), active: false };
    return annotation;
  }

  function buildVisibleSimulationHsiRenderItems(source, state, rows, panelKind) {
    return (state.simulationHsiAnnotations || [])
      .filter(annotation => annotation?.source_type === SIMULATION_HSI_ANCHOR_SOURCE_TYPE)
      .filter(annotation => annotation?.display?.visible !== false)
      .filter(annotation => hsiAnnotationMatchesPanel(annotation, panelKind, state))
      .map(annotation => {
        const idx = hsiAnnotationIndexForRows(annotation, rows);
        const anchorPrice = numberOrNull(annotation?.price);
        if (idx == null || !rows[idx] || anchorPrice == null) return null;
        const retiredMs = numberOrNull(annotation?.retired_at_ms) ?? parseDateTimeMs(annotation?.retired_at_time);
        const endIdx = retiredMs == null ? null : findIndexForTime(rows, retiredMs);
        return { annotation, idx, endIdx, anchorPrice, targets: buildHsiTargetsFromAnnotation(source, annotation) };
      })
      .filter(Boolean);
  }

  function escapeHtml(value) {
    return String(value ?? '')
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  function nowLocalIso() {
    const d = new Date();
    const pad = n => String(n).padStart(2, '0');
    return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`;
  }

  function compactTimestamp() {
    const d = new Date();
    const pad = n => String(n).padStart(2, '0');
    return `${d.getFullYear()}${pad(d.getMonth() + 1)}${pad(d.getDate())}_${pad(d.getHours())}${pad(d.getMinutes())}${pad(d.getSeconds())}`;
  }

  function shortText(value, max = 56) {
    const text = String(value ?? '').trim().replace(/\s+/g, ' ');
    return text.length > max ? text.slice(0, max - 1) + '…' : text;
  }


  function getSimulationTraceFileName(source) {
    const configured = source?.simulation_trace_sidecar?.file
      || pluginManifest?.display_policy?.simulation_trace_sidecar?.default_file
      || pluginManifest?.chart_viewer_policy?.simulation_trace_sidecar?.default_file;
    const clean = String(configured || DEFAULT_SIMULATION_TRACE_FILE).trim().replace(/\\/g, '/').split('/').pop();
    return clean && clean.toLowerCase().endsWith('.json') ? clean : DEFAULT_SIMULATION_TRACE_FILE;
  }

  function getSimulationTracePaths(source) {
    const file = getSimulationTraceFileName(source);
    return {
      file,
      relativePath: `studio_overlays/gpt_fx_lab/sidecars/${file}`,
      staticPath: `studio_overlays/gpt_fx_lab/sidecars/${file}`,
      apiPath: `/api/overlays/gpt_fx_lab/sidecars/${file}`
    };
  }

  function buildEmptySimulationTrace(source) {
    const paths = getSimulationTracePaths(source);
    return {
      schema_version: 'fx_simulation_trace_sidecar_v0_1',
      kind: 'fx_simulation_trace_sidecar',
      run: {
        run_id: '',
        status: 'fixture_or_not_started',
        rule_version: '',
        generated_at: ''
      },
      target: {
        symbol: source?.symbol || 'USDJPY',
        primary_timeframe: source?.timeframe || source?.timeframe_label || 'M5',
        data_path_hint: currentJsonParam('dataNameInput', DEFAULT_URL_DATA),
        sidecar_path_hint: paths.relativePath
      },
      display_policy: {
        default_visible: true,
        default_open: false,
        source_type: SIMULATION_TRACE_SOURCE_TYPE,
        teacher_guard: 'trace fixture / rule execution explanation only; no live trading signal'
      },
      trace_replay: null,
      run_result: {
        status: 'NO_EXECUTION_YET',
        execution_event_count: 0,
        trade_ids: [],
        teacher_guard: 'M5仮想実行と建玉Lifecycleを保存します。リアル注文・資金管理・売買推奨は行いません。'
      },
      simulation_hsi_annotations: [],
      events: []
    };
  }

  function normalizeStringArray(value) {
    if (Array.isArray(value)) return value.map(item => String(item ?? '').trim()).filter(Boolean);
    return String(value ?? '').split(/[，,\s]+/).map(item => item.trim()).filter(Boolean);
  }

  function normalizeSimulationTrace(raw, source) {
    const base = buildEmptySimulationTrace(source);
    const data = raw && typeof raw === 'object' ? raw : {};
    const events = Array.isArray(data.events)
      ? data.events
      : (Array.isArray(data.annotations) ? data.annotations : []);
    return {
      ...base,
      ...data,
      run: { ...base.run, ...(data.run || {}) },
      target: { ...base.target, ...(data.target || {}) },
      display_policy: { ...base.display_policy, ...(data.display_policy || {}) },
      trace_replay: data.trace_replay && typeof data.trace_replay === 'object' ? data.trace_replay : null,
      run_result: { ...base.run_result, ...(data.run_result || {}) },
      simulation_hsi_annotations: Array.isArray(data.simulation_hsi_annotations)
        ? data.simulation_hsi_annotations.map(item => ({ ...item, source_type: SIMULATION_HSI_ANCHOR_SOURCE_TYPE }))
        : [],
      events: events.map((event, index) => {
        const eventId = event.event_id || event.id || `trace_${index + 1}`;
        const simulationTime = event.simulation_time || event.time || event.datetime || '';
        const timeframe = String(event.timeframe || event.panel || 'M5').toUpperCase();
        return {
          ...event,
          event_id: eventId,
          id: eventId,
          source_type: event.source_type || SIMULATION_TRACE_SOURCE_TYPE,
          event_type: String(event.event_type || 'state_changed'),
          event_class: String(event.event_class || traceReplayEventClass(event)).toUpperCase(),
          event_class_label: String(event.event_class_label || traceEventClassLabel(event.event_class || traceReplayEventClass(event))),
          simulation_time: simulationTime,
          time: simulationTime,
          timeframe,
          panel: String(event.panel || timeframe).toUpperCase(),
          price: numberOrNull(event.price),
          summary: String(event.summary || event.result_summary || event.message || event.event_type || 'Simulation trace'),
          reason_codes: normalizeStringArray(event.reason_codes),
          rule_ids: normalizeStringArray(event.rule_ids),
          cause_event_ids: normalizeStringArray(event.cause_event_ids || event.caused_by_event_ids),
          state_before: event.state_before && typeof event.state_before === 'object' ? event.state_before : {},
          state_after: event.state_after && typeof event.state_after === 'object' ? event.state_after : {},
          upper_state_summary: event.upper_state_summary && typeof event.upper_state_summary === 'object' ? event.upper_state_summary : {},
          display: {
            visible: event.display?.visible !== false,
            open: Boolean(event.display?.open),
            pinned: Boolean(event.display?.pinned),
            style: event.display?.style || 'simulation_trace'
          }
        };
      })
    };
  }

  async function loadSimulationTraceSidecar(source) {
    const paths = getSimulationTracePaths(source);
    let data = null;
    let from = 'empty';
    try {
      data = await fetchJsonIfExists(paths.apiPath);
      from = 'api';
    } catch {
      try {
        data = await fetchJsonIfExists(paths.staticPath);
        from = 'static';
      } catch {
        data = buildEmptySimulationTrace(source);
      }
    }
    const trace = normalizeSimulationTrace(data, source);
    trace._loaded_from = from;
    return trace;
  }

  function batchSimulationExecutionEvents(batchRun) {
    return (Array.isArray(batchRun?.cases) ? batchRun.cases : [])
      .flatMap(item => Array.isArray(item?.execution_events) ? item.execution_events : []);
  }

  function focusedTradeExecutionEvents(batchRun, focus) {
    const tradeId = String(focus?.trade_id || '').trim();
    const lane = String(focus?.rule_lane || '').trim().toUpperCase();
    const entryEventId = String(focus?.entry_event_id || '').trim();
    const allEvents = batchSimulationExecutionEvents(batchRun);
    let selected = allEvents.filter(event => {
      if (tradeId && String(event?.trade_id || '') !== tradeId) return false;
      const eventLane = String(event?.rule_lane || event?.execution?.rule_lane || '').trim().toUpperCase();
      if (lane && eventLane !== lane) return false;
      return Boolean(tradeId || (entryEventId && String(event?.event_id || '') === entryEventId));
    });
    if (!selected.length && entryEventId) {
      const entryEvent = allEvents.find(event => String(event?.event_id || '') === entryEventId);
      if (entryEvent) {
        const resolvedTradeId = String(entryEvent.trade_id || '').trim();
        const resolvedLane = String(entryEvent.rule_lane || entryEvent.execution?.rule_lane || '').trim().toUpperCase();
        selected = allEvents.filter(event => String(event?.trade_id || '') === resolvedTradeId
          && String(event?.rule_lane || event?.execution?.rule_lane || '').trim().toUpperCase() === resolvedLane);
      }
    }
    return selected.sort((a, b) => {
      const timeDiff = (parseDateTimeMs(a?.simulation_time) ?? 0) - (parseDateTimeMs(b?.simulation_time) ?? 0);
      if (timeDiff !== 0) return timeDiff;
      return (numberOrNull(a?.case_step_no) ?? 0) - (numberOrNull(b?.case_step_no) ?? 0);
    });
  }

  function focusedEntryFallbackEvent(focus) {
    if (!focus?.time || numberOrNull(focus?.price) == null) return null;
    const lane = String(focus.rule_lane || 'NORMAL').toUpperCase();
    const side = String(focus.side || '').toUpperCase();
    const label = lane === RULE_LANE_EXPANSION_LITE
      ? `Expansion-Lite Entry${side ? ` ${side}` : ''}`
      : `Entry${side ? ` ${side}` : ''}`;
    return {
      event_id: focus.entry_event_id || `focused_entry_${focus.time_ms || compactTimestamp()}`,
      source_type: SIMULATION_TRACE_SOURCE_TYPE,
      generated_by: M5_EXECUTION_GENERATOR,
      event_type: 'entry',
      event_class: 'EXECUTION',
      simulation_time: focus.time,
      timeframe: 'M5',
      panel: 'M5',
      price: numberOrNull(focus.price),
      trade_id: focus.trade_id || '',
      rule_lane: lane,
      summary: `選択Entry${side ? ` ${side}` : ''} / ${round3(focus.price)}`,
      reason_codes: ['ENTRY_RESULT_CHART_FOCUS_FALLBACK'],
      rule_ids: [],
      execution: {
        action: 'ENTRY',
        rule_lane: lane,
        side,
        price: numberOrNull(focus.price),
        entry_price: numberOrNull(focus.price),
        chart_marker_label: label
      },
      display: { visible: true, open: false, pinned: true, focused: true, style: 'execution_entry_focus_fallback' }
    };
  }

  function mergeFocusedTradeProjection(state, source, rawEvents, loadedFrom) {
    const focus = state?.entryFocus;
    const normalized = normalizeSimulationTrace({ events: rawEvents || [] }, source).events.map(event => {
      const eventType = simulationRuleAwareEventType(event);
      const isFocusedEntry = String(event.event_id || '') === String(focus?.entry_event_id || '')
        || (!focus?.entry_event_id && ['entry', 'reentry'].includes(eventType));
      const side = String(event?.execution?.side || focus?.side || '').toUpperCase();
      const lane = String(event?.rule_lane || event?.execution?.rule_lane || focus?.rule_lane || '').toUpperCase();
      const currentLabel = String(event?.execution?.chart_marker_label || '').trim();
      event.execution = { ...(event.execution || {}) };
      if (isFocusedEntry && !currentLabel) {
        event.execution.chart_marker_label = lane === RULE_LANE_EXPANSION_LITE
          ? `Expansion-Lite Entry${side ? ` ${side}` : ''}`
          : `Entry${side ? ` ${side}` : ''}`;
      }
      event.display = {
        ...(event.display || {}),
        visible: true,
        open: false,
        pinned: true,
        focused: isFocusedEntry,
        batch_focus: true
      };
      return event;
    });
    const fallback = normalized.length ? null : focusedEntryFallbackEvent(focus);
    const additions = fallback ? normalizeSimulationTrace({ events: [fallback] }, source).events.map(event => ({
      ...event,
      display: { ...(event.display || {}), visible: true, pinned: true, focused: true, batch_focus: true }
    })) : normalized;
    const byId = new Map((state.simulationTraceEvents || []).map(event => [String(event.event_id || ''), event]));
    additions.forEach(event => byId.set(String(event.event_id || ''), event));
    state.simulationTraceEvents = [...byId.values()];
    state.entryFocusProjectionStatus = additions.length
      ? `loaded:${loadedFrom} / Trade Event ${additions.length}件`
      : 'focus projection unavailable';
    return additions;
  }

  async function loadEntryFocusBatchProjection(state, source) {
    const focus = state?.entryFocus;
    if (!focus) return [];
    const batchDataPath = validJsonParam(focus.batch_data_path);
    if (!batchDataPath) return mergeFocusedTradeProjection(state, source, [], 'URL fallback');
    try {
      const loaded = await loadUpperMapDataSource(batchDataPath);
      const events = focusedTradeExecutionEvents(loaded.source, focus);
      return mergeFocusedTradeProjection(state, source, events, `${loaded.from}:${batchDataPath}`);
    } catch (err) {
      console.warn('[GPT FX Lab] focused batch trade projection load failed', err);
      state.entryFocusProjectionStatus = `batch load failed:${batchDataPath}`;
      return mergeFocusedTradeProjection(state, source, [], 'URL fallback');
    }
  }

  function getSimulationRunProfileFileName() {
    const configured = pluginManifest?.display_policy?.simulation_run_profile?.default_file
      || pluginManifest?.chart_viewer_policy?.simulation_run_profile?.default_file;
    const clean = String(configured || DEFAULT_SIMULATION_RUN_PROFILE_FILE).trim().replace(/\\/g, '/').split('/').pop();
    return clean && clean.toLowerCase().endsWith('.json') ? clean : DEFAULT_SIMULATION_RUN_PROFILE_FILE;
  }

  function getSimulationRunProfilePaths() {
    const file = getSimulationRunProfileFileName();
    return {
      file,
      relativePath: `studio_overlays/gpt_fx_lab/simulation/${file}`,
      staticPath: `studio_overlays/gpt_fx_lab/simulation/${file}`,
      apiPath: `/api/overlays/gpt_fx_lab/simulation/${file}`
    };
  }

  function buildEmptySimulationRunProfile() {
    return {
      schema_version: 'fx_simulation_run_profile_v0_1',
      kind: 'fx_simulation_run_profile',
      profile_id: '',
      status: 'missing',
      rule_version: '',
      dataset: { primary: {}, upper_map: {} },
      period_policy: { mode: 'current_chart_window' },
      time_sync_policy: {
        reference_axis: 'M5_CLOSE',
        bar_timestamp_role: 'open_time',
        confirmation_rule: 'bar_end_ms <= reference_close_ms',
        week_start: 'MONDAY_00:00',
        dataset_timezone: 'UNSPECIFIED_LOCAL_WALL_CLOCK',
        runtime_interpretation: 'browser_local_time',
        future_rows: 'exclude',
        missing_bars: 'do_not_fill',
        state_rebuild: 'only_when_latest_confirmed_bar_changes'
      },
      swing_point_policy: {
        detector_id: SHARED_SWING_POINT_DETECTOR_ID,
        algorithm: 'center_window_unique_extreme',
        confirm_bars_source: 'timeframe_profiles[].confirm_bars',
        timeframe_specific_class: 'forbidden',
        no_lookahead: true,
        candidate_policy: 'left_window_unique_extreme_pending_until_full_window',
        confirmation_policy: 'full_window_unique_extreme',
        retirement_policy: 'same_type_replaced_by_more_extreme_confirmed_point',
        event_output: 'run_snapshot.swing_point_detection.observation_events',
        chart_event_projection: 'latest_active_high_low_per_timeframe'
      },
      dow_trend_policy: {
        evaluator_id: DOW_TREND_EVALUATOR_ID,
        input_source: 'run_snapshot.swing_point_detection.timeframes[].points + M5 confirmed bars for breakout detection',
        confirmed_points_only: true,
        pending_candidate_usage: 'forbidden',
        timeframe_specific_class: 'forbidden',
        comparison_rule: 'last_two_structure_highs_and_last_two_structure_lows',
        same_type_policy: 'replace_only_when_more_extreme',
        equal_price_policy: 'NO_TREND',
        mixed_structure_policy: 'REVERSAL_WATCH_when_prior_direction_exists_else_NO_TREND',
        insufficient_structure_policy: 'UNDETERMINED',
        state_change_event_only: true,
        confirmation_event_enabled: true,
        confirmation_event_policy: 'M5 confirmed pullback/return then prior structure high/low breakout; other TF complete directional structure pair advance',
        confirmation_event_output: 'run_snapshot.dow_trend_evaluation.confirmation_events',
        entry_permission_output: 'forbidden',
        no_lookahead: true,
        event_output: 'run_snapshot.dow_trend_evaluation.state_change_events',
        chart_event_projection: 'latest_state_change_per_timeframe'
      },
      cycle_position_policy: {
        evaluator_id: CYCLE_POSITION_EVALUATOR_ID,
        input_source: 'run_snapshot.swing_point_detection.timeframes[].points + candle_sync confirmed rows',
        origin_selection: 'latest_confirmed_usable_swing',
        candidate_usage: 'forbidden',
        retired_usage_for_current_origin: 'forbidden',
        historical_retired_origin_replay: true,
        timeframe_specific_class: 'forbidden',
        phase_threshold_source: 'timeframe_profiles[].cycle.phase_thresholds',
        context_mapping_source: 'timeframe_profiles[].cycle.context_state_map',
        elapsed_bar_rule: 'confirmed_bars_after_origin_pivot_excluding_origin_bar',
        origin_change_event: true,
        phase_change_event: true,
        action_permission_output: 'forbidden',
        no_lookahead: true,
        event_output: 'run_snapshot.cycle_position_evaluation.state_change_events',
        chart_event_projection: 'latest_cycle_state_event_per_timeframe'
      },
      hsi_anchor_policy: {
        registry_id: HSI_ANCHOR_REGISTRY_ID,
        resolver_id: HSI_ANCHOR_RESOLVER_ID,
        input_source: 'run_snapshot.swing_point_detection + dow_trend_evaluation + cycle_position_evaluation',
        source_type: SIMULATION_HSI_ANCHOR_SOURCE_TYPE,
        human_saved_hsi_source_type: SAVED_HSI_SOURCE_TYPE,
        timeframe_specific_class: 'forbidden',
        lifecycle_statuses: ['CANDIDATE', 'CONFIRMED', 'RETIRED'],
        adoption_statuses: ['NOT_ELIGIBLE', 'AVAILABLE', 'ADOPTED', 'RETIRED'],
        candidate_usage: 'registry_only_not_resolvable',
        confirmed_active_eligibility: true,
        retired_retention: true,
        status_role_separation: true,
        direction_rule: 'swing_low_is_up_anchor_swing_high_is_down_anchor',
        direction_context_rule: 'normal_dow_directional_regime_for_normal_entry_and_expansion_detection_regime_for_expansion',
        role_assignment: 'normal_dow_entry_reset_plus_expansion_detection_retain_and_entry_dual_anchor',
        purpose_resolvers: {
          entry: 'normal_dow_anchor_reset_on_reversal_watch_no_trend_undetermined_then_adopt_new_previous_swing',
          normal_entry: 'normal_dow_anchor_reset_on_reversal_watch_no_trend_undetermined_then_adopt_new_previous_swing',
          expansion_detection: 'original_dow_anchor_retained_across_non_directional_state_until_opposite_dow',
          expansion_entry: 'latest_active_aligned_pullback_anchor_separate_from_detection_anchor',
          hold: 'oldest_active_aligned_anchor_in_analysis_scope',
          target: 'oldest_active_aligned_anchor_in_analysis_scope',
          thesis: 'oldest_active_aligned_anchor_in_analysis_scope',
          confluence: 'all_active_aligned_anchors'
        },
        normal_anchor_reset_policy: 'reversal_watch_no_trend_undetermined',
        same_direction_reconfirmation_policy: 'adopt_new_previous_swing_after_reset',
        new_swing_during_same_dow_policy: 'candidate_only_do_not_replace_normal_entry_anchor',
        expansion_dual_anchor_policy: {
          detection_anchor: 'original_dow_adopted_anchor',
          entry_anchor: 'latest_confirmed_pullback_or_retracement_anchor',
          replace_detection_anchor: false,
          non_directional_state_policy: 'retain_detection_anchor'
        },
        human_saved_hsi_comparison: 'same_timeframe_nearest_time_then_price_reference_only',
        action_permission_output: 'forbidden',
        no_lookahead: true,
        event_output: 'run_snapshot.hsi_anchor_registry.lifecycle_events',
        chart_event_projection: 'latest_adopted_anchor_per_timeframe'
      },
      timeframe_state_policy: {
        builder_id: TIMEFRAME_STATE_BUILDER_ID,
        input_source: 'candle_sync + swing_point_detection + dow_trend_evaluation + cycle_position_evaluation + hsi_anchor_registry + confirmed_close_bb',
        timeframe_specific_class: 'forbidden',
        state_as_of_source: 'candle_sync.reference.reference_close_time',
        state_id_policy: 'stable_reference_plus_observation_signature',
        source_event_ids_required: true,
        data_sufficiency_separate_from_market_state: true,
        action_permission_output: 'forbidden',
        no_lookahead: true,
        bb_phase: {
          period: 20,
          deviations: 2,
          source: 'close',
          lookback_bands: 20,
          width_change_threshold_ratio: 0.03,
          states: ['SQUEEZE', 'OPENING', 'EXPANSION', 'MATURE', 'CONTRACTING', 'STABLE', 'UNDETERMINED']
        },
        event_output: 'run_snapshot.timeframe_states.state_events',
        chart_event_projection: 'one_current_state_summary_per_timeframe'
      },
      upper_context_decision_policy: {
        engine_id: UPPER_CONTEXT_DECISION_ENGINE_ID,
        input_source: 'run_snapshot.timeframe_states.timeframes',
        required_timeframes: ['WEEK', 'DAY', 'H4', 'H1'],
        timeframe_specific_class: 'forbidden',
        rule_evaluation: 'priority_ordered_specification_registry',
        no_trade_priority: true,
        data_sufficiency_required_for_new_entry: 'READY',
        permission_states: ['ALLOW_SEARCH', 'CONDITIONAL', 'WAIT', 'BLOCKED', 'NOT_EVALUATED'],
        direction_bias_rule: 'h4_direction_plus_h1_alignment',
        week_direct_close: false,
        week_late_policy: {
          expansion_entry: 'BLOCKED',
          reentry: 'BLOCKED',
          add_on: 'BLOCKED',
          h1_exit_trigger_enabled: true,
          exit_policy: 'ACCELERATED'
        },
        profit_take_arm_rule: {
          h4_cycle_phase: 'LATE',
          h4_bb_phase: 'CONTRACTING',
          minimum_hsi_confluence_anchors: 2
        },
        h1_exit_trigger_rule: {
          enabled_by: ['WEEK_LATE', 'PROFIT_TAKE_ARMED'],
          confirmed_by: 'h1_opposes_h4_direction',
          watch_by: ['REVERSAL_WATCH', 'NO_TREND'],
          direct_close: false
        },
        action_execution_output: 'forbidden',
        no_lookahead: true,
        event_output: 'run_snapshot.upper_context_decision.decision_events',
        chart_event_projection: 'one_current_decision_summary'
      },
      trace_replay_policy: {
        engine_id: TRACE_REPLAY_ENGINE_ID,
        input_sources: [
          'run_snapshot.swing_point_detection.observation_events',
          'run_snapshot.dow_trend_evaluation.state_change_events',
          'run_snapshot.dow_trend_evaluation.confirmation_events',
          'run_snapshot.cycle_position_evaluation.state_change_events',
          'run_snapshot.hsi_anchor_registry.lifecycle_events',
          'run_snapshot.timeframe_states.state_events',
          'run_snapshot.upper_context_decision.decision_events'
        ],
        event_classes: [...TRACE_EVENT_CLASSES],
        append_only: true,
        full_state_per_event: false,
        delta_patch_required: true,
        cause_event_ids_required_for: ['STATE_CHANGE', 'DECISION', 'EXECUTION'],
        root_event_types: ['swing_candidate', 'dow_confirmation', 'timeframe_state_snapshot', 'timeframe_state_changed'],
        checkpoint_interval_events: 50,
        final_checkpoint_required: true,
        replay_method: 'nearest_checkpoint_then_apply_delta_patches',
        dag_validation: true,
        missing_cause_reference: 'error',
        circular_cause_reference: 'forbidden',
        future_cause_reference: 'error',
        ui_language: 'ja',
        action_execution_output: 'forbidden',
        no_lookahead: true,
        event_output: 'run_snapshot.trace_replay.events',
        checkpoint_output: 'run_snapshot.trace_replay.checkpoints'
      },
      m5_execution_policy: {
        engine_id: M5_EXECUTION_ENGINE_ID,
        mode: 'reference_point_step',
        input_source: 'H4/H1 T3 state + M5 confirmed pullback/return and structure breakout confirmation + H4/H1 cycle state + confirmation-adopted HSI anchor + previous position_lifecycle',
        execution_timeframe: 'M5',
        upper_decision_reimplementation: NORMAL_ENTRY_V0_17_UPPER_DECISION_EXCEPTION,
        allowed_actions: ['ENTRY', 'REENTRY', 'ADD_ON', 'FULL_CLOSE', 'STOP_CLOSE'],
        rule_lane_policy: {
          active_entry_rule_lane: RULE_LANE_NORMAL,
          allowed_entry_rule_lanes: [RULE_LANE_NORMAL, RULE_LANE_EXPANSION, RULE_LANE_EXPANSION_LITE],
          allowed_entry_lane_modes: [RULE_LANE_NORMAL, RULE_LANE_EXPANSION_LITE, ENTRY_LANE_MODE_NORMAL_AND_EXPANSION_LITE, ENTRY_LANE_MODE_PARALLEL_RULE_LANES],
          shared_fact_source: 'TIMEFRAME_STATE_SNAPSHOT',
          close_lane_source: 'OPEN_TRADE_RULE_LANE',
          arbitration: ['EVALUATE_EACH_RULE_LANE_INDEPENDENTLY', 'ALLOW_ALL_MATCHED_LANES_ON_SAME_BAR'],
          parallel_entry_enabled: false,
          simultaneous_entry_policy: 'SINGLE_LANE_ONLY',
          lanes: {
            NORMAL: { enabled: true, entry_evaluator_id: NORMAL_ENTRY_EVALUATOR_ID, close_evaluator_id: NORMAL_CLOSE_EVALUATOR_ID, allowed_actions: ['ENTRY', 'FULL_CLOSE', 'STOP_CLOSE'] },
            EXPANSION: { enabled: false, entry_evaluator_id: EXPANSION_ENTRY_EVALUATOR_ID, close_evaluator_id: EXPANSION_CLOSE_EVALUATOR_ID, allowed_actions: ['ENTRY', 'REENTRY', 'ADD_ON', 'FULL_CLOSE', 'STOP_CLOSE'] },
            EXPANSION_LITE: { enabled: false, entry_evaluator_id: EXPANSION_LITE_ENTRY_EVALUATOR_ID, close_evaluator_id: EXPANSION_LITE_CLOSE_EVALUATOR_ID, allowed_actions: ['ENTRY', 'REENTRY', 'ADD_ON', 'FULL_CLOSE', 'STOP_CLOSE'] }
          }
        },
        normal_entry_policy: {
          rule_version: NORMAL_RULE_VERSION,
          applies_to: ['ENTRY'],
          direction_permission: 'H4_H1_T3_SLOPE_AND_CLOSE_SIDE_PLUS_M5_DOW',
          h4_dow_required: false,
          h1_dow_required: false,
          h1_t3_required: true,
          m5_dow_required: true,
          h1_m5_dow_match_required: false,
          cycle_late_guard_timeframes: ['H1'],
          cycle_late_entry_allowed: false,
          week_filter_required: false,
          day_expansion_grade_required: false,
          expansion_confirmation_required: false,
          entry_trigger: 'DOW_BREAKOUT_CONFIRMATION_IF_R2_READY_ELSE_FIRST_R2_TOUCH',
          entry_raw: 89,
          entry_label: 'R2',
          target_policy: 'NEXT_HSI_BOUNDARY_FROM_ENTRY_DISTANCE',
          one_entry_opportunity_per_dow_confirmation: true,
          late_entry_after_r2: 'ALLOWED_ONLY_AT_NEW_DOW_BREAKOUT_CONFIRMATION',
          r2_ready_at_confirmation: 'IMMEDIATE_ENTRY_AT_FIRST_PRICE_SATISFYING_DOW_BREAKOUT_AND_R2',
          target_selection_at_confirmation: 'NEXT_HSI_BOUNDARY_AHEAD',
          next_normal_entry_requires_new_dow_confirmation_after_previous_close: true,
          normal_hsi_anchor_lifecycle: 'DOW_CONFIRMATION_TO_PRE_ENTRY_BREAK_OR_TRADE_CLOSE',
          normal_hsi_anchor_retired_on_close: true,
          normal_hsi_anchor_reuse_after_close: false,
          next_normal_hsi_anchor_source: 'FIRST_NEW_M5_DOW_CONFIRMATION_AFTER_BREAK_OR_CLOSE_PREVIOUS_SWING',
          same_confirmation_reuse_for_next_normal_entry: false,
          same_direction_dow_reconfirmation_replaces_anchor: false,
          same_direction_reconfirmation_after_break_creates_new_anchor: true,
          dow_reconfirmation_point_is_anchor: false,
          normal_reentry_concept: 'NOT_DEFINED',
          normal_add_on_concept: 'FORBIDDEN',
          pre_entry_dow_structure_break_expires_opportunity: true,
          pre_entry_dow_structure_break_policy: 'CONFIRMED_RESET_STATE_OR_NEWER_OPPOSITE_DOW_CONFIRMATION',
          pre_entry_dow_structure_break_states: ['REVERSAL_WATCH', 'NO_TREND', 'UNDETERMINED'],
          post_entry_dow_structure_break_close_policy: 'OBSERVE_ONLY_NO_CLOSE',
          post_entry_anchor_target_stop_policy: 'FIX_UNTIL_TRADE_CLOSE'
        },
        entry_guard_policy: {
          day_up_h4_down_r5_short: {
            enabled: true,
            rule_version: EXPANSION_LITE_ENTRY_GUARD_RULE_VERSION,
            block_at_or_above_raw: 377,
            block_at_or_above_label: 'R5',
            applies_to_rule_lanes: [RULE_LANE_NORMAL, RULE_LANE_EXPANSION, RULE_LANE_EXPANSION_LITE]
          },
          normal_h4_same_direction_r4: {
            enabled: true,
            rule_version: 'v0.22',
            block_at_or_above_raw: 233,
            block_at_or_above_label: 'R4',
            applies_to_rule_lanes: [RULE_LANE_NORMAL]
          }
        },
        normal_close_miss_policy: {
          strategy_id: 'target_distance_ratio_v0_1',
          max_loss_to_reward_ratio: 1.0,
          hsi_anchor_hard_limit: true,
          fix_price_at_entry: true,
          trigger_price_source: 'M5_HIGH_LOW'
        },
        expansion_lite_policy: {
          rule_version: EXPANSION_LITE_RULE_VERSION,
          entry_guard_rule_version: EXPANSION_LITE_ENTRY_GUARD_RULE_VERSION,
          day_cycle_position_required: false,
          h4_close_t3_side_required: true,
          h1_close_t3_side_required: true,
          h1_cycle_entry_allowed_max_bars_source: 'timeframe_profiles[H1].cycle.entry_allowed_max_bars',
          m5_dow_confirmation_required: true,
          entry_raw: 144,
          entry_label: 'R3',
          entry_trigger: 'DOW_CONFIRMATION_IF_R3_READY_ELSE_FIRST_R3_TOUCH',
          entry_price_policy: 'FIRST_PRICE_SATISFYING_DOW_CONFIRMATION_AND_R3_ELSE_FIRST_R3_TOUCH',
          add_on_levels: [
            { raw: 188, label: 'R3.5' },
            { raw: 233, label: 'R4' },
            { raw: 305, label: 'R4.5' }
          ],
          target_raw: 377,
          target_label: 'R5',
          target_touch_source: 'M5_HIGH_LOW',
          t3_exit_touch_source: 'M5_HIGH_LOW',
          anchor_exit_touch_source: 'M5_HIGH_LOW',
          structural_exit_source: 'M5_CONFIRMED_DOW_STRUCTURE_POINT',
          same_bar_exit_priority: ['ANCHOR_EXIT', 'T3_EXIT', 'STRUCTURAL_EXIT', 'TARGET_EXIT'],
          one_entry_per_dow_confirmation: true,
          same_add_on_level_once: true,
          other_rule_lane_fallback: 'FORBIDDEN'
        },
        hsi_distance: {
          point_size: 0.001,
          scale: 6,
          entry_min_raw: 89,
          entry_min_label: 'R2',
          levels: HSI_RANGE_LEVELS.map(item => ({ raw: item.raw, label: item.label }))
        },
        position_sizing: {
          initial_units: 10,
          core_units: 10,
          runner_units: 0,
          add_on_units: 2,
          partial_close_units: 0,
          close_policy: 'SINGLE_CLOSE',
          max_active_normal_positions: 1,
          normal_add_on_allowed: false,
          expansion_add_on_allowed: true
        },
        valuation_policy: {
          unit_base_currency_amount: 1000,
          display_currency: 'JPY',
          quote_currency: 'JPY',
          pnl_formula: 'USDJPY_DIRECT_QUOTE',
          stop_basis: 'TARGET_DISTANCE_RATIO_WITH_HSI_ANCHOR_HARD_LIMIT',
          fee_and_slippage_included: false
        },
        management_timeframe: {
          normal_core_initial: 'H1',
          expansion_core_initial: 'H4',
          add_on_initial: 'H1',
          runner_initial: 'H4',
          cap: 'DAY',
          week_forbidden: true,
          loss_avoidance_promotion: 'forbidden',
          promotion_requires_higher_wave_connection: true
        },
        execution_priority: ['STOP_CLOSE', 'FULL_CLOSE', 'ADD_ON', 'REENTRY', 'ENTRY'],
        close_execution_policy: {
          close_policy: 'SINGLE_CLOSE',
          touch_source: 'M5_HIGH_LOW',
          stop_basis: 'TARGET_DISTANCE_RATIO_FIXED_AT_ENTRY_WITH_HSI_ANCHOR_HARD_LIMIT',
          target_basis: 'NEXT_HSI_BOUNDARY_AHEAD_OF_ACTUAL_ENTRY_DISTANCE',
          normal_entry_target_policy: 'NEXT_HSI_BOUNDARY',
          ambiguous_same_bar_policy: 'STOP_FIRST_CONSERVATIVE',
          normal_close_retires_entry_anchor: true,
          normal_close_next_state: 'AWAIT_NEW_M5_DOW_CONFIRMATION'
        },
        expansion_confirmation_required: true,
        expansion_confirmation_source: 'future_expansion_state_not_yet_available',
        real_order_output: 'forbidden',
        money_management_output: 'forbidden',
        no_lookahead: true,
        event_output: 'run_snapshot.position_lifecycle.execution_events',
        decision_event_output: 'run_snapshot.position_lifecycle.decision_events',
        chart_event_projection: 'execution_events_only'
      },
      timeframe_profiles: [],
      validation_policy: {
        required_timeframes: [...REQUIRED_SIMULATION_TIMEFRAMES],
        confirm_bars_min: 3,
        confirm_bars_max: 101,
        inheritance: 'forbidden',
        calculation_from_other_timeframes: 'forbidden',
        implicit_default: 'forbidden',
        implicit_fallback: 'forbidden'
      },
      snapshot_policy: {
        storage: 'simulation_trace_sidecar.run_snapshot',
        engine_enabled: true,
        decision_engine_enabled: true,
        trace_replay_engine_enabled: true,
        copy_trace_replay_events: true,
        copy_trace_checkpoints: true,
        m5_trigger_engine_enabled: true,
        trade_execution_enabled: true,
        copy_position_lifecycle: true,
        copy_m5_trigger_decisions: true,
        copy_execution_events: true
      }
    };
  }

  function cloneJsonValue(value) {
    if (value == null) return value;
    return JSON.parse(JSON.stringify(value));
  }

  function normalizeHsiAnchorPolicyContract(rawPolicy) {
    const policy = rawPolicy && typeof rawPolicy === 'object' ? { ...rawPolicy } : {};
    const resolverId = String(policy.resolver_id || '').trim();
    if (!LEGACY_HSI_ANCHOR_RESOLVER_IDS.has(resolverId)) return policy;
    return {
      ...policy,
      resolver_id: HSI_ANCHOR_RESOLVER_ID,
      direction_context_rule: 'normal_dow_directional_regime_for_normal_entry_and_expansion_detection_regime_for_expansion',
      role_assignment: 'normal_dow_entry_reset_plus_expansion_detection_retain_and_entry_dual_anchor',
      purpose_resolvers: {
        ...(policy.purpose_resolvers || {}),
        entry: 'normal_dow_anchor_reset_on_reversal_watch_no_trend_undetermined_then_adopt_new_previous_swing',
        normal_entry: 'normal_dow_anchor_reset_on_reversal_watch_no_trend_undetermined_then_adopt_new_previous_swing',
        expansion_detection: 'original_dow_anchor_retained_across_non_directional_state_until_opposite_dow',
        expansion_entry: 'latest_active_aligned_pullback_anchor_separate_from_detection_anchor'
      },
      normal_anchor_reset_policy: 'reversal_watch_no_trend_undetermined',
      same_direction_reconfirmation_policy: 'adopt_new_previous_swing_after_reset',
      new_swing_during_same_dow_policy: 'candidate_only_do_not_replace_normal_entry_anchor',
      expansion_dual_anchor_policy: {
        ...(policy.expansion_dual_anchor_policy || {}),
        detection_anchor: 'original_dow_adopted_anchor',
        entry_anchor: 'latest_confirmed_pullback_or_retracement_anchor',
        replace_detection_anchor: false,
        non_directional_state_policy: 'retain_detection_anchor'
      }
    };
  }

  function normalizeSimulationRunProfile(raw) {
    const base = buildEmptySimulationRunProfile();
    const data = raw && typeof raw === 'object' ? raw : {};
    const profiles = Array.isArray(data.timeframe_profiles) ? data.timeframe_profiles : [];
    const normalizedHsiAnchorPolicy = normalizeHsiAnchorPolicyContract(data.hsi_anchor_policy || {});
    return {
      ...base,
      ...data,
      dataset: {
        primary: { ...(base.dataset.primary || {}), ...(data.dataset?.primary || {}) },
        upper_map: { ...(base.dataset.upper_map || {}), ...(data.dataset?.upper_map || {}) }
      },
      period_policy: { ...base.period_policy, ...(data.period_policy || {}) },
      time_sync_policy: { ...base.time_sync_policy, ...(data.time_sync_policy || {}) },
      swing_point_policy: { ...base.swing_point_policy, ...(data.swing_point_policy || {}) },
      dow_trend_policy: { ...base.dow_trend_policy, ...(data.dow_trend_policy || {}) },
      cycle_position_policy: { ...base.cycle_position_policy, ...(data.cycle_position_policy || {}) },
      hsi_anchor_policy: {
        ...base.hsi_anchor_policy,
        ...normalizedHsiAnchorPolicy,
        purpose_resolvers: { ...(base.hsi_anchor_policy.purpose_resolvers || {}), ...(normalizedHsiAnchorPolicy.purpose_resolvers || {}) },
        expansion_dual_anchor_policy: { ...(base.hsi_anchor_policy.expansion_dual_anchor_policy || {}), ...(normalizedHsiAnchorPolicy.expansion_dual_anchor_policy || {}) }
      },
      timeframe_state_policy: {
        ...base.timeframe_state_policy,
        ...(data.timeframe_state_policy || {}),
        bb_phase: { ...(base.timeframe_state_policy.bb_phase || {}), ...(data.timeframe_state_policy?.bb_phase || {}) }
      },
      upper_context_decision_policy: {
        ...base.upper_context_decision_policy,
        ...(data.upper_context_decision_policy || {}),
        week_late_policy: { ...(base.upper_context_decision_policy.week_late_policy || {}), ...(data.upper_context_decision_policy?.week_late_policy || {}) },
        profit_take_arm_rule: { ...(base.upper_context_decision_policy.profit_take_arm_rule || {}), ...(data.upper_context_decision_policy?.profit_take_arm_rule || {}) },
        h1_exit_trigger_rule: { ...(base.upper_context_decision_policy.h1_exit_trigger_rule || {}), ...(data.upper_context_decision_policy?.h1_exit_trigger_rule || {}) }
      },
      trace_replay_policy: { ...base.trace_replay_policy, ...(data.trace_replay_policy || {}) },
      m5_execution_policy: {
        ...base.m5_execution_policy,
        ...(data.m5_execution_policy || {}),
        hsi_distance: { ...(base.m5_execution_policy.hsi_distance || {}), ...(data.m5_execution_policy?.hsi_distance || {}) },
        position_sizing: { ...(base.m5_execution_policy.position_sizing || {}), ...(data.m5_execution_policy?.position_sizing || {}) },
        rule_lane_policy: {
          ...(base.m5_execution_policy.rule_lane_policy || {}),
          ...(data.m5_execution_policy?.rule_lane_policy || {}),
          lanes: {
            ...(base.m5_execution_policy.rule_lane_policy?.lanes || {}),
            ...(data.m5_execution_policy?.rule_lane_policy?.lanes || {}),
            NORMAL: { ...(base.m5_execution_policy.rule_lane_policy?.lanes?.NORMAL || {}), ...(data.m5_execution_policy?.rule_lane_policy?.lanes?.NORMAL || {}) },
            EXPANSION: { ...(base.m5_execution_policy.rule_lane_policy?.lanes?.EXPANSION || {}), ...(data.m5_execution_policy?.rule_lane_policy?.lanes?.EXPANSION || {}) },
            EXPANSION_LITE: { ...(base.m5_execution_policy.rule_lane_policy?.lanes?.EXPANSION_LITE || {}), ...(data.m5_execution_policy?.rule_lane_policy?.lanes?.EXPANSION_LITE || {}) }
          }
        },
        normal_entry_policy: { ...(base.m5_execution_policy.normal_entry_policy || {}), ...(data.m5_execution_policy?.normal_entry_policy || {}) },
        entry_guard_policy: {
          ...(base.m5_execution_policy.entry_guard_policy || {}),
          ...(data.m5_execution_policy?.entry_guard_policy || {}),
          day_up_h4_down_r5_short: {
            ...(base.m5_execution_policy.entry_guard_policy?.day_up_h4_down_r5_short || {}),
            ...(data.m5_execution_policy?.entry_guard_policy?.day_up_h4_down_r5_short || {})
          },
          normal_h4_same_direction_r4: {
            ...(base.m5_execution_policy.entry_guard_policy?.normal_h4_same_direction_r4 || {}),
            ...(data.m5_execution_policy?.entry_guard_policy?.normal_h4_same_direction_r4 || {})
          }
        },
        normal_close_miss_policy: { ...(base.m5_execution_policy.normal_close_miss_policy || {}), ...(data.m5_execution_policy?.normal_close_miss_policy || {}) },
        expansion_lite_policy: { ...(base.m5_execution_policy.expansion_lite_policy || {}), ...(data.m5_execution_policy?.expansion_lite_policy || {}) },
        valuation_policy: { ...(base.m5_execution_policy.valuation_policy || {}), ...(data.m5_execution_policy?.valuation_policy || {}) },
        management_timeframe: { ...(base.m5_execution_policy.management_timeframe || {}), ...(data.m5_execution_policy?.management_timeframe || {}) }
      },
      validation_policy: { ...base.validation_policy, ...(data.validation_policy || {}) },
      snapshot_policy: { ...base.snapshot_policy, ...(data.snapshot_policy || {}) },
      timeframe_profiles: profiles.map(item => ({
        ...item,
        timeframe: normalizePanelTimeframe(item?.timeframe, String(item?.timeframe || '').toUpperCase()),
        confirm_bars: item?.confirm_bars == null || item?.confirm_bars === '' ? null : Number(item.confirm_bars),
        required: item?.required !== false,
        source_mapping: item?.source_mapping && typeof item.source_mapping === 'object' ? { ...item.source_mapping } : {},
        warmup: item?.warmup && typeof item.warmup === 'object' ? { ...item.warmup } : {},
        cycle: item?.cycle && typeof item.cycle === 'object' ? {
          ...item.cycle,
          phase_thresholds: item.cycle.phase_thresholds && typeof item.cycle.phase_thresholds === 'object' ? { ...item.cycle.phase_thresholds } : {},
          context_state_map: item.cycle.context_state_map && typeof item.cycle.context_state_map === 'object' ? { ...item.cycle.context_state_map } : {}
        } : {}
      }))
    };
  }

  async function loadSimulationRunProfile() {
    const paths = getSimulationRunProfilePaths();
    let data = null;
    let from = 'missing';
    try {
      data = await fetchJsonIfExists(paths.apiPath);
      from = 'api';
    } catch {
      try {
        data = await fetchJsonIfExists(paths.staticPath);
        from = 'static';
      } catch {
        data = buildEmptySimulationRunProfile();
      }
    }
    const profile = normalizeSimulationRunProfile(data);
    profile._loaded_from = from;
    profile._profile_file = paths.file;
    return profile;
  }

  function getSimulationReasonRuleCatalogFileName() {
    const configured = pluginManifest?.display_policy?.simulation_reason_rule_catalog?.default_file
      || pluginManifest?.chart_viewer_policy?.simulation_reason_rule_catalog?.default_file;
    const clean = String(configured || DEFAULT_SIMULATION_REASON_RULE_CATALOG_FILE).trim().replace(/\\/g, '/').split('/').pop();
    return clean && clean.toLowerCase().endsWith('.json') ? clean : DEFAULT_SIMULATION_REASON_RULE_CATALOG_FILE;
  }

  function getSimulationReasonRuleCatalogPaths() {
    const file = getSimulationReasonRuleCatalogFileName();
    return {
      file,
      staticPath: `studio_overlays/gpt_fx_lab/simulation/${file}`,
      apiPath: `/api/overlays/gpt_fx_lab/simulation/${file}`
    };
  }

  function buildEmptySimulationReasonRuleCatalog() {
    return {
      schema_version: 'fx_simulation_reason_rule_catalog_v0_1',
      kind: 'fx_simulation_reason_rule_catalog',
      display_policy: { unmapped_text: '日本語説明未登録。コードは保持し、カタログへ追加してください。' },
      judgment_templates: { default: { title: 'シミュレーション判断を記録しました。', body: '下の日本語理由と使用ルールを確認してください。' } },
      reason_codes: [],
      rule_ids: [],
      _reason_map: {},
      _rule_map: {}
    };
  }

  function normalizeSimulationReasonRuleCatalog(raw) {
    const base = buildEmptySimulationReasonRuleCatalog();
    const data = raw && typeof raw === 'object' ? raw : {};
    const reasonRows = Array.isArray(data.reason_codes) ? data.reason_codes : [];
    const ruleRows = Array.isArray(data.rule_ids) ? data.rule_ids : [];
    const normalized = {
      ...base,
      ...data,
      display_policy: { ...base.display_policy, ...(data.display_policy || {}) },
      judgment_templates: { ...base.judgment_templates, ...(data.judgment_templates || {}) },
      reason_codes: reasonRows.map(row => ({ code: String(row?.code || '').trim(), ja: String(row?.ja || '').trim(), category: String(row?.category || '') })).filter(row => row.code),
      rule_ids: ruleRows.map(row => ({ code: String(row?.code || '').trim(), ja: String(row?.ja || '').trim(), category: String(row?.category || '') })).filter(row => row.code)
    };
    normalized._reason_map = Object.fromEntries(normalized.reason_codes.map(row => [row.code, row]));
    normalized._rule_map = Object.fromEntries(normalized.rule_ids.map(row => [row.code, row]));
    return normalized;
  }

  async function loadSimulationReasonRuleCatalog() {
    const paths = getSimulationReasonRuleCatalogPaths();
    let data = null;
    let from = 'missing';
    try {
      data = await fetchJsonIfExists(paths.apiPath);
      from = 'api';
    } catch {
      try {
        data = await fetchJsonIfExists(paths.staticPath);
        from = 'static';
      } catch {
        data = buildEmptySimulationReasonRuleCatalog();
      }
    }
    const catalog = normalizeSimulationReasonRuleCatalog(data);
    catalog._loaded_from = from;
    catalog._catalog_file = paths.file;
    return catalog;
  }

  function simulationRunDraftFromProfile(profile) {
    const draft = cloneJsonValue(profile || buildEmptySimulationRunProfile());
    delete draft?._loaded_from;
    delete draft?._profile_file;
    return draft;
  }

  function validateSimulationRunDraft(draft) {
    const errors = [];
    const warnings = ['Expansion Core / Expansion Add-on execution is not implemented. NORMAL and EXPANSION_LITE are independent Rule Lanes.'];
    const policy = draft?.validation_policy || {};
    const min = Math.max(1, Math.floor(numberOrNull(policy.confirm_bars_min) ?? 3));
    const max = Math.max(min, Math.floor(numberOrNull(policy.confirm_bars_max) ?? 101));
    if (!String(draft?.profile_id || '').trim()) errors.push('profile_id が未設定です。');
    if (!String(draft?.rule_version || '').trim()) errors.push('rule_version が未設定です。');
    if (!String(draft?.dataset?.primary?.path || '').trim()) errors.push('Primary dataset path が未設定です。');
    if (!String(draft?.dataset?.primary?.sha256 || '').trim()) errors.push('Primary dataset sha256 が未設定です。');
    if (!String(draft?.dataset?.upper_map?.path || '').trim()) errors.push('UpperMap dataset path が未設定です。');
    if (!String(draft?.dataset?.upper_map?.sha256 || '').trim()) errors.push('UpperMap dataset sha256 が未設定です。');
    const profiles = Array.isArray(draft?.timeframe_profiles) ? draft.timeframe_profiles : [];
    const counts = new Map();
    profiles.forEach(item => {
      const tf = normalizePanelTimeframe(item?.timeframe, String(item?.timeframe || '').toUpperCase());
      counts.set(tf, (counts.get(tf) || 0) + 1);
    });
    REQUIRED_SIMULATION_TIMEFRAMES.forEach(tf => {
      const matched = profiles.filter(item => normalizePanelTimeframe(item?.timeframe, String(item?.timeframe || '').toUpperCase()) === tf);
      if (!matched.length) {
        errors.push(`${tf} timeframe profile がありません。`);
        return;
      }
      if (matched.length > 1) errors.push(`${tf} timeframe profile が重複しています。`);
      const value = matched[0]?.confirm_bars;
      if (value == null || value === '') {
        errors.push(`${tf} Confirm bars が未設定です。`);
      } else if (!Number.isInteger(Number(value))) {
        errors.push(`${tf} Confirm bars は整数で指定してください。`);
      } else if (Number(value) < min || Number(value) > max) {
        errors.push(`${tf} Confirm bars は ${min}〜${max} の範囲で指定してください。`);
      }
      if (!String(matched[0]?.source_mapping?.kind || '').trim()) errors.push(`${tf} source_mapping.kind が未設定です。`);
    });
    if (String(policy.inheritance || '').toLowerCase() !== 'forbidden') errors.push('Confirm bars inheritance は forbidden である必要があります。');
    if (String(policy.calculation_from_other_timeframes || '').toLowerCase() !== 'forbidden') errors.push('他時間足からのConfirm bars計算は禁止設定である必要があります。');
    if (String(policy.implicit_default || '').toLowerCase() !== 'forbidden') errors.push('暗黙Defaultは禁止設定である必要があります。');
    if (String(policy.implicit_fallback || '').toLowerCase() !== 'forbidden') errors.push('暗黙Fallbackは禁止設定である必要があります。');
    const syncPolicy = draft?.time_sync_policy || {};
    if (String(syncPolicy.reference_axis || '').toUpperCase() !== 'M5_CLOSE') errors.push('time_sync_policy.reference_axis は M5_CLOSE である必要があります。');
    if (!String(syncPolicy.dataset_timezone || '').trim()) errors.push('time_sync_policy.dataset_timezone が未設定です。');
    if (!String(syncPolicy.runtime_interpretation || '').trim()) errors.push('time_sync_policy.runtime_interpretation が未設定です。');
    if (String(syncPolicy.future_rows || '').toLowerCase() !== 'exclude') errors.push('未来足は exclude 設定である必要があります。');
    if (String(syncPolicy.missing_bars || '').toLowerCase() !== 'do_not_fill') errors.push('欠損バーは暗黙補完せず do_not_fill とする必要があります。');
    const swingPolicy = draft?.swing_point_policy || {};
    if (String(swingPolicy.detector_id || '') !== SHARED_SWING_POINT_DETECTOR_ID) errors.push(`swing_point_policy.detector_id は ${SHARED_SWING_POINT_DETECTOR_ID} である必要があります。`);
    if (String(swingPolicy.timeframe_specific_class || '').toLowerCase() !== 'forbidden') errors.push('時間足ごとの専用Swing Point Detectorクラスは禁止設定である必要があります。');
    if (swingPolicy.no_lookahead !== true) errors.push('Swing Point Detectorのno_lookaheadはtrueである必要があります。');
    if (String(swingPolicy.confirm_bars_source || '') !== 'timeframe_profiles[].confirm_bars') errors.push('Swing Point Detectorは各時間足Profileの明示Confirm barsを使用する必要があります。');
    const dowPolicy = draft?.dow_trend_policy || {};
    if (String(dowPolicy.evaluator_id || '') !== DOW_TREND_EVALUATOR_ID) errors.push(`dow_trend_policy.evaluator_id は ${DOW_TREND_EVALUATOR_ID} である必要があります。`);
    if (dowPolicy.confirmed_points_only !== true) errors.push('Dow Trend Evaluatorは確定済みSwing Pointだけを使用する必要があります。');
    if (String(dowPolicy.pending_candidate_usage || '').toLowerCase() !== 'forbidden') errors.push('未確定Swing CandidateのDow判定利用は禁止設定である必要があります。');
    if (String(dowPolicy.timeframe_specific_class || '').toLowerCase() !== 'forbidden') errors.push('時間足ごとの専用Dow Evaluatorクラスは禁止設定である必要があります。');
    if (String(dowPolicy.entry_permission_output || '').toLowerCase() !== 'forbidden') errors.push('Dow Trend EvaluatorはEntry Permissionを出力してはいけません。');
    if (dowPolicy.state_change_event_only !== true) errors.push('Dow TrendState変更Eventは状態変更時だけ出力する必要があります。');
    if (dowPolicy.confirmation_event_enabled !== true) errors.push('v0.14通常EntryにはDow Confirmation Event出力が必要です。');
    if (!['each_complete_directional_structure_pair_advance', 'M5: confirmed pullback/return then prior structure high/low breakout on confirmed bar; other timeframes: complete directional structure pair advance', 'M5 confirmed pullback/return then prior structure high/low breakout; other TF complete directional structure pair advance'].includes(String(dowPolicy.confirmation_event_policy || ''))) errors.push('Dow Confirmation Event Policyは、M5構造突破確認または旧互換の完全構造ペア確認を明示する必要があります。');
    if (dowPolicy.no_lookahead !== true) errors.push('Dow Trend Evaluatorのno_lookaheadはtrueである必要があります。');
    const cyclePolicy = draft?.cycle_position_policy || {};
    if (String(cyclePolicy.evaluator_id || '') !== CYCLE_POSITION_EVALUATOR_ID) errors.push(`cycle_position_policy.evaluator_id は ${CYCLE_POSITION_EVALUATOR_ID} である必要があります。`);
    if (String(cyclePolicy.origin_selection || '') !== 'latest_confirmed_usable_swing') errors.push('Cycle originはlatest_confirmed_usable_swingである必要があります。');
    if (String(cyclePolicy.candidate_usage || '').toLowerCase() !== 'forbidden') errors.push('未確定Swing CandidateのCycle origin利用は禁止設定である必要があります。');
    if (String(cyclePolicy.retired_usage_for_current_origin || '').toLowerCase() !== 'forbidden') errors.push('Retired Swingを現在Cycle originとして利用してはいけません。');
    if (cyclePolicy.historical_retired_origin_replay !== true) errors.push('過去にActiveだったRetired Swingは履歴再生対象として保持する必要があります。');
    if (String(cyclePolicy.timeframe_specific_class || '').toLowerCase() !== 'forbidden') errors.push('時間足ごとの専用Cycle Evaluatorクラスは禁止設定である必要があります。');
    if (String(cyclePolicy.phase_threshold_source || '') !== 'timeframe_profiles[].cycle.phase_thresholds') errors.push('Cycle Phase閾値は各時間足Profileの明示設定を使用する必要があります。');
    if (String(cyclePolicy.action_permission_output || '').toLowerCase() !== 'forbidden') errors.push('Cycle Position EvaluatorはAction Permissionを出力してはいけません。');
    if (cyclePolicy.origin_change_event !== true || cyclePolicy.phase_change_event !== true) errors.push('Cycle origin変更とphase変更はTrace Eventへ出力する必要があります。');
    if (cyclePolicy.no_lookahead !== true) errors.push('Cycle Position Evaluatorのno_lookaheadはtrueである必要があります。');
    const hsiPolicy = draft?.hsi_anchor_policy || {};
    if (String(hsiPolicy.registry_id || '') !== HSI_ANCHOR_REGISTRY_ID) errors.push(`hsi_anchor_policy.registry_id は ${HSI_ANCHOR_REGISTRY_ID} である必要があります。`);
    if (String(hsiPolicy.resolver_id || '') !== HSI_ANCHOR_RESOLVER_ID) errors.push(`hsi_anchor_policy.resolver_id は ${HSI_ANCHOR_RESOLVER_ID} である必要があります。`);
    if (String(hsiPolicy.timeframe_specific_class || '').toLowerCase() !== 'forbidden') errors.push('時間足ごとの専用HSI Anchor Registry/Resolverクラスは禁止設定である必要があります。');
    if (String(hsiPolicy.source_type || '') !== SIMULATION_HSI_ANCHOR_SOURCE_TYPE) errors.push(`Simulation HSI Anchor source_type は ${SIMULATION_HSI_ANCHOR_SOURCE_TYPE} である必要があります。`);
    if (String(hsiPolicy.human_saved_hsi_source_type || '') !== SAVED_HSI_SOURCE_TYPE) errors.push(`Human Saved HSI source_type は ${SAVED_HSI_SOURCE_TYPE} である必要があります。`);
    if (String(hsiPolicy.candidate_usage || '') !== 'registry_only_not_resolvable') errors.push('未確定HSI Anchor CandidateはRegistry記録だけとし、Purpose Resolver利用は禁止する必要があります。');
    if (hsiPolicy.confirmed_active_eligibility !== true) errors.push('Confirmed Active Swing由来AnchorだけをPurpose Resolver候補にする必要があります。');
    if (hsiPolicy.retired_retention !== true) errors.push('Retired HSI Anchorは履歴追跡用に保持する必要があります。');
    if (hsiPolicy.status_role_separation !== true) errors.push('HSI AnchorのLifecycle statusとRoleは分離する必要があります。');
    if (String(hsiPolicy.action_permission_output || '').toLowerCase() !== 'forbidden') errors.push('HSI Anchor ResolverはAction Permissionを出力してはいけません。');
    if (hsiPolicy.no_lookahead !== true) errors.push('HSI Anchor Registry / Resolverのno_lookaheadはtrueである必要があります。');
    ['entry', 'hold', 'target', 'thesis', 'confluence'].forEach(purpose => {
      if (!String(hsiPolicy.purpose_resolvers?.[purpose] || '').trim()) errors.push(`hsi_anchor_policy.purpose_resolvers.${purpose} が未設定です。`);
    });
    const statePolicy = draft?.timeframe_state_policy || {};
    if (String(statePolicy.builder_id || '') !== TIMEFRAME_STATE_BUILDER_ID) errors.push(`timeframe_state_policy.builder_id は ${TIMEFRAME_STATE_BUILDER_ID} である必要があります。`);
    if (String(statePolicy.timeframe_specific_class || '').toLowerCase() !== 'forbidden') errors.push('時間足ごとの専用Timeframe State Builderクラスは禁止設定である必要があります。');
    if (statePolicy.source_event_ids_required !== true) errors.push('Timeframe Stateはsource_event_idsを必須とする必要があります。');
    if (statePolicy.data_sufficiency_separate_from_market_state !== true) errors.push('data_sufficiencyと相場状態は分離する必要があります。');
    if (String(statePolicy.action_permission_output || '').toLowerCase() !== 'forbidden') errors.push('Timeframe State BuilderはAction Permissionを出力してはいけません。');
    if (statePolicy.no_lookahead !== true) errors.push('Timeframe State Builderのno_lookaheadはtrueである必要があります。');
    const bbPolicy = statePolicy.bb_phase || {};
    if (!Number.isInteger(Number(bbPolicy.period)) || Number(bbPolicy.period) < 2) errors.push('timeframe_state_policy.bb_phase.period は2以上の整数である必要があります。');
    if (!(Number(bbPolicy.deviations) > 0)) errors.push('timeframe_state_policy.bb_phase.deviations は0より大きい数値である必要があります。');
    if (!Number.isInteger(Number(bbPolicy.lookback_bands)) || Number(bbPolicy.lookback_bands) < 5) errors.push('timeframe_state_policy.bb_phase.lookback_bands は5以上の整数である必要があります。');
    if (!(Number(bbPolicy.width_change_threshold_ratio) > 0)) errors.push('timeframe_state_policy.bb_phase.width_change_threshold_ratio は0より大きい数値である必要があります。');
    const upperPolicy = draft?.upper_context_decision_policy || {};
    if (String(upperPolicy.engine_id || '') !== UPPER_CONTEXT_DECISION_ENGINE_ID) errors.push(`upper_context_decision_policy.engine_id は ${UPPER_CONTEXT_DECISION_ENGINE_ID} である必要があります。`);
    if (String(upperPolicy.timeframe_specific_class || '').toLowerCase() !== 'forbidden') errors.push('時間足ごとの専用Upper Context Decisionクラスは禁止設定である必要があります。');
    if (String(upperPolicy.rule_evaluation || '') !== 'priority_ordered_specification_registry') errors.push('Upper Context Decisionはpriority_ordered_specification_registryで評価する必要があります。');
    if (upperPolicy.no_trade_priority !== true) errors.push('NoTrade / Block Ruleは許可Ruleより優先する必要があります。');
    if (String(upperPolicy.data_sufficiency_required_for_new_entry || '').toUpperCase() !== 'READY') errors.push('新規Entry探索には上位足Data Sufficiency READYを要求する必要があります。');
    if (upperPolicy.week_direct_close !== false) errors.push('WEEKは直接Closeしてはいけません。');
    if (upperPolicy.week_late_policy?.h1_exit_trigger_enabled !== true) errors.push('WEEK LateではH1 Exit Trigger監視を有効化する必要があります。');
    if (String(upperPolicy.action_execution_output || '').toLowerCase() !== 'forbidden') errors.push('Upper Context Decision EngineはM5売買実行を出力してはいけません。');
    if (upperPolicy.h1_exit_trigger_rule?.direct_close !== false) errors.push('H1 Exit Triggerは直接Close実行を行ってはいけません。');
    if (!(Number(upperPolicy.profit_take_arm_rule?.minimum_hsi_confluence_anchors) >= 1)) errors.push('Profit Take Armedのminimum_hsi_confluence_anchorsは1以上である必要があります。');
    if (upperPolicy.no_lookahead !== true) errors.push('Upper Context Decision Engineのno_lookaheadはtrueである必要があります。');
    const tracePolicy = draft?.trace_replay_policy || {};
    if (String(tracePolicy.engine_id || '') !== TRACE_REPLAY_ENGINE_ID) errors.push(`trace_replay_policy.engine_id は ${TRACE_REPLAY_ENGINE_ID} である必要があります。`);
    if (tracePolicy.append_only !== true) errors.push('Trace Replay Logは追記型である必要があります。');
    if (tracePolicy.full_state_per_event !== false) errors.push('各Eventへ全Stateを複製せず、差分Patchを使う必要があります。');
    if (tracePolicy.delta_patch_required !== true) errors.push('Trace Eventにはreplay_patchが必要です。');
    if (tracePolicy.dag_validation !== true) errors.push('caused_by_event_idsのDAG検査を有効にする必要があります。');
    if (String(tracePolicy.circular_cause_reference || '').toLowerCase() !== 'forbidden') errors.push('原因Eventの循環参照は禁止設定である必要があります。');
    if (!Number.isInteger(Number(tracePolicy.checkpoint_interval_events)) || Number(tracePolicy.checkpoint_interval_events) < 1) errors.push('checkpoint_interval_eventsは1以上の整数である必要があります。');
    if (tracePolicy.final_checkpoint_required !== true) errors.push('最終Checkpointを必須にする必要があります。');
    if (String(tracePolicy.ui_language || '').toLowerCase() !== 'ja') errors.push('Trace Replay UIは日本語表示を基本とする必要があります。');
    if (String(tracePolicy.action_execution_output || '').toLowerCase() !== 'forbidden') errors.push('Trace Replay Logは売買実行を出力してはいけません。');
    if (tracePolicy.no_lookahead !== true) errors.push('Trace Replay Logのno_lookaheadはtrueである必要があります。');
    const executionPolicy = draft?.m5_execution_policy || {};
    if (String(executionPolicy.engine_id || '') !== M5_EXECUTION_ENGINE_ID) errors.push(`m5_execution_policy.engine_id は ${M5_EXECUTION_ENGINE_ID} である必要があります。`);
    if (String(executionPolicy.mode || '') !== 'reference_point_step') errors.push('M5 Execution初期実装はreference_point_stepである必要があります。');
    if (String(executionPolicy.execution_timeframe || '').toUpperCase() !== 'M5') errors.push('売買実行時間足はM5である必要があります。');
    if (!ALLOWED_UPPER_DECISION_REIMPLEMENTATIONS.has(String(executionPolicy.upper_decision_reimplementation || '').toLowerCase())) errors.push('upper_decision_reimplementation は許可済み通常Entry例外を明示してください。');
    const lanePolicy = executionPolicy.rule_lane_policy || {};
    const activeRuleLane = String(lanePolicy.active_entry_rule_lane || '').toUpperCase();
    if (![RULE_LANE_NORMAL, RULE_LANE_EXPANSION_LITE, ENTRY_LANE_MODE_NORMAL_AND_EXPANSION_LITE, ENTRY_LANE_MODE_PARALLEL_RULE_LANES].includes(activeRuleLane)) errors.push('active_entry_rule_laneはNORMAL / EXPANSION_LITE / NORMAL_AND_EXPANSION_LITE / PARALLEL_RULE_LANESのいずれかである必要があります。');
    if (String(lanePolicy.shared_fact_source || '') !== 'TIMEFRAME_STATE_SNAPSHOT') errors.push('Rule Laneの共通観測入力はTIMEFRAME_STATE_SNAPSHOTである必要があります。');
    if (String(lanePolicy.close_lane_source || '') !== 'OPEN_TRADE_RULE_LANE') errors.push('Close判定はOPEN_TRADE_RULE_LANEから選択する必要があります。');
    if (String(lanePolicy.lanes?.NORMAL?.entry_evaluator_id || '') !== NORMAL_ENTRY_EVALUATOR_ID) errors.push(`NORMAL Entry Evaluatorは${NORMAL_ENTRY_EVALUATOR_ID}である必要があります。`);
    if (String(lanePolicy.lanes?.NORMAL?.close_evaluator_id || '') !== NORMAL_CLOSE_EVALUATOR_ID) errors.push(`NORMAL Close Evaluatorは${NORMAL_CLOSE_EVALUATOR_ID}である必要があります。`);
    if (String(lanePolicy.lanes?.EXPANSION_LITE?.entry_evaluator_id || '') !== EXPANSION_LITE_ENTRY_EVALUATOR_ID) errors.push(`EXPANSION_LITE Entry Evaluatorは${EXPANSION_LITE_ENTRY_EVALUATOR_ID}である必要があります。`);
    if (String(lanePolicy.lanes?.EXPANSION_LITE?.close_evaluator_id || '') !== EXPANSION_LITE_CLOSE_EVALUATOR_ID) errors.push(`EXPANSION_LITE Close Evaluatorは${EXPANSION_LITE_CLOSE_EVALUATOR_ID}である必要があります。`);
    if (lanePolicy.lanes?.EXPANSION?.enabled !== false) errors.push('未実装のEXPANSION Rule Laneは無効である必要があります。');
    if (activeRuleLane === RULE_LANE_NORMAL) {
      if (lanePolicy.lanes?.NORMAL?.enabled !== true) errors.push('NORMAL ProfileではNORMAL Rule Laneだけを有効にする必要があります。');
      if (lanePolicy.lanes?.EXPANSION_LITE?.enabled !== false) errors.push('NORMAL ProfileへEXPANSION_LITE Rule Laneを混ぜてはいけません。');
    }
    if (activeRuleLane === RULE_LANE_EXPANSION_LITE) {
      if (lanePolicy.lanes?.NORMAL?.enabled !== false) errors.push('EXPANSION_LITE専用ProfileではNORMAL Rule Laneを無効にしてください。');
      if (lanePolicy.lanes?.EXPANSION_LITE?.enabled !== true) errors.push('EXPANSION_LITE ProfileではEXPANSION_LITE Rule Laneを有効にする必要があります。');
      const lite = executionPolicy.expansion_lite_policy || {};
      if (String(lite.rule_version || '') !== EXPANSION_LITE_RULE_VERSION) errors.push(`Expansion-Lite rule_versionは${EXPANSION_LITE_RULE_VERSION}である必要があります。`);
      if (lite.day_cycle_position_required !== false) errors.push('Expansion-LiteではDayサイクル位置条件を使用しません。');
      if (String(lite.h1_cycle_entry_allowed_max_bars_source || '') !== 'timeframe_profiles[H1].cycle.entry_allowed_max_bars') errors.push('Expansion-LiteのH1 Entry許可本数はH1 Profileのcycle.entry_allowed_max_barsを使用してください。');
      if (Number(lite.entry_raw) !== 144 || String(lite.entry_label || '').toUpperCase() !== 'R3') errors.push('Expansion-Lite EntryはR3タッチです。');
      const addOnLabels = (lite.add_on_levels || []).map(item => String(item?.label || '').toUpperCase()).join(',');
      if (addOnLabels !== 'R3.5,R4,R4.5') errors.push('Expansion-Lite Add-onはR3.5 / R4 / R4.5に限定します。');
      if (Number(lite.target_raw) !== 377 || String(lite.target_label || '').toUpperCase() !== 'R5') errors.push('Expansion-Lite TargetはR5です。');
      if (String(lite.other_rule_lane_fallback || '').toUpperCase() !== 'FORBIDDEN') errors.push('Expansion-Liteから他Rule LaneへのFallbackは禁止です。');
    }
    if ([ENTRY_LANE_MODE_NORMAL_AND_EXPANSION_LITE, ENTRY_LANE_MODE_PARALLEL_RULE_LANES].includes(activeRuleLane)) {
      if (lanePolicy.lanes?.NORMAL?.enabled !== true) errors.push('並列実行ProfileではNORMAL Rule Laneを有効にする必要があります。');
      if (lanePolicy.lanes?.EXPANSION_LITE?.enabled !== true) errors.push('並列実行ProfileではEXPANSION_LITE Rule Laneを有効にする必要があります。');
      if (String(lanePolicy.cross_lane_condition_sharing || '').toUpperCase() !== 'FORBIDDEN') errors.push('並列実行でもRule Lane間の条件流用は禁止です。');
      if (activeRuleLane === ENTRY_LANE_MODE_PARALLEL_RULE_LANES) {
        if (lanePolicy.parallel_entry_enabled !== true) errors.push('PARALLEL_RULE_LANESではparallel_entry_enabled=trueが必要です。');
        if (String(lanePolicy.simultaneous_entry_policy || '').toUpperCase() !== 'ALLOW_ALL_MATCHED_LANES') errors.push('同一足で成立した全Rule LaneのEntryを許可してください。');
      }
    }
    const normalEntryPolicy = executionPolicy.normal_entry_policy || {};
    if (!['v0.6', 'v0.6.1', 'v0.7', 'v0.8', 'v0.9', 'v0.10', 'v0.11', 'v0.12', 'v0.13', 'v0.14', 'v0.15', 'v0.16', 'v0.17', 'v0.17.1', 'v0.23', 'v0.24'].includes(String(normalEntryPolicy.rule_version || ''))) errors.push('通常M5 Entryはnormal_entry_policy.rule_version=v0.6〜v0.24の許可済み値を明示してください。');
    if (normalEntryPolicy.h4_dow_required !== false) errors.push('通常EntryではH4 Dowを必須条件にしません。');
    if (['v0.8', 'v0.9', 'v0.10', 'v0.11', 'v0.12', 'v0.13', 'v0.14', 'v0.15', 'v0.16', 'v0.17', 'v0.17.1', 'v0.23', 'v0.24'].includes(String(normalEntryPolicy.rule_version || ''))) {
      if (normalEntryPolicy.h1_dow_required !== false) errors.push('v0.8/v0.9通常EntryではH1 Dowを必須条件にしません。');
      if (normalEntryPolicy.h1_t3_required !== true) errors.push('v0.8/v0.9通常EntryではH1 T3方向と終値位置を必須にします。');
      if (normalEntryPolicy.m5_dow_required !== true) errors.push('v0.8/v0.9通常EntryではM5 Dowを実行トリガーとして必須にします。');
      if (normalEntryPolicy.h1_m5_dow_match_required !== false) errors.push('v0.8/v0.9通常EntryではH1/M5 Dow一致を要求しません。');
      if (String(normalEntryPolicy.rule_version || '') === 'v0.9') {
        if (normalEntryPolicy.new_swing_replaces_anchor !== false) errors.push('v0.9通常Entryでは同方向Dow継続中の新しいSwingでHSI起点を変更しません。');
        if (normalEntryPolicy.opposite_direction_dow_replaces_anchor !== true) errors.push('v0.9通常Entryでは反対方向Dow成立時だけHSI起点を更新します。');
        if (normalEntryPolicy.expansion_uses_separate_entry_anchor !== true) errors.push('v0.9ではExpansion Entry起点を通常Dow起点と分離します。');
      }
      if (String(normalEntryPolicy.rule_version || '') === 'v0.12') {
        if (String(normalEntryPolicy.entry_trigger || '') !== 'FIRST_R2_TOUCH_AFTER_DOW_CONFIRMATION') errors.push('v0.12通常EntryはDow確認Event後のR2初回到達をEntry Triggerにする必要があります。');
        if (Number(normalEntryPolicy.entry_raw) !== 89 || String(normalEntryPolicy.entry_label || '').toUpperCase() !== 'R2') errors.push('v0.12通常EntryはR2（raw=89）でEntryする必要があります。');
        if (Number(normalEntryPolicy.target_raw) !== 117 || String(normalEntryPolicy.target_label || '').toUpperCase() !== 'R2.5') errors.push('v0.12通常EntryはR2.5（raw=117）で全Closeする必要があります。');
        if (normalEntryPolicy.one_entry_opportunity_per_dow_confirmation !== true) errors.push('v0.12は1 Dow Confirmation IDにつき通常Entry機会を最大1回に制限する必要があります。');
        if (String(normalEntryPolicy.late_entry_after_r2 || '').toUpperCase() !== 'FORBIDDEN') errors.push('v0.12ではR2通過後の遅れEntryを禁止する必要があります。');
        if (normalEntryPolicy.reentry_requires_new_dow_confirmation_after_close !== true) errors.push('v0.12のReEntryには前Trade終了後の新しいDow確認Eventを必須にする必要があります。');
        if (normalEntryPolicy.same_confirmation_reuse_for_reentry !== false) errors.push('v0.12では同じDow確認IDをReEntryへ再利用してはいけません。');
      }
      if (String(normalEntryPolicy.rule_version || '') === 'v0.13') {
        if (String(normalEntryPolicy.entry_trigger || '') !== 'DOW_CONFIRMATION_IF_R2_READY_ELSE_FIRST_R2_TOUCH') errors.push('v0.13通常EntryはDow確認時にR2到達状態を判定し、未到達時だけR2初回到達を待つ必要があります。');
        if (Number(normalEntryPolicy.entry_raw) !== 89 || String(normalEntryPolicy.entry_label || '').toUpperCase() !== 'R2') errors.push('v0.13通常Entryの最低到達水準はR2（raw=89）です。');
        if (Number(normalEntryPolicy.target_raw) !== 117 || String(normalEntryPolicy.target_label || '').toUpperCase() !== 'R2.5') errors.push('v0.13通常EntryはR2.5（raw=117）で全Closeする必要があります。');
        if (normalEntryPolicy.one_entry_opportunity_per_dow_confirmation !== true) errors.push('v0.13は1 Dow Confirmation IDにつき通常Entry機会を最大1回に制限する必要があります。');
        if (String(normalEntryPolicy.r2_ready_at_confirmation || '').toUpperCase() !== 'IMMEDIATE_ENTRY_BEFORE_R2_5') errors.push('v0.13ではDow確認時にR2到達済みかつR2.5未到達なら即Entryする必要があります。');
        if (String(normalEntryPolicy.target_already_reached_at_confirmation || '').toUpperCase() !== 'MISSED') errors.push('v0.13ではDow確認時にR2.5到達済みなら通常Entryを見送る必要があります。');
        if (normalEntryPolicy.reentry_requires_new_dow_confirmation_after_close !== true) errors.push('v0.13のReEntryには前Trade終了後の新しいDow確認Eventを必須にする必要があります。');
        if (normalEntryPolicy.same_confirmation_reuse_for_reentry !== false) errors.push('v0.13では同じDow確認IDをReEntryへ再利用してはいけません。');
      }
      if (String(normalEntryPolicy.rule_version || '') === 'v0.14') {
        if (String(normalEntryPolicy.entry_trigger || '') !== 'DOW_BREAKOUT_CONFIRMATION_IF_R2_READY_ELSE_FIRST_R2_TOUCH') errors.push('v0.14通常EntryはM5構造高値/安値の突破確認をDow Confirmation Eventにする必要があります。');
        if (Number(normalEntryPolicy.entry_raw) !== 89 || String(normalEntryPolicy.entry_label || '').toUpperCase() !== 'R2') errors.push('v0.14通常Entryの最低到達水準はR2（raw=89）です。');
        if (String(normalEntryPolicy.target_policy || '') !== 'NEXT_HSI_BOUNDARY_FROM_ENTRY_DISTANCE') errors.push('v0.14通常EntryはEntry地点より先の次HSI境界を全Close Targetにする必要があります。');
        if (normalEntryPolicy.one_entry_opportunity_per_dow_confirmation !== true) errors.push('v0.14は1 Dow Confirmation IDにつき通常Entry機会を最大1回に制限する必要があります。');
        if (String(normalEntryPolicy.r2_ready_at_confirmation || '') !== 'IMMEDIATE_ENTRY_AT_CONFIRMATION_PRICE') errors.push('v0.14ではDow突破確認時にR2以上なら確認価格で即Entryする必要があります。');
        if (normalEntryPolicy.reentry_requires_new_dow_confirmation_after_close !== true) errors.push('v0.14のReEntryには前Trade終了後の新しいM5 Dow突破確認Eventを必須にする必要があります。');
        if (normalEntryPolicy.same_confirmation_reuse_for_reentry !== false) errors.push('v0.14では同じDow確認IDをReEntryへ再利用してはいけません。');
      }
      if (String(normalEntryPolicy.rule_version || '') === 'v0.15') {
        if (String(normalEntryPolicy.entry_trigger || '') !== 'DOW_BREAKOUT_CONFIRMATION_IF_R2_READY_ELSE_FIRST_R2_TOUCH') errors.push('v0.15通常EntryはM5構造高値/安値の突破確認をDow Confirmation Eventにする必要があります。');
        if (Number(normalEntryPolicy.entry_raw) !== 89 || String(normalEntryPolicy.entry_label || '').toUpperCase() !== 'R2') errors.push('v0.15通常Entryの最低到達水準はR2（raw=89）です。');
        if (String(normalEntryPolicy.target_policy || '') !== 'NEXT_HSI_BOUNDARY_FROM_ENTRY_DISTANCE') errors.push('v0.15通常EntryはEntry地点より先の次HSI境界を全Close Targetにする必要があります。');
        if (normalEntryPolicy.one_entry_opportunity_per_dow_confirmation !== true) errors.push('v0.15は1 Dow Confirmation IDにつき通常Entry機会を最大1回に制限する必要があります。');
        if (String(normalEntryPolicy.r2_ready_at_confirmation || '') !== 'IMMEDIATE_ENTRY_AT_CONFIRMATION_PRICE') errors.push('v0.15ではDow突破確認時にR2以上なら確認価格で即Entryする必要があります。');
        if (normalEntryPolicy.next_normal_entry_requires_new_dow_confirmation_after_previous_close !== true) errors.push('v0.15の次回通常Entryには前Trade終了後の新しいM5 Dow突破確認Eventを必須にする必要があります。');
        if (normalEntryPolicy.same_confirmation_reuse_for_next_normal_entry !== false) errors.push('v0.15では同じDow確認IDを次回通常Entryへ再利用してはいけません。');
        if (String(normalEntryPolicy.normal_reentry_concept || '') !== 'NOT_DEFINED') errors.push('v0.15のNORMAL Rule LaneにはReEntry概念を定義しません。');
        if (String(normalEntryPolicy.normal_add_on_concept || '') !== 'FORBIDDEN') errors.push('v0.15のNORMAL Rule LaneではAdd-onを禁止します。');
        if (JSON.stringify(normalEntryPolicy.applies_to || []) !== JSON.stringify(['ENTRY'])) errors.push('v0.15の通常Entry PolicyはENTRYだけへ適用してください。');
        const normalLaneActions = (lanePolicy.lanes?.NORMAL?.allowed_actions || []).map(value => String(value).toUpperCase());
        if (normalLaneActions.includes('REENTRY') || normalLaneActions.includes('ADD_ON')) errors.push('NORMAL Rule Laneのallowed_actionsへREENTRY / ADD_ONを含めてはいけません。');
        if (!['ENTRY', 'FULL_CLOSE', 'STOP_CLOSE'].every(value => normalLaneActions.includes(value))) errors.push('NORMAL Rule LaneはENTRY / FULL_CLOSE / STOP_CLOSEを許可する必要があります。');
      }
      if (String(normalEntryPolicy.rule_version || '') === 'v0.16') {
        if (String(normalEntryPolicy.entry_trigger || '') !== 'DOW_BREAKOUT_CONFIRMATION_IF_R2_READY_ELSE_FIRST_R2_TOUCH') errors.push('v0.16通常EntryはM5構造高値/安値の突破確認をDow Confirmation Eventにする必要があります。');
        if (Number(normalEntryPolicy.entry_raw) !== 89 || String(normalEntryPolicy.entry_label || '').toUpperCase() !== 'R2') errors.push('v0.16通常Entryの最低到達水準はR2（raw=89）です。');
        if (String(normalEntryPolicy.target_policy || '') !== 'NEXT_HSI_BOUNDARY_FROM_ENTRY_DISTANCE') errors.push('v0.16通常EntryはEntry地点より先の次HSI境界を全Close Targetにする必要があります。');
        if (normalEntryPolicy.one_entry_opportunity_per_dow_confirmation !== true) errors.push('v0.16は1 Dow Confirmation IDにつき通常Entry機会を最大1回に制限する必要があります。');
        if (String(normalEntryPolicy.r2_ready_at_confirmation || '') !== 'IMMEDIATE_ENTRY_AT_FIRST_PRICE_SATISFYING_DOW_BREAKOUT_AND_R2') errors.push('v0.16ではDow突破確認時に、突破閾値とR2の双方を満たす最初の価格でEntryする必要があります。');
        if (String(normalEntryPolicy.entry_execution_price_policy || '') !== 'DOW_BREAKOUT_THRESHOLD_OR_R2_WHICHEVER_IS_FARTHER_FROM_ANCHOR_ELSE_FIRST_AVAILABLE_GAP_PRICE') errors.push('v0.16ではEntry価格をDow突破閾値とR2のうち起点から遠い方へ固定する必要があります。');
        if (normalEntryPolicy.next_normal_entry_requires_new_dow_confirmation_after_previous_close !== true) errors.push('v0.16の次回通常Entryには前Trade終了後の新しいM5 Dow突破確認Eventを必須にする必要があります。');
        if (normalEntryPolicy.same_confirmation_reuse_for_next_normal_entry !== false) errors.push('v0.16では同じDow確認IDを次回通常Entryへ再利用してはいけません。');
        if (String(normalEntryPolicy.normal_reentry_concept || '') !== 'NOT_DEFINED') errors.push('v0.16のNORMAL Rule LaneにはReEntry概念を定義しません。');
        if (String(normalEntryPolicy.normal_add_on_concept || '') !== 'FORBIDDEN') errors.push('v0.16のNORMAL Rule LaneではAdd-onを禁止します。');
        if (JSON.stringify(normalEntryPolicy.applies_to || []) !== JSON.stringify(['ENTRY'])) errors.push('v0.16の通常Entry PolicyはENTRYだけへ適用してください。');
        const normalLaneActions = (lanePolicy.lanes?.NORMAL?.allowed_actions || []).map(value => String(value).toUpperCase());
        if (normalLaneActions.includes('REENTRY') || normalLaneActions.includes('ADD_ON')) errors.push('NORMAL Rule Laneのallowed_actionsへREENTRY / ADD_ONを含めてはいけません。');
        if (!['ENTRY', 'FULL_CLOSE', 'STOP_CLOSE'].every(value => normalLaneActions.includes(value))) errors.push('NORMAL Rule LaneはENTRY / FULL_CLOSE / STOP_CLOSEを許可する必要があります。');
      }
      if (['v0.17', 'v0.17.1', 'v0.23', 'v0.24'].includes(String(normalEntryPolicy.rule_version || ''))) {
        if (['v0.17.1', 'v0.23', 'v0.24'].includes(String(normalEntryPolicy.rule_version || ''))) {
          if (JSON.stringify(normalEntryPolicy.cycle_late_guard_timeframes || []) !== JSON.stringify(['H1'])) errors.push('v0.17.1通常EntryのCycle Late GuardはH1だけに適用してください。');
        }
        if (String(normalEntryPolicy.entry_trigger || '') !== 'DOW_BREAKOUT_CONFIRMATION_IF_R2_READY_ELSE_FIRST_R2_TOUCH') errors.push('v0.17/v0.17.1/v0.23/v0.24通常EntryはM5構造高値/安値の突破確認をDow Confirmation Eventにする必要があります。');
        if (Number(normalEntryPolicy.entry_raw) !== 89 || String(normalEntryPolicy.entry_label || '').toUpperCase() !== 'R2') errors.push('v0.17/v0.17.1/v0.23/v0.24通常Entryの最低到達水準はR2（raw=89）です。');
        if (String(normalEntryPolicy.target_policy || '') !== 'NEXT_HSI_BOUNDARY_FROM_ENTRY_DISTANCE') errors.push('v0.17/v0.17.1/v0.23/v0.24通常EntryはEntry地点より先の次HSI境界を全Close Targetにする必要があります。');
        if (normalEntryPolicy.one_entry_opportunity_per_dow_confirmation !== true) errors.push('v0.17は1 Dow Confirmation IDにつき通常Entry機会を最大1回に制限する必要があります。');
        if (String(normalEntryPolicy.r2_ready_at_confirmation || '') !== 'IMMEDIATE_ENTRY_AT_FIRST_PRICE_SATISFYING_DOW_BREAKOUT_AND_R2') errors.push('v0.17/v0.17.1/v0.23/v0.24ではDow突破確認時に、突破閾値とR2の双方を満たす最初の価格でEntryする必要があります。');
        if (String(normalEntryPolicy.entry_execution_price_policy || '') !== 'DOW_BREAKOUT_THRESHOLD_OR_R2_WHICHEVER_IS_FARTHER_FROM_ANCHOR_ELSE_FIRST_AVAILABLE_GAP_PRICE') errors.push('v0.17/v0.17.1/v0.23/v0.24ではEntry価格をDow突破閾値とR2のうち起点から遠い方へ固定する必要があります。');
        if (normalEntryPolicy.next_normal_entry_requires_new_dow_confirmation_after_previous_close !== true) errors.push('v0.17/v0.17.1/v0.23/v0.24の次回通常Entryには前Trade終了後の新しいM5 Dow突破確認Eventを必須にする必要があります。');
        if (normalEntryPolicy.same_confirmation_reuse_for_next_normal_entry !== false) errors.push('v0.17/v0.17.1/v0.23/v0.24では同じDow確認IDを次回通常Entryへ再利用してはいけません。');
        const expectedNormalAnchorLifecycle = String(normalEntryPolicy.rule_version || '') === 'v0.24'
          ? 'DOW_CONFIRMATION_TO_PRE_ENTRY_BREAK_OR_TRADE_CLOSE' : 'DOW_CONFIRMATION_TO_TRADE_CLOSE';
        if (String(normalEntryPolicy.normal_hsi_anchor_lifecycle || '') !== expectedNormalAnchorLifecycle) errors.push('通常HSI起点LifecycleがRule Version契約と一致しません。');
        if (normalEntryPolicy.normal_hsi_anchor_retired_on_close !== true) errors.push('v0.17/v0.17.1/v0.23/v0.24ではNormal Close時に通常HSI起点を即破棄する必要があります。');
        if (normalEntryPolicy.normal_hsi_anchor_reuse_after_close !== false) errors.push('v0.17/v0.17.1/v0.23/v0.24ではClose済み通常HSI起点を次回Entryへ再利用してはいけません。');
        const expectedNextNormalAnchorSource = String(normalEntryPolicy.rule_version || '') === 'v0.24'
          ? 'FIRST_NEW_M5_DOW_CONFIRMATION_AFTER_BREAK_OR_CLOSE_PREVIOUS_SWING'
          : 'FIRST_NEW_M5_DOW_CONFIRMATION_AFTER_CLOSE_PREVIOUS_SWING';
        if (String(normalEntryPolicy.next_normal_hsi_anchor_source || '') !== expectedNextNormalAnchorSource) errors.push('次回通常HSI起点の採用元がRule Version契約と一致しません。');
        if (String(normalEntryPolicy.normal_reentry_concept || '') !== 'NOT_DEFINED') errors.push('v0.17/v0.17.1/v0.23/v0.24のNORMAL Rule LaneにはReEntry概念を定義しません。');
        if (String(normalEntryPolicy.normal_add_on_concept || '') !== 'FORBIDDEN') errors.push('v0.17/v0.17.1/v0.23/v0.24のNORMAL Rule LaneではAdd-onを禁止します。');
        if (JSON.stringify(normalEntryPolicy.applies_to || []) !== JSON.stringify(['ENTRY'])) errors.push('v0.17/v0.17.1/v0.23/v0.24の通常Entry PolicyはENTRYだけへ適用してください。');
        const normalLaneActions = (lanePolicy.lanes?.NORMAL?.allowed_actions || []).map(value => String(value).toUpperCase());
        if (normalLaneActions.includes('REENTRY') || normalLaneActions.includes('ADD_ON')) errors.push('NORMAL Rule Laneのallowed_actionsへREENTRY / ADD_ONを含めてはいけません。');
        if (!['ENTRY', 'FULL_CLOSE', 'STOP_CLOSE'].every(value => normalLaneActions.includes(value))) errors.push('NORMAL Rule LaneはENTRY / FULL_CLOSE / STOP_CLOSEを許可する必要があります。');
        if (String(normalEntryPolicy.rule_version || '') === 'v0.23') {
          if (normalEntryPolicy.pre_entry_dow_structure_break_expires_opportunity !== true) errors.push('v0.23ではEntry前のM5 Dow構造崩壊でWAITING_R2 Opportunityを失効させる必要があります。');
          if (String(normalEntryPolicy.pre_entry_dow_structure_break_policy || '') !== 'NEWER_OPPOSITE_DOW_CONFIRMATION_ONLY') errors.push('v0.23.1ではEntry前Dow崩壊を後発の逆方向M5 Dow Confirmation成立時だけに限定してください。');
          const breakStates = (normalEntryPolicy.pre_entry_dow_structure_break_states || []).map(value => String(value).toUpperCase());
          if (breakStates.length !== 0) errors.push('v0.23.1ではREVERSAL_WATCH / NO_TREND / UNDETERMINEDをEntry Opportunity失効条件へ使用しないでください。');
          const guards = executionPolicy.entry_guard_policy || {};
          if (guards.normal_h4_same_direction_r4?.enabled !== true || Number(guards.normal_h4_same_direction_r4?.block_at_or_above_raw) !== 233) errors.push('v0.22〜v0.24のNORMAL H4同方向GuardはR4(raw=233)以上で有効にしてください。');
          if (guards.day_up_h4_down_r5_short?.enabled !== true || Number(guards.day_up_h4_down_r5_short?.block_at_or_above_raw) !== 377) errors.push('v0.21のDay Up / H4 Down Short GuardはR5(raw=377)以上で有効にしてください。');
          const closeMiss = executionPolicy.normal_close_miss_policy || {};
          if (String(closeMiss.strategy_id || '') !== 'target_distance_ratio_v0_1') errors.push('v0.23のNormal CloseMiss strategy_idはtarget_distance_ratio_v0_1である必要があります。');
          if (!(Number(closeMiss.max_loss_to_reward_ratio) > 0)) errors.push('v0.23のmax_loss_to_reward_ratioは0より大きい固定値である必要があります。');
          if (closeMiss.hsi_anchor_hard_limit !== true) errors.push('v0.23ではHSI起点をStopのHard Limitとして維持してください。');
          if (closeMiss.fix_price_at_entry !== true) errors.push('v0.23のNormal CloseMiss StopはEntry時に固定してください。');
        }
        if (String(normalEntryPolicy.rule_version || '') === 'v0.24') {
          if (normalEntryPolicy.pre_entry_dow_structure_break_expires_opportunity !== true) errors.push('v0.24ではEntry前の確定M5 Dow構造崩壊でWAITING_R2 Opportunityを失効させる必要があります。');
          if (String(normalEntryPolicy.pre_entry_dow_structure_break_policy || '') !== 'CONFIRMED_RESET_STATE_OR_NEWER_OPPOSITE_DOW_CONFIRMATION') errors.push('v0.24のEntry前Dow崩壊Policyは確定Reset Stateまたは後発逆方向Confirmationである必要があります。');
          const breakStates = (normalEntryPolicy.pre_entry_dow_structure_break_states || []).map(value => String(value).toUpperCase());
          if (JSON.stringify(breakStates) !== JSON.stringify(['REVERSAL_WATCH', 'NO_TREND', 'UNDETERMINED'])) errors.push('v0.24ではREVERSAL_WATCH / NO_TREND / UNDETERMINEDの確定遷移をEntry前Dow崩壊Stateとして明示してください。');
          if (String(normalEntryPolicy.normal_hsi_anchor_lifecycle || '') !== 'DOW_CONFIRMATION_TO_PRE_ENTRY_BREAK_OR_TRADE_CLOSE') errors.push('v0.24のNormal HSI Anchor LifecycleはEntry前Dow崩壊またはTrade Closeまでに限定してください。');
          if (String(normalEntryPolicy.next_normal_hsi_anchor_source || '') !== 'FIRST_NEW_M5_DOW_CONFIRMATION_AFTER_BREAK_OR_CLOSE_PREVIOUS_SWING') errors.push('v0.24の次Normal HSI起点はDow崩壊またはClose後の新Confirmationに属するprevious Swingから採用してください。');
          if (normalEntryPolicy.same_direction_dow_reconfirmation_replaces_anchor !== false) errors.push('v0.24では同一構造内の同方向継続だけでNormal HSI Anchorを更新してはいけません。');
          if (normalEntryPolicy.same_direction_reconfirmation_after_break_creates_new_anchor !== true) errors.push('v0.24では崩壊後の同方向Dow再確定を新Confirmation・新Anchorとして扱ってください。');
          if (normalEntryPolicy.dow_reconfirmation_point_is_anchor !== false) errors.push('v0.24ではDow再確定点そのものをNormal HSI Anchorにしてはいけません。');
          if (String(normalEntryPolicy.post_entry_dow_structure_break_close_policy || '') !== 'OBSERVE_ONLY_NO_CLOSE') errors.push('v0.24ではEntry後Dow崩壊を観測のみとし、単独でCloseしてはいけません。');
          if (String(normalEntryPolicy.post_entry_anchor_target_stop_policy || '') !== 'FIX_UNTIL_TRADE_CLOSE') errors.push('v0.24ではEntry後のAnchor / Target / StopをTrade Closeまで固定してください。');
          const guards = executionPolicy.entry_guard_policy || {};
          if (guards.normal_h4_same_direction_r4?.enabled !== true || Number(guards.normal_h4_same_direction_r4?.block_at_or_above_raw) !== 233) errors.push('v0.24のNORMAL H4同方向GuardはR4(raw=233)以上で有効にしてください。');
          const closeMiss = executionPolicy.normal_close_miss_policy || {};
          if (String(closeMiss.strategy_id || '') !== 'target_distance_ratio_v0_1' || !(Number(closeMiss.max_loss_to_reward_ratio) > 0) || closeMiss.hsi_anchor_hard_limit !== true || closeMiss.fix_price_at_entry !== true) errors.push('v0.24でもv0.23のJSON固定倍率Stop契約を維持してください。');
        }
      }
    } else if (normalEntryPolicy.h1_m5_dow_match_required !== true) errors.push('v0.6/v0.7通常EntryではH1/M5 Dow一致を必須にします。');
    if (executionPolicy.no_lookahead !== true) errors.push('M5 Executionのno_lookaheadはtrueである必要があります。');
    if (String(executionPolicy.real_order_output || '').toLowerCase() !== 'forbidden') errors.push('リアル注文出力は禁止設定である必要があります。');
    if (String(executionPolicy.money_management_output || '').toLowerCase() !== 'forbidden') errors.push('資金管理出力は禁止設定である必要があります。');
    if (String(executionPolicy.management_timeframe?.cap || '').toUpperCase() !== 'DAY') errors.push('Management Timeframe上限はDAYである必要があります。');
    if (executionPolicy.management_timeframe?.week_forbidden !== true) errors.push('Management TimeframeのWEEK昇格は禁止する必要があります。');
    if (String(executionPolicy.management_timeframe?.loss_avoidance_promotion || '').toLowerCase() !== 'forbidden') errors.push('損失先送り目的のManagement Timeframe昇格は禁止する必要があります。');
    const sizing = executionPolicy.position_sizing || {};
    const initialUnits = Number(sizing.initial_units);
    const coreUnits = Number(sizing.core_units);
    const runnerUnits = Number(sizing.runner_units);
    if (![initialUnits, coreUnits, runnerUnits].every(value => Number.isFinite(value) && value >= 0)) errors.push('Position unitsは0以上の数値で明示してください。');
    else if (coreUnits + runnerUnits !== initialUnits) errors.push('core_units + runner_units は initial_units と一致する必要があります。');
    if (['v0.7', 'v0.8', 'v0.9', 'v0.10', 'v0.11', 'v0.12', 'v0.13', 'v0.14', 'v0.15', 'v0.16', 'v0.17', 'v0.17.1', 'v0.23', 'v0.24'].includes(String(normalEntryPolicy.rule_version || ''))) {
      if (String(sizing.close_policy || '').toUpperCase() !== 'SINGLE_CLOSE') errors.push('v0.7以降のClose PolicyはSINGLE_CLOSEである必要があります。');
      if (runnerUnits !== 0) errors.push('v0.7以降の通常Entryではrunner_units=0である必要があります。');
      if (Number(sizing.partial_close_units || 0) !== 0) errors.push('v0.7以降の通常Entryではpartial_close_units=0である必要があります。');
      if (sizing.normal_add_on_allowed !== false) errors.push('v0.7以降の通常Add-onは禁止設定である必要があります。');
    }
    if (!(Number(executionPolicy.hsi_distance?.point_size) > 0)) errors.push('M5 Execution HSI point_sizeは0より大きい必要があります。');
    if (!(Number(executionPolicy.hsi_distance?.scale) > 0)) errors.push('M5 Execution HSI scaleは0より大きい必要があります。');
    if (!(Number(executionPolicy.hsi_distance?.entry_min_raw) >= 0)) errors.push('M5 Execution entry_min_rawは0以上である必要があります。');
    REQUIRED_SIMULATION_TIMEFRAMES.forEach(tf => {
      const profile = profiles.find(item => normalizePanelTimeframe(item?.timeframe, String(item?.timeframe || '').toUpperCase()) === tf);
      const cycle = profile?.cycle || {};
      const thresholds = cycle.phase_thresholds || {};
      const earlyMax = numberOrNull(thresholds.early_max_bars);
      const middleMax = numberOrNull(thresholds.middle_max_bars);
      const lateFrom = numberOrNull(thresholds.late_from_bars);
      if (String(cycle.origin_policy || '') !== 'latest_confirmed_usable_swing') errors.push(`${tf} cycle.origin_policy が未設定または不正です。`);
      const entryAllowedMaxBars = numberOrNull(cycle.entry_allowed_max_bars);
      if (!Number.isInteger(entryAllowedMaxBars) || entryAllowedMaxBars < 0) errors.push(`${tf} cycle.entry_allowed_max_bars は0以上の整数で明示してください。Confirm barsから計算してはいけません。`);
      if (![earlyMax, middleMax, lateFrom].every(Number.isInteger)) errors.push(`${tf} Cycle phase thresholdsは整数で明示してください。`);
      else {
        if (earlyMax < 0 || middleMax <= earlyMax || lateFrom !== middleMax + 1) errors.push(`${tf} Cycle thresholdsは 0<=early_max<middle_max かつ late_from=middle_max+1 である必要があります。`);
      }
      if (!String(cycle.context_role || '').trim()) errors.push(`${tf} cycle.context_role が未設定です。`);
      const map = cycle.context_state_map || {};
      ['EARLY', 'MIDDLE', 'LATE', 'UNDETERMINED'].forEach(phase => {
        if (!String(map[phase] || '').trim()) errors.push(`${tf} cycle.context_state_map.${phase} が未設定です。`);
      });
    });
    return { valid: errors.length === 0, errors, warnings, checked_at: nowLocalIso() };
  }

  function runtimeTimezoneSnapshot(referenceMs, policy = {}) {
    let runtimeTimeZone = 'unknown';
    try {
      runtimeTimeZone = Intl.DateTimeFormat().resolvedOptions().timeZone || 'unknown';
    } catch {
      runtimeTimeZone = 'unknown';
    }
    const d = new Date(referenceMs);
    return {
      dataset_timezone: String(policy.dataset_timezone || 'UNSPECIFIED_LOCAL_WALL_CLOCK'),
      runtime_interpretation: String(policy.runtime_interpretation || 'browser_local_time'),
      runtime_timezone: runtimeTimeZone,
      runtime_utc_offset_minutes: Number.isNaN(d.getTime()) ? null : -d.getTimezoneOffset()
    };
  }

  function normalizeRowsForSimulationTimeframe(rows, timeframe) {
    const tf = normalizePanelTimeframe(timeframe, 'M5');
    const durationMs = panelTimeframeMinutes(tf) * 60 * 1000;
    return (rows || []).map((row, index) => {
      const copy = { ...row };
      const startMs = numberOrNull(copy.start_ms) ?? rowTimeMs(copy);
      if (startMs != null) {
        copy.start_ms = startMs;
        copy.end_ms = numberOrNull(copy.end_ms) ?? (startMs + durationMs - 1);
      }
      copy.index = Math.max(0, Math.floor(numberOrNull(copy.index) ?? index));
      copy.row_no = Math.max(1, Math.floor(numberOrNull(copy.row_no) ?? (index + 1)));
      copy.timeframe = tf;
      return copy;
    }).filter(row => numberOrNull(row.start_ms) != null).sort((a, b) => a.start_ms - b.start_ms);
  }

  function simulationReferenceM5(state, preparedM5Rows = null) {
    // Range Simulationでは同じ全M5を各stepで再正規化しない。
    // simulationCandleSourceRowsのキャッシュ済みM5を受け取ることで、判定内容を変えずに連続実行を軽量化する。
    const allM5 = Array.isArray(preparedM5Rows) && preparedM5Rows.length
      ? preparedM5Rows
      : normalizeRowsForSimulationTimeframe(state?.simulationAllRows || [], 'M5');
    if (!allM5.length) return null;
    const source = state?.simulationSource;
    const visibleRows = source ? getChartWindowRows(source, state?.simulationAllRows || [], state) : [];
    const fallbackMs = rowTimeMs(visibleRows[visibleRows.length - 1]) ?? allM5[allM5.length - 1].start_ms;
    const contextReferenceMs = numberOrNull(state?.simulationRunReferenceOverrideMs);
    const syncReferenceMs = numberOrNull(state?.syncCenterTimeMs);
    const requestedMs = contextReferenceMs ?? syncReferenceMs ?? fallbackMs;
    const index = findIndexForTime(allM5, requestedMs);
    const row = index == null ? allM5[allM5.length - 1] : allM5[index];
    const referenceCloseMs = numberOrNull(row.end_ms) ?? (numberOrNull(row.start_ms) + panelTimeframeMinutes('M5') * 60 * 1000 - 1);
    return {
      source: contextReferenceMs != null ? 'm5_context_menu_reference' : syncReferenceMs != null ? 'chart_sync_center_m5' : 'current_chart_window_last_m5',
      requested_time_ms: requestedMs,
      requested_time: formatRowDateTime(requestedMs),
      row,
      reference_close_ms: referenceCloseMs,
      reference_close_time: formatRowDateTime(referenceCloseMs)
    };
  }

  function latestConfirmedBarAt(rows, referenceMs) {
    const list = rows || [];
    let lo = 0;
    let hi = list.length - 1;
    let latestIndex = -1;
    while (lo <= hi) {
      const mid = Math.floor((lo + hi) / 2);
      const row = list[mid];
      const startMs = numberOrNull(row?.start_ms) ?? rowTimeMs(row);
      const endMs = numberOrNull(row?.end_ms) ?? startMs;
      if (endMs != null && endMs <= referenceMs) {
        latestIndex = mid;
        lo = mid + 1;
      } else {
        hi = mid - 1;
      }
    }
    const latest = latestIndex >= 0 ? list[latestIndex] : null;
    const next = latestIndex + 1 < list.length ? list[latestIndex + 1] : null;
    const nextStart = numberOrNull(next?.start_ms) ?? rowTimeMs(next);
    const nextEnd = numberOrNull(next?.end_ms) ?? nextStart;
    const currentUnconfirmed = nextStart != null && nextEnd != null && nextStart <= referenceMs && referenceMs < nextEnd ? next : null;
    const futureRowsExcluded = Math.max(0, list.length - (latestIndex + 1));
    return { latest, latestIndex, currentUnconfirmed, futureRowsExcluded };
  }

  function summarizeSimulationCandle(row, timeframe, sourceRole) {
    if (!row) return null;
    const startMs = numberOrNull(row.start_ms) ?? rowTimeMs(row);
    const endMs = numberOrNull(row.end_ms) ?? startMs;
    return {
      timeframe,
      source_role: sourceRole,
      index: Math.max(0, Math.floor(numberOrNull(row.index) ?? 0)),
      row_no: Math.max(1, Math.floor(numberOrNull(row.row_no) ?? 1)),
      start_ms: startMs,
      end_ms: endMs,
      start_time: formatRowDateTime(startMs),
      end_time: formatRowDateTime(endMs),
      open: numberOrNull(row.open),
      high: rowHigh(row),
      low: rowLow(row),
      close: numberOrNull(row.close),
      t3_20_0_2: numberOrNull(row.t3_20_0_2),
      t3_slope: numberOrNull(row.t3_slope),
      t3_direction: String(row.t3_direction || ''),
      close_t3_diff: numberOrNull(row.close_t3_diff),
      close_t3_position: String(row.close_t3_position || ''),
      t3_ready: row.t3_ready === true || numberOrNull(row.t3_20_0_2) != null,
      source_row_start: numberOrNull(row.source_row_start),
      source_row_end: numberOrNull(row.source_row_end),
      confirmed_bar_key: `${timeframe}:${startMs}:${endMs}`
    };
  }

  function simulationProfileForTimeframe(draft, timeframe) {
    return (draft?.timeframe_profiles || []).find(item => normalizePanelTimeframe(item?.timeframe, String(item?.timeframe || '').toUpperCase()) === timeframe) || null;
  }

  function simulationCandleSourceRows(state) {
    const primaryRaw = state?.simulationAllRows || [];
    const dayRaw = state?.upperMapAllRows || [];
    const primaryLast = primaryRaw[primaryRaw.length - 1];
    const dayLast = dayRaw[dayRaw.length - 1];
    const cacheKey = `${primaryRaw.length}:${rowTimeMs(primaryLast) ?? '-'}|${dayRaw.length}:${rowTimeMs(dayLast) ?? '-'}`;
    let sourceRows = state?.simulationCandleSourceCache?.key === cacheKey
      ? state.simulationCandleSourceCache.rows
      : null;
    if (!sourceRows) {
      const primaryRows = normalizeRowsForSimulationTimeframe(primaryRaw, 'M5');
      const dayRows = normalizeRowsForSimulationTimeframe(dayRaw, 'DAY');
      sourceRows = {
        M5: primaryRows,
        H1: primaryRows.length ? buildUpperTimeframeRows(primaryRows, 'H1') : [],
        H4: primaryRows.length ? buildUpperTimeframeRows(primaryRows, 'H4') : [],
        DAY: dayRows,
        WEEK: dayRows.length ? buildUpperTimeframeRows(dayRows, 'WEEK') : []
      };
      state.simulationCandleSourceCache = { key: cacheKey, rows: sourceRows };
    }
    return sourceRows;
  }

  function buildMultiTimeframeCandleSyncSnapshot(state, draft) {
    const errors = [];
    const warnings = [];
    const sourceRows = simulationCandleSourceRows(state);
    const reference = simulationReferenceM5(state, sourceRows.M5);
    if (!reference) {
      return {
        schema_version: 'fx_multi_timeframe_candle_sync_snapshot_v0_1',
        kind: 'fx_multi_timeframe_candle_sync_snapshot',
        status: 'invalid',
        errors: ['M5 reference candle could not be resolved.'],
        warnings,
        timeframes: {}
      };
    }
    if (!sourceRows.M5.length) errors.push('Primary M5 rows are unavailable.');
    if (!sourceRows.DAY.length) errors.push('UpperMap DAY rows are unavailable. Synchronizer does not use M5-derived DAY fallback.');
    const sourceRoles = {
      M5: 'primary_dataset',
      H1: 'aggregate_primary_m5',
      H4: 'aggregate_primary_m5',
      DAY: 'external_upper_map_day',
      WEEK: 'aggregate_upper_map_day'
    };
    const timeframeResults = {};
    REQUIRED_SIMULATION_TIMEFRAMES.forEach(timeframe => {
      const rows = sourceRows[timeframe] || [];
      const resolved = latestConfirmedBarAt(rows, reference.reference_close_ms);
      const latest = summarizeSimulationCandle(resolved.latest, timeframe, sourceRoles[timeframe]);
      const unconfirmed = summarizeSimulationCandle(resolved.currentUnconfirmed, timeframe, sourceRoles[timeframe]);
      const profile = simulationProfileForTimeframe(draft, timeframe);
      const warmup = profile?.warmup || {};
      const warmupMode = String(warmup.mode || 'none');
      const warmupBars = Math.max(0, Math.floor(numberOrNull(warmup.bars) ?? 0));
      const availableConfirmedBars = resolved.latestIndex + 1;
      const warmupSatisfied = warmupMode === 'none' || warmupMode === 'all_history' || availableConfirmedBars >= warmupBars;
      const lookaheadDetected = Boolean(latest && latest.end_ms > reference.reference_close_ms);
      if (!latest) errors.push(`${timeframe}: latest confirmed candle was not found.`);
      if (lookaheadDetected) errors.push(`${timeframe}: Lookahead detected. confirmed end exceeds M5 reference close.`);
      if (!warmupSatisfied) warnings.push(`${timeframe}: warmup ${warmupBars} bars requested, only ${availableConfirmedBars} confirmed bars available.`);
      timeframeResults[timeframe] = {
        source_mapping: cloneJsonValue(profile?.source_mapping || {}),
        latest_confirmed_bar: latest,
        current_unconfirmed_bar: unconfirmed,
        future_rows_excluded: resolved.futureRowsExcluded,
        available_confirmed_bars: availableConfirmedBars,
        warmup: {
          mode: warmupMode,
          required_bars: warmupBars,
          satisfied: warmupSatisfied
        },
        lookahead_detected: lookaheadDetected,
        state_rebuild_key: latest?.confirmed_bar_key || null
      };
    });
    const timePolicy = draft?.time_sync_policy || {};
    if (String(timePolicy.dataset_timezone || '').toUpperCase().includes('UNSPECIFIED')) {
      warnings.push('Dataset timezone is not declared; timestamps are interpreted as browser-local wall clock and recorded in the snapshot.');
    }
    return {
      schema_version: 'fx_multi_timeframe_candle_sync_snapshot_v0_1',
      kind: 'fx_multi_timeframe_candle_sync_snapshot',
      status: errors.length ? 'invalid' : 'confirmed_only_ready',
      phase: 'v0.9.0.03-multi-timeframe-candle-synchronizer',
      created_at: nowLocalIso(),
      reference: {
        axis: String(timePolicy.reference_axis || 'M5_CLOSE'),
        source: reference.source,
        requested_time_ms: reference.requested_time_ms,
        requested_time: reference.requested_time,
        m5_bar: summarizeSimulationCandle(reference.row, 'M5', 'primary_dataset'),
        reference_close_ms: reference.reference_close_ms,
        reference_close_time: reference.reference_close_time
      },
      timezone: runtimeTimezoneSnapshot(reference.reference_close_ms, timePolicy),
      policy: {
        bar_timestamp_role: String(timePolicy.bar_timestamp_role || 'open_time'),
        confirmation_rule: String(timePolicy.confirmation_rule || 'bar_end_ms <= reference_close_ms'),
        week_start: String(timePolicy.week_start || 'MONDAY_00:00'),
        future_rows: String(timePolicy.future_rows || 'exclude'),
        missing_bars: String(timePolicy.missing_bars || 'do_not_fill'),
        state_rebuild: String(timePolicy.state_rebuild || 'only_when_latest_confirmed_bar_changes')
      },
      timeframes: timeframeResults,
      validation: {
        valid: errors.length === 0,
        checked_at: nowLocalIso(),
        errors,
        warnings,
        no_lookahead: errors.every(message => !message.includes('Lookahead detected'))
      },
      teacher_guard: 'Confirmed-candle synchronization only. No Dow/Cycle/HSI/Entry/Close decision is executed.'
    };
  }

  function swingPointAnalysisRows(rows, timeframe, profile, periodFromMs, confirmedCount) {
    const confirmedRows = (rows || []).slice(0, Math.max(0, confirmedCount));
    if (!confirmedRows.length) return { rows: [], start_index: 0, confirmed_count: 0, scope: 'empty' };
    const warmup = profile?.warmup || {};
    const mode = String(warmup.mode || 'none');
    const warmupBars = Math.max(0, Math.floor(numberOrNull(warmup.bars) ?? 0));
    if (mode === 'all_history') return { rows: confirmedRows, start_index: 0, confirmed_count: confirmedRows.length, scope: 'all_history' };
    let periodIndex = 0;
    if (periodFromMs != null) {
      const found = confirmedRows.findIndex(row => (numberOrNull(row.end_ms) ?? rowTimeMs(row) ?? 0) >= periodFromMs);
      periodIndex = found >= 0 ? found : Math.max(0, confirmedRows.length - 1);
    }
    const confirmBars = Math.max(3, Math.floor(numberOrNull(profile?.confirm_bars) ?? 3));
    const requiredContext = Math.max(confirmBars - 1, mode === 'past_bars' ? warmupBars : 0);
    const startIndex = Math.max(0, periodIndex - requiredContext);
    return {
      rows: confirmedRows.slice(startIndex),
      start_index: startIndex,
      confirmed_count: confirmedRows.length,
      scope: mode === 'past_bars' ? `current_period_plus_${warmupBars}_past_bars` : 'current_period_plus_confirm_context'
    };
  }

  function buildSharedSwingPointSnapshot(state, draft, candleSync) {
    const errors = [];
    const warnings = [];
    const sourceRows = simulationCandleSourceRows(state);
    const period = simulationRunVisiblePeriod(state);
    const periodFromMs = parseDateTimeMs(period.from);
    const policy = { ...(draft?.swing_point_policy || {}) };
    const timeframes = {};
    const observationEvents = [];
    REQUIRED_SIMULATION_TIMEFRAMES.forEach(timeframe => {
      const profile = simulationProfileForTimeframe(draft, timeframe);
      const confirmBars = Number(profile?.confirm_bars);
      const sync = candleSync?.timeframes?.[timeframe] || {};
      const allRows = sourceRows[timeframe] || [];
      const analysis = swingPointAnalysisRows(allRows, timeframe, profile, periodFromMs, sync.available_confirmed_bars || 0);
      const sourceRole = String(sync?.latest_confirmed_bar?.source_role || profile?.source_mapping?.source_dataset_role || '');
      if (!Number.isInteger(confirmBars) || confirmBars < 3) {
        errors.push(`${timeframe}: explicit confirm_bars is invalid.`);
        timeframes[timeframe] = { status: 'invalid_confirm_bars', confirm_bars: confirmBars, points: [], pending_candidates: [] };
        return;
      }
      if (analysis.rows.length < confirmBars) warnings.push(`${timeframe}: detector input ${analysis.rows.length} bars is shorter than confirm_bars=${confirmBars}.`);
      const confirmedPoints = buildCandidatePoints(analysis.rows, null, confirmBars, { timeframe, source_role: sourceRole });
      const layers = buildPointLayers(confirmedPoints);
      const pendingCandidates = buildPendingSwingCandidates(analysis.rows, timeframe, confirmBars, sourceRole);
      const events = buildSwingObservationEvents(timeframe, pendingCandidates, layers);
      const referenceMs = numberOrNull(candleSync?.reference?.reference_close_ms);
      const lookaheadPoints = (layers.all || []).filter(point => numberOrNull(point.confirmed_ms) != null && referenceMs != null && point.confirmed_ms > referenceMs);
      if (lookaheadPoints.length) errors.push(`${timeframe}: ${lookaheadPoints.length} swing point(s) confirmed after M5 reference close.`);
      const activeHigh = [...(layers.activeBasis || [])].reverse().find(point => point.type === 'swing_high') || null;
      const activeLow = [...(layers.activeBasis || [])].reverse().find(point => point.type === 'swing_low') || null;
      timeframes[timeframe] = {
        status: lookaheadPoints.length ? 'lookahead_detected' : 'ready',
        detector_id: SHARED_SWING_POINT_DETECTOR_ID,
        confirm_bars: confirmBars,
        source_mapping: cloneJsonValue(profile?.source_mapping || {}),
        analysis_scope: {
          mode: analysis.scope,
          source_confirmed_bars: analysis.confirmed_count,
          detector_input_bars: analysis.rows.length,
          source_start_index: analysis.start_index,
          from: analysis.rows[0]?.datetime || analysis.rows[0]?.time || '',
          to: analysis.rows[analysis.rows.length - 1]?.datetime || analysis.rows[analysis.rows.length - 1]?.time || ''
        },
        counts: {
          pending_candidates: pendingCandidates.length,
          confirmed_points: layers.all.length,
          candidate_only: layers.candidateOnly.length,
          active_basis: layers.activeBasis.length,
          retired_basis: layers.retiredBasis.length,
          observation_events: events.length
        },
        latest_active: {
          high: activeHigh ? { point_id: activeHigh.point_id, pivot_time: activeHigh.pivot_time, confirmed_time: activeHigh.confirmed_time, pivot_price: activeHigh.pivot_price } : null,
          low: activeLow ? { point_id: activeLow.point_id, pivot_time: activeLow.pivot_time, confirmed_time: activeLow.confirmed_time, pivot_price: activeLow.pivot_price } : null
        },
        pending_candidates: pendingCandidates,
        points: layers.all,
        ui_marker_projection: {
          status: 'shared_core',
          detector_functions: ['buildCandidatePoints', 'buildPointLayers'],
          marker_counts: { candidate: layers.candidateOnly.length, active: layers.activeBasis.length, retired: layers.retiredBasis.length },
          note: 'Chart UI and Simulation Snapshot use the same shared detector core. Display range/settings may differ from Run analysis scope.'
        },
        no_lookahead: lookaheadPoints.length === 0
      };
      observationEvents.push(...events);
    });
    return {
      schema_version: 'fx_shared_swing_point_snapshot_v0_1',
      kind: 'fx_shared_swing_point_snapshot',
      status: errors.length ? 'invalid' : 'ready',
      phase: 'v0.9.0.04-shared-swing-point-detector',
      created_at: nowLocalIso(),
      detector: {
        detector_id: String(policy.detector_id || SHARED_SWING_POINT_DETECTOR_ID),
        algorithm: String(policy.algorithm || 'center_window_unique_extreme'),
        confirm_bars_source: String(policy.confirm_bars_source || 'timeframe_profiles[].confirm_bars'),
        timeframe_specific_class: String(policy.timeframe_specific_class || 'forbidden'),
        candidate_policy: String(policy.candidate_policy || ''),
        confirmation_policy: String(policy.confirmation_policy || ''),
        retirement_policy: String(policy.retirement_policy || ''),
        no_lookahead: policy.no_lookahead === true
      },
      timeframes,
      observation_events: observationEvents,
      validation: { valid: errors.length === 0, checked_at: nowLocalIso(), errors, warnings, no_lookahead: errors.every(message => !message.includes('reference close')) },
      teacher_guard: 'Swing point observation only. Dow/Cycle/HSI/Entry/Close decisions are not executed. Only confirmed points marked usable_as_basis=true may be consumed by later phases.'
    };
  }

  function swingSnapshotPreview(snapshot) {
    if (!snapshot) return null;
    const copy = cloneJsonValue(snapshot);
    Object.values(copy.timeframes || {}).forEach(item => {
      if (Array.isArray(item.points)) item.points = `[${item.points.length} points omitted from preview]`;
      if (Array.isArray(item.pending_candidates)) item.pending_candidates = `[${item.pending_candidates.length} candidates omitted from preview]`;
    });
    if (Array.isArray(copy.observation_events)) copy.observation_events = `[${copy.observation_events.length} events omitted from preview]`;
    return copy;
  }

  function mergeSwingChartEvents(existingEvents, swingSnapshot) {
    const kept = (existingEvents || []).filter(event => event?.generated_by !== SHARED_SWING_POINT_GENERATOR).map(event => {
      if (String(event?.event_id || '').startsWith('trace_fixture_')) {
        return { ...event, display: { ...(event.display || {}), visible: false } };
      }
      return event;
    });
    const projected = (swingSnapshot?.observation_events || []).filter(event => event?.display?.visible === true);
    return [...kept, ...projected];
  }


  function dowPriceRelation(currentPrice, previousPrice) {
    const current = numberOrNull(currentPrice);
    const previous = numberOrNull(previousPrice);
    if (current == null || previous == null) return 'UNKNOWN';
    if (current > previous) return 'HIGHER';
    if (current < previous) return 'LOWER';
    return 'EQUAL';
  }

  function dowPointSummary(point) {
    if (!point) return null;
    return {
      point_id: point.point_id || point.key || '',
      type: point.type || '',
      pivot_time: point.pivot_time || '',
      pivot_ms: numberOrNull(point.pivot_ms),
      confirmed_time: point.confirmed_time || '',
      confirmed_ms: numberOrNull(point.confirmed_ms),
      pivot_price: numberOrNull(point.pivot_price),
      confirm_bars: numberOrNull(point.confirm_bars),
      lifecycle_status: point.lifecycle_status || '',
      basis_role: point.basis_role || point.role || '',
      usable_as_basis: point.usable_as_basis === true
    };
  }

  function dowPointConfirmedEventId(point) {
    return point ? sharedSwingPointEventId(point, 'confirmed') : '';
  }

  function dowTrendEventId(timeframe, triggerPoint, nextState) {
    return `dow_evt_${String(timeframe || '').toLowerCase()}_${stableSwingToken(triggerPoint?.point_id || triggerPoint?.key || triggerPoint?.confirmed_time)}_${String(nextState || '').toLowerCase()}`;
  }

  function dowConfirmationEventId(timeframe, direction, signature, triggerPoint) {
    return `dow_confirm_${String(timeframe || '').toLowerCase()}_${String(direction || '').toLowerCase()}_${stableSwingToken(triggerPoint?.confirmed_ms || triggerPoint?.confirmed_time || triggerPoint?.point_id || triggerPoint?.key)}_${stableTextHash(String(signature || ''))}`;
  }

  function dowStateClass(state) {
    const value = String(state || '').toUpperCase();
    if (value === 'UP') return 'gpt-fx-chart-trend-up';
    if (value === 'DOWN') return 'gpt-fx-chart-trend-down';
    if (value === 'REVERSAL_WATCH') return 'gpt-fx-chart-trend-watch';
    return 'gpt-fx-chart-trend-neutral';
  }

  function evaluateDowStructureState(previousState, lastDirectionalState, previousHigh, currentHigh, previousLow, currentLow) {
    if (!previousHigh || !currentHigh || !previousLow || !currentLow) {
      return {
        state: 'UNDETERMINED',
        high_relation: previousHigh && currentHigh ? dowPriceRelation(currentHigh.pivot_price, previousHigh.pivot_price) : 'INSUFFICIENT',
        low_relation: previousLow && currentLow ? dowPriceRelation(currentLow.pivot_price, previousLow.pivot_price) : 'INSUFFICIENT',
        directional_bias: lastDirectionalState || null,
        reason_codes: ['DOW_UNDETERMINED', 'INSUFFICIENT_CONFIRMED_SWING_PAIRS']
      };
    }
    const highRelation = dowPriceRelation(currentHigh.pivot_price, previousHigh.pivot_price);
    const lowRelation = dowPriceRelation(currentLow.pivot_price, previousLow.pivot_price);
    if (highRelation === 'HIGHER' && lowRelation === 'HIGHER') {
      return { state: 'UP', high_relation: highRelation, low_relation: lowRelation, directional_bias: 'UP', reason_codes: ['DOW_TREND_UP_CONFIRMED', 'HIGHER_HIGH', 'HIGHER_LOW'] };
    }
    if (highRelation === 'LOWER' && lowRelation === 'LOWER') {
      return { state: 'DOWN', high_relation: highRelation, low_relation: lowRelation, directional_bias: 'DOWN', reason_codes: ['DOW_TREND_DOWN_CONFIRMED', 'LOWER_HIGH', 'LOWER_LOW'] };
    }
    if (highRelation === 'EQUAL' || lowRelation === 'EQUAL') {
      return { state: 'NO_TREND', high_relation: highRelation, low_relation: lowRelation, directional_bias: lastDirectionalState || null, reason_codes: ['DOW_NO_TREND', 'EQUAL_SWING_PRICE'] };
    }
    if (lastDirectionalState === 'UP' || lastDirectionalState === 'DOWN') {
      return {
        state: 'REVERSAL_WATCH',
        high_relation: highRelation,
        low_relation: lowRelation,
        directional_bias: lastDirectionalState,
        reason_codes: ['DOW_REVERSAL_WATCH', `FROM_${lastDirectionalState}`, `HIGH_${highRelation}`, `LOW_${lowRelation}`]
      };
    }
    return {
      state: 'NO_TREND',
      high_relation: highRelation,
      low_relation: lowRelation,
      directional_bias: null,
      reason_codes: ['DOW_NO_TREND', 'MIXED_STRUCTURE_WITHOUT_PRIOR_DIRECTION', `HIGH_${highRelation}`, `LOW_${lowRelation}`]
    };
  }

  function m5BreakoutRowEndMs(row) {
    const startMs = rowTimeMs(row);
    return startMs == null ? null : startMs + 5 * 60 * 1000 - 1;
  }

  function firstM5BreakoutRow(sourceRows, startAfterMs, referenceMs, direction, thresholdPrice) {
    const rows = Array.isArray(sourceRows) ? sourceRows : [];
    const threshold = numberOrNull(thresholdPrice);
    if (!rows.length || threshold == null || referenceMs == null) return null;
    let lo = 0;
    let hi = rows.length;
    while (lo < hi) {
      const mid = (lo + hi) >> 1;
      const ms = rowTimeMs(rows[mid]);
      if (ms == null || ms < Number(startAfterMs || 0)) lo = mid + 1;
      else hi = mid;
    }
    for (let idx = lo; idx < rows.length; idx += 1) {
      const row = rows[idx];
      const startMs = rowTimeMs(row);
      const endMs = m5BreakoutRowEndMs(row);
      if (startMs == null || endMs == null) continue;
      if (endMs > Number(referenceMs)) break;
      const crossed = direction === 'DOWN'
        ? numberOrNull(row?.low) != null && Number(row.low) < threshold
        : numberOrNull(row?.high) != null && Number(row.high) > threshold;
      if (crossed) return { row, start_ms: startMs, end_ms: endMs, index: idx };
    }
    return null;
  }

  function latestM5BreakoutConfirmation(structure, sourceRows, referenceMs, minimumBreakoutAfterMs = null) {
    const points = Array.isArray(structure) ? structure : [];
    const highs = [];
    const lows = [];
    const candidates = [];
    points.forEach(point => {
      if (point?.type === 'swing_low') {
        const previousLow = lows.length ? lows[lows.length - 1] : null;
        const currentLow = point;
        const currentHigh = highs.length ? highs[highs.length - 1] : null;
        const previousHigh = highs.length >= 2 ? highs[highs.length - 2] : null;
        const sequenceValid = previousLow && currentHigh
          && numberOrNull(previousLow.pivot_ms) < numberOrNull(currentHigh.pivot_ms)
          && numberOrNull(currentHigh.pivot_ms) < numberOrNull(currentLow.pivot_ms);
        const higherLow = previousLow && numberOrNull(currentLow.pivot_price) > numberOrNull(previousLow.pivot_price);
        if (sequenceValid && higherLow) {
          candidates.push({
            direction: 'UP',
            previousHigh,
            currentHigh,
            previousLow,
            currentLow,
            anchorPoint: previousLow,
            thresholdPoint: currentHigh,
            readyAfterMs: Math.max(numberOrNull(currentHigh.confirmed_ms) || 0, numberOrNull(currentLow.confirmed_ms) || 0)
          });
        }
        lows.push(point);
      } else if (point?.type === 'swing_high') {
        const previousHigh = highs.length ? highs[highs.length - 1] : null;
        const currentHigh = point;
        const currentLow = lows.length ? lows[lows.length - 1] : null;
        const previousLow = lows.length >= 2 ? lows[lows.length - 2] : null;
        const sequenceValid = previousHigh && currentLow
          && numberOrNull(previousHigh.pivot_ms) < numberOrNull(currentLow.pivot_ms)
          && numberOrNull(currentLow.pivot_ms) < numberOrNull(currentHigh.pivot_ms);
        const lowerHigh = previousHigh && numberOrNull(currentHigh.pivot_price) < numberOrNull(previousHigh.pivot_price);
        if (sequenceValid && lowerHigh) {
          candidates.push({
            direction: 'DOWN',
            previousHigh,
            currentHigh,
            previousLow,
            currentLow,
            anchorPoint: previousHigh,
            thresholdPoint: currentLow,
            readyAfterMs: Math.max(numberOrNull(currentHigh.confirmed_ms) || 0, numberOrNull(currentLow.confirmed_ms) || 0)
          });
        }
        highs.push(point);
      }
    });
    for (let idx = candidates.length - 1; idx >= 0; idx -= 1) {
      const candidate = candidates[idx];
      const breakout = firstM5BreakoutRow(sourceRows, candidate.readyAfterMs, referenceMs, candidate.direction, candidate.thresholdPoint?.pivot_price);
      if (!breakout) continue;
      const breakoutEndMs = numberOrNull(breakout.end_ms);
      const minimumMs = numberOrNull(minimumBreakoutAfterMs);
      if (minimumMs != null && (breakoutEndMs == null || breakoutEndMs <= minimumMs)) continue;
      return { ...candidate, breakout };
    }
    return null;
  }

  function replayDowTrendForTimeframe(timeframe, swingTimeframe, referenceMs, referenceBar = null, sourceRows = []) {
    const tf = String(timeframe || '').toUpperCase();
    const sourcePoints = Array.isArray(swingTimeframe?.points) ? swingTimeframe.points : [];
    const confirmedPoints = sourcePoints
      .filter(point => point && String(point.lifecycle_status || '').toLowerCase() !== 'candidate' && numberOrNull(point.confirmed_ms) != null)
      .sort((a, b) => (numberOrNull(a.confirmed_ms) ?? 0) - (numberOrNull(b.confirmed_ms) ?? 0) || (numberOrNull(a.pivot_ms) ?? 0) - (numberOrNull(b.pivot_ms) ?? 0) || String(a.type || '').localeCompare(String(b.type || '')));
    const structure = [];
    const events = [];
    const confirmationEvents = [];
    const timeline = [];
    let latestConfirmation = null;
    let latestConfirmationAnchorPoint = null;
    let lastConfirmationSignature = '';
    let lastConfirmationCurrentHighId = '';
    let lastConfirmationCurrentLowId = '';
    let ignoredSameTypeNonExtreme = 0;
    let currentState = null;
    let lastDirectionalState = null;
    let latestEvaluation = null;
    let lookaheadCount = 0;
    // 通常HSI起点は「成立中の通常Dow」にだけ所属する。
    // REVERSAL_WATCH / NO_TREND / UNDETERMINEDへ遷移した時点で通常起点を解除し、
    // 同方向へ再成立しても新しいDowとしてprevious Swingを採用する。
    let directionalRegime = null;
    let directionalRegimeStartedAt = '';
    let directionalRegimeTriggerEventId = '';
    let directionalRegimeAnchorPoint = null;
    let directionalRegimeAnchorSelectionPolicy = '';
    let directionalRegimeAnchorFallbackUsed = false;
    let directionalRegimeResetAt = '';
    let directionalRegimeResetEventId = '';
    let directionalRegimeResetReason = '';
    let latestNormalDowStructureBreak = null;

    // Expansionだけは通常Dowとは別Lifecycleで大起点を保持する。
    // REVERSAL_WATCH等は押し戻りとして許容し、反対方向Dow成立時だけDetection Anchorを更新する。
    let expansionDetectionRegime = null;
    let expansionDetectionStartedAt = '';
    let expansionDetectionTriggerEventId = '';
    let expansionDetectionAnchorPoint = null;
    let expansionDetectionAnchorSelectionPolicy = '';
    let expansionDetectionAnchorFallbackUsed = false;

    function isMoreExtreme(next, current) {
      const nextPrice = numberOrNull(next?.pivot_price);
      const currentPrice = numberOrNull(current?.pivot_price);
      if (nextPrice == null || currentPrice == null) return false;
      return next.type === 'swing_high' ? nextPrice > currentPrice : nextPrice < currentPrice;
    }

    confirmedPoints.forEach(point => {
      const confirmedMs = numberOrNull(point.confirmed_ms);
      if (referenceMs != null && confirmedMs != null && confirmedMs > referenceMs) {
        lookaheadCount += 1;
        return;
      }
      let structureChanged = false;
      if (!structure.length) {
        structure.push(point);
        structureChanged = true;
      } else {
        const last = structure[structure.length - 1];
        if (last.type === point.type) {
          if (isMoreExtreme(point, last)) {
            structure[structure.length - 1] = point;
            structureChanged = true;
          } else {
            ignoredSameTypeNonExtreme += 1;
          }
        } else {
          structure.push(point);
          structureChanged = true;
        }
      }
      if (!structureChanged) return;
      const highs = structure.filter(item => item.type === 'swing_high');
      const lows = structure.filter(item => item.type === 'swing_low');
      const previousHigh = highs.length >= 2 ? highs[highs.length - 2] : null;
      const currentHigh = highs.length ? highs[highs.length - 1] : null;
      const previousLow = lows.length >= 2 ? lows[lows.length - 2] : null;
      const currentLow = lows.length ? lows[lows.length - 1] : null;
      const evaluated = evaluateDowStructureState(currentState, lastDirectionalState, previousHigh, currentHigh, previousLow, currentLow);
      latestEvaluation = {
        ...evaluated,
        comparison_points: {
          previous_high: dowPointSummary(previousHigh),
          current_high: dowPointSummary(currentHigh),
          previous_low: dowPointSummary(previousLow),
          current_low: dowPointSummary(currentLow)
        },
        trigger_point: dowPointSummary(point)
      };
      const previousDirectionalState = lastDirectionalState;
      const directionalConfirmation = evaluated.state === 'UP' || evaluated.state === 'DOWN';
      const confirmationAnchorPoint = evaluated.state === 'UP' ? previousLow : evaluated.state === 'DOWN' ? previousHigh : null;
      const confirmationCurrentHighId = currentHigh?.point_id || currentHigh?.key || '';
      const confirmationCurrentLowId = currentLow?.point_id || currentLow?.key || '';
      const confirmationSignature = directionalConfirmation
        ? [
            evaluated.state,
            previousHigh?.point_id || previousHigh?.key || '',
            confirmationCurrentHighId,
            previousLow?.point_id || previousLow?.key || '',
            confirmationCurrentLowId
          ].join('|')
        : '';
      // 新しいDow確認Eventは、High側とLow側の比較ペアが両方とも前回確認から進んだ時だけ発行する。
      // 片側だけの更新を新しいEntry切符にすると、R2.5 Close直後の階段ReEntryへ戻ってしまうため禁止する。
      const completeStructurePairAdvanced = !lastConfirmationSignature
        || (confirmationCurrentHighId !== lastConfirmationCurrentHighId
          && confirmationCurrentLowId !== lastConfirmationCurrentLowId);
      if (tf !== 'M5' && directionalConfirmation && confirmationAnchorPoint && confirmationSignature && completeStructurePairAdvanced) {
        const confirmationEvent = {
          event_id: dowConfirmationEventId(tf, evaluated.state, confirmationSignature, point),
          source_type: SIMULATION_TRACE_SOURCE_TYPE,
          generated_by: DOW_TREND_GENERATOR,
          evaluator_id: DOW_TREND_EVALUATOR_ID,
          event_type: 'dow_confirmation',
          simulation_time: point.confirmed_time || point.pivot_time || '',
          timeframe: tf,
          panel: tf,
          price: numberOrNull(point.pivot_price),
          summary: `${tf} Dow ${evaluated.state}確認。新しい通常Entry機会を発行します。`,
          reason_codes: uniqueStrings([
            ...evaluated.reason_codes,
            'M5_DOW_CONFIRMATION_EVENT_ISSUED',
            evaluated.state === 'UP' ? 'DOW_CONFIRMATION_PREVIOUS_LOW_ANCHOR' : 'DOW_CONFIRMATION_PREVIOUS_HIGH_ANCHOR'
          ]),
          rule_ids: [
            'rule_dow_confirmation_event_per_structure_pair',
            'rule_normal_entry_one_opportunity_per_dow_confirmation',
            'rule_normal_hsi_anchor_uses_previous_structure_origin'
          ],
          cause_event_ids: [previousHigh, currentHigh, previousLow, currentLow].filter(Boolean).map(dowPointConfirmedEventId).filter(Boolean),
          swing_point_ids: [previousHigh, currentHigh, previousLow, currentLow].filter(Boolean).map(item => item.point_id || item.key).filter(Boolean),
          direction: evaluated.state,
          confirmation_signature: confirmationSignature,
          anchor_point: dowPointSummary(confirmationAnchorPoint),
          comparison_points: latestEvaluation.comparison_points,
          state_before: {
            trend_state: currentState || 'UNINITIALIZED',
            latest_confirmation_id: latestConfirmation?.confirmation_id || null
          },
          state_after: {
            trend_state: evaluated.state,
            confirmation_id: '',
            anchor_point_id: confirmationAnchorPoint?.point_id || confirmationAnchorPoint?.key || null,
            opportunity_status: 'WAITING_R2'
          },
          display: { visible: false, open: false, pinned: false, style: `dow_confirmation_${String(evaluated.state || '').toLowerCase()}` }
        };
        confirmationEvent.state_after.confirmation_id = confirmationEvent.event_id;
        confirmationEvents.push(confirmationEvent);
        latestConfirmationAnchorPoint = confirmationAnchorPoint;
        latestConfirmation = {
          confirmation_id: confirmationEvent.event_id,
          direction: evaluated.state,
          confirmed_at: confirmationEvent.simulation_time,
          confirmed_at_ms: numberOrNull(point.confirmed_ms),
          trigger_point_id: point?.point_id || point?.key || null,
          anchor_point_id: confirmationAnchorPoint?.point_id || confirmationAnchorPoint?.key || null,
          anchor_type: confirmationAnchorPoint?.type || null,
          anchor_price: numberOrNull(confirmationAnchorPoint?.pivot_price),
          anchor_time: confirmationAnchorPoint?.pivot_time || null,
          confirmation_signature: confirmationSignature,
          opportunity_policy: 'ONE_NORMAL_ENTRY_AT_DOW_BREAKOUT_CONFIRMATION_IF_R2_READY_ELSE_FIRST_R2_TOUCH'
        };
        lastConfirmationSignature = confirmationSignature;
        lastConfirmationCurrentHighId = confirmationCurrentHighId;
        lastConfirmationCurrentLowId = confirmationCurrentLowId;
        if (evaluated.state === currentState && directionalRegime === evaluated.state) {
          directionalRegimeTriggerEventId = confirmationEvent.event_id;
          directionalRegimeAnchorPoint = confirmationAnchorPoint;
          directionalRegimeAnchorSelectionPolicy = evaluated.state === 'UP'
            ? 'PREVIOUS_LOW_FROM_LATEST_DOW_CONFIRMATION'
            : 'PREVIOUS_HIGH_FROM_LATEST_DOW_CONFIRMATION';
          directionalRegimeAnchorFallbackUsed = false;
        }
      }
      if (evaluated.state === currentState) {
        if (evaluated.state === 'UP' || evaluated.state === 'DOWN') lastDirectionalState = evaluated.state;
        return;
      }
      const previousState = currentState || 'UNINITIALIZED';
      const usedPoints = [previousHigh, currentHigh, previousLow, currentLow].filter(Boolean);
      const event = {
        event_id: dowTrendEventId(tf, point, evaluated.state),
        source_type: SIMULATION_TRACE_SOURCE_TYPE,
        generated_by: DOW_TREND_GENERATOR,
        evaluator_id: DOW_TREND_EVALUATOR_ID,
        event_type: 'trend_changed',
        simulation_time: point.confirmed_time || point.pivot_time || '',
        simulation_time_ms: numberOrNull(point.confirmed_ms) ?? numberOrNull(point.pivot_ms),
        timeframe: tf,
        panel: tf,
        price: numberOrNull(point.pivot_price),
        summary: evaluated.state === 'UP'
          ? `${tf} Dow UP確定。Higher High + Higher Low。`
          : evaluated.state === 'DOWN'
            ? `${tf} Dow DOWN確定。Lower High + Lower Low。`
            : evaluated.state === 'REVERSAL_WATCH'
              ? `${tf} Dow反転監視。高値・安値の方向が一致していません。`
              : evaluated.state === 'NO_TREND'
                ? `${tf} Dow NoTrend。確定高安値の方向が揃っていません。`
                : `${tf} Dow判定保留。確定高値・安値の比較ペアが不足しています。`,
        reason_codes: [...evaluated.reason_codes],
        rule_ids: ['rule_dow_confirmed_swing_structure', 'rule_dow_state_not_entry_permission', 'rule_no_lookahead_confirmed_swings'],
        cause_event_ids: usedPoints.map(dowPointConfirmedEventId).filter(Boolean),
        swing_point_ids: usedPoints.map(item => item.point_id || item.key).filter(Boolean),
        upper_state_summary: { [tf]: evaluated.state, directional_bias: evaluated.directional_bias || 'NONE', entry_permission: 'NOT_EVALUATED' },
        state_before: { trend_state: previousState, directional_bias: previousDirectionalState || null },
        state_after: {
          trend_state: evaluated.state,
          directional_bias: evaluated.directional_bias || null,
          high_relation: evaluated.high_relation,
          low_relation: evaluated.low_relation,
          entry_permission: 'NOT_EVALUATED'
        },
        comparison_points: latestEvaluation.comparison_points,
        display: { visible: false, open: false, pinned: false, style: `dow_${String(evaluated.state || '').toLowerCase()}` }
      };
      events.push(event);
      if (evaluated.state === 'UP' || evaluated.state === 'DOWN') {
        // 通常Lane: non-directional stateで一度解除されていれば、同方向再成立でも新しいDowとして再採用する。
        if (directionalRegime !== evaluated.state) {
          directionalRegime = evaluated.state;
          directionalRegimeStartedAt = event.simulation_time;
          directionalRegimeTriggerEventId = latestConfirmation?.confirmation_id || event.event_id;
          const preferredOriginPoint = latestConfirmationAnchorPoint || (evaluated.state === 'UP' ? previousLow : previousHigh);
          const defensiveFallbackPoint = evaluated.state === 'UP' ? currentLow : currentHigh;
          directionalRegimeAnchorPoint = preferredOriginPoint || defensiveFallbackPoint;
          directionalRegimeAnchorSelectionPolicy = latestConfirmationAnchorPoint
            ? (evaluated.state === 'UP' ? 'PREVIOUS_LOW_FROM_LATEST_DOW_CONFIRMATION' : 'PREVIOUS_HIGH_FROM_LATEST_DOW_CONFIRMATION')
            : evaluated.state === 'UP'
              ? 'PREVIOUS_LOW_AS_DOW_ORIGIN'
              : 'PREVIOUS_HIGH_AS_DOW_ORIGIN';
          directionalRegimeAnchorFallbackUsed = !preferredOriginPoint && !!defensiveFallbackPoint;
          directionalRegimeResetAt = '';
          directionalRegimeResetEventId = '';
          directionalRegimeResetReason = '';
        }

        // Expansion Lane: 同方向再成立では元の大起点を維持し、反対方向Dow成立時だけ更新する。
        if (expansionDetectionRegime !== evaluated.state) {
          expansionDetectionRegime = evaluated.state;
          expansionDetectionStartedAt = event.simulation_time;
          expansionDetectionTriggerEventId = event.event_id;
          const preferredExpansionOrigin = evaluated.state === 'UP' ? previousLow : previousHigh;
          const defensiveExpansionFallback = evaluated.state === 'UP' ? currentLow : currentHigh;
          expansionDetectionAnchorPoint = preferredExpansionOrigin || defensiveExpansionFallback;
          expansionDetectionAnchorSelectionPolicy = evaluated.state === 'UP'
            ? 'PREVIOUS_LOW_AS_EXPANSION_DETECTION_ORIGIN'
            : 'PREVIOUS_HIGH_AS_EXPANSION_DETECTION_ORIGIN';
          expansionDetectionAnchorFallbackUsed = !preferredExpansionOrigin && !!defensiveExpansionFallback;
        }
        lastDirectionalState = evaluated.state;
      } else {
        // 通常LaneではDowが崩れた時点で起点を解除する。
        // 旧大起点を保持する挙動はExpansion Detection専用。
        if (directionalRegime || directionalRegimeAnchorPoint || latestConfirmation || ['UP', 'DOWN'].includes(previousState)) {
          directionalRegimeResetAt = event.simulation_time;
          directionalRegimeResetEventId = event.event_id;
          directionalRegimeResetReason = `NORMAL_DOW_ANCHOR_RESET_ON_${evaluated.state}`;
          latestNormalDowStructureBreak = {
            break_at: event.simulation_time,
            break_at_ms: numberOrNull(point?.confirmed_ms) ?? parseDateTimeMs(event.simulation_time),
            break_event_id: event.event_id,
            break_state: evaluated.state,
            previous_direction: ['UP', 'DOWN'].includes(previousState) ? previousState : lastDirectionalState,
            invalidated_confirmation_id: latestConfirmation?.confirmation_id || null,
            invalidated_anchor_point_id: latestConfirmationAnchorPoint?.point_id || latestConfirmationAnchorPoint?.key || directionalRegimeAnchorPoint?.point_id || directionalRegimeAnchorPoint?.key || null,
            trigger_point_id: point?.point_id || point?.key || null,
            reason_code: 'NORMAL_DOW_STRUCTURE_BROKEN_BEFORE_ENTRY',
            lifecycle_action: 'RETIRE_PRE_ENTRY_CONFIRMATION_ANCHOR_OPPORTUNITY_R2_HISTORY'
          };
        }
        directionalRegime = null;
        directionalRegimeStartedAt = '';
        directionalRegimeTriggerEventId = '';
        directionalRegimeAnchorPoint = null;
        directionalRegimeAnchorSelectionPolicy = '';
        directionalRegimeAnchorFallbackUsed = false;
        latestConfirmation = null;
        latestConfirmationAnchorPoint = null;
        lastConfirmationSignature = '';
        lastConfirmationCurrentHighId = '';
        lastConfirmationCurrentLowId = '';
      }
      timeline.push({
        event_id: event.event_id,
        at: event.simulation_time,
        from: previousState,
        to: evaluated.state,
        directional_bias: evaluated.directional_bias || null,
        high_relation: evaluated.high_relation,
        low_relation: evaluated.low_relation,
        trigger_point_id: point.point_id || point.key || '',
        used_swing_point_ids: event.swing_point_ids
      });
      currentState = evaluated.state;
    });

    if (tf === 'M5') {
      // M5 breakout候補は1回だけ解決する。
      // 以前は各non-directional Eventごとに全Structure/全M5 Rowを再走査しており、
      // Visible Range Simulationの各足で指数的に重くなっていた。
      let breakoutConfirmation = latestM5BreakoutConfirmation(structure, sourceRows, referenceMs, null);
      const breakoutConfirmationMs = numberOrNull(breakoutConfirmation?.breakout?.end_ms);

      // M5のDow Confirmationはローソク足breakoutで後段確定するため、
      // 最新の非方向状態が最新breakoutより後なら、そのbreakoutをEntry前Dow崩壊で失効する。
      if (!latestNormalDowStructureBreak && breakoutConfirmation && breakoutConfirmationMs != null) {
        const breakEvent = [...events].reverse().find(item => {
          const stateValue = String(item?.state_after?.trend_state || '').toUpperCase();
          const eventMs = numberOrNull(item?.simulation_time_ms) ?? parseDateTimeMs(item?.simulation_time);
          return ['REVERSAL_WATCH', 'NO_TREND', 'UNDETERMINED'].includes(stateValue)
            && eventMs != null
            && eventMs > breakoutConfirmationMs;
        });
        if (breakEvent) {
          const breakMs = numberOrNull(breakEvent?.simulation_time_ms) ?? parseDateTimeMs(breakEvent?.simulation_time);
          latestNormalDowStructureBreak = {
            break_at: breakEvent.simulation_time,
            break_at_ms: breakMs,
            break_event_id: breakEvent.event_id,
            break_state: String(breakEvent?.state_after?.trend_state || '').toUpperCase(),
            previous_direction: breakoutConfirmation.direction,
            invalidated_confirmation_id: dowConfirmationEventId(tf, breakoutConfirmation.direction, [
              breakoutConfirmation.direction,
              breakoutConfirmation.anchorPoint?.point_id || breakoutConfirmation.anchorPoint?.key || '',
              breakoutConfirmation.thresholdPoint?.point_id || breakoutConfirmation.thresholdPoint?.key || '',
              breakoutConfirmation.direction === 'UP'
                ? breakoutConfirmation.currentLow?.point_id || breakoutConfirmation.currentLow?.key || ''
                : breakoutConfirmation.currentHigh?.point_id || breakoutConfirmation.currentHigh?.key || '',
              breakoutConfirmation.breakout.start_ms
            ].join('|'), {
              point_id: `m5_breakout_bar_${stableSwingToken(breakoutConfirmation.breakout.start_ms)}`,
              confirmed_ms: breakoutConfirmation.breakout.end_ms,
              pivot_ms: breakoutConfirmation.breakout.start_ms,
              type: breakoutConfirmation.direction === 'UP' ? 'breakout_high' : 'breakout_low'
            }),
            invalidated_anchor_point_id: breakoutConfirmation.anchorPoint?.point_id || breakoutConfirmation.anchorPoint?.key || null,
            trigger_point_id: breakEvent?.comparison_points?.current_high?.point_id || breakEvent?.comparison_points?.current_low?.point_id || null,
            reason_code: 'NORMAL_DOW_STRUCTURE_BROKEN_BEFORE_ENTRY',
            lifecycle_action: 'RETIRE_PRE_ENTRY_CONFIRMATION_ANCHOR_OPPORTUNITY_R2_HISTORY'
          };
        }
      }
      const breakBarrierMs = numberOrNull(latestNormalDowStructureBreak?.break_at_ms);
      if (breakBarrierMs != null && (breakoutConfirmationMs == null || breakoutConfirmationMs <= breakBarrierMs)) {
        // v0.9.1.10: 旧Confirmationを単にnullへ落とすだけでは、その後に成立した
        // 新しいDow再確定まで見失い、NORMALだけでなく共有Dow事実を参照する
        // EXPANSION_LITEのEntryも長期間停止してしまう。
        // 崩壊時刻を下限として再検索し、崩壊後の最初の有効breakout Confirmationを復元する。
        breakoutConfirmation = latestM5BreakoutConfirmation(structure, sourceRows, referenceMs, breakBarrierMs);
      }
      if (breakoutConfirmation) {
        const direction = breakoutConfirmation.direction;
        const anchorPoint = breakoutConfirmation.anchorPoint;
        const thresholdPoint = breakoutConfirmation.thresholdPoint;
        const breakoutRow = breakoutConfirmation.breakout.row || referenceBar || {};
        const breakoutStartMs = breakoutConfirmation.breakout.start_ms;
        const breakoutEndMs = breakoutConfirmation.breakout.end_ms;
        const breakoutPrice = direction === 'DOWN'
          ? numberOrNull(breakoutRow.low ?? breakoutRow.close)
          : numberOrNull(breakoutRow.high ?? breakoutRow.close);
        const signature = [
          direction,
          anchorPoint?.point_id || anchorPoint?.key || '',
          thresholdPoint?.point_id || thresholdPoint?.key || '',
          direction === 'UP'
            ? breakoutConfirmation.currentLow?.point_id || breakoutConfirmation.currentLow?.key || ''
            : breakoutConfirmation.currentHigh?.point_id || breakoutConfirmation.currentHigh?.key || '',
          breakoutStartMs
        ].join('|');
        const triggerPoint = {
          point_id: `m5_breakout_bar_${stableSwingToken(breakoutStartMs)}`,
          key: `m5_breakout_bar_${stableSwingToken(breakoutStartMs)}`,
          confirmed_ms: breakoutEndMs,
          confirmed_time: String(breakoutRow.datetime || breakoutRow.start_time || ''),
          pivot_ms: breakoutStartMs,
          pivot_time: String(breakoutRow.datetime || breakoutRow.start_time || ''),
          pivot_price: breakoutPrice,
          type: direction === 'UP' ? 'breakout_high' : 'breakout_low'
        };
        const confirmationEvent = {
          event_id: dowConfirmationEventId(tf, direction, signature, triggerPoint),
          source_type: SIMULATION_TRACE_SOURCE_TYPE,
          generated_by: DOW_TREND_GENERATOR,
          evaluator_id: DOW_TREND_EVALUATOR_ID,
          event_type: 'dow_confirmation',
          simulation_time: triggerPoint.confirmed_time,
          timeframe: tf,
          panel: tf,
          price: breakoutPrice,
          summary: direction === 'UP'
            ? `${tf} Dow UP確認。確定済み押し安値の後、直前構造高値 ${round3(thresholdPoint?.pivot_price)}をM5確定足で突破しました。`
            : `${tf} Dow DOWN確認。確定済み戻り高値の後、直前構造安値 ${round3(thresholdPoint?.pivot_price)}をM5確定足で突破しました。`,
          reason_codes: uniqueStrings([
            direction === 'UP' ? 'DOW_TREND_UP_BREAKOUT_CONFIRMED' : 'DOW_TREND_DOWN_BREAKOUT_CONFIRMED',
            direction === 'UP' ? 'HIGHER_LOW_CONFIRMED_BEFORE_BREAKOUT' : 'LOWER_HIGH_CONFIRMED_BEFORE_BREAKOUT',
            direction === 'UP' ? 'PREVIOUS_STRUCTURE_HIGH_BROKEN' : 'PREVIOUS_STRUCTURE_LOW_BROKEN',
            'M5_DOW_CONFIRMATION_EVENT_ISSUED',
            direction === 'UP' ? 'DOW_CONFIRMATION_PREVIOUS_LOW_ANCHOR' : 'DOW_CONFIRMATION_PREVIOUS_HIGH_ANCHOR'
          ]),
          rule_ids: [
            'rule_m5_dow_confirmation_on_structure_breakout',
            'rule_normal_entry_one_opportunity_per_dow_confirmation',
            'rule_normal_hsi_anchor_uses_previous_structure_origin'
          ],
          cause_event_ids: [
            breakoutConfirmation.previousHigh,
            breakoutConfirmation.currentHigh,
            breakoutConfirmation.previousLow,
            breakoutConfirmation.currentLow
          ].filter(Boolean).map(dowPointConfirmedEventId).filter(Boolean),
          swing_point_ids: [
            breakoutConfirmation.previousHigh,
            breakoutConfirmation.currentHigh,
            breakoutConfirmation.previousLow,
            breakoutConfirmation.currentLow
          ].filter(Boolean).map(item => item.point_id || item.key).filter(Boolean),
          direction,
          confirmation_signature: signature,
          breakout_threshold_point: dowPointSummary(thresholdPoint),
          breakout_bar: {
            start_ms: breakoutStartMs,
            end_ms: breakoutEndMs,
            time: triggerPoint.confirmed_time,
            open: numberOrNull(breakoutRow.open),
            high: numberOrNull(breakoutRow.high),
            low: numberOrNull(breakoutRow.low),
            close: numberOrNull(breakoutRow.close)
          },
          anchor_point: dowPointSummary(anchorPoint),
          comparison_points: {
            previous_high: dowPointSummary(breakoutConfirmation.previousHigh),
            current_high: dowPointSummary(breakoutConfirmation.currentHigh),
            previous_low: dowPointSummary(breakoutConfirmation.previousLow),
            current_low: dowPointSummary(breakoutConfirmation.currentLow)
          },
          state_before: {
            trend_state: currentState || 'UNINITIALIZED',
            latest_confirmation_id: latestConfirmation?.confirmation_id || null
          },
          state_after: {
            trend_state: direction,
            confirmation_id: '',
            anchor_point_id: anchorPoint?.point_id || anchorPoint?.key || null,
            opportunity_status: 'WAITING_R2_OR_IMMEDIATE_ENTRY'
          },
          display: { visible: false, open: false, pinned: false, style: `dow_confirmation_${String(direction).toLowerCase()}` }
        };
        confirmationEvent.state_after.confirmation_id = confirmationEvent.event_id;
        confirmationEvents.push(confirmationEvent);
        latestConfirmationAnchorPoint = anchorPoint;
        latestConfirmation = {
          confirmation_id: confirmationEvent.event_id,
          direction,
          confirmed_at: confirmationEvent.simulation_time,
          confirmed_at_ms: breakoutEndMs,
          trigger_point_id: triggerPoint.point_id,
          anchor_point_id: anchorPoint?.point_id || anchorPoint?.key || null,
          anchor_type: anchorPoint?.type || null,
          anchor_price: numberOrNull(anchorPoint?.pivot_price),
          anchor_time: anchorPoint?.pivot_time || null,
          confirmation_signature: signature,
          breakout_threshold_point_id: thresholdPoint?.point_id || thresholdPoint?.key || null,
          breakout_threshold_price: numberOrNull(thresholdPoint?.pivot_price),
          opportunity_policy: 'ONE_NORMAL_ENTRY_AT_DOW_BREAKOUT_IF_R2_READY_ELSE_FIRST_R2_TOUCH'
        };
        currentState = direction;
        lastDirectionalState = direction;
        latestEvaluation = {
          state: direction,
          high_relation: direction === 'UP' ? 'BREAKOUT_HIGHER' : latestEvaluation?.high_relation || 'MIXED',
          low_relation: direction === 'DOWN' ? 'BREAKOUT_LOWER' : latestEvaluation?.low_relation || 'MIXED',
          directional_bias: direction,
          reason_codes: [...confirmationEvent.reason_codes],
          comparison_points: confirmationEvent.comparison_points,
          trigger_point: triggerPoint
        };
        directionalRegime = direction;
        directionalRegimeStartedAt = confirmationEvent.simulation_time;
        directionalRegimeTriggerEventId = confirmationEvent.event_id;
        directionalRegimeAnchorPoint = anchorPoint;
        directionalRegimeAnchorSelectionPolicy = direction === 'UP'
          ? 'PREVIOUS_LOW_FROM_M5_BREAKOUT_CONFIRMATION'
          : 'PREVIOUS_HIGH_FROM_M5_BREAKOUT_CONFIRMATION';
        directionalRegimeAnchorFallbackUsed = false;
        directionalRegimeResetAt = '';
        directionalRegimeResetEventId = '';
        directionalRegimeResetReason = '';
        if (expansionDetectionRegime !== direction) {
          expansionDetectionRegime = direction;
          expansionDetectionStartedAt = confirmationEvent.simulation_time;
          expansionDetectionTriggerEventId = confirmationEvent.event_id;
          expansionDetectionAnchorPoint = anchorPoint;
          expansionDetectionAnchorSelectionPolicy = direction === 'UP'
            ? 'PREVIOUS_LOW_AS_EXPANSION_DETECTION_ORIGIN'
            : 'PREVIOUS_HIGH_AS_EXPANSION_DETECTION_ORIGIN';
          expansionDetectionAnchorFallbackUsed = false;
        }
      }
    }

    if (!latestEvaluation) {
      latestEvaluation = {
        state: 'UNDETERMINED',
        high_relation: 'INSUFFICIENT',
        low_relation: 'INSUFFICIENT',
        directional_bias: null,
        reason_codes: ['DOW_UNDETERMINED', 'NO_CONFIRMED_STRUCTURE_POINTS'],
        comparison_points: { previous_high: null, current_high: null, previous_low: null, current_low: null },
        trigger_point: null
      };
      currentState = 'UNDETERMINED';
    }
    if (events.length) events[events.length - 1].display.visible = true;
    const previousTrendState = timeline.length >= 2 ? timeline[timeline.length - 2].to : (timeline.length ? timeline[0].from : null);
    return {
      status: lookaheadCount ? 'lookahead_detected' : `ready_${String(currentState || 'UNDETERMINED').toLowerCase()}`,
      evaluator_id: DOW_TREND_EVALUATOR_ID,
      trend_state: currentState || 'UNDETERMINED',
      previous_trend_state: previousTrendState,
      last_directional_state: lastDirectionalState,
      directional_bias: latestEvaluation.directional_bias || null,
      high_relation: latestEvaluation.high_relation,
      low_relation: latestEvaluation.low_relation,
      reason_codes: latestEvaluation.reason_codes || [],
      comparison_points: latestEvaluation.comparison_points,
      used_swing_point_ids: [
        latestEvaluation.comparison_points?.previous_high?.point_id,
        latestEvaluation.comparison_points?.current_high?.point_id,
        latestEvaluation.comparison_points?.previous_low?.point_id,
        latestEvaluation.comparison_points?.current_low?.point_id
      ].filter(Boolean),
      source_confirmed_point_count: confirmedPoints.length,
      accepted_structure_point_count: structure.length,
      ignored_same_type_non_extreme_count: ignoredSameTypeNonExtreme,
      accepted_structure_points: structure.map(dowPointSummary),
      state_change_count: events.length,
      confirmation_count: confirmationEvents.length,
      timeline,
      state_change_events: events,
      confirmation_events: confirmationEvents,
      normal_dow_confirmation: latestConfirmation ? cloneJsonValue(latestConfirmation) : null,
      directional_regime: directionalRegime ? {
        direction: directionalRegime,
        started_at: directionalRegimeStartedAt,
        trigger_event_id: directionalRegimeTriggerEventId,
        anchor_point_id: directionalRegimeAnchorPoint?.point_id || directionalRegimeAnchorPoint?.key || null,
        anchor_type: directionalRegimeAnchorPoint?.type || null,
        anchor_price: numberOrNull(directionalRegimeAnchorPoint?.pivot_price),
        anchor_time: directionalRegimeAnchorPoint?.pivot_time || null,
        anchor_selection_policy: directionalRegimeAnchorSelectionPolicy,
        anchor_selection_fallback_used: directionalRegimeAnchorFallbackUsed,
        reset_policy: 'RESET_ON_REVERSAL_WATCH_NO_TREND_UNDETERMINED',
        same_direction_reconfirmation_policy: 'ADOPT_NEW_PREVIOUS_SWING_AFTER_RESET'
      } : null,
      directional_regime_reset: directionalRegimeResetAt ? {
        reset_at: directionalRegimeResetAt,
        reset_event_id: directionalRegimeResetEventId,
        reason_code: directionalRegimeResetReason
      } : null,
      normal_dow_structure_break: cloneJsonValue(latestNormalDowStructureBreak),
      dow_adopted_anchor_point: dowPointSummary(latestConfirmationAnchorPoint || directionalRegimeAnchorPoint),
      expansion_detection_regime: expansionDetectionRegime ? {
        direction: expansionDetectionRegime,
        started_at: expansionDetectionStartedAt,
        trigger_event_id: expansionDetectionTriggerEventId,
        anchor_point_id: expansionDetectionAnchorPoint?.point_id || expansionDetectionAnchorPoint?.key || null,
        anchor_type: expansionDetectionAnchorPoint?.type || null,
        anchor_price: numberOrNull(expansionDetectionAnchorPoint?.pivot_price),
        anchor_time: expansionDetectionAnchorPoint?.pivot_time || null,
        anchor_selection_policy: expansionDetectionAnchorSelectionPolicy,
        anchor_selection_fallback_used: expansionDetectionAnchorFallbackUsed,
        reset_policy: 'OPPOSITE_DIRECTIONAL_DOW_CONFIRMED',
        non_directional_state_policy: 'KEEP_EXPANSION_DETECTION_ANCHOR'
      } : null,
      expansion_detection_anchor_point: dowPointSummary(expansionDetectionAnchorPoint),
      lookahead_detected: lookaheadCount > 0,
      entry_permission: 'NOT_EVALUATED'
    };
  }

  function buildDowTrendEvaluationSnapshot(state, draft, swingSnapshot, candleSync) {
    const errors = [];
    const warnings = [];
    const policy = { ...(draft?.dow_trend_policy || {}) };
    const timeframes = {};
    const stateChangeEvents = [];
    const confirmationEvents = [];
    const referenceMs = numberOrNull(candleSync?.reference?.reference_close_ms);
    REQUIRED_SIMULATION_TIMEFRAMES.forEach(timeframe => {
      const swingTimeframe = swingSnapshot?.timeframes?.[timeframe];
      if (!swingTimeframe) {
        errors.push(`${timeframe}: Swing Point snapshot is missing.`);
        timeframes[timeframe] = { status: 'missing_swing_snapshot', trend_state: 'UNDETERMINED', state_change_events: [], confirmation_events: [], normal_dow_confirmation: null };
        return;
      }
      const evaluated = replayDowTrendForTimeframe(timeframe, swingTimeframe, referenceMs, candleSync?.timeframes?.[timeframe]?.latest_confirmed_bar || null, timeframe === 'M5' ? (state?.simulationAllRows || []) : []);
      if (evaluated.lookahead_detected) errors.push(`${timeframe}: Dow evaluator received swing confirmed after M5 reference close.`);
      if (evaluated.trend_state === 'UNDETERMINED') warnings.push(`${timeframe}: Dow TrendState is UNDETERMINED because confirmed high/low pairs are insufficient.`);
      timeframes[timeframe] = evaluated;
      stateChangeEvents.push(...(evaluated.state_change_events || []));
      confirmationEvents.push(...(evaluated.confirmation_events || []));
    });
    return {
      schema_version: 'fx_dow_trend_evaluation_snapshot_v0_1',
      kind: 'fx_dow_trend_evaluation_snapshot',
      status: errors.length ? 'invalid' : 'ready',
      phase: 'v0.9.0.05-dow-trend-evaluator',
      created_at: nowLocalIso(),
      evaluator: {
        evaluator_id: String(policy.evaluator_id || DOW_TREND_EVALUATOR_ID),
        input_source: String(policy.input_source || 'run_snapshot.swing_point_detection.timeframes[].points'),
        confirmed_points_only: policy.confirmed_points_only === true,
        pending_candidate_usage: String(policy.pending_candidate_usage || 'forbidden'),
        timeframe_specific_class: String(policy.timeframe_specific_class || 'forbidden'),
        comparison_rule: String(policy.comparison_rule || 'last_two_structure_highs_and_last_two_structure_lows'),
        same_type_policy: String(policy.same_type_policy || 'replace_only_when_more_extreme'),
        equal_price_policy: String(policy.equal_price_policy || 'NO_TREND'),
        mixed_structure_policy: String(policy.mixed_structure_policy || ''),
        insufficient_structure_policy: String(policy.insufficient_structure_policy || 'UNDETERMINED'),
        state_change_event_only: policy.state_change_event_only === true,
        confirmation_event_enabled: policy.confirmation_event_enabled !== false,
        confirmation_event_policy: String(policy.confirmation_event_policy || 'each_complete_directional_structure_pair_advance'),
        entry_permission_output: String(policy.entry_permission_output || 'forbidden'),
        no_lookahead: policy.no_lookahead === true
      },
      timeframes,
      state_change_events: stateChangeEvents,
      confirmation_events: confirmationEvents,
      validation: { valid: errors.length === 0, checked_at: nowLocalIso(), errors, warnings, no_lookahead: errors.every(message => !message.includes('reference close')) },
      teacher_guard: 'Dow TrendState observation only. TrendState is not Entry Permission. Cycle/HSI/Entry/Close decisions are not executed.'
    };
  }

  function dowTrendSnapshotPreview(snapshot) {
    if (!snapshot) return null;
    const copy = cloneJsonValue(snapshot);
    Object.values(copy.timeframes || {}).forEach(item => {
      if (Array.isArray(item.accepted_structure_points)) item.accepted_structure_points = `[${item.accepted_structure_points.length} points omitted from preview]`;
      if (Array.isArray(item.timeline)) item.timeline = `[${item.timeline.length} state changes omitted from preview]`;
      if (Array.isArray(item.state_change_events)) item.state_change_events = `[${item.state_change_events.length} events omitted from preview]`;
      if (Array.isArray(item.confirmation_events)) item.confirmation_events = `[${item.confirmation_events.length} events omitted from preview]`;
    });
    if (Array.isArray(copy.state_change_events)) copy.state_change_events = `[${copy.state_change_events.length} events omitted from preview]`;
    if (Array.isArray(copy.confirmation_events)) copy.confirmation_events = `[${copy.confirmation_events.length} events omitted from preview]`;
    return copy;
  }

  function mergeDowTrendChartEvents(existingEvents, dowSnapshot) {
    const kept = (existingEvents || []).filter(event => event?.generated_by !== DOW_TREND_GENERATOR);
    const projected = (dowSnapshot?.state_change_events || []).filter(event => event?.display?.visible === true);
    return [...kept, ...projected];
  }


  function cycleThresholds(profile) {
    const raw = profile?.cycle?.phase_thresholds || {};
    return {
      early_max_bars: Math.max(0, Math.floor(numberOrNull(raw.early_max_bars) ?? 0)),
      middle_max_bars: Math.max(1, Math.floor(numberOrNull(raw.middle_max_bars) ?? 1)),
      late_from_bars: Math.max(2, Math.floor(numberOrNull(raw.late_from_bars) ?? 2))
    };
  }

  function cyclePhaseForElapsed(elapsedBars, thresholds) {
    const elapsed = Math.max(0, Math.floor(numberOrNull(elapsedBars) ?? 0));
    if (!thresholds) return 'UNDETERMINED';
    if (elapsed <= thresholds.early_max_bars) return 'EARLY';
    if (elapsed <= thresholds.middle_max_bars) return 'MIDDLE';
    return 'LATE';
  }

  function cycleContextState(profile, phase) {
    const map = profile?.cycle?.context_state_map || {};
    return String(map[String(phase || 'UNDETERMINED').toUpperCase()] || map.UNDETERMINED || 'UNKNOWN');
  }

  function cycleOriginDirection(point) {
    if (!point) return 'UNKNOWN';
    return point.type === 'swing_low' ? 'UP_CYCLE' : point.type === 'swing_high' ? 'DOWN_CYCLE' : 'UNKNOWN';
  }

  function cycleOriginSummary(point) {
    if (!point) return null;
    return {
      point_id: point.point_id || point.key || '',
      type: point.type || '',
      direction: cycleOriginDirection(point),
      pivot_time: point.pivot_time || '',
      pivot_ms: numberOrNull(point.pivot_ms),
      confirmed_time: point.confirmed_time || '',
      confirmed_ms: numberOrNull(point.confirmed_ms),
      pivot_price: numberOrNull(point.pivot_price),
      basis_role: point.basis_role || point.role || '',
      confirm_bars: numberOrNull(point.confirm_bars)
    };
  }

  function cycleFirstRowIndexAfter(rows, originPivotMs) {
    const list = rows || [];
    const origin = numberOrNull(originPivotMs);
    if (origin == null || !list.length) return list.length;
    let lo = 0;
    let hi = list.length;
    while (lo < hi) {
      const mid = (lo + hi) >> 1;
      const startMs = numberOrNull(list[mid]?.start_ms) ?? rowTimeMs(list[mid]) ?? Number.MAX_SAFE_INTEGER;
      if (startMs <= origin) lo = mid + 1;
      else hi = mid;
    }
    return lo;
  }

  function cycleLastConfirmedRowIndexAt(rows, untilMs) {
    const list = rows || [];
    const until = numberOrNull(untilMs);
    if (until == null || !list.length) return -1;
    let lo = 0;
    let hi = list.length;
    while (lo < hi) {
      const mid = (lo + hi) >> 1;
      const startMs = numberOrNull(list[mid]?.start_ms) ?? rowTimeMs(list[mid]);
      const endMs = numberOrNull(list[mid]?.end_ms) ?? startMs ?? Number.MAX_SAFE_INTEGER;
      if (endMs <= until) lo = mid + 1;
      else hi = mid;
    }
    return lo - 1;
  }

  function cycleElapsedBars(rows, originPivotMs, untilMs) {
    const list = rows || [];
    const origin = numberOrNull(originPivotMs);
    const until = numberOrNull(untilMs);
    if (origin == null || until == null || !list.length) return 0;
    const first = cycleFirstRowIndexAfter(list, origin);
    const last = cycleLastConfirmedRowIndexAt(list, until);
    return last < first ? 0 : (last - first + 1);
  }

  function cycleRowAtElapsed(rows, originPivotMs, targetElapsedBars) {
    const list = rows || [];
    const origin = numberOrNull(originPivotMs);
    const target = Math.max(0, Math.floor(numberOrNull(targetElapsedBars) ?? 0));
    if (origin == null || target <= 0 || !list.length) return null;
    const first = cycleFirstRowIndexAfter(list, origin);
    const index = first + target - 1;
    return index >= 0 && index < list.length ? list[index] : null;
  }

  function cycleEventId(timeframe, originPoint, eventType, suffix = '') {
    return `cycle_evt_${String(timeframe || '').toLowerCase()}_${stableSwingToken(originPoint?.point_id || originPoint?.key || originPoint?.confirmed_time)}_${stableSwingToken(eventType)}${suffix ? '_' + stableSwingToken(suffix) : ''}`;
  }

  function cycleStateAtTime(profile, rows, originPoint, atMs) {
    if (!originPoint) {
      return {
        origin: null,
        direction: 'UNKNOWN',
        elapsed_bars: 0,
        phase: 'UNDETERMINED',
        context_role: String(profile?.cycle?.context_role || ''),
        context_state: cycleContextState(profile, 'UNDETERMINED'),
        progress_to_late: 0,
        action_permission: 'NOT_EVALUATED'
      };
    }
    const thresholds = cycleThresholds(profile);
    const elapsedBars = cycleElapsedBars(rows, originPoint.pivot_ms, atMs);
    const phase = cyclePhaseForElapsed(elapsedBars, thresholds);
    return {
      origin: cycleOriginSummary(originPoint),
      direction: cycleOriginDirection(originPoint),
      elapsed_bars: elapsedBars,
      phase,
      context_role: String(profile?.cycle?.context_role || ''),
      context_state: cycleContextState(profile, phase),
      progress_to_late: thresholds.late_from_bars > 0 ? Math.round(Math.min(1, elapsedBars / thresholds.late_from_bars) * 1000) / 1000 : 0,
      action_permission: 'NOT_EVALUATED'
    };
  }

  function cyclePhaseReasonCodes(phase) {
    const value = String(phase || 'UNDETERMINED').toUpperCase();
    if (value === 'EARLY') return ['CYCLE_PHASE_EARLY'];
    if (value === 'MIDDLE') return ['CYCLE_PHASE_MIDDLE'];
    if (value === 'LATE') return ['CYCLE_PHASE_LATE'];
    return ['CYCLE_PHASE_UNDETERMINED'];
  }

  function replayCyclePositionForTimeframe(timeframe, profile, swingTimeframe, confirmedRows, referenceMs) {
    const tf = String(timeframe || '').toUpperCase();
    const rows = (confirmedRows || []).filter(row => {
      const endMs = numberOrNull(row?.end_ms) ?? rowTimeMs(row);
      return referenceMs == null || endMs == null || endMs <= referenceMs;
    });
    const sourcePoints = Array.isArray(swingTimeframe?.points) ? swingTimeframe.points : [];
    const historicalOrigins = sourcePoints
      .filter(point => point && ['basis_active', 'basis_retired'].includes(String(point.basis_role || point.role || '').toLowerCase()))
      .filter(point => numberOrNull(point.confirmed_ms) != null && (referenceMs == null || numberOrNull(point.confirmed_ms) <= referenceMs))
      .sort((a, b) => (numberOrNull(a.confirmed_ms) ?? 0) - (numberOrNull(b.confirmed_ms) ?? 0) || (numberOrNull(a.pivot_ms) ?? 0) - (numberOrNull(b.pivot_ms) ?? 0));
    const currentOrigins = sourcePoints
      .filter(point => point && String(point.basis_role || point.role || '').toLowerCase() === 'basis_active' && point.usable_as_basis === true)
      .filter(point => numberOrNull(point.confirmed_ms) != null && (referenceMs == null || numberOrNull(point.confirmed_ms) <= referenceMs))
      .sort((a, b) => (numberOrNull(a.pivot_ms) ?? 0) - (numberOrNull(b.pivot_ms) ?? 0) || (numberOrNull(a.confirmed_ms) ?? 0) - (numberOrNull(b.confirmed_ms) ?? 0));
    const currentOrigin = currentOrigins.length ? currentOrigins[currentOrigins.length - 1] : null;
    const events = [];
    const timeline = [];
    let previousOrigin = null;
    let previousState = cycleStateAtTime(profile, rows, null, referenceMs);
    let lookaheadCount = 0;

    historicalOrigins.forEach((originPoint, index) => {
      const confirmedMs = numberOrNull(originPoint.confirmed_ms);
      if (referenceMs != null && confirmedMs != null && confirmedMs > referenceMs) {
        lookaheadCount += 1;
        return;
      }
      if (previousOrigin && numberOrNull(originPoint.pivot_ms) != null && numberOrNull(previousOrigin.pivot_ms) != null && originPoint.pivot_ms <= previousOrigin.pivot_ms) return;
      const adoptionMs = confirmedMs ?? numberOrNull(originPoint.pivot_ms) ?? referenceMs;
      const priorAtAdoption = previousOrigin ? cycleStateAtTime(profile, rows, previousOrigin, adoptionMs) : cycleStateAtTime(profile, rows, null, adoptionMs);
      const nextState = cycleStateAtTime(profile, rows, originPoint, adoptionMs);
      const originEvent = {
        event_id: cycleEventId(tf, originPoint, 'origin_changed'),
        source_type: SIMULATION_TRACE_SOURCE_TYPE,
        generated_by: CYCLE_POSITION_GENERATOR,
        evaluator_id: CYCLE_POSITION_EVALUATOR_ID,
        event_type: 'cycle_origin_changed',
        simulation_time: originPoint.confirmed_time || originPoint.pivot_time || '',
        timeframe: tf,
        panel: tf,
        price: numberOrNull(originPoint.pivot_price),
        summary: `${tf} Cycle起点を${originPoint.type === 'swing_low' ? '直近確定安値' : '直近確定高値'}へ更新。${nextState.phase} / ${nextState.elapsed_bars} bars。`,
        reason_codes: ['CYCLE_ORIGIN_NEWER_USABLE_SWING', originPoint.type === 'swing_low' ? 'ORIGIN_SWING_LOW' : 'ORIGIN_SWING_HIGH', ...cyclePhaseReasonCodes(nextState.phase)],
        rule_ids: ['rule_cycle_latest_confirmed_usable_swing_origin', 'rule_cycle_explicit_phase_thresholds', 'rule_cycle_state_not_action_permission'],
        cause_event_ids: [dowPointConfirmedEventId(originPoint)].filter(Boolean),
        origin_swing_point_id: originPoint.point_id || originPoint.key || '',
        upper_state_summary: { [tf]: `${nextState.phase} / ${nextState.context_role}:${nextState.context_state}`, action_permission: 'NOT_EVALUATED' },
        state_before: priorAtAdoption,
        state_after: nextState,
        thresholds: cycleThresholds(profile),
        display: { visible: false, open: false, pinned: false, style: `cycle_origin_${String(nextState.phase || '').toLowerCase()}` }
      };
      events.push(originEvent);
      timeline.push({ event_id: originEvent.event_id, at: originEvent.simulation_time, event_type: originEvent.event_type, origin_point_id: originEvent.origin_swing_point_id, from_phase: priorAtAdoption.phase, to_phase: nextState.phase, elapsed_bars: nextState.elapsed_bars });

      const nextOrigin = historicalOrigins[index + 1] || null;
      const segmentEndMs = Math.min(referenceMs ?? Number.MAX_SAFE_INTEGER, numberOrNull(nextOrigin?.confirmed_ms) ?? Number.MAX_SAFE_INTEGER);
      const thresholds = cycleThresholds(profile);
      [
        { phase: 'MIDDLE', elapsed: thresholds.early_max_bars + 1 },
        { phase: 'LATE', elapsed: thresholds.late_from_bars }
      ].forEach(transition => {
        const row = cycleRowAtElapsed(rows, originPoint.pivot_ms, transition.elapsed);
        const transitionMs = numberOrNull(row?.end_ms) ?? rowTimeMs(row);
        if (!row || transitionMs == null || transitionMs < adoptionMs || transitionMs >= segmentEndMs) return;
        const beforePhase = transition.phase === 'MIDDLE' ? 'EARLY' : 'MIDDLE';
        const afterState = cycleStateAtTime(profile, rows, originPoint, transitionMs);
        const phaseEvent = {
          event_id: cycleEventId(tf, originPoint, 'phase_changed', transition.phase),
          source_type: SIMULATION_TRACE_SOURCE_TYPE,
          generated_by: CYCLE_POSITION_GENERATOR,
          evaluator_id: CYCLE_POSITION_EVALUATOR_ID,
          event_type: 'cycle_phase_changed',
          simulation_time: formatRowDateTime(transitionMs) || row.datetime || row.time || '',
          timeframe: tf,
          panel: tf,
          price: numberOrNull(row?.close) ?? numberOrNull(originPoint.pivot_price),
          summary: `${tf} Cycleが${beforePhase}から${transition.phase}へ移行。起点から${afterState.elapsed_bars}本。`,
          reason_codes: ['CYCLE_PHASE_THRESHOLD_REACHED', ...cyclePhaseReasonCodes(transition.phase)],
          rule_ids: ['rule_cycle_explicit_phase_thresholds', 'rule_cycle_elapsed_confirmed_bars', 'rule_cycle_state_not_action_permission'],
          cause_event_ids: [originEvent.event_id],
          origin_swing_point_id: originPoint.point_id || originPoint.key || '',
          upper_state_summary: { [tf]: `${transition.phase} / ${afterState.context_role}:${afterState.context_state}`, action_permission: 'NOT_EVALUATED' },
          state_before: { ...afterState, phase: beforePhase, context_state: cycleContextState(profile, beforePhase) },
          state_after: afterState,
          thresholds,
          display: { visible: false, open: false, pinned: false, style: `cycle_phase_${String(transition.phase).toLowerCase()}` }
        };
        events.push(phaseEvent);
        timeline.push({ event_id: phaseEvent.event_id, at: phaseEvent.simulation_time, event_type: phaseEvent.event_type, origin_point_id: phaseEvent.origin_swing_point_id, from_phase: beforePhase, to_phase: transition.phase, elapsed_bars: afterState.elapsed_bars });
      });
      previousOrigin = originPoint;
      previousState = nextState;
    });

    const currentState = cycleStateAtTime(profile, rows, currentOrigin, referenceMs);
    const orderedEvents = events.sort((a, b) => (parseDateTimeMs(a.simulation_time) ?? 0) - (parseDateTimeMs(b.simulation_time) ?? 0) || String(a.event_id).localeCompare(String(b.event_id)));
    const tfEvents = orderedEvents.filter(event => event.timeframe === tf);
    if (tfEvents.length) tfEvents[tfEvents.length - 1].display.visible = true;
    return {
      status: lookaheadCount ? 'lookahead_detected' : currentOrigin ? `ready_${String(currentState.phase).toLowerCase()}` : 'undetermined_no_origin',
      evaluator_id: CYCLE_POSITION_EVALUATOR_ID,
      origin_policy: String(profile?.cycle?.origin_policy || ''),
      origin: currentState.origin,
      direction: currentState.direction,
      elapsed_bars: currentState.elapsed_bars,
      phase: currentState.phase,
      context_role: currentState.context_role,
      context_state: currentState.context_state,
      progress_to_late: currentState.progress_to_late,
      thresholds: cycleThresholds(profile),
      source_origin_count: historicalOrigins.length,
      current_origin_candidate_count: currentOrigins.length,
      origin_change_count: orderedEvents.filter(event => event.event_type === 'cycle_origin_changed').length,
      phase_change_count: orderedEvents.filter(event => event.event_type === 'cycle_phase_changed').length,
      timeline,
      state_change_events: orderedEvents,
      lookahead_detected: lookaheadCount > 0,
      action_permission: 'NOT_EVALUATED'
    };
  }

  function buildCyclePositionEvaluationSnapshot(state, draft, swingSnapshot, candleSync) {
    const errors = [];
    const warnings = [];
    const policy = { ...(draft?.cycle_position_policy || {}) };
    const sourceRows = simulationCandleSourceRows(state);
    const timeframes = {};
    const stateChangeEvents = [];
    const referenceMs = numberOrNull(candleSync?.reference?.reference_close_ms);
    REQUIRED_SIMULATION_TIMEFRAMES.forEach(timeframe => {
      const profile = simulationProfileForTimeframe(draft, timeframe);
      const swingTimeframe = swingSnapshot?.timeframes?.[timeframe];
      const confirmedCount = Math.max(0, Math.floor(numberOrNull(candleSync?.timeframes?.[timeframe]?.available_confirmed_bars) ?? 0));
      const rows = (sourceRows[timeframe] || []).slice(0, confirmedCount);
      if (!profile || !swingTimeframe) {
        errors.push(`${timeframe}: Cycle evaluator input is missing.`);
        timeframes[timeframe] = { status: 'missing_input', phase: 'UNDETERMINED', state_change_events: [] };
        return;
      }
      const evaluated = replayCyclePositionForTimeframe(timeframe, profile, swingTimeframe, rows, referenceMs);
      if (evaluated.lookahead_detected) errors.push(`${timeframe}: Cycle evaluator received origin confirmed after M5 reference close.`);
      if (!evaluated.origin) warnings.push(`${timeframe}: Cycle origin is UNDETERMINED because no confirmed usable Swing exists.`);
      timeframes[timeframe] = evaluated;
      stateChangeEvents.push(...(evaluated.state_change_events || []));
    });
    return {
      schema_version: 'fx_cycle_position_evaluation_snapshot_v0_1',
      kind: 'fx_cycle_position_evaluation_snapshot',
      status: errors.length ? 'invalid' : 'ready',
      phase: 'v0.9.0.06-cycle-position-evaluator',
      created_at: nowLocalIso(),
      evaluator: {
        evaluator_id: String(policy.evaluator_id || CYCLE_POSITION_EVALUATOR_ID),
        input_source: String(policy.input_source || ''),
        origin_selection: String(policy.origin_selection || ''),
        candidate_usage: String(policy.candidate_usage || 'forbidden'),
        retired_usage_for_current_origin: String(policy.retired_usage_for_current_origin || 'forbidden'),
        historical_retired_origin_replay: policy.historical_retired_origin_replay === true,
        timeframe_specific_class: String(policy.timeframe_specific_class || 'forbidden'),
        phase_threshold_source: String(policy.phase_threshold_source || ''),
        context_mapping_source: String(policy.context_mapping_source || ''),
        elapsed_bar_rule: String(policy.elapsed_bar_rule || ''),
        action_permission_output: String(policy.action_permission_output || 'forbidden'),
        no_lookahead: policy.no_lookahead === true
      },
      timeframes,
      state_change_events: stateChangeEvents,
      validation: { valid: errors.length === 0, checked_at: nowLocalIso(), errors, warnings, no_lookahead: errors.every(message => !message.includes('reference close')) },
      teacher_guard: 'Cycle Position observation only. EARLY/MIDDLE/LATE and context state are not Entry/Add-on/Exit permissions. HSI/Entry/Close decisions are not executed.'
    };
  }

  function cyclePositionSnapshotPreview(snapshot) {
    if (!snapshot) return null;
    const copy = cloneJsonValue(snapshot);
    Object.values(copy.timeframes || {}).forEach(item => {
      if (Array.isArray(item.timeline)) item.timeline = `[${item.timeline.length} cycle changes omitted from preview]`;
      if (Array.isArray(item.state_change_events)) item.state_change_events = `[${item.state_change_events.length} events omitted from preview]`;
    });
    if (Array.isArray(copy.state_change_events)) copy.state_change_events = `[${copy.state_change_events.length} events omitted from preview]`;
    return copy;
  }

  function mergeCyclePositionChartEvents(existingEvents, cycleSnapshot) {
    const kept = (existingEvents || []).filter(event => event?.generated_by !== CYCLE_POSITION_GENERATOR);
    const projected = (cycleSnapshot?.state_change_events || []).filter(event => event?.display?.visible === true);
    return [...kept, ...projected];
  }

  function hsiAnchorStableId(timeframe, point) {
    return `hsi_anchor_${String(timeframe || '').toLowerCase()}_${stableSwingToken(point?.point_id || point?.key || point?.pivot_time)}`;
  }

  function hsiAnchorDirection(point) {
    if (point?.type === 'swing_low') return 'UP';
    if (point?.type === 'swing_high') return 'DOWN';
    return 'UNRESOLVED';
  }

  function hsiDirectionContext(dowItem, cycleItem) {
    const trend = String(dowItem?.trend_state || '').toUpperCase();
    if (trend === 'UP' || trend === 'DOWN') return { direction: trend, source: 'DOW_TREND' };
    const cycleDirection = String(cycleItem?.direction || '').toUpperCase();
    if (cycleDirection === 'UP_CYCLE') return { direction: 'UP', source: 'CYCLE_DIRECTION' };
    if (cycleDirection === 'DOWN_CYCLE') return { direction: 'DOWN', source: 'CYCLE_DIRECTION' };
    return { direction: 'UNRESOLVED', source: 'NONE' };
  }

  function hsiAnchorFromSwing(timeframe, point, pending = false) {
    const lifecycle = pending ? 'CANDIDATE' : String(point?.lifecycle_status || '').toLowerCase() === 'retired' || String(point?.basis_role || '').toLowerCase() === 'basis_retired' ? 'RETIRED' : 'CONFIRMED';
    const eligible = lifecycle === 'CONFIRMED' && point?.usable_as_basis === true && String(point?.basis_role || '').toLowerCase() === 'basis_active';
    return {
      anchor_id: hsiAnchorStableId(timeframe, point),
      source_type: SIMULATION_HSI_ANCHOR_SOURCE_TYPE,
      timeframe: String(timeframe || '').toUpperCase(),
      source_swing_point_id: point?.point_id || point?.key || '',
      anchor_type: point?.type === 'swing_low' ? 'LOW' : point?.type === 'swing_high' ? 'HIGH' : 'UNKNOWN',
      direction: hsiAnchorDirection(point),
      pivot_time: point?.pivot_time || '',
      pivot_ms: numberOrNull(point?.pivot_ms),
      confirmed_time: pending ? '' : point?.confirmed_time || '',
      confirmed_ms: pending ? null : numberOrNull(point?.confirmed_ms),
      price: numberOrNull(point?.pivot_price),
      confirm_bars: numberOrNull(point?.confirm_bars),
      lifecycle_status: lifecycle,
      adoption_status: lifecycle === 'RETIRED' ? 'RETIRED' : eligible ? 'AVAILABLE' : 'NOT_ELIGIBLE',
      eligible_for_resolver: eligible,
      roles: eligible ? ['STRUCTURE_REFERENCE'] : [],
      reason_codes: pending ? ['HSI_ANCHOR_FROM_PENDING_SWING', 'CANDIDATE_NOT_RESOLVABLE'] : lifecycle === 'RETIRED' ? ['HSI_ANCHOR_FROM_RETIRED_SWING', 'RETAINED_FOR_TRACE'] : eligible ? ['HSI_ANCHOR_FROM_CONFIRMED_ACTIVE_SWING', 'RESOLVER_ELIGIBLE'] : ['HSI_ANCHOR_FROM_CONFIRMED_NON_ACTIVE_SWING', 'NOT_RESOLVER_ELIGIBLE'],
      rule_ids: ['rule_hsi_anchor_from_swing_identity', 'rule_hsi_anchor_status_role_separation', 'rule_hsi_anchor_no_action_permission'],
      cause_event_ids: [pending ? sharedSwingPointEventId(point, 'candidate') : dowPointConfirmedEventId(point)].filter(Boolean),
      action_permission: 'NOT_EVALUATED'
    };
  }


  function hsiAnchorFromDowAdoption(timeframe, dowItem) {
    const regime = dowItem?.directional_regime || {};
    const confirmation = dowItem?.normal_dow_confirmation || {};
    if (!confirmation?.confirmation_id) return null;
    const point = dowItem?.dow_adopted_anchor_point || null;
    const direction = String(confirmation?.direction || '').toUpperCase();
    const expectedType = direction === 'UP' ? 'swing_low' : direction === 'DOWN' ? 'swing_high' : '';
    if (!point || !expectedType || String(point?.type || '') !== expectedType) return null;
    const price = numberOrNull(point?.pivot_price);
    if (price == null) return null;
    return {
      anchor_id: hsiAnchorStableId(timeframe, point),
      source_type: SIMULATION_HSI_ANCHOR_SOURCE_TYPE,
      timeframe: String(timeframe || '').toUpperCase(),
      source_swing_point_id: point?.point_id || point?.key || '',
      anchor_type: expectedType === 'swing_low' ? 'LOW' : 'HIGH',
      direction,
      pivot_time: point?.pivot_time || '',
      pivot_ms: numberOrNull(point?.pivot_ms),
      confirmed_time: confirmation?.confirmed_at || point?.confirmed_time || regime?.started_at || '',
      confirmed_ms: numberOrNull(confirmation?.confirmed_at_ms ?? point?.confirmed_ms),
      price,
      confirm_bars: numberOrNull(point?.confirm_bars),
      lifecycle_status: 'CONFIRMED',
      adoption_status: 'ADOPTED',
      eligible_for_resolver: true,
      roles: ['STRUCTURE_REFERENCE', 'NORMAL_DOW_ENTRY_REFERENCE'],
      reason_codes: ['HSI_ANCHOR_FROM_DOW_CONFIRMATION_EVENT', 'DOW_ORIGIN_PREVIOUS_SWING_ADOPTED', 'DOW_CONFIRMATION_HSI_ANCHOR_FIXED', `DIRECTION_FROM_DOW_${direction}`],
      rule_ids: ['rule_normal_hsi_anchor_adopted_by_dow_confirmation', 'rule_normal_hsi_anchor_uses_previous_structure_origin', 'rule_one_normal_entry_opportunity_per_dow_confirmation'],
      cause_event_ids: uniqueStrings([confirmation?.confirmation_id, regime?.trigger_event_id, dowPointConfirmedEventId(point)]),
      action_permission: 'NOT_EVALUATED',
      dow_confirmation_id: confirmation?.confirmation_id || null,
      dow_confirmation_at: confirmation?.confirmed_at || null,
      dow_confirmation_at_ms: numberOrNull(confirmation?.confirmed_at_ms),
      dow_regime: {
        direction,
        started_at: regime?.started_at || '',
        trigger_event_id: regime?.trigger_event_id || '',
        reset_policy: 'RESET_ON_REVERSAL_WATCH_NO_TREND_UNDETERMINED'
      }
    };
  }


  function hsiAnchorFromExpansionDetectionAdoption(timeframe, dowItem) {
    const regime = dowItem?.expansion_detection_regime || {};
    const point = dowItem?.expansion_detection_anchor_point || null;
    const direction = String(regime?.direction || '').toUpperCase();
    const expectedType = direction === 'UP' ? 'swing_low' : direction === 'DOWN' ? 'swing_high' : '';
    if (!point || !expectedType || String(point?.type || '') !== expectedType) return null;
    const price = numberOrNull(point?.pivot_price);
    if (price == null) return null;
    return {
      anchor_id: hsiAnchorStableId(timeframe, point),
      source_type: SIMULATION_HSI_ANCHOR_SOURCE_TYPE,
      timeframe: String(timeframe || '').toUpperCase(),
      source_swing_point_id: point?.point_id || point?.key || '',
      anchor_type: expectedType === 'swing_low' ? 'LOW' : 'HIGH',
      direction,
      pivot_time: point?.pivot_time || '',
      pivot_ms: numberOrNull(point?.pivot_ms),
      confirmed_time: point?.confirmed_time || regime?.started_at || '',
      confirmed_ms: numberOrNull(point?.confirmed_ms),
      price,
      confirm_bars: numberOrNull(point?.confirm_bars),
      lifecycle_status: 'CONFIRMED',
      adoption_status: 'ADOPTED',
      eligible_for_resolver: true,
      roles: ['STRUCTURE_REFERENCE', 'EXPANSION_DETECTION_REFERENCE'],
      reason_codes: ['HSI_ANCHOR_FROM_EXPANSION_DETECTION_REGIME', 'EXPANSION_DETECTION_ANCHOR_RETAINED_ACROSS_NON_DIRECTIONAL_STATE', `DIRECTION_FROM_DOW_${direction}`],
      rule_ids: ['rule_expansion_detection_anchor_uses_original_dow_origin', 'rule_expansion_detection_anchor_retained_across_reversal_watch'],
      cause_event_ids: uniqueStrings([regime?.trigger_event_id, dowPointConfirmedEventId(point)]),
      action_permission: 'NOT_EVALUATED',
      expansion_detection_regime: {
        direction,
        started_at: regime?.started_at || '',
        trigger_event_id: regime?.trigger_event_id || '',
        reset_policy: 'OPPOSITE_DIRECTIONAL_DOW_CONFIRMED',
        non_directional_state_policy: 'KEEP_EXPANSION_DETECTION_ANCHOR'
      }
    };
  }

  function hsiResolvedReference(purpose, anchor, reasonCodes = []) {
    return {
      purpose,
      status: anchor ? 'RESOLVED_REFERENCE' : 'UNRESOLVED',
      direction: anchor?.direction || 'UNRESOLVED',
      anchor_id: anchor?.anchor_id || null,
      anchor: hsiResolutionSummary(anchor),
      reason_codes: anchor ? uniqueStrings(reasonCodes) : ['DOW_ADOPTED_HSI_ANCHOR_UNRESOLVED'],
      action_permission: 'NOT_EVALUATED'
    };
  }

  function humanSavedHsiForTimeframe(state, timeframe) {
    const tf = String(timeframe || '').toUpperCase();
    return (state?.hsiAnnotations || []).filter(item => String(item?.source_type || '') === SAVED_HSI_SOURCE_TYPE && normalizePanelTimeframe(item?.timeframe || item?.panel || 'M5', 'M5') === tf);
  }

  function nearestHumanSavedHsi(anchor, humanItems) {
    if (!anchor || !(humanItems || []).length) return null;
    const anchorMs = numberOrNull(anchor.pivot_ms) ?? parseDateTimeMs(anchor.pivot_time);
    const anchorPrice = numberOrNull(anchor.price);
    const ranked = (humanItems || []).map(item => {
      const itemMs = parseDateTimeMs(item?.time);
      const itemPrice = numberOrNull(item?.price);
      return {
        item,
        time_distance_ms: anchorMs != null && itemMs != null ? Math.abs(anchorMs - itemMs) : null,
        price_distance: anchorPrice != null && itemPrice != null ? Math.abs(anchorPrice - itemPrice) : null
      };
    }).sort((a, b) => (a.time_distance_ms ?? Number.MAX_SAFE_INTEGER) - (b.time_distance_ms ?? Number.MAX_SAFE_INTEGER) || (a.price_distance ?? Number.MAX_VALUE) - (b.price_distance ?? Number.MAX_VALUE));
    const best = ranked[0];
    if (!best) return null;
    return {
      source_type: SAVED_HSI_SOURCE_TYPE,
      annotation_id: best.item.id || '',
      timeframe: String(best.item.timeframe || best.item.panel || ''),
      time: best.item.time || '',
      price: numberOrNull(best.item.price),
      direction: normalizeHsiDirection(best.item.hsi?.direction),
      scale: numberOrNull(best.item.hsi?.scale),
      time_distance_ms: best.time_distance_ms,
      price_distance: best.price_distance,
      relation: 'REFERENCE_ONLY_NOT_AUTO_ADOPTED'
    };
  }

  function hsiResolutionSummary(anchor) {
    if (!anchor) return null;
    return {
      anchor_id: anchor.anchor_id,
      anchor_type: anchor.anchor_type,
      direction: anchor.direction,
      pivot_time: anchor.pivot_time,
      price: anchor.price,
      lifecycle_status: anchor.lifecycle_status,
      adoption_status: anchor.adoption_status,
      roles: [...(anchor.roles || [])],
      dow_confirmation_id: anchor.dow_confirmation_id || null,
      dow_confirmation_at: anchor.dow_confirmation_at || null,
      dow_confirmation_at_ms: numberOrNull(anchor.dow_confirmation_at_ms)
    };
  }

  function resolveHsiPurpose(purpose, anchors, directionContext, cycleOriginPointId) {
    const direction = String(directionContext?.direction || 'UNRESOLVED').toUpperCase();
    const eligible = (anchors || []).filter(anchor => anchor.eligible_for_resolver === true);
    const aligned = direction === 'UP' || direction === 'DOWN' ? eligible.filter(anchor => anchor.direction === direction) : [];
    const ordered = [...aligned].sort((a, b) => (numberOrNull(a.pivot_ms) ?? 0) - (numberOrNull(b.pivot_ms) ?? 0));
    const cycleAnchor = eligible.find(anchor => anchor.source_swing_point_id === cycleOriginPointId) || null;
    if (purpose === 'confluence') {
      return {
        purpose,
        status: ordered.length ? 'RESOLVED_SET' : 'UNRESOLVED',
        direction,
        anchor_ids: ordered.map(anchor => anchor.anchor_id),
        anchors: ordered.map(hsiResolutionSummary),
        reason_codes: ordered.length ? ['ALL_ACTIVE_ALIGNED_ANCHORS', `DIRECTION_FROM_${directionContext.source}`] : ['NO_ACTIVE_ALIGNED_ANCHOR'],
        action_permission: 'NOT_EVALUATED'
      };
    }
    let selected = null;
    let reason = '';
    if (purpose === 'entry') {
      selected = ordered[ordered.length - 1] || null;
      reason = 'LATEST_ACTIVE_ALIGNED_ANCHOR';
    } else {
      selected = ordered[0] || cycleAnchor || null;
      reason = ordered[0] ? 'OLDEST_ACTIVE_ALIGNED_ANCHOR_IN_ANALYSIS_SCOPE' : cycleAnchor ? 'CYCLE_ORIGIN_FALLBACK_REFERENCE' : '';
    }
    return {
      purpose,
      status: selected ? 'RESOLVED_REFERENCE' : 'UNRESOLVED',
      direction,
      anchor_id: selected?.anchor_id || null,
      anchor: hsiResolutionSummary(selected),
      reason_codes: selected ? [reason, `DIRECTION_FROM_${directionContext.source}`] : ['NO_ACTIVE_ALIGNED_ANCHOR'],
      action_permission: 'NOT_EVALUATED'
    };
  }

  function hsiAnchorLifecycleEvent(timeframe, anchor, eventType, visible = false) {
    return {
      event_id: `hsi_evt_${stableSwingToken(anchor.anchor_id)}_${stableSwingToken(eventType)}`,
      source_type: SIMULATION_TRACE_SOURCE_TYPE,
      generated_by: HSI_ANCHOR_GENERATOR,
      registry_id: HSI_ANCHOR_REGISTRY_ID,
      resolver_id: HSI_ANCHOR_RESOLVER_ID,
      event_type: eventType,
      simulation_time: anchor.confirmed_time || anchor.pivot_time || '',
      timeframe: String(timeframe || '').toUpperCase(),
      panel: String(timeframe || '').toUpperCase(),
      price: numberOrNull(anchor.price),
      summary: `${String(timeframe || '').toUpperCase()} HSI Anchor ${anchor.anchor_type} ${anchor.lifecycle_status} / ${anchor.adoption_status} / ${(anchor.roles || []).join(', ') || 'NO_ROLE'}`,
      reason_codes: [...(anchor.reason_codes || [])],
      rule_ids: [...(anchor.rule_ids || [])],
      cause_event_ids: [...(anchor.cause_event_ids || [])],
      anchor_id: anchor.anchor_id,
      source_swing_point_id: anchor.source_swing_point_id,
      upper_state_summary: { [String(timeframe || '').toUpperCase()]: `HSI ${anchor.anchor_type}/${anchor.direction}`, action_permission: 'NOT_EVALUATED' },
      state_before: { lifecycle_status: anchor.lifecycle_status, adoption_status: eventType === 'hsi_anchor_adopted' ? 'AVAILABLE' : anchor.adoption_status },
      state_after: { lifecycle_status: anchor.lifecycle_status, adoption_status: anchor.adoption_status, roles: [...(anchor.roles || [])], action_permission: 'NOT_EVALUATED' },
      display: { visible, open: false, pinned: false, style: `hsi_anchor_${String(anchor.direction || '').toLowerCase()}` }
    };
  }

  function buildHsiAnchorRegistrySnapshot(state, draft, swingSnapshot, dowSnapshot, cycleSnapshot, candleSync) {
    const errors = [];
    const warnings = [];
    const policy = { ...(draft?.hsi_anchor_policy || {}) };
    const referenceMs = numberOrNull(candleSync?.reference?.reference_close_ms);
    const timeframes = {};
    const lifecycleEvents = [];
    REQUIRED_SIMULATION_TIMEFRAMES.forEach(timeframe => {
      const swingItem = swingSnapshot?.timeframes?.[timeframe];
      const dowItem = dowSnapshot?.timeframes?.[timeframe] || {};
      const cycleItem = cycleSnapshot?.timeframes?.[timeframe] || {};
      if (!swingItem) {
        errors.push(`${timeframe}: HSI Anchor Registry input swing snapshot is missing.`);
        timeframes[timeframe] = { status: 'missing_input', anchors: [], resolutions: {} };
        return;
      }
      const confirmedAnchors = (swingItem.points || []).map(point => hsiAnchorFromSwing(timeframe, point, false));
      const pendingAnchors = (swingItem.pending_candidates || []).map(point => hsiAnchorFromSwing(timeframe, point, true));
      const normalDowAnchor = hsiAnchorFromDowAdoption(timeframe, dowItem);
      const expansionDetectionAnchor = hsiAnchorFromExpansionDetectionAdoption(timeframe, dowItem);
      const anchors = [...confirmedAnchors, ...pendingAnchors];
      const mergeAdoptedAnchor = adoptedAnchor => {
        if (!adoptedAnchor) return;
        const existingIndex = anchors.findIndex(anchor => anchor.anchor_id === adoptedAnchor.anchor_id);
        if (existingIndex >= 0) {
          anchors[existingIndex] = {
            ...anchors[existingIndex],
            ...adoptedAnchor,
            roles: uniqueStrings([...(anchors[existingIndex].roles || []), ...(adoptedAnchor.roles || [])]),
            reason_codes: uniqueStrings([...(anchors[existingIndex].reason_codes || []), ...(adoptedAnchor.reason_codes || [])]),
            rule_ids: uniqueStrings([...(anchors[existingIndex].rule_ids || []), ...(adoptedAnchor.rule_ids || [])]),
            cause_event_ids: uniqueStrings([...(anchors[existingIndex].cause_event_ids || []), ...(adoptedAnchor.cause_event_ids || [])])
          };
        } else {
          anchors.push(adoptedAnchor);
        }
      };
      mergeAdoptedAnchor(normalDowAnchor);
      mergeAdoptedAnchor(expansionDetectionAnchor);
      anchors.sort((a, b) => (numberOrNull(a.pivot_ms) ?? 0) - (numberOrNull(b.pivot_ms) ?? 0) || String(a.anchor_id).localeCompare(String(b.anchor_id)));
      const lookahead = anchors.filter(anchor => numberOrNull(anchor.confirmed_ms) != null && referenceMs != null && anchor.confirmed_ms > referenceMs);
      if (lookahead.length) errors.push(`${timeframe}: ${lookahead.length} HSI Anchor(s) confirmed after M5 reference close.`);
      const normalRegimeDirection = String(dowItem?.normal_dow_confirmation?.direction || dowItem?.directional_regime?.direction || '').toUpperCase();
      const expansionRegimeDirection = String(dowItem?.expansion_detection_regime?.direction || '').toUpperCase();
      const normalDirectionContext = normalRegimeDirection === 'UP' || normalRegimeDirection === 'DOWN'
        ? { direction: normalRegimeDirection, source: 'NORMAL_DOW_DIRECTIONAL_REGIME' }
        : { direction: 'UNRESOLVED', source: 'NORMAL_DOW_NOT_DIRECTIONAL' };
      const expansionDirectionContext = expansionRegimeDirection === 'UP' || expansionRegimeDirection === 'DOWN'
        ? { direction: expansionRegimeDirection, source: 'EXPANSION_DETECTION_REGIME' }
        : hsiDirectionContext(dowItem, cycleItem);
      const cycleOriginPointId = cycleItem?.origin?.point_id || '';
      const resolutions = {};
      const expansionEntryCandidates = anchors.filter(anchor => anchor.anchor_id !== expansionDetectionAnchor?.anchor_id && anchor.anchor_id !== normalDowAnchor?.anchor_id);
      const expansionEntry = resolveHsiPurpose('entry', expansionEntryCandidates, expansionDirectionContext, cycleOriginPointId);
      resolutions.entry = hsiResolvedReference('entry', normalDowAnchor, ['DOW_CONFIRMATION_PREVIOUS_SWING_ADOPTED', 'ONE_NORMAL_ENTRY_OPPORTUNITY_PER_DOW_CONFIRMATION', 'NORMAL_ENTRY_USES_DOW_CONFIRMATION_ANCHOR', `DIRECTION_FROM_${normalDirectionContext.source}`]);
      resolutions.normal_entry = cloneJsonValue(resolutions.entry);
      resolutions.normal_entry.purpose = 'normal_entry';
      resolutions.expansion_detection = hsiResolvedReference('expansion_detection', expansionDetectionAnchor, ['EXPANSION_DETECTION_USES_ORIGINAL_DOW_ANCHOR', 'EXPANSION_DETECTION_ANCHOR_RETAINED_ACROSS_NON_DIRECTIONAL_STATE', `DIRECTION_FROM_${expansionDirectionContext.source}`]);
      resolutions.expansion_entry = {
        ...expansionEntry,
        purpose: 'expansion_entry',
        reason_codes: expansionEntry?.anchor_id
          ? ['EXPANSION_ENTRY_USES_LATEST_PULLBACK_ANCHOR', `DIRECTION_FROM_${expansionDirectionContext.source}`]
          : ['NO_ACTIVE_ALIGNED_EXPANSION_ENTRY_ANCHOR']
      };
      ['hold', 'target', 'thesis', 'confluence'].forEach(purpose => {
        resolutions[purpose] = resolveHsiPurpose(purpose, anchors, expansionDirectionContext, cycleOriginPointId);
      });
      const roleByAnchor = new Map();
      const assignRole = (anchorId, role) => {
        if (!anchorId) return;
        const roles = roleByAnchor.get(anchorId) || new Set();
        roles.add(role);
        roleByAnchor.set(anchorId, roles);
      };
      assignRole(resolutions.entry?.anchor_id, 'ENTRY_REFERENCE_CANDIDATE');
      assignRole(resolutions.entry?.anchor_id, 'NORMAL_DOW_ENTRY_REFERENCE');
      assignRole(resolutions.expansion_detection?.anchor_id, 'EXPANSION_DETECTION_REFERENCE');
      assignRole(resolutions.expansion_entry?.anchor_id, 'EXPANSION_ENTRY_REFERENCE_CANDIDATE');
      assignRole(resolutions.hold?.anchor_id, 'HOLD_REFERENCE_CANDIDATE');
      assignRole(resolutions.target?.anchor_id, 'TARGET_REFERENCE_CANDIDATE');
      assignRole(resolutions.thesis?.anchor_id, 'THESIS_REFERENCE_CANDIDATE');
      (resolutions.confluence?.anchor_ids || []).forEach(anchorId => assignRole(anchorId, 'CONFLUENCE_REFERENCE_CANDIDATE'));
      const cycleAnchor = anchors.find(anchor => anchor.source_swing_point_id === cycleOriginPointId);
      if (cycleAnchor) assignRole(cycleAnchor.anchor_id, 'CYCLE_ORIGIN');
      anchors.forEach(anchor => {
        const extra = [...(roleByAnchor.get(anchor.anchor_id) || [])];
        if (extra.length) {
          anchor.roles = [...new Set([...(anchor.roles || []), ...extra])];
          anchor.adoption_status = anchor.eligible_for_resolver ? 'ADOPTED' : anchor.adoption_status;
          anchor.reason_codes = [...new Set([...(anchor.reason_codes || []), 'PURPOSE_ROLE_ASSIGNED'])];
        }
        anchor.nearest_human_saved_hsi = nearestHumanSavedHsi(anchor, humanSavedHsiForTimeframe(state, timeframe));
      });
      Object.values(resolutions).forEach(resolution => {
        if (resolution?.anchor_id) resolution.anchor = hsiResolutionSummary(anchors.find(anchor => anchor.anchor_id === resolution.anchor_id));
        if (Array.isArray(resolution?.anchor_ids)) resolution.anchors = resolution.anchor_ids.map(anchorId => hsiResolutionSummary(anchors.find(anchor => anchor.anchor_id === anchorId))).filter(Boolean);
      });
      const adopted = anchors.filter(anchor => anchor.adoption_status === 'ADOPTED');
      const events = anchors.map(anchor => hsiAnchorLifecycleEvent(timeframe, anchor, anchor.adoption_status === 'ADOPTED' ? 'hsi_anchor_adopted' : anchor.lifecycle_status === 'RETIRED' ? 'hsi_anchor_retired' : 'hsi_anchor_registered', false));
      const latestAdopted = [...adopted].sort((a, b) => (numberOrNull(a.pivot_ms) ?? 0) - (numberOrNull(b.pivot_ms) ?? 0)).pop() || null;
      if (latestAdopted) {
        const event = events.find(item => item.anchor_id === latestAdopted.anchor_id && item.event_type === 'hsi_anchor_adopted');
        if (event) event.display.visible = true;
      }
      lifecycleEvents.push(...events);
      const humanItems = humanSavedHsiForTimeframe(state, timeframe);
      const unresolvedPurposes = Object.values(resolutions).filter(item => String(item?.status || '').startsWith('UNRESOLVED')).length;
      // direction_contextは既存下流処理との互換用に通常Dow文脈を指す。
      // Expansionの大起点維持文脈はexpansion_direction_contextへ明示分離する。
      if (normalDirectionContext.direction === 'UNRESOLVED') warnings.push(`${timeframe}: Normal HSI direction context is unresolved; normal entry reference remains unresolved.`);
      timeframes[timeframe] = {
        status: lookahead.length ? 'lookahead_detected' : normalDirectionContext.direction === 'UNRESOLVED' ? 'ready_direction_unresolved' : adopted.length ? 'ready_adopted' : 'ready_no_adopted_anchor',
        registry_id: HSI_ANCHOR_REGISTRY_ID,
        resolver_id: HSI_ANCHOR_RESOLVER_ID,
        direction_context: normalDirectionContext,
        normal_direction_context: normalDirectionContext,
        expansion_direction_context: expansionDirectionContext,
        source_anchor_count: anchors.length,
        counts: {
          candidate: anchors.filter(anchor => anchor.lifecycle_status === 'CANDIDATE').length,
          confirmed: anchors.filter(anchor => anchor.lifecycle_status === 'CONFIRMED').length,
          retired: anchors.filter(anchor => anchor.lifecycle_status === 'RETIRED').length,
          resolver_eligible: anchors.filter(anchor => anchor.eligible_for_resolver).length,
          adopted: adopted.length,
          human_saved_hsi: humanItems.length,
          unresolved_purposes: unresolvedPurposes
        },
        anchors,
        resolutions,
        human_saved_hsi: humanItems.map(item => ({ id: item.id || '', time: item.time || '', price: numberOrNull(item.price), direction: normalizeHsiDirection(item.hsi?.direction), scale: numberOrNull(item.hsi?.scale), source_type: SAVED_HSI_SOURCE_TYPE })),
        lifecycle_events: events,
        action_permission: 'NOT_EVALUATED',
        no_lookahead: lookahead.length === 0
      };
    });
    return {
      schema_version: 'fx_hsi_anchor_registry_snapshot_v0_2',
      kind: 'fx_hsi_anchor_registry_snapshot',
      status: errors.length ? 'invalid' : 'ready',
      phase: 'v0.9.0.27-dow-adopted-normal-anchor-expansion-dual-anchor',
      created_at: nowLocalIso(),
      registry: {
        registry_id: String(policy.registry_id || HSI_ANCHOR_REGISTRY_ID),
        resolver_id: String(policy.resolver_id || HSI_ANCHOR_RESOLVER_ID),
        source_type: String(policy.source_type || SIMULATION_HSI_ANCHOR_SOURCE_TYPE),
        human_saved_hsi_source_type: String(policy.human_saved_hsi_source_type || SAVED_HSI_SOURCE_TYPE),
        timeframe_specific_class: String(policy.timeframe_specific_class || 'forbidden'),
        status_role_separation: policy.status_role_separation === true,
        action_permission_output: String(policy.action_permission_output || 'forbidden'),
        no_lookahead: policy.no_lookahead === true
      },
      timeframes,
      lifecycle_events: lifecycleEvents,
      validation: { valid: errors.length === 0, checked_at: nowLocalIso(), errors, warnings, no_lookahead: errors.every(message => !message.includes('reference close')) },
      teacher_guard: 'HSI Anchor identity, lifecycle, roles, and purpose references only. Purpose resolution is a structural reference candidate, not Entry/Hold/Target permission or a trading signal. Human Saved HSI remains separate and comparison-only.'
    };
  }

  function hsiAnchorRegistrySnapshotPreview(snapshot) {
    if (!snapshot) return null;
    const copy = cloneJsonValue(snapshot);
    Object.values(copy.timeframes || {}).forEach(item => {
      if (Array.isArray(item.anchors)) item.anchors = `[${item.anchors.length} anchors omitted from preview]`;
      if (Array.isArray(item.lifecycle_events)) item.lifecycle_events = `[${item.lifecycle_events.length} events omitted from preview]`;
      if (Array.isArray(item.human_saved_hsi)) item.human_saved_hsi = `[${item.human_saved_hsi.length} human annotations omitted from preview]`;
    });
    if (Array.isArray(copy.lifecycle_events)) copy.lifecycle_events = `[${copy.lifecycle_events.length} events omitted from preview]`;
    return copy;
  }

  function mergeHsiAnchorChartEvents(existingEvents, hsiSnapshot) {
    const kept = (existingEvents || []).filter(event => event?.generated_by !== HSI_ANCHOR_GENERATOR);
    const projected = (hsiSnapshot?.lifecycle_events || []).filter(event => event?.display?.visible === true);
    return [...kept, ...projected];
  }

  function stableTextHash(value) {
    const text = String(value ?? '');
    let hash = 2166136261;
    for (let i = 0; i < text.length; i++) {
      hash ^= text.charCodeAt(i);
      hash = Math.imul(hash, 16777619);
    }
    return (hash >>> 0).toString(16).padStart(8, '0');
  }

  function percentileSorted(values, ratio) {
    if (!Array.isArray(values) || !values.length) return null;
    const sorted = [...values].filter(Number.isFinite).sort((a, b) => a - b);
    if (!sorted.length) return null;
    const position = Math.max(0, Math.min(sorted.length - 1, (sorted.length - 1) * ratio));
    const lower = Math.floor(position);
    const upper = Math.ceil(position);
    if (lower === upper) return sorted[lower];
    const weight = position - lower;
    return sorted[lower] * (1 - weight) + sorted[upper] * weight;
  }

  function bbPhaseStateForTimeframe(state, draft, candleSync, timeframe) {
    const statePolicy = draft?.timeframe_state_policy || {};
    const raw = statePolicy.bb_phase || {};
    const settings = {
      period: Math.max(2, Math.floor(numberOrNull(raw.period) ?? 20)),
      deviations: Math.max(0.1, numberOrNull(raw.deviations) ?? 2),
      shift: 0,
      source: String(raw.source || 'close')
    };
    const lookbackBands = Math.max(5, Math.floor(numberOrNull(raw.lookback_bands) ?? 20));
    const threshold = Math.max(0.000001, numberOrNull(raw.width_change_threshold_ratio) ?? 0.03);
    const rows = simulationCandleSourceRows(state)?.[timeframe] || [];
    const confirmedCount = Math.max(0, Math.floor(numberOrNull(candleSync?.timeframes?.[timeframe]?.available_confirmed_bars) ?? 0));
    const confirmedRows = rows.slice(0, confirmedCount);
    const bands = buildBollingerBandsForRows(confirmedRows, settings).filter(Boolean);
    const requiredBands = Math.min(lookbackBands, Math.max(5, lookbackBands));
    if (bands.length < requiredBands) {
      return {
        status: 'insufficient_history',
        phase: 'UNDETERMINED',
        settings: { ...settings, lookback_bands: lookbackBands, width_change_threshold_ratio: threshold },
        available_bands: bands.length,
        required_bands: requiredBands,
        reason_codes: ['BB_HISTORY_INSUFFICIENT']
      };
    }
    const recent = bands.slice(-lookbackBands);
    const widths = recent.map(item => numberOrNull(item.width)).filter(Number.isFinite);
    const current = recent[recent.length - 1];
    const previous = recent[recent.length - 2];
    const currentWidth = numberOrNull(current?.width);
    const previousWidth = numberOrNull(previous?.width);
    const changeRatio = currentWidth != null && previousWidth != null && previousWidth !== 0
      ? (currentWidth - previousWidth) / previousWidth
      : null;
    const q25 = percentileSorted(widths, 0.25);
    const median = percentileSorted(widths, 0.5);
    const q75 = percentileSorted(widths, 0.75);
    let phase = 'STABLE';
    const reasons = [];
    if (currentWidth == null || changeRatio == null || median == null) {
      phase = 'UNDETERMINED';
      reasons.push('BB_WIDTH_UNAVAILABLE');
    } else if (changeRatio <= -threshold) {
      phase = 'CONTRACTING';
      reasons.push('BB_WIDTH_DECREASING');
    } else if (changeRatio >= threshold && currentWidth <= median) {
      phase = 'OPENING';
      reasons.push('BB_WIDTH_INCREASING_FROM_LOWER_HALF');
    } else if (changeRatio >= threshold) {
      phase = 'EXPANSION';
      reasons.push('BB_WIDTH_INCREASING_ABOVE_MEDIAN');
    } else if (q25 != null && currentWidth <= q25) {
      phase = 'SQUEEZE';
      reasons.push('BB_WIDTH_LOW_QUARTILE');
    } else if (q75 != null && currentWidth >= q75) {
      phase = 'MATURE';
      reasons.push('BB_WIDTH_HIGH_QUARTILE_FLAT');
    } else {
      reasons.push('BB_WIDTH_STABLE_MID_RANGE');
    }
    const latestRow = confirmedRows[confirmedRows.length - 1] || {};
    const close = numberOrNull(latestRow.close);
    const middle = numberOrNull(current?.middle);
    return {
      status: phase === 'UNDETERMINED' ? 'undetermined' : 'ready',
      phase,
      settings: { ...settings, lookback_bands: lookbackBands, width_change_threshold_ratio: threshold },
      current: {
        upper: numberOrNull(current?.upper),
        middle,
        lower: numberOrNull(current?.lower),
        width: currentWidth,
        close,
        close_vs_middle: close == null || middle == null ? 'UNKNOWN' : close > middle ? 'ABOVE' : close < middle ? 'BELOW' : 'AT'
      },
      width_change_ratio: changeRatio,
      width_distribution: { q25, median, q75, sample_count: widths.length },
      available_bands: bands.length,
      required_bands: requiredBands,
      reason_codes: reasons
    };
  }

  function compactSwingRef(point) {
    if (!point) return null;
    return {
      point_id: point.point_id || point.key || '',
      type: point.type || '',
      pivot_time: point.pivot_time || point.time || '',
      pivot_ms: numberOrNull(point.pivot_ms),
      pivot_price: numberOrNull(point.pivot_price ?? point.price),
      source_index: numberOrNull(point.source_index ?? point.index),
      confirmed_time: point.confirmed_time || '',
      confirmed_ms: numberOrNull(point.confirmed_ms),
      confirm_bars: numberOrNull(point.confirm_bars),
      candidate_offset: numberOrNull(point.candidate_offset),
      confirmation_remaining_bars: numberOrNull(point.confirmation_remaining_bars),
      lifecycle_status: point.lifecycle_status || point.status || '',
      basis_role: point.basis_role || point.role || '',
      usable_as_basis: point.usable_as_basis === true
    };
  }

  function compactHsiResolution(item, purpose) {
    const resolution = item?.resolutions?.[purpose];
    if (!resolution) return { status: 'UNRESOLVED', anchor_id: null };
    if (purpose === 'confluence') {
      return {
        status: resolution.status || 'UNRESOLVED',
        anchor_ids: [...(resolution.anchor_ids || [])],
        count: resolution.anchor_ids?.length || 0
      };
    }
    const anchor = resolution.anchor || null;
    return {
      status: resolution.status || (anchor ? 'RESOLVED' : 'UNRESOLVED'),
      anchor_id: resolution.anchor_id || anchor?.anchor_id || null,
      anchor: anchor ? {
        anchor_id: anchor.anchor_id || '',
        anchor_type: anchor.anchor_type || '',
        direction: anchor.direction || '',
        pivot_time: anchor.pivot_time || '',
        price: numberOrNull(anchor.price),
        lifecycle_status: anchor.lifecycle_status || '',
        adoption_status: anchor.adoption_status || '',
        roles: [...(anchor.roles || [])],
        dow_confirmation_id: anchor.dow_confirmation_id || null,
        dow_confirmation_at: anchor.dow_confirmation_at || null,
        dow_confirmation_at_ms: numberOrNull(anchor.dow_confirmation_at_ms)
      } : null
    };
  }

  function latestEventId(events) {
    const list = Array.isArray(events) ? events : [];
    return list.length ? String(list[list.length - 1]?.event_id || '') : '';
  }

  function uniqueStrings(values) {
    return [...new Set((values || []).map(value => String(value || '').trim()).filter(Boolean))];
  }

  function timeframeStateSignature(item) {
    return JSON.stringify({
      timeframe: item.timeframe,
      latest_bar: item.latest_confirmed_bar?.confirmed_bar_key || null,
      active_high: item.swing_state?.latest_active_high?.point_id || null,
      active_low: item.swing_state?.latest_active_low?.point_id || null,
      trend: item.trend_state,
      cycle_origin: item.cycle_state?.origin?.point_id || null,
      cycle_phase: item.cycle_state?.phase,
      hsi_entry: item.hsi_anchor_state?.entry?.anchor_id || null,
      hsi_normal_entry: item.hsi_anchor_state?.normal_entry?.anchor_id || null,
      hsi_expansion_detection: item.hsi_anchor_state?.expansion_detection?.anchor_id || null,
      hsi_expansion_entry: item.hsi_anchor_state?.expansion_entry?.anchor_id || null,
      hsi_hold: item.hsi_anchor_state?.hold?.anchor_id || null,
      hsi_target: item.hsi_anchor_state?.target?.anchor_id || null,
      hsi_confluence: item.hsi_anchor_state?.confluence?.anchor_ids || [],
      bb_phase: item.bb_state?.phase,
      bb_width: item.bb_state?.current?.width == null ? null : Number(item.bb_state.current.width.toFixed(8)),
      sufficiency: item.data_sufficiency?.status
    });
  }

  function compareTimeframeState(current, previous) {
    if (!previous) {
      return { status: 'NO_PREVIOUS_SNAPSHOT', previous_state_id: null, changed: true, changed_fields: ['INITIAL_STATE'] };
    }
    const fields = [
      ['trend_state', current.trend_state, previous.trend_state],
      ['cycle_phase', current.cycle_state?.phase, previous.cycle_state?.phase],
      ['cycle_origin', current.cycle_state?.origin?.point_id, previous.cycle_state?.origin?.point_id],
      ['bb_phase', current.bb_state?.phase, previous.bb_state?.phase],
      ['hsi_entry_anchor', current.hsi_anchor_state?.entry?.anchor_id, previous.hsi_anchor_state?.entry?.anchor_id],
      ['hsi_expansion_entry_anchor', current.hsi_anchor_state?.expansion_entry?.anchor_id, previous.hsi_anchor_state?.expansion_entry?.anchor_id],
      ['hsi_hold_anchor', current.hsi_anchor_state?.hold?.anchor_id, previous.hsi_anchor_state?.hold?.anchor_id],
      ['hsi_target_anchor', current.hsi_anchor_state?.target?.anchor_id, previous.hsi_anchor_state?.target?.anchor_id],
      ['data_sufficiency', current.data_sufficiency?.status, previous.data_sufficiency?.status],
      ['latest_confirmed_bar', current.latest_confirmed_bar?.confirmed_bar_key, previous.latest_confirmed_bar?.confirmed_bar_key]
    ];
    const changedFields = fields.filter(([, a, b]) => JSON.stringify(a ?? null) !== JSON.stringify(b ?? null)).map(([name]) => name);
    return {
      status: changedFields.length ? 'CHANGED' : 'UNCHANGED',
      previous_state_id: previous.state_id || null,
      changed: changedFields.length > 0,
      changed_fields: changedFields
    };
  }

  function buildTimeframeStateEvent(item, previous) {
    const comparison = item.comparison_to_previous_snapshot || {};
    const hsi = item.hsi_anchor_state || {};
    const summary = `${item.timeframe} State / Dow ${item.trend_state} / Cycle ${item.cycle_state?.phase || 'UNDETERMINED'} / BB ${item.bb_state?.phase || 'UNDETERMINED'} / Data ${item.data_sufficiency?.status || 'UNKNOWN'}`;
    return {
      event_id: `tf_state_evt_${String(item.timeframe || '').toLowerCase()}_${stableSwingToken(item.state_as_of_ms)}_${stableTextHash(item.state_signature)}`,
      source_type: SIMULATION_TRACE_SOURCE_TYPE,
      generated_by: TIMEFRAME_STATE_GENERATOR,
      builder_id: TIMEFRAME_STATE_BUILDER_ID,
      event_type: comparison.status === 'CHANGED' ? 'timeframe_state_changed' : 'timeframe_state_snapshot',
      simulation_time: item.state_as_of,
      timeframe: item.timeframe,
      panel: item.timeframe,
      price: numberOrNull(item.latest_confirmed_bar?.close),
      summary,
      reason_codes: uniqueStrings([
        `TREND_${item.trend_state}`,
        `CYCLE_${item.cycle_state?.phase || 'UNDETERMINED'}`,
        `BB_${item.bb_state?.phase || 'UNDETERMINED'}`,
        `DATA_${item.data_sufficiency?.status || 'UNKNOWN'}`,
        ...(item.data_sufficiency?.reason_codes || [])
      ]),
      rule_ids: ['rule_timeframe_state_observation_aggregation', 'rule_state_data_sufficiency_separation', 'rule_state_not_action_permission', 'rule_no_lookahead_confirmed_inputs'],
      cause_event_ids: [...(item.source_event_ids || [])],
      source_bar_keys: [...(item.source_bar_keys || [])],
      state_id: item.state_id,
      upper_state_summary: {
        [item.timeframe]: {
          trend_state: item.trend_state,
          cycle_phase: item.cycle_state?.phase || 'UNDETERMINED',
          cycle_context: item.cycle_state?.context_state || 'UNKNOWN',
          bb_phase: item.bb_state?.phase || 'UNDETERMINED',
          hsi_entry_anchor: hsi.entry?.anchor_id || null,
          hsi_hold_anchor: hsi.hold?.anchor_id || null,
          hsi_target_anchor: hsi.target?.anchor_id || null,
          data_sufficiency: item.data_sufficiency?.status || 'UNKNOWN'
        },
        action_permission: 'NOT_EVALUATED'
      },
      state_before: previous ? {
        state_id: previous.state_id || null,
        trend_state: previous.trend_state || 'UNDETERMINED',
        cycle_phase: previous.cycle_state?.phase || 'UNDETERMINED',
        bb_phase: previous.bb_state?.phase || 'UNDETERMINED',
        data_sufficiency: previous.data_sufficiency?.status || 'UNKNOWN'
      } : null,
      state_after: {
        state_id: item.state_id,
        trend_state: item.trend_state,
        cycle_phase: item.cycle_state?.phase || 'UNDETERMINED',
        cycle_context: item.cycle_state?.context_state || 'UNKNOWN',
        bb_phase: item.bb_state?.phase || 'UNDETERMINED',
        data_sufficiency: item.data_sufficiency?.status || 'UNKNOWN',
        action_permission: 'NOT_EVALUATED'
      },
      comparison_to_previous_snapshot: comparison,
      display: { visible: true, open: false, pinned: false, style: `timeframe_state_${String(item.data_sufficiency?.status || 'unknown').toLowerCase()}` }
    };
  }

  function buildTimeframeStateSnapshot(state, draft, candleSync, swingSnapshot, dowSnapshot, cycleSnapshot, hsiSnapshot) {
    const errors = [];
    const warnings = [];
    const policy = { ...(draft?.timeframe_state_policy || {}) };
    const referenceMs = numberOrNull(candleSync?.reference?.reference_close_ms);
    const referenceTime = String(candleSync?.reference?.reference_close_time || '');
    const previousSnapshot = state?.simulationTrace?.run_snapshot?.timeframe_states || state?.simulationRunSnapshot?.timeframe_states || null;
    const previousTimeframes = previousSnapshot?.timeframes || {};
    const allUpstreamEventIds = new Set([
      ...(swingSnapshot?.observation_events || []).map(event => event?.event_id),
      ...(dowSnapshot?.state_change_events || []).map(event => event?.event_id),
      ...(dowSnapshot?.confirmation_events || []).map(event => event?.event_id),
      ...(cycleSnapshot?.state_change_events || []).map(event => event?.event_id),
      ...(hsiSnapshot?.lifecycle_events || []).map(event => event?.event_id)
    ].filter(Boolean));
    const timeframes = {};
    const stateEvents = [];
    const stateIds = new Set();
    REQUIRED_SIMULATION_TIMEFRAMES.forEach(timeframe => {
      const candleItem = candleSync?.timeframes?.[timeframe] || {};
      const swingItem = swingSnapshot?.timeframes?.[timeframe] || {};
      const dowItem = dowSnapshot?.timeframes?.[timeframe] || {};
      const cycleItem = cycleSnapshot?.timeframes?.[timeframe] || {};
      const hsiItem = hsiSnapshot?.timeframes?.[timeframe] || {};
      const latestBar = cloneJsonValue(candleItem.latest_confirmed_bar || null);
      const latestHigh = compactSwingRef(swingItem.latest_active?.high);
      const latestLow = compactSwingRef(swingItem.latest_active?.low);
      const pendingSwingCandidates = Array.isArray(swingItem.pending_candidates) ? swingItem.pending_candidates : [];
      const latestPendingHigh = compactSwingRef([...pendingSwingCandidates].reverse().find(point => String(point?.type || '').toLowerCase() === 'swing_high'));
      const latestPendingLow = compactSwingRef([...pendingSwingCandidates].reverse().find(point => String(point?.type || '').toLowerCase() === 'swing_low'));
      const bbState = bbPhaseStateForTimeframe(state, draft, candleSync, timeframe);
      const sourceEventIds = uniqueStrings([
        latestHigh ? dowPointConfirmedEventId(latestHigh) : '',
        latestLow ? dowPointConfirmedEventId(latestLow) : '',
        latestEventId(dowItem.state_change_events),
        dowItem?.normal_dow_confirmation?.confirmation_id || '',
        ...((cycleItem.state_change_events || []).slice(-2).map(event => event?.event_id)),
        ...((hsiItem.lifecycle_events || []).filter(event => event?.display?.visible === true).map(event => event?.event_id))
      ]);
      const missingRefs = sourceEventIds.filter(eventId => !allUpstreamEventIds.has(eventId));
      if (missingRefs.length) errors.push(`${timeframe}: ${missingRefs.length} source_event_ids could not be resolved.`);
      const reasonCodes = [];
      const components = {
        candle_sync: latestBar ? 'READY' : 'INSUFFICIENT',
        swing: String(swingItem.status || '').startsWith('ready') ? (latestHigh || latestLow ? 'READY' : 'PARTIAL') : 'INSUFFICIENT',
        dow: dowItem.trend_state === 'UNDETERMINED' ? 'PARTIAL' : String(dowItem.status || '').startsWith('ready') ? 'READY' : 'INSUFFICIENT',
        cycle: cycleItem.phase === 'UNDETERMINED' ? 'PARTIAL' : String(cycleItem.status || '').startsWith('ready') ? 'READY' : 'INSUFFICIENT',
        hsi: String(hsiItem.status || '').startsWith('ready') ? (hsiItem.direction_context?.direction === 'UNRESOLVED' ? 'PARTIAL' : 'READY') : 'INSUFFICIENT',
        bb: bbState.status === 'ready' ? 'READY' : bbState.status === 'insufficient_history' ? 'PARTIAL' : 'PARTIAL'
      };
      Object.entries(components).forEach(([name, value]) => {
        if (value !== 'READY') reasonCodes.push(`${name.toUpperCase()}_${value}`);
      });
      const sufficiencyStatus = !latestBar || components.swing === 'INSUFFICIENT' ? 'INSUFFICIENT'
        : Object.values(components).every(value => value === 'READY') ? 'READY'
          : 'PARTIAL';
      const item = {
        state_id: '',
        timeframe,
        state_as_of: referenceTime,
        state_as_of_ms: referenceMs,
        latest_confirmed_bar: latestBar,
        data_sufficiency: {
          status: sufficiencyStatus,
          components,
          reason_codes: uniqueStrings([...reasonCodes, ...(bbState.reason_codes || [])]),
          market_state_uncertainty: {
            trend_undetermined: dowItem.trend_state === 'UNDETERMINED',
            cycle_undetermined: cycleItem.phase === 'UNDETERMINED',
            hsi_direction_unresolved: hsiItem.direction_context?.direction === 'UNRESOLVED',
            bb_undetermined: bbState.phase === 'UNDETERMINED'
          }
        },
        swing_state: {
          latest_active_high: latestHigh,
          latest_active_low: latestLow,
          latest_pending_high: latestPendingHigh,
          latest_pending_low: latestPendingLow,
          counts: cloneJsonValue(swingItem.counts || {}),
          status: swingItem.status || 'missing'
        },
        trend_state: String(dowItem.trend_state || 'UNDETERMINED'),
        trend_detail: {
          previous_trend_state: dowItem.previous_trend_state || null,
          directional_bias: dowItem.directional_bias || null,
          high_relation: dowItem.high_relation || 'INSUFFICIENT',
          low_relation: dowItem.low_relation || 'INSUFFICIENT',
          used_swing_point_ids: [...(dowItem.used_swing_point_ids || [])],
          reason_codes: [...(dowItem.reason_codes || [])],
          normal_dow_confirmation: cloneJsonValue(dowItem.normal_dow_confirmation || null),
          // v0.9.1.11: Entry EvaluatorはTimeframe Stateを入力にするため、
          // Dow Trend Snapshotだけに崩壊事実を保持するとBatch継続時に失効判定できない。
          normal_dow_structure_break: cloneJsonValue(dowItem.normal_dow_structure_break || null),
          directional_regime_reset: cloneJsonValue(dowItem.directional_regime_reset || null)
        },
        cycle_state: {
          phase: cycleItem.phase || 'UNDETERMINED',
          direction: cycleItem.direction || 'UNDETERMINED',
          elapsed_bars: numberOrNull(cycleItem.elapsed_bars),
          context_role: cycleItem.context_role || '',
          context_state: cycleItem.context_state || 'UNKNOWN',
          origin: cycleItem.origin ? cloneJsonValue(cycleItem.origin) : null,
          thresholds: cloneJsonValue(cycleItem.thresholds || {})
        },
        hsi_anchor_state: {
          direction_context: cloneJsonValue(hsiItem.direction_context || { direction: 'UNRESOLVED', source: 'none' }),
          normal_direction_context: cloneJsonValue(hsiItem.normal_direction_context || hsiItem.direction_context || { direction: 'UNRESOLVED', source: 'none' }),
          expansion_direction_context: cloneJsonValue(hsiItem.expansion_direction_context || { direction: 'UNRESOLVED', source: 'none' }),
          counts: cloneJsonValue(hsiItem.counts || {}),
          entry: compactHsiResolution(hsiItem, 'entry'),
          normal_entry: compactHsiResolution(hsiItem, 'normal_entry'),
          expansion_detection: compactHsiResolution(hsiItem, 'expansion_detection'),
          expansion_entry: compactHsiResolution(hsiItem, 'expansion_entry'),
          hold: compactHsiResolution(hsiItem, 'hold'),
          target: compactHsiResolution(hsiItem, 'target'),
          thesis: compactHsiResolution(hsiItem, 'thesis'),
          confluence: compactHsiResolution(hsiItem, 'confluence'),
          rule_lanes: {
            NORMAL: {
              entry_anchor: compactHsiResolution(hsiItem, 'normal_entry'),
              close_anchor_policy: 'ENTRY_ANCHOR_FIXED_AT_ENTRY'
            },
            EXPANSION: {
              detection_anchor: compactHsiResolution(hsiItem, 'expansion_detection'),
              entry_anchor: compactHsiResolution(hsiItem, 'expansion_entry'),
              status: 'NOT_IMPLEMENTED'
            },
            EXPANSION_LITE: {
              status: 'NOT_DEFINED'
            }
          }
        },
        bb_state: bbState,
        source_event_ids: sourceEventIds,
        source_bar_keys: uniqueStrings([latestBar?.confirmed_bar_key]),
        action_permission: 'NOT_EVALUATED',
        no_lookahead: Boolean(latestBar && referenceMs != null && numberOrNull(latestBar.end_ms) <= referenceMs)
      };
      item.state_signature = timeframeStateSignature(item);
      item.state_id = `tf_state_${timeframe.toLowerCase()}_${stableSwingToken(referenceMs)}_${stableTextHash(item.state_signature)}`;
      if (stateIds.has(item.state_id)) errors.push(`${timeframe}: duplicate state_id ${item.state_id}.`);
      stateIds.add(item.state_id);
      const previous = previousTimeframes[timeframe] || null;
      item.comparison_to_previous_snapshot = compareTimeframeState(item, previous);
      if (!item.no_lookahead) errors.push(`${timeframe}: TimeframeState includes candle after reference close.`);
      if (item.data_sufficiency.status !== 'READY') warnings.push(`${timeframe}: TimeframeState data_sufficiency=${item.data_sufficiency.status}.`);
      timeframes[timeframe] = item;
      stateEvents.push(buildTimeframeStateEvent(item, previous));
    });
    return {
      schema_version: 'fx_timeframe_state_snapshot_v0_1',
      kind: 'fx_timeframe_state_snapshot',
      status: errors.length ? 'invalid' : 'ready',
      phase: 'v0.9.0.08-timeframe-state-builder',
      created_at: nowLocalIso(),
      builder: {
        builder_id: String(policy.builder_id || TIMEFRAME_STATE_BUILDER_ID),
        input_source: String(policy.input_source || ''),
        timeframe_specific_class: String(policy.timeframe_specific_class || 'forbidden'),
        state_as_of_source: String(policy.state_as_of_source || 'candle_sync.reference.reference_close_time'),
        state_id_policy: String(policy.state_id_policy || 'stable_reference_plus_observation_signature'),
        source_event_ids_required: policy.source_event_ids_required === true,
        data_sufficiency_separate_from_market_state: policy.data_sufficiency_separate_from_market_state === true,
        action_permission_output: String(policy.action_permission_output || 'forbidden'),
        no_lookahead: policy.no_lookahead === true
      },
      reference: { state_as_of: referenceTime, state_as_of_ms: referenceMs, source: candleSync?.reference?.source || '' },
      timeframes,
      state_events: stateEvents,
      validation: {
        valid: errors.length === 0,
        checked_at: nowLocalIso(),
        errors,
        warnings,
        no_lookahead: errors.every(message => !message.includes('after reference close')),
        source_event_ids_resolved: errors.every(message => !message.includes('source_event_ids'))
      },
      action_permission: 'NOT_EVALUATED',
      teacher_guard: 'TimeframeState is an observation snapshot only. Swing, Dow, Cycle, HSI, BB, data sufficiency, and source references are integrated without producing Entry/Hold/Close permission or executing trades.'
    };
  }

  function timeframeStateSnapshotPreview(snapshot) {
    if (!snapshot) return null;
    const copy = cloneJsonValue(snapshot);
    Object.values(copy.timeframes || {}).forEach(item => {
      if (typeof item.state_signature === 'string') item.state_signature = `[signature ${stableTextHash(item.state_signature)}]`;
    });
    if (Array.isArray(copy.state_events)) copy.state_events = `[${copy.state_events.length} events omitted from preview]`;
    return copy;
  }

  function mergeTimeframeStateChartEvents(existingEvents, snapshot) {
    const kept = (existingEvents || []).filter(event => event?.generated_by !== TIMEFRAME_STATE_GENERATOR);
    const projected = (snapshot?.state_events || []).filter(event => event?.display?.visible === true);
    return [...kept, ...projected];
  }

  function timeframeStateHsiLabel(item) {
    const hsi = item?.hsi_anchor_state || {};
    const shortAnchor = resolution => resolution?.anchor_id ? String(resolution.anchor_id).replace(/^hsi_anchor_[^_]+_/, '').slice(-12) : '-';
    return `E:${shortAnchor(hsi.entry)} H:${shortAnchor(hsi.hold)} T:${shortAnchor(hsi.target)}`;
  }

  function renderTimeframeStateRows(snapshot) {
    return REQUIRED_SIMULATION_TIMEFRAMES.map(tf => {
      const item = snapshot?.timeframes?.[tf] || {};
      const sufficiency = String(item.data_sufficiency?.status || 'MISSING').toUpperCase();
      const statusCls = sufficiency === 'READY' ? 'gpt-fx-chart-sync-ok' : sufficiency === 'PARTIAL' ? 'gpt-fx-chart-sync-warn' : 'gpt-fx-chart-sync-error';
      const swings = `${item.swing_state?.latest_active_high ? 'H' : '-'} / ${item.swing_state?.latest_active_low ? 'L' : '-'}`;
      return `<tr><td>${tf}</td><td>${escapeHtml(item.state_as_of || '-')}</td><td class="${statusCls}">${escapeHtml(sufficiency)}</td><td class="${dowStateClass(item.trend_state)}">${escapeHtml(item.trend_state || 'UNDETERMINED')}</td><td class="${cyclePhaseClass(item.cycle_state?.phase)}">${escapeHtml(item.cycle_state?.phase || 'UNDETERMINED')}</td><td>${escapeHtml(item.cycle_state?.context_state || 'UNKNOWN')}</td><td>${escapeHtml(item.bb_state?.phase || 'UNDETERMINED')}</td><td>${escapeHtml(swings)}</td><td>${escapeHtml(timeframeStateHsiLabel(item))}</td><td>${(item.source_event_ids || []).length}</td><td>${escapeHtml(item.comparison_to_previous_snapshot?.status || '-')}</td><td>${escapeHtml(item.state_id || '-')}</td></tr>`;
    }).join('');
  }

  function hsiAnchorResolutionLabel(item, purpose) {
    const resolution = item?.resolutions?.[purpose];
    if (!resolution) return '-';
    if (purpose === 'confluence') return `${resolution.anchor_ids?.length || 0} anchors`;
    const anchor = resolution.anchor;
    if (!anchor) return 'UNRESOLVED';
    return `${anchor.anchor_type} ${round3(anchor.price)} / ${anchor.pivot_time || '-'}`;
  }

  function renderHsiAnchorRows(snapshot) {
    return REQUIRED_SIMULATION_TIMEFRAMES.map(tf => {
      const item = snapshot?.timeframes?.[tf] || {};
      const counts = item.counts || {};
      const status = String(item.status || 'missing').toUpperCase();
      const cls = String(item.status || '').startsWith('ready_') ? 'gpt-fx-chart-sync-ok' : 'gpt-fx-chart-sync-error';
      return `<tr><td>${tf}</td><td>${escapeHtml(item.direction_context?.direction || '-')} / ${escapeHtml(item.direction_context?.source || '-')}</td><td>${counts.candidate ?? 0}/${counts.confirmed ?? 0}/${counts.retired ?? 0}</td><td>${counts.resolver_eligible ?? 0}</td><td>${counts.adopted ?? 0}</td><td>${escapeHtml(hsiAnchorResolutionLabel(item, 'entry'))}</td><td>${escapeHtml(hsiAnchorResolutionLabel(item, 'hold'))}</td><td>${escapeHtml(hsiAnchorResolutionLabel(item, 'target'))}</td><td>${escapeHtml(hsiAnchorResolutionLabel(item, 'confluence'))}</td><td>${counts.human_saved_hsi ?? 0}</td><td class="${cls}">${escapeHtml(status)}</td></tr>`;
    }).join('');
  }

  function cyclePhaseClass(phase) {
    const value = String(phase || '').toUpperCase();
    if (value === 'EARLY') return 'gpt-fx-chart-cycle-early';
    if (value === 'MIDDLE') return 'gpt-fx-chart-cycle-middle';
    if (value === 'LATE') return 'gpt-fx-chart-cycle-late';
    return 'gpt-fx-chart-cycle-neutral';
  }

  function cycleOriginLabel(item) {
    const origin = item?.origin;
    if (!origin) return '-';
    const side = origin.type === 'swing_low' ? 'Low' : origin.type === 'swing_high' ? 'High' : '?';
    return `${side} ${round3(origin.pivot_price)} / ${origin.pivot_time || '-'}`;
  }

  function renderCyclePositionRows(snapshot) {
    return REQUIRED_SIMULATION_TIMEFRAMES.map(tf => {
      const item = snapshot?.timeframes?.[tf] || {};
      const phase = String(item.phase || 'UNDETERMINED').toUpperCase();
      const cls = cyclePhaseClass(phase);
      const statusCls = String(item.status || '').startsWith('ready_') ? 'gpt-fx-chart-sync-ok' : 'gpt-fx-chart-sync-error';
      const thresholds = item.thresholds || {};
      const thresholdText = `E≤${thresholds.early_max_bars ?? '-'} / M≤${thresholds.middle_max_bars ?? '-'} / L≥${thresholds.late_from_bars ?? '-'}`;
      return `<tr><td>${tf}</td><td>${escapeHtml(cycleOriginLabel(item))}</td><td>${escapeHtml(item.direction || '-')}</td><td>${item.elapsed_bars ?? 0}</td><td class="${cls}">${escapeHtml(phase)}</td><td>${escapeHtml(`${item.context_role || '-'}:${item.context_state || '-'}`)}</td><td>${escapeHtml(thresholdText)}</td><td>${(item.origin_change_count || 0) + (item.phase_change_count || 0)}</td><td class="${statusCls}">${escapeHtml(String(item.status || 'missing').toUpperCase())}</td></tr>`;
    }).join('');
  }

  function upperDecisionPermission(status = 'WAIT', note = '') {
    return {
      status,
      note,
      reason_codes: [],
      rule_ids: [],
      prerequisites: []
    };
  }

  function upperDecisionPathTarget(root, path) {
    if (!path || path === '$') return root;
    return String(path).split('.').reduce((current, key) => current && current[key], root);
  }

  function applyUpperDecisionEffect(decision, effect, rule, locks) {
    const targetPath = String(effect?.target || '$');
    const target = upperDecisionPathTarget(decision, targetPath);
    if (!target || typeof target !== 'object') return false;
    target.reason_codes = uniqueStrings([...(target.reason_codes || []), ...(rule.reason_codes || [])]);
    target.rule_ids = uniqueStrings([...(target.rule_ids || []), rule.rule_id]);
    if (locks.has(targetPath)) return false;
    Object.assign(target, cloneJsonValue(effect.assign || {}));
    if (Array.isArray(effect.prerequisites)) target.prerequisites = uniqueStrings([...(target.prerequisites || []), ...effect.prerequisites]);
    if (effect.lock === true) locks.add(targetPath);
    return true;
  }

  function upperContextDirectionFacts(timeframes) {
    const h4Trend = String(timeframes?.H4?.trend_state || 'UNDETERMINED').toUpperCase();
    const h1Trend = String(timeframes?.H1?.trend_state || 'UNDETERMINED').toUpperCase();
    const h4Direction = h4Trend === 'UP' ? 'LONG' : h4Trend === 'DOWN' ? 'SHORT' : 'UNDETERMINED';
    let value = 'UNDETERMINED';
    let alignment = 'UNDETERMINED';
    if (h4Direction !== 'UNDETERMINED') {
      if ((h4Direction === 'LONG' && h1Trend === 'UP') || (h4Direction === 'SHORT' && h1Trend === 'DOWN')) {
        value = h4Direction;
        alignment = 'ALIGNED';
      } else if ((h4Direction === 'LONG' && h1Trend === 'DOWN') || (h4Direction === 'SHORT' && h1Trend === 'UP')) {
        value = 'NEUTRAL';
        alignment = 'CONFLICT';
      } else if (['REVERSAL_WATCH', 'NO_TREND'].includes(h1Trend)) {
        value = h4Direction;
        alignment = 'WATCH';
      } else {
        value = h4Direction;
        alignment = 'H1_UNDETERMINED';
      }
    }
    return { value, alignment, h4_direction: h4Direction, h4_trend: h4Trend, h1_trend: h1Trend };
  }

  function upperContextFacts(timeframeStates, policy) {
    const timeframes = timeframeStates?.timeframes || {};
    const required = Array.isArray(policy?.required_timeframes) && policy.required_timeframes.length
      ? policy.required_timeframes.map(tf => String(tf || '').toUpperCase())
      : ['WEEK', 'DAY', 'H4', 'H1'];
    const notReady = required.filter(tf => String(timeframes?.[tf]?.data_sufficiency?.status || 'MISSING').toUpperCase() !== 'READY');
    const direction = upperContextDirectionFacts(timeframes);
    const week = timeframes.WEEK || {};
    const day = timeframes.DAY || {};
    const h4 = timeframes.H4 || {};
    const h1 = timeframes.H1 || {};
    const confluenceCount = Math.max(0, Math.floor(numberOrNull(h4?.hsi_anchor_state?.confluence?.count) ?? h4?.hsi_anchor_state?.confluence?.anchor_ids?.length ?? 0));
    return {
      timeframes,
      required_timeframes: required,
      not_ready_timeframes: notReady,
      direction,
      week_phase: String(week?.cycle_state?.phase || 'UNDETERMINED').toUpperCase(),
      week_context: String(week?.cycle_state?.context_state || 'UNKNOWN').toUpperCase(),
      day_phase: String(day?.cycle_state?.phase || 'UNDETERMINED').toUpperCase(),
      day_context: String(day?.cycle_state?.context_state || 'UNKNOWN').toUpperCase(),
      h4_phase: String(h4?.cycle_state?.phase || 'UNDETERMINED').toUpperCase(),
      h4_context: String(h4?.cycle_state?.context_state || 'UNKNOWN').toUpperCase(),
      h4_bb: String(h4?.bb_state?.phase || 'UNDETERMINED').toUpperCase(),
      h4_hsi_entry_resolved: String(h4?.hsi_anchor_state?.entry?.status || '').toUpperCase() === 'RESOLVED',
      h4_hsi_confluence_count: confluenceCount,
      h1_trend: String(h1?.trend_state || 'UNDETERMINED').toUpperCase(),
      all_no_lookahead: required.every(tf => timeframes?.[tf]?.no_lookahead === true)
    };
  }

  function upperContextDecisionRules(facts, policy) {
    const minimumConfluence = Math.max(1, Math.floor(numberOrNull(policy?.profit_take_arm_rule?.minimum_hsi_confluence_anchors) ?? 2));
    const weekLate = facts.week_phase === 'LATE' || facts.week_context === 'CLOSED';
    const weekCaution = facts.week_phase === 'MIDDLE' || facts.week_context === 'CAUTION';
    const dayNotExpansion = facts.day_phase === 'LATE' || facts.day_context === 'NOT_EXPANSION';
    const dayWarning = facts.day_phase === 'MIDDLE' || facts.day_context === 'WARNING';
    const h4Late = facts.h4_phase === 'LATE' || facts.h4_context === 'PROTECT';
    const h4Directional = ['UP', 'DOWN'].includes(facts.direction.h4_trend);
    const aligned = facts.direction.alignment === 'ALIGNED';
    const h4EarlyMiddle = ['EARLY', 'MIDDLE'].includes(facts.h4_phase);
    const upperExpansionWindow = facts.week_context === 'OPEN' && facts.day_context === 'OK' && h4EarlyMiddle;
    const profitTakeArmed = h4Late && facts.h4_bb === 'CONTRACTING' && facts.h4_hsi_confluence_count >= minimumConfluence;
    return [
      {
        rule_id: 'rule_upper_context_required_state_ready',
        priority: 10,
        category: 'guard',
        matched: facts.not_ready_timeframes.length > 0,
        summary: '上位足StateのData SufficiencyがREADYでない場合、新規探索を停止する。',
        reason_codes: ['UPPER_STATE_DATA_NOT_READY', ...facts.not_ready_timeframes.map(tf => `${tf}_DATA_NOT_READY`)],
        effects: [
          { target: 'no_trade', assign: { active: true }, lock: true },
          { target: 'entry_policy.normal_entry', assign: { status: 'BLOCKED' }, lock: true },
          { target: 'entry_policy.expansion_entry', assign: { status: 'BLOCKED' }, lock: true },
          { target: 'entry_policy.reentry', assign: { status: 'BLOCKED' }, lock: true },
          { target: 'entry_policy.add_on', assign: { status: 'BLOCKED' }, lock: true }
        ]
      },
      {
        rule_id: 'rule_upper_context_h4_no_trade',
        priority: 20,
        category: 'guard',
        matched: ['UNDETERMINED', 'NO_TREND'].includes(facts.direction.h4_trend),
        summary: 'H4方向が未判定またはNoTrendなら新規Entry探索を行わない。',
        reason_codes: [`H4_TREND_${facts.direction.h4_trend}`],
        effects: [
          { target: 'no_trade', assign: { active: true }, lock: true },
          { target: 'entry_policy.normal_entry', assign: { status: 'BLOCKED' }, lock: true },
          { target: 'entry_policy.expansion_entry', assign: { status: 'BLOCKED' }, lock: true },
          { target: 'entry_policy.reentry', assign: { status: 'BLOCKED' }, lock: true },
          { target: 'entry_policy.add_on', assign: { status: 'BLOCKED' }, lock: true }
        ]
      },
      {
        rule_id: 'rule_upper_context_h4_reversal_watch',
        priority: 25,
        category: 'guard',
        matched: facts.direction.h4_trend === 'REVERSAL_WATCH',
        summary: 'H4反転監視中はWatchを優先し、新規Entry探索を止める。',
        reason_codes: ['H4_REVERSAL_WATCH'],
        effects: [
          { target: 'entry_policy.normal_entry', assign: { status: 'BLOCKED' }, lock: true },
          { target: 'entry_policy.expansion_entry', assign: { status: 'BLOCKED' }, lock: true },
          { target: 'entry_policy.reentry', assign: { status: 'BLOCKED' }, lock: true },
          { target: 'entry_policy.add_on', assign: { status: 'BLOCKED' }, lock: true }
        ]
      },
      {
        rule_id: 'rule_upper_context_h4_h1_direction_conflict',
        priority: 30,
        category: 'guard',
        matched: facts.direction.alignment === 'CONFLICT',
        summary: 'H4とH1の方向が逆なら新規Entry探索を止める。',
        reason_codes: ['H4_H1_DIRECTION_CONFLICT'],
        effects: [
          { target: 'entry_policy.normal_entry', assign: { status: 'BLOCKED' }, lock: true },
          { target: 'entry_policy.expansion_entry', assign: { status: 'BLOCKED' }, lock: true },
          { target: 'entry_policy.reentry', assign: { status: 'BLOCKED' }, lock: true },
          { target: 'entry_policy.add_on', assign: { status: 'BLOCKED' }, lock: true },
          { target: 'position_policy.hold_core', assign: { status: 'REVIEW_H1_CONFLICT' }, lock: false }
        ]
      },
      {
        rule_id: 'rule_week_late_expansion_defensive_mode',
        priority: 40,
        category: 'season_guard',
        matched: weekLate,
        summary: 'WEEK Late/CLOSEDではExpansion Entry・ReEntry・Add-onを禁止し、H1早期Exit監視を有効化する。',
        reason_codes: ['WEEK_CYCLE_LATE', 'WEEK_EXPANSION_SEASON_CLOSED'],
        effects: [
          { target: 'entry_policy.expansion_entry', assign: { status: 'BLOCKED' }, lock: true },
          { target: 'entry_policy.reentry', assign: { status: 'BLOCKED' }, lock: true },
          { target: 'entry_policy.add_on', assign: { status: 'BLOCKED' }, lock: true },
          { target: 'position_policy.hold_core', assign: { status: 'HOLD_WITH_ACCELERATED_EXIT' }, lock: true },
          { target: 'position_policy.h1_exit_trigger', assign: { enabled: true, exit_policy: 'ACCELERATED' }, lock: true }
        ]
      },
      {
        rule_id: 'rule_week_caution_expansion_wait',
        priority: 45,
        category: 'season_guard',
        matched: weekCaution,
        summary: 'WEEK CAUTIONではExpansion系の新規探索を待機する。',
        reason_codes: ['WEEK_EXPANSION_SEASON_CAUTION'],
        effects: [
          { target: 'entry_policy.expansion_entry', assign: { status: 'WAIT' }, lock: true },
          { target: 'entry_policy.reentry', assign: { status: 'WAIT' }, lock: true },
          { target: 'entry_policy.add_on', assign: { status: 'WAIT' }, lock: true }
        ]
      },
      {
        rule_id: 'rule_day_not_expansion_guard',
        priority: 50,
        category: 'age_guard',
        matched: dayNotExpansion,
        summary: 'DAY Late/NOT_EXPANSIONではExpansion系の新規探索を禁止する。',
        reason_codes: ['DAY_EXPANSION_AGE_EXPIRED', 'DAY_NOT_EXPANSION'],
        effects: [
          { target: 'entry_policy.expansion_entry', assign: { status: 'BLOCKED' }, lock: true },
          { target: 'entry_policy.reentry', assign: { status: 'BLOCKED' }, lock: true },
          { target: 'entry_policy.add_on', assign: { status: 'BLOCKED' }, lock: true }
        ]
      },
      {
        rule_id: 'rule_day_warning_expansion_wait',
        priority: 55,
        category: 'age_guard',
        matched: dayWarning,
        summary: 'DAY WARNINGではExpansion系をGrade Downし、追加確認待ちにする。',
        reason_codes: ['DAY_EXPANSION_GRADE_WARNING'],
        effects: [
          { target: 'entry_policy.expansion_entry', assign: { status: 'WAIT' }, lock: true },
          { target: 'entry_policy.reentry', assign: { status: 'WAIT' }, lock: true },
          { target: 'entry_policy.add_on', assign: { status: 'WAIT' }, lock: true }
        ]
      },
      {
        rule_id: 'rule_h4_late_protect_mode',
        priority: 60,
        category: 'management_guard',
        matched: h4Late,
        summary: 'H4 Late/PROTECTでは新規Expansion・ReEntry・Add-onを禁止し、利益保護へ切り替える。',
        reason_codes: ['H4_CYCLE_LATE', 'H4_PROTECT_MODE'],
        effects: [
          { target: 'entry_policy.expansion_entry', assign: { status: 'BLOCKED' }, lock: true },
          { target: 'entry_policy.reentry', assign: { status: 'BLOCKED' }, lock: true },
          { target: 'entry_policy.add_on', assign: { status: 'BLOCKED' }, lock: true },
          { target: 'position_policy.hold_core', assign: { status: 'PROTECT' }, lock: false }
        ]
      },
      {
        rule_id: 'rule_h4_profit_take_armed',
        priority: 65,
        category: 'management',
        matched: profitTakeArmed,
        summary: 'H4 Late + BB Contracting + HSI Confluenceで利益確定準備をONにする。',
        reason_codes: ['H4_PROFIT_TAKE_ARMED', 'H4_BB_CONTRACTING', 'H4_HSI_CONFLUENCE'],
        effects: [
          { target: 'position_policy.profit_take_armed', assign: { enabled: true, judge_timeframe: 'H4' }, lock: true },
          { target: 'position_policy.h1_exit_trigger', assign: { enabled: true, exit_policy: 'NORMAL_PROFIT_TAKE' }, lock: false },
          { target: 'position_policy.hold_core', assign: { status: 'EXIT_ARMED' }, lock: true }
        ]
      },
      {
        rule_id: 'rule_upper_context_core_hold_bias',
        priority: 70,
        category: 'management',
        matched: aligned && h4Directional && h4EarlyMiddle && ['OPENING', 'EXPANSION', 'MATURE', 'STABLE'].includes(facts.h4_bb),
        summary: 'H4方向継続・Cycle Early/Middle・BB継続中はCore Holdを優先する。',
        reason_codes: ['H4_DIRECTION_CONTINUATION', `H4_CYCLE_${facts.h4_phase}`, `H4_BB_${facts.h4_bb}`],
        effects: [
          { target: 'position_policy.hold_core', assign: { status: 'PREFER_HOLD' }, lock: false }
        ]
      },
      {
        rule_id: 'rule_upper_context_normal_entry_search_allowed',
        priority: 80,
        category: 'permission',
        matched: aligned && facts.not_ready_timeframes.length === 0 && !h4Late,
        summary: 'H4/H1方向整合と上位足READYを満たす場合、M5通常Entry Trigger探索を許可する。',
        reason_codes: ['H4_H1_DIRECTION_ALIGNED', 'UPPER_STATE_READY'],
        effects: [
          { target: 'entry_policy.normal_entry', assign: { status: 'ALLOW_SEARCH' }, prerequisites: ['M5_DOW_TRIGGER', 'HSI_DISTANCE', 'RISK_REWARD'], lock: false }
        ]
      },
      {
        rule_id: 'rule_upper_context_expansion_search_allowed',
        priority: 85,
        category: 'permission',
        matched: aligned && facts.not_ready_timeframes.length === 0 && upperExpansionWindow && facts.h4_hsi_entry_resolved,
        summary: 'WEEK OPEN・DAY OK・H4 Early/Middle・H4/H1整合・HSI Entry起点解決時、Expansion探索を許可する。',
        reason_codes: ['WEEK_EXPANSION_SEASON_OPEN', 'DAY_EXPANSION_GRADE_OK', `H4_CYCLE_${facts.h4_phase}`, 'H4_HSI_ENTRY_REFERENCE_RESOLVED'],
        effects: [
          { target: 'entry_policy.expansion_entry', assign: { status: 'ALLOW_SEARCH' }, prerequisites: ['EXPANSION_CONFIRMATION', 'M5_DOW_TRIGGER', 'HSI_DISTANCE', 'RISK_REWARD'], lock: false },
          { target: 'entry_policy.reentry', assign: { status: 'CONDITIONAL' }, prerequisites: ['PREVIOUS_CLOSE_OK', 'HSI_ANCHOR_MAINTAINED', 'M5_DOW_TRIGGER'], lock: false },
          { target: 'entry_policy.add_on', assign: { status: 'CONDITIONAL' }, prerequisites: ['EXISTING_CORE_PROFITABLE', 'NEW_CONFIRMED_PULLBACK_ANCHOR', 'M5_DOW_TRIGGER'], lock: false }
        ]
      }
    ];
  }

  function upperDecisionCompact(snapshot) {
    if (!snapshot) return null;
    return {
      decision_id: snapshot.decision_id || null,
      direction_bias: snapshot.direction_bias?.value || 'UNDETERMINED',
      direction_alignment: snapshot.direction_bias?.alignment || 'UNDETERMINED',
      decision_mode: snapshot.decision_mode || 'WATCH',
      no_trade: snapshot.no_trade?.active === true,
      normal_entry: snapshot.entry_policy?.normal_entry?.status || 'NOT_EVALUATED',
      expansion_entry: snapshot.entry_policy?.expansion_entry?.status || 'NOT_EVALUATED',
      reentry: snapshot.entry_policy?.reentry?.status || 'NOT_EVALUATED',
      add_on: snapshot.entry_policy?.add_on?.status || 'NOT_EVALUATED',
      hold_core: snapshot.position_policy?.hold_core?.status || 'UNRESOLVED',
      profit_take_armed: snapshot.position_policy?.profit_take_armed?.enabled === true,
      h1_exit_trigger_enabled: snapshot.position_policy?.h1_exit_trigger?.enabled === true,
      h1_exit_trigger_signal: snapshot.position_policy?.h1_exit_trigger?.signal || 'NONE'
    };
  }

  function compareUpperDecision(current, previous) {
    if (!previous) return { status: 'NO_PREVIOUS_SNAPSHOT', previous_decision_id: null, changed: true, changed_fields: ['INITIAL_DECISION'] };
    const a = upperDecisionCompact(current);
    const b = upperDecisionCompact(previous);
    const changedFields = Object.keys(a).filter(key => key !== 'decision_id' && JSON.stringify(a[key] ?? null) !== JSON.stringify(b?.[key] ?? null));
    return {
      status: changedFields.length ? 'CHANGED' : 'UNCHANGED',
      previous_decision_id: previous.decision_id || null,
      changed: changedFields.length > 0,
      changed_fields: changedFields
    };
  }

  function upperDecisionStatusClass(status) {
    const value = String(status || '').toUpperCase();
    if (value === 'ALLOW_SEARCH') return 'gpt-fx-chart-decision-allow';
    if (value === 'CONDITIONAL') return 'gpt-fx-chart-decision-conditional';
    if (value === 'WAIT' || value === 'WATCH') return 'gpt-fx-chart-decision-wait';
    if (value === 'BLOCKED' || value === 'NO_TRADE' || value === 'CONFIRMED') return 'gpt-fx-chart-decision-blocked';
    return 'gpt-fx-chart-decision-neutral';
  }

  function buildUpperContextDecisionEvent(snapshot, previous) {
    const compact = upperDecisionCompact(snapshot);
    const referenceM5 = snapshot?.input_states?.M5 || {};
    return {
      event_id: `upper_decision_evt_${stableSwingToken(snapshot?.reference?.state_as_of_ms)}_${stableTextHash(snapshot?.decision_signature || '')}`,
      source_type: SIMULATION_TRACE_SOURCE_TYPE,
      generated_by: UPPER_CONTEXT_DECISION_GENERATOR,
      engine_id: UPPER_CONTEXT_DECISION_ENGINE_ID,
      event_type: snapshot?.comparison_to_previous_snapshot?.status === 'CHANGED' ? 'upper_context_decision_changed' : 'upper_context_decision_snapshot',
      simulation_time: snapshot?.reference?.state_as_of || '',
      timeframe: 'M5',
      panel: 'M5',
      price: numberOrNull(referenceM5?.latest_confirmed_bar?.close),
      summary: `Upper Context / Bias ${compact.direction_bias} ${compact.direction_alignment} / ${compact.decision_mode} / Expansion ${compact.expansion_entry} / H1 Exit ${compact.h1_exit_trigger_enabled ? compact.h1_exit_trigger_signal : 'OFF'}`,
      reason_codes: [...(snapshot?.reason_codes || [])],
      rule_ids: [...(snapshot?.rule_ids || [])],
      cause_event_ids: [...(snapshot?.input_state_event_ids || [])],
      input_state_ids: cloneJsonValue(snapshot?.input_state_ids || {}),
      upper_state_summary: {
        WEEK: snapshot?.input_state_summary?.WEEK || {},
        DAY: snapshot?.input_state_summary?.DAY || {},
        H4: snapshot?.input_state_summary?.H4 || {},
        H1: snapshot?.input_state_summary?.H1 || {},
        decision: compact,
        action_execution: 'NOT_EVALUATED'
      },
      state_before: upperDecisionCompact(previous),
      state_after: { ...compact, action_execution: 'NOT_EVALUATED' },
      display: { visible: true, open: false, pinned: false, style: `upper_context_${String(snapshot?.decision_mode || 'watch').toLowerCase()}` }
    };
  }

  function buildUpperContextDecisionSnapshot(state, draft, timeframeStates) {
    const policy = cloneJsonValue(draft?.upper_context_decision_policy || {});
    const facts = upperContextFacts(timeframeStates, policy);
    const previous = state?.simulationTrace?.run_snapshot?.upper_context_decision || state?.simulationRunSnapshot?.upper_context_decision || null;
    const decision = {
      schema_version: 'fx_upper_context_decision_snapshot_v0_1',
      kind: 'fx_upper_context_decision_snapshot',
      status: 'ready',
      phase: 'v0.9.0.09-upper-context-decision-engine',
      created_at: nowLocalIso(),
      engine: {
        engine_id: String(policy.engine_id || UPPER_CONTEXT_DECISION_ENGINE_ID),
        input_source: String(policy.input_source || 'run_snapshot.timeframe_states.timeframes'),
        rule_evaluation: String(policy.rule_evaluation || 'priority_ordered_specification_registry'),
        no_trade_priority: policy.no_trade_priority === true,
        timeframe_specific_class: String(policy.timeframe_specific_class || 'forbidden'),
        action_execution_output: String(policy.action_execution_output || 'forbidden'),
        no_lookahead: policy.no_lookahead === true
      },
      reference: {
        state_as_of: timeframeStates?.reference?.state_as_of || '',
        state_as_of_ms: numberOrNull(timeframeStates?.reference?.state_as_of_ms),
        source: timeframeStates?.reference?.source || ''
      },
      input_state_ids: {},
      input_state_event_ids: [],
      input_state_summary: {},
      input_states: {},
      direction_bias: {
        value: facts.direction.value,
        alignment: facts.direction.alignment,
        h4_direction: facts.direction.h4_direction,
        reason_codes: [],
        rule_ids: []
      },
      decision_mode: 'WATCH',
      no_trade: { active: false, reason_codes: [], rule_ids: [] },
      entry_policy: {
        normal_entry: upperDecisionPermission('WAIT', 'M5 Trigger探索は上位足Rule評価後に決定する。'),
        expansion_entry: upperDecisionPermission('WAIT', 'Expansion確認とM5 Triggerは後続責務。'),
        reentry: upperDecisionPermission('WAIT', 'Position Lifecycleと前Trade結果は後続責務。'),
        add_on: upperDecisionPermission('WAIT', '既存Core含み益等のPosition条件は後続責務。')
      },
      position_policy: {
        hold_core: upperDecisionPermission('UNRESOLVED', 'Position未作成でも上位文脈のHold方針だけを示す。'),
        profit_take_armed: { enabled: false, judge_timeframe: 'H4', reason_codes: [], rule_ids: [] },
        h1_exit_trigger: { enabled: false, signal: 'NONE', exit_policy: 'NORMAL', trigger_timeframe: 'H1', direct_close: false, reason_codes: [], rule_ids: [] },
        week_direct_close: false
      },
      management_policy: {
        season_timeframe: 'WEEK',
        expansion_grade_timeframe: 'DAY',
        profit_take_judge_timeframe: 'H4',
        exit_trigger_timeframe: 'H1',
        execution_timeframe: 'M5',
        management_timeframe_cap: 'DAY',
        week_direct_close: false
      },
      m5_instruction: {
        mode: 'WAIT',
        allowed_searches: [],
        blocked_actions: [],
        action_execution: 'NOT_EVALUATED'
      },
      reason_codes: [],
      rule_ids: [],
      matched_rules: [],
      rule_evaluations: [],
      action_execution: 'NOT_EVALUATED'
    };
    const tfEvents = new Map((timeframeStates?.state_events || []).map(event => [String(event?.timeframe || '').toUpperCase(), event]));
    REQUIRED_SIMULATION_TIMEFRAMES.forEach(tf => {
      const item = timeframeStates?.timeframes?.[tf] || null;
      decision.input_states[tf] = item ? {
        state_id: item.state_id || null,
        timeframe: tf,
        state_as_of: item.state_as_of || '',
        latest_confirmed_bar: item.latest_confirmed_bar ? {
          confirmed_bar_key: item.latest_confirmed_bar.confirmed_bar_key || null,
          start_time: item.latest_confirmed_bar.start_time || '',
          end_time: item.latest_confirmed_bar.end_time || '',
          close: numberOrNull(item.latest_confirmed_bar.close)
        } : null,
        data_sufficiency: { status: item.data_sufficiency?.status || 'MISSING' },
        trend_state: item.trend_state || 'UNDETERMINED',
        cycle_state: {
          phase: item.cycle_state?.phase || 'UNDETERMINED',
          context_state: item.cycle_state?.context_state || 'UNKNOWN'
        },
        bb_state: { phase: item.bb_state?.phase || 'UNDETERMINED' },
        hsi_anchor_state: {
          entry_status: item.hsi_anchor_state?.entry?.status || 'UNRESOLVED',
          entry_anchor_id: item.hsi_anchor_state?.entry?.anchor_id || null,
          confluence_count: item.hsi_anchor_state?.confluence?.count || 0,
          confluence_anchor_ids: [...(item.hsi_anchor_state?.confluence?.anchor_ids || [])]
        },
        source_event_ids: [...(item.source_event_ids || [])],
        source_bar_keys: [...(item.source_bar_keys || [])],
        no_lookahead: item.no_lookahead === true
      } : null;
      decision.input_state_ids[tf] = item?.state_id || null;
      const eventId = tfEvents.get(tf)?.event_id || '';
      if (eventId) decision.input_state_event_ids.push(eventId);
      decision.input_state_summary[tf] = item ? {
        trend_state: item.trend_state || 'UNDETERMINED',
        cycle_phase: item.cycle_state?.phase || 'UNDETERMINED',
        cycle_context: item.cycle_state?.context_state || 'UNKNOWN',
        bb_phase: item.bb_state?.phase || 'UNDETERMINED',
        data_sufficiency: item.data_sufficiency?.status || 'MISSING',
        state_id: item.state_id || null
      } : { data_sufficiency: 'MISSING', state_id: null };
    });
    decision.input_state_event_ids = uniqueStrings(decision.input_state_event_ids);
    const locks = new Set();
    const rules = upperContextDecisionRules(facts, policy).sort((a, b) => a.priority - b.priority || String(a.rule_id).localeCompare(String(b.rule_id)));
    rules.forEach(rule => {
      const evaluation = {
        rule_id: rule.rule_id,
        priority: rule.priority,
        category: rule.category,
        matched: rule.matched === true,
        summary: rule.summary,
        reason_codes: [...(rule.reason_codes || [])],
        applied_effects: []
      };
      if (rule.matched === true) {
        decision.matched_rules.push(rule.rule_id);
        decision.reason_codes.push(...(rule.reason_codes || []));
        decision.rule_ids.push(rule.rule_id);
        (rule.effects || []).forEach(effect => {
          if (applyUpperDecisionEffect(decision, effect, rule, locks)) {
            evaluation.applied_effects.push({ target: effect.target, assign: cloneJsonValue(effect.assign || {}), locked: effect.lock === true });
          }
        });
      }
      decision.rule_evaluations.push(evaluation);
    });
    decision.reason_codes = uniqueStrings(decision.reason_codes);
    decision.rule_ids = uniqueStrings(decision.rule_ids);
    decision.matched_rules = uniqueStrings(decision.matched_rules);
    const h4Direction = facts.direction.h4_direction;
    const h1Trend = facts.h1_trend;
    if (decision.position_policy.h1_exit_trigger.enabled === true) {
      if ((h4Direction === 'LONG' && h1Trend === 'DOWN') || (h4Direction === 'SHORT' && h1Trend === 'UP')) {
        decision.position_policy.h1_exit_trigger.signal = 'CONFIRMED';
        decision.position_policy.h1_exit_trigger.reason_codes = uniqueStrings([...(decision.position_policy.h1_exit_trigger.reason_codes || []), 'H1_OPPOSES_H4_DIRECTION']);
      } else if (['REVERSAL_WATCH', 'NO_TREND'].includes(h1Trend)) {
        decision.position_policy.h1_exit_trigger.signal = 'WATCH';
        decision.position_policy.h1_exit_trigger.reason_codes = uniqueStrings([...(decision.position_policy.h1_exit_trigger.reason_codes || []), `H1_${h1Trend}`]);
      }
    }
    const entryPolicies = Object.entries(decision.entry_policy);
    const allowed = entryPolicies.filter(([, item]) => ['ALLOW_SEARCH', 'CONDITIONAL'].includes(item.status)).map(([name]) => name);
    const blocked = entryPolicies.filter(([, item]) => item.status === 'BLOCKED').map(([name]) => name);
    if (decision.no_trade.active) decision.decision_mode = 'NO_TRADE';
    else if (decision.position_policy.h1_exit_trigger.enabled && decision.position_policy.h1_exit_trigger.signal === 'CONFIRMED') decision.decision_mode = 'EXIT_CONTEXT_CONFIRMED';
    else if (decision.position_policy.profit_take_armed.enabled) decision.decision_mode = 'PROFIT_TAKE_ARMED';
    else if (decision.position_policy.h1_exit_trigger.enabled) decision.decision_mode = 'DEFENSIVE_MANAGEMENT';
    else if (allowed.length) decision.decision_mode = 'ENTRY_SEARCH';
    else decision.decision_mode = 'WATCH';
    decision.m5_instruction = {
      mode: decision.decision_mode === 'NO_TRADE' ? 'NO_NEW_ENTRY'
        : decision.decision_mode === 'EXIT_CONTEXT_CONFIRMED' ? 'AWAIT_M5_EXIT_EXECUTION'
          : ['PROFIT_TAKE_ARMED', 'DEFENSIVE_MANAGEMENT'].includes(decision.decision_mode) ? 'MONITOR_H1_EXIT_TRIGGER'
            : allowed.length ? 'SEARCH_ALLOWED_TRIGGERS' : 'WAIT',
      allowed_searches: allowed,
      blocked_actions: blocked,
      action_execution: 'NOT_EVALUATED'
    };
    decision.direction_bias.reason_codes = uniqueStrings([
      `H4_TREND_${facts.direction.h4_trend}`,
      `H1_TREND_${facts.direction.h1_trend}`,
      `H4_H1_${facts.direction.alignment}`
    ]);
    decision.decision_signature = JSON.stringify(upperDecisionCompact(decision));
    decision.decision_id = `upper_decision_${stableSwingToken(decision.reference.state_as_of_ms)}_${stableTextHash(decision.decision_signature)}`;
    decision.comparison_to_previous_snapshot = compareUpperDecision(decision, previous);
    const errors = [];
    const warnings = [];
    policy.required_timeframes?.forEach(tf => {
      if (!decision.input_state_ids[String(tf).toUpperCase()]) errors.push(`${tf}: input_state_id is missing.`);
    });
    if (!facts.all_no_lookahead || policy.no_lookahead !== true) errors.push('Upper Context Decision input contains lookahead or policy no_lookahead is disabled.');
    if (decision.position_policy.week_direct_close !== false || decision.management_policy.week_direct_close !== false) errors.push('WEEK direct close must remain false.');
    if (decision.action_execution !== 'NOT_EVALUATED' || decision.m5_instruction.action_execution !== 'NOT_EVALUATED') errors.push('M5 action execution must remain NOT_EVALUATED in this phase.');
    if (!decision.rule_ids.length) warnings.push('No decision rule matched; Decision Mode remains WATCH.');
    if (facts.not_ready_timeframes.length) warnings.push(`New entry blocked by data sufficiency: ${facts.not_ready_timeframes.join(', ')}.`);
    decision.status = errors.length ? 'invalid' : 'ready';
    decision.validation = {
      valid: errors.length === 0,
      checked_at: nowLocalIso(),
      errors,
      warnings,
      input_state_ids_present: errors.every(message => !message.includes('input_state_id')),
      no_lookahead: errors.every(message => !message.includes('lookahead')),
      week_direct_close_forbidden: errors.every(message => !message.includes('WEEK direct close')),
      action_execution_forbidden: errors.every(message => !message.includes('action execution'))
    };
    const decisionEvent = buildUpperContextDecisionEvent(decision, previous);
    decision.decision_events = [decisionEvent];
    decision.teacher_guard = 'Upper Context Decision emits permission to search, wait, hold, protect, or monitor H1 exit. It does not confirm Expansion itself, evaluate M5 triggers, inspect live positions, or execute Entry/Close.';
    return decision;
  }

  function upperContextDecisionSnapshotPreview(snapshot) {
    if (!snapshot) return null;
    const copy = cloneJsonValue(snapshot);
    if (copy.input_states) copy.input_states = '[full TimeframeState inputs omitted from preview]';
    if (Array.isArray(copy.rule_evaluations)) copy.rule_evaluations = copy.rule_evaluations.map(item => ({ rule_id: item.rule_id, priority: item.priority, matched: item.matched, applied_effects: item.applied_effects }));
    if (Array.isArray(copy.decision_events)) copy.decision_events = `[${copy.decision_events.length} event omitted from preview]`;
    return copy;
  }

  function mergeUpperContextDecisionChartEvents(existingEvents, snapshot) {
    const kept = (existingEvents || []).filter(event => event?.generated_by !== UPPER_CONTEXT_DECISION_GENERATOR);
    const projected = (snapshot?.decision_events || []).filter(event => event?.display?.visible === true);
    return [...kept, ...projected];
  }

  function m5ExecutionDirection(decision) {
    const value = String(decision?.direction_bias?.value || 'UNDETERMINED').toUpperCase();
    return value === 'LONG' || value === 'SHORT' ? value : 'UNDETERMINED';
  }

  function m5ExecutionNormalEntryV08Facts(timeframeSnapshot) {
    const timeframes = timeframeSnapshot?.timeframes || {};
    const h4 = timeframes.H4 || {};
    const h1 = timeframes.H1 || {};
    const m5 = timeframes.M5 || {};
    const h4Bar = h4.latest_confirmed_bar || {};
    const h1Bar = h1.latest_confirmed_bar || {};

    const h4Close = numberOrNull(h4Bar.close);
    const h4T3 = numberOrNull(h4Bar.t3_20_0_2);
    const h4T3Slope = numberOrNull(h4Bar.t3_slope);
    const h4T3Direction = String(h4Bar.t3_direction || (h4T3Slope > 0 ? 'up' : h4T3Slope < 0 ? 'down' : '')).toLowerCase();
    const h4T3Position = String(h4Bar.close_t3_position || (h4Close != null && h4T3 != null ? (h4Close > h4T3 ? 'above' : h4Close < h4T3 ? 'below' : 'equal') : '')).toLowerCase();

    const h1Close = numberOrNull(h1Bar.close);
    const h1T3 = numberOrNull(h1Bar.t3_20_0_2);
    const h1T3Slope = numberOrNull(h1Bar.t3_slope);
    const h1T3Direction = String(h1Bar.t3_direction || (h1T3Slope > 0 ? 'up' : h1T3Slope < 0 ? 'down' : '')).toLowerCase();
    const h1T3Position = String(h1Bar.close_t3_position || (h1Close != null && h1T3 != null ? (h1Close > h1T3 ? 'above' : h1Close < h1T3 ? 'below' : 'equal') : '')).toLowerCase();

    const m5Trend = String(m5.trend_state || 'UNDETERMINED').toUpperCase();
    const h4CyclePhase = String(h4?.cycle_state?.phase || 'UNDETERMINED').toUpperCase();
    const h1CyclePhase = String(h1?.cycle_state?.phase || 'UNDETERMINED').toUpperCase();

    const h4T3Long = h4T3 != null && h4Close != null && h4T3Direction === 'up' && h4T3Position === 'above';
    const h4T3Short = h4T3 != null && h4Close != null && h4T3Direction === 'down' && h4T3Position === 'below';
    const h1T3Long = h1T3 != null && h1Close != null && h1T3Direction === 'up' && h1T3Position === 'above';
    const h1T3Short = h1T3 != null && h1Close != null && h1T3Direction === 'down' && h1T3Position === 'below';
    const m5Long = m5Trend === 'UP';
    const m5Short = m5Trend === 'DOWN';
    const h4H1T3Long = h4T3Long && h1T3Long;
    const h4H1T3Short = h4T3Short && h1T3Short;
    const h4CycleLate = h4CyclePhase === 'LATE';
    const h1CycleLate = h1CyclePhase === 'LATE';

    let direction = 'UNDETERMINED';
    if (h4H1T3Long && m5Long) direction = 'LONG';
    if (h4H1T3Short && m5Short) direction = 'SHORT';

    return {
      direction,
      h4_t3_ready: h4T3 != null && h4Close != null && ['up', 'down'].includes(h4T3Direction),
      h4_t3_direction: h4T3Direction.toUpperCase() || 'UNDETERMINED',
      h4_t3_position: h4T3Position.toUpperCase() || 'UNDETERMINED',
      h4_t3_value: h4T3,
      h4_close: h4Close,
      h1_t3_ready: h1T3 != null && h1Close != null && ['up', 'down'].includes(h1T3Direction),
      h1_t3_direction: h1T3Direction.toUpperCase() || 'UNDETERMINED',
      h1_t3_position: h1T3Position.toUpperCase() || 'UNDETERMINED',
      h1_t3_value: h1T3,
      h1_close: h1Close,
      m5_trend: m5Trend,
      h4_h1_t3_aligned: h4H1T3Long || h4H1T3Short,
      m5_dow_aligned: (h4H1T3Long && m5Long) || (h4H1T3Short && m5Short),
      h4_cycle_phase: h4CyclePhase,
      h1_cycle_phase: h1CyclePhase,
      h4_cycle_late: h4CycleLate,
      h1_cycle_late: h1CycleLate,
      cycle_guard_passed: !h1CycleLate,
      entry_direction_ready: direction === 'LONG' || direction === 'SHORT'
    };
  }

  function m5ExecutionTimeframeProfile(draft, timeframe) {
    const tf = String(timeframe || '').toUpperCase();
    return (draft?.timeframe_profiles || []).find(item => String(item?.timeframe || '').toUpperCase() === tf) || null;
  }

  function m5ExecutionExpansionLiteFacts(timeframeSnapshot, draft, dowConfirmation) {
    const timeframes = timeframeSnapshot?.timeframes || {};
    const h4 = timeframes.H4 || {};
    const h1 = timeframes.H1 || {};
    const m5 = timeframes.M5 || {};
    const h4Bar = h4.latest_confirmed_bar || {};
    const h1Bar = h1.latest_confirmed_bar || {};
    const h4Close = numberOrNull(h4Bar.close);
    const h4T3 = numberOrNull(h4Bar.t3_20_0_2);
    const h1Close = numberOrNull(h1Bar.close);
    const h1T3 = numberOrNull(h1Bar.t3_20_0_2);
    const h1Cycle = h1.cycle_state || {};
    const h1SwingState = h1.swing_state || {};
    const h1Profile = m5ExecutionTimeframeProfile(draft, 'H1');
    const confirmationDirection = String(dowConfirmation?.direction || '').toUpperCase();
    const confirmationSide = confirmationDirection === 'UP' ? 'LONG' : confirmationDirection === 'DOWN' ? 'SHORT' : 'UNDETERMINED';
    // Expansion-Lite固有のH1 Entry Window判定。
    // Longは最新H1安値候補、Shortは最新H1高値候補を優先し、
    // H1 Profileに明示したcycle.entry_allowed_max_bars以内だけEntryを許可する。
    // Confirm barsはSwing確定用であり、Entry Windowの長さには使用しない。
    // この候補点はH1 Cycle Gateの観測にだけ使用し、NORMAL/EXPANSIONのHSI起点やDow起点へ流用しない。
    const directionalPendingOrigin = confirmationSide === 'LONG'
      ? h1SwingState.latest_pending_low
      : confirmationSide === 'SHORT'
        ? h1SwingState.latest_pending_high
        : null;
    const directionalActiveOrigin = confirmationSide === 'LONG'
      ? h1SwingState.latest_active_low
      : confirmationSide === 'SHORT'
        ? h1SwingState.latest_active_high
        : null;
    const h1DirectionalOrigin = directionalPendingOrigin || directionalActiveOrigin || h1Cycle.origin || null;
    const h1ConfirmBars = Math.max(1, Number(h1DirectionalOrigin?.confirm_bars ?? h1Profile?.confirm_bars ?? h1Cycle?.origin?.confirm_bars ?? 0));
    const h1EntryAllowedMaxBars = numberOrNull(h1Profile?.cycle?.entry_allowed_max_bars);
    const latestH1Index = numberOrNull(h1Bar.index);
    const originH1Index = numberOrNull(h1DirectionalOrigin?.source_index);
    const elapsedFromDirectionalOrigin = latestH1Index != null && originH1Index != null
      ? Math.max(0, latestH1Index - originH1Index)
      : null;
    const h1CycleElapsedBars = elapsedFromDirectionalOrigin ?? numberOrNull(h1Cycle.elapsed_bars);
    const h1CycleEntryAllowed = Boolean(h1DirectionalOrigin)
      && Number.isInteger(h1EntryAllowedMaxBars)
      && h1EntryAllowedMaxBars >= 0
      && h1CycleElapsedBars != null
      && h1CycleElapsedBars <= h1EntryAllowedMaxBars;
    const longT3Aligned = h4Close != null && h4T3 != null && h4Close >= h4T3
      && h1Close != null && h1T3 != null && h1Close >= h1T3;
    const shortT3Aligned = h4Close != null && h4T3 != null && h4Close <= h4T3
      && h1Close != null && h1T3 != null && h1Close <= h1T3;
    let direction = 'UNDETERMINED';
    if (confirmationSide === 'LONG' && longT3Aligned && h1CycleEntryAllowed) direction = 'LONG';
    if (confirmationSide === 'SHORT' && shortT3Aligned && h1CycleEntryAllowed) direction = 'SHORT';
    return {
      direction,
      confirmation_side: confirmationSide,
      h4_close: h4Close,
      h4_t3: h4T3,
      h1_close: h1Close,
      h1_t3: h1T3,
      h4_t3_side_long: h4Close != null && h4T3 != null && h4Close >= h4T3,
      h4_t3_side_short: h4Close != null && h4T3 != null && h4Close <= h4T3,
      h1_t3_side_long: h1Close != null && h1T3 != null && h1Close >= h1T3,
      h1_t3_side_short: h1Close != null && h1T3 != null && h1Close <= h1T3,
      h1_cycle_origin: cloneJsonValue(h1DirectionalOrigin || null),
      h1_cycle_origin_source: directionalPendingOrigin ? 'DIRECTIONAL_PENDING_SWING' : directionalActiveOrigin ? 'DIRECTIONAL_ACTIVE_SWING' : 'GENERIC_CYCLE_ORIGIN',
      h1_cycle_elapsed_bars: h1CycleElapsedBars,
      h1_confirm_bars: h1ConfirmBars,
      h1_cycle_entry_allowed_max_bars: h1EntryAllowedMaxBars,
      h1_cycle_entry_allowed: h1CycleEntryAllowed,
      // 後方互換用。意味は「前半」ではなく明示Entry Window。
      h1_cycle_front_half_limit: h1EntryAllowedMaxBars,
      h1_cycle_front_half: h1CycleEntryAllowed,
      m5_trend_state: String(m5.trend_state || 'UNDETERMINED').toUpperCase(),
      day_cycle_position_used: false,
      entry_direction_ready: direction === 'LONG' || direction === 'SHORT'
    };
  }

  function m5ExecutionExpansionLiteAnchorResolution(dowConfirmation) {
    const anchorPrice = numberOrNull(dowConfirmation?.anchor_price);
    const confirmationId = String(dowConfirmation?.confirmation_id || '');
    if (!confirmationId || anchorPrice == null) {
      return { status: 'UNRESOLVED', anchor_id: null, anchor: null, reason_codes: ['EXPANSION_LITE_DOW_ANCHOR_UNRESOLVED'] };
    }
    const direction = String(dowConfirmation?.direction || '').toUpperCase() === 'DOWN' ? 'DOWN' : 'UP';
    const anchorId = `expansion_lite_anchor_${stableSwingToken(confirmationId)}`;
    return {
      status: 'RESOLVED_REFERENCE',
      anchor_id: anchorId,
      anchor: {
        anchor_id: anchorId,
        source_anchor_point_id: dowConfirmation?.anchor_point_id || null,
        dow_confirmation_id: confirmationId,
        price: anchorPrice,
        pivot_time: dowConfirmation?.anchor_time || null,
        direction,
        purpose: 'EXPANSION_LITE_ENTRY_AND_LIFECYCLE'
      },
      reason_codes: ['EXPANSION_LITE_DOW_CONFIRMATION_ANCHOR_ADOPTED']
    };
  }

  function m5ExecutionLevelTouch(bar, anchorPrice, direction, raw, label, policy) {
    const levelPrice = m5ExecutionTargetPrice(anchorPrice, direction, raw, policy);
    const open = numberOrNull(bar?.open);
    const high = numberOrNull(bar?.high);
    const low = numberOrNull(bar?.low);
    const touched = direction === 'SHORT'
      ? low != null && levelPrice != null && low <= levelPrice
      : high != null && levelPrice != null && high >= levelPrice;
    const passedAtOpen = direction === 'SHORT'
      ? open != null && levelPrice != null && open <= levelPrice
      : open != null && levelPrice != null && open >= levelPrice;
    return { raw: Number(raw), label: String(label || raw), price: levelPrice, touched, passed_at_open: passedAtOpen, open, high, low };
  }

  function m5ExecutionExpansionLiteOpportunity(portfolio, dowConfirmation, entryResolution, referenceMs, referenceTime) {
    portfolio.expansion_lite_entry_opportunities = Array.isArray(portfolio.expansion_lite_entry_opportunities)
      ? portfolio.expansion_lite_entry_opportunities : [];
    const confirmationId = String(dowConfirmation?.confirmation_id || '');
    if (!confirmationId) return null;
    let opportunity = portfolio.expansion_lite_entry_opportunities.find(item => String(item?.dow_confirmation_id || '') === confirmationId) || null;
    if (!opportunity) {
      opportunity = {
        opportunity_id: `expansion_lite_opportunity_${stableSwingToken(confirmationId)}`,
        rule_lane: RULE_LANE_EXPANSION_LITE,
        dow_confirmation_id: confirmationId,
        confirmation_direction: String(dowConfirmation?.direction || '').toUpperCase(),
        confirmed_at: dowConfirmation?.confirmed_at || null,
        confirmed_at_ms: numberOrNull(dowConfirmation?.confirmed_at_ms),
        anchor_id: entryResolution?.anchor_id || null,
        anchor_price: numberOrNull(entryResolution?.anchor?.price),
        status: 'WAITING_R3',
        created_at_reference: referenceTime,
        created_at_reference_ms: referenceMs,
        first_r3_touch_at: null,
        first_r3_touch_at_ms: null,
        entry_trade_id: null,
        entry_execution_price: null,
        terminal_reason_code: null
      };
      portfolio.expansion_lite_entry_opportunities.push(opportunity);
    }
    return opportunity;
  }

  function m5ExecutionExpansionLiteStructuralBreak(activeTrade, m5State) {
    const direction = String(activeTrade?.side || '').toUpperCase();
    const highRelation = String(m5State?.trend_detail?.high_relation || '').toUpperCase();
    const lowRelation = String(m5State?.trend_detail?.low_relation || '').toUpperCase();
    const trendState = String(m5State?.trend_state || 'UNDETERMINED').toUpperCase();
    if (direction === 'LONG') {
      const broken = ['LOWER', 'EQUAL'].includes(lowRelation) || trendState === 'DOWN';
      return { broken, relation: lowRelation, trend_state: trendState, point_type: 'CONFIRMED_LOW' };
    }
    if (direction === 'SHORT') {
      const broken = ['HIGHER', 'EQUAL'].includes(highRelation) || trendState === 'UP';
      return { broken, relation: highRelation, trend_state: trendState, point_type: 'CONFIRMED_HIGH' };
    }
    return { broken: false, relation: 'UNDETERMINED', trend_state: trendState, point_type: 'NONE' };
  }

  function m5ExecutionTrendAligned(direction, trendState) {
    const trend = String(trendState || 'UNDETERMINED').toUpperCase();
    return (direction === 'LONG' && trend === 'UP') || (direction === 'SHORT' && trend === 'DOWN');
  }

  function m5ExecutionOpenPositions(portfolio) {
    return (portfolio?.positions || []).filter(position => position?.status === 'OPEN' && Number(position?.units_open || 0) > 0);
  }

  function m5ExecutionPortfolioCompact(portfolio) {
    const open = m5ExecutionOpenPositions(portfolio);
    return {
      portfolio_status: open.length ? 'OPEN' : 'FLAT',
      active_trade_id: portfolio?.active_trade_id || null,
      open_position_count: open.length,
      open_units: open.reduce((sum, position) => sum + Number(position.units_open || 0), 0),
      open_positions: open.map(position => ({
        position_id: position.position_id,
        trade_id: position.trade_id,
        role: position.role,
        rule_lane: position.rule_lane || RULE_LANE_NORMAL,
        entry_evaluator_id: position.entry_evaluator_id || null,
        close_evaluator_id: position.close_evaluator_id || null,
        side: position.side,
        units_initial: position.units_initial,
        units_open: position.units_open,
        entry_price: position.entry_price,
        entry_anchor_id: position.entry_anchor_id,
        entry_anchor_price: position.entry_anchor_price,
        dow_confirmation_id: position.dow_confirmation_id || null,
        management_timeframe: position.management_timeframe,
        target_plan: cloneJsonValue(position.target_plan || {}),
        risk_profile: cloneJsonValue(position.risk_profile || {}),
        close_miss_plan: cloneJsonValue(position.close_miss_plan || {}),
        status: position.status
      })),
      normal_entry_opportunity_counts: m5ExecutionOpportunityCounts(portfolio),
      latest_normal_entry_opportunity: cloneJsonValue((portfolio?.normal_entry_opportunities || []).slice(-1)[0] || null),
      normal_anchor_lifecycle: cloneJsonValue(m5ExecutionEnsureNormalAnchorLifecycle(portfolio))
    };
  }

  function m5ExecutionDistanceRaw(price, anchorPrice, direction, policy) {
    const pointSize = Number(policy?.hsi_distance?.point_size || 0.001);
    const scale = Number(policy?.hsi_distance?.scale || 1);
    if (!(pointSize > 0) || !(scale > 0) || price == null || anchorPrice == null) return null;
    const signed = direction === 'SHORT' ? anchorPrice - price : price - anchorPrice;
    return signed / (pointSize * scale);
  }

  function m5ExecutionHsiBand(distanceRaw, policy) {
    const configured = Array.isArray(policy?.hsi_distance?.levels) ? policy.hsi_distance.levels : HSI_RANGE_LEVELS;
    const levels = configured.map(item => ({ raw: Number(item.raw), label: String(item.label || item.raw) })).filter(item => Number.isFinite(item.raw)).sort((a, b) => a.raw - b.raw);
    if (distanceRaw == null || !levels.length) return { current: null, next: null, levels };
    let current = null;
    let next = null;
    const boundaryEpsilon = 1e-6;
    levels.forEach(level => {
      if (level.raw <= Number(distanceRaw) + boundaryEpsilon) current = level;
      else if (!next) next = level;
    });
    return { current, next, levels };
  }

  function m5ExecutionTargetPrice(anchorPrice, direction, levelRaw, policy) {
    const pointSize = Number(policy?.hsi_distance?.point_size || 0.001);
    const scale = Number(policy?.hsi_distance?.scale || 1);
    if (anchorPrice == null || levelRaw == null || !(pointSize > 0) || !(scale > 0)) return null;
    const delta = Number(levelRaw) * pointSize * scale;
    return direction === 'SHORT' ? anchorPrice - delta : anchorPrice + delta;
  }

  function m5ExecutionTargetDirectionValid(direction, entryPrice, targetPrice) {
    const entry = numberOrNull(entryPrice);
    const target = numberOrNull(targetPrice);
    if (entry == null || target == null) return false;
    const epsilon = 1e-9;
    return String(direction || '').toUpperCase() === 'SHORT'
      ? target < entry - epsilon
      : target > entry + epsilon;
  }

  function m5ExecutionUpperWaveHsiFacts(timeframeSnapshot, candidatePrice, policy) {
    const timeframes = timeframeSnapshot?.timeframes || {};
    const day = timeframes.DAY || {};
    const h4 = timeframes.H4 || {};
    const cycle = h4.cycle_state || {};
    const cycleDirection = String(cycle.direction || '').toUpperCase();
    const h4WaveSide = cycleDirection === 'UP_CYCLE' ? 'LONG' : cycleDirection === 'DOWN_CYCLE' ? 'SHORT' : 'UNDETERMINED';
    const h4WaveDirection = h4WaveSide === 'LONG' ? 'UP' : h4WaveSide === 'SHORT' ? 'DOWN' : 'UNDETERMINED';
    const origin = cycle.origin || null;
    const originPrice = numberOrNull(origin?.pivot_price);
    const price = numberOrNull(candidatePrice);
    const distanceRaw = h4WaveSide === 'UNDETERMINED' ? null : m5ExecutionDistanceRaw(price, originPrice, h4WaveSide, policy);
    const band = m5ExecutionHsiBand(distanceRaw, policy);
    return {
      day_trend_state: String(day.trend_state || 'UNDETERMINED').toUpperCase(),
      h4_wave_side: h4WaveSide,
      h4_wave_direction: h4WaveDirection,
      h4_cycle_direction: cycleDirection || 'UNDETERMINED',
      h4_wave_anchor_id: origin?.point_id || null,
      h4_wave_anchor_time: origin?.pivot_time || null,
      h4_wave_anchor_price: originPrice,
      h4_wave_distance_raw: distanceRaw,
      h4_wave_range_level: band?.current?.label || null,
      candidate_price: price,
      no_lookahead: true
    };
  }

  function m5ExecutionEntryGuardDecision(ruleLane, entrySide, timeframeSnapshot, candidatePrice, policy) {
    const lane = String(ruleLane || RULE_LANE_NORMAL).toUpperCase();
    const side = String(entrySide || '').toUpperCase();
    const facts = m5ExecutionUpperWaveHsiFacts(timeframeSnapshot, candidatePrice, policy);
    const guardPolicy = policy?.entry_guard_policy || {};
    const matched = [];
    const normalR4 = guardPolicy.normal_h4_same_direction_r4 || {};
    const normalThreshold = Number(normalR4.block_at_or_above_raw ?? 233);
    const normalApplies = Array.isArray(normalR4.applies_to_rule_lanes)
      ? normalR4.applies_to_rule_lanes.map(value => String(value).toUpperCase()).includes(lane)
      : lane === RULE_LANE_NORMAL;
    if (normalR4.enabled !== false && normalApplies && lane === RULE_LANE_NORMAL
      && ['LONG', 'SHORT'].includes(side) && facts.h4_wave_side === side
      && Number.isFinite(facts.h4_wave_distance_raw)
      && Number(facts.h4_wave_distance_raw) >= normalThreshold - 1e-6) {
      matched.push({
        reason_code: 'NORMAL_H4_SAME_DIRECTION_R4_ENTRY_BLOCKED',
        rule_id: 'rule_normal_h4_same_direction_r4_entry_guard',
        summary: `H4現在波がEntry方向へ${String(normalR4.block_at_or_above_label || 'R4')}以上進行しているため、伸び切り後の新規Normal Entryを見送ります。`
      });
    }
    const common = guardPolicy.day_up_h4_down_r5_short || {};
    const commonThreshold = Number(common.block_at_or_above_raw ?? 377);
    const commonApplies = Array.isArray(common.applies_to_rule_lanes)
      ? common.applies_to_rule_lanes.map(value => String(value).toUpperCase()).includes(lane)
      : true;
    if (common.enabled !== false && commonApplies && side === 'SHORT'
      && facts.day_trend_state === 'UP' && facts.h4_wave_side === 'SHORT'
      && Number.isFinite(facts.h4_wave_distance_raw)
      && Number(facts.h4_wave_distance_raw) >= commonThreshold - 1e-6) {
      matched.push({
        reason_code: 'DAY_UP_H4_DOWN_R5_SHORT_ENTRY_BLOCKED',
        rule_id: 'rule_day_up_h4_down_r5_short_entry_guard',
        summary: `Day上昇トレンド中のH4調整下降が${String(common.block_at_or_above_label || 'R5')}以上進行しているため、下降末期からの新規Short Entryを見送ります。`
      });
    }
    const primary = matched.find(item => item.reason_code === 'NORMAL_H4_SAME_DIRECTION_R4_ENTRY_BLOCKED') || matched[0] || null;
    return {
      blocked: matched.length > 0,
      primary_reason_code: primary?.reason_code || null,
      summary: primary?.summary || '',
      matched_reason_codes: matched.map(item => item.reason_code),
      matched_rule_ids: matched.map(item => item.rule_id),
      facts
    };
  }

  function m5ExecutionNormalStopPlan(entryPrice, targetPrice, anchorPrice, direction, policy) {
    const source = policy?.normal_close_miss_policy || {};
    const side = String(direction || '').toUpperCase();
    const entry = numberOrNull(entryPrice);
    const target = numberOrNull(targetPrice);
    const anchor = numberOrNull(anchorPrice);
    const ratio = Number(source.max_loss_to_reward_ratio ?? 1.0);
    const rewardDistance = entry == null || target == null ? null : Math.abs(target - entry);
    const ratioStop = rewardDistance == null || !Number.isFinite(ratio) || ratio <= 0
      ? null : side === 'SHORT' ? entry + rewardDistance * ratio : entry - rewardDistance * ratio;
    const anchorIsLossSide = anchor != null && entry != null && (side === 'SHORT' ? anchor > entry : anchor < entry);
    let stopPrice = ratioStop;
    let hardLimitApplied = false;
    if (source.hsi_anchor_hard_limit !== false && anchorIsLossSide && ratioStop != null) {
      const limited = side === 'SHORT' ? Math.min(ratioStop, anchor) : Math.max(ratioStop, anchor);
      hardLimitApplied = Math.abs(limited - ratioStop) > 1e-12;
      stopPrice = limited;
    }
    const stopIsLossSide = stopPrice != null && entry != null && (side === 'SHORT' ? stopPrice > entry : stopPrice < entry);
    return {
      valid: ['LONG', 'SHORT'].includes(side) && m5ExecutionTargetDirectionValid(side, entry, target)
        && rewardDistance != null && rewardDistance > 0 && Number.isFinite(ratio) && ratio > 0 && stopIsLossSide,
      strategy_id: String(source.strategy_id || 'target_distance_ratio_v0_1'),
      max_loss_to_reward_ratio: ratio,
      reward_distance: rewardDistance,
      max_loss_distance: rewardDistance == null || !Number.isFinite(ratio) ? null : rewardDistance * ratio,
      ratio_stop_price: ratioStop,
      hsi_anchor_hard_limit_enabled: source.hsi_anchor_hard_limit !== false,
      hsi_anchor_hard_limit_price: anchor,
      hsi_anchor_hard_limit_applied: hardLimitApplied,
      stop_price: stopPrice,
      fixed_at_entry: source.fix_price_at_entry !== false,
      direction: side
    };
  }

  function m5ExecutionNormalDowStructureBreak(m5State) {
    const source = m5State?.trend_detail?.normal_dow_structure_break
      || m5State?.normal_dow_structure_break
      || null;
    if (!source) return null;
    const breakAtMs = numberOrNull(source.break_at_ms) ?? parseDateTimeMs(source.break_at);
    if (breakAtMs == null) return null;
    return {
      break_at: String(source.break_at || ''),
      break_at_ms: breakAtMs,
      break_event_id: source.break_event_id || null,
      break_state: String(source.break_state || '').toUpperCase(),
      previous_direction: String(source.previous_direction || '').toUpperCase(),
      invalidated_confirmation_id: source.invalidated_confirmation_id || null,
      invalidated_anchor_point_id: source.invalidated_anchor_point_id || null,
      trigger_point_id: source.trigger_point_id || null,
      reason_code: source.reason_code || 'NORMAL_DOW_STRUCTURE_BROKEN_BEFORE_ENTRY',
      lifecycle_action: source.lifecycle_action || 'RETIRE_PRE_ENTRY_CONFIRMATION_ANCHOR_OPPORTUNITY_R2_HISTORY'
    };
  }

  function m5ExecutionExpireNormalOpportunitiesPriorToDowBreak(portfolio, normalFacts, currentConfirmation, policy, referenceMs, referenceTime, m5State = null) {
    const opportunities = Array.isArray(portfolio?.normal_entry_opportunities) ? portfolio.normal_entry_opportunities : [];
    const currentTrend = String(normalFacts?.m5_trend || '').toUpperCase();
    const normalEntryPolicy = policy?.normal_entry_policy || {};
    const breakPolicy = String(normalEntryPolicy.pre_entry_dow_structure_break_policy || 'CONFIRMED_RESET_STATE_OR_NEWER_OPPOSITE_DOW_CONFIRMATION').toUpperCase();
    const resetStates = (normalEntryPolicy.pre_entry_dow_structure_break_states || ['REVERSAL_WATCH', 'NO_TREND', 'UNDETERMINED'])
      .map(value => String(value || '').toUpperCase());
    const breakFact = m5ExecutionNormalDowStructureBreak(m5State);
    const currentConfirmationId = String(currentConfirmation?.confirmation_id || '');
    const currentConfirmationMs = numberOrNull(currentConfirmation?.confirmed_at_ms);
    const currentConfirmationSide = String(currentConfirmation?.direction || '').toUpperCase() === 'UP'
      ? 'LONG' : String(currentConfirmation?.direction || '').toUpperCase() === 'DOWN' ? 'SHORT' : 'UNDETERMINED';
    const expired = [];
    for (const opportunity of opportunities) {
      if (String(opportunity?.status || '').toUpperCase() !== 'WAITING_R2') continue;
      const confirmedMs = numberOrNull(opportunity?.confirmed_at_ms);
      if (confirmedMs != null && referenceMs != null && Number(referenceMs) < confirmedMs) continue;
      const opportunitySide = String(opportunity?.direction || '').toUpperCase();
      const differentConfirmation = Boolean(currentConfirmationId && String(opportunity?.dow_confirmation_id || '') !== currentConfirmationId);
      const oppositeDirection = currentConfirmationSide !== 'UNDETERMINED' && currentConfirmationSide !== opportunitySide;
      const newerConfirmation = currentConfirmationMs != null && confirmedMs != null
        ? Number(currentConfirmationMs) > Number(confirmedMs)
        : differentConfirmation;
      const oppositeNewConfirmation = differentConfirmation && oppositeDirection && newerConfirmation;
      const confirmedBreakState = Boolean(
        breakFact
        && resetStates.includes(breakFact.break_state)
        && (confirmedMs == null || Number(breakFact.break_at_ms) > Number(confirmedMs))
        && (referenceMs == null || Number(breakFact.break_at_ms) <= Number(referenceMs))
      );
      const policyAllowsBreakState = ['CONFIRMED_RESET_STATE_OR_NEWER_OPPOSITE_DOW_CONFIRMATION', 'CONFIRMED_RESET_STATE'].includes(breakPolicy);
      const policyAllowsOpposite = ['CONFIRMED_RESET_STATE_OR_NEWER_OPPOSITE_DOW_CONFIRMATION', 'NEWER_OPPOSITE_DOW_CONFIRMATION_ONLY'].includes(breakPolicy);
      if (!((policyAllowsBreakState && confirmedBreakState) || (policyAllowsOpposite && oppositeNewConfirmation))) continue;

      const effectiveBreak = confirmedBreakState ? breakFact : {
        break_at: referenceTime || currentConfirmation?.confirmed_at || '',
        break_at_ms: currentConfirmationMs ?? numberOrNull(referenceMs),
        break_event_id: currentConfirmationId || null,
        break_state: currentTrend,
        previous_direction: opportunitySide === 'LONG' ? 'UP' : 'DOWN',
        invalidated_confirmation_id: opportunity?.dow_confirmation_id || null,
        invalidated_anchor_point_id: opportunity?.anchor_id || null,
        trigger_point_id: null,
        reason_code: 'NORMAL_DOW_STRUCTURE_BROKEN_BEFORE_ENTRY',
        lifecycle_action: 'RETIRE_PRE_ENTRY_CONFIRMATION_ANCHOR_OPPORTUNITY_R2_HISTORY'
      };
      opportunity.status = 'EXPIRED';
      opportunity.terminal_reason_code = 'NORMAL_DOW_STRUCTURE_BROKEN_BEFORE_ENTRY';
      opportunity.structure_broken_at = effectiveBreak.break_at;
      opportunity.structure_broken_at_ms = numberOrNull(effectiveBreak.break_at_ms);
      opportunity.structure_break_event_id = effectiveBreak.break_event_id || null;
      opportunity.structure_break_trend_state = effectiveBreak.break_state || currentTrend;
      opportunity.structure_break_confirmation_id = currentConfirmationId || null;
      opportunity.structure_break_confirmation_side = currentConfirmationSide;
      opportunity.anchor_invalidated_before_entry = true;
      opportunity.anchor_retired_before_entry = true;
      opportunity.r2_history_retired_before_entry = true;
      opportunity.r2_history_retired_reason = 'NORMAL_DOW_STRUCTURE_BROKEN_BEFORE_ENTRY';
      opportunity.first_r2_touch_at = null;
      opportunity.first_r2_touch_at_ms = null;
      opportunity.r2_price = null;
      opportunity.normal_anchor_lifecycle_after_break = m5ExecutionRetireNormalAnchorBeforeEntry(portfolio, opportunity, effectiveBreak);
      expired.push(opportunity);
    }
    return expired;
  }

  function m5ExecutionBarFill(direction, bar, requestedPrice, fillKind = 'TARGET') {
    const side = String(direction || '').toUpperCase();
    const kind = String(fillKind || 'TARGET').toUpperCase();
    const requested = numberOrNull(requestedPrice);
    const open = numberOrNull(bar?.open);
    const high = numberOrNull(bar?.high);
    const low = numberOrNull(bar?.low);
    if (!['LONG', 'SHORT'].includes(side) || requested == null || high == null || low == null) {
      return { touched: false, execution_price: null, requested_price: requested, fill_mode: 'INVALID_INPUT', within_bar: false, open, high, low };
    }
    const inRange = requested >= low - 1e-9 && requested <= high + 1e-9;
    let touched = false;
    let executionPrice = null;
    let fillMode = 'NOT_TOUCHED';
    if (kind === 'STOP') {
      if (side === 'SHORT') {
        if (open != null && open >= requested) { touched = true; executionPrice = open; fillMode = 'OPEN_GAP_STOP'; }
        else if (high >= requested && inRange) { touched = true; executionPrice = requested; fillMode = 'INTRABAR_STOP'; }
      } else {
        if (open != null && open <= requested) { touched = true; executionPrice = open; fillMode = 'OPEN_GAP_STOP'; }
        else if (low <= requested && inRange) { touched = true; executionPrice = requested; fillMode = 'INTRABAR_STOP'; }
      }
    } else {
      if (side === 'SHORT') {
        if (open != null && open <= requested) { touched = true; executionPrice = open; fillMode = 'OPEN_GAP_TARGET'; }
        else if (low <= requested && inRange) { touched = true; executionPrice = requested; fillMode = 'INTRABAR_TARGET'; }
      } else {
        if (open != null && open >= requested) { touched = true; executionPrice = open; fillMode = 'OPEN_GAP_TARGET'; }
        else if (high >= requested && inRange) { touched = true; executionPrice = requested; fillMode = 'INTRABAR_TARGET'; }
      }
    }
    const withinBar = executionPrice != null && executionPrice >= low - 1e-9 && executionPrice <= high + 1e-9;
    return { touched: touched && withinBar, execution_price: withinBar ? executionPrice : null, requested_price: requested, fill_mode: withinBar ? fillMode : 'OUTSIDE_BAR_REJECTED', within_bar: withinBar, open, high, low };
  }

  function m5ExecutionPriceReached(direction, price, target) {
    if (price == null || target == null) return false;
    return direction === 'SHORT' ? price <= target : price >= target;
  }

  function m5ExecutionPriceInvalidated(direction, price, invalidationPrice) {
    if (price == null || invalidationPrice == null) return false;
    return direction === 'SHORT' ? price >= invalidationPrice : price <= invalidationPrice;
  }

  function m5ExecutionBarTouch(position, bar) {
    const side = String(position?.side || '').toUpperCase();
    const high = numberOrNull(bar?.high);
    const low = numberOrNull(bar?.low);
    const stopPrice = numberOrNull(position?.invalidation_rule?.invalidation_price);
    const targetPrice = numberOrNull(position?.target_plan?.next_target_price);
    const entryPrice = numberOrNull(position?.entry_price);
    const stopFill = m5ExecutionBarFill(side, bar, stopPrice, 'STOP');
    const targetDirectionValid = m5ExecutionTargetDirectionValid(side, entryPrice, targetPrice);
    const targetFill = targetDirectionValid
      ? m5ExecutionBarFill(side, bar, targetPrice, 'TARGET')
      : { touched: false, execution_price: null, requested_price: targetPrice, fill_mode: 'TARGET_DIRECTION_INVALID', within_bar: false };
    return {
      high,
      low,
      stop_price: stopPrice,
      target_price: targetPrice,
      stop_execution_price: stopFill.execution_price,
      target_execution_price: targetFill.execution_price,
      stop_fill_mode: stopFill.fill_mode,
      target_fill_mode: targetFill.fill_mode,
      target_direction_valid: targetDirectionValid,
      stop_touched: stopFill.touched,
      target_touched: targetFill.touched,
      ambiguous: stopFill.touched && targetFill.touched
    };
  }

  function m5ExecutionDowConfirmation(m5State) {
    const source = m5State?.trend_detail?.normal_dow_confirmation || null;
    if (!source?.confirmation_id) return null;
    const direction = String(source.direction || '').toUpperCase();
    if (!['UP', 'DOWN'].includes(direction)) return null;
    return {
      confirmation_id: String(source.confirmation_id),
      direction,
      confirmed_at: String(source.confirmed_at || ''),
      confirmed_at_ms: numberOrNull(source.confirmed_at_ms),
      anchor_point_id: source.anchor_point_id || null,
      anchor_type: source.anchor_type || null,
      anchor_price: numberOrNull(source.anchor_price),
      anchor_time: source.anchor_time || null,
      confirmation_signature: source.confirmation_signature || '',
      breakout_threshold_point_id: source.breakout_threshold_point_id || null,
      breakout_threshold_price: numberOrNull(source.breakout_threshold_price),
      opportunity_policy: source.opportunity_policy || 'ONE_NORMAL_ENTRY_AT_DOW_BREAKOUT_CONFIRMATION_IF_R2_READY_ELSE_FIRST_R2_TOUCH'
    };
  }

  function m5ExecutionLatestClosedTradeMs(portfolio, ruleLane = null) {
    const lane = ruleLane == null ? null : String(ruleLane).toUpperCase();
    const values = (portfolio?.trades || [])
      .filter(trade => trade?.status === 'CLOSED' && (!lane || m5TradeRuleLane(trade, null) === lane))
      .map(trade => numberOrNull(trade?.closed_at_ms))
      .filter(value => value != null);
    return values.length ? Math.max(...values) : null;
  }

  function m5ExecutionR2Touch(bar, anchorPrice, direction, policy) {
    const entryRaw = Number(policy?.normal_entry_policy?.entry_raw ?? policy?.hsi_distance?.entry_min_raw ?? 89);
    const entryLabel = String(policy?.normal_entry_policy?.entry_label || policy?.hsi_distance?.entry_min_label || 'R2').toUpperCase();
    const entryPrice = m5ExecutionTargetPrice(anchorPrice, direction, entryRaw, policy);
    const open = numberOrNull(bar?.open);
    const high = numberOrNull(bar?.high);
    const low = numberOrNull(bar?.low);
    const touched = direction === 'SHORT'
      ? low != null && entryPrice != null && low <= entryPrice
      : high != null && entryPrice != null && high >= entryPrice;
    const passedBeforeBar = direction === 'SHORT'
      ? open != null && entryPrice != null && open <= entryPrice
      : open != null && entryPrice != null && open >= entryPrice;
    return {
      entry_raw: entryRaw,
      entry_label: entryLabel,
      entry_price: entryPrice,
      open,
      high,
      low,
      touched,
      passed_before_bar: passedBeforeBar
    };
  }

  function m5ExecutionR25Touch(bar, anchorPrice, direction, policy) {
    const targetRaw = Number(policy?.normal_entry_policy?.target_raw ?? 117);
    const targetLabel = String(policy?.normal_entry_policy?.target_label || '次HSI境界').toUpperCase();
    const targetPrice = m5ExecutionTargetPrice(anchorPrice, direction, targetRaw, policy);
    const open = numberOrNull(bar?.open);
    const high = numberOrNull(bar?.high);
    const low = numberOrNull(bar?.low);
    const close = numberOrNull(bar?.close);
    const touched = direction === 'SHORT'
      ? low != null && targetPrice != null && low <= targetPrice
      : high != null && targetPrice != null && high >= targetPrice;
    const closePassed = direction === 'SHORT'
      ? close != null && targetPrice != null && close <= targetPrice
      : close != null && targetPrice != null && close >= targetPrice;
    return {
      target_raw: targetRaw,
      target_label: targetLabel,
      target_price: targetPrice,
      open,
      high,
      low,
      close,
      touched,
      close_passed: closePassed
    };
  }

  function m5ExecutionOpportunityForConfirmation(portfolio, confirmation, anchor, referenceMs, referenceTime) {
    if (!confirmation?.confirmation_id) return null;
    portfolio.normal_entry_opportunities = Array.isArray(portfolio.normal_entry_opportunities) ? portfolio.normal_entry_opportunities : [];
    let opportunity = portfolio.normal_entry_opportunities.find(item => item?.dow_confirmation_id === confirmation.confirmation_id) || null;
    if (!opportunity) {
      opportunity = {
        opportunity_id: `normal_entry_opportunity_${stableSwingToken(confirmation.confirmation_id)}`,
        dow_confirmation_id: confirmation.confirmation_id,
        direction: confirmation.direction === 'UP' ? 'LONG' : 'SHORT',
        confirmed_at: confirmation.confirmed_at || '',
        confirmed_at_ms: numberOrNull(confirmation.confirmed_at_ms),
        created_at_reference: referenceTime || '',
        created_at_reference_ms: numberOrNull(referenceMs),
        anchor_id: anchor?.anchor_id || null,
        anchor_price: numberOrNull(anchor?.price ?? confirmation.anchor_price),
        anchor_time: anchor?.time || anchor?.pivot_time || confirmation?.anchor_time || null,
        breakout_threshold_price: numberOrNull(confirmation?.breakout_threshold_price),
        trigger_point_id: confirmation?.trigger_point_id || null,
        status: 'WAITING_R2',
        first_r2_touch_at: null,
        first_r2_touch_at_ms: null,
        entry_execution_mode: null,
        entry_execution_price: null,
        entry_trade_id: null,
        terminal_reason_code: null
      };
      portfolio.normal_entry_opportunities.push(opportunity);
      m5ExecutionAdoptNormalAnchorForOpportunity(portfolio, opportunity, confirmation, anchor, referenceMs, referenceTime);
    }
    return opportunity;
  }

  function m5ExecutionOpportunityCounts(portfolio) {
    const opportunities = Array.isArray(portfolio?.normal_entry_opportunities) ? portfolio.normal_entry_opportunities : [];
    return opportunities.reduce((counts, item) => {
      const key = String(item?.status || 'UNKNOWN').toUpperCase();
      counts[key] = (counts[key] || 0) + 1;
      return counts;
    }, {});
  }

  function m5ExecutionEmptyNormalAnchorLifecycle() {
    return {
      schema_version: 'normal_hsi_anchor_trade_lifecycle_v0_2',
      status: 'NONE',
      active_anchor_id: null,
      active_anchor_price: null,
      active_confirmation_id: null,
      active_trade_id: null,
      adopted_at: null,
      adopted_at_ms: null,
      last_retired_anchor_id: null,
      last_retired_confirmation_id: null,
      last_retired_trade_id: null,
      last_retired_at: null,
      last_retired_at_ms: null,
      last_retired_reason: null,
      retired_count: 0,
      next_required_state: 'NEW_M5_DOW_CONFIRMATION_AFTER_BREAK_OR_CLOSE'
    };
  }

  function m5ExecutionEnsureNormalAnchorLifecycle(portfolio) {
    if (!portfolio) return m5ExecutionEmptyNormalAnchorLifecycle();
    const current = portfolio.normal_anchor_lifecycle && typeof portfolio.normal_anchor_lifecycle === 'object'
      ? portfolio.normal_anchor_lifecycle
      : m5ExecutionEmptyNormalAnchorLifecycle();
    portfolio.normal_anchor_lifecycle = { ...m5ExecutionEmptyNormalAnchorLifecycle(), ...current };
    return portfolio.normal_anchor_lifecycle;
  }

  function m5ExecutionAdoptNormalAnchorForOpportunity(portfolio, opportunity, confirmation, anchor, referenceMs, referenceTime) {
    if (!portfolio || !opportunity || !confirmation?.confirmation_id) return m5ExecutionEnsureNormalAnchorLifecycle(portfolio);
    const lifecycle = m5ExecutionEnsureNormalAnchorLifecycle(portfolio);
    if (String(lifecycle.status || '') === 'ACTIVE') return lifecycle;
    lifecycle.status = 'WAITING_R2';
    lifecycle.active_anchor_id = anchor?.anchor_id || opportunity?.anchor_id || null;
    lifecycle.active_anchor_price = numberOrNull(anchor?.price ?? opportunity?.anchor_price ?? confirmation?.anchor_price);
    lifecycle.active_confirmation_id = confirmation.confirmation_id;
    lifecycle.active_trade_id = null;
    lifecycle.adopted_at = confirmation?.confirmed_at || referenceTime || null;
    lifecycle.adopted_at_ms = numberOrNull(confirmation?.confirmed_at_ms) ?? numberOrNull(referenceMs);
    lifecycle.next_required_state = 'R2_ENTRY_OR_CONFIRMED_DOW_BREAK';
    return lifecycle;
  }

  function m5ExecutionRetireNormalAnchorBeforeEntry(portfolio, opportunity, breakFact) {
    const lifecycle = m5ExecutionEnsureNormalAnchorLifecycle(portfolio);
    const opportunityConfirmationId = String(opportunity?.dow_confirmation_id || '');
    if (String(lifecycle.status || '') === 'ACTIVE') return null;
    if (lifecycle.active_confirmation_id && opportunityConfirmationId
      && String(lifecycle.active_confirmation_id) !== opportunityConfirmationId) return null;
    const retiredAnchorId = opportunity?.anchor_id || lifecycle.active_anchor_id || null;
    lifecycle.status = 'AWAITING_NEW_DOW_CONFIRMATION';
    lifecycle.last_retired_anchor_id = retiredAnchorId;
    lifecycle.last_retired_confirmation_id = opportunity?.dow_confirmation_id || lifecycle.active_confirmation_id || null;
    lifecycle.last_retired_trade_id = null;
    lifecycle.last_retired_at = breakFact?.break_at || opportunity?.structure_broken_at || null;
    lifecycle.last_retired_at_ms = numberOrNull(breakFact?.break_at_ms ?? opportunity?.structure_broken_at_ms);
    lifecycle.last_retired_reason = 'NORMAL_DOW_STRUCTURE_BROKEN_BEFORE_ENTRY';
    lifecycle.retired_count = Number(lifecycle.retired_count || 0) + 1;
    lifecycle.active_anchor_id = null;
    lifecycle.active_anchor_price = null;
    lifecycle.active_confirmation_id = null;
    lifecycle.active_trade_id = null;
    lifecycle.adopted_at = null;
    lifecycle.adopted_at_ms = null;
    lifecycle.next_required_state = 'NEW_M5_DOW_CONFIRMATION_AFTER_BREAK';
    return cloneJsonValue(lifecycle);
  }

  function m5ExecutionActivateNormalAnchor(portfolio, context, tradeId) {
    const lifecycle = m5ExecutionEnsureNormalAnchorLifecycle(portfolio);
    lifecycle.status = 'ACTIVE';
    lifecycle.active_anchor_id = context?.entryAnchor?.anchor_id || null;
    lifecycle.active_anchor_price = numberOrNull(context?.anchorPrice);
    lifecycle.active_confirmation_id = context?.dowConfirmation?.confirmation_id || null;
    lifecycle.active_trade_id = tradeId || null;
    lifecycle.adopted_at = context?.referenceTime || null;
    lifecycle.adopted_at_ms = numberOrNull(context?.referenceMs);
    lifecycle.next_required_state = 'TRADE_CLOSE';
    return lifecycle;
  }

  function m5ExecutionRetireNormalAnchor(portfolio, trade, context, closeClass) {
    const lifecycle = m5ExecutionEnsureNormalAnchorLifecycle(portfolio);
    const retiredAnchorId = trade?.entry_anchor_id || lifecycle.active_anchor_id || null;
    const retiredConfirmationId = trade?.dow_confirmation_id || lifecycle.active_confirmation_id || null;
    lifecycle.status = 'AWAITING_NEW_DOW_CONFIRMATION';
    lifecycle.last_retired_anchor_id = retiredAnchorId;
    lifecycle.last_retired_confirmation_id = retiredConfirmationId;
    lifecycle.last_retired_trade_id = trade?.trade_id || lifecycle.active_trade_id || null;
    lifecycle.last_retired_at = context?.referenceTime || null;
    lifecycle.last_retired_at_ms = numberOrNull(context?.referenceMs);
    lifecycle.last_retired_reason = closeClass || 'CLOSE';
    lifecycle.retired_count = Number(lifecycle.retired_count || 0) + 1;
    lifecycle.active_anchor_id = null;
    lifecycle.active_anchor_price = null;
    lifecycle.active_confirmation_id = null;
    lifecycle.active_trade_id = null;
    lifecycle.adopted_at = null;
    lifecycle.adopted_at_ms = null;
    lifecycle.next_required_state = 'NEW_M5_DOW_CONFIRMATION_AFTER_CLOSE';
    return {
      retired: Boolean(retiredAnchorId),
      anchor_id: retiredAnchorId,
      confirmation_id: retiredConfirmationId,
      trade_id: trade?.trade_id || null,
      retired_at: lifecycle.last_retired_at,
      retired_at_ms: lifecycle.last_retired_at_ms,
      reason: lifecycle.last_retired_reason,
      next_required_state: lifecycle.next_required_state
    };
  }

  function m5RuleLanePolicy(policy) {
    const source = policy?.rule_lane_policy || {};
    const activeEntryMode = String(source.active_entry_rule_lane || RULE_LANE_NORMAL).toUpperCase();
    const validLanes = [RULE_LANE_NORMAL, RULE_LANE_EXPANSION, RULE_LANE_EXPANSION_LITE];
    const configured = Array.isArray(source.enabled_entry_rule_lanes)
      ? source.enabled_entry_rule_lanes.map(value => String(value || '').toUpperCase()).filter(value => validLanes.includes(value))
      : [];
    let enabled = configured.length ? configured : (
      activeEntryMode === ENTRY_LANE_MODE_PARALLEL_RULE_LANES
        ? [RULE_LANE_NORMAL, RULE_LANE_EXPANSION, RULE_LANE_EXPANSION_LITE]
        : activeEntryMode === ENTRY_LANE_MODE_NORMAL_AND_EXPANSION_LITE
          ? [RULE_LANE_NORMAL, RULE_LANE_EXPANSION_LITE]
          : [activeEntryMode]
    );
    enabled = uniqueStrings(enabled).filter(lane => source?.lanes?.[lane]?.enabled !== false);
    return {
      active_entry_rule_lane: activeEntryMode,
      enabled_entry_rule_lanes: enabled,
      parallel_entry_enabled: source.parallel_entry_enabled === true || activeEntryMode === ENTRY_LANE_MODE_PARALLEL_RULE_LANES,
      simultaneous_entry_policy: String(source.simultaneous_entry_policy || (activeEntryMode === ENTRY_LANE_MODE_PARALLEL_RULE_LANES ? 'ALLOW_ALL_MATCHED_LANES' : 'SINGLE_LANE_ONLY')).toUpperCase(),
      simultaneous_entry_priority: String(source.simultaneous_entry_priority || RULE_LANE_EXPANSION_LITE).toUpperCase(),
      cross_lane_condition_sharing: String(source.cross_lane_condition_sharing || 'FORBIDDEN').toUpperCase(),
      shared_fact_source: String(source.shared_fact_source || 'TIMEFRAME_STATE_SNAPSHOT'),
      close_lane_source: String(source.close_lane_source || 'OPEN_TRADE_RULE_LANE'),
      lanes: cloneJsonValue(source.lanes || {})
    };
  }

  function m5TradeRuleLane(trade, position) {
    const value = String(trade?.rule_lane || position?.rule_lane || '').toUpperCase();
    if ([RULE_LANE_NORMAL, RULE_LANE_EXPANSION, RULE_LANE_EXPANSION_LITE].includes(value)) return value;
    if (String(trade?.entry_mode || position?.entry_mode || '').toUpperCase() === 'EXPANSION') return RULE_LANE_EXPANSION;
    return RULE_LANE_NORMAL;
  }

  function normalRuleLaneEntryDecision(input) {
    const {
      portfolio,
      referenceMs,
      referenceTime,
      price,
      direction,
      confirmationSide,
      normalFacts,
      m5State,
      dowConfirmation,
      entryResolution,
      entryAnchor,
      anchorPrice,
      r2Touch,
      currentBar,
      policy,
      minEntryLabel,
      hsiNotReachedReasonCode,
      timeframeSnapshot
    } = input || {};
    const latestClosedTradeMs = m5ExecutionLatestClosedTradeMs(portfolio, RULE_LANE_NORMAL);
    const normalAnchorLifecycle = m5ExecutionEnsureNormalAnchorLifecycle(portfolio);
    const triggerAligned = normalFacts?.entry_direction_ready === true;
    const normalPermission = normalFacts?.entry_direction_ready && normalFacts?.cycle_guard_passed ? 'ALLOW_SEARCH' : 'BLOCKED';
    const noTrade = normalFacts?.h1_cycle_late || !normalFacts?.entry_direction_ready;

    // v0.24の順序契約:
    // 1) まず確定Dow崩壊で旧WAITING_R2を終了する。
    // 2) 崩壊していなければ、最初に採用したConfirmation/Anchorを維持する。
    // 3) 同方向の後続Confirmationを新しい起点へ乗り換える理由にしない。
    const expiredPriorToEntry = policy?.normal_entry_policy?.pre_entry_dow_structure_break_expires_opportunity === false
      ? []
      : m5ExecutionExpireNormalOpportunitiesPriorToDowBreak(
          portfolio,
          normalFacts,
          dowConfirmation,
          policy,
          referenceMs,
          referenceTime,
          m5State
        );

    const lifecycleActiveConfirmationId = String(normalAnchorLifecycle?.active_confirmation_id || '');
    let activeWaitingOpportunity = lifecycleActiveConfirmationId
      ? (portfolio?.normal_entry_opportunities || []).find(item =>
          String(item?.dow_confirmation_id || '') === lifecycleActiveConfirmationId
          && String(item?.status || '').toUpperCase() === 'WAITING_R2'
        ) || null
      : null;

    let entryOpportunity = activeWaitingOpportunity;
    if (!entryOpportunity) {
      entryOpportunity = m5ExecutionOpportunityForConfirmation(portfolio, dowConfirmation, entryAnchor, referenceMs, referenceTime);
    }
    if ((!entryOpportunity || String(entryOpportunity.status || '').toUpperCase() !== 'WAITING_R2') && expiredPriorToEntry.length) {
      entryOpportunity = expiredPriorToEntry[expiredPriorToEntry.length - 1];
    }

    const opportunityDirection = String(entryOpportunity?.direction || '').toUpperCase();
    const opportunityConfirmationId = String(entryOpportunity?.dow_confirmation_id || '');
    const incomingConfirmationId = String(dowConfirmation?.confirmation_id || '');
    const preservingActiveConfirmation = Boolean(
      activeWaitingOpportunity
      && opportunityConfirmationId
      && incomingConfirmationId
      && opportunityConfirmationId !== incomingConfirmationId
    );

    const effectiveDowConfirmation = entryOpportunity && opportunityConfirmationId
      ? {
          ...(dowConfirmation && incomingConfirmationId === opportunityConfirmationId ? dowConfirmation : {}),
          confirmation_id: opportunityConfirmationId,
          direction: opportunityDirection === 'SHORT' ? 'DOWN' : 'UP',
          confirmed_at: entryOpportunity.confirmed_at || '',
          confirmed_at_ms: numberOrNull(entryOpportunity.confirmed_at_ms),
          trigger_point_id: entryOpportunity.trigger_point_id || null,
          anchor_point_id: entryOpportunity.anchor_id || null,
          anchor_price: numberOrNull(entryOpportunity.anchor_price),
          anchor_time: entryOpportunity.anchor_time || null,
          breakout_threshold_price: numberOrNull(entryOpportunity.breakout_threshold_price)
        }
      : dowConfirmation;
    const effectiveConfirmationSide = opportunityDirection || (
      effectiveDowConfirmation?.direction === 'DOWN' ? 'SHORT'
        : effectiveDowConfirmation?.direction === 'UP' ? 'LONG'
          : confirmationSide
    );
    const effectiveDirection = opportunityDirection || direction;
    const effectiveEntryAnchor = entryOpportunity?.anchor_id
      ? {
          anchor_id: entryOpportunity.anchor_id,
          price: numberOrNull(entryOpportunity.anchor_price),
          time: entryOpportunity.anchor_time || null,
          dow_confirmation_id: opportunityConfirmationId
        }
      : entryAnchor;
    const effectiveAnchorPrice = numberOrNull(entryOpportunity?.anchor_price) ?? numberOrNull(anchorPrice);
    const effectiveEntryResolution = effectiveEntryAnchor
      ? { status: 'RESOLVED_REFERENCE', anchor_id: effectiveEntryAnchor.anchor_id, anchor: effectiveEntryAnchor }
      : entryResolution;
    const effectiveR2Touch = currentBar && effectiveAnchorPrice != null && ['LONG', 'SHORT'].includes(effectiveConfirmationSide)
      ? m5ExecutionR2Touch(currentBar, effectiveAnchorPrice, effectiveConfirmationSide, policy)
      : r2Touch;

    const confirmationDirection = effectiveDowConfirmation?.direction === 'UP' ? 'LONG'
      : effectiveDowConfirmation?.direction === 'DOWN' ? 'SHORT' : 'UNDETERMINED';
    const confirmationAligned = confirmationDirection !== 'UNDETERMINED' && confirmationDirection === effectiveDirection;
    const anchorResolved = effectiveEntryResolution?.status === 'RESOLVED_REFERENCE' && effectiveAnchorPrice != null;
    const anchorMatchesConfirmation = Boolean(
      effectiveDowConfirmation?.confirmation_id
      && effectiveEntryAnchor?.dow_confirmation_id
      && String(effectiveEntryAnchor.dow_confirmation_id) === String(effectiveDowConfirmation.confirmation_id)
    );
    const confirmationAfterLatestClose = latestClosedTradeMs == null
      || (numberOrNull(effectiveDowConfirmation?.confirmed_at_ms) != null
        && Number(effectiveDowConfirmation.confirmed_at_ms) > latestClosedTradeMs);
    const confirmationAfterAnchorRetirement = numberOrNull(normalAnchorLifecycle?.last_retired_at_ms) == null
      || (numberOrNull(effectiveDowConfirmation?.confirmed_at_ms) != null
        && Number(effectiveDowConfirmation.confirmed_at_ms) > Number(normalAnchorLifecycle.last_retired_at_ms));
    const anchorLifecycleReady = String(normalAnchorLifecycle?.status || 'NONE') !== 'ACTIVE'
      && confirmationAfterAnchorRetirement;

    const opportunityCreatedNow = numberOrNull(entryOpportunity?.created_at_reference_ms) != null
      && referenceMs != null
      && Number(entryOpportunity.created_at_reference_ms) === Number(referenceMs);
    const confirmationMs = numberOrNull(effectiveDowConfirmation?.confirmed_at_ms);
    const confirmationEventOnCurrentBar = confirmationMs != null
      && referenceMs != null
      && Math.abs(Number(confirmationMs) - Number(referenceMs)) <= 5 * 60 * 1000;
    const staleOpportunityHydratedNow = opportunityCreatedNow && !confirmationEventOnCurrentBar;

    (portfolio?.normal_entry_opportunities || []).forEach(opportunity => {
      if (String(opportunity?.status || '') !== 'WAITING_R2') return;
      const opportunityConfirmedMs = numberOrNull(opportunity?.confirmed_at_ms);
      if (latestClosedTradeMs != null && opportunityConfirmedMs != null && opportunityConfirmedMs <= latestClosedTradeMs) {
        opportunity.status = 'EXPIRED';
        opportunity.terminal_reason_code = 'DOW_CONFIRMATION_NOT_AFTER_PREVIOUS_TRADE_CLOSE';
      }
    });

    const result = {
      rule_lane: RULE_LANE_NORMAL,
      evaluator_id: NORMAL_ENTRY_EVALUATOR_ID,
      action: 'WAIT',
      action_label: '待機',
      status_label: '条件未成立',
      summary: '新しいM5 Dow突破確認Eventを待ちます。確認時点でR2以上なら即Entry、R2未満ならR2初回到達を待ちます。',
      reason_codes: [],
      rule_ids: [],
      permission: normalPermission,
      no_trade: noTrade,
      trigger_aligned: triggerAligned,
      anchor_resolved: anchorResolved,
      anchor_matches_confirmation: anchorMatchesConfirmation,
      confirmation_aligned: confirmationAligned,
      normal_anchor_lifecycle: cloneJsonValue(normalAnchorLifecycle),
      anchor_lifecycle_ready: anchorLifecycleReady,
      confirmation_event_on_current_bar: confirmationEventOnCurrentBar,
      preserving_active_confirmation: preservingActiveConfirmation,
      ignored_same_direction_confirmation_id: preservingActiveConfirmation ? incomingConfirmationId : null,
      effective_dow_confirmation: cloneJsonValue(effectiveDowConfirmation || null),
      effective_entry_anchor: cloneJsonValue(effectiveEntryAnchor || null),
      effective_anchor_price: effectiveAnchorPrice,
      effective_confirmation_side: effectiveConfirmationSide,
      effective_direction: effectiveDirection,
      entry_opportunity: entryOpportunity,
      execution_candidate: null
    };

    const opportunityWaiting = entryOpportunity?.status === 'WAITING_R2';
    const opportunityUsed = entryOpportunity?.status === 'USED';
    const opportunityExpired = entryOpportunity?.status === 'EXPIRED';
    const opportunityMissed = entryOpportunity?.status === 'MISSED';

    if (opportunityExpired && entryOpportunity?.terminal_reason_code === 'NORMAL_DOW_STRUCTURE_BROKEN_BEFORE_ENTRY') {
      result.status_label = 'Entry前Dow構造崩壊';
      result.summary = 'R2 Entry前に確定Dow構造が崩壊したため、旧Dow Confirmation・通常HSI起点・Entry Opportunity・旧R2到達履歴を終了しました。新しいDow Confirmationとprevious SwingからR2を再計算します。';
      result.reason_codes = [
        'NORMAL_DOW_STRUCTURE_BROKEN_BEFORE_ENTRY',
        'DOW_CONFIRMATION_OPPORTUNITY_EXPIRED',
        'NORMAL_HSI_ANCHOR_INVALIDATED_BEFORE_ENTRY',
        'NORMAL_R2_HISTORY_RETIRED_BEFORE_ENTRY'
      ];
      result.rule_ids = ['rule_normal_pre_entry_dow_structure_break_expires_opportunity'];
      result.permission = 'BLOCKED';
      result.no_trade = true;
      return result;
    }

    if (!effectiveDowConfirmation) {
      result.status_label = 'Dow確認待ち';
      result.summary = '通常Entryに使用できるM5 Dow確認Eventがありません。';
      result.reason_codes = ['M5_DOW_CONFIRMATION_EVENT_UNAVAILABLE'];
      result.rule_ids = ['rule_normal_entry_requires_dow_confirmation_event'];
      return result;
    }
    if (opportunityUsed) {
      result.status_label = '新Dow確認待ち';
      result.summary = 'このDow確認Eventの通常Entry機会は使用済みです。同じ確認を次の通常Entryへ再利用しません。';
      result.reason_codes = ['DOW_CONFIRMATION_OPPORTUNITY_ALREADY_USED', 'NEXT_NORMAL_ENTRY_REQUIRES_NEW_DOW_CONFIRMATION_AFTER_PREVIOUS_CLOSE'];
      result.rule_ids = ['rule_normal_entry_one_opportunity_per_dow_confirmation', 'rule_next_normal_entry_requires_new_dow_confirmation_after_previous_close'];
      return result;
    }
    if (!anchorLifecycleReady) {
      if (entryOpportunity && String(entryOpportunity.status || '') === 'WAITING_R2') {
        entryOpportunity.status = 'EXPIRED';
        entryOpportunity.terminal_reason_code = 'NORMAL_HSI_ANCHOR_RETIRED_WAIT_NEW_CONFIRMATION';
      }
      result.status_label = '新Dow確認待ち';
      result.summary = '前TradeのCloseで通常HSI起点は破棄済みです。Close後に成立した新しいM5 Dow Confirmation Eventと、その根拠となる新しいprevious Swingを待ちます。';
      result.reason_codes = ['NORMAL_HSI_ANCHOR_RETIRED_ON_CLOSE', 'NEXT_NORMAL_ENTRY_REQUIRES_NEW_DOW_CONFIRMATION_AFTER_PREVIOUS_CLOSE'];
      result.rule_ids = ['rule_normal_hsi_anchor_retired_immediately_on_close', 'rule_next_normal_entry_requires_new_dow_confirmation_after_previous_close'];
      return result;
    }
    if (opportunityExpired || opportunityMissed) {
      result.status_label = '新Dow確認待ち';
      result.summary = '現在のDow確認Eventは見送り済みまたは期限切れです。次のM5 Dow確認Eventを待ちます。';
      result.reason_codes = [opportunityExpired ? 'DOW_CONFIRMATION_OPPORTUNITY_EXPIRED' : 'NORMAL_ENTRY_OPPORTUNITY_MISSED'];
      result.rule_ids = ['rule_next_normal_entry_requires_new_dow_confirmation_after_previous_close', 'rule_late_entry_after_r2_forbidden'];
      return result;
    }
    if (opportunityWaiting && !effectiveR2Touch?.touched) {
      result.status_label = 'R2到達待ち';
      result.summary = `新しいDow確認Eventを受け付けました。確定時点ではR2未到達のため、HSI起点 ${round3(effectiveAnchorPrice)}からR2 ${round3(effectiveR2Touch?.entry_price)}への初回到達を待ちます。`;
      result.reason_codes = uniqueStrings(['M5_DOW_CONFIRMATION_EVENT_AVAILABLE', 'NORMAL_ENTRY_OPPORTUNITY_WAITING_R2', preservingActiveConfirmation ? 'NORMAL_ACTIVE_CONFIRMATION_PRESERVED_UNTIL_BREAK_OR_ENTRY' : '', hsiNotReachedReasonCode]);
      result.rule_ids = uniqueStrings(['rule_normal_entry_one_opportunity_per_dow_confirmation', preservingActiveConfirmation ? 'rule_normal_active_confirmation_fixed_until_break_entry_or_miss' : '', 'rule_dow_breakout_confirmation_immediate_entry_when_r2_ready', 'rule_normal_entry_first_r2_touch_after_confirmation']);
      return result;
    }
    if (!opportunityWaiting || !effectiveR2Touch?.touched) return result;

    entryOpportunity.first_r2_touch_at = referenceTime;
    entryOpportunity.first_r2_touch_at_ms = referenceMs;
    entryOpportunity.r2_price = effectiveR2Touch.entry_price;
    const entryAtDowConfirmation = opportunityCreatedNow && confirmationEventOnCurrentBar;
    const breakoutThresholdPrice = numberOrNull(effectiveDowConfirmation?.breakout_threshold_price);
    const confirmationRequiredPrice = entryAtDowConfirmation
      ? (effectiveConfirmationSide === 'SHORT'
        ? Math.min(breakoutThresholdPrice != null ? breakoutThresholdPrice : Number(price), Number(effectiveR2Touch.entry_price))
        : Math.max(breakoutThresholdPrice != null ? breakoutThresholdPrice : Number(price), Number(effectiveR2Touch.entry_price)))
      : null;
    const candidateExecutionPrice = entryAtDowConfirmation
      ? (effectiveR2Touch.open != null && (
        (effectiveConfirmationSide === 'SHORT' && Number(effectiveR2Touch.open) < Number(confirmationRequiredPrice))
        || (effectiveConfirmationSide !== 'SHORT' && Number(effectiveR2Touch.open) > Number(confirmationRequiredPrice))
      ) ? Number(effectiveR2Touch.open) : Number(confirmationRequiredPrice))
      : (effectiveR2Touch.passed_before_bar && effectiveR2Touch.open != null ? effectiveR2Touch.open : effectiveR2Touch.entry_price);
    const candidateEntryDistanceRaw = m5ExecutionDistanceRaw(candidateExecutionPrice, effectiveAnchorPrice, effectiveConfirmationSide, policy);
    const candidateEntryBand = m5ExecutionHsiBand(candidateEntryDistanceRaw, policy);
    const candidateTarget = candidateEntryBand?.next || null;
    const candidateTargetPrice = candidateTarget
      ? m5ExecutionTargetPrice(effectiveAnchorPrice, effectiveConfirmationSide, candidateTarget.raw, policy)
      : null;
    result.execution_candidate = {
      entry_at_dow_confirmation: entryAtDowConfirmation,
      breakout_threshold_price: breakoutThresholdPrice,
      confirmation_required_price: confirmationRequiredPrice,
      entry_price: candidateExecutionPrice,
      entry_distance_raw: candidateEntryDistanceRaw,
      entry_band: candidateEntryBand,
      target: candidateTarget,
      target_price: candidateTargetPrice
    };

    if (staleOpportunityHydratedNow) {
      entryOpportunity.status = 'EXPIRED';
      entryOpportunity.terminal_reason_code = 'DOW_CONFIRMATION_PREDATES_SIMULATION_START';
      result.status_label = '表示範囲前のDow確認';
      result.summary = '表示範囲Simulation開始前に成立したDow確認Eventは、新しい通常Entryの切符として使用しません。';
      result.reason_codes = ['DOW_CONFIRMATION_OPPORTUNITY_EXPIRED', 'DOW_CONFIRMATION_PREDATES_SIMULATION_START'];
      result.rule_ids = ['rule_normal_entry_requires_dow_confirmation_event', 'rule_normal_entry_one_opportunity_per_dow_confirmation'];
      return result;
    }
    if (!candidateTarget || candidateTargetPrice == null) {
      entryOpportunity.status = 'MISSED';
      entryOpportunity.terminal_reason_code = 'NEXT_HSI_BOUNDARY_UNAVAILABLE';
      result.status_label = '次HSI境界なし';
      result.summary = 'Entry地点より先に利用可能なHSI境界がないため、通常Entryを見送ります。';
      result.reason_codes = ['NORMAL_ENTRY_OPPORTUNITY_MISSED', 'NEXT_HSI_BOUNDARY_UNAVAILABLE'];
      result.rule_ids = ['rule_normal_entry_target_must_remain_ahead', 'rule_normal_close_next_hsi_boundary'];
      return result;
    }
    if (!confirmationAfterLatestClose) {
      entryOpportunity.status = 'EXPIRED';
      entryOpportunity.terminal_reason_code = 'DOW_CONFIRMATION_NOT_AFTER_PREVIOUS_TRADE_CLOSE';
      result.status_label = '新Dow確認待ち';
      result.summary = 'このDow確認Eventは前Trade終了後に発生していないため、次の通常Entryには使用しません。';
      result.reason_codes = ['NEXT_NORMAL_ENTRY_REQUIRES_NEW_DOW_CONFIRMATION_AFTER_PREVIOUS_CLOSE', 'DOW_CONFIRMATION_NOT_AFTER_PREVIOUS_TRADE_CLOSE'];
      result.rule_ids = ['rule_next_normal_entry_requires_new_dow_confirmation_after_previous_close'];
      return result;
    }
    const entryGuard = m5ExecutionEntryGuardDecision(
      RULE_LANE_NORMAL,
      effectiveConfirmationSide,
      timeframeSnapshot,
      candidateExecutionPrice,
      policy
    );
    const normalStopPlan = m5ExecutionNormalStopPlan(
      candidateExecutionPrice,
      candidateTargetPrice,
      effectiveAnchorPrice,
      effectiveConfirmationSide,
      policy
    );
    result.entry_guard = cloneJsonValue(entryGuard);
    result.normal_stop_plan = cloneJsonValue(normalStopPlan);
    if (entryGuard.blocked) {
      entryOpportunity.status = 'MISSED';
      entryOpportunity.terminal_reason_code = entryGuard.primary_reason_code || 'NORMAL_ENTRY_GUARD_BLOCKED';
      entryOpportunity.entry_guard = cloneJsonValue(entryGuard);
      entryOpportunity.gate_failure = {
        schema_version: 'normal_entry_gate_failure_v0_1',
        trigger_type: entryAtDowConfirmation ? 'DOW_CONFIRMATION_R2_READY' : 'FIRST_R2_TOUCH',
        evaluated_at: referenceTime,
        evaluated_at_ms: referenceMs,
        entry_allowed: false,
        failure_category: 'ENTRY_GUARD',
        primary_failure_code: entryGuard.primary_reason_code || 'NORMAL_ENTRY_GUARD_BLOCKED',
        failed_gates: uniqueStrings(entryGuard.matched_reason_codes || []),
        gate_results: {
          h4_t3_ready: normalFacts?.h4_t3_ready === true,
          h1_t3_ready: normalFacts?.h1_t3_ready === true,
          h4_h1_t3_aligned: normalFacts?.h4_h1_t3_aligned === true,
          m5_dow_aligned: normalFacts?.m5_dow_aligned === true,
          h1_cycle_not_late: normalFacts?.h1_cycle_late !== true,
          entry_direction_ready: normalFacts?.entry_direction_ready === true,
          cycle_guard_passed: normalFacts?.cycle_guard_passed === true,
          anchor_resolved: anchorResolved === true,
          anchor_matches_confirmation: anchorMatchesConfirmation === true,
          confirmation_aligned: confirmationAligned === true,
          anchor_lifecycle_ready: anchorLifecycleReady === true,
          h4_r4_guard_passed: !(entryGuard.matched_reason_codes || []).includes('NORMAL_H4_SAME_DIRECTION_R4_ENTRY_BLOCKED'),
          day_up_h4_down_r5_short_guard_passed: !(entryGuard.matched_reason_codes || []).includes('DAY_UP_H4_DOWN_R5_SHORT_ENTRY_BLOCKED')
        },
        facts: cloneJsonValue({
          direction: effectiveConfirmationSide,
          candidate_price: candidateExecutionPrice,
          dow_confirmation_id: effectiveDowConfirmation?.confirmation_id || null,
          dow_confirmation_time: effectiveDowConfirmation?.confirmed_at || null,
          anchor_id: effectiveEntryAnchor?.anchor_id || effectiveEntryAnchor?.point_id || null,
          anchor_time: effectiveEntryAnchor?.pivot_time || effectiveEntryAnchor?.anchor_time || null,
          anchor_price: effectiveAnchorPrice,
          r2_price: effectiveR2Touch?.entry_price ?? null,
          entry_guard: entryGuard
        })
      };
      result.status_label = 'H4 HSI進行度Guard';
      result.summary = entryGuard.summary || 'H4現在波のHSI進行度Guardにより、新規Normal Entryを見送ります。';
      result.reason_codes = uniqueStrings(['NORMAL_ENTRY_OPPORTUNITY_MISSED', ...(entryGuard.matched_reason_codes || [])]);
      result.rule_ids = uniqueStrings(entryGuard.matched_rule_ids || []);
      result.permission = 'BLOCKED';
      result.no_trade = true;
      return result;
    }
    if (!normalStopPlan.valid) {
      entryOpportunity.status = 'MISSED';
      entryOpportunity.terminal_reason_code = 'NORMAL_CLOSE_MISS_STOP_PLAN_INVALID';
      result.status_label = 'Stop計画不正';
      result.summary = 'Target距離とmax_loss_to_reward_ratioから有効なNormal CloseMiss Stopを確定できないためEntryを見送ります。';
      result.reason_codes = ['NORMAL_ENTRY_OPPORTUNITY_MISSED', 'NORMAL_CLOSE_MISS_STOP_PLAN_INVALID'];
      result.rule_ids = ['rule_normal_close_miss_target_distance_ratio'];
      result.permission = 'BLOCKED';
      result.no_trade = true;
      return result;
    }

    if (!noTrade && triggerAligned && anchorResolved && anchorMatchesConfirmation && confirmationAligned && anchorLifecycleReady && normalPermission === 'ALLOW_SEARCH') {
      result.action = 'ENTRY';
      result.action_label = '通常Entry';
      result.status_label = entryAtDowConfirmation ? 'Dow確定時R2到達済み' : 'R2初回到達';
      result.summary = entryAtDowConfirmation
        ? `Dow確認 ${shortText(effectiveDowConfirmation?.confirmation_id || '-', 18)} の成立時点でR2到達済みのため、Dow突破閾値とR2の双方を満たす最初の価格 ${round3(candidateExecutionPrice)}でEntry。Targetは${candidateTarget?.label || '次HSI境界'}。`
        : `Dow確認 ${shortText(effectiveDowConfirmation?.confirmation_id || '-', 18)} 後、${minEntryLabel} ${round3(effectiveR2Touch.entry_price)}へ初到達したためEntry。Targetは${candidateTarget?.label || '次HSI境界'}。`;
      result.reason_codes = uniqueStrings([
        latestClosedTradeMs != null ? 'NORMAL_ENTRY_NEW_DOW_CONFIRMATION_AFTER_PREVIOUS_CLOSE' : 'NORMAL_ENTRY_FIRST_DOW_CONFIRMATION',
        'M5_DOW_CONFIRMATION_EVENT_AVAILABLE',
        'ONE_ENTRY_PER_DOW_CONFIRMATION',
        entryAtDowConfirmation ? 'R2_ALREADY_REACHED_AT_DOW_CONFIRMATION' : 'HSI_R2_FIRST_TOUCH',
        entryAtDowConfirmation ? 'ENTRY_AT_DOW_BREAKOUT_THRESHOLD_AND_R2' : (effectiveR2Touch.passed_before_bar ? 'ENTRY_AT_FIRST_AVAILABLE_PRICE_AFTER_R2_GAP' : 'ENTRY_AT_R2_BOUNDARY'),
        'H4_T3_DIRECTION_ALLOWED',
        'H1_T3_DIRECTION_ALLOWED',
        'M5_DOW_ALIGNED',
        'H1_CYCLE_NOT_LATE',
        'HSI_ENTRY_ANCHOR_RESOLVED',
        'DOW_CONFIRMATION_HSI_ANCHOR_FIXED',
        preservingActiveConfirmation ? 'NORMAL_ACTIVE_CONFIRMATION_PRESERVED_UNTIL_BREAK_OR_ENTRY' : '',
        latestClosedTradeMs != null ? 'NEW_NORMAL_HSI_ANCHOR_AFTER_PREVIOUS_CLOSE' : 'NORMAL_HSI_ANCHOR_FIRST_ADOPTION',
        'NORMAL_H4_ENTRY_GUARD_PASSED',
        'NORMAL_CLOSE_MISS_TARGET_DISTANCE_RATIO_FIXED'
      ]);
      result.rule_ids = uniqueStrings([
        'rule_normal_entry_v14_h4_h1_t3_direction',
        'rule_normal_entry_v14_m5_dow_breakout_confirmation_trigger',
        'rule_normal_entry_v17_1_h1_cycle_late_guard',
        'rule_normal_entry_one_opportunity_per_dow_confirmation',
        preservingActiveConfirmation ? 'rule_normal_active_confirmation_fixed_until_break_entry_or_miss' : '',
        latestClosedTradeMs != null ? 'rule_next_normal_entry_requires_new_dow_confirmation_after_previous_close' : '',
        entryAtDowConfirmation ? 'rule_dow_breakout_confirmation_immediate_entry_when_r2_ready' : 'rule_normal_entry_first_r2_touch_after_confirmation',
        'rule_normal_entry_target_must_remain_ahead',
        'rule_normal_close_next_hsi_boundary',
        'rule_single_position_single_close',
        'rule_normal_close_miss_target_distance_ratio',
        'rule_normal_hsi_anchor_hard_limit',
        'rule_normal_hsi_anchor_trade_scoped_until_close'
      ]);
      entryOpportunity.status = 'USED';
      entryOpportunity.entry_execution_mode = entryAtDowConfirmation
        ? 'DOW_BREAKOUT_CONFIRMATION_R2_READY'
        : (effectiveR2Touch.passed_before_bar ? 'FIRST_AVAILABLE_PRICE_AFTER_R2_GAP' : 'FIRST_R2_TOUCH_AFTER_CONFIRMATION');
      entryOpportunity.entry_execution_price = candidateExecutionPrice;
      entryOpportunity.preserved_over_same_direction_confirmation = preservingActiveConfirmation;
      entryOpportunity.ignored_same_direction_confirmation_id = preservingActiveConfirmation ? incomingConfirmationId : null;
      entryOpportunity.breakout_threshold_price = breakoutThresholdPrice;
      entryOpportunity.confirmation_required_price = confirmationRequiredPrice;
      entryOpportunity.entry_distance_raw = candidateEntryDistanceRaw;
      entryOpportunity.entry_band_label = candidateEntryBand?.current?.label || null;
      entryOpportunity.target_label = candidateTarget?.label || null;
      entryOpportunity.target_raw = candidateTarget?.raw ?? null;
      entryOpportunity.target_price = candidateTargetPrice;
      entryOpportunity.entry_guard = cloneJsonValue(entryGuard);
      entryOpportunity.normal_stop_plan = cloneJsonValue(normalStopPlan);
      result.execution_candidate.entry_guard = cloneJsonValue(entryGuard);
      result.execution_candidate.normal_stop_plan = cloneJsonValue(normalStopPlan);
      result.execution_candidate.stop_price = normalStopPlan.stop_price;
      entryOpportunity.terminal_reason_code = entryAtDowConfirmation
        ? 'ENTRY_EXECUTED_AT_DOW_BREAKOUT_CONFIRMATION_WITH_R2_READY'
        : 'ENTRY_EXECUTED_AT_R2';
      portfolio.used_dow_confirmation_ids = uniqueStrings([
        ...(portfolio.used_dow_confirmation_ids || []),
        effectiveDowConfirmation.confirmation_id
      ]);
      return result;
    }

    entryOpportunity.status = 'MISSED';
    entryOpportunity.terminal_reason_code = entryAtDowConfirmation
      ? 'DOW_CONFIRMATION_R2_READY_ENTRY_GATES_NOT_READY'
      : 'R2_FIRST_TOUCH_ENTRY_GATES_NOT_READY';
    const failedEntryGates = uniqueStrings([
      !normalFacts?.h4_t3_ready ? 'H4_T3_NOT_READY' : '',
      !normalFacts?.h1_t3_ready ? 'H1_T3_NOT_READY' : '',
      !normalFacts?.h4_h1_t3_aligned ? 'H4_H1_T3_NOT_ALIGNED' : '',
      !normalFacts?.m5_dow_aligned ? 'M5_DOW_NOT_ALIGNED' : '',
      normalFacts?.h1_cycle_late ? 'H1_CYCLE_LATE_ENTRY_BLOCKED' : '',
      !normalFacts?.entry_direction_ready ? 'ENTRY_DIRECTION_NOT_READY' : '',
      !normalFacts?.cycle_guard_passed ? 'CYCLE_GUARD_NOT_PASSED' : '',
      noTrade ? 'NORMAL_NO_TRADE' : '',
      !triggerAligned ? 'TRIGGER_NOT_ALIGNED' : '',
      !anchorResolved ? 'HSI_ENTRY_ANCHOR_UNRESOLVED' : '',
      !anchorMatchesConfirmation ? 'HSI_ANCHOR_CONFIRMATION_MISMATCH' : '',
      !confirmationAligned ? 'DOW_CONFIRMATION_DIRECTION_MISMATCH' : '',
      !anchorLifecycleReady ? 'NORMAL_HSI_ANCHOR_LIFECYCLE_NOT_READY' : '',
      normalPermission !== 'ALLOW_SEARCH' ? 'NORMAL_PERMISSION_NOT_ALLOW_SEARCH' : ''
    ]);
    entryOpportunity.gate_failure = {
      schema_version: 'normal_entry_gate_failure_v0_1',
      trigger_type: entryAtDowConfirmation ? 'DOW_CONFIRMATION_R2_READY' : 'FIRST_R2_TOUCH',
      evaluated_at: referenceTime,
      evaluated_at_ms: referenceMs,
      entry_allowed: false,
      failure_category: 'ENTRY_GATES_NOT_READY',
      primary_failure_code: failedEntryGates[0] || entryOpportunity.terminal_reason_code,
      failed_gates: failedEntryGates,
      gate_results: {
        h4_t3_ready: normalFacts?.h4_t3_ready === true,
        h1_t3_ready: normalFacts?.h1_t3_ready === true,
        h4_h1_t3_aligned: normalFacts?.h4_h1_t3_aligned === true,
        m5_dow_aligned: normalFacts?.m5_dow_aligned === true,
        h1_cycle_not_late: normalFacts?.h1_cycle_late !== true,
        entry_direction_ready: normalFacts?.entry_direction_ready === true,
        cycle_guard_passed: normalFacts?.cycle_guard_passed === true,
        no_trade_clear: noTrade !== true,
        trigger_aligned: triggerAligned === true,
        anchor_resolved: anchorResolved === true,
        anchor_matches_confirmation: anchorMatchesConfirmation === true,
        confirmation_aligned: confirmationAligned === true,
        anchor_lifecycle_ready: anchorLifecycleReady === true,
        permission_allow_search: normalPermission === 'ALLOW_SEARCH'
      },
      facts: cloneJsonValue({
        direction: effectiveConfirmationSide,
        candidate_price: candidateExecutionPrice,
        dow_confirmation_id: effectiveDowConfirmation?.confirmation_id || null,
        dow_confirmation_time: effectiveDowConfirmation?.confirmed_at || null,
        anchor_id: effectiveEntryAnchor?.anchor_id || effectiveEntryAnchor?.point_id || null,
        anchor_time: effectiveEntryAnchor?.pivot_time || effectiveEntryAnchor?.anchor_time || null,
        anchor_price: effectiveAnchorPrice,
        r2_price: effectiveR2Touch?.entry_price ?? null,
        normal_facts: normalFacts
      })
    };
    result.status_label = entryAtDowConfirmation ? 'Dow確定時に条件不足' : 'R2初回到達時に条件不足';
    result.summary = entryAtDowConfirmation
      ? 'Dow確認時点でR2へ到達済みでしたが、通常ルールの方向・H1 Cycle・起点整合条件がそろわなかったため、このDow確認EventではEntryしません。'
      : 'R2初回到達時点で通常ルールの方向・H1 Cycle・起点整合条件がそろわなかったため、このDow確認Eventでは後からEntryしません。';
    result.reason_codes = uniqueStrings([
      'NORMAL_ENTRY_OPPORTUNITY_MISSED',
      entryAtDowConfirmation ? 'DOW_CONFIRMATION_R2_READY_ENTRY_GATES_NOT_READY' : 'R2_FIRST_TOUCH_ENTRY_GATES_NOT_READY',
      !normalFacts?.h4_t3_ready ? 'H4_T3_NOT_READY' : '',
      !normalFacts?.h1_t3_ready ? 'H1_T3_NOT_READY' : '',
      !normalFacts?.h4_h1_t3_aligned ? 'H4_H1_T3_NOT_ALIGNED' : '',
      !normalFacts?.m5_dow_aligned ? 'M5_DOW_NOT_ALIGNED' : '',
      normalFacts?.h1_cycle_late ? 'H1_CYCLE_LATE_ENTRY_BLOCKED' : '',
      !anchorResolved ? 'HSI_ENTRY_ANCHOR_UNRESOLVED' : '',
      !anchorMatchesConfirmation ? 'HSI_ANCHOR_CONFIRMATION_MISMATCH' : '',
      !confirmationAligned ? 'DOW_CONFIRMATION_DIRECTION_MISMATCH' : '',
      !anchorLifecycleReady ? 'NORMAL_HSI_ANCHOR_LIFECYCLE_NOT_READY' : ''
    ]);
    result.rule_ids = [entryAtDowConfirmation ? 'rule_dow_breakout_confirmation_immediate_entry_when_r2_ready' : 'rule_normal_entry_first_r2_touch_after_confirmation', 'rule_normal_entry_missed_not_late_entry'];
    return result;
  }

  function normalRuleLaneCloseDecision(input) {
    const activePosition = input?.activePosition || null;
    const activeTrade = input?.activeTrade || null;
    const currentBar = input?.currentBar || {};
    const m5State = input?.m5State || {};
    if (!activePosition) {
      return {
        rule_lane: RULE_LANE_NORMAL,
        evaluator_id: NORMAL_CLOSE_EVALUATOR_ID,
        action: 'NOT_APPLICABLE',
        action_label: '対象なし',
        status_label: '通常建玉なし',
        summary: '通常Close判定の対象建玉がありません。',
        reason_codes: [],
        rule_ids: [],
        bar_touch: { stop_touched: false, target_touched: false, ambiguous: false }
      };
    }
    const barTouch = m5ExecutionBarTouch(activePosition, currentBar);
    if (barTouch.ambiguous) {
      return {
        rule_lane: RULE_LANE_NORMAL,
        evaluator_id: NORMAL_CLOSE_EVALUATOR_ID,
        action: 'STOP_CLOSE',
        action_label: '損切り決済',
        status_label: '同一足でStop/Target両到達',
        summary: '通常ルールの同一M5足でStopとTargetの両方へ到達したため、保守的にEntry時固定の倍率Stopを先に適用します。',
        reason_codes: uniqueStrings(['AMBIGUOUS_STOP_TARGET', 'STOP_CLOSE_TARGET_DISTANCE_RATIO', activePosition?.close_miss_plan?.hsi_anchor_hard_limit_applied ? 'STOP_CLOSE_HSI_ANCHOR_HARD_LIMIT' : '']),
        rule_ids: uniqueStrings(['rule_single_close_ambiguous_stop_first', 'rule_normal_close_miss_target_distance_ratio', activePosition?.close_miss_plan?.hsi_anchor_hard_limit_applied ? 'rule_normal_hsi_anchor_hard_limit' : '']),
        bar_touch: barTouch
      };
    }
    if (barTouch.stop_touched) {
      return {
        rule_lane: RULE_LANE_NORMAL,
        evaluator_id: NORMAL_CLOSE_EVALUATOR_ID,
        action: 'STOP_CLOSE',
        action_label: '損切り決済',
        status_label: '倍率Stop到達',
        summary: `Entry時にTarget距離とmax_loss_to_reward_ratioから固定したStop ${round3(barTouch.stop_price)}へ到達したため全決済します。`,
        reason_codes: uniqueStrings(['STOP_CLOSE_TARGET_DISTANCE_RATIO', activePosition?.close_miss_plan?.hsi_anchor_hard_limit_applied ? 'STOP_CLOSE_HSI_ANCHOR_HARD_LIMIT' : '']),
        rule_ids: uniqueStrings(['rule_normal_close_miss_target_distance_ratio', activePosition?.close_miss_plan?.hsi_anchor_hard_limit_applied ? 'rule_normal_hsi_anchor_hard_limit' : '', 'rule_single_position_single_close']),
        bar_touch: barTouch
      };
    }
    if (barTouch.target_touched) {
      return {
        rule_lane: RULE_LANE_NORMAL,
        evaluator_id: NORMAL_CLOSE_EVALUATOR_ID,
        action: 'FULL_CLOSE',
        action_label: '全決済',
        status_label: `${activePosition?.target_plan?.next_target_label || '次HSI境界'}到達`,
        summary: `${activePosition?.target_plan?.next_target_label || '次HSI境界'}へ到達したため通常建玉を全決済します。`,
        reason_codes: ['CLOSE_OK_NEXT_HSI_BOUNDARY', 'SINGLE_CLOSE_ALL_UNITS'],
        rule_ids: ['rule_normal_close_next_hsi_boundary', 'rule_single_position_single_close'],
        bar_touch: barTouch
      };
    }
    const postEntryBreak = m5ExecutionNormalDowStructureBreak(m5State);
    const entryMs = numberOrNull(activePosition?.entry_ms ?? activeTrade?.entry_ms);
    const observedBreakIds = Array.isArray(activeTrade?.post_entry_dow_break_observation_ids)
      ? activeTrade.post_entry_dow_break_observation_ids.map(value => String(value)) : [];
    const postEntryBreakObserved = Boolean(
      postEntryBreak
      && entryMs != null
      && Number(postEntryBreak.break_at_ms) > Number(entryMs)
      && !observedBreakIds.includes(String(postEntryBreak.break_event_id || postEntryBreak.break_at_ms))
    );
    if (postEntryBreakObserved) {
      return {
        rule_lane: RULE_LANE_NORMAL,
        evaluator_id: NORMAL_CLOSE_EVALUATOR_ID,
        action: 'WAIT',
        action_label: '保有継続',
        status_label: 'Entry後Dow崩壊を観測・Closeなし',
        summary: 'R2 Entry後にM5 Dow構造崩壊を観測しましたが、NORMALではDow崩壊単独をClose条件にしません。Entry時のHSI起点・Target・Stopを固定したまま保有を継続します。',
        reason_codes: ['NORMAL_POST_ENTRY_DOW_BREAKDOWN_OBSERVED_NO_CLOSE', 'POSITION_ALREADY_OPEN'],
        rule_ids: ['rule_normal_post_entry_dow_break_observe_only_no_close', 'rule_normal_hsi_anchor_trade_scoped_until_close', 'rule_single_position_single_close'],
        bar_touch: barTouch,
        post_entry_dow_break_observation: { ...cloneJsonValue(postEntryBreak), close_event_emitted: false, position_action: 'HOLD' }
      };
    }
    return {
      rule_lane: RULE_LANE_NORMAL,
      evaluator_id: NORMAL_CLOSE_EVALUATOR_ID,
      action: 'WAIT',
      action_label: '保有継続',
      status_label: '通常Close条件未到達',
      summary: '通常建玉はEntry時にTarget距離とmax_loss_to_reward_ratioから固定したStop、またはTargetへ到達するまで保有します。Entry後のDow崩壊だけでは自動Closeせず、通常Add-onも行いません。',
      reason_codes: ['NORMAL_ADD_ON_DISABLED', 'POSITION_ALREADY_OPEN'],
      rule_ids: ['rule_normal_add_on_forbidden', 'rule_single_position_single_close'],
      bar_touch: barTouch
    };
  }

  function expansionRuleLaneEntryDecision(input) {
    const permission = String(input?.upperDecision?.entry_policy?.expansion_entry?.status || 'NOT_EVALUATED').toUpperCase();
    return {
      rule_lane: RULE_LANE_EXPANSION,
      evaluator_id: EXPANSION_ENTRY_EVALUATOR_ID,
      action: 'WAIT',
      action_label: 'Expansion待機',
      status_label: '未実装',
      summary: 'Expansion EntryはNormal Rule Laneと分離されています。確定条件が未実装のため建玉を作りません。',
      reason_codes: ['EXPANSION_CONFIRMATION_NOT_IMPLEMENTED'],
      rule_ids: ['rule_expansion_entry_requires_explicit_confirmation'],
      permission,
      entry_opportunity: null
    };
  }

  function expansionLiteRuleLaneEntryDecision(input) {
    const {
      portfolio,
      referenceMs,
      referenceTime,
      price,
      currentBar,
      expansionLiteFacts,
      dowConfirmation,
      entryResolution,
      entryAnchor,
      anchorPrice,
      distanceRaw,
      r3Touch,
      policy,
      timeframeSnapshot
    } = input || {};
    const direction = String(expansionLiteFacts?.confirmation_side || '').toUpperCase();
    const confirmationDirection = String(dowConfirmation?.direction || '').toUpperCase();
    const confirmationAligned = (direction === 'LONG' && confirmationDirection === 'UP')
      || (direction === 'SHORT' && confirmationDirection === 'DOWN');
    const anchorResolved = entryResolution?.status === 'RESOLVED_REFERENCE' && anchorPrice != null;
    const opportunity = m5ExecutionExpansionLiteOpportunity(portfolio, dowConfirmation, entryResolution, referenceMs, referenceTime);
    const confirmationMs = numberOrNull(dowConfirmation?.confirmed_at_ms);
    const confirmationEventOnCurrentBar = confirmationMs != null && referenceMs != null
      && Math.abs(Number(confirmationMs) - Number(referenceMs)) <= 5 * 60 * 1000;
    const opportunityCreatedNow = numberOrNull(opportunity?.created_at_reference_ms) != null
      && referenceMs != null && Number(opportunity.created_at_reference_ms) === Number(referenceMs);
    const r3ReachedByState = Number(distanceRaw) >= Number(r3Touch?.raw ?? 144) - 1e-6;
    const r3Ready = r3Touch?.touched === true || r3ReachedByState;
    const result = {
      rule_lane: RULE_LANE_EXPANSION_LITE,
      evaluator_id: EXPANSION_LITE_ENTRY_EVALUATOR_ID,
      action: 'WAIT',
      action_label: 'Expansion-Lite待機',
      status_label: '条件未成立',
      summary: 'Expansion-LiteはH4/H1のT3側、H1 Cycle Entry Window内、M5 Dow確認、R3タッチを独立評価します。',
      reason_codes: [],
      rule_ids: [],
      permission: 'BLOCKED',
      no_trade: true,
      trigger_aligned: expansionLiteFacts?.entry_direction_ready === true,
      anchor_resolved: anchorResolved,
      confirmation_aligned: confirmationAligned,
      confirmation_event_on_current_bar: confirmationEventOnCurrentBar,
      entry_opportunity: opportunity,
      execution_candidate: null
    };
    if (!dowConfirmation) {
      result.status_label = 'M5 Dow確認待ち';
      result.summary = 'Expansion-Lite用のM5 Dow Confirmation Eventを待ちます。';
      result.reason_codes = ['EXPANSION_LITE_M5_DOW_CONFIRMATION_UNAVAILABLE'];
      result.rule_ids = ['rule_expansion_lite_requires_m5_dow_confirmation'];
      return result;
    }
    if (!anchorResolved) {
      result.status_label = 'Dow HSI起点待ち';
      result.summary = 'M5 Dow Confirmationに紐づくExpansion-Lite専用HSI起点を解決できません。';
      result.reason_codes = ['EXPANSION_LITE_DOW_ANCHOR_UNRESOLVED'];
      result.rule_ids = ['rule_expansion_lite_uses_confirmation_adopted_hsi_anchor'];
      return result;
    }
    if (['USED', 'MISSED', 'EXPIRED'].includes(String(opportunity?.status || ''))) {
      result.status_label = '新M5 Dow確認待ち';
      result.summary = 'このM5 Dow Confirmation EventのExpansion-Lite Entry機会は終了済みです。';
      result.reason_codes = [`EXPANSION_LITE_OPPORTUNITY_${String(opportunity.status).toUpperCase()}`];
      result.rule_ids = ['rule_expansion_lite_one_entry_per_dow_confirmation'];
      return result;
    }
    if (opportunityCreatedNow && !confirmationEventOnCurrentBar && r3ReachedByState) {
      opportunity.status = 'EXPIRED';
      opportunity.terminal_reason_code = 'VISIBLE_RANGE_STARTED_AFTER_R3_REACHED';
      result.status_label = '表示範囲前にR3到達済み';
      result.summary = '表示範囲開始時点ですでにR3以上のため、過去のタッチを遡ってEntryしません。';
      result.reason_codes = ['EXPANSION_LITE_STALE_CONFIRMATION_R3_STATE_UNKNOWN'];
      result.rule_ids = ['rule_expansion_lite_no_backdated_entry'];
      return result;
    }
    const t3Aligned = direction === 'LONG'
      ? expansionLiteFacts?.h4_t3_side_long && expansionLiteFacts?.h1_t3_side_long
      : direction === 'SHORT'
        ? expansionLiteFacts?.h4_t3_side_short && expansionLiteFacts?.h1_t3_side_short
        : false;
    const h1CycleEntryAllowed = expansionLiteFacts?.h1_cycle_entry_allowed === true
      || (expansionLiteFacts?.h1_cycle_entry_allowed == null && expansionLiteFacts?.h1_cycle_front_half === true);
    const gateReady = confirmationAligned
      && t3Aligned
      && h1CycleEntryAllowed
      && expansionLiteFacts?.entry_direction_ready === true;
    if (!r3Ready) {
      result.permission = gateReady ? 'ALLOW_SEARCH' : 'BLOCKED';
      result.no_trade = !gateReady;
      result.status_label = gateReady ? 'R3タッチ待ち' : 'Entry前提待ち';
      result.summary = gateReady
        ? `M5 Dow確認と上位前提が成立済みです。起点 ${round3(anchorPrice)}から${r3Touch?.label || 'R3'} ${round3(r3Touch?.price)}への初回タッチを待ちます。`
        : 'H4/H1 CloseのT3側、H1 Cycle Entry Window内、M5 Dow方向のいずれかが未成立です。';
      result.reason_codes = uniqueStrings([
        gateReady ? 'EXPANSION_LITE_WAITING_R3_TOUCH' : 'EXPANSION_LITE_ENTRY_GATE_NOT_READY',
        !t3Aligned ? 'EXPANSION_LITE_H4_H1_T3_SIDE_NOT_ALIGNED' : '',
        !h1CycleEntryAllowed ? 'EXPANSION_LITE_H1_CYCLE_ENTRY_WINDOW_EXCEEDED' : '',
        !confirmationAligned ? 'EXPANSION_LITE_DOW_DIRECTION_MISMATCH' : ''
      ]);
      result.rule_ids = ['rule_expansion_lite_entry_r3_touch', 'rule_expansion_lite_h1_cycle_entry_window'];
      return result;
    }
    opportunity.first_r3_touch_at = referenceTime;
    opportunity.first_r3_touch_at_ms = referenceMs;
    opportunity.r3_price = r3Touch?.price;
    if (!gateReady) {
      opportunity.status = 'MISSED';
      opportunity.terminal_reason_code = 'R3_TOUCH_ENTRY_GATES_NOT_READY';
      result.status_label = 'R3タッチ時に条件不足';
      result.summary = 'R3タッチ時点でExpansion-Lite固有のT3/Cycle/Dow条件がそろわなかったため、このDow確認EventではEntryしません。';
      result.reason_codes = uniqueStrings([
        'EXPANSION_LITE_ENTRY_OPPORTUNITY_MISSED',
        !t3Aligned ? 'EXPANSION_LITE_H4_H1_T3_SIDE_NOT_ALIGNED' : '',
        !h1CycleEntryAllowed ? 'EXPANSION_LITE_H1_CYCLE_ENTRY_WINDOW_EXCEEDED' : '',
        !confirmationAligned ? 'EXPANSION_LITE_DOW_DIRECTION_MISMATCH' : ''
      ]);
      result.rule_ids = ['rule_expansion_lite_r3_touch_gate_terminal'];
      return result;
    }
    const breakoutThreshold = numberOrNull(dowConfirmation?.breakout_threshold_price);
    const requiredPrice = confirmationEventOnCurrentBar
      ? (direction === 'SHORT'
        ? Math.min(breakoutThreshold != null ? breakoutThreshold : r3Touch.price, r3Touch.price)
        : Math.max(breakoutThreshold != null ? breakoutThreshold : r3Touch.price, r3Touch.price))
      : r3Touch.price;
    const open = numberOrNull(currentBar?.open);
    const executionPrice = direction === 'SHORT'
      ? (open != null && requiredPrice != null && open <= requiredPrice ? open : requiredPrice)
      : (open != null && requiredPrice != null && open >= requiredPrice ? open : requiredPrice);
    const targetRaw = Number(policy?.expansion_lite_policy?.target_raw ?? 377);
    const targetPrice = m5ExecutionTargetPrice(anchorPrice, direction, targetRaw, policy);
    if (!m5ExecutionTargetDirectionValid(direction, executionPrice, targetPrice)) {
      opportunity.status = 'MISSED';
      opportunity.terminal_reason_code = 'TARGET_NOT_BEYOND_ENTRY';
      opportunity.entry_execution_price = executionPrice;
      opportunity.target_price = targetPrice;
      result.status_label = 'Target方向不正';
      result.summary = `Expansion-Lite Entry候補 ${round3(executionPrice)} に対し、R5 Target ${round3(targetPrice)} が利益方向に存在しないためEntryを拒否します。`;
      result.reason_codes = ['EXPANSION_LITE_TARGET_NOT_BEYOND_ENTRY'];
      result.rule_ids = ['rule_expansion_lite_target_must_be_beyond_entry'];
      result.execution_validation_errors = [`${direction} Entry ${round3(executionPrice)} / Target ${round3(targetPrice)}`];
      return result;
    }
    const entryGuard = m5ExecutionEntryGuardDecision(
      RULE_LANE_EXPANSION_LITE,
      direction,
      timeframeSnapshot,
      executionPrice,
      policy
    );
    result.entry_guard = cloneJsonValue(entryGuard);
    if (entryGuard.blocked) {
      opportunity.status = 'MISSED';
      opportunity.terminal_reason_code = entryGuard.primary_reason_code || 'EXPANSION_LITE_ENTRY_GUARD_BLOCKED';
      opportunity.entry_guard = cloneJsonValue(entryGuard);
      result.status_label = '上位足HSI進行度Guard';
      result.summary = entryGuard.summary || '上位足・HSI進行度GuardによりExpansion-Lite Entryを見送ります。';
      result.reason_codes = uniqueStrings(['EXPANSION_LITE_ENTRY_OPPORTUNITY_MISSED', ...(entryGuard.matched_reason_codes || [])]);
      result.rule_ids = uniqueStrings(entryGuard.matched_rule_ids || []);
      result.permission = 'BLOCKED';
      result.no_trade = true;
      return result;
    }
    opportunity.status = 'USED';
    opportunity.entry_execution_price = executionPrice;
    opportunity.entry_execution_mode = confirmationEventOnCurrentBar
      ? 'DOW_CONFIRMATION_R3_READY'
      : 'FIRST_R3_TOUCH_AFTER_DOW_CONFIRMATION';
    opportunity.terminal_reason_code = confirmationEventOnCurrentBar
      ? 'ENTRY_AT_DOW_CONFIRMATION_WITH_R3_READY'
      : 'ENTRY_AT_FIRST_R3_TOUCH';
    portfolio.used_expansion_lite_confirmation_ids = uniqueStrings([
      ...(portfolio.used_expansion_lite_confirmation_ids || []),
      dowConfirmation.confirmation_id
    ]);
    result.action = 'ENTRY';
    result.action_label = 'Expansion-Lite Entry';
    result.status_label = confirmationEventOnCurrentBar ? 'Dow確定時R3到達済み' : 'R3初回タッチ';
    result.summary = confirmationEventOnCurrentBar
      ? `M5 Dow確認時点でR3条件も成立したため、Expansion-Lite Entryを ${round3(executionPrice)}で実行します。`
      : `M5 Dow確認後にR3へ初回タッチしたため、Expansion-Lite Entryを ${round3(executionPrice)}で実行します。`;
    result.reason_codes = uniqueStrings([
      'EXPANSION_LITE_ENTRY_EXECUTED',
      'EXPANSION_LITE_H4_H1_T3_SIDE_ALIGNED',
      'EXPANSION_LITE_H1_CYCLE_ENTRY_WINDOW_OK',
      confirmationEventOnCurrentBar ? 'EXPANSION_LITE_R3_READY_AT_DOW_CONFIRMATION' : 'EXPANSION_LITE_FIRST_R3_TOUCH_AFTER_DOW_CONFIRMATION'
    ]);
    result.rule_ids = [
      'rule_expansion_lite_entry_independent_lane',
      'rule_expansion_lite_entry_r3_touch',
      'rule_expansion_lite_h1_cycle_entry_window',
      'rule_expansion_lite_day_cycle_not_used'
    ];
    result.permission = 'ALLOW_ENTRY';
    result.no_trade = false;
    result.execution_candidate = {
      price: executionPrice,
      entry_level: 'R3',
      entry_raw: 144,
      anchor_id: entryResolution?.anchor_id || null,
      anchor_price: anchorPrice,
      target_price: targetPrice,
      target_raw: targetRaw,
      direction
    };
    return result;
  }

  function expansionRuleLaneCloseDecision(input) {
    const activePosition = input?.activePosition || null;
    const barTouch = activePosition ? m5ExecutionBarTouch(activePosition, input?.currentBar || {}) : { stop_touched: false, target_touched: false, ambiguous: false };
    return {
      rule_lane: RULE_LANE_EXPANSION,
      evaluator_id: EXPANSION_CLOSE_EVALUATOR_ID,
      action: 'WAIT',
      action_label: 'Expansion保有監視',
      status_label: 'Close未実装',
      summary: 'Expansion Close PolicyはNormal Close Evaluatorと分離されています。現時点では未実装です。',
      reason_codes: ['EXPANSION_CLOSE_POLICY_NOT_IMPLEMENTED'],
      rule_ids: [],
      bar_touch: barTouch
    };
  }

  function expansionLiteRuleLaneCloseDecision(input) {
    const activePosition = input?.activePosition || null;
    const activeTrade = input?.activeTrade || null;
    const currentBar = input?.currentBar || {};
    const m5State = input?.m5State || {};
    const policy = input?.policy || {};
    if (!activePosition || !activeTrade) {
      return {
        rule_lane: RULE_LANE_EXPANSION_LITE,
        evaluator_id: EXPANSION_LITE_CLOSE_EVALUATOR_ID,
        action: 'NOT_APPLICABLE',
        action_label: '対象なし',
        status_label: 'Expansion-Lite建玉なし',
        summary: 'Expansion-Lite管理対象の建玉がありません。',
        reason_codes: [],
        rule_ids: [],
        bar_touch: { stop_touched: false, target_touched: false, ambiguous: false }
      };
    }
    const direction = String(activeTrade.side || activePosition.side || '').toUpperCase();
    const high = numberOrNull(currentBar.high);
    const low = numberOrNull(currentBar.low);
    const close = numberOrNull(currentBar.close);
    const t3 = numberOrNull(currentBar.t3_20_0_2);
    const anchorPrice = numberOrNull(activeTrade.entry_anchor_price ?? activePosition.entry_anchor_price);
    const targetPrice = numberOrNull(activeTrade.target_price)
      ?? m5ExecutionTargetPrice(anchorPrice, direction, Number(policy?.expansion_lite_policy?.target_raw ?? 377), policy);
    const anchorFill = m5ExecutionBarFill(direction, currentBar, anchorPrice, 'STOP');
    const t3Fill = m5ExecutionBarFill(direction, currentBar, t3, 'STOP');
    const targetDirectionValid = m5ExecutionTargetDirectionValid(direction, activeTrade?.entry_price ?? activePosition?.entry_price, targetPrice);
    const targetFill = targetDirectionValid
      ? m5ExecutionBarFill(direction, currentBar, targetPrice, 'TARGET')
      : { touched: false, execution_price: null, fill_mode: 'TARGET_DIRECTION_INVALID', within_bar: false };
    const anchorTouched = anchorFill.touched;
    const t3Touched = t3Fill.touched;
    const targetTouched = targetFill.touched;
    const structural = m5ExecutionExpansionLiteStructuralBreak(activeTrade, m5State);
    const baseTouch = {
      high, low, close,
      stop_price: anchorPrice,
      target_price: targetPrice,
      t3_price: t3,
      stop_execution_price: anchorFill.execution_price,
      target_execution_price: targetFill.execution_price,
      t3_execution_price: t3Fill.execution_price,
      stop_fill_mode: anchorFill.fill_mode,
      target_fill_mode: targetFill.fill_mode,
      t3_fill_mode: t3Fill.fill_mode,
      target_direction_valid: targetDirectionValid,
      stop_touched: anchorTouched,
      target_touched: targetTouched,
      t3_touched: t3Touched,
      structural_broken: structural.broken,
      ambiguous: [anchorTouched, t3Touched, structural.broken, targetTouched].filter(Boolean).length > 1
    };
    function exitDecision(exitType, executionPrice, label, summary, reasonCode, ruleId) {
      return {
        rule_lane: RULE_LANE_EXPANSION_LITE,
        evaluator_id: EXPANSION_LITE_CLOSE_EVALUATOR_ID,
        action: 'FULL_CLOSE',
        action_label: label,
        status_label: label,
        summary,
        reason_codes: [reasonCode, 'EXPANSION_LITE_ALL_POSITIONS_CLOSE'],
        rule_ids: [ruleId, 'rule_expansion_lite_close_all_positions'],
        exit_type: exitType,
        exit_reason_code: reasonCode,
        execution_price: executionPrice,
        bar_touch: baseTouch
      };
    }
    if (anchorTouched) {
      return exitDecision('ANCHOR_EXIT', anchorFill.execution_price, 'Anchor Exit', `M5 ${direction === 'LONG' ? '安値' : '高値'}が採用HSI起点 ${round3(anchorPrice)}を逆抜けたため全建玉Closeします。`, 'EXPANSION_LITE_ANCHOR_EXIT', 'rule_expansion_lite_anchor_exit_touch');
    }
    if (t3Touched) {
      return exitDecision('T3_EXIT', t3Fill.execution_price, 'T3 Exit', `M5 ${direction === 'LONG' ? '安値' : '高値'}がM5 T3 ${round3(t3)}を逆抜けたため全建玉Closeします。`, 'EXPANSION_LITE_T3_EXIT', 'rule_expansion_lite_t3_exit_touch');
    }
    if (structural.broken) {
      return exitDecision('STRUCTURAL_EXIT', close, 'Structural Exit', `新しいM5 Dow点の確定により${direction === 'LONG' ? '上昇' : '下降'}構造が破綻したため、M5終値 ${round3(close)}で全建玉Closeします。`, 'EXPANSION_LITE_STRUCTURAL_EXIT', 'rule_expansion_lite_m5_dow_structure_break_exit');
    }
    if (targetTouched) {
      return exitDecision('TARGET_EXIT', targetFill.execution_price, 'R5 Exit', `採用HSI起点からR5 ${round3(targetPrice)}へタッチしたため全建玉Closeします。`, 'EXPANSION_LITE_R5_TARGET_EXIT', 'rule_expansion_lite_r5_target_exit');
    }
    const addOnDefs = Array.isArray(policy?.expansion_lite_policy?.add_on_levels)
      ? policy.expansion_lite_policy.add_on_levels
      : [{ raw: 188, label: 'R3.5' }, { raw: 233, label: 'R4' }, { raw: 305, label: 'R4.5' }];
    const consumed = new Set((activeTrade.consumed_add_on_levels || []).map(value => String(value).toUpperCase()));
    const newLevels = addOnDefs
      .map(item => m5ExecutionLevelTouch(currentBar, anchorPrice, direction, item.raw, item.label, policy))
      .filter(item => item.touched && !consumed.has(String(item.label).toUpperCase()));
    if (newLevels.length) {
      return {
        rule_lane: RULE_LANE_EXPANSION_LITE,
        evaluator_id: EXPANSION_LITE_CLOSE_EVALUATOR_ID,
        action: 'ADD_ON',
        action_label: 'Expansion-Lite Add-on',
        status_label: `${newLevels.map(item => item.label).join(' / ')}タッチ`,
        summary: `${newLevels.map(item => item.label).join(' / ')}へタッチしたため、各境界で1回だけExpansion-Lite Add-onします。`,
        reason_codes: ['EXPANSION_LITE_ADD_ON_LEVEL_TOUCHED'],
        rule_ids: ['rule_expansion_lite_add_on_r35_r4_r45_once'],
        add_on_levels: newLevels,
        bar_touch: baseTouch
      };
    }
    return {
      rule_lane: RULE_LANE_EXPANSION_LITE,
      evaluator_id: EXPANSION_LITE_CLOSE_EVALUATOR_ID,
      action: 'WAIT',
      action_label: 'Expansion-Lite保有継続',
      status_label: 'Exit / Add-on条件未到達',
      summary: 'R5 / M5 T3 / M5 Dow構造 / 採用HSI起点のExit条件と、未使用Add-on境界を監視します。',
      reason_codes: ['EXPANSION_LITE_POSITION_HOLD'],
      rule_ids: ['rule_expansion_lite_independent_position_management'],
      bar_touch: baseTouch
    };
  }

  function evaluateEntryRuleLane(ruleLane, input) {
    const lane = String(ruleLane || RULE_LANE_NORMAL).toUpperCase();
    if (lane === RULE_LANE_EXPANSION) return expansionRuleLaneEntryDecision(input);
    if (lane === RULE_LANE_EXPANSION_LITE) return expansionLiteRuleLaneEntryDecision(input);
    return normalRuleLaneEntryDecision(input);
  }

  function evaluateEnabledEntryRuleLanes(lanePolicy, inputByLane) {
    const lanes = Array.isArray(lanePolicy?.enabled_entry_rule_lanes) && lanePolicy.enabled_entry_rule_lanes.length
      ? lanePolicy.enabled_entry_rule_lanes
      : [String(lanePolicy?.active_entry_rule_lane || RULE_LANE_NORMAL).toUpperCase()];
    const decisions = [];
    for (const lane of lanes) {
      const input = inputByLane?.[lane];
      if (!input) continue;
      decisions.push(evaluateEntryRuleLane(lane, input));
    }
    const entryDecisions = decisions.filter(decision => String(decision?.action || '').toUpperCase() === 'ENTRY');
    const selected = entryDecisions[0]
      || decisions.find(decision => decision?.rule_lane === RULE_LANE_NORMAL)
      || decisions[0]
      || null;
    return {
      selected_decision: selected,
      selected_lane: selected?.rule_lane || lanes[0] || RULE_LANE_NORMAL,
      selected_decisions: entryDecisions,
      entry_decisions: entryDecisions,
      lane_decisions: decisions,
      simultaneous_entry: entryDecisions.length > 1,
      simultaneous_entry_policy: String(lanePolicy?.simultaneous_entry_policy || 'SINGLE_LANE_ONLY').toUpperCase()
    };
  }

  function evaluateCloseRuleLane(ruleLane, input) {
    const lane = String(ruleLane || RULE_LANE_NORMAL).toUpperCase();
    if (lane === RULE_LANE_EXPANSION) return expansionRuleLaneCloseDecision(input);
    if (lane === RULE_LANE_EXPANSION_LITE) return expansionLiteRuleLaneCloseDecision(input);
    return normalRuleLaneCloseDecision(input);
  }

  function m5ExecutionPreviousLifecycle(state, referenceMs, draft) {
    const previous = state?.simulationTrace?.run_snapshot?.position_lifecycle || state?.simulationRunSnapshot?.position_lifecycle || null;
    if (!previous) return { lifecycle: null, status: 'NO_PREVIOUS', warning: '' };
    const previousMs = numberOrNull(previous?.reference?.reference_close_ms ?? previous?.reference?.state_as_of_ms);
    const sameProfile = !previous?.profile_id || previous.profile_id === draft?.profile_id;
    const currentDataset = String(draft?.dataset?.primary?.sha256 || '');
    const previousDataset = String(previous?.dataset_sha256 || '');
    const sameDataset = !previousDataset || !currentDataset || previousDataset === currentDataset;
    const currentRuleVersion = String(draft?.rule_version || '');
    const previousRuleVersion = String(previous?.rule_version || '');
    const sameRuleVersion = !!previousRuleVersion && previousRuleVersion === currentRuleVersion;
    if (!sameProfile || !sameDataset) return { lifecycle: null, status: 'RESET_PROFILE_OR_DATASET_CHANGED', warning: '前回の建玉状態はProfileまたはDatasetが異なるため引き継ぎません。' };
    if (!sameRuleVersion) return { lifecycle: null, status: 'RESET_RULE_VERSION_CHANGED', warning: 'Simulation Ruleが変更されたため、旧ルールの建玉状態を引き継がずFlatから開始します。' };
    if (previousMs != null && referenceMs != null && previousMs > referenceMs) return { lifecycle: null, status: 'RESET_REFERENCE_MOVED_BACKWARD', warning: '基準地点を過去へ戻したため、未来側の建玉状態は引き継ぎません。' };
    return { lifecycle: cloneJsonValue(previous), status: 'CONTINUED', warning: '' };
  }

  function m5ExecutionEmptyLifecycle(draft, reference) {
    return {
      schema_version: 'fx_position_lifecycle_snapshot_v0_1',
      kind: 'fx_position_lifecycle_snapshot',
      status: 'ready',
      phase: 'v0.9.0.42-normal-anchor-retire-on-close',
      created_at: nowLocalIso(),
      profile_id: draft?.profile_id || '',
      rule_version: draft?.rule_version || '',
      dataset_sha256: draft?.dataset?.primary?.sha256 || '',
      reference: cloneJsonValue(reference || {}),
      valuation_policy: m5ExecutionValuationPolicy(draft?.m5_execution_policy || {}),
      engine: {
        engine_id: M5_EXECUTION_ENGINE_ID,
        mode: 'reference_point_step',
        execution_timeframe: 'M5',
        management_timeframe_cap: 'DAY',
        week_management_forbidden: true,
        no_lookahead: true,
        rule_lane_orchestration: true,
        shared_fact_source: 'TIMEFRAME_STATE_SNAPSHOT',
        close_lane_source: 'OPEN_TRADE_RULE_LANE'
      },
      portfolio: {
        status: 'FLAT',
        active_trade_id: null,
        positions: [],
        trades: [],
        evaluated_reference_keys: [],
        evaluated_reference_count: 0,
        last_evaluated_reference_key: null,
        last_evaluated_reference_ms: null,
        normal_entry_opportunities: [],
        used_dow_confirmation_ids: [],
        expansion_lite_entry_opportunities: [],
        used_expansion_lite_confirmation_ids: [],
        normal_anchor_lifecycle: m5ExecutionEmptyNormalAnchorLifecycle()
      },
      trigger_evaluation: null,
      decision_events: [],
      state_change_events: [],
      execution_events: [],
      run_result: {
        status: 'NO_EXECUTION_YET',
        execution_event_count: 0,
        trade_ids: [],
        open_trade_ids: [],
        closed_trade_ids: [],
        open_position_ids: [],
        realized_price_delta_units: 0
      },
      validation: { valid: true, checked_at: nowLocalIso(), errors: [], warnings: [], no_lookahead: true },
      teacher_guard: '共通観測Stateから、選択されたRule LaneのEntry Evaluatorと、保有TradeのRule Laneに対応するClose Evaluatorを独立実行します。通常Rule LaneはWEEK/DAY/Expansion判定を参照しません。過去チャート検証用で、リアル注文・売買推奨・資金管理は行いません。'
    };
  }

  function m5ExecutionCauseIds(upperSnapshot, timeframeSnapshot, hsiSnapshot, anchorId) {
    const upperEventId = upperSnapshot?.decision_events?.[upperSnapshot.decision_events.length - 1]?.event_id || '';
    const m5StateEventId = (timeframeSnapshot?.state_events || []).find(event => String(event?.timeframe || '').toUpperCase() === 'M5')?.event_id || '';
    const hsiEventId = (hsiSnapshot?.lifecycle_events || []).find(event => event?.anchor_id === anchorId && event?.event_type === 'hsi_anchor_adopted')?.event_id
      || (hsiSnapshot?.lifecycle_events || []).find(event => event?.anchor_id === anchorId)?.event_id
      || '';
    return uniqueStrings([upperEventId, m5StateEventId, hsiEventId]);
  }

  function m5ExecutionCreateTriggerEvent(context, trigger, lifecycleBefore) {
    const referenceMs = context.referenceMs;
    return {
      event_id: `m5_trigger_evt_${stableSwingToken(referenceMs)}_${stableTextHash(JSON.stringify(trigger))}`,
      source_type: SIMULATION_TRACE_SOURCE_TYPE,
      generated_by: M5_EXECUTION_GENERATOR,
      engine_id: M5_EXECUTION_ENGINE_ID,
      event_type: 'm5_trigger_evaluated',
      simulation_time: context.referenceTime,
      timeframe: 'M5',
      panel: 'M5',
      price: context.price,
      rule_lane: trigger.rule_lane || null,
      evaluator_id: trigger.evaluator_id || null,
      decision_scope: trigger.decision_scope || null,
      summary: `M5実行判定 / ${trigger.action_label} / ${trigger.status_label} / ${trigger.summary}`,
      reason_codes: [...(trigger.reason_codes || [])],
      rule_ids: [...(trigger.rule_ids || [])],
      cause_event_ids: [...(context.causeEventIds || [])],
      upper_state_summary: {
        direction: context.direction,
        upper_mode: context.upperDecision?.decision_mode || 'WATCH',
        normal_entry: context.upperDecision?.entry_policy?.normal_entry?.status || 'NOT_EVALUATED',
        expansion_entry: context.upperDecision?.entry_policy?.expansion_entry?.status || 'NOT_EVALUATED',
        reentry: context.upperDecision?.entry_policy?.reentry?.status || 'NOT_EVALUATED',
        add_on: context.upperDecision?.entry_policy?.add_on?.status || 'NOT_EVALUATED',
        h1_exit: context.upperDecision?.position_policy?.h1_exit_trigger?.signal || 'NONE'
      },
      state_before: m5ExecutionPortfolioCompact(lifecycleBefore?.portfolio),
      state_after: { trigger: cloneJsonValue(trigger), portfolio: m5ExecutionPortfolioCompact(lifecycleBefore?.portfolio) },
      display: { visible: false, open: false, pinned: false, style: 'm5_trigger_evaluated' }
    };
  }

  function m5ExecutionValuationPolicy(policy) {
    const source = policy?.valuation_policy || {};
    const unitAmount = Number(source.unit_base_currency_amount || 1000);
    return {
      unit_base_currency_amount: Number.isFinite(unitAmount) && unitAmount > 0 ? unitAmount : 1000,
      display_currency: String(source.display_currency || 'JPY').toUpperCase(),
      quote_currency: String(source.quote_currency || 'JPY').toUpperCase(),
      pnl_formula: String(source.pnl_formula || 'USDJPY_DIRECT_QUOTE'),
      stop_basis: String(source.stop_basis || 'HSI_ENTRY_ANCHOR'),
      fee_and_slippage_included: source.fee_and_slippage_included === true
    };
  }

  function m5ExecutionRiskProfile(entryPrice, stopPrice, units, policy, stopBasisOverride = null) {
    const valuation = m5ExecutionValuationPolicy(policy);
    const entry = numberOrNull(entryPrice);
    const stop = numberOrNull(stopPrice);
    const unitCount = Math.max(0, Number(units || 0));
    const riskPrice = entry == null || stop == null ? null : Math.abs(entry - stop);
    const initialRiskJpy = riskPrice == null ? null : riskPrice * valuation.unit_base_currency_amount * unitCount;
    return {
      stop_basis: stopBasisOverride || valuation.stop_basis,
      stop_price: stop,
      entry_price: entry,
      initial_units: unitCount,
      unit_base_currency_amount: valuation.unit_base_currency_amount,
      display_currency: valuation.display_currency,
      initial_risk_price: riskPrice,
      initial_risk_jpy: initialRiskJpy
    };
  }

  function m5ExecutionPortfolioRunRealizedJpy(portfolio, policy) {
    const valuation = m5ExecutionValuationPolicy(policy);
    const cumulativeDelta = (portfolio?.trades || []).reduce((sum, trade) => sum + Number(trade?.realized_price_delta_units || 0), 0);
    return cumulativeDelta * valuation.unit_base_currency_amount;
  }

  function m5ExecutionFinancialSnapshot(trade, realizedPriceDeltaUnits, policy, portfolio = null) {
    const valuation = m5ExecutionValuationPolicy(policy);
    const risk = trade?.risk_profile || {};
    const initialRiskJpy = numberOrNull(risk.initial_risk_jpy);
    const realizedDelta = Number(realizedPriceDeltaUnits || 0);
    const realizedJpy = realizedDelta * valuation.unit_base_currency_amount;
    const tradeCumulativeDelta = Number(trade?.realized_price_delta_units || 0);
    const tradeCumulativeJpy = tradeCumulativeDelta * valuation.unit_base_currency_amount;
    const runCumulativeJpy = portfolio ? m5ExecutionPortfolioRunRealizedJpy(portfolio, policy) : tradeCumulativeJpy;
    const ratio = initialRiskJpy && initialRiskJpy > 0 ? tradeCumulativeJpy / initialRiskJpy : null;
    return {
      stop_basis: risk.stop_basis || valuation.stop_basis,
      stop_price: numberOrNull(risk.stop_price),
      entry_price: numberOrNull(risk.entry_price ?? trade?.entry_price),
      initial_units: numberOrNull(risk.initial_units),
      unit_base_currency_amount: valuation.unit_base_currency_amount,
      display_currency: valuation.display_currency,
      initial_risk_jpy: initialRiskJpy,
      realized_profit_jpy: realizedJpy,
      trade_cumulative_realized_profit_jpy: tradeCumulativeJpy,
      cumulative_realized_profit_jpy: runCumulativeJpy,
      profit_vs_initial_risk_pct: ratio == null ? null : ratio * 100,
      risk_multiple: ratio
    };
  }

  function m5ExecutionEvent(context, eventType, summary, ruleIds, reasonCodes, causeIds, beforePortfolio, afterPortfolio, extra = {}) {
    const token = `${eventType}|${context.referenceMs}|${afterPortfolio?.active_trade_id || ''}|${(extra.position_ids || []).join(',')}`;
    return {
      event_id: `execution_evt_${stableSwingToken(context.referenceMs)}_${stableTextHash(token)}`,
      source_type: SIMULATION_TRACE_SOURCE_TYPE,
      generated_by: M5_EXECUTION_GENERATOR,
      engine_id: M5_EXECUTION_ENGINE_ID,
      event_type: eventType,
      simulation_time: context.referenceTime,
      timeframe: 'M5',
      panel: 'M5',
      price: context.price,
      summary,
      reason_codes: uniqueStrings(reasonCodes),
      rule_ids: uniqueStrings(ruleIds),
      cause_event_ids: uniqueStrings(causeIds),
      trade_id: extra.trade_id || afterPortfolio?.active_trade_id || beforePortfolio?.active_trade_id || null,
      position_ids: [...(extra.position_ids || [])],
      rule_lane: extra.rule_lane || extra.execution?.rule_lane || null,
      evaluator_id: extra.evaluator_id || extra.execution?.evaluator_id || null,
      execution: cloneJsonValue(extra.execution || {}),
      upper_state_summary: {
        direction: context.direction,
        decision_mode: context.upperDecision?.decision_mode || 'WATCH',
        h1_exit_signal: context.upperDecision?.position_policy?.h1_exit_trigger?.signal || 'NONE'
      },
      state_before: { portfolio: m5ExecutionPortfolioCompact(beforePortfolio) },
      state_after: { portfolio: m5ExecutionPortfolioCompact(afterPortfolio), execution: cloneJsonValue(extra.execution || {}) },
      display: { visible: true, open: false, pinned: false, style: `execution_${eventType}` }
    };
  }

  function m5ExecutionNewTrade(portfolio, context, triggerEvent, entryMode, policy) {
    const tradeNo = (portfolio.trades || []).length + 1;
    const normalEntryNo = (portfolio.trades || []).filter(item => String(item?.rule_lane || '').toUpperCase() === RULE_LANE_NORMAL).length + 1;
    const tradeId = `trade_${String(tradeNo).padStart(4, '0')}_${stableSwingToken(context.referenceMs)}`;
    const initialUnits = Math.max(1, Number(policy?.position_sizing?.initial_units || 10));
    const anchor = context.entryAnchor;
    const band = context.hsiBand;
    const target = band?.next || null;
    const targetPrice = target ? m5ExecutionTargetPrice(context.anchorPrice, context.direction, target.raw, policy) : null;
    const stopPlan = context?.entryOpportunity?.normal_stop_plan?.valid
      ? cloneJsonValue(context.entryOpportunity.normal_stop_plan)
      : m5ExecutionNormalStopPlan(context.price, targetPrice, context.anchorPrice, context.direction, policy);
    if (!stopPlan?.valid) throw new Error('NORMAL_CLOSE_MISS_STOP_PLAN_INVALID');
    const stopBasis = 'TARGET_DISTANCE_RATIO_WITH_HSI_ANCHOR_HARD_LIMIT';
    const riskProfile = m5ExecutionRiskProfile(context.price, stopPlan.stop_price, initialUnits, policy, stopBasis);
    const positionId = `${tradeId}_normal`;
    const position = {
      position_id: positionId,
      trade_id: tradeId,
      role: 'NORMAL',
      rule_lane: RULE_LANE_NORMAL,
      entry_evaluator_id: NORMAL_ENTRY_EVALUATOR_ID,
      close_evaluator_id: NORMAL_CLOSE_EVALUATOR_ID,
      side: context.direction,
      units_initial: initialUnits,
      units_open: initialUnits,
      entry_mode: entryMode,
      normal_entry_sequence_no: normalEntryNo,
      entry_timeframe: 'M5',
      management_timeframe: 'H1',
      management_timeframe_cap: 'DAY',
      entry_time: context.referenceTime,
      entry_ms: context.referenceMs,
      entry_price: context.price,
      entry_anchor_id: anchor?.anchor_id || null,
      entry_anchor_price: context.anchorPrice,
      dow_confirmation_id: context.dowConfirmation?.confirmation_id || null,
      dow_breakout_threshold_price: numberOrNull(context.dowConfirmation?.breakout_threshold_price),
      entry_opportunity_id: context.entryOpportunity?.opportunity_id || null,
      status: 'OPEN',
      closed_at: null,
      close_price: null,
      close_class: null,
      risk_profile: cloneJsonValue(riskProfile),
      close_miss_plan: cloneJsonValue(stopPlan),
      invalidation_rule: {
        rule_id: 'rule_normal_close_miss_target_distance_ratio',
        type: stopBasis,
        anchor_id: anchor?.anchor_id || null,
        invalidation_price: stopPlan.stop_price,
        ratio_stop_price: stopPlan.ratio_stop_price,
        hsi_anchor_hard_limit_price: stopPlan.hsi_anchor_hard_limit_price,
        hsi_anchor_hard_limit_applied: stopPlan.hsi_anchor_hard_limit_applied,
        max_loss_to_reward_ratio: stopPlan.max_loss_to_reward_ratio,
        direction: context.direction,
        fixed_at_entry: true
      },
      target_plan: {
        mode: 'SINGLE_CLOSE_NEXT_HSI_BOUNDARY',
        entry_distance_raw: context.distanceRaw,
        entry_band: band?.current?.label || null,
        next_target_label: target?.label || null,
        next_target_raw: target?.raw ?? null,
        next_target_price: targetPrice,
        fixed_at_entry: true,
        close_all_units: true,
        partial_close_units: 0
      },
      promotion_history: []
    };
    const trade = {
      trade_id: tradeId,
      sequence: tradeNo,
      status: 'OPEN',
      rule_lane: RULE_LANE_NORMAL,
      entry_evaluator_id: NORMAL_ENTRY_EVALUATOR_ID,
      close_evaluator_id: NORMAL_CLOSE_EVALUATOR_ID,
      side: context.direction,
      entry_mode: entryMode,
      normal_entry_sequence_no: normalEntryNo,
      close_policy: 'SINGLE_CLOSE',
      opened_at: context.referenceTime,
      opened_at_ms: context.referenceMs,
      entry_price: context.price,
      entry_event_id: null,
      entry_anchor_id: anchor?.anchor_id || null,
      entry_anchor_price: context.anchorPrice,
      dow_confirmation_id: context.dowConfirmation?.confirmation_id || null,
      dow_breakout_threshold_price: numberOrNull(context.dowConfirmation?.breakout_threshold_price),
      entry_opportunity_id: context.entryOpportunity?.opportunity_id || null,
      target_label: target?.label || null,
      target_price: targetPrice,
      position_ids: [positionId],
      closed_at: null,
      closed_at_ms: null,
      close_price: null,
      close_class: null,
      terminal_close_event_id: null,
      risk_profile: cloneJsonValue(riskProfile),
      close_miss_plan: cloneJsonValue(stopPlan),
      valuation_policy: m5ExecutionValuationPolicy(policy),
      realized_price_delta_units: 0,
      realized_profit_jpy: 0
    };
    portfolio.positions.push(position);
    portfolio.trades.push(trade);
    portfolio.active_trade_id = tradeId;
    portfolio.status = 'OPEN';
    const normalAnchorLifecycle = m5ExecutionActivateNormalAnchor(portfolio, context, tradeId);
    trade.normal_hsi_anchor_lifecycle_at_entry = cloneJsonValue(normalAnchorLifecycle);
    position.normal_hsi_anchor_lifecycle_status = normalAnchorLifecycle.status;
    return { trade, positions: [position], targetPrice, stopPlan, triggerEvent, normalAnchorLifecycle };
  }

  function m5ExecutionNewExpansionLiteTrade(portfolio, context, triggerEvent, policy) {
    const tradeNo = (portfolio.trades || []).length + 1;
    const tradeId = `trade_${String(tradeNo).padStart(4, '0')}_${stableSwingToken(context.referenceMs)}`;
    const initialUnits = Math.max(1, Number(policy?.position_sizing?.initial_units || 10));
    const targetRaw = Number(policy?.expansion_lite_policy?.target_raw ?? 377);
    const targetLabel = String(policy?.expansion_lite_policy?.target_label || 'R5');
    const targetPrice = m5ExecutionTargetPrice(context.anchorPrice, context.direction, targetRaw, policy);
    const positionId = `${tradeId}_expansion_lite_core`;
    const position = {
      position_id: positionId,
      trade_id: tradeId,
      role: 'EXPANSION_LITE_CORE',
      rule_lane: RULE_LANE_EXPANSION_LITE,
      entry_evaluator_id: EXPANSION_LITE_ENTRY_EVALUATOR_ID,
      close_evaluator_id: EXPANSION_LITE_CLOSE_EVALUATOR_ID,
      side: context.direction,
      units_initial: initialUnits,
      units_open: initialUnits,
      entry_mode: 'EXPANSION_LITE_R3',
      entry_timeframe: 'M5',
      management_timeframe: 'M5',
      management_timeframe_cap: 'H1',
      entry_time: context.referenceTime,
      entry_ms: context.referenceMs,
      entry_price: context.price,
      entry_anchor_id: context.entryAnchor?.anchor_id || null,
      entry_anchor_price: context.anchorPrice,
      dow_confirmation_id: context.dowConfirmation?.confirmation_id || null,
      status: 'OPEN',
      closed_at: null,
      close_price: null,
      close_class: null,
      risk_profile: m5ExecutionRiskProfile(context.price, context.anchorPrice, initialUnits, policy),
      invalidation_rule: {
        rule_id: 'rule_expansion_lite_anchor_exit_touch',
        type: 'EXPANSION_LITE_ANCHOR_EXIT',
        anchor_id: context.entryAnchor?.anchor_id || null,
        invalidation_price: context.anchorPrice,
        direction: context.direction,
        fixed_at_entry: true
      },
      target_plan: {
        mode: 'EXPANSION_LITE_R5_TARGET',
        entry_distance_raw: context.distanceRaw,
        entry_band: 'R3',
        next_target_label: targetLabel,
        next_target_raw: targetRaw,
        next_target_price: targetPrice,
        fixed_at_entry: true,
        close_all_units: true,
        partial_close_units: 0
      },
      promotion_history: []
    };
    const trade = {
      trade_id: tradeId,
      sequence: tradeNo,
      status: 'OPEN',
      rule_lane: RULE_LANE_EXPANSION_LITE,
      entry_evaluator_id: EXPANSION_LITE_ENTRY_EVALUATOR_ID,
      close_evaluator_id: EXPANSION_LITE_CLOSE_EVALUATOR_ID,
      side: context.direction,
      entry_mode: 'EXPANSION_LITE_R3',
      close_policy: 'EXPANSION_LITE_ALL_CLOSE',
      opened_at: context.referenceTime,
      opened_at_ms: context.referenceMs,
      entry_price: context.price,
      entry_event_id: null,
      entry_anchor_id: context.entryAnchor?.anchor_id || null,
      entry_anchor_price: context.anchorPrice,
      dow_confirmation_id: context.dowConfirmation?.confirmation_id || null,
      target_label: targetLabel,
      target_price: targetPrice,
      position_ids: [positionId],
      consumed_add_on_levels: [],
      closed_at: null,
      closed_at_ms: null,
      close_price: null,
      close_class: null,
      terminal_close_event_id: null,
      risk_profile: m5ExecutionRiskProfile(context.price, context.anchorPrice, initialUnits, policy),
      valuation_policy: m5ExecutionValuationPolicy(policy),
      realized_price_delta_units: 0,
      realized_profit_jpy: 0
    };
    portfolio.positions.push(position);
    portfolio.trades.push(trade);
    portfolio.active_trade_id = tradeId;
    portfolio.status = 'OPEN';
    return { trade, positions: [position], targetPrice, triggerEvent };
  }

  function m5ExecutionAddExpansionLitePositions(portfolio, trade, context, levels, policy) {
    const unitsPerLevel = Math.max(1, Number(policy?.position_sizing?.add_on_units || 2));
    const created = [];
    const existingCount = (portfolio.positions || []).filter(position => position.trade_id === trade?.trade_id && position.role === 'EXPANSION_LITE_ADD_ON').length;
    (levels || []).forEach((level, index) => {
      const label = String(level?.label || 'R?');
      const raw = Number(level?.raw);
      const levelPrice = numberOrNull(level?.price)
        ?? m5ExecutionTargetPrice(trade?.entry_anchor_price, trade?.side, raw, policy);
      const open = numberOrNull(level?.open);
      const executionPrice = trade?.side === 'SHORT'
        ? (open != null && levelPrice != null && open <= levelPrice ? open : levelPrice)
        : (open != null && levelPrice != null && open >= levelPrice ? open : levelPrice);
      const positionId = `${trade?.trade_id || 'trade'}_expansion_lite_addon_${String(existingCount + index + 1).padStart(2, '0')}`;
      const targetRaw = Number(policy?.expansion_lite_policy?.target_raw ?? 377);
      const targetLabel = String(policy?.expansion_lite_policy?.target_label || 'R5');
      const targetPrice = m5ExecutionTargetPrice(trade?.entry_anchor_price, trade?.side, targetRaw, policy);
      const position = {
        position_id: positionId,
        trade_id: trade?.trade_id || portfolio.active_trade_id,
        role: 'EXPANSION_LITE_ADD_ON',
        rule_lane: RULE_LANE_EXPANSION_LITE,
        entry_evaluator_id: EXPANSION_LITE_ENTRY_EVALUATOR_ID,
        close_evaluator_id: EXPANSION_LITE_CLOSE_EVALUATOR_ID,
        side: trade?.side || context.direction,
        units_initial: unitsPerLevel,
        units_open: unitsPerLevel,
        entry_mode: `EXPANSION_LITE_ADD_ON_${label}`,
        entry_level: label,
        entry_level_raw: raw,
        entry_timeframe: 'M5',
        management_timeframe: 'M5',
        management_timeframe_cap: 'H1',
        entry_time: context.referenceTime,
        entry_ms: context.referenceMs,
        entry_price: executionPrice,
        entry_anchor_id: trade?.entry_anchor_id || null,
        entry_anchor_price: trade?.entry_anchor_price,
        status: 'OPEN',
        risk_profile: m5ExecutionRiskProfile(executionPrice, trade?.entry_anchor_price, unitsPerLevel, policy),
        invalidation_rule: {
          rule_id: 'rule_expansion_lite_anchor_exit_touch',
          type: 'EXPANSION_LITE_ANCHOR_EXIT',
          anchor_id: trade?.entry_anchor_id || null,
          invalidation_price: trade?.entry_anchor_price,
          direction: trade?.side || context.direction,
          fixed_at_entry: true
        },
        target_plan: {
          mode: 'EXPANSION_LITE_R5_TARGET',
          entry_distance_raw: raw,
          entry_band: label,
          next_target_label: targetLabel,
          next_target_raw: targetRaw,
          next_target_price: targetPrice,
          fixed_at_entry: true,
          close_all_units: true,
          partial_close_units: 0
        },
        promotion_history: [],
        closed_at: null,
        close_price: null,
        close_class: null
      };
      portfolio.positions.push(position);
      trade.position_ids.push(positionId);
      trade.consumed_add_on_levels = uniqueStrings([...(trade.consumed_add_on_levels || []), label]);
      created.push(position);
    });
    return created;
  }

  function m5ExecutionRealizedDelta(position, closePrice, units) {
    const sign = position.side === 'SHORT' ? -1 : 1;
    return sign * (Number(closePrice) - Number(position.entry_price)) * Number(units || 0);
  }

  function m5ExecutionClosePositions(portfolio, positions, context, closeClass) {
    let realized = 0;
    positions.forEach(position => {
      const units = Number(position.units_open || 0);
      if (units <= 0) return;
      realized += m5ExecutionRealizedDelta(position, context.price, units);
      position.units_open = 0;
      position.status = 'CLOSED';
      position.closed_at = context.referenceTime;
      position.close_price = context.price;
      position.close_class = closeClass;
    });
    const tradeId = positions[0]?.trade_id || portfolio.active_trade_id;
    const trade = (portfolio.trades || []).find(item => item.trade_id === tradeId);
    if (trade && !m5ExecutionOpenPositions({ positions: portfolio.positions.filter(position => position.trade_id === tradeId) }).length) {
      trade.status = 'CLOSED';
      trade.closed_at = context.referenceTime;
      trade.closed_at_ms = context.referenceMs;
      trade.close_price = context.price;
      trade.close_class = closeClass;
      trade.realized_price_delta_units = Number(trade.realized_price_delta_units || 0) + realized;
      if (portfolio.active_trade_id === tradeId) portfolio.active_trade_id = null;
    }
    let normalAnchorRetirement = null;
    if (trade && trade.status === 'CLOSED' && String(trade.rule_lane || '').toUpperCase() === RULE_LANE_NORMAL) {
      normalAnchorRetirement = m5ExecutionRetireNormalAnchor(portfolio, trade, context, closeClass);
      trade.normal_hsi_anchor_retired_at = normalAnchorRetirement.retired_at;
      trade.normal_hsi_anchor_retired_at_ms = normalAnchorRetirement.retired_at_ms;
      trade.normal_hsi_anchor_retired_reason = normalAnchorRetirement.reason;
    }
    portfolio.status = m5ExecutionOpenPositions(portfolio).length ? 'OPEN' : 'FLAT';
    return { realized, trade, normalAnchorRetirement };
  }

  function m5ExecutionRunResult(lifecycle) {
    const trades = lifecycle?.portfolio?.trades || [];
    const positions = lifecycle?.portfolio?.positions || [];
    const executionEvents = lifecycle?.execution_events || [];
    const openTrades = trades.filter(trade => trade.status === 'OPEN');
    const closedTrades = trades.filter(trade => trade.status === 'CLOSED');
    const openPositions = positions.filter(position => position.status === 'OPEN' && Number(position.units_open || 0) > 0);
    return {
      status: openTrades.length ? 'POSITION_OPEN' : executionEvents.length ? 'EXECUTION_COMPLETE_OR_FLAT' : 'NO_EXECUTION_YET',
      execution_event_count: executionEvents.length,
      trade_ids: trades.map(trade => trade.trade_id),
      open_trade_ids: openTrades.map(trade => trade.trade_id),
      closed_trade_ids: closedTrades.map(trade => trade.trade_id),
      open_position_ids: openPositions.map(position => position.position_id),
      realized_price_delta_units: trades.reduce((sum, trade) => sum + Number(trade.realized_price_delta_units || 0), 0),
      realized_profit_jpy: trades.reduce((sum, trade) => sum + Number(trade.realized_profit_jpy || 0), 0),
      unit_base_currency_amount: Number(lifecycle?.valuation_policy?.unit_base_currency_amount || trades[0]?.valuation_policy?.unit_base_currency_amount || 1000),
      teacher_guard: 'Rule Lane別のEntry/Close Evaluatorによる検証用の仮想売買結果です。通常Rule LaneはWEEK/DAY/Expansion判定から独立しています。損益額は1単位=1,000通貨の表示用試算で、手数料・スリッページ・税・資金管理・リアル注文は対象外です。'
    };
  }

  function buildM5ExecutionSingleLanePositionLifecycleSnapshot(state, draft, candleSync, timeframeSnapshot, hsiSnapshot, upperSnapshot) {
    const policy = cloneJsonValue(draft?.m5_execution_policy || {});
    const referenceMs = numberOrNull(candleSync?.reference?.reference_close_ms);
    const referenceTime = String(candleSync?.reference?.reference_close_time || '');
    const m5State = timeframeSnapshot?.timeframes?.M5 || {};
    const currentBar = m5State?.latest_confirmed_bar || candleSync?.timeframes?.M5?.latest_confirmed_bar || {};
    const price = numberOrNull(currentBar?.close);
    const lanePolicy = m5RuleLanePolicy(policy);
    const selectedEntryRuleLane = lanePolicy.active_entry_rule_lane;
    const normalEntryV08 = m5ExecutionNormalEntryV08Facts(timeframeSnapshot);
    const dowConfirmation = m5ExecutionDowConfirmation(m5State);
    const expansionLiteFacts = m5ExecutionExpansionLiteFacts(timeframeSnapshot, draft, dowConfirmation);
    const confirmationTrendDirection = String(dowConfirmation?.direction || '').toUpperCase();
    const fallbackConfirmationSide = confirmationTrendDirection === 'DOWN'
      ? 'SHORT'
      : confirmationTrendDirection === 'UP'
        ? 'LONG'
        : 'UNDETERMINED';
    const normalEntryResolution = m5State?.hsi_anchor_state?.rule_lanes?.NORMAL?.entry_anchor
      || m5State?.hsi_anchor_state?.normal_entry
      || m5State?.hsi_anchor_state?.entry
      || {};
    const expansionLiteEntryResolution = m5ExecutionExpansionLiteAnchorResolution(dowConfirmation);
    const expansionLiteEntryRaw = Number(policy?.expansion_lite_policy?.entry_raw ?? 144);
    const expansionLiteEntryLabel = String(policy?.expansion_lite_policy?.entry_label || 'R3');

    function buildEntryLaneContext(ruleLane) {
      const isLite = ruleLane === RULE_LANE_EXPANSION_LITE;
      const direction = isLite ? expansionLiteFacts.confirmation_side : normalEntryV08.direction;
      const confirmationSide = fallbackConfirmationSide === 'UNDETERMINED' ? direction : fallbackConfirmationSide;
      const entryResolution = isLite ? expansionLiteEntryResolution : normalEntryResolution;
      const entryAnchor = entryResolution?.anchor || null;
      const anchorPrice = numberOrNull(entryAnchor?.price);
      const distanceRaw = m5ExecutionDistanceRaw(price, anchorPrice, confirmationSide, policy);
      const hsiBand = m5ExecutionHsiBand(distanceRaw, policy);
      const r2Touch = m5ExecutionR2Touch(currentBar, anchorPrice, confirmationSide, policy);
      const r25Touch = m5ExecutionR25Touch(currentBar, anchorPrice, confirmationSide, policy);
      const r3Touch = m5ExecutionLevelTouch(currentBar, anchorPrice, confirmationSide, expansionLiteEntryRaw, expansionLiteEntryLabel, policy);
      const minEntryRaw = isLite ? expansionLiteEntryRaw : Number(policy?.hsi_distance?.entry_min_raw || 89);
      const minEntryLabel = isLite ? expansionLiteEntryLabel.toUpperCase() : String(policy?.hsi_distance?.entry_min_label || 'R2').toUpperCase();
      const minEntryToken = minEntryLabel.replace(/[^A-Z0-9]+/g, '_');
      const causeEventIds = m5ExecutionCauseIds(upperSnapshot, timeframeSnapshot, hsiSnapshot, entryResolution?.anchor_id);
      return {
        ruleLane,
        direction,
        confirmationSide,
        entryResolution,
        entryAnchor,
        anchorPrice,
        distanceRaw,
        hsiBand,
        r2Touch,
        r25Touch,
        r3Touch,
        minEntryRaw,
        minEntryLabel,
        hsiReachedReasonCode: `HSI_${minEntryToken}_REACHED`,
        hsiNotReachedReasonCode: `HSI_${minEntryToken}_NOT_REACHED`,
        hsiEntryRuleId: `rule_m5_trigger_hsi_${minEntryToken.toLowerCase()}`,
        causeEventIds: uniqueStrings([...causeEventIds, dowConfirmation?.confirmation_id])
      };
    }

    const entryLaneContexts = {
      [RULE_LANE_NORMAL]: buildEntryLaneContext(RULE_LANE_NORMAL),
      [RULE_LANE_EXPANSION_LITE]: buildEntryLaneContext(RULE_LANE_EXPANSION_LITE)
    };
    let activeEntryLane = selectedEntryRuleLane === ENTRY_LANE_MODE_NORMAL_AND_EXPANSION_LITE
      ? RULE_LANE_NORMAL
      : selectedEntryRuleLane;
    let activeEntryContext = entryLaneContexts[activeEntryLane] || entryLaneContexts[RULE_LANE_NORMAL];
    let { direction, confirmationSide, entryResolution, entryAnchor, anchorPrice, distanceRaw, hsiBand, r2Touch, r25Touch, r3Touch, minEntryRaw, minEntryLabel, hsiReachedReasonCode, hsiNotReachedReasonCode, hsiEntryRuleId, causeEventIds } = activeEntryContext;
    const context = { referenceMs, referenceTime, price, direction, confirmationSide, currentBar, m5State, timeframeSnapshot, entryResolution, entryAnchor, anchorPrice, distanceRaw, hsiBand, r2Touch, r25Touch, r3Touch, dowConfirmation, entryOpportunity: null, causeEventIds, upperDecision: upperSnapshot, normalEntryV08, expansionLiteFacts };
    function selectEntryLaneContext(ruleLane) {
      activeEntryLane = ruleLane === RULE_LANE_EXPANSION_LITE ? RULE_LANE_EXPANSION_LITE : RULE_LANE_NORMAL;
      activeEntryContext = entryLaneContexts[activeEntryLane] || entryLaneContexts[RULE_LANE_NORMAL];
      ({ direction, confirmationSide, entryResolution, entryAnchor, anchorPrice, distanceRaw, hsiBand, r2Touch, r25Touch, r3Touch, minEntryRaw, minEntryLabel, hsiReachedReasonCode, hsiNotReachedReasonCode, hsiEntryRuleId, causeEventIds } = activeEntryContext);
      Object.assign(context, { direction, confirmationSide, entryResolution, entryAnchor, anchorPrice, distanceRaw, hsiBand, r2Touch, r25Touch, r3Touch, causeEventIds });
    }
    const previousInfo = m5ExecutionPreviousLifecycle(state, referenceMs, draft);
    const lifecycle = previousInfo.lifecycle || m5ExecutionEmptyLifecycle(draft, candleSync?.reference);
    lifecycle.phase = 'v0.9.1.13-normal-entry-gate-failure-log';
    lifecycle.created_at = nowLocalIso();
    lifecycle.reference = cloneJsonValue(candleSync?.reference || {});
    lifecycle.profile_id = draft?.profile_id || '';
    lifecycle.rule_version = draft?.rule_version || '';
    lifecycle.dataset_sha256 = draft?.dataset?.primary?.sha256 || '';
    lifecycle.engine = {
      engine_id: String(policy.engine_id || M5_EXECUTION_ENGINE_ID),
      mode: String(policy.mode || 'reference_point_step'),
      execution_timeframe: 'M5',
      management_timeframe_cap: String(policy?.management_timeframe?.cap || 'DAY'),
      week_management_forbidden: policy?.management_timeframe?.week_forbidden !== false,
      no_lookahead: policy.no_lookahead === true,
      rule_lane_orchestration: true,
      selected_entry_rule_lane: m5RuleLanePolicy(policy).active_entry_rule_lane,
      enabled_entry_rule_lanes: m5RuleLanePolicy(policy).enabled_entry_rule_lanes,
      cross_lane_condition_sharing: m5RuleLanePolicy(policy).cross_lane_condition_sharing,
      shared_fact_source: m5RuleLanePolicy(policy).shared_fact_source,
      close_lane_source: m5RuleLanePolicy(policy).close_lane_source
    };
    lifecycle.portfolio = lifecycle.portfolio || { status: 'FLAT', active_trade_id: null, positions: [], trades: [], evaluated_reference_keys: [], normal_entry_opportunities: [], used_dow_confirmation_ids: [], expansion_lite_entry_opportunities: [], used_expansion_lite_confirmation_ids: [], normal_anchor_lifecycle: m5ExecutionEmptyNormalAnchorLifecycle() };
    lifecycle.portfolio.positions = Array.isArray(lifecycle.portfolio.positions) ? lifecycle.portfolio.positions : [];
    lifecycle.portfolio.trades = Array.isArray(lifecycle.portfolio.trades) ? lifecycle.portfolio.trades : [];
    lifecycle.portfolio.evaluated_reference_keys = Array.isArray(lifecycle.portfolio.evaluated_reference_keys) ? lifecycle.portfolio.evaluated_reference_keys : [];
    lifecycle.portfolio.evaluated_reference_count = Math.max(0, Number(lifecycle.portfolio.evaluated_reference_count || lifecycle.portfolio.evaluated_reference_keys.length || 0));
    lifecycle.portfolio.last_evaluated_reference_key = lifecycle.portfolio.last_evaluated_reference_key
      || lifecycle.portfolio.evaluated_reference_keys[lifecycle.portfolio.evaluated_reference_keys.length - 1]
      || null;
    lifecycle.portfolio.normal_entry_opportunities = Array.isArray(lifecycle.portfolio.normal_entry_opportunities) ? lifecycle.portfolio.normal_entry_opportunities : [];
    lifecycle.portfolio.used_dow_confirmation_ids = Array.isArray(lifecycle.portfolio.used_dow_confirmation_ids) ? lifecycle.portfolio.used_dow_confirmation_ids : [];
    lifecycle.portfolio.expansion_lite_entry_opportunities = Array.isArray(lifecycle.portfolio.expansion_lite_entry_opportunities) ? lifecycle.portfolio.expansion_lite_entry_opportunities : [];
    lifecycle.portfolio.used_expansion_lite_confirmation_ids = Array.isArray(lifecycle.portfolio.used_expansion_lite_confirmation_ids) ? lifecycle.portfolio.used_expansion_lite_confirmation_ids : [];
    m5ExecutionEnsureNormalAnchorLifecycle(lifecycle.portfolio);
    lifecycle.decision_events = Array.isArray(lifecycle.decision_events) ? lifecycle.decision_events : [];
    lifecycle.state_change_events = Array.isArray(lifecycle.state_change_events) ? lifecycle.state_change_events : [];
    lifecycle.execution_events = Array.isArray(lifecycle.execution_events) ? lifecycle.execution_events : [];
    const referenceKey = `${referenceMs}|${currentBar?.confirmed_bar_key || ''}`;
    const alreadyEvaluated = String(lifecycle.portfolio.last_evaluated_reference_key || '') === referenceKey;
    const errors = [];
    const warnings = [];
    if (previousInfo.warning) warnings.push(previousInfo.warning);
    if (price == null) errors.push('M5確定足Closeが取得できません。');
    if (referenceMs == null) errors.push('M5基準時刻が取得できません。');
    if (m5State?.no_lookahead !== true) errors.push('M5 TimeframeStateがLookaheadなしで確定していません。');
    const allEntryCauseEventIds = uniqueStrings(Object.values(entryLaneContexts).flatMap(item => item.causeEventIds || []));
    if (!allEntryCauseEventIds.length) errors.push('M5実行判定の原因Eventが取得できません。');
    const openPositionsBefore = m5ExecutionOpenPositions(lifecycle.portfolio);
    const openTradePositions = openPositionsBefore.filter(position => !lifecycle.portfolio.active_trade_id || position.trade_id === lifecycle.portfolio.active_trade_id);
    const activePosition = openTradePositions.find(position => Number(position.units_open || 0) > 0) || null;
    const activeTrade = lifecycle.portfolio.trades.find(item => item.trade_id === lifecycle.portfolio.active_trade_id) || null;
    if (activeTrade?.side) context.direction = String(activeTrade.side).toUpperCase();
    const closeRuleLane = activePosition ? m5TradeRuleLane(activeTrade, activePosition) : null;
    if (activePosition && closeRuleLane) selectEntryLaneContext(closeRuleLane);
    const upperNoTrade = upperSnapshot?.no_trade?.active === true;
    const expansionPermission = String(upperSnapshot?.entry_policy?.expansion_entry?.status || 'NOT_EVALUATED').toUpperCase();

    let selectedDecision = null;
    let evaluatedEntryLaneDecisions = [];
    if (alreadyEvaluated) {
      selectedDecision = {
        rule_lane: activePosition ? closeRuleLane : selectedEntryRuleLane,
        evaluator_id: 'reference_point_once_guard',
        action: 'ALREADY_EVALUATED',
        action_label: '評価済み',
        status_label: '重複実行なし',
        summary: '同じM5確定足は既に評価済みです。',
        reason_codes: ['REFERENCE_POINT_ALREADY_EVALUATED'],
        rule_ids: ['rule_m5_reference_once_only'],
        permission: 'BLOCKED',
        entry_opportunity: null,
        bar_touch: { stop_touched: false, target_touched: false, ambiguous: false }
      };
    } else if (errors.length) {
      selectedDecision = {
        rule_lane: activePosition ? closeRuleLane : selectedEntryRuleLane,
        evaluator_id: 'm5_execution_input_guard',
        action: 'BLOCKED',
        action_label: '実行不可',
        status_label: '入力エラー',
        summary: errors.join(' / '),
        reason_codes: ['M5_EXECUTION_INPUT_INVALID'],
        rule_ids: ['rule_m5_execution_input_valid'],
        permission: 'BLOCKED',
        entry_opportunity: null,
        bar_touch: { stop_touched: false, target_touched: false, ambiguous: false }
      };
    } else if (activePosition) {
      selectedDecision = evaluateCloseRuleLane(closeRuleLane, {
        activePosition,
        activeTrade,
        currentBar,
        m5State,
        timeframeSnapshot,
        referenceMs,
        referenceTime,
        policy
      });
    } else {
      const inputByLane = {};
      for (const ruleLane of lanePolicy.enabled_entry_rule_lanes) {
        const laneContext = entryLaneContexts[ruleLane];
        if (!laneContext) continue;
        inputByLane[ruleLane] = {
          portfolio: lifecycle.portfolio,
          referenceMs,
          referenceTime,
          price,
          direction: laneContext.direction,
          confirmationSide: laneContext.confirmationSide,
          normalFacts: normalEntryV08,
          m5State,
          expansionLiteFacts,
          currentBar,
          distanceRaw: laneContext.distanceRaw,
          dowConfirmation,
          entryResolution: laneContext.entryResolution,
          entryAnchor: laneContext.entryAnchor,
          anchorPrice: laneContext.anchorPrice,
          r2Touch: laneContext.r2Touch,
          r3Touch: laneContext.r3Touch,
          policy,
          minEntryLabel: laneContext.minEntryLabel,
          hsiNotReachedReasonCode: laneContext.hsiNotReachedReasonCode,
          upperDecision: upperSnapshot,
          timeframeSnapshot
        };
      }
      const orchestration = evaluateEnabledEntryRuleLanes(lanePolicy, inputByLane);
      selectedDecision = orchestration.selected_decision;
      if (orchestration.selected_lane) selectEntryLaneContext(orchestration.selected_lane);
      evaluatedEntryLaneDecisions = orchestration.lane_decisions || [];
    }

    const decisionRuleLane = selectedDecision?.rule_lane || activeEntryLane || RULE_LANE_NORMAL;
    if (!activePosition) selectEntryLaneContext(decisionRuleLane);
    const action = selectedDecision?.action || 'WAIT';
    const actionLabel = selectedDecision?.action_label || '待機';
    const statusLabel = selectedDecision?.status_label || '条件未成立';
    const summary = selectedDecision?.summary || 'Rule Lane判定結果がありません。';
    const reasonCodes = uniqueStrings(selectedDecision?.reason_codes || []);
    const ruleIds = uniqueStrings(selectedDecision?.rule_ids || []);
    const entryOpportunity = selectedDecision?.entry_opportunity || null;
    const selectedNormalDowConfirmation = decisionRuleLane === RULE_LANE_NORMAL
      ? (selectedDecision?.effective_dow_confirmation || (entryOpportunity?.dow_confirmation_id ? {
          confirmation_id: entryOpportunity.dow_confirmation_id,
          direction: String(entryOpportunity.direction || '').toUpperCase() === 'SHORT' ? 'DOWN' : 'UP',
          confirmed_at: entryOpportunity.confirmed_at || null,
          confirmed_at_ms: numberOrNull(entryOpportunity.confirmed_at_ms),
          anchor_point_id: entryOpportunity.anchor_id || null,
          anchor_price: numberOrNull(entryOpportunity.anchor_price),
          anchor_time: entryOpportunity.anchor_time || null,
          breakout_threshold_price: numberOrNull(entryOpportunity.breakout_threshold_price),
          trigger_point_id: entryOpportunity.trigger_point_id || null
        } : dowConfirmation))
      : dowConfirmation;
    const selectedNormalEntryAnchor = decisionRuleLane === RULE_LANE_NORMAL
      ? (selectedDecision?.effective_entry_anchor || (entryOpportunity?.anchor_id ? {
          anchor_id: entryOpportunity.anchor_id,
          price: numberOrNull(entryOpportunity.anchor_price),
          time: entryOpportunity.anchor_time || null,
          dow_confirmation_id: entryOpportunity.dow_confirmation_id || null
        } : entryAnchor))
      : entryAnchor;
    const selectedNormalAnchorPrice = decisionRuleLane === RULE_LANE_NORMAL
      ? (numberOrNull(selectedDecision?.effective_anchor_price) ?? numberOrNull(entryOpportunity?.anchor_price) ?? numberOrNull(anchorPrice))
      : numberOrNull(anchorPrice);
    const selectedNormalConfirmationSide = decisionRuleLane === RULE_LANE_NORMAL
      ? String(selectedDecision?.effective_confirmation_side || entryOpportunity?.direction || confirmationSide || '').toUpperCase()
      : confirmationSide;
    context.entryOpportunity = entryOpportunity;
    context.ruleLane = decisionRuleLane;
    context.evaluatorId = selectedDecision?.evaluator_id || null;
    const barTouch = selectedDecision?.bar_touch || { stop_touched: false, target_touched: false, ambiguous: false };
    const normalPermission = decisionRuleLane === RULE_LANE_NORMAL
      ? String(selectedDecision?.permission || (normalEntryV08.entry_direction_ready && normalEntryV08.cycle_guard_passed ? 'ALLOW_SEARCH' : 'BLOCKED')).toUpperCase()
      : 'BLOCKED';
    const expansionLitePermission = decisionRuleLane === RULE_LANE_EXPANSION_LITE
      ? String(selectedDecision?.permission || (expansionLiteFacts.entry_direction_ready ? 'ALLOW_SEARCH' : 'BLOCKED')).toUpperCase()
      : 'BLOCKED';
    const addOnPermission = activePosition && closeRuleLane === RULE_LANE_EXPANSION_LITE
      ? (action === 'ADD_ON' ? 'ALLOW_ADD_ON' : 'MONITOR')
      : 'BLOCKED';
    const triggerAligned = selectedDecision?.trigger_aligned ?? (decisionRuleLane === RULE_LANE_EXPANSION_LITE
      ? expansionLiteFacts.entry_direction_ready === true
      : normalEntryV08.entry_direction_ready === true);
    const noTrade = selectedDecision?.no_trade ?? (decisionRuleLane === RULE_LANE_EXPANSION_LITE
      ? !expansionLiteFacts.entry_direction_ready
      : (normalEntryV08.h1_cycle_late || !normalEntryV08.entry_direction_ready));
    const confirmationEventOnCurrentBar = selectedDecision?.confirmation_event_on_current_bar === true;

    const trigger = {
      action,
      action_label: actionLabel,
      status_label: statusLabel,
      summary,
      rule_lane: decisionRuleLane,
      evaluator_id: selectedDecision?.evaluator_id || null,
      decision_scope: activePosition ? 'CLOSE' : 'ENTRY',
      selected_entry_rule_lane: selectedEntryRuleLane,
      enabled_entry_rule_lanes: lanePolicy.enabled_entry_rule_lanes,
      evaluated_entry_rule_lanes: evaluatedEntryLaneDecisions.map(item => item?.rule_lane).filter(Boolean),
      entry_lane_decisions: evaluatedEntryLaneDecisions.map(item => ({ rule_lane: item?.rule_lane || null, action: item?.action || 'WAIT', status_label: item?.status_label || '', reason_codes: uniqueStrings(item?.reason_codes || []) })),
      active_trade_rule_lane: closeRuleLane,
      shared_fact_source: lanePolicy.shared_fact_source,
      close_lane_source: lanePolicy.close_lane_source,
      direction,
      m5_trend_state: m5State?.trend_state || 'UNDETERMINED',
      h1_t3_direction: normalEntryV08.h1_t3_direction,
      h1_t3_position: normalEntryV08.h1_t3_position,
      h1_t3_value: normalEntryV08.h1_t3_value,
      h1_close: normalEntryV08.h1_close,
      h4_t3_direction: normalEntryV08.h4_t3_direction,
      h4_t3_position: normalEntryV08.h4_t3_position,
      h4_t3_value: normalEntryV08.h4_t3_value,
      h4_close: normalEntryV08.h4_close,
      h4_cycle_phase: normalEntryV08.h4_cycle_phase,
      h1_cycle_phase: normalEntryV08.h1_cycle_phase,
      normal_entry_rule_version: NORMAL_RULE_VERSION,
      trigger_aligned: triggerAligned,
      no_trade: noTrade,
      legacy_upper_no_trade: upperNoTrade,
      current_price: price,
      entry_anchor_id: decisionRuleLane === RULE_LANE_NORMAL ? (selectedNormalEntryAnchor?.anchor_id || null) : (entryResolution?.anchor_id || null),
      entry_anchor_price: decisionRuleLane === RULE_LANE_NORMAL ? selectedNormalAnchorPrice : anchorPrice,
      entry_anchor_policy: decisionRuleLane === RULE_LANE_EXPANSION_LITE ? 'EXPANSION_LITE_DOW_CONFIRMATION_ANCHOR_FIXED_FOR_TRADE' : 'NORMAL_RULE_LANE_DOW_CONFIRMATION_PREVIOUS_SWING',
      entry_anchor_reason_codes: [...(entryResolution?.reason_codes || [])],
      dow_confirmation_id: decisionRuleLane === RULE_LANE_NORMAL ? (selectedNormalDowConfirmation?.confirmation_id || null) : (dowConfirmation?.confirmation_id || null),
      dow_confirmation_at: decisionRuleLane === RULE_LANE_NORMAL ? (selectedNormalDowConfirmation?.confirmed_at || null) : (dowConfirmation?.confirmed_at || null),
      dow_confirmation_at_ms: decisionRuleLane === RULE_LANE_NORMAL ? numberOrNull(selectedNormalDowConfirmation?.confirmed_at_ms) : numberOrNull(dowConfirmation?.confirmed_at_ms),
      entry_opportunity_id: entryOpportunity?.opportunity_id || null,
      entry_opportunity_status: entryOpportunity?.status || null,
      entry_opportunity_terminal_reason_code: entryOpportunity?.terminal_reason_code || null,
      next_normal_entry_requires_new_confirmation_after_previous_close: true,
      normal_hsi_anchor_lifecycle_status: m5ExecutionEnsureNormalAnchorLifecycle(lifecycle.portfolio).status,
      normal_hsi_active_anchor_id: m5ExecutionEnsureNormalAnchorLifecycle(lifecycle.portfolio).active_anchor_id,
      normal_hsi_last_retired_anchor_id: m5ExecutionEnsureNormalAnchorLifecycle(lifecycle.portfolio).last_retired_anchor_id,
      normal_hsi_last_retired_at: m5ExecutionEnsureNormalAnchorLifecycle(lifecycle.portfolio).last_retired_at,
      entry_guard: cloneJsonValue(selectedDecision?.entry_guard || null),
      h4_wave_hsi_facts: cloneJsonValue(selectedDecision?.entry_guard?.facts || null),
      normal_close_miss_policy: cloneJsonValue(policy?.normal_close_miss_policy || null),
      normal_stop_plan: cloneJsonValue(selectedDecision?.normal_stop_plan || entryOpportunity?.normal_stop_plan || null),
      normal_dow_structure_break: cloneJsonValue(m5ExecutionNormalDowStructureBreak(m5State)),
      post_entry_dow_break_observation: cloneJsonValue(selectedDecision?.post_entry_dow_break_observation || null),
      close_event_emitted_for_dow_break: selectedDecision?.post_entry_dow_break_observation ? false : null,
      hsi_distance_raw: distanceRaw,
      hsi_entry_min_raw: minEntryRaw,
      hsi_entry_min_label: minEntryLabel,
      hsi_current_band: hsiBand?.current?.label || null,
      hsi_entry_touch_label: decisionRuleLane === RULE_LANE_EXPANSION_LITE ? r3Touch.label : r2Touch.entry_label,
      hsi_entry_touch_price: decisionRuleLane === RULE_LANE_EXPANSION_LITE ? r3Touch.price : (numberOrNull(entryOpportunity?.r2_price) ?? numberOrNull(selectedDecision?.execution_candidate?.entry_price) ?? r2Touch.entry_price),
      hsi_entry_touch_detected: decisionRuleLane === RULE_LANE_EXPANSION_LITE ? r3Touch.touched === true : Boolean(entryOpportunity?.first_r2_touch_at_ms || selectedDecision?.action === 'ENTRY'),
      hsi_target_touch_price: numberOrNull(entryOpportunity?.target_price ?? barTouch?.target_price),
      hsi_target_touch_detected: barTouch?.target_touched === true,
      dow_confirmation_event_on_current_bar: confirmationEventOnCurrentBar,
      entry_execution_mode: entryOpportunity?.entry_execution_mode || null,
      entry_execution_price: numberOrNull(entryOpportunity?.entry_execution_price),
      dow_breakout_threshold_price: numberOrNull(entryOpportunity?.breakout_threshold_price ?? dowConfirmation?.breakout_threshold_price),
      confirmation_required_price: numberOrNull(entryOpportunity?.confirmation_required_price),
      hsi_next_boundary: entryOpportunity?.target_label || activePosition?.target_plan?.next_target_label || hsiBand?.next?.label || null,
      expansion_lite_rule_version: decisionRuleLane === RULE_LANE_EXPANSION_LITE ? EXPANSION_LITE_RULE_VERSION : null,
      expansion_lite_h1_cycle_entry_allowed: decisionRuleLane === RULE_LANE_EXPANSION_LITE ? expansionLiteFacts.h1_cycle_entry_allowed : null,
      expansion_lite_h1_cycle_elapsed_bars: decisionRuleLane === RULE_LANE_EXPANSION_LITE ? expansionLiteFacts.h1_cycle_elapsed_bars : null,
      expansion_lite_h1_cycle_entry_allowed_max_bars: decisionRuleLane === RULE_LANE_EXPANSION_LITE ? expansionLiteFacts.h1_cycle_entry_allowed_max_bars : null,
      expansion_lite_h1_cycle_front_half: decisionRuleLane === RULE_LANE_EXPANSION_LITE ? expansionLiteFacts.h1_cycle_front_half : null,
      expansion_lite_h1_cycle_front_half_limit: decisionRuleLane === RULE_LANE_EXPANSION_LITE ? expansionLiteFacts.h1_cycle_front_half_limit : null,
      expansion_lite_day_cycle_position_used: false,
      exit_type: selectedDecision?.exit_type || null,
      exit_reason_code: selectedDecision?.exit_reason_code || null,
      add_on_levels: cloneJsonValue(selectedDecision?.add_on_levels || []),
      permissions: decisionRuleLane === RULE_LANE_NORMAL
        ? { normal_entry: normalPermission }
        : decisionRuleLane === RULE_LANE_EXPANSION_LITE
          ? { expansion_lite: expansionLitePermission, add_on: addOnPermission }
          : { expansion_entry: expansionPermission },
      reason_codes: reasonCodes,
      rule_ids: ruleIds
    };
    if (selectedDecision?.post_entry_dow_break_observation && activeTrade) {
      const observation = selectedDecision.post_entry_dow_break_observation;
      const observationId = String(observation.break_event_id || observation.break_at_ms || '');
      activeTrade.post_entry_dow_break_observation_ids = uniqueStrings([
        ...(activeTrade.post_entry_dow_break_observation_ids || []),
        observationId
      ]);
      activeTrade.post_entry_dow_break_observations = [
        ...(activeTrade.post_entry_dow_break_observations || []),
        cloneJsonValue(observation)
      ];
    }
    const beforePortfolio = cloneJsonValue(lifecycle.portfolio);
    const triggerEvent = m5ExecutionCreateTriggerEvent(context, trigger, lifecycle);
    if (!alreadyEvaluated) lifecycle.decision_events.push(triggerEvent);
    let executionEvent = null;
    if (!alreadyEvaluated && !errors.length) {
      if (context.ruleLane === RULE_LANE_NORMAL && action === 'ENTRY') {
        const selectedEntryPrice = numberOrNull(entryOpportunity?.entry_execution_price)
          ?? numberOrNull(selectedDecision?.execution_candidate?.entry_price)
          ?? r2Touch.entry_price;
        const selectedEntryDistanceRaw = m5ExecutionDistanceRaw(selectedEntryPrice, selectedNormalAnchorPrice, selectedNormalConfirmationSide, policy);
        const selectedEntryResolution = selectedNormalEntryAnchor
          ? { status: 'RESOLVED_REFERENCE', anchor_id: selectedNormalEntryAnchor.anchor_id, anchor: selectedNormalEntryAnchor }
          : entryResolution;
        const entryContext = {
          ...context,
          direction: selectedNormalConfirmationSide,
          confirmationSide: selectedNormalConfirmationSide,
          price: selectedEntryPrice,
          entryResolution: selectedEntryResolution,
          entryAnchor: selectedNormalEntryAnchor,
          anchorPrice: selectedNormalAnchorPrice,
          distanceRaw: selectedEntryDistanceRaw,
          hsiBand: m5ExecutionHsiBand(selectedEntryDistanceRaw, policy),
          dowConfirmation: selectedNormalDowConfirmation,
          causeEventIds: uniqueStrings([...(context.causeEventIds || []), selectedNormalDowConfirmation?.confirmation_id]),
          entryOpportunity
        };
        const created = m5ExecutionNewTrade(lifecycle.portfolio, entryContext, triggerEvent, 'NORMAL', policy);
        const position = created.positions[0];
        if (entryOpportunity) entryOpportunity.entry_trade_id = created.trade.trade_id;
        const afterPortfolio = cloneJsonValue(lifecycle.portfolio);
        const entryExecutionMode = String(entryOpportunity?.entry_execution_mode || 'FIRST_R2_TOUCH_AFTER_CONFIRMATION');
        const entryDisplayLabel = entryExecutionMode === 'DOW_BREAKOUT_CONFIRMATION_R2_READY' ? 'Dow突破確定即Entry' : 'R2 Entry';
        executionEvent = m5ExecutionEvent(entryContext, 'entry', `通常Entry #${created.trade.normal_entry_sequence_no || created.trade.sequence} ${entryContext.direction} / ${position?.units_open || 0}単位 / ${entryDisplayLabel} ${round3(entryContext.price)}`, [...trigger.rule_ids], [...trigger.reason_codes, 'POSITION_LIFECYCLE_OPENED'], [triggerEvent.event_id, selectedNormalDowConfirmation?.confirmation_id].filter(Boolean), beforePortfolio, afterPortfolio, { trade_id: created.trade.trade_id, position_ids: [position.position_id], rule_lane: RULE_LANE_NORMAL, evaluator_id: NORMAL_ENTRY_EVALUATOR_ID, execution: { rule_lane: RULE_LANE_NORMAL, evaluator_id: NORMAL_ENTRY_EVALUATOR_ID, close_evaluator_id: NORMAL_CLOSE_EVALUATOR_ID, action, normal_entry_sequence_no: created.trade.normal_entry_sequence_no, side: entryContext.direction, units: position.units_open, price: entryContext.price, entry_price: entryContext.price, entry_level: entryExecutionMode === 'DOW_BREAKOUT_CONFIRMATION_R2_READY' ? 'R2_OR_MORE_AT_DOW_BREAKOUT_CONFIRMATION' : 'R2', entry_execution_mode: entryExecutionMode, target_price: created.targetPrice, target_label: created.trade.target_label || position?.target_plan?.next_target_label || null, entry_timeframe: 'M5', entry_anchor_id: entryContext.entryAnchor?.anchor_id || null, entry_anchor_price: entryContext.anchorPrice, entry_anchor_time: entryContext.entryAnchor?.time || entryContext.entryAnchor?.pivot_time || null, dow_confirmation_id: selectedNormalDowConfirmation?.confirmation_id || null, dow_breakout_threshold_price: numberOrNull(selectedNormalDowConfirmation?.breakout_threshold_price), entry_opportunity_id: entryOpportunity?.opportunity_id || null, stop_basis: created.trade.risk_profile?.stop_basis || 'TARGET_DISTANCE_RATIO_WITH_HSI_ANCHOR_HARD_LIMIT', stop_price: created.trade.risk_profile?.stop_price ?? created.stopPlan?.stop_price, max_loss_to_reward_ratio: created.stopPlan?.max_loss_to_reward_ratio ?? null, reward_distance: created.stopPlan?.reward_distance ?? null, max_loss_distance: created.stopPlan?.max_loss_distance ?? null, ratio_stop_price: created.stopPlan?.ratio_stop_price ?? null, hsi_anchor_hard_limit_price: created.stopPlan?.hsi_anchor_hard_limit_price ?? entryContext.anchorPrice, hsi_anchor_hard_limit_applied: created.stopPlan?.hsi_anchor_hard_limit_applied === true, initial_units: created.trade.risk_profile?.initial_units ?? position.units_initial, unit_base_currency_amount: created.trade.risk_profile?.unit_base_currency_amount || 1000, initial_risk_jpy: created.trade.risk_profile?.initial_risk_jpy ?? null, close_policy: 'SINGLE_CLOSE', normal_hsi_anchor_lifecycle_status: created.normalAnchorLifecycle?.status || 'ACTIVE', cumulative_realized_profit_jpy: m5ExecutionPortfolioRunRealizedJpy(lifecycle.portfolio, policy), trade_cumulative_realized_profit_jpy: 0, profit_vs_initial_risk_pct: 0, risk_multiple: 0 } });
        created.trade.entry_event_id = executionEvent.event_id;
      } else if (context.ruleLane === RULE_LANE_EXPANSION_LITE && action === 'ENTRY') {
        const selectedEntryPrice = numberOrNull(selectedDecision?.execution_candidate?.price)
          ?? numberOrNull(entryOpportunity?.entry_execution_price)
          ?? r3Touch.price;
        const selectedEntryDistanceRaw = m5ExecutionDistanceRaw(selectedEntryPrice, anchorPrice, confirmationSide, policy);
        const entryContext = {
          ...context,
          direction: confirmationSide,
          price: selectedEntryPrice,
          distanceRaw: selectedEntryDistanceRaw,
          hsiBand: m5ExecutionHsiBand(selectedEntryDistanceRaw, policy),
          entryOpportunity
        };
        const created = m5ExecutionNewExpansionLiteTrade(lifecycle.portfolio, entryContext, triggerEvent, policy);
        const position = created.positions[0];
        if (entryOpportunity) entryOpportunity.entry_trade_id = created.trade.trade_id;
        const afterPortfolio = cloneJsonValue(lifecycle.portfolio);
        executionEvent = m5ExecutionEvent(
          entryContext,
          'entry',
          `Expansion-Lite Entry ${entryContext.direction} / ${position?.units_open || 0}単位 / R3 ${round3(entryContext.price)}`,
          [...trigger.rule_ids],
          [...trigger.reason_codes, 'EXPANSION_LITE_POSITION_LIFECYCLE_OPENED'],
          [triggerEvent.event_id, dowConfirmation?.confirmation_id].filter(Boolean),
          beforePortfolio,
          afterPortfolio,
          {
            trade_id: created.trade.trade_id,
            position_ids: [position.position_id],
            rule_lane: RULE_LANE_EXPANSION_LITE,
            evaluator_id: EXPANSION_LITE_ENTRY_EVALUATOR_ID,
            execution: {
              rule_lane: RULE_LANE_EXPANSION_LITE,
              evaluator_id: EXPANSION_LITE_ENTRY_EVALUATOR_ID,
              close_evaluator_id: EXPANSION_LITE_CLOSE_EVALUATOR_ID,
              action: 'ENTRY',
              side: entryContext.direction,
              units: position.units_open,
              price: entryContext.price,
              entry_price: entryContext.price,
              entry_level: 'R3',
              entry_execution_mode: entryOpportunity?.entry_execution_mode || 'FIRST_R3_TOUCH_AFTER_DOW_CONFIRMATION',
              target_price: created.targetPrice,
              target_label: 'R5',
              entry_timeframe: 'M5',
              entry_anchor_id: entryContext.entryAnchor?.anchor_id || null,
              entry_anchor_price: entryContext.anchorPrice,
              entry_anchor_time: entryContext.entryAnchor?.pivot_time || null,
              dow_confirmation_id: dowConfirmation?.confirmation_id || null,
              entry_opportunity_id: entryOpportunity?.opportunity_id || null,
              close_policy: 'EXPANSION_LITE_ALL_CLOSE',
              initial_units: position.units_initial,
              unit_base_currency_amount: position.risk_profile?.unit_base_currency_amount || 1000,
              initial_risk_jpy: position.risk_profile?.initial_risk_jpy ?? null,
              chart_marker_label: 'Expansion-Lite Entry',
              cumulative_realized_profit_jpy: m5ExecutionPortfolioRunRealizedJpy(lifecycle.portfolio, policy)
            }
          }
        );
        created.trade.entry_event_id = executionEvent.event_id;
      } else if (action === 'ADD_ON') {
        const trade = lifecycle.portfolio.trades.find(item => item.trade_id === lifecycle.portfolio.active_trade_id);
        if (context.ruleLane === RULE_LANE_EXPANSION_LITE && trade) {
          const levels = selectedDecision?.add_on_levels || [];
          const positions = m5ExecutionAddExpansionLitePositions(lifecycle.portfolio, trade, context, levels, policy);
          const totalUnits = positions.reduce((sum, position) => sum + Number(position.units_open || 0), 0);
          const labels = levels.map(level => level.label).join(' / ');
          const afterPortfolio = cloneJsonValue(lifecycle.portfolio);
          executionEvent = m5ExecutionEvent(
            { ...context, price: positions[positions.length - 1]?.entry_price ?? context.price },
            'add_on',
            `Expansion-Lite Add-on ${labels} / ${totalUnits}単位追加`,
            [...trigger.rule_ids],
            [...trigger.reason_codes, 'EXPANSION_LITE_ADD_ON_POSITIONS_OPENED'],
            [triggerEvent.event_id],
            beforePortfolio,
            afterPortfolio,
            {
              trade_id: trade.trade_id,
              position_ids: positions.map(position => position.position_id),
              rule_lane: RULE_LANE_EXPANSION_LITE,
              evaluator_id: EXPANSION_LITE_CLOSE_EVALUATOR_ID,
              execution: {
                rule_lane: RULE_LANE_EXPANSION_LITE,
                evaluator_id: EXPANSION_LITE_CLOSE_EVALUATOR_ID,
                close_evaluator_id: EXPANSION_LITE_CLOSE_EVALUATOR_ID,
                action: 'ADD_ON',
                side: trade.side,
                units: totalUnits,
                price: positions[positions.length - 1]?.entry_price ?? context.price,
                add_on_levels: levels.map(level => level.label),
                consumed_add_on_levels: [...(trade.consumed_add_on_levels || [])],
                target_label: 'R5',
                target_price: trade.target_price,
                entry_anchor_id: trade.entry_anchor_id,
                entry_anchor_price: trade.entry_anchor_price,
                chart_marker_label: labels ? `Expansion-Lite Add-on ${labels}` : 'Expansion-Lite Add-on'
              }
            }
          );
        } else {
          const units = Math.max(1, Number(policy?.position_sizing?.add_on_units || 2));
          const positionId = `${trade?.trade_id || 'trade'}_addon_${String(lifecycle.portfolio.positions.filter(position => position.role === 'ADD_ON').length + 1).padStart(2, '0')}`;
          const target = hsiBand?.next || null;
          const position = {
            position_id: positionId,
            trade_id: trade?.trade_id || lifecycle.portfolio.active_trade_id,
            role: 'ADD_ON', side: context.direction, units_initial: units, units_open: units,
            entry_mode: 'ADD_ON', entry_timeframe: 'M5', management_timeframe: 'H1', management_timeframe_cap: 'DAY',
            entry_time: context.referenceTime, entry_ms: context.referenceMs, entry_price: context.price,
            entry_anchor_id: entryResolution?.anchor_id || null, entry_anchor_price: anchorPrice, status: 'OPEN',
            risk_profile: m5ExecutionRiskProfile(context.price, anchorPrice, units, policy),
            invalidation_rule: { rule_id: 'rule_position_structural_anchor_break', type: 'STRUCTURAL_ANCHOR_BREAK', anchor_id: entryResolution?.anchor_id || null, invalidation_price: anchorPrice, direction: context.direction },
            target_plan: { mode: 'NEXT_HSI_BOUNDARY', entry_distance_raw: distanceRaw, entry_band: hsiBand?.current?.label || null, next_target_label: target?.label || null, next_target_raw: target?.raw ?? null, next_target_price: target ? m5ExecutionTargetPrice(anchorPrice, context.direction, target.raw, policy) : null, partial_close_units: units },
            promotion_history: [], closed_at: null, close_price: null, close_class: null
          };
          lifecycle.portfolio.positions.push(position);
          if (trade) trade.position_ids.push(positionId);
          const afterPortfolio = cloneJsonValue(lifecycle.portfolio);
          executionEvent = m5ExecutionEvent(context, 'add_on', `買い増し ${context.direction} / ${units}単位 / ${round3(context.price)}`, [...trigger.rule_ids], [...trigger.reason_codes, 'ADD_ON_POSITION_OPENED'], [triggerEvent.event_id], beforePortfolio, afterPortfolio, { trade_id: trade?.trade_id, position_ids: [positionId], rule_lane: RULE_LANE_EXPANSION, evaluator_id: EXPANSION_ENTRY_EVALUATOR_ID, execution: { rule_lane: RULE_LANE_EXPANSION, evaluator_id: EXPANSION_ENTRY_EVALUATOR_ID, close_evaluator_id: EXPANSION_CLOSE_EVALUATOR_ID, action: 'ADD_ON', side: context.direction, units, price: context.price, target_label: position.target_plan?.next_target_label || null, entry_anchor_id: position.entry_anchor_id } });
        }
      } else if (action === 'FULL_CLOSE' || action === 'STOP_CLOSE') {
        const isExpansionLiteClose = closeRuleLane === RULE_LANE_EXPANSION_LITE;
        const isStop = !isExpansionLiteClose && action === 'STOP_CLOSE';
        const closeClass = isExpansionLiteClose
          ? String(selectedDecision?.exit_type || 'EXPANSION_LITE_EXIT')
          : (isStop ? 'STOP_CLOSE' : 'CLOSE_OK');
        const executionPrice = isExpansionLiteClose
          ? numberOrNull(selectedDecision?.execution_price)
          : (isStop
            ? numberOrNull(barTouch.stop_execution_price) ?? barTouch.stop_price
            : numberOrNull(barTouch.target_execution_price) ?? barTouch.target_price);
        const closeContext = { ...context, direction: activeTrade?.side || context.direction, price: executionPrice ?? context.price };
        const closedUnits = openTradePositions.reduce((sum, position) => sum + Number(position.units_open || 0), 0);
        const closed = m5ExecutionClosePositions(lifecycle.portfolio, openTradePositions, closeContext, closeClass);
        if (closed.trade) closed.trade.realized_profit_jpy = Number(closed.trade.realized_price_delta_units || 0) * m5ExecutionValuationPolicy(policy).unit_base_currency_amount;
        const financial = m5ExecutionFinancialSnapshot(closed.trade, closed.realized, policy, lifecycle.portfolio);
        const reachedTargetLabel = isExpansionLiteClose
          ? (selectedDecision?.exit_type === 'TARGET_EXIT' ? 'R5' : null)
          : (isStop ? null : activePosition?.target_plan?.next_target_label || null);
        const afterPortfolio = cloneJsonValue(lifecycle.portfolio);
        const eventType = isStop ? 'stop_close' : 'close';
        const eventSummary = isExpansionLiteClose
          ? `${selectedDecision?.action_label || selectedDecision?.exit_type || 'Expansion-Lite Exit'} / ${closedUnits}単位全決済 / ${round3(closeContext.price)}`
          : (isStop
            ? `倍率Stop / ${closedUnits}単位全決済 / ${round3(closeContext.price)}`
            : `${reachedTargetLabel || '次HSI境界'}到達 / ${closedUnits}単位全決済 / ${round3(closeContext.price)}`);
        const closeRuleIds = isExpansionLiteClose
          ? [...trigger.rule_ids]
          : [...trigger.rule_ids, 'rule_normal_hsi_anchor_retired_immediately_on_close'];
        const closeReasonCodes = isExpansionLiteClose
          ? [...trigger.reason_codes, closeClass]
          : [...trigger.reason_codes, closeClass, 'NORMAL_HSI_ANCHOR_RETIRED_ON_CLOSE'];
        executionEvent = m5ExecutionEvent(closeContext, eventType, eventSummary, closeRuleIds, closeReasonCodes, [triggerEvent.event_id], beforePortfolio, afterPortfolio, {
          trade_id: closed.trade?.trade_id,
          position_ids: openTradePositions.map(position => position.position_id),
          rule_lane: closeRuleLane,
          evaluator_id: selectedDecision?.evaluator_id || null,
          execution: {
            rule_lane: closeRuleLane,
            evaluator_id: selectedDecision?.evaluator_id || null,
            action,
            units: closedUnits,
            price: closeContext.price,
            entry_price: closed.trade?.entry_price ?? activePosition?.entry_price ?? null,
            realized_price_delta_units: closed.realized,
            close_class: closeClass,
            exit_type: isExpansionLiteClose ? selectedDecision?.exit_type || null : null,
            exit_reason_code: isExpansionLiteClose ? selectedDecision?.exit_reason_code || null : null,
            reached_target_label: reachedTargetLabel,
            target_label: reachedTargetLabel,
            target_price: barTouch.target_price ?? closed.trade?.target_price ?? null,
            stop_basis: isExpansionLiteClose ? 'EXPANSION_LITE_DEFINED_EXIT' : (closed.trade?.risk_profile?.stop_basis || activePosition?.risk_profile?.stop_basis || 'TARGET_DISTANCE_RATIO_WITH_HSI_ANCHOR_HARD_LIMIT'),
            stop_price: barTouch.stop_price ?? activePosition?.invalidation_rule?.invalidation_price ?? null,
            max_loss_to_reward_ratio: isExpansionLiteClose ? null : (closed.trade?.close_miss_plan?.max_loss_to_reward_ratio ?? activePosition?.close_miss_plan?.max_loss_to_reward_ratio ?? null),
            ratio_stop_price: isExpansionLiteClose ? null : (closed.trade?.close_miss_plan?.ratio_stop_price ?? activePosition?.close_miss_plan?.ratio_stop_price ?? null),
            hsi_anchor_hard_limit_price: isExpansionLiteClose ? null : (closed.trade?.close_miss_plan?.hsi_anchor_hard_limit_price ?? activePosition?.close_miss_plan?.hsi_anchor_hard_limit_price ?? null),
            hsi_anchor_hard_limit_applied: isExpansionLiteClose ? false : (closed.trade?.close_miss_plan?.hsi_anchor_hard_limit_applied === true || activePosition?.close_miss_plan?.hsi_anchor_hard_limit_applied === true),
            initial_units: closed.trade?.risk_profile?.initial_units ?? closedUnits,
            close_policy: isExpansionLiteClose ? 'EXPANSION_LITE_ALL_CLOSE' : 'SINGLE_CLOSE',
            ambiguous_stop_target: barTouch.ambiguous === true,
            target_direction_valid: barTouch.target_direction_valid !== false,
            stop_fill_mode: barTouch.stop_fill_mode || null,
            target_fill_mode: barTouch.target_fill_mode || null,
            t3_fill_mode: barTouch.t3_fill_mode || null,
            execution_price_within_bar: closeContext.price != null && barTouch.high != null && barTouch.low != null
              ? closeContext.price >= Number(barTouch.low) - 1e-9 && closeContext.price <= Number(barTouch.high) + 1e-9
              : null,
            bar_high: barTouch.high ?? null,
            bar_low: barTouch.low ?? null,
            t3_price: barTouch.t3_price ?? null,
            structural_broken: barTouch.structural_broken === true,
            chart_marker_label: isExpansionLiteClose ? selectedDecision?.action_label || null : null,
            normal_hsi_anchor_retired: isExpansionLiteClose ? false : closed.normalAnchorRetirement?.retired === true,
            normal_hsi_anchor_retired_anchor_id: isExpansionLiteClose ? null : closed.normalAnchorRetirement?.anchor_id || null,
            normal_hsi_anchor_retired_confirmation_id: isExpansionLiteClose ? null : closed.normalAnchorRetirement?.confirmation_id || null,
            normal_hsi_anchor_retired_at: isExpansionLiteClose ? null : closed.normalAnchorRetirement?.retired_at || closeContext.referenceTime,
            normal_hsi_anchor_retired_at_ms: isExpansionLiteClose ? null : closed.normalAnchorRetirement?.retired_at_ms ?? closeContext.referenceMs,
            next_required_state: isExpansionLiteClose ? 'NEW_EXPANSION_LITE_DOW_CONFIRMATION' : closed.normalAnchorRetirement?.next_required_state || 'NEW_M5_DOW_CONFIRMATION_AFTER_CLOSE',
            ...financial
          }
        });
        if (closed.trade) closed.trade.terminal_close_event_id = executionEvent.event_id;
      }
    }
    if (executionEvent) lifecycle.execution_events.push(executionEvent);
    if (!alreadyEvaluated) {
      lifecycle.portfolio.last_evaluated_reference_key = referenceKey;
      lifecycle.portfolio.last_evaluated_reference_ms = referenceMs;
      lifecycle.portfolio.evaluated_reference_count = Number(lifecycle.portfolio.evaluated_reference_count || 0) + 1;
      // Batch継続に必要なのは直近参照点だけ。全履歴配列を積み続けない。
      lifecycle.portfolio.evaluated_reference_keys = [referenceKey];
    }
    lifecycle.portfolio.status = m5ExecutionOpenPositions(lifecycle.portfolio).length ? 'OPEN' : 'FLAT';
    lifecycle.trigger_evaluation = trigger;
    lifecycle.run_result = m5ExecutionRunResult(lifecycle);
    lifecycle.validation = { valid: errors.length === 0, checked_at: nowLocalIso(), errors, warnings, no_lookahead: m5State?.no_lookahead === true && policy.no_lookahead === true, previous_state_policy: previousInfo.status };
    lifecycle.status = errors.length ? 'invalid' : executionEvent ? 'executed' : 'evaluated_no_execution';
    lifecycle.teacher_guard = 'v0.21〜v0.23対応。Day Up/H4 Down/R5 Short Guardと、NORMAL H4同方向R4 GuardをEntry直前に評価します。NORMALのWAITING_R2はEntry前のM5 Dow構造崩壊で失効し、後からR2へ到達してもEntryしません。Entry後のDow崩壊は別問題であり、それだけでは自動Closeしません。Normal CloseMiss StopはEntry時のTarget距離×JSON固定max_loss_to_reward_ratioで決定し、HSI起点をHard Limitとして固定します。Rule Lane間の条件・起点・建玉・Close Evaluatorは流用しません。';
    return lifecycle;
  }

  function m5ExecutionOpenTradeIdForLane(portfolio, ruleLane) {
    const lane = String(ruleLane || '').toUpperCase();
    const mapped = portfolio?.active_trade_ids_by_lane?.[lane] || null;
    if (mapped && (portfolio?.trades || []).some(trade => trade?.trade_id === mapped && trade?.status === 'OPEN')) return mapped;
    return (portfolio?.trades || []).find(trade => trade?.status === 'OPEN' && m5TradeRuleLane(trade, null) === lane)?.trade_id || null;
  }

  function m5ExecutionLaneLifecycleSlice(master, ruleLane) {
    if (!master) return null;
    const lane = String(ruleLane || RULE_LANE_NORMAL).toUpperCase();
    const slice = cloneJsonValue(master);
    const portfolio = slice.portfolio || {};
    portfolio.positions = (portfolio.positions || []).filter(position => String(position?.rule_lane || RULE_LANE_NORMAL).toUpperCase() === lane);
    portfolio.trades = (portfolio.trades || []).filter(trade => m5TradeRuleLane(trade, null) === lane);
    const activeTradeId = m5ExecutionOpenTradeIdForLane(portfolio, lane);
    portfolio.active_trade_id = activeTradeId;
    portfolio.active_trade_ids_by_lane = activeTradeId ? { [lane]: activeTradeId } : {};
    const laneLastKey = master?.portfolio?.last_evaluated_reference_key_by_lane?.[lane]
      || master?.portfolio?.evaluated_reference_keys_by_lane?.[lane]?.slice?.(-1)?.[0]
      || null;
    portfolio.evaluated_reference_keys = laneLastKey ? [laneLastKey] : [];
    portfolio.last_evaluated_reference_key = laneLastKey;
    portfolio.last_evaluated_reference_ms = master?.portfolio?.last_evaluated_reference_ms_by_lane?.[lane] ?? null;
    portfolio.evaluated_reference_count = Number(master?.portfolio?.evaluated_reference_count_by_lane?.[lane] || portfolio.evaluated_reference_count || 0);
    portfolio.evaluated_reference_keys_by_lane = { [lane]: [...portfolio.evaluated_reference_keys] };
    if (lane !== RULE_LANE_NORMAL) {
      portfolio.normal_entry_opportunities = [];
      portfolio.used_dow_confirmation_ids = [];
      portfolio.normal_anchor_lifecycle = m5ExecutionEmptyNormalAnchorLifecycle();
    }
    if (lane !== RULE_LANE_EXPANSION_LITE) {
      portfolio.expansion_lite_entry_opportunities = [];
      portfolio.used_expansion_lite_confirmation_ids = [];
    }
    portfolio.status = m5ExecutionOpenPositions(portfolio).length ? 'OPEN' : 'FLAT';
    slice.portfolio = portfolio;
    const belongs = event => String(event?.rule_lane || event?.execution?.rule_lane || '').toUpperCase() === lane;
    slice.decision_events = (slice.decision_events || []).filter(belongs);
    slice.state_change_events = (slice.state_change_events || []).filter(event => !event?.rule_lane || belongs(event));
    slice.execution_events = (slice.execution_events || []).filter(belongs);
    slice.run_result = m5ExecutionRunResult(slice);
    return slice;
  }

  function m5ExecutionMergeParallelLaneSnapshots(draft, previousMaster, laneSnapshots, lanePolicy) {
    const base = cloneJsonValue(laneSnapshots[0] || previousMaster || m5ExecutionEmptyLifecycle(draft, {}));
    const snapshots = laneSnapshots.filter(Boolean);
    const portfolio = base.portfolio || {};
    portfolio.positions = snapshots.flatMap(snapshot => snapshot?.portfolio?.positions || []);
    portfolio.trades = snapshots.flatMap(snapshot => snapshot?.portfolio?.trades || []);
    portfolio.normal_entry_opportunities = cloneJsonValue(snapshots.find(snapshot => snapshot?.engine?.selected_entry_rule_lane === RULE_LANE_NORMAL)?.portfolio?.normal_entry_opportunities || []);
    portfolio.used_dow_confirmation_ids = cloneJsonValue(snapshots.find(snapshot => snapshot?.engine?.selected_entry_rule_lane === RULE_LANE_NORMAL)?.portfolio?.used_dow_confirmation_ids || []);
    portfolio.normal_anchor_lifecycle = cloneJsonValue(snapshots.find(snapshot => snapshot?.engine?.selected_entry_rule_lane === RULE_LANE_NORMAL)?.portfolio?.normal_anchor_lifecycle || m5ExecutionEmptyNormalAnchorLifecycle());
    portfolio.expansion_lite_entry_opportunities = cloneJsonValue(snapshots.find(snapshot => snapshot?.engine?.selected_entry_rule_lane === RULE_LANE_EXPANSION_LITE)?.portfolio?.expansion_lite_entry_opportunities || []);
    portfolio.used_expansion_lite_confirmation_ids = cloneJsonValue(snapshots.find(snapshot => snapshot?.engine?.selected_entry_rule_lane === RULE_LANE_EXPANSION_LITE)?.portfolio?.used_expansion_lite_confirmation_ids || []);
    portfolio.active_trade_ids_by_lane = {};
    portfolio.evaluated_reference_keys_by_lane = {};
    portfolio.last_evaluated_reference_key_by_lane = {};
    portfolio.last_evaluated_reference_ms_by_lane = {};
    portfolio.evaluated_reference_count_by_lane = {};
    for (const lane of lanePolicy.enabled_entry_rule_lanes) {
      const snapshot = snapshots.find(item => item?.engine?.selected_entry_rule_lane === lane);
      const tradeId = m5ExecutionOpenTradeIdForLane(snapshot?.portfolio, lane);
      if (tradeId) portfolio.active_trade_ids_by_lane[lane] = tradeId;
      const laneLastKey = snapshot?.portfolio?.last_evaluated_reference_key
        || snapshot?.portfolio?.evaluated_reference_keys?.slice?.(-1)?.[0]
        || null;
      portfolio.evaluated_reference_keys_by_lane[lane] = laneLastKey ? [laneLastKey] : [];
      portfolio.last_evaluated_reference_key_by_lane[lane] = laneLastKey;
      portfolio.last_evaluated_reference_ms_by_lane[lane] = snapshot?.portfolio?.last_evaluated_reference_ms ?? null;
      portfolio.evaluated_reference_count_by_lane[lane] = Number(snapshot?.portfolio?.evaluated_reference_count || 0);
    }
    portfolio.active_trade_id = Object.values(portfolio.active_trade_ids_by_lane)[0] || null;
    portfolio.evaluated_reference_keys = uniqueStrings(Object.entries(portfolio.last_evaluated_reference_key_by_lane).filter(([, key]) => key).map(([lane, key]) => `${lane}|${key}`));
    portfolio.evaluated_reference_count = Object.values(portfolio.evaluated_reference_count_by_lane).reduce((sum, value) => sum + Number(value || 0), 0);
    portfolio.status = m5ExecutionOpenPositions(portfolio).length ? 'OPEN' : 'FLAT';
    base.portfolio = portfolio;
    const eventSort = (a, b) => String(a?.simulation_time || '').localeCompare(String(b?.simulation_time || '')) || String(a?.rule_lane || '').localeCompare(String(b?.rule_lane || ''));
    base.decision_events = snapshots.flatMap(snapshot => snapshot?.decision_events || []).sort(eventSort);
    base.state_change_events = snapshots.flatMap(snapshot => snapshot?.state_change_events || []).sort(eventSort);
    base.execution_events = snapshots.flatMap(snapshot => snapshot?.execution_events || []).sort(eventSort);
    base.trigger_evaluation = {
      action: 'PARALLEL_RULE_LANE_EVALUATION',
      action_label: 'Rule Lane並列評価',
      status_label: '各Lane独立',
      rule_lane: 'PARALLEL',
      lane_triggers: Object.fromEntries(snapshots.map(snapshot => [snapshot?.engine?.selected_entry_rule_lane || 'UNKNOWN', cloneJsonValue(snapshot?.trigger_evaluation || null)])),
      simultaneous_entry_policy: lanePolicy.simultaneous_entry_policy,
      cross_lane_condition_sharing: lanePolicy.cross_lane_condition_sharing
    };
    base.engine = {
      ...(base.engine || {}),
      selected_entry_rule_lane: ENTRY_LANE_MODE_PARALLEL_RULE_LANES,
      enabled_entry_rule_lanes: [...lanePolicy.enabled_entry_rule_lanes],
      parallel_entry_enabled: true,
      simultaneous_entry_policy: lanePolicy.simultaneous_entry_policy,
      close_lane_source: 'EACH_OPEN_TRADE_RULE_LANE'
    };
    base.phase = 'v0.9.0.53-cycle-entry-window-independent-from-confirm';
    base.run_result = m5ExecutionRunResult(base);
    const validations = snapshots.map(snapshot => snapshot?.validation || {});
    const errors = validations.flatMap(value => value.errors || []);
    const warnings = validations.flatMap(value => value.warnings || []);
    base.validation = {
      valid: errors.length === 0,
      checked_at: nowLocalIso(),
      errors: uniqueStrings(errors),
      warnings: uniqueStrings(warnings),
      no_lookahead: validations.every(value => value.no_lookahead !== false),
      parallel_rule_lanes: true
    };
    const currentRef = base?.reference?.reference_close_ms;
    const currentExecutions = base.execution_events.filter(event => numberOrNull(event?.simulation_time_ms) === numberOrNull(currentRef) || String(event?.simulation_time || '') === String(base?.reference?.reference_close_time || ''));
    base.status = errors.length ? 'invalid' : currentExecutions.length ? 'executed' : 'evaluated_no_execution';
    base.teacher_guard = 'NORMAL / EXPANSION / EXPANSION_LITEは独立したRule Lane・独立Trade・独立Close Evaluatorとしてパラレル走行します。同一M5足で複数LaneのEntry成立を許可し、条件・HSI起点・Entry Opportunity・建玉・Exit理由を相互流用しません。';
    return base;
  }

  function buildM5ExecutionPositionLifecycleSnapshot(state, draft, candleSync, timeframeSnapshot, hsiSnapshot, upperSnapshot) {
    const lanePolicy = m5RuleLanePolicy(draft?.m5_execution_policy || {});
    if (!lanePolicy.parallel_entry_enabled || lanePolicy.enabled_entry_rule_lanes.length <= 1) {
      return buildM5ExecutionSingleLanePositionLifecycleSnapshot(state, draft, candleSync, timeframeSnapshot, hsiSnapshot, upperSnapshot);
    }
    const referenceMs = numberOrNull(candleSync?.reference?.reference_close_ms);
    const previousInfo = m5ExecutionPreviousLifecycle(state, referenceMs, draft);
    const previousMaster = previousInfo.lifecycle || null;
    const snapshots = [];
    for (const lane of lanePolicy.enabled_entry_rule_lanes) {
      const laneDraft = cloneJsonValue(draft);
      laneDraft.m5_execution_policy = laneDraft.m5_execution_policy || {};
      laneDraft.m5_execution_policy.rule_lane_policy = laneDraft.m5_execution_policy.rule_lane_policy || {};
      laneDraft.m5_execution_policy.rule_lane_policy.active_entry_rule_lane = lane;
      laneDraft.m5_execution_policy.rule_lane_policy.enabled_entry_rule_lanes = [lane];
      laneDraft.m5_execution_policy.rule_lane_policy.parallel_entry_enabled = false;
      laneDraft.m5_execution_policy.rule_lane_policy.simultaneous_entry_policy = 'SINGLE_LANE_ONLY';
      const lanePrevious = m5ExecutionLaneLifecycleSlice(previousMaster, lane);
      const laneState = lanePrevious
        ? { simulationTrace: { run_snapshot: { position_lifecycle: lanePrevious } } }
        : {};
      const snapshot = buildM5ExecutionSingleLanePositionLifecycleSnapshot(laneState, laneDraft, candleSync, timeframeSnapshot, hsiSnapshot, upperSnapshot);
      snapshot.engine = { ...(snapshot.engine || {}), selected_entry_rule_lane: lane };
      snapshots.push(snapshot);
    }
    return m5ExecutionMergeParallelLaneSnapshots(draft, previousMaster, snapshots, lanePolicy);
  }

  function mergeM5ExecutionChartEvents(existingEvents, snapshot) {
    const kept = (existingEvents || []).filter(event => event?.generated_by !== M5_EXECUTION_GENERATOR);
    const projected = (snapshot?.execution_events || []).filter(event => event?.display?.visible === true);
    return [...kept, ...projected];
  }

  function executionActionLabel(value) {
    return ({ ENTRY: '新規Entry', REENTRY: '再Entry', ADD_ON: '買い増し', PARTIAL_CLOSE: '一部決済', FULL_CLOSE: '全決済', STOP_CLOSE: '損切り決済', WAIT: '待機', BLOCKED: '実行不可', ALREADY_EVALUATED: '評価済み' })[String(value || '').toUpperCase()] || String(value || '-');
  }

  function positionRoleLabel(value) {
    return ({ NORMAL: '通常玉', EXPANSION_CORE: 'Expansion本玉', EXPANSION_ADD_ON: 'Expansion追撃玉', EXPANSION_LITE_CORE: 'Expansion-Lite本玉', EXPANSION_LITE_ADD_ON: 'Expansion-Lite追撃玉', CORE: '本玉', ADD_ON: '追撃玉', RUNNER: 'Runner' })[String(value || '').toUpperCase()] || String(value || '-');
  }

  function renderM5ExecutionRows(snapshot) {
    const positions = snapshot?.portfolio?.positions || [];
    if (!positions.length) return '<tr><td colspan="10">建玉はまだありません。</td></tr>';
    return positions.map(position => `<tr><td>${escapeHtml(positionRoleLabel(position.role))}</td><td>${escapeHtml(position.side || '-')}</td><td>${position.units_open ?? 0} / ${position.units_initial ?? 0}</td><td>${round3(position.entry_price)}</td><td>${escapeHtml(position.entry_time || '-')}</td><td>${escapeHtml(position.management_timeframe || '-')}</td><td>${escapeHtml(position.target_plan?.next_target_label || '-')} / ${position.target_plan?.next_target_price == null ? '-' : round3(position.target_plan.next_target_price)}</td><td>${position.invalidation_rule?.invalidation_price == null ? '-' : round3(position.invalidation_rule.invalidation_price)}</td><td>${escapeHtml(position.status || '-')}</td><td>${escapeHtml(shortText(position.position_id || '-', 22))}</td></tr>`).join('');
  }

  function renderM5ExecutionEventRows(snapshot) {
    const events = snapshot?.execution_events || [];
    if (!events.length) return '<tr><td colspan="6">この地点では売買実行なし。</td></tr>';
    return events.slice(-12).map(event => `<tr><td>${escapeHtml(event.simulation_time || '-')}</td><td>${escapeHtml(traceReplayEventTypeLabelForEvent(event))}</td><td>${escapeHtml(event.trade_id || '-')}</td><td>${round3(event.price)}</td><td>${escapeHtml(event.summary || '-')}</td><td>${(event.cause_event_ids || []).length}</td></tr>`).join('');
  }

  function decisionStatusLabel(value) {
    return ({ ALLOW_SEARCH: '探索可', CONDITIONAL: '条件付き', WAIT: '待機', BLOCKED: '禁止', NOT_EVALUATED: '未評価', PREFER_HOLD: '保有優先', HOLD_WITH_ACCELERATED_EXIT: '保有継続・早期離脱監視', REVIEW_H1_CONFLICT: 'H1不一致を再確認', UNRESOLVED: '未解決', ARMED: '準備ON', OFF: 'OFF', ON: 'ON', CONFIRMED: '確認済み', NONE: '未成立', ACCELERATED: '前倒し', NORMAL: '通常' })[String(value || '').toUpperCase()] || String(value || '-');
  }

  function directionBiasLabel(value, alignment) {
    const dir = ({ LONG: '買い方向', SHORT: '売り方向', UNDETERMINED: '方向未定' })[String(value || '').toUpperCase()] || String(value || '-');
    const align = ({ ALIGNED: '整合', CONFLICT: '不一致', UNDETERMINED: '未判定' })[String(alignment || '').toUpperCase()] || String(alignment || '-');
    return `${dir} / ${align}`;
  }

  function decisionModeLabel(value) {
    return ({ NORMAL_SEARCH: '通常探索', EXPANSION_SEARCH: 'Expansion探索', DEFENSIVE_MANAGEMENT: '防御管理', EXIT_CONTEXT_ARMED: '離脱準備', EXIT_CONTEXT_CONFIRMED: '離脱条件確認', NO_TRADE: '売買対象外', WATCH: '監視' })[String(value || '').toUpperCase()] || String(value || '-');
  }

  function decisionEffectLabel(effect) {
    const target = ({ 'entry_policy.normal_entry': '通常Entry', 'entry_policy.expansion_entry': 'Expansion Entry', 'entry_policy.reentry': '再Entry', 'entry_policy.add_on': '買い増し', 'position_policy.hold_core': 'Core保有', 'position_policy.profit_take_armed': '利確準備', 'position_policy.h1_exit_trigger': 'H1離脱監視', no_trade: '売買対象外' })[String(effect?.target || '')] || String(effect?.target || '-');
    const assign = effect?.assign || {};
    return `${target}: ${Object.entries(assign).map(([key, value]) => `${key}=${decisionStatusLabel(value)}`).join(', ') || '-'}`;
  }

  function renderUpperContextDecisionRows(snapshot) {
    const entry = snapshot?.entry_policy || {};
    const position = snapshot?.position_policy || {};
    const exit = position.h1_exit_trigger || {};
    const cells = [
      directionBiasLabel(snapshot?.direction_bias?.value, snapshot?.direction_bias?.alignment),
      decisionModeLabel(snapshot?.decision_mode),
      decisionStatusLabel(entry.normal_entry?.status),
      decisionStatusLabel(entry.expansion_entry?.status),
      decisionStatusLabel(entry.reentry?.status),
      decisionStatusLabel(entry.add_on?.status),
      decisionStatusLabel(position.hold_core?.status),
      position.profit_take_armed?.enabled ? '準備ON' : '未準備',
      exit.enabled ? `${decisionStatusLabel(exit.signal || 'NONE')} / ${decisionStatusLabel(exit.exit_policy || 'NORMAL')}` : 'OFF',
      snapshot?.no_trade?.active ? '対象外' : '対象内'
    ];
    return `<tr>${cells.map((value, index) => `<td class="${index === 0 ? 'gpt-fx-chart-decision-neutral' : upperDecisionStatusClass(value)}">${escapeHtml(value)}</td>`).join('')}</tr>`;
  }

  function renderUpperContextRuleRows(snapshot) {
    const matched = (snapshot?.rule_evaluations || []).filter(item => item?.matched === true);
    if (!matched.length) return '<tr><td colspan="5">該当ルールなし / 監視継続</td></tr>';
    return matched.map(item => `<tr><td>${item.priority}</td><td>${escapeHtml(item.rule_id || '-')}</td><td>${escapeHtml(({ season_guard: '季節ガード', management: '保有管理', permission: '探索権限', no_trade: '売買対象外' })[item.category] || item.category || '-')}</td><td>${escapeHtml(item.summary || '-')}</td><td>${escapeHtml((item.applied_effects || []).map(decisionEffectLabel).join(' / ') || '-')}</td></tr>`).join('');
  }

  function traceEventClassLabel(value) {
    const key = String(value || '').toUpperCase();
    return ({ OBSERVATION: '観測', STATE_CHANGE: '状態変化', DECISION: '判断', EXECUTION: '実行' })[key] || 'その他';
  }

  function traceReplayEventClass(event) {
    const type = String(event?.event_type || '').toLowerCase();
    if (String(event?.generated_by || '') === UPPER_CONTEXT_DECISION_GENERATOR || type.startsWith('upper_context_decision') || ['entry_blocked', 'exit_armed', 'm5_trigger_evaluated'].includes(type)) return 'DECISION';
    if (type === 'management_timeframe_promoted' || type === 'position_lifecycle_changed') return 'STATE_CHANGE';
    if (['entry', 'reentry', 'add_on', 'partial_close', 'close', 'stop_close', 'execution'].includes(type) || type.startsWith('execution_') || type.endsWith('_executed')) return 'EXECUTION';
    if (type.startsWith('swing_')) return 'OBSERVATION';
    return 'STATE_CHANGE';
  }

  function traceReplayDomain(event) {
    const generated = String(event?.generated_by || '');
    if (generated === SHARED_SWING_POINT_GENERATOR || String(event?.event_type || '').startsWith('swing_')) return 'swing';
    if (generated === DOW_TREND_GENERATOR || ['trend_changed', 'dow_confirmation'].includes(String(event?.event_type || ''))) return 'trend';
    if (generated === CYCLE_POSITION_GENERATOR || String(event?.event_type || '').startsWith('cycle_')) return 'cycle';
    if (generated === HSI_ANCHOR_GENERATOR || String(event?.event_type || '').startsWith('hsi_anchor_')) return 'hsi_anchor';
    if (generated === TIMEFRAME_STATE_GENERATOR || String(event?.event_type || '').startsWith('timeframe_state_')) return 'timeframe_state';
    if (generated === UPPER_CONTEXT_DECISION_GENERATOR || String(event?.event_type || '').startsWith('upper_context_decision')) return 'upper_context';
    if (generated === M5_EXECUTION_GENERATOR && traceReplayEventClass(event) !== 'EXECUTION') return 'position_lifecycle';
    if (traceReplayEventClass(event) === 'EXECUTION') return 'execution';
    return 'other';
  }

  function traceReplaySetPath(target, path, value) {
    const keys = String(path || '').split('.').filter(Boolean);
    if (!keys.length) return;
    let cursor = target;
    keys.forEach((key, index) => {
      if (index === keys.length - 1) cursor[key] = cloneJsonValue(value);
      else {
        if (!cursor[key] || typeof cursor[key] !== 'object' || Array.isArray(cursor[key])) cursor[key] = {};
        cursor = cursor[key];
      }
    });
  }

  function traceReplayApplyPatch(replayState, patch) {
    const next = cloneJsonValue(replayState || {});
    Object.entries(patch?.set || {}).forEach(([path, value]) => traceReplaySetPath(next, path, value));
    return next;
  }

  function traceReplayPatchForEvent(event) {
    const tf = normalizePanelTimeframe(event?.timeframe || event?.panel || 'M5', String(event?.timeframe || event?.panel || 'M5').toUpperCase());
    const domain = traceReplayDomain(event);
    const compact = {
      event_id: event?.event_id || '',
      event_type: event?.event_type || '',
      event_class: traceReplayEventClass(event),
      simulation_time: event?.simulation_time || event?.time || '',
      summary: event?.summary || '',
      state_after: cloneJsonValue(event?.state_after || {}),
      reason_codes: [...(event?.reason_codes || [])],
      rule_ids: [...(event?.rule_ids || [])]
    };
    const set = {
      last_event: compact,
      event_count: numberOrNull(event?.sequence) || 0,
      reference_time: compact.simulation_time
    };
    if (domain === 'upper_context') set.upper_context = compact;
    else if (domain === 'position_lifecycle') set.position_lifecycle = compact;
    else if (domain === 'execution') { set.execution = compact; set.position_lifecycle = compact; }
    else set[`timeframes.${tf}.${domain}`] = compact;
    return { op: 'SET', set };
  }

  function traceReplayInitialState(reference) {
    return {
      schema_version: 'fx_trace_replay_state_v0_1',
      reference_time: reference?.reference_close_time || reference?.state_as_of || '',
      event_count: 0,
      last_event: null,
      timeframes: {},
      upper_context: null,
      position_lifecycle: null,
      execution: null
    };
  }

  function traceReplayCollectEvents(state, reference, swingSnapshot, dowSnapshot, cycleSnapshot, hsiSnapshot, timeframeSnapshot, upperSnapshot, positionSnapshot) {
    const referenceMs = numberOrNull(reference?.reference_close_ms ?? reference?.state_as_of_ms);
    const previousTrace = state?.simulationTrace?.run_snapshot?.trace_replay || state?.simulationRunSnapshot?.trace_replay || null;
    const previousReferenceMs = numberOrNull(previousTrace?.reference?.reference_close_ms ?? previousTrace?.reference?.state_as_of_ms);
    const carryPrevious = previousTrace && (previousReferenceMs == null || referenceMs == null || previousReferenceMs <= referenceMs);
    const all = [
      ...(carryPrevious ? (previousTrace.events || []).filter(event => {
        const ms = parseDateTimeMs(event?.simulation_time || event?.time);
        return referenceMs == null || ms == null || ms <= referenceMs;
      }) : []),
      ...(swingSnapshot?.observation_events || []),
      ...(dowSnapshot?.state_change_events || []),
      ...(dowSnapshot?.confirmation_events || []),
      ...(cycleSnapshot?.state_change_events || []),
      ...(hsiSnapshot?.lifecycle_events || []),
      ...(timeframeSnapshot?.state_events || []),
      ...(upperSnapshot?.decision_events || []),
      ...(positionSnapshot?.decision_events || []),
      ...(positionSnapshot?.state_change_events || []),
      ...(positionSnapshot?.execution_events || [])
    ].map(event => cloneJsonValue(event));
    const byId = new Map();
    all.forEach(event => { if (event?.event_id) byId.set(event.event_id, event); });
    return [...byId.values()];
  }

  function traceReplayValidateDag(events, policy) {
    const errors = [];
    const warnings = [];
    const byId = new Map();
    events.forEach(event => {
      const id = String(event?.event_id || '');
      if (!id) errors.push('event_idが空のTrace Eventがあります。');
      else if (byId.has(id)) errors.push(`Trace Event IDが重複しています: ${id}`);
      else byId.set(id, event);
    });
    const roots = new Set((policy?.root_event_types || []).map(x => String(x)));
    events.forEach(event => {
      const causes = normalizeStringArray(event?.cause_event_ids || event?.caused_by_event_ids);
      const eventClass = traceReplayEventClass(event);
      if ((policy?.cause_event_ids_required_for || []).includes(eventClass) && !roots.has(String(event?.event_type || '')) && !causes.length) {
        errors.push(`${event.event_id}: ${traceEventClassLabel(eventClass)}Eventに原因Eventがありません。`);
      }
      causes.forEach(causeId => {
        const cause = byId.get(causeId);
        if (!cause) errors.push(`${event.event_id}: 原因Eventが見つかりません: ${causeId}`);
        else {
          const causeMs = parseDateTimeMs(cause.simulation_time || cause.time);
          const eventMs = parseDateTimeMs(event.simulation_time || event.time);
          if (causeMs != null && eventMs != null && causeMs > eventMs) errors.push(`${event.event_id}: 原因Event ${causeId} が結果Eventより未来です。`);
        }
      });
    });
    const visiting = new Set();
    const visited = new Set();
    const visit = id => {
      if (visiting.has(id)) { errors.push(`原因Eventに循環参照があります: ${id}`); return; }
      if (visited.has(id)) return;
      visiting.add(id);
      const event = byId.get(id);
      normalizeStringArray(event?.cause_event_ids || event?.caused_by_event_ids).forEach(causeId => { if (byId.has(causeId)) visit(causeId); });
      visiting.delete(id);
      visited.add(id);
    };
    byId.forEach((_, id) => visit(id));
    return { valid: errors.length === 0, errors: uniqueStrings(errors), warnings: uniqueStrings(warnings) };
  }

  function buildTraceReplaySnapshot(state, draft, reference, swingSnapshot, dowSnapshot, cycleSnapshot, hsiSnapshot, timeframeSnapshot, upperSnapshot, positionSnapshot) {
    const policy = { ...(draft?.trace_replay_policy || {}) };
    const rawEvents = traceReplayCollectEvents(state, reference, swingSnapshot, dowSnapshot, cycleSnapshot, hsiSnapshot, timeframeSnapshot, upperSnapshot, positionSnapshot);
    rawEvents.sort((a, b) => (parseDateTimeMs(a?.simulation_time || a?.time) ?? 0) - (parseDateTimeMs(b?.simulation_time || b?.time) ?? 0) || String(a?.event_id || '').localeCompare(String(b?.event_id || '')));
    const events = rawEvents.map((event, index) => {
      const normalized = {
        ...event,
        sequence: index + 1,
        event_class: traceReplayEventClass(event),
        event_class_label: traceEventClassLabel(traceReplayEventClass(event)),
        domain: traceReplayDomain(event),
        cause_event_ids: normalizeStringArray(event?.cause_event_ids || event?.caused_by_event_ids)
      };
      normalized.replay_patch = traceReplayPatchForEvent(normalized);
      return normalized;
    });
    const dag = traceReplayValidateDag(events, policy);
    const checkpointInterval = Math.max(1, Math.floor(numberOrNull(policy.checkpoint_interval_events) ?? 50));
    const checkpoints = [];
    let replayState = traceReplayInitialState(reference);
    events.forEach((event, index) => {
      replayState = traceReplayApplyPatch(replayState, event.replay_patch);
      const sequence = index + 1;
      if (sequence % checkpointInterval === 0 || (policy.final_checkpoint_required === true && sequence === events.length)) {
        checkpoints.push({
          checkpoint_id: `trace_checkpoint_${String(sequence).padStart(6, '0')}`,
          after_sequence: sequence,
          after_event_id: event.event_id,
          simulation_time: event.simulation_time || '',
          state_digest: stableTextHash(JSON.stringify(replayState)),
          replay_state: cloneJsonValue(replayState)
        });
      }
    });
    const counts = Object.fromEntries(TRACE_EVENT_CLASSES.map(key => [key, events.filter(event => event.event_class === key).length]));
    const executionEvents = events.filter(event => event.event_class === 'EXECUTION');
    return {
      schema_version: 'fx_simulation_trace_replay_v0_1',
      kind: 'fx_simulation_trace_replay',
      engine: {
        engine_id: TRACE_REPLAY_ENGINE_ID,
        storage_model: 'append_only_delta_events_plus_periodic_checkpoints',
        replay_method: 'nearest_checkpoint_then_apply_delta_patches',
        checkpoint_interval_events: checkpointInterval,
        full_state_per_event: false,
        ui_language: 'ja'
      },
      reference: cloneJsonValue(reference || {}),
      summary: {
        event_count: events.length,
        checkpoint_count: checkpoints.length,
        event_class_counts: counts,
        root_event_count: events.filter(event => !(event.cause_event_ids || []).length).length,
        causal_edge_count: events.reduce((sum, event) => sum + (event.cause_event_ids || []).length, 0),
        execution_event_count: executionEvents.length
      },
      events,
      checkpoints,
      final_state: cloneJsonValue(replayState),
      event_index: Object.fromEntries(events.map(event => [event.event_id, { sequence: event.sequence, event_class: event.event_class, event_type: event.event_type, simulation_time: event.simulation_time || '', timeframe: event.timeframe || event.panel || '' }])),
      run_result: {
        ...(cloneJsonValue(positionSnapshot?.run_result || {})),
        status: positionSnapshot?.run_result?.status || (executionEvents.length ? 'EXECUTION_EVENTS_PRESENT' : 'NO_EXECUTION_YET'),
        execution_event_count: executionEvents.length,
        trade_ids: uniqueStrings([...(positionSnapshot?.run_result?.trade_ids || []), ...executionEvents.map(event => event.trade_id).filter(Boolean)]),
        teacher_guard: 'M5 Execution / Position Lifecycleで生成した仮想実行Eventを集計します。リアル注文・資金管理は対象外です。'
      },
      validation: {
        ...dag,
        no_lookahead: policy.no_lookahead === true,
        checked_at: nowLocalIso()
      },
      teacher_guard: '観測・状態変化・判断・仮想実行を原因EventとCheckpointから再生します。売買推奨やリアル注文ではありません。'
    };
  }

  function replayTraceStateAt(snapshot, requestedSequence) {
    const max = snapshot?.events?.length || 0;
    const sequence = Math.max(0, Math.min(max, Math.floor(numberOrNull(requestedSequence) ?? max)));
    const checkpoints = (snapshot?.checkpoints || []).filter(item => Number(item.after_sequence) <= sequence).sort((a, b) => Number(b.after_sequence) - Number(a.after_sequence));
    const checkpoint = checkpoints[0] || null;
    let state = checkpoint ? cloneJsonValue(checkpoint.replay_state) : traceReplayInitialState(snapshot?.reference);
    const start = checkpoint ? Number(checkpoint.after_sequence) : 0;
    (snapshot?.events || []).filter(event => Number(event.sequence) > start && Number(event.sequence) <= sequence).forEach(event => { state = traceReplayApplyPatch(state, event.replay_patch); });
    return { sequence, checkpoint_id: checkpoint?.checkpoint_id || null, replay_state: state, event: sequence > 0 ? snapshot.events[sequence - 1] : null };
  }

  function traceReplayCausalChain(snapshot, eventId, maxDepth = 12) {
    const byId = new Map((snapshot?.events || []).map(event => [event.event_id, event]));
    const output = [];
    const seen = new Set();
    const walk = (id, depth) => {
      if (!id || depth > maxDepth || seen.has(id)) return;
      seen.add(id);
      const event = byId.get(id);
      if (!event) return;
      output.push({ depth, event_id: id, event_type: event.event_type, rule_lane: event.rule_lane || event.execution?.rule_lane || null, execution: cloneJsonValue(event.execution || {}), event_class: event.event_class, event_class_label: event.event_class_label, timeframe: event.timeframe || event.panel || '', simulation_time: event.simulation_time || '', summary: event.summary || '' });
      (event.cause_event_ids || []).forEach(causeId => walk(causeId, depth + 1));
    };
    walk(eventId, 0);
    return output;
  }

  function traceReplayEventTypeLabel(type) {
    const key = String(type || '');
    return ({
      swing_candidate: '山谷候補', swing_confirmed: '山谷確定', swing_retired: '山谷退役',
      trend_changed: 'ダウ状態変更', cycle_origin_changed: 'サイクル起点変更', cycle_phase_changed: 'サイクル段階変更',
      hsi_anchor_registered: 'HSI起点登録', hsi_anchor_adopted: 'HSI起点採用', hsi_anchor_retired: 'HSI起点退役',
      timeframe_state_snapshot: '時間足状態確定', timeframe_state_changed: '時間足状態変更',
      upper_context_decision_snapshot: '上位判断確定', upper_context_decision_changed: '上位判断変更', m5_trigger_evaluated: 'M5実行判定',
      entry_blocked: 'Entry禁止', exit_armed: '利確準備', entry: '新規Entry', reentry: '再Entry', add_on: '買い増し', partial_close: '一部決済', close: '全決済', stop_close: '損切り決済', management_timeframe_promoted: '管理時間足昇格'
    })[key] || key || 'イベント';
  }

  function traceReplayEventTypeLabelForEvent(event) {
    return traceReplayEventTypeLabel(simulationRuleAwareEventType(event));
  }

  function traceReplayClassCss(value) {
    return ({ OBSERVATION: 'gpt-fx-chart-trace-observation', STATE_CHANGE: 'gpt-fx-chart-trace-state', DECISION: 'gpt-fx-chart-trace-decision', EXECUTION: 'gpt-fx-chart-trace-execution' })[String(value || '').toUpperCase()] || '';
  }

  function renderTraceReplayRows(snapshot, selectedSequence) {
    const events = snapshot?.events || [];
    if (!events.length) return '<tr><td colspan="8">判断履歴はまだありません。</td></tr>';
    const start = Math.max(0, Number(selectedSequence || events.length) - 24);
    return events.slice(start, start + 25).map(event => `<tr><td>${event.sequence}</td><td>${escapeHtml(event.simulation_time || '-')}</td><td>${escapeHtml(event.timeframe || event.panel || '-')}</td><td class="${traceReplayClassCss(event.event_class)}">${escapeHtml(event.event_class_label || traceEventClassLabel(event.event_class))}</td><td>${escapeHtml(traceReplayEventTypeLabelForEvent(event))}</td><td>${escapeHtml(shortText(event.summary || '-', 72))}</td><td>${(event.cause_event_ids || []).length}</td><td><button class="gpt-fx-chart-replay-event-btn" type="button" data-trace-replay-sequence="${event.sequence}" data-trace-replay-event-id="${escapeHtml(event.event_id)}">追う</button></td></tr>`).join('');
  }

  function renderTraceReplayInspector(snapshot, selectedSequence) {
    const replay = replayTraceStateAt(snapshot, selectedSequence);
    const event = replay.event;
    const chain = event ? traceReplayCausalChain(snapshot, event.event_id) : [];
    const chainHtml = chain.length ? `<ol class="gpt-fx-chart-replay-chain">${chain.map(item => `<li style="margin-left:${Math.min(item.depth, 6) * 8}px"><strong>${escapeHtml(item.event_class_label || traceEventClassLabel(item.event_class))}</strong> / ${escapeHtml(item.timeframe || '-')} / ${escapeHtml(traceReplayEventTypeLabelForEvent(item))}<br>${escapeHtml(shortText(item.summary || '-', 94))}</li>`).join('')}</ol>` : '<div class="gpt-fx-chart-replay-meta">原因連鎖はありません。</div>';
    const stateText = JSON.stringify(replay.replay_state || {}, null, 2);
    return `<div class="gpt-fx-chart-replay-panel"><div class="gpt-fx-chart-replay-title">復元地点 ${replay.sequence} / ${snapshot?.events?.length || 0}</div><div class="gpt-fx-chart-replay-meta">${event ? `${escapeHtml(event.simulation_time || '-')} / ${escapeHtml(event.timeframe || event.panel || '-')} / ${escapeHtml(traceReplayEventTypeLabelForEvent(event))}` : '開始前状態'}<br>復元元Checkpoint: ${escapeHtml(replay.checkpoint_id || '先頭から再生')}</div><pre class="gpt-fx-chart-run-preview" style="max-height:180px;margin-top:7px">${escapeHtml(stateText)}</pre></div><div class="gpt-fx-chart-replay-panel"><div class="gpt-fx-chart-replay-title">なぜこうなった？ 原因を逆に追う</div>${chainHtml}</div>`;
  }

  function renderTraceReplaySection(snapshot, selectedSequence) {
    if (!snapshot) return '';
    const max = snapshot?.events?.length || 0;
    const selected = Math.max(0, Math.min(max, Math.floor(numberOrNull(selectedSequence) ?? max)));
    const counts = snapshot?.summary?.event_class_counts || {};
    return `<div class="gpt-fx-chart-run-summary-card"><div class="gpt-fx-chart-run-label">判断履歴・再生ログ</div><div class="gpt-fx-chart-run-value">観測 ${counts.OBSERVATION || 0} / 状態変化 ${counts.STATE_CHANGE || 0} / 判断 ${counts.DECISION || 0} / 実行 ${counts.EXECUTION || 0}<br>Event ${max}件 / Checkpoint ${snapshot?.checkpoints?.length || 0}件 / 原因線 ${snapshot?.summary?.causal_edge_count || 0}本</div></div><div class="gpt-fx-chart-replay-controls"><button class="gpt-fx-chart-btn" type="button" data-run-action="replay-prev">前へ</button><input class="gpt-fx-chart-replay-range" type="range" min="0" max="${max}" step="1" value="${selected}" data-trace-replay-range><button class="gpt-fx-chart-btn" type="button" data-run-action="replay-next">次へ</button></div><div class="gpt-fx-chart-replay-grid" data-role="trace-replay-inspector">${renderTraceReplayInspector(snapshot, selected)}</div><table class="gpt-fx-chart-run-table"><thead><tr><th>No.</th><th>時刻</th><th>足</th><th>区分</th><th>出来事</th><th>要約</th><th>原因</th><th>確認</th></tr></thead><tbody>${renderTraceReplayRows(snapshot, selected)}</tbody></table><div class="gpt-fx-chart-sync-status ${snapshot?.validation?.valid === true ? '' : 'is-error'}"><strong class="${snapshot?.validation?.valid === true ? 'gpt-fx-chart-sync-ok' : 'gpt-fx-chart-sync-error'}">${snapshot?.validation?.valid === true ? '判断履歴の逆追跡・再生 OK' : '判断履歴の整合エラー'}</strong><br><span class="gpt-fx-chart-sync-note">${escapeHtml(snapshot?.validation?.valid === true ? '差分Eventと定期Checkpointから任意地点を復元できます。原因Eventは循環なしのDAGとして検査しています。' : (snapshot?.validation?.errors || []).join(' / '))}</span></div>`;
  }

  function simulationRunVisiblePeriod(state) {
    const source = state?.simulationSource;
    const allRows = state?.simulationAllRows || [];
    if (!source || !allRows.length) return { mode: 'current_chart_window', from: '', to: '', row_count: 0 };
    const rows = getChartWindowRows(source, allRows, state);
    const first = rows[0] || {};
    const last = rows[rows.length - 1] || {};
    return {
      mode: 'current_chart_window',
      from: String(first.datetime || ''),
      to: String(last.datetime || ''),
      row_count: rows.length,
      window_start: Math.max(0, Math.floor(numberOrNull(state?.windowStart) ?? 0)),
      window_size: Math.max(1, Math.floor(numberOrNull(state?.windowSize) ?? rows.length))
    };
  }

  function simulationRunConfirmBarsMap(draft) {
    const map = {};
    REQUIRED_SIMULATION_TIMEFRAMES.forEach(tf => {
      const item = (draft?.timeframe_profiles || []).find(x => normalizePanelTimeframe(x?.timeframe, String(x?.timeframe || '').toUpperCase()) === tf);
      map[tf] = item?.confirm_bars == null || item?.confirm_bars === '' ? null : Number(item.confirm_bars);
    });
    return map;
  }

  function buildSimulationRunSnapshot(state, options = {}) {
    const draft = cloneJsonValue(state?.simulationRunDraft || buildEmptySimulationRunProfile());
    const validation = validateSimulationRunDraft(draft);
    if (!validation.valid) return { snapshot: null, validation };
    const createdAt = nowLocalIso();
    const candleSync = buildMultiTimeframeCandleSyncSnapshot(state, draft);
    if (!candleSync?.validation?.valid) {
      return {
        snapshot: null,
        validation: {
          ...validation,
          valid: false,
          errors: [...validation.errors, ...(candleSync?.validation?.errors || [])]
        },
        candleSync
      };
    }
    const swingPointDetection = buildSharedSwingPointSnapshot(state, draft, candleSync);
    if (!swingPointDetection?.validation?.valid) {
      return {
        snapshot: null,
        validation: {
          ...validation,
          valid: false,
          errors: [...validation.errors, ...(swingPointDetection?.validation?.errors || [])]
        },
        candleSync,
        swingPointDetection
      };
    }
    const dowTrendEvaluation = buildDowTrendEvaluationSnapshot(state, draft, swingPointDetection, candleSync);
    if (!dowTrendEvaluation?.validation?.valid) {
      return {
        snapshot: null,
        validation: {
          ...validation,
          valid: false,
          errors: [...validation.errors, ...(dowTrendEvaluation?.validation?.errors || [])]
        },
        candleSync,
        swingPointDetection,
        dowTrendEvaluation
      };
    }
    const cyclePositionEvaluation = buildCyclePositionEvaluationSnapshot(state, draft, swingPointDetection, candleSync);
    if (!cyclePositionEvaluation?.validation?.valid) {
      return {
        snapshot: null,
        validation: {
          ...validation,
          valid: false,
          errors: [...validation.errors, ...(cyclePositionEvaluation?.validation?.errors || [])]
        },
        candleSync,
        swingPointDetection,
        dowTrendEvaluation,
        cyclePositionEvaluation
      };
    }
    const hsiAnchorRegistry = buildHsiAnchorRegistrySnapshot(state, draft, swingPointDetection, dowTrendEvaluation, cyclePositionEvaluation, candleSync);
    if (!hsiAnchorRegistry?.validation?.valid) {
      return {
        snapshot: null,
        validation: {
          ...validation,
          valid: false,
          errors: [...validation.errors, ...(hsiAnchorRegistry?.validation?.errors || [])]
        },
        candleSync,
        swingPointDetection,
        dowTrendEvaluation,
        cyclePositionEvaluation,
        hsiAnchorRegistry
      };
    }
    const timeframeStates = buildTimeframeStateSnapshot(state, draft, candleSync, swingPointDetection, dowTrendEvaluation, cyclePositionEvaluation, hsiAnchorRegistry);
    if (!timeframeStates?.validation?.valid) {
      return {
        snapshot: null,
        validation: {
          ...validation,
          valid: false,
          errors: [...validation.errors, ...(timeframeStates?.validation?.errors || [])]
        },
        candleSync,
        swingPointDetection,
        dowTrendEvaluation,
        cyclePositionEvaluation,
        hsiAnchorRegistry,
        timeframeStates
      };
    }
    const upperContextDecision = buildUpperContextDecisionSnapshot(state, draft, timeframeStates);
    if (!upperContextDecision?.validation?.valid) {
      return {
        snapshot: null,
        validation: {
          ...validation,
          valid: false,
          errors: [...validation.errors, ...(upperContextDecision?.validation?.errors || [])]
        },
        candleSync,
        swingPointDetection,
        dowTrendEvaluation,
        cyclePositionEvaluation,
        hsiAnchorRegistry,
        timeframeStates,
        upperContextDecision
      };
    }
    const positionLifecycle = buildM5ExecutionPositionLifecycleSnapshot(state, draft, candleSync, timeframeStates, hsiAnchorRegistry, upperContextDecision);
    if (!positionLifecycle?.validation?.valid) {
      return {
        snapshot: null,
        validation: { ...validation, valid: false, errors: [...validation.errors, ...(positionLifecycle?.validation?.errors || [])] },
        candleSync, swingPointDetection, dowTrendEvaluation, cyclePositionEvaluation, hsiAnchorRegistry, timeframeStates, upperContextDecision, positionLifecycle
      };
    }
    // 表示範囲の連続stepでは、各足ごとのReplay全再構築はLifecycle判定に不要。
    // 一点診断では従来どおりReplayを作り、Range実行だけ明示的に省略して応答性を確保する。
    const skipTraceReplay = options?.skipTraceReplay === true;
    const traceReplay = skipTraceReplay
      ? null
      : buildTraceReplaySnapshot(state, draft, candleSync?.reference, swingPointDetection, dowTrendEvaluation, cyclePositionEvaluation, hsiAnchorRegistry, timeframeStates, upperContextDecision, positionLifecycle);
    if (!skipTraceReplay && !traceReplay?.validation?.valid) {
      return {
        snapshot: null,
        validation: { ...validation, valid: false, errors: [...validation.errors, ...(traceReplay?.validation?.errors || [])] },
        candleSync, swingPointDetection, dowTrendEvaluation, cyclePositionEvaluation, hsiAnchorRegistry, timeframeStates, upperContextDecision, positionLifecycle, traceReplay
      };
    }
    const snapshot = {
      schema_version: 'fx_simulation_run_snapshot_v0_11',
      kind: 'fx_simulation_run_snapshot',
      run_id: `sim_run_${compactTimestamp()}`,
      status: positionLifecycle.execution_events?.length ? 'validated_m5_execution' : 'validated_m5_evaluated_no_execution',
      phase: 'v0.9.0.34-dow-confirmation-immediate-entry-when-r2-ready',
      created_at: createdAt,
      engine_enabled: true,
      decision_engine_enabled: true,
      m5_trigger_engine_enabled: true,
      trade_execution_enabled: true,
      profile: {
        profile_id: draft.profile_id,
        profile_file: getSimulationRunProfileFileName(),
        rule_version: draft.rule_version,
        loaded_from: state?.simulationRunProfile?._loaded_from || 'unknown'
      },
      dataset: cloneJsonValue(draft.dataset || {}),
      period: simulationRunVisiblePeriod(state),
      confirm_bars: simulationRunConfirmBarsMap(draft),
      timeframe_profiles: cloneJsonValue(draft.timeframe_profiles || []),
      time_sync_policy: cloneJsonValue(draft.time_sync_policy || {}),
      candle_sync: candleSync,
      swing_point_detection: swingPointDetection,
      dow_trend_evaluation: dowTrendEvaluation,
      cycle_position_evaluation: cyclePositionEvaluation,
      hsi_anchor_registry: hsiAnchorRegistry,
      timeframe_states: timeframeStates,
      upper_context_decision: upperContextDecision,
      position_lifecycle: positionLifecycle,
      trace_replay: traceReplay,
      run_result: cloneJsonValue(positionLifecycle.run_result),
      chart_state: chartStateSnapshot(state),
      validation: {
        status: 'passed',
        checked_at: validation.checked_at,
        required_timeframes: [...REQUIRED_SIMULATION_TIMEFRAMES],
        errors: []
      },
      policy: {
        inheritance: 'forbidden',
        calculation_from_other_timeframes: 'forbidden',
        implicit_default: 'forbidden',
        implicit_fallback: 'forbidden'
      },
      teacher_guard: '上位足Decisionに従うM5仮想実行とCore/Add-on/Runnerの建玉LifecycleをTraceへ保存します。リアル注文・資金管理・売買推奨は対象外です。'
    };
    return { snapshot, validation, candleSync, swingPointDetection, dowTrendEvaluation, cyclePositionEvaluation, hsiAnchorRegistry, timeframeStates, upperContextDecision, positionLifecycle, traceReplay };
  }

  function simulationRuleAwareEventType(event) {
    const type = String(event?.event_type || '').toLowerCase();
    const lane = String(event?.rule_lane || event?.execution?.rule_lane || '').toUpperCase();
    if (lane === RULE_LANE_NORMAL && type === 'reentry') return 'entry';
    return type;
  }

  function simulationExecutionMarkerLabel(event) {
    const type = simulationRuleAwareEventType(event);
    const lane = String(event?.rule_lane || event?.execution?.rule_lane || '').toUpperCase();
    const explicit = String(event?.execution?.chart_marker_label || event?.chart_marker_label || '').trim();
    if (explicit) return explicit;
    if (lane === RULE_LANE_EXPANSION_LITE) {
      if (type === 'entry') return 'Expansion-Lite Entry';
      if (type === 'add_on') return 'Expansion-Lite Add-on';
      if (type === 'close') {
        const exitType = String(event?.execution?.exit_type || '').toUpperCase();
        return ({ TARGET_EXIT: 'R5 Exit', T3_EXIT: 'T3 Exit', STRUCTURAL_EXIT: 'Structural Exit', ANCHOR_EXIT: 'Anchor Exit' })[exitType] || 'Expansion-Lite Exit';
      }
    }
    if (type === 'entry') return 'Entry';
    if (type === 'reentry') return 'ReEntry';
    if (type === 'add_on') return 'Add-on';
    if (type === 'partial_close') return 'CloseOK';
    if (type === 'close') return 'CloseOK';
    if (type === 'stop_close') return 'CloseMiss';
    return '';
  }

  function isSimulationExecutionMarker(event) {
    return String(event?.generated_by || '') === M5_EXECUTION_GENERATOR && Boolean(simulationExecutionMarkerLabel(event));
  }

  function visibleRangeSimulationRows(state) {
    const source = state?.simulationSource;
    const allRows = state?.simulationAllRows || [];
    return (source ? getChartWindowRows(source, allRows, state) : [])
      .map((row, index) => ({ row, index, reference_ms: rowTimeMs(row) }))
      .filter(item => item.reference_ms != null);
  }

  function nextAnimationFrame() {
    return new Promise(resolve => {
      if (typeof requestAnimationFrame === 'function') requestAnimationFrame(() => resolve());
      else setTimeout(resolve, 0);
    });
  }

  function rangeExecutionSummary(events) {
    const summary = {
      entry_count: 0,
      reentry_count: 0,
      add_on_count: 0,
      close_event_count: 0,
      exit_count: 0,
      profit_close_count: 0,
      loss_close_count: 0,
      break_even_close_count: 0,
      close_ok_count: 0,
      close_miss_count: 0,
      target_exit_count: 0,
      t3_exit_count: 0,
      structural_exit_count: 0,
      anchor_exit_count: 0,
      stop_exit_count: 0,
      execution_event_count: (events || []).length,
      realized_profit_jpy: 0,
      unrealized_profit_jpy: 0,
      total_profit_jpy: 0,
      open_position_count: 0,
      open_trade_count: 0,
      win_rate_pct: 0
    };
    (events || []).forEach(event => {
      const type = simulationRuleAwareEventType(event);
      if (type === 'entry') summary.entry_count += 1;
      else if (type === 'reentry') summary.reentry_count += 1;
      else if (type === 'add_on') summary.add_on_count += 1;
      const isClose = type === 'partial_close' || type === 'close' || type === 'stop_close';
      if (isClose) {
        summary.close_event_count += 1;
        const pnl = Number(event?.execution?.realized_profit_jpy || 0);
        if (pnl > 0.000001) summary.profit_close_count += 1;
        else if (pnl < -0.000001) summary.loss_close_count += 1;
        else summary.break_even_close_count += 1;
        let exitType = String(event?.execution?.exit_type || (type === 'stop_close' ? 'STOP_EXIT' : '')).toUpperCase();
        if (!exitType && (type === 'partial_close' || type === 'close') && event?.execution?.reached_target_label) exitType = 'TARGET_EXIT';
        if (exitType === 'TARGET_EXIT') summary.target_exit_count += 1;
        else if (exitType === 'T3_EXIT') summary.t3_exit_count += 1;
        else if (exitType === 'STRUCTURAL_EXIT') summary.structural_exit_count += 1;
        else if (exitType === 'ANCHOR_EXIT') summary.anchor_exit_count += 1;
        else if (exitType === 'STOP_EXIT' || type === 'stop_close') summary.stop_exit_count += 1;
      }
      summary.realized_profit_jpy += Number(event?.execution?.realized_profit_jpy || 0);
    });
    summary.exit_count = summary.t3_exit_count + summary.structural_exit_count + summary.anchor_exit_count + summary.stop_exit_count;
    // 互換項目。CloseOKは利益決済、CloseMissは損失決済としてのみ数える。
    summary.close_ok_count = summary.profit_close_count;
    summary.close_miss_count = summary.loss_close_count;
    const decided = summary.profit_close_count + summary.loss_close_count;
    summary.win_rate_pct = decided > 0 ? summary.profit_close_count / decided * 100 : 0;
    summary.total_profit_jpy = summary.realized_profit_jpy;
    return summary;
  }

  function batchSimulationOpenPositionSummary(snapshot, currentPrice, ruleLane = '') {
    const positions = snapshot?.position_lifecycle?.portfolio?.positions || [];
    const lane = String(ruleLane || '').toUpperCase();
    const mark = numberOrNull(currentPrice);
    const openPositions = positions.filter(position => {
      const units = Number(position?.units_open || 0);
      const status = String(position?.status || '').toUpperCase();
      const positionLane = String(position?.rule_lane || '').toUpperCase();
      return units > 0 && status !== 'CLOSED' && (!lane || positionLane === lane);
    });
    let unrealized = 0;
    const tradeIds = new Set();
    if (mark != null) {
      openPositions.forEach(position => {
        const entry = numberOrNull(position?.entry_price);
        if (entry == null) return;
        const units = Number(position?.units_open || 0);
        const base = Number(position?.risk_profile?.unit_base_currency_amount || 1000);
        const side = String(position?.side || '').toUpperCase();
        const difference = side === 'SHORT' ? entry - mark : mark - entry;
        unrealized += difference * units * base;
        if (position?.trade_id) tradeIds.add(String(position.trade_id));
      });
    } else {
      openPositions.forEach(position => { if (position?.trade_id) tradeIds.add(String(position.trade_id)); });
    }
    return {
      unrealized_profit_jpy: unrealized,
      open_position_count: openPositions.length,
      open_trade_count: tradeIds.size
    };
  }

  function batchSimulationSummaryWithState(events, snapshot, currentPrice, ruleLane = '') {
    const lane = String(ruleLane || '').toUpperCase();
    const filteredEvents = lane
      ? (events || []).filter(event => batchSimulationEventRuleLane(event) === lane)
      : (events || []);
    const summary = rangeExecutionSummary(filteredEvents);
    const open = batchSimulationOpenPositionSummary(snapshot, currentPrice, lane);
    summary.unrealized_profit_jpy = open.unrealized_profit_jpy;
    summary.total_profit_jpy = summary.realized_profit_jpy + open.unrealized_profit_jpy;
    summary.open_position_count = open.open_position_count;
    summary.open_trade_count = open.open_trade_count;
    return summary;
  }

  function mergeBatchSimulationSummaries(...summaries) {
    const result = rangeExecutionSummary([]);
    const additiveKeys = [
      'entry_count','reentry_count','add_on_count','close_event_count','exit_count',
      'profit_close_count','loss_close_count','break_even_close_count','close_ok_count','close_miss_count',
      'target_exit_count','t3_exit_count','structural_exit_count','anchor_exit_count','stop_exit_count',
      'execution_event_count','realized_profit_jpy','unrealized_profit_jpy','total_profit_jpy',
      'open_position_count','open_trade_count'
    ];
    summaries.filter(Boolean).forEach(summary => {
      additiveKeys.forEach(key => { result[key] = Number(result[key] || 0) + Number(summary?.[key] || 0); });
    });
    const decided = result.profit_close_count + result.loss_close_count;
    result.win_rate_pct = decided > 0 ? result.profit_close_count / decided * 100 : 0;
    return result;
  }

  function incrementRangeDiagnosticCount(target, key) {
    const normalized = String(key || 'UNKNOWN').trim() || 'UNKNOWN';
    target[normalized] = Number(target[normalized] || 0) + 1;
  }

  function topRangeDiagnosticCounts(counts, limit = 4) {
    return Object.entries(counts || {})
      .map(([key, count]) => ({ key, count: Number(count || 0) }))
      .sort((a, b) => b.count - a.count || a.key.localeCompare(b.key))
      .slice(0, Math.max(1, limit));
  }

  function rangeDiagnosticReasonLabel(code) {
    return ({
      UPPER_NO_TRADE: '上位足NoTrade',
      H1_T3_NOT_READY: 'H1 T3判定不能',
      H1_CLOSE_NOT_ABOVE_T3: 'H1終値がT3より上ではない',
      H1_CLOSE_NOT_BELOW_T3: 'H1終値がT3より下ではない',
      H4_H1_T3_NOT_ALIGNED: 'H4/H1 T3方向不一致',
      M5_DOW_NOT_ALIGNED: 'M5方向不一致',
      HSI_ENTRY_ANCHOR_UNRESOLVED: 'HSI起点未解決',
      HSI_R1_NOT_REACHED: 'R1未到達',
      HSI_R2_NOT_REACHED: 'R2未到達',
      POSITION_ALREADY_OPEN: '建玉保有中',
      NORMAL_ENTRY_BLOCKED: '通常Entry禁止',
      NORMAL_ENTRY_CONDITIONAL: '通常Entry条件付き',
      NORMAL_ENTRY_NOT_EVALUATED: '通常Entry未評価',
      H4_REVERSAL_WATCH: 'H4反転監視',
      H4_TREND_UNDETERMINED: 'H4トレンド未確定',
      WEEK_CYCLE_LATE: 'WEEKサイクル終盤',
      WEEK_EXPANSION_SEASON_CLOSED: 'WEEK Expansion終了',
      EXPANSION_CONFIRMATION_NOT_IMPLEMENTED: 'Expansion確定未実装'
    })[String(code || '').toUpperCase()] || String(code || 'UNKNOWN');
  }

  function visibleRangeDiagnosticText(rangeRun) {
    const top = rangeRun?.decision_diagnostics?.top_trigger_reasons || [];
    if (!top.length) return '未成立理由の集計はありません。';
    return top.map(item => `${rangeDiagnosticReasonLabel(item.key)} ${item.count}回`).join(' / ');
  }

  function renderVisibleRangeRunResult(backdrop, state) {
    const node = backdrop?.querySelector?.('[data-role="visible-range-run-result"]');
    if (!node) return;
    const visible = state?.simulationRangeRunNoticeVisible === true;
    node.classList.toggle('is-visible', visible);
    if (!visible) {
      node.innerHTML = '';
      return;
    }
    node.classList.remove('is-running', 'is-zero', 'is-success', 'is-error');
    let title = '';
    let body = '';
    if (state?.simulationRangeRunInProgress === true) {
      node.classList.add('is-running');
      title = '表示範囲Simulation 実行中';
      body = String(state?.simulationRangeRunStatus || '表示中のM5足を古い方から評価しています。');
    } else if (String(state?.simulationRangeRunStatus || '').includes('失敗') || String(state?.simulationRangeRunStatus || '').includes('例外')) {
      node.classList.add('is-error');
      title = '表示範囲Simulationを完了できませんでした';
      body = String(state?.simulationRangeRunStatus || '原因不明');
    } else if (state?.simulationRangeRunSnapshot) {
      const run = state.simulationRangeRunSnapshot;
      const summary = run.summary || {};
      const period = run.period || {};
      const eventCount = Number(summary.execution_event_count || 0);
      const steps = Number(period.completed_step_count || 0);
      if (eventCount <= 0) {
        node.classList.add('is-zero');
        title = `${steps.toLocaleString()}足の判定完了 — Entry / Closeは0件`;
        body = `ボタンは動いています。チャートに印が出ないのは、実行条件が一度も成立しなかったためです。主な未成立理由: ${visibleRangeDiagnosticText(run)}`;
      } else {
        node.classList.add('is-success');
        title = `${steps.toLocaleString()}足の判定完了 — 実行Event ${eventCount}件`;
        body = `Entry ${summary.entry_count || 0} / ReEntry ${summary.reentry_count || 0} / Add-on ${summary.add_on_count || 0} / CloseOK ${summary.close_ok_count || 0} / CloseMiss ${summary.close_miss_count || 0}`;
      }
    } else {
      node.classList.add('is-running');
      title = '表示範囲Simulation';
      body = String(state?.simulationRangeRunStatus || '準備中');
    }
    node.innerHTML = `<div class="gpt-fx-chart-range-result-main"><div class="gpt-fx-chart-range-result-title">${escapeHtml(title)}</div><div class="gpt-fx-chart-range-result-body">${escapeHtml(body)}</div></div><button class="gpt-fx-chart-range-result-close" type="button" data-action="close-visible-range-run-result" title="結果表示を閉じる">×</button>`;
  }

  function compactSimulationContinuationSnapshot(snapshot) {
    if (!snapshot) return null;
    const timeframeStates = cloneJsonValue(snapshot.timeframe_states || null);
    if (timeframeStates) timeframeStates.state_events = [];
    const upperContextDecision = cloneJsonValue(snapshot.upper_context_decision || null);
    if (upperContextDecision) upperContextDecision.decision_events = [];
    const positionLifecycle = cloneJsonValue(snapshot.position_lifecycle || null);
    if (positionLifecycle) {
      positionLifecycle.decision_events = [];
      positionLifecycle.state_change_events = [];
    }
    return {
      run_id: snapshot.run_id,
      profile: cloneJsonValue(snapshot.profile || {}),
      timeframe_states: timeframeStates,
      upper_context_decision: upperContextDecision,
      position_lifecycle: positionLifecycle,
      trace_replay: null
    };
  }

  async function buildVisibleRangeSimulationRun(state, onProgress) {
    const draft = cloneJsonValue(state?.simulationRunDraft || state?.simulationRunProfile || buildEmptySimulationRunProfile());
    const validation = validateSimulationRunDraft(draft);
    if (!validation.valid) return { rangeRun: null, validation };
    const rows = visibleRangeSimulationRows(state);
    if (!rows.length) {
      return {
        rangeRun: null,
        validation: { ...validation, valid: false, errors: [...(validation.errors || []), '現在のM5表示範囲に評価可能な足がありません。'] }
      };
    }
    const workingState = Object.assign(Object.create(state || null), {
      simulationRunDraft: draft,
      simulationRunSnapshot: null,
      simulationRunReferenceOverrideMs: null,
      simulationRunReferenceSource: 'visible_range_step',
      simulationTrace: { ...buildEmptySimulationTrace(state?.simulationSource), run_snapshot: null },
      simulationTraceEvents: [],
      simulationCandleSourceCache: state?.simulationCandleSourceCache || null
    });
    const executionEvents = [];
    const executionEventIds = new Set();
    const simulationHsiAnnotations = [];
    const simulationHsiAnchorIds = new Set();
    const decisionActionCounts = {};
    const triggerReasonCounts = {};
    const normalPermissionCounts = {};
    const ruleLaneCounts = {};
    const evaluatorCounts = {};
    const legacyUpperContextReasonCounts = {};
    const stepErrors = [];
    let finalSnapshot = null;
    let lastMarkPrice = null;
    let completedSteps = 0;
    let lastReportedExecutionCount = 0;
    let lastReportedHsiCount = 0;
    const startedAt = nowLocalIso();
    for (let index = 0; index < rows.length; index += 1) {
      const item = rows[index];
      workingState.simulationRunReferenceOverrideMs = item.reference_ms;
      const result = buildSimulationRunSnapshot(workingState, { skipTraceReplay: true });
      if (result.snapshot) {
        finalSnapshot = result.snapshot;
        completedSteps += 1;
        const trigger = result.snapshot?.position_lifecycle?.trigger_evaluation || {};
        const upperNormal = result.snapshot?.upper_context_decision?.entry_policy?.normal_entry || {};
        incrementRangeDiagnosticCount(decisionActionCounts, trigger.action || 'UNKNOWN');
        (trigger.reason_codes || []).forEach(code => incrementRangeDiagnosticCount(triggerReasonCounts, code));
        incrementRangeDiagnosticCount(normalPermissionCounts, trigger?.permissions?.normal_entry || 'UNKNOWN');
        incrementRangeDiagnosticCount(ruleLaneCounts, trigger.rule_lane || 'UNKNOWN');
        incrementRangeDiagnosticCount(evaluatorCounts, trigger.evaluator_id || 'UNKNOWN');
        // Upper Context Decisionは観測・Expansion用の旧診断として保持するが、Normal Rule LaneのEntry可否には使用しない。
        (upperNormal.reason_codes || []).forEach(code => incrementRangeDiagnosticCount(legacyUpperContextReasonCounts, code));
        const cumulative = result.snapshot?.position_lifecycle?.execution_events || [];
        cumulative.forEach(event => {
          const eventId = String(event?.event_id || '');
          if (!eventId || executionEventIds.has(eventId)) return;
          executionEventIds.add(eventId);
          const markerLabel = simulationExecutionMarkerLabel(event);
          executionEvents.push({
            ...cloneJsonValue(event),
            range_runner_id: VISIBLE_RANGE_SIMULATION_RUNNER_ID,
            range_step_index: index,
            range_step_no: index + 1,
            chart_marker_label: markerLabel,
            display: {
              ...(event.display || {}),
              visible: true,
              open: false,
              pinned: false,
              style: `range_${String(event.event_type || 'execution')}`,
              marker_label: markerLabel
            }
          });
        });
        const entryLinkedExecutionEvents = executionEvents.slice(lastReportedExecutionCount)
          .filter(event => ['entry', 'reentry', 'add_on'].includes(String(event?.event_type || '').toLowerCase()));
        entryLinkedExecutionEvents.forEach(event => {
          const simulationHsi = simulationEntryHsiAnnotationFromSnapshot(result.snapshot, state?.simulationSource, draft, event);
          if (simulationHsi && !simulationHsiAnchorIds.has(simulationHsi.id)) {
            simulationHsiAnchorIds.add(simulationHsi.id);
            simulationHsiAnnotations.push(simulationHsi);
          }
        });
        const continuationSnapshot = compactSimulationContinuationSnapshot(result.snapshot);
        workingState.simulationRunSnapshot = continuationSnapshot;
        workingState.simulationTrace.run_snapshot = continuationSnapshot;
      } else {
        stepErrors.push({
          step_no: index + 1,
          reference_time: String(item.row?.datetime || ''),
          errors: [...(result.validation?.errors || ['Snapshot作成失敗'])]
        });
      }
      const newExecutionEvents = executionEvents.slice(lastReportedExecutionCount);
      const updatedHsiAnnotations = [];
      (newExecutionEvents || []).forEach(event => {
        const retired = retireSimulationHsiAnnotationForExecutionEvent(simulationHsiAnnotations, event);
        if (retired) updatedHsiAnnotations.push(cloneJsonValue(retired));
      });
      const newHsiAnnotations = simulationHsiAnnotations.slice(lastReportedHsiCount);
      const shouldReportProgress = index === 0
        || index === rows.length - 1
        || (index + 1) % 5 === 0
        || newExecutionEvents.length > 0
        || newHsiAnnotations.length > 0
        || updatedHsiAnnotations.length > 0;
      if (typeof onProgress === 'function' && shouldReportProgress) {
        onProgress({
          current: index + 1,
          total: rows.length,
          completed: completedSteps,
          failed: stepErrors.length,
          execution_count: executionEvents.length,
          reference_time: String(item.row?.datetime || ''),
          reference_ms: item.reference_ms,
          new_execution_events: newExecutionEvents.map(event => cloneJsonValue(event)),
          new_hsi_annotations: newHsiAnnotations.map(annotation => cloneJsonValue(annotation)),
          updated_hsi_annotations: updatedHsiAnnotations,
          hsi_anchor_count: simulationHsiAnnotations.length
        });
        lastReportedExecutionCount = executionEvents.length;
        lastReportedHsiCount = simulationHsiAnnotations.length;
      }
      if ((index + 1) % 5 === 0 || newExecutionEvents.length > 0 || newHsiAnnotations.length > 0 || updatedHsiAnnotations.length > 0) await nextAnimationFrame();
    }
    const summary = rangeExecutionSummary(executionEvents);
    const firstRow = rows[0]?.row || {};
    const lastRow = rows[rows.length - 1]?.row || {};
    const rangeRun = {
      schema_version: 'fx_visible_range_simulation_run_v0_1',
      kind: 'fx_visible_range_simulation_run',
      runner_id: VISIBLE_RANGE_SIMULATION_RUNNER_ID,
      run_id: `sim_range_${compactTimestamp()}`,
      status: finalSnapshot ? (stepErrors.length ? 'completed_with_step_errors' : 'completed') : 'failed',
      started_at: startedAt,
      completed_at: nowLocalIso(),
      profile_id: draft.profile_id || '',
      rule_version: draft.rule_version || '',
      period: {
        mode: 'current_chart_window',
        from: String(firstRow.datetime || ''),
        to: String(lastRow.datetime || ''),
        requested_step_count: rows.length,
        completed_step_count: completedSteps,
        failed_step_count: stepErrors.length,
        final_mark_price: lastMarkPrice
      },
      initial_position_policy: 'FLAT_AT_VISIBLE_RANGE_START',
      execution_events: executionEvents,
      simulation_hsi_annotations: simulationHsiAnnotations,
      summary: { ...summary, simulation_hsi_anchor_count: simulationHsiAnnotations.length },
      decision_diagnostics: {
        evaluated_step_count: completedSteps,
        action_counts: decisionActionCounts,
        trigger_reason_counts: triggerReasonCounts,
        normal_entry_permission_counts: normalPermissionCounts,
        rule_lane_counts: ruleLaneCounts,
        evaluator_counts: evaluatorCounts,
        legacy_upper_context_reason_counts: legacyUpperContextReasonCounts,
        upper_context_affects_normal_rule_lane: false,
        top_trigger_reasons: topRangeDiagnosticCounts(triggerReasonCounts, 5),
        top_legacy_upper_context_reasons: topRangeDiagnosticCounts(legacyUpperContextReasonCounts, 5)
      },
      step_errors: stepErrors.slice(0, 50),
      final_snapshot: finalSnapshot,
      validation: {
        valid: Boolean(finalSnapshot),
        checked_at: nowLocalIso(),
        errors: finalSnapshot ? [] : ['表示範囲内で有効なSnapshotを作成できませんでした。'],
        warnings: stepErrors.length ? [`${stepErrors.length}地点で評価をスキップしました。`] : []
      },
      teacher_guard: [ENTRY_LANE_MODE_NORMAL_AND_EXPANSION_LITE, ENTRY_LANE_MODE_PARALLEL_RULE_LANES].includes(String(draft?.m5_execution_policy?.rule_lane_policy?.active_entry_rule_lane || '').toUpperCase())
        ? '現在表示中のM5範囲を古い足から順に評価し、各Rule Laneを独立Portfolioとしてパラレル判定します。同一足で複数Entryが成立した場合も、成立した全LaneのEntryを残します。条件・起点・Close条件は相互流用しません。'
        : String(draft?.m5_execution_policy?.rule_lane_policy?.active_entry_rule_lane || '').toUpperCase() === RULE_LANE_EXPANSION_LITE
          ? '現在表示中のM5範囲を古い足から順に評価するExpansion-Lite専用仮想検証です。NORMAL / EXPANSIONへFallbackせず、Day Cycle PositionもEntry条件へ使用しません。表示範囲開始時点は建玉なしです。'
          : '現在表示中のM5範囲を古い足から順に評価したNORMAL専用仮想検証です。WEEK/DAY/Expansionの旧Upper Context診断は通常Entry可否へ影響しません。表示範囲開始時点は建玉なしです。'
    };
    return { rangeRun, validation: rangeRun.validation };
  }

  function commitVisibleRangeSimulationRun(state, source, rangeRun) {
    const finalSnapshot = rangeRun?.final_snapshot || null;
    state.simulationRunSnapshot = finalSnapshot;
    state.simulationRangeRunSnapshot = rangeRun;
    state.simulationTrace = state.simulationTrace || buildEmptySimulationTrace(source);
    state.simulationTrace.run = {
      ...(state.simulationTrace.run || {}),
      run_id: rangeRun.run_id,
      status: rangeRun.status,
      rule_version: rangeRun.rule_version,
      profile_id: rangeRun.profile_id,
      phase: 'v0.9.0.16-simulation-focus-ui',
      generated_at: rangeRun.completed_at,
      engine_enabled: true,
      range_runner_enabled: true,
      trade_execution_enabled: true,
      note: '現在のM5表示範囲を古い足から順番に自動評価し、Entry / CloseOK / CloseMissとSimulation専用HSI起点/R線をチャートへライブ投影。Human HSI/Userコメントは実行開始時に自動OFF。'
    };
    state.simulationTrace.range_run = cloneJsonValue({
      ...rangeRun,
      final_snapshot: undefined,
      execution_events: undefined,
      execution_event_ids: (rangeRun.execution_events || []).map(event => event.event_id).filter(Boolean)
    });
    state.simulationHsiAnnotations = cloneJsonValue(rangeRun.simulation_hsi_annotations || []);
    state.simulationTrace.simulation_hsi_annotations = cloneJsonValue(state.simulationHsiAnnotations);
    state.simulationTrace.run_snapshot = finalSnapshot;
    state.simulationTrace.run_result = {
      status: rangeRun.status,
      ...cloneJsonValue(rangeRun.summary || {}),
      open_position_ids: finalSnapshot?.run_result?.open_position_ids || [],
      trade_ids: finalSnapshot?.run_result?.trade_ids || [],
      teacher_guard: rangeRun.teacher_guard
    };
    state.simulationTrace.trace_replay = finalSnapshot?.trace_replay || null;
    state.simulationTraceReplaySnapshot = finalSnapshot?.trace_replay || null;
    state.simulationTraceReplaySequence = finalSnapshot?.trace_replay?.events?.length || 0;
    state.simulationPositionLifecycleSnapshot = finalSnapshot?.position_lifecycle || null;
    state.simulationTraceEvents = (rangeRun.execution_events || []).map(event => normalizeSimulationTrace({ events: [event] }, source).events[0]);
    state.simulationTrace.events = state.simulationTraceEvents;
    state.showSimulationComments = true;
    state.showAllSimulationComments = false;
    state.openSimulationTraceId = null;
    state.simulationRunReferenceOverrideMs = null;
    state.simulationRunReferenceSource = null;
    state.simulationTrace.run.execution_event_count = rangeRun.summary?.execution_event_count || 0;
    state.simulationTrace.run.entry_count = rangeRun.summary?.entry_count || 0;
    state.simulationTrace.run.close_ok_count = rangeRun.summary?.close_ok_count || 0;
    state.simulationTrace.run.close_miss_count = rangeRun.summary?.close_miss_count || 0;
    state.simulationTrace.run.chart_projection_event_count = state.simulationTraceEvents.length;
  }

  async function saveSimulationTraceSidecar(state, source, backdrop) {
    if (!state?.simulationTrace) return false;
    const paths = getSimulationTracePaths(source);
    const payload = cloneJsonValue(state.simulationTrace);
    delete payload?._loaded_from;
    payload.updated_at = nowLocalIso();
    payload.events = state.simulationTraceEvents || payload.events || [];
    try {
      const response = await fetch(paths.apiPath, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload, null, 2)
      });
      if (!response.ok) throw new Error(`${response.status} ${response.statusText}`);
      state.simulationTrace = normalizeSimulationTrace(payload, source);
      state.simulationTrace._loaded_from = 'api:saved';
      state.simulationTraceEvents = state.simulationTrace.events || [];
      state.simulationTraceLoadStatus = `saved:${paths.file}`;
      applyModeButtonState(backdrop, state);
      return true;
    } catch (err) {
      console.warn('[GPT FX Lab] simulation trace sidecar save failed', err);
      state.simulationTraceLoadStatus = `save failed:${paths.file}`;
      applyModeButtonState(backdrop, state);
      return false;
    }
  }


  function batchSimulationSettings() {
    const raw = pluginManifest?.display_policy?.batch_simulation_runner
      || pluginManifest?.chart_viewer_policy?.batch_simulation_runner
      || {};
    return {
      enabled: raw.enabled !== false,
      manifest_path: String(raw.manifest_path || BATCH_SIMULATION_MANIFEST_PATH),
      execution_mode: String(raw.execution_mode || 'SEQUENTIAL_CASES'),
      progress_yield_every_bars: Math.max(1, Math.floor(numberOrNull(raw.progress_yield_every_bars) ?? 250)),
      progress_event_min_interval_ms: Math.max(100, Math.floor(numberOrNull(raw.progress_event_min_interval_ms) ?? 500)),
      hide_chart_during_batch: raw.hide_chart_during_batch !== false,
      suppress_chart_redraw_during_batch: raw.suppress_chart_redraw_during_batch !== false,
      result_api_root: String(raw.result_api_root || 'gpt_fx_lab/simulation/results'),
      fallback_result_api_root: String(raw.fallback_result_api_root || 'gpt_fx_lab/simulation'),
      default_period_mode: String(raw.default_period_mode || 'FULL_DATASET').toUpperCase(),
      show_cumulative_realized_profit: raw.show_cumulative_realized_profit !== false,
      stop_check_every_bars: Math.max(1, Math.floor(numberOrNull(raw.stop_check_every_bars) ?? 1))
    };
  }

  function applyBatchSimulationVisualMode(backdrop, state) {
    const settings = batchSimulationSettings();
    const running = state?.batchSimulationRunInProgress === true;
    backdrop?.classList?.toggle('is-batch-running', running && settings.hide_chart_during_batch);
  }

  function batchSimulationNormalizeDataPath(value) {
    const raw = String(value || '').trim().replace(/\\/g, '/');
    if (!raw) return DEFAULT_URL_DATA;
    if (raw.startsWith('overlay/')) return raw;
    if (raw.startsWith('studio_overlays/')) return `overlay/${raw.slice('studio_overlays/'.length)}`;
    if (raw.startsWith('gpt_fx_lab/')) return `overlay/${raw}`;
    if (raw.startsWith('data/')) return `overlay/gpt_fx_lab/${raw}`;
    return raw.includes('/') ? raw : `overlay/gpt_fx_lab/data/${raw}`;
  }

  function batchSimulationCurrentDataPath() {
    return batchSimulationNormalizeDataPath(currentJsonParam('dataNameInput', DEFAULT_URL_DATA));
  }

  function batchSimulationDatasetLabel(pathValue) {
    const path = batchSimulationNormalizeDataPath(pathValue);
    const file = path.split('/').pop() || path;
    return file.replace(/\.json$/i, '');
  }

  async function loadBatchSimulationDatasetCatalog(state) {
    const currentPath = batchSimulationCurrentDataPath();
    const paths = [currentPath];
    const settings = batchSimulationSettings();
    let manifest = null;
    try {
      manifest = await fetchJsonIfExists('/api/overlays/gpt_fx_lab/studio_manifest.json');
    } catch {
      try { manifest = await fetchJsonIfExists(settings.manifest_path); } catch { manifest = null; }
    }
    (manifest?.data_files || []).forEach(item => {
      const normalized = batchSimulationNormalizeDataPath(item);
      if (!paths.includes(normalized)) paths.push(normalized);
    });
    state.batchSimulationDatasetCatalog = paths.map(path => ({
      path,
      label: batchSimulationDatasetLabel(path),
      current: path === currentPath
    }));
    state.batchSimulationDatasetCatalogStatus = `loaded:${state.batchSimulationDatasetCatalog.length}`;
    if (!state.batchSimulationDraft?.dataset_paths?.length) {
      state.batchSimulationDraft = {
        ...(state.batchSimulationDraft || {}),
        dataset_paths: [currentPath]
      };
    }
    return state.batchSimulationDatasetCatalog;
  }

  function buildEmptyBatchSimulationDraft(state) {
    const settings = batchSimulationSettings();
    const source = state?.simulationSource;
    return {
      dataset_paths: [batchSimulationCurrentDataPath()],
      period_mode: settings.default_period_mode,
      period_from: String(source?.date_from || ''),
      period_to: String(source?.date_to || ''),
      case_execution_mode: settings.execution_mode,
      persist_results: true
    };
  }

  function validateBatchSimulationDraft(state, draft) {
    const errors = [];
    const warnings = [];
    if (state?.simulationRunValidation?.valid !== true) errors.push('Run ProfileがREADYではありません。');
    const datasetPaths = uniqueStrings((draft?.dataset_paths || []).map(batchSimulationNormalizeDataPath));
    if (!datasetPaths.length) errors.push('対象Datasetを1件以上選択してください。');
    const mode = String(draft?.period_mode || 'FULL_DATASET').toUpperCase();
    if (!['FULL_DATASET', 'CUSTOM'].includes(mode)) errors.push('期間モードが不正です。');
    if (mode === 'CUSTOM') {
      const fromMs = parseDateTimeMs(draft?.period_from);
      const toMs = parseDateTimeMs(draft?.period_to);
      if (fromMs == null || toMs == null) errors.push('開始・終了日時を入力してください。');
      else if (fromMs > toMs) errors.push('開始日時が終了日時より後です。');
    }
    if (datasetPaths.length > 1) warnings.push('v0.1はCaseを直列実行します。');
    return { valid: errors.length === 0, errors, warnings, dataset_paths: datasetPaths, checked_at: nowLocalIso() };
  }

  function readBatchSimulationDraftFromDialog(dialog, state) {
    const draft = cloneJsonValue(state?.batchSimulationDraft || buildEmptyBatchSimulationDraft(state));
    draft.dataset_paths = [...dialog.querySelectorAll('[data-batch-dataset-path]:checked')]
      .map(input => batchSimulationNormalizeDataPath(input.getAttribute('data-batch-dataset-path')));
    draft.period_mode = String(dialog.querySelector('[data-batch-period-mode]')?.value || 'FULL_DATASET').toUpperCase();
    draft.period_from = String(dialog.querySelector('[data-batch-period-from]')?.value || '').trim();
    draft.period_to = String(dialog.querySelector('[data-batch-period-to]')?.value || '').trim();
    state.batchSimulationDraft = draft;
    state.batchSimulationValidation = validateBatchSimulationDraft(state, draft);
    return draft;
  }

  function batchSimulationPrimaryWarmupBars(profile) {
    const primaryMinutes = 5;
    let maximum = 0;
    (profile?.timeframe_profiles || []).forEach(item => {
      const mapping = item?.source_mapping || {};
      if (String(mapping.source_dataset_role || '').toLowerCase() !== 'primary') return;
      const bars = Math.max(0, Math.floor(numberOrNull(item?.warmup?.bars) ?? 0));
      const timeframe = normalizePanelTimeframe(item?.timeframe, String(item?.timeframe || 'M5').toUpperCase());
      const ratio = Math.max(1, Math.round(panelTimeframeMinutes(timeframe) / primaryMinutes));
      maximum = Math.max(maximum, bars * ratio);
    });
    return maximum;
  }

  function batchSimulationRowPlan(source, draft, profile) {
    const rows = normalizeAllRows(source)
      .map((row, index) => ({ row, source_index: index, reference_ms: rowTimeMs(row) }))
      .filter(item => item.reference_ms != null);
    if (!rows.length) return { valid: false, errors: ['DatasetにM5足がありません。'], rows: [] };
    const mode = String(draft?.period_mode || 'FULL_DATASET').toUpperCase();
    const firstMs = rows[0].reference_ms;
    const lastMs = rows[rows.length - 1].reference_ms;
    const requestedFrom = mode === 'CUSTOM' ? parseDateTimeMs(draft?.period_from) : firstMs;
    const requestedTo = mode === 'CUSTOM' ? parseDateTimeMs(draft?.period_to) : lastMs;
    const fromMs = requestedFrom == null ? firstMs : Math.max(firstMs, requestedFrom);
    const toMs = requestedTo == null ? lastMs : Math.min(lastMs, requestedTo);
    const targetStartIndex = rows.findIndex(item => item.reference_ms >= fromMs);
    let targetEndIndex = -1;
    for (let index = rows.length - 1; index >= 0; index -= 1) {
      if (rows[index].reference_ms <= toMs) { targetEndIndex = index; break; }
    }
    if (targetStartIndex < 0 || targetEndIndex < targetStartIndex) {
      return { valid: false, errors: ['指定期間に評価可能なM5足がありません。'], rows: [] };
    }
    const warmupBars = mode === 'CUSTOM' ? batchSimulationPrimaryWarmupBars(profile) : 0;
    const processStartIndex = Math.max(0, targetStartIndex - warmupBars);
    return {
      valid: true,
      errors: [],
      all_rows: rows,
      process_rows: rows.slice(processStartIndex, targetEndIndex + 1),
      process_start_index: processStartIndex,
      target_start_index: targetStartIndex,
      target_end_index: targetEndIndex,
      warmup_bar_count: targetStartIndex - processStartIndex,
      target_bar_count: targetEndIndex - targetStartIndex + 1,
      period: {
        mode,
        from: String(rows[targetStartIndex]?.row?.datetime || ''),
        to: String(rows[targetEndIndex]?.row?.datetime || ''),
        from_ms: rows[targetStartIndex]?.reference_ms,
        to_ms: rows[targetEndIndex]?.reference_ms
      }
    };
  }

  function batchSimulationAnalysisWindow(rowPlan, allRows) {
    const total = Math.max(0, Array.isArray(allRows) ? allRows.length : 0);
    const requestedStart = Math.max(0, Math.floor(numberOrNull(rowPlan?.target_start_index) ?? 0));
    const requestedEnd = Math.max(requestedStart, Math.floor(numberOrNull(rowPlan?.target_end_index) ?? Math.max(0, total - 1)));
    const start = Math.min(requestedStart, Math.max(0, total - 1));
    const endExclusive = total > 0 ? Math.min(total, requestedEnd + 1) : 0;
    const size = Math.max(1, endExclusive - start);
    return {
      source: 'BATCH_TARGET_PERIOD',
      window_start: start,
      window_size: size,
      window_end_exclusive: endExclusive,
      period_from: String(rowPlan?.period?.from || ''),
      period_to: String(rowPlan?.period?.to || '')
    };
  }

  async function loadBatchSimulationUpperMapData(profile, state) {
    const configuredPath = profile?.dataset?.upper_map?.path
      || state?.upperMapDataPath
      || defaultUpperMapDataPath();
    const normalizedPath = normalizeUpperMapDataPath(configuredPath);
    try {
      const loaded = await loadUpperMapDataSource(normalizedPath);
      const rows = normalizeAllRows(loaded.source);
      if (!rows.length) throw new Error(`UpperMap DAY Datasetに足がありません: ${normalizedPath}`);
      return { ...loaded, path: normalizedPath, rows };
    } catch (error) {
      const inheritedRows = normalizeAllRows(state?.upperMapSource || {});
      if (inheritedRows.length) {
        return {
          source: state.upperMapSource,
          path: normalizedPath,
          rows: inheritedRows,
          from: 'current_chart_fallback',
          warning: `Profile UpperMapの再読込に失敗したため、現在チャートで読込済みのUpperMapを使用: ${String(error?.message || error)}`
        };
      }
      throw error;
    }
  }

  function batchSimulationEventRuleLane(event) {
    return String(event?.rule_lane || event?.execution?.rule_lane || RULE_LANE_NORMAL).toUpperCase();
  }

  function batchSimulationLaneSummaries(events, snapshot = null, currentPrice = null) {
    const result = {};
    [RULE_LANE_NORMAL, RULE_LANE_EXPANSION, RULE_LANE_EXPANSION_LITE].forEach(lane => {
      result[lane] = batchSimulationSummaryWithState(events, snapshot, currentPrice, lane);
    });
    return result;
  }

  function batchSimulationProfitClass(value) {
    const amount = Number(value || 0);
    return amount > 0 ? 'is-positive' : amount < 0 ? 'is-negative' : '';
  }

  function batchSimulationFormatJpy(value) {
    const amount = Number(value || 0);
    const sign = amount > 0 ? '+' : '';
    return `${sign}${Math.round(amount).toLocaleString()}円`;
  }

  function compactBatchSimulationContinuationSnapshot(snapshot) {
    const compact = compactSimulationContinuationSnapshot(snapshot);
    if (compact?.position_lifecycle) compact.position_lifecycle.execution_events = [];
    return compact;
  }

  async function batchSimulationDatasetSha256(source) {
    const text = JSON.stringify(source || {});
    try {
      if (globalThis.crypto?.subtle && typeof TextEncoder !== 'undefined') {
        const digest = await globalThis.crypto.subtle.digest('SHA-256', new TextEncoder().encode(text));
        return [...new Uint8Array(digest)].map(value => value.toString(16).padStart(2, '0')).join('');
      }
    } catch { }
    return `fnv1a32-${stableTextHash(text)}`;
  }

  async function loadBatchSimulationPrimaryData(path, state) {
    const normalized = batchSimulationNormalizeDataPath(path);
    if (normalized === batchSimulationCurrentDataPath() && state?.simulationSource) {
      return { source: state.simulationSource, path: normalized, from: 'current' };
    }
    const loaded = await loadUpperMapDataSource(normalized);
    return { source: loaded.source, path: normalized, from: loaded.from };
  }

  async function buildBatchSimulationDatasetDescriptor(source, path) {
    const sha256 = await batchSimulationDatasetSha256(source);
    return {
      dataset_id: String(source?.dataset_id || source?.schema_version || batchSimulationDatasetLabel(path)),
      path: batchSimulationNormalizeDataPath(path).replace(/^overlay\//, 'studio_overlays/'),
      sha256,
      symbol: String(source?.symbol || ''),
      timeframe: String(source?.timeframe || source?.timeframe_label || 'M5'),
      row_count: Number(source?.row_count || normalizeAllRows(source).length || 0),
      date_from: String(source?.date_from || ''),
      date_to: String(source?.date_to || '')
    };
  }

  function batchSimulationCaseId(batchId, index, path) {
    return `${batchId}_case_${String(index + 1).padStart(3, '0')}_${stableTextHash(path)}`;
  }

  function batchSimulationCaseFocusWindow(caseResult) {
    const event = (caseResult?.execution_events || [])[0];
    return {
      first_event_time: String(event?.simulation_time || caseResult?.period?.from || ''),
      first_event_ms: numberOrNull(event?.simulation_time_ms) ?? parseDateTimeMs(event?.simulation_time || caseResult?.period?.from)
    };
  }

  async function executeBatchSimulationCase(state, batchId, caseIndex, caseDraft, onProgress) {
    const loaded = await loadBatchSimulationPrimaryData(caseDraft.dataset_path, state);
    const source = loaded.source;
    const allRows = normalizeAllRows(source);
    const profile = cloneJsonValue(state?.simulationRunDraft || state?.simulationRunProfile || buildEmptySimulationRunProfile());
    const descriptor = await buildBatchSimulationDatasetDescriptor(source, loaded.path);
    profile.dataset = cloneJsonValue(profile.dataset || {});
    profile.dataset.primary = descriptor;
    profile.period_policy = {
      mode: String(caseDraft.period_mode || 'FULL_DATASET').toLowerCase(),
      from: String(caseDraft.period_from || source?.date_from || ''),
      to: String(caseDraft.period_to || source?.date_to || ''),
      batch_case: true
    };
    const validation = validateSimulationRunDraft(profile);
    const caseId = batchSimulationCaseId(batchId, caseIndex, loaded.path);
    if (!validation.valid) {
      return { case_id: caseId, status: 'failed', dataset: descriptor, validation, execution_events: [], summary: rangeExecutionSummary([]), lane_summaries: batchSimulationLaneSummaries([]) };
    }
    const rowPlan = batchSimulationRowPlan(source, caseDraft, profile);
    if (!rowPlan.valid) {
      return { case_id: caseId, status: 'failed', dataset: descriptor, validation: { valid: false, errors: rowPlan.errors, warnings: [] }, execution_events: [], summary: rangeExecutionSummary([]), lane_summaries: batchSimulationLaneSummaries([]) };
    }
    let upperLoaded;
    try {
      upperLoaded = await loadBatchSimulationUpperMapData(profile, state);
    } catch (error) {
      return {
        case_id: caseId,
        status: 'failed',
        dataset: descriptor,
        validation: { valid: false, errors: [`UpperMap DAY DatasetをCase用に読込できませんでした: ${String(error?.message || error)}`], warnings: [] },
        execution_events: [],
        summary: rangeExecutionSummary([]),
        lane_summaries: batchSimulationLaneSummaries([])
      };
    }
    const upperDescriptor = await buildBatchSimulationDatasetDescriptor(upperLoaded.source, upperLoaded.path);
    profile.dataset.upper_map = upperDescriptor;
    const analysisWindow = batchSimulationAnalysisWindow(rowPlan, allRows);
    const confirmBarsByTf = simulationRunConfirmBarsMap(profile);
    const workingState = Object.assign(Object.create(state || null), {
      simulationSource: source,
      simulationAllRows: allRows,
      upperMapSource: upperLoaded.source,
      upperMapAllRows: upperLoaded.rows,
      upperMapDataPath: upperLoaded.path,
      windowStart: analysisWindow.window_start,
      windowSize: analysisWindow.window_size,
      windowEndExclusive: analysisWindow.window_end_exclusive,
      syncCenterTimeMs: null,
      chartLayout: 'm5_execution',
      upperTimeframe: 'H1',
      confirmBars: confirmBarsByTf.M5,
      upperConfirmBars: confirmBarsByTf.H1,
      dayConfirmBars: confirmBarsByTf.DAY,
      weekConfirmBars: confirmBarsByTf.WEEK,
      simulationRunDraft: profile,
      simulationRunSnapshot: null,
      simulationRunReferenceOverrideMs: null,
      simulationRunReferenceSource: 'batch_case_step',
      simulationTrace: { ...buildEmptySimulationTrace(source), run_snapshot: null },
      simulationTraceEvents: [],
      simulationCandleSourceCache: null
    });
    const executionEvents = [];
    const executionEventIds = new Set();
    const stepErrors = [];
    let finalSnapshot = null;
    let completedSteps = 0;
    const settings = batchSimulationSettings();
    const startedAt = nowLocalIso();
    let lastProgressReportAtMs = 0;
    for (let index = 0; index < rowPlan.process_rows.length; index += 1) {
      if (state?.batchSimulationStopRequested === true) break;
      const item = rowPlan.process_rows[index];
      const eventCountBeforeStep = executionEvents.length;
      lastMarkPrice = numberOrNull(item?.row?.close);
      workingState.simulationRunReferenceOverrideMs = item.reference_ms;
      const result = buildSimulationRunSnapshot(workingState, { skipTraceReplay: true });
      if (result.snapshot) {
        finalSnapshot = result.snapshot;
        completedSteps += 1;
        const currentEvents = result.snapshot?.position_lifecycle?.execution_events || [];
        currentEvents.forEach(event => {
          const eventId = String(event?.event_id || '');
          if (!eventId || executionEventIds.has(eventId)) return;
          executionEventIds.add(eventId);
          const eventMs = numberOrNull(event?.simulation_time_ms) ?? parseDateTimeMs(event?.simulation_time);
          if (eventMs == null || eventMs < rowPlan.period.from_ms || eventMs > rowPlan.period.to_ms) return;
          executionEvents.push({
            ...cloneJsonValue(event),
            batch_runner_id: BATCH_SIMULATION_RUNNER_ID,
            batch_run_id: batchId,
            case_id: caseId,
            case_step_no: index + 1
          });
        });
        const continuation = compactBatchSimulationContinuationSnapshot(result.snapshot);
        workingState.simulationRunSnapshot = continuation;
        workingState.simulationTrace.run_snapshot = continuation;
      } else {
        stepErrors.push({ step_no: index + 1, reference_time: String(item.row?.datetime || ''), errors: [...(result.validation?.errors || ['Snapshot作成失敗'])] });
      }
      const progressNowMs = Date.now();
      const periodicProgress = (index + 1) % settings.progress_yield_every_bars === 0;
      const executionEventChanged = executionEvents.length > eventCountBeforeStep;
      const executionEventReportDue = executionEventChanged
        && progressNowMs - lastProgressReportAtMs >= settings.progress_event_min_interval_ms;
      const shouldReport = index === 0
        || index === rowPlan.process_rows.length - 1
        || periodicProgress
        || executionEventReportDue;
      if (shouldReport && typeof onProgress === 'function') {
        lastProgressReportAtMs = progressNowMs;
        const summary = batchSimulationSummaryWithState(executionEvents, finalSnapshot, lastMarkPrice);
        onProgress({
          case_id: caseId,
          case_index: caseIndex,
          current: index + 1,
          total: rowPlan.process_rows.length,
          warmup_bar_count: rowPlan.warmup_bar_count,
          target_bar_count: rowPlan.target_bar_count,
          phase: item.source_index < rowPlan.target_start_index ? 'WARMUP' : 'TARGET',
          reference_time: String(item.row?.datetime || ''),
          mark_price: lastMarkPrice,
          execution_count: executionEvents.length,
          failed_step_count: stepErrors.length,
          latest_step_error: stepErrors.length ? cloneJsonValue(stepErrors[stepErrors.length - 1]) : null,
          summary,
          realized_profit_jpy: summary.realized_profit_jpy,
          unrealized_profit_jpy: summary.unrealized_profit_jpy,
          total_profit_jpy: summary.total_profit_jpy,
          lane_summaries: batchSimulationLaneSummaries(executionEvents, finalSnapshot, lastMarkPrice)
        });
      }
      if (periodicProgress) await nextAnimationFrame();
    }
    const stopped = state?.batchSimulationStopRequested === true;
    const summary = batchSimulationSummaryWithState(executionEvents, finalSnapshot, lastMarkPrice);
    const laneSummaries = batchSimulationLaneSummaries(executionEvents, finalSnapshot, lastMarkPrice);
    const focus = batchSimulationCaseFocusWindow({ execution_events: executionEvents, period: rowPlan.period });
    const result = {
      schema_version: 'fx_batch_simulation_case_result_v0_1',
      kind: 'fx_batch_simulation_case_result',
      case_id: caseId,
      batch_run_id: batchId,
      status: stopped ? 'stopped' : finalSnapshot ? (stepErrors.length ? 'completed_with_step_errors' : 'completed') : 'failed',
      started_at: startedAt,
      completed_at: nowLocalIso(),
      dataset: descriptor,
      source_mapping_snapshot: {
        primary: descriptor,
        upper_map: upperDescriptor,
        primary_loaded_from: loaded.from,
        upper_map_loaded_from: upperLoaded.from,
        upper_map_warning: String(upperLoaded.warning || '')
      },
      analysis_window: analysisWindow,
      profile_snapshot: {
        profile_id: profile.profile_id || '',
        rule_version: profile.rule_version || '',
        app_version: String(pluginManifest?.version || ''),
        profile_hash: stableTextHash(JSON.stringify(profile))
      },
      period: rowPlan.period,
      processing: {
        warmup_bar_count: rowPlan.warmup_bar_count,
        requested_step_count: rowPlan.process_rows.length,
        completed_step_count: completedSteps,
        failed_step_count: stepErrors.length
      },
      execution_events: executionEvents,
      summary,
      lane_summaries: laneSummaries,
      focus,
      open_position_ids: finalSnapshot?.position_lifecycle?.run_result?.open_position_ids || [],
      final_state: finalSnapshot ? compactBatchSimulationContinuationSnapshot(finalSnapshot) : null,
      normal_entry_gate_failures: finalSnapshot
        ? batchSimulationNormalGateFailureRowsFromSnapshot(finalSnapshot, { case_id: caseId, dataset_path: descriptor.path })
        : [],
      step_errors: stepErrors.slice(0, 100),
      validation: { valid: Boolean(finalSnapshot) && !stopped, errors: finalSnapshot ? [] : ['有効な最終Snapshotを作成できませんでした。'], warnings: stepErrors.length ? [`${stepErrors.length}地点で評価をスキップしました。`] : [] }
    };
    result.normal_entry_gate_failure_summary = batchSimulationNormalGateFailureSummary(result.normal_entry_gate_failures);
    result.result_hash = stableTextHash(JSON.stringify({ case_id: result.case_id, status: result.status, summary: result.summary, event_ids: executionEvents.map(event => event.event_id), normal_entry_gate_failure_summary: result.normal_entry_gate_failure_summary }));
    return result;
  }

  function combineBatchSimulationResults(caseResults) {
    const normalizedCases = (caseResults || []).map(item => ({
      ...item,
      summary: item?.summary || rangeExecutionSummary(item?.execution_events || []),
      lane_summaries: item?.lane_summaries || batchSimulationLaneSummaries(item?.execution_events || [])
    }));
    const summary = mergeBatchSimulationSummaries(...normalizedCases.map(item => item.summary));
    const laneSummaries = {};
    [RULE_LANE_NORMAL, RULE_LANE_EXPANSION, RULE_LANE_EXPANSION_LITE].forEach(lane => {
      laneSummaries[lane] = mergeBatchSimulationSummaries(...normalizedCases.map(item => item?.lane_summaries?.[lane]));
    });
    return {
      ...summary,
      case_count: (caseResults || []).length,
      completed_case_count: (caseResults || []).filter(item => String(item.status).startsWith('completed')).length,
      failed_case_count: (caseResults || []).filter(item => item.status === 'failed').length,
      stopped_case_count: (caseResults || []).filter(item => item.status === 'stopped').length,
      lane_summaries: laneSummaries
    };
  }

  function batchSimulationCasePathKey(value) {
    return batchSimulationNormalizeDataPath(value).replace(/^overlay\//, '').replace(/^studio_overlays\//, '');
  }

  function batchSimulationExistingCaseByPath(batchRun, datasetPath) {
    const key = batchSimulationCasePathKey(datasetPath);
    return (batchRun?.cases || []).find(item => batchSimulationCasePathKey(item?.dataset?.path || '') === key) || null;
  }

  function batchSimulationShouldExecuteCase(existingCase, mode) {
    const normalizedMode = String(mode || 'fresh').toLowerCase();
    if (normalizedMode === 'fresh') return true;
    if (!existingCase) return true;
    const status = String(existingCase.status || '').toLowerCase();
    if (normalizedMode === 'resume') return !status.startsWith('completed');
    if (normalizedMode === 'retry_failed') return status === 'failed' || status === 'completed_with_step_errors';
    return true;
  }

  async function buildBatchSimulationRun(state, draft, onProgress, options = {}) {
    const validation = validateBatchSimulationDraft(state, draft);
    if (!validation.valid) return { batchRun: null, validation };
    const existingBatchRun = options?.existing_batch_run || null;
    const executionMode = String(options?.mode || 'fresh').toLowerCase();
    const batchId = existingBatchRun?.batch_run_id || `batch_${compactTimestamp()}`;
    const startedAt = nowLocalIso();
    const caseResults = [];
    const datasetPaths = validation.dataset_paths;
    let executedCaseCount = 0;
    let skippedCaseCount = 0;
    for (let index = 0; index < datasetPaths.length; index += 1) {
      if (state?.batchSimulationStopRequested === true) break;
      const path = datasetPaths[index];
      const existingCase = batchSimulationExistingCaseByPath(existingBatchRun, path);
      if (!batchSimulationShouldExecuteCase(existingCase, executionMode)) {
        caseResults.push(cloneJsonValue(existingCase));
        skippedCaseCount += 1;
        continue;
      }
      const completedBefore = combineBatchSimulationResults(caseResults);
      const caseDraft = {
        dataset_path: path,
        period_mode: draft.period_mode,
        period_from: draft.period_from,
        period_to: draft.period_to
      };
      const caseResult = await executeBatchSimulationCase(state, batchId, index, caseDraft, progress => {
        const progressSummary = mergeBatchSimulationSummaries(completedBefore, progress.summary);
        const laneTotals = {};
        [RULE_LANE_NORMAL, RULE_LANE_EXPANSION, RULE_LANE_EXPANSION_LITE].forEach(lane => {
          laneTotals[lane] = mergeBatchSimulationSummaries(completedBefore.lane_summaries?.[lane], progress.lane_summaries?.[lane]);
        });
        if (typeof onProgress === 'function') onProgress({
          batch_run_id: batchId,
          execution_mode: executionMode,
          case_index: index,
          case_no: index + 1,
          case_total: datasetPaths.length,
          dataset_path: path,
          case_progress: progress,
          summary: progressSummary,
          cumulative_realized_profit_jpy: progressSummary.realized_profit_jpy,
          cumulative_unrealized_profit_jpy: progressSummary.unrealized_profit_jpy,
          cumulative_total_profit_jpy: progressSummary.total_profit_jpy,
          lane_summaries: laneTotals,
          completed_case_count: caseResults.filter(item => String(item.status || '').startsWith('completed')).length,
          skipped_case_count: skippedCaseCount
        });
      });
      caseResults.push(caseResult);
      executedCaseCount += 1;
      if (state?.batchSimulationStopRequested === true) break;
    }
    // Stop時にまだ到達していない既存Caseは、結果を失わないよう末尾へ保持する。
    if (existingBatchRun && state?.batchSimulationStopRequested === true) {
      datasetPaths.forEach(path => {
        if (batchSimulationExistingCaseByPath({ cases: caseResults }, path)) return;
        const previous = batchSimulationExistingCaseByPath(existingBatchRun, path);
        if (previous) caseResults.push(cloneJsonValue(previous));
      });
    }
    const orderedCases = datasetPaths
      .map(path => batchSimulationExistingCaseByPath({ cases: caseResults }, path))
      .filter(Boolean);
    const combined = combineBatchSimulationResults(orderedCases);
    const hasStepErrors = orderedCases.some(item => String(item.status || '') === 'completed_with_step_errors');
    const status = state?.batchSimulationStopRequested === true
      ? 'stopped'
      : combined.failed_case_count > 0 || hasStepErrors
        ? 'completed_with_errors'
        : 'completed';
    const completedAt = nowLocalIso();
    const attempts = [...(existingBatchRun?.attempts || []), {
      attempt_no: (existingBatchRun?.attempts?.length || 0) + 1,
      mode: executionMode,
      started_at: startedAt,
      completed_at: completedAt,
      executed_case_count: executedCaseCount,
      skipped_case_count: skippedCaseCount,
      stopped: state?.batchSimulationStopRequested === true
    }];
    const batchRun = {
      schema_version: BATCH_SIMULATION_SCHEMA_VERSION,
      kind: 'fx_batch_simulation_run',
      runner_id: BATCH_SIMULATION_RUNNER_ID,
      batch_run_id: batchId,
      status,
      started_at: existingBatchRun?.started_at || startedAt,
      completed_at: completedAt,
      last_execution_mode: executionMode,
      attempts,
      execution_mode: 'SEQUENTIAL_CASES',
      case_definition: 'PRIMARY_DATASET_X_PERIOD_X_PROFILE_SNAPSHOT_X_RULE_APP_VERSION',
      profile_snapshot: cloneJsonValue(state?.simulationRunDraft || state?.simulationRunProfile || {}),
      rule_version: String(state?.simulationRunDraft?.rule_version || state?.simulationRunProfile?.rule_version || ''),
      app_version: String(pluginManifest?.version || ''),
      timezone: String(state?.simulationRunDraft?.time_sync_policy?.dataset_timezone || 'UNSPECIFIED_LOCAL_WALL_CLOCK'),
      requested_dataset_paths: datasetPaths,
      period_request: { mode: draft.period_mode, from: draft.period_from, to: draft.period_to },
      cases: orderedCases,
      summary: combined,
      resume_policy: 'CASE_BOUNDARY_RESTART_REPLACE_RESULT',
      teacher_guard: 'Case内部のNORMAL / EXPANSION / EXPANSION_LITEは独立Portfolioとしてパラレル評価します。条件・起点・建玉・Closeは共有しません。COMBINEDは損益・件数の集計だけです。停止後の再開は完了Caseを保持し、未完了CaseをCase先頭から再評価して結果を置換します。'
    };
    const normalEntryGateFailureRows = orderedCases.flatMap(item => item?.normal_entry_gate_failures || [])
      .map((item, index) => ({ ...item, row_no: index + 1 }));
    batchRun.normal_entry_gate_failures = {
      schema_version: 'fx_batch_normal_entry_gate_failures_v0_1',
      kind: 'fx_batch_normal_entry_gate_failures',
      generated_at: completedAt,
      rows: normalEntryGateFailureRows,
      summary: batchSimulationNormalGateFailureSummary(normalEntryGateFailureRows)
    };
    batchRun.result_hash = stableTextHash(JSON.stringify({ status, summary: combined, case_hashes: orderedCases.map(item => item.result_hash), normal_entry_gate_failure_summary: batchRun.normal_entry_gate_failures.summary }));
    return { batchRun, validation };
  }


  function batchSimulationNormalGateFailureRowsFromSnapshot(snapshot, caseContext = {}) {
    const opportunities = snapshot?.position_lifecycle?.portfolio?.normal_entry_opportunities || [];
    return opportunities
      .filter(item => item?.gate_failure && String(item?.status || '').toUpperCase() === 'MISSED')
      .map((item, index) => {
        const diagnostic = item.gate_failure || {};
        const gateResults = diagnostic.gate_results || {};
        const facts = diagnostic.facts || {};
        return {
          row_no: index + 1,
          case_id: caseContext.case_id || '',
          dataset_path: caseContext.dataset_path || '',
          opportunity_id: item.opportunity_id || '',
          direction: item.direction || facts.direction || '',
          trigger_type: diagnostic.trigger_type || '',
          evaluated_at: diagnostic.evaluated_at || item.first_r2_touch_at || '',
          dow_confirmation_id: item.dow_confirmation_id || facts.dow_confirmation_id || '',
          dow_confirmation_time: item.confirmed_at || facts.dow_confirmation_time || '',
          anchor_id: item.anchor_id || facts.anchor_id || '',
          anchor_time: item.anchor_time || facts.anchor_time || '',
          anchor_price: numberOrNull(item.anchor_price ?? facts.anchor_price),
          r2_price: numberOrNull(item.r2_price ?? facts.r2_price),
          candidate_price: numberOrNull(facts.candidate_price),
          terminal_reason_code: item.terminal_reason_code || '',
          failure_category: diagnostic.failure_category || '',
          primary_failure_code: diagnostic.primary_failure_code || '',
          failed_gate_count: (diagnostic.failed_gates || []).length,
          failed_gates: uniqueStrings(diagnostic.failed_gates || []),
          gate_results: cloneJsonValue(gateResults),
          h4_t3_ready: gateResults.h4_t3_ready === true,
          h1_t3_ready: gateResults.h1_t3_ready === true,
          h4_h1_t3_aligned: gateResults.h4_h1_t3_aligned === true,
          m5_dow_aligned: gateResults.m5_dow_aligned === true,
          h1_cycle_not_late: gateResults.h1_cycle_not_late === true,
          entry_direction_ready: gateResults.entry_direction_ready === true,
          cycle_guard_passed: gateResults.cycle_guard_passed === true,
          anchor_resolved: gateResults.anchor_resolved === true,
          anchor_matches_confirmation: gateResults.anchor_matches_confirmation === true,
          confirmation_aligned: gateResults.confirmation_aligned === true,
          anchor_lifecycle_ready: gateResults.anchor_lifecycle_ready === true,
          h4_r4_guard_passed: gateResults.h4_r4_guard_passed !== false,
          day_up_h4_down_r5_short_guard_passed: gateResults.day_up_h4_down_r5_short_guard_passed !== false
        };
      });
  }

  function batchSimulationNormalGateFailureSummary(rows) {
    const gateCounts = {};
    const primaryCounts = {};
    (rows || []).forEach(row => {
      uniqueStrings(row?.failed_gates || []).forEach(code => { gateCounts[code] = (gateCounts[code] || 0) + 1; });
      const primary = String(row?.primary_failure_code || '');
      if (primary) primaryCounts[primary] = (primaryCounts[primary] || 0) + 1;
    });
    const sortCounts = source => Object.entries(source)
      .map(([code, count]) => ({ code, count }))
      .sort((a, b) => b.count - a.count || a.code.localeCompare(b.code));
    return {
      opportunity_count: (rows || []).length,
      gate_violation_count: Object.values(gateCounts).reduce((sum, value) => sum + Number(value || 0), 0),
      gate_counts: sortCounts(gateCounts),
      primary_failure_counts: sortCounts(primaryCounts)
    };
  }

  function batchSimulationNormalGateFailureCsv(batchRun) {
    const headers = [
      'row_no','case_id','dataset_path','evaluated_at','direction','trigger_type',
      'dow_confirmation_time','dow_confirmation_id','anchor_time','anchor_price',
      'r2_price','candidate_price','terminal_reason_code','failure_category',
      'primary_failure_code','failed_gate_count','failed_gates',
      'h4_t3_ready','h1_t3_ready','h4_h1_t3_aligned','m5_dow_aligned',
      'h1_cycle_not_late','entry_direction_ready','cycle_guard_passed',
      'anchor_resolved','anchor_matches_confirmation','confirmation_aligned',
      'anchor_lifecycle_ready','h4_r4_guard_passed','day_up_h4_down_r5_short_guard_passed'
    ];
    const csvEscape = value => `"${String(value ?? '').replace(/"/g, '""')}"`;
    const rows = (batchRun?.normal_entry_gate_failures?.rows || []).map(item => [
      item.row_no,item.case_id,item.dataset_path,item.evaluated_at,item.direction,item.trigger_type,
      item.dow_confirmation_time,item.dow_confirmation_id,item.anchor_time,item.anchor_price,
      item.r2_price,item.candidate_price,item.terminal_reason_code,item.failure_category,
      item.primary_failure_code,item.failed_gate_count,(item.failed_gates || []).join(' / '),
      item.h4_t3_ready,item.h1_t3_ready,item.h4_h1_t3_aligned,item.m5_dow_aligned,
      item.h1_cycle_not_late,item.entry_direction_ready,item.cycle_guard_passed,
      item.anchor_resolved,item.anchor_matches_confirmation,item.confirmation_aligned,
      item.anchor_lifecycle_ready,item.h4_r4_guard_passed,item.day_up_h4_down_r5_short_guard_passed
    ].map(csvEscape).join(','));
    return `\uFEFF${headers.map(csvEscape).join(',')}\r\n${rows.join('\r\n')}\r\n`;
  }

  function batchSimulationCsv(batchRun) {
    const headers = ['case_id','status','dataset','period_from','period_to','execution_event_count','entry_count','reentry_count','add_on_count','close_event_count','exit_count','profit_close_count','loss_close_count','break_even_close_count','win_rate_pct','target_exit_count','t3_exit_count','structural_exit_count','anchor_exit_count','stop_exit_count','realized_profit_jpy','unrealized_profit_jpy','total_profit_jpy','open_position_count','normal_total_profit_jpy','expansion_total_profit_jpy','expansion_lite_total_profit_jpy','result_hash'];
    const csvEscape = value => `"${String(value ?? '').replace(/"/g, '""')}"`;
    const rows = (batchRun?.cases || []).map(item => [
      item.case_id,
      item.status,
      item.dataset?.path || '',
      item.period?.from || '',
      item.period?.to || '',
      item.summary?.execution_event_count || 0,
      item.summary?.entry_count || 0,
      item.summary?.reentry_count || 0,
      item.summary?.add_on_count || 0,
      item.summary?.close_event_count || 0,
      item.summary?.exit_count || 0,
      item.summary?.profit_close_count || 0,
      item.summary?.loss_close_count || 0,
      item.summary?.break_even_close_count || 0,
      Number(item.summary?.win_rate_pct || 0).toFixed(3),
      item.summary?.target_exit_count || 0,
      item.summary?.t3_exit_count || 0,
      item.summary?.structural_exit_count || 0,
      item.summary?.anchor_exit_count || 0,
      item.summary?.stop_exit_count || 0,
      item.summary?.realized_profit_jpy || 0,
      item.summary?.unrealized_profit_jpy || 0,
      item.summary?.total_profit_jpy || 0,
      item.summary?.open_position_count || 0,
      item.lane_summaries?.NORMAL?.total_profit_jpy || 0,
      item.lane_summaries?.EXPANSION?.total_profit_jpy || 0,
      item.lane_summaries?.EXPANSION_LITE?.total_profit_jpy || 0,
      item.result_hash || ''
    ].map(csvEscape).join(','));
    return `\uFEFF${headers.map(csvEscape).join(',')}\r\n${rows.join('\r\n')}\r\n`;
  }

  function downloadBatchSimulationArtifact(fileName, content, mimeType) {
    const blob = new Blob([content], { type: mimeType || 'application/octet-stream' });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement('a');
    anchor.href = url;
    anchor.download = fileName;
    document.body.appendChild(anchor);
    anchor.click();
    anchor.remove();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  }

  async function postBatchSimulationJson(relativePath, payload, apiRoot = '') {
    const settings = batchSimulationSettings();
    const root = String(apiRoot || settings.result_api_root).replace(/^\/+|\/+$/g, '');
    const clean = `${root}/${String(relativePath || '').replace(/^\/+/, '')}`.replace(/\\/g, '/');
    const response = await fetch(`/api/overlays/${clean}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload, null, 2)
    });
    if (!response.ok) throw new Error(`${response.status} ${response.statusText}`);
    return clean;
  }

  async function persistBatchSimulationRun(batchRun) {
    if (!batchRun) return { saved: 0, failed: 0, errors: [], saved_paths: [] };
    const settings = batchSimulationSettings();
    const fileName = `${batchRun.batch_run_id}.json`;
    const attempts = [
      { root: settings.result_api_root, label: 'primary' },
      { root: settings.fallback_result_api_root, label: 'fallback' }
    ].filter((item, index, items) => item.root && items.findIndex(other => other.root === item.root) === index);
    const errors = [];
    for (const attempt of attempts) {
      try {
        const savedPath = await postBatchSimulationJson(fileName, batchRun, attempt.root);
        const savedPaths = [savedPath];
        const gatePayload = batchRun.normal_entry_gate_failures || null;
        if (gatePayload) {
          try {
            const gatePath = await postBatchSimulationJson(`${batchRun.batch_run_id}_normal_entry_gate_failures.json`, gatePayload, attempt.root);
            savedPaths.push(gatePath);
          } catch (gateError) {
            errors.push(`${attempt.label}:${attempt.root}/${batchRun.batch_run_id}_normal_entry_gate_failures.json: ${gateError?.message || gateError}`);
          }
        }
        return { saved: savedPaths.length, failed: errors.length, errors, saved_paths: savedPaths, mode: attempt.label };
      } catch (err) {
        errors.push(`${attempt.label}:${attempt.root}/${fileName}: ${err?.message || err}`);
      }
    }
    return { saved: 0, failed: errors.length, errors, saved_paths: [] };
  }

  function batchSimulationFormatPercent(value) {
    const number = Number(value || 0);
    return `${number.toFixed(1)}%`;
  }

  function batchSimulationMetricCard(label, value, extraClass = '') {
    return `<div class="gpt-fx-chart-batch-metric-card"><div class="gpt-fx-chart-batch-metric-label">${escapeHtml(label)}</div><div class="gpt-fx-chart-batch-metric-value ${extraClass}">${escapeHtml(String(value ?? 0))}</div></div>`;
  }

  function batchSimulationLaneLiveText(label, summary) {
    const item = summary || {};
    return `${label}: Entry ${Number(item.entry_count || 0)} / 決済 ${Number(item.close_event_count || 0)} / 利益 ${Number(item.profit_close_count || 0)} / 損失 ${Number(item.loss_close_count || 0)} / 勝率 ${batchSimulationFormatPercent(item.win_rate_pct)} / 未決済 ${Number(item.open_position_count || 0)} / 評価 ${batchSimulationFormatJpy(item.total_profit_jpy)}`;
  }

  function batchSimulationCaseRowsHtml(batchRun) {
    const cases = batchRun?.cases || [];
    if (!cases.length) return '<tr><td colspan="13">結果はまだありません。</td></tr>';
    return cases.map(item => `<tr><td>${escapeHtml(item.case_id)}</td><td>${escapeHtml(item.status)}</td><td>${escapeHtml(batchSimulationDatasetLabel(item.dataset?.path || ''))}</td><td>${escapeHtml(item.period?.from || '-')} → ${escapeHtml(item.period?.to || '-')}</td><td>${item.summary?.execution_event_count || 0}</td><td>${item.summary?.entry_count || 0}</td><td>${item.summary?.close_event_count || 0}</td><td>${item.summary?.profit_close_count || 0}</td><td>${item.summary?.loss_close_count || 0}</td><td>${escapeHtml(batchSimulationFormatPercent(item.summary?.win_rate_pct))}</td><td class="${batchSimulationProfitClass(item.summary?.total_profit_jpy)}">${escapeHtml(batchSimulationFormatJpy(item.summary?.total_profit_jpy))}</td><td>${item.summary?.open_position_count || 0}</td><td><button class="gpt-fx-chart-btn" type="button" data-batch-open-case="${escapeHtml(item.case_id)}">チャートで開く</button></td></tr>`).join('');
  }

  function renderBatchSimulationDialog(backdrop, state) {
    applyBatchSimulationVisualMode(backdrop, state);
    const overlay = backdrop?.querySelector?.('[data-role="batch-simulation-overlay"]');
    const dialog = backdrop?.querySelector?.('[data-role="batch-simulation-dialog"]');
    if (!overlay || !dialog) return;
    const open = state?.batchSimulationDialogOpen === true || state?.batchSimulationRunInProgress === true;
    overlay.classList.toggle('is-open', open);
    if (!open) { dialog.innerHTML = ''; return; }
    const draft = state.batchSimulationDraft || buildEmptyBatchSimulationDraft(state);
    const validation = state.batchSimulationValidation || validateBatchSimulationDraft(state, draft);
    const progress = state.batchSimulationProgress || {};
    const batchRun = state.batchSimulationRunSnapshot;
    const combined = batchRun?.summary || rangeExecutionSummary([]);
    const activeSummary = state.batchSimulationRunInProgress ? (progress.summary || rangeExecutionSummary([])) : combined;
    const laneSummaries = state.batchSimulationRunInProgress ? (progress.lane_summaries || {}) : (combined.lane_summaries || {});
    const current = Number(progress.case_progress?.current || 0);
    const total = Number(progress.case_progress?.total || 0);
    const percent = total > 0 ? Math.max(0, Math.min(100, current / total * 100)) : 0;
    const catalog = state.batchSimulationDatasetCatalog || [];
    const selected = new Set((draft.dataset_paths || []).map(batchSimulationNormalizeDataPath));
    const datasetHtml = catalog.length
      ? catalog.map(item => `<label class="gpt-fx-chart-batch-dataset"><input type="checkbox" data-batch-dataset-path="${escapeHtml(item.path)}" ${selected.has(item.path) ? 'checked' : ''} ${state.batchSimulationRunInProgress ? 'disabled' : ''}><span><strong>${escapeHtml(item.label)}</strong>${item.current ? '（現在表示中）' : ''}<br><span class="gpt-fx-chart-batch-note">${escapeHtml(item.path)}</span></span></label>`).join('')
      : '<div class="gpt-fx-chart-batch-note">Dataset一覧を読込中…</div>';
    const statusText = String(state.batchSimulationRunStatus || '未実行');
    const hasStoppedCase = (batchRun?.cases || []).some(item => String(item.status || '') === 'stopped') || String(batchRun?.status || '') === 'stopped';
    const hasFailedCase = (batchRun?.cases || []).some(item => ['failed', 'completed_with_step_errors'].includes(String(item.status || '')));
    const persistErrors = state.batchSimulationPersistErrors || [];
    const canRetryPersist = Boolean(batchRun) && !state.batchSimulationRunInProgress && persistErrors.length > 0;
    const persistErrorHtml = persistErrors.length
      ? `<details class="gpt-fx-chart-batch-persist-errors"><summary>保存エラー詳細 ${persistErrors.length}件</summary><ul>${persistErrors.slice(0, 10).map(item => `<li>${escapeHtml(item)}</li>`).join('')}</ul></details>`
      : '';
    dialog.innerHTML = `
      <div class="gpt-fx-chart-batch-header">
        <div><h3 class="gpt-fx-chart-batch-title">一括Simulation / Batch Runner</h3><div class="gpt-fx-chart-batch-subtitle">1 Dataset × 1期間 × 1 Profile Snapshot = 1 Case。Case内部はRule Lane独立・パラレル、Case間は逐次実行。</div></div>
        <div class="gpt-fx-chart-batch-actions">
          <button class="gpt-fx-chart-btn is-active" type="button" data-batch-action="start" ${state.batchSimulationRunInProgress || !validation.valid ? 'disabled' : ''}>${state.batchSimulationRunInProgress ? '実行中…' : '一括実行'}</button>
          <button class="gpt-fx-chart-btn" type="button" data-batch-action="resume" ${state.batchSimulationRunInProgress || !validation.valid || !hasStoppedCase ? 'disabled' : ''}>未完了から再開</button>
          <button class="gpt-fx-chart-btn" type="button" data-batch-action="retry-failed" ${state.batchSimulationRunInProgress || !validation.valid || !hasFailedCase ? 'disabled' : ''}>失敗Case再実行</button>
          <button class="gpt-fx-chart-btn" type="button" data-batch-action="stop" ${state.batchSimulationRunInProgress ? '' : 'disabled'}>停止</button>
          <button class="gpt-fx-chart-btn" type="button" data-batch-action="retry-save" ${canRetryPersist ? '' : 'disabled'}>保存再試行</button>
          <button class="gpt-fx-chart-btn" type="button" data-batch-action="download-json" ${batchRun ? '' : 'disabled'}>結果JSON</button>
          <button class="gpt-fx-chart-btn" type="button" data-batch-action="download-csv" ${batchRun ? '' : 'disabled'}>集計CSV</button>
          <button class="gpt-fx-chart-btn" type="button" data-batch-action="download-gate-json" ${batchRun ? '' : 'disabled'}>Gate失敗JSON</button>
          <button class="gpt-fx-chart-btn" type="button" data-batch-action="download-gate-csv" ${batchRun ? '' : 'disabled'}>Gate失敗CSV</button>
          <button class="gpt-fx-chart-btn" type="button" data-batch-action="close" ${state.batchSimulationRunInProgress ? 'disabled' : ''}>閉じる</button>
        </div>
      </div>
      <div class="gpt-fx-chart-batch-body">
        <div class="gpt-fx-chart-batch-live-stack">
          <div class="gpt-fx-chart-batch-pnl-board" aria-live="polite">
          <div class="gpt-fx-chart-batch-pnl-card"><div class="gpt-fx-chart-batch-pnl-label">評価損益合計</div><div class="gpt-fx-chart-batch-pnl-value ${batchSimulationProfitClass(activeSummary.total_profit_jpy)}">${escapeHtml(batchSimulationFormatJpy(activeSummary.total_profit_jpy))}</div></div>
          <div class="gpt-fx-chart-batch-pnl-card"><div class="gpt-fx-chart-batch-pnl-label">実現損益</div><div class="gpt-fx-chart-batch-pnl-value ${batchSimulationProfitClass(activeSummary.realized_profit_jpy)}">${escapeHtml(batchSimulationFormatJpy(activeSummary.realized_profit_jpy))}</div></div>
          <div class="gpt-fx-chart-batch-pnl-card"><div class="gpt-fx-chart-batch-pnl-label">含み損益</div><div class="gpt-fx-chart-batch-pnl-value ${batchSimulationProfitClass(activeSummary.unrealized_profit_jpy)}">${escapeHtml(batchSimulationFormatJpy(activeSummary.unrealized_profit_jpy))}</div></div>
          <div class="gpt-fx-chart-batch-pnl-card"><div class="gpt-fx-chart-batch-pnl-label">NORMAL評価</div><div class="gpt-fx-chart-batch-pnl-value ${batchSimulationProfitClass(laneSummaries?.NORMAL?.total_profit_jpy)}">${escapeHtml(batchSimulationFormatJpy(laneSummaries?.NORMAL?.total_profit_jpy))}</div></div>
          <div class="gpt-fx-chart-batch-pnl-card"><div class="gpt-fx-chart-batch-pnl-label">EXPANSION-LITE評価</div><div class="gpt-fx-chart-batch-pnl-value ${batchSimulationProfitClass(laneSummaries?.EXPANSION_LITE?.total_profit_jpy)}">${escapeHtml(batchSimulationFormatJpy(laneSummaries?.EXPANSION_LITE?.total_profit_jpy))}</div></div>
        </div>
        <div class="gpt-fx-chart-batch-metric-board" aria-live="polite">
          ${batchSimulationMetricCard('実行Event', activeSummary.execution_event_count)}
          ${batchSimulationMetricCard('Entry', activeSummary.entry_count)}
          ${batchSimulationMetricCard('Add-on', activeSummary.add_on_count)}
          ${batchSimulationMetricCard('決済', activeSummary.close_event_count)}
          ${batchSimulationMetricCard('非Target Exit', activeSummary.exit_count)}
          ${batchSimulationMetricCard('利益Close', activeSummary.profit_close_count, 'is-positive')}
          ${batchSimulationMetricCard('損失Close', activeSummary.loss_close_count, 'is-negative')}
          ${batchSimulationMetricCard('勝率', batchSimulationFormatPercent(activeSummary.win_rate_pct))}
          ${batchSimulationMetricCard('未決済', activeSummary.open_position_count)}
        </div>
        <div class="gpt-fx-chart-batch-lane-live">
          <div>${escapeHtml(batchSimulationLaneLiveText('NORMAL', laneSummaries?.NORMAL))}</div>
          <div>${escapeHtml(batchSimulationLaneLiveText('EXPANSION-LITE', laneSummaries?.EXPANSION_LITE))}</div>
          <div>決済理由: Target ${Number(activeSummary.target_exit_count || 0)} / T3 ${Number(activeSummary.t3_exit_count || 0)} / Structural ${Number(activeSummary.structural_exit_count || 0)} / Anchor ${Number(activeSummary.anchor_exit_count || 0)} / Stop ${Number(activeSummary.stop_exit_count || 0)}</div>
        </div>
        </div>
        <section class="gpt-fx-chart-batch-section"><h4 class="gpt-fx-chart-batch-section-title">対象Dataset</h4><div class="gpt-fx-chart-batch-datasets">${datasetHtml}</div></section>
        <section class="gpt-fx-chart-batch-section"><h4 class="gpt-fx-chart-batch-section-title">対象期間</h4><div class="gpt-fx-chart-batch-controls"><select class="gpt-fx-chart-batch-select" data-batch-period-mode ${state.batchSimulationRunInProgress ? 'disabled' : ''}><option value="FULL_DATASET" ${draft.period_mode === 'FULL_DATASET' ? 'selected' : ''}>全期間</option><option value="CUSTOM" ${draft.period_mode === 'CUSTOM' ? 'selected' : ''}>開始・終了指定</option></select><input class="gpt-fx-chart-batch-input" data-batch-period-from value="${escapeHtml(draft.period_from || '')}" placeholder="YYYY-MM-DD HH:mm" ${draft.period_mode === 'CUSTOM' && !state.batchSimulationRunInProgress ? '' : 'disabled'}><span>→</span><input class="gpt-fx-chart-batch-input" data-batch-period-to value="${escapeHtml(draft.period_to || '')}" placeholder="YYYY-MM-DD HH:mm" ${draft.period_mode === 'CUSTOM' && !state.batchSimulationRunInProgress ? '' : 'disabled'}></div><div class="gpt-fx-chart-batch-note" style="margin-top:7px">CUSTOM期間では、H4/H1の必要文脈分を過去側Warmupとして処理し、集計は指定期間内Eventだけを対象にします。</div></section>
        <section class="gpt-fx-chart-batch-section"><h4 class="gpt-fx-chart-batch-section-title">処理状況</h4><div class="gpt-fx-chart-batch-progress-track"><div class="gpt-fx-chart-batch-progress-bar" style="width:${percent.toFixed(2)}%"></div></div><div class="gpt-fx-chart-batch-status">${escapeHtml(statusText)}${state.batchSimulationRunInProgress ? `<br>Case ${progress.case_no || 0}/${progress.case_total || 0} / ${escapeHtml(batchSimulationDatasetLabel(progress.dataset_path || ''))} / ${escapeHtml(progress.case_progress?.phase || '')} / ${current.toLocaleString()}/${total.toLocaleString()}足 / ${escapeHtml(progress.case_progress?.reference_time || '-')} / 評価失敗 ${Number(progress.case_progress?.failed_step_count || 0).toLocaleString()}件` : ''}<br>${validation.valid ? '<span style="color:#86efac">設定OK</span>' : `<span style="color:#fca5a5">${escapeHtml((validation.errors || []).join(' / '))}</span>`}${state.batchSimulationPersistStatus ? `<br>${escapeHtml(state.batchSimulationPersistStatus)}` : ''}${persistErrorHtml}</div></section>
        <section class="gpt-fx-chart-batch-section"><h4 class="gpt-fx-chart-batch-section-title">Case結果</h4><div class="gpt-fx-chart-batch-table-wrap"><table class="gpt-fx-chart-batch-table"><thead><tr><th>Case</th><th>Status</th><th>Dataset</th><th>期間</th><th>Event</th><th>Entry</th><th>決済</th><th>利益</th><th>損失</th><th>勝率</th><th>評価損益</th><th>未決済</th><th>確認</th></tr></thead><tbody>${batchSimulationCaseRowsHtml(batchRun)}</tbody></table></div></section>
        <div class="gpt-fx-chart-batch-note">評価損益合計 = 実現損益 + 停止/表示時点の含み損益。1単位=1,000通貨の表示用試算で、手数料・スリッページ・税・資金管理は含みません。勝率は利益Close ÷（利益Close + 損失Close）です。</div>
      </div>`;
  }

  function openBatchSimulationCaseOnChart(caseResult) {
    if (!caseResult) return;
    const url = new URL(location.href);
    url.searchParams.set('action', 'fx_chart');
    url.searchParams.set('data', batchSimulationNormalizeDataPath(caseResult.dataset?.path || DEFAULT_URL_DATA));
    url.searchParams.set('view', DEFAULT_URL_VIEW);
    url.searchParams.set('windowSize', '1000');
    const focusMs = numberOrNull(caseResult.focus?.first_event_ms) ?? parseDateTimeMs(caseResult.period?.from);
    if (focusMs != null) url.searchParams.set('syncTime', String(focusMs));
    location.href = url.toString();
  }

  function readSimulationRunDraftFromDialog(dialog, state) {
    const draft = cloneJsonValue(state?.simulationRunDraft || state?.simulationRunProfile || buildEmptySimulationRunProfile());
    const profiles = Array.isArray(draft.timeframe_profiles) ? draft.timeframe_profiles : [];
    REQUIRED_SIMULATION_TIMEFRAMES.forEach(tf => {
      const input = dialog.querySelector(`[data-run-confirm-bars="${tf}"]`);
      let item = profiles.find(x => normalizePanelTimeframe(x?.timeframe, String(x?.timeframe || '').toUpperCase()) === tf);
      if (!item) {
        item = { timeframe: tf, confirm_bars: null, required: true, source_mapping: {}, warmup: {} };
        profiles.push(item);
      }
      const raw = String(input?.value ?? '').trim();
      item.confirm_bars = raw === '' ? null : Number(raw);
    });
    draft.timeframe_profiles = profiles;
    state.simulationRunDraft = draft;
    state.simulationRunValidation = validateSimulationRunDraft(draft);
    return draft;
  }

  function updateSimulationRunValidationUi(dialog, state) {
    if (!dialog) return;
    const validation = state?.simulationRunValidation || validateSimulationRunDraft(state?.simulationRunDraft);
    const candleSync = buildMultiTimeframeCandleSyncSnapshot(state, state?.simulationRunDraft);
    const swingPointDetection = candleSync?.validation?.valid === true
      ? buildSharedSwingPointSnapshot(state, state?.simulationRunDraft, candleSync)
      : null;
    const dowTrendEvaluation = swingPointDetection?.validation?.valid === true
      ? buildDowTrendEvaluationSnapshot(state, state?.simulationRunDraft, swingPointDetection, candleSync)
      : null;
    const cyclePositionEvaluation = swingPointDetection?.validation?.valid === true
      ? buildCyclePositionEvaluationSnapshot(state, state?.simulationRunDraft, swingPointDetection, candleSync)
      : null;
    const hsiAnchorRegistry = cyclePositionEvaluation?.validation?.valid === true && dowTrendEvaluation?.validation?.valid === true
      ? buildHsiAnchorRegistrySnapshot(state, state?.simulationRunDraft, swingPointDetection, dowTrendEvaluation, cyclePositionEvaluation, candleSync)
      : null;
    const timeframeStates = hsiAnchorRegistry?.validation?.valid === true
      ? buildTimeframeStateSnapshot(state, state?.simulationRunDraft, candleSync, swingPointDetection, dowTrendEvaluation, cyclePositionEvaluation, hsiAnchorRegistry)
      : null;
    const upperContextDecision = timeframeStates?.validation?.valid === true
      ? buildUpperContextDecisionSnapshot(state, state?.simulationRunDraft, timeframeStates)
      : null;
    const positionLifecycle = upperContextDecision?.validation?.valid === true
      ? buildM5ExecutionPositionLifecycleSnapshot(state, state?.simulationRunDraft, candleSync, timeframeStates, hsiAnchorRegistry, upperContextDecision)
      : null;
    const traceReplay = positionLifecycle?.validation?.valid === true
      ? buildTraceReplaySnapshot(state, state?.simulationRunDraft, candleSync?.reference, swingPointDetection, dowTrendEvaluation, cyclePositionEvaluation, hsiAnchorRegistry, timeframeStates, upperContextDecision, positionLifecycle)
      : null;
    state.simulationRunValidation = validation;
    state.simulationCandleSyncSnapshot = candleSync;
    state.simulationSwingPointSnapshot = swingPointDetection;
    state.simulationDowTrendSnapshot = dowTrendEvaluation;
    state.simulationCyclePositionSnapshot = cyclePositionEvaluation;
    state.simulationHsiAnchorRegistrySnapshot = hsiAnchorRegistry;
    state.simulationTimeframeStateSnapshot = timeframeStates;
    state.simulationUpperContextDecisionSnapshot = upperContextDecision;
    state.simulationPositionLifecycleSnapshot = positionLifecycle;
    state.simulationTraceReplaySnapshot = traceReplay;
    if (state.simulationTraceReplaySequence == null && traceReplay) state.simulationTraceReplaySequence = traceReplay.events?.length || 0;
    const ready = validation.valid && candleSync?.validation?.valid === true && swingPointDetection?.validation?.valid === true && dowTrendEvaluation?.validation?.valid === true && cyclePositionEvaluation?.validation?.valid === true && hsiAnchorRegistry?.validation?.valid === true && timeframeStates?.validation?.valid === true && upperContextDecision?.validation?.valid === true && positionLifecycle?.validation?.valid === true && traceReplay?.validation?.valid === true;
    const combinedErrors = [...(validation.errors || []), ...(candleSync?.validation?.errors || []), ...(swingPointDetection?.validation?.errors || []), ...(dowTrendEvaluation?.validation?.errors || []), ...(cyclePositionEvaluation?.validation?.errors || []), ...(hsiAnchorRegistry?.validation?.errors || []), ...(timeframeStates?.validation?.errors || []), ...(upperContextDecision?.validation?.errors || []), ...(positionLifecycle?.validation?.errors || []), ...(traceReplay?.validation?.errors || [])];
    const status = dialog.querySelector('[data-role="run-validation-status"]');
    if (status) {
      status.classList.toggle('is-error', !ready);
      status.innerHTML = ready
        ? `<strong>現在地点を保存可能</strong><br>Confirm bars独立設定 + 確定足同期 + Swing + Dow + Cycle + HSI + 時間足状態 + 上位判断 + M5実行判定 + 建玉Lifecycle + 判断履歴再生 + Lookahead検査が通過しています。`
        : `<strong>現在地点を保存不可</strong><ul class="gpt-fx-chart-run-errors">${combinedErrors.map(x => `<li>${escapeHtml(x)}</li>`).join('')}</ul>`;
    }
    const button = dialog.querySelector('[data-run-action="snapshot"]');
    if (button) {
      button.disabled = !ready;
      button.classList.toggle('is-muted', !ready);
      button.title = ready ? '現在の設定・上位判断・M5実行判定・建玉Lifecycle・判断履歴CheckpointをTrace Sidecarへ保存します' : '設定または確定足同期エラーを解消してください';
    }
  }

  function sourceMappingLabel(item) {
    const mapping = item?.source_mapping || {};
    const kind = String(mapping.kind || '-');
    const from = String(mapping.source_timeframe || mapping.source_dataset_role || '-');
    return `${kind} / ${from}`;
  }

  function warmupLabel(item) {
    const warmup = item?.warmup || {};
    const mode = String(warmup.mode || '-');
    const bars = numberOrNull(warmup.bars);
    return bars == null ? mode : `${mode} / ${Math.floor(bars)} bars`;
  }

  function syncStatusClass(sync) {
    return sync?.validation?.valid === true ? 'gpt-fx-chart-sync-ok' : 'gpt-fx-chart-sync-error';
  }

  function renderCandleSyncRows(sync) {
    const timeframes = sync?.timeframes || {};
    return REQUIRED_SIMULATION_TIMEFRAMES.map(tf => {
      const item = timeframes[tf] || {};
      const latest = item.latest_confirmed_bar;
      const pending = item.current_unconfirmed_bar;
      const status = item.lookahead_detected ? 'LOOKAHEAD' : (latest ? 'CONFIRMED' : 'MISSING');
      const cls = item.lookahead_detected || !latest ? 'gpt-fx-chart-sync-error' : (item.warmup?.satisfied === false ? 'gpt-fx-chart-sync-warn' : 'gpt-fx-chart-sync-ok');
      return `<tr><td>${tf}</td><td>${escapeHtml(latest?.start_time || '-')}</td><td>${escapeHtml(latest?.end_time || '-')}</td><td>${escapeHtml(pending?.start_time || '-')}</td><td>${item.future_rows_excluded ?? 0}</td><td class="${cls}">${escapeHtml(status)}</td></tr>`;
    }).join('');
  }

  function renderSwingPointRows(snapshot) {
    const timeframes = snapshot?.timeframes || {};
    return REQUIRED_SIMULATION_TIMEFRAMES.map(tf => {
      const item = timeframes[tf] || {};
      const counts = item.counts || {};
      const lastTimes = [item.latest_active?.high?.confirmed_time, item.latest_active?.low?.confirmed_time].filter(Boolean).sort();
      const cls = item.status === 'ready' ? 'gpt-fx-chart-sync-ok' : 'gpt-fx-chart-sync-error';
      return `<tr><td>${tf}</td><td>${item.confirm_bars ?? '-'}</td><td>${item.analysis_scope?.detector_input_bars ?? 0}</td><td>${counts.pending_candidates ?? 0}</td><td>${counts.confirmed_points ?? 0}</td><td>${counts.active_basis ?? 0}</td><td>${counts.retired_basis ?? 0}</td><td>${escapeHtml(lastTimes[lastTimes.length - 1] || '-')}</td><td class="${cls}">${escapeHtml(String(item.status || 'missing').toUpperCase())}</td></tr>`;
    }).join('');
  }


  function dowPairLabel(previousPoint, currentPoint, relation) {
    if (!previousPoint || !currentPoint) return '不足';
    return `${round3(previousPoint.pivot_price)} → ${round3(currentPoint.pivot_price)} / ${String(relation || '-').toUpperCase()}`;
  }

  function renderDowTrendRows(snapshot) {
    const timeframes = snapshot?.timeframes || {};
    return REQUIRED_SIMULATION_TIMEFRAMES.map(tf => {
      const item = timeframes[tf] || {};
      const comparison = item.comparison_points || {};
      const state = String(item.trend_state || 'UNDETERMINED').toUpperCase();
      const previous = String(item.previous_trend_state || '-').toUpperCase();
      const cls = dowStateClass(state);
      const statusCls = item.lookahead_detected ? 'gpt-fx-chart-sync-error' : 'gpt-fx-chart-sync-ok';
      return `<tr><td>${tf}</td><td class="${cls}">${escapeHtml(state)}</td><td>${escapeHtml(previous)}</td><td>${escapeHtml(dowPairLabel(comparison.previous_high, comparison.current_high, item.high_relation))}</td><td>${escapeHtml(dowPairLabel(comparison.previous_low, comparison.current_low, item.low_relation))}</td><td>${(item.used_swing_point_ids || []).length}</td><td>${item.state_change_count ?? 0}</td><td class="${statusCls}">${escapeHtml(String(item.status || 'missing').toUpperCase())}</td></tr>`;
    }).join('');
  }

  function clampSimulationDialogValue(value, min, max) {
    return Math.min(max, Math.max(min, value));
  }

  function simulationRunDialogDefaultGeometry(overlay) {
    const rect = overlay?.getBoundingClientRect?.();
    const availableWidth = Math.max(1, rect?.width || 900);
    const width = Math.min(760, Math.max(Math.min(440, availableWidth - 16), Math.floor(availableWidth * 0.58)));
    return {
      left: Math.max(8, availableWidth - width - 8),
      top: 8,
      width
    };
  }

  function normalizeSimulationRunDialogGeometry(overlay, state) {
    const rect = overlay?.getBoundingClientRect?.();
    const availableWidth = Math.max(1, rect?.width || 900);
    const availableHeight = Math.max(1, rect?.height || 600);
    const minimumWidth = Math.max(180, Math.min(440, availableWidth - 16));
    const defaultGeometry = simulationRunDialogDefaultGeometry(overlay);
    const raw = state?.simulationRunDialogGeometry || defaultGeometry;
    const width = clampSimulationDialogValue(Number(raw.width) || defaultGeometry.width, minimumWidth, Math.max(minimumWidth, availableWidth - 16));
    const left = clampSimulationDialogValue(Number(raw.left) || 0, 8, Math.max(8, availableWidth - width - 8));
    const top = clampSimulationDialogValue(Number(raw.top) || 0, 8, Math.max(8, availableHeight - 96));
    return { left, top, width };
  }

  function applySimulationRunDialogGeometry(overlay, dialog, state) {
    if (!overlay || !dialog) return;
    const geometry = normalizeSimulationRunDialogGeometry(overlay, state);
    state.simulationRunDialogGeometry = geometry;
    const overlayRect = overlay.getBoundingClientRect();
    dialog.style.left = `${geometry.left}px`;
    dialog.style.top = `${geometry.top}px`;
    dialog.style.width = `${geometry.width}px`;
    dialog.style.maxHeight = `${Math.max(120, overlayRect.height - geometry.top - 8)}px`;
  }

  function resetSimulationRunDialogGeometry(overlay, dialog, state) {
    state.simulationRunDialogGeometry = simulationRunDialogDefaultGeometry(overlay);
    applySimulationRunDialogGeometry(overlay, dialog, state);
  }

  function renderSimulationRunDialog(backdrop, state) {
    const overlay = backdrop?.querySelector('[data-role="simulation-run-overlay"]');
    const dialog = backdrop?.querySelector('[data-role="simulation-run-dialog"]');
    if (!overlay || !dialog) return;
    overlay.classList.toggle('is-open', state?.simulationRunDialogOpen === true);
    if (state?.simulationRunDialogOpen !== true) return;
    const profile = state.simulationRunProfile;
    if (!profile || state.simulationRunProfileLoadStatus === 'loading') {
      dialog.innerHTML = `<div class="gpt-fx-chart-run-header" data-run-drag-handle><div class="gpt-fx-chart-run-resize-handle" data-run-resize-handle title="左右にドラッグして横幅変更"></div><div><h3 class="gpt-fx-chart-run-title">シミュレーション設定・状態確認</h3><div class="gpt-fx-chart-run-subtitle">設定Profileを読み込んでいます...</div></div><div class="gpt-fx-chart-run-header-actions"><button class="gpt-fx-chart-btn" type="button" data-run-action="reset-window">位置戻す</button><button class="gpt-fx-chart-btn" type="button" data-run-action="close">閉じる</button></div></div>`;
      applySimulationRunDialogGeometry(overlay, dialog, state);
      return;
    }
    const draft = state.simulationRunDraft || simulationRunDraftFromProfile(profile);
    state.simulationRunDraft = draft;
    state.simulationRunValidation = validateSimulationRunDraft(draft);
    state.simulationCandleSyncSnapshot = buildMultiTimeframeCandleSyncSnapshot(state, draft);
    const candleSync = state.simulationCandleSyncSnapshot;
    state.simulationSwingPointSnapshot = candleSync?.validation?.valid === true ? buildSharedSwingPointSnapshot(state, draft, candleSync) : null;
    const swingPointDetection = state.simulationSwingPointSnapshot;
    state.simulationDowTrendSnapshot = swingPointDetection?.validation?.valid === true ? buildDowTrendEvaluationSnapshot(state, draft, swingPointDetection, candleSync) : null;
    const dowTrendEvaluation = state.simulationDowTrendSnapshot;
    state.simulationCyclePositionSnapshot = swingPointDetection?.validation?.valid === true ? buildCyclePositionEvaluationSnapshot(state, draft, swingPointDetection, candleSync) : null;
    const cyclePositionEvaluation = state.simulationCyclePositionSnapshot;
    state.simulationHsiAnchorRegistrySnapshot = cyclePositionEvaluation?.validation?.valid === true && dowTrendEvaluation?.validation?.valid === true ? buildHsiAnchorRegistrySnapshot(state, draft, swingPointDetection, dowTrendEvaluation, cyclePositionEvaluation, candleSync) : null;
    const hsiAnchorRegistry = state.simulationHsiAnchorRegistrySnapshot;
    state.simulationTimeframeStateSnapshot = hsiAnchorRegistry?.validation?.valid === true ? buildTimeframeStateSnapshot(state, draft, candleSync, swingPointDetection, dowTrendEvaluation, cyclePositionEvaluation, hsiAnchorRegistry) : null;
    const timeframeStates = state.simulationTimeframeStateSnapshot;
    state.simulationUpperContextDecisionSnapshot = timeframeStates?.validation?.valid === true ? buildUpperContextDecisionSnapshot(state, draft, timeframeStates) : null;
    const upperContextDecision = state.simulationUpperContextDecisionSnapshot;
    state.simulationPositionLifecycleSnapshot = upperContextDecision?.validation?.valid === true ? buildM5ExecutionPositionLifecycleSnapshot(state, draft, candleSync, timeframeStates, hsiAnchorRegistry, upperContextDecision) : null;
    const positionLifecycle = state.simulationPositionLifecycleSnapshot;
    state.simulationTraceReplaySnapshot = positionLifecycle?.validation?.valid === true ? buildTraceReplaySnapshot(state, draft, candleSync?.reference, swingPointDetection, dowTrendEvaluation, cyclePositionEvaluation, hsiAnchorRegistry, timeframeStates, upperContextDecision, positionLifecycle) : null;
    const traceReplay = state.simulationTraceReplaySnapshot;
    if (state.simulationTraceReplaySequence == null && traceReplay) state.simulationTraceReplaySequence = traceReplay.events?.length || 0;
    const byTf = new Map((draft.timeframe_profiles || []).map(item => [normalizePanelTimeframe(item?.timeframe, String(item?.timeframe || '').toUpperCase()), item]));
    const period = simulationRunVisiblePeriod(state);
    const snapshotText = state.simulationRunSnapshot
      ? JSON.stringify({ ...state.simulationRunSnapshot, swing_point_detection: swingSnapshotPreview(state.simulationRunSnapshot.swing_point_detection), dow_trend_evaluation: dowTrendSnapshotPreview(state.simulationRunSnapshot.dow_trend_evaluation), cycle_position_evaluation: cyclePositionSnapshotPreview(state.simulationRunSnapshot.cycle_position_evaluation), hsi_anchor_registry: hsiAnchorRegistrySnapshotPreview(state.simulationRunSnapshot.hsi_anchor_registry), timeframe_states: timeframeStateSnapshotPreview(state.simulationRunSnapshot.timeframe_states), upper_context_decision: upperContextDecisionSnapshotPreview(state.simulationRunSnapshot.upper_context_decision), position_lifecycle: { ...state.simulationRunSnapshot.position_lifecycle, decision_events: `[${state.simulationRunSnapshot.position_lifecycle?.decision_events?.length || 0} events]`, execution_events: `[${state.simulationRunSnapshot.position_lifecycle?.execution_events?.length || 0} events]` }, trace_replay: { ...state.simulationRunSnapshot.trace_replay, events: `[${state.simulationRunSnapshot.trace_replay?.events?.length || 0} events]`, checkpoints: `[${state.simulationRunSnapshot.trace_replay?.checkpoints?.length || 0} checkpoints]` } }, null, 2)
      : 'Snapshotはまだ作成されていません。\n上位足Decisionを入力に、M5確定足で仮想Entry・保有・決済を一地点ずつ評価します。Expansion確定条件とリアル注文は対象外です。';
    dialog.innerHTML = `
      <div class="gpt-fx-chart-run-header" data-run-drag-handle title="ドラッグして移動できます">
        <div class="gpt-fx-chart-run-resize-handle" data-run-resize-handle title="左右にドラッグして横幅変更"></div>
        <div>
          <h3 class="gpt-fx-chart-run-title">シミュレーション設定・状態確認</h3>
          <div class="gpt-fx-chart-run-subtitle">チャートを操作しながら確認できます。上部をドラッグで移動、左端を左右へドラッグすると横幅を変更できます。</div>
        </div>
        <div class="gpt-fx-chart-run-header-actions">
          <button class="gpt-fx-chart-btn" type="button" data-run-action="reset-window">位置戻す</button>
          <button class="gpt-fx-chart-btn" type="button" data-run-action="close">閉じる</button>
        </div>
      </div>
      <div class="gpt-fx-chart-run-body">
        <div class="gpt-fx-chart-run-summary-grid">
          <div class="gpt-fx-chart-run-summary-card"><div class="gpt-fx-chart-run-label">設定Profile</div><div class="gpt-fx-chart-run-value">${escapeHtml(draft.profile_id || '-')}<br>${escapeHtml(state.simulationRunProfileLoadStatus || '-')}</div></div>
          <div class="gpt-fx-chart-run-summary-card"><div class="gpt-fx-chart-run-label">ルール版</div><div class="gpt-fx-chart-run-value">${escapeHtml(draft.rule_version || '-')}</div></div>
          <div class="gpt-fx-chart-run-summary-card"><div class="gpt-fx-chart-run-label">M5データ</div><div class="gpt-fx-chart-run-value">${escapeHtml(draft.dataset?.primary?.path || '-')}<br>sha256: ${escapeHtml(shortText(draft.dataset?.primary?.sha256 || '-', 28))}</div></div>
          <div class="gpt-fx-chart-run-summary-card"><div class="gpt-fx-chart-run-label">上位足データ</div><div class="gpt-fx-chart-run-value">${escapeHtml(draft.dataset?.upper_map?.path || '-')}<br>sha256: ${escapeHtml(shortText(draft.dataset?.upper_map?.sha256 || '-', 28))}</div></div>
          <div class="gpt-fx-chart-run-summary-card"><div class="gpt-fx-chart-run-label">対象期間</div><div class="gpt-fx-chart-run-value">${escapeHtml(period.from || '-')} → ${escapeHtml(period.to || '-')}<br>${period.row_count.toLocaleString()} M5 rows / current chart window</div></div>
          <div class="gpt-fx-chart-run-summary-card"><div class="gpt-fx-chart-run-label">処理状態</div><div class="gpt-fx-chart-run-value">上位判断 ON / M5実行判定 ON / 仮想建玉Lifecycle ON</div></div>
        </div>
        <div class="gpt-fx-chart-run-summary-card">
          <div class="gpt-fx-chart-run-label">基準地点</div>
          <div class="gpt-fx-chart-run-value">${escapeHtml(candleSync?.reference?.reference_close_time || '-')} / ${escapeHtml(candleSync?.reference?.source || '-')}<br>${candleSync?.reference?.source === 'm5_context_menu_reference' ? 'M5右クリックで固定した一点を解析中' : 'トップRun設定は同期位置、未指定時は表示M5右端を参照'}</div>
        </div>
        <table class="gpt-fx-chart-run-table">
          <thead><tr><th>時間足</th><th>確定本数</th><th>データ元</th><th>事前履歴</th></tr></thead>
          <tbody>
            ${REQUIRED_SIMULATION_TIMEFRAMES.map(tf => {
              const item = byTf.get(tf) || { timeframe: tf, confirm_bars: null, source_mapping: {}, warmup: {} };
              const value = item.confirm_bars == null ? '' : String(item.confirm_bars);
              return `<tr><td>${tf}</td><td><input class="gpt-fx-chart-run-confirm-input" type="number" min="3" max="101" step="1" value="${escapeHtml(value)}" data-run-confirm-bars="${tf}" aria-label="${tf} Confirm bars"></td><td>${escapeHtml(sourceMappingLabel(item))}</td><td>${escapeHtml(warmupLabel(item))}</td></tr>`;
            }).join('')}
          </tbody>
        </table>
        <div class="gpt-fx-chart-run-summary-card">
          <div class="gpt-fx-chart-run-label">確定足同期</div>
          <div class="gpt-fx-chart-run-value">Reference: ${escapeHtml(candleSync?.reference?.reference_close_time || '-')} / ${escapeHtml(candleSync?.reference?.source || '-')}<br>Timezone: ${escapeHtml(candleSync?.timezone?.dataset_timezone || '-')} → runtime ${escapeHtml(candleSync?.timezone?.runtime_timezone || '-')} (${candleSync?.timezone?.runtime_utc_offset_minutes ?? '-'} min)</div>
        </div>
        <table class="gpt-fx-chart-run-table">
          <thead><tr><th>時間足</th><th>最新確定足</th><th>確定終了</th><th>現在未確定</th><th>除外数</th><th>状態</th></tr></thead>
          <tbody>${renderCandleSyncRows(candleSync)}</tbody>
        </table>
        <div class="gpt-fx-chart-sync-status ${candleSync?.validation?.valid === true ? '' : 'is-error'}" data-role="candle-sync-status">
          <strong class="${syncStatusClass(candleSync)}">${candleSync?.validation?.valid === true ? '確定足同期OK / Lookaheadなし' : '確定足同期エラー'}</strong><br>
          <span class="gpt-fx-chart-sync-note">${escapeHtml((candleSync?.validation?.warnings || []).join(' / ') || '上位足はM5 Close時点で確定した足だけを使用します。未確定足・未来足は状態判定へ渡しません。')}</span>
        </div>
        <div class="gpt-fx-chart-run-summary-card">
          <div class="gpt-fx-chart-run-label">共通の山谷判定</div>
          <div class="gpt-fx-chart-run-value">Detector: ${escapeHtml(swingPointDetection?.detector?.detector_id || '-')}<br>Candidate → Confirmed → Retired / Confirmed Activeだけが後続起点候補</div>
        </div>
        <table class="gpt-fx-chart-run-table">
          <thead><tr><th>時間足</th><th>確定本数</th><th>入力足</th><th>確認待ち</th><th>確定</th><th>有効</th><th>退役</th><th>最新確定</th><th>状態</th></tr></thead>
          <tbody>${renderSwingPointRows(swingPointDetection)}</tbody>
        </table>
        <div class="gpt-fx-chart-sync-status ${swingPointDetection?.validation?.valid === true ? '' : 'is-error'}">
          <strong class="${swingPointDetection?.validation?.valid === true ? 'gpt-fx-chart-sync-ok' : 'gpt-fx-chart-sync-error'}">${swingPointDetection?.validation?.valid === true ? 'Shared Detector OK / 全時間足共通ロジック' : 'Swing Point Detectorエラー'}</strong><br>
          <span class="gpt-fx-chart-sync-note">${escapeHtml((swingPointDetection?.validation?.warnings || []).join(' / ') || 'Chart UIとSimulation SnapshotはbuildCandidatePoints / buildPointLayersの共通Coreを利用します。')}</span>
        </div>
        <div class="gpt-fx-chart-run-summary-card">
          <div class="gpt-fx-chart-run-label">ダウ状態判定</div>
          <div class="gpt-fx-chart-run-value">Evaluator: ${escapeHtml(dowTrendEvaluation?.evaluator?.evaluator_id || '-')}<br>確定Swing構造だけを比較 / TrendState ≠ Entry Permission</div>
        </div>
        <table class="gpt-fx-chart-run-table">
          <thead><tr><th>時間足</th><th>現在</th><th>直前</th><th>高値比較</th><th>安値比較</th><th>使用点</th><th>変更回数</th><th>状態</th></tr></thead>
          <tbody>${renderDowTrendRows(dowTrendEvaluation)}</tbody>
        </table>
        <div class="gpt-fx-chart-sync-status ${dowTrendEvaluation?.validation?.valid === true ? '' : 'is-error'}">
          <strong class="${dowTrendEvaluation?.validation?.valid === true ? 'gpt-fx-chart-sync-ok' : 'gpt-fx-chart-sync-error'}">${dowTrendEvaluation?.validation?.valid === true ? 'Dow TrendState OK / 行動判断は未評価' : 'Dow Trend Evaluatorエラー'}</strong><br>
          <span class="gpt-fx-chart-sync-note">${escapeHtml((dowTrendEvaluation?.validation?.warnings || []).join(' / ') || 'UP/DOWNはHigher/Lower High + Higher/Lower Lowが揃った場合だけ確定し、曖昧状態を無理に方向へ丸めません。')}</span>
        </div>
        <div class="gpt-fx-chart-run-summary-card">
          <div class="gpt-fx-chart-run-label">サイクル位置判定</div>
          <div class="gpt-fx-chart-run-value">Evaluator: ${escapeHtml(cyclePositionEvaluation?.evaluator?.evaluator_id || '-')}<br>最新の確定・利用可能Swingを起点化 / EARLY・MIDDLE・LATE ≠ Action Permission</div>
        </div>
        <table class="gpt-fx-chart-run-table">
          <thead><tr><th>時間足</th><th>起点</th><th>方向</th><th>経過本数</th><th>段階</th><th>文脈状態</th><th>閾値</th><th>変更回数</th><th>状態</th></tr></thead>
          <tbody>${renderCyclePositionRows(cyclePositionEvaluation)}</tbody>
        </table>
        <div class="gpt-fx-chart-sync-status ${cyclePositionEvaluation?.validation?.valid === true ? '' : 'is-error'}">
          <strong class="${cyclePositionEvaluation?.validation?.valid === true ? 'gpt-fx-chart-sync-ok' : 'gpt-fx-chart-sync-error'}">${cyclePositionEvaluation?.validation?.valid === true ? 'Cycle Position OK / Action Permissionは未評価' : 'Cycle Position Evaluatorエラー'}</strong><br>
          <span class="gpt-fx-chart-sync-note">${escapeHtml((cyclePositionEvaluation?.validation?.warnings || []).join(' / ') || '起点Swing、経過本数、明示閾値、Phase変更時刻をTraceへ残します。WEEK/DAY/H4/H1/M5は同じEvaluatorへProfile設定を渡します。')}</span>
        </div>
        <div class="gpt-fx-chart-run-summary-card">
          <div class="gpt-fx-chart-run-label">HSI起点管理・選択</div>
          <div class="gpt-fx-chart-run-value">Registry: ${escapeHtml(hsiAnchorRegistry?.registry?.registry_id || '-')}<br>複数AnchorをLifecycle・Role・Purpose別に保持 / Human Saved HSIとは別source_type</div>
        </div>
        <table class="gpt-fx-chart-run-table">
          <thead><tr><th>時間足</th><th>方向文脈</th><th>候補/確定/退役</th><th>利用可</th><th>採用</th><th>Entry起点</th><th>Hold起点</th><th>Target起点</th><th>重なり</th><th>人間HSI</th><th>状態</th></tr></thead>
          <tbody>${renderHsiAnchorRows(hsiAnchorRegistry)}</tbody>
        </table>
        <div class="gpt-fx-chart-sync-status ${hsiAnchorRegistry?.validation?.valid === true ? '' : 'is-error'}">
          <strong class="${hsiAnchorRegistry?.validation?.valid === true ? 'gpt-fx-chart-sync-ok' : 'gpt-fx-chart-sync-error'}">${hsiAnchorRegistry?.validation?.valid === true ? 'HSI Anchor Registry OK / Purpose Reference ≠ 売買判断' : 'HSI Anchor Registry / Resolverエラー'}</strong><br>
          <span class="gpt-fx-chart-sync-note">${escapeHtml((hsiAnchorRegistry?.validation?.warnings || []).join(' / ') || 'Candidateは記録のみ、Confirmed ActiveだけをResolver候補にします。Entry/Hold/Target/Thesis/Confluenceは構造参照候補であり、Action Permissionではありません。')}</span>
        </div>
        <div class="gpt-fx-chart-run-summary-card">
          <div class="gpt-fx-chart-run-label">時間足状態の統合</div>
          <div class="gpt-fx-chart-run-value">Builder: ${escapeHtml(timeframeStates?.builder?.builder_id || '-')}<br>同一Reference Pointの確定情報を時間足別State JSONへ統合 / Data Sufficiencyと相場状態を分離</div>
        </div>
        <table class="gpt-fx-chart-run-table">
          <thead><tr><th>足</th><th>基準時刻</th><th>データ</th><th>ダウ</th><th>サイクル</th><th>文脈</th><th>BB</th><th>山/谷</th><th>HSI起点 E/H/T</th><th>根拠数</th><th>前回差分</th><th>状態ID</th></tr></thead>
          <tbody>${renderTimeframeStateRows(timeframeStates)}</tbody>
        </table>
        <div class="gpt-fx-chart-sync-status ${timeframeStates?.validation?.valid === true ? '' : 'is-error'}">
          <strong class="${timeframeStates?.validation?.valid === true ? 'gpt-fx-chart-sync-ok' : 'gpt-fx-chart-sync-error'}">${timeframeStates?.validation?.valid === true ? 'Timeframe State OK / Action Permissionは未評価' : 'Timeframe State Builderエラー'}</strong><br>
          <span class="gpt-fx-chart-sync-note">${escapeHtml((timeframeStates?.validation?.warnings || []).join(' / ') || 'Swing / Dow / Cycle / HSI / BBとsource_event_idsを一つの時間足Stateへ束ねます。UNKNOWN相場と履歴不足はdata_sufficiencyで区別します。')}</span>
        </div>
        <div class="gpt-fx-chart-run-summary-card">
          <div class="gpt-fx-chart-run-label">上位足の統合判断</div>
          <div class="gpt-fx-chart-run-value">判断器: ${escapeHtml(upperContextDecision?.engine?.engine_id || '-')}<br>売買対象外を最優先 / WEEKは季節 / H4で利確判断 / H1で離脱監視 / M5実行は未評価</div>
        </div>
        <table class="gpt-fx-chart-run-table">
          <thead><tr><th>方向</th><th>管理モード</th><th>通常Entry探索</th><th>Expansion探索</th><th>再Entry</th><th>買い増し</th><th>Core保有</th><th>利確準備</th><th>H1離脱監視</th><th>売買対象</th></tr></thead>
          <tbody>${renderUpperContextDecisionRows(upperContextDecision)}</tbody>
        </table>
        <table class="gpt-fx-chart-run-table">
          <thead><tr><th>優先度</th><th>ルールID</th><th>分類</th><th>該当したルール</th><th>適用結果</th></tr></thead>
          <tbody>${renderUpperContextRuleRows(upperContextDecision)}</tbody>
        </table>
        <div class="gpt-fx-chart-sync-status ${upperContextDecision?.validation?.valid === true ? '' : 'is-error'}">
          <strong class="${upperContextDecision?.validation?.valid === true ? 'gpt-fx-chart-sync-ok' : 'gpt-fx-chart-sync-error'}">${upperContextDecision?.validation?.valid === true ? '上位足の統合判断 OK / M5へ許可・禁止を受け渡し' : '上位足の統合判断エラー'}</strong><br>
          <span class="gpt-fx-chart-sync-note">${escapeHtml((upperContextDecision?.validation?.warnings || []).join(' / ') || 'M5はこの判断を再解釈せず、許可された探索と離脱監視だけを実行します。WEEKは直接Closeしません。')}</span>
        </div>
        <div class="gpt-fx-chart-run-summary-card">
          <div class="gpt-fx-chart-run-label">M5実行・建玉ライフサイクル</div>
          <div class="gpt-fx-chart-run-value">判断: ${escapeHtml(executionActionLabel(positionLifecycle?.trigger_evaluation?.action))} / ${escapeHtml(positionLifecycle?.trigger_evaluation?.status_label || '-')}<br>${escapeHtml(positionLifecycle?.trigger_evaluation?.summary || 'M5実行判定なし')}<br>建玉: ${positionLifecycle?.run_result?.open_position_ids?.length || 0}件 / 実行Event: ${positionLifecycle?.execution_events?.length || 0}件 / 累積Trade: ${positionLifecycle?.run_result?.trade_ids?.length || 0}件</div>
        </div>
        <table class="gpt-fx-chart-run-table">
          <thead><tr><th>役割</th><th>方向</th><th>残数/初期</th><th>Entry価格</th><th>Entry時刻</th><th>管理足</th><th>次目標</th><th>無効価格</th><th>状態</th><th>Position ID</th></tr></thead>
          <tbody>${renderM5ExecutionRows(positionLifecycle)}</tbody>
        </table>
        <table class="gpt-fx-chart-run-table">
          <thead><tr><th>時刻</th><th>実行</th><th>Trade</th><th>価格</th><th>要約</th><th>原因数</th></tr></thead>
          <tbody>${renderM5ExecutionEventRows(positionLifecycle)}</tbody>
        </table>
        <div class="gpt-fx-chart-sync-status ${positionLifecycle?.validation?.valid === true ? '' : 'is-error'}">
          <strong class="${positionLifecycle?.validation?.valid === true ? 'gpt-fx-chart-sync-ok' : 'gpt-fx-chart-sync-error'}">${positionLifecycle?.validation?.valid === true ? 'M5実行判定・建玉Lifecycle OK' : 'M5実行判定エラー'}</strong><br>
          <span class="gpt-fx-chart-sync-note">${escapeHtml((positionLifecycle?.validation?.warnings || []).join(' / ') || 'Core / Add-on / Runnerを別Positionとして保持し、Entry時間足・管理時間足・無効化ルール・原因Eventを保存します。Expansion確定条件は未実装のため通常Entryへ丸めません。')}</span>
        </div>
        ${renderTraceReplaySection(traceReplay, state.simulationTraceReplaySequence)}
        <div class="gpt-fx-chart-run-status" data-role="run-validation-status"></div>
        <div class="gpt-fx-chart-run-summary-card"><div class="gpt-fx-chart-run-label">表示範囲Simulation</div><div class="gpt-fx-chart-run-value" data-role="visible-range-run-status">${escapeHtml(state.simulationRangeRunStatus || '未実行')}<br>表示範囲の先頭は建玉なしで開始し、古いM5足から順番にEntry / CloseOK / CloseMissを評価します。</div></div>
        <div class="gpt-fx-chart-run-summary-card"><div class="gpt-fx-chart-run-label">保存状態 / Trace Sidecar</div><div class="gpt-fx-chart-run-value">${escapeHtml(state.simulationRunSnapshotStatus || '未作成')}</div></div>
        <pre class="gpt-fx-chart-run-preview">${escapeHtml(snapshotText)}</pre>
        <div class="gpt-fx-chart-run-actions">
          <button class="gpt-fx-chart-btn" type="button" data-run-action="close">閉じる</button>
          <button class="gpt-fx-chart-btn is-active" type="button" data-run-action="range" ${state.simulationRangeRunInProgress ? 'disabled' : ''}>${state.simulationRangeRunInProgress ? '表示範囲を実行中…' : '表示範囲を実行'}</button>
          <button class="gpt-fx-chart-btn" type="button" data-run-action="snapshot">現在地点を保存</button>
        </div>
      </div>`;
    applySimulationRunDialogGeometry(overlay, dialog, state);
    updateSimulationRunValidationUi(dialog, state);
  }

  function getCommentSidecarFileName(source) {
    const configured = source?.chart_comment_sidecar?.file
      || source?.comment_sidecar?.file
      || pluginManifest?.display_policy?.chart_comment_sidecar?.default_file
      || pluginManifest?.chart_viewer_policy?.chart_comment_sidecar?.default_file;
    const clean = String(configured || DEFAULT_COMMENT_SIDECAR_FILE).trim().replace(/\\/g, '/').split('/').pop();
    return clean && clean.toLowerCase().endsWith('.json') ? clean : DEFAULT_COMMENT_SIDECAR_FILE;
  }

  function getCommentSidecarPaths(source) {
    const file = getCommentSidecarFileName(source);
    return {
      file,
      relativePath: `studio_overlays/gpt_fx_lab/sidecars/${file}`,
      staticPath: `studio_overlays/gpt_fx_lab/sidecars/${file}`,
      apiPath: `/api/overlays/gpt_fx_lab/sidecars/${file}`
    };
  }

  function commentLocalStorageKey(source) {
    return COMMENT_LOCAL_STORAGE_PREFIX + getCommentSidecarFileName(source);
  }

  function buildEmptyCommentSidecar(source) {
    const paths = getCommentSidecarPaths(source);
    return {
      schema_version: '0.1',
      kind: 'fx_chart_comment_sidecar',
      target: {
        symbol: source?.symbol || 'USDJPY',
        timeframe: source?.timeframe || source?.timeframe_label || 'M5',
        data_path_hint: currentJsonParam('dataNameInput', DEFAULT_URL_DATA),
        sidecar_path_hint: paths.relativePath
      },
      display_policy: {
        default_visible: true,
        default_open: false,
        interaction: 'right-click chart point to add HSI anchor or comment; marker click opens tooltip/popover; edit is inline in popover',
        teacher_guard: 'observation memo only; no trend/entry/simulation logic',
        saved_hsi_interaction: 'right-click chart point to add HSI anchor; right-click current HSI anchor to save; right-click saved HSI anchor to delete',
        saved_vertical_interaction: 'right-click chart point/current sync line to save vertical marker; right-click saved vertical marker to delete',
        saved_cycle_vertical_interaction: 'right-click chart point to add cycle vertical marker; right-click cycle vertical label to delete',
        text_label_interaction: 'right-click chart point to add chart text label; click text label to edit/delete'
      },
      comments: [],
      hsi_annotations: [],
      vertical_annotations: [],
      cycle_vertical_annotations: [],
      text_annotations: []
    };
  }

  function normalizeCommentSidecar(raw, source) {
    const base = buildEmptyCommentSidecar(source);
    const data = raw && typeof raw === 'object' ? raw : {};
    const comments = Array.isArray(data.comments) ? data.comments : [];
    const hsiAnnotations = Array.isArray(data.hsi_annotations) ? data.hsi_annotations : [];
    const verticalAnnotations = Array.isArray(data.vertical_annotations) ? data.vertical_annotations : [];
    const cycleVerticalAnnotations = Array.isArray(data.cycle_vertical_annotations) ? data.cycle_vertical_annotations : [];
    const textAnnotations = Array.isArray(data.text_annotations) ? data.text_annotations : [];
    return {
      ...base,
      ...data,
      target: { ...base.target, ...(data.target || {}) },
      display_policy: { ...base.display_policy, ...(data.display_policy || {}) },
      comments: comments.map((comment, index) => ({
        id: comment.id || `comment_${compactTimestamp()}_${index + 1}`,
        created_at: comment.created_at || nowLocalIso(),
        updated_at: comment.updated_at || comment.created_at || nowLocalIso(),
        source_type: comment.source_type || 'human_comment',
        panel: comment.panel || 'M5',
        timeframe: comment.timeframe || comment.panel || 'M5',
        time: comment.time || comment.datetime || '',
        price: numberOrNull(comment.price),
        x_index_hint: numberOrNull(comment.x_index_hint ?? comment.x_index),
        comment_type: normalizeCommentType(comment.comment_type || comment.type || 'note'),
        title: comment.title || '',
        text: comment.text || comment.body || '',
        tags: Array.isArray(comment.tags) ? comment.tags : String(comment.tags || '').split(/[，,\s]+/).filter(Boolean),
        display: {
          pinned: Boolean(comment.display?.pinned),
          open: Boolean(comment.display?.open),
          editing: Boolean(comment.display?.editing)
        },
        chart_state: comment.chart_state || {},
        note: comment.note || ''
      })),
      hsi_annotations: hsiAnnotations.map((annotation, index) => {
        const hsi = annotation.hsi || {};
        const values = hsiValuesFromAnnotation(annotation);
        const scale = numberOrNull(hsi.scale ?? annotation.scale) ?? 1;
        const pointSize = numberOrNull(hsi.point_size ?? annotation.point_size) ?? hsiPointSize(source);
        const direction = normalizeHsiDirection(hsi.direction ?? annotation.direction);
        return {
          id: annotation.id || `hsi_${compactTimestamp()}_${index + 1}`,
          created_at: annotation.created_at || nowLocalIso(),
          updated_at: annotation.updated_at || annotation.created_at || nowLocalIso(),
          source_type: annotation.source_type || SAVED_HSI_SOURCE_TYPE,
          event_type: annotation.event_type || SAVED_HSI_EVENT_TYPE,
          panel: annotation.panel || 'M5',
          timeframe: annotation.timeframe || annotation.panel || 'M5',
          time: annotation.time || annotation.datetime || '',
          price: numberOrNull(annotation.price ?? annotation.anchor?.price),
          x_index_hint: numberOrNull(annotation.x_index_hint ?? annotation.x_index ?? annotation.anchor?.x_index_hint),
          title: annotation.title || '保存HSI',
          hsi: {
            values,
            values_text: normalizeHsiValuesText(hsi.values_text || values.join(',')),
            scale,
            direction,
            point_size: pointSize
          },
          display: {
            visible: annotation.display?.visible !== false,
            pinned: annotation.display?.pinned !== false,
            style: annotation.display?.style || 'saved_hsi'
          },
          chart_state: annotation.chart_state || {},
          note: annotation.note || ''
        };
      }),
      vertical_annotations: verticalAnnotations.map((annotation, index) => ({
        id: annotation.id || `vertical_${compactTimestamp()}_${index + 1}`,
        no: Math.max(1, Math.floor(numberOrNull(annotation.no ?? annotation.number ?? annotation.marker_no) ?? (index + 1))),
        created_at: annotation.created_at || nowLocalIso(),
        updated_at: annotation.updated_at || annotation.created_at || nowLocalIso(),
        source_type: annotation.source_type || SAVED_VERTICAL_SOURCE_TYPE,
        event_type: annotation.event_type || SAVED_VERTICAL_EVENT_TYPE,
        time: annotation.time || annotation.datetime || '',
        time_ms: numberOrNull(annotation.time_ms),
        label: annotation.label || '',
        display: {
          visible: annotation.display?.visible !== false,
          style: annotation.display?.style || 'saved_vertical_marker'
        },
        chart_state: annotation.chart_state || {},
        note: annotation.note || ''
      })),
      cycle_vertical_annotations: cycleVerticalAnnotations.map((annotation, index) => ({
        id: annotation.id || `cycle_vertical_${compactTimestamp()}_${index + 1}`,
        no: Math.max(1, Math.floor(numberOrNull(annotation.no ?? annotation.number ?? annotation.marker_no) ?? (index + 1))),
        created_at: annotation.created_at || nowLocalIso(),
        updated_at: annotation.updated_at || annotation.created_at || nowLocalIso(),
        source_type: annotation.source_type || SAVED_CYCLE_VERTICAL_SOURCE_TYPE,
        event_type: annotation.event_type || SAVED_CYCLE_VERTICAL_EVENT_TYPE,
        time: annotation.time || annotation.datetime || '',
        time_ms: numberOrNull(annotation.time_ms),
        label: annotation.label || '',
        display: {
          visible: annotation.display?.visible !== false,
          style: annotation.display?.style || 'saved_cycle_vertical_marker'
        },
        chart_state: annotation.chart_state || {},
        note: annotation.note || ''
      })),
      text_annotations: textAnnotations.map((annotation, index) => ({
        id: annotation.id || `text_label_${compactTimestamp()}_${index + 1}`,
        created_at: annotation.created_at || nowLocalIso(),
        updated_at: annotation.updated_at || annotation.created_at || nowLocalIso(),
        source_type: annotation.source_type || SAVED_TEXT_LABEL_SOURCE_TYPE,
        event_type: annotation.event_type || SAVED_TEXT_LABEL_EVENT_TYPE,
        panel: annotation.panel || 'M5',
        timeframe: annotation.timeframe || annotation.panel || 'M5',
        time: annotation.time || annotation.datetime || '',
        price: numberOrNull(annotation.price),
        x_index_hint: numberOrNull(annotation.x_index_hint ?? annotation.x_index),
        text: String(annotation.text || annotation.label || 'Expansion'),
        box: {
          width: Math.max(80, Math.floor(numberOrNull(annotation.box?.width ?? annotation.width) ?? 138)),
          height: Math.max(28, Math.floor(numberOrNull(annotation.box?.height ?? annotation.height) ?? 42))
        },
        display: {
          visible: annotation.display?.visible !== false,
          pinned: annotation.display?.pinned !== false,
          open: Boolean(annotation.display?.open),
          editing: Boolean(annotation.display?.editing),
          style: annotation.display?.style || 'expansion_label',
          offset_x: Math.floor(numberOrNull(annotation.display?.offset_x) ?? 12),
          offset_y: Math.floor(numberOrNull(annotation.display?.offset_y) ?? -48)
        },
        chart_state: annotation.chart_state || {},
        note: annotation.note || ''
      }))
    };
  }

  async function fetchJsonIfExists(url) {
    const response = await fetch(url, { cache: 'no-store' });
    if (!response.ok) throw new Error(`${response.status} ${response.statusText}`);
    return await response.json();
  }

  async function loadCommentSidecar(source) {
    const paths = getCommentSidecarPaths(source);
    let from = 'empty';
    let data = null;
    try {
      const rawLocal = localStorage.getItem(commentLocalStorageKey(source));
      if (rawLocal) {
        data = JSON.parse(rawLocal);
        from = 'localStorage';
      }
    } catch (err) {
      console.warn('[GPT FX Lab] comment sidecar localStorage load failed', err);
    }
    if (!data) {
      try {
        data = await fetchJsonIfExists(paths.apiPath);
        from = 'api';
      } catch {
        try {
          data = await fetchJsonIfExists(paths.staticPath);
          from = 'static';
        } catch {
          data = buildEmptyCommentSidecar(source);
        }
      }
    }
    const sidecar = normalizeCommentSidecar(data, source);
    sidecar._loaded_from = from;
    return sidecar;
  }

  function chartStateSnapshot(state) {
    const anchorPrice = numberOrNull(state?.hsiAnchor?.price);
    return {
      windowStart: Math.max(0, Math.floor(numberOrNull(state?.windowStart) ?? 0)),
      windowSize: Math.max(10, Math.floor(numberOrNull(state?.windowSize) ?? 1000)),
      chartLayout: normalizeChartLayout(state?.chartLayout),
      upperTf: normalizeUpperDisplayMode(state?.upperTimeframe),
      upperConfirmBars: Math.max(3, Math.floor(numberOrNull(state?.upperConfirmBars) ?? 7)),
      confirmBars: Math.max(3, Math.floor(numberOrNull(state?.confirmBars) ?? 20)),
      viewMode: String(state?.viewMode || 'all'),
      hlRange: state?.showHighLowRange === false ? 0 : 1,
      bb: state?.showBollinger === true ? 1 : 0,
      dayData: normalizeUpperMapDataPath(state?.upperMapDataPath || defaultUpperMapDataPath()),
      dayConfirmBars: Math.max(3, Math.floor(numberOrNull(state?.dayConfirmBars) ?? 7)),
      hsi: normalizeHsiValuesText(state?.hsiValuesText || '55,89,144,188,233,305,377,493,610,798,987'),
      hsiScale: numberOrNull(state?.hsiScale) ?? 1,
      hsiDir: normalizeHsiDirection(state?.hsiDirection),
      hsiAnchorPrice: anchorPrice,
      hsiAnchorIndex: anchorPrice == null ? null : Math.max(0, Math.floor(numberOrNull(state?.hsiAnchor?.index) ?? 0)),
      hsiAnchorPanel: anchorPrice == null ? null : hsiAnchorPanelLabel(state?.hsiAnchor, state)
    };
  }

  async function saveCommentSidecar(state, source, backdrop) {
    if (!state.commentSidecar) return false;
    const paths = getCommentSidecarPaths(source);
    state.commentSidecar.updated_at = nowLocalIso();
    state.commentSidecar.comments = state.comments || [];
    state.commentSidecar.hsi_annotations = state.hsiAnnotations || [];
    state.commentSidecar.vertical_annotations = state.verticalAnnotations || [];
    state.commentSidecar.cycle_vertical_annotations = state.cycleVerticalAnnotations || [];
    state.commentSidecar.text_annotations = state.textAnnotations || [];
    delete state.commentSidecar._loaded_from;
    state.commentSidecar.target = {
      ...(state.commentSidecar.target || {}),
      symbol: source?.symbol || state.commentSidecar.target?.symbol || 'USDJPY',
      timeframe: source?.timeframe || source?.timeframe_label || state.commentSidecar.target?.timeframe || 'M5',
      data_path_hint: currentJsonParam('dataNameInput', DEFAULT_URL_DATA),
      sidecar_path_hint: paths.relativePath
    };
    const jsonText = JSON.stringify(state.commentSidecar, null, 2);

    const attempts = [
      { url: paths.apiPath, options: { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: jsonText } }
    ];
    for (const attempt of attempts) {
      try {
        const response = await fetch(attempt.url, attempt.options);
        if (response.ok) {
          try { localStorage.removeItem(commentLocalStorageKey(source)); } catch { }
          state.commentSaveStatus = `保存済: ${paths.file}`;
          applyModeButtonState(backdrop, state);
          return true;
        }
      } catch {
        // continue fallback attempts
      }
    }

    try {
      localStorage.setItem(commentLocalStorageKey(source), jsonText);
    } catch (err) {
      console.warn('[GPT FX Lab] comment sidecar localStorage save failed', err);
    }
    state.commentSaveStatus = `一時保存(localStorage): ${paths.file}`;
    applyModeButtonState(backdrop, state);
    return false;
  }


  function commentPanelLabel(comment) {
    return String(comment?.panel || comment?.timeframe || 'M5').toUpperCase();
  }

  function commentMatchesPanel(comment, panelKind, state) {
    const panel = commentPanelLabel(comment);
    const targetPanel = panelKindToTimeframe(panelKind, state);
    if (targetPanel === 'M5') return ['M5', 'LOWER'].includes(panel);
    return panel === targetPanel || (panel === 'UPPER' && isUpperPanelKind(panelKind));
  }

  function commentIndexForRows(comment, rows) {
    const ms = parseDateTimeMs(comment?.time);
    if (ms != null) return findIndexForTime(rows, ms);
    const hint = numberOrNull(comment?.x_index_hint);
    if (hint != null) return Math.max(0, Math.min(rows.length - 1, Math.floor(hint)));
    return null;
  }

  function drawRoundedRect(ctx, x, y, w, h, r) {
    const radius = Math.min(r, w / 2, h / 2);
    ctx.beginPath();
    ctx.moveTo(x + radius, y);
    ctx.lineTo(x + w - radius, y);
    ctx.quadraticCurveTo(x + w, y, x + w, y + radius);
    ctx.lineTo(x + w, y + h - radius);
    ctx.quadraticCurveTo(x + w, y + h, x + w - radius, y + h);
    ctx.lineTo(x + radius, y + h);
    ctx.quadraticCurveTo(x, y + h, x, y + h - radius);
    ctx.lineTo(x, y + radius);
    ctx.quadraticCurveTo(x, y, x + radius, y);
    ctx.closePath();
  }

  function commentColor(comment) {
    const type = normalizeCommentType(comment?.comment_type || 'note');
    if (['miss', 'anchor_out', 'scale_out', 'context_out', 'dawDown', 'closeMiss', 'exit'].includes(type)) return { fill: 'rgba(248, 113, 113, 0.96)', stroke: 'rgba(254, 202, 202, 0.92)' };
    if (['hit', 'dawUp', 'entry', 'closeOk'].includes(type)) return { fill: 'rgba(34, 197, 94, 0.95)', stroke: 'rgba(187, 247, 208, 0.90)' };
    if (type === 'question') return { fill: 'rgba(96, 165, 250, 0.95)', stroke: 'rgba(191, 219, 254, 0.90)' };
    if (['maybe', 'dawNone'].includes(type)) return { fill: 'rgba(250, 204, 21, 0.96)', stroke: 'rgba(254, 249, 195, 0.92)' };
    return { fill: 'rgba(167, 139, 250, 0.96)', stroke: 'rgba(221, 214, 254, 0.94)' };
  }

  function commentDisplayTitle(comment) {
    const title = String(comment?.title || '').trim();
    if (!title) return '';
    const typeLabel = commentTypeLabel(comment?.comment_type);
    // 種類はアイコン色で表現する。自動補完された Maybe/Hit などをラベル文字として重ねない。
    if (title === typeLabel && String(comment?.comment_type || 'note') !== 'note') return '';
    return title;
  }

  function drawCommentLabel(ctx, xx, yy, comment, pad) {
    // コメント表示は「種類 + 本文」に統一する。タイトル欄はUIから廃止。
    const typeSource = commentTypeLabel(comment?.comment_type || 'note');
    const textSource = String(comment.text || '').trim();
    const primary = shortText(typeSource || 'note', 28);
    const secondary = textSource ? shortText(textSource, 42) : '';
    const lines = secondary && secondary !== primary ? [primary, secondary] : [primary];
    const w = Math.min(230, Math.max(92, ...lines.map(line => ctx.measureText(line).width + 18)));
    const h = 18 + lines.length * 14;
    let x = xx + 12;
    let y = yy - h - 8;
    if (x + w > pad.right) x = Math.max(pad.left + 4, xx - w - 12);
    if (y < pad.top) y = yy + 14;
    if (y + h > pad.bottom) y = Math.max(pad.top + 4, pad.bottom - h - 4);
    ctx.save();
    drawRoundedRect(ctx, x, y, w, h, 8);
    ctx.fillStyle = 'rgba(15, 23, 42, 0.88)';
    ctx.fill();
    ctx.strokeStyle = 'rgba(250, 204, 21, 0.42)';
    ctx.lineWidth = 1;
    ctx.stroke();
    ctx.font = '11px system-ui, sans-serif';
    ctx.textAlign = 'left';
    ctx.textBaseline = 'top';
    ctx.fillStyle = 'rgba(248, 250, 252, 0.98)';
    ctx.fillText(lines[0], x + 8, y + 7);
    if (lines[1]) {
      ctx.fillStyle = 'rgba(226, 232, 240, 0.92)';
      ctx.fillText(lines[1], x + 8, y + 21);
    }
    ctx.restore();
  }



  function isHsiMidpointObservationTarget(target) {
    return target?.observation === true
      || target?.style === 'r23_mid_observation'
      || target?.style === 'hsi_midpoint_observation'
      || !!findHsiMidpointObservation(target?.raw);
  }

  function hsiRenderItemIdentity(item) {
    const annotation = item?.annotation || {};
    return String(
      annotation.anchor_id
      || annotation.id
      || annotation.annotation_id
      || `${annotation.time || ''}:${annotation.price ?? item?.anchorPrice ?? ''}`
    );
  }

  function hsiPaletteForSlot(slot) {
    const size = Math.max(1, HSI_LINE_COLOR_PALETTE.length);
    const normalized = ((Math.floor(numberOrNull(slot) ?? 0) % size) + size) % size;
    return HSI_LINE_COLOR_PALETTE[normalized];
  }

  function assignHsiAnnotationColorSlots(annotations) {
    if (!Array.isArray(annotations) || !annotations.length) return annotations || [];
    const ordered = [...annotations].sort((a, b) => {
      const aMs = parseDateTimeMs(a?.recognized_time || a?.used_at_time || a?.time) ?? Number.MAX_SAFE_INTEGER;
      const bMs = parseDateTimeMs(b?.recognized_time || b?.used_at_time || b?.time) ?? Number.MAX_SAFE_INTEGER;
      if (aMs !== bMs) return aMs - bMs;
      const aKey = String(a?.anchor_id || a?.id || a?.annotation_id || '');
      const bKey = String(b?.anchor_id || b?.id || b?.annotation_id || '');
      return aKey.localeCompare(bKey);
    });
    const slotByIdentity = new Map();
    let nextSlot = 0;
    ordered.forEach(annotation => {
      const identity = String(annotation?.anchor_id || annotation?.id || annotation?.annotation_id || `${annotation?.time || ''}:${annotation?.price ?? ''}`);
      const explicitSlot = numberOrNull(annotation?.hsi_color_slot ?? annotation?.display?.hsi_color_slot);
      if (explicitSlot != null) {
        const slot = Math.max(0, Math.floor(explicitSlot));
        slotByIdentity.set(identity, slot);
        nextSlot = Math.max(nextSlot, slot + 1);
      }
    });
    ordered.forEach(annotation => {
      const identity = String(annotation?.anchor_id || annotation?.id || annotation?.annotation_id || `${annotation?.time || ''}:${annotation?.price ?? ''}`);
      let slot = slotByIdentity.get(identity);
      if (slot == null) {
        slot = nextSlot;
        nextSlot += 1;
        slotByIdentity.set(identity, slot);
      }
      annotation.hsi_color_slot = ((slot % HSI_LINE_COLOR_PALETTE.length) + HSI_LINE_COLOR_PALETTE.length) % HSI_LINE_COLOR_PALETTE.length;
      annotation.display = { ...(annotation.display || {}), hsi_color_slot: annotation.hsi_color_slot };
    });
    return annotations;
  }

  function assignHsiRenderPaletteSlots(items) {
    if (!Array.isArray(items) || !items.length) return items || [];
    const ordered = [...items].sort((a, b) => {
      const idxDiff = (numberOrNull(a?.idx) ?? Number.MAX_SAFE_INTEGER) - (numberOrNull(b?.idx) ?? Number.MAX_SAFE_INTEGER);
      if (idxDiff !== 0) return idxDiff;
      const aMs = parseDateTimeMs(a?.annotation?.recognized_time || a?.annotation?.used_at_time || a?.annotation?.time) ?? Number.MAX_SAFE_INTEGER;
      const bMs = parseDateTimeMs(b?.annotation?.recognized_time || b?.annotation?.used_at_time || b?.annotation?.time) ?? Number.MAX_SAFE_INTEGER;
      if (aMs !== bMs) return aMs - bMs;
      return hsiRenderItemIdentity(a).localeCompare(hsiRenderItemIdentity(b));
    });
    const slotByIdentity = new Map();
    let nextSlot = 0;
    ordered.forEach(item => {
      const identity = hsiRenderItemIdentity(item);
      const explicitSlot = numberOrNull(item?.annotation?.hsi_color_slot ?? item?.annotation?.display?.hsi_color_slot);
      let slot = explicitSlot == null ? slotByIdentity.get(identity) : Math.floor(explicitSlot);
      if (slot == null) {
        slot = nextSlot;
        nextSlot += 1;
      } else {
        nextSlot = Math.max(nextSlot, slot + 1);
      }
      slotByIdentity.set(identity, slot);
      item.hsiPaletteSlot = ((slot % HSI_LINE_COLOR_PALETTE.length) + HSI_LINE_COLOR_PALETTE.length) % HSI_LINE_COLOR_PALETTE.length;
      item.hsiPalette = hsiPaletteForSlot(item.hsiPaletteSlot);
    });
    return items;
  }

  function drawHsiTargetLine(ctx, args) {
    const { anchorX, x2, yy, target, pad, saved, palette } = args;
    const observation = isHsiMidpointObservationTarget(target);
    const color = palette || null;
    ctx.setLineDash(observation ? [2, 4] : (saved ? [6, 5] : []));
    ctx.lineCap = 'round';
    ctx.strokeStyle = color
      ? (observation ? color.observationLine : (saved ? color.savedLine : color.line))
      : (observation
        ? 'rgba(248, 250, 252, 0.82)'
        : (saved ? 'rgba(250, 204, 21, 0.54)' : 'rgba(248, 113, 113, 0.94)'));
    ctx.lineWidth = observation
      ? (saved ? 0.9 : 1.0)
      : (saved ? 1.7 : 2.2);
    ctx.beginPath();
    ctx.moveTo(anchorX, yy);
    ctx.lineTo(x2, yy);
    ctx.stroke();

    ctx.fillStyle = color
      ? (observation ? color.observationLabel : color.label)
      : (observation
        ? 'rgba(248, 250, 252, 0.88)'
        : (saved ? 'rgba(254, 249, 195, 0.72)' : 'rgba(248, 113, 113, 0.96)'));
    ctx.font = observation ? '10px system-ui, sans-serif' : (saved ? '10px system-ui, sans-serif' : '11px system-ui, sans-serif');
    ctx.textAlign = 'left';
    ctx.textBaseline = 'middle';
    const label = target.label || hsiRangeLabel(target.raw);
    ctx.fillText(label, Math.min(pad.right - 34, x2 + 5), yy);
  }

  function drawSavedHsiAnnotationsForPanel(ctx, args) {
    const { source, items, x, y, pad, plotW, state, panelKind } = args;
    if (!items?.length) return;
    items.forEach(item => {
      const { annotation, idx, anchorPrice, targets } = item;
      const palette = item.hsiPalette || hsiPaletteForSlot(item.hsiPaletteSlot || 0);
      const anchorX = x(idx);
      const anchorY = y(anchorPrice);
      if (anchorX < pad.left - 18 || anchorX > pad.right + 18 || anchorY < pad.top - 18 || anchorY > pad.bottom + 18) return;
      const x2 = Math.min(pad.right, anchorX + Math.max(96, plotW * 0.12));
      ctx.save();
      targets.forEach(target => {
        const yy = y(target.price);
        if (yy < pad.top - 12 || yy > pad.bottom + 12) return;
        drawHsiTargetLine(ctx, { anchorX, x2, yy, target, pad, saved: true, palette });
      });
      ctx.setLineDash([]);
      ctx.shadowColor = 'rgba(0,0,0,.36)';
      ctx.shadowBlur = 8;
      ctx.shadowColor = palette.glow;
      ctx.shadowBlur = 12;
      ctx.fillStyle = palette.anchorFill;
      // 起点リングは白固定にせず、同一起点の横バー色へ合わせる。
      ctx.strokeStyle = palette.savedLine;
      ctx.lineWidth = 2.6;
      ctx.beginPath();
      ctx.arc(anchorX, anchorY, 8.6, 0, Math.PI * 2);
      ctx.fill();
      ctx.stroke();
      ctx.shadowBlur = 0;
      ctx.fillStyle = 'rgba(15, 23, 42, 0.92)';
      ctx.beginPath();
      ctx.arc(anchorX, anchorY, 3.6, 0, Math.PI * 2);
      ctx.fill();
      ctx.restore();
      state.savedHsiHitBoxes = state.savedHsiHitBoxes || [];
      state.savedHsiHitBoxes.push({ id: annotation.id, x: anchorX, y: anchorY, radius: 18, annotation, panelKind });
    });
  }

  function drawSimulationHsiAnnotationsForPanel(ctx, args) {
    const { items, x, y, pad, plotW, state, panelKind } = args;
    if (!items?.length) return;
    items.forEach(item => {
      const { annotation, idx, anchorPrice, targets } = item;
      const palette = item.hsiPalette || hsiPaletteForSlot(item.hsiPaletteSlot || 0);
      const anchorX = x(idx);
      const anchorY = y(anchorPrice);
      if (anchorX < pad.left - 18 || anchorX > pad.right + 18 || anchorY < pad.top - 18 || anchorY > pad.bottom + 18) return;
      const defaultX2 = Math.min(pad.right, anchorX + Math.max(120, plotW * 0.16));
      const retiredX = item.endIdx == null ? null : x(item.endIdx);
      const x2 = retiredX == null ? defaultX2 : Math.min(pad.right, Math.max(anchorX + 8, retiredX));
      const liveFlash = annotation?.display?.live_flash === true;
      ctx.save();
      if (liveFlash) {
        ctx.shadowColor = 'rgba(217, 70, 239, 0.96)';
        ctx.shadowBlur = 20;
      }
      targets.forEach(target => {
        const yy = y(target.price);
        if (yy < pad.top - 12 || yy > pad.bottom + 12) return;
        const observation = isHsiMidpointObservationTarget(target);
        ctx.setLineDash(observation ? [2, 4] : [7, 4]);
        ctx.strokeStyle = observation ? palette.observationLine : palette.line;
        ctx.lineWidth = observation ? 0.9 : 1.8;
        ctx.beginPath();
        ctx.moveTo(anchorX, yy);
        ctx.lineTo(x2, yy);
        ctx.stroke();
        ctx.setLineDash([]);
        ctx.fillStyle = observation ? palette.observationLabel : palette.label;
        ctx.font = observation ? '9px system-ui, sans-serif' : '800 10px system-ui, sans-serif';
        ctx.textAlign = 'left';
        ctx.textBaseline = 'middle';
        ctx.fillText(target.label || hsiRangeLabel(target.raw), Math.min(pad.right - 34, x2 + 5), yy);
      });
      ctx.setLineDash([]);
      ctx.shadowColor = liveFlash ? 'rgba(217, 70, 239, 0.98)' : palette.glow;
      ctx.shadowBlur = liveFlash ? 22 : 12;
      ctx.fillStyle = palette.anchorFill;
      // Simulation HSIも横バーと同じ色で起点を囲み、Dow丸との重なりを識別しやすくする。
      ctx.strokeStyle = palette.line;
      ctx.lineWidth = 2.5;
      ctx.beginPath();
      ctx.arc(anchorX, anchorY, liveFlash ? 10.5 : 8.8, 0, Math.PI * 2);
      ctx.fill();
      ctx.stroke();
      ctx.shadowBlur = 0;
      ctx.fillStyle = '#081423';
      ctx.beginPath();
      ctx.arc(anchorX, anchorY, 3.5, 0, Math.PI * 2);
      ctx.fill();
      const label = liveFlash ? 'SIM HSI NEW' : 'SIM HSI';
      ctx.font = '900 10px system-ui, sans-serif';
      ctx.textAlign = 'left';
      ctx.textBaseline = 'bottom';
      ctx.fillStyle = liveFlash ? 'rgba(253, 244, 255, 0.99)' : palette.label;
      ctx.fillText(label, Math.min(pad.right - 72, anchorX + 9), Math.max(pad.top + 12, anchorY - 7));
      ctx.restore();
      state.simulationHsiHitBoxes = state.simulationHsiHitBoxes || [];
      state.simulationHsiHitBoxes.push({ id: annotation.id, x: anchorX, y: anchorY, radius: 18, annotation, panelKind });
    });
  }

  function drawCommentBubbleIcon(ctx, xx, yy, comment) {
    const color = commentColor(comment);
    const w = 20;
    const h = 15;
    const r = 7;
    const x0 = xx - w / 2;
    const y0 = yy - h / 2 - 1;
    ctx.save();
    ctx.shadowColor = 'rgba(0,0,0,.40)';
    ctx.shadowBlur = 8;
    ctx.fillStyle = color.fill;
    ctx.strokeStyle = color.stroke || 'rgba(221, 214, 254, 0.94)';
    ctx.lineWidth = 1.35;
    drawRoundedRect(ctx, x0, y0, w, h, r);
    ctx.fill();
    ctx.stroke();
    ctx.beginPath();
    ctx.moveTo(xx - 4, y0 + h - 1);
    ctx.lineTo(xx - 8, y0 + h + 5);
    ctx.lineTo(xx + 1, y0 + h - 1);
    ctx.closePath();
    ctx.fill();
    ctx.stroke();
    ctx.shadowBlur = 0;
    ctx.fillStyle = 'rgba(255, 255, 255, 0.92)';
    [-5, 0, 5].forEach(dx => {
      ctx.beginPath();
      ctx.arc(xx + dx, yy - 1.5, 1.55, 0, Math.PI * 2);
      ctx.fill();
    });
    ctx.restore();
  }

  function drawCommentsForPanel(ctx, args) {
    const { rows, state, panelKind, x, y, min, max, pad } = args;
    if (state.showUserComments === false || !state.comments?.length) return;
    state.commentHitBoxes = state.commentHitBoxes || [];
    state.comments.forEach(comment => {
      if (comment.source_type && comment.source_type !== 'human_comment') return;
      if (!commentMatchesPanel(comment, panelKind, state)) return;
      const idx = commentIndexForRows(comment, rows);
      if (idx == null || !rows[idx]) return;
      const price = numberOrNull(comment.price) ?? numberOrNull(rows[idx].close);
      if (price == null || price < min || price > max) return;
      const xx = x(idx);
      const yy = y(price);
      if (xx < pad.left - 16 || xx > pad.right + 16 || yy < pad.top - 16 || yy > pad.bottom + 16) return;
      drawCommentBubbleIcon(ctx, xx, yy, comment);
      state.commentHitBoxes.push({ id: comment.id, x: xx, y: yy, radius: 14, comment, panelKind });
      if (state.showAllComments || comment.display?.open || state.openCommentId === comment.id) {
        drawCommentLabel(ctx, xx, yy, comment, pad);
      }
    });
  }



  function simulationTracePanelLabel(event) {
    return String(event?.panel || event?.timeframe || 'M5').toUpperCase();
  }

  function simulationTraceMatchesPanel(event, panelKind, state) {
    const panel = simulationTracePanelLabel(event);
    const targetPanel = panelKindToTimeframe(panelKind, state);
    if (targetPanel === 'M5') return ['M5', 'LOWER'].includes(panel);
    return panel === targetPanel || (panel === 'UPPER' && isUpperPanelKind(panelKind));
  }

  function simulationTraceIndexForRows(event, rows) {
    const ms = parseDateTimeMs(event?.simulation_time || event?.time);
    if (ms != null) return findIndexForTime(rows, ms);
    const hint = numberOrNull(event?.x_index_hint);
    if (hint != null) return Math.max(0, Math.min(rows.length - 1, Math.floor(hint)));
    return null;
  }

  function simulationTraceColor(event) {
    const type = simulationRuleAwareEventType(event);
    if (['close', 'partial_close', 'stop_close'].includes(type)) return { fill: 'rgba(248, 113, 113, 0.96)', stroke: 'rgba(207, 250, 254, 0.98)' };
    if (type === 'swing_confirmed' && String(event?.display?.style || '').includes('low')) return { fill: 'rgba(239, 68, 68, 0.96)', stroke: 'rgba(254, 226, 226, 0.98)' };
    if (['entry', 'anchor_adopted', 'hsi_anchor_adopted', 'swing_confirmed'].includes(type)) return { fill: 'rgba(34, 197, 94, 0.95)', stroke: 'rgba(207, 250, 254, 0.98)' };
    if (type === 'swing_candidate') return { fill: 'rgba(250, 204, 21, 0.96)', stroke: 'rgba(254, 249, 195, 0.98)' };
    if (type === 'swing_retired') return { fill: 'rgba(148, 163, 184, 0.92)', stroke: 'rgba(226, 232, 240, 0.98)' };
    if (['entry', 'reentry', 'add_on'].includes(type)) return { fill: 'rgba(34, 197, 94, 0.96)', stroke: 'rgba(220, 252, 231, 0.98)' };
    if (['partial_close', 'close'].includes(type)) return { fill: 'rgba(59, 130, 246, 0.96)', stroke: 'rgba(219, 234, 254, 0.98)' };
    if (type === 'stop_close') return { fill: 'rgba(239, 68, 68, 0.96)', stroke: 'rgba(254, 226, 226, 0.98)' };
    if (['entry_blocked', 'exit_armed', 'cycle_phase_changed', 'cycle_origin_changed'].includes(type)) return { fill: 'rgba(250, 204, 21, 0.96)', stroke: 'rgba(207, 250, 254, 0.98)' };
    return { fill: 'rgba(34, 211, 238, 0.95)', stroke: 'rgba(236, 254, 255, 0.98)' };
  }

  function drawSimulationTraceIcon(ctx, xx, yy, event) {
    const color = simulationTraceColor(event);
    const size = 9;
    ctx.save();
    ctx.translate(xx, yy);
    ctx.rotate(Math.PI / 4);
    ctx.shadowColor = 'rgba(34, 211, 238, 0.54)';
    ctx.shadowBlur = 10;
    ctx.fillStyle = color.fill;
    ctx.strokeStyle = color.stroke;
    ctx.lineWidth = 1.4;
    ctx.fillRect(-size, -size, size * 2, size * 2);
    ctx.strokeRect(-size, -size, size * 2, size * 2);
    ctx.restore();
    ctx.save();
    ctx.fillStyle = 'rgba(2, 6, 23, 0.94)';
    ctx.font = '900 10px system-ui, sans-serif';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(traceReplayEventClass(event) === 'EXECUTION' ? '実' : 'S', xx, yy + 0.5);
    ctx.restore();
  }

  function drawSimulationTraceLabel(ctx, xx, yy, event, pad) {
    const primary = `${String(event.timeframe || event.panel || 'M5').toUpperCase()} ${String(event.event_type || 'state')}`;
    const secondary = shortText(event.summary || '', 62);
    const lines = secondary ? [primary, secondary] : [primary];
    ctx.save();
    ctx.font = '11px system-ui, sans-serif';
    const w = Math.min(300, Math.max(126, ...lines.map(line => ctx.measureText(line).width + 20)));
    const h = 18 + lines.length * 14;
    let x = xx + 14;
    let y = yy - h - 10;
    if (x + w > pad.right) x = Math.max(pad.left + 4, xx - w - 14);
    if (y < pad.top) y = yy + 16;
    if (y + h > pad.bottom) y = Math.max(pad.top + 4, pad.bottom - h - 4);
    drawRoundedRect(ctx, x, y, w, h, 8);
    ctx.fillStyle = 'rgba(8, 20, 35, 0.92)';
    ctx.fill();
    ctx.strokeStyle = 'rgba(34, 211, 238, 0.62)';
    ctx.lineWidth = 1;
    ctx.stroke();
    ctx.textAlign = 'left';
    ctx.textBaseline = 'top';
    ctx.fillStyle = 'rgba(165, 243, 252, 0.98)';
    ctx.font = '800 11px system-ui, sans-serif';
    ctx.fillText(lines[0], x + 9, y + 7);
    if (lines[1]) {
      ctx.fillStyle = 'rgba(226, 232, 240, 0.94)';
      ctx.font = '11px system-ui, sans-serif';
      ctx.fillText(lines[1], x + 9, y + 21);
    }
    ctx.restore();
  }

  function simulationExecutionMarkerPlacementSide(event) {
    const type = simulationRuleAwareEventType(event);
    if (['entry', 'reentry', 'add_on', 'stop_close'].includes(type)) return 'bottom';
    return 'top';
  }

  function simulationExecutionMarkerLayoutBucket(state, panelKind, side) {
    state.simulationExecutionMarkerLayout = state.simulationExecutionMarkerLayout || {};
    const key = `${panelKind}:${side}`;
    if (!state.simulationExecutionMarkerLayout[key]) state.simulationExecutionMarkerLayout[key] = { boxes: [] };
    return state.simulationExecutionMarkerLayout[key];
  }

  function simulationExecutionMarkerRectOverlapsLayout(bucket, rect, gap = 7) {
    return (bucket?.boxes || []).some(item => !(
      rect.right + gap < item.left
      || rect.left - gap > item.right
      || rect.bottom + gap < item.top
      || rect.top - gap > item.bottom
    ));
  }

  function simulationExecutionMarkerLocalEnvelope(args) {
    const { rows, idx, x, y, labelLeft, labelRight, bollingerBands, showBollinger } = args;
    if (!rows?.length || typeof x !== 'function' || typeof y !== 'function') return null;
    const safeIdx = Math.max(0, Math.min(rows.length - 1, Math.floor(numberOrNull(idx) ?? 0)));
    const nextIdx = Math.min(rows.length - 1, safeIdx + 1);
    const prevIdx = Math.max(0, safeIdx - 1);
    const nextStep = Math.abs(x(nextIdx) - x(safeIdx));
    const prevStep = Math.abs(x(safeIdx) - x(prevIdx));
    const pixelsPerBar = Math.max(nextStep || prevStep || 1, 0.5);
    const startOffset = Math.floor((labelLeft - x(safeIdx)) / pixelsPerBar) - 2;
    const endOffset = Math.ceil((labelRight - x(safeIdx)) / pixelsPerBar) + 2;
    const startIdx = Math.max(0, safeIdx + Math.min(startOffset, endOffset));
    const endIdx = Math.min(rows.length - 1, safeIdx + Math.max(startOffset, endOffset));
    let top = Number.POSITIVE_INFINITY;
    let bottom = Number.NEGATIVE_INFINITY;
    const includeValue = value => {
      const n = numberOrNull(value);
      if (n == null) return;
      const yy = y(n);
      if (!Number.isFinite(yy)) return;
      top = Math.min(top, yy);
      bottom = Math.max(bottom, yy);
    };
    for (let rowIndex = startIdx; rowIndex <= endIdx; rowIndex += 1) {
      const row = rows[rowIndex] || {};
      ['high', 'low', 'close', 'ma5', 'ma20', 't3_20_0_2'].forEach(key => includeValue(row[key]));
      if (showBollinger === true) {
        const band = bollingerBands?.[rowIndex] || {};
        includeValue(band.upper);
        includeValue(band.lower);
        includeValue(band.middle);
      }
    }
    if (!Number.isFinite(top) || !Number.isFinite(bottom)) return null;
    return { top, bottom, start_idx: startIdx, end_idx: endIdx };
  }

  function drawSimulationExecutionMarker(ctx, xx, yy, event, pad, state, panelKind, layoutContext = {}) {
    const label = simulationExecutionMarkerLabel(event);
    if (!label) return null;
    const type = simulationRuleAwareEventType(event);
    const lane = String(event?.rule_lane || event?.execution?.rule_lane || '').toUpperCase();
    const isExpansionLiteEntry = lane === RULE_LANE_EXPANSION_LITE && ['entry', 'add_on'].includes(type);
    const isEntry = ['entry', 'reentry', 'add_on'].includes(type);
    const isMiss = type === 'stop_close';
    const liveFlash = event?.display?.live_flash === true;
    const focused = event?.display?.focused === true;
    const preferredSide = simulationExecutionMarkerPlacementSide(event);
    const leaderColor = isExpansionLiteEntry
      ? 'rgba(196, 181, 253, 0.98)'
      : isMiss
        ? 'rgba(248,113,113,0.96)'
        : isEntry
          ? 'rgba(74,222,128,0.96)'
          : 'rgba(96,165,250,0.96)';
    ctx.save();
    if (liveFlash || focused) {
      ctx.shadowColor = focused ? 'rgba(250, 204, 21, 0.96)' : leaderColor;
      ctx.shadowBlur = focused ? 22 : 18;
    }
    ctx.font = '900 11px system-ui, sans-serif';
    const width = Math.max(46, Math.ceil(ctx.measureText(label).width + 18));
    const height = 22;
    const chartClearance = 10;
    const horizontalShiftBase = 26;
    const horizontalShiftPerLane = 11;
    const chartMidX = (pad.left + pad.right) / 2;
    const preferredDirection = xx <= chartMidX ? 1 : -1;
    const directions = [preferredDirection, -preferredDirection];
    const sides = [preferredSide, preferredSide === 'top' ? 'bottom' : 'top'];
    let selected = null;

    for (const side of sides) {
      const bucket = simulationExecutionMarkerLayoutBucket(state, panelKind, side);
      for (let lane = 0; lane < 6 && !selected; lane += 1) {
        for (const direction of directions) {
          const shift = direction * (horizontalShiftBase + lane * horizontalShiftPerLane);
          const left = Math.max(pad.left + 3, Math.min(pad.right - width - 3, xx - width / 2 + shift));
          const right = left + width;
          const envelope = simulationExecutionMarkerLocalEnvelope({
            rows: layoutContext.rows,
            idx: layoutContext.idx,
            x: layoutContext.x,
            y: layoutContext.y,
            labelLeft: left,
            labelRight: right,
            bollingerBands: layoutContext.bollingerBands,
            showBollinger: layoutContext.showBollinger
          }) || { top: yy, bottom: yy };
          let top = side === 'top'
            ? envelope.top - height - chartClearance
            : envelope.bottom + chartClearance;
          top += side === 'top' ? -(lane * 3) : lane * 3;
          top = Math.max(pad.top + 3, Math.min(pad.bottom - height - 3, top));
          const rect = { left, right, top, bottom: top + height };
          const clearsChart = side === 'top'
            ? rect.bottom <= envelope.top - chartClearance + 0.5
            : rect.top >= envelope.bottom + chartClearance - 0.5;
          if (!clearsChart) continue;
          if (simulationExecutionMarkerRectOverlapsLayout(bucket, rect, 7)) continue;
          selected = { ...rect, side, lane, envelope, bucket };
          break;
        }
      }
    }

    if (!selected) {
      const side = preferredSide;
      const bucket = simulationExecutionMarkerLayoutBucket(state, panelKind, side);
      const left = Math.max(pad.left + 3, Math.min(pad.right - width - 3, xx - width / 2 + preferredDirection * horizontalShiftBase));
      const top = side === 'top' ? pad.top + 4 : pad.bottom - height - 4;
      selected = {
        left,
        right: left + width,
        top,
        bottom: top + height,
        side,
        lane: 0,
        envelope: { top: yy, bottom: yy },
        bucket
      };
    }

    selected.bucket.boxes.push({
      left: selected.left,
      right: selected.right,
      top: selected.top,
      bottom: selected.bottom
    });
    const x0 = selected.left;
    const y0 = selected.top;
    const placementSide = selected.side;

    // ラベルはローカル価格帯の外側に置き、小さな終点ドットへ斜めの直線で接続する。
    const leaderStartY = placementSide === 'top' ? y0 + height : y0;
    const leaderStartX = (x0 + width / 2) <= xx ? (x0 + width - 10) : (x0 + 10);
    ctx.shadowBlur = 0;
    ctx.strokeStyle = leaderColor;
    ctx.lineWidth = 1.35;
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';
    ctx.beginPath();
    ctx.moveTo(leaderStartX, leaderStartY);
    ctx.lineTo(xx, yy);
    ctx.stroke();

    drawRoundedRect(ctx, x0, y0, width, height, 7);
    ctx.fillStyle = isExpansionLiteEntry
      ? 'rgba(88, 28, 135, 0.97)'
      : isMiss
        ? 'rgba(127, 29, 29, 0.96)'
        : isEntry
          ? 'rgba(20, 83, 45, 0.96)'
          : 'rgba(30, 64, 175, 0.96)';
    ctx.fill();
    ctx.strokeStyle = isExpansionLiteEntry
      ? 'rgba(237, 233, 254, 0.99)'
      : isMiss
        ? 'rgba(254, 202, 202, 0.98)'
        : isEntry
          ? 'rgba(220, 252, 231, 0.98)'
          : 'rgba(219, 234, 254, 0.98)';
    ctx.lineWidth = 1.2;
    ctx.stroke();
    ctx.fillStyle = 'rgba(255,255,255,0.98)';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(label, x0 + width / 2, y0 + height / 2 + 0.5);

    const endpointRadius = 2.8;
    ctx.fillStyle = leaderColor;
    ctx.strokeStyle = 'rgba(2, 6, 23, 0.94)';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.arc(xx, yy, endpointRadius, 0, Math.PI * 2);
    ctx.fill();
    ctx.stroke();

    if (focused || liveFlash) {
      ctx.font = '900 9px system-ui, sans-serif';
      ctx.textBaseline = 'bottom';
      ctx.fillStyle = 'rgba(254, 249, 195, 0.99)';
      ctx.fillText(focused ? '選択' : 'NEW', x0 + width / 2, Math.max(pad.top + 10, y0 - 3));
    }
    ctx.restore();
    return {
      x: x0,
      y: y0,
      width,
      height,
      center_x: x0 + width / 2,
      center_y: y0 + height / 2,
      target_x: xx,
      target_y: yy,
      endpoint_radius: endpointRadius,
      placement_side: placementSide,
      lane: selected.lane,
      chart_envelope_top: selected.envelope.top,
      chart_envelope_bottom: selected.envelope.bottom
    };
  }

  function drawVisibleRangeSimulationCursor(ctx, args) {
    const { rows, state, panelKind, x, pad } = args;
    if (state?.simulationRangeRunInProgress !== true) return;
    const cursorMs = numberOrNull(state?.simulationRangeRunCursorMs);
    if (cursorMs == null || !rows?.length) return;
    const idx = findIndexForTime(rows, cursorMs);
    if (idx == null || !rows[idx]) return;
    const xx = x(idx);
    const panelTf = panelKindToTimeframe(panelKind, state);
    const isM5 = panelTf === 'M5';
    const step = Math.max(0, Math.floor(numberOrNull(state?.simulationRangeRunCursorStep) ?? 0));
    const total = Math.max(0, Math.floor(numberOrNull(state?.simulationRangeRunCursorTotal) ?? 0));
    const eventCount = Math.max(0, Math.floor(numberOrNull(state?.simulationRangeRunLiveEventCount) ?? 0));
    const pulseStrong = step % 2 === 0;

    ctx.save();
    ctx.shadowColor = isM5 ? 'rgba(250, 204, 21, 0.95)' : 'rgba(34, 211, 238, 0.70)';
    ctx.shadowBlur = isM5 ? (pulseStrong ? 14 : 9) : 5;
    ctx.strokeStyle = isM5 ? 'rgba(250, 204, 21, 0.98)' : 'rgba(34, 211, 238, 0.72)';
    ctx.lineWidth = isM5 ? 2.2 : 1.15;
    ctx.setLineDash(isM5 ? [7, 4] : [4, 5]);
    ctx.beginPath();
    ctx.moveTo(xx, pad.top);
    ctx.lineTo(xx, pad.bottom);
    ctx.stroke();
    ctx.setLineDash([]);
    ctx.shadowBlur = 0;

    if (isM5) {
      // 進行方向を直感的に追えるよう、上端に下向き▽カーソルを表示する。
      ctx.fillStyle = 'rgba(250, 204, 21, 0.98)';
      ctx.strokeStyle = 'rgba(255, 251, 235, 0.98)';
      ctx.lineWidth = 1.2;
      ctx.beginPath();
      ctx.moveTo(xx - 8, pad.top + 2);
      ctx.lineTo(xx + 8, pad.top + 2);
      ctx.lineTo(xx, pad.top + 13);
      ctx.closePath();
      ctx.fill();
      ctx.stroke();

      const label = `SIM ${step.toLocaleString()} / ${total.toLocaleString()}  Event ${eventCount}`;
      ctx.font = '900 10px system-ui, sans-serif';
      const labelW = Math.ceil(ctx.measureText(label).width + 16);
      const labelH = 20;
      const labelX = Math.max(pad.left + 3, Math.min(pad.right - labelW - 3, xx + 10));
      const labelY = pad.top + 4;
      drawRoundedRect(ctx, labelX, labelY, labelW, labelH, 7);
      ctx.fillStyle = 'rgba(113, 63, 18, 0.94)';
      ctx.fill();
      ctx.strokeStyle = 'rgba(254, 240, 138, 0.96)';
      ctx.lineWidth = 1;
      ctx.stroke();
      ctx.fillStyle = 'rgba(255, 251, 235, 0.99)';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText(label, labelX + labelW / 2, labelY + labelH / 2 + 0.5);
    }
    ctx.restore();
  }

  function drawSimulationTraceForPanel(ctx, args) {
    const { rows, state, panelKind, x, y, min, max, pad, bollingerBands, showBollinger } = args;
    if (state.showSimulationComments === false || !state.simulationTraceEvents?.length) return;
    state.simulationTraceHitBoxes = state.simulationTraceHitBoxes || [];
    state.simulationExecutionMarkerLayout = state.simulationExecutionMarkerLayout || {};
    state.simulationExecutionMarkerLayout[`${panelKind}:top`] = { boxes: [] };
    state.simulationExecutionMarkerLayout[`${panelKind}:bottom`] = { boxes: [] };
    state.simulationTraceEvents.forEach(event => {
      if ((event.source_type || SIMULATION_TRACE_SOURCE_TYPE) !== SIMULATION_TRACE_SOURCE_TYPE) return;
      if (event.display?.visible === false) return;
      if (!simulationTraceMatchesPanel(event, panelKind, state)) return;
      const idx = simulationTraceIndexForRows(event, rows);
      if (idx == null || !rows[idx]) return;
      const price = numberOrNull(event.price) ?? numberOrNull(rows[idx].close);
      if (price == null || price < min || price > max) return;
      const xx = x(idx);
      const yy = y(price);
      if (xx < pad.left - 18 || xx > pad.right + 18 || yy < pad.top - 18 || yy > pad.bottom + 18) return;
      if (isSimulationExecutionMarker(event)) {
        const marker = drawSimulationExecutionMarker(ctx, xx, yy, event, pad, state, panelKind, { rows, idx, x, y, bollingerBands, showBollinger });
        state.simulationTraceHitBoxes.push({
          id: event.event_id,
          x: marker?.center_x ?? xx,
          y: marker?.center_y ?? yy,
          radius: Math.max(18, (marker?.width || 24) / 2),
          event,
          panelKind
        });
      } else {
        drawSimulationTraceIcon(ctx, xx, yy, event);
        state.simulationTraceHitBoxes.push({ id: event.event_id, x: xx, y: yy, radius: 16, event, panelKind });
      }
      if (state.showAllSimulationComments || event.display?.open || state.openSimulationTraceId === event.event_id) {
        drawSimulationTraceLabel(ctx, xx, yy, event, pad);
      }
    });
  }

  function findSimulationTraceHit(state, px, py) {
    const boxes = state.simulationTraceHitBoxes || [];
    for (let i = boxes.length - 1; i >= 0; i--) {
      const box = boxes[i];
      const dx = px - box.x;
      const dy = py - box.y;
      if (Math.sqrt(dx * dx + dy * dy) <= (box.radius || 16)) return box;
    }
    return null;
  }

  function textLabelPanelLabel(annotation) {
    return String(annotation?.panel || annotation?.timeframe || 'M5').toUpperCase();
  }

  function textLabelMatchesPanel(annotation, panelKind, state) {
    const panel = textLabelPanelLabel(annotation);
    const targetPanel = panelKindToTimeframe(panelKind, state);
    if (targetPanel === 'M5') return ['M5', 'LOWER'].includes(panel);
    return panel === targetPanel || (panel === 'UPPER' && isUpperPanelKind(panelKind));
  }

  function textLabelIndexForRows(annotation, rows) {
    if (!rows?.length) return null;
    const ms = parseDateTimeMs(annotation?.time);
    if (ms != null) return findIndexForTime(rows, ms);
    const hint = numberOrNull(annotation?.x_index_hint);
    if (hint != null) return Math.max(0, Math.min(rows.length - 1, Math.floor(hint)));
    return null;
  }

  function drawTextLabelBox(ctx, x0, y0, annotation, pad) {
    const text = String(annotation.text || 'Expansion').trim() || 'Expansion';
    const display = annotation.display || {};
    const baseW = Math.max(88, Math.floor(numberOrNull(annotation.box?.width) ?? 138));
    const lines = text.split(/\r?\n/).slice(0, 4);
    const primary = lines[0] || 'Expansion';
    const fontSize = primary.length <= 10 ? 18 : 15;
    ctx.save();
    ctx.font = `900 ${fontSize}px system-ui, sans-serif`;
    const measured = Math.max(baseW, ...lines.map(line => ctx.measureText(line || ' ').width + 24));
    const w = Math.min(260, Math.max(92, measured));
    const h = Math.max(34, 18 + lines.length * (fontSize + 3));
    const left = Math.min(pad.right - w - 4, Math.max(pad.left + 4, x0));
    const top = Math.min(pad.bottom - h - 4, Math.max(pad.top + 4, y0));
    const style = String(display.style || 'expansion_label');
    const isExpansion = /expansion/i.test(text) || style === 'expansion_label';
    ctx.shadowColor = 'rgba(0,0,0,.42)';
    ctx.shadowBlur = 10;
    ctx.fillStyle = isExpansion ? 'rgba(250, 204, 21, 0.15)' : 'rgba(15, 23, 42, 0.82)';
    ctx.strokeStyle = isExpansion ? 'rgba(250, 204, 21, 0.88)' : 'rgba(148, 163, 184, 0.74)';
    ctx.lineWidth = 1.6;
    drawRoundedRect(ctx, left, top, w, h, 9);
    ctx.fill();
    ctx.stroke();
    ctx.shadowBlur = 0;
    ctx.textBaseline = 'top';
    ctx.textAlign = 'left';
    lines.forEach((line, index) => {
      ctx.font = `${index === 0 ? 900 : 700} ${index === 0 ? fontSize : 12}px system-ui, sans-serif`;
      ctx.fillStyle = index === 0
        ? (isExpansion ? 'rgba(254, 243, 199, 0.98)' : 'rgba(226, 232, 240, 0.96)')
        : 'rgba(203, 213, 225, 0.94)';
      ctx.fillText(line || ' ', left + 12, top + 9 + index * (fontSize + 3));
    });
    ctx.restore();
    return { x: left, y: top, w, h };
  }

  function drawTextLabelsForPanel(ctx, args) {
    const { rows, state, panelKind, x, y, min, max, pad } = args;
    if (state.showUserComments === false || !state.textAnnotations?.length) return;
    state.textLabelHitBoxes = state.textLabelHitBoxes || [];
    state.textAnnotations.forEach(annotation => {
      if ((annotation.source_type || SAVED_TEXT_LABEL_SOURCE_TYPE) !== SAVED_TEXT_LABEL_SOURCE_TYPE) return;
      if ((annotation.event_type || SAVED_TEXT_LABEL_EVENT_TYPE) !== SAVED_TEXT_LABEL_EVENT_TYPE) return;
      if (annotation.display?.visible === false) return;
      if (!textLabelMatchesPanel(annotation, panelKind, state)) return;
      const idx = textLabelIndexForRows(annotation, rows);
      if (idx == null || !rows[idx]) return;
      const price = numberOrNull(annotation.price) ?? numberOrNull(rows[idx].close);
      if (price == null || price < min || price > max) return;
      const anchorX = x(idx);
      const anchorY = y(price);
      if (anchorX < pad.left - 16 || anchorX > pad.right + 16 || anchorY < pad.top - 16 || anchorY > pad.bottom + 16) return;
      const offsetX = numberOrNull(annotation.display?.offset_x) ?? 12;
      const offsetY = numberOrNull(annotation.display?.offset_y) ?? -48;
      const box = drawTextLabelBox(ctx, anchorX + offsetX, anchorY + offsetY, annotation, pad);
      state.textLabelHitBoxes.push({ id: annotation.id, ...box, anchorX, anchorY, annotation, panelKind });
    });
  }

  function findTextLabelHit(state, px, py) {
    const boxes = state.textLabelHitBoxes || [];
    for (let i = boxes.length - 1; i >= 0; i--) {
      const box = boxes[i];
      if (px >= box.x && px <= box.x + box.w && py >= box.y && py <= box.y + box.h) return box;
    }
    return null;
  }

  function circledNumber(value) {
    const n = Math.max(1, Math.floor(numberOrNull(value) ?? 1));
    const circled = ['①','②','③','④','⑤','⑥','⑦','⑧','⑨','⑩','⑪','⑫','⑬','⑭','⑮','⑯','⑰','⑱','⑲','⑳'];
    return circled[n - 1] || `(${n})`;
  }

  function markerIndexForRows(marker, rows) {
    const explicitMs = numberOrNull(marker?.time_ms);
    if (explicitMs != null) return findIndexForTime(rows, explicitMs);
    const ms = parseDateTimeMs(marker?.time);
    if (ms != null) return findIndexForTime(rows, ms);
    return null;
  }

  function visibleVerticalMarkers(state, rows) {
    return (state.verticalAnnotations || [])
      .filter(marker => marker?.display?.visible !== false)
      .map(marker => ({ marker, idx: markerIndexForRows(marker, rows) }))
      .filter(item => item.idx != null && rows[item.idx]);
  }

  function visibleCycleVerticalMarkers(state, rows) {
    return (state.cycleVerticalAnnotations || [])
      .filter(marker => marker?.display?.visible !== false)
      .map(marker => ({ marker, idx: markerIndexForRows(marker, rows) }))
      .filter(item => item.idx != null && rows[item.idx]);
  }

  function drawVerticalMarkerLabel(ctx, xx, yy, text) {
    ctx.save();
    ctx.shadowColor = 'rgba(0, 0, 0, 0.34)';
    ctx.shadowBlur = 6;
    ctx.fillStyle = 'rgba(15, 23, 42, 0.78)';
    ctx.strokeStyle = 'rgba(226, 232, 240, 0.86)';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.arc(xx, yy, 10.5, 0, Math.PI * 2);
    ctx.fill();
    ctx.stroke();
    ctx.shadowBlur = 0;
    ctx.fillStyle = 'rgba(255, 255, 255, 0.98)';
    ctx.font = '13px system-ui, sans-serif';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(text, xx, yy + 0.5);
    ctx.restore();
  }

  function drawCycleVerticalMarkerLabel(ctx, xx, yy, text) {
    ctx.save();
    ctx.shadowColor = 'rgba(0, 0, 0, 0.42)';
    ctx.shadowBlur = 7;
    ctx.fillStyle = 'rgba(15, 23, 42, 0.82)';
    ctx.strokeStyle = 'rgba(253, 224, 71, 0.92)';
    ctx.lineWidth = 1.2;
    ctx.beginPath();
    ctx.arc(xx, yy, 11.5, 0, Math.PI * 2);
    ctx.fill();
    ctx.stroke();
    ctx.shadowBlur = 0;
    ctx.fillStyle = 'rgba(253, 224, 71, 0.98)';
    ctx.font = '700 13px system-ui, sans-serif';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(text, xx, yy + 0.5);
    ctx.restore();
  }

  function drawSavedVerticalMarkersForPanel(ctx, args) {
    const { rows, state, panelKind, x, pad } = args;
    const items = visibleVerticalMarkers(state, rows);
    if (!items.length) return;
    items.forEach(({ marker, idx }) => {
      const xx = x(idx);
      if (xx < pad.left - 10 || xx > pad.right + 10) return;
      ctx.save();
      ctx.strokeStyle = 'rgba(255, 255, 255, 0.85)';
      ctx.lineWidth = 0.65;
      ctx.setLineDash([1.5, 5]);
      ctx.beginPath();
      ctx.moveTo(xx, pad.top);
      ctx.lineTo(xx, pad.bottom);
      ctx.stroke();
      ctx.restore();
      const label = marker.label || circledNumber(marker.no);
      const labelY = pad.top + 14;
      drawVerticalMarkerLabel(ctx, xx, labelY, label);
      state.savedVerticalHitBoxes = state.savedVerticalHitBoxes || [];
      state.savedVerticalHitBoxes.push({ id: marker.id, x: xx, labelY, top: pad.top, bottom: pad.bottom, radius: 11, marker, panelKind });
    });
  }

  function drawSavedCycleVerticalMarkersForPanel(ctx, args) {
    const { rows, state, panelKind, x, pad } = args;
    const items = visibleCycleVerticalMarkers(state, rows);
    if (!items.length) return;
    items.forEach(({ marker, idx }) => {
      const xx = x(idx);
      if (xx < pad.left - 10 || xx > pad.right + 10) return;
      ctx.save();
      ctx.strokeStyle = 'rgba(253, 224, 71, 0.82)';
      ctx.lineWidth = 2.15;
      ctx.setLineDash([8, 4]);
      ctx.beginPath();
      ctx.moveTo(xx, pad.top);
      ctx.lineTo(xx, pad.bottom);
      ctx.stroke();
      ctx.restore();
      const label = marker.label || circledNumber(marker.no);
      const labelY = pad.top + 36;
      drawCycleVerticalMarkerLabel(ctx, xx, labelY, label);
      state.savedCycleVerticalHitBoxes = state.savedCycleVerticalHitBoxes || [];
      state.savedCycleVerticalHitBoxes.push({ id: marker.id, x: xx, labelY, radius: 13, marker, panelKind });
    });
  }

  function findSavedVerticalHit(state, px, py) {
    const boxes = state.savedVerticalHitBoxes || [];
    for (let i = boxes.length - 1; i >= 0; i--) {
      const box = boxes[i];
      const dx = Math.abs(px - box.x);
      const inY = py >= (box.top - 12) && py <= (box.bottom + 12);
      if (dx <= (box.radius || 9) && inY) return box;
    }
    return null;
  }

  function findSavedCycleVerticalHit(state, px, py) {
    const boxes = state.savedCycleVerticalHitBoxes || [];
    for (let i = boxes.length - 1; i >= 0; i--) {
      const box = boxes[i];
      const dx = Math.abs(px - box.x);
      const dy = Math.abs(py - box.labelY);
      if (dx <= (box.radius || 11) && dy <= (box.radius || 11)) return box;
    }
    return null;
  }

  function nextVerticalMarkerNo(state) {
    const nums = (state.verticalAnnotations || []).map(x => numberOrNull(x.no)).filter(x => x != null);
    return Math.max(0, ...nums) + 1;
  }

  function createSavedVerticalMarkerFromPanel(state, panel, idx) {
    if (!panel || !panel.rows?.length) return null;
    const safeIdx = Math.max(0, Math.min(panel.rows.length - 1, Math.floor(numberOrNull(idx) ?? 0)));
    const row = panel.rows[safeIdx] || {};
    const ms = numberOrNull(row.start_ms) ?? rowTimeMs(row);
    const created = nowLocalIso();
    const no = nextVerticalMarkerNo(state);
    return {
      id: `vertical_${compactTimestamp()}_${Math.random().toString(36).slice(2, 7)}`,
      no,
      created_at: created,
      updated_at: created,
      source_type: SAVED_VERTICAL_SOURCE_TYPE,
      event_type: SAVED_VERTICAL_EVENT_TYPE,
      time: formatRowDateTime(ms) || row.datetime || [row.date, row.time].filter(Boolean).join(' ') || '',
      time_ms: ms,
      label: circledNumber(no),
      display: { visible: true, style: 'saved_vertical_marker' },
      chart_state: chartStateSnapshot(state),
      note: 'Saved from fx_chart_viewer synchronized vertical cursor by right-click.'
    };
  }

  function nextCycleVerticalMarkerNo(state) {
    const nums = (state.cycleVerticalAnnotations || []).map(x => numberOrNull(x.no)).filter(x => x != null);
    return Math.max(0, ...nums) + 1;
  }

  function createSavedCycleVerticalMarkerFromPanel(state, panel, idx) {
    if (!panel || !panel.rows?.length) return null;
    const safeIdx = Math.max(0, Math.min(panel.rows.length - 1, Math.floor(numberOrNull(idx) ?? 0)));
    const row = panel.rows[safeIdx] || {};
    const ms = numberOrNull(row.start_ms) ?? rowTimeMs(row);
    const created = nowLocalIso();
    const no = nextCycleVerticalMarkerNo(state);
    return {
      id: `cycle_vertical_${compactTimestamp()}_${Math.random().toString(36).slice(2, 7)}`,
      no,
      created_at: created,
      updated_at: created,
      source_type: SAVED_CYCLE_VERTICAL_SOURCE_TYPE,
      event_type: SAVED_CYCLE_VERTICAL_EVENT_TYPE,
      time: formatRowDateTime(ms) || row.datetime || [row.date, row.time].filter(Boolean).join(' ') || '',
      time_ms: ms,
      label: circledNumber(no),
      display: { visible: true, style: 'saved_cycle_vertical_marker' },
      chart_state: chartStateSnapshot(state),
      note: 'Saved from fx_chart_viewer cycle vertical marker by right-click.'
    };
  }

  function findCommentHit(state, px, py) {
    const boxes = state.commentHitBoxes || [];
    for (let i = boxes.length - 1; i >= 0; i--) {
      const box = boxes[i];
      const dx = px - box.x;
      const dy = py - box.y;
      if (Math.sqrt(dx * dx + dy * dy) <= (box.radius || 12)) return box;
    }
    return null;
  }



  function findSavedHsiHit(state, px, py) {
    const boxes = state.savedHsiHitBoxes || [];
    for (let i = boxes.length - 1; i >= 0; i--) {
      const box = boxes[i];
      const dx = px - box.x;
      const dy = py - box.y;
      if (Math.sqrt(dx * dx + dy * dy) <= (box.radius || 14)) return box;
    }
    return null;
  }

  function findCurrentHsiAnchorHit(state, px, py) {
    const box = state.currentHsiAnchorHitBox;
    if (!box) return null;
    const dx = px - box.x;
    const dy = py - box.y;
    return Math.sqrt(dx * dx + dy * dy) <= (box.radius || 16) ? box : null;
  }

  function createSavedHsiAnnotationFromState(source, state, panel) {
    const anchor = state?.hsiAnchor;
    const anchorPrice = numberOrNull(anchor?.price);
    if (!panel || anchorPrice == null) return null;
    const idx = Math.max(0, Math.min(panel.rows.length - 1, Math.floor(numberOrNull(anchor?.index) ?? 0)));
    const row = panel.rows[idx] || {};
    const panelName = panelTimeframeLabel(panel, state);
    const values = parseHsiValues(state?.hsiValuesText);
    const scale = numberOrNull(state?.hsiScale) ?? getManualHsiSettings(source).scale;
    const direction = normalizeHsiDirection(state?.hsiDirection);
    const created = nowLocalIso();
    return {
      id: `hsi_${compactTimestamp()}_${Math.random().toString(36).slice(2, 7)}`,
      created_at: created,
      updated_at: created,
      source_type: SAVED_HSI_SOURCE_TYPE,
      event_type: SAVED_HSI_EVENT_TYPE,
      panel: panelName,
      timeframe: panelName,
      time: formatRowDateTime(rowTimeMs(row)) || anchor.time || row.datetime || [row.date, row.time].filter(Boolean).join(' ') || '',
      price: anchorPrice,
      x_index_hint: idx,
      title: `保存HSI ×${formatHsiNumber(scale, 3)}`,
      hsi: {
        values,
        values_text: values.join(','),
        scale,
        direction,
        point_size: hsiPointSize(source)
      },
      display: { visible: true, pinned: true, style: 'saved_hsi' },
      chart_state: chartStateSnapshot(state),
      note: 'Saved from fx_chart_viewer current manual HSI anchor by right-click.'
    };
  }

  function hideHsiContextMenu(backdrop) {
    const menu = backdrop?.querySelector?.('[data-role="hsi-context-menu"]');
    if (!menu) return;
    menu.classList.remove('is-open');
    menu.innerHTML = '';
  }

  function showHsiContextMenu(backdrop, state, options) {
    const menu = backdrop.querySelector('[data-role="hsi-context-menu"]');
    const body = backdrop.querySelector('[data-role="body"]');
    if (!menu || !body) return;
    const bodyRect = body.getBoundingClientRect();
    const x = Math.max(10, Math.min(bodyRect.width - 220, options.clientX - bodyRect.left));
    const y = Math.max(56, Math.min(bodyRect.height - 120, options.clientY - bodyRect.top));
    menu.style.left = `${x}px`;
    menu.style.top = `${y}px`;
    menu.innerHTML = `
      <div class="gpt-fx-chart-context-menu-title">${escapeHtml(options.title || 'HSI仮説')}</div>
      <div class="gpt-fx-chart-context-menu-meta">${escapeHtml(options.meta || '')}</div>
      <div class="gpt-fx-chart-context-menu-actions">
        ${options.kind === 'point' ? '<button class="gpt-fx-chart-context-menu-btn" type="button" data-hsi-menu-action="save-hsi-up">HSI上を追加</button>' : ''}
        ${options.kind === 'point' ? '<button class="gpt-fx-chart-context-menu-btn" type="button" data-hsi-menu-action="save-hsi-down">HSI下を追加</button>' : ''}
        ${options.kind === 'point' && options.onOpenReference ? '<button class="gpt-fx-chart-context-menu-btn is-primary" type="button" data-hsi-menu-action="open-reference">この時点の状態を見る</button>' : ''}
        ${options.kind === 'point' ? '<button class="gpt-fx-chart-context-menu-btn" type="button" data-hsi-menu-action="add-comment">コメントを追加</button>' : ''}
        ${options.kind === 'point' ? '<button class="gpt-fx-chart-context-menu-btn" type="button" data-hsi-menu-action="add-text-label">Expansionラベル追加</button>' : ''}
        ${options.kind === 'point' ? '<button class="gpt-fx-chart-context-menu-btn" type="button" data-hsi-menu-action="save-cycle-vertical">サイクル縦線追加</button>' : ''}
        ${options.kind === 'saved' ? '<button class="gpt-fx-chart-context-menu-btn is-danger" type="button" data-hsi-menu-action="delete-saved">保存HSIを削除</button>' : ''}
        ${options.kind === 'vertical-saved' ? '<button class="gpt-fx-chart-context-menu-btn is-danger" type="button" data-hsi-menu-action="delete-vertical">保存縦線を削除</button>' : ''}
        ${options.kind === 'cycle-vertical-saved' ? '<button class="gpt-fx-chart-context-menu-btn is-danger" type="button" data-hsi-menu-action="delete-cycle-vertical">サイクル縦線を削除</button>' : ''}
        ${options.kind === 'current' ? '<button class="gpt-fx-chart-context-menu-btn" type="button" data-hsi-menu-action="save-current">このHSI仮説を保存</button>' : ''}
        ${options.kind === 'point' ? '<button class="gpt-fx-chart-context-menu-btn" type="button" data-hsi-menu-action="save-vertical">この縦線を保存</button>' : ''}
        <button class="gpt-fx-chart-context-menu-btn" type="button" data-hsi-menu-action="close">閉じる</button>
      </div>
    `;
    menu.classList.add('is-open');

    const runAndAutoCloseMenu = async (event, handler) => {
      event.preventDefault();
      event.stopPropagation();
      // 操作ボタンを押した瞬間に閉じる。
      // handler内でredraw()やコメントPopover表示が走っても、右クリックメニューを残さない。
      hideHsiContextMenu(backdrop);
      try {
        await handler?.();
      } finally {
        hideHsiContextMenu(backdrop);
      }
    };

    menu.querySelector('[data-hsi-menu-action="close"]')?.addEventListener('click', event => {
      event.preventDefault();
      event.stopPropagation();
      hideHsiContextMenu(backdrop);
    });
    menu.querySelector('[data-hsi-menu-action="save-hsi-up"]')?.addEventListener('click', event => {
      runAndAutoCloseMenu(event, options.onSaveHsiUp);
    });
    menu.querySelector('[data-hsi-menu-action="save-hsi-down"]')?.addEventListener('click', event => {
      runAndAutoCloseMenu(event, options.onSaveHsiDown);
    });
    menu.querySelector('[data-hsi-menu-action="open-reference"]')?.addEventListener('click', event => {
      runAndAutoCloseMenu(event, options.onOpenReference);
    });
    menu.querySelector('[data-hsi-menu-action="add-comment"]')?.addEventListener('click', event => {
      runAndAutoCloseMenu(event, options.onAddComment);
    });
    menu.querySelector('[data-hsi-menu-action="add-text-label"]')?.addEventListener('click', event => {
      runAndAutoCloseMenu(event, options.onAddTextLabel);
    });
    menu.querySelector('[data-hsi-menu-action="save-current"]')?.addEventListener('click', event => {
      runAndAutoCloseMenu(event, options.onSave);
    });
    menu.querySelector('[data-hsi-menu-action="delete-saved"]')?.addEventListener('click', event => {
      runAndAutoCloseMenu(event, options.onDelete);
    });
    menu.querySelector('[data-hsi-menu-action="save-cycle-vertical"]')?.addEventListener('click', event => {
      runAndAutoCloseMenu(event, options.onSaveCycleVertical);
    });
    menu.querySelector('[data-hsi-menu-action="save-vertical"]')?.addEventListener('click', event => {
      runAndAutoCloseMenu(event, options.onSaveVertical);
    });
    menu.querySelector('[data-hsi-menu-action="delete-vertical"]')?.addEventListener('click', event => {
      runAndAutoCloseMenu(event, options.onDeleteVertical);
    });
    menu.querySelector('[data-hsi-menu-action="delete-cycle-vertical"]')?.addEventListener('click', event => {
      runAndAutoCloseMenu(event, options.onDeleteCycleVertical);
    });
  }

  function createCommentFromPoint(source, state, panel, idx, price) {
    const row = panel.rows[idx] || {};
    const panelName = panelTimeframeLabel(panel, state);
    const created = nowLocalIso();
    return {
      id: `comment_${compactTimestamp()}_${Math.random().toString(36).slice(2, 7)}`,
      created_at: created,
      updated_at: created,
      source_type: 'human_comment',
      panel: panelName,
      timeframe: panelName,
      time: formatRowDateTime(rowTimeMs(row)) || row.datetime || [row.date, row.time].filter(Boolean).join(' ') || '',
      price,
      x_index_hint: idx,
      comment_type: 'note',
      title: '',
      text: '',
      tags: [],
      display: { pinned: false, open: true, editing: true },
      chart_state: chartStateSnapshot(state),
      note: 'Created from fx_chart_viewer comment mode.'
    };
  }


  function createTextLabelFromPoint(source, state, panel, idx, price, text = 'Expansion') {
    const row = panel.rows[idx] || {};
    const panelName = panelTimeframeLabel(panel, state);
    const created = nowLocalIso();
    return {
      id: `text_label_${compactTimestamp()}_${Math.random().toString(36).slice(2, 7)}`,
      created_at: created,
      updated_at: created,
      source_type: SAVED_TEXT_LABEL_SOURCE_TYPE,
      event_type: SAVED_TEXT_LABEL_EVENT_TYPE,
      panel: panelName,
      timeframe: panelName,
      time: formatRowDateTime(rowTimeMs(row)) || row.datetime || [row.date, row.time].filter(Boolean).join(' ') || '',
      price,
      x_index_hint: idx,
      text: String(text || 'Expansion'),
      box: { width: 138, height: 42 },
      display: { visible: true, pinned: true, open: true, editing: true, style: 'expansion_label', offset_x: 12, offset_y: -48 },
      chart_state: chartStateSnapshot(state),
      note: 'Created from fx_chart_viewer text label mode.'
    };
  }


  function resolveStudioConfirmDialog() {
    if (typeof window.showStudioConfirmDialog === 'function') return window.showStudioConfirmDialog;
    try {
      if (window.parent && window.parent !== window && typeof window.parent.showStudioConfirmDialog === 'function') {
        return window.parent.showStudioConfirmDialog.bind(window.parent);
      }
    } catch (_) {
      // same-originでない場合はFX専用の画面内ダイアログへフォールバックする。
    }
    return null;
  }

  function showFxChartConfirmDialog(options = {}) {
    const studioConfirm = resolveStudioConfirmDialog();
    if (studioConfirm) return studioConfirm(options);

    return new Promise(resolve => {
      const old = document.querySelector('.gpt-fx-chart-dialog-backdrop[data-runtime="fx-confirm"]');
      if (old) old.remove();

      const backdrop = document.createElement('div');
      backdrop.className = 'gpt-fx-chart-dialog-backdrop';
      backdrop.setAttribute('data-runtime', 'fx-confirm');
      backdrop.innerHTML = `
        <section class="gpt-fx-chart-dialog-panel" role="dialog" aria-modal="true" aria-label="FX chart confirmation dialog">
          <div class="gpt-fx-chart-dialog-title" data-role="title"></div>
          <div class="gpt-fx-chart-dialog-message" data-role="message"></div>
          <div class="gpt-fx-chart-dialog-detail" data-role="detail"></div>
          <div class="gpt-fx-chart-dialog-actions">
            <button type="button" data-action="cancel"></button>
            <button type="button" data-action="ok"></button>
          </div>
        </section>`;
      backdrop.querySelector('[data-role="title"]').textContent = String(options.title || '確認');
      backdrop.querySelector('[data-role="message"]').textContent = String(options.message || '実行しますか？');
      const detail = backdrop.querySelector('[data-role="detail"]');
      detail.textContent = String(options.detail || '');
      detail.style.display = String(options.detail || '').trim() ? '' : 'none';
      backdrop.querySelector('[data-action="ok"]').textContent = String(options.okText || 'OK');
      backdrop.querySelector('[data-action="cancel"]').textContent = String(options.cancelText || 'キャンセル');

      const previousFocus = document.activeElement;
      function finish(ok) {
        backdrop.remove();
        if (previousFocus && typeof previousFocus.focus === 'function') {
          requestAnimationFrame(() => previousFocus.focus({ preventScroll: true }));
        }
        resolve(!!ok);
      }
      backdrop.addEventListener('click', event => {
        const btn = event.target.closest('button[data-action]');
        if (!btn) return;
        event.preventDefault();
        event.stopPropagation();
        finish(btn.dataset.action === 'ok');
      }, true);
      backdrop.addEventListener('keydown', event => {
        if (event.key === 'Escape' || event.key === 'Esc') {
          event.preventDefault();
          event.stopPropagation();
          finish(false);
        }
        if (event.key === 'Enter') {
          event.preventDefault();
          event.stopPropagation();
          finish(true);
        }
      }, true);
      document.body.appendChild(backdrop);
      requestAnimationFrame(() => {
        backdrop.classList.add('is-open');
        backdrop.querySelector('[data-action="cancel"]')?.focus({ preventScroll: true });
      });
    });
  }

  function buildCommentDeleteDialogDetail(comment) {
    return [
      `${comment.panel || '-'} / ${comment.time || '-'} / ${round3(comment.price)}`,
      comment.title ? `title: ${comment.title}` : '',
      comment.text ? String(comment.text).slice(0, 240) : ''
    ].filter(Boolean).join('\n');
  }

  function commentTypeLabel(value) {
    const v = normalizeCommentType(value || 'note');
    const labels = {
      note: 'note',
      dawUp: 'dawUp',
      dawDown: 'dawDown',
      dawNone: 'dawNone',
      entry: 'entry',
      closeOk: 'closeOk',
      closeMiss: 'closeMiss',
      exit: 'exit'
    };
    return labels[v] || v;
  }

  function buildTextLabelDeleteDialogDetail(annotation) {
    return [
      `${annotation.panel || '-'} / ${annotation.time || '-'} / ${round3(annotation.price)}`,
      String(annotation.text || '').slice(0, 240)
    ].filter(Boolean).join('\n');
  }

  function renderTextLabelPopover(backdrop, state) {
    const popover = backdrop.querySelector('[data-role="text-label-popover"]');
    if (!popover) return;
    const labels = state.textAnnotations || [];
    const annotation = labels.find(x => x.id === state.openTextLabelId);
    const hit = (state.textLabelHitBoxes || []).find(x => x.id === state.openTextLabelId);
    if (!annotation || !hit || state.showUserComments === false) {
      popover.classList.remove('is-open');
      popover.innerHTML = '';
      return;
    }
    const body = backdrop.querySelector('[data-role="body"]');
    const bodyRect = body.getBoundingClientRect();
    const x = Math.max(10, Math.min(bodyRect.width - 270, hit.x + 8));
    const shouldPlaceBelow = hit.y < 160;
    const y = shouldPlaceBelow
      ? Math.max(8, Math.min(bodyRect.height - 130, hit.y + hit.h + 6))
      : Math.max(56, Math.min(bodyRect.height - 12, hit.y - 8));
    popover.style.left = `${x}px`;
    popover.style.top = `${y}px`;
    popover.classList.toggle('is-below', shouldPlaceBelow);
    popover.classList.add('is-open');

    annotation.display = { ...(annotation.display || {}), open: true, editing: true };
    state.textLabelEditDrafts = state.textLabelEditDrafts || {};
    const draft = state.textLabelEditDrafts[annotation.id] || { text: annotation.text || 'Expansion' };
    state.textLabelEditDrafts[annotation.id] = draft;
    popover.innerHTML = `
      <div class="gpt-fx-chart-comment-form">
        <div class="gpt-fx-chart-comment-title">チャートテキスト</div>
        <textarea class="gpt-fx-chart-comment-textarea" data-role="text-label-text" placeholder="Expansion など">${escapeHtml(draft.text || '')}</textarea>
        <div class="gpt-fx-chart-comment-meta">${escapeHtml(annotation.panel)} / ${escapeHtml(annotation.time)} / ${round3(annotation.price)}</div>
        <div class="gpt-fx-chart-comment-buttons">
          <button class="gpt-fx-chart-comment-mini-btn is-danger" type="button" data-text-label-action="delete">削除</button>
          <button class="gpt-fx-chart-comment-mini-btn" type="button" data-text-label-action="cancel">閉じる</button>
          <button class="gpt-fx-chart-comment-mini-btn" type="button" data-text-label-action="save">保存</button>
        </div>
      </div>`;
    const textArea = popover.querySelector('[data-role="text-label-text"]');
    textArea?.addEventListener('input', () => { draft.text = textArea.value || ''; });
    popover.querySelector('[data-text-label-action="save"]')?.addEventListener('click', async () => {
      draft.text = textArea?.value ?? draft.text ?? '';
      annotation.text = draft.text || 'Expansion';
      annotation.updated_at = nowLocalIso();
      annotation.display = { ...(annotation.display || {}), open: false, editing: false };
      delete annotation.is_draft;
      delete state.textLabelEditDrafts?.[annotation.id];
      state.openTextLabelId = null;
      await state.requestCommentSave?.();
      state.redraw?.();
    });
    popover.querySelector('[data-text-label-action="cancel"]')?.addEventListener('click', () => {
      delete state.textLabelEditDrafts?.[annotation.id];
      if (!annotation.text && annotation.is_draft) {
        state.textAnnotations = state.textAnnotations.filter(x => x.id !== annotation.id);
        if (state.commentSidecar) state.commentSidecar.text_annotations = state.textAnnotations;
      } else {
        annotation.display = { ...(annotation.display || {}), open: false, editing: false };
      }
      state.openTextLabelId = null;
      state.redraw?.();
    });
    popover.querySelector('[data-text-label-action="delete"]')?.addEventListener('click', async () => {
      const ok = await showFxChartConfirmDialog({
        title: 'テキストを削除しますか？',
        message: 'チャート上テキストラベルを削除します。',
        detail: buildTextLabelDeleteDialogDetail(annotation),
        okText: '削除',
        cancelText: 'キャンセル',
        danger: true
      });
      if (!ok) return;
      delete state.textLabelEditDrafts?.[annotation.id];
      state.textAnnotations = state.textAnnotations.filter(x => x.id !== annotation.id);
      if (state.commentSidecar) state.commentSidecar.text_annotations = state.textAnnotations;
      state.openTextLabelId = null;
      await state.requestCommentSave?.();
      state.redraw?.();
    });
  }


  function simulationStateBlock(value) {
    if (!value || typeof value !== 'object' || !Object.keys(value).length) return '-';
    return JSON.stringify(value, null, 2);
  }

  function placeSimulationTracePopover(popover, body, hit) {
    const bodyRect = body.getBoundingClientRect();
    const margin = 10;
    const gap = 18;
    popover.style.visibility = 'hidden';
    popover.classList.add('is-open');
    popover.classList.remove('is-below');
    popover.style.left = '0px';
    popover.style.top = '0px';
    const width = Math.min(popover.offsetWidth || 780, Math.max(320, bodyRect.width - margin * 2));
    const height = Math.min(popover.offsetHeight || 420, Math.max(160, bodyRect.height - margin * 2));
    const available = {
      right: bodyRect.width - hit.x - gap - margin,
      left: hit.x - gap - margin,
      below: bodyRect.height - hit.y - gap - margin,
      above: hit.y - gap - margin
    };
    let placement = 'right';
    if (available.right >= width || available.left >= width) placement = available.right >= available.left ? 'right' : 'left';
    else if (available.below >= height || available.above >= height) placement = available.below >= available.above ? 'below' : 'above';
    else placement = Math.max(available.right, available.left) >= Math.max(available.below, available.above) ? (available.right >= available.left ? 'right' : 'left') : (available.below >= available.above ? 'below' : 'above');
    let x = hit.x + gap;
    let y = hit.y - height / 2;
    if (placement === 'left') x = hit.x - width - gap;
    if (placement === 'below') { x = hit.x - width / 2; y = hit.y + gap; }
    if (placement === 'above') { x = hit.x - width / 2; y = hit.y - height - gap; }
    x = Math.max(margin, Math.min(bodyRect.width - width - margin, x));
    y = Math.max(margin, Math.min(bodyRect.height - height - margin, y));
    popover.style.left = `${x}px`;
    popover.style.top = `${y}px`;
    popover.dataset.placement = placement;
    popover.classList.toggle('is-below', placement === 'below');
    popover.style.visibility = 'visible';
  }

  function simulationCatalogEventKey(traceEvent) {
    const eventType = simulationRuleAwareEventType(traceEvent);
    const actionRaw = String(traceEvent?.execution?.action || '').toLowerCase();
    const action = String(traceEvent?.rule_lane || traceEvent?.execution?.rule_lane || '').toUpperCase() === RULE_LANE_NORMAL && actionRaw === 'reentry' ? 'entry' : actionRaw;
    if (action === 'partial_close' || eventType === 'partial_close') return 'partial_close';
    if (action === 'stop_close' || eventType === 'stop_close') return 'stop_close';
    if (action === 'full_close' || eventType === 'close') return 'close';
    if (action === 'reentry' || eventType === 'reentry') return 'reentry';
    if (action === 'add_on' || eventType === 'add_on') return 'add_on';
    if (action === 'entry' || eventType === 'entry') return 'entry';
    return eventType || 'default';
  }

  function previousHsiLabel(label) {
    const current = String(label || '');
    const index = HSI_RANGE_LEVELS.findIndex(item => item.label === current);
    return index > 0 ? HSI_RANGE_LEVELS[index - 1].label : '';
  }

  function simulationCatalogTemplateValues(traceEvent) {
    const summary = String(traceEvent?.summary || '');
    const execution = traceEvent?.execution && typeof traceEvent.execution === 'object' ? traceEvent.execution : {};
    const unitsMatch = summary.match(/(\d+(?:\.\d+)?)\s*単位/);
    const roleMatch = summary.match(/\b(CORE|RUNNER|ADD_ON)\b/i);
    const positionId = String((traceEvent?.position_ids || [])[0] || '');
    const afterPositions = traceEvent?.state_after?.portfolio?.open_positions || [];
    const afterPosition = afterPositions.find(item => String(item?.position_id || '') === positionId) || afterPositions[0] || {};
    const nextTargetLabel = execution.next_target_label || '';
    const reachedTargetLabel = execution.reached_target_label || previousHsiLabel(nextTargetLabel) || 'HSI境界';
    return {
      units: execution.units ?? unitsMatch?.[1] ?? '設定',
      role: execution.role || roleMatch?.[1]?.toUpperCase() || 'NORMAL',
      reached_target_label: reachedTargetLabel,
      next_target_label: nextTargetLabel || '次目標未設定',
      remaining_units: execution.remaining_units ?? afterPosition.units_open ?? '-',
      direction: execution.side || traceEvent?.direction || '-',
      price: round3(execution.price ?? traceEvent?.price)
    };
  }

  function formatSimulationCatalogText(template, values) {
    return String(template || '').replace(/\{([a-z0-9_]+)\}/gi, (_, key) => String(values?.[key] ?? '-'));
  }

  function simulationJapaneseJudgment(traceEvent, catalog) {
    const key = simulationCatalogEventKey(traceEvent);
    const template = catalog?.judgment_templates?.[key] || catalog?.judgment_templates?.default || {};
    const values = simulationCatalogTemplateValues(traceEvent);
    return {
      title: formatSimulationCatalogText(template.title || 'シミュレーション判断を記録しました。', values),
      body: formatSimulationCatalogText(template.body || traceEvent?.summary || '日本語説明はありません。', values)
    };
  }

  function simulationDynamicJapaneseText(code, kind, traceEvent, fallback) {
    const values = simulationCatalogTemplateValues(traceEvent);
    const dynamicReason = {
      NEXT_HSI_BOUNDARY_REACHED: `${values.reached_target_label}到達`,
      CORE_PARTIAL_TAKE_PROFIT: `${values.role}を${values.units}単位利確`,
      POSITION_UNITS_REDUCED: `残り${values.remaining_units}単位を保有`,
      H1_EXIT_TRIGGER_CONFIRMED: 'H1保有根拠の崩れを確認',
      M5_CLOSE_EXECUTION: 'M5確定足で決済実行',
      CLOSE_OK: '利益確定として決済',
      CLOSE_OK_NEXT_HSI_TARGET: `${values.reached_target_label}到達`,
      STOP_CLOSE_ENTRY_HSI_ANCHOR: 'Entryに使用したHSI起点へ到達',
      STOP_CLOSE_TARGET_DISTANCE_RATIO: 'Target距離と固定倍率からEntry時に確定したStopへ到達',
      STOP_CLOSE_HSI_ANCHOR_HARD_LIMIT: '倍率StopへHSI起点Hard Limitを適用',
      NORMAL_DOW_STRUCTURE_BROKEN_BEFORE_ENTRY: 'Entry前に後発の逆方向M5 Dow Confirmationが成立したためEntry権利を失効',
      NORMAL_HSI_ANCHOR_INVALIDATED_BEFORE_ENTRY: '崩壊したDow構造の通常HSI起点をEntry判定から無効化',
      NORMAL_H4_SAME_DIRECTION_R4_ENTRY_BLOCKED: 'H4現在波がEntry方向へR4以上進行しているため新規Normal Entry禁止',
      DAY_UP_H4_DOWN_R5_SHORT_ENTRY_BLOCKED: 'Day上昇中のH4調整下降がR5以上進行しているため新規Short Entry禁止',
      NORMAL_CLOSE_MISS_TARGET_DISTANCE_RATIO_FIXED: 'Target距離とJSON固定倍率からCloseMiss StopをEntry時に固定',
      SINGLE_CLOSE_ALL_UNITS: `${values.units}単位を全決済`,
      AMBIGUOUS_STOP_TARGET: '同一M5足でStopとTargetの両方へ到達',
      NORMAL_ADD_ON_DISABLED: '通常PositionではAdd-on禁止'
    };
    const dynamicRule = {
      rule_core_next_hsi_partial_close: `${values.reached_target_label}到達時、${values.role}を${values.units}単位利確。残りは${values.next_target_label}を目標とし保有`,
      rule_h1_exit_confirmed_m5_full_close: 'H1決済トリガー確定後、M5で残り建玉を全決済',
      rule_single_close_next_hsi_target: `${values.reached_target_label}到達時に${values.units}単位を全決済`,
      rule_entry_hsi_anchor_stop_fixed: 'Entry時に使用したHSI起点をStopとして固定',
      rule_normal_close_miss_target_distance_ratio: 'Target距離×max_loss_to_reward_ratioでNormal StopをEntry時に固定',
      rule_normal_hsi_anchor_hard_limit: '倍率StopがHSI起点より遠い場合はHSI起点をHard Limitとして採用',
      rule_normal_pre_entry_dow_structure_break_expires_opportunity: 'Entry前の確定Dow崩壊でWAITING_R2 OpportunityとHSI起点を失効',
      rule_normal_h4_same_direction_r4_entry_guard: 'NORMALはH4現在波と同方向へR4以上進行後の新規Entryを禁止',
      rule_day_up_h4_down_r5_short_entry_guard: 'Day UpかつH4 Down R5以上で新規Short Entryを禁止',
      rule_single_position_single_close: '1 Entryにつき1 Position・1回の全Close',
      rule_normal_add_on_forbidden: '通常Entry中のAdd-onを禁止',
      rule_single_close_ambiguous_stop_first: '同一足でStopとTargetへ到達した場合は保守的にStopを優先'
    };
    return (kind === 'rule' ? dynamicRule[code] : dynamicReason[code]) || fallback;
  }

  function simulationCatalogRows(codes, catalog, kind, traceEvent) {
    const map = kind === 'rule' ? catalog?._rule_map : catalog?._reason_map;
    const unmapped = catalog?.display_policy?.unmapped_text || '日本語説明未登録。コードは保持し、カタログへ追加してください。';
    return normalizeStringArray(codes).map(code => {
      const fallback = map?.[code]?.ja || unmapped;
      return { code, ja: simulationDynamicJapaneseText(code, kind, traceEvent, fallback) };
    });
  }

  function simulationCatalogTableHtml(rows, emptyText = '該当なし') {
    if (!rows.length) return `<div class="gpt-fx-chart-comment-meta">${escapeHtml(emptyText)}</div>`;
    return `<div class="gpt-fx-chart-simulation-table-scroll"><table class="gpt-fx-chart-simulation-code-table"><thead><tr><th>日本語内容</th><th>コード</th></tr></thead><tbody>${rows.map(row => `<tr><td>${escapeHtml(row.ja)}</td><td>${escapeHtml(row.code)}</td></tr>`).join('')}</tbody></table></div>`;
  }

  function formatSimulationJpy(value, signed = false) {
    const number = numberOrNull(value);
    if (number == null) return '-';
    const rounded = Math.round(number);
    const prefix = signed && rounded > 0 ? '+' : '';
    return `${prefix}${rounded.toLocaleString('ja-JP')}円`;
  }

  function formatSimulationPct(value) {
    const number = numberOrNull(value);
    if (number == null) return '-';
    const prefix = number > 0 ? '+' : '';
    return `${prefix}${number.toFixed(1)}%`;
  }

  function formatSimulationR(value) {
    const number = numberOrNull(value);
    if (number == null) return '-';
    const prefix = number > 0 ? '+' : '';
    return `${prefix}${number.toFixed(2)}R`;
  }

  function simulationTradeEntryEvent(traceEvent, state) {
    const tradeId = String(traceEvent?.trade_id || '');
    const lane = String(traceEvent?.rule_lane || traceEvent?.execution?.rule_lane || '').toUpperCase();
    if (!tradeId) return null;
    return (state?.simulationTraceEvents || []).find(event => {
      const eventLane = String(event?.rule_lane || event?.execution?.rule_lane || '').toUpperCase();
      return String(event?.trade_id || '') === tradeId
        && (!lane || eventLane === lane)
        && ['entry', 'reentry'].includes(String(event?.event_type || '').toLowerCase());
    }) || null;
  }

  function simulationTradeStopAnnotation(entryEvent, state) {
    if (!entryEvent) return null;
    const eventId = String(entryEvent.event_id || '');
    return (state?.simulationHsiAnnotations || []).find(item => String(item?.usage_event_id || '') === eventId)
      || (state?.simulationHsiAnnotations || []).find(item => String(item?.anchor_id || '') === String(entryEvent?.execution?.entry_anchor_id || ''))
      || null;
  }

  function simulationFinancialMetrics(traceEvent, state) {
    const execution = traceEvent?.execution && typeof traceEvent.execution === 'object' ? traceEvent.execution : {};
    const profile = state?.simulationRunProfile?.m5_execution_policy?.valuation_policy || {};
    const unitAmount = Number(execution.unit_base_currency_amount || profile.unit_base_currency_amount || 1000);
    const entryEvent = simulationTradeEntryEvent(traceEvent, state) || (['entry', 'reentry'].includes(String(traceEvent?.event_type || '').toLowerCase()) ? traceEvent : null);
    const annotation = simulationTradeStopAnnotation(entryEvent, state);
    const entryPrice = numberOrNull(execution.entry_price ?? entryEvent?.execution?.price ?? entryEvent?.price);
    const stopPrice = numberOrNull(execution.stop_price ?? entryEvent?.execution?.stop_price ?? annotation?.price);
    const initialUnits = numberOrNull(execution.initial_units ?? entryEvent?.execution?.initial_units ?? entryEvent?.state_after?.portfolio?.open_units);
    const calculatedRisk = entryPrice == null || stopPrice == null || initialUnits == null ? null : Math.abs(entryPrice - stopPrice) * unitAmount * initialUnits;
    const initialRiskJpy = numberOrNull(execution.initial_risk_jpy ?? entryEvent?.execution?.initial_risk_jpy ?? calculatedRisk);
    const traceEvents = state?.simulationTraceEvents || [];
    const currentIndex = traceEvents.findIndex(item => item?.event_id === traceEvent?.event_id);
    const currentRunId = String(traceEvent?.run_id || '');
    const throughCurrent = traceEvents.filter((event, index) => {
      if (currentIndex >= 0 && index > currentIndex) return false;
      if (currentRunId && String(event?.run_id || '') && String(event?.run_id || '') !== currentRunId) return false;
      return true;
    });
    const traceLane = String(traceEvent?.rule_lane || traceEvent?.execution?.rule_lane || '').toUpperCase();
    const sameTradeEvents = throughCurrent.filter(event => {
      const eventLane = String(event?.rule_lane || event?.execution?.rule_lane || '').toUpperCase();
      return String(event?.trade_id || '') === String(traceEvent?.trade_id || '')
        && (!traceLane || eventLane === traceLane);
    });
    const eventRealizedJpy = event => {
      const explicit = numberOrNull(event?.execution?.realized_profit_jpy);
      if (explicit != null) return explicit;
      const delta = numberOrNull(event?.execution?.realized_price_delta_units);
      return delta == null ? 0 : delta * unitAmount;
    };
    const runCumulativeFallback = throughCurrent.reduce((sum, event) => sum + eventRealizedJpy(event), 0);
    const tradeCumulativeFallback = sameTradeEvents.reduce((sum, event) => sum + eventRealizedJpy(event), 0);
    const realizedProfitJpy = numberOrNull(execution.realized_profit_jpy ?? (numberOrNull(execution.realized_price_delta_units) == null ? null : Number(execution.realized_price_delta_units) * unitAmount));
    const cumulativeRealizedProfitJpy = runCumulativeFallback;
    const tradeCumulativeRealizedProfitJpy = numberOrNull(execution.trade_cumulative_realized_profit_jpy) ?? tradeCumulativeFallback;
    const ratio = initialRiskJpy && initialRiskJpy > 0 && tradeCumulativeRealizedProfitJpy != null ? tradeCumulativeRealizedProfitJpy / initialRiskJpy : null;
    const eventType = String(traceEvent?.event_type || '').toLowerCase();
    const stopBasis = String(execution.stop_basis || entryEvent?.execution?.stop_basis || 'HSI_ENTRY_ANCHOR');
    const stopText = stopBasis === 'HSI_ENTRY_ANCHOR' ? `HSI起点${stopPrice == null ? '' : ` ${round3(stopPrice)}`}` : `${stopBasis}${stopPrice == null ? '' : ` ${round3(stopPrice)}`}`;
    let closeText = '-';
    if (execution.reached_target_label) closeText = `${execution.reached_target_label}到達`;
    else if (eventType === 'partial_close' && execution.next_target_label) closeText = `${previousHsiLabel(execution.next_target_label) || 'HSI境界'}到達`;
    else if (execution.target_label) closeText = String(execution.target_label);
    else if (eventType === 'close') closeText = (traceEvent?.reason_codes || []).includes('H1_EXIT_TRIGGER_CONFIRMED') ? 'H1離脱確認' : '全決済';
    else if (eventType === 'stop_close') closeText = 'HSI起点割れ';
    if (execution.next_target_label) closeText += ` / 次 ${execution.next_target_label}`;
    return {
      stopText,
      closeText,
      entryPrice,
      stopPrice,
      initialUnits,
      unitAmount,
      initialRiskJpy,
      realizedProfitJpy,
      cumulativeRealizedProfitJpy,
      profitVsInitialRiskPct: numberOrNull(execution.profit_vs_initial_risk_pct) ?? (ratio == null ? null : ratio * 100),
      riskMultiple: numberOrNull(execution.risk_multiple) ?? ratio
    };
  }

  function simulationFinancialCardHtml(traceEvent, state) {
    const metrics = simulationFinancialMetrics(traceEvent, state);
    const realizedClass = numberOrNull(metrics.realizedProfitJpy) > 0 ? 'is-positive' : numberOrNull(metrics.realizedProfitJpy) < 0 ? 'is-negative' : '';
    const cumulativeClass = numberOrNull(metrics.cumulativeRealizedProfitJpy) > 0 ? 'is-positive' : numberOrNull(metrics.cumulativeRealizedProfitJpy) < 0 ? 'is-negative' : '';
    const ratioClass = numberOrNull(metrics.riskMultiple) > 0 ? 'is-positive' : numberOrNull(metrics.riskMultiple) < 0 ? 'is-negative' : '';
    return `<div class="gpt-fx-chart-simulation-risk-card">
      <div class="gpt-fx-chart-simulation-risk-main">
        <div class="gpt-fx-chart-simulation-risk-stop">STOP基準：${escapeHtml(metrics.stopText)}</div>
        <div class="gpt-fx-chart-simulation-risk-target">CLOSE目安：${escapeHtml(metrics.closeText)}</div>
      </div>
      <div class="gpt-fx-chart-simulation-risk-metrics">
        <div class="gpt-fx-chart-simulation-risk-metric"><div class="gpt-fx-chart-simulation-risk-metric-label">初期リスク</div><div class="gpt-fx-chart-simulation-risk-metric-value">${escapeHtml(formatSimulationJpy(metrics.initialRiskJpy))}</div></div>
        <div class="gpt-fx-chart-simulation-risk-metric"><div class="gpt-fx-chart-simulation-risk-metric-label">今回確定</div><div class="gpt-fx-chart-simulation-risk-metric-value ${realizedClass}">${escapeHtml(formatSimulationJpy(metrics.realizedProfitJpy, true))}</div></div>
        <div class="gpt-fx-chart-simulation-risk-metric"><div class="gpt-fx-chart-simulation-risk-metric-label">累積確定</div><div class="gpt-fx-chart-simulation-risk-metric-value ${cumulativeClass}">${escapeHtml(formatSimulationJpy(metrics.cumulativeRealizedProfitJpy, true))}</div></div>
        <div class="gpt-fx-chart-simulation-risk-metric"><div class="gpt-fx-chart-simulation-risk-metric-label">初期リスク比</div><div class="gpt-fx-chart-simulation-risk-metric-value ${ratioClass}">${escapeHtml(formatSimulationPct(metrics.profitVsInitialRiskPct))} / ${escapeHtml(formatSimulationR(metrics.riskMultiple))}</div></div>
      </div>
      <div class="gpt-fx-chart-simulation-risk-note">仮想損益：1単位=${Number(metrics.unitAmount || 1000).toLocaleString('ja-JP')}通貨。手数料・スリッページ・税は未反映。</div>
    </div>`;
  }

  function renderSimulationTracePopover(backdrop, state) {
    const popover = backdrop.querySelector('[data-role="simulation-trace-popover"]');
    if (!popover) return;
    const events = state.simulationTraceEvents || [];
    const traceEvent = events.find(x => x.event_id === state.openSimulationTraceId);
    const hit = (state.simulationTraceHitBoxes || []).find(x => x.id === state.openSimulationTraceId);
    if (!traceEvent || !hit || state.showSimulationComments === false) {
      popover.classList.remove('is-open');
      popover.innerHTML = '';
      return;
    }
    const body = backdrop.querySelector('[data-role="body"]');
    const runId = traceEvent.batch_run_id || traceEvent.run_id || state.simulationTrace?.run?.run_id || '-';
    const catalog = state.simulationReasonRuleCatalog || buildEmptySimulationReasonRuleCatalog();
    const judgment = simulationJapaneseJudgment(traceEvent, catalog);
    const reasonRows = simulationCatalogRows(traceEvent.reason_codes, catalog, 'reason', traceEvent);
    const ruleRows = simulationCatalogRows(traceEvent.rule_ids, catalog, 'rule', traceEvent);
    const causeIds = (traceEvent.cause_event_ids || []).join(', ') || '-';
    popover.innerHTML = `
      <button class="gpt-fx-chart-simulation-popover-close" type="button" data-simulation-action="close" title="判断画面を閉じる" aria-label="判断画面を閉じる">×</button>
      <div class="gpt-fx-chart-simulation-title">シミュレーション判断 / ${escapeHtml(traceReplayEventTypeLabelForEvent(traceEvent))}</div>
      <div class="gpt-fx-chart-comment-meta">${escapeHtml(traceEvent.timeframe || traceEvent.panel || '-')} / ${escapeHtml(traceEvent.simulation_time || traceEvent.time || '-')} / ${round3(traceEvent.price)} / run=${escapeHtml(runId)}</div>
      <div class="gpt-fx-chart-comment-text">${escapeHtml(traceEvent.summary || '（summaryなし）')}</div>
      <div class="gpt-fx-chart-simulation-judgment">
        <div class="gpt-fx-chart-simulation-judgment-title">${escapeHtml(judgment.title)}</div>
        <div class="gpt-fx-chart-simulation-judgment-body">${escapeHtml(judgment.body)}</div>
      </div>
      ${simulationFinancialCardHtml(traceEvent, state)}
      <div class="gpt-fx-chart-simulation-section">
        <div class="gpt-fx-chart-simulation-section-title">判断理由（日本語 / コード）</div>
        ${simulationCatalogTableHtml(reasonRows, '理由コードなし')}
      </div>
      <div class="gpt-fx-chart-simulation-section">
        <div class="gpt-fx-chart-simulation-section-title">使用ルール（日本語 / コード）</div>
        ${simulationCatalogTableHtml(ruleRows, '使用ルールなし')}
        <div class="gpt-fx-chart-comment-meta" style="margin-top:5px">原因Event: ${escapeHtml(causeIds)}<br>日本語カタログ: ${escapeHtml(state.simulationReasonRuleCatalogLoadStatus || 'loading')}</div>
      </div>
      <div class="gpt-fx-chart-simulation-section">
        <div class="gpt-fx-chart-simulation-section-title">上位足状態の要約</div>
        <pre class="gpt-fx-chart-simulation-code">${escapeHtml(simulationStateBlock(traceEvent.upper_state_summary))}</pre>
      </div>
      <div class="gpt-fx-chart-simulation-section">
        <div class="gpt-fx-chart-simulation-section-title">変更前</div>
        <pre class="gpt-fx-chart-simulation-code">${escapeHtml(simulationStateBlock(traceEvent.state_before))}</pre>
      </div>
      <div class="gpt-fx-chart-simulation-section">
        <div class="gpt-fx-chart-simulation-section-title">変更後</div>
        <pre class="gpt-fx-chart-simulation-code">${escapeHtml(simulationStateBlock(traceEvent.state_after))}</pre>
      </div>
      <div class="gpt-fx-chart-comment-buttons">
        ${state.simulationRunSnapshot?.trace_replay?.event_index?.[traceEvent.event_id] ? '<button class="gpt-fx-chart-comment-mini-btn" type="button" data-simulation-action="trace-replay">判断履歴で追う</button>' : ''}
        <button class="gpt-fx-chart-comment-mini-btn" type="button" data-simulation-action="close">閉じる</button>
      </div>`;
    placeSimulationTracePopover(popover, body, hit);
    popover.querySelector('[data-simulation-action="trace-replay"]')?.addEventListener('click', () => {
      const sequence = state.simulationRunSnapshot?.trace_replay?.event_index?.[traceEvent.event_id]?.sequence;
      state.simulationTraceReplaySequence = numberOrNull(sequence) ?? state.simulationRunSnapshot?.trace_replay?.events?.length ?? 0;
      state.simulationTraceReplayFocusEventId = traceEvent.event_id;
      state.simulationRunDialogOpen = true;
      renderSimulationRunDialog(backdrop, state);
      applyModeButtonState(backdrop, state);
    });
    popover.querySelectorAll('[data-simulation-action="close"]').forEach(button => button.addEventListener('click', () => {
      traceEvent.display = { ...(traceEvent.display || {}), open: false };
      state.openSimulationTraceId = null;
      state.redraw?.();
    }));
  }

  function renderCommentPopover(backdrop, state) {
    const popover = backdrop.querySelector('[data-role="comment-popover"]');
    if (!popover) return;
    const comments = state.comments || [];
    const comment = comments.find(x => x.id === state.openCommentId);
    const hit = (state.commentHitBoxes || []).find(x => x.id === state.openCommentId);
    if (!comment || !hit || state.showUserComments === false) {
      popover.classList.remove('is-open');
      popover.innerHTML = '';
      return;
    }
    const body = backdrop.querySelector('[data-role="body"]');
    const bodyRect = body.getBoundingClientRect();
    const x = Math.max(10, Math.min(bodyRect.width - 250, hit.x + 18));
    // 画面上部のメニュー/メタ領域にコメントエディターがかぶる場合は、
    // 従来の「点の上」配置ではなく「点の下」へ逃がす。
    const shouldPlaceBelow = hit.y < 190;
    const y = shouldPlaceBelow
      ? Math.max(8, Math.min(bodyRect.height - 120, hit.y + 8))
      : Math.max(56, Math.min(bodyRect.height - 12, hit.y - 12));
    popover.style.left = `${x}px`;
    popover.style.top = `${y}px`;
    popover.classList.toggle('is-below', shouldPlaceBelow);
    popover.classList.add('is-open');

    // コメントアイコンを開いた時は、閲覧専用Popoverを挟まず直接編集する。
    comment.display = { ...(comment.display || {}), open: true, editing: true };
    const editing = true;
    if (editing) {
      const options = COMMENT_TYPE_OPTIONS;
      state.commentEditDrafts = state.commentEditDrafts || {};
      const normalizeCommentTypeValue = value => {
        const raw = String(value || 'note');
        return normalizeCommentType(raw);
      };
      const draft = state.commentEditDrafts[comment.id] || {
        comment_type: normalizeCommentTypeValue(comment.comment_type),
        text: comment.text || '',
        tagsText: (comment.tags || []).join(', ')
      };
      draft.comment_type = normalizeCommentTypeValue(draft.comment_type);
      state.commentEditDrafts[comment.id] = draft;
      popover.innerHTML = `
        <div class="gpt-fx-chart-comment-form">
          <select class="gpt-fx-chart-comment-select" data-role="comment-type">
            ${options.map(opt => `<option value="${escapeHtml(opt)}" ${opt === draft.comment_type ? 'selected' : ''}>${escapeHtml(commentTypeLabel(opt))}</option>`).join('')}
          </select>
          <textarea class="gpt-fx-chart-comment-textarea" data-role="comment-text" placeholder="コメント本文">${escapeHtml(draft.text || '')}</textarea>
          <input class="gpt-fx-chart-comment-input" data-role="comment-tags" value="${escapeHtml(draft.tagsText || '')}" placeholder="tags: HSI_R2, T3_exit など">
          <div class="gpt-fx-chart-comment-meta">${escapeHtml(comment.panel)} / ${escapeHtml(comment.time)} / ${round3(comment.price)}</div>
          <div class="gpt-fx-chart-comment-buttons">
            <button class="gpt-fx-chart-comment-mini-btn is-danger" type="button" data-comment-action="delete">削除</button>
            <button class="gpt-fx-chart-comment-mini-btn" type="button" data-comment-action="cancel">閉じる</button>
            <button class="gpt-fx-chart-comment-mini-btn" type="button" data-comment-action="save">保存</button>
          </div>
        </div>`;
      const typeSelect = popover.querySelector('[data-role="comment-type"]');
      const textArea = popover.querySelector('[data-role="comment-text"]');
      const tagsInput = popover.querySelector('[data-role="comment-tags"]');
      typeSelect?.addEventListener('change', () => {
        draft.comment_type = normalizeCommentTypeValue(typeSelect.value);
        typeSelect.value = draft.comment_type;
      });
      textArea?.addEventListener('input', () => { draft.text = textArea.value || ''; });
      tagsInput?.addEventListener('input', () => { draft.tagsText = tagsInput.value || ''; });
      popover.querySelector('[data-comment-action="save"]')?.addEventListener('click', async () => {
        draft.comment_type = normalizeCommentTypeValue(typeSelect?.value ?? draft.comment_type);
        draft.text = textArea?.value ?? draft.text ?? '';
        draft.tagsText = tagsInput?.value ?? draft.tagsText ?? '';
        comment.comment_type = draft.comment_type;
        comment.title = '';
        comment.text = draft.text || '';
        comment.tags = String(draft.tagsText || '').split(/[，,\s]+/).filter(Boolean);
        comment.updated_at = nowLocalIso();
        delete comment.is_draft;
        comment.display = { ...(comment.display || {}), open: false, editing: false };
        delete state.commentEditDrafts?.[comment.id];
        state.openCommentId = null;
        await state.requestCommentSave?.();
        state.redraw?.();
      });
      popover.querySelector('[data-comment-action="cancel"]')?.addEventListener('click', () => {
        delete state.commentEditDrafts?.[comment.id];
        if (!comment.text && !comment.title && comment.is_draft) {
          state.comments = state.comments.filter(x => x.id !== comment.id);
          if (state.commentSidecar) state.commentSidecar.comments = state.comments;
        } else {
          comment.display = { ...(comment.display || {}), open: false, editing: false };
        }
        state.openCommentId = null;
        state.redraw?.();
      });
      popover.querySelector('[data-comment-action="delete"]')?.addEventListener('click', async () => {
        const ok = await showFxChartConfirmDialog({
          title: 'このコメントを削除しますか？',
          message: 'FXチャート上のコメントを削除します。',
          detail: buildCommentDeleteDialogDetail(comment),
          okText: '削除する',
          cancelText: 'キャンセル',
          danger: true
        });
        if (!ok) return;
        delete state.commentEditDrafts?.[comment.id];
        state.comments = state.comments.filter(x => x.id !== comment.id);
        if (state.commentSidecar) state.commentSidecar.comments = state.comments;
        state.openCommentId = null;
        await state.requestCommentSave?.();
        state.redraw?.();
      });
      return;
    }

    popover.innerHTML = `
      <div class="gpt-fx-chart-comment-title">${escapeHtml(commentTypeLabel(comment.comment_type || 'note'))}</div>
      <div class="gpt-fx-chart-comment-meta">${escapeHtml(comment.panel)} / ${escapeHtml(comment.time)} / ${round3(comment.price)}</div>
      <div class="gpt-fx-chart-comment-text">${escapeHtml(comment.text || '（コメント本文なし）')}</div>
      <div class="gpt-fx-chart-comment-meta">tags: ${escapeHtml((comment.tags || []).join(', ') || '-')}</div>
      <div class="gpt-fx-chart-comment-buttons">
        <button class="gpt-fx-chart-comment-mini-btn" type="button" data-comment-action="edit">編集</button>
        <button class="gpt-fx-chart-comment-mini-btn" type="button" data-comment-action="close">閉じる</button>
      </div>`;
    popover.querySelector('[data-comment-action="edit"]')?.addEventListener('click', () => {
      comment.display = { ...(comment.display || {}), editing: true, open: true };
      state.redraw?.();
    });
    popover.querySelector('[data-comment-action="close"]')?.addEventListener('click', async () => {
      comment.display = { ...(comment.display || {}), open: false, editing: false };
      state.openCommentId = null;
      await state.requestCommentSave?.();
      state.redraw?.();
    });
  }

  function validJsonParam(value) {
    const text = String(value ?? '').trim().replace(/\\/g, '/');
    if (!text || !text.toLowerCase().endsWith('.json')) return '';
    if (text.includes('://') || text.startsWith('/') || text.includes('?') || text.includes('#')) return '';
    return text;
  }

  function currentJsonParam(inputId, fallback) {
    const value = typeof document !== 'undefined' && typeof document.getElementById === 'function'
      ? document.getElementById(inputId)?.value
      : '';
    return validJsonParam(value) || fallback;
  }


  function normalizeUpperMapDataPath(value, fallback = DEFAULT_UPPER_MAP_DATA) {
    return validJsonParam(value) || fallback;
  }

  function defaultUpperMapDataPath() {
    const displayPolicy = pluginManifest?.display_policy || {};
    const dayRaw = displayPolicy.day_upper_map_settings || displayPolicy.day_upper_map || {};
    const chartViewerRaw = pluginManifest?.chart_viewer_policy?.day_upper_map || {};
    const policy = pluginChartPolicy();
    return normalizeUpperMapDataPath(
      dayRaw.default_data_path
      ?? dayRaw.defaultDataPath
      ?? dayRaw.data_path
      ?? dayRaw.dataPath
      ?? chartViewerRaw.default_data_path
      ?? chartViewerRaw.defaultDataPath
      ?? policy.day_upper_map_default_data_path
      ?? policy.upper_map_default_data_path
      ?? DEFAULT_UPPER_MAP_DATA,
      DEFAULT_UPPER_MAP_DATA
    );
  }

  function overlayDataFetchPaths(dataPath) {
    const clean = normalizeUpperMapDataPath(dataPath);
    let rel = clean.replace(/\\/g, '/').replace(/^\/+/, '');
    rel = rel.replace(/^overlay\//, '').replace(/^studio_overlays\//, '');
    if (rel.startsWith('gpt_fx_lab/')) {
      // already overlay-relative
    } else if (rel.startsWith('data/')) {
      rel = `gpt_fx_lab/${rel}`;
    } else if (!rel.includes('/')) {
      rel = `gpt_fx_lab/data/${rel}`;
    }
    return {
      dataPath: clean,
      relativePath: rel,
      apiPath: `/api/overlays/${rel}`,
      staticPath: rel.startsWith('gpt_fx_lab/') ? `studio_overlays/${rel}` : clean
    };
  }

  async function loadUpperMapDataSource(dataPath) {
    const paths = overlayDataFetchPaths(dataPath);
    try {
      const source = await fetchJsonIfExists(paths.apiPath);
      return { source, paths, from: 'api' };
    } catch (apiErr) {
      try {
        const source = await fetchJsonIfExists(paths.staticPath);
        return { source, paths, from: 'static' };
      } catch (staticErr) {
        throw apiErr || staticErr;
      }
    }
  }

  function normalizeRowsForTimeframeSource(source, timeframe = 'DAY') {
    const tf = normalizePanelTimeframe(timeframe, 'DAY');
    const bucketMs = panelTimeframeMinutes(tf) * 60 * 1000;
    const rows = normalizeAllRows(source).map((row, index) => {
      const copy = { ...row };
      const startMs = numberOrNull(copy.start_ms) ?? rowTimeMs(copy);
      if (startMs != null) {
        copy.start_ms = startMs;
        copy.end_ms = numberOrNull(copy.end_ms) ?? (startMs + bucketMs - 1);
      }
      copy.index = index;
      copy.row_no = Math.max(1, Math.floor(numberOrNull(copy.row_no) ?? (index + 1)));
      copy.timeframe = copy.timeframe || tf;
      if (numberOrNull(copy.range) == null && numberOrNull(copy.high) != null && numberOrNull(copy.low) != null) {
        copy.range = numberOrNull(copy.high) - numberOrNull(copy.low);
      }
      if (numberOrNull(copy.body) == null && numberOrNull(copy.open) != null && numberOrNull(copy.close) != null) {
        copy.body = numberOrNull(copy.close) - numberOrNull(copy.open);
      }
      if (!copy.direction && numberOrNull(copy.body) != null) {
        copy.direction = copy.body >= 0 ? 'up' : 'down';
      }
      return copy;
    });
    const hasMa20 = rows.some(row => numberOrNull(row.ma20) != null);
    const hasT3 = rows.some(row => numberOrNull(row.t3_20_0_2) != null);
    return hasMa20 && hasT3 ? rows : enrichDerivedIndicators(rows);
  }

  function upperMapWindowSize(source) {
    const chartRaw = source?.chart_viewer_settings || source?.gpt_fx_lab_settings?.chart_viewer || {};
    const raw = chartRaw.upper_map_window_size
      ?? chartRaw.day_window_size
      ?? source?.display_sets?.chart_latest_1000?.length
      ?? 1000;
    return Math.max(120, Math.min(1500, Math.floor(numberOrNull(raw) ?? 1000)));
  }

  function referenceTimeForPanelWindow(baseRows, state) {
    const synced = numberOrNull(state?.syncCenterTimeMs);
    if (synced != null) return synced;
    if (!baseRows?.length) return null;
    const mid = baseRows[Math.floor(baseRows.length / 2)];
    return panelRowTimeMs(mid) ?? rowTimeMs(baseRows[baseRows.length - 1]);
  }

  function nearestIndexForTime(rows, timeMs) {
    if (!rows?.length) return null;
    const n = numberOrNull(timeMs);
    if (n == null) return rows.length - 1;
    let bestIndex = 0;
    let bestDistance = Infinity;
    rows.forEach((row, index) => {
      const start = numberOrNull(row.start_ms) ?? rowTimeMs(row);
      const end = numberOrNull(row.end_ms) ?? start;
      if (start != null && end != null && n >= start && n <= end) {
        bestIndex = index;
        bestDistance = -1;
        return;
      }
      const base = start ?? rowTimeMs(row);
      if (base == null) return;
      const distance = Math.abs(base - n);
      if (distance < bestDistance) {
        bestDistance = distance;
        bestIndex = index;
      }
    });
    return bestDistance === Infinity ? null : bestIndex;
  }

  function sliceRowsAroundTime(sourceRows, timeMs, count) {
    if (!sourceRows?.length) return [];
    const safeCount = Math.max(1, Math.min(sourceRows.length, Math.floor(numberOrNull(count) ?? sourceRows.length)));
    const centerIndex = findIndexForTime(sourceRows, timeMs) ?? nearestIndexForTime(sourceRows, timeMs);
    const start = centerIndex == null
      ? Math.max(0, sourceRows.length - safeCount)
      : clampWindowStart(centerIndex - Math.floor(safeCount / 2), safeCount, sourceRows.length);
    return sourceRows.slice(start, start + safeCount);
  }

  function isFxChartUrlAction(value) {
    const v = String(value ?? '').trim().toLowerCase();
    return URL_ACTION_ALIASES.includes(v);
  }

  async function fetchDefaultUrlLaunchSource() {
    if (defaultUrlLaunchSourcePromise) return defaultUrlLaunchSourcePromise;
    defaultUrlLaunchSourcePromise = (async () => {
      const apiUrl = '/api/overlays/gpt_fx_lab/data/fx_usdjpy_m5_t3_data_v0_1.json';
      const staticUrl = 'studio_overlays/gpt_fx_lab/data/fx_usdjpy_m5_t3_data_v0_1.json';
      try {
        return await fetchJson(apiUrl);
      } catch (apiErr) {
        try {
          return await fetchJson(staticUrl);
        } catch {
          throw apiErr;
        }
      }
    })();
    return defaultUrlLaunchSourcePromise;
  }

  function sourceLooksChartReady(source) {
    return Boolean(source && typeof source === 'object' && normalizeAllRows(source).length);
  }

  async function sourceForUrlLaunch(studio, params, attempt) {
    const source = studio?.getSourceData?.() || window.sourceData;
    if (sourceLooksChartReady(source)) return source;

    // data/view付きURLではStudio本体のautoLoadFromQueryを待つ。
    // 旧URLのように data が無い場合だけ、FX Lab既定データをPlugin側で保険ロードする。
    const hasDataParam = Boolean(params?.get?.('data'));
    if (hasDataParam && attempt < 40) return null;
    return await fetchDefaultUrlLaunchSource();
  }

  function scheduleAutoOpenFromUrl(studio) {
    let params = null;
    try {
      params = new URLSearchParams(location.search);
    } catch {
      return;
    }
    if (!isFxChartUrlAction(params.get('action'))) return;
    if (window.__gptFxLabUrlChartOpened) return;
    window.__gptFxLabUrlChartOpened = true;

    let attempt = 0;
    const maxAttempts = 60;
    const run = async () => {
      attempt += 1;
      try {
        const source = await sourceForUrlLaunch(studio, params, attempt);
        if (!source) {
          if (attempt < maxAttempts) setTimeout(run, 250);
          return;
        }
        showFxChart(source, chartOptionsFromParams(params));
      } catch (err) {
        console.error('[GPT FX Lab] URL chart launch failed', err);
        if (typeof window.setStatus === 'function') {
          window.setStatus('FXチャートURL起動エラー: ' + (err?.message || String(err)), { kind: 'error', title: 'GPT FX Lab' });
        }
      }
    };
    setTimeout(run, 300);
  }

  function buildChartStateUrl(state) {
    const url = new URL(location.href);
    // URL単体で再現できるように、チャート状態だけでなくData/ViewDefも明示する。
    url.searchParams.set('data', url.searchParams.get('data') || currentJsonParam('dataNameInput', DEFAULT_URL_DATA));
    url.searchParams.set('view', url.searchParams.get('view') || url.searchParams.get('def') || currentJsonParam('defNameInput', DEFAULT_URL_VIEW));
    url.searchParams.set('action', 'fx_chart');
    url.searchParams.set('confirmBars', String(Math.max(3, Math.floor(numberOrNull(state?.confirmBars) ?? 10))));
    url.searchParams.set('viewMode', String(state?.viewMode || 'all'));
    url.searchParams.set('hlRange', state?.showHighLowRange === false ? '0' : '1');
    url.searchParams.set('bb', state?.showBollinger === true ? '1' : '0');
    url.searchParams.set('wide', state?.widthMultiplier > 1 ? '1' : '0');
    url.searchParams.set('windowSize', String(Math.max(10, Math.floor(numberOrNull(state?.windowSize) ?? 1000))));
    url.searchParams.set('chartLayout', normalizeChartLayout(state?.chartLayout));
    const windowStart = numberOrNull(state?.windowStart);
    if (windowStart != null) {
      url.searchParams.set('windowStart', String(Math.max(0, Math.floor(windowStart))));
    }
    url.searchParams.set('upperTf', normalizeUpperDisplayMode(state?.upperTimeframe));
    url.searchParams.set('upperConfirmBars', String(Math.max(3, Math.floor(numberOrNull(state?.upperConfirmBars) ?? 7))));
    url.searchParams.set('upperWarmupBars', String(normalizeUpperWarmupBars(state?.upperWarmupBars, 30)));
    url.searchParams.set('dayData', normalizeUpperMapDataPath(state?.upperMapDataPath || defaultUpperMapDataPath()));
    url.searchParams.set('dayConfirmBars', String(Math.max(3, Math.floor(numberOrNull(state?.dayConfirmBars) ?? 7))));
    // HSI / コメント / サイクル縦線は chart_comments.json を正本にする。
    // URLコピーでは未保存HSIドラフト用の旧パラメータを出力しない。
    [
      'hsi', 'hsiValues', 'hsi_values',
      'hsiScale', 'hsi_scale',
      'hsiDir', 'hsiDirection', 'hsi_direction',
      'hsiAnchorPrice', 'hsi_anchor_price',
      'hsiAnchorIndex', 'hsi_anchor_index',
      'hsiAnchorPanel', 'hsi_anchor_panel'
    ].forEach(name => url.searchParams.delete(name));
    return url.toString();
  }

  async function copyTextToClipboard(text) {
    if (navigator.clipboard?.writeText && window.isSecureContext) {
      await navigator.clipboard.writeText(text);
      return true;
    }
    const textarea = document.createElement('textarea');
    textarea.value = text;
    textarea.setAttribute('readonly', 'readonly');
    textarea.style.position = 'fixed';
    textarea.style.left = '-9999px';
    textarea.style.top = '0';
    document.body.appendChild(textarea);
    textarea.select();
    try {
      document.execCommand('copy');
      return true;
    } finally {
      textarea.remove();
    }
  }

  function getDowBasisPointSettings(source, overrideConfirmBars) {
    const raw = source?.dow_basis_point_settings || source?.strategy_settings?.dow_basis_points || {};
    const base = overrideConfirmBars ?? getConfirmBarsDefault(source);
    const confirmBars = Math.max(3, Math.floor(numberOrNull(base) ?? getConfirmBarsDefault(source)));
    return {
      method: raw.method || 'no_lookahead_center_window_extreme_locked_points',
      confirm_bars: confirmBars,
      no_lookahead: true,
      price_source: raw.price_source || 'high_low_window_extreme',
      threshold_enabled: false,
      lock_policy: 'basis points may be replaced later, but replaced points remain visible as history when requested.',
      threshold_note: 'Fib/point thresholds are reserved for later entry simulation and are not used for current basis point extraction.'
    };
  }

  function rowHigh(row) { return numberOrNull(row?.high); }
  function rowLow(row) { return numberOrNull(row?.low); }

  function pointPriceSource(type) {
    return type === 'swing_high' ? 'high' : 'low';
  }

  function pluginChartPolicy() {
    return pluginManifest?.chart_viewer_policy || pluginManifest?.signal_policy || {};
  }

  function pluginManualHsiDefaults() {
    return pluginManifest?.display_policy?.manual_hsi_lines
      || pluginManifest?.chart_viewer_policy?.manual_hsi_lines
      || pluginManifest?.signal_policy?.manual_hsi_lines
      || {};
  }

  function sourceManualHsiDefaults(source) {
    return source?.hsi_settings?.manual_lines
      || source?.hsi_settings
      || source?.strategy_settings?.hsi
      || source?.chart_viewer_settings?.manual_hsi_lines
      || {};
  }

  function getManualHsiSettings(source) {
    const pluginRaw = pluginManualHsiDefaults();
    const sourceRaw = sourceManualHsiDefaults(source);
    const values = sourceRaw.default_values ?? sourceRaw.values ?? sourceRaw.hsi_values
      ?? pluginRaw.default_values ?? pluginRaw.values ?? pluginRaw.hsi_values
      ?? '55,89,144,188,233,305,377,493,610,798,987';
    const scale = numberOrNull(sourceRaw.default_scale ?? sourceRaw.scale ?? pluginRaw.default_scale ?? pluginRaw.scale) ?? 1;
    const scaleStep = numberOrNull(sourceRaw.scale_step ?? sourceRaw.step ?? pluginRaw.scale_step ?? pluginRaw.step) ?? 1;
    const direction = sourceRaw.default_direction ?? sourceRaw.direction ?? pluginRaw.default_direction ?? pluginRaw.direction ?? 'up';
    return {
      valuesText: String(values),
      scale,
      scaleStep,
      direction: normalizeHsiDirection(direction)
    };
  }

  function getConfirmBarsDefault(source) {
    const raw = source?.dow_basis_point_settings || source?.strategy_settings?.dow_basis_points || {};
    const chartRaw = source?.chart_viewer_settings || source?.gpt_fx_lab_settings?.chart_viewer || {};
    const policy = pluginChartPolicy();
    return Math.max(3, Math.floor(numberOrNull(
      raw.confirm_bars_default
      ?? chartRaw.confirm_bars_default
      ?? policy.confirm_bars_default
      ?? raw.confirm_bars
      ?? raw.confirmation_bars
      ?? 20
    ) ?? 20));
  }

  function getWindowSettings(source) {
    const chartRaw = source?.chart_viewer_settings || source?.gpt_fx_lab_settings?.chart_viewer || {};
    const policy = pluginChartPolicy();
    const windowRaw = chartRaw.window || policy.window || {};
    const defaultSize = Math.max(50, Math.floor(numberOrNull(
      chartRaw.window_size
      ?? chartRaw.default_window_size
      ?? windowRaw.default_size
      ?? windowRaw.window_size
      ?? policy.window_size
      ?? policy.default_window_size
      ?? 1000
    ) ?? 1000));
    const minSize = Math.max(10, Math.floor(numberOrNull(windowRaw.min_size ?? 100) ?? 100));
    return { default_size: defaultSize, min_size: minSize };
  }

  function clampWindowStart(start, size, total) {
    const maxStart = Math.max(0, total - size);
    const n = Math.floor(numberOrNull(start) ?? maxStart);
    return Math.max(0, Math.min(maxStart, n));
  }

  function getChartWindowRows(source, allRows, state) {
    const settings = getWindowSettings(source);
    const total = allRows.length;
    const size = Math.max(settings.min_size, Math.floor(numberOrNull(state.windowSize) ?? settings.default_size));
    const safeSize = total > 0 ? Math.min(total, size) : size;
    const start = state.windowStart == null
      ? Math.max(0, total - safeSize)
      : clampWindowStart(state.windowStart, safeSize, total);
    state.windowSize = safeSize;
    state.windowStart = start;
    state.windowEndExclusive = Math.min(total, start + safeSize);
    return allRows.slice(start, state.windowEndExclusive);
  }

  function getUpperTimeframeSettings(source) {
    const chartRaw = source?.chart_viewer_settings || source?.gpt_fx_lab_settings?.chart_viewer || {};
    const policy = pluginChartPolicy();
    const upperRaw = chartRaw.upper_timeframe || policy.upper_timeframe || {};
    return {
      default_timeframe: normalizeUpperTimeframe(upperRaw.default_timeframe ?? upperRaw.timeframe ?? policy.upper_timeframe_default ?? 'H1'),
      confirm_bars: Math.max(3, Math.floor(numberOrNull(upperRaw.confirm_bars_default ?? upperRaw.confirm_bars ?? policy.upper_confirm_bars_default ?? 7) ?? 7)),
      warmup_bars: normalizeUpperWarmupBars(
        upperRaw.warmup_bars_default
        ?? upperRaw.warmup_bars
        ?? upperRaw.context_bars_before
        ?? policy.upper_warmup_bars_default
        ?? policy.upper_context_bars_before
        ?? 30,
        30
      )
    };
  }


  function getDayUpperMapSettings(primarySource, upperMapSource) {
    // DAY UpperMapのConfirm bars/marker設定は plugin.json display_policy.day_upper_map_settings を正本にする。
    // chart_layout はレイアウト説明、signal_policy は機能宣言。設定値の正本としては読まない。
    // D1 Data JSONは差し替え可能な相場データなので、UI/判定補助設定を持たせない。
    const displayPolicy = pluginManifest?.display_policy || {};
    const dayDisplayRaw = displayPolicy.day_upper_map_settings || displayPolicy.day_upper_map || {};
    const chartViewerRaw = pluginManifest?.chart_viewer_policy?.day_upper_map || {};
    const policy = pluginChartPolicy();
    const confirmBars = Math.max(3, Math.floor(numberOrNull(
      dayDisplayRaw.confirm_bars_default
      ?? dayDisplayRaw.confirm_bars
      ?? chartViewerRaw.confirm_bars_default
      ?? chartViewerRaw.confirm_bars
      ?? policy.day_upper_map_confirm_bars_default
      ?? policy.day_upper_map_confirm_bars
      ?? 7
    ) ?? 7));
    return {
      confirm_bars: confirmBars,
      point_marker_mode: String(
        dayDisplayRaw.point_marker_mode
        ?? chartViewerRaw.point_marker_mode
        ?? policy.day_upper_map_point_marker_mode
        ?? 'active_basis_only'
      ),
      show_confirm_stride_lines: boolFromParam(
        dayDisplayRaw.show_confirm_stride_lines
        ?? dayDisplayRaw.confirm_stride_lines_visible
        ?? chartViewerRaw.show_confirm_stride_lines
        ?? chartViewerRaw.confirm_stride_lines_visible
        ?? true,
        true
      )
    };
  }

  function getWeekContextSettings() {
    const displayPolicy = pluginManifest?.display_policy || {};
    const raw = displayPolicy.week_context_settings || displayPolicy.week_context || {};
    return {
      confirm_bars: Math.max(3, Math.floor(numberOrNull(raw.confirm_bars_default ?? raw.confirm_bars ?? 15) ?? 15)),
      point_marker_mode: String(raw.point_marker_mode ?? 'active_basis_only'),
      window_mode: String(raw.window_mode ?? 'all_history').trim().toLowerCase() || 'all_history',
      window_bars: Math.max(20, Math.floor(numberOrNull(raw.window_bars_default ?? raw.window_bars ?? 260) ?? 260)),
      show_saved_vertical_markers: boolFromParam(raw.show_saved_vertical_markers, false),
      show_cycle_vertical_markers: boolFromParam(raw.show_cycle_vertical_markers, false)
    };
  }

  function getChartLayoutSettings(source) {
    const chartRaw = source?.chart_viewer_settings || source?.gpt_fx_lab_settings?.chart_viewer || {};
    const policy = pluginChartPolicy();
    const displayPolicy = pluginManifest?.display_policy || {};
    const layoutRaw = chartRaw.chart_layout || chartRaw.layout || displayPolicy.chart_layout || policy.chart_layout || {};
    return {
      default_layout: normalizeChartLayout(
        chartRaw.chart_layout_default
        ?? chartRaw.default_layout
        ?? layoutRaw.default_layout
        ?? layoutRaw.default
        ?? displayPolicy.chart_layout_default
        ?? policy.chart_layout_default
        ?? 'EXPANSION_REVIEW'
      )
    };
  }

  function stableSwingToken(value) {
    return String(value ?? '').trim().replace(/[^0-9A-Za-z_-]+/g, '_').replace(/^_+|_+$/g, '') || 'unknown';
  }

  function swingPointStableId(timeframe, type, row, confirmBars) {
    const tf = normalizePanelTimeframe(timeframe, String(timeframe || 'M5').toUpperCase());
    const startMs = numberOrNull(row?.start_ms) ?? rowTimeMs(row) ?? row?.datetime ?? row?.time ?? 'unknown';
    const side = type === 'swing_high' ? 'high' : 'low';
    return `swing_${tf.toLowerCase()}_${side}_${stableSwingToken(startMs)}_cb${confirmBars}`;
  }

  function buildPendingSwingCandidates(rows, timeframe, confirmBars, sourceRole = '') {
    const list = rows || [];
    if (!list.length || confirmBars < 3) return [];
    const candidateOffset = Math.max(1, Math.min(confirmBars - 2, Math.floor((confirmBars - 1) / 2)));
    const rightBars = confirmBars - candidateOffset - 1;
    if (rightBars <= 0) return [];
    const firstCandidateIndex = Math.max(candidateOffset, list.length - rightBars);
    const pending = [];
    const seen = new Set();
    for (let candidateIndex = firstCandidateIndex; candidateIndex < list.length; candidateIndex++) {
      const leftStart = candidateIndex - candidateOffset;
      if (leftStart < 0) continue;
      const observedWindow = list.slice(leftStart);
      const candidate = list[candidateIndex] || {};
      const candidateHigh = rowHigh(candidate);
      const candidateLow = rowLow(candidate);
      const remainingBars = Math.max(1, candidateIndex + rightBars - (list.length - 1));
      const add = (type, price, mode) => {
        if (!isUniqueExtreme(observedWindow.map(mode === 'high' ? rowHigh : rowLow), price, mode)) return;
        const pointId = swingPointStableId(timeframe, type, candidate, confirmBars);
        const key = `${type}:${candidateIndex}`;
        if (seen.has(key)) return;
        seen.add(key);
        pending.push({
          key,
          point_id: pointId,
          index: candidateIndex,
          source_index: Math.max(0, Math.floor(numberOrNull(candidate.index) ?? candidateIndex)),
          type,
          pivot_time: candidate.datetime || candidate.time || '',
          pivot_ms: numberOrNull(candidate.start_ms) ?? rowTimeMs(candidate),
          pivot_price: price,
          price_source: pointPriceSource(type),
          confirm_bars: confirmBars,
          candidate_offset: candidateOffset,
          confirmation_remaining_bars: remainingBars,
          lifecycle_status: 'candidate',
          basis_role: 'candidate_pending',
          usable_as_basis: false,
          source_role: sourceRole,
          no_lookahead: true,
          rule: `left-side unique ${mode}; waiting ${remainingBars} bar(s) for full confirmation window`
        });
      };
      add('swing_high', candidateHigh, 'high');
      add('swing_low', candidateLow, 'low');
    }
    return pending.sort((a, b) => a.index - b.index || (a.type === 'swing_high' ? -1 : 1));
  }

  function sharedSwingPointEventId(point, transition) {
    return `swing_evt_${stableSwingToken(point?.point_id || point?.key)}_${stableSwingToken(transition)}`;
  }

  function buildSwingObservationEvents(timeframe, pendingCandidates, layers) {
    const tf = normalizePanelTimeframe(timeframe, String(timeframe || 'M5').toUpperCase());
    const events = [];
    const activeByType = {};
    (layers?.activeBasis || []).forEach(point => { activeByType[point.type] = point; });
    const visiblePointIds = new Set(Object.values(activeByType).map(point => point?.point_id).filter(Boolean));
    (pendingCandidates || []).forEach(point => {
      events.push({
        event_id: sharedSwingPointEventId(point, 'candidate'),
        source_type: SIMULATION_TRACE_SOURCE_TYPE,
        generated_by: SHARED_SWING_POINT_GENERATOR,
        detector_id: SHARED_SWING_POINT_DETECTOR_ID,
        event_type: 'swing_candidate',
        simulation_time: point.pivot_time,
        timeframe: tf,
        panel: tf,
        price: point.pivot_price,
        point_id: point.point_id,
        summary: `${tf} ${point.type === 'swing_high' ? '高値' : '安値'}Candidate。Confirmまで残り${point.confirmation_remaining_bars}本。`,
        reason_codes: ['SWING_CANDIDATE_PENDING', point.type === 'swing_high' ? 'UNIQUE_HIGH_LEFT_WINDOW' : 'UNIQUE_LOW_LEFT_WINDOW'],
        rule_ids: ['rule_shared_swing_candidate', 'rule_explicit_timeframe_confirm_bars'],
        cause_event_ids: [],
        state_before: {},
        state_after: { lifecycle_status: 'candidate', usable_as_basis: false, confirmation_remaining_bars: point.confirmation_remaining_bars },
        display: { visible: false, open: false, pinned: false, style: 'swing_candidate' }
      });
    });
    (layers?.all || []).forEach(point => {
      const candidateEventId = sharedSwingPointEventId(point, 'candidate');
      const confirmedEventId = sharedSwingPointEventId(point, 'confirmed');
      events.push({
        event_id: candidateEventId,
        source_type: SIMULATION_TRACE_SOURCE_TYPE,
        generated_by: SHARED_SWING_POINT_GENERATOR,
        detector_id: SHARED_SWING_POINT_DETECTOR_ID,
        event_type: 'swing_candidate',
        simulation_time: point.pivot_time,
        timeframe: tf,
        panel: tf,
        price: point.pivot_price,
        point_id: point.point_id,
        summary: `${tf} ${point.type === 'swing_high' ? '高値' : '安値'}Candidateを観測。`,
        reason_codes: ['SWING_CANDIDATE_CREATED'],
        rule_ids: ['rule_shared_swing_candidate'],
        cause_event_ids: [],
        state_before: {},
        state_after: { lifecycle_status: 'candidate', usable_as_basis: false },
        display: { visible: false, open: false, pinned: false, style: 'swing_candidate' }
      });
      events.push({
        event_id: confirmedEventId,
        source_type: SIMULATION_TRACE_SOURCE_TYPE,
        generated_by: SHARED_SWING_POINT_GENERATOR,
        detector_id: SHARED_SWING_POINT_DETECTOR_ID,
        event_type: 'swing_confirmed',
        simulation_time: point.confirmed_time,
        timeframe: tf,
        panel: tf,
        price: point.pivot_price,
        point_id: point.point_id,
        summary: `${tf} ${point.type === 'swing_high' ? '高値' : '安値'}をConfirm bars=${point.confirm_bars}で確定。${point.role_label || ''}`,
        reason_codes: ['SWING_CONFIRMED', point.type === 'swing_high' ? 'UNIQUE_HIGH_FULL_WINDOW' : 'UNIQUE_LOW_FULL_WINDOW', String(point.role || '').toUpperCase()],
        rule_ids: ['rule_shared_swing_confirm', 'rule_no_lookahead_confirm_window', 'rule_explicit_timeframe_confirm_bars'],
        cause_event_ids: [candidateEventId],
        state_before: { lifecycle_status: 'candidate', usable_as_basis: false },
        state_after: {
          lifecycle_status: 'confirmed',
          basis_role: point.role === 'basis_retired' ? 'basis_active' : point.role,
          usable_as_basis: point.role === 'basis_active' || point.role === 'basis_retired'
        },
        display: { visible: visiblePointIds.has(point.point_id), open: false, pinned: false, style: point.type === 'swing_high' ? 'swing_high_confirmed' : 'swing_low_confirmed' }
      });
      if (point.role === 'basis_retired') {
        const replacingPointId = point.retired_by_point_id || point.retired_by_key || '';
        const replacingConfirmedEventId = replacingPointId ? `swing_evt_${stableSwingToken(replacingPointId)}_confirmed` : '';
        events.push({
          event_id: sharedSwingPointEventId(point, 'retired'),
          source_type: SIMULATION_TRACE_SOURCE_TYPE,
          generated_by: SHARED_SWING_POINT_GENERATOR,
          detector_id: SHARED_SWING_POINT_DETECTOR_ID,
          event_type: 'swing_retired',
          simulation_time: point.retired_time || point.confirmed_time,
          timeframe: tf,
          panel: tf,
          price: point.pivot_price,
          point_id: point.point_id,
          summary: `${tf} ${point.type === 'swing_high' ? '高値' : '安値'}確定点を、より極端な同種点によりRetired。`,
          reason_codes: ['SWING_RETIRED', String(point.retired_reason || 'REPLACED_BY_MORE_EXTREME').toUpperCase()],
          rule_ids: ['rule_shared_swing_retirement'],
          cause_event_ids: [confirmedEventId, replacingConfirmedEventId].filter(Boolean),
          state_before: { lifecycle_status: 'confirmed', basis_role: 'basis_active', usable_as_basis: true },
          state_after: { lifecycle_status: 'retired', basis_role: 'basis_retired', usable_as_basis: false, retired_by_point_id: replacingPointId },
          display: { visible: false, open: false, pinned: false, style: 'swing_retired' }
        });
      }
    });
    return events;
  }

  function isUniqueExtreme(values, candidateValue, mode) {
    if (candidateValue == null) return false;
    let count = 0;
    for (const value of values) {
      if (value == null) return false;
      if (value === candidateValue) count += 1;
      if (mode === 'high' && value > candidateValue) return false;
      if (mode === 'low' && value < candidateValue) return false;
    }
    return count === 1;
  }

  function buildCandidatePoints(rows, source, overrideConfirmBars, context = {}) {
    const settings = getDowBasisPointSettings(source, overrideConfirmBars);
    if (!rows.length) return [];

    const points = [];
    const locked = new Set();
    const confirmBars = settings.confirm_bars;
    const candidateOffset = Math.max(1, Math.min(confirmBars - 2, Math.floor((confirmBars - 1) / 2)));

    function addPoint(candidateIndex, type, currentIndex, rule) {
      const key = `${type}:${candidateIndex}`;
      if (locked.has(key)) return;
      const row = rows[candidateIndex] || {};
      const confirmRow = rows[currentIndex] || {};
      const price = type === 'swing_high' ? rowHigh(row) : rowLow(row);
      if (price == null) return;
      locked.add(key);
      const timeframe = normalizePanelTimeframe(context.timeframe || row.timeframe || source?.timeframe || 'M5', 'M5');
      const pointId = swingPointStableId(timeframe, type, row, confirmBars);
      points.push({
        key,
        point_id: pointId,
        index: candidateIndex,
        source_index: Math.max(0, Math.floor(numberOrNull(row.index) ?? candidateIndex)),
        type,
        timeframe,
        source_role: String(context.source_role || ''),
        pivot_time: row.datetime || row.time || '',
        pivot_ms: numberOrNull(row.start_ms) ?? rowTimeMs(row),
        pivot_price: price,
        price_source: pointPriceSource(type),
        confirmed_time: confirmRow.datetime || confirmRow.time || '',
        confirmed_ms: numberOrNull(confirmRow.end_ms) ?? numberOrNull(confirmRow.start_ms) ?? rowTimeMs(confirmRow),
        confirmed_index: currentIndex,
        confirmed_source_index: Math.max(0, Math.floor(numberOrNull(confirmRow.index) ?? currentIndex)),
        lag_bars: currentIndex - candidateIndex,
        confirm_bars: confirmBars,
        candidate_offset: candidateOffset,
        method: settings.method,
        rule,
        no_lookahead: true,
        threshold_enabled: false,
        lifecycle_status: 'confirmed',
        basis_role: 'unresolved',
        usable_as_basis: false
      });
    }

    for (let currentIndex = confirmBars - 1; currentIndex < rows.length; currentIndex++) {
      const startIndex = currentIndex - confirmBars + 1;
      const candidateIndex = startIndex + candidateOffset;
      const window = rows.slice(startIndex, currentIndex + 1);
      const highs = window.map(rowHigh);
      const lows = window.map(rowLow);
      const candidate = rows[candidateIndex] || {};
      const candidateHigh = rowHigh(candidate);
      const candidateLow = rowLow(candidate);

      if (isUniqueExtreme(highs, candidateHigh, 'high')) {
        addPoint(candidateIndex, 'swing_high', currentIndex, `center bar is unique high within last ${confirmBars} bars`);
      }
      if (isUniqueExtreme(lows, candidateLow, 'low')) {
        addPoint(candidateIndex, 'swing_low', currentIndex, `center bar is unique low within last ${confirmBars} bars`);
      }
    }

    return points.sort((a, b) => a.index - b.index || (a.type === 'swing_high' ? -1 : 1));
  }

  function buildPointLayers(candidatePoints) {
    const roles = new Map();
    candidatePoints.forEach((point, idx) => {
      roles.set(point.key, {
        ...point,
        role: 'candidate',
        basis_role: 'candidate_only',
        lifecycle_status: 'confirmed',
        usable_as_basis: false,
        role_label: point.type === 'swing_high' ? 'Candidate high' : 'Candidate low',
        candidate_id: idx + 1,
        retired_time: '',
        retired_by_key: '',
        retired_reason: ''
      });
    });

    const activeSequence = [];

    function moreExtreme(next, current) {
      const nextPrice = numberOrNull(next?.pivot_price);
      const currentPrice = numberOrNull(current?.pivot_price);
      if (nextPrice == null || currentPrice == null) return false;
      if (next.type === 'swing_high') return nextPrice > currentPrice;
      return nextPrice < currentPrice;
    }

    candidatePoints.forEach(point => {
      const rec = roles.get(point.key);
      if (!rec) return;

      if (!activeSequence.length) {
        rec.role = 'basis_active';
        rec.basis_role = 'basis_active';
        rec.lifecycle_status = 'confirmed';
        rec.usable_as_basis = true;
        rec.role_label = point.type === 'swing_high' ? 'Active basis high' : 'Active basis low';
        activeSequence.push(rec);
        return;
      }

      const last = activeSequence[activeSequence.length - 1];
      if (last.type === point.type) {
        if (moreExtreme(rec, last)) {
          last.role = 'basis_retired';
          last.basis_role = 'basis_retired';
          last.lifecycle_status = 'retired';
          last.usable_as_basis = false;
          last.role_label = last.type === 'swing_high' ? 'Retired basis high' : 'Retired basis low';
          last.retired_time = rec.confirmed_time || rec.pivot_time || '';
          last.retired_by_key = rec.key;
          last.retired_by_point_id = rec.point_id || rec.key;
          last.retired_by_pivot_time = rec.pivot_time || '';
          last.retired_by_confirmed_time = rec.confirmed_time || '';
          last.retired_by_price = rec.pivot_price;
          last.retired_by_price_source = rec.price_source || pointPriceSource(rec.type);
          last.retired_price_diff = (numberOrNull(rec.pivot_price) != null && numberOrNull(last.pivot_price) != null)
            ? numberOrNull(rec.pivot_price) - numberOrNull(last.pivot_price)
            : null;
          last.retired_reason = last.type === 'swing_high' ? 'replaced_by_higher_high_candidate' : 'replaced_by_lower_low_candidate';

          rec.role = 'basis_active';
          rec.basis_role = 'basis_active';
          rec.lifecycle_status = 'confirmed';
          rec.usable_as_basis = true;
          rec.role_label = point.type === 'swing_high' ? 'Active basis high' : 'Active basis low';
          activeSequence[activeSequence.length - 1] = rec;
        }
      } else {
        rec.role = 'basis_active';
        rec.basis_role = 'basis_active';
        rec.lifecycle_status = 'confirmed';
        rec.usable_as_basis = true;
        rec.role_label = point.type === 'swing_high' ? 'Active basis high' : 'Active basis low';
        activeSequence.push(rec);
      }
    });

    const all = Array.from(roles.values()).sort((a, b) => a.index - b.index || (a.type === 'swing_high' ? -1 : 1));
    return {
      all,
      candidateOnly: all.filter(p => p.role === 'candidate'),
      activeBasis: all.filter(p => p.role === 'basis_active'),
      retiredBasis: all.filter(p => p.role === 'basis_retired')
    };
  }

  function createModal(state) {
    ensureStyle();
    const old = document.getElementById('gptFxLabChartBackdrop');
    if (old) old.remove();

    const backdrop = document.createElement('div');
    backdrop.id = 'gptFxLabChartBackdrop';
    backdrop.className = 'gpt-fx-chart-backdrop';
    backdrop.innerHTML = `
      <section class="gpt-fx-chart-modal" role="dialog" aria-modal="true" aria-label="GPT FX Lab Dow basis point chart viewer">
        <button class="gpt-fx-chart-window-btn" type="button" data-action="toggle-wide" title="画面最大化 / 元に戻す" aria-label="画面最大化 / 元に戻す">□</button>
        <header class="gpt-fx-chart-header">
          <div>
            <h2 class="gpt-fx-chart-title">USDJPY Multi-TF / Expansion Review + Entry Observation / Close + MA20 + T3 + BB + Dow Candidate / Basis / History</h2>
            <div class="gpt-fx-chart-subtitle">gpt_fx_lab Overlay Plugin / Expansion検討=左H4・右DAY/WEEK / M5実行観測レイアウトも保持 / 共有縦線は時刻同期 / Dow・Cycle状態は観測のみ / Entry判定はまだ行わない</div>
          </div>
          <div class="gpt-fx-chart-actions">
            <button class="gpt-fx-chart-btn" type="button" data-action="open-display-settings" title="表示・解析設定を開く">⚙ 設定</button>
            <button class="gpt-fx-chart-btn" type="button" data-action="window-older">古い窓</button>
            <button class="gpt-fx-chart-btn" type="button" data-action="window-newer">新しい窓</button>
            <button class="gpt-fx-chart-btn" type="button" data-action="window-random">ランダム窓</button>
            <button class="gpt-fx-chart-btn" type="button" data-action="window-latest">最新窓</button>
            <button class="gpt-fx-chart-btn" type="button" data-layout="EXPANSION_REVIEW" title="左H4 / 右上DAY / 右下WEEK のExpansion検討レイアウト">Expansion検討</button>
            <button class="gpt-fx-chart-btn" type="button" data-layout="M5_ENTRY" title="左M5 / 右H1・H4のEntry観測レイアウト">M5実行</button>
            <button class="gpt-fx-chart-btn" type="button" data-action="copy-url">URLコピー</button>
            <button class="gpt-fx-chart-btn is-active" type="button" data-action="run-visible-range-simulation" title="現在表示中のM5範囲を古い足から順番に評価">表示範囲Simulation</button>
            <button class="gpt-fx-chart-btn is-active" type="button" data-action="open-batch-simulation" title="複数Dataset・期間をCase単位で一括実行">一括Simulation</button>
            <button class="gpt-fx-chart-btn" type="button" data-action="open-simulation-run-profile">Run設定</button>
            <button class="gpt-fx-chart-btn" type="button" data-action="comment-open-all">User全表示</button>
            <button class="gpt-fx-chart-btn" type="button" data-action="simulation-open-all">Simulation全表示</button>
            <button class="gpt-fx-chart-btn" type="button" data-action="comment-close-all">注釈全閉じ</button>
            <button class="gpt-fx-chart-btn" type="button" data-action="comment-save">Userコメント保存</button>
            <button class="gpt-fx-chart-btn" type="button" data-action="scroll-left" title="表示窓を100本左へ">←100</button>
            <button class="gpt-fx-chart-btn" type="button" data-action="scroll-right" title="表示窓を100本右へ">100→</button>
            <button class="gpt-fx-chart-btn" type="button" data-action="redraw">再抽出</button>
            <button class="gpt-fx-chart-btn" type="button" data-action="close">閉じる</button>
          </div>
        </header>
        <div class="gpt-fx-chart-meta is-collapsed" data-role="meta"></div>
        <div class="gpt-fx-chart-body" data-role="body">
          <div class="gpt-fx-chart-scroll" data-role="scroll">
            <canvas class="gpt-fx-chart-canvas" data-role="canvas"></canvas>
          </div>
          <section class="gpt-fx-chart-settings-panel" data-role="display-settings-panel" aria-label="チャート表示・解析設定">
            <div class="gpt-fx-chart-settings-header">
              <div>
                <h3 class="gpt-fx-chart-settings-title">表示・解析設定</h3>
                <div class="gpt-fx-chart-settings-subtitle">設定変更後は即時再描画。パネル外のチャート操作も可能です。</div>
              </div>
              <button class="gpt-fx-chart-settings-close" type="button" data-action="close-display-settings" title="設定を閉じる">×</button>
            </div>
            <div class="gpt-fx-chart-settings-body">
              <section class="gpt-fx-chart-settings-section">
                <h4 class="gpt-fx-chart-settings-section-title">表示窓・材料点</h4>
                <div class="gpt-fx-chart-settings-controls">
                  <label class="gpt-fx-chart-control">窓
                    <input class="gpt-fx-chart-number" type="number" min="50" step="100" value="1000" data-role="window-size" title="表示窓の件数">
                  </label>
                  <label class="gpt-fx-chart-control">Confirm
                    <input class="gpt-fx-chart-number" type="number" min="3" max="101" step="1" value="10" data-role="confirm-bars">
                  </label>
                  <button class="gpt-fx-chart-btn" type="button" data-confirm-preset="10">10</button>
                  <button class="gpt-fx-chart-btn" type="button" data-confirm-preset="15">15</button>
                  <button class="gpt-fx-chart-btn" type="button" data-confirm-preset="20">20</button>
                  <button class="gpt-fx-chart-btn" type="button" data-confirm-preset="30">30</button>
                </div>
              </section>
              <section class="gpt-fx-chart-settings-section">
                <h4 class="gpt-fx-chart-settings-section-title">上位足パネル</h4>
                <div class="gpt-fx-chart-settings-controls">
                  <label class="gpt-fx-chart-control">上位Confirm
                    <input class="gpt-fx-chart-number" type="number" min="3" max="101" step="1" value="7" data-role="upper-confirm-bars">
                  </label>
                  <label class="gpt-fx-chart-control">余白
                    <input class="gpt-fx-chart-number" type="number" min="0" max="300" step="10" value="30" data-role="upper-warmup-bars">
                  </label>
                  <button class="gpt-fx-chart-btn" type="button" data-upper-warmup-preset="0">0</button>
                  <button class="gpt-fx-chart-btn" type="button" data-upper-warmup-preset="30">30</button>
                  <button class="gpt-fx-chart-btn" type="button" data-upper-warmup-preset="60">60</button>
                  <button class="gpt-fx-chart-btn" type="button" data-upper-warmup-preset="100">100</button>
                  <button class="gpt-fx-chart-btn" type="button" data-upper-tf="H1">H1</button>
                  <button class="gpt-fx-chart-btn" type="button" data-upper-tf="H4">H4</button>
                  <button class="gpt-fx-chart-btn" type="button" data-upper-tf="BOTH">H1+H4</button>
                </div>
              </section>
              <section class="gpt-fx-chart-settings-section">
                <h4 class="gpt-fx-chart-settings-section-title">描画レイヤー</h4>
                <div class="gpt-fx-chart-settings-controls">
                  <button class="gpt-fx-chart-btn" type="button" data-mode="basis_only">Basisのみ</button>
                  <button class="gpt-fx-chart-btn" type="button" data-mode="basis_history">Basis+履歴</button>
                  <button class="gpt-fx-chart-btn" type="button" data-mode="all">全部表示</button>
                  <button class="gpt-fx-chart-btn" type="button" data-action="toggle-high-low-range">H/Lレンジ</button>
                  <button class="gpt-fx-chart-btn" type="button" data-action="toggle-bollinger">BB</button>
                  <button class="gpt-fx-chart-btn" type="button" data-action="toggle-meta">状態表示</button>
                </div>
              </section>
              <section class="gpt-fx-chart-settings-section">
                <h4 class="gpt-fx-chart-settings-section-title">注釈表示</h4>
                <div class="gpt-fx-chart-settings-controls">
                  <button class="gpt-fx-chart-btn" type="button" data-action="toggle-saved-hsi">User HSI表示ON</button>
                  <button class="gpt-fx-chart-btn" type="button" data-action="toggle-user-comments">UserコメントON</button>
                  <button class="gpt-fx-chart-btn" type="button" data-action="toggle-simulation-comments">SimulationコメントON</button>
                </div>
              </section>
              <section class="gpt-fx-chart-settings-section is-wide">
                <h4 class="gpt-fx-chart-settings-section-title">HSI表示</h4>
                <div class="gpt-fx-chart-settings-controls">
                  <label class="gpt-fx-chart-control">HSI
                    <input class="gpt-fx-chart-text" type="text" value="55,89,144,188,233,305,377" data-role="hsi-values" title="カンマ区切りのHSI値">
                  </label>
                  <label class="gpt-fx-chart-control">倍率
                    <span class="gpt-fx-chart-scale-wrap">
                      <input class="gpt-fx-chart-number is-scale" type="text" inputmode="decimal" value="6" data-role="hsi-scale">
                      <span class="gpt-fx-chart-scale-buttons" aria-label="倍率調整">
                        <button class="gpt-fx-chart-scale-step-btn" type="button" data-action="hsi-scale-up">▲</button>
                        <button class="gpt-fx-chart-scale-step-btn" type="button" data-action="hsi-scale-down">▼</button>
                      </span>
                    </span>
                  </label>
                  <button class="gpt-fx-chart-btn" type="button" data-action="hsi-clear">HSIクリア</button>
                </div>
              </section>
            </div>
          </section>
          <div class="gpt-fx-chart-range-result" data-role="visible-range-run-result" aria-live="polite"></div>
          <div class="gpt-fx-chart-tooltip" data-role="tooltip"></div>
          <div class="gpt-fx-chart-comment-popover" data-role="comment-popover"></div>
          <div class="gpt-fx-chart-simulation-popover" data-role="simulation-trace-popover"></div>
          <div class="gpt-fx-chart-text-label-popover" data-role="text-label-popover"></div>
          <div class="gpt-fx-chart-context-menu" data-role="hsi-context-menu"></div>
          <div class="gpt-fx-chart-run-overlay" data-role="simulation-run-overlay">
            <div class="gpt-fx-chart-run-dialog" data-role="simulation-run-dialog" role="dialog" aria-modal="false" aria-label="Simulation Run / Timeframe Profile"></div>
          </div>
          <div class="gpt-fx-chart-batch-overlay" data-role="batch-simulation-overlay">
            <div class="gpt-fx-chart-batch-dialog" data-role="batch-simulation-dialog" role="dialog" aria-modal="false" aria-label="Batch Simulation Runner"></div>
          </div>
        </div>
        <footer class="gpt-fx-chart-footer">
          <div class="gpt-fx-chart-legend" data-role="legend"></div>
          <div data-role="footer-note">Data path: $.display_sets.chart_latest_1000</div>
        </footer>
      </section>
    `;
    document.body.appendChild(backdrop);
    backdrop.addEventListener('click', event => {
      if (event.target === backdrop) backdrop.remove();
    });
    backdrop.querySelector('[data-action="close"]').addEventListener('click', () => backdrop.remove());
    const scroll = backdrop.querySelector('[data-role="scroll"]');
    scroll.addEventListener('wheel', event => {
      if (state.widthMultiplier <= 1) return;
      if (Math.abs(event.deltaY) > Math.abs(event.deltaX)) {
        scroll.scrollLeft += event.deltaY;
        event.preventDefault();
      }
    }, { passive: false });
    return backdrop;
  }

  function applyModeButtonState(backdrop, state) {
    backdrop.querySelectorAll('[data-mode]').forEach(btn => {
      btn.classList.toggle('is-active', btn.getAttribute('data-mode') === state.viewMode);
    });
    backdrop.querySelectorAll('[data-confirm-preset]').forEach(btn => {
      btn.classList.toggle('is-active', Number(btn.getAttribute('data-confirm-preset')) === Number(state.confirmBars));
    });
    const highLowButton = backdrop.querySelector('[data-action="toggle-high-low-range"]');
    if (highLowButton) {
      highLowButton.classList.toggle('is-active', state.showHighLowRange !== false);
      highLowButton.textContent = state.showHighLowRange === false ? 'H/LレンジOFF' : 'H/LレンジON';
    }
    const bbButton = backdrop.querySelector('[data-action="toggle-bollinger"]');
    if (bbButton) {
      bbButton.classList.toggle('is-active', state.showBollinger === true);
      bbButton.textContent = state.showBollinger === true ? 'BB ON' : 'BB OFF';
    }
    backdrop.querySelectorAll('[data-layout]').forEach(btn => {
      btn.classList.toggle('is-active', normalizeChartLayout(btn.getAttribute('data-layout')) === normalizeChartLayout(state.chartLayout));
    });
    backdrop.querySelectorAll('[data-upper-tf]').forEach(btn => {
      btn.classList.toggle('is-active', normalizeUpperDisplayMode(btn.getAttribute('data-upper-tf')) === normalizeUpperDisplayMode(state.upperTimeframe));
      btn.classList.toggle('is-muted', isExpansionReviewLayout(state));
    });
    backdrop.querySelectorAll('[data-upper-warmup-preset]').forEach(btn => {
      btn.classList.toggle('is-active', normalizeUpperWarmupBars(btn.getAttribute('data-upper-warmup-preset'), 30) === normalizeUpperWarmupBars(state.upperWarmupBars, 30));
      btn.title = '右側上位足パネルだけ過去側へ追加表示するバー数';
    });
    backdrop.querySelectorAll('[data-hsi-dir]').forEach(btn => {
      btn.classList.toggle('is-active', btn.getAttribute('data-hsi-dir') === normalizeHsiDirection(state.hsiDirection));
    });
    const savedHsiButton = backdrop.querySelector('[data-action="toggle-saved-hsi"]');
    if (savedHsiButton) {
      const userHsiVisible = state.showSavedHsi !== false || state.showManualHsi !== false;
      savedHsiButton.classList.toggle('is-active', userHsiVisible);
      savedHsiButton.textContent = userHsiVisible ? 'User HSI表示ON' : 'User HSI表示OFF';
      savedHsiButton.title = '人間が設定した現在HSI・保存HSIをまとめて表示ON/OFF。Simulation HSIとは独立。';
    }
    const metaButton = backdrop.querySelector('[data-action="toggle-meta"]');
    const metaNode = backdrop.querySelector('[data-role="meta"]');
    if (metaButton) {
      metaButton.classList.toggle('is-active', state.showMeta === true);
      metaButton.textContent = state.showMeta === true ? '状態表示ON' : '状態表示';
    }
    if (metaNode) metaNode.classList.toggle('is-collapsed', state.showMeta !== true);
    // HSI起点追加・コメント追加は右クリックメニューに統一。
    // 事前モード切替ボタンは認知負荷が高いため表示しない。
    const userCommentButton = backdrop.querySelector('[data-action="toggle-user-comments"]');
    if (userCommentButton) {
      userCommentButton.classList.toggle('is-active', state.showUserComments !== false);
      userCommentButton.textContent = state.showUserComments === false ? 'UserコメントOFF' : 'UserコメントON';
      userCommentButton.title = '手動入力したHuman Commentの表示ON/OFF';
    }
    const simulationCommentButton = backdrop.querySelector('[data-action="toggle-simulation-comments"]');
    if (simulationCommentButton) {
      simulationCommentButton.classList.toggle('is-active', state.showSimulationComments !== false);
      simulationCommentButton.textContent = state.showSimulationComments === false ? 'SimulationコメントOFF' : 'SimulationコメントON';
      simulationCommentButton.title = 'Simulation Trace JSON由来の読み取り専用コメント表示ON/OFF';
    }
    const runProfileButton = backdrop.querySelector('[data-action="open-simulation-run-profile"]');
    if (runProfileButton) {
      const valid = state?.simulationRunValidation?.valid === true;
      runProfileButton.classList.toggle('is-active', valid);
      runProfileButton.textContent = valid ? 'Run設定✓' : 'Run設定';
      runProfileButton.title = `${state?.simulationRunProfileLoadStatus || 'Run Profile loading'} / ${valid ? 'Snapshot作成可能' : '設定確認が必要'}`;
    }
    const settingsPanel = backdrop.querySelector('[data-role="display-settings-panel"]');
    const settingsButton = backdrop.querySelector('[data-action="open-display-settings"]');
    if (settingsPanel) settingsPanel.classList.toggle('is-open', state.displaySettingsOpen === true);
    if (settingsButton) settingsButton.classList.toggle('is-active', state.displaySettingsOpen === true);
    const batchButton = backdrop.querySelector('[data-action="open-batch-simulation"]');
    if (batchButton) {
      const running = state?.batchSimulationRunInProgress === true;
      batchButton.disabled = false;
      batchButton.classList.toggle('is-active', state?.batchSimulationDialogOpen === true || running);
      batchButton.textContent = running
        ? `一括Simulation ${state?.batchSimulationProgress?.case_no || 0}/${state?.batchSimulationProgress?.case_total || 0}`
        : state?.batchSimulationRunSnapshot
          ? `一括Simulation ✓ ${state.batchSimulationRunSnapshot.summary?.case_count || 0}Case`
          : '一括Simulation';
      batchButton.title = running
        ? `${state?.batchSimulationRunStatus || '実行中'} / 累計実現損益 ${batchSimulationFormatJpy(state?.batchSimulationProgress?.cumulative_realized_profit_jpy)}`
        : '複数Dataset・期間をCase単位で逐次実行します。';
    }
    const visibleRangeButton = backdrop.querySelector('[data-action="run-visible-range-simulation"]');
    if (visibleRangeButton) {
      const running = state?.simulationRangeRunInProgress === true;
      const summary = state?.simulationRangeRunSnapshot?.summary || {};
      visibleRangeButton.disabled = running;
      visibleRangeButton.classList.toggle('is-active', !running);
      const period = state?.simulationRangeRunSnapshot?.period || {};
      visibleRangeButton.textContent = running
        ? '表示範囲Simulation 実行中…'
        : state?.simulationRangeRunSnapshot
          ? `表示範囲Simulation ✓ ${period.completed_step_count || 0}足 / Event${summary.execution_event_count || 0}`
          : '表示範囲Simulation';
      visibleRangeButton.title = running
        ? String(state?.simulationRangeRunStatus || '表示範囲を評価中')
        : '現在表示中のM5範囲を古い足から順番に評価し、Entry / CloseOK / CloseMissをチャートへ表示';
    }
    const commentOpenAllButton = backdrop.querySelector('[data-action="comment-open-all"]');
    if (commentOpenAllButton) {
      commentOpenAllButton.classList.toggle('is-active', state.showAllComments === true);
      commentOpenAllButton.textContent = state.showAllComments === true ? 'User全表示ON' : 'User全表示';
    }
    const simulationOpenAllButton = backdrop.querySelector('[data-action="simulation-open-all"]');
    if (simulationOpenAllButton) {
      simulationOpenAllButton.classList.toggle('is-active', state.showAllSimulationComments === true);
      simulationOpenAllButton.textContent = state.showAllSimulationComments === true ? 'Simulation全表示ON' : 'Simulation全表示';
    }
    const commentSaveButton = backdrop.querySelector('[data-action="comment-save"]');
    if (commentSaveButton) {
      commentSaveButton.title = state.commentSaveStatus || 'コメントSidecar JSONを保存します';
    }
    const wideButton = backdrop.querySelector('[data-action="toggle-wide"]');
    if (wideButton) {
      const isWide = state.widthMultiplier > 1;
      wideButton.classList.toggle('is-active', isWide);
      wideButton.textContent = isWide ? '▢' : '□';
      wideButton.title = isWide ? '元のサイズへ戻す' : '画面最大化';
      wideButton.setAttribute('aria-label', wideButton.title);
    }
  }

  function buildMeta(backdrop, source, rows, layers, state) {
    const meta = backdrop.querySelector('[data-role="meta"]');
    if (!meta) return;
    meta.classList.toggle('is-collapsed', state.showMeta !== true);
    const first = rows[0] || {};
    const last = rows[rows.length - 1] || {};
    const settings = source?.indicator_settings?.t3 || {};
    const bbSettings = getBollingerSettings(source);
    const dowSettings = getDowBasisPointSettings(source, state?.confirmBars);
    const activeHighCount = layers.activeBasis.filter(p => p.type === 'swing_high').length;
    const activeLowCount = layers.activeBasis.filter(p => p.type === 'swing_low').length;
    const retiredHighCount = layers.retiredBasis.filter(p => p.type === 'swing_high').length;
    const retiredLowCount = layers.retiredBasis.filter(p => p.type === 'swing_low').length;
    const candidateHighCount = layers.candidateOnly.filter(p => p.type === 'swing_high').length;
    const candidateLowCount = layers.candidateOnly.filter(p => p.type === 'swing_low').length;
    const hsiValues = parseHsiValues(state?.hsiValuesText);
    const hsiAnchorPrice = numberOrNull(state?.hsiAnchor?.price);
    const totalRows = Number(source?.row_count ?? source?.bars?.length ?? rows.length);
    const windowStart = Math.floor(numberOrNull(state?.windowStart) ?? 0);
    const windowEnd = Math.floor(numberOrNull(state?.windowEndExclusive) ?? (windowStart + rows.length));
    meta.innerHTML = '';
    [
      `${source?.symbol || 'USDJPY'} ${source?.timeframe_label || 'M5'}`,
      `表示 ${rows.length.toLocaleString()} / 全 ${(source?.row_count ?? rows.length).toLocaleString()} 件`,
      `Window ${Math.min(totalRows, windowStart + 1).toLocaleString()}-${windowEnd.toLocaleString()} / ${totalRows.toLocaleString()}`,
      `${first.datetime || ''} → ${last.datetime || ''}`,
      `T3 Periods=${settings.periods ?? 20} / VF=${settings.volume_factor ?? 0.2}`,
      `BB=${state.showBollinger === true ? 'on' : 'off'} (${bbSettings.period}, ${bbSettings.deviations}, shift ${bbSettings.shift})`,
      `Candidate H/L: ${candidateHighCount}/${candidateLowCount}`,
      `Active basis H/L: ${activeHighCount}/${activeLowCount}`,
      `Retired basis H/L: ${retiredHighCount}/${retiredLowCount}`,
      `Confirm bars=${dowSettings.confirm_bars}`,
      `View mode=${state.viewMode}`,
      `Layout=${chartLayoutLabel(state)}`,
      `H/L range=${state.showHighLowRange === false ? 'off' : 'on'}`,
      isExpansionReviewLayout(state)
        ? `Panels=H4 main + DAY/WEEK context / WEEK confirm=${Math.max(3, Math.floor(numberOrNull(state.weekConfirmBars) ?? getWeekContextSettings().confirm_bars))}`
        : `Upper TF=${normalizeUpperDisplayMode(state.upperTimeframe) === 'BOTH' ? 'H1+H4' : normalizeUpperTimeframe(state.upperTimeframe)} / Upper confirm=${Math.max(3, Math.floor(numberOrNull(state.upperConfirmBars) ?? 7))}`,
      isExpansionReviewLayout(state)
        ? `DAY source=${state.upperMapLoadStatus || 'loading'} / ${normalizeUpperMapDataPath(state.upperMapDataPath || defaultUpperMapDataPath())}`
        : `Context warmup=${normalizeUpperWarmupBars(state.upperWarmupBars, 30)} bars / past only`,
      ...(isExpansionReviewLayout(state) ? [`DAY Confirm=${Math.max(3, Math.floor(numberOrNull(state.dayConfirmBars) ?? 7))} / active H-L markers`] : []),
      state.syncCenterTimeMs == null ? 'Time sync: hover only' : `Time sync center: ${formatRowDateTime(state.syncCenterTimeMs)}${state.syncCenterSourcePanel ? ' from ' + state.syncCenterSourcePanel : ''}`,
      `HSI ${normalizeHsiDirection(state.hsiDirection)} ${hsiValues.join(',') || '-'} ×${formatHsiNumber(state.hsiScale ?? getManualHsiSettings(source).scale, 3)} ${hsiAnchorPrice == null ? '(no anchor)' : '@ ' + round3(hsiAnchorPrice)}`,
      `Human HSI=${(state.hsiAnnotations || []).length} saved / ${state.showSavedHsi === false && state.showManualHsi === false ? 'hidden' : 'visible'}`,
      `Simulation HSI=${(state.simulationHsiAnnotations || []).length} / separate source`,
      `Saved VLine=${(state.verticalAnnotations || []).length}`,
      `Cycle VLine=${(state.cycleVerticalAnnotations || []).length}`,
      `User Comments=${(state.comments || []).length} / ${state.showUserComments === false ? 'hidden' : (state.showAllComments ? 'all open' : 'icons')} / ${state.commentSaveStatus || 'sidecar loading'}`,
      `Simulation Trace=${(state.simulationTraceEvents || []).length} / ${state.showSimulationComments === false ? 'hidden' : (state.showAllSimulationComments ? 'all labels' : 'icons')} / ${state.simulationTraceLoadStatus || 'trace loading'}`,
      ...(state.entryFocus ? [`Entry Focus=${state.entryFocus.trade_id || '-'} / ${state.entryFocus.rule_lane || '-'} / ${state.entryFocusProjectionStatus || 'loading'}`] : []),
      `Run Profile=${state.simulationRunValidation?.valid === true ? 'READY' : 'NOT READY'} / ${state.simulationRunProfileLoadStatus || 'loading'} / Snapshot=${state.simulationRunSnapshot?.run_id || 'none'}`,
      `Visible Range Simulation=${state.simulationRangeRunInProgress ? 'RUNNING' : (state.simulationRangeRunSnapshot?.run_id || 'none')} / ${state.simulationRangeRunStatus || '未実行'}`,
      `Dow State=${REQUIRED_SIMULATION_TIMEFRAMES.map(tf => `${tf}:${state.simulationDowTrendSnapshot?.timeframes?.[tf]?.trend_state || '-'}`).join(' / ')}`,
      `Cycle=${REQUIRED_SIMULATION_TIMEFRAMES.map(tf => `${tf}:${state.simulationCyclePositionSnapshot?.timeframes?.[tf]?.phase || '-'}`).join(' / ')}`,
      `TF State=${REQUIRED_SIMULATION_TIMEFRAMES.map(tf => `${tf}:${state.simulationTimeframeStateSnapshot?.timeframes?.[tf]?.data_sufficiency?.status || '-'}`).join(' / ')}`,
      `Upper Decision=${state.simulationUpperContextDecisionSnapshot?.decision_mode || '-'} / Bias=${state.simulationUpperContextDecisionSnapshot?.direction_bias?.value || '-'} / Expansion=${state.simulationUpperContextDecisionSnapshot?.entry_policy?.expansion_entry?.status || '-'}`,
      `Basis price source: High=high / Low=low / Close not used`,
      `No lookahead / Fib threshold not used`
    ].forEach(text => {
      const pill = document.createElement('span');
      pill.className = 'gpt-fx-chart-pill';
      pill.textContent = text;
      meta.appendChild(pill);
    });
  }

  const series = [
    { key: 'close', label: 'Close', color: '#e5e7eb', width: 1.25 },
    { key: 'ma20', label: 'MA20', color: '#f59e0b', width: 1.5 },
    { key: 't3_20_0_2', label: 'T3(20,0.2)', color: '#22d3ee', width: 2.0 }
  ];

  function buildLegend(backdrop) {
    const legend = backdrop.querySelector('[data-role="legend"]');
    legend.innerHTML = '';
    series.forEach(item => {
      const el = document.createElement('span');
      el.className = 'gpt-fx-chart-legend-item';
      el.innerHTML = `<span class="gpt-fx-chart-swatch" style="background:${item.color}"></span><span>${item.label}</span>`;
      legend.appendChild(el);
    });
    const bb = document.createElement('span');
    bb.className = 'gpt-fx-chart-legend-item';
    bb.innerHTML = `<span class="gpt-fx-chart-swatch" style="background:rgba(125,211,252,.72)"></span><span>BB outer</span>`;
    legend.appendChild(bb);
    const bbHalf = document.createElement('span');
    bbHalf.className = 'gpt-fx-chart-legend-item';
    bbHalf.innerHTML = `<span class="gpt-fx-chart-swatch" style="background:rgba(167,139,250,.72)"></span><span>H1 BB half</span>`;
    legend.appendChild(bbHalf);
    const range = document.createElement('span');
    range.className = 'gpt-fx-chart-legend-item';
    range.innerHTML = `<span class="gpt-fx-chart-swatch" style="background:rgba(248,250,252,.58)"></span><span>High/Low range</span>`;
    legend.appendChild(range);
    const hsi = document.createElement('span');
    hsi.className = 'gpt-fx-chart-legend-item';
    hsi.innerHTML = `<span class="gpt-fx-chart-swatch" style="background:rgba(248,113,113,.92)"></span><span>User HSI lines</span>`;
    legend.appendChild(hsi);
    const savedHsi = document.createElement('span');
    savedHsi.className = 'gpt-fx-chart-legend-item';
    savedHsi.innerHTML = `<span style="display:inline-flex;gap:2px"><span style="color:#22d3ee">◆</span><span style="color:#fbbf24">◆</span><span style="color:#c084fc">◆</span></span><span>User Saved HSI（起点別色）</span>`;
    legend.appendChild(savedHsi);
    const simulationHsi = document.createElement('span');
    simulationHsi.className = 'gpt-fx-chart-legend-item';
    simulationHsi.innerHTML = `<span style="display:inline-flex;gap:2px"><span style="color:#22d3ee">●</span><span style="color:#fbbf24">●</span><span style="color:#c084fc">●</span><span style="color:#a3e635">●</span></span><span>Simulation HSI（起点別色）</span>`;
    legend.appendChild(simulationHsi);
    const r23Mid = document.createElement('span');
    r23Mid.className = 'gpt-fx-chart-legend-item';
    r23Mid.innerHTML = `<span style="color:#f8fafc">━</span><span>R2.5</span>`;
    legend.appendChild(r23Mid);
    const comment = document.createElement('span');
    comment.className = 'gpt-fx-chart-legend-item';
    comment.innerHTML = `<span style="color:#facc15">●</span><span>Human comment</span>`;
    legend.appendChild(comment);
    const simulationTrace = document.createElement('span');
    simulationTrace.className = 'gpt-fx-chart-legend-item';
    simulationTrace.innerHTML = `<span style="color:#22d3ee">◆S</span><span>Simulation trace</span>`;
    legend.appendChild(simulationTrace);
    const items = [
      ['○', '#86efac', 'Candidate high'],
      ['○', '#fda4af', 'Candidate low'],
      ['●', '#22c55e', 'Active basis high'],
      ['●', '#ef4444', 'Active basis low'],
      ['●', '#bbf7d0', 'Retired basis high'],
      ['●', '#fbcfe8', 'Retired basis low']
    ];
    items.forEach(([symbol, color, label]) => {
      const el = document.createElement('span');
      el.className = 'gpt-fx-chart-legend-item';
      el.innerHTML = `<span style="color:${color}">${symbol}</span><span>${label}</span>`;
      legend.appendChild(el);
    });
  }

  function getRenderablePoints(layers, mode, markerMode = '') {
    if (markerMode === 'active_basis_only') return layers.activeBasis;
    if (markerMode === 'basis_history') return [...layers.retiredBasis, ...layers.activeBasis];
    if (mode === 'basis_only') return layers.activeBasis;
    if (mode === 'basis_history') return [...layers.retiredBasis, ...layers.activeBasis];
    return layers.all;
  }

  function getPointStyle(point) {
    const isHigh = point.type === 'swing_high';
    if (point.role === 'basis_active') {
      return {
        fill: isHigh ? '#22c55e' : '#ef4444',
        stroke: 'rgba(15, 23, 42, 0.92)',
        radius: 5.8,
        lineWidth: 1.8,
        hollow: false,
        symbol: '●'
      };
    }
    if (point.role === 'basis_retired') {
      return {
        fill: isHigh ? '#bbf7d0' : '#fbcfe8',
        stroke: 'rgba(15, 23, 42, 0.80)',
        radius: 4.8,
        lineWidth: 1.4,
        hollow: false,
        symbol: '●'
      };
    }
    return {
      fill: 'transparent',
      stroke: isHigh ? '#86efac' : '#fda4af',
      radius: 4.6,
      lineWidth: 1.7,
      hollow: true,
      symbol: '○'
    };
  }

  function drawPoint(ctx, xx, yy, point) {
    const style = getPointStyle(point);
    ctx.beginPath();
    ctx.arc(xx, yy, style.radius, 0, Math.PI * 2);
    if (style.hollow) {
      ctx.fillStyle = 'rgba(15, 23, 42, 0.72)';
      ctx.fill();
      ctx.strokeStyle = style.stroke;
      ctx.lineWidth = style.lineWidth;
      ctx.stroke();
    } else {
      ctx.fillStyle = style.fill;
      ctx.fill();
      ctx.strokeStyle = style.stroke;
      ctx.lineWidth = style.lineWidth;
      ctx.stroke();
    }
  }

  function parseDateTimeMs(value) {
    const raw = String(value ?? '').trim();
    const match = raw.match(/^(\d{4})-(\d{2})-(\d{2})[ T](\d{2}):(\d{2})(?::(\d{2}))?/);
    if (!match) {
      const n = Date.parse(raw);
      return Number.isFinite(n) ? n : null;
    }
    const [, yy, mm, dd, hh, mi, ss] = match;
    return new Date(Number(yy), Number(mm) - 1, Number(dd), Number(hh), Number(mi), Number(ss || 0)).getTime();
  }

  function rowTimeMs(row) {
    return parseDateTimeMs(row?.datetime || [row?.date, row?.time].filter(Boolean).join(' '));
  }

  function businessDayKeyForRow(row) {
    const explicit = String(row?.date || '').trim();
    if (/^\d{4}-\d{2}-\d{2}$/.test(explicit)) return explicit;
    const raw = String(row?.datetime || '').trim();
    const matched = raw.match(/^(\d{4}-\d{2}-\d{2})/);
    if (matched) return matched[1];
    const ms = numberOrNull(row?.start_ms) ?? rowTimeMs(row);
    return ms == null ? '' : formatRowDateTime(ms).slice(0, 10);
  }

  function drawBusinessDayBoundaryLines(ctx, args) {
    const { rows, x, pad, panelTimeframe } = args;
    if (!['M5', 'H1', 'H4'].includes(String(panelTimeframe || '').toUpperCase())) return;
    if (!Array.isArray(rows) || rows.length < 2) return;
    ctx.save();
    // 営業日境界線は全窓で同じ見た目に統一する。
    // Confirm stride（1.1px / [4,6] / alpha 0.30）より一段強く、
    // 画像イメージの「長めダッシュ + 点」の特徴を持たせる。
    ctx.strokeStyle = 'rgba(241, 245, 249, 0.70)';
    ctx.lineWidth = 1.7;
    ctx.lineCap = 'round';
    ctx.setLineDash([10, 4, 2, 4]);
    for (let idx = 1; idx < rows.length; idx += 1) {
      const previousDay = businessDayKeyForRow(rows[idx - 1]);
      const currentDay = businessDayKeyForRow(rows[idx]);
      if (!previousDay || !currentDay || previousDay === currentDay) continue;
      const xx = x(idx);
      ctx.beginPath();
      ctx.moveTo(xx, pad.top);
      ctx.lineTo(xx, pad.bottom);
      ctx.stroke();
    }
    ctx.restore();
  }

  function twoDigits(value) {
    return String(value).padStart(2, '0');
  }

  function formatRowDateTime(ms) {
    const n = numberOrNull(ms);
    if (n == null) return '';
    const d = new Date(n);
    if (Number.isNaN(d.getTime())) return '';
    return `${d.getFullYear()}-${twoDigits(d.getMonth() + 1)}-${twoDigits(d.getDate())} ${twoDigits(d.getHours())}:${twoDigits(d.getMinutes())}`;
  }

  function calcSmaRows(rows, period = 20) {
    rows.forEach((row, index) => {
      if (index < period - 1) {
        row.ma20 = null;
        return;
      }
      let sum = 0;
      let valid = true;
      for (let i = index - period + 1; i <= index; i++) {
        const close = numberOrNull(rows[i]?.close);
        if (close == null) { valid = false; break; }
        sum += close;
      }
      row.ma20 = valid ? sum / period : null;
    });
  }

  function calcT3Rows(rows, period = 20, volumeFactor = 0.2) {
    const alpha = 2 / (period + 1);
    const v = volumeFactor;
    const c1 = -v * v * v;
    const c2 = 3 * v * v + 3 * v * v * v;
    const c3 = -6 * v * v - 3 * v - 3 * v * v * v;
    const c4 = 1 + 3 * v + v * v * v + 3 * v * v;
    let e1 = null, e2 = null, e3 = null, e4 = null, e5 = null, e6 = null;
    let previousT3 = null;
    rows.forEach(row => {
      const close = numberOrNull(row.close);
      if (close == null) {
        row.t3_20_0_2 = null;
        row.t3_slope = null;
        row.t3_direction = '';
        row.close_t3_diff = null;
        row.close_t3_position = '';
        row.t3_ready = false;
        return;
      }
      e1 = e1 == null ? close : alpha * close + (1 - alpha) * e1;
      e2 = e2 == null ? e1 : alpha * e1 + (1 - alpha) * e2;
      e3 = e3 == null ? e2 : alpha * e2 + (1 - alpha) * e3;
      e4 = e4 == null ? e3 : alpha * e3 + (1 - alpha) * e4;
      e5 = e5 == null ? e4 : alpha * e4 + (1 - alpha) * e5;
      e6 = e6 == null ? e5 : alpha * e5 + (1 - alpha) * e6;
      const t3 = c1 * e6 + c2 * e5 + c3 * e4 + c4 * e3;
      const slope = previousT3 == null ? null : t3 - previousT3;
      row.t3_20_0_2 = t3;
      row.t3_slope = slope;
      row.t3_direction = slope == null ? '' : slope > 0 ? 'up' : slope < 0 ? 'down' : 'flat';
      row.close_t3_diff = close - t3;
      row.close_t3_position = close > t3 ? 'above' : close < t3 ? 'below' : 'equal';
      row.t3_ready = true;
      previousT3 = t3;
    });
  }

  function enrichDerivedIndicators(rows) {
    calcSmaRows(rows, 20);
    calcT3Rows(rows, 20, 0.2);
    return rows;
  }

  function buildUpperTimeframeRows(allRows, timeframe) {
    const tf = normalizeUpperTimeframe(timeframe);
    const minutes = upperTimeframeMinutes(tf);
    const bucketMs = minutes * 60 * 1000;
    const map = new Map();

    allRows.forEach((row, sourceIndex) => {
      const ms = rowTimeMs(row);
      if (ms == null) return;
      const d = new Date(ms);
      let startMs;
      if (tf === 'WEEK') {
        const day = d.getDay();
        const mondayOffset = day === 0 ? -6 : 1 - day;
        startMs = new Date(d.getFullYear(), d.getMonth(), d.getDate() + mondayOffset, 0, 0, 0, 0).getTime();
      } else {
        const baseHour = tf === 'DAY' ? 0 : (tf === 'H4' ? Math.floor(d.getHours() / 4) * 4 : d.getHours());
        startMs = new Date(d.getFullYear(), d.getMonth(), d.getDate(), baseHour, 0, 0, 0).getTime();
      }
      const key = String(startMs);
      let bucket = map.get(key);
      if (!bucket) {
        bucket = {
          row_no: map.size + 1,
          source_row_start: sourceIndex,
          source_row_end: sourceIndex,
          timeframe: tf,
          date: formatRowDateTime(startMs).slice(0, 10),
          time: formatRowDateTime(startMs).slice(11),
          datetime: formatRowDateTime(startMs),
          start_ms: startMs,
          end_ms: startMs + bucketMs - 1,
          open: numberOrNull(row.open),
          high: rowHigh(row),
          low: rowLow(row),
          close: numberOrNull(row.close),
          volume: numberOrNull(row.volume) ?? 0
        };
        map.set(key, bucket);
        return;
      }
      bucket.source_row_end = sourceIndex;
      const high = rowHigh(row);
      const low = rowLow(row);
      bucket.high = bucket.high == null ? high : (high == null ? bucket.high : Math.max(bucket.high, high));
      bucket.low = bucket.low == null ? low : (low == null ? bucket.low : Math.min(bucket.low, low));
      bucket.close = numberOrNull(row.close) ?? bucket.close;
      bucket.volume += numberOrNull(row.volume) ?? 0;
    });

    const rows = Array.from(map.values()).sort((a, b) => a.start_ms - b.start_ms);
    rows.forEach((row, index) => {
      row.index = index;
      row.row_no = index + 1;
      row.range = numberOrNull(row.high) != null && numberOrNull(row.low) != null ? row.high - row.low : null;
      row.body = numberOrNull(row.open) != null && numberOrNull(row.close) != null ? row.close - row.open : null;
      row.direction = numberOrNull(row.body) == null ? '' : (row.body >= 0 ? 'up' : 'down');
    });
    return enrichDerivedIndicators(rows);
  }

  function filterUpperRowsForWindow(upperRows, m5Rows, upperWarmupBars = 0) {
    const firstMs = rowTimeMs(m5Rows[0]);
    const lastMs = rowTimeMs(m5Rows[m5Rows.length - 1]);
    const warmup = normalizeUpperWarmupBars(upperWarmupBars, 0);
    if (firstMs == null || lastMs == null) return upperRows.slice(-Math.max(120, warmup));
    const matchedIndexes = [];
    upperRows.forEach((row, index) => {
      const start = numberOrNull(row.start_ms);
      const end = numberOrNull(row.end_ms);
      if (start != null && end != null && end >= firstMs && start <= lastMs) {
        matchedIndexes.push(index);
      }
    });
    if (!matchedIndexes.length) return upperRows.slice(-Math.max(120, warmup));
    // M5表示窓は変えず、上位足パネルだけ過去側へ文脈バーを追加する。
    // 未来側へは広げない。同期縦線は各パネルの時刻範囲内だけ描画する。
    const startIndex = Math.max(0, matchedIndexes[0] - warmup);
    const endIndex = matchedIndexes[matchedIndexes.length - 1];
    return upperRows.slice(startIndex, endIndex + 1);
  }

  function centerUpperRowsOnTime(upperRows, baseRows, timeMs) {
    if (!upperRows?.length || !baseRows?.length || timeMs == null) return baseRows || [];
    const centerIndex = findIndexForTime(upperRows, timeMs);
    if (centerIndex == null) return baseRows;
    const count = Math.max(1, Math.min(upperRows.length, baseRows.length));
    const start = clampWindowStart(centerIndex - Math.floor(count / 2), count, upperRows.length);
    return upperRows.slice(start, start + count);
  }

  function getPanelRowIndexFromPoint(panel, px) {
    if (!panel?.rows?.length) return null;
    const ratio = panel.plotW <= 0 ? 0 : (px - panel.pad.left) / panel.plotW;
    return Math.max(0, Math.min(panel.rows.length - 1, Math.round(ratio * (panel.rows.length - 1))));
  }

  function panelRowTimeMs(row) {
    return numberOrNull(row?.start_ms) ?? rowTimeMs(row);
  }

  function buildBollingerBandsForRows(chartRows, settings = { period: 20, deviations: 2, shift: 0, source: 'close' }) {
    const values = chartRows.map(row => numberOrNull(row?.[settings.source]) ?? numberOrNull(row?.close));
    const result = new Array(chartRows.length).fill(null);
    const period = Math.max(2, Math.floor(numberOrNull(settings.period) ?? 20));
    const dev = Math.max(0.1, numberOrNull(settings.deviations) ?? 2.0);
    const shift = Math.floor(numberOrNull(settings.shift) ?? 0);
    for (let i = 0; i < chartRows.length; i++) {
      if (i < period - 1) continue;
      let sum = 0;
      let valid = true;
      for (let j = i - period + 1; j <= i; j++) {
        const n = values[j];
        if (n == null) { valid = false; break; }
        sum += n;
      }
      if (!valid) continue;
      const middle = sum / period;
      let variance = 0;
      for (let j = i - period + 1; j <= i; j++) {
        const d = values[j] - middle;
        variance += d * d;
      }
      const sd = Math.sqrt(variance / period);
      const targetIndex = i + shift;
      if (!chartRows[targetIndex]) continue;
      result[targetIndex] = { upper: middle + dev * sd, middle, lower: middle - dev * sd, width: dev * sd * 2 };
    }
    return result;
  }

  function findIndexForTime(rows, timeMs) {
    if (!rows?.length || timeMs == null) return null;
    const firstStart = numberOrNull(rows[0]?.start_ms) ?? rowTimeMs(rows[0]);
    const lastRow = rows[rows.length - 1];
    const lastEnd = numberOrNull(lastRow?.end_ms) ?? rowTimeMs(lastRow);
    if (firstStart != null && lastEnd != null && (timeMs < firstStart || timeMs > lastEnd)) {
      return null;
    }
    let bestIndex = 0;
    let bestDistance = Infinity;
    rows.forEach((row, index) => {
      const start = numberOrNull(row.start_ms) ?? rowTimeMs(row);
      const end = numberOrNull(row.end_ms) ?? start;
      if (start != null && end != null && timeMs >= start && timeMs <= end) {
        bestIndex = index;
        bestDistance = -1;
        return;
      }
      const base = start ?? rowTimeMs(row);
      if (base == null) return;
      const distance = Math.abs(base - timeMs);
      if (distance < bestDistance) {
        bestDistance = distance;
        bestIndex = index;
      }
    });
    return bestDistance === Infinity ? null : bestIndex;
  }

  function drawChart(backdrop, source, rows, layers, state) {
    const canvas = backdrop.querySelector('[data-role="canvas"]');
    const tooltip = backdrop.querySelector('[data-role="tooltip"]');
    const body = backdrop.querySelector('[data-role="body"]');
    const scroll = backdrop.querySelector('[data-role="scroll"]');
    const scrollLeftBefore = scroll.scrollLeft;
    const rect = scroll.getBoundingClientRect();
    const dpr = window.devicePixelRatio || 1;
    const baseWidth = Math.max(860, Math.floor(rect.width));
    // v0.7.15:
    // 2ペイン化後に widthMultiplier をそのまま canvas 幅へ掛けると、
    // 最大化時に右側の上位足パネルが横スクロール領域の奥へ押し出される。
    // 上位足パネルは「同時に見える」ことが価値なので、描画幅は現在の可視幅に合わせる。
    // widthMultiplier はモーダル最大化状態の保持に使い、2ペイン描画の横幅拡大には使わない。
    const width = Math.max(860, baseWidth);
    const height = Math.max(360, Math.floor(rect.height));
    canvas.width = Math.floor(width * dpr);
    canvas.height = Math.floor(height * dpr);
    canvas.style.width = `${width}px`;
    canvas.style.height = `${height}px`;

    const ctx = canvas.getContext('2d');
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.clearRect(0, 0, width, height);
    state.commentHitBoxes = [];
    state.simulationTraceHitBoxes = [];
    state.savedHsiHitBoxes = [];
    state.simulationHsiHitBoxes = [];
    state.savedVerticalHitBoxes = [];
    state.savedCycleVerticalHitBoxes = [];
    state.textLabelHitBoxes = [];
    state.currentHsiAnchorHitBox = null;

    if (!rows.length) {
      ctx.fillStyle = '#cbd5e1';
      ctx.font = '14px system-ui, sans-serif';
      ctx.fillText('表示できるチャートデータがありません。', 28, 44);
      return;
    }

    const panelTop = 26;
    const panelBottom = 46;
    const panelGap = 18;
    const subPanelGap = 12;

    function buildPanelLayoutRects() {
      const layout = normalizeChartLayout(state.chartLayout);
      const leftW = Math.max(520, Math.floor((width - panelGap) * 0.58));
      const rightW = Math.max(320, width - leftW - panelGap);
      const rightX = leftW + panelGap;

      if (layout === 'EXPANSION_REVIEW') {
        const rightTopH = Math.floor((height - subPanelGap) * 0.46);
        return {
          layout,
          panels: [
            { x: 0, y: 0, w: leftW, h: height, title: 'H4 / Expansion review main', kind: 'h4', timeframe: 'H4', role: 'main' },
            { x: rightX, y: 0, w: rightW, h: rightTopH, title: 'DAY / upper map', kind: 'day', timeframe: 'DAY', role: 'context_top' },
            { x: rightX, y: rightTopH + subPanelGap, w: rightW, h: height - rightTopH - subPanelGap, title: 'WEEK / expansion context', kind: 'week', timeframe: 'WEEK', role: 'context_bottom' }
          ]
        };
      }

      const upperMode = normalizeUpperDisplayMode(state.upperTimeframe);
      const dualUpper = upperMode === 'BOTH';
      const legacyLeftW = Math.max(520, Math.floor((width - panelGap) * (dualUpper ? 0.58 : 0.62)));
      const legacyRightW = Math.max(320, width - legacyLeftW - panelGap);
      const legacyRightX = legacyLeftW + panelGap;
      const legacyRightGap = dualUpper ? subPanelGap : 0;
      const upperPanels = dualUpper
        ? [
            { x: legacyRightX, y: 0, w: legacyRightW, h: Math.floor((height - legacyRightGap) / 2), title: 'H1 upper / context observation', kind: 'h1', timeframe: 'H1', role: 'context_top' },
            { x: legacyRightX, y: Math.floor((height - legacyRightGap) / 2) + legacyRightGap, w: legacyRightW, h: height - Math.floor((height - legacyRightGap) / 2) - legacyRightGap, title: 'H4 upper / macro context observation', kind: 'h4', timeframe: 'H4', role: 'context_bottom' }
          ]
        : [
            { x: legacyRightX, y: 0, w: legacyRightW, h: height, title: `${normalizeUpperTimeframe(state.upperTimeframe)} upper / context observation`, kind: 'upper', timeframe: normalizeUpperTimeframe(state.upperTimeframe), role: 'context' }
          ];
      return {
        layout,
        panels: [
          { x: 0, y: 0, w: legacyLeftW, h: height, title: 'M5 lower / entry observation', kind: 'm5', timeframe: 'M5', role: 'main' },
          ...upperPanels
        ]
      };
    }

    const panelLayout = buildPanelLayoutRects();
    const panelRects = panelLayout.panels;
    const allRows = normalizeAllRows(source);
    const upperConfirm = Math.max(3, Math.floor(numberOrNull(state.upperConfirmBars) ?? getUpperTimeframeSettings(source).confirm_bars));
    function buildPanelData(rect) {
      const timeframe = normalizePanelTimeframe(rect.timeframe, 'M5');
      if (timeframe === 'M5') {
        return { timeframe, panelRows: rows, panelLayers: layers, confirmBars: state.confirmBars, panelSource: source };
      }
      if (timeframe === 'DAY' && isExpansionReviewLayout(state) && state.upperMapAllRows?.length) {
        const referenceTimeMs = referenceTimeForPanelWindow(rows, state);
        const panelRows = sliceRowsAroundTime(state.upperMapAllRows, referenceTimeMs, upperMapWindowSize(state.upperMapSource));
        const panelSource = state.upperMapSource || source;
        const daySettings = getDayUpperMapSettings(source, panelSource);
        const dayConfirm = Math.max(3, Math.floor(numberOrNull(state.dayConfirmBars) ?? daySettings.confirm_bars));
        const candidatePoints = buildCandidatePoints(panelRows, panelSource, dayConfirm);
        const panelLayers = buildPointLayers(candidatePoints);
        // DAY UpperMap is a macro map, but it still needs D1-scale Dow material points.
        // Show only active high/low dots by default so Expansion格付けに必要な構造だけを残す。
        return {
          timeframe,
          panelRows,
          panelLayers,
          confirmBars: dayConfirm,
          panelSource,
          sourceRole: 'upperMap',
          suppressPointMarkers: false,
          pointMarkerMode: daySettings.point_marker_mode || 'active_basis_only'
        };
      }
      if (timeframe === 'WEEK' && isExpansionReviewLayout(state) && state.upperMapAllRows?.length) {
        const panelSource = state.upperMapSource || source;
        const weekRows = buildUpperTimeframeRows(state.upperMapAllRows, 'WEEK');
        const referenceTimeMs = referenceTimeForPanelWindow(rows, state);
        const weekSettings = getWeekContextSettings();
        const useAllHistory = weekSettings.window_mode === 'all_history';
        const panelRows = useAllHistory
          ? weekRows
          : sliceRowsAroundTime(weekRows, referenceTimeMs, Math.max(20, Math.min(weekSettings.window_bars, weekRows.length)));
        const weekConfirm = Math.max(3, Math.floor(numberOrNull(state.weekConfirmBars) ?? weekSettings.confirm_bars));
        const candidatePoints = buildCandidatePoints(panelRows, panelSource, weekConfirm);
        return {
          timeframe,
          panelRows,
          panelLayers: buildPointLayers(candidatePoints),
          confirmBars: weekConfirm,
          panelSource,
          sourceRole: 'weekContext',
          suppressPointMarkers: false,
          pointMarkerMode: weekSettings.point_marker_mode
        };
      }
      const upperAllRows = buildUpperTimeframeRows(allRows, timeframe);
      const baseUpperRows = filterUpperRowsForWindow(upperAllRows, rows, state.upperWarmupBars);
      // ダブルクリック同期時は、M5窓だけでなく全表示ペインを同じ時刻へ寄せる。
      // 通常の上位余白(past only)表示は維持しつつ、同期補正時だけ見比べやすさを優先する。
      const panelRows = state.syncCenterTimeMs == null
        ? baseUpperRows
        : centerUpperRowsOnTime(upperAllRows, baseUpperRows, state.syncCenterTimeMs);
      const candidatePoints = buildCandidatePoints(panelRows, source, upperConfirm);
      const panelLayers = buildPointLayers(candidatePoints);
      return { timeframe, panelRows, panelLayers, confirmBars: upperConfirm, panelSource: source, sourceRole: 'derived' };
    }

    function drawPanel(args) {
      const { ctx, source, rows, layers, state, rect, title, confirmBars, allowHsi, showHighLowRange, showBollinger, suppressPointMarkers, pointMarkerMode } = args;
      const panelTf = panelKindToTimeframe(rect.kind, state);
      const isDayPanel = panelTf === 'DAY';
      const isWeekPanel = panelTf === 'WEEK';
      const weekSettings = isWeekPanel ? getWeekContextSettings() : null;
      const hidePointMarkers = suppressPointMarkers === true;
      const renderPoints = hidePointMarkers ? [] : getRenderablePoints(layers, state.viewMode, pointMarkerMode);
      const pad = {
        left: rect.x + 62,
        right: rect.x + rect.w - 42,
        top: rect.y + panelTop,
        bottom: rect.y + rect.h - panelBottom
      };
      const plotW = pad.right - pad.left;
      const plotH = pad.bottom - pad.top;

      ctx.save();
      ctx.beginPath();
      ctx.rect(rect.x, rect.y, rect.w, rect.h);
      ctx.clip();

      ctx.fillStyle = rect.kind === 'm5' ? 'rgba(15, 23, 42, 0.18)' : 'rgba(2, 6, 23, 0.22)';
      ctx.fillRect(rect.x, rect.y, rect.w, rect.h);

      ctx.fillStyle = 'rgba(226, 232, 240, 0.92)';
      ctx.font = '12px system-ui, sans-serif';
      ctx.textAlign = 'left';
      ctx.textBaseline = 'top';
      ctx.fillText(title, rect.x + 14, rect.y + 8);

      if (!rows.length) {
        ctx.fillStyle = '#cbd5e1';
        ctx.fillText('表示できる上位足データがありません。', rect.x + 28, 44);
        ctx.restore();
        return null;
      }

      const bbSettings = getBollingerSettings(source);
      const bollingerBands = isUpperPanelKind(rect.kind)
        ? buildBollingerBandsForRows(rows, bbSettings)
        : buildBollingerBands(source, rows, bbSettings);
      const manualHsiEnabled = state.showManualHsi !== false && allowHsi && hsiAnchorMatchesPanel(state?.hsiAnchor, rect.kind, state);
      const manualHsiTargets = manualHsiEnabled ? buildManualHsiTargets(source, state) : [];
      assignHsiAnnotationColorSlots([...(state.hsiAnnotations || []), ...(state.simulationHsiAnnotations || [])]);
      const savedHsiItems = allowHsi ? buildVisibleSavedHsiRenderItems(source, state, rows, rect.kind) : [];
      const simulationHsiItems = allowHsi ? buildVisibleSimulationHsiRenderItems(source, state, rows, rect.kind) : [];
      // 表示中のHuman/SIM HSIを時系列順にまとめて色割当する。
      // 同一起点(anchor_id)は同じ色、隣接する別起点は次の色へ進めるため、
      // 横線が重なってもどの起点由来かを追いやすい。
      assignHsiRenderPaletteSlots([...savedHsiItems, ...simulationHsiItems]);
      const values = [];
      rows.forEach((row, index) => {
        series.forEach(s => {
          const n = numberOrNull(row[s.key]);
          if (n != null) values.push(n);
        });
        if (showBollinger === true) {
          const band = bollingerBands[index];
          const upper = numberOrNull(band?.upper);
          const lower = numberOrNull(band?.lower);
          if (upper != null) values.push(upper);
          if (lower != null) values.push(lower);
        }
        const high = rowHigh(row);
        const low = rowLow(row);
        if (high != null) values.push(high);
        if (low != null) values.push(low);
      });
      // HSI target lines are observation aids and can extend far beyond the visible price action.
      // Do not let R5.5/R6/R6.5/R7 targets expand the vertical price scale; keep the chart body
      // scaled by actual price/MA/T3/BB/high-low data.  Anchor points themselves are still included
      // because they are human-selected price points on the chart.
      savedHsiItems.forEach(item => {
        const anchor = numberOrNull(item.anchorPrice);
        if (anchor != null) values.push(anchor);
      });
      simulationHsiItems.forEach(item => {
        const anchor = numberOrNull(item.anchorPrice);
        if (anchor != null) values.push(anchor);
      });
      const anchorPriceForScale = manualHsiEnabled ? numberOrNull(state?.hsiAnchor?.price) : null;
      if (anchorPriceForScale != null) values.push(anchorPriceForScale);
      let min = Math.min(...values);
      let max = Math.max(...values);
      if (!Number.isFinite(min) || !Number.isFinite(max)) { min = 0; max = 1; }
      const extra = Math.max((max - min) * 0.08, 0.02);
      min -= extra;
      max += extra;

      const x = index => pad.left + (rows.length <= 1 ? 0 : (index / (rows.length - 1)) * plotW);
      const y = value => pad.top + ((max - value) / (max - min)) * plotH;

      ctx.fillStyle = 'rgba(15, 23, 42, 0.28)';
      ctx.fillRect(pad.left, pad.top, plotW, plotH);

      ctx.font = '11px system-ui, sans-serif';
      ctx.textBaseline = 'middle';
      for (let i = 0; i <= 5; i++) {
        const rate = i / 5;
        const yy = pad.top + rate * plotH;
        const val = max - rate * (max - min);
        ctx.strokeStyle = 'rgba(148, 163, 184, 0.15)';
        ctx.lineWidth = 1;
        ctx.setLineDash([]);
        ctx.beginPath();
        ctx.moveTo(pad.left, yy);
        ctx.lineTo(pad.right, yy);
        ctx.stroke();
        ctx.fillStyle = 'rgba(203, 213, 225, 0.82)';
        ctx.textAlign = 'right';
        ctx.fillText(val.toFixed(3), pad.left - 8, yy);
      }

      const dayUpperMapSettings = isDayPanel ? getDayUpperMapSettings(source, source) : null;
      const showConfirmStrideLines = rows.length > 1
        && confirmBars >= 2
        && (!isDayPanel || dayUpperMapSettings?.show_confirm_stride_lines !== false);
      if (showConfirmStrideLines) {
        ctx.save();
        ctx.strokeStyle = isDayPanel ? 'rgba(226, 232, 240, 0.24)' : 'rgba(226, 232, 240, 0.30)';
        ctx.lineWidth = isDayPanel ? 1.0 : 1.1;
        ctx.setLineDash([4, 6]);
        for (let idx = 0; idx < rows.length; idx += confirmBars) {
          const xx = x(idx);
          ctx.beginPath();
          ctx.moveTo(xx, pad.top);
          ctx.lineTo(xx, pad.bottom);
          ctx.stroke();
        }
        ctx.restore();
      }

      const panelTimeframe = normalizePanelTimeframe(rect.timeframe || panelKindToTimeframe(rect.kind, state), panelKindToTimeframe(rect.kind, state));
      drawBusinessDayBoundaryLines(ctx, { rows, x, pad, panelTimeframe });

      ctx.textBaseline = 'top';
      ctx.textAlign = 'center';
      const ticks = isUpperPanelKind(rect.kind) ? 4 : (state.widthMultiplier > 1 ? 8 : 5);
      for (let i = 0; i < ticks; i++) {
        const idx = Math.min(rows.length - 1, Math.round((rows.length - 1) * i / Math.max(1, ticks - 1)));
        const row = rows[idx] || {};
        const xx = x(idx);
        ctx.strokeStyle = 'rgba(148, 163, 184, 0.12)';
        ctx.lineWidth = 1;
        ctx.setLineDash([]);
        ctx.beginPath();
        ctx.moveTo(xx, pad.top);
        ctx.lineTo(xx, pad.bottom);
        ctx.stroke();
        ctx.fillStyle = 'rgba(148, 163, 184, 0.95)';
        ctx.fillText(String(row.datetime || row.time || ''), xx, pad.bottom + 14);
      }

      if (showHighLowRange && !isDayPanel) {
        ctx.save();
        ctx.setLineDash([1.5, 2.0]);
        ctx.lineDashOffset = 0;
        ctx.lineCap = 'round';
        ctx.strokeStyle = 'rgba(248, 250, 252, 0.70)';
        ctx.lineWidth = 1.15;
        const pixelsPerBar = rows.length <= 1 ? plotW : plotW / (rows.length - 1);
        const rangeStep = Math.max(1, Math.ceil((isUpperPanelKind(rect.kind) ? 1.5 : 3) / Math.max(pixelsPerBar, 0.001)));
        rows.forEach((row, index) => {
          if (index % rangeStep !== 0) return;
          const high = rowHigh(row);
          const low = rowLow(row);
          if (high == null || low == null) return;
          const xx = x(index);
          ctx.beginPath();
          ctx.moveTo(xx, y(high));
          ctx.lineTo(xx, y(low));
          ctx.stroke();
        });
        ctx.restore();
      }

      if (showBollinger) {
        const isUpperPanel = isUpperPanelKind(rect.kind);
        const bbOuterStroke = isUpperPanel ? 'rgba(125, 211, 252, 0.72)' : 'rgba(167, 139, 250, 0.72)';
        const bbHalfStroke = 'rgba(167, 139, 250, 0.72)';
        const bbFill = isUpperPanel ? 'rgba(14, 165, 233, 0.040)' : 'rgba(139, 92, 246, 0.055)';

        const drawBandValueLine = (valueOf, strokeStyle, lineWidth = 1.05, dash = [5, 4]) => {
          ctx.beginPath();
          ctx.strokeStyle = strokeStyle;
          ctx.lineWidth = lineWidth;
          ctx.setLineDash(dash);
          let started = false;
          bollingerBands.forEach((band, index) => {
            const n = numberOrNull(valueOf(band));
            if (n == null) { started = false; return; }
            const xx = x(index);
            const yy = y(n);
            if (!started) {
              ctx.moveTo(xx, yy);
              started = true;
            } else {
              ctx.lineTo(xx, yy);
            }
          });
          ctx.stroke();
        };

        ctx.save();
        ctx.setLineDash([]);
        ctx.fillStyle = bbFill;
        ctx.beginPath();
        let fillStarted = false;
        const lowerPath = [];
        bollingerBands.forEach((band, index) => {
          const upper = numberOrNull(band?.upper);
          const lower = numberOrNull(band?.lower);
          if (upper == null || lower == null) {
            if (fillStarted && lowerPath.length) {
              for (let i = lowerPath.length - 1; i >= 0; i--) ctx.lineTo(lowerPath[i].x, lowerPath[i].y);
              ctx.closePath();
              ctx.fill();
            }
            ctx.beginPath();
            fillStarted = false;
            lowerPath.length = 0;
            return;
          }
          const xx = x(index);
          const yyUpper = y(upper);
          const yyLower = y(lower);
          if (!fillStarted) {
            ctx.moveTo(xx, yyUpper);
            fillStarted = true;
          } else {
            ctx.lineTo(xx, yyUpper);
          }
          lowerPath.push({ x: xx, y: yyLower });
        });
        if (fillStarted && lowerPath.length) {
          for (let i = lowerPath.length - 1; i >= 0; i--) ctx.lineTo(lowerPath[i].x, lowerPath[i].y);
          ctx.closePath();
          ctx.fill();
        }

        ['upper', 'lower'].forEach(key => {
          drawBandValueLine(band => band?.[key], bbOuterStroke, 1.05, [5, 4]);
        });

        // H1側だけ、MA20(BB middle) と BB外枠の中間線を表示する。
        // M5側は情報量が増えすぎるため、従来のBB外枠のみ。
        if (isUpperPanel) {
          drawBandValueLine(band => {
            const middle = numberOrNull(band?.middle);
            const upper = numberOrNull(band?.upper);
            return middle == null || upper == null ? null : middle + (upper - middle) * 0.5;
          }, bbHalfStroke, 0.95, [3, 5]);
          drawBandValueLine(band => {
            const middle = numberOrNull(band?.middle);
            const lower = numberOrNull(band?.lower);
            return middle == null || lower == null ? null : middle - (middle - lower) * 0.5;
          }, bbHalfStroke, 0.95, [3, 5]);
        }
        ctx.restore();
      }

      series.forEach(s => {
        ctx.strokeStyle = s.color;
        ctx.lineWidth = isUpperPanelKind(rect.kind) ? Math.max(1, s.width - 0.25) : s.width;
        ctx.setLineDash([]);
        ctx.beginPath();
        let started = false;
        rows.forEach((row, index) => {
          const n = numberOrNull(row[s.key]);
          if (n == null) { started = false; return; }
          const xx = x(index);
          const yy = y(n);
          if (!started) {
            ctx.moveTo(xx, yy);
            started = true;
          } else {
            ctx.lineTo(xx, yy);
          }
        });
        ctx.stroke();
      });

      if (allowHsi && savedHsiItems.length) {
        drawSavedHsiAnnotationsForPanel(ctx, { source, items: savedHsiItems, x, y, pad, plotW, state, panelKind: rect.kind });
      }

      if (simulationHsiItems.length) {
        drawSimulationHsiAnnotationsForPanel(ctx, { items: simulationHsiItems, x, y, pad, plotW, state, panelKind: rect.kind });
      }

      if (manualHsiEnabled && manualHsiTargets.length && state.hsiAnchor) {
        const anchorIndex = Math.max(0, Math.min(rows.length - 1, Math.floor(numberOrNull(state.hsiAnchor.index) ?? 0)));
        const anchorPrice = numberOrNull(state.hsiAnchor.price);
        const anchorX = x(anchorIndex);
        const anchorY = anchorPrice == null ? null : y(anchorPrice);
        const x2 = Math.min(pad.right, anchorX + Math.max(96, plotW * 0.12));
        ctx.save();
        if (anchorY != null) {
          ctx.shadowColor = 'rgba(34, 211, 238, 0.72)';
          ctx.shadowBlur = 12;
          ctx.fillStyle = 'rgba(34, 211, 238, 0.95)';
          // 一時HSIの起点リングも、既定のHSI横バー色へ合わせる。
          ctx.strokeStyle = 'rgba(248, 113, 113, 0.94)';
          ctx.lineWidth = 2.8;
          ctx.beginPath();
          ctx.arc(anchorX, anchorY, 8.2, 0, Math.PI * 2);
          ctx.fill();
          ctx.stroke();
          ctx.shadowBlur = 0;
          ctx.fillStyle = 'rgba(15, 23, 42, 0.92)';
          ctx.beginPath();
          ctx.arc(anchorX, anchorY, 3.6, 0, Math.PI * 2);
          ctx.fill();
          state.currentHsiAnchorHitBox = { x: anchorX, y: anchorY, radius: 18, panelKind: rect.kind };
          ctx.font = '11px system-ui, sans-serif';
          ctx.fillStyle = 'rgba(254, 249, 195, 0.95)';
          ctx.textAlign = 'left';
          ctx.textBaseline = 'top';
          const anchorLabelX = Math.min(pad.right - 74, anchorX + 6);
          const hsiDirection = normalizeHsiDirection(state?.hsiDirection);
          const labelHeight = 26;
          // HSIラインの伸びる方向を邪魔しないように、ラベルは逆側へ逃がす。
          // 上向きライン: 起点より下へ表示 / 下向きライン: 起点より上へ表示。
          const preferredLabelY = hsiDirection === 'down'
            ? anchorY - labelHeight - 8
            : anchorY + 8;
          const anchorLabelY = Math.min(
            pad.bottom - labelHeight - 4,
            Math.max(pad.top + 4, preferredLabelY)
          );
          const hsiScaleLabel = formatHsiNumber(numberOrNull(state?.hsiScale) ?? getManualHsiSettings(source).scale, 3);
          ctx.fillText('HSI起点', anchorLabelX, anchorLabelY);
          ctx.fillText(`倍率: ${hsiScaleLabel}`, anchorLabelX, anchorLabelY + 13);
        }
        manualHsiTargets.forEach(target => {
          const yy = y(target.price);
          if (yy < pad.top - 12 || yy > pad.bottom + 12) return;
          drawHsiTargetLine(ctx, { anchorX, x2, yy, target, pad, saved: false });
        });
        ctx.restore();
      }

      const pointsByIndex = new Map();
      renderPoints.forEach(point => {
        const price = numberOrNull(point.pivot_price);
        if (price == null) return;
        const list = pointsByIndex.get(point.index) || [];
        list.push(point);
        pointsByIndex.set(point.index, list);
        drawPoint(ctx, x(point.index), y(price), point);
      });

      const showSavedVerticalMarkers = !isDayPanel && !(isWeekPanel && weekSettings?.show_saved_vertical_markers === false);
      const showSavedCycleVerticalMarkers = !isDayPanel && !(isWeekPanel && weekSettings?.show_cycle_vertical_markers === false);
      if (showSavedVerticalMarkers) {
        drawSavedVerticalMarkersForPanel(ctx, { rows, state, panelKind: rect.kind, x, pad });
      }
      if (showSavedCycleVerticalMarkers) {
        drawSavedCycleVerticalMarkersForPanel(ctx, { rows, state, panelKind: rect.kind, x, pad });
      }

      drawVisibleRangeSimulationCursor(ctx, { rows, state, panelKind: rect.kind, x, pad });
      drawCommentsForPanel(ctx, { rows, state, panelKind: rect.kind, x, y, min, max, pad });
      drawSimulationTraceForPanel(ctx, { rows, state, panelKind: rect.kind, x, y, min, max, pad, bollingerBands, showBollinger });
      drawTextLabelsForPanel(ctx, { rows, state, panelKind: rect.kind, x, y, min, max, pad });
      // 十字カーソルは最後に描画し、HSI線・注釈の上から日時/価格を読み取れるようにする。
      // 操作中パネルの時刻・価格を全表示パネルへ同期し、時間足をまたいで同一点を追えるようにする。
      drawCrosshairForPanel(ctx, { state, panelKind: rect.kind, rows, x, y, min, max, pad, rect });

      ctx.restore();
      return { rect, pad, rows, layers, bollingerBands, x, y, min, max, pointsByIndex, plotW, plotH, allowHsi, title };
    }

    const panelEntries = panelRects.map(rect => {
      const data = buildPanelData(rect);
      const panel = drawPanel({
        ctx,
        source: data.panelSource || source,
        rows: data.panelRows,
        layers: data.panelLayers,
        state,
        rect,
        title: rect.title || `${data.timeframe} context`,
        confirmBars: data.confirmBars,
        allowHsi: true,
        showHighLowRange: state.showHighLowRange !== false,
        showBollinger: state.showBollinger === true,
        suppressPointMarkers: data.suppressPointMarkers,
        pointMarkerMode: data.pointMarkerMode
      });
      if (panel) panel.timeframe = data.timeframe;
      return { panel, data, rect };
    });

    const contextEntries = panelEntries.filter(item => item.data.timeframe !== 'M5');
    state.upperVisibleRows = contextEntries.length > 1
      ? Object.fromEntries(contextEntries.map(item => [item.data.timeframe, item.data.panelRows.length]))
      : (contextEntries[0]?.data.panelRows.length || 0);
    state.upperPointCounts = contextEntries.reduce((acc, item) => {
      const itemLayers = item.data.panelLayers || {};
      acc.candidates += itemLayers.candidateOnly?.length || 0;
      acc.active += itemLayers.activeBasis?.length || 0;
      acc.retired += itemLayers.retiredBasis?.length || 0;
      return acc;
    }, { candidates: 0, active: 0, retired: 0 });

    const panels = panelEntries.map(item => item.panel).filter(Boolean);
    const panelByKind = new Map(panels.map(panel => [panel.rect.kind, panel]));

    function panelAt(px, py) {
      return panels.find(panel => px >= panel.pad.left && px <= panel.pad.right && py >= panel.pad.top && py <= panel.pad.bottom) || null;
    }

    function pointLinesFor(panel, idx) {
      const pointsAtIndex = (panel.pointsByIndex.get(idx) || []).sort((a, b) => {
        const order = { basis_active: 0, basis_retired: 1, candidate: 2 };
        return (order[a.role] ?? 9) - (order[b.role] ?? 9);
      });
      const pointLines = [];
      pointsAtIndex.forEach(point => {
        pointLines.push(`<strong>${getPointStyle(point).symbol} ${point.role_label}</strong>`);
        pointLines.push(`Type: ${point.type}`);
        pointLines.push(`Pivot: ${point.pivot_time} / ${round3(point.pivot_price)}`);
        pointLines.push(`Price source: ${point.price_source || pointPriceSource(point.type)}`);
        pointLines.push(`Confirmed: ${point.confirmed_time}`);
        pointLines.push(`Lag bars: ${point.lag_bars}`);
        pointLines.push(`Confirm bars: ${point.confirm_bars}`);
        pointLines.push(`Rule: ${point.rule}`);
        if (point.role === 'basis_retired') {
          pointLines.push(`Retired: ${point.retired_time || '-'}`);
          pointLines.push(`Retired reason: ${point.retired_reason || '-'}`);
          pointLines.push(`Replaced by pivot: ${point.retired_by_pivot_time || '-'} / ${round3(point.retired_by_price)}`);
          pointLines.push(`Replacement diff: ${round3(point.retired_price_diff)}`);
        }
        if (point.role === 'candidate') pointLines.push(`Basis adopted: no`);
        if (point.role === 'basis_active') pointLines.push(`Basis adopted: yes`);
        pointLines.push(`Threshold used: false`);
        pointLines.push(`No lookahead: true`);
      });
      return pointLines;
    }

    canvas.onclick = event => {
      hideHsiContextMenu(backdrop);
      const bounds = canvas.getBoundingClientRect();
      const px = event.clientX - bounds.left;
      const py = event.clientY - bounds.top;
      const hitTextLabel = findTextLabelHit(state, px, py);
      if (hitTextLabel) {
        const annotation = hitTextLabel.annotation;
        const wasEditingOpen = state.openTextLabelId === annotation.id && annotation.display?.open && annotation.display?.editing;
        state.openTextLabelId = wasEditingOpen ? null : annotation.id;
        state.openCommentId = null;
        state.openSimulationTraceId = null;
        annotation.display = { ...(annotation.display || {}), open: !wasEditingOpen, editing: !wasEditingOpen };
        state.requestCommentSave?.();
        drawChart(backdrop, source, rows, layers, state);
        return;
      }
      const hitSimulationTrace = findSimulationTraceHit(state, px, py);
      if (hitSimulationTrace) {
        const traceEvent = hitSimulationTrace.event;
        const wasOpen = state.openSimulationTraceId === traceEvent.event_id;
        state.openSimulationTraceId = wasOpen ? null : traceEvent.event_id;
        state.openCommentId = null;
        state.openTextLabelId = null;
        traceEvent.display = { ...(traceEvent.display || {}), open: !wasOpen };
        drawChart(backdrop, source, rows, layers, state);
        return;
      }
      const hitComment = findCommentHit(state, px, py);
      if (hitComment) {
        const comment = hitComment.comment;
        const wasEditingOpen = state.openCommentId === comment.id && comment.display?.open && comment.display?.editing;
        state.openCommentId = wasEditingOpen ? null : comment.id;
        state.openSimulationTraceId = null;
        comment.display = { ...(comment.display || {}), open: !wasEditingOpen, editing: !wasEditingOpen };
        state.requestCommentSave?.();
        drawChart(backdrop, source, rows, layers, state);
        return;
      }

      // 点に対する HSI 起点追加・コメント追加は、右クリックメニュー経由に統一する。
      // 左クリックは十字カーソルの固定/解除だけに使用する。
      const panel = panelAt(px, py);
      if (!panel) return;
      const crosshair = ensureCrosshairState(state);
      if (crosshair.locked === true) {
        crosshair.locked = false;
        crosshair.visible = true;
      } else {
        const idx = getPanelRowIndexFromPoint(panel, px);
        if (idx == null) return;
        setCrosshairFromPanelPoint(state, panel, idx, py, true);
      }
      tooltip.style.opacity = '0';
      drawChart(backdrop, source, rows, layers, state);
    };

    canvas.ondblclick = event => {
      event.preventDefault();
      hideHsiContextMenu(backdrop);
      const bounds = canvas.getBoundingClientRect();
      const px = event.clientX - bounds.left;
      const py = event.clientY - bounds.top;
      const panel = panelAt(px, py);
      if (!panel) return;
      const idx = getPanelRowIndexFromPoint(panel, px);
      if (idx == null) return;
      const row = panel.rows[idx] || {};
      const timeMs = panelRowTimeMs(row);
      if (timeMs == null) return;
      const moved = state.syncWindowToTimeMs?.(timeMs, {
        sourcePanel: panelTimeframeLabel(panel, state),
        redrawNow: true
      });
      if (moved === false) {
        state.hoverTimeMs = timeMs;
        drawChart(backdrop, source, rows, layers, state);
      }
    };

    canvas.oncontextmenu = event => {
      event.preventDefault();
      const bounds = canvas.getBoundingClientRect();
      const px = event.clientX - bounds.left;
      const py = event.clientY - bounds.top;
      const cycleVerticalHit = findSavedCycleVerticalHit(state, px, py);
      if (cycleVerticalHit) {
        const marker = cycleVerticalHit.marker;
        showHsiContextMenu(backdrop, state, {
          kind: 'cycle-vertical-saved',
          clientX: event.clientX,
          clientY: event.clientY,
          title: `サイクル縦線 ${marker.label || circledNumber(marker.no)}`,
          meta: `${marker.time || '-'} / サイクル確認用の左右同期観測点`,
          onDeleteCycleVertical: async () => {
            state.cycleVerticalAnnotations = (state.cycleVerticalAnnotations || []).filter(x => x.id !== marker.id);
            if (state.commentSidecar) state.commentSidecar.cycle_vertical_annotations = state.cycleVerticalAnnotations;
            await state.requestCommentSave?.();
            redraw();
          }
        });
        return;
      }
      const verticalHit = findSavedVerticalHit(state, px, py);
      if (verticalHit) {
        const marker = verticalHit.marker;
        showHsiContextMenu(backdrop, state, {
          kind: 'vertical-saved',
          clientX: event.clientX,
          clientY: event.clientY,
          title: `保存縦線 ${marker.label || circledNumber(marker.no)}`,
          meta: `${marker.time || '-'} / 左右同期観測点`,
          onDeleteVertical: async () => {
            state.verticalAnnotations = (state.verticalAnnotations || []).filter(x => x.id !== marker.id);
            if (state.commentSidecar) state.commentSidecar.vertical_annotations = state.verticalAnnotations;
            await state.requestCommentSave?.();
            redraw();
          }
        });
        return;
      }
      const savedHit = findSavedHsiHit(state, px, py);
      if (savedHit) {
        const ann = savedHit.annotation;
        showHsiContextMenu(backdrop, state, {
          kind: 'saved',
          clientX: event.clientX,
          clientY: event.clientY,
          title: ann.title || '保存HSI',
          meta: `${ann.panel || 'M5'} / ${ann.time || '-'} / ${round3(ann.price)} / ×${formatHsiNumber(ann.hsi?.scale, 3)} ${normalizeHsiDirection(ann.hsi?.direction)}`,
          onDelete: async () => {
            if (savedHsiAnnotationMatchesCurrentAnchor(source, state, ann)) clearCurrentHsiAnchor(state);
            state.hsiAnnotations = (state.hsiAnnotations || []).filter(x => x.id !== ann.id);
            if (state.commentSidecar) state.commentSidecar.hsi_annotations = state.hsiAnnotations;
            await state.requestCommentSave?.();
            redraw();
          }
        });
        return;
      }
      const currentHit = findCurrentHsiAnchorHit(state, px, py);
      const currentPanel = currentHit ? (panelByKind.get(currentHit.panelKind) || null) : null;
      if (currentHit && currentPanel?.allowHsi && state.hsiAnchor && hsiAnchorMatchesPanel(state.hsiAnchor, currentHit.panelKind, state)) {
        const scale = numberOrNull(state.hsiScale) ?? getManualHsiSettings(source).scale;
        const panelName = panelKindToTimeframe(currentHit.panelKind, state);
        showHsiContextMenu(backdrop, state, {
          kind: 'current',
          clientX: event.clientX,
          clientY: event.clientY,
          title: '現在のHSI仮説',
          meta: `${panelName} / ${state.hsiAnchor.time || '-'} / ${round3(state.hsiAnchor.price)} / ×${formatHsiNumber(scale, 3)} ${normalizeHsiDirection(state.hsiDirection)}`,
          onSave: async () => {
            const ann = createSavedHsiAnnotationFromState(source, state, currentPanel);
            if (!ann) return;
            state.hsiAnnotations = [...(state.hsiAnnotations || []), ann];
            state.showSavedHsi = true;
            if (state.commentSidecar) state.commentSidecar.hsi_annotations = state.hsiAnnotations;
            await state.requestCommentSave?.();
            redraw();
          }
        });
        return;
      }

      const panel = panelAt(px, py);
      if (!panel) return;
      const idx = getPanelRowIndexFromPoint(panel, px);
      if (idx == null) return;
      const price = panel.max - ((py - panel.pad.top) / panel.plotH) * (panel.max - panel.min);
      const row = panel.rows[idx] || {};
      const panelName = panelTimeframeLabel(panel, state);
      showHsiContextMenu(backdrop, state, {
        kind: 'point',
        clientX: event.clientX,
        clientY: event.clientY,
        title: 'この点に追加',
        meta: `${panelName} / ${formatRowDateTime(rowTimeMs(row)) || row.datetime || '-'} / ${round3(price)}`,
        onOpenReference: panelName === 'M5' ? async () => {
          const referenceMs = rowTimeMs(row);
          if (referenceMs == null) return;
          state.simulationRunReferenceOverrideMs = referenceMs;
          state.simulationRunReferenceSource = 'm5_context_menu_reference';
          state.syncCenterTimeMs = referenceMs;
          state.hoverTimeMs = referenceMs;
          state.simulationRunDialogOpen = true;
          renderSimulationRunDialog(backdrop, state);
          applyModeButtonState(backdrop, state);
          redraw();
        } : null,
        onSaveHsiUp: async () => {
          if (!panel.allowHsi) return;
          state.hsiDirection = 'up';
          state.hsiAnchor = {
            index: idx,
            price,
            time: row.datetime || '',
            panel: panelName,
            timeframe: panelName,
            panelKind: panel.rect.kind
          };
          const ann = createSavedHsiAnnotationFromState(source, state, panel);
          if (!ann) return;
          state.hsiAnnotations = [...(state.hsiAnnotations || []), ann];
          state.showSavedHsi = true;
          if (state.commentSidecar) state.commentSidecar.hsi_annotations = state.hsiAnnotations;
          await state.requestCommentSave?.();
          clearCurrentHsiAnchor(state);
          redraw();
        },
        onSaveHsiDown: async () => {
          if (!panel.allowHsi) return;
          state.hsiDirection = 'down';
          state.hsiAnchor = {
            index: idx,
            price,
            time: row.datetime || '',
            panel: panelName,
            timeframe: panelName,
            panelKind: panel.rect.kind
          };
          const ann = createSavedHsiAnnotationFromState(source, state, panel);
          if (!ann) return;
          state.hsiAnnotations = [...(state.hsiAnnotations || []), ann];
          state.showSavedHsi = true;
          if (state.commentSidecar) state.commentSidecar.hsi_annotations = state.hsiAnnotations;
          await state.requestCommentSave?.();
          clearCurrentHsiAnchor(state);
          redraw();
        },
        onAddComment: async () => {
          state.showUserComments = true;
          const comment = createCommentFromPoint(source, state, panel, idx, price);
          comment.is_draft = true;
          state.comments.push(comment);
          if (state.commentSidecar) state.commentSidecar.comments = state.comments;
          state.openCommentId = comment.id;
          state.openSimulationTraceId = null;
          state.openTextLabelId = null;
          redraw();
        },
        onAddTextLabel: async () => {
          state.showUserComments = true;
          const annotation = createTextLabelFromPoint(source, state, panel, idx, price, 'Expansion');
          annotation.is_draft = true;
          state.textAnnotations.push(annotation);
          if (state.commentSidecar) state.commentSidecar.text_annotations = state.textAnnotations;
          state.openTextLabelId = annotation.id;
          state.openCommentId = null;
          state.openSimulationTraceId = null;
          redraw();
        },
        onSaveCycleVertical: async () => {
          const marker = createSavedCycleVerticalMarkerFromPanel(state, panel, idx);
          if (!marker) return;
          state.cycleVerticalAnnotations = [...(state.cycleVerticalAnnotations || []), marker];
          if (state.commentSidecar) state.commentSidecar.cycle_vertical_annotations = state.cycleVerticalAnnotations;
          await state.requestCommentSave?.();
          redraw();
        },
        onSaveVertical: async () => {
          const marker = createSavedVerticalMarkerFromPanel(state, panel, idx);
          if (!marker) return;
          state.verticalAnnotations = [...(state.verticalAnnotations || []), marker];
          if (state.commentSidecar) state.commentSidecar.vertical_annotations = state.verticalAnnotations;
          await state.requestCommentSave?.();
          redraw();
        }
      });
    };

    canvas.onmousemove = event => {
      const bounds = canvas.getBoundingClientRect();
      const bodyBounds = body.getBoundingClientRect();
      const px = event.clientX - bounds.left;
      const py = event.clientY - bounds.top;
      const panel = panelAt(px, py);
      const crosshair = ensureCrosshairState(state);
      if (!panel) {
        tooltip.style.opacity = '0';
        return;
      }
      if (crosshair.locked === true) {
        tooltip.style.opacity = '0';
        return;
      }
      const idx = getPanelRowIndexFromPoint(panel, px);
      if (idx == null) return;
      const row = panel.rows[idx];
      if (!row) return;
      const ms = panelRowTimeMs(row);
      setCrosshairFromPanelPoint(state, panel, idx, py, false);
      drawChart(backdrop, source, rows, layers, state);
      const pointLines = pointLinesFor(panel, idx);
      const title = panel.rect?.role === 'main'
        ? `${panelTimeframeLabel(panel, state)} main review`
        : (isUpperPanelKind(panel.rect.kind)
          ? `${panelTimeframeLabel(panel, state)} context`
          : 'M5 lower observation');
      tooltip.innerHTML = [
        `<strong>${title}</strong>`,
        `<strong>${row.datetime || ''}</strong>`,
        `Close: ${round3(row.close)}`,
        `High: ${round3(row.high)}`,
        `Low: ${round3(row.low)}`,
        `MA20: ${round3(row.ma20)}`,
        `T3: ${round3(row.t3_20_0_2)}`,
        `Close-T3: ${round3(row.close_t3_diff)}`,
        ...(panel.allowHsi && state.hsiAnchor && hsiAnchorMatchesPanel(state.hsiAnchor, panel.rect.kind, state) ? [
          `HSI anchor: ${round3(state.hsiAnchor.price)}`,
          `HSI values: ${parseHsiValues(state.hsiValuesText).join(',') || '-'} ×${formatHsiNumber(state.hsiScale ?? getManualHsiSettings(source).scale, 3)} ${normalizeHsiDirection(state.hsiDirection)}`
        ] : []),
        ...(state.showBollinger === true && panel.bollingerBands[idx] ? [
          `BB upper: ${round3(panel.bollingerBands[idx].upper)}`,
          `BB lower: ${round3(panel.bollingerBands[idx].lower)}`,
          `BB width: ${round3(panel.bollingerBands[idx].width)}`
        ] : []),
        ...pointLines
      ].filter(Boolean).join('<br>');
      // ガイダンスは、コメントを入れたい点やHSI起点を隠さないように、
      // 価格位置ではなくマウス位置を基準に少し上へ逃がす。
      // 上端に近い場合だけ下へ退避し、クリック対象そのものは常に見える状態を保つ。
      const mouseX = event.clientX - bodyBounds.left;
      const mouseY = event.clientY - bodyBounds.top;
      const tooltipLeft = Math.max(112, Math.min(bodyBounds.width - 112, mouseX));
      const placeBelow = mouseY < 150;
      tooltip.style.left = `${tooltipLeft}px`;
      tooltip.style.top = `${Math.max(18, Math.min(bodyBounds.height - 18, mouseY + (placeBelow ? 14 : -12)))}px`;
      tooltip.style.transform = placeBelow ? 'translate(-50%, 14px)' : 'translate(-50%, calc(-100% - 14px))';
      tooltip.style.opacity = '1';
    };
    canvas.onmouseleave = () => {
      tooltip.style.opacity = '0';
      const crosshair = ensureCrosshairState(state);
      if (crosshair.locked !== true) {
        crosshair.visible = false;
        crosshair.panelKind = '';
        crosshair.timeMs = null;
        crosshair.rowIndex = null;
        crosshair.price = null;
        state.hoverTimeMs = null;
      }
      drawChart(backdrop, source, rows, layers, state);
      if (state.simulationRunDialogOpen === true) renderSimulationRunDialog(backdrop, state);
    };

    renderTextLabelPopover(backdrop, state);
    renderCommentPopover(backdrop, state);
    renderSimulationTracePopover(backdrop, state);
    scroll.scrollLeft = 0;
  }

  function showFxChart(source, options = {}) {
    const allRows = normalizeAllRows(source);
    const windowSettings = getWindowSettings(source);
    const initialSettings = getDowBasisPointSettings(source);
    const hsiSettings = getManualHsiSettings(source);
    const upperSettings = getUpperTimeframeSettings(source);
    const layoutSettings = getChartLayoutSettings(source);
    const launchOptions = { ...chartOptionsFromLocation(), ...(options || {}) };
    const initialWindowSize = Math.max(windowSettings.min_size, Math.floor(numberOrNull(launchOptions.windowSize) ?? windowSettings.default_size));
    const focusTimeMs = parseDateTimeMs(launchOptions.focusTime);
    const focusPrice = numberOrNull(launchOptions.focusPrice);
    let initialWindowStart = numberOrNull(launchOptions.windowStart);
    if (initialWindowStart == null && focusTimeMs != null && allRows.length) {
      const focusIndex = nearestIndexForTime(allRows, focusTimeMs);
      if (focusIndex != null) initialWindowStart = clampWindowStart(focusIndex - Math.floor(initialWindowSize / 2), initialWindowSize, allRows.length);
    }
    const hasEntryFocus = focusTimeMs != null && focusPrice != null;
    const state = {
      widthMultiplier: launchOptions.widthMultiplier || 1,
      confirmBars: Math.max(3, Math.floor(numberOrNull(launchOptions.confirmBars) ?? initialSettings.confirm_bars)),
      viewMode: viewModeFromParam(launchOptions.viewMode, 'all'),
      showHighLowRange: launchOptions.showHighLowRange ?? true,
      showBollinger: launchOptions.showBollinger ?? false,
      windowSize: initialWindowSize,
      windowStart: initialWindowStart,
      chartLayout: normalizeChartLayout(launchOptions.chartLayout ?? layoutSettings.default_layout),
      upperTimeframe: normalizeUpperDisplayMode(launchOptions.upperTimeframe ?? upperSettings.default_timeframe),
      upperConfirmBars: Math.max(3, Math.floor(numberOrNull(launchOptions.upperConfirmBars) ?? upperSettings.confirm_bars)),
      upperWarmupBars: normalizeUpperWarmupBars(launchOptions.upperWarmupBars, upperSettings.warmup_bars),
      upperMapDataPath: normalizeUpperMapDataPath(launchOptions.upperMapDataPath || defaultUpperMapDataPath()),
      dayConfirmBars: Math.max(3, Math.floor(numberOrNull(launchOptions.dayConfirmBars) ?? getDayUpperMapSettings(source, null).confirm_bars)),
      weekConfirmBars: getWeekContextSettings().confirm_bars,
      dayConfirmBarsUrlOverride: numberOrNull(launchOptions.dayConfirmBars) != null,
      upperMapSource: null,
      upperMapAllRows: [],
      upperMapLoadStatus: 'loading',
      hoverTimeMs: hasEntryFocus ? focusTimeMs : null,
      crosshair: hasEntryFocus
        ? { visible: true, locked: true, panelKind: 'm5', timeMs: focusTimeMs, rowIndex: null, price: focusPrice }
        : { visible: false, locked: false, panelKind: '', timeMs: null, rowIndex: null, price: null },
      syncCenterTimeMs: focusTimeMs,
      syncCenterSourcePanel: hasEntryFocus ? 'm5' : '',
      entryFocus: hasEntryFocus ? {
        time: String(launchOptions.focusTime || ''),
        time_ms: focusTimeMs,
        price: focusPrice,
        trade_id: String(launchOptions.focusTradeId || ''),
        rule_lane: String(launchOptions.focusLane || ''),
        side: String(launchOptions.focusSide || '').toUpperCase(),
        row_id: String(launchOptions.focusRowId || ''),
        entry_event_id: String(launchOptions.focusEntryEventId || ''),
        exit_event_id: String(launchOptions.focusExitEventId || ''),
        batch_data_path: String(launchOptions.focusBatchData || '')
      } : null,
      entryFocusProjectionStatus: hasEntryFocus ? 'batch trade projection loading' : 'not requested',
      syncWindowToTimeMs: null,
      hsiValuesText: normalizeHsiValuesText(launchOptions.hsiValuesText ?? hsiSettings.valuesText),
      hsiScale: numberOrNull(launchOptions.hsiScale) ?? hsiSettings.scale,
      hsiDirection: normalizeHsiDirection(launchOptions.hsiDirection ?? hsiSettings.direction),
      hsiAnchor: launchOptions.hsiAnchor || null,
      commentMode: false,
      showUserComments: true,
      showSimulationComments: true,
      showMeta: false,
      showManualHsi: true,
      showAllComments: false,
      showAllSimulationComments: false,
      showSavedHsi: true,
      openCommentId: null,
      openSimulationTraceId: null,
      openTextLabelId: null,
      commentHitBoxes: [],
      simulationTraceHitBoxes: [],
      textLabelHitBoxes: [],
      savedHsiHitBoxes: [],
      savedVerticalHitBoxes: [],
      savedCycleVerticalHitBoxes: [],
      currentHsiAnchorHitBox: null,
      commentSaveStatus: 'sidecar loading',
      commentSidecar: buildEmptyCommentSidecar(source),
      simulationTrace: buildEmptySimulationTrace(source),
      simulationTraceEvents: [],
      simulationHsiAnnotations: [],
      simulationHsiHitBoxes: [],
      simulationTraceLoadStatus: 'trace loading',
      simulationSource: source,
      simulationAllRows: allRows,
      simulationRunDialogOpen: false,
      displaySettingsOpen: false,
      simulationRunDialogGeometry: null,
      simulationRunDialogPointer: null,
      simulationRunProfile: null,
      simulationRunProfileLoadStatus: 'loading',
      simulationReasonRuleCatalog: buildEmptySimulationReasonRuleCatalog(),
      simulationReasonRuleCatalogLoadStatus: 'loading',
      simulationRunDraft: null,
      simulationRunValidation: { valid: false, errors: ['Run Profile loading'], warnings: [] },
      simulationRunSnapshot: null,
      simulationRangeRunSnapshot: null,
      simulationRangeRunStatus: '未実行',
      simulationRangeRunInProgress: false,
      simulationRangeRunNoticeVisible: false,
      simulationRangeRunCursorMs: null,
      simulationRangeRunCursorStep: 0,
      simulationRangeRunCursorTotal: 0,
      simulationRangeRunLiveEventCount: 0,
      simulationRangeRunLastEventId: null,
      batchSimulationDialogOpen: false,
      batchSimulationDatasetCatalog: [],
      batchSimulationDatasetCatalogStatus: 'loading',
      batchSimulationDraft: null,
      batchSimulationValidation: { valid: false, errors: ['Batch設定未読込'], warnings: [] },
      batchSimulationRunSnapshot: null,
      batchSimulationRunStatus: '未実行',
      batchSimulationRunInProgress: false,
      batchSimulationStopRequested: false,
      batchSimulationProgress: null,
      batchSimulationPersistStatus: '',
      batchSimulationPersistErrors: [],
      batchSimulationPersistSavedPaths: [],
      simulationRunSnapshotStatus: '未作成',
      simulationRunReferenceOverrideMs: null,
      simulationRunReferenceSource: null,
      simulationHsiAnchorRegistrySnapshot: null,
      simulationTimeframeStateSnapshot: null,
      simulationUpperContextDecisionSnapshot: null,
      simulationTraceReplaySnapshot: null,
      simulationPositionLifecycleSnapshot: null,
      simulationTraceReplaySequence: null,
      simulationTraceReplayFocusEventId: null,
      simulationCandleSyncSnapshot: null,
      simulationCandleSourceCache: null,
      simulationSwingPointSnapshot: null,
      simulationDowTrendSnapshot: null,
      simulationCyclePositionSnapshot: null,
      comments: [],
      hsiAnnotations: [],
      verticalAnnotations: [],
      cycleVerticalAnnotations: [],
      textAnnotations: []
    };
    const backdrop = createModal(state);
    const modal = backdrop.querySelector('.gpt-fx-chart-modal');
    const scroll = backdrop.querySelector('[data-role="scroll"]');
    const wideButton = backdrop.querySelector('[data-action="toggle-wide"]');
    const confirmInput = backdrop.querySelector('[data-role="confirm-bars"]');
    const windowSizeInput = backdrop.querySelector('[data-role="window-size"]');
    const upperConfirmInput = backdrop.querySelector('[data-role="upper-confirm-bars"]');
    const upperWarmupInput = backdrop.querySelector('[data-role="upper-warmup-bars"]');
    const hsiValuesInput = backdrop.querySelector('[data-role="hsi-values"]');
    const hsiScaleInput = backdrop.querySelector('[data-role="hsi-scale"]');
    if (confirmInput) confirmInput.value = String(state.confirmBars);
    if (windowSizeInput) windowSizeInput.value = String(state.windowSize);
    if (upperConfirmInput) upperConfirmInput.value = String(state.upperConfirmBars);
    if (upperWarmupInput) upperWarmupInput.value = String(state.upperWarmupBars);
    if (hsiValuesInput) hsiValuesInput.value = state.hsiValuesText;
    if (hsiScaleInput) {
      hsiScaleInput.value = String(state.hsiScale);
      hsiScaleInput.step = String(hsiSettings.scaleStep);
    }
    if (state.widthMultiplier > 1) {
      modal.classList.add('is-wide');
    }

    buildLegend(backdrop);

    state.requestCommentSave = async () => await saveCommentSidecar(state, source, backdrop);

    loadUpperMapDataSource(state.upperMapDataPath).then(result => {
      state.upperMapSource = result.source;
      state.upperMapAllRows = normalizeRowsForTimeframeSource(result.source, 'DAY');
      if (!state.dayConfirmBarsUrlOverride) {
        state.dayConfirmBars = getDayUpperMapSettings(source, result.source).confirm_bars;
      }
      state.upperMapLoadStatus = `${result.from}:${state.upperMapAllRows.length.toLocaleString()} bars`;
      redraw();
    }).catch(err => {
      console.warn('[GPT FX Lab] upper map data load failed', err);
      state.upperMapSource = null;
      state.upperMapAllRows = [];
      if (!state.dayConfirmBarsUrlOverride) {
        state.dayConfirmBars = getDayUpperMapSettings(source, null).confirm_bars;
      }
      state.upperMapLoadStatus = 'fallback:M5-derived DAY';
      redraw();
    });

    const resolveCurrentWindowSize = () => Math.max(
      windowSettings.min_size,
      Math.floor(numberOrNull(windowSizeInput?.value) ?? state.windowSize ?? windowSettings.default_size)
    );

    const centerWindowStartForTime = (timeMs, windowSize) => {
      const idx = findIndexForTime(allRows, timeMs);
      if (idx == null) return null;
      return clampWindowStart(idx - Math.floor(windowSize / 2), windowSize, allRows.length);
    };

    state.syncWindowToTimeMs = (timeMs, options = {}) => {
      const n = numberOrNull(timeMs);
      if (n == null) return false;
      const currentSize = resolveCurrentWindowSize();
      const nextStart = centerWindowStartForTime(n, currentSize);
      state.windowSize = currentSize;
      if (windowSizeInput) windowSizeInput.value = String(currentSize);
      // Primary(M5)に該当時刻がある場合はM5窓も同期する。
      // ない場合でも UpperMap(DAY) 側の同期位置は表示したいので、syncCenterTimeMs は必ず残す。
      if (nextStart != null) state.windowStart = nextStart;
      state.syncCenterTimeMs = n;
      state.syncCenterSourcePanel = String(options.sourcePanel || '');
      state.hoverTimeMs = n;
      state.hsiAnchor = null;
      if (options.redrawNow !== false) redraw();
      return true;
    };

    const clearSyncCenter = () => {
      state.syncCenterTimeMs = null;
      state.syncCenterSourcePanel = '';
      state.hoverTimeMs = null;
    };

    const redraw = () => {
      const nextConfirm = Math.max(3, Math.floor(numberOrNull(confirmInput?.value) ?? state.confirmBars));
      state.confirmBars = nextConfirm;
      if (confirmInput) confirmInput.value = String(nextConfirm);
      const nextWindowSize = Math.max(windowSettings.min_size, Math.floor(numberOrNull(windowSizeInput?.value) ?? state.windowSize ?? windowSettings.default_size));
      state.windowSize = nextWindowSize;
      if (windowSizeInput) windowSizeInput.value = String(nextWindowSize);
      if (state.syncCenterTimeMs != null) {
        const centeredStart = centerWindowStartForTime(state.syncCenterTimeMs, nextWindowSize);
        if (centeredStart != null) state.windowStart = centeredStart;
      }
      const nextUpperConfirm = Math.max(3, Math.floor(numberOrNull(upperConfirmInput?.value) ?? state.upperConfirmBars ?? upperSettings.confirm_bars));
      state.upperConfirmBars = nextUpperConfirm;
      if (upperConfirmInput) upperConfirmInput.value = String(nextUpperConfirm);
      const nextUpperWarmup = normalizeUpperWarmupBars(upperWarmupInput?.value, state.upperWarmupBars ?? upperSettings.warmup_bars);
      state.upperWarmupBars = nextUpperWarmup;
      if (upperWarmupInput) upperWarmupInput.value = String(nextUpperWarmup);
      state.hsiValuesText = String(hsiValuesInput?.value ?? state.hsiValuesText ?? hsiSettings.valuesText);
      state.hsiScale = numberOrNull(hsiScaleInput?.value) ?? state.hsiScale ?? hsiSettings.scale;
      const batchSettings = batchSimulationSettings();
      const suppressChartRedraw = state.batchSimulationRunInProgress === true
        && batchSettings.suppress_chart_redraw_during_batch;
      applyModeButtonState(backdrop, state);
      if (!suppressChartRedraw) {
        const rows = getChartWindowRows(source, allRows, state);
        const candidatePoints = buildCandidatePoints(rows, source, state.confirmBars);
        const layers = buildPointLayers(candidatePoints);
        buildMeta(backdrop, source, rows, layers, state);
        drawChart(backdrop, source, rows, layers, state);
        renderVisibleRangeRunResult(backdrop, state);
        if (state.simulationRunDialogOpen === true) renderSimulationRunDialog(backdrop, state);
      }
      if (state.batchSimulationDialogOpen === true || state.batchSimulationRunInProgress === true) renderBatchSimulationDialog(backdrop, state);
    };

    state.redraw = redraw;
    state.batchSimulationDraft = buildEmptyBatchSimulationDraft(state);
    state.batchSimulationValidation = validateBatchSimulationDraft(state, state.batchSimulationDraft);

    const runBatchSimulation = async (mode = 'fresh') => {
      if (state.batchSimulationRunInProgress) return;
      const normalizedMode = String(mode || 'fresh').toLowerCase();
      const draft = cloneJsonValue(state.batchSimulationDraft || buildEmptyBatchSimulationDraft(state));
      const validation = validateBatchSimulationDraft(state, draft);
      state.batchSimulationValidation = validation;
      if (!validation.valid) {
        state.batchSimulationRunStatus = `一括Simulation開始不可: ${(validation.errors || []).join(' / ')}`;
        state.batchSimulationDialogOpen = true;
        renderBatchSimulationDialog(backdrop, state);
        return;
      }
      const existingBatchRun = normalizedMode === 'fresh' ? null : state.batchSimulationRunSnapshot;
      if (normalizedMode !== 'fresh' && !existingBatchRun) {
        state.batchSimulationRunStatus = '再開対象のBatch結果がありません。';
        renderBatchSimulationDialog(backdrop, state);
        return;
      }
      state.batchSimulationRunInProgress = true;
      state.batchSimulationStopRequested = false;
      if (normalizedMode === 'fresh') state.batchSimulationRunSnapshot = null;
      const existingSummary = existingBatchRun?.summary || {};
      state.batchSimulationProgress = {
        summary: cloneJsonValue(existingSummary || rangeExecutionSummary([])),
        cumulative_realized_profit_jpy: Number(existingSummary.realized_profit_jpy || 0),
        cumulative_unrealized_profit_jpy: Number(existingSummary.unrealized_profit_jpy || 0),
        cumulative_total_profit_jpy: Number(existingSummary.total_profit_jpy || 0),
        lane_summaries: cloneJsonValue(existingSummary.lane_summaries || {}),
        case_no: 0,
        case_total: validation.dataset_paths.length,
        case_progress: { current: 0, total: 0, execution_count: 0 }
      };
      state.batchSimulationPersistStatus = '';
      state.batchSimulationPersistErrors = [];
      state.batchSimulationPersistSavedPaths = [];
      state.batchSimulationRunStatus = normalizedMode === 'resume'
        ? '未完了Caseから再開しています…'
        : normalizedMode === 'retry_failed'
          ? '失敗Caseを再実行しています…'
          : '一括Simulationを開始しています…';
      state.batchSimulationDialogOpen = true;
      renderBatchSimulationDialog(backdrop, state);
      try {
        const result = await buildBatchSimulationRun(state, draft, progress => {
          state.batchSimulationProgress = progress;
          state.batchSimulationRunStatus = `Case ${progress.case_no}/${progress.case_total} / ${batchSimulationDatasetLabel(progress.dataset_path)} / ${progress.case_progress?.phase || ''} / ${progress.case_progress?.current || 0}/${progress.case_progress?.total || 0}足 / 評価損益 ${batchSimulationFormatJpy(progress.cumulative_total_profit_jpy)}`;
          renderBatchSimulationDialog(backdrop, state);
        }, { mode: normalizedMode, existing_batch_run: existingBatchRun });
        if (!result.batchRun) {
          state.batchSimulationRunStatus = `一括Simulation失敗: ${(result.validation?.errors || []).join(' / ') || '原因不明'}`;
          return;
        }
        state.batchSimulationRunSnapshot = result.batchRun;
        state.batchSimulationRunStatus = `${result.batchRun.status === 'stopped' ? '停止' : '完了'}: Case処理 ${result.batchRun.summary?.case_count || 0}/${validation.dataset_paths.length} / 完了 ${result.batchRun.summary?.completed_case_count || 0} / 停止 ${result.batchRun.summary?.stopped_case_count || 0} / Event ${result.batchRun.summary?.execution_event_count || 0} / 評価損益 ${batchSimulationFormatJpy(result.batchRun.summary?.total_profit_jpy)}`;
        if (draft.persist_results !== false) {
          state.batchSimulationPersistStatus = 'Batch成果物を保存中…';
          renderBatchSimulationDialog(backdrop, state);
          const persisted = await persistBatchSimulationRun(result.batchRun);
          state.batchSimulationPersistErrors = persisted.errors || [];
          state.batchSimulationPersistSavedPaths = persisted.saved_paths || [];
          state.batchSimulationPersistStatus = persisted.failed
            ? `自動保存失敗（${persisted.failed}経路）。完全版の結果JSONは手動ダウンロード可能です。`
            : `完全版JSON保存済: ${(persisted.saved_paths || []).join(' / ')}`;
        }
      } catch (err) {
        console.error('[GPT FX Lab] batch simulation failed', err);
        state.batchSimulationRunStatus = `一括Simulation例外: ${err?.message || err}`;
      } finally {
        state.batchSimulationRunInProgress = false;
        applyBatchSimulationVisualMode(backdrop, state);
        redraw();
      }
    };

    const runVisibleRangeSimulation = async () => {
      if (state.simulationRangeRunInProgress) return;
      if (!state.simulationRunProfile || state.simulationRunProfileLoadStatus === 'loading') {
        state.simulationRangeRunStatus = 'Run Profileの読込完了後に実行してください。';
        state.simulationRunDialogOpen = true;
        renderSimulationRunDialog(backdrop, state);
        applyModeButtonState(backdrop, state);
        return;
      }
      state.simulationRangeRunInProgress = true;
      state.simulationRangeRunNoticeVisible = true;
      state.simulationRangeRunStatus = '表示範囲の評価を開始しています…';
      state.simulationRunSnapshotStatus = state.simulationRangeRunStatus;
      state.simulationRangeRunCursorMs = null;
      state.simulationRangeRunCursorStep = 0;
      state.simulationRangeRunCursorTotal = 0;
      state.simulationRangeRunLiveEventCount = 0;
      state.simulationRangeRunLastEventId = null;
      // ライブ中継を遮らないよう、既存の判断ポップオーバーは必ず閉じる。
      state.openSimulationTraceId = null;
      state.showAllSimulationComments = false;
      (state.simulationTraceEvents || []).forEach(item => {
        item.display = { ...(item.display || {}), open: false };
      });
      // Human由来の注釈とHSIはSimulation専用表示と完全分離し、実行開始時に自動OFF。
      state.showUserComments = false;
      state.showSavedHsi = false;
      state.showManualHsi = false;
      state.openCommentId = null;
      state.openTextLabelId = null;
      state.simulationHsiAnnotations = [];
      state.simulationHsiHitBoxes = [];
      // 前回結果を残したままだと「今回いま発生したEvent」が分かりにくいので、
      // Range実行中は今回分だけをライブ投影し、完了時に正式結果へ置き換える。
      state.simulationTraceEvents = [];
      state.showSimulationComments = true;
      applyModeButtonState(backdrop, state);
      redraw();
      if (state.simulationRunDialogOpen === true) renderSimulationRunDialog(backdrop, state);
      const liveEventIds = new Set();
      try {
        const result = await buildVisibleRangeSimulationRun(state, progress => {
          state.simulationRangeRunStatus = `${progress.current} / ${progress.total} 足を評価中 / 実行Event ${progress.execution_count}件 / ${progress.reference_time || '-'}`;
          state.simulationRunSnapshotStatus = state.simulationRangeRunStatus;
          state.simulationRangeRunCursorMs = progress.reference_ms;
          state.simulationRangeRunCursorStep = progress.current;
          state.simulationRangeRunCursorTotal = progress.total;
          state.simulationRangeRunLiveEventCount = progress.execution_count;
          (progress.new_hsi_annotations || []).forEach(rawAnnotation => {
            const annotationId = String(rawAnnotation?.id || rawAnnotation?.anchor_id || '');
            if (!annotationId) return;
            (state.simulationHsiAnnotations || []).forEach(item => {
              item.display = { ...(item.display || {}), live_flash: false };
            });
            const annotation = cloneJsonValue(rawAnnotation);
            annotation.display = { ...(annotation.display || {}), visible: true, live_flash: true };
            if (!(state.simulationHsiAnnotations || []).some(item => String(item?.id || '') === annotationId)) {
              state.simulationHsiAnnotations = [...(state.simulationHsiAnnotations || []), annotation];
            }
          });
          (progress.updated_hsi_annotations || []).forEach(rawAnnotation => {
            const annotationId = String(rawAnnotation?.id || rawAnnotation?.anchor_id || '');
            if (!annotationId) return;
            state.simulationHsiAnnotations = (state.simulationHsiAnnotations || []).map(item =>
              String(item?.id || item?.anchor_id || '') === annotationId ? cloneJsonValue(rawAnnotation) : item
            );
          });
          (progress.new_execution_events || []).forEach(rawEvent => {
            const eventId = String(rawEvent?.event_id || '');
            if (!eventId || liveEventIds.has(eventId)) return;
            liveEventIds.add(eventId);
            // 直前EventのNEW強調を解除し、今生まれたEventだけを一瞬強く見せる。
            (state.simulationTraceEvents || []).forEach(item => {
              item.display = { ...(item.display || {}), live_flash: false };
            });
            const normalized = normalizeSimulationTrace({ events: [rawEvent] }, source).events[0];
            if (!normalized) return;
            normalized.display = {
              ...(normalized.display || {}),
              visible: true,
              open: false,
              pinned: false,
              live: true,
              live_flash: true,
              marker_label: simulationExecutionMarkerLabel(normalized)
            };
            state.simulationTraceEvents = [...(state.simulationTraceEvents || []), normalized];
            state.simulationRangeRunLastEventId = eventId;
          });
          applyModeButtonState(backdrop, state);
          renderVisibleRangeRunResult(backdrop, state);
          const statusNode = backdrop.querySelector('[data-role="visible-range-run-status"]');
          if (statusNode) statusNode.textContent = state.simulationRangeRunStatus;
          // 大窓では10足ごと、小窓では5足ごと。Event発生時は即時再描画する。
          const liveStride = progress.total > 600 ? 10 : 5;
          if (progress.current === 1
              || progress.current === progress.total
              || progress.current % liveStride === 0
              || (progress.new_execution_events || []).length > 0
              || (progress.new_hsi_annotations || []).length > 0
              || (progress.updated_hsi_annotations || []).length > 0) {
            redraw();
          }
        });
        state.simulationRunValidation = result.validation || state.simulationRunValidation;
        if (!result.rangeRun) {
          state.simulationRangeRunStatus = `表示範囲Simulation失敗: ${(result.validation?.errors || []).join(' / ') || '原因不明'}`;
          state.simulationRunSnapshotStatus = state.simulationRangeRunStatus;
          state.simulationRunDialogOpen = true;
          renderSimulationRunDialog(backdrop, state);
          return;
        }
        commitVisibleRangeSimulationRun(state, source, result.rangeRun);
        const summary = result.rangeRun.summary || {};
        state.simulationRangeRunStatus = `完了: Entry ${summary.entry_count || 0} / ReEntry ${summary.reentry_count || 0} / Add-on ${summary.add_on_count || 0} / CloseOK ${summary.close_ok_count || 0} / CloseMiss ${summary.close_miss_count || 0}`;
        state.simulationRunSnapshotStatus = `${state.simulationRangeRunStatus} / 保存中…`;
        redraw();
        const saved = await saveSimulationTraceSidecar(state, source, backdrop);
        state.simulationRunSnapshotStatus = `${state.simulationRangeRunStatus} / ${saved ? `保存済: ${getSimulationTraceFileName(source)}` : 'Trace Sidecar保存失敗'}`;
      } catch (err) {
        console.error('[GPT FX Lab] visible range simulation failed', err);
        state.simulationRangeRunStatus = `表示範囲Simulation例外: ${err?.message || err}`;
        state.simulationRunSnapshotStatus = state.simulationRangeRunStatus;
        state.simulationRunDialogOpen = true;
      } finally {
        state.simulationRangeRunInProgress = false;
        state.simulationRangeRunCursorMs = null;
        state.simulationRangeRunCursorStep = 0;
        state.simulationRangeRunCursorTotal = 0;
        (state.simulationTraceEvents || []).forEach(item => {
          item.display = { ...(item.display || {}), live: false, live_flash: false };
        });
        (state.simulationHsiAnnotations || []).forEach(item => {
          item.display = { ...(item.display || {}), live_flash: false };
        });
        redraw();
      }
    };

    loadCommentSidecar(source).then(sidecar => {
      state.commentSidecar = sidecar;
      state.comments = sidecar.comments || [];
      state.hsiAnnotations = sidecar.hsi_annotations || [];
      state.verticalAnnotations = sidecar.vertical_annotations || [];
      state.cycleVerticalAnnotations = sidecar.cycle_vertical_annotations || [];
      state.textAnnotations = sidecar.text_annotations || [];
      state.commentSaveStatus = `loaded:${sidecar._loaded_from || 'empty'} / ${getCommentSidecarFileName(source)}`;
      redraw();
    }).catch(err => {
      console.warn('[GPT FX Lab] comment sidecar load failed', err);
      state.commentSidecar = buildEmptyCommentSidecar(source);
      state.comments = state.commentSidecar.comments;
      state.hsiAnnotations = state.commentSidecar.hsi_annotations;
      state.verticalAnnotations = state.commentSidecar.vertical_annotations || [];
      state.cycleVerticalAnnotations = state.commentSidecar.cycle_vertical_annotations || [];
      state.textAnnotations = state.commentSidecar.text_annotations || [];
      state.commentSaveStatus = 'sidecar load failed';
      redraw();
    });

    loadSimulationTraceSidecar(source).then(async trace => {
      state.simulationTrace = trace;
      state.simulationTraceEvents = trace.events || [];
      state.simulationHsiAnnotations = cloneJsonValue((trace.simulation_hsi_annotations || []).length ? trace.simulation_hsi_annotations : (trace.range_run?.simulation_hsi_annotations || []));
      state.simulationTraceLoadStatus = `loaded:${trace._loaded_from || 'empty'} / ${getSimulationTraceFileName(source)}`;
      if (trace.run_snapshot && typeof trace.run_snapshot === 'object') {
        state.simulationRunSnapshot = cloneJsonValue(trace.run_snapshot);
        state.simulationRunSnapshotStatus = `読込済: ${trace.run_snapshot.run_id || 'snapshot'}`;
      }
      if (trace.range_run && typeof trace.range_run === 'object') {
        state.simulationRangeRunSnapshot = cloneJsonValue(trace.range_run);
        const summary = trace.range_run.summary || {};
        state.simulationRangeRunStatus = `読込済: Entry ${summary.entry_count || 0} / CloseOK ${summary.close_ok_count || 0} / CloseMiss ${summary.close_miss_count || 0}`;
      }
      await loadEntryFocusBatchProjection(state, source);
      renderSimulationRunDialog(backdrop, state);
      redraw();
    }).catch(err => {
      console.warn('[GPT FX Lab] simulation trace sidecar load failed', err);
      state.simulationTrace = buildEmptySimulationTrace(source);
      state.simulationTraceEvents = [];
      state.simulationHsiAnnotations = [];
      state.simulationTraceLoadStatus = 'trace load failed';
      loadEntryFocusBatchProjection(state, source).finally(() => redraw());
    });

    loadSimulationReasonRuleCatalog().then(catalog => {
      state.simulationReasonRuleCatalog = catalog;
      state.simulationReasonRuleCatalogLoadStatus = `loaded:${catalog._loaded_from || 'missing'} / ${catalog._catalog_file || getSimulationReasonRuleCatalogFileName()}`;
      redraw();
    }).catch(err => {
      console.warn('[GPT FX Lab] simulation reason/rule catalog load failed', err);
      state.simulationReasonRuleCatalog = buildEmptySimulationReasonRuleCatalog();
      state.simulationReasonRuleCatalogLoadStatus = 'load failed / fallback';
      redraw();
    });

    loadSimulationRunProfile().then(profile => {
      state.simulationRunProfile = profile;
      state.simulationRunDraft = simulationRunDraftFromProfile(profile);
      state.simulationRunValidation = validateSimulationRunDraft(state.simulationRunDraft);
      state.simulationRunProfileLoadStatus = `loaded:${profile._loaded_from || 'missing'} / ${profile._profile_file || getSimulationRunProfileFileName()}`;
      const existingSnapshot = state.simulationTrace?.run_snapshot;
      if (existingSnapshot && typeof existingSnapshot === 'object') {
        state.simulationRunSnapshot = cloneJsonValue(existingSnapshot);
        state.simulationRunSnapshotStatus = `読込済: ${existingSnapshot.run_id || 'snapshot'}`;
      }
      renderSimulationRunDialog(backdrop, state);
      redraw();
    }).catch(err => {
      console.warn('[GPT FX Lab] simulation run profile load failed', err);
      state.simulationRunProfile = buildEmptySimulationRunProfile();
      state.simulationRunDraft = simulationRunDraftFromProfile(state.simulationRunProfile);
      state.simulationRunValidation = validateSimulationRunDraft(state.simulationRunDraft);
      state.simulationRunProfileLoadStatus = 'load failed / no fallback';
      renderSimulationRunDialog(backdrop, state);
      redraw();
    });

    const hsiScaleStep = Math.max(0.000001, numberOrNull(hsiSettings.scaleStep) ?? 1);
    const normalizeScaleDisplay = value => {
      const n = Math.max(0, numberOrNull(value) ?? hsiSettings.scale);
      const rounded = Math.round(n * 1000000) / 1000000;
      return String(rounded);
    };
    const adjustHsiScale = delta => {
      const current = numberOrNull(hsiScaleInput?.value) ?? state.hsiScale ?? hsiSettings.scale;
      const next = current + delta * hsiScaleStep;
      if (hsiScaleInput) hsiScaleInput.value = normalizeScaleDisplay(next);
      redraw();
    };

    const shiftWindow = delta => {
      const currentSize = Math.max(windowSettings.min_size, Math.floor(numberOrNull(windowSizeInput?.value) ?? state.windowSize ?? windowSettings.default_size));
      const maxStart = Math.max(0, allRows.length - currentSize);
      const currentStart = clampWindowStart(state.windowStart, currentSize, allRows.length);
      state.windowStart = Math.max(0, Math.min(maxStart, currentStart + delta * currentSize));
      state.hsiAnchor = null;
      clearSyncCenter();
      redraw();
    };
    const shiftWindowByBars = deltaBars => {
      const currentSize = Math.max(windowSettings.min_size, Math.floor(numberOrNull(windowSizeInput?.value) ?? state.windowSize ?? windowSettings.default_size));
      const maxStart = Math.max(0, allRows.length - currentSize);
      const currentStart = clampWindowStart(state.windowStart, currentSize, allRows.length);
      const stepBars = Math.max(1, Math.floor(Math.abs(numberOrNull(deltaBars) ?? 100)));
      const direction = deltaBars < 0 ? -1 : 1;
      state.windowStart = Math.max(0, Math.min(maxStart, currentStart + direction * stepBars));
      state.hsiAnchor = null;
      clearSyncCenter();
      redraw();
    };
    const setRandomWindow = () => {
      const currentSize = Math.max(windowSettings.min_size, Math.floor(numberOrNull(windowSizeInput?.value) ?? state.windowSize ?? windowSettings.default_size));
      const maxStart = Math.max(0, allRows.length - currentSize);
      state.windowStart = maxStart <= 0 ? 0 : Math.floor(Math.random() * (maxStart + 1));
      state.hsiAnchor = null;
      clearSyncCenter();
      redraw();
    };
    const setLatestWindow = () => {
      const currentSize = Math.max(windowSettings.min_size, Math.floor(numberOrNull(windowSizeInput?.value) ?? state.windowSize ?? windowSettings.default_size));
      state.windowStart = Math.max(0, allRows.length - currentSize);
      state.hsiAnchor = null;
      clearSyncCenter();
      redraw();
    };

    backdrop.querySelector('[data-action="open-display-settings"]')?.addEventListener('click', () => {
      state.displaySettingsOpen = state.displaySettingsOpen !== true;
      applyModeButtonState(backdrop, state);
    });
    backdrop.querySelector('[data-action="close-display-settings"]')?.addEventListener('click', () => {
      state.displaySettingsOpen = false;
      applyModeButtonState(backdrop, state);
    });
    backdrop.querySelector('[data-action="redraw"]').addEventListener('click', redraw);
    confirmInput?.addEventListener('change', redraw);
    confirmInput?.addEventListener('keydown', event => {
      if (event.key === 'Enter') redraw();
    });
    windowSizeInput?.addEventListener('change', () => {
      state.hsiAnchor = null;
      clearSyncCenter();
      redraw();
    });
    windowSizeInput?.addEventListener('keydown', event => {
      if (event.key === 'Enter') {
        state.hsiAnchor = null;
        clearSyncCenter();
        redraw();
      }
    });
    upperConfirmInput?.addEventListener('change', redraw);
    upperConfirmInput?.addEventListener('keydown', event => {
      if (event.key === 'Enter') redraw();
    });
    upperWarmupInput?.addEventListener('change', redraw);
    upperWarmupInput?.addEventListener('keydown', event => {
      if (event.key === 'Enter') redraw();
    });
    backdrop.querySelectorAll('[data-upper-warmup-preset]').forEach(btn => {
      btn.addEventListener('click', () => {
        const preset = normalizeUpperWarmupBars(btn.getAttribute('data-upper-warmup-preset'), state.upperWarmupBars ?? upperSettings.warmup_bars);
        state.upperWarmupBars = preset;
        if (upperWarmupInput) upperWarmupInput.value = String(preset);
        state.hoverTimeMs = null;
        redraw();
      });
    });
    backdrop.querySelectorAll('[data-layout]').forEach(btn => {
      btn.addEventListener('click', () => {
        state.chartLayout = normalizeChartLayout(btn.getAttribute('data-layout'));
        state.hsiAnchor = null;
        state.hoverTimeMs = null;
        redraw();
      });
    });
    backdrop.querySelectorAll('[data-upper-tf]').forEach(btn => {
      btn.addEventListener('click', () => {
        state.upperTimeframe = normalizeUpperDisplayMode(btn.getAttribute('data-upper-tf'));
        // 上位足切替はM5実行レイアウト用。Expansion検討中に押した場合は、
        // 既存操作との互換性を優先して設定だけ保存し、レイアウトは勝手に変えない。
        state.hsiAnchor = null;
        state.hoverTimeMs = null;
        redraw();
      });
    });
    backdrop.querySelector('[data-action="window-older"]')?.addEventListener('click', () => shiftWindow(-1));
    backdrop.querySelector('[data-action="window-newer"]')?.addEventListener('click', () => shiftWindow(1));
    backdrop.querySelector('[data-action="window-random"]')?.addEventListener('click', setRandomWindow);
    backdrop.querySelector('[data-action="window-latest"]')?.addEventListener('click', setLatestWindow);
    backdrop.querySelectorAll('[data-mode]').forEach(btn => {
      btn.addEventListener('click', () => {
        state.viewMode = btn.getAttribute('data-mode') || 'all';
        redraw();
      });
    });
    backdrop.querySelectorAll('[data-confirm-preset]').forEach(btn => {
      btn.addEventListener('click', () => {
        const preset = Math.max(3, Math.floor(numberOrNull(btn.getAttribute('data-confirm-preset')) ?? state.confirmBars));
        state.confirmBars = preset;
        if (confirmInput) confirmInput.value = String(preset);
        redraw();
      });
    });
    backdrop.querySelector('[data-action="toggle-high-low-range"]')?.addEventListener('click', () => {
      state.showHighLowRange = state.showHighLowRange === false;
      redraw();
    });
    backdrop.querySelector('[data-action="toggle-bollinger"]')?.addEventListener('click', () => {
      state.showBollinger = state.showBollinger !== true;
      redraw();
    });
    hsiValuesInput?.addEventListener('change', redraw);
    hsiScaleInput?.addEventListener('change', redraw);
    [hsiValuesInput, hsiScaleInput].forEach(input => {
      input?.addEventListener('keydown', event => {
        if (event.key === 'Enter') redraw();
      });
    });
    backdrop.querySelector('[data-action="hsi-scale-up"]')?.addEventListener('click', event => {
      event.preventDefault();
      event.stopPropagation();
      adjustHsiScale(1);
    });
    backdrop.querySelector('[data-action="hsi-scale-down"]')?.addEventListener('click', event => {
      event.preventDefault();
      event.stopPropagation();
      adjustHsiScale(-1);
    });
    backdrop.querySelectorAll('[data-hsi-dir]').forEach(btn => {
      btn.addEventListener('click', () => {
        state.hsiDirection = normalizeHsiDirection(btn.getAttribute('data-hsi-dir'));
        redraw();
      });
    });
    backdrop.querySelector('[data-action="hsi-clear"]')?.addEventListener('click', () => {
      state.hsiAnchor = null;
      state.hoverTimeMs = null;
      redraw();
    });
    backdrop.querySelector('[data-action="toggle-saved-hsi"]')?.addEventListener('click', () => {
      const nextVisible = state.showSavedHsi === false && state.showManualHsi === false;
      state.showSavedHsi = nextVisible;
      state.showManualHsi = nextVisible;
      redraw();
    });
    backdrop.querySelector('[data-action="toggle-meta"]')?.addEventListener('click', () => {
      state.showMeta = state.showMeta !== true;
      applyModeButtonState(backdrop, state);
      redraw();
    });
    backdrop.querySelector('[data-action="copy-url"]')?.addEventListener('click', async event => {
      const button = event.currentTarget;
      const url = buildChartStateUrl(state);
      try {
        await copyTextToClipboard(url);
        if (button) {
          const original = button.textContent;
          button.textContent = 'URLコピー済';
          button.classList.add('is-active');
          setTimeout(() => {
            if (!document.body.contains(button)) return;
            button.textContent = original || 'URLコピー';
            button.classList.remove('is-active');
          }, 1400);
        }
      } catch (err) {
        console.error(err);
        if (button) {
          button.textContent = 'コピー失敗';
          setTimeout(() => {
            if (document.body.contains(button)) button.textContent = 'URLコピー';
          }, 1800);
        }
      }
    });
    backdrop.querySelector('[data-action="open-batch-simulation"]')?.addEventListener('click', async () => {
      state.batchSimulationDialogOpen = true;
      if (!state.batchSimulationDatasetCatalog?.length) {
        state.batchSimulationDatasetCatalogStatus = 'loading';
        renderBatchSimulationDialog(backdrop, state);
        try { await loadBatchSimulationDatasetCatalog(state); }
        catch (err) { state.batchSimulationDatasetCatalogStatus = `load failed:${err?.message || err}`; }
      }
      state.batchSimulationValidation = validateBatchSimulationDraft(state, state.batchSimulationDraft);
      renderBatchSimulationDialog(backdrop, state);
      applyModeButtonState(backdrop, state);
    });
    const batchDialog = backdrop.querySelector('[data-role="batch-simulation-dialog"]');
    batchDialog?.addEventListener('change', event => {
      if (!event.target?.matches?.('[data-batch-dataset-path], [data-batch-period-mode], [data-batch-period-from], [data-batch-period-to]')) return;
      readBatchSimulationDraftFromDialog(batchDialog, state);
      renderBatchSimulationDialog(backdrop, state);
    });
    batchDialog?.addEventListener('input', event => {
      if (!event.target?.matches?.('[data-batch-period-from], [data-batch-period-to]')) return;
      readBatchSimulationDraftFromDialog(batchDialog, state);
    });
    batchDialog?.addEventListener('click', async event => {
      const openCaseButton = event.target?.closest?.('[data-batch-open-case]');
      if (openCaseButton) {
        const caseId = openCaseButton.getAttribute('data-batch-open-case');
        const caseResult = (state.batchSimulationRunSnapshot?.cases || []).find(item => item.case_id === caseId);
        openBatchSimulationCaseOnChart(caseResult);
        return;
      }
      const action = event.target?.closest?.('[data-batch-action]')?.getAttribute('data-batch-action');
      if (!action) return;
      if (action === 'close') {
        if (state.batchSimulationRunInProgress) return;
        state.batchSimulationDialogOpen = false;
        renderBatchSimulationDialog(backdrop, state);
        applyModeButtonState(backdrop, state);
        return;
      }
      if (action === 'stop') {
        state.batchSimulationStopRequested = true;
        state.batchSimulationRunStatus = '停止要求を受け付けました。現在のM5足評価が終わり次第停止します…';
        renderBatchSimulationDialog(backdrop, state);
        return;
      }
      if (action === 'retry-save' && state.batchSimulationRunSnapshot) {
        state.batchSimulationPersistStatus = '完全版JSONの保存を再試行しています…';
        state.batchSimulationPersistErrors = [];
        renderBatchSimulationDialog(backdrop, state);
        const persisted = await persistBatchSimulationRun(state.batchSimulationRunSnapshot);
        state.batchSimulationPersistErrors = persisted.errors || [];
        state.batchSimulationPersistSavedPaths = persisted.saved_paths || [];
        state.batchSimulationPersistStatus = persisted.failed
          ? `保存再試行失敗（${persisted.failed}経路）。結果JSONの手動ダウンロードは利用可能です。`
          : `保存再試行成功: ${(persisted.saved_paths || []).join(' / ')}`;
        renderBatchSimulationDialog(backdrop, state);
        return;
      }
      if (action === 'download-json' && state.batchSimulationRunSnapshot) {
        downloadBatchSimulationArtifact(`${state.batchSimulationRunSnapshot.batch_run_id}.json`, JSON.stringify(state.batchSimulationRunSnapshot, null, 2), 'application/json;charset=utf-8');
        return;
      }
      if (action === 'download-csv' && state.batchSimulationRunSnapshot) {
        downloadBatchSimulationArtifact(`${state.batchSimulationRunSnapshot.batch_run_id}_summary.csv`, batchSimulationCsv(state.batchSimulationRunSnapshot), 'text/csv;charset=utf-8');
        return;
      }
      if (action === 'download-gate-json' && state.batchSimulationRunSnapshot) {
        const payload = state.batchSimulationRunSnapshot.normal_entry_gate_failures || {
          schema_version: 'fx_batch_normal_entry_gate_failures_v0_1',
          kind: 'fx_batch_normal_entry_gate_failures',
          rows: [],
          summary: batchSimulationNormalGateFailureSummary([])
        };
        downloadBatchSimulationArtifact(`${state.batchSimulationRunSnapshot.batch_run_id}_normal_entry_gate_failures.json`, JSON.stringify(payload, null, 2), 'application/json;charset=utf-8');
        return;
      }
      if (action === 'download-gate-csv' && state.batchSimulationRunSnapshot) {
        downloadBatchSimulationArtifact(`${state.batchSimulationRunSnapshot.batch_run_id}_normal_entry_gate_failures.csv`, batchSimulationNormalGateFailureCsv(state.batchSimulationRunSnapshot), 'text/csv;charset=utf-8');
        return;
      }
      if (action === 'start' || action === 'resume' || action === 'retry-failed') {
        readBatchSimulationDraftFromDialog(batchDialog, state);
        const mode = action === 'resume' ? 'resume' : action === 'retry-failed' ? 'retry_failed' : 'fresh';
        await runBatchSimulation(mode);
      }
    });
    backdrop.querySelector('[data-action="run-visible-range-simulation"]')?.addEventListener('click', async () => {
      await runVisibleRangeSimulation();
    });
    backdrop.querySelector('[data-role="visible-range-run-result"]')?.addEventListener('click', event => {
      if (!event.target?.closest?.('[data-action="close-visible-range-run-result"]')) return;
      state.simulationRangeRunNoticeVisible = false;
      renderVisibleRangeRunResult(backdrop, state);
    });
    backdrop.querySelector('[data-action="open-simulation-run-profile"]')?.addEventListener('click', () => {
      state.simulationRunReferenceOverrideMs = null;
      state.simulationRunReferenceSource = null;
      state.simulationRunDialogOpen = true;
      renderSimulationRunDialog(backdrop, state);
      applyModeButtonState(backdrop, state);
    });
    const simulationRunOverlay = backdrop.querySelector('[data-role="simulation-run-overlay"]');
    const simulationRunDialog = backdrop.querySelector('[data-role="simulation-run-dialog"]');
    simulationRunDialog?.addEventListener('pointerdown', event => {
      const resizeHandle = event.target?.closest?.('[data-run-resize-handle]');
      const dragHandle = event.target?.closest?.('[data-run-drag-handle]');
      if (!resizeHandle && !dragHandle) return;
      if (dragHandle && event.target?.closest?.('button, input, select, textarea, a')) return;
      const dialogRect = simulationRunDialog.getBoundingClientRect();
      const overlayRect = simulationRunOverlay?.getBoundingClientRect?.();
      if (!overlayRect) return;
      state.simulationRunDialogPointer = {
        pointer_id: event.pointerId,
        mode: resizeHandle ? 'resize-left' : 'drag',
        start_client_x: event.clientX,
        start_client_y: event.clientY,
        start_left: dialogRect.left - overlayRect.left,
        start_top: dialogRect.top - overlayRect.top,
        start_width: dialogRect.width,
        fixed_right: overlayRect.width - (dialogRect.left - overlayRect.left + dialogRect.width)
      };
      simulationRunDialog.setPointerCapture?.(event.pointerId);
      event.preventDefault();
      event.stopPropagation();
    });
    simulationRunDialog?.addEventListener('pointermove', event => {
      const pointer = state.simulationRunDialogPointer;
      if (!pointer || pointer.pointer_id !== event.pointerId || !simulationRunOverlay) return;
      const overlayRect = simulationRunOverlay.getBoundingClientRect();
      const dx = event.clientX - pointer.start_client_x;
      const dy = event.clientY - pointer.start_client_y;
      if (pointer.mode === 'resize-left') {
        const minimumWidth = Math.max(180, Math.min(440, overlayRect.width - 16));
        const rightEdge = overlayRect.width - pointer.fixed_right;
        const nextLeft = clampSimulationDialogValue(pointer.start_left + dx, 8, Math.max(8, rightEdge - minimumWidth));
        state.simulationRunDialogGeometry = {
          left: nextLeft,
          top: pointer.start_top,
          width: Math.max(minimumWidth, rightEdge - nextLeft)
        };
      } else {
        const width = Math.min(pointer.start_width, Math.max(1, overlayRect.width - 16));
        state.simulationRunDialogGeometry = {
          left: clampSimulationDialogValue(pointer.start_left + dx, 8, Math.max(8, overlayRect.width - width - 8)),
          top: clampSimulationDialogValue(pointer.start_top + dy, 8, Math.max(8, overlayRect.height - 96)),
          width
        };
      }
      applySimulationRunDialogGeometry(simulationRunOverlay, simulationRunDialog, state);
      event.preventDefault();
    });
    const finishSimulationRunDialogPointer = event => {
      const pointer = state.simulationRunDialogPointer;
      if (!pointer || pointer.pointer_id !== event.pointerId) return;
      try { simulationRunDialog.releasePointerCapture?.(event.pointerId); } catch { }
      state.simulationRunDialogPointer = null;
    };
    simulationRunDialog?.addEventListener('pointerup', finishSimulationRunDialogPointer);
    simulationRunDialog?.addEventListener('pointercancel', finishSimulationRunDialogPointer);
    simulationRunDialog?.addEventListener('input', event => {
      if (event.target?.matches?.('[data-trace-replay-range]')) {
        state.simulationTraceReplaySequence = Number(event.target.value || 0);
        const inspector = simulationRunDialog.querySelector('[data-role="trace-replay-inspector"]');
        if (inspector && state.simulationTraceReplaySnapshot) inspector.innerHTML = renderTraceReplayInspector(state.simulationTraceReplaySnapshot, state.simulationTraceReplaySequence);
        return;
      }
      if (!event.target?.matches?.('[data-run-confirm-bars]')) return;
      readSimulationRunDraftFromDialog(simulationRunDialog, state);
      updateSimulationRunValidationUi(simulationRunDialog, state);
      applyModeButtonState(backdrop, state);
    });
    simulationRunDialog?.addEventListener('click', async event => {
      const replayButton = event.target?.closest?.('[data-trace-replay-sequence]');
      if (replayButton) {
        state.simulationTraceReplaySequence = Number(replayButton.getAttribute('data-trace-replay-sequence') || 0);
        state.simulationTraceReplayFocusEventId = replayButton.getAttribute('data-trace-replay-event-id') || null;
        renderSimulationRunDialog(backdrop, state);
        return;
      }
      const action = event.target?.getAttribute?.('data-run-action');
      if (!action) return;
      if (action === 'close') {
        state.simulationRunDialogOpen = false;
        renderSimulationRunDialog(backdrop, state);
        return;
      }
      if (action === 'reset-window') {
        resetSimulationRunDialogGeometry(simulationRunOverlay, simulationRunDialog, state);
        return;
      }
      if (action === 'replay-prev' || action === 'replay-next') {
        const max = state.simulationTraceReplaySnapshot?.events?.length || 0;
        const current = Math.max(0, Math.min(max, Math.floor(numberOrNull(state.simulationTraceReplaySequence) ?? max)));
        state.simulationTraceReplaySequence = action === 'replay-prev' ? Math.max(0, current - 1) : Math.min(max, current + 1);
        renderSimulationRunDialog(backdrop, state);
        return;
      }
      if (action === 'range') {
        readSimulationRunDraftFromDialog(simulationRunDialog, state);
        await runVisibleRangeSimulation();
        return;
      }
      if (action === 'snapshot') {
        readSimulationRunDraftFromDialog(simulationRunDialog, state);
        const result = buildSimulationRunSnapshot(state);
        state.simulationRunValidation = result.validation;
        if (!result.snapshot) {
          updateSimulationRunValidationUi(simulationRunDialog, state);
          return;
        }
        state.simulationRunSnapshot = result.snapshot;
        state.simulationTrace = state.simulationTrace || buildEmptySimulationTrace(source);
        state.simulationTrace.run = {
          ...(state.simulationTrace.run || {}),
          run_id: result.snapshot.run_id,
          status: result.snapshot.status,
          rule_version: result.snapshot.profile.rule_version,
          profile_id: result.snapshot.profile.profile_id,
          profile_file: result.snapshot.profile.profile_file,
          phase: result.snapshot.phase,
          generated_at: result.snapshot.created_at,
          engine_enabled: true,
          decision_engine_enabled: true,
          trace_replay_engine_enabled: true,
          m5_trigger_engine_enabled: true,
          trade_execution_enabled: true,
          note: '上位足Decisionに従うM5仮想実行とCore/Add-on/Runnerの建玉LifecycleをTraceへ統合しました。リアル注文・資金管理は行いません。'
        };
        state.simulationTrace.run_profile = {
          profile_id: result.snapshot.profile.profile_id,
          profile_file: result.snapshot.profile.profile_file,
          loaded_from: result.snapshot.profile.loaded_from
        };
        state.simulationTrace.run_snapshot = result.snapshot;
        state.simulationTrace.cycle_position_evaluator = {
          evaluator_id: CYCLE_POSITION_EVALUATOR_ID,
          snapshot_path: 'run_snapshot.cycle_position_evaluation',
          full_state_change_events_path: 'run_snapshot.cycle_position_evaluation.state_change_events',
          chart_projection_policy: 'latest cycle state event per timeframe only',
          generated_event_source_type: SIMULATION_TRACE_SOURCE_TYPE,
          generated_by: CYCLE_POSITION_GENERATOR,
          action_permission: 'NOT_EVALUATED'
        };
        state.simulationTrace.hsi_anchor_registry_resolver = {
          registry_id: HSI_ANCHOR_REGISTRY_ID,
          resolver_id: HSI_ANCHOR_RESOLVER_ID,
          snapshot_path: 'run_snapshot.hsi_anchor_registry',
          lifecycle_event_path: 'run_snapshot.hsi_anchor_registry.lifecycle_events',
          chart_projection_policy: 'latest adopted HSI anchor per timeframe only',
          simulation_source_type: SIMULATION_HSI_ANCHOR_SOURCE_TYPE,
          human_saved_hsi_source_type: SAVED_HSI_SOURCE_TYPE,
          action_permission: 'NOT_EVALUATED'
        };
        state.simulationTrace.timeframe_state_builder = {
          builder_id: TIMEFRAME_STATE_BUILDER_ID,
          snapshot_path: 'run_snapshot.timeframe_states',
          state_event_path: 'run_snapshot.timeframe_states.state_events',
          chart_projection_policy: 'one current state summary per timeframe',
          data_sufficiency_policy: 'separate_from_market_state',
          action_permission: 'NOT_EVALUATED'
        };
        state.simulationTrace.upper_context_decision_engine = {
          engine_id: UPPER_CONTEXT_DECISION_ENGINE_ID,
          snapshot_path: 'run_snapshot.upper_context_decision',
          decision_event_path: 'run_snapshot.upper_context_decision.decision_events',
          chart_projection_policy: 'one current decision summary',
          no_trade_priority: true,
          week_direct_close: false,
          action_execution: 'NOT_EVALUATED'
        };
        state.simulationTrace.m5_execution_position_lifecycle = {
          engine_id: M5_EXECUTION_ENGINE_ID,
          snapshot_path: 'run_snapshot.position_lifecycle',
          decision_event_path: 'run_snapshot.position_lifecycle.decision_events',
          execution_event_path: 'run_snapshot.position_lifecycle.execution_events',
          execution_timeframe: 'M5',
          management_timeframe_cap: 'DAY',
          week_management_forbidden: true,
          real_order_output: 'FORBIDDEN'
        };
        state.simulationTrace.trace_replay_log = {
          engine_id: TRACE_REPLAY_ENGINE_ID,
          snapshot_path: 'run_snapshot.trace_replay',
          event_path: 'run_snapshot.trace_replay.events',
          checkpoint_path: 'run_snapshot.trace_replay.checkpoints',
          replay_method: 'nearest_checkpoint_then_apply_delta_patches',
          ui_language: 'ja',
          action_execution: 'NOT_EVALUATED'
        };
        state.simulationTrace.trace_replay = result.snapshot.trace_replay;
        state.simulationTrace.run_result = result.snapshot.run_result;
        state.simulationTraceReplaySnapshot = result.snapshot.trace_replay;
        state.simulationTraceReplaySequence = result.snapshot.trace_replay?.events?.length || 0;
        state.simulationTraceEvents = mergeM5ExecutionChartEvents(mergeUpperContextDecisionChartEvents(mergeTimeframeStateChartEvents(mergeHsiAnchorChartEvents(mergeCyclePositionChartEvents(mergeDowTrendChartEvents(mergeSwingChartEvents(state.simulationTraceEvents || state.simulationTrace.events || [], result.snapshot.swing_point_detection), result.snapshot.dow_trend_evaluation), result.snapshot.cycle_position_evaluation), result.snapshot.hsi_anchor_registry), result.snapshot.timeframe_states), result.snapshot.upper_context_decision), result.snapshot.position_lifecycle);
        state.simulationTrace.events = state.simulationTraceEvents;
        state.simulationTrace.run.observation_event_count = result.snapshot.swing_point_detection?.observation_events?.length || 0;
        state.simulationTrace.run.trend_state_change_event_count = result.snapshot.dow_trend_evaluation?.state_change_events?.length || 0;
        state.simulationTrace.run.cycle_state_change_event_count = result.snapshot.cycle_position_evaluation?.state_change_events?.length || 0;
        state.simulationTrace.run.hsi_anchor_lifecycle_event_count = result.snapshot.hsi_anchor_registry?.lifecycle_events?.length || 0;
        state.simulationTrace.run.timeframe_state_event_count = result.snapshot.timeframe_states?.state_events?.length || 0;
        state.simulationTrace.run.upper_context_decision_event_count = result.snapshot.upper_context_decision?.decision_events?.length || 0;
        state.simulationTrace.run.m5_trigger_decision_event_count = result.snapshot.position_lifecycle?.decision_events?.length || 0;
        state.simulationTrace.run.execution_event_count = result.snapshot.position_lifecycle?.execution_events?.length || 0;
        state.simulationTrace.run.open_position_count = result.snapshot.position_lifecycle?.run_result?.open_position_ids?.length || 0;
        state.simulationTrace.run.trace_replay_event_count = result.snapshot.trace_replay?.events?.length || 0;
        state.simulationTrace.run.trace_checkpoint_count = result.snapshot.trace_replay?.checkpoints?.length || 0;
        state.simulationTrace.run.trace_causal_edge_count = result.snapshot.trace_replay?.summary?.causal_edge_count || 0;
        state.simulationTrace.run.chart_projection_event_count = state.simulationTraceEvents.filter(event => [SHARED_SWING_POINT_GENERATOR, DOW_TREND_GENERATOR, CYCLE_POSITION_GENERATOR, HSI_ANCHOR_GENERATOR, TIMEFRAME_STATE_GENERATOR, UPPER_CONTEXT_DECISION_GENERATOR, M5_EXECUTION_GENERATOR].includes(event?.generated_by)).length;
        state.simulationRunSnapshotStatus = '保存中...';
        renderSimulationRunDialog(backdrop, state);
        const saved = await saveSimulationTraceSidecar(state, source, backdrop);
        state.simulationRunSnapshotStatus = saved
          ? `保存済: ${result.snapshot.run_id} / ${getSimulationTraceFileName(source)}`
          : `保存失敗: ${result.snapshot.run_id} / Trace Sidecar APIを確認`;
        renderSimulationRunDialog(backdrop, state);
        redraw();
      }
    });
    backdrop.querySelector('[data-action="toggle-user-comments"]')?.addEventListener('click', () => {
      state.showUserComments = state.showUserComments === false;
      if (state.showUserComments === false) {
        state.openCommentId = null;
        state.openTextLabelId = null;
      }
      redraw();
    });
    backdrop.querySelector('[data-action="toggle-simulation-comments"]')?.addEventListener('click', () => {
      state.showSimulationComments = state.showSimulationComments === false;
      if (state.showSimulationComments === false) {
        state.openSimulationTraceId = null;
        (state.simulationTraceEvents || []).forEach(traceEvent => {
          traceEvent.display = { ...(traceEvent.display || {}), open: false };
        });
      }
      redraw();
    });
    backdrop.querySelector('[data-action="comment-open-all"]')?.addEventListener('click', () => {
      state.showAllComments = state.showAllComments !== true;
      redraw();
    });
    backdrop.querySelector('[data-action="simulation-open-all"]')?.addEventListener('click', () => {
      state.showAllSimulationComments = state.showAllSimulationComments !== true;
      redraw();
    });
    backdrop.querySelector('[data-action="comment-close-all"]')?.addEventListener('click', async () => {
      state.showAllComments = false;
      state.showAllSimulationComments = false;
      state.openCommentId = null;
      state.openSimulationTraceId = null;
      state.openTextLabelId = null;
      (state.comments || []).forEach(comment => {
        comment.display = { ...(comment.display || {}), open: false, editing: false };
      });
      (state.textAnnotations || []).forEach(annotation => {
        annotation.display = { ...(annotation.display || {}), open: false, editing: false };
      });
      (state.simulationTraceEvents || []).forEach(traceEvent => {
        traceEvent.display = { ...(traceEvent.display || {}), open: false };
      });
      await state.requestCommentSave?.();
      redraw();
    });
    backdrop.querySelector('[data-action="comment-save"]')?.addEventListener('click', async event => {
      const button = event.currentTarget;
      const ok = await state.requestCommentSave?.();
      if (button) {
        const original = button.textContent;
        button.textContent = ok ? 'コメント保存済' : '一時保存済';
        button.classList.add('is-active');
        setTimeout(() => {
          if (!document.body.contains(button)) return;
          button.textContent = original || 'Userコメント保存';
          button.classList.remove('is-active');
        }, 1500);
      }
      redraw();
    });
    wideButton.addEventListener('click', () => {
      const wasWide = state.widthMultiplier > 1;
      state.widthMultiplier = wasWide ? 1 : 2.6;
      modal.classList.toggle('is-wide', !wasWide);
      setTimeout(redraw, 80);
    });
    backdrop.querySelector('[data-action="scroll-left"]')?.addEventListener('click', () => {
      // M5 window micro-scroll: move the data window itself, not the modal scrollbar.
      shiftWindowByBars(-100);
    });
    backdrop.querySelector('[data-action="scroll-right"]')?.addEventListener('click', () => {
      // M5 window micro-scroll: move the data window itself, not the modal scrollbar.
      shiftWindowByBars(100);
    });
    setTimeout(redraw, 0);

    const onResize = () => {
      if (!document.body.contains(backdrop)) {
        window.removeEventListener('resize', onResize);
        return;
      }
      redraw();
    };
    window.addEventListener('resize', onResize);
  }

  const plugin = {
    id: PLUGIN_ID,
    activate(studio) {
      pluginManifest = studio?.plugin?.manifest || studio?.plugin?.indexItem || null;
      studio.registerAction(ENTRY_CHART_URL_ACTION_ID, async (context = {}) => {
        const row = context.selectedRow || context.getSelectedRow?.() || null;
        const sourceData = context.getSourceData?.() || studio.getSourceData?.() || (typeof window !== 'undefined' ? window.sourceData : null);
        const navigation = navigateToEntryChart(row, { ...context, sourceData });
        return {
          message: `新しいタブでEntryチャートを開きます: ${navigation.entryTime} / ${navigation.lane || '-'} / ${navigation.entryPrice}`,
          status_kind: 'success',
          status_title: 'GPT FX Lab'
        };
      }, ['OpenSelectedFxEntryChart', 'OpenEntryChartUrl']);
      studio.registerAction(ACTION_ID, async (context = {}) => {
        const source = context.getSourceData?.() || studio.getSourceData?.() || window.sourceData;
        if (!source || typeof source !== 'object') {
          throw new Error('FXチャート用のJSONデータが読み込まれていません。');
        }
        const rows = normalizeRows(source);
        if (!rows.length) {
          throw new Error('$.display_sets.chart_latest_1000 に表示可能な行がありません。');
        }
        showFxChart(source, chartOptionsFromContext(context));
        return {
          message: `Dow候補/基準点チャートを表示しました（${rows.length.toLocaleString()}件）`,
          status_kind: 'success',
          status_title: 'GPT FX Lab'
        };
      }, ['OpenFxChartViewer', 'FxT3Chart', 'fx_chart', 'gpt_fx_lab.fx_chart']);
      scheduleAutoOpenFromUrl(studio);
    }
  };

  window.StudioOverlayPlugins = window.StudioOverlayPlugins || {};
  window.StudioOverlayPlugins[PLUGIN_ID] = plugin;
  if (typeof window.registerStudioPlugin === 'function') window.registerStudioPlugin(plugin);
})();
