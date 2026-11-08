# FRB Launch + Studio Portable variable initialization v0.3
# Windows PowerShell 5.1 compatible. Only the bundled COPY is edited.
# JSON is parsed/validated, then the exact launch_value string is surgically replaced.
# NO regular-expression matching and NO whole-file JSON reserialization.
[CmdletBinding()]
param([Parameter(Mandatory = $true)][string]$BundleRoot)
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

function Skip-White([string]$text, [int]$pos) {
    while ($pos -lt $text.Length -and [char]::IsWhiteSpace($text[$pos])) { $pos++ }
    return $pos
}
function Read-JsonString([string]$text, [int]$start) {
    if ($start -ge $text.Length -or $text[$start] -ne '"') {
        throw "Expected a JSON string at offset $start."
    }
    $pos = $start + 1
    while ($pos -lt $text.Length) {
        if ($text[$pos] -eq '\') {
            $pos += 2 # Skip escape sequence (escaped quote/backslash/Unicode escape prefix)
            continue
        }
        if ($text[$pos] -eq '"') {
            return @{ Start = $start; End = ($pos + 1) }
        }
        $pos++
    }
    throw "Unterminated JSON string at offset $start."
}
function Find-ObjectEnd([string]$text, [int]$start) {
    if ($text[$start] -ne '{') { throw 'Expected a JSON object.' }
    $depth = 0
    $pos = $start
    while ($pos -lt $text.Length) {
        if ($text[$pos] -eq '"') {
            $span = Read-JsonString $text $pos
            $pos = $span.End
            continue
        }
        if ($text[$pos] -eq '{') { $depth++ }
        if ($text[$pos] -eq '}') {
            $depth--
            if ($depth -eq 0) { return $pos }
        }
        $pos++
    }
    throw 'Unterminated JSON object in launch_variables.'
}

try {
    $root = [System.IO.Path]::GetFullPath($BundleRoot.Trim().Trim('"'))
    $cfg = Join-Path $root 'config\frb_launch_sample_data_v0_1.json'
    if (-not (Test-Path -LiteralPath $cfg -PathType Leaf)) { throw "Launch config missing: $cfg" }

    $raw = [System.IO.File]::ReadAllText($cfg, [System.Text.Encoding]::UTF8)
    $document = ConvertFrom-Json -InputObject $raw
    $variables = @($document.launch_variables | Where-Object { $_.variable_id -eq 'studio_root' })
    if ($variables.Count -ne 1) {
        throw "Expected exactly one studio_root variable; found $($variables.Count)."
    }

    # Navigate the JSON source without altering the formatting or other values.
    $arrayKey = '"launch_variables"'
    $keyAt = $raw.IndexOf($arrayKey, [System.StringComparison]::Ordinal)
    if ($keyAt -lt 0) { throw 'launch_variables field missing in JSON text.' }
    $pos = Skip-White $raw ($keyAt + $arrayKey.Length)
    if ($pos -ge $raw.Length -or $raw[$pos] -ne ':') { throw 'Invalid launch_variables property.' }
    $pos = Skip-White $raw ($pos + 1)
    if ($pos -ge $raw.Length -or $raw[$pos] -ne '[') { throw 'launch_variables must be an array.' }
    $pos++

    $targetStart = -1
    $targetEnd = -1
    $found = 0
    while ($pos -lt $raw.Length) {
        $pos = Skip-White $raw $pos
        if ($raw[$pos] -eq ']') { break }
        if ($raw[$pos] -eq ',') { $pos++; continue }
        if ($raw[$pos] -ne '{') { throw "Expected a variable object at offset $pos." }
        $end = Find-ObjectEnd $raw $pos
        $segment = $raw.Substring($pos, $end - $pos + 1)
        $entry = ConvertFrom-Json -InputObject $segment

        if ($entry.variable_id -eq 'studio_root') {
            $found++
            $valueKey = '"launch_value"'
            $valueKeyAt = $segment.IndexOf($valueKey, [System.StringComparison]::Ordinal)
            if ($valueKeyAt -lt 0) { throw 'studio_root is missing launch_value.' }
            if ($segment.IndexOf($valueKey, $valueKeyAt + $valueKey.Length, [System.StringComparison]::Ordinal) -ge 0) {
                throw 'studio_root has multiple launch_value fields.'
            }
            $valueAt = Skip-White $segment ($valueKeyAt + $valueKey.Length)
            if ($segment[$valueAt] -ne ':') { throw 'Invalid launch_value field.' }
            $valueAt = Skip-White $segment ($valueAt + 1)
            $span = Read-JsonString $segment $valueAt
            $targetStart = $pos + $span.Start
            $targetEnd = $pos + $span.End
        }
        $pos = $end + 1
    }
    if ($found -ne 1) { throw "Expected exactly one studio_root object in JSON text; found $found." }
    $updated = $raw.Substring(0, $targetStart) + '"Studio"' + $raw.Substring($targetEnd)

    # Validate the resulting JSON and the new value before committing it.
    $check = ConvertFrom-Json -InputObject $updated
    $checkVariables = @($check.launch_variables | Where-Object { $_.variable_id -eq 'studio_root' })
    if ($checkVariables.Count -ne 1 -or $checkVariables[0].launch_value -cne 'Studio') {
        throw 'Post-edit JSON validation failed.'
    }

    if ($updated -cne $raw) {
        $temp = $cfg + '.portable.tmp'
        try {
            [System.IO.File]::WriteAllText($temp, $updated, (New-Object System.Text.UTF8Encoding($false)))
            [System.IO.File]::Copy($temp, $cfg, $true)
        } finally {
            if (Test-Path -LiteralPath $temp) { Remove-Item -LiteralPath $temp -Force }
        }
    }
    Write-Host '[OK] studio_root=Studio (relative; Launch runtime locates sibling Studio)'
    exit 0
} catch {
    Write-Host ('[ERROR] ' + $_.Exception.Message) -ForegroundColor Red
    exit 1
}
