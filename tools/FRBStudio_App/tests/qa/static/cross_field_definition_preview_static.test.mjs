import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import test from 'node:test';

const root = process.cwd();
const readText = relativePath => fs.readFileSync(path.join(root, relativePath), 'utf8');
const readJson = relativePath => JSON.parse(readText(relativePath));

test('Cross Field Constraint View declares a readonly Derived Test Preview Component', () => {
  const viewDef = readJson('defs/fielddefs/frb_fft_measurement_field_definitions_view_def_v0_1.json');
  const view = viewDef.views.find(item => item.id === 'frb_fft_measurement_cross_field_constraints_v0_1');
  const section = view.sections.find(item => item.id === 'cross_field_constraints');
  const component = section.editorComponents.find(item => item.type === 'cross_field_test_preview');

  assert.ok(component);
  assert.equal(component.placement, 'afterChildGrids');
  assert.equal(component.readonly, true);
  assert.equal(component.config.registryDataPath, 'config/validation_type_registry_v0_1.json');
});

test('Cross Field Preview is capability-specific Component + shared Service and standard Detail Editor stays neutral', () => {
  const component = readText('wwwroot/js/components/definition/cross_field_test_preview_component.js');
  const service = readText('wwwroot/js/services/definition/cross_field_verification_service.js');
  const detail = readText('wwwroot/js/runtime/detail_save.js');

  assert.match(component, /extends DerivedSubGridComponent/);
  assert.match(component, /CrossFieldVerificationService/);
  assert.match(component, /registerEditorComponent\(\s*['"]cross_field_test_preview['"]/);
  assert.doesNotMatch(service, /\bdocument\b|querySelector|EditorComponent|SubGridComponent/);
  assert.doesNotMatch(detail, /cross_field_test_preview|CrossFieldVerificationService/);
});

test('index loads Cross Field Verification dependencies and Component before Detail Editor runtime', () => {
  const index = readText('wwwroot/index.html');
  const validator = index.indexOf('js/services/definition/definition_value_validator.js?v=definition-test-runner-crossfield-01845');
  const service = index.indexOf('js/services/definition/cross_field_verification_service.js?v=definition-test-runner-crossfield-01845');
  const component = index.indexOf('js/components/definition/cross_field_test_preview_component.js?v=definition-test-runner-crossfield-01845');
  const detail = index.indexOf('js/runtime/detail_save.js?v=field-definition-derived-preview-01843');

  assert.ok(validator >= 0);
  assert.ok(service > validator);
  assert.ok(component > service);
  assert.ok(detail > component);
});

test('Definition TestRunner wrapper captures canonical Expected/Actual/Diff evidence outside runtime folder', () => {
  const ps1 = readText('tools/test/TestRunner.ps1');
  assert.match(ps1, /--evidence-dir/);
  assert.match(ps1, /data\/json\/03_tests\/contracts\/definition_test_runner_frb_fft_v0_1/);
  assert.match(ps1, /tests\/\.runtime\/definition\/definition_test_runner\.result\.json/);
});
