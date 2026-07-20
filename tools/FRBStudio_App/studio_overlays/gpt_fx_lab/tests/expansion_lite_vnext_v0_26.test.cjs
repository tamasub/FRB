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
const profilePath = artifactPath('studio_overlays','gpt_fx_lab','simulation','fx_simulation_run_profile_expansion_lite_v0_1.json');
const source = fs.readFileSync(pluginPath,'utf8');
const manifest = JSON.parse(fs.readFileSync(manifestPath,'utf8'));
const profile = JSON.parse(fs.readFileSync(profilePath,'utf8'));

assert.equal(manifest.version, '0.9.1.23');
const lite = profile.m5_execution_policy.expansion_lite_policy;
assert.equal(lite.rule_version,'v0.27');
assert.equal(lite.episode_anchor_lifecycle,'FIXED_AFTER_FIRST_M5_DOW_CONFIRMATION');
assert.equal(lite.dow_break_anchor_policy,'KEEP_ANCHOR_AND_EPISODE');
assert.equal(lite.entry_trigger,'VALID_R3_TOUCH_WHILE_T3_ALIGNED');
assert.equal(lite.t3_exit_grace_bars,3);
assert.equal(lite.t3_exit_touch_source,'M5_CLOSE');
assert.equal(lite.structural_exit,'SHADOW_ONLY_NO_CLOSE');

const hook = `
window.__liteV026 = {
  normalizeSimulationRunProfile,
  validateSimulationRunDraft,
  m5ExecutionLevelTouch,
  m5ExecutionExpansionLiteEpisode,
  expansionLiteRuleLaneEntryDecision,
  expansionLiteRuleLaneCloseDecision
};`;
const closeIndex = source.lastIndexOf('})();');
const instrumented = source.slice(0, closeIndex) + hook + source.slice(closeIndex);
const context = { window:{}, console, setTimeout, clearTimeout, URL, structuredClone, Intl, Date, Math, JSON, Map, Set, Promise };
vm.runInNewContext(instrumented, context, {filename:pluginPath});
const api = context.window.__liteV026;
const normalized = api.normalizeSimulationRunProfile(profile);
const validation = api.validateSimulationRunDraft(normalized);
assert.equal(validation.valid,true,validation.errors.join('\n'));
const policy = normalized.m5_execution_policy;

function resolution(id, direction, price, startedAt='2025-12-01 10:00', startedMs=Date.parse('2025-12-01T10:00:00+09:00')) {
  return {
    status:'RESOLVED_REFERENCE', direction, anchor_id:id, detection_anchor_id:id, entry_anchor_id:id,
    anchor:{anchor_id:id,direction,pivot_time:'2025-12-01 09:00',price,
      expansion_detection_regime:{direction,started_at:startedAt,started_at_ms:startedMs}}
  };
}

// 同方向の再確定・起点候補変更では、最初のEpisode Anchorを維持する。
const portfolio = {trades:[],positions:[],expansion_lite_episodes:[],expansion_lite_entry_opportunities:[],used_expansion_lite_episode_ids:[]};
const t0 = Date.parse('2025-12-01T10:00:00+09:00');
const first = api.m5ExecutionExpansionLiteEpisode(portfolio,resolution('anchor_A','DOWN',155.560),t0,'2025-12-01 10:00');
const sameDirectionNewAnchor = api.m5ExecutionExpansionLiteEpisode(portfolio,resolution('anchor_B','DOWN',155.200,'2025-12-01 11:00',t0+3600000),t0+3600000,'2025-12-01 11:00');
assert.equal(sameDirectionNewAnchor.episode_id,first.episode_id);
assert.equal(sameDirectionNewAnchor.entry_anchor_id,'anchor_A');
assert.equal(sameDirectionNewAnchor.entry_anchor_price,155.560);
assert.equal(sameDirectionNewAnchor.latest_observed_detection_anchor_id,'anchor_B');
assert.equal(sameDirectionNewAnchor.last_anchor_change_reason_code,'EXPANSION_LITE_SAME_DIRECTION_ANCHOR_CHANGE_IGNORED');

const entryResolution = resolution('anchor_A','DOWN',155.560);
const r3Price = 154.696;
const factsMisaligned = {
  episode_side:'SHORT', confirmation_side:'SHORT', entry_direction_ready:false,
  h4_t3_side_short:true, h1_t3_side_short:false,
  h4_t3_side_long:false, h1_t3_side_long:false,
  h1_cycle_entry_allowed:true, h1_cycle_elapsed_bars:4, h1_cycle_entry_allowed_max_bars:14
};
const factsAligned = {...factsMisaligned,entry_direction_ready:true,h1_t3_side_short:true};
function decide(ms,time,bar,facts) {
  const r3=api.m5ExecutionLevelTouch(bar,155.560,'SHORT',144,'R3',policy);
  return api.expansionLiteRuleLaneEntryDecision({
    portfolio,referenceMs:ms,referenceTime:time,price:bar.close,currentBar:bar,
    expansionLiteFacts:facts,entryResolution,entryAnchor:entryResolution.anchor,anchorPrice:155.560,
    distanceRaw:144,r3Touch:r3,policy,timeframeSnapshot:{timeframes:{H4:{},H1:{},M5:{}}}
  });
}

// T3不整合中のR3タッチは消費せず、再タッチ待ち。
const d1=decide(t0+7200000,'2025-12-01 12:00',{open:154.760,high:154.780,low:154.680,close:154.680},factsMisaligned);
assert.equal(d1.action,'WAIT');
assert.equal(d1.entry_opportunity.initial_entry_status,'WAITING_R3');
assert.ok(d1.reason_codes.includes('EXPANSION_LITE_R3_TOUCH_T3_NOT_ALIGNED_RETOUCH_REQUIRED'));
assert.equal(d1.entry_opportunity.r3_retouch_required,true);

// 外側に居続けてT3が揃っても、遅れてEntryしない。
const d2=decide(t0+7500000,'2025-12-01 12:05',{open:154.680,high:154.690,low:154.620,close:154.650},factsAligned);
assert.equal(d2.action,'WAIT');
assert.ok(d2.reason_codes.includes('EXPANSION_LITE_WAITING_R3_RETURN_INSIDE'));

// M5 CloseがR3内側へ戻ると再武装。
const d3=decide(t0+7800000,'2025-12-01 12:10',{open:154.650,high:154.730,low:154.640,close:154.710},factsAligned);
assert.equal(d3.action,'WAIT');
assert.equal(d3.entry_opportunity.r3_retouch_required,false);
assert.equal(d3.entry_opportunity.r3_retouch_armed,true);

// 次の内側→外側の再タッチでEntry。
const d4=decide(t0+8100000,'2025-12-01 12:15',{open:154.710,high:154.720,low:154.660,close:154.680},factsAligned);
assert.equal(d4.action,'ENTRY');
assert.equal(d4.execution_candidate.anchor_id,'anchor_A');
assert.equal(d4.execution_candidate.anchor_price,155.560);
assert.equal(d4.entry_opportunity.entry_execution_mode,'VALID_R3_TOUCH_WHILE_T3_ALIGNED');
assert.ok(d4.reason_codes.includes('EXPANSION_LITE_VALID_R3_TOUCH'));

function tradeAndPosition() {
  const trade={trade_id:'lite_trade_001',status:'OPEN',rule_lane:'EXPANSION_LITE',side:'SHORT',entry_price:r3Price,entry_anchor_price:155.560,target_price:153.298,consumed_add_on_levels:[],t3_exit_observed_m5_bars_after_entry:0};
  const position={position_id:'lite_pos_001',trade_id:trade.trade_id,status:'OPEN',rule_lane:'EXPANSION_LITE',side:'SHORT',units_open:10,entry_price:r3Price,entry_anchor_price:155.560};
  return {trade,position};
}
const brokenState={trend_state:'UP',trend_detail:{high_relation:'HIGHER',low_relation:'HIGHER'}};
const safeBar={open:154.70,high:154.76,low:154.60,close:154.75,t3_20_0_2:154.70}; // ShortではClose>T3
const tp={...policy,expansion_lite_policy:{...policy.expansion_lite_policy,add_on_levels:[]}};
const pair=tradeAndPosition();
for(let i=1;i<=3;i++){
  const c=api.expansionLiteRuleLaneCloseDecision({activePosition:pair.position,activeTrade:pair.trade,currentBar:safeBar,m5State:brokenState,policy:tp,referenceMs:t0+i*300000,referenceTime:`bar${i}`});
  assert.equal(c.action,'WAIT');
  assert.equal(c.bar_touch.t3_exit_armed,false);
  assert.ok(c.reason_codes.includes('EXPANSION_LITE_T3_EXIT_GRACE_ACTIVE'));
  assert.ok(c.reason_codes.includes('EXPANSION_LITE_STRUCTURAL_BREAK_SHADOW_OBSERVED'));
}
const c4=api.expansionLiteRuleLaneCloseDecision({activePosition:pair.position,activeTrade:pair.trade,currentBar:safeBar,m5State:brokenState,policy:tp,referenceMs:t0+1200000,referenceTime:'bar4'});
assert.equal(c4.action,'FULL_CLOSE');
assert.equal(c4.exit_type,'T3_EXIT');
assert.equal(c4.execution_price,safeBar.close);
assert.equal(c4.bar_touch.t3_exit_bar_number_after_entry,4);
assert.equal(c4.bar_touch.structural_exit_shadow_only,true);

// Anchor ExitはGrace中でも即時有効。
const pair2=tradeAndPosition();
const anchorClose=api.expansionLiteRuleLaneCloseDecision({activePosition:pair2.position,activeTrade:pair2.trade,currentBar:{open:155.50,high:155.60,low:155.40,close:155.50,t3_20_0_2:155.45},m5State:{trend_state:'DOWN',trend_detail:{}},policy:tp,referenceMs:t0+300000,referenceTime:'anchor'});
assert.equal(anchorClose.action,'FULL_CLOSE');
assert.equal(anchorClose.exit_type,'ANCHOR_EXIT');

assert.match(source,/SHADOW_ONLY_NO_CLOSE/);
assert.match(source,/FOURTH_M5_BAR_AFTER_ENTRY/);
console.log('PASS expansion_lite_vnext_v0_26');
