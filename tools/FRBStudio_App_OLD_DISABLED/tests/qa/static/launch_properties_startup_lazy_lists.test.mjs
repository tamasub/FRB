import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';

const runtime = fs.readFileSync('wwwroot/js/runtime/load_runtime.js', 'utf8');
const app = fs.readFileSync('wwwroot/app.js', 'utf8');
const picker = fs.readFileSync('wwwroot/js/ui/file_tree_picker.js', 'utf8');
const resolver = fs.readFileSync('wwwroot/js/core/viewdef_resolver.js', 'utf8');

function createResolverContext(search) {
  const context = {
    URLSearchParams, location: { search }, console,
    $: () => null,
    setStatus: () => {},
    window: { FRBStudioNativeHost: { isAvailable: () => true } },
    refreshServerLists: Object.assign(async () => ({}), { hasCompleted: false })
  };
  vm.createContext(context);
  vm.runInContext(runtime, context);
  return context;
}

test('Launch item properties only: defer enumeration (normal and Page starts stay normal)', () => {
  for (const [search, expected] of [
    ['?startupJson=1&launchItemProperties=1&focusField=item_id', true],
    ['?startupJson=1&launchPageId=page_1', false],
    ['?startupJson=1', false],
    ['?data=some.json&launchItemProperties=1', false],
    ['', false]
  ]) {
    const context = createResolverContext(search);
    assert.equal(vm.runInContext('isLaunchPropertiesFastStartup()', context), expected, search);
  }
});

test('fast startup can resolve a declared ViewDef without touching the full lists', async () => {
  const context = createResolverContext('?startupJson=1&launchItemProperties=1');
  let reads = 0;
  context.resolveDefForData = async () => ({ defName: 'launch.json', defObj: {} });
  context.refreshServerLists = Object.assign(async () => { reads++; }, { hasCompleted: false });
  const result = await vm.runInContext('resolveStartupViewDefWithFallback({view_def:"launch.json"}, "data.json", new URLSearchParams(location.search))', context);
  assert.equal(result.defName, 'launch.json');
  assert.equal(reads, 0);
});

test('fast startup retries with the full list only if resolving the ViewDef fails', async () => {
  const context = createResolverContext('?startupJson=1&launchItemProperties=1');
  let reads = 0, attempts = 0;
  context.resolveDefForData = async () => {
    if (++attempts === 1) throw new Error('No matching ViewDef');
    return { defName: 'fallback.json' };
  };
  context.refreshServerLists = Object.assign(async (options) => {
    reads++;
    assert.equal(options.status, false);
    assert.equal(options.toast, false);
  }, { hasCompleted: false });
  const result = await vm.runInContext('resolveStartupViewDefWithFallback({}, "data.json", new URLSearchParams(location.search))', context);
  assert.equal(result.defName, 'fallback.json');
  assert.equal(reads, 1);
  assert.equal(attempts, 2);
});

test('normal startup does not retry and preserve original error', async () => {
  const context = createResolverContext('?startupJson=1');
  let reads = 0;
  context.resolveDefForData = async () => { throw Error('No matching ViewDef'); };
  context.refreshServerLists = Object.assign(async () => { reads++; }, { hasCompleted: false });
  await assert.rejects(vm.runInContext('resolveStartupViewDefWithFallback({}, "data.json", new URLSearchParams(location.search))', context), /No matching ViewDef/);
  assert.equal(reads, 0);
});

test('fast startup fallback rethrows real errors after one refresh (no loop)', async () => {
  const context = createResolverContext('?startupJson=1&launchItemProperties=1');
  let reads = 0, attempts = 0;
  context.resolveDefForData = async () => { attempts++; throw Error('incompatible ViewDef'); };
  context.refreshServerLists = Object.assign(async () => { reads++; }, { hasCompleted: false });
  await assert.rejects(vm.runInContext('resolveStartupViewDefWithFallback({}, "data.json", new URLSearchParams(location.search))', context), /incompatible ViewDef/);
  assert.equal(reads, 1);
  assert.equal(attempts, 2);
});

test('app.js startup chain defers list only in Launch properties and keeps ready notification', async () => {
  const start = app.indexOf('const deferStartupFileLists =');
  const end = app.indexOf('window.__NCJS_exportScreenState', start);
  assert.ok(start >= 0 && end > start);
  const startupCode = app.slice(start, end);
  for (const fast of [true, false]) {
    const calls = [];
    const completed = new Promise(resolve => {
      const context = {
        Promise, console,
        isLaunchPropertiesFastStartup: () => fast,
        refreshServerLists: async () => { calls.push('enumerate'); },
        loadStudioOverlayPlugins: async () => { calls.push('plugins'); return []; },
        autoLoadFromQuery: async () => { calls.push('load'); },
        updateViewDefMarkdownButtonState: () => {},
        setupSelectedJsonFolderButtons: () => {},
        window: { chrome: { webview: { postMessage: message => { calls.push('ready'); assert.equal(message.studio_startup_ready, true); resolve(); } } } }
      };
      vm.runInNewContext(startupCode, context);
    });
    await completed;
    assert.deepEqual(calls, fast ? ['plugins', 'load', 'ready'] : ['enumerate', 'plugins', 'load', 'ready']);
  }
});

test('file picker retains delayed read for omitted lists', () => {
  assert.match(picker, /showFileTreePicker\(state\)[\s\S]*?ensureFileTreePickerServerList\(state\)/);
  assert.match(picker, /function ensureFileTreePickerServerList\(state\)[\s\S]*?refreshServerLists\(\{ status: false, toast: false \}\)/);
  assert.match(resolver, /refreshServerLists\.hasCompleted = false/);
});
