import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import test from 'node:test';
import vm from 'node:vm';

const root = process.cwd();

function readText(relativePath) {
  return fs.readFileSync(path.join(root, relativePath), 'utf8');
}

function createFakeDocument() {
  let document;
  const createElement = (tagName='div') => {
    const listeners = new Map();
    const attrs = new Map();
    const node = {
      tagName: String(tagName).toUpperCase(),
      dataset: {},
      className: '',
      textContent: '',
      title: '',
      hidden: false,
      children: [],
      parentNode: null,
      ownerDocument: null,
      style: {},
      get firstChild() { return this.children[0] ?? null; },
      appendChild(child) {
        child.parentNode = this;
        child.ownerDocument = this.ownerDocument;
        this.children.push(child);
        return child;
      },
      removeChild(child) {
        this.children = this.children.filter(x => x !== child);
        child.parentNode = null;
        return child;
      },
      replaceChildren(...children) {
        this.children.forEach(child => { child.parentNode = null; });
        this.children = [];
        children.forEach(child => this.appendChild(child));
      },
      remove() { this.parentNode?.removeChild?.(this); },
      addEventListener(name, handler) { listeners.set(name, handler); },
      removeEventListener(name) { listeners.delete(name); },
      click() { listeners.get('click')?.({ target: this, currentTarget: this }); },
      setAttribute(name, value) { attrs.set(name, String(value)); },
      getAttribute(name) { return attrs.get(name) ?? null; },
      querySelector() { return null; },
      classList: { remove() {} }
    };
    node.ownerDocument = document;
    return node;
  };
  document = { createElement };
  return document;
}

function loadSubGridRuntime() {
  const document = createFakeDocument();
  const sandbox = { console, document, globalThis: null };
  sandbox.globalThis = sandbox;
  vm.createContext(sandbox);
  [
    'wwwroot/js/components/studio_component.js',
    'wwwroot/js/components/editor_component.js',
    'wwwroot/js/components/subgrid_component.js',
    'wwwroot/js/components/derived_subgrid_component.js'
  ].forEach(relative => vm.runInContext(readText(relative), sandbox, { filename: relative }));
  return { sandbox, document };
}

function headerToggle(card) {
  const header = card.children[0];
  const meta = header.children[1];
  return meta.children.at(-1);
}

test('Component SubGrid is expanded by default and header toggle collapses/reopens it', () => {
  const { sandbox, document } = loadSubGridRuntime();
  const host = document.createElement('div');
  sandbox.__host = host;

  vm.runInContext(`
    class ProbeSubGrid extends DerivedSubGridComponent {
      buildRows() { return [{ id: 1 }]; }
      buildColumns() { return [{ field: 'id', caption: 'ID' }]; }
    }
    globalThis.__probe = new ProbeSubGrid({ caption: 'Probe' });
    __probe.mount(__host, {});
  `, sandbox);

  const card = host.children[0];
  const toggle = headerToggle(card);
  const tableWrap = card.children[1];

  assert.equal(card.dataset.subgridExpanded, 'true');
  assert.equal(tableWrap.hidden, false);
  assert.equal(toggle.textContent, '▼');
  assert.equal(toggle.getAttribute('aria-expanded'), 'true');

  toggle.click();
  assert.equal(card.dataset.subgridExpanded, 'false');
  assert.equal(tableWrap.hidden, true);
  assert.equal(toggle.textContent, '▶');

  toggle.click();
  assert.equal(card.dataset.subgridExpanded, 'true');
  assert.equal(tableWrap.hidden, false);
  assert.equal(toggle.textContent, '▼');
});

test('Component SubGrid respects ViewDef config.initialExpanded=false only when explicitly specified', () => {
  const { sandbox, document } = loadSubGridRuntime();
  const host = document.createElement('div');
  sandbox.__host = host;

  vm.runInContext(`
    class ProbeCollapsedSubGrid extends DerivedSubGridComponent {
      buildRows() { return [{ id: 1 }]; }
      buildColumns() { return [{ field: 'id', caption: 'ID' }]; }
    }
    globalThis.__probe = new ProbeCollapsedSubGrid({
      caption: 'Collapsed Probe',
      config: { initialExpanded: false }
    });
    __probe.mount(__host, {});
  `, sandbox);

  const card = host.children[0];
  const toggle = headerToggle(card);
  const tableWrap = card.children[1];

  assert.equal(card.dataset.subgridExpanded, 'false');
  assert.equal(tableWrap.hidden, true);
  assert.equal(toggle.textContent, '▶');
  assert.equal(toggle.getAttribute('aria-expanded'), 'false');
});

test('legacy Data SubGrid uses the same default-open / explicit-false contract', () => {
  const runtime = readText('wwwroot/js/runtime/detail_subgrid_edit.js');
  assert.match(runtime, /function detailSubGridInitialExpanded\(field\)/);
  assert.match(runtime, /cfg\?\.initialExpanded \?\? cfg\?\.initial_expanded/);
  assert.match(runtime, /return value !== false/);
  assert.match(runtime, /detail-subgrid-toggle-btn/);
  assert.match(runtime, /wrap\.hidden = !expanded/);
  assert.match(runtime, /note\.hidden = !expanded/);
});

test('Field Definition Generated TestPattern preview is collapsed by ViewDef while other SubGrids stay default-open', () => {
  const viewDef = JSON.parse(readText('defs/fielddefs/frb_fft_measurement_field_definitions_view_def_v0_1.json'));
  const components = viewDef.views.flatMap(view => view.sections ?? []).flatMap(section => section.editorComponents ?? []);
  const constraint = components.find(component => component.id === 'field_definition_constraint_diff');
  const preview = components.find(component => component.id === 'field_definition_test_preview');

  assert.ok(constraint);
  assert.ok(preview);
  assert.equal(constraint.config?.initialExpanded, undefined);
  assert.equal(preview.config?.initialExpanded, false);
});
