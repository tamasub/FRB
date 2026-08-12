// v0.18.42-definition-verification-service
// Resolves Expected from a derived TestPattern + ResolvedFieldContract.

class ExpectedResolver {
  resolve(contract={}, pattern={}) {
    const rule = pattern.expectation_rule ?? {};
    const source = {
      field_path: contract.field_path ?? '',
      validation_type_id: contract.validation_type_id ?? '',
      registry_version: contract.source?.registry_version ?? '',
      validation_type_contract_version: contract.source?.validation_type_contract_version ?? '',
      constraint_ref: pattern.constraint_ref ?? ''
    };

    if (contract.resolution_status === 'INVALID') {
      return this.#expected('UNRESOLVED', 'FIELD_CONTRACT_INVALID', source);
    }

    switch (rule.type) {
      case 'required_policy':
        return this.#fromBooleanConstraint(contract, 'required', true, 'REQUIRED_MISSING_REJECTED', 'OPTIONAL_MISSING_ACCEPTED', source);
      case 'nullable_policy':
        return this.#fromBooleanConstraint(contract, 'nullable', false, 'NULL_REJECTED', 'NULL_ACCEPTED', source);
      case 'valid_value_contract':
        return this.#expected('ACCEPT', 'VALUE_CONTRACT_VALID_SAMPLE', source);
      case 'invalid_value_contract':
        return this.#expected('REJECT', 'VALUE_CONTRACT_INVALID_SAMPLE', source);
      case 'boundary_at':
        return this.#expected(rule.inclusive === false ? 'REJECT' : 'ACCEPT', rule.inclusive === false ? 'EXCLUSIVE_BOUNDARY_REJECTED' : 'INCLUSIVE_BOUNDARY_ACCEPTED', source);
      case 'boundary_outside':
        return this.#expected('REJECT', 'OUTSIDE_BOUNDARY_REJECTED', source);
      case 'length_at':
        return this.#expected('ACCEPT', 'LENGTH_BOUNDARY_ACCEPTED', source);
      case 'length_outside':
        return this.#expected('REJECT', 'LENGTH_OUTSIDE_BOUNDARY_REJECTED', source);
      default:
        return this.#expected('UNRESOLVED', 'EXPECTATION_RULE_UNRESOLVED', source);
    }
  }

  #fromBooleanConstraint(contract, constraintKey, rejectWhenValue, rejectReason, acceptReason, source) {
    const resolution = contract.constraint_resolutions?.find(item => item.constraint === constraintKey);
    if (!resolution || resolution.status !== 'RESOLVED') {
      return this.#expected('UNRESOLVED', `CONSTRAINT_UNRESOLVED:${constraintKey}`, source);
    }
    const rejected = resolution.resolved_value === rejectWhenValue;
    return this.#expected(rejected ? 'REJECT' : 'ACCEPT', rejected ? rejectReason : acceptReason, source);
  }

  #expected(outcome, reasonCode, source) {
    return {
      outcome,
      reason_code: reasonCode,
      source: definitionVerificationClone(source)
    };
  }
}

globalThis.ExpectedResolver = ExpectedResolver;
