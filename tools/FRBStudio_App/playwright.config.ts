import { defineConfig } from '@playwright/test';

// FRBStudio runtime artifacts must not be generated at repository root.
// Test Evidence JSON remains under data/json/03_tests/**.
export default defineConfig({
  outputDir: 'tests/.runtime/playwright-output',
  reporter: [['list']],
});
