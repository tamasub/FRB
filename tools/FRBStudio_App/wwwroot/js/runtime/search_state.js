// v0.17.14-search-state-save-load
// 検索条件の保存・呼出・画面復元を担当する最小ブリッジ。
// Core検索欄とPlugin SearchFilter stateを同じ ui_state として扱う。

const STUDIO_SEARCH_PATTERN_STORAGE_KEY = 'frbStudio.searchPatterns.v0_17_14';
let studioOverlaySearchPatternCache = null;

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

function studioCoreSearchControls() {
  const form = $('searchForm');
  if (!form) return [];
  return [...form.querySelectorAll('input, select, textarea')]
    .filter(control => !control.closest('.studio-plugin-search-filter'));
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
  return {
    target_data: currentLoadedDataDisplayPath || currentDataApiUrl || '',
    target_view_def: lastLoadedDefName || ''
  };
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

function saveCurrentStudioSearchPattern() {
  const state = getStudioSearchState();
  if (isEmptyStudioSearchState(state) && !confirm('検索条件が空です。この状態を保存しますか？')) return null;

  const defaultName = `検索条件 ${new Date().toLocaleString('ja-JP')}`;
  const caption = prompt('保存する検索条件名を入力してください。', defaultName);
  if (!caption) return null;

  const patterns = loadLocalStudioSearchPatterns();
  const existingIndex = patterns.findIndex(p => String(p.caption ?? '') === String(caption));
  if (existingIndex >= 0 && !confirm(`「${caption}」を上書きしますか？`)) return null;

  const now = new Date().toISOString();
  const target = currentStudioSearchPatternTarget();
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
  refreshStudioSearchPatternSelect();
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
  const localItems = loadLocalStudioSearchPatterns().map(pattern => ({ ...pattern, __source: 'local' }));
  const overlayItems = await loadOverlayStudioSearchPatterns();
  return [...localItems, ...overlayItems];
}

async function refreshStudioSearchPatternSelect() {
  const select = $('searchPatternSelect');
  if (!select) return;
  const current = select.value;
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
    option.textContent = `${pattern.__source === 'overlay' ? 'Overlay' : '保存済み'}: ${pattern.caption ?? pattern.id ?? '(no name)'}`;
    if (!pattern.ui_state && !pattern.uiState) option.textContent += '（画面復元なし）';
    select.appendChild(option);
  });
  if ([...select.options].some(option => option.value === current)) select.value = current;
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
  if (!pattern.ui_state && !pattern.uiState && !pattern.search_state && !pattern.searchState) {
    if (typeof setStatus === 'function') setStatus(`この検索パターンには画面復元用 ui_state がありません: ${pattern.caption ?? pattern.id}`, { kind: 'warn', title: 'ui_stateなし' });
    return null;
  }
  applyStudioSearchState(pattern, { runSearch: options.runSearch !== false });
  if (typeof setStatus === 'function') setStatus(`検索条件を呼び出しました: ${pattern.caption ?? pattern.id}`, { kind: 'success', title: '検索条件呼出' });
  return pattern;
}

function deleteSelectedLocalStudioSearchPattern() {
  const select = $('searchPatternSelect');
  const option = select?.selectedOptions?.[0];
  if (!select || !option || option.dataset.source !== 'local') {
    if (typeof setStatus === 'function') setStatus('削除できるのは保存済み検索条件だけです', { kind: 'warn', title: '検索条件削除' });
    return false;
  }
  const index = Number(option.dataset.index ?? -1);
  const allOptions = [...select.options].filter(o => o.dataset.source);
  const localOrder = allOptions.slice(0, allOptions.findIndex(o => o.dataset.source === 'overlay') >= 0 ? allOptions.findIndex(o => o.dataset.source === 'overlay') : allOptions.length);
  const localIndex = localOrder.indexOf(option);
  const patterns = loadLocalStudioSearchPatterns();
  const pattern = patterns[localIndex];
  if (!pattern) return false;
  if (!confirm(`保存済み検索条件「${pattern.caption ?? pattern.id}」を削除しますか？`)) return false;
  patterns.splice(localIndex, 1);
  saveLocalStudioSearchPatterns(patterns);
  refreshStudioSearchPatternSelect();
  if (typeof setStatus === 'function') setStatus('検索条件を削除しました', { kind: 'success', title: '検索条件削除' });
  return true;
}

function setupStudioSearchPatternButtons() {
  $('saveSearchPatternBtn')?.addEventListener('click', saveCurrentStudioSearchPattern);
  $('loadSearchPatternBtn')?.addEventListener('click', () => loadSelectedStudioSearchPattern({ runSearch: true }));
  $('deleteSearchPatternBtn')?.addEventListener('click', deleteSelectedLocalStudioSearchPattern);
  refreshStudioSearchPatternSelect();
}
