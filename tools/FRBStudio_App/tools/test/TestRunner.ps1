<#
.SYNOPSIS
  FRB Studio / JSON Object Studio Test Runner.

.DESCRIPTION
  StudioくんのCommandProfileから呼び出す、許可済みテストだけを実行する薄いランナー。
  任意commandLineや任意test_fileは受け付けない。

.EXAMPLE
  powershell -ExecutionPolicy Bypass -File .\TestRunner.ps1 -TestRunnerId playwright_ui -RunMode launch

.EXAMPLE
  powershell -ExecutionPolicy Bypass -File .\TestRunner.ps1 -TestRunnerId incident_prompt_copy_action_static -RunMode wait
#>
param(
    [Parameter(Mandatory = $true)]
    [ValidateSet('playwright_ui', 'incident_prompt_copy_action_static')]
    [string]$TestRunnerId,

    [Parameter(Mandatory = $false)]
    [ValidateSet('launch', 'wait')]
    [string]$RunMode = '',

    [Parameter(Mandatory = $false)]
    [string]$RepositoryRoot = ''
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Test-StudioAppRoot {
    param([string]$Path)

    if ([string]::IsNullOrWhiteSpace($Path)) { return $false }
    if (-not (Test-Path -LiteralPath $Path -PathType Container)) { return $false }

    $packageJson = Join-Path $Path 'package.json'
    $playwrightConfig = Join-Path $Path 'playwright.config.ts'
    $screenStateTests = Join-Path $Path 'tests/screen_state'

    return (
        (Test-Path -LiteralPath $packageJson -PathType Leaf) -and
        (Test-Path -LiteralPath $playwrightConfig -PathType Leaf) -and
        (Test-Path -LiteralPath $screenStateTests -PathType Container)
    )
}

function Resolve-StudioAppRoot {
    param([string]$InputRoot)

    $candidates = New-Object System.Collections.Generic.List[string]

    if (-not [string]::IsNullOrWhiteSpace($InputRoot)) {
        $inputCandidate = [System.IO.Path]::GetFullPath($InputRoot)
        if (-not (Test-Path -LiteralPath $inputCandidate -PathType Container)) {
            throw "RepositoryRoot does not exist: $inputCandidate"
        }

        # Backward compatibility:
        # Program.cs / CommandProfile may pass the Git repository root (e.g. F:\FRB).
        # Playwright assets live under tools/FRBStudio_App, so normalize it here.
        $candidates.Add($inputCandidate)
        $candidates.Add((Join-Path $inputCandidate 'tools/FRBStudio_App'))
    }

    # TestRunner.ps1 is stored under tools/test, so ../.. is the FRBStudio_App root.
    if (-not [string]::IsNullOrWhiteSpace($PSScriptRoot)) {
        $candidates.Add((Join-Path $PSScriptRoot '../..'))
    }

    # Last fallback for manual execution from the FRBStudio_App directory.
    $current = (Get-Location).Path
    $candidates.Add($current)
    $candidates.Add((Join-Path $current 'tools/FRBStudio_App'))

    $seen = @{}
    foreach ($candidate in $candidates) {
        if ([string]::IsNullOrWhiteSpace($candidate)) { continue }
        $fullPath = [System.IO.Path]::GetFullPath($candidate)
        if ($seen.ContainsKey($fullPath)) { continue }
        $seen[$fullPath] = $true

        if (Test-StudioAppRoot -Path $fullPath) {
            return $fullPath
        }
    }

    throw "FRBStudio_App root could not be resolved. Run from tools/FRBStudio_App or pass that path as -RepositoryRoot."
}

$root = Resolve-StudioAppRoot -InputRoot $RepositoryRoot
Set-Location -LiteralPath $root

$runner = switch ($TestRunnerId) {
    'playwright_ui' {
        [pscustomobject]@{
            Id = 'playwright_ui'
            ExpectedRunMode = 'launch'
            Command = 'npx'
            Arguments = @('playwright', 'test', '--config=playwright.config.ts', '--ui')
            Preview = 'npx playwright test --config=playwright.config.ts --ui'
        }
    }
    'incident_prompt_copy_action_static' {
        [pscustomobject]@{
            Id = 'incident_prompt_copy_action_static'
            ExpectedRunMode = 'wait'
            Command = 'node'
            Arguments = @('--test', 'tests/qa/static/incident_prompt_copy_action_viewdef_static.test.mjs')
            Preview = 'node --test tests/qa/static/incident_prompt_copy_action_viewdef_static.test.mjs'
        }
    }
    default {
        throw "Unsupported TestRunnerId: $TestRunnerId"
    }
}

if ([string]::IsNullOrWhiteSpace($RunMode)) {
    $RunMode = $runner.ExpectedRunMode
}

if ($RunMode -ne $runner.ExpectedRunMode) {
    throw "RunMode mismatch for $($runner.Id): expected $($runner.ExpectedRunMode), got $RunMode"
}

Write-Host "FRB Studio TestRunner"
Write-Host "  TestRunnerId : $($runner.Id)"
Write-Host "  RunMode      : $RunMode"
Write-Host "  Repository   : $root"
Write-Host "  Command      : $($runner.Preview)"

& $runner.Command @($runner.Arguments)
$exitCode = if ($LASTEXITCODE -is [int]) { $LASTEXITCODE } else { 0 }
exit $exitCode
