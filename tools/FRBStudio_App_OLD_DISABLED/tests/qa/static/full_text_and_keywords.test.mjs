import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';

const code = fs.readFileSync('wwwroot/js/responsibilities/search_filter.js', 'utf8');
const scope = vm.createContext({});
vm.runInContext(code, scope);
const SearchFilter = scope.SearchFilter;
const ids = (entries) => Array.from(entries, entry => entry.row.id);

const rows = [
  { id: 'a', title: '社員マスタ', detail: { note: 'Tokyo office' }, childRows: [{ name: '佐藤' }] },
  { id: 'b', title: '社員マスタ', detail: { note: 'Osaka office' }, childRows: [{ name: '田中' }] },
  { id: 'c', title: '部門マスタ', detail: { note: 'Tokyo office' } },
  { id: 'd', title: '東京都', note: '社員向け', number: 2026 }
];

test('full-text uses whitespace-separated AND keywords across nested fields and rows stay scoped', () => {
  assert.deepEqual(ids(SearchFilter.apply(rows, [], { fullText: '社員 tokyo' })), ['a']);
  assert.deepEqual(ids(SearchFilter.apply(rows, [], { fullText: 'TOKYO 社員' })), ['a']);
  assert.deepEqual(ids(SearchFilter.apply(rows, [], { fullText: '社員　Tokyo' })), ['a']);
  assert.deepEqual(ids(SearchFilter.apply(rows, [], { fullText: ' 社員   Tokyo  ' })), ['a']);
  assert.deepEqual(ids(SearchFilter.apply(rows, [], { fullText: '社員 Tokyo 佐藤' })), ['a']);
  assert.deepEqual(ids(SearchFilter.apply(rows, [], { fullText: '社員 Tokyo 田中' })), []);
});

test('single keyword, empty query, and original indexes retain compatibility', () => {
  assert.deepEqual(ids(SearchFilter.apply(rows, [], { fullText: 'tokyo' })), ['a', 'c']);
  assert.deepEqual(Array.from(SearchFilter.apply(rows, [], { fullText: '  ' }), e => e.index), [0, 1, 2, 3]);
  assert.deepEqual(ids(SearchFilter.apply(rows, [], { fullText: '2026' })), [], 'numbers remain excluded');
  assert.deepEqual(ids(SearchFilter.apply(rows, [], { fullText: 'childRows' })), [], 'object keys remain excluded');
});

test('AND full-text combines with per-column criteria as before', () => {
  const criterion = [{ field: 'title', type: 'text', operator: 'equals', value: '社員マスタ' }];
  assert.deepEqual(ids(SearchFilter.apply(rows, criterion, { fullText: 'Tokyo 佐藤' })), ['a']);
  assert.deepEqual(ids(SearchFilter.apply(rows, criterion, { fullText: 'Osaka 佐藤' })), []);
});

test('legacy fallback predicate has same AND behavior when SearchFilter is absent', () => {
  const source = fs.readFileSync('wwwroot/js/renderers/grid_detail.js', 'utf8');
  const from = source.indexOf('function fallbackMatchesStudioFullText(');
  const to = source.indexOf('\nfunction applySearch()', from);
  assert.ok(from >= 0 && to > from);
  const sandbox = vm.createContext({});
  vm.runInContext(source.slice(from, to), sandbox);
  assert.equal(sandbox.fallbackMatchesStudioFullText(rows[0], '社員 佐藤'), true);
  assert.equal(sandbox.fallbackMatchesStudioFullText(rows[0], '社員 田中'), false);
  assert.equal(sandbox.fallbackMatchesStudioFullText(rows[0], ' Tokyo\t佐藤 '), true);
  assert.equal(sandbox.fallbackMatchesStudioFullText(rows[0], '  '), true);
  assert.equal(sandbox.fallbackMatchesStudioFullText(rows[0], '2026'), false);
});

test('global search UI advertises Smart Search and refreshes both script caches', () => {
  const html = fs.readFileSync('wwwroot/index.html', 'utf8');
  assert.match(html, /placeholder="全文検索・空白AND・OR・括弧・項目名=値"/);
  assert.match(html, /js\/responsibilities\/search_filter\.js\?[^"\n]*smart=20261022/);
  assert.match(html, /js\/renderers\/grid_detail\.js\?[^"\n]*smart=20261022/);
});
