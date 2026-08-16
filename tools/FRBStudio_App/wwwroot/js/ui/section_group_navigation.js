// v0.18.73-section-group-navigation-phase2
// ViewDef sectionGroups navigation.
// Pinch from the Outside: choose existing Sections outside the Renderer,
// then let the existing Header / Search / Grid renderers do their normal work.

let activeSectionGroupId = '';

function sectionGroupsForView(view) {
  return Array.isArray(view?.sectionGroups) ? view.sectionGroups : [];
}

function sectionGroupContractForView(view, requestedGroupId='') {
  const sections = Array.isArray(view?.sections) ? view.sections : [];
  const groups = sectionGroupsForView(view);
  if (!groups.length) {
    return {
      enabled: false,
      groups: [],
      activeGroup: null,
      sections
    };
  }

  const sectionsById = new Map();
  for (const section of sections) {
    const sectionId = String(section?.id ?? '').trim();
    if (sectionId) sectionsById.set(sectionId, section);
  }

  const groupIds = new Set();
  for (const group of groups) {
    const groupId = String(group?.id ?? '').trim();
    if (!groupId) throw new Error('sectionGroups[].id が空です');
    if (groupIds.has(groupId)) throw new Error(`sectionGroups の id が重複しています: ${groupId}`);
    groupIds.add(groupId);

    const refs = Array.isArray(group?.sectionIds) ? group.sectionIds : [];
    if (!refs.length) throw new Error(`sectionGroup ${groupId} の sectionIds が空です`);
    const seenRefs = new Set();
    for (const rawSectionId of refs) {
      const sectionId = String(rawSectionId ?? '').trim();
      if (!sectionId) throw new Error(`sectionGroup ${groupId} に空の sectionId があります`);
      if (seenRefs.has(sectionId)) throw new Error(`sectionGroup ${groupId} の sectionId が重複しています: ${sectionId}`);
      seenRefs.add(sectionId);
      if (!sectionsById.has(sectionId)) {
        throw new Error(`sectionGroup ${groupId} が存在しないSectionを参照しています: ${sectionId}`);
      }
    }
  }

  const requested = String(requestedGroupId ?? '').trim();
  const activeGroup = groups.find(group => String(group?.id ?? '').trim() === requested) ?? groups[0];
  const activeSections = activeGroup.sectionIds.map(sectionId => sectionsById.get(String(sectionId).trim()));
  return {
    enabled: true,
    groups,
    activeGroup,
    sections: activeSections
  };
}

function activeSectionGroupContract(view=(typeof mainView === 'function' ? mainView() : null)) {
  return sectionGroupContractForView(view, activeSectionGroupId);
}

function activeSectionsForView(view=(typeof mainView === 'function' ? mainView() : null)) {
  return activeSectionGroupContract(view).sections;
}

function resetSectionGroupNavigation() {
  activeSectionGroupId = '';
  const host = typeof $ === 'function' ? $('sectionGroupNavigation') : null;
  if (host) {
    host.innerHTML = '';
    host.classList.add('hidden');
    host.removeAttribute('aria-label');
  }
  const pane = typeof document !== 'undefined' ? document.querySelector('.json-studio-main-pane') : null;
  pane?.classList.remove('has-section-groups');
}

function renderSectionGroupNavigation() {
  const host = typeof $ === 'function' ? $('sectionGroupNavigation') : null;
  if (!host || typeof mainView !== 'function') return;

  const contract = activeSectionGroupContract(mainView());
  const pane = document.querySelector('.json-studio-main-pane');
  host.innerHTML = '';

  if (!contract.enabled) {
    host.classList.add('hidden');
    host.removeAttribute('aria-label');
    pane?.classList.remove('has-section-groups');
    return;
  }

  activeSectionGroupId = String(contract.activeGroup.id);
  host.classList.remove('hidden');
  host.setAttribute('aria-label', '表示グループ');
  pane?.classList.add('has-section-groups');

  const title = document.createElement('div');
  title.className = 'section-group-navigation-title';
  title.textContent = '表示グループ';
  host.appendChild(title);

  const list = document.createElement('div');
  list.className = 'section-group-navigation-list';
  list.setAttribute('role', 'tablist');
  list.setAttribute('aria-orientation', 'vertical');

  contract.groups.forEach(group => {
    const id = String(group.id);
    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'section-group-navigation-item';
    button.dataset.sectionGroupId = id;
    button.setAttribute('role', 'tab');
    button.setAttribute('aria-selected', String(id === activeSectionGroupId));
    if (id === activeSectionGroupId) button.classList.add('active');
    button.textContent = String(group.caption ?? id);
    button.addEventListener('click', () => activateSectionGroup(id));
    list.appendChild(button);
  });

  host.appendChild(list);
}

function initializeSectionGroupNavigation(defObj=viewDef) {
  const view = defObj?.views?.[0] ?? defObj;
  const contract = sectionGroupContractForView(view, '');
  activeSectionGroupId = contract.enabled ? String(contract.activeGroup.id) : '';
  renderSectionGroupNavigation();
  return contract;
}

function hidePrimaryEditorSections() {
  ['headerSection', 'searchSection', 'gridSection'].forEach(id => {
    const element = typeof $ === 'function' ? $(id) : null;
    if (element) element.classList.add('hidden');
  });
}

function syncActiveGridControls(defObj=viewDef) {
  const gd = typeof gridDef === 'function' ? gridDef() : null;
  const hasGrid = Boolean(gd);
  const readonly = Boolean(typeof launchRuntime !== 'undefined' && launchRuntime?.readonly);
  const virtual = hasGrid && typeof isVirtualDataCompatible === 'function'
    ? isVirtualDataCompatible(defObj, gd)
    : false;

  const add = typeof $ === 'function' ? $('addRowBtn') : null;
  const remove = typeof $ === 'function' ? $('deleteRowBtn') : null;
  const csv = typeof $ === 'function' ? $('gridCsvExportBtn') : null;
  if (add) add.disabled = !hasGrid || virtual || readonly;
  if (remove) remove.disabled = !hasGrid || virtual || readonly;
  if (csv) csv.disabled = !hasGrid;
}

function renderActiveSectionGroup(options={}) {
  const resetSelection = options.resetSelection !== false;
  hidePrimaryEditorSections();

  if (resetSelection) {
    selectedIndex = -1;
    sortState = { field: null, direction: null };
    copiedRow = null;
  }

  const dialog = typeof $ === 'function' ? $('detailDialog') : null;
  if (dialog?.open) dialog.close();

  const hd = typeof headerDef === 'function' ? headerDef() : null;
  const gd = typeof gridDef === 'function' ? gridDef() : null;

  if (hd) renderByKey('header');
  if (gd) {
    renderByKey('search');
    loadRows();
    renderByKey('grid');
  } else {
    currentRows = [];
    filteredRows = [];
  }

  renderByKey('viewExecuteButton');
  if (typeof renderRelatedGridLaunchButtons === 'function') renderRelatedGridLaunchButtons();
  syncActiveGridControls(viewDef);
  return { header: hd, grid: gd };
}

function activateSectionGroup(groupId) {
  if (typeof mainView !== 'function') return false;
  const view = mainView();
  const groups = sectionGroupsForView(view);
  const target = groups.find(group => String(group?.id ?? '').trim() === String(groupId ?? '').trim());
  if (!target) {
    if (typeof setStatus === 'function') {
      setStatus(`表示グループが見つかりません: ${groupId}`, { kind: 'warn', title: '表示グループ' });
    }
    return false;
  }

  activeSectionGroupId = String(target.id);
  renderSectionGroupNavigation();
  renderActiveSectionGroup({ resetSelection: true });

  if (typeof setStatus === 'function') {
    setStatus(`表示グループ: ${target.caption ?? target.id}`, { toast: false });
  }
  return true;
}
