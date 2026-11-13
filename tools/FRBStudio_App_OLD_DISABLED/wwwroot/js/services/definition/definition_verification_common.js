// v0.18.42-definition-verification-service
// Shared pure helpers for Definition Verification. No DOM / Editor dependency.

const DEFINITION_VERIFICATION_SCHEMA_VERSION = 'definition_verification_result_v0_1';
const RESOLVED_FIELD_CONTRACT_SCHEMA_VERSION = 'resolved_field_contract_v0_1';

function definitionVerificationClone(value) {
  if (value === undefined) return undefined;
  return JSON.parse(JSON.stringify(value));
}

function definitionVerificationHasOwn(object, key) {
  return Object.prototype.hasOwnProperty.call(object ?? {}, key);
}

function definitionVerificationConstraintKeys(validationTypeDefinition={}) {
  return [...new Set([
    ...Object.keys(validationTypeDefinition.default_constraints ?? {}),
    ...(validationTypeDefinition.required_constraints ?? []),
    ...(validationTypeDefinition.overridable_constraints ?? [])
  ])];
}

function definitionVerificationBoundaryValue(value) {
  if (value && typeof value === 'object' && definitionVerificationHasOwn(value, 'value')) {
    return value.value;
  }
  return value;
}

function definitionVerificationBoundaryInclusive(value) {
  if (value && typeof value === 'object' && definitionVerificationHasOwn(value, 'inclusive')) {
    return value.inclusive !== false;
  }
  return true;
}

function definitionVerificationCompareValues(left, right) {
  if (typeof left === 'number' && typeof right === 'number') {
    return left === right ? 0 : (left < right ? -1 : 1);
  }
  const a = String(left);
  const b = String(right);
  return a === b ? 0 : (a < b ? -1 : 1);
}

function definitionVerificationIsNarrowerBoundary(key, baseBoundary, overrideBoundary) {
  const baseValue = definitionVerificationBoundaryValue(baseBoundary);
  const overrideValue = definitionVerificationBoundaryValue(overrideBoundary);
  const comparison = definitionVerificationCompareValues(overrideValue, baseValue);
  const baseInclusive = definitionVerificationBoundaryInclusive(baseBoundary);
  const overrideInclusive = definitionVerificationBoundaryInclusive(overrideBoundary);

  if (/^minimum(?:_|$)/.test(key)) {
    if (comparison > 0) return true;
    if (comparison < 0) return false;
    return !(baseInclusive === false && overrideInclusive === true);
  }
  if (/^maximum(?:_|$)/.test(key)) {
    if (comparison < 0) return true;
    if (comparison > 0) return false;
    return !(baseInclusive === false && overrideInclusive === true);
  }
  return true;
}

function definitionVerificationShiftIsoDate(value, days) {
  const match = /^(\d{4})-(\d{2})-(\d{2})$/.exec(String(value ?? ''));
  if (!match) return null;
  const date = new Date(Date.UTC(Number(match[1]), Number(match[2]) - 1, Number(match[3])));
  if (Number.isNaN(date.getTime())) return null;
  date.setUTCDate(date.getUTCDate() + days);
  return date.toISOString().slice(0, 10);
}

function definitionVerificationShiftLocalDateTime(value, minutes) {
  const text = String(value ?? '');
  const match = /^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2})(?::(\d{2}))?$/.exec(text);
  if (!match) return null;
  const date = new Date(Date.UTC(
    Number(match[1]), Number(match[2]) - 1, Number(match[3]),
    Number(match[4]), Number(match[5]), Number(match[6] ?? 0)
  ));
  if (Number.isNaN(date.getTime())) return null;
  date.setUTCMinutes(date.getUTCMinutes() + minutes);
  const iso = date.toISOString();
  return match[6] === undefined ? iso.slice(0, 16) : iso.slice(0, 19);
}

function definitionVerificationShiftInstant(value, seconds) {
  const date = new Date(String(value ?? ''));
  if (Number.isNaN(date.getTime())) return null;
  date.setUTCSeconds(date.getUTCSeconds() + seconds);
  return date.toISOString();
}

function definitionVerificationShiftBoundary(valueFamily, boundaryValue, direction) {
  const sign = direction < 0 ? -1 : 1;
  if (['number', 'integer', 'float', 'decimal'].includes(valueFamily)) {
    return typeof boundaryValue === 'number' ? boundaryValue + sign : null;
  }
  if (valueFamily === 'date') return definitionVerificationShiftIsoDate(boundaryValue, sign);
  if (valueFamily === 'datetime') return definitionVerificationShiftLocalDateTime(boundaryValue, sign);
  if (valueFamily === 'instant') return definitionVerificationShiftInstant(boundaryValue, sign);
  return null;
}

function definitionVerificationStringSeed(valueContract={}) {
  const pattern = String(valueContract?.pattern ?? '');
  if (pattern.includes('[0-9]') && !pattern.includes('A-Za-z')) return '1';
  if (pattern.includes('A-Za-z0-9')) return 'A1';
  if (valueContract?.character_policy === 'identifier') return 'a';
  return 'a';
}

function definitionVerificationSampleValue(valueFamily, valueContract={}, resolvedConstraints={}) {
  const constraintValue = key => definitionVerificationBoundaryValue(resolvedConstraints?.[key]);
  const constraintInclusive = key => definitionVerificationBoundaryInclusive(resolvedConstraints?.[key]);

  if (valueFamily === 'string') {
    const minimumLength = Number.isInteger(resolvedConstraints?.minimum_length) ? resolvedConstraints.minimum_length : 1;
    const maximumLength = Number.isInteger(resolvedConstraints?.maximum_length) ? resolvedConstraints.maximum_length : null;
    let length = Math.max(0, minimumLength);
    if (maximumLength !== null) length = Math.min(length, Math.max(0, maximumLength));
    const seed = definitionVerificationStringSeed(valueContract);
    return seed.repeat(Math.ceil(Math.max(1, length) / seed.length)).slice(0, length);
  }

  if (['number', 'float', 'integer'].includes(valueFamily)) {
    let value = valueFamily === 'integer' ? 1 : 1.5;
    const minimum = constraintValue('minimum');
    const maximum = constraintValue('maximum');
    if (typeof minimum === 'number') value = minimum + (constraintInclusive('minimum') ? 0 : 1);
    if (typeof maximum === 'number' && value > maximum) value = maximum - (constraintInclusive('maximum') ? 0 : 1);
    if (valueFamily === 'integer') value = Math.trunc(value);
    return value;
  }

  if (valueFamily === 'boolean') return true;

  if (valueFamily === 'date') {
    const minimum = constraintValue('minimum_date');
    if (minimum != null) return constraintInclusive('minimum_date') ? minimum : definitionVerificationShiftIsoDate(minimum, 1);
    return '2026-01-15';
  }

  if (valueFamily === 'datetime') {
    const minimum = constraintValue('minimum_datetime');
    if (minimum != null) return constraintInclusive('minimum_datetime') ? minimum : definitionVerificationShiftLocalDateTime(minimum, 1);
    return valueContract?.default_precision === 'minute' ? '2026-01-15T12:34' : '2026-01-15T12:34:56';
  }

  if (valueFamily === 'instant') {
    const minimum = constraintValue('minimum_instant');
    if (minimum != null) return constraintInclusive('minimum_instant') ? minimum : definitionVerificationShiftInstant(minimum, 1);
    return '2026-01-15T12:34:56Z';
  }

  if (valueFamily === 'decimal') return '1.00';
  return 'sample';
}

function definitionVerificationInvalidValue(valueFamily, valueContract={}) {
  if (valueFamily === 'string') {
    const pattern = String(valueContract?.pattern ?? '');
    if (valueContract?.character_policy === 'identifier') return '1 invalid';
    if (pattern.includes('[0-9]') && !pattern.includes('A-Za-z')) return '12A';
    if (pattern.includes('A-Za-z0-9')) return 'A-1';
    return 123;
  }
  switch (valueFamily) {
    case 'number':
    case 'float':
    case 'integer': return 'not-a-number';
    case 'boolean': return 'true';
    case 'date': return '2026-02-30';
    case 'datetime': return '2026-02-30T25:61';
    case 'instant': return '2026-01-15T12:34:56';
    case 'decimal': return 'not-a-decimal';
    default: return null;
  }
}


globalThis.DEFINITION_VERIFICATION_SCHEMA_VERSION = DEFINITION_VERIFICATION_SCHEMA_VERSION;
globalThis.RESOLVED_FIELD_CONTRACT_SCHEMA_VERSION = RESOLVED_FIELD_CONTRACT_SCHEMA_VERSION;
globalThis.definitionVerificationClone = definitionVerificationClone;
globalThis.definitionVerificationHasOwn = definitionVerificationHasOwn;
globalThis.definitionVerificationConstraintKeys = definitionVerificationConstraintKeys;
globalThis.definitionVerificationBoundaryValue = definitionVerificationBoundaryValue;
globalThis.definitionVerificationBoundaryInclusive = definitionVerificationBoundaryInclusive;
globalThis.definitionVerificationCompareValues = definitionVerificationCompareValues;
globalThis.definitionVerificationIsNarrowerBoundary = definitionVerificationIsNarrowerBoundary;
globalThis.definitionVerificationShiftBoundary = definitionVerificationShiftBoundary;
globalThis.definitionVerificationSampleValue = definitionVerificationSampleValue;
globalThis.definitionVerificationInvalidValue = definitionVerificationInvalidValue;
