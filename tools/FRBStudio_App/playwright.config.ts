import { defineConfig } from '@playwright/test';

// FRBStudio runtime artifacts must not be generated at repository root.
// Test Evidence JSON remains under data/json/03_tests/**.
//
// tests/qa/static/** is owned by the Node.js test runner.
// Exclude it from Playwright discovery so `npx playwright test --ui`
// does not also execute/update Node-test evidence or diff artifacts.
export default defineConfig({
  testIgnore: [
    '**/qa/static/**',
  ],
  outputDir: 'tests/.runtime/playwright-output',
  reporter: [['list']],
});
