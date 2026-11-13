import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import test from 'node:test';

const root = process.cwd();
const readJson = (relativePath) => JSON.parse(fs.readFileSync(path.join(root, relativePath), 'utf8'));
const schemaPath = 'data/json/00_rules/frb_view_def_schema_v0_9.json';
const schemaReviewPath = 'data/json/00_rules/frb_view_def_schema_review_data_v0_1.json';
const incidentPath = 'data/json/01_main/_studio_work_incident_data_v2.json';

function validateSectionGroups(view) {
  const groups = Array.isArray(view?.sectionGroups) ? view.sectionGroups : [];
  const sectionIds = new Set((Array.isArray(view?.sections) ? view.sections : []).map((section) => section?.id).filter(Boolean));
  const groupIds = new Set();
  const errors = [];

  for (const group of groups) {
    if (!group || typeof group !== 'object') {
      errors.push('GROUP_NOT_OBJECT');
      continue;
    }
    if (groupIds.has(group.id)) errors.push(`DUPLICATE_GROUP_ID:${group.id}`);
    groupIds.add(group.id);

    const refs = Array.isArray(group.sectionIds) ? group.sectionIds : [];
    const seenRefs = new Set();
    for (const sectionId of refs) {
      if (seenRefs.has(sectionId)) errors.push(`DUPLICATE_SECTION_ID:${group.id}:${sectionId}`);
      seenRefs.add(sectionId);
      if (!sectionIds.has(sectionId)) errors.push(`UNKNOWN_SECTION_ID:${group.id}:${sectionId}`);
    }
  }
  return errors;
}

test('ViewDef Schema formalizes optional sectionGroups beside sections without changing the existing required contract', () => {
  const schema = readJson(schemaPath);
  const view = schema.$defs.view;
  const group = schema.$defs.sectionGroup;

  assert.ok(view.properties.sections);
  assert.ok(view.properties.sectionGroups);
  assert.equal(view.properties.sectionGroups.type, 'array');
  assert.equal(view.properties.sectionGroups.minItems, 1);
  assert.equal(view.properties.sectionGroups.items.$ref, '#/$defs/sectionGroup');
  assert.equal(view.required.includes('sectionGroups'), false);

  assert.equal(group.type, 'object');
  assert.deepEqual(group.required, ['id', 'caption', 'sectionIds']);
  assert.equal(group.properties.id.type, 'string');
  assert.equal(group.properties.caption.type, 'string');
  assert.equal(group.properties.sectionIds.type, 'array');
  assert.equal(group.properties.sectionIds.minItems, 1);
  assert.equal(group.properties.sectionIds.uniqueItems, true);
  assert.equal(group.properties.sectionIds.items.type, 'string');
  assert.equal(Object.hasOwn(group.properties, 'children'), false, 'Phase 1 must not prebuild recursive grouping');
});

test('sectionGroups contract rejects duplicate group IDs, duplicate sectionIds, and unknown Section references', () => {
  const invalid = {
    sections: [
      { id: 'a' },
      { id: 'b' }
    ],
    sectionGroups: [
      { id: 'main', caption: 'Main', sectionIds: ['a', 'a', 'missing'] },
      { id: 'main', caption: 'Duplicate', sectionIds: ['b'] }
    ]
  };
  assert.deepEqual(validateSectionGroups(invalid), [
    'DUPLICATE_SECTION_ID:main:a',
    'UNKNOWN_SECTION_ID:main:missing',
    'DUPLICATE_GROUP_ID:main'
  ]);
});

test('sectionGroups allows one Section in multiple groups and allows ungrouped Sections', () => {
  const valid = {
    sections: [
      { id: 'shared' },
      { id: 'only_a' },
      { id: 'only_b' },
      { id: 'hidden_internal' }
    ],
    sectionGroups: [
      { id: 'a', caption: 'A', sectionIds: ['shared', 'only_a'] },
      { id: 'b', caption: 'B', sectionIds: ['shared', 'only_b'] }
    ]
  };
  assert.deepEqual(validateSectionGroups(valid), []);
});

test('Schema Review mirrors sectionGroups / sectionGroup and keeps them human-reviewable', () => {
  const review = readJson(schemaReviewPath);
  const view = review.schema_items.find((item) => item.item_id === 'def__view');
  const viewGroups = review.schema_items.find((item) => item.item_id === 'defprop__view__sectionGroups');
  const group = review.schema_items.find((item) => item.item_id === 'def__sectionGroup');
  const groupId = review.schema_items.find((item) => item.item_id === 'defprop__sectionGroup__id');
  const caption = review.schema_items.find((item) => item.item_id === 'defprop__sectionGroup__caption');
  const refs = review.schema_items.find((item) => item.item_id === 'defprop__sectionGroup__sectionIds');

  assert.ok(view && viewGroups && group && groupId && caption && refs);
  assert.match(view.raw_schema_json, /sectionGroups/);
  assert.match(viewGroups.raw_schema_json, /sectionGroup/);
  assert.match(group.raw_schema_json, /sectionIds/);
  assert.equal(refs.required, true);
  assert.match(refs.raw_schema_json, /"uniqueItems": true/);
  assert.equal(review.schema_items_count, review.schema_items.length);
  assert.equal(review.defs_count, review.schema_items.filter((item) => item.item_type === 'definition').length);
  assert.equal(review.definition_property_count, review.schema_items.filter((item) => item.item_type === 'definition_property').length);
});

test('Phase 1 remains backward compatible because existing ViewDefs do not need sectionGroups added', () => {
  const schema = readJson(schemaPath);
  assert.equal(schema.$defs.view.required.includes('sectionGroups'), false);

  const defsRoot = path.join(root, 'defs');
  let viewDefCount = 0;
  for (const file of fs.readdirSync(defsRoot, { recursive: true, withFileTypes: true })) {
    if (!file.isFile() || !file.name.endsWith('.json')) continue;
    const parentPath = file.parentPath ?? file.path;
    const fullPath = path.join(parentPath, file.name);
    let data;
    try {
      data = JSON.parse(fs.readFileSync(fullPath, 'utf8'));
    } catch {
      continue;
    }
    if (!Array.isArray(data.views)) continue;
    viewDefCount += 1;
    for (const view of data.views) {
      assert.ok(Array.isArray(view.sections), `${path.relative(root, fullPath)} has no sections array`);
      // Existing files are allowed to omit sectionGroups entirely.
      if (view.sectionGroups !== undefined) assert.deepEqual(validateSectionGroups(view), []);
    }
  }
  assert.ok(viewDefCount > 0, 'expected existing ViewDefs to be discovered');
});

test('studio_work_0194-0198 are registered before Phase 1 completion and Phase 1 owns only the contract work', () => {
  const incident = readJson(incidentPath);
  const ids = ['studio_work_0194', 'studio_work_0195', 'studio_work_0196', 'studio_work_0197', 'studio_work_0198'];
  for (const id of ids) assert.ok(incident.work_items.some((item) => item.work_item_id === id), `${id} is not registered`);

  const phase1 = incident.work_items.find((item) => item.work_item_id === 'studio_work_0194');
  assert.equal(phase1.phase, 'v0.18.72-viewdef-section-groups-contract-phase1');
  assert.match(phase1.scope, /Schema Review Data/);
  assert.match(phase1.out_of_scope, /Group Navigation UI/);
  assert.ok(phase1.follow_up_actions.some((action) => action.related_ids?.includes('studio_work_0195')));
});
