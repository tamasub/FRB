const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const plugin = fs.readFileSync(path.join(__dirname, '..', 'plugins', 'fx_chart_viewer', 'plugin.js'), 'utf8');

test('T3 gate component diagnostics are present', () => {
  for (const token of ['H4_T3_DIRECTION_NOT_ALIGNED','H4_CLOSE_T3_POSITION_NOT_ALIGNED','H1_T3_DIRECTION_NOT_ALIGNED','H1_CLOSE_T3_POSITION_NOT_ALIGNED','t3_component_failure_counts']) assert.ok(plugin.includes(token), token);
});

test('R4 guard shadow lifecycle is isolated and exported', () => {
  for (const token of ['normal_r4_shadow_trades','STOP_FIRST_CONSERVATIVE','r4_guard_shadow','r4_shadow_outcome']) assert.ok(plugin.includes(token), token);
  assert.ok(plugin.includes("guard_reason_code: 'NORMAL_H4_SAME_DIRECTION_R4_ENTRY_BLOCKED'"));
});
