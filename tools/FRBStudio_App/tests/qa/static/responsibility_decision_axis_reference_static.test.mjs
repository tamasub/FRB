import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';

const ROOT = process.cwd();
const readJson = rel => JSON.parse(fs.readFileSync(path.join(ROOT, rel), 'utf8'));

test('Responsibility decision_axis_* constraint references resolve to canonical governance item IDs', () => {
  const governance = readJson('data/json/00_rules/frb_coding_constraints_data_v0_3.json');
  const responsibilities = readJson('data/json/03_tests/responsibilities/responsibility_data_v0_2.json');
  const ids = new Set((governance.governance_items ?? []).map(item => item.item_id));
  const unresolved = [];
  for (const responsibility of responsibilities.responsibilities ?? []) {
    for (const id of responsibility.constraint_ids ?? []) {
      if (String(id).startsWith('decision_axis_') && !ids.has(id)) unresolved.push(`${responsibility.responsibility_cd}: ${id}`);
    }
  }
  assert.deepEqual(unresolved, []);
});
