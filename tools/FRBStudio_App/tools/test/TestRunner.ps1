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

function Resolve-RepositoryRoot {
    param([string]$InputRoot)

    if (-not [string]::IsNullOrWhiteSpace($InputRoot)) {
        $candidate = [System.IO.Path]::GetFullPath($InputRoot)
        if (Test-Path -LiteralPath $candidate -PathType Container) {
            return $candidate
        }
        throw "RepositoryRoot does not exist: $candidate"
    }

    $dir = Get-Location
    while ($null -ne $dir) {
        $gitDir = Join-Path $dir.Path '.git'
        if (Test-Path -LiteralPath $gitDir -PathType Container) {
            return $dir.Path
        }
        $dir = $dir.Parent
    }

    return (Get-Location).Path
}

$root = Resolve-RepositoryRoot -InputRoot $RepositoryRoot
Set-Location -LiteralPath $root

$runner = switch ($TestRunnerId) {
    'playwright_ui' {
        [pscustomobject]@{
            Id = 'playwright_ui'
            ExpectedRunMode = 'launch'
            Command = 'npx'
            Arguments = @('playwright', 'test', '--ui')
            Preview = 'npx playwright test --ui'
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
