import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';

const root = process.cwd();
const read = relative => fs.readFileSync(path.join(root, relative), 'utf8');

test('manual/URL/startup loads all send structured failures to the diagnostics logger', () => {
  const app = read('wwwroot/app.js');
  const runtime = read('wwwroot/js/runtime/load_runtime.js');
  const native = read('NativeShell/NativeCommandDispatcher.cs');
  const config = JSON.parse(read('NativeShell/native_shell.config.json'));
  const page = read('wwwroot/index.html');
  assert.match(app, /recordStudioJsonLoadFailure\(err, \{/);
  assert.match(runtime, /stage: 'startupJson\.read'/);
  assert.match(runtime, /stage: 'URL load'/);
  assert.match(native, /JsonLoadDiagnostics\.TryNativeFailure/);
  assert.match(native, /case "diagnostics\.recordJsonLoadError"/);
  assert.ok(config.allowed_commands.includes('diagnostics.recordJsonLoadError'));
  assert.match(page, /js\/runtime\/json_load_diagnostics\.js/);
  assert.match(read('NativeShell/JsonLoadDiagnostics.cs'), /json_load_errors\.log/);
});

test('diagnostic logger records error information but does not send document contents', async () => {
  const requests = [];
  const fakeWindow = { FRBStudioNativeHost: { isAvailable: () => true,
    async invoke(name, payload) {
      requests.push({ name, payload });
      return { written: true, path: 'example.log' };
    } } };
  const ctx = { window: fakeWindow, console: { error() {}, warn() {} } };
  vm.runInNewContext(read('wwwroot/js/runtime/json_load_diagnostics.js'), ctx);
  const error = Object.assign(new Error('no such table: persons'), { code: 'SQLITE_DATABASE_ERROR' });
  const result = await fakeWindow.FRBStudioJsonLoadDiagnostics.record(error, {
    stage: 'manual load', dataPath: 'data/persons.json', viewDefPath: 'defs/persons.json'
  });
  assert.equal(result.path, 'example.log');
  assert.equal(requests.length, 1);
  assert.equal(requests[0].name, 'diagnostics.recordJsonLoadError');
  assert.equal(requests[0].payload.code, 'SQLITE_DATABASE_ERROR');
  assert.equal(requests[0].payload.data_path, 'data/persons.json');
  assert.equal(requests[0].payload.view_def_path, 'defs/persons.json');
  assert.equal(requests[0].payload.message, 'no such table: persons');
  assert.equal(Object.hasOwn(requests[0].payload, 'content'), false);
});

test('fetchJson explains SQLite HTTP errors and JSON syntax errors with paths', async () => {
  const runtime = read('wwwroot/js/runtime/load_runtime.js');
  const text = runtime.slice(runtime.indexOf('async function fetchJson(url) {'), runtime.indexOf('function normalizeRuntimeFieldDefinitionRef'));
  let response;
  const ctx = { fetch: async () => response, Error, JSON };
  vm.runInNewContext(text, ctx);
  response = { ok: false, status: 500, text: async () => JSON.stringify({
    error: 'SQLITE_DATABASE_ERROR', message: 'no such table: employees',
    details: { table: 'employees', operation: 'SELECT', sqlite_code: 1 }
  }) };
  await assert.rejects(ctx.fetchJson('/api/data/sample.json'), error =>
    error.code === 'SQLITE_DATABASE_ERROR' && /employees/.test(error.message) && /sample\.json/.test(error.message));
  response = { ok: true, status: 200, text: async () => '{"oops": }' };
  await assert.rejects(ctx.fetchJson('/api/data/invalid.json'), error =>
    error.code === 'JSON_PARSE_ERROR' && /invalid\.json/.test(error.message));
  response = { ok: true, status: 200, text: async () => '{"ok":true}' };
  assert.equal((await ctx.fetchJson('/api/data/valid.json')).ok, true);
});
