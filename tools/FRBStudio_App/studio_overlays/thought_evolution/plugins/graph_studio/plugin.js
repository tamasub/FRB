// Thought Evolution Studio v0.1 / Generic Graph Overlay
// External library free: SVG + CSS + plain JavaScript.

(function () {
  'use strict';

  const PLUGIN_ID = 'thought_evolution.graph_studio';
  const ACTION_ID = 'thought_evolution.open';
  const STYLE_ID = 'thoughtEvolutionStudioV01Styles';
  const DIALOG_ID = 'thoughtEvolutionStudioV01';
  const SVG_NS = 'http://www.w3.org/2000/svg';

  function clone(value) {
    if (value == null) return value;
    try {
      return typeof structuredClone === 'function'
        ? structuredClone(value)
        : JSON.parse(JSON.stringify(value));
    } catch {
      return value;
    }
  }

  function normalizeArray(value) {
    if (Array.isArray(value)) return value;
    if (value == null || value === '') return [];
    return [value];
  }

  function text(value) {
    return value == null ? '' : String(value);
  }

  function escapeHtml(value) {
    return text(value).replace(/[&<>"']/g, ch => ({
      '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
    }[ch]));
  }

  function safeId(value, fallback = '') {
    const id = text(value).trim();
    return /^[A-Za-z0-9_.:-]+$/.test(id) ? id : fallback;
  }

  function safeRelativePath(value) {
    const raw = text(value).trim().replace(/\\/g, '/').replace(/^\/+/, '');
    if (!raw || raw.includes('://') || /^[A-Za-z]:/.test(raw)) return '';
    const parts = raw.split('/');
    if (parts.some(part => !part || part === '.' || part === '..')) return '';
    return parts.join('/');
  }

  function pathCandidates(defaultOverlayId, rawPath) {
    const raw = text(rawPath).trim().replace(/\\/g, '/');
    if (!raw) return [];

    if (raw.startsWith('/api/overlays/')) return [raw];
    if (raw.startsWith('studio_overlays/')) return [raw];

    if (raw.startsWith('overlay/')) {
      const parts = raw.split('/').filter(Boolean);
      if (parts.length < 3) return [];
      const overlayId = safeId(parts[1]);
      const rel = safeRelativePath(parts.slice(2).join('/'));
      if (!overlayId || !rel) return [];
      return [
        `/api/overlays/${encodeURIComponent(overlayId)}/${rel.split('/').map(encodeURIComponent).join('/')}`,
        `studio_overlays/${encodeURIComponent(overlayId)}/${rel.split('/').map(encodeURIComponent).join('/')}`
      ];
    }

    const overlayId = safeId(defaultOverlayId, 'thought_evolution');
    const rel = safeRelativePath(raw);
    if (!rel) return [];
    return [
      `/api/overlays/${encodeURIComponent(overlayId)}/${rel.split('/').map(encodeURIComponent).join('/')}`,
      `studio_overlays/${encodeURIComponent(overlayId)}/${rel.split('/').map(encodeURIComponent).join('/')}`
    ];
  }

  async function fetchJson(defaultOverlayId, rawPath, options = {}) {
    const candidates = pathCandidates(defaultOverlayId, rawPath);
    let lastError = null;
    for (const url of candidates) {
      try {
        const response = await fetch(url, { cache: options.cache || 'no-store' });
        if (!response.ok) throw new Error(`${response.status} ${response.statusText}`);
        return { json: await response.json(), url };
      } catch (error) {
        lastError = error;
      }
    }
    if (options.optional) return null;
    throw new Error(`${rawPath} を読み込めませんでした${lastError ? `: ${lastError.message}` : ''}`);
  }

  function ensureStyles() {
    if (document.getElementById(STYLE_ID)) return;
    const style = document.createElement('style');
    style.id = STYLE_ID;
    style.textContent = `
      .tes-backdrop{position:fixed;inset:0;z-index:10080;background:rgba(2,8,14,.78);backdrop-filter:blur(4px);padding:12px;color:#e9f2f8;font-family:Inter,"Yu Gothic UI","Meiryo",sans-serif}
      .tes-shell{height:100%;min-height:0;display:grid;grid-template-rows:auto 1fr;background:#081018;border:1px solid #355067;border-radius:14px;overflow:hidden;box-shadow:0 24px 70px rgba(0,0,0,.55)}
      .tes-header{display:flex;align-items:center;gap:12px;min-width:0;padding:10px 12px;background:linear-gradient(90deg,#0d1e2c,#18283b);border-bottom:1px solid #294258}
      .tes-brand{font-size:17px;font-weight:800;white-space:nowrap}.tes-brand-a{color:#2ee6d6}.tes-brand-b{color:#ff6bb5}
      .tes-graph-select{min-width:260px;max-width:460px;flex:1;background:#08131d;color:#edf7fc;border:1px solid #35536b;border-radius:7px;padding:7px 9px}
      .tes-badge{font-size:10px;border:1px solid #3d596f;border-radius:999px;padding:3px 7px;color:#bcd0dc;background:#0b1722;white-space:nowrap}
      .tes-badge.is-dirty{color:#ffe5a3;border-color:#8f6d25}.tes-header-spacer{flex:1}
      .tes-button{background:#162a3a;color:#dbeaf3;border:1px solid #35536b;border-radius:7px;padding:7px 9px;cursor:pointer;font-size:12px;white-space:nowrap}
      .tes-button:hover{border-color:#2ee6d6;color:#fff}.tes-button.is-primary{background:#163a45;border-color:#2d7d83}.tes-button.is-active{border-color:#ffd166;color:#fff3c2;background:#3a321b}.tes-button:disabled{opacity:.45;cursor:default}
      .tes-close{font-size:19px;line-height:1;width:34px;height:32px;padding:0}
      .tes-layout{min-height:0;display:grid;grid-template-columns:260px minmax(0,1fr) 360px}
      .tes-left,.tes-right{min-height:0;overflow:auto;background:#0f1b27;padding:13px}.tes-left{border-right:1px solid #294258}.tes-right{border-left:1px solid #294258}
      .tes-main{min-width:0;min-height:0;position:relative;background:radial-gradient(circle at 24% 22%,rgba(46,230,214,.06),transparent 30%),radial-gradient(circle at 76% 78%,rgba(255,107,181,.06),transparent 30%),#081018}
      .tes-section-title{font-size:12px;margin:5px 0 9px;color:#d9e7f0;text-transform:uppercase;letter-spacing:.08em}
      .tes-search{width:100%;padding:8px 9px;background:#08131d;color:#fff;border:1px solid #304a60;border-radius:7px;outline:none}
      .tes-filter-group{margin:14px 0}.tes-check{display:flex;align-items:center;gap:7px;margin:7px 0;font-size:12px;color:#c9d8e2}.tes-check input{accent-color:#2ee6d6}.tes-dot{width:9px;height:9px;border-radius:50%;display:inline-block;flex:0 0 auto}
      .tes-presets{display:grid;gap:5px}.tes-preset{text-align:left;width:100%}.tes-help,.tes-stats{font-size:11px;color:#8fa7b8;line-height:1.62}.tes-help{border-top:1px solid #243b4d;margin-top:14px;padding-top:11px}
      .tes-svg{width:100%;height:100%;display:block;cursor:grab;touch-action:none;user-select:none}.tes-svg.is-dragging{cursor:grabbing}
      .tes-edge{fill:none;stroke-width:1.6;opacity:.72;pointer-events:none}.tes-edge.is-dim{opacity:.08}.tes-edge.is-active{stroke:#ffd166!important;stroke-width:3;opacity:1}
      .tes-edge-hit{fill:none;stroke:transparent;stroke-width:14;pointer-events:stroke;cursor:pointer}.tes-edge-label{fill:#8ea6b7;font-size:10px;pointer-events:none;text-anchor:middle}.tes-edge-label.is-active{fill:#ffe6a0;font-weight:700}
      .tes-node{cursor:move}.tes-node .tes-shape{stroke:#dceaf2;stroke-width:1.25;filter:drop-shadow(0 2px 4px rgba(0,0,0,.58))}.tes-node text{fill:#f5fbff;font-size:11px;font-weight:700;text-anchor:middle;pointer-events:none}.tes-node .tes-node-sub{font-size:8px;fill:#a9bcc9;font-weight:500}.tes-node.is-dim{opacity:.12}.tes-node.is-active .tes-shape{stroke:#ffd166;stroke-width:3;filter:drop-shadow(0 0 8px rgba(255,209,102,.65))}.tes-node.is-neighbor .tes-shape{stroke:#fff;stroke-width:2}
      .tes-zoom-controls{position:absolute;right:12px;top:12px;display:flex;gap:5px}.tes-zoom-controls .tes-button{width:35px;height:33px;padding:0;font-size:16px;background:#0c1924dd}
      .tes-canvas-status{position:absolute;left:12px;bottom:10px;max-width:72%;background:#07111add;border:1px solid #2b4255;border-radius:8px;padding:7px 9px;font-size:10px;color:#abc0ce;display:flex;gap:10px;flex-wrap:wrap}
      .tes-tabs{display:flex;gap:6px;margin-bottom:10px;position:sticky;top:-13px;background:#0f1b27;padding:13px 0 8px;z-index:3}.tes-tab.is-active{background:#20445a;border-color:#2ee6d6;color:#fff}
      .tes-card{background:#132333;border:1px solid #29445a;border-radius:10px;padding:12px;margin-bottom:10px}.tes-card h3{font-size:15px;margin:0 0 7px;line-height:1.4}.tes-meta{font-size:10px;color:#8eabba;margin-bottom:8px;display:flex;gap:6px;flex-wrap:wrap}.tes-pill{border-radius:999px;border:1px solid #3c566d;padding:2px 6px}.tes-summary{font-size:12px;line-height:1.65;color:#d3e0e8}.tes-evidence{margin-top:9px;padding:9px;border-left:3px solid #2ee6d6;background:#0a1722;font-size:11px;line-height:1.55;color:#bcd0dc}.tes-tags{margin-top:9px;display:flex;flex-wrap:wrap;gap:5px}.tes-tag{font-size:9px;background:#1d3447;padding:3px 6px;border-radius:999px;color:#bfd1dd}.tes-empty{color:#7f97a7;font-size:12px;padding:30px 5px;text-align:center}.tes-insight{cursor:pointer;transition:.15s}.tes-insight:hover{border-color:#ff6bb5;transform:translateY(-1px)}.tes-insight-confidence{color:#ffd166;font-size:10px}.tes-hidden{display:none!important}
      .tes-loading{position:absolute;inset:0;display:grid;place-items:center;background:rgba(5,12,18,.82);z-index:5;color:#cde1ec;font-size:13px}.tes-loading.tes-hidden{display:none}
      .tes-error{border-color:#8f3c4e;background:#2b1720;color:#ffd7df}.tes-toast{position:absolute;left:50%;top:14px;transform:translateX(-50%);z-index:10;background:#102432;border:1px solid #42647a;border-radius:8px;padding:8px 12px;font-size:11px;color:#d9edf7;box-shadow:0 8px 22px rgba(0,0,0,.35)}
      @media(max-width:1050px){.tes-layout{grid-template-columns:220px minmax(0,1fr) 300px}.tes-badge{display:none}.tes-graph-select{min-width:180px}}
    `;
    document.head.appendChild(style);
  }

  function createSvgElement(name, attrs = {}) {
    const el = document.createElementNS(SVG_NS, name);
    Object.entries(attrs).forEach(([key, value]) => {
      if (value != null && value !== '') el.setAttribute(key, String(value));
    });
    return el;
  }

  function typeMap(graphDef) {
    return Object.fromEntries(normalizeArray(graphDef?.node_types).map(item => [text(item?.id), item]));
  }

  function edgeTypeMap(graphDef) {
    return Object.fromEntries(normalizeArray(graphDef?.edge_types).map(item => [text(item?.id), item]));
  }

  function fieldValues(nodes, field) {
    const values = new Set();
    nodes.forEach(node => {
      normalizeArray(node?.[field]).forEach(value => {
        const s = text(value).trim();
        if (s) values.add(s);
      });
    });
    return [...values].sort((a, b) => a.localeCompare(b, 'ja'));
  }

  function graphCanvas(graphDef) {
    return {
      width: Math.max(600, Number(graphDef?.canvas?.width) || 1600),
      height: Math.max(400, Number(graphDef?.canvas?.height) || 920),
      minScale: Math.max(0.1, Number(graphDef?.canvas?.min_scale) || 0.32),
      maxScale: Math.max(1, Number(graphDef?.canvas?.max_scale) || 3.2),
      initialScale: Math.max(0.1, Number(graphDef?.canvas?.initial_scale) || 1)
    };
  }

  function defaultPosition(index, canvas) {
    const columns = Math.max(2, Math.floor(Math.sqrt(index + 5)));
    const column = index % columns;
    const row = Math.floor(index / columns);
    return {
      x: 130 + column * Math.max(150, (canvas.width - 260) / Math.max(1, columns - 1)),
      y: 130 + row * 175
    };
  }

  function normalizeLayout(graphData, rawLayout, graphDef) {
    const canvas = graphCanvas(graphDef);
    const source = rawLayout && typeof rawLayout === 'object' ? rawLayout : {};
    const positions = source.positions && typeof source.positions === 'object' ? source.positions : {};
    const nodes = normalizeArray(graphData?.nodes).map((node, index) => {
      const fromLayout = positions[node?.id] || {};
      const fallback = defaultPosition(index, canvas);
      return {
        ...clone(node),
        x: Number.isFinite(Number(fromLayout.x)) ? Number(fromLayout.x) : fallback.x,
        y: Number.isFinite(Number(fromLayout.y)) ? Number(fromLayout.y) : fallback.y
      };
    });
    const viewport = source.viewport || {};
    return {
      nodes,
      viewport: {
        x: Number.isFinite(Number(viewport.x)) ? Number(viewport.x) : 0,
        y: Number.isFinite(Number(viewport.y)) ? Number(viewport.y) : 0,
        scale: Number.isFinite(Number(viewport.scale)) ? Number(viewport.scale) : canvas.initialScale
      }
    };
  }

  function layoutPayload(state) {
    return {
      schema_version: 'thought_graph_layout_state_v0_1',
      document_type: 'thought_graph_layout_state',
      graph_id: state.graphData?.graph_id || state.currentRow?.graph_id || '',
      updated_at: new Date().toISOString(),
      viewport: {
        x: Number(state.transform.x.toFixed(3)),
        y: Number(state.transform.y.toFixed(3)),
        scale: Number(state.transform.k.toFixed(5))
      },
      positions: Object.fromEntries(state.nodes.map(node => [node.id, {
        x: Number(node.x.toFixed(3)),
        y: Number(node.y.toFixed(3))
      }]))
    };
  }

  function localStorageKey(overlayId, row) {
    return `thought-evolution-layout:${overlayId}:${row?.graph_id || row?.layout_save_file || 'default'}`;
  }

  async function loadLayout(state, row) {
    const initialResult = await fetchJson(state.overlayId, row.layout_state_file, { optional: true });
    const initial = initialResult?.json || { graph_id: row.graph_id, viewport: {}, positions: {} };
    let saved = null;
    const saveName = safeRelativePath(row.layout_save_file || `${row.graph_id || 'graph'}.json`);
    if (saveName) {
      const sidecar = await fetchJson(state.overlayId, `sidecars/${saveName}`, { optional: true });
      saved = sidecar?.json || null;
    }
    if (!saved) {
      try {
        const raw = localStorage.getItem(localStorageKey(state.overlayId, row));
        if (raw) saved = JSON.parse(raw);
      } catch { /* ignore local cache errors */ }
    }
    if (saved?.graph_id && row.graph_id && saved.graph_id !== row.graph_id) saved = null;
    return { initial, active: saved || initial, source: saved ? 'saved' : 'initial' };
  }

  async function saveLayout(state) {
    const row = state.currentRow;
    if (!row) return;
    const payload = layoutPayload(state);
    const saveName = safeRelativePath(row.layout_save_file || `${row.graph_id || 'graph'}.json`);
    if (!saveName) throw new Error('layout_save_file が不正です');
    const apiUrl = `/api/overlays/${encodeURIComponent(state.overlayId)}/sidecars/${saveName.split('/').map(encodeURIComponent).join('/')}`;
    let apiError = null;
    try {
      const response = await fetch(apiUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      if (!response.ok) throw new Error(`${response.status} ${response.statusText}`);
      localStorage.setItem(localStorageKey(state.overlayId, row), JSON.stringify(payload));
      state.dirty = false;
      updateDirtyBadge(state);
      toast(state, 'レイアウトをOverlay sidecarへ保存しました');
      return;
    } catch (error) {
      apiError = error;
    }
    try {
      localStorage.setItem(localStorageKey(state.overlayId, row), JSON.stringify(payload));
      state.dirty = false;
      updateDirtyBadge(state);
      toast(state, `API保存不可のためブラウザへ保存しました${apiError ? ` (${apiError.message})` : ''}`);
    } catch (error) {
      throw new Error(`レイアウト保存に失敗しました: ${error.message}`);
    }
  }

  function updateDirtyBadge(state) {
    const badge = state.root?.querySelector('[data-role="dirty-badge"]');
    if (!badge) return;
    badge.textContent = state.dirty ? '● レイアウト未保存' : 'レイアウト保存済み';
    badge.classList.toggle('is-dirty', state.dirty);
  }

  function setDirty(state, value = true) {
    state.dirty = Boolean(value);
    updateDirtyBadge(state);
  }

  function toast(state, message, kind = 'info') {
    const main = state.root?.querySelector('.tes-main');
    if (!main) return;
    main.querySelector('.tes-toast')?.remove();
    const el = document.createElement('div');
    el.className = `tes-toast${kind === 'error' ? ' tes-error' : ''}`;
    el.textContent = message;
    main.appendChild(el);
    window.setTimeout(() => el.remove(), kind === 'error' ? 5200 : 2600);
  }

  function createDialog(state) {
    document.getElementById(DIALOG_ID)?.remove();
    const root = document.createElement('div');
    root.id = DIALOG_ID;
    root.className = 'tes-backdrop';
    root.innerHTML = `
      <div class="tes-shell" role="dialog" aria-modal="true" aria-label="Thought Evolution Studio">
        <header class="tes-header">
          <div class="tes-brand"><span class="tes-brand-a">Thought Evolution</span> <span class="tes-brand-b">Studio</span></div>
          <select class="tes-graph-select" data-role="graph-select" aria-label="グラフ選択"></select>
          <span class="tes-badge">v0.1 Generic Graph</span>
          <span class="tes-badge">外部ライブラリなし</span>
          <span class="tes-badge" data-role="dirty-badge">レイアウト保存済み</span>
          <div class="tes-header-spacer"></div>
          <button class="tes-button" data-action="reload">再読込</button>
          <button class="tes-button" data-action="reset-layout">初期配置</button>
          <button class="tes-button is-primary" data-action="save-layout">配置保存</button>
          <button class="tes-button tes-close" data-action="close" aria-label="閉じる">×</button>
        </header>
        <div class="tes-layout">
          <aside class="tes-left">
            <div class="tes-section-title">Search</div>
            <input class="tes-search" data-role="search" type="text" placeholder="ノード・タグを検索">
            <div data-role="filters"></div>
            <div class="tes-filter-group">
              <div class="tes-section-title">Preset Path</div>
              <div class="tes-presets" data-role="presets"></div>
            </div>
            <div class="tes-stats" data-role="stats"></div>
            <div class="tes-help" data-role="help">ノードをドラッグ。背景ドラッグで移動。ホイールでカーソル位置を中心に拡大縮小。<br><br>配置保存はOverlay sidecarへ保存し、API不可時はブラウザ内へ退避します。</div>
          </aside>
          <main class="tes-main">
            <svg class="tes-svg" data-role="svg" preserveAspectRatio="xMidYMid meet">
              <defs>
                <marker id="tes-arrow-v01" markerWidth="8" markerHeight="8" refX="7" refY="3.5" orient="auto"><polygon points="0 0, 8 3.5, 0 7" fill="#647f91"></polygon></marker>
                <marker id="tes-arrow-active-v01" markerWidth="8" markerHeight="8" refX="7" refY="3.5" orient="auto"><polygon points="0 0, 8 3.5, 0 7" fill="#ffd166"></polygon></marker>
              </defs>
              <g data-role="viewport"><g data-role="edges"></g><g data-role="edge-labels"></g><g data-role="nodes"></g></g>
            </svg>
            <div class="tes-zoom-controls">
              <button class="tes-button" data-action="zoom-in" title="拡大">＋</button>
              <button class="tes-button" data-action="zoom-out" title="縮小">−</button>
              <button class="tes-button" data-action="fit" title="全体表示">□</button>
            </div>
            <div class="tes-canvas-status" data-role="legend"></div>
            <div class="tes-loading" data-role="loading">GraphDef / GraphData / LayoutState を読み込み中...</div>
          </main>
          <section class="tes-right">
            <div class="tes-tabs"><button class="tes-button tes-tab is-active" data-tab="detail">Detail</button><button class="tes-button tes-tab" data-tab="insights">Insights</button></div>
            <div data-panel="detail"></div>
            <div class="tes-hidden" data-panel="insights"></div>
          </section>
        </div>
      </div>`;
    document.body.appendChild(root);
    state.root = root;
    state.svg = root.querySelector('[data-role="svg"]');
    state.viewport = root.querySelector('[data-role="viewport"]');
    state.edgeGroup = root.querySelector('[data-role="edges"]');
    state.edgeLabelGroup = root.querySelector('[data-role="edge-labels"]');
    state.nodeGroup = root.querySelector('[data-role="nodes"]');
    populateGraphSelect(state);
    bindShellEvents(state);
    updateDirtyBadge(state);
    return root;
  }

  function populateGraphSelect(state) {
    const select = state.root.querySelector('[data-role="graph-select"]');
    select.innerHTML = state.catalogRows.map((row, index) =>
      `<option value="${index}">${escapeHtml(row.title || row.graph_id || `Graph ${index + 1}`)}</option>`
    ).join('');
    const currentIndex = Math.max(0, state.catalogRows.indexOf(state.currentRow));
    select.value = String(currentIndex);
  }

  function showLoading(state, message = '') {
    const loading = state.root?.querySelector('[data-role="loading"]');
    if (!loading) return;
    loading.textContent = message || '読み込み中...';
    loading.classList.remove('tes-hidden');
  }

  function hideLoading(state) {
    state.root?.querySelector('[data-role="loading"]')?.classList.add('tes-hidden');
  }

  function showLoadError(state, error) {
    const loading = state.root?.querySelector('[data-role="loading"]');
    if (!loading) return;
    loading.innerHTML = `<div class="tes-card tes-error"><h3>グラフ読込エラー</h3><div class="tes-summary">${escapeHtml(error?.message || error)}</div></div>`;
    loading.classList.remove('tes-hidden');
  }

  async function loadGraph(state, row, options = {}) {
    if (!row) throw new Error('グラフ定義行がありません');
    showLoading(state, `${row.title || row.graph_id || 'Graph'} を読み込み中...`);
    state.currentRow = row;
    state.selected = null;
    state.highlightNodes = null;
    state.search = '';
    state.activePreset = 'all';
    state.root.querySelector('[data-role="search"]').value = '';
    try {
      const [defResult, dataResult, layoutResult] = await Promise.all([
        fetchJson(state.overlayId, row.graph_def_file),
        fetchJson(state.overlayId, row.graph_data_file),
        loadLayout(state, row)
      ]);
      state.graphDef = defResult.json;
      state.graphData = dataResult.json;
      state.initialLayout = clone(layoutResult.initial);
      state.layoutSource = layoutResult.source;
      const normalized = normalizeLayout(state.graphData, layoutResult.active, state.graphDef);
      state.nodes = normalized.nodes;
      state.nodeById = Object.fromEntries(state.nodes.map(node => [node.id, node]));
      state.edges = normalizeArray(state.graphData?.edges).map((edge, index) => ({ id: edge.id || `edge_${index + 1}`, ...clone(edge) }));
      state.edgeById = Object.fromEntries(state.edges.map(edge => [edge.id, edge]));
      state.transform = {
        x: normalized.viewport.x,
        y: normalized.viewport.y,
        k: normalized.viewport.scale
      };
      const canvas = graphCanvas(state.graphDef);
      state.transform.k = Math.max(canvas.minScale, Math.min(canvas.maxScale, state.transform.k));
      state.filterSelections = {};
      buildFilters(state);
      buildPresets(state);
      renderInsights(state);
      switchTab(state, 'detail');
      renderEmptyDetail(state);
      applyTransform(state);
      renderGraph(state);
      setDirty(state, false);
      const select = state.root.querySelector('[data-role="graph-select"]');
      select.value = String(Math.max(0, state.catalogRows.indexOf(row)));
      hideLoading(state);
      if (!options.silent) toast(state, `読込完了: ${state.graphData.title || row.title || row.graph_id}`);
    } catch (error) {
      showLoadError(state, error);
      throw error;
    }
  }

  function buildFilters(state) {
    const wrap = state.root.querySelector('[data-role="filters"]');
    const nodeTypes = typeMap(state.graphDef);
    const usedTypes = [...new Set(state.nodes.map(node => text(node.type)).filter(Boolean))];
    state.typeSelection = new Set(usedTypes);

    const typeHtml = usedTypes.map(typeId => {
      const def = nodeTypes[typeId] || {};
      return `<label class="tes-check"><input type="checkbox" data-filter-kind="type" value="${escapeHtml(typeId)}" checked><span class="tes-dot" style="background:${escapeHtml(def.color || '#8fa7b8')}"></span>${escapeHtml(def.label || typeId)}</label>`;
    }).join('');

    const customHtml = normalizeArray(state.graphDef?.filters).map(filter => {
      const field = text(filter?.field).trim();
      if (!field) return '';
      const values = fieldValues(state.nodes, field);
      state.filterSelections[field] = new Set(values);
      return `<div class="tes-filter-group"><div class="tes-section-title">${escapeHtml(filter.caption || field)}</div>${values.map(value =>
        `<label class="tes-check"><input type="checkbox" data-filter-kind="field" data-filter-field="${escapeHtml(field)}" value="${escapeHtml(value)}" checked>${escapeHtml(value)}</label>`
      ).join('')}</div>`;
    }).join('');

    wrap.innerHTML = `<div class="tes-filter-group"><div class="tes-section-title">Node Type</div>${typeHtml}</div>${customHtml}`;
    wrap.querySelectorAll('input[type="checkbox"]').forEach(input => {
      input.addEventListener('change', () => {
        const kind = input.dataset.filterKind;
        if (kind === 'type') {
          if (input.checked) state.typeSelection.add(input.value); else state.typeSelection.delete(input.value);
        } else {
          const field = input.dataset.filterField;
          const set = state.filterSelections[field] || new Set();
          if (input.checked) set.add(input.value); else set.delete(input.value);
          state.filterSelections[field] = set;
        }
        state.selected = null;
        renderEmptyDetail(state);
        renderGraph(state);
      });
    });
  }

  function buildPresets(state) {
    const wrap = state.root.querySelector('[data-role="presets"]');
    const presets = normalizeArray(state.graphData?.presets);
    const list = presets.length ? presets : [{ id: 'all', label: '全体表示', match: { all: true } }];
    if (!list.some(item => item.id === 'all')) list.unshift({ id: 'all', label: '全体表示', match: { all: true } });
    state.presets = list;
    wrap.innerHTML = list.map(item => `<button class="tes-button tes-preset${item.id === state.activePreset ? ' is-active' : ''}" data-preset="${escapeHtml(item.id)}">${escapeHtml(item.label || item.id)}</button>`).join('');
    wrap.querySelectorAll('[data-preset]').forEach(button => {
      button.addEventListener('click', () => {
        state.activePreset = button.dataset.preset || 'all';
        state.selected = null;
        state.highlightNodes = null;
        wrap.querySelectorAll('[data-preset]').forEach(x => x.classList.toggle('is-active', x === button));
        renderEmptyDetail(state);
        renderGraph(state);
      });
    });
  }

  function matchPreset(node, state) {
    const preset = normalizeArray(state.presets).find(item => item.id === state.activePreset);
    const match = preset?.match || {};
    if (!preset || match.all === true || state.activePreset === 'all') return true;
    const checks = [];
    if (Array.isArray(match.node_ids)) checks.push(match.node_ids.includes(node.id));
    if (Array.isArray(match.clusters)) checks.push(match.clusters.includes(node.cluster));
    if (Array.isArray(match.types)) checks.push(match.types.includes(node.type));
    if (Array.isArray(match.tags_any)) checks.push(normalizeArray(node.tags).some(tag => match.tags_any.includes(tag)));
    return checks.length ? checks.some(Boolean) : true;
  }

  function nodeVisible(node, state) {
    if (!state.typeSelection?.has(text(node.type))) return false;
    for (const [field, selected] of Object.entries(state.filterSelections || {})) {
      const values = normalizeArray(node?.[field]).map(text);
      if (!values.some(value => selected.has(value))) return false;
    }
    if (!matchPreset(node, state)) return false;
    const query = text(state.search).trim().toLowerCase();
    if (!query) return true;
    const fields = normalizeArray(state.graphDef?.search_fields);
    const haystack = fields.flatMap(field => normalizeArray(node?.[field])).map(text).join(' ').toLowerCase();
    return haystack.includes(query);
  }

  function nodeRadius(node, state) {
    const def = typeMap(state.graphDef)[node.type] || {};
    return Math.max(18, Number(def.radius) || 27);
  }

  function edgeBoundaryRadius(node, state) {
    const def = typeMap(state.graphDef)[node.type] || {};
    const radius = nodeRadius(node, state);
    return def.shape === 'rounded_rect' ? radius * 1.38 : radius * 1.08;
  }

  function shapeElement(node, state) {
    const def = typeMap(state.graphDef)[node.type] || {};
    const radius = nodeRadius(node, state);
    const shape = text(def.shape || 'circle');
    const common = { class: 'tes-shape', fill: def.color || '#7790a2' };
    if (shape === 'rounded_rect') {
      return createSvgElement('rect', { ...common, x: -radius * 1.38, y: -radius * .82, width: radius * 2.76, height: radius * 1.64, rx: Math.max(8, radius * .34) });
    }
    if (shape === 'diamond') {
      return createSvgElement('polygon', { ...common, points: `0,${-radius} ${radius * 1.12},0 0,${radius} ${-radius * 1.12},0` });
    }
    if (shape === 'hexagon') {
      const r = radius * 1.06;
      const points = [0,1,2,3,4,5].map(i => {
        const angle = Math.PI / 3 * i - Math.PI / 2;
        return `${Math.cos(angle) * r},${Math.sin(angle) * r}`;
      }).join(' ');
      return createSvgElement('polygon', { ...common, points });
    }
    return createSvgElement('circle', { ...common, r: radius });
  }

  function wrapLabel(value, maxChars = 10) {
    const s = text(value);
    if (s.length <= maxChars) return [s];
    const result = [];
    for (let i = 0; i < s.length; i += maxChars) result.push(s.slice(i, i + maxChars));
    return result.slice(0, 3);
  }

  function selectionContext(state) {
    const selected = state.selected;
    const activeNodes = new Set();
    const activeEdges = new Set();
    if (!selected) return { activeNodes, activeEdges };
    if (selected.kind === 'node') {
      activeNodes.add(selected.id);
      state.edges.forEach(edge => {
        if (edge.source === selected.id || edge.target === selected.id) {
          activeEdges.add(edge.id);
          activeNodes.add(edge.source);
          activeNodes.add(edge.target);
        }
      });
    } else if (selected.kind === 'edge') {
      const edge = state.edgeById[selected.id];
      if (edge) {
        activeEdges.add(edge.id);
        activeNodes.add(edge.source);
        activeNodes.add(edge.target);
      }
    }
    return { activeNodes, activeEdges };
  }

  function renderGraph(state) {
    if (!state.graphDef || !state.graphData) return;
    const canvas = graphCanvas(state.graphDef);
    state.svg.setAttribute('viewBox', `0 0 ${canvas.width} ${canvas.height}`);
    state.edgeGroup.innerHTML = '';
    state.edgeLabelGroup.innerHTML = '';
    state.nodeGroup.innerHTML = '';

    const visibleNodes = state.nodes.filter(node => nodeVisible(node, state));
    const visibleIds = new Set(visibleNodes.map(node => node.id));
    const visibleEdges = state.edges.filter(edge => visibleIds.has(edge.source) && visibleIds.has(edge.target));
    const { activeNodes, activeEdges } = selectionContext(state);
    const highlight = state.highlightNodes;
    const edgeTypes = edgeTypeMap(state.graphDef);

    visibleEdges.forEach(edge => {
      const source = state.nodeById[edge.source];
      const target = state.nodeById[edge.target];
      if (!source || !target) return;
      const dx = target.x - source.x;
      const dy = target.y - source.y;
      const length = Math.hypot(dx, dy) || 1;
      const startR = edgeBoundaryRadius(source, state) + 4;
      const endR = edgeBoundaryRadius(target, state) + 10;
      const x1 = source.x + dx / length * startR;
      const y1 = source.y + dy / length * startR;
      const x2 = target.x - dx / length * endR;
      const y2 = target.y - dy / length * endR;
      const edgeDef = edgeTypes[edge.type] || {};
      const isActive = activeEdges.has(edge.id);
      const isDim = Boolean(state.selected) && !isActive;
      const line = createSvgElement('line', {
        x1, y1, x2, y2,
        class: `tes-edge${isActive ? ' is-active' : ''}${isDim ? ' is-dim' : ''}`,
        stroke: edgeDef.stroke || '#526b7d',
        'stroke-dasharray': edgeDef.dasharray || '',
        'marker-end': isActive ? 'url(#tes-arrow-active-v01)' : 'url(#tes-arrow-v01)'
      });
      state.edgeGroup.appendChild(line);

      const hit = createSvgElement('line', { x1, y1, x2, y2, class: 'tes-edge-hit' });
      hit.dataset.edgeId = edge.id;
      hit.addEventListener('pointerdown', event => event.stopPropagation());
      hit.addEventListener('click', event => {
        event.stopPropagation();
        selectEdge(state, edge.id);
      });
      state.edgeGroup.appendChild(hit);

      if (isActive || state.selected?.kind === 'edge') {
        const label = createSvgElement('text', {
          x: (x1 + x2) / 2,
          y: (y1 + y2) / 2 - 7,
          class: `tes-edge-label${isActive ? ' is-active' : ''}`
        });
        label.textContent = edge.label || edgeDef.label || edge.type || '';
        state.edgeLabelGroup.appendChild(label);
      }
    });

    visibleNodes.forEach(node => {
      const group = createSvgElement('g', { transform: `translate(${node.x} ${node.y})`, class: 'tes-node' });
      group.dataset.nodeId = node.id;
      const selectedNode = state.selected?.kind === 'node' && state.selected.id === node.id;
      const activeNode = activeNodes.has(node.id);
      const highlighted = highlight instanceof Set ? highlight.has(node.id) : false;
      const shouldDim = (Boolean(state.selected) && !activeNode) || (highlight instanceof Set && !highlighted);
      group.classList.toggle('is-active', selectedNode || highlighted);
      group.classList.toggle('is-neighbor', !selectedNode && activeNode);
      group.classList.toggle('is-dim', shouldDim);
      group.appendChild(shapeElement(node, state));

      const typeDef = typeMap(state.graphDef)[node.type] || {};
      const lines = wrapLabel(node.label || node.id, Number(typeDef.label_max_chars) || 10);
      lines.forEach((lineText, index) => {
        const label = createSvgElement('text', { y: (index - (lines.length - 1) / 2) * 12 + 3 });
        label.textContent = lineText;
        group.appendChild(label);
      });
      const sub = createSvgElement('text', { class: 'tes-node-sub', y: nodeRadius(node, state) + 16 });
      sub.textContent = node.cluster || typeDef.label || node.type || '';
      group.appendChild(sub);

      group.addEventListener('pointerdown', event => startNodeDrag(state, event, node));
      state.nodeGroup.appendChild(group);
    });

    renderLegendAndStats(state, visibleNodes, visibleEdges);
    applyTransform(state);
  }

  function renderLegendAndStats(state, visibleNodes, visibleEdges) {
    const typeDefs = typeMap(state.graphDef);
    const used = [...new Set(visibleNodes.map(node => node.type))];
    state.root.querySelector('[data-role="legend"]').innerHTML = used.map(typeId => {
      const def = typeDefs[typeId] || {};
      return `<span><span class="tes-dot" style="background:${escapeHtml(def.color || '#8fa7b8')}"></span> ${escapeHtml(def.label || typeId)}</span>`;
    }).join('');
    state.root.querySelector('[data-role="stats"]').innerHTML = `表示ノード：<b>${visibleNodes.length}</b> / ${state.nodes.length}<br>表示リレーション：<b>${visibleEdges.length}</b> / ${state.edges.length}<br>Layout：<b>${escapeHtml(state.layoutSource || 'initial')}</b>`;
  }

  function renderEmptyDetail(state) {
    const panel = state.root.querySelector('[data-panel="detail"]');
    const empty = state.graphDef?.labels?.empty || 'グラフのノードまたはリレーションを選択してください。';
    panel.innerHTML = `<div class="tes-empty">${escapeHtml(empty)}</div>`;
  }

  function selectNode(state, nodeId) {
    state.selected = { kind: 'node', id: nodeId };
    state.highlightNodes = null;
    const node = state.nodeById[nodeId];
    if (!node) return;
    const typeDef = typeMap(state.graphDef)[node.type] || {};
    const relations = state.edges.filter(edge => edge.source === nodeId || edge.target === nodeId);
    const relationHtml = relations.map(edge => {
      const otherId = edge.source === nodeId ? edge.target : edge.source;
      const other = state.nodeById[otherId];
      const arrow = edge.source === nodeId ? '→' : '←';
      return `<div class="tes-summary" style="margin:8px 0"><b>${arrow} ${escapeHtml(other?.label || otherId)}</b><br><span style="color:#8fa7b8">${escapeHtml(edge.label || edge.type || '')}</span></div>`;
    }).join('') || '<div class="tes-summary">なし</div>';
    const evidence = normalizeArray(node.evidence);
    const tags = normalizeArray(node.tags);
    const panel = state.root.querySelector('[data-panel="detail"]');
    panel.innerHTML = `
      <div class="tes-card"><h3>${escapeHtml(node.label || node.id)}</h3>
        <div class="tes-meta"><span class="tes-pill">${escapeHtml(typeDef.label || node.type || '')}</span><span class="tes-pill">${escapeHtml(node.cluster || '')}</span><span class="tes-pill">${escapeHtml(node.source || '')}</span></div>
        <div class="tes-summary">${escapeHtml(node.summary || '')}</div>
        ${evidence.length ? `<div class="tes-evidence"><b>根拠メモ</b><br>${evidence.map(escapeHtml).join('<br>')}</div>` : ''}
        ${tags.length ? `<div class="tes-tags">${tags.map(tag => `<span class="tes-tag">${escapeHtml(tag)}</span>`).join('')}</div>` : ''}
      </div>
      <div class="tes-card"><h3>直接リレーション</h3>${relationHtml}</div>`;
    switchTab(state, 'detail');
    renderGraph(state);
  }

  function selectEdge(state, edgeId) {
    state.selected = { kind: 'edge', id: edgeId };
    state.highlightNodes = null;
    const edge = state.edgeById[edgeId];
    if (!edge) return;
    const source = state.nodeById[edge.source];
    const target = state.nodeById[edge.target];
    const edgeDef = edgeTypeMap(state.graphDef)[edge.type] || {};
    const panel = state.root.querySelector('[data-panel="detail"]');
    panel.innerHTML = `
      <div class="tes-card"><h3>${escapeHtml(edge.label || edgeDef.label || edge.type || edge.id)}</h3>
        <div class="tes-meta"><span class="tes-pill">${escapeHtml(edgeDef.label || edge.type || '')}</span><span class="tes-pill">${escapeHtml(edge.id || '')}</span></div>
        <div class="tes-summary"><b>${escapeHtml(source?.label || edge.source)}</b><br>↓<br><b>${escapeHtml(target?.label || edge.target)}</b></div>
        ${edge.summary ? `<div class="tes-evidence">${escapeHtml(edge.summary)}</div>` : ''}
      </div>`;
    switchTab(state, 'detail');
    renderGraph(state);
  }

  function renderInsights(state) {
    const panel = state.root.querySelector('[data-panel="insights"]');
    const insights = normalizeArray(state.graphData?.insights);
    if (!insights.length) {
      panel.innerHTML = '<div class="tes-empty">InsightはこのGraphDataに定義されていません。</div>';
      return;
    }
    panel.innerHTML = insights.map((item, index) => `
      <div class="tes-card tes-insight" data-insight-index="${index}">
        <div class="tes-insight-confidence">信頼度：${escapeHtml(item.confidence || '')}</div>
        <h3>${escapeHtml(item.title || `Insight ${index + 1}`)}</h3>
        <div class="tes-summary">${escapeHtml(item.body || '')}</div>
      </div>`).join('');
    panel.querySelectorAll('[data-insight-index]').forEach(card => {
      card.addEventListener('click', () => {
        const item = insights[Number(card.dataset.insightIndex)];
        state.selected = null;
        state.highlightNodes = new Set(normalizeArray(item?.node_ids || item?.nodes));
        renderGraph(state);
      });
    });
  }

  function switchTab(state, tab) {
    state.root.querySelectorAll('[data-tab]').forEach(button => button.classList.toggle('is-active', button.dataset.tab === tab));
    state.root.querySelector('[data-panel="detail"]').classList.toggle('tes-hidden', tab !== 'detail');
    state.root.querySelector('[data-panel="insights"]').classList.toggle('tes-hidden', tab !== 'insights');
  }

  function svgPoint(state, clientX, clientY) {
    const point = state.svg.createSVGPoint();
    point.x = clientX;
    point.y = clientY;
    const matrix = state.svg.getScreenCTM();
    return matrix ? point.matrixTransform(matrix.inverse()) : point;
  }

  function graphPoint(state, clientX, clientY) {
    const point = svgPoint(state, clientX, clientY);
    return {
      x: (point.x - state.transform.x) / state.transform.k,
      y: (point.y - state.transform.y) / state.transform.k
    };
  }

  function applyTransform(state) {
    state.viewport?.setAttribute('transform', `translate(${state.transform.x} ${state.transform.y}) scale(${state.transform.k})`);
  }

  function zoomAt(state, factor, clientX, clientY) {
    const canvas = graphCanvas(state.graphDef);
    const cursor = svgPoint(state, clientX, clientY);
    const graphX = (cursor.x - state.transform.x) / state.transform.k;
    const graphY = (cursor.y - state.transform.y) / state.transform.k;
    const next = Math.max(canvas.minScale, Math.min(canvas.maxScale, state.transform.k * factor));
    state.transform.x = cursor.x - graphX * next;
    state.transform.y = cursor.y - graphY * next;
    state.transform.k = next;
    applyTransform(state);
    setDirty(state);
  }

  function fitGraph(state) {
    const visible = state.nodes.filter(node => nodeVisible(node, state));
    if (!visible.length) return;
    const canvas = graphCanvas(state.graphDef);
    const minX = Math.min(...visible.map(node => node.x)) - 80;
    const maxX = Math.max(...visible.map(node => node.x)) + 80;
    const minY = Math.min(...visible.map(node => node.y)) - 80;
    const maxY = Math.max(...visible.map(node => node.y)) + 80;
    const width = Math.max(100, maxX - minX);
    const height = Math.max(100, maxY - minY);
    const scale = Math.max(canvas.minScale, Math.min(canvas.maxScale, Math.min(canvas.width / width, canvas.height / height) * .9));
    state.transform.k = scale;
    state.transform.x = (canvas.width - (minX + maxX) * scale) / 2;
    state.transform.y = (canvas.height - (minY + maxY) * scale) / 2;
    applyTransform(state);
    setDirty(state);
  }

  function startNodeDrag(state, event, node) {
    event.preventDefault();
    event.stopPropagation();
    state.svg.setPointerCapture?.(event.pointerId);
    const point = graphPoint(state, event.clientX, event.clientY);
    state.drag = {
      kind: 'node', pointerId: event.pointerId, nodeId: node.id,
      offsetX: point.x - node.x, offsetY: point.y - node.y,
      startClientX: event.clientX, startClientY: event.clientY, moved: false
    };
    state.svg.classList.add('is-dragging');
  }

  function bindShellEvents(state) {
    const root = state.root;
    root.querySelector('[data-action="close"]').addEventListener('click', () => root.remove());
    root.querySelector('[data-role="graph-select"]').addEventListener('change', async event => {
      const row = state.catalogRows[Number(event.target.value)] || state.catalogRows[0];
      try { await loadGraph(state, row); } catch (error) { console.error(error); }
    });
    root.querySelector('[data-role="search"]').addEventListener('input', event => {
      state.search = event.target.value || '';
      state.selected = null;
      state.highlightNodes = null;
      renderEmptyDetail(state);
      renderGraph(state);
    });
    root.querySelector('[data-action="reload"]').addEventListener('click', async () => {
      try { await loadGraph(state, state.currentRow); } catch (error) { console.error(error); }
    });
    root.querySelector('[data-action="reset-layout"]').addEventListener('click', () => {
      const normalized = normalizeLayout(state.graphData, state.initialLayout, state.graphDef);
      state.nodes = normalized.nodes;
      state.nodeById = Object.fromEntries(state.nodes.map(node => [node.id, node]));
      state.transform = { x: normalized.viewport.x, y: normalized.viewport.y, k: normalized.viewport.scale };
      state.layoutSource = 'initial';
      setDirty(state);
      renderGraph(state);
      toast(state, '初期配置へ戻しました。保存するまではSidecarへ反映されません。');
    });
    root.querySelector('[data-action="save-layout"]').addEventListener('click', async event => {
      try {
        event.currentTarget.disabled = true;
        await saveLayout(state);
      } catch (error) {
        console.error(error);
        toast(state, error.message, 'error');
      } finally {
        event.currentTarget.disabled = false;
      }
    });
    root.querySelector('[data-action="zoom-in"]').addEventListener('click', () => {
      const rect = state.svg.getBoundingClientRect();
      zoomAt(state, 1.2, rect.left + rect.width / 2, rect.top + rect.height / 2);
    });
    root.querySelector('[data-action="zoom-out"]').addEventListener('click', () => {
      const rect = state.svg.getBoundingClientRect();
      zoomAt(state, 1 / 1.2, rect.left + rect.width / 2, rect.top + rect.height / 2);
    });
    root.querySelector('[data-action="fit"]').addEventListener('click', () => fitGraph(state));
    root.querySelectorAll('[data-tab]').forEach(button => button.addEventListener('click', () => switchTab(state, button.dataset.tab)));

    state.svg.addEventListener('pointerdown', event => {
      if (event.target.closest?.('.tes-node') || event.target.closest?.('.tes-edge-hit')) return;
      event.preventDefault();
      state.svg.setPointerCapture?.(event.pointerId);
      const point = svgPoint(state, event.clientX, event.clientY);
      state.drag = {
        kind: 'pan', pointerId: event.pointerId,
        startX: point.x, startY: point.y,
        originX: state.transform.x, originY: state.transform.y,
        startClientX: event.clientX, startClientY: event.clientY, moved: false
      };
      state.svg.classList.add('is-dragging');
    });

    state.svg.addEventListener('pointermove', event => {
      const drag = state.drag;
      if (!drag || drag.pointerId !== event.pointerId) return;
      const distance = Math.hypot(event.clientX - drag.startClientX, event.clientY - drag.startClientY);
      if (distance > 3) drag.moved = true;
      if (drag.kind === 'node') {
        const point = graphPoint(state, event.clientX, event.clientY);
        const node = state.nodeById[drag.nodeId];
        if (!node) return;
        node.x = point.x - drag.offsetX;
        node.y = point.y - drag.offsetY;
        setDirty(state);
        renderGraph(state);
      } else {
        const point = svgPoint(state, event.clientX, event.clientY);
        state.transform.x = drag.originX + point.x - drag.startX;
        state.transform.y = drag.originY + point.y - drag.startY;
        applyTransform(state);
        setDirty(state);
      }
    });

    const finishPointer = event => {
      const drag = state.drag;
      if (!drag || drag.pointerId !== event.pointerId) return;
      if (drag.kind === 'node' && !drag.moved) selectNode(state, drag.nodeId);
      if (drag.kind === 'pan' && !drag.moved) {
        state.selected = null;
        state.highlightNodes = null;
        renderEmptyDetail(state);
        renderGraph(state);
      }
      state.drag = null;
      state.svg.classList.remove('is-dragging');
      try { state.svg.releasePointerCapture?.(event.pointerId); } catch { /* ignore */ }
    };
    state.svg.addEventListener('pointerup', finishPointer);
    state.svg.addEventListener('pointercancel', finishPointer);
    state.svg.addEventListener('wheel', event => {
      event.preventDefault();
      zoomAt(state, event.deltaY < 0 ? 1.12 : 0.89, event.clientX, event.clientY);
    }, { passive: false });

    root.addEventListener('keydown', event => {
      if (event.key === 'Escape') root.remove();
    });
    root.tabIndex = -1;
    root.focus();
  }

  function catalogRowsFromContext(studio, context) {
    const source = context?.sourceData || context?.getSourceData?.() || studio.getSourceData?.() || {};
    return normalizeArray(source?.graphs).filter(row => row && row.status !== 'disabled');
  }

  function selectedRowFromContext(studio, context, rows) {
    const selected = context?.selectedRow || context?.getSelectedRow?.() || studio.getSelectedRow?.();
    if (selected && rows.includes(selected)) return selected;
    if (selected?.graph_id) return rows.find(row => row.graph_id === selected.graph_id) || selected;
    return rows[0] || null;
  }

  async function openStudio(studio, context = {}) {
    ensureStyles();
    const catalogRows = catalogRowsFromContext(studio, context);
    if (!catalogRows.length) throw new Error('現在のDataに graphs[] がありません。Graph Catalog Dataを開いてください。');
    const currentRow = selectedRowFromContext(studio, context, catalogRows);
    const overlayId = safeId(studio.plugin?.overlayId || context?.overlayId || 'thought_evolution', 'thought_evolution');
    const state = {
      studio, context, overlayId, catalogRows, currentRow,
      graphDef: null, graphData: null, nodes: [], edges: [], nodeById: {}, edgeById: {},
      initialLayout: null, transform: { x: 0, y: 0, k: 1 },
      filterSelections: {}, typeSelection: new Set(), presets: [], activePreset: 'all',
      search: '', selected: null, highlightNodes: null, drag: null, dirty: false
    };
    createDialog(state);
    await loadGraph(state, currentRow, { silent: true });
    window.ThoughtEvolutionStudioV01 = { state, reload: () => loadGraph(state, state.currentRow), saveLayout: () => saveLayout(state) };
    return state;
  }

  const plugin = {
    id: PLUGIN_ID,
    activate(studio) {
      studio.registerAction(ACTION_ID, async context => {
        const state = await openStudio(studio, context);
        return {
          message: `Thought Evolution Studioを開きました: ${state.graphData?.title || state.currentRow?.title || ''}`,
          statusOptions: { kind: 'success', title: 'Thought Evolution Studio' }
        };
      }, ['OpenThoughtEvolutionStudio', 'OpenThoughtGraph']);
    }
  };

  window.StudioOverlayPlugins = window.StudioOverlayPlugins || {};
  window.StudioOverlayPlugins[PLUGIN_ID] = plugin;
})();
