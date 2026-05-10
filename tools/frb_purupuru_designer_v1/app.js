const els = {
  canvas: document.getElementById('waveCanvas'),
  playBtn: document.getElementById('playBtn'),
  stopBtn: document.getElementById('stopBtn'),
  formulaText: document.getElementById('formulaText'),
  timeReadout: document.getElementById('timeReadout'),
  freqReadout: document.getElementById('freqReadout'),
};

const params = {
  duration: document.getElementById('duration'),
  amp: document.getElementById('amp'),
  decay: document.getElementById('decay'),
  f0: document.getElementById('f0'),
  f1: document.getElementById('f1'),
  curve: document.getElementById('curve'),
  secondAmp: document.getElementById('secondAmp'),
  secondPos: document.getElementById('secondPos'),
  jitter: document.getElementById('jitter'),
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

function fmt(key, v) {
  if (key === 'duration') return `${v.toFixed(1)}s`;
  if (key === 'f0' || key === 'f1') return `${v.toFixed(1)}Hz`;
  if (key === 'secondPos') return `${Math.round(v * 100)}%`;
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
    `y(t)=A·e^(-λt)·sin(2π∫f(t)dt) + 第2波 + 微細ゆらぎ`;
}

function fitCanvas() {
  const dpr = window.devicePixelRatio || 1;
  const rect = els.canvas.getBoundingClientRect();
  els.canvas.width = Math.max(600, Math.floor(rect.width * dpr));
  els.canvas.height = Math.max(260, Math.floor(rect.height * dpr));
}

function freqAt(t, p) {
  const u = Math.max(0, Math.min(1, t / p.duration));
  const shaped = Math.pow(u, p.curve);
  return p.f0 + (p.f1 - p.f0) * shaped;
}

function secondEnvelope(t, p) {
  const center = p.duration * p.secondPos;
  const width = Math.max(0.08, p.duration * 0.08);
  const x = (t - center) / width;
  return p.secondAmp * Math.exp(-x * x);
}

function sampleWave(p, samples = 1600) {
  const data = [];
  let phase = 0;
  let phase2 = 0;
  const dt = p.duration / samples;

  for (let i = 0; i <= samples; i++) {
    const t = i * dt;
    const f = freqAt(t, p);
    phase += 2 * Math.PI * f * dt;

    const env = p.amp * Math.exp(-p.decay * t);
    const second = secondEnvelope(t, p);

    phase2 += 2 * Math.PI * (f * 1.7 + 18) * dt;

    const deterministicJitter =
      p.jitter *
      (0.55 * Math.sin(2 * Math.PI * 7.3 * t) +
       0.30 * Math.sin(2 * Math.PI * 13.7 * t + 1.3) +
       0.15 * Math.sin(2 * Math.PI * 23.1 * t + 0.4));

    const y =
      env * Math.sin(phase) +
      second * Math.sin(phase2) +
      env * deterministicJitter;

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

  const steps = 180;
  for (let i = 0; i <= steps; i++) {
    const t = p.duration * i / steps;
    const at = now + t;
    const f = freqAt(t, p);
    const env = p.amp * Math.exp(-p.decay * t);

    osc.frequency.linearRampToValueAtTime(f, at);
    gain.gain.linearRampToValueAtTime(Math.max(0, env), at);
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

  const lfo = audioCtx.createOscillator();
  lfo.type = 'sine';
  lfo.frequency.setValueAtTime(9.5, now);
  const lfoGain = audioCtx.createGain();
  lfoGain.gain.setValueAtTime(p.jitter * 80, now);
  lfo.connect(lfoGain).connect(osc.frequency);

  osc.connect(gain).connect(master);
  second.connect(secondGain).connect(master);
  master.connect(audioCtx.destination);

  osc.start(now);
  second.start(now);
  lfo.start(now);

  osc.stop(now + p.duration + 0.02);
  second.stop(now + p.duration + 0.02);
  lfo.stop(now + p.duration + 0.02);

  playingNodes = [osc, second, lfo, gain, secondGain, master];
}

function setPreset(name) {
  const presets = {
    soft: {
      duration: 12, amp: 0.70, decay: 0.18, f0: 18, f1: 95, curve: 1.2,
      secondAmp: 0.12, secondPos: 0.55, jitter: 0.04, volume: 0.34
    },
    tokujou: {
      duration: 10, amp: 0.92, decay: 0.24, f0: 20, f1: 170, curve: 1.8,
      secondAmp: 0.26, secondPos: 0.42, jitter: 0.10, volume: 0.35
    },
    sharp: {
      duration: 5, amp: 1.0, decay: 0.55, f0: 35, f1: 230, curve: 2.4,
      secondAmp: 0.10, secondPos: 0.25, jitter: 0.05, volume: 0.30
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
window.addEventListener('resize', draw);

draw();
