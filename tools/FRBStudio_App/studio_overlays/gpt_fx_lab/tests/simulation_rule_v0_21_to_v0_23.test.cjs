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
  throw new Error(`missing: ${parts.join('/')}`);
}
const pluginPath = artifactPath('studio_overlays','gpt_fx_lab','plugins','fx_chart_viewer','plugin.js');
const profilePath = artifactPath('studio_overlays','gpt_fx_lab','simulation','fx_simulation_run_profile_v0_1.json');
const combinedPath = artifactPath('studio_overlays','gpt_fx_lab','simulation','fx_simulation_run_profile_normal_plus_expansion_lite_v0_1.json');
const source = fs.readFileSync(pluginPath,'utf8');
const profile = JSON.parse(fs.readFileSync(profilePath,'utf8'));
const combined = JSON.parse(fs.readFileSync(combinedPath,'utf8'));
const hook = `
  window.__fxRuleV024Test = {
    m5ExecutionEntryGuardDecision,
    m5ExecutionNormalStopPlan,
    m5ExecutionExpireNormalOpportunitiesPriorToDowBreak,
    normalRuleLaneCloseDecision,
    validateSimulationRunDraft
  };
`;
const closeIndex = source.lastIndexOf('})();');
const instrumented = source.slice(0, closeIndex) + hook + source.slice(closeIndex);
const context = {window:{},console,setTimeout,clearTimeout,URL,structuredClone,Intl,Date,Math,JSON,Map,Set,Promise};
vm.runInNewContext(instrumented, context, {filename:pluginPath});
const api = context.window.__fxRuleV024Test;
const policy = profile.m5_execution_policy;

assert.equal(profile.m5_execution_policy.normal_entry_policy.rule_version,'v0.24');
assert.equal(profile.m5_execution_policy.entry_guard_policy.normal_h4_same_direction_r4.block_at_or_above_raw,233);
assert.equal(profile.m5_execution_policy.entry_guard_policy.day_up_h4_down_r5_short.block_at_or_above_raw,377);
assert.equal(profile.m5_execution_policy.normal_close_miss_policy.max_loss_to_reward_ratio,1.0);
assert.equal(combined.m5_execution_policy.normal_entry_policy.rule_version,'v0.24');

const normalR4 = api.m5ExecutionEntryGuardDecision('NORMAL','LONG',{
  timeframes:{DAY:{trend_state:'UP'},H4:{cycle_state:{direction:'UP_CYCLE',origin:{point_id:'h4low',pivot_time:'t0',pivot_price:100}}}}
},101.398,policy);
assert.equal(normalR4.blocked,true);
assert.equal(normalR4.primary_reason_code,'NORMAL_H4_SAME_DIRECTION_R4_ENTRY_BLOCKED');
const normalBelowR4 = api.m5ExecutionEntryGuardDecision('NORMAL','LONG',{
  timeframes:{DAY:{trend_state:'UP'},H4:{cycle_state:{direction:'UP_CYCLE',origin:{pivot_price:100}}}}
},101.3979,policy);
assert.equal(normalBelowR4.blocked,false);

const dayUpR5Short = api.m5ExecutionEntryGuardDecision('EXPANSION_LITE','SHORT',{
  timeframes:{DAY:{trend_state:'UP'},H4:{cycle_state:{direction:'DOWN_CYCLE',origin:{point_id:'h4high',pivot_time:'t0',pivot_price:500}}}}
},497.738,policy);
assert.equal(dayUpR5Short.blocked,true);
assert.equal(dayUpR5Short.primary_reason_code,'DAY_UP_H4_DOWN_R5_SHORT_ENTRY_BLOCKED');

for (const transientState of ['REVERSAL_WATCH','NO_TREND','UNDETERMINED']) {
  const transientPortfolio={normal_entry_opportunities:[{
    opportunity_id:`opp_${transientState}`,status:'WAITING_R2',direction:'LONG',dow_confirmation_id:'conf1',confirmed_at_ms:1000,anchor_id:'a1',anchor_price:100
  }],normal_anchor_lifecycle:{status:'WAITING_R2',active_anchor_id:'a1',active_confirmation_id:'conf1'}};
  const transientExpired=api.m5ExecutionExpireNormalOpportunitiesPriorToDowBreak(
    transientPortfolio,{m5_trend:transientState},null,policy,2000,'2026-01-01 00:00',{
      trend_detail:{normal_dow_structure_break:{break_at:'2026-01-01 00:00',break_at_ms:1900,break_event_id:`break_${transientState}`,break_state:transientState,previous_direction:'UP'}}
    }
  );
  assert.equal(transientExpired.length,1,`${transientState}への確定遷移でWAITING_R2を失効する必要があります。`);
  assert.equal(transientPortfolio.normal_entry_opportunities[0].status,'EXPIRED');
  assert.equal(transientPortfolio.normal_entry_opportunities[0].r2_history_retired_before_entry,true);
}

const portfolio={normal_entry_opportunities:[{
  opportunity_id:'opp1',status:'WAITING_R2',direction:'LONG',dow_confirmation_id:'conf1',confirmed_at_ms:1000
}]};
const expired=api.m5ExecutionExpireNormalOpportunitiesPriorToDowBreak(
  portfolio,{m5_trend:'DOWN'},{confirmation_id:'conf2',direction:'DOWN',confirmed_at_ms:2100},policy,2200,'2026-01-01 00:00'
);
assert.equal(expired.length,1);
assert.equal(portfolio.normal_entry_opportunities[0].status,'EXPIRED');
assert.equal(portfolio.normal_entry_opportunities[0].terminal_reason_code,'NORMAL_DOW_STRUCTURE_BROKEN_BEFORE_ENTRY');
assert.equal(portfolio.normal_entry_opportunities[0].anchor_invalidated_before_entry,true);
assert.equal(portfolio.normal_entry_opportunities[0].structure_break_confirmation_id,'conf2');

const staleOppositePortfolio={normal_entry_opportunities:[{
  opportunity_id:'opp_stale',status:'WAITING_R2',direction:'LONG',dow_confirmation_id:'conf_new',confirmed_at_ms:3000
}]};
const staleExpired=api.m5ExecutionExpireNormalOpportunitiesPriorToDowBreak(
  staleOppositePortfolio,{m5_trend:'DOWN'},{confirmation_id:'conf_old',direction:'DOWN',confirmed_at_ms:2000},policy,3200,'2026-01-01 00:00'
);
assert.equal(staleExpired.length,0,'古い逆方向Confirmationで新しいOpportunityを失効してはいけません。');

const stop1=api.m5ExecutionNormalStopPlan(100,150,20,'LONG',policy);
assert.equal(stop1.valid,true);
assert.equal(stop1.reward_distance,50);
assert.equal(stop1.stop_price,50);
assert.equal(stop1.hsi_anchor_hard_limit_applied,false);
const policy15=structuredClone(policy);
policy15.normal_close_miss_policy.max_loss_to_reward_ratio=1.5;
const stop15=api.m5ExecutionNormalStopPlan(100,150,40,'LONG',policy15);
assert.equal(stop15.ratio_stop_price,25);
assert.equal(stop15.stop_price,40);
assert.equal(stop15.hsi_anchor_hard_limit_applied,true);

const closeWait=api.normalRuleLaneCloseDecision({
  activePosition:{
    side:'LONG',entry_price:100,units_open:10,
    risk_profile:{stop_price:50},close_miss_plan:{max_loss_to_reward_ratio:1.0},
    target_plan:{next_target_price:150,next_target_label:'R2.5'}
  },
  currentBar:{open:110,high:120,low:105,close:115},
  m5State:{trend_state:'DOWN'}
});
assert.equal(closeWait.action,'WAIT','Entry後のDow崩壊だけで自動Closeしてはいけません。');

const validation=api.validateSimulationRunDraft(profile);
assert.equal(validation.valid,true,validation.errors.join('\n'));
console.log('PASS simulation_rule_v0_21_to_v0_24');
