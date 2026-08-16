// v0.18.67-standard-search-ui-context-menu-phase4
// Standard Search UI controller.
// SearchCapabilityResolverの結果を、検索入力・1階層Context Menu・Override表示へ投影する。
// Field type固有の検索UI判断を画面コードへ分散させず、将来Field Control Class化へ置換可能な境界に集約する。

(function installStandardSearchUiController(global) {
  if (global.StandardSearchUi) return;

  const SEARCH_OPERATOR_REGISTRY_API_PATH = '/api/data/config/search_operator_registry_v0_1.json';
  const VALIDATION_TYPE_REGISTRY_API_PATH = '/api/data/config/validation_type_registry_v0_1.json';

  const runtime = {
    searchOperatorRegistry: null,
    validationTypeRegistry: null,
    resolver: null,
    activeMenu: null,
    menuCleanup: null
  };

  const OPERATOR_CAPTIONS = Object.freeze({
    contains: { default: '含む' },
    not_contains: { default: '含まない' },
    equals: { string: '完全一致', select: '完全一致', boolean: '等しい', default: '等しい' },
    not_equals: { string: '一致以外', select: '一致以外', default: '等しくない' },
    gte: { date: '以降', datetime: '以降', instant: '以降', default: '以上' },
    lte: { date: '以前', datetime: '以前', instant: '以前', default: '以下' },
    between: { date: '範囲', datetime: '範囲', instant: '範囲', default: '範囲' },
    blank: { default: '空白' },
    not_blank: { default: '空白以外' }
  });

  async function ensureContext() {
    if (runtime.resolver && runtime.searchOperatorRegistry && runtime.validationTypeRegistry) {
      return getContextSnapshot();
    }
    if (typeof global.fetchJson !== 'function') {
      throw new Error('標準検索Registryを読み込めません: fetchJson が未初期化です');
    }
    const [searchOperatorRegistry, validationTypeRegistry] = await Promise.all([
      global.fetchJson(SEARCH_OPERATOR_REGISTRY_API_PATH),
      global.fetchJson(VALIDATION_TYPE_REGISTRY_API_PATH)
    ]);
    if (searchOperatorRegistry?.document_type !== 'search_operator_registry' || !Array.isArray(searchOperatorRegistry?.operators)) {
      throw new Error('Search Operator Registryが不正です: config/search_operator_registry_v0_1.json');
    }
    if (validationTypeRegistry?.document_type !== 'validation_type_registry' || !Array.isArray(validationTypeRegistry?.validation_type_definitions)) {
      throw new Error('Validation Type Registryが不正です: config/validation_type_registry_v0_1.json');
    }
    if (typeof global.SearchCapabilityResolver !== 'function') {
      throw new Error('SearchCapabilityResolverが未初期化です');
    }
    runtime.searchOperatorRegistry = searchOperatorRegistry;
    runtime.validationTypeRegistry = validationTypeRegistry;
    runtime.resolver = new global.SearchCapabilityResolver({
      searchOperatorRegistry,
      validationTypeRegistry
    });
    return getContextSnapshot();
  }

  function getContextSnapshot() {
    return {
      searchOperatorRegistry: runtime.searchOperatorRegistry,
      validationTypeRegistry: runtime.validationTypeRegistry,
      ready: Boolean(runtime.resolver)
    };
  }

  function resolveCapability(fieldDefinition) {
    if (!runtime.resolver) return null;
    return runtime.resolver.resolve(fieldDefinition ?? {});
  }

  function operatorCaption(operatorId, valueFamily='') {
    const id = String(operatorId ?? '').trim();
    const family = String(valueFamily ?? '').trim().toLowerCase();
    const entry = OPERATOR_CAPTIONS[id];
    if (!entry) return id;
    return entry[family] ?? entry.default ?? id;
  }

  function operatorMeta(capability, operatorId) {
    return (capability?.effective?.operators ?? []).find(item => String(item?.id ?? '') === String(operatorId ?? '')) ?? null;
  }

  function standardOperator(capability) {
    return String(capability?.derived?.default_operator ?? capability?.effective?.default_operator ?? '').trim();
  }

  function effectiveDefaultOperator(capability) {
    return String(capability?.effective?.default_operator ?? standardOperator(capability)).trim();
  }

  function isVisualOverride(operatorId, capability) {
    const operator = String(operatorId ?? '').trim();
    const standard = standardOperator(capability);
    if (!operator || !standard || operator === standard) return false;
    // RangeはFrom/Toの形そのものが意味を示すため、📌を必須にしない。
    if (operator === 'between') return false;
    return true;
  }

  function closeMenu() {
    if (typeof runtime.menuCleanup === 'function') runtime.menuCleanup();
    runtime.menuCleanup = null;
    runtime.activeMenu?.remove?.();
    runtime.activeMenu = null;
  }

  function placeMenu(menu, x, y) {
    menu.style.left = `${Math.max(6, Number(x) || 0)}px`;
    menu.style.top = `${Math.max(6, Number(y) || 0)}px`;
    requestAnimationFrame(() => {
      const rect = menu.getBoundingClientRect();
      const maxX = Math.max(6, window.innerWidth - rect.width - 6);
      const maxY = Math.max(6, window.innerHeight - rect.height - 6);
      menu.style.left = `${Math.min(Math.max(6, Number(x) || 0), maxX)}px`;
      menu.style.top = `${Math.min(Math.max(6, Number(y) || 0), maxY)}px`;
    });
  }

  function addMenuButton(menu, { text, current=false, className='', onClick }) {
    const button = document.createElement('button');
    button.type = 'button';
    button.className = className;
    button.textContent = `${current ? '✓ ' : '  '}${text}`;
    if (current) button.classList.add('current');
    button.addEventListener('click', (event) => {
      event.preventDefault();
      event.stopPropagation();
      closeMenu();
      onClick?.();
    });
    menu.appendChild(button);
    return button;
  }

  function addMenuSeparator(menu) {
    const separator = document.createElement('div');
    separator.className = 'standard-search-context-separator';
    separator.setAttribute('role', 'separator');
    menu.appendChild(separator);
  }

  function openContextMenu(state, x, y) {
    closeMenu();
    const menu = document.createElement('div');
    menu.className = 'context-menu standard-search-context-menu';
    menu.dataset.standardSearchContextMenu = '1';
    menu.addEventListener('contextmenu', event => event.preventDefault());

    for (const operator of state.capability?.effective?.operators ?? []) {
      const id = String(operator?.id ?? '').trim();
      if (!id) continue;
      addMenuButton(menu, {
        text: operatorCaption(id, state.capability?.value_family),
        current: id === state.currentOperator,
        onClick: () => setOperator(state, id)
      });
    }

    if (String(state.field?.type ?? '') === 'select') {
      addMenuSeparator(menu);
      addMenuButton(menu, {
        text: '⚙ 選択肢メンテナンス...',
        className: 'field-command',
        onClick: () => {
          if (typeof global.openComboOptionMaintenanceForField === 'function') {
            global.openComboOptionMaintenanceForField(state.field);
          }
        }
      });
    }

    document.body.appendChild(menu);
    runtime.activeMenu = menu;
    placeMenu(menu, x, y);

    const closeOnPointer = event => {
      if (!menu.contains(event.target)) closeMenu();
    };
    const closeOnKey = event => {
      if (event.key === 'Escape') closeMenu();
    };
    const closeOnScroll = () => closeMenu();
    setTimeout(() => document.addEventListener('pointerdown', closeOnPointer, true), 0);
    document.addEventListener('keydown', closeOnKey, true);
    window.addEventListener('scroll', closeOnScroll, true);
    runtime.menuCleanup = () => {
      document.removeEventListener('pointerdown', closeOnPointer, true);
      document.removeEventListener('keydown', closeOnKey, true);
      window.removeEventListener('scroll', closeOnScroll, true);
    };
  }

  function rawControl(field, value, controlFactory, state, role='value') {
    const searchField = {
      ...field,
      readonly: false,
      edit: { ...(field?.edit ?? {}), readonly: false }
    };
    // Search Projectionは編集画面固有のradio/listbox指定を引き継がず、
    // select型は検索用の標準ComboBoxとして扱う。
    if (String(searchField.type ?? '') === 'select') {
      delete searchField.control;
      if (searchField.edit) delete searchField.edit.control;
      if (searchField.edit) delete searchField.edit.selectMode;
    }
    const input = controlFactory({
      field: searchField,
      value,
      prefix: 'search',
      readonly: false,
      row: null,
      gd: null
    });
    input.dataset.field = String(field?.field ?? '');
    input.dataset.type = String(field?.type ?? 'text');
    input.dataset.prefix = 'search';
    input.dataset.searchOperator = state.currentOperator;
    input.dataset.searchRole = role;
    input.dataset.searchValueFamily = String(state.capability?.value_family ?? field?.type ?? 'string');
    input.dataset.standardSearchContextMenu = '1';
    input.autocomplete = 'off';

    const family = String(state.capability?.value_family ?? '').toLowerCase();
    if (String(input.tagName).toLowerCase() === 'input') {
      if (family === 'date') input.type = 'date';
      else if (family === 'datetime') input.type = 'datetime-local';
    }
    if (String(field?.type ?? '') === 'select') {
      input.title = '右クリック: 検索方法 / 選択肢メンテナンス';
    } else {
      input.title = '右クリック: 検索方法';
    }
    return input;
  }

  function captureValues(state) {
    if (!state?.controlHost) return;
    const controls = [...state.controlHost.querySelectorAll('input, select, textarea')];
    for (const control of controls) {
      const role = control.dataset.searchRole || 'value';
      if (role === 'from') state.values.from = control.value ?? '';
      else if (role === 'to') state.values.to = control.value ?? '';
      else state.values.value = control.value ?? '';
    }
  }

  function prepareValuesForModeChange(state, previousOperator, nextOperator) {
    const previousMeta = operatorMeta(state.capability, previousOperator);
    const nextMeta = operatorMeta(state.capability, nextOperator);
    const previousMode = String(previousMeta?.value_mode ?? 'single');
    const nextMode = String(nextMeta?.value_mode ?? 'single');
    if (previousMode === nextMode) return;

    if (previousMode === 'single' && nextMode === 'range') {
      const value = state.values.value;
      if (value !== '' && value != null) {
        if (previousOperator === 'lte') state.values.to = value;
        else state.values.from = value;
      }
      return;
    }

    if (previousMode === 'range' && nextMode === 'single') {
      if (nextOperator === 'lte') state.values.value = state.values.to || state.values.from || '';
      else state.values.value = state.values.from || state.values.to || '';
    }
  }

  function updatePin(state) {
    const override = isVisualOverride(state.currentOperator, state.capability);
    state.pinButton.hidden = !override;
    const currentCaption = operatorCaption(state.currentOperator, state.capability?.value_family);
    const standardCaption = operatorCaption(standardOperator(state.capability), state.capability?.value_family);
    state.pinButton.title = override
      ? `標準検索から変更中: ${currentCaption} / 標準: ${standardCaption}`
      : `標準検索: ${standardCaption}`;
  }

  function renderOperator(state) {
    const meta = operatorMeta(state.capability, state.currentOperator);
    const valueMode = String(meta?.value_mode ?? 'single');
    state.controlHost.innerHTML = '';

    if (valueMode === 'range') {
      const range = document.createElement('div');
      range.className = 'standard-search-range';
      const from = rawControl(state.field, state.values.from, state.controlFactory, state, 'from');
      from.placeholder = 'From';
      const separator = document.createElement('span');
      separator.className = 'standard-search-range-separator';
      separator.textContent = '～';
      const to = rawControl(state.field, state.values.to, state.controlFactory, state, 'to');
      to.placeholder = 'To';
      range.append(from, separator, to);
      state.controlHost.appendChild(range);
    } else if (valueMode === 'none') {
      const hidden = document.createElement('input');
      hidden.type = 'hidden';
      hidden.dataset.field = String(state.field?.field ?? '');
      hidden.dataset.type = String(state.field?.type ?? 'text');
      hidden.dataset.prefix = 'search';
      hidden.dataset.searchOperator = state.currentOperator;
      hidden.dataset.searchRole = 'value';
      hidden.dataset.searchValueFamily = String(state.capability?.value_family ?? state.field?.type ?? 'string');
      hidden.dataset.standardSearchContextMenu = '1';
      state.controlHost.appendChild(hidden);
    } else {
      const input = rawControl(state.field, state.values.value, state.controlFactory, state, 'value');
      state.controlHost.appendChild(input);
    }
    updatePin(state);
  }

  function setOperator(state, operatorId) {
    const nextOperator = String(operatorId ?? '').trim();
    if (!nextOperator || !operatorMeta(state.capability, nextOperator)) return;
    const previousOperator = state.currentOperator;
    captureValues(state);
    prepareValuesForModeChange(state, previousOperator, nextOperator);
    state.currentOperator = nextOperator;
    renderOperator(state);
    if (typeof global.setStatus === 'function') {
      global.setStatus(
        `${state.field?.caption ?? state.field?.field ?? '検索'}: ${operatorCaption(nextOperator, state.capability?.value_family)}`,
        { toast: false }
      );
    }
  }

  function createField(field, capability, controlFactory) {
    if (!field || !capability || capability.resolution_status !== 'RESOLVED' || typeof controlFactory !== 'function') return null;
    const wrap = document.createElement('div');
    wrap.className = 'field standard-search-field';
    wrap.dataset.searchField = String(field.field ?? '');

    const label = document.createElement('label');
    label.textContent = String(field.caption ?? field.field ?? '');
    wrap.appendChild(label);

    const line = document.createElement('div');
    line.className = 'standard-search-control-line';
    const controlHost = document.createElement('div');
    controlHost.className = 'standard-search-control-host';
    const pinButton = document.createElement('button');
    pinButton.type = 'button';
    pinButton.className = 'standard-search-pin';
    pinButton.textContent = '📌';
    pinButton.setAttribute('aria-label', '検索方法が標準から変更されています');
    pinButton.hidden = true;
    line.append(controlHost, pinButton);
    wrap.appendChild(line);

    const state = {
      field,
      capability,
      controlFactory,
      currentOperator: effectiveDefaultOperator(capability),
      effectiveDefaultOperator: effectiveDefaultOperator(capability),
      standardOperator: standardOperator(capability),
      values: { value: '', from: '', to: '' },
      wrap,
      controlHost,
      pinButton
    };
    wrap.__standardSearchState = state;
    renderOperator(state);

    wrap.addEventListener('contextmenu', event => {
      event.preventDefault();
      event.stopPropagation();
      openContextMenu(state, event.clientX, event.clientY);
    });
    pinButton.addEventListener('click', event => {
      event.preventDefault();
      event.stopPropagation();
      const rect = pinButton.getBoundingClientRect();
      openContextMenu(state, rect.left, rect.bottom + 4);
    });
    return wrap;
  }

  function resetField(wrap) {
    const state = wrap?.__standardSearchState;
    if (!state) return false;
    state.values = { value: '', from: '', to: '' };
    state.currentOperator = state.effectiveDefaultOperator;
    renderOperator(state);
    return true;
  }

  function resetForm(form) {
    if (!form) return;
    [...form.querySelectorAll('.standard-search-field')].forEach(resetField);
  }

  global.StandardSearchUi = Object.freeze({
    ensureContext,
    getContextSnapshot,
    resolveCapability,
    createField,
    resetField,
    resetForm,
    operatorCaption,
    standardOperator,
    effectiveDefaultOperator,
    isVisualOverride,
    closeMenu,
    registryPaths: Object.freeze({
      searchOperatorRegistry: SEARCH_OPERATOR_REGISTRY_API_PATH,
      validationTypeRegistry: VALIDATION_TYPE_REGISTRY_API_PATH
    })
  });

  global.ensureStandardSearchUiContext = ensureContext;
  global.resolveStandardSearchCapability = resolveCapability;
  global.createStandardSearchField = createField;
  global.resetStandardSearchUi = resetForm;
})(globalThis);
