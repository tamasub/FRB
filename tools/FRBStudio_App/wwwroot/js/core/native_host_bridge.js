// v0.18.64-fielddefs-data-picker-access
// Browser mode: no-op.
// WebView2 Native Shell mode: translate the existing /api/* fetch contract into
// a small generic JSON command bridge so Studio application logic stays unchanged.
(function initFrbStudioNativeHostBridge(global) {
  'use strict';

  const webview = global.chrome?.webview;
  if (!webview) {
    global.FRBStudioNativeHost = Object.freeze({
      protocolVersion: '1.0',
      isAvailable: () => false,
      invoke: async () => { throw new Error('Native host is not available.'); }
    });
    return;
  }

  const PROTOCOL_VERSION = '1.0';
  const pending = new Map();
  let requestSequence = 0;
  const originalFetch = global.fetch.bind(global);

  function nextRequestId() {
    requestSequence += 1;
    return `native-${Date.now()}-${requestSequence}`;
  }

  function invoke(command, payload = {}, options = {}) {
    const requestId = nextRequestId();
    const timeoutMs = Number(options.timeoutMs ?? 30000);
    const request = {
      protocol_version: PROTOCOL_VERSION,
      request_id: requestId,
      command,
      payload: payload ?? {}
    };

    return new Promise((resolve, reject) => {
      const timeoutId = global.setTimeout(() => {
        pending.delete(requestId);
        const error = new Error(`Native command timeout: ${command}`);
        error.code = 'NATIVE_TIMEOUT';
        reject(error);
      }, timeoutMs);

      pending.set(requestId, { resolve, reject, timeoutId, command });
      webview.postMessage(request);
    });
  }

  webview.addEventListener('message', event => {
    const response = event.data;
    const requestId = String(response?.request_id ?? '');
    if (!requestId || !pending.has(requestId)) return;

    const slot = pending.get(requestId);
    pending.delete(requestId);
    global.clearTimeout(slot.timeoutId);

    if (response?.success) {
      slot.resolve(response.result);
      return;
    }

    const error = new Error(String(response?.error?.message ?? `Native command failed: ${slot.command}`));
    error.code = String(response?.error?.code ?? 'NATIVE_COMMAND_FAILED');
    error.nativeResponse = response;
    slot.reject(error);
  });

  global.FRBStudioNativeHost = Object.freeze({
    protocolVersion: PROTOCOL_VERSION,
    isAvailable: () => true,
    invoke
  });

  function jsonResponse(value, status = 200) {
    return new Response(JSON.stringify(value), {
      status,
      headers: { 'Content-Type': 'application/json; charset=utf-8' }
    });
  }

  function textResponse(value, contentType = 'text/plain; charset=utf-8', status = 200) {
    return new Response(String(value ?? ''), {
      status,
      headers: { 'Content-Type': contentType }
    });
  }

  function errorResponse(status, code, message) {
    return jsonResponse({ error: code, message }, status);
  }

  function normalizedRelativePath(value) {
    const decoded = decodeURIComponent(String(value ?? '')).replace(/\\/g, '/').replace(/^\/+/, '');
    const parts = decoded.split('/').filter(Boolean);
    if (parts.some(part => part === '.' || part === '..')) throw Object.assign(new Error('Invalid relative path.'), { code: 'INVALID_PATH' });
    return parts.join('/');
  }

  function joinPath(...parts) {
    return parts
      .map(normalizedRelativePath)
      .filter(Boolean)
      .join('/');
  }

  async function listRelativeFiles(root, extensions) {
    const result = await invoke('file.list', {
      path: root,
      recursive: true,
      entry_kind: 'files',
      extensions
    });
    const rootPrefix = normalizedRelativePath(root).replace(/\/$/, '') + '/';
    return (result?.items ?? [])
      .map(item => String(item?.path ?? '').replace(/\\/g, '/'))
      .filter(Boolean)
      .map(path => path.toLowerCase().startsWith(rootPrefix.toLowerCase()) ? path.slice(rootPrefix.length) : path)
      .sort((a, b) => a.localeCompare(b, 'ja'));
  }

  async function listDirectories(root) {
    const result = await invoke('file.list', {
      path: root,
      recursive: false,
      entry_kind: 'directories'
    });
    const rootPrefix = normalizedRelativePath(root).replace(/\/$/, '') + '/';
    return (result?.items ?? [])
      .map(item => String(item?.path ?? '').replace(/\\/g, '/'))
      .filter(Boolean)
      .map(path => path.toLowerCase().startsWith(rootPrefix.toLowerCase()) ? path.slice(rootPrefix.length) : path)
      .sort((a, b) => a.localeCompare(b, 'ja'));
  }

  async function listStudioDataJsonFiles() {
    const [dataFiles, fieldDefinitionFiles] = await Promise.all([
      listRelativeFiles('data/json', ['.json']),
      listRelativeFiles('fielddefs', ['.json'])
    ]);
    return [
      ...dataFiles,
      ...fieldDefinitionFiles.map(path => joinPath('fielddefs', path))
    ].sort((a, b) => a.localeCompare(b, 'ja'));
  }

  function studioDataWorkspacePath(relativePath) {
    const relative = normalizedRelativePath(relativePath);
    if (relative === 'fielddefs' || relative.startsWith('fielddefs/')) return relative;
    return joinPath('data/json', relative);
  }

  async function requestBodyText(input, init) {
    if (init?.body != null) {
      if (typeof init.body === 'string') return init.body;
      if (init.body instanceof Blob) return await init.body.text();
      return String(init.body);
    }
    if (typeof Request !== 'undefined' && input instanceof Request) {
      return await input.clone().text();
    }
    return '';
  }

  async function parseJsonBody(input, init) {
    const text = await requestBodyText(input, init);
    if (!text.trim()) return {};
    return JSON.parse(text);
  }

  function prettyJson(value) {
    return JSON.stringify(value, null, 2) + '\n';
  }

  function markdownContentType(path) {
    return path.toLowerCase().endsWith('.json')
      ? 'application/json; charset=utf-8'
      : 'text/markdown; charset=utf-8';
  }

  async function nativeApiFetch(input, init = {}) {
    const sourceUrl = typeof input === 'string' || input instanceof URL ? String(input) : input?.url;
    const url = new URL(sourceUrl, global.location.href);
    const method = String(init?.method ?? input?.method ?? 'GET').toUpperCase();
    const path = url.pathname;

    if (url.origin !== global.location.origin || !path.startsWith('/api/'))
      return originalFetch(input, init);

    try {
      if (method === 'GET' && path === '/api/data')
        return jsonResponse(await listStudioDataJsonFiles());

      if (method === 'GET' && path === '/api/defs')
        return jsonResponse(await listRelativeFiles('defs', ['.json']));

      if (method === 'GET' && path === '/api/markdown')
        return jsonResponse(await listRelativeFiles('data/markdown', ['.md', '.markdown']));

      if (method === 'GET' && path === '/api/overlays')
        return jsonResponse(await listDirectories('studio_overlays'));

      if (path === '/api/app-settings') {
        const settingsPath = 'wwwroot/config/app_settings.json';
        if (method === 'GET') {
          const result = await invoke('file.readText', { path: settingsPath });
          return textResponse(result?.content ?? '', 'application/json; charset=utf-8');
        }
        if (method === 'POST') {
          const body = await parseJsonBody(input, init);
          if (!body || typeof body !== 'object' || Array.isArray(body)) {
            return errorResponse(400, 'APP_SETTINGS_OBJECT_REQUIRED', 'app_settings.json must be a JSON object.');
          }
          await invoke('file.writeText', {
            path: settingsPath,
            content: prettyJson(body),
            create_directories: false
          });
          return jsonResponse({ saved: settingsPath });
        }
        return errorResponse(405, 'METHOD_NOT_ALLOWED', 'Only GET/POST are supported for app settings.');
      }

      if (method === 'POST' && path === '/api/data/drop') {
        const body = await parseJsonBody(input, init);
        const name = normalizedRelativePath(body?.name);
        await invoke('file.writeText', { path: joinPath('data/json', name), content: prettyJson(body?.json), create_directories: true });
        return jsonResponse({ saved: name });
      }

      if (method === 'POST' && path === '/api/defs/drop') {
        const body = await parseJsonBody(input, init);
        const name = normalizedRelativePath(body?.name);
        await invoke('file.writeText', { path: joinPath('defs', name), content: prettyJson(body?.json), create_directories: true });
        return jsonResponse({ saved: name });
      }

      if (method === 'POST' && path === '/api/markdown/drop') {
        const body = await parseJsonBody(input, init);
        const name = normalizedRelativePath(body?.name);
        await invoke('file.writeText', { path: joinPath('data/markdown', name), content: String(body?.content ?? ''), create_directories: true });
        return jsonResponse({ saved: name });
      }

      if (method === 'POST' && path === '/api/markdown/open-dialog') {
        try {
          const result = await invoke('dialog.openText', {
            title: 'Markdownを開く',
            filter: 'Markdown (*.md;*.markdown)|*.md;*.markdown|Text (*.txt)|*.txt|All files (*.*)|*.*',
            companion_suffixes: []
          });
          return jsonResponse({
            cancelled: false,
            document_id: result?.document_id ?? '',
            file_name: result?.file_name ?? '',
            path: result?.path ?? '',
            content: result?.content ?? '',
            // External DocumentはMarkdown本文だけをGrant対象にする。
            // Review JSONはWorkspaceへImportした後に初めて扱う。
            sidecar_file: '',
            sidecar_path: '',
            sidecar_content: '',
            sidecar_found: false
          });
        } catch (error) {
          if (error?.code === 'USER_CANCELLED') return jsonResponse({ cancelled: true });
          throw error;
        }
      }

      if (method === 'POST' && path === '/api/markdown/review-save-as-dialog') {
        const body = await parseJsonBody(input, init);
        try {
          const result = await invoke('dialog.saveText', {
            title: 'Review JSONを名前を付けて保存',
            filter: 'JSON (*.json)|*.json|All files (*.*)|*.*',
            file_name: String(body?.name ?? body?.file_name ?? 'document.md.review.json'),
            default_extension: 'json',
            content: String(body?.content ?? ''),
            companions: []
          });
          return jsonResponse({
            cancelled: false,
            document_id: result?.document_id ?? '',
            saved: result?.file_name ?? '',
            path: result?.path ?? ''
          });
        } catch (error) {
          if (error?.code === 'USER_CANCELLED') return jsonResponse({ cancelled: true });
          throw error;
        }
      }

      if (method === 'POST' && path === '/api/markdown/save-as-dialog') {
        const body = await parseJsonBody(input, init);
        // Save As はMarkdown本文の自由な保存/Exportとして扱い、
        // FRB Studio固有Review JSONはWorkspace外へ自動持ち出ししない。
        try {
          const result = await invoke('dialog.saveText', {
            title: 'Markdownを名前を付けて保存',
            filter: 'Markdown (*.md)|*.md|Markdown (*.markdown)|*.markdown|Text (*.txt)|*.txt|All files (*.*)|*.*',
            file_name: String(body?.name ?? body?.file_name ?? 'document.md'),
            default_extension: 'md',
            content: String(body?.content ?? ''),
            companions: []
          });
          return jsonResponse({
            cancelled: false,
            document_id: result?.document_id ?? '',
            saved: result?.file_name ?? '',
            path: result?.path ?? '',
            sidecar_saved: false,
            sidecar_file: '',
            sidecar_path: '',
            sidecar_error: ''
          });
        } catch (error) {
          if (error?.code === 'USER_CANCELLED') return jsonResponse({ cancelled: true });
          throw error;
        }
      }

      if (method === 'POST' && path === '/api/shell/open-json-folder') {
        const body = await parseJsonBody(input, init);
        const kind = String(body?.kind ?? '').toLowerCase();
        const relative = normalizedRelativePath(body?.path);
        let workspacePath;
        if (relative.startsWith('overlay/')) {
          const overlayParts = relative.split('/');
          workspacePath = joinPath('studio_overlays', overlayParts.slice(1).join('/'));
        } else {
          workspacePath = kind === 'viewdef' || kind === 'def' || kind === 'defs'
            ? joinPath('defs', relative)
            : studioDataWorkspacePath(relative);
        }
        const result = await invoke('shell.openFolder', { path: workspacePath, select_file: body?.selectFile ?? body?.select_file ?? true });
        return jsonResponse({ opened: result?.path ?? workspacePath, selected: workspacePath, kind, path: relative });
      }

      const dataMatch = path.match(/^\/api\/data\/(.+)$/);
      if (dataMatch) {
        const relative = normalizedRelativePath(dataMatch[1]);
        const workspacePath = studioDataWorkspacePath(relative);
        if (method === 'GET') {
          const result = await invoke('file.readText', { path: workspacePath });
          return textResponse(result?.content ?? '', 'application/json; charset=utf-8');
        }
        if (method === 'POST') {
          const body = await parseJsonBody(input, init);
          await invoke('file.writeText', { path: workspacePath, content: prettyJson(body), create_directories: true });
          return jsonResponse({ saved: relative });
        }
      }

      const defsMatch = path.match(/^\/api\/defs\/(.+)$/);
      if (defsMatch) {
        const relative = normalizedRelativePath(defsMatch[1]);
        const workspacePath = joinPath('defs', relative);
        if (method === 'GET') {
          const result = await invoke('file.readText', { path: workspacePath });
          return textResponse(result?.content ?? '', 'application/json; charset=utf-8');
        }
        if (method === 'POST') {
          const body = await parseJsonBody(input, init);
          await invoke('file.writeText', { path: workspacePath, content: prettyJson(body), create_directories: true });
          return jsonResponse({ saved: relative });
        }
      }

      const fieldDefsMatch = path.match(/^\/api\/fielddefs\/(.+)$/);
      if (method === 'GET' && fieldDefsMatch) {
        const relative = normalizedRelativePath(fieldDefsMatch[1]);
        const result = await invoke('file.readText', { path: joinPath('fielddefs', relative) });
        return textResponse(result?.content ?? '', 'application/json; charset=utf-8');
      }

      const markdownMatch = path.match(/^\/api\/markdown\/(.+)$/);
      if (markdownMatch) {
        const relative = normalizedRelativePath(markdownMatch[1]);
        const workspacePath = joinPath('data/markdown', relative);
        if (method === 'GET') {
          const result = await invoke('file.readText', { path: workspacePath });
          return textResponse(result?.content ?? '', markdownContentType(relative));
        }
        if (method === 'POST') {
          const body = await parseJsonBody(input, init);
          await invoke('file.writeText', {
            path: workspacePath,
            content: String(body?.content ?? ''),
            create_directories: true
          });
          return jsonResponse({ saved: relative });
        }
      }

      const overlaySidecarMatch = path.match(/^\/api\/overlays\/([^/]+)\/sidecars\/(.+)$/);
      if (method === 'POST' && overlaySidecarMatch) {
        const overlayId = normalizedRelativePath(overlaySidecarMatch[1]);
        const relative = normalizedRelativePath(overlaySidecarMatch[2]);
        const body = await parseJsonBody(input, init);
        const target = joinPath('studio_overlays', overlayId, 'sidecars', relative);
        await invoke('file.writeText', { path: target, content: prettyJson(body), create_directories: true });
        return jsonResponse({ saved: `overlay/${overlayId}/sidecars/${relative}` });
      }

      const overlayMatch = path.match(/^\/api\/overlays\/([^/]+)\/(.+)$/);
      if (method === 'GET' && overlayMatch) {
        const overlayId = normalizedRelativePath(overlayMatch[1]);
        const relative = normalizedRelativePath(overlayMatch[2]);
        const result = await invoke('file.readText', { path: joinPath('studio_overlays', overlayId, relative) });
        const contentType = relative.toLowerCase().endsWith('.js')
          ? 'application/javascript; charset=utf-8'
          : relative.toLowerCase().endsWith('.md')
            ? 'text/markdown; charset=utf-8'
            : 'application/json; charset=utf-8';
        return textResponse(result?.content ?? '', contentType);
      }

      if (method === 'POST' && path === '/api/actions/command/run') {
        const body = await parseJsonBody(input, init);
        const profileId = String(body?.command_profile_id ?? body?.profile_id ?? '').trim() || (body?.test_runner_id ? 'test_runner' : 'git_diff_export');
        const result = await invoke('process.runProfile', { profile_id: profileId, ...body }, { timeoutMs: 240000 });

        if (profileId === 'git_diff_export' && Array.isArray(result?.output_artifacts)) {
          const artifact = result.output_artifacts.find(item => String(item?.path ?? '').toLowerCase().startsWith('wwwroot/diff/'));
          if (artifact?.path) {
            const webPath = '/' + String(artifact.path).replace(/\\/g, '/').replace(/^wwwroot\//i, '');
            result.viewer_url = `/DiffJsonViewer.html?src=${encodeURIComponent(webPath)}`;
            result.diff_json_viewer_url = result.viewer_url;
          }
        }

        const status = result?.success === true ? 200 : (result?.result_kind === 'test_failed' ? 422 : 500);
        return jsonResponse(result, status);
      }

      if (method === 'GET' && path === '/api/actions/command/profiles') {
        return jsonResponse([
          { command_profile_id: 'git_diff_export', display_name: 'Export-DiffToJson.ps1 / Git Diff JSON Export', kind: 'git_diff_export' },
          { command_profile_id: 'test_runner', display_name: 'TestRunner.ps1 / Studio Test Runner', kind: 'test_runner' }
        ]);
      }

      if (method === 'GET' && path === '/api/actions/command/diagnostics') {
        const workspace = await invoke('workspace.getCurrent');
        return jsonResponse({ native_shell: true, workspace_root: workspace?.root_path ?? '' });
      }

      return errorResponse(404, 'NATIVE_API_NOT_MAPPED', `${method} ${path} is not mapped by Native Shell Phase A.`);
    } catch (error) {
      const status = error?.code === 'WORKSPACE_PATH_DENIED' ? 403 : 500;
      return errorResponse(status, String(error?.code ?? 'NATIVE_BRIDGE_ERROR'), String(error?.message ?? error));
    }
  }

  global.fetch = nativeApiFetch;
})(window);
