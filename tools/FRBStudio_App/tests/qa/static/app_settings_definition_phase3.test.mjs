import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';

const ROOT = process.cwd();
const read = rel => fs.readFileSync(path.join(ROOT, rel), 'utf8');
const readJson = rel => JSON.parse(read(rel));

const settings = readJson('wwwroot/config/app_settings.json');
const viewDef = readJson('wwwroot/config/app_settings/app_settings_view_def_v0_1.json');
const fieldDefs = readJson('wwwroot/config/app_settings/app_settings_field_definitions_v0_1.json');
const shellJs = read('wwwroot/js/ui/frb_studio_shell.js');
const loadRuntime = read('wwwroot/js/runtime/load_runtime.js');
const incident = readJson('data/json/01_main/_studio_work_incident_data_v2.json');

test('App Settings keeps default_launch retired and stores current launch shortcuts explicitly', () => {
  assert.equal(Object.hasOwn(settings, 'default_launch'), false);
  assert.ok(Array.isArray(settings.launch_shortcuts));
  assert.ok(settings.launch_shortcuts.length >= 1);
  const ids = settings.launch_shortcuts.map(item => item.id);
  assert.equal(new Set(ids).size, ids.length);
  assert.ok(settings.launch_shortcuts.every(item => item.id && item.caption && item.data));
  assert.equal(settings.markdown.large_file_warning_enabled, true);
  assert.equal(settings.markdown.large_file_warning_bytes, 524288);
});

test('System App Settings ViewDef uses sectionGroups to pinch existing Grid and Form Sections', () => {
  const view = viewDef.views?.[0];
  assert.equal(view?.id, 'appSettings');
  assert.deepEqual(view.sectionGroups, [
    { id: 'launch', caption: 'JSON Object Studio', sectionIds: ['launchShortcuts'] },
    { id: 'markdown', caption: 'Markdown Studio', sectionIds: ['markdownSettings'] }
  ]);
  const sections = new Map(view.sections.map(section => [section.id, section]));
  assert.equal(sections.get('launchShortcuts')?.type, 'grid');
  assert.equal(sections.get('launchShortcuts')?.dataPath, 'launch_shortcuts');
  assert.equal(sections.get('markdownSettings')?.type, 'form');
  assert.equal(sections.get('markdownSettings')?.dataPath, 'markdown');
});

test('System App Settings Field Definition covers only settings intentionally exposed in Phase 3', () => {
  assert.equal(fieldDefs.document_type, 'field_definition');
  assert.equal(fieldDefs.definition_id, 'frb.studio.app_settings');
  assert.equal(fieldDefs.field_definition_count, fieldDefs.field_definitions.length);
  const paths = fieldDefs.field_definitions.map(item => item.field_path);
  assert.deepEqual(paths, [
    '$.launch_shortcuts[].id',
    '$.launch_shortcuts[].caption',
    '$.launch_shortcuts[].data',
    '$.launch_shortcuts[].view_def',
    '$.markdown.large_file_warning_enabled',
    '$.markdown.large_file_warning_bytes'
  ]);
  assert.equal(paths.some(value => value.startsWith('$.hosting.')), false);
  assert.equal(paths.some(value => value.startsWith('$.ui.')), false);
});

test('Common Shell exposes Settings as a separate trigger into the existing JSON Object Studio editor', () => {
  assert.match(shellJs, /data-frb-settings/);
  assert.match(shellJs, /href="index\.html\?mode=settings"/);
  assert.match(shellJs, /Studio設定を開く/);
});

test('mode=settings keeps the fixed System Data/ViewDef trigger while later phases may evolve the save contract', () => {
  assert.match(loadRuntime, /SYSTEM_APP_SETTINGS_DATA_PATH = 'config\/app_settings\.json'/);
  assert.match(loadRuntime, /SYSTEM_APP_SETTINGS_VIEW_DEF_PATH = 'config\/app_settings\/app_settings_view_def_v0_1\.json'/);
  assert.match(loadRuntime, /async function loadSystemAppSettings\(\)/);
  assert.match(loadRuntime, /mode: 'settings'/);
  assert.match(loadRuntime, /await loadFromObjects\([\s\S]*defObj,[\s\S]*dataObj/);
  assert.match(loadRuntime, /String\(mode\)\.trim\(\)\.toLowerCase\(\) === 'settings'/);
});

test('studio_work_0196 remains the Phase 3 owner for App Settings Definition work', () => {
  const item = incident.work_items.find(row => row.work_item_id === 'studio_work_0196');
  assert.ok(item);
  assert.equal(item.phase, 'v0.18.74-app-settings-definition-phase3');
  assert.match(item.objective, /launch_shortcuts/);
  assert.match(item.scope, /System側Settings ViewDef \/ Field Definition/);
});
