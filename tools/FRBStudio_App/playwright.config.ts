import { defineConfig } from '@playwright/test';

// FRBStudio_App Playwright policy
// - Do not create root-level playwright-report/ or test-results/
// - Keep runtime artifacts under tests/.runtime/ only
// - Studio-managed JSON evidence is written under data/json/03_tests/
export default defineConfig({
  testDir: './tests',
  outputDir: './tests/.runtime/playwright-output',
  reporter: [['list']],
  use: {
    trace: 'off',
    screenshot: 'off',
    video: 'off'
  }
});
