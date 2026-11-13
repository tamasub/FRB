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
const runtime = read('wwwroot/js/runtime/load_runtime.js');
const settings = readJson('wwwroot/config/app_settings.json');
const incident = readJson('data/json/01_main/_studio_work_incident_data_v2.json');

function shellSandbox() {
  const sandbox = {
    console,
    URL,
    URLSearchParams,
    location: {
      href: 'http://127.0.0.1:8765/index.html',
      pathname: '/index.html'
    },
    window: {}
  };
  vm.createContext(sandbox);
  vm.runInContext(shellJs, sandbox, { filename: shellPath });
  return sandbox;
}

test('v0.18.77 registers Git Diff WorkingTree shortcut with generic focus/action launch_params', () => {
  const shortcut = settings.launch_shortcuts.find(item => item.id === 'gitdiff_working_tree');
  assert.ok(shortcut);
  assert.equal(shortcut.data.replaceAll('\\', '/'), 'data/json/04_tools/git_diff_export_run_config_data_v0_1.json');
  assert.equal(shortcut.view_def, 'tools/git_diff_export_run_config_view_def_v0_1.json');
  assert.deepEqual(shortcut.launch_params, {
    focusField: 'run_config_id',
    focusValue: 'gitdiff_001_default_working_tree',
    openDetail: false,
    action: 'RunCommandProfile'
  });
});

test('shortcutHref appends only the supported generic launch_params to the existing JSON Object Studio URL contract', () => {
  const shortcutHref = shellSandbox().window.FrbStudioShell.shortcutHref;
  const href = shortcutHref({
    data: 'data/json/04_tools/git_diff_export_run_config_data_v0_1.json',
    view_def: 'tools/git_diff_export_run_config_view_def_v0_1.json',
    launch_params: {
      focusField: 'run_config_id',
      focusValue: 'gitdiff_001_default_working_tree',
      openDetail: false,
      action: 'RunCommandProfile',
      ignoredParam: 'must-not-leak'
    }
  });
  const url = new URL(href);
  assert.equal(url.pathname, '/index.html');
  assert.equal(url.searchParams.get('data'), 'data/json/04_tools/git_diff_export_run_config_data_v0_1.json');
  assert.equal(url.searchParams.get('view'), 'tools/git_diff_export_run_config_view_def_v0_1.json');
  assert.equal(url.searchParams.get('focusField'), 'run_config_id');
  assert.equal(url.searchParams.get('focusValue'), 'gitdiff_001_default_working_tree');
  assert.equal(url.searchParams.get('openDetail'), 'false');
  assert.equal(url.searchParams.get('action'), 'RunCommandProfile');
  assert.equal(url.searchParams.has('ignoredParam'), false);
});

test('launch_params remain optional so existing shortcuts keep the previous URL shape', () => {
  const shortcutHref = shellSandbox().window.FrbStudioShell.shortcutHref;
  const href = shortcutHref({
    data: 'data/json/01_main/_studio_work_incident_data_v2.json',
    view_def: ''
  });
  const url = new URL(href);
  assert.equal(url.searchParams.has('focusField'), false);
  assert.equal(url.searchParams.has('focusValue'), false);
  assert.equal(url.searchParams.has('action'), false);
});

test('URL action context receives the row selected by URL focus and the current executeButton definition', () => {
  assert.match(runtime, /const selectedRow = selectedIndex >= 0 && Array\.isArray\(currentRows\)/);
  assert.match(runtime, /const executeButton = typeof viewExecuteButtonDef === 'function' \? viewExecuteButtonDef\(\) : null;/);
  assert.match(runtime, /currentStudioActionContext\(\{[\s\S]*selectedRow,[\s\S]*executeButton/);
  const focusCall = runtime.indexOf('applyLaunchFocusFromQuery(params);');
  const actionCall = runtime.indexOf('await executeLaunchActionFromQuery(params);');
  assert.ok(focusCall >= 0 && actionCall > focusCall, 'URL focus must run before URL action');
});

test('studio_work_0199 explicitly leaves launch_params Settings UI editing as follow-up work', () => {
  const item = incident.work_items.find(row => row.work_item_id === 'studio_work_0199');
  assert.ok(item);
  assert.equal(item.phase, 'v0.18.77-launch-shortcut-focus-action');
  assert.match(item.objective, /gitdiff_001_default_working_tree/);
  assert.match(item.out_of_scope, /Settings画面からlaunch_params/);
  const follow = item.follow_up_actions.find(action => action.action_type === 'SETTINGS_SHORTCUT_LAUNCH_PARAMS_UI');
  assert.ok(follow);
  assert.equal(follow.status, 'PENDING');
});
