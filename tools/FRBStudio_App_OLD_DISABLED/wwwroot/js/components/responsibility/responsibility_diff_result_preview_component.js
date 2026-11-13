// v0.18.123-responsibility-result-evidence-cross-responsibility
// Readonly Result Evidence projection.
// IMPORTANT: this component does not re-derive Expected/Actual.
// It renders only the saved Diff JSON facts, including the persisted planned_pattern snapshot.

function responsibilityDiffEvidenceDisplay(value) {
  if (value === undefined) return 'undefined';
  if (value === null) return 'null';
  if (typeof value === 'string') return value;
  if (typeof value === 'object') {
    try { return JSON.stringify(value); }
    catch { return String(value); }
  }
  return String(value);
}

class ResponsibilityDiffResultPreviewComponent extends EditorComponent {
  get componentTitle() {
    return String(this.config?.caption ?? this.config?.title ?? 'TestPattern / Result Evidence Preview');
  }

  get showRawJson() {
    const options = this.config?.config && typeof this.config.config === 'object'
      ? this.config.config
      : {};
    return options.showRawJson !== false;
  }

  clearHost() {
    if (!this.hostElement) return;
    if (typeof this.hostElement.replaceChildren === 'function') {
      this.hostElement.replaceChildren();
      return;
    }
    while (this.hostElement.firstChild) this.hostElement.removeChild(this.hostElement.firstChild);
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

  detailLead(doc, text) {
    const lead = doc.createElement('div');
    lead.className = 'responsibility-preview-detail-lead';
    lead.textContent = text;
    return lead;
  }

  metricLabel(check) {
    return String(check?.metric ?? check?.name ?? check?.case_id ?? check?.check_id ?? '');
  }

  renderMetricTable(doc, checks, mode='diff') {
    const wrap = doc.createElement('div');
    wrap.className = 'responsibility-result-evidence-table-wrap';

    const table = doc.createElement('table');
    table.className = `responsibility-result-evidence-table is-${mode}`;

    const headers = mode === 'expected'
      ? ['Metric', 'Expected']
      : mode === 'actual'
        ? ['Metric', 'Actual', 'Observed Source']
        : ['Metric', 'Expected', 'Actual', 'Result', 'Message'];

    const head = doc.createElement('thead');
    const hr = doc.createElement('tr');
    headers.forEach(label => {
      const th = doc.createElement('th');
      th.textContent = label;
      hr.appendChild(th);
    });
    head.appendChild(hr);
    table.appendChild(head);

    const body = doc.createElement('tbody');
    (checks ?? []).forEach(check => {
      const tr = doc.createElement('tr');
      if (mode === 'diff') tr.className = check?.pass === true ? 'is-pass' : 'is-fail';

      const metric = doc.createElement('td');
      metric.className = 'is-metric';
      metric.textContent = this.metricLabel(check);
      metric.title = String(check?.case_id ?? check?.check_id ?? '');
      tr.appendChild(metric);

      if (mode === 'expected' || mode === 'diff') {
        const expected = doc.createElement('td');
        expected.className = 'is-expected-value';
        expected.textContent = responsibilityDiffEvidenceDisplay(
          Object.prototype.hasOwnProperty.call(check ?? {}, 'expected_raw')
            ? check.expected_raw
            : check?.expected
        );
        tr.appendChild(expected);
      }

      if (mode === 'actual' || mode === 'diff') {
        const actual = doc.createElement('td');
        actual.className = 'is-actual-value';
        actual.textContent = responsibilityDiffEvidenceDisplay(
          Object.prototype.hasOwnProperty.call(check ?? {}, 'actual_raw')
            ? check.actual_raw
            : check?.actual
        );
        tr.appendChild(actual);
      }

      if (mode === 'actual') {
        const source = doc.createElement('td');
        source.className = 'is-source';
        source.textContent = String(check?.source ?? '');
        tr.appendChild(source);
      }

      if (mode === 'diff') {
        const result = doc.createElement('td');
        result.className = 'is-result';
        result.textContent = check?.pass === true ? 'PASS' : 'FAIL';
        tr.appendChild(result);

        const message = doc.createElement('td');
        message.className = 'is-message';
        message.textContent = String(check?.message ?? '');
        tr.appendChild(message);
      }

      body.appendChild(tr);
    });
    table.appendChild(body);
    wrap.appendChild(table);
    return wrap;
  }

  renderExpectedMetricTable(doc, generatedCases=[]) {
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
      expected.textContent = responsibilityDiffEvidenceDisplay(item?.expected?.value);
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

  detailSnapshotTable(doc, snapshot=[], selectedIndexes=[]) {
    const wrap = doc.createElement('div');
    wrap.className = 'responsibility-preview-snapshot-wrap';
    const table = doc.createElement('table');
    table.className = 'responsibility-preview-snapshot-table';

    const head = doc.createElement('thead');
    const hr = doc.createElement('tr');
    ['Index', 'Row ID', 'Value'].forEach(label => {
      const th = doc.createElement('th');
      th.textContent = label;
      hr.appendChild(th);
    });
    head.appendChild(hr);
    table.appendChild(head);

    const matched = new Set(Array.isArray(selectedIndexes) ? selectedIndexes : []);
    const body = doc.createElement('tbody');
    (snapshot ?? []).forEach(item => {
      const tr = doc.createElement('tr');
      if (matched.has(item?.index) || item?.selected === true) tr.className = 'is-expected-match';
      const index = doc.createElement('td');
      index.textContent = String(item?.index ?? '');
      const rowId = doc.createElement('td');
      rowId.textContent = String(item?.row_id ?? '');
      rowId.title = rowId.textContent;
      const value = doc.createElement('td');
      value.textContent = responsibilityDiffEvidenceDisplay(item?.value);
      tr.appendChild(index);
      tr.appendChild(rowId);
      tr.appendChild(value);
      body.appendChild(tr);
    });
    table.appendChild(body);
    wrap.appendChild(table);
    return wrap;
  }

  detailCsvSelectedRows(snapshot=[]) {
    const selected = (snapshot ?? []).filter(item => item?.selected === true);
    if (!selected.length) return 'なし';
    return selected.map(item => `#${item.index} ${item.row_id}`).join('\n');
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
      before.textContent = responsibilityDiffEvidenceDisplay(item?.before);
      const after = doc.createElement('td');
      after.className = 'is-after';
      after.textContent = responsibilityDiffEvidenceDisplay(item?.after);
      tr.appendChild(field);
      tr.appendChild(before);
      tr.appendChild(after);
      body.appendChild(tr);
    });
    table.appendChild(body);
    wrap.appendChild(table);
    return wrap;
  }

  renderSearchFactSections(doc, row, body) {
    const pattern = row?.planned_pattern ?? {};
    const generatedCase = (pattern?.generated_cases ?? [])[0] ?? {};
    const expected = generatedCase?.expected ?? {};
    const input = this.detailSection(doc, '① 対象項目の入力状況');
    input.appendChild(this.detailLead(doc, `${generatedCase?.target_field ?? ''} / ${generatedCase?.field_path ?? generatedCase?.target_data_path ?? ''}`));
    input.appendChild(this.detailSnapshotTable(doc, generatedCase?.input_snapshot ?? [], expected?.indexes ?? []));
    body.appendChild(input);

    const criteria = this.detailSection(doc, '② 検索へ投入', 'is-criteria');
    this.detailKeyValue(doc, criteria, 'Field', generatedCase?.target_field ?? '', { mono: true });
    this.detailKeyValue(doc, criteria, 'Operator', `${generatedCase?.operator_id ?? pattern?.operator_id ?? ''} / ${generatedCase?.operator_caption ?? pattern?.operator_caption ?? ''}`);
    const c = generatedCase?.criteria ?? {};
    if (Object.prototype.hasOwnProperty.call(c, 'value')) this.detailKeyValue(doc, criteria, 'Value', responsibilityDiffEvidenceDisplay(c.value), { mono: true });
    if (Object.prototype.hasOwnProperty.call(c, 'from')) this.detailKeyValue(doc, criteria, 'From', responsibilityDiffEvidenceDisplay(c.from), { mono: true });
    if (Object.prototype.hasOwnProperty.call(c, 'to')) this.detailKeyValue(doc, criteria, 'To', responsibilityDiffEvidenceDisplay(c.to), { mono: true });
    if (!Object.prototype.hasOwnProperty.call(c, 'value') && !Object.prototype.hasOwnProperty.call(c, 'from') && !Object.prototype.hasOwnProperty.call(c, 'to')) {
      this.detailKeyValue(doc, criteria, 'Value', '（値入力なし）');
    }
    body.appendChild(criteria);

    const expectedSection = this.detailSection(doc, '③ Expected Result', 'is-expected');
    this.detailKeyValue(doc, expectedSection, 'Match Count', expected?.match_count ?? '');
    this.detailKeyValue(doc, expectedSection, 'Row IDs', this.detailJson(expected?.row_ids ?? []), { pre: true });
    this.detailKeyValue(doc, expectedSection, 'Indexes', this.detailJson(expected?.indexes ?? []), { pre: true });
    body.appendChild(expectedSection);
  }

  renderDataUpdatePersistFactSections(doc, row, body) {
    const pattern = row?.planned_pattern ?? {};
    const mutations = Array.isArray(pattern?.mutations) ? pattern.mutations : [];
    const input = this.detailSection(doc, '① Before / 対象状況');
    this.detailKeyValue(doc, input, 'Target Row', pattern?.input?.target_row ?? `${pattern?.target_data_path ?? ''}[${pattern?.row_index ?? ''}]`, { mono: true });
    this.detailKeyValue(doc, input, 'Target Structure', pattern?.target_structure ?? '');
    this.detailKeyValue(doc, input, '対象Field数', mutations.length);
    body.appendChild(input);

    const action = this.detailSection(doc, '② 操作へ投入', 'is-criteria');
    this.detailKeyValue(doc, action, 'Action', `${mutations.length}項目を Before (-) → After (+) へ変更`);
    this.detailKeyValue(doc, action, 'Procedure', 'Editorへ入力 → F12反映 → 保存 → 再読込');
    this.detailKeyValue(doc, action, 'Value Rule', `${pattern?.value_pattern ?? ''} / ${pattern?.field_selection_policy ?? ''}`, { mono: true });
    body.appendChild(action);

    const expected = this.detailSection(doc, '③ Expected Result', 'is-expected');
    this.detailKeyValue(doc, expected, 'ExpectedDef', pattern?.expected_def_type ?? 'JsonDiffExpectedDef', { mono: true });
    this.detailKeyValue(doc, expected, 'Expected Changes', mutations.length);
    this.detailKeyValue(doc, expected, 'Unexpected Diff Count', pattern?.expected?.unexpected_diff_count ?? 0);
    expected.appendChild(this.detailMutationTable(doc, mutations));
    body.appendChild(expected);
  }

  renderAggregateFactSections(doc, row, body) {
    const pattern = row?.planned_pattern ?? {};
    const generatedCases = Array.isArray(pattern?.generated_cases) ? pattern.generated_cases : [];
    const firstCase = generatedCases[0] ?? {};
    const snapshot = Array.isArray(firstCase?.input_snapshot) ? firstCase.input_snapshot : [];
    const selectedIndexes = snapshot.filter(item => item?.selected === true).map(item => item?.index);

    const input = this.detailSection(doc, '① 対象値の入力状況');
    input.appendChild(this.detailLead(doc, `${pattern?.target_field ?? ''} / ${pattern?.target_data_path ?? ''}`));
    input.appendChild(this.detailSnapshotTable(doc, snapshot, selectedIndexes));
    body.appendChild(input);

    const action = this.detailSection(doc, '② 集計へ投入', 'is-criteria');
    this.detailKeyValue(doc, action, 'Field', pattern?.target_field ?? '', { mono: true });
    this.detailKeyValue(doc, action, 'Aggregate', pattern?.aggregate_operator
      ? `${pattern.aggregate_operator} / ${pattern.aggregate_scope}`
      : 'NO AGGREGATE');
    this.detailKeyValue(doc, action, 'Selected Indexes', this.detailJson(selectedIndexes), { pre: true });
    this.detailKeyValue(doc, action, 'Expected Metric Set', pattern?.expected_metric_set ?? '', { mono: true });
    body.appendChild(action);

    const expected = this.detailSection(doc, '③ Expected Result', 'is-expected');
    this.detailKeyValue(doc, expected, 'ExpectedDef', pattern?.expected_def_type ?? 'ScalarExpectedDef', { mono: true });
    expected.appendChild(this.renderExpectedMetricTable(doc, generatedCases));
    body.appendChild(expected);
  }

  renderCsvFactSections(doc, row, body) {
    const pattern = row?.planned_pattern ?? {};
    const generatedCase = (pattern?.generated_cases ?? [])[0] ?? {};
    const snapshot = Array.isArray(generatedCase?.input_snapshot) ? generatedCase.input_snapshot : [];
    const selected = snapshot.filter(item => item?.selected === true);
    const expectedValue = generatedCase?.expected ?? {};
    const fieldNames = Array.isArray(expectedValue?.field_names) ? expectedValue.field_names : [];

    const input = this.detailSection(doc, '① 対象行の入力状況');
    this.detailKeyValue(doc, input, 'Target Data', generatedCase?.target_data_path ?? pattern?.target_data_path ?? '', { mono: true });
    this.detailKeyValue(doc, input, 'Row Scope', generatedCase?.row_scope ?? pattern?.row_scope ?? '', { mono: true });
    this.detailKeyValue(doc, input, 'Input Rows', snapshot.length);
    this.detailKeyValue(doc, input, 'Export Rows', selected.length);
    this.detailKeyValue(doc, input, 'Selected Rows', this.detailCsvSelectedRows(snapshot), { pre: true });
    body.appendChild(input);

    const action = this.detailSection(doc, '② CSV出力へ投入', 'is-criteria');
    this.detailKeyValue(doc, action, 'Action', '現在のGrid表示行をCSVとして出力する');
    this.detailKeyValue(doc, action, 'Columns', fieldNames.join(', '), { mono: true });
    this.detailKeyValue(doc, action, 'Column Count', fieldNames.length);
    body.appendChild(action);

    const expected = this.detailSection(doc, '③ Expected Result', 'is-expected');
    this.detailKeyValue(doc, expected, 'ExpectedDef', generatedCase?.expected_def_type ?? pattern?.expected_def_type ?? 'CsvExpectedDef', { mono: true });
    this.detailKeyValue(doc, expected, 'Rows', selected.length);
    this.detailKeyValue(doc, expected, 'UTF-8 BOM', expectedValue?.has_bom === true ? 'YES' : 'NO');
    const csvPreview = String(expectedValue?.csv_without_bom ?? '').split(/\r?\n/).filter(Boolean).slice(0, 6).join('\n');
    if (csvPreview) this.detailKeyValue(doc, expected, 'CSV Preview', csvPreview, { pre: true });
    body.appendChild(expected);
  }

  renderGenericFactSections(doc, row, body) {
    const pattern = row?.planned_pattern ?? null;
    const checks = Array.isArray(row?.checks) ? row.checks : [];
    const input = this.detailSection(doc, '① 対象値の入力状況');
    this.detailKeyValue(doc, input, 'Guarantee ID', row?.guarantee_id ?? '', { mono: true });
    this.detailKeyValue(doc, input, 'TestPattern', row?.test_pattern_id ?? '', { mono: true });
    if (pattern) {
      this.detailKeyValue(doc, input, 'Generation Mode', pattern?.generation_mode ?? '', { mono: true });
      if (pattern?.target_data_path) this.detailKeyValue(doc, input, 'Target Data', pattern.target_data_path, { mono: true });
      if (pattern?.input) this.detailKeyValue(doc, input, 'Input Snapshot', this.detailJson(pattern.input), { pre: true });
    } else {
      this.detailKeyValue(doc, input, 'Cases', row?.case_count ?? '');
      this.detailKeyValue(doc, input, 'Checks', row?.check_count ?? '');
    }
    body.appendChild(input);

    const action = this.detailSection(doc, '② 実行へ投入', 'is-criteria');
    this.detailKeyValue(doc, action, 'Observed At', row?.observed_at ?? '', { mono: true });
    this.detailKeyValue(doc, action, 'Observed Source', (row?.sources ?? []).join('\n'), { pre: true });
    body.appendChild(action);

    const expected = this.detailSection(doc, '③ Expected Result', 'is-expected');
    expected.appendChild(this.renderMetricTable(doc, checks, 'expected'));
    body.appendChild(expected);
  }

  renderFactSections(doc, row, body) {
    const pattern = row?.planned_pattern ?? {};
    const mode = String(pattern?.generation_mode ?? '');
    const responsibilityCd = String(row?.responsibility_cd ?? pattern?.pattern_cd ?? '').toLowerCase();
    if (mode === 'AGGREGATE_SCALAR_CASE') {
      this.renderAggregateFactSections(doc, row, body);
      return;
    }
    if (mode === 'CSV_EXPORT_CASE') {
      this.renderCsvFactSections(doc, row, body);
      return;
    }
    if (mode === 'SEARCH_OPERATOR_MATRIX') {
      this.renderSearchFactSections(doc, row, body);
      return;
    }
    if (responsibilityCd === 'data_update_persist' || String(pattern?.pattern_cd ?? '').toUpperCase() === 'DATA_UPDATE_PERSIST') {
      this.renderDataUpdatePersistFactSections(doc, row, body);
      return;
    }
    this.renderGenericFactSections(doc, row, body);
  }

  render() {
    if (!this.hostElement) return;
    this.clearHost();

    const row = this.row;
    if (!row || typeof row !== 'object') return;

    const doc = this.hostElement.ownerDocument ?? globalThis.document;
    if (!doc?.createElement) throw new Error('ResponsibilityDiffResultPreviewComponent: document.createElement is required');

    const checks = Array.isArray(row.checks) ? row.checks : [];
    const diffCount = Number.isInteger(row.diff_count)
      ? row.diff_count
      : checks.filter(check => check?.pass !== true).length;
    const caseCount = Number.isInteger(row.case_count)
      ? row.case_count
      : new Set(checks.map(check => check?.case_id).filter(Boolean)).size;
    const checkCount = Number.isInteger(row.check_count) ? row.check_count : checks.length;

    const card = doc.createElement('section');
    card.className = 'child-card detail-subgrid-edit studio-subgrid-component responsibility-result-evidence-card is-readonly';

    const header = doc.createElement('div');
    header.className = 'detail-subgrid-header';

    const heading = doc.createElement('h3');
    heading.textContent = this.componentTitle;
    header.appendChild(heading);

    const meta = doc.createElement('div');
    meta.className = 'detail-subgrid-meta';
    [
      `Cases ${caseCount}`,
      `Checks ${checkCount}`,
      `Diff ${diffCount}`,
      row?.pass === true ? 'PASS' : 'FAIL'
    ].forEach(text => {
      const badge = doc.createElement('span');
      badge.className = 'badge';
      badge.textContent = text;
      meta.appendChild(badge);
    });
    header.appendChild(meta);
    card.appendChild(header);

    const pane = doc.createElement('div');
    pane.className = 'responsibility-result-evidence-pane';

    const detailHeader = doc.createElement('div');
    detailHeader.className = 'responsibility-preview-detail-header';
    const kicker = doc.createElement('div');
    kicker.className = 'responsibility-preview-detail-kicker';
    kicker.textContent = 'EXECUTION EVIDENCE';
    const title = doc.createElement('h3');
    title.textContent = String(row?.test_pattern_id ?? '');
    detailHeader.appendChild(kicker);
    detailHeader.appendChild(title);
    pane.appendChild(detailHeader);

    const body = doc.createElement('div');
    body.className = 'responsibility-preview-case-detail';

    this.renderFactSections(doc, row, body);

    const actual = this.detailSection(doc, '④ Actual', 'is-actual');
    actual.appendChild(this.renderMetricTable(doc, checks, 'actual'));
    body.appendChild(actual);

    const diff = this.detailSection(
      doc,
      '⑤ Diff',
      diffCount > 0 ? 'is-diff-fail' : 'is-diff-pass'
    );
    this.detailKeyValue(doc, diff, 'Result', row?.pass === true ? 'PASS' : 'FAIL');
    this.detailKeyValue(doc, diff, 'Summary', `${checkCount} checks / ${diffCount} diff`);
    diff.appendChild(this.renderMetricTable(doc, checks, 'diff'));
    body.appendChild(diff);

    const supplement = this.detailSection(doc, '補足情報', 'is-supplement');
    this.detailKeyValue(doc, supplement, 'Guarantee ID', row?.guarantee_id ?? '', { mono: true });
    this.detailKeyValue(doc, supplement, 'Observed At', row?.observed_at ?? '', { mono: true });
    this.detailKeyValue(doc, supplement, 'Observed Source', (row?.sources ?? []).join('\n'), { pre: true });
    this.detailKeyValue(doc, supplement, 'Runner', row?.source_runner ?? '', { mono: true });
    this.detailKeyValue(doc, supplement, 'Actual File', row?.actual_file ?? '', { mono: true });
    this.detailKeyValue(doc, supplement, 'Diff File', row?.diff_file ?? '', { mono: true });
    if (this.showRawJson) {
      if (row?.planned_pattern) this.detailDisclosure(doc, supplement, 'Saved Planned Pattern を表示', this.detailJson(row.planned_pattern));
      this.detailDisclosure(doc, supplement, 'Raw Checks を表示', JSON.stringify(checks, null, 2));
    }
    body.appendChild(supplement);

    pane.appendChild(body);
    card.appendChild(pane);
    this.hostElement.appendChild(card);
  }
}

registerEditorComponent(
  'responsibility_diff_result_preview',
  ({ config, services }) => new ResponsibilityDiffResultPreviewComponent(config, services)
);
