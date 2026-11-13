// FRB Studio: show ● on 反映(F12) only while the current editor has an unapplied draft.
// Editor draft -> F12 commit -> canonical JSON -> Save is intentionally a separate boundary.
(function installStudioDetailApplyIndicator(doc, win) {
  'use strict';
  if (!doc || win.StudioDetailApplyIndicator) return;
  const dialog = doc.getElementById('detailDialog');
  const button = doc.getElementById('applyDetailBtn');
  if (!dialog || !button) return;

  const cleanText = '反映(F12)';
  let baseline = null;
  let refreshQueued = false;
  let lastDirty = null;

  // The existing F12 path already knows how to collect inputs, component panels,
  // subgrids, cards and the pending PasteJSON draft WITHOUT committing anything.
  // Reusing that exact path prevents false 'clean' from DOM-only field inspection.
  function snapshot() {
    if (!dialog.open || typeof win.snapshotCurrentDetailApplyDraft !== 'function') return null;
    return win.snapshotCurrentDetailApplyDraft();
  }

  function paint(dirty) {
    if (lastDirty === dirty && button.dataset.unapplied === String(dirty)) return;
    lastDirty = dirty;
    button.textContent = dirty ? `● ${cleanText}` : cleanText;
    button.classList.toggle('is-unapplied', dirty);
    button.dataset.unapplied = String(dirty);
    button.setAttribute('aria-label', dirty ? '反映（未反映の変更あり、F12）' : '反映（F12）');
    button.title = dirty ? '未反映の変更があります。Enter / F12で反映できます。' : 'F12';
  }

  function refresh() {
    if (!dialog.open || baseline === null) {
      paint(false);
      return false;
    }
    try {
      const current = snapshot();
      const dirty = current !== null && current !== baseline;
      paint(dirty);
      return dirty;
    } catch (error) {
      // Never interfere with an actual F12 apply if the indicator cannot inspect a draft.
      console.warn('[FRB Studio] Apply indicator could not inspect draft', error);
      return false;
    }
  }

  function queueRefresh() {
    if (refreshQueued) return;
    refreshQueued = true;
    win.setTimeout(() => {
      refreshQueued = false;
      refresh();
    }, 0);
  }

  function markReflected() {
    // Only called by successful F12 rebind or by opening a row/new editor.
    // Failed validation never rebinds, so its ● stays on.
    try { baseline = snapshot(); }
    catch (error) {
      baseline = null;
      console.warn('[FRB Studio] Apply indicator baseline unavailable', error);
    }
    paint(false);
  }

  function wrap(name, after) {
    const original = win[name];
    if (typeof original !== 'function') return;
    win[name] = function (...args) {
      const result = original.apply(this, args);
      after();
      return result;
    };
  }

  // Opening a different row or successfully rebuilding the editor establishes
  // a clean draft baseline. Conditional visibility / PasteJSON rerenders do NOT.
  wrap('openDetail', markReflected);
  wrap('openNewDetail', markReflected);
  wrap('rebindDetailAfterCanonicalCommit', markReflected);
  wrap('renderDetailForRow', queueRefresh);

  // Capture after existing input/change/click handlers update the actual draft.
  // Click also catches subgrid row-add/delete/reorder, card actions, preview apply.
  doc.addEventListener('input', event => {
    if (dialog.open && (dialog.contains(event.target) || event.target?.closest?.('dialog[open]'))) queueRefresh();
  }, true);
  doc.addEventListener('change', event => {
    if (dialog.open && (dialog.contains(event.target) || event.target?.closest?.('dialog[open]'))) queueRefresh();
  }, true);
  doc.addEventListener('click', () => {
    if (dialog.open) queueRefresh();
  }, true);
  dialog.addEventListener('close', () => {
    baseline = null;
    paint(false);
  });

  paint(false);
  win.StudioDetailApplyIndicator = Object.freeze({ refresh, markReflected });
})(document, window);
