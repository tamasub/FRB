import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import test from 'node:test';
import vm from 'node:vm';

const root = process.cwd();
const readText = (relativePath) => fs.readFileSync(path.join(root, relativePath), 'utf8');
const readJson = (relativePath) => JSON.parse(readText(relativePath));

function loadResolver() {
  const sandbox = { console, JSON, globalThis: null };
  sandbox.globalThis = sandbox;
  vm.createContext(sandbox);
  vm.runInContext(readText('wwwroot/js/services/search_capability_resolver.js'), sandbox, {
    filename: 'wwwroot/js/services/search_capability_resolver.js'
  });
  return sandbox;
}

function resolve(field, options={}) {
  const sandbox = loadResolver();
  sandbox.__searchRegistry = options.searchRegistry ?? readJson('data/json/config/search_operator_registry_v0_1.json');
  sandbox.__validationRegistry = options.validationRegistry ?? readJson('data/json/config/validation_type_registry_v0_1.json');
  sandbox.__field = field;
  sandbox.__resolvedFieldContract = options.resolvedFieldContract ?? null;
  vm.runInContext(`
    globalThis.__result = new SearchCapabilityResolver({
      searchOperatorRegistry: __searchRegistry,
      validationTypeRegistry: __validationRegistry
    }).resolve(__field, { resolvedFieldContract: __resolvedFieldContract });
  `, sandbox);
  return JSON.parse(JSON.stringify(sandbox.__result));
}

test('Validation Type value_family takes precedence over visual Field type', () => {
  const result = resolve({
    field: 'quantity_text',
    type: 'text',
    validation_type: 'studio.integer.signed',
    search: { visible: true }
  });
  assert.equal(result.resolution_status, 'RESOLVED');
  assert.equal(result.value_family, 'integer');
  assert.equal(result.value_family_source, 'validation_type_registry');
  assert.equal(result.derived.operator_set_id, 'numeric_standard');
  assert.equal(result.effective.default_operator, 'between');
  assert.ok(result.effective.operator_ids.includes('gte'));
  assert.ok(result.effective.operator_ids.includes('lte'));
  assert.equal(result.derived.source, 'validation_value_family');
  assert.equal(result.source.search_registry_version, '0.1.0');
  assert.equal(result.source.validation_registry_version, '0.1.0');
});

test('Field type fallback resolves select without a Validation Type', () => {
  const result = resolve({
    field: 'status',
    type: 'select',
    search: { visible: true }
  });
  assert.equal(result.resolution_status, 'RESOLVED');
  assert.equal(result.value_family, '');
  assert.equal(result.value_family_source, 'field_type_fallback');
  assert.equal(result.derived.operator_set_id, 'select_standard');
  assert.equal(result.effective.default_operator, 'equals');
  assert.deepEqual(result.effective.operator_ids, ['equals', 'not_equals', 'blank', 'not_blank']);
});

test('Resolved Field Contract value_family can drive search without re-resolving Validation Type', () => {
  const result = resolve({
    field_path: '$.measurement_date',
    type: 'text',
    search: { visible: true }
  }, {
    validationRegistry: null,
    resolvedFieldContract: {
      resolution_status: 'RESOLVED',
      validation_type_id: 'studio.date.ymd',
      value_family: 'date'
    }
  });
  assert.equal(result.resolution_status, 'RESOLVED');
  assert.equal(result.value_family, 'date');
  assert.equal(result.value_family_source, 'resolved_field_contract');
  assert.equal(result.derived.operator_set_id, 'date_standard');
  assert.equal(result.effective.default_operator, 'between');
});

test('search.operator_set can replace the derived set only with a compatible registered set', () => {
  const searchRegistry = readJson('data/json/config/search_operator_registry_v0_1.json');
  searchRegistry.operator_sets.push({
    id: 'text_exact',
    caption: 'Text exact search',
    status: 'active',
    value_families: ['string'],
    field_types: ['text', 'textarea'],
    default_operator: 'equals',
    operator_ids: ['equals', 'not_equals', 'blank', 'not_blank']
  });
  const result = resolve({
    field: 'caption',
    type: 'text',
    search: { visible: true, operator_set: 'text_exact' }
  }, { searchRegistry });
  assert.equal(result.resolution_status, 'RESOLVED');
  assert.equal(result.derived.operator_set_id, 'text_standard');
  assert.equal(result.derived.source, 'field_type_fallback');
  assert.equal(result.effective.operator_set_id, 'text_exact');
  assert.equal(result.effective.default_operator, 'equals');
  assert.equal(result.overrides.operator_set.applied, true);
});

test('search.operator_set rejects a registered but incompatible set', () => {
  const result = resolve({
    field: 'caption',
    type: 'text',
    search: { visible: true, operator_set: 'numeric_standard' }
  });
  assert.equal(result.resolution_status, 'INVALID');
  assert.ok(result.issues.some(issue => issue.code === 'SEARCH_OPERATOR_SET_INCOMPATIBLE'));
});

test('search.operators narrows the effective set and search.operator selects the remaining default', () => {
  const result = resolve({
    field: 'caption',
    type: 'text',
    search: {
      visible: true,
      operators: ['equals', 'not_equals', 'blank', 'not_blank'],
      operator: 'equals'
    }
  });
  assert.equal(result.resolution_status, 'RESOLVED');
  assert.deepEqual(result.effective.operator_ids, ['equals', 'not_equals', 'blank', 'not_blank']);
  assert.equal(result.effective.default_operator, 'equals');
  assert.equal(result.overrides.operators.applied, true);
  assert.equal(result.overrides.operator.applied, true);
});

test('narrowing that removes the standard default requires explicit search.operator', () => {
  const result = resolve({
    field: 'caption',
    type: 'text',
    search: {
      visible: true,
      operators: ['equals', 'not_equals']
    }
  });
  assert.equal(result.resolution_status, 'INVALID');
  assert.ok(result.issues.some(issue => issue.code === 'SEARCH_DEFAULT_OPERATOR_REMOVED_BY_OVERRIDE'));
});

test('search.operators is narrowing only and cannot inject an Operator outside the resolved set', () => {
  const result = resolve({
    field: 'caption',
    type: 'text',
    search: {
      visible: true,
      operators: ['contains', 'between'],
      operator: 'contains'
    }
  });
  assert.equal(result.resolution_status, 'INVALID');
  assert.ok(result.issues.some(issue => issue.code === 'SEARCH_OPERATORS_OVERRIDE_NOT_NARROWING' && issue.operator === 'between'));
});

test('blank legacy search.operator is treated as no override for compatibility', () => {
  const result = resolve({
    field: 'caption',
    type: 'text',
    search: { visible: true, operator: '' }
  });
  assert.equal(result.resolution_status, 'RESOLVED');
  assert.equal(result.effective.default_operator, 'contains');
  assert.equal(result.overrides.operator.defined, false);
});

test('explicit unknown Validation Type is INVALID rather than silently falling back', () => {
  const result = resolve({
    field: 'score',
    type: 'number',
    validation_type: 'studio.unknown.type',
    search: { visible: true }
  });
  assert.equal(result.resolution_status, 'INVALID');
  assert.ok(result.issues.some(issue => issue.code === 'VALIDATION_TYPE_NOT_FOUND'));
});

test('unknown Field type without Validation Type is UNSUPPORTED, not silently treated as text', () => {
  const result = resolve({
    field: 'custom',
    type: 'custom_plugin',
    search: { visible: true }
  });
  assert.equal(result.resolution_status, 'UNSUPPORTED');
  assert.equal(result.effective.operator_ids.length, 0);
  assert.ok(result.issues.some(issue => issue.code === 'SEARCH_OPERATOR_SET_UNSUPPORTED'));
});

test('resolver remains UI-independent and is loaded before SearchFilter in index.html', () => {
  const source = readText('wwwroot/js/services/search_capability_resolver.js');
  assert.doesNotMatch(source, /document\.|querySelector|HTMLElement|HTMLInputElement|addEventListener/);
  const html = readText('wwwroot/index.html');
  const resolverIndex = html.indexOf('js/services/search_capability_resolver.js');
  const filterIndex = html.indexOf('js/responsibilities/search_filter.js');
  assert.ok(resolverIndex >= 0);
  assert.ok(filterIndex > resolverIndex);
});

test('Phase 2 through Phase 6 are registered as concrete work items before Phase 2 completion', () => {
  const incident = readJson('data/json/01_main/_studio_work_incident_data_v2.json');
  const expected = [
    ['studio_work_0187', 'v0.18.65-standard-search-capability-resolver-phase2'],
    ['studio_work_0188', 'v0.18.66-standard-search-filter-operators-phase3'],
    ['studio_work_0189', 'v0.18.67-standard-search-ui-context-menu-phase4'],
    ['studio_work_0190', 'v0.18.68-standard-search-viewdef-standardization-phase5'],
    ['studio_work_0191', 'v0.18.69-definition-driven-search-test-phase6']
  ];
  for (const [workItemId, phase] of expected) {
    const item = incident.work_items.find(work => work.work_item_id === workItemId);
    assert.ok(item, `${workItemId} not registered`);
    assert.equal(item.phase, phase);
  }
  assert.equal(incident.items_count, incident.work_items.length);
});
