const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const assert = require('node:assert/strict');

const root = path.resolve(process.argv[2] || process.cwd());
function artifactPath(...parts) {
  const normalized = path.join(root, ...parts);
  if (fs.existsSync(normalized)) return normalized;
  const windowsEntry = path.join(root, parts.join('\\'));
  if (fs.existsSync(windowsEntry)) return windowsEntry;
  throw new Error(`テスト対象ファイルが見つかりません: ${parts.join('/')}`);
}

const pluginPath = artifactPath('studio_overlays', 'gpt_fx_lab', 'plugins', 'fx_chart_viewer', 'plugin.js');
const profilePath = artifactPath('studio_overlays', 'gpt_fx_lab', 'simulation', 'fx_simulation_run_profile_v0_1.json');
const manifestPath = artifactPath('studio_overlays', 'gpt_fx_lab', 'plugins', 'fx_chart_viewer', 'plugin.json');

const canonicalException = 'normal_entry_v0_17_trade_scoped_hsi_anchor_explicit_exception';
const expectedEngineId = 'm5_rule_lane_execution_orchestrator_v0_2';
const pluginSource = fs.readFileSync(pluginPath, 'utf8');
const profile = JSON.parse(fs.readFileSync(profilePath, 'utf8'));
const manifest = JSON.parse(fs.readFileSync(manifestPath, 'utf8'));

assert.equal(profile.m5_execution_policy.upper_decision_reimplementation, canonicalException,
  'Run Profileのupper_decision_reimplementationがv0.15正式値と一致していません。');
assert.equal(profile.m5_execution_policy.engine_id, expectedEngineId,
  'Run ProfileのM5 execution engineがRule Lane Orchestratorではありません。');
const versionParts = String(manifest.version || '').split('.').map(Number);
assert.equal(versionParts.length, 4, `plugin version形式が不正です: ${manifest.version}`);
assert.ok(versionParts[0] === 0 && versionParts[1] === 9 && versionParts[2] === 1 && versionParts[3] >= 13,
  `plugin versionは0.9.1.13以降である必要があります: ${manifest.version}`);
assert.equal(manifest.signal_policy.m5_execution_engine_id, expectedEngineId,
  'plugin.jsonのM5 execution engineがRun Profileと一致していません。');
assert.match(pluginSource, /const NORMAL_ENTRY_V0_17_UPPER_DECISION_EXCEPTION = 'normal_entry_v0_17_trade_scoped_hsi_anchor_explicit_exception';/,
  'Plugin側にv0.17.1正式値の単一定数がありません。');
assert.doesNotMatch(pluginSource, /normal_entry_v0_15_dow_breakout_next_boundary_explicit_exception/,
  '旧短縮名がPlugin内に残っています。');

const lanePolicy = profile.m5_execution_policy.rule_lane_policy;
assert.equal(lanePolicy.active_entry_rule_lane, 'NORMAL');
assert.equal(lanePolicy.shared_fact_source, 'TIMEFRAME_STATE_SNAPSHOT');
assert.equal(lanePolicy.close_lane_source, 'OPEN_TRADE_RULE_LANE');
assert.equal(lanePolicy.lanes.NORMAL.enabled, true);
assert.equal(lanePolicy.lanes.NORMAL.entry_evaluator_id, 'normal_m5_entry_evaluator_v0_1');
assert.equal(lanePolicy.lanes.NORMAL.close_evaluator_id, 'normal_m5_close_evaluator_v0_1');
assert.equal(lanePolicy.lanes.EXPANSION.enabled, false);
assert.equal(lanePolicy.lanes.EXPANSION_LITE.enabled, false);

const hook = `\n  window.__fxProfileContractTest = {\n    normalizeSimulationRunProfile,\n    validateSimulationRunDraft,\n    buildEmptySimulationRunProfile\n  };\n`;
const closeIndex = pluginSource.lastIndexOf('})();');
assert.ok(closeIndex > 0, 'Plugin IIFE終端を検出できません。');
const instrumented = pluginSource.slice(0, closeIndex) + hook + pluginSource.slice(closeIndex);

const context = {
  window: {},
  console,
  setTimeout,
  clearTimeout,
  URL,
  structuredClone,
  Intl,
  Date,
  Math,
  JSON,
  Map,
  Set,
  Promise
};
vm.runInNewContext(instrumented, context, { filename: pluginPath });
const api = context.window.__fxProfileContractTest;
assert.ok(api, 'テスト用Validator公開に失敗しました。');

const normalized = api.normalizeSimulationRunProfile(profile);
const result = api.validateSimulationRunDraft(normalized);
assert.equal(result.valid, true, `Run Profile検証失敗:\n${result.errors.join('\n')}`);
assert.deepEqual(Array.from(result.errors), [], 'Run Profile検証にエラーが残っています。');

const emptyProfile = api.buildEmptySimulationRunProfile();
assert.equal(emptyProfile.m5_execution_policy.upper_decision_reimplementation, canonicalException,
  'Plugin初期Profileのupper_decision_reimplementationが正式値と一致していません。');
assert.equal(emptyProfile.m5_execution_policy.engine_id, expectedEngineId,
  'Plugin初期ProfileのM5 execution engineがRule Lane Orchestratorではありません。');
assert.equal(emptyProfile.m5_execution_policy.rule_lane_policy.active_entry_rule_lane, 'NORMAL');

console.log('PASS simulation_profile_contract_v0_17');
console.log(`profile=${profile.profile_id}`);
console.log(`rule=${profile.rule_version}`);
console.log(`engine=${profile.m5_execution_policy.engine_id}`);
console.log(`entry_lane=${lanePolicy.active_entry_rule_lane}`);
console.log(`validation_errors=${result.errors.length}`);
