// v0.18.58-caption-derived-recursion-and-viewdef-order-save-safety
// Readonly Editor Component that shows the human-facing caption from the target Data ViewDef.
// The caption is derived, not persisted into Field Definition JSON.

const definitionTargetViewPromiseCache = new Map();
const definitionTargetViewResolvedCache = new Map();

function invalidateDefinitionTargetViewDefCache(path='') {
  const normalized = String(path ?? '').trim();
  if (normalized) {
    definitionTargetViewPromiseCache.delete(normalized);
    definitionTargetViewResolvedCache.delete(normalized);
  } else {
    definitionTargetViewPromiseCache.clear();
    definitionTargetViewResolvedCache.clear();
  }
}


function definitionTargetCaptionOptions(component) {
  const raw = component?.config?.config;
  return raw && typeof raw === 'object' ? raw : {};
}

function definitionTargetCaptionDerivedFields(viewDef={}) {
  const result = [];
  const views = Array.isArray(viewDef?.views) ? viewDef.views : [];
  views.forEach(view => {
    const sections = Array.isArray(view?.sections) ? view.sections : [];
    sections.forEach(section => {
      const fields = Array.isArray(section?.fields) ? section.fields : [];
      fields.forEach(field => {
        const derived = field?.derived;
        if (!derived || String(derived.type ?? '').trim() !== 'definition_target_caption') return;
        const targetViewDefPath = String(
          derived.targetViewDefPath ?? derived.target_view_def_path ?? ''
        ).trim();
        const sourceField = String(derived.sourceField ?? derived.source_field ?? 'field_path').trim() || 'field_path';
        if (!field?.field || !targetViewDefPath) return;

        // Save-safety: a derived Caption field must never overwrite its own source field.
        // A malformed ViewDef such as field="field_path" + sourceField="field_path"
        // would otherwise install a getter that recursively reads itself and causes
        // "Maximum call stack size exceeded".
        if (String(field.field).trim() === sourceField) {
          console.warn(
            `[FRBStudio] definition_target_caption skipped self-recursive field: ${String(field.field)}`
          );
          return;
        }

        result.push({
          section,
          field,
          targetViewDefPath,
          sourceField,
          unresolvedValue: String(derived.unresolvedValue ?? derived.unresolved_value ?? '⚠ 未解決')
        });
      });
    });
  });
  return result;
}

function definitionTargetCaptionRows(dataObj={}, section={}) {
  if (typeof getByPath !== 'function') return [];
  const rows = getByPath(dataObj, section?.dataPath ?? section?.data_path ?? '$');
  return Array.isArray(rows) ? rows : [];
}

function attachDefinitionTargetCaptionGetter(row, spec, targetViewDef) {
  if (!row || typeof row !== 'object' || !spec?.field?.field || !targetViewDef) return;
  const targetFieldName = String(spec.field.field);
  Object.defineProperty(row, targetFieldName, {
    enumerable: false,
    configurable: true,
    get() {
      const sourceValue = (typeof getByPath === 'function')
        ? getByPath(row, spec.sourceField)
        : row?.[spec.sourceField];
      const resolved = (typeof resolveFieldDefinitionTargetViewField === 'function')
        ? resolveFieldDefinitionTargetViewField(targetViewDef, sourceValue)
        : null;
      return resolved?.caption || spec.unresolvedValue;
    }
  });
}

function refreshDefinitionTargetCaptionDerivedProperties(viewDef={}, dataObj={}) {
  const specs = definitionTargetCaptionDerivedFields(viewDef);
  specs.forEach(spec => {
    const target = definitionTargetViewResolvedCache.get(spec.targetViewDefPath);
    if (!target) return;
    definitionTargetCaptionRows(dataObj, spec.section).forEach(row => {
      attachDefinitionTargetCaptionGetter(row, spec, target);
    });
  });
  return dataObj;
}

async function materializeDefinitionTargetCaptionDerivedProperties(viewDef={}, dataObj={}) {
  const specs = definitionTargetCaptionDerivedFields(viewDef);
  if (!specs.length) return dataObj;

  const targets = new Map();
  for (const spec of specs) {
    if (!targets.has(spec.targetViewDefPath)) {
      targets.set(spec.targetViewDefPath, await loadDefinitionTargetViewDef(spec.targetViewDefPath));
    }
  }
  specs.forEach(spec => {
    const target = targets.get(spec.targetViewDefPath);
    definitionTargetCaptionRows(dataObj, spec.section).forEach(row => {
      attachDefinitionTargetCaptionGetter(row, spec, target);
    });
  });
  return dataObj;
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
        definitionTargetViewResolvedCache.set(normalized, loaded.json);
        return loaded.json;
      }

      if (typeof fetch === 'function') {
        const encoded = normalized.split('/').map(encodeURIComponent).join('/');
        const response = await fetch(`/api/defs/${encoded}`);
        if (!response.ok) throw new Error(`Target ViewDef load failed (${response.status}): ${normalized}`);
        const json = await response.json();
        definitionTargetViewResolvedCache.set(normalized, json);
        return json;
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
globalThis.definitionTargetCaptionDerivedFields = definitionTargetCaptionDerivedFields;
globalThis.refreshDefinitionTargetCaptionDerivedProperties = refreshDefinitionTargetCaptionDerivedProperties;
globalThis.materializeDefinitionTargetCaptionDerivedProperties = materializeDefinitionTargetCaptionDerivedProperties;
globalThis.DefinitionTargetCaptionComponent = DefinitionTargetCaptionComponent;
