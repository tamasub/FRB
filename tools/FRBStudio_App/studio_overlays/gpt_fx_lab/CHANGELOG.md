# gpt_fx_lab CHANGELOG

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

