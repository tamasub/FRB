// v0.16.2-detail-subgrid-table-edit-core-mvp
// Detail内 objectArray / stringArray を、特定フィールド名に依存せず編集するMVP。
// NOTE: This is the MVP implementation for objectArray/stringArray editing.
// The common editing behavior should later be extracted into Studio Table Edit Core
// and shared with the Markdown table editor.

function detailSubGridConfig(field) {
  return field?.edit?.subGrid ?? field?.edit?.subgrid ?? field?.subGrid ?? field?.subgrid ?? {};
}

function isDetailSubGridEditable(field) {
  const cfg = detailSubGridConfig(field);
  if (field?.readonly || field?.edit?.readonly) return false;
  if (cfg.editable === false || cfg.readonly === true) return false;
  return true;
}

function normalizeSubGridColumn(raw) {
  if (typeof raw === 'string') return { field: raw, caption: raw, type: 'text' };
  if (!raw || typeof raw !== 'object') return null;
  const name = raw.field ?? raw.key ?? raw.name ?? raw.column;
  if (!name) return null;
  return {
    ...raw,
    field: String(name),
    caption: raw.caption ?? raw.label ?? raw.title ?? String(name),
    type: raw.type ?? raw.dataType ?? raw.data_type ?? 'text'
  };
}

function configuredSubGridColumns(field) {
  const cfg = detailSubGridConfig(field);
  const candidates =
    cfg.columns ?? cfg.itemFields ?? cfg.item_fields ??
    field?.edit?.columns ?? field?.edit?.itemFields ?? field?.edit?.item_fields ??
    field?.columns ?? field?.itemFields ?? field?.item_fields ?? [];
  return Array.isArray(candidates) ? candidates.map(normalizeSubGridColumn).filter(Boolean) : [];
}

function inferSubGridCellType(value, col={}) {
  const t = col.type ?? col.dataType ?? col.data_type;
  if (t && t !== 'text') return t;
  if (typeof value === 'boolean') return 'boolean';
  if (typeof value === 'number') return 'number';
  if (value && typeof value === 'object') return 'json';
  return t ?? 'text';
}

function objectArraySubGridColumns(field, data) {
  const configured = configuredSubGridColumns(field);
  const byName = new Map();
  configured.forEach(col => byName.set(col.field, col));

  normalizeArray(data).forEach(row => {
    if (!row || typeof row !== 'object' || Array.isArray(row)) return;
    Object.keys(row).forEach(key => {
      if (!byName.has(key)) byName.set(key, { field: key, caption: key, type: inferSubGridCellType(row[key]) });
    });
  });

  const defaultItem = detailSubGridConfig(field)?.defaultItem ?? field?.defaultItem ?? field?.edit?.defaultItem;
  if (defaultItem && typeof defaultItem === 'object' && !Array.isArray(defaultItem)) {
    Object.keys(defaultItem).forEach(key => {
      if (!byName.has(key)) byName.set(key, { field: key, caption: key, type: inferSubGridCellType(defaultItem[key]) });
    });
  }

  if (!byName.size) byName.set('value', { field: 'value', caption: 'value', type: 'text' });
  return [...byName.values()];
}

function subGridCellText(value) {
  if (value == null) return '';
  if (typeof value === 'object') return JSON.stringify(value, null, 2);
  return String(value);
}

function createSubGridCellControl({ value, column, editable, field }) {
  const type = inferSubGridCellType(value, column);
  const readonly = !editable || column.readonly || column.edit?.readonly;
  const control = column.control ?? column.edit?.control ?? (column.options ? 'select' : null);
  let input;

  if (type === 'boolean') {
    input = document.createElement('select');
    ['', 'true', 'false'].forEach(v => {
      const opt = document.createElement('option');
      opt.value = v;
      opt.textContent = v;
      input.appendChild(opt);
    });
    input.value = value === true ? 'true' : value === false ? 'false' : '';
  } else if (control === 'select' || Array.isArray(column.options)) {
    input = document.createElement('select');
    const blank = document.createElement('option');
    blank.value = '';
    blank.textContent = '';
    input.appendChild(blank);
    (column.options ?? []).forEach(opt => {
      const o = document.createElement('option');
      o.value = optionValue(opt, column);
      o.textContent = optionLabel(opt, column);
      input.appendChild(o);
    });
    input.value = value ?? '';
  } else if (type === 'number') {
    input = document.createElement('input');
    input.type = 'number';
    input.value = value ?? '';
  } else {
    const text = subGridCellText(value);
    const preferTextarea =
      type === 'textarea' || type === 'markdown' || type === 'json' ||
      column.control === 'textarea' || column.edit?.control === 'textarea' ||
      String(text).includes('\n') || String(text).length > 80;
    if (preferTextarea) {
      input = document.createElement('textarea');
      input.rows = Math.min(6, Math.max(2, String(text).split('\n').length));
      input.value = text;
    } else {
      input = document.createElement('input');
      input.type = 'text';
      input.value = text;
    }
  }

  input.className = 'detail-subgrid-cell-input';
  input.dataset.column = column.field;
  input.dataset.cellType = type;
  input.dataset.markdownFuture = (type === 'markdown' || column.markdown || field?.markdown || field?.edit?.markdown) ? 'true' : 'false';
  if (column.width) input.style.minWidth = typeof column.width === 'number' ? `${column.width}px` : String(column.width);
  if (readonly) input.disabled = true;
  input.addEventListener('input', () => markDetailSubGridDirty(input.closest('.detail-subgrid-edit')));
  input.addEventListener('change', () => markDetailSubGridDirty(input.closest('.detail-subgrid-edit')));
  input.addEventListener('keydown', (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
      e.preventDefault();
      if (typeof applyDetail === 'function') applyDetail(e);
    }
  });
  return input;
}

function createSubGridActionButton(label, title, onClick) {
  const btn = document.createElement('button');
  btn.type = 'button';
  btn.className = 'detail-subgrid-action-btn';
  btn.textContent = label;
  btn.title = title;
  btn.addEventListener('click', onClick);
  return btn;
}

function renumberDetailSubGridRows(card) {
  [...card.querySelectorAll('tbody tr')].forEach((tr, index) => {
    const no = tr.querySelector('.detail-subgrid-row-no');
    if (no) no.textContent = String(index + 1);
  });
}

function markDetailSubGridDirty(card) {
  if (!card) return;
  card.classList.add('is-dirty');
  const badge = card.querySelector('.detail-subgrid-dirty-badge');
  if (badge) badge.textContent = '未反映';
  if (typeof setStatus === 'function') setStatus('サブグリッドを編集中です。F12または反映ボタンで親JSONへ反映してください。');
}

function createStringArraySubGridRow({ value='', editable=true, card }) {
  const tr = document.createElement('tr');
  const op = document.createElement('td');
  op.className = 'detail-subgrid-row-actions';
  const no = document.createElement('span');
  no.className = 'detail-subgrid-row-no';
  op.appendChild(no);
  if (editable) {
    op.appendChild(createSubGridActionButton('＋▲', 'この行の上に追加', () => insertDetailSubGridRow(card, tr, 'before')));
    op.appendChild(createSubGridActionButton('＋▼', 'この行の下に追加', () => insertDetailSubGridRow(card, tr, 'after')));
    op.appendChild(createSubGridActionButton('削除', 'この行を削除', () => { tr.remove(); renumberDetailSubGridRows(card); markDetailSubGridDirty(card); }));
  }
  tr.appendChild(op);

  const td = document.createElement('td');
  const input = createSubGridCellControl({ value, column: { field: 'value', caption: 'value', type: 'textarea' }, editable, field: { type: 'stringArray' } });
  td.appendChild(input);
  tr.appendChild(td);
  return tr;
}

function createObjectArraySubGridRow({ item={}, columns, editable=true, card, field }) {
  const tr = document.createElement('tr');
  const op = document.createElement('td');
  op.className = 'detail-subgrid-row-actions';
  if (editable) {
    op.appendChild(createSubGridActionButton('＋▲', 'この行の上に追加', () => insertDetailSubGridRow(card, tr, 'before')));
    op.appendChild(createSubGridActionButton('＋▼', 'この行の下に追加', () => insertDetailSubGridRow(card, tr, 'after')));
    op.appendChild(createSubGridActionButton('削除', 'この行を削除', () => { tr.remove(); renumberDetailSubGridRows(card); markDetailSubGridDirty(card); }));
  }
  tr.appendChild(op);

  columns.forEach(col => {
    const td = document.createElement('td');
    const value = item && typeof item === 'object' ? item[col.field] : undefined;
    td.appendChild(createSubGridCellControl({ value, column: col, editable, field }));
    tr.appendChild(td);
  });
  return tr;
}

function emptyObjectForColumns(columns) {
  const row = {};
  (columns ?? []).forEach(col => { row[col.field] = col.defaultValue ?? col.default ?? ''; });
  return row;
}

function insertDetailSubGridRow(card, baseRow=null, position='after') {
  if (!card) return;
  const type = card.dataset.subgridType;
  const tbody = card.querySelector('tbody');
  if (!tbody) return;
  let row;
  if (type === 'stringArray') {
    row = createStringArraySubGridRow({ value: '', editable: true, card });
  } else {
    const columns = [...card.querySelectorAll('thead th[data-column]')].map(th => ({
      field: th.dataset.column,
      caption: th.textContent,
      type: th.dataset.cellType || 'text'
    }));
    row = createObjectArraySubGridRow({ item: emptyObjectForColumns(columns), columns, editable: true, card, field: { type: 'objectArray' } });
  }

  if (!baseRow) tbody.appendChild(row);
  else if (position === 'before') tbody.insertBefore(row, baseRow);
  else tbody.insertBefore(row, baseRow.nextSibling);
  renumberDetailSubGridRows(card);
  markDetailSubGridDirty(card);
}

function createDetailSubGridCard({ field, row, gd, data }) {
  const editable = isDetailSubGridEditable(field);
  const card = document.createElement('div');
  card.className = 'child-card detail-subgrid-edit' + (editable ? ' is-editable' : ' is-readonly');
  card.dataset.subgridField = field.field;
  card.dataset.subgridType = field.type;

  const header = document.createElement('div');
  header.className = 'detail-subgrid-header';
  const title = document.createElement('h3');
  title.textContent = field.caption ?? field.field;
  header.appendChild(title);

  const meta = document.createElement('div');
  meta.className = 'detail-subgrid-meta';
  const count = document.createElement('span');
  count.className = 'badge';
  count.textContent = `${data.length}件`;
  meta.appendChild(count);
  const dirty = document.createElement('span');
  dirty.className = 'detail-subgrid-dirty-badge';
  dirty.textContent = editable ? '編集可' : '読取専用';
  meta.appendChild(dirty);
  if (editable) {
    meta.appendChild(createSubGridActionButton('+行', '末尾に行を追加', () => insertDetailSubGridRow(card)));
  }
  header.appendChild(meta);
  card.appendChild(header);

  const wrap = document.createElement('div');
  wrap.className = 'child-table-wrap detail-subgrid-table-wrap';
  const table = document.createElement('table');
  table.className = 'detail-subgrid-table';
  const thead = document.createElement('thead');
  const trh = document.createElement('tr');
  const actionTh = document.createElement('th');
  actionTh.className = 'detail-subgrid-action-th';
  actionTh.textContent = field.type === 'stringArray' ? '#' : '操作';
  trh.appendChild(actionTh);

  let columns = [];
  if (field.type === 'stringArray') {
    columns = [{ field: 'value', caption: 'value', type: 'textarea' }];
  } else {
    columns = objectArraySubGridColumns(field, data);
  }

  columns.forEach(col => {
    const th = document.createElement('th');
    th.textContent = col.caption ?? col.field;
    th.dataset.column = col.field;
    th.dataset.cellType = col.type ?? 'text';
    if (col.width) th.style.minWidth = typeof col.width === 'number' ? `${col.width}px` : String(col.width);
    trh.appendChild(th);
  });
  thead.appendChild(trh);
  table.appendChild(thead);

  const tbody = document.createElement('tbody');
  data.forEach(item => {
    const tr = field.type === 'stringArray'
      ? createStringArraySubGridRow({ value: item, editable, card })
      : createObjectArraySubGridRow({ item: item ?? {}, columns, editable, card, field });
    tbody.appendChild(tr);
  });
  table.appendChild(tbody);
  wrap.appendChild(table);
  card.appendChild(wrap);

  const note = document.createElement('div');
  note.className = 'detail-subgrid-note';
  note.textContent = editable
    ? 'セル編集・行追加・削除後、F12または反映ボタンで親JSONへ同期します。文字列セルはMarkdown原文を保持する前提です。'
    : 'この配列は読取専用です。';
  card.appendChild(note);

  renumberDetailSubGridRows(card);
  return card;
}

function readSubGridControlValue(input) {
  if (!input) return '';
  const type = input.dataset.cellType ?? 'text';
  const raw = input.value ?? '';
  if (type === 'boolean') {
    if (raw === 'true') return true;
    if (raw === 'false') return false;
    return null;
  }
  if (type === 'number') return raw === '' ? null : Number(raw);
  if (type === 'json') {
    if (!raw.trim()) return null;
    try { return JSON.parse(raw); } catch { return raw; }
  }
  return raw;
}

function collectDetailSubGridValue(card) {
  const type = card.dataset.subgridType;
  const rows = [...card.querySelectorAll('tbody tr')];
  if (type === 'stringArray') {
    return rows.map(tr => readSubGridControlValue(tr.querySelector('[data-column="value"]')));
  }

  const columns = [...card.querySelectorAll('thead th[data-column]')].map(th => th.dataset.column).filter(Boolean);
  return rows.map(tr => {
    const obj = {};
    columns.forEach(col => {
      const input = [...tr.querySelectorAll('[data-column]')].find(el => el.dataset.column === col);
      obj[col] = readSubGridControlValue(input);
    });
    return obj;
  });
}

function applyDetailSubGridEdits(row, gd) {
  if (!row) return;
  const root = $('detailDialog') ?? document;
  [...root.querySelectorAll('.detail-subgrid-edit')].forEach(card => {
    const fieldName = card.dataset.subgridField;
    const field = (gd?.fields ?? []).find(f => f.field === fieldName);
    if (!field || !isDetailSubGridEditable(field)) return;
    const value = collectDetailSubGridValue(card);
    setByPath(row, fieldName, value);
    card.classList.remove('is-dirty');
    const badge = card.querySelector('.detail-subgrid-dirty-badge');
    if (badge) badge.textContent = '反映済み';
  });
}
