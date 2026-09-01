// v0.18.130-responsibility-pattern-def-trace
// Responsibility -> Guarantee -> Pattern Def -> Generated TestPattern の生成Traceを明示する。
// Pattern Def IDは主情報ではなくTrace用補助情報なので、Preview表では最終列へ静かに表示する。
(function installResponsibilityPatternDefTrace(){
  'use strict';

  if (globalThis.__frbResponsibilityPatternDefTraceLoaded) return;
  globalThis.__frbResponsibilityPatternDefTraceLoaded = true;

  function normalizeId(value) {
    return String(value ?? '').trim();
  }

  function enabledPatternDefinitions(responsibility={}) {
    return (responsibility?.test_pattern_definitions ?? [])
      .filter(item => item?.enabled !== false && normalizeId(item?.pattern_def_id));
  }

  function resolvePatternDefId(pattern={}, responsibility={}) {
    const explicit = normalizeId(pattern?.pattern_def_id);
    if (explicit) return explicit;

    const sourceExplicit = normalizeId(
      pattern?.source?.pattern_def_id ??
      pattern?.source?.patternDefId ??
      pattern?.definition?.pattern_def_id
    );
    if (sourceExplicit) return sourceExplicit;

    const patternId = normalizeId(pattern?.pattern_id);
    if (!patternId) return '';

    const definitions = enabledPatternDefinitions(responsibility);

    // 1) 1 Pattern Def -> 1 TestPattern の責務は完全一致。
    const exact = definitions.find(item => normalizeId(item?.pattern_def_id) === patternId);
    if (exact) return normalizeId(exact.pattern_def_id);

    // 2) SEARCH_OPERATOR_MATRIX等、1 Pattern Def -> N TestPatterns は
    //    Pattern Def IDをprefixとする現在の命名契約から生成元を一意解決する。
    const prefixCandidates = definitions
      .map(item => normalizeId(item?.pattern_def_id))
      .filter(id => patternId.startsWith(`${id}_`))
      .sort((a, b) => b.length - a.length);

    return prefixCandidates[0] ?? '';
  }

  function annotateGeneratedPatterns(result={}, responsibility={}) {
    const patterns = Array.isArray(result?.test_patterns) ? result.test_patterns : [];
    patterns.forEach(pattern => {
      const patternDefId = resolvePatternDefId(pattern, responsibility);
      pattern.pattern_def_id = patternDefId;

      // Generated Caseも同じTraceを継承する。主表示には出さないがEvidence追跡に使える。
      (pattern?.generated_cases ?? []).forEach(generatedCase => {
        if (generatedCase && typeof generatedCase === 'object') {
          generatedCase.pattern_def_id = patternDefId;
        }
      });
    });
    return result;
  }

  function patchPreviewService() {
    if (typeof ResponsibilityTestPreviewService === 'undefined') return false;
    const proto = ResponsibilityTestPreviewService.prototype;
    if (!proto || proto.__patternDefTracePatched) return true;

    const originalDerive = proto.derive;
    if (typeof originalDerive !== 'function') return false;

    proto.derive = function deriveWithPatternDefTrace(args={}) {
      const result = originalDerive.call(this, args);
      return annotateGeneratedPatterns(result, args?.responsibility ?? {});
    };
    proto.__patternDefTracePatched = true;
    return true;
  }

  function patchPreviewComponent() {
    if (typeof ResponsibilityTestPreviewComponent === 'undefined') return false;
    const proto = ResponsibilityTestPreviewComponent.prototype;
    if (!proto || proto.__patternDefTracePatched) return true;

    const originalBuildRows = proto.buildRows;
    const originalBuildColumns = proto.buildColumns;
    if (typeof originalBuildRows !== 'function' || typeof originalBuildColumns !== 'function') return false;

    proto.buildRows = function buildRowsWithPatternDefTrace(...args) {
      const rows = originalBuildRows.apply(this, args);
      const patterns = this?._result?.test_patterns ?? [];
      return (rows ?? []).map(row => {
        const index = Number(row?.__pattern_index);
        const pattern = Number.isInteger(index) ? patterns[index] : null;
        return {
          ...row,
          pattern_def_id: normalizeId(pattern?.pattern_def_id)
        };
      });
    };

    proto.buildColumns = function buildColumnsWithPatternDefTrace(rows=[]) {
      const columns = originalBuildColumns.call(this, rows) ?? [];
      const withoutDuplicate = columns.filter(column => column?.field !== 'pattern_def_id');
      return [
        ...withoutDuplicate,
        { field: 'pattern_def_id', caption: 'Pattern Def ID' }
      ];
    };

    proto.__patternDefTracePatched = true;
    return true;
  }

  function install() {
    const serviceReady = patchPreviewService();
    const componentReady = patchPreviewComponent();

    if (serviceReady && componentReady) {
      globalThis.FrbResponsibilityPatternDefTrace = Object.freeze({
        resolvePatternDefId,
        annotateGeneratedPatterns
      });
      console.info('[Responsibility Preview] Pattern Def Traceを有効化しました');
      return;
    }

    // script読込順の差を吸収。通常はDOMContentLoaded時点で両方定義済み。
    let retry = 0;
    const timer = globalThis.setInterval?.(() => {
      retry += 1;
      const ok = patchPreviewService() && patchPreviewComponent();
      if (ok || retry >= 40) {
        globalThis.clearInterval?.(timer);
        if (ok) {
          globalThis.FrbResponsibilityPatternDefTrace = Object.freeze({
            resolvePatternDefId,
            annotateGeneratedPatterns
          });
          console.info('[Responsibility Preview] Pattern Def Traceを有効化しました');
        } else {
          console.warn('[Responsibility Preview] Pattern Def Traceの初期化対象が見つかりませんでした');
        }
      }
    }, 100);
  }

  if (typeof document !== 'undefined' && document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', install, { once: true });
  } else {
    install();
  }
})();
