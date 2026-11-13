// studio_work_0269 Step 4 - shared, dependency-free diff contract for browser / Node.
// Browser: window.FrbStudioChangeDiff; Node CJS: require(...).
// No document mutation, DOM access, I/O, or domain-specific field names.
(function exposeFrbStudioChangeDiff(root) {
  'use strict';
  const isObject = value => value !== null && typeof value === 'object' && !Array.isArray(value);
  const clone = value => structuredClone(value);
  const pointerPart = value => String(value).replaceAll('~', '~0').replaceAll('/', '~1');
  const canonical = value => JSON.stringify(value, (_key, v) =>
    isObject(v) ? Object.fromEntries(Object.keys(v).sort().map(k => [k, v[k]])) : v);

  function compareDiff(left, right, path = '') {
    if (canonical(left) === canonical(right)) return [];
    if (Array.isArray(left) && Array.isArray(right)) {
      const out = [];
      for (let i = 0; i < Math.max(left.length, right.length); i++) {
        const p = `${path}/${i}`;
        if (i >= left.length) out.push({ op: 'add', path: p, value: clone(right[i]) });
        else if (i >= right.length) out.push({ op: 'remove', path: p, before: clone(left[i]) });
        else out.push(...compareDiff(left[i], right[i], p));
      }
      return out;
    }
    if (isObject(left) && isObject(right)) {
      const out = [];
      for (const k of new Set([...Object.keys(left), ...Object.keys(right)])) {
        const p = `${path}/${pointerPart(k)}`;
        if (!Object.hasOwn(right, k)) out.push({ op: 'remove', path: p, before: clone(left[k]) });
        else if (!Object.hasOwn(left, k)) out.push({ op: 'add', path: p, value: clone(right[k]) });
        else out.push(...compareDiff(left[k], right[k], p));
      }
      return out;
    }
    return [{ op: 'replace', path: path || '/', before: clone(left), value: clone(right) }];
  }

  // Compare by full diff entry, including op, path and value; never silently allow
  // unexpected replacement/removal. Missing expected entries are also reported.
  function compareExpectedActual(expectedDiff, actualDiff) {
    const fingerprint = entry => canonical(entry);
    const expected = new Map(expectedDiff.map(d => [d.path, fingerprint(d)]));
    const actual = new Map(actualDiff.map(d => [d.path, fingerprint(d)]));
    const unexpected = actualDiff.filter(d => expected.get(d.path) !== fingerprint(d));
    for (const d of expectedDiff) {
      if (actual.get(d.path) !== fingerprint(d)) {
        unexpected.push({ op: 'missing_expected', path: d.path, value: clone(d.value) });
      }
    }
    return unexpected;
  }

  const api = Object.freeze({ compareDiff, compareExpectedActual });
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  if (root) root.FrbStudioChangeDiff = api;
})(typeof window !== 'undefined' ? window : null);
