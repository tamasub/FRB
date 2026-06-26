// v0.5-registry: Action registry skeleton.
// v0.6-action-execute-button で toolbar.executeButton から actionId を渡すための受け皿。
// この段階では既存ヘッダーボタンの動作は変更しない。

const ActionRegistry = createNamedRegistry('ActionRegistry');

function registerStudioAction(actionId, handler, aliases=[]) {
  return ActionRegistry.register(actionId, handler, { aliases });
}

async function executeStudioAction(actionId, context={}) {
  const action = ActionRegistry.get(actionId);
  if (!action) throw new Error(`未登録のActionです: ${actionId}`);
  return await action(context);
}

function currentStudioActionContext(extra={}) {
  return {
    viewDef,
    sourceData,
    currentRows,
    filteredRows,
    selectedIndex,
    currentDataApiUrl,
    setStatus,
    renderByKey,
    ...extra
  };
}



// v0.14.2-incident-prompt-copy-action:
// ViewDefの toolbar.executeButton.promptTemplate を、現在のDataファイル情報と選択行で展開する汎用Action。
// プロンプト本文はJSに固定せず、ViewDef側へ置く。
function normalizePromptPathValue(raw) {
  return String(raw ?? '')
    .trim()
    .replace(/\\/g, '/')
    .replace(/^\/+/, '')
    .replace(/[?#].*$/, '');
}

function decodePromptPathValue(raw) {
  const value = normalizePromptPathValue(raw);
  if (!value) return '';
  return value.split('/').map(part => {
    try { return decodeURIComponent(part); }
    catch { return part; }
  }).join('/');
}

function stripApiDataPrefixForPrompt(raw) {
  let value = decodePromptPathValue(raw);
  if (!value) return '';
  value = value.replace(/^api\/data\//, '');
  value = value.replace(/^data\//, match => match);
  return value;
}

function toStudioDataJsonPath(raw) {
  let value = stripApiDataPrefixForPrompt(raw);
  if (!value) return '';

  // /api/data/01_main/foo.json や 01_main/foo.json は、Studio管理Dataの canonical path へ寄せる。
  if (value.startsWith('data/json/')) return value;
  if (value.startsWith('json/')) return `data/${value}`;
  if (value.startsWith('data/')) {
    if (value.startsWith('data/markdown/')) return value;
    return value;
  }
  return `data/json/${value}`;
}

function promptFileNameFromPath(path) {
  return String(path ?? '').split('/').filter(Boolean).pop() || '';
}

function currentDataFileInfoForPrompt() {
  const candidates = [];
  if (launchRuntime?.dataParam) candidates.push(launchRuntime.dataParam);
  if (currentDataViewDefCandidateDataName) candidates.push(currentDataViewDefCandidateDataName);
  const inputValue = $('dataNameInput')?.value;
  if (inputValue) candidates.push(inputValue);
  if (currentDataApiUrl) {
    const fromApi = jsonNameFromUrl(currentDataApiUrl, 'data');
    if (fromApi) candidates.push(fromApi);
    candidates.push(currentDataApiUrl);
  }

  for (const raw of candidates) {
    const filePath = toStudioDataJsonPath(raw);
    if (filePath && filePath.toLowerCase().endsWith('.json')) {
      return {
        filePath,
        path: filePath,
        fullPath: filePath,
        fileName: promptFileNameFromPath(filePath),
        name: promptFileNameFromPath(filePath),
        apiUrl: currentDataApiUrl || '',
        displayName: raw || filePath
      };
    }
  }

  return {
    filePath: '',
    path: '',
    fullPath: '',
    fileName: '',
    name: '',
    apiUrl: currentDataApiUrl || '',
    displayName: ''
  };
}

function currentViewDefFileInfoForPrompt() {
  const raw = lastLoadedDefName || $('defNameInput')?.value || '';
  const filePath = raw ? (raw.startsWith('defs/') ? raw : `defs/${raw}`) : '';
  return {
    filePath,
    path: filePath,
    fullPath: filePath,
    fileName: promptFileNameFromPath(filePath),
    name: promptFileNameFromPath(filePath)
  };
}

function getTemplateValue(path, values) {
  const parts = String(path ?? '').split('.').filter(Boolean);
  let cur = values;
  for (const part of parts) {
    if (cur == null) return '';
    cur = cur[part];
  }
  if (cur == null) return '';
  if (Array.isArray(cur) || typeof cur === 'object') {
    try { return JSON.stringify(cur, null, 2); }
    catch { return String(cur); }
  }
  return String(cur);
}

function renderPromptTemplate(template, values) {
  const text = String(template ?? '');
  return text.replace(/{{\s*([\w.-]+)\s*}}/g, (_, key) => getTemplateValue(key, values));
}

function createManualCopyDialog(text) {
  let overlay = document.getElementById('manualCopyPromptOverlay');
  if (overlay) overlay.remove();

  overlay = document.createElement('div');
  overlay.id = 'manualCopyPromptOverlay';
  overlay.className = 'manual-copy-overlay';
  overlay.innerHTML = `
    <div class="manual-copy-dialog" role="dialog" aria-modal="true" aria-labelledby="manualCopyPromptTitle">
      <div class="manual-copy-title-row">
        <div>
          <div class="manual-copy-kicker">Clipboard fallback</div>
          <h2 id="manualCopyPromptTitle">手動コピーしてください</h2>
        </div>
        <button type="button" class="icon-button manual-copy-close" aria-label="閉じる">×</button>
      </div>
      <p class="manual-copy-note">ブラウザのクリップボードAPIが使えなかったため、下の依頼文を選択してコピーしてください。</p>
      <textarea class="manual-copy-textarea" readonly></textarea>
      <div class="button-row right">
        <button type="button" class="ghost-button manual-copy-select">全文選択</button>
        <button type="button" class="primary-button manual-copy-close2">閉じる</button>
      </div>
    </div>`;
  document.body.appendChild(overlay);
  const textarea = overlay.querySelector('.manual-copy-textarea');
  textarea.value = text;
  const close = () => overlay.remove();
  overlay.querySelectorAll('.manual-copy-close, .manual-copy-close2').forEach(btn => btn.addEventListener('click', close));
  overlay.querySelector('.manual-copy-select')?.addEventListener('click', () => {
    textarea.focus();
    textarea.select();
  });
  overlay.addEventListener('click', (e) => {
    if (e.target === overlay) close();
  });
  window.setTimeout(() => {
    textarea.focus();
    textarea.select();
  }, 0);
}

async function copyPromptTextToClipboard(text) {
  const value = String(text ?? '');
  if (!value) throw new Error('コピーするテキストが空です');

  if (navigator.clipboard?.writeText) {
    try {
      await navigator.clipboard.writeText(value);
      return { copied: true, fallback: false };
    } catch (err) {
      console.warn('navigator.clipboard.writeText failed:', err);
    }
  }

  const textarea = document.createElement('textarea');
  textarea.value = value;
  textarea.setAttribute('readonly', 'readonly');
  textarea.style.position = 'fixed';
  textarea.style.left = '-9999px';
  textarea.style.top = '0';
  document.body.appendChild(textarea);
  textarea.focus();
  textarea.select();
  try {
    if (document.execCommand?.('copy')) {
      textarea.remove();
      return { copied: true, fallback: false };
    }
  } catch (err) {
    console.warn('document.execCommand copy failed:', err);
  }
  textarea.remove();

  createManualCopyDialog(value);
  return { copied: false, fallback: true };
}

function buildPromptTemplateValues(context={}) {
  const row = context.selectedRow || null;
  const data = currentDataFileInfoForPrompt();
  const viewDefFile = currentViewDefFileInfoForPrompt();
  return {
    row: row || {},
    data,
    viewDef: viewDefFile,
    view: viewDefFile,
    action: context.executeButton || {},
    app: currentAppInfo || {}
  };
}

// 既存ボタンと同等の代表Actionを登録しておく。
// v0.6では toolbar.executeButton.action から渡された actionId で実行される。
registerStudioAction('LoadData', async () => loadFromFiles(), ['LoadJson']);
registerStudioAction('SaveData', async () => saveOverwriteJson(), ['SaveJson']);
registerStudioAction('ExportMarkdown', async () => {
  await exportMarkdown();
  return { message: 'Markdown出力を実行しました' };
});
registerStudioAction('ExportViewDefMarkdown', async () => {
  await exportViewDefMarkdown();
  return { message: 'ViewDef Markdown出力を実行しました' };
});
registerStudioAction('RefreshServerLists', async () => {
  await refreshServerLists();
  return { message: 'サーバー側JSON一覧を更新しました' };
});
registerStudioAction('ShowActionContext', async (context={}) => {
  console.log('ShowActionContext', context);
  return { message: `ActionContext確認: ${context.executeButton?.action ?? ''}` };
});
registerStudioAction('CopyPromptFromTemplate', async (context={}) => {
  const executeButton = context.executeButton || {};
  const template = executeButton.promptTemplate ?? executeButton.prompt_template ?? executeButton.template ?? '';
  if (!String(template).trim()) {
    throw new Error('promptTemplate がViewDefに定義されていません');
  }

  const row = context.selectedRow || null;
  if (!row) {
    throw new Error('プロンプトを作成する作業行を選択してください');
  }

  const values = buildPromptTemplateValues(context);
  if (!values.data.filePath) {
    throw new Error('現在読み込み中のData JSONファイル名を特定できません');
  }

  const prompt = renderPromptTemplate(template, values);
  const result = await copyPromptTextToClipboard(prompt);
  return {
    message: result.fallback
      ? 'AI依頼プロンプトを生成しました。手動コピー欄からコピーしてください'
      : `AI依頼プロンプトをコピーしました: ${values.row.phase || values.row.work_item_id || values.data.fileName}`
  };
}, ['CopyPrompt']);
registerStudioAction('Noop', async (context={}) => {
  return { message: `${context.executeButton?.caption ?? 'Action'} はNoopとして実行されました` };
});
