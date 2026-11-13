// Virtual JOIN WriteBack Planner. Generates explicit operations without mutating sources.
// Initial execution supports ONE target; targets[] is future-compatible with N sources.
function planVirtualJoinWriteBack(config, rows, baseline, sourceByName) {
  const targets = config?.writeBack?.targets;
  if (!Array.isArray(targets) || targets.length !== 1)
    throw new Error('left_join writeBack v1 requires exactly one target');
  const target = targets[0];
  const source = sourceByName(target.source);
  const sourceRows = getByPath(source, target.path) ?? [];
  if (!Array.isArray(sourceRows)) throw new Error('writeBack target path must be an array');
  const keyFields = target.keyFields;
  const fields = target.fields;
  if (!Array.isArray(keyFields) || !keyFields.length || !fields || !Object.keys(fields).length)
    throw new Error('writeBack requires keyFields and fields');
  const identity = row => joinKeyForRow(row, keyFields);
  const baselineMap = new Map(baseline.map(row => [identity(row), row]));
  const seen = new Set();
  if (rows.length !== baseline.length || baselineMap.size !== baseline.length)
    throw new Error('Virtual JOIN rows changed; adding/deleting joined rows is not allowed');
  const originalMap = new Map(sourceRows.map(row => [identity(row), row]));
  if (originalMap.size !== sourceRows.length) throw new Error('writeBack has duplicate target keys');
  const operations = [];
  for (const row of rows) {
    const key = identity(row);
    if (seen.has(key) || !baselineMap.has(key))
      throw new Error('Virtual JOIN key changed/duplicated; cannot write back');
    seen.add(key);
    const before = baselineMap.get(key);
    // Only changes to declared editable columns are persisted.
    const values = Object.fromEntries(Object.entries(fields).map(([from,to]) => [to, cloneData(getByPath(row, from) ?? '')]));
    const baselineValues = Object.fromEntries(Object.entries(fields).map(([from,to]) => [to, cloneData(getByPath(before, from) ?? '')]));
    if (JSON.stringify(values) === JSON.stringify(baselineValues)) continue;
    const allBlank = Object.values(values).every(v => v == null || (typeof v === 'string' && !v.trim()));
    const exists = originalMap.has(key);
    if (allBlank && target.deleteWhenBlank === true && exists) {
      operations.push({ op: 'delete', key, source: target.source, path: target.path });
    } else if (!allBlank && !exists && target.insertWhenMissing === true) {
      const newRow = Object.fromEntries(keyFields.map(k => [k, getByPath(before, k)]));
      Object.assign(newRow, values);
      operations.push({ op: 'insert', key, row: newRow, source: target.source, path: target.path });
    } else if (exists) {
      operations.push({ op: 'update', key, values, source: target.source, path: target.path });
    }
  }
  return { target, operations };
}

function applyVirtualJoinWriteBackPlan(plan, sourceByName) {
  if (!plan.operations.length) return 0;
  const {target, operations} = plan;
  const source = sourceByName(target.source);
  let rows = getByPath(source, target.path);
  if (rows === undefined) { rows = []; setByPath(source, target.path, rows); }
  if (!Array.isArray(rows)) throw new Error('writeBack target path must be an array');
  const keyOf = row => joinKeyForRow(row, target.keyFields);
  for (const op of operations) {
    const i = rows.findIndex(row => keyOf(row) === op.key);
    if (op.op === 'insert') {
      if (i >= 0) throw new Error('WriteBack concurrent insert conflict');
      rows.push(op.row);
    } else {
      if (i < 0) throw new Error('WriteBack missing source row');
      if (op.op === 'delete') rows.splice(i, 1);
      else Object.assign(rows[i], op.values);
    }
  }
  return operations.length;
}

function virtualJoinHasPendingEdits() {
  if (typeof viewDef === 'undefined' || !viewDef || typeof sourceData === 'undefined' || !sourceData) return false;
  for (const config of virtualDataArrayConfigOf(viewDef)) {
    if (virtualDataBuilderName(config) !== 'left_join') continue;
    const path = virtualDataTargetPath(config);
    const baseline = virtualDataJoinBaselines.get(path);
    const current = getByPath(sourceData, path);
    if (baseline && JSON.stringify(current) !== JSON.stringify(baseline)) return true;
  }
  return false;
}
