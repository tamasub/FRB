import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';

const ROOT = path.resolve(import.meta.dirname, '../../..');
const read = rel => fs.readFileSync(path.join(ROOT, rel), 'utf8');

test('all Responsibility Pattern Def IDs are explicit, unique, and do not use _sample', () => {
  const document = JSON.parse(read('data/json/03_tests/responsibilities/responsibility_data_v0_2.json'));
  assert.match(document.policy.pattern_def_trace_contract, /Generated TestPattern/);
  assert.match(document.policy.pattern_def_trace_contract, /pattern_def_id/);
  assert.match(document.policy.pattern_def_trace_contract, /最終列/);

  for (const responsibility of document.responsibilities ?? []) {
    const guaranteeIds = new Set((responsibility.guarantees ?? []).map(item => item.guarantee_id));
    const ids = [];
    for (const patternDef of responsibility.test_pattern_definitions ?? []) {
      assert.equal(typeof patternDef.pattern_def_id, 'string');
      assert.ok(patternDef.pattern_def_id.length > 0);
      assert.equal(patternDef.pattern_def_id.includes('_sample'), false, patternDef.pattern_def_id);
      assert.ok(guaranteeIds.has(patternDef.guarantee_id), `${responsibility.responsibility_cd}/${patternDef.pattern_def_id}`);
      ids.push(patternDef.pattern_def_id);
    }
    assert.equal(ids.length, new Set(ids).size, `${responsibility.responsibility_cd}: Pattern Def ID duplicate`);
  }
});

test('SEARCH_FILTER formal Pattern Def IDs no longer say sample', () => {
  const document = JSON.parse(read('data/json/03_tests/responsibilities/responsibility_data_v0_2.json'));
  const responsibility = document.responsibilities.find(item => item.responsibility_cd === 'search_filter');
  assert.deepEqual(
    responsibility.test_pattern_definitions.map(item => item.pattern_def_id),
    ['search_filter_string', 'search_filter_number']
  );
});

test('Pattern Def Trace runtime maps every current responsibility family and puts Pattern Def ID last', () => {
  const sandbox = {
    console: { info(){}, warn(){}, log(){}, error(){} },
    setInterval(fn){ sandbox.__retry = fn; return 1; },
    clearInterval(){},
    document: {
      readyState: 'complete',
      addEventListener(){}
    }
  };
  sandbox.globalThis = sandbox;

  vm.createContext(sandbox);
  vm.runInContext(`
    class ResponsibilityTestPreviewService {
      derive(args) {
        const cd = args.responsibility.responsibility_cd;
        const samples = {
          search_filter: [
            { pattern_id:'search_filter_string_contains', generated_cases:[{}] },
            { pattern_id:'search_filter_number_gte', generated_cases:[{}] }
          ],
          grid_column_build: [
            { pattern_id:'grid_column_build_visible_fields', generated_cases:[{}] }
          ],
          csv_export: [
            { pattern_id:'csv_export_all_rows', generated_cases:[{}] }
          ],
          grid_aggregate: [
            { pattern_id:'grid_aggregate_sum_filtered', generated_cases:[{}] }
          ],
          data_update_persist: [
            { pattern_id:'data_update_persist_single_grid_first', generated_cases:[{}] }
          ]
        };
        return { test_patterns: samples[cd] || [] };
      }
    }
    class ResponsibilityTestPreviewComponent {
      constructor(){ this._result={test_patterns:[]}; }
      buildRows(){ return this._result.test_patterns.map((p,i)=>({__pattern_index:i,pattern:p.pattern_id})); }
      buildColumns(){ return [{field:'pattern',caption:'TestPattern'},{field:'role',caption:'Role'}]; }
    }
  `, sandbox);

  vm.runInContext(read('wwwroot/js/services/responsibility/responsibility_pattern_def_trace.js'), sandbox);

  const document = JSON.parse(read('data/json/03_tests/responsibilities/responsibility_data_v0_2.json'));
  for (const responsibility of document.responsibilities) {
    const result = vm.runInContext(`
      (() => {
        const r = ${JSON.stringify(responsibility)};
        const service = new ResponsibilityTestPreviewService();
        return service.derive({ responsibility:r });
      })()
    `, sandbox);

    for (const pattern of result.test_patterns) {
      assert.equal(typeof pattern.pattern_def_id, 'string');
      assert.ok(pattern.pattern_def_id, `${responsibility.responsibility_cd}/${pattern.pattern_id}`);
      assert.equal(pattern.generated_cases[0].pattern_def_id, pattern.pattern_def_id);
    }
  }

  const columns = vm.runInContext(`
    (() => {
      const c = new ResponsibilityTestPreviewComponent();
      return c.buildColumns([]);
    })()
  `, sandbox);
  assert.equal(columns.at(-1).field, 'pattern_def_id');
  assert.equal(columns.at(-1).caption, 'Pattern Def ID');
});

test('Core loader activates Pattern Def Trace as a core service, not Overlay', () => {
  const state = read('wwwroot/js/core/state.js');
  assert.match(state, /ensureResponsibilityPatternDefTraceRuntime/);
  assert.match(state, /js\/services\/responsibility\/responsibility_pattern_def_trace\.js/);
  const traceSection = state.slice(state.indexOf('v0.18.130-responsibility-pattern-def-trace'));
  assert.doesNotMatch(traceSection, /studio_overlays\/default\/plugins/);
});
