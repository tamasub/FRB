// v0.18.136-live-view-design-editor-tip-top-layer-fix
// Live View Design: Field.width is the canonical visual width for data display/editing.
// Field.width accepts a numeric px value or FULL. Search controls stay at Studio standard width.
// Grid legacy grid.width remains read-compatible.

const STUDIO_STANDARD_FIELD_WIDTH_PX = 220;
const STUDIO_MIN_FIELD_WIDTH_PX = 80;
const STUDIO_MAX_FIELD_WIDTH_PX = 1200;
const STUDIO_FIELD_WIDTH_FULL = 'FULL';

let studioFieldWidthDrafts = new Map();

function studioNormalizeFieldWidth(value) {
  if (value == null || value === '') return null;
  const n = typeof value === 'string' ? Number.parseFloat(value) : Number(value);
  if (!Number.isFinite(n) || n <= 0) return null;
  return Math.max(STUDIO_MIN_FIELD_WIDTH_PX, Math.min(STUDIO_MAX_FIELD_WIDTH_PX, Math.round(n)));
}

function studioNormalizeFieldWidthValue(value) {
  if (typeof value === 'string' && value.trim().toUpperCase() === STUDIO_FIELD_WIDTH_FULL) {
    return STUDIO_FIELD_WIDTH_FULL;
  }
  return studioNormalizeFieldWidth(value);
}

function studioFieldWidthIsFull(value) {
  return studioNormalizeFieldWidthValue(value) === STUDIO_FIELD_WIDTH_FULL;
}

function studioFieldTypeUsesFixedControlWidth(field) {
  const type = String(field?.type ?? '').trim().toLowerCase();
  // Combo/select keeps the Studio standard width by default, but an explicit
  // Field.width (or a Live View Design draft) may resize it just like text fields.
  // Boolean/checkbox/radio remain compact fixed operation controls.
  return ['boolean', 'checkbox', 'radio'].includes(type);
}

function studioFieldWidthKey(section, fieldName) {
  const viewId = String((typeof mainView === 'function' ? mainView()?.id : '') ?? '');
  const sectionId = String(section?.id ?? '');
  const sectionType = String(section?.type ?? '');
  const dataPath = String(section?.dataPath ?? section?.data_path ?? '');
  return [viewId, sectionId, sectionType, dataPath, String(fieldName ?? '')].join('::');
}

function studioFieldWidthSectionDescriptor(section) {
  if (!section) return null;
  return {
    id: String(section.id ?? ''),
    type: String(section.type ?? ''),
    dataPath: String(section.dataPath ?? section.data_path ?? ''),
    caption: String(section.caption ?? '')
  };
}

function studioFieldWidthSectionForContext(prefix, gd=null) {
  const p = String(prefix ?? '').toLowerCase();
  if (p === 'header' && typeof headerDef === 'function') return headerDef();
  if ((p === 'detail' || p === 'grid') && gd) return gd;
  if ((p === 'detail' || p === 'grid') && typeof gridDef === 'function') return gridDef();
  return null;
}

function studioDraftFieldWidth(field, section=null) {
  if (!field?.field) return null;
  const key = studioFieldWidthKey(section, field.field);
  return studioNormalizeFieldWidth(studioFieldWidthDrafts.get(key)?.width);
}

function studioResolvedFieldWidth(field, context='detail', section=null) {
  const ctx = String(context ?? '').toLowerCase();
  if (ctx === 'search') return STUDIO_STANDARD_FIELD_WIDTH_PX;

  // Combo-like controls are intentionally compact operation UI.
  if ((ctx === 'header' || ctx === 'detail') && studioFieldTypeUsesFixedControlWidth(field)) {
    return STUDIO_STANDARD_FIELD_WIDTH_PX;
  }

  const draft = studioDraftFieldWidth(field, section);
  if (draft) return draft;

  const canonical = studioNormalizeFieldWidthValue(field?.width);
  if (canonical === STUDIO_FIELD_WIDTH_FULL) return STUDIO_FIELD_WIDTH_FULL;
  if (canonical) return canonical;

  // Backward compatibility:
  // - Grid keeps reading legacy grid.width.
  // - text / textarea may reuse the legacy width in Header/Detail so existing ViewDefs
  //   immediately gain the common-width experience without a bulk migration.
  const legacy = studioNormalizeFieldWidth(field?.grid?.width);
  if (ctx === 'grid' && legacy) return legacy;
  if ((ctx === 'header' || ctx === 'detail') && ['text', 'textarea'].includes(String(field?.type ?? 'text')) && legacy) {
    return legacy;
  }

  return STUDIO_STANDARD_FIELD_WIDTH_PX;
}

function studioApplyFieldContainerWidth(wrap, field, context='detail', section=null) {
  if (!wrap || !field) return null;
  const width = studioResolvedFieldWidth(field, context, section);
  const full = width === STUDIO_FIELD_WIDTH_FULL;

  wrap.classList.toggle('studio-field-width-full', full);
  wrap.style.width = full ? '100%' : `${width}px`;
  wrap.style.flex = full ? '1 0 100%' : `0 0 ${width}px`;
  wrap.style.maxWidth = '100%';
  wrap.style.boxSizing = 'border-box';
  wrap.dataset.studioFieldWidth = String(width);
  wrap.dataset.studioFieldWidthMode = full ? STUDIO_FIELD_WIDTH_FULL : 'FIXED';
  return width;
}

function studioFieldWidthSaveButtons() {
  return [
    document.getElementById('saveFieldWidthsBtn'),
    document.getElementById('saveDetailFieldWidthsBtn')
  ].filter(Boolean);
}

function studioRefreshFieldWidthSaveButtons() {
  const dirty = studioFieldWidthDrafts.size > 0;
  studioFieldWidthSaveButtons().forEach(button => {
    button.classList.toggle('hidden', !dirty);
    button.disabled = !dirty;
    button.dataset.widthDirty = dirty ? 'true' : 'false';
    button.title = dirty
      ? `${studioFieldWidthDrafts.size}項目の幅変更をViewDefへ保存`
      : '項目幅の変更はありません';
  });
}

function studioResetLiveFieldWidths() {
  studioFieldWidthDrafts = new Map();
  studioRefreshFieldWidthSaveButtons();
}

function studioSetLiveFieldWidth(field, width, section, source='live') {
  if (!field?.field || !section) return null;
  const normalized = studioNormalizeFieldWidth(width);
  if (!normalized) return null;
  const key = studioFieldWidthKey(section, field.field);
  studioFieldWidthDrafts.set(key, {
    width: normalized,
    fieldName: String(field.field),
    section: studioFieldWidthSectionDescriptor(section),
    source: String(source ?? 'live')
  });
  studioRefreshFieldWidthSaveButtons();
  return normalized;
}

function studioFindRawTargetView(defObj, currentViewId='') {
  if (Array.isArray(defObj?.views) && defObj.views.length) {
    return defObj.views.find(view => String(view?.id ?? '') === String(currentViewId ?? '')) ?? defObj.views[0];
  }
  return defObj;
}

function studioFindRawTargetSection(view, descriptor) {
  const sections = Array.isArray(view?.sections) ? view.sections : [];
  if (!sections.length || !descriptor) return null;

  if (descriptor.id) {
    const byId = sections.find(section => String(section?.id ?? '') === descriptor.id);
    if (byId) return byId;
  }
  if (descriptor.dataPath) {
    const byPath = sections.find(section =>
      String(section?.type ?? '') === descriptor.type &&
      String(section?.dataPath ?? section?.data_path ?? '') === descriptor.dataPath
    );
    if (byPath) return byPath;
  }
  if (descriptor.caption) {
    const byCaption = sections.find(section =>
      String(section?.type ?? '') === descriptor.type &&
      String(section?.caption ?? '') === descriptor.caption
    );
    if (byCaption) return byCaption;
  }
  return sections.find(section => String(section?.type ?? '') === descriptor.type) ?? null;
}

function studioViewDefApiPath(rawName) {
  const name = String(rawName ?? '').trim().replace(/^defs\//, '').replace(/\\/g, '/');
  if (!name || name.startsWith('overlay/') || name.startsWith('studio_overlays/')) return '';
  if (name.split('/').some(part => !part || part === '.' || part === '..')) return '';
  return '/api/defs/' + name.split('/').map(part => encodeURIComponent(part)).join('/');
}

function studioApplySavedWidthsToCurrentResolvedView() {
  if (!studioFieldWidthDrafts.size || typeof mainView !== 'function') return;
  const currentView = mainView();
  const sections = Array.isArray(currentView?.sections) ? currentView.sections : [];
  studioFieldWidthDrafts.forEach(entry => {
    const section = studioFindRawTargetSection(currentView, entry.section);
    const field = section?.fields?.find(item => String(item?.field ?? '') === entry.fieldName);
    if (!field) return;
    field.width = entry.width;
    if (field.grid && Object.prototype.hasOwnProperty.call(field.grid, 'width')) {
      delete field.grid.width;
    }
  });
}

async function saveStudioLiveFieldWidths() {
  if (!studioFieldWidthDrafts.size) return true;

  const rawName = String(
    (typeof lastLoadedDefName !== 'undefined' && lastLoadedDefName)
      ? lastLoadedDefName
      : (document.getElementById('defNameInput')?.value ?? '')
  ).trim();
  const apiPath = studioViewDefApiPath(rawName);
  if (!apiPath) {
    const message = '現在のViewDefは直接保存できません。Coreのdefs配下ViewDefを選択してください。';
    if (typeof setStatus === 'function') setStatus(message, { kind: 'warn', title: '項目幅保存' });
    return false;
  }

  const read = await fetch(apiPath, { cache: 'no-store' });
  if (!read.ok) throw new Error(`ViewDef読込に失敗しました (${read.status})`);
  const rawDef = await read.json();

  const currentViewId = String((typeof mainView === 'function' ? mainView()?.id : '') ?? '');
  const rawView = studioFindRawTargetView(rawDef, currentViewId);
  const notFound = [];

  studioFieldWidthDrafts.forEach(entry => {
    const section = studioFindRawTargetSection(rawView, entry.section);
    const field = section?.fields?.find(item => String(item?.field ?? '') === entry.fieldName);
    if (!field) {
      notFound.push(`${entry.section?.id || entry.section?.caption || entry.section?.type}:${entry.fieldName}`);
      return;
    }

    field.width = entry.width;

    // Once a field is explicitly saved through Live View Design, migrate that field
    // from legacy Grid-only width to the single canonical Field.width.
    if (field.grid && Object.prototype.hasOwnProperty.call(field.grid, 'width')) {
      delete field.grid.width;
    }
  });

  if (notFound.length) {
    throw new Error(`ViewDef内の保存対象Fieldを解決できません: ${notFound.join(', ')}`);
  }

  const write = await fetch(apiPath, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(rawDef)
  });
  if (!write.ok) {
    const text = await write.text().catch(() => '');
    throw new Error(`ViewDef項目幅の保存に失敗しました (${write.status}) ${text}`);
  }

  studioApplySavedWidthsToCurrentResolvedView();
  const count = studioFieldWidthDrafts.size;
  studioFieldWidthDrafts.clear();
  studioRefreshFieldWidthSaveButtons();

  if (typeof renderHeader === 'function') renderHeader();
  if (typeof renderGrid === 'function') renderGrid();
  if (document.getElementById('detailDialog')?.open && typeof renderDetailForRow === 'function') {
    const row = (typeof detailMode !== 'undefined' && detailMode === 'new')
      ? (typeof draftRow !== 'undefined' ? draftRow : null)
      : (typeof currentRows !== 'undefined' && typeof selectedIndex !== 'undefined' ? currentRows[selectedIndex] : null);
    if (row) renderDetailForRow(row);
  }

  if (typeof invalidateDefinitionTargetViewDefCache === 'function') {
    invalidateDefinitionTargetViewDefCache(rawName);
  }
  if (typeof setStatus === 'function') {
    setStatus(`項目幅をViewDefへ保存しました: ${count}項目`, { kind: 'success', title: 'Live View Design', toast: false });
  }
  return true;
}

function studioInstallFieldWidthSaveButtons() {
  studioFieldWidthSaveButtons().forEach(button => {
    if (button.dataset.liveWidthInstalled === '1') return;
    button.dataset.liveWidthInstalled = '1';
    button.addEventListener('click', async event => {
      event.preventDefault();
      try {
        await saveStudioLiveFieldWidths();
      } catch (error) {
        console.error('Live View Design width save failed:', error);
        if (typeof setStatus === 'function') {
          setStatus(`項目幅を保存できません: ${error.message}`, { kind: 'error', title: '項目幅保存' });
        }
      }
    });
  });
  studioRefreshFieldWidthSaveButtons();
}


let studioFieldWidthTip = null;

function studioFieldWidthTipHost(sourceElement=null) {
  // A modal <dialog> is rendered in the browser Top Layer.
  // A Tip appended to document.body can therefore sit *behind* the open Detail dialog
  // even with a very large z-index. Keep the Tip in the same Top Layer when the
  // resize source lives inside a modal dialog.
  const source = sourceElement instanceof Element ? sourceElement : null;
  const dialog = source?.closest?.('dialog[open]');
  if (dialog) return dialog;
  return document.body;
}

function studioEnsureFieldWidthTip(sourceElement=null) {
  const host = studioFieldWidthTipHost(sourceElement);
  if (!studioFieldWidthTip?.isConnected) {
    const tip = document.createElement('div');
    tip.className = 'studio-field-width-tip hidden';
    tip.setAttribute('role', 'status');
    tip.setAttribute('aria-live', 'polite');
    studioFieldWidthTip = tip;
  }
  if (studioFieldWidthTip.parentElement !== host) {
    host.appendChild(studioFieldWidthTip);
  }
  return studioFieldWidthTip;
}

function studioShowFieldWidthTip(width, clientX, clientY, sourceElement=null) {
  const normalized = studioNormalizeFieldWidth(width);
  if (!normalized) return;
  const tip = studioEnsureFieldWidthTip(sourceElement);
  tip.textContent = `${normalized}px`;
  tip.style.left = `${Math.round(clientX) + 14}px`;
  tip.style.top = `${Math.round(clientY) + 14}px`;
  tip.classList.remove('hidden');
}

function studioHideFieldWidthTip() {
  if (!studioFieldWidthTip) return;
  studioFieldWidthTip.classList.add('hidden');
}

function studioInstallFieldResizeHandle(wrap, field, context='detail', section=null) {
  if (!wrap || !field || !section) return;
  if (context === 'search' || studioFieldTypeUsesFixedControlWidth(field)) return;
  if (!['text', 'textarea', 'number', 'date', 'datetime', 'select'].includes(String(field.type ?? 'text'))) return;
  if (wrap.querySelector(':scope > .studio-field-resize-handle')) return;

  wrap.classList.add('studio-live-width-field');
  const handle = document.createElement('span');
  handle.className = 'studio-field-resize-handle';
  handle.setAttribute('role', 'separator');
  handle.setAttribute('aria-orientation', 'vertical');
  handle.title = 'ドラッグして項目幅を調整';
  handle.tabIndex = -1;
  wrap.appendChild(handle);

  handle.addEventListener('mousedown', event => {
    if (event.button !== 0) return;
    event.preventDefault();
    event.stopPropagation();

    const startX = event.clientX;
    const startWidth = wrap.getBoundingClientRect().width;
    document.body.classList.add('studio-field-width-resizing');
    studioShowFieldWidthTip(startWidth, event.clientX, event.clientY, wrap);

    let moved = false;
    const onMove = moveEvent => {
      const delta = moveEvent.clientX - startX;
      if (Math.abs(delta) < 1) return;
      moved = true;
      const width = studioNormalizeFieldWidth(startWidth + delta);
      if (!width) return;
      // Direct resize is an explicit choice to leave FULL and use a concrete px width.
      wrap.classList.remove('studio-field-width-full');
      wrap.style.width = `${width}px`;
      wrap.style.flex = `0 0 ${width}px`;
      wrap.dataset.studioFieldWidth = String(width);
      wrap.dataset.studioFieldWidthMode = 'FIXED';
      studioShowFieldWidthTip(width, moveEvent.clientX, moveEvent.clientY, wrap);
    };

    const onUp = upEvent => {
      document.removeEventListener('mousemove', onMove);
      document.removeEventListener('mouseup', onUp);
      document.body.classList.remove('studio-field-width-resizing');
      studioHideFieldWidthTip();
      if (!moved) return;
      const width = studioNormalizeFieldWidth(startWidth + (upEvent.clientX - startX));
      if (!width) return;
      studioSetLiveFieldWidth(field, width, section, `${context}.resize`);
    };

    document.addEventListener('mousemove', onMove);
    document.addEventListener('mouseup', onUp, { once: true });
  });
}

function studioInstallGridColumnResizeHandle(th, field, section, table, col, visibleFields) {
  if (!th || !field || !section || !table || !col) return;
  th.dataset.field = String(field.field ?? '');
  th.classList.add('studio-live-width-column');

  const handle = document.createElement('span');
  handle.className = 'grid-column-resize-handle';
  handle.setAttribute('role', 'separator');
  handle.setAttribute('aria-orientation', 'vertical');
  handle.title = 'ドラッグして項目幅を調整';
  th.appendChild(handle);

  const recalcTableWidth = () => {
    const cols = [...table.querySelectorAll('col')];
    const fullCount = cols.filter(item => item.dataset.studioFieldWidthMode === STUDIO_FIELD_WIDTH_FULL).length;
    const fixedTotal = cols.reduce((sum, item) => {
      if (item.dataset.studioFieldWidthMode === STUDIO_FIELD_WIDTH_FULL) return sum;
      return sum + (studioNormalizeFieldWidth(item.style.width) ?? STUDIO_STANDARD_FIELD_WIDTH_PX);
    }, 0);
    if (fullCount > 0) {
      table.style.width = '100%';
      table.style.minWidth = `${fixedTotal + (fullCount * STUDIO_STANDARD_FIELD_WIDTH_PX)}px`;
      return;
    }
    table.style.width = `${fixedTotal}px`;
    table.style.minWidth = `${fixedTotal}px`;
  };

  handle.addEventListener('click', event => {
    event.preventDefault();
    event.stopPropagation();
  });

  handle.addEventListener('mousedown', event => {
    if (event.button !== 0) return;
    event.preventDefault();
    event.stopPropagation();

    const startX = event.clientX;
    const startWidth = th.getBoundingClientRect().width;
    document.body.classList.add('studio-field-width-resizing');
    studioShowFieldWidthTip(startWidth, event.clientX, event.clientY, th);

    let moved = false;
    const onMove = moveEvent => {
      const delta = moveEvent.clientX - startX;
      if (Math.abs(delta) < 1) return;
      moved = true;
      const width = studioNormalizeFieldWidth(startWidth + delta);
      if (!width) return;
      // Dragging a FULL column intentionally converts that live draft to a fixed px width.
      col.dataset.studioFieldWidthMode = 'FIXED';
      col.style.width = `${width}px`;
      th.style.width = `${width}px`;
      th.style.maxWidth = `${width}px`;
      recalcTableWidth();
      studioShowFieldWidthTip(width, moveEvent.clientX, moveEvent.clientY, th);
    };

    const onUp = upEvent => {
      document.removeEventListener('mousemove', onMove);
      document.removeEventListener('mouseup', onUp);
      document.body.classList.remove('studio-field-width-resizing');
      studioHideFieldWidthTip();

      if (!moved) return;
      const width = studioNormalizeFieldWidth(startWidth + (upEvent.clientX - startX));
      if (!width) return;
      col.dataset.studioFieldWidthMode = 'FIXED';
      col.style.width = `${width}px`;
      th.style.width = `${width}px`;
      th.style.maxWidth = `${width}px`;
      studioSetLiveFieldWidth(field, width, section, 'grid.resize');
      recalcTableWidth();
    };

    document.addEventListener('mousemove', onMove);
    document.addEventListener('mouseup', onUp, { once: true });
  });
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', studioInstallFieldWidthSaveButtons, { once: true });
} else {
  studioInstallFieldWidthSaveButtons();
}
