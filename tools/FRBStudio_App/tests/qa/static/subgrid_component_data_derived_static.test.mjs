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
    const node = {
      tagName: String(tagName).toUpperCase(),
      dataset: {},
      className: '',
      textContent: '',
      children: [],
      parentNode: null,
      ownerDocument: null,
      isConnected: true,
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
      remove() {
        this.parentNode?.removeChild?.(this);
        this.isConnected = false;
      },
      querySelector() { return null; },
      classList: {
        remove() {}
      }
    };
    node.ownerDocument = document;
    return node;
  };
  document = { createElement };
  return document;
}

function loadSubGridRuntime(extra={}) {
  const document = createFakeDocument();
  const sandbox = {
    console,
    document,
    globalThis: null,
    ...extra
  };
  sandbox.globalThis = sandbox;
  vm.createContext(sandbox);

  [
    'wwwroot/js/components/studio_component.js',
    'wwwroot/js/components/editor_component.js',
    'wwwroot/js/components/subgrid_component.js',
    'wwwroot/js/components/data_subgrid_component.js',
    'wwwroot/js/components/derived_subgrid_component.js'
  ].forEach(relative => vm.runInContext(readText(relative), sandbox, { filename: relative }));

  return { sandbox, document };
}

test('SubGrid class hierarchy separates canonical Data persistence from readonly Derived presentation', () => {
  const { sandbox } = loadSubGridRuntime();

  assert.equal(vm.runInContext('SubGridComponent.prototype instanceof EditorComponent', sandbox), true);
  assert.equal(vm.runInContext('DataSubGridComponent.prototype instanceof SubGridComponent', sandbox), true);
  assert.equal(vm.runInContext('DerivedSubGridComponent.prototype instanceof SubGridComponent', sandbox), true);

  assert.equal(vm.runInContext('(new DataSubGridComponent({ field: "items" })).componentRole', sandbox), 'data');
  assert.equal(vm.runInContext('(new DataSubGridComponent({ field: "items" })).persistenceMode', sandbox), 'canonical');
  assert.equal(vm.runInContext('(new DerivedSubGridComponent()).componentRole', sandbox), 'derived');
  assert.equal(vm.runInContext('(new DerivedSubGridComponent()).persistenceMode', sandbox), 'derived-readonly');
  assert.equal(vm.runInContext('(new DerivedSubGridComponent()).isEditable()', sandbox), false);
});

test('DerivedSubGridComponent renders derived rows in the standard SubGrid table boundary and cannot mutate source Data', () => {
  const { sandbox, document } = loadSubGridRuntime();
  const host = document.createElement('div');
  const row = { source: 3 };

  sandbox.__host = host;
  sandbox.__row = row;
  vm.runInContext(`
    class DerivedProbeSubGrid extends DerivedSubGridComponent {
      get title() { return 'Derived Preview'; }
      buildRows(context) {
        return [
          { label: 'double', value: context.row.source * 2 },
          { label: 'triple', value: context.row.source * 3 }
        ];
      }
      buildColumns() {
        return [
          { field: 'label', caption: 'Label' },
          { field: 'value', caption: 'Value' }
        ];
      }
    }
    globalThis.__derived = new DerivedProbeSubGrid();
    __derived.mount(__host, { row: __row });
  `, sandbox);

  assert.equal(host.children.length, 1);
  const card = host.children[0];
  assert.equal(card.dataset.subgridRole, 'derived');
  assert.equal(card.dataset.subgridPersistence, 'derived-readonly');
  assert.match(card.className, /is-readonly/);
  assert.equal(row.source, 3);

  assert.throws(
    () => vm.runInContext('__derived.commit()', sandbox),
    /derived rows are readonly/
  );
  assert.deepEqual(row, { source: 3 });
});

test('DataSubGridComponent is the only Component persistence path and delegates commit to the existing Data SubGrid adapter', () => {
  const collected = [{ id: 2, name: 'changed' }];
  const { sandbox } = loadSubGridRuntime({
    collectDetailSubGridValue() { return collected; }
  });

  sandbox.__row = { items: [{ id: 1, name: 'before' }] };
  sandbox.__card = {
    classList: { remove() {} },
    querySelector() { return null; }
  };

  vm.runInContext(`
    globalThis.__data = new DataSubGridComponent({
      field: 'items',
      fieldDef: { field: 'items', caption: 'Items', type: 'objectArray' }
    });
    __data.context = { row: __row, gridDef: { fields: [] } };
    __data._legacyCard = __card;
    globalThis.__committed = __data.commit();
  `, sandbox);

  assert.equal(vm.runInContext('__committed', sandbox), true);
  assert.deepEqual(Array.from(sandbox.__row.items, x => ({ ...x })), collected);
});

test('legacy objectArray/stringArray cards are explicitly canonical Data SubGrids and F12 commit excludes Derived cards', () => {
  const runtime = readText('wwwroot/js/runtime/detail_subgrid_edit.js');
  assert.match(runtime, /card\.dataset\.subgridRole = 'data'/);
  assert.match(runtime, /card\.dataset\.subgridPersistence = 'canonical'/);
  assert.match(runtime, /card\.dataset\.subgridRole && card\.dataset\.subgridRole !== 'data'/);
  assert.match(runtime, /collectDetailSubGridValue\(card\)/);
});

test('index loads the SubGrid Component hierarchy before Detail SubGrid runtime', () => {
  const index = readText('wwwroot/index.html');
  const subGrid = index.indexOf('js/components/subgrid_component.js?v=field-definition-derived-preview-01843');
  const data = index.indexOf('js/components/data_subgrid_component.js?v=subgrid-component-data-derived-01841');
  const derived = index.indexOf('js/components/derived_subgrid_component.js?v=subgrid-component-data-derived-01841');
  const legacyRuntime = index.indexOf('js/runtime/detail_subgrid_edit.js');

  assert.ok(subGrid >= 0);
  assert.ok(data > subGrid);
  assert.ok(derived > data);
  assert.ok(legacyRuntime > derived);
});
