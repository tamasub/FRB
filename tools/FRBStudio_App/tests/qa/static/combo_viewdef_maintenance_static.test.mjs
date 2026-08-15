import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import test from 'node:test';
import vm from 'node:vm';

const root = process.cwd();
const text = (p) => fs.readFileSync(path.join(root, p), 'utf8');
const json = (p) => JSON.parse(text(p));

test('ViewDef maintenance adds only the quiet ellipsis entry and preserves existing load/folder responsibilities', () => {
  const index = text('wwwroot/index.html');
  const pageSetup = text('wwwroot/js/ui/page_setup.js');
  const app = text('wwwroot/app.js');

  assert.match(index, /id="maintainViewDefBtn"[^>]*>…<\/button>/);
  assert.match(index, /id="openDefFolderBtn"[^>]*>📁<\/button>/);
  assert.match(index, /id="loadBtn" class="primary-button">読み込み<\/button>/);
  assert.match(pageSetup, /VIEWDEF_MAINTENANCE_VIEWDEF_PATH = 'common\/view_def_maint_fields_v0_2\.json'/);
  assert.match(pageSetup, /loadFromObjects\([\s\S]*'viewdef'[\s\S]*\)/);
  assert.match(app, /setupViewDefMaintenanceButton\(\)/);
  assert.match(index, /js\/services\/viewdef_maintenance_projection\.js\?v=viewdef-row-order-01857/);
  assert.match(pageSetup, /buildViewDefMaintenanceDocument\(target\.json\)/);
  assert.match(pageSetup, /configureViewDefMaintenanceViewDef\(maintenance\.json, target\.json\)/);
  assert.match(pageSetup, /viewDefMaintenancePreferredDefaultSectionRef/);
  assert.match(pageSetup, /__maintenance_section_ref: maintenanceDefaultSectionRef/);
  assert.match(pageSetup, /applyStudioSearchState\([\s\S]*runSearch: true/);
});

test('ViewDef maintenance reuses one common ViewDef and saves the edited ViewDef through /api/defs without injecting view_def', () => {
  const maint = json('defs/common/view_def_maint_fields_v0_2.json');
  const program = text('Program.cs/Program.cs');
  const state = text('wwwroot/js/core/state.js');
  const save = text('wwwroot/js/runtime/detail_save.js');
  const runtime = text('wwwroot/js/runtime/load_runtime.js');

  assert.equal(maint.views?.[0]?.id, 'view_def_fields_maint');
  assert.equal(maint.views?.[0]?.sections?.[1]?.dataPath, '$.__studio_viewdef_maintenance_fields');
  assert.equal(maint.views?.[0]?.sections?.[0]?.fields?.some(field => field.field === 'views.0.layout'), false);
  assert.ok(maint.views?.[0]?.sections?.[1]?.fields?.find(field => field.field === 'type')?.options?.includes('date'));
  assert.match(program, /MapPost\("\/api\/defs\/\{\*\*name\}"/);
  assert.match(state, /currentDataSourceKind = 'data'/);
  assert.match(runtime, /dataSourceKind='data'/);
  assert.match(save, /if \(currentDataSourceKind !== 'viewdef'\)[\s\S]*ensureViewDefNameInData/);
  assert.match(save, /finalizeViewDefMaintenanceDocument\(sourceData\)/);
});

test('all standard select render paths bind the shared right-click option maintenance behavior', () => {
  const fieldControls = text('wwwroot/js/renderers/field_controls.js');
  const gridDetail = text('wwwroot/js/renderers/grid_detail.js');
  const subgrid = text('wwwroot/js/runtime/detail_subgrid_edit.js');
  const service = text('wwwroot/js/services/option_maintenance_service.js');
  const index = text('wwwroot/index.html');

  assert.match(fieldControls, /bindComboOptionMaintenance\(input, field\)/);
  assert.match(gridDetail, /bindComboOptionMaintenance\(input, field\)/);
  assert.match(subgrid, /bindComboOptionMaintenance\(input, column\)/);
  assert.match(service, /addEventListener\('contextmenu'/);
  assert.match(service, /source_type === 'viewDefOptions'/);
  assert.match(service, /source_type === 'fieldType'/);
  assert.match(service, /source_type === 'valueVocabulary'/);
  assert.match(index, /js\/services\/option_maintenance_service\.js\?v=combo-option-maintenance-01854/);
});

test('option source resolution keeps canonical source ownership and deprecates registry values instead of orphaning existing data', () => {
  const fieldTypes = text('wwwroot/js/core/field_types.js');
  const service = text('wwwroot/js/services/option_maintenance_service.js');

  assert.match(fieldTypes, /annotateFieldTypeRegistrySource/);
  assert.match(fieldTypes, /annotateEnumRegistrySource/);
  assert.match(fieldTypes, /_option_maintenance_source/);
  assert.match(fieldTypes, /override\?\._option_maintenance_source/);
  assert.match(fieldTypes, /_option_maintenance_source\.node_path = definitionPath/);
  assert.match(service, /findViewDefOptionsNode\(documentJson,[^;]+source\.node_path\)/);
  assert.match(fieldTypes, /filter\(item => item\?\.deprecated !== true\)/);
  assert.match(service, /raw\.deprecated = !item\.deprecated/);
  assert.match(service, /deprecated=true（無効化）/);
});


test('one ViewDef maintenance projection covers every view/section and round-trips fields to canonical ownership', () => {
  const source = text('wwwroot/js/services/viewdef_maintenance_projection.js');
  const sandbox = { globalThis: {} };
  sandbox.globalThis = sandbox;
  vm.createContext(sandbox);
  vm.runInContext(source, sandbox);

  const target = json('defs/frb/frb_fft_field_definition_sample_view_def_v0_1.json');
  const maint = json('defs/common/view_def_maint_fields_v0_2.json');
  const projected = sandbox.buildViewDefMaintenanceDocument(target);
  const configured = sandbox.configureViewDefMaintenanceViewDef(maint, target);
  const rows = projected.__studio_viewdef_maintenance_fields;

  const canonicalCount = target.views.reduce(
    (sum, view) => sum + (view.sections ?? []).reduce((sectionSum, section) => sectionSum + (section.fields?.length ?? 0), 0),
    0
  );
  assert.equal(rows.length, canonicalCount);
  assert.ok(rows.some(row => row.field === 'analysis_start_date' && row.__maintenance_section_ref === '0:0'));
  assert.ok(rows.some(row => row.field === 'measurement_name' && row.__maintenance_section_ref === '0:1'));
  assert.ok(rows.some(row => row.field === 'threshold_id' && row.__maintenance_section_ref === '1:0'));

  const sectionSelector = configured.views[0].sections[1].fields.find(field => field.field === '__maintenance_section_ref');
  assert.ok(sectionSelector.options.length >= 3);
  assert.equal(sectionSelector.grid.visible, false);
  assert.equal(sectionSelector.search.visible, true);
  assert.equal(sectionSelector.defaultValue, '0:1');
  assert.equal(sandbox.viewDefMaintenancePreferredDefaultSectionRef(sandbox.viewDefMaintenanceSectionCatalog(target)), '0:1');
  assert.equal(configured.views[0].sections[1].keyField, '__maintenance_key');

  rows.push({
    __maintenance_section_ref: '0:0',
    __maintenance_key: 'new-row',
    field: 'projection_round_trip_sample',
    caption: 'Projection Round Trip',
    type: 'text',
    grid: { visible: false },
    edit: { visible: true, readonly: false }
  });
  const finalized = sandbox.finalizeViewDefMaintenanceDocument(projected);
  const header = finalized.views[0].sections[0];
  assert.ok(header.fields.some(field => field.field === 'projection_round_trip_sample'));
  assert.equal(finalized.__studio_viewdef_maintenance_fields, undefined);
  assert.equal(finalized.__studio_viewdef_maintenance, undefined);
  assert.ok(header.fields.every(field => !('__maintenance_section_ref' in field) && !('__maintenance_key' in field)));
});


test('ViewDef maintenance initial section is the first main grid, so captions match the normal screen first', () => {
  const source = text('wwwroot/js/services/viewdef_maintenance_projection.js');
  const sandbox = { globalThis: {} };
  sandbox.globalThis = sandbox;
  vm.createContext(sandbox);
  vm.runInContext(source, sandbox);

  const target = json('defs/fielddefs/frb_fft_measurement_field_definitions_view_def_v0_1.json');
  const catalog = sandbox.viewDefMaintenanceSectionCatalog(target);
  const selected = sandbox.viewDefMaintenancePreferredDefaultSectionRef(catalog);
  assert.equal(selected, '0:1');

  const projected = sandbox.buildViewDefMaintenanceDocument(target).__studio_viewdef_maintenance_fields
    .filter(row => row.__maintenance_section_ref === selected);
  const captions = projected.map(row => row.caption);
  assert.deepEqual(Array.from(captions), ['項目名（Caption）', 'Field Path', 'Validation Type', 'Required', 'Nullable', 'Constraint Overrides', 'Note']);
});

test('ViewDef maintenance does not rewrite object layout as [object Object]', () => {
  const fieldDefEditor = json('defs/fielddefs/frb_fft_measurement_field_definitions_view_def_v0_1.json');
  assert.deepEqual(fieldDefEditor.views[0].layout, { detailDialog: 'wide' });
});


test('ViewDef maintenance supports one-row up/down movement only inside the same Section and finalize preserves order', () => {
  const source = text('wwwroot/js/services/viewdef_maintenance_projection.js');
  const sandbox = { globalThis: {} };
  sandbox.globalThis = sandbox;
  vm.createContext(sandbox);
  vm.runInContext(source, sandbox);

  const target = json('defs/fielddefs/frb_fft_measurement_field_definitions_view_def_v0_1.json');
  const projected = sandbox.buildViewDefMaintenanceDocument(target);
  const rows = projected.__studio_viewdef_maintenance_fields;
  const sectionRef = '0:1';
  const sectionRows = rows.filter(row => row.__maintenance_section_ref === sectionRef);
  const validationTypeRow = sectionRows.find(row => row.field === 'validation_type');
  assert.ok(validationTypeRow);

  const before = sectionRows.map(row => row.field);
  const originalPos = before.indexOf('validation_type');
  assert.ok(originalPos > 0);

  const moved = sandbox.moveViewDefMaintenanceProjectionRow(projected, validationTypeRow.__maintenance_key, -1);
  assert.equal(moved.moved, true);

  const after = projected.__studio_viewdef_maintenance_fields
    .filter(row => row.__maintenance_section_ref === sectionRef)
    .map(row => row.field);
  assert.equal(after.indexOf('validation_type'), originalPos - 1);

  const finalized = sandbox.finalizeViewDefMaintenanceDocument(projected);
  const canonical = finalized.views[0].sections[1].fields.map(field => field.field);
  assert.deepEqual(Array.from(canonical), Array.from(after));

  const firstKey = projected.__studio_viewdef_maintenance_fields
    .filter(row => row.__maintenance_section_ref === sectionRef)[0].__maintenance_key;
  const boundary = sandbox.moveViewDefMaintenanceProjectionRow(projected, firstKey, -1);
  assert.equal(boundary.moved, false);
  assert.equal(boundary.reason, 'section_boundary');
});

test('ViewDef row-order buttons are visible only for maintenance documents and wire to one-row movement', () => {
  const index = text('wwwroot/index.html');
  const grid = text('wwwroot/js/renderers/grid_detail.js');
  const pageSetup = text('wwwroot/js/ui/page_setup.js');

  assert.match(index, /id="viewDefMoveUpBtn"[^>]*class="ghost-button small hidden"[^>]*>↑ 上へ<\/button>/);
  assert.match(index, /id="viewDefMoveDownBtn"[^>]*class="ghost-button small hidden"[^>]*>↓ 下へ<\/button>/);
  assert.match(grid, /isViewDefMaintenanceDocument\(sourceData\)/);
  assert.match(grid, /moveViewDefMaintenanceProjectionRow\(sourceData, rowKey, Number\(delta\)\)/);
  assert.match(grid, /ソート中はViewDefの並び順を変更できません/);
  assert.match(pageSetup, /viewDefMoveUpBtn[\s\S]*moveSelectedViewDefMaintenanceRow\(-1\)/);
  assert.match(pageSetup, /viewDefMoveDownBtn[\s\S]*moveSelectedViewDefMaintenanceRow\(1\)/);
});
