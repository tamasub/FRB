// v0.18.55-viewdef-maintenance-all-sections
// ViewDef maintenance projection.
// The maintenance UI edits one flattened temporary field list, while the canonical ViewDef
// keeps fields under their original views[].sections[].fields ownership.
(function installViewDefMaintenanceProjection(){
  const PROJECTION_PATH = '__studio_viewdef_maintenance_fields';
  const MARKER_PATH = '__studio_viewdef_maintenance';
  const SECTION_REF_FIELD = '__maintenance_section_ref';
  const KEY_FIELD = '__maintenance_key';

  function clone(value) {
    if (value == null) return value;
    if (typeof structuredClone === 'function') return structuredClone(value);
    return JSON.parse(JSON.stringify(value));
  }

  function sectionRef(viewIndex, sectionIndex) {
    return `${viewIndex}:${sectionIndex}`;
  }

  function sectionCatalog(targetViewDef={}) {
    const catalog = [];
    const views = Array.isArray(targetViewDef?.views) ? targetViewDef.views : [];
    views.forEach((view, viewIndex) => {
      const sections = Array.isArray(view?.sections) ? view.sections : [];
      sections.forEach((section, sectionIndex) => {
        const viewName = String(view?.caption ?? view?.id ?? `View ${viewIndex + 1}`).trim();
        const sectionName = String(section?.caption ?? section?.id ?? `Section ${sectionIndex + 1}`).trim();
        catalog.push({
          cd: sectionRef(viewIndex, sectionIndex),
          name: `${viewName} / ${sectionName}`,
          view_index: viewIndex,
          section_index: sectionIndex,
          view_id: String(view?.id ?? ''),
          section_id: String(section?.id ?? ''),
          section_type: String(section?.type ?? ''),
          data_path: String(section?.dataPath ?? section?.data_path ?? '$')
        });
      });
    });
    return catalog;
  }

  function preferredDefaultSectionRef(catalog=[]) {
    const firstMainGrid = catalog.find(item => item.view_index === 0 && item.section_type.toLowerCase() === 'grid');
    return firstMainGrid?.cd ?? catalog[0]?.cd ?? '';
  }

  function buildViewDefMaintenanceDocument(targetViewDef={}) {
    const document = clone(targetViewDef ?? {});
    const fields = [];
    const views = Array.isArray(document?.views) ? document.views : [];

    views.forEach((view, viewIndex) => {
      const sections = Array.isArray(view?.sections) ? view.sections : [];
      sections.forEach((section, sectionIndex) => {
        const sectionFields = Array.isArray(section?.fields) ? section.fields : [];
        sectionFields.forEach((field, fieldIndex) => {
          const row = clone(field ?? {});
          row[SECTION_REF_FIELD] = sectionRef(viewIndex, sectionIndex);
          row[KEY_FIELD] = `${viewIndex}:${sectionIndex}:${fieldIndex}:${String(field?.field ?? 'field')}`;
          fields.push(row);
        });
      });
    });

    document[PROJECTION_PATH] = fields;
    document[MARKER_PATH] = {
      version: 'v0.18.55',
      temporary: true,
      purpose: 'Flatten ViewDef fields across all views/sections for Studio maintenance.'
    };
    return document;
  }

  function configureViewDefMaintenanceViewDef(maintenanceViewDef={}, targetViewDef={}) {
    const configured = clone(maintenanceViewDef ?? {});
    const view = configured?.views?.[0];
    const sections = Array.isArray(view?.sections) ? view.sections : [];
    const grid = sections.find(section => section?.id === 'fields') ?? sections.find(section => section?.type === 'grid');
    if (!grid) return configured;

    grid.dataPath = `$.${PROJECTION_PATH}`;
    grid.keyField = KEY_FIELD;

    const catalog = sectionCatalog(targetViewDef);
    const fieldDefs = Array.isArray(grid?.fields) ? grid.fields : [];

    // Keep every type already used by the target selectable even when it is a legacy/extended type.
    const typeField = fieldDefs.find(field => field?.field === 'type');
    if (typeField) {
      const known = Array.isArray(typeField.options) ? typeField.options.map(value => String(value)) : [];
      const used = [];
      (targetViewDef?.views ?? []).forEach(view => (view?.sections ?? []).forEach(section => (section?.fields ?? []).forEach(field => {
        const type = String(field?.type ?? '').trim();
        if (type) used.push(type);
      })));
      typeField.options = [...new Set([...known, ...used])];
      typeField._option_maintenance_source = {
        kind: 'fixed',
        source_type: 'fixed',
        readonly: true,
        reason: 'Studio標準候補と対象ViewDefで既に使用中のtypeから導出した候補です。'
      };
    }

    const sectionField = fieldDefs.find(field => field?.field === SECTION_REF_FIELD);
    if (sectionField) {
      sectionField.options = catalog.map(item => ({ cd: item.cd, name: item.name }));
      sectionField.defaultValue = preferredDefaultSectionRef(catalog);
      sectionField._option_maintenance_source = {
        kind: 'fixed',
        source_type: 'fixed',
        readonly: true,
        reason: 'ViewDefメンテ対象から導出したView / Section候補です。候補自体は対象ViewDefのsectionsで管理します。'
      };
    }
    return configured;
  }

  function parseSectionRef(value) {
    const match = String(value ?? '').trim().match(/^(\d+):(\d+)$/);
    if (!match) return null;
    return { viewIndex: Number(match[1]), sectionIndex: Number(match[2]) };
  }

  function stripMaintenanceMetadata(row={}) {
    const field = clone(row ?? {});
    delete field[SECTION_REF_FIELD];
    delete field[KEY_FIELD];
    return field;
  }

  function finalizeViewDefMaintenanceDocument(maintenanceDocument={}) {
    const result = clone(maintenanceDocument ?? {});
    const projection = Array.isArray(result?.[PROJECTION_PATH]) ? result[PROJECTION_PATH] : null;
    if (!projection) return result;

    const views = Array.isArray(result?.views) ? result.views : [];
    views.forEach(view => {
      const sections = Array.isArray(view?.sections) ? view.sections : [];
      sections.forEach(section => {
        if (Array.isArray(section?.fields)) section.fields = [];
      });
    });

    projection.forEach(row => {
      const ref = parseSectionRef(row?.[SECTION_REF_FIELD]);
      if (!ref) throw new Error(`ViewDefメンテ行のView / Sectionが未指定です: ${String(row?.field ?? '(field未設定)')}`);
      const section = views?.[ref.viewIndex]?.sections?.[ref.sectionIndex];
      if (!section) throw new Error(`ViewDefメンテ行のView / Section参照が不正です: ${row?.[SECTION_REF_FIELD]}`);
      if (!Array.isArray(section.fields)) section.fields = [];
      section.fields.push(stripMaintenanceMetadata(row));
    });

    delete result[PROJECTION_PATH];
    delete result[MARKER_PATH];
    return result;
  }

  function isViewDefMaintenanceDocument(value={}) {
    return Boolean(value && typeof value === 'object' && value[MARKER_PATH]?.temporary === true && Array.isArray(value[PROJECTION_PATH]));
  }

  globalThis.buildViewDefMaintenanceDocument = buildViewDefMaintenanceDocument;
  globalThis.configureViewDefMaintenanceViewDef = configureViewDefMaintenanceViewDef;
  globalThis.finalizeViewDefMaintenanceDocument = finalizeViewDefMaintenanceDocument;
  globalThis.isViewDefMaintenanceDocument = isViewDefMaintenanceDocument;
  globalThis.viewDefMaintenanceSectionCatalog = sectionCatalog;
})();
