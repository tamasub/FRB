# Updates ONLY the Launch studio_root variable when the TEST bundle is moved.
# Avoids parsing/rewriting the entire large JSON document.
[CmdletBinding()]
param([Parameter(Mandatory=$true)][string]$BundleRoot)
$ErrorActionPreference = 'Stop'
try {
    $root = [System.IO.Path]::GetFullPath($BundleRoot)
    $studio = Join-Path $root 'Studio'
    $exe = Join-Path $studio 'NativeShell\_publish\FRBStudio.NativeShell.exe'
    if (-not (Test-Path -LiteralPath $exe -PathType Leaf)) { throw "Studio EXE missing: $exe" }
    $cfg = Join-Path $root 'config\frb_launch_sample_data_v0_1.json'
    if (-not (Test-Path -LiteralPath $cfg -PathType Leaf)) { throw "Launch config missing: $cfg" }
    $raw = [System.IO.File]::ReadAllText($cfg, [System.Text.Encoding]::UTF8)
    # Search only inside the studio_root variable object (the current schema uses this ordering).
    $pattern = '(?s)(?<head>"variable_id"\s*:\s*"studio_root"\s*,[^{}]*?"launch_value"\s*:\s*)"(?:\\.|[^"\\])*"'
    $rx = New-Object System.Text.RegularExpressions.Regex($pattern)
    $matches = $rx.Matches($raw)
    if ($matches.Count -ne 1) { throw "Expected exactly one studio_root variable entry; found $($matches.Count)." }
    $jsonString = ConvertTo-Json -InputObject $studio -Compress
    $matched = $matches[0]
    $updated = $raw.Substring(0, $matched.Index) + $matched.Groups['head'].Value + $jsonString + $raw.Substring($matched.Index + $matched.Length)
    if ($updated -ne $raw) {
        # Write atomically, no backup proliferation; sources and other config fields stay intact.
        $temp = $cfg + '.studio_root.tmp'
        [System.IO.File]::WriteAllText($temp, $updated, (New-Object System.Text.UTF8Encoding($false)))
        [System.IO.File]::Copy($temp, $cfg, $true)
        Remove-Item -LiteralPath $temp -Force
    }
    Write-Host "[OK] studio_root -> $studio"
    exit 0
} catch {
    Write-Host ('[ERROR] ' + $_.Exception.Message) -ForegroundColor Red
    exit 1
}
