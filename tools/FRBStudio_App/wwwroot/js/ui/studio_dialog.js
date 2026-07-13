// v0.18.13-studio-dialog-no-browser-standard
// FRB Studio共通の画面内ダイアログ。
// alert/confirm/prompt等のブラウザ標準ダイアログを使わず、視線と文脈を画面内に保つ。
(function installStudioDialog(){
  if (window.__frbStudioDialogInstalled) return;
  window.__frbStudioDialogInstalled = true;

  const css = `
    .studio-dialog-backdrop {
      position: fixed;
      inset: 0;
      z-index: 2147483400;
      display: none;
      place-items: center;
      padding: 18px;
      background: rgba(15, 23, 42, .24);
      backdrop-filter: blur(2px);
    }
    .studio-dialog-backdrop.show { display: grid; }
    .studio-dialog-panel {
      width: min(520px, calc(100vw - 36px));
      max-height: min(78vh, 640px);
      overflow: auto;
      border-radius: 18px;
      border: 1px solid rgba(148, 163, 184, .42);
      background: rgba(255, 255, 255, .98);
      color: #0f172a;
      box-shadow: 0 26px 80px rgba(15, 23, 42, .28);
      padding: 18px;
      display: grid;
      gap: 14px;
    }
    .studio-dialog-title {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 16px;
      font-weight: 900;
      line-height: 1.45;
    }
    .studio-dialog-title::before {
      content: "◆";
      color: #3b82f6;
      font-size: 12px;
    }
    .studio-dialog-panel.danger .studio-dialog-title::before { content: "⚠"; color: #ef4444; font-size: 15px; }
    .studio-dialog-message {
      font-size: 13px;
      line-height: 1.8;
      white-space: pre-wrap;
      word-break: break-word;
      color: #1f2937;
    }
    .studio-dialog-detail {
      display: none;
      border: 1px solid rgba(148, 163, 184, .32);
      border-radius: 12px;
      padding: 11px 12px;
      background: rgba(248, 250, 252, .94);
      color: #334155;
      font-size: 12px;
      line-height: 1.7;
      white-space: pre-wrap;
      word-break: break-word;
      max-height: 180px;
      overflow: auto;
    }
    .studio-dialog-detail.has-detail { display: block; }
    .studio-dialog-input {
      width: 100%;
      min-height: 38px;
      padding: 9px 11px;
      border: 1px solid rgba(148, 163, 184, .55);
      border-radius: 10px;
      background: #fff;
      color: #0f172a;
      font: inherit;
      ime-mode: inactive;
    }
    .studio-dialog-textarea {
      width: 100%;
      min-height: 160px;
      resize: vertical;
      padding: 10px 11px;
      border: 1px solid rgba(148, 163, 184, .55);
      border-radius: 10px;
      background: #fff;
      color: #0f172a;
      font: 12px/1.65 ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
    }
    .studio-dialog-actions {
      display: flex;
      justify-content: flex-end;
      gap: 10px;
      flex-wrap: wrap;
    }
    .studio-dialog-actions button {
      min-width: 92px;
      border: 0;
      border-radius: 999px;
      padding: 9px 16px;
      font-size: 13px;
      font-weight: 900;
      cursor: pointer;
    }
    .studio-dialog-actions [data-action="cancel"] { background: #e2e8f0; color: #0f172a; }
    .studio-dialog-actions [data-action="ok"] { background: linear-gradient(135deg, #2563eb, #3b82f6); color: #fff; }
    .studio-dialog-panel.danger .studio-dialog-actions [data-action="ok"] { background: linear-gradient(135deg, #ef4444, #f97316); }
    body.studio-dialog-open { overflow: hidden; }
  `;

  function ensureStyles(){
    if (document.getElementById('studioDialogStyles')) return;
    const style = document.createElement('style');
    style.id = 'studioDialogStyles';
    style.textContent = css;
    document.head.appendChild(style);
  }

  const runtime = { backdrop:null, panel:null, resolver:null, previousFocus:null, input:null, mode:'confirm' };

  function ensureDialog(){
    ensureStyles();
    if (runtime.backdrop) return runtime.backdrop;
    const backdrop = document.createElement('div');
    backdrop.id = 'studioDialogBackdrop';
    backdrop.className = 'studio-dialog-backdrop';
    backdrop.innerHTML = `
      <section class="studio-dialog-panel" role="dialog" aria-modal="true" aria-labelledby="studioDialogTitle">
        <div class="studio-dialog-title" id="studioDialogTitle"></div>
        <div class="studio-dialog-message" data-role="message"></div>
        <div class="studio-dialog-detail" data-role="detail"></div>
        <div data-role="inputWrap"></div>
        <div class="studio-dialog-actions">
          <button type="button" data-action="cancel">キャンセル</button>
          <button type="button" data-action="ok">OK</button>
        </div>
      </section>`;
    runtime.backdrop = backdrop;
    runtime.panel = backdrop.querySelector('.studio-dialog-panel');
    document.body.appendChild(backdrop);

    function finish(ok){
      const resolver = runtime.resolver;
      let value = !!ok;
      if (runtime.mode === 'prompt') value = ok ? String(runtime.input?.value ?? '') : null;
      hide();
      if (resolver) resolver(value);
    }
    backdrop.addEventListener('pointerdown', (e) => {
      const btn = e.target.closest('button[data-action]');
      if (!btn) return;
      e.preventDefault();
      e.stopPropagation();
      finish(btn.dataset.action === 'ok');
    }, true);
    backdrop.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' || e.key === 'Esc') { e.preventDefault(); e.stopPropagation(); finish(false); }
      if (e.key === 'Enter' && runtime.mode === 'confirm') { e.preventDefault(); e.stopPropagation(); finish(true); }
      if ((e.ctrlKey || e.metaKey) && e.key === 'Enter' && runtime.mode !== 'confirm') { e.preventDefault(); e.stopPropagation(); finish(true); }
    }, true);
    return backdrop;
  }

  function hide(){
    if (runtime.backdrop) runtime.backdrop.classList.remove('show');
    document.body.classList.remove('studio-dialog-open');
    runtime.resolver = null;
    runtime.input = null;
    const focusTarget = runtime.previousFocus;
    runtime.previousFocus = null;
    if (focusTarget && typeof focusTarget.focus === 'function') requestAnimationFrame(() => focusTarget.focus({ preventScroll:true }));
  }

  function openDialog(options = {}, mode = 'confirm'){
    if (runtime.resolver) hide();
    const backdrop = ensureDialog();
    const panel = runtime.panel;
    runtime.mode = mode;
    runtime.previousFocus = document.activeElement;
    panel.classList.toggle('danger', !!options.danger);
    panel.querySelector('#studioDialogTitle').textContent = String(options.title || (mode === 'prompt' ? '入力' : '確認'));
    panel.querySelector('[data-role="message"]').textContent = String(options.message || '実行しますか？');
    const detail = panel.querySelector('[data-role="detail"]');
    detail.textContent = String(options.detail || '');
    detail.classList.toggle('has-detail', !!String(options.detail || '').trim());
    const inputWrap = panel.querySelector('[data-role="inputWrap"]');
    inputWrap.innerHTML = '';
    runtime.input = null;
    if (mode === 'prompt') {
      const multiline = !!options.multiline;
      const input = document.createElement(multiline ? 'textarea' : 'input');
      input.className = multiline ? 'studio-dialog-textarea' : 'studio-dialog-input';
      if (!multiline) input.type = 'text';
      input.value = String(options.defaultValue ?? '');
      input.setAttribute('autocomplete', 'off');
      input.setAttribute('autocapitalize', 'none');
      input.setAttribute('spellcheck', 'false');
      input.setAttribute('inputmode', options.inputMode || 'text');
      inputWrap.appendChild(input);
      runtime.input = input;
    }
    panel.querySelector('button[data-action="ok"]').textContent = String(options.okText || options.okLabel || (options.danger ? '実行する' : 'OK'));
    panel.querySelector('button[data-action="cancel"]').textContent = String(options.cancelText || options.cancelLabel || 'キャンセル');
    document.body.classList.add('studio-dialog-open');
    backdrop.classList.add('show');
    requestAnimationFrame(() => (runtime.input || panel.querySelector('button[data-action="ok"]'))?.focus({ preventScroll:true }));
    return new Promise(resolve => { runtime.resolver = resolve; });
  }

  window.showStudioConfirmDialog = (options = {}) => openDialog(options, 'confirm');
  window.showStudioPromptDialog = (options = {}) => openDialog(options, 'prompt');
  window.showStudioManualCopyDialog = (title, content) => openDialog({
    title: title || '手動コピー',
    message: '自動コピーできませんでした。下の内容をコピーしてください。',
    defaultValue: String(content ?? ''),
    multiline: true,
    okText: '閉じる',
    cancelText: 'キャンセル'
  }, 'prompt');
})();
