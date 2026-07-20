const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');

const root = path.resolve(process.argv[2] || process.cwd());
function artifactPath(...parts) {
  const normalized = path.join(root, ...parts);
  if (fs.existsSync(normalized)) return normalized;
  const windowsEntry = path.join(root, parts.join('\\'));
  if (fs.existsSync(windowsEntry)) return windowsEntry;
  throw new Error(`テスト対象ファイルが見つかりません: ${parts.join('/')}`);
}

const pluginPath = artifactPath('studio_overlays', 'gpt_fx_lab', 'plugins', 'fx_chart_viewer', 'plugin.js');
const manifestPath = artifactPath('studio_overlays', 'gpt_fx_lab', 'plugins', 'fx_chart_viewer', 'plugin.json');
const source = fs.readFileSync(pluginPath, 'utf8');
const manifest = JSON.parse(fs.readFileSync(manifestPath, 'utf8'));

assert.equal(manifest.version, '0.9.1.23');
assert.equal(manifest.signal_policy.simulation_execution_marker_leader_line, true);
assert.equal(manifest.signal_policy.simulation_execution_marker_endpoint_dot, true);
assert.equal(manifest.signal_policy.simulation_execution_marker_endpoint_dot_radius_px, 3.1);
assert.equal(manifest.signal_policy.simulation_execution_marker_endpoint_dot_radius_px_focused, 4.2);
assert.equal(manifest.signal_policy.simulation_execution_marker_diagonal_connector, true);
assert.equal(manifest.signal_policy.simulation_execution_marker_chart_overlap_avoidance, true);
assert.equal(manifest.signal_policy.simulation_execution_marker_chart_clearance_px, 10);
assert.equal(manifest.signal_policy.simulation_execution_marker_label_horizontal_shift_px_base, 32);
assert.equal(manifest.signal_policy.simulation_execution_marker_label_horizontal_shift_px_base_focused, 44);
assert.equal(manifest.signal_policy.simulation_execution_marker_label_horizontal_shift_px_per_lane, 12);
assert.equal(manifest.signal_policy.simulation_execution_marker_label_horizontal_shift_px_per_lane_focused, 16);
assert.equal(manifest.signal_policy.simulation_execution_marker_leader_line_policy, 'local_chart_envelope_avoidance_with_diagonal_connector');
assert.match(source, /function simulationExecutionMarkerLocalEnvelope\(args\)/);
assert.match(source, /\['high', 'low', 'close', 'ma5', 'ma20', 't3_20_0_2'\]\.forEach/);
assert.match(source, /includeValue\(band\.upper\);/);
assert.match(source, /includeValue\(band\.lower\);/);
assert.match(source, /const chartClearance = batchFocus \|\| focused \? 12 : 10;/);
assert.match(source, /rect\.bottom <= envelope\.top - chartClearance \+ 0\.5/);
assert.match(source, /rect\.top >= envelope\.bottom \+ chartClearance - 0\.5/);
assert.match(source, /ctx\.lineTo\(xx, yy\);/);
assert.match(source, /const endpointRadius = batchFocus \|\| focused \? 4\.2 : 3\.1;/);
assert.match(source, /chart_envelope_top: selected\.envelope\.top/);
assert.match(source, /bollingerBands, showBollinger/);
assert.match(source, /state\.simulationExecutionMarkerLayout\[`\$\{panelKind\}:top`\] = \{ boxes: \[\] \};/);
assert.match(source, /state\.simulationExecutionMarkerLayout\[`\$\{panelKind\}:bottom`\] = \{ boxes: \[\] \};/);

console.log('PASS simulation_execution_marker_pointer_v0_1');
