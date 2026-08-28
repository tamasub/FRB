// v0.18.109-responsibility-generated-test-preview
// UI-independent derivation for Responsibility Definition Driven Test preview.
// Canonical Responsibility JSON stores generation rules; Generated TestPattern / Expected remain derived readonly data.

function responsibilityPreviewClone(value) {
  if (value === undefined) return undefined;
  return JSON.parse(JSON.stringify(value));
}

function responsibilityPreviewPathParts(dataPath) {
  const normalized = String(dataPath ?? '').trim();
  if (!normalized.startsWith('$')) return [];
  return normalized
    .replace(/^\$\.?/, '')
    .split('.')
    .map(part => part.trim())
    .filter(Boolean);
}

function responsibilityPreviewGetByDataPath(root, dataPath) {
  let current = root;
  for (const part of responsibilityPreviewPathParts(dataPath)) {
    if (current == null || typeof current !== 'object') return undefined;
    current = current[part];
  }
  return current;
}

function responsibilityPreviewCanonicalFieldPath(dataPath, fieldName) {
  const root = String(dataPath ?? '').trim().replace(/\[\]$/, '');
  return `${root}[].${String(fieldName ?? '').trim()}`;
}

function responsibilityPreviewFindSection(viewDef, dataPath) {
  const target = String(dataPath ?? '').trim();
  for (const view of (viewDef?.views ?? [])) {
    for (const section of (view?.sections ?? [])) {
      if (String(section?.dataPath ?? '').trim() === target) return section;
    }
  }
  return null;
}

function responsibilityPreviewBoundaryValue(value) {
  if (value && typeof value === 'object' && Object.prototype.hasOwnProperty.call(value, 'value')) return value.value;
  return value;
}

function responsibilityPreviewFormatValue(value) {
  if (value === undefined) return 'undefined';
  try { return JSON.stringify(value); }
  catch { return String(value); }
}

function responsibilityPreviewRotateToken(token) {
  const text = String(token ?? '');
  if (text.length <= 1) return text;
  return text.slice(1) + text[0];
}

function responsibilityPreviewStringReplacement(original, contract, token) {
  const text = String(original ?? '');
  const resolved = contract?.resolved_constraints ?? {};
  const minLength = Number.isInteger(resolved.minimum_length) ? resolved.minimum_length : 0;
  const maxLength = Number.isInteger(resolved.maximum_length) ? resolved.maximum_length : Number.POSITIVE_INFINITY;
  const rawToken = String(token ?? '').trim() || 'TEST';

  // Primary contract: keep TEST-like token at the right edge.
  // Length may grow only when the original is shorter than the shared token/minimum and maxLength allows it.
  const targetLength = Math.min(
    Number.isFinite(maxLength) ? maxLength : Number.MAX_SAFE_INTEGER,
    Math.max(text.length, minLength, Math.min(rawToken.length, Number.isFinite(maxLength) ? maxLength : rawToken.length))
  );
  const suffix = rawToken.slice(0, Math.min(rawToken.length, targetLength));
  const prefixLength = Math.max(0, targetLength - suffix.length);
  let prefix = text.slice(0, prefixLength);
  if (prefix.length < prefixLength) {
    const fillSeed = text || rawToken;
    prefix = (prefix + fillSeed.repeat(Math.ceil((prefixLength - prefix.length) / Math.max(1, fillSeed.length)) + 1)).slice(0, prefixLength);
  }
  let candidate = prefix + suffix;

  // If the original already equals the primary result, derive a deterministic alternate from the same shared token.
  if (candidate === text) {
    const alternate = responsibilityPreviewRotateToken(rawToken);
    const altSuffix = alternate.slice(0, Math.min(alternate.length, targetLength));
    candidate = text.slice(0, Math.max(0, targetLength - altSuffix.length)) + altSuffix;
  }
  return candidate;
}

function responsibilityPreviewAppendMultiline(original, contract, token) {
  const text = String(original ?? '');
  const resolved = contract?.resolved_constraints ?? {};
  const maxLength = Number.isInteger(resolved.maximum_length) ? resolved.maximum_length : Number.POSITIVE_INFINITY;
  const maxLines = Number.isInteger(resolved.maximum_lines) ? resolved.maximum_lines : Number.POSITIVE_INFINITY;
  const rawToken = String(token ?? '').trim() || 'TEST';
  const lineCount = text === '' ? 1 : text.split(/\r\n|\r|\n/).length;
  const append = `${text}${text ? '\n' : ''}${rawToken}`;
  if (lineCount < maxLines && append.length <= maxLength) return append;

  // Fallback keeps the existing line structure but still changes a deterministic suffix.
  return responsibilityPreviewStringReplacement(text, contract, rawToken);
}

function responsibilityPreviewAddDays(value, days) {
  const match = /^(\d{4})-(\d{2})-(\d{2})$/.exec(String(value ?? ''));
  if (!match) return null;
  const date = new Date(Date.UTC(Number(match[1]), Number(match[2]) - 1, Number(match[3])));
  date.setUTCDate(date.getUTCDate() + days);
  return `${date.getUTCFullYear().toString().padStart(4, '0')}-${String(date.getUTCMonth() + 1).padStart(2, '0')}-${String(date.getUTCDate()).padStart(2, '0')}`;
}

function responsibilityPreviewAddLocalMinutes(value, minutes) {
  const match = /^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2})(?::(\d{2}))?$/.exec(String(value ?? ''));
  if (!match) return null;
  const hasSeconds = match[6] !== undefined;
  const date = new Date(Date.UTC(
    Number(match[1]), Number(match[2]) - 1, Number(match[3]),
    Number(match[4]), Number(match[5]), Number(match[6] ?? 0)
  ));
  date.setUTCMinutes(date.getUTCMinutes() + minutes);
  const base = `${date.getUTCFullYear().toString().padStart(4, '0')}-${String(date.getUTCMonth() + 1).padStart(2, '0')}-${String(date.getUTCDate()).padStart(2, '0')}T${String(date.getUTCHours()).padStart(2, '0')}:${String(date.getUTCMinutes()).padStart(2, '0')}`;
  return hasSeconds ? `${base}:${String(date.getUTCSeconds()).padStart(2, '0')}` : base;
}

function responsibilityPreviewAddInstantMinutes(value, minutes) {
  const text = String(value ?? '');
  const match = /^(.*?)(Z|([+-])(\d{2}):(\d{2}))$/.exec(text);
  if (!match) return null;
  const timestamp = Date.parse(text);
  if (Number.isNaN(timestamp)) return null;

  const suffix = match[2];
  let offsetMinutes = 0;
  if (suffix !== 'Z') {
    offsetMinutes = Number(match[4]) * 60 + Number(match[5]);
    if (match[3] === '-') offsetMinutes *= -1;
  }
  const shifted = new Date(timestamp + minutes * 60000 + offsetMinutes * 60000);
  const base = `${shifted.getUTCFullYear().toString().padStart(4, '0')}-${String(shifted.getUTCMonth() + 1).padStart(2, '0')}-${String(shifted.getUTCDate()).padStart(2, '0')}T${String(shifted.getUTCHours()).padStart(2, '0')}:${String(shifted.getUTCMinutes()).padStart(2, '0')}:${String(shifted.getUTCSeconds()).padStart(2, '0')}`;
  return `${base}${suffix}`;
}

class ResponsibilityTestPreviewService {
  constructor({ registry=null, fieldContractResolver=null, valueValidator=null }={}) {
    this.registry = registry;
    this.fieldContractResolver = fieldContractResolver ?? (typeof FieldContractResolver !== 'undefined' ? new FieldContractResolver(registry) : null);
    this.valueValidator = valueValidator ?? (typeof DefinitionValueValidator !== 'undefined' ? new DefinitionValueValidator() : null);
  }

  derive({ responsibility={}, rootDocument={}, inputData={}, viewDef={}, fieldDefinitionDocument={}, registry=null }={}) {
    const effectiveRegistry = registry ?? this.registry;
    const setup = (responsibility?.test_setup ?? []).find(item => item?.setup_id) ?? null;
    const definitions = (responsibility?.test_pattern_definitions ?? []).filter(item => item?.enabled !== false);
    const config = rootDocument?.test_generation_config ?? {};
    const issues = [];

    if (!setup) issues.push({ code: 'TEST_SETUP_REQUIRED', message: 'test_setup is required.' });
    if (!definitions.length) issues.push({ code: 'TEST_PATTERN_DEFINITION_REQUIRED', message: 'enabled test_pattern_definitions are required.' });
    if (!effectiveRegistry) issues.push({ code: 'VALIDATION_TYPE_REGISTRY_REQUIRED', message: 'Validation Type Registry is required.' });
    if (!this.fieldContractResolver) issues.push({ code: 'FIELD_CONTRACT_RESOLVER_REQUIRED', message: 'FieldContractResolver is required.' });
    if (!this.valueValidator) issues.push({ code: 'VALUE_VALIDATOR_REQUIRED', message: 'DefinitionValueValidator is required.' });

    const patterns = [];
    if (!issues.length) {
      definitions.forEach(definition => {
        try {
          patterns.push(this.#derivePattern({ definition, setup, config, inputData, viewDef, fieldDefinitionDocument, registry: effectiveRegistry }));
        } catch (err) {
          issues.push({ code: 'PATTERN_DERIVATION_FAILED', pattern_def_id: definition?.pattern_def_id ?? '', message: String(err?.message ?? err) });
        }
      });
    }

    const mutationCount = patterns.reduce((sum, pattern) => sum + (pattern.mutations?.length ?? 0), 0);
    const invalidMutationCount = patterns.reduce((sum, pattern) => sum + (pattern.mutations ?? []).filter(item => item.validation_outcome !== 'ACCEPT').length, 0);
    const approvalStatus = String(setup?.input_approval_status ?? '').trim().toLowerCase();
    const executionReady = approvalStatus === 'approved' && issues.length === 0 && invalidMutationCount === 0 && patterns.length > 0;

    return {
      schema_version: 'responsibility_generated_test_preview_v0_1',
      status: issues.length ? 'PARTIAL' : 'READY',
      execution_ready: executionReady,
      responsibility_cd: String(responsibility?.responsibility_cd ?? ''),
      setup_id: String(setup?.setup_id ?? ''),
      input_approval_status: approvalStatus || 'unknown',
      expected_def_type: String(responsibility?.guarantees?.[0]?.expected_def_type ?? definitions?.[0]?.expected_def_type ?? ''),
      test_patterns: patterns,
      issues,
      summary: {
        test_pattern_count: patterns.length,
        mutation_count: mutationCount,
        invalid_mutation_count: invalidMutationCount,
        issue_count: issues.length,
        expected_unexpected_diff_count: 0
      }
    };
  }

  #derivePattern({ definition, setup, config, inputData, viewDef, fieldDefinitionDocument, registry }) {
    const dataPath = String(definition?.target_data_path ?? '').trim();
    const rows = responsibilityPreviewGetByDataPath(inputData, dataPath);
    if (!Array.isArray(rows) || rows.length === 0) throw new Error(`Target DataPath must resolve to a non-empty array: ${dataPath}`);

    const rowPosition = String(definition?.row_position ?? '').trim().toUpperCase();
    const rowIndex = rowPosition === 'LAST' ? rows.length - 1 : 0;
    const row = rows[rowIndex];
    if (!row || typeof row !== 'object' || Array.isArray(row)) throw new Error(`Target row is not an object: ${dataPath}[${rowIndex}]`);

    const section = responsibilityPreviewFindSection(viewDef, dataPath);
    if (!section) throw new Error(`ViewDef section not found for DataPath: ${dataPath}`);

    const fieldDefs = Array.isArray(fieldDefinitionDocument?.field_definitions) ? fieldDefinitionDocument.field_definitions : [];
    const fieldDefByPath = new Map(fieldDefs.map(item => [String(item?.field_path ?? '').trim(), item]));
    const keyField = String(section?.keyField ?? '').trim();
    const selectionPolicy = String(definition?.field_selection_policy ?? '').trim();
    const wantMultiline = selectionPolicy === 'EDITABLE_EXPLICIT_MULTILINE';
    const excludeKey = config?.target_selection?.exclude_key_field !== false;
    const excludeReadonly = config?.target_selection?.exclude_readonly !== false;

    const candidates = (section?.fields ?? []).filter(field => {
      const fieldName = String(field?.field ?? '').trim();
      if (!fieldName || !Object.prototype.hasOwnProperty.call(row, fieldName)) return false;
      if (excludeKey && keyField && fieldName === keyField) return false;
      if (excludeReadonly && (field?.readonly === true || field?.edit?.readonly === true || field?.edit?.visible === false)) return false;
      const fieldPath = responsibilityPreviewCanonicalFieldPath(dataPath, fieldName);
      const fieldDef = fieldDefByPath.get(fieldPath);
      if (!fieldDef) return false;
      const isMultiline = String(fieldDef.validation_type ?? '') === 'studio.string.multi_line';
      return wantMultiline ? isMultiline : !isMultiline;
    });

    if (!candidates.length) throw new Error(`No target fields matched ${selectionPolicy}: ${dataPath}`);

    const mutations = candidates.map(field => {
      const fieldName = String(field.field);
      const fieldPath = responsibilityPreviewCanonicalFieldPath(dataPath, fieldName);
      const fieldDef = fieldDefByPath.get(fieldPath);
      const contract = this.fieldContractResolver.resolve(fieldDef, registry);
      const before = responsibilityPreviewClone(row[fieldName]);
      const after = this.#generateDifferentValidValue({ before, field, contract, config, valuePattern: definition?.value_pattern });
      const validation = this.valueValidator.validate(contract, { state: 'VALUE', value: after });
      return {
        field: fieldName,
        field_path: fieldPath,
        actual_path: `${dataPath}[${rowIndex}].${fieldName}`,
        validation_type: String(fieldDef?.validation_type ?? ''),
        value_family: String(contract?.value_family ?? ''),
        before,
        after,
        validation_outcome: String(validation?.outcome ?? 'UNRESOLVED'),
        validation_reason: String(validation?.reason_code ?? '')
      };
    });

    const bad = mutations.filter(item => item.validation_outcome !== 'ACCEPT' || Object.is(item.before, item.after));
    if (bad.length) {
      const detail = bad.map(item => `${item.actual_path}:${item.validation_outcome}/${item.validation_reason}`).join(', ');
      throw new Error(`Generated mutation is not a different valid value: ${detail}`);
    }

    const diffText = mutations.map(item => [
      `(-) ${item.actual_path} = ${responsibilityPreviewFormatValue(item.before)}`,
      `(+) ${item.actual_path} = ${responsibilityPreviewFormatValue(item.after)}`
    ].join('\n')).join('\n');

    return {
      pattern_id: String(definition?.pattern_def_id ?? ''),
      pattern_cd: String(definition?.pattern_cd ?? ''),
      pattern_role: String(definition?.pattern_role ?? ''),
      target_structure: String(definition?.target_structure ?? ''),
      target_data_path: dataPath,
      row_position: rowPosition || 'FIRST',
      row_index: rowIndex,
      value_pattern: String(definition?.value_pattern ?? ''),
      field_selection_policy: selectionPolicy,
      guarantee_id: String(definition?.guarantee_id ?? ''),
      expected_def_type: String(definition?.expected_def_type ?? ''),
      input: {
        setup_id: String(setup?.setup_id ?? ''),
        target_row: `${dataPath}[${rowIndex}]`,
        changes: mutations.map(item => ({ path: item.actual_path, value: responsibilityPreviewClone(item.after) }))
      },
      expected: {
        diff: diffText,
        unexpected_diff_count: 0
      },
      mutations,
      source: {
        input_file: String(setup?.input_file ?? ''),
        view_def_file: String(setup?.view_def_file ?? ''),
        field_definition_file: String(setup?.field_definition_file ?? ''),
        input_approval_status: String(setup?.input_approval_status ?? '')
      }
    };
  }

  #generateDifferentValidValue({ before, field, contract, config, valuePattern }) {
    const family = String(contract?.value_family ?? '');
    const generator = config?.value_generation ?? {};
    const token = String(generator?.string?.replace_suffix_token ?? 'TEST');
    const candidates = [];

    const options = Array.isArray(field?.options)
      ? field.options.map(option => option && typeof option === 'object' ? (option.cd ?? option.value ?? option.id ?? option.name) : option)
      : [];
    if (options.length > 1) {
      const index = options.findIndex(value => Object.is(value, before));
      candidates.push(options[(index >= 0 ? index + 1 : 0) % options.length]);
    }

    if (String(valuePattern ?? '') === 'MULTILINE_DIFFERENT_VALID') {
      candidates.push(responsibilityPreviewAppendMultiline(before, contract, token));
    } else if (family === 'string') {
      candidates.push(responsibilityPreviewStringReplacement(before, contract, token));
    } else if (family === 'integer' || family === 'number' || family === 'float') {
      const numeric = Number(before);
      if (Number.isFinite(numeric)) {
        candidates.push(numeric + 1, numeric - 1);
        const min = responsibilityPreviewBoundaryValue(contract?.resolved_constraints?.minimum);
        const max = responsibilityPreviewBoundaryValue(contract?.resolved_constraints?.maximum);
        if (typeof min === 'number' && typeof max === 'number') {
          const mid = family === 'integer' ? Math.trunc((min + max) / 2) : (min + max) / 2;
          candidates.push(mid);
        }
      }
    } else if (family === 'boolean') {
      candidates.push(!Boolean(before));
    } else if (family === 'date') {
      candidates.push(responsibilityPreviewAddDays(before, 1), responsibilityPreviewAddDays(before, -1));
    } else if (family === 'datetime') {
      candidates.push(responsibilityPreviewAddLocalMinutes(before, 1), responsibilityPreviewAddLocalMinutes(before, -1));
    } else if (family === 'instant') {
      candidates.push(responsibilityPreviewAddInstantMinutes(before, 1), responsibilityPreviewAddInstantMinutes(before, -1));
    }

    for (const candidate of candidates) {
      if (candidate === null || candidate === undefined || Object.is(candidate, before)) continue;
      const validation = this.valueValidator.validate(contract, { state: 'VALUE', value: candidate });
      if (validation?.outcome === 'ACCEPT') return candidate;
    }

    throw new Error(`DIFFERENT_VALID generation failed: ${contract?.field_path ?? ''}`);
  }
}

globalThis.responsibilityPreviewClone = responsibilityPreviewClone;
globalThis.ResponsibilityTestPreviewService = ResponsibilityTestPreviewService;
