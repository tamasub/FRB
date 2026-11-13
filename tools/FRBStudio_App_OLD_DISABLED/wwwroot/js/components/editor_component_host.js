// v0.18.40-studio-editor-component-model
// Standard Editor host for mounting/updating/destroying ViewDef-declared Editor Components.

function editorComponentEnabled(config) {
  return config?.enabled !== false;
}

function editorComponentPlacement(config) {
  const placement = String(config?.placement ?? 'afterChildGrids').trim();
  return placement || 'afterChildGrids';
}

function editorComponentInstanceKey(config, index) {
  const id = String(config?.id ?? '').trim();
  if (id) return id;
  const type = normalizeEditorComponentType(config);
  return `${type || 'component'}:${index}`;
}

function editorComponentConfigSignature(configs=[]) {
  const normalized = (configs ?? [])
    .filter(editorComponentEnabled)
    .map((config, index) => ({
      key: editorComponentInstanceKey(config, index),
      type: normalizeEditorComponentType(config),
      placement: editorComponentPlacement(config),
      config
    }));
  return JSON.stringify(normalized);
}

function resolveEditorComponentHost(slots, config) {
  const placement = editorComponentPlacement(config);
  if (typeof slots === 'function') return slots(placement, config) ?? null;
  if (slots && typeof slots === 'object') return slots[placement] ?? null;
  return null;
}

function createEditorComponentMountElement(slotElement, config, index) {
  const doc = slotElement?.ownerDocument ?? globalThis.document;
  if (!doc?.createElement || !slotElement?.appendChild) return slotElement;

  const mountElement = doc.createElement('div');
  mountElement.className = 'editor-component-host-item';
  mountElement.dataset.componentType = normalizeEditorComponentType(config);
  mountElement.dataset.componentKey = editorComponentInstanceKey(config, index);
  mountElement.dataset.componentPlacement = editorComponentPlacement(config);
  slotElement.appendChild(mountElement);
  return mountElement;
}

class EditorComponentHost {
  constructor({ registry=EditorComponentRegistry, services={} }={}) {
    this.registry = registry;
    this.services = services && typeof services === 'object' ? services : {};
    this.context = null;
    this._entries = [];
    this._signature = '';
    this._slots = null;
  }

  get size() {
    return this._entries.length;
  }

  get instances() {
    return this._entries.map(entry => entry.component);
  }

  mount(configs=[], slots={}, context={}) {
    this.destroy();
    this.context = context ?? {};
    this._slots = slots;
    this._signature = editorComponentConfigSignature(configs);

    (configs ?? [])
      .filter(editorComponentEnabled)
      .forEach((config, index) => {
        const type = normalizeEditorComponentType(config);
        if (!type) throw new Error(`EditorComponentHost: component type is required at index ${index}`);

        const hostElement = resolveEditorComponentHost(slots, config);
        if (!hostElement) {
          throw new Error(`EditorComponentHost: placement host not found: ${editorComponentPlacement(config)} (${type})`);
        }

        const mountElement = createEditorComponentMountElement(hostElement, config, index);
        const component = createEditorComponent(config, this.services, this.registry);
        component.mount(mountElement, this.context);

        this._entries.push({
          key: editorComponentInstanceKey(config, index),
          type,
          placement: editorComponentPlacement(config),
          config,
          hostElement,
          mountElement,
          component
        });
      });

    return this.instances;
  }

  update(context={}) {
    this.context = context ?? {};
    this._entries.forEach(entry => entry.component.update(this.context));
    return this.instances;
  }

  sync(configs=[], slots={}, context={}) {
    const signature = editorComponentConfigSignature(configs);
    const sameSlots = this._slots === slots;

    if (signature !== this._signature || !sameSlots) {
      return this.mount(configs, slots, context);
    }

    return this.update(context);
  }

  destroy() {
    const entries = this._entries.splice(0).reverse();
    entries.forEach(entry => {
      try { entry.component.destroy(); }
      catch (err) { console.warn(`EditorComponentHost: destroy failed: ${entry.type}`, err); }

      if (entry.mountElement && entry.mountElement !== entry.hostElement) {
        try { entry.mountElement.remove?.(); }
        catch {
          try { entry.mountElement.parentNode?.removeChild?.(entry.mountElement); }
          catch { /* ignore */ }
        }
      }
    });

    this.context = null;
    this._signature = '';
    this._slots = null;
  }
}

globalThis.EditorComponentHost = EditorComponentHost;
globalThis.editorComponentPlacement = editorComponentPlacement;
globalThis.editorComponentConfigSignature = editorComponentConfigSignature;
