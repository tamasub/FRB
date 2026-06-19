# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: ncjs-screen-state-compare.spec.ts >> 画面状態JSONをExpectedと比較してDiffを保存できる
- Location: tests\ncjs-screen-state-compare.spec.ts:33:5

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
      - generic [ref=e27]: "一覧を更新しました: defs 6件 / data 7件"
  - main [ref=e28]
```

# Test source

```ts
  44  |   );
  45  | 
  46  |   const pattern = JSON.parse(
  47  |     fs.readFileSync(patternPath, 'utf8')
  48  |   ) as ExpectedPattern;
  49  | 
  50  |   const actualButtonLabels = state.buttons ?? [];
  51  |   const actualInputIds = (state.inputs ?? []).map(input => input.id);
  52  | 
  53  |   const diff = {
  54  |     view_def: DIFF_VIEW_DEF,
  55  |     testId: TEST_ID,
  56  |     title: pattern.title,
  57  |     capturedAt: new Date().toISOString(),
  58  |     url: BASE_URL,
  59  |     status: 'pass',
  60  |     checks: [
  61  |       {
  62  |         name: 'appTitle',
  63  |         expected: pattern.expected.appTitle,
  64  |         actual: state.appTitle,
  65  |         pass: state.appTitle === pattern.expected.appTitle
  66  |       },
  67  |       {
  68  |         name: 'headerText',
  69  |         expected: pattern.expected.headerText,
  70  |         actual: state.headerText,
  71  |         pass: state.headerText === pattern.expected.headerText
  72  |       },
  73  |       {
  74  |         name: 'requiredButtons',
  75  |         expected: pattern.expected.requiredButtons,
  76  |         actual: actualButtonLabels,
  77  |         missing: missingItems(pattern.expected.requiredButtons, actualButtonLabels),
  78  |         pass: missingItems(pattern.expected.requiredButtons, actualButtonLabels).length === 0
  79  |       },
  80  |       {
  81  |         name: 'requiredInputIds',
  82  |         expected: pattern.expected.requiredInputIds,
  83  |         actual: actualInputIds,
  84  |         missing: missingItems(pattern.expected.requiredInputIds, actualInputIds),
  85  |         pass: missingItems(pattern.expected.requiredInputIds, actualInputIds).length === 0
  86  |       }
  87  |     ],
  88  |     actualState: state
  89  |   };
  90  | 
  91  |   const failedChecks = diff.checks.filter(check => !check.pass);
  92  |   diff.status = failedChecks.length === 0 ? 'pass' : 'fail';
  93  | 
  94  |   const firstFailure = failedChecks[0] ?? null;
  95  | 
  96  |   const emphasizedDiff = {
  97  |     ...diff,
  98  |     resultLabel: diff.status === 'pass' ? '✅ PASS' : '🚨 FAIL',
  99  |     failedCount: failedChecks.length,
  100 |     failedChecks: failedChecks.map(check => check.name),
  101 |     summary: failedChecks.length === 0
  102 |       ? '✅ すべてのチェックに合格しました'
  103 |       : `🚨 ${failedChecks.length}件の差分を検出しました: ${failedChecks.map(check => check.name).join(', ')}`,
  104 |     firstFailure: firstFailure
  105 |       ? {
  106 |           name: firstFailure.name,
  107 |           expected: firstFailure.expected,
  108 |           actual: firstFailure.actual,
  109 |           missing: 'missing' in firstFailure ? firstFailure.missing : undefined
  110 |         }
  111 |       : null
  112 |   };
  113 | 
  114 |   const resultRoot = path.join(process.cwd(), 'tests_screen_state', 'test_results');
  115 | 
  116 |   const actualDir = path.join(resultRoot, 'actual');
  117 |   const diffDir = path.join(resultRoot, 'diff');
  118 | 
  119 |   fs.mkdirSync(actualDir, { recursive: true });
  120 |   fs.mkdirSync(diffDir, { recursive: true });
  121 | 
  122 |   const actualPath = path.join(actualDir, `${TEST_ID}.actual.json`);
  123 |   const diffPath = path.join(diffDir, `${TEST_ID}.diff.json`);
  124 | 
  125 |   fs.writeFileSync(actualPath, JSON.stringify({
  126 |     view_def: DIFF_VIEW_DEF,
  127 |     testId: TEST_ID,
  128 |     capturedAt: new Date().toISOString(),
  129 |     state
  130 |   }, null, 2), 'utf8');
  131 | 
  132 |   fs.writeFileSync(diffPath, JSON.stringify(emphasizedDiff, null, 2), 'utf8');
  133 | 
  134 |   await testInfo.attach(`${TEST_ID}.actual.json`, {
  135 |     path: actualPath,
  136 |     contentType: 'application/json'
  137 |   });
  138 | 
  139 |   await testInfo.attach(`${TEST_ID}.diff.json`, {
  140 |     path: diffPath,
  141 |     contentType: 'application/json'
  142 |   });
  143 | 
> 144 |   expect(emphasizedDiff.status).toBe('pass');
      |                                 ^ Error: expect(received).toBe(expected) // Object.is equality
  145 | 
  146 | });
  147 | 
```