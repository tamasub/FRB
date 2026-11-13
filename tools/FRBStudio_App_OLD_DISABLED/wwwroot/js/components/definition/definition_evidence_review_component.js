// v0.18.46-definition-review-evidence-and-fielddefs-access
// Diff Detail companion that renders execution evidence beside the exact Field Definition snapshot.
// It reuses the same Definition UI Components used by the Field Definition Editor.

function definitionEvidenceReviewOptions(component) {
  const raw = component?.config?.config;
  return raw && typeof raw === 'object' ? raw : {};
}

function definitionEvidenceReviewDisplayValue(value) {
  if (value === undefined) return '';
  if (value === null) return 'null';
  if (typeof value === 'object') {
    try { return JSON.stringify(value); }
    catch { return String(value); }
  }
  if (typeof value === 'boolean') return value ? 'true' : 'false';
  return String(value);
}

function definitionEvidenceReviewFieldPath(row={}) {
  const direct = row.field_path ?? row.source?.field_path;
  if (direct) return String(direct);
  const target = String(row.target ?? '');
  return target.startsWith('$.') ? target : '';
}

function resolveDefinitionEvidenceReviewSnapshot(sourceData={}, row={}) {
  const fieldPath = definitionEvidenceReviewFieldPath(row);
  if (!fieldPath) return null;
  const fields = sourceData?.definition_review_snapshots?.fields;
  if (!Array.isArray(fields)) return null;
  return fields.find(item => String(item?.field_path ?? '') === fieldPath) ?? null;
}

class DefinitionEvidenceReviewComponent extends EditorComponent {
  constructor(config={}, services={}) {
    super(config, services);
    this._nestedHost = null;
    this._layoutBody = null;
    this._layoutDialog = null;
  }

  get componentOptions() {
    return definitionEvidenceReviewOptions(this);
  }

  get snapshot() {
    return resolveDefinitionEvidenceReviewSnapshot(this.sourceData ?? {}, this.row ?? {});
  }

  onMount() {
    this.#applyReviewLayout();
  }

  onUpdate() {
    this.#applyReviewLayout();
  }

  onDestroy() {
    this._nestedHost?.destroy();
    this._nestedHost = null;
    this._layoutBody?.classList?.remove('definition-evidence-review-layout');
    this._layoutDialog?.classList?.remove('detail-dialog-definition-evidence-review');
    this._layoutBody = null;
    this._layoutDialog = null;
  }

  #applyReviewLayout() {
    const body = this.hostElement?.closest?.('.dialog-body') ?? null;
    const dialog = this.hostElement?.closest?.('dialog') ?? null;
    if (this._layoutBody && this._layoutBody !== body) {
      this._layoutBody.classList?.remove('definition-evidence-review-layout');
    }
    if (this._layoutDialog && this._layoutDialog !== dialog) {
      this._layoutDialog.classList?.remove('detail-dialog-definition-evidence-review');
    }
    this._layoutBody = body;
    this._layoutDialog = dialog;
    body?.classList?.add('definition-evidence-review-layout');
    dialog?.classList?.add('detail-dialog-definition-evidence-review');
  }

  render() {
    if (!this.hostElement) return;
    this._nestedHost?.destroy();
    this._nestedHost = null;
    if (typeof this.hostElement.replaceChildren === 'function') this.hostElement.replaceChildren();
    else this.hostElement.innerHTML = '';

    const doc = this.hostElement.ownerDocument ?? globalThis.document;
    if (!doc?.createElement) return;

    const snapshot = this.snapshot;
    const row = this.row ?? {};
    const panel = doc.createElement('section');
    panel.className = 'definition-evidence-review-panel';

    const header = doc.createElement('div');
    header.className = 'definition-evidence-review-header';
    const title = doc.createElement('div');
    title.innerHTML = `<strong>${String(this.config?.caption ?? 'Linked Field Definition / Execution Evidence')}</strong><span>実行時Snapshot</span>`;
    header.appendChild(title);
    panel.appendChild(header);

    if (!snapshot) {
      const empty = doc.createElement('div');
      empty.className = 'definition-evidence-review-empty';
      empty.textContent = definitionEvidenceReviewFieldPath(row)
        ? 'このDiffにはField Definition実行時Snapshotがありません。Definition Testを再実行してEvidenceを更新してください。'
        : 'Cross Field等、このDetailは単項目Field Definition連動の対象外です。';
      panel.appendChild(empty);
      this.hostElement.appendChild(panel);
      return;
    }

    panel.appendChild(this.#renderExecutionEvidence(doc, row, snapshot));

    const captionSlot = doc.createElement('div');
    captionSlot.className = 'definition-evidence-review-slot definition-evidence-caption-slot';
    const constraintSlot = doc.createElement('div');
    constraintSlot.className = 'definition-evidence-review-slot';
    const patternSlot = doc.createElement('div');
    patternSlot.className = 'definition-evidence-review-slot';
    panel.append(captionSlot, constraintSlot, patternSlot);
    this.hostElement.appendChild(panel);

    const targetViewDefPath = String(
      this.componentOptions.targetViewDefPath
        ?? this.componentOptions.target_view_def_path
        ?? ''
    ).trim();
    const configs = [];
    const slots = {};

    if (targetViewDefPath) {
      configs.push({
        id: 'definition_evidence_target_caption',
        type: 'definition_target_caption',
        placement: 'caption',
        caption: 'Data項目名（Caption）',
        readonly: true,
        config: { targetViewDefPath }
      });
      slots.caption = captionSlot;
    }

    configs.push(
      {
        id: 'definition_evidence_constraint_resolution',
        type: 'definition_constraint_diff',
        placement: 'constraints',
        caption: 'Constraint Resolution — Standard / Override / Resolved',
        readonly: true
      },
      {
        id: 'definition_evidence_test_pattern',
        type: 'definition_test_preview',
        placement: 'patterns',
        caption: 'Generated TestPattern / Expected — Execution Evidence',
        readonly: true
      }
    );
    slots.constraints = constraintSlot;
    slots.patterns = patternSlot;

    const nestedContext = {
      row: snapshot.field_definition ?? {},
      rowIndex: this.rowIndex,
      mode: 'readonly',
      viewDef: this.viewDef,
      gridDef: this.gridDef,
      sourceData: this.sourceData,
      verificationResult: snapshot.verification_result ?? null,
      evidenceCheck: row,
      highlight: {
        patternKey: String(row.name ?? ''),
        constraint: String(row.constraint_ref ?? '')
      },
      services: this.serviceContext
    };

    this._nestedHost = new EditorComponentHost({ services: this.serviceContext });
    this._nestedHost.mount(configs, slots, nestedContext);
  }

  #renderExecutionEvidence(doc, row, snapshot) {
    const card = doc.createElement('section');
    card.className = 'definition-execution-evidence-card';

    const heading = doc.createElement('div');
    heading.className = 'definition-execution-evidence-heading';
    heading.innerHTML = '<strong>Execution Evidence</strong><span>実際に実行した値・期待・結果</span>';
    card.appendChild(heading);

    const items = [
      ['Field Path', definitionEvidenceReviewFieldPath(row)],
      ['Validation Type', row.validation_type_id ?? snapshot.validation_type_id ?? ''],
      ['Pattern', row.name ?? ''],
      ['Input', definitionEvidenceReviewDisplayValue(row.input)],
      ['Expected', row.expected ?? ''],
      ['Actual', row.actual ?? ''],
      ['Result', row.result ?? (row.pass === true ? 'PASS' : row.pass === false ? 'FAIL' : '')],
      ['Expected Reason', row.expected_reason_code ?? ''],
      ['Actual Reason', row.actual_reason_code ?? ''],
      ['Comparison', row.comparison_reason_code ?? '']
    ];

    const grid = doc.createElement('div');
    grid.className = 'definition-execution-evidence-grid';
    items.forEach(([labelText, valueText]) => {
      const item = doc.createElement('div');
      item.className = 'definition-execution-evidence-item';
      const label = doc.createElement('span');
      label.textContent = labelText;
      const value = doc.createElement('strong');
      value.textContent = String(valueText ?? '');
      if (labelText === 'Input') value.classList.add('is-json-like');
      if (labelText === 'Result') value.classList.add(`is-result-${String(valueText ?? '').toLowerCase()}`);
      item.append(label, value);
      grid.appendChild(item);
    });
    card.appendChild(grid);

    const source = doc.createElement('div');
    source.className = 'definition-execution-evidence-source';
    const capturedAt = this.sourceData?.definition_review_snapshots?.captured_at ?? '';
    const hash = this.sourceData?.definition_review_snapshots?.field_definition_source?.sha256 ?? '';
    source.textContent = `Snapshot: ${capturedAt || '—'}${hash ? ` / Field Definition SHA-256: ${hash}` : ''}`;
    card.appendChild(source);
    return card;
  }
}

registerEditorComponent(
  'definition_evidence_review',
  ({ config, services }) => new DefinitionEvidenceReviewComponent(config, services)
);

globalThis.definitionEvidenceReviewFieldPath = definitionEvidenceReviewFieldPath;
globalThis.resolveDefinitionEvidenceReviewSnapshot = resolveDefinitionEvidenceReviewSnapshot;
globalThis.DefinitionEvidenceReviewComponent = DefinitionEvidenceReviewComponent;
