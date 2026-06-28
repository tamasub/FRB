// v0.15.5-v0.15.5.3: ViewDef context model recognizer + main/target context panels
// ViewDef only declares where context data lives and how it is displayed.
// Actual Main Context refs belong in Data JSON (for example $.main_context_refs).
// Actual Target Context refs belong in each target row (for example context_refs[]).

function contextContractAsArray(value) {
  if (Array.isArray(value)) return value.filter(x => x != null);
  if (value == null) return [];
  return [value];
}

function contextContractString(value, fallback='') {
  const s = String(value ?? '').trim();
  return s || fallback;
}

function contextContractBool(value, fallback=false) {
  if (typeof value === 'boolean') return value;
  if (value == null || value === '') return fallback;
  const s = String(value).trim().toLowerCase();
  if (['true', '1', 'yes', 'y', 'on'].includes(s)) return true;
  if (['false', '0', 'no', 'n', 'off'].includes(s)) return false;
  return fallback;
}

function contextContractNumber(value, fallback=0) {
  const n = Number(value);
  return Number.isFinite(n) ? n : fallback;
}

function normalizeContextRefContract(raw, index=0, defaults={}) {
  if (!raw || typeof raw !== 'object' || Array.isArray(raw)) return null;
  const refId = contextContractString(raw.ref_id ?? raw.context_ref_id ?? raw.id, `context_ref_${index + 1}`);
  const required = contextContractBool(raw.required, contextContractBool(defaults.required, false));
  const failurePolicy = contextContractString(
    raw.failure_policy ?? raw.failurePolicy ?? defaults.failure_policy ?? defaults.failurePolicy,
    required ? 'stop_and_report' : 'warn_and_continue'
  );
  return {
    ref_id: refId,
    context_ref_id: refId,
    title: contextContractString(raw.title ?? raw.name, refId),
    target_path: contextContractString(raw.target_path ?? raw.targetPath ?? raw.path ?? raw.file ?? raw.url),
    read_timing: contextContractString(raw.read_timing ?? raw.readTiming ?? raw.timing ?? defaults.default_timing ?? defaults.defaultTiming, 'before_load'),
    required,
    enabled: contextContractBool(raw.enabled, true),
    failure_policy: failurePolicy,
    trust: contextContractString(raw.trust ?? raw.trust_category ?? raw.trustCategory ?? defaults.trust, required ? 'canonical' : 'reference'),
    trust_category: contextContractString(raw.trust_category ?? raw.trustCategory ?? raw.trust ?? defaults.trust, required ? 'canonical' : 'reference'),
    purpose: contextContractString(raw.purpose ?? raw.reason ?? raw.description),
    note: contextContractString(raw.note ?? raw.notes),
    sort_order: contextContractNumber(raw.sort_order ?? raw.sortOrder, index + 1)
  };
}

function normalizeRowContextContract(raw) {
  if (!raw || typeof raw !== 'object' || Array.isArray(raw)) return null;
  return {
    enabled: contextContractBool(raw.enabled, true),
    data_path: contextContractString(raw.data_path ?? raw.dataPath ?? raw.path, '$.context_refs'),
    row_ref_field: contextContractString(raw.row_ref_field ?? raw.rowRefField ?? raw.ref_field ?? raw.refField),
    id_field: contextContractString(raw.id_field ?? raw.idField, 'context_ref_id'),
    title_field: contextContractString(raw.title_field ?? raw.titleField, 'title'),
    target_path_field: contextContractString(raw.target_path_field ?? raw.targetPathField, 'target_path'),
    read_timing_field: contextContractString(raw.read_timing_field ?? raw.readTimingField ?? raw.timing_field ?? raw.timingField, 'read_timing'),
    failure_policy_field: contextContractString(raw.failure_policy_field ?? raw.failurePolicyField, 'failure_policy'),
    trust_field: contextContractString(raw.trust_field ?? raw.trustField ?? raw.trust_category_field ?? raw.trustCategoryField, 'trust_category'),
    purpose_field: contextContractString(raw.purpose_field ?? raw.purposeField, 'purpose')
  };
}

function normalizeReadContract(raw, sourceLabel='viewdef') {
  if (!raw || typeof raw !== 'object' || Array.isArray(raw)) return null;
  const defaults = {
    default_timing: raw.default_timing ?? raw.defaultTiming ?? 'before_load',
    failure_policy: raw.failure_policy ?? raw.failurePolicy ?? 'stop_and_report',
    trust: raw.trust ?? 'canonical'
  };
  const requiredRefs = [
    ...contextContractAsArray(raw.required_refs ?? raw.requiredRefs),
    ...contextContractAsArray(raw.preflight_rules ?? raw.preflightRules)
  ].map((item, i) => normalizeContextRefContract(item, i, { ...defaults, required: true })).filter(Boolean);
  const optionalRefs = contextContractAsArray(raw.optional_refs ?? raw.optionalRefs)
    .map((item, i) => normalizeContextRefContract(item, i, { ...defaults, required: false })).filter(Boolean);

  return {
    source: sourceLabel,
    enabled: contextContractBool(raw.enabled, true),
    contract_id: contextContractString(raw.contract_id ?? raw.contractId ?? raw.id, `${sourceLabel}_read_contract`),
    description: contextContractString(raw.description ?? raw.summary),
    default_timing: contextContractString(defaults.default_timing, 'before_load'),
    failure_policy: contextContractString(defaults.failure_policy, 'stop_and_report'),
    required_refs: requiredRefs,
    optional_refs: optionalRefs,
    main_context_data_path: contextContractString(raw.main_context_data_path ?? raw.mainContextDataPath ?? raw.required_refs_data_path ?? raw.requiredRefsDataPath),
    row_context: normalizeRowContextContract(raw.row_context ?? raw.rowContext ?? raw.row_context_refs ?? raw.rowContextRefs),
    notes: contextContractString(raw.notes ?? raw.note)
  };
}

function normalizeMainContextConfig(raw, legacyReadContract=null) {
  const cfg = (raw && typeof raw === 'object' && !Array.isArray(raw)) ? raw : {};
  const legacyPath = legacyReadContract?.main_context_data_path ?? '';
  return {
    enabled: contextContractBool(cfg.enabled, true),
    display_name: contextContractString(cfg.display_name ?? cfg.displayName, '主文脈'),
    data_path: contextContractString(cfg.data_path ?? cfg.dataPath ?? cfg.path ?? legacyPath, '$.main_context_refs'),
    description: contextContractString(cfg.description ?? cfg.summary),
    id_field: contextContractString(cfg.id_field ?? cfg.idField, 'context_ref_id'),
    title_field: contextContractString(cfg.title_field ?? cfg.titleField, 'title'),
    target_path_field: contextContractString(cfg.target_path_field ?? cfg.targetPathField, 'target_path'),
    read_timing_field: contextContractString(cfg.read_timing_field ?? cfg.readTimingField, 'read_timing'),
    failure_policy_field: contextContractString(cfg.failure_policy_field ?? cfg.failurePolicyField, 'failure_policy'),
    trust_category_field: contextContractString(cfg.trust_category_field ?? cfg.trustCategoryField ?? cfg.trust_field ?? cfg.trustField, 'trust_category'),
    purpose_field: contextContractString(cfg.purpose_field ?? cfg.purposeField, 'purpose'),
    required_field: contextContractString(cfg.required_field ?? cfg.requiredField, 'required'),
    enabled_field: contextContractString(cfg.enabled_field ?? cfg.enabledField, 'enabled'),
    sort_order_field: contextContractString(cfg.sort_order_field ?? cfg.sortOrderField, 'sort_order'),
    note_field: contextContractString(cfg.note_field ?? cfg.noteField, 'note'),
    notes: contextContractString(cfg.notes ?? cfg.note)
  };
}

function normalizeTargetContextConfig(raw, legacyRowContext=null) {
  const cfg = (raw && typeof raw === 'object' && !Array.isArray(raw)) ? raw : {};
  return {
    enabled: contextContractBool(cfg.enabled, true),
    display_name: contextContractString(cfg.display_name ?? cfg.displayName, '対象文脈'),
    parent_data_path: contextContractString(cfg.parent_data_path ?? cfg.parentDataPath),
    field: contextContractString(cfg.field ?? cfg.name, 'context_refs'),
    data_path: contextContractString(cfg.data_path ?? cfg.dataPath ?? legacyRowContext?.data_path, '$.context_refs'),
    description: contextContractString(cfg.description ?? cfg.summary),
    id_field: contextContractString(cfg.id_field ?? cfg.idField ?? legacyRowContext?.id_field, 'context_ref_id'),
    title_field: contextContractString(cfg.title_field ?? cfg.titleField ?? legacyRowContext?.title_field, 'title'),
    target_path_field: contextContractString(cfg.target_path_field ?? cfg.targetPathField ?? legacyRowContext?.target_path_field, 'target_path'),
    read_timing_field: contextContractString(cfg.read_timing_field ?? cfg.readTimingField ?? legacyRowContext?.read_timing_field, 'read_timing'),
    failure_policy_field: contextContractString(cfg.failure_policy_field ?? cfg.failurePolicyField ?? legacyRowContext?.failure_policy_field, 'failure_policy'),
    trust_category_field: contextContractString(cfg.trust_category_field ?? cfg.trustCategoryField ?? legacyRowContext?.trust_field, 'trust_category'),
    purpose_field: contextContractString(cfg.purpose_field ?? cfg.purposeField ?? legacyRowContext?.purpose_field, 'purpose'),
    required_field: contextContractString(cfg.required_field ?? cfg.requiredField, 'required'),
    enabled_field: contextContractString(cfg.enabled_field ?? cfg.enabledField, 'enabled'),
    sort_order_field: contextContractString(cfg.sort_order_field ?? cfg.sortOrderField, 'sort_order'),
    note_field: contextContractString(cfg.note_field ?? cfg.noteField, 'note'),
    grid_summary: contextContractBool(cfg.grid_summary ?? cfg.gridSummary, true),
    detail_panel: (cfg.detail_panel ?? cfg.detailPanel ?? null),
    notes: contextContractString(cfg.notes ?? cfg.note)
  };
}

function readContractFromObject(obj, sourceLabel) {
  const raw = obj?.context?.read_contract ?? obj?.context?.readContract ?? obj?.read_contract ?? obj?.readContract ?? null;
  return normalizeReadContract(raw, sourceLabel);
}

function extractViewDefReadContract(defObj) {
  const contracts = [];
  const rootContract = readContractFromObject(defObj, 'viewdef');
  if (rootContract) contracts.push(rootContract);
  (defObj?.views ?? []).forEach((view, index) => {
    const label = `view:${view?.id || index + 1}`;
    const c = readContractFromObject(view, label);
    if (c) contracts.push(c);
  });
  const requiredRefs = contracts.flatMap(c => c.required_refs ?? []);
  const optionalRefs = contracts.flatMap(c => c.optional_refs ?? []);
  return {
    enabled: contracts.some(c => c.enabled !== false),
    contracts,
    required_refs: requiredRefs,
    optional_refs: optionalRefs,
    row_contexts: contracts.map(c => c.row_context).filter(Boolean)
  };
}

function extractViewDefContextModel(defObj) {
  const rootContext = defObj?.context ?? {};
  const legacy = readContractFromObject(defObj, 'viewdef');
  const legacyRow = legacy?.row_context ?? null;
  return {
    main_context: normalizeMainContextConfig(rootContext.main_context ?? rootContext.mainContext, legacy),
    target_context: normalizeTargetContextConfig(rootContext.target_context ?? rootContext.targetContext, legacyRow),
    legacy_read_contract: legacy
  };
}

function logViewDefReadContract(contract) {
  if (!contract || !contract.contracts?.length) return;
  console.info(
    `[ViewDef read_contract] contracts=${contract.contracts.length}, required_refs=${contract.required_refs.length}, row_contexts=${contract.row_contexts.length}`,
    contract
  );
}

function logViewDefContextModel(model) {
  if (!model) return;
  console.info('[ViewDef context model]', model);
}

function mainContextConfig() {
  return currentViewDefContextModel?.main_context ?? normalizeMainContextConfig(viewDef?.context?.main_context ?? viewDef?.context?.mainContext);
}

function mainContextRefs() {
  const cfg = mainContextConfig();
  if (!cfg?.enabled || !sourceData) return [];
  const rows = getByPath(sourceData, cfg.data_path);
  return Array.isArray(rows) ? rows : [];
}

function readContextRefValue(ref, cfg, key) {
  const fieldName = cfg?.[`${key}_field`] ?? key;
  return ref?.[fieldName] ?? ref?.[key] ?? '';
}

function countMainContextRefs(refs, cfg) {
  const enabledRefs = refs.filter(ref => contextContractBool(readContextRefValue(ref, cfg, 'enabled'), true));
  const required = enabledRefs.filter(ref => contextContractBool(readContextRefValue(ref, cfg, 'required'), false));
  const stopLike = enabledRefs.filter(ref => String(readContextRefValue(ref, cfg, 'failure_policy')).startsWith('stop'));
  const timings = new Map();
  enabledRefs.forEach(ref => {
    const timing = contextContractString(readContextRefValue(ref, cfg, 'read_timing'), '(未設定)');
    timings.set(timing, (timings.get(timing) ?? 0) + 1);
  });
  return { enabledRefs, required, stopLike, timings };
}

function mainContextTimingLabel(value) {
  const map = {
    before_load: '読込前',
    after_load: '読込後',
    before_code_update: 'コード更新前',
    before_test_update: 'テスト更新前',
    before_zip_return: 'ZIP返却前'
  };
  return map[value] ?? value;
}

function createMainContextBadge(text) {
  const span = document.createElement('span');
  span.className = 'context-badge';
  span.textContent = text;
  return span;
}

function createMainContextInput(refs, index, field, value, type='text') {
  const input = type === 'textarea' ? document.createElement('textarea') : document.createElement('input');
  if (type === 'checkbox') {
    input.type = 'checkbox';
    input.checked = contextContractBool(value, false);
  } else if (type === 'number') {
    input.type = 'number';
    input.value = value == null ? '' : String(value);
  } else if (type !== 'textarea') {
    input.type = 'text';
    input.value = value == null ? '' : String(value);
  } else {
    input.value = value == null ? '' : String(value);
    input.rows = 2;
  }
  input.dataset.mainContextIndex = String(index);
  input.dataset.mainContextField = field;
  return input;
}


function createContextPreviewButton(label, title, onClick) {
  if (typeof createSubGridActionButton === 'function') return createSubGridActionButton(label, title, onClick);
  const btn = document.createElement('button');
  btn.type = 'button';
  btn.className = 'ghost-button small';
  btn.textContent = label;
  btn.title = title;
  btn.addEventListener('click', onClick);
  return btn;
}

function mainContextColumnMetas(cfg) {
  return [
    { label: 'タイトル', field: cfg.title_field, key: 'title', type: 'text' },
    { label: '読みタイミング', field: cfg.read_timing_field, key: 'read_timing', type: 'text' },
    { label: '対象パス', field: cfg.target_path_field, key: 'target_path', type: 'textarea' },
    { label: '読む目的', field: cfg.purpose_field, key: 'purpose', type: 'textarea' },
    { label: '失敗時方針', field: cfg.failure_policy_field, key: 'failure_policy', type: 'text' },
    { label: '信頼区分', field: cfg.trust_category_field, key: 'trust_category', type: 'text' },
    { label: '必須', field: cfg.required_field, key: 'required', type: 'checkbox' },
    { label: '有効', field: cfg.enabled_field, key: 'enabled', type: 'checkbox' },
    { label: 'メモ', field: cfg.note_field, key: 'note', type: 'textarea' }
  ];
}

function collectContextPreviewRowsFromPanel(panel, refs, indexAttr, fieldAttr) {
  const rows = normalizeArray(refs).map(ref => ({ ...(ref ?? {}) }));
  if (!panel) return rows;
  [...panel.querySelectorAll(`[${indexAttr}][${fieldAttr}]`)].forEach(control => {
    const index = Number(control.getAttribute(indexAttr));
    const field = control.getAttribute(fieldAttr);
    if (!Number.isInteger(index) || index < 0 || !field) return;
    if (!rows[index]) rows[index] = {};
    if (control.type === 'checkbox') rows[index][field] = control.checked;
    else if (control.type === 'number') rows[index][field] = control.value === '' ? null : Number(control.value);
    else rows[index][field] = control.value;
  });
  return rows;
}

function contextPreviewEditColumnsFromMetas(metas) {
  return (metas ?? []).map(meta => ({
    field: meta.field,
    caption: meta.label,
    type: meta.type === 'checkbox' ? 'boolean' : meta.type,
    // checkbox由来のbooleanは、空select化ではなくcheckboxとして扱う。
    // select/options由来の項目は従来通りコンボとして生かす。
    control: meta.type === 'checkbox' ? 'checkbox' : meta.control,
    options: meta.options,
    edit: meta.edit,
    grid: meta.grid
  })).filter(col => col.field);
}

function replaceContextRefsArray(refs, rows) {
  if (!Array.isArray(refs)) return;
  refs.splice(0, refs.length, ...((rows ?? []).map(row => (
    row && typeof row === 'object' && !Array.isArray(row) ? { ...row } : {}
  ))));
}

function emptyContextPreviewEditRow(columns) {
  if (typeof emptyObjectForColumns === 'function') return emptyObjectForColumns(columns);
  const obj = {};
  (columns ?? []).forEach(col => { if (col?.field) obj[col.field] = ''; });
  return obj;
}

function contextPreviewEditRowTitle(row, index, columns=[]) {
  if (typeof detailSubGridEditorRowTitle === 'function') return detailSubGridEditorRowTitle(row, index, columns);
  return `${index + 1}件目`;
}

function showContextRefsPreviewEdit({ title='文脈', rows=[], columns=[], onApply=null, onClose=null }={}) {
  if (typeof createDetailSubGridPreviewEditValue !== 'function') {
    if (typeof showDetailSubGridPreview === 'function') {
      showDetailSubGridPreview({
        title: `${title} プレビュー`,
        rows,
        columns,
        type: 'objectArray',
        field: { type: 'objectArray', markdown: { enabled: true, allowLinks: true, allowImages: false } },
        note: 'プレビュー編集機能を利用できないため、読み取りプレビューで表示しています'
      });
    }
    return;
  }

  const editorField = { type: 'objectArray', markdown: { enabled: true, allowLinks: true, allowImages: false } };
  const editRows = (typeof normalizeRowsForDetailSubGridEditor === 'function')
    ? normalizeRowsForDetailSubGridEditor(rows, 'objectArray')
    : (Array.isArray(rows) ? rows.map(row => ({ ...(row ?? {}) })) : []);

  document.querySelectorAll('.context-preview-edit-overlay').forEach(el => {
    try { if (typeof el.close === 'function' && el.open) el.close(); } catch { /* ignore */ }
    el.remove();
  });

  const overlay = document.createElement('dialog');
  overlay.className = 'detail-subgrid-preview-overlay detail-subgrid-card-editor-overlay context-preview-edit-overlay';
  const closeEditor = () => {
    try { if (typeof overlay.close === 'function' && overlay.open) overlay.close(); } catch { /* ignore */ }
    overlay.remove();
    if (typeof onClose === 'function') onClose();
  };
  overlay.addEventListener('click', (e) => { if (e.target === overlay) closeEditor(); });
  overlay.addEventListener('cancel', (e) => { e.preventDefault(); closeEditor(); });

  const dialog = document.createElement('div');
  dialog.className = 'detail-subgrid-preview-dialog detail-subgrid-card-editor-dialog context-preview-edit-dialog';
  dialog.setAttribute('role', 'document');

  const header = document.createElement('div');
  header.className = 'detail-subgrid-preview-header detail-subgrid-card-editor-header';
  const headingWrap = document.createElement('div');
  const kicker = document.createElement('div');
  kicker.className = 'detail-subgrid-preview-kicker';
  kicker.textContent = 'Context Preview Edit';
  const h2 = document.createElement('h2');
  h2.textContent = `${title} プレビュー編集`;
  headingWrap.appendChild(kicker);
  headingWrap.appendChild(h2);
  header.appendChild(headingWrap);

  const headerActions = document.createElement('div');
  headerActions.className = 'detail-subgrid-card-editor-header-actions';
  const applyBtn = createContextPreviewButton('一覧へ反映', 'プレビュー編集内容を文脈一覧へ反映して閉じる', () => {
    if (typeof onApply === 'function') onApply(editRows);
    closeEditor();
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
  body.className = 'detail-subgrid-preview-body detail-subgrid-card-editor-body context-preview-edit-body';
  dialog.appendChild(body);

  const setRowValue = (rowIndex, column, input) => {
    if (!editRows[rowIndex]) editRows[rowIndex] = {};
    if (typeof readSubGridControlValue === 'function') {
      editRows[rowIndex][column.field] = readSubGridControlValue(input);
    } else if (input?.type === 'checkbox') {
      editRows[rowIndex][column.field] = Boolean(input.checked);
    } else if (column?.type === 'boolean') {
      editRows[rowIndex][column.field] = input?.value === 'true';
    } else {
      editRows[rowIndex][column.field] = input?.value;
    }
  };

  const rerender = () => {
    summary.textContent = `${editRows.length}件 / ${columns.length}列 — 長文はクリックで原文編集、blurでMarkdownプレビューへ戻ります。最後に「一覧へ反映」してください`;
    body.innerHTML = '';

    const toolbar = document.createElement('div');
    toolbar.className = 'detail-subgrid-card-editor-toolbar';
    toolbar.appendChild(createContextPreviewButton('＋末尾に追加', '末尾に空カードを追加', () => {
      editRows.push(emptyContextPreviewEditRow(columns));
      rerender();
    }));
    body.appendChild(toolbar);

    if (!editRows.length) {
      const empty = document.createElement('div');
      empty.className = 'detail-subgrid-preview-empty-card';
      empty.textContent = '文脈行がありません。＋末尾に追加で行を作成できます。';
      body.appendChild(empty);
      return;
    }

    editRows.forEach((row, index) => {
      const itemRow = row && typeof row === 'object' ? row : {};
      const section = document.createElement('section');
      section.className = 'detail-subgrid-preview-card detail-subgrid-card-editor-card context-preview-edit-card';

      const titleLine = document.createElement('div');
      titleLine.className = 'detail-subgrid-preview-card-title detail-subgrid-card-editor-card-title';
      const titleText = document.createElement('span');
      titleText.textContent = contextPreviewEditRowTitle(itemRow, index, columns);
      titleLine.appendChild(titleText);

      const actions = document.createElement('div');
      actions.className = 'detail-subgrid-card-editor-row-actions';
      actions.appendChild(createContextPreviewButton('＋上', 'このカードの上に追加', () => { editRows.splice(index, 0, emptyContextPreviewEditRow(columns)); rerender(); }));
      actions.appendChild(createContextPreviewButton('＋下', 'このカードの下に追加', () => { editRows.splice(index + 1, 0, emptyContextPreviewEditRow(columns)); rerender(); }));
      actions.appendChild(createContextPreviewButton('複製', 'このカードを複製して下に追加', () => { editRows.splice(index + 1, 0, JSON.parse(JSON.stringify(itemRow))); rerender(); }));
      actions.appendChild(createContextPreviewButton('↑', 'このカードを上へ移動', () => {
        if (index <= 0) return;
        const [moved] = editRows.splice(index, 1);
        editRows.splice(index - 1, 0, moved);
        rerender();
      }));
      actions.appendChild(createContextPreviewButton('↓', 'このカードを下へ移動', () => {
        if (index >= editRows.length - 1) return;
        const [moved] = editRows.splice(index, 1);
        editRows.splice(index + 1, 0, moved);
        rerender();
      }));
      actions.appendChild(createContextPreviewButton('削除', 'このカードを削除', () => { editRows.splice(index, 1); rerender(); }));
      titleLine.appendChild(actions);
      section.appendChild(titleLine);

      columns.forEach(col => {
        const fieldLine = document.createElement('div');
        fieldLine.className = 'detail-subgrid-preview-field detail-subgrid-card-editor-field';
        const label = document.createElement('div');
        label.className = 'detail-subgrid-preview-label';
        label.textContent = col.caption ?? col.field;
        const value = document.createElement('div');
        value.className = 'detail-subgrid-card-editor-value';
        const editorColumn = { ...col, field: col.field, type: col.type ?? 'text' };
        value.appendChild(createDetailSubGridPreviewEditValue({
          rowIndex: index,
          column: editorColumn,
          itemRow,
          field: editorField,
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

function openContextRefsPreviewEdit({ title, refs, metas, panel, indexAttr, fieldAttr, onApply }) {
  const rows = collectContextPreviewRowsFromPanel(panel, refs, indexAttr, fieldAttr);
  const columns = contextPreviewEditColumnsFromMetas(metas);
  showContextRefsPreviewEdit({
    title,
    rows,
    columns,
    onApply: (nextRows) => {
      if (typeof onApply === 'function') onApply(nextRows);
    }
  });
}

function openMainContextPreview(panel, cfg) {
  const refs = mainContextRefs();
  openContextRefsPreviewEdit({
    title: `${cfg?.display_name || '主文脈'}`,
    refs,
    metas: mainContextColumnMetas(cfg),
    panel,
    indexAttr: 'data-main-context-index',
    fieldAttr: 'data-main-context-field',
    onApply: (nextRows) => {
      replaceContextRefsArray(refs, nextRows);
      renderMainContextHeaderPanel($('headerSection'));
      if (typeof setStatus === 'function') setStatus('主文脈のプレビュー編集内容を一覧へ反映しました。F12または反映ボタンで親JSONへ同期してください。');
    }
  });
}

function openTargetContextPreview(panel, row, cfg) {
  const refs = targetContextRefsFromRow(row, cfg, true);
  openContextRefsPreviewEdit({
    title: `${cfg?.display_name || '対象文脈'}`,
    refs,
    metas: targetContextColumnMetas(cfg),
    panel,
    indexAttr: 'data-target-context-index',
    fieldAttr: 'data-target-context-field',
    onApply: (nextRows) => {
      replaceContextRefsArray(refs, nextRows);
      targetContextDetailPanelExpanded = true;
      renderDetailForRow(row);
      if (typeof renderGrid === 'function') renderGrid();
      if (typeof setStatus === 'function') setStatus('対象文脈のプレビュー編集内容を一覧へ反映しました。F12または反映ボタンで親JSONへ同期してください。');
    }
  });
}

function renderMainContextHeaderPanel(host) {
  const section = host ?? $('headerSection');
  if (!section) return;
  section.querySelector('#mainContextHeaderPanel')?.remove();

  const cfg = mainContextConfig();
  if (!cfg?.enabled) return;
  const refs = mainContextRefs();
  if (!Array.isArray(refs) || refs.length === 0) return;

  const counts = countMainContextRefs(refs, cfg);
  const panel = document.createElement('div');
  panel.id = 'mainContextHeaderPanel';
  panel.className = 'main-context-panel';

  const summary = document.createElement('div');
  summary.className = 'main-context-summary';

  const title = document.createElement('div');
  title.className = 'main-context-title';
  title.textContent = cfg.display_name || '主文脈';
  summary.appendChild(title);

  const badges = document.createElement('div');
  badges.className = 'main-context-badges';
  badges.appendChild(createMainContextBadge(`${counts.enabledRefs.length}件`));
  badges.appendChild(createMainContextBadge(`必須${counts.required.length}`));
  badges.appendChild(createMainContextBadge(`停止${counts.stopLike.length}`));
  [...counts.timings.entries()].forEach(([timing, count]) => badges.appendChild(createMainContextBadge(`${mainContextTimingLabel(timing)} ${count}`)));
  summary.appendChild(badges);

  const actions = document.createElement('div');
  actions.className = 'main-context-actions';
  const toggle = document.createElement('button');
  toggle.type = 'button';
  toggle.className = 'ghost-button small';
  toggle.textContent = mainContextPanelExpanded ? '主文脈を隠す' : '主文脈を確認';
  toggle.addEventListener('click', () => {
    mainContextPanelExpanded = !mainContextPanelExpanded;
    renderMainContextHeaderPanel(section);
  });
  actions.appendChild(toggle);
  if (mainContextPanelExpanded && typeof showDetailSubGridPreview === 'function') {
    actions.appendChild(createContextPreviewButton('プレビュー編集', '主文脈を読み物兼編集画面で開く', () => openMainContextPreview(panel, cfg)));
  }
  summary.appendChild(actions);
  panel.appendChild(summary);

  const detail = document.createElement('div');
  detail.className = 'main-context-detail' + (mainContextPanelExpanded ? '' : ' hidden');
  const tableWrap = document.createElement('div');
  tableWrap.className = 'main-context-table-wrap';
  const table = document.createElement('table');
  table.className = 'main-context-table';
  const mainMetas = mainContextColumnMetas(cfg);
  const thead = document.createElement('thead');
  const trh = document.createElement('tr');
  const thNo = document.createElement('th');
  thNo.textContent = '#';
  trh.appendChild(thNo);
  mainMetas.forEach(meta => {
    const th = document.createElement('th');
    th.textContent = meta.label;
    trh.appendChild(th);
  });
  thead.appendChild(trh);
  table.appendChild(thead);
  const tbody = document.createElement('tbody');
  refs.forEach((ref, index) => {
    const tr = document.createElement('tr');
    const order = readContextRefValue(ref, cfg, 'sort_order') || index + 1;
    const fields = mainMetas;
    const no = document.createElement('td');
    no.textContent = String(order);
    tr.appendChild(no);
    fields.forEach(meta => {
      const td = document.createElement('td');
      td.appendChild(createMainContextInput(refs, index, meta.field, ref?.[meta.field] ?? ref?.[meta.key], meta.type));
      tr.appendChild(td);
    });
    tbody.appendChild(tr);
  });
  table.appendChild(tbody);
  tableWrap.appendChild(table);
  detail.appendChild(tableWrap);

  const footer = document.createElement('div');
  footer.className = 'main-context-footer';
  const applyBtn = document.createElement('button');
  applyBtn.type = 'button';
  applyBtn.className = 'primary-button small';
  applyBtn.textContent = '主文脈を反映';
  applyBtn.addEventListener('click', () => {
    applyMainContextHeaderPanelEdits();
    renderMainContextHeaderPanel(section);
    setStatus('主文脈を反映しました');
  });
  footer.appendChild(applyBtn);
  const hint = document.createElement('span');
  hint.className = 'main-context-hint';
  hint.textContent = 'Data rootの主文脈を編集します。ViewDefには文脈実データを保存しません。';
  footer.appendChild(hint);
  detail.appendChild(footer);
  panel.appendChild(detail);

  section.appendChild(panel);
}

function applyMainContextHeaderPanelEdits(options={}) {
  const cfg = mainContextConfig();
  if (!cfg?.enabled || !sourceData) return;
  const refs = mainContextRefs();
  if (!Array.isArray(refs)) return;
  const panel = $('mainContextHeaderPanel');
  if (!panel) return;
  const controls = [...panel.querySelectorAll('[data-main-context-index][data-main-context-field]')];
  controls.forEach(control => {
    const index = Number(control.dataset.mainContextIndex);
    const field = control.dataset.mainContextField;
    if (!Number.isInteger(index) || index < 0 || !refs[index] || !field) return;
    let value;
    if (control.type === 'checkbox') value = control.checked;
    else if (control.type === 'number') value = control.value === '' ? null : Number(control.value);
    else value = control.value;
    refs[index][field] = value;
  });
  if (!options.silent && typeof setStatus === 'function') setStatus('主文脈を反映しました');
}

function targetContextConfig() {
  return currentViewDefContextModel?.target_context ?? normalizeTargetContextConfig(viewDef?.context?.target_context ?? viewDef?.context?.targetContext);
}

function targetContextFieldName(cfg=targetContextConfig()) {
  const explicit = contextContractString(cfg?.field, '');
  if (explicit) return explicit;
  const path = contextContractString(cfg?.data_path, '$.context_refs');
  const normalized = path.startsWith('$.') ? path.slice(2) : path;
  return normalized.split('.').filter(Boolean).pop() || 'context_refs';
}

function isTargetContextField(field) {
  const cfg = targetContextConfig();
  if (!cfg?.enabled || !field) return false;
  const configured = targetContextFieldName(cfg);
  return field.field === configured || field.field === cfg.data_path || field.contextRole === 'targetContext' || field.context_role === 'targetContext';
}

function targetContextRefsFromRow(row, cfg=targetContextConfig(), create=false) {
  if (!cfg?.enabled || !row) return [];
  const path = contextContractString(cfg.data_path, '$.context_refs');
  let refs = getByPath(row, path);
  if (!Array.isArray(refs)) {
    if (!create) return [];
    refs = [];
    setByPath(row, path, refs);
  }
  return refs;
}

function countContextRefs(refs, cfg) {
  const rows = Array.isArray(refs) ? refs : [];
  const enabledRefs = rows.filter(ref => contextContractBool(readContextRefValue(ref, cfg, 'enabled'), true));
  const required = enabledRefs.filter(ref => contextContractBool(readContextRefValue(ref, cfg, 'required'), false));
  const stopLike = enabledRefs.filter(ref => String(readContextRefValue(ref, cfg, 'failure_policy')).startsWith('stop'));
  return { rows, enabledRefs, required, stopLike };
}

function formatTargetContextValue(value, field=null) {
  if (!isTargetContextField(field) || !Array.isArray(value)) return null;
  const cfg = targetContextConfig();
  const counts = countContextRefs(value, cfg);
  if (!counts.rows.length) return '対象文脈 0件';
  const bits = [`${counts.enabledRefs.length}件`];
  if (counts.required.length) bits.push(`必須${counts.required.length}`);
  if (counts.stopLike.length) bits.push(`停止${counts.stopLike.length}`);
  return bits.join(' / ');
}

function createTargetContextBadge(text) {
  const span = document.createElement('span');
  span.className = 'context-badge target-context-badge';
  span.textContent = text;
  return span;
}

function createTargetContextInput(index, field, value, type='text') {
  const input = type === 'textarea' ? document.createElement('textarea') : document.createElement('input');
  if (type === 'checkbox') {
    input.type = 'checkbox';
    input.checked = contextContractBool(value, false);
  } else if (type === 'number') {
    input.type = 'number';
    input.value = value == null ? '' : String(value);
  } else if (type === 'textarea') {
    input.value = value == null ? '' : String(value);
    input.rows = 2;
  } else {
    input.type = 'text';
    input.value = value == null ? '' : String(value);
  }
  input.dataset.targetContextIndex = String(index);
  input.dataset.targetContextField = field;
  return input;
}

function targetContextColumnMetas(cfg) {
  return [
    { label: 'Context Ref ID', field: cfg.id_field, key: 'context_ref_id', type: 'text', className: 'target-context-id' },
    { label: 'タイトル', field: cfg.title_field, key: 'title', type: 'text', className: 'target-context-title' },
    { label: '読みタイミング', field: cfg.read_timing_field, key: 'read_timing', type: 'text', className: 'target-context-timing' },
    { label: '対象パス', field: cfg.target_path_field, key: 'target_path', type: 'textarea', className: 'target-context-path' },
    { label: '読む目的', field: cfg.purpose_field, key: 'purpose', type: 'textarea', className: 'target-context-purpose' },
    { label: '失敗時方針', field: cfg.failure_policy_field, key: 'failure_policy', type: 'text', className: 'target-context-failure' },
    { label: '信頼区分', field: cfg.trust_category_field, key: 'trust_category', type: 'text', className: 'target-context-trust' },
    { label: '必須', field: cfg.required_field ?? 'required', key: 'required', type: 'checkbox', className: 'target-context-check' },
    { label: '有効', field: cfg.enabled_field ?? 'enabled', key: 'enabled', type: 'checkbox', className: 'target-context-check' }
  ];
}

function newTargetContextRef(row, refs, cfg) {
  const baseId = String(getByPath(row, 'target_id') ?? getByPath(row, 'work_item_id') ?? getByPath(row, 'id') ?? 'target').trim() || 'target';
  const n = (refs?.length ?? 0) + 1;
  return {
    [cfg.id_field]: `${baseId}_context_${String(n).padStart(3, '0')}`,
    [cfg.title_field]: '対象文脈を追加',
    [cfg.read_timing_field]: 'before_code_update',
    [cfg.target_path_field]: '',
    [cfg.purpose_field]: '',
    [cfg.failure_policy_field]: 'stop_and_ask',
    [cfg.trust_category_field]: 'canonical',
    [cfg.required_field]: true,
    [cfg.enabled_field]: true,
    [cfg.sort_order_field]: n * 10,
    [cfg.note_field]: ''
  };
}

function addTargetContextRef(row) {
  const cfg = targetContextConfig();
  const refs = targetContextRefsFromRow(row, cfg, true);
  refs.push(newTargetContextRef(row, refs, cfg));
  targetContextDetailPanelExpanded = true;
  renderDetailForRow(row);
  if (typeof renderGrid === 'function') renderGrid();
  if (typeof setStatus === 'function') setStatus('対象文脈を1件追加しました');
}

function removeTargetContextRef(row, index) {
  const cfg = targetContextConfig();
  const refs = targetContextRefsFromRow(row, cfg, true);
  if (index < 0 || index >= refs.length) return;
  refs.splice(index, 1);
  targetContextDetailPanelExpanded = true;
  renderDetailForRow(row);
  if (typeof renderGrid === 'function') renderGrid();
  if (typeof setStatus === 'function') setStatus('対象文脈を1件削除しました');
}

function renderTargetContextDetailPanel(row, gd, host) {
  const cfg = targetContextConfig();
  if (!cfg?.enabled || !row || !host) return;
  const targetField = (gd?.fields ?? []).find(f => isTargetContextField(f));
  if (!targetField) return;

  const refs = targetContextRefsFromRow(row, cfg, false);
  const counts = countContextRefs(refs, cfg);
  const panel = document.createElement('div');
  panel.id = 'targetContextDetailPanel';
  panel.className = 'target-context-panel';

  const summary = document.createElement('div');
  summary.className = 'target-context-summary';
  const title = document.createElement('div');
  title.className = 'target-context-title';
  title.textContent = cfg.display_name || targetField.caption || '対象文脈';
  summary.appendChild(title);

  const badges = document.createElement('div');
  badges.className = 'target-context-badges';
  badges.appendChild(createTargetContextBadge(`${counts.enabledRefs.length}件`));
  badges.appendChild(createTargetContextBadge(`必須${counts.required.length}`));
  badges.appendChild(createTargetContextBadge(`停止${counts.stopLike.length}`));
  summary.appendChild(badges);

  const actions = document.createElement('div');
  actions.className = 'target-context-actions';
  const toggle = document.createElement('button');
  toggle.type = 'button';
  toggle.className = 'ghost-button small';
  toggle.textContent = targetContextDetailPanelExpanded ? '対象文脈を隠す' : '対象文脈を確認';
  toggle.addEventListener('click', () => {
    targetContextDetailPanelExpanded = !targetContextDetailPanelExpanded;
    renderDetailForRow(row);
  });
  actions.appendChild(toggle);
  if (targetContextDetailPanelExpanded) {
    if (typeof showDetailSubGridPreview === 'function') {
      actions.appendChild(createContextPreviewButton('プレビュー編集', '対象文脈を読み物兼編集画面で開く', () => openTargetContextPreview(panel, row, cfg)));
    }
    const addBtn = document.createElement('button');
    addBtn.type = 'button';
    addBtn.className = 'ghost-button small';
    addBtn.textContent = '対象文脈を追加';
    addBtn.addEventListener('click', () => addTargetContextRef(row));
    actions.appendChild(addBtn);
  }
  summary.appendChild(actions);
  panel.appendChild(summary);

  const detail = document.createElement('div');
  detail.className = 'target-context-detail' + (targetContextDetailPanelExpanded ? '' : ' hidden');
  const wrap = document.createElement('div');
  wrap.className = 'target-context-table-wrap';
  const table = document.createElement('table');
  table.className = 'target-context-table';
  const metas = targetContextColumnMetas(cfg);
  const thead = document.createElement('thead');
  const trh = document.createElement('tr');
  metas.forEach(meta => {
    const th = document.createElement('th');
    th.textContent = meta.label;
    if (meta.className) th.classList.add(meta.className);
    trh.appendChild(th);
  });
  const thAction = document.createElement('th');
  thAction.textContent = '操作';
  trh.appendChild(thAction);
  thead.appendChild(trh);
  table.appendChild(thead);

  const tbody = document.createElement('tbody');
  refs.forEach((ref, index) => {
    const tr = document.createElement('tr');
    metas.forEach(meta => {
      const td = document.createElement('td');
      if (meta.className) td.classList.add(meta.className);
      const value = ref?.[meta.field] ?? ref?.[meta.key];
      td.appendChild(createTargetContextInput(index, meta.field, value, meta.type));
      tr.appendChild(td);
    });
    const tdAction = document.createElement('td');
    const del = document.createElement('button');
    del.type = 'button';
    del.className = 'danger-button mini';
    del.textContent = '削除';
    del.addEventListener('click', () => removeTargetContextRef(row, index));
    tdAction.appendChild(del);
    tr.appendChild(tdAction);
    tbody.appendChild(tr);
  });
  if (!refs.length) {
    const tr = document.createElement('tr');
    const td = document.createElement('td');
    td.colSpan = metas.length + 1;
    td.className = 'target-context-empty';
    td.textContent = '対象文脈は未登録です。必要なら「対象文脈を追加」してください。';
    tr.appendChild(td);
    tbody.appendChild(tr);
  }
  table.appendChild(tbody);
  wrap.appendChild(table);
  detail.appendChild(wrap);

  const footer = document.createElement('div');
  footer.className = 'target-context-footer';
  const applyBtn = document.createElement('button');
  applyBtn.type = 'button';
  applyBtn.className = 'primary-button small';
  applyBtn.textContent = '対象文脈を反映';
  applyBtn.addEventListener('click', () => {
    applyTargetContextDetailPanelEdits(row);
    if (typeof renderGrid === 'function') renderGrid();
    setStatus('対象文脈を反映しました');
  });
  footer.appendChild(applyBtn);
  const hint = document.createElement('span');
  hint.className = 'target-context-hint';
  hint.textContent = 'この対象を扱う前に読む文脈です。Data明細の context_refs[] を編集します。';
  footer.appendChild(hint);
  detail.appendChild(footer);
  panel.appendChild(detail);
  host.appendChild(panel);
}

function applyTargetContextDetailPanelEdits(row) {
  const cfg = targetContextConfig();
  if (!cfg?.enabled || !row) return;
  const panel = $('targetContextDetailPanel');
  if (!panel) return;
  const refs = targetContextRefsFromRow(row, cfg, true);
  const controls = [...panel.querySelectorAll('[data-target-context-index][data-target-context-field]')];
  controls.forEach(control => {
    const index = Number(control.dataset.targetContextIndex);
    const field = control.dataset.targetContextField;
    if (!Number.isInteger(index) || index < 0 || !refs[index] || !field) return;
    let value;
    if (control.type === 'checkbox') value = control.checked;
    else if (control.type === 'number') value = control.value === '' ? null : Number(control.value);
    else value = control.value;
    refs[index][field] = value;
  });
}

