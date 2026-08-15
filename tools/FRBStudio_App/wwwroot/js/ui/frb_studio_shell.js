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
      description: 'Markdown > Sidecarコメントを管理'
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
        <div class="frb-shell-utility" aria-hidden="true"></div>
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
        ${showHome ? '<button type="button" class="frb-pagebar-button" data-frb-home>⌂ ホームに戻る</button>' : ''}
        ${showReset ? '<button type="button" class="frb-pagebar-button" data-frb-reset>↻ この画面の初期状態へ戻す</button>' : ''}
      </div>`;
    return pagebar;
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

    const homeButton = pagebar.querySelector('[data-frb-home]');
    if (homeButton) homeButton.addEventListener('click', () => location.assign('home.html'));

    const resetButton = pagebar.querySelector('[data-frb-reset]');
    if (resetButton) resetButton.addEventListener('click', () => requestReset(options));
  }

  window.FrbStudioShell = { mount, pages: Object.freeze({ ...pages }) };
})();
