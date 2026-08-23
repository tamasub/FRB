import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(here, '../../..');
const read = rel => fs.readFileSync(path.join(root, rel), 'utf8');

const program = read('NativeShell/Program.cs');
const launchOptions = read('NativeShell/NativeLaunchOptions.cs');
const jumpList = read('NativeShell/JumpListManager.cs');
const shellForm = read('NativeShell/NativeShellForm.cs');
const csproj = read('NativeShell/FRBStudio.NativeShell.csproj');

test('NativeShell parses --launch=markdown and opens Markdown Studio directly', () => {
  assert.match(launchOptions, /arg\.StartsWith\("--launch=", StringComparison\.OrdinalIgnoreCase\)/);
  assert.match(launchOptions, /string\.Equals\(value, "markdown", StringComparison\.OrdinalIgnoreCase\)/);
  assert.match(launchOptions, /options\.InitialPage = "mdViewer\.html"/);
  assert.match(program, /var launchOptions = NativeLaunchOptions\.Parse\(args\)/);
  assert.match(program, /Application\.Run\(new NativeShellForm\(initialPage: launchOptions\.InitialPage\)\)/);
  assert.match(shellForm, /private readonly string _initialPage;/);
  assert.match(shellForm, /requestedPageUri = !string\.IsNullOrWhiteSpace\(_initialPage\)/);
  assert.match(shellForm, /_allowedOrigin \+ "\/" \+ _initialPage\.TrimStart\('\/'\)/);
});

test('Jump List registers Markdown Studio task with dedicated Markdown icon', () => {
  assert.match(program, /JumpListManager\.TryRegisterTasks\(\)/);
  assert.match(jumpList, /title:\s*"Markdown Studioを開く"/);
  assert.match(jumpList, /arguments:\s*"--launch=markdown"/);
  assert.match(jumpList, /description:\s*"Markdown Studioを直接開きます。"/);
  assert.match(jumpList, /ResolveMarkdownTaskIconPath\(\)/);
  assert.match(jumpList, /MarkdownStudio\.ico/);
  assert.match(jumpList, /shellLink\.SetIconLocation\(iconPath, iconIndex\)/);
  assert.match(jumpList, /var titleKey = PropertyKey\.Title/);
  assert.match(jumpList, /propertyStore\.SetValue\(ref titleKey, pv\)/);
  assert.doesNotMatch(jumpList, /SetValue\(ref PropertyKey\.Title/);
  assert.match(jumpList, /destinationList\.AddUserTasks\(\(IObjectArray\)tasks\)/);
  assert.match(csproj, /<None Update="MarkdownStudio\.ico">[\s\S]*?<CopyToOutputDirectory>PreserveNewest<\/CopyToOutputDirectory>[\s\S]*?<CopyToPublishDirectory>PreserveNewest<\/CopyToPublishDirectory>/);
});

test('NativeShell publish explicitly carries runtime icon/config assets into _publish', () => {
  assert.match(csproj, /<None Update="FRB_Studio\.ico">[\s\S]*?<CopyToOutputDirectory>PreserveNewest<\/CopyToOutputDirectory>[\s\S]*?<CopyToPublishDirectory>PreserveNewest<\/CopyToPublishDirectory>/);
  assert.match(csproj, /<None Update="native_shell\.config\.json">[\s\S]*?<CopyToPublishDirectory>PreserveNewest<\/CopyToPublishDirectory>/);
  assert.match(csproj, /<None Update="MarkdownStudio\.ico">[\s\S]*?<CopyToPublishDirectory>PreserveNewest<\/CopyToPublishDirectory>/);
});

test('Jump List mirrors configured JSON Object Studio launch_shortcuts without hardcoding individual shortcut IDs', () => {
  const catalog = read('NativeShell/NativeLaunchShortcutCatalog.cs');
  const settings = JSON.parse(read('wwwroot/config/app_settings.json'));

  assert.ok(Array.isArray(settings.launch_shortcuts));
  assert.ok(settings.launch_shortcuts.length > 0, 'fixture must contain configured launch shortcuts');
  assert.match(jumpList, /foreach \(var shortcut in NativeLaunchShortcutCatalog\.Load\(\)\)/);
  assert.match(jumpList, /title:\s*shortcut\.Caption/);
  assert.match(jumpList, /arguments:\s*"--launch-shortcut=" \+ Uri\.EscapeDataString\(shortcut\.Id\)/);
  assert.match(jumpList, /ResolveStudioTaskIconPath\(\)/);
  assert.match(catalog, /Path\.Combine\(appRoot, "wwwroot", "config", "app_settings\.json"\)/);
  assert.match(catalog, /using System\.Web\.Script\.Serialization/);
  assert.match(csproj, /<Reference Include="System\.Web\.Extensions" \/>/);
  assert.match(catalog, /root\.TryGetValue\("launch_shortcuts"/);
  assert.match(catalog, /NormalizeJsonPath\(GetString\(row, "data"\), required: true\)/);
  assert.match(catalog, /NormalizeJsonPath\(GetString\(row, "view_def"\), required: false\)/);

  for (const shortcut of settings.launch_shortcuts) {
    assert.doesNotMatch(jumpList, new RegExp(shortcut.id.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')));
  }
});

test('Taskbar launch shortcut resolves the current app_settings entry into the same index.html query contract as the Common Shell menu', () => {
  const catalog = read('NativeShell/NativeLaunchShortcutCatalog.cs');

  assert.match(launchOptions, /arg\.StartsWith\("--launch-shortcut=", StringComparison\.OrdinalIgnoreCase\)/);
  assert.match(launchOptions, /Uri\.UnescapeDataString\(encodedId\)/);
  assert.match(launchOptions, /NativeLaunchShortcutCatalog\.TryBuildInitialPage\(shortcutId, out var initialPage\)/);
  assert.match(catalog, /return "index\.html\?" \+ string\.Join\("&", query\)/);
  assert.match(catalog, /"data=" \+ Uri\.EscapeDataString\(shortcut\.DataPath\)/);
  assert.match(catalog, /"view=" \+ Uri\.EscapeDataString\(shortcut\.ViewDefPath\)/);
  assert.match(catalog, /"focusField"/);
  assert.match(catalog, /"focusValue"/);
  assert.match(catalog, /"openDetail"/);
  assert.match(catalog, /"action"/);
});

test('studio_work_0224 records the taskbar projection as a NativeShell feature with real-device verification pending', () => {
  const incident = JSON.parse(read('data/json/01_main/_studio_work_incident_data_v2.json'));
  const item = incident.work_items.find(row => row.work_item_id === 'studio_work_0224');
  assert.ok(item);
  assert.equal(item.phase, 'v0.18.107-taskbar-jump-list-launch-shortcuts');
  assert.match(item.objective, /タスクバーアイコン右クリック|タスクバー.*タスク|タスク.*起動/);
  assert.match(item.verification_status, /実機確認待ち/);
});
