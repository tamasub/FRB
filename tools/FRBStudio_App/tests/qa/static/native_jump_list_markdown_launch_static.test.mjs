import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(here, '../../..');
const read = rel => fs.readFileSync(path.join(root, rel), 'utf8');
const readJson = rel => JSON.parse(read(rel));

const program = read('NativeShell/Program.cs');
const launchOptions = read('NativeShell/NativeLaunchOptions.cs');
const jumpList = read('NativeShell/JumpListManager.cs');
const shellForm = read('NativeShell/NativeShellForm.cs');
const readme = read('NativeShell/README.md');
const incident = readJson('data/json/01_main/_studio_work_incident_data_v2.json');

test('Native Shell accepts the Markdown direct-launch argument without creating a second executable', () => {
  assert.match(program, /Main\(string\[\] args\)/);
  assert.match(program, /NativeLaunchOptions\.Parse\(args\)/);
  assert.match(program, /new NativeShellForm\(initialPage:\s*launchOptions\.InitialPage\)/);
  assert.match(launchOptions, /--launch=/);
  assert.match(launchOptions, /string\.Equals\(target, "markdown"/);
  assert.match(launchOptions, /options\.InitialPage = "mdViewer\.html"/);
});

test('Markdown direct launch is resolved against the configured Native Shell virtual host only after config load', () => {
  assert.match(shellForm, /private readonly string _initialPage/);
  assert.match(shellForm, /_allowedOrigin = "https:\/\/" \+ _config\.VirtualHostName/);
  assert.match(shellForm, /_allowedOrigin \+ "\/" \+ ResolveInitialPage\(webRoot\)\.TrimStart\('\/'\)/);
  assert.match(shellForm, /candidate\.IndexOf\("\.\."/);
  assert.match(shellForm, /Uri\.TryCreate\(candidate, UriKind\.Absolute/);
  assert.match(shellForm, /File\.Exists\(candidatePath\)/);
});

test('Windows Jump List adds a task that launches Markdown Studio through the same Native Shell executable', () => {
  assert.match(program, /JumpListManager\.TryInstall\(\)/);
  assert.match(jumpList, /ICustomDestinationList/);
  assert.match(jumpList, /AddUserTasks/);
  assert.match(jumpList, /Application\.ExecutablePath/);
  assert.match(jumpList, /"--launch=markdown"/);
  assert.match(jumpList, /"Markdown Studioを開く"/);
  assert.match(jumpList, /PkeyTitle/);
  assert.match(jumpList, /SetArguments\(arguments\)/);
  assert.match(jumpList, /CommitList\(\)/);
});

test('Jump List failure is isolated from normal FRB Studio startup', () => {
  assert.match(jumpList, /catch\s*\{[\s\S]*destinationList\?\.AbortList\(\)/);
  assert.match(jumpList, /Jump List is a convenience entry point\. It must never block FRB Studio startup/);
  assert.match(readme, /may not show the custom task until the updated Native Shell has been launched at least once/);
});


test('studio_work_0215 records the Native Jump List Markdown direct-launch responsibility', () => {
  const item = incident.work_items.find(row => row.work_item_id === 'studio_work_0215');
  assert.ok(item);
  assert.equal(item.phase, 'v0.18.98-native-jump-list-markdown-launch');
  assert.match(item.expected_outputs, /Markdown Studioを開く/);
  assert.match(item.verification_log, /Windows.*PENDING|PENDING.*Windows/);
});
