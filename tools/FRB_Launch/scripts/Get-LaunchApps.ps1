[CmdletBinding()]
param([Parameter(Mandatory=$true)][string]$OutputPath)
$ErrorActionPreference = 'Stop'

# Use built-in commands only.  In company environments COM activation and
# arbitrary .NET method invocation may be prohibited by policy.
try {
    $partial = $false
    $gotStartApps = $false
    $gotShortcuts = $false
    $apps = @()

    try {
        $apps = @(Get-StartApps -ErrorAction Stop)
        $gotStartApps = $true
        Write-Output ('APPS Get-StartApps count=' + $apps.Count)
    } catch {
        $partial = $true
        Write-Output ('APPS Get-StartApps unavailable: ' + $_.Exception.Message)
    }

    $roots = @()
    if ($env:APPDATA) { $roots += (Join-Path $env:APPDATA 'Microsoft\Windows\Start Menu\Programs') }
    if ($env:PROGRAMDATA) { $roots += (Join-Path $env:PROGRAMDATA 'Microsoft\Windows\Start Menu\Programs') }
    $shortcuts = @(
        foreach ($root in ($roots | Select-Object -Unique)) {
            try {
                if (-not (Test-Path -LiteralPath $root -PathType Container)) {
                    Write-Warning ('APPS Start Menu unavailable: ' + $root)
                    $partial = $true
                    continue
                }
                # Some company folders are access-restricted; skip unreadable subfolders.
                $scanErrors = @()
                $files = @(Get-ChildItem -LiteralPath $root -Filter '*.lnk' -Recurse -File -ErrorAction SilentlyContinue -ErrorVariable +scanErrors)
                if ($scanErrors.Count -gt 0) {
                    $partial = $true
                    Write-Warning ('APPS Some shortcut folders were restricted under ' + $root + ': ' + $scanErrors.Count)
                }
                $gotShortcuts = $true
                foreach ($file in $files) {
                    [pscustomobject]@{ name=[string]$file.BaseName; path=[string]$file.FullName }
                }
                Write-Warning ('APPS Start Menu count=' + $files.Count)
            } catch {
                $partial = $true
                Write-Warning ('APPS Start Menu enumeration failed: ' + $_.Exception.Message)
            }
        }
    )
    if (-not $gotStartApps -and -not $gotShortcuts) {
        throw 'Neither Get-StartApps nor Start Menu shortcuts could be read'
    }

    # Hash tables avoid O(start-app-count * shortcut-count) lookup loops.
    $linkByName = @{}
    foreach ($link in $shortcuts) {
        if (-not $linkByName.ContainsKey($link.name)) { $linkByName[$link.name] = $link.path }
    }
    $existingNames = @{}
    $records = @(
        foreach ($app in $apps) {
            if (-not $app.Name -or -not $app.AppID) { continue }
            $name = [string]$app.Name
            $icon = ''
            if ($linkByName.ContainsKey($name)) { $icon = $linkByName[$name] }
            [pscustomobject]@{ name=$name; target=[string]$app.AppID; kind='aumid'; icon_path=$icon }
            $existingNames[$name] = $true
        }
        foreach ($link in $shortcuts) {
            if ($existingNames.ContainsKey($link.name)) { continue }
            [pscustomobject]@{ name=$link.name; target=$link.path; kind='shortcut'; icon_path=$link.path }
        }
    )
    if ($records.Count -eq 0) { throw 'No applications were discovered; refusing to replace the cached list' }

    $json = ConvertTo-Json -InputObject @{version=1; apps=@($records); partial=$partial} -Depth 5
    # Set-Content works in PowerShell ConstrainedLanguage (unlike static .NET IO APIs).
    Set-Content -LiteralPath $OutputPath -Value $json -Encoding UTF8 -ErrorAction Stop
    Write-Output ('APPS saved count=' + $records.Count + ' partial=' + $partial)
    exit 0
} catch {
    Write-Output ('APPS ERROR: ' + $_.Exception.ToString())
    exit 1
}
