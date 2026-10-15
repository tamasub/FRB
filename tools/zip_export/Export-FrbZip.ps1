<#
.SYNOPSIS
    FRB と FRB_docsExcel を ZIP に保存し、外付け D ドライブへも二重保存する。
.DESCRIPTION
    既定動作:
      F:\FRB           -> F:\FRB_backups\FRB_backup_yyyyMMdd_HHmmss_fff.zip
      F:\FRB_docsExcel -> F:\FRB_backups\FRB_docsExcel_backup_yyyyMMdd_HHmmss_fff.zip
    D: が利用できる場合は D:\FRB_backups\ に同じ ZIP をコピーし、SHA256 で照合する。
    D: が未接続ならエラーにせず、F: への保存結果と「D: 未接続」を表示する。
    除外パターンは従来の exclude_patterns.txt を *変更せず* 両方に適用する。
    ZIP の中のファイルパスは従来どおり、各フォルダー直下を起点にする。
.PARAMETER SourcePath
    旧スクリプトとの互換用。指定するとこの1フォルダーのみをバックアップ。
.PARAMETER SourcePaths
    個別に複数のバックアップ対象を指定したい場合。SourcePath とは併用不可。
.PARAMETER OutputDir
    ローカルのバックアップ保存先 (既定 F:\FRB_backups)。
.PARAMETER MirrorDir
    二重保存先 (既定 D:\FRB_backups)。未接続時は正常スキップ。
.PARAMETER ExcludeFile
    除外ルールファイル (既定: スクリプトと同じ場所)。
.PARAMETER AdditionalExclude
    従来どおり、一時的な追加除外。
.PARAMETER LogFile
    実行ログ (既定: Export-FrbZip.log)。
.PARAMETER DryRun
    対象ファイル数・サイズ・除外対象・コピー先の利用可否だけ表示する。
.EXAMPLE
    .\Export-FrbZip.ps1
.EXAMPLE
    .\Export-FrbZip.ps1 -DryRun
.EXAMPLE
    .\Export-FrbZip.ps1 -SourcePath 'F:\FRB' -DryRun
#>
[CmdletBinding()]
param(
    [string]$SourcePath = "",
    [string[]]$SourcePaths = @(),
    [string]$OutputDir = "F:\FRB_backups",
    [string]$MirrorDir = "D:\FRB_backups",
    [string]$ExcludeFile = "",
    [string[]]$AdditionalExclude = @(),
    [string]$LogFile = "",
    [switch]$DryRun
)

$ErrorActionPreference = 'Stop'
$scriptDir = if ($PSScriptRoot) { $PSScriptRoot } elseif ($MyInvocation.MyCommand.Path) {
    Split-Path -Parent $MyInvocation.MyCommand.Path
} else { (Get-Location).Path }
if (-not $ExcludeFile) { $ExcludeFile = Join-Path $scriptDir 'exclude_patterns.txt' }
if (-not $LogFile) { $LogFile = Join-Path $scriptDir 'Export-FrbZip.log' }

function Get-ExcludePatterns {
    param([string]$Path, [string[]]$Extra)
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        throw "除外設定が見つかりません: $Path (除外漏れ防止のため中止します)"
    }
    $lines = @(Get-Content -LiteralPath $Path -Encoding UTF8) + @($Extra)
    $names = New-Object 'System.Collections.Generic.List[string]'
    $paths = New-Object 'System.Collections.Generic.List[string]'
    foreach ($raw in $lines) {
        if ($null -eq $raw) { continue }
        $p = $raw.Trim()
        if (-not $p -or $p.StartsWith('#')) { continue }
        $p = $p.Replace('\','/')
        if ($p.Contains('/')) { $paths.Add($p) } else { $names.Add($p) }
    }
    return [PSCustomObject]@{ NameOnly = $names; PathPattern = $paths }
}
function Test-ExcludedName {
    param([string]$Name, [System.Collections.Generic.List[string]]$Patterns)
    foreach ($p in $Patterns) { if ($Name -like $p) { return $true } }
    return $false
}
function Test-ExcludedPath {
    param([string]$RelativePath, [System.Collections.Generic.List[string]]$Patterns)
    foreach ($p in $Patterns) { if ($RelativePath -like $p) { return $true } }
    return $false
}
function Test-UnderOrSame {
    param([string]$Candidate, [string]$Parent)
    $a = [System.IO.Path]::GetFullPath($Candidate).TrimEnd('\')
    $b = [System.IO.Path]::GetFullPath($Parent).TrimEnd('\')
    return ($a.Equals($b, [StringComparison]::OrdinalIgnoreCase) -or
            $a.StartsWith($b + '\', [StringComparison]::OrdinalIgnoreCase))
}
function Get-FilesForArchive {
    param([string]$Source, $Patterns, [string]$TranscriptFile)
    $files = New-Object 'System.Collections.Generic.List[object]'
    $excludedDirs = New-Object 'System.Collections.Generic.List[string]'
    $totalBytes = [long]0
    $stack = New-Object 'System.Collections.Generic.Stack[string]'
    $stack.Push($Source)
    while ($stack.Count -gt 0) {
        $dir = $stack.Pop()
        # 読み取り失敗を握りつぶさず、欠落 ZIP を「成功」と扱わない。
        foreach ($entry in (Get-ChildItem -LiteralPath $dir -Force -ErrorAction Stop)) {
            $rel = $entry.FullName.Substring($Source.Length + 1).Replace('\','/')
            $excluded = (Test-ExcludedName $entry.Name $Patterns.NameOnly) -or
                        (Test-ExcludedPath $rel $Patterns.PathPattern)
            if ($entry.PSIsContainer) {
                if ($excluded) { $excludedDirs.Add($rel); continue }
                if (($entry.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -ne 0) {
                    # フォルダーリンクの先へ迷い込まない (バックアップの再帰・重複防止)。
                    Write-Warning "リンクフォルダーをスキップ: $rel"
                    $excludedDirs.Add($rel + ' [link]')
                    continue
                }
                $stack.Push($entry.FullName)
            } else {
                if ($excluded) { continue }
                if ([string]::Equals($entry.FullName, $TranscriptFile,
                        [System.StringComparison]::OrdinalIgnoreCase)) { continue }
                $files.Add([PSCustomObject]@{ FullPath=$entry.FullName; RelativePath=$rel; Length=[long]$entry.Length })
                $totalBytes += [long]$entry.Length
            }
        }
    }
    return [PSCustomObject]@{ Files=$files; SkippedDirs=$excludedDirs; TotalBytes=$totalBytes }
}
function Test-ZipReadable {
    param([string]$Path, $SelectedFiles)
    # ZIP を再読み込みし、全エントリーを展開してサイズが一致することを検証。
    $stream = [System.IO.File]::Open($Path,[System.IO.FileMode]::Open,[System.IO.FileAccess]::Read,[System.IO.FileShare]::Read)
    $archive = $null
    try {
        $archive = New-Object System.IO.Compression.ZipArchive($stream, [System.IO.Compression.ZipArchiveMode]::Read)
        if ($archive.Entries.Count -ne $SelectedFiles.Count) {
            throw "ZIP のエントリー数が一致しません ($($archive.Entries.Count) / $($SelectedFiles.Count))"
        }
        $expected = @{}
        foreach ($f in $SelectedFiles) { $expected[$f.RelativePath] = $f.Length }
        $buffer = New-Object byte[] (1024*1024)
        foreach ($entry in $archive.Entries) {
            if (-not $expected.ContainsKey($entry.FullName)) { throw "想定外の ZIP エントリー: $($entry.FullName)" }
            if ([long]$expected[$entry.FullName] -ne [long]$entry.Length) {
                throw "ZIP サイズ不一致: $($entry.FullName)"
            }
            $inputStream = $entry.Open()
            try {
                $readTotal = [long]0
                while (($n = $inputStream.Read($buffer,0,$buffer.Length)) -gt 0) { $readTotal += [long]$n }
                if ($readTotal -ne $entry.Length) { throw "ZIP の展開サイズが一致しません: $($entry.FullName)" }
            } finally { $inputStream.Dispose() }
        }
    } finally {
        if ($null -ne $archive) { $archive.Dispose() }
        $stream.Dispose()
    }
}
function New-ArchiveOnF {
    param([string]$Source, [string]$Output, [string]$Mirror, [bool]$MirrorReady, $Patterns, [string]$TranscriptFile)
    if (-not (Test-Path -LiteralPath $Source -PathType Container)) { throw "元フォルダーがありません: $Source" }
    $sourceResolved = (Resolve-Path -LiteralPath $Source).ProviderPath.TrimEnd('\')
    if ((Test-UnderOrSame $Output $sourceResolved) -or (Test-UnderOrSame $Mirror $sourceResolved)) {
        throw "バックアップ先が対象フォルダー内です (自己 ZIP 化防止): $sourceResolved"
    }
    $selection = Get-FilesForArchive -Source $sourceResolved -Patterns $Patterns -TranscriptFile $TranscriptFile
    Write-Host ""
    Write-Host "対象       : $sourceResolved" -ForegroundColor Cyan
    Write-Host ("ファイル数 : {0:N0} / 元の合計 {1:N1} MB / 除外フォルダー {2:N0} 件" -f
        $selection.Files.Count,($selection.TotalBytes/1MB),$selection.SkippedDirs.Count)
    $selection.SkippedDirs | Select-Object -Unique | Sort-Object | Select-Object -First 25 | ForEach-Object {
        Write-Host "  除外: $_" -ForegroundColor DarkGray
    }
    if ($DryRun) { Write-Host 'DryRun: ZIP は作成しません。'; return $null }
    if ($selection.Files.Count -eq 0) { throw "ZIP 対象のファイルが 0 件です: $sourceResolved" }

    $folderName = Split-Path $sourceResolved -Leaf
    $timestamp = Get-Date -Format 'yyyyMMdd_HHmmss_fff'
    $zipPath = $null
    for ($i=0; $i -lt 100; $i++) {
        $suffix = if ($i -eq 0) { '' } else { "_$i" }
        $filename = "${folderName}_backup_${timestamp}${suffix}.zip"
        $candidate = Join-Path $Output $filename
        $nameTakenOnD = $false
        if ($MirrorReady) { $nameTakenOnD = Test-Path -LiteralPath (Join-Path $Mirror $filename) }
        if (-not (Test-Path -LiteralPath $candidate) -and -not $nameTakenOnD) {
            $zipPath = $candidate; break
        }
    }
    if (-not $zipPath) { throw "重複しない ZIP ファイル名を作れません: $folderName" }
    $partial = $zipPath + '.partial'
    $success = $false
    $watch = [System.Diagnostics.Stopwatch]::StartNew()
    try {
        $stream = [System.IO.File]::Open($partial,[System.IO.FileMode]::CreateNew,[System.IO.FileAccess]::ReadWrite,[System.IO.FileShare]::None)
        $archive = $null
        try {
            $archive = New-Object System.IO.Compression.ZipArchive($stream,[System.IO.Compression.ZipArchiveMode]::Create)
            foreach ($f in $selection.Files) {
                [System.IO.Compression.ZipFileExtensions]::CreateEntryFromFile(
                    $archive,$f.FullPath,$f.RelativePath,[System.IO.Compression.CompressionLevel]::Optimal) | Out-Null
            }
        } finally {
            if ($null -ne $archive) { $archive.Dispose() }
            $stream.Dispose()
        }
        Test-ZipReadable -Path $partial -SelectedFiles $selection.Files
        [System.IO.File]::Move($partial,$zipPath)
        $success = $true
        $watch.Stop()
        $zipBytes = (Get-Item -LiteralPath $zipPath).Length
        Write-Host ("F: 保存・ZIP検証 OK: {0}  ({1:N1} MB, {2:N1} 秒)" -f
            $zipPath,($zipBytes/1MB),$watch.Elapsed.TotalSeconds) -ForegroundColor Green
        return $zipPath
    } finally {
        if (-not $success -and (Test-Path -LiteralPath $partial)) {
            Remove-Item -LiteralPath $partial -Force -ErrorAction SilentlyContinue
        }
    }
}
function Copy-ToMirror {
    param([string]$ZipPath, [string]$TargetDirectory)
    $destination = Join-Path $TargetDirectory (Split-Path $ZipPath -Leaf)
    $temporary = $destination + '.partial'
    try {
        if (Test-Path -LiteralPath $destination) { throw "同名ファイルが D: にあります (上書きしません): $destination" }
        if (Test-Path -LiteralPath $temporary) { throw "D: に一時ファイルが残っています: $temporary" }
        [System.IO.File]::Copy($ZipPath,$temporary,$false)
        $a = (Get-FileHash -LiteralPath $ZipPath -Algorithm SHA256).Hash
        $b = (Get-FileHash -LiteralPath $temporary -Algorithm SHA256).Hash
        if ($a -ne $b) { throw "SHA256 が不一致です: $destination" }
        [System.IO.File]::Move($temporary,$destination)
        Write-Host "D: コピー・SHA256一致 OK: $destination" -ForegroundColor Green
        return $true
    } catch {
        Write-Warning "D: への二重保存に失敗: $($_.Exception.Message)"
        return $false
    } finally {
        if (Test-Path -LiteralPath $temporary) {
            Remove-Item -LiteralPath $temporary -Force -ErrorAction SilentlyContinue
        }
    }
}

$transcriptStarted = $false
$failed = $false
$missingMirror = $false
try {
    try {
        Start-Transcript -Path $LogFile -Append | Out-Null
        $transcriptStarted = $true
    } catch {
        Write-Warning "ログを開始できません: $($_.Exception.Message)"
    }
    Add-Type -AssemblyName System.IO.Compression
    Add-Type -AssemblyName System.IO.Compression.FileSystem
    if ($SourcePath -and $SourcePaths.Count -gt 0) { throw 'SourcePath と SourcePaths は併用できません' }
    $sourceList = if ($SourcePath) { @($SourcePath) } elseif ($SourcePaths.Count -gt 0) {
        @($SourcePaths)
    } else { @('F:\FRB','F:\FRB_docsExcel') }
    $patterns = Get-ExcludePatterns -Path $ExcludeFile -Extra $AdditionalExclude
    $logFull = [System.IO.Path]::GetFullPath($LogFile)

    # D: が無い場合は正常スキップ。検出と表示は一度だけ行う。
    $driveRoot = [System.IO.Path]::GetPathRoot([System.IO.Path]::GetFullPath($MirrorDir))
    $mirrorReady = $false
    try {
        if (Test-Path -LiteralPath $driveRoot -PathType Container) {
            if (-not $DryRun -and -not (Test-Path -LiteralPath $MirrorDir)) {
                New-Item -ItemType Directory -Path $MirrorDir -Force | Out-Null
            }
            $mirrorReady = $true
        } else {
            $missingMirror = $true
            Write-Host "外付けDドライブが見つかりません ($driveRoot)。D:へのコピーはスキップします。" -ForegroundColor Yellow
        }
    } catch {
        Write-Warning "二重保存先 D: を使用できません: $($_.Exception.Message)"
        $missingMirror = $true
    }
    if ($mirrorReady) { Write-Host "二重保存先: $MirrorDir (利用可能)" -ForegroundColor Cyan }
    Write-Host "ローカル保存先: $OutputDir" -ForegroundColor Cyan

    if (-not $DryRun -and -not (Test-Path -LiteralPath $OutputDir)) {
        New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
    }
    $created = New-Object 'System.Collections.Generic.List[string]'
    foreach ($src in $sourceList) {
        try {
            $zipPath = New-ArchiveOnF -Source $src -Output $OutputDir -Mirror $MirrorDir -MirrorReady $mirrorReady -Patterns $patterns -TranscriptFile $logFull
            if ($zipPath) { $created.Add($zipPath) }
        } catch {
            $failed = $true
            Write-Warning "F: ZIP作成失敗 [$src]: $($_.Exception.Message)"
        }
    }
    if (-not $DryRun -and $mirrorReady) {
        foreach ($zipPath in $created) {
            if (-not (Copy-ToMirror -ZipPath $zipPath -TargetDirectory $MirrorDir)) { $failed = $true }
        }
    }
    Write-Host ''
    Write-Host '========== バックアップ結果 ==========' -ForegroundColor Cyan
    if ($DryRun) {
        Write-Host 'DryRun 完了 (ZIP・コピーは作成していません)'
    } else {
        Write-Host "F: ZIP作成・検証完了: $($created.Count) / $($sourceList.Count) 件"
        if ($missingMirror) {
            Write-Host "D: 未接続 / 利用不可: コピーをスキップ (F: ZIPは保持)" -ForegroundColor Yellow
        } elseif ($mirrorReady) {
            Write-Host "D: 保存先: $MirrorDir (各ZIPをSHA256で照合)"
        }
        if ($failed) {
            Write-Warning '一部のバックアップに失敗しました。ログを確認してください。'
        } else {
            Write-Host '処理完了。' -ForegroundColor Green
        }
    }
} catch {
    $failed = $true
    Write-Error "バックアップ処理を中断しました: $($_.Exception.Message)" -ErrorAction Continue
} finally {
    if ($transcriptStarted) { Stop-Transcript | Out-Null }
}
if ($failed) { exit 1 } else { exit 0 }
