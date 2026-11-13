# Expansion v0.28 実装レポート

更新日: 2026-07-20  
APP: gpt_fx_lab.fx_chart_viewer v0.9.1.23

## 実装内容

- 未実装だった `EXPANSION` Rule Laneを独立実装。
- 観測単位を `H1 Dow Confirmation` とした。
- H1 Dow Confirmationのprevious Swingを固定H1 Anchorとして採用。
- Entry条件を次のとおり実装。
  - H1 Dow Confirmation
  - 固定H1 AnchorからR2到達
  - `H1 Low <= H1 T3 <= H1 High` による軽いT3 Touch
  - H4 CloseがEntry方向のT3側
  - Entry時M5 OpenがH1 T3のEntry方向側
- R2 / T3は同一Opportunity内で順不同に記憶。
- 同一H1 Confirmation足のR2 / T3事実を採用。
- 過去Entryを禁止し、全条件成立後の次M5 OpenでEntry。
- Opportunity終了条件を実装。
  - 反対H1 Dow Confirmation
  - H1 Closeによる固定Anchor崩壊
  - H1 Confirmationから14本超過
  - Entry成立
- Targetを固定H1 AnchorからR5へ設定。
- Expansion専用Closeを実装。
  - H1 Anchor Exit
  - 反対H1 Dow Exit
  - R5 Target Exit
  - H1 Close T3 Exit
- v0.1ではAdd-on / ReEntryを禁止。
- `NORMAL / EXPANSION / EXPANSION_LITE` 全3 Lane並列Profileを追加し、既定Profileへ設定。
- 既存Expansion-Lite v0.27は変更せず保護。

## 追加Profile

- `simulation/fx_simulation_run_profile_expansion_v0_1.json`
- `simulation/fx_simulation_run_profile_all_rule_lanes_v0_1.json`

## ルール文書

- `シュミレーションルール仮_v0.28.md`
- `シュミレーションルール要約_v0.28.md`

## テスト結果

```text
Test files: 29
Passed:     29
Failed:      0
```

主な確認:

- R2 / T3の順不同記憶
- 同一Confirmation足の事実採用
- 次M5 Open Entry / No Backdate
- H1 Anchor崩壊による候補破棄
- H1 T3 Exit / R5優先
- 3 Lane独立並列実行
- 実USDJPYデータ40本Smoke
  - Expansion Entry: `2025-10-30 07:04`
- Normal / Expansion-Lite / Batch / UIマーカー回帰

添付元ZIPに含まれていなかった `batch_20260712_230503.json` の固定実績値検証は任意化し、合成データによるEntry Result Builder検証とCLI検証は常時実行するよう修正した。

## 補足修正

- 実描画コードと不一致だったExecution Marker設定JSONを同期。
  - 通常Endpoint Radius: 3.1
  - Focused Endpoint Radius: 4.2
  - 通常横シフト: 32 / 12
  - Focused横シフト: 44 / 16
- 元ZIP時点で期待値が古かったLite固定範囲Smokeを、現行挙動へ同期。
  - 08:59 Lite Entry
  - 09:44 Lite Add-on + Normal Entry
