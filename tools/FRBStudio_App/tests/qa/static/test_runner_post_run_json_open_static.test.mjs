import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const repoRoot = path.resolve(path.dirname(__filename), '../../..');

const readText = (rel) => fs.readFileSync(path.join(repoRoot, rel), 'utf8');
const readJson = (rel) => JSON.parse(readText(rel).replace(/^\uFEFF/, ''));

test('wait型Test Runnerはoutput_artifact_pathをJSON Object Studioで開く契約を持つ', () => {
  const source = readText('wwwroot/js/actions/action_registry.js');
  assert.match(source, /function scheduleTestOutputArtifactOpen\(/);
  assert.match(source, /commandProfileRowValue\(row, 'output_artifact_path'\)/);
  assert.match(source, /new URL\('index\.html', location\.href\)/);
  assert.match(source, /fetchApiJsonWithUrl\('data', apiName\)/);
  assert.match(source, /relativePath\.startsWith\('data\/json\/'\)/);
  assert.doesNotMatch(source, /new URL\(relativePath, location\.href\)/);
  const indexHtml = readText('wwwroot/index.html');
  assert.match(indexHtml, /action_registry\.js\?v=01887-test-run-post-json-api-fix/);
  assert.match(source, /url\.searchParams\.set\('data', relativeJsonPath\)/);
  assert.match(source, /\['test_passed', 'test_failed'\]/);
  assert.match(source, /isCommandProfileLaunchResult\(result\).*return false/);
});

test('Test Runner ViewDefはoutput_artifact_pathを完了後に開くJSONとして編集可能にする', () => {
  const viewDef = readJson('defs/tools/test_runner_run_config_view_def_v0_1.json');
  const fields = viewDef.views.flatMap(view => (view.sections ?? []).flatMap(section => section.fields ?? []));
  const field = fields.find(item => item.field === 'output_artifact_path');
  assert.ok(field, 'output_artifact_path field is required');
  assert.equal(field.caption, '完了後に開くJSON');
  assert.equal(field.readonly, false);
  assert.equal(field.edit?.readonly, false);
  assert.match(field.description ?? '', /wait/);
  assert.match(field.description ?? '', /JSON Object Studio/);
});

test('爆速デモショートカットはwait型Run Config IDまで固定して起動する', () => {
  const settings = readJson('wwwroot/config/app_settings.json');
  const shortcut = settings.launch_shortcuts.find(item => item.id === 'test_demo_incident_prompt');
  assert.ok(shortcut, 'demo shortcut is required');
  assert.equal(shortcut.data.replaceAll('\\', '/'), 'data/json/04_tools/test_runner_run_config_data_v0_1.json');
  assert.equal(shortcut.view_def, 'tools/test_runner_run_config_view_def_v0_1.json');
  assert.equal(shortcut.launch_params?.focusField, 'run_config_id');
  assert.equal(shortcut.launch_params?.focusValue, 'test_run_002_incident_prompt_copy_action_static');
  assert.equal(shortcut.launch_params?.action, 'RunCommandProfile');

  const runConfig = readJson('data/json/04_tools/test_runner_run_config_data_v0_1.json');
  const row = runConfig.run_configs.find(item => item.run_config_id === shortcut.launch_params.focusValue);
  assert.ok(row, 'shortcut target Run Config must exist');
  assert.equal(row.run_mode, 'wait');
  assert.ok(String(row.output_artifact_path ?? '').endsWith('.json'));
});

test('Diff JSON Viewerの保存ボタンはファイル選択・文字コードと同一コントロール列に置く', () => {
  const html = readText('wwwroot/DiffJsonViewer.html');
  assert.match(html, /class="file-open-controls"[\s\S]*id="jsonFile"[\s\S]*id="jsonEncoding"[\s\S]*id="saveAsBtn"/);
  assert.doesNotMatch(html, /class="save-as-group"/);
  assert.match(html, /\.file-open-controls\{display:grid;grid-template-columns:/);
  assert.doesNotMatch(html, /\.file-open-controls\{[^}]*flex-wrap:wrap/);
  assert.match(html, /\.file-open-controls select,\.file-open-controls button\{white-space:nowrap\}/);
});
