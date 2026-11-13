const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const root = path.resolve(process.argv[2] || process.cwd());
function artifactPath(...parts){const p=path.join(root,...parts);if(fs.existsSync(p))return p;const w=path.join(root,parts.join('\\'));if(fs.existsSync(w))return w;throw new Error(`missing: ${parts.join('/')}`);}
const pluginPath=artifactPath('studio_overlays','gpt_fx_lab','plugins','fx_chart_viewer','plugin.js');
const profilePath=artifactPath('studio_overlays','gpt_fx_lab','simulation','fx_simulation_run_profile_v0_1.json');
const source=fs.readFileSync(pluginPath,'utf8');
const profile=JSON.parse(fs.readFileSync(profilePath,'utf8'));
const hook=`window.__v024={latestM5BreakoutConfirmation,replayDowTrendForTimeframe,hsiAnchorFromDowAdoption,m5ExecutionExpireNormalOpportunitiesPriorToDowBreak,normalRuleLaneCloseDecision,m5ExecutionNormalDowStructureBreak,validateSimulationRunDraft};`;
const idx=source.lastIndexOf('})();');
const ctx={window:{},console,setTimeout,clearTimeout,URL,structuredClone,Intl,Date,Math,JSON,Map,Set,Promise};
vm.runInNewContext(source.slice(0,idx)+hook+source.slice(idx),ctx,{filename:pluginPath});
const api=ctx.window.__v024;
const policy=profile.m5_execution_policy;
assert.equal(policy.normal_entry_policy.rule_version,'v0.24');
assert.equal(policy.normal_entry_policy.same_direction_dow_reconfirmation_replaces_anchor,false);
assert.equal(policy.normal_entry_policy.post_entry_dow_structure_break_close_policy,'OBSERVE_ONLY_NO_CLOSE');
assert.equal(api.validateSimulationRunDraft(profile).valid,true,api.validateSimulationRunDraft(profile).errors.join('\n'));

const portfolio={normal_entry_opportunities:[{opportunity_id:'old',status:'WAITING_R2',direction:'LONG',dow_confirmation_id:'up_old',confirmed_at_ms:1000,anchor_id:'low_old',anchor_price:100,first_r2_touch_at:'old',first_r2_touch_at_ms:1500,r2_price:101}],normal_anchor_lifecycle:{status:'WAITING_R2',active_anchor_id:'low_old',active_anchor_price:100,active_confirmation_id:'up_old'}};
const m5State={trend_detail:{normal_dow_structure_break:{break_at:'2025-11-17 14:00',break_at_ms:2000,break_event_id:'break_1',break_state:'REVERSAL_WATCH',previous_direction:'UP',invalidated_confirmation_id:'up_old'}}};
const expired=api.m5ExecutionExpireNormalOpportunitiesPriorToDowBreak(portfolio,{m5_trend:'REVERSAL_WATCH'},null,policy,2000,'2025-11-17 14:00',m5State);
assert.equal(expired.length,1);
assert.equal(expired[0].status,'EXPIRED');
assert.equal(expired[0].first_r2_touch_at,null);
assert.equal(expired[0].r2_history_retired_before_entry,true);
assert.equal(portfolio.normal_anchor_lifecycle.status,'AWAITING_NEW_DOW_CONFIRMATION');
assert.equal(portfolio.normal_anchor_lifecycle.active_anchor_id,null);

const oldCandidate={direction:'UP',previousHigh:null,currentHigh:{pivot_ms:200},previousLow:{pivot_ms:100,pivot_price:100},currentLow:{pivot_ms:300,pivot_price:101},anchorPoint:{pivot_ms:100,pivot_price:100},thresholdPoint:{pivot_ms:200,pivot_price:102},readyAfterMs:300};
const rows=[{datetime:'1970-01-01 00:00',start_ms:400,end_ms:500,open:101,high:103,low:101,close:102.5}];
const resurrected=api.latestM5BreakoutConfirmation([oldCandidate.previousLow,oldCandidate.currentHigh,oldCandidate.currentLow].map((p,i)=>({...p,type:i===1?'swing_high':'swing_low',confirmed_ms:p.pivot_ms,point_id:`p${i}`})),rows,600,550);
assert.equal(resurrected,null,'Dow崩壊前のbreakout Confirmationを復活させてはいけません。');


const base=Date.parse('2025-01-01T00:00:00Z');
const minute=60*1000;
const at=(offsetMinutes)=>base+offsetMinutes*minute;
const dt=(offsetMinutes)=>new Date(at(offsetMinutes)).toISOString().slice(0,19).replace('T',' ');
const swingTimeframe={points:[
  {point_id:'l1',key:'l1',type:'swing_low',pivot_ms:at(0),pivot_time:dt(0),pivot_price:100,confirmed_ms:at(1),confirmed_time:dt(1)},
  {point_id:'h1',key:'h1',type:'swing_high',pivot_ms:at(10),pivot_time:dt(10),pivot_price:110,confirmed_ms:at(11),confirmed_time:dt(11)},
  {point_id:'l2',key:'l2',type:'swing_low',pivot_ms:at(20),pivot_time:dt(20),pivot_price:105,confirmed_ms:at(21),confirmed_time:dt(21)},
  {point_id:'h2',key:'h2',type:'swing_high',pivot_ms:at(30),pivot_time:dt(30),pivot_price:108,confirmed_ms:at(31),confirmed_time:dt(31)},
  {point_id:'l3',key:'l3',type:'swing_low',pivot_ms:at(40),pivot_time:dt(40),pivot_price:106,confirmed_ms:at(41),confirmed_time:dt(41)}
]};
const replayRows=[
  {datetime:dt(22),open:109,high:111,low:109,close:110.5},
  {datetime:dt(42),open:107,high:109,low:107,close:108.5}
];
const beforeBreak=api.replayDowTrendForTimeframe('M5',swingTimeframe,at(29),null,replayRows);
assert.equal(beforeBreak.normal_dow_confirmation.direction,'UP');
assert.equal(beforeBreak.normal_dow_confirmation.anchor_point_id,'l1');
const afterBreak=api.replayDowTrendForTimeframe('M5',swingTimeframe,at(35),null,replayRows);
assert.equal(afterBreak.normal_dow_confirmation,null,'Dow崩壊後に旧breakout Confirmationを復活させてはいけません。');
assert.equal(['REVERSAL_WATCH','NO_TREND','UNDETERMINED'].includes(afterBreak.normal_dow_structure_break.break_state),true);
assert.equal(api.hsiAnchorFromDowAdoption('M5',afterBreak),null,'新しいDow再確定前にNormal HSI Anchorを持ってはいけません。');
const afterReconfirm=api.replayDowTrendForTimeframe('M5',swingTimeframe,at(48),null,replayRows);
assert.equal(afterReconfirm.normal_dow_confirmation.direction,'UP');
assert.equal(afterReconfirm.normal_dow_confirmation.anchor_point_id,'l2','崩壊後の新しいDow構造ではprevious Lowを新起点にする必要があります。');
assert.equal(afterReconfirm.normal_dow_confirmation.anchor_price,105);
assert.notEqual(afterReconfirm.normal_dow_confirmation.anchor_point_id,afterReconfirm.normal_dow_confirmation.trigger_point_id,'Dow再確定点そのものをHSI起点にしてはいけません。');
const adopted=api.hsiAnchorFromDowAdoption('M5',afterReconfirm);
assert.equal(adopted.source_swing_point_id,'l2');
assert.equal(adopted.price,105);

const close=api.normalRuleLaneCloseDecision({activePosition:{side:'LONG',entry_price:100,entry_ms:1500,units_open:10,invalidation_rule:{invalidation_price:90},target_plan:{next_target_price:110,next_target_label:'R2.5'},close_miss_plan:{}},activeTrade:{entry_ms:1500,post_entry_dow_break_observation_ids:[]},currentBar:{open:100,high:105,low:95,close:101},m5State});
assert.equal(close.action,'WAIT');
assert.equal(close.reason_codes.includes('NORMAL_POST_ENTRY_DOW_BREAKDOWN_OBSERVED_NO_CLOSE'),true);
assert.equal(close.post_entry_dow_break_observation.close_event_emitted,false);
console.log('PASS normal_hsi_anchor_v0_24_break_reconfirm_no_close');
