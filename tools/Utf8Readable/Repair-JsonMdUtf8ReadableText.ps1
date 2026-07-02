<#
.SYNOPSIS
  FRB Studio 用: .json / .md の Unicode escape 化された日本語を検出し、UTF-8可読文字へ戻す。

.DESCRIPTION
  - 既定ではスキャンのみ。
  - -Fix を付けると、非ASCII文字の \uXXXX を実文字へ一括変換する。
  - JSONファイルは変換後に ConvertFrom-Json で検証し、壊れる場合は書き戻さない。
  - true mojibake（例: ãã / 縺薙ｌ / �）は既定では抽出のみ。
  - -RepairMojibake を付けると、明らかに改善する行だけを慎重に修復する。

.USAGE
  # まず検出だけ
  .\Repair-JsonMdUtf8ReadableText.ps1 -Root "F:\FRB\tools\FRBStudio_App"

  # Unicode escape を修復し、バックアップも残す
  .\Repair-JsonMdUtf8ReadableText.ps1 -Root "F:\FRB\tools\FRBStudio_App" -Fix -Backup

  # 文字化け疑い行も、改善判定できるものだけ修復
  .\Repair-JsonMdUtf8ReadableText.ps1 -Root "F:\FRB\tools\FRBStudio_App" -Fix -Backup -RepairMojibake
#>

param(
    [string]$Root = ".",
    [string[]]$Extensions = @(".json", ".md"),
    [switch]$Fix,
    [switch]$Backup,
    [switch]$RepairMojibake,
    [string]$ReportPath = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

try {
    [System.Text.Encoding]::RegisterProvider([System.Text.CodePagesEncodingProvider]::Instance)
}
catch {
    # Windows PowerShell 5.1 では不要。PowerShell 7 では存在する場合のみ登録する。
}

$ScriptStartedAt = Get-Date
$Timestamp = $ScriptStartedAt.ToString("yyyyMMdd_HHmmss")
$Utf8NoBomStrict = New-Object System.Text.UTF8Encoding($false, $true)
$Utf8NoBomWrite = New-Object System.Text.UTF8Encoding($false)

if ([string]::IsNullOrWhiteSpace($ReportPath)) {
    $ReportPath = Join-Path (Resolve-Path $Root).Path ("encoding_escape_scan_report_{0}.json" -f $Timestamp)
}

$ResolvedRoot = (Resolve-Path $Root).Path

# runtime / dependency / VCS 系は原則対象外
$ExcludeDirNames = @(
    ".git",
    ".vs",
    "node_modules",
    "bin",
    "obj",
    "playwright-report",
    "test-results",
    "test_results",
    ".runtime",
    "tests_screen_state"
)

# 非ASCIIのUnicode escapeのみを対象にする。
# ASCII escape（\n, \", \\ はもちろん、\u005c 等）まで雑に戻すとJSON構文を壊す可能性があるため。
function Test-NonAsciiUnicodeEscape {
    param([string]$Text)

    foreach ($m in [regex]::Matches($Text, '(?<!\\)\\u([0-9a-fA-F]{4})')) {
        $code = [Convert]::ToInt32($m.Groups[1].Value, 16)
        if ($code -ge 128) {
            return $true
        }
    }
    return $false
}

function Count-NonAsciiUnicodeEscape {
    param([string]$Text)

    $count = 0
    foreach ($m in [regex]::Matches($Text, '(?<!\\)\\u([0-9a-fA-F]{4})')) {
        $code = [Convert]::ToInt32($m.Groups[1].Value, 16)
        if ($code -ge 128) {
            $count++
        }
    }
    return $count
}

function Convert-NonAsciiUnicodeEscapes {
    param([string]$Text)

    $pattern = '(?<!\\)(?:\\u[0-9a-fA-F]{4})+'

    return [regex]::Replace($Text, $pattern, {
        param($Match)

        $units = [regex]::Matches($Match.Value, '(?<!\\)\\u([0-9a-fA-F]{4})')
        $sb = New-Object System.Text.StringBuilder
        $changed = $false

        foreach ($unit in $units) {
            $hex = $unit.Groups[1].Value
            $code = [Convert]::ToInt32($hex, 16)

            if ($code -ge 128) {
                [void]$sb.Append([char]$code)
                $changed = $true
            }
            else {
                # JSON構文を壊す可能性があるASCII escapeは戻さない
                [void]$sb.Append($unit.Value)
            }
        }

        if ($changed) {
            return $sb.ToString()
        }

        return $Match.Value
    })
}

# 典型的なUTF-8誤デコード系の文字化けを疑う。
# これは検出優先。自動修復は -RepairMojibake 指定時のみ。
$script:MojibakePattern = '�|ã.|Â.|縺|繧|荳|譁|蜷|邱|鬆|驥|菴|莨|螟|逕|蜿|螳|隕|髫|譌'

function Count-MojibakeSuspects {
    param([string]$Text)
    return ([regex]::Matches($Text, $script:MojibakePattern)).Count
}

function Count-JapaneseChars {
    param([string]$Text)
    return ([regex]::Matches($Text, '[\p{IsHiragana}\p{IsKatakana}\p{IsCJKUnifiedIdeographs}]')).Count
}

function Try-RepairMojibakeLine {
    param([string]$Line)

    $beforeSuspicious = Count-MojibakeSuspects $Line
    if ($beforeSuspicious -eq 0) {
        return $Line
    }

    $beforeJapanese = Count-JapaneseChars $Line
    $candidates = New-Object System.Collections.Generic.List[object]

    foreach ($codepage in @(1252, 932)) {
        try {
            $sourceEncoding = [System.Text.Encoding]::GetEncoding($codepage)
            $bytes = $sourceEncoding.GetBytes($Line)
            $fixed = [System.Text.Encoding]::UTF8.GetString($bytes)

            $afterSuspicious = Count-MojibakeSuspects $fixed
            $afterJapanese = Count-JapaneseChars $fixed

            $candidates.Add([pscustomobject]@{
                CodePage = $codepage
                Text = $fixed
                BeforeSuspicious = $beforeSuspicious
                AfterSuspicious = $afterSuspicious
                BeforeJapanese = $beforeJapanese
                AfterJapanese = $afterJapanese
            })
        }
        catch {
            # 候補生成不可なら無視
        }
    }

    $best = $candidates |
        Where-Object {
            $_.AfterSuspicious -lt $_.BeforeSuspicious -and
            $_.AfterJapanese -ge $_.BeforeJapanese -and
            $_.Text -ne $Line
        } |
        Sort-Object AfterSuspicious, @{Expression = "AfterJapanese"; Descending = $true} |
        Select-Object -First 1

    if ($null -ne $best) {
        return $best.Text
    }

    return $Line
}

function Repair-MojibakeLines {
    param([string]$Text)

    $lines = $Text -split "(`r`n|`n|`r)", 0, "Multiline"
    $sb = New-Object System.Text.StringBuilder

    for ($i = 0; $i -lt $lines.Count; $i++) {
        $part = $lines[$i]

        # split結果には区切りも含めるため、改行トークンはそのまま戻す
        if ($part -eq "`r`n" -or $part -eq "`n" -or $part -eq "`r") {
            [void]$sb.Append($part)
        }
        else {
            [void]$sb.Append((Try-RepairMojibakeLine $part))
        }
    }

    return $sb.ToString()
}

function Get-Samples {
    param(
        [string]$Text,
        [int]$MaxSamples = 8
    )

    $samples = New-Object System.Collections.Generic.List[object]
    $lines = $Text -split "`r?`n"

    for ($i = 0; $i -lt $lines.Count; $i++) {
        $line = $lines[$i]
        $hasUnicode = Test-NonAsciiUnicodeEscape $line
        $hasMojibake = (Count-MojibakeSuspects $line) -gt 0

        if ($hasUnicode -or $hasMojibake) {
            $converted = Convert-NonAsciiUnicodeEscapes $line
            if ($RepairMojibake) {
                $converted = Try-RepairMojibakeLine $converted
            }

            $samples.Add([pscustomobject]@{
                line = $i + 1
                kind = (@(
                    $(if ($hasUnicode) { "unicode_escape" }),
                    $(if ($hasMojibake) { "mojibake_suspect" })
                ) | Where-Object { $_ })
                before = if ($line.Length -gt 220) { $line.Substring(0, 220) + "..." } else { $line }
                after = if ($converted.Length -gt 220) { $converted.Substring(0, 220) + "..." } else { $converted }
            })
        }

        if ($samples.Count -ge $MaxSamples) {
            break
        }
    }

    return $samples
}


function Get-FrbRelativePath {
    param(
        [string]$BasePath,
        [string]$TargetPath
    )

    $baseFull = [System.IO.Path]::GetFullPath($BasePath)
    $targetFull = [System.IO.Path]::GetFullPath($TargetPath)

    if (-not $baseFull.EndsWith([System.IO.Path]::DirectorySeparatorChar)) {
        $baseFull = $baseFull + [System.IO.Path]::DirectorySeparatorChar
    }

    $baseUri = New-Object System.Uri($baseFull)
    $targetUri = New-Object System.Uri($targetFull)
    $relativeUri = $baseUri.MakeRelativeUri($targetUri)

    return [System.Uri]::UnescapeDataString($relativeUri.ToString()).Replace('/', [System.IO.Path]::DirectorySeparatorChar)
}

function Test-IsExcludedPath {
    param([string]$FullName)

    $relative = Get-FrbRelativePath -BasePath $ResolvedRoot -TargetPath $FullName
    $parts = $relative -split '[\\/]+'

    foreach ($part in $parts) {
        if ($ExcludeDirNames -contains $part) {
            return $true
        }
    }

    return $false
}

$extensionsLower = $Extensions | ForEach-Object { $_.ToLowerInvariant() }
$targetFiles = @(Get-ChildItem -Path $ResolvedRoot -Recurse -File |
    Where-Object {
        ($extensionsLower -contains $_.Extension.ToLowerInvariant()) -and
        -not (Test-IsExcludedPath $_.FullName)
    })

$results = New-Object System.Collections.Generic.List[object]
$fixedCount = 0
$skippedInvalidJsonCount = 0
$decodeErrorCount = 0

foreach ($file in $targetFiles) {
    $relativePath = Get-FrbRelativePath -BasePath $ResolvedRoot -TargetPath $file.FullName
    $bytes = [System.IO.File]::ReadAllBytes($file.FullName)

    try {
        $text = $Utf8NoBomStrict.GetString($bytes)
    }
    catch {
        $decodeErrorCount++
        $results.Add([pscustomobject]@{
            path = $relativePath
            extension = $file.Extension
            status = "decode_error"
            unicode_escape_count = 0
            mojibake_suspect_count = 0
            fixed = $false
            message = "UTF-8として読めません。CP932等の可能性があります。手動確認してください。"
            samples = @()
        })
        continue
    }

    $unicodeCount = Count-NonAsciiUnicodeEscape $text
    $mojibakeCount = Count-MojibakeSuspects $text
    $needsFix = ($unicodeCount -gt 0) -or ($RepairMojibake -and $mojibakeCount -gt 0)
    $samples = Get-Samples -Text $text

    $status = "ok"
    $wasFixed = $false
    $message = ""

    if ($unicodeCount -gt 0 -or $mojibakeCount -gt 0) {
        $status = "found"
    }

    if ($Fix -and $needsFix) {
        $newText = Convert-NonAsciiUnicodeEscapes $text

        if ($RepairMojibake) {
            $newText = Repair-MojibakeLines $newText
        }

        if ($newText -ne $text) {
            $jsonValid = $true
            if ($file.Extension -ieq ".json") {
                try {
                    $null = $newText | ConvertFrom-Json -ErrorAction Stop
                }
                catch {
                    $jsonValid = $false
                    $skippedInvalidJsonCount++
                    $status = "skip_invalid_json_after_fix"
                    $message = $_.Exception.Message
                }
            }

            if ($jsonValid) {
                if ($Backup) {
                    $backupPath = "{0}.bak_{1}" -f $file.FullName, $Timestamp
                    [System.IO.File]::Copy($file.FullName, $backupPath, $true)
                }

                [System.IO.File]::WriteAllText($file.FullName, $newText, $Utf8NoBomWrite)
                $fixedCount++
                $wasFixed = $true
                $status = "fixed"
            }
        }
    }

    if ($unicodeCount -gt 0 -or $mojibakeCount -gt 0 -or $wasFixed) {
        $results.Add([pscustomobject]@{
            path = $relativePath
            extension = $file.Extension
            status = $status
            unicode_escape_count = $unicodeCount
            mojibake_suspect_count = $mojibakeCount
            fixed = $wasFixed
            message = $message
            samples = $samples
        })
    }
}

$summary = [pscustomobject]@{
    tool = "Repair-JsonMdUtf8ReadableText.ps1"
    started_at = $ScriptStartedAt.ToString("s")
    finished_at = (Get-Date).ToString("s")
    root = $ResolvedRoot
    extensions = $Extensions
    fix = [bool]$Fix
    backup = [bool]$Backup
    repair_mojibake = [bool]$RepairMojibake
    scanned_file_count = $targetFiles.Count
    finding_file_count = $results.Count
    fixed_file_count = $fixedCount
    decode_error_count = $decodeErrorCount
    skipped_invalid_json_after_fix_count = $skippedInvalidJsonCount
    note = "既定では非ASCIIのUnicode escapeを安全に実文字へ戻します。true mojibakeは抽出優先で、-RepairMojibake指定時のみ慎重に行単位修復します。"
    results = $results
}

$reportJson = $summary | ConvertTo-Json -Depth 12
[System.IO.File]::WriteAllText($ReportPath, $reportJson, $Utf8NoBomWrite)

Write-Host ""
Write-Host "FRB JSON/Markdown UTF-8可読性チェック 完了"
Write-Host ("Root                    : {0}" -f $ResolvedRoot)
Write-Host ("Scanned files           : {0}" -f $targetFiles.Count)
Write-Host ("Finding files           : {0}" -f $results.Count)
Write-Host ("Fixed files             : {0}" -f $fixedCount)
Write-Host ("Decode errors           : {0}" -f $decodeErrorCount)
Write-Host ("Skipped invalid JSON    : {0}" -f $skippedInvalidJsonCount)
Write-Host ("Report                  : {0}" -f $ReportPath)

if (-not $Fix) {
    Write-Host ""
    Write-Host "現在はスキャンのみです。修復する場合は -Fix を付けてください。"
}

if ($results.Count -gt 0) {
    Write-Host ""
    Write-Host "検出ファイル例:"
    $results | Select-Object -First 10 | ForEach-Object {
        Write-Host ("- [{0}] {1}  unicode_escape={2} mojibake={3}" -f $_.status, $_.path, $_.unicode_escape_count, $_.mojibake_suspect_count)
    }
}
