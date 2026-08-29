import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

import {
  CompareStrategies,
  ExpectedDefCompareStrategyRegistry,
  buildExpectedChecks,
} from '../../responsibilities/lib/responsibility_expected_compare_strategies.mjs';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const APP_ROOT = path.resolve(HERE, '../../..');

test('ScalarExpectedDef uses ValueEquals instead of JsonEquals', () => {
  assert.equal(ExpectedDefCompareStrategyRegistry.ScalarExpectedDef.fields.value, 'ValueEquals');

  const pass = buildExpectedChecks({
    test_pattern_id: 'scalar_number',
    expected_def_type: 'ScalarExpectedDef',
    expected: { value: 146 },
  }, { value: 146 });

  assert.equal(pass.length, 1);
  assert.equal(pass[0].compare_strategy, 'ValueEquals');
  assert.equal(pass[0].pass, true);

  const typeMismatch = buildExpectedChecks({
    test_pattern_id: 'scalar_number_type_mismatch',
    expected_def_type: 'ScalarExpectedDef',
    expected: { value: 146 },
  }, { value: '146' });

  assert.equal(typeMismatch[0].compare_strategy, 'ValueEquals');
  assert.equal(typeMismatch[0].pass, false);
});

test('ValueEquals accepts scalar values and rejects object/array values', () => {
  assert.equal(CompareStrategies.ValueEquals.compare({ key: 'v', expected: false, actual: false }).pass, true);
  assert.equal(CompareStrategies.ValueEquals.compare({ key: 'v', expected: 'A', actual: 'A' }).pass, true);
  assert.equal(CompareStrategies.ValueEquals.compare({ key: 'v', expected: null, actual: null }).pass, true);
  assert.equal(CompareStrategies.ValueEquals.compare({ key: 'v', expected: [1], actual: [1] }).pass, false);
  assert.equal(CompareStrategies.ValueEquals.compare({ key: 'v', expected: { a: 1 }, actual: { a: 1 } }).pass, false);
});

test('Responsibility Selenium runner pacing is configurable after value input', () => {
  const settingsPath = path.join(APP_ROOT, 'SeleniumTaste/config/selenium_runner_settings_v0_1.json');
  const settings = JSON.parse(fs.readFileSync(settingsPath, 'utf8'));
  assert.equal(settings.schema_version, 'selenium_runner_settings_v0_1');
  assert.equal(typeof settings.timing.after_value_input_ms, 'number');
  assert.ok(settings.timing.after_value_input_ms >= 0);

  const runner = fs.readFileSync(path.join(APP_ROOT, 'SeleniumTaste/responsibility_selenium_runner.js'), 'utf8');
  assert.match(runner, /pauseAfterValueInput/);
  assert.match(runner, /await pauseAfterValueInput\(\);/);
  assert.match(runner, /printSeleniumRunnerTiming/);
});
