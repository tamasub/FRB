import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';

const ROOT = process.cwd();
const readText = rel => fs.readFileSync(path.join(ROOT, rel), 'utf8');
const readJson = rel => JSON.parse(readText(rel));

function loadServiceSandbox() {
  const sandbox = { console, structuredClone, Date, JSON, Object, Array, Map, Set, Number, String, Boolean, Math, RegExp };
  sandbox.globalThis = sandbox;
  vm.createContext(sandbox);
  vm.runInContext(readText('wwwroot/js/services/responsibility/responsibility_test_preview_service.js'), sandbox, {
    filename: 'wwwroot/js/services/responsibility/responsibility_test_preview_service.js'
  });
  return sandbox;
}

test('GRID_AGGREGATE uses one Guarantee ID that owns 5 standard TestPattern definitions', () => {
  const document = readJson('data/json/03_tests/responsibilities/responsibility_data_v0_2.json');
  const responsibility = document.responsibilities.find(item => item.responsibility_cd === 'grid_aggregate');
  assert.ok(responsibility);
  assert.deepEqual(responsibility.guarantees.map(item => item.guarantee_id), ['grid_aggregate_g001']);
  assert.equal(responsibility.test_pattern_definitions.length, 5);
  assert.ok(responsibility.test_pattern_definitions.every(item => item.guarantee_id === 'grid_aggregate_g001'));
  assert.ok(responsibility.test_pattern_definitions.every(item => item.generation_mode === 'AGGREGATE_SCALAR_CASE'));
});

test('GRID_AGGREGATE preview derives 5 TestPatterns / 9 Generated Cases with independent scalar Expected values', () => {
  const sandbox = loadServiceSandbox();
  const document = readJson('data/json/03_tests/responsibilities/responsibility_data_v0_2.json');
  const responsibility = document.responsibilities.find(item => item.responsibility_cd === 'grid_aggregate');
  const inputData = readJson('data/json/80_frb/frb_grid_aggregate_test_data_v0_1.json');
  const viewDef = readJson('defs/frb/frb_grid_aggregate_test_view_def_v0_1.json');

  const service = new sandbox.ResponsibilityTestPreviewService();
  const result = JSON.parse(JSON.stringify(service.derive({ responsibility, rootDocument: document, inputData, viewDef })));

  assert.equal(result.status, 'READY');
  assert.equal(result.execution_ready, true, 'approved Input is execution-ready');
  assert.equal(result.expected_def_type, 'ScalarExpectedDef');
  assert.equal(result.summary.test_pattern_count, 5);
  assert.equal(result.summary.generated_case_count, 9);
  assert.equal(result.summary.issue_count, 0);

  const byPattern = Object.fromEntries(result.test_patterns.map(pattern => [pattern.pattern_id, pattern]));
  const scalar = (patternId, metric) => byPattern[patternId].generated_cases.find(item => item.metric === metric).expected.value;

  assert.equal(scalar('grid_aggregate_sum_filtered', 'value'), 146);
  assert.equal(scalar('grid_aggregate_sum_filtered', 'source_count'), 3);
  assert.equal(scalar('grid_aggregate_sum_all', 'value'), 100);
  assert.equal(scalar('grid_aggregate_sum_all', 'source_count'), 4);
  assert.equal(scalar('grid_aggregate_comma_numeric', 'value'), 1244.5);
  assert.equal(scalar('grid_aggregate_invalid_exclusion', 'value'), 10);
  assert.equal(scalar('grid_aggregate_invalid_exclusion', 'valid_count'), 1);
  assert.equal(scalar('grid_aggregate_invalid_exclusion', 'ignored_count'), 3);
  assert.equal(scalar('grid_aggregate_no_declaration', 'has_aggregates'), false);
  assert.ok(result.test_patterns.every(pattern => pattern.expected_def_type === 'ScalarExpectedDef'));
});

test('ScalarExpectedDef is registered as one-value Expected FieldGroup and TestPattern option', () => {
  const config = readJson('defs/config/field_group_types_config_data_v0_1.json');
  const groups = config.namespaces.studio.fieldGroups;
  assert.equal(groups.ExpectedDef.dynamic.map.ScalarExpectedDef, 'studio.ScalarExpectedDef');
  assert.deepEqual(groups.ScalarExpectedDef.fields.map(item => item.field), ['expected.value']);

  const viewDef = readJson('defs/qa/tests/responsibilities/responsibility_view_def_v0_2.json');
  const section = viewDef.views.flatMap(view => view.sections ?? []).find(item => item.id === 'responsibilities');
  const patternGrid = section.fields.find(item => item.field === 'test_pattern_definitions').edit.subGrid;
  const expectedDef = patternGrid.columns.find(item => item.field === 'expected_def_type');
  assert.ok(expectedDef.options.includes('ScalarExpectedDef'));
});
