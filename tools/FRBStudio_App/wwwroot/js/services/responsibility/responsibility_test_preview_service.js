// v0.18.115-responsibility-rule-driven-input-planning
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


function responsibilityPreviewSearchIsBlank(value) {
  return value == null || (typeof value === 'string' && value.trim() === '');
}

function responsibilityPreviewSearchStableValueKey(value) {
  if (value == null) return `${value}`;
  if (typeof value === 'object') {
    try { return JSON.stringify(value); }
    catch { return String(value); }
  }
  return `${typeof value}:${String(value)}`;
}

function responsibilityPreviewSearchRepeatedValue(values) {
  const counts = new Map();
  for (const value of values.filter(v => !responsibilityPreviewSearchIsBlank(v))) {
    const key = responsibilityPreviewSearchStableValueKey(value);
    const current = counts.get(key) ?? { value, count: 0 };
    current.count += 1;
    counts.set(key, current);
  }
  for (const item of counts.values()) if (item.count > 1) return item.value;
  return undefined;
}


function responsibilityPreviewSearchResolveDerivationRule(searchGenerationConfig, operatorId, family) {
  const rules = Array.isArray(searchGenerationConfig?.criteria_derivation_rules)
    ? searchGenerationConfig.criteria_derivation_rules
    : [];
  const op = String(operatorId ?? '').trim();
  const fam = String(family ?? '').trim().toLowerCase();
  const matches = rules.filter(rule => {
    if (String(rule?.status ?? 'active').toLowerCase() !== 'active') return false;
    const applies = rule?.applies_to ?? {};
    const operators = Array.isArray(applies?.operator_ids) ? applies.operator_ids.map(String) : [];
    const families = Array.isArray(applies?.value_families) ? applies.value_families.map(item => String(item).toLowerCase()) : [];
    return operators.includes(op) && (families.includes('*') || families.includes(fam));
  });
  if (matches.length !== 1) {
    throw new Error(
      matches.length === 0
        ? `Search Criteria derivation rule is missing: operator=${op}, family=${fam}. Ruleを追加・ブラッシュアップしてください。`
        : `Search Criteria derivation rule is ambiguous: operator=${op}, family=${fam}, count=${matches.length}`
    );
  }
  return matches[0];
}

function responsibilityPreviewSearchInputProfile(snapshot, family) {
  const rows = Array.isArray(snapshot) ? snapshot : [];
  const nonBlank = rows.filter(item => !responsibilityPreviewSearchIsBlank(item?.value));
  const blank = rows.filter(item => responsibilityPreviewSearchIsBlank(item?.value));
  const counts = new Map();
  for (const item of nonBlank) {
    const key = responsibilityPreviewSearchStableValueKey(item.value);
    const current = counts.get(key) ?? { value: responsibilityPreviewClone(item.value), count: 0, indexes: [], row_ids: [] };
    current.count += 1;
    current.indexes.push(item.index);
    current.row_ids.push(item.row_id);
    counts.set(key, current);
  }
  const repeated = [...counts.values()].filter(item => item.count > 1);
  const comparable = nonBlank
    .map(item => ({
      index: item.index,
      row_id: item.row_id,
      value: responsibilityPreviewClone(item.value),
      comparable: responsibilityPreviewSearchComparable(item.value, family)
    }))
    .filter(item => item.comparable != null)
    .sort((a, b) => a.comparable - b.comparable);

  return {
    row_count: rows.length,
    blank_count: blank.length,
    non_blank_count: nonBlank.length,
    distinct_non_blank_count: counts.size,
    repeated_non_blank_values: repeated,
    comparable_values: comparable
  };
}

function responsibilityPreviewSearchTraceSourceRows(snapshot, value) {
  const key = responsibilityPreviewSearchStableValueKey(value);
  return (snapshot ?? [])
    .filter(item => responsibilityPreviewSearchStableValueKey(item?.value) === key)
    .map(item => ({ index: item.index, row_id: item.row_id, value: responsibilityPreviewClone(item.value) }));
}

function responsibilityPreviewSearchComparable(value, family) {
  if (responsibilityPreviewSearchIsBlank(value)) return null;
  if (['number', 'integer', 'float', 'decimal'].includes(family)) {
    const n = typeof value === 'number' ? value : Number(String(value).replace(/,/g, '').trim());
    return Number.isFinite(n) ? n : null;
  }
  if (family === 'date') {
    const text = String(value).trim();
    return /^\d{4}-\d{2}-\d{2}$/.test(text) ? Date.parse(`${text}T00:00:00Z`) : null;
  }
  if (family === 'datetime') {
    const text = String(value).trim();
    const normalized = /Z|[+-]\d{2}:\d{2}$/.test(text) ? text : `${text}Z`;
    const timestamp = Date.parse(normalized);
    return Number.isFinite(timestamp) ? timestamp : null;
  }
  if (family === 'instant') {
    const timestamp = Date.parse(String(value).trim());
    return Number.isFinite(timestamp) ? timestamp : null;
  }
  return null;
}


function responsibilityPreviewSearchRequirementEvidence({ requirement, snapshot, family, criteria, trace }) {
  const rows = Array.isArray(snapshot) ? snapshot : [];
  const profile = trace?.input_profile ?? responsibilityPreviewSearchInputProfile(rows, family);
  const kind = String(requirement?.kind ?? '').trim();
  const minimum = Number(requirement?.minimum ?? 0);
  const selectedRows = Array.isArray(trace?.selected_source_rows) ? trace.selected_source_rows : [];
  const comparable = Array.isArray(profile?.comparable_values) ? profile.comparable_values : [];
  const comparableDistinct = new Set(comparable.map(item => String(item?.comparable))).size;
  const valueComparable = responsibilityPreviewSearchComparable(criteria?.value, family);
  const fromComparable = responsibilityPreviewSearchComparable(criteria?.from, family);
  const toComparable = responsibilityPreviewSearchComparable(criteria?.to, family);

  let actual = 0;
  let evidence = '';

  if (kind === 'ROW_COUNT_MIN') {
    actual = rows.length;
    evidence = `rows=${actual}`;
  } else if (kind === 'NON_BLANK_MIN') {
    actual = Number(profile?.non_blank_count ?? 0);
    evidence = `nonBlank=${actual}`;
  } else if (kind === 'DISTINCT_NON_BLANK_MIN') {
    actual = Number(profile?.distinct_non_blank_count ?? 0);
    evidence = `distinctNonBlank=${actual}`;
  } else if (kind === 'COMPARABLE_MIN') {
    actual = comparable.length;
    evidence = `comparable=${actual}`;
  } else if (kind === 'DISTINCT_COMPARABLE_MIN') {
    actual = comparableDistinct;
    evidence = `distinctComparable=${actual}`;
  } else if (kind === 'REPEATED_SELECTED_MIN_OCCURRENCES') {
    actual = selectedRows.length;
    evidence = `selectedOccurrences=${actual}`;
  } else if (kind === 'CONTAINS_VARIANT_FOR_SELECTED_MIN') {
    if (criteria && Object.prototype.hasOwnProperty.call(criteria, 'value')) {
      const needle = String(criteria.value ?? '').toLowerCase();
      actual = rows.filter(item => {
        const text = String(item?.value ?? '').toLowerCase();
        return needle !== '' && text !== needle && text.includes(needle);
      }).length;
    }
    evidence = `partialContainsVariant=${actual}`;
  } else if (kind === 'LOWER_THAN_SELECTED_MIN') {
    actual = valueComparable == null ? 0 : comparable.filter(item => item.comparable < valueComparable).length;
    evidence = `lowerThanSelected=${actual}`;
  } else if (kind === 'HIGHER_THAN_SELECTED_MIN') {
    actual = valueComparable == null ? 0 : comparable.filter(item => item.comparable > valueComparable).length;
    evidence = `higherThanSelected=${actual}`;
  } else if (kind === 'REPEATED_FROM_MIN_OCCURRENCES') {
    if (fromComparable != null) actual = comparable.filter(item => item.comparable === fromComparable).length;
    evidence = `fromOccurrences=${actual}`;
  } else if (kind === 'LOWER_THAN_FROM_MIN') {
    actual = fromComparable == null ? 0 : comparable.filter(item => item.comparable < fromComparable).length;
    evidence = `lowerThanFrom=${actual}`;
  } else if (kind === 'HIGHER_THAN_TO_MIN') {
    actual = toComparable == null ? 0 : comparable.filter(item => item.comparable > toComparable).length;
    evidence = `higherThanTo=${actual}`;
  } else {
    return {
      supported: false,
      actual: null,
      minimum,
      evidence: `unsupported kind=${kind}`
    };
  }

  return { supported: true, actual, minimum, evidence };
}

function responsibilityPreviewSearchEvaluateInputRequirements({ rule, snapshot, family, criteria=null, trace=null }) {
  const requirements = Array.isArray(rule?.input_requirement_rules) ? rule.input_requirement_rules : [];
  const effectiveTrace = trace ?? {
    input_profile: responsibilityPreviewSearchInputProfile(snapshot, family),
    selected_source_rows: []
  };
  const evaluations = requirements.map(requirement => {
    const evidence = responsibilityPreviewSearchRequirementEvidence({
      requirement, snapshot, family, criteria, trace: effectiveTrace
    });
    const severity = String(requirement?.severity ?? 'required').toLowerCase();
    const pass = evidence.supported && Number(evidence.actual) >= Number(evidence.minimum);
    return {
      requirement_id: String(requirement?.requirement_id ?? ''),
      severity,
      kind: String(requirement?.kind ?? ''),
      statement: String(requirement?.statement ?? ''),
      minimum: Number(evidence.minimum ?? 0),
      actual: evidence.actual,
      evidence: evidence.evidence,
      status: pass ? 'PASS' : (severity === 'required' ? 'MISSING_REQUIRED' : 'MISSING_RECOMMENDED')
    };
  });

  const missingRequired = evaluations.filter(item => item.status === 'MISSING_REQUIRED');
  const missingRecommended = evaluations.filter(item => item.status === 'MISSING_RECOMMENDED');
  return {
    status: missingRequired.length
      ? 'GENERATION_REQUIRED'
      : missingRecommended.length
        ? 'AUGMENTATION_RECOMMENDED'
        : 'READY',
    generation_needed: missingRequired.length > 0,
    augmentation_recommended: missingRecommended.length > 0,
    required_count: evaluations.filter(item => item.severity === 'required').length,
    recommended_count: evaluations.filter(item => item.severity !== 'required').length,
    missing_required_count: missingRequired.length,
    missing_recommended_count: missingRecommended.length,
    requirements: evaluations
  };
}

function responsibilityPreviewBuildAiInputGenerationRequest({
  setup, dataPath, fieldName, fieldPath, family, snapshot, rule, requirementEvaluation
}) {
  const missing = (requirementEvaluation?.requirements ?? []).filter(item => item.status !== 'PASS');
  const status = requirementEvaluation?.generation_needed
    ? 'REQUIRED'
    : requirementEvaluation?.augmentation_recommended
      ? 'OPTIONAL_AUGMENTATION'
      : 'NOT_REQUIRED';
  return {
    status,
    action: status === 'NOT_REQUIRED' ? 'KEEP_CURRENT_INPUT' : 'CREATE_OR_AUGMENT_TEST_INPUT_DRAFT',
    target_input_file: String(setup?.input_file ?? ''),
    target_data_path: String(dataPath ?? ''),
    target_field: String(fieldName ?? ''),
    field_path: String(fieldPath ?? ''),
    value_family: String(family ?? ''),
    source_rule_id: String(rule?.rule_id ?? ''),
    source_rule_statement: String(rule?.statement ?? ''),
    missing_requirements: responsibilityPreviewClone(missing),
    current_input_snapshot: responsibilityPreviewClone(snapshot),
    constraints: [
      '不足Requirementを満たす最小限のInput Draftを作る。',
      '対象Field以外の既存値、Key、Row順は原則として維持する。',
      '既存行の補強で足りない場合だけ行追加を提案する。',
      'Field Definition / ViewDefの型・制約に違反する値を作らない。',
      'Expectedやテスト理由をTest Input JSONへ埋め込まない。',
      '生成物はdraftとし、approvedへ自動変更しない。'
    ],
    approval_gate: {
      generated_status: 'draft',
      human_review_required: true,
      execution_requires: 'approved'
    }
  };
}

function responsibilityPreviewBuildSearchInputGenerationPlan(patterns, setup) {
  const cases = (patterns ?? []).flatMap(pattern => Array.isArray(pattern?.generated_cases) ? pattern.generated_cases : []);
  const byField = new Map();
  for (const item of cases) {
    const key = String(item?.field_path ?? `${item?.target_data_path ?? ''}.${item?.target_field ?? ''}`);
    let field = byField.get(key);
    if (!field) {
      field = {
        field_path: key,
        target_data_path: String(item?.target_data_path ?? ''),
        target_field: String(item?.target_field ?? ''),
        value_family: String(item?.resolved_value_family ?? item?.value_family ?? ''),
        generation_needed: false,
        augmentation_recommended: false,
        missing_required: [],
        missing_recommended: [],
        rule_ids: []
      };
      byField.set(key, field);
    }
    const evaluation = item?.input_requirement_evaluation ?? {};
    field.generation_needed ||= evaluation?.generation_needed === true;
    field.augmentation_recommended ||= evaluation?.augmentation_recommended === true;
    for (const requirement of (evaluation?.requirements ?? [])) {
      const target = requirement?.status === 'MISSING_REQUIRED'
        ? field.missing_required
        : requirement?.status === 'MISSING_RECOMMENDED'
          ? field.missing_recommended
          : null;
      if (target && !target.some(existing => existing.requirement_id === requirement.requirement_id)) {
        target.push(responsibilityPreviewClone(requirement));
      }
    }
    const ruleId = String(item?.criteria_derivation?.rule_id ?? '');
    if (ruleId && !field.rule_ids.includes(ruleId)) field.rule_ids.push(ruleId);
  }

  const fields = [...byField.values()].map(field => ({
    ...field,
    status: field.generation_needed
      ? 'GENERATION_REQUIRED'
      : field.augmentation_recommended
        ? 'AUGMENTATION_RECOMMENDED'
        : 'READY'
  }));
  return {
    policy: 'RULE_DRIVEN_AI_DRAFT_HUMAN_APPROVAL',
    input_file: String(setup?.input_file ?? ''),
    current_input_approval_status: String(setup?.input_approval_status ?? ''),
    human_approval_required: true,
    approval_flow: ['RULE', 'INPUT_REQUIREMENT_EVALUATION', 'AI_DRAFT_IF_REQUIRED', 'HUMAN_REVIEW', 'approved', 'GENERATED_CASE', 'RUNNER'],
    generation_needed: fields.some(field => field.generation_needed),
    augmentation_recommended: fields.some(field => field.augmentation_recommended),
    fields
  };
}


function responsibilityPreviewSearchEquals(actual, expected, family) {
  if (['number', 'integer', 'float', 'decimal', 'date', 'datetime', 'instant'].includes(family)) {
    const a = responsibilityPreviewSearchComparable(actual, family);
    const b = responsibilityPreviewSearchComparable(expected, family);
    return a != null && b != null && a === b;
  }
  if (family === 'boolean') return String(actual ?? '').toLowerCase() === String(expected ?? '').toLowerCase();
  return String(actual ?? '') === String(expected ?? '');
}

function responsibilityPreviewSearchMatches(actual, operatorId, criteria, family) {
  if (operatorId === 'blank') return responsibilityPreviewSearchIsBlank(actual);
  if (operatorId === 'not_blank') return !responsibilityPreviewSearchIsBlank(actual);
  if (operatorId === 'contains') return String(actual ?? '').toLowerCase().includes(String(criteria?.value ?? '').toLowerCase());
  if (operatorId === 'not_contains') return !String(actual ?? '').toLowerCase().includes(String(criteria?.value ?? '').toLowerCase());
  if (operatorId === 'equals') return responsibilityPreviewSearchEquals(actual, criteria?.value, family);
  if (operatorId === 'not_equals') return !responsibilityPreviewSearchEquals(actual, criteria?.value, family);
  if (operatorId === 'gte' || operatorId === 'lte') {
    const a = responsibilityPreviewSearchComparable(actual, family);
    const b = responsibilityPreviewSearchComparable(criteria?.value, family);
    if (a == null || b == null) return false;
    return operatorId === 'gte' ? a >= b : a <= b;
  }
  if (operatorId === 'between') {
    const a = responsibilityPreviewSearchComparable(actual, family);
    if (a == null) return false;
    const from = responsibilityPreviewSearchComparable(criteria?.from, family);
    const to = responsibilityPreviewSearchComparable(criteria?.to, family);
    if (from != null && a < from) return false;
    if (to != null && a > to) return false;
    return from != null || to != null;
  }
  return false;
}

function responsibilityPreviewSearchPatternFamily(operatorSetId, rawFamily) {
  if (operatorSetId === 'text_standard') return 'string';
  if (operatorSetId === 'numeric_standard') return 'number';
  if (operatorSetId === 'date_standard') return 'date';
  if (operatorSetId === 'boolean_standard') return 'boolean';
  if (operatorSetId === 'select_standard') return 'select';
  return String(rawFamily ?? 'unknown');
}


function responsibilityPreviewAggregateToFiniteNumber(value) {
  if (typeof value === 'number') return Number.isFinite(value) ? value : null;
  if (typeof value !== 'string') return null;
  const text = value.trim();
  if (!text) return null;
  const parsed = Number(text.replace(/,/g, ''));
  return Number.isFinite(parsed) ? parsed : null;
}

function responsibilityPreviewAggregateMetrics(metricSet) {
  const id = String(metricSet ?? '').trim().toUpperCase();
  if (id === 'VALUE') return ['value'];
  if (id === 'VALUE_SOURCE_COUNT') return ['value', 'source_count'];
  if (id === 'VALUE_VALID_IGNORED') return ['value', 'valid_count', 'ignored_count'];
  if (id === 'HAS_AGGREGATES') return ['has_aggregates'];
  throw new Error(`Unsupported aggregate expected_metric_set: ${metricSet}`);
}


function responsibilityPreviewCsvEscapeCell(value) {
  const text = String(value ?? '');
  if (/[",\r\n]/.test(text)) return '"' + text.replace(/"/g, '""') + '"';
  return text;
}

function responsibilityPreviewCsvVisibleFields(section) {
  const fields = (section?.fields ?? []).filter(field => field?.grid?.visible !== false);
  const keyField = String(section?.keyField ?? section?.key_field ?? '').trim();
  const out = [];
  const seen = new Set();
  const push = (field) => {
    const fieldName = String(field?.field ?? '').trim();
    if (!fieldName || seen.has(fieldName)) return;
    seen.add(fieldName);
    out.push(field);
  };
  if (keyField && !fields.some(field => String(field?.field ?? '').trim() === keyField)) {
    push((section?.fields ?? []).find(field => String(field?.field ?? '').trim() === keyField)
      ?? { field: keyField, caption: keyField, type: 'text' });
  }
  fields.forEach(push);
  return out;
}

function responsibilityPreviewCsvValue(row, field) {
  const fieldName = String(field?.field ?? '').trim();
  const value = row?.[fieldName];
  if (value == null) return '';
  if (typeof value === 'object') return JSON.stringify(value);
  return String(value);
}

function responsibilityPreviewBuildCsvExpected({ rows, section, selectedIndexes }) {
  const fields = responsibilityPreviewCsvVisibleFields(section);
  const fieldNames = fields.map(field => String(field?.field ?? '').trim());
  const selectedRows = selectedIndexes.map(index => rows[index]).filter(row => row !== undefined);
  const header = fieldNames.map(responsibilityPreviewCsvEscapeCell).join(',');
  const body = selectedRows.map(row =>
    fields.map(field => responsibilityPreviewCsvEscapeCell(responsibilityPreviewCsvValue(row, field))).join(',')
  );
  const csvWithoutBom = [header, ...body].join('\r\n') + '\r\n';
  return {
    field_names: fieldNames,
    has_bom: true,
    csv_text: '\ufeff' + csvWithoutBom,
    csv_without_bom: csvWithoutBom
  };
}

class ResponsibilityTestPreviewService {
  constructor({ registry=null, fieldContractResolver=null, valueValidator=null }={}) {
    this.registry = registry;
    this.fieldContractResolver = fieldContractResolver ?? (typeof FieldContractResolver !== 'undefined' ? new FieldContractResolver(registry) : null);
    this.valueValidator = valueValidator ?? (typeof DefinitionValueValidator !== 'undefined' ? new DefinitionValueValidator() : null);
  }

  derive({ responsibility={}, rootDocument={}, inputData={}, viewDef={}, fieldDefinitionDocument={}, registry=null, searchOperatorRegistry=null }={}) {
    const effectiveRegistry = registry ?? this.registry;
    const setup = (responsibility?.test_setup ?? []).find(item => item?.setup_id) ?? null;
    const definitions = (responsibility?.test_pattern_definitions ?? []).filter(item => item?.enabled !== false);
    const searchDefinitions = definitions.filter(item => String(item?.generation_mode ?? '') === 'SEARCH_OPERATOR_MATRIX');
    const aggregateDefinitions = definitions.filter(item => String(item?.generation_mode ?? '') === 'AGGREGATE_SCALAR_CASE');
    const csvDefinitions = definitions.filter(item => String(item?.generation_mode ?? '') === 'CSV_EXPORT_CASE');
    const mutationDefinitions = definitions.filter(item => {
      const mode = String(item?.generation_mode ?? '');
      return mode !== 'SEARCH_OPERATOR_MATRIX' && mode !== 'AGGREGATE_SCALAR_CASE' && mode !== 'CSV_EXPORT_CASE';
    });
    const config = rootDocument?.test_generation_config ?? {};
    const issues = [];
    const guaranteeIds = new Set((responsibility?.guarantees ?? []).map(item => String(item?.guarantee_id ?? '').trim()).filter(Boolean));

    if (!setup) issues.push({ code: 'TEST_SETUP_REQUIRED', message: 'test_setup is required.' });
    if (!definitions.length) issues.push({ code: 'TEST_PATTERN_DEFINITION_REQUIRED', message: 'enabled test_pattern_definitions are required.' });
    const needsFieldContract = mutationDefinitions.length > 0 || searchDefinitions.length > 0;
    if (needsFieldContract && !effectiveRegistry) issues.push({ code: 'VALIDATION_TYPE_REGISTRY_REQUIRED', message: 'Validation Type Registry is required.' });
    if (needsFieldContract && !this.fieldContractResolver) issues.push({ code: 'FIELD_CONTRACT_RESOLVER_REQUIRED', message: 'FieldContractResolver is required.' });
    if (mutationDefinitions.length && !this.valueValidator) issues.push({ code: 'VALUE_VALIDATOR_REQUIRED', message: 'DefinitionValueValidator is required.' });
    if (searchDefinitions.length && !searchOperatorRegistry) issues.push({ code: 'SEARCH_OPERATOR_REGISTRY_REQUIRED', message: 'Search Operator Registry is required.' });

    for (const definition of definitions) {
      const guaranteeId = String(definition?.guarantee_id ?? '').trim();
      if (!guaranteeId) {
        issues.push({
          code: 'TEST_PATTERN_GUARANTEE_REQUIRED',
          pattern_def_id: String(definition?.pattern_def_id ?? ''),
          message: 'Each TestPattern definition must belong to exactly one guarantee_id.'
        });
      } else if (!guaranteeIds.has(guaranteeId)) {
        issues.push({
          code: 'TEST_PATTERN_GUARANTEE_NOT_FOUND',
          pattern_def_id: String(definition?.pattern_def_id ?? ''),
          guarantee_id: guaranteeId,
          message: `TestPattern guarantee_id was not found in responsibility guarantees: ${guaranteeId}`
        });
      }
      if (Array.isArray(definition?.guarantee_ids)) {
        issues.push({
          code: 'TEST_PATTERN_MULTI_GUARANTEE_NOT_ALLOWED',
          pattern_def_id: String(definition?.pattern_def_id ?? ''),
          message: 'Use singular guarantee_id. A TestPattern must not belong to multiple guarantees.'
        });
      }
    }

    const patterns = [];
    if (!issues.length) {
      mutationDefinitions.forEach(definition => {
        try {
          patterns.push(this.#derivePattern({ definition, setup, config, inputData, viewDef, fieldDefinitionDocument, registry: effectiveRegistry }));
        } catch (err) {
          issues.push({ code: 'PATTERN_DERIVATION_FAILED', pattern_def_id: definition?.pattern_def_id ?? '', message: String(err?.message ?? err) });
        }
      });

      if (searchDefinitions.length) {
        try {
          patterns.push(...this.#deriveSearchPatterns({
            definitions: searchDefinitions, setup, config, inputData, viewDef, fieldDefinitionDocument,
            registry: effectiveRegistry, searchOperatorRegistry
          }));
        } catch (err) {
          issues.push({ code: 'SEARCH_PATTERN_DERIVATION_FAILED', message: String(err?.message ?? err) });
        }
      }


      if (aggregateDefinitions.length) {
        try {
          patterns.push(...this.#deriveAggregatePatterns({ definitions: aggregateDefinitions, setup, inputData, viewDef }));
        } catch (err) {
          issues.push({ code: 'AGGREGATE_PATTERN_DERIVATION_FAILED', message: String(err?.message ?? err) });
        }
      }


      if (csvDefinitions.length) {
        try {
          patterns.push(...this.#deriveCsvPatterns({ definitions: csvDefinitions, setup, inputData, viewDef }));
        } catch (err) {
          issues.push({ code: 'CSV_PATTERN_DERIVATION_FAILED', message: String(err?.message ?? err) });
        }
      }
    }

    const blockedSearchCases = patterns
      .filter(pattern => String(pattern?.generation_mode ?? '') === 'SEARCH_OPERATOR_MATRIX')
      .flatMap(pattern => Array.isArray(pattern?.generated_cases) ? pattern.generated_cases : [])
      .filter(item => String(item?.generation_status ?? '') === 'INPUT_GENERATION_REQUIRED');
    blockedSearchCases.forEach(item => {
      issues.push({
        code: 'SEARCH_INPUT_GENERATION_REQUIRED',
        case_id: String(item?.case_id ?? ''),
        field_path: String(item?.field_path ?? ''),
        rule_id: String(item?.criteria_derivation?.rule_id ?? ''),
        message: `RuleのRequired Input条件が不足しています。AI Input Draftを生成し、人間承認後に再実行してください: ${item?.field_path ?? ''}`
      });
    });

    const inputGenerationPlan = searchDefinitions.length
      ? responsibilityPreviewBuildSearchInputGenerationPlan(patterns, setup)
      : null;

    const mutationCount = patterns.reduce((sum, pattern) => sum + (pattern.mutations?.length ?? 0), 0);
    const generatedCaseCount = patterns.reduce((sum, pattern) => sum + (pattern.generated_cases?.length ?? 0), 0);
    const invalidMutationCount = patterns.reduce((sum, pattern) => sum + (pattern.mutations ?? []).filter(item => item.validation_outcome !== 'ACCEPT').length, 0);
    const approvalStatus = String(setup?.input_approval_status ?? '').trim().toLowerCase();
    const executionReady = approvalStatus === 'approved' && issues.length === 0 && invalidMutationCount === 0 && patterns.length > 0;

    return {
      schema_version: 'responsibility_generated_test_preview_v0_2',
      status: issues.length ? 'PARTIAL' : 'READY',
      execution_ready: executionReady,
      responsibility_cd: String(responsibility?.responsibility_cd ?? ''),
      setup_id: String(setup?.setup_id ?? ''),
      input_approval_status: approvalStatus || 'unknown',
      expected_def_type: String(patterns?.[0]?.expected_def_type ?? definitions?.[0]?.expected_def_type ?? ''),
      input_generation_plan: responsibilityPreviewClone(inputGenerationPlan),
      test_patterns: patterns,
      issues,
      summary: {
        test_pattern_count: patterns.length,
        generated_case_count: generatedCaseCount,
        mutation_count: mutationCount,
        invalid_mutation_count: invalidMutationCount,
        issue_count: issues.length,
        expected_unexpected_diff_count: 0
      }
    };
  }

  #deriveCsvPatterns({ definitions, setup, inputData, viewDef }) {
    return definitions.map(definition => {
      const dataPath = String(definition?.target_data_path ?? '').trim();
      const rows = responsibilityPreviewGetByDataPath(inputData, dataPath);
      if (!Array.isArray(rows) || rows.length === 0) throw new Error(`CSV Target DataPath must resolve to a non-empty array: ${dataPath}`);
      const section = responsibilityPreviewFindSection(viewDef, dataPath);
      if (!section) throw new Error(`CSV ViewDef section not found for DataPath: ${dataPath}`);

      const rowScope = String(definition?.row_scope ?? 'ALL').trim().toUpperCase();
      const requestedFilteredIndexes = Array.isArray(definition?.filtered_row_indexes)
        ? definition.filtered_row_indexes.filter(index => Number.isInteger(index) && index >= 0 && index < rows.length)
        : [];
      const selectedIndexes = rowScope === 'FILTERED'
        ? requestedFilteredIndexes
        : rows.map((_, index) => index);
      if (rowScope === 'FILTERED' && !selectedIndexes.length) {
        throw new Error(`CSV FILTERED pattern requires filtered_row_indexes: ${definition?.pattern_def_id ?? ''}`);
      }

      const keyField = String(section?.keyField ?? '').trim();
      const selectedSet = new Set(selectedIndexes);
      const snapshot = rows.map((row, index) => ({
        index,
        row_id: keyField && row?.[keyField] != null ? String(row[keyField]) : String(index),
        selected: selectedSet.has(index),
        row: responsibilityPreviewClone(row)
      }));
      const expected = responsibilityPreviewBuildCsvExpected({ rows, section, selectedIndexes });
      const generatedCase = {
        case_id: `${String(definition?.pattern_def_id ?? 'csv')}_case`,
        target_data_path: dataPath,
        row_scope: rowScope,
        filtered_row_indexes: responsibilityPreviewClone(requestedFilteredIndexes),
        input_snapshot: responsibilityPreviewClone(snapshot),
        expected_def_type: 'CsvExpectedDef',
        expected,
        guarantee_id: String(definition?.guarantee_id ?? ''),
        source_definition_id: String(definition?.pattern_def_id ?? '')
      };

      return {
        pattern_id: String(definition?.pattern_def_id ?? 'csv_export'),
        pattern_cd: String(definition?.pattern_cd ?? 'CSV_EXPORT'),
        pattern_role: String(definition?.pattern_role ?? 'STANDARD'),
        generation_mode: 'CSV_EXPORT_CASE',
        target_data_path: dataPath,
        row_scope: rowScope,
        expected_def_type: 'CsvExpectedDef',
        guarantee_id: String(definition?.guarantee_id ?? ''),
        generated_cases: [generatedCase],
        source: {
          input_file: String(setup?.input_file ?? ''),
          view_def_file: String(setup?.view_def_file ?? ''),
          input_approval_status: String(setup?.input_approval_status ?? '')
        }
      };
    });
  }

  #deriveAggregatePatterns({ definitions, setup, inputData, viewDef }) {
    return definitions.map(definition => {
      const dataPath = String(definition?.target_data_path ?? '').trim();
      const rows = responsibilityPreviewGetByDataPath(inputData, dataPath);
      if (!Array.isArray(rows) || rows.length === 0) throw new Error(`Aggregate Target DataPath must resolve to a non-empty array: ${dataPath}`);
      const section = responsibilityPreviewFindSection(viewDef, dataPath);
      if (!section) throw new Error(`Aggregate ViewDef section not found for DataPath: ${dataPath}`);

      const fieldName = String(definition?.target_field ?? '').trim();
      const field = (section?.fields ?? []).find(item => String(item?.field ?? '').trim() === fieldName);
      if (!field) throw new Error(`Aggregate target field not found in ViewDef: ${dataPath}.${fieldName}`);
      const keyField = String(section?.keyField ?? '').trim();
      const rawAggregate = field?.grid?.aggregate;
      const aggregate = rawAggregate && typeof rawAggregate === 'object' && !Array.isArray(rawAggregate)
        && String(field?.type ?? '').toLowerCase() === 'number'
        && String(rawAggregate?.operator ?? '').trim().toLowerCase() === 'sum'
        ? {
            operator: 'sum',
            scope: ['all', 'filtered'].includes(String(rawAggregate?.scope ?? 'filtered').trim().toLowerCase())
              ? String(rawAggregate?.scope ?? 'filtered').trim().toLowerCase()
              : 'filtered',
            label: String(rawAggregate?.label ?? '')
          }
        : null;

      const requestedFilteredIndexes = Array.isArray(definition?.filtered_row_indexes)
        ? definition.filtered_row_indexes.filter(index => Number.isInteger(index) && index >= 0 && index < rows.length)
        : [];
      const selectedIndexes = aggregate?.scope === 'filtered' ? requestedFilteredIndexes : rows.map((_, index) => index);
      const selectedSet = new Set(selectedIndexes);
      const selectedRows = selectedIndexes.map(index => rows[index]);
      const snapshot = rows.map((row, index) => ({
        index,
        row_id: keyField && row?.[keyField] != null ? String(row[keyField]) : String(index),
        selected: selectedSet.has(index),
        value: responsibilityPreviewClone(row?.[fieldName])
      }));

      let aggregateResult = { has_aggregates: false };
      if (aggregate) {
        let value = 0;
        let validCount = 0;
        let ignoredCount = 0;
        for (const row of selectedRows) {
          const numeric = responsibilityPreviewAggregateToFiniteNumber(row?.[fieldName]);
          if (numeric == null) ignoredCount += 1;
          else { value += numeric; validCount += 1; }
        }
        aggregateResult = {
          has_aggregates: true,
          value,
          source_count: selectedRows.length,
          valid_count: validCount,
          ignored_count: ignoredCount
        };
      }

      const metrics = responsibilityPreviewAggregateMetrics(definition?.expected_metric_set);
      const generatedCases = metrics.map(metric => {
        const expectedValue = metric === 'has_aggregates' ? aggregateResult.has_aggregates : aggregateResult[metric];
        if (expectedValue === undefined) throw new Error(`Aggregate Expected metric could not be derived: ${fieldName}.${metric}`);
        return {
          case_id: `${String(definition?.pattern_def_id ?? 'aggregate')}_${metric}`,
          target_data_path: dataPath,
          target_field: fieldName,
          metric,
          actual_path: metric === 'has_aggregates' ? '$.has_aggregates' : `$.byField.${fieldName}.${metric}`,
          input_snapshot: responsibilityPreviewClone(snapshot),
          aggregate_declaration: responsibilityPreviewClone(rawAggregate ?? null),
          filtered_row_indexes: responsibilityPreviewClone(requestedFilteredIndexes),
          expected_def_type: 'ScalarExpectedDef',
          expected: { value: responsibilityPreviewClone(expectedValue) },
          guarantee_id: String(definition?.guarantee_id ?? ''),
          source_definition_id: String(definition?.pattern_def_id ?? '')
        };
      });

      return {
        pattern_id: String(definition?.pattern_def_id ?? ''),
        pattern_cd: String(definition?.pattern_cd ?? 'GRID_AGGREGATE'),
        pattern_role: String(definition?.pattern_role ?? 'STANDARD'),
        generation_mode: 'AGGREGATE_SCALAR_CASE',
        target_data_path: dataPath,
        target_field: fieldName,
        aggregate_operator: aggregate?.operator ?? '',
        aggregate_scope: aggregate?.scope ?? '',
        expected_metric_set: String(definition?.expected_metric_set ?? ''),
        expected_def_type: 'ScalarExpectedDef',
        guarantee_id: String(definition?.guarantee_id ?? ''),
        generated_cases: generatedCases,
        source: {
          input_file: String(setup?.input_file ?? ''),
          view_def_file: String(setup?.view_def_file ?? ''),
          input_approval_status: String(setup?.input_approval_status ?? '')
        }
      };
    });
  }

  #deriveSearchPatterns({ definitions, setup, config, inputData, viewDef, fieldDefinitionDocument, registry, searchOperatorRegistry }) {
    const operatorById = new Map((searchOperatorRegistry?.operators ?? []).map(item => [String(item?.id ?? ''), item]));
    const operatorSetById = new Map((searchOperatorRegistry?.operator_sets ?? []).map(item => [String(item?.id ?? ''), item]));
    const validationFamilyMap = new Map((searchOperatorRegistry?.validation_value_family_mappings ?? []).map(item => [String(item?.value_family ?? ''), String(item?.operator_set_id ?? '')]));
    const fieldTypeFallbackMap = new Map((searchOperatorRegistry?.field_type_fallbacks ?? []).map(item => [String(item?.field_type ?? ''), String(item?.operator_set_id ?? '')]));
    const fieldDefs = Array.isArray(fieldDefinitionDocument?.field_definitions) ? fieldDefinitionDocument.field_definitions : [];
    const fieldDefByPath = new Map(fieldDefs.map(item => [String(item?.field_path ?? '').trim(), item]));
    const groups = new Map();

    for (const definition of definitions) {
      const dataPath = String(definition?.target_data_path ?? '').trim();
      const rows = responsibilityPreviewGetByDataPath(inputData, dataPath);
      if (!Array.isArray(rows) || rows.length === 0) throw new Error(`Search Target DataPath must resolve to a non-empty array: ${dataPath}`);
      const section = responsibilityPreviewFindSection(viewDef, dataPath);
      if (!section) throw new Error(`Search ViewDef section not found for DataPath: ${dataPath}`);

      const fieldName = String(definition?.target_field ?? '').trim();
      const field = (section?.fields ?? []).find(item => String(item?.field ?? '').trim() === fieldName);
      if (!field) throw new Error(`Search target field not found in ViewDef: ${dataPath}.${fieldName}`);
      if (field?.search?.visible === false) throw new Error(`Search target field is not searchable: ${dataPath}.${fieldName}`);

      const fieldPath = responsibilityPreviewCanonicalFieldPath(dataPath, fieldName);
      const fieldDef = fieldDefByPath.get(fieldPath) ?? null;
      const contract = fieldDef ? this.fieldContractResolver.resolve(fieldDef, registry) : null;
      const rawFamily = String(contract?.value_family ?? field?.type ?? '').trim().toLowerCase();
      const operatorSetId = validationFamilyMap.get(rawFamily) || fieldTypeFallbackMap.get(String(field?.type ?? '').trim().toLowerCase());
      const operatorSet = operatorSetById.get(operatorSetId);
      if (!operatorSet) throw new Error(`Search Operator Set could not be resolved: ${fieldPath} (${rawFamily})`);
      const patternFamily = responsibilityPreviewSearchPatternFamily(operatorSetId, rawFamily);
      const keyField = String(section?.keyField ?? '').trim();
      const snapshot = rows.map((row, index) => ({
        index,
        row_id: keyField && row?.[keyField] != null ? String(row[keyField]) : String(index),
        value: responsibilityPreviewClone(row?.[fieldName])
      }));
      const values = snapshot.map(item => item.value);

      for (const operatorId of (operatorSet?.operator_ids ?? [])) {
        const operator = operatorById.get(String(operatorId));
        if (!operator || operator?.status !== 'active') continue;
        const rule = responsibilityPreviewSearchResolveDerivationRule(config?.search_generation, String(operatorId), rawFamily);
        const preRequirementEvaluation = responsibilityPreviewSearchEvaluateInputRequirements({
          rule,
          snapshot,
          family: rawFamily,
          criteria: null,
          trace: {
            input_profile: responsibilityPreviewSearchInputProfile(snapshot, rawFamily),
            selected_source_rows: []
          }
        });

        let generatedCase;
        if (preRequirementEvaluation.generation_needed) {
          const blockedTrace = {
            rule_id: String(rule?.rule_id ?? ''),
            strategy: String(rule?.strategy ?? ''),
            input_profile: responsibilityPreviewSearchInputProfile(snapshot, rawFamily),
            basis: 'INPUT_REQUIREMENT_NOT_MET',
            selected_source_rows: [],
            derived_criteria: null,
            result_coverage: {
              matched_count: null,
              non_matched_count: null,
              coverage_kind: 'NOT_EVALUATED',
              preference: String(rule?.coverage_preference ?? ''),
              assessment: 'BLOCKED_BY_INPUT_REQUIREMENT'
            },
            result_rows: []
          };
          const aiRequest = responsibilityPreviewBuildAiInputGenerationRequest({
            setup,
            dataPath,
            fieldName,
            fieldPath,
            family: rawFamily,
            snapshot,
            rule,
            requirementEvaluation: preRequirementEvaluation
          });
          generatedCase = {
            case_id: `${String(definition?.pattern_def_id ?? 'search')}_${String(operatorId)}`,
            generation_status: 'INPUT_GENERATION_REQUIRED',
            target_data_path: dataPath,
            target_field: fieldName,
            field_path: fieldPath,
            value_family: patternFamily,
            resolved_value_family: rawFamily,
            operator_id: String(operatorId),
            operator_caption: String(operator?.caption ?? operatorId),
            input_snapshot: responsibilityPreviewClone(snapshot),
            criteria: null,
            criteria_derivation: {
              rule_id: String(rule?.rule_id ?? ''),
              rule: responsibilityPreviewClone(rule),
              trace: responsibilityPreviewClone(blockedTrace)
            },
            input_requirement_evaluation: responsibilityPreviewClone(preRequirementEvaluation),
            ai_input_generation_request: responsibilityPreviewClone(aiRequest),
            expected_def_type: String(definition?.expected_def_type ?? 'StateExpectedDef'),
            expected: null,
            guarantee_id: String(definition?.guarantee_id ?? ''),
            source_definition_id: String(definition?.pattern_def_id ?? '')
          };
        } else {
          const derivation = this.#generateSearchCriteria({
            operatorId: String(operatorId),
            snapshot,
            family: rawFamily,
            rule
          });
          const criteria = derivation.criteria;
          const matched = snapshot.filter(item => responsibilityPreviewSearchMatches(item.value, String(operatorId), criteria, rawFamily));
          const matchedIndexSet = new Set(matched.map(item => item.index));
          const coverageKind = matched.length === 0
            ? 'ZERO_MATCH'
            : matched.length === snapshot.length
              ? 'ALL_MATCH'
              : 'MATCH_AND_NON_MATCH';
          derivation.trace.result_coverage = {
            matched_count: matched.length,
            non_matched_count: Math.max(0, snapshot.length - matched.length),
            coverage_kind: coverageKind,
            preference: String(rule?.coverage_preference ?? ''),
            assessment: coverageKind === 'MATCH_AND_NON_MATCH' ? 'PREFERRED' : 'REVIEW'
          };
          derivation.trace.result_rows = snapshot.map(item => ({
            index: item.index,
            row_id: item.row_id,
            matched: matchedIndexSet.has(item.index)
          }));
          const requirementEvaluation = responsibilityPreviewSearchEvaluateInputRequirements({
            rule,
            snapshot,
            family: rawFamily,
            criteria,
            trace: derivation.trace
          });
          const aiRequest = responsibilityPreviewBuildAiInputGenerationRequest({
            setup,
            dataPath,
            fieldName,
            fieldPath,
            family: rawFamily,
            snapshot,
            rule,
            requirementEvaluation
          });
          const expected = {
            row_ids: matched.map(item => item.row_id),
            indexes: matched.map(item => item.index),
            match_count: matched.length
          };
          generatedCase = {
            case_id: `${String(definition?.pattern_def_id ?? 'search')}_${String(operatorId)}`,
            generation_status: 'READY',
            target_data_path: dataPath,
            target_field: fieldName,
            field_path: fieldPath,
            value_family: patternFamily,
            resolved_value_family: rawFamily,
            operator_id: String(operatorId),
            operator_caption: String(operator?.caption ?? operatorId),
            input_snapshot: responsibilityPreviewClone(snapshot),
            criteria: responsibilityPreviewClone(criteria),
            criteria_derivation: {
              rule_id: String(rule?.rule_id ?? ''),
              rule: responsibilityPreviewClone(rule),
              trace: responsibilityPreviewClone(derivation.trace)
            },
            input_requirement_evaluation: responsibilityPreviewClone(requirementEvaluation),
            ai_input_generation_request: responsibilityPreviewClone(aiRequest),
            expected_def_type: String(definition?.expected_def_type ?? 'StateExpectedDef'),
            expected,
            guarantee_id: String(definition?.guarantee_id ?? ''),
            source_definition_id: String(definition?.pattern_def_id ?? '')
          };
        }

        const groupKey = `${patternFamily}::${String(operatorId)}`;
        let pattern = groups.get(groupKey);
        if (!pattern) {
          pattern = {
            pattern_id: `search_filter_${patternFamily}_${String(operatorId)}`,
            pattern_cd: String(definition?.pattern_cd ?? 'SEARCH_FILTER'),
            pattern_role: String(definition?.pattern_role ?? 'STANDARD'),
            generation_mode: 'SEARCH_OPERATOR_MATRIX',
            value_family: patternFamily,
            operator_id: String(operatorId),
            operator_caption: String(operator?.caption ?? operatorId),
            operator_set_id: operatorSetId,
            expected_def_type: String(definition?.expected_def_type ?? 'StateExpectedDef'),
            guarantee_id: String(definition?.guarantee_id ?? ''),
            generated_cases: [],
            source: {
              input_file: String(setup?.input_file ?? ''),
              view_def_file: String(setup?.view_def_file ?? ''),
              field_definition_file: String(setup?.field_definition_file ?? ''),
              search_operator_registry_file: String(setup?.search_operator_registry_file ?? config?.search_generation?.operator_registry_file ?? ''),
              input_approval_status: String(setup?.input_approval_status ?? '')
            }
          };
          groups.set(groupKey, pattern);
        }
        if (pattern.guarantee_id !== generatedCase.guarantee_id) {
          throw new Error(`Generated TestPattern cannot span multiple Guarantee IDs: ${pattern.pattern_id}`);
        }
        pattern.generated_cases.push(generatedCase);
      }
    }

    return [...groups.values()];
  }

  #generateSearchCriteria({ operatorId, snapshot, family, rule }) {
    const rows = Array.isArray(snapshot) ? snapshot : [];
    const values = rows.map(item => item?.value);
    const profile = responsibilityPreviewSearchInputProfile(rows, family);
    const strategy = String(rule?.strategy ?? '').trim();
    const baseTrace = {
      rule_id: String(rule?.rule_id ?? ''),
      strategy,
      input_profile: responsibilityPreviewClone(profile),
      basis: '',
      selected_source_rows: [],
      derived_criteria: null
    };

    if (strategy === 'NO_VALUE') {
      const criteria = { operator: operatorId };
      return {
        criteria,
        trace: {
          ...baseTrace,
          basis: 'OPERATOR_REQUIRES_NO_VALUE',
          derived_criteria: responsibilityPreviewClone(criteria)
        }
      };
    }

    const nonBlank = rows.filter(item => !responsibilityPreviewSearchIsBlank(item?.value));
    if (!nonBlank.length) {
      throw new Error(`Search criteria generation requires a non-blank value: ${operatorId}`);
    }
    const repeated = responsibilityPreviewSearchRepeatedValue(values);

    if (strategy === 'PREFER_REPEATED_NON_BLANK_ELSE_FIRST_NON_BLANK') {
      const selected = repeated === undefined ? nonBlank[0].value : repeated;
      const criteria = { operator: operatorId, value: responsibilityPreviewClone(selected) };
      return {
        criteria,
        trace: {
          ...baseTrace,
          basis: repeated === undefined ? 'FIRST_NON_BLANK' : 'REPEATED_NON_BLANK',
          selected_source_rows: responsibilityPreviewSearchTraceSourceRows(rows, selected),
          derived_criteria: responsibilityPreviewClone(criteria)
        }
      };
    }

    if (strategy === 'PREFER_REPEATED_NON_BLANK_ELSE_MIDDLE_COMPARABLE') {
      const comparable = profile.comparable_values ?? [];
      if (!comparable.length) throw new Error(`Comparable criteria generation failed: ${family}`);
      const repeatedComparable = repeated === undefined ? null : responsibilityPreviewSearchComparable(repeated, family);
      const selected = repeatedComparable == null
        ? comparable[Math.floor((comparable.length - 1) / 2)]?.value
        : repeated;
      const criteria = { operator: operatorId, value: responsibilityPreviewClone(selected) };
      return {
        criteria,
        trace: {
          ...baseTrace,
          basis: repeatedComparable == null ? 'MIDDLE_COMPARABLE' : 'REPEATED_NON_BLANK',
          selected_source_rows: responsibilityPreviewSearchTraceSourceRows(rows, selected),
          derived_criteria: responsibilityPreviewClone(criteria)
        }
      };
    }

    if (strategy === 'REPEATED_PIVOT_TO_NEXT_GREATER_ELSE_NEIGHBOR_RANGE') {
      const comparable = profile.comparable_values ?? [];
      if (!comparable.length) throw new Error(`Range criteria generation failed: ${family}`);
      const repeatedComparable = repeated === undefined ? null : responsibilityPreviewSearchComparable(repeated, family);
      let fromItem = repeatedComparable == null
        ? comparable[Math.floor((comparable.length - 1) / 2)]
        : comparable.find(item => item.comparable === repeatedComparable);
      if (!fromItem) fromItem = comparable[0];

      let toItem = comparable.find(item => item.comparable > fromItem.comparable);
      let basis = repeatedComparable == null
        ? 'MIDDLE_PIVOT_TO_NEXT_GREATER'
        : 'REPEATED_PIVOT_TO_NEXT_GREATER';

      if (!toItem) {
        const prev = [...comparable].reverse().find(item => item.comparable < fromItem.comparable);
        if (prev) {
          const criteria = {
            operator: operatorId,
            from: responsibilityPreviewClone(prev.value),
            to: responsibilityPreviewClone(fromItem.value)
          };
          return {
            criteria,
            trace: {
              ...baseTrace,
              basis: 'PREVIOUS_TO_PIVOT_FALLBACK',
              selected_source_rows: [
                ...responsibilityPreviewSearchTraceSourceRows(rows, prev.value),
                ...responsibilityPreviewSearchTraceSourceRows(rows, fromItem.value)
              ],
              derived_criteria: responsibilityPreviewClone(criteria)
            }
          };
        }
        toItem = fromItem;
        basis = 'SINGLE_COMPARABLE_FALLBACK';
      }

      const criteria = {
        operator: operatorId,
        from: responsibilityPreviewClone(fromItem.value),
        to: responsibilityPreviewClone(toItem.value)
      };
      return {
        criteria,
        trace: {
          ...baseTrace,
          basis,
          selected_source_rows: [
            ...responsibilityPreviewSearchTraceSourceRows(rows, fromItem.value),
            ...responsibilityPreviewSearchTraceSourceRows(rows, toItem.value)
          ],
          derived_criteria: responsibilityPreviewClone(criteria)
        }
      };
    }

    throw new Error(`Unsupported Search Criteria derivation strategy: ${strategy || '(empty)'} / rule=${rule?.rule_id ?? ''}`);
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
