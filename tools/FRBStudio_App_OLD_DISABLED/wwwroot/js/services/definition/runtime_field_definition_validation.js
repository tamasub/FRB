// v0.18.47-field-definition-runtime-validation
// Runtime contract validation for one Studio Detail row.
// The top-level responsibility is the Editor commit contract:
// values that violate an explicit Field Definition must not reach canonical Data.

function runtimeFieldDefinitionCanonicalPath(sectionDataPath, fieldName) {
  const base = String(sectionDataPath || '$').trim();
  const field = String(fieldName || '').trim();
  if (!field) return '';
  const normalizedBase = base === '$'
    ? '$'
    : `${base.replace(/\[\]$/, '')}[]`;
  return normalizedBase === '$' ? `$.${field}` : `${normalizedBase}.${field}`;
}

function runtimeFieldDefinitionHasPath(object, pathName) {
  if (!object || typeof object !== 'object') return false;
  const normalized = String(pathName ?? '').replace(/^\$\.?/, '');
  if (!normalized) return true;
  const parts = normalized.split('.').filter(Boolean);
  let current = object;
  for (const part of parts) {
    if (current == null || typeof current !== 'object' || !Object.prototype.hasOwnProperty.call(current, part)) {
      return false;
    }
    current = current[part];
  }
  return true;
}

function runtimeFieldDefinitionGetPath(object, pathName) {
  const normalized = String(pathName ?? '').replace(/^\$\.?/, '');
  if (!normalized) return object;
  return normalized.split('.').filter(Boolean).reduce(
    (current, part) => current == null ? undefined : current[part],
    object
  );
}

function runtimeFieldDefinitionFormatValue(value) {
  if (value === undefined) return '(MISSING)';
  if (typeof value === 'string') return value;
  try { return JSON.stringify(value); }
  catch { return String(value); }
}

function runtimeFieldDefinitionConstraintEvidence(check) {
  const violations = Array.isArray(check?.validation?.violations) ? check.validation.violations : [];
  const resolutions = Array.isArray(check?.contract?.constraint_resolutions)
    ? check.contract.constraint_resolutions
    : [];

  const evidence = [];
  violations.forEach(violation => {
    const key = String(violation?.constraint ?? '').trim();
    if (!key) return;
    const resolution = resolutions.find(item => item?.constraint === key);
    evidence.push({
      constraint: key,
      resolved_value: resolution?.resolved_value,
      status: resolution?.status ?? ''
    });
  });
  return evidence;
}

class RuntimeFieldDefinitionValidationService {
  constructor(options={}) {
    this.fieldContractResolver = options.fieldContractResolver
      ?? (typeof FieldContractResolver !== 'undefined' ? new FieldContractResolver() : null);
    this.valueValidator = options.valueValidator
      ?? (typeof DefinitionValueValidator !== 'undefined' ? new DefinitionValueValidator() : null);
  }

  validateRow(options={}) {
    const row = options.row ?? null;
    const gd = options.gridDef ?? null;
    const document = options.fieldDefinitionDocument ?? null;
    const registry = options.registry ?? null;

    if (!document) {
      return {
        status: 'SKIPPED',
        reason_code: 'FIELD_DEFINITION_NOT_DECLARED',
        checks: [],
        blocking_checks: []
      };
    }
    if (!Array.isArray(document.field_definitions)) {
      return {
        status: 'UNRESOLVED',
        reason_code: 'FIELD_DEFINITION_DOCUMENT_INVALID',
        checks: [],
        blocking_checks: [{
          field_name: '',
          field_caption: '',
          field_path: '',
          input: { state: 'MISSING' },
          validation: {
            outcome: 'UNRESOLVED',
            reason_code: 'FIELD_DEFINITION_DOCUMENT_INVALID',
            violations: [{ code: 'FIELD_DEFINITION_DOCUMENT_INVALID', constraint: '' }]
          },
          contract: null
        }]
      };
    }
    if (!registry || !this.fieldContractResolver || !this.valueValidator) {
      return {
        status: 'UNRESOLVED',
        reason_code: 'RUNTIME_VALIDATION_DEPENDENCY_UNAVAILABLE',
        checks: [],
        blocking_checks: [{
          field_name: '',
          field_caption: '',
          field_path: '',
          input: { state: 'MISSING' },
          validation: {
            outcome: 'UNRESOLVED',
            reason_code: 'RUNTIME_VALIDATION_DEPENDENCY_UNAVAILABLE',
            violations: [{ code: 'RUNTIME_VALIDATION_DEPENDENCY_UNAVAILABLE', constraint: '' }]
          },
          contract: null
        }]
      };
    }

    const byPath = new Map(
      document.field_definitions
        .filter(item => item && typeof item === 'object')
        .map(item => [String(item.field_path ?? '').trim(), item])
        .filter(([path]) => path)
    );
    const checks = [];

    for (const field of gd?.fields ?? []) {
      if (!field?.field) continue;
      const fieldPath = runtimeFieldDefinitionCanonicalPath(gd?.dataPath ?? '$', field.field);
      const fieldDefinition = byPath.get(fieldPath);
      if (!fieldDefinition) continue; // fielddefs is intentionally sparse.

      const contract = this.fieldContractResolver.resolve(fieldDefinition, registry);
      const hasValue = runtimeFieldDefinitionHasPath(row, field.field);
      const input = hasValue
        ? { state: 'VALUE', value: runtimeFieldDefinitionGetPath(row, field.field) }
        : { state: 'MISSING' };
      const validation = this.valueValidator.validate(contract, input);

      checks.push({
        field_name: field.field,
        field_caption: String(field.caption ?? field.field),
        field_path: fieldPath,
        validation_type: String(fieldDefinition.validation_type ?? ''),
        input: typeof definitionVerificationClone === 'function'
          ? definitionVerificationClone(input)
          : JSON.parse(JSON.stringify(input)),
        validation: typeof definitionVerificationClone === 'function'
          ? definitionVerificationClone(validation)
          : JSON.parse(JSON.stringify(validation)),
        contract: typeof definitionVerificationClone === 'function'
          ? definitionVerificationClone(contract)
          : JSON.parse(JSON.stringify(contract))
      });
    }

    const blocking = checks.filter(check => check.validation?.outcome !== 'ACCEPT');
    const hasReject = blocking.some(check => check.validation?.outcome === 'REJECT');
    const hasUnresolved = blocking.some(check => check.validation?.outcome === 'UNRESOLVED');

    return {
      status: hasReject ? 'REJECT' : (hasUnresolved ? 'UNRESOLVED' : 'ACCEPT'),
      reason_code: hasReject
        ? 'FIELD_DEFINITION_CONTRACT_VIOLATION'
        : (hasUnresolved ? 'FIELD_DEFINITION_CONTRACT_UNRESOLVED' : 'FIELD_DEFINITION_CONTRACT_ACCEPTED'),
      checks,
      blocking_checks: blocking
    };
  }
}

function formatRuntimeFieldDefinitionValidationDetail(result={}) {
  const checks = Array.isArray(result.blocking_checks) ? result.blocking_checks : [];
  if (!checks.length) return '';

  const blocks = [];
  checks.forEach((check, index) => {
    const inputValue = check?.input?.state === 'MISSING'
      ? '(MISSING)'
      : runtimeFieldDefinitionFormatValue(check?.input?.value);
    const evidence = runtimeFieldDefinitionConstraintEvidence(check);
    const lines = [
      `${index + 1}. ${check.field_caption || check.field_name || check.field_path}`,
      `- Field Path: ${check.field_path || '(unknown)'}`,
      `- Validation Type: ${check.validation_type || check.contract?.validation_type_id || '(unknown)'}`,
      `- 入力値: ${inputValue}`,
      `- 判定: ${check.validation?.outcome || 'UNRESOLVED'}`,
      `- Reason: ${check.validation?.reason_code || result.reason_code || 'UNRESOLVED'}`
    ];
    if (evidence.length) {
      lines.push('- 契約根拠:');
      evidence.forEach(item => {
        lines.push(`  - ${item.constraint} = ${runtimeFieldDefinitionFormatValue(item.resolved_value)} (${item.status || 'UNRESOLVED'})`);
      });
    }
    blocks.push(lines.join('\n'));
  });
  return blocks.join('\n\n');
}

globalThis.runtimeFieldDefinitionCanonicalPath = runtimeFieldDefinitionCanonicalPath;
globalThis.RuntimeFieldDefinitionValidationService = RuntimeFieldDefinitionValidationService;
globalThis.formatRuntimeFieldDefinitionValidationDetail = formatRuntimeFieldDefinitionValidationDetail;
