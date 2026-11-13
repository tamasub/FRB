// v0.18.43-field-definition-editor-derived-preview
// Shared UI base for Definition Verification derived previews.
// UI lifecycle/data loading stay here; calculation stays in DefinitionVerificationService.

const DEFINITION_VERIFICATION_DEFAULT_REGISTRY_DATA_PATH = 'config/validation_type_registry_v0_1.json';
const definitionVerificationRegistryPromiseCache = new Map();

function definitionVerificationComponentOptions(component) {
  const raw = component?.config?.config;
  return raw && typeof raw === 'object' ? raw : {};
}

function definitionVerificationComponentDisplayValue(value, undefinedLabel='未定義') {
  if (value === undefined) return undefinedLabel;
  if (value === null) return 'null';
  if (typeof value === 'object') {
    try { return JSON.stringify(value); }
    catch { return String(value); }
  }
  if (typeof value === 'boolean') return value ? 'true' : 'false';
  return String(value);
}

async function loadDefinitionVerificationRegistry(dataPath=DEFINITION_VERIFICATION_DEFAULT_REGISTRY_DATA_PATH) {
  const normalized = String(dataPath || DEFINITION_VERIFICATION_DEFAULT_REGISTRY_DATA_PATH).trim();
  if (!normalized) throw new Error('Validation Type Registry data path is required.');

  if (!definitionVerificationRegistryPromiseCache.has(normalized)) {
    const promise = (async () => {
      if (typeof fetchApiJsonWithUrl === 'function') {
        const loaded = await fetchApiJsonWithUrl('data', normalized);
        if (!loaded?.json || typeof loaded.json !== 'object') {
          throw new Error(`Validation Type Registry load returned invalid JSON: ${normalized}`);
        }
        return loaded.json;
      }

      if (typeof fetch === 'function') {
        const path = normalized.split('/').map(encodeURIComponent).join('/');
        const response = await fetch(`/api/data/${path}`);
        if (!response.ok) throw new Error(`Validation Type Registry load failed (${response.status}): ${normalized}`);
        return response.json();
      }

      throw new Error('Validation Type Registry loader is unavailable.');
    })().catch(err => {
      definitionVerificationRegistryPromiseCache.delete(normalized);
      throw err;
    });
    definitionVerificationRegistryPromiseCache.set(normalized, promise);
  }

  return definitionVerificationRegistryPromiseCache.get(normalized);
}

class DefinitionVerificationDerivedSubGridComponent extends DerivedSubGridComponent {
  constructor(config={}, services={}) {
    super(config, services);
    this._verificationService = null;
    this._verificationResult = null;
    this._verificationState = 'idle';
    this._verificationError = null;
    this._refreshToken = 0;
  }

  get componentOptions() {
    return definitionVerificationComponentOptions(this);
  }

  get registryDataPath() {
    return String(
      this.componentOptions.registryDataPath ??
      this.componentOptions.registry_data_path ??
      DEFINITION_VERIFICATION_DEFAULT_REGISTRY_DATA_PATH
    ).trim() || DEFINITION_VERIFICATION_DEFAULT_REGISTRY_DATA_PATH;
  }

  get verificationResult() {
    return this._verificationResult;
  }

  get verificationState() {
    return this._verificationState;
  }

  onMount() {
    this.refreshVerification();
  }

  onUpdate() {
    this.refreshVerification();
  }

  onDestroy() {
    this._refreshToken += 1;
  }

  async resolveVerificationService() {
    const injectedService = this.serviceContext?.definitionVerificationService;
    if (injectedService && typeof injectedService.deriveForPreview === 'function') return injectedService;

    const injectedRegistry = this.serviceContext?.validationTypeRegistry;
    if (injectedRegistry && typeof injectedRegistry === 'object') {
      return new DefinitionVerificationService({ registry: injectedRegistry });
    }

    if (this._verificationService) return this._verificationService;
    const registry = await loadDefinitionVerificationRegistry(this.registryDataPath);
    this._verificationService = new DefinitionVerificationService({ registry });
    return this._verificationService;
  }

  async refreshVerification() {
    const token = ++this._refreshToken;
    this._verificationState = 'loading';
    this._verificationError = null;
    this._verificationResult = null;

    try {
      // v0.18.46-definition-review-evidence:
      // Diff/Evidence review may provide the frozen execution-time verification result.
      // The same Component renders it without re-deriving from today's Definition.
      const frozenVerification = this.context?.verificationResult ?? this.context?.verification_result ?? null;
      if (frozenVerification && typeof frozenVerification === 'object') {
        if (token !== this._refreshToken || !this.mounted) return;
        this._verificationResult = frozenVerification;
        this._verificationState = 'ready';
        this.render();
        return;
      }

      const service = await this.resolveVerificationService();
      if (token !== this._refreshToken || !this.mounted) return;
      this._verificationResult = service.deriveForPreview(this.row ?? {});
      this._verificationState = 'ready';
      this.render();
    } catch (err) {
      if (token !== this._refreshToken || !this.mounted) return;
      this._verificationState = 'error';
      this._verificationError = err;
      this.render();
    }
  }

  buildRows(context) {
    if (this._verificationState !== 'ready' || !this._verificationResult) return [];
    return this.buildVerificationRows(this._verificationResult, context);
  }

  buildVerificationRows(_verificationResult, _context) {
    throw new Error(`${this.constructor.name}: buildVerificationRows(result, context) must be implemented`);
  }

  buildViewModel() {
    const model = super.buildViewModel();
    if (this._verificationState === 'loading') {
      model.note = 'Validation Type Registryを読み込み、派生情報を計算しています。';
    } else if (this._verificationState === 'error') {
      model.note = `派生情報を計算できませんでした: ${this._verificationError?.message ?? this._verificationError ?? 'unknown error'}`;
    } else if (this._verificationResult) {
      const summary = this._verificationResult.summary ?? {};
      const status = String(this._verificationResult.status ?? '');
      model.note = this.buildReadyNote(status, summary, this._verificationResult);
    }
    return model;
  }

  buildReadyNote(status, _summary, _result) {
    return status ? `Definition Verification: ${status}` : '';
  }
}

globalThis.DEFINITION_VERIFICATION_DEFAULT_REGISTRY_DATA_PATH = DEFINITION_VERIFICATION_DEFAULT_REGISTRY_DATA_PATH;
globalThis.definitionVerificationComponentDisplayValue = definitionVerificationComponentDisplayValue;
globalThis.loadDefinitionVerificationRegistry = loadDefinitionVerificationRegistry;
globalThis.DefinitionVerificationDerivedSubGridComponent = DefinitionVerificationDerivedSubGridComponent;
