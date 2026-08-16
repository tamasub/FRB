import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import test from 'node:test';
import vm from 'node:vm';

const root = process.cwd();
const readText = (relativePath) => fs.readFileSync(path.join(root, relativePath), 'utf8');
const readJson = (relativePath) => JSON.parse(readText(relativePath));

function loadSearchFilter() {
  const context = { console };
  vm.createContext(context);
  vm.runInContext(readText('wwwroot/js/responsibilities/search_filter.js'), context, {
    filename: 'wwwroot/js/responsibilities/search_filter.js'
  });
  return context.SearchFilter;
}

function loadSearchUi() {
  const sandbox = { console, globalThis: null };
  sandbox.globalThis = sandbox;
  vm.createContext(sandbox);
  vm.runInContext(readText('wwwroot/js/services/search_ui_controller.js'), sandbox, {
    filename: 'wwwroot/js/services/search_ui_controller.js'
  });
  return sandbox.StandardSearchUi;
}

const SearchFilter = loadSearchFilter();
const SearchUi = loadSearchUi();

test('Phase 4 wires SearchCapabilityResolver -> StandardSearchUi -> SearchFilter before Runtime render', () => {
  const html = readText('wwwroot/index.html');
  const resolver = html.indexOf('js/services/search_capability_resolver.js');
  const ui = html.indexOf('js/services/search_ui_controller.js');
  const filter = html.indexOf('js/responsibilities/search_filter.js');
  const runtime = html.indexOf('js/runtime/load_runtime.js');
  assert.ok(resolver >= 0);
  assert.ok(ui > resolver);
  assert.ok(filter > ui);
  assert.ok(runtime > filter);
  assert.match(html, /search_ui_controller\.js\?v=standard-search-ui-01867/);

  const loadRuntime = readText('wwwroot/js/runtime/load_runtime.js');
  assert.match(loadRuntime, /await ensureStandardSearchUiContext\(\)/);
  assert.ok(loadRuntime.indexOf('await ensureStandardSearchUiContext()') < loadRuntime.indexOf("renderByKey('search')"));

  const renderer = readText('wwwroot/js/renderers/field_controls.js');
  assert.match(renderer, /resolveStandardSearchCapability\(field\)/);
  assert.match(renderer, /createStandardSearchField\(field, capability, createFieldControlElement\)/);
});

test('standard operator stays visually quiet and only non-range override requires the pin', () => {
  const textCapability = {
    value_family: 'string',
    derived: { default_operator: 'contains' },
    effective: { default_operator: 'contains' }
  };
  assert.equal(SearchUi.isVisualOverride('contains', textCapability), false);
  assert.equal(SearchUi.isVisualOverride('not_contains', textCapability), true);
  assert.equal(SearchUi.operatorCaption('equals', 'string'), '完全一致');
  assert.equal(SearchUi.operatorCaption('not_equals', 'string'), '一致以外');
  assert.equal(SearchUi.operatorCaption('gte', 'date'), '以降');
  assert.equal(SearchUi.operatorCaption('lte', 'number'), '以下');

  const rangeOverride = {
    value_family: 'number',
    derived: { default_operator: 'equals' },
    effective: { default_operator: 'between' }
  };
  assert.equal(SearchUi.isVisualOverride('between', rangeOverride), false, 'From/To shape itself is the visual signal');
});

test('context menu remains one level and merges Combo option maintenance below a separator', () => {
  const source = readText('wwwroot/js/services/search_ui_controller.js');
  assert.match(source, /standard-search-context-separator/);
  assert.match(source, /String\(state\.field\?\.type \?\? ''\) === 'select'/);
  assert.match(source, /⚙ 選択肢メンテナンス\.\.\./);
  assert.match(source, /openComboOptionMaintenanceForField/);
  assert.doesNotMatch(source, /submenu|sub-menu|createElement\(['"]ul['"]\)|createElement\(['"]menu['"]\)/i);

  const optionMaintenance = readText('wwwroot/js/services/option_maintenance_service.js');
  assert.match(optionMaintenance, /openComboOptionMaintenanceForField/);
  assert.match(optionMaintenance, /input\.dataset\.standardSearchContextMenu === '1'/);
  assert.match(optionMaintenance, /input\.__studioOpenOptionMaintenance/);
});

test('range controls emit one between criterion with From/To and resolved value family', () => {
  const fields = [{ field: 'score', type: 'number', search: { visible: true } }];
  const inputs = [
    {
      dataset: { field: 'score', searchOperator: 'between', searchRole: 'from', searchValueFamily: 'integer' },
      value: '5', multiple: false
    },
    {
      dataset: { field: 'score', searchOperator: 'between', searchRole: 'to', searchValueFamily: 'integer' },
      value: '10', multiple: false
    }
  ];
  const criteria = SearchFilter.criteriaFromInputs(inputs, fields);
  assert.equal(criteria.length, 1);
  assert.equal(criteria[0].field, 'score');
  assert.equal(criteria[0].operator, 'between');
  assert.equal(criteria[0].value_family, 'integer');
  assert.equal(criteria[0].from, '5');
  assert.equal(criteria[0].to, '10');

  const rows = [{ id: 'a', score: 4 }, { id: 'b', score: 5 }, { id: 'c', score: 10 }, { id: 'd', score: 11 }];
  assert.deepEqual(Array.from(SearchFilter.apply(rows, criteria), item => item.row.id), ['b', 'c']);
});

test('no-value operators stay active with a hidden empty control', () => {
  const fields = [{ field: 'caption', type: 'text', search: { visible: true } }];
  const inputs = [{
    dataset: { field: 'caption', searchOperator: 'not_blank', searchRole: 'value', searchValueFamily: 'string' },
    value: '', multiple: false
  }];
  const criteria = SearchFilter.criteriaFromInputs(inputs, fields);
  assert.equal(criteria.length, 1);
  assert.equal(criteria[0].operator, 'not_blank');
  const rows = [{ id: 'blank', caption: '' }, { id: 'set', caption: 'abc' }];
  assert.deepEqual(Array.from(SearchFilter.apply(rows, criteria), item => item.row.id), ['set']);
});

test('Number and Date standard sets remain between, while Combo stays equals', () => {
  const registry = readJson('data/json/config/search_operator_registry_v0_1.json');
  const sets = new Map(registry.operator_sets.filter(x => x.status === 'active').map(x => [x.id, x]));
  assert.equal(sets.get('numeric_standard').default_operator, 'between');
  assert.equal(sets.get('date_standard').default_operator, 'between');
  assert.equal(sets.get('select_standard').default_operator, 'equals');

  const source = readText('wwwroot/js/services/search_ui_controller.js');
  assert.match(source, /from\.placeholder = 'From'/);
  assert.match(source, /to\.placeholder = 'To'/);
  assert.match(source, /family === 'date'\) input\.type = 'date'/);
  assert.match(source, /family === 'datetime'\) input\.type = 'datetime-local'/);
});

test('Search clear resets runtime operator override to the effective default', () => {
  const app = readText('wwwroot/app.js');
  assert.match(app, /resetStandardSearchUi\(\$\('searchForm'\)\)/);
  const source = readText('wwwroot/js/services/search_ui_controller.js');
  assert.match(source, /state\.currentOperator = state\.effectiveDefaultOperator/);
  assert.match(source, /state\.values = \{ value: '', from: '', to: '' \}/);
});

test('Phase 4 incident is completed and its Phase 5 follow-up lifecycle is updated', () => {
  const incident = readJson('data/json/01_main/_studio_work_incident_data_v2.json');
  const phase3 = incident.work_items.find(work => work.work_item_id === 'studio_work_0188');
  const phase4 = incident.work_items.find(work => work.work_item_id === 'studio_work_0189');
  const phase5 = incident.work_items.find(work => work.work_item_id === 'studio_work_0190');
  assert.ok(phase3 && phase4 && phase5);
  assert.equal(phase4.phase, 'v0.18.67-standard-search-ui-context-menu-phase4');
  assert.equal(phase4.status, '完了');
  assert.equal(phase4.follow_up_status, 'COMPLETED');
  assert.ok(phase4.follow_up_actions.some(action => action.related_ids?.includes('studio_work_0190') && action.status === 'COMPLETED'));
  assert.ok(phase3.follow_up_actions.some(action => action.related_ids?.includes('studio_work_0189') && action.status === 'COMPLETED'));
  assert.equal(incident.items_count, incident.work_items.length);
});
