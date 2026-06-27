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
    }
  };
}

registerRenderer('viewExecuteButton', renderViewExecuteButton);
