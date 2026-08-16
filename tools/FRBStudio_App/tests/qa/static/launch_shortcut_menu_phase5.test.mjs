import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';

const ROOT = process.cwd();
const read = rel => fs.readFileSync(path.join(ROOT, rel), 'utf8');
const readJson = rel => JSON.parse(read(rel));

const shellPath = 'wwwroot/js/ui/frb_studio_shell.js';
const shellJs = read(shellPath);
const css = read('wwwroot/css/frb-studio-shell.css');
const detailSave = read('wwwroot/js/runtime/detail_save.js');
const settings = readJson('wwwroot/config/app_settings.json');
const incident = readJson('data/json/01_main/_studio_work_incident_data_v2.json');

function shellSandbox() {
  const sandbox = {
    console,
    URL,
    URLSearchParams,
    location: {
      href: 'http://127.0.0.1:8765/mdViewer.html',
      pathname: '/mdViewer.html'
    },
    window: {}
  };
  vm.createContext(sandbox);
  vm.runInContext(shellJs, sandbox, { filename: shellPath });
  return sandbox;
}

test('Phase 5 places the shortcut trigger in the common pagebar rather than the dark module topbar', () => {
  const topbarStart = shellJs.indexOf('function buildTopbar');
  const pagebarStart = shellJs.indexOf('function buildPagebar');
  const syncStart = shellJs.indexOf('function syncStickyOffsets');
  const topbarSource = shellJs.slice(topbarStart, pagebarStart);
  const pagebarSource = shellJs.slice(pagebarStart, syncStart);

  assert.doesNotMatch(topbarSource, /data-frb-shortcuts/);
  assert.match(pagebarSource, /data-frb-shortcuts/);
  assert.match(pagebarSource, />ショートカット</);
  assert.match(pagebarSource, /data-frb-home/);
});

test('Phase 5 reads launch_shortcuts from canonical app_settings and keeps the launcher available to every Common Shell page', () => {
  assert.match(shellJs, /const APP_SETTINGS_URL = 'config\/app_settings\.json'/);
  assert.match(shellJs, /settings\?\.launch_shortcuts/);
  assert.match(shellJs, /fetch\(APP_SETTINGS_URL, \{ cache: 'no-store' \}\)/);
  assert.match(shellJs, /void refreshLaunchShortcuts\(pagebar\)/);
  assert.ok(Array.isArray(settings.launch_shortcuts));
});

test('Shortcut href normalizes Windows separators and launches the existing JSON Object Studio URL contract', () => {
  const sandbox = shellSandbox();
  const shortcutHref = sandbox.window.FrbStudioShell.shortcutHref;
  const href = shortcutHref({
    id: 'incident',
    caption: 'Incident',
    data: 'data\\json\\01_main\\incident.json',
    view_def: ''
  });
  const url = new URL(href);
  assert.equal(url.pathname, '/index.html');
  assert.equal(url.searchParams.get('data'), 'data/json/01_main/incident.json');
  assert.equal(url.searchParams.has('view'), false);
});

test('Shortcut href passes an explicitly configured ViewDef but rejects external or traversal paths', () => {
  const sandbox = shellSandbox();
  const shortcutHref = sandbox.window.FrbStudioShell.shortcutHref;
  const href = shortcutHref({
    data: 'data/json/01_main/incident.json',
    view_def: 'rules/studio_work_incident_view_def_v0_5.json'
  });
  const url = new URL(href);
  assert.equal(url.searchParams.get('view'), 'rules/studio_work_incident_view_def_v0_5.json');
  assert.throws(() => shortcutHref({ data: 'https://example.com/x.json', view_def: '' }), /外部URL/);
  assert.throws(() => shortcutHref({ data: '../x.json', view_def: '' }), /パスが不正/);
});

test('Group Navigation keeps its outer full height while its title and buttons stay top-aligned at normal height', () => {
  assert.match(css, /> \.section-group-navigation \{[\s\S]*align-self:stretch;[\s\S]*height:100%/);
  assert.match(css, /\.section-group-navigation \{[\s\S]*display:flex;[\s\S]*flex-direction:column;[\s\S]*justify-content:flex-start/);
  assert.match(css, /\.section-group-navigation-list \{[\s\S]*display:flex;[\s\S]*flex-direction:column;[\s\S]*justify-content:flex-start/);
  assert.match(css, /\.section-group-navigation-item \{[\s\S]*padding:9px 10px/);
});

test('Saving app_settings refreshes the common shortcut menu and studio_work_0198 owns Phase 5', () => {
  assert.match(detailSave, /FrbStudioShell\?\.refreshLaunchShortcuts/);
  const item = incident.work_items.find(row => row.work_item_id === 'studio_work_0198');
  assert.ok(item);
  assert.equal(item.phase, 'v0.18.76-launch-shortcut-menu-phase5');
});


test('Settings mode rethemes the page and marks the gear settings button as the active shell entry', () => {
  const runtime = read('wwwroot/js/runtime/load_runtime.js');
  assert.match(runtime, /pageIcon\.textContent = '⚙'/);
  assert.match(runtime, /pageIcon\.classList\.add\('frb-icon-settings'\)/);
  assert.match(runtime, /settingsLink\?\.classList\.add\('is-active'\)/);
  assert.match(css, /body\.studio-settings-mode \.frb-shell-nav-link\.is-active::after \{/);
  assert.match(css, /\.frb-shell-utility-link\.is-active::after \{/);
});

test('Shortcut launch uses API loading for managed data paths outside static hosting', () => {
  const runtime = read('wwwroot/js/runtime/load_runtime.js');
  assert.match(runtime, /if \(managedName && isStaticHostingMode\(\)\)/);
  assert.match(runtime, /const loaded = await fetchApiJsonWithUrl\('data', managedName\)/);
  assert.match(runtime, /defObj: await fetchResolvedViewDef\(managedName\)/);
});


test('Shortcut managed data path strips data/json before calling Native /api/data', () => {
  const runtime = read('wwwroot/js/runtime/load_runtime.js');
  const start = runtime.indexOf('function staticJsonKindPath');
  const end = runtime.indexOf('function launchApiNameFromStaticPath');
  assert.ok(start >= 0 && end > start, 'staticJsonKindPath source must exist');

  const source = runtime.slice(start, end);
  const sandbox = {};
  vm.createContext(sandbox);
  vm.runInContext(`${source}; this.staticJsonKindPath = staticJsonKindPath;`, sandbox);

  assert.equal(
    sandbox.staticJsonKindPath('data/json/01_main/_studio_work_incident_data_v2.json', 'data'),
    '01_main/_studio_work_incident_data_v2.json'
  );
  assert.equal(
    sandbox.staticJsonKindPath('defs/rules/studio_work_incident_view_def_v0_5.json', 'defs'),
    'rules/studio_work_incident_view_def_v0_5.json'
  );
});
