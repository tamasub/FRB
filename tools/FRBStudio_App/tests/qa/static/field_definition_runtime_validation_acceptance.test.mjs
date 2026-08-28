import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const root = path.resolve(__dirname, '../../..');

const readText = relative => fs.readFileSync(path.join(root, relative), 'utf8');
const readJson = relative => JSON.parse(readText(relative));

const scripts = [
  'wwwroot/js/services/definition/definition_verification_common.js',
  'wwwroot/js/services/definition/field_contract_resolver.js',
  'wwwroot/js/services/definition/definition_value_validator.js',
  'wwwroot/js/services/definition/runtime_field_definition_validation.js',
  'wwwroot/js/runtime/detail_save.js'
];

function getByPath(obj, pathName) {
  const normalized = String(pathName ?? '').replace(/^\$\.?/, '');
  if (!normalized) return obj;
  return normalized.split('.').reduce((current, part) => current == null ? undefined : current[part], obj);
}

function setByPath(obj, pathName, value) {
  const normalized = String(pathName ?? '').replace(/^\$\.?/, '');
  const parts = normalized.split('.').filter(Boolean);
  let current = obj;
  for (let index = 0; index < parts.length - 1; index++) {
    if (!current[parts[index]] || typeof current[parts[index]] !== 'object') current[parts[index]] = {};
    current = current[parts[index]];
  }
  if (parts.length) current[parts.at(-1)] = value;
}

function measurementGridDef() {
  const viewDef = readJson('defs/frb/frb_fft_field_definition_sample_view_def_v0_1.json');
  for (const view of viewDef.views ?? []) {
    for (const section of view.sections ?? []) {
      if (section.dataPath === '$.measurement_sessions') return section;
    }
  }
  throw new Error('measurement_sessions section not found');
}

function createF12Runtime() {
  const grid = measurementGridDef();
  const fieldDefs = readJson('fielddefs/samples/frb_fft_measurement_field_definitions_v0_2.json');
  const registry = readJson('data/json/config/validation_type_registry_v0_1.json');

  const dialogRoot = {
    isConnected: true,
    querySelectorAll: () => [],
    querySelector: () => null,
    dataset: {},
    addEventListener() {}
  };
  const context = {
    console,
    globalThis: null,
    window: null,
    document: { querySelectorAll: () => [] },
    CSS: { escape: value => String(value) },
    detailMode: 'edit',
    selectedIndex: 0,
    draftRow: null,
    currentRows: [JSON.parse(JSON.stringify(
      readJson('data/json/80_frb/frb_fft_field_definition_sample_data_v0_1.json').measurement_sessions[0]
    ))],
    filteredRows: [],
    viewDef: {},
    sourceData: {},
    currentRuntimeFieldDefinitionDocument: fieldDefs,
    currentRuntimeValidationTypeRegistry: registry,
    currentRuntimeFieldDefinitionRef: 'samples/frb_fft_measurement_field_definitions_v0_2.json',
    uiField: 'measurement_date',
    uiValue: '2016-07-26',
    gridDef: () => grid,
    cloneData: value => value == null ? value : JSON.parse(JSON.stringify(value)),
    getByPath,
    setByPath,
    applyDetailInputsToRow: (row) => {
      setByPath(row, context.uiField, context.uiValue);
    },
    getStudioJsonRoundTripDraftRow: () => null,
    discardStudioJsonRoundTripDraft: () => {},
    markDetailSubGridEditsCommitted: () => { context.subgridCommitted = true; },
    renderGrid: () => { context.renderCount = (context.renderCount ?? 0) + 1; },
    updateDetailNavButtons: () => {},
    registerRenderer: () => {},
    setStatus: (message, options={}) => {
      context.lastStatus = message;
      context.lastStatusOptions = options;
    },
    showStudioConfirmDialog: options => {
      context.lastDialog = options;
      return Promise.resolve(true);
    },
    $: id => id === 'detailDialog' ? dialogRoot : null,
    EditorComponentHost: undefined,
    clearStudioJsonRoundTripDiff: () => {},
    setTimeout,
    structuredClone
  };
  context.window = context;
  context.globalThis = context;

  vm.createContext(context);
  for (const script of scripts) {
    vm.runInContext(readText(script), context, { filename: script });
  }
  // v0.18.46: successful F12 now performs a full Detail rebind after canonical commit.
  // This acceptance harness verifies the Runtime Validation/commit responsibility, not DOM rendering,
  // so replace the full renderer with a no-op while preserving the actual applyDetail -> rebind call path.
  vm.runInContext('renderDetailForRow = function () {};', context);
  return context;
}

test('Acceptance: 実Data Editorでminimum_date違反値をF12反映するとcanonical Dataを変更せず拒否する', () => {
  const runtime = createF12Runtime();
  const before = runtime.currentRows[0].measurement_date;

  runtime.applyDetail();

  assert.equal(before, '2026-07-26');
  assert.equal(runtime.currentRows[0].measurement_date, '2026-07-26', 'canonical Data must stay unchanged');
  assert.equal(runtime.uiValue, '2016-07-26', 'rejected input must remain editable in the Editor');
  assert.match(runtime.lastStatus, /F12反映を拒否/);
  assert.match(runtime.lastStatus, /Field Definition契約違反/);
  assert.match(runtime.lastDialog.detail, /measurement_date/);
  assert.match(runtime.lastDialog.detail, /2016-07-26/);
  assert.match(runtime.lastDialog.detail, /minimum_date/);
  assert.match(runtime.lastDialog.detail, /2020-01-01/);
  assert.equal(runtime.renderCount ?? 0, 0, 'rejection must not redraw away the invalid input');
});

test('Acceptance: 契約境界値へ修正して再度F12するとcanonical Dataへ反映できる', () => {
  const runtime = createF12Runtime();

  runtime.applyDetail();
  assert.equal(runtime.currentRows[0].measurement_date, '2026-07-26');

  runtime.uiValue = '2020-01-01';
  runtime.applyDetail();

  assert.equal(runtime.currentRows[0].measurement_date, '2020-01-01');
  assert.equal(runtime.renderCount, 1);
  assert.match(runtime.lastStatus, /詳細を反映しました/);
});


test('Acceptance: maximum_date超過値をF12反映するとcanonical Dataを変更せず拒否する', () => {
  const runtime = createF12Runtime();
  runtime.uiValue = '2100-01-01';

  runtime.applyDetail();

  assert.equal(runtime.currentRows[0].measurement_date, '2026-07-26');
  assert.match(runtime.lastDialog.detail, /maximum_date/);
  assert.match(runtime.lastDialog.detail, /2099-12-31/);
  assert.match(runtime.lastDialog.detail, /2100-01-01/);
});

test('Acceptance: instant契約へtimezone offsetなし値を入力するとF12反映を拒否する', () => {
  const runtime = createF12Runtime();
  const before = runtime.currentRows[0].received_at;
  runtime.uiField = 'received_at';
  runtime.uiValue = '2026-01-15T12:34:56';

  runtime.applyDetail();

  assert.equal(runtime.currentRows[0].received_at, before);
  assert.match(runtime.lastDialog.detail, /received_at/);
  assert.match(runtime.lastDialog.detail, /INSTANT_FORMAT_INVALID/);
});

test('Contract: F12 Runtime Validation uses the same FieldContractResolver / DefinitionValueValidator outcome', () => {
  const runtime = createF12Runtime();
  const service = new runtime.RuntimeFieldDefinitionValidationService();
  const staged = { ...runtime.currentRows[0], measurement_date: '2016-07-26' };
  const result = service.validateRow({
    row: staged,
    gridDef: runtime.gridDef(),
    fieldDefinitionDocument: runtime.currentRuntimeFieldDefinitionDocument,
    registry: runtime.currentRuntimeValidationTypeRegistry
  });

  assert.equal(result.status, 'REJECT');
  const check = result.blocking_checks.find(item => item.field_name === 'measurement_date');
  assert.ok(check);
  assert.equal(check.validation.reason_code, 'MINIMUM_BOUNDARY_VIOLATION');
  assert.equal(check.validation.outcome, 'REJECT');
});

test('Static connection: ViewDef item_definition_ref is loaded through fielddefs root before Editor use', () => {
  const loader = readText('wwwroot/js/runtime/load_runtime.js');
  const program = readText('Program.cs/Program.cs');
  assert.match(loader, /loadRuntimeFieldDefinitionContext\(defObj\)/);
  assert.match(loader, /\/api\/fielddefs\//);
  assert.match(program, /MapGet\("\/api\/fielddefs\/\{\*\*name\}"/);
});
