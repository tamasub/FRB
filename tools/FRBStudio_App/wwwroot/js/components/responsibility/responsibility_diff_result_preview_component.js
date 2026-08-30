// v0.18.121-responsibility-diff-testpattern-projection
// Readonly Result Evidence projection.
// IMPORTANT: this component does not re-derive Expected/Actual.
// It renders only the TestPattern summary + saved checks/evidence already persisted in the Diff JSON.

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
        ? ['Metric', 'Actual']
        : ['Metric', 'Expected', 'Actual', 'Result'];

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

      if (mode === 'diff') {
        const result = doc.createElement('td');
        result.className = 'is-result';
        result.textContent = check?.pass === true ? 'PASS' : 'FAIL';
        tr.appendChild(result);
      }

      body.appendChild(tr);
    });
    table.appendChild(body);
    wrap.appendChild(table);
    return wrap;
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

    const scope = this.detailSection(doc, '① 実行対象 / 検証量');
    this.detailKeyValue(doc, scope, 'Guarantee ID', row?.guarantee_id ?? '', { mono: true });
    this.detailKeyValue(doc, scope, 'TestPattern', row?.test_pattern_id ?? '', { mono: true });
    this.detailKeyValue(doc, scope, 'Cases', caseCount);
    this.detailKeyValue(doc, scope, 'Checks', checkCount);
    this.detailKeyValue(doc, scope, 'Diff', diffCount);
    body.appendChild(scope);

    const expected = this.detailSection(doc, '② Expected Result', 'is-expected');
    expected.appendChild(this.renderMetricTable(doc, checks, 'expected'));
    body.appendChild(expected);

    const actual = this.detailSection(doc, '③ Actual Result', 'is-actual');
    actual.appendChild(this.renderMetricTable(doc, checks, 'actual'));
    body.appendChild(actual);

    const diff = this.detailSection(
      doc,
      '④ Diff / 判定',
      diffCount > 0 ? 'is-diff-fail' : 'is-diff-pass'
    );
    this.detailKeyValue(doc, diff, 'Result', row?.pass === true ? 'PASS' : 'FAIL');
    this.detailKeyValue(doc, diff, 'Summary', `${checkCount} checks / ${diffCount} diff`);
    diff.appendChild(this.renderMetricTable(doc, checks, 'diff'));
    body.appendChild(diff);

    const evidence = this.detailSection(doc, '★ 観測Evidence / 事実根拠', 'is-rule');
    this.detailKeyValue(doc, evidence, 'Observed At', row?.observed_at ?? '', { mono: true });
    this.detailKeyValue(doc, evidence, 'Observed Source', (row?.sources ?? []).join('\n'), { pre: true });
    this.detailKeyValue(doc, evidence, 'Runner', row?.source_runner ?? '', { mono: true });
    this.detailKeyValue(doc, evidence, 'Actual File', row?.actual_file ?? '', { mono: true });
    this.detailKeyValue(doc, evidence, 'Diff File', row?.diff_file ?? '', { mono: true });
    if (this.showRawJson) {
      this.detailDisclosure(doc, evidence, 'Raw Checks を表示', JSON.stringify(checks, null, 2));
    }
    body.appendChild(evidence);

    pane.appendChild(body);
    card.appendChild(pane);
    this.hostElement.appendChild(card);
  }
}

registerEditorComponent(
  'responsibility_diff_result_preview',
  ({ config, services }) => new ResponsibilityDiffResultPreviewComponent(config, services)
);

globalThis.ResponsibilityDiffResultPreviewComponent = ResponsibilityDiffResultPreviewComponent;
