// v0.15.5-v0.15.5.2: ViewDef context model recognizer + main context header panel
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
  summary.appendChild(actions);
  panel.appendChild(summary);

  const detail = document.createElement('div');
  detail.className = 'main-context-detail' + (mainContextPanelExpanded ? '' : ' hidden');
  const tableWrap = document.createElement('div');
  tableWrap.className = 'main-context-table-wrap';
  const table = document.createElement('table');
  table.className = 'main-context-table';
  table.innerHTML = '<thead><tr><th>#</th><th>タイトル</th><th>読みタイミング</th><th>対象パス</th><th>読む目的</th><th>失敗時方針</th><th>信頼区分</th><th>必須</th><th>有効</th></tr></thead>';
  const tbody = document.createElement('tbody');
  refs.forEach((ref, index) => {
    const tr = document.createElement('tr');
    const order = readContextRefValue(ref, cfg, 'sort_order') || index + 1;
    const fields = [
      { field: cfg.title_field, key: 'title', type: 'text' },
      { field: cfg.read_timing_field, key: 'read_timing', type: 'text' },
      { field: cfg.target_path_field, key: 'target_path', type: 'textarea' },
      { field: cfg.purpose_field, key: 'purpose', type: 'textarea' },
      { field: cfg.failure_policy_field, key: 'failure_policy', type: 'text' },
      { field: cfg.trust_category_field, key: 'trust_category', type: 'text' },
      { field: cfg.required_field, key: 'required', type: 'checkbox' },
      { field: cfg.enabled_field, key: 'enabled', type: 'checkbox' }
    ];
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
