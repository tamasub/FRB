import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';

const read = file => fs.readFileSync(file, 'utf8');
const load = file => JSON.parse(read(file));
const schema = load('data/json/00_rules/frb_view_def_schema_v0_9.json');
const launch = load('defs/launch/frb_launch_maintenance_view_def_v0_1.json');
const rules = load('data/json/00_rules/frb_viewdef_generation_rules_data_v0_1.json');
const items = launch.views.find(v => v.id === 'items_view').sections.find(s => s.id === 'items');

function createRuntime() {
  const head = { textContent: '詳細' };
  const row = { title: 'FRB StudioをZIP保存', location: { title: '<b>not HTML</b>' }, page_id: 'work', parent_item_id: 'zip', item_id: 'editor' };
  const grandparent = { row: { title: '開発' }, parent: null };
  const parent = { row: { title: 'ZIP作成' }, parent: grandparent };
  let pending = row;
  let builderCalls = 0;
  const ctx = {
    console,
    registerRenderer() {},
    detailMode: 'edit', currentRows: [row], selectedIndex: 0, draftRow: null,
    gridDef: () => items,
    getByPath(obj, path) { return path.replace(/^\$\./, '').split('.').reduce((v, k) => v?.[k], obj); },
    studioTreeConfig: gd => gd?.tree,
    studioTreeGroups: () => new Map([['work', '仕事']]),
    studioTreeModel: () => ({ ids: new Map([['zip', parent]]) }),
    studioTreeLabel: n => {const parts = []; for (let x = n; x; x = x.parent) parts.unshift(x.row.title); return parts.join(' › ');},
    $: id => id === 'detailTitle' ? head : null
  };
  vm.createContext(ctx);
  vm.runInContext(read('wwwroot/js/runtime/detail_save.js'), ctx, { filename: 'detail_save.js' });
  ctx.buildPendingDetailApplyRow = () => { builderCalls++; return pending; };
  return { ctx, head, row, getBuilderCalls: () => builderCalls, setPending: v => { pending = v; } };
}

test('launch ViewDef opts into a generic title; legacy tree placement stays out of detail body', () => {
  assert.deepEqual(items.detailHeader.title, {
    mode: 'template', template: '配置先: {tree.parentPath}', fallback: '詳細'
  });
  const runtime = read('wwwroot/js/runtime/tree_grid.js');
  assert.match(runtime, /detailHeaderTitleConfig\(gridDef\(\)\)/);
  assert.match(runtime, /if \s*\(typeof detailHeaderTitleConfig/);
  const html = read('wwwroot/index.html');
  assert.match(html, /<h2 id="detailTitle">詳細<\/h2>/);
  assert.match(read('wwwroot/js/runtime/detail_save.js'), /renderDetailHeaderTitle\(row, gd\)/);
});

test('template resolves all tree ancestors and row values; fallback and safe text rendering', () => {
  const { ctx, head, row } = createRuntime();
  assert.equal(ctx.resolveDetailHeaderTitle(row, items), '配置先: 仕事 › 開発 › ZIP作成');
  const rowSpec = { detailHeader: { title: { mode: 'template', template: '案件: {row.location.title}' } } };
  assert.equal(ctx.resolveDetailHeaderTitle(row, rowSpec), '案件: <b>not HTML</b>');
  ctx.renderDetailHeaderTitle(row, rowSpec);
  assert.equal(head.textContent, '案件: <b>not HTML</b>');
  assert.equal(ctx.resolveDetailHeaderTitle(row, {}), '詳細');
  assert.equal(ctx.resolveDetailHeaderTitle(row, { detailHeader: { title: { mode: 'template', template: 'X{row.missing}', fallback: '不明' } } }), '不明');
  assert.equal(ctx.resolveDetailHeaderTitle(row, { detailHeader: { title: { mode: 'template', template: '{unknown.token}', fallback: '不明' } } }), '不明');
  assert.equal(ctx.resolveDetailHeaderTitle(row, { tree: items.tree, detailHeader: { title: { mode: 'template', template: '{tree.ancestorPath}' } } }), '開発 › ZIP作成');
  assert.equal(ctx.resolveDetailHeaderTitle(row, { tree: items.tree, detailHeader: { title: { mode: 'template', template: '{tree.groupLabel}' } } }), '仕事');
  assert.equal(ctx.resolveDetailHeaderTitle({ ...row, parent_item_id: '' }, items), '配置先: 仕事');
  assert.equal(ctx.resolveDetailHeaderTitle({ ...row, parent_item_id: 'missing' }, items), '詳細');
});

test('live edit previews changed row title but does not mutate canonical data', () => {
  const { ctx, row, head, setPending, getBuilderCalls } = createRuntime();
  const gd = { detailHeader: { title: { mode: 'template', template: '名称: {row.title}', fallback: '詳細' } } };
  ctx.gridDef = () => gd;
  setPending({ ...row, title: '変更途中' });
  ctx.refreshDetailHeaderTitleOnEdit({ target: { dataset: { field: 'title' } } });
  assert.equal(head.textContent, '名称: 変更途中');
  assert.equal(row.title, 'FRB StudioをZIP保存');
  assert.equal(getBuilderCalls(), 1);
  ctx.refreshDetailHeaderTitleOnEdit({ target: { dataset: { field: 'location' } } });
  assert.equal(getBuilderCalls(), 1);
});

test('schema and rulebook describe new title and existing external JSON left_join contracts', () => {
  assert.equal(schema.$defs.section.properties.detailHeader.$ref, '#/$defs/detailHeader');
  assert.deepEqual(schema.$defs.detailHeaderTitle.properties.mode.enum, ['template']);
  assert.equal(schema.$defs.detailHeaderTitle.additionalProperties, false);
  assert.equal(schema.$defs.dataSourceSpec.properties.pathFromData.type, 'string');
  assert.equal(schema.$defs.virtualDataConfig.properties.keys.items.$ref, '#/$defs/virtualJoinKey');
  assert.equal(schema.$defs.virtualDataWriteBack.properties.targets.items.$ref, '#/$defs/virtualJoinWriteBackTarget');
  const r41 = rules.rules.find(r => r.rule_id === 'viewdef_rule_41');
  const r42 = rules.rules.find(r => r.rule_id === 'viewdef_rule_42');
  assert.match(r41.body, /tree\.parentPath/);
  assert.match(r42.body, /left_join/);
  assert.equal(r41.approval_decision, '未承認');
  assert.equal(r42.approval_decision, '未承認');
  assert.equal(rules.rule_count, rules.rules.length);
  assert.equal(rules.approved_count, 90);
});
