# FRBStudio_App runtime artifact cleanup
# v0.14.18 Delivery / Cleanup / ZIP Safety Policy
#
# Deletes regenerated runtime artifacts that must not be included in returned source ZIPs.
# This script must NOT delete Test Evidence source-of-truth files under data/json/03_tests/**.
# Expected / Actual / Diff / Test Pattern files are evidence, not runtime trash.

$ErrorActionPreference = "Stop"

$targets = @(
  ".\playwright-report",
  ".\test-results",
  ".\test_results",
  ".\tests_screen_state",
  ".\tests\.runtime"
)

foreach ($target in $targets) {
  if (Test-Path -LiteralPath $target) {
    Remove-Item -LiteralPath $target -Recurse -Force
    Write-Host "Removed $target"
  }
}

$mustNotExist = @(
  ".\playwright-report",
  ".\test-results",
  ".\test_results",
  ".\tests_screen_state",
  ".\tests\.runtime"
)

$remaining = @()
foreach ($target in $mustNotExist) {
  if (Test-Path -LiteralPath $target) {
    $remaining += $target
  }
}

if ($remaining.Count -gt 0) {
  Write-Error ("Runtime artifact cleanup incomplete: " + ($remaining -join ", "))
}

Write-Host "FRBStudio runtime artifact cleanup completed. Test Evidence under data/json/03_tests was not touched."
Write-Host "Do not include node_modules, playwright-report, test-results, test_results, tests/.runtime, or tests_screen_state in returned ZIPs."
