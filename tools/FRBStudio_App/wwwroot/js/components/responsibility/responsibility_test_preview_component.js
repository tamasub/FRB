// v0.18.118-responsibility-preview-format-unification
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
      const needsFieldContracts = definitions.some(item => {
        const mode = String(item?.generation_mode ?? '');
        return mode !== 'AGGREGATE_SCALAR_CASE' && mode !== 'CSV_EXPORT_CASE' && mode !== 'GRID_COLUMN_BUILD_CASE';
      });
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
    const gridColumnMode = patterns.some(pattern => String(pattern?.generation_mode ?? '') === 'GRID_COLUMN_BUILD_CASE');

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

    if (gridColumnMode) {
      return patterns.map((pattern, index) => ({
        __pattern_index: index,
        pattern: pattern.pattern_id,
        role: pattern.pattern_role,
        fixture: pattern.fixture_id,
        policy: pattern.include_policy,
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
    const gridColumnMode = patterns.some(pattern => String(pattern?.generation_mode ?? '') === 'GRID_COLUMN_BUILD_CASE');

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
    if (gridColumnMode) {
      return [
        { field: 'pattern', caption: 'TestPattern' },
        { field: 'role', caption: 'Role' },
        { field: 'fixture', caption: 'Fixture' },
        { field: 'policy', caption: 'Policy' },
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

  detailMutationTable(doc, mutations=[]) {
    const wrap = doc.createElement('div');
    wrap.className = 'responsibility-preview-mutation-wrap';
    const table = doc.createElement('table');
    table.className = 'responsibility-preview-mutation-table';

    const head = doc.createElement('thead');
    const hr = doc.createElement('tr');
    ['Field', 'Before (-)', 'After (+)'].forEach(label => {
      const th = doc.createElement('th');
      th.textContent = label;
      hr.appendChild(th);
    });
    head.appendChild(hr);
    table.appendChild(head);

    const body = doc.createElement('tbody');
    (mutations ?? []).forEach(item => {
      const tr = doc.createElement('tr');
      const field = doc.createElement('td');
      field.className = 'is-field';
      field.textContent = String(item?.field ?? '');
      field.title = String(item?.actual_path ?? item?.field_path ?? item?.field ?? '');

      const before = doc.createElement('td');
      before.className = 'is-before';
      before.textContent = responsibilityPreviewDisplay(item?.before);

      const after = doc.createElement('td');
      after.className = 'is-after';
      after.textContent = responsibilityPreviewDisplay(item?.after);

      tr.appendChild(field);
      tr.appendChild(before);
      tr.appendChild(after);
      body.appendChild(tr);
    });
    table.appendChild(body);
    wrap.appendChild(table);
    return wrap;
  }

  detailDisclosure(doc, section, label, value) {
    const details = doc.createElement('details');
    details.className = 'responsibility-preview-detail-disclosure';
    const summary = doc.createElement('summary');
    summary.textContent = label;
    const pre = doc.createElement('pre');
    pre.textContent = value == null ? '' : String(value);
    details.appendChild(summary);
    details.appendChild(pre);
    section.appendChild(details);
    return details;
  }

  renderDataUpdatePersistDetail(doc, pattern) {
    const host = doc.createElement('div');
    host.className = 'responsibility-preview-case-detail';

    const mutations = Array.isArray(pattern?.mutations) ? pattern.mutations : [];
    const definition = (this.row?.test_pattern_definitions ?? []).find(item =>
      String(item?.pattern_def_id ?? '') === String(pattern?.pattern_id ?? '')
    ) ?? {};
    const setup = (this.row?.test_setup ?? []).find(item => item?.setup_id) ?? {};
    const contract = this.row?.expected_first_contract ?? {};

    const input = this.detailSection(doc, '① Before / 対象状況');
    this.detailKeyValue(doc, input, 'Target Row', pattern?.input?.target_row ?? `${pattern?.target_data_path ?? ''}[${pattern?.row_index ?? ''}]`, { mono: true });
    this.detailKeyValue(doc, input, 'Target Structure', pattern?.target_structure ?? '');
    this.detailKeyValue(doc, input, '対象Field数', mutations.length);
    this.detailKeyValue(doc, input, 'Seed Fixture', setup?.input_role ?? 'SEED_FIXTURE');
    host.appendChild(input);

    const action = this.detailSection(doc, '② 操作へ投入', 'is-criteria');
    this.detailKeyValue(doc, action, 'Action', `${mutations.length}項目を Before (-) → After (+) へ変更`);
    this.detailKeyValue(doc, action, 'Procedure', 'Editorへ入力 → F12反映 → 保存 → 再読込');
    this.detailKeyValue(doc, action, 'Value Rule', `${pattern?.value_pattern ?? definition?.value_pattern ?? ''} / ${pattern?.field_selection_policy ?? definition?.field_selection_policy ?? ''}`, { mono: true });
    host.appendChild(action);

    const expected = this.detailSection(doc, '③ Expected Result', 'is-expected');
    this.detailKeyValue(doc, expected, 'ExpectedDef', pattern?.expected_def_type ?? '', { mono: true });
    this.detailKeyValue(doc, expected, 'Expected Changes', mutations.length);
    this.detailKeyValue(doc, expected, 'Unexpected Diff Count', pattern?.expected?.unexpected_diff_count ?? 0);
    const lead = doc.createElement('div');
    lead.className = 'responsibility-preview-detail-lead is-expected-lead';
    lead.textContent = '承認対象: この Before (-) → After (+) の差分を正しい世界とする';
    expected.appendChild(lead);
    expected.appendChild(this.detailMutationTable(doc, mutations));
    host.appendChild(expected);

    const ruleSection = this.detailSection(doc, '★ 導出ルール / なぜこの変更値なのか', 'is-rule');
    this.detailKeyValue(doc, ruleSection, 'Rule ID', 'EXPECTED_FIRST_DATA_UPDATE_PERSIST', { mono: true });
    this.detailKeyValue(doc, ruleSection, 'Rule', 'Expected First / Before・Action・AfterをExpected Diffから対応付ける');
    this.detailKeyValue(doc, ruleSection, 'Before (-)', 'Seed Fixtureの現在値を変更前世界として使う。');
    this.detailKeyValue(doc, ruleSection, 'After (+)', 'Resolved Contract内で現在値と異なる正常値を決定論的に生成する。');
    this.detailKeyValue(doc, ruleSection, 'Expected Diff', '各Fieldの (-)Before / (+)After を検証意図として比較する。');
    this.detailKeyValue(doc, ruleSection, '不変条件', 'Expected Diff対象外の値には差分を発生させない。');
    this.detailKeyValue(doc, ruleSection, '人間が変更できるもの', contract?.role_boundary?.human ?? 'Expected / Expected Diff（検証意図）');
    this.detailKeyValue(doc, ruleSection, '機械が固定化するもの', contract?.role_boundary?.machine ?? 'Input / Action / Runner手順');
    this.detailKeyValue(doc, ruleSection, 'Expected変更時', contract?.expected_change_policy === 'MARK_INPUT_ACTION_STALE_AND_REGENERATE'
      ? 'Generated Input / Action を STALE にして再生成する。'
      : (contract?.expected_change_policy ?? ''));
    if (definition?.notes) this.detailKeyValue(doc, ruleSection, 'Pattern Note', definition.notes);
    host.appendChild(ruleSection);

    const supplement = this.detailSection(doc, '補足情報', 'is-supplement');
    this.detailKeyValue(doc, supplement, 'Guarantee ID', pattern?.guarantee_id ?? '', { mono: true });
    this.detailKeyValue(doc, supplement, 'Source', this.detailJson(pattern?.source ?? {}), { pre: true });
    if (pattern?.expected?.diff) this.detailDisclosure(doc, supplement, 'Expected Diff (raw) を表示', pattern.expected.diff);
    if (this.detailPanelShowRawJson) this.detailDisclosure(doc, supplement, 'Raw Generated Pattern を表示', this.detailJson(pattern ?? {}));
    host.appendChild(supplement);

    return host;
  }

  detailMetricTable(doc, generatedCases=[]) {
    const wrap = doc.createElement('div');
    wrap.className = 'responsibility-preview-metric-wrap';
    const table = doc.createElement('table');
    table.className = 'responsibility-preview-metric-table';

    const head = doc.createElement('thead');
    const hr = doc.createElement('tr');
    ['Metric', 'Expected', 'Actual Path'].forEach(label => {
      const th = doc.createElement('th');
      th.textContent = label;
      hr.appendChild(th);
    });
    head.appendChild(hr);
    table.appendChild(head);

    const body = doc.createElement('tbody');
    (generatedCases ?? []).forEach(item => {
      const tr = doc.createElement('tr');
      const metric = doc.createElement('td');
      metric.className = 'is-field';
      metric.textContent = String(item?.metric ?? '');
      const expected = doc.createElement('td');
      expected.className = 'is-after';
      expected.textContent = responsibilityPreviewDisplay(item?.expected?.value);
      const path = doc.createElement('td');
      path.className = 'is-path';
      path.textContent = String(item?.actual_path ?? '');
      tr.appendChild(metric);
      tr.appendChild(expected);
      tr.appendChild(path);
      body.appendChild(tr);
    });
    table.appendChild(body);
    wrap.appendChild(table);
    return wrap;
  }

  detailCsvSelectedRows(doc, snapshot=[]) {
    const selected = (snapshot ?? []).filter(item => item?.selected === true);
    if (!selected.length) return 'なし';
    return selected.map(item => `#${item.index} ${item.row_id}`).join('\n');
  }

  renderCsvExportDetail(doc, pattern, generatedCase) {
    const host = doc.createElement('div');
    host.className = 'responsibility-preview-case-detail';
    const snapshot = Array.isArray(generatedCase?.input_snapshot) ? generatedCase.input_snapshot : [];
    const selected = snapshot.filter(item => item?.selected === true);
    const expectedValue = generatedCase?.expected ?? {};
    const fieldNames = Array.isArray(expectedValue?.field_names) ? expectedValue.field_names : [];

    const input = this.detailSection(doc, '① 対象行の入力状況');
    this.detailKeyValue(doc, input, 'Target Data', generatedCase?.target_data_path ?? pattern?.target_data_path ?? '', { mono: true });
    this.detailKeyValue(doc, input, 'Row Scope', generatedCase?.row_scope ?? pattern?.row_scope ?? '', { mono: true });
    this.detailKeyValue(doc, input, 'Input Rows', snapshot.length);
    this.detailKeyValue(doc, input, 'Export Rows', selected.length);
    this.detailKeyValue(doc, input, 'Selected Rows', this.detailCsvSelectedRows(doc, snapshot), { pre: true });
    host.appendChild(input);

    const action = this.detailSection(doc, '② CSV出力へ投入', 'is-criteria');
    this.detailKeyValue(doc, action, 'Action', '現在のGrid表示行をCSVとして出力する');
    this.detailKeyValue(doc, action, 'Columns', fieldNames.join(', '), { mono: true });
    this.detailKeyValue(doc, action, 'Column Count', fieldNames.length);
    host.appendChild(action);

    const expected = this.detailSection(doc, '③ Expected Result', 'is-expected');
    this.detailKeyValue(doc, expected, 'ExpectedDef', generatedCase?.expected_def_type ?? pattern?.expected_def_type ?? 'CsvExpectedDef', { mono: true });
    this.detailKeyValue(doc, expected, 'Rows', selected.length);
    this.detailKeyValue(doc, expected, 'UTF-8 BOM', expectedValue?.has_bom === true ? 'YES' : 'NO');
    const csvPreview = String(expectedValue?.csv_without_bom ?? '').split(/\r?\n/).filter(Boolean).slice(0, 6).join('\n');
    if (csvPreview) this.detailKeyValue(doc, expected, 'CSV Preview', csvPreview, { pre: true });
    host.appendChild(expected);

    const ruleSection = this.detailSection(doc, '★ 導出ルール / なぜこのCSVが期待値なのか', 'is-rule');
    this.detailKeyValue(doc, ruleSection, 'Rule ID', 'CSV_EXPORT_VISIBLE_GRID_STATE', { mono: true });
    this.detailKeyValue(doc, ruleSection, '列', 'ViewDefでGrid表示対象となるFieldを表示順でCSV列にする。keyFieldは必要に応じて先頭列へ含める。');
    this.detailKeyValue(doc, ruleSection, '行', String(pattern?.row_scope ?? '').toUpperCase() === 'FILTERED'
      ? 'filtered_row_indexesで指定された表示行だけを出力する。'
      : 'ALL指定では対象Dataの全行を出力する。');
    this.detailKeyValue(doc, ruleSection, 'セル', 'カンマ・引用符・改行を含む値はCSV引用し、内部の引用符は二重化する。');
    this.detailKeyValue(doc, ruleSection, '文字コード / 改行', 'UTF-8 BOM付き / CRLF');
    host.appendChild(ruleSection);

    const supplement = this.detailSection(doc, '補足情報', 'is-supplement');
    this.detailKeyValue(doc, supplement, 'Guarantee ID', generatedCase?.guarantee_id ?? pattern?.guarantee_id ?? '', { mono: true });
    this.detailKeyValue(doc, supplement, 'Source Definition', generatedCase?.source_definition_id ?? '', { mono: true });
    this.detailKeyValue(doc, supplement, 'Source', this.detailJson(pattern?.source ?? {}), { pre: true });
    if (expectedValue?.csv_text) this.detailDisclosure(doc, supplement, 'Expected CSV (raw) を表示', expectedValue.csv_text);
    if (this.detailPanelShowRawJson) this.detailDisclosure(doc, supplement, 'Raw Generated Case を表示', this.detailJson(generatedCase ?? {}));
    host.appendChild(supplement);
    return host;
  }

  renderGridAggregateDetail(doc, pattern) {
    const host = doc.createElement('div');
    host.className = 'responsibility-preview-case-detail';
    const generatedCases = Array.isArray(pattern?.generated_cases) ? pattern.generated_cases : [];
    const firstCase = generatedCases[0] ?? {};
    const snapshot = Array.isArray(firstCase?.input_snapshot) ? firstCase.input_snapshot : [];
    const selectedIndexes = snapshot.filter(item => item?.selected === true).map(item => item?.index);
    const aggregateDeclaration = firstCase?.aggregate_declaration;

    const input = this.detailSection(doc, '① 対象値の入力状況');
    const targetLine = doc.createElement('div');
    targetLine.className = 'responsibility-preview-detail-lead';
    targetLine.textContent = `${pattern?.target_field ?? ''} / ${pattern?.target_data_path ?? ''}`;
    input.appendChild(targetLine);
    input.appendChild(this.detailSnapshotTable(doc, snapshot, selectedIndexes));
    host.appendChild(input);

    const action = this.detailSection(doc, '② 集計へ投入', 'is-criteria');
    this.detailKeyValue(doc, action, 'Field', pattern?.target_field ?? '', { mono: true });
    this.detailKeyValue(doc, action, 'Aggregate', pattern?.aggregate_operator
      ? `${pattern.aggregate_operator} / ${pattern.aggregate_scope}`
      : 'NO AGGREGATE');
    this.detailKeyValue(doc, action, 'Selected Indexes', this.detailJson(selectedIndexes), { pre: true });
    this.detailKeyValue(doc, action, 'Expected Metric Set', pattern?.expected_metric_set ?? '', { mono: true });
    host.appendChild(action);

    const expected = this.detailSection(doc, '③ Expected Result', 'is-expected');
    this.detailKeyValue(doc, expected, 'ExpectedDef', pattern?.expected_def_type ?? 'ScalarExpectedDef', { mono: true });
    expected.appendChild(this.detailMetricTable(doc, generatedCases));
    host.appendChild(expected);

    const ruleSection = this.detailSection(doc, '★ 導出ルール / なぜこの集計値なのか', 'is-rule');
    this.detailKeyValue(doc, ruleSection, 'Rule ID', 'GRID_AGGREGATE_SIMPLE_ORACLE', { mono: true });
    this.detailKeyValue(doc, ruleSection, '宣言', aggregateDeclaration
      ? 'ViewDefのnumber Fieldにある grid.aggregate 宣言を読み、operator / scopeを決定する。'
      : '有効なgrid.aggregate宣言が無いため、has_aggregates=falseを期待する。');
    if (aggregateDeclaration) {
      this.detailKeyValue(doc, ruleSection, '対象行', String(pattern?.aggregate_scope ?? '').toLowerCase() === 'filtered'
        ? 'filtered_row_indexesで指定された行だけを独立Oracleへ投入する。'
        : '対象Dataの全行を独立Oracleへ投入する。');
      this.detailKeyValue(doc, ruleSection, '数値化', 'numberまたはカンマ除去後に有限数へ変換できる文字列だけを有効値とし、それ以外はignoredとして数える。');
      this.detailKeyValue(doc, ruleSection, 'SUM', '有効値だけを単純加算し、value / source_count / valid_count / ignored_countをExpected Metric Setに応じて出力する。');
    }
    this.detailKeyValue(doc, ruleSection, '独立性', 'ExpectedはGridAggregator本体を使わず、Preview Service側の単純Oracleで導出する。');
    host.appendChild(ruleSection);

    const supplement = this.detailSection(doc, '補足情報', 'is-supplement');
    this.detailKeyValue(doc, supplement, 'Guarantee ID', pattern?.guarantee_id ?? '', { mono: true });
    this.detailKeyValue(doc, supplement, 'Source', this.detailJson(pattern?.source ?? {}), { pre: true });
    if (this.detailPanelShowRawJson) this.detailDisclosure(doc, supplement, 'Raw Generated Pattern を表示', this.detailJson(pattern ?? {}));
    host.appendChild(supplement);
    return host;
  }

  detailGridColumnInputTable(doc, fields=[]) {
    const wrap = doc.createElement('div');
    wrap.className = 'responsibility-preview-snapshot-wrap';
    const table = doc.createElement('table');
    table.className = 'responsibility-preview-snapshot-table';
    const head = doc.createElement('thead');
    const hr = doc.createElement('tr');
    ['Index', 'Field', 'Caption', 'grid.visible'].forEach(label => {
      const th = doc.createElement('th');
      th.textContent = label;
      hr.appendChild(th);
    });
    head.appendChild(hr);
    table.appendChild(head);
    const body = doc.createElement('tbody');
    (fields ?? []).forEach((field, index) => {
      const tr = doc.createElement('tr');
      const values = [index, field?.field ?? '', field?.caption ?? '', field?.grid?.visible === false ? 'false' : field?.grid?.visible === true ? 'true' : '(default)'];
      values.forEach(value => {
        const td = doc.createElement('td');
        td.textContent = String(value);
        tr.appendChild(td);
      });
      body.appendChild(tr);
    });
    table.appendChild(body);
    wrap.appendChild(table);
    return wrap;
  }

  renderGridColumnBuildDetail(doc, pattern, generatedCase) {
    const host = doc.createElement('div');
    host.className = 'responsibility-preview-case-detail';
    const snapshot = Array.isArray(generatedCase?.input_snapshot) ? generatedCase.input_snapshot : [];
    const expected = generatedCase?.expected ?? {};

    const input = this.detailSection(doc, '① Fields入力状況');
    this.detailKeyValue(doc, input, 'Fixture', generatedCase?.fixture_id ?? pattern?.fixture_id ?? '', { mono: true });
    input.appendChild(this.detailGridColumnInputTable(doc, snapshot));
    host.appendChild(input);

    const action = this.detailSection(doc, '② GridColumnBuilderへ投入', 'is-criteria');
    this.detailKeyValue(doc, action, 'Policy', generatedCase?.include_policy ?? pattern?.include_policy ?? 'GRID_VISIBLE', { mono: true });
    const includeFields = Array.isArray(generatedCase?.include_fields) ? generatedCase.include_fields : [];
    if (includeFields.length) this.detailKeyValue(doc, action, 'Include Fields', includeFields.join(', '), { mono: true });
    host.appendChild(action);

    const expectedSection = this.detailSection(doc, '③ Expected Result', 'is-expected');
    this.detailKeyValue(doc, expectedSection, 'ExpectedDef', generatedCase?.expected_def_type ?? pattern?.expected_def_type ?? '', { mono: true });
    this.detailKeyValue(doc, expectedSection, 'Field Names', this.detailJson(expected?.field_names ?? []), { pre: true });
    this.detailKeyValue(doc, expectedSection, 'Count', expected?.count ?? 0);
    if (Object.prototype.hasOwnProperty.call(expected, 'input_unchanged')) {
      this.detailKeyValue(doc, expectedSection, 'Input Unchanged', expected.input_unchanged === true ? 'YES' : 'NO');
    }
    host.appendChild(expectedSection);

    const ruleSection = this.detailSection(doc, '★ 導出ルール / なぜこの列構成なのか', 'is-rule');
    this.detailKeyValue(doc, ruleSection, 'Rule ID', 'GRID_COLUMN_BUILD_SIMPLE_ORACLE', { mono: true });
    this.detailKeyValue(doc, ruleSection, 'GRID_VISIBLE', 'grid.visible=falseを除外し、それ以外を入力順のまま採用する。');
    this.detailKeyValue(doc, ruleSection, 'FIELD_ALLOWLIST', '呼出側includeField相当として、明示されたFieldだけを入力順のまま採用する。');
    this.detailKeyValue(doc, ruleSection, '副作用なし', '入力fieldsの内容はExpected導出時に変更せず、no_side_effectパターンではinput_unchanged=trueを期待する。');
    host.appendChild(ruleSection);

    const supplement = this.detailSection(doc, '補足情報', 'is-supplement');
    this.detailKeyValue(doc, supplement, 'Guarantee ID', generatedCase?.guarantee_id ?? pattern?.guarantee_id ?? '', { mono: true });
    this.detailKeyValue(doc, supplement, 'Source Definition', generatedCase?.source_definition_id ?? '', { mono: true });
    this.detailKeyValue(doc, supplement, 'Source', this.detailJson(pattern?.source ?? {}), { pre: true });
    if (this.detailPanelShowRawJson) this.detailDisclosure(doc, supplement, 'Raw Generated Case を表示', this.detailJson(generatedCase ?? {}));
    host.appendChild(supplement);
    return host;
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
    if (String(generatedCase?.generation_status ?? '') === 'INPUT_GENERATION_REQUIRED') {
      this.detailKeyValue(doc, criteria, 'Generation Status', 'INPUT_GENERATION_REQUIRED / Input条件不足');
      this.detailKeyValue(doc, criteria, 'Value', '（Rule条件を満たすInput Draft承認後に導出）');
    } else if (!Object.prototype.hasOwnProperty.call(c, 'value')
        && !Object.prototype.hasOwnProperty.call(c, 'from')
        && !Object.prototype.hasOwnProperty.call(c, 'to')) {
      this.detailKeyValue(doc, criteria, 'Value', '（値入力なし）');
    }
    host.appendChild(criteria);

    
    const expected = this.detailSection(doc, '③ Expected Result', 'is-expected');
    this.detailKeyValue(doc, expected, 'Match Count', generatedCase?.expected?.match_count ?? '');
    this.detailKeyValue(doc, expected, 'Row IDs', this.detailJson(generatedCase?.expected?.row_ids ?? []), { pre: true });
    this.detailKeyValue(doc, expected, 'Indexes', this.detailJson(generatedCase?.expected?.indexes ?? []), { pre: true });
    host.appendChild(expected);


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

    const requirementEvaluation = generatedCase?.input_requirement_evaluation ?? {};
    if (Array.isArray(requirementEvaluation?.requirements) && requirementEvaluation.requirements.length) {
      const reqSub = doc.createElement('div');
      reqSub.className = 'responsibility-preview-detail-subtitle';
      reqSub.textContent = 'Rule → Input Requirement評価';
      ruleSection.appendChild(reqSub);
      requirementEvaluation.requirements.forEach(item => {
        const mark = item?.status === 'PASS' ? '✓' : item?.status === 'MISSING_REQUIRED' ? '✕' : '△';
        const severity = String(item?.severity ?? '').toUpperCase();
        this.detailKeyValue(
          doc,
          ruleSection,
          `${mark} ${severity} / ${item?.requirement_id ?? ''}`,
          `${item?.statement ?? ''}\n${item?.evidence ?? ''} / minimum=${item?.minimum ?? ''}`,
          { pre: true }
        );
      });
      this.detailKeyValue(
        doc,
        ruleSection,
        'Input Rule判定',
        `${requirementEvaluation?.status ?? ''} / Required不足=${requirementEvaluation?.missing_required_count ?? 0} / Recommended不足=${requirementEvaluation?.missing_recommended_count ?? 0}`
      );
    }

    const aiRequest = generatedCase?.ai_input_generation_request ?? {};
    if (aiRequest?.status) {
      this.detailKeyValue(doc, ruleSection, 'AI Input生成判定', aiRequest.status);
      this.detailKeyValue(
        doc,
        ruleSection,
        'Human Approval Gate',
        `${aiRequest?.approval_gate?.generated_status ?? 'draft'} → HUMAN REVIEW → ${aiRequest?.approval_gate?.execution_requires ?? 'approved'}`
      );
      if (aiRequest.status !== 'NOT_REQUIRED') {
        this.detailKeyValue(doc, ruleSection, 'AI Input Generation Request', this.detailJson(aiRequest), { pre: true });
      }
    }
    host.appendChild(ruleSection);

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

    const input = this.detailSection(doc, '① Input / 対象状況');
    this.detailKeyValue(doc, input, 'Target', generatedCase?.target_data_path ?? pattern?.target_data_path ?? '', { mono: true });
    this.detailKeyValue(doc, input, 'Input Snapshot', this.detailJson(generatedCase?.input_snapshot ?? pattern?.input ?? {}), { pre: true });
    host.appendChild(input);

    const action = this.detailSection(doc, '② 操作 / 評価へ投入', 'is-criteria');
    this.detailKeyValue(doc, action, 'Pattern', pattern?.pattern_cd ?? pattern?.pattern_id ?? '', { mono: true });
    this.detailKeyValue(doc, action, 'Generation Mode', pattern?.generation_mode ?? 'GENERIC', { mono: true });
    host.appendChild(action);

    const expected = this.detailSection(doc, '③ Expected Result', 'is-expected');
    this.detailKeyValue(doc, expected, 'ExpectedDef', generatedCase?.expected_def_type ?? pattern?.expected_def_type ?? '', { mono: true });
    this.detailKeyValue(doc, expected, 'Expected', this.detailJson(generatedCase?.expected ?? pattern?.expected ?? {}), { pre: true });
    host.appendChild(expected);

    const ruleSection = this.detailSection(doc, '★ 導出ルール / どの定義から導出したか', 'is-rule');
    this.detailKeyValue(doc, ruleSection, 'Guarantee ID', generatedCase?.guarantee_id ?? pattern?.guarantee_id ?? '', { mono: true });
    this.detailKeyValue(doc, ruleSection, 'Source Definition', generatedCase?.source_definition_id ?? '', { mono: true });
    this.detailKeyValue(doc, ruleSection, 'Generation Mode', pattern?.generation_mode ?? 'GENERIC', { mono: true });
    host.appendChild(ruleSection);

    const supplement = this.detailSection(doc, '補足情報', 'is-supplement');
    this.detailKeyValue(doc, supplement, 'Source', this.detailJson(pattern?.source ?? {}), { pre: true });
    if (this.detailPanelShowRawJson) this.detailDisclosure(doc, supplement, 'Raw Generated Case / Pattern を表示', this.detailJson(generatedCase ?? pattern ?? {}));
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
    const patternCd = String(pattern?.pattern_cd ?? '').toUpperCase();
    const generationMode = String(pattern?.generation_mode ?? '');
    if (patternCd.startsWith('DATA_UPDATE_PERSIST')) {
      pane.appendChild(this.renderDataUpdatePersistDetail(doc, pattern));
    } else if (generationMode === 'SEARCH_OPERATOR_MATRIX' && generatedCases.length) {
      generatedCases.forEach(item => pane.appendChild(this.renderSearchCaseDetail(doc, pattern, item)));
    } else if (generationMode === 'CSV_EXPORT_CASE' && generatedCases.length) {
      pane.appendChild(this.renderCsvExportDetail(doc, pattern, generatedCases[0]));
    } else if (generationMode === 'AGGREGATE_SCALAR_CASE' && generatedCases.length) {
      pane.appendChild(this.renderGridAggregateDetail(doc, pattern));
    } else if (generationMode === 'GRID_COLUMN_BUILD_CASE' && generatedCases.length) {
      pane.appendChild(this.renderGridColumnBuildDetail(doc, pattern, generatedCases[0]));
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
      const inputPlan = this._result?.input_generation_plan;
      const inputPlanText = inputPlan
        ? ` / Input Rule ${inputPlan.generation_needed ? 'AI DRAFT REQUIRED' : inputPlan.augmentation_recommended ? 'AUGMENT REVIEW' : 'READY'}`
        : '';
      model.note = `Responsibility Verification: ${this._result.status} / TestPattern ${s.test_pattern_count ?? 0}件${generated}${inputPlanText} / ${execution}`;
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
