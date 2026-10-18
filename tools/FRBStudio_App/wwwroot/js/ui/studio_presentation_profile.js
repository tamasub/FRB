// Studio standard: ViewDef-driven presentation, independent of Data/Edit/Save contracts.
// ViewDef owns density/shell; an opt-in launcher session may switch palette only.
(function (global) {
  'use strict';
  const VALID = Object.freeze({
    preset: ['standard', 'compact', 'launcher'],
    density: ['standard', 'compact'],
    theme: ['light', 'dark', 'launch-dark', 'launch-light'],
    shell: ['standard', 'minimal'],
    savePlacement: ['sidebar', 'footer', 'heading']
  });
  // The CLI hint arrives in the main page URL and is not written to Data or ViewDef.
  const initialTheme = (() => {
    try {
      const value = new URLSearchParams(global.location?.search || '').get('studioTheme');
      return value === 'light' ? 'launch-light' : value === 'dark' ? 'launch-dark' : null;
    } catch (_) { return null; }
  })();
  let sessionTheme = null;
  function isLauncher(config) {
    return config.preset === 'launcher' && config.shell === 'minimal';
  }
  function resolveSession(def) {
    const config = resolve(def);
    if (isLauncher(config)) config.theme = sessionTheme || initialTheme || config.theme;
    return config;
  }
  function resolve(def) {
    const raw = def?.app?.presentation || {};
    const preset = VALID.preset.includes(raw.preset) ? raw.preset : 'standard';
    const base = preset === 'launcher'
      ? { density:'compact', theme:'launch-dark', shell:'minimal', savePlacement:'heading' }
      : preset === 'compact'
        ? { density:'compact', theme:'light', shell:'standard', savePlacement:'sidebar' }
        : { density:'standard', theme:'light', shell:'standard', savePlacement:'sidebar' };
    const out = { preset };
    for (const [key, fallback] of Object.entries(base)) {
      out[key] = VALID[key].includes(raw[key]) ? raw[key] : fallback;
    }
    // A hidden sidebar must not hide the single canonical Save button.
    // Explicit footer remains available; launcher defaults to heading.
    if (out.shell === 'minimal' && out.savePlacement === 'sidebar') out.savePlacement = 'heading';
    // Header actions are ViewDef-declared; no automatic menu based on a domain/preset name.
    // actionId maps to registered Studio actions or the shared ViewDef maintenance path.
    if (Array.isArray(raw.headingMenu?.items)) {
      out.headingMenuItems = raw.headingMenu.items
        .filter(item => item && typeof item === 'object' && item.visible !== false)
        .map(item => ({
          id: String(item.id || '').trim(),
          label: String(item.label || '').trim(),
          actionId: String(item.actionId || '').trim()
        }))
        .filter(item => item.id && item.label && item.actionId);
    }
    return out;
  }
  function ensureScaffold(doc) {
    const pane = doc.querySelector('.json-studio-main-pane');
    const workspace = doc.querySelector('.json-studio-workspace');
    if (!pane || !workspace) return null;
    let head = doc.getElementById('studioPresentationHeading');
    if (!head) {
      head = doc.createElement('div');
      head.id = 'studioPresentationHeading';
      head.className = 'studio-presentation-heading';
      head.setAttribute('role', 'heading');
      head.setAttribute('aria-level','1');
      pane.prepend(head);
    }
    // A real title node prevents each presentation refresh from destroying Save.
    let headingTitle = doc.getElementById('studioPresentationTitle');
    if (!headingTitle) {
      headingTitle = doc.createElement('span');
      headingTitle.id = 'studioPresentationTitle';
      headingTitle.className = 'studio-presentation-title';
      head.append(headingTitle);
    }
    let headingActions = doc.getElementById('studioPresentationHeadingActions');
    if (!headingActions) {
      headingActions = doc.createElement('div');
      headingActions.id = 'studioPresentationHeadingActions';
      headingActions.className = 'studio-presentation-heading-actions';
      head.append(headingActions);
    }
    let footer = doc.getElementById('studioPresentationFooter');
    if (!footer) {
      footer = doc.createElement('footer');
      footer.id = 'studioPresentationFooter';
      footer.className = 'studio-presentation-footer';
      footer.setAttribute('aria-label','編集・保存');
      const info = doc.createElement('span');
      info.id = 'studioPresentationInfo';
      info.className = 'studio-presentation-info';
      const actions = doc.createElement('div');
      actions.id = 'studioPresentationActions';
      actions.className = 'studio-presentation-actions';
      footer.append(info, actions);
      pane.append(footer);
    }
    return { head, headingTitle, headingActions, footer, info:doc.getElementById('studioPresentationInfo'), actions:doc.getElementById('studioPresentationActions') };
  }
  function syncInfo(doc, widgets) {
    const status = doc.getElementById('status');
    const count = doc.getElementById('gridCount');
    widgets.info.textContent = [count?.textContent?.trim(), status?.textContent?.trim()].filter(Boolean).join('  /  ') || '準備OK';
  }

  // One reusable overflow for ViewDef-declared header commands. The legacy sidebar
  // maintenance control remains the canonical guarded entry point, not a second editor.
  function ensureHeadingMenu(doc, widgets) {
    let wrap = doc.getElementById('studioHeadingMenuWrap');
    if (wrap) return wrap;
    wrap = doc.createElement('div');
    wrap.id = 'studioHeadingMenuWrap';
    wrap.className = 'studio-heading-menu-wrap';
    wrap.hidden = true;
    const trigger = doc.createElement('button');
    trigger.id = 'studioHeadingMenuButton';
    trigger.className = 'studio-heading-menu-button';
    trigger.type = 'button';
    trigger.textContent = '⋯';
    trigger.title = 'その他の操作';
    trigger.setAttribute('aria-label', 'その他の操作');
    trigger.setAttribute('aria-haspopup', 'menu');
    trigger.setAttribute('aria-expanded', 'false');
    const menu = doc.createElement('div');
    menu.id = 'studioHeadingMenu';
    menu.className = 'studio-heading-menu';
    menu.setAttribute('role', 'menu');
    menu.setAttribute('aria-label', 'その他の操作');
    menu.hidden = true;
    wrap.append(trigger, menu);
    widgets.headingActions.append(wrap);

    function close(returnFocus=false) {
      menu.hidden = true;
      trigger.setAttribute('aria-expanded','false');
      if (returnFocus) trigger.focus();
    }
    function menuButtons() { return Array.from(menu.querySelectorAll('button[role="menuitem"]:not(:disabled)')); }
    trigger.addEventListener('click', () => {
      const open = menu.hidden;
      menu.hidden = !open;
      trigger.setAttribute('aria-expanded', String(open));
      if (open) menuButtons()[0]?.focus();
    });
    trigger.addEventListener('keydown', event => {
      if (event.key === 'ArrowDown' || event.key === 'ArrowUp') {
        event.preventDefault();
        menu.hidden = false;
        trigger.setAttribute('aria-expanded','true');
        const buttons=menuButtons();
        (event.key === 'ArrowUp' ? buttons[buttons.length-1] : buttons[0])?.focus();
      }
    });
    menu.addEventListener('keydown', event => {
      if (event.key === 'Escape') { event.preventDefault(); close(true); return; }
      if (!['ArrowDown','ArrowUp','Home','End'].includes(event.key)) return;
      event.preventDefault();
      const buttons=menuButtons();
      if (!buttons.length) return;
      const index=buttons.indexOf(doc.activeElement);
      const next=event.key === 'Home' ? 0 : event.key === 'End' ? buttons.length-1
        : (index + (event.key === 'ArrowDown' ? 1 : -1) + buttons.length) % buttons.length;
      buttons[next].focus();
    });
    doc.addEventListener('pointerdown', event => { if (!wrap.contains(event.target)) close(); });
    doc.addEventListener('keydown', event => {
      if (event.key === 'Escape' && !menu.hidden) { event.preventDefault(); close(true); }
    });
    wrap._studioCloseMenu = close;
    return wrap;
  }
  async function executeHeadingMenuAction(actionId) {
    if (actionId === 'MaintainCurrentViewDef') {
      // Reuse the existing UI click so JSON unsaved-change guard can intercept it.
      const maintenance = global.document.getElementById('maintainViewDefBtn');
      if (!maintenance || maintenance.disabled) throw new Error('現在のViewDefはメンテナンスできません');
      maintenance.click();
      return;
    }
    if (typeof global.executeStudioAction !== 'function') throw new Error('Studio Action Registryを利用できません');
    return global.executeStudioAction(actionId,
      typeof global.currentStudioActionContext === 'function' ? global.currentStudioActionContext() : {});
  }
  function renderHeadingMenu(doc, widgets, config, def) {
    const entries = config.savePlacement === 'heading' ? [...(config.headingMenuItems || [])] : [];
    if (config.savePlacement === 'heading' && isLauncher(config) && initialTheme) {
      entries.push({
        id: 'launcher_theme_switch',
        label: config.theme === 'launch-dark' ? '☀ ライトモードに切替' : '☾ ダークモードに切替',
        actionId: 'ToggleLauncherTheme'
      });
    }
    // Existing ViewDefs without a header menu keep their original DOM untouched.
    if (!entries.length && !doc.getElementById('studioHeadingMenuWrap')) return;
    const wrap = ensureHeadingMenu(doc, widgets);
    const menu = doc.getElementById('studioHeadingMenu');
    wrap._studioCloseMenu();
    menu.replaceChildren();
    wrap.hidden = entries.length === 0;
    if (wrap.hidden) return;
    for (const entry of entries) {
      const button=doc.createElement('button');
      button.type = 'button';
      button.className = 'studio-heading-menu-item';
      button.dataset.actionId = entry.actionId;
      button.setAttribute('role','menuitem');
      button.textContent = entry.label;
      button.addEventListener('click', async () => {
        wrap._studioCloseMenu();
        if (entry.actionId === 'ToggleLauncherTheme') {
          // Only the theme changes; never reload Data or re-create the Save button.
          sessionTheme = config.theme === 'launch-dark' ? 'launch-light' : 'launch-dark';
          apply(def, doc);
          doc.getElementById('studioHeadingMenuButton')?.focus();
          return;
        }
        try { await executeHeadingMenuAction(entry.actionId); }
        catch (error) {
          console.error(error);
          if (typeof global.setStatus === 'function') global.setStatus('操作を実行できません: ' + error.message,
            {kind:'error',title:'ヘッダーメニュー'});
        }
      });
      menu.append(button);
    }
  }

  let observers = [];
  function apply(def, doc=global.document) {
    const config = resolveSession(def);
    const body = doc?.body;
    const widgets = ensureScaffold(doc);
    if (!body || !widgets) return config;
    body.dataset.studioPreset = config.preset;
    body.dataset.studioDensity = config.density;
    body.dataset.studioTheme = config.theme;
    body.dataset.studioShell = config.shell;
    body.dataset.studioSavePlacement = config.savePlacement;
    const name = String(def?.app?.name || 'JSON Object Studio');
    widgets.headingTitle.textContent = name;
    doc.title = name;
    // Notify the trusted NativeShell host about the resolved ViewDef presentation.
    // Browser-only Studio ignores this. NativeShell also follows live palette switches.
    try {
      if (global.chrome?.webview?.postMessage && doc === global.document) {
        global.chrome.webview.postMessage({ studio_presentation: {
          preset: config.preset, theme: config.theme, shell: config.shell
        }});
      }
    } catch (_) { /* presentation never blocks editing */ }
    const save = doc.getElementById('saveBtn');
    const original = doc.querySelector('.loader-panel');
    // Move, never clone: save listeners, dirty-state and disabled-state retain identity.
    if (save && config.savePlacement === 'heading') widgets.headingActions.append(save);
    else if (save && config.savePlacement === 'footer') widgets.actions.append(save);
    else if (save && original) {
      const dock = original.querySelector('.studio-viewer-dock');
      if (dock) original.insertBefore(save, dock);
      else original.append(save);
    }
    renderHeadingMenu(doc, widgets, config, def);
    // Keep the overflow to the right of the single canonical Save button.
    const menuWrap = doc.getElementById('studioHeadingMenuWrap');
    if (menuWrap) widgets.headingActions.append(menuWrap);
    for (const obs of observers) obs.disconnect();
    observers = [];
    syncInfo(doc, widgets);
    if (typeof MutationObserver === 'function') {
      for (const id of ['status','gridCount']) {
        const elem = doc.getElementById(id);
        if (!elem) continue;
        const obs = new MutationObserver(() => syncInfo(doc,widgets));
        obs.observe(elem,{childList:true,characterData:true,subtree:true});
        observers.push(obs);
      }
    }
    return config;
  }
  global.StudioPresentationProfile = Object.freeze({ resolve, resolveSession, apply });
})(typeof window !== 'undefined' ? window : globalThis);
