// studio_work_0268 date precision - use real Parser + SearchFilter without DOM.
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
const c={console,Date};vm.createContext(c);
for (const f of ['wwwroot/js/responsibilities/smart_search_engine.js','wwwroot/js/responsibilities/search_filter.js']) {
  vm.runInContext(fs.readFileSync(f,'utf8'),c,{filename:f});
}
const engine=c.StudioSmartSearch, filter=c.SearchFilter;
const fields=[{field:'day',caption:'日付',type:'date'},{field:'at',caption:'日時',type:'datetime'},
  {field:'n',type:'number'}, {field:'label',type:'text'}, {field:'stamp',type:'instant'}];
const rows=[
  {id:1,day:'2026/04/01',at:'2026-10-23T09:00:00.001'},
  {id:2,day:'2026-10-23',at:'2026/10/23 15:00:01'},
  {id:3,day:'2026.11.30',at:'2026.11.30 23:59:59.999'},
  {id:4,day:'2026-12-01',at:'2026-12-01T00:00:00'},
  {id:5,day:'2027-03-31',at:'2027-03-31T23:59:59'},
  {id:6,day:'2027-04-01',at:'2027-04-01T00:00:00'},
];
const fiscal={year_mode:'fiscal',fiscal_year_start_month:4};
const calendar={year_mode:'calendar',fiscal_year_start_month:4};
const ids=(expr,dateSearch=fiscal)=>Array.from(filter.apply(rows,[],{fullText:expr,fields,dateSearch}),x=>x.row.id);
const problem=(expr,code)=>assert.throws(()=>engine.parse(expr,fields,{dateSearch:fiscal}),e=>e.code===code);
test('year in fiscal/calendar mode, month/day precision',()=>{
  assert.deepEqual(ids('日付=2026'),[1,2,3,4,5]);
  assert.deepEqual(ids('日付=2026',calendar),[1,2,3,4]);
  assert.deepEqual(ids('日付=202610'),[2]);
  assert.deepEqual(ids('日付=202611'),[3]);
  assert.deepEqual(ids('日付=20261023'),[2]);
  assert.deepEqual(ids('日付=2026-10-23'),[2]);
  assert.deepEqual(ids('日付=2026/10/23'),[2]);
  assert.deepEqual(ids('日付=2026.10.23'),[2]);
  assert.deepEqual(ids('日付=202610..202611'),[2,3]);
  assert.deepEqual(ids('日付=202610..'),[2,3,4,5,6]);
  assert.deepEqual(ids('日付=..202610'),[1,2]);
  assert.deepEqual(ids('日付=2025..2026'),[1,2,3,4,5]);
});
test('datetime hour/minute/second input precision and inclusive range end',()=>{
  assert.deepEqual(ids('日時=20261023_09'),[1]);
  assert.deepEqual(ids('日時=20261023_15'),[2]);
  assert.deepEqual(ids('日時=20261023_1500'),[2]);
  assert.deepEqual(ids('日時=20261023_150001'),[2]);
  assert.deepEqual(ids('日時=20261023_09..20261023_15'),[1,2]);
  assert.deepEqual(ids('日時=202610..202611'),[1,2,3]);
  assert.deepEqual(ids('日時=20261023..20261130'),[1,2,3]);
  assert.deepEqual(ids('日時=2026-10-23T15:00'),[2]);
  assert.deepEqual(ids('日時=2026-10-23_15:00:01'),[2]);
  assert.deepEqual(ids('日時=20261023_15..20261023_15'),[2]);
});
test('comparators align to interval boundaries, numeric semantics unchanged',()=>{
  assert.deepEqual(ids('日時>20261023_15'),[3,4,5,6]);
  assert.deepEqual(ids('日時>=20261023_15'),[2,3,4,5,6]);
  assert.deepEqual(ids('日時<20261023_15'),[1]);
  assert.deepEqual(ids('日時<=20261023_15'),[1,2]);
  assert.deepEqual(ids('日時!=20261023_15'),[1,3,4,5,6]);
  assert.deepEqual(ids('日時==20261023_15'),[2]);
  assert.equal(engine.evaluate({n:2026},engine.parse('n=2026',fields)),true);
  assert.equal(engine.evaluate({n:2027},engine.parse('n=2026',fields)),false);
  assert.equal(engine.evaluate({label:'20261023'},engine.parse('label=202610',fields)),true);
});
test('invalid dates, unsupported time on date, reverse/empty ranges fail closed',()=>{
  for(const expr of ['日付=20260230','日付=202613','日時=20261023_25','日時=20261023_1560',
    '日時=20261023_150099','日時=20261023_1','日時=20261023_150','日付=20261023_15']) problem(expr,'INVALID_VALUE');
  problem('日付=202611..202610','REVERSED_RANGE');
  problem('日時=20261024_09..20261023_17','REVERSED_RANGE');
  problem('日時=202610..bad','INVALID_RANGE');
  problem('日時=..','INVALID_RANGE');
  assert.equal(engine.parseDatePeriod('20260229','date',fiscal),null);
  assert.ok(engine.parseDatePeriod('20240229','date',fiscal));
  assert.deepEqual(ids('日時=20261023_09..20261023_15 or 日付=202611'),[1,2,3]);
});
test('instant retains timezone-aware ISO search behavior',()=>{
  const row={stamp:'2026-10-23T15:30:00+09:00'};
  assert.equal(engine.evaluate(row,engine.parse('stamp=2026-10-23T06:30:00Z',fields)),true);
  problem('stamp=20261023','INVALID_VALUE');
});
test('settings source and portable interface wire their options',()=>{
  const config=JSON.parse(fs.readFileSync('wwwroot/config/app_settings.json','utf8'));
  assert.deepEqual(config.smart_search.date_search,fiscal);
  const main=fs.readFileSync('wwwroot/index.html','utf8');
  assert.match(main,/smart_search_date_settings\.js/);
  assert.match(fs.readFileSync('wwwroot/js/renderers/grid_detail.js','utf8'),/StudioSmartSearchDateSettings\.get\(\)/);
  assert.match(fs.readFileSync('data/markdown/40_Copilotくんへ/FRB_SmartSearch_JS_v0_1/js/frb_smart_search_api.js','utf8'),/dateSearch:options\.dateSearch/);
  assert.equal(fs.readFileSync('wwwroot/js/responsibilities/smart_search_engine.js','utf8'),fs.readFileSync('data/markdown/40_Copilotくんへ/FRB_SmartSearch_JS_v0_1/js/smart_search_engine.js','utf8'));
});

// Regression: real incident data mixes date-only, Studio local datetime,
// and ISO datetime with timezone offsets in one ViewDef datetime column.
test('datetime stored values use calendar/time as written regardless of optional offset',()=>{
  const mixed = [
    {id:1,at:'2026-06-21'},
    {id:2,at:'2026-10-11T21:02:30+09:00'},
    {id:3,at:'2026-09-18_19:09:34'},
    {id:4,at:'2027-03-31T23:59:59+09:00'},
    {id:5,at:'2027-04-01'},
    {id:6,at:'2026-10-23T00:45:00Z'},
    {id:7,at:'2026-10-23T23:45:00-07:00'},
    {id:8,at:'2026-02-30'},
    {id:9,at:'2026-10-23T18:45:00+19:00'},
    {id:10,at:null},
  ];
  const find=(expr,options=fiscal)=>mixed.filter(row=>engine.evaluate(row,engine.parse(expr,fields,{dateSearch:options}))).map(x=>x.id);
  assert.deepEqual(find('日時=2026'),[1,2,3,4,6,7]);
  assert.deepEqual(find('日時=202610'),[2,6,7]);
  assert.deepEqual(find('日時=202610..202611'),[2,6,7]);
  assert.deepEqual(find('日時=20261023_00'),[6]);
  assert.deepEqual(find('日時=20261023_23'),[7]);
  assert.deepEqual(find('日時=202610',calendar),[2,6,7]);
  // Instant search does *not* use this local wall-clock interpretation.
  assert.equal(engine.evaluate({stamp:'2026-10-23T15:30:00+09:00'},engine.parse('stamp=2026-10-23T06:30:00Z',fields)),true);
});

test('real 256-record incident data: 2026 fiscal-year datetime search does not lose date-only or offset rows',()=>{
  const incident=JSON.parse(fs.readFileSync('data/json/01_main/_studio_work_incident_data_v2.json','utf8'));
  const all=incident.work_items;
  const names=[{field:'created_at',caption:'作成日',type:'datetime'}];
  const search=expr=>all.filter(row=>engine.evaluate(row,engine.parse(expr,names,{dateSearch:fiscal})));
  // Independent expected results from the yyyy-mm-dd date portion of the stored value.
  const expected=all.filter(row=>{const d=String(row.created_at??'').slice(0,10);return d>='2026-04-01' && d<'2027-04-01';});
  assert.ok(expected.length>=200, 'fixture contains many mixed 2026 records');
  assert.equal(search('作成日=2026').length,expected.length);
  const integrated=filter.apply(all,[],{fullText:'作成日=2026',fields:names,dateSearch:fiscal});
  assert.equal(integrated.length,expected.length, 'SearchFilter / Studio UI pipeline also sees all rows');
  assert.equal(search('作成日=202610').length,all.filter(row=>String(row.created_at??'').startsWith('2026-10')).length);
  assert.equal(search('作成日=202610..202611').length,
    all.filter(row=>String(row.created_at??'').slice(0,7)>='2026-10' && String(row.created_at??'').slice(0,7)<='2026-11').length);
});
