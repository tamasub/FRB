import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import test from 'node:test';

const root = process.cwd();
const readJson = (relativePath) => JSON.parse(fs.readFileSync(path.join(root, relativePath), 'utf8'));

const registryPath = 'data/json/config/search_operator_registry_v0_1.json';
const validationRegistryPath = 'data/json/config/validation_type_registry_v0_1.json';
const schemaPath = 'data/json/00_rules/frb_view_def_schema_v0_9.json';
const rulesPath = 'data/json/00_rules/frb_viewdef_generation_rules_data_v0_1.json';
const schemaReviewPath = 'data/json/00_rules/frb_view_def_schema_review_data_v0_1.json';
const incidentPath = 'data/json/01_main/_studio_work_incident_data_v2.json';

test('SearchOperatorRegistry is the single vocabulary source and all active references are internally valid', () => {
  const registry = readJson(registryPath);
  assert.equal(registry.document_type, 'search_operator_registry');
  assert.equal(registry.validation_type_registry_ref, 'config/validation_type_registry_v0_1.json');

  const operatorIds = registry.operators.map((item) => item.id);
  const operatorSetIds = registry.operator_sets.map((item) => item.id);
  assert.equal(new Set(operatorIds).size, operatorIds.length);
  assert.equal(new Set(operatorSetIds).size, operatorSetIds.length);

  const activeOperatorIds = new Set(registry.operators.filter((item) => item.status === 'active').map((item) => item.id));
  for (const set of registry.operator_sets.filter((item) => item.status === 'active')) {
    assert.ok(set.operator_ids.length > 0, `${set.id} has no operators`);
    assert.ok(set.operator_ids.includes(set.default_operator), `${set.id} default is outside its operator_ids`);
    for (const operatorId of set.operator_ids) {
      assert.ok(activeOperatorIds.has(operatorId), `${set.id} references inactive/unknown operator ${operatorId}`);
    }
  }
});

test('standard operator sets cover text, numeric, temporal, boolean, and select with range-first numeric/date defaults', () => {
  const registry = readJson(registryPath);
  const sets = new Map(registry.operator_sets.map((item) => [item.id, item]));
  assert.equal(sets.get('text_standard')?.default_operator, 'contains');
  assert.equal(sets.get('numeric_standard')?.default_operator, 'between');
  assert.equal(sets.get('date_standard')?.default_operator, 'between');
  assert.equal(sets.get('boolean_standard')?.default_operator, 'equals');
  assert.equal(sets.get('select_standard')?.default_operator, 'equals');
  assert.deepEqual(sets.get('text_standard')?.operator_ids, ['contains', 'not_contains', 'equals', 'not_equals', 'blank', 'not_blank']);
  assert.ok(sets.get('numeric_standard')?.operator_ids.includes('gte'));
  assert.ok(sets.get('numeric_standard')?.operator_ids.includes('lte'));
  assert.ok(sets.get('date_standard')?.operator_ids.includes('between'));
});

test('Validation Type value families and Field type fallbacks resolve to registered operator sets', () => {
  const registry = readJson(registryPath);
  const validationRegistry = readJson(validationRegistryPath);
  const setIds = new Set(registry.operator_sets.map((item) => item.id));
  const familyMappings = new Map(registry.validation_value_family_mappings.map((item) => [item.value_family, item.operator_set_id]));
  const fallbackMappings = new Map(registry.field_type_fallbacks.map((item) => [item.field_type, item.operator_set_id]));

  for (const definition of validationRegistry.validation_type_definitions) {
    assert.ok(familyMappings.has(definition.value_family), `missing search mapping for validation value_family ${definition.value_family}`);
    assert.ok(setIds.has(familyMappings.get(definition.value_family)));
  }
  for (const fieldType of ['text', 'textarea', 'number', 'boolean', 'date', 'datetime', 'select']) {
    assert.ok(fallbackMappings.has(fieldType), `missing field type fallback ${fieldType}`);
    assert.ok(setIds.has(fallbackMappings.get(fieldType)));
  }
});

test('multi-select vocabulary is reserved for the near future without becoming an active v1 operator', () => {
  const registry = readJson(registryPath);
  const active = new Set(registry.operators.filter((item) => item.status === 'active').map((item) => item.id));
  const planned = new Set(registry.future_operator_reservations.map((item) => item.id));
  assert.equal(active.has('in'), false);
  assert.equal(active.has('not_in'), false);
  assert.ok(planned.has('in'));
  assert.ok(planned.has('not_in'));
  assert.match(registry.contract.future_multi_select_policy, /values\[\]/);
});

test('ViewDef search schema validates override shape while registry remains the vocabulary source', () => {
  const schema = readJson(schemaPath);
  const search = schema.$defs.searchOptions;
  assert.equal(search.properties.visible.type, 'boolean');
  assert.equal(search.properties.operator.type, 'string');
  assert.equal(Object.hasOwn(search.properties.operator, 'enum'), false);
  assert.equal(search.properties.operator_set.type, 'string');
  assert.equal(search.properties.operators.type, 'array');
  assert.equal(search.properties.operators.uniqueItems, true);
  assert.match(search.description, /Registry/);
});


test('Schema Review mirrors the new search override shape and does not retain the old operator enum', () => {
  const review = readJson(schemaReviewPath);
  const searchDef = review.schema_items.find((item) => item.item_id === 'def__searchOptions');
  const operator = review.schema_items.find((item) => item.item_id === 'defprop__searchOptions__operator');
  const operatorSet = review.schema_items.find((item) => item.item_id === 'defprop__searchOptions__operator_set');
  const operators = review.schema_items.find((item) => item.item_id === 'defprop__searchOptions__operators');
  assert.ok(searchDef && operator && operatorSet && operators);
  assert.equal(operator.enum_summary, '');
  assert.doesNotMatch(operator.raw_schema_json, /\"enum\"/);
  assert.match(searchDef.raw_schema_json, /operator_set/);
  assert.match(searchDef.raw_schema_json, /operators/);
  assert.equal(review.schema_items_count, review.schema_items.length);
});

test('ViewDef generation rules use search.visible as the standard form and define Search Projection / legacy compatibility', () => {
  const rules = readJson(rulesPath);
  const fieldRule = rules.rules.find((item) => item.rule_id === 'viewdef_rule_05');
  const searchRule = rules.rules.find((item) => item.rule_id === 'viewdef_rule_36');
  assert.ok(fieldRule);
  assert.match(fieldRule.body, /"search": \{ "visible": true \}/);
  assert.doesNotMatch(fieldRule.body, /"search": \{ "visible": true, "operator": "contains" \}/);
  assert.equal(fieldRule.approval_decision, '未承認');
  assert.ok(searchRule);
  assert.equal(searchRule.approval_decision, '未承認');
  assert.match(searchRule.body, /Canonical Field Definition/);
  assert.match(searchRule.body, /SearchOperatorRegistry/);
  assert.match(searchRule.body, /右クリックメニューは原則1階層/);
  assert.match(searchRule.body, /選択肢メンテナンス/);
  assert.match(searchRule.body, /既存Search Sectionは即削除しない/);
  assert.equal(rules.rule_count, rules.rules.length);
});

test('studio_work_0186 records Phase 1 completion and keeps runtime/UI work as explicit follow-ups', () => {
  const incident = readJson(incidentPath);
  const item = incident.work_items.find((work) => work.work_item_id === 'studio_work_0186');
  assert.ok(item);
  assert.equal(item.phase, 'v0.18.64-standard-search-contract-phase1');
  assert.equal(item.status, '完了');
  assert.equal(item.follow_up_status, 'PENDING');
  assert.ok(item.follow_up_actions.some((action) => action.action_type === 'SEARCH_CAPABILITY_RESOLVER' && action.related_ids?.includes('studio_work_0187')));
  assert.ok(item.follow_up_actions.some((action) => action.action_type === 'SEARCH_UI_CONTEXT_MENU' && action.status === 'COMPLETED'));
  assert.ok(item.follow_up_actions.some((action) => action.action_type === 'VIEWDEF_SEARCH_STANDARDIZATION' && action.status === 'COMPLETED'));
  assert.ok(item.follow_up_actions.some((action) => action.action_type === 'DEFINITION_DRIVEN_SEARCH_TEST' && action.status === 'PENDING'));
});
