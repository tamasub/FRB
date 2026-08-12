// v0.18.43-field-definition-editor-derived-preview
// Readonly Derived SubGrid for TestPattern + Expected preview.

class DefinitionTestPreviewComponent extends DefinitionVerificationDerivedSubGridComponent {
  get title() {
    return String(this.config?.caption ?? this.config?.title ?? 'TestPattern / Expected Preview');
  }

  buildColumns() {
    return [
      { field: 'pattern', caption: 'Pattern' },
      { field: 'category', caption: 'Category' },
      { field: 'input', caption: 'Input' },
      { field: 'expected', caption: 'Expected' },
      { field: 'reason', caption: 'Reason' },
      { field: 'source', caption: 'Source' }
    ];
  }

  buildVerificationRows(result) {
    return (result?.test_patterns ?? []).map(pattern => ({
      pattern: pattern.pattern_key ?? pattern.pattern_id ?? '',
      category: pattern.category ?? '',
      input: definitionVerificationComponentDisplayValue(pattern.input, ''),
      expected: pattern.expected?.outcome ?? 'UNRESOLVED',
      reason: pattern.expected?.reason_code ?? '',
      source: pattern.constraint_ref || pattern.source?.validation_type_id || result?.validation_type_id || ''
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

  buildReadyNote(status, summary) {
    return [
      `Definition Verification: ${status}`,
      `TestPattern ${summary?.test_pattern_count ?? 0}件`,
      `ACCEPT ${summary?.accept_count ?? 0}件`,
      `REJECT ${summary?.reject_count ?? 0}件`,
      `UNRESOLVED ${summary?.unresolved_expected_count ?? 0}件`
    ].join(' / ');
  }
}

registerEditorComponent(
  'definition_test_preview',
  ({ config, services }) => new DefinitionTestPreviewComponent(config, services)
);

globalThis.DefinitionTestPreviewComponent = DefinitionTestPreviewComponent;
