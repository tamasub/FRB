# studio_work_0269 Step 4: Windows 11 / PowerShell 5.1+ filesystem smoke test.
# Uses disposable fixture data ONLY. Never targets the user's production JSON.
param(
    [string]$NodeExecutable = 'node',
    [switch]$KeepFixture
)
$ErrorActionPreference = 'Stop'
if ($env:OS -ne 'Windows_NT') { throw 'Windows smoke requires Windows_NT.' }
$root = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$cli = Join-Path $root 'tools/change_core/cli.mjs'
$testDir = Join-Path ([IO.Path]::GetTempPath()) ('frb-change-core-0269-' + [Guid]::NewGuid().ToString('N'))
$docFile = Join-Path $testDir 'temporary-launch.json'
$configFile = Join-Path $testDir 'trusted-config.json'
$utf8 = New-Object System.Text.UTF8Encoding($false)
$passCount = 0
function Write-Utf8NoBom([string]$p, [string]$value) {
    [IO.File]::WriteAllText($p, $value, $utf8)
}
function Write-Json([string]$p, $obj) {
    Write-Utf8NoBom $p ($obj | ConvertTo-Json -Depth 40)
}
function Get-Sha([string]$p) {
    $bytes = [IO.File]::ReadAllBytes($p)
    $hasher = [Security.Cryptography.SHA256]::Create()
    try { return ([BitConverter]::ToString($hasher.ComputeHash($bytes))).Replace('-', '').ToLowerInvariant() }
    finally { $hasher.Dispose() }
}
function Assert-Equal($actual, $expected, [string]$description) {
    if ($actual -ne $expected) { throw "FAIL: $description (actual=$actual, expected=$expected)" }
    $script:passCount++
    Write-Host "PASS: $description"
}
function Invoke-ChangeCore($request) {
    $json = $request | ConvertTo-Json -Depth 40 -Compress
    # A stdin pipe is used exactly as Python/Launch uses it; no server/Port.
    $output = $json | & $NodeExecutable $cli --config $configFile
    $code = $LASTEXITCODE
    if (-not $output) { throw "No CLI JSON response (exit=$code)" }
    return @{ exit_code=$code; result=($output | Out-String | ConvertFrom-Json) }
}
function New-Request([string]$base, [string]$mode) {
    return @{
        schema_version = 'studio_changeset_v0_1'
        request_id = 'windows-smoke-0269'
        mode = $mode
        document_ref = 'fixture'
        base_sha256 = $base
        view_def = 'launch/frb_launch_maintenance_view_def_v0_1.json'
        view_id = 'items_view'
        operations = @(@{
            operation = 'add'
            section_id = 'items'
            placement = @{group_id='work'; parent_id='folders'; position='end'}
            records = @(
                @{title='Smoke A'; item_kind='command'; launch_actions=@(@{ launch_action_type='Open'; launch_target='C:\A.txt'})},
                @{title='Smoke B'; item_kind='command'; launch_actions=@(@{ launch_action_type='Open'; launch_target='C:\A.txt'})}
            )
        })
    }
}
New-Item -Path $testDir -ItemType Directory -Force | Out-Null
try {
    Write-Json $docFile @{
        title = 'Windows smoke fixture'
        pages = @(@{page_id='work';title='Work'})
        items = @(@{item_id='folders';parent_item_id='';page_id='work';sort_order=10;title='Folder';item_kind='category'})
    }
    Write-Json $configFile @{
        schema_version='studio_change_core_config_v0_1'
        documents=@{fixture=@{path=$docFile;view_def='launch/frb_launch_maintenance_view_def_v0_1.json';view_id='items_view';section_ids=@('items')}}
    }
    $base = Get-Sha $docFile
    $preview = Invoke-ChangeCore (New-Request $base 'dry_run')
    Assert-Equal $preview.result.status 'PREVIEW' 'dry_run returns PREVIEW'
    Assert-Equal (Get-Sha $docFile) $base 'dry_run does not change JSON bytes'

    $commit = Invoke-ChangeCore (New-Request $base 'commit')
    Assert-Equal $commit.result.status 'COMMITTED' 'two Add operations commit together'
    $after = Get-Sha $docFile
    Assert-Equal ((Get-Content -LiteralPath $docFile -Raw -Encoding UTF8 | ConvertFrom-Json).items.Count) 3 'all new rows persisted'
    $stale = Invoke-ChangeCore (New-Request $base 'commit')
    Assert-Equal $stale.result.status 'CONFLICT' 'stale SHA returns conflict'
    Assert-Equal (Get-Sha $docFile) $after 'stale SHA leaves file unchanged'

    $lockedPath = $docFile + '.studio-changeset.lock'
    Write-Utf8NoBom $lockedPath 'held by test'
    try {
        $locked = Invoke-ChangeCore (New-Request $after 'commit')
        Assert-Equal $locked.result.errors[0].code 'LOCKED' 'cooperating writer lock detected'
        Assert-Equal (Get-Sha $docFile) $after 'cooperative lock preserves file'
    } finally { Remove-Item -LiteralPath $lockedPath -Force }

    $exclusive = [IO.File]::Open($docFile, [IO.FileMode]::Open, [IO.FileAccess]::ReadWrite, [IO.FileShare]::None)
    try {
        $blocked = Invoke-ChangeCore (New-Request $after 'commit')
        Assert-Equal $blocked.result.saved $false 'OS-level exclusive file handle blocks commit'
        Assert-Equal $blocked.exit_code 1 'OS-level exclusive file handle returns failure'
    } finally { $exclusive.Dispose() }
    Assert-Equal (Get-Sha $docFile) $after 'OS-level exclusive handle preserves bytes'

    # External editor changes file without participating in the Studio lock protocol.
    Write-Utf8NoBom $docFile ([IO.File]::ReadAllText($docFile) + ' ')
    $external = Get-Sha $docFile
    $conflict = Invoke-ChangeCore (New-Request $after 'commit')
    Assert-Equal $conflict.result.status 'CONFLICT' 'non-cooperating editor change rejected by SHA'
    Assert-Equal (Get-Sha $docFile) $external 'external change is preserved'
    Assert-Equal ((@(Get-ChildItem -LiteralPath $testDir -Force | Where-Object { $_.Name -like '*.tmp' -or $_.Name -like '*.studio-changeset.lock' })).Count) 0 'no temporary/lock files left'
    Write-Host "SUCCESS: Windows CLI filesystem smoke $passCount assertions passed."
} finally {
    if ($KeepFixture) { Write-Host "Fixture retained: $testDir" }
    else { Remove-Item -LiteralPath $testDir -Force -Recurse -ErrorAction SilentlyContinue }
}
