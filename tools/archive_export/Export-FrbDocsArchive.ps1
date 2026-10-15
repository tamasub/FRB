#Requires -Version 5.1
<#
FRB DocsExcel archive exporter v3: split by REAL compressed ZIP size.
ZIP content, .zip_ extension. Windows PowerShell 5.1.
Only replaces the previous archives after ALL new archives for that source
have passed content integrity verification. Keep private data out of public Git.
#>
[CmdletBinding()]
param(
    [switch]$DryRun,
    [ValidateRange(1,90)]
    [int]$MaxPartMiB = 50
)

$ErrorActionPreference = 'Stop'
$Sources = @(
    [pscustomobject]@{ Label='設計書'; Root='F:\FRB_docsExcel\設計書' },
    [pscustomobject]@{ Label='実験ログ'; Root='F:\FRB_docsExcel\実験ログ' }
)
$Destination = 'F:\FRB\_archive'
[long]$LimitBytes = [long]$MaxPartMiB * 1MB
[long]$GitHubHardLimitBytes = 100000000L
$ExitCode = 0
Add-Type -AssemblyName System.IO.Compression

function Get-ReadableSize([long]$Bytes) {
    return ('{0:N2} MiB' -f ($Bytes / 1MB))
}

function Get-Items([string]$Root) {
    $rootPath = [IO.Path]::GetFullPath($Root).TrimEnd([char]'\')
    $pending = New-Object 'System.Collections.Generic.Stack[string]'
    $pending.Push($rootPath)
    $items = New-Object 'System.Collections.Generic.List[object]'
    while ($pending.Count -gt 0) {
        $folder = $pending.Pop()
        $children = [IO.Directory]::GetFileSystemEntries($folder) | Sort-Object
        foreach ($child in $children) {
            $attrs = [IO.File]::GetAttributes($child)
            if (($attrs -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
                Write-Warning ("リンク/リパースポイントは対象外: " + $child)
                continue
            }
            $relative = $child.Substring($rootPath.Length).TrimStart([char]'\').Replace('\', '/')
            if (($attrs -band [IO.FileAttributes]::Directory) -ne 0) {
                $items.Add([pscustomobject]@{ Path=$child; Relative=$relative; IsDirectory=$true; Size=0L })
                $pending.Push($child)
            }
            else {
                $file = [IO.FileInfo]::new($child)
                $items.Add([pscustomobject]@{ Path=$child; Relative=$relative; IsDirectory=$false; Size=[long]$file.Length })
            }
        }
    }
    return @($items.ToArray() | Sort-Object Relative)
}

function Get-StreamHash {
    param(
        [Parameter(Mandatory=$true)][System.IO.Stream]$InputStream,
        [System.IO.Stream]$OutputStream
    )
    $hasher = [System.Security.Cryptography.SHA256]::Create()
    $buffer = New-Object byte[] (1024 * 1024)
    try {
        while (($read = $InputStream.Read($buffer, 0, $buffer.Length)) -gt 0) {
            if ($null -ne $OutputStream) { $OutputStream.Write($buffer, 0, $read) }
            [void]$hasher.TransformBlock($buffer, 0, $read, $buffer, 0)
        }
        [void]$hasher.TransformFinalBlock($buffer, 0, 0)
        return [BitConverter]::ToString($hasher.Hash).Replace('-', '')
    }
    finally { $hasher.Dispose() }
}

function New-ZipPart {
    param(
        [string]$Label,
        [object[]]$Items,
        [string]$OutputPath
    )
    # Build in the same directory, so the published .zip_ is never partial.
    $tempPath = Join-Path $Destination ('.frb-archive-' + [guid]::NewGuid().ToString('N') + '.tmp')
    $hashes = @{}
    $fileCount = 0
    $expectedEntries = 1 + $Items.Count
    $completed = $false
    try {
        $fs = [IO.File]::Open($tempPath, [IO.FileMode]::CreateNew, [IO.FileAccess]::ReadWrite, [IO.FileShare]::None)
        try {
            $zip = [IO.Compression.ZipArchive]::new($fs, [IO.Compression.ZipArchiveMode]::Create, $true, [Text.Encoding]::UTF8)
            try {
                $rootEntry = $zip.CreateEntry($Label + '/')
                $rootEntry.LastWriteTime = [DateTimeOffset]::new(1980,1,1,0,0,0,[TimeSpan]::Zero)
                foreach ($item in $Items) {
                    $entryName = $Label + '/' + $item.Relative
                    if ($item.IsDirectory) {
                        $entry = $zip.CreateEntry($entryName + '/')
                    }
                    else {
                        $entry = $zip.CreateEntry($entryName, [IO.Compression.CompressionLevel]::Optimal)
                        $fileInfo = [IO.FileInfo]::new($item.Path)
                        $mtime = $fileInfo.LastWriteTime
                        if ($mtime.Year -ge 1980 -and $mtime.Year -le 2107) {
                            $entry.LastWriteTime = [DateTimeOffset]$mtime
                        }
                        $src = [IO.File]::Open($item.Path, [IO.FileMode]::Open, [IO.FileAccess]::Read, [IO.FileShare]::Read)
                        $target = $entry.Open()
                        try {
                            $hashes[$entryName] = Get-StreamHash -InputStream $src -OutputStream $target
                            $fileCount++
                        }
                        finally {
                            $target.Dispose()
                            $src.Dispose()
                        }
                    }
                }
            }
            finally { $zip.Dispose() }
        }
        finally { $fs.Dispose() }

        # Read back every entry. Verify decompressed SHA-256, not just ZIP headers.
        $verifyFs = [IO.File]::Open($tempPath, [IO.FileMode]::Open, [IO.FileAccess]::Read, [IO.FileShare]::Read)
        try {
            $verifyZip = [IO.Compression.ZipArchive]::new($verifyFs, [IO.Compression.ZipArchiveMode]::Read, $true, [Text.Encoding]::UTF8)
            try {
                if ($verifyZip.Entries.Count -ne $expectedEntries) {
                    throw ("ZIP entry count mismatch: " + $OutputPath)
                }
                foreach ($entry in $verifyZip.Entries) {
                    if ($entry.FullName.EndsWith('/')) { continue }
                    $readStream = $entry.Open()
                    try { $actualHash = Get-StreamHash -InputStream $readStream }
                    finally { $readStream.Dispose() }
                    if ($hashes[$entry.FullName] -cne $actualHash) {
                        throw ("ZIP hash mismatch: " + $entry.FullName)
                    }
                }
            }
            finally { $verifyZip.Dispose() }
        }
        finally { $verifyFs.Dispose() }

        $completed = $true
        return [pscustomobject]@{
            TempPath = $tempPath
            Size = [long]([IO.FileInfo]::new($tempPath).Length)
            FileCount = $fileCount
        }
    }
    finally {
        if (-not $completed -and [IO.File]::Exists($tempPath)) { [IO.File]::Delete($tempPath) }
    }
}


function Split-ByCompressedSize {
    param(
        [string]$Label,
        [object[]]$Files,
        [string]$VerifiedZipPath,
        [long]$TargetBytes
    )
    # Use the actual Deflate sizes in the verified ZIP, not uncompressed JSON sizes.
    # Allow some room for entry headers, timestamps, directory entries and the ZIP index.
    $weights = @{}
    $stream = [IO.File]::Open($VerifiedZipPath, [IO.FileMode]::Open, [IO.FileAccess]::Read, [IO.FileShare]::Read)
    try {
        $archive = [IO.Compression.ZipArchive]::new($stream, [IO.Compression.ZipArchiveMode]::Read, $true, [Text.Encoding]::UTF8)
        try {
            foreach ($entry in $archive.Entries) {
                if ($entry.FullName.EndsWith('/')) { continue }
                $relative = $entry.FullName.Substring(($Label + '/').Length)
                $weights[$relative] = [long]$entry.CompressedLength + 512L + (4L * $entry.FullName.Length)
            }
        }
        finally { $archive.Dispose() }
    }
    finally { $stream.Dispose() }

    [long]$packingLimit = [Math]::Max(1L, ($TargetBytes - 1MB))
    $groups = New-Object 'System.Collections.Generic.List[object]'
    $group = New-Object 'System.Collections.Generic.List[object]'
    [long]$used = 0
    foreach ($f in $Files) {
        if (-not $weights.ContainsKey($f.Relative)) { throw ('Missing compressed-size entry: ' + $f.Relative) }
        [long]$weight = $weights[$f.Relative]
        if ($group.Count -gt 0 -and ($used + $weight) -gt $packingLimit) {
            $groups.Add([object]$group.ToArray())
            $group = New-Object 'System.Collections.Generic.List[object]'
            $used = 0
        }
        $group.Add($f)
        $used += $weight
    }
    if ($group.Count -gt 0) { $groups.Add([object]$group.ToArray()) }

    # Unusual case: mostly ZIP overhead. Ensure recursion makes progress.
    if ($groups.Count -le 1 -and $Files.Count -gt 1) {
        [int]$middle = [int][Math]::Floor($Files.Count / 2)
        [pscustomobject]@{ Files=@($Files[0..($middle-1)]) }
        [pscustomobject]@{ Files=@($Files[$middle..($Files.Count-1)]) }
        return
    }
    foreach ($g in $groups) {
        [pscustomobject]@{ Files=@($g) }
    }
}

function Add-StagedZipParts {
    param(
        [string]$Label,
        [object[]]$Dirs,
        [object[]]$Files,
        [long]$MaxSizeBytes,
        [System.Collections.Generic.List[object]]$Staged
    )
    $parts = @($Dirs) + @($Files)
    $result = New-ZipPart -Label $Label -Items $parts -OutputPath '[not yet named]'
    if ($result.Size -le $MaxSizeBytes) {
        $Staged.Add($result)
        return
    }

    # Large single files cannot be split into valid, independent ZIPs by file.
    # Do not publish any archives from this source on that error.
    if ($Files.Count -le 1) {
        $tooLarge = Get-ReadableSize $result.Size
        [IO.File]::Delete($result.TempPath)
        throw ('One source file requires a ZIP larger than ' + $MaxPartMiB + ' MiB (' + $tooLarge + '). Previous archives remain intact. Use Git LFS or a different split strategy for this file.')
    }

    try {
        $groups = @(Split-ByCompressedSize -Label $Label -Files $Files -VerifiedZipPath $result.TempPath -TargetBytes $MaxSizeBytes)
    }
    finally {
        if ([IO.File]::Exists($result.TempPath)) { [IO.File]::Delete($result.TempPath) }
    }
    Write-Host ('  Compressed result exceeds ' + $MaxPartMiB + ' MiB; splitting into ' + $groups.Count + ' group(s).')
    foreach ($set in $groups) {
        Add-StagedZipParts -Label $Label -Dirs $Dirs -Files $set.Files -MaxSizeBytes $MaxSizeBytes -Staged $Staged
    }
}

function Publish-ArchiveSet {
    param(
        [string]$Label,
        [System.Collections.Generic.List[object]]$Staged
    )
    # All new ZIPs are already complete and SHA256-verified at this point.
    # Move ALL old variations (including stale _001/_002) aside, then publish
    # the new set. On error, rollback to the original names.
    $old = @(Get-ChildItem -LiteralPath $Destination -File | Where-Object {
        $_.Name -match ('^' + [regex]::Escape($Label) + '(_[0-9]{3})?\.zip_$')
    })
    $backups = New-Object 'System.Collections.Generic.List[object]'
    $published = New-Object 'System.Collections.Generic.List[string]'
    $batchId = [guid]::NewGuid().ToString('N')
    try {
        foreach ($f in $old) {
            $back = $f.FullName + '.previous-' + $batchId + '.bak'
            [IO.File]::Move($f.FullName, $back)
            $backups.Add([pscustomobject]@{ Original=$f.FullName; Backup=$back })
        }
        for ($i=0; $i -lt $Staged.Count; $i++) {
            if ($Staged.Count -eq 1) { $name = $Label + '.zip_' }
            else { $name = ('{0}_{1:D3}.zip_' -f $Label, $i + 1) }
            $out = Join-Path $Destination $name
            [IO.File]::Move($Staged[$i].TempPath, $out)
            $published.Add($out)
            $size = [IO.FileInfo]::new($out).Length
            if ($size -ne $Staged[$i].Size -or $size -gt $LimitBytes) {
                throw ('Published file size mismatch: ' + $out)
            }
            Write-Host ('  [OK] ' + $out + ' (' + $Staged[$i].FileCount + ' files, ' + (Get-ReadableSize $size) + ')')
        }
    }
    catch {
        Write-Warning 'Publish failed. Attempting to restore ALL prior archives for this source.'
        foreach ($f in $published) {
            if ([IO.File]::Exists($f)) {
                try { [IO.File]::Delete($f) } catch { Write-Warning ('Could not remove new file: ' + $f) }
            }
        }
        foreach ($pair in $backups) {
            if ([IO.File]::Exists($pair.Backup)) {
                try { [IO.File]::Move($pair.Backup, $pair.Original) }
                catch { Write-Warning ('SAVE AND RESTORE MANUALLY: ' + $pair.Backup) }
            }
        }
        throw
    }

    # Only once the new set was published completely, retire outdated split files.
    foreach ($pair in $backups) {
        try { [IO.File]::Delete($pair.Backup) }
        catch { Write-Warning ('Old archive retained (can be manually removed): ' + $pair.Backup) }
    }
    Write-Host ('  Published ' + $Staged.Count + ' verified archive(s). Removed ' + $old.Count + ' old variant(s).')
}

Write-Host '=== FRB DocsExcel -> GitHub archive (.zip_) ==='
Write-Host ('Destination: ' + $Destination)
Write-Host ('Limit: ' + $MaxPartMiB + ' MiB per COMPRESSED ZIP (not source size)')
foreach ($source in $Sources) {
    Write-Host ''; Write-Host ('[Source] ' + $source.Root)
    if (-not [IO.Directory]::Exists($source.Root)) {
        Write-Warning ('Source folder not found; existing archives preserved: ' + $source.Root)
        $ExitCode = 1
        continue
    }
    $staged = New-Object 'System.Collections.Generic.List[object]'
    try {
        $items = @(Get-Items -Root $source.Root)
        $dirs = @($items | Where-Object { $_.IsDirectory })
        $files = @($items | Where-Object { -not $_.IsDirectory })
        [long]$total = 0
        foreach ($file in $files) { $total += $file.Size }
        Write-Host ('  Files: ' + $files.Count + ', total original: ' + (Get-ReadableSize $total))
        if ($files.Count -eq 0) {
            Write-Warning 'Empty source: skipped; previous archives preserved.'
            continue
        }
        if ($DryRun) {
            Write-Host '  [DRY RUN] Count only. Actual ZIP part count is determined AFTER compression.'
            continue
        }
        if (-not [IO.Directory]::Exists($Destination)) {
            [void][IO.Directory]::CreateDirectory($Destination)
        }
        Add-StagedZipParts -Label $source.Label -Dirs $dirs -Files $files -MaxSizeBytes $LimitBytes -Staged $staged
        # Prevent unexpected GitHub hard limit errors if custom -MaxPartMiB is increased.
        foreach ($record in $staged) {
            if ($record.Size -ge $GitHubHardLimitBytes) { throw 'GitHub 100MB hard limit exceeded. Nothing was published.' }
        }
        Publish-ArchiveSet -Label $source.Label -Staged $staged
    }
    catch {
        Write-Host ('  [ERROR] ' + $_.Exception.Message) -ForegroundColor Red
        $ExitCode = 1
    }
    finally {
        foreach ($record in $staged) {
            if ([IO.File]::Exists($record.TempPath)) {
                try { [IO.File]::Delete($record.TempPath) }
                catch { Write-Warning ('Temporary ZIP cleanup failed: ' + $record.TempPath) }
            }
        }
    }
}
if ($DryRun) { Write-Host 'DRY RUN: no ZIPs were written.' }
Write-Host ('Done. Exit code: ' + $ExitCode)
exit $ExitCode
