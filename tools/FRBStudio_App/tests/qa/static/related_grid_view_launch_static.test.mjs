import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const root = path.resolve(__dirname, '../../..');

function readText(relative) {
  return fs.readFileSync(path.join(root, relative), 'utf8');
}

function readJson(relative) {
  return JSON.parse(readText(relative));
}

test('rule review ViewDef declares a generic related Root Grid launch', () => {
  const viewDef = readJson('defs/rules/rule_review_common_view_def_v0_3.json');
  const related = viewDef.views?.[0]?.toolbar?.relatedGridViews;
  assert.ok(Array.isArray(related));
  assert.equal(related.length, 1);
  assert.equal(related[0].action, 'OpenRelatedGridView');
  assert.equal(related[0].dataPath, '$.governance_items');
  assert.equal(related[0].shellMode, 'grid_only');
  assert.equal(related[0].launchMode, 'modal');
  assert.equal(related[0].viewDef, 'rules/governance_items_common_view_def_v0_1.json');
});

test('coding constraints keeps decision axes as an extensible canonical set including approval / observability axes', () => {
  const data = readJson('data/json/00_rules/frb_coding_constraints_data_v0_3.json');
  assert.ok(Array.isArray(data.governance_items));
  assert.ok(data.governance_items.length >= 5);
  assert.ok(data.governance_items.every(x => x.item_type === 'DECISION_AXIS'));
  const ids = data.governance_items.map(x => x.item_id);
  assert.equal(new Set(ids).size, ids.length);
  for (const requiredId of [
    'decision_axis_small_meaningful_diff_approval_first',
    'decision_axis_good_over_gain',
    'decision_axis_safety_quality_delivery',
    'decision_axis_human_readability_first',
    'decision_axis_responsibility_before_commonization',
    'decision_axis_responsibility_observability',
    'decision_axis_expected_independent_simple_derivation_copy_1'
  ]) assert.ok(ids.includes(requiredId), `missing decision axis: ${requiredId}`);

  const statements = data.governance_items.map(x => x.statement).join('\n');
  assert.match(statements, /損得より善悪/);
  assert.match(statements, /安心安全・セキュリティー ＞ 品質 ＞ 納期/);
  assert.match(statements, /人間の視認性を最優先/);
  assert.match(statements, /最小十分な差分/);
  assert.match(statements, /責務境界の外側から観測可能/);
  const northStar = data.governance_items.find(x => x.item_id === 'decision_axis_small_meaningful_diff_approval_first');
  assert.ok(northStar);
  assert.match(northStar.evaluation_guidance, /base\/reference/);
  assert.match(northStar.evaluation_guidance, /override\/diff/);
});

test('related Grid child ViewDef points to the declared root array', () => {
  const viewDef = readJson('defs/rules/governance_items_common_view_def_v0_1.json');
  const grid = viewDef.views?.[0]?.sections?.find(section => section.type === 'grid');
  assert.equal(grid?.dataPath, '$.governance_items');
  assert.equal(grid?.keyField, 'item_id');
  assert.ok(grid.fields.some(field => field.field === 'item_type'));
  assert.ok(grid.fields.some(field => field.field === 'source_decision_log_ids'));
});

test('Runtime uses ViewDef paths and parent-child array-only apply with conflict guard', () => {
  const runtime = readText('wwwroot/js/runtime/related_grid_view.js');
  assert.match(runtime, /toolbar\?\.relatedGridViews/);
  assert.match(runtime, /registerStudioAction\('OpenRelatedGridView'/);
  assert.match(runtime, /postMessage/);
  assert.match(runtime, /openRelatedGridModal/);
  assert.match(runtime, /related-grid-modal-frame/);
  assert.match(runtime, /same array|同じ配列/);
  assert.match(runtime, /sourceData !== session\.sourceDataRef/);
  assert.match(runtime, /relatedGridViewDefForViewId/);
  assert.doesNotMatch(runtime, /getByPath\(sourceData, ['"]\$\.governance_items['"]\)/);
});

test('ViewDef Schema documents generic related grid declarations', () => {
  const schema = readJson('data/json/00_rules/frb_view_def_schema_v0_9.json');
  const toolbar = schema.$defs?.toolbarOptions?.properties;
  assert.equal(toolbar?.relatedGridViews?.items?.$ref, '#/$defs/relatedGridViewOptions');
  assert.equal(schema.$defs?.relatedGridViewOptions?.properties?.shellMode?.enum?.[0], 'grid_only');
  assert.deepEqual(schema.$defs?.relatedGridViewOptions?.properties?.launchMode?.enum, ['modal', 'new_window']);
  assert.equal(schema.$defs?.relatedGridViewOptions?.properties?.viewId?.type, 'string');
});


test('Validation Type Registry keeps related Root Grid views in one ViewDef file', () => {
  const viewDef = readJson('defs/config/validation_type_registry_view_def_v0_1.json');
  assert.equal(viewDef.views?.length, 2);
  const related = viewDef.views?.[0]?.toolbar?.relatedGridViews?.[0];
  assert.equal(related?.dataPath, '$.view_def_type_catalogs');
  assert.equal(related?.viewId, 'validation_type_catalogs_v0_1');
  assert.equal(related?.viewDef, undefined);
  const childView = viewDef.views.find(view => view.id === related.viewId);
  const grid = childView?.sections?.find(section => section.type === 'grid');
  assert.equal(grid?.dataPath, '$.view_def_type_catalogs');
  assert.equal(grid?.keyField, 'view_def_type');
  assert.equal(fs.existsSync(path.join(root, 'defs/config/validation_type_catalogs_view_def_v0_1.json')), false);
});

test('Runtime supports same-file viewId and external viewDef plus viewId', () => {
  const runtime = readText('wwwroot/js/runtime/related_grid_view.js');
  assert.match(runtime, /raw\.viewId \?\? raw\.view_id/);
  assert.match(runtime, /relatedGridViewDefForViewId/);
  assert.match(runtime, /payload\.sourceViewDef/);
  assert.match(runtime, /config\.viewDef/);
  assert.match(runtime, /config\.viewId/);
  assert.match(runtime, /viewId=.*が見つかりません/);
});

test('ViewDef Schema accepts viewId as an alternative to external viewDef', () => {
  const schema = readJson('data/json/00_rules/frb_view_def_schema_v0_9.json');
  const related = schema.$defs?.relatedGridViewOptions;
  assert.equal(related?.properties?.viewId?.type, 'string');
  assert.equal(related?.properties?.view_id?.type, 'string');
  const targetRequirement = related?.allOf?.[1]?.anyOf ?? [];
  assert.ok(targetRequirement.some(item => item.required?.[0] === 'viewDef'));
  assert.ok(targetRequirement.some(item => item.required?.[0] === 'viewId'));
});

test('index.html refreshes the Related Grid Runtime asset after viewId support', () => {
  const index = readText('wwwroot/index.html');
  assert.match(index, /js\/runtime\/related_grid_view\.js\?v=related-grid-inline-view-id-01834b/);
  assert.doesNotMatch(index, /js\/runtime\/related_grid_view\.js\?v=related-grid-modal-01828a/);
});

