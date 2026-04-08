//v0.0.0

const st = document.getElementById('st');
const fpsEl = document.getElementById('fps');
//peakAEl = document.getElementById('peakA');
//peakMEl = document.getElementById('peakM');

const a1 = document.getElementById('a1');
const a2 = document.getElementById('a2');
const a3 = document.getElementById('a3');

const m1 = document.getElementById('m1');
const m2 = document.getElementById('m2');
const m3 = document.getElementById('m3');
const warnEl = document.getElementById('warn');

const canvas = document.getElementById('c');
const g = canvas.getContext('2d');

const specA = document.getElementById('specA');
const specM = document.getElementById('specM');
const gA = specA.getContext('2d');
const gM = specM.getContext('2d');

const tsCanvas = document.getElementById('ts');
const gT = tsCanvas.getContext('2d');
const tsFluxCanvas = document.getElementById('tsFlux');
const gTF = tsFluxCanvas.getContext('2d');
const tsPeakCanvas = document.getElementById('tsPeak');
const gTP = tsPeakCanvas.getContext('2d');
const tsStateCanvas = document.getElementById('tsState');
const gTS = tsStateCanvas.getContext('2d');

const scrEl = document.getElementById('scr');
const scrTxt = document.getElementById('scrTxt');
const scrState = document.getElementById('scrState');

const timeWindowSel = document.getElementById('timeWindow');
const thrEl = document.getElementById('thr');
const thrTxt = document.getElementById('thrTxt');

// latest value (used as reference for the time log at the moment of touch)
let lastScrape = 0;

let selectedShotId = null; // currently selected shot
let viewNowT = null;       // reference time for the time‑log display (null means live)

let shotSeq = 1;
const SNAP_DT = 0.3; // seconds


//Decay = 振動の形　、　Energy = 振動の量

const touchShots = [];
// {t, scrape, peakA, peakM, count, long, kind,
//  preT, preScrape, prePeakA, prePeakM,
//  postT, postScrape, postPeakA, postPeakM,
//  freezeReadyAt, frozenSeries,
//  fluxA, fluxM, peakMoveA, peakMoveM,
//  decayA, decayM, energyA, energyM,
//  attackScore, attackState, attackReason}

const stateTransitions = []; // {t, from, to, state}
let lastPhase2State = 'IDLE';

const STATE_COLORS = {
  IDLE:    '#cfd8dc',
  IMPULSE: '#ef5350',
  SUCTION: '#42a5f5',
  WEED:    '#9ccc65',
};

const STATE_LABELS = {
  IDLE: 'Idle',
  IMPULSE: 'Impulse',
  SUCTION: 'Suction',
  WEED: 'Weed',
};


// TIME LOG view control
let timeLogFollowLatest = true;   // 通常は最新追従
let timeLogCenterSec = null;      // 中央表示したい時刻

let frozenSeries = null; //選択時に、そのイベント周辺の描画用時系列を別保存
let freezeReadyAt =null; //タップ後、いつまでに時系列をfrozenSeriesに保存するか（タップ前の値も欲しいので、タップ後に少し待つ）
let isLoadedSessionMode = false;

const MAX_SHOTS = 200;

let trackA = [];
let trackM = [];

let touchTableEl;

let lastTouchAcceptT = -Infinity;
const TOUCH_DEBOUNCE_SEC = 0.25;

let noiseFluxA = 0.03;
let noiseFluxM = 0.03;


// === Band scoring ===
// const BANDS = [
//   { key:'b0', label:'0-40',    f0:0,   f1:40 },
//   { key:'b1', label:'40-80',   f0:40,  f1:80 },
//   { key:'b2', label:'80-100',  f0:80,  f1:100 },

//   { key:'b3', label:'100-120', f0:100, f1:120 },
//   { key:'b4', label:'120-140', f0:120, f1:140 },
//   { key:'b5', label:'140-160', f0:140, f1:160 },
//   { key:'b6', label:'160-180', f0:160, f1:180 },
//   { key:'b7', label:'180-200', f0:180, f1:200 },

//   { key:'b8', label:'200-300', f0:200, f1:300 },
//   { key:'b9', label:'300+',    f0:300, f1:Infinity },
// ];

const BANDS = [
  { key:'b0', label:'0-80',    f0:0,   f1:80 },
  { key:'b1', label:'80-160',  f0:80,  f1:160 },
  { key:'b2', label:'160-250', f0:160, f1:250 },
  { key:'b3', label:'250-500', f0:250, f1:500 },
];

// const BAND_W = [
//   1.6, //0-40
//   1.4, //40-80
//   1.2, //80-100
//   1.1, //100-120
//   1.0, //120-140
//   0.9, //140-160
//   0.8, //160-180
//   0.7, //180-200
//   0.6, //200-300
//   0.4  //300+
// ];

const BAND_W = [
  1.2, // 0-80
  1.1, // 80-160
  1.0, // 160-250
  0.9  // 250-500
];

function makeZeroBandMap(){
  const out = {};
  for (const b of BANDS) out[b.key] = 0;
  return out;
}

// latest band scores (per type)
let latestBandA = null;
let latestBandM = null;

// EMA for smooth display
const bandEma = {
  A: makeZeroBandMap(),
  M: makeZeroBandMap(),
};

function buildBandRows(containerId, prefixBar, prefixTxt, fillClass){
  const root = document.getElementById(containerId);
  if (!root) return;

  root.innerHTML = '';

  for (const b of BANDS) {
    const row = document.createElement('div');
    row.className = 'bandRow';

    row.innerHTML = `
      <div class="bandLabel">${b.label}</div>
      <div class="bandBar">
        <div id="${prefixBar}_${b.key}" class="${fillClass}"></div>
      </div>
      <div id="${prefixTxt}_${b.key}" class="bandVal">0%</div>
    `;

    root.appendChild(row);
  }
}

window.addEventListener('DOMContentLoaded', () => {
  buildBandRows('bandNowA',  'barA',   'txtA',   'bandFillA');
//  buildBandRows('bandNowM',  'barM',   'txtM',   'bandFillM');

  buildBandRows('bandRecA_A','rbarA',  'rtxtA',  'bandFillA');
  buildBandRows('bandRecA_M','rbarM',  'rtxtM',  'bandFillM');

  buildBandRows('bandRecB_A','rbarA2', 'rtxtA2', 'bandFillA');
  buildBandRows('bandRecB_M','rbarM2', 'rtxtM2', 'bandFillM');
});

function calcBandFlux(spec, prevSpec, df, maxHz){
  const out = makeZeroBandMap();

  if (!spec || !prevSpec || spec.length !== prevSpec.length) {
    return out;
  }

  const maxBin = Math.min(spec.length - 1, Math.floor(maxHz / df));

  for (const b of BANDS) {
    const bandF1 = Number.isFinite(b.f1) ? b.f1 : maxHz;
    const f1 = Math.min(bandF1, maxHz);

    const i0 = Math.max(0, Math.floor(b.f0 / df));
    const i1 = Math.min(maxBin, Math.floor(f1 / df));

    out[b.key] = calcSpectralFlux(spec, prevSpec, i0, i1);
  }

  return out;
}

function calcBandSums(specLin, df, maxHz){
  const out = makeZeroBandMap();
  out.total = 0;

  const maxBin = Math.min(specLin.length - 1, Math.floor(maxHz / df));

  for (let i = 0; i <= maxBin; i++) {
    const v = specLin[i] || 0;
    out.total += v;
  }

  for (const b of BANDS) {
    const bandF1 = Number.isFinite(b.f1) ? b.f1 : maxHz;
    const f1 = Math.min(bandF1, maxHz);

    const i0 = Math.max(0, Math.floor(b.f0 / df));
    const i1 = Math.min(maxBin, Math.floor(f1 / df));

    let s = 0;
    for (let i = i0; i <= i1; i++) {
      s += (specLin[i] || 0);
    }
    out[b.key] = s;
  }

  return out;
}

function emaBands(type, bands, alpha = 0.15){
  const st = bandEma[type];
  for (const b of BANDS) {
    const k = b.key;
    st[k] = (Number(st[k]) || 0) + alpha * ((Number(bands[k]) || 0) - (Number(st[k]) || 0));
  }
  return st;
}

function sumBands(obj){
  let s = 0;
  for (const b of BANDS) {
    const v = Number(obj?.[b.key]) || 0;
    if (v > 0) s += v;
  }
  return s;
}

function normalizeBandMap(map){
  const total = Math.max(1e-9, sumBands(map));
  const out = {};

  for (const b of BANDS) {
    const k = b.key;
    out[k] = (Number(map?.[k]) || 0) / total;
  }

  return out;
}

const fluxBandEmaA = makeZeroBandMap();
const fluxBandEmaM = makeZeroBandMap();

function emaFluxBand(target, src, alpha = 0.25){
  for (const b of BANDS) {
    const k = b.key;
    target[k] = (Number(target[k]) || 0) + alpha * ((Number(src[k]) || 0) - (Number(target[k]) || 0));
  }
  return target;
}

function updateBandBars(){
  if (!latestBandA) return;

  const aNorm = normalizeBandMap(latestBandA.smooth);

  for (const b of BANDS) {
    const k = b.key;
    const aRatio = Math.max(0, Math.min(1, Number(aNorm[k]) || 0));

    const aEl = document.getElementById(`barA_${k}`);
    const aTx = document.getElementById(`txtA_${k}`);

    if (aEl) aEl.style.width = `${(aRatio * 100).toFixed(1)}%`;
    if (aTx) aTx.textContent = `${(aRatio * 100).toFixed(1)}%`;
  }
}

// function updateBandBars(){

//   if (!latestBandA || !latestBandM) return;

//   const aNorm = normalizeBandMap(latestBandA.smooth);
//   const mNorm = normalizeBandMap(latestBandM.smooth);

//   for (const b of BANDS) {
//     const k = b.key;

//     const aRatio = Math.max(0, Math.min(1, Number(aNorm[k]) || 0));
//     const mRatio = Math.max(0, Math.min(1, Number(mNorm[k]) || 0));

//     const aEl = document.getElementById(`barA_${k}`);
//     const mEl = document.getElementById(`barM_${k}`);
//     const aTx = document.getElementById(`txtA_${k}`);
//     const mTx = document.getElementById(`txtM_${k}`);

//     if (aEl) aEl.style.width = `${(aRatio * 100).toFixed(1)}%`;
//     if (mEl) mEl.style.width = `${(mRatio * 100).toFixed(1)}%`;
//     if (aTx) aTx.textContent = `${(aRatio * 100).toFixed(1)}%`;
//     if (mTx) mTx.textContent = `${(mRatio * 100).toFixed(1)}%`;
//   }
// }


function updateNowBandFluxBars(){
  if (!lastFluxBandsA || !lastFluxBandsM) return;

  let vmax = 1e-9;
  for (const b of BANDS) {
    vmax = Math.max(vmax, Number(lastFluxBandsA[b.key]) || 0);
    vmax = Math.max(vmax, Number(lastFluxBandsM[b.key]) || 0);
  }

  for (const b of BANDS) {
    const k = b.key;

    const aVal = Number(lastFluxBandsA[k]) || 0;
    const mVal = Number(lastFluxBandsM[k]) || 0;

    const aRatio = Math.max(0, Math.min(1, aVal / vmax));
    const mRatio = Math.max(0, Math.min(1, mVal / vmax));

    const aEl = document.getElementById(`barA_${k}`);
    const mEl = document.getElementById(`barM_${k}`);
    const aTx = document.getElementById(`txtA_${k}`);
    const mTx = document.getElementById(`txtM_${k}`);

    if (aEl) aEl.style.width = `${(aRatio * 100).toFixed(1)}%`;
    if (mEl) mEl.style.width = `${(mRatio * 100).toFixed(1)}%`;

    if (aTx) aTx.textContent = aVal.toFixed(3);
    if (mTx) aTx ? null : null;
    if (mTx) mTx.textContent = mVal.toFixed(3);
  }
}


function updateBandFluxBars(){
  if (!lastFluxBandsA || !lastFluxBandsM) return;

  // A/Bの両方の最大値を基準にして比較しやすくする
  let vmax = 1e-9;
  for (const b of BANDS) {
    vmax = Math.max(vmax, Number(lastFluxBandsA[b.key]) || 0);
    vmax = Math.max(vmax, Number(lastFluxBandsM[b.key]) || 0);
  }

  for (const b of BANDS) {
    const k = b.key;

    const aRatio = Math.max(0, Math.min(1, (Number(lastFluxBandsA[k]) || 0) / vmax));
    const mRatio = Math.max(0, Math.min(1, (Number(lastFluxBandsM[k]) || 0) / vmax));

    const aEl = document.getElementById(`barA_${k}`);
    const mEl = document.getElementById(`barM_${k}`);
    const aTx = document.getElementById(`txtA_${k}`);
    const mTx = document.getElementById(`txtM_${k}`);

    if (aEl) aEl.style.width = `${(aRatio * 100).toFixed(1)}%`;
    if (mEl) mEl.style.width = `${(mRatio * 100).toFixed(1)}%`;

    // 数値そのものを見たいので % ではなく生値表示
    if (aTx) aTx.textContent = (Number(lastFluxBandsA[k]) || 0).toFixed(3);
    if (mTx) mTx.textContent = (Number(lastFluxBandsM[k]) || 0).toFixed(3);
  }
}

// === RECORD (10s avg) ===
const REC_SEC = 10;

let isRec = false;
let recStartMs = 0;

// accumulate ratios (normalized) over time
let recSum = {
  A: makeZeroBandMap(),
  M: makeZeroBandMap(),
};
let recCount = 0;

let recFluxHist = {
  A: [],
  M: [],
};

function resetRec(){
  recSum = {
    A: makeZeroBandMap(),
    M: makeZeroBandMap(),
  };
  recCount = 0;

  recFluxHist = {
    A: [],
    M: [],
  };
}


window.addEventListener('DOMContentLoaded', () => {
  touchTableEl = document.getElementById('touchTable');
  diffAccelEl = document.getElementById('diffAccel');
  diffMicEl   = document.getElementById('diffMic');

  scoreA_accelEl = document.getElementById('scoreA_accel');
  scoreA_micEl   = document.getElementById('scoreA_mic');
  scoreA_totalEl = document.getElementById('scoreA_total');

  scoreB_accelEl = document.getElementById('scoreB_accel');
  scoreB_micEl   = document.getElementById('scoreB_mic');
  scoreB_totalEl = document.getElementById('scoreB_total');

  scoreWinnerEl  = document.getElementById('scoreWinner');
  scoreDeltaEl   = document.getElementById('scoreDelta');

  fishA_valEl = document.getElementById('fishA_val');
  fishB_valEl = document.getElementById('fishB_val');
  fishA_barEl = document.getElementById('fishA_bar');
  fishB_barEl = document.getElementById('fishB_bar');
  fishWinnerEl = document.getElementById('fishWinner');
  fishDeltaEl  = document.getElementById('fishDelta');

});



let recAvgA = null; // { accel: {key:ratio...}, mic:{key:ratio...} }
let recAvgB = null;

let diffAccelEl, diffMicEl;


let scoreA_accelEl, scoreA_micEl, scoreA_totalEl;
let scoreB_accelEl, scoreB_micEl, scoreB_totalEl;
let scoreWinnerEl, scoreDeltaEl;

// ===== Attack detector =====
let prevSpecA = null;
let prevSpecM = null;

let lastFluxA = 0;
let lastFluxM = 0;
let lastFluxBandsA = null;
let lastFluxBandsM = null;

let lastAttackScore = 0;
let lastAttackState = 'IDLE'; // IDLE / CANDIDATE / HIT / COOLDOWN
let lastAttackReason = '';


const detector = {
  state: 'IDLE',
  candidate: null,
  cooldownUntil: 0,
};

const DET = {
  fluxA_on: 0.18,
  fluxM_on: 0.18,
  scoreHit: 0.62,
  candidateMaxSec: 0.70,
  longPenaltySec: 1.20,
  cooldownSec: 0.60,
};

let prevPeakAForClass = null;
let prevPeakMForClass = null;
let lastPeakMoveA = 0;
let lastPeakMoveM = 0;



let fishA_valEl, fishB_valEl, fishA_barEl, fishB_barEl, fishWinnerEl, fishDeltaEl;


window.addEventListener('error', (e)=>{
  //showWarn('JS Error: ' + (e.message || e.type));
});

let viewMinHz = 10;
let viewMaxHz = 600;

document.getElementById('apply').onclick = () => {
  viewMinHz = Number(document.getElementById('fmin').value);
  viewMaxHz = Number(document.getElementById('fmax').value);

  if (!isFinite(viewMinHz)) viewMinHz = 10;
  if (!isFinite(viewMaxHz)) viewMaxHz = 600;
  if (viewMaxHz <= viewMinHz) viewMaxHz = viewMinHz + 1;

  // 帯域変更時はピークトラックを捨てる
  trackA = [];
  trackM = [];

  // ついでに直近ピーク移動の基準もリセットしておくと自然
  prevPeakAForClass = null;
  prevPeakMForClass = null;

  // 表示中データがあれば即再描画
  const list = [];
  if (latestA) list.push(latestA);
  if (latestM) list.push(latestM);
  drawSpectra(list);
};


const recBtn = document.getElementById('recBtn');
if(recBtn){
  recBtn.addEventListener('click', ()=>{
    if(isRec) stopRec();
    else startRec();
  });
}

document.getElementById('timeWindow')?.addEventListener('change', () => {
  drawTimeLog();
});

document.getElementById("saveLogBtn")
  ?.addEventListener("click", saveSessionToFile);

document.getElementById("loadLogBtn")
  ?.addEventListener("click", () => {

    document.getElementById("loadLogFile").click();

  });

document.getElementById("loadLogFile")
  ?.addEventListener("change", (e) => {

    const file = e.target.files[0];

    if (file) openSessionFile(file);

    e.target.value = "";

  });


  document.getElementById('resumeLiveBtn')
  ?.addEventListener('click', resumeLiveMode);
  

// ===== WebSocket =====
let lastT = performance.now();
let counter = 0;

function wsUrl(){ return `ws://${location.host}/ws`; }
const ws = new WebSocket(wsUrl());

ws.onopen  = ()=>{ st.textContent='connected'; };
ws.onclose = (e)=>{ st.textContent=`closed (${e.code})`; };
ws.onerror = ()=>{ st.textContent='error'; showWarn('WebSocket error (cannot connect)'); };

ws.onmessage = (e) => {

  if (isLoadedSessionMode) {
    return;
  }
  
  const msg = String(e.data || '');

  const [meta, payload] = msg.split('|');
  if (!payload) return;

  const parts = meta.split(',');
  if (parts.length < 5) return;

  const type = parts[0];
  const fs = Number(parts[2]);
  const n  = Number(parts[3]);
  const maxHz = Number(parts[4]);

  //console.log('WS type =', type, 'payload =', payload);
  

  // ===== TOUCH EVENT =====
  if (type === 'T') {
    console.log('T event accepted');
    console.log('touchShots length =', touchShots.length + 1);

    // 互換:
    // 旧: "1"
    // 新: "1,2,0" → value,count,long
    const tp = payload.split(',');
    const v = Number(tp[0] || 0);              // 1 or 0
    const count = Number(tp[1] || 1) || 1;    // tap count
    const long  = Number(tp[2] || 0) === 1;   // long press flag

    //console.log('TOUCH parsed =', { v, count, long });

    const nowT = (tsBuf && tsBuf.length)
      ? tsBuf[tsBuf.length - 1].t
      : (performance.now() * 0.001);
      
      if (v === 1) {
      if ((nowT - lastTouchAcceptT) < TOUCH_DEBOUNCE_SEC) {
        return;
      }
      lastTouchAcceptT = nowT;

      // 従来の縦線用
      touchBuf.push({
        t: nowT,
        v: 1,
        count,
        long,
        kind: long ? 'long' : 'tap'
      });

      // スナップショット保存
      const pre = nearestSampleAt(nowT - SNAP_DT);
      const cur = {
        scrape: Number(lastScrape) || 0,
        peakA: Number(lastPeakAHz) || 0,
        peakM: Number(lastPeakMHz) || 0
      };

      const clsInfo = classifyContact({
        scrape: cur.scrape,
        peakAHz: cur.peakA,
        peakMHz: cur.peakM,
        fluxA: Number(lastFluxA) || 0,
        fluxM: Number(lastFluxM) || 0,
        peakMoveA: Number(lastPeakMoveA) || 0,
        peakMoveM: Number(lastPeakMoveM) || 0,
        attackScore: Number(lastAttackScore) || 0,
        attackState: lastAttackState || 'IDLE',
        attackReason: lastAttackReason || '',

      });

      const shot = {
        id: shotSeq++,
        t: nowT,

        count,
        long,
        kind: long ? 'long' : 'tap',

        scrape: cur.scrape,
        peakA: cur.peakA,
        peakM: cur.peakM,

        preT: nowT - SNAP_DT,
        preScrape: pre ? (Number(pre.scrape) || 0) : null,
        prePeakA: pre ? (Number(pre.peakAHz ?? pre.peakA) || 0) : null,
        prePeakM: pre ? (Number(pre.peakMHz ?? pre.peakM) || 0) : null,

        postT: nowT + SNAP_DT,
        postScrape: null,
        postPeakA: null,
        postPeakM: null,

        freezeReadyAt: nowT + getFreezeWindowSec() / 2,
        frozenSeries: null,

        fluxA: Number(lastFluxA) || 0,
        fluxM: Number(lastFluxM) || 0,
        
        peakMoveA: Number(lastPeakMoveA) || 0,
        peakMoveM: Number(lastPeakMoveM) || 0,

        decayA: 0,
        decayM: 0,
        energyA: 0,
        energyM: 0,

        attackScore: Number(lastAttackScore) || 0,
        attackState: lastAttackState || 'IDLE',
        attackReason: lastAttackReason || '',
        contactClass: clsInfo.cls,
        classReason: clsInfo.reason,
        
        impulseScore: 0,
        suctionScore: 0,
        weedScore: 0,

        preMeanFlux: 0,
        hitMeanFlux: 0,
        postShortMeanFlux: 0,
        postLongMeanFlux: 0,
        postFluxVar: 0,
        postMicroPeakCount: 0,
        scrapeRecoveryTime: 0,
        eventClass: '',

      };
      touchShots.push(shot);
      enrichShotScores(shot, tsBuf);

      console.log('after push length =', touchShots.length);
      console.log('last shot =', touchShots[touchShots.length - 1]);

      // 最大件数だけ制限（1回だけ）
      if (touchShots.length > MAX_SHOTS) {
        touchShots.shift();
      }

      if (selectedShotId == null) {
        followLatestTimeLog();
      }

      pruneTouch(nowT);
      renderTouchTable();
      drawTimeSeries();
      drawFluxTimeSeries();
      drawPeakTimeline();
      drawStateTimeline();
      drawTimeLog();

    }

    return;
  }

  if (!isFinite(fs) || !isFinite(n) || !isFinite(maxHz) || n <= 0) return;

  let color = (type === 'M') ? '#ff6f00' : '#1e88e5';

  const df = fs / n;
  const maxBin = Math.floor(maxHz / df);

  const arr = payload.split(',').map(Number);
  if (arr.length < (maxBin + 1)) return;

  const spec = emaUpdate(arr, type);

  // --- spectral flux ---
  const fluxMinBin = Math.max(0, Math.floor(10 / df));
  const fluxMaxBin = Math.min(maxBin, Math.floor(Math.min(viewMaxHz, maxHz) / df));

if(type === 'A'){
  lastFluxA = calcSpectralFlux(spec, prevSpecA, fluxMinBin, fluxMaxBin);
  lastFluxBandsA = calcBandFlux(spec, prevSpecA, df, Math.min(viewMaxHz, maxHz));
  emaFluxBand(fluxBandEmaA, lastFluxBandsA, 0.25);
  prevSpecA = spec.slice();
}
if(type === 'M'){
  lastFluxM = calcSpectralFlux(spec, prevSpecM, fluxMinBin, fluxMaxBin);
  lastFluxBandsM = calcBandFlux(spec, prevSpecM, df, Math.min(viewMaxHz, maxHz));
  emaFluxBand(fluxBandEmaM, lastFluxBandsM, 0.25);
  prevSpecM = spec.slice();
}


  // --- band sums (use linear spec) ---
  const bandSums = calcBandSums(spec, df, maxHz);
  const bandsSmooth = emaBands(type, bandSums, 0.15);

  const bandItem = {
    raw: bandSums,
    smooth: { ...bandsSmooth },
  };

  if (type === 'A') latestBandA = bandItem;
  if (type === 'M') latestBandM = bandItem;

  const minBin = Math.max(0, Math.floor(viewMinHz / df));
  const maxBinView = Math.min(maxBin, Math.floor(viewMaxHz / df));
  if (maxBinView <= minBin) return;

  const magsLin = spec.slice(minBin, maxBinView + 1);
  const freqs = magsLin.map((_, i) => (minBin + i) * df);

  let mags = magsLin;
  let maxV = 1;
  for (const v of magsLin) if (v > maxV) maxV = v;

  if (isDb()) mags = toDbArray(magsLin, maxV);

    // peak (from linear spec)
  const startHz = 10;
  const startBin = Math.max(minBin, Math.ceil(startHz / df));

  let pBin = startBin, pVal = -1;
  for (let i = startBin; i <= maxBinView; i++) {
    const v = spec[i];
    if (v > pVal) {
      pVal = v;
      pBin = i;
    }
  }

  const peakHz = (pBin * df);
  const topPeaks = findTopPeaks(spec, df, startBin, maxBinView, 3);

  if (type === 'A') {
    lastPeakAHz = peakHz;
    lastPeakMoveA = (prevPeakAForClass == null) ? 0 : Math.abs(peakHz - prevPeakAForClass);
    prevPeakAForClass = peakHz;
  }

  if (type === 'M') {
    lastPeakMHz = peakHz;
    lastPeakMoveM = (prevPeakMForClass == null) ? 0 : Math.abs(peakHz - prevPeakMForClass);
    prevPeakMForClass = peakHz;
  }

  updatePeakTable(type, topPeaks);

  const item = { freqs, mags, color, type, maxV, topPeaks };
  if (type === 'A') latestA = item;
  if (type === 'M') latestM = item;

  if(type==='A'){
    trackA = trackPeaks(topPeaks,trackA);
    item.topPeaks = trackA;
  }

  if(type==='M'){
    trackM = trackPeaks(topPeaks,trackM);
    item.topPeaks = trackM;
  }


  // draw main FFT
  const list = [];
  if (latestA) list.push(latestA);
  if (latestM) list.push(latestM);
  drawSpectra(list);

  // spectrogram
  if (latestA) pushSpectrogramColumn(gA, ensureDb(latestA));
  if (latestM) pushSpectrogramColumn(gM, ensureDb(latestM));

  // scrape + time series
  if (latestA && latestM) {
    const lvl = calcScrapeLevel(ensureDb(latestA), ensureDb(latestM));
    updateScrapeMeter(lvl);
    lastScrape = lvl;

    const nowT = performance.now() * 0.001;

    const feat = {
      t: nowT,
      scrape: scrSmooth,
      peakAHz: lastPeakAHz,
      peakMHz: lastPeakMHz,
      fluxA: lastFluxA,
      fluxM: lastFluxM,
      peakMoveA: lastPeakMoveA,
      peakMoveM: lastPeakMoveM,
      attackScore: 0,
      attackState: 'IDLE',
      contactClass: 'NONE',
      classReason: '',

      topPeaksA: (latestA?.topPeaks || []).map(p => ({
        hz: Number(p.hz) || 0,
        mag: Number(p.mag) || 0
      })),
      topPeaksM: (latestM?.topPeaks || []).map(p => ({
        hz: Number(p.hz) || 0,
        mag: Number(p.mag) || 0
      })),
      density: calcPeakDensity(
        latestA?.topPeaks,
        latestM?.topPeaks
       ),

    };

    const hit = updateAttackDetector(feat);
    feat.attackScore = lastAttackScore;
    feat.attackState = lastAttackState;

    const clsInfo = classifyContact(feat);
    feat.contactClass = clsInfo.cls;
    feat.classReason = clsInfo.reason;

    feat.phase2State = classifyPhase2State(feat);

    if (feat.phase2State !== lastPhase2State) {
      pushStateTransition(nowT, lastPhase2State, feat.phase2State);
      lastPhase2State = feat.phase2State;
    }

    tsBuf.push(feat);



    updateNoiseFloor(feat);


    fillPendingPost(nowT);

    pruneTimeSeries(nowT);
    drawTimeSeries();
    drawFluxTimeSeries();
    drawPeakTimeline();
    drawStateTimeline();
    drawTimeLog();
    //updateNowBandFluxBars();
    updateBandBars();
    updateBandFluxBars();
    updateRecIfNeeded();
    finalizeFrozenSeries(nowT);

function drawPeakTimeline(){
  if (!tsPeakCanvas || !gTP) return;

  const W = tsPeakCanvas.width;
  const H = tsPeakCanvas.height;
  gTP.clearRect(0, 0, W, H);

  const selectedFrozen = getSelectedFrozenSeries();
  const seriesSrc = (!timeLogFollowLatest && selectedFrozen)
    ? selectedFrozen
    : tsBuf;

  const ml = 58, mr = 58, mt = 18, mb = 24;
  const pw = W - ml - mr;
  const ph = H - mt - mb;

  const chartLeft   = ml;
  const chartRight  = ml + pw;
  const chartTop    = mt;
  const chartBottom = mt + ph;

  gTP.fillStyle = '#fcfcfc';
  gTP.fillRect(0, 0, W, H);

  gTP.strokeStyle = '#d4d4d4';
  gTP.lineWidth = 1;
  gTP.beginPath();
  gTP.moveTo(chartLeft, chartTop);
  gTP.lineTo(chartLeft, chartBottom);
  gTP.lineTo(chartRight, chartBottom);
  gTP.stroke();

  if (!seriesSrc || seriesSrc.length < 2) {
    gTP.fillStyle = '#999';
    gTP.font = '12px sans-serif';
    gTP.fillText('no peak timeline yet', chartLeft + 10, chartTop + 18);
    return;
  }

  const nowSec = seriesSrc[seriesSrc.length - 1].t;
  const winSec = getTimeWindowSec();

  let viewStart = 0;
  let viewEnd = winSec;

  if (!timeLogFollowLatest && isFinite(timeLogCenterSec)) {
    viewStart = Math.max(0, timeLogCenterSec - winSec / 2);
    viewEnd = viewStart + winSec;

    if (viewEnd > nowSec && nowSec > winSec) {
      viewEnd = nowSec;
      viewStart = Math.max(0, viewEnd - winSec);
    }
  } else {
    viewStart = Math.max(0, nowSec - winSec);
    viewEnd = Math.max(winSec, nowSec);
  }

  const hzMin = Math.max(0, viewMinHz || 0);
  const hzMax = Math.max(hzMin + 1, viewMaxHz || 600);

  function xMap(t){
    return chartLeft + ((t - viewStart) / Math.max(1e-9, (viewEnd - viewStart))) * pw;
  }

  function yMapHz(hz){
    const v = Math.max(hzMin, Math.min(hzMax, Number(hz) || 0));
    return chartBottom - ((v - hzMin) / Math.max(1e-9, (hzMax - hzMin))) * ph;
  }

  // horizontal grid
  gTP.strokeStyle = '#ececec';
  gTP.lineWidth = 1;
  for(let i = 0; i <= 4; i++){
    const y = chartTop + ph * i / 4;
    gTP.beginPath();
    gTP.moveTo(chartLeft, y);
    gTP.lineTo(chartRight, y);
    gTP.stroke();

    const hzVal = hzMax - ((hzMax - hzMin) * i / 4);
    gTP.fillStyle = '#666';
    gTP.font = '11px sans-serif';
    gTP.textAlign = 'right';
    gTP.textBaseline = 'middle';
    gTP.fillText(`${Math.round(hzVal)}`, chartLeft - 8, y);
  }

  // dots only
  const visible = seriesSrc.filter(p => p.t >= viewStart && p.t <= viewEnd);

  const rankRadius = [4.0, 3.0, 2.2, 1.8, 1.4];
  const rankAlphaA = [0.90, 0.72, 0.56, 0.42, 0.32];
  const rankAlphaM = [0.90, 0.72, 0.56, 0.42, 0.32];

  for (const p of visible) {
    const x = xMap(p.t);

    const peaksA = Array.isArray(p.topPeaksA) ? p.topPeaksA : [];
    const peaksM = Array.isArray(p.topPeaksM) ? p.topPeaksM : [];

    peaksA.slice(0, 5).forEach((pk, i) => {
      const hz = Number(pk?.hz) || 0;
      if (hz < hzMin || hz > hzMax) return;

      const y = yMapHz(hz);
      gTP.save();
      gTP.fillStyle = `rgba(30,136,229,${rankAlphaA[i] ?? 0.28})`;
      gTP.beginPath();
      gTP.arc(x, y, rankRadius[i] ?? 1.4, 0, Math.PI * 2);
      gTP.fill();
      gTP.restore();
    });

    peaksM.slice(0, 5).forEach((pk, i) => {
      const hz = Number(pk?.hz) || 0;
      if (hz < hzMin || hz > hzMax) return;

      const y = yMapHz(hz);
      gTP.save();
      gTP.fillStyle = `rgba(255,111,0,${rankAlphaM[i] ?? 0.28})`;
      gTP.beginPath();
      gTP.arc(x, y, rankRadius[i] ?? 1.4, 0, Math.PI * 2);
      gTP.fill();
      gTP.restore();
    });
  }

  // touch marker
  for (const s of touchShots) {
    if (s.t < viewStart || s.t > viewEnd) continue;
    const x = xMap(s.t);
    drawTouchMarker(gTP, x, chartTop, chartBottom, s);
  }

  // legend
  gTP.font = '11px sans-serif';
  gTP.textBaseline = 'alphabetic';
  gTP.textAlign = 'left';

  gTP.fillStyle = '#1e88e5';
  gTP.fillText('A peak dots', chartLeft + 8, chartTop - 4);

  gTP.fillStyle = '#ff6f00';
  gTP.fillText('M peak dots', chartLeft + 92, chartTop - 4);

  gTP.fillStyle = '#777';
  gTP.fillText('size = peak rank', chartLeft + 182, chartTop - 4);

  gTP.fillStyle = '#777';
  gTP.fillText('Peak Timeline', chartLeft, H - 6);
}

    if(hit){
      //console.log('ATTACK HIT', hit);
      mark(gA);
      mark(gM);
    }

    const thr = Number(thrEl.value);
    if (scrSmooth >= thr) {
      mark(gA);
      mark(gM);
    }
  }


  // FPS
  counter++;
  const now = performance.now();
  if (now - lastT > 1000) {
    fpsEl.textContent = counter.toString();
    counter = 0;
    lastT = now;
  }
};


function getAlpha(){
  const a = Number(document.getElementById('alpha').value);
  if(!isFinite(a)) return 0.25;
  return Math.min(1, Math.max(0.01, a));
}
function isDb(){
  return (document.getElementById('db')?.checked ?? true);
}

thrTxt.textContent = Number(thrEl.value).toFixed(1);
thrEl.addEventListener('input', ()=>{ thrTxt.textContent = Number(thrEl.value).toFixed(1); });

// high‑DPI support
function fitCanvasEl(el){
  const dpr = window.devicePixelRatio || 1;
  const rect = el.getBoundingClientRect();
  el.width  = Math.max(300, Math.floor(rect.width  * dpr));
  el.height = Math.max(180,  Math.floor(rect.height * dpr));
}

function fitAll(){
  fitCanvasEl(canvas);
  fitCanvasEl(specA);
  fitCanvasEl(specM);
  fitCanvasEl(tsCanvas);
  fitCanvasEl(tsFluxCanvas);
  fitCanvasEl(tsPeakCanvas);
  fitCanvasEl(tsStateCanvas);
  
  gA.clearRect(0,0,specA.width,specA.height);
  gM.clearRect(0,0,specM.width,specM.height);
  gT.clearRect(0,0,tsCanvas.width,tsCanvas.height);
  gTF.clearRect(0,0,tsFluxCanvas.width,tsFluxCanvas.height);
  gTP.clearRect(0,0,tsPeakCanvas.width,tsPeakCanvas.height);
  gTS.clearRect(0,0,tsStateCanvas.width,tsStateCanvas.height);
}

window.addEventListener('resize', fitAll);
fitAll();

// ===== Spectrogram =====
// map dB values to grayscale color: 0dB = white, -80dB = black (contrast)
function dbToGray(db){
  const top = 0, bot = -80;
  const t = Math.max(0, Math.min(1, (db - bot) / (top - bot))); // 0..1
  return Math.floor(255 * t);
}

// scroll spectrogram by advancing 1px and drawing latest column at right edge
function pushSpectrogramColumn(ctx, magsDb){
  const W = ctx.canvas.width, H = ctx.canvas.height;

  // shift canvas 1px to the left
  ctx.drawImage(ctx.canvas, -1, 0);

  // draw 1px column at right edge
  const x = W - 1;
  const N = magsDb.length;
  if(N < 2) return;

  for(let i=0;i<N;i++){
    const y = H - 1 - Math.floor((H-1) * i / (N-1));
    const gray = dbToGray(magsDb[i]);
    ctx.fillStyle = 'rgb(' + gray + ',' + gray + ',' + gray + ')';
    ctx.fillRect(x, y, 1, 1);
  }
}

function mark(ctx){
  ctx.fillStyle = 'rgba(255,0,0,0.7)';
  ctx.fillRect(ctx.canvas.width-1, 0, 1, ctx.canvas.height);
}

// ===== EMA (exponential moving average) =====
let smoothA = [];
let smoothM = [];
function emaUpdate(arr, type){
  let smooth = (type === 'M') ? smoothM : smoothA;
  if(smooth.length !== arr.length) smooth = arr.slice();
  const a = getAlpha();
  for(let i=0;i<arr.length;i++){
    const v = arr[i];
    if(!isFinite(v)) continue;
    smooth[i] = smooth[i] + a * (v - smooth[i]);
  }
  if(type === 'M') smoothM = smooth; else smoothA = smooth;
  return smooth;
}

// convert to dB (with safeguards for zero‑division/logarithm issues)
function toDbArray(mags, ref){
  const eps = 1e-9;
  const r = Math.max(eps, ref || 1);
  return mags.map(v => 20 * Math.log10(Math.max(eps, v) / r));
}

// even when dB display is off, the spectrogram itself uses dB values
function ensureDb(item){
  if(!item) return null;
  if(isDb()) return item.mags; // already in dB when the dB display is enabled
  let maxV = 1;
  for(const v of item.mags) if(v > maxV) maxV = v;
  return toDbArray(item.mags, maxV);
}

function findTopPeaks(spec, df, minBin, maxBin, topN = 3) {
  const peaks = [];
  const guard = 1; // 両隣比較

  const i0 = Math.max(minBin + guard, guard);
  const i1 = Math.min(maxBin - guard, spec.length - 1 - guard);

  for (let i = i0; i <= i1; i++) {
    const c = Number(spec[i]) || 0;
    const l = Number(spec[i - 1]) || 0;
    const r = Number(spec[i + 1]) || 0;

    // 局所ピーク
    if (c >= l && c >= r) {
      peaks.push({
        bin: i,
        hz: i * df,
        mag: c
      });
    }
  }

  // 局所ピークが少なすぎる時の保険
  if (peaks.length === 0) {
    for (let i = minBin; i <= maxBin; i++) {
      peaks.push({
        bin: i,
        hz: i * df,
        mag: Number(spec[i]) || 0
      });
    }
  }

  peaks.sort((a, b) => b.mag - a.mag);

  // 近すぎるピークは同一扱いにして間引く
  const selected = [];
  const minSepHz = Math.max(8, df * 2);

  for (const p of peaks) {
    const tooClose = selected.some(s => Math.abs(s.hz - p.hz) < minSepHz);
    if (!tooClose) selected.push(p);
    if (selected.length >= topN) break;
  }

  return selected;
}
function trackPeaks(peaks, tracks){

  const MAX_TRACK = 3;
  const MATCH_HZ  = 20;    // 同一ピークとみなす距離
  const MERGE_HZ  = 10;    // 最後に統合する距離
  const ALPHA     = 0.35;  // 平滑係数
  const HOLD_FRAMES = 6;   // 一瞬消えても少し残す

  // 既存trackをコピー
  const pool = (tracks || []).map(t => ({
    hz: t.hz,
    mag: t.mag,
    age: (t.age || 0) + 1,
    hit: false
  }));

  // 近いtrackへ1対1で割り当て
  for(const p of peaks){
    let bestIdx = -1;
    let bestDist = 1e9;

    for(let i=0; i<pool.length; i++){
      const t = pool[i];
      if(t.hit) continue; // すでに他ピークを割当済み
      const d = Math.abs(t.hz - p.hz);
      if(d < MATCH_HZ && d < bestDist){
        bestDist = d;
        bestIdx = i;
      }
    }

    if(bestIdx >= 0){
      const t = pool[bestIdx];
      t.hz = t.hz * (1 - ALPHA) + p.hz * ALPHA;
      t.mag = p.mag;
      t.age = 0;
      t.hit = true;
    }else{
      pool.push({
        hz: p.hz,
        mag: p.mag,
        age: 0,
        hit: true
      });
    }
  }

  // 古すぎるtrackを捨てる
  let next = pool.filter(t => t.age <= HOLD_FRAMES);

  // 強い順に並べる
  next.sort((a,b) => b.mag - a.mag);

  // 近すぎるtrackを統合
  const merged = [];
  for(const t of next){
    const near = merged.find(m => Math.abs(m.hz - t.hz) < MERGE_HZ);
    if(near){
      // 強い方を優先しつつ少し平均
      if(t.mag > near.mag){
        near.hz = t.hz;
        near.mag = t.mag;
        near.age = Math.min(near.age, t.age);
      }else{
        near.hz = (near.hz + t.hz) / 2;
      }
    }else{
      merged.push({...t});
    }
  }

  merged.sort((a,b) => b.mag - a.mag);

  return merged.slice(0, MAX_TRACK);
}




function updatePeakTable(type, peaks){

  if(!peaks) return;

  const fmt = p => p ? p.hz.toFixed(1)+"Hz" : "-";

  if(type==='A'){
    a1.textContent = fmt(peaks[0]);
    a2.textContent = fmt(peaks[1]);
    a3.textContent = fmt(peaks[2]);
  }

  if(type==='M'){
    m1.textContent = fmt(peaks[0]);
    m2.textContent = fmt(peaks[1]);
    m3.textContent = fmt(peaks[2]);
  }

}


function drawSpectra(seriesList){
  if (!seriesList || seriesList.length === 0) return;

  const useDb = isDb();

  const sA = seriesList.find(s => s && s.type === 'A') || null;
  const sM = seriesList.find(s => s && s.type === 'M') || null;
  const base = sA || sM;
  if (!base) return;

  const freqs0 = base.freqs;
  if (!freqs0 || freqs0.length < 2) return;

  const W = canvas.width, H = canvas.height;
  g.clearRect(0, 0, W, H);

  const ml = 60, mr = 60, mt = 16, mb = 40;
  const pw = W - ml - mr, ph = H - mt - mb;

  g.strokeStyle = '#888';
  g.lineWidth = 1;
  g.beginPath();
  g.moveTo(ml, mt);
  g.lineTo(ml, mt + ph);
  g.lineTo(ml + pw, mt + ph);
  g.stroke();

  g.font = `${Math.floor(12 * (window.devicePixelRatio || 1))}px sans-serif`;

  let yMin = -60, yMax = 0;
  if (useDb) {
    yMin = -60;
    yMax = 0;
  } else {
    if (sA && !isFinite(sA.maxV)) {
      let m = 1;
      for (const v of sA.mags) if (v > m) m = v;
      sA.maxV = m;
    }
    if (sM && !isFinite(sM.maxV)) {
      let m = 1;
      for (const v of sM.mags) if (v > m) m = v;
      sM.maxV = m;
    }
  }

  const ticks = 4;
  for (let t = 0; t <= ticks; t++) {
    const y = mt + ph - (ph * t / ticks);

    g.strokeStyle = '#eee';
    g.beginPath();
    g.moveTo(ml, y);
    g.lineTo(ml + pw, y);
    g.stroke();

    if (useDb) {
      const val = yMin + (yMax - yMin) * (t / ticks);
      g.fillStyle = '#666';
      g.fillText(val.toFixed(0) + ' dB', 4, y + 4);
    } else {
      if (sA) {
        g.fillStyle = '#1e88e5';
        const valA = (sA.maxV || 1) * (t / ticks);
        g.fillText(valA.toFixed(0), 4, y + 4);
      }
      if (sM) {
        g.fillStyle = '#ff6f00';
        const valM = (sM.maxV || 1) * (t / ticks);
        const txt = valM.toFixed(0);
        const tw = g.measureText(txt).width;
        g.fillText(txt, ml + pw + mr - tw - 4, y + 4);
      }
    }
  }

  const f0 = freqs0[0];
  const f1 = freqs0[Math.floor(freqs0.length / 2)];
  const f2 = freqs0[freqs0.length - 1];

  g.fillStyle = '#666';
  g.fillText(f0.toFixed(1) + 'Hz', ml, mt + ph + 28);

  {
    const txt = f1.toFixed(1) + 'Hz';
    const tw = g.measureText(txt).width;
    g.fillText(txt, ml + pw / 2 - tw / 2, mt + ph + 28);
  }

  {
    const txt = f2.toFixed(1) + 'Hz';
    const tw = g.measureText(txt).width;
    g.fillText(txt, ml + pw - tw, mt + ph + 28);
  }

  function yMapDb(v){
    const t = (v - yMin) / (yMax - yMin);
    return mt + ph - (ph * t);
  }

  function yMapLinear(v, maxV){
    return mt + ph - (ph * (v / (maxV || 1)));
  }

  function drawLine(s){
    if (!s || !s.mags || s.mags.length < 2) return;

    g.strokeStyle = s.color || '#000';
    g.lineWidth = 2;
    g.beginPath();

    for (let i = 0; i < s.mags.length; i++) {
      const x = ml + (pw * i / (s.mags.length - 1));
      const y = useDb
        ? yMapDb(s.mags[i])
        : yMapLinear(s.mags[i], s.maxV || 1);

      if (i === 0) g.moveTo(x, y);
      else g.lineTo(x, y);
    }

    g.stroke();
  }

  function drawPeakMarkers(s){
    if (!s || !s.topPeaks || !s.topPeaks.length) return;

    const fMin = freqs0[0];
    const fMax = freqs0[freqs0.length - 1];
    if (!isFinite(fMin) || !isFinite(fMax) || fMax <= fMin) return;

    const levels = [];

    s.topPeaks.forEach((p) => {
      if (!isFinite(p.hz) || p.hz < fMin || p.hz > fMax) return;

      const rel = (p.hz - fMin) / (fMax - fMin);
      const x = ml + pw * rel;

      let y;
      if (useDb) {
        const vDb = 20 * Math.log10(Math.max(1e-9, p.mag) / (s.maxV || 1));
        y = yMapDb(vDb);
      } else {
        y = yMapLinear(p.mag, s.maxV || 1);
      }

      // ラベル衝突回避
      let level = 0;
      while (true) {
        let hit = false;

        for (const l of levels) {
          if (Math.abs(l.x - x) < 56 && l.level === level) {
            hit = true;
            break;
          }
        }

        if (!hit) break;
        level++;
      }

      levels.push({ x, level });

      const yShift = level * 16;
      const label = p.hz.toFixed(1) + 'Hz';

      g.fillStyle = s.color || '#000';
      g.beginPath();
      g.arc(x, y, 3.5, 0, Math.PI * 2);
      g.fill();

      const tw = g.measureText(label).width;
      const tx = Math.max(ml, Math.min(x - tw / 2, ml + pw - tw));
      const ty = Math.max(mt + 10, y - 8 - yShift);

      g.fillText(label, tx, ty);
    });
  }

  drawLine(sA);
  drawLine(sM);

  drawPeakMarkers(sA);
  drawPeakMarkers(sM);
}


// ===== FFT plot (the two lines above) =====
let latestA = null;
let latestM = null;

// ===== Scrape detection =====
function calcScrapeLevel(magsDbA, magsDbM){
  if(!magsDbA || !magsDbM) return 0;
  const N = Math.min(magsDbA.length, magsDbM.length);
  const skipBins = 6;

  function noiseFloor(arr){
    const a = arr.slice().sort((x,y)=>x-y);
    const idx = Math.floor(a.length * 0.2);
    return a[Math.max(0, idx)];
  }
  const floorA = noiseFloor(magsDbA);
  const floorM = noiseFloor(magsDbM);

  const scores = [];
  for(let i=skipBins;i<N;i++){
    const a = Math.max(0, (magsDbA[i] - floorA));
    const m = Math.max(0, (magsDbM[i] - floorM));
    scores.push(a * m);
  }
  if(scores.length === 0) return 0;

  scores.sort((x,y)=>y-x);
  const K = Math.min(12, scores.length);
  let sum = 0;
  for(let i=0;i<K;i++) sum += scores[i];
  const avgTop = sum / K;

  return Math.max(0, Math.min(100, avgTop / 8));
}

function calcSpectralFlux(curr, prev, i0 = 0, i1 = null){
  if(!curr || !prev) return 0;

  const end = Math.min(
    curr.length - 1,
    prev.length - 1,
    (i1 == null ? Math.min(curr.length, prev.length) - 1 : i1)
  );
  const start = Math.max(0, i0);

  if(end <= start) return 0;

  let sumPos = 0;
  let sumCur = 0;

  for(let i = start; i <= end; i++){
    const c = Math.max(0, Number(curr[i]) || 0);
    const p = Math.max(0, Number(prev[i]) || 0);
    const d = c - p;

    // 正方向だけ使うとイベント検出に向く
    if(d > 0) sumPos += d;
    sumCur += c;
  }

  if(sumCur <= 1e-9) return 0;
  return sumPos / sumCur; // だいたい 0〜1 付近
}

function clamp01(v){
  return Math.max(0, Math.min(1, v));
}

function scoreEventFeatures(f){
  const nBase = Math.max(Math.max(noiseFluxA, noiseFluxM), 0.01);

  const entryRise   = f.hitMeanFlux / Math.max(f.preMeanFlux, nBase);
  const shortDecay  = f.hitMeanFlux / Math.max(f.postShortMeanFlux, nBase);
  const longHold    = f.postLongMeanFlux / Math.max(f.preMeanFlux, nBase);
  const scrapeHold  = f.scrapePostLong / Math.max(f.scrapePre, 0.2);
  const recoveryBad = f.scrapeRecoveryTime / 1.2;
  const varNorm     = f.postFluxVar / Math.max(nBase * nBase, 1e-4);
  const microNorm   = f.postMicroPeakCount / 3.0;

  // 1) impulse: 立ち上がり急 + すぐ減衰
  const impulseScore = clamp01(
    0.45 * clamp01((entryRise  - 1.4) / 2.0) +
    0.35 * clamp01((shortDecay - 1.2) / 1.8) +
    0.20 * clamp01((f.hitMeanFlux / nBase - 1.5) / 3.0)
  );

  // 2) suction: 中程度の入口 + 少し状態変化が続く + 微小再変化あり
  const suctionScore = clamp01(
    0.30 * clamp01((entryRise - 1.1) / 1.8) +
    0.25 * clamp01((longHold  - 1.05) / 0.9) +
    0.25 * clamp01(varNorm / 2.5) +
    0.20 * clamp01(microNorm)
    - 0.20 * clamp01((scrapeHold - 1.8) / 1.8)
  );

  // 3) weed: 長持ち + scrape高止まり + 戻り遅い + 微小再変化少ない
  const weedScore = clamp01(
    0.30 * clamp01((longHold - 1.15) / 1.2) +
    0.30 * clamp01((scrapeHold - 1.2) / 1.8) +
    0.25 * clamp01(recoveryBad) +
    0.15 * (1.0 - clamp01(microNorm))
  );

  let eventClass = 'none';
  const mx = Math.max(impulseScore, suctionScore, weedScore);

  if (mx >= 0.35) {
    if (mx === weedScore) eventClass = 'weed';
    else if (mx === suctionScore) eventClass = 'suction';
    else eventClass = 'impulse';
  }

  return {
    impulseScore,
    suctionScore,
    weedScore,
    eventClass,
  };
}



function mean(arr){
  if (!arr || !arr.length) return 0;
  let s = 0;
  for (const v of arr) s += v;
  return s / arr.length;
}

function maxAbs(arr){
  if (!arr || !arr.length) return 0;
  let m = 0;
  for (const v of arr) {
    const a = Math.abs(Number(v) || 0);
    if (a > m) m = a;
  }
  return m;
}

function calcDecayIndex(values){
  if (!values || values.length < 6) return 0;

  const absVals = values.map(v => Math.abs(Number(v) || 0));
  const peak = maxAbs(absVals);
  if (peak <= 1e-9) return 0;

  const half = Math.floor(absVals.length / 2);
  const tail = absVals.slice(half);
  const tailAvg = mean(tail);

  return peak / (tailAvg + 1e-9);
}

function calcEnergyIndex(values){
  if (!values || !values.length) return 0;

  let e = 0;
  for (const v of values) {
    const x = Number(v) || 0;
    e += x * x;
  }
  return e;
}

/*
AttackScore =
  Fluxの強さ
+ Scrapeの立ち上がり
+ 短パルスらしさ
+ Decay（すっと減る）
+ Energy（十分な振動量）
- SustainPenalty（だらだら続く）
*/  


function calcAttackScoreFromFrames(frames){
  if (!frames || !frames.length) {
    return {
      score: 0,
      state: 'IDLE',
      reason: 'no frames'
    };
  }

  const dur = Math.max(0, frames[frames.length - 1].t - frames[0].t);

  let maxFluxA = 0;
  let maxFluxM = 0;
  let maxScrape = 0;

  let sumFluxA = 0;
  let sumFluxM = 0;
  let sumScrape = 0;

  const fluxAList = [];
  const fluxMList = [];
  const scrapeList = [];

  for (const f of frames) {
    const fa = Number(f.fluxA) || 0;
    const fm = Number(f.fluxM) || 0;
    const sc = Number(f.scrape) || 0;

    if (fa > maxFluxA) maxFluxA = fa;
    if (fm > maxFluxM) maxFluxM = fm;
    if (sc > maxScrape) maxScrape = sc;

    sumFluxA += fa;
    sumFluxM += fm;
    sumScrape += sc;

    fluxAList.push(fa);
    fluxMList.push(fm);
    scrapeList.push(sc);
  }

  const n = Math.max(1, frames.length);
  const avgFluxA = sumFluxA / n;
  const avgFluxM = sumFluxM / n;
  const avgScrape = sumScrape / n;

  const fluxA_norm  = clamp01(maxFluxA / 0.35);
  const fluxM_norm  = clamp01(maxFluxM / 0.35);
  const scrape_norm = clamp01(maxScrape / 12.0);
  const avgFlux_norm = clamp01((avgFluxA + avgFluxM) / 0.30);

  const shortPulseScore =
    dur <= 0.35 ? 1.00 :
    dur <= 0.70 ? 0.75 :
    dur <= 1.00 ? 0.45 : 0.15;

  const decayA = calcDecayIndex(fluxAList);
  const decayM = calcDecayIndex(fluxMList);
  const decayS = calcDecayIndex(scrapeList);

  const decayA_norm = clamp01((decayA - 1.2) / 4.0);
  const decayM_norm = clamp01((decayM - 1.2) / 4.0);
  const decayS_norm = clamp01((decayS - 1.2) / 4.0);

  const decayBonus =
      0.45 * decayA_norm
    + 0.35 * decayM_norm
    + 0.20 * decayS_norm;

  const energyA = calcEnergyIndex(fluxAList);
  const energyM = calcEnergyIndex(fluxMList);
  const energyS = calcEnergyIndex(scrapeList);

  const energyA_norm = clamp01(energyA / 0.20);
  const energyM_norm = clamp01(energyM / 0.20);
  const energyS_norm = clamp01(energyS / 300.0);

  const energyBonus =
      0.40 * energyA_norm
    + 0.30 * energyM_norm
    + 0.30 * energyS_norm;

  const sustainPenalty =
    dur <= 0.8 ? 0 :
    clamp01((dur - 0.8) / 0.8)
    * clamp01(avgScrape / 8.0)
    * (1 - avgFlux_norm);

  const weakDecayPenalty =
    dur <= 0.8 ? 0 :
    clamp01((dur - 0.8) / 1.0)
    * (1 - decayBonus)
    * clamp01(avgScrape / 8.0);

  const rawScore =
      0.24 * fluxA_norm
    + 0.18 * fluxM_norm
    + 0.10 * scrape_norm
    + 0.16 * shortPulseScore
    + 0.10 * avgFlux_norm
    + 0.14 * decayBonus
    + 0.08 * energyBonus
    - 0.18 * sustainPenalty
    - 0.12 * weakDecayPenalty;

  const score = clamp01(rawScore);

  let state = 'NO';
  if (score >= 0.75) state = 'FISH';
  else if (score >= 0.50) state = 'MAYBE';
  else if (score >= 0.30) state = 'WEAK';

  const reasons = [];

  if (fluxA_norm >= 0.55) reasons.push('fluxA strong');
  if (fluxM_norm >= 0.55) reasons.push('fluxM strong');
  if (scrape_norm >= 0.45) reasons.push('scrape rise');
  if (shortPulseScore >= 0.75) reasons.push('short pulse');
  if (decayBonus >= 0.45) reasons.push('decay strong');
  if (energyBonus >= 0.40) reasons.push('energy enough');

  if (sustainPenalty >= 0.18) reasons.push('sustain penalty');
  if (weakDecayPenalty >= 0.12) reasons.push('weak decay');

  if (!reasons.length) {
    if (dur > 1.0) reasons.push('long event');
    else reasons.push('small response');
  }

  return {
    score,
    state,
    reason: reasons.join(' / '),

    // デバッグ用に残しておく
    detail: {
      dur,
      fluxA_norm,
      fluxM_norm,
      scrape_norm,
      avgFlux_norm,
      shortPulseScore,
      decayA,
      decayM,
      decayS,
      decayBonus,
      energyA,
      energyM,
      energyS,
      energyBonus,
      sustainPenalty,
      weakDecayPenalty,
      rawScore
    }
  };
}

function updateAttackDetector(feat){
  const now = feat.t;

  if(detector.state === 'COOLDOWN'){
    if(now >= detector.cooldownUntil){
      detector.state = 'IDLE';
      detector.candidate = null;
    } else {
      lastAttackScore = 0;
      lastAttackState = 'NO';
      lastAttackReason = 'cooldown';
      return null;
    }
  }

  if(detector.state === 'IDLE'){
    if(feat.fluxA >= DET.fluxA_on || feat.fluxM >= DET.fluxM_on){
      detector.state = 'CANDIDATE';
      detector.candidate = {
        t0: now,
        frames: [feat],
      };

      lastAttackScore = 0.25;
      lastAttackState = 'WEAK';
      lastAttackReason = 'candidate start';
      return null;
    }

    lastAttackScore = 0;
    lastAttackState = 'NO';
    lastAttackReason = '';
    return null;
  }

  if(detector.state === 'CANDIDATE'){
    detector.candidate.frames.push(feat);

    const frames = detector.candidate.frames;
    const dur = now - detector.candidate.t0;

    const atk = calcAttackScoreFromFrames(frames);

    lastAttackScore = atk.score;
    lastAttackState = atk.state;     // NO / WEAK / MAYBE / FISH
    lastAttackReason = atk.reason;

    if(atk.score >= DET.scoreHit && dur <= DET.candidateMaxSec){
      detector.state = 'COOLDOWN';
      detector.cooldownUntil = now + DET.cooldownSec;
      detector.candidate = null;

      pushAttackMark(now, atk.score, 'HIT');

      return {
        t: now,
        score: atk.score,
        dur,
        state: atk.state,
        reason: atk.reason
      };
    }

    if(dur > DET.longPenaltySec){
      detector.state = 'IDLE';
      detector.candidate = null;

      lastAttackScore = 0;
      lastAttackState = 'NO';
      lastAttackReason = 'long event';
      return null;
    }

    return null;
  }

  return null;
}

let scrSmooth = 0;
function updateScrapeMeter(lvl){
  scrSmooth = scrSmooth + 0.2 * (lvl - scrSmooth);
  scrEl.value = scrSmooth;
  scrTxt.textContent = scrSmooth.toFixed(1);

  if(scrSmooth >= 15) scrState.textContent = 'STRONG';
  else if(scrSmooth >= Number(thrEl.value)) scrState.textContent = 'SCRAPE';
  else scrState.textContent = '';
}

// ===== Time-series =====
const tsBuf = []; // {t, scrape, peakA, peakM}
let lastPeakAHz = NaN;
let lastPeakMHz = NaN;

const touchBuf = []; // {t, v}  v=1 touched

function pruneTouch(nowT){
  // TOUCHログは実験記録として残す。
  // 以前はここで古い shot を splice していて、
  // 新しいタッチのたびにテーブル行が減っていた。
  return;
}

function pruneTimeSeries(nowT){
  const keepLatestSec = Math.max(getTimeWindowSec(), 30) + 5;

  let focusStart = Infinity;
  let focusEnd = -Infinity;

  if (!timeLogFollowLatest) {
    const sel = getSelectedShot();
    if (sel) {
      const winSec = getTimeWindowSec();
      focusStart = sel.t - winSec / 2 - 1;
      focusEnd   = sel.t + winSec / 2 + 1;
    }
  }

  for (let i = tsBuf.length - 1; i >= 0; i--) {
    const t = tsBuf[i].t;

    const keepLatest = (t >= nowT - keepLatestSec);
    const keepFocus  = (t >= focusStart && t <= focusEnd);

    if (!keepLatest && !keepFocus) {
      tsBuf.splice(i, 1);
    }
  }
}


function drawTimeSeries(){
  const W = tsCanvas.width, H = tsCanvas.height;
  gT.clearRect(0, 0, W, H);

  const ml = 52, mr = 52, mt = 14, mb = 22;
  const pw = W - ml - mr, ph = H - mt - mb;

  // 軸
  gT.strokeStyle = '#888';
  gT.lineWidth = 1;
  gT.beginPath();
  gT.moveTo(ml, mt);
  gT.lineTo(ml, mt + ph);
  gT.lineTo(ml + pw, mt + ph);
  gT.stroke();

  if (tsBuf.length < 2) {
    gT.fillStyle = '#999';
    gT.font = `${Math.floor(12 * (window.devicePixelRatio || 1))}px sans-serif`;
    gT.fillText('no time series yet', ml + 10, mt + 20);
    return;
  }

  const t0 = tsBuf[0].t;
  const t1 = tsBuf[tsBuf.length - 1].t;
  const dt = Math.max(0.001, t1 - t0);

  const yScrMin = 0, yScrMax = 100;
  const yHzMin  = 0, yHzMax  = viewMaxHz;

  function xMap(t){
    return ml + pw * ((t - t0) / dt);
  }
  function yMapScr(v){
    return mt + ph - ph * ((v - yScrMin) / (yScrMax - yScrMin));
  }
  function yMapHz(v){
    return mt + ph - ph * ((v - yHzMin) / Math.max(1e-9, (yHzMax - yHzMin)));
  }

  // グリッド＆目盛り
  gT.font = `${Math.floor(11 * (window.devicePixelRatio || 1))}px sans-serif`;
  const ticks = 4;

  for (let i = 0; i <= ticks; i++) {
    const y = mt + ph - ph * (i / ticks);

    gT.strokeStyle = '#eee';
    gT.beginPath();
    gT.moveTo(ml, y);
    gT.lineTo(ml + pw, y);
    gT.stroke();

    // 左: SCRAPE
    gT.fillStyle = '#0b7a75';
    const vL = yScrMin + (yScrMax - yScrMin) * (i / ticks);
    gT.fillText(vL.toFixed(0), 6, y + 4);

    // 右: Hz
    gT.fillStyle = '#666';
    const vR = yHzMin + (yHzMax - yHzMin) * (i / ticks);
    const txt = vR.toFixed(0);
    const tw = gT.measureText(txt).width;
    gT.fillText(txt, ml + pw + mr - tw - 6, y + 4);
  }

  gT.fillStyle = '#666';
  gT.fillText(`${dt.toFixed(1)}s window`, ml, mt + ph + 18);

  // ===== SCRAPE =====
  gT.strokeStyle = '#0b7a75';
  gT.lineWidth = 2;
  gT.beginPath();

  for (let i = 0; i < tsBuf.length; i++) {
    const p = tsBuf[i];
    const scrape = Number(p.scrape) || 0;
    const x = xMap(p.t);
    const y = yMapScr(scrape);

    if (i === 0) gT.moveTo(x, y);
    else gT.lineTo(x, y);
  }
  gT.stroke();

  // ===== PeakA =====
  gT.strokeStyle = '#1e88e5';
  gT.lineWidth = 2;
  gT.beginPath();

  let startedA = false;
  for (const p of tsBuf) {
    const peakA = Number(p.peakAHz ?? p.peakA);
    if (!isFinite(peakA)) continue;

    const x = xMap(p.t);
    const y = yMapHz(peakA);

    if (!startedA) {
      gT.moveTo(x, y);
      startedA = true;
    } else {
      gT.lineTo(x, y);
    }
  }
  if (startedA) gT.stroke();

  // ===== PeakM =====
  gT.strokeStyle = '#ff6f00';
  gT.lineWidth = 2;
  gT.beginPath();

  let startedM = false;
  for (const p of tsBuf) {
    const peakM = Number(p.peakMHz ?? p.peakM);
    if (!isFinite(peakM)) continue;

    const x = xMap(p.t);
    const y = yMapHz(peakM);

    if (!startedM) {
      gT.moveTo(x, y);
      startedM = true;
    } else {
      gT.lineTo(x, y);
    }
  }
  if (startedM) gT.stroke();

  // ===== legend =====
  gT.fillStyle = '#0b7a75';
  gT.fillText('SCRAPE', ml + 6, mt + 12);

  gT.fillStyle = '#1e88e5';
  gT.fillText('PeakA Hz', ml + 80, mt + 12);

  gT.fillStyle = '#ff6f00';
  gT.fillText('PeakM Hz', ml + 170, mt + 12);

  // ===== Touch markers =====
  gT.strokeStyle = '#d81b60';
  gT.lineWidth = 2;
  for (const ev of touchBuf) {
    const x = xMap(ev.t);
    gT.beginPath();
    gT.moveTo(x, mt);
    gT.lineTo(x, mt + ph);
    gT.stroke();
  }

  gT.fillStyle = '#d81b60';
  gT.fillText('TOUCH', ml + 260, mt + 12);

  // ===== 表示時間範囲 =====
  const nowSec = (tsBuf && tsBuf.length) ? tsBuf[tsBuf.length - 1].t : 0;
  const timeWindowEl = document.getElementById('timeWindow');
  const winSec = Number(timeWindowEl?.value || 30);

  const viewStart = Math.max(0, nowSec - winSec);
  const viewEnd   = Math.max(winSec, nowSec);

  // 最後に丸印を重ねる
  drawTouchCircles({
    xMap,
    yScrapeMap: yMapScr,
    ml, pw, mt, ph,
    viewStart, viewEnd
  });





}

function drawFluxTimeSeries(){
  if (!tsFluxCanvas || !gTF) return;

  const W = tsFluxCanvas.width;
  const H = tsFluxCanvas.height;
  gTF.clearRect(0, 0, W, H);

  const selectedFrozen = getSelectedFrozenSeries();
  const seriesSrc = (!timeLogFollowLatest && selectedFrozen)
    ? selectedFrozen
    : tsBuf;

  // ★ 上段 drawTimeLog() と同じ余白にする
  const ml = 58, mr = 58, mt = 14, mb = 22;
  const pw = W - ml - mr;
  const ph = H - mt - mb;

  const chartLeft   = ml;
  const chartRight  = ml + pw;
  const chartTop    = mt;
  const chartBottom = mt + ph;

  // 軸
  gTF.strokeStyle = '#d4d4d4';
  gTF.lineWidth = 1;
  gTF.beginPath();
  gTF.moveTo(chartLeft, chartTop);
  gTF.lineTo(chartLeft, chartBottom);
  gTF.lineTo(chartRight, chartBottom);
  gTF.stroke();

  if (!seriesSrc || seriesSrc.length < 2) {
    gTF.fillStyle = '#999';
    gTF.font = '12px sans-serif';
    gTF.fillText('no flux yet', chartLeft + 10, chartTop + 18);
    return;
  }

  // ★ 上段 drawTimeLog() と同じ時間窓にする
  const nowSec = seriesSrc[seriesSrc.length - 1].t;
  const winSec = getTimeWindowSec();

  let viewStart = 0;
  let viewEnd = winSec;

  if (!timeLogFollowLatest && isFinite(timeLogCenterSec)) {
    viewStart = Math.max(0, timeLogCenterSec - winSec / 2);
    viewEnd = viewStart + winSec;

    if (viewEnd > nowSec && nowSec > winSec) {
      viewEnd = nowSec;
      viewStart = Math.max(0, viewEnd - winSec);
    }
  } else {
    viewStart = Math.max(0, nowSec - winSec);
    viewEnd = Math.max(winSec, nowSec);
  }

  const visible = seriesSrc.filter(p => p.t >= viewStart && p.t <= viewEnd);
  if (visible.length < 2) {
    gTF.fillStyle = '#999';
    gTF.font = '12px sans-serif';
    gTF.fillText('no flux in view', chartLeft + 10, chartTop + 18);
    return;
  }

  let fluxMax = 0.12;
  for (const p of visible) {
    const fa = Number(p.fluxA) || 0;
    const fm = Number(p.fluxM) || 0;
    if (fa > fluxMax) fluxMax = fa;
    if (fm > fluxMax) fluxMax = fm;
  }
  fluxMax *= 1.15;

  // ★ 上段と同じ xMap ロジック
  function xMap(t){
    return chartLeft + ((t - viewStart) / Math.max(1e-9, (viewEnd - viewStart))) * pw;
  }

  function yMap(v){
    const vv = Math.max(0, Math.min(fluxMax, v || 0));
    return chartBottom - (vv / Math.max(1e-9, fluxMax)) * ph;
  }

  // 横ガイド
  gTF.strokeStyle = '#ececec';
  gTF.lineWidth = 1;
  gTF.setLineDash([]);
  for(let i = 0; i <= 4; i++){
    const y = chartTop + ph * i / 4;
    gTF.beginPath();
    gTF.moveTo(chartLeft, y);
    gTF.lineTo(chartRight, y);
    gTF.stroke();
  }

  // 左目盛
  gTF.font = '11px sans-serif';
  gTF.textBaseline = 'middle';
  for(let i = 0; i <= 4; i++){
    const y = chartTop + ph * i / 4;
    const val = fluxMax - (fluxMax * i / 4);

    gTF.fillStyle = '#666';
    gTF.textAlign = 'right';
    gTF.fillText(val.toFixed(2), chartLeft - 8, y);
  }

  // FluxA
  gTF.save();
  gTF.strokeStyle = '#8e24aa';
  gTF.lineWidth = 2;
  gTF.beginPath();
  let startedA = false;
  for (const p of visible) {
    const x = xMap(p.t);
    const y = yMap(Number(p.fluxA) || 0);
    if (!startedA) {
      gTF.moveTo(x, y);
      startedA = true;
    } else {
      gTF.lineTo(x, y);
    }
  }
  if (startedA) gTF.stroke();
  gTF.restore();

  // FluxM
  gTF.save();
  gTF.strokeStyle = '#fb8c00';
  gTF.lineWidth = 2;
  gTF.beginPath();
  let startedM = false;
  for (const p of visible) {
    const x = xMap(p.t);
    const y = yMap(Number(p.fluxM) || 0);
    if (!startedM) {
      gTF.moveTo(x, y);
      startedM = true;
    } else {
      gTF.lineTo(x, y);
    }
  }
  if (startedM) gTF.stroke();
  gTF.restore();

  // TOUCH
  for (const s of touchShots) {
    if (s.t < viewStart || s.t > viewEnd) continue;
    const x = xMap(s.t);
    drawTouchMarker(gTF, x, chartTop, chartBottom, s);
  }

  // ATTACK
  for (const p of visible) {
    const atk = Number(p.attackScore) || 0;
    if (atk < 0.62) continue;
    const x = xMap(p.t);

    gTF.save();
    gTF.strokeStyle = '#e53935';
    gTF.lineWidth = 1.5;
    gTF.setLineDash([5, 4]);
    gTF.beginPath();
    gTF.moveTo(x, chartTop);
    gTF.lineTo(x, chartBottom);
    gTF.stroke();
    gTF.restore();
  }

  // 現在値
  const last = visible[visible.length - 1];
  gTF.textBaseline = 'top';
  gTF.textAlign = 'left';
  gTF.fillStyle = '#8e24aa';
  gTF.fillText(`A:${(Number(last?.fluxA) || 0).toFixed(3)}`, chartLeft + 8, chartTop + 6);
  gTF.fillStyle = '#fb8c00';
  gTF.fillText(`M:${(Number(last?.fluxM) || 0).toFixed(3)}`, chartLeft + 90, chartTop + 6);

  // 下部表示
  gTF.font = '11px sans-serif';
  gTF.textBaseline = 'alphabetic';
  gTF.fillStyle = '#777';
  gTF.textAlign = 'left';
  gTF.fillText(`Flux 0 - ${fluxMax.toFixed(2)}`, chartLeft, H - 6);
}


function drawStateTimeline(){
  if (!tsStateCanvas || !gTS) return;

  const W = tsStateCanvas.width;
  const H = tsStateCanvas.height;
  gTS.clearRect(0, 0, W, H);

  const selectedFrozen = getSelectedFrozenSeries();
  const seriesSrc = (!timeLogFollowLatest && selectedFrozen)
    ? selectedFrozen
    : tsBuf;

  const ml = 58, mr = 58, mt = 10, mb = 18;
  const pw = W - ml - mr;
  const ph = H - mt - mb;

  const chartLeft   = ml;
  const chartRight  = ml + pw;
  const chartTop    = mt;
  const chartBottom = mt + ph;

  gTS.fillStyle = '#fcfcfc';
  gTS.fillRect(0, 0, W, H);

  gTS.strokeStyle = '#d4d4d4';
  gTS.lineWidth = 1;
  gTS.beginPath();
  gTS.moveTo(chartLeft, chartTop);
  gTS.lineTo(chartLeft, chartBottom);
  gTS.lineTo(chartRight, chartBottom);
  gTS.stroke();

  if (!seriesSrc || seriesSrc.length < 2) {
    gTS.fillStyle = '#999';
    gTS.font = '12px sans-serif';
    gTS.fillText('no state yet', chartLeft + 10, chartTop + 18);
    return;
  }

  const nowSec = seriesSrc[seriesSrc.length - 1].t;
  const winSec = getTimeWindowSec();

  let viewStart = 0;
  let viewEnd = winSec;

  if (!timeLogFollowLatest && isFinite(timeLogCenterSec)) {
    viewStart = Math.max(0, timeLogCenterSec - winSec / 2);
    viewEnd = viewStart + winSec;

    if (viewEnd > nowSec && nowSec > winSec) {
      viewEnd = nowSec;
      viewStart = Math.max(0, viewEnd - winSec);
    }
  } else {
    viewStart = Math.max(0, nowSec - winSec);
    viewEnd = Math.max(winSec, nowSec);
  }

  function xMap(t){
    return chartLeft + ((t - viewStart) / Math.max(1e-9, (viewEnd - viewStart))) * pw;
  }

  const visible = seriesSrc.filter(p => p.t >= viewStart && p.t <= viewEnd);
  if (!visible.length) return;

  // レーン背景
  gTS.fillStyle = '#f2f4f5';
  gTS.fillRect(chartLeft, chartTop + 12, pw, ph - 24);

  // 連続区間で state を塗る
  let segStart = visible[0].t;
  let segState = visible[0].phase2State || 'IDLE';

  for (let i = 1; i <= visible.length; i++) {
    const cur = visible[i];
    const curState = cur ? (cur.phase2State || 'IDLE') : null;

    if (!cur || curState !== segState) {
      const t0 = segStart;
      const t1 = cur ? cur.t : visible[visible.length - 1].t;

      const x0 = xMap(t0);
      const x1 = xMap(t1);

      gTS.fillStyle = STATE_COLORS[segState] || '#cfd8dc';
      gTS.globalAlpha = 0.55;
      gTS.fillRect(x0, chartTop + 12, Math.max(2, x1 - x0), ph - 24);
      gTS.globalAlpha = 1.0;

      if (x1 - x0 > 40) {
        gTS.fillStyle = '#222';
        gTS.font = '12px sans-serif';
        gTS.textAlign = 'center';
        gTS.textBaseline = 'middle';
        gTS.fillText(
          STATE_LABELS[segState] || segState,
          (x0 + x1) / 2,
          chartTop + ph / 2
        );
      }

      if (cur) {
        segStart = cur.t;
        segState = curState;
      }
    }
  }

  // 遷移線
  for (const tr of stateTransitions) {
    if (tr.t < viewStart || tr.t > viewEnd) continue;
    const x = xMap(tr.t);

    gTS.save();
    gTS.strokeStyle = '#263238';
    gTS.lineWidth = 1.5;
    gTS.setLineDash([4, 3]);
    gTS.beginPath();
    gTS.moveTo(x, chartTop + 8);
    gTS.lineTo(x, chartBottom - 8);
    gTS.stroke();
    gTS.restore();

    gTS.fillStyle = '#263238';
    gTS.font = '10px sans-serif';
    gTS.textAlign = 'left';
    gTS.textBaseline = 'top';
    gTS.fillText(`${tr.from}→${tr.to}`, x + 4, chartTop + 2);
  }

  // touch marker
  for (const s of touchShots) {
    if (s.t < viewStart || s.t > viewEnd) continue;
    const x = xMap(s.t);
    drawTouchMarker(gTS, x, chartTop, chartBottom, s);
  }

  // 左ラベル
  gTS.fillStyle = '#666';
  gTS.font = '11px sans-serif';
  gTS.textAlign = 'right';
  gTS.textBaseline = 'middle';
  gTS.fillText('STATE', chartLeft - 8, chartTop + ph / 2);

  // 下部
  gTS.fillStyle = '#777';
  gTS.font = '11px sans-serif';
  gTS.textAlign = 'left';
  gTS.textBaseline = 'alphabetic';
  gTS.fillText('Phase2 State Timeline', chartLeft, H - 4);
}

function drawPeakTimeline(){
  if (!tsPeakCanvas || !gTP) return;

  const W = tsPeakCanvas.width;
  const H = tsPeakCanvas.height;
  gTP.clearRect(0, 0, W, H);

  const selectedFrozen = getSelectedFrozenSeries();
  const seriesSrc = (!timeLogFollowLatest && selectedFrozen)
    ? selectedFrozen
    : tsBuf;

  const ml = 58, mr = 58, mt = 18, mb = 24;
  const pw = W - ml - mr;
  const ph = H - mt - mb;

  const chartLeft   = ml;
  const chartRight  = ml + pw;
  const chartTop    = mt;
  const chartBottom = mt + ph;

  gTP.fillStyle = '#fcfcfc';
  gTP.fillRect(0, 0, W, H);

  gTP.strokeStyle = '#d4d4d4';
  gTP.lineWidth = 1;
  gTP.beginPath();
  gTP.moveTo(chartLeft, chartTop);
  gTP.lineTo(chartLeft, chartBottom);
  gTP.lineTo(chartRight, chartBottom);
  gTP.stroke();

  if (!seriesSrc || seriesSrc.length < 2) {
    gTP.fillStyle = '#999';
    gTP.font = '12px sans-serif';
    gTP.fillText('no peak timeline yet', chartLeft + 10, chartTop + 18);
    return;
  }

  const nowSec = seriesSrc[seriesSrc.length - 1].t;
  const winSec = getTimeWindowSec();

  let viewStart = 0;
  let viewEnd = winSec;

  if (!timeLogFollowLatest && isFinite(timeLogCenterSec)) {
    viewStart = Math.max(0, timeLogCenterSec - winSec / 2);
    viewEnd = viewStart + winSec;

    if (viewEnd > nowSec && nowSec > winSec) {
      viewEnd = nowSec;
      viewStart = Math.max(0, viewEnd - winSec);
    }
  } else {
    viewStart = Math.max(0, nowSec - winSec);
    viewEnd = Math.max(winSec, nowSec);
  }

  const hzMin = Math.max(0, viewMinHz || 0);
  const hzMax = Math.max(hzMin + 1, viewMaxHz || 600);

  function xMap(t){
    return chartLeft + ((t - viewStart) / Math.max(1e-9, (viewEnd - viewStart))) * pw;
  }

  function yMapHz(hz){
    const v = Math.max(hzMin, Math.min(hzMax, Number(hz) || 0));
    return chartBottom - ((v - hzMin) / Math.max(1e-9, (hzMax - hzMin))) * ph;
  }

  // horizontal grid
  gTP.strokeStyle = '#ececec';
  gTP.lineWidth = 1;
  for(let i = 0; i <= 4; i++){
    const y = chartTop + ph * i / 4;
    gTP.beginPath();
    gTP.moveTo(chartLeft, y);
    gTP.lineTo(chartRight, y);
    gTP.stroke();

    const hzVal = hzMax - ((hzMax - hzMin) * i / 4);
    gTP.fillStyle = '#666';
    gTP.font = '11px sans-serif';
    gTP.textAlign = 'right';
    gTP.textBaseline = 'middle';
    gTP.fillText(`${Math.round(hzVal)}`, chartLeft - 8, y);
  }

  // dots only
  const visible = seriesSrc.filter(p => p.t >= viewStart && p.t <= viewEnd);

  const rankRadius = [4.0, 3.0, 2.2, 1.8, 1.4];
  const rankAlphaA = [0.90, 0.72, 0.56, 0.42, 0.32];
  const rankAlphaM = [0.90, 0.72, 0.56, 0.42, 0.32];

  for (const p of visible) {
    const x = xMap(p.t);

    const peaksA = Array.isArray(p.topPeaksA) ? p.topPeaksA : [];
    const peaksM = Array.isArray(p.topPeaksM) ? p.topPeaksM : [];

    peaksA.slice(0, 5).forEach((pk, i) => {
      const hz = Number(pk?.hz) || 0;
      if (hz < hzMin || hz > hzMax) return;

      const y = yMapHz(hz);
      gTP.save();
      gTP.fillStyle = `rgba(30,136,229,${rankAlphaA[i] ?? 0.28})`;
      gTP.beginPath();
      gTP.arc(x, y, rankRadius[i] ?? 1.4, 0, Math.PI * 2);
      gTP.fill();
      gTP.restore();
    });

    peaksM.slice(0, 5).forEach((pk, i) => {
      const hz = Number(pk?.hz) || 0;
      if (hz < hzMin || hz > hzMax) return;

      const y = yMapHz(hz);
      gTP.save();
      gTP.fillStyle = `rgba(255,111,0,${rankAlphaM[i] ?? 0.28})`;
      gTP.beginPath();
      gTP.arc(x, y, rankRadius[i] ?? 1.4, 0, Math.PI * 2);
      gTP.fill();
      gTP.restore();
    });
  }

  // touch marker
  for (const s of touchShots) {
    if (s.t < viewStart || s.t > viewEnd) continue;
    const x = xMap(s.t);
    drawTouchMarker(gTP, x, chartTop, chartBottom, s);
  }

  // legend
  gTP.font = '11px sans-serif';
  gTP.textBaseline = 'alphabetic';
  gTP.textAlign = 'left';

  gTP.fillStyle = '#1e88e5';
  gTP.fillText('A peak dots', chartLeft + 8, chartTop - 4);

  gTP.fillStyle = '#ff6f00';
  gTP.fillText('M peak dots', chartLeft + 92, chartTop - 4);

  gTP.fillStyle = '#777';
  gTP.fillText('size = peak rank', chartLeft + 182, chartTop - 4);

  gTP.fillStyle = '#777';
  gTP.fillText('Peak Timeline', chartLeft, H - 6);
}



function drawTouchCircles({ xMap, yScrapeMap, ml, pw, mt, ph, viewStart, viewEnd }){
  gT.fillStyle = '#d81b60';
  gT.font = '12px sans-serif';

  for(const s of touchShots){
    if (s.t < viewStart || s.t > viewEnd) continue;
    const x = xMap(s.t);
    if(x < ml || x > ml+pw) continue;

    const y = yScrapeMap(s.scrape);

    const isSel = (s.id === selectedShotId);
    const r = isSel ? 6 : 4;

    gT.beginPath();
    gT.arc(x, y, r, 0, Math.PI * 2);
    gT.fill();

    if (isSel) {
      gT.save();
      gT.strokeStyle = '#111';
      gT.lineWidth = 2;
      gT.beginPath();
      gT.arc(x, y, r + 2, 0, Math.PI * 2);
      gT.stroke();
      gT.restore();
    }


    if(isSel) gT.font = 'bold 13px sans-serif';
    gT.fillText(Number(s.scrape).toFixed(1), x + 6, y - 6);
    if(isSel) gT.font = '12px sans-serif';

    drawTouchMarker(gT, x, mt, mt + ph, s);
  }
}








function startRec(){
  if(isRec) return;
  isRec = true;
  recStartMs = performance.now();
  resetRec();
  const st = document.getElementById('recStatus');
  const btn = document.getElementById('recBtn');
  if(st) st.textContent = 'recording...';
  if(btn) btn.textContent = 'STOP';
}

function stopRec(){
  if(!isRec) return;
  isRec = false;

  const st = document.getElementById('recStatus');
  const btn = document.getElementById('recBtn');
  if(btn) btn.textContent = `RECORD (${REC_SEC}s)`;

  if(recCount <= 0){
    if(st) st.textContent = 'no data';
    return;
  }
 
  let bandAccel = {};
  let bandMic   = {};

  for(const b of BANDS){
    const k = b.key;
    bandAccel[k] = recSum.A[k] / recCount;
    bandMic[k]   = recSum.M[k] / recCount;
  }

  // 平均後に再正規化して合計100%へそろえる
  bandAccel = normalizeBandMap(bandAccel);
  bandMic   = normalizeBandMap(bandMic);

  // create object for comparison and save into slot
  const slot = getRecSlot();

  const mdiInfo = calcCombinedMDI(recFluxHist.A, recFluxHist.M);

  saveCurrentAvg(slot, {
    accel: structuredClone(bandAccel),
    mic:   structuredClone(bandMic),
    count: recCount,
    stamp: Date.now(),
    mdi: mdiInfo.mdi,
    mdiA: mdiInfo.mdiA,
    mdiM: mdiInfo.mdiM,
  });


  // show panel + render bars
    const panel = document.getElementById(slot === 'A' ? 'recPanelA' : 'recPanelB');
    if(panel) panel.style.display = 'block';

    const suf = (slot === 'A') ? '' : '2';


    for(const b of BANDS){
      const k = b.key;

      const aRatio = Math.max(0, Math.min(1, bandAccel[k]));
      const mRatio = Math.max(0, Math.min(1, bandMic[k]));

      const aEl = document.getElementById(`rbarA${suf}_${k}`);
      const mEl = document.getElementById(`rbarM${suf}_${k}`);
      const aTx = document.getElementById(`rtxtA${suf}_${k}`);
      const mTx = document.getElementById(`rtxtM${suf}_${k}`);

      if(aEl) aEl.style.width = `${(aRatio*100).toFixed(1)}%`;
      if(mEl) mEl.style.width = `${(mRatio*100).toFixed(1)}%`;
      if(aTx) aTx.textContent = `${(aRatio*100).toFixed(1)}%`;
      if(mTx) mTx.textContent = `${(mRatio*100).toFixed(1)}%`;
    }

  if(st) st.textContent = `saved (${recCount} frames)`;

  const stamp = new Date().toLocaleTimeString();
  if(st) st.textContent = `saved to ${slot} (${recCount} frames) @ ${stamp}`;

  // differences (only when both A and B are available)
  if (recAvgA && recAvgB) {
  
    if (!diffAccelEl || !diffMicEl) {
      console.warn('diff elements not found');
      return;
    }

    const diffAccel = calcDiff(recAvgA.accel, recAvgB.accel);
    const diffMic   = calcDiff(recAvgA.mic,   recAvgB.mic);

    drawDiff(diffAccelEl, diffAccel);
    drawDiff(diffMicEl,   diffMic);
  
    // === score calculation starts here ===
    const aAccel = bandsToArray(recAvgA.accel);
    const aMic   = bandsToArray(recAvgA.mic);
    const bAccel = bandsToArray(recAvgB.accel);
    const bMic   = bandsToArray(recAvgB.mic);

    
    // if any data is missing, log a reason (this is important)
    if(!aAccel || !aMic || !bAccel || !bMic){
      console.log('recAvgA', recAvgA);
      console.log('recAvgB', recAvgB);

      console.warn('score bands missing', {aAccel,aMic,bAccel,bMic, recAvgA, recAvgB});
      if(scoreWinnerEl){
        scoreWinnerEl.textContent = 'NoData';
        scoreDeltaEl.textContent  = '-';
        scoreA_accelEl.textContent = scoreA_micEl.textContent = scoreA_totalEl.textContent = '-';
        scoreB_accelEl.textContent = scoreB_micEl.textContent = scoreB_totalEl.textContent = '-';
      }
    } else {
      const sA_accel = weightedScore(aAccel);
      const sA_mic   = weightedScore(aMic);
      const sB_accel = weightedScore(bAccel);
      const sB_mic   = weightedScore(bMic);

      const MIC_WEIGHT = 0.8;
      const ACC_WEIGHT = 1.0;

      const sA_total = ACC_WEIGHT*sA_accel + MIC_WEIGHT*sA_mic;
      const sB_total = ACC_WEIGHT*sB_accel + MIC_WEIGHT*sB_mic;

      scoreA_accelEl.textContent = fmtScore(sA_accel);
      scoreA_micEl.textContent   = fmtScore(sA_mic);
      scoreA_totalEl.textContent = fmtScore(sA_total);

      scoreB_accelEl.textContent = fmtScore(sB_accel);
      scoreB_micEl.textContent   = fmtScore(sB_mic);
      scoreB_totalEl.textContent = fmtScore(sB_total);

      const d = sB_total - sA_total;
      scoreDeltaEl.textContent = (d>=0?'+':'') + fmtScore(d);
      scoreWinnerEl.textContent = (d>0) ? 'B' : (d<0 ? 'A' : 'Draw');
      
      // ▼▼▼ ここに追加 ▼▼▼
      const mdiA = Number(recAvgA.mdi) || 0;
      const mdiB = Number(recAvgB.mdi) || 0;

      document.getElementById("mdiA").textContent = mdiA.toFixed(3);
      document.getElementById("mdiB").textContent = mdiB.toFixed(3);

      const deltaMdi = mdiB - mdiA;
      document.getElementById("mdiDelta").textContent = (deltaMdi >= 0 ? '+' : '') + deltaMdi.toFixed(3);

      // 小さい方が安定
      let mdiWinner = 'Draw';
      if (Math.abs(deltaMdi) > 0.001) {
        mdiWinner = deltaMdi > 0 ? 'A' : 'B';
      }
      document.getElementById("mdiWinner").textContent = mdiWinner;

      // ▲▲▲ ここまで ▲▲▲

      // ▼▼▼ MDI2（構造分散） ▼▼▼
      // Accel + Mic を平均で使う
      function calcCombinedMDI2(rec){
        const a = calcMDI2FromBandMap(rec.accel);
        const m = calcMDI2FromBandMap(rec.mic);
        return (a + m) / 2;
      }

      const mdi2A = calcCombinedMDI2(recAvgA);
      const mdi2B = calcCombinedMDI2(recAvgB);

      document.getElementById("mdi2A").textContent = mdi2A.toFixed(3);
      document.getElementById("mdi2B").textContent = mdi2B.toFixed(3);

      const delta2 = mdi2B - mdi2A;
      document.getElementById("mdi2Delta").textContent =
        (delta2 >= 0 ? '+' : '') + delta2.toFixed(3);

      let winner2 = 'Draw';
      if (Math.abs(delta2) > 0.001){
        winner2 = delta2 > 0 ? 'B' : 'A';
      }

      document.getElementById("mdi2Winner").textContent = winner2;

      // ▲▲▲ ここまで ▲▲▲

      // ▼▼▼ Immersion Score ▼▼▼

      const immA = Math.pow(1 - mdiA, 2) * (1 - mdi2A);
      const immB = Math.pow(1 - mdiB, 2) * (1 - mdi2B);


      document.getElementById("immA").textContent = immA.toFixed(3);
      document.getElementById("immB").textContent = immB.toFixed(3);

      const deltaImm = immB - immA;
      document.getElementById("immDelta").textContent =
        (deltaImm >= 0 ? '+' : '') + deltaImm.toFixed(3);

      let immWinner = 'Draw';
      if (Math.abs(deltaImm) > 0.001){
        immWinner = deltaImm > 0 ? 'B' : 'A';
      }

      document.getElementById("immWinner").textContent = immWinner;

      // ▲▲▲ ここまで ▲▲▲


    }
    // === end of scoring section ===



    if(aAccel && aMic && bAccel && bMic && fishA_valEl){
      const fA = fishIndexFromBands(aAccel, aMic);
      const fB = fishIndexFromBands(bAccel, bMic);

      fishA_valEl.textContent = fmt1(fA);
      fishB_valEl.textContent = fmt1(fB);
      fishA_barEl.style.width = fA + '%';
      fishB_barEl.style.width = fB + '%';

      const d = fB - fA;
      fishDeltaEl.textContent = (d>=0?'+':'') + fmt1(d);
      fishWinnerEl.textContent = (d>0) ? 'B' : (d<0 ? 'A' : 'Draw');
    }  

  } else {
    // optional: clear display or show guidance
    
  }

}

// save array for comparison
function saveCurrentAvg(slot, avg) {
  if (slot === 'A') {
    const v = Number(recAvgA?.mdi) || 0;
    document.getElementById("mdiA").textContent = v.toFixed(3);
  }

  if (slot === 'B') {
    const v = Number(recAvgB?.mdi) || 0;
    document.getElementById("mdiB").textContent = v.toFixed(3);
  }

  if (slot === 'A') recAvgA = avg;
  if (slot === 'B') recAvgB = avg;
}

function updateRecIfNeeded(){
  if(!isRec) return;
  if(!latestBandA || !latestBandM) return;

  const aNorm = normalizeBandMap(latestBandA.smooth);
  const mNorm = normalizeBandMap(latestBandM.smooth);

  for(const b of BANDS){
    const k = b.key;
    recSum.A[k] += Number(aNorm[k]) || 0;
    recSum.M[k] += Number(mNorm[k]) || 0;
  }
  recCount++;

  recFluxHist.A.push(Number(lastFluxA) || 0);
  recFluxHist.M.push(Number(lastFluxM) || 0);

  const elapsed = (performance.now() - recStartMs) * 0.001;
  const st = document.getElementById('recStatus');
  if(st) st.textContent = `recording... ${elapsed.toFixed(1)}s`;

  if(elapsed >= REC_SEC){
    stopRec();
  }
}

let recSlot = 'A';

function getRecSlot(){
  const a = document.getElementById('slotA');
  const b = document.getElementById('slotB');
  if(b && b.checked) return 'B';
  return 'A';
}

function weightedScore(bands, w=BAND_W){
  // bands: expected as [b0,b1,b2,b3] (ratios 0–1 or percentages work)
  let s = 0;
  for(let i=0;i<Math.min(bands.length, w.length);i++){
    const v = Number(bands[i]) || 0;
    s += v * w[i];
  }
  return s;
}

// 表示用フォーマット（0〜1系なら小数、%系ならそのまま）
function fmtScore(x){
  if(!isFinite(x)) return '-';
  return x.toFixed(3);
}

function pickBands(rec, kind){
  // kind: 'accel' or 'mic'
  if(!rec) return null;

  // try all common candidate keys
  const cand = (kind === 'accel')
    ? [rec.accel, rec.A, rec.a, rec.acc, rec.accBands, rec.bandsA]
    : [rec.mic,   rec.M, rec.m, rec.micBands, rec.bandsM];

  for(const v of cand){
    if(Array.isArray(v) && v.length) return v;
  }
  return null;
}

// emphasize b2 (60–120Hz) and b3 (120–200Hz) when scaling index (0–100)
function fishIndexFromBands(accelBands, micBands){
  const a = accelBands || [];
  const m = micBands || [];

  let raw = 0;
  let maxRaw = 0;

  for (let i = 0; i < BANDS.length; i++) {
    const b = BANDS[i];
    const center = Number.isFinite(b.f1) ? (b.f0 + b.f1) / 2 : (b.f0 + 50);

    let wa = 1.0;
    let wm = 1.0;

    if (center >= 100 && center < 200) {
      wa = 2.5;
      wm = 3.0;
    } else if (center >= 80 && center < 100) {
      wa = 1.5;
      wm = 1.8;
    }

    raw += (Number(a[i]) || 0) * wa;
    raw += (Number(m[i]) || 0) * wm;
    maxRaw += wa + wm;
  }

  const idx = Math.max(0, Math.min(100, raw / Math.max(1e-9, maxRaw) * 100));
  return idx;
}


function fmt1(x){ return isFinite(x) ? x.toFixed(1) : '-'; }

function calcDiff(aMap, bMap){
  const out = {};
  for (const b of BANDS){
    const k = b.key;
    const a = Number(aMap?.[k] ?? 0);
    const bb = Number(bMap?.[k] ?? 0);
    out[k] = bb - a; // B - A（必要なら A-B に変えてOK）
  }
  return out;
}

function calcMDIFromSeries(arr){
  if (!Array.isArray(arr) || arr.length < 2) return 0;

  let sum = 0;
  for (let i = 1; i < arr.length; i++) {
    sum += Math.abs((Number(arr[i]) || 0) - (Number(arr[i - 1]) || 0));
  }
  return sum / (arr.length - 1);
}

function calcMDI2FromBandMap(map){
  if (!map) return 0;

  let max = 0;
  let high = 0;

  for (const b of BANDS){
    const k = b.key;
    const v = Number(map[k]) || 0;

    if (v > max) max = v;

    if (b.f0 >= 200){
      high += v;
    }
  }

  const dispersion = 1 - max;

  // ▼ここが重要（加算じゃなく平均）
  return (dispersion * 0.7) + (high * 0.3);
}



function calcCombinedMDI(fluxAList, fluxMList){
  const mdiA = calcMDIFromSeries(fluxAList);
  const mdiM = calcMDIFromSeries(fluxMList);

  // まずは単純平均
  return {
    mdiA,
    mdiM,
    mdi: (mdiA + mdiM) / 2
  };
}

function drawDiff(el, diff){
  if (!el) return;

  const values = Array.isArray(diff)
    ? diff.map(v => Number(v) || 0)
    : BANDS.map(b => Number(diff?.[b.key] ?? 0));

  const max = Math.max(1e-9, ...values.map(v => Math.abs(v)));

  el.innerHTML = '';

  values.forEach((v, i) => {
    const band = BANDS?.[i];
    const labelText = band?.label ?? String(i);

    const row = document.createElement('div');
    row.className = 'diffRow';

    const label = document.createElement('div');
    label.className = 'diffLabel';
    label.textContent = labelText;

    const barWrap = document.createElement('div');
    barWrap.className = 'diffBar';

    const zero = document.createElement('div');
    zero.className = 'diffZero';
    barWrap.appendChild(zero);

    const fill = document.createElement('div');
    fill.className = `diffFill ${v >= 0 ? 'plus' : 'minus'}`;

    const w = (Math.abs(v) / max) * 50;

    if (v >= 0) {
      fill.style.left = '50%';
      fill.style.width = `${w}%`;
    } else {
      fill.style.left = `${50 - w}%`;
      fill.style.width = `${w}%`;
    }

    barWrap.appendChild(fill);

    const val = document.createElement('div');
    val.className = 'diffVal';
    val.textContent = `${v >= 0 ? '+' : ''}${v.toFixed(3)}`;

    row.appendChild(label);
    row.appendChild(barWrap);
    row.appendChild(val);

    el.appendChild(row);
  });
}



let scrapeMaxForPlot = 1;

function yScrapeMap(v){
  const max = scrapeMaxForPlot || 1;
  const vv = Math.max(0, Math.min(max, v));
  return mt + ph - (vv / max) * ph;
}

function nearestSampleAt(tTarget){
  if (!tsBuf || tsBuf.length === 0) return null;

  let best = null;
  let bestDt = Infinity;

  for (const p of tsBuf) {
    const dt = Math.abs(p.t - tTarget);
    if (dt < bestDt) {
      bestDt = dt;
      best = p;
    }
  }
  return best;
}

function fillPendingPost(nowT){
  for (const s of touchShots) {
    if (s.postScrape != null) continue;   // すでに埋まっていればスキップ
    if (nowT < s.postT) continue;         // まだ未来時刻に達していない

    const post = nearestSampleAt(s.postT);
    if (!post) continue;

    s.postScrape = Number(post.scrape) || 0;
    s.postPeakA  = Number(post.peakAHz ?? post.peakA) || 0;
    s.postPeakM  = Number(post.peakMHz ?? post.peakM) || 0;
  }
}

let maxRef = 0;

function updateBand(v){
  maxRef = Math.max(maxRef, v);  // 過去最大

  const norm = v / (maxRef || 1);
}


function setLineStyleForTouch(ctx, shot){
  ctx.lineWidth = 2;

  if(shot.long || shot.kind === 'long'){
    ctx.strokeStyle = '#111';     // 長押し = 黒
    ctx.setLineDash([]);          // 実線
    ctx.lineWidth = 3;
    return;
  }

  if((shot.count || 1) === 1){
    ctx.strokeStyle = '#ff4fa3';  // 1tap = ピンク
    ctx.setLineDash([]);          // 実線
  }else if(shot.count === 2){
    ctx.strokeStyle = '#8e44ad';  // 2tap = 紫
    ctx.setLineDash([6,4]);       // 破線
  }else{
    ctx.strokeStyle = '#e53935';  // 3tap以上 = 赤
    ctx.setLineDash([2,4]);       // 点線っぽく
  }
}

function drawTouchMarker(ctx, x, topY, bottomY, shot){
  ctx.save();

  const isSel = (shot.id === selectedShotId);

  setLineStyleForTouch(ctx, shot);

  if (isSel) {
    ctx.lineWidth = Math.max(ctx.lineWidth + 2, 4);
  }

  // 縦線
  ctx.beginPath();
  ctx.moveTo(x, topY);
  ctx.lineTo(x, bottomY);
  ctx.stroke();

  // 選択中は上に薄い帯を出す
  if (isSel) {
    ctx.setLineDash([]);
    ctx.fillStyle = 'rgba(255, 215, 0, 0.18)';
    ctx.fillRect(x - 8, topY, 16, bottomY - topY);
  }

  // ラベル
  ctx.setLineDash([]);
  ctx.fillStyle = isSel ? '#000' : ctx.strokeStyle;
  ctx.font = isSel ? 'bold 12px sans-serif' : '11px sans-serif';
  ctx.fillText(touchLabel(shot), x + 4, topY + 12);

  ctx.restore();
}


function drawTouchLegend(ctx){
  const y = 16;

  ctx.save();
  ctx.font = '11px sans-serif';

  // SCRAPE
  ctx.fillStyle = '#4db6ac';
  ctx.fillText('SCRAPE', 8, y + 4);

  // PeakA
  ctx.fillStyle = '#1e88e5';
  ctx.fillText('PeakAHz', 70, y + 4);

  // PeakM
  ctx.fillStyle = '#ff6f00';
  ctx.fillText('PeakMHz', 135, y + 4);

  // T1
  ctx.strokeStyle = '#ff4fa3';
  ctx.setLineDash([]);
  ctx.lineWidth = 2;
  ctx.beginPath();
  ctx.moveTo(215, y);
  ctx.lineTo(235, y);
  ctx.stroke();
  ctx.fillStyle = '#ff4fa3';
  ctx.fillText('T1', 240, y + 4);

  // T2
  ctx.strokeStyle = '#8e44ad';
  ctx.setLineDash([6, 4]);
  ctx.beginPath();
  ctx.moveTo(270, y);
  ctx.lineTo(290, y);
  ctx.stroke();
  ctx.fillStyle = '#8e44ad';
  ctx.fillText('T2', 295, y + 4);

  // T3+
  ctx.strokeStyle = '#e53935';
  ctx.setLineDash([2, 4]);
  ctx.beginPath();
  ctx.moveTo(325, y);
  ctx.lineTo(345, y);
  ctx.stroke();
  ctx.fillStyle = '#e53935';
  ctx.fillText('T3+', 350, y + 4);

  // LONG
  ctx.strokeStyle = '#111';
  ctx.setLineDash([]);
  ctx.lineWidth = 3;
  ctx.beginPath();
  ctx.moveTo(390, y);
  ctx.lineTo(410, y);
  ctx.stroke();
  ctx.fillStyle = '#111';
  ctx.fillText('LONG', 415, y + 4);

  ctx.restore();
}


function touchLabel(shot){
  if (shot.long || shot.kind === 'long') return 'LONG';
  const c = shot.count || 1;
  if (c >= 3) return 'T3+';
  return `T${c}`;
}


function drawTimeLog(){
  //const W = ts.width, H = ts.height;
  const W = tsCanvas.width, H = tsCanvas.height;

  gT.clearRect(0, 0, W, H);

  const selectedFrozen = getSelectedFrozenSeries();
  const seriesSrc = (!timeLogFollowLatest && selectedFrozen)
    ? selectedFrozen
    : tsBuf;

  // 余白
  const ml = 58, mr = 58, mt = 24, mb = 26;
  const pw = W - ml - mr;
  const ph = H - mt - mb;

  const chartLeft   = ml;
  const chartRight  = ml + pw;
  const chartTop    = mt;
  const chartBottom = mt + ph;

  const hzMax  = 600;
  const scrMax = 20;   // 今のUIに合わせるなら20。必要に応じて100へ戻してOK

  if (selectedShotId != null) {
    const sel = getSelectedShot();
    if (!sel) {
      selectedShotId = null;
      followLatestTimeLog();
    } else if (!timeLogFollowLatest) {
      timeLogCenterSec = sel.t;
    }
  }

  const nowSec = (seriesSrc && seriesSrc.length) ? seriesSrc[seriesSrc.length - 1].t : 0;
  const winSec = getTimeWindowSec();

  let viewStart = 0;
  let viewEnd = winSec;

  if (!timeLogFollowLatest && isFinite(timeLogCenterSec)) {
    viewStart = Math.max(0, timeLogCenterSec - winSec / 2);
    viewEnd = viewStart + winSec;

    if (viewEnd > nowSec && nowSec > winSec) {
      viewEnd = nowSec;
      viewStart = Math.max(0, viewEnd - winSec);
    }
  } else {
    viewStart = Math.max(0, nowSec - winSec);
    viewEnd = Math.max(winSec, nowSec);
  }

  function xMap(t){
    return chartLeft + ((t - viewStart) / Math.max(1e-9, (viewEnd - viewStart))) * pw;
  }

  function yMapHz(hz){
    const v = Math.max(0, Math.min(hzMax, hz || 0));
    return chartBottom - (v / hzMax) * ph;
  }

  function yMapScr(scr){
    const v = Math.max(0, Math.min(scrMax, scr || 0));
    return chartBottom - (v / scrMax) * ph;
  }

  // 背景
  gT.fillStyle = '#fcfcfc';
  gT.fillRect(0, 0, W, H);

  // 横ガイド
  gT.strokeStyle = '#ececec';
  gT.lineWidth = 1;
  gT.setLineDash([]);
  for(let i = 0; i <= 4; i++){
    const y = chartTop + ph * i / 4;
    gT.beginPath();
    gT.moveTo(chartLeft, y);
    gT.lineTo(chartRight, y);
    gT.stroke();
  }

  // 枠
  gT.strokeStyle = '#d4d4d4';
  gT.lineWidth = 1;
  gT.beginPath();
  gT.moveTo(chartLeft, chartTop);
  gT.lineTo(chartLeft, chartBottom);
  gT.lineTo(chartRight, chartBottom);
  gT.stroke();

  // 軸ラベル
  gT.font = '12px sans-serif';
  gT.textBaseline = 'middle';

  for(let i = 0; i <= 4; i++){
    const y = chartTop + ph * i / 4;

    const hzVal = hzMax - (hzMax * i / 4);
    gT.fillStyle = '#1e88e5';
    gT.textAlign = 'right';
    gT.fillText(`${Math.round(hzVal)}`, chartLeft - 8, y);

    const scrVal = scrMax - (scrMax * i / 4);
    gT.fillStyle = '#4db6ac';
    gT.textAlign = 'left';
    gT.fillText(`${Math.round(scrVal)}`, chartRight + 8, y);
  }

  // 上部軸タイトル
  gT.textBaseline = 'alphabetic';
  gT.font = '12px sans-serif';

  gT.fillStyle = '#1e88e5';
  gT.textAlign = 'left';
  gT.fillText('Hz', chartLeft - 18, chartTop - 8);

  gT.fillStyle = '#4db6ac';
  gT.textAlign = 'right';
  gT.fillText('SCRAPE LEVEL', chartRight + 34, chartTop - 8);

  // SCRAPE
  if (seriesSrc && seriesSrc.length >= 2) {
    gT.save();
    gT.strokeStyle = '#4db6ac';
    gT.lineWidth = 2;
    gT.beginPath();

    let started = false;
    for (const p of seriesSrc) {
      if (p.t < viewStart || p.t > viewEnd) continue;
      const x = xMap(p.t);
      const y = yMapScr(p.scrape || 0);

      if (!started) {
        gT.moveTo(x, y);
        started = true;
      } else {
        gT.lineTo(x, y);
      }
    }
    if (started) gT.stroke();
    gT.restore();
  }

  // PeakAHz
  if (seriesSrc && seriesSrc.length >= 2) {
    gT.save();
    gT.strokeStyle = '#1e88e5';
    gT.lineWidth = 2;
    gT.beginPath();

    let started = false;
    for (const p of seriesSrc) {
      if (p.t < viewStart || p.t > viewEnd) continue;
      const x = xMap(p.t);
      const y = yMapHz(p.peakAHz || 0);

      if (!started) {
        gT.moveTo(x, y);
        started = true;
      } else {
        gT.lineTo(x, y);
      }
    }
    if (started) gT.stroke();
    gT.restore();
  }

  // PeakMHz
  if (seriesSrc && seriesSrc.length >= 2) {
    gT.save();
    gT.strokeStyle = '#ff6f00';
    gT.lineWidth = 2;
    gT.beginPath();

    let started = false;
    for (const p of seriesSrc) {
      if (p.t < viewStart || p.t > viewEnd) continue;
      const x = xMap(p.t);
      const y = yMapHz(p.peakMHz || 0);

      if (!started) {
        gT.moveTo(x, y);
        started = true;
      } else {
        gT.lineTo(x, y);
      }
    }
    if (started) gT.stroke();
    gT.restore();


  }

  // TOUCHマーカー
  for (const s of touchShots) {
    if (s.t < viewStart || s.t > viewEnd) continue;
    const x = xMap(s.t);
    drawTouchMarker(gT, x, chartTop, chartBottom, s);
  }

    // -------- ATTACK SCORE 線 --------
  if (seriesSrc && seriesSrc.length >= 2) {
    gT.save();
    gT.strokeStyle = '#e53935';
    gT.lineWidth = 2;
    gT.setLineDash([8, 4]);
    gT.beginPath();

    let started = false;
    for (const p of seriesSrc) {
      if (p.t < viewStart || p.t > viewEnd) continue;
      const x = xMap(p.t);
      const y = chartBottom - (clamp01(p.attackScore || 0)) * ph;

      if (!started) {
        gT.moveTo(x, y);
        started = true;
      } else {
        gT.lineTo(x, y);
      }
    }

    if (started) gT.stroke();
    gT.restore();
  }

  if (seriesSrc && seriesSrc.length > 0) {
  const d = Number(seriesSrc[seriesSrc.length - 1]?.density) || 0;

  gT.fillStyle = '#111';
  gT.font = '12px monospace';
  gT.textAlign = 'left';
  gT.textBaseline = 'top';
  const dNow = Number(seriesSrc[seriesSrc.length - 1]?.density) || 0;
  const dMean = calcRecentMeanDensity(seriesSrc, 2.0);

  gT.fillText(`DensityNow: ${dNow.toFixed(2)}`, chartLeft + 8, chartTop + 6);
  gT.fillText(`Density2s : ${dMean.toFixed(2)}`, chartLeft + 8, chartTop + 22);

}

  // 下部表示
  gT.font = '11px sans-serif';
  gT.textBaseline = 'alphabetic';

  gT.fillStyle = '#777';
  gT.textAlign = 'left';
  gT.fillText(`${winSec.toFixed(1)}s window`, chartLeft, H - 6);

  const modeText = timeLogFollowLatest ? 'FOLLOW' : 'FOCUS';
  gT.fillStyle = timeLogFollowLatest ? 'red': 'green';
  gT.textAlign = 'right';
  gT.fillText(modeText, chartRight, H - 6);
}


function touchTypeText(s){
  if (!s) return '';
  if (s.long || s.kind === 'long') return 'LONG';
  const c = s.count || 1;
  if (c >= 3) return 'T3+';
  return `T${c}`;
}

function clearSelectedShot(){
  selectedShotId = null;
  frozenSeries = null;
  followLatestTimeLog();
  renderTouchTable();
  drawTimeSeries();
  drawFluxTimeSeries();
  drawPeakTimeline();
  drawStateTimeline();
  drawTimeLog();
}


function getTimeWindowSec(){
  const timeWindowEl = document.getElementById('timeWindow');
  return Number(timeWindowEl?.value || 30);
}

function centerTimeLogAt(t){
  if (!isFinite(t)) return;
  timeLogCenterSec = t;
  timeLogFollowLatest = false;
}

function followLatestTimeLog(){
  timeLogCenterSec = null;
  timeLogFollowLatest = true;
}

function getSelectedShot(){
  if (selectedShotId == null) return null;
  return touchShots.find(s => s.id === selectedShotId) || null;
}
/* 
function captureFocusWindow(shotT){
  const winSec = getTimeWindowSec();
  const start = shotT - winSec / 2;
  const end   = shotT + winSec / 2;

  frozenSeries = tsBuf
    .filter(p => p.t >= start && p.t <= end)
    .map(p => ({ ...p }));
} */

function captureSeriesWindow(centerT, winSec){
  const start = centerT - winSec / 2;
  const end   = centerT + winSec / 2;

  return tsBuf
    .filter(p => p.t >= start && p.t <= end)
    .map(p => ({ ...p }));
}

function finalizeFrozenSeries(nowT){
  for (const s of touchShots) {
    if (s.frozenSeries) continue;
    if (!isFinite(s.freezeReadyAt)) continue;
    if (nowT < s.freezeReadyAt) continue;

    s.frozenSeries = captureSeriesWindow(s.t, getFreezeWindowSec());

    const m = calcShotDecayMetrics(s.frozenSeries);
    s.decayA = m.decayA;
    s.decayM = m.decayM;
    s.energyA = m.energyA;
    s.energyM = m.energyM;
  }

  requestTouchTableRender(); // ←これ
}


function getSelectedFrozenSeries(){
  const s = getSelectedShot();
  if (!s) return null;
  return s.frozenSeries || null;
}

function getFreezeWindowSec(){
  return 30; // 固定
}

function downsampleTimeSeries(src, stepSec = 0.1){
  const out = [];
  let lastT = -Infinity;

  for (const p of src) {
    if ((p.t - lastT) >= stepSec) {
      out.push({ ...p });
      lastT = p.t;
    }
  }
  return out;
}

function buildSessionData(){
  return {
    version: 1,
    savedAt: new Date().toISOString(),
    touchShots: touchShots.map(s => ({ ...s })),
    // tsBufは軽量化して保存
    tsBuf: downsampleTimeSeries(tsBuf, 0.1),
    recAvgA: Array.isArray(recAvgA) ? recAvgA.map(x => ({ ...x })) : [],
    recAvgB: Array.isArray(recAvgB) ? recAvgB.map(x => ({ ...x })) : []  };
}


function saveSessionToFile(){
  const data = buildSessionData();
  const blob = new Blob(
    [JSON.stringify(data, null, 2)],
    { type: 'application/json' }
  );

  const a = document.createElement('a');
  const stamp = new Date().toISOString().replace(/[:.]/g, '-');
  a.href = URL.createObjectURL(blob);
  a.download = `fft_log_${stamp}.json`;
  a.click();
  console.log('session data saved', a.href.toString);
  URL.revokeObjectURL(a.href);
}

function loadSessionFromObject(data){
  if (!data || typeof data !== 'object') {
    throw new Error('loadSessionFromObject: invalid data');
  }

  // 本体クリア
  if (Array.isArray(touchShots)) touchShots.length = 0;
  if (Array.isArray(tsBuf)) tsBuf.length = 0;

  // recAvgA / recAvgB は null の可能性があるので守る
  if (Array.isArray(recAvgA)) recAvgA.length = 0;
  if (Array.isArray(recAvgB)) recAvgB.length = 0;

  // touchShots
  if (Array.isArray(data.touchShots)) {
    for (const s of data.touchShots) {
      touchShots.push({
        ...s,
        // 古い/未完成データ対策
        frozenSeries: Array.isArray(s.frozenSeries) ? s.frozenSeries : null
      });
    }
  }

  // tsBuf
  if (Array.isArray(data.tsBuf)) {
    for (const p of data.tsBuf) {
      tsBuf.push({ ...p });
    }
  }

  // recAvgA
  if (Array.isArray(data.recAvgA) && Array.isArray(recAvgA)) {
    for (const x of data.recAvgA) recAvgA.push({ ...x });
  }

  // recAvgB
  if (Array.isArray(data.recAvgB) && Array.isArray(recAvgB)) {
    for (const x of data.recAvgB) recAvgB.push({ ...x });
  }

  // UI状態
  selectedShotId = null;
  focusedTimeSeries = null;
  isLoadedSessionMode = true;

  if (typeof followLatestTimeLog === 'function') {
    followLatestTimeLog();
  }

  if (typeof renderTouchTable === 'function') renderTouchTable();
  if (typeof drawTimeSeries === 'function') drawTimeSeries();
  if (typeof drawTimeLog === 'function') drawTimeLog();
  if (typeof drawFluxTimeSeries === 'function') drawFluxTimeSeries();
  if (typeof drawPeakTimeline === 'function') drawPeakTimeline();
  if (typeof drawStateTimeline === 'function') drawStateTimeline();
  if (typeof updateBandBars === 'function') updateBandBars();
}

function openSessionFile(file){
  const reader = new FileReader();

  reader.onload = () => {
    try {
      const data = JSON.parse(reader.result);
      console.log('LOAD parsed OK', data);
      loadSessionFromObject(data);
      console.log('LOAD finished OK');
    } catch (e) {
      console.error('LOAD ERROR', e);
      alert("JSON読み込みエラー");
    }
  };

  reader.readAsText(file);
}

function renderTouchTable(){
  if (!touchTableEl) return;
  try {
    console.log('renderTouchTable start', {
      len: touchShots.length,
      touchTableEl,
    });
    if (!touchTableEl) {
      console.warn('touchTableEl is null');
      return;
    }
    
    const rows = [...touchShots].reverse(); // ← フィルタしない

    let html = `
        <table class="touch-table">
          <colgroup>
            <col class="c-id">
            <col class="c-time">
            <col class="c-kind">
            <col class="c-num">
            <col class="c-num">
            <col class="c-num">
            <col class="c-num">
            <col class="c-num">
            <col class="c-num">
            <col class="c-num">
            <col class="c-num">
            <col class="c-num">
            <col class="c-num">
            <col class="c-num">
            <col class="c-attack">
            <col class="c-state">
            <col class="c-attackReason">
            <col class="c-class">
            <col class="c-reason">
            <col class="c-num">
            <col class="c-num">
            <col class="c-num">
            <col class="c-num">
          </colgroup>
          
          <thead>
            <tr class="groupHeader">
            <th rowspan="2">#</th>
            <th rowspan="2">t[s]</th>
            <th rowspan="2">Kind</th>
            <th rowspan="2">Scrape</th>

            <th colspan="2">Peak</th>
            <th colspan="2">Flux</th>
            <th colspan="2">Move</th>
            <th colspan="2">Decay</th>
            <th colspan="2">Energy</th>

            <th colspan="3">Attack</th>
            <th colspan="2">Class</th>
            <th rowspan="2">Impulse</th>
            <th rowspan="2">Suction</th>
            <th rowspan="2">Weed</th>
            <th rowspan="2">Class2</th>

            </tr>

            <tr>
            <th>A</th>
            <th>M</th>

            <th>A</th>
            <th>M</th>

            <th>A</th>
            <th>M</th>

            <th>A</th>
            <th>M</th>

            <th>A</th>
            <th>M</th>

            <th>Score</th>
            <th>State</th>
            <th>Reason</th>
            <th>State</th>
            <th>Reason</th>
            
            </tr>

          </thead>

          <tbody>
    `;

    for (const s of rows) {
      const cls = s.contactClass ?? 'NONE';
      const classReason = 'no rule';
      const atkState = s.attackState ?? 'IDLE';
      const selected = (selectedShotId === s.id) ? ' selected' : '';

      html += `
        <tr class="shot-row${selected}" data-shot-id="${s.id}">
          <td>${s.id}</td>
          <td>${num2(s.t)}</td>
          <td>${s.kind === 'long' ? 'LONG' : `T${s.count || 1}`}</td>
          <td>${num1(s.scrape)}</td>
          <td>${num1(s.peakA)}</td>
          <td>${num1(s.peakM)}</td>
          <td>${num1(s.fluxA)}</td>
          <td>${num1(s.fluxM)}</td>
          <td>${num1(s.peakMoveA)}</td>
          <td>${num1(s.peakMoveM)}</td>
          <td>${num2(s.decayA)}</td>
          <td>${num2(s.decayM)}</td>
          <td>${num1(s.energyA)}</td>
          <td>${num1(s.energyM)}</td>
          <td>${num2(s.attackScore)}</td>
          <td>${escapeHtml(s.attackState || '')}</td>
          <td>${escapeHtml(s.attackReason || '')}</td>
          <td class="cls-${cls}">${cls}</td>
          <td>${s.classReason || ''}</td>
          <td>${(s.impulseScore ?? 0).toFixed(2)}</td>
          <td>${(s.suctionScore ?? 0).toFixed(2)}</td>
          <td>${(s.weedScore ?? 0).toFixed(2)}</td>
          <td>${s.eventClass || ''}</td>
          </tr>
      `;
    }

    html += `
          </tbody>
        </table>
      </div>
    `;

    touchTableEl.innerHTML = html;

    touchTableEl.querySelectorAll('tr[data-shot-id]').forEach(tr => {
      tr.addEventListener('click', () => {
        const id = Number(tr.dataset.shotId);
        if (!Number.isFinite(id)) return;

        selectedShotId = id;
        timeLogFollowLatest = false;

        const sel = getSelectedShot();
        if (sel) timeLogCenterSec = sel.t;

        renderTouchTable();
        drawTimeLog();
      });
    });
  } catch (err) {
    console.error('renderTouchTable error:', err);
  }
}

function resumeLiveMode(){
  isLoadedSessionMode = false;
  selectedShotId = null;
  focusedTimeSeries = null;
  followLatestTimeLog();
  drawTimeSeries();
  drawFluxTimeSeries();
  drawPeakTimeline();
  drawStateTimeline();
  drawTimeLog();
  requestTouchTableRender();
}

function normalizeBandMap(map){
  const total = Math.max(1e-9, sumBands(map));
  const out = {};
  for(const b of BANDS){
    const k = b.key;
    out[k] = (Number(map[k]) || 0) / total;
  }
  return out;
}

function classifyPhase2State(feat){
  const fluxA = Number(feat.fluxA) || 0;
  const fluxM = Number(feat.fluxM) || 0;
  const moveA = Number(feat.peakMoveA) || 0;
  const moveM = Number(feat.peakMoveM) || 0;
  const atk   = Number(feat.attackScore) || 0;
  const scrape = Number(feat.scrape) || 0;

  const fluxMax = Math.max(fluxA, fluxM);
  const fluxSum = fluxA + fluxM;
  const moveSum = moveA + moveM;

  // 1) 強い立ち上がり＋短いイベント寄り
  if (atk >= 0.62 || fluxMax >= 0.18) {
    return 'IMPULSE';
  }

  // 2) 中程度の変化があり、ピーク移動が小さめ → 吸い込み
  if (fluxSum >= 0.05 && scrape < 6 && moveSum < 28) {
    return 'SUCTION';
  }

  // 3) やや長引く / ピーク移動あり / scrape高め → weed
  if ((scrape >= 4 && fluxSum >= 0.02) || moveSum >= 28) {
    return 'WEED';
  }

  return 'IDLE';
}

function pushStateTransition(t, from, to){
  const state = to || 'IDLE';
  const last = stateTransitions[stateTransitions.length - 1];

  if (last && Math.abs((last.t || 0) - t) < 0.08 && last.to === to) {
    return;
  }

  stateTransitions.push({ t, from, to, state });

  if (stateTransitions.length > 400) {
    stateTransitions.shift();
  }
}

//ラベル分類 FISH/BOTTOM/WEED/NONE
function classifyContact(feat){
  const scrape = Number(feat.scrape) || 0;
  const fluxA  = Number(feat.fluxA) || 0;
  const fluxM  = Number(feat.fluxM) || 0;
  const moveA  = Number(feat.peakMoveA) || 0;
  const moveM  = Number(feat.peakMoveM) || 0;
  const peakA  = Number(feat.peakAHz) || 0;
  const peakM  = Number(feat.peakMHz) || 0;
  const attack = Number(feat.attackScore) || 0;

  const fluxSum = fluxA + fluxM;
  const moveSum = moveA + moveM;

  // 魚:
  // 変化が急で、ピークが揺れる
  if ((fluxSum >= 0.4 && moveSum >= 30) || (attack >= 0.7 && moveSum >= 18)) {
    return {
      cls: 'FISH',
      reason: `fish: flux/move or attack/move matched (atk=${attack.toFixed(2)}, flux=${fluxSum.toFixed(1)}, move=${moveSum.toFixed(1)})`
    };
  }

  // 岩・底:
  // scrapeあり、ピークが比較的固定、高周波寄りに張り付きやすい
  if (scrape >= 3 && moveSum < 18 && (peakM >= 180 || peakA >= 120)) {
    return {
      cls: 'BOTTOM',
      reason: `bottom: scrape>=3 & moveSum<18 & highPeak (scr=${scrape.toFixed(1)}, move=${moveSum.toFixed(1)}, A=${peakA.toFixed(1)}, M=${peakM.toFixed(1)})`
    };
  }

  // 草:
  // scrape高め、でもピーク移動は小さめ、だらっと続く
  if (scrape >= 4 && fluxSum < 10 && moveSum < 25) {
    return {
      cls: 'WEED',
      reason: `weed: scrape>=4 & fluxSum<10 & moveSum<25 (scr=${scrape.toFixed(1)}, flux=${fluxSum.toFixed(1)}, move=${moveSum.toFixed(1)})`
    };
  }

  if (attack <= 0) {
    return {
      cls: 'NONE',
      reason: `none: attack low (${attack.toFixed(2)})`
    };
  }

  return {
    cls: 'NONE',
    reason: `none: no rule matched (scr=${scrape.toFixed(1)}, flux=${fluxSum.toFixed(1)}, move=${moveSum.toFixed(1)})`
  };
}


function num1(v){
  const n = Number(v);
  return Number.isFinite(n) ? n.toFixed(1) : '-';
}

function num2(v){
  const n = Number(v);
  return Number.isFinite(n) ? n.toFixed(2) : '-';
}

// === Band scoring ===
function makeBands(){
  const bands = [];

  bands.push({key:'b0',label:'0-40',f0:0,f1:40});
  bands.push({key:'b1',label:'40-80',f0:40,f1:80});
  bands.push({key:'b2',label:'80-100',f0:80,f1:100});

  for(let f=100; f<200; f+=20){
    bands.push({
      key:`b${bands.length}`,
      label:`${f}-${f+20}`,
      f0:f,
      f1:f+20
    });
  }

  bands.push({key:`b${bands.length}`,label:'200-300',f0:200,f1:300});
  bands.push({key:`b${bands.length}`,label:'300+',f0:300,f1:Infinity});

  return bands;
}

function buildBandRows(containerId, prefixBar, prefixTxt, fillClass){
  const root = document.getElementById(containerId);
  if (!root) return;

  root.innerHTML = '';

  for (const b of BANDS) {
    const row = document.createElement('div');
    row.className = 'bandRow';

    row.innerHTML = `
      <div class="bandLabel">${b.label}</div>
      <div class="bandBar">
        <div id="${prefixBar}_${b.key}" class="${fillClass}"></div>
      </div>
      <div id="${prefixTxt}_${b.key}" class="bandVal">0%</div>
    `;

    root.appendChild(row);
  }
}

function bandsToArray(b){
  if (!b) return null;

  if (Array.isArray(b)) return b;

  if (typeof b === 'object') {
    return BANDS.map(x => Number(b?.[x.key] ?? 0));
  }

  return null;
}


function getSeriesFieldValues(series, key){
  if (!Array.isArray(series) || !series.length) return [];

  const out = [];
  for (const p of series) {
    const v = Number(p?.[key]);
    if (isFinite(v)) out.push(v);
  }
  return out;
}

function mean(arr){
  if (!arr || !arr.length) return 0;
  let s = 0;
  for (const v of arr) s += v;
  return s / arr.length;
}

function maxAbs(arr){
  if (!arr || !arr.length) return 0;
  let m = 0;
  for (const v of arr) {
    const a = Math.abs(Number(v) || 0);
    if (a > m) m = a;
  }
  return m;
}

function calcDecayIndex(values){
  if (!values || values.length < 6) return 0;

  const absVals = values.map(v => Math.abs(Number(v) || 0));
  const peak = maxAbs(absVals);
  if (peak <= 1e-9) return 0;

  // 前半ピーク、後半テール平均で減衰を見る
  const half = Math.floor(absVals.length / 2);
  const tail = absVals.slice(half);
  const tailAvg = mean(tail);

  return peak / (tailAvg + 1e-9);
}

function calcEnergyIndex(values){
  if (!values || !values.length) return 0;

  let e = 0;
  for (const v of values) {
    const x = Number(v) || 0;
    e += x * x;
  }
  return e;
}

function calcShotDecayMetrics(series){
  if (!Array.isArray(series) || !series.length) {
    return {
      decayA: 0,
      decayM: 0,
      energyA: 0,
      energyM: 0
    };
  }

  // 今の tsBuf / frozenSeries の実データに合わせる
  const scrapeVals = getSeriesFieldValues(series, 'scrape');
  const fluxAVals  = getSeriesFieldValues(series, 'fluxA');
  const fluxMVals  = getSeriesFieldValues(series, 'fluxM');

  return {
    decayA: calcDecayIndex(fluxAVals),
    decayM: calcDecayIndex(fluxMVals),
    energyA: calcEnergyIndex(fluxAVals),
    energyM: calcEnergyIndex(fluxMVals),
    scrapeEnergy: calcEnergyIndex(scrapeVals)
  };
}

function escapeHtml(str){
  return String(str ?? '')
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#39;');
}

let touchTableDirty = false;
let touchTableRenderTimer = null;
let isTouchTableInteracting = false;

let touchTableWrapEl = null;
let touchTableInteractTimer = null;

window.addEventListener('DOMContentLoaded', () => {
  touchTableEl = document.querySelector('#touchTable');
  touchTableWrapEl = document.querySelector('.touch-table-wrap'); // 外側div

  if (touchTableWrapEl) {
    touchTableWrapEl.addEventListener('scroll', () => {
      isTouchTableInteracting = true;

      clearTimeout(touchTableInteractTimer);
      touchTableInteractTimer = setTimeout(() => {
        isTouchTableInteracting = false;
        if (touchTableDirty) {
          touchTableDirty = false;
          renderTouchTable();
        }
      }, 250);
    });
  }
});

function requestTouchTableRender(delay = 10000){
  touchTableDirty = true;

  if (isTouchTableInteracting) return;
  if (touchTableRenderTimer) return;
  // 行選択中は再描画しない
  if (selectedShotId !== null) return;

  touchTableRenderTimer = setTimeout(() => {
    touchTableRenderTimer = null;
    if (!touchTableDirty || isTouchTableInteracting) return;

    touchTableDirty = false;
    renderTouchTable();
  }, delay);
}

function updateNoiseFloor(feat){
  const a = Number(feat.fluxA) || 0;
  const m = Number(feat.fluxM) || 0;

  // 強イベント中はノイズ更新を弱める
  const strong = (a > noiseFluxA * 3.0) || (m > noiseFluxM * 3.0);
  const alpha = strong ? 0.002 : 0.02;

  noiseFluxA = noiseFluxA * (1 - alpha) + a * alpha;
  noiseFluxM = noiseFluxM * (1 - alpha) + m * alpha;

  noiseFluxA = Math.max(0.005, noiseFluxA);
  noiseFluxM = Math.max(0.005, noiseFluxM);
}


function meanOf(arr, key){
  if (!arr.length) return 0;
  let s = 0;
  for (const x of arr) s += Number(x[key]) || 0;
  return s / arr.length;
}

function varianceOf(arr, key){
  if (arr.length < 2) return 0;
  const mu = meanOf(arr, key);
  let s = 0;
  for (const x of arr) {
    const v = (Number(x[key]) || 0) - mu;
    s += v * v;
  }
  return s / arr.length;
}

function countMicroPeaks(arr, key, threshold){
  let c = 0;
  for (let i = 1; i < arr.length - 1; i++) {
    const a = Number(arr[i - 1][key]) || 0;
    const b = Number(arr[i][key]) || 0;
    const c2 = Number(arr[i + 1][key]) || 0;
    if (b > a && b >= c2 && b >= threshold) c++;
  }
  return c;
}

function findRecoveryTime(series, t0, hitMeanFlux, preMeanFlux){
  const target = preMeanFlux + (hitMeanFlux - preMeanFlux) * 0.35;
  const after = series.filter(p => p.t >= t0 && p.t <= t0 + 1.2);
  for (const p of after) {
    const f = Math.max(Number(p.fluxA) || 0, Number(p.fluxM) || 0);
    if (f <= target) return p.t - t0;
  }
  return 1.2;
}

function analyzeEventWindow(series, t0){
  const pre      = series.filter(p => p.t >= t0 - 0.18 && p.t <  t0 - 0.02);
  const hit      = series.filter(p => p.t >= t0 - 0.02 && p.t <= t0 + 0.08);
  const postS    = series.filter(p => p.t >  t0 + 0.08 && p.t <= t0 + 0.30);
  const postL    = series.filter(p => p.t >  t0 + 0.30 && p.t <= t0 + 1.00);

  const preMeanFlux =
    Math.max(meanOf(pre, 'fluxA'), meanOf(pre, 'fluxM'));

  const hitMeanFlux =
    Math.max(meanOf(hit, 'fluxA'), meanOf(hit, 'fluxM'));

  const postShortMeanFlux =
    Math.max(meanOf(postS, 'fluxA'), meanOf(postS, 'fluxM'));

  const postLongMeanFlux =
    Math.max(meanOf(postL, 'fluxA'), meanOf(postL, 'fluxM'));

  const postFluxVar =
    Math.max(varianceOf(postL, 'fluxA'), varianceOf(postL, 'fluxM'));

  const microThresh =
    Math.max(preMeanFlux * 1.4, Math.max(noiseFluxA, noiseFluxM) * 1.6);

  const postMicroPeakCount =
    Math.max(
      countMicroPeaks(postL, 'fluxA', microThresh),
      countMicroPeaks(postL, 'fluxM', microThresh)
    );

  const scrapePre = meanOf(pre, 'scrape');
  const scrapePostLong = meanOf(postL, 'scrape');

  const scrapeRecoveryTime =
    findRecoveryTime(series, t0, hitMeanFlux, preMeanFlux);

  return {
    preMeanFlux,
    hitMeanFlux,
    postShortMeanFlux,
    postLongMeanFlux,
    postFluxVar,
    postMicroPeakCount,
    scrapePre,
    scrapePostLong,
    scrapeRecoveryTime,
  };
}

function enrichShotScores(shot, series){
  const f = analyzeEventWindow(series, shot.t);
  const s = scoreEventFeatures(f);

  shot.preMeanFlux = f.preMeanFlux;
  shot.hitMeanFlux = f.hitMeanFlux;
  shot.postShortMeanFlux = f.postShortMeanFlux;
  shot.postLongMeanFlux = f.postLongMeanFlux;
  shot.postFluxVar = f.postFluxVar;
  shot.postMicroPeakCount = f.postMicroPeakCount;
  shot.scrapeRecoveryTime = f.scrapeRecoveryTime;

  shot.impulseScore = s.impulseScore;
  shot.suctionScore = s.suctionScore;
  shot.weedScore = s.weedScore;
  shot.eventClass = s.eventClass;
}
function calcMDI(buf) {
  if (buf.length < 5) return 0;

  let sum = 0;
  for (let i = 1; i < buf.length; i++) {
    sum += Math.abs(buf[i] - buf[i-1]);
  }

  return sum / (buf.length - 1);
}


function calcPeakDensity(topPeaksA, topPeaksM) {
  const all = [];

  (topPeaksA || []).forEach(p => {
    if (p && p.hz > 0) all.push(p.hz);
  });
  (topPeaksM || []).forEach(p => {
    if (p && p.hz > 0) all.push(p.hz);
  });

  if (all.length === 0) return 0;

  const binSize = 20; // ←ここ変えると解像度変わる
  const bins = {};

  all.forEach(hz => {
    const b = Math.floor(hz / binSize);
    bins[b] = (bins[b] || 0) + 1;
  });

  let maxCount = 0;
  Object.values(bins).forEach(c => {
    if (c > maxCount) maxCount = c;
  });

  return maxCount / all.length; // 0〜1
}



function calcRecentMeanDensity(series, sec = 2.0){
  if (!Array.isArray(series) || !series.length) return 0;

  const t1 = series[series.length - 1].t;
  const recent = series.filter(p => (t1 - p.t) <= sec);

  if (!recent.length) return 0;

  let sum = 0;
  let n = 0;
  for (const p of recent) {
    const d = Number(p.density);
    if (isFinite(d)) {
      sum += d;
      n++;
    }
  }
  return n ? (sum / n) : 0;
}