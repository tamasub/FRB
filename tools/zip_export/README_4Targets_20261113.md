# zip_export — 4対象を毎回一括バックアップ (2026-11-13)

## 適用

この差分ZIP内の `zip_export/` を `F:\FRB\tools\zip_export\` に上書きします（`F:\FRB\tools\` を展開の起点にしてください）。既存の `Export-FrbZip.log` は**変更・上書きしません**。バックアップ前に作業中のファイルを保存し、可能ならStudioやLaunchを終了してください。

## ボタン/バッチを1回実行したときの対象

| 元フォルダー | F: のZIP名 |
| --- | --- |
| `F:\FRB` | `FRB_backup_年月日時刻.zip` |
| `F:\FRB_docsExcel` | `FRB_docsExcel_backup_年月日時刻.zip` |
| `F:\FRB_Apps\FRB_Studio` | `FRB_Studio_backup_年月日時刻.zip` |
| `F:\FRB_Apps\FRB_Launch` | `FRB_Launch_backup_年月日時刻.zip` |

**毎回すべての4対象**を実行します。選択ダイアログは出しません。元フォルダーが1つでも欠けている場合はZIP作成前に停止します。旧来の `-SourcePath` / `-SourcePaths` はスクリプトを直接呼ぶ際の互換オプションとして残しています（通常の `.bat` は指定しません）。

- `F:\FRB_backups\` に4本のZIPをそれぞれ作成し、ZIP内部の全エントリーの展開・サイズを検証。
- Dドライブが接続されていれば `D:\FRB_backups\` に4本を複製、個々のSHA256一致を検証。
- Dが未接続でもFへの保存は実施。Dへの二重保存が失敗した場合はエラー扱い。
- `.git`, `bin`, `obj`, `node_modules`, `app_zip` など、従来の除外設定を引き続き適用。Studio独立後の `wwwroot/js/lib/mermaid` も対象外（別途復元スクリプトで再取得）。**Gitの管理履歴そのものはZIPに含めません**。
- `Export-FrbZip.log` はこれまでどおり追記。
- 既存の `.partial` があれば勝手に削除・上書きせず停止。

## まずDryRunで対象件数を確認

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "F:\FRB\tools\zip_export\Export-FrbZip.ps1" -DryRun
```

DryRunではZIPと二重コピーを作成しません（ログは追記されます）。4件とも対象として表示されたら、通常は `Export-FrbZip.bat` をダブルクリックします。

この環境ではWindows PowerShell 5.1による実機実行はできないため、**初回はDryRunを必須の確認手順**にしてください。
