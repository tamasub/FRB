import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';

const bridgeSource = fs.readFileSync('wwwroot/js/core/native_host_bridge.js', 'utf8');
const indexHtml = fs.readFileSync('wwwroot/index.html', 'utf8');

function createNativeBridgeHarness() {
  const calls = [];
  let messageHandler = null;

  const webview = {
    addEventListener(type, handler) {
      if (type === 'message') messageHandler = handler;
    },
    postMessage(request) {
      calls.push(request);
      assert.ok(messageHandler, 'native bridge message listener must be registered');

      let result = {};
      if (request.command === 'file.readText') {
        const target = String(request.payload?.path ?? '');
        if (target.endsWith('/studio_manifest.json')) {
          result = {
            path: target,
            content: JSON.stringify({ overlay_id: 'default', status: 'active' })
          };
        } else {
          result = {
            path: target,
            content: JSON.stringify({ source_path: target })
          };
        }
      }

      messageHandler({
        data: {
          request_id: request.request_id,
          success: true,
          result
        }
      });
    }
  };

  const windowObject = {
    chrome: { webview },
    location: {
      href: 'https://frb-studio.local/index.html',
      origin: 'https://frb-studio.local'
    },
    fetch: async () => new Response('original fetch should not be used', { status: 599 }),
    setTimeout,
    clearTimeout
  };

  const context = {
    window: windowObject,
    URL,
    Response,
    Request,
    Blob,
    console,
    setTimeout,
    clearTimeout
  };

  vm.runInNewContext(bridgeSource, context, { filename: 'native_host_bridge.js' });
  return { windowObject, calls };
}

test('NativeShell overlay manifest API resolves the manifest alias to studio_manifest.json', async () => {
  const { windowObject, calls } = createNativeBridgeHarness();
  const response = await windowObject.fetch('/api/overlays/default/manifest');

  assert.equal(response.status, 200);
  assert.deepEqual(await response.json(), { overlay_id: 'default', status: 'active' });
  assert.equal(calls.length, 1);
  assert.equal(calls[0].command, 'file.readText');
  assert.equal(calls[0].payload.path, 'studio_overlays/default/studio_manifest.json');
});

test('NativeShell generic overlay file API keeps reading the requested relative file', async () => {
  const { windowObject, calls } = createNativeBridgeHarness();
  const response = await windowObject.fetch('/api/overlays/default/data/company_sample.json');

  assert.equal(response.status, 200);
  assert.deepEqual(await response.json(), {
    source_path: 'studio_overlays/default/data/company_sample.json'
  });
  assert.equal(calls[0].payload.path, 'studio_overlays/default/data/company_sample.json');
});

test('index.html cache-busts the repaired NativeShell bridge', () => {
  assert.match(indexHtml, /js\/core\/native_host_bridge\.js\?v=native-overlay-manifest-01893/);
});
