// Studio standard: ViewDef-driven presentation, independent of Data/Edit/Save contracts.
// Applied when a ViewDef is loaded. No in-session profile switch UI is provided.
(function (global) {
  'use strict';
  const VALID = Object.freeze({
    preset: ['standard', 'compact', 'launcher'],
    density: ['standard', 'compact'],
    theme: ['light', 'dark', 'launch-dark'],
    shell: ['standard', 'minimal'],
    savePlacement: ['sidebar', 'footer']
  });
  function resolve(def) {
    const raw = def?.app?.presentation || {};
    const preset = VALID.preset.includes(raw.preset) ? raw.preset : 'standard';
    const base = preset === 'launcher'
      ? { density:'compact', theme:'launch-dark', shell:'minimal', savePlacement:'footer' }
      : preset === 'compact'
        ? { density:'compact', theme:'light', shell:'standard', savePlacement:'sidebar' }
        : { density:'standard', theme:'light', shell:'standard', savePlacement:'sidebar' };
    const out = { preset };
    for (const [key, fallback] of Object.entries(base)) {
      out[key] = VALID[key].includes(raw[key]) ? raw[key] : fallback;
    }
    // A hidden sidebar must not hide the single canonical Save button.
    if (out.shell === 'minimal') out.savePlacement = 'footer';
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
    return { head, footer, info:doc.getElementById('studioPresentationInfo'), actions:doc.getElementById('studioPresentationActions') };
  }
  function syncInfo(doc, widgets) {
    const status = doc.getElementById('status');
    const count = doc.getElementById('gridCount');
    widgets.info.textContent = [count?.textContent?.trim(), status?.textContent?.trim()].filter(Boolean).join('  /  ') || '準備OK';
  }
  let observers = [];
  function apply(def, doc=global.document) {
    const config = resolve(def);
    const body = doc?.body;
    const widgets = ensureScaffold(doc);
    if (!body || !widgets) return config;
    body.dataset.studioPreset = config.preset;
    body.dataset.studioDensity = config.density;
    body.dataset.studioTheme = config.theme;
    body.dataset.studioShell = config.shell;
    const name = String(def?.app?.name || 'JSON Object Studio');
    widgets.head.textContent = name;
    doc.title = name;
    // Notify the trusted NativeShell host about the resolved ViewDef presentation.
    // The browser-only Studio ignores this, and there is no runtime mode switch.
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
    if (save && config.savePlacement === 'footer') widgets.actions.append(save);
    else if (save && original) {
      const dock = original.querySelector('.studio-viewer-dock');
      if (dock) original.insertBefore(save, dock);
      else original.append(save);
    }
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
  global.StudioPresentationProfile = Object.freeze({ resolve, apply });
})(typeof window !== 'undefined' ? window : globalThis);
