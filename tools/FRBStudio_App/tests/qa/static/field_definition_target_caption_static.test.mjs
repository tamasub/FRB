import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import { fileURLToPath } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(here, '../../..');

function read(rel) {
  return fs.readFileSync(path.join(root, rel), 'utf8');
}
function readJson(rel) {
  return JSON.parse(read(rel));
}

const resolverSource = read('wwwroot/js/services/definition/field_definition_target_view_resolver.js');
const sandbox = { globalThis: {} };
sandbox.globalThis = sandbox;
vm.createContext(sandbox);
vm.runInContext(resolverSource, sandbox);

const targetViewDef = readJson('defs/frb/frb_fft_field_definition_sample_view_def_v0_1.json');
const fieldDefEditor = readJson('defs/fielddefs/frb_fft_measurement_field_definitions_view_def_v0_1.json');

test('target ViewDef caption resolver maps canonical Field Definition path to human caption', () => {
  const resolved = sandbox.resolveFieldDefinitionTargetViewField(
    targetViewDef,
    '$.measurement_sessions[].measurement_name'
  );
  assert.equal(resolved?.caption, '測定名');
  assert.equal(resolved?.section_caption, 'FFT測定セッション');
});

test('date field caption resolves from the same target Data ViewDef', () => {
  const resolved = sandbox.resolveFieldDefinitionTargetViewField(
    targetViewDef,
    '$.measurement_sessions[].measurement_date'
  );
  assert.equal(resolved?.caption, '測定日');
});

test('Field Definition Editor declares target caption as a readonly Editor Component', () => {
  const section = fieldDefEditor.views
    .flatMap(view => view.sections ?? [])
    .find(item => item.id === 'field_definitions');
  const component = section?.editorComponents?.find(item => item.id === 'field_definition_target_caption');
  assert.ok(component);
  assert.equal(component.type, 'definition_target_caption');
  assert.equal(component.placement, 'detailBody');
  assert.equal(component.readonly, true);
  assert.equal(component.config.targetViewDefPath, 'frb/frb_fft_field_definition_sample_view_def_v0_1.json');
});



test('root cross-field date captions resolve from the target Data ViewDef', () => {
  const start = sandbox.resolveFieldDefinitionTargetViewField(targetViewDef, '$.analysis_start_date');
  const end = sandbox.resolveFieldDefinitionTargetViewField(targetViewDef, '$.analysis_end_date');
  assert.equal(start?.caption, '分析開始日');
  assert.equal(end?.caption, '分析終了日');
  assert.equal(start?.section_id, 'header');
  assert.equal(end?.section_id, 'header');
});

test('Field Definition Editor does not persist target Data field names as its own row properties', () => {
  const section = fieldDefEditor.views
    .flatMap(view => view.sections ?? [])
    .find(item => item.id === 'field_definitions');
  const names = new Set((section?.fields ?? []).map(field => field.field));
  assert.equal(names.has('analysis_start_date'), false);
  assert.equal(names.has('analysis_end_date'), false);
});

test('detail header spacing keeps first field labels below the sticky header', () => {
  const css = read('wwwroot/styles.css');
  assert.match(css, /v0\.18\.48-field-definition-caption-and-detail-header-spacing/);
  assert.match(css, /#detailDialog \.dialog-title-row\s*\{\s*margin-bottom:\s*14px;/s);
  assert.match(css, /#detailDialog #detailForm\s*\{\s*padding-top:\s*2px;/s);
});
