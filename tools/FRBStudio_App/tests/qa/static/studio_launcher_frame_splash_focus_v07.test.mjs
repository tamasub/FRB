import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';

const form = fs.readFileSync('NativeShell/NativeShellForm.cs', 'utf8');
const keyboard = fs.readFileSync('wwwroot/js/runtime/studio_keyboard_standard.js', 'utf8');

test('launcher adds 5px outer rim plus 1px inner line without changing default Studio', () => {
  assert.match(form, /if \(_launcherPresentation && _nativeTitleBarLaunchPalette\)\s*\{\s*Padding = new Padding\(5\)/);
  assert.match(form, /_clientSurface\.Padding = new Padding\(1\)/);
  assert.match(form, /_clientSurface\.Controls\.Add\(_webView\)/);
  assert.match(form, /_clientSurface\.Controls\.Add\(_status\)/);
  assert.match(form, /_clientSurface\.Padding = new Padding\(0\)/);
});

test('splash uses a rounded face, shadow, Studio font family and centered labels', () => {
  assert.match(form, /private sealed class StartupSplashForm : Form/);
  assert.match(form, /Font\("Segoe UI", 10\.5f/);
  assert.match(form, /TextFormatFlags\.HorizontalCenter[\s\S]*?TextFormatFlags\.VerticalCenter/);
  assert.match(form, /classStyle/i); // Windows class style (shadow)
  assert.match(form, /ClassStyle \|= 0x00020000/);
  assert.match(form, /Region = new Region\(path\)/);
  assert.match(form, /new LinearGradientBrush/);
});

test('mouse and keyboard launch: native command and page converge to the unsaved guard', () => {
  assert.match(form, /protected override bool ProcessCmdKey\(ref Message msg, Keys keyData\)/);
  assert.match(form, /keyData == \(Keys\.Control \| Keys\.Q\)/);
  assert.match(form, /ExecuteScriptAsync\([\s\S]*?window\.__frbStudioRequestClose\?\.\(\)/);
  assert.match(form, /if \(_webView\.CanFocus\) _webView\.Focus\(\);/);
  assert.match(keyboard, /window\.__frbStudioRequestClose = requestStudioClose/);
  assert.match(keyboard, /await guard\.confirmNavigationAway\('exit'\)/);
  assert.match(form, /BeginInvoke\(new Action\(Close\)\)/);
});
