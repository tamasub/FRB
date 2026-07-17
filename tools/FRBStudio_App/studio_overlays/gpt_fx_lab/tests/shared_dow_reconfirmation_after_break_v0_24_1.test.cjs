const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const root = path.resolve(process.argv[2] || process.cwd());
function ap(...parts) { const p = path.join(root, ...parts); if (fs.existsSync(p)) return p; const w = path.join(root, parts.join('\\')); if (fs.existsSync(w)) return w; throw new Error(`missing ${parts.join('/')}`); }
const pluginPath = ap('studio_overlays','gpt_fx_lab','plugins','fx_chart_viewer','plugin.js');
const profilePath = ap('studio_overlays','gpt_fx_lab','simulation','fx_simulation_run_profile_normal_plus_expansion_lite_v0_1.json');
const m5Path = ap('studio_overlays','gpt_fx_lab','data','fx_usdjpy_m5_t3_data_v0_1.json');
const d1Path = ap('studio_overlays','gpt_fx_lab','data','fx_usdjpy_d1_t3_data_v0_1.json');
const source = fs.readFileSync(pluginPath,'utf8'); const idx = source.lastIndexOf('})();');
const hook = `window.__t={normalizeAllRows,simulationRunDraftFromProfile,buildSimulationRunSnapshot,buildEmptySimulationTrace,compactSimulationContinuationSnapshot,validateSimulationRunDraft};`;
const ctx = { window:{}, console, setTimeout, clearTimeout, URL, structuredClone, Intl, Date, Math, JSON, Map, Set, Promise, requestAnimationFrame: cb => setTimeout(cb,0) };
vm.runInNewContext(source.slice(0,idx)+hook+source.slice(idx),ctx,{filename:pluginPath}); const api=ctx.window.__t;
const profile = JSON.parse(fs.readFileSync(profilePath,'utf8')); assert.equal(api.validateSimulationRunDraft(profile).valid,true);
(async()=>{
  const m5=JSON.parse(fs.readFileSync(m5Path,'utf8')); const d1=JSON.parse(fs.readFileSync(d1Path,'utf8')); const rows=api.normalizeAllRows(m5);
  const state={simulationSource:m5,simulationAllRows:rows,upperMapSource:d1,upperMapAllRows:api.normalizeAllRows(d1),simulationRunDraft:api.simulationRunDraftFromProfile(profile),windowStart:0,windowSize:rows.length,chartLayout:'m5_execution',upperTimeframe:'H1',upperConfirmBars:7,dayConfirmBars:45,weekConfirmBars:20,confirmBars:20,upperWarmupBars:200,simulationTrace:api.buildEmptySimulationTrace(m5),simulationRunSnapshot:null,simulationRunReferenceOverrideMs:null,simulationRunReferenceSource:'focused_shared_dow_step',hsiAnnotations:[],simulationTraceEvents:[]};
  const from=rows.findIndex(row=>row.datetime==='2025-10-29 20:50'); const to=rows.findIndex(row=>row.datetime==='2025-10-29 21:45');
  let finalSnapshot=null;
  for(let i=from;i<=to;i+=1){const row=rows[i];state.simulationRunReferenceOverrideMs=new Date(row.datetime.replace(' ','T')).getTime()+5*60*1000-1;const result=api.buildSimulationRunSnapshot(state,{skipTraceReplay:true});assert.ok(result.snapshot,`snapshot failed ${row.datetime}`);finalSnapshot=result.snapshot;const cont=api.compactSimulationContinuationSnapshot(result.snapshot);state.simulationRunSnapshot=cont;state.simulationTrace.run_snapshot=cont;}
  const events=finalSnapshot.position_lifecycle.execution_events||[];
  const normalEntry=events.find(e=>e.rule_lane==='NORMAL'&&e.event_type==='entry');
  const liteEntry=events.find(e=>e.rule_lane==='EXPANSION_LITE'&&e.event_type==='entry');
  const normalClose=events.find(e=>e.rule_lane==='NORMAL'&&e.event_type==='close');
  const liteAddOn=events.find(e=>e.rule_lane==='EXPANSION_LITE'&&e.event_type==='add_on');
  assert.ok(normalEntry,'崩壊後の新Dow再確定をNORMALが取得できていません');
  assert.ok(liteEntry,'共有Dow再確定をEXPANSION_LITEが取得できていません');
  assert.ok(normalClose,'NORMAL R2.5 Closeがありません');
  assert.ok(liteAddOn,'EXPANSION_LITE R3.5 Add-onがありません');
  assert.equal(normalEntry.simulation_time,'2025-10-29 21:04');
  assert.equal(liteEntry.simulation_time,'2025-10-29 21:39');
  assert.equal(liteAddOn.simulation_time,'2025-10-29 21:44');
  console.log('PASS shared_dow_reconfirmation_after_break_v0_24_1');
  console.log(`normal=${normalEntry.simulation_time} lite=${liteEntry.simulation_time} add_on=${liteAddOn.simulation_time}`);
})().catch(error=>{console.error(error);process.exitCode=1;});
