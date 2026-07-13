# Entry Result Rows Builder v0.1

Batch Simulationの `execution_events[]` を、**初回Entryから最終決済までを1行にした成績表**へ変換するNode.jsスクリプト。

## 生成するもの

元の `batch_*.json` は変更せず、同じフォルダへ次のSidecar JSONを作る。

```text
batch_20260712_230503.json
↓
batch_20260712_230503_entry_results.json
```

Sidecarの主データは次の配列。

```json
{
  "entry_result_rows": []
}
```

1行には、以下をまとめる。

- Entry日時・価格・方向・Rule Lane
- Entry理由コードと日本語説明
- Add-on回数・価格・単位・平均Entry価格
- 終了日時・価格・終了理由
- 成功 / 失敗 / 未決済
- 利益 / 損失 / 損益額
- Risk Multiple・保有時間

## 実行方法

FRB Studioのリポジトリルートで実行する。

```bat
node studio_overlays\gpt_fx_lab\simulation\tools\build_entry_result_rows_v0_1.cjs
```

またはWindows用ランチャー。

```bat
studio_overlays\gpt_fx_lab\simulation\tools\build_entry_result_rows_v0_1.cmd
```

入力ファイルを指定する場合。

```bat
node studio_overlays\gpt_fx_lab\simulation\tools\build_entry_result_rows_v0_1.cjs ^
  studio_overlays\gpt_fx_lab\simulattion_集計\batch_20260712_230503.json
```

フォルダを指定すると、その配下の `batch_*.json` を一括処理する。

```bat
node studio_overlays\gpt_fx_lab\simulation\tools\build_entry_result_rows_v0_1.cjs ^
  studio_overlays\gpt_fx_lab\simulattion_集計
```

## 成功・失敗の定義

```text
realized_profit_jpy > 0  → 成功 / 利益
realized_profit_jpy < 0  → 失敗 / 損失
realized_profit_jpy = 0  → 引分 / ±0
決済Eventなし           → 未決済 / 未確定
```

Target到達だけを成功扱いにはしない。Structural ExitやT3 Exitでも利益なら成功、Target Exitでも損失なら失敗として扱う。

## Trade結合キー

同じ `trade_id` が複数Rule Laneで使われる場合があるため、次の組合せでEntry・Add-on・Closeを結合する。

```text
case_id + rule_lane + trade_id
```

これにより、NORMALとEXPANSION_LITEのEventを誤結合しない。

## ViewDef

生成される `batch_*_entry_results.json` は、次のViewDefを参照します。

```text
overlay/gpt_fx_lab/view_defs/fx_batch_entry_results_view_def_v0_1.json
```

Entryごとの成功・失敗・損益・Entry理由・終了理由を一覧/詳細で確認できます。
