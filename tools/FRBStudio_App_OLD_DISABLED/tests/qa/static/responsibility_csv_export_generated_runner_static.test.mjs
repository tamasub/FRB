import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { createRequire } from 'node:module';

const ROOT = path.resolve(import.meta.dirname, '../../..');
const require = createRequire(import.meta.url);
const { buildResponsibilityExecutionPlan } = require(path.join(ROOT, 'SeleniumTaste/responsibility_test_plan.js'));

function readJson(rel) {
  return JSON.parse(fs.readFileSync(path.join(ROOT, rel), 'utf8'));
}

test('csv_export is one Guarantee -> N TestPatterns and derives CsvExpectedDef', () => {
  const doc = readJson('data/json/03_tests/responsibilities/responsibility_data_v0_2.json');
  const responsibility = doc.responsibilities.find(item => item.responsibility_cd === 'csv_export');
  assert.ok(responsibility);
  assert.equal(responsibility.guarantees.length, 1);
  assert.equal(responsibility.guarantees[0].guarantee_id, 'csv_export_g001');
  assert.equal(responsibility.test_pattern_definitions.length, 2);
  assert.ok(responsibility.test_pattern_definitions.every(item => item.guarantee_id === 'csv_export_g001'));
  assert.ok(responsibility.test_pattern_definitions.every(item => Array.isArray(item.filtered_row_indexes)));
  assert.ok(responsibility.test_pattern_definitions.every(item => !('expected_def_type' in item)));

  const plan = buildResponsibilityExecutionPlan({ responsibilityCd: 'csv_export' });
  assert.equal(plan.execution_kind, 'CSV_EXPORT');
  assert.equal(plan.expected_def_type, 'CsvExpectedDef');
  assert.equal(plan.summary.test_pattern_count, 2);
  assert.equal(plan.summary.generated_case_count, 2);
  assert.equal(plan.setup.input_approval_status, responsibility.test_setup[0].input_approval_status);
  assert.equal(plan.execution_ready, plan.setup.input_approval_status === 'approved');

  const all = plan.patterns.find(item => item.pattern_id === 'csv_export_all_rows');
  const filtered = plan.patterns.find(item => item.pattern_id === 'csv_export_filtered_rows');
  assert.ok(all);
  assert.ok(filtered);

  const expected = all.generated_cases[0].expected;
  assert.deepEqual(expected.field_names, ['row_id', 'title', 'score', 'note']);
  assert.equal(expected.has_bom, true);
  assert.ok(expected.csv_text.startsWith('\ufeff'));
  const expectedBody = [
    'row_id,title,score,note',
    'csv_001,"Alpha,One",10,"Line1\nLine2"',
    'csv_002,"Quote ""Beta""",20,Plain',
    'csv_003,Gamma,30,Tail',
    ''
  ].join('\r\n');
  assert.equal(expected.csv_without_bom, expectedBody);

  assert.equal(filtered.ui_filter.required, true);
  assert.equal(filtered.ui_filter.field, 'row_id');
  assert.equal(filtered.ui_filter.operator_id, 'not_equals');
  assert.deepEqual(filtered.ui_filter.criteria, { value: 'csv_003' });
  assert.deepEqual(filtered.ui_filter.expected_indexes, [0, 1]);
});

test('CSV fixture keeps key/hidden fields out of visible columns but generated expected injects key once', () => {
  const viewDef = readJson('defs/frb/frb_csv_export_test_view_def_v0_1.json');
  const section = viewDef.views[0].sections[0];
  const rowId = section.fields.find(item => item.field === 'row_id');
  const hidden = section.fields.find(item => item.field === 'hidden_note');
  assert.equal(section.keyField, 'row_id');
  assert.equal(rowId.grid.visible, false);
  assert.equal(hidden.grid.visible, false);

  const plan = buildResponsibilityExecutionPlan({ responsibilityCd: 'csv_export' });
  const names = plan.patterns[0].generated_cases[0].expected.field_names;
  assert.equal(names.filter(name => name === 'row_id').length, 1);
  assert.ok(!names.includes('hidden_note'));
});

test('CSV Selenium runner observes Blob/download boundary instead of calling CsvExporter directly', () => {
  const source = fs.readFileSync(path.join(ROOT, 'SeleniumTaste/responsibility_selenium_runner.js'), 'utf8');
  assert.match(source, /armCsvDownloadCapture/);
  assert.match(source, /blob\.arrayBuffer\(\)/);
  assert.match(source, /HTMLAnchorElement\.prototype\.click/);
  assert.match(source, /gridCsvExportBtn/);
  assert.match(source, /Download \$\{check\.name\}/);
  assert.doesNotMatch(source, /CsvExporter\.export/);
});

test('CSV scripts and Responsibility ViewDef options are registered', () => {
  const pkg = readJson('SeleniumTaste/package.json');
  assert.equal(pkg.scripts['test:responsibility:csv:plan'], 'node responsibility_test_plan.js csv_export');
  assert.equal(pkg.scripts['test:responsibility:csv'], 'node selenium_taste.js --responsibility csv_export');

  const viewDef = readJson('defs/qa/tests/responsibilities/responsibility_view_def_v0_2.json');
  const fields = viewDef.views.flatMap(view => view.sections ?? []).flatMap(section => section.fields ?? []);
  const patternField = fields.find(field => field.field === 'test_pattern_definitions');
  const columns = patternField.edit.subGrid.columns;
  assert.ok(columns.find(c => c.field === 'pattern_cd').options.includes('CSV_EXPORT'));
  assert.ok(columns.find(c => c.field === 'generation_mode').options.includes('CSV_EXPORT_CASE'));
  assert.ok(columns.find(c => c.field === 'expected_def_type').options.includes('CsvExpectedDef'));
  assert.ok(columns.find(c => c.field === 'row_scope'));
  const filteredIndexes = columns.find(c => c.field === 'filtered_row_indexes');
  assert.equal(filteredIndexes.type, 'json');
  assert.equal(filteredIndexes.control, 'textarea');
});


test('CSV Generated Preview does not require Field Definition / Validation Registry', () => {
  const component = fs.readFileSync(
    path.join(ROOT, 'wwwroot/js/components/responsibility/responsibility_test_preview_component.js'),
    'utf8'
  );
  assert.match(component, /mode !== 'AGGREGATE_SCALAR_CASE' && mode !== 'CSV_EXPORT_CASE'/);
  assert.doesNotMatch(component, /definitions\.some\(item => String\(item\?\.generation_mode \?\? ''\) !== 'AGGREGATE_SCALAR_CASE'\)/);
});
