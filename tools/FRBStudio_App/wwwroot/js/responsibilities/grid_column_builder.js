// v0.18.7-responsibility-refactor-first-step
// ResponsibilityDef: grid_column_build
// ViewDef fields定義からGrid表示に必要な列定義を生成する薄い責務Interface。
// 既存render/overlay/toolbarの契約を壊さないため、DOM描画は行わず列配列だけを返す。

var GridColumnBuilder = (function () {
  function normalizeField(field) {
    return field && typeof field === 'object' ? field : null;
  }

  function isVisibleInGrid(field) {
    const f = normalizeField(field);
    if (!f) return false;
    return f.grid?.visible !== false;
  }

  function build(viewOrGridDef, options = {}) {
    const fields = Array.isArray(viewOrGridDef?.fields) ? viewOrGridDef.fields : [];
    const includeField = typeof options.includeField === 'function'
      ? options.includeField
      : isVisibleInGrid;

    return fields
      .filter(field => includeField(field, { viewOrGridDef, options }))
      .map(field => field);
  }

  return {
    build,
    isVisibleInGrid
  };
})();
