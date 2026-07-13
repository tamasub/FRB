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
const m5Path = artifactPath('studio_overlays','gpt_fx_lab','data','fx_usdjpy_m5_t3_data_v0_1.json');
const d1Path = artifactPath('studio_overlays','gpt_fx_lab','data','fx_usdjpy_d1_t3_data_v0_1.json');
const source = fs.readFileSync(pluginPath,'utf8');
const profile = JSON.parse(fs.readFileSync(profilePath,'utf8'));
assert.equal(profile.m5_execution_policy.normal_entry_policy.rule_version,'v0.17.1');
assert.equal(profile.m5_execution_policy.normal_entry_policy.normal_hsi_anchor_retired_on_close,true);
assert.equal(profile.m5_execution_policy.normal_entry_policy.normal_hsi_anchor_reuse_after_close,false);
assert.match(source,/function m5ExecutionRetireNormalAnchor\(/);
assert.match(source,/NORMAL_HSI_ANCHOR_RETIRED_ON_CLOSE/);
assert.match(source,/rule_normal_hsi_anchor_retired_immediately_on_close/);
assert.match(source,/status = 'AWAITING_NEW_DOW_CONFIRMATION'/);
assert.match(source,/boundaryEpsilon = 1e-6/);
const hook = `
  window.__fxNormalAnchorLifecycleTest = {
    normalizeAllRows,
    simulationRunDraftFromProfile,
    buildVisibleRangeSimulationRun,
    buildEmptySimulationTrace,
    validateSimulationRunDraft,
    m5ExecutionHsiBand
  };
`;
const closeIndex = source.lastIndexOf('})();');
const instrumented = source.slice(0,closeIndex)+hook+source.slice(closeIndex);
const context={window:{},console,setTimeout,clearTimeout,URL,structuredClone,Intl,Date,Math,JSON,Map,Set,Promise,requestAnimationFrame:cb=>setTimeout(cb,0)};
vm.runInNewContext(instrumented,context,{filename:pluginPath});
const api=context.window.__fxNormalAnchorLifecycleTest;
const validation=api.validateSimulationRunDraft(profile);
assert.equal(validation.valid,true,validation.errors.join('\n'));
const exactBand=api.m5ExecutionHsiBand(88.99999999999999,profile.m5_execution_policy);
assert.equal(exactBand.current.label,'R2','R2境界の浮動小数点誤差でcurrentがR1へ戻っています。');
assert.equal(exactBand.next.label,'R2.5','R2 EntryのTargetがR2.5になっていません。');
(async()=>{
  const m5=JSON.parse(fs.readFileSync(m5Path,'utf8'));
  const d1=JSON.parse(fs.readFileSync(d1Path,'utf8'));
  const state={
    simulationSource:m5,
    simulationAllRows:api.normalizeAllRows(m5),
    upperMapSource:d1,
    upperMapAllRows:api.normalizeAllRows(d1),
    simulationRunDraft:api.simulationRunDraftFromProfile(profile),
    windowStart:520,
    windowSize:180,
    chartLayout:'m5_execution',
    upperTimeframe:'H1',upperConfirmBars:7,dayConfirmBars:45,weekConfirmBars:20,confirmBars:20,upperWarmupBars:200,
    simulationTrace:api.buildEmptySimulationTrace(m5),simulationRunSnapshot:null,simulationRunReferenceOverrideMs:null,simulationRunReferenceSource:'visible_range_step',hsiAnnotations:[],simulationTraceEvents:[]
  };
  const result=await api.buildVisibleRangeSimulationRun(state);
  assert.equal(result.validation.valid,true,(result.validation.errors||[]).join(' / '));
  const run=result.rangeRun;
  const events=run.execution_events||[];
  const entries=events.filter(e=>e.event_type==='entry'&&String(e.rule_lane||e.execution?.rule_lane).toUpperCase()==='NORMAL');
  const closes=events.filter(e=>['close','stop_close'].includes(e.event_type)&&String(e.rule_lane||e.execution?.rule_lane).toUpperCase()==='NORMAL');
  assert.ok(entries.length>=2,`Normal Entryが不足しています: ${entries.length}`);
  assert.ok(closes.length>=2,`Normal Closeが不足しています: ${closes.length}`);
  const firstClose=closes[0];
  assert.equal(firstClose.execution?.normal_hsi_anchor_retired,true,'Close時に通常HSI起点が破棄されていません。');
  assert.ok(firstClose.execution?.normal_hsi_anchor_retired_anchor_id,'破棄した通常HSI起点IDがありません。');
  assert.equal(firstClose.state_after?.portfolio?.normal_anchor_lifecycle?.status,'AWAITING_NEW_DOW_CONFIRMATION');
  assert.equal(firstClose.state_after?.portfolio?.normal_anchor_lifecycle?.active_anchor_id,null);
  const nextEntry=entries.find(e=>Date.parse(e.simulation_time)>Date.parse(firstClose.simulation_time));
  assert.ok(nextEntry,'Close後の次のNormal Entryがありません。');
  assert.ok(Date.parse(nextEntry.simulation_time)>Date.parse(firstClose.simulation_time));
  assert.notEqual(nextEntry.execution?.entry_anchor_id,firstClose.execution?.normal_hsi_anchor_retired_anchor_id,'Close済み通常HSI起点を次回Entryへ再利用しています。');
  assert.notEqual(nextEntry.execution?.dow_confirmation_id,firstClose.execution?.normal_hsi_anchor_retired_confirmation_id,'Close前のDow Confirmationを次回Entryへ再利用しています。');
  const ann=(run.simulation_hsi_annotations||[]).find(a=>String(a.trade_id||'')===String(firstClose.trade_id||''));
  assert.ok(ann,'Close対象TradeのSimulation HSI annotationがありません。');
  assert.equal(ann.lifecycle_status,'RETIRED_ON_NORMAL_CLOSE');
  assert.equal(ann.retired_at_time,firstClose.simulation_time);
  console.log('PASS normal_hsi_anchor_trade_lifecycle_v0_1');
  console.log(`retired=${firstClose.execution.normal_hsi_anchor_retired_anchor_id} at ${firstClose.simulation_time}`);
  console.log(`next=${nextEntry.execution.entry_anchor_id} at ${nextEntry.simulation_time}`);
})().catch(err=>{console.error(err);process.exitCode=1;});
