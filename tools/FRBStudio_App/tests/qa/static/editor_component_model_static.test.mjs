import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import test from 'node:test';
import vm from 'node:vm';

const root = process.cwd();

function readText(relativePath) {
  return fs.readFileSync(path.join(root, relativePath), 'utf8');
}

function readJson(relativePath) {
  return JSON.parse(readText(relativePath));
}

function createFakeDocument() {
  const createElement = (tagName='div') => {
    const node = {
      tagName: String(tagName).toUpperCase(),
      dataset: {},
      className: '',
      children: [],
      parentNode: null,
      ownerDocument: null,
      isConnected: true,
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
      remove() {
        this.parentNode?.removeChild?.(this);
        this.isConnected = false;
      }
    };
    node.ownerDocument = document;
    return node;
  };

  const document = { createElement };
  return document;
}

function loadComponentRuntime() {
  const document = createFakeDocument();
  const sandbox = {
    console,
    document,
    globalThis: null,
    normalizeArray(value) {
      if (Array.isArray(value)) return value;
      if (value == null || value === '') return [];
      return [value];
    }
  };
  sandbox.globalThis = sandbox;
  vm.createContext(sandbox);

  [
    'wwwroot/js/core/registry.js',
    'wwwroot/js/components/studio_component.js',
    'wwwroot/js/components/editor_component.js',
    'wwwroot/js/components/editor_component_registry.js',
    'wwwroot/js/components/editor_component_host.js'
  ].forEach(relative => vm.runInContext(readText(relative), sandbox, { filename: relative }));

  return { sandbox, document };
}

test('StudioComponent owns mount/update/destroy lifecycle and releases registered listeners', () => {
  const { sandbox, document } = loadComponentRuntime();

  vm.runInContext(`
    class LifecycleProbeComponent extends EditorComponent {
      constructor(config, services) {
        super(config, services);
        this.renderCount = 0;
        this.clickCount = 0;
      }
      onMount() {
        this.listen(this.hostElement, 'click', () => { this.clickCount += 1; });
      }
      render() {
        this.renderCount += 1;
      }
    }
    globalThis.LifecycleProbeComponent = LifecycleProbeComponent;
  `, sandbox);

  const listeners = new Map();
  const host = document.createElement('div');
  host.addEventListener = (name, handler) => listeners.set(name, handler);
  host.removeEventListener = (name, handler) => {
    if (listeners.get(name) === handler) listeners.delete(name);
  };

  sandbox.__host = host;
  vm.runInContext(`
    globalThis.__probe = new LifecycleProbeComponent({ type: 'probe' }, {});
    __probe.mount(__host, { row: { id: 1 }, rowIndex: 0, mode: 'edit' });
  `, sandbox);

  assert.equal(vm.runInContext('__probe.mounted', sandbox), true);
  assert.equal(vm.runInContext('__probe.row.id', sandbox), 1);
  assert.equal(vm.runInContext('__probe.renderCount', sandbox), 1);
  assert.equal(listeners.size, 1);

  vm.runInContext(`__probe.update({ row: { id: 2 }, rowIndex: 1, mode: 'edit' });`, sandbox);
  assert.equal(vm.runInContext('__probe.row.id', sandbox), 2);
  assert.equal(vm.runInContext('__probe.renderCount', sandbox), 2);

  vm.runInContext('__probe.destroy()', sandbox);
  assert.equal(vm.runInContext('__probe.mounted', sandbox), false);
  assert.equal(vm.runInContext('__probe.hostElement', sandbox), null);
  assert.equal(listeners.size, 0);
});

test('EditorComponentHost creates multiple registered components, updates them, and removes owned mount nodes', () => {
  const { sandbox, document } = loadComponentRuntime();

  vm.runInContext(`
    class HostProbeComponent extends EditorComponent {
      constructor(config, services) {
        super(config, services);
        this.values = [];
      }
      render() {
        this.values.push(this.row?.value ?? null);
      }
    }
    registerEditorComponent('host_probe', ({ config, services }) => new HostProbeComponent(config, services));
  `, sandbox);

  const afterChildGrids = document.createElement('div');
  sandbox.__slots = {
    detailBody: document.createElement('div'),
    afterChildGrids,
    detailFooter: document.createElement('div')
  };

  vm.runInContext(`
    globalThis.__configs = [
      { id: 'a', type: 'host_probe', placement: 'afterChildGrids' },
      { id: 'b', type: 'host_probe', placement: 'afterChildGrids' }
    ];
    globalThis.__componentHost = new EditorComponentHost();
    __componentHost.mount(__configs, __slots, { row: { value: 'first' } });
  `, sandbox);

  assert.equal(vm.runInContext('__componentHost.size', sandbox), 2);
  assert.equal(afterChildGrids.children.length, 2);
  assert.deepEqual(
    Array.from(vm.runInContext('__componentHost.instances.map(x => x.values[0])', sandbox)),
    ['first', 'first']
  );

  vm.runInContext(`__componentHost.sync(__configs, __slots, { row: { value: 'second' } });`, sandbox);
  assert.deepEqual(
    Array.from(vm.runInContext('__componentHost.instances.map(x => x.values.at(-1))', sandbox)),
    ['second', 'second']
  );
  assert.equal(afterChildGrids.children.length, 2);

  vm.runInContext('__componentHost.destroy()', sandbox);
  assert.equal(vm.runInContext('__componentHost.size', sandbox), 0);
  assert.equal(afterChildGrids.children.length, 0);
});

test('standard Detail Editor uses generic editorComponents + Host/Registry integration without capability-specific branches', () => {
  const detailRuntime = readText('wwwroot/js/runtime/detail_save.js');
  const index = readText('wwwroot/index.html');

  assert.match(detailRuntime, /gd\?\.editorComponents/);
  assert.match(detailRuntime, /new EditorComponentHost\(\)/);
  assert.match(detailRuntime, /detailEditorComponentHost\.sync|host\.sync/);
  assert.match(detailRuntime, /editorComponentHostCloseBound/);

  assert.doesNotMatch(detailRuntime, /definition_test_preview|definition_constraint_diff|ExpectedResolver|TestPatternDeriver/);

  assert.match(index, /data-editor-component-slot="detailBody"/);
  assert.match(index, /data-editor-component-slot="afterChildGrids"/);
  assert.match(index, /data-editor-component-slot="detailFooter"/);
  assert.match(index, /js\/components\/studio_component\.js\?v=studio-editor-component-model-01840/);
  assert.match(index, /js\/components\/editor_component_host\.js\?v=studio-editor-component-model-01840/);
  assert.match(index, /js\/runtime\/detail_save\.js\?v=studio-editor-component-model-01840/);
});

test('ViewDef Schema declares editorComponents as a declarative Detail Editor connection contract', () => {
  const schema = readJson('data/json/00_rules/frb_view_def_schema_v0_9.json');
  const sectionProps = schema.$defs?.section?.properties ?? {};
  const component = schema.$defs?.editorComponentOptions;

  assert.equal(sectionProps.editorComponents?.items?.$ref, '#/$defs/editorComponentOptions');
  assert.deepEqual(component?.required, ['type']);
  assert.deepEqual(component?.properties?.placement?.enum, ['detailBody', 'afterChildGrids', 'detailFooter']);
  assert.equal(component?.properties?.config?.additionalProperties, true);
  assert.equal(component?.additionalProperties, false);
});
