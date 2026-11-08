# Standalone regression test for Windows PowerShell 5.1 (no developer files touched).
[CmdletBinding()]
param([string]$ConfigSource)
$ErrorActionPreference = 'Stop'
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$dir = Join-Path ([System.IO.Path]::GetTempPath()) ('frb_studio_root_test_' + [guid]::NewGuid().ToString('N'))
try {
    $cfgDir = Join-Path $dir 'config'
    New-Item -Path $cfgDir -ItemType Directory -Force | Out-Null
    $cfg = Join-Path $cfgDir 'frb_launch_sample_data_v0_1.json'
    $original = @'
{
  "launch_variables": [
    {"variable_id":"studio_root","title":"日本語の説明","launch_value":"C:\\Previous\\Studio"},
    {"variable_id":"another","launch_value":"other value", "title":"保持する"}
  ],
  "some_other_value": "studio_root may appear in strings but not as a variable"
}
'@
    [System.IO.File]::WriteAllText($cfg, $original, (New-Object System.Text.UTF8Encoding($false)))
    & powershell.exe -NoProfile -ExecutionPolicy Bypass -File (Join-Path $here '_set_portable_studio_root.ps1') -BundleRoot $dir
    if ($LASTEXITCODE -ne 0) { throw 'Test: setter exited non-zero.' }
    $expected = $original.Replace('"launch_value":"C:\\Previous\\Studio"', '"launch_value":"Studio"')
    $actual = [System.IO.File]::ReadAllText($cfg, [System.Text.Encoding]::UTF8)
    if ($actual -cne $expected) { throw 'Test: non-target bytes changed, or studio_root was not updated.' }
    Write-Host '[PASS] JSON string replacement preserves all other fields and Japanese text.'
    & powershell.exe -NoProfile -ExecutionPolicy Bypass -File (Join-Path $here '_set_portable_studio_root.ps1') -BundleRoot $dir
    if ($LASTEXITCODE -ne 0) { throw 'Test: second setter call failed.' }
    $actual2 = [System.IO.File]::ReadAllText($cfg, [System.Text.Encoding]::UTF8)
    if ($actual2 -cne $actual) { throw 'Test: setter is not idempotent.' }
    Write-Host '[PASS] Second run is idempotent.'
    if ($ConfigSource) {
        # Validate the exact current Launch config against the patch, using a TEMP COPY.
        # The developer source file is never written.
        Copy-Item -LiteralPath $ConfigSource -Destination $cfg -Force
        & powershell.exe -NoProfile -ExecutionPolicy Bypass -File (Join-Path $here '_set_portable_studio_root.ps1') -BundleRoot $dir
        if ($LASTEXITCODE -ne 0) { throw 'Test: current Launch config cannot be patched.' }
        $doc = ConvertFrom-Json -InputObject ([System.IO.File]::ReadAllText($cfg, [System.Text.Encoding]::UTF8))
        $entry = @($doc.launch_variables | Where-Object { $_.variable_id -eq 'studio_root' })
        if ($entry.Count -ne 1 -or $entry[0].launch_value -cne 'Studio') {
            throw 'Test: current Launch config does not contain studio_root=Studio.'
        }
        Write-Host '[PASS] Exact current Launch config accepted (source unchanged).'
    }
    Write-Host 'ALL PASS'
} catch {
    Write-Host ('[FAIL] ' + $_.Exception.Message) -ForegroundColor Red
    exit 1
} finally {
    if (Test-Path -LiteralPath $dir) { Remove-Item -LiteralPath $dir -Recurse -Force }
}
