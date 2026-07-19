const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const root = path.resolve(process.argv[2] || process.cwd());
function ap(...parts){ const p=path.join(root,...parts); if(fs.existsSync(p))return p; const w=path.join(root,parts.join('\\')); if(fs.existsSync(w))return w; throw new Error(`missing ${parts.join('/')}`); }
const pluginPath=ap('studio_overlays','gpt_fx_lab','plugins','fx_chart_viewer','plugin.js');
const manifest=JSON.parse(fs.readFileSync(ap('studio_overlays','gpt_fx_lab','plugins','fx_chart_viewer','plugin.json'),'utf8'));
const profile=JSON.parse(fs.readFileSync(ap('studio_overlays','gpt_fx_lab','simulation','fx_simulation_run_profile_normal_plus_expansion_lite_v0_1.json'),'utf8'));
const source=fs.readFileSync(pluginPath,'utf8');
assert.equal(manifest.version,'0.9.1.22');
assert.equal(profile.m5_execution_policy.rule_lane_policy.active_entry_rule_lane,'PARALLEL_RULE_LANES');
assert.equal(profile.m5_execution_policy.rule_lane_policy.cross_lane_condition_sharing,'FORBIDDEN');
assert.equal(profile.m5_execution_policy.expansion_lite_policy.other_lane_trade_state_input,'FORBIDDEN');
const hook=`window.__parallelV025={normalizeSimulationRunProfile,validateSimulationRunDraft,m5RuleLanePolicy,m5ExecutionLaneLifecycleSlice};`;
const i=source.lastIndexOf('})();');
const ctx={window:{},console,setTimeout,clearTimeout,URL,structuredClone,Intl,Date,Math,JSON,Map,Set,Promise};
vm.runInNewContext(source.slice(0,i)+hook+source.slice(i),ctx,{filename:pluginPath});
const api=ctx.window.__parallelV025;
const normalized=api.normalizeSimulationRunProfile(profile);
const validation=api.validateSimulationRunDraft(normalized);
assert.equal(validation.valid,true,validation.errors.join('\n'));
const lanePolicy=api.m5RuleLanePolicy(normalized.m5_execution_policy);
assert.deepEqual(Array.from(lanePolicy.enabled_entry_rule_lanes),['NORMAL','EXPANSION_LITE']);
assert.equal(lanePolicy.parallel_entry_enabled,true);

const master={
  portfolio:{
    positions:[
      {position_id:'n1',trade_id:'nt1',rule_lane:'NORMAL',status:'OPEN',units_open:10},
      {position_id:'l1',trade_id:'lt1',rule_lane:'EXPANSION_LITE',status:'OPEN',units_open:10}
    ],
    trades:[
      {trade_id:'nt1',rule_lane:'NORMAL',status:'OPEN'},
      {trade_id:'lt1',rule_lane:'EXPANSION_LITE',status:'OPEN',expansion_lite_episode_id:'ep1'}
    ],
    normal_entry_opportunities:[{opportunity_id:'nopp'}],
    expansion_lite_episodes:[{episode_id:'ep1',status:'ACTIVE',initial_entry_status:'USED',direction:'SHORT'}],
    expansion_lite_entry_opportunities:[{episode_id:'ep1',status:'ACTIVE',initial_entry_status:'USED',direction:'SHORT'}],
    active_expansion_lite_episode_id:'ep1',
    used_expansion_lite_episode_ids:['ep1'],
    active_trade_ids_by_lane:{NORMAL:'nt1',EXPANSION_LITE:'lt1'},
    last_evaluated_reference_key_by_lane:{NORMAL:'nkey',EXPANSION_LITE:'lkey'},
    evaluated_reference_count_by_lane:{NORMAL:1,EXPANSION_LITE:1}
  },
  decision_events:[],state_change_events:[],execution_events:[]
};
const normal=api.m5ExecutionLaneLifecycleSlice(master,'NORMAL');
const lite=api.m5ExecutionLaneLifecycleSlice(master,'EXPANSION_LITE');
assert.deepEqual(normal.portfolio.positions.map(x=>x.rule_lane),['NORMAL']);
assert.equal(normal.portfolio.expansion_lite_episodes.length,0);
assert.deepEqual(lite.portfolio.positions.map(x=>x.rule_lane),['EXPANSION_LITE']);
assert.equal(lite.portfolio.normal_entry_opportunities.length,0);
assert.equal(lite.portfolio.expansion_lite_episodes.length,1);
assert.equal(lite.portfolio.active_expansion_lite_episode_id,'ep1');
assert.match(source,/EVALUATE_EACH_RULE_LANE_INDEPENDENTLY/);
assert.match(source,/other_lane_trade_state_input/);
console.log('PASS normal_plus_expansion_lite_orchestration_v0_1');
