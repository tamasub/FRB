const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const root = path.resolve(process.argv[2] || process.cwd());
function artifactPath(...parts) {
  const normalized = path.join(root, ...parts);
  if (fs.existsSync(normalized)) return normalized;
  const windowsEntry = path.join(root, parts.join('\\'));
  if (fs.existsSync(windowsEntry)) return windowsEntry;
  throw new Error(`テスト対象ファイルが見つかりません: ${parts.join('/')}`);
}

const pluginPath = artifactPath('studio_overlays', 'gpt_fx_lab', 'plugins', 'fx_chart_viewer', 'plugin.js');
const manifestPath = artifactPath('studio_overlays', 'gpt_fx_lab', 'plugins', 'fx_chart_viewer', 'plugin.json');
const viewDefPath = artifactPath('studio_overlays', 'gpt_fx_lab', 'view_defs', 'fx_batch_entry_results_view_def_v0_1.json');
const source = fs.readFileSync(pluginPath, 'utf8');
const manifest = JSON.parse(fs.readFileSync(manifestPath, 'utf8'));
const viewDef = JSON.parse(fs.readFileSync(viewDefPath, 'utf8'));

assert.equal(manifest.version, '0.9.1.23');
assert.ok(manifest.actions.includes('OpenFxEntryChartUrl'));
const executeButton = viewDef.views[0].toolbar.executeButton;
assert.equal(executeButton.action, 'OpenFxEntryChartUrl');
assert.equal(executeButton.chartNavigation.timeField, 'entry_time');
assert.equal(executeButton.chartNavigation.priceField, 'entry_price');
assert.equal(executeButton.chartNavigation.target, 'new_tab');
assert.equal(executeButton.chartNavigation.chartLayout, 'M5_ENTRY');
assert.equal(executeButton.chartNavigation.upperTimeframe, 'BOTH');
assert.equal(executeButton.chartNavigation.entryEventIdField, 'entry_event_id');
assert.equal(executeButton.chartNavigation.batchFileField, 'source_batch_file');

const registered = new Map();
const fakeLocation = { href: 'http://localhost:5055/index.html?ver=new&data=old.json', search: '' };
let openedUrl = '';
let openedTarget = '';
const openedWindow = { opener: 'initial' };
const fakeWindow = {
  location: fakeLocation,
  StudioOverlayPlugins: {},
  registerStudioPlugin(plugin) { this.registeredPlugin = plugin; },
  open(url, target) { openedUrl = String(url); openedTarget = String(target); return openedWindow; }
};
const context = {
  window: fakeWindow,
  location: fakeLocation,
  URL,
  URLSearchParams,
  console,
  setTimeout() { return 0; },
  clearTimeout() {},
  document: {},
  navigator: {},
  structuredClone: global.structuredClone,
  crypto: global.crypto,
  Blob: global.Blob,
  TextEncoder: global.TextEncoder,
  TextDecoder: global.TextDecoder
};
context.globalThis = context;
vm.createContext(context);
vm.runInContext(source, context, { filename: pluginPath, timeout: 10000 });
const plugin = fakeWindow.registeredPlugin || fakeWindow.StudioOverlayPlugins['gpt_fx_lab.fx_chart_viewer'];
assert.ok(plugin, 'Pluginが登録されていません');
plugin.activate({
  plugin: { manifest },
  registerAction(id, handler, aliases = []) {
    registered.set(id, handler);
    aliases.forEach(alias => registered.set(alias, handler));
  },
  getSourceData() { return { source_batch_file: 'batch_20260712_230503.json' }; }
});

const action = registered.get('OpenFxEntryChartUrl');
assert.equal(typeof action, 'function');
const selectedRow = {
  entry_time: '2025-10-29 21:04',
  entry_price: 152.391,
  trade_id: 'trade_0001_1761739499999',
  rule_lane: 'NORMAL',
  side: 'LONG',
  row_id: 'entry_result_test_001',
  entry_event_id: 'execution_evt_entry_001',
  exit_event_id: 'execution_evt_close_001'
};
const resultPromise = action({ selectedRow, executeButton });
Promise.resolve(resultPromise).then(result => {
  assert.equal(fakeLocation.href, 'http://localhost:5055/index.html?ver=new&data=old.json');
  assert.equal(openedTarget, '_blank');
  assert.equal(openedWindow.opener, null);
  const url = new URL(openedUrl);
  assert.equal(url.searchParams.get('ver'), 'new');
  assert.equal(url.searchParams.get('data'), 'overlay/gpt_fx_lab/data/fx_usdjpy_m5_t3_data_v0_1.json');
  assert.equal(url.searchParams.get('view'), 'overlay/gpt_fx_lab/view_defs/fx_usdjpy_t3_view_def_v0_1.json');
  assert.equal(url.searchParams.get('action'), 'fx_chart');
  assert.equal(url.searchParams.get('focusTime'), '2025-10-29 21:04');
  assert.equal(url.searchParams.get('focusPrice'), '152.391');
  assert.equal(url.searchParams.get('focusTradeId'), selectedRow.trade_id);
  assert.equal(url.searchParams.get('focusLane'), 'NORMAL');
  assert.equal(url.searchParams.get('focusSide'), 'LONG');
  assert.equal(url.searchParams.get('focusRowId'), selectedRow.row_id);
  assert.equal(url.searchParams.get('focusEntryEventId'), selectedRow.entry_event_id);
  assert.equal(url.searchParams.get('focusExitEventId'), selectedRow.exit_event_id);
  assert.equal(url.searchParams.get('focusBatchData'), 'overlay/gpt_fx_lab/simulattion_集計/batch_20260712_230503.json');
  assert.equal(url.searchParams.get('windowSize'), '1000');
  assert.equal(url.searchParams.get('chartLayout'), 'M5_ENTRY');
  assert.equal(url.searchParams.get('upperTf'), 'BOTH');
  assert.equal(url.searchParams.get('wide'), '1');
  assert.match(result.message, /新しいタブでEntryチャートを開きます/);
  assert.match(source, /focusIndex - Math\.floor\(initialWindowSize \/ 2\)/);
  assert.match(source, /visible: true, locked: true, panelKind: 'm5'/);
  assert.match(source, /function loadEntryFocusBatchProjection/);
  assert.match(source, /cases\) \? batchRun\.cases/);
  assert.match(source, /batch_focus: true/);
  assert.match(source, /focused \? '選択' : 'NEW'/);
  console.log('PASS entry_result_chart_url_navigation_v0_1');
}).catch(err => {
  console.error(err);
  process.exitCode = 1;
});
