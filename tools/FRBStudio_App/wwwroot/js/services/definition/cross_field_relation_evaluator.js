// v0.18.45-definition-test-runner-diff-crossfield-e2e
// Executes one derived Cross Field compare pattern against its resolved field contracts.

class CrossFieldRelationEvaluator {
  constructor({ valueValidator=null }={}) {
    this.valueValidator = valueValidator ?? new DefinitionValueValidator();
  }

  evaluate(verification={}, pattern={}) {
    if (!verification || verification.status === 'INVALID') {
      return this.#result('UNRESOLVED', 'CROSS_FIELD_VERIFICATION_INVALID');
    }

    const leftInput = pattern?.input?.left ?? {};
    const rightInput = pattern?.input?.right ?? {};
    const leftActual = this.valueValidator.validate(verification.left_contract, {
      state: leftInput.state ?? 'VALUE',
      value: leftInput.value
    });
    const rightActual = this.valueValidator.validate(verification.right_contract, {
      state: rightInput.state ?? 'VALUE',
      value: rightInput.value
    });

    if (leftActual.outcome === 'REJECT' || rightActual.outcome === 'REJECT') {
      return this.#result('REJECT', 'CROSS_FIELD_INPUT_FIELD_CONTRACT_REJECTED', { left: leftActual, right: rightActual });
    }
    if (leftActual.outcome === 'UNRESOLVED' || rightActual.outcome === 'UNRESOLVED') {
      return this.#result('UNRESOLVED', 'CROSS_FIELD_INPUT_FIELD_CONTRACT_UNRESOLVED', { left: leftActual, right: rightActual });
    }

    const leftValue = leftInput.value;
    const rightValue = rightInput.value;
    if (leftValue === null || rightValue === null) {
      return this.#evaluateNullPolicy(verification.null_policy, { left: leftActual, right: rightActual });
    }

    const comparison = this.#compareValues(
      verification.left_contract?.value_family,
      verification.right_contract?.value_family,
      leftValue,
      rightValue
    );
    if (comparison === null) {
      return this.#result('UNRESOLVED', 'CROSS_FIELD_VALUES_NOT_COMPARABLE', { left: leftActual, right: rightActual });
    }

    const accepted = this.#operatorMatches(verification.operator, comparison);
    return this.#result(
      accepted ? 'ACCEPT' : 'REJECT',
      accepted ? 'CROSS_FIELD_RELATION_ACCEPTED' : 'CROSS_FIELD_RELATION_REJECTED',
      {
        left: leftActual,
        right: rightActual,
        comparison: comparison < 0 ? 'LT' : (comparison > 0 ? 'GT' : 'EQ'),
        operator: verification.operator
      }
    );
  }

  #evaluateNullPolicy(nullPolicy, details) {
    switch (String(nullPolicy ?? '').toUpperCase()) {
      case 'SKIP_IF_EITHER_NULL': return this.#result('ACCEPT', 'CROSS_FIELD_RELATION_SKIPPED_NULL', details);
      case 'REJECT_IF_EITHER_NULL': return this.#result('REJECT', 'CROSS_FIELD_RELATION_NULL_REJECTED', details);
      case 'DEFER_TO_FIELD_CONTRACTS': return this.#result('UNRESOLVED', 'CROSS_FIELD_RELATION_DEFERRED_TO_FIELD_CONTRACTS', details);
      default: return this.#result('UNRESOLVED', 'CROSS_FIELD_NULL_POLICY_UNSUPPORTED', details);
    }
  }

  #compareValues(leftFamily, rightFamily, left, right) {
    const numeric = new Set(['number', 'float', 'integer']);
    if (numeric.has(leftFamily) && numeric.has(rightFamily)) {
      if (typeof left !== 'number' || typeof right !== 'number') return null;
      return left === right ? 0 : (left < right ? -1 : 1);
    }

    const temporal = new Set(['date', 'datetime', 'instant']);
    if (temporal.has(leftFamily) && temporal.has(rightFamily)) {
      if (leftFamily === 'instant' || rightFamily === 'instant' || leftFamily !== rightFamily) {
        const a = Date.parse(String(left));
        const b = Date.parse(String(right));
        if (Number.isNaN(a) || Number.isNaN(b)) return null;
        return a === b ? 0 : (a < b ? -1 : 1);
      }
      const a = String(left);
      const b = String(right);
      return a === b ? 0 : (a < b ? -1 : 1);
    }

    if (leftFamily === 'string' && rightFamily === 'string') {
      const a = String(left);
      const b = String(right);
      return a === b ? 0 : (a < b ? -1 : 1);
    }

    return null;
  }

  #operatorMatches(operator, comparison) {
    switch (String(operator ?? '').toUpperCase()) {
      case 'LT': return comparison < 0;
      case 'LTE': return comparison <= 0;
      case 'GT': return comparison > 0;
      case 'GTE': return comparison >= 0;
      case 'EQ': return comparison === 0;
      case 'NE': return comparison !== 0;
      default: return false;
    }
  }

  #result(outcome, reasonCode, details={}) {
    return {
      outcome,
      reason_code: reasonCode,
      details: definitionVerificationClone(details)
    };
  }
}

globalThis.CrossFieldRelationEvaluator = CrossFieldRelationEvaluator;
