(() => {
  'use strict';

  const $ = (id) => document.getElementById(id);

  const state = {
    reference: { name: '', raw: null, tsBuf: [], pianoRoll: [], offsetMs: 0 },
    left:      { name: '', raw: null, tsBuf: [], pianoRoll: [], offsetMs: 0 },
    right:     { name: '', raw: null, tsBuf: [], pianoRoll: [], offsetMs: 0 },
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

  const BridgeMetrics = window.FRBBridgeMetrics;

  function getBridgeDerived(side) {
    return BridgeMetrics ? BridgeMetrics.deriveSeries(side?.tsBuf || []) : [];
  }

  function getBridgeLegacyScore(frame) {
    if (BridgeMetrics) return BridgeMetrics.getLegacyScoreFromFrame(frame);
    return Number(frame?.bridgeLegacyScore ?? frame?.stairError) || 0;
  }

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
    $('referenceFile')?.addEventListener('change', e => readFile('reference', e.target.files?.[0]));
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

  let hoverTooltipEl = null;

  function ensureHoverTooltip(){
    if (hoverTooltipEl) return hoverTooltipEl;
    const el = document.createElement('div');
    el.className = 'frb-chart-tooltip';
    document.body.appendChild(el);
    hoverTooltipEl = el;
    return el;
  }

  function hideHoverTooltip(){
    if (hoverTooltipEl) hoverTooltipEl.style.display = 'none';
  }

  function nearestByX(points, xValue, key = 'x'){
    const arr = Array.isArray(points) ? points : [];
    let best = null, bestDist = Infinity;
    for (const p of arr) {
      const v = Number(p?.[key]);
      if (!Number.isFinite(v)) continue;
      const d = Math.abs(v - xValue);
      if (d < bestDist) { best = p; bestDist = d; }
    }
    return best;
  }

  function setCanvasFrequencyProbe(canvas, meta){
    if (!canvas) return;
    canvas._frbHoverMeta = meta || null;
    canvas.classList.toggle('frb-hover-probe', !!meta);
    if (canvas.dataset.frbHoverBound === '1') return;
    canvas.dataset.frbHoverBound = '1';

    canvas.addEventListener('mouseleave', hideHoverTooltip);
    canvas.addEventListener('mousemove', ev => {
      const m = canvas._frbHoverMeta;
      if (!m || typeof m.format !== 'function') return hideHoverTooltip();

      const rect = canvas.getBoundingClientRect();
      if (!rect.width || !canvas.width) return hideHoverTooltip();
      const pxX = (ev.clientX - rect.left) * canvas.width / rect.width;
      const chart = m.chart;
      if (!chart || pxX < chart.left || pxX > chart.right) return hideHoverTooltip();

      const r = (pxX - chart.left) / Math.max(1e-9, chart.width);
      const xValue = Number(m.xMin) + r * (Number(m.xMax) - Number(m.xMin));
      const html = m.format(xValue);
      if (!html) return hideHoverTooltip();

      const tip = ensureHoverTooltip();
      tip.innerHTML = html;
      tip.style.display = 'block';
      const pad = 12;
      let left = ev.clientX + 14;
      let top = ev.clientY + 14;
      const tw = tip.offsetWidth || 220;
      const th = tip.offsetHeight || 60;
      if (left + tw + pad > window.innerWidth) left = ev.clientX - tw - 14;
      if (top + th + pad > window.innerHeight) top = ev.clientY - th - 14;
      tip.style.left = `${Math.max(pad, left)}px`;
      tip.style.top = `${Math.max(pad, top)}px`;
    });
  }

  function fmtHz(v){
    const n = Number(v);
    return Number.isFinite(n) && n > 0 ? `${n.toFixed(1)} Hz` : '-';
  }

  function fmtAmp(v){
    const n = Number(v);
    return Number.isFinite(n) ? formatCompactNumber(n) : '-';
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

  function formatCompactNumber(v) {
    const n = Number(v) || 0;
    if (Math.abs(n) >= 1000000) return `${Math.round(n / 1000000)}M`;
    if (Math.abs(n) >= 1000) return `${Math.round(n / 1000)}k`;
    return `${Math.round(n)}`;
  }

  function drawSweepLegend(ctx, chart, defs) {
    ctx.font = `${10 * (window.devicePixelRatio || 1)}px sans-serif`;
    ctx.textAlign = 'left';
    ctx.textBaseline = 'top';
    let x = chart.left + px(8);
    const y = chart.top + px(4);
    for (const [color, label] of defs) {
      ctx.fillStyle = color;
      ctx.fillRect(x, y + px(4), px(12), px(3));
      ctx.fillStyle = '#333';
      ctx.fillText(label, x + px(16), y);
      x += ctx.measureText(label).width + px(34);
    }
  }

  function drawSweepHz(canvas, side) {
    resizeCanvas(canvas);
    const ctx = canvas.getContext('2d');
    const W = canvas.width, H = canvas.height;
    clearChart(ctx, W, H);
    const chart = setupAxes(ctx, W, H, { ml: PLOT_LEFT_CSS, mr: PLOT_RIGHT_CSS, mt: 16, mb: 24 });
    const series = side.tsBuf || [];
    if (series.length < 2) return drawNoData(ctx, 'no sweep trace Hz');

    const hasSweep = series.some(p =>
      (Number(p.inputHz) || 0) > 0 ||
      (Number(p.peakAHz) || 0) > 0 ||
      (Number(p.melodyHz) || 0) > 0 ||
      (Number(p.melodyCandidateHz) || 0) > 0
    );
    if (!hasSweep) return drawNoData(ctx, 'sweep trace fields unavailable');

    const { start, end } = getTimeBounds(series);
    const xMap = t => chart.left + ((t - start) / (end - start)) * chart.width;
    const hzMax = 300;
    const yMap = hz => chart.bottom - Math.max(0, Math.min(hzMax, Number(hz) || 0)) / hzMax * chart.height;

    drawGrid(ctx, chart, [0,1,2,3,4,5,6], i => String(Math.round(hzMax - hzMax * i / 6)));

    function trace(key, color, width = 2, dashed = false) {
      ctx.save();
      ctx.strokeStyle = color;
      ctx.lineWidth = width * (window.devicePixelRatio || 1);
      ctx.setLineDash(dashed ? [px(6), px(4)] : []);
      ctx.beginPath();
      let started = false;
      for (const p of series) {
        const v = Number(p[key]) || 0;
        if (v <= 0) continue;
        const x = xMap(Number(p.t) || 0);
        const y = yMap(v);
        if (!started) { ctx.moveTo(x, y); started = true; }
        else ctx.lineTo(x, y);
      }
      if (started) ctx.stroke();
      ctx.restore();
    }

    trace('inputHz', '#777777', 1.8, true);
    trace('peakAHz', '#1e88e5', 1.8, false);
    trace('melodyHz', '#fbc02d', 2.1, false);
    trace('melodyCandidateHz', '#26c6da', 1.6, true);

    drawSweepLegend(ctx, chart, [
      ['#777777', 'Input Hz'],
      ['#1e88e5', 'PeakA Hz'],
      ['#fbc02d', 'Melody Hz'],
      ['#26c6da', 'Energy Candidate Hz'],
    ]);
    drawFooter(ctx, chart, H, 'Sweep Trace Hz / Y 0-300Hz');
    setCanvasFrequencyProbe(canvas, {
      chart,
      xMin: start,
      xMax: end,
      format: tCursor => {
        const p = nearestByX(series.map(x => ({ ...x, x: Number(x.t) || 0 })), tCursor);
        if (!p) return '';
        return `<div class="hz">Input ${fmtHz(p.inputHz)}</div>` +
          `<div>PeakA ${fmtHz(p.peakAHz)} / Melody ${fmtHz(p.melodyHz)}</div>` +
          `<div>Candidate ${fmtHz(p.melodyCandidateHz)}</div>` +
          `<div class="sub">t ${Number(p.t).toFixed(2)} s</div>`;
      }
    });
  }

  function getSharedSweepEnergyMax() {
    let rawMax = 0;
    for (const side of [state.left, state.right]) {
      for (const p of side.tsBuf || []) {
        rawMax = Math.max(
          rawMax,
          Number(p.peakAEnergy) || 0,
          Number(p.inputResponseMagnitudeA) || 0,
          Number(p.melodyAmp) || 0,
          Number(p.melodyCandidateAmp) || 0
        );
      }
    }
    return Math.max(1, niceAxisMax(rawMax * 1.02));
  }

  function drawSweepEnergy(canvas, side) {
    resizeCanvas(canvas);
    const ctx = canvas.getContext('2d');
    const W = canvas.width, H = canvas.height;
    clearChart(ctx, W, H);
    const chart = setupAxes(ctx, W, H, { ml: PLOT_LEFT_CSS, mr: PLOT_RIGHT_CSS, mt: 16, mb: 24 });
    const series = side.tsBuf || [];
    if (series.length < 2) return drawNoData(ctx, 'no sweep trace energy');

    const hasEnergy = series.some(p =>
      (Number(p.peakAEnergy) || 0) > 0 ||
      (Number(p.inputResponseMagnitudeA) || 0) > 0 ||
      (Number(p.melodyAmp) || 0) > 0 ||
      (Number(p.melodyCandidateAmp) || 0) > 0
    );
    if (!hasEnergy) return drawNoData(ctx, 'sweep energy fields unavailable');

    const { start, end } = getTimeBounds(series);
    const xMap = t => chart.left + ((t - start) / (end - start)) * chart.width;
    const vmax = getSharedSweepEnergyMax();
    const yMap = v => chart.bottom - Math.max(0, Math.min(vmax, Number(v) || 0)) / vmax * chart.height;
    drawGrid(ctx, chart, [0,1,2,3,4], i => `${Math.round(100 - 100 * i / 4)}%`);

    drawLine(ctx, series, p => Number(p.peakAEnergy) || 0, xMap, yMap, '#8e24aa');
    drawLine(ctx, series, p => Number(p.inputResponseMagnitudeA) || 0, xMap, yMap, '#1565c0');
    drawLine(ctx, series, p => Number(p.melodyAmp) || 0, xMap, yMap, '#43a047');
    drawLine(ctx, series, p => Number(p.melodyCandidateAmp) || 0, xMap, yMap, '#ff9800');

    drawSweepLegend(ctx, chart, [
      ['#8e24aa', 'PeakA Energy'],
      ['#1565c0', 'Input Response'],
      ['#43a047', 'Melody Amp'],
      ['#ff9800', 'Melody Candidate Amp'],
    ]);
    drawFooter(ctx, chart, H, `Sweep Trace Energy / Shared Auto Max ${formatCompactNumber(vmax)}`);
    setCanvasFrequencyProbe(canvas, {
      chart,
      xMin: start,
      xMax: end,
      format: tCursor => {
        const p = nearestByX(series.map(x => ({ ...x, x: Number(x.t) || 0 })), tCursor);
        if (!p) return '';
        return `<div class="hz">Input ${fmtHz(p.inputHz)}</div>` +
          `<div>Input Response <b>${fmtAmp(p.inputResponseMagnitudeA)}</b> / PeakA ${fmtAmp(p.peakAEnergy)}</div>` +
          `<div>Melody ${fmtAmp(p.melodyAmp)} / Candidate ${fmtAmp(p.melodyCandidateAmp)}</div>` +
          `<div class="sub">t ${Number(p.t).toFixed(2)} s</div>`;
      }
    });
  }


  function getInputResponsePoints(side) {
    const src = Array.isArray(side?.tsBuf) ? side.tsBuf : [];
    return src
      .map(p => ({
        hz: Number(p?.inputHz) || 0,
        responseHz: Number(p?.inputResponseHz) || 0,
        mag: Number(p?.inputResponseMagnitudeA) || 0,
      }))
      .filter(p => p.hz > 0 && p.mag > 0)
      .sort((a, b) => a.hz - b.hz);
  }

  function median(values) {
    const arr = (values || []).map(Number).filter(Number.isFinite).sort((a, b) => a - b);
    if (!arr.length) return NaN;
    const mid = Math.floor(arr.length / 2);
    return arr.length % 2 ? arr[mid] : (arr[mid - 1] + arr[mid]) / 2;
  }

  function interpolateMagnitude(points, hz) {
    if (!Array.isArray(points) || points.length < 2 || !Number.isFinite(hz)) return NaN;
    if (hz < points[0].hz || hz > points[points.length - 1].hz) return NaN;

    let lo = 0;
    let hi = points.length - 1;
    while (lo + 1 < hi) {
      const mid = (lo + hi) >> 1;
      if (points[mid].hz <= hz) lo = mid;
      else hi = mid;
    }

    const a = points[lo];
    const b = points[hi];
    if (!a || !b) return NaN;
    if (Math.abs(b.hz - a.hz) < 1e-9) return Number(a.mag) || NaN;
    const r = (hz - a.hz) / (b.hz - a.hz);
    return a.mag + (b.mag - a.mag) * r;
  }

  function buildTransmissionSeries(side, referencePoints, referenceFloor) {
    const points = getInputResponsePoints(side);
    if (!points.length || !referencePoints.length) return [];
    const out = [];
    for (const p of points) {
      const refMag = interpolateMagnitude(referencePoints, p.hz);
      if (!Number.isFinite(refMag) || refMag <= referenceFloor) continue;
      const ratio = (p.mag / refMag) * 100;
      if (!Number.isFinite(ratio) || ratio <= 0) continue;
      out.push({
        hz: p.hz,
        ratio,
        gainDb: 20 * Math.log10(ratio / 100),
        mag: p.mag,
        referenceMag: refMag,
      });
    }
    return out;
  }

  function summarizeTransmission(points) {
    if (!Array.isArray(points) || !points.length) return null;
    const inBand = (f0, f1) => points.filter(p => p.hz >= f0 && p.hz < f1).map(p => p.ratio);
    const maxPoint = points.reduce((best, p) => (!best || p.ratio > best.ratio) ? p : best, null);
    return {
      count: points.length,
      overall: median(points.map(p => p.ratio)),
      low: median(inBand(20, 80)),
      mid: median(inBand(80, 160)),
      high: median(inBand(160, 250)),
      upper: median(inBand(250, 301)),
      maxPoint,
    };
  }

  function formatRatioAndDb(pct) {
    if (!Number.isFinite(pct) || pct <= 0) return '-';
    const db = 20 * Math.log10(pct / 100);
    return `${pct.toFixed(1)}% (${db >= 0 ? '+' : ''}${db.toFixed(1)}dB)`;
  }

  function formatTransmissionSummary(label, summary) {
    if (!summary) return `${label}: no transmission data`;
    const max = summary.maxPoint
      ? `${summary.maxPoint.ratio.toFixed(0)}%@${summary.maxPoint.hz.toFixed(0)}Hz`
      : '-';
    return `<b>${label}</b> Overall ${formatRatioAndDb(summary.overall)} / ` +
      `Low 20-80 ${formatRatioAndDb(summary.low)} / ` +
      `Mid 80-160 ${formatRatioAndDb(summary.mid)} / ` +
      `High 160-250 ${formatRatioAndDb(summary.high)} / ` +
      `250-300 ${formatRatioAndDb(summary.upper)} / Max ${max}`;
  }

  function drawTransmissionRatio() {
    const canvas = $('transmissionRatio');
    const statsEl = $('transmissionStats');
    if (!canvas) return;

    resizeCanvas(canvas);
    const ctx = canvas.getContext('2d');
    const W = canvas.width, H = canvas.height;
    clearChart(ctx, W, H);
    const chart = setupAxes(ctx, W, H, { ml: PLOT_LEFT_CSS, mr: PLOT_RIGHT_CSS, mt: 24, mb: 30 });

    const referencePoints = getInputResponsePoints(state.reference);
    if (referencePoints.length < 2) {
      if (statsEl) {
        statsEl.textContent = state.reference.raw
          ? 'Reference log has no inputResponseMagnitudeA. Re-measure with v0.2.6 or later.'
          : 'Load Speaker Direct log as Reference.';
      }
      return drawNoData(ctx, state.reference.raw
        ? 'reference input-response fields unavailable'
        : 'load Reference Log (Speaker Direct)');
    }

    const refMedian = median(referencePoints.map(p => p.mag));
    const referenceFloor = Math.max(1e-9, (Number.isFinite(refMedian) ? refMedian : 0) * 0.05);
    const leftSeries = buildTransmissionSeries(state.left, referencePoints, referenceFloor);
    const rightSeries = buildTransmissionSeries(state.right, referencePoints, referenceFloor);

    if (!leftSeries.length && !rightSeries.length) {
      if (statsEl) statsEl.textContent = 'Load rod logs measured with v0.2.6 or later.';
      return drawNoData(ctx, 'no rod input-response fields');
    }

    const all = [...leftSeries, ...rightSeries];
    const minHz = Math.max(0, Math.min(20, ...all.map(p => p.hz)));
    const maxHz = Math.max(300, ...all.map(p => p.hz));
    const rawMax = Math.max(100, ...all.map(p => p.ratio));
    const yMax = Math.max(200, niceAxisMax(rawMax * 1.05));

    const xMap = hz => chart.left + ((hz - minHz) / Math.max(1e-9, maxHz - minHz)) * chart.width;
    const yMap = pct => chart.bottom - Math.max(0, Math.min(yMax, Number(pct) || 0)) / yMax * chart.height;

    // Y grid + 100% reference baseline
    const yTicks = 5;
    drawGrid(ctx, chart, Array.from({ length: yTicks }, (_, i) => i), i =>
      `${Math.round(yMax - yMax * i / (yTicks - 1))}%`
    );

    ctx.save();
    ctx.strokeStyle = '#555';
    ctx.lineWidth = 1.5 * (window.devicePixelRatio || 1);
    ctx.setLineDash([px(7), px(5)]);
    ctx.beginPath();
    ctx.moveTo(chart.left, yMap(100));
    ctx.lineTo(chart.right, yMap(100));
    ctx.stroke();
    ctx.restore();

    // X frequency guides
    ctx.font = `${10 * (window.devicePixelRatio || 1)}px sans-serif`;
    ctx.textAlign = 'center';
    ctx.textBaseline = 'top';
    for (let hz = 50; hz <= 300; hz += 50) {
      const x = xMap(hz);
      ctx.strokeStyle = '#ececec';
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.moveTo(x, chart.top);
      ctx.lineTo(x, chart.bottom);
      ctx.stroke();
      ctx.fillStyle = '#666';
      ctx.fillText(`${hz}`, x, chart.bottom + px(4));
    }

    function drawRatioSeries(series, color) {
      if (!series.length) return;
      ctx.save();
      ctx.strokeStyle = color;
      ctx.lineWidth = 2.2 * (window.devicePixelRatio || 1);
      ctx.beginPath();
      let started = false;
      for (const p of series) {
        const x = xMap(p.hz);
        const y = yMap(p.ratio);
        if (!started) { ctx.moveTo(x, y); started = true; }
        else ctx.lineTo(x, y);
      }
      if (started) ctx.stroke();
      ctx.restore();
    }

    drawRatioSeries(leftSeries, '#1565c0');
    drawRatioSeries(rightSeries, '#d81b60');

    const leftLabel = state.left.raw?.experiment?.rod || state.left.name || 'Left';
    const rightLabel = state.right.raw?.experiment?.rod || state.right.name || 'Right';

    drawSweepLegend(ctx, chart, [
      ['#555', 'Reference 100%'],
      ['#1565c0', leftLabel],
      ['#d81b60', rightLabel],
    ]);
    drawFooter(ctx, chart, H, `Transmission Ratio / Input Response RMS ±1bin / Ref floor ${formatCompactNumber(referenceFloor)} / Y Max ${Math.round(yMax)}%`);

    setCanvasFrequencyProbe(canvas, {
      chart,
      xMin: minHz,
      xMax: maxHz,
      format: hzCursor => {
        const lp = nearestByX(leftSeries.map(p => ({ ...p, x: p.hz })), hzCursor);
        const rp = nearestByX(rightSeries.map(p => ({ ...p, x: p.hz })), hzCursor);
        const candidates = [lp, rp].filter(Boolean);
        if (!candidates.length) return '';
        const anchor = candidates.reduce((best, p) => !best || Math.abs(p.hz - hzCursor) < Math.abs(best.hz - hzCursor) ? p : best, null);
        const hz = Number(anchor?.hz) || hzCursor;
        const l = nearestByX(leftSeries.map(p => ({ ...p, x: p.hz })), hz);
        const r = nearestByX(rightSeries.map(p => ({ ...p, x: p.hz })), hz);
        const lines = [`<div class="hz">${hz.toFixed(1)} Hz</div>`];
        if (l) lines.push(`<div>${leftLabel}: <b>${l.ratio.toFixed(1)}%</b> (${l.gainDb >= 0 ? '+' : ''}${l.gainDb.toFixed(1)} dB)</div>`);
        if (r) lines.push(`<div>${rightLabel}: <b>${r.ratio.toFixed(1)}%</b> (${r.gainDb >= 0 ? '+' : ''}${r.gainDb.toFixed(1)} dB)</div>`);
        lines.push('<div class="sub">Speaker Direct = 100%</div>');
        return lines.join('');
      }
    });

    if (statsEl) {
      const parts = [];
      if (leftSeries.length) parts.push(formatTransmissionSummary(leftLabel, summarizeTransmission(leftSeries)));
      if (rightSeries.length) parts.push(formatTransmissionSummary(rightLabel, summarizeTransmission(rightSeries)));
      statsEl.innerHTML = parts.join('<br>');
    }
  }

  function getRingDownSeries(side) {
    const raw = side?.raw;
    const source = Array.isArray(raw?.tsBuf) ? raw.tsBuf : [];
    const meta = raw?.automationMeta || {};
    const stopT = Number(meta?.toneStoppedT);
    const targetHz = Number(meta?.ringDownTargetHz ?? meta?.ringDownSummary?.targetHz) || 0;
    if (!Number.isFinite(stopT) || targetHz <= 0 || !source.length) return [];

    return source
      .map(frame => ({
        sec: (Number(frame?.t) || 0) - stopT,
        mag: Number(frame?.ringDownMagnitudeRawA) || 0,
        responseHz: Number(frame?.ringDownResponseHz) || 0,
        centerHz: Number(frame?.ringDownResponseCenterHz) || 0,
        peakMag: Number(frame?.ringDownPeakMagnitudeRawA) || 0,
      }))
      .filter(p => Number.isFinite(p.sec) && p.sec >= -0.002 && Number.isFinite(p.mag) && p.mag >= 0)
      .sort((a, b) => a.sec - b.sec);
  }

  function getRingDownSummary(side) {
    const summary = side?.raw?.automationMeta?.ringDownSummary;
    if (!summary || typeof summary !== 'object') return null;
    return summary;
  }

  function formatSeconds(v) {
    const n = Number(v);
    return Number.isFinite(n) ? `${n.toFixed(3)}s` : '-';
  }

  function formatRingDownSummary(label, side) {
    const s = getRingDownSummary(side);
    if (!s) return `<b>${label}</b> no RingDown summary`;
    const targetHz = Number(s.targetHz ?? side?.raw?.automationMeta?.ringDownTargetHz) || 0;
    const start = Number(s.startMagnitudeRawA);
    const end = Number(s.endMagnitudeRawA);
    const endRatio = Number(s.endRatioPct);
    const tail = Number(s.tailMedianMagnitudeRawA);
    return `<b>${label}</b> Target ${targetHz ? targetHz.toFixed(0) + 'Hz' : '-'} / ` +
      `Start ${fmtAmp(start)} / T50 ${formatSeconds(s.t50Sec)} / T10 ${formatSeconds(s.t10Sec)} / ` +
      `Tail median ${fmtAmp(tail)} / End ${fmtAmp(end)}${Number.isFinite(endRatio) ? ` (${endRatio.toFixed(1)}%)` : ''}`;
  }

  function drawRingDownCompare() {
    const canvas = $('ringDownCompare');
    const statsEl = $('ringDownStats');
    if (!canvas) return;

    resizeCanvas(canvas);
    const ctx = canvas.getContext('2d');
    const W = canvas.width, H = canvas.height;
    clearChart(ctx, W, H);
    const chart = setupAxes(ctx, W, H, { ml: PLOT_LEFT_CSS, mr: PLOT_RIGHT_CSS, mt: 24, mb: 32 });

    const leftSeries = getRingDownSeries(state.left);
    const rightSeries = getRingDownSeries(state.right);
    const leftLabel = state.left.raw?.experiment?.rod || state.left.name || 'Left';
    const rightLabel = state.right.raw?.experiment?.rod || state.right.name || 'Right';

    if (!leftSeries.length && !rightSeries.length) {
      if (statsEl) statsEl.textContent = 'Load RingDown logs into Left / Right.';
      setCanvasFrequencyProbe(canvas, null);
      return drawNoData(ctx, 'load RingDown logs into Left / Right');
    }

    const all = [...leftSeries, ...rightSeries];
    const maxSec = Math.max(0.5, ...all.map(p => Math.max(0, Number(p.sec) || 0)));
    const rawMax = Math.max(1, ...all.map(p => Number(p.mag) || 0));
    const yMax = Math.max(100, niceAxisMax(rawMax * 1.05));
    const xMap = sec => chart.left + (Math.max(0, sec) / Math.max(1e-9, maxSec)) * chart.width;
    const yMap = mag => chart.bottom - Math.max(0, Math.min(yMax, Number(mag) || 0)) / yMax * chart.height;

    drawGrid(ctx, chart, [0,1,2,3,4], i => formatCompactNumber(yMax - yMax * i / 4));

    // X guides are elapsed seconds after audio STOP.  Both logs share STOP = 0s.
    ctx.font = `${10 * (window.devicePixelRatio || 1)}px sans-serif`;
    ctx.textAlign = 'center';
    ctx.textBaseline = 'top';
    const xTicks = 5;
    for (let i = 0; i <= xTicks; i++) {
      const sec = maxSec * i / xTicks;
      const x = xMap(sec);
      ctx.strokeStyle = i === 0 ? '#94a3b8' : '#ececec';
      ctx.lineWidth = i === 0 ? 1.5 * (window.devicePixelRatio || 1) : 1;
      ctx.beginPath();
      ctx.moveTo(x, chart.top);
      ctx.lineTo(x, chart.bottom);
      ctx.stroke();
      ctx.fillStyle = '#666';
      ctx.fillText(sec.toFixed(maxSec <= 2 ? 2 : 1), x, chart.bottom + px(4));
    }

    function drawRingSeries(series, color) {
      if (!series.length) return;
      ctx.save();
      ctx.strokeStyle = color;
      ctx.lineWidth = 2.2 * (window.devicePixelRatio || 1);
      ctx.beginPath();
      let started = false;
      for (const p of series) {
        if (p.sec < 0) continue;
        const x = xMap(p.sec);
        const y = yMap(p.mag);
        if (!started) { ctx.moveTo(x, y); started = true; }
        else ctx.lineTo(x, y);
      }
      if (started) ctx.stroke();
      ctx.restore();
    }

    drawRingSeries(leftSeries, '#1565c0');
    drawRingSeries(rightSeries, '#d81b60');

    drawSweepLegend(ctx, chart, [
      ['#1565c0', leftLabel],
      ['#d81b60', rightLabel],
    ]);

    const leftTarget = Number(state.left.raw?.automationMeta?.ringDownTargetHz ?? state.left.raw?.automationMeta?.ringDownSummary?.targetHz) || 0;
    const rightTarget = Number(state.right.raw?.automationMeta?.ringDownTargetHz ?? state.right.raw?.automationMeta?.ringDownSummary?.targetHz) || 0;
    const sameTarget = leftTarget > 0 && rightTarget > 0 && Math.abs(leftTarget - rightTarget) < 1e-6;
    const targetText = sameTarget
      ? `Target ${leftTarget.toFixed(0)}Hz`
      : [leftTarget ? `L ${leftTarget.toFixed(0)}Hz` : '', rightTarget ? `R ${rightTarget.toFixed(0)}Hz` : ''].filter(Boolean).join(' / ');
    drawFooter(ctx, chart, H, `Ring Down Raw FFT RMS ±1bin / STOP = 0s / ${targetText || 'target -'} / Shared Y Max ${formatCompactNumber(yMax)}`);

    const leftStart = Number(getRingDownSummary(state.left)?.startMagnitudeRawA) || (leftSeries[0]?.mag || 0);
    const rightStart = Number(getRingDownSummary(state.right)?.startMagnitudeRawA) || (rightSeries[0]?.mag || 0);
    setCanvasFrequencyProbe(canvas, {
      chart,
      xMin: 0,
      xMax: maxSec,
      format: secCursor => {
        const l = nearestByX(leftSeries.map(p => ({ ...p, x: Math.max(0, p.sec) })), secCursor);
        const r = nearestByX(rightSeries.map(p => ({ ...p, x: Math.max(0, p.sec) })), secCursor);
        if (!l && !r) return '';
        const sec = Math.max(0, Number((l && Math.abs(l.sec - secCursor) <= Math.abs((r?.sec ?? Infinity) - secCursor)) ? l.sec : r?.sec) || secCursor);
        const ln = nearestByX(leftSeries.map(p => ({ ...p, x: Math.max(0, p.sec) })), sec);
        const rn = nearestByX(rightSeries.map(p => ({ ...p, x: Math.max(0, p.sec) })), sec);
        const lines = [`<div class="hz">STOP +${sec.toFixed(3)} s</div>`];
        if (ln) {
          const retain = leftStart > 0 ? (ln.mag / leftStart) * 100 : NaN;
          lines.push(`<div>${leftLabel}: <b>${fmtAmp(ln.mag)}</b>${Number.isFinite(retain) ? ` / ${retain.toFixed(1)}%` : ''}</div>`);
        }
        if (rn) {
          const retain = rightStart > 0 ? (rn.mag / rightStart) * 100 : NaN;
          lines.push(`<div>${rightLabel}: <b>${fmtAmp(rn.mag)}</b>${Number.isFinite(retain) ? ` / ${retain.toFixed(1)}%` : ''}</div>`);
        }
        lines.push(`<div class="sub">Raw FFT RMS ±1bin${targetText ? ' / ' + targetText : ''}</div>`);
        return lines.join('');
      }
    });

    if (statsEl) {
      const parts = [];
      if (state.left.raw) parts.push(formatRingDownSummary(leftLabel, state.left));
      if (state.right.raw) parts.push(formatRingDownSummary(rightLabel, state.right));
      if (leftTarget > 0 && rightTarget > 0 && !sameTarget) {
        parts.push(`<span class="warn">Warning: RingDown target mismatch (${leftTarget.toFixed(0)}Hz vs ${rightTarget.toFixed(0)}Hz)</span>`);
      }
      statsEl.innerHTML = parts.join('<br>');
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
    setCanvasFrequencyProbe(canvas, {
      chart,
      xMin: start,
      xMax: end,
      format: tCursor => {
        const p = nearestByX(series.map(x => ({ ...x, x: Number(x.t) || 0 })), tCursor);
        if (!p) return '';
        return `<div class="hz">Input ${fmtHz(p.inputHz)}</div>` +
          `<div class="sub">t ${Number(p.t).toFixed(2)} s / Band timeline</div>`;
      }
    });
  }

  // Flux / Triangle Motion are comparison charts.
  // Decide one shared Y-axis maximum from BOTH loaded logs so that the
  // left/right heights mean the same value.  Add a little headroom and
  // round upward to a human-friendly scale (e.g. 0.43 -> 0.50,
  // 0.279 -> 0.30).
  function niceAxisMax(value) {
    const v = Number(value) || 0;
    if (v <= 0) return 1;
    const exponent = Math.floor(Math.log10(v));
    const base = Math.pow(10, exponent);
    const normalized = v / base;
    const steps = [1, 1.2, 1.5, 2, 2.5, 3, 4, 5, 6, 7.5, 10];
    const step = steps.find(x => normalized <= x + 1e-12) || 10;
    return step * base;
  }

  function getSharedFluxMax() {
    let rawMax = 0;
    for (const side of [state.left, state.right]) {
      for (const p of side.tsBuf || []) {
        rawMax = Math.max(rawMax, Number(p.fluxA) || 0, Number(p.fluxM) || 0);
      }
    }
    // Keep the old small-signal floor, but use one shared maximum when data exists.
    return Math.max(0.12, niceAxisMax(rawMax * 1.05));
  }

  function getSharedTriangleMax() {
    let rawMax = 0;
    for (const side of [state.left, state.right]) {
      for (const p of side.tsBuf || []) rawMax = Math.max(rawMax, Number(p.tingleMotion) || 0);
    }
    if (rawMax <= 0) return 0.10;
    return niceAxisMax(rawMax * 1.05);
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
    const vmax = getSharedFluxMax();
    const yMap = (v) => chart.bottom - Math.max(0, Math.min(vmax, v || 0)) / vmax * chart.height;
    drawGrid(ctx, chart, [0,1,2,3,4], i => (vmax - vmax * i / 4).toFixed(2));
    drawLine(ctx, series, p => Number(p.fluxA) || 0, xMap, yMap, '#8e24aa');
    drawLine(ctx, series, p => Number(p.fluxM) || 0, xMap, yMap, '#fb8c00');
    ctx.font = `${11 * (window.devicePixelRatio || 1)}px sans-serif`;
    ctx.textAlign = 'left'; ctx.textBaseline = 'top';
    const last = series[series.length - 1] || {};
    ctx.fillStyle = '#8e24aa'; ctx.fillText(`A:${(Number(last.fluxA) || 0).toFixed(3)}`, chart.left + 8, chart.top + 6);
    ctx.fillStyle = '#fb8c00'; ctx.fillText(`M:${(Number(last.fluxM) || 0).toFixed(3)}`, chart.left + 90 * (window.devicePixelRatio || 1), chart.top + 6);
    drawFooter(ctx, chart, H, `Flux (A/M) / Shared Y Max ${vmax.toFixed(2)}`);
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
    const vmax = getSharedTriangleMax();
    const yMap = (v) => chart.bottom - Math.max(0, Math.min(vmax, v || 0)) / vmax * chart.height;
    drawGrid(ctx, chart, [0,1,2,3,4], i => (vmax - vmax * i / 4).toFixed(3));
    drawLine(ctx, series, p => Number(p.tingleMotion) || 0, xMap, yMap, '#8e24aa');
    drawFooter(ctx, chart, H, `Triangle Motion / Tingle Motion / Shared Y Max ${vmax.toFixed(3)}`);
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
    drawLine(ctx, series, p => getBridgeLegacyScore(p), xMap, yMap, '#d81b60');
    drawFooter(ctx, chart, H, 'BridgeScore v1 Legacy / shared calc');
  }

  function getSharedBridgeBreakdownMax() {
    if (!BridgeMetrics) return 1;
    let rawMax = 0;
    for (const side of [state.left, state.right]) {
      for (const p of getBridgeDerived(side)) {
        rawMax = Math.max(rawMax, Number(p.low) || 0, Number(p.mid) || 0, Number(p.high) || 0);
      }
    }
    return Math.max(1, niceAxisMax(rawMax * 1.05));
  }

  function formatBridgeStats(summary) {
    if (!summary || !summary.count) return 'Bridge Research: no data';
    const f = (v, d = 3) => Number.isFinite(v) ? Number(v).toFixed(d) : '-';
    const occ = Number.isFinite(summary.highOccupancy) ? `${(summary.highOccupancy * 100).toFixed(1)}%` : '-';
    return `Legacy Mean ${f(summary.scoreMean)} / SD ${f(summary.scoreSd)} / P10 ${f(summary.scoreP10)} / >=0.80 ${occ}` +
      `<br>L ${f(summary.lowMean,0)} / M ${f(summary.midMean,0)} / H ${f(summary.highMean,0)} / r1 ${f(summary.ratioLowMidMean)} / r2 ${f(summary.ratioMidHighMean)}`;
  }

  function drawBridgeStability(canvas, side, slot) {
    resizeCanvas(canvas);
    const ctx = canvas.getContext('2d');
    const W = canvas.width, H = canvas.height;
    clearChart(ctx, W, H);
    const chart = setupAxes(ctx, W, H, { ml: PLOT_LEFT_CSS, mr: PLOT_RIGHT_CSS, mt: 16, mb: 24 });
    const derived = getBridgeDerived(side);
    const statsEl = $(slot + 'BridgeStats');
    if (!derived || derived.length < 2) {
      if (statsEl) statsEl.textContent = 'Bridge Research: no data';
      return drawNoData(ctx, 'no bridge stability');
    }

    const { start, end } = getTimeBounds(derived);
    const xMap = t => chart.left + ((t - start) / (end - start)) * chart.width;
    const yMap = v => chart.bottom - Math.max(0, Math.min(1, Number(v) || 0)) * chart.height;
    drawGrid(ctx, chart, [0,1,2,3,4], i => (1 - i / 4).toFixed(2));
    drawLine(ctx, derived, p => Number(p.rollingMean) || 0, xMap, yMap, '#d81b60');
    drawLine(ctx, derived, p => Number(p.stability) || 0, xMap, yMap, '#1565c0');

    ctx.font = `${10 * (window.devicePixelRatio || 1)}px sans-serif`;
    ctx.textAlign = 'left'; ctx.textBaseline = 'top';
    ctx.fillStyle = '#d81b60'; ctx.fillText('Mean', chart.left + px(8), chart.top + px(4));
    ctx.fillStyle = '#1565c0'; ctx.fillText('Stability', chart.left + px(55), chart.top + px(4));
    drawFooter(ctx, chart, H, 'Stability = 1 - 2*rolling SD / 1.0s (Research)');

    if (statsEl && BridgeMetrics) statsEl.innerHTML = formatBridgeStats(BridgeMetrics.summarize(side.tsBuf || []));
  }

  function drawBridgeBreakdown(canvas, side) {
    resizeCanvas(canvas);
    const ctx = canvas.getContext('2d');
    const W = canvas.width, H = canvas.height;
    clearChart(ctx, W, H);
    const chart = setupAxes(ctx, W, H, { ml: PLOT_LEFT_CSS, mr: PLOT_RIGHT_CSS, mt: 18, mb: 24 });
    const derived = getBridgeDerived(side);
    if (!derived || derived.length < 2) return drawNoData(ctx, 'no legacy band breakdown');
    const hasBreakdown = derived.some(p => Number.isFinite(p.low) || Number.isFinite(p.mid) || Number.isFinite(p.high));
    if (!hasBreakdown) return drawNoData(ctx, 'legacy log: bandA breakdown unavailable');

    const { start, end } = getTimeBounds(derived);
    const vmax = getSharedBridgeBreakdownMax();
    const xMap = t => chart.left + ((t - start) / (end - start)) * chart.width;
    const yMap = v => chart.bottom - Math.max(0, Math.min(vmax, Number(v) || 0)) / vmax * chart.height;
    drawGrid(ctx, chart, [0,1,2,3,4], i => Math.round(vmax - vmax * i / 4).toString());

    drawLine(ctx, derived, p => Number(p.low) || 0, xMap, yMap, '#1565c0');
    drawLine(ctx, derived, p => Number(p.mid) || 0, xMap, yMap, '#43a047');
    drawLine(ctx, derived, p => Number(p.high) || 0, xMap, yMap, '#e53935');

    ctx.font = `${10 * (window.devicePixelRatio || 1)}px sans-serif`;
    ctx.textAlign = 'left'; ctx.textBaseline = 'top';
    let lx = chart.left + px(8);
    const defs = [
      ['#1565c0', 'Low 0-80'],
      ['#43a047', 'Mid 80-160'],
      ['#e53935', 'High 160-250'],
    ];
    for (const [color, label] of defs) {
      ctx.fillStyle = color; ctx.fillRect(lx, chart.top + px(6), px(12), px(3));
      ctx.fillStyle = '#333'; ctx.fillText(label, lx + px(16), chart.top + px(2));
      lx += ctx.measureText(label).width + px(34);
    }
    drawFooter(ctx, chart, H, `Legacy bands / Shared Y Max ${Math.round(vmax)}`);
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
    drawSweepHz($(slot + 'SweepHz'), side);
    drawSweepEnergy($(slot + 'SweepEnergy'), side);
    drawBandTimeline($(slot + 'Band'), side);
    drawPianoRoll($(slot + 'Piano'), side);
    drawFlux($(slot + 'Flux'), side);
    drawTriangle($(slot + 'Triangle'), side);
    drawBridge($(slot + 'Bridge'), side);
    drawBridgeStability($(slot + 'BridgeStability'), side, slot);
    drawBridgeBreakdown($(slot + 'BridgeBreakdown'), side);
  }

  function renderAll() {
    updateScaleStatus();
    drawTransmissionRatio();
    drawRingDownCompare();
    renderSide('left');
    renderSide('right');
  }

  async function loadFromUrlParam(slot, url) {
    if (!url) return;
    try {
      const res = await fetch(url, { cache: 'no-store' });
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
    loadFromUrlParam('reference', params.get('reference'));
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
