# FRB Launch 手裏剣スクロール・実機診断版（2026-11-09）

## 方針
- **診断ログを加えるだけ**。手裏剣自動起動の各閾値、滑走速度、スクロールバー処理、エリアジャンプ無効化、UI設定は変更していません。
- **まだ修正版ではありません**。原因を推測してパラメータを追加変更することは避けています。
- PySide6 の Windows 上の入力はこの環境で実際に操作できないため、所長の実機ログを取ります。

## 使い方
1. 同梱のソースで、普段どおり `_run_windows.bat` から Launch を起動。
2. **Files List を表示し、スクロールバーがある状態**で、次の4パターンを順に実施。ひとつのケースで数秒間ぐりぐりし、実際に手裏剣が動いたかをメモしてください。
   - A: `C:\Windows\System32`（約4,700件）の**先頭50行以内**。下方向へぐりぐり。
   - B: 同フォルダーの**スクロールバー中間付近**。下方向へぐりぐり。
   - C: 同フォルダーの**最終行付近**。上方向へぐりぐり。
   - D: `C:\Users\...\Downloads`（約300件）の**中間付近**。下方向へぐりぐり。
3. Launchを**完全終了**（トレイアイコンから終了）。
4. `export_shuriken_trace.bat` をダブルクリック。ソースと同じフォルダーに **`FRBLaunch_ShuriTrace.zip`** を生成します。既存の同名ZIPは上書きされます。
5. 生成した `FRBLaunch_ShuriTrace.zip` をチャットに添付し、A〜Dで走ったか、スピードがどうだったか教えてください。

診断ログ本体は `%LOCALAPPDATA%\FRBLaunch\shuriken_trace.log`。最大3MB、旧ログは最大2世代のローテートです。**既存の `error.log` や設定JSONは触れません**。ログにはファイル名やURL、フォルダーのフルパスは出力しません。

## 記録する情報（JSON Lines）

| event | 意味 |
|---|---|
| `list_wheel` | Files List が受け取ったホイールの角度／ピクセル差分、ノッチ換算、スクロール位置、全行数 |
| `list_wheel_hybrid` | 通常ハイブリッドに渡った入力とバー移動量 |
| `input_target` / `input_no_target` | 入力が手裏剣判定へ進めたか、対象Listが存在したか |
| `gate_result` / `gate_reject` / `gate_reset` | 継続回転のイベント数・ノッチ数・時間・レート・起動判定・クールダウン |
| `input_gate_fired` | 高速回転判定の成立 |
| `start_request` / `start_plan` / `start_reject` | 既存手裏剣へ起動を依頼したか、滑走計画が成立したか（残距離、計画時間） |
| `flight_begin` | 実際に滑走を始めた時点のスクロール範囲／入力速度 |
| `flight_tick` | 約350msごとの実際のスクロール移動と時間・速度倍率 |
| `flight_arrival` / `flight_interrupted` / `flight_finish` | 到達、途中中断、完了 |

**注意:** 長い操作のあとに新規のログがない場合は、ホイール入力自体がこの経路に来ていない可能性を疑います。出力が多すぎる場合は `src/shuriken_trace.py` の `SHURIKEN_TRACE_ENABLED = False` でOFFにできます。公開用に戻すときは、この診断機能ごと外す予定です。
