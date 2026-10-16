// FRB Studio standard keyboard policy (2026-10-16)
// Route shortcuts through the existing apply/search/save actions and validation.
(function installStudioKeyboardStandard(doc) {
  'use strict';
  if (!doc || doc.__studioKeyboardStandardInstalled) return;
  doc.__studioKeyboardStandardInstalled = true;

  function isTextEditing(target) {
    return target?.matches?.('textarea, input:not([type="checkbox"]):not([type="radio"]), [contenteditable="true"]') || false;
  }
  function isMultiline(target) {
    return target?.matches?.('textarea, [contenteditable="true"]') || false;
  }
  function isComposing(event) {
    return event.isComposing || event.keyCode === 229 || event.key === 'Process';
  }
  function clickEnabled(id) {
    const button = doc.getElementById(id);
    if (!button || button.disabled) return false;
    button.click();
    return true;
  }
  function insertNewline(target) {
    if (target.tagName === 'TEXTAREA') {
      const start = target.selectionStart;
      const end = target.selectionEnd;
      target.setRangeText('\n', start, end, 'end');
      target.dispatchEvent(new Event('input', { bubbles: true }));
    } else if (target.isContentEditable) {
      target.focus();
      // Native editing inserts a line break while preserving the current caret.
      if (!doc.execCommand?.('insertLineBreak', false, null)) {
        const selection = doc.getSelection?.();
        if (!selection?.rangeCount) return;
        const range = selection.getRangeAt(0);
        range.deleteContents();
        const br = doc.createElement('br');
        range.insertNode(br);
        range.setStartAfter(br);
        range.collapse(true);
        selection.removeAllRanges();
        selection.addRange(range);
        target.dispatchEvent(new Event('input', { bubbles: true }));
      }
    }
  }
  function isForeignDialogActive(detail) {
    return [...doc.querySelectorAll('dialog[open]')].some(d => d !== detail);
  }
  function isInteractiveChild(target, row) {
    return target !== row && !!target.closest?.('input, textarea, select, button, a, [contenteditable], .document-grid-value');
  }

  // Ctrl+Q: request a real WinForms Close() for the Studio NativeShell window.
  // The launcher is a separate application; do not hide the Studio window here.
  let studioClosePending = false;
  async function requestStudioClose() {
    if (studioClosePending) return;
    studioClosePending = true;
    try {
      const guard = window.FrbJsonObjectUnsavedGuard;
      const confirmed = typeof guard?.confirmNavigationAway === 'function'
        ? await guard.confirmNavigationAway('exit')
        : window.confirm('FRB Studio を終了しますか？ 未保存の変更がある場合は失われます。');
      if (!confirmed) {
        studioClosePending = false;
        return;
      }
      // NativeShell handles the request on its UI thread with Form.Close().
      window.chrome.webview.postMessage({ studio_close_request: true });
    } catch (error) {
      studioClosePending = false;
      console.error('[FRB Studio] Ctrl+Q 終了要求に失敗しました', error);
    }
  }

  // WinForms may receive Ctrl+Q before the WebView document after a mouse
  // launch. Both routes must use this single unsaved-confirmation function.
  if (typeof window !== 'undefined') window.__frbStudioRequestClose = requestStudioClose;

  doc.addEventListener('keydown', event => {
    if (event.defaultPrevented || isComposing(event) || event.altKey) return;
    // Ctrl+Q must not close an ordinary browser tab or bypass unsaved edits.
    if (event.ctrlKey && !event.shiftKey && !event.metaKey &&
        (event.code === 'KeyQ' || event.key?.toLowerCase() === 'q') &&
        window.FRBStudioNativeHost?.isAvailable?.() &&
        typeof window.chrome?.webview?.postMessage === 'function') {
      event.preventDefault();
      event.stopImmediatePropagation();
      if (!event.repeat) void requestStudioClose();
      return;
    }
    const target = event.target;
    if (!(target instanceof Element)) return;
    const detail = doc.getElementById('detailDialog');
    const detailOpen = Boolean(detail?.open);
    const foreignDialog = isForeignDialogActive(detail);

    if ((event.ctrlKey || event.metaKey) && !event.shiftKey && event.key.toLowerCase() === 's') {
      if (foreignDialog) return;
      // Save is only the existing overwrite button; F12 remains a separate commit step.
      event.preventDefault(); // never open the browser Save As dialog
      if (!event.repeat) clickEnabled('saveBtn');
      return;
    }

    if (event.key === 'Enter') {
      const search = doc.getElementById('searchForm');
      const fullTextSearch = doc.getElementById('studioFullTextSearchInput');
      const isSearchInput = search?.contains(target) || target === fullTextSearch;
      const isEditor = detailOpen && detail.contains(target) && !foreignDialog;
      if (isSearchInput || isEditor) {
        // Modified Enter means newline *only* in multiline text controls.
        if (event.ctrlKey || event.shiftKey || event.metaKey) {
          if (isMultiline(target) && (event.ctrlKey || event.shiftKey) && !event.altKey) {
            event.preventDefault();
            event.stopImmediatePropagation();
            insertNewline(target);
          } else if (isTextEditing(target)) {
            event.preventDefault(); // no submit/commit on a modified Enter
          }
          return;
        }
        if (isSearchInput && target.matches?.('input, select, textarea, [contenteditable="true"]')) {
          if (clickEnabled('searchBtn')) {
            event.preventDefault();
            event.stopImmediatePropagation();
          }
          return;
        }
        if (isEditor) {
          if (target.closest?.('.detail-subgrid-card-preview-editor')) {
            // Inline preview first commits its own draft before the parent F12.
            return;
          }
          // Preserve native options/buttons, only change Enter for editable fields
          // and the editor background. No interference with modal pickers.
          if (target.closest?.('button, select, a, [role="combobox"]')) return;
          event.preventDefault();
          event.stopImmediatePropagation();
          clickEnabled('applyDetailBtn');
          return;
        }
      }
    }

    if (event.key !== 'ArrowRight' && event.key !== 'Enter') return;
    if (event.ctrlKey || event.metaKey || event.shiftKey || detailOpen || foreignDialog) return;
    if (isTextEditing(target)) return;
    const grid = doc.getElementById('dataGrid');
    if (!grid?.contains(target)) return;
    const row = target.closest?.('tr[data-source-index], .document-grid-card[data-source-index]');
    if (!row || isInteractiveChild(target, row)) return;
    const index = Number(row.dataset.sourceIndex);
    if (!Number.isInteger(index)) return;
    event.preventDefault();
    event.stopImmediatePropagation();
    // Group roots use the same editor invoked by Enter/double-click.
    if (row.hasAttribute('data-group-id')) {
      selectedIndex = -1;
      studioTreeState().selectedGroup = row.dataset.groupId;
      studioTreeRun(() => studioTreeEditGroup(false));
      return;
    }
    selectedIndex = index;
    if (typeof studioTreeConfig === 'function' && studioTreeConfig()) {
      studioTreeState().selectedGroup = null;
    }
    if (typeof openDetail === 'function') openDetail(index);
  }, true);
})(document);
