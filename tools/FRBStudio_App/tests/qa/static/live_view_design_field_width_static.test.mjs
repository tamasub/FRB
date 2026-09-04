// v0.18.132 Live View Design / Field.width
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';

const read = path => fs.readFileSync(path, 'utf8');

test('ViewDef schema exposes canonical Field.width and marks grid.width as legacy', () => {
  const schema = JSON.parse(read('data/json/00_rules/frb_view_def_schema_v0_9.json'));
  const fieldWidth = schema?.$defs?.field?.properties?.width;
  const gridWidth = schema?.$defs?.gridOptions?.properties?.width;
  assert.equal(fieldWidth?.type, 'number');
  assert.equal(fieldWidth?.minimum, 0);
  assert.match(String(fieldWidth?.description ?? ''), /Field共通|正本/);
  assert.match(String(gridWidth?.description ?? ''), /Legacy|互換/);
});

test('ViewDef maintenance exposes Field.width and makes legacy grid.width read-only', () => {
  const def = JSON.parse(read('defs/common/view_def_maint_fields_v0_2.json'));
  const fields = def.views[0].sections.find(section => section.id === 'fields').fields;
  const canonical = fields.find(field => field.field === 'width');
  const legacy = fields.find(field => field.field === 'grid.width');
  assert.ok(canonical);
  assert.equal(canonical.caption, '項目幅');
  assert.equal(canonical.edit?.readonly, false);
  assert.equal(legacy.caption, '旧Grid列幅');
  assert.equal(legacy.edit?.readonly, true);
});

test('Search UI uses fixed Studio standard width rather than stretching to Section width', () => {
  const css = read('wwwroot/styles.css');
  assert.match(css, /--studio-standard-field-width:\s*220px/);
  assert.match(css, /#searchSection #searchForm\.search-grid > \.field/);
  assert.match(css, /flex:\s*0 0 var\(--studio-standard-field-width\)\s*!important/);
  assert.match(css, /width:\s*var\(--studio-standard-field-width\)\s*!important/);
});

test('Field controls apply common width and install direct resize handles outside Search', () => {
  const js = read('wwwroot/js/renderers/field_controls.js');
  assert.match(js, /studioApplyFieldContainerWidth/);
  assert.match(js, /studioInstallFieldResizeHandle/);
  const live = read('wwwroot/js/runtime/live_view_design.js');
  assert.match(live, /ctx === 'search'.*STUDIO_STANDARD_FIELD_WIDTH_PX/s);
  assert.match(live, /studioFieldTypeUsesFixedControlWidth/);
  assert.match(live, /grid\.width remains read-compatible|grid\.width/);
});

test('Grid uses fixed resolved widths and exposes drag handles without auto-stretch', () => {
  const js = read('wwwroot/js/renderers/grid_detail.js');
  assert.match(js, /studioResolvedFieldWidth\(field, 'grid', gd\)/);
  assert.match(js, /document\.createElement\('colgroup'\)/);
  assert.match(js, /table\.style\.tableLayout = 'fixed'/);
  assert.match(js, /studioInstallGridColumnResizeHandle/);
});

test('Width changes are explicit-save Live View Design state and persist to ViewDef Field.width', () => {
  const html = read('wwwroot/index.html');
  const live = read('wwwroot/js/runtime/live_view_design.js');
  assert.match(html, /id="saveFieldWidthsBtn"[^>]*hidden/);
  assert.match(html, /id="saveDetailFieldWidthsBtn"[^>]*hidden/);
  assert.match(live, /studioFieldWidthDrafts/);
  assert.match(live, /field\.width = entry\.width/);
  assert.match(live, /delete field\.grid\.width/);
  assert.match(live, /fetch\(apiPath,\s*\{\s*method: 'POST'/s);
});

test('Loading another document clears uncommitted live width drafts', () => {
  const js = read('wwwroot/js/runtime/load_runtime.js');
  assert.match(js, /studioResetLiveFieldWidths/);
});
