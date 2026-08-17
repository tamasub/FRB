import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(here, '../../..');
const read = rel => fs.readFileSync(path.join(root, rel), 'utf8');
const readJson = rel => JSON.parse(read(rel).replace(/^\uFEFF/, ''));

test('GitDiff normal output is one current JSON overwritten in place instead of timestamp accumulation', () => {
  const script = read('tools/git/Export-DiffToJson.ps1');
  const nativeConfig = readJson('NativeShell/native_shell.config.json');
  const runConfig = readJson('data/json/04_tools/git_diff_export_run_config_data_v0_1.json');
  const nativeBridge = read('wwwroot/js/core/native_host_bridge.js');
  const gitignore = read('.gitignore');

  assert.match(script, /\$relativeDefault\s*=\s*'wwwroot\/diff\/DiffToJson_current\.json'/);
  assert.match(script, /\$resolvedOutputPath\s*=\s*Resolve-AppRootOutputPath/);
  assert.doesNotMatch(script, /Format-StudioFileTimestamp/);
  assert.doesNotMatch(script, /DiffToJson_\d{8}_\d{6}/);

  const profile = nativeConfig.process_profiles.find(item => item.id === 'git_diff_export');
  assert.ok(profile, 'git_diff_export profile must exist');
  assert.deepEqual(profile.output_globs, ['wwwroot/diff/DiffToJson_current.json']);

  assert.equal(runConfig.output_path_display, 'wwwroot/diff/DiffToJson_current.json');
  assert.match(runConfig.output_path_note, /同じ1ファイルを上書き/);
  assert.doesNotMatch(runConfig.output_path_note, /yyyyMMdd|日時付きJSON.*自動生成(?!しない)/);

  assert.match(nativeBridge, /startsWith\('wwwroot\/diff\/'\)/);
  assert.match(nativeBridge, /DiffJsonViewer\.html\?src=/);
  assert.match(gitignore, /wwwroot\/diff\/\*\.json/);
});
