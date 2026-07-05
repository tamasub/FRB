# make_wwwroot_zip_v4.ps1
# FRBStudio_App packaging script
# data / defs / tests / tools / wwwroot + selected root files を ZIP 化する

$ErrorActionPreference = "Stop"

# この ps1 を置いたフォルダを基準にする
#$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$root = "F:\FRB\tools\FRBStudio_App\"

# ZIP に含めるフォルダ
$targetDirs = @(
    "studio_overlays"

)

# ZIP に含めるルート直下ファイル
$targetRootFiles = @(
)

# ZIP に含めないパス
# ルートからの相対パス、または $root 配下の絶対パスを指定できる。
# 例: "wwwroot\js\lib\mermaid"
# 例: "F:\FRB\tools\FRBStudio_App\wwwroot\js\lib\mermaid"
$excludePaths = @(
    "wwwroot\js\lib\mermaid"
)

# 出力 ZIP 名
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$zipName = "studio_overlays$timestamp.zip"
$zipPath = Join-Path $root $zipName

# 一時ステージングフォルダ
$stage = Join-Path $env:TEMP ("frbstudio_zip_stage_" + [guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Path $stage | Out-Null

try {
    Write-Host ""
    Write-Host "studio_overlays package zip create start"
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

    # 除外対象をステージングフォルダから削除する。
    # Copy-Item 後に消す方式にして、既存のコピー処理を大きく変えない。
    foreach ($excludePath in $excludePaths) {
        if ([string]::IsNullOrWhiteSpace($excludePath)) {
            continue
        }

        $relativeExcludePath = $excludePath

        if ([System.IO.Path]::IsPathRooted($excludePath)) {
            $rootFull = [System.IO.Path]::GetFullPath($root).TrimEnd('\', '/')
            $excludeFull = [System.IO.Path]::GetFullPath($excludePath)

            if ($excludeFull.StartsWith($rootFull, [System.StringComparison]::OrdinalIgnoreCase)) {
                $relativeExcludePath = $excludeFull.Substring($rootFull.Length).TrimStart('\', '/')
            }
            else {
                Write-Warning "[SKIP EXCLUDE] outside root: $excludePath"
                continue
            }
        }

        $stageExcludePath = Join-Path $stage $relativeExcludePath

        if (Test-Path -LiteralPath $stageExcludePath) {
            Remove-Item -LiteralPath $stageExcludePath -Recurse -Force
            Write-Host "[EXCLUDE] $relativeExcludePath"
        }
        else {
            Write-Host "[EXCLUDE SKIP] not found in stage: $relativeExcludePath"
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
