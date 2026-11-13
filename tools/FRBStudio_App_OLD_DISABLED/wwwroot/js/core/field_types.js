// v0.4-split: Common field type registry and resolver
// v0.15.2: FieldType enumRef resolver added. Enum is the canonical value vocabulary.
// v0.17.7: common_enums / value_sets are unified as Value Vocabulary Registry instances.

function normalizeCommonTypeSourceItems(defObj) {
  const raw = defObj?.fieldTypeSources ?? defObj?.field_type_sources ?? defObj?.typeSources ?? defObj?.type_sources ?? null;
  const out = [];
  const push = (value, explicit=true) => {
    const n = safeJsonFileName(value);
    if (n) out.push({ name: n, explicit });
  };
  if (Array.isArray(raw)) raw.forEach(x => push(x, true));
  else if (typeof raw === 'string') push(raw, true);

  // スモールスタートでは common_types_v0_1.json を既定の共通語彙ファイルとして読む。
  // 存在しない環境では無視し、既存ViewDefには影響させない。
  if (!out.some(x => x.name === DEFAULT_COMMON_TYPES_FILE)) out.push({ name: DEFAULT_COMMON_TYPES_FILE, explicit: false });
  return out;
}

function normalizeDataJsonApiPath(name) {
  const n = safeJsonFileName(name);
  if (!n) return null;
  // /api/data は data/json を起点にするため、定義側で data/json/ や json/ を含めていてもAPI用相対パスへ正規化する。
  let apiPath = n;
  if (apiPath.startsWith('data/json/')) apiPath = apiPath.slice('data/json/'.length);
  if (apiPath.startsWith('json/')) apiPath = apiPath.slice('json/'.length);

  // v0.18.13-config-folder-path-and-common-data-migration:
  // common_enums は Rules ではなく Studio Core の値語彙Configとして data/json/config へ移行した。
  // 旧ViewDef/旧履歴に残る 00_rules 指定は互換Aliasとして新パスへ寄せる。
  if (apiPath === '00_rules/common_enums_v0_1.json') return 'config/common_enums_v0_1.json';
  return apiPath;
}

function normalizeCommonEnumSourceItems(defObj) {
  // v0.17.7-value-vocabulary-registry-diet:
  // valueVocabularySources is the canonical logical name.
  // commonEnumSources / enumSources remain compatible aliases for Core-era ViewDefs.
  const raw = defObj?.valueVocabularySources ?? defObj?.value_vocabulary_sources ??
    defObj?.commonEnumSources ?? defObj?.common_enum_sources ??
    defObj?.enumSources ?? defObj?.enum_sources ?? null;
  const out = [];
  const push = (value, explicit=true) => {
    const n = normalizeDataJsonApiPath(value);
    if (n) out.push({ name: n, explicit });
  };
  if (Array.isArray(raw)) raw.forEach(x => push(x, true));
  else if (typeof raw === 'string') push(raw, true);

  // v0.15.3.1: Enum正本は /api/data の起点(data/json)からの相対パスで指定する。
  // 存在しない環境では警告に留め、既存options直書きViewDef/FieldTypeの互換性を保つ。
  if (!out.some(x => x.name === DEFAULT_COMMON_ENUMS_FILE)) out.push({ name: DEFAULT_COMMON_ENUMS_FILE, explicit: false });

  // v0.17.7: Overlay側 value_sets は別スキーマではなく、Value Vocabulary Registry の overlay scope 実体。
  // manifest経由で読み込み、Core側 common_enums と同じEnumRegistryへマージする。
  if (typeof studioOverlayValueSetSourceItems === 'function') {
    studioOverlayValueSetSourceItems().forEach(item => {
      if (item?.name && !out.some(x => x.name === item.name)) out.push(item);
    });
  }
  return out;
}


function studioDefinitionSource(kind, path, extra={}) {
  const safePath = safeJsonFileName(path);
  if (!safePath) return null;
  return { kind, path: safePath, ...extra };
}

function annotateFieldTypeRegistrySource(src, source) {
  if (!src || typeof src !== 'object' || Array.isArray(src) || !source) return src;
  const annotateNamespace = (nsObj, nsId) => {
    if (!nsObj || typeof nsObj !== 'object' || Array.isArray(nsObj)) return;
    const group = nsObj.fieldTypes ?? nsObj.field_types;
    if (Array.isArray(group)) {
      group.forEach((typeObj, index) => {
        if (!typeObj || typeof typeObj !== 'object' || Array.isArray(typeObj)) return;
        const typeId = String(typeObj.id ?? typeObj.field_type_id ?? typeObj.name ?? `type_${index + 1}`).trim();
        typeObj._studio_definition_source = { ...source, source_type: 'fieldType', ref: nsId && typeId ? `${nsId}.${typeId}` : typeId };
      });
    } else if (group && typeof group === 'object') {
      Object.entries(group).forEach(([typeId, typeObj]) => {
        if (!typeObj || typeof typeObj !== 'object' || Array.isArray(typeObj)) return;
        typeObj._studio_definition_source = { ...source, source_type: 'fieldType', ref: nsId ? `${nsId}.${typeId}` : typeId };
      });
    }
  };

  if (Array.isArray(src.namespaces)) {
    src.namespaces.forEach((nsObj, index) => annotateNamespace(nsObj, enumNamespaceId(nsObj, `ns_${index + 1}`)));
  } else if (src.namespaces && typeof src.namespaces === 'object') {
    Object.entries(src.namespaces).forEach(([nsId, nsObj]) => annotateNamespace(nsObj, nsId));
  }
  if (src.fieldTypes || src.field_types) annotateNamespace(src, 'core');
  return src;
}

function annotateEnumRegistrySource(src, source) {
  if (!src || typeof src !== 'object' || Array.isArray(src) || !source) return src;
  const annotateEnum = (enumObj, nsId, fallbackId) => {
    if (!enumObj || typeof enumObj !== 'object' || Array.isArray(enumObj)) return;
    const ref = canonicalEnumRef(nsId, enumObj, fallbackId);
    enumObj._studio_definition_source = { ...source, source_type: 'valueVocabulary', ref };
  };
  const annotateNamespace = (nsObj, nsId) => {
    if (!nsObj || typeof nsObj !== 'object' || Array.isArray(nsObj)) return;
    const enums = nsObj.enums;
    if (Array.isArray(enums)) enums.forEach((enumObj, index) => annotateEnum(enumObj, nsId, enumObj?.enum_id ?? enumObj?.id ?? `enum_${index + 1}`));
    else if (enums && typeof enums === 'object') Object.entries(enums).forEach(([enumId, enumObj]) => annotateEnum(enumObj, nsId, enumId));
  };
  if (Array.isArray(src.namespaces)) {
    src.namespaces.forEach((nsObj, index) => annotateNamespace(nsObj, enumNamespaceId(nsObj, `ns_${index + 1}`)));
  } else if (src.namespaces && typeof src.namespaces === 'object') {
    Object.entries(src.namespaces).forEach(([nsId, nsObj]) => annotateNamespace(nsObj, nsId));
  }
  if (Array.isArray(src.enums)) src.enums.forEach((enumObj, index) => {
    const ref = String(enumObj?.enum_ref ?? enumObj?.enumRef ?? '').trim();
    annotateEnum(enumObj, ref.includes('.') ? ref.split('.')[0] : 'studio', enumObj?.enum_id ?? enumObj?.id ?? `enum_${index + 1}`);
  });
  return src;
}

function emptyFieldTypeRegistry() {
  return { namespaces: {} };
}

function emptyEnumRegistry() {
  return { namespaces: {}, enumsByRef: {} };
}

function deepMergePlain(base, override) {
  if (Array.isArray(base) || Array.isArray(override)) return cloneData(override);
  if (
    base && typeof base === 'object' &&
    override && typeof override === 'object'
  ) {
    const out = { ...cloneData(base) };
    Object.keys(override).forEach(key => {
      out[key] = key in out ? deepMergePlain(out[key], override[key]) : cloneData(override[key]);
    });
    return out;
  }
  return cloneData(override);
}

function mergeFieldTypeRegistry(target, src) {
  if (!src || typeof src !== 'object' || Array.isArray(src)) return target;
  if (!target.namespaces) target.namespaces = {};

  const mergeNamespace = (nsName, nsObj) => {
    if (!nsObj || typeof nsObj !== 'object' || Array.isArray(nsObj)) return;
    const dst = target.namespaces[nsName] ?? { fieldTypes: {}, fieldGroups: {}, tableTypes: {}, fileTypes: {} };
    ['fieldTypes', 'field_types', 'fieldGroups', 'field_groups', 'tableTypes', 'table_types', 'fileTypes', 'file_types'].forEach(key => {
      const srcGroup = nsObj[key];
      if (!srcGroup || typeof srcGroup !== 'object' || Array.isArray(srcGroup)) return;
      const normalizedKey = key.replace(/_([a-z])/g, (_, c) => c.toUpperCase());
      dst[normalizedKey] = deepMergePlain(dst[normalizedKey] ?? {}, srcGroup);
    });
    target.namespaces[nsName] = dst;
  };

  Object.entries(src.namespaces ?? {}).forEach(([nsName, nsObj]) => mergeNamespace(nsName, nsObj));

  // ルート直下に fieldTypes がある場合は core 名前空間として扱う。
  if (src.fieldTypes || src.field_types) {
    mergeNamespace('core', { fieldTypes: src.fieldTypes ?? src.field_types });
  }
  return target;
}

function enumNamespaceId(nsObj, fallback) {
  return String(nsObj?.namespace_id ?? nsObj?.namespaceId ?? nsObj?.id ?? fallback ?? '').trim();
}

function enumId(enumObj, fallback) {
  return String(enumObj?.enum_id ?? enumObj?.enumId ?? enumObj?.id ?? fallback ?? '').trim();
}

function canonicalEnumRef(nsId, enumObj, fallbackEnumId=null) {
  const explicit = String(enumObj?.enum_ref ?? enumObj?.enumRef ?? '').trim();
  if (explicit) return explicit;
  const eid = enumId(enumObj, fallbackEnumId);
  return nsId && eid ? `${nsId}.${eid}` : '';
}

function normalizeEnumItems(items) {
  if (!Array.isArray(items)) return [];
  return items
    .filter(item => item != null)
    .map((item, index) => {
      if (item && typeof item === 'object' && !Array.isArray(item)) {
        const out = cloneData(item);
        if (out.cd == null && out.value != null) out.cd = out.value;
        if (out.name == null && out.label != null) out.name = out.label;
        if (out.name == null && out.caption != null) out.name = out.caption;
        if (out.sort_order == null && out.sortOrder != null) out.sort_order = out.sortOrder;
        if (out.sort_order == null) out.sort_order = (index + 1) * 10;
        if (out.deprecated == null) out.deprecated = false;
        return out;
      }
      return { cd: String(item), name: String(item), sort_order: (index + 1) * 10, deprecated: false };
    })
    .sort((a, b) => Number(a.sort_order ?? 999999) - Number(b.sort_order ?? 999999));
}

function registerEnum(target, nsId, enumObj, fallbackEnumId=null) {
  if (!nsId || !enumObj || typeof enumObj !== 'object' || Array.isArray(enumObj)) return;
  const eid = enumId(enumObj, fallbackEnumId);
  const ref = canonicalEnumRef(nsId, enumObj, eid);
  if (!eid || !ref) return;

  const normalized = cloneData(enumObj);
  normalized.enum_id = eid;
  normalized.enum_ref = ref;
  if (normalized.name == null && normalized.caption != null) normalized.name = normalized.caption;
  if (normalized.kind == null) normalized.kind = 'code_list';
  if (normalized.value_type == null && normalized.valueType != null) normalized.value_type = normalized.valueType;
  if (normalized.value_type == null) normalized.value_type = 'string';
  normalized.items = normalizeEnumItems(enumObj.items ?? enumObj.options ?? []);

  if (!target.namespaces[nsId]) target.namespaces[nsId] = { enums: {} };
  target.namespaces[nsId].enums[eid] = normalized;
  target.enumsByRef[ref] = normalized;
}

function mergeEnumRegistry(target, src) {
  if (!src || typeof src !== 'object' || Array.isArray(src)) return target;
  if (!target.namespaces) target.namespaces = {};
  if (!target.enumsByRef) target.enumsByRef = {};

  const namespaces = src.namespaces;
  if (Array.isArray(namespaces)) {
    namespaces.forEach((nsObj, nsIndex) => {
      const nsId = enumNamespaceId(nsObj, nsObj?.name ?? `ns_${nsIndex + 1}`);
      if (!nsId) return;
      const enums = nsObj?.enums;
      if (Array.isArray(enums)) enums.forEach((enumObj, enumIndex) => registerEnum(target, nsId, enumObj, enumObj?.name ?? `enum_${enumIndex + 1}`));
      else if (enums && typeof enums === 'object') Object.entries(enums).forEach(([key, enumObj]) => registerEnum(target, nsId, enumObj, key));
    });
    return target;
  }

  if (namespaces && typeof namespaces === 'object') {
    Object.entries(namespaces).forEach(([nsKey, nsObj]) => {
      const nsId = enumNamespaceId(nsObj, nsKey);
      const enums = nsObj?.enums;
      if (Array.isArray(enums)) enums.forEach((enumObj, enumIndex) => registerEnum(target, nsId, enumObj, enumObj?.name ?? `enum_${enumIndex + 1}`));
      else if (enums && typeof enums === 'object') Object.entries(enums).forEach(([key, enumObj]) => registerEnum(target, nsId, enumObj, key));
    });
  }

  // ルート直下に enums がある場合は、enum_ref があればそれを、なければ studio 名前空間として扱う。
  if (Array.isArray(src.enums)) {
    src.enums.forEach((enumObj, enumIndex) => {
      const ref = String(enumObj?.enum_ref ?? enumObj?.enumRef ?? '').trim();
      const inferredNs = ref.includes('.') ? ref.split('.')[0] : 'studio';
      registerEnum(target, inferredNs, enumObj, enumObj?.name ?? `enum_${enumIndex + 1}`);
    });
  } else if (src.enums && typeof src.enums === 'object') {
    Object.entries(src.enums).forEach(([key, enumObj]) => {
      const ref = String(enumObj?.enum_ref ?? enumObj?.enumRef ?? key ?? '').trim();
      const inferredNs = ref.includes('.') ? ref.split('.')[0] : 'studio';
      registerEnum(target, inferredNs, enumObj, key.includes('.') ? key.split('.').slice(1).join('.') : key);
    });
  }
  return target;
}

async function loadFieldTypeRegistryForViewDef(defObj) {
  const sourceItems = normalizeCommonTypeSourceItems(defObj);
  const cacheKey = sourceItems.map(x => `${x.name}:${x.explicit ? '1' : '0'}`).join('|');
  if (fieldTypeRegistryCache.has(cacheKey)) return cloneData(fieldTypeRegistryCache.get(cacheKey));

  const registry = emptyFieldTypeRegistry();
  for (const item of sourceItems) {
    try {
      const common = await fetchApiJson('defs', item.name);
      annotateFieldTypeRegistrySource(common, studioDefinitionSource('defs', item.name));
      mergeFieldTypeRegistry(registry, common);
    } catch (err) {
      // 現行FRBStudio APIは defs/common/foo.json のようなサブフォルダ取得に対応していない構成がある。
      // その場合は basename を defs 直下としてフォールバックする。
      const baseName = item.name.split('/').pop();
      if (baseName && baseName !== item.name) {
        try {
          const common = await fetchApiJson('defs', baseName);
          annotateFieldTypeRegistrySource(common, studioDefinitionSource('defs', baseName));
          mergeFieldTypeRegistry(registry, common);
          continue;
        } catch {
          // 元エラーで処理する
        }
      }
      if (item.explicit) throw new Error(`共通Type定義JSON「${item.name}」を読み込めません: ${err.message}`);
      console.info(`共通Type定義JSON「${item.name}」は未使用です`, err);
    }
  }

  // ViewDef内に直接 commonTypeRegistry / commonTypes を持たせる将来形も許容する。
  if (defObj?.commonTypeRegistry) mergeFieldTypeRegistry(registry, defObj.commonTypeRegistry);
  if (defObj?.common_type_registry) mergeFieldTypeRegistry(registry, defObj.common_type_registry);
  if (defObj?.commonTypes && typeof defObj.commonTypes === 'object' && !Array.isArray(defObj.commonTypes)) mergeFieldTypeRegistry(registry, defObj.commonTypes);
  if (defObj?.common_types && typeof defObj.common_types === 'object' && !Array.isArray(defObj.common_types)) mergeFieldTypeRegistry(registry, defObj.common_types);

  fieldTypeRegistryCache.set(cacheKey, cloneData(registry));
  return registry;
}


function normalizeFieldGroupSourceItems(defObj) {
  const raw = defObj?.fieldGroupSources ?? defObj?.field_group_sources ?? null;
  const out = [];
  const push = (value, explicit=true) => {
    const n = safeJsonFileName(value);
    if (n) out.push({ name: n, explicit });
  };
  if (Array.isArray(raw)) raw.forEach(x => push(x, true));
  else if (typeof raw === 'string') push(raw, true);

  // v0.18.14-fieldgroup-type-dynamic-switch-expecteddef-viewdef:
  // FieldGroupType は Studio Core のViewDef拡張Configとして defs/config を既定参照にする。
  if (typeof DEFAULT_FIELD_GROUP_TYPES_FILE !== 'undefined' &&
      !out.some(x => x.name === DEFAULT_FIELD_GROUP_TYPES_FILE)) {
    out.push({ name: DEFAULT_FIELD_GROUP_TYPES_FILE, explicit: false });
  }
  return out;
}

async function loadFieldGroupRegistryForViewDef(defObj) {
  const sourceItems = normalizeFieldGroupSourceItems(defObj);
  const cacheKey = sourceItems.map(x => `${x.name}:${x.explicit ? '1' : '0'}`).join('|');
  if (fieldGroupRegistryCache.has(cacheKey)) return cloneData(fieldGroupRegistryCache.get(cacheKey));

  const registry = emptyFieldTypeRegistry();
  for (const item of sourceItems) {
    try {
      const config = await fetchApiJson('defs', item.name);
      mergeFieldTypeRegistry(registry, config);
    } catch (err) {
      const baseName = item.name.split('/').pop();
      if (baseName && baseName !== item.name) {
        try {
          const config = await fetchApiJson('defs', baseName);
          mergeFieldTypeRegistry(registry, config);
          continue;
        } catch {
          // 元エラーで処理する
        }
      }
      if (item.explicit) throw new Error(`FieldGroupType定義JSON「${item.name}」を読み込めません: ${err.message}`);
      console.info(`FieldGroupType定義JSON「${item.name}」は未使用です`, err);
    }
  }

  if (defObj?.fieldGroupRegistry) mergeFieldTypeRegistry(registry, defObj.fieldGroupRegistry);
  if (defObj?.field_group_registry) mergeFieldTypeRegistry(registry, defObj.field_group_registry);
  if (defObj?.fieldGroups && typeof defObj.fieldGroups === 'object' && !Array.isArray(defObj.fieldGroups)) {
    mergeFieldTypeRegistry(registry, { namespaces: { view: { fieldGroups: defObj.fieldGroups } } });
  }
  if (defObj?.field_groups && typeof defObj.field_groups === 'object' && !Array.isArray(defObj.field_groups)) {
    mergeFieldTypeRegistry(registry, { namespaces: { view: { fieldGroups: defObj.field_groups } } });
  }

  fieldGroupRegistryCache.set(cacheKey, cloneData(registry));
  return registry;
}

async function loadEnumRegistryForViewDef(defObj) {
  if (typeof loadStudioOverlayRuntime === 'function') {
    try {
      await loadStudioOverlayRuntime({ status: false });
    } catch (err) {
      console.warn('Studio Overlay manifest の読み込みに失敗しました', err);
    }
  }

  const sourceItems = normalizeCommonEnumSourceItems(defObj);
  const cacheKey = sourceItems.map(x => `${x.name}:${x.explicit ? '1' : '0'}`).join('|');
  if (enumRegistryCache.has(cacheKey)) return cloneData(enumRegistryCache.get(cacheKey));

  const registry = emptyEnumRegistry();
  for (const item of sourceItems) {
    try {
      const common = await fetchApiJson('data', item.name);
      annotateEnumRegistrySource(common, studioDefinitionSource(item.overlay ? 'overlay' : 'data', item.name, { readonly: Boolean(item.overlay) }));
      mergeEnumRegistry(registry, common);
    } catch (err) {
      const baseName = item.name.split('/').pop();
      if (baseName && baseName !== item.name) {
        try {
          const common = await fetchApiJson('data', baseName);
          annotateEnumRegistrySource(common, studioDefinitionSource('data', baseName));
          mergeEnumRegistry(registry, common);
          continue;
        } catch {
          // 元エラーで処理する
        }
      }
      if (item.explicit) throw new Error(`共通Enum定義JSON「${item.name}」を読み込めません: ${err.message}`);
      console.info(`共通Enum定義JSON「${item.name}」は未使用です`, err);
    }
  }

  // ViewDef内に直接 commonEnumRegistry / commonEnums を持たせる将来形も許容する。
  if (defObj?.commonEnumRegistry) mergeEnumRegistry(registry, defObj.commonEnumRegistry);
  if (defObj?.common_enum_registry) mergeEnumRegistry(registry, defObj.common_enum_registry);
  if (defObj?.commonEnums && typeof defObj.commonEnums === 'object' && !Array.isArray(defObj.commonEnums)) mergeEnumRegistry(registry, defObj.commonEnums);
  if (defObj?.common_enums && typeof defObj.common_enums === 'object' && !Array.isArray(defObj.common_enums)) mergeEnumRegistry(registry, defObj.common_enums);

  enumRegistryCache.set(cacheKey, cloneData(registry));
  return registry;
}

function findFieldType(registry, ref) {
  const key = String(ref ?? '').trim();
  if (!key || !registry?.namespaces) return null;
  const dot = key.indexOf('.');
  if (dot > 0) {
    const ns = key.slice(0, dot);
    const name = key.slice(dot + 1);
    return registry.namespaces?.[ns]?.fieldTypes?.[name] ?? null;
  }
  for (const nsObj of Object.values(registry.namespaces)) {
    if (nsObj?.fieldTypes?.[key]) return nsObj.fieldTypes[key];
  }
  return null;
}

function findEnum(enumRegistry, enumRef) {
  const ref = String(enumRef ?? '').trim();
  if (!ref || !enumRegistry) return null;
  if (enumRegistry.enumsByRef?.[ref]) return enumRegistry.enumsByRef[ref];

  const dot = ref.indexOf('.');
  if (dot > 0) {
    const ns = ref.slice(0, dot);
    const id = ref.slice(dot + 1);
    return enumRegistry.namespaces?.[ns]?.enums?.[id] ?? null;
  }

  for (const nsObj of Object.values(enumRegistry.namespaces ?? {})) {
    if (nsObj?.enums?.[ref]) return nsObj.enums[ref];
  }
  return null;
}


function findFieldGroup(registry, ref) {
  const key = String(ref ?? '').trim();
  if (!key || !registry?.namespaces) return null;
  const dot = key.indexOf('.');
  if (dot > 0) {
    const ns = key.slice(0, dot);
    const name = key.slice(dot + 1);
    return registry.namespaces?.[ns]?.fieldGroups?.[name] ?? null;
  }
  for (const nsObj of Object.values(registry.namespaces)) {
    if (nsObj?.fieldGroups?.[key]) return nsObj.fieldGroups[key];
  }
  return null;
}

function fieldGroupRef(field) {
  return String(
    field?.fieldGroupType ?? field?.field_group_type ??
    field?.fieldGroup?.type ?? field?.field_group?.type ??
    field?.fieldGroup?.fieldGroupType ?? field?.field_group?.field_group_type ??
    ''
  ).trim();
}

function isFieldGroupPlaceholder(field) {
  if (!field || typeof field !== 'object' || Array.isArray(field)) return false;
  return field.type === 'fieldGroup' || Boolean(fieldGroupRef(field));
}

function normalizeFieldGroupFields(groupObj) {
  const raw = groupObj?.fields ?? groupObj?.field_defs ?? groupObj?.fieldDefs ?? [];
  return Array.isArray(raw) ? raw.map(cloneData).filter(x => x && typeof x === 'object' && !Array.isArray(x)) : [];
}

function fieldGroupDynamicConfig(groupObj, placeholder) {
  const dynamic = groupObj?.dynamic ?? groupObj?.switch ?? placeholder?.fieldGroup?.dynamic ?? placeholder?.field_group?.dynamic ?? null;
  if (!dynamic || typeof dynamic !== 'object' || Array.isArray(dynamic)) return null;
  const sourceField = String(
    dynamic.sourceField ?? dynamic.source_field ?? dynamic.bindField ?? dynamic.bind_field ??
    placeholder?.fieldGroup?.sourceField ?? placeholder?.field_group?.source_field ?? ''
  ).trim();
  const map = dynamic.map ?? dynamic.mapping ?? dynamic.switchMap ?? dynamic.switch_map ?? {};
  if (!sourceField || !map || typeof map !== 'object' || Array.isArray(map)) return null;
  return {
    sourceField,
    map,
    defaultFieldGroupType: dynamic.defaultFieldGroupType ?? dynamic.default_field_group_type ?? dynamic.default ?? null
  };
}

function mergeVisibleWhenCondition(existing, condition) {
  if (!condition) return existing ? cloneData(existing) : null;
  if (!existing) return cloneData(condition);
  const field = existing.field ?? existing.sourceField ?? condition.field ?? condition.sourceField;
  const values = [];
  const pushValues = (cond) => {
    if (!cond) return;
    if (Array.isArray(cond.in)) values.push(...cond.in);
    else if (Array.isArray(cond.values)) values.push(...cond.values);
    else if (cond.equals != null) values.push(cond.equals);
    else if (cond.value != null) values.push(cond.value);
  };
  pushValues(existing);
  pushValues(condition);
  const uniqueValues = Array.from(new Set(values.map(x => String(x))));
  return uniqueValues.length === 1 ? { field, equals: uniqueValues[0] } : { field, in: uniqueValues };
}

function applyFieldGroupMetadata(field, groupRef, options={}) {
  const out = cloneData(field);
  out._field_group_type = groupRef;
  if (options.placeholderField) out._field_group_placeholder = options.placeholderField;
  if (options.dynamicSourceField) out._field_group_dynamic_source_field = options.dynamicSourceField;
  if (options.dynamicValue != null) out._field_group_dynamic_value = options.dynamicValue;
  if (options.visibleWhen) {
    out.visibleWhen = mergeVisibleWhenCondition(out.visibleWhen ?? out.visible_when, options.visibleWhen);
    out.visible_when = out.visibleWhen;
  }
  return out;
}

function expandStaticFieldGroup(placeholder, groupObj, groupRef) {
  return normalizeFieldGroupFields(groupObj).map(field => applyFieldGroupMetadata(field, groupRef, {
    placeholderField: placeholder?.field
  }));
}

function expandDynamicFieldGroup(placeholder, groupObj, groupRef, registry) {
  const dynamic = fieldGroupDynamicConfig(groupObj, placeholder);
  if (!dynamic) return null;

  const byField = new Map();
  const order = [];
  const entries = Object.entries(dynamic.map ?? {});
  entries.forEach(([dynamicValue, childRefRaw]) => {
    const childRef = String(childRefRaw ?? '').trim();
    if (!childRef) return;
    const childGroup = findFieldGroup(registry, childRef);
    if (!childGroup) {
      console.warn(`FieldGroupType「${childRef}」が見つかりません`, { placeholder, groupRef, dynamicValue });
      return;
    }
    normalizeFieldGroupFields(childGroup).forEach(rawField => {
      if (!rawField?.field) return;
      const condition = { field: dynamic.sourceField, equals: dynamicValue };
      const expanded = applyFieldGroupMetadata(rawField, childRef, {
        placeholderField: placeholder?.field,
        dynamicSourceField: dynamic.sourceField,
        dynamicValue,
        visibleWhen: condition
      });
      const key = String(expanded.field);
      if (!byField.has(key)) {
        byField.set(key, expanded);
        order.push(key);
      } else {
        const current = byField.get(key);
        current.visibleWhen = mergeVisibleWhenCondition(current.visibleWhen ?? current.visible_when, condition);
        current.visible_when = current.visibleWhen;
        current._field_group_type = [current._field_group_type, childRef].filter(Boolean).join(' / ');
        const merged = deepMergePlain(expanded, current);
        merged.visibleWhen = current.visibleWhen;
        merged.visible_when = current.visibleWhen;
        byField.set(key, merged);
      }
    });
  });

  const fields = order.map(key => byField.get(key)).filter(Boolean);
  fields.forEach(field => {
    field._field_group_parent_type = groupRef;
    field._field_group_dynamic_source_field = dynamic.sourceField;
  });
  return fields;
}

function expandFieldGroupPlaceholder(field, registry) {
  const groupRef = fieldGroupRef(field);
  if (!groupRef) return [field];
  const groupObj = findFieldGroup(registry, groupRef);
  if (!groupObj) {
    console.warn(`FieldGroupType「${groupRef}」が見つかりません`, field);
    return [field];
  }

  const dynamicFields = expandDynamicFieldGroup(field, groupObj, groupRef, registry);
  if (dynamicFields) return dynamicFields;
  return expandStaticFieldGroup(field, groupObj, groupRef);
}

function resolveFieldGroupsForViewDef(defObj, registry) {
  const out = cloneData(defObj);
  const views = Array.isArray(out.views) ? out.views : (out.sections ? [out] : []);
  views.forEach(view => {
    (view?.sections ?? []).forEach(section => {
      if (!Array.isArray(section.fields)) return;
      const expanded = [];
      section.fields.forEach(field => {
        if (isFieldGroupPlaceholder(field)) expanded.push(...expandFieldGroupPlaceholder(field, registry));
        else expanded.push(field);
      });
      section.fields = expanded;
    });
  });
  out._resolved_field_group_namespaces = Object.keys(registry?.namespaces ?? {});
  return out;
}

function normalizeFieldTypeObject(typeObj) {
  const out = cloneData(typeObj ?? {});
  if (out.baseType != null && out.type == null) out.type = out.baseType;
  if (out.base_type != null && out.type == null) out.type = out.base_type;
  delete out.baseType;
  delete out.base_type;
  return out;
}

function fieldEnumRef(field) {
  // v0.17.7: enumRef / valueSet are compatible ViewDef aliases.
  // Runtime treats both as Value Vocabulary Ref and resolves them through one options pipeline.
  return String(
    field?.valueVocabularyRef ?? field?.value_vocabulary_ref ??
    field?.valueSet ?? field?.value_set ??
    field?.enumRef ?? field?.enum_ref ??
    field?.edit?.valueVocabularyRef ?? field?.edit?.value_vocabulary_ref ??
    field?.edit?.valueSet ?? field?.edit?.value_set ??
    field?.edit?.enumRef ?? field?.edit?.enum_ref ??
    ''
  ).trim();
}

function fieldVocabularyRefSource(field) {
  if (field?.valueVocabularyRef != null || field?.value_vocabulary_ref != null ||
      field?.edit?.valueVocabularyRef != null || field?.edit?.value_vocabulary_ref != null) return 'valueVocabularyRef';
  if (field?.valueSet != null || field?.value_set != null ||
      field?.edit?.valueSet != null || field?.edit?.value_set != null) return 'valueSet';
  if (field?.enumRef != null || field?.enum_ref != null ||
      field?.edit?.enumRef != null || field?.edit?.enum_ref != null) return 'enumRef';
  return '';
}

function fieldEffectiveType(field) {
  return String(field?.type ?? field?.baseType ?? field?.base_type ?? '').trim();
}

function isSelectFieldLike(field) {
  const t = fieldEffectiveType(field);
  const explicitEditor = String(field?.editor ?? field?.edit?.editor ?? field?.control ?? field?.edit?.control ?? '').trim();

  // v0.17.6-pluginhost-mvp:
  // Plugin Editorや配列Fieldでも valueSet / enumRef を解決できるようにする。
  // これにより、複数選択コンボは会社マスタをPlugin内蔵せず、ValueSetDefからoptionsを受け取れる。
  return t === 'select'
    || t === 'radio'
    || t === 'array'
    || t === 'stringArray'
    || explicitEditor.startsWith('plugin:')
    || field?.edit?.control === 'radio'
    || field?.control === 'radio';
}

function enumItemsToOptions(enumObj) {
  return normalizeEnumItems(enumObj?.items ?? [])
    .filter(item => item?.deprecated !== true)
    .map(item => {
      const out = cloneData(item);
      if (out.cd == null && out.value != null) out.cd = out.value;
      if (out.name == null && out.label != null) out.name = out.label;
      return out;
    });
}

function resolveEnumRefForField(field, enumRegistry) {
  if (!field || typeof field !== 'object' || Array.isArray(field)) return field;
  const enumRef = fieldEnumRef(field);
  if (!enumRef) return field;
  const refSource = fieldVocabularyRefSource(field);

  const out = cloneData(field);
  if (out.enumRef == null && refSource === 'enumRef') out.enumRef = enumRef;
  if (out.valueSet == null && refSource === 'valueSet') out.valueSet = enumRef;
  if (out.valueVocabularyRef == null) out.valueVocabularyRef = enumRef;

  if (!isSelectFieldLike(out)) {
    console.warn(`enumRef「${enumRef}」はselect系FieldTypeでのみoptions解決対象です`, out);
    return out;
  }

  const enumObj = findEnum(enumRegistry, enumRef);
  if (!enumObj) {
    console.warn(`Enum「${enumRef}」が見つかりません。既存optionsがあれば互換表示を継続します`, out);
    return out;
  }

  if (enumObj?._studio_definition_source) {
    out._option_maintenance_source = cloneData(enumObj._studio_definition_source);
  }

  const enumOptions = enumItemsToOptions(enumObj);
  if (!enumOptions.length) {
    console.warn(`Enum「${enumRef}」に有効なitemsがありません。既存optionsがあれば互換表示を継続します`, out);
    return out;
  }

  if (Array.isArray(out.options) && out.options.length) {
    out._local_options_count = out.options.length;
  }
  out._options_source = refSource || 'valueVocabularyRef';
  out.options = enumOptions;
  out.valueField = out.valueField ?? out.value_field ?? 'cd';
  out.labelField = out.labelField ?? out.label_field ?? 'name';
  if (refSource === 'enumRef') out.enumRef = enumRef;
  if (refSource === 'valueSet') out.valueSet = enumRef;
  out.valueVocabularyRef = enumRef;
  out._resolved_enum_ref = enumRef;
  out._resolved_value_vocabulary_ref = enumRef;
  return out;
}

function maybeResolveFieldTypeRefFromType(field, registry) {
  const typeValue = String(field?.type ?? '').trim();
  if (!typeValue || !typeValue.includes('.')) return null;
  return findFieldType(registry, typeValue) ? typeValue : null;
}

function resolveFieldTypeForField(field, registry, enumRegistry=null) {
  if (!field || typeof field !== 'object' || Array.isArray(field)) return field;
  const explicitRef = field.fieldType ?? field.field_type ?? field.typeRef ?? field.type_ref;
  const typeRef = explicitRef ?? maybeResolveFieldTypeRefFromType(field, registry);
  const hasLocalOptions = Array.isArray(field.options);
  if (!typeRef) {
    const resolved = resolveEnumRefForField(field, enumRegistry);
    if (!resolved?._option_maintenance_source && hasLocalOptions) {
      resolved._option_maintenance_source = { kind: 'viewdef', source_type: 'viewDefOptions', field: String(field.field ?? '') };
    }
    return resolved;
  }

  const typeObj = findFieldType(registry, typeRef);
  if (!typeObj) {
    console.warn(`FieldType「${typeRef}」が見つかりません`, field);
    const resolved = resolveEnumRefForField(field, enumRegistry);
    if (!resolved?._option_maintenance_source && hasLocalOptions) {
      resolved._option_maintenance_source = { kind: 'viewdef', source_type: 'viewDefOptions', field: String(field.field ?? '') };
    }
    return resolved;
  }

  const base = normalizeFieldTypeObject(typeObj);
  const override = cloneData(field);
  if (explicitRef == null && override.type === typeRef) delete override.type;
  const merged = deepMergePlain(base, override);
  merged.fieldType = typeRef;
  if (hasLocalOptions) {
    merged._option_maintenance_source = override?._option_maintenance_source
      ? cloneData(override._option_maintenance_source)
      : { kind: 'viewdef', source_type: 'viewDefOptions', field: String(field.field ?? ''), ref: typeRef };
  } else if (typeObj?._studio_definition_source && Array.isArray(typeObj.options)) {
    merged._option_maintenance_source = cloneData(typeObj._studio_definition_source);
  }
  return resolveEnumRefForField(merged, enumRegistry);
}

function resolveFieldTypesDeep(obj, registry, enumRegistry=null, definitionPath='$') {
  if (Array.isArray(obj)) {
    return obj.map((x, index) => resolveFieldTypesDeep(x, registry, enumRegistry, `${definitionPath}[${index}]`));
  }
  if (!obj || typeof obj !== 'object') return obj;

  let current = obj;
  if (current.field || current.fieldType || current.field_type || current.typeRef || current.type_ref || current.enumRef || current.enum_ref) {
    current = resolveFieldTypeForField(current, registry, enumRegistry);
    if (current?._option_maintenance_source?.source_type === 'viewDefOptions') {
      current._option_maintenance_source.node_path = definitionPath;
    }
  }

  Object.keys(current).forEach(key => {
    current[key] = resolveFieldTypesDeep(current[key], registry, enumRegistry, `${definitionPath}.${key}`);
  });
  return current;
}

async function resolveFieldTypesForViewDef(defObj) {
  const registry = await loadFieldTypeRegistryForViewDef(defObj);
  const fieldGroupRegistry = await loadFieldGroupRegistryForViewDef(defObj);
  const enumRegistry = await loadEnumRegistryForViewDef(defObj);
  const expanded = resolveFieldGroupsForViewDef(cloneData(defObj), fieldGroupRegistry);
  const resolved = resolveFieldTypesDeep(expanded, registry, enumRegistry);
  resolved._resolved_common_types = Object.keys(registry.namespaces ?? {});
  resolved._resolved_field_groups = Object.keys(fieldGroupRegistry.namespaces ?? {});
  resolved._resolved_common_enums = Object.keys(enumRegistry.enumsByRef ?? {});
  resolved._resolved_value_vocabulary_refs = Object.keys(enumRegistry.enumsByRef ?? {});
  return resolved;
}

function optionValue(opt, field=null) {
  if (opt && typeof opt === 'object' && !Array.isArray(opt)) {
    const valueField = field?.valueField ?? field?.value_field ?? field?.optionValueField ?? field?.option_value_field ?? 'cd';
    return opt[valueField] ?? opt.cd ?? opt.value ?? opt.id ?? opt.key ?? '';
  }
  return opt;
}

function optionLabel(opt, field=null) {
  if (opt && typeof opt === 'object' && !Array.isArray(opt)) {
    const labelField = field?.labelField ?? field?.label_field ?? field?.optionLabelField ?? field?.option_label_field ?? 'name';
    return opt[labelField] ?? opt.name ?? opt.label ?? opt.caption ?? opt.text ?? opt.cd ?? opt.value ?? '';
  }
  return opt;
}

function optionLabelForValue(value, field=null) {
  const options = field?.options;
  if (!Array.isArray(options)) return value;
  const found = options.find(opt => String(optionValue(opt, field)) === String(value ?? ''));
  return found ? optionLabel(found, field) : value;
}

// v0.16.8-detail-select-preserve-unknown-value:
// Grid表示は候補外の既存値も文字列として表示できるが、HTML select は options に存在しない値を
// value にセットしても空表示になる。既存Dataに候補外値がある場合でも、Detail Editor /
// Document Grid / SubGrid Editor が空表示にならないよう、現在値を一時optionとして保持する。
function selectHasOptionValue(input, value) {
  const normalized = String(value ?? '');
  return Array.from(input?.options ?? []).some(opt => String(opt.value) === normalized);
}

function ensureSelectCurrentValueOption(input, field, value, options={}) {
  if (!input) return;
  const normalized = String(value ?? '');
  if (!normalized) return;
  if (selectHasOptionValue(input, normalized)) return;

  const opt = document.createElement('option');
  opt.value = normalized;
  opt.textContent = String(options.label ?? optionLabelForValue(normalized, field) ?? normalized);
  opt.dataset.runtimeAddedCurrentValue = 'true';
  opt.dataset.reason = 'value-not-in-viewdef-options';
  opt.title = 'ViewDef options に存在しない既存値です';
  input.appendChild(opt);
}

function setSelectValuePreservingUnknown(input, field, value) {
  const normalized = String(value ?? '');
  ensureSelectCurrentValueOption(input, field, normalized);
  input.value = normalized;
}
