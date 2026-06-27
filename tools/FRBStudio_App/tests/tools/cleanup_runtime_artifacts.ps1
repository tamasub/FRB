# FRBStudio_App runtime artifact cleanup
# Deletes generated Playwright/legacy folders that should not be source-controlled.
# This script removes only regenerated runtime artifacts.
# It must not delete Test Evidence source-of-truth files under data/json/03_tests/**.

$targets = @(
  ".\playwright-report",
  ".\test-results",
  ".\test_results",
  ".\tests_screen_state",
  ".\tests\.runtime"
)

foreach ($target in $targets) {
  if (Test-Path $target) {
    Remove-Item -Recurse -Force $target
    Write-Host "Removed $target"
  }
}

Write-Host "FRBStudio runtime artifact cleanup completed. Test Evidence under data/json/03_tests was not touched."
