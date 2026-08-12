// v0.18.43-field-definition-editor-derived-preview
// Readonly Derived SubGrid for Registry default / Field override / resolved constraint comparison.

class DefinitionConstraintDiffComponent extends DefinitionVerificationDerivedSubGridComponent {
  get title() {
    return String(this.config?.caption ?? this.config?.title ?? 'Constraint Diff');
  }

  buildColumns() {
    return [
      { field: 'constraint', caption: 'Constraint' },
      { field: 'standard', caption: 'Standard' },
      { field: 'override', caption: 'Override' },
      { field: 'resolved', caption: 'Resolved' },
      { field: 'status', caption: 'Status' }
    ];
  }

  buildVerificationRows(result) {
    const contract = result?.field_contract ?? {};
    const issues = Array.isArray(contract.issues) ? contract.issues : [];
    return (contract.constraint_resolutions ?? []).map(resolution => {
      const rowIssues = issues.filter(issue =>
        issue?.constraint === resolution.constraint ||
        (Array.isArray(issue?.constraints) && issue.constraints.includes(resolution.constraint))
      );
      const hasError = rowIssues.some(issue => issue?.severity === 'ERROR');
      const status = hasError
        ? 'INVALID'
        : (resolution.status === 'UNRESOLVED'
          ? 'UNRESOLVED'
          : (resolution.override_defined ? 'OVERRIDE' : 'STANDARD'));

      return {
        constraint: resolution.constraint,
        standard: resolution.default_defined
          ? definitionVerificationComponentDisplayValue(resolution.default_value)
          : '未定義',
        override: resolution.override_defined
          ? definitionVerificationComponentDisplayValue(resolution.override_value)
          : '—',
        resolved: resolution.status === 'RESOLVED'
          ? definitionVerificationComponentDisplayValue(resolution.resolved_value)
          : 'UNRESOLVED',
        status,
        issue_codes: rowIssues.map(issue => issue.code).filter(Boolean).join(', '),
        override_defined: resolution.override_defined === true
      };
    });
  }

  getRowClassName(row) {
    const classes = ['definition-constraint-diff-row'];
    if (row?.override_defined) classes.push('is-override');
    if (row?.status === 'UNRESOLVED') classes.push('is-unresolved');
    if (row?.status === 'INVALID') classes.push('is-invalid');
    const highlightedConstraint = String(
      this.context?.highlight?.constraint
        ?? this.context?.highlight?.constraint_ref
        ?? ''
    );
    if (highlightedConstraint && String(row?.constraint ?? '') === highlightedConstraint) {
      classes.push('is-evidence-source');
    }
    return classes.join(' ');
  }

  getCellClassName(row, column) {
    const classes = [];
    if (row?.override_defined && ['override', 'resolved', 'status'].includes(column?.field)) {
      classes.push('definition-constraint-override-cell');
    }
    if (column?.field === 'status') classes.push(`definition-constraint-status-${String(row?.status ?? '').toLowerCase()}`);
    return classes.join(' ');
  }

  buildReadyNote(status, summary, result) {
    const contract = result?.field_contract ?? {};
    const overrideCount = (contract.constraint_resolutions ?? []).filter(item => item?.override_defined).length;
    return [
      `Definition Verification: ${status}`,
      `Override ${overrideCount}件`,
      `未解決 ${summary?.unresolved_constraint_count ?? 0}件`,
      `Issue ${summary?.issue_count ?? 0}件`
    ].join(' / ');
  }
}

registerEditorComponent(
  'definition_constraint_diff',
  ({ config, services }) => new DefinitionConstraintDiffComponent(config, services)
);

globalThis.DefinitionConstraintDiffComponent = DefinitionConstraintDiffComponent;
