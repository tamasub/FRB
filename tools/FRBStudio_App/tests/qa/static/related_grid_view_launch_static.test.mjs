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
  assert.equal(related[0].viewDef, 'rules/governance_items_common_view_def_v0_1.json');
});

test('coding constraints sample has three document-level decision axes', () => {
  const data = readJson('data/json/00_rules/frb_coding_constraints_data_v0_3.json');
  assert.ok(Array.isArray(data.governance_items));
  assert.equal(data.governance_items.length, 3);
  assert.deepEqual(data.governance_items.map(x => x.item_type), [
    'DECISION_AXIS', 'DECISION_AXIS', 'DECISION_AXIS'
  ]);
  const statements = data.governance_items.map(x => x.statement).join('\n');
  assert.match(statements, /損得より善悪/);
  assert.match(statements, /安心安全・セキュリティー ＞ 品質 ＞ 納期/);
  assert.match(statements, /人間の視認性を最優先/);
  assert.match(statements, /作業を中断し、人間と協議/);
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
  assert.match(runtime, /same array|同じ配列/);
  assert.match(runtime, /sourceData !== session\.sourceDataRef/);
  assert.doesNotMatch(runtime, /getByPath\(sourceData, ['"]\$\.governance_items['"]\)/);
});

test('ViewDef Schema documents generic related grid declarations', () => {
  const schema = readJson('data/json/00_rules/frb_view_def_schema_v0_9.json');
  const toolbar = schema.$defs?.toolbarOptions?.properties;
  assert.equal(toolbar?.relatedGridViews?.items?.$ref, '#/$defs/relatedGridViewOptions');
  assert.equal(schema.$defs?.relatedGridViewOptions?.properties?.shellMode?.enum?.[0], 'grid_only');
});
