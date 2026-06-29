// v0.16.2-detail-subgrid-table-edit-core-mvp
// v0.16.5.5-subgrid-auto-column-width: column widths are inferred by type/control/content kind, never by field/caption names.
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


function detailSubGridCssSize(value) {
  if (value == null || value === '') return '';
  if (typeof value === 'number') return `${value}px`;
  const text = String(value).trim();
  return /^\d+$/.test(text) ? `${text}px` : text;
}

function detailSubGridColumnSampleValues(data, column, limit=20) {
  const rows = normalizeArray(data);
  const values = [];
  for (const row of rows) {
    if (values.length >= limit) break;
    if (!row || typeof row !== 'object' || Array.isArray(row)) continue;
    values.push(row[column.field]);
  }
  return values;
}

function detailSubGridMeasureText(value) {
  const text = subGridCellText(value);
  const lines = String(text).split(/\r?\n/);
  return {
    text,
    length: text.length,
    lines: lines.length,
    maxLineLength: lines.reduce((max, line) => Math.max(max, line.length), 0)
  };
}

function detailSubGridColumnKind(column={}, sampleValues=[], field=null) {
  const declaredType = String(column.type ?? column.dataType ?? column.data_type ?? 'text').toLowerCase();
  const control = String(column.control ?? column.edit?.control ?? '').toLowerCase();
  const hasOptions = Array.isArray(column.options) || control === 'select';
  const sample = sampleValues.find(v => v != null && v !== '');
  const sampleType = inferSubGridCellType(sample, column);

  if (declaredType === 'boolean' || sampleType === 'boolean' || typeof sample === 'boolean') return 'choice';
  if (hasOptions) return 'choice';
  if (declaredType === 'number' || declaredType === 'integer' || sampleType === 'number' || typeof sample === 'number') return 'number';
  if (declaredType === 'date') return 'date';
  if (declaredType === 'time') return 'time';
  if (declaredType === 'datetime' || declaredType === 'datetime-local' || declaredType === 'timestamp') return 'datetime';
  if (declaredType === 'json' || sampleType === 'json' || sampleValues.some(v => v && typeof v === 'object')) return 'longText';
  if (
    declaredType === 'textarea' || declaredType === 'markdown' ||
    control === 'textarea' || column.edit?.control === 'textarea' ||
    column.markdown || field?.markdown || field?.edit?.markdown ||
    sampleValues.some(v => {
      const m = detailSubGridMeasureText(v);
      return m.lines > 1 || m.length > 80 || m.maxLineLength > 48;
    })
  ) return 'longText';

  const maxLen = sampleValues.reduce((max, v) => Math.max(max, detailSubGridMeasureText(v).maxLineLength), 0);
  if (maxLen <= 12) return 'compactText';
  if (maxLen <= 28) return 'shortText';
  if (maxLen <= 52) return 'mediumText';
  return 'longText';
}

function detailSubGridColumnAutoWidth(column={}, data=[], field=null) {
  const explicitWidth = detailSubGridCssSize(column.width ?? column.grid?.width ?? column.edit?.width);
  if (explicitWidth) return { kind: 'explicit', width: explicitWidth, inputMinWidth: explicitWidth };

  const sampleValues = detailSubGridColumnSampleValues(data, column);
  const kind = detailSubGridColumnKind(column, sampleValues, field);
  const metrics = sampleValues.map(detailSubGridMeasureText);
  const maxLine = metrics.reduce((max, m) => Math.max(max, m.maxLineLength), 0);
  const maxLength = metrics.reduce((max, m) => Math.max(max, m.length), 0);

  let width = 150;
  if (kind === 'choice') {
    const optionLabels = Array.isArray(column.options) ? column.options.map(opt => optionLabel(opt, column)) : [];
    const optionMax = optionLabels.reduce((max, text) => Math.max(max, String(text ?? '').length), 0);
    width = Math.max(96, Math.min(180, 72 + Math.max(maxLine, optionMax) * 8));
  } else if (kind === 'number') {
    width = Math.max(88, Math.min(130, 72 + maxLine * 8));
  } else if (kind === 'date') {
    width = 132;
  } else if (kind === 'time') {
    width = 104;
  } else if (kind === 'datetime') {
    width = 176;
  } else if (kind === 'compactText') {
    width = Math.max(104, Math.min(136, 72 + maxLine * 7));
  } else if (kind === 'shortText') {
    width = Math.max(136, Math.min(180, 76 + maxLine * 7));
  } else if (kind === 'mediumText') {
    width = Math.max(180, Math.min(260, 84 + maxLine * 6));
  } else {
    // 長文系はフィールド名ではなく type/control/値の長さ・改行で判定する。
    // 横幅が短いとtextareaが「ちんけ」に見えるため、最低幅を厚めに確保する。
    width = Math.max(320, Math.min(520, 260 + Math.min(Math.max(maxLine, maxLength / 3), 72) * 3));
  }

  return {
    kind,
    width: `${Math.round(width)}px`,
    inputMinWidth: `${Math.max(72, Math.round(width) - 18)}px`
  };
}

function applyDetailSubGridColumnLayoutToCell(el, column={}) {
  if (!el || !column) return;
  const width = detailSubGridCssSize(column.__autoWidth ?? column.width ?? column.grid?.width ?? column.edit?.width);
  const kind = column.__autoKind;
  if (kind) el.dataset.subgridKind = kind;
  if (width) {
    el.style.width = width;
    el.style.minWidth = width;
  }
}

function decorateDetailSubGridColumnsWithAutoLayout(columns=[], data=[], field=null) {
  return (columns ?? []).map(col => {
    const layout = detailSubGridColumnAutoWidth(col, data, field);
    return {
      ...col,
      __autoKind: layout.kind,
      __autoWidth: layout.width,
      __autoInputMinWidth: layout.inputMinWidth
    };
  });
}

function createSubGridCellControl({ value, column, editable, field }) {
  const type = inferSubGridCellType(value, column);
  const readonly = !editable || column.readonly || column.edit?.readonly;
  const control = column.control ?? column.edit?.control ?? (column.options ? 'select' : null);
  let input;

  if (type === 'boolean') {
    const boolValue = (value === true || value === 'true') ? true : ((value === false || value === 'false') ? false : null);
    if (control === 'checkbox') {
      input = document.createElement('input');
      input.type = 'checkbox';
      input.checked = boolValue === true;
    } else {
      input = document.createElement('select');
      ['true', 'false'].forEach(v => {
        const opt = document.createElement('option');
        opt.value = v;
        opt.textContent = v;
        input.appendChild(opt);
      });
      // boolean列は空optionを持たせない。文字列true/falseも既存値として保持する。
      input.value = boolValue === false ? 'false' : 'true';
    }
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
    setSelectValuePreservingUnknown(input, column, value);
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
      input.rows = Math.min(4, Math.max(1, String(text).split('\n').length));
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
  const inputMinWidth = detailSubGridCssSize(column.__autoInputMinWidth ?? column.width ?? column.grid?.width ?? column.edit?.width);
  if (inputMinWidth) input.style.minWidth = inputMinWidth;
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


function detailSubGridPreviewMarkdownConfig(field=null, column=null) {
  const fallback = { enabled: true, allowLinks: true, allowImages: false };
  if (typeof normalizeChatMarkdownConfig === 'function') {
    const cfg = normalizeChatMarkdownConfig(
      fallback,
      field?.markdown,
      field?.edit?.markdown,
      column?.markdown,
      column?.edit?.markdown
    );
    return { ...fallback, ...cfg, enabled: true };
  }
  return fallback;
}

function detailSubGridPreviewHtml(value, field=null, column=null) {
  if (value == null || value === '') return '<span class="detail-subgrid-preview-empty">(空)</span>';
  if (typeof value === 'boolean') return value ? 'true' : 'false';
  if (typeof value === 'number') return String(value);
  if (typeof value === 'object') {
    const text = JSON.stringify(value, null, 2);
    return `<pre><code>${typeof escapeHtmlText === 'function' ? escapeHtmlText(text) : text}</code></pre>`;
  }
  const text = String(value);
  const cfg = detailSubGridPreviewMarkdownConfig(field, column);
  if (typeof renderMarkdownContent === 'function') return renderMarkdownContent(text, cfg);
  return typeof escapeHtmlText === 'function' ? escapeHtmlText(text) : text;
}

function normalizePreviewRows(rows, type) {
  const arr = Array.isArray(rows) ? rows : [];
  if (type === 'stringArray') return arr.map((value, i) => ({ __no: i + 1, value }));
  return arr.map((row, i) => (row && typeof row === 'object' && !Array.isArray(row)) ? row : { __no: i + 1, value: row });
}

function showDetailSubGridPreview({ title='プレビュー', rows=[], columns=[], field=null, type='objectArray', note='' }={}) {
  document.querySelectorAll('.detail-subgrid-preview-overlay').forEach(el => {
    try { if (typeof el.close === 'function' && el.open) el.close(); } catch { /* ignore */ }
    el.remove();
  });
  const previewRows = normalizePreviewRows(rows, type);
  const previewColumns = (columns && columns.length) ? columns : [{ field: 'value', caption: 'value', type: 'textarea' }];

  // v0.16.5-grid-card-document-renderer:
  // detailDialog(showModal) の上から開くPreviewは、div overlayではなくdialogでtop-layerへ載せる。
  // これにより、編集ダイアログの背面へPreviewが隠れる問題を防ぐ。
  const overlay = document.createElement('dialog');
  overlay.className = 'detail-subgrid-preview-overlay';
  const closePreview = () => {
    try { if (typeof overlay.close === 'function' && overlay.open) overlay.close(); } catch { /* ignore */ }
    overlay.remove();
  };
  overlay.addEventListener('click', (e) => {
    if (e.target === overlay) closePreview();
  });
  overlay.addEventListener('cancel', (e) => {
    e.preventDefault();
    closePreview();
  });

  const dialog = document.createElement('div');
  dialog.className = 'detail-subgrid-preview-dialog';
  dialog.setAttribute('role', 'document');

  const header = document.createElement('div');
  header.className = 'detail-subgrid-preview-header';
  const headingWrap = document.createElement('div');
  const kicker = document.createElement('div');
  kicker.className = 'detail-subgrid-preview-kicker';
  kicker.textContent = 'Grid Preview';
  const h2 = document.createElement('h2');
  h2.textContent = title;
  headingWrap.appendChild(kicker);
  headingWrap.appendChild(h2);
  header.appendChild(headingWrap);
  const close = document.createElement('button');
  close.type = 'button';
  close.className = 'icon-button';
  close.textContent = '×';
  close.setAttribute('aria-label', '閉じる');
  close.addEventListener('click', closePreview);
  header.appendChild(close);
  dialog.appendChild(header);

  const summary = document.createElement('div');
  summary.className = 'detail-subgrid-preview-summary';
  summary.textContent = `${previewRows.length}件 / ${previewColumns.length}列` + (note ? ` — ${note}` : '');
  dialog.appendChild(summary);

  const body = document.createElement('div');
  body.className = 'detail-subgrid-preview-body';
  if (!previewRows.length) {
    const empty = document.createElement('div');
    empty.className = 'detail-subgrid-preview-empty-card';
    empty.textContent = 'プレビュー対象の行がありません。';
    body.appendChild(empty);
  } else {
    previewRows.forEach((row, index) => {
      const card = document.createElement('section');
      card.className = 'detail-subgrid-preview-card';
      const cardTitle = document.createElement('div');
      cardTitle.className = 'detail-subgrid-preview-card-title';
      const idColumn = previewColumns.find(c => /(^|_)(id|no)$/.test(String(c.field)) || String(c.field).endsWith('_id'));
      const idText = idColumn ? (row?.[idColumn.field] ?? '') : '';
      cardTitle.textContent = idText ? `${index + 1}. ${idText}` : `${index + 1}件目`;
      card.appendChild(cardTitle);

      previewColumns.forEach(col => {
        const item = document.createElement('div');
        item.className = 'detail-subgrid-preview-field';
        const label = document.createElement('div');
        label.className = 'detail-subgrid-preview-label';
        label.textContent = col.caption ?? col.field;
        const value = document.createElement('div');
        value.className = 'detail-subgrid-preview-value markdown-rendered';
        value.innerHTML = detailSubGridPreviewHtml(row?.[col.field], field, col);
        item.appendChild(label);
        item.appendChild(value);
        card.appendChild(item);
      });
      body.appendChild(card);
    });
  }
  dialog.appendChild(body);
  overlay.appendChild(dialog);
  document.body.appendChild(overlay);
  if (typeof overlay.showModal === 'function') overlay.showModal();
  else overlay.setAttribute('open', '');
  close.focus();
}

function enrichSubGridColumnsWithFieldConfig(columns=[], field=null) {
  const configured = configuredSubGridColumns(field);
  const byField = new Map(configured.map(col => [col.field, col]));
  return (columns ?? []).map(col => {
    const cfg = byField.get(col.field) ?? {};
    return {
      ...cfg,
      ...col,
      caption: col.caption ?? cfg.caption ?? col.field,
      type: col.type ?? cfg.type ?? 'text',
      control: col.control ?? cfg.control,
      edit: col.edit ?? cfg.edit,
      options: col.options ?? cfg.options,
      markdown: col.markdown ?? cfg.markdown,
      width: col.width ?? cfg.width
    };
  });
}

function detailSubGridColumnsFromCard(card, field=null) {
  const columns = [...card.querySelectorAll('thead th[data-column]')].map(th => ({
    field: th.dataset.column,
    caption: th.textContent,
    type: th.dataset.cellType || 'text',
    __autoKind: th.dataset.subgridKind,
    __autoWidth: th.style.width || th.style.minWidth || '',
    __autoInputMinWidth: th.dataset.subgridInputMinWidth || ''
  })).filter(c => c.field);
  return enrichSubGridColumnsWithFieldConfig(columns, field).map(col => ({
    ...col,
    __autoKind: col.__autoKind,
    __autoWidth: col.__autoWidth,
    __autoInputMinWidth: col.__autoInputMinWidth
  }));
}

function openDetailSubGridPreview(card, field) {
  if (!card) return;
  const type = card.dataset.subgridType;
  const rows = collectDetailSubGridValue(card);
  const columns = type === 'stringArray'
    ? [{ field: 'value', caption: 'value', type: 'textarea' }]
    : detailSubGridColumnsFromCard(card, field);
  showDetailSubGridPreview({
    title: `${field?.caption ?? card.dataset.subgridField ?? 'Grid'} プレビュー`,
    rows,
    columns,
    field,
    type,
    note: '未反映の編集中セルも含めて表示します'
  });
}


function detailSubGridEditorColumns(card, field) {
  if (!card) return [];
  const type = card.dataset.subgridType;
  if (type === 'stringArray') return [{ field: 'value', caption: 'value', type: 'textarea' }];
  const fromTable = detailSubGridColumnsFromCard(card, field);
  if (fromTable.length) return fromTable;
  return configuredSubGridColumns(field);
}

function detailSubGridEditorRowTitle(row, index, columns=[]) {
  const idColumn = columns.find(c => /(^|_)(id|no)$/.test(String(c.field)) || String(c.field).endsWith('_id'));
  const idText = idColumn ? (row?.[idColumn.field] ?? '') : '';
  return idText ? `${index + 1}. ${idText}` : `${index + 1}件目`;
}

function normalizeRowsForDetailSubGridEditor(rows, type) {
  const arr = Array.isArray(rows) ? rows : [];
  if (type === 'stringArray') return arr.map(value => ({ value }));
  return arr.map(row => (row && typeof row === 'object' && !Array.isArray(row)) ? { ...row } : { value: row });
}

function denormalizeRowsFromDetailSubGridEditor(rows, type) {
  const arr = Array.isArray(rows) ? rows : [];
  if (type === 'stringArray') return arr.map(row => row?.value ?? '');
  return arr.map(row => (row && typeof row === 'object' && !Array.isArray(row)) ? { ...row } : { value: row });
}

function replaceDetailSubGridRows(card, rows, field, columns) {
  if (!card) return;
  const type = card.dataset.subgridType;
  const tbody = card.querySelector('tbody');
  if (!tbody) return;
  tbody.innerHTML = '';
  const nextRows = denormalizeRowsFromDetailSubGridEditor(rows, type);
  nextRows.forEach(item => {
    const tr = type === 'stringArray'
      ? createStringArraySubGridRow({ value: item, editable: true, card, column: columns?.[0] })
      : createObjectArraySubGridRow({ item: item ?? {}, columns, editable: true, card, field });
    tbody.appendChild(tr);
  });
  const count = card.querySelector('.detail-subgrid-meta .badge');
  if (count) count.textContent = `${nextRows.length}件`;
  renumberDetailSubGridRows(card);
  markDetailSubGridDirty(card);
}


function isSubGridLongTextColumn(column, value, field=null) {
  const type = inferSubGridCellType(value, column);
  const control = column?.control ?? column?.edit?.control;
  const text = subGridCellText(value);
  return Boolean(
    type === 'textarea' || type === 'markdown' || type === 'json' ||
    control === 'textarea' || column?.edit?.control === 'textarea' ||
    column?.markdown || field?.markdown || field?.edit?.markdown ||
    String(text).includes('\n') || String(text).length > 80
  );
}

function createDetailSubGridPreviewEditValue({ rowIndex, column, itemRow, field, onValueChange }) {
  const value = itemRow?.[column.field];
  const longText = isSubGridLongTextColumn(column, value, field);

  // Select / boolean / short values stay as always-visible controls.
  // Only long textarea/markdown-like cells use click-to-edit, blur-to-preview.
  if (!longText) {
    const input = createSubGridCellControl({ value, column, editable: true, field });
    input.classList.add('detail-subgrid-card-live-control');
    const sync = () => onValueChange(rowIndex, column, input);
    input.addEventListener('input', sync);
    input.addEventListener('change', sync);
    input.addEventListener('blur', sync);
    return input;
  }

  const box = document.createElement('div');
  box.className = 'detail-subgrid-card-preview-edit-value markdown-rendered is-editable';
  box.tabIndex = 0;
  box.title = 'クリックするとMarkdown原文を編集できます。フォーカスが外れるとプレビューへ戻ります。';

  let editing = false;
  const renderPreview = () => {
    editing = false;
    box.dataset.editing = 'false';
    box.innerHTML = '';
    const preview = document.createElement('div');
    preview.className = 'detail-subgrid-card-preview-rendered';
    preview.innerHTML = detailSubGridPreviewHtml(itemRow?.[column.field], field, column);
    box.appendChild(preview);
  };

  const enterEdit = () => {
    if (editing) return;
    editing = true;
    box.dataset.editing = 'true';
    const editorColumn = {
      ...column,
      type: column.type === 'json' ? 'json' : (column.type === 'markdown' ? 'markdown' : 'textarea'),
      control: column.control ?? 'textarea'
    };
    const input = createSubGridCellControl({ value: itemRow?.[column.field], column: editorColumn, editable: true, field });
    input.classList.add('detail-subgrid-card-preview-editor');
    box.innerHTML = '';
    box.appendChild(input);

    let done = false;
    const commit = () => {
      if (done) return;
      done = true;
      onValueChange(rowIndex, editorColumn, input);
      renderPreview();
    };
    const cancel = () => {
      if (done) return;
      done = true;
      renderPreview();
    };

    input.addEventListener('blur', commit, { once: true });
    input.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') {
        e.preventDefault();
        cancel();
        return;
      }
      if (e.key === 'F12' || ((e.ctrlKey || e.metaKey) && e.key === 'Enter')) {
        e.preventDefault();
        commit();
      }
    });
    requestAnimationFrame(() => {
      input.focus();
      if (input.select && input.tagName !== 'TEXTAREA') input.select();
    });
  };

  box.addEventListener('click', (e) => {
    if (editing) return;
    if (e.target.closest?.('a') && (e.ctrlKey || e.metaKey)) return;
    e.preventDefault();
    enterEdit();
  });
  box.addEventListener('keydown', (e) => {
    // v0.16.5.4-subgrid-preview-edit-textarea-enter-compact:
    // 編集中textareaのEnter改行を親boxのpreview起動ショートカットで潰さない。
    if (e.target !== box || editing) return;
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      enterEdit();
    }
  });
  renderPreview();
  return box;
}

function showDetailSubGridCardEditor({ card, field }={}) {
  if (!card) return;
  const type = card.dataset.subgridType;
  const columns = detailSubGridEditorColumns(card, field);
  let rows = normalizeRowsForDetailSubGridEditor(collectDetailSubGridValue(card), type);

  document.querySelectorAll('.detail-subgrid-card-editor-overlay').forEach(el => {
    try { if (typeof el.close === 'function' && el.open) el.close(); } catch { /* ignore */ }
    el.remove();
  });

  const overlay = document.createElement('dialog');
  overlay.className = 'detail-subgrid-preview-overlay detail-subgrid-card-editor-overlay';
  const closeEditor = () => {
    try { if (typeof overlay.close === 'function' && overlay.open) overlay.close(); } catch { /* ignore */ }
    overlay.remove();
  };
  overlay.addEventListener('click', (e) => { if (e.target === overlay) closeEditor(); });
  overlay.addEventListener('cancel', (e) => { e.preventDefault(); closeEditor(); });

  const dialog = document.createElement('div');
  dialog.className = 'detail-subgrid-preview-dialog detail-subgrid-card-editor-dialog';
  dialog.setAttribute('role', 'document');

  const header = document.createElement('div');
  header.className = 'detail-subgrid-preview-header detail-subgrid-card-editor-header';
  const headingWrap = document.createElement('div');
  const kicker = document.createElement('div');
  kicker.className = 'detail-subgrid-preview-kicker';
  kicker.textContent = 'Preview Edit';
  const h2 = document.createElement('h2');
  h2.textContent = `${field?.caption ?? card.dataset.subgridField ?? 'Grid'} プレビュー編集`;
  headingWrap.appendChild(kicker);
  headingWrap.appendChild(h2);
  header.appendChild(headingWrap);

  const headerActions = document.createElement('div');
  headerActions.className = 'detail-subgrid-card-editor-header-actions';
  const applyBtn = createSubGridActionButton('一覧へ反映', 'プレビュー編集内容をサブグリッド一覧へ反映して閉じる', () => {
    replaceDetailSubGridRows(card, rows, field, columns);
    closeEditor();
    if (typeof setStatus === 'function') setStatus('プレビュー編集内容をサブグリッド一覧へ反映しました。F12または反映ボタンで親JSONへ同期してください。');
  });
  applyBtn.classList.add('primary');
  const close = document.createElement('button');
  close.type = 'button';
  close.className = 'icon-button';
  close.textContent = '×';
  close.setAttribute('aria-label', '閉じる');
  close.addEventListener('click', closeEditor);
  headerActions.appendChild(applyBtn);
  headerActions.appendChild(close);
  header.appendChild(headerActions);
  dialog.appendChild(header);

  const summary = document.createElement('div');
  summary.className = 'detail-subgrid-preview-summary detail-subgrid-card-editor-summary';
  dialog.appendChild(summary);

  const body = document.createElement('div');
  body.className = 'detail-subgrid-preview-body detail-subgrid-card-editor-body';
  dialog.appendChild(body);

  const setRowValue = (rowIndex, column, input) => {
    // v0.16.5.6: preview編集内のboolean/checkbox/selectはSubGrid側の読取規約を優先する。
    // DocumentGrid共通読取はcheckbox.value(=on)をboolean falseへ誤変換し得るためここでは使わない。
    rows[rowIndex][column.field] = readSubGridControlValue(input);
  };

  const rerender = () => {
    summary.textContent = `${rows.length}件 / ${columns.length}列 — 長文はクリックで原文編集、blurでMarkdownプレビューへ戻ります。最後に「一覧へ反映」してください`;
    body.innerHTML = '';

    const toolbar = document.createElement('div');
    toolbar.className = 'detail-subgrid-card-editor-toolbar';
    toolbar.appendChild(createSubGridActionButton('＋末尾に追加', '末尾に空カードを追加', () => {
      rows.push(emptyObjectForColumns(columns));
      rerender();
    }));
    body.appendChild(toolbar);

    if (!rows.length) {
      const empty = document.createElement('div');
      empty.className = 'detail-subgrid-preview-empty-card';
      empty.textContent = 'プレビュー編集対象の行がありません。＋末尾に追加で行を作成できます。';
      body.appendChild(empty);
      return;
    }

    rows.forEach((row, index) => {
      const itemRow = row && typeof row === 'object' ? row : {};
      const section = document.createElement('section');
      section.className = 'detail-subgrid-preview-card detail-subgrid-card-editor-card';

      const title = document.createElement('div');
      title.className = 'detail-subgrid-preview-card-title detail-subgrid-card-editor-card-title';
      const titleText = document.createElement('span');
      titleText.textContent = detailSubGridEditorRowTitle(itemRow, index, columns);
      title.appendChild(titleText);

      const actions = document.createElement('div');
      actions.className = 'detail-subgrid-card-editor-row-actions';
      actions.appendChild(createSubGridActionButton('＋上', 'このカードの上に追加', () => { rows.splice(index, 0, emptyObjectForColumns(columns)); rerender(); }));
      actions.appendChild(createSubGridActionButton('＋下', 'このカードの下に追加', () => { rows.splice(index + 1, 0, emptyObjectForColumns(columns)); rerender(); }));
      actions.appendChild(createSubGridActionButton('複製', 'このカードを複製して下に追加', () => { rows.splice(index + 1, 0, JSON.parse(JSON.stringify(itemRow))); rerender(); }));
      actions.appendChild(createSubGridActionButton('↑', 'このカードを上へ移動', () => {
        if (index <= 0) return;
        const [moved] = rows.splice(index, 1);
        rows.splice(index - 1, 0, moved);
        rerender();
      }));
      actions.appendChild(createSubGridActionButton('↓', 'このカードを下へ移動', () => {
        if (index >= rows.length - 1) return;
        const [moved] = rows.splice(index, 1);
        rows.splice(index + 1, 0, moved);
        rerender();
      }));
      actions.appendChild(createSubGridActionButton('削除', 'このカードを削除', () => {
        rows.splice(index, 1);
        rerender();
      }));
      title.appendChild(actions);
      section.appendChild(title);

      columns.forEach(col => {
        const fieldLine = document.createElement('div');
        fieldLine.className = 'detail-subgrid-preview-field detail-subgrid-card-editor-field';
        const label = document.createElement('div');
        label.className = 'detail-subgrid-preview-label';
        label.textContent = col.caption ?? col.field;
        const value = document.createElement('div');
        value.className = 'detail-subgrid-card-editor-value';
        const editorField = { ...col, field: col.field, type: col.type ?? 'text' };
        value.appendChild(createDetailSubGridPreviewEditValue({
          rowIndex: index,
          column: editorField,
          itemRow,
          field,
          onValueChange: setRowValue
        }));
        fieldLine.appendChild(label);
        fieldLine.appendChild(value);
        section.appendChild(fieldLine);
      });

      body.appendChild(section);
    });
  };

  rerender();
  overlay.appendChild(dialog);
  document.body.appendChild(overlay);
  if (typeof overlay.showModal === 'function') overlay.showModal();
  else overlay.setAttribute('open', '');
  applyBtn.focus();
}

function openDetailSubGridCardEditor(card, field) {
  if (!card) return;
  showDetailSubGridCardEditor({ card, field });
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

function createStringArraySubGridRow({ value='', editable=true, card, column=null }) {
  const tr = document.createElement('tr');
  const op = document.createElement('td');
  op.className = 'detail-subgrid-row-actions';
  const no = document.createElement('span');
  no.className = 'detail-subgrid-row-no';
  op.appendChild(no);
  if (editable) {
    op.appendChild(createSubGridActionButton('▲', 'この行の上に追加', () => insertDetailSubGridRow(card, tr, 'before')));
    op.appendChild(createSubGridActionButton('▼', 'この行の下に追加', () => insertDetailSubGridRow(card, tr, 'after')));
    op.appendChild(createSubGridActionButton('削除', 'この行を削除', () => { tr.remove(); renumberDetailSubGridRows(card); markDetailSubGridDirty(card); }));
  }
  tr.appendChild(op);

  const td = document.createElement('td');
  const cellColumn = column ?? { field: 'value', caption: 'value', type: 'textarea' };
  applyDetailSubGridColumnLayoutToCell(td, cellColumn);
  const input = createSubGridCellControl({ value, column: cellColumn, editable, field: { type: 'stringArray' } });
  td.appendChild(input);
  tr.appendChild(td);
  return tr;
}

function createObjectArraySubGridRow({ item={}, columns, editable=true, card, field }) {
  const tr = document.createElement('tr');
  const op = document.createElement('td');
  op.className = 'detail-subgrid-row-actions';
  if (editable) {
    op.appendChild(createSubGridActionButton('▲', 'この行の上に追加', () => insertDetailSubGridRow(card, tr, 'before')));
    op.appendChild(createSubGridActionButton('▼', 'この行の下に追加', () => insertDetailSubGridRow(card, tr, 'after')));
    op.appendChild(createSubGridActionButton('削除', 'この行を削除', () => { tr.remove(); renumberDetailSubGridRows(card); markDetailSubGridDirty(card); }));
  }
  tr.appendChild(op);

  columns.forEach(col => {
    const td = document.createElement('td');
    applyDetailSubGridColumnLayoutToCell(td, col);
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
    row = createStringArraySubGridRow({ value: '', editable: true, card, column: { field: 'value', caption: 'value', type: 'textarea', __autoKind: 'longText', __autoWidth: '420px', __autoInputMinWidth: '402px' } });
  } else {
    const columns = [...card.querySelectorAll('thead th[data-column]')].map(th => ({
      field: th.dataset.column,
      caption: th.textContent,
      type: th.dataset.cellType || 'text',
      __autoKind: th.dataset.subgridKind,
      __autoWidth: th.style.width || th.style.minWidth || '',
      __autoInputMinWidth: th.dataset.subgridInputMinWidth || ''
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
  meta.appendChild(createSubGridActionButton('プレビュー編集', 'このグリッドを読み物兼編集画面で開く', () => openDetailSubGridCardEditor(card, field)));
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

  columns = decorateDetailSubGridColumnsWithAutoLayout(columns, data, field);

  columns.forEach(col => {
    const th = document.createElement('th');
    th.textContent = col.caption ?? col.field;
    th.dataset.column = col.field;
    th.dataset.cellType = col.type ?? 'text';
    if (col.__autoKind) th.dataset.subgridKind = col.__autoKind;
    if (col.__autoInputMinWidth) th.dataset.subgridInputMinWidth = col.__autoInputMinWidth;
    applyDetailSubGridColumnLayoutToCell(th, col);
    trh.appendChild(th);
  });
  thead.appendChild(trh);
  table.appendChild(thead);

  const tbody = document.createElement('tbody');
  data.forEach(item => {
    const tr = field.type === 'stringArray'
      ? createStringArraySubGridRow({ value: item, editable, card, column: columns?.[0] })
      : createObjectArraySubGridRow({ item: item ?? {}, columns, editable, card, field });
    tbody.appendChild(tr);
  });
  table.appendChild(tbody);
  wrap.appendChild(table);
  card.appendChild(wrap);

  const note = document.createElement('div');
  note.className = 'detail-subgrid-note';
  note.textContent = editable
    ? 'サブグリッドは一覧表示です。長文編集はプレビュー編集で行い、F12または反映ボタンで親JSONへ同期します。'
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
    if (input.type === 'checkbox') return Boolean(input.checked);
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
