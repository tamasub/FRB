(() => {
  'use strict';

  const $ = (id) => document.getElementById(id);

  const state = {
    left:  { name: '', raw: null, tsBuf: [], pianoRoll: [], offsetMs: 0 },
    right: { name: '', raw: null, tsBuf: [], pianoRoll: [], offsetMs: 0 },
    bandScale: '80000',
  };

  const BANDS_INVESTIGATE = [
    { key:'b0',   label:'20-40',    f0:20,  f1:40  },
    { key:'b1',   label:'40-60',    f0:40,  f1:60  },
    { key:'b2',   label:'60-80',    f0:60,  f1:80  },
    { key:'b2_5', label:'80-100',   f0:80,  f1:100 },
    { key:'b3',   label:'100-120',  f0:100, f1:120 },
    { key:'b4',   label:'120-160',  f0:120, f1:160 },
    { key:'b4_5', label:'160-220',  f0:160, f1:220 },
    { key:'b5',   label:'220-240',  f0:220, f1:240 },
    { key:'b6',   label:'240-280',  f0:240, f1:280 },
  ];

  const BANDS_INVESTIGATE_LEGEND = [
    ['b0',   '20-40Hz'],
    ['b1',   '40-60Hz'],
    ['b2',   '60-80Hz'],
    ['b2_5', '80-100Hz'],
    ['b3',   '100-120Hz'],
    ['b4',   '120-160Hz'],
    ['b4_5', '160-220Hz'],
    ['b5',   '220-240Hz'],
    ['b6',   '240-280Hz'],
  ];

  const BAND_COLORS_INVESTIGATE = [
    '#283593', '#1565c0', '#26c6da', '#4dd0e1', '#43a047',
    '#c0ca33', '#d4e157', '#fb8c00', '#e53935'
  ];

  const PIANO = {
    midiMin: 24,
    midiMax: 84,
    guideNotes: [24, 36, 48, 60, 72, 84],
    fixedColorMax: 8000,
  };

  // Compare view layout baseline.
  // Keep every plot area's left and right edge identical across all five views.
  // Values are CSS pixels; px() converts them to the actual canvas pixel size.
  const PLOT_LEFT_CSS = 78;
  const PLOT_RIGHT_CSS = 58;
  // Piano Roll だけ右端が伸びて見えないよう、他チャートと同じ右余白に揃える。
  const PIANO_RIGHT_CSS = PLOT_RIGHT_CSS;
  const px = (v) => v * (window.devicePixelRatio || 1);

  function normalizeSeries(tsBuf) {
    const arr = Array.isArray(tsBuf) ? tsBuf.filter(Boolean).map(p => ({ ...p })) : [];
    if (!arr.length) return [];
    const t0 = Number(arr[0].t) || 0;
    return arr.map(p => ({ ...p, t: (Number(p.t) || 0) - t0 }));
  }

  function normalizePiano(frames) {
    const arr = Array.isArray(frames) ? frames.filter(Boolean).map(fr => ({
      ...fr,
      melody: fr?.melody ? { ...fr.melody } : null,
      notes: Array.isArray(fr?.notes) ? fr.notes.map(n => ({ ...n })) : []
    })) : [];
    if (!arr.length) return [];
    const t0 = Number(arr[0].t) || 0;
    return arr.map(fr => ({ ...fr, t: (Number(fr.t) || 0) - t0 }));
  }

  function loadSession(slot, data, name) {
    const target = state[slot];
    target.name = name || '';
    target.raw = data;
    target.tsBuf = normalizeSeries(data?.tsBuf || []);
    target.pianoRoll = normalizePiano(data?.pianoRoll || []);
    target.offsetMs = 0;
    updateStatus(slot);
    renderAll();
  }

  function updateStatus(slot) {
    const s = state[slot];
    const el = $(slot + 'Status');
    if (!el) return;
    const memo = s.raw?.experiment?.memo || s.raw?.experimentMemo || '';
    el.textContent = s.raw
      ? `${s.name || 'loaded'} / ts:${s.tsBuf.length} / piano:${s.pianoRoll.length}${memo ? ' / ' + memo : ''}`
      : '未読込';
  }

  function readFile(slot, file) {
    if (!file) return;
    const reader = new FileReader();
    reader.onload = () => {
      try {
        const data = JSON.parse(String(reader.result || ''));
        loadSession(slot, data, file.name);
      } catch (e) {
        console.error(e);
        alert(`${slot} JSON読み込みエラー`);
      }
    };
    reader.readAsText(file);
  }

  function setupFileInputs() {
    $('leftFile')?.addEventListener('change', e => readFile('left', e.target.files?.[0]));
    $('rightFile')?.addEventListener('change', e => readFile('right', e.target.files?.[0]));
    $('bandScale')?.addEventListener('change', e => {
      state.bandScale = String(e.target.value || '80000');
      updateScaleStatus();
      renderAll();
    });
  }

  function updateScaleStatus() {
    const el = $('scaleStatus');
    if (!el) return;
    const max = getBandScaleMax();
    el.textContent = state.bandScale === 'auto'
      ? `Auto shared / Max ${Math.round(max)}`
      : `Fixed ${Math.round(max / 1000)}k`;
  }

  function resizeCanvas(canvas) {
    if (!canvas) return;

    // IMPORTANT:
    // Do not read canvas.getAttribute('height') after resizing.
    // Setting canvas.height updates the DOM attribute, so repeated renders would
    // change the CSS aspect ratio and the whole Compare view would shrink/grow.
    // Keep the original CSS height separately and use it as the fixed display height.
    if (!canvas.dataset.cssHeight) {
      canvas.dataset.cssHeight = canvas.getAttribute('height') || String(Math.round(canvas.getBoundingClientRect().height || 160));
    }

    const dpr = window.devicePixelRatio || 1;
    const cssH = Number(canvas.dataset.cssHeight) || 160;
    canvas.style.height = `${cssH}px`;

    const rect = canvas.getBoundingClientRect();
    const cssW = Math.max(320, Math.round(rect.width || canvas.clientWidth || 640));
    const w = Math.max(1, Math.round(cssW * dpr));
    const h = Math.max(1, Math.round(cssH * dpr));
    if (canvas.width !== w || canvas.height !== h) {
      canvas.width = w;
      canvas.height = h;
    }
  }

  function clearChart(ctx, W, H, fill = '#fcfcfc') {
    ctx.clearRect(0, 0, W, H);
    ctx.fillStyle = fill;
    ctx.fillRect(0, 0, W, H);
  }

  function drawNoData(ctx, text, left = px(PLOT_LEFT_CSS), top = px(18)) {
    ctx.fillStyle = '#999';
    ctx.font = `${12 * (window.devicePixelRatio || 1)}px sans-serif`;
    ctx.textAlign = 'left';
    ctx.textBaseline = 'top';
    ctx.fillText(text, left + 10, top + 18);
  }

  function getTimeBounds(series) {
    if (!Array.isArray(series) || series.length < 2) return { start: 0, end: 1 };
    const start = Number(series[0].t) || 0;
    const end = Number(series[series.length - 1].t) || start + 1;
    return { start, end: Math.max(start + 1e-6, end) };
  }

  function getBandScaleMax() {
    if (state.bandScale !== 'auto') return Math.max(1e-9, Number(state.bandScale) || 80000);
    let max = 1e-9;
    for (const side of [state.left, state.right]) {
      for (const p of side.tsBuf) {
        const map = p.bandAInvestigate || {};
        for (const band of BANDS_INVESTIGATE) max = Math.max(max, Number(map[band.key]) || 0);
      }
    }
    return Math.max(1, max * 1.05);
  }

  function setupAxes(ctx, W, H, opt = {}) {
    const ml = px(opt.ml ?? PLOT_LEFT_CSS);
    const mr = px(opt.mr ?? PLOT_RIGHT_CSS);
    const mt = px(opt.mt ?? 18);
    const mb = px(opt.mb ?? 28);
    const chart = {
      left: ml,
      right: W - mr,
      top: mt,
      bottom: H - mb,
      width: W - ml - mr,
      height: H - mt - mb,
    };
    ctx.strokeStyle = '#d4d4d4';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(chart.left, chart.top);
    ctx.lineTo(chart.left, chart.bottom);
    ctx.lineTo(chart.right, chart.bottom);
    ctx.stroke();
    return chart;
  }

  function drawGrid(ctx, chart, ticks, labelFn) {
    ctx.strokeStyle = '#ececec';
    ctx.lineWidth = 1;
    ctx.font = `${11 * (window.devicePixelRatio || 1)}px sans-serif`;
    ctx.textAlign = 'right';
    ctx.textBaseline = 'middle';
    for (let i = 0; i < ticks.length; i++) {
      const y = chart.top + chart.height * i / Math.max(1, ticks.length - 1);
      ctx.beginPath();
      ctx.moveTo(chart.left, y);
      ctx.lineTo(chart.right, y);
      ctx.stroke();
      ctx.fillStyle = '#666';
      ctx.fillText(labelFn(i, ticks.length), chart.left - 8, y);
    }
  }

  function drawBandTimeline(canvas, side) {
    resizeCanvas(canvas);
    const ctx = canvas.getContext('2d');
    const W = canvas.width, H = canvas.height;
    clearChart(ctx, W, H);
    const chart = setupAxes(ctx, W, H, { ml: PLOT_LEFT_CSS, mr: PLOT_RIGHT_CSS, mt: 18, mb: 28 });
    const series = side.tsBuf;
    if (!series || series.length < 2) return drawNoData(ctx, 'no band timeline investigate');

    const { start, end } = getTimeBounds(series);
    const globalMax = getBandScaleMax();
    const xMap = (t) => chart.left + ((t - start) / (end - start)) * chart.width;
    const yMap = (v) => chart.bottom - Math.max(0, Math.min(100, v)) / 100 * chart.height;
    drawGrid(ctx, chart, [0,1,2,3,4,5], i => String(Math.round(100 - (100 * i / 5))));

    for (let b = 0; b < BANDS_INVESTIGATE.length; b++) {
      const band = BANDS_INVESTIGATE[b];
      ctx.save();
      ctx.strokeStyle = BAND_COLORS_INVESTIGATE[b] || '#333';
      ctx.lineWidth = 2;
      ctx.beginPath();
      let started = false;
      for (const p of series) {
        const raw = Number(p.bandAInvestigate?.[band.key]) || 0;
        const x = xMap(Number(p.t) || 0);
        const y = yMap((raw / globalMax) * 100);
        if (!started) { ctx.moveTo(x, y); started = true; }
        else ctx.lineTo(x, y);
      }
      if (started) ctx.stroke();
      ctx.restore();
    }

    let lx = chart.left + 8, ly = chart.top + 8;
    ctx.font = `${12 * (window.devicePixelRatio || 1)}px sans-serif`;
    ctx.textAlign = 'left'; ctx.textBaseline = 'top';
    for (let i = 0; i < BANDS_INVESTIGATE_LEGEND.length; i++) {
      const [key, label] = BANDS_INVESTIGATE_LEGEND[i];
      const color = BAND_COLORS_INVESTIGATE[i] || '#333';
      const tw = ctx.measureText(label).width;
      if (lx + 16 + tw + 16 > chart.right - 8) { lx = chart.left + 8; ly += 18 * (window.devicePixelRatio || 1); }
      ctx.fillStyle = color; ctx.fillRect(lx, ly + 4, 12 * (window.devicePixelRatio || 1), 3 * (window.devicePixelRatio || 1));
      ctx.fillStyle = '#333'; ctx.fillText(label, lx + 16 * (window.devicePixelRatio || 1), ly);
      lx += 16 * (window.devicePixelRatio || 1) + tw + 16 * (window.devicePixelRatio || 1);
    }
    drawFooter(ctx, chart, H, `Band Timeline Investigate / ${state.bandScale === 'auto' ? 'Auto shared' : 'Fixed ' + Math.round(globalMax)}`);
  }

  function drawFlux(canvas, side) {
    resizeCanvas(canvas);
    const ctx = canvas.getContext('2d');
    const W = canvas.width, H = canvas.height;
    clearChart(ctx, W, H);
    const chart = setupAxes(ctx, W, H, { ml: PLOT_LEFT_CSS, mr: PLOT_RIGHT_CSS, mt: 14, mb: 22 });
    const series = side.tsBuf;
    if (!series || series.length < 2) return drawNoData(ctx, 'no flux');
    const { start, end } = getTimeBounds(series);
    const xMap = (t) => chart.left + ((t - start) / (end - start)) * chart.width;
    let vmax = 0.12;
    for (const p of series) vmax = Math.max(vmax, Number(p.fluxA) || 0, Number(p.fluxM) || 0);
    vmax *= 1.15;
    const yMap = (v) => chart.bottom - Math.max(0, Math.min(vmax, v || 0)) / vmax * chart.height;
    drawGrid(ctx, chart, [0,1,2,3,4], i => (vmax - vmax * i / 4).toFixed(2));
    drawLine(ctx, series, p => Number(p.fluxA) || 0, xMap, yMap, '#8e24aa');
    drawLine(ctx, series, p => Number(p.fluxM) || 0, xMap, yMap, '#fb8c00');
    ctx.font = `${11 * (window.devicePixelRatio || 1)}px sans-serif`;
    ctx.textAlign = 'left'; ctx.textBaseline = 'top';
    const last = series[series.length - 1] || {};
    ctx.fillStyle = '#8e24aa'; ctx.fillText(`A:${(Number(last.fluxA) || 0).toFixed(3)}`, chart.left + 8, chart.top + 6);
    ctx.fillStyle = '#fb8c00'; ctx.fillText(`M:${(Number(last.fluxM) || 0).toFixed(3)}`, chart.left + 90 * (window.devicePixelRatio || 1), chart.top + 6);
    drawFooter(ctx, chart, H, 'Flux (A/M)');
  }

  function drawTriangle(canvas, side) {
    resizeCanvas(canvas);
    const ctx = canvas.getContext('2d');
    const W = canvas.width, H = canvas.height;
    clearChart(ctx, W, H);
    const chart = setupAxes(ctx, W, H, { ml: PLOT_LEFT_CSS, mr: PLOT_RIGHT_CSS, mt: 14, mb: 22 });
    const series = side.tsBuf;
    if (!series || series.length < 2) return drawNoData(ctx, 'no triangle motion');
    const { start, end } = getTimeBounds(series);
    const xMap = (t) => chart.left + ((t - start) / (end - start)) * chart.width;
    let vmax = 1e-9;
    for (const p of series) vmax = Math.max(vmax, Number(p.tingleMotion) || 0);
    vmax *= 1.10;
    const yMap = (v) => chart.bottom - Math.max(0, Math.min(vmax, v || 0)) / vmax * chart.height;
    drawGrid(ctx, chart, [0,1,2,3,4], i => (vmax - vmax * i / 4).toFixed(3));
    drawLine(ctx, series, p => Number(p.tingleMotion) || 0, xMap, yMap, '#8e24aa');
    drawFooter(ctx, chart, H, 'Triangle Motion / Tingle Motion');
  }

  function drawBridge(canvas, side) {
    resizeCanvas(canvas);
    const ctx = canvas.getContext('2d');
    const W = canvas.width, H = canvas.height;
    clearChart(ctx, W, H);
    const chart = setupAxes(ctx, W, H, { ml: PLOT_LEFT_CSS, mr: PLOT_RIGHT_CSS, mt: 18, mb: 24 });
    const series = side.tsBuf;
    if (!series || series.length < 2) return drawNoData(ctx, 'no bridge score');
    const { start, end } = getTimeBounds(series);
    const xMap = (t) => chart.left + ((t - start) / (end - start)) * chart.width;
    const yMap = (v) => chart.bottom - Math.max(0, Math.min(1, v || 0)) * chart.height;
    drawGrid(ctx, chart, [0,1,2,3,4], i => (1 - i / 4).toFixed(2));
    drawLine(ctx, series, p => Number(p.stairError) || 0, xMap, yMap, '#d81b60');
    drawFooter(ctx, chart, H, 'BridgeScore (0.00-1.00, Zoomなし)');
  }

  function drawLine(ctx, series, valueFn, xMap, yMap, color) {
    ctx.save();
    ctx.strokeStyle = color;
    ctx.lineWidth = 2 * (window.devicePixelRatio || 1);
    ctx.beginPath();
    let started = false;
    for (const p of series) {
      const x = xMap(Number(p.t) || 0);
      const y = yMap(valueFn(p));
      if (!started) { ctx.moveTo(x, y); started = true; }
      else ctx.lineTo(x, y);
    }
    if (started) ctx.stroke();
    ctx.restore();
  }

  function drawFooter(ctx, chart, H, text) {
    ctx.fillStyle = '#777';
    ctx.font = `${11 * (window.devicePixelRatio || 1)}px sans-serif`;
    ctx.textAlign = 'left';
    ctx.textBaseline = 'alphabetic';
    ctx.fillText(text, chart.left, H - 6 * (window.devicePixelRatio || 1));
  }

  function midiToHz(midi) { return 440 * Math.pow(2, (midi - 69) / 12); }
  function midiToNoteName(midi) {
    const names = ['C','C#','D','D#','E','F','F#','G','G#','A','A#','B'];
    const m = Math.round(Number(midi) || 0);
    return `${names[((m % 12) + 12) % 12]}${Math.floor(m / 12) - 1}`;
  }
  function pianoY(midi, top, bottom) {
    return top + (PIANO.midiMax - midi) / (PIANO.midiMax - PIANO.midiMin) * (bottom - top);
  }

  function drawPianoRoll(canvas, side) {
    resizeCanvas(canvas);
    const ctx = canvas.getContext('2d');
    const W = canvas.width, H = canvas.height;
    const frames = side.pianoRoll || [];
    const left = px(PLOT_LEFT_CSS);
    const right = W - px(PIANO_RIGHT_CSS);
    const top = px(12);
    const bottom = H - px(24);
    const plotW = Math.max(1, right - left);

    // 右端の見た目を他グラフと揃えるため、canvas全体は薄背景、
    // Piano Roll本体だけを chart.right まで黒背景で塗る。
    // これで右余白の黒い余りが「はみ出し」に見えない。
    clearChart(ctx, W, H, '#fbfdff');
    ctx.fillStyle = '#101418';
    ctx.fillRect(0, 0, right, H);

    ctx.save();
    ctx.lineWidth = 1;
    ctx.strokeStyle = 'rgba(255,255,255,0.055)';
    for (let midi = PIANO.midiMin; midi <= PIANO.midiMax; midi++) {
      const y = pianoY(midi, top, bottom);
      ctx.beginPath(); ctx.moveTo(left, y); ctx.lineTo(right, y); ctx.stroke();
    }

    ctx.font = `${10 * (window.devicePixelRatio || 1)}px monospace`;
    ctx.textAlign = 'left'; ctx.textBaseline = 'middle';
    for (const midi of PIANO.guideNotes) {
      const y = pianoY(midi, top, bottom);
      ctx.strokeStyle = 'rgba(255,255,255,0.22)';
      ctx.beginPath(); ctx.moveTo(left, y); ctx.lineTo(right, y); ctx.stroke();
      ctx.fillStyle = 'rgba(235,245,255,0.88)';
      ctx.fillText(`${midiToNoteName(midi)} (${Math.round(midiToHz(midi))}Hz)`, px(6), y);
    }
    ctx.fillStyle = 'rgba(235,245,255,0.62)';
    ctx.font = `${9 * (window.devicePixelRatio || 1)}px sans-serif`;
    ctx.textAlign = 'left'; ctx.textBaseline = 'top';
    ctx.fillText('note + Hz labels', left + px(6), top + px(4));
    ctx.strokeStyle = 'rgba(255,255,255,0.18)';
    ctx.strokeRect(left, top, plotW, bottom - top);

    if (!frames.length) {
      ctx.fillStyle = 'rgba(235,245,255,0.72)';
      ctx.font = `${12 * (window.devicePixelRatio || 1)}px sans-serif`;
      ctx.fillText('no piano roll in log', left + 10, top + 22);
      ctx.restore();
      return;
    }

    const t0 = Number(frames[0]?.t) || 0;
    const t1 = Number(frames[frames.length - 1]?.t) || (t0 + frames.length);
    const spanT = Math.max(1e-6, t1 - t0);
    let noteCount = 0;
    for (let i = 0; i < frames.length; i++) {
      const fr = frames[i];
      const t = Number(fr?.t);
      const x = Number.isFinite(t) ? left + ((t - t0) / spanT) * plotW : left + (i / Math.max(1, frames.length - 1)) * plotW;
      const next = frames[i + 1];
      const nt = Number(next?.t);
      const nx = Number.isFinite(t) && Number.isFinite(nt) ? left + ((nt - t0) / spanT) * plotW : x + Math.max(2, plotW / Math.max(1, frames.length));
      const rawW = Math.max(2 * (window.devicePixelRatio || 1), Math.min(10 * (window.devicePixelRatio || 1), nx - x));
      const w = Math.max(0, Math.min(rawW, right - x));
      if (w <= 0) continue;

      for (const n of (fr.notes || [])) {
        const midi = Number(n?.midi);
        if (!Number.isFinite(midi) || midi < PIANO.midiMin || midi > PIANO.midiMax) continue;
        const y = pianoY(midi, top, bottom);
        const v = Math.max(0, Math.min(1, (Number(n?.mag) || 0) / PIANO.fixedColorMax));
        const h = (2 + v * 5) * (window.devicePixelRatio || 1);
        const alpha = 0.35 + v * 0.55;
        ctx.fillStyle = `rgba(0, 255, 204, ${alpha.toFixed(3)})`;
        ctx.fillRect(x, y - h / 2, w, h);
        noteCount++;
      }
      if (fr.melody) {
        const midi = Number(fr.melody?.midi);
        if (Number.isFinite(midi) && midi >= PIANO.midiMin && midi <= PIANO.midiMax) {
          const y = pianoY(midi, top, bottom);
          const v = Math.max(0, Math.min(1, (Number(fr.melody?.mag) || 0) / PIANO.fixedColorMax));
          const h = (3 + v * 6) * (window.devicePixelRatio || 1);
          const alpha = 0.45 + v * 0.50;
          ctx.fillStyle = `rgba(255, 224, 102, ${alpha.toFixed(3)})`;
          ctx.fillRect(x, y - h / 2, w, h);
          noteCount++;
        }
      }
    }
    ctx.fillStyle = 'rgba(235,245,255,0.72)';
    ctx.font = `${11 * (window.devicePixelRatio || 1)}px sans-serif`;
    ctx.textAlign = 'right'; ctx.textBaseline = 'alphabetic';
    ctx.fillText(`${frames.length} frames / ${noteCount} notes / Color Fixed 8k`, right, H - 6 * (window.devicePixelRatio || 1));
    ctx.restore();
  }

  function renderSide(slot) {
    const side = state[slot];
    drawBandTimeline($(slot + 'Band'), side);
    drawPianoRoll($(slot + 'Piano'), side);
    drawFlux($(slot + 'Flux'), side);
    drawTriangle($(slot + 'Triangle'), side);
    drawBridge($(slot + 'Bridge'), side);
  }

  function renderAll() {
    updateScaleStatus();
    renderSide('left');
    renderSide('right');
  }

  async function loadFromUrlParam(slot, url) {
    if (!url) return;
    try {
      const res = await fetch(url);
      if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
      const data = await res.json();
      loadSession(slot, data, url.split('/').pop() || url);
    } catch (e) {
      console.error(e);
      const el = $(slot + 'Status');
      if (el) el.textContent = `URL読込失敗: ${url}`;
    }
  }

  function setupUrlParams() {
    const params = new URLSearchParams(location.search);
    loadFromUrlParam('left', params.get('left'));
    loadFromUrlParam('right', params.get('right'));
  }

  window.addEventListener('resize', renderAll);
  document.addEventListener('DOMContentLoaded', () => {
    setupFileInputs();
    updateScaleStatus();
    renderAll();
    setupUrlParams();
  });
})();
