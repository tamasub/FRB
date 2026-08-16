// v0.18.75-app-settings-save-phase4
// UI-independent Definition Driven validation for a whole JSON document.
// Supports sparse Field Definitions and array item paths such as $.items[].id.

function definitionDocumentClone(value) {
  if (typeof definitionVerificationClone === 'function') return definitionVerificationClone(value);
  if (value === undefined) return undefined;
  return JSON.parse(JSON.stringify(value));
}

function definitionDocumentPathSegments(fieldPath) {
  const raw = String(fieldPath ?? '').trim();
  if (!raw.startsWith('$.')) return [];
  return raw.slice(2).split('.').filter(Boolean).map(segment => ({
    key: segment.endsWith('[]') ? segment.slice(0, -2) : segment,
    array: segment.endsWith('[]')
  }));
}

function definitionDocumentEnumerateInputs(document, fieldPath) {
  const segments = definitionDocumentPathSegments(fieldPath);
  if (!segments.length) {
    return { inputs: [], issues: [{ code: 'FIELD_PATH_UNSUPPORTED', field_path: String(fieldPath ?? '') }] };
  }

  let contexts = [{ value: document, path: '$' }];
  const issues = [];

  for (let index = 0; index < segments.length; index += 1) {
    const segment = segments[index];
    const leaf = index === segments.length - 1;
    const next = [];

    for (const context of contexts) {
      const object = context.value;
      if (segment.array) {
        if (object == null || typeof object !== 'object' || !Object.prototype.hasOwnProperty.call(object, segment.key)) {
          // Item-level Field Definitions do not imply that the parent array itself is required.
          continue;
        }
        const arrayValue = object[segment.key];
        if (!Array.isArray(arrayValue)) {
          issues.push({
            code: 'ARRAY_CONTAINER_REQUIRED',
            field_path: String(fieldPath ?? ''),
            instance_path: `${context.path}.${segment.key}`
          });
          continue;
        }
        arrayValue.forEach((item, itemIndex) => {
          next.push({ value: item, path: `${context.path}.${segment.key}[${itemIndex}]` });
        });
        continue;
      }

      if (leaf) {
        const hasValue = object != null
          && typeof object === 'object'
          && Object.prototype.hasOwnProperty.call(object, segment.key);
        next.push({
          value: hasValue ? object[segment.key] : undefined,
          path: `${context.path}.${segment.key}`,
          state: hasValue ? 'VALUE' : 'MISSING'
        });
        continue;
      }

      if (object == null || typeof object !== 'object' || !Object.prototype.hasOwnProperty.call(object, segment.key)) {
        next.push({ value: undefined, path: `${context.path}.${segment.key}`, missing: true });
        continue;
      }
      next.push({ value: object[segment.key], path: `${context.path}.${segment.key}` });
    }

    contexts = next;
  }

  const inputs = contexts
    .filter(context => Object.prototype.hasOwnProperty.call(context, 'state'))
    .map(context => ({
      instance_path: context.path,
      input: context.state === 'MISSING'
        ? { state: 'MISSING' }
        : { state: 'VALUE', value: definitionDocumentClone(context.value) }
    }));

  return { inputs, issues };
}

class DefinitionDocumentValidator {
  constructor(options={}) {
    this.fieldContractResolver = options.fieldContractResolver
      ?? (typeof FieldContractResolver !== 'undefined' ? new FieldContractResolver() : null);
    this.valueValidator = options.valueValidator
      ?? (typeof DefinitionValueValidator !== 'undefined' ? new DefinitionValueValidator() : null);
  }

  validate(document, fieldDefinitionDocument, registry) {
    if (!fieldDefinitionDocument || !Array.isArray(fieldDefinitionDocument.field_definitions)) {
      return this.#unresolved('FIELD_DEFINITION_DOCUMENT_INVALID');
    }
    if (!registry || !this.fieldContractResolver || !this.valueValidator) {
      return this.#unresolved('DEFINITION_VALIDATION_DEPENDENCY_UNAVAILABLE');
    }

    const checks = [];
    const structuralIssues = [];

    for (const fieldDefinition of fieldDefinitionDocument.field_definitions) {
      if (!fieldDefinition || typeof fieldDefinition !== 'object') continue;
      const fieldPath = String(fieldDefinition.field_path ?? '').trim();
      if (!fieldPath) continue;

      const contract = this.fieldContractResolver.resolve(fieldDefinition, registry);
      const enumerated = definitionDocumentEnumerateInputs(document, fieldPath);
      structuralIssues.push(...enumerated.issues.map(issue => ({ ...issue, field_path: fieldPath })));

      for (const item of enumerated.inputs) {
        const validation = this.valueValidator.validate(contract, item.input);
        checks.push({
          field_path: fieldPath,
          instance_path: item.instance_path,
          validation_type: String(fieldDefinition.validation_type ?? ''),
          input: definitionDocumentClone(item.input),
          validation: definitionDocumentClone(validation),
          contract: definitionDocumentClone(contract)
        });
      }
    }

    structuralIssues.forEach(issue => {
      checks.push({
        field_path: issue.field_path ?? '',
        instance_path: issue.instance_path ?? '',
        validation_type: '',
        input: { state: 'MISSING' },
        validation: {
          outcome: 'UNRESOLVED',
          reason_code: issue.code,
          violations: [{ code: issue.code, constraint: '' }]
        },
        contract: null
      });
    });

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

  #unresolved(reasonCode) {
    return {
      status: 'UNRESOLVED',
      reason_code: reasonCode,
      checks: [],
      blocking_checks: [{
        field_path: '',
        instance_path: '',
        validation_type: '',
        input: { state: 'MISSING' },
        validation: {
          outcome: 'UNRESOLVED',
          reason_code: reasonCode,
          violations: [{ code: reasonCode, constraint: '' }]
        },
        contract: null
      }]
    };
  }
}

function formatDefinitionDocumentValidationDetail(result={}) {
  const checks = Array.isArray(result?.blocking_checks) ? result.blocking_checks : [];
  return checks.map((check, index) => {
    const value = check?.input?.state === 'MISSING'
      ? '(MISSING)'
      : (() => {
          try { return JSON.stringify(check?.input?.value); }
          catch { return String(check?.input?.value ?? ''); }
        })();
    const violationCodes = (check?.validation?.violations ?? [])
      .map(item => item?.code)
      .filter(Boolean)
      .join(', ');
    return [
      `${index + 1}. ${check.instance_path || check.field_path || '(unknown)'}`,
      `- Field Definition: ${check.field_path || '(unknown)'}`,
      `- Validation Type: ${check.validation_type || check.contract?.validation_type_id || '(unknown)'}`,
      `- 入力値: ${value}`,
      `- 判定: ${check.validation?.outcome || 'UNRESOLVED'}`,
      `- Reason: ${check.validation?.reason_code || result.reason_code || 'UNRESOLVED'}`,
      violationCodes ? `- Violations: ${violationCodes}` : ''
    ].filter(Boolean).join('\n');
  }).join('\n\n');
}

globalThis.definitionDocumentPathSegments = definitionDocumentPathSegments;
globalThis.definitionDocumentEnumerateInputs = definitionDocumentEnumerateInputs;
globalThis.DefinitionDocumentValidator = DefinitionDocumentValidator;
globalThis.formatDefinitionDocumentValidationDetail = formatDefinitionDocumentValidationDetail;
