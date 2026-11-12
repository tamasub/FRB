# FRB Launch user settings / diagnostics ZIP backup sample (Windows PowerShell 5.1+).
# Only user-authored settings, state and diagnostics are included.  In particular
# Qt WebEngine's web_profile (cookies/cache/database files) is NEVER traversed.
# The self-contained backup goes to %LOCALAPPDATA%\FRBLaunch\_Backups.
$ErrorActionPreference = 'Stop'
$archive = $null
$stream = $null
$tempPath = $null
$completed = $false
$script:entryCount = 0
$script:skippedLogEntries = New-Object System.Collections.Generic.List[string]

function Add-LiveLogFile {
    param(
        [Parameter(Mandatory=$true)][string]$SourceFile,
        [Parameter(Mandatory=$true)][string]$EntryName,
        [Parameter(Mandatory=$true)][System.IO.Compression.ZipArchive]$Destination
    )

    # Open active logs with cooperative sharing; unlike configuration files,
    # diagnostics are optional when a writer denies even shared read access.
    $inputStream = $null
    $shareMode = [System.IO.FileShare]::ReadWrite -bor [System.IO.FileShare]::Delete
    try {
        $inputStream = [System.IO.File]::Open(
            $SourceFile, [System.IO.FileMode]::Open,
            [System.IO.FileAccess]::Read, $shareMode)
    } catch [System.IO.IOException] {
        $script:skippedLogEntries.Add($EntryName)
        Write-Host ('[WARN] Active log skipped: ' + $EntryName) -ForegroundColor Yellow
        return
    }

    try {
        $entry = $Destination.CreateEntry(
            $EntryName, [System.IO.Compression.CompressionLevel]::Optimal)
        $outputStream = $entry.Open()
        try {
            # Do not chase a log that is being appended while we back it up.
            $remaining = [long]$inputStream.Length
            $buffer = New-Object 'byte[]' 65536
            while ($remaining -gt 0) {
                $amount = [int][Math]::Min([long]$buffer.Length, $remaining)
                $read = $inputStream.Read($buffer, 0, $amount)
                if ($read -le 0) { break }
                $outputStream.Write($buffer, 0, $read)
                $remaining -= $read
            }
        } finally {
            $outputStream.Dispose()
        }
        $script:entryCount++
    } finally {
        $inputStream.Dispose()
    }
}

function Add-BackupDirectory {
    param(
        [Parameter(Mandatory=$true)][string]$Source,
        [Parameter(Mandatory=$true)][string]$EntryPrefix,
        [Parameter(Mandatory=$true)][System.IO.Compression.ZipArchive]$Destination,
        [switch]$DiagnosticOnly
    )

    if (-not (Test-Path -LiteralPath $Source -PathType Container)) {
        return
    }

    # Enumerate without following junction/symlink paths.
    $stack = New-Object System.Collections.Stack
    $stack.Push(@($Source, $EntryPrefix))
    while ($stack.Count -gt 0) {
        $current = $stack.Pop()
        $folder = [string]$current[0]
        $prefix = [string]$current[1]
        foreach ($child in (Get-ChildItem -LiteralPath $folder -Force -ErrorAction Stop)) {
            if (($child.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -ne 0) {
                continue
            }
            # Log folders must not accidentally include runtime lock markers.
            if ($DiagnosticOnly -and $child.Name -match '(?i)\.(lock|lck|tmp)$') {
                continue
            }
            $entryName = ($prefix + '/' + $child.Name).Replace('\', '/')
            if ($child.PSIsContainer) {
                $stack.Push(@($child.FullName, $entryName))
            } elseif ($DiagnosticOnly) {
                Add-LiveLogFile -SourceFile $child.FullName `
                    -EntryName $entryName -Destination $Destination
            } else {
                [void][System.IO.Compression.ZipFileExtensions]::CreateEntryFromFile(
                    $Destination,
                    $child.FullName,
                    $entryName,
                    [System.IO.Compression.CompressionLevel]::Optimal
                )
                $script:entryCount++
            }
        }
    }
}

function Add-UserSettingsAndLogs {
    param(
        [Parameter(Mandatory=$true)][string]$Source,
        [Parameter(Mandatory=$true)][System.IO.Compression.ZipArchive]$Destination
    )

    # IMPORTANT: allowlist the LocalAppData root instead of recursively
    # archiving everything.  Qt WebEngine's web_profile/data/Cookies and other
    # live browser databases are outside the backup scope entirely.
    # Root-level JSON / INI: settings, favorites, searches, navigation history.
    # Root-level logs and conventional diagnostic folders: best-effort logs.
    # All other directories and runtime/cache files are deliberately ignored.
    foreach ($child in (Get-ChildItem -LiteralPath $Source -Force -ErrorAction Stop)) {
        if (($child.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -ne 0) {
            continue
        }
        if ($child.PSIsContainer) {
            if ($child.Name -match '(?i)^(log|logs|diagnostic|diagnostics)$') {
                Add-BackupDirectory -Source $child.FullName `
                    -EntryPrefix ('user_data/' + $child.Name) `
                    -Destination $Destination -DiagnosticOnly
            } elseif ($child.Name -ieq '_Backups' -or $child.Name -ieq 'web_profile') {
                Write-Host ('[INFO] Backup/runtime/browser directory excluded: user_data/' +
                    $child.Name)
            } else {
                Write-Host ('[INFO] Unlisted user-data directory excluded: user_data/' +
                    $child.Name)
            }
            continue
        }

        $name = [string]$child.Name
        $entryName = 'user_data/' + $name
        $isDiagnosticLog = ($name -match '(?i)\.log($|[._-])')
        $isSettingsFile = ($name -match '(?i)\.(json|ini)$')
        $isRuntimeFile = (
            $name -match '(?i)\.(lock|lck|tmp)$' -or
            $name -match '(?i)^file_index\.db(?:-wal|-shm|-journal)?$' -or
            $name -match '(?i)^\.file_index_.*\.db$' -or
            $name -match '(?i)^apps_scan_.*\.json$' -or
            $name -match '(?i)^apps_cache\.json$'
        )
        if ($isRuntimeFile) {
            Write-Host ('[INFO] Runtime/cache file excluded: ' + $entryName)
            continue
        }
        if ($isDiagnosticLog) {
            Add-LiveLogFile -SourceFile $child.FullName `
                -EntryName $entryName -Destination $Destination
        } elseif ($isSettingsFile) {
            # User settings/history failures must not be silently skipped.
            [void][System.IO.Compression.ZipFileExtensions]::CreateEntryFromFile(
                $Destination,
                $child.FullName,
                $entryName,
                [System.IO.Compression.CompressionLevel]::Optimal
            )
            $script:entryCount++
        } else {
            Write-Host ('[INFO] Unlisted user-data file excluded: ' + $entryName)
        }
    }
}

try {
    Add-Type -AssemblyName System.IO.Compression
    Add-Type -AssemblyName System.IO.Compression.FileSystem

    # Derive LaunchHome from the installed script path, never from cmd arguments.
    if ([string]::IsNullOrWhiteSpace($PSScriptRoot)) {
        throw 'Cannot resolve the PowerShell script directory.'
    }
    $root = Split-Path -Parent $PSScriptRoot
    if (-not (Test-Path -LiteralPath $root -PathType Container)) {
        throw "Cannot find Launch directory: $root"
    }
    $configDir = Join-Path $root 'config'
    $requiredJson = Join-Path $configDir 'frb_launch_data.json'
    if (-not (Test-Path -LiteralPath $requiredJson -PathType Leaf)) {
        throw "Cannot find Launch settings JSON: $requiredJson"
    }

    # Keep backups out of the user's home directory; never copy _Backups back
    # into itself (the allowlist never recurses into that directory).
    $localAppData = [Environment]::GetFolderPath('LocalApplicationData')
    if ([string]::IsNullOrWhiteSpace($localAppData)) {
        throw 'Cannot resolve LocalApplicationData.'
    }
    $userDataDir = Join-Path $localAppData 'FRBLaunch'
    $outDir = Join-Path $userDataDir '_Backups'
    [void](New-Item -ItemType Directory -Force -Path $outDir)

    $timestamp = Get-Date -Format 'yyyyMMdd_HHmmss'
    $basename = 'FRBLaunch_Backup_' + $timestamp
    $zipPath = Join-Path $outDir ($basename + '.zip')
    $serial = 2
    while ((Test-Path -LiteralPath $zipPath) -or
           (Test-Path -LiteralPath ($zipPath + '.partial'))) {
        $zipPath = Join-Path $outDir ($basename + '_' + $serial + '.zip')
        $serial++
    }
    $tempPath = $zipPath + '.partial'

    $stream = [System.IO.File]::Open(
        $tempPath,
        [System.IO.FileMode]::CreateNew,
        [System.IO.FileAccess]::Write,
        [System.IO.FileShare]::None
    )
    $archive = [System.IO.Compression.ZipArchive]::new(
        $stream,
        [System.IO.Compression.ZipArchiveMode]::Create,
        $false,
        [System.Text.Encoding]::UTF8
    )

    # Launch's own config and ViewDefs remain strict/complete backups.
    Add-BackupDirectory -Source $configDir -EntryPrefix 'config' -Destination $archive
    Add-BackupDirectory -Source (Join-Path $root 'defs\launch') `
        -EntryPrefix 'defs/launch' -Destination $archive
    # Only persistent user settings and optional diagnostics, NOT web_profile.
    Add-UserSettingsAndLogs -Source $userDataDir -Destination $archive

    if ($script:entryCount -lt 1) {
        throw 'No files were found to back up.'
    }
    $archive.Dispose()
    $archive = $null
    $stream = $null
    [System.IO.File]::Move($tempPath, $zipPath)
    $completed = $true

    Write-Host ('[OK] Files: ' + $script:entryCount)
    if ($script:skippedLogEntries.Count -gt 0) {
        Write-Host ('[WARN] Skipped active diagnostic log(s): ' +
                    $script:skippedLogEntries.Count) -ForegroundColor Yellow
        Write-Host '[WARN] Settings were backed up; skipped logs are not in this ZIP.' -ForegroundColor Yellow
    }
    Write-Host ('[OK] Backup ZIP: ' + $zipPath)
    Write-Host '[INFO] Browser cookies/sessions are not included; re-login may be needed after restore.'
    Write-Host '[INFO] ZIP contains personal settings and logs; do not publish or share it as-is.'

    # Convenience only: after the ZIP has been committed, open its containing
    # directory in Explorer. A shell-launch error must NOT mark a valid backup
    # as failed. Use the resolved LocalAppData location, never a user-specific path.
    try {
        Start-Process -FilePath 'explorer.exe' -ArgumentList ('"' + $outDir + '"') -ErrorAction Stop | Out-Null
        Write-Host ('[INFO] Opening backup folder: ' + $outDir)
    } catch {
        Write-Host ('[WARN] Backup ZIP was created, but Explorer could not open: ' +
                    $_.Exception.Message) -ForegroundColor Yellow
    }
} catch {
    Write-Host ('[ERROR] ' + $_.Exception.Message) -ForegroundColor Red
    exit 1
} finally {
    if ($null -ne $archive) {
        $archive.Dispose()
    } elseif ($null -ne $stream) {
        $stream.Dispose()
    }
    if (-not $completed -and $tempPath -and (Test-Path -LiteralPath $tempPath)) {
        Remove-Item -LiteralPath $tempPath -Force -ErrorAction SilentlyContinue
    }
}
