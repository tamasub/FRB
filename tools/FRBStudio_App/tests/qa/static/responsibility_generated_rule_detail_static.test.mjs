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

function deriveSearch(documentOverride=null) {
  const sandbox = loadServiceSandbox();
  const document = documentOverride ?? readJson('data/json/03_tests/responsibilities/responsibility_data_v0_2.json');
  const responsibility = document.responsibilities.find(item => item.responsibility_cd === 'search_filter');
  const inputData = readJson('data/json/80_frb/frb_fft_search_test_data_v0_1.json');
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
