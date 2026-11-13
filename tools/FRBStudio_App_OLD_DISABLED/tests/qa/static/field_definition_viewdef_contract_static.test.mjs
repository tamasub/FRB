import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import test from 'node:test';

const root = process.cwd();
const readJson = (relativePath) => JSON.parse(fs.readFileSync(path.join(root, relativePath), 'utf8'));

const dataPath = 'data/json/80_frb/frb_fft_field_definition_sample_data_v0_1.json';
const viewDefPath = 'defs/frb/frb_fft_field_definition_sample_view_def_v0_1.json';
const fieldDefPath = 'fielddefs/samples/frb_fft_measurement_field_definitions_v0_2.json';
const fieldDefSchemaPath = 'fielddefs/schema/field_definition_data_schema_v0_1.json';
const viewDefSchemaPath = 'data/json/00_rules/frb_view_def_schema_v0_9.json';
const schemaReviewPath = 'data/json/00_rules/frb_view_def_schema_review_data_v0_1.json';
const rulesPath = 'data/json/00_rules/frb_viewdef_generation_rules_data_v0_1.json';

function canonicalFieldPath(sectionDataPath, fieldName) {
  const base = String(sectionDataPath || '$').trim();
  const normalizedBase = base === '$'
    ? '$'
    : `${base.replace(/\[\]$/, '')}[]`;
  return normalizedBase === '$' ? `$.${fieldName}` : `${normalizedBase}.${fieldName}`;
}

function allViewDefFields(viewDef) {
  const fields = [];
  for (const view of viewDef.views || []) {
    for (const section of view.sections || []) {
      for (const field of section.fields || []) {
        fields.push({ view, section, field, fieldPath: canonicalFieldPath(section.dataPath, field.field) });
      }
    }
  }
  return fields;
}

test('sample Data points to the sample ViewDef and does not reference fielddefs directly', () => {
  const data = readJson(dataPath);
  assert.equal(data.view_def, 'frb/frb_fft_field_definition_sample_view_def_v0_1.json');
  assert.equal(Object.hasOwn(data, 'item_definition_ref'), false);
});

test('sample ViewDef references one fielddefs file only at the ViewDef root', () => {
  const viewDef = readJson(viewDefPath);
  assert.equal(viewDef.item_definition_ref, 'samples/frb_fft_measurement_field_definitions_v0_2.json');
  const fields = allViewDefFields(viewDef);
  assert.ok(fields.length > 0);
  for (const { field } of fields) {
    assert.equal(Object.hasOwn(field, 'item_definition_id'), false);
    assert.equal(Object.hasOwn(field, 'validation_type'), false);
  }
});

test('measurement sessions and acceptance thresholds stay in one ViewDef file as two views', () => {
  const viewDef = readJson(viewDefPath);
  assert.deepEqual(
    viewDef.views.map((view) => view.id),
    ['frb_fft_measurement_sessions_v0_1', 'frb_fft_acceptance_thresholds_v0_1']
  );
  const related = viewDef.views[0].toolbar.relatedGridViews[0];
  assert.equal(related.dataPath, '$.acceptance_thresholds');
  assert.equal(related.viewId, 'frb_fft_acceptance_thresholds_v0_1');
  assert.equal(related.shellMode, 'grid_only');
});

test('all explicit fielddefs paths resolve to ViewDef dataPath + field identities', () => {
  const viewDef = readJson(viewDefPath);
  const fieldDefs = readJson(fieldDefPath);
  const viewPaths = new Set(allViewDefFields(viewDef).map((entry) => entry.fieldPath));
  assert.equal(fieldDefs.field_definition_count, fieldDefs.field_definitions.length);
  for (const definition of fieldDefs.field_definitions) {
    assert.ok(viewPaths.has(definition.field_path), `missing ViewDef field for ${definition.field_path}`);
  }
  assert.ok(viewPaths.has('$.measurement_sessions[].peak_frequency_hz'));
  assert.ok(viewPaths.has('$.acceptance_thresholds[].peak_frequency_hz'));
});

test('fielddefs structural schema requires field_path and validation_type', () => {
  const schema = readJson(fieldDefSchemaPath);
  const fieldDefinition = schema.$defs.fieldDefinition;
  assert.deepEqual(fieldDefinition.required, ['field_path', 'validation_type']);
  assert.equal(fieldDefinition.additionalProperties, false);
  assert.equal(schema.properties.definition_policy.$ref, '#/$defs/definitionPolicy');
});

test('ViewDef Schema declares optional item_definition_ref and no field-level validation contract keys', () => {
  const schema = readJson(viewDefSchemaPath);
  assert.equal(schema.properties.item_definition_ref.type, 'string');
  assert.equal(schema.required.includes('item_definition_ref'), false);
  const fieldProperties = schema.$defs.field.properties;
  assert.equal(Object.hasOwn(fieldProperties, 'item_definition_id'), false);
  assert.equal(Object.hasOwn(fieldProperties, 'validation_type'), false);
});

test('Schema Review and ViewDef Generation Rules track the current approval states', () => {
  const review = readJson(schemaReviewPath);
  const reviewItem = review.schema_items.find((item) => item.item_id === 'root_property__item_definition_ref');
  assert.ok(reviewItem);
  assert.equal(reviewItem.approval_decision, '未承認');
  const rootReviewItems = review.schema_items.filter((item) => item.item_type === 'root_property');
  assert.equal(review.root_properties_count, rootReviewItems.length);
  assert.equal(review.root_properties_count, 20);
  assert.equal(review.schema_items_count, review.schema_items.length);

  const rules = readJson(rulesPath);
  const rule = rules.rules.find((item) => item.rule_id === 'viewdef_rule_33');
  assert.ok(rule);
  assert.equal(rule.approval_decision, '承認する');
  assert.match(rule.body, /item_definition_ref/);
  assert.match(rule.body, /validation_type.*item_definition_id/s);
  assert.equal(rules.rule_count, rules.rules.length);
});


test('date and datetime are separated in the sample, Schema, and Validation Type Registry', () => {
  const data = readJson(dataPath);
  const viewDef = readJson(viewDefPath);
  const fieldDefs = readJson(fieldDefPath);
  const schema = readJson(viewDefSchemaPath);
  const registry = readJson('data/json/config/validation_type_registry_v0_1.json');

  const first = data.measurement_sessions[0];
  assert.equal(first.measurement_date, '2026-07-26');
  assert.equal(first.captured_at, '2026-07-26T21:30');
  assert.equal(first.received_at, '2026-07-26T21:30:00+09:00');

  const fields = new Map(allViewDefFields(viewDef).map((entry) => [entry.fieldPath, entry.field]));
  assert.equal(fields.get('$.measurement_sessions[].measurement_date')?.type, 'date');
  assert.equal(fields.get('$.measurement_sessions[].captured_at')?.type, 'datetime');
  assert.equal(fields.get('$.measurement_sessions[].received_at')?.type, 'datetime');
  assert.equal(fields.get('$.created_at')?.type, 'date');
  assert.equal(fields.get('$.updated_at')?.type, 'date');

  const receivedDef = fieldDefs.field_definitions.find((item) => item.field_path === '$.measurement_sessions[].received_at');
  assert.equal(receivedDef?.validation_type, 'studio.instant.iso8601');
  assert.equal(fieldDefs.field_definition_count, 20);

  assert.ok(schema.$defs.fieldType.enum.includes('date'));
  const dateCatalog = registry.view_def_type_catalogs.find((item) => item.view_def_type === 'date');
  const datetimeCatalog = registry.view_def_type_catalogs.find((item) => item.view_def_type === 'datetime');
  assert.equal(dateCatalog?.default_validation_type_id, 'studio.date.ymd');
  assert.deepEqual(dateCatalog?.validation_type_ids, ['studio.date.ymd']);
  assert.equal(datetimeCatalog?.default_validation_type_id, 'studio.datetime.local');
  assert.equal(datetimeCatalog?.validation_type_ids.includes('studio.date.ymd'), false);
  assert.ok(datetimeCatalog?.validation_type_ids.includes('studio.instant.iso8601'));
  const standardNumber = registry.validation_type_definitions.find((item) => item.id === 'studio.number.standard');
  assert.equal(standardNumber?.status, 'active');
});

test('ViewDef generation rules define deepest datetime inference while preserving legacy compatibility', () => {
  const rules = readJson(rulesPath);
  const rule = rules.rules.find((item) => item.rule_id === 'viewdef_rule_34');
  assert.ok(rule);
  assert.equal(rule.approval_decision, '承認する');
  assert.match(rule.body, /2026-07-26\s+→ date/);
  assert.match(rule.body, /2026-07-26T21:30\s+→ datetime/);
  assert.match(rule.body, /2026-07-26T21:30:00\+09:00\s+→ datetime/);
  assert.match(rule.body, /混在.*datetime/s);
  assert.match(rule.body, /既存ViewDef.*互換/s);
  assert.equal(rules.rule_count, rules.rules.length);
});
