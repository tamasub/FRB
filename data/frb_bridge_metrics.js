// FRB Bridge Metrics shared logic
// BridgeScore v1 (Legacy) is intentionally preserved as the baseline.
// Research metrics add observability around level / stability / legacy-band breakdown
// without redefining the meaning of the legacy score.
(() => {
  'use strict';

  const SPEC = Object.freeze({
    id: 'frb-bridge-research-0.1',
    legacyId: 'bridge-score-v1-legacy',
    legacyBands: Object.freeze([
      Object.freeze({ key: 'b0', label: 'Low',  range: '0-80Hz',    f0: 0,   f1: 80 }),
      Object.freeze({ key: 'b1', label: 'Mid',  range: '80-160Hz',  f0: 80,  f1: 160 }),
      Object.freeze({ key: 'b2', label: 'High', range: '160-250Hz', f0: 160, f1: 250 }),
    ]),
    stabilityWindowSec: 1.0,
    highBridgeThreshold: 0.80,
    note: 'Legacy score is unchanged. Stability is observation-only and must not be treated as a quality score.'
  });

  const EPS = 1e-9;

  function num(v, fallback = 0) {
    const n = Number(v);
    return Number.isFinite(n) ? n : fallback;
  }

  function clamp01(v) {
    return Math.max(0, Math.min(1, num(v)));
  }

  function calcLegacyDetails(bandA) {
    const low = Math.max(0, num(bandA?.b0));
    const mid = Math.max(0, num(bandA?.b1));
    const high = Math.max(0, num(bandA?.b2));

    const ratioLowMid = mid / (low + EPS);
    const ratioMidHigh = high / (mid + EPS);
    const ratioGap = Math.abs(ratioLowMid - ratioMidHigh);
    const score = 1 / (1 + ratioGap);

    return {
      low,
      mid,
      high,
      ratioLowMid,
      ratioMidHigh,
      ratioGap,
      score: clamp01(score),
      energyTotal: low + mid + high,
    };
  }

  function hasLegacyBandMap(frame) {
    const map = frame?.bandA;
    return !!map && ['b0', 'b1', 'b2'].some(k => Number.isFinite(Number(map[k])));
  }

  function getLegacyDetailsFromFrame(frame) {
    if (hasLegacyBandMap(frame)) return calcLegacyDetails(frame.bandA);

    // Old logs may not have bandA. Keep display compatibility with the stored score.
    const fallbackScore = clamp01(
      Number.isFinite(Number(frame?.bridgeLegacyScore))
        ? Number(frame.bridgeLegacyScore)
        : num(frame?.stairError)
    );
    return {
      low: NaN,
      mid: NaN,
      high: NaN,
      ratioLowMid: NaN,
      ratioMidHigh: NaN,
      ratioGap: NaN,
      score: fallbackScore,
      energyTotal: NaN,
    };
  }

  function getLegacyScoreFromFrame(frame) {
    return getLegacyDetailsFromFrame(frame).score;
  }

  function mean(values) {
    const xs = values.map(Number).filter(Number.isFinite);
    if (!xs.length) return NaN;
    return xs.reduce((a, b) => a + b, 0) / xs.length;
  }

  function populationSd(values, avg = NaN) {
    const xs = values.map(Number).filter(Number.isFinite);
    if (!xs.length) return NaN;
    const m = Number.isFinite(avg) ? avg : mean(xs);
    return Math.sqrt(xs.reduce((sum, x) => sum + (x - m) ** 2, 0) / xs.length);
  }

  function percentile(values, p) {
    const xs = values.map(Number).filter(Number.isFinite).sort((a, b) => a - b);
    if (!xs.length) return NaN;
    const q = Math.max(0, Math.min(1, num(p)));
    const pos = (xs.length - 1) * q;
    const lo = Math.floor(pos);
    const hi = Math.ceil(pos);
    if (lo === hi) return xs[lo];
    const w = pos - lo;
    return xs[lo] * (1 - w) + xs[hi] * w;
  }

  function getRollingStats(series, index, windowSec = SPEC.stabilityWindowSec) {
    const src = Array.isArray(series) ? series : [];
    if (!src.length || index < 0 || index >= src.length) {
      return { count: 0, mean: NaN, sd: NaN, stability: NaN };
    }

    const t = num(src[index]?.t, index);
    const startT = t - Math.max(0.05, num(windowSec, SPEC.stabilityWindowSec));
    const values = [];

    for (let i = index; i >= 0; i--) {
      const ti = num(src[i]?.t, i);
      if (ti < startT) break;
      values.push(getLegacyScoreFromFrame(src[i]));
    }

    const avg = mean(values);
    const sd = populationSd(values, avg);
    // BridgeScore itself is bounded [0,1]. Its theoretical maximum population SD is 0.5.
    // Therefore 1 - 2*SD is a transparent 0..1 normalization of *stability only*.
    // It says nothing about whether the score level itself is high or low.
    const stability = Number.isFinite(sd) ? clamp01(1 - 2 * sd) : NaN;

    return { count: values.length, mean: avg, sd, stability };
  }

  function deriveSeries(series, windowSec = SPEC.stabilityWindowSec) {
    const src = Array.isArray(series) ? series : [];
    return src.map((frame, index) => {
      const details = getLegacyDetailsFromFrame(frame);
      const rolling = getRollingStats(src, index, windowSec);
      return {
        t: num(frame?.t, index),
        ...details,
        rollingMean: rolling.mean,
        rollingSd: rolling.sd,
        stability: rolling.stability,
        rollingCount: rolling.count,
      };
    });
  }

  function summarize(series, threshold = SPEC.highBridgeThreshold) {
    const derived = deriveSeries(series);
    const scores = derived.map(x => x.score).filter(Number.isFinite);
    const low = derived.map(x => x.low).filter(Number.isFinite);
    const mid = derived.map(x => x.mid).filter(Number.isFinite);
    const high = derived.map(x => x.high).filter(Number.isFinite);
    const r1 = derived.map(x => x.ratioLowMid).filter(Number.isFinite);
    const r2 = derived.map(x => x.ratioMidHigh).filter(Number.isFinite);
    const gaps = derived.map(x => x.ratioGap).filter(Number.isFinite);

    const scoreMean = mean(scores);
    const scoreSd = populationSd(scores, scoreMean);
    const highCount = scores.filter(x => x >= threshold).length;

    return {
      count: scores.length,
      scoreMean,
      scoreSd,
      scoreP10: percentile(scores, 0.10),
      highThreshold: threshold,
      highOccupancy: scores.length ? highCount / scores.length : NaN,
      stabilityOverall: Number.isFinite(scoreSd) ? clamp01(1 - 2 * scoreSd) : NaN,
      lowMean: mean(low),
      midMean: mean(mid),
      highMean: mean(high),
      ratioLowMidMean: mean(r1),
      ratioMidHighMean: mean(r2),
      ratioGapMean: mean(gaps),
    };
  }

  window.FRBBridgeMetrics = Object.freeze({
    SPEC,
    calcLegacyDetails,
    getLegacyDetailsFromFrame,
    getLegacyScoreFromFrame,
    getRollingStats,
    deriveSeries,
    summarize,
    mean,
    populationSd,
    percentile,
  });
})();
