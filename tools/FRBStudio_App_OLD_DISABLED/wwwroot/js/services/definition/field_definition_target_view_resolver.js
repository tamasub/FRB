// v0.18.48-field-definition-caption-and-detail-header-spacing
// Resolve a human-facing target ViewDef caption from a canonical Field Definition field_path.
// This is UI-independent so the same resolution can later be reused by Diff/Evidence views.

function normalizeFieldDefinitionTargetPath(raw) {
  const value = String(raw ?? '').trim();
  if (!value) return '';
  return value.replace(/\\/g, '/').replace(/\/+$/, '');
}

function fieldDefinitionTargetSectionBasePath(section={}) {
  let base = normalizeFieldDefinitionTargetPath(section.dataPath ?? section.data_path ?? '$') || '$';
  const type = String(section.type ?? '').trim().toLowerCase();
  if (type === 'grid' && base !== '$' && !base.endsWith('[]')) base += '[]';
  return base;
}

function fieldDefinitionTargetFieldPath(section={}, field={}) {
  const name = String(field.field ?? field.name ?? '').trim();
  if (!name) return '';
  const base = fieldDefinitionTargetSectionBasePath(section);
  if (base === '$') return `$.${name}`;
  return `${base}.${name}`;
}

function buildFieldDefinitionTargetViewCatalog(viewDef={}) {
  const catalog = [];
  const views = Array.isArray(viewDef?.views) ? viewDef.views : [];

  views.forEach(view => {
    const sections = Array.isArray(view?.sections) ? view.sections : [];
    sections.forEach(section => {
      const fields = Array.isArray(section?.fields) ? section.fields : [];
      fields.forEach(field => {
        const fieldPath = fieldDefinitionTargetFieldPath(section, field);
        if (!fieldPath) return;
        catalog.push({
          field_path: fieldPath,
          field: String(field.field ?? field.name ?? ''),
          caption: String(field.caption ?? field.label ?? field.field ?? field.name ?? '').trim(),
          type: String(field.type ?? '').trim(),
          view_id: String(view.id ?? '').trim(),
          view_caption: String(view.caption ?? '').trim(),
          section_id: String(section.id ?? '').trim(),
          section_caption: String(section.caption ?? '').trim()
        });
      });
    });
  });

  return catalog;
}

function resolveFieldDefinitionTargetViewField(viewDef={}, fieldPath='') {
  const target = normalizeFieldDefinitionTargetPath(fieldPath);
  if (!target) return null;
  return buildFieldDefinitionTargetViewCatalog(viewDef).find(item => item.field_path === target) ?? null;
}

globalThis.normalizeFieldDefinitionTargetPath = normalizeFieldDefinitionTargetPath;
globalThis.fieldDefinitionTargetSectionBasePath = fieldDefinitionTargetSectionBasePath;
globalThis.fieldDefinitionTargetFieldPath = fieldDefinitionTargetFieldPath;
globalThis.buildFieldDefinitionTargetViewCatalog = buildFieldDefinitionTargetViewCatalog;
globalThis.resolveFieldDefinitionTargetViewField = resolveFieldDefinitionTargetViewField;
