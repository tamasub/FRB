# make_wwwroot_zip_v3.ps1
# FRBStudio_App packaging script
# data / defs / tests / tools / wwwroot + selected root files を ZIP 化する

$ErrorActionPreference = "Stop"

# この ps1 を置いたフォルダを基準にする
$root = Split-Path -Parent $MyInvocation.MyCommand.Path

# ZIP に含めるフォルダ
$targetDirs = @(
    "data",
    "defs",
    "Program.cs",
    "tests",
    "tools",
    "wwwroot"
)

# ZIP に含めるルート直下ファイル
$targetRootFiles = @(
    ".gitignore",
    "appsettings.Development.json",
    "appsettings.json",
    "FRBStudio.staticwebassets.endpoints.json",
    "package.json",
    "package-lock.json",
    "playwright.config.ts",
    "web.config"
)

# 出力 ZIP 名
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$zipName = "wwwroot$timestamp.zip"
$zipPath = Join-Path $root $zipName

# 一時ステージングフォルダ
$stage = Join-Path $env:TEMP ("frbstudio_zip_stage_" + [guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Path $stage | Out-Null

try {
    Write-Host ""
    Write-Host "FRBStudio package zip create start"
    Write-Host "Root : $root"
    Write-Host "Zip  : $zipPath"
    Write-Host ""

    $copiedCount = 0

    foreach ($dirName in $targetDirs) {
        $src = Join-Path $root $dirName
        $dst = Join-Path $stage $dirName

        if (Test-Path -LiteralPath $src) {
            Copy-Item -LiteralPath $src -Destination $dst -Recurse -Force
            Write-Host "[DIR ] $dirName"
            $copiedCount++
        }
        else {
            Write-Warning "[SKIP DIR ] not found: $dirName"
        }
    }

    foreach ($fileName in $targetRootFiles) {
        $src = Join-Path $root $fileName
        $dst = Join-Path $stage $fileName

        if (Test-Path -LiteralPath $src) {
            Copy-Item -LiteralPath $src -Destination $dst -Force
            Write-Host "[FILE] $fileName"
            $copiedCount++
        }
        else {
            Write-Warning "[SKIP FILE] not found: $fileName"
        }
    }

    if ($copiedCount -eq 0) {
        throw "ZIP対象が1つも見つかりません。ps1を FRBStudio_App 直下に置いてください。"
    }

    if (Test-Path -LiteralPath $zipPath) {
        Remove-Item -LiteralPath $zipPath -Force
    }

    # stage 配下のトップレベル項目を ZIP 化する。
    # -Force を付けることで .gitignore などの隠しファイルも拾う。
    $items = Get-ChildItem -LiteralPath $stage -Force
    Compress-Archive -LiteralPath $items.FullName -DestinationPath $zipPath -Force

    Write-Host ""
    Write-Host "ZIP作成完了！！"
    Write-Host $zipPath
}
finally {
    if (Test-Path -LiteralPath $stage) {
        Remove-Item -LiteralPath $stage -Recurse -Force
    }
}
