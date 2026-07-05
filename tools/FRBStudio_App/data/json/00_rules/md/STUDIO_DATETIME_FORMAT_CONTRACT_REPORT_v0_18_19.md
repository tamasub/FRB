# STUDIO_DATETIME_FORMAT_CONTRACT_REPORT v0.18.19

## 目的

人間が見る日時を、Studio標準のJST人間可読形式へ統一する。

```text
2026-07-05_09:39:32
```

UTCの `Z` 表記、`+09:00` 付きISO、不要なミリ秒を、Generated At / Observed At / saved_at / updated_at などの人間表示へ直接出さない。

## 追加ルール

`frb_coding_constraints_data_v0_3.json` に以下を追加した。

```text
constitution_27
Studio日時表記契約
```

標準方針：

```text
人間表示: 2026-07-05_09:39:32
ファイル名: 20260705_093932
秒未満: 明示オプション時のみ
ISO形式: 外部連携・厳密な機械処理時のみ
```

## 共通化した部品

### Browser / Studio本体

```text
wwwroot/js/core/studio_datetime.js
```

提供関数：

```text
studioFormatDateTime()
studioFormatFileTimestamp()
studioFormatIsoJst()
```

### mjs Test Runner

```text
tests/responsibilities/lib/responsibility_datetime_utils.mjs
```

提供関数：

```text
toStudioDateTime()
toStudioFileTimestamp()
toStudioIsoJst()
```

### PowerShell

```text
tools/common/StudioLog.ps1
```

提供関数：

```text
Get-StudioNow
Format-StudioDateTime
Format-StudioFileTimestamp
Format-StudioIsoJst
```

### C# Backend

```text
Program.cs/Program.cs
```

提供関数：

```text
StudioNow()
FormatStudioDateTime()
FormatStudioFileTimestamp()
FormatStudioIsoJst()
```

## 主な修正箇所

- Markdown Export の `Exported At`
- mdViewer のコメントSidecar `created_at / updated_at`
- mdViewer の保存検査・バックアップ時刻
- Grid CSV Export のファイル名timestamp
- JSON別名保存ファイルtimestamp
- 検索条件保存 `saved_at`
- virtualData生成meta `generated_at`
- mjs responsibility expected actual/diff `generated_at / observed_at`
- PowerShell `Export-DiffToJson.ps1` の `generated_at`
- PowerShell `Repair-JsonMdUtf8ReadableText.ps1` のレポート `started_at / finished_at`
- PowerShell共通ログの行頭日時
- C# CommandProfile / TestRunner API返却の `started_at / finished_at`
- C# Markdown Sidecar正規化時の `updated_at`

## 確認

```text
node --check tests/responsibilities/lib/responsibility_datetime_utils.mjs
node --check tests/responsibilities/responsibility_expected_tests.mjs
node --check tests/qa/static/incident_prompt_copy_action_viewdef_static.test.mjs
node --check wwwroot/js/core/studio_datetime.js
```

OK。

```text
node tests/responsibilities/responsibility_expected_tests.mjs
```

結果は既知の意図的FAILを含むため `5/6 passed`。

出力確認：

```text
generated_at: 2026-07-05_09:57:20
observed_at: 2026-07-05_09:57:20
```

## 未実施

作業環境に `dotnet` がないため、C#ビルドは未実行。
