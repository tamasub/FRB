param([switch]$Remove)
$ErrorActionPreference = 'Stop'
# The user's Startup folder works with redirected profiles and OneDrive.
$startup = [Environment]::GetFolderPath('Startup')
$linkPath = Join-Path $startup 'FRB Launch.lnk'
if ($Remove) {
    if (Test-Path -LiteralPath $linkPath) { Remove-Item -LiteralPath $linkPath -Force }
    Write-Host 'FRB Launch: Windows startup disabled.'
    exit 0
}
$projectRoot = Split-Path -Parent $PSScriptRoot
$exe = Join-Path $projectRoot 'dist\FRBLaunch\FRBLaunch.exe'
if (-not (Test-Path -LiteralPath $exe -PathType Leaf)) {
    throw "EXE not found: $exe`nRun build_windows.bat first."
}
$sh = New-Object -ComObject WScript.Shell
$shortcut = $sh.CreateShortcut($linkPath)
$shortcut.TargetPath = $exe
$shortcut.WorkingDirectory = Split-Path -Parent $exe
$shortcut.Description = 'FRB Launch: desktop empty-space double-click'
$shortcut.IconLocation = "$exe,0"
$shortcut.Save()
Write-Host "FRB Launch: Windows startup enabled. $linkPath"
