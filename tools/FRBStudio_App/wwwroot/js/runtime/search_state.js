// v0.18.21-json-full-text-search
// 検索条件の保存・呼出・画面復元を担当する最小ブリッジ。
// Core検索欄とPlugin SearchFilter stateを同じ ui_state として扱う。
// v0.17.16: 標準UIは方針整理まで非表示。Core API / Plugin state bridge のみ残す。

const STUDIO_SEARCH_PATTERN_STORAGE_KEY = 'frbStudio.searchPatterns.v0_17_14';
const STUDIO_SEARCH_PATTERN_STANDARD_UI_ENABLED = false;
let studioOverlaySearchPatternCache = null;
let studioSearchPatternPanelOpen = false;

function studioSearchStateClone(value) {
  if (value == null) return value;
  try {
    return typeof structuredClone === 'function' ? structuredClone(value) : JSON.parse(JSON.stringify(value));
  } catch {
    return Array.isArray(value) ? [...value] : { ...value };
  }
}

function normalizeStudioSearchUiState(value) {
  const raw = value?.ui_state ?? value?.uiState ?? value?.search_state ?? value?.searchState ?? value ?? {};
  return {
    schema_version: raw.schema_version ?? raw.schemaVersion ?? 'studio_search_ui_state_v0_1',
    core: raw.core && typeof raw.core === 'object' ? studioSearchStateClone(raw.core) : {},
    plugins: raw.plugins && typeof raw.plugins === 'object' ? studioSearchStateClone(raw.plugins) : {}
  };
}

function hasStudioSearchUiState(pattern) {
  return Boolean(pattern?.ui_state || pattern?.uiState || pattern?.search_state || pattern?.searchState);
}

function studioCoreSearchControls() {
  const controls = [];
  const fullText = $('studioFullTextSearchInput');
  if (fullText) controls.push(fullText);

  const form = $('searchForm');
  if (form) {
    controls.push(...[...form.querySelectorAll('input, select, textarea')]
      .filter(control => !control.closest('.studio-plugin-search-filter')));
  }
  return controls;
}

function getStudioControlValue(control) {
  if (!control) return '';
  if (control instanceof HTMLSelectElement && control.multiple) {
    return [...control.selectedOptions].map(opt => opt.value).filter(Boolean);
  }
  if (control instanceof HTMLInputElement && control.type === 'checkbox') {
    return control.checked ? control.value : '';
  }
  if (control instanceof HTMLInputElement && control.type === 'radio') {
    return control.checked ? control.value : '';
  }
  return control.value ?? '';
}

function setStudioControlValue(control, value) {
  if (!control) return;
  if (control instanceof HTMLSelectElement && control.multiple) {
    const selected = new Set((Array.isArray(value) ? value : String(value ?? '').split(','))
      .map(x => String(x ?? '').trim())
      .filter(Boolean));
    [...control.options].forEach(option => { option.selected = selected.has(String(option.value)); });
    return;
  }
  if (control instanceof HTMLSelectElement) {
    const next = value == null ? '' : String(value);
    if (next && ![...control.options].some(option => String(option.value) === next)) {
      const option = document.createElement('option');
      option.value = next;
      option.textContent = next;
      control.appendChild(option);
    }
    control.value = next;
    return;
  }
  if (control instanceof HTMLInputElement && control.type === 'checkbox') {
    const values = new Set((Array.isArray(value) ? value : [value]).map(x => String(x ?? '')));
    control.checked = values.has(String(control.value));
    return;
  }
  if (control instanceof HTMLInputElement && control.type === 'radio') {
    control.checked = String(control.value) === String(value ?? '');
    return;
  }
  control.value = value == null ? '' : String(value);
}

function getStudioSearchState() {
  const core = {};
  for (const control of studioCoreSearchControls()) {
    const field = control.dataset.field;
    if (!field) continue;
    const value = getStudioControlValue(control);
    if (Array.isArray(value) ? value.length > 0 : value !== '') core[field] = value;
  }

  const plugins = typeof getStudioPluginSearchFilterStates === 'function'
    ? getStudioPluginSearchFilterStates()
    : {};

  return {
    schema_version: 'studio_search_ui_state_v0_1',
    core,
    plugins
  };
}

function applyStudioCoreSearchState(coreState = {}) {
  const controlsByField = new Map();
  for (const control of studioCoreSearchControls()) {
    const field = control.dataset.field;
    if (!field) continue;
    if (!controlsByField.has(field)) controlsByField.set(field, []);
    controlsByField.get(field).push(control);
  }

  for (const controls of controlsByField.values()) controls.forEach(control => setStudioControlValue(control, ''));
  Object.entries(coreState && typeof coreState === 'object' ? coreState : {}).forEach(([field, value]) => {
    (controlsByField.get(field) ?? []).forEach(control => setStudioControlValue(control, value));
  });
}

function applyStudioSearchState(stateOrPattern, options = {}) {
  const uiState = normalizeStudioSearchUiState(stateOrPattern);
  applyStudioCoreSearchState(uiState.core);
  if (typeof resetStudioPluginSearchFilters === 'function') resetStudioPluginSearchFilters();
  if (typeof applyStudioPluginSearchFilterStates === 'function') {
    applyStudioPluginSearchFilterStates(uiState.plugins, { syncControls: true });
  }
  if (options.runSearch === true && typeof applySearch === 'function') applySearch();
  return uiState;
}


// v0.18.125-viewdef-search-initial-state:
// ViewDef field.search.initialValue / applyOnLoad を、既存のStudio Search State復元経路へ接続する。
// Field defaultValue（新規Data初期値）とは責務を分離し、検索Projectionの初期状態だけを扱う。
function viewDefInitialSearchDescriptor(gd = (typeof gridDef === 'function' ? gridDef() : null)) {
  const core = {};
  const configuredFields = [];
  let applyOnLoad = false;
  for (const field of (gd?.fields ?? [])) {
    const search = field?.search;
    if (!search || search.visible !== true) continue;
    const hasInitialValue = Object.prototype.hasOwnProperty.call(search, 'initialValue')
      || Object.prototype.hasOwnProperty.call(search, 'initial_value');
    if (hasInitialValue) {
      const initialValue = Object.prototype.hasOwnProperty.call(search, 'initialValue')
        ? search.initialValue
        : search.initial_value;
      core[String(field?.field ?? '')] = studioSearchStateClone(initialValue);
      configuredFields.push(String(field?.field ?? ''));
    }
    if (search.applyOnLoad === true || search.apply_on_load === true) {
      applyOnLoad = true;
      if (!configuredFields.includes(String(field?.field ?? ''))) configuredFields.push(String(field?.field ?? ''));
    }
  }
  return {
    schema_version: 'viewdef_initial_search_v0_1',
    configured: configuredFields.length > 0,
    apply_on_load: applyOnLoad,
    configured_fields: configuredFields,
    ui_state: {
      schema_version: 'studio_search_ui_state_v0_1',
      core,
      plugins: {}
    }
  };
}

function applyViewDefInitialSearch(gd = (typeof gridDef === 'function' ? gridDef() : null), options = {}) {
  const descriptor = viewDefInitialSearchDescriptor(gd);
  if (!descriptor.configured) return descriptor;
  applyStudioSearchState(descriptor.ui_state, { runSearch: false });
  if (descriptor.apply_on_load && options.runSearch !== false && typeof applySearch === 'function') {
    applySearch();
    return { ...descriptor, search_applied: true };
  }
  return { ...descriptor, search_applied: false };
}

function loadLocalStudioSearchPatterns() {
  try {
    const raw = localStorage.getItem(STUDIO_SEARCH_PATTERN_STORAGE_KEY);
    const parsed = raw ? JSON.parse(raw) : [];
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

function saveLocalStudioSearchPatterns(patterns) {
  localStorage.setItem(STUDIO_SEARCH_PATTERN_STORAGE_KEY, JSON.stringify(patterns ?? []));
}

function currentStudioSearchPatternTarget() {
  const dataPath = (typeof currentLoadedDataDisplayPath !== 'undefined' && currentLoadedDataDisplayPath)
    ? currentLoadedDataDisplayPath
    : ((typeof currentDataApiUrl !== 'undefined' && currentDataApiUrl) ? currentDataApiUrl : '');
  const viewDefPath = (typeof lastLoadedDefName !== 'undefined' && lastLoadedDefName) ? lastLoadedDefName : '';
  return {
    target_data: dataPath,
    target_view_def: viewDefPath
  };
}

function normalizeStudioTargetPath(value) {
  return String(value ?? '')
    .trim()
    .replace(/\\/g, '/')
    .replace(/^https?:\/\/[^/]+\//i, '')
    .replace(/^\/+/, '')
    .replace(/^wwwroot\//i, '')
    .replace(/\?.*$/, '')
    .toLowerCase();
}

function studioTargetMatches(patternTarget, currentTarget, options = {}) {
  const allowUntargeted = options.allowUntargeted === true;
  const saved = normalizeStudioTargetPath(patternTarget);
  const current = normalizeStudioTargetPath(currentTarget);
  if (!saved) return allowUntargeted;
  if (!current) return false;
  return saved === current || saved.endsWith(`/${current}`) || current.endsWith(`/${saved}`);
}

function isStudioSearchPatternTargetCompatible(pattern, options = {}) {
  const current = currentStudioSearchPatternTarget();
  const allowUntargeted = options.allowUntargeted === true;
  const dataOk = studioTargetMatches(pattern?.target_data ?? pattern?.targetData, current.target_data, { allowUntargeted });
  const viewOk = studioTargetMatches(pattern?.target_view_def ?? pattern?.targetViewDef, current.target_view_def, { allowUntargeted });
  return dataOk && viewOk;
}

function isEmptyStudioSearchState(state) {
  const uiState = normalizeStudioSearchUiState(state);
  const coreEmpty = Object.keys(uiState.core ?? {}).length === 0;
  const pluginsEmpty = Object.values(uiState.plugins ?? {}).every(value => {
    if (!value || typeof value !== 'object') return true;
    return Object.values(value).every(item => Array.isArray(item) ? item.length === 0 : item == null || item === '');
  });
  return coreEmpty && pluginsEmpty;
}

function makeSearchPatternId(caption) {
  const base = String(caption ?? '').trim()
    .toLowerCase()
    .replace(/\s+/g, '_')
    .replace(/[^a-z0-9_\-ぁ-んァ-ン一-龥]/g, '')
    .slice(0, 60) || 'search_pattern';
  return `local.${base}.${Date.now()}`;
}

function setStudioSearchPatternControlsOpen(open) {
  studioSearchPatternPanelOpen = Boolean(open);
  const controls = $('searchPatternControls');
  const toggle = $('toggleSearchPatternBtn');
  if (controls) controls.classList.toggle('hidden', !studioSearchPatternPanelOpen);
  if (toggle) {
    toggle.textContent = studioSearchPatternPanelOpen ? '検索条件▲' : '検索条件';
    toggle.title = studioSearchPatternPanelOpen ? '検索条件の保存・呼出メニューを閉じる' : '検索条件の保存・呼出メニューを開く';
  }
}

function updateStudioSearchPatternControlState(optionCount = 0) {
  const select = $('searchPatternSelect');
  const loadBtn = $('loadSearchPatternBtn');
  const deleteBtn = $('deleteSearchPatternBtn');
  const selectedOption = select?.selectedOptions?.[0];
  if (loadBtn) loadBtn.disabled = !selectedOption || !selectedOption.dataset.source;
  if (deleteBtn) deleteBtn.disabled = !selectedOption || selectedOption.dataset.source !== 'local';
  if (select) select.title = optionCount > 0
    ? `保存済み検索条件 / Overlay検索パターン: ${optionCount}件`
    : '保存済み検索条件はまだありません。保存ボタンで現在の検索条件を保存できます。';
}

async function saveCurrentStudioSearchPattern() {
  const state = getStudioSearchState();
  if (isEmptyStudioSearchState(state)) {
    const ok = await showStudioConfirmDialog({ title: '空の検索条件を保存しますか？', message: '現在の検索条件は空です。この状態を保存しますか？', okText: '保存する', cancelText: 'キャンセル' });
    if (!ok) return null;
  }

  const defaultName = `検索条件 ${typeof studioFormatDateTime === 'function' ? studioFormatDateTime() : new Date().toLocaleString('ja-JP')}`;
  const caption = await showStudioPromptDialog({ title: '検索条件名', message: '保存する検索条件名を入力してください。', defaultValue: defaultName, okText: '保存する', cancelText: 'キャンセル' });
  if (!caption) return null;

  const patterns = loadLocalStudioSearchPatterns();
  const target = currentStudioSearchPatternTarget();
  const existingIndex = patterns.findIndex(p =>
    String(p.caption ?? '') === String(caption) &&
    isStudioSearchPatternTargetCompatible(p, { allowUntargeted: true })
  );
  if (existingIndex >= 0) {
    const ok = await showStudioConfirmDialog({ title: '検索条件を上書きしますか？', message: `「${caption}」を上書きしますか？`, okText: '上書きする', cancelText: 'キャンセル', danger: true });
    if (!ok) return null;
  }

  const now = typeof studioFormatDateTime === 'function' ? studioFormatDateTime() : new Date().toLocaleString('sv-SE').replace(' ', '_');
  const pattern = {
    schema_version: 'studio_saved_search_pattern_v0_1',
    id: existingIndex >= 0 ? patterns[existingIndex].id : makeSearchPatternId(caption),
    caption,
    saved_at: now,
    ...target,
    ui_state: state
  };

  if (existingIndex >= 0) patterns[existingIndex] = pattern;
  else patterns.push(pattern);
  saveLocalStudioSearchPatterns(patterns);
  setStudioSearchPatternControlsOpen(true);
  refreshStudioSearchPatternSelect(pattern.id);
  if (typeof setStatus === 'function') setStatus(`検索条件を保存しました: ${caption}`, { kind: 'success', title: '検索条件保存' });
  return pattern;
}

async function loadOverlayStudioSearchPatterns() {
  if (studioOverlaySearchPatternCache) return studioOverlaySearchPatternCache;
  const items = [];
  try {
    if (typeof loadStudioOverlayRuntime === 'function') await loadStudioOverlayRuntime();
    const names = typeof studioOverlaySearchPatternNames === 'function' ? studioOverlaySearchPatternNames() : [];
    for (const name of names) {
      try {
        const payload = (await fetchApiJsonWithUrl('data', name)).json;
        (Array.isArray(payload?.search_patterns) ? payload.search_patterns : []).forEach((pattern, index) => {
          items.push({ ...pattern, __source: 'overlay', __apiName: name, __index: index });
        });
      } catch (err) {
        console.warn('Overlay search_patterns の読込に失敗しました:', name, err);
      }
    }
  } catch (err) {
    console.warn('Overlay search_patterns の一覧取得に失敗しました:', err);
  }
  studioOverlaySearchPatternCache = items;
  return items;
}

async function studioSearchPatternOptions() {
  const localItems = loadLocalStudioSearchPatterns()
    .filter(pattern => isStudioSearchPatternTargetCompatible(pattern, { allowUntargeted: true }))
    .map(pattern => ({ ...pattern, __source: 'local' }));
  const overlayItems = (await loadOverlayStudioSearchPatterns())
    .filter(pattern => hasStudioSearchUiState(pattern))
    .filter(pattern => isStudioSearchPatternTargetCompatible(pattern, { allowUntargeted: false }))
    .map(pattern => ({ ...pattern, __source: 'overlay' }));
  return [...localItems, ...overlayItems];
}

async function refreshStudioSearchPatternSelect(selectId = null) {
  const select = $('searchPatternSelect');
  if (!select) return;
  const current = selectId ? '' : select.value;
  select.innerHTML = '';
  const blank = document.createElement('option');
  blank.value = '';
  blank.textContent = '検索条件を選択';
  select.appendChild(blank);

  const options = await studioSearchPatternOptions();
  options.forEach((pattern, index) => {
    const option = document.createElement('option');
    option.value = `${pattern.__source}:${pattern.id ?? pattern.__apiName ?? index}`;
    option.dataset.source = pattern.__source;
    option.dataset.index = String(index);
    option.dataset.patternId = String(pattern.id ?? '');
    option.textContent = `${pattern.__source === 'overlay' ? 'Overlay' : '保存済み'}: ${pattern.caption ?? pattern.id ?? '(no name)'}`;
    select.appendChild(option);
  });
  if (selectId) {
    const byId = [...select.options].find(option => option.dataset.patternId === String(selectId));
    if (byId) select.value = byId.value;
  } else if ([...select.options].some(option => option.value === current)) {
    select.value = current;
  }
  updateStudioSearchPatternControlState(options.length);
}

async function selectedStudioSearchPattern() {
  const select = $('searchPatternSelect');
  if (!select || !select.value) return null;
  const index = Number(select.selectedOptions?.[0]?.dataset?.index ?? -1);
  const options = await studioSearchPatternOptions();
  return Number.isInteger(index) && index >= 0 ? options[index] ?? null : null;
}

async function loadSelectedStudioSearchPattern(options = {}) {
  const pattern = await selectedStudioSearchPattern();
  if (!pattern) {
    if (typeof setStatus === 'function') setStatus('呼び出す検索条件を選択してください', { kind: 'warn', title: '検索条件未選択' });
    return null;
  }
  if (!hasStudioSearchUiState(pattern)) {
    if (typeof setStatus === 'function') setStatus(`この検索パターンには画面復元用 ui_state がありません: ${pattern.caption ?? pattern.id}`, { kind: 'warn', title: 'ui_stateなし' });
    return null;
  }
  applyStudioSearchState(pattern, { runSearch: options.runSearch !== false });
  if (typeof setStatus === 'function') setStatus(`検索条件を呼び出しました: ${pattern.caption ?? pattern.id}`, { kind: 'success', title: '検索条件呼出' });
  return pattern;
}

async function deleteSelectedLocalStudioSearchPattern() {
  const pattern = await selectedStudioSearchPattern();
  if (!pattern || pattern.__source !== 'local') {
    if (typeof setStatus === 'function') setStatus('削除できるのは保存済み検索条件だけです', { kind: 'warn', title: '検索条件削除' });
    return false;
  }
  const patterns = loadLocalStudioSearchPatterns();
  const index = patterns.findIndex(p => String(p.id ?? '') === String(pattern.id ?? ''));
  if (index < 0) return false;
  const ok = await showStudioConfirmDialog({
    title: '保存済み検索条件を削除しますか？',
    message: `保存済み検索条件「${pattern.caption ?? pattern.id}」を削除しますか？`,
    okText: '削除する',
    cancelText: 'キャンセル',
    danger: true
  });
  if (!ok) return false;
  patterns.splice(index, 1);
  saveLocalStudioSearchPatterns(patterns);
  refreshStudioSearchPatternSelect();
  if (typeof setStatus === 'function') setStatus('検索条件を削除しました', { kind: 'success', title: '検索条件削除' });
  return true;
}

function hideStudioSearchPatternStandardUi() {
  ['toggleSearchPatternBtn', 'searchPatternControls'].forEach(id => {
    const el = $(id);
    if (!el) return;
    el.classList.add('hidden');
    el.setAttribute('hidden', 'hidden');
    el.style.display = 'none';
  });
}

function setupStudioSearchPatternButtons() {
  hideStudioSearchPatternStandardUi();
  if (!STUDIO_SEARCH_PATTERN_STANDARD_UI_ENABLED) return;

  $('toggleSearchPatternBtn')?.addEventListener('click', () => setStudioSearchPatternControlsOpen(!studioSearchPatternPanelOpen));
  $('saveSearchPatternBtn')?.addEventListener('click', saveCurrentStudioSearchPattern);
  $('loadSearchPatternBtn')?.addEventListener('click', () => loadSelectedStudioSearchPattern({ runSearch: true }));
  $('deleteSearchPatternBtn')?.addEventListener('click', deleteSelectedLocalStudioSearchPattern);
  $('searchPatternSelect')?.addEventListener('change', () => updateStudioSearchPatternControlState());
  setStudioSearchPatternControlsOpen(false);
  refreshStudioSearchPatternSelect();
}
