<#
.SYNOPSIS
    F:\FRB フォルダーを、除外パターンに従って zip 化する。

.DESCRIPTION
    bin/obj/node_modules などビルド生成物や肥大化しやすいフォルダーを
    exclude_patterns.txt (このスクリプトと同じフォルダー) の設定に従ってスキップしながら
    zip を作成する。除外対象のフォルダーはそもそも中を走査しないため、
    Explorer の「送る > 圧縮 (zip 形式) フォルダー」より高速。

    実行内容は Export-FrbZip.log (このスクリプトと同じフォルダー) に追記されるため、
    過去の実行履歴（いつ・何MBのzipができたか等）を後から見返せる。

.PARAMETER SourcePath
    zip化する対象フォルダー。既定は F:\FRB。

.PARAMETER OutputDir
    zip の出力先フォルダー。既定は F:\FRB_backups（無ければ作成する）。
    F:\FRB の外に出すことで、zip自身がzip対象に巻き込まれるのを防ぐ。

.PARAMETER ExcludeFile
    除外パターン設定ファイルのパス。既定はこのスクリプトと同じフォルダーの exclude_patterns.txt。

.PARAMETER AdditionalExclude
    exclude_patterns.txt の内容に加えて、今回の実行だけ追加したい除外パターン。

.PARAMETER LogFile
    実行ログの出力先。既定はこのスクリプトと同じフォルダーの Export-FrbZip.log（追記型・削除しない限り蓄積し続ける）。

.PARAMETER DryRun
    実際に zip を作らず、含まれるファイル数・除外されるフォルダー一覧だけ表示する。

.EXAMPLE
    F:\FRB\tools\zip_export\Export-FrbZip.ps1

.EXAMPLE
    F:\FRB\tools\zip_export\Export-FrbZip.ps1 -DryRun

.EXAMPLE
    F:\FRB\tools\zip_export\Export-FrbZip.ps1 -AdditionalExclude "tools/FRBStudio_App/studio_overlays/gpt_fx_lab/sidecars"
#>
[CmdletBinding()]
param(
    [string]$SourcePath = "F:\FRB",
    [string]$OutputDir = "F:\FRB_backups",
    [string]$ExcludeFile = "",
    [string[]]$AdditionalExclude = @(),
    [string]$LogFile = "",
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"

# $PSScriptRoot is blank when this script is invoked in certain ways (e.g. pasted
# into an interactive prompt), so fall back to $MyInvocation / current directory.
$ScriptDir = if ($PSScriptRoot) {
    $PSScriptRoot
} elseif ($MyInvocation.MyCommand.Path) {
    Split-Path -Parent $MyInvocation.MyCommand.Path
} else {
    (Get-Location).Path
}

if (-not $ExcludeFile) { $ExcludeFile = Join-Path $ScriptDir "exclude_patterns.txt" }
if (-not $LogFile) { $LogFile = Join-Path $ScriptDir "Export-FrbZip.log" }

function Get-ExcludePatterns {
    param([string]$Path, [string[]]$Extra)

    $lines = @()
    if (Test-Path -LiteralPath $Path) {
        $lines += Get-Content -LiteralPath $Path -Encoding UTF8
    } else {
        Write-Warning "除外設定ファイルが見つからない: $Path (除外なしで続行する)"
    }
    $lines += $Extra

    $nameOnly = New-Object System.Collections.Generic.List[string]
    $pathPattern = New-Object System.Collections.Generic.List[string]

    foreach ($raw in $lines) {
        $line = $raw.Trim()
        if ($line -eq "" -or $line.StartsWith("#")) { continue }
        $normalized = $line.Replace('\', '/')
        if ($normalized.Contains('/')) {
            $pathPattern.Add($normalized)
        } else {
            $nameOnly.Add($normalized)
        }
    }

    [PSCustomObject]@{
        NameOnly    = $nameOnly
        PathPattern = $pathPattern
    }
}

function Test-ExcludedName {
    param([string]$Name, [System.Collections.Generic.List[string]]$Patterns)
    foreach ($p in $Patterns) {
        if ($Name -like $p) { return $true }
    }
    return $false
}

function Test-ExcludedPath {
    param([string]$RelativePath, [System.Collections.Generic.List[string]]$Patterns)
    foreach ($p in $Patterns) {
        if ($RelativePath -like $p) { return $true }
    }
    return $false
}

$transcriptStarted = $false
try {
    Start-Transcript -Path $LogFile -Append | Out-Null
    $transcriptStarted = $true
} catch {
    Write-Warning "ログ出力を開始できなかった: $($_.Exception.Message)"
}

try {
    $patterns = Get-ExcludePatterns -Path $ExcludeFile -Extra $AdditionalExclude

    $sourceFull = (Resolve-Path -LiteralPath $SourcePath).ProviderPath.TrimEnd('\')
    $logFileFull = [System.IO.Path]::GetFullPath($LogFile)

    $filesToZip = New-Object System.Collections.Generic.List[object]
    $skippedDirs = New-Object System.Collections.Generic.List[string]
    $totalBytes = 0L

    $stack = New-Object System.Collections.Generic.Stack[string]
    $stack.Push($sourceFull)

    while ($stack.Count -gt 0) {
        $currentDir = $stack.Pop()
        $entries = Get-ChildItem -LiteralPath $currentDir -Force -ErrorAction SilentlyContinue

        foreach ($entry in $entries) {
            $relativePath = $entry.FullName.Substring($sourceFull.Length + 1).Replace('\', '/')
            $isExcluded = (Test-ExcludedName -Name $entry.Name -Patterns $patterns.NameOnly) -or
                          (Test-ExcludedPath -RelativePath $relativePath -Patterns $patterns.PathPattern)

            if ($entry.PSIsContainer) {
                if ($isExcluded) {
                    $skippedDirs.Add($relativePath)
                    continue
                }
                $stack.Push($entry.FullName)
            } else {
                if ($isExcluded) { continue }
                # 実行中は Start-Transcript がこのファイルを開きっぱなしにしているため、
                # 自分自身のログファイルは常に除外する（除外設定に関わらず）。
                if ($entry.FullName -ieq $logFileFull) { continue }
                $filesToZip.Add([PSCustomObject]@{
                    FullPath     = $entry.FullName
                    RelativePath = $relativePath
                    Length       = $entry.Length
                })
                $totalBytes += $entry.Length
            }
        }
    }

    Write-Host ""
    Write-Host "対象フォルダー       : $sourceFull"
    Write-Host "含めるファイル数     : $($filesToZip.Count)"
    Write-Host ("含めるサイズ合計     : {0:N1} MB" -f ($totalBytes / 1MB))
    Write-Host "除外したフォルダー数 : $($skippedDirs.Count)"
    if ($skippedDirs.Count -gt 0) {
        $skippedDirs | Select-Object -Unique | Sort-Object | Select-Object -First 30 | ForEach-Object {
            Write-Host "  - $_"
        }
        if ($skippedDirs.Count -gt 30) {
            Write-Host "  ... 他 $($skippedDirs.Count - 30) 件"
        }
    }

    if ($DryRun) {
        Write-Host ""
        Write-Host "DryRun のため zip は作成しない。"
    } else {
        if (-not (Test-Path -LiteralPath $OutputDir)) {
            New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
        }

        $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
        $zipPath = Join-Path $OutputDir "FRB_backup_$timestamp.zip"

        Add-Type -AssemblyName System.IO.Compression
        Add-Type -AssemblyName System.IO.Compression.FileSystem

        $sw = [System.Diagnostics.Stopwatch]::StartNew()

        $zipStream = [System.IO.File]::Open($zipPath, [System.IO.FileMode]::Create)
        $archive = New-Object System.IO.Compression.ZipArchive($zipStream, [System.IO.Compression.ZipArchiveMode]::Create)

        try {
            foreach ($f in $filesToZip) {
                [System.IO.Compression.ZipFileExtensions]::CreateEntryFromFile(
                    $archive, $f.FullPath, $f.RelativePath, [System.IO.Compression.CompressionLevel]::Optimal
                ) | Out-Null
            }
        } finally {
            $archive.Dispose()
            $zipStream.Dispose()
        }

        $sw.Stop()
        $zipSize = (Get-Item -LiteralPath $zipPath).Length

        Write-Host ""
        Write-Host "zip作成完了     : $zipPath"
        Write-Host ("zipサイズ       : {0:N1} MB" -f ($zipSize / 1MB))
        Write-Host ("所要時間        : {0:N1} 秒" -f $sw.Elapsed.TotalSeconds)
    }
} finally {
    if ($transcriptStarted) {
        Stop-Transcript | Out-Null
    }
}
