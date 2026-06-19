# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: ncjs-screen-state-compare.checks.spec.ts >> 画面状態JSONをExpectedと比較してDiffを保存できる
- Location: tests\ncjs-screen-state-compare.checks.spec.ts:191:5

# Error details

```
Error: expect(received).toBe(expected) // Object.is equality

Expected: "pass"
Received: "fail"
```

# Page snapshot

```yaml
- generic [active] [ref=e1]:
  - banner [ref=e2]:
    - generic [ref=e3]:
      - generic [ref=e4]: FRB Studio Lab
      - heading "No-Code JSON Studiov0.3-draft" [level=1] [ref=e5]
      - paragraph [ref=e6]: 1画面1グリッド / Header Form + Search Form + Grid + Detail Dialog
    - region "JSON読み込み" [ref=e7]:
      - generic [ref=e8]:
        - generic [ref=e9]: 画面定義JSON
        - combobox "画面定義JSON" [ref=e10]
      - generic [ref=e11]:
        - generic [ref=e12]: 対象JSON
        - combobox "対象JSON" [ref=e13]
      - generic [ref=e14] [cursor=pointer]:
        - generic [ref=e15]: 定義Drop
        - generic [ref=e16]: Drop
      - generic [ref=e17] [cursor=pointer]:
        - generic [ref=e18]: 対象Drop
        - generic [ref=e19]: Drop
      - button "読み込み" [ref=e20] [cursor=pointer]
      - button "保存" [disabled] [ref=e21]
      - button "Markdown出力→Viewer" [disabled] [ref=e22]
      - link "📝 Markdown Viewer / Editor" [ref=e23] [cursor=pointer]:
        - /url: mdViewer.html
        - generic [ref=e24]: 📝
        - generic [ref=e25]:
          - text: Markdown
          - generic [ref=e26]: Viewer / Editor
      - generic [ref=e27]: "一覧を更新しました: defs 7件 / data 7件"
  - main [ref=e28]
```

# Test source

```ts
  167 |     }
  168 | 
  169 |     case 'exists':
  170 |       pass = actualValue !== undefined && actualValue !== null && displayValue(actualValue) !== '';
  171 |       break;
  172 | 
  173 |     default:
  174 |       throw new Error(`未対応のcheck.typeです: ${(check as { type: string }).type}`);
  175 |   }
  176 | 
  177 |   return {
  178 |     name: check.name,
  179 |     type: check.type,
  180 |     target: check.target,
  181 |     expected: displayValue(expectedValue),
  182 |     actual: displayValue(actualValue),
  183 |     missing,
  184 |     pass,
  185 |     message: pass
  186 |       ? 'OK'
  187 |       : `${check.name} failed: expected ${displayValue(expectedValue)}, actual ${displayValue(actualValue)}`
  188 |   };
  189 | }
  190 | 
  191 | test('画面状態JSONをExpectedと比較してDiffを保存できる', async ({ page }, testInfo) => {
  192 |   await page.goto(BASE_URL);
  193 | 
  194 |   const state = await page.evaluate(() => {
  195 |     return (window as any).__NCJS_exportScreenState();
  196 |   }) as ScreenState;
  197 | 
  198 |   const pattern = readExpectedPattern();
  199 | 
  200 |   if (!Array.isArray(pattern.checks)) {
  201 |     throw new Error('expected.json の checks が Array ではありません');
  202 |   }
  203 | 
  204 |   const checks = pattern.checks.map(check => evaluateCheck(check, state));
  205 |   const failedChecks = checks.filter(check => !check.pass);
  206 |   const status = failedChecks.length === 0 ? 'pass' : 'fail';
  207 |   const firstFailure = failedChecks[0] ?? null;
  208 |   const capturedAt = new Date().toISOString();
  209 | 
  210 |   const emphasizedDiff = {
  211 |     view_def: DIFF_VIEW_DEF,
  212 |     testId: pattern.testId || TEST_ID,
  213 |     title: pattern.title,
  214 |     capturedAt,
  215 |     url: BASE_URL,
  216 |     status,
  217 |     checks,
  218 |     resultLabel: status === 'pass' ? '✅ PASS' : '🚨 FAIL',
  219 |     failedCount: failedChecks.length,
  220 |     failedChecks: failedChecks.map(check => check.name),
  221 |     summary: failedChecks.length === 0
  222 |       ? '✅ すべてのチェックに合格しました'
  223 |       : `🚨 ${failedChecks.length}件の差分を検出しました: ${failedChecks.map(check => check.name).join(', ')}`,
  224 |     firstFailure: firstFailure
  225 |       ? {
  226 |           name: firstFailure.name,
  227 |           type: firstFailure.type,
  228 |           target: firstFailure.target,
  229 |           expected: firstFailure.expected,
  230 |           actual: firstFailure.actual,
  231 |           missing: firstFailure.missing
  232 |         }
  233 |       : null,
  234 |     actualState: state
  235 |   };
  236 | 
  237 |   const resultRoot = path.join(process.cwd(), 'tests_screen_state', 'test_results');
  238 | 
  239 |   const actualDir = path.join(resultRoot, 'actual');
  240 |   const diffDir = path.join(resultRoot, 'diff');
  241 | 
  242 |   fs.mkdirSync(actualDir, { recursive: true });
  243 |   fs.mkdirSync(diffDir, { recursive: true });
  244 | 
  245 |   const actualPath = path.join(actualDir, `${TEST_ID}.actual.json`);
  246 |   const diffPath = path.join(diffDir, `${TEST_ID}.diff.json`);
  247 | 
  248 |   fs.writeFileSync(actualPath, JSON.stringify({
  249 |     testId: pattern.testId || TEST_ID,
  250 |     title: pattern.title,
  251 |     capturedAt,
  252 |     state
  253 |   }, null, 2), 'utf8');
  254 | 
  255 |   fs.writeFileSync(diffPath, JSON.stringify(emphasizedDiff, null, 2), 'utf8');
  256 | 
  257 |   await testInfo.attach(`${TEST_ID}.actual.json`, {
  258 |     path: actualPath,
  259 |     contentType: 'application/json'
  260 |   });
  261 | 
  262 |   await testInfo.attach(`${TEST_ID}.diff.json`, {
  263 |     path: diffPath,
  264 |     contentType: 'application/json'
  265 |   });
  266 | 
> 267 |   expect(emphasizedDiff.status).toBe('pass');
      |                                 ^ Error: expect(received).toBe(expected) // Object.is equality
  268 | });
  269 | 
```