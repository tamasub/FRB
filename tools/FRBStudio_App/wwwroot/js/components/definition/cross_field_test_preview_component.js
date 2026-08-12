// v0.18.45-definition-test-runner-diff-crossfield-e2e
// Readonly Derived SubGrid for Cross Field Constraint TestPattern + Expected preview.

class CrossFieldTestPreviewComponent extends DerivedSubGridComponent {
  constructor(config={}, services={}) {
    super(config, services);
    this._service = null;
    this._result = null;
    this._state = 'idle';
    this._error = null;
    this._refreshToken = 0;
  }

  get title() {
    return String(this.config?.caption ?? this.config?.title ?? 'Cross Field TestPattern / Expected Preview');
  }

  get componentOptions() {
    const raw = this.config?.config;
    return raw && typeof raw === 'object' ? raw : {};
  }

  get registryDataPath() {
    return String(
      this.componentOptions.registryDataPath ??
      this.componentOptions.registry_data_path ??
      globalThis.DEFINITION_VERIFICATION_DEFAULT_REGISTRY_DATA_PATH ??
      'config/validation_type_registry_v0_1.json'
    ).trim();
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

  buildColumns() {
    return [
      { field: 'pattern', caption: 'Pattern' },
      { field: 'left_input', caption: 'Left Input' },
      { field: 'operator', caption: '比較' },
      { field: 'right_input', caption: 'Right Input' },
      { field: 'expected', caption: 'Expected' },
      { field: 'reason', caption: 'Reason' }
    ];
  }

  displayOperator(value) {
    const operatorField = (this.gridDef?.fields ?? []).find(field => field?.field === 'operator');
    if (operatorField && typeof optionLabelForValue === 'function') {
      return String(optionLabelForValue(value, operatorField) ?? value ?? '');
    }
    return String(value ?? '');
  }

  buildRows() {
    if (this._state !== 'ready' || !this._result) return [];
    return (this._result.test_patterns ?? []).map(pattern => ({
      pattern: pattern.pattern_key ?? pattern.pattern_id ?? '',
      left_input: definitionVerificationComponentDisplayValue(pattern.input?.left?.value, ''),
      operator: this.displayOperator(pattern.relation?.operator ?? this._result.operator ?? ''),
      right_input: definitionVerificationComponentDisplayValue(pattern.input?.right?.value, ''),
      expected: pattern.expected?.outcome ?? 'UNRESOLVED',
      reason: pattern.expected?.reason_code ?? ''
    }));
  }

  getRowClassName(row) {
    const outcome = String(row?.expected ?? '').toLowerCase();
    return `definition-test-preview-row expected-${outcome || 'unknown'}`;
  }

  getCellClassName(row, column) {
    if (column?.field !== 'expected') return '';
    return `definition-test-expected definition-test-expected-${String(row?.expected ?? '').toLowerCase()}`;
  }

  buildViewModel() {
    const model = super.buildViewModel();
    if (this._state === 'loading') {
      model.note = 'Validation Type Registryを読み込み、Cross Field TestPatternを導出しています。';
    } else if (this._state === 'error') {
      model.note = `Cross Field TestPatternを導出できませんでした: ${this._error?.message ?? this._error ?? 'unknown error'}`;
    } else if (this._result) {
      const summary = this._result.summary ?? {};
      model.note = [
        `Cross Field Verification: ${this._result.status ?? ''}`,
        `TestPattern ${summary.test_pattern_count ?? 0}件`,
        `ACCEPT ${summary.accept_count ?? 0}件`,
        `REJECT ${summary.reject_count ?? 0}件`,
        `Issue ${summary.issue_count ?? 0}件`
      ].join(' / ');
    }
    return model;
  }

  async refreshVerification() {
    const token = ++this._refreshToken;
    this._state = 'loading';
    this._error = null;
    this._result = null;

    try {
      const injected = this.serviceContext?.crossFieldVerificationService;
      if (injected && typeof injected.deriveForPreview === 'function') {
        this._service = injected;
      } else if (!this._service) {
        const registry = this.serviceContext?.validationTypeRegistry ?? await loadDefinitionVerificationRegistry(this.registryDataPath);
        this._service = new CrossFieldVerificationService({ registry });
      }

      if (token !== this._refreshToken || !this.mounted) return;
      this._result = this._service.deriveForPreview(this.row ?? {}, this.sourceData ?? {});
      this._state = 'ready';
      this.render();
    } catch (err) {
      if (token !== this._refreshToken || !this.mounted) return;
      this._state = 'error';
      this._error = err;
      this.render();
    }
  }
}

registerEditorComponent(
  'cross_field_test_preview',
  ({ config, services }) => new CrossFieldTestPreviewComponent(config, services)
);

globalThis.CrossFieldTestPreviewComponent = CrossFieldTestPreviewComponent;
