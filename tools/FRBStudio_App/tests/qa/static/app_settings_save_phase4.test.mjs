import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';

const ROOT = process.cwd();
const read = rel => fs.readFileSync(path.join(ROOT, rel), 'utf8');
const readJson = rel => JSON.parse(read(rel));

function validationSandbox() {
  const sandbox = { console };
  vm.createContext(sandbox);
  [
    'wwwroot/js/services/definition/definition_verification_common.js',
    'wwwroot/js/services/definition/field_contract_resolver.js',
    'wwwroot/js/services/definition/definition_value_validator.js',
    'wwwroot/js/services/definition/definition_document_validator.js'
  ].forEach(file => vm.runInContext(read(file), sandbox, { filename: file }));
  return sandbox;
}

test('Phase 4 grants only the canonical app_settings.json file and does not make wwwroot/config a writable root', () => {
  const config = readJson('NativeShell/native_shell.config.json');
  const configCs = read('NativeShell/NativeShellConfig.cs');
  const policyCs = read('NativeShell/WorkspacePolicy.cs');
  const dispatcherCs = read('NativeShell/NativeCommandDispatcher.cs');

  assert.equal(config.writable_roots.includes('wwwroot'), false);
  assert.equal(config.writable_roots.includes('wwwroot/config'), false);
  assert.deepEqual(config.writable_files, ['wwwroot/config/app_settings.json']);
  assert.match(configCs, /WritableFiles/);
  assert.match(policyCs, /allowedByFile/);
  assert.match(policyCs, /string\.Equals\(relative, file/);
  assert.match(dispatcherCs, /_config\.WritableFiles/);
});

test('Native bridge exposes a fixed /api/app-settings save contract to exactly one System file', () => {
  const bridge = read('wwwroot/js/core/native_host_bridge.js');
  assert.match(bridge, /path === '\/api\/app-settings'/);
  assert.match(bridge, /const settingsPath = 'wwwroot\/config\/app_settings\.json'/);
  assert.match(bridge, /invoke\('file\.writeText',[\s\S]*path: settingsPath/);
  assert.doesNotMatch(bridge, /\/api\/app-settings\/\(\.\+\)/);
});

test('DefinitionDocumentValidator accepts valid exposed App Settings and rejects invalid values from the System Field Definition', () => {
  const sandbox = validationSandbox();
  sandbox.fieldDefs = readJson('wwwroot/config/app_settings/app_settings_field_definitions_v0_1.json');
  sandbox.registry = readJson('data/json/config/validation_type_registry_v0_1.json');
  sandbox.valid = {
    launch_shortcuts: [{ id: 'incident', caption: 'インシデント管理', data: '01_main/x.json', view_def: '' }],
    markdown: { large_file_warning_enabled: true, large_file_warning_bytes: 524288 }
  };
  sandbox.invalid = {
    launch_shortcuts: [{ id: '1bad', caption: '', data: '01_main/x.json', view_def: '' }],
    markdown: { large_file_warning_enabled: 'true', large_file_warning_bytes: 0 }
  };

  const valid = vm.runInContext('new DefinitionDocumentValidator().validate(valid, fieldDefs, registry)', sandbox);
  const invalid = vm.runInContext('new DefinitionDocumentValidator().validate(invalid, fieldDefs, registry)', sandbox);
  assert.equal(valid.status, 'ACCEPT');
  assert.equal(invalid.status, 'REJECT');
  assert.ok(invalid.blocking_checks.length >= 4);
  assert.ok(invalid.blocking_checks.some(check => check.instance_path === '$.launch_shortcuts[0].id'));
  assert.ok(invalid.blocking_checks.some(check => check.instance_path === '$.markdown.large_file_warning_bytes'));
});

test('Settings mode becomes writable only through /api/app-settings and loads System Field Definition validation context', () => {
  const runtime = read('wwwroot/js/runtime/load_runtime.js');
  assert.match(runtime, /SYSTEM_APP_SETTINGS_SAVE_API_PATH = '\/api\/app-settings'/);
  assert.match(runtime, /SYSTEM_APP_SETTINGS_FIELD_DEF_PATH = 'config\/app_settings\/app_settings_field_definitions_v0_1\.json'/);
  assert.match(runtime, /const readonly = typeof isStaticHostingMode/);
  assert.match(runtime, /readonly \? null : SYSTEM_APP_SETTINGS_SAVE_API_PATH/);
  assert.match(runtime, /loadSystemAppSettingsValidationContext\(\)/);
  assert.match(runtime, /currentRuntimeFieldDefinitionDocument = fieldDefinitionDocument/);
  assert.match(runtime, /prepareSystemAppSettingsSaveDocument/);
  assert.match(runtime, /prepared\.updated_at = typeof studioFormatIsoJst/);
});

test('Generic save path preserves App Settings Round Trip and never injects ViewDef metadata into the canonical settings document', () => {
  const save = read('wwwroot/js/runtime/detail_save.js');
  assert.match(save, /const systemAppSettingsMode = typeof isSystemAppSettingsMode/);
  assert.match(save, /if \(!systemAppSettingsMode && currentDataSourceKind !== 'viewdef'\)/);
  assert.match(save, /prepareSystemAppSettingsSaveDocument\(sourceData\)/);
  assert.match(save, /saveDocument = prepared\.document/);
  assert.match(save, /sourceData\.updated_at = saveDocument\.updated_at/);

  const settings = readJson('wwwroot/config/app_settings.json');
  assert.ok(settings.hosting && settings.ui, 'hidden System settings remain part of canonical JSON');
  assert.equal(Object.hasOwn(settings, 'view_def'), false, 'Settings canonical must not gain Data view_def metadata');
});

test('sectionGroup switch commits the active Form through the existing Header edit contract before pinching another Section', () => {
  const navigation = read('wwwroot/js/ui/section_group_navigation.js');
  const applyIndex = navigation.indexOf("if (typeof applyHeaderEdits === 'function') applyHeaderEdits();");
  const switchIndex = navigation.indexOf('activeSectionGroupId = String(target.id);');
  assert.ok(applyIndex >= 0 && switchIndex >= 0 && applyIndex < switchIndex);
});

test('studio_work_0197 records Phase 4 ownership, fixed save boundary, validation, round trip, and verification', () => {
  const incident = readJson('data/json/01_main/_studio_work_incident_data_v2.json');
  const item = incident.work_items.find(row => row.work_item_id === 'studio_work_0197');
  assert.ok(item);
  assert.equal(item.phase, 'v0.18.75-app-settings-save-phase4');
  assert.equal(item.status, '完了');
  assert.match(item.actual_updated_files, /definition_document_validator\.js/);
  assert.match(item.actual_updated_files, /native_shell\.config\.json/);
  assert.match(item.latest_ai_response, /Round Trip/);
  assert.match(item.verification_log, /Phase 4専用Static: 7 \/ 7 PASS/);
});
