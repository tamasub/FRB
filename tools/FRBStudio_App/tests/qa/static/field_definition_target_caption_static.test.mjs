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
  assert.equal(component.placement, 'detailHeader');
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


test('Field Definition Grid exposes target ViewDef caption as the leftmost non-persistent derived column', () => {
  const section = fieldDefEditor.views
    .flatMap(view => view.sections ?? [])
    .find(item => item.id === 'field_definitions');
  const first = section?.fields?.[0];
  assert.equal(first?.field, '__target_caption');
  assert.equal(first?.caption, '項目名（Caption）');
  assert.equal(first?.readonly, true);
  assert.equal(first?.grid?.visible, true);
  assert.equal(first?.edit?.visible, false);
  assert.equal(first?.create?.include, false);
  assert.equal(first?.derived?.type, 'definition_target_caption');
  assert.equal(first?.derived?.sourceField, 'field_path');
  assert.equal(first?.derived?.targetViewDefPath, 'frb/frb_fft_field_definition_sample_view_def_v0_1.json');
});

test('derived target caption getter follows field_path changes and never persists into Field Definition JSON', async () => {
  const componentSource = read('wwwroot/js/components/definition/definition_target_caption_component.js');
  const data = readJson('fielddefs/samples/frb_fft_measurement_field_definitions_v0_2.json');
  const target = readJson('defs/frb/frb_fft_field_definition_sample_view_def_v0_1.json');

  const getByPath = (obj, pathValue) => {
    const raw = String(pathValue ?? '').replace(/^\$\.?/, '');
    if (!raw) return obj;
    return raw.split('.').reduce((cur, part) => cur == null ? undefined : cur[part], obj);
  };
  const localSandbox = {
    globalThis: {},
    EditorComponent: class {},
    registerEditorComponent: () => {},
    getByPath,
    resolveFieldDefinitionTargetViewField: sandbox.resolveFieldDefinitionTargetViewField,
    fetchApiJsonWithUrl: async (kind, name) => ({ json: target, url: `/api/${kind}/${name}` }),
    console
  };
  localSandbox.globalThis = localSandbox;
  vm.createContext(localSandbox);
  vm.runInContext(componentSource, localSandbox);

  await localSandbox.materializeDefinitionTargetCaptionDerivedProperties(fieldDefEditor, data);
  const row = data.field_definitions.find(item => item.field_path === '$.measurement_sessions[].measurement_name');
  assert.equal(row.__target_caption, '測定名');
  assert.equal(Object.prototype.propertyIsEnumerable.call(row, '__target_caption'), false);
  assert.equal(JSON.stringify(row).includes('__target_caption'), false);

  row.field_path = '$.analysis_start_date';
  assert.equal(row.__target_caption, '分析開始日');
});


test('malformed derived caption may not overwrite its own source field or recurse', async () => {
  const componentSource = read('wwwroot/js/components/definition/definition_target_caption_component.js');
  const target = readJson('defs/frb/frb_fft_field_definition_sample_view_def_v0_1.json');
  const malformed = structuredClone(fieldDefEditor);
  const section = malformed.views
    .flatMap(view => view.sections ?? [])
    .find(item => item.id === 'field_definitions');
  const derived = section.fields.find(field => field.derived?.type === 'definition_target_caption');
  derived.field = 'field_path';
  derived.derived.sourceField = 'field_path';

  const data = { field_definitions: [{ field_path: '$.analysis_start_date' }] };
  const getByPath = (obj, pathValue) => {
    const raw = String(pathValue ?? '').replace(/^\$\.?/, '');
    if (!raw) return obj;
    return raw.split('.').reduce((cur, part) => cur == null ? undefined : cur[part], obj);
  };
  const warnings = [];
  const localSandbox = {
    globalThis: {},
    EditorComponent: class {},
    registerEditorComponent: () => {},
    getByPath,
    resolveFieldDefinitionTargetViewField: sandbox.resolveFieldDefinitionTargetViewField,
    fetchApiJsonWithUrl: async () => ({ json: target }),
    console: { ...console, warn: (...args) => warnings.push(args.join(' ')) }
  };
  localSandbox.globalThis = localSandbox;
  vm.createContext(localSandbox);
  vm.runInContext(componentSource, localSandbox);

  await localSandbox.materializeDefinitionTargetCaptionDerivedProperties(malformed, data);
  assert.equal(data.field_definitions[0].field_path, '$.analysis_start_date');
  assert.ok(warnings.some(message => message.includes('self-recursive')));
});

test('overwrite save never applies stale hidden detail form after ViewDef row-order changes', () => {
  const source = read('wwwroot/js/runtime/detail_save.js');
  assert.match(source, /const detailDialogOpen = Boolean\(\$\('detailDialog'\)\?\.open\);/);
  assert.match(
    source,
    /detailMode === 'edit' && selectedIndex >= 0 && detailDialogOpen/
  );
});


test('Detail dialog exposes a dedicated detailHeader Editor Component slot', () => {
  const html = read('wwwroot/index.html');
  assert.match(
    html,
    /id="detailComponentHeaderArea"[^>]*data-editor-component-slot="detailHeader"/
  );
});

test('Detail runtime maps detailHeader placement to the sticky header slot', () => {
  const source = read('wwwroot/js/runtime/detail_save.js');
  assert.match(source, /detailHeader:\s*\$\('detailComponentHeaderArea'\)/);
  assert.match(source, /cached\?\.detailHeader\?\.isConnected/);
});

test('target Caption component is rendered compactly when mounted in the detail header', () => {
  const css = read('wwwroot/styles.css');
  assert.match(css, /v0\.18\.59-field-definition-caption-in-detail-header/);
  assert.match(
    css,
    /#detailDialog \.detail-header-component-slot \.definition-target-caption-card\s*\{/s
  );
  assert.match(css, /background:\s*transparent;/);
});
