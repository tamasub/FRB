// v0.18.36-detail-dialog-expand
// v0.18.21-json-full-text-search
// v0.13.10.1-main-json-select-autofill-silent
// Main screen UX stabilization:
// - Non-blocking toast status messages
// - When target JSON changes, clear stale ViewDef selection and re-resolve from data.view_def

function setDetailDialogExpanded(expanded) {
  const dialog = $('detailDialog');
  const button = $('detailDialogSizeToggleBtn');
  if (!dialog || !button) return false;

  const next = Boolean(expanded);
  dialog.classList.toggle('detail-dialog-expanded', next);
  button.setAttribute('aria-pressed', String(next));
  const label = next ? '詳細画面を元のサイズに戻す' : '詳細画面を最大化';
  button.setAttribute('aria-label', label);
  button.title = label;
  return next;
}

function toggleDetailDialogSize() {
  const dialog = $('detailDialog');
  if (!dialog) return false;
  return setDetailDialogExpanded(!dialog.classList.contains('detail-dialog-expanded'));
}

function setupDetailDialogSizeToggle() {
  const button = $('detailDialogSizeToggleBtn');
  if (!button || button.dataset.detailDialogSizeBound === 'true') return;
  button.dataset.detailDialogSizeBound = 'true';
  button.addEventListener('click', event => {
    event.preventDefault();
    event.stopPropagation();
    toggleDetailDialogSize();
  });
}

function installMainStatusToast() {
  if (window.__frbMainStatusToastInstalled) return;
  window.__frbMainStatusToastInstalled = true;

  const css = `
    .studio-toast-stack {
      position: fixed;
      right: 18px;
      bottom: 18px;
      z-index: 2147483000;
      display: grid;
      gap: 10px;
      width: min(420px, calc(100vw - 36px));
      pointer-events: none;
    }
    .studio-toast {
      pointer-events: auto;
      display: grid;
      gap: 4px;
      padding: 14px 16px;
      border: 1px solid rgba(148, 163, 184, 0.34);
      border-radius: 14px;
      background: rgba(255, 255, 255, 0.96);
      color: #0f172a;
      box-shadow: 0 18px 44px rgba(15, 23, 42, 0.18);
      font-size: 13px;
      line-height: 1.55;
      white-space: pre-wrap;
      word-break: break-word;
      transform: translateY(8px);
      opacity: 0;
      transition: opacity .18s ease, transform .18s ease;
    }
    .studio-toast.visible {
      transform: translateY(0);
      opacity: 1;
    }
    .studio-toast-title {
      font-weight: 900;
      font-size: 13px;
    }
    .studio-toast-body {
      color: #334155;
    }
    .studio-toast.info {
      border-color: rgba(59, 130, 246, 0.28);
    }
    .studio-toast.success {
      border-color: rgba(34, 197, 94, 0.34);
    }
    .studio-toast.warn {
      border-color: rgba(245, 158, 11, 0.38);
    }
    .studio-toast.error {
      border-color: rgba(239, 68, 68, 0.42);
    }
    .status.status-transient {
      transition: opacity .18s ease;
    }
  `;

  if (!document.getElementById('studioMainToastStyles')) {
    const style = document.createElement('style');
    style.id = 'studioMainToastStyles';
    style.textContent = css;
    document.head.appendChild(style);
  }

  function ensureStack() {
    let stack = document.getElementById('studioMainToastStack');
    if (!stack) {
      stack = document.createElement('div');
      stack.id = 'studioMainToastStack';
      stack.className = 'studio-toast-stack';
      stack.setAttribute('aria-live', 'polite');
      stack.setAttribute('aria-atomic', 'false');
      document.body.appendChild(stack);
    }
    return stack;
  }

  function classifyStatusMessage(message) {
    const text = String(message ?? '');
    if (/エラー|失敗|不正|できません|ありません/.test(text)) return 'error';
    if (/警告|注意|未使用|確認|補正/.test(text)) return 'warn';
    if (/完了|読み込みました|保存しました|追加しました|更新しました|実行しました|コピー/.test(text)) return 'success';
    return 'info';
  }

  function defaultStatusText() {
    if (typeof currentLoadedDataStatusText === 'function') {
      const loadedDataText = currentLoadedDataStatusText();
      if (loadedDataText) return loadedDataText;
    }
    if (viewDef && sourceData) return '準備OK';
    if (viewDef) return '画面定義読み込み済み';
    return '未読み込み';
  }

  function studioDebugStatus(message, options = {}) {
    const text = String(message ?? '').trim();
    if (!text) return;
    const source = options.source ? `[${options.source}] ` : '';
    console.log(`[FRBStudio status] ${source}${text}`);
  }

  function shouldShowStatusToast(kind, options = {}) {
    if (options.toast === false) return false;
    if (options.forceToast === true) return true;
    return kind === 'warn' || kind === 'error';
  }

  let statusTimer = null;

  window.showStudioToast = function showStudioToast(message, options = {}) {
    const text = String(message ?? '').trim();
    if (!text) return null;
    const kind = options.kind || classifyStatusMessage(text);
    if (!shouldShowStatusToast(kind, options)) {
      studioDebugStatus(text, { ...options, source: options.source || 'toast-suppressed' });
      return null;
    }
    const stack = ensureStack();
    const toast = document.createElement('div');
    toast.className = `studio-toast ${kind}`;
    const title = options.title || (kind === 'error' ? 'エラー' : kind === 'warn' ? '確認' : kind === 'success' ? '完了' : '通知');
    toast.innerHTML = `<div class="studio-toast-title"></div><div class="studio-toast-body"></div>`;
    toast.querySelector('.studio-toast-title').textContent = title;
    toast.querySelector('.studio-toast-body').textContent = text;
    stack.appendChild(toast);
    requestAnimationFrame(() => toast.classList.add('visible'));
    const duration = Number(options.duration ?? (kind === 'error' ? 6800 : 4200));
    const close = () => {
      toast.classList.remove('visible');
      window.setTimeout(() => toast.remove(), 220);
    };
    toast.addEventListener('click', close);
    window.setTimeout(close, Math.max(1200, duration));
    return toast;
  };

  setStatus = function setStatusToast(message, options = {}) {
    const text = String(message ?? '');
    const statusEl = $('status');
    if (statusEl) {
      statusEl.textContent = text;
      statusEl.title = text;
      statusEl.classList.add('status-transient');
      statusEl.classList.toggle('status-error', classifyStatusMessage(text) === 'error');
    }
    const kind = options.kind || classifyStatusMessage(text);
    if (text.trim() && shouldShowStatusToast(kind, options)) {
      window.showStudioToast(text, { ...options, kind });
    } else if (text.trim()) {
      studioDebugStatus(text, { ...options, source: options.source || 'status-suppressed' });
    }
    window.clearTimeout(statusTimer);
    if (statusEl && !options.sticky) {
      const duration = Number(options.duration ?? 4200);
      statusTimer = window.setTimeout(() => {
        if (statusEl.textContent === text) {
          const fallbackText = defaultStatusText();
          statusEl.textContent = fallbackText;
          statusEl.title = fallbackText;
          statusEl.classList.remove('status-error');
        }
      }, Math.max(1200, duration));
    }
  };
}


function hideAllFileTreePickersSoon() {
  const hide = () => {
    try {
      document.querySelectorAll('.file-tree-picker:not(.hidden)').forEach(picker => picker.classList.add('hidden'));
    } catch { /* ignore */ }
  };
  hide();
  window.requestAnimationFrame?.(hide);
  window.setTimeout(hide, 0);
  window.setTimeout(hide, 80);
}

function setComboValueSilently(input, value) {
  if (!input) return;
  input.value = value || '';
  if (typeof updateSelectedJsonFolderButtonStates === 'function') {
    updateSelectedJsonFolderButtonStates();
  }
  hideAllFileTreePickersSoon();
}

function setupDataSelectionViewDefReset() {
  const dataInput = $('dataNameInput');
  const defInput = $('defNameInput');
  if (!dataInput || !defInput || dataInput.dataset.viewDefResetInstalled === '1') return;
  dataInput.dataset.viewDefResetInstalled = '1';

  let lastObservedDataName = safeJsonFileName(dataInput.value) || '';
  let resolveSeq = 0;
  let debounceTimer = null;

  function clearDefSelection(reason) {
    const hadDef = String(defInput.value ?? '').trim();
    setComboValueSilently(defInput, '');

    const defFile = $('defFile');
    if (defFile) {
      try { defFile.value = ''; } catch { /* ignore */ }
    }
    const defFileName = $('defFileName');
    if (defFileName) defFileName.textContent = 'Drop';
    updateViewDefMarkdownButtonState();

    if (hadDef && reason) {
      console.log('[FRBStudio viewdef] ' + reason);
    }
  }

  async function resolveEmbeddedViewDefForData(dataName, seq) {
    try {
      const loaded = await fetchApiJsonWithUrl('data', dataName);
      if (seq !== resolveSeq) return;
      const actualDataName = loaded.correctedName || jsonNameFromUrl(loaded.url, 'data') || dataName;
      if (actualDataName && actualDataName !== dataName && safeJsonFileName(dataInput.value) === dataName) {
        dataInput.value = actualDataName;
        lastObservedDataName = actualDataName;
      }
      const candidates = updateCurrentDataViewDefCandidates(loaded.json, actualDataName);
      const embeddedDef = getPreferredDataViewDefName(loaded.json);
      if (embeddedDef) {
        setComboValueSilently(defInput, embeddedDef);
        updateViewDefMarkdownButtonState();
        const candidateMsg = currentDataViewDefCandidateMode
          ? ` / 候補 ${candidates.length}件`
          : '';
        console.log(`[FRBStudio viewdef] 対象JSONの view_def を反映: ${embeddedDef}${candidateMsg}`);
      } else {
        clearCurrentDataViewDefCandidates();
        console.log('[FRBStudio viewdef] 対象JSONに view_def がないため、読み込み時に互換ViewDefを自動探索します');
      }
    } catch (err) {
      if (seq !== resolveSeq) return;
      console.warn('対象JSONの view_def 事前解決をスキップ:', err);
      clearCurrentDataViewDefCandidates();
      console.warn('対象JSONの view_def 事前解決をスキップしました:', err);
    }
  }

  function handleDataSelectionChanged(event) {
    const dataName = safeJsonFileName(dataInput.value);
    if (!dataName) {
      clearCurrentDataViewDefCandidates();
      return;
    }
    if (dataName === lastObservedDataName && event?.type !== 'change') return;
    lastObservedDataName = dataName;
    resolveSeq += 1;
    const seq = resolveSeq;

    clearDefSelection('対象JSONを変更したため、古い画面定義JSON選択をクリアしました');

    window.clearTimeout(debounceTimer);
    debounceTimer = window.setTimeout(() => {
      resolveEmbeddedViewDefForData(dataName, seq);
    }, event?.type === 'change' ? 0 : 280);
  }

  dataInput.addEventListener('input', handleDataSelectionChanged);
  dataInput.addEventListener('change', handleDataSelectionChanged);
}


function selectedJsonFolderButtonConfigs() {
  return [
    {
      kind: 'viewdef',
      inputId: 'defNameInput',
      buttonId: 'openDefFolderBtn',
      label: '画面定義JSON',
      getName: () => selectedDefName()
    },
    {
      kind: 'data',
      inputId: 'dataNameInput',
      buttonId: 'openDataFolderBtn',
      label: '対象JSON',
      getName: () => selectedDataName()
    }
  ];
}

function updateSelectedJsonFolderButtonStates() {
  selectedJsonFolderButtonConfigs().forEach(({ inputId, buttonId }) => {
    const input = $(inputId);
    const button = $(buttonId);
    if (!input || !button) return;
    button.disabled = !safeJsonFileName(input.value);
  });
}

function setupSelectedJsonFolderButtons() {
  const configs = selectedJsonFolderButtonConfigs();
  updateSelectedJsonFolderButtonStates();

  configs.forEach(({ kind, inputId, buttonId, label, getName }) => {
    const input = $(inputId);
    const button = $(buttonId);
    if (!input || !button) return;
    if (button.dataset.folderOpenInstalled === '1') {
      updateSelectedJsonFolderButtonStates();
      return;
    }
    button.dataset.folderOpenInstalled = '1';

    const sync = () => updateSelectedJsonFolderButtonStates();
    input.addEventListener('input', sync);
    input.addEventListener('change', sync);
    sync();

    button.addEventListener('click', async (event) => {
      event.preventDefault();
      event.stopPropagation();

      let jsonName = null;
      try {
        jsonName = getName();
      } catch (err) {
        console.warn(err);
        setStatus(`${label}の場所を開けません: ${err.message}`, { kind: 'error', title: 'フォルダーを開けません' });
        return;
      }

      if (!jsonName) {
        setStatus(`${label}が選択されていません`, { kind: 'warn', title: 'JSON未選択' });
        return;
      }

      try {
        const res = await fetch('/api/shell/open-json-folder', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ kind, path: jsonName, select_file: true })
        });
        const text = await res.text();
        let payload = null;
        try { payload = text ? JSON.parse(text) : null; } catch { /* ignore */ }
        if (!res.ok) throw new Error(payload?.error || text || `HTTP ${res.status}`);
        setStatus(`${label}の場所を開きました: ${jsonName}`, { kind: 'success', title: 'Explorer起動', toast: false });
      } catch (err) {
        console.error(err);
        setStatus(`${label}の場所を開けません: ${err.message}`, { kind: 'error', title: 'フォルダーを開けません' });
      }
    });
  });
}

installMainStatusToast();
loadAndApplyAppInfo();
setupPageDrop();
setupComboClearButtons();
setupViewDefMaintenanceButton();
setupSelectedJsonFolderButtons();
setupFileTreePickers();
setupDataSelectionViewDefReset();
setupViewDefMarkdownButtonState();
if (typeof setupStudioSearchPatternButtons === 'function') setupStudioSearchPatternButtons();
if (typeof setupStudioJsonRoundTrip === 'function') setupStudioJsonRoundTrip();
setupDetailDialogSizeToggle();
suppressBrowserAutofillOnComboInputs();

$('loadBtn').addEventListener('click', async () => {
  try {
    await loadFromFiles();
  } catch (err) {
    console.error(err);
    setStatus('エラー: ' + err.message, { kind: 'error', title: '読込エラー' });
  }
});

$('searchBtn').addEventListener('click', applySearch);
$('addRowBtn').addEventListener('click', addGridRow);
$('deleteRowBtn').addEventListener('click', deleteSelectedRow);
if ($('gridCsvExportBtn')) $('gridCsvExportBtn').addEventListener('click', exportVisibleGridCsv);
$('clearSearchBtn').addEventListener('click', () => {
  const fullText = $('studioFullTextSearchInput');
  if (fullText) fullText.value = '';
  [...$('searchForm').querySelectorAll('input, select, textarea')].forEach(i => {
    if (i instanceof HTMLSelectElement && i.multiple) [...i.options].forEach(opt => { opt.selected = false; });
    else i.value = '';
  });
  if (typeof resetStudioPluginSearchFilters === 'function') resetStudioPluginSearchFilters();
  filteredRows = currentRows.map((row, index) => ({row, index}));
  applySortToFilteredRows();
  renderGrid();
});
$('applyDetailBtn').addEventListener('click', applyDetail);
if ($('pasteCopiedBtn')) $('pasteCopiedBtn').addEventListener('click', pasteCopiedRowToForm);
$('prevDetailBtn').addEventListener('click', () => moveDetail(-1));
$('nextDetailBtn').addEventListener('click', () => moveDetail(1));
$('exportMarkdownBtn').addEventListener('click', () => exportMarkdown(typeof markdownSelectedExportModeId === 'function' ? markdownSelectedExportModeId() : null));
if ($('exportMarkdownModeSelect')) $('exportMarkdownModeSelect').addEventListener('change', () => {
  if (typeof setStatus === 'function') setStatus(`Markdown出力モード: ${$('exportMarkdownModeSelect').selectedOptions?.[0]?.textContent || $('exportMarkdownModeSelect').value}`, { toast: false });
});
if ($('exportViewDefMarkdownBtn')) $('exportViewDefMarkdownBtn').addEventListener('click', exportViewDefMarkdown);
$('saveBtn').addEventListener('click', async () => {
  try {
    await saveOverwriteJson();
  } catch (err) {
    console.error(err);
    setStatus('保存エラー: ' + err.message, { kind: 'error', title: '保存エラー' });
  }
});

refreshServerLists().finally(async () => {
  if (typeof loadStudioOverlayPlugins === 'function') {
    const results = await loadStudioOverlayPlugins();
    const activated = results.filter(x => x?.activated).map(x => x.id);
    if (activated.length) {
      console.log(`[FRBStudio PluginHost] Overlay Pluginを読み込みました: ${activated.join(' / ')}`);
    }
  }
  await autoLoadFromQuery();
  updateViewDefMarkdownButtonState();
  setupSelectedJsonFolderButtons();
});

window.__NCJS_exportScreenState = function () {
  return {
    appTitle: document.title,
    url: location.href,
    headerText: document.body.innerText.includes('JSON Object Studio'),
    buttons: Array.from(document.querySelectorAll('button')).map(b => b.innerText.trim()).filter(Boolean),
    selects: Array.from(document.querySelectorAll('select')).map(s => ({ id: s.id || '', value: s.value || '', optionCount: s.options.length })),
    inputs: Array.from(document.querySelectorAll('input')).map(i => ({ id: i.id || '', type: i.type || '', value: i.value || '' }))
  };
};
