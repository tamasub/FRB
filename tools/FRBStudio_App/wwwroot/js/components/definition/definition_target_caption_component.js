// v0.18.48-field-definition-caption-and-detail-header-spacing
// Readonly Editor Component that shows the human-facing caption from the target Data ViewDef.
// The caption is derived, not persisted into Field Definition JSON.

const definitionTargetViewPromiseCache = new Map();

function invalidateDefinitionTargetViewDefCache(path='') {
  const normalized = String(path ?? '').trim();
  if (normalized) definitionTargetViewPromiseCache.delete(normalized);
  else definitionTargetViewPromiseCache.clear();
}


function definitionTargetCaptionOptions(component) {
  const raw = component?.config?.config;
  return raw && typeof raw === 'object' ? raw : {};
}

async function loadDefinitionTargetViewDef(path) {
  const normalized = String(path ?? '').trim();
  if (!normalized) throw new Error('targetViewDefPath is required.');

  if (!definitionTargetViewPromiseCache.has(normalized)) {
    const promise = (async () => {
      if (typeof fetchApiJsonWithUrl === 'function') {
        const loaded = await fetchApiJsonWithUrl('defs', normalized);
        if (!loaded?.json || typeof loaded.json !== 'object') {
          throw new Error(`Target ViewDef load returned invalid JSON: ${normalized}`);
        }
        return loaded.json;
      }

      if (typeof fetch === 'function') {
        const encoded = normalized.split('/').map(encodeURIComponent).join('/');
        const response = await fetch(`/api/defs/${encoded}`);
        if (!response.ok) throw new Error(`Target ViewDef load failed (${response.status}): ${normalized}`);
        return response.json();
      }

      throw new Error('Target ViewDef loader is unavailable.');
    })().catch(err => {
      definitionTargetViewPromiseCache.delete(normalized);
      throw err;
    });
    definitionTargetViewPromiseCache.set(normalized, promise);
  }

  return definitionTargetViewPromiseCache.get(normalized);
}

class DefinitionTargetCaptionComponent extends EditorComponent {
  constructor(config={}, services={}) {
    super(config, services);
    this._targetViewDef = null;
    this._resolvedField = null;
    this._state = 'idle';
    this._error = null;
    this._refreshToken = 0;
  }

  get componentOptions() {
    return definitionTargetCaptionOptions(this);
  }

  get targetViewDefPath() {
    return String(
      this.componentOptions.targetViewDefPath ??
      this.componentOptions.target_view_def_path ??
      ''
    ).trim();
  }

  onMount() {
    this.refreshTargetCaption();
  }

  onUpdate() {
    this.refreshTargetCaption();
  }

  onDestroy() {
    this._refreshToken += 1;
  }

  async refreshTargetCaption() {
    const token = ++this._refreshToken;
    this._state = 'loading';
    this._error = null;
    this._resolvedField = null;

    try {
      const path = this.targetViewDefPath;
      const viewDef = await loadDefinitionTargetViewDef(path);
      if (token !== this._refreshToken || !this.mounted) return;
      this._targetViewDef = viewDef;
      this._resolvedField = resolveFieldDefinitionTargetViewField(viewDef, this.row?.field_path ?? '');
      this._state = this._resolvedField ? 'ready' : 'unresolved';
      this.render();
    } catch (err) {
      if (token !== this._refreshToken || !this.mounted) return;
      this._state = 'error';
      this._error = err;
      this.render();
    }
  }

  render() {
    if (!this.hostElement) return;
    if (typeof this.hostElement.replaceChildren === 'function') this.hostElement.replaceChildren();
    else this.hostElement.innerHTML = '';

    const doc = this.hostElement.ownerDocument ?? globalThis.document;
    if (!doc?.createElement) return;

    const card = doc.createElement('section');
    card.className = `definition-target-caption-card is-${this._state}`;

    const label = doc.createElement('span');
    label.className = 'definition-target-caption-label';
    label.textContent = String(this.config?.caption ?? 'Data項目名（Caption）');
    card.appendChild(label);

    const value = doc.createElement('strong');
    value.className = 'definition-target-caption-value';
    if (this._state === 'loading') value.textContent = '読み込み中…';
    else if (this._state === 'error') value.textContent = '取得できませんでした';
    else if (this._state === 'unresolved') value.textContent = '該当Caption未解決';
    else value.textContent = this._resolvedField?.caption || this._resolvedField?.field || '未設定';
    card.appendChild(value);

    const meta = doc.createElement('span');
    meta.className = 'definition-target-caption-meta';
    if (this._state === 'ready') {
      const section = this._resolvedField?.section_caption || this._resolvedField?.section_id || '';
      meta.textContent = section ? `${section} / ${this.row?.field_path ?? ''}` : String(this.row?.field_path ?? '');
    } else if (this._state === 'error') {
      meta.textContent = String(this._error?.message ?? this._error ?? 'unknown error');
    } else {
      meta.textContent = String(this.row?.field_path ?? '');
    }
    card.appendChild(meta);

    this.hostElement.appendChild(card);
  }
}

registerEditorComponent(
  'definition_target_caption',
  ({ config, services }) => new DefinitionTargetCaptionComponent(config, services)
);

globalThis.loadDefinitionTargetViewDef = loadDefinitionTargetViewDef;
globalThis.invalidateDefinitionTargetViewDefCache = invalidateDefinitionTargetViewDefCache;
globalThis.DefinitionTargetCaptionComponent = DefinitionTargetCaptionComponent;
