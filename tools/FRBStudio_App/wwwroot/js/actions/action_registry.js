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

// v0.14.38-test-runner-command-profile:
// ViewDefの toolbar.executeButton から、選択行のCommandProfile実行設定をProgram.csへ渡す。
// Data JSONには任意commandLine/scriptPath/test_fileを持たせず、Program.cs側の許可済みprofileだけを実行する。
function commandProfileRowValue(row, ...keys) {
  for (const key of keys) {
    const value = getByPath(row, key);
    if (value !== undefined && value !== null && String(value).trim() !== '') return value;
  }
  return '';
}

function commandProfileBooleanValue(value) {
  if (value === true) return true;
  if (value === false || value === null || value === undefined) return false;
  const text = String(value).trim().toLowerCase();
  return text === 'true' || text === '1' || text === 'yes' || text === 'on';
}

function buildCommandProfileRunRequest(row) {
  const request = {
    command_profile_id: String(commandProfileRowValue(row, 'command_profile_id', 'profile_id')).trim(),
    mode: String(commandProfileRowValue(row, 'mode')).trim(),
    range: String(commandProfileRowValue(row, 'range')).trim(),
    from_ref: String(commandProfileRowValue(row, 'from_ref', 'from')).trim(),
    to_ref: String(commandProfileRowValue(row, 'to_ref', 'to')).trim(),
    output_path_display: String(commandProfileRowValue(row, 'output_path_display', 'output_path')).trim(),
    unified: Number(commandProfileRowValue(row, 'unified')) || 3,
    max_patch_chars: Number(commandProfileRowValue(row, 'max_patch_chars')) || 60000,
    no_patch: commandProfileBooleanValue(commandProfileRowValue(row, 'no_patch')),
    test_runner_id: String(commandProfileRowValue(row, 'test_runner_id')).trim(),
    run_config_id: String(commandProfileRowValue(row, 'run_config_id')).trim(),
    run_mode: String(commandProfileRowValue(row, 'run_mode')).trim(),
    command_preview: String(commandProfileRowValue(row, 'command_preview')).trim()
  };

  if (!request.command_profile_id) request.command_profile_id = request.test_runner_id ? 'test_runner' : 'git_diff_export';
  return request;
}

async function postCommandProfileRun(request) {
  const res = await fetch('/api/actions/command/run', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request)
  });

  let payload = null;
  const text = await res.text();
  if (text) {
    try { payload = JSON.parse(text); }
    catch { payload = { message: text }; }
  }

  if (!res.ok) {
    // v0.14.39-test-runner-result-classification:
    // wait mode のテスト失敗は、HTTPエラー扱いで届いてもAction起動エラーにしない。
    if (payload?.result_kind === 'test_failed') return payload;

    const message = payload?.message || payload?.error || `CommandProfile API error: ${res.status}`;
    const detail = payload?.stderr ? `\n${payload.stderr}` : '';
    const err = new Error(message + detail);
    err.commandResult = payload;
    err.statusOptions = { kind: 'error', title: '起動エラー', duration: 6800, sticky: true };
    throw err;
  }

  return payload || {};
}

function commandProfileOutputArtifactsText(artifacts) {
  if (!Array.isArray(artifacts) || artifacts.length === 0) return '';
  return artifacts.map(a => {
    const path = a?.path || a?.full_path || '';
    const exists = a?.exists === true ? 'exists' : (a?.exists === false ? 'missing' : 'unknown');
    const kind = a?.kind ? ` / ${a.kind}` : '';
    return `- ${path} [${exists}${kind}]`;
  }).join('\n');
}

function commandProfileResultDetailText(result, caption) {
  const lines = [];
  lines.push(`Caption: ${caption || ''}`);
  lines.push(`Result Kind: ${result?.result_kind || ''}`);
  lines.push(`Success: ${result?.success === true}`);
  if (result?.profile_id) lines.push(`Profile: ${result.profile_id}`);
  if (result?.test_runner_id) lines.push(`Test Runner ID: ${result.test_runner_id}`);
  if (result?.run_mode) lines.push(`Run Mode: ${result.run_mode}`);
  if (result?.exit_code !== undefined && result?.exit_code !== null) lines.push(`Exit Code: ${result.exit_code}`);
  if (result?.duration_ms !== undefined && result?.duration_ms !== null) lines.push(`Duration: ${result.duration_ms} ms`);
  if (result?.working_directory) lines.push(`Working Directory: ${result.working_directory}`);
  if (result?.command_preview) lines.push(`Command Preview: ${result.command_preview}`);
  if (result?.message) lines.push(`Message: ${result.message}`);

  const artifacts = commandProfileOutputArtifactsText(result?.output_artifacts);
  if (artifacts) {
    lines.push('');
    lines.push('Output Artifacts:');
    lines.push(artifacts);
  }

  if (result?.stdout) {
    lines.push('');
    lines.push('STDOUT:');
    lines.push(String(result.stdout));
  }
  if (result?.stderr) {
    lines.push('');
    lines.push('STDERR:');
    lines.push(String(result.stderr));
  }

  return lines.join('\n');
}

function showCommandProfileResultDialog(result, caption) {
  const detailText = commandProfileResultDetailText(result, caption);
  if (!detailText.trim()) return;

  let overlay = document.getElementById('commandProfileResultOverlay');
  if (overlay) overlay.remove();

  const kind = result?.result_kind || '';
  const title = kind === 'test_failed' ? 'テスト失敗の詳細' : 'CommandProfile 実行結果';
  const note = kind === 'test_failed'
    ? 'TestRunnerは起動済みです。テスト本体がfailしました。stdout / stderr / artifact path を確認してください。'
    : 'CommandProfileの実行結果です。';

  overlay = document.createElement('div');
  overlay.id = 'commandProfileResultOverlay';
  overlay.className = 'manual-copy-overlay';
  overlay.innerHTML = `
    <div class="manual-copy-dialog" role="dialog" aria-modal="true" aria-labelledby="commandProfileResultTitle">
      <div class="manual-copy-title-row">
        <div>
          <div class="manual-copy-kicker">CommandProfile Result</div>
          <h2 id="commandProfileResultTitle"></h2>
        </div>
        <button type="button" class="icon-button command-result-close" aria-label="閉じる">×</button>
      </div>
      <p class="manual-copy-note"></p>
      <textarea class="manual-copy-textarea" readonly></textarea>
      <div class="button-row right">
        <button type="button" class="ghost-button command-result-select">全文選択</button>
        <button type="button" class="primary-button command-result-close2">閉じる</button>
      </div>
    </div>`;
  document.body.appendChild(overlay);
  overlay.querySelector('#commandProfileResultTitle').textContent = title;
  overlay.querySelector('.manual-copy-note').textContent = note;
  const textarea = overlay.querySelector('.manual-copy-textarea');
  textarea.value = detailText;
  const close = () => overlay.remove();
  overlay.querySelectorAll('.command-result-close, .command-result-close2').forEach(btn => btn.addEventListener('click', close));
  overlay.querySelector('.command-result-select')?.addEventListener('click', () => {
    textarea.focus();
    textarea.select();
  });
  overlay.addEventListener('click', (e) => {
    if (e.target === overlay) close();
  });
}

function isCommandProfileLaunchResult(result) {
  return String(result?.run_mode || '').toLowerCase() === 'launch'
    || result?.result_kind === 'command_launched';
}

function commandProfileStatusFromResult(result, caption) {
  const kind = result?.result_kind || '';
  const exitCode = result?.exit_code !== undefined && result?.exit_code !== null ? ` exit_code=${result.exit_code}` : '';

  // v0.16.6-test-runner-launch-toast:
  // launch mode は「テスト結果」ではなく「対話型UIの起動」として扱う。
  // 画面を塞ぐ結果ダイアログではなく、短時間の軽いトーストだけにする。
  if (isCommandProfileLaunchResult(result)) {
    return {
      message: result?.message || `${caption} を起動しました`,
      options: { kind: 'success', title: '起動しました', duration: 3200, sticky: false }
    };
  }

  if (kind === 'test_failed') {
    return {
      message: result?.message || `テスト失敗: ${caption}${exitCode}`,
      options: { kind: 'warn', title: 'テスト失敗', duration: 7600, sticky: true }
    };
  }

  if (kind === 'launcher_error') {
    return {
      message: result?.message || `TestRunner起動エラー: ${caption}`,
      options: { kind: 'error', title: '起動エラー', duration: 7600, sticky: true }
    };
  }

  if (kind === 'test_passed' && result?.run_mode === 'wait') {
    return {
      message: result?.message || `テスト成功: ${caption}`,
      options: { kind: 'success', title: 'テスト成功' }
    };
  }

  return {
    message: result?.message || `CommandProfile Run完了: ${caption}`,
    options: { kind: 'success', title: '完了' }
  };
}

registerStudioAction('RunCommandProfile', async (context={}) => {
  if (typeof isStaticHostingMode === 'function' && isStaticHostingMode()) {
    throw new Error('CommandProfile Run はローカルFRBStudio実行時のみ使用できます');
  }

  const row = context.selectedRow || null;
  if (!row) throw new Error('CommandProfileを実行する設定行を選択してください');

  const request = buildCommandProfileRunRequest(row);
  const caption = row.caption || row.run_config_id || request.test_runner_id || request.mode || request.command_profile_id;

  if (row.enabled === false) throw new Error(`この実行設定は無効です: ${caption}`);

  const result = await postCommandProfileRun(request);
  console.log('RunCommandProfile result', result);

  if (result?.result_kind === 'test_failed' && !isCommandProfileLaunchResult(result)) {
    showCommandProfileResultDialog(result, caption);
  }

  const status = commandProfileStatusFromResult(result, caption);
  return {
    message: status.message,
    statusOptions: status.options,
    status_kind: status.options?.kind,
    status_title: status.options?.title,
    result
  };
}, ['RunGitDiffExport', 'GitDiffRun', 'RunTestRunner', 'TestRun']);