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

test('GRID_COLUMN_BUILD keeps 5 Pattern Defs under one human approval Guarantee', () => {
  const document = readJson('data/json/03_tests/responsibilities/responsibility_data_v0_2.json');
  const responsibility = document.responsibilities.find(item => item.responsibility_cd === 'grid_column_build');
  assert.ok(responsibility);
  assert.equal(responsibility.guarantees.length, 1);
  assert.equal(responsibility.guarantees[0].guarantee_id, 'grid_column_build_g001');
  assert.equal(responsibility.test_setup.length, 1);
  assert.equal(responsibility.test_pattern_definitions.length, 5);
  assert.deepEqual(
    [...new Set(responsibility.test_pattern_definitions.map(item => item.guarantee_id))],
    ['grid_column_build_g001'],
  );
  assert.ok(responsibility.test_pattern_definitions.every(item => item.generation_mode === 'GRID_COLUMN_BUILD_CASE'));
});

test('GRID_COLUMN_BUILD Generated Preview derives 5 factual Expected cases', () => {
  const sandbox = loadServiceSandbox();
  const document = readJson('data/json/03_tests/responsibilities/responsibility_data_v0_2.json');
  const responsibility = document.responsibilities.find(item => item.responsibility_cd === 'grid_column_build');
  const inputData = readJson('data/json/80_frb/frb_grid_column_build_test_data_v0_1.json');
  const viewDef = readJson('defs/frb/frb_grid_column_build_test_view_def_v0_1.json');
  const service = new sandbox.ResponsibilityTestPreviewService();
  const result = JSON.parse(JSON.stringify(service.derive({ responsibility, rootDocument: document, inputData, viewDef })));

  assert.equal(result.status, 'READY');
  assert.equal(result.execution_ready, false, 'Preview is restored first; formal runner wiring is intentionally separate');
  assert.equal(result.summary.test_pattern_count, 5);
  assert.equal(result.summary.generated_case_count, 5);
  assert.equal(result.summary.issue_count, 0);

  const byId = Object.fromEntries(result.test_patterns.map(item => [item.pattern_id, item]));
  assert.deepEqual(byId.grid_column_build_visible_fields.generated_cases[0].expected.field_names, ['title', 'score']);
  assert.deepEqual(byId.grid_column_build_order_preserve.generated_cases[0].expected.field_names, ['score', 'title', 'note']);
  assert.deepEqual(byId.grid_column_build_empty_safe.generated_cases[0].expected.field_names, []);
  assert.deepEqual(byId.grid_column_build_include_policy.generated_cases[0].expected.field_names, ['id', 'score']);
  assert.equal(byId.grid_column_build_no_side_effect.generated_cases[0].expected.input_unchanged, true);
});

test('GRID_COLUMN_BUILD detail renderer is wired without requiring Field Definition Registry', () => {
  const component = readText('wwwroot/js/components/responsibility/responsibility_test_preview_component.js');
  assert.match(component, /GRID_COLUMN_BUILD_CASE/);
  assert.match(component, /① Fields入力状況/);
  assert.match(component, /② GridColumnBuilderへ投入/);
  assert.match(component, /③ Expected Result/);
  assert.match(component, /GRID_COLUMN_BUILD_SIMPLE_ORACLE/);
  assert.match(component, /mode !== 'GRID_COLUMN_BUILD_CASE'/);
});
