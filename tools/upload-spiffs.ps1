param(
  [string]$Port = "COM3",
  [string]$Fqbn = "esp32:esp32:esp32",
  [string]$SketchDir = "",
  [string]$DataDir = ""
)

$ErrorActionPreference = "Stop"

if (-not $SketchDir) {
  $SketchDir = Join-Path $PSScriptRoot "..\firmware\FRB"
}
if (-not $DataDir) {
  $DataDir = Join-Path $PSScriptRoot "..\data"
}

$SketchDir = [System.IO.Path]::GetFullPath($SketchDir)
$DataDir   = [System.IO.Path]::GetFullPath($DataDir)

if (-not (Test-Path $SketchDir)) {
  throw "SketchDir not found: $SketchDir"
}
if (-not (Test-Path $DataDir)) {
  throw "DataDir not found: $DataDir"
}



Write-Host "=== FRB SPIFFS Upload ==="
Write-Host "SketchDir: $SketchDir"
Write-Host "DataDir  : $DataDir"
Write-Host "Port     : $Port"
Write-Host "FQBN     : $Fqbn"

$propText = & arduino-cli compile --fqbn $Fqbn --show-properties $SketchDir 2>&1
if ($LASTEXITCODE -ne 0) {
  $propText | ForEach-Object { Write-Host $_ }
  throw "arduino-cli compile --show-properties failed"
}

$props = @{}
foreach ($line in $propText) {
  if ($line -match '^([^=]+)=(.*)$') {
    $props[$matches[1].Trim()] = $matches[2].Trim()
  }
}

function Get-Prop([string]$name) {
  if ($props.ContainsKey($name)) { return $props[$name] }
  return $null
}

function Resolve-ExistingPath([string[]]$candidates) {
  foreach ($p in $candidates) {
    if ($p -and (Test-Path $p)) { return (Resolve-Path $p).Path }
  }
  return $null
}

function Parse-SizeToInt64([string]$s) {
  if (-not $s) { return $null }
  $v = $s.Trim()

  if ($v -match '^0x[0-9A-Fa-f]+$') {
    return [Convert]::ToInt64($v, 16)
  }
  if ($v -match '^[0-9]+$') {
    return [Int64]$v
  }
  if ($v -match '^([0-9]+)\s*[Kk]$') {
    return [Int64]$matches[1] * 1024
  }
  if ($v -match '^([0-9]+)\s*[Mm]$') {
    return [Int64]$matches[1] * 1024 * 1024
  }
  throw "Unsupported size format: $s"
}

$mkspiffsPath = Get-Prop "runtime.tools.mkspiffs.path"
$esptoolPath  = Get-Prop "runtime.tools.esptool_py.path"

if (-not $mkspiffsPath) { throw "runtime.tools.mkspiffs.path not found" }
if (-not $esptoolPath)  { throw "runtime.tools.esptool_py.path not found" }

$mkspiffsExe = Get-ChildItem -Path $mkspiffsPath -Recurse -File |
  Where-Object { $_.Name -ieq "mkspiffs.exe" } |
  Select-Object -First 1

Write-Host "=== DataDir resolved ==="
Write-Host $DataDir

Write-Host "=== files to package ==="
Get-ChildItem -File -Recurse $DataDir |
  Select-Object FullName, Length, LastWriteTime |
  Format-Table -AutoSize



if (-not $mkspiffsExe) {
  throw "mkspiffs.exe not found under: $mkspiffsPath"
}

$esptoolExe = Get-ChildItem -Path $esptoolPath -Recurse -File |
  Where-Object { $_.Name -ieq "esptool.exe" -or $_.Name -ieq "esptool.py" } |
  Select-Object -First 1

if (-not $esptoolExe) {
  throw "esptool executable not found under: $esptoolPath"
}

$runtimePlatformPath = Get-Prop "runtime.platform.path"
$buildVariantPath    = Get-Prop "build.variant.path"
$buildPartitions     = Get-Prop "build.partitions"

$spiffsStart = Get-Prop "build.spiffs_start"
$spiffsEnd   = Get-Prop "build.spiffs_end"
$spiffsPage  = Get-Prop "build.spiffs_pagesize"
$spiffsBlock = Get-Prop "build.spiffs_blocksize"

if (-not $spiffsPage)  { $spiffsPage = "256" }
if (-not $spiffsBlock) { $spiffsBlock = "4096" }

$size = $null
if ($spiffsStart) {
  if ($spiffsEnd) {
    $size = ([Convert]::ToInt64($spiffsEnd, 16) - [Convert]::ToInt64($spiffsStart, 16))
  } else {
    $spiffsSize = Get-Prop "build.spiffs_size"
    if ($spiffsSize) {
      $size = [Convert]::ToInt64($spiffsSize, 16)
    }
  }
}

if (-not $spiffsStart -or -not $size) {
  if (-not $buildPartitions) {
    throw "build.partitions not found"
  }

  $partitionCandidates = @(
    (Join-Path $runtimePlatformPath "tools\partitions\$buildPartitions.csv"),
    (Join-Path $runtimePlatformPath "partitions\$buildPartitions.csv"),
    (Join-Path $buildVariantPath "$buildPartitions.csv"),
    (Join-Path $SketchDir "$buildPartitions.csv")
  )

  $partitionCsv = Resolve-ExistingPath $partitionCandidates
  if (-not $partitionCsv) {
    throw "Partition CSV not found. build.partitions=$buildPartitions"
  }

  Write-Host "Partition CSV: $partitionCsv"

  $csvLines = Get-Content $partitionCsv | Where-Object {
    $_.Trim() -ne "" -and -not $_.Trim().StartsWith("#")
  }

  $spiffsRow = $null
  foreach ($line in $csvLines) {
    $cols = $line.Split(",") | ForEach-Object { $_.Trim() }
    if ($cols.Count -lt 5) { continue }

    $name    = $cols[0]
    $type    = $cols[1]
    $subtype = $cols[2]
    $offset  = $cols[3]
    $psize   = $cols[4]

    if (
      ($subtype -ieq "spiffs") -or
      ($name -match "spiffs") -or
      ($subtype -ieq "littlefs") -or
      ($name -match "littlefs")
    ) {
      $spiffsRow = @{
        name    = $name
        type    = $type
        subtype = $subtype
        offset  = $offset
        size    = $psize
      }
      break
    }
  }

  if (-not $spiffsRow) {
    throw "SPIFFS/LittleFS partition not found in CSV: $partitionCsv"
  }

  $spiffsStart = $spiffsRow.offset
  $size        = Parse-SizeToInt64 $spiffsRow.size
}

$flashMode   = Get-Prop "build.flash_mode"
$flashFreq   = Get-Prop "build.flash_freq"
$flashSize   = Get-Prop "build.flash_size"
$uploadSpeed = Get-Prop "upload.speed"

if (-not $flashMode)   { $flashMode = "dio" }
if (-not $flashFreq)   { $flashFreq = "80m" }
if (-not $flashSize)   { $flashSize = "4MB" }
if (-not $uploadSpeed) { $uploadSpeed = "921600" }

$buildDir = Join-Path $PSScriptRoot "..\.vscode\build"
New-Item -ItemType Directory -Force -Path $buildDir | Out-Null
$imagePath = Join-Path $buildDir "spiffs.bin"

Write-Host ""
Write-Host "--- Flash SPIFFS image ---"
Write-Host ("esptool  : " + $esptoolExe.FullName)
Write-Host ("port     : " + $Port)
Write-Host ("mode     : " + $flashMode)
Write-Host ("freq     : " + $flashFreq)
Write-Host ("size     : " + $flashSize)

$mkspiffs = Join-Path $env:LOCALAPPDATA "Arduino15\packages\esp32\tools\mkspiffs\0.2.3\mkspiffs.exe"

Write-Host "mkspiffs : $mkspiffs"
if (!(Test-Path $mkspiffs)) {
  Write-Error "mkspiffs.exe not found: $mkspiffs"
  exit 1
}

& $mkspiffs `
  -c $DataDir `
  -b 4096 `
  -p 256 `
  -s 0x160000 `
  $imagePath

if (!(Test-Path $imagePath)) {
  Write-Error "SPIFFS image was not created: $imagePath"
  exit 1
}


if (!(Test-Path $imagePath)) {
  Write-Error "SPIFFS image was not created: $imagePath"
  exit 1
}

if ($esptoolExe.Name -ieq "esptool.py") {
  & python $esptoolExe.FullName --chip esp32 --port $Port --baud $uploadSpeed `
    write_flash -z --flash_mode $flashMode --flash_freq $flashFreq --flash_size $flashSize `
    $spiffsStart $imagePath
}
else {
  & $esptoolExe.FullName --chip esp32 --port $Port --baud $uploadSpeed `
    write_flash -z --flash_mode $flashMode --flash_freq $flashFreq --flash_size $flashSize `
    $spiffsStart $imagePath
}

if ($LASTEXITCODE -ne 0) {
  Write-Host "SPIFFS upload skipped or failed."
  exit 0
}

Write-Host ""
Write-Host "SPIFFS upload completed successfully."
exit 0
