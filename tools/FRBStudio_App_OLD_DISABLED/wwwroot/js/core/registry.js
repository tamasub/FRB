// v0.5-registry: Small named registry primitive used by renderers, virtualData, markdown, and actions.
// This keeps Runtime thin: identifiers are declared by ViewDef/config, then resolved through a registry.

function createNamedRegistry(registryName) {
  const items = new Map();

  const normalizeName = (name) => String(name ?? '').trim();

  return {
    name: registryName,

    register(name, handler, options={}) {
      const key = normalizeName(name);
      if (!key) throw new Error(`${registryName}: registry key is empty`);
      if (typeof handler !== 'function') throw new Error(`${registryName}: handler for ${key} must be a function`);
      items.set(key, { handler, meta: { ...(options.meta ?? {}) } });

      normalizeArray(options.aliases).forEach(alias => {
        const aliasKey = normalizeName(alias);
        if (aliasKey) items.set(aliasKey, { handler, meta: { ...(options.meta ?? {}), aliasOf: key } });
      });

      return handler;
    },

    get(name) {
      return items.get(normalizeName(name))?.handler ?? null;
    },

    has(name) {
      return items.has(normalizeName(name));
    },

    keys() {
      return [...items.keys()];
    },

    require(name) {
      const key = normalizeName(name);
      const handler = this.get(key);
      if (!handler) throw new Error(`${registryName}: 未登録のキーです: ${key}`);
      return handler;
    },

    invoke(name, ...args) {
      return this.require(name)(...args);
    }
  };
}
