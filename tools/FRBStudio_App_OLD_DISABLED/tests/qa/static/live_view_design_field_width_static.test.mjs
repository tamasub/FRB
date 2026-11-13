// v0.18.136 Live View Design / Field.width + FULL + width tip + combo resize + dialog top-layer tip fix
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';

const read = path => fs.readFileSync(path, 'utf8');

test('ViewDef schema exposes canonical Field.width with numeric px or FULL and marks grid.width as legacy', () => {
  const schema = JSON.parse(read('data/json/00_rules/frb_view_def_schema_v0_9.json'));
  const fieldWidth = schema?.$defs?.field?.properties?.width;
  const gridWidth = schema?.$defs?.gridOptions?.properties?.width;
  assert.ok(Array.isArray(fieldWidth?.oneOf));
  assert.ok(fieldWidth.oneOf.some(rule => rule?.type === 'number'));
  assert.ok(fieldWidth.oneOf.some(rule => rule?.type === 'string' && rule?.enum?.includes('FULL')));
  assert.match(String(fieldWidth?.description ?? ''), /Field共通|正本/);
  assert.match(String(fieldWidth?.description ?? ''), /FULL/);
  assert.match(String(gridWidth?.description ?? ''), /Legacy|互換/);
});

test('ViewDef maintenance exposes px/FULL input and keeps legacy grid.width read-only', () => {
  const def = JSON.parse(read('defs/common/view_def_maint_fields_v0_2.json'));
  const fields = def.views[0].sections.find(section => section.id === 'fields').fields;
  const canonical = fields.find(field => field.field === 'width');
  const legacy = fields.find(field => field.field === 'grid.width');
  assert.ok(canonical);
  assert.match(canonical.caption, /FULL/);
  assert.equal(canonical.type, 'text');
  assert.equal(canonical.edit?.readonly, false);
  assert.match(String(canonical.edit?.placeholder ?? ''), /FULL/);
  assert.equal(legacy.caption, '旧Grid列幅');
  assert.equal(legacy.edit?.readonly, true);
});

test('ViewDef maintenance projection normalizes numeric text and FULL for canonical width', () => {
  const js = read('wwwroot/js/services/viewdef_maintenance_projection.js');
  assert.match(js, /text\.toUpperCase\(\) === 'FULL'/);
  assert.match(js, /field\.width = 'FULL'/);
  assert.match(js, /Number\.isFinite\(numeric\).*field\.width = numeric/s);
  assert.match(js, /delete field\.width/);
});

test('Search UI uses fixed Studio standard width rather than stretching to Section width', () => {
  const css = read('wwwroot/styles.css');
  assert.match(css, /--studio-standard-field-width:\s*220px/);
  assert.match(css, /#searchSection #searchForm\.search-grid > \.field/);
  assert.match(css, /flex:\s*0 0 var\(--studio-standard-field-width\)\s*!important/);
  assert.match(css, /width:\s*var\(--studio-standard-field-width\)\s*!important/);
});

test('Field controls apply common width and FULL can consume the available Header/Detail row', () => {
  const js = read('wwwroot/js/renderers/field_controls.js');
  assert.match(js, /studioApplyFieldContainerWidth/);
  assert.match(js, /studioInstallFieldResizeHandle/);
  const live = read('wwwroot/js/runtime/live_view_design.js');
  const css = read('wwwroot/styles.css');
  assert.match(live, /STUDIO_FIELD_WIDTH_FULL = 'FULL'/);
  assert.match(live, /ctx === 'search'.*STUDIO_STANDARD_FIELD_WIDTH_PX/s);
  assert.match(live, /canonical === STUDIO_FIELD_WIDTH_FULL.*return STUDIO_FIELD_WIDTH_FULL/s);
  assert.match(live, /wrap\.style\.width = full \? '100%' :/);
  assert.match(live, /wrap\.style\.flex = full \? '1 0 100%'/);
  assert.match(css, /\.field\.studio-field-width-full/);
});


test('Chat fields also honor canonical Field.width/FULL instead of bypassing the common resolver', () => {
  const js = read('wwwroot/js/renderers/field_controls.js');
  assert.match(js, /field\.type === 'chat'[\s\S]*createChatInput/);
  assert.match(js, /field\.type === 'chat'[\s\S]*studioApplyFieldContainerWidth\(chatWrap, field, prefix, widthSection\)/);
});

test('Grid supports FULL columns as remaining-width columns while fixed fields stay fixed', () => {
  const js = read('wwwroot/js/renderers/grid_detail.js');
  assert.match(js, /studioResolvedFieldWidth\(field, 'grid', gd\)/);
  assert.match(js, /fullCount = resolvedWidths\.filter/);
  assert.match(js, /table\.style\.width = fullCount > 0 \? '100%'/);
  assert.match(js, /fixedTotalWidth \+ \(fullCount \* standardWidth\)/);
  assert.match(js, /col\.dataset\.studioFieldWidthMode = full \? fullToken : 'FIXED'/);
  assert.match(js, /studioInstallGridColumnResizeHandle/);
});

test('Dragging a FULL field intentionally changes it to a numeric live draft without auto-save', () => {
  const live = read('wwwroot/js/runtime/live_view_design.js');
  assert.match(live, /Direct resize is an explicit choice to leave FULL/);
  assert.match(live, /wrap\.classList\.remove\('studio-field-width-full'\)/);
  assert.match(live, /col\.dataset\.studioFieldWidthMode = 'FIXED'/);
  assert.match(live, /studioSetLiveFieldWidth\(field, width, section/);
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

test('Live resize shows the current px width as a realtime pointer tip for Field and Grid resizing', () => {
  const live = read('wwwroot/js/runtime/live_view_design.js');
  const css = read('wwwroot/styles.css');
  assert.match(live, /function studioShowFieldWidthTip\(width, clientX, clientY, sourceElement=null\)/);
  assert.match(live, /tip\.textContent = `\$\{normalized\}px`/);
  assert.match(live, /studioShowFieldWidthTip\(startWidth, event\.clientX, event\.clientY, wrap\)/);
  assert.match(live, /studioShowFieldWidthTip\(startWidth, event\.clientX, event\.clientY, th\)/);
  assert.ok((live.match(/studioShowFieldWidthTip\(width, moveEvent\.clientX, moveEvent\.clientY, (?:wrap|th)\)/g) ?? []).length >= 2);
  assert.ok((live.match(/studioHideFieldWidthTip\(\)/g) ?? []).length >= 3);
  assert.match(css, /\.studio-field-width-tip\s*\{/);
  assert.match(css, /position:\s*fixed/);
  assert.match(css, /pointer-events:\s*none/);
});

test('Editor resize Tip is mounted in the same modal dialog Top Layer so it stays visible above Detail', () => {
  const live = read('wwwroot/js/runtime/live_view_design.js');
  assert.match(live, /function studioFieldWidthTipHost\(sourceElement=null\)/);
  assert.match(live, /source\?\.closest\?\.\('dialog\[open\]'\)/);
  assert.match(live, /if \(dialog\) return dialog/);
  assert.match(live, /host\.appendChild\(studioFieldWidthTip\)/);
});

test('Combo/select keeps standard width by default but supports explicit and Live View Design width changes outside Search', () => {
  const live = read('wwwroot/js/runtime/live_view_design.js');
  assert.match(live, /return \['boolean', 'checkbox', 'radio'\]\.includes\(type\)/);
  assert.match(live, /\['text', 'textarea', 'number', 'date', 'datetime', 'select'\]\.includes/);
  assert.doesNotMatch(live, /return \['select', 'boolean', 'checkbox', 'radio'\]\.includes\(type\)/);
  assert.match(live, /if \(ctx === 'search'\) return STUDIO_STANDARD_FIELD_WIDTH_PX/);
});

