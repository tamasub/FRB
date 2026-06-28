// v0.4-split: Common field type registry and resolver
// v0.15.2: FieldType enumRef resolver added. Enum is the canonical value vocabulary.

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
  if (n.startsWith('data/json/')) return n.slice('data/json/'.length);
  if (n.startsWith('json/')) return n.slice('json/'.length);
  return n;
}

function normalizeCommonEnumSourceItems(defObj) {
  const raw = defObj?.commonEnumSources ?? defObj?.common_enum_sources ?? defObj?.enumSources ?? defObj?.enum_sources ?? null;
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
  return out;
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
        if (out.sort_order == null && out.sortOrder != null) out.sort_order = out.sortOrder;
        if (out.sort_order == null) out.sort_order = (index + 1) * 10;
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
      mergeFieldTypeRegistry(registry, common);
    } catch (err) {
      // 現行FRBStudio APIは defs/common/foo.json のようなサブフォルダ取得に対応していない構成がある。
      // その場合は basename を defs 直下としてフォールバックする。
      const baseName = item.name.split('/').pop();
      if (baseName && baseName !== item.name) {
        try {
          const common = await fetchApiJson('defs', baseName);
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

async function loadEnumRegistryForViewDef(defObj) {
  const sourceItems = normalizeCommonEnumSourceItems(defObj);
  const cacheKey = sourceItems.map(x => `${x.name}:${x.explicit ? '1' : '0'}`).join('|');
  if (enumRegistryCache.has(cacheKey)) return cloneData(enumRegistryCache.get(cacheKey));

  const registry = emptyEnumRegistry();
  for (const item of sourceItems) {
    try {
      const common = await fetchApiJson('data', item.name);
      mergeEnumRegistry(registry, common);
    } catch (err) {
      const baseName = item.name.split('/').pop();
      if (baseName && baseName !== item.name) {
        try {
          const common = await fetchApiJson('data', baseName);
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

function normalizeFieldTypeObject(typeObj) {
  const out = cloneData(typeObj ?? {});
  if (out.baseType != null && out.type == null) out.type = out.baseType;
  if (out.base_type != null && out.type == null) out.type = out.base_type;
  delete out.baseType;
  delete out.base_type;
  return out;
}

function fieldEnumRef(field) {
  return String(field?.enumRef ?? field?.enum_ref ?? field?.edit?.enumRef ?? field?.edit?.enum_ref ?? '').trim();
}

function fieldEffectiveType(field) {
  return String(field?.type ?? field?.baseType ?? field?.base_type ?? '').trim();
}

function isSelectFieldLike(field) {
  const t = fieldEffectiveType(field);
  return t === 'select' || t === 'radio' || field?.edit?.control === 'radio' || field?.control === 'radio';
}

function enumItemsToOptions(enumObj) {
  return normalizeEnumItems(enumObj?.items ?? []).map(item => {
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

  const out = cloneData(field);
  if (out.enumRef == null) out.enumRef = enumRef;

  if (!isSelectFieldLike(out)) {
    console.warn(`enumRef「${enumRef}」はselect系FieldTypeでのみoptions解決対象です`, out);
    return out;
  }

  const enumObj = findEnum(enumRegistry, enumRef);
  if (!enumObj) {
    console.warn(`Enum「${enumRef}」が見つかりません。既存optionsがあれば互換表示を継続します`, out);
    return out;
  }

  const enumOptions = enumItemsToOptions(enumObj);
  if (!enumOptions.length) {
    console.warn(`Enum「${enumRef}」にitemsがありません。既存optionsがあれば互換表示を継続します`, out);
    return out;
  }

  if (Array.isArray(out.options) && out.options.length) {
    out._local_options_count = out.options.length;
    out._options_source = 'enumRef';
  }
  out.options = enumOptions;
  out.valueField = out.valueField ?? out.value_field ?? 'cd';
  out.labelField = out.labelField ?? out.label_field ?? 'name';
  out.enumRef = enumRef;
  out._resolved_enum_ref = enumRef;
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
  if (!typeRef) return resolveEnumRefForField(field, enumRegistry);

  const typeObj = findFieldType(registry, typeRef);
  if (!typeObj) {
    console.warn(`FieldType「${typeRef}」が見つかりません`, field);
    return resolveEnumRefForField(field, enumRegistry);
  }

  const base = normalizeFieldTypeObject(typeObj);
  const override = cloneData(field);
  if (explicitRef == null && override.type === typeRef) delete override.type;
  const merged = deepMergePlain(base, override);
  merged.fieldType = typeRef;
  return resolveEnumRefForField(merged, enumRegistry);
}

function resolveFieldTypesDeep(obj, registry, enumRegistry=null) {
  if (Array.isArray(obj)) return obj.map(x => resolveFieldTypesDeep(x, registry, enumRegistry));
  if (!obj || typeof obj !== 'object') return obj;

  let current = obj;
  if (current.field || current.fieldType || current.field_type || current.typeRef || current.type_ref || current.enumRef || current.enum_ref) {
    current = resolveFieldTypeForField(current, registry, enumRegistry);
  }

  Object.keys(current).forEach(key => {
    current[key] = resolveFieldTypesDeep(current[key], registry, enumRegistry);
  });
  return current;
}

async function resolveFieldTypesForViewDef(defObj) {
  const registry = await loadFieldTypeRegistryForViewDef(defObj);
  const enumRegistry = await loadEnumRegistryForViewDef(defObj);
  const resolved = resolveFieldTypesDeep(cloneData(defObj), registry, enumRegistry);
  resolved._resolved_common_types = Object.keys(registry.namespaces ?? {});
  resolved._resolved_common_enums = Object.keys(enumRegistry.enumsByRef ?? {});
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
