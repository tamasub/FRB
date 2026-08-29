import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';

const ROOT = process.cwd();
const readJson = rel => JSON.parse(fs.readFileSync(path.join(ROOT, rel), 'utf8'));

test('Guarantee keeps only responsibility-level promise fields; ExpectedDef/TestPattern seed stay below Guarantee', () => {
  const document = readJson('data/json/03_tests/responsibilities/responsibility_data_v0_2.json');
  for (const responsibility of document.responsibilities ?? []) {
    for (const guarantee of responsibility.guarantees ?? []) {
      assert.equal(Object.hasOwn(guarantee, 'expected_def_type'), false, `${responsibility.responsibility_cd}/${guarantee.guarantee_id}`);
      assert.equal(Object.hasOwn(guarantee, 'test_pattern_seed'), false, `${responsibility.responsibility_cd}/${guarantee.guarantee_id}`);
    }
  }
});

test('Each TestPattern definition belongs to exactly one existing Guarantee ID', () => {
  const document = readJson('data/json/03_tests/responsibilities/responsibility_data_v0_2.json');
  for (const responsibility of document.responsibilities ?? []) {
    const guaranteeIds = new Set((responsibility.guarantees ?? []).map(item => item.guarantee_id));
    for (const pattern of responsibility.test_pattern_definitions ?? []) {
      assert.equal(typeof pattern.guarantee_id, 'string', `${responsibility.responsibility_cd}/${pattern.pattern_def_id}`);
      assert.ok(pattern.guarantee_id.length > 0, `${responsibility.responsibility_cd}/${pattern.pattern_def_id}`);
      assert.equal(Array.isArray(pattern.guarantee_ids), false, `${responsibility.responsibility_cd}/${pattern.pattern_def_id}`);
      assert.ok(guaranteeIds.has(pattern.guarantee_id), `${responsibility.responsibility_cd}/${pattern.pattern_def_id} -> ${pattern.guarantee_id}`);
    }
  }
});

test('SEARCH_FILTER uses one Guarantee ID that owns all current generator definitions', () => {
  const document = readJson('data/json/03_tests/responsibilities/responsibility_data_v0_2.json');
  const responsibility = document.responsibilities.find(item => item.responsibility_cd === 'search_filter');
  assert.ok(responsibility);
  assert.deepEqual(responsibility.guarantees.map(item => item.guarantee_id), ['search_filter_g001']);
  assert.ok(responsibility.test_pattern_definitions.length > 0);
  assert.ok(responsibility.test_pattern_definitions.every(item => item.guarantee_id === 'search_filter_g001'));
});

test('Responsibility ViewDef no longer exposes obsolete Guarantee-level ExpectedDef/TestPattern candidate columns', () => {
  const viewDef = readJson('defs/qa/tests/responsibilities/responsibility_view_def_v0_2.json');
  const section = viewDef.views.flatMap(view => view.sections ?? []).find(item => item.id === 'responsibilities');
  const guaranteeGrid = section.fields.find(item => item.field === 'guarantees').edit.subGrid;
  const fields = guaranteeGrid.columns.map(item => item.field);
  assert.equal(fields.includes('expected_def_type'), false);
  assert.equal(fields.includes('test_pattern_seed'), false);
  assert.equal(Object.hasOwn(guaranteeGrid.defaultItem, 'expected_def_type'), false);
  assert.equal(Object.hasOwn(guaranteeGrid.defaultItem, 'test_pattern_seed'), false);
});
