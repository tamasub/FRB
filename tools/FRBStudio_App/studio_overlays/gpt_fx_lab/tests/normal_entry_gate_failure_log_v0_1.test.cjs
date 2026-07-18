const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const assert = require('node:assert/strict');

const root = path.resolve(process.argv[2] || process.cwd());
const pluginPath = path.join(root, 'studio_overlays','gpt_fx_lab','plugins','fx_chart_viewer','plugin.js');
const manifestPath = path.join(root, 'studio_overlays','gpt_fx_lab','plugins','fx_chart_viewer','plugin.json');
const source = fs.readFileSync(pluginPath, 'utf8');
const manifest = JSON.parse(fs.readFileSync(manifestPath, 'utf8'));

assert.equal(manifest.version, '0.9.1.14');
assert.equal(manifest.display_policy.batch_simulation_runner.normal_entry_gate_failure_log_enabled, true);
assert.match(source, /normal_entry_gate_failure_v0_2/);
assert.match(source, /failedEntryGates/);
assert.match(source, /batchSimulationNormalGateFailureRowsFromSnapshot/);
assert.match(source, /batchSimulationNormalGateFailureCsv/);
assert.match(source, /download-gate-json/);
assert.match(source, /download-gate-csv/);
assert.match(source, /_normal_entry_gate_failures\.json/);

const hook = `window.__gateFailureTest={
  batchSimulationNormalGateFailureRowsFromSnapshot,
  batchSimulationNormalGateFailureSummary,
  batchSimulationNormalGateFailureCsv
};`;
const closeIndex = source.lastIndexOf('})();');
assert.ok(closeIndex > 0);
const instrumented = source.slice(0, closeIndex) + hook + source.slice(closeIndex);
const context = {
  window: {}, console, setTimeout, clearTimeout, URL, structuredClone, Intl, Date, Math, JSON, Map, Set, Promise,
  globalThis: {}
};
vm.runInNewContext(instrumented, context, { filename: pluginPath });
const api = context.window.__gateFailureTest;

const snapshot = {
  position_lifecycle: {
    portfolio: {
      normal_entry_opportunities: [
        {
          opportunity_id: 'opp1',
          status: 'MISSED',
          direction: 'LONG',
          confirmed_at: '2025-01-01 10:00',
          dow_confirmation_id: 'dow1',
          anchor_id: 'a1',
          anchor_time: '2025-01-01 09:00',
          anchor_price: 150,
          r2_price: 150.534,
          terminal_reason_code: 'R2_FIRST_TOUCH_ENTRY_GATES_NOT_READY',
          gate_failure: {
            trigger_type: 'FIRST_R2_TOUCH',
            evaluated_at: '2025-01-01 10:30',
            failure_category: 'ENTRY_GATES_NOT_READY',
            primary_failure_code: 'H1_T3_NOT_READY',
            failed_gates: ['H1_T3_NOT_READY','H4_H1_T3_NOT_ALIGNED'],
            gate_results: {
              h4_t3_ready: true,
              h1_t3_ready: false,
              h4_h1_t3_aligned: false,
              m5_dow_aligned: true,
              h1_cycle_not_late: true,
              entry_direction_ready: false,
              cycle_guard_passed: true,
              anchor_resolved: true,
              anchor_matches_confirmation: true,
              confirmation_aligned: true,
              anchor_lifecycle_ready: true
            },
            facts: { candidate_price: 150.534 }
          }
        }
      ]
    }
  }
};
const rows = api.batchSimulationNormalGateFailureRowsFromSnapshot(snapshot, { case_id:'case1', dataset_path:'data.json' });
assert.equal(rows.length, 1);
assert.equal(rows[0].primary_failure_code, 'H1_T3_NOT_READY');
assert.equal(rows[0].failed_gate_count, 2);
assert.equal(rows[0].h1_t3_ready, false);
const summary = api.batchSimulationNormalGateFailureSummary(rows);
assert.equal(summary.opportunity_count, 1);
assert.equal(summary.gate_violation_count, 2);
assert.equal(summary.gate_counts[0].count, 1);
const csv = api.batchSimulationNormalGateFailureCsv({ normal_entry_gate_failures: { rows, summary } });
assert.match(csv, /H1_T3_NOT_READY/);
assert.match(csv, /FIRST_R2_TOUCH/);
console.log('PASS normal_entry_gate_failure_log_v0_1');
