// v0.18.44-definition-test-runner-core
// UI-independent executor for one TestPattern input against one ResolvedFieldContract.

class DefinitionValueValidator {
  validate(contract={}, input={}) {
    if (!contract || contract.resolution_status === 'INVALID') {
      return this.#result('UNRESOLVED', 'FIELD_CONTRACT_INVALID', [this.#violation('FIELD_CONTRACT_INVALID')]);
    }

    const state = String(input?.state ?? 'VALUE');
    if (state === 'MISSING') return this.#validateMissing(contract);
    if (state !== 'VALUE') {
      return this.#result('UNRESOLVED', 'INPUT_STATE_UNSUPPORTED', [this.#violation('INPUT_STATE_UNSUPPORTED')]);
    }

    const value = input?.value;
    if (value === null) return this.#validateNull(contract);

    const violations = [];
    const unresolved = [];
    this.#validateValueContract(contract, value, violations, unresolved);
    this.#validateResolvedConstraints(contract, value, violations, unresolved);

    if (violations.length > 0) {
      return this.#result('REJECT', violations[0].code, violations);
    }
    if (unresolved.length > 0) {
      return this.#result('UNRESOLVED', unresolved[0].code, unresolved);
    }
    return this.#result('ACCEPT', 'VALUE_ACCEPTED', []);
  }

  #validateMissing(contract) {
    const required = this.#constraintResolution(contract, 'required');
    if (!required || required.status !== 'RESOLVED') {
      return this.#result('UNRESOLVED', 'CONSTRAINT_UNRESOLVED:required', [this.#violation('CONSTRAINT_UNRESOLVED:required', 'required')]);
    }
    return required.resolved_value === true
      ? this.#result('REJECT', 'REQUIRED_MISSING', [this.#violation('REQUIRED_MISSING', 'required')])
      : this.#result('ACCEPT', 'OPTIONAL_MISSING_ACCEPTED', []);
  }

  #validateNull(contract) {
    const nullable = this.#constraintResolution(contract, 'nullable');
    if (!nullable || nullable.status !== 'RESOLVED') {
      return this.#result('UNRESOLVED', 'CONSTRAINT_UNRESOLVED:nullable', [this.#violation('CONSTRAINT_UNRESOLVED:nullable', 'nullable')]);
    }
    return nullable.resolved_value === true
      ? this.#result('ACCEPT', 'NULL_ACCEPTED', [])
      : this.#result('REJECT', 'NULL_NOT_ALLOWED', [this.#violation('NULL_NOT_ALLOWED', 'nullable')]);
  }

  #validateValueContract(contract, value, violations, unresolved) {
    const family = String(contract.value_family ?? '');
    const valueContract = contract.value_contract ?? {};

    switch (family) {
      case 'string':
        this.#validateStringContract(valueContract, value, violations);
        break;
      case 'number':
      case 'float':
        this.#validateNumberContract(valueContract, value, violations, false);
        break;
      case 'integer':
        this.#validateNumberContract(valueContract, value, violations, true);
        break;
      case 'boolean':
        if (typeof value !== 'boolean') violations.push(this.#violation('BOOLEAN_REQUIRED'));
        break;
      case 'date':
        if (typeof value !== 'string' || !this.#isValidDate(value)) violations.push(this.#violation('DATE_FORMAT_INVALID'));
        break;
      case 'datetime':
        if (typeof value !== 'string' || !this.#isValidLocalDateTime(value)) violations.push(this.#violation('DATETIME_FORMAT_INVALID'));
        break;
      case 'instant':
        if (typeof value !== 'string' || !this.#isValidInstant(value)) violations.push(this.#violation('INSTANT_FORMAT_INVALID'));
        break;
      case 'decimal':
        unresolved.push(this.#violation('DECIMAL_RUNTIME_CONTRACT_UNRESOLVED'));
        break;
      default:
        unresolved.push(this.#violation(`VALUE_FAMILY_UNSUPPORTED:${family || 'EMPTY'}`));
        break;
    }
  }

  #validateStringContract(valueContract, value, violations) {
    if (typeof value !== 'string') {
      violations.push(this.#violation('STRING_REQUIRED'));
      return;
    }
    if (valueContract.line_break_allowed === false && /[\r\n]/.test(value)) {
      violations.push(this.#violation('LINE_BREAK_NOT_ALLOWED'));
    }
    const pattern = String(valueContract.pattern ?? '');
    if (pattern) {
      let expression = null;
      try {
        expression = new RegExp(pattern);
      } catch {
        violations.push(this.#violation('VALUE_CONTRACT_PATTERN_INVALID'));
      }
      if (expression && !expression.test(value)) {
        violations.push(this.#violation('VALUE_PATTERN_MISMATCH'));
      }
    }
  }

  #validateNumberContract(valueContract, value, violations, integerFamily) {
    if (typeof value !== 'number') {
      violations.push(this.#violation('NUMBER_REQUIRED'));
      return;
    }
    if (valueContract.finite_required === true && !Number.isFinite(value)) {
      violations.push(this.#violation('FINITE_NUMBER_REQUIRED'));
      return;
    }
    if ((integerFamily || valueContract.integer_required === true) && !Number.isInteger(value)) {
      violations.push(this.#violation('INTEGER_REQUIRED'));
    }
    if (valueContract.safe_integer_required === true && !Number.isSafeInteger(value)) {
      violations.push(this.#violation('SAFE_INTEGER_REQUIRED'));
    }
    if (valueContract.negative_allowed === false && value < 0) {
      violations.push(this.#violation('NEGATIVE_NOT_ALLOWED'));
    }
    if (valueContract.zero_allowed === false && value === 0) {
      violations.push(this.#violation('ZERO_NOT_ALLOWED'));
    }
  }

  #validateResolvedConstraints(contract, value, violations, unresolved) {
    const family = String(contract.value_family ?? '');
    const resolved = contract.resolved_constraints ?? {};

    if (family === 'string' && typeof value === 'string') {
      this.#validateBooleanPolicy(contract, 'empty_string_allowed', value.length === 0, false, 'EMPTY_STRING_NOT_ALLOWED', violations, unresolved);
      if (Number.isInteger(resolved.minimum_length) && value.length < resolved.minimum_length) {
        violations.push(this.#violation('MINIMUM_LENGTH_VIOLATION', 'minimum_length'));
      }
      if (Number.isInteger(resolved.maximum_length) && value.length > resolved.maximum_length) {
        violations.push(this.#violation('MAXIMUM_LENGTH_VIOLATION', 'maximum_length'));
      }
      if (Number.isInteger(resolved.maximum_lines)) {
        const lines = value.split(/\r\n|\r|\n/).length;
        if (lines > resolved.maximum_lines) violations.push(this.#violation('MAXIMUM_LINES_VIOLATION', 'maximum_lines'));
      }
      return;
    }

    if (family === 'datetime' && typeof value === 'string' && this.#isValidLocalDateTime(value)) {
      const hasSeconds = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}$/.test(value);
      this.#validateBooleanPolicy(contract, 'seconds_allowed', hasSeconds, false, 'SECONDS_NOT_ALLOWED', violations, unresolved);
    }

    const boundaryKeys = this.#boundaryKeysForFamily(family);
    if (!boundaryKeys) return;
    const [minimumKey, maximumKey] = boundaryKeys;
    if (definitionVerificationHasOwn(resolved, minimumKey)) {
      this.#validateBoundary(family, value, minimumKey, resolved[minimumKey], true, violations);
    }
    if (definitionVerificationHasOwn(resolved, maximumKey)) {
      this.#validateBoundary(family, value, maximumKey, resolved[maximumKey], false, violations);
    }
  }

  #validateBooleanPolicy(contract, key, conditionTriggered, rejectingValue, violationCode, violations, _unresolved) {
    if (!conditionTriggered) return;
    const resolution = this.#constraintResolution(contract, key);
    if (!resolution || resolution.status !== 'RESOLVED') return;
    if (resolution.resolved_value === rejectingValue) {
      violations.push(this.#violation(violationCode, key));
    }
  }

  #validateBoundary(family, value, key, boundary, isMinimum, violations) {
    const boundaryValue = definitionVerificationBoundaryValue(boundary);
    const inclusive = definitionVerificationBoundaryInclusive(boundary);
    const comparison = this.#compareFamilyValues(family, value, boundaryValue);
    if (comparison === null) return;
    const rejected = isMinimum
      ? (comparison < 0 || (comparison === 0 && !inclusive))
      : (comparison > 0 || (comparison === 0 && !inclusive));
    if (rejected) violations.push(this.#violation(isMinimum ? 'MINIMUM_BOUNDARY_VIOLATION' : 'MAXIMUM_BOUNDARY_VIOLATION', key));
  }

  #compareFamilyValues(family, left, right) {
    if (['number', 'float', 'integer'].includes(family)) {
      if (typeof left !== 'number' || typeof right !== 'number') return null;
      return left === right ? 0 : (left < right ? -1 : 1);
    }
    if (family === 'date' || family === 'datetime') {
      if (typeof left !== 'string' || typeof right !== 'string') return null;
      return left === right ? 0 : (left < right ? -1 : 1);
    }
    if (family === 'instant') {
      const a = Date.parse(String(left));
      const b = Date.parse(String(right));
      if (Number.isNaN(a) || Number.isNaN(b)) return null;
      return a === b ? 0 : (a < b ? -1 : 1);
    }
    return null;
  }

  #boundaryKeysForFamily(family) {
    if (['number', 'float', 'integer'].includes(family)) return ['minimum', 'maximum'];
    if (family === 'date') return ['minimum_date', 'maximum_date'];
    if (family === 'datetime') return ['minimum_datetime', 'maximum_datetime'];
    if (family === 'instant') return ['minimum_instant', 'maximum_instant'];
    return null;
  }

  #constraintResolution(contract, key) {
    return contract.constraint_resolutions?.find(item => item.constraint === key) ?? null;
  }

  #isValidDate(value) {
    const match = /^(\d{4})-(\d{2})-(\d{2})$/.exec(value);
    if (!match) return false;
    return this.#isValidCalendarParts(Number(match[1]), Number(match[2]), Number(match[3]));
  }

  #isValidLocalDateTime(value) {
    const match = /^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2})(?::(\d{2}))?$/.exec(value);
    if (!match) return false;
    if (!this.#isValidCalendarParts(Number(match[1]), Number(match[2]), Number(match[3]))) return false;
    const hour = Number(match[4]);
    const minute = Number(match[5]);
    const second = Number(match[6] ?? 0);
    return hour >= 0 && hour <= 23 && minute >= 0 && minute <= 59 && second >= 0 && second <= 59;
  }

  #isValidInstant(value) {
    const match = /^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})$/.exec(value);
    if (!match) return false;
    if (!this.#isValidCalendarParts(Number(match[1]), Number(match[2]), Number(match[3]))) return false;
    if (Number(match[4]) > 23 || Number(match[5]) > 59 || Number(match[6]) > 59) return false;
    return !Number.isNaN(Date.parse(value));
  }

  #isValidCalendarParts(year, month, day) {
    if (month < 1 || month > 12 || day < 1 || day > 31) return false;
    const date = new Date(Date.UTC(year, month - 1, day));
    return date.getUTCFullYear() === year && date.getUTCMonth() === month - 1 && date.getUTCDate() === day;
  }

  #violation(code, constraint='') {
    return { code, constraint };
  }

  #result(outcome, reasonCode, violations) {
    return {
      outcome,
      reason_code: reasonCode,
      violations: definitionVerificationClone(violations ?? [])
    };
  }
}

globalThis.DefinitionValueValidator = DefinitionValueValidator;
