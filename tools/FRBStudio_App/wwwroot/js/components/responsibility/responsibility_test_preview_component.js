// v0.18.114-responsibility-preview-snapshot-column-width
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
    this._selectedRowIndex = 0;
  }

  get title() {
    return String(this.config?.caption ?? this.config?.title ?? 'Generated TestPattern / Expected Preview');
  }

  get componentOptions() {
    const raw = this.config?.config;
    return raw && typeof raw === 'object' ? raw : {};
  }

  get detailPanelOptions() {
    const raw = this.componentOptions?.detailPanel;
    return raw && typeof raw === 'object' ? raw : {};
  }

  get detailPanelEnabled() {
    return this.detailPanelOptions.enabled !== false;
  }

  get detailPanelShowRawJson() {
    return this.detailPanelOptions.showRawJson !== false;
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
    const csvMode = patterns.some(pattern => String(pattern?.generation_mode ?? '') === 'CSV_EXPORT_CASE');

    if (aggregateMode) {
      return patterns.map((pattern, index) => ({
        __pattern_index: index,
        pattern: pattern.pattern_id,
        role: pattern.pattern_role,
        target_field: pattern.target_field,
        aggregate: pattern.aggregate_operator ? `${pattern.aggregate_operator} / ${pattern.aggregate_scope}` : 'NO AGGREGATE',
        case_count: pattern.generated_cases?.length ?? 0,
        expected_def: pattern.expected_def_type
      }));
    }
    if (searchMode) {
      return patterns.map((pattern, index) => ({
        __pattern_index: index,
        pattern: pattern.pattern_id,
        role: pattern.pattern_role,
        value_family: pattern.value_family,
        operator: `${pattern.operator_id} / ${pattern.operator_caption}`,
        case_count: pattern.generated_cases?.length ?? 0,
        expected_def: pattern.expected_def_type
      }));
    }
    if (csvMode) {
      return patterns.map((pattern, index) => ({
        __pattern_index: index,
        pattern: pattern.pattern_id,
        role: pattern.pattern_role,
        row_scope: pattern.row_scope,
        case_count: pattern.generated_cases?.length ?? 0,
        expected_def: pattern.expected_def_type
      }));
    }

    return patterns.map((pattern, index) => ({
      __pattern_index: index,
      pattern: pattern.pattern_id,
      role: pattern.pattern_role,
      target: `${pattern.target_data_path}[${pattern.row_index}]`,
      expected_def: pattern.expected_def_type,
      mutation_count: pattern.mutations?.length ?? 0
    }));
  }

  buildColumns(rows=[]) {
    const patterns = this._result?.test_patterns ?? [];
    const aggregateMode = patterns.some(pattern => String(pattern?.generation_mode ?? '') === 'AGGREGATE_SCALAR_CASE');
    const searchMode = patterns.some(pattern => String(pattern?.generation_mode ?? '') === 'SEARCH_OPERATOR_MATRIX');
    const csvMode = patterns.some(pattern => String(pattern?.generation_mode ?? '') === 'CSV_EXPORT_CASE');

    if (aggregateMode) {
      return [
        { field: 'pattern', caption: 'TestPattern' },
        { field: 'role', caption: 'Role' },
        { field: 'target_field', caption: 'Target Field' },
        { field: 'aggregate', caption: 'Aggregate' },
        { field: 'case_count', caption: 'Cases' },
        { field: 'expected_def', caption: 'ExpectedDef' }
      ];
    }
    if (searchMode) {
      return [
        { field: 'pattern', caption: 'TestPattern' },
        { field: 'role', caption: 'Role' },
        { field: 'value_family', caption: 'Type' },
        { field: 'operator', caption: 'Operator' },
        { field: 'case_count', caption: 'Cases' },
        { field: 'expected_def', caption: 'ExpectedDef' }
      ];
    }
    if (csvMode) {
      return [
        { field: 'pattern', caption: 'TestPattern' },
        { field: 'role', caption: 'Role' },
        { field: 'row_scope', caption: 'Rows' },
        { field: 'case_count', caption: 'Cases' },
        { field: 'expected_def', caption: 'ExpectedDef' }
      ];
    }
    return [
      { field: 'pattern', caption: 'Pattern' },
      { field: 'role', caption: 'Role' },
      { field: 'target', caption: 'Target' },
      { field: 'mutation_count', caption: 'Mutations' },
      { field: 'expected_def', caption: 'ExpectedDef' }
    ];
  }

  detailJson(value) {
    try { return JSON.stringify(value, null, 2); }
    catch { return String(value ?? ''); }
  }

  detailSection(doc, title, className='') {
    const section = doc.createElement('section');
    section.className = `responsibility-preview-detail-section ${className}`.trim();
    const heading = doc.createElement('h4');
    heading.textContent = title;
    section.appendChild(heading);
    return section;
  }

  detailKeyValue(doc, section, label, value, options={}) {
    const row = doc.createElement('div');
    row.className = 'responsibility-preview-detail-kv';
    const key = doc.createElement('div');
    key.className = 'responsibility-preview-detail-key';
    key.textContent = label;
    const val = doc.createElement(options.pre ? 'pre' : 'div');
    val.className = options.pre
      ? 'responsibility-preview-detail-value is-pre'
      : `responsibility-preview-detail-value ${options.mono ? 'is-mono' : ''}`.trim();
    val.textContent = value == null ? '' : String(value);
    row.appendChild(key);
    row.appendChild(val);
    section.appendChild(row);
    return row;
  }

  detailList(doc, section, items=[]) {
    const list = doc.createElement('ul');
    list.className = 'responsibility-preview-detail-list';
    (items ?? []).forEach(item => {
      const li = doc.createElement('li');
      li.textContent = String(item ?? '');
      list.appendChild(li);
    });
    section.appendChild(list);
  }

  detailSnapshotTable(doc, snapshot=[], expectedIndexes=[]) {
    const wrap = doc.createElement('div');
    wrap.className = 'responsibility-preview-snapshot-wrap';
    const table = doc.createElement('table');
    table.className = 'responsibility-preview-snapshot-table';
    const colgroup = doc.createElement('colgroup');
    [
      'responsibility-preview-snapshot-col-index',
      'responsibility-preview-snapshot-col-row-id',
      'responsibility-preview-snapshot-col-value'
    ].forEach(className => {
      const col = doc.createElement('col');
      col.className = className;
      colgroup.appendChild(col);
    });
    table.appendChild(colgroup);
    const head = doc.createElement('thead');
    const hr = doc.createElement('tr');
    ['Index', 'Row ID', 'Value'].forEach(label => {
      const th = doc.createElement('th');
      th.textContent = label;
      hr.appendChild(th);
    });
    head.appendChild(hr);
    table.appendChild(head);
    const body = doc.createElement('tbody');
    const matched = new Set(Array.isArray(expectedIndexes) ? expectedIndexes : []);
    (snapshot ?? []).forEach(item => {
      const tr = doc.createElement('tr');
      if (matched.has(item?.index)) tr.className = 'is-expected-match';
      const index = doc.createElement('td');
      index.textContent = String(item?.index ?? '');
      const rowId = doc.createElement('td');
      rowId.textContent = String(item?.row_id ?? '');
      rowId.title = rowId.textContent;
      const value = doc.createElement('td');
      value.textContent = responsibilityPreviewDisplay(item?.value);
      tr.appendChild(index);
      tr.appendChild(rowId);
      tr.appendChild(value);
      body.appendChild(tr);
    });
    table.appendChild(body);
    wrap.appendChild(table);
    return wrap;
  }

  renderSearchCaseDetail(doc, pattern, generatedCase) {
    const host = doc.createElement('div');
    host.className = 'responsibility-preview-case-detail';

    const input = this.detailSection(doc, '① 対象項目の入力状況');
    const targetLine = doc.createElement('div');
    targetLine.className = 'responsibility-preview-detail-lead';
    targetLine.textContent = `${generatedCase?.target_field ?? ''} / ${generatedCase?.field_path ?? generatedCase?.target_data_path ?? ''}`;
    input.appendChild(targetLine);
    input.appendChild(this.detailSnapshotTable(doc, generatedCase?.input_snapshot ?? [], generatedCase?.expected?.indexes ?? []));
    host.appendChild(input);

    const criteria = this.detailSection(doc, '② 検索へ投入', 'is-criteria');
    this.detailKeyValue(doc, criteria, 'Field', generatedCase?.target_field ?? '', { mono: true });
    this.detailKeyValue(doc, criteria, 'Operator', `${generatedCase?.operator_id ?? ''} / ${generatedCase?.operator_caption ?? ''}`);
    const c = generatedCase?.criteria ?? {};
    if (Object.prototype.hasOwnProperty.call(c, 'value')) {
      this.detailKeyValue(doc, criteria, 'Value', responsibilityPreviewDisplay(c.value), { mono: true });
    }
    if (Object.prototype.hasOwnProperty.call(c, 'from')) {
      this.detailKeyValue(doc, criteria, 'From', responsibilityPreviewDisplay(c.from), { mono: true });
    }
    if (Object.prototype.hasOwnProperty.call(c, 'to')) {
      this.detailKeyValue(doc, criteria, 'To', responsibilityPreviewDisplay(c.to), { mono: true });
    }
    if (!Object.prototype.hasOwnProperty.call(c, 'value')
        && !Object.prototype.hasOwnProperty.call(c, 'from')
        && !Object.prototype.hasOwnProperty.call(c, 'to')) {
      this.detailKeyValue(doc, criteria, 'Value', '（値入力なし）');
    }
    host.appendChild(criteria);

    const derivation = generatedCase?.criteria_derivation ?? {};
    const rule = derivation?.rule ?? {};
    const trace = derivation?.trace ?? {};
    const ruleSection = this.detailSection(doc, '★ 導出ルール / なぜこの検索値なのか', 'is-rule');
    this.detailKeyValue(doc, ruleSection, 'Rule ID', derivation?.rule_id ?? rule?.rule_id ?? '', { mono: true });
    this.detailKeyValue(doc, ruleSection, 'Rule', rule?.title ?? '');
    this.detailKeyValue(doc, ruleSection, '規則', rule?.statement ?? '');
    this.detailKeyValue(doc, ruleSection, '理由', rule?.reason ?? '');
    if (Array.isArray(rule?.fixture_requirements) && rule.fixture_requirements.length) {
      const sub = doc.createElement('div');
      sub.className = 'responsibility-preview-detail-subtitle';
      sub.textContent = 'Inputに要求・推奨する条件';
      ruleSection.appendChild(sub);
      this.detailList(doc, ruleSection, rule.fixture_requirements);
    }
    if (rule?.ai_input_guidance) {
      this.detailKeyValue(doc, ruleSection, 'AI Input生成ガイド', rule.ai_input_guidance);
    }
    this.detailKeyValue(doc, ruleSection, '今回の選択根拠', trace?.basis ?? '', { mono: true });
    if (Array.isArray(trace?.selected_source_rows) && trace.selected_source_rows.length) {
      this.detailKeyValue(doc, ruleSection, '選択元Rows', trace.selected_source_rows
        .map(item => `#${item.index} ${item.row_id}: ${responsibilityPreviewDisplay(item.value)}`)
        .join('\n'), { pre: true });
    }
    const profile = trace?.input_profile ?? {};
    this.detailKeyValue(
      doc,
      ruleSection,
      'Input Profile',
      `rows=${profile.row_count ?? 0}, blank=${profile.blank_count ?? 0}, nonBlank=${profile.non_blank_count ?? 0}, distinct=${profile.distinct_non_blank_count ?? 0}`
    );
    const coverage = trace?.result_coverage ?? {};
    this.detailKeyValue(
      doc,
      ruleSection,
      '結果Coverage',
      `${coverage.coverage_kind ?? ''} / match=${coverage.matched_count ?? ''}, nonMatch=${coverage.non_matched_count ?? ''} / ${coverage.assessment ?? ''}`
    );
    host.appendChild(ruleSection);

    const expected = this.detailSection(doc, '③ Expected Result', 'is-expected');
    this.detailKeyValue(doc, expected, 'Match Count', generatedCase?.expected?.match_count ?? '');
    this.detailKeyValue(doc, expected, 'Row IDs', this.detailJson(generatedCase?.expected?.row_ids ?? []), { pre: true });
    this.detailKeyValue(doc, expected, 'Indexes', this.detailJson(generatedCase?.expected?.indexes ?? []), { pre: true });
    host.appendChild(expected);

    const supplement = this.detailSection(doc, '補足情報', 'is-supplement');
    this.detailKeyValue(doc, supplement, 'Case ID', generatedCase?.case_id ?? '', { mono: true });
    this.detailKeyValue(doc, supplement, 'Guarantee ID', generatedCase?.guarantee_id ?? pattern?.guarantee_id ?? '', { mono: true });
    this.detailKeyValue(doc, supplement, 'ExpectedDef', generatedCase?.expected_def_type ?? pattern?.expected_def_type ?? '', { mono: true });
    this.detailKeyValue(doc, supplement, 'Source Definition', generatedCase?.source_definition_id ?? '', { mono: true });
    this.detailKeyValue(doc, supplement, 'Source', this.detailJson(pattern?.source ?? {}), { pre: true });
    if (this.detailPanelShowRawJson) {
      this.detailKeyValue(doc, supplement, 'Raw Generated Case', this.detailJson(generatedCase ?? {}), { pre: true });
    }
    host.appendChild(supplement);

    return host;
  }

  renderGenericCaseDetail(doc, pattern, generatedCase) {
    const host = doc.createElement('div');
    host.className = 'responsibility-preview-case-detail';

    const input = this.detailSection(doc, 'Input / 対象状況');
    this.detailKeyValue(doc, input, 'Input Snapshot', this.detailJson(generatedCase?.input_snapshot ?? pattern?.input ?? {}), { pre: true });
    host.appendChild(input);

    const expected = this.detailSection(doc, 'Expected');
    this.detailKeyValue(doc, expected, 'ExpectedDef', generatedCase?.expected_def_type ?? pattern?.expected_def_type ?? '', { mono: true });
    this.detailKeyValue(doc, expected, 'Expected', this.detailJson(generatedCase?.expected ?? pattern?.expected ?? {}), { pre: true });
    host.appendChild(expected);

    const supplement = this.detailSection(doc, '補足情報', 'is-supplement');
    this.detailKeyValue(doc, supplement, 'Guarantee ID', generatedCase?.guarantee_id ?? pattern?.guarantee_id ?? '', { mono: true });
    this.detailKeyValue(doc, supplement, 'Source', this.detailJson(pattern?.source ?? {}), { pre: true });
    if (this.detailPanelShowRawJson) {
      this.detailKeyValue(doc, supplement, 'Raw', this.detailJson(generatedCase ?? pattern ?? {}), { pre: true });
    }
    host.appendChild(supplement);
    return host;
  }

  renderSelectedDetail(doc, pattern) {
    const pane = doc.createElement('aside');
    pane.className = 'responsibility-preview-detail-pane';
    if (!pattern) {
      const empty = doc.createElement('div');
      empty.className = 'responsibility-preview-detail-empty';
      empty.textContent = '左のTestPatternを選択すると詳細を表示します。';
      pane.appendChild(empty);
      return pane;
    }

    const header = doc.createElement('div');
    header.className = 'responsibility-preview-detail-header';
    const kicker = doc.createElement('div');
    kicker.className = 'responsibility-preview-detail-kicker';
    kicker.textContent = 'Generated Case Detail';
    const title = doc.createElement('h3');
    title.textContent = String(pattern?.pattern_id ?? '');
    header.appendChild(kicker);
    header.appendChild(title);
    pane.appendChild(header);

    const generatedCases = Array.isArray(pattern?.generated_cases) ? pattern.generated_cases : [];
    if (String(pattern?.generation_mode ?? '') === 'SEARCH_OPERATOR_MATRIX' && generatedCases.length) {
      generatedCases.forEach(item => pane.appendChild(this.renderSearchCaseDetail(doc, pattern, item)));
    } else if (generatedCases.length) {
      generatedCases.forEach(item => pane.appendChild(this.renderGenericCaseDetail(doc, pattern, item)));
    } else {
      pane.appendChild(this.renderGenericCaseDetail(doc, pattern, null));
    }
    return pane;
  }

  renderCard(model) {
    const card = super.renderCard(model);
    card.classList?.add('responsibility-generated-preview-card');
    const doc = this.hostElement?.ownerDocument ?? globalThis.document;
    const tableWrap = card.querySelector?.('.detail-subgrid-table-wrap');
    if (!this.detailPanelEnabled || !tableWrap || !doc?.createElement || !model.rows.length) return card;

    const maxIndex = Math.max(0, model.rows.length - 1);
    this._selectedRowIndex = Math.min(Math.max(0, this._selectedRowIndex ?? 0), maxIndex);
    const patternIndex = Number(model.rows[this._selectedRowIndex]?.__pattern_index ?? this._selectedRowIndex);
    const pattern = this._result?.test_patterns?.[patternIndex] ?? null;

    const layout = doc.createElement('div');
    layout.className = 'responsibility-preview-master-detail';
    layout.dataset.subgridCollapsibleContent = 'true';
    tableWrap.parentNode?.insertBefore(layout, tableWrap);
    layout.appendChild(tableWrap);
    layout.appendChild(this.renderSelectedDetail(doc, pattern));

    const rows = tableWrap.querySelectorAll?.('tbody tr') ?? [];
    [...rows].forEach((tr, index) => {
      tr.classList?.add('responsibility-preview-master-row');
      tr.tabIndex = 0;
      tr.setAttribute?.('role', 'button');
      tr.setAttribute?.('aria-label', `${model.rows[index]?.pattern ?? 'TestPattern'} のGenerated Case詳細を表示`);
      if (index === this._selectedRowIndex) tr.classList?.add('is-selected');
      const select = () => {
        if (this._selectedRowIndex === index) return;
        this._selectedRowIndex = index;
        this.render();
      };
      tr.addEventListener?.('click', select);
      tr.addEventListener?.('keydown', event => {
        if (event?.key === 'Enter' || event?.key === ' ') {
          event.preventDefault?.();
          select();
        }
      });
    });

    return card;
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
