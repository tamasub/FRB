// FRB Studio Common UI Shell
// studio_work_0185 / v0.18.63-common-ui-shell-visual-foundation
(function () {
  'use strict';

  const pages = {
    'json-object': {
      href: 'index.html',
      label: 'JSON Object Studio',
      icon: '{}',
      iconClass: 'json',
      description: 'JSON > Definition & Data を構造化して管理'
    },
    'markdown': {
      href: 'mdViewer.html',
      label: 'Markdown Studio',
      icon: 'M',
      iconClass: 'markdown',
      description: 'Markdown > AIレビューコメントを構造化'
    },
    'diff-json': {
      href: 'DiffJsonViewer.html',
      label: 'Diff JSON Viewer',
      icon: '⇄',
      iconClass: 'diff',
      description: 'DiffToJson > ファイル差分を確認'
    },
    'meta-diff': {
      href: 'MetaDiff_HypothesisViewer.html',
      label: 'MetaDiff Viewer',
      icon: '✦',
      iconClass: 'meta',
      description: 'AI仮説 > 根拠差分を確認'
    }
  };

  const APP_SETTINGS_URL = 'config/app_settings.json';

  function htmlEscape(value) {
    return String(value == null ? '' : value)
      .replaceAll('&', '&amp;')
      .replaceAll('<', '&lt;')
      .replaceAll('>', '&gt;')
      .replaceAll('"', '&quot;');
  }

  function pageUrlWithoutState() {
    const current = String(location.pathname || '');
    const fileName = current.split('/').filter(Boolean).pop();
    return fileName || 'home.html';
  }

  function requestReset(options) {
    const detail = { handled: false };
    const event = new CustomEvent('frb-studio:reset-request', { cancelable: true, detail });
    document.dispatchEvent(event);
    if (event.defaultPrevented || detail.handled) return;

    const message = options.resetConfirmMessage || '現在の画面状態を破棄して、初期状態へ戻します。よろしいですか？';
    if (!window.confirm(message)) return;
    location.assign(pageUrlWithoutState());
  }

  function normalizeShortcutJsonPath(raw, label) {
    const value = String(raw == null ? '' : raw).trim();
    if (!value) return '';
    const normalized = value.replace(/\\/g, '/');
    if (
      normalized.includes('://') ||
      normalized.startsWith('/') ||
      normalized.startsWith('//') ||
      /^[A-Za-z]:/.test(normalized) ||
      /[?#]/.test(normalized)
    ) {
      throw new Error(`${label} に外部URL・絶対パス・クエリは指定できません: ${value}`);
    }
    if (!normalized.toLowerCase().endsWith('.json')) {
      throw new Error(`${label} は .json を指定してください: ${value}`);
    }
    const parts = normalized.split('/');
    if (parts.some(part => !part || part === '.' || part === '..')) {
      throw new Error(`${label} のパスが不正です: ${value}`);
    }
    return parts.join('/');
  }

  const SHORTCUT_LAUNCH_PARAM_KEYS = Object.freeze([
    'focusField',
    'focusValue',
    'openDetail',
    'action'
  ]);

  function appendShortcutLaunchParams(url, shortcut) {
    const params = shortcut?.launch_params ?? shortcut?.launchParams ?? null;
    if (!params || typeof params !== 'object' || Array.isArray(params)) return;

    SHORTCUT_LAUNCH_PARAM_KEYS.forEach(key => {
      if (!(key in params)) return;
      const raw = params[key];
      if (raw === null || raw === undefined) return;
      const value = typeof raw === 'boolean' ? String(raw) : String(raw).trim();
      if (!value) return;
      url.searchParams.set(key, value);
    });
  }

  function shortcutHref(shortcut) {
    const data = normalizeShortcutJsonPath(shortcut?.data, 'Data JSON');
    if (!data) throw new Error('Data JSON が未設定です');
    const viewDef = normalizeShortcutJsonPath(shortcut?.view_def, 'ViewDef');
    const url = new URL('index.html', location.href);
    url.search = '';
    url.hash = '';
    url.searchParams.set('data', data);
    if (viewDef) url.searchParams.set('view', viewDef);
    appendShortcutLaunchParams(url, shortcut);
    return url.href;
  }

  function shortcutHost(root) {
    return root?.querySelector?.('[data-frb-shortcuts]') || document.querySelector('[data-frb-shortcuts]');
  }

  function setShortcutMenuOpen(host, open) {
    if (!host) return;
    const trigger = host.querySelector('[data-frb-shortcuts-trigger]');
    const menu = host.querySelector('[data-frb-shortcuts-menu]');
    const nextOpen = Boolean(open && trigger && !trigger.disabled);
    if (trigger) trigger.setAttribute('aria-expanded', String(nextOpen));
    if (menu) menu.hidden = !nextOpen;
    host.classList.toggle('is-open', nextOpen);
  }

  function bindShortcutMenu(host) {
    if (!host || host.dataset.bound === 'true') return;
    host.dataset.bound = 'true';
    const trigger = host.querySelector('[data-frb-shortcuts-trigger]');
    const menu = host.querySelector('[data-frb-shortcuts-menu]');
    if (!trigger || !menu) return;

    trigger.addEventListener('click', () => {
      setShortcutMenuOpen(host, menu.hidden);
    });
    menu.addEventListener('click', event => {
      if (event.target.closest('[data-frb-launch-shortcut]')) setShortcutMenuOpen(host, false);
    });
    document.addEventListener('click', event => {
      if (!host.contains(event.target)) setShortcutMenuOpen(host, false);
    });
    document.addEventListener('keydown', event => {
      if (event.key === 'Escape') setShortcutMenuOpen(host, false);
    });
  }

  function renderLaunchShortcuts(host, settings) {
    if (!host) return;
    const trigger = host.querySelector('[data-frb-shortcuts-trigger]');
    const menu = host.querySelector('[data-frb-shortcuts-menu]');
    if (!trigger || !menu) return;

    const rawItems = Array.isArray(settings?.launch_shortcuts) ? settings.launch_shortcuts : [];
    menu.innerHTML = '';

    const title = document.createElement('div');
    title.className = 'frb-pagebar-shortcut-menu-title';
    title.textContent = 'JSON Object Studio';
    menu.appendChild(title);

    let validCount = 0;
    rawItems.forEach(shortcut => {
      const caption = String(shortcut?.caption ?? shortcut?.id ?? '').trim() || '名称未設定';
      try {
        const href = shortcutHref(shortcut);
        const item = document.createElement('a');
        item.className = 'frb-pagebar-shortcut-item';
        item.href = href;
        item.dataset.frbLaunchShortcut = String(shortcut?.id ?? '');
        item.setAttribute('role', 'menuitem');

        const label = document.createElement('span');
        label.className = 'frb-pagebar-shortcut-item-label';
        label.textContent = caption;
        item.appendChild(label);

        const path = document.createElement('span');
        path.className = 'frb-pagebar-shortcut-item-path';
        path.textContent = normalizeShortcutJsonPath(shortcut?.data, 'Data JSON');
        item.appendChild(path);

        menu.appendChild(item);
        validCount += 1;
      } catch (err) {
        const invalid = document.createElement('div');
        invalid.className = 'frb-pagebar-shortcut-item is-invalid';
        invalid.setAttribute('role', 'menuitem');
        invalid.setAttribute('aria-disabled', 'true');
        invalid.title = err.message;
        invalid.textContent = `${caption}（設定を確認）`;
        menu.appendChild(invalid);
      }
    });

    if (!rawItems.length) {
      const empty = document.createElement('div');
      empty.className = 'frb-pagebar-shortcut-empty';
      empty.textContent = 'JSON Object Studioのショートカットは未登録です';
      menu.appendChild(empty);
    }

    host.hidden = false;
    trigger.disabled = rawItems.length === 0;
    trigger.title = rawItems.length
      ? `JSON Object Studio ショートカット ${validCount}/${rawItems.length}件`
      : 'Studio設定からJSON Object Studioのショートカットを登録できます';
    setShortcutMenuOpen(host, false);
    bindShortcutMenu(host);
  }

  async function refreshLaunchShortcuts(root) {
    const host = shortcutHost(root);
    if (!host) return { loaded: false, count: 0 };
    try {
      const response = await fetch(APP_SETTINGS_URL, { cache: 'no-store' });
      if (!response.ok) throw new Error(`app_settings.json (${response.status})`);
      const settings = await response.json();
      renderLaunchShortcuts(host, settings);
      return {
        loaded: true,
        count: Array.isArray(settings?.launch_shortcuts) ? settings.launch_shortcuts.length : 0
      };
    } catch (err) {
      console.warn('FRB Studio shortcut menu load failed.', err);
      host.hidden = true;
      return { loaded: false, count: 0, error: String(err?.message ?? err) };
    }
  }

  function buildTopbar(activePage) {
    const nav = Object.entries(pages).map(([id, page]) => {
      const active = id === activePage ? ' is-active' : '';
      return `
        <a class="frb-shell-nav-link${active}" data-page="${id}" href="${page.href}">
          <span class="frb-shell-nav-icon frb-icon-${htmlEscape(page.iconClass || id)}" aria-hidden="true">${htmlEscape(page.icon)}</span>
          <span>${htmlEscape(page.label)}</span>
        </a>`;
    }).join('');

    const shell = document.createElement('header');
    shell.className = 'frb-app-shell';
    shell.setAttribute('data-frb-shell', 'common');
    shell.innerHTML = `
      <div class="frb-shell-topbar">
        <a class="frb-shell-brand" href="home.html" title="FRB Studio Homeへ戻る">
          <span class="frb-shell-home-icon">⌂</span>
          <span>FRB Studio</span>
        </a>
        <nav class="frb-shell-nav" aria-label="FRB Studio modules">${nav}</nav>
        <div class="frb-shell-utility">
          <a class="frb-shell-utility-link" data-frb-settings href="index.html?mode=settings" title="Studio設定を開く" aria-label="Studio設定を開く">
            <span class="frb-shell-utility-icon" aria-hidden="true">⚙</span>
            <span>設定</span>
          </a>
        </div>
      </div>`;
    return shell;
  }

  function buildPagebar(pageId, options) {
    const page = pages[pageId] || {};
    const title = options.pageTitle || page.label || 'FRB Studio';
    const description = options.description || page.description || '';
    const icon = options.icon || page.icon || '•';
    const showReset = options.showReset !== false;
    const showHome = options.showHome !== false;

    const pagebar = document.createElement('section');
    pagebar.className = 'frb-pagebar';
    pagebar.setAttribute('data-frb-pagebar', pageId || 'home');
    pagebar.innerHTML = `
      <div class="frb-pagebar-main">
        <span class="frb-page-icon frb-icon-${htmlEscape(page.iconClass || pageId || 'default')}" aria-hidden="true">${htmlEscape(icon)}</span>
        <h1 class="frb-page-title">${htmlEscape(title)}</h1>
        ${description ? `<span class="frb-page-separator">›</span><span class="frb-page-description">${htmlEscape(description)}</span>` : ''}
      </div>
      <div class="frb-pagebar-actions">
        <div class="frb-pagebar-shortcuts" data-frb-shortcuts hidden>
          <button type="button" class="frb-pagebar-button frb-pagebar-shortcut-trigger" data-frb-shortcuts-trigger
                  aria-haspopup="menu" aria-expanded="false" title="JSON Object Studio ショートカット">
            <span aria-hidden="true">↗</span>
            <span>ショートカット</span>
            <span class="frb-pagebar-shortcut-caret" aria-hidden="true">▾</span>
          </button>
          <div class="frb-pagebar-shortcut-menu" data-frb-shortcuts-menu role="menu" hidden></div>
        </div>
        ${showHome ? '<button type="button" class="frb-pagebar-button" data-frb-home>⌂ ホームに戻る</button>' : ''}
        ${showReset ? '<button type="button" class="frb-pagebar-button" data-frb-reset>↻ この画面の初期状態へ戻す</button>' : ''}
      </div>`;
    return pagebar;
  }

  function syncStickyOffsets(shell, pagebar) {
    const update = () => {
      const shellHeight = Math.ceil(shell.getBoundingClientRect().height || 0);
      const pagebarHeight = Math.ceil(pagebar.getBoundingClientRect().height || 0);
      document.documentElement.style.setProperty('--frb-shell-height', `${shellHeight}px`);
      document.documentElement.style.setProperty('--frb-fixed-header-height', `${shellHeight + pagebarHeight}px`);
    };

    requestAnimationFrame(update);
    window.addEventListener('resize', update, { passive: true });
    if ('ResizeObserver' in window) {
      const observer = new ResizeObserver(update);
      observer.observe(shell);
      observer.observe(pagebar);
    }
  }

  function mount(options) {
    options = options || {};
    if (document.querySelector('[data-frb-shell="common"]')) return;

    const pageId = options.pageId || '';
    document.body.classList.add('frb-shell-enabled');
    if (pageId) document.body.classList.add(`frb-page-${pageId}`);

    const shell = buildTopbar(pageId);
    const pagebar = buildPagebar(pageId, options);
    document.body.prepend(pagebar);
    document.body.prepend(shell);
    syncStickyOffsets(shell, pagebar);
    void refreshLaunchShortcuts(pagebar);

    const homeButton = pagebar.querySelector('[data-frb-home]');
    if (homeButton) homeButton.addEventListener('click', () => location.assign('home.html'));

    const resetButton = pagebar.querySelector('[data-frb-reset]');
    if (resetButton) resetButton.addEventListener('click', () => requestReset(options));
  }

  window.FrbStudioShell = {
    mount,
    pages: Object.freeze({ ...pages }),
    refreshLaunchShortcuts,
    shortcutHref
  };
})();
