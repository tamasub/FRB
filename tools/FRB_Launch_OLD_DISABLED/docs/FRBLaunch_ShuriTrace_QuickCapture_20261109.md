# 手裏剣が走らない現象の即時採取（Windowsを再起動する前に）

## 状況
- FRB Launchだけ再起動しても再現し、Windows再起動後は正常に戻る可能性がある。
- Windowsの再起動は診断ログ採取後にする。Launchの再起動は可能。
- この差分は観測のみ。手裏剣速度・ホイール閾値・GUI設定は変えない。

## 最短手順
1. FRB Launchをタスクトレイから完全終了する（**Windowsは再起動しない**）。
2. 差分ZIPをLaunchフォルダーへ上書き展開する。
3. `_run_windows.bat` でLaunchを起動する。既存のビルド済みEXEでは診断コードが反映されない場合がある。
4. Files Listで項目が多いフォルダー（例：`C:\Windows\System32`）を開く。スクロールバーを先頭付近にし、いつも手裏剣が発動するように同方向へ素早くホイール操作する。**発動したか／しなかったかを覚えておく**。
5. 余裕があればリスト中間位置でも同様に試す。Remoteの手裏剣操作が動くかも比較する。
6. Launchを完全終了して `export_shuriken_trace.bat` をダブルクリックする。
7. 出力された `FRBLaunch_ShuriTrace.zip` をChatGPTに添付し、現象（Files List／Remoteのどちらで動いたか）を簡単に伝える。

## ログ取得
`%LOCALAPPDATA%\FRBLaunch\shuriken_trace.log`（最大3 MB + ローテーション2世代）。ファイル名・フルパス・URLはログに出さず、入力イベント、ゲート判定、滑走タイマーの数値を記録する。

**重要:** `export_shuriken_trace.bat` はログが存在している必要がある。必ず診断版Launchを起動し、ホイールを動かしてから実行する。
