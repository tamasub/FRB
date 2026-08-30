import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';

const ROOT = process.cwd();

test('Main grid preserves numeric zero as visible 0 instead of blank', () => {
  const source = fs.readFileSync(path.join(ROOT, 'wwwroot/js/renderers/grid_detail.js'), 'utf8');
  assert.match(source, /td\.textContent = value === 0 \? '0' : formatValue\(value, f\);/);
});

test('Responsibility Diff result keeps diff_count zero as numeric data', () => {
  const diff = JSON.parse(fs.readFileSync(
    path.join(ROOT, 'data/json/03_tests/responsibilities/results/search_filter.diff.json'),
    'utf8',
  ));
  assert.ok(diff.test_pattern_results.length > 0);
  assert.ok(diff.test_pattern_results.every(row => Number.isInteger(row.diff_count)));
  assert.ok(diff.test_pattern_results.some(row => row.diff_count === 0));
});
