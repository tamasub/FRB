// v0.15.5: ViewDef context read contract recognizer
// This file recognizes ViewDef-level context.read_contract definitions.
// It does not fetch external context automatically; it only normalizes the contract
// so AI/Human/Runtime can share the same structure safely.

function contextContractAsArray(value) {
  if (Array.isArray(value)) return value.filter(x => x != null);
  if (value == null) return [];
  return [value];
}

function contextContractString(value, fallback='') {
  const s = String(value ?? '').trim();
  return s || fallback;
}

function contextContractBool(value, fallback=false) {
  if (typeof value === 'boolean') return value;
  if (value == null || value === '') return fallback;
  const s = String(value).trim().toLowerCase();
  if (['true', '1', 'yes', 'y', 'on'].includes(s)) return true;
  if (['false', '0', 'no', 'n', 'off'].includes(s)) return false;
  return fallback;
}

function normalizeContextRefContract(raw, index=0, defaults={}) {
  if (!raw || typeof raw !== 'object' || Array.isArray(raw)) return null;
  const refId = contextContractString(raw.ref_id ?? raw.context_ref_id ?? raw.id, `context_ref_${index + 1}`);
  const required = contextContractBool(raw.required, contextContractBool(defaults.required, false));
  const failurePolicy = contextContractString(
    raw.failure_policy ?? raw.failurePolicy ?? defaults.failure_policy ?? defaults.failurePolicy,
    required ? 'stop_and_report' : 'warn_and_continue'
  );
  return {
    ref_id: refId,
    title: contextContractString(raw.title ?? raw.name, refId),
    target_path: contextContractString(raw.target_path ?? raw.targetPath ?? raw.path ?? raw.file ?? raw.url),
    read_timing: contextContractString(raw.read_timing ?? raw.readTiming ?? raw.timing ?? defaults.default_timing ?? defaults.defaultTiming, 'before_load'),
    required,
    failure_policy: failurePolicy,
    trust: contextContractString(raw.trust ?? raw.trust_category ?? raw.trustCategory ?? defaults.trust, required ? 'canonical' : 'reference'),
    purpose: contextContractString(raw.purpose ?? raw.reason ?? raw.description),
    note: contextContractString(raw.note ?? raw.notes)
  };
}

function normalizeRowContextContract(raw) {
  if (!raw || typeof raw !== 'object' || Array.isArray(raw)) return null;
  return {
    enabled: contextContractBool(raw.enabled, true),
    data_path: contextContractString(raw.data_path ?? raw.dataPath ?? raw.path, '$.context_refs'),
    row_ref_field: contextContractString(raw.row_ref_field ?? raw.rowRefField ?? raw.ref_field ?? raw.refField),
    id_field: contextContractString(raw.id_field ?? raw.idField, 'context_ref_id'),
    title_field: contextContractString(raw.title_field ?? raw.titleField, 'title'),
    target_path_field: contextContractString(raw.target_path_field ?? raw.targetPathField, 'target_path'),
    read_timing_field: contextContractString(raw.read_timing_field ?? raw.readTimingField ?? raw.timing_field ?? raw.timingField, 'read_timing'),
    failure_policy_field: contextContractString(raw.failure_policy_field ?? raw.failurePolicyField, 'failure_policy'),
    trust_field: contextContractString(raw.trust_field ?? raw.trustField, 'trust'),
    purpose_field: contextContractString(raw.purpose_field ?? raw.purposeField, 'purpose')
  };
}

function normalizeReadContract(raw, sourceLabel='viewdef') {
  if (!raw || typeof raw !== 'object' || Array.isArray(raw)) return null;
  const defaults = {
    default_timing: raw.default_timing ?? raw.defaultTiming ?? 'before_load',
    failure_policy: raw.failure_policy ?? raw.failurePolicy ?? 'stop_and_report',
    trust: raw.trust ?? 'canonical'
  };
  const requiredRefs = [
    ...contextContractAsArray(raw.required_refs ?? raw.requiredRefs),
    ...contextContractAsArray(raw.preflight_rules ?? raw.preflightRules)
  ].map((item, i) => normalizeContextRefContract(item, i, { ...defaults, required: true })).filter(Boolean);
  const optionalRefs = contextContractAsArray(raw.optional_refs ?? raw.optionalRefs)
    .map((item, i) => normalizeContextRefContract(item, i, { ...defaults, required: false })).filter(Boolean);

  return {
    source: sourceLabel,
    enabled: contextContractBool(raw.enabled, true),
    contract_id: contextContractString(raw.contract_id ?? raw.contractId ?? raw.id, `${sourceLabel}_read_contract`),
    description: contextContractString(raw.description ?? raw.summary),
    default_timing: contextContractString(defaults.default_timing, 'before_load'),
    failure_policy: contextContractString(defaults.failure_policy, 'stop_and_report'),
    required_refs: requiredRefs,
    optional_refs: optionalRefs,
    row_context: normalizeRowContextContract(raw.row_context ?? raw.rowContext ?? raw.row_context_refs ?? raw.rowContextRefs),
    notes: contextContractString(raw.notes ?? raw.note)
  };
}

function readContractFromObject(obj, sourceLabel) {
  const raw = obj?.context?.read_contract ?? obj?.context?.readContract ?? obj?.read_contract ?? obj?.readContract ?? null;
  return normalizeReadContract(raw, sourceLabel);
}

function extractViewDefReadContract(defObj) {
  const contracts = [];
  const rootContract = readContractFromObject(defObj, 'viewdef');
  if (rootContract) contracts.push(rootContract);
  (defObj?.views ?? []).forEach((view, index) => {
    const label = `view:${view?.id || index + 1}`;
    const c = readContractFromObject(view, label);
    if (c) contracts.push(c);
  });
  const requiredRefs = contracts.flatMap(c => c.required_refs ?? []);
  const optionalRefs = contracts.flatMap(c => c.optional_refs ?? []);
  return {
    enabled: contracts.some(c => c.enabled !== false),
    contracts,
    required_refs: requiredRefs,
    optional_refs: optionalRefs,
    row_contexts: contracts.map(c => c.row_context).filter(Boolean)
  };
}

function logViewDefReadContract(contract) {
  if (!contract || !contract.contracts?.length) return;
  console.info(
    `[ViewDef read_contract] contracts=${contract.contracts.length}, required_refs=${contract.required_refs.length}, row_contexts=${contract.row_contexts.length}`,
    contract
  );
}
