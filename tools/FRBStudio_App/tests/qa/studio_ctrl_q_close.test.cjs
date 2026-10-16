// Ctrl+Q should close only the native Studio form, after the unsaved-change check.
// Standalone Node regression test; no WebView2 or GUI dependencies.
const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');

const script = fs.readFileSync('wwwroot/js/runtime/studio_keyboard_standard.js', 'utf8');

function setup({ native = true, guard = true, allowed = true } = {}) {
  let handler;
  const posted = [];
  const calls = [];
  let fallbackResult = true;
  const document = {
    getElementById() { return null; },
    querySelectorAll() { return []; },
    addEventListener(type, callback, capture) {
      if (type === 'keydown') {
        assert.equal(capture, true);
        handler = callback;
      }
    }
  };
  class Element {}
  const window = {
    FRBStudioNativeHost: { isAvailable: () => native },
    chrome: native ? { webview: { postMessage(data) { posted.push(data); } } } : undefined,
    FrbJsonObjectUnsavedGuard: guard ? {
      async confirmNavigationAway(mode) { calls.push(mode); return allowed; }
    } : undefined,
    confirm(message) { calls.push(message); return fallbackResult; }
  };
  vm.runInNewContext(script, { document, Element, window, console, Event, selectedIndex: -1 }, { filename: 'studio_keyboard_standard.js' });
  function send(overrides = {}) {
    const event = {
      target: new Element(), key: 'q', code: 'KeyQ',
      ctrlKey: true, altKey: false, shiftKey: false, metaKey: false,
      isComposing: false, keyCode: 0, defaultPrevented: false, repeat: false,
      preventDefault() { this.defaultPrevented = true; },
      stopImmediatePropagation() { this.stopped = true; },
      ...overrides
    };
    handler(event);
    return event;
  }
  return { send, posted, calls, setFallbackResult(value) { fallbackResult = value; } };
}

async function flush() { await Promise.resolve(); await Promise.resolve(); }

test('Ctrl+Q checks unsaved state and requests a real native close', async () => {
  const ui = setup();
  const key = ui.send();
  assert.equal(key.defaultPrevented, true);
  assert.equal(key.stopped, true);
  await flush();
  assert.deepEqual(ui.calls, ['exit']);
  assert.equal(ui.posted.length, 1);
  assert.equal(ui.posted[0].studio_close_request, true);
  // A second keypress before the form has closed cannot send another request.
  ui.send();
  await flush();
  assert.equal(ui.posted.length, 1);
});

test('Cancel in unsaved confirmation preserves Studio and allows retry', async () => {
  const ui = setup({ allowed: false });
  ui.send();
  await flush();
  assert.deepEqual(ui.posted, []);
  ui.send();
  await flush();
  assert.deepEqual(ui.calls, ['exit', 'exit']);
  assert.deepEqual(ui.posted, []);
});

test('Ordinary browser mode leaves Ctrl+Q untouched', async () => {
  const ui = setup({ native: false });
  assert.equal(ui.send().defaultPrevented, false);
  await flush();
  assert.deepEqual(ui.calls, []);
  assert.deepEqual(ui.posted, []);
});

test('Modifiers, composition, and pre-handled keystrokes are ignored', async () => {
  for (const changes of [
    { shiftKey: true }, { altKey: true }, { metaKey: true },
    { ctrlKey: false }, { isComposing: true }, { defaultPrevented: true },
    { key: 'w', code: 'KeyW' }
  ]) {
    const ui = setup();
    assert.equal(ui.send(changes).stopped, undefined);
    await flush();
    assert.deepEqual(ui.posted, []);
  }
});

test('Auto-repeat never opens extra dialogs', async () => {
  const ui = setup();
  ui.send({ repeat: true });
  await flush();
  assert.deepEqual(ui.calls, []);
  assert.deepEqual(ui.posted, []);
});

test('Missing unsaved guard fails safe by asking before exiting', async () => {
  const ui = setup({ guard: false });
  ui.setFallbackResult(false);
  ui.send();
  await flush();
  assert.equal(ui.posted.length, 0);
  assert.match(ui.calls[0], /未保存/);
});

test('Native handler uses trusted index.html message and real Form.Close()', () => {
  const form = fs.readFileSync('NativeShell/NativeShellForm.cs', 'utf8');
  assert.match(form, /if \(!IsAllowedSource\(e\.Source\)\) return;/);
  assert.match(form, /message\.TryGetValue\("studio_close_request"/);
  assert.match(form, /string\.Equals\(closeSource\.AbsolutePath, "\/index\.html"/);
  assert.match(form, /BeginInvoke\(new Action\(Close\)\)/);
  assert.doesNotMatch(form.slice(form.indexOf('studio_close_request'), form.indexOf('studio_startup_ready')), /\.Hide\(|Visible\s*=\s*false/);
});

test('Unsaved guard exposes an exit-specific confirmation without changing navigation confirmation', () => {
  const guard = fs.readFileSync('wwwroot/js/runtime/json_unsaved_guard.js', 'utf8');
  assert.match(guard, /confirmNavigationAway\(context = 'navigation'\)/);
  assert.match(guard, /context === 'exit'/);
  assert.match(guard, /保存せずにStudioを終了しますか/);
  assert.match(guard, /options.okText = '終了する'/);
});
