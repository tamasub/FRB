// FRB Studio JSON load diagnostics: failure only; do not send document contents.
(function installStudioJsonLoadDiagnostics(global) {
  'use strict';

  function oneLine(value, max = 1600) {
    const text = String(value ?? '').replace(/[\r\n\t]+/g, ' ');
    return text.length > max ? text.slice(0, max) + '...' : text;
  }

  async function record(error, context = {}) {
    const payload = {
      stage: oneLine(context.stage || 'json-load', 100),
      data_path: oneLine(context.dataPath, 1200),
      view_def_path: oneLine(context.viewDefPath, 1200),
      code: oneLine(error?.code || error?.name || 'JSON_LOAD_FAILED', 100),
      message: oneLine(error?.message || error, 2000),
      detail: oneLine([
        error?.details && JSON.stringify(error.details),
        error?.stack,
      ].filter(Boolean).join(' / '), 2200),
    };
    console.error('[FRBStudio JSON LOAD FAILURE]', payload, error);
    try {
      if (global.FRBStudioNativeHost?.isAvailable?.()) {
        return await global.FRBStudioNativeHost.invoke('diagnostics.recordJsonLoadError', payload);
      }
    } catch (logError) {
      console.warn('[FRBStudio] JSON load diagnostic file write failed:', logError);
    }
    return null;
  }

  global.FRBStudioJsonLoadDiagnostics = Object.freeze({ record });
})(window);
