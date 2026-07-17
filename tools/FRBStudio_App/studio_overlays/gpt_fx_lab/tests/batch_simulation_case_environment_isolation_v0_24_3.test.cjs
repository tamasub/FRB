const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const assert = require('node:assert/strict');

const root = path.resolve(process.argv[2] || process.cwd());
function artifactPath(...parts) {
  const p = path.join(root, ...parts);
  if (fs.existsSync(p)) return p;
  const w = path.join(root, parts.join('\\'));
  if (fs.existsSync(w)) return w;
  throw new Error(`missing ${parts.join('/')}`);
}

const pluginPath = artifactPath('studio_overlays','gpt_fx_lab','plugins','fx_chart_viewer','plugin.js');
const manifestPath = artifactPath('studio_overlays','gpt_fx_lab','plugins','fx_chart_viewer','plugin.json');
const profilePath = artifactPath('studio_overlays','gpt_fx_lab','simulation','fx_simulation_run_profile_normal_plus_expansion_lite_v0_1.json');
const d1Path = artifactPath('studio_overlays','gpt_fx_lab','data','fx_usdjpy_d1_t3_data_v0_1.json');
const source = fs.readFileSync(pluginPath, 'utf8');
const manifest = JSON.parse(fs.readFileSync(manifestPath, 'utf8'));
const profile = JSON.parse(fs.readFileSync(profilePath, 'utf8'));
const d1 = JSON.parse(fs.readFileSync(d1Path, 'utf8'));
const idx = source.lastIndexOf('})();');
const hook = `pluginManifest=window.__manifest; window.__t={batchSimulationAnalysisWindow,loadBatchSimulationUpperMapData,normalizeAllRows};`;
const ctx = {
  window: { __manifest: manifest }, console, setTimeout, clearTimeout, URL, structuredClone, Intl, Date, Math, JSON, Map, Set, Promise,
  fetch: async () => ({ ok: true, status: 200, statusText: 'OK', json: async () => d1 })
};
vm.runInNewContext(source.slice(0, idx) + hook + source.slice(idx), ctx, { filename: pluginPath });
const api = ctx.window.__t;

assert.equal(manifest.version, '0.9.1.13');
const fakeRows = Array.from({ length: 50314 }, (_, index) => ({ datetime: `row-${index}` }));
const full = api.batchSimulationAnalysisWindow({ target_start_index: 0, target_end_index: 50313, period: { from: '2025-10-28 06:10', to: '2026-07-03 23:50' } }, fakeRows);
assert.deepEqual(JSON.parse(JSON.stringify(full)), {
  source: 'BATCH_TARGET_PERIOD', window_start: 0, window_size: 50314, window_end_exclusive: 50314,
  period_from: '2025-10-28 06:10', period_to: '2026-07-03 23:50'
});
const custom = api.batchSimulationAnalysisWindow({ target_start_index: 10000, target_end_index: 10999, period: { from: 'A', to: 'B' } }, fakeRows);
assert.equal(custom.window_start, 10000);
assert.equal(custom.window_size, 1000);

(async () => {
  const loaded = await api.loadBatchSimulationUpperMapData(profile, { upperMapSource: null, upperMapAllRows: [] });
  assert.equal(loaded.from, 'api');
  assert.ok(loaded.rows.length > 1000, 'Profile指定UpperMap DAYをCase単位で読込できていません');
  assert.match(source, /windowStart: analysisWindow\.window_start/);
  assert.match(source, /upperMapSource: upperLoaded\.source/);
  assert.match(source, /syncCenterTimeMs: null/);
  assert.match(source, /failed_step_count: stepErrors\.length/);
  console.log('PASS batch_simulation_case_environment_isolation_v0_24_3');
  console.log(`full_window=${full.window_size} custom_window=${custom.window_size} upper_rows=${loaded.rows.length}`);
})().catch(error => {
  console.error(error);
  process.exitCode = 1;
});
