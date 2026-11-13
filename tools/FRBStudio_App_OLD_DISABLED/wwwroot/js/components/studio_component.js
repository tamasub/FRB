// v0.18.40-studio-editor-component-model
// Studio UI Component Model base.
// Only UI parts with lifecycle/state belong here; calculation/domain logic stays in Service / Resolver / Deriver.

class StudioComponent {
  constructor(config={}, services={}) {
    this.config = config && typeof config === 'object' ? { ...config } : {};
    this.services = services && typeof services === 'object' ? services : {};
    this.hostElement = null;
    this.context = null;
    this._mounted = false;
    this._cleanups = [];
  }

  get mounted() {
    return this._mounted;
  }

  mount(hostElement, context={}) {
    if (!hostElement) throw new Error(`${this.constructor.name}: mount host is required`);
    if (this._mounted) this.destroy();

    this.hostElement = hostElement;
    this.context = context ?? {};
    this._mounted = true;
    this.onMount();
    this.render();
    return this;
  }

  update(context={}) {
    if (!this._mounted) throw new Error(`${this.constructor.name}: update() called before mount()`);
    this.context = context ?? {};
    this.onUpdate();
    this.render();
    return this;
  }

  setConfig(config={}) {
    this.config = config && typeof config === 'object' ? { ...config } : {};
    return this;
  }

  addCleanup(cleanup) {
    if (typeof cleanup !== 'function') throw new Error(`${this.constructor.name}: cleanup must be a function`);
    this._cleanups.push(cleanup);
    return cleanup;
  }

  listen(target, eventName, handler, options) {
    if (!target?.addEventListener || !target?.removeEventListener) {
      throw new Error(`${this.constructor.name}: listen target must support add/removeEventListener`);
    }
    target.addEventListener(eventName, handler, options);
    this.addCleanup(() => target.removeEventListener(eventName, handler, options));
    return handler;
  }

  onMount() {}

  onUpdate() {}

  render() {
    throw new Error(`${this.constructor.name}: render() must be implemented`);
  }

  onDestroy() {}

  destroy() {
    if (!this._mounted && !this.hostElement && this._cleanups.length === 0) return;

    const cleanups = this._cleanups.splice(0).reverse();
    cleanups.forEach(cleanup => {
      try { cleanup(); }
      catch (err) { console.warn(`${this.constructor.name}: cleanup failed`, err); }
    });

    try { this.onDestroy(); }
    finally {
      this.hostElement = null;
      this.context = null;
      this._mounted = false;
    }
  }
}

globalThis.StudioComponent = StudioComponent;
