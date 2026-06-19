import { test, expect } from '@playwright/test';
import fs from 'fs';
import path from 'path';

const BASE_URL = 'http://localhost:5055/';

test('画面状態JSONを取得してファイル保存できる', async ({ page }, testInfo) => {
  await page.goto(BASE_URL);

  const state = await page.evaluate(() => {
    return (window as any).__NCJS_exportScreenState();
  });

  expect(state.appTitle).toMatch(/No-Code|JSON|FRB|Studio/i);
  expect(state.headerText).toBeTruthy();
  expect(state.buttons.length).toBeGreaterThan(0);

  const output = {
    testId: 'screen_state_smoke_001',
    title: '初期表示の画面状態JSONを取得する',
    capturedAt: new Date().toISOString(),
    url: BASE_URL,
    state
  };

  const outDir = path.join(process.cwd(), 'test_results', 'actual');
  fs.mkdirSync(outDir, { recursive: true });

  const outPath = path.join(outDir, 'screen_state_smoke_001.actual.json');
  fs.writeFileSync(outPath, JSON.stringify(output, null, 2), 'utf8');

  await testInfo.attach('screen_state_smoke_001.actual.json', {
    path: outPath,
    contentType: 'application/json'
  });
});