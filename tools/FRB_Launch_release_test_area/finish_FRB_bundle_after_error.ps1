# Finish the v0.2 bundle that stopped at step [4/5].
# Never removes files and never changes developer source directories.
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$BundleRoot,
    [Parameter(Mandatory = $true)][string]$ToolDir
)
$ErrorActionPreference = 'Stop'
try {
    $root = [System.IO.Path]::GetFullPath($BundleRoot.Trim().Trim('"'))
    $tool = [System.IO.Path]::GetFullPath($ToolDir.Trim().Trim('"'))
    foreach ($relative in @(
        'FRBLaunch.exe',
        'portable_studio_ready.txt',
        'launch_home.json',
        'config\frb_launch_sample_data_v0_1.json',
        'Studio\NativeShell\_publish\FRBStudio.NativeShell.exe',
        'Studio\wwwroot\index.html')) {
        $p = Join-Path $root $relative
        if (-not (Test-Path -LiteralPath $p -PathType Leaf)) { throw "Required bundled file missing: $p" }
    }
    foreach ($relative in @('Studio\data\json', 'Studio\defs')) {
        $p = Join-Path $root $relative
        if (-not (Test-Path -LiteralPath $p -PathType Container)) { throw "Required folder missing: $p" }
    }
    Write-Host '[4/5] Resume portable configuration...'
    & powershell.exe -NoProfile -ExecutionPolicy Bypass -File (Join-Path $tool '_set_portable_studio_root.ps1') -BundleRoot $root
    if ($LASTEXITCODE -ne 0) { throw 'Portable variable initialization failed.' }
    Copy-Item -LiteralPath (Join-Path $tool 'Start_FRB_Launch.bat') -Destination (Join-Path $root 'Start_FRB_Launch.bat') -Force
    [System.IO.File]::WriteAllText(
        (Join-Path $root 'TEST_ONLY_DO_NOT_UPLOAD.txt'),
        "TEST BUNDLE - NOT READY FOR PUBLIC RELEASE`r`nContains developer Launch settings and Studio research data.`r`nDo not upload to Vector.`r`n",
        (New-Object System.Text.UTF8Encoding($false)))
    Write-Host '[5/5] Bundle recovered successfully.'
    Write-Host "Bundle: $root"
    Write-Host 'Shut down any tray-resident FRB Launch, then launch FRBLaunch.exe directly.'
    exit 0
} catch {
    Write-Host ('[ERROR] ' + $_.Exception.Message) -ForegroundColor Red
    exit 1
}
