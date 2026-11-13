const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const assert = require('node:assert/strict');

const root = path.resolve(process.argv[2] || process.cwd());
function ap(...parts) {
  const p = path.join(root, ...parts);
  if (fs.existsSync(p)) return p;
  const w = path.join(root, parts.join('\\'));
  if (fs.existsSync(w)) return w;
  throw new Error(`missing ${parts.join('/')}`);
}
const pluginPath = ap('studio_overlays','gpt_fx_lab','plugins','fx_chart_viewer','plugin.js');
const profilePath = ap('studio_overlays','gpt_fx_lab','simulation','fx_simulation_run_profile_expansion_v0_1.json');
const allProfilePath = ap('studio_overlays','gpt_fx_lab','simulation','fx_simulation_run_profile_all_rule_lanes_v0_1.json');
const source = fs.readFileSync(pluginPath,'utf8');
const profile = JSON.parse(fs.readFileSync(profilePath,'utf8'));
const allProfile = JSON.parse(fs.readFileSync(allProfilePath,'utf8'));
const hook = `window.__expansionV028={normalizeSimulationRunProfile,validateSimulationRunDraft,m5ExecutionExpansionFacts,m5ExecutionR2Touch,expansionRuleLaneEntryDecision,expansionRuleLaneCloseDecision};`;
const idx = source.lastIndexOf('})();');
const context = {window:{},console,setTimeout,clearTimeout,URL,structuredClone,Intl,Date,Math,JSON,Map,Set,Promise};
vm.runInNewContext(source.slice(0,idx)+hook+source.slice(idx),context,{filename:pluginPath});
const api=context.window.__expansionV028;

assert.equal(api.validateSimulationRunDraft(api.normalizeSimulationRunProfile(profile)).valid,true);
assert.equal(api.validateSimulationRunDraft(api.normalizeSimulationRunProfile(allProfile)).valid,true);
assert.equal(profile.m5_execution_policy.expansion_policy.rule_version,'v0.28');
assert.equal(profile.m5_execution_policy.expansion_policy.entry_execution,'NEXT_M5_OPEN_AFTER_ALL_FACTS_CONFIRMED');
assert.deepEqual(Array.from(allProfile.m5_execution_policy.rule_lane_policy.enabled_entry_rule_lanes),['NORMAL','EXPANSION','EXPANSION_LITE']);

const t0=Date.parse('2026-01-05T10:00:00+09:00');
function snapshot({h1Low=100.10,h1High=100.50,h1Close=100.45,h1T3=100.30,h1Key='h1_1',h4Close=101,h4T3=100.50,direction='UP',confirmationId='h1_up_001'}={}) {
  return {timeframes:{
    H1:{latest_confirmed_bar:{open:100.2,low:h1Low,high:h1High,close:h1Close,t3_20_0_2:h1T3,confirmed_bar_key:h1Key,index:10},trend_detail:{normal_dow_confirmation:{confirmation_id:confirmationId,direction,confirmed_at:'2026-01-05 10:00',confirmed_at_ms:t0,anchor_point_id:'h1_anchor_001',anchor_type:direction==='UP'?'swing_low':'swing_high',anchor_price:100,anchor_time:'2026-01-05 08:00',breakout_threshold_price:100.4}}},
    H4:{latest_confirmed_bar:{close:h4Close,t3_20_0_2:h4T3}},
    M5:{}
  }};
}
const policy=api.normalizeSimulationRunProfile(profile).m5_execution_policy;
const portfolio={trades:[],positions:[],expansion_entry_opportunities:[],used_expansion_confirmation_ids:[]};

// 先にT3接触だけ成立。R2は未到達。
let tf=snapshot({h1High:100.40,h1Low:100.20,h1T3:100.30,h1Key:'h1_1'});
let facts=api.m5ExecutionExpansionFacts(tf,policy,100.40);
let d1=api.expansionRuleLaneEntryDecision({portfolio,referenceMs:t0,referenceTime:'2026-01-05 10:00',price:100.40,currentBar:{open:100.35,high:100.40,low:100.30,close:100.40},r2Touch:{touched:false},policy,timeframeSnapshot:tf,expansionFacts:facts,upperDecision:{entry_policy:{expansion_entry:{status:'ALLOW'}}}});
assert.equal(d1.action,'WAIT');
assert.equal(d1.entry_opportunity.t3_touched,true);
assert.equal(d1.entry_opportunity.r2_touched,false);

// 次のH1足でR2へ到達。T3接触履歴は保持され、次M5 Open待ちになる。
tf=snapshot({h1High:100.60,h1Low:100.40,h1T3:100.30,h1Key:'h1_2'});
facts=api.m5ExecutionExpansionFacts(tf,policy,100.58);
const r2=api.m5ExecutionR2Touch({open:100.50,high:100.60,low:100.48,close:100.58},100,'LONG',policy);
let d2=api.expansionRuleLaneEntryDecision({portfolio,referenceMs:t0+3600000,referenceTime:'2026-01-05 11:00',price:100.58,currentBar:{open:100.50,high:100.60,low:100.48,close:100.58},r2Touch:r2,policy,timeframeSnapshot:tf,expansionFacts:facts,upperDecision:{entry_policy:{expansion_entry:{status:'ALLOW'}}}});
assert.equal(d2.action,'WAIT');
assert.equal(d2.entry_opportunity.status,'READY_NEXT_M5_OPEN');
assert.equal(d2.entry_opportunity.r2_touched,true);
assert.equal(d2.entry_opportunity.t3_touched,true);

// 同じ足へ遡らず、次のM5 OpenでEntry。
facts=api.m5ExecutionExpansionFacts(tf,policy,100.61);
let d3=api.expansionRuleLaneEntryDecision({portfolio,referenceMs:t0+3900000,referenceTime:'2026-01-05 11:05',price:100.61,currentBar:{open:100.59,high:100.63,low:100.57,close:100.61},r2Touch:{touched:true},policy,timeframeSnapshot:tf,expansionFacts:facts,upperDecision:{entry_policy:{expansion_entry:{status:'ALLOW'}}}});
assert.equal(d3.action,'ENTRY');
assert.equal(d3.execution_candidate.price,100.59);
assert.equal(d3.entry_opportunity.entry_execution_mode,'NEXT_M5_OPEN_AFTER_H1_DOW_R2_T3_CONFIRMED');
assert.ok(d3.reason_codes.includes('EXPANSION_NEXT_M5_OPEN_ENTRY'));

// H1 CloseでAnchorを割れば候補破棄。
const p2={trades:[],positions:[],expansion_entry_opportunities:[],used_expansion_confirmation_ids:[]};
const broken=snapshot({h1Low:99.7,h1High:100.2,h1Close:99.9,h1T3:100.1,h1Key:'h1_broken'});
const brokenDecision=api.expansionRuleLaneEntryDecision({portfolio:p2,referenceMs:t0,referenceTime:'broken',price:99.9,currentBar:{open:100.1,high:100.2,low:99.8,close:99.9},r2Touch:{touched:false},policy,timeframeSnapshot:broken,expansionFacts:api.m5ExecutionExpansionFacts(broken,policy,99.9),upperDecision:{entry_policy:{expansion_entry:{status:'ALLOW'}}}});
assert.equal(brokenDecision.entry_opportunity.status,'EXPIRED_H1_ANCHOR_BREAK');
assert.ok(brokenDecision.reason_codes.includes('EXPANSION_H1_ANCHOR_CLOSE_BREAK'));

const activeTrade={trade_id:'exp_001',status:'OPEN',rule_lane:'EXPANSION',side:'LONG',entry_price:100.59,entry_anchor_price:100,target_price:102.262,h1_dow_confirmation_id:'h1_up_001'};
const activePosition={position_id:'exp_pos_001',trade_id:'exp_001',status:'OPEN',rule_lane:'EXPANSION',side:'LONG',units_open:10,entry_price:100.59,entry_anchor_price:100,target_plan:{next_target_price:102.262}};
// H1 T3逆抜けClose。
const t3ExitTf=snapshot({h1Low:100.10,h1High:100.45,h1Close:100.20,h1T3:100.30,h1Key:'h1_3'});
const close1=api.expansionRuleLaneCloseDecision({activeTrade,activePosition,currentBar:{open:100.25,high:100.30,low:100.18,close:100.20},timeframeSnapshot:t3ExitTf,policy});
assert.equal(close1.action,'FULL_CLOSE');
assert.equal(close1.exit_type,'H1_T3_EXIT');
assert.equal(close1.execution_price,100.20);

// R5到達はH1 T3 Exitより先に採用。
const targetTf=snapshot({h1Low:100.2,h1High:102.4,h1Close:100.20,h1T3:100.30,h1Key:'h1_4'});
const close2=api.expansionRuleLaneCloseDecision({activeTrade,activePosition,currentBar:{open:102.20,high:102.30,low:102.10,close:102.20},timeframeSnapshot:targetTf,policy});
assert.equal(close2.action,'FULL_CLOSE');
assert.equal(close2.exit_type,'R5_TARGET_EXIT');
assert.equal(close2.execution_price,102.262);

console.log('PASS expansion_h1_dow_r2_t3_v0_28');
