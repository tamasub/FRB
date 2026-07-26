// v0.18.34-related-grid-inline-view-id
// ViewDef-driven related Root Grid launcher.
// The Runtime does not know domain field names such as governance_items.
// A parent Studio owns the whole Data JSON; a child grid_only Studio edits one declared array
// and returns only that array to the parent via postMessage.

const RELATED_GRID_MESSAGE_NS = 'frb-studio-related-grid-v0.18.28';
const relatedGridParentSessions = new Map();
let relatedGridChildRuntime = null;
let relatedGridChildInitResolve = null;
let relatedGridChildInitReject = null;
let relatedGridChildReadyTimer = null;
let relatedGridChildCloseApproved = false;

function relatedGridQueryParams() {
  try { return new URLSearchParams(location.search); }
  catch { return new URLSearchParams(); }
}

function isRelatedGridLaunchQuery(params=relatedGridQueryParams()) {
  const raw = String(params.get('relatedGrid') ?? params.get('related_grid') ?? '').trim().toLowerCase();
  return ['1', 'true', 'yes', 'on'].includes(raw);
}

function relatedGridTargetOrigin() {
  return location.origin && location.origin !== 'null' ? location.origin : '*';
}

function relatedGridMessageOriginAllowed(event) {
  if (!event) return false;
  if (!location.origin || location.origin === 'null') return true;
  return event.origin === location.origin;
}

function stableRelatedGridJson(value) {
  try { return JSON.stringify(value); }
  catch { return ''; }
}

function relatedGridToolbarDef() {
  const mv = typeof mainView === 'function' ? mainView() : (viewDef?.views?.[0] ?? viewDef ?? {});
  return mv?.toolbar ?? viewDef?.toolbar ?? {};
}

function relatedGridRawDefinitions() {
  const mv = typeof mainView === 'function' ? mainView() : (viewDef?.views?.[0] ?? viewDef ?? {});
  const toolbar = relatedGridToolbarDef();
  const raw =
    toolbar?.relatedGridViews ?? toolbar?.related_grid_views ??
    mv?.relatedGridViews ?? mv?.related_grid_views ??
    viewDef?.relatedGridViews ?? viewDef?.related_grid_views ?? [];
  return Array.isArray(raw) ? raw : [];
}

function normalizeRelatedGridDefinition(raw, index=0) {
  if (!raw || typeof raw !== 'object') return null;
  const dataPath = String(raw.dataPath ?? raw.data_path ?? raw.path ?? '').trim();
  const viewDefPath = String(raw.viewDef ?? raw.view_def ?? raw.view ?? '').trim();
  const viewId = String(raw.viewId ?? raw.view_id ?? '').trim();
  if (!dataPath || (!viewDefPath && !viewId) || raw.visible === false) return null;
  const id = String(raw.id ?? raw.key ?? `related_grid_${index + 1}`).trim() || `related_grid_${index + 1}`;
  return {
    ...raw,
    id,
    caption: String(raw.caption ?? raw.label ?? id).trim() || id,
    dataPath,
    viewDef: viewDefPath,
    viewId,
    action: String(raw.action ?? raw.actionId ?? raw.action_id ?? 'OpenRelatedGridView').trim() || 'OpenRelatedGridView',
    launchMode: String(raw.launchMode ?? raw.launch_mode ?? 'new_window').trim() || 'new_window',
    shellMode: String(raw.shellMode ?? raw.shell_mode ?? 'grid_only').trim() || 'grid_only',
    windowFeatures: String(raw.windowFeatures ?? raw.window_features ?? 'popup=yes,width=1600,height=920,resizable=yes,scrollbars=yes').trim()
  };
}

function relatedGridDefinitions() {
  return relatedGridRawDefinitions().map(normalizeRelatedGridDefinition).filter(Boolean);
}

function relatedGridArrayFor(definition, data=sourceData) {
  if (!definition || !data) return null;
  const value = getByPath(data, definition.dataPath);
  return Array.isArray(value) ? value : null;
}

function normalizeRelatedGridViewStaticPath(raw) {
  let value = String(raw ?? '').trim().replace(/\\/g, '/').replace(/^\/+/, '');
  if (!value) return '';
  if (!value.startsWith('defs/')) value = `defs/${value}`;
  return value;
}

function relatedGridChannelId() {
  if (globalThis.crypto?.randomUUID) return globalThis.crypto.randomUUID();
  return `rg_${Date.now()}_${Math.random().toString(36).slice(2, 10)}`;
}

function relatedGridLaunchUrl(definition, channel, hostMode='window') {
  const url = new URL(location.href);
  url.search = '';
  url.hash = '';
  url.searchParams.set('relatedGrid', '1');
  url.searchParams.set('relatedGridChannel', channel);
  if (definition.viewDef) {
    url.searchParams.set('view', normalizeRelatedGridViewStaticPath(definition.viewDef));
  } else if (lastLoadedDefName) {
    url.searchParams.set('view', normalizeRelatedGridViewStaticPath(lastLoadedDefName));
  }
  if (definition.viewId) url.searchParams.set('relatedGridViewId', definition.viewId);
  url.searchParams.set('shell', definition.shellMode || 'grid_only');
  url.searchParams.set('relatedGridId', definition.id);
  url.searchParams.set('relatedGridHost', hostMode);
  return url.toString();
}

function relatedGridParentWindow(params=relatedGridQueryParams()) {
  const hostMode = String(params.get('relatedGridHost') ?? '').trim().toLowerCase();
  if (hostMode === 'modal' && window.parent && window.parent !== window) return window.parent;
  if (window.opener && !window.opener.closed) return window.opener;
  if (window.parent && window.parent !== window) return window.parent;
  return null;
}

function createRelatedGridParentSession(definition, channel, child, extra={}) {
  const rows = relatedGridArrayFor(definition);
  const session = {
    channel,
    child,
    definition,
    sourceDataRef: sourceData,
    sourceDataSnapshot: cloneData(sourceData),
    parentDataDisplayPath: String(currentLoadedDataDisplayPath || currentDataApiUrl || ''),
    parentDataTitle: String(currentLoadedDataTitle || ''),
    parentViewDefName: String(lastLoadedDefName || ''),
    sourceViewDef: cloneData(viewDef),
    baseline: stableRelatedGridJson(rows),
    openedAt: Date.now(),
    ...extra
  };
  relatedGridParentSessions.set(channel, session);
  return session;
}

function approveRelatedGridChildClose() {
  relatedGridChildCloseApproved = true;
}

function relatedGridModalIsDirty(session) {
  try {
    return Boolean(session?.child?.relatedGridChildIsDirty?.());
  } catch {
    return false;
  }
}

function closeRelatedGridModal(channel, options={}) {
  const session = relatedGridParentSessions.get(channel);
  if (!session?.modalOverlay) return false;
  if (!options.force && relatedGridModalIsDirty(session)) {
    const ok = window.confirm('親画面へ未反映の変更があります。閉じると変更は失われます。閉じますか？');
    if (!ok) return false;
  }
  try { session.child?.approveRelatedGridChildClose?.(); } catch {}
  session.modalOverlay.remove();
  relatedGridParentSessions.delete(channel);
  if (!document.querySelector('.related-grid-modal-overlay')) {
    document.body.classList.remove('related-grid-modal-open');
  }
  return true;
}

function openRelatedGridModal(definition) {
  const rows = relatedGridArrayFor(definition);
  if (!rows) throw new Error(`別Grid対象がArrayではありません: ${definition.dataPath}`);

  const channel = relatedGridChannelId();
  const overlay = document.createElement('div');
  overlay.className = 'related-grid-modal-overlay';
  overlay.dataset.relatedGridChannel = channel;

  const panel = document.createElement('section');
  panel.className = 'related-grid-modal-panel';
  panel.setAttribute('role', 'dialog');
  panel.setAttribute('aria-modal', 'true');
  panel.setAttribute('aria-label', definition.caption);
  panel.tabIndex = -1;

  const header = document.createElement('header');
  header.className = 'related-grid-modal-header';
  const title = document.createElement('strong');
  title.textContent = definition.caption;
  const closeButton = document.createElement('button');
  closeButton.type = 'button';
  closeButton.className = 'icon-button related-grid-modal-close';
  closeButton.setAttribute('aria-label', '閉じる');
  closeButton.title = '閉じる';
  closeButton.textContent = '×';
  header.append(title, closeButton);

  const body = document.createElement('div');
  body.className = 'related-grid-modal-body';
  const iframe = document.createElement('iframe');
  iframe.className = 'related-grid-modal-frame';
  iframe.title = definition.caption;
  body.appendChild(iframe);
  panel.append(header, body);
  overlay.appendChild(panel);
  document.body.appendChild(overlay);
  document.body.classList.add('related-grid-modal-open');

  const child = iframe.contentWindow;
  createRelatedGridParentSession(definition, channel, child, {
    modalOverlay: overlay,
    modalFrame: iframe,
    modal: true
  });

  closeButton.addEventListener('click', () => closeRelatedGridModal(channel));
  iframe.src = relatedGridLaunchUrl(definition, channel, 'modal');
  closeButton.focus();
  return iframe;
}

function openRelatedGridWindow(definition) {
  const rows = relatedGridArrayFor(definition);
  if (!rows) throw new Error(`別Grid対象がArrayではありません: ${definition.dataPath}`);
  const channel = relatedGridChannelId();
  const url = relatedGridLaunchUrl(definition, channel, 'window');
  const child = window.open(url, `frb_related_grid_${definition.id}_${channel}`, definition.windowFeatures || undefined);
  if (!child) throw new Error('別Grid画面を開けませんでした。ブラウザのポップアップ許可を確認してください');

  createRelatedGridParentSession(definition, channel, child);
  return child;
}

function openRelatedGridView(definition) {
  const launchMode = String(definition.launchMode || 'new_window').trim().toLowerCase();
  if (launchMode === 'modal') return openRelatedGridModal(definition);
  if (launchMode === 'new_window') return openRelatedGridWindow(definition);
  throw new Error(`未対応のrelated Grid launchModeです: ${definition.launchMode}`);
}

function removeRelatedGridButtons() {
  document.querySelectorAll('.related-grid-launch-button, .related-grid-apply-button').forEach(button => button.remove());
}

function ensureRelatedGridButton(definition, rows) {
  const actions = document.querySelector('.grid-actions');
  if (!actions) return null;
  const button = document.createElement('button');
  button.type = 'button';
  button.className = 'ghost-button small related-grid-launch-button';
  button.dataset.relatedGridId = definition.id;
  button.textContent = `${definition.caption} ${rows.length}件`;
  const viewSource = definition.viewDef
    ? `${definition.viewDef}${definition.viewId ? `#${definition.viewId}` : ''}`
    : `同一ViewDef#${definition.viewId}`;
  button.title = `${definition.dataPath} を ${viewSource} で${definition.launchMode === 'modal' ? 'モーダル' : '別Grid'}表示`;
  const addButton = $('addRowBtn');
  if (addButton && addButton.parentElement === actions) actions.insertBefore(button, addButton);
  else actions.appendChild(button);
  button.addEventListener('click', async () => {
    try {
      button.disabled = true;
      const context = currentStudioActionContext({
        source: 'toolbar.relatedGridViews',
        relatedGridView: definition,
        toolbar: relatedGridToolbarDef()
      });
      const result = await executeStudioAction(definition.action, context);
      setStatus(result?.message || `${definition.caption}を開きました`, { toast: false });
    } catch (error) {
      console.error(error);
      setStatus(`別Grid起動エラー: ${error.message}`, { kind: 'error', title: '別Grid起動エラー' });
    } finally {
      button.disabled = false;
    }
  });
  return button;
}

function relatedGridChildRows() {
  if (!relatedGridChildRuntime || !sourceData) return null;
  return getByPath(sourceData, relatedGridChildRuntime.dataPath);
}

function relatedGridChildIsDirty() {
  const rows = relatedGridChildRows();
  if (!Array.isArray(rows) || !relatedGridChildRuntime) return false;
  return stableRelatedGridJson(rows) !== relatedGridChildRuntime.baseline;
}

function ensureRelatedGridApplyButton() {
  const actions = document.querySelector('.grid-actions');
  if (!actions || !relatedGridChildRuntime) return null;
  const button = document.createElement('button');
  button.id = 'relatedGridApplyToParentBtn';
  button.type = 'button';
  button.className = 'primary-button small related-grid-apply-button';
  button.textContent = '親画面へ反映';
  button.title = 'このGrid配列だけを親StudioのDataへ反映します。ファイル保存は親画面で行います。';
  const addButton = $('addRowBtn');
  if (addButton && addButton.parentElement === actions) actions.insertBefore(button, addButton);
  else actions.appendChild(button);
  button.addEventListener('click', () => applyRelatedGridToParent(button));
  return button;
}

function renderRelatedGridLaunchButtons() {
  removeRelatedGridButtons();
  if (!viewDef || !sourceData) return;
  if (relatedGridChildRuntime) {
    ensureRelatedGridApplyButton();
    return;
  }
  relatedGridDefinitions().forEach(definition => {
    const rows = relatedGridArrayFor(definition);
    if (rows) ensureRelatedGridButton(definition, rows);
  });
}

function applyRelatedGridToParent(button) {
  if (!relatedGridChildRuntime) return;
  const rows = relatedGridChildRows();
  if (!Array.isArray(rows)) {
    setStatus(`反映対象がArrayではありません: ${relatedGridChildRuntime.dataPath}`, { kind: 'error', title: '別Grid反映エラー' });
    return;
  }
  const parentWindow = relatedGridParentWindow();
  if (!parentWindow) {
    setStatus('親Studio画面が閉じられているため反映できません', { kind: 'error', title: '親画面なし' });
    return;
  }
  if (button) button.disabled = true;
  relatedGridChildRuntime.applyPending = true;
  setRelatedGridShellStatus('親画面へ反映中', 'info');
  parentWindow.postMessage({
    namespace: RELATED_GRID_MESSAGE_NS,
    type: 'APPLY',
    channel: relatedGridChildRuntime.channel,
    dataPath: relatedGridChildRuntime.dataPath,
    rows: cloneData(rows),
    baseline: relatedGridChildRuntime.baseline
  }, relatedGridTargetOrigin());
}

function relatedGridShellBannerText(payload) {
  const title = String(payload?.parentDataTitle ?? '').trim();
  const path = String(payload?.parentDataDisplayPath ?? '').trim();
  const caption = String(payload?.config?.caption ?? '別Grid').trim();
  return [caption, title, path].filter(Boolean).join(' / ');
}

function ensureRelatedGridShellBanner(payload) {
  let banner = document.getElementById('relatedGridShellBanner');
  if (!banner) {
    banner = document.createElement('section');
    banner.id = 'relatedGridShellBanner';
    banner.className = 'related-grid-shell-banner';
    const main = document.querySelector('main');
    if (main) main.insertBefore(banner, main.firstChild);
  }
  banner.innerHTML = '';
  const textBlock = document.createElement('div');
  textBlock.className = 'related-grid-shell-text';
  const title = document.createElement('strong');
  title.textContent = relatedGridShellBannerText(payload) || '別Grid';
  const note = document.createElement('span');
  note.textContent = '編集後は「親画面へ反映」を押し、最終保存は親Studio画面で行ってください。';
  const status = document.createElement('span');
  status.id = 'relatedGridShellStatus';
  status.className = 'related-grid-shell-status';
  status.textContent = '親画面を待機中';
  textBlock.append(title, note);
  banner.append(textBlock, status);
}

function setRelatedGridShellStatus(message, kind='info') {
  const status = document.getElementById('relatedGridShellStatus');
  if (!status) return;
  status.textContent = String(message ?? '');
  status.dataset.kind = kind;
}

function relatedGridViewDefForViewId(sourceViewDef, viewId, sourceLabel='ViewDef') {
  if (!sourceViewDef || typeof sourceViewDef !== 'object') {
    throw new Error(`${sourceLabel}を解決できません`);
  }
  const normalizedId = String(viewId ?? '').trim();
  if (!normalizedId) return cloneData(sourceViewDef);
  const views = Array.isArray(sourceViewDef.views) ? sourceViewDef.views : [];
  const targetView = views.find(candidate => String(candidate?.id ?? '').trim() === normalizedId);
  if (!targetView) {
    throw new Error(`${sourceLabel}にviewId=${normalizedId}が見つかりません`);
  }
  return {
    ...cloneData(sourceViewDef),
    views: [cloneData(targetView)]
  };
}

async function loadRelatedGridChildPayload(payload) {
  const config = normalizeRelatedGridDefinition(payload?.config, 0);
  if (!config) throw new Error('related Grid設定が不正です');
  if (!payload?.sourceData || typeof payload.sourceData !== 'object') throw new Error('親画面からDataを受信できませんでした');
  const rows = getByPath(payload.sourceData, config.dataPath);
  if (!Array.isArray(rows)) throw new Error(`related Grid対象がArrayではありません: ${config.dataPath}`);

  let loadedDef;
  if (config.viewDef) {
    const relatedDefName = safeJsonFileName(config.viewDef);
    if (!relatedDefName) throw new Error(`related Grid ViewDef名が不正です: ${config.viewDef}`);
    if (typeof isStaticHostingMode === 'function' && isStaticHostingMode()) {
      loadedDef = await fetchLaunchViewDefJson(normalizeRelatedGridViewStaticPath(config.viewDef));
    } else {
      loadedDef = {
        defName: relatedDefName,
        defObj: await fetchResolvedViewDef(relatedDefName),
        displayPath: `defs/${relatedDefName}`
      };
    }
    loadedDef.defObj = relatedGridViewDefForViewId(
      loadedDef.defObj,
      config.viewId,
      `related Grid ViewDef ${config.viewDef}`
    );
  } else {
    loadedDef = {
      defName: String(payload.parentViewDefName ?? lastLoadedDefName ?? '').trim(),
      defObj: relatedGridViewDefForViewId(
        payload.sourceViewDef,
        config.viewId,
        '親画面のViewDef'
      ),
      displayPath: String(payload.parentViewDefName ?? '').trim()
        ? `defs/${String(payload.parentViewDefName).trim()}`
        : `same-view-def#${config.viewId}`
    };
  }
  lastLoadedDefName = loadedDef.defName;
  launchRuntime = {
    fromUrl: true,
    mode: 'related_grid',
    readonly: false,
    dataParam: String(payload.parentDataDisplayPath ?? ''),
    viewParam: config.viewDef
      ? normalizeRelatedGridViewStaticPath(config.viewDef)
      : normalizeRelatedGridViewStaticPath(payload.parentViewDefName || ''),
    fileParam: ''
  };
  relatedGridChildRuntime = {
    channel: String(payload.channel ?? ''),
    config,
    dataPath: config.dataPath,
    baseline: stableRelatedGridJson(rows),
    applyPending: false
  };

  document.body.classList.add('studio-grid-only-shell');
  ensureRelatedGridShellBanner(payload);
  if ($('dataNameInput')) $('dataNameInput').value = String(payload.parentDataDisplayPath ?? '');
  if ($('defNameInput')) {
    $('defNameInput').value = loadedDef.defName || config.viewDef || `same-view-def#${config.viewId}`;
  }

  await loadFromObjects(
    loadedDef.defObj,
    cloneData(payload.sourceData),
    `${config.caption}を親画面から受信しました`,
    null,
    String(payload.parentDataDisplayPath ?? config.caption)
  );

  if ($('saveBtn')) {
    $('saveBtn').disabled = true;
    $('saveBtn').textContent = '親画面で保存';
  }
  renderRelatedGridLaunchButtons();
  setRelatedGridShellStatus(`親画面から受信済み / ${rows.length}件`, 'success');
  setStatus(`${config.caption}: 親画面から受信済み`, { toast: false, sticky: true });
}

function sendRelatedGridReady() {
  if (!relatedGridChildRuntime?.channel && !isRelatedGridLaunchQuery()) return;
  const params = relatedGridQueryParams();
  const channel = relatedGridChildRuntime?.channel || String(params.get('relatedGridChannel') ?? '').trim();
  const parentWindow = relatedGridParentWindow(params);
  if (!channel || !parentWindow) return;
  parentWindow.postMessage({
    namespace: RELATED_GRID_MESSAGE_NS,
    type: 'READY',
    channel
  }, relatedGridTargetOrigin());
}

function initializeRelatedGridChildFromQuery(params=relatedGridQueryParams()) {
  if (!isRelatedGridLaunchQuery(params)) return Promise.resolve(false);
  const channel = String(params.get('relatedGridChannel') ?? '').trim();
  if (!channel) return Promise.reject(new Error('relatedGridChannel がありません'));
  if (!relatedGridParentWindow(params)) return Promise.reject(new Error('親Studio画面が見つかりません。親画面の「別Grid」ボタンから開いてください'));

  document.body.classList.add('studio-grid-only-shell');
  relatedGridChildRuntime = {
    channel,
    config: null,
    dataPath: '',
    baseline: '',
    applyPending: false,
    initializing: false,
    loaded: false
  };
  ensureRelatedGridShellBanner({ config: { caption: '別Grid' } });
  setRelatedGridShellStatus('親画面からDataを受信中', 'info');

  return new Promise((resolve, reject) => {
    relatedGridChildInitResolve = resolve;
    relatedGridChildInitReject = reject;
    sendRelatedGridReady();
    relatedGridChildReadyTimer = window.setInterval(sendRelatedGridReady, 600);
    window.setTimeout(() => {
      if (relatedGridChildInitReject) {
        const fail = relatedGridChildInitReject;
        relatedGridChildInitResolve = null;
        relatedGridChildInitReject = null;
        window.clearInterval(relatedGridChildReadyTimer);
        relatedGridChildReadyTimer = null;
        setRelatedGridShellStatus('親画面からDataを受信できませんでした', 'error');
        fail(new Error('親Studio画面から別Gridデータを受信できませんでした'));
      }
    }, 15000);
  });
}

function parentRelatedGridInitPayload(session) {
  return {
    namespace: RELATED_GRID_MESSAGE_NS,
    type: 'INIT',
    channel: session.channel,
    config: session.definition,
    sourceData: cloneData(session.sourceDataSnapshot),
    parentDataDisplayPath: session.parentDataDisplayPath,
    parentDataTitle: session.parentDataTitle,
    parentViewDefName: session.parentViewDefName,
    sourceViewDef: cloneData(session.sourceViewDef),
    baseline: session.baseline
  };
}

function sendRelatedGridApplyResult(targetWindow, channel, result) {
  if (!targetWindow || targetWindow.closed) return;
  targetWindow.postMessage({
    namespace: RELATED_GRID_MESSAGE_NS,
    type: 'APPLY_RESULT',
    channel,
    ...result
  }, relatedGridTargetOrigin());
}

function handleParentRelatedGridMessage(event, message) {
  const session = relatedGridParentSessions.get(message.channel);
  if (!session || event.source !== session.child) return;

  if (message.type === 'READY') {
    session.child.postMessage(parentRelatedGridInitPayload(session), relatedGridTargetOrigin());
    return;
  }

  if (message.type !== 'APPLY') return;
  if (sourceData !== session.sourceDataRef) {
    sendRelatedGridApplyResult(session.child, session.channel, {
      ok: false,
      conflict: true,
      message: '親画面で別のData JSONが読み込まれました。現在の別Grid内容は反映していません。'
    });
    return;
  }
  const currentRowsAtPath = relatedGridArrayFor(session.definition);
  if (!currentRowsAtPath) {
    sendRelatedGridApplyResult(session.child, session.channel, {
      ok: false,
      message: `親画面の対象配列が見つかりません: ${session.definition.dataPath}`
    });
    return;
  }
  if (stableRelatedGridJson(currentRowsAtPath) !== session.baseline) {
    sendRelatedGridApplyResult(session.child, session.channel, {
      ok: false,
      conflict: true,
      message: '親画面側でも同じ配列が変更されています。上書きを避けるため反映を中断しました。親画面で再読込してから開き直してください。'
    });
    return;
  }
  if (!Array.isArray(message.rows)) {
    sendRelatedGridApplyResult(session.child, session.channel, {
      ok: false,
      message: '別Gridから受信した値がArrayではありません。'
    });
    return;
  }

  const nextRows = cloneData(message.rows);
  setByPath(sourceData, session.definition.dataPath, nextRows);
  session.baseline = stableRelatedGridJson(nextRows);
  renderRelatedGridLaunchButtons();
  if (typeof gridDef === 'function' && gridDef()?.dataPath === session.definition.dataPath) {
    loadRows();
    renderGrid();
  }
  setStatus(`${session.definition.caption} ${nextRows.length}件を親Dataへ反映しました。保存は親画面で実行してください`, {
    kind: 'success', title: '別Grid反映', toast: false, sticky: true
  });
  sendRelatedGridApplyResult(session.child, session.channel, {
    ok: true,
    baseline: session.baseline,
    count: nextRows.length,
    message: `親Dataへ${nextRows.length}件を反映しました。最終保存は親画面で行ってください。`
  });
}

async function handleChildRelatedGridMessage(event, message) {
  const parentWindow = relatedGridParentWindow();
  if (!parentWindow || event.source !== parentWindow) return;
  if (message.channel !== relatedGridChildRuntime?.channel) return;

  if (message.type === 'INIT') {
    if (relatedGridChildRuntime.loaded || relatedGridChildRuntime.initializing) return;
    relatedGridChildRuntime.initializing = true;
    try {
      window.clearInterval(relatedGridChildReadyTimer);
      relatedGridChildReadyTimer = null;
      await loadRelatedGridChildPayload(message);
      relatedGridChildRuntime.initializing = false;
      relatedGridChildRuntime.loaded = true;
      const resolve = relatedGridChildInitResolve;
      relatedGridChildInitResolve = null;
      relatedGridChildInitReject = null;
      if (resolve) resolve(true);
    } catch (error) {
      relatedGridChildRuntime.initializing = false;
      setRelatedGridShellStatus(`初期化エラー: ${error.message}`, 'error');
      const reject = relatedGridChildInitReject;
      relatedGridChildInitResolve = null;
      relatedGridChildInitReject = null;
      if (reject) reject(error);
      else setStatus(`別Grid初期化エラー: ${error.message}`, { kind: 'error', title: '別Grid初期化エラー' });
    }
    return;
  }

  if (message.type === 'APPLY_RESULT') {
    relatedGridChildRuntime.applyPending = false;
    const button = $('relatedGridApplyToParentBtn');
    if (button) button.disabled = false;
    if (message.ok) {
      relatedGridChildRuntime.baseline = String(message.baseline ?? stableRelatedGridJson(relatedGridChildRows()));
      setRelatedGridShellStatus(message.message || '親Dataへ反映しました', 'success');
      setStatus(message.message || '親Dataへ反映しました', { kind: 'success', title: '別Grid反映', toast: false, sticky: true });
    } else {
      setRelatedGridShellStatus(message.message || '親Dataへ反映できませんでした', message.conflict ? 'warn' : 'error');
      setStatus(message.message || '親Dataへ反映できませんでした', {
        kind: message.conflict ? 'warn' : 'error',
        title: message.conflict ? '競合を検知' : '別Grid反映エラー',
        sticky: true
      });
    }
  }
}

window.addEventListener('message', (event) => {
  if (!relatedGridMessageOriginAllowed(event)) return;
  const message = event.data;
  if (!message || message.namespace !== RELATED_GRID_MESSAGE_NS || !message.channel) return;
  if (relatedGridChildRuntime) {
    handleChildRelatedGridMessage(event, message).catch(error => {
      console.error(error);
      setRelatedGridShellStatus(`通信エラー: ${error.message}`, 'error');
      setStatus(`別Grid通信エラー: ${error.message}`, { kind: 'error', title: '別Grid通信エラー' });
    });
  } else {
    handleParentRelatedGridMessage(event, message);
  }
});

window.addEventListener('beforeunload', (event) => {
  if (!relatedGridChildRuntime) {
    relatedGridParentSessions.forEach(session => {
      if (!session.modal && session.child && !session.child.closed) {
        try { session.child.close(); } catch {}
      }
    });
    return;
  }
  if (relatedGridChildCloseApproved || !relatedGridChildIsDirty()) return;
  event.preventDefault();
  event.returnValue = '';
});

window.addEventListener('keydown', event => {
  if (event.key !== 'Escape' || relatedGridChildRuntime) return;
  const modalSession = [...relatedGridParentSessions.values()].reverse().find(session => session.modalOverlay);
  if (modalSession) {
    event.preventDefault();
    closeRelatedGridModal(modalSession.channel);
  }
});

registerStudioAction('OpenRelatedGridView', async (context={}) => {
  const definition = normalizeRelatedGridDefinition(context.relatedGridView, 0);
  if (!definition) throw new Error('relatedGridView定義がありません');
  openRelatedGridView(definition);
  return { message: `${definition.caption}を${definition.launchMode === 'modal' ? 'モーダル' : '別Studio画面'}で開きました` };
}, ['OpenRelatedGrid', 'LaunchRelatedGridView']);

if (isRelatedGridLaunchQuery()) document.body.classList.add('studio-grid-only-shell');
