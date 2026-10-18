import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import test from 'node:test';

function load(rel) { return JSON.parse(readFileSync(rel, 'utf8')); }
const canonical = load('defs/frb/fft_log_view_def_v0_2.json');
const dataCopy = load('data/json/80_frb/fft_log_view_def_v0_2.json');
const getGrid = obj => obj.views.find(v => v.id === 'fft_log_main').sections.find(s => s.id === 'tsBuf');

test('FFT log fieldSets use section-level references, not parent IDs in each Field', () => {
  const grid = getGrid(canonical);
  assert.deepEqual(grid.fieldSets.map(g => g.id), ['fft_time_input','fft_peak_response','fft_phase_state','fft_band_a']);
  const names = grid.fields.map(f => f.field);
  const grouped = grid.fieldSets.flatMap(g => g.fields);
  for (const name of grouped) assert.ok(names.includes(name), `missing ${name}`);
  assert.equal(new Set(grouped).size, grouped.length, 'a field must not be in two groups');
  for (const f of grid.fields) assert.equal(f.parentGroupId, undefined);
  assert.equal(grid.keyField, 't');
});

test('FFT fieldSets are aligned with the sample data-facing ViewDef copy', () => {
  assert.deepEqual(getGrid(dataCopy).fieldSets, getGrid(canonical).fieldSets);
});

test('FFT sample only groups scalar fields; child grids remain ungrouped', () => {
  const grid = getGrid(canonical);
  const grouped = new Set(grid.fieldSets.flatMap(g => g.fields));
  for (const f of grid.fields.filter(f => f.type === 'objectArray')) assert.ok(!grouped.has(f.field));
});
