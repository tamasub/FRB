import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';

const form = fs.readFileSync('NativeShell/NativeShellForm.cs', 'utf8');
const app = fs.readFileSync('wwwroot/app.js', 'utf8');
const bounds = fs.readFileSync('NativeShell/NativeShellWindowBounds.cs', 'utf8');

test('top-level NativeShell stays transparent until startup ready, popup windows unaffected', () => {
  assert.match(form, /_useStartupSplash = sharedEnvironment == null && !deferInitialNavigation;/);
  assert.match(form, /if \(_useStartupSplash\)\s*\{\s*Opacity = 0;\s*ShowInTaskbar = false;/);
  assert.match(form, /Shown \+= async \(_, __\) => \{\s*ShowStartupSplash\(\);\s*await EnsureInitializedAsync\(\);/);
  assert.match(form, /Text = "FRB Studio  起動中\.\.\./);
});

test('native window only appears after profile sizing and web app initialization', () => {
  assert.match(app, /await autoLoadFromQuery\(\);[\s\S]*?studio_startup_ready: true/);
  assert.match(app, /\} finally \{[\s\S]*?studio_startup_ready: true/);
  assert.match(form, /message\.TryGetValue\("studio_startup_ready", out var readyValue\)/);
  assert.match(form, /ApplyNativePresentation\(get\("preset"\), get\("theme"\), get\("shell"\)\)/);
  assert.match(form, /BeginInvoke\(new Action\(RevealMainWindow\)\)/);
  assert.match(form, /PerformLayout\(\);\s*_webView\.PerformLayout\(\);\s*Opacity = 1;/);
  assert.match(form, /SetNativeTitleBarDark\(_nativeTitleBarDark, _nativeTitleBarLaunchPalette, _nativeTitleBarLaunchLightPalette\)/);
  assert.match(form, /NativeShellWindowBounds\.TryLoad\(out var bounds\)/);
  assert.match(bounds, /launcher_window_bounds\.json/);
});

test('startup splash closes on success or errors; non-index tools are not left invisible', () => {
  assert.match(form, /_startupDeadline = new Timer \{ Interval = 20000 \}/);
  assert.match(form, /_startupDeadline\.Tick \+= \(_, __\) => RevealMainWindow\(\)/);
  assert.match(form, /NavigationCompleted \+=/);
  assert.match(form, /!page\.EndsWith\("\/index\.html"/);
  assert.match(form, /if \(!_useStartupSplash \|\| _startupRevealed \|\| IsDisposed\) return;/);
  assert.match(form, /_startupSplash\?\.Close\(\)/);
  assert.match(form, /_startupSplash\?\.Dispose\(\)/);
  assert.match(form, /catch \(Exception ex\)\s*\{\s*\/\/ Close the splash before opening a modal error dialog\.\s*RevealMainWindow\(\);\s*_status\.Text = "起動失敗/);
});

test('launcher keeps compact bounds on theme changes, without a Standard layout switch', () => {
  assert.doesNotMatch(app, /通常表示に戻す/);
  assert.match(form, /if \(_presentationReceived && \(!_launcherPresentation \|\| !launcher\)\) return;/);
  assert.match(form, /if \(!launcher \|\| !firstPresentation\) return;/);
});
