// v0.17.14-search-state-bridge
// Overlay PluginをCoreへ接続する最小PluginHost。
// CoreはPluginの中身を知らず、FieldEditor / SearchFilter / Action の登録口だけを提供する。

const StudioPluginHost = (() => {
  const registeredPlugins = new Map();
  const activatedPlugins = new Set();
  const loadedScripts = new Set();
  const searchFilters = new Map();

  function normalizePluginId(value) {
    return String(value ?? '').trim();
  }

  function normalizePluginArray(value) {
    if (typeof normalizeArray === 'function') return normalizeArray(value);
    if (Array.isArray(value)) return value;
    if (value == null) return [];
    return [value];
  }

  function pluginLog(...args) {
    console.info('[StudioPluginHost]', ...args);
  }

  function pluginWarn(...args) {
    console.warn('[StudioPluginHost]', ...args);
  }

  function dirname(path) {
    const parts = String(path ?? '').replace(/\\/g, '/').split('/').filter(Boolean);
    parts.pop();
    return parts.join('/');
  }

  function isOverlayRootRelative(path) {
    return /^(plugins|value_sets|view_defs|search_patterns|data)\//.test(String(path ?? '').replace(/\\/g, '/'));
  }

  function resolveOverlayRelativePath(baseDir, rawPath, options = {}) {
    const raw = String(rawPath ?? '').trim();
    if (!raw) return null;
    if (raw.startsWith('overlay/')) {
      const parsed = parseStudioOverlayApiName(raw);
      return parsed?.relativePath ?? null;
    }

    const normalized = raw.replace(/\\/g, '/').replace(/^\.\//, '');
    const candidate = isOverlayRootRelative(normalized)
      ? normalized
      : [baseDir, normalized].filter(Boolean).join('/');

    return overlaySafeRelativePath(candidate, options);
  }

  function overlayFileUrl(overlayId, relativePath) {
    const id = overlaySafeId(overlayId);
    const rel = overlaySafeRelativePath(relativePath, { allowedExts: [] });
    if (!id || !rel) throw new Error(`Overlayファイルパスが不正です: ${overlayId}/${relativePath}`);
    return `/api/overlays/${encodeURIComponent(id)}/${rel.split('/').map(encodeURIComponent).join('/')}`;
  }

  function overlayStaticUrl(overlayId, relativePath) {
    const id = overlaySafeId(overlayId);
    const rel = overlaySafeRelativePath(relativePath, { allowedExts: [] });
    if (!id || !rel) throw new Error(`Overlayファイルパスが不正です: ${overlayId}/${relativePath}`);
    return `studio_overlays/${encodeURIComponent(id)}/${rel.split('/').map(encodeURIComponent).join('/')}`;
  }

  function nativeHostBridgeAvailable() {
    try {
      return window.FRBStudioNativeHost?.isAvailable?.() === true;
    } catch {
      return false;
    }
  }

  async function loadScriptThroughFetch(url, meta = {}) {
    const response = await fetch(url, { cache: 'no-store' });
    if (!response.ok) throw new Error(`Plugin script の読み込みに失敗しました: ${url} (${response.status})`);

    // WebView2 NativeShellではwindow.fetchだけが /api/* → Native commandへBridgeされる。
    // <script src="/api/..."> はfetch overrideを通らないため、script本文をBridge経由で取得して実行する。
    const source = await response.text();
    const script = document.createElement('script');
    script.async = false;
    script.dataset.studioPluginScript = 'true';
    script.dataset.studioPluginSource = url;
    script.textContent = `${source}\n//# sourceURL=${url}`;
    document.head.appendChild(script);
    loadedScripts.add(url);
    return { url, cached: false, ...meta, bridged: true };
  }

  async function loadScriptOnce(primaryUrl, fallbackUrl = '') {
    if (loadedScripts.has(primaryUrl)) return { url: primaryUrl, cached: true };

    // v0.18.94: NativeShellではDOMのscript.src通信がnative_host_bridge.jsのfetch契約を通らない。
    // PluginもData/ViewDefと同じOverlay API境界を使うため、Native時だけfetch経由で本文を取得する。
    if (nativeHostBridgeAvailable()) {
      try {
        return await loadScriptThroughFetch(primaryUrl);
      } catch (primaryErr) {
        if (!fallbackUrl || loadedScripts.has(fallbackUrl)) throw primaryErr;
        try {
          return await loadScriptThroughFetch(fallbackUrl, { fallback: true });
        } catch {
          throw primaryErr;
        }
      }
    }

    return new Promise((resolve, reject) => {
      const script = document.createElement('script');
      script.src = primaryUrl;
      script.async = false;
      script.dataset.studioPluginScript = 'true';
      script.onload = () => {
        loadedScripts.add(primaryUrl);
        resolve({ url: primaryUrl, cached: false });
      };
      script.onerror = () => {
        script.remove();
        if (!fallbackUrl || loadedScripts.has(fallbackUrl)) {
          reject(new Error(`Plugin script の読み込みに失敗しました: ${primaryUrl}`));
          return;
        }
        const fallback = document.createElement('script');
        fallback.src = fallbackUrl;
        fallback.async = false;
        fallback.dataset.studioPluginScript = 'true';
        fallback.onload = () => {
          loadedScripts.add(fallbackUrl);
          resolve({ url: fallbackUrl, cached: false, fallback: true });
        };
        fallback.onerror = () => {
          fallback.remove();
          reject(new Error(`Plugin script の読み込みに失敗しました: ${primaryUrl} / ${fallbackUrl}`));
        };
        document.head.appendChild(fallback);
      };
      document.head.appendChild(script);
    });
  }

  function register(plugin) {
    const id = normalizePluginId(plugin?.id ?? plugin?.plugin_id ?? plugin?.name);
    if (!id) throw new Error('Plugin id が空です');
    registeredPlugins.set(id, plugin);
    return plugin;
  }

  function pluginCandidateIds(meta) {
    const ids = [meta?.id, meta?.manifest?.id, meta?.indexItem?.id]
      .map(normalizePluginId)
      .filter(Boolean);
    ids.forEach(id => {
      if (id.includes('.')) ids.push(id.split('.').pop());
      if (id.startsWith('plugin:')) ids.push(id.slice('plugin:'.length));
    });
    return [...new Set(ids.filter(Boolean))];
  }

  function findLoadedPlugin(meta) {
    const overlayPlugins = window.StudioOverlayPlugins || {};
    for (const id of pluginCandidateIds(meta)) {
      if (registeredPlugins.has(id)) return registeredPlugins.get(id);
      if (overlayPlugins[id]) return overlayPlugins[id];
    }
    return null;
  }

  function fieldEditorAliases(editorId) {
    const id = normalizePluginId(editorId);
    const aliases = new Set();
    if (id.startsWith('plugin:')) aliases.add(id.slice('plugin:'.length));
    else aliases.add(`plugin:${id}`);
    return [...aliases].filter(Boolean);
  }

  function normalizeControlValue(value) {
    if (Array.isArray(value)) return value.map(v => String(v));
    if (value == null || value === '') return [];
    return String(value).split(',').map(x => x.trim()).filter(Boolean);
  }


  function clonePluginStateValue(value) {
    if (value == null) return value;
    try {
      return typeof structuredClone === 'function' ? structuredClone(value) : JSON.parse(JSON.stringify(value));
    } catch {
      return Array.isArray(value) ? [...value] : { ...value };
    }
  }

  function replaceObjectContents(target, value) {
    const dest = target && typeof target === 'object' && !Array.isArray(target) ? target : {};
    Object.keys(dest).forEach(key => { delete dest[key]; });
    if (value && typeof value === 'object' && !Array.isArray(value)) {
      Object.entries(value).forEach(([key, item]) => { dest[key] = clonePluginStateValue(item); });
    }
    return dest;
  }

  function setPluginControlValue(control, value) {
    if (!control) return;
    if (control instanceof HTMLSelectElement && control.multiple) {
      const selected = new Set(normalizeControlValue(value).map(String));
      [...control.options].forEach(option => { option.selected = selected.has(String(option.value)); });
      return;
    }
    if (control instanceof HTMLInputElement && control.type === 'checkbox') {
      const selected = new Set(normalizeControlValue(value).map(String));
      control.checked = selected.has(String(control.value));
      return;
    }
    if (control instanceof HTMLInputElement && control.type === 'radio') {
      control.checked = String(control.value) === String(value ?? '');
      return;
    }
    control.value = value == null ? '' : String(value);
  }

  function syncSearchFilterControls(filter) {
    const state = filter?.state ?? {};
    filter?.host?.querySelectorAll?.('input, select, textarea')?.forEach(control => {
      const fieldName = control.dataset.pluginSearchField || control.dataset.field;
      if (!fieldName) return;
      setPluginControlValue(control, state[fieldName]);
    });
  }

  function preparePluginControl(control, context) {
    if (!control || !context) return control;
    if (control instanceof HTMLSelectElement && control.multiple) {
      const selectedValues = new Set(normalizeControlValue(context.value));
      [...control.options].forEach(option => {
        option.selected = selectedValues.has(String(option.value));
      });
      control.dataset.valueMode = 'array';
    }
    return control;
  }

  function registerFieldEditor(editorId, editorDef, aliases = []) {
    const id = normalizePluginId(editorId);
    if (!id) throw new Error('FieldEditor id が空です');

    const factory = (context = {}) => {
      const field = context.field ?? {};
      const normalizedContext = {
        ...context,
        options: context.options ?? field.options ?? [],
        getValue: (row, path) => getByPath(row, path),
        setValue: (row, path, value) => setByPath(row, path, value),
        optionValue,
        optionLabel
      };

      const control = typeof editorDef === 'function'
        ? editorDef(normalizedContext)
        : editorDef?.render?.(normalizedContext);
      if (!control) throw new Error(`FieldEditor ${id} はcontrolを返しませんでした`);
      return preparePluginControl(control, normalizedContext);
    };

    const allAliases = [...fieldEditorAliases(id), ...normalizePluginArray(aliases)];
    registerFieldControl(id, factory, allAliases);
    pluginLog(`FieldEditor registered: ${id}`);
    return factory;
  }

  function registerSearchFilter(filterId, filterDef) {
    const id = normalizePluginId(filterId);
    if (!id) throw new Error('SearchFilter id が空です');
    if (!filterDef || typeof filterDef !== 'object') throw new Error(`SearchFilter ${id} の定義が不正です`);
    searchFilters.set(id, { id, state: {}, ...filterDef });
    pluginLog(`SearchFilter registered: ${id}`);
    return filterDef;
  }

  function registerAction(actionId, handler, aliases = []) {
    const id = normalizePluginId(actionId);
    if (!id) throw new Error('Action id が空です');
    return registerStudioAction(id, handler, aliases);
  }

  function createPluginApi(meta = {}) {
    return {
      plugin: meta,
      registerFieldEditor,
      registerSearchFilter,
      registerAction,
      getViewDef: () => viewDef,
      getSourceData: () => sourceData,
      getRows: () => currentRows,
      getFilteredRowEntries: () => filteredRows,
      getFilteredRows: () => normalizePluginArray(filteredRows).map(x => x?.row ?? x),
      getSelectedIndex: () => selectedIndex,
      getSelectedRow: () => selectedIndex >= 0 ? currentRows?.[selectedIndex] ?? null : null,
      getGridDef: () => typeof gridDef === 'function' ? gridDef() : null,
      renderByKey,
      setStatus,
      showToast: window.showStudioToast,
      getByPath,
      setByPath,
      optionValue,
      optionLabel,
      formatValue,
      cloneData,
      normalizeArray: normalizePluginArray
    };
  }

  async function activatePlugin(plugin, meta = {}) {
    const id = normalizePluginId(plugin?.id ?? meta.id ?? meta?.manifest?.id ?? meta?.indexItem?.id);
    if (!id) throw new Error('Plugin id を特定できません');
    if (activatedPlugins.has(id)) return { id, activated: false, skipped: true };

    const api = createPluginApi({ ...meta, id });
    if (typeof plugin.activate === 'function') {
      await plugin.activate(api);
    } else if (typeof plugin === 'function') {
      await plugin(api);
    } else {
      throw new Error(`Plugin ${id} には activate(studio) がありません`);
    }

    activatedPlugins.add(id);
    pluginLog(`Plugin activated: ${id}`);
    return { id, activated: true };
  }

  async function loadPluginFromIndexItem(indexApiName, indexItem) {
    if (!indexItem || indexItem.enabled === false) return { skipped: true, reason: 'disabled', id: indexItem?.id };

    const parsedIndex = parseStudioOverlayApiName(indexApiName);
    if (!parsedIndex) throw new Error(`Plugin index名が不正です: ${indexApiName}`);
    const overlayId = parsedIndex.overlayId;
    const indexDir = dirname(parsedIndex.relativePath);

    let manifest = null;
    let manifestRel = resolveOverlayRelativePath(indexDir, indexItem.manifest ?? indexItem.plugin_manifest, { allowedExts: ['.json'] });
    if (manifestRel) {
      const manifestName = overlayApiName(overlayId, manifestRel);
      manifest = (await fetchStudioOverlayJsonWithUrl(manifestName)).json;
    }

    const entryRaw = indexItem.script ?? indexItem.entry ?? manifest?.entry ?? manifest?.script ?? 'plugin.js';
    const baseDir = manifestRel ? dirname(manifestRel) : indexDir;
    const entryRel = resolveOverlayRelativePath(baseDir, entryRaw, { allowedExts: ['.js'] });
    if (!entryRel) throw new Error(`Plugin entry が不正です: ${entryRaw}`);

    const primaryUrl = overlayFileUrl(overlayId, entryRel);
    const fallbackUrl = overlayStaticUrl(overlayId, entryRel);
    await loadScriptOnce(primaryUrl, fallbackUrl);

    const meta = { id: indexItem.id ?? manifest?.id, overlayId, indexApiName, indexItem, manifest, manifestRel, entryRel };
    const plugin = findLoadedPlugin(meta);
    if (!plugin) throw new Error(`Plugin script読み込み後にPlugin定義が見つかりません: ${indexItem.id ?? manifest?.id ?? entryRel}`);
    return activatePlugin(plugin, meta);
  }

  async function loadOverlayPlugins(options = {}) {
    const overlay = await loadStudioOverlayRuntime(options);
    const indexNames = overlay?.pluginIndexApiNames ?? [];
    const results = [];
    for (const indexApiName of indexNames) {
      try {
        const indexJson = (await fetchApiJsonWithUrl('data', indexApiName)).json;
        for (const item of normalizePluginArray(indexJson?.plugins)) {
          results.push(await loadPluginFromIndexItem(indexApiName, item));
        }
      } catch (err) {
        pluginWarn(`Plugin index の読み込みに失敗しました: ${indexApiName}`, err);
        results.push({ indexApiName, error: err.message });
      }
    }
    return results;
  }

  function injectSearchFilterStyles() {
    if (document.getElementById('studioPluginHostStyles')) return;
    const style = document.createElement('style');
    style.id = 'studioPluginHostStyles';
    style.textContent = `
      .studio-plugin-search-filters { display: contents; }
      .studio-plugin-search-filter { display: grid; gap: 6px; }
      .studio-plugin-search-filter select[multiple] { min-height: 92px; }
      .studio-plugin-field-hint { font-size: 11px; color: #64748b; }
    `;
    document.head.appendChild(style);
  }

  function renderSearchFilters(container, context = {}) {
    if (!container || !searchFilters.size) return;
    injectSearchFilterStyles();
    const wrap = document.createElement('div');
    wrap.className = 'studio-plugin-search-filters';

    for (const filter of searchFilters.values()) {
      try {
        if (typeof filter.visible === 'function' && !filter.visible(context)) continue;
        const host = document.createElement('div');
        host.className = 'field studio-plugin-search-filter';
        filter.host = host;
        const rendered = filter.render?.(host, {
          ...createPluginApi({ id: filter.id, kind: 'search_filter' }),
          ...context,
          state: filter.state,
          filter
        });
        if (rendered instanceof Node && rendered !== host) host.appendChild(rendered);
        if (host.childNodes.length) wrap.appendChild(host);
      } catch (err) {
        pluginWarn(`SearchFilter render failed: ${filter.id}`, err);
      }
    }

    if (wrap.childNodes.length) container.appendChild(wrap);
  }

  function applySearchFilters(rowEntries, context = {}) {
    let entries = normalizePluginArray(rowEntries);
    for (const filter of searchFilters.values()) {
      if (typeof filter.predicate !== 'function') continue;
      try {
        if (typeof filter.visible === 'function' && !filter.visible(context)) continue;
        entries = entries.filter(entry => filter.predicate(entry.row, filter.state, {
          ...createPluginApi({ id: filter.id, kind: 'search_filter' }),
          ...context,
          entry,
          filter
        }));
      } catch (err) {
        pluginWarn(`SearchFilter predicate failed: ${filter.id}`, err);
      }
    }
    return entries;
  }

  function getSearchFilterStates() {
    const result = {};
    for (const filter of searchFilters.values()) {
      try {
        const raw = typeof filter.getState === 'function'
          ? filter.getState(filter.state, filter)
          : filter.state;
        result[filter.id] = clonePluginStateValue(raw ?? {});
      } catch (err) {
        pluginWarn(`SearchFilter getState failed: ${filter.id}`, err);
      }
    }
    return result;
  }

  function applySearchFilterStates(states = {}, options = {}) {
    const source = states && typeof states === 'object' ? states : {};
    for (const filter of searchFilters.values()) {
      if (!Object.prototype.hasOwnProperty.call(source, filter.id)) continue;
      try {
        const nextState = source[filter.id] ?? {};
        if (typeof filter.setState === 'function') {
          filter.setState(filter.state, clonePluginStateValue(nextState), filter);
        } else {
          filter.state = replaceObjectContents(filter.state, nextState);
        }
        if (options.syncControls !== false) syncSearchFilterControls(filter);
      } catch (err) {
        pluginWarn(`SearchFilter setState failed: ${filter.id}`, err);
      }
    }
  }

  function resetSearchFilters() {
    for (const filter of searchFilters.values()) {
      try {
        if (typeof filter.reset === 'function') filter.reset(filter.state, filter);
        else filter.state = replaceObjectContents(filter.state, {});
        filter.host?.querySelectorAll('input, select, textarea').forEach(el => {
          if (el instanceof HTMLSelectElement && el.multiple) [...el.options].forEach(opt => { opt.selected = false; });
          else if (el instanceof HTMLInputElement && (el.type === 'checkbox' || el.type === 'radio')) el.checked = false;
          else el.value = '';
        });
      } catch (err) {
        pluginWarn(`SearchFilter reset failed: ${filter.id}`, err);
      }
    }
  }

  return {
    register,
    registerFieldEditor,
    registerSearchFilter,
    registerAction,
    loadOverlayPlugins,
    renderSearchFilters,
    applySearchFilters,
    getSearchFilterStates,
    applySearchFilterStates,
    resetSearchFilters,
    createPluginApi,
    _debug: { registeredPlugins, activatedPlugins, loadedScripts, searchFilters }
  };
})();

window.StudioPluginHost = StudioPluginHost;
window.registerStudioPlugin = (plugin) => StudioPluginHost.register(plugin);

async function loadStudioOverlayPlugins(options = {}) {
  return StudioPluginHost.loadOverlayPlugins(options);
}

function renderStudioPluginSearchFilters(container, context = {}) {
  return StudioPluginHost.renderSearchFilters(container, context);
}

function applyStudioPluginSearchFilters(rowEntries, context = {}) {
  return StudioPluginHost.applySearchFilters(rowEntries, context);
}

function getStudioPluginSearchFilterStates() {
  return StudioPluginHost.getSearchFilterStates();
}

function applyStudioPluginSearchFilterStates(states = {}, options = {}) {
  return StudioPluginHost.applySearchFilterStates(states, options);
}

function resetStudioPluginSearchFilters() {
  return StudioPluginHost.resetSearchFilters();
}
