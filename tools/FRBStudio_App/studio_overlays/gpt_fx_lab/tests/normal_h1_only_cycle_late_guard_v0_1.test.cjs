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
assert.equal(profile.m5_execution_policy.normal_entry_policy.rule_version,'v0.17.1');
assert.deepEqual(profile.m5_execution_policy.normal_entry_policy.cycle_late_guard_timeframes,['H1']);

const hook = `window.__h1OnlyGuardTest = { m5ExecutionNormalEntryV08Facts, normalRuleLaneEntryDecision, validateSimulationRunDraft };`;
const closeIndex = source.lastIndexOf('})();');
assert.ok(closeIndex > 0);
const context = { window:{}, console, setTimeout, clearTimeout, URL, structuredClone, Intl, Date, Math, JSON, Map, Set, Promise, requestAnimationFrame: cb => setTimeout(cb,0) };
vm.runInNewContext(source.slice(0,closeIndex)+hook+source.slice(closeIndex),context,{filename:pluginPath});
const api=context.window.__h1OnlyGuardTest;
const snapshot={timeframes:{
  H4:{latest_confirmed_bar:{close:154,t3_20_0_2:153,t3_direction:'up',close_t3_position:'above'},cycle_state:{phase:'LATE'}},
  H1:{latest_confirmed_bar:{close:154,t3_20_0_2:153,t3_direction:'up',close_t3_position:'above'},cycle_state:{phase:'MIDDLE'}},
  M5:{trend_state:'UP'}
}};
const facts=api.m5ExecutionNormalEntryV08Facts(snapshot);
assert.equal(facts.h4_cycle_late,true,'H4 Lateの観測事実は保持する必要があります。');
assert.equal(facts.h1_cycle_late,false);
assert.equal(facts.cycle_guard_passed,true,'H4 LateだけでNORMAL Entryを禁止してはいけません。');
assert.equal(facts.entry_direction_ready,true);

const h1LateFacts={...facts,h1_cycle_late:true,cycle_guard_passed:false};
function decision(normalFacts){
  const ms=Date.parse('2025-10-30T09:44:00+09:00');
  return api.normalRuleLaneEntryDecision({
    portfolio:{trades:[],positions:[],normal_entry_opportunities:[],used_dow_confirmation_ids:[],normal_anchor_lifecycle:{status:'NONE',last_retired_at_ms:null}},
    referenceMs:ms,referenceTime:'2025-10-30 09:44',price:153.498,direction:'LONG',confirmationSide:'LONG',normalFacts,
    dowConfirmation:{confirmation_id:'h1_guard_dow_001',direction:'UP',confirmed_at:'2025-10-30 09:44',confirmed_at_ms:ms,breakout_threshold_price:153.135},
    entryResolution:{status:'RESOLVED_REFERENCE',anchor_id:'h1_guard_anchor',anchor:{anchor_id:'h1_guard_anchor',price:152.164,direction:'UP',dow_confirmation_id:'h1_guard_dow_001'}},
    entryAnchor:{anchor_id:'h1_guard_anchor',price:152.164,direction:'UP',dow_confirmation_id:'h1_guard_dow_001'},anchorPrice:152.164,
    r2Touch:{touched:true,entry_price:152.698,passed_before_bar:true,open:153.300},policy:profile.m5_execution_policy,minEntryLabel:'R2',hsiNotReachedReasonCode:'HSI_R2_NOT_REACHED'
  });
}
const h4LateDecision=decision(facts);
assert.equal(h4LateDecision.action,'ENTRY','H4 LateだけならNORMAL Entryを許可する必要があります。');
assert.ok(!h4LateDecision.reason_codes.includes('H4_CYCLE_LATE_ENTRY_BLOCKED'));
const h1LateDecision=decision(h1LateFacts);
assert.equal(h1LateDecision.action,'WAIT');
assert.ok(h1LateDecision.reason_codes.includes('H1_CYCLE_LATE_ENTRY_BLOCKED'));
assert.equal(api.validateSimulationRunDraft(profile).valid,true);
console.log('PASS normal_h1_only_cycle_late_guard_v0_1');
