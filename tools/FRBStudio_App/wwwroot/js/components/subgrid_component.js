// v0.18.41-subgrid-component-data-derived
// SubGrid UI Component base.
// The class owns SubGrid presentation/lifecycle only. Persistence and derived calculation belong to subclasses/services.

function subGridComponentArray(value) {
  if (Array.isArray(value)) return value;
  if (value == null || value === '') return [];
  return [value];
}

function subGridComponentColumn(raw) {
  if (typeof raw === 'string') return { field: raw, caption: raw, type: 'text' };
  if (!raw || typeof raw !== 'object') return null;
  const field = raw.field ?? raw.key ?? raw.name ?? raw.column;
  if (!field) return null;
  return {
    ...raw,
    field: String(field),
    caption: raw.caption ?? raw.label ?? raw.title ?? String(field),
    type: raw.type ?? raw.dataType ?? raw.data_type ?? 'text'
  };
}

function subGridComponentColumnsFromRows(rows=[]) {
  const names = new Set();
  subGridComponentArray(rows).forEach(row => {
    if (!row || typeof row !== 'object' || Array.isArray(row)) {
      names.add('value');
      return;
    }
    Object.keys(row).forEach(key => names.add(key));
  });
  if (!names.size) names.add('value');
  return [...names].map(field => ({ field, caption: field, type: 'text' }));
}

function subGridComponentCellText(value) {
  if (value == null) return '';
  if (typeof value === 'object') {
    try { return JSON.stringify(value); }
    catch { return String(value); }
  }
  return String(value);
}

function clearSubGridComponentHost(hostElement) {
  if (!hostElement) return;
  if (typeof hostElement.replaceChildren === 'function') {
    hostElement.replaceChildren();
    return;
  }
  while (hostElement.firstChild) hostElement.removeChild(hostElement.firstChild);
  if (Array.isArray(hostElement.children)) {
    [...hostElement.children].forEach(child => hostElement.removeChild?.(child));
  }
}

class SubGridComponent extends EditorComponent {
  get componentRole() {
    return 'subgrid';
  }

  get persistenceMode() {
    return 'none';
  }

  get title() {
    return String(this.config?.title ?? this.config?.caption ?? this.config?.id ?? 'SubGrid');
  }

  isEditable() {
    return false;
  }

  getRows() {
    return [];
  }

  getColumns(rows=this.getRows()) {
    const configured = subGridComponentArray(this.config?.columns)
      .map(subGridComponentColumn)
      .filter(Boolean);
    return configured.length ? configured : subGridComponentColumnsFromRows(rows);
  }

  normalizeRows(rows=this.getRows()) {
    return subGridComponentArray(rows).map(row => {
      if (row && typeof row === 'object' && !Array.isArray(row)) return row;
      return { value: row };
    });
  }

  buildViewModel() {
    const rows = this.normalizeRows(this.getRows());
    const columns = this.getColumns(rows).map(subGridComponentColumn).filter(Boolean);
    return {
      title: this.title,
      role: this.componentRole,
      persistenceMode: this.persistenceMode,
      editable: this.isEditable(),
      rows,
      columns,
      note: String(this.config?.note ?? '')
    };
  }

  render() {
    if (!this.hostElement) return;
    const model = this.buildViewModel();
    clearSubGridComponentHost(this.hostElement);
    this.hostElement.appendChild(this.renderCard(model));
  }

  renderCard(model) {
    const doc = this.hostElement?.ownerDocument ?? globalThis.document;
    if (!doc?.createElement) throw new Error(`${this.constructor.name}: document.createElement is required`);

    const card = doc.createElement('section');
    card.className = `child-card detail-subgrid-edit studio-subgrid-component ${model.editable ? 'is-editable' : 'is-readonly'}`;
    card.dataset.subgridRole = model.role;
    card.dataset.subgridPersistence = model.persistenceMode;

    const header = doc.createElement('div');
    header.className = 'detail-subgrid-header';

    const heading = doc.createElement('h3');
    heading.textContent = model.title;
    header.appendChild(heading);

    const meta = doc.createElement('div');
    meta.className = 'detail-subgrid-meta';

    const count = doc.createElement('span');
    count.className = 'badge';
    count.textContent = `${model.rows.length}件`;
    meta.appendChild(count);

    const role = doc.createElement('span');
    role.className = 'detail-subgrid-dirty-badge';
    role.textContent = model.editable ? '編集可' : '読取専用';
    meta.appendChild(role);

    header.appendChild(meta);
    card.appendChild(header);

    card.appendChild(this.renderTable(model, doc));

    if (model.note) {
      const note = doc.createElement('div');
      note.className = 'detail-subgrid-note';
      note.textContent = model.note;
      card.appendChild(note);
    }

    return card;
  }

  // Common Table Renderer boundary for Component-based SubGrids.
  // Editing controls are intentionally not implemented here; DataSubGrid may delegate to the legacy editor during migration.
  renderTable(model, doc) {
    const wrap = doc.createElement('div');
    wrap.className = 'child-table-wrap detail-subgrid-table-wrap';

    const table = doc.createElement('table');
    table.className = 'detail-subgrid-table studio-subgrid-component-table';

    const thead = doc.createElement('thead');
    const headRow = doc.createElement('tr');
    model.columns.forEach(column => {
      const th = doc.createElement('th');
      th.dataset.column = column.field;
      th.textContent = column.caption ?? column.field;
      headRow.appendChild(th);
    });
    thead.appendChild(headRow);
    table.appendChild(thead);

    const tbody = doc.createElement('tbody');
    model.rows.forEach(row => {
      const tr = doc.createElement('tr');
      model.columns.forEach(column => {
        const td = doc.createElement('td');
        td.dataset.column = column.field;
        td.textContent = subGridComponentCellText(row?.[column.field]);
        tr.appendChild(td);
      });
      tbody.appendChild(tr);
    });
    table.appendChild(tbody);
    wrap.appendChild(table);
    return wrap;
  }

  commit() {
    throw new Error(`${this.constructor.name}: this SubGrid does not own a persistence contract`);
  }
}

globalThis.SubGridComponent = SubGridComponent;
globalThis.subGridComponentColumnsFromRows = subGridComponentColumnsFromRows;
globalThis.subGridComponentCellText = subGridComponentCellText;
