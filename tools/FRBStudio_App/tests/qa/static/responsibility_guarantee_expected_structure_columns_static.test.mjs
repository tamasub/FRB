import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';

const ROOT = process.cwd();
const readText = rel => fs.readFileSync(path.join(ROOT, rel), 'utf8');
const readJson = rel => JSON.parse(readText(rel));

function loadComponentSandbox() {
  const sandbox = {
    console, JSON, Object, Array, Map, Set, Number, String, Boolean, Math, RegExp,
    DerivedSubGridComponent: class {},
    registerEditorComponent() {}
  };
  sandbox.globalThis = sandbox;
  vm.createContext(sandbox);
  vm.runInContext(
    readText('wwwroot/js/components/responsibility/responsibility_test_preview_component.js'),
    sandbox,
    { filename: 'responsibility_test_preview_component.js' }
  );
  return sandbox;
}

test('Guarantee Definition structure_caption determines Generated Preview Expected Structure columns', () => {
  const sandbox = loadComponentSandbox();
  const document = readJson('data/json/03_tests/responsibilities/responsibility_data_v0_2.json');
  const registry = readJson('data/json/config/guarantee_definition_registry_v0_1.json');

  const search = document.responsibilities.find(item => item.responsibility_cd === 'search_filter');
  assert.deepEqual(
    JSON.parse(JSON.stringify(
      sandbox.responsibilityPreviewExpectedStructureDefinitions(search, registry)
        .map(item => item.structure_caption)
    )),
    ['Hit Structure']
  );

  const csv = document.responsibilities.find(item => item.responsibility_cd === 'csv_export');
  assert.deepEqual(
    JSON.parse(JSON.stringify(
      sandbox.responsibilityPreviewExpectedStructureDefinitions(csv, registry)
        .map(item => item.structure_caption)
    )),
    ['Row / Column Structure', 'Key Structure', 'CSV Format Structure']
  );

  const aggregate = document.responsibilities.find(item => item.responsibility_cd === 'grid_aggregate');
  assert.deepEqual(
    JSON.parse(JSON.stringify(
      sandbox.responsibilityPreviewExpectedStructureDefinitions(aggregate, registry)
        .map(item => item.structure_caption)
    )),
    ['Aggregate Structure']
  );
});

test('Expected fields are demoted into compact JSON string inside one Expected Structure cell', () => {
  const sandbox = loadComponentSandbox();
  const document = readJson('data/json/03_tests/responsibilities/responsibility_data_v0_2.json');
  const registry = readJson('data/json/config/guarantee_definition_registry_v0_1.json');
  const search = document.responsibilities.find(item => item.responsibility_cd === 'search_filter');
  const hit = sandbox.responsibilityPreviewExpectedStructureDefinitions(search, registry)[0];

  const pattern = {
    guarantee_id: 'search_filter_g001',
    structural_expected: [{
      structure_id: 'hit_structure',
      operator_id: 'contains',
      expected_hit_count: 3,
      expected_hit_indexes: [0, 2, 5]
    }]
  };

  assert.equal(
    sandbox.responsibilityPreviewExpectedStructureJson(pattern, hit),
    '{"expected_hit_count":3,"expected_hit_indexes":[0,2,5]}'
  );
});

test('Responsibility ViewDef explicitly references Guarantee Definition Registry', () => {
  const viewDef = readJson('defs/qa/tests/responsibilities/responsibility_view_def_v0_2.json');
  const section = viewDef.views.flatMap(view => view.sections ?? []).find(item => item.id === 'responsibilities');
  const component = section.editorComponents.find(item => item.id === 'responsibility_generated_test_preview');

  assert.equal(
    component.config.guaranteeDefinitionRegistryDataPath,
    'config/guarantee_definition_registry_v0_1.json'
  );
});
