# make_wwwroot_zip_v4.ps1
# FRBStudio_App packaging script
# data / defs / tests / tools / wwwroot + selected root files を ZIP 化する

$ErrorActionPreference = "Stop"

# tools/zip 配下のこのPS1自身から FRBStudio_App root を解決する。
# PC固有の絶対パスは持たない。
$root = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot "../.."))

if (
    -not (Test-Path -LiteralPath (Join-Path $root "wwwroot\index.html") -PathType Leaf) -or
    -not (Test-Path -LiteralPath (Join-Path $root "data\json") -PathType Container) -or
    -not (Test-Path -LiteralPath (Join-Path $root "defs") -PathType Container) -or
    -not (Test-Path -LiteralPath (Join-Path $root "tools") -PathType Container)
) {
    throw "FRBStudio_App root could not be resolved from tools/zip. Root=$root"
}

# ZIP に含めるフォルダ
$targetDirs = @(
    "data",
    "defs",
    "fielddefs",
    "NativeShell",
    "tests",
    "tools",
    "wwwroot",
    "studio_overlays",
    "SeleniumTaste"
)

# ZIP に含めるルート直下ファイル
$targetRootFiles = @(
    ".gitignore",
    "cmd_make_FRBStudio_App_zip_v2.bat",
    "cmd_compile_NativeShell.bat",
    "playwright.config.ts",
    "cmd_file_size_list.py",
    "count_js_steps.py"
)

# ZIP に含めないパス
# ルートからの相対パス、または $root 配下の絶対パスを指定できる。
# 例: "wwwroot\js\lib\mermaid"
$excludePaths = @(
    "wwwroot\js\lib\mermaid",
    "studio_overlays\default",
    "studio_overlays\gpt_fx_lab",
    "tools\chatgpt-share-export-minimum\node_modules",
    "wwwroot\data\json",
    "NativeShell\bin",
    "NativeShell\obj",
    "NativeShell\_publish",
    "data\json\81_frb_OrgSample",
    "SeleniumTaste\bin",
    "SeleniumTaste\driver",
    "SeleniumTaste\obj"
)

# 出力 ZIP 名
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$zipName = "FRBStudio_App$timestamp.zip"
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
