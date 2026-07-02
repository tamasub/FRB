# JSON UTF-8 Human Readable Save Report v0.9

## 対象

- phase: `v0.9-json-utf8-human-readable-save`
- incident: `studio_work_0018`

## 方針

Data JSON は Studioくんの原本であり、AIだけでなく人間も直接読む対象である。
そのため、保存時の日本語本文は `\uXXXX` へ過剰エスケープせず、UTF-8の日本語として保存する。

ただし、既存JSON全体の一括変換は今回の範囲外とし、保存処理と生成スクリプト側の再発防止を優先する。

## 実装

- `Program.cs` の `WriteJsonAsync` を `HumanReadableJsonOptions` に統一。
- `HumanReadableJsonOptions` は `JavaScriptEncoder.Create(UnicodeRanges.All)` を使用し、非ASCII日本語の過剰エスケープを避ける。
- `File.WriteAllTextAsync` は `UTF8Encoding(false)` を明示し、BOMなしUTF-8で保存する。
- `/api/data/{name}` と `/api/defs/{name}` のJSONレスポンスを `application/json; charset=utf-8` に明示。
- `Export-DiffToJson.ps1` は `ConvertTo-StudioReadableJson` 経由でJSON出力する。
- `StudioLog.ps1` に共通の `ConvertTo-StudioReadableJson` を追加し、ログ内JSONも日本語可読へ寄せる。

## 確認

- `data/json/01_main/studio_work_incident_data_v0_110_search_state_ui_policy_record_done.json` のJSON parse確認を実施。
- C#ビルド確認は、作業環境に `dotnet` CLI がないため未実行。
- 返却ZIPには更新ファイルのみを収録する。
- `wwwroot/data` / `wwwroot/defs` の公開用静的コピーは更新しない。

## 注意

PowerShell 実行環境がこの作業環境にないため、`Export-DiffToJson.ps1` / `StudioLog.ps1` は静的確認のみ。
Windows PowerShell 5.1での実機確認では、日本語を含む差分JSONを生成し、本文に `\uXXXX` が残らないことを確認する。
