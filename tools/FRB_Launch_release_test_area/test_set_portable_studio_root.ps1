# Portable JSON setter regression test (Windows PowerShell 5.1 / v0.4)
# ASCII-only source file: Windows PowerShell 5.1 may decode UTF-8 without BOM as ANSI.
# This test constructs real Japanese Unicode text at runtime, then writes UTF-8 JSON.
[CmdletBinding()]
param([string]$ConfigSource)
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$dir = Join-Path ([System.IO.Path]::GetTempPath()) ('frb_studio_root_test_' + [guid]::NewGuid().ToString('N'))
$utf8 = New-Object System.Text.UTF8Encoding($false)
try {
    $cfgDir = Join-Path $dir 'config'
    New-Item -Path $cfgDir -ItemType Directory -Force | Out-Null
    $cfg = Join-Path $cfgDir 'frb_launch_sample_data_v0_1.json'

    # Generate genuine Japanese characters without embedding multibyte literals
    # in this PowerShell 5.1 script source.
    $jpTitle = -join @([char]0x65E5, [char]0x672C, [char]0x8A9E, [char]0x306E, [char]0x8AAC, [char]0x660E)
    $jpKeep = -join @([char]0x4FDD, [char]0x6301, [char]0x3059, [char]0x308B)
    $original = @'
{
  "launch_variables": [
    {"variable_id":"studio_root","title":"__TITLE__","launch_value":"C:\\Previous\\Studio"},
    {"variable_id":"another","launch_value":"other value", "title":"__KEEP__"}
  ],
  "some_other_value": "studio_root may appear in strings but not as a variable"
}
'@
    $original = $original.Replace('__TITLE__', $jpTitle).Replace('__KEEP__', $jpKeep)
    $initialDoc = ConvertFrom-Json -InputObject $original
    if ($initialDoc.launch_variables[0].title -cne $jpTitle) {
        throw 'Preflight fixture Unicode text did not survive JSON parse.'
    }

    [System.IO.File]::WriteAllText($cfg, $original, $utf8)
    & powershell.exe -NoProfile -ExecutionPolicy Bypass -File (Join-Path $here '_set_portable_studio_root.ps1') -BundleRoot $dir
    if ($LASTEXITCODE -ne 0) { throw 'Test: portable setter exited non-zero.' }

    $expected = $original.Replace('"launch_value":"C:\\Previous\\Studio"', '"launch_value":"Studio"')
    $actual = [System.IO.File]::ReadAllText($cfg, [System.Text.Encoding]::UTF8)
    if ($actual -cne $expected) {
        throw 'Test: non-target characters changed, or studio_root was not updated.'
    }
    $parsed = ConvertFrom-Json -InputObject $actual
    if ($parsed.launch_variables[0].title -cne $jpTitle -or $parsed.launch_variables[1].title -cne $jpKeep) {
        throw 'Test: Japanese field contents were changed.'
    }
    Write-Host '[PASS] UTF-8 JSON retains Japanese characters and non-target fields.'

    & powershell.exe -NoProfile -ExecutionPolicy Bypass -File (Join-Path $here '_set_portable_studio_root.ps1') -BundleRoot $dir
    if ($LASTEXITCODE -ne 0) { throw 'Test: second setter call failed.' }
    $again = [System.IO.File]::ReadAllText($cfg, [System.Text.Encoding]::UTF8)
    if ($again -cne $actual) { throw 'Test: setter is not idempotent.' }
    Write-Host '[PASS] Second run is idempotent.'

    if ($ConfigSource) {
        # Preflight uses a temporary copy; original development config is immutable.
        if (-not (Test-Path -LiteralPath $ConfigSource -PathType Leaf)) {
            throw "Current Launch config not found: $ConfigSource"
        }
        $hashBefore = (Get-FileHash -LiteralPath $ConfigSource -Algorithm SHA256).Hash
        Copy-Item -LiteralPath $ConfigSource -Destination $cfg -Force
        & powershell.exe -NoProfile -ExecutionPolicy Bypass -File (Join-Path $here '_set_portable_studio_root.ps1') -BundleRoot $dir
        if ($LASTEXITCODE -ne 0) { throw 'Test: current Launch config could not be patched.' }
        $doc = ConvertFrom-Json -InputObject ([System.IO.File]::ReadAllText($cfg, [System.Text.Encoding]::UTF8))
        $entry = @($doc.launch_variables | Where-Object { $_.variable_id -eq 'studio_root' })
        if ($entry.Count -ne 1 -or $entry[0].launch_value -cne 'Studio') {
            throw 'Test: current Launch config does not contain studio_root=Studio.'
        }
        $hashAfter = (Get-FileHash -LiteralPath $ConfigSource -Algorithm SHA256).Hash
        if ($hashBefore -cne $hashAfter) { throw 'Test: development config unexpectedly changed.' }
        Write-Host '[PASS] Current Launch config patched in temp; development config unchanged.'
    }
    Write-Host 'ALL PASS'
    exit 0
} catch {
    Write-Host ('[FAIL] ' + $_.Exception.Message) -ForegroundColor Red
    exit 1
} finally {
    if (Test-Path -LiteralPath $dir) {
        Remove-Item -LiteralPath $dir -Recurse -Force
    }
}
