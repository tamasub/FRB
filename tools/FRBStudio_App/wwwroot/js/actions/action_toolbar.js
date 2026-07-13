// v0.6-action-execute-button: ViewDef-driven primary execute button runtime.
// Runtime does not know concrete Action names. It reads toolbar.executeButton.action
// from ViewDef and passes that variable actionId to ActionRegistry.

function activeMainViewForAction() {
  return mainView();
}

function viewToolbarDef() {
  const mv = activeMainViewForAction();
  return mv?.toolbar ?? viewDef?.toolbar ?? null;
}

function viewExecuteButtonDef() {
  const toolbar = viewToolbarDef();
  const executeButton = toolbar?.executeButton ?? toolbar?.execute_button ?? null;
  if (!executeButton || executeButton.visible === false) return null;

  const actionId = String(executeButton.action ?? executeButton.actionId ?? executeButton.action_id ?? '').trim();
  if (!actionId) return null;

  return {
    ...executeButton,
    action: actionId,
    caption: String(executeButton.caption ?? executeButton.label ?? '実行').trim() || '実行'
  };
}

// v0.18.6.1-visible-rows-md-button-visibility-guard
// 「表示行をMD出力」は、Markdown Export Mode が review_report の時だけ現れる
// 表示行レビューMD用ショートカットである。Git Diff Run など他Actionは触らない。
function isVisibleRowsMarkdownExecuteButton(executeButton) {
  if (!executeButton) return false;
  const action = String(executeButton.action ?? '').trim();
  const caption = String(executeButton.caption ?? executeButton.label ?? '').trim();
  return action === 'ExportMarkdown' && caption.includes('表示行をMD出力');
}

function currentMarkdownExportModeIsReviewReport() {
  let modeId = '';
  if (typeof markdownSelectedExportModeId === 'function') {
    try { modeId = String(markdownSelectedExportModeId() ?? '').trim(); } catch { modeId = ''; }
  }
  if (!modeId && $('exportMarkdownModeSelect')) modeId = String($('exportMarkdownModeSelect').value ?? '').trim();

  let modeType = modeId;
  if (typeof markdownExportModeById === 'function') {
    try {
      const mode = markdownExportModeById(modeId);
      modeType = String(mode?.type ?? mode?.id ?? modeId).trim();
    } catch { /* keep modeId */ }
  }
  return String(modeId).toLowerCase() === 'review_report'
    || String(modeType).toLowerCase() === 'review_report';
}

function syncViewExecuteButtonVisibilityForMarkdownMode() {
  const btn = $('viewExecuteActionBtn');
  if (!btn) return;

  const executeButton = viewExecuteButtonDef();
  const isTarget = isVisibleRowsMarkdownExecuteButton(executeButton);
  if (!isTarget) {
    btn.classList.remove('hidden');
    btn.removeAttribute('aria-hidden');
    btn.title = executeButton ? `Action: ${executeButton.action}` : '';
    return;
  }

  const shouldShow = currentMarkdownExportModeIsReviewReport();
  btn.classList.toggle('hidden', !shouldShow);
  btn.setAttribute('aria-hidden', shouldShow ? 'false' : 'true');
  btn.title = shouldShow
    ? '現在フィルター表示されている行をレビュー用Markdownとして出力します'
    : 'レビュー用Markdown出力モードの時だけ表示されます';
}

function setupVisibleRowsMarkdownButtonModeGuard() {
  const select = $('exportMarkdownModeSelect');
  if (!select || select.dataset.visibleRowsMarkdownButtonGuard === '1') return;
  select.dataset.visibleRowsMarkdownButtonGuard = '1';
  select.addEventListener('change', syncViewExecuteButtonVisibilityForMarkdownMode);
}

function selectedActionRow() {
  if (selectedIndex >= 0 && Array.isArray(currentRows)) return currentRows[selectedIndex] ?? null;
  return null;
}

function currentExecuteActionContext(executeButton) {
  return currentStudioActionContext({
    source: 'toolbar.executeButton',
    toolbar: viewToolbarDef(),
    executeButton,
    mainView: activeMainViewForAction(),
    gridDef: gridDef(),
    selectedRow: selectedActionRow()
  });
}

function ensureViewExecuteButtonElement() {
  const actions = document.querySelector('.grid-actions');
  if (!actions) return null;

  let btn = $('viewExecuteActionBtn');
  if (!btn) {
    btn = document.createElement('button');
    btn.id = 'viewExecuteActionBtn';
    btn.type = 'button';
    btn.className = 'primary-button small view-execute-action-button';

    const addBtn = $('addRowBtn');
    if (addBtn && addBtn.parentElement === actions) actions.insertBefore(btn, addBtn);
    else actions.appendChild(btn);
  }
  return btn;
}

function removeViewExecuteButtonElement() {
  const btn = $('viewExecuteActionBtn');
  if (btn) btn.remove();
}

function renderViewExecuteButton() {
  const executeButton = viewExecuteButtonDef();
  if (!executeButton) {
    removeViewExecuteButtonElement();
    return;
  }

  const btn = ensureViewExecuteButtonElement();
  if (!btn) return;

  btn.textContent = executeButton.caption;
  btn.title = `Action: ${executeButton.action}`;
  btn.dataset.action = executeButton.action;
  btn.dataset.source = 'toolbar.executeButton';
  btn.disabled = false;

  setupVisibleRowsMarkdownButtonModeGuard();
  syncViewExecuteButtonVisibilityForMarkdownMode();

  btn.onclick = async () => {
    const currentDef = viewExecuteButtonDef();
    const actionId = currentDef?.action;
    if (!actionId) return;

    try {
      btn.disabled = true;
      setStatus(`${currentDef.caption} 実行中...`);
      const result = await executeStudioAction(actionId, currentExecuteActionContext(currentDef));
      const message = result?.message ?? `${currentDef.caption} を実行しました`;
      const statusOptions = result?.statusOptions
        || (result?.status_kind ? { kind: result.status_kind, title: result.status_title } : undefined);
      setStatus(message, statusOptions);
    } catch (err) {
      console.error(err);
      const statusOptions = err?.statusOptions || { kind: 'error', title: 'Actionエラー', duration: 6800, sticky: true };
      setStatus('Actionエラー: ' + err.message, statusOptions);
    } finally {
      const refreshed = viewExecuteButtonDef();
      btn.disabled = !refreshed;
      syncViewExecuteButtonVisibilityForMarkdownMode();
    }
  };
}

registerRenderer('viewExecuteButton', renderViewExecuteButton);
setupVisibleRowsMarkdownButtonModeGuard();
