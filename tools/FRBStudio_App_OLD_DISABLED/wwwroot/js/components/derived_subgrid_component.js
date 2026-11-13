// v0.18.41-subgrid-component-data-derived
// Readonly derived SubGrid base.
// Derived rows are presentation results and must never be committed to canonical Data JSON.

class DerivedSubGridComponent extends SubGridComponent {
  get componentRole() {
    return 'derived';
  }

  get persistenceMode() {
    return 'derived-readonly';
  }

  isEditable() {
    return false;
  }

  buildRows(_context) {
    throw new Error(`${this.constructor.name}: buildRows(context) must be implemented`);
  }

  buildColumns(_rows, _context) {
    return this.config?.columns ?? [];
  }

  getRows() {
    return subGridComponentArray(this.buildRows(this.context));
  }

  getColumns(rows=this.getRows()) {
    const built = subGridComponentArray(this.buildColumns(rows, this.context))
      .map(subGridComponentColumn)
      .filter(Boolean);
    return built.length ? built : subGridComponentColumnsFromRows(rows);
  }

  commit() {
    throw new Error(`${this.constructor.name}: derived rows are readonly and cannot be committed to canonical Data`);
  }
}

globalThis.DerivedSubGridComponent = DerivedSubGridComponent;
