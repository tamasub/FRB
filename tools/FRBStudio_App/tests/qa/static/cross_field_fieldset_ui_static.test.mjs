import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import test from 'node:test';

const root = process.cwd();
const readText = relativePath => fs.readFileSync(path.join(root, relativePath), 'utf8');
const readJson = relativePath => JSON.parse(readText(relativePath));

test('ViewDef Schema formalizes caption-optional full-width FieldSet references', () => {
  const schema = readJson('data/json/00_rules/frb_view_def_schema_v0_9.json');
  const section = schema.$defs.section;
  const fieldSet = schema.$defs.fieldSet;

  assert.equal(section.properties.fieldSets.items.$ref, '#/$defs/fieldSet');
  assert.deepEqual(fieldSet.required, ['id', 'fields']);
  assert.equal(fieldSet.properties.caption.type, 'string');
  assert.equal(fieldSet.properties.caption.default, '');
  assert.equal(fieldSet.properties.fields.uniqueItems, true);
  assert.match(fieldSet.description, /3列フル幅/);
  assert.match(fieldSet.description, /caption.*任意/);
});

test('Cross Field ViewDef groups the positive relation as OK condition and preserves canonical codes behind human labels', () => {
  const viewDef = readJson('defs/fielddefs/frb_fft_measurement_field_definitions_view_def_v0_1.json');
  const view = viewDef.views.find(item => item.id === 'frb_fft_measurement_cross_field_constraints_v0_1');
  const section = view.sections.find(item => item.id === 'cross_field_constraints');
  const fieldSet = section.fieldSets.find(item => item.id === 'accept_condition');
  const fieldByName = Object.fromEntries(section.fields.map(field => [field.field, field]));

  assert.equal(fieldSet.caption, 'OK条件');
  assert.deepEqual(fieldSet.fields, ['left_field_path', 'operator', 'right_field_path', 'unset_policy']);

  assert.deepEqual(
    fieldByName.operator.options.map(item => [item.cd, item.name]),
    [['LT', '<'], ['LTE', '<='], ['EQ', '='], ['NE', '!='], ['GTE', '>='], ['GT', '>']]
  );
  assert.deepEqual(
    fieldByName.unset_policy.options.map(item => [item.cd, item.name]),
    [
      ['ACCEPT_IF_EITHER_UNSET', '未設定ならOK'],
      ['REJECT_IF_EITHER_UNSET', '未設定ならNG']
    ]
  );
});

test('Detail Renderer treats FieldSet as one full-width block and omits empty legend', () => {
  const runtime = readText('wwwroot/js/runtime/detail_save.js');
  const css = readText('wwwroot/styles.css');

  assert.match(runtime, /function detailFieldSetConfigs\(/);
  assert.match(runtime, /function createDetailFieldSet\(/);
  assert.match(runtime, /if \(caption\) \{[\s\S]*createElement\('legend'\)/);
  assert.match(runtime, /detail-fieldset-captionless/);
  assert.match(runtime, /renderDetailBodyFields\(form, row, gd\)/);
  assert.match(css, /\.detail-fieldset \{[\s\S]*grid-column:\s*1 \/ -1;/);
  assert.match(css, /\.detail-fieldset-grid \{[\s\S]*grid-template-columns:\s*repeat\(3, minmax\(0, 1fr\)\)/);
});

test('Cross Field Preview reuses ViewDef option label and shows Expected as OK/NG', () => {
  const component = readText('wwwroot/js/components/definition/cross_field_test_preview_component.js');

  assert.match(component, /displayOperator\(value\)/);
  assert.match(component, /optionLabelForValue\(value, operatorField\)/);
  assert.match(component, /operator:\s*this\.displayOperator/);
  assert.doesNotMatch(component, /LT\s*:\s*['"]<['"]/);
  assert.match(component, /if \(value === 'ACCEPT'\) return 'OK'/);
  assert.match(component, /if \(value === 'REJECT'\) return 'NG'/);
});

test('ViewDef Generation Rules records full-width / optional-caption / no-redundant-summary FieldSet policy', () => {
  const rules = readJson('data/json/00_rules/frb_viewdef_generation_rules_data_v0_1.json');
  const rule = rules.rules.find(item => item.rule_id === 'viewdef_rule_10_02');

  assert.ok(rule);
  assert.equal(rule.verification_status, '確認済み');
  assert.equal(rule.approval_decision, '承認する');
  assert.match(rule.body, /3列フル幅/);
  assert.match(rule.body, /caption.*任意/);
  assert.match(rule.body, /要約文を重ねない/);
  assert.equal(rules.rule_count, rules.rules.length);
});

test('Test Evidence Rules formalize Cross Field 3-shape interior values and two-value unset policy', () => {
  const rules = readJson('data/json/00_rules/frb_test_evidence_rules_data_v0_2.json');
  const rule = rules.rules.find(item => item.rule_id === 'test_evidence_rule_021');

  assert.ok(rule);
  assert.equal(rule.verification_status, '確認済み');
  assert.equal(rule.approval_decision, '承認する');
  assert.match(rule.body, /LEFT < RIGHT/);
  assert.match(rule.body, /MID\s+= midpoint/);
  assert.match(rule.body, /LOW\s+= midpoint/);
  assert.match(rule.body, /HIGH\s+= midpoint/);
  assert.match(rule.body, /ACCEPT_IF_EITHER_UNSET/);
  assert.match(rule.body, /REJECT_IF_EITHER_UNSET/);
  assert.match(rule.body, /警告という第三状態/);
  assert.equal(rules.rule_count, rules.rules.length);
});
