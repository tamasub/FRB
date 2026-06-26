// v0.13.10.1-main-json-select-autofill-silent
// Main screen UX stabilization:
// - Non-blocking toast status messages
// - When target JSON changes, clear stale ViewDef selection and re-resolve from data.view_def

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
    if (viewDef && sourceData) return '準備OK';
    if (viewDef) return '画面定義読み込み済み';
    return '未読み込み';
  }

  let statusTimer = null;

  window.showStudioToast = function showStudioToast(message, options = {}) {
    const text = String(message ?? '').trim();
    if (!text) return null;
    const stack = ensureStack();
    const kind = options.kind || classifyStatusMessage(text);
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
      statusEl.classList.add('status-transient');
      statusEl.classList.toggle('status-error', classifyStatusMessage(text) === 'error');
    }
    if (text.trim() && options.toast !== false) {
      window.showStudioToast(text, options);
    }
    window.clearTimeout(statusTimer);
    if (statusEl && !options.sticky) {
      const duration = Number(options.duration ?? 4200);
      statusTimer = window.setTimeout(() => {
        if (statusEl.textContent === text) {
          statusEl.textContent = defaultStatusText();
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
      setStatus(reason, { title: '画面定義を再解決します', duration: 2600 });
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
        setStatus(`対象JSONの view_def を反映しました: ${embeddedDef}${candidateMsg}`, { title: '画面定義を再表示', duration: 3200 });
      } else {
        clearCurrentDataViewDefCandidates();
        setStatus('対象JSONに view_def がないため、読み込み時に互換ViewDefを自動探索します', { title: '画面定義を自動探索', duration: 3200 });
      }
    } catch (err) {
      if (seq !== resolveSeq) return;
      console.warn('対象JSONの view_def 事前解決をスキップ:', err);
      clearCurrentDataViewDefCandidates();
      setStatus('対象JSONの view_def 事前解決をスキップしました: ' + err.message, { title: '確認', duration: 4200 });
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

installMainStatusToast();
loadAndApplyAppInfo();
setupPageDrop();
setupComboClearButtons();
setupFileTreePickers();
setupDataSelectionViewDefReset();
setupViewDefMarkdownButtonState();
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
$('clearSearchBtn').addEventListener('click', () => {
  [...$('searchForm').querySelectorAll('input, select, textarea')].forEach(i => i.value = '');
  filteredRows = currentRows.map((row, index) => ({row, index}));
  applySortToFilteredRows();
  renderGrid();
});
$('applyDetailBtn').addEventListener('click', applyDetail);
if ($('pasteCopiedBtn')) $('pasteCopiedBtn').addEventListener('click', pasteCopiedRowToForm);
$('prevDetailBtn').addEventListener('click', () => moveDetail(-1));
$('nextDetailBtn').addEventListener('click', () => moveDetail(1));
$('exportMarkdownBtn').addEventListener('click', exportMarkdown);
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
  await autoLoadFromQuery();
  updateViewDefMarkdownButtonState();
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
