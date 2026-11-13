import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';

const form = fs.readFileSync('NativeShell/NativeShellForm.cs', 'utf8');
const program = fs.readFileSync('NativeShell/Program.cs', 'utf8');
const options = fs.readFileSync('NativeShell/NativeLaunchOptions.cs', 'utf8');

test('studio startup appearance hint reaches splash before WebView2 initialization', () => {
  assert.match(options, /--studio-theme=/);
  assert.match(program, /startupTheme: launchOptions\.StudioTheme/);
  assert.match(form, /_startupSplashLight = string\.Equals\(startupTheme, "light"/);
  assert.match(form, /new StartupSplashForm\(_startupSplashLight\)/);
});

test('splash uses distinct light and dark palettes without altering visibility and sizing', () => {
  assert.match(form, /internal StartupSplashForm\(bool light\)/);
  assert.match(form, /_light \? Color\.FromArgb\(246, 250, 247\) : Color\.FromArgb\(32, 43, 41\)/);
  assert.match(form, /internal void SetAppearance\(bool light\)/);
  assert.match(form, /if \(launcher\)\s*\(_startupSplash as StartupSplashForm\)\?\.SetAppearance\(!dark\)/);
  assert.match(form, /ShowStartupSplash\(\);\s*await EnsureInitializedAsync\(\);/);
  assert.match(form, /_startupSplash\?\.Close\(\)/);
  assert.match(form, /ClientSize = new Size\(340, 112\)/);
});
