# FRBStudio_App runtime artifact cleanup
# Deletes generated Playwright/legacy folders that should not be source-controlled.

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
