// v0.18.18-test-runner-expecteddef-compare-strategy-pattern
// ExpectedDef -> CompareStrategy resolver for responsibility Expected tests.
//
// ExpectedDef is a test-pattern design key. The Editor side may use the same
// key to select a FieldGroupStrategy, while this mjs runner resolves it into
// CompareStrategy entries. Keep those layers separate.

import { isDeepStrictEqual } from 'node:util';

export function toDisplayValue(value) {
  if (typeof value === 'string') return value;
  return JSON.stringify(value);
}

function ok(message = 'OK') {
  return { pass: true, message };
}

function ng(message) {
  return { pass: false, message };
}

function valueLabel(value) {
  return toDisplayValue(value);
}

export const CompareStrategies = Object.freeze({
  ArrayEquals: Object.freeze({
    strategy_id: 'ArrayEquals',
    compare({ expected, actual, key }) {
      const pass = Array.isArray(expected) && Array.isArray(actual) && isDeepStrictEqual(actual, expected);
      return pass
        ? ok()
        : ng(`${key} failed by ArrayEquals: expected ${valueLabel(expected)}, actual ${valueLabel(actual)}`);
    }
  }),

  JsonEquals: Object.freeze({
    strategy_id: 'JsonEquals',
    compare({ expected, actual, key }) {
      const pass = isDeepStrictEqual(actual, expected);
      return pass
        ? ok()
        : ng(`${key} failed by JsonEquals: expected ${valueLabel(expected)}, actual ${valueLabel(actual)}`);
    }
  }),

  ValueEquals: Object.freeze({
    strategy_id: 'ValueEquals',
    compare({ expected, actual, key }) {
      const isScalar = (value) => value === null
        || typeof value === 'string'
        || typeof value === 'number'
        || typeof value === 'boolean';
      const pass = isScalar(expected) && isScalar(actual) && Object.is(actual, expected);
      return pass
        ? ok()
        : ng(`${key} failed by ValueEquals: expected ${valueLabel(expected)}, actual ${valueLabel(actual)}`);
    }
  }),

  CsvEquals: Object.freeze({
    strategy_id: 'CsvEquals',
    compare({ expected, actual, key }) {
      const pass = typeof expected === 'string' && typeof actual === 'string' && actual === expected;
      return pass
        ? ok()
        : ng(`${key} failed by CsvEquals: expected ${valueLabel(expected)}, actual ${valueLabel(actual)}`);
    }
  }),

  MarkdownEquals: Object.freeze({
    strategy_id: 'MarkdownEquals',
    compare({ expected, actual, key }) {
      const pass = typeof expected === 'string' && typeof actual === 'string' && actual === expected;
      return pass
        ? ok()
        : ng(`${key} failed by MarkdownEquals: expected ${valueLabel(expected)}, actual ${valueLabel(actual)}`);
    }
  }),

  ImageEquals: Object.freeze({
    strategy_id: 'ImageEquals',
    compare({ key }) {
      return ng(`${key} failed by ImageEquals: image comparison is not implemented in v0.18.18`);
    }
  }),

  BooleanEquals: Object.freeze({
    strategy_id: 'BooleanEquals',
    compare({ expected, actual, key }) {
      const pass = typeof expected === 'boolean' && typeof actual === 'boolean' && actual === expected;
      return pass
        ? ok()
        : ng(`${key} failed by BooleanEquals: expected ${valueLabel(expected)}, actual ${valueLabel(actual)}`);
    }
  }),

  StringEquals: Object.freeze({
    strategy_id: 'StringEquals',
    compare({ expected, actual, key }) {
      const pass = typeof expected === 'string' && typeof actual === 'string' && actual === expected;
      return pass
        ? ok()
        : ng(`${key} failed by StringEquals: expected ${valueLabel(expected)}, actual ${valueLabel(actual)}`);
    }
  })
});

export const ExpectedDefCompareStrategyRegistry = Object.freeze({
  RuleExpectedDef: Object.freeze({
    expected_def_type: 'RuleExpectedDef',
    purpose: 'ルール期待値。主に生成ルール・列ルールなどの配列/JSON結果を比較する。',
    fields: Object.freeze({
      field_names: 'ArrayEquals'
    })
  }),

  ScalarExpectedDef: Object.freeze({
    expected_def_type: 'ScalarExpectedDef',
    purpose: '単一Scalar期待値。計算値・件数・boolean等のExpected Valueを比較する。',
    fields: Object.freeze({
      value: 'ValueEquals'
    })
  }),

  StateExpectedDef: Object.freeze({
    expected_def_type: 'StateExpectedDef',
    purpose: '状態期待値。検索後状態・行ID・元indexなどを比較する。',
    fields: Object.freeze({
      row_ids: 'ArrayEquals',
      indexes: 'ArrayEquals'
    })
  }),

  CsvExpectedDef: Object.freeze({
    expected_def_type: 'CsvExpectedDef',
    purpose: 'CSV期待値。列順、BOM有無、CSV本文を比較する。',
    fields: Object.freeze({
      field_names: 'ArrayEquals',
      has_bom: 'BooleanEquals',
      csv_text: 'CsvEquals',
      csv_without_bom: 'CsvEquals',
      csv_preview: 'CsvEquals'
    })
  }),

  ErrorExpectedDef: Object.freeze({
    expected_def_type: 'ErrorExpectedDef',
    purpose: 'エラー期待値。エラーそのもの、または不正入力でも安全に返す値を比較する。',
    fields: Object.freeze({
      field_names: 'ArrayEquals',
      error_name: 'StringEquals',
      error_message: 'StringEquals',
      error_code: 'StringEquals',
      path: 'StringEquals',
      message: 'StringEquals'
    })
  })
});

function inferExpectedDefType(pattern) {
  const expected = pattern?.expected ?? {};
  if ('csv_text' in expected || 'csv_without_bom' in expected || 'has_bom' in expected || 'csv_preview' in expected) {
    return { expectedDefType: 'CsvExpectedDef', source: 'inferred_from_expected_keys' };
  }
  if ('row_ids' in expected || 'indexes' in expected) {
    return { expectedDefType: 'StateExpectedDef', source: 'inferred_from_expected_keys' };
  }
  if ('error_name' in expected || 'error_message' in expected || 'error_code' in expected) {
    return { expectedDefType: 'ErrorExpectedDef', source: 'inferred_from_expected_keys' };
  }
  return { expectedDefType: 'RuleExpectedDef', source: 'default_rule_expected_def' };
}

export function resolveExpectedDefType(pattern) {
  const declared = pattern?.expected_def_type ?? pattern?.expected_def ?? pattern?.expectedDef ?? pattern?.expected_type_cd;
  if (declared) {
    return { expectedDefType: declared, source: 'declared' };
  }
  return inferExpectedDefType(pattern);
}

export function resolveExpectedDefStrategy(pattern) {
  const { expectedDefType, source } = resolveExpectedDefType(pattern);
  const expectedDefStrategy = ExpectedDefCompareStrategyRegistry[expectedDefType];

  if (!expectedDefStrategy) {
    throw new Error(`Unsupported expected_def_type: ${expectedDefType}`);
  }

  return { expectedDefType, expectedDefTypeSource: source, expectedDefStrategy };
}

function resolveCompareStrategy(expectedDefStrategy, expectedDefType, key) {
  const compareStrategyId = expectedDefStrategy.fields?.[key];

  if (!compareStrategyId) {
    throw new Error(`Unsupported expected key for ${expectedDefType}: ${key}`);
  }

  const compareStrategy = CompareStrategies[compareStrategyId];

  if (!compareStrategy) {
    throw new Error(`CompareStrategy not registered: ${compareStrategyId}`);
  }

  return { compareStrategyId, compareStrategy };
}

export function buildExpectedChecks(pattern, actual) {
  const expected = pattern.expected ?? {};
  const { expectedDefType, expectedDefTypeSource, expectedDefStrategy } = resolveExpectedDefStrategy(pattern);

  return Object.entries(expected).map(([key, expectedValue]) => {
    const actualValue = actual?.[key];
    const { compareStrategyId, compareStrategy } = resolveCompareStrategy(expectedDefStrategy, expectedDefType, key);
    const compareResult = compareStrategy.compare({
      key,
      expected: expectedValue,
      actual: actualValue,
      pattern,
      actualObject: actual
    });

    return {
      check_id: `${pattern.test_pattern_id}.${key}`,
      name: key,
      target: key,
      type: 'compareStrategy',
      expected_def_type: expectedDefType,
      expected_def_type_source: expectedDefTypeSource,
      compare_strategy: compareStrategyId,
      responsibility_cd: pattern.responsibility_cd,
      test_pattern_id: pattern.test_pattern_id,
      expected: toDisplayValue(expectedValue),
      actual: toDisplayValue(actualValue),
      expected_raw: expectedValue,
      actual_raw: actualValue,
      pass: compareResult.pass === true,
      message: compareResult.message ?? (compareResult.pass ? 'OK' : `${key} failed`)
    };
  });
}
