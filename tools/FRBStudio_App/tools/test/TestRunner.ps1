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

.EXAMPLE
  powershell -ExecutionPolicy Bypass -File .\TestRunner.ps1 -TestRunnerId responsibility_expected_tests -RunMode wait

.EXAMPLE
  powershell -ExecutionPolicy Bypass -File .\TestRunner.ps1 -TestRunnerId responsibility_refactor_first_step_smoke -RunMode wait

.EXAMPLE
  powershell -ExecutionPolicy Bypass -File .\TestRunner.ps1 -TestRunnerId definition_test_runner -RunMode wait

.EXAMPLE
  powershell -ExecutionPolicy Bypass -File .\TestRunner.ps1 -TestRunnerId definition_test_runner_cross_field_operator_matrix -RunMode wait
#>
param(
    [Parameter(Mandatory = $true)]
    [ValidateSet('playwright_ui', 'incident_prompt_copy_action_static', 'responsibility_expected_tests', 'responsibility_refactor_first_step_smoke', 'definition_test_runner', 'definition_test_runner_cross_field_operator_matrix')]
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

        # CommandProfile must pass the FRBStudio_App root itself.
        # Do not assume a parent repository path such as tools/FRBStudio_App exists.
        $candidates.Add($inputCandidate)
    }

    # TestRunner.ps1 is stored under tools/test, so ../.. is the FRBStudio_App root.
    if (-not [string]::IsNullOrWhiteSpace($PSScriptRoot)) {
        $candidates.Add((Join-Path $PSScriptRoot '../..'))
    }

    # Last fallback for manual execution from the FRBStudio_App directory.
    $current = (Get-Location).Path
    $candidates.Add($current)

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

    throw "FRBStudio_App root could not be resolved. Run from FRBStudio_App or pass that path as -RepositoryRoot."
}

$root = Resolve-StudioAppRoot -InputRoot $RepositoryRoot
Set-Location -LiteralPath $root

$studioLogScript = Join-Path $root 'tools/common/StudioLog.ps1'
if (-not (Test-Path -LiteralPath $studioLogScript -PathType Leaf)) {
    throw "StudioLog.ps1 is required for batch processing: $studioLogScript"
}
. $studioLogScript
Initialize-StudioLog -StudioAppRoot $root -BatchName 'TestRunner.ps1' -Context @{
    test_runner_id = $TestRunnerId
    requested_run_mode = $RunMode
    repository_root_argument = $RepositoryRoot
    resolved_root = $root
}

trap {
    try {
        Write-StudioLog -Level 'ERROR' -Message 'Unhandled error' -Data (Get-StudioLogExceptionData -ErrorRecord $_)
        Complete-StudioLog -Status 'FAILED' -Data @{ test_runner_id = $TestRunnerId; run_mode = $RunMode }
    } catch {}
    break
}

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

    'responsibility_expected_tests' {
        [pscustomobject]@{
            Id = 'responsibility_expected_tests'
            ExpectedRunMode = 'wait'
            Command = 'node'
            Arguments = @('tests/responsibilities/responsibility_expected_tests.mjs')
            Preview = 'node tests/responsibilities/responsibility_expected_tests.mjs'
        }
    }
    'responsibility_refactor_first_step_smoke' {
        [pscustomobject]@{
            Id = 'responsibility_refactor_first_step_smoke'
            ExpectedRunMode = 'wait'
            Command = 'node'
            Arguments = @('tests/responsibilities/responsibility_refactor_first_step_smoke.mjs')
            Preview = 'node tests/responsibilities/responsibility_refactor_first_step_smoke.mjs'
        }
    }
    'definition_test_runner' {
        [pscustomobject]@{
            Id = 'definition_test_runner'
            ExpectedRunMode = 'wait'
            Command = 'node'
            Arguments = @(
                'tests/definition/definition_test_runner_cli.mjs',
                '--field-defs', 'fielddefs/samples/frb_fft_measurement_field_definitions_v0_2.json',
                '--registry', 'data/json/config/validation_type_registry_v0_1.json',
                '--out', 'tests/.runtime/definition/definition_test_runner.result.json',
                '--evidence-dir', 'data/json/03_tests/contracts/definition_test_runner_frb_fft_v0_1'
            )
            Preview = 'node tests/definition/definition_test_runner_cli.mjs --field-defs fielddefs/samples/frb_fft_measurement_field_definitions_v0_2.json --registry data/json/config/validation_type_registry_v0_1.json --out tests/.runtime/definition/definition_test_runner.result.json --evidence-dir data/json/03_tests/contracts/definition_test_runner_frb_fft_v0_1'
        }
    }

    'definition_test_runner_cross_field_operator_matrix' {
        [pscustomobject]@{
            Id = 'definition_test_runner_cross_field_operator_matrix'
            ExpectedRunMode = 'wait'
            Command = 'node'
            Arguments = @(
                'tests/definition/definition_test_runner_cli.mjs',
                '--field-defs', 'fielddefs/samples/cross_field_compare_operator_matrix_v0_1.json',
                '--registry', 'data/json/config/validation_type_registry_v0_1.json',
                '--out', 'tests/.runtime/definition/definition_test_runner_cross_field_operator_matrix.result.json',
                '--evidence-dir', 'data/json/03_tests/contracts/definition_test_runner_cross_field_operator_matrix_v0_1'
            )
            Preview = 'node tests/definition/definition_test_runner_cli.mjs --field-defs fielddefs/samples/cross_field_compare_operator_matrix_v0_1.json --registry data/json/config/validation_type_registry_v0_1.json --out tests/.runtime/definition/definition_test_runner_cross_field_operator_matrix.result.json --evidence-dir data/json/03_tests/contracts/definition_test_runner_cross_field_operator_matrix_v0_1'
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

Write-StudioLog -Level 'INFO' -Message 'Runner resolved' -Data @{
    test_runner_id = $runner.Id
    run_mode = $RunMode
    repository = $root
    command_preview = $runner.Preview
}

Write-StudioLog -Level 'INFO' -Message 'Command start' -Data @{ command = $runner.Command; arguments = $runner.Arguments }
& $runner.Command @($runner.Arguments)
$exitCode = if ($LASTEXITCODE -is [int]) { $LASTEXITCODE } else { 0 }
$logLevel = if ($exitCode -eq 0) { 'INFO' } else { 'WARN' }
Write-StudioLog -Level $logLevel -Message 'Command end' -Data @{ exit_code = $exitCode; command_preview = $runner.Preview }
Complete-StudioLog -Status $(if ($exitCode -eq 0) { 'SUCCESS' } else { 'FAILED' }) -Data @{ exit_code = $exitCode; test_runner_id = $runner.Id; run_mode = $RunMode }
exit $exitCode
