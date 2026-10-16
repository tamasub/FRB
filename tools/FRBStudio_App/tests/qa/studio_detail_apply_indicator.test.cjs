// Lightweight regression for Studio's editor-only unapplied ● indicator.
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const source = fs.readFileSync(path.resolve(__dirname, '../../wwwroot/js/runtime/studio_detail_apply_indicator.js'), 'utf8');

function rig() {
  const handlers = new Map();
  const dialogHandlers = new Map();
  let value = 'initial';
  let editorOpen = false;
  const button = {
    textContent: '反映(F12)', dataset: {}, title: '', aria: '',
    classList: { state: new Set(), toggle(className, on) { if (on) this.state.add(className); else this.state.delete(className); } },
    setAttribute(name, text) { this[name] = text; }
  };
  const dialog = {
    get open() { return editorOpen; },
    contains() { return true; },
    addEventListener(name, callback) { dialogHandlers.set(name, callback); }
  };
  const document = {
    getElementById(id) { return { detailDialog: dialog, applyDetailBtn: button }[id] ?? null; },
    addEventListener(name, callback) { handlers.set(name, callback); }
  };
  const timers = [];
  const window = {
    snapshotCurrentDetailApplyDraft() { return JSON.stringify({ value }); },
    setTimeout(callback) { timers.push(callback); },
    openDetail() { editorOpen = true; },
    openNewDetail() { editorOpen = true; },
    rebindDetailAfterCanonicalCommit() {},
    renderDetailForRow() {}
  };
  vm.runInNewContext(source, { document, window, console: { warn() {} } });
  function flush() { while (timers.length) timers.shift()(); }
  return {
    button, dialog, window,
    setValue(next) { value = next; },
    close() { editorOpen = false; dialogHandlers.get('close')(); },
    event(name) { handlers.get(name)({ target: { closest() { return dialog; } } }); flush(); },
    flush
  };
}

test('open editor starts clean; changes display ●, edits reverted remove ●', () => {
  const ui = rig();
  ui.window.openDetail();
  assert.equal(ui.button.textContent, '反映(F12)');
  ui.setValue('edited'); ui.event('input');
  assert.equal(ui.button.textContent, '● 反映(F12)');
  assert.equal(ui.button.dataset.unapplied, 'true');
  ui.setValue('initial'); ui.event('change');
  assert.equal(ui.button.textContent, '反映(F12)');
});

test('F12 canonical rebind clears ●, subsequent edits light it again', () => {
  const ui = rig(); ui.window.openDetail();
  ui.setValue('first edit'); ui.event('input');
  ui.window.rebindDetailAfterCanonicalCommit();
  assert.equal(ui.button.textContent, '反映(F12)');
  ui.setValue('second edit'); ui.event('input');
  assert.equal(ui.button.textContent, '● 反映(F12)');
});

test('failed validation (no canonical rebind) keeps ●', () => {
  const ui = rig(); ui.window.openDetail();
  ui.setValue('invalid'); ui.event('input');
  ui.event('click');
  assert.equal(ui.button.textContent, '● 反映(F12)');
});

test('navigation/new editor establishes baseline; close resets display', () => {
  const ui = rig(); ui.window.openDetail();
  ui.setValue('unapplied'); ui.event('input');
  ui.window.openNewDetail();
  assert.equal(ui.button.textContent, '反映(F12)');
  ui.setValue('new item'); ui.event('input');
  assert.equal(ui.button.textContent, '● 反映(F12)');
  ui.close();
  assert.equal(ui.button.textContent, '反映(F12)');
});

test('subgrid click and PasteJSON rerender refresh without falsely resetting baseline', () => {
  const ui = rig(); ui.window.openDetail();
  ui.setValue('subgrid changed'); ui.event('click');
  assert.equal(ui.button.textContent, '● 反映(F12)');
  ui.setValue('pasted'); ui.window.renderDetailForRow(); ui.flush();
  assert.equal(ui.button.textContent, '● 反映(F12)');
});

test('indicator never mutates data; inspection failures cannot block normal editor', () => {
  const ui = rig(); ui.window.openDetail();
  ui.window.snapshotCurrentDetailApplyDraft = () => { throw new Error('inspection only'); };
  ui.event('input');
  assert.equal(ui.button.textContent, '反映(F12)');
});
