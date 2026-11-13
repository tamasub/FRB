// v0.18.41-subgrid-component-data-derived
// Canonical Data SubGrid adapter.
// During migration it delegates mature objectArray/stringArray UI behavior to detail_subgrid_edit.js.

function dataSubGridFieldPath(config={}) {
  return String(config.field ?? config.fieldPath ?? config.field_path ?? '').trim();
}

function dataSubGridGetByPath(row, path) {
  if (!path) return row;
  if (typeof getByPath === 'function') return getByPath(row, path);
  return String(path).split('.').filter(Boolean).reduce((value, key) => value?.[key], row);
}

function dataSubGridSetByPath(row, path, value) {
  if (!row || !path) return;
  if (typeof setByPath === 'function') {
    setByPath(row, path, value);
    return;
  }
  const parts = String(path).split('.').filter(Boolean);
  let target = row;
  parts.slice(0, -1).forEach(key => {
    if (!target[key] || typeof target[key] !== 'object') target[key] = {};
    target = target[key];
  });
  if (parts.length) target[parts.at(-1)] = value;
}

class DataSubGridComponent extends SubGridComponent {
  constructor(config={}, services={}) {
    super(config, services);
    this._legacyCard = null;
  }

  get componentRole() {
    return 'data';
  }

  get persistenceMode() {
    return 'canonical';
  }

  get fieldPath() {
    return dataSubGridFieldPath(this.config);
  }

  get fieldDefinition() {
    if (this.config?.fieldDef && typeof this.config.fieldDef === 'object') return this.config.fieldDef;
    const fields = this.gridDef?.fields ?? [];
    const found = fields.find(field => field?.field === this.fieldPath);
    if (found) return found;
    const fieldType = this.config?.fieldType ?? this.config?.field_type ?? 'objectArray';
    return {
      field: this.fieldPath,
      caption: this.config?.caption ?? this.config?.title ?? this.fieldPath,
      type: fieldType,
      readonly: this.config?.readonly === true
    };
  }

  get title() {
    return String(this.config?.title ?? this.fieldDefinition?.caption ?? this.fieldPath ?? 'Data SubGrid');
  }

  getRows() {
    return subGridComponentArray(dataSubGridGetByPath(this.row, this.fieldPath));
  }

  isEditable() {
    const field = this.fieldDefinition;
    if (typeof isDetailSubGridEditable === 'function') return isDetailSubGridEditable(field);
    if (field?.readonly || field?.edit?.readonly) return false;
    if (this.config?.editable === false || this.config?.readonly === true) return false;
    return true;
  }

  render() {
    if (!this.hostElement) return;
    const field = this.fieldDefinition;
    const rows = this.getRows();

    // Compatibility adapter: keep the mature current Data SubGrid UI intact while classifying its persistence responsibility.
    if (field?.field && typeof createDetailSubGridCard === 'function') {
      clearSubGridComponentHost(this.hostElement);
      this._legacyCard = createDetailSubGridCard({
        field,
        row: this.row,
        gd: this.gridDef,
        data: rows
      });
      this._legacyCard.dataset.subgridRole = 'data';
      this._legacyCard.dataset.subgridPersistence = 'canonical';
      this.hostElement.appendChild(this._legacyCard);
      return;
    }

    this._legacyCard = null;
    super.render();
  }

  commit() {
    if (!this.row || !this.fieldPath) return false;
    if (!this.isEditable()) return false;
    if (!this._legacyCard || typeof collectDetailSubGridValue !== 'function') {
      throw new Error(`${this.constructor.name}: editable commit requires the Data SubGrid edit adapter`);
    }

    const value = collectDetailSubGridValue(this._legacyCard);
    dataSubGridSetByPath(this.row, this.fieldPath, value);
    this._legacyCard.classList?.remove?.('is-dirty');
    const badge = this._legacyCard.querySelector?.('.detail-subgrid-dirty-badge');
    if (badge) badge.textContent = '反映済み';
    return true;
  }

  onDestroy() {
    this._legacyCard = null;
  }
}

globalThis.DataSubGridComponent = DataSubGridComponent;
globalThis.dataSubGridFieldPath = dataSubGridFieldPath;
