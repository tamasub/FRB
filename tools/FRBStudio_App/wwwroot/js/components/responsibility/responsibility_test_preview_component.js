// v0.18.109-responsibility-generated-test-preview
// Readonly Generated TestPattern / JsonDiffExpectedDef preview for Responsibility Definition.

const responsibilityPreviewJsonPromiseCache = new Map();

function responsibilityPreviewNormalizedRef(raw) {
  return String(raw ?? '').trim().replace(/\\/g, '/').replace(/^\.\//, '');
}

async function responsibilityPreviewFetchJson(ref) {
  const normalized = responsibilityPreviewNormalizedRef(ref);
  if (!normalized) throw new Error('JSON reference is required.');

  if (responsibilityPreviewJsonPromiseCache.has(normalized)) {
    return responsibilityPreviewJsonPromiseCache.get(normalized);
  }

  const promise = (async () => {
    if (normalized.startsWith('data/json/')) {
      const name = normalized.slice('data/json/'.length);
      if (typeof fetchApiJsonWithUrl === 'function') return (await fetchApiJsonWithUrl('data', name)).json;
    }
    if (normalized.startsWith('defs/')) {
      const name = normalized.slice('defs/'.length);
      if (typeof fetchApiJsonWithUrl === 'function') return (await fetchApiJsonWithUrl('defs', name)).json;
    }
    if (normalized.startsWith('fielddefs/')) {
      const name = normalized.slice('fielddefs/'.length);
      const encoded = name.split('/').map(encodeURIComponent).join('/');
      if (typeof fetch === 'function') {
        try {
          const response = await fetch(`/api/fielddefs/${encoded}`, { cache: 'no-store' });
          if (response.ok) return response.json();
        } catch { /* static fallback below */ }
        const response = await fetch(`fielddefs/${name}`, { cache: 'no-store' });
        if (!response.ok) throw new Error(`Field Definition load failed (${response.status}): ${normalized}`);
        return response.json();
      }
    }
    if (normalized.startsWith('config/')) {
      if (typeof fetchApiJsonWithUrl === 'function') return (await fetchApiJsonWithUrl('data', normalized)).json;
    }
    if (typeof fetch === 'function') {
      const response = await fetch(normalized, { cache: 'no-store' });
      if (!response.ok) throw new Error(`JSON load failed (${response.status}): ${normalized}`);
      return response.json();
    }
    throw new Error(`No JSON loader available for: ${normalized}`);
  })().catch(err => {
    responsibilityPreviewJsonPromiseCache.delete(normalized);
    throw err;
  });

  responsibilityPreviewJsonPromiseCache.set(normalized, promise);
  return promise;
}

function responsibilityPreviewDisplay(value) {
  if (value == null) return value === null ? 'null' : '';
  if (typeof value === 'object') {
    try { return JSON.stringify(value); }
    catch { return String(value); }
  }
  return String(value);
}

class ResponsibilityTestPreviewComponent extends DerivedSubGridComponent {
  constructor(config={}, services={}) {
    super(config, services);
    this._state = 'idle';
    this._result = null;
    this._error = null;
    this._token = 0;
  }

  get title() {
    return String(this.config?.caption ?? this.config?.title ?? 'Generated TestPattern / Expected Preview');
  }

  get componentOptions() {
    const raw = this.config?.config;
    return raw && typeof raw === 'object' ? raw : {};
  }

  onMount() { this.refreshPreview(); }
  onUpdate() { this.refreshPreview(); }
  onDestroy() { this._token += 1; }

  async refreshPreview() {
    const token = ++this._token;
    const responsibility = this.row ?? {};
    const definitions = (responsibility?.test_pattern_definitions ?? []).filter(item => item?.enabled !== false);
    if (!definitions.length) {
      this._state = 'empty';
      this._result = null;
      this._error = null;
      this.render();
      return;
    }

    this._state = 'loading';
    this._result = null;
    this._error = null;
    this.render();

    try {
      const setup = (responsibility?.test_setup ?? []).find(item => item?.setup_id) ?? null;
      if (!setup) throw new Error('test_setup がありません。');
      const registryPath = String(this.componentOptions.registryDataPath ?? 'config/validation_type_registry_v0_1.json');
      const needsSearchOperatorRegistry = definitions.some(item => String(item?.generation_mode ?? '') === 'SEARCH_OPERATOR_MATRIX');
      const needsFieldContracts = definitions.some(item => String(item?.generation_mode ?? '') !== 'AGGREGATE_SCALAR_CASE');
      const searchOperatorRegistryPath = String(
        setup?.search_operator_registry_file ??
        this.componentOptions.searchOperatorRegistryDataPath ??
        'config/search_operator_registry_v0_1.json'
      );
      const [inputData, viewDef, fieldDefinitionDocument, registry, searchOperatorRegistry] = await Promise.all([
        responsibilityPreviewFetchJson(setup.input_file),
        responsibilityPreviewFetchJson(setup.view_def_file),
        needsFieldContracts ? responsibilityPreviewFetchJson(setup.field_definition_file) : Promise.resolve({ field_definitions: [] }),
        needsFieldContracts ? responsibilityPreviewFetchJson(registryPath) : Promise.resolve(null),
        needsSearchOperatorRegistry ? responsibilityPreviewFetchJson(searchOperatorRegistryPath) : Promise.resolve(null)
      ]);
      if (token !== this._token || !this.mounted) return;

      const service = new ResponsibilityTestPreviewService({ registry });
      this._result = service.derive({
        responsibility,
        rootDocument: this.sourceData ?? {},
        inputData,
        viewDef,
        fieldDefinitionDocument,
        registry,
        searchOperatorRegistry
      });
      this._state = 'ready';
      this.render();
    } catch (err) {
      if (token !== this._token || !this.mounted) return;
      this._state = 'error';
      this._error = err;
      this.render();
    }
  }

  buildRows() {
    if (this._state !== 'ready' || !this._result) return [];
    const patterns = this._result.test_patterns ?? [];
    const aggregateMode = patterns.some(pattern => String(pattern?.generation_mode ?? '') === 'AGGREGATE_SCALAR_CASE');
    const searchMode = patterns.some(pattern => String(pattern?.generation_mode ?? '') === 'SEARCH_OPERATOR_MATRIX');
    if (aggregateMode) {
      return patterns.map(pattern => ({
        pattern: pattern.pattern_id,
        role: pattern.pattern_role,
        target_field: pattern.target_field,
        aggregate: pattern.aggregate_operator ? `${pattern.aggregate_operator} / ${pattern.aggregate_scope}` : 'NO AGGREGATE',
        case_count: pattern.generated_cases?.length ?? 0,
        expected_def: pattern.expected_def_type,
        generated_cases: responsibilityPreviewDisplay((pattern.generated_cases ?? []).map(item => ({
          case_id: item.case_id,
          metric: item.metric,
          actual_path: item.actual_path,
          input_snapshot: item.input_snapshot,
          aggregate_declaration: item.aggregate_declaration,
          filtered_row_indexes: item.filtered_row_indexes,
          expected: item.expected
        }))),
        source: `${pattern.source?.input_approval_status ?? ''} / ${pattern.source?.input_file ?? ''}`
      }));
    }
    if (searchMode) {
      return patterns.map(pattern => ({
        pattern: pattern.pattern_id,
        role: pattern.pattern_role,
        value_family: pattern.value_family,
        operator: `${pattern.operator_id} / ${pattern.operator_caption}`,
        case_count: pattern.generated_cases?.length ?? 0,
        expected_def: pattern.expected_def_type,
        generated_cases: responsibilityPreviewDisplay((pattern.generated_cases ?? []).map(item => ({
          case_id: item.case_id,
          target_field: item.target_field,
          input_snapshot: item.input_snapshot,
          criteria: item.criteria,
          expected: item.expected
        }))),
        source: `${pattern.source?.input_approval_status ?? ''} / ${pattern.source?.input_file ?? ''}`
      }));
    }

    return patterns.map(pattern => ({
      pattern: pattern.pattern_id,
      role: pattern.pattern_role,
      target: `${pattern.target_data_path}[${pattern.row_index}]`,
      input: responsibilityPreviewDisplay(pattern.input),
      expected_diff: pattern.expected?.diff ?? '',
      unexpected_diff_count: pattern.expected?.unexpected_diff_count ?? '',
      source: `${pattern.source?.input_approval_status ?? ''} / ${pattern.source?.field_definition_file ?? ''}`
    }));
  }

  buildColumns(rows=[]) {
    const aggregateMode = rows.some(row => Object.prototype.hasOwnProperty.call(row ?? {}, 'aggregate'));
    const searchMode = !aggregateMode && rows.some(row => Object.prototype.hasOwnProperty.call(row ?? {}, 'generated_cases'));
    if (aggregateMode) {
      return [
        { field: 'pattern', caption: 'TestPattern' },
        { field: 'role', caption: 'Role' },
        { field: 'target_field', caption: 'Target Field' },
        { field: 'aggregate', caption: 'Aggregate' },
        { field: 'case_count', caption: 'Cases' },
        { field: 'expected_def', caption: 'ExpectedDef' },
        { field: 'generated_cases', caption: 'Generated Cases / Input Snapshot / Metric / Expected' },
        { field: 'source', caption: 'Source' }
      ];
    }
    if (searchMode) {
      return [
        { field: 'pattern', caption: 'TestPattern' },
        { field: 'role', caption: 'Role' },
        { field: 'value_family', caption: 'Type' },
        { field: 'operator', caption: 'Operator' },
        { field: 'case_count', caption: 'Cases' },
        { field: 'expected_def', caption: 'ExpectedDef' },
        { field: 'generated_cases', caption: 'Generated Cases / Input Snapshot / Criteria / Expected' },
        { field: 'source', caption: 'Source' }
      ];
    }
    return [
      { field: 'pattern', caption: 'Pattern' },
      { field: 'role', caption: 'Role' },
      { field: 'target', caption: 'Target' },
      { field: 'input', caption: 'Generated Input / Mutation' },
      { field: 'expected_diff', caption: 'Expected: Diff' },
      { field: 'unexpected_diff_count', caption: 'Expected: Unexpected Diff Count' },
      { field: 'source', caption: 'Source' }
    ];
  }

  buildViewModel() {
    const model = super.buildViewModel();
    if (this._state === 'loading') {
      model.note = 'Test DATA / ViewDef / Field Definition / RegistryからGenerated TestPattern / Generated Case / Expectedを機械導出しています。';
    } else if (this._state === 'error') {
      model.note = `Generated Previewを導出できませんでした: ${this._error?.message ?? this._error ?? 'unknown error'}`;
    } else if (this._state === 'ready' && this._result) {
      const s = this._result.summary ?? {};
      const execution = this._result.execution_ready ? 'EXECUTION READY' : `PREVIEW ONLY (Input=${this._result.input_approval_status})`;
      const cases = s.generated_case_count ?? 0;
      const generated = cases > 0 ? ` / Generated Case ${cases}件` : ` / Mutation ${s.mutation_count ?? 0}件 / Invalid ${s.invalid_mutation_count ?? 0}件`;
      model.note = `Responsibility Verification: ${this._result.status} / TestPattern ${s.test_pattern_count ?? 0}件${generated} / ${execution}`;
    }
    return model;
  }

  render() {
    // Existing responsibilities without generation definitions must not gain an empty visual card.
    const definitions = (this.row?.test_pattern_definitions ?? []).filter(item => item?.enabled !== false);
    if (!definitions.length) {
      if (this.hostElement) clearSubGridComponentHost(this.hostElement);
      return;
    }
    super.render();
  }
}

registerEditorComponent(
  'responsibility_test_preview',
  ({ config, services }) => new ResponsibilityTestPreviewComponent(config, services)
);

globalThis.responsibilityPreviewFetchJson = responsibilityPreviewFetchJson;
globalThis.ResponsibilityTestPreviewComponent = ResponsibilityTestPreviewComponent;
