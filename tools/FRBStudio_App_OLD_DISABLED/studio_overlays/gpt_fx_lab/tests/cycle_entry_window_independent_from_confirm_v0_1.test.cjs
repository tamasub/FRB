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

const pluginPath = artifactPath('studio_overlays','gpt_fx_lab','plugins','fx_chart_viewer','plugin.js');
const profilePath = artifactPath('studio_overlays','gpt_fx_lab','simulation','fx_simulation_run_profile_normal_plus_expansion_lite_v0_1.json');
const source = fs.readFileSync(pluginPath,'utf8');
const profile = JSON.parse(fs.readFileSync(profilePath,'utf8'));
const hook = `window.__cycleEntryWindowTest={normalizeSimulationRunProfile,validateSimulationRunDraft,m5ExecutionExpansionLiteFacts};`;
const closeIndex = source.lastIndexOf('})();');
const instrumented = source.slice(0, closeIndex) + hook + source.slice(closeIndex);
const context = {window:{},console,setTimeout,clearTimeout,URL,structuredClone,Intl,Date,Math,JSON,Map,Set,Promise};
vm.runInNewContext(instrumented, context, {filename:pluginPath});
const api = context.window.__cycleEntryWindowTest;
const normalized = api.normalizeSimulationRunProfile(profile);
const validation = api.validateSimulationRunDraft(normalized);
assert.equal(validation.valid,true,validation.errors.join('\n'));

const h1Profile = normalized.timeframe_profiles.find(x => x.timeframe === 'H1');
const h4Profile = normalized.timeframe_profiles.find(x => x.timeframe === 'H4');
assert.equal(h1Profile.cycle.entry_allowed_max_bars,14);
assert.equal(h4Profile.cycle.entry_allowed_max_bars,14);
assert.equal(normalized.timeframe_profiles.find(x => x.timeframe === 'WEEK').cycle.entry_allowed_max_bars,20);
assert.equal(normalized.timeframe_profiles.find(x => x.timeframe === 'DAY').cycle.entry_allowed_max_bars,45);
assert.equal(normalized.timeframe_profiles.find(x => x.timeframe === 'M5').cycle.entry_allowed_max_bars,20);

const dowUp = {confirmation_id:'confirm_up',direction:'UP',anchor_price:150};
function snapshot(elapsed, confirmBars) {
  return {
    timeframes: {
      H4: {latest_confirmed_bar:{close:151,t3_20_0_2:150.5}},
      H1: {
        latest_confirmed_bar:{index:100,close:150.9,t3_20_0_2:150.6},
        swing_state:{latest_pending_low:{point_id:'h1_low',source_index:100-elapsed,confirm_bars:confirmBars}},
        cycle_state:{origin:{point_id:'old',source_index:70,confirm_bars:confirmBars},elapsed_bars:30}
      },
      M5: {trend_state:'UP'}
    }
  };
}

const at13Confirm7 = api.m5ExecutionExpansionLiteFacts(snapshot(13,7), normalized, dowUp);
assert.equal(at13Confirm7.h1_cycle_entry_allowed,true);
assert.equal(at13Confirm7.h1_cycle_entry_allowed_max_bars,14);
assert.equal(at13Confirm7.h1_cycle_elapsed_bars,13);

const at13Confirm3 = api.m5ExecutionExpansionLiteFacts(snapshot(13,3), normalized, dowUp);
assert.equal(at13Confirm3.h1_cycle_entry_allowed,true,'Confirm barsを3へ変えても14本Entry Windowは変わらない');
assert.equal(at13Confirm3.h1_cycle_entry_allowed_max_bars,14);

const at15Confirm20 = api.m5ExecutionExpansionLiteFacts(snapshot(15,20), normalized, dowUp);
assert.equal(at15Confirm20.h1_cycle_entry_allowed,false,'15本目はH1 Entry Window外');
assert.equal(at15Confirm20.h1_cycle_entry_allowed_max_bars,14);

console.log('PASS cycle_entry_window_independent_from_confirm_v0_1');
console.log('H1/H4=14, WEEK=20, DAY=45, M5=20');
