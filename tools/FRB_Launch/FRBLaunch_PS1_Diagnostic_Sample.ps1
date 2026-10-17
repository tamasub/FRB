# FRB Launch - simple PowerShell execution test (works on Windows PowerShell 5.1).
# No administrator privileges required. Does not change execution policy.
$ErrorActionPreference = 'Stop'
$stamp = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
$log = Join-Path $env:TEMP 'FRBLaunch_PS1_Test.log'
"[$stamp] PS1 execution OK (pid=$PID)" | Add-Content -LiteralPath $log -Encoding UTF8
Write-Host "[SUCCESS] FRB Launch PS1 script executed at $stamp"
Write-Host "Log: $log"
$shell = New-Object -ComObject WScript.Shell
[void]$shell.Popup("PowerShell script ran successfully!`n$stamp", 0, 'FRB Launch PS1 Test', 64)
