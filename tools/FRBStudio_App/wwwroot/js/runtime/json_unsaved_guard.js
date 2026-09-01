// v0.18.127-json-object-unsaved-guard-fix
// JSON Object Studio Core Runtime:
// - 未保存状態を保存ボタンで常時可視化
// - 保存せずに画面/JSONを移動する場合は確認
// - 保存/読込成功でCleanへ戻す
// - Markdown Studioと同じ画面内Confirmを優先
(function installJsonObjectUnsavedGuard(){
  'use strict';

  if (window.__frbJsonObjectUnsavedGuardRuntimeLoaded) return;
  window.__frbJsonObjectUnsavedGuardRuntimeLoaded = true;

  function bootstrap() {
    if (window.__frbJsonObjectUnsavedGuardActive) return;
    window.__frbJsonObjectUnsavedGuardActive = true;

    let baselineSerialized = null;
    let lastSourceDataRef = null;
    let headerDraftDirty = false;
    let detailDraftDirty = false;
    let navigationAwayConfirmed = false;
    let saveWatchToken = 0;
    const bypassClickOnce = new WeakSet();

    function currentSourceData() {
      try {
        return typeof sourceData === 'undefined' ? null : sourceData;
      } catch {
        return null;
      }
    }

    function currentSerialized() {
      const data = currentSourceData();
      if (data == null) return null;
      try {
        return JSON.stringify(data);
      } catch {
        return null;
      }
    }

    function isReadonly() {
      try {
        return Boolean(launchRuntime?.readonly);
      } catch {
        return false;
      }
    }

    function hasLoadedDocument() {
      return currentSourceData() != null;
    }

    function canonicalHasChanged() {
      if (baselineSerialized === null) return false;
      const now = currentSerialized();
      return now !== null && now !== baselineSerialized;
    }

    function hasUnsavedChanges() {
      if (isReadonly() || !hasLoadedDocument()) return false;
      return headerDraftDirty || detailDraftDirty || canonicalHasChanged();
    }

    function cleanSaveLabel() {
      if (isReadonly()) return 'ReadOnly';
      try {
        return currentDataApiUrl ? '保　存' : '別名保存';
      } catch {
        return '保　存';
      }
    }

    function installStyles() {
      if (document.getElementById('jsonObjectUnsavedGuardStyles')) return;
      const style = document.createElement('style');
      style.id = 'jsonObjectUnsavedGuardStyles';
      style.textContent = `
        #saveBtn.is-unsaved {
          border-color: #f59e0b !important;
          background: linear-gradient(135deg, #fff7ed 0%, #fef3c7 100%) !important;
          color: #92400e !important;
          font-weight: 900 !important;
          box-shadow:
            0 0 0 3px rgba(245, 158, 11, .22),
            0 8px 18px rgba(180, 83, 9, .14) !important;
        }
        #saveBtn.is-unsaved:hover:not(:disabled) {
          filter: brightness(.985);
          box-shadow:
            0 0 0 4px rgba(245, 158, 11, .26),
            0 10px 22px rgba(180, 83, 9, .18) !important;
        }
        #saveBtn.is-unsaved:focus-visible {
          outline: 3px solid rgba(245, 158, 11, .38);
          outline-offset: 2px;
        }
      `;
      document.head.appendChild(style);
    }

    function refreshSaveButton() {
      const saveBtn = document.getElementById('saveBtn');
      if (!saveBtn) return false;

      const dirty = hasUnsavedChanges();
      const label = cleanSaveLabel();

      saveBtn.classList.toggle('is-unsaved', dirty);
      saveBtn.dataset.unsaved = dirty ? 'true' : 'false';
      saveBtn.textContent = dirty && !isReadonly() ? `● ${label}` : label;
      saveBtn.title = dirty
        ? '未保存の変更があります。保存してください。'
        : (isReadonly() ? 'ReadOnly' : '保存済みです');
      saveBtn.setAttribute(
        'aria-label',
        dirty
          ? `${label.replace(/\s+/g, '')}（未保存の変更あり）`
          : label.replace(/\s+/g, '')
      );
      return dirty;
    }

    function markSavedBaseline() {
      const data = currentSourceData();
      lastSourceDataRef = data;
      baselineSerialized = data == null ? null : currentSerialized();
      headerDraftDirty = false;
      detailDraftDirty = false;
      navigationAwayConfirmed = false;
      refreshSaveButton();
    }

    function markHeaderDraftDirty() {
      if (!hasLoadedDocument() || isReadonly()) return;
      headerDraftDirty = true;
      refreshSaveButton();
    }

    function markDetailDraftDirty() {
      if (!hasLoadedDocument() || isReadonly()) return;
      detailDraftDirty = true;
      refreshSaveButton();
    }

    function refreshFromCanonical() {
      refreshSaveButton();
    }

    function scheduleCanonicalRefresh() {
      window.setTimeout(refreshFromCanonical, 0);
      window.setTimeout(refreshFromCanonical, 40);
    }

    async function confirmNavigationAway() {
      if (!hasUnsavedChanges()) return true;

      const options = {
        title: '未保存の変更があります',
        message: '現在のJSONに未保存の変更があります。保存せずに別の画面へ移動しますか？',
        okText: '移動する',
        cancelText: 'キャンセル',
        danger: true
      };

      if (typeof window.showStudioConfirmDialog === 'function') {
        return Boolean(await window.showStudioConfirmDialog(options));
      }
      return window.confirm(options.message);
    }

    function shouldIgnoreAnchor(event, anchor) {
      if (!anchor) return true;
      if (event.button !== 0) return true;
      if (event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return true;
      if (anchor.target && String(anchor.target).toLowerCase() === '_blank') return true;
      if (anchor.hasAttribute('download')) return true;

      const raw = String(anchor.getAttribute('href') || '').trim();
      if (!raw || raw.startsWith('#') || raw.toLowerCase().startsWith('javascript:')) return true;

      try {
        const current = new URL(location.href);
        const next = new URL(anchor.href, current);
        if (
          next.origin === current.origin &&
          next.pathname === current.pathname &&
          next.search === current.search &&
          next.hash !== current.hash
        ) return true;
      } catch {
        // URL解決不能なら既存処理へ委ねる。
      }
      return false;
    }

    async function guardNavigationClick(event) {
      const target = event.target instanceof Element ? event.target : null;
      if (!target) return;

      const replaceButton = target.closest(
        '#loadBtn, #maintainViewDefBtn, [data-frb-home], [data-frb-reset]'
      );

      if (replaceButton) {
        if (bypassClickOnce.has(replaceButton)) {
          bypassClickOnce.delete(replaceButton);
          return;
        }
        if (!hasUnsavedChanges()) return;

        event.preventDefault();
        event.stopImmediatePropagation();

        const ok = await confirmNavigationAway();
        if (!ok) return;

        bypassClickOnce.add(replaceButton);
        replaceButton.click();
        return;
      }

      const anchor = target.closest('a[href]');
      if (shouldIgnoreAnchor(event, anchor)) return;
      if (!hasUnsavedChanges()) return;

      event.preventDefault();
      event.stopImmediatePropagation();

      const ok = await confirmNavigationAway();
      if (!ok) return;

      navigationAwayConfirmed = true;
      location.assign(anchor.href);
    }

    function installDraftObservers() {
      document.addEventListener('input', event => {
        const target = event.target instanceof Element ? event.target : null;
        if (!target) return;

        if (target.closest('#headerForm, #headerSection')) {
          markHeaderDraftDirty();
          return;
        }
        if (target.closest('#detailDialog')) {
          markDetailDraftDirty();
        }
      }, true);

      document.addEventListener('change', event => {
        const target = event.target instanceof Element ? event.target : null;
        if (!target) return;

        if (target.closest('#headerForm, #headerSection')) {
          markHeaderDraftDirty();
          return;
        }
        if (target.closest('#detailDialog')) {
          markDetailDraftDirty();
        }
      }, true);

      // button操作でcanonical Dataが変わるものは、既存handler実行後に実Dataとの差分を見る。
      document.addEventListener('click', event => {
        const target = event.target instanceof Element ? event.target : null;
        if (!target) return;

        if (target.closest(
          '#applyDetailBtn, #deleteRowBtn, #viewDefMoveUpBtn, #viewDefMoveDownBtn'
        )) {
          scheduleCanonicalRefresh();
        }

        // SubGridの追加/削除やPasteJSON等はF12前のDraft変更。
        if (
          target.closest('#detailDialog') &&
          target.closest(
            '#pasteDetailJsonBtn, [data-action="add"], [data-action="delete"], ' +
            '.detail-subgrid-add-button, .detail-subgrid-delete-button, .detail-subgrid-row-delete'
          )
        ) {
          markDetailDraftDirty();
        }
      }, true);

      document.addEventListener('keydown', event => {
        if (event.key === 'F12') scheduleCanonicalRefresh();
      }, true);

      const dialog = document.getElementById('detailDialog');
      dialog?.addEventListener('close', () => {
        // F12されずに閉じたDetail DOM Draftは破棄されたので解除。
        detailDraftDirty = false;
        refreshSaveButton();
      });
    }

    function wrapGlobalFunction(name, factory) {
      const original = window[name];
      if (typeof original !== 'function' || original.__frbUnsavedGuardWrapped) return false;

      const wrapped = factory(original);
      wrapped.__frbUnsavedGuardWrapped = true;
      wrapped.__frbUnsavedGuardOriginal = original;
      window[name] = wrapped;
      return true;
    }

    function installBoundaryWrappers() {
      wrapGlobalFunction('loadFromObjects', original => async function (...args) {
        const result = await original.apply(this, args);
        markSavedBaseline();
        return result;
      });

      wrapGlobalFunction('saveOverwriteJson', original => async function (...args) {
        const result = await original.apply(this, args);
        if (result !== false) markSavedBaseline();
        return result;
      });

      wrapGlobalFunction('applyHeaderEdits', original => function (...args) {
        const result = original.apply(this, args);
        headerDraftDirty = false;
        refreshSaveButton();
        return result;
      });

      wrapGlobalFunction('tryCommitCurrentDetailEdits', original => function (...args) {
        const result = original.apply(this, args);
        if (result === true) {
          detailDraftDirty = false;
          refreshSaveButton();
        }
        return result;
      });

      wrapGlobalFunction('syncLoadedDocumentSaveButtonState', original => function (...args) {
        const result = original.apply(this, args);
        refreshSaveButton();
        return result;
      });
    }

    function saveSucceededStatus(text) {
      return /(?:上書き保存しました|主対象JSONを上書き保存しました|保存しました)/.test(
        String(text || '')
      );
    }

    function watchSaveButtonFallback() {
      const saveBtn = document.getElementById('saveBtn');
      if (!saveBtn) return;

      saveBtn.addEventListener('click', () => {
        const token = ++saveWatchToken;
        const startedAt = Date.now();

        const check = () => {
          if (token !== saveWatchToken) return;

          const statusText = String(document.getElementById('status')?.textContent || '');
          if (saveSucceededStatus(statusText)) {
            markSavedBaseline();
            return;
          }

          if (Date.now() - startedAt < 12000) {
            window.setTimeout(check, 120);
          }
        };

        window.setTimeout(check, 80);
      });
    }

    function installSourceReplacementFallback() {
      // loadFromObjectsのwrapが将来のscope変更等で効かなくても、
      // 新しいJSON読込時はsourceData object identityが変わるためClean基準を再確立する。
      lastSourceDataRef = currentSourceData();

      window.setInterval(() => {
        const nowRef = currentSourceData();
        if (nowRef !== lastSourceDataRef) {
          lastSourceDataRef = nowRef;
          baselineSerialized = nowRef == null ? null : currentSerialized();
          headerDraftDirty = false;
          detailDraftDirty = false;
          navigationAwayConfirmed = false;
          refreshSaveButton();
        }
      }, 300);
    }

    function installNavigationGuard() {
      document.addEventListener('click', guardNavigationClick, true);

      window.addEventListener('beforeunload', event => {
        if (navigationAwayConfirmed || !hasUnsavedChanges()) return;
        event.preventDefault();
        event.returnValue = '';
      });
    }

    installStyles();
    installBoundaryWrappers();
    installDraftObservers();
    watchSaveButtonFallback();
    installSourceReplacementFallback();
    installNavigationGuard();

    // 起動時点ですでにautoLoad済みなら、その状態をClean基準にする。
    markSavedBaseline();

    window.FrbJsonObjectUnsavedGuard = Object.freeze({
      hasUnsavedChanges,
      refresh: refreshSaveButton,
      markSaved: markSavedBaseline,
      confirmNavigationAway
    });

    console.info('[JSON Object Studio] 未保存ガード v0.18.127 を有効化しました');
  }

  // このscriptはstate.jsから早期読込される場合がある。
  // 全Runtime/App functionの定義後にbootstrapして、関数ラップの順序依存をなくす。
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', bootstrap, { once: true });
  } else {
    bootstrap();
  }
})();
