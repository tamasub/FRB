// v0.18.46-definition-review-evidence-and-fielddefs-access
// Readonly Derived SubGrid for TestPattern + Expected preview.
// Field Definition Editor derives current preview; Diff Review can inject frozen execution evidence.

class DefinitionTestPreviewComponent extends DefinitionVerificationDerivedSubGridComponent {
  get title() {
    return String(this.config?.caption ?? this.config?.title ?? 'TestPattern / Expected Preview');
  }

  get evidenceCheck() {
    const value = this.context?.evidenceCheck ?? this.context?.evidence_check ?? null;
    return value && typeof value === 'object' ? value : null;
  }

  get highlightedPatternKey() {
    return String(
      this.context?.highlight?.patternKey
        ?? this.context?.highlight?.pattern_key
        ?? this.evidenceCheck?.name
        ?? ''
    );
  }

  buildColumns() {
    const columns = [
      { field: 'pattern', caption: 'Pattern' },
      { field: 'category', caption: 'Category' },
      { field: 'input', caption: 'Input' },
      { field: 'expected', caption: 'Expected' }
    ];

    if (this.evidenceCheck) {
      columns.push(
        { field: 'actual', caption: 'Actual' },
        { field: 'result', caption: 'Result' }
      );
    }

    columns.push(
      { field: 'reason', caption: 'Reason' },
      { field: 'source', caption: 'Source' }
    );
    return columns;
  }

  buildVerificationRows(result) {
    const evidence = this.evidenceCheck;
    const highlighted = this.highlightedPatternKey;

    return (result?.test_patterns ?? []).map(pattern => {
      const patternKey = pattern.pattern_key ?? pattern.pattern_id ?? '';
      const isEvidenceTarget = Boolean(evidence && highlighted && String(patternKey) === highlighted);
      const row = {
        pattern: patternKey,
        category: pattern.category ?? '',
        input: definitionVerificationComponentDisplayValue(pattern.input, ''),
        expected: pattern.expected?.outcome ?? 'UNRESOLVED',
        actual: '',
        result: '',
        reason: pattern.expected?.reason_code ?? '',
        source: pattern.constraint_ref || pattern.expected?.source?.constraint_ref || pattern.source?.validation_type_id || result?.validation_type_id || '',
        is_evidence_target: isEvidenceTarget
      };

      if (isEvidenceTarget) {
        // The selected Diff row must show the value that was actually executed,
        // not a newly generated preview sample.
        row.input = definitionVerificationComponentDisplayValue(evidence.input, '');
        row.expected = evidence.expected ?? row.expected;
        row.actual = evidence.actual ?? 'UNRESOLVED';
        row.result = evidence.result ?? (evidence.pass === true ? 'PASS' : evidence.pass === false ? 'FAIL' : '');
        row.reason = evidence.expected_reason_code ?? row.reason;
        row.source = evidence.constraint_ref || row.source;
      }

      return row;
    });
  }

  getRowClassName(row) {
    const classes = ['definition-test-preview-row'];
    classes.push(`expected-${String(row?.expected ?? '').toLowerCase() || 'unknown'}`);
    if (row?.is_evidence_target) classes.push('is-evidence-target');
    return classes.join(' ');
  }

  getCellClassName(row, column) {
    const classes = [];
    if (column?.field === 'expected') {
      classes.push('definition-test-expected', `definition-test-expected-${String(row?.expected ?? '').toLowerCase()}`);
    }
    if (column?.field === 'result' && row?.result) {
      classes.push(`definition-test-result-${String(row.result).toLowerCase()}`);
    }
    if (row?.is_evidence_target) classes.push('definition-evidence-target-cell');
    return classes.join(' ');
  }

  buildReadyNote(status, summary) {
    const parts = [
      `Definition Verification: ${status}`,
      `TestPattern ${summary?.test_pattern_count ?? 0}件`,
      `ACCEPT ${summary?.accept_count ?? 0}件`,
      `REJECT ${summary?.reject_count ?? 0}件`,
      `UNRESOLVED ${summary?.unresolved_expected_count ?? 0}件`
    ];
    if (this.evidenceCheck && this.highlightedPatternKey) {
      parts.push(`Execution Evidence: ${this.highlightedPatternKey} を強調表示`);
    }
    return parts.join(' / ');
  }
}

registerEditorComponent(
  'definition_test_preview',
  ({ config, services }) => new DefinitionTestPreviewComponent(config, services)
);

globalThis.DefinitionTestPreviewComponent = DefinitionTestPreviewComponent;
