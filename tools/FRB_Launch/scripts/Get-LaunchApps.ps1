[CmdletBinding()]
param([Parameter(Mandatory=$true)][string]$OutputPath)
$ErrorActionPreference='Stop'
try {
    $apps=@(Get-StartApps -ErrorAction Stop)
    $shell=New-Object -ComObject WScript.Shell
    $shortcuts=@()
    $roots=@([Environment]::GetFolderPath('Programs'),[Environment]::GetFolderPath('CommonPrograms'))
    foreach ($root in $roots) {
        if (-not $root -or -not (Test-Path -LiteralPath $root)) { continue }
        foreach ($file in @(Get-ChildItem -LiteralPath $root -Filter '*.lnk' -Recurse -File -ErrorAction SilentlyContinue)) {
            try {
                $link=$shell.CreateShortcut($file.FullName)
                $target=[Environment]::ExpandEnvironmentVariables($link.TargetPath)
                if (-not $target -or -not (Test-Path -LiteralPath $target -PathType Leaf)) { continue }
                if ([IO.Path]::GetExtension($target) -notin @('.exe','.com','.bat','.cmd')) { continue }
                if ([IO.Path]::GetFileName($target) -match '^(unins\d*|uninstall|uninstaller)\.exe$') { continue }
                $shortcuts+=@([pscustomobject]@{name=$file.BaseName;path=$file.FullName})
            } catch { }
        }
    }
    $records=@()
    foreach ($app in $apps) {
        if (-not $app.Name -or -not $app.AppID) { continue }
        $match=$shortcuts | Where-Object {$_.name -eq $app.Name} | Select-Object -First 1
        $records+=@([pscustomobject]@{name=[string]$app.Name;target=[string]$app.AppID;kind='aumid';icon_path=$(if ($match) {$match.path} else {''})})
    }
    foreach ($link in $shortcuts) {
        if (@($apps | Where-Object {$_.Name -eq $link.name}).Count) { continue }
        $records+=@([pscustomobject]@{name=$link.name;target=$link.path;kind='shortcut';icon_path=$link.path})
    }
    $json=ConvertTo-Json -InputObject @{version=1;apps=@($records)} -Depth 5
    [IO.File]::WriteAllText($OutputPath,$json,[Text.UTF8Encoding]::new($false))
    exit 0
} catch {
    $logDir=Join-Path $env:LOCALAPPDATA 'FRBLaunch'
    New-Item -ItemType Directory -Force -Path $logDir | Out-Null
    Add-Content -LiteralPath (Join-Path $logDir 'apps.log') -Encoding UTF8 -Value ((Get-Date -Format 'yyyy/MM/dd HH:mm:ss')+' '+$_.Exception.ToString())
    exit 1
}
