import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import test from 'node:test';

const root = process.cwd();
const readJson = (relativePath) => JSON.parse(fs.readFileSync(path.join(root, relativePath), 'utf8'));

function normalizeFieldPath(dataPath, field) {
  const base = String(dataPath || '$').replace(/\[\]$/, '');
  return base === '$' ? `$.${field}` : `${base}[].${field}`;
}

test('FRB FFT sample Data -> ViewDef -> FieldDef reference chain resolves', () => {
  const dataPath = 'data/json/80_frb/frb_fft_field_definition_sample_data_v0_1.json';
  const data = readJson(dataPath);
  const viewDefPath = `defs/${data.view_def}`;
  assert.ok(fs.existsSync(path.join(root, viewDefPath)), viewDefPath);

  const viewDef = readJson(viewDefPath);
  assert.equal(viewDef.item_definition_ref, 'samples/frb_fft_measurement_field_definitions_v0_2.json');

  const fieldDefPath = `fielddefs/${viewDef.item_definition_ref}`;
  assert.ok(fs.existsSync(path.join(root, fieldDefPath)), fieldDefPath);

  const fieldDef = readJson(fieldDefPath);
  assert.equal(fieldDef.target_document_type, data.document_type);
  assert.equal(fieldDef.target_schema_version, data.schema_version);
});

test('DATA_UPDATE_PERSIST setup points to the concrete Data/ViewDef/FieldDef trio', () => {
  const responsibility = readJson('data/json/03_tests/responsibilities/responsibility_data_v0_2.json');
  const target = responsibility.responsibilities.find((item) => item.responsibility_cd === 'data_update_persist');
  assert.ok(target);

  const setup = target.test_setup[0];
  assert.equal(setup.input_file, 'data/json/80_frb/frb_fft_field_definition_sample_data_v0_1.json');
  assert.equal(setup.view_def_file, 'defs/frb/frb_fft_field_definition_sample_view_def_v0_1.json');
  assert.equal(setup.field_definition_file, 'fielddefs/samples/frb_fft_measurement_field_definitions_v0_2.json');
  assert.equal(setup.target_resolution_policy, 'DATA_JSON_VIEW_DEF_FIELD_DEFINITION');

  for (const file of [setup.input_file, setup.view_def_file, setup.field_definition_file]) {
    assert.ok(fs.existsSync(path.join(root, file)), file);
  }
});

test('DATA_UPDATE_PERSIST FIRST/LAST patterns have distinct rows in both grid targets', () => {
  const data = readJson('data/json/80_frb/frb_fft_field_definition_sample_data_v0_1.json');
  assert.ok(data.measurement_sessions.length >= 2);
  assert.ok(data.acceptance_thresholds.length >= 2);
});

test('DATA_UPDATE_PERSIST target selectors resolve to editable explicit FieldDef candidates', () => {
  const responsibility = readJson('data/json/03_tests/responsibilities/responsibility_data_v0_2.json');
  const target = responsibility.responsibilities.find((item) => item.responsibility_cd === 'data_update_persist');
  const viewDef = readJson('defs/frb/frb_fft_field_definition_sample_view_def_v0_1.json');
  const fieldDef = readJson('fielddefs/samples/frb_fft_measurement_field_definitions_v0_2.json');

  const explicitPaths = new Set(fieldDef.field_definitions.map((item) => item.field_path));
  const candidatesByDataPath = new Map();

  for (const view of viewDef.views || []) {
    for (const section of view.sections || []) {
      const candidates = [];
      for (const field of section.fields || []) {
        const readonly = field.readonly === true || field.edit?.readonly === true;
        const fieldPath = normalizeFieldPath(section.dataPath, field.field);
        if (!readonly && explicitPaths.has(fieldPath)) candidates.push(fieldPath);
      }
      candidatesByDataPath.set(section.dataPath, candidates);
    }
  }

  const single = candidatesByDataPath.get('$.measurement_sessions') || [];
  const multi = candidatesByDataPath.get('$.acceptance_thresholds') || [];
  assert.ok(single.length > 0, 'measurement_sessions editable explicit fields');
  assert.ok(multi.length > 0, 'acceptance_thresholds editable explicit fields');
  assert.ok(single.includes('$.measurement_sessions[].note'));
  assert.ok(multi.includes('$.acceptance_thresholds[].note'));

  for (const pattern of target.test_pattern_definitions) {
    assert.ok(candidatesByDataPath.has(pattern.target_data_path), pattern.pattern_def_id);
    assert.ok(
      ['EDITABLE_EXPLICIT_NON_MULTILINE', 'EDITABLE_EXPLICIT_MULTILINE'].includes(pattern.field_selection_policy),
      pattern.pattern_def_id
    );
  }
});
