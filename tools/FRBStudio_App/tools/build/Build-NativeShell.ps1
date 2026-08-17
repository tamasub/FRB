<#
.SYNOPSIS
  Build and publish FRB Studio NativeShell without PC-specific paths.

.DESCRIPTION
  Resolves FRBStudio_App from this script location (tools/build/../..),
  then publishes NativeShell to NativeShell/_publish.
#>

[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Test-FRBStudioAppRoot {
    param([string]$Path)

    if ([string]::IsNullOrWhiteSpace($Path)) { return $false }
    if (-not (Test-Path -LiteralPath $Path -PathType Container)) { return $false }

    return (
        (Test-Path -LiteralPath (Join-Path $Path 'wwwroot/index.html') -PathType Leaf) -and
        (Test-Path -LiteralPath (Join-Path $Path 'data/json') -PathType Container) -and
        (Test-Path -LiteralPath (Join-Path $Path 'defs') -PathType Container) -and
        (Test-Path -LiteralPath (Join-Path $Path 'NativeShell/FRBStudio.NativeShell.csproj') -PathType Leaf)
    )
}

$studioAppRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
if (-not (Test-FRBStudioAppRoot -Path $studioAppRoot)) {
    throw "FRBStudio_App root could not be resolved from tools/build. Root=$studioAppRoot"
}

$studioLogScript = Join-Path $studioAppRoot 'tools/common/StudioLog.ps1'
if (-not (Test-Path -LiteralPath $studioLogScript -PathType Leaf)) {
    throw "StudioLog.ps1 is required for batch processing: $studioLogScript"
}
. $studioLogScript

$projectPath = Join-Path $studioAppRoot 'NativeShell/FRBStudio.NativeShell.csproj'
$publishDir = Join-Path $studioAppRoot 'NativeShell/_publish'

Initialize-StudioLog -StudioAppRoot $studioAppRoot -BatchName 'Build-NativeShell.ps1' -Context @{
    project_path = 'NativeShell/FRBStudio.NativeShell.csproj'
    publish_dir = 'NativeShell/_publish'
    resolved_studio_app_root = $studioAppRoot
}

trap {
    try {
        Write-StudioLog -Level 'ERROR' -Message 'Unhandled error' -Data (Get-StudioLogExceptionData -ErrorRecord $_)
        Complete-StudioLog -Status 'FAILED'
    } catch {}
    break
}

$dotnet = Get-Command dotnet -ErrorAction SilentlyContinue
if ($null -eq $dotnet) {
    throw 'dotnet command was not found in PATH. Install/enable a .NET SDK that can build net48.'
}

if (Test-Path -LiteralPath $publishDir) {
    Remove-Item -LiteralPath $publishDir -Recurse -Force
}
New-Item -ItemType Directory -Path $publishDir -Force | Out-Null

Write-Host ''
Write-Host 'FRB Studio NativeShell publish start'
Write-Host "Root    : $studioAppRoot"
Write-Host "Project : $projectPath"
Write-Host "Output  : $publishDir"
Write-Host ''

Write-StudioLog -Level 'INFO' -Message 'dotnet publish start' -Data @{
    command = 'dotnet publish NativeShell/FRBStudio.NativeShell.csproj -c Release -o NativeShell/_publish'
}

& $dotnet.Source publish $projectPath -c Release -o $publishDir
$exitCode = $LASTEXITCODE
if ($exitCode -ne 0) {
    throw "dotnet publish failed. exit_code=$exitCode"
}

Write-StudioLog -Level 'INFO' -Message 'dotnet publish completed' -Data @{
    exit_code = $exitCode
    publish_dir = 'NativeShell/_publish'
}
Complete-StudioLog -Status 'SUCCESS' -Data @{
    publish_dir = 'NativeShell/_publish'
}

Write-Host ''
Write-Host 'NativeShell publish completed.'
Write-Host $publishDir
