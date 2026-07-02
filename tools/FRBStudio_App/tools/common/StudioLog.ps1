<#
.SYNOPSIS
  FRB Studio PowerShell common daily logger.

.DESCRIPTION
  TestRunner.ps1 / Export-DiffToJson.ps1 などのStudioバッチ処理で共通利用するログ出力部品。
  ログは FRBStudio_App/Log/Log_yyyyMMdd.log に日次追記する。
  ログ出力失敗は本処理を止めない。
#>

$script:StudioLogState = $null

function Initialize-StudioLog {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)]
        [string]$StudioAppRoot,

        [Parameter(Mandatory=$true)]
        [string]$BatchName,

        [hashtable]$Context = @{}
    )

    try {
        if ([string]::IsNullOrWhiteSpace($StudioAppRoot)) { return }
        if ([string]::IsNullOrWhiteSpace($BatchName)) { $BatchName = 'UnknownBatch' }

        $root = [System.IO.Path]::GetFullPath($StudioAppRoot)
        $logDir = Join-Path $root 'Log'
        New-Item -ItemType Directory -Force -Path $logDir | Out-Null

        $script:StudioLogState = [pscustomobject]@{
            StudioAppRoot = $root
            BatchName = $BatchName
            LogDir = $logDir
            StartedAt = Get-Date
        }

        Write-StudioLog -Level 'INFO' -Message 'START' -Data $Context
    }
    catch {
        # ログ初期化失敗で本処理を止めない。
        try { Write-Warning "StudioLog initialization failed: $($_.Exception.Message)" } catch {}
    }
}


function ConvertTo-StudioReadableJson {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true, ValueFromPipeline=$true)]
        [object]$InputObject,

        [int]$Depth = 12,

        [switch]$Compress
    )

    begin {
        $items = New-Object 'System.Collections.Generic.List[object]'
    }

    process {
        [void]$items.Add($InputObject)
    }

    end {
        $target = if ($items.Count -eq 1) { $items[0] } else { $items.ToArray() }
        $json = if ($Compress) {
            $target | ConvertTo-Json -Depth $Depth -Compress
        } else {
            $target | ConvertTo-Json -Depth $Depth
        }

        # v0.9-json-utf8-human-readable-save:
        # Windows PowerShell 5.1 can emit Japanese as \uXXXX.
        # Decode only real JSON unicode escapes, and keep literal "\\uXXXX" text untouched.
        return [System.Text.RegularExpressions.Regex]::Replace(
            $json,
            '(?<!\\)\\u([0-9a-fA-F]{4})',
            { param($m) [string][char]([Convert]::ToInt32($m.Groups[1].Value, 16)) }
        )
    }
}

function Write-StudioLog {
    [CmdletBinding()]
    param(
        [ValidateSet('TRACE','DEBUG','INFO','WARN','ERROR')]
        [string]$Level = 'INFO',

        [string]$Message = '',

        [object]$Data = $null
    )

    try {
        if ($null -eq $script:StudioLogState) { return }

        $date = Get-Date
        $logPath = Join-Path $script:StudioLogState.LogDir ("Log_{0}.log" -f $date.ToString('yyyyMMdd'))
        $safeMessage = if ($null -eq $Message) { '' } else { ($Message -replace "`r|`n", ' ') }

        $line = "{0}`t{1}`t{2}`t{3}" -f $date.ToString('yyyy-MM-dd HH:mm:ss.fff'), $Level, $script:StudioLogState.BatchName, $safeMessage

        if ($null -ne $Data) {
            try {
                $dataJson = $Data | ConvertTo-StudioReadableJson -Depth 12 -Compress
                $line = $line + "`t" + $dataJson
            }
            catch {
                $line = $line + "`t" + ($Data | Out-String).Trim()
            }
        }

        $encoding = [System.Text.UTF8Encoding]::new($false)
        [System.IO.File]::AppendAllText($logPath, $line + [Environment]::NewLine, $encoding)
    }
    catch {
        # ログ書き込み失敗で本処理を止めない。
    }
}

function Complete-StudioLog {
    [CmdletBinding()]
    param(
        [string]$Status = 'SUCCESS',
        [object]$Data = $null
    )

    try {
        $payload = [ordered]@{
            status = $Status
        }

        if ($null -ne $script:StudioLogState -and $null -ne $script:StudioLogState.StartedAt) {
            $payload.duration_ms = [int]((Get-Date) - $script:StudioLogState.StartedAt).TotalMilliseconds
        }

        if ($null -ne $Data) {
            $payload.data = $Data
        }

        $level = if ($Status -eq 'SUCCESS') { 'INFO' } else { 'ERROR' }
        Write-StudioLog -Level $level -Message 'END' -Data $payload
    }
    catch {
        # ログ完了処理失敗で本処理を止めない。
    }
}

function Get-StudioLogExceptionData {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)]
        [object]$ErrorRecord
    )

    try {
        $exception = $ErrorRecord.Exception
        return [ordered]@{
            message = if ($null -ne $exception) { $exception.Message } else { $ErrorRecord.ToString() }
            category = $ErrorRecord.CategoryInfo.ToString()
            script_stack_trace = $ErrorRecord.ScriptStackTrace
        }
    }
    catch {
        return [ordered]@{
            message = $ErrorRecord.ToString()
        }
    }
}
