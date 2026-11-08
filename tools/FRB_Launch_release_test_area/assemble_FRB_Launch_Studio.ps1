# FRB Launch + Studio - portable test-bundle assembler v0.3 (Windows PowerShell 5.1 compatible)
# Sources are read-only. Existing output is never overwritten or deleted.
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$LaunchSource,
    [Parameter(Mandatory = $true)][string]$StudioSource,
    [Parameter(Mandatory = $true)][string]$OutputParent,
    [Parameter(Mandatory = $true)][string]$ToolDir
)
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

function FullPath([string]$p) {
    return [System.IO.Path]::GetFullPath($p.Trim().Trim('"'))
}
function RequireFile([string]$p) {
    if (-not [System.IO.File]::Exists($p)) { throw "Required file not found: $p" }
}
function RequireDir([string]$p) {
    if (-not [System.IO.Directory]::Exists($p)) { throw "Required directory not found: $p" }
}
function CopyDir([string]$from, [string]$to) {
    RequireDir $from
    New-Item -ItemType Directory -Force -Path $to | Out-Null
    # Robocopy keeps file contents and timestamps, including hidden runtime files.
    & robocopy.exe $from $to /E /R:1 /W:1 /XJ /NFL /NDL /NJH /NJS /NP | Out-Null
    if ($LASTEXITCODE -ge 8) { throw "Copy failed ($LASTEXITCODE): $from -> $to" }
}
function Under([string]$p, [string]$root) {
    $a = (FullPath $p).TrimEnd('\') + '\'
    $b = (FullPath $root).TrimEnd('\') + '\'
    return $a.StartsWith($b, [StringComparison]::OrdinalIgnoreCase)
}

try {
    $launchInput = FullPath $LaunchSource
    $studioInput = FullPath $StudioSource
    $output = FullPath $OutputParent
    $tool = FullPath $ToolDir

    if (Test-Path (Join-Path $launchInput 'FRBLaunch.exe')) {
        $launchDist = $launchInput
        $launchProject = FullPath (Join-Path $launchDist '..\..')
    } elseif (Test-Path (Join-Path $launchInput 'dist\FRBLaunch\FRBLaunch.exe')) {
        $launchProject = $launchInput
        $launchDist = Join-Path $launchProject 'dist\FRBLaunch'
    } else {
        throw "Launch EXE not found. Specify the project root or dist\FRBLaunch: $launchInput"
    }
    # Marker is written only by the patched Launch _build_windows.bat after a successful build.
    # A stale pre-patch EXE cannot reliably resolve Studio after relocation.
    RequireFile (Join-Path $launchDist 'portable_studio_ready.txt')
    RequireFile (Join-Path $launchProject 'config\frb_launch_sample_data_v0_1.json')
    RequireDir (Join-Path $launchProject 'scripts')
    RequireDir (Join-Path $launchProject 'defs')

    if (Test-Path (Join-Path $studioInput 'FRBStudio.NativeShell.exe')) {
        $studioRoot = FullPath (Join-Path $studioInput '..\..')
    } else {
        $studioRoot = $studioInput
    }
    $studioPublish = Join-Path $studioRoot 'NativeShell\_publish'
    RequireFile (Join-Path $studioPublish 'FRBStudio.NativeShell.exe')
    RequireFile (Join-Path $studioRoot 'wwwroot\index.html')
    RequireDir (Join-Path $studioRoot 'data\json')
    RequireDir (Join-Path $studioRoot 'defs')
    RequireFile (Join-Path $tool '_set_portable_studio_root.ps1')
    RequireFile (Join-Path $tool 'test_set_portable_studio_root.ps1')

    $target = Join-Path $output 'FRB_Launch'
    # No accidental source-folder replacement or recursive copy.
    if ((Under $target $launchDist) -or (Under $target $studioRoot) -or
        (Under $launchDist $target) -or (Under $studioRoot $target)) {
        throw "Output overlaps with a source folder: $target"
    }
    if (Test-Path $target) {
        throw "Output exists: $target`nRename/delete the old TEST bundle manually, or choose a new output parent."
    }

    Write-Host '[0/5] Preflight test for portable JSON editor...'
    & powershell.exe -NoProfile -ExecutionPolicy Bypass -File (Join-Path $tool 'test_set_portable_studio_root.ps1') -ConfigSource (Join-Path $launchProject 'config\frb_launch_sample_data_v0_1.json')
    if ($LASTEXITCODE -ne 0) { throw 'Preflight portable JSON editor failed; nothing copied.' }

    Write-Host '[1/5] Copy Launch dist...'
    New-Item -ItemType Directory -Force -Path $target | Out-Null
    CopyDir $launchDist $target
    Write-Host '[2/5] Copy editable Launch config, defs, scripts...'
    foreach ($name in @('config', 'defs', 'scripts')) {
        CopyDir (Join-Path $launchProject $name) (Join-Path $target $name)
    }
    # dist/FRBLaunch/launch_home.json normally points to ../.. (the developer's source).
    # Set to '.' so the bundle is self-contained.
    [System.IO.File]::WriteAllText(
        (Join-Path $target 'launch_home.json'),
        '{"launch_home":"."}' + "`r`n",
        (New-Object System.Text.UTF8Encoding($false)))

    Write-Host '[3/5] Copy Studio executable and runtime resources...'
    $dstStudio = Join-Path $target 'Studio'
    CopyDir $studioPublish (Join-Path $dstStudio 'NativeShell\_publish')
    foreach ($name in @('wwwroot', 'defs', 'fielddefs', 'studio_overlays', 'tools')) {
        $source = Join-Path $studioRoot $name
        if (Test-Path $source -PathType Container) {
            CopyDir $source (Join-Path $dstStudio $name)
        }
    }
    # Test bundle: Copy all existing Studio JSONs to preserve current functionality.
    # WARNING: Such JSONs may contain private research or individual-specific data.
    CopyDir (Join-Path $studioRoot 'data\json') (Join-Path $dstStudio 'data\json')
    New-Item -ItemType Directory -Force -Path (Join-Path $dstStudio 'data\markdown') | Out-Null
    # Keep runtime config beside EXE, as NativeShell checks this path first.
    $dstConfig = Join-Path $dstStudio 'NativeShell\_publish\native_shell.config.json'
    if (-not (Test-Path $dstConfig)) {
        Copy-Item -LiteralPath (Join-Path $studioRoot 'NativeShell\native_shell.config.json') -Destination $dstConfig
    }

    Write-Host '[4/5] Set relative Studio variable and verify folder structure...'
    # The patched EXE computes Studio root dynamically. Do NOT bind it to an
    # absolute value during assembly, or the package will retain this PC's path.
    & powershell.exe -NoProfile -ExecutionPolicy Bypass -File (Join-Path $tool '_set_portable_studio_root.ps1') -BundleRoot $target
    if ($LASTEXITCODE -ne 0) { throw 'Portable variable initialization failed.' }
    Copy-Item -LiteralPath (Join-Path $tool 'Start_FRB_Launch.bat') -Destination (Join-Path $target 'Start_FRB_Launch.bat')
    foreach ($relative in @(
        'FRBLaunch.exe', 'launch_home.json', 'config\frb_launch_sample_data_v0_1.json',
        'Studio\NativeShell\_publish\FRBStudio.NativeShell.exe',
        'Studio\NativeShell\_publish\native_shell.config.json',
        'Studio\wwwroot\index.html'
    )) { RequireFile (Join-Path $target $relative) }
    foreach ($relative in @('Studio\data\json', 'Studio\defs')) {
        RequireDir (Join-Path $target $relative)
    }

    $notice = @'
TEST BUNDLE - NOT READY FOR PUBLIC RELEASE

The bundled FRBLaunch.exe is rebuilt with bundled_studio_root_v1.
It resolves <EXE directory>\Studio on EVERY launch, including direct EXE launch,
without using a build-machine absolute path or the working directory.

Launch config uses studio_root=Studio as an informational fallback value.
The patched runtime overrides it only when bundled Studio EXE exists.
Start_FRB_Launch.bat simply changes working directory and starts the app.

IMPORTANT: Shut down any already-running FRB Launch from the task tray before
moving/testing. FRB Launch uses a single-instance lock ACROSS ALL installations.

Contains current Launch config and Studio data/json from the developer machine.
These can contain private paths, personal information and research records.
DO NOT UPLOAD THIS TEST BUNDLE TO VECTOR.

This assembler does not compile EXEs. Before assembling, patch Launch source
and rebuild dist using _build_windows.bat. No developer data is modified by
this assembler. Tests on a clean Windows PC are still required.
'@
    [System.IO.File]::WriteAllText((Join-Path $target 'TEST_ONLY_DO_NOT_UPLOAD.txt'), $notice, (New-Object System.Text.UTF8Encoding($false)))
    Write-Host '[5/5] Done.'
    Write-Host "Bundle: $target"
    Write-Host 'Launch: FRBLaunch.exe (direct start OK after patch/rebuild)'
    Write-Host 'WARNING: This TEST bundle contains development data. Do NOT upload to Vector.'
    exit 0
} catch {
    Write-Host ('[ERROR] ' + $_.Exception.Message) -ForegroundColor Red
    exit 1
}
