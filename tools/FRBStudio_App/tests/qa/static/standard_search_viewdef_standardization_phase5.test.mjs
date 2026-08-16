import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import test from 'node:test';

const root = process.cwd();
const readText = (relativePath) => fs.readFileSync(path.join(root, relativePath), 'utf8');
const readJson = (relativePath) => JSON.parse(readText(relativePath));

function firstView(relativePath) {
  const def = readJson(relativePath);
  return def.views[0];
}

function section(view, predicate) {
  return view.sections.find(predicate);
}

test('Test Runner representative ViewDef owns search visibility only on the Canonical Grid fields', () => {
  const view = firstView('defs/tools/test_runner_run_config_view_def_v0_1.json');
  const legacySearch = section(view, item => item.id === 'search');
  const grid = section(view, item => item.type === 'grid' && item.dataPath === 'run_configs');
  assert.equal(legacySearch, undefined);
  assert.ok(grid);
  const searchable = grid.fields.filter(field => field.search?.visible === true).map(field => field.field);
  assert.deepEqual(searchable, ['run_config_id', 'caption', 'test_runner_id', 'run_mode', 'enabled']);
});

test('Git Diff representative ViewDef does not retain an empty legacy Search Section', () => {
  const view = firstView('defs/tools/git_diff_export_run_config_view_def_v0_1.json');
  assert.equal(view.sections.some(item => item.id === 'search'), false);
  const grid = section(view, item => item.type === 'grid' && item.dataPath === 'run_configs');
  assert.ok(grid);
  assert.ok(grid.fields.some(field => field.search?.visible === true));
});

test('Runtime search renderer projects from gridDef fields and does not require a Search Section', () => {
  const source = readText('wwwroot/js/renderers/field_controls.js');
  assert.match(source, /function renderSearch\(\) \{\s*const gd = gridDef\(\)/);
  assert.match(source, /gd\.fields\.filter\(f => f\.search\?\.visible\)/);
  assert.doesNotMatch(source, /mainView\(\)\.sections\.find\([^\n]*id[^\n]*search/);
});

test('ViewDef generation contract forbids new duplicate/empty Search Sections while retaining staged legacy compatibility', () => {
  const rules = readJson('data/json/00_rules/frb_viewdef_generation_rules_data_v0_1.json');
  const rule = rules.rules.find(item => item.rule_id === 'viewdef_rule_36');
  assert.ok(rule);
  assert.match(rule.body, /新規ViewDefでは、検索UI配置だけを理由に `id: search` のSectionを作成しない/);
  assert.match(rule.body, /空のSearch Sectionも新規生成しない/);
  assert.match(rule.body, /同一dataPath \/ 同一fieldへ検索意図を明示的に転記/);
  assert.match(rule.body, /全件自動変換せず/);
  assert.match(rule.body, /既存Search Sectionは即削除しない/);
});

test('JSON creation prompt carries the same Canonical Search Projection rule for future ViewDefs', () => {
  const prompt = readText('data/json/00_rules/_json_creation_prompt.md');
  assert.match(prompt, /v0\.18\.68 追加ルール: 標準検索ViewDef \/ Canonical Search Projection/);
  assert.match(prompt, /検索Fieldを独立したSearch Sectionへ複製しない/);
  assert.match(prompt, /Fieldを持たない空のSearch Sectionも新規生成しない/);
  assert.match(prompt, /Canonical Fieldへ検索意図を転記/);
});

test('Phase 5 incident is completed and Phase 6 remains the explicit next phase', () => {
  const incident = readJson('data/json/01_main/_studio_work_incident_data_v2.json');
  const phase4 = incident.work_items.find(work => work.work_item_id === 'studio_work_0189');
  const phase5 = incident.work_items.find(work => work.work_item_id === 'studio_work_0190');
  const phase6 = incident.work_items.find(work => work.work_item_id === 'studio_work_0191');
  assert.ok(phase4 && phase5 && phase6);
  assert.equal(phase5.status, '完了');
  assert.equal(phase5.phase, 'v0.18.68-standard-search-viewdef-standardization-phase5');
  assert.equal(phase5.follow_up_status, 'PENDING');
  assert.ok(phase5.follow_up_actions.some(action => action.related_ids?.includes('studio_work_0191') && action.status === 'PENDING'));
  assert.ok(phase4.follow_up_actions.some(action => action.related_ids?.includes('studio_work_0190') && action.status === 'COMPLETED'));
});
