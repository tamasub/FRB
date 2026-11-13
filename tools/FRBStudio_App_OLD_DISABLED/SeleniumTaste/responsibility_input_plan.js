'use strict';

// Rule-driven Test Input planning boundary.
// This tool never edits/approves Test Input. It exposes the machine-evaluated
// Input Requirements and, when needed, the exact AI Input Generation Request.

const { buildResponsibilityExecutionPlan } = require('./responsibility_test_plan');

function uniqueRequests(plan) {
  const result = [];
  const seen = new Set();
  for (const item of (plan?.search_cases ?? [])) {
    const request = item?.ai_input_generation_request;
    if (!request || request.status === 'NOT_REQUIRED') continue;
    const key = `${request.field_path}::${request.source_rule_id}::${request.status}`;
    if (seen.has(key)) continue;
    seen.add(key);
    result.push(request);
  }
  return result;
}

function formatInputPlan(plan) {
  const inputPlan = plan?.input_generation_plan ?? null;
  if (!inputPlan) return 'Input Generation Plan: N/A';
  const lines = [
    `Responsibility: ${plan.responsibility_cd} / ${plan.responsibility_name}`,
    `Input: ${inputPlan.input_file} (${inputPlan.current_input_approval_status})`,
    `Policy: ${inputPlan.policy}`,
    `Human Approval: ${inputPlan.human_approval_required ? 'REQUIRED' : 'NO'}`,
    `AI Draft: ${inputPlan.generation_needed ? 'REQUIRED' : inputPlan.augmentation_recommended ? 'OPTIONAL_AUGMENTATION' : 'NOT_REQUIRED'}`,
  ];
  for (const field of (inputPlan.fields ?? [])) {
    lines.push(
      `Field: ${field.field_path} / ${field.status} / RequiredMissing=${field.missing_required?.length ?? 0} / RecommendedMissing=${field.missing_recommended?.length ?? 0}`
    );
  }
  return lines.join('\n');
}

if (require.main === module) {
  const responsibilityCd = process.argv[2] || 'search_filter';
  const plan = buildResponsibilityExecutionPlan({ responsibilityCd });
  if (plan.execution_kind !== 'SEARCH_FILTER') {
    throw new Error(`Rule-driven Search Input plan requires SEARCH_FILTER responsibility: ${plan.execution_kind}`);
  }
  console.log(formatInputPlan(plan));
  if (process.argv.includes('--requests')) {
    const requests = uniqueRequests(plan);
    console.log(`AI Input Generation Requests: ${requests.length}`);
    console.log(JSON.stringify(requests, null, 2));
  } else if (process.argv.includes('--json')) {
    console.log(JSON.stringify(plan.input_generation_plan, null, 2));
  }
}

module.exports = { formatInputPlan, uniqueRequests };
