<# 
Export-DiffToJson.ps1
MetaDiff v0.1.2-draft

Git差分を、AIに渡しやすい DiffToJson.json に変換するPowerShellスクリプト。

使い方:
  # 作業ツリーの未ステージ差分
  powershell -ExecutionPolicy Bypass -File .\Export-DiffToJson.ps1

  # ステージ済み差分
  powershell -ExecutionPolicy Bypass -File .\Export-DiffToJson.ps1 -Mode Staged

  # HEADとの差分（ステージ済み + 未ステージを含めて見たい時）
  powershell -ExecutionPolicy Bypass -File .\Export-DiffToJson.ps1 -Mode Head

  # コミット範囲を指定
  powershell -ExecutionPolicy Bypass -File .\Export-DiffToJson.ps1 -Range "main..HEAD"

  powershell -ExecutionPolicy Bypass -File .\Export-DiffToJson.ps1 -Range "aa8e0169abda0fbcf09b2ab34ff9f6abf547f83a..HEAD"

  # パッチ本文を長めに入れる
  powershell -ExecutionPolicy Bypass -File .\Export-DiffToJson.ps1 -MaxPatchChars 200000

注意:
  - git diff は未追跡ファイルを差分本文としては拾いません。
  - 未追跡ファイルは status 上の注意情報として記録します。
  - AIの出力は「レビュー結果」ではなく「仮説」として扱う前提です。
#>

param(
    [ValidateSet("WorkingTree", "Staged", "Head")]
    [string]$Mode = "WorkingTree",

    [string]$Range = "",

    [string]$OutputPath = "F:\FRB\tools\FRBStudio_App\wwwroot\diff\DiffToJson.json",

    [int]$Unified = 3,

    [int]$MaxPatchChars = 60000,

    [switch]$NoPatch
)

$ErrorActionPreference = "Stop"

# Windows PowerShell 5.1 は Git のUTF-8出力を文字化けさせやすいため、
# スクリプト開始時にコンソールとPowerShellの出力エンコードをUTF-8へ寄せる。
# chcpの変更は現在のPowerShellセッションに影響します。
try {
    & chcp.com 65001 > $null
} catch {}

try {
    [Console]::InputEncoding  = [System.Text.UTF8Encoding]::new($false)
    [Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
    $OutputEncoding = [System.Text.UTF8Encoding]::new($false)
} catch {
    Write-Warning "UTF-8 encoding setup failed: $($_.Exception.Message)"
}

# Gitがstderrへwarningを出しても、exit code が0なら処理を継続する。
# PowerShellは native command の stderr を NativeCommandError として扱うことがあるため、
# ErrorActionPreference を一時的に Continue にして捕捉する。
$script:GitWarnings = @()

function Invoke-Git {
    param(
        [Parameter(Mandatory=$true)]
        [string[]]$GitArgs
    )

    $oldEap = $ErrorActionPreference
    $ErrorActionPreference = "Continue"

    try {
        $rawOutput = & git -c core.quotepath=false -c i18n.logOutputEncoding=utf-8 @GitArgs 2>&1 | ForEach-Object { $_.ToString() }
        $exit = $LASTEXITCODE
    }
    finally {
        $ErrorActionPreference = $oldEap
    }

    if ($null -eq $rawOutput) {
        $rawOutput = @()
    }

    $warnings = @()
    $output = @()

    foreach ($line in $rawOutput) {
        # 代表的なgitのstderr warning/hintは、JSON変換対象のstdoutから分離して保持する。
        if ($line -match "^(warning|hint):") {
            $warnings += $line
        }
        else {
            $output += $line
        }
    }

    if ($warnings.Count -gt 0) {
        $script:GitWarnings += [pscustomobject]@{
            command = "git -c core.quotepath=false -c i18n.logOutputEncoding=utf-8 " + ($GitArgs -join " ")
            warnings = $warnings
        }
    }

    if ($exit -ne 0) {
        $message = ($rawOutput -join "`n")
        throw "git $($GitArgs -join ' ') failed. exit_code=$exit`n$message"
    }

    return $output
}

function Get-DiffArgs {
    param(
        [string]$Mode,
        [string]$Range
    )

    $args = @("diff", "--find-renames")

    if ($Range -and $Range.Trim().Length -gt 0) {
        $args += $Range
        return $args
    }

    switch ($Mode) {
        "WorkingTree" { }
        "Staged" { $args += "--cached" }
        "Head" { $args += "HEAD" }
    }

    return $args
}

function Parse-NameStatus {
    param([string[]]$Lines)

    $items = @()

    foreach ($line in $Lines) {
        if ([string]::IsNullOrWhiteSpace($line)) { continue }

        $parts = $line -split "`t"
        if ($parts.Count -lt 2) { continue }

        $status = $parts[0]
        $oldPath = $null
        $path = $null

        if (($status.StartsWith("R") -or $status.StartsWith("C")) -and $parts.Count -ge 3) {
            $oldPath = $parts[1]
            $path = $parts[2]
        } else {
            $path = $parts[1]
        }

        $items += [pscustomobject]@{
            status = $status
            path = $path
            old_path = $oldPath
        }
    }

    return $items
}

function Parse-NumStat {
    param([string[]]$Lines)

    $map = @{}

    foreach ($line in $Lines) {
        if ([string]::IsNullOrWhiteSpace($line)) { continue }

        $parts = $line -split "`t"
        if ($parts.Count -lt 3) { continue }

        $addedRaw = $parts[0]
        $deletedRaw = $parts[1]
        $path = ($parts[2..($parts.Count - 1)] -join "`t")

        $added = $null
        $deleted = $null
        $isBinary = $false

        if ($addedRaw -eq "-" -or $deletedRaw -eq "-") {
            $isBinary = $true
        } else {
            $added = [int]$addedRaw
            $deleted = [int]$deletedRaw
        }

        $map[$path] = [pscustomobject]@{
            added = $added
            deleted = $deleted
            binary = $isBinary
        }
    }

    return $map
}

function Truncate-Text {
    param(
        [string]$Text,
        [int]$MaxChars
    )

    if ($null -eq $Text) { return "" }

    if ($Text.Length -le $MaxChars) {
        return $Text
    }

    return $Text.Substring(0, $MaxChars) + "`n`n--- PATCH TRUNCATED: max_patch_chars=$MaxChars ---"
}

# Gitリポジトリ確認
$repoRoot = (Invoke-Git @("rev-parse", "--show-toplevel")).Trim()
Set-Location $repoRoot

$branch = ""
try { $branch = (Invoke-Git @("branch", "--show-current")).Trim() } catch { $branch = "" }

$head = ""
try { $head = (Invoke-Git @("rev-parse", "--short", "HEAD")).Trim() } catch { $head = "" }

$diffArgs = Get-DiffArgs -Mode $Mode -Range $Range

$nameStatusLines = Invoke-Git ($diffArgs + @("--name-status"))
$numStatLines = Invoke-Git ($diffArgs + @("--numstat"))
$statusShort = Invoke-Git @("status", "--short")

$files = Parse-NameStatus $nameStatusLines
$numStat = Parse-NumStat $numStatLines

$changedFiles = @()
$totalAdded = 0
$totalDeleted = 0
$binaryCount = 0

foreach ($file in $files) {
    $stats = $null

    if ($numStat.ContainsKey($file.path)) {
        $stats = $numStat[$file.path]
    } else {
        # rename表示などで直接一致しない場合のフォールバック
        $stats = [pscustomobject]@{
            added = $null
            deleted = $null
            binary = $false
        }
    }

    if ($stats.binary) {
        $binaryCount += 1
    } else {
        if ($null -ne $stats.added) { $totalAdded += $stats.added }
        if ($null -ne $stats.deleted) { $totalDeleted += $stats.deleted }
    }

    $patchText = ""
    if (-not $NoPatch) {
        try {
            $fileDiffArgs = @()
            if ($Range -and $Range.Trim().Length -gt 0) {
                $fileDiffArgs = @("diff", "--find-renames", "--unified=$Unified", $Range, "--", $file.path)
            } else {
                switch ($Mode) {
                    "WorkingTree" { $fileDiffArgs = @("diff", "--find-renames", "--unified=$Unified", "--", $file.path) }
                    "Staged" { $fileDiffArgs = @("diff", "--find-renames", "--cached", "--unified=$Unified", "--", $file.path) }
                    "Head" { $fileDiffArgs = @("diff", "--find-renames", "--unified=$Unified", "HEAD", "--", $file.path) }
                }
            }
            $patchText = (Invoke-Git $fileDiffArgs) -join "`n"
            $patchText = Truncate-Text -Text $patchText -MaxChars $MaxPatchChars
        } catch {
            $patchText = "PATCH_UNAVAILABLE: $($_.Exception.Message)"
        }
    }

    $changedFiles += [pscustomobject]@{
        path = $file.path
        old_path = $file.old_path
        status = $file.status
        added = $stats.added
        deleted = $stats.deleted
        binary = $stats.binary
        patch = $patchText
        ai_input_notes = @(
            "このファイルの変更目的を断定せず、仮説として読むこと。",
            "変更理由・影響範囲・違和感候補を分けて扱うこと。"
        )
    }
}

$untracked = @()
foreach ($line in $statusShort) {
    if ($line.StartsWith("?? ")) {
        $untracked += $line.Substring(3)
    }
}

$result = [ordered]@{
    schema_version = "0.1.2-draft"
    generated_at = (Get-Date).ToString("o")
    tool = [ordered]@{
        name = "MetaDiff Export-DiffToJson.ps1"
        version = "0.1.2-draft"
    }
    repository = [ordered]@{
        root = $repoRoot
        branch = $branch
        head = $head
    }
    diff_source = [ordered]@{
        mode = $Mode
        range = $Range
        command = "git " + ($diffArgs -join " ")
        unified_context_lines = $Unified
        patch_included = (-not $NoPatch).IsPresent
        max_patch_chars_per_file = $MaxPatchChars
    }
    git_warnings = $script:GitWarnings
    summary = [ordered]@{
        files_changed = $changedFiles.Count
        total_added = $totalAdded
        total_deleted = $totalDeleted
        binary_files = $binaryCount
        untracked_files_count = $untracked.Count
    }
    diff_facts = [ordered]@{
        changed_files = $changedFiles
        untracked_files = $untracked
        status_short = $statusShort
    }
    ai_hypothesis_input = [ordered]@{
        instruction = "AIはレビュー結果ではなく、仮説（差分ストーリー）・違和感候補・確認観点を出す。最終判断は人間が行う。"
        desired_outputs = @(
            "変更内容の事実要約",
            "AI仮説（差分ストーリー）",
            "差異想定理由",
            "カテゴリ候補",
            "影響範囲の仮説",
            "違和感候補",
            "人間への確認質問",
            "テスト観点",
            "ドキュメント更新観点",
            "人間が記入する意図・違和感メモ"
        )
        forbidden_labels = @(
            "AIレビュー結果",
            "AI判定",
            "AI承認",
            "AIチェック済み"
        )
    }
    human_reflection = [ordered]@{
        intended_change_reason = ""
        mismatch_notes = @()
        confirmed_unintended_changes = @()
        next_actions = @()
    }
}

$json = $result | ConvertTo-Json -Depth 30


# OutputPath が絶対パスならそのまま使う
# 相対パスなら repoRoot からの相対パスとして扱う
if ([System.IO.Path]::IsPathRooted($OutputPath)) {
    $baseOutputPath = $OutputPath
} else {
    $baseOutputPath = Join-Path $repoRoot $OutputPath
}

# 日時付きファイル名にする
# 例: DiffToJson_20260523_213045.json
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"

$outputDir = Split-Path -Parent $baseOutputPath
$outputFileName = [System.IO.Path]::GetFileNameWithoutExtension($baseOutputPath)
$outputExt = [System.IO.Path]::GetExtension($baseOutputPath)

if ([string]::IsNullOrWhiteSpace($outputExt)) {
    $outputExt = ".json"
}

$resolvedOutputPath = Join-Path $outputDir ("{0}_{1}{2}" -f $outputFileName, $timestamp, $outputExt)

# 出力先フォルダがなければ作成
if (-not [string]::IsNullOrWhiteSpace($outputDir)) {
    New-Item -ItemType Directory -Force -Path $outputDir | Out-Null
}

[System.IO.File]::WriteAllText(
    $resolvedOutputPath,
    $json,
    [System.Text.UTF8Encoding]::new($false)
)

Write-Host "Created: $resolvedOutputPath"


Write-Host "Repository: $repoRoot"
Write-Host "Files changed: $($changedFiles.Count)"
Write-Host "Added: $totalAdded / Deleted: $totalDeleted"
if ($untracked.Count -gt 0) {
    Write-Host "Untracked files are listed, but not included as diff patches: $($untracked.Count)"
}
