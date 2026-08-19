import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';

const bridgeSource = fs.readFileSync('wwwroot/js/core/native_host_bridge.js', 'utf8');
const indexHtml = fs.readFileSync('wwwroot/index.html', 'utf8');

function createNativeBridgeHarness(options = {}) {
  const calls = [];
  let messageHandler = null;
  const manifest = options.manifest ?? { overlay_id: 'default', status: 'active' };
  const overlayFiles = options.overlayFiles ?? [];

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
            content: JSON.stringify(manifest)
          };
        } else if (target.endsWith('.js')) {
          result = {
            path: target,
            content: 'window.__overlayPluginLoaded = true;'
          };
        } else {
          result = {
            path: target,
            content: JSON.stringify({ source_path: target })
          };
        }
      } else if (request.command === 'file.list') {
        result = {
          items: overlayFiles.map(path => ({ path, name: path.split('/').pop(), is_directory: false, size: 1 }))
        };
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

test('NativeShell overlay manifest expands declared wildcard data files to concrete files', async () => {
  const { windowObject, calls } = createNativeBridgeHarness({
    manifest: {
      overlay_id: 'gpt_fx_lab',
      status: 'active',
      data_files: [
        'data/fx_usdjpy_m5_t3_data_v0_1.json',
        'simulattion_集計/batch_*_entry_results.json'
      ]
    },
    overlayFiles: [
      'studio_overlays/gpt_fx_lab/data/fx_usdjpy_m5_t3_data_v0_1.json',
      'studio_overlays/gpt_fx_lab/simulattion_集計/batch_20260717_203022_entry_results.json',
      'studio_overlays/gpt_fx_lab/simulattion_集計/batch_20260720_094623_entry_results.json',
      'studio_overlays/gpt_fx_lab/simulattion_集計/batch_20260720_094623_summary.csv'
    ]
  });

  const response = await windowObject.fetch('/api/overlays/gpt_fx_lab/manifest');
  const body = await response.json();

  assert.deepEqual(body.data_files, [
    'data/fx_usdjpy_m5_t3_data_v0_1.json',
    'simulattion_集計/batch_20260717_203022_entry_results.json',
    'simulattion_集計/batch_20260720_094623_entry_results.json'
  ]);
  assert.ok(!body.data_files.some(path => path.includes('*')));
  assert.equal(calls[0].payload.path, 'studio_overlays/gpt_fx_lab/studio_manifest.json');
  assert.equal(calls[1].command, 'file.list');
  assert.equal(calls[1].payload.path, 'studio_overlays/gpt_fx_lab');
  assert.equal(calls[1].payload.recursive, true);
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

test('NativeShell generic overlay file API can return plugin JavaScript through fetch bridge', async () => {
  const { windowObject, calls } = createNativeBridgeHarness();
  const response = await windowObject.fetch('/api/overlays/gpt_fx_lab/plugins/fx_chart_viewer/plugin.js');

  assert.equal(response.status, 200);
  assert.match(response.headers.get('content-type') ?? '', /application\/javascript/);
  assert.equal(await response.text(), 'window.__overlayPluginLoaded = true;');
  assert.equal(calls[0].payload.path, 'studio_overlays/gpt_fx_lab/plugins/fx_chart_viewer/plugin.js');
});

test('index.html cache-busts the repaired NativeShell overlay runtime scripts', () => {
  assert.match(indexHtml, /js\/core\/native_host_bridge\.js\?v=native-overlay-runtime-01894/);
  assert.match(indexHtml, /js\/core\/plugin_host\.js\?v=native-overlay-runtime-01894/);
});
