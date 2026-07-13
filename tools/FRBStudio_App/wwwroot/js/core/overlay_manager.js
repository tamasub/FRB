// v0.17.0-studio-overlay-manifest-separation
// Studio Core(wwwroot) と勇者Overlay(studio_overlays/default) の握手処理。
// Coreは manifest に宣言された追加定義だけを読む。OverlayはCoreを直接変更しない。

function overlaySafeId(value) {
  const id = String(value ?? '').trim();
  return /^[A-Za-z0-9_-]+$/.test(id) ? id : null;
}

function overlaySafeRelativePath(value, options = {}) {
  const raw = String(value ?? '').trim();
  if (!raw) return null;
  const n = raw.replace(/\\/g, '/').replace(/^\/+/, '');
  if (!n || n.includes('://') || /^[A-Za-z]:/.test(n)) return null;

  const parts = n.split('/');
  if (parts.some(part => !part || part === '.' || part === '..')) return null;

  const allowedExts = options.allowedExts ?? ['.json'];
  if (allowedExts.length) {
    const lower = parts[parts.length - 1].toLowerCase();
    if (!allowedExts.some(ext => lower.endsWith(ext))) return null;
  }
  return parts.join('/');
}

function overlayManifestArray(manifest, ...keys) {
  for (const key of keys) {
    if (Array.isArray(manifest?.[key])) return manifest[key];
  }
  return [];
}

function overlayApiName(overlayId, relativePath) {
  const id = overlaySafeId(overlayId);
  const rel = overlaySafeRelativePath(relativePath, { allowedExts: [] });
  return id && rel ? `overlay/${id}/${rel}` : null;
}

function isStudioOverlayApiName(name) {
  const n = safeJsonFileName(name);
  return Boolean(n && n.startsWith('overlay/'));
}

function parseStudioOverlayApiName(name) {
  const n = safeJsonFileName(name);
  if (!n || !n.startsWith('overlay/')) return null;

  const parts = n.split('/');
  if (parts.length < 4) return null;
  const overlayId = overlaySafeId(parts[1]);
  const relativePath = overlaySafeRelativePath(parts.slice(2).join('/'), { allowedExts: ['.json'] });
  if (!overlayId || !relativePath) return null;

  return { overlayId, relativePath, apiName: `overlay/${overlayId}/${relativePath}` };
}

async function fetchStudioOverlayJsonWithUrl(name) {
  const parsed = parseStudioOverlayApiName(name);
  if (!parsed) throw new Error(`Overlay JSON名が不正です: ${name}`);

  const apiUrl = `/api/overlays/${encodeURIComponent(parsed.overlayId)}/${parsed.relativePath.split('/').map(encodeURIComponent).join('/')}`;
  try {
    return {
      json: await fetchJson(apiUrl),
      url: apiUrl,
      correctedName: parsed.apiName,
      readonly: true
    };
  } catch (apiErr) {
    // GitHub Pages等で wwwroot/studio_overlays/default/... を静的配置した場合の保険。
    const staticUrl = `studio_overlays/${encodeURIComponent(parsed.overlayId)}/${parsed.relativePath.split('/').map(encodeURIComponent).join('/')}`;
    try {
      return {
        json: await fetchJson(staticUrl),
        url: staticUrl,
        correctedName: parsed.apiName,
        readonly: true
      };
    } catch {
      throw apiErr;
    }
  }
}

function normalizeOverlayManifest(manifest, overlayId) {
  const id = overlaySafeId(manifest?.overlay_id) || overlaySafeId(overlayId) || DEFAULT_STUDIO_OVERLAY_ID;

  const jsonList = (values) => values
    .map(value => overlaySafeRelativePath(value, { allowedExts: ['.json'] }))
    .filter(Boolean)
    .map(value => overlayApiName(id, value))
    .filter(Boolean);

  const pluginList = (values) => values
    .map(value => overlaySafeRelativePath(value, { allowedExts: ['.json'] }))
    .filter(Boolean)
    .map(value => overlayApiName(id, value))
    .filter(Boolean);

  return {
    overlayId: id,
    available: true,
    manifest: cloneData(manifest ?? {}),
    valueSetApiNames: jsonList(overlayManifestArray(manifest, 'value_set_files', 'valueSetFiles', 'value_sets')),
    viewDefApiNames: jsonList(overlayManifestArray(manifest, 'view_def_files', 'viewDefFiles', 'view_defs')),
    dataApiNames: jsonList(overlayManifestArray(manifest, 'data_files', 'dataFiles')),
    searchPatternApiNames: jsonList(overlayManifestArray(manifest, 'search_pattern_files', 'searchPatternFiles', 'search_patterns')),
    pluginIndexApiNames: pluginList(overlayManifestArray(manifest, 'plugin_index_files', 'pluginIndexFiles', 'plugin_indexes'))
  };
}

function uniqueOverlayNames(names) {
  const seen = new Set();
  const out = [];
  (Array.isArray(names) ? names : []).forEach(raw => {
    const n = safeJsonFileName(raw);
    if (!n || seen.has(n)) return;
    seen.add(n);
    out.push(n);
  });
  return out;
}

async function fetchSingleStudioOverlayRuntime(requestedId) {
  const id = overlaySafeId(requestedId) || DEFAULT_STUDIO_OVERLAY_ID;
  try {
    let manifest = null;
    let source = '';

    try {
      manifest = await fetchJson(`/api/overlays/${encodeURIComponent(id)}/manifest`);
      source = `/api/overlays/${id}/manifest`;
    } catch (apiErr) {
      try {
        manifest = await fetchJson(`studio_overlays/${encodeURIComponent(id)}/studio_manifest.json`);
        source = `studio_overlays/${id}/studio_manifest.json`;
      } catch {
        console.info(`Studio Overlay「${id}」は未配置です`, apiErr);
        return {
          overlayId: id,
          available: false,
          manifest: null,
          valueSetApiNames: [],
          viewDefApiNames: [],
          dataApiNames: [],
          searchPatternApiNames: [],
          pluginIndexApiNames: []
        };
      }
    }

    const runtime = normalizeOverlayManifest(manifest, id);
    runtime.source = source;
    return runtime;
  } catch (err) {
    console.warn(`Studio Overlay「${id}」の読み込みに失敗しました`, err);
    return {
      overlayId: id,
      available: false,
      manifest: null,
      valueSetApiNames: [],
      viewDefApiNames: [],
      dataApiNames: [],
      searchPatternApiNames: [],
      pluginIndexApiNames: [],
      error: err?.message || String(err)
    };
  }
}

async function listStudioOverlayIdsForLoad(explicitId = '') {
  const direct = overlaySafeId(explicitId);
  if (direct) return [direct];

  try {
    const payload = await fetchJson('/api/overlays');
    const rawIds = Array.isArray(payload) ? payload : (payload?.overlay_ids ?? payload?.overlays ?? payload?.items ?? []);
    const ids = rawIds
      .map(item => overlaySafeId(typeof item === 'string' ? item : (item?.overlay_id ?? item?.id ?? item?.name)))
      .filter(Boolean);
    return [...new Set(ids)].sort((a, b) => a.localeCompare(b));
  } catch {
    return [DEFAULT_STUDIO_OVERLAY_ID];
  }
}

function mergeStudioOverlayRuntimes(runtimes) {
  const active = (Array.isArray(runtimes) ? runtimes : [])
    .filter(r => r?.available && String(r?.manifest?.status ?? 'active').toLowerCase() !== 'disabled');

  if (!active.length) {
    return {
      overlayId: DEFAULT_STUDIO_OVERLAY_ID,
      available: false,
      overlays: [],
      manifest: null,
      valueSetApiNames: [],
      viewDefApiNames: [],
      dataApiNames: [],
      searchPatternApiNames: [],
      pluginIndexApiNames: []
    };
  }

  return {
    overlayId: active.map(r => r.overlayId).join(','),
    available: true,
    overlays: active,
    manifest: {
      schema_version: 'studio_overlay_runtime_merged_v0_1',
      overlay_ids: active.map(r => r.overlayId),
      manifests: active.map(r => r.manifest)
    },
    valueSetApiNames: uniqueOverlayNames(active.flatMap(r => r.valueSetApiNames ?? [])),
    viewDefApiNames: uniqueOverlayNames(active.flatMap(r => r.viewDefApiNames ?? [])),
    dataApiNames: uniqueOverlayNames(active.flatMap(r => r.dataApiNames ?? [])),
    searchPatternApiNames: uniqueOverlayNames(active.flatMap(r => r.searchPatternApiNames ?? [])),
    pluginIndexApiNames: uniqueOverlayNames(active.flatMap(r => r.pluginIndexApiNames ?? [])),
    sources: active.map(r => r.source).filter(Boolean)
  };
}

async function loadStudioOverlayRuntime(options = {}) {
  if (studioOverlayLoadPromise) return studioOverlayLoadPromise;

  const explicitId = overlaySafeId(options.overlayId ?? options.overlay_id ?? '');
  studioOverlayLoadPromise = (async () => {
    try {
      const ids = await listStudioOverlayIdsForLoad(explicitId);
      const runtimes = await Promise.all(ids.map(id => fetchSingleStudioOverlayRuntime(id)));
      const runtime = mergeStudioOverlayRuntimes(runtimes);
      studioOverlayRuntime = runtime;
      return studioOverlayRuntime;
    } finally {
      studioOverlayLoadPromise = null;
    }
  })();

  return studioOverlayLoadPromise;
}

function studioOverlayValueSetSourceItems() {
  const names = studioOverlayRuntime?.valueSetApiNames ?? [];
  return names.map(name => ({ name, explicit: false, overlay: true }));
}

function studioOverlayViewDefNames() {
  return studioOverlayRuntime?.viewDefApiNames ?? [];
}

function studioOverlayDataNames() {
  return studioOverlayRuntime?.dataApiNames ?? [];
}

function studioOverlaySearchPatternNames() {
  return studioOverlayRuntime?.searchPatternApiNames ?? [];
}
