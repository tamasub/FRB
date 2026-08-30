import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';

const ROOT = process.cwd();
const readText = rel => fs.readFileSync(path.join(ROOT, rel), 'utf8');
const readJson = rel => JSON.parse(readText(rel));

function loadServiceSandbox() {
  const sandbox = { console, structuredClone, Date, JSON, Object, Array, Map, Set, Number, String, Boolean, Math, RegExp };
  sandbox.globalThis = sandbox;
  vm.createContext(sandbox);
  [
    'wwwroot/js/services/definition/definition_verification_common.js',
    'wwwroot/js/services/definition/field_contract_resolver.js',
    'wwwroot/js/services/definition/definition_value_validator.js',
    'wwwroot/js/services/responsibility/responsibility_test_preview_service.js'
  ].forEach(rel => vm.runInContext(readText(rel), sandbox, { filename: rel }));
  return sandbox;
}

function deriveSearch(documentOverride=null, inputOverride=null) {
  const sandbox = loadServiceSandbox();
  const document = documentOverride ?? readJson('data/json/03_tests/responsibilities/responsibility_data_v0_2.json');
  const responsibility = document.responsibilities.find(item => item.responsibility_cd === 'search_filter');
  const inputData = inputOverride ?? readJson('data/json/80_frb/frb_fft_search_test_data_v0_1.json');
  const viewDef = readJson('defs/frb/frb_fft_field_definition_sample_view_def_v0_1.json');
  const fieldDefinitionDocument = readJson('fielddefs/samples/frb_fft_measurement_field_definitions_v0_2.json');
  const registry = readJson('data/json/config/validation_type_registry_v0_1.json');
  const searchOperatorRegistry = readJson('data/json/config/search_operator_registry_v0_1.json');
  const service = new sandbox.ResponsibilityTestPreviewService({ registry });
  return JSON.parse(JSON.stringify(service.derive({
    responsibility,
    rootDocument: document,
    inputData,
    viewDef,
    fieldDefinitionDocument,
    registry,
    searchOperatorRegistry
  })));
}

test('Responsibility Search generation makes derivation rules canonical and AI fixture generation human-approved', () => {
  const document = readJson('data/json/03_tests/responsibilities/responsibility_data_v0_2.json');
  const search = document.test_generation_config.search_generation;
  const rules = search.criteria_derivation_rules;

  assert.match(document.policy.rule_first_generation, /ルール/);
  assert.match(document.policy.rule_first_generation, /AI生成/);
  assert.match(search.rule_first_policy, /ルール追加/);
  assert.match(search.fixture_generation_policy, /approved/);
  assert.equal(rules.length, 4);
  assert.ok(rules.every(rule => rule.rule_id && rule.strategy && rule.statement && rule.reason));
  assert.ok(rules.every(rule => Array.isArray(rule.fixture_requirements) && rule.fixture_requirements.length > 0));
  assert.ok(rules.every(rule => String(rule.ai_input_guidance ?? '').length > 0));
});

test('SEARCH_FILTER Generated Case exposes applied Rule and derivation trace, not only Criteria result', () => {
  const result = deriveSearch();
  assert.equal(result.status, 'READY');

  const byId = new Map(result.test_patterns.map(pattern => [pattern.pattern_id, pattern.generated_cases[0]]));
  const contains = byId.get('search_filter_string_contains');
  assert.equal(contains.criteria_derivation.rule_id, 'search_rule_string_repeated_else_first');
  assert.equal(contains.criteria_derivation.trace.basis, 'REPEATED_NON_BLANK');
  assert.deepEqual(contains.criteria_derivation.trace.selected_source_rows.map(item => item.index), [0, 2]);
  assert.equal(contains.criteria_derivation.trace.input_profile.row_count, 6);
  assert.equal(contains.criteria_derivation.trace.input_profile.blank_count, 1);
  assert.equal(contains.criteria_derivation.trace.result_coverage.coverage_kind, 'MATCH_AND_NON_MATCH');
  assert.equal(contains.criteria_derivation.trace.result_coverage.matched_count, 3);
  assert.equal(contains.criteria_derivation.trace.result_coverage.non_matched_count, 3);

  const between = byId.get('search_filter_number_between');
  assert.equal(between.criteria_derivation.rule_id, 'search_rule_between_repeated_pivot_range');
  assert.equal(between.criteria_derivation.trace.basis, 'REPEATED_PIVOT_TO_NEXT_GREATER');
  assert.deepEqual(between.criteria, { operator: 'between', from: 0.5, to: 0.9 });
});

test('SEARCH_FILTER does not silently invent Criteria when an applicable derivation rule is missing', () => {
  const document = readJson('data/json/03_tests/responsibilities/responsibility_data_v0_2.json');
  document.test_generation_config.search_generation.criteria_derivation_rules =
    document.test_generation_config.search_generation.criteria_derivation_rules
      .filter(rule => rule.rule_id !== 'search_rule_string_repeated_else_first');

  const result = deriveSearch(document);
  assert.equal(result.status, 'PARTIAL');
  assert.ok(result.issues.some(issue =>
    issue.code === 'SEARCH_PATTERN_DERIVATION_FAILED'
    && /derivation rule is missing/.test(issue.message)
  ));
});

test('Generated Preview uses row-click right detail panel and removes giant Generated JSON column', () => {
  const component = readText('wwwroot/js/components/responsibility/responsibility_test_preview_component.js');
  const css = readText('wwwroot/styles.css');
  const viewDef = readJson('defs/qa/tests/responsibilities/responsibility_view_def_v0_2.json');
  const section = viewDef.views.flatMap(view => view.sections ?? []).find(item => item.id === 'responsibilities');
  const preview = section.editorComponents.find(item => item.id === 'responsibility_generated_test_preview');

  assert.equal(component.includes("caption: 'Generated Cases / Input Snapshot / Criteria / Expected'"), false);
  assert.match(component, /responsibility-preview-master-detail/);
  assert.match(component, /★ 導出ルール \/ なぜこの検索値なのか/);
  assert.match(component, /① 対象項目の入力状況/);
  assert.match(component, /② 検索へ投入/);
  assert.match(component, /③ Expected Result/);
  assert.match(component, /criteria_derivation/);
  assert.match(css, /responsibility-generated-preview-card/);
  assert.match(component, /responsibility-preview-snapshot-col-index/);
  assert.match(component, /responsibility-preview-snapshot-col-row-id/);
  assert.match(css, /responsibility-preview-snapshot-col-index\s*\{\s*width:\s*52px;/);
  assert.match(css, /responsibility-preview-snapshot-col-row-id\s*\{\s*width:\s*190px;/);
  assert.equal(preview.config.detailPanel.enabled, true);
  assert.equal(preview.config.detailPanel.position, 'right');
});


test('Search Rule defines machine-readable Input Requirements and current approved fixture satisfies them', () => {
  const document = readJson('data/json/03_tests/responsibilities/responsibility_data_v0_2.json');
  const search = document.test_generation_config.search_generation;
  const rules = search.criteria_derivation_rules;

  assert.match(search.fixture_planning_policy, /Required不足/);
  assert.deepEqual(search.fixture_approval_flow, [
    'RULE',
    'INPUT_REQUIREMENT_EVALUATION',
    'AI_DRAFT_IF_REQUIRED',
    'HUMAN_REVIEW',
    'approved',
    'GENERATED_CASE',
    'RUNNER'
  ]);
  assert.ok(rules.every(rule =>
    Array.isArray(rule.input_requirement_rules)
    && rule.input_requirement_rules.length > 0
    && rule.input_requirement_rules.every(req => req.requirement_id && req.kind && req.severity && req.statement)
  ));

  const result = deriveSearch();
  assert.equal(result.status, 'READY');
  assert.equal(result.execution_ready, true);
  assert.equal(result.input_generation_plan.policy, 'RULE_DRIVEN_AI_DRAFT_HUMAN_APPROVAL');
  assert.equal(result.input_generation_plan.generation_needed, false);
  assert.equal(result.input_generation_plan.augmentation_recommended, false);
  assert.equal(result.input_generation_plan.human_approval_required, true);

  const allCases = result.test_patterns.flatMap(pattern => pattern.generated_cases ?? []);
  assert.equal(allCases.length, 13);
  assert.ok(allCases.every(item => item.generation_status === 'READY'));
  assert.ok(allCases.every(item => item.input_requirement_evaluation?.generation_needed === false));
  assert.ok(allCases.every(item => item.ai_input_generation_request?.status === 'NOT_REQUIRED'));
});

test('Search Rule blocks Criteria generation and emits AI Input Generation Request when Required Input is missing', () => {
  const input = readJson('data/json/80_frb/frb_fft_search_test_data_v0_1.json');
  input.measurement_sessions.forEach(row => {
    row.note = '';
    row.amplitude_g = 0.5;
  });

  const result = deriveSearch(null, input);
  assert.equal(result.status, 'PARTIAL');
  assert.equal(result.execution_ready, false);
  assert.equal(result.input_generation_plan.generation_needed, true);
  assert.ok(result.issues.some(issue => issue.code === 'SEARCH_INPUT_GENERATION_REQUIRED'));

  const byId = new Map(result.test_patterns.map(pattern => [pattern.pattern_id, pattern.generated_cases[0]]));
  const contains = byId.get('search_filter_string_contains');
  assert.equal(contains.generation_status, 'INPUT_GENERATION_REQUIRED');
  assert.equal(contains.criteria, null);
  assert.equal(contains.expected, null);
  assert.equal(contains.criteria_derivation.trace.basis, 'INPUT_REQUIREMENT_NOT_MET');
  assert.equal(contains.input_requirement_evaluation.status, 'GENERATION_REQUIRED');
  assert.ok(contains.input_requirement_evaluation.requirements.some(item =>
    item.requirement_id === 'string_non_blank_min_1'
    && item.status === 'MISSING_REQUIRED'
  ));
  assert.equal(contains.ai_input_generation_request.status, 'REQUIRED');
  assert.equal(contains.ai_input_generation_request.action, 'CREATE_OR_AUGMENT_TEST_INPUT_DRAFT');
  assert.equal(contains.ai_input_generation_request.approval_gate.generated_status, 'draft');
  assert.equal(contains.ai_input_generation_request.approval_gate.execution_requires, 'approved');
  assert.ok(contains.ai_input_generation_request.constraints.some(item => /対象Field以外/.test(item)));

  const between = byId.get('search_filter_number_between');
  assert.equal(between.generation_status, 'INPUT_GENERATION_REQUIRED');
  assert.ok(between.input_requirement_evaluation.requirements.some(item =>
    item.requirement_id === 'range_distinct_comparable_min_2'
    && item.status === 'MISSING_REQUIRED'
  ));
});

test('Generated Preview shows Rule Input Requirement evaluation and AI Draft/Human Approval gate', () => {
  const component = readText('wwwroot/js/components/responsibility/responsibility_test_preview_component.js');
  assert.match(component, /Rule → Input Requirement評価/);
  assert.match(component, /AI Input生成判定/);
  assert.match(component, /AI Input Generation Request/);
  assert.match(component, /Human Approval Gate/);
  assert.match(component, /INPUT_GENERATION_REQUIRED/);
});
