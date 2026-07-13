const els = {
  canvas: document.getElementById('waveCanvas'),
  playBtn: document.getElementById('playBtn'),
  stopBtn: document.getElementById('stopBtn'),
  saveSettingsBtn: document.getElementById('saveSettingsBtn'),
  loadSettingsBtn: document.getElementById('loadSettingsBtn'),
  loadSettingsInput: document.getElementById('loadSettingsInput'),
  formulaText: document.getElementById('formulaText'),
  settingsStatus: document.getElementById('settingsStatus'),
  timeReadout: document.getElementById('timeReadout'),
  freqReadout: document.getElementById('freqReadout'),
  settingsName: document.getElementById('settingsName'),
};

const params = {
  duration: document.getElementById('duration'),
  amp: document.getElementById('amp'),
  decay: document.getElementById('decay'),
  f0: document.getElementById('f0'),
  f1: document.getElementById('f1'),
  curve: document.getElementById('curve'),
  speedBoost: document.getElementById('speedBoost'),
  accel: document.getElementById('accel'),
  tailSpeed: document.getElementById('tailSpeed'),
  modFreq: document.getElementById('modFreq'),
  modDepth: document.getElementById('modDepth'),
  detuneHz: document.getElementById('detuneHz'),
  detuneMix: document.getElementById('detuneMix'),
  detunePhase: document.getElementById('detunePhase'),
  secondAmp: document.getElementById('secondAmp'),
  secondPos: document.getElementById('secondPos'),
  jitter: document.getElementById('jitter'),
  lowAmp: document.getElementById('lowAmp'),
  lowHz: document.getElementById('lowHz'),
  lowDelay: document.getElementById('lowDelay'),
  lowRise: document.getElementById('lowRise'),
  lowTail: document.getElementById('lowTail'),
  lowLayerAmp: document.getElementById('lowLayerAmp'),
  lowLayerHz: document.getElementById('lowLayerHz'),
  lowLayerDelay: document.getElementById('lowLayerDelay'),
  lowLayerAttack: document.getElementById('lowLayerAttack'),
  lowLayerHold: document.getElementById('lowLayerHold'),
  lowLayerRelease: document.getElementById('lowLayerRelease'),
  lowLayerWobbleHz: document.getElementById('lowLayerWobbleHz'),
  lowLayerWobbleDepth: document.getElementById('lowLayerWobbleDepth'),
  lowLayerHarmonic: document.getElementById('lowLayerHarmonic'),
  highLayerAmp: document.getElementById('highLayerAmp'),
  highLayerHz: document.getElementById('highLayerHz'),
  highLayerDelay: document.getElementById('highLayerDelay'),
  highLayerAttack: document.getElementById('highLayerAttack'),
  highLayerHold: document.getElementById('highLayerHold'),
  highLayerRelease: document.getElementById('highLayerRelease'),
  highLayerShimmerHz: document.getElementById('highLayerShimmerHz'),
  highLayerShimmerDepth: document.getElementById('highLayerShimmerDepth'),
  highLayerHarmonic: document.getElementById('highLayerHarmonic'),
  volume: document.getElementById('volume'),
};

const outs = {};
for (const key of Object.keys(params)) {
  outs[key] = document.getElementById(`${key}Out`);
}

let audioCtx = null;
let playingNodes = [];

function getP() {
  const p = {};
  for (const [key, el] of Object.entries(params)) {
    p[key] = Number(el.value);
  }
  return p;
}

function setStatus(message, isError = false) {
  if (!els.settingsStatus) return;
  els.settingsStatus.textContent = message;
  els.settingsStatus.classList.toggle('error', Boolean(isError));
}

function getParamMeta(key) {
  const el = params[key];
  if (!el) return null;
  return {
    min: Number(el.min),
    max: Number(el.max),
    step: el.step,
  };
}

function clampParamValue(key, value) {
  const el = params[key];
  if (!el) return null;
  const n = Number(value);
  if (!Number.isFinite(n)) return null;
  const min = Number(el.min);
  const max = Number(el.max);
  return Math.max(min, Math.min(max, n));
}

function buildSettingsJson() {
  const settings = getP();
  const parameterMeta = {};
  for (const key of Object.keys(params)) {
    parameterMeta[key] = getParamMeta(key);
  }

  return {
    app: 'frb_purupuru_designer',
    schemaVersion: 1,
    appVersion: 'v2.6',
    savedAt: new Date().toISOString(),
    settingsName: els.settingsName?.value?.trim() || '',
    settings,
    parameterMeta,
    notes: 'Artificial PuruPuru Designer setting file. Load this JSON from the app to restore the slider values.'
  };
}

function makeSettingsFileName() {
  const d = new Date();
  const pad = (n) => String(n).padStart(2, '0');
  const stamp =
    `${d.getFullYear()}${pad(d.getMonth() + 1)}${pad(d.getDate())}_` +
    `${pad(d.getHours())}${pad(d.getMinutes())}${pad(d.getSeconds())}`;

  const rawName = els.settingsName?.value?.trim() || 'noname';
  const safeName = rawName.replace(/[^a-zA-Z0-9ぁ-んァ-ヶ一-龠_-]/g, '_');

  return `frb_purupuru_${safeName}_${stamp}.json`;
}

function saveSettingsJson() {
  const payload = buildSettingsJson();
  const text = JSON.stringify(payload, null, 2);
  const blob = new Blob([text], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = makeSettingsFileName();
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
  setStatus(`設定JSONを保存しました: ${a.download}`);
}

function guessSettingsNameFromFileName(fileName) {
  const base = String(fileName || '').replace(/\.json$/i, '');
  const m = base.match(/^frb_purupuru_(.+?)_\d{8}_\d{6}$/);
  if (!m) return '';
  return m[1].replace(/_/g, ' ');
}

function normalizeSettingsPayload(payload) {
  // v2.2形式: { settings: { duration: ... } }
  if (payload && typeof payload === 'object' && payload.settings && typeof payload.settings === 'object') {
    return payload.settings;
  }
  // 予備互換: { duration: ... } のような素のパラメータJSONも読めるようにしておく
  if (payload && typeof payload === 'object') {
    return payload;
  }
  return null;
}

function applySettings(settings, payload = null, fileName = '') {
  if (!settings || typeof settings !== 'object') {
    throw new Error('settings オブジェクトが見つかりません。');
  }

  if (els.settingsName) {
    const payloadName = payload && typeof payload === 'object' ? (payload.settingsName || payload.name || payload.title || '') : '';
    const guessedName = !payloadName && fileName ? guessSettingsNameFromFileName(fileName) : '';
    els.settingsName.value = payloadName || guessedName || els.settingsName.value || '';
  }

  let applied = 0;
  const skipped = [];

  for (const key of Object.keys(params)) {
    if (!Object.prototype.hasOwnProperty.call(settings, key)) continue;
    const value = clampParamValue(key, settings[key]);
    if (value === null) {
      skipped.push(key);
      continue;
    }
    params[key].value = value;
    applied += 1;
  }

  if (applied === 0) {
    throw new Error('読み込める設定項目がありません。');
  }

  draw();
  return { applied, skipped };
}

async function loadSettingsJson(file) {
  if (!file) return;
  try {
    const text = await file.text();
    const payload = JSON.parse(text);
    const settings = normalizeSettingsPayload(payload);
    const result = applySettings(settings, payload, file.name);
    const skippedText = result.skipped.length ? ` / 無効値スキップ: ${result.skipped.join(', ')}` : '';
    setStatus(`設定JSONを読み込みました: ${file.name} / ${result.applied}項目${skippedText}`);
  } catch (err) {
    console.error(err);
    setStatus(`設定JSONの読み込みに失敗しました: ${err.message}`, true);
  } finally {
    // 同じファイルを連続で選べるようにリセット
    if (els.loadSettingsInput) els.loadSettingsInput.value = '';
  }
}

function fmt(key, v) {
  if (key === 'duration') return `${v.toFixed(1)}s`;
  if (key === 'f0' || key === 'f1') return `${v.toFixed(1)}Hz`;
  if (key === 'secondPos') return `${Math.round(v * 100)}%`;
  if (key === 'speedBoost') return `${v.toFixed(2)}x`;
  if (key === 'accel' || key === 'tailSpeed' || key === 'modDepth' || key === 'detuneMix') return `${Math.round(v * 100)}%`;
  if (key === 'modFreq' || key === 'detuneHz') return `${v.toFixed(1)}Hz`;
  if (key === 'detunePhase') return `${Math.round(v)}°`;
  if (key === 'lowHz') return `${v.toFixed(0)}Hz`;
  if (key === 'lowDelay' || key === 'lowRise' || key === 'lowTail' || key === 'lowLayerDelay' || key === 'lowLayerAttack' || key === 'lowLayerHold' || key === 'lowLayerRelease') return `${v.toFixed(2)}s`;
  if (key === 'lowHz' || key === 'lowLayerHz') return `${v.toFixed(0)}Hz`;
  if (key === 'lowLayerWobbleHz') return `${v.toFixed(2)}Hz`;
  if (key === 'lowLayerWobbleDepth' || key === 'highLayerShimmerDepth') return `${Math.round(v * 100)}%`;
  if (key === 'highLayerHz') return `${v.toFixed(0)}Hz`;
  if (key === 'highLayerShimmerHz') return `${v.toFixed(1)}Hz`;
  if (key === 'highLayerDelay' || key === 'highLayerAttack' || key === 'highLayerHold' || key === 'highLayerRelease') return `${v.toFixed(2)}s`;
  if (key === 'lowAmp' || key === 'lowLayerAmp' || key === 'lowLayerHarmonic' || key === 'highLayerAmp' || key === 'highLayerHarmonic') return v.toFixed(2);
  return v.toFixed(2);
}

function updateOutputs() {
  const p = getP();
  for (const [key, value] of Object.entries(p)) {
    if (outs[key]) outs[key].textContent = fmt(key, value);
  }
  els.timeReadout.textContent = `${p.duration.toFixed(1)}s`;
  els.freqReadout.textContent = `${p.f0.toFixed(1)}Hz → ${p.f1.toFixed(1)}Hz`;
  els.formulaText.textContent =
    `y(t)=MainPuru(t) + LowLayer(t-delay) + HighLayer(t-delay) + Tail + 第2波`;
}

function fitCanvas() {
  const dpr = window.devicePixelRatio || 1;
  const rect = els.canvas.getBoundingClientRect();
  els.canvas.width = Math.max(600, Math.floor(rect.width * dpr));
  els.canvas.height = Math.max(260, Math.floor(rect.height * dpr));
}

function freqAt(t, p) {
  const u = Math.max(0, Math.min(1, t / Math.max(0.001, p.duration)));

  // speedBoost: 時間を圧縮したように、早めに f1 へ寄せる
  const speed = Math.max(0.25, p.speedBoost || 1);
  const uSpeed = Math.max(0, Math.min(1, u * speed));

  // accel: 後半で急に細かくなる「バネの加速感」
  // accel=0 なら通常カーブ、accel=1 なら後半寄りの急加速。
  const baseCurve = Math.max(0.05, p.curve || 1);
  const accelCurve = Math.max(0.05, baseCurve * (1.0 + 2.8 * (p.accel || 0)));
  const normal = Math.pow(uSpeed, baseCurve);
  const accelerated = Math.pow(uSpeed, accelCurve);
  const shaped = normal * (1 - (p.accel || 0)) + accelerated * (p.accel || 0);

  // tailSpeed: 尾っぽだけ高周波ぷるぷるを残す。後半ほど f1 を少し超える。
  const tailStart = 0.62;
  const tailU = Math.max(0, (u - tailStart) / Math.max(0.001, 1 - tailStart));
  const tailLift = (p.tailSpeed || 0) * Math.pow(tailU, 1.6) * Math.max(0, p.f1 - p.f0) * 0.85;

  return Math.max(1, p.f0 + (p.f1 - p.f0) * shaped + tailLift);
}

function secondEnvelope(t, p) {
  const center = p.duration * p.secondPos;
  const width = Math.max(0.08, p.duration * 0.08);
  const x = (t - center) / width;
  return p.secondAmp * Math.exp(-x * x);
}

function amAt(t, p) {
  const depth = Math.max(0, Math.min(1, p.modDepth || 0));
  const hz = Math.max(0.01, p.modFreq || 5);
  // depth=0 -> 1.0固定 / depth=1 -> 0.0〜1.0のうねり
  return (1 - depth * 0.5) + depth * 0.5 * (1 + Math.sin(2 * Math.PI * hz * t));
}

function lowEnvelope(t, p) {
  const delay = Math.max(0, p.lowDelay || 0);
  if (t < delay) return 0;
  const x = t - delay;
  const rise = Math.max(0.05, p.lowRise || 0.55);
  const tail = Math.max(0.1, p.lowTail || 3.0);
  // 遅れて、ふわっと立ち上がり、低域だけ長めに残る。
  return (1 - Math.exp(-x / rise)) * Math.exp(-x / tail);
}



function lowLayerEnvelope(t, p) {
  const delay = Math.max(0, p.lowLayerDelay || 0);
  if (t < delay) return 0;
  const x = t - delay;
  const attack = Math.max(0.02, p.lowLayerAttack || 0.35);
  const hold = Math.max(0, p.lowLayerHold || 0);
  const release = Math.max(0.1, p.lowLayerRelease || 4.0);

  // 別トラックの低域共振。遅れて立ち上がり、しばらく生きて、ゆっくり消える。
  const rise = 1 - Math.exp(-x / attack);
  const tail = x <= hold ? 1 : Math.exp(-(x - hold) / release);
  return rise * tail;
}

function lowLayerFreqAt(t, p) {
  const base = Math.max(1, p.lowLayerHz || 46);
  const wobbleHz = Math.max(0, p.lowLayerWobbleHz || 0);
  const depth = Math.max(0, p.lowLayerWobbleDepth || 0);
  if (wobbleHz <= 0 || depth <= 0) return base;

  // 完全なsin固定にしないため、低速ヨレを2成分で混ぜる。
  const w =
    0.62 * Math.sin(2 * Math.PI * wobbleHz * t + 0.4) +
    0.38 * Math.sin(2 * Math.PI * wobbleHz * 2.37 * t + 1.8);
  return Math.max(1, base * (1 + depth * w));
}

function lowLayerSample(t, p) {
  const amp = Math.max(0, p.lowLayerAmp || 0);
  if (amp <= 0) return 0;
  const env = lowLayerEnvelope(t, p);
  const f = lowLayerFreqAt(t, p);
  const harmonic = Math.max(0, Math.min(1, p.lowLayerHarmonic || 0));
  const fundamental = Math.sin(2 * Math.PI * f * t + 0.22);
  const sub = Math.sin(2 * Math.PI * Math.max(1, f * 0.52) * t + 1.4);
  const upper = Math.sin(2 * Math.PI * Math.max(1, f * 2.0) * t + 0.7);

  // 主ぷるに混ぜるのではなく、低域専用レイヤーとして別人格で足す。
  return amp * env * ((1 - harmonic * 0.45) * fundamental + harmonic * 0.28 * sub + harmonic * 0.17 * upper);
}


function highLayerEnvelope(t, p) {
  const delay = Math.max(0, p.highLayerDelay || 0);
  if (t < delay) return 0;
  const x = t - delay;
  const attack = Math.max(0.01, p.highLayerAttack || 0.08);
  const hold = Math.max(0, p.highLayerHold || 0);
  const release = Math.max(0.05, p.highLayerRelease || 1.8);

  // 高域の別トラック。すぐ立ち上がり、短めに残る“ジリジリ/きらめき”成分。
  const rise = 1 - Math.exp(-x / attack);
  const tail = x <= hold ? 1 : Math.exp(-(x - hold) / release);
  return rise * tail;
}

function highLayerFreqAt(t, p) {
  const base = Math.max(1, p.highLayerHz || 260);
  const shimmerHz = Math.max(0, p.highLayerShimmerHz || 0);
  const depth = Math.max(0, p.highLayerShimmerDepth || 0);
  if (shimmerHz <= 0 || depth <= 0) return base;

  // 速めの微細なきらめき。完全な一定音にせず、少しだけ高域を揺らす。
  const w =
    0.58 * Math.sin(2 * Math.PI * shimmerHz * t + 0.9) +
    0.27 * Math.sin(2 * Math.PI * shimmerHz * 1.73 * t + 2.1) +
    0.15 * Math.sin(2 * Math.PI * shimmerHz * 3.11 * t + 0.2);
  return Math.max(1, base * (1 + depth * w));
}

function highLayerSample(t, p) {
  const amp = Math.max(0, p.highLayerAmp || 0);
  if (amp <= 0) return 0;
  const env = highLayerEnvelope(t, p);
  const f = highLayerFreqAt(t, p);
  const harmonic = Math.max(0, Math.min(1, p.highLayerHarmonic || 0));
  const fundamental = Math.sin(2 * Math.PI * f * t + 0.6);
  const upper2 = Math.sin(2 * Math.PI * Math.max(1, f * 1.5) * t + 1.1);
  const upper3 = Math.sin(2 * Math.PI * Math.max(1, f * 2.0) * t + 2.3);

  // 高域は強すぎると“自然界じゃない感”が出やすいので、倍音は薄めに混ぜる。
  return amp * env * ((1 - harmonic * 0.38) * fundamental + harmonic * 0.24 * upper2 + harmonic * 0.14 * upper3);
}

function sampleWave(p, samples = 4200) {
  const data = [];
  let phase = 0;
  let detunePhase = (p.detunePhase || 0) * Math.PI / 180;
  let phase2 = 0;
  const dt = p.duration / samples;

  for (let i = 0; i <= samples; i++) {
    const t = i * dt;
    const f = freqAt(t, p);
    phase += 2 * Math.PI * f * dt;
    detunePhase += 2 * Math.PI * Math.max(1, f + (p.detuneHz || 0)) * dt;

    const env = p.amp * Math.exp(-p.decay * t);
    const am = amAt(t, p);
    const second = secondEnvelope(t, p);

    phase2 += 2 * Math.PI * (f * 1.7 + 18) * dt;

    const tailU = Math.max(0, (t / Math.max(0.001, p.duration) - 0.58) / 0.42);
    const tailEnv = Math.exp(-2.4 * tailU) * Math.min(1, tailU * 2.5);
    const tailPuru =
      (p.tailSpeed || 0) * tailEnv *
      (0.70 * Math.sin(2 * Math.PI * (38 + p.f1 * 0.10) * t + 0.5) +
       0.30 * Math.sin(2 * Math.PI * (71 + p.f1 * 0.16) * t + 1.7));

    const low = (p.lowAmp || 0) * lowEnvelope(t, p) * (
      0.78 * Math.sin(2 * Math.PI * Math.max(1, p.lowHz || 32) * t + 0.15) +
      0.22 * Math.sin(2 * Math.PI * Math.max(1, (p.lowHz || 32) * 0.52) * t + 1.10)
    );

    const lowLayer = lowLayerSample(t, p);
    const highLayer = highLayerSample(t, p);

    const deterministicJitter =
      p.jitter *
      (0.55 * Math.sin(2 * Math.PI * (7.3 + 18 * (p.accel || 0)) * t) +
       0.30 * Math.sin(2 * Math.PI * (13.7 + 32 * (p.tailSpeed || 0)) * t + 1.3) +
       0.15 * Math.sin(2 * Math.PI * 23.1 * t + 0.4));

    const y =
      env * am * (Math.sin(phase) + (p.detuneMix || 0) * Math.sin(detunePhase)) / (1 + (p.detuneMix || 0)) +
      second * Math.sin(phase2) +
      env * deterministicJitter +
      env * tailPuru +
      low +
      lowLayer +
      highLayer;

    data.push({ t, y, env, f });
  }
  return data;
}

function draw() {
  updateOutputs();
  fitCanvas();

  const p = getP();
  const ctx = els.canvas.getContext('2d');
  const W = els.canvas.width;
  const H = els.canvas.height;
  const data = sampleWave(p);

  ctx.clearRect(0, 0, W, H);

  const padL = 54, padR = 18, padT = 20, padB = 34;
  const cw = W - padL - padR;
  const ch = H - padT - padB;
  const midY = padT + ch * 0.5;

  ctx.fillStyle = '#0b1220';
  ctx.fillRect(0, 0, W, H);

  ctx.strokeStyle = 'rgba(255,255,255,0.08)';
  ctx.lineWidth = 1;
  for (let i = 0; i <= 8; i++) {
    const x = padL + cw * i / 8;
    ctx.beginPath();
    ctx.moveTo(x, padT);
    ctx.lineTo(x, padT + ch);
    ctx.stroke();
  }
  for (let i = 0; i <= 4; i++) {
    const y = padT + ch * i / 4;
    ctx.beginPath();
    ctx.moveTo(padL, y);
    ctx.lineTo(padL + cw, y);
    ctx.stroke();
  }

  ctx.strokeStyle = 'rgba(250,204,21,0.35)';
  ctx.beginPath();
  ctx.moveTo(padL, midY);
  ctx.lineTo(padL + cw, midY);
  ctx.stroke();

  const maxAbs = Math.max(0.01, ...data.map(d => Math.abs(d.y)));
  const yScale = (ch * 0.45) / maxAbs;

  ctx.strokeStyle = '#38bdf8';
  ctx.lineWidth = Math.max(2, window.devicePixelRatio || 1);
  ctx.beginPath();

  data.forEach((d, i) => {
    const x = padL + (d.t / p.duration) * cw;
    const y = midY - d.y * yScale;
    if (i === 0) ctx.moveTo(x, y);
    else ctx.lineTo(x, y);
  });
  ctx.stroke();

  // envelope guide
  ctx.strokeStyle = 'rgba(167,243,208,0.35)';
  ctx.lineWidth = 1;
  ctx.beginPath();
  data.forEach((d, i) => {
    const x = padL + (d.t / p.duration) * cw;
    const y = midY - d.env * yScale;
    if (i === 0) ctx.moveTo(x, y);
    else ctx.lineTo(x, y);
  });
  ctx.stroke();

  // legacy delayed low-band guide
  if ((p.lowAmp || 0) > 0) {
    ctx.strokeStyle = 'rgba(251,191,36,0.45)';
    ctx.lineWidth = 1;
    ctx.beginPath();
    data.forEach((d, i) => {
      const x = padL + (d.t / p.duration) * cw;
      const y = midY - (p.lowAmp || 0) * lowEnvelope(d.t, p) * yScale;
      if (i === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    });
    ctx.stroke();
  }

  // low layer guide（別トラックの低域共振）
  if ((p.lowLayerAmp || 0) > 0) {
    ctx.strokeStyle = 'rgba(251,146,60,0.75)';
    ctx.lineWidth = Math.max(1, window.devicePixelRatio || 1);
    ctx.beginPath();
    data.forEach((d, i) => {
      const x = padL + (d.t / p.duration) * cw;
      const y = midY - (p.lowLayerAmp || 0) * lowLayerEnvelope(d.t, p) * yScale;
      if (i === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    });
    ctx.stroke();
  }

  // high layer guide（別トラックの高域きらめき）
  if ((p.highLayerAmp || 0) > 0) {
    ctx.strokeStyle = 'rgba(244,114,182,0.78)';
    ctx.lineWidth = Math.max(1, window.devicePixelRatio || 1);
    ctx.beginPath();
    data.forEach((d, i) => {
      const x = padL + (d.t / p.duration) * cw;
      const y = midY - (p.highLayerAmp || 0) * highLayerEnvelope(d.t, p) * yScale;
      if (i === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    });
    ctx.stroke();
  }

  ctx.fillStyle = '#cbd5e1';
  ctx.font = `${12 * (window.devicePixelRatio || 1)}px system-ui`;
  ctx.textAlign = 'left';
  ctx.fillText('0s', padL, H - 10);
  ctx.textAlign = 'right';
  ctx.fillText(`${p.duration.toFixed(1)}s`, padL + cw, H - 10);

  ctx.textAlign = 'left';
  ctx.fillStyle = '#93c5fd';
  ctx.fillText('main puru wave', padL + 8, padT + 18);
}

function stop() {
  for (const n of playingNodes) {
    try {
      if (n.stop) n.stop();
      if (n.disconnect) n.disconnect();
    } catch (_) {}
  }
  playingNodes = [];
}

async function play() {
  stop();
  const p = getP();
  audioCtx = audioCtx || new (window.AudioContext || window.webkitAudioContext)();
  await audioCtx.resume();

  const now = audioCtx.currentTime;
  const master = audioCtx.createGain();
  master.gain.setValueAtTime(0, now);
  master.gain.linearRampToValueAtTime(p.volume, now + 0.03);
  master.gain.setValueAtTime(p.volume, now + Math.max(0.04, p.duration - 0.08));
  master.gain.linearRampToValueAtTime(0, now + p.duration);

  const osc = audioCtx.createOscillator();
  osc.type = 'sine';

  const gain = audioCtx.createGain();
  gain.gain.setValueAtTime(p.amp, now);

  const steps = 320;
  for (let i = 0; i <= steps; i++) {
    const t = p.duration * i / steps;
    const at = now + t;
    const f = freqAt(t, p);
    const env = p.amp * Math.exp(-p.decay * t);
    const am = amAt(t, p);

    osc.frequency.linearRampToValueAtTime(f, at);
    gain.gain.linearRampToValueAtTime(Math.max(0, env * am), at);
  }

  const second = audioCtx.createOscillator();
  second.type = 'triangle';
  const secondGain = audioCtx.createGain();
  secondGain.gain.setValueAtTime(0, now);

  const secondCenter = now + p.duration * p.secondPos;
  second.frequency.setValueAtTime((p.f0 + p.f1) * 0.85 + 20, now);
  secondGain.gain.linearRampToValueAtTime(0, Math.max(now, secondCenter - p.duration * 0.10));
  secondGain.gain.linearRampToValueAtTime(p.secondAmp, secondCenter);
  secondGain.gain.linearRampToValueAtTime(0, Math.min(now + p.duration, secondCenter + p.duration * 0.14));

  const detuneOsc = audioCtx.createOscillator();
  detuneOsc.type = 'sine';
  const detuneGain = audioCtx.createGain();
  detuneGain.gain.setValueAtTime(0, now);

  const detuneMix = Math.max(0, Math.min(1, p.detuneMix || 0));
  for (let i = 0; i <= steps; i++) {
    const t = p.duration * i / steps;
    const at = now + t;
    const f = freqAt(t, p) + (p.detuneHz || 0);
    const env = p.amp * Math.exp(-p.decay * t);
    const am = amAt(t, p);
    detuneOsc.frequency.linearRampToValueAtTime(Math.max(1, f), at);
    detuneGain.gain.linearRampToValueAtTime(Math.max(0, env * am * detuneMix), at);
  }

  const lfo = audioCtx.createOscillator();
  lfo.type = 'sine';
  lfo.frequency.setValueAtTime(9.5 + 26 * (p.accel || 0), now);
  const lfoGain = audioCtx.createGain();
  lfoGain.gain.setValueAtTime(p.jitter * (70 + 70 * (p.tailSpeed || 0)), now);
  lfo.connect(lfoGain).connect(osc.frequency);

  // 尾っぽ高速ぷるぷる専用。最後にだけ細かい震えを残す。
  const tailOsc = audioCtx.createOscillator();
  tailOsc.type = 'triangle';
  const tailGain = audioCtx.createGain();
  const tailStart = now + p.duration * 0.58;
  const tailPeak = now + p.duration * 0.74;
  const tailEnd = now + p.duration;
  tailOsc.frequency.setValueAtTime(Math.max(20, p.f1 * (0.65 + 1.25 * (p.tailSpeed || 0))), now);
  tailGain.gain.setValueAtTime(0, now);
  tailGain.gain.setValueAtTime(0, tailStart);
  tailGain.gain.linearRampToValueAtTime(p.amp * (p.tailSpeed || 0) * 0.26, tailPeak);
  tailGain.gain.linearRampToValueAtTime(0, tailEnd);


  // 低域 Attack Delay 専用。主旋律に遅れて、低域だけふくらませる。
  const lowOsc = audioCtx.createOscillator();
  lowOsc.type = 'sine';
  const lowGain = audioCtx.createGain();
  lowGain.gain.setValueAtTime(0, now);
  lowOsc.frequency.setValueAtTime(Math.max(1, p.lowHz || 32), now);
  const lowSteps = 160;
  for (let i = 0; i <= lowSteps; i++) {
    const t = p.duration * i / lowSteps;
    const at = now + t;
    const g = Math.max(0, (p.lowAmp || 0) * lowEnvelope(t, p));
    lowGain.gain.linearRampToValueAtTime(g, at);
  }


  // 低域Layer（別トラック）。主ぷるとは別の発振器・別のゲイン包絡・別のヨレを持つ。
  const lowLayerOsc = audioCtx.createOscillator();
  lowLayerOsc.type = 'sine';
  const lowLayerGain = audioCtx.createGain();
  lowLayerGain.gain.setValueAtTime(0, now);

  const lowLayerFilter = audioCtx.createBiquadFilter();
  lowLayerFilter.type = 'lowpass';
  lowLayerFilter.frequency.setValueAtTime(95, now);
  lowLayerFilter.Q.setValueAtTime(0.7, now);

  const lowLayerSteps = 260;
  lowLayerOsc.frequency.setValueAtTime(Math.max(1, lowLayerFreqAt(0, p)), now);
  for (let i = 0; i <= lowLayerSteps; i++) {
    const t = p.duration * i / lowLayerSteps;
    const at = now + t;
    lowLayerOsc.frequency.linearRampToValueAtTime(Math.max(1, lowLayerFreqAt(t, p)), at);
    lowLayerGain.gain.linearRampToValueAtTime(Math.max(0, (p.lowLayerAmp || 0) * lowLayerEnvelope(t, p)), at);
  }

  // 倍音用の薄いサブトラック。低域Layerの“生き物感”だけを足す。
  const lowLayerSubOsc = audioCtx.createOscillator();
  lowLayerSubOsc.type = 'triangle';
  lowLayerSubOsc.frequency.setValueAtTime(Math.max(1, lowLayerFreqAt(0, p) * 0.52), now);
  const lowLayerSubGain = audioCtx.createGain();
  lowLayerSubGain.gain.setValueAtTime(0, now);
  for (let i = 0; i <= lowLayerSteps; i++) {
    const t = p.duration * i / lowLayerSteps;
    const at = now + t;
    const f = Math.max(1, lowLayerFreqAt(t, p));
    lowLayerSubOsc.frequency.linearRampToValueAtTime(Math.max(1, f * 0.52), at);
    lowLayerSubGain.gain.linearRampToValueAtTime(Math.max(0, (p.lowLayerAmp || 0) * (p.lowLayerHarmonic || 0) * 0.35 * lowLayerEnvelope(t, p)), at);
  }



  // 高域Layer（別トラック）。ジリジリ/きらめき用。主ぷるから独立して足す。
  const highLayerOsc = audioCtx.createOscillator();
  highLayerOsc.type = 'sine';
  const highLayerGain = audioCtx.createGain();
  highLayerGain.gain.setValueAtTime(0, now);

  const highLayerFilter = audioCtx.createBiquadFilter();
  highLayerFilter.type = 'highpass';
  highLayerFilter.frequency.setValueAtTime(110, now);
  highLayerFilter.Q.setValueAtTime(0.65, now);

  const highLayerSteps = 300;
  highLayerOsc.frequency.setValueAtTime(Math.max(1, highLayerFreqAt(0, p)), now);
  for (let i = 0; i <= highLayerSteps; i++) {
    const t = p.duration * i / highLayerSteps;
    const at = now + t;
    highLayerOsc.frequency.linearRampToValueAtTime(Math.max(1, highLayerFreqAt(t, p)), at);
    highLayerGain.gain.linearRampToValueAtTime(Math.max(0, (p.highLayerAmp || 0) * highLayerEnvelope(t, p)), at);
  }

  // 高域倍音。強すぎると耳に刺さるので控えめ。
  const highLayerUpperOsc = audioCtx.createOscillator();
  highLayerUpperOsc.type = 'triangle';
  highLayerUpperOsc.frequency.setValueAtTime(Math.max(1, highLayerFreqAt(0, p) * 1.5), now);
  const highLayerUpperGain = audioCtx.createGain();
  highLayerUpperGain.gain.setValueAtTime(0, now);
  for (let i = 0; i <= highLayerSteps; i++) {
    const t = p.duration * i / highLayerSteps;
    const at = now + t;
    const f = Math.max(1, highLayerFreqAt(t, p));
    highLayerUpperOsc.frequency.linearRampToValueAtTime(Math.max(1, f * 1.5), at);
    highLayerUpperGain.gain.linearRampToValueAtTime(Math.max(0, (p.highLayerAmp || 0) * (p.highLayerHarmonic || 0) * 0.24 * highLayerEnvelope(t, p)), at);
  }

  osc.connect(gain).connect(master);
  detuneOsc.connect(detuneGain).connect(master);
  second.connect(secondGain).connect(master);
  tailOsc.connect(tailGain).connect(master);
  lowOsc.connect(lowGain).connect(master);
  lowLayerOsc.connect(lowLayerGain).connect(lowLayerFilter).connect(master);
  lowLayerSubOsc.connect(lowLayerSubGain).connect(lowLayerFilter);
  highLayerOsc.connect(highLayerGain).connect(highLayerFilter).connect(master);
  highLayerUpperOsc.connect(highLayerUpperGain).connect(highLayerFilter);
  master.connect(audioCtx.destination);

  osc.start(now);
  detuneOsc.start(now);
  second.start(now);
  lfo.start(now);
  tailOsc.start(now);
  lowOsc.start(now);
  lowLayerOsc.start(now);
  lowLayerSubOsc.start(now);
  highLayerOsc.start(now);
  highLayerUpperOsc.start(now);

  osc.stop(now + p.duration + 0.02);
  detuneOsc.stop(now + p.duration + 0.02);
  second.stop(now + p.duration + 0.02);
  lfo.stop(now + p.duration + 0.02);
  tailOsc.stop(now + p.duration + 0.02);
  lowOsc.stop(now + p.duration + 0.02);
  lowLayerOsc.stop(now + p.duration + 0.02);
  lowLayerSubOsc.stop(now + p.duration + 0.02);
  highLayerOsc.stop(now + p.duration + 0.02);
  highLayerUpperOsc.stop(now + p.duration + 0.02);

  playingNodes = [osc, detuneOsc, second, lfo, tailOsc, lowOsc, lowLayerOsc, lowLayerSubOsc, highLayerOsc, highLayerUpperOsc, gain, detuneGain, secondGain, tailGain, lowGain, lowLayerGain, lowLayerSubGain, highLayerGain, highLayerUpperGain, lowLayerFilter, highLayerFilter, master];
}

function setPreset(name) {
  const presets = {
    soft: {
      duration: 12, amp: 0.70, decay: 0.18, f0: 18, f1: 95, curve: 1.2,
      speedBoost: 0.85, accel: 0.20, tailSpeed: 0.25,
      secondAmp: 0.12, secondPos: 0.55, jitter: 0.04, lowAmp: 0.08, lowHz: 30, lowDelay: 1.05, lowRise: 0.65, lowTail: 4.0, lowLayerAmp: 0.26, lowLayerHz: 42, lowLayerDelay: 0.65, lowLayerAttack: 0.60, lowLayerHold: 2.6, lowLayerRelease: 4.4, lowLayerWobbleHz: 0.14, lowLayerWobbleDepth: 0.07, lowLayerHarmonic: 0.16, highLayerAmp: 0.10, highLayerHz: 210, highLayerDelay: 0.55, highLayerAttack: 0.12, highLayerHold: 1.7, highLayerRelease: 2.8, highLayerShimmerHz: 3.5, highLayerShimmerDepth: 0.10, highLayerHarmonic: 0.18, volume: 0.34,
      modFreq: 3.5, modDepth: 0.22, detuneHz: 2.0, detuneMix: 0.22, detunePhase: 0
    },
    tokujou: {
      duration: 10, amp: 0.92, decay: 0.24, f0: 20, f1: 170, curve: 1.8,
      speedBoost: 1.15, accel: 0.45, tailSpeed: 0.45,
      secondAmp: 0.26, secondPos: 0.42, jitter: 0.10, lowAmp: 0.16, lowHz: 32, lowDelay: 0.85, lowRise: 0.55, lowTail: 3.6, lowLayerAmp: 0.38, lowLayerHz: 46, lowLayerDelay: 0.42, lowLayerAttack: 0.36, lowLayerHold: 2.2, lowLayerRelease: 4.0, lowLayerWobbleHz: 0.18, lowLayerWobbleDepth: 0.08, lowLayerHarmonic: 0.22, highLayerAmp: 0.18, highLayerHz: 265, highLayerDelay: 0.18, highLayerAttack: 0.08, highLayerHold: 0.95, highLayerRelease: 1.9, highLayerShimmerHz: 6.0, highLayerShimmerDepth: 0.18, highLayerHarmonic: 0.28, volume: 0.35,
      modFreq: 5.0, modDepth: 0.50, detuneHz: 3.0, detuneMix: 0.35, detunePhase: 0
    },
    sharp: {
      duration: 5, amp: 1.0, decay: 0.55, f0: 35, f1: 230, curve: 2.4,
      speedBoost: 1.80, accel: 0.65, tailSpeed: 0.35,
      secondAmp: 0.10, secondPos: 0.25, jitter: 0.05, lowAmp: 0.04, lowHz: 38, lowDelay: 0.35, lowRise: 0.25, lowTail: 1.4, lowLayerAmp: 0.16, lowLayerHz: 52, lowLayerDelay: 0.18, lowLayerAttack: 0.16, lowLayerHold: 0.7, lowLayerRelease: 1.5, lowLayerWobbleHz: 0.35, lowLayerWobbleDepth: 0.06, lowLayerHarmonic: 0.25, highLayerAmp: 0.28, highLayerHz: 330, highLayerDelay: 0.08, highLayerAttack: 0.04, highLayerHold: 0.45, highLayerRelease: 0.9, highLayerShimmerHz: 11.0, highLayerShimmerDepth: 0.22, highLayerHarmonic: 0.36, volume: 0.30,
      modFreq: 12.0, modDepth: 0.28, detuneHz: 7.0, detuneMix: 0.25, detunePhase: 90
    },
    spring: {
      duration: 2.4, amp: 1.0, decay: 0.95, f0: 24, f1: 320, curve: 2.8,
      speedBoost: 2.65, accel: 0.82, tailSpeed: 0.78,
      secondAmp: 0.34, secondPos: 0.36, jitter: 0.18, lowAmp: 0.18, lowHz: 34, lowDelay: 0.28, lowRise: 0.25, lowTail: 1.8, lowLayerAmp: 0.32, lowLayerHz: 44, lowLayerDelay: 0.22, lowLayerAttack: 0.22, lowLayerHold: 1.1, lowLayerRelease: 2.2, lowLayerWobbleHz: 0.28, lowLayerWobbleDepth: 0.10, lowLayerHarmonic: 0.24, highLayerAmp: 0.24, highLayerHz: 310, highLayerDelay: 0.06, highLayerAttack: 0.05, highLayerHold: 0.35, highLayerRelease: 0.75, highLayerShimmerHz: 13.0, highLayerShimmerDepth: 0.26, highLayerHarmonic: 0.34, volume: 0.30,
      modFreq: 6.5, modDepth: 0.72, detuneHz: 4.5, detuneMix: 0.42, detunePhase: 30
    }
  };

  const p = presets[name];
  if (!p) return;
  for (const [key, value] of Object.entries(p)) {
    if (params[key]) params[key].value = value;
  }
  draw();
}

for (const el of Object.values(params)) {
  el.addEventListener('input', draw);
  el.addEventListener('change', draw);
}

document.querySelectorAll('[data-preset]').forEach(btn => {
  btn.addEventListener('click', () => setPreset(btn.dataset.preset));
});

els.playBtn.addEventListener('click', play);
els.stopBtn.addEventListener('click', stop);

if (els.saveSettingsBtn) {
  els.saveSettingsBtn.addEventListener('click', saveSettingsJson);
}

if (els.loadSettingsBtn && els.loadSettingsInput) {
  els.loadSettingsBtn.addEventListener('click', () => els.loadSettingsInput.click());
  els.loadSettingsInput.addEventListener('change', (event) => {
    const file = event.target.files && event.target.files[0];
    loadSettingsJson(file);
  });
}

window.addEventListener('resize', draw);

draw();
