// v0.18.40-studio-editor-component-model
// Named registry for Editor Component factories.
// ViewDef declares a component type; Runtime resolves it here without component-specific if branches.

const EditorComponentRegistry = createNamedRegistry('EditorComponentRegistry');

function normalizeEditorComponentType(configOrType) {
  if (typeof configOrType === 'string') return configOrType.trim();
  return String(configOrType?.type ?? '').trim();
}

function registerEditorComponent(type, factory, aliases=[]) {
  return EditorComponentRegistry.register(type, factory, { aliases });
}

function createEditorComponent(config, services={}, registry=EditorComponentRegistry) {
  const type = normalizeEditorComponentType(config);
  if (!type) throw new Error('EditorComponentRegistry: component type is required');

  const factory = registry.require(type);
  const component = factory({
    config: config && typeof config === 'object' ? { ...config } : { type },
    services
  });

  const lifecycleMethods = ['mount', 'update', 'destroy'];
  const missing = lifecycleMethods.filter(name => typeof component?.[name] !== 'function');
  if (missing.length) {
    throw new Error(`EditorComponentRegistry: ${type} does not satisfy lifecycle contract: ${missing.join(', ')}`);
  }
  return component;
}

globalThis.EditorComponentRegistry = EditorComponentRegistry;
globalThis.registerEditorComponent = registerEditorComponent;
globalThis.createEditorComponent = createEditorComponent;
