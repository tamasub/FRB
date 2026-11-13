// Generic VirtualData LEFT JOIN (independent of JSON/SQLite source adapters).
// Display/entry fields are projected into a virtual-only array; source rows are never changed here.
function joinKeyForRow(row, fields) {
  return JSON.stringify(fields.map(field => String(getByPath(row, field) ?? '').trim().toLowerCase()));
}

function projectedJoinFields(row, mappings) {
  const projected = {};
  for (const [to, from] of Object.entries(mappings ?? {})) {
    const value = getByPath(row, from);
    if (value !== undefined) projected[to] = cloneData(value);
  }
  return projected;
}

function buildLeftJoinRows({config, dataObj, sources}) {
  const left = config.left, right = config.right;
  if (!left || !right) throw new Error('left_join requires left and right');
  const resolve = spec => (spec.source === '$current' ? dataObj : sources[spec.source]);
  const leftRows = getByPath(resolve(left), left.path);
  const rightRows = getByPath(resolve(right), right.path) ?? [];
  if (!Array.isArray(leftRows) || !Array.isArray(rightRows))
    throw new Error('left_join requires array source paths');
  const keys = config.keys ?? [];
  if (!keys.length || !keys.every(k => k.left && k.right))
    throw new Error('left_join requires explicit keys');
  const leftKeys = keys.map(k => k.left), rightKeys = keys.map(k => k.right);
  const rightMap = new Map();
  for (const row of rightRows) {
    const key = joinKeyForRow(row, rightKeys);
    if (rightMap.has(key)) throw new Error(`left_join duplicate right-side key: ${key}`);
    rightMap.set(key, row);
  }
  const seen = new Set();
  return leftRows.map(row => {
    const key = joinKeyForRow(row, leftKeys);
    if (seen.has(key)) throw new Error(`left_join duplicate left-side key: ${key}`);
    seen.add(key);
    const matched = rightMap.get(key);
    return {
      ...projectedJoinFields(row, left.fields),
      ...projectedJoinFields(matched, right.fields),
      ...(matched ? {} : Object.fromEntries(Object.keys(right.fields ?? {}).map(field => [field, ''])))
    };
  });
}

registerVirtualDataBuilder('left_join', buildLeftJoinRows);
