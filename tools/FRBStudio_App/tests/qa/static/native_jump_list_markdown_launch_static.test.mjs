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
