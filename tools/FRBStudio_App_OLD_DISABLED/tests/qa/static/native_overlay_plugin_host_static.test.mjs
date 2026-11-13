import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';

const source = fs.readFileSync('wwwroot/js/core/plugin_host.js', 'utf8');

test('NativeShell PluginHost loads overlay plugin scripts through bridged fetch', () => {
  assert.match(source, /function nativeHostBridgeAvailable\(\)/);
  assert.match(source, /window\.FRBStudioNativeHost\?\.isAvailable\?\.\(\) === true/);
  assert.match(source, /async function loadScriptThroughFetch\(url, meta = \{\}\)/);
  assert.match(source, /const response = await fetch\(url, \{ cache: 'no-store' \}\)/);
  assert.match(source, /script\.textContent = `\$\{source\}\\n\/\/# sourceURL=\$\{url\}`/);
  assert.match(source, /if \(nativeHostBridgeAvailable\(\)\) \{/);
});

test('Browser/static mode keeps the existing script src loading path', () => {
  assert.match(source, /script\.src = primaryUrl/);
  assert.match(source, /fallback\.src = fallbackUrl/);
});
