import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import test from 'node:test';
import vm from 'node:vm';

const root = process.cwd();
const readText = (relativePath) => fs.readFileSync(path.join(root, relativePath), 'utf8');
const readJson = (relativePath) => JSON.parse(readText(relativePath));

function loadSearchFilter() {
  const context = { console };
  vm.createContext(context);
  vm.runInContext(
    readText('wwwroot/js/responsibilities/search_filter.js'),
    context,
    { filename: 'wwwroot/js/responsibilities/search_filter.js' }
  );
  return context.SearchFilter;
}

const SearchFilter = loadSearchFilter();
const ids = (rows) => Array.from(rows, entry => entry.row.id);

test('SearchFilter implements every active SearchOperatorRegistry v0.1 operator', () => {
  const registry = readJson('data/json/config/search_operator_registry_v0_1.json');
  const active = registry.operators.filter(item => item.status === 'active').map(item => item.id);
  assert.deepEqual(Array.from(SearchFilter.operatorIds), active);
  for (const operatorId of active) {
    assert.equal(SearchFilter.supportsOperator(operatorId), true, operatorId);
  }
  assert.equal(SearchFilter.supportsOperator('in'), false, 'planned multi-select operator must not become active in Phase 3');
});

test('text operators support contains / not_contains / equals / not_equals', () => {
  const rows = [
    { id: 'a', caption: 'Alpha Beta' },
    { id: 'b', caption: 'beta' },
    { id: 'c', caption: 'Gamma' }
  ];
  assert.deepEqual(ids(SearchFilter.apply(rows, [{ field: 'caption', type: 'text', operator: 'contains', value: 'BETA' }])), ['a', 'b']);
  assert.deepEqual(ids(SearchFilter.apply(rows, [{ field: 'caption', type: 'text', operator: 'not_contains', value: 'beta' }])), ['c']);
  assert.deepEqual(ids(SearchFilter.apply(rows, [{ field: 'caption', type: 'text', operator: 'equals', value: 'beta' }])), ['b']);
  assert.deepEqual(ids(SearchFilter.apply(rows, [{ field: 'caption', type: 'text', operator: 'not_equals', value: 'beta' }])), ['a', 'c']);
});

test('numeric operators are finite-number aware and include boundaries', () => {
  const rows = [
    { id: 'zero', score: 0 },
    { id: 'five', score: 5 },
    { id: 'ten', score: 10 },
    { id: 'blank', score: '' },
    { id: 'invalid', score: 'x' }
  ];
  assert.deepEqual(ids(SearchFilter.apply(rows, [{ field: 'score', type: 'number', operator: 'gte', value: '5' }])), ['five', 'ten']);
  assert.deepEqual(ids(SearchFilter.apply(rows, [{ field: 'score', type: 'number', operator: 'lte', value: '5' }])), ['zero', 'five']);
  assert.deepEqual(ids(SearchFilter.apply(rows, [{ field: 'score', type: 'number', operator: 'equals', value: '5' }])), ['five']);
  assert.deepEqual(ids(SearchFilter.apply(rows, [{ field: 'score', type: 'number', operator: 'not_equals', value: '5' }])), ['zero', 'ten', 'blank', 'invalid']);
});

test('between supports From-only / To-only / both and inclusive boundaries', () => {
  const rows = [
    { id: '1', score: 1 },
    { id: '5', score: 5 },
    { id: '10', score: 10 },
    { id: '20', score: 20 }
  ];
  assert.deepEqual(ids(SearchFilter.apply(rows, [{ field: 'score', type: 'number', operator: 'between', from: 5, to: 10 }])), ['5', '10']);
  assert.deepEqual(ids(SearchFilter.apply(rows, [{ field: 'score', type: 'number', operator: 'between', from: 10 }])), ['10', '20']);
  assert.deepEqual(ids(SearchFilter.apply(rows, [{ field: 'score', type: 'number', operator: 'between', to: 5 }])), ['1', '5']);
  assert.deepEqual(ids(SearchFilter.apply(rows, [{ field: 'score', value_family: 'integer', operator: 'between', value: { from: 5, to: 10 } }])), ['5', '10']);
});

test('blank / not_blank work without an input value and do not treat 0 or false as blank', () => {
  const rows = [
    { id: 'null', value: null },
    { id: 'undefined' },
    { id: 'empty', value: '' },
    { id: 'spaces', value: '   ' },
    { id: 'array', value: [] },
    { id: 'zero', value: 0 },
    { id: 'false', value: false },
    { id: 'text', value: 'x' }
  ];
  assert.deepEqual(ids(SearchFilter.apply(rows, [{ field: 'value', type: 'text', operator: 'blank' }])), ['null', 'undefined', 'empty', 'spaces', 'array']);
  assert.deepEqual(ids(SearchFilter.apply(rows, [{ field: 'value', type: 'text', operator: 'not_blank' }])), ['zero', 'false', 'text']);
  assert.equal(SearchFilter.criterionIsActive({ field: 'value', operator: 'blank', raw: '' }), true);
  assert.equal(SearchFilter.criterionIsActive({ field: 'value', operator: 'not_blank', raw: '' }), true);
});

test('date comparison is strict YYYY-MM-DD and supports range boundaries', () => {
  const rows = [
    { id: 'before', day: '2026-07-31' },
    { id: 'from', day: '2026-08-01' },
    { id: 'inside', day: '2026-08-15' },
    { id: 'to', day: '2026-08-31' },
    { id: 'after', day: '2026-09-01' },
    { id: 'invalid', day: '2026-02-30' }
  ];
  assert.deepEqual(ids(SearchFilter.apply(rows, [{ field: 'day', value_family: 'date', operator: 'between', from: '2026-08-01', to: '2026-08-31' }])), ['from', 'inside', 'to']);
  assert.deepEqual(ids(SearchFilter.apply(rows, [{ field: 'day', value_family: 'date', operator: 'gte', value: '2026-08-31' }])), ['to', 'after']);
  assert.deepEqual(ids(SearchFilter.apply(rows, [{ field: 'day', value_family: 'date', operator: 'lte', value: '2026-08-01' }])), ['before', 'from']);
  assert.equal(SearchFilter.parseDateValue('2026-02-30'), null);
});

test('local datetime and instant comparison use temporal ordering without browser-local timezone dependence', () => {
  const localRows = [
    { id: 'a', at: '2026-08-16T09:00' },
    { id: 'b', at: '2026-08-16T12:30:00' },
    { id: 'c', at: '2026-08-17T00:00' }
  ];
  assert.deepEqual(ids(SearchFilter.apply(localRows, [{ field: 'at', value_family: 'datetime', operator: 'between', from: '2026-08-16T12:30', to: '2026-08-17T00:00' }])), ['b', 'c']);
  assert.equal(SearchFilter.parseLocalDateTimeValue('2026-08-16T25:00'), null);

  const instantRows = [
    { id: 'z', at: '2026-08-16T00:00:00Z' },
    { id: 'jst', at: '2026-08-16T10:00:00+09:00' }
  ];
  assert.deepEqual(ids(SearchFilter.apply(instantRows, [{ field: 'at', value_family: 'instant', operator: 'gte', value: '2026-08-16T00:30:00Z' }])), ['jst']);
  assert.equal(SearchFilter.parseInstantValue('2026-08-16T10:00:00'), null);
});

test('legacy raw criteria, legacy >= alias, and multi-select matching remain compatible', () => {
  const rows = [
    { id: 'a', score: 3, tags: ['x', 'y'] },
    { id: 'b', score: 10, tags: ['z'] },
    { id: 'c', score: 7, tags: ['y'] }
  ];
  assert.deepEqual(ids(SearchFilter.apply(rows, [{ field: 'score', raw: '7', type: 'number', operator: '>=' }])), ['b', 'c']);
  assert.deepEqual(ids(SearchFilter.apply(rows, [{ field: 'tags', raw: ['z'], type: 'select' }])), ['b']);
});

test('unknown operators fail closed instead of silently becoming contains/equals', () => {
  assert.equal(SearchFilter.matchesCriterion({ caption: 'Alpha' }, { field: 'caption', type: 'text', operator: 'future_unknown', value: 'Alpha' }), false);
});

test('full-text search remains AND-combined with structured criteria', () => {
  const rows = [
    { id: 'a', caption: 'Alpha', detail: { memo: 'Needle' } },
    { id: 'b', caption: 'Beta', detail: { memo: 'Needle' } },
    { id: 'c', caption: 'Gamma', detail: { memo: 'Other' } }
  ];
  assert.deepEqual(ids(SearchFilter.apply(
    rows,
    [{ field: 'caption', type: 'text', operator: 'not_equals', value: 'Beta' }],
    { fullText: 'needle' }
  )), ['a']);
});

test('Phase 3 implementation remains UI-independent and index cache key is advanced', () => {
  const source = readText('wwwroot/js/responsibilities/search_filter.js');
  assert.doesNotMatch(source, /document\.|querySelector|addEventListener/);
  const html = readText('wwwroot/index.html');
  assert.match(html, /js\/responsibilities\/search_filter\.js\?v=standard-search-ui-01867/);
});

test('studio_work_0188 is completed and Phase 4 remains an explicit follow-up', () => {
  const incident = readJson('data/json/01_main/_studio_work_incident_data_v2.json');
  const item = incident.work_items.find(work => work.work_item_id === 'studio_work_0188');
  const phase2 = incident.work_items.find(work => work.work_item_id === 'studio_work_0187');
  assert.ok(item && phase2);
  assert.equal(item.phase, 'v0.18.66-standard-search-filter-operators-phase3');
  assert.equal(item.status, '完了');
  assert.equal(item.follow_up_status, 'COMPLETED');
  assert.ok(item.follow_up_actions.some(action => action.related_ids?.includes('studio_work_0189') && action.status === 'COMPLETED'));
  assert.ok(phase2.follow_up_actions.some(action => action.related_ids?.includes('studio_work_0188') && action.status === 'COMPLETED'));
  assert.equal(incident.items_count, incident.work_items.length);
});
