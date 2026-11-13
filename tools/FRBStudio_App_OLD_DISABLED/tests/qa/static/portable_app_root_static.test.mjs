import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(here, '../../..');
const read = rel => fs.readFileSync(path.join(root, rel), 'utf8');

const operationalFiles = [
  'cmd_make_FRBStudio_App_zip_v2.bat',
  'cmd_compile_NativeShell.bat',
  'tools/build/Build-NativeShell.ps1',
  'tools/git/Export-DiffToJson.ps1',
  'tools/test/TestRunner.ps1',
  'tools/zip/make_FRBStudio_App_zip_v2.ps1',
  'tools/zip/make_studio_overlays_zip_v1.ps1',
  'tools/FileTree/file_list_Tree.bat',
  'wwwroot/count_js_steps_add_datetime.bat'
];

test('PC-portable operational scripts do not embed machine-specific absolute application paths', () => {
  for (const rel of operationalFiles) {
    const source = read(rel);
    assert.doesNotMatch(
      source,
      /(?:^|["'= ])(?:[A-Za-z]:\\(?:Users|FRB|work|src|dev|repo|projects?)\\|[A-Za-z]:\/(?:Users|FRB|work|src|dev|repo|projects?)\/)/im,
      `machine-specific path remained in ${rel}`
    );
    assert.doesNotMatch(source, /F:\\FRB\\tools\\FRBStudio_App/i, `legacy FRBStudio_App path remained in ${rel}`);
  }
});

test('NativeShell compile wrapper resolves from its own location and publishes through the common build script', () => {
  const bat = read('cmd_compile_NativeShell.bat');
  const build = read('tools/build/Build-NativeShell.ps1');

  assert.match(bat, /%~dp0tools\\build\\Build-NativeShell\.ps1/i);
  assert.match(build, /Join-Path \$PSScriptRoot '\.\.\/\.\.'/);
  assert.match(build, /NativeShell\/FRBStudio\.NativeShell\.csproj/);
  assert.match(build, /NativeShell\/_publish/);
  assert.match(build, /Get-Command dotnet/);
  assert.match(build, /StudioLog\.ps1/);
  assert.match(build, /Initialize-StudioLog/);
});

test('package ZIP resolves AppRoot from tools/zip and includes the portable compile wrapper', () => {
  const zipScript = read('tools/zip/make_FRBStudio_App_zip_v2.ps1');

  assert.match(zipScript, /Join-Path \$PSScriptRoot "\.\.\/\.\."/);
  assert.match(zipScript, /"cmd_compile_NativeShell\.bat"/);
  assert.match(zipScript, /"NativeShell\\_publish"/);
  assert.doesNotMatch(zipScript, /\$root\s*=\s*"[A-Za-z]:\\/);
});

test('support BAT files derive targets from their own location', () => {
  const treeBat = read('tools/FileTree/file_list_Tree.bat');
  const countBat = read('wwwroot/count_js_steps_add_datetime.bat');

  assert.match(treeBat, /%~dp0\.\.\\\.\./);
  assert.match(treeBat, /set "APP_ROOT=%%~fI"/);
  assert.match(countBat, /%~dp0\./);
  assert.match(countBat, /set "ROOT=%%~fI"/);
});

test('TestRunner identifies FRBStudio_App with packaged root markers instead of package.json', () => {
  const runner = read('tools/test/TestRunner.ps1');

  assert.match(runner, /wwwroot\/index\.html/);
  assert.match(runner, /data\/json/);
  assert.match(runner, /Join-Path \$Path 'defs'/);
  assert.match(runner, /Join-Path \$Path 'tools'/);
  assert.match(runner, /Join-Path \$Path 'tests'/);
  assert.doesNotMatch(runner, /Join-Path \$Path 'package\.json'/);
  assert.match(runner, /playwright\.config\.ts is required for playwright_ui/);
});
