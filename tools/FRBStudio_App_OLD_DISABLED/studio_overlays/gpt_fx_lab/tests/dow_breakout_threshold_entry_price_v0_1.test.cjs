const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const root = path.resolve(process.argv[2] || process.cwd());
function artifactPath(...parts) {
  const normalized = path.join(root, ...parts);
  if (fs.existsSync(normalized)) return normalized;
  const windowsEntry = path.join(root, parts.join('\\'));
  if (fs.existsSync(windowsEntry)) return windowsEntry;
  throw new Error(`missing: ${parts.join('/')}`);
}
const pluginPath = artifactPath('studio_overlays','gpt_fx_lab','plugins','fx_chart_viewer','plugin.js');
const profilePath = artifactPath('studio_overlays','gpt_fx_lab','simulation','fx_simulation_run_profile_v0_1.json');
const source = fs.readFileSync(pluginPath,'utf8');
const profile = JSON.parse(fs.readFileSync(profilePath,'utf8'));
assert.match(source, /breakout_threshold_price: numberOrNull\(source\.breakout_threshold_price\)/,
  'Dow ConfirmationからM5 Executionへbreakout_threshold_priceが伝搬されていません。');
assert.match(source, /ENTRY_AT_DOW_BREAKOUT_THRESHOLD_AND_R2/,
  'Dow突破閾値Entryのreason codeがありません。');
const p = profile.m5_execution_policy.normal_entry_policy;
assert.equal(p.rule_version,'v0.24');
assert.equal(p.r2_ready_at_confirmation,'IMMEDIATE_ENTRY_AT_FIRST_PRICE_SATISFYING_DOW_BREAKOUT_AND_R2');
assert.equal(p.entry_execution_price_policy,'DOW_BREAKOUT_THRESHOLD_OR_R2_WHICHEVER_IS_FARTHER_FROM_ANCHOR_ELSE_FIRST_AVAILABLE_GAP_PRICE');
console.log('PASS dow_breakout_threshold_entry_price_v0_1');
