param(
  [string]$WatchDir = "",
  [string]$UploadScript = "",
  [string]$Port = "COM3",
  [string]$Fqbn = "esp32:esp32:esp32",
  [string]$SketchDir = "",
  [string]$DataDir = "",
  [int]$PollMs = 1000
)

$ErrorActionPreference = "Stop"

if (-not $WatchDir) {
  $WatchDir = Join-Path $PSScriptRoot "..\data"
}
if (-not $UploadScript) {
  $UploadScript = Join-Path $PSScriptRoot "upload-spiffs.ps1"
}
if (-not $SketchDir) {
  $SketchDir = Join-Path $PSScriptRoot "..\firmware\FRB"
}
if (-not $DataDir) {
  $DataDir = Join-Path $PSScriptRoot "..\data"
}

$WatchDir = [System.IO.Path]::GetFullPath($WatchDir)
$UploadScript = [System.IO.Path]::GetFullPath($UploadScript)
$SketchDir = [System.IO.Path]::GetFullPath($SketchDir)
$DataDir = [System.IO.Path]::GetFullPath($DataDir)

if (-not (Test-Path $WatchDir)) {
  throw "WatchDir not found: $WatchDir"
}
if (-not (Test-Path $UploadScript)) {
  throw "UploadScript not found: $UploadScript"
}

function Get-WatchedState([string]$dir) {
  $files = Get-ChildItem -Path $dir -Recurse -File |
    Where-Object { $_.Extension -match '^\.(js)$' } |
    Sort-Object FullName

  $state = @()
  foreach ($f in $files) {
    $state += "$($f.FullName)|$($f.LastWriteTimeUtc.Ticks)|$($f.Length)"
  }
  return ($state -join "`n")
}

Write-Host "Watching: $WatchDir"
Write-Host "Upload script: $UploadScript"
Write-Host "Poll interval: $PollMs ms"
Write-Host "Press Ctrl+C to stop."
Write-Host ""

$lastState = Get-WatchedState $WatchDir
$lastUploadAt = Get-Date "2000-01-01"

while ($true) {
  Start-Sleep -Milliseconds $PollMs

  try {
    $newState = Get-WatchedState $WatchDir
  }
  catch {
    Write-Host "State scan failed:"
    Write-Host $_
    continue
  }

  if ($newState -ne $lastState) {
    $now = Get-Date
    $elapsed = ($now - $lastUploadAt).TotalSeconds

    # 保存直後の連続変化を少し待つ
    Start-Sleep -Milliseconds 700
    try {
      $settledState = Get-WatchedState $WatchDir
    }
    catch {
      Write-Host "State rescan failed:"
      Write-Host $_
      continue
    }

    if ($settledState -ne $lastState) {
      Write-Host "Detected change in data/ -> uploading SPIFFS..."
      try {
        & powershell -ExecutionPolicy Bypass -File $UploadScript `
          -Port $Port `
          -Fqbn $Fqbn `
          -SketchDir $SketchDir `
          -DataDir $DataDir

        $lastUploadAt = Get-Date
        $lastState = $settledState
        Write-Host ""
        Write-Host "Watch loop ready."
        Write-Host ""
      }
      catch {
        Write-Host "Upload failed:"
        Write-Host $_
      }
    }
  }
}