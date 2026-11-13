import test from 'node:test';
import assert from 'node:assert/strict';
import { createRequire } from 'node:module';
import path from 'node:path';

const require = createRequire(import.meta.url);
const ROOT = process.cwd();
const { buildResponsibilityExecutionPlan, formatPlanSummary } = require(path.join(ROOT, 'SeleniumTaste/responsibility_test_plan.js'));
const { formatInputPlan, uniqueRequests } = require(path.join(ROOT, 'SeleniumTaste/responsibility_input_plan.js'));

test('Search execution plan carries Rule-driven Input Generation Plan', () => {
  const plan = buildResponsibilityExecutionPlan({ responsibilityCd: 'search_filter' });
  assert.equal(plan.execution_kind, 'SEARCH_FILTER');
  assert.equal(plan.execution_ready, true);
  assert.equal(plan.input_generation_plan.policy, 'RULE_DRIVEN_AI_DRAFT_HUMAN_APPROVAL');
  assert.equal(plan.input_generation_plan.generation_needed, false);
  assert.equal(plan.input_generation_plan.augmentation_recommended, false);
  assert.equal(plan.input_generation_plan.human_approval_required, true);
  assert.match(formatPlanSummary(plan), /Input Rule: READY \/ Human Approval=REQUIRED/);
  assert.match(formatInputPlan(plan), /AI Draft: NOT_REQUIRED/);
  assert.deepEqual(uniqueRequests(plan), []);
});
