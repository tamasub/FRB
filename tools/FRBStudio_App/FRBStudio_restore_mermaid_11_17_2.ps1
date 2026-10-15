# FRB Studio: restore the omitted Mermaid v11 library only.
# Put this file at FRBStudio_App root, beside wwwroot and NativeShell.
# Downloads the official npm package archive. Does not modify existing project source files.
[CmdletBinding()]
param()
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$viewer = Join-Path $root 'wwwroot\mdViewer.html'
$lib = Join-Path $root 'wwwroot\js\lib'
$target = Join-Path $lib 'mermaid'
$entry = Join-Path $target 'mermaid.esm.min.mjs'
$version = '11.17.2'
$url = "https://registry.npmjs.org/mermaid/-/mermaid-$version.tgz"

if (!(Test-Path -LiteralPath $viewer -PathType Leaf)) {
    throw "FRBStudio_App root not detected. Place this script beside the wwwroot folder: $root"
}
if (Test-Path -LiteralPath $target) {
    throw "The target folder already exists. To avoid overwriting it, first check it manually: $target"
}
if (!(Get-Command tar.exe -ErrorAction SilentlyContinue)) {
    throw 'tar.exe is required. Use Windows 10/11 or extract the npm .tgz archive manually.'
}
$tempDir = Join-Path $env:TEMP ('frbstudio_mermaid_restore_' + [guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $tempDir -Force | Out-Null
try {
    $archive = Join-Path $tempDir "mermaid-$version.tgz"
    Write-Host "Downloading Mermaid $version from the official npm registry..."
    Invoke-WebRequest -Uri $url -OutFile $archive -UseBasicParsing
    & tar.exe -xzf $archive -C $tempDir
    if ($LASTEXITCODE -ne 0) { throw 'Archive extraction failed.' }
    $dist = Join-Path $tempDir 'package\dist'
    if (!(Test-Path -LiteralPath (Join-Path $dist 'mermaid.esm.min.mjs') -PathType Leaf)) {
        throw 'The downloaded package does not contain the expected Mermaid entry file.'
    }
    if (!(Test-Path -LiteralPath (Join-Path $dist 'chunks') -PathType Container)) {
        throw 'The downloaded package does not contain the expected chunks folder.'
    }
    New-Item -ItemType Directory -Path $target -Force | Out-Null
    Copy-Item -Path (Join-Path $dist '*') -Destination $target -Recurse -Force
    $license = Join-Path $tempDir 'package\LICENSE'
    if (Test-Path -LiteralPath $license) {
        Copy-Item -LiteralPath $license -Destination (Join-Path $target 'LICENSE') -Force
    }
    if (!(Test-Path -LiteralPath $entry -PathType Leaf)) { throw 'Installation verification failed.' }
    Write-Host "OK: $entry"
    Write-Host "Chunks: $(Join-Path $target 'chunks')"
    Write-Host 'Next: start FRB Studio Markdown Viewer and verify a mermaid flowchart.'
}
finally {
    if (Test-Path -LiteralPath $tempDir) { Remove-Item -LiteralPath $tempDir -Recurse -Force }
}
