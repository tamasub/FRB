// v0.5-registry: Renderer registry.
// High-level render steps can be registered and invoked by name without adding new Runtime branches.

const RendererRegistry = createNamedRegistry('RendererRegistry');

function registerRenderer(name, renderer, aliases=[]) {
  return RendererRegistry.register(name, renderer, { aliases });
}

function renderByKey(name, ...args) {
  return RendererRegistry.invoke(name, ...args);
}
