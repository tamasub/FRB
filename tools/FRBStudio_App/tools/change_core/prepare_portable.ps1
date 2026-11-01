# studio_work_0269 / Step 3 (Windows packaging helper)
# Copy a user-provided Node runtime into a self-contained ChangeSet CLI folder.
# The Node binary and its license must be supplied from an authorized distribution.
param(
    [Parameter(Mandatory=$true)][string]$NodeExecutable,
    [Parameter(Mandatory=$true)][string]$NodeLicenseFile,
    [Parameter(Mandatory=$true)][string]$Destination
)
$ErrorActionPreference = 'Stop'
$root = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$node = (Resolve-Path $NodeExecutable).Path
$license = (Resolve-Path $NodeLicenseFile).Path
if (-not $node.EndsWith('.exe', [System.StringComparison]::OrdinalIgnoreCase)) {
    throw 'Windows portable runtime requires a node.exe file.'
}
if (Test-Path $Destination) { throw 'Destination must not exist; refusing to merge with an existing release folder.' }
New-Item -Path $Destination -ItemType Directory | Out-Null
$destinationRoot = (Resolve-Path $Destination).Path
function Copy-Relative([string]$relative) {
    $src = Join-Path $root $relative
    if (-not (Test-Path $src)) { throw "Missing required source: $relative" }
    $target = Join-Path $destinationRoot $relative
    $parent = Split-Path $target -Parent
    New-Item -Path $parent -ItemType Directory -Force | Out-Null
    Copy-Item -Path $src -Destination $target -Recurse -Force
}
Copy-Item $node (Join-Path $destinationRoot 'node.exe')
Copy-Item $license (Join-Path $destinationRoot 'NODE_LICENSE.txt')
foreach ($relative in @(
    'tools/change_core/cli.mjs',
    'tools/change_core/change_core.mjs',
    'tools/change_core/storage.mjs',
    'tools/change_core/field_validation.mjs',
    'tools/change_core/python_client.py',
    'tools/change_core/config.example.json',
    'tools/change_core/README.md',
    'wwwroot/js/runtime/tree_model.js',
    'wwwroot/js/services/definition/definition_verification_common.js',
    'wwwroot/js/services/definition/field_contract_resolver.js',
    'wwwroot/js/services/definition/definition_value_validator.js',
    'wwwroot/js/services/definition/runtime_field_definition_validation.js',
    'defs',
    'fielddefs',
    'data/json/config/validation_type_registry_v0_1.json'
)) { Copy-Relative $relative }
Write-Output "ChangeSet portable folder created: $destinationRoot"
Write-Output 'Configure trusted documents and absolute paths; run node.exe tools/change_core/cli.mjs --config <config_path>.'
