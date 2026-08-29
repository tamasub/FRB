import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';

const ROOT = path.resolve(import.meta.dirname, '../../..');

function walkFiles(dir, out=[]) {
  if (!fs.existsSync(dir)) return out;
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) walkFiles(full, out);
    else if (entry.isFile() && /view_?def|viewdef/i.test(entry.name) && entry.name.endsWith('.json')) out.push(full);
  }
  return out;
}

function valueKind(value) {
  if (Array.isArray(value)) return 'array';
  if (value === null) return 'null';
  if (typeof value === 'boolean') return 'boolean';
  if (typeof value === 'number') return 'number';
  if (value && typeof value === 'object') return 'object';
  return 'string';
}

function scanNode(node, file, jsonPath='$', findings=[]) {
  if (Array.isArray(node)) {
    node.forEach((item, index) => scanNode(item, file, `${jsonPath}[${index}]`, findings));
    return findings;
  }
  if (!node || typeof node !== 'object') return findings;

  if (node.defaultItem && typeof node.defaultItem === 'object' && !Array.isArray(node.defaultItem) && Array.isArray(node.columns)) {
    const columns = new Map(node.columns.filter(item => item && typeof item === 'object' && item.field).map(item => [item.field, item]));
    for (const [field, value] of Object.entries(node.defaultItem)) {
      const column = columns.get(field);
      if (!column) continue;
      const kind = valueKind(value);
      const type = String(column.type ?? 'text').toLowerCase();

      if ((kind === 'array' || kind === 'object') && type !== 'json') {
        findings.push(`${path.relative(ROOT, file)} ${jsonPath}.${field}: defaultItem=${kind} but column.type=${type}`);
      }
      if (kind === 'number' && !['number', 'integer', 'float', 'decimal', 'json'].includes(type)) {
        findings.push(`${path.relative(ROOT, file)} ${jsonPath}.${field}: defaultItem=number but column.type=${type}`);
      }
      if (kind === 'boolean' && !['boolean', 'json'].includes(type)) {
        findings.push(`${path.relative(ROOT, file)} ${jsonPath}.${field}: defaultItem=boolean but column.type=${type}`);
      }
    }
  }

  if (Array.isArray(node.columns)) {
    node.columns.forEach((column, index) => {
      if (!column || typeof column !== 'object') return;
      const display = String(column.grid?.display ?? '').toLowerCase();
      const type = String(column.type ?? 'text').toLowerCase();
      if (display === 'json' && type !== 'json') {
        findings.push(`${path.relative(ROOT, file)} ${jsonPath}.columns[${index}].${column.field ?? '?'}: grid.display=json but column.type=${type}`);
      }
    });
  }

  for (const [key, value] of Object.entries(node)) {
    scanNode(value, file, `${jsonPath}.${key}`, findings);
  }
  return findings;
}

test('all ViewDefs satisfy SubGrid canonical type / editor type compatibility conditions', () => {
  const candidates = [
    ...walkFiles(path.join(ROOT, 'defs')),
    ...walkFiles(path.join(ROOT, 'wwwroot', 'defs')),
    ...walkFiles(path.join(ROOT, 'wwwroot', 'config')),
    ...walkFiles(path.join(ROOT, 'data', 'json')),
    ...walkFiles(path.join(ROOT, 'studio_overlays'))
  ];
  const uniqueFiles = [...new Set(candidates)];
  const findings = [];

  for (const file of uniqueFiles) {
    let parsed;
    try {
      parsed = JSON.parse(fs.readFileSync(file, 'utf8').replace(/^\uFEFF/, ''));
    } catch {
      continue;
    }
    scanNode(parsed, file, '$', findings);
  }

  assert.deepEqual(findings, [], [
    'View Round-trip Type Drift risk detected.',
    'Composite(Array/Object) requires type=json; Number requires numeric/json; Boolean requires boolean/json.',
    'grid.display=json is presentation only and must not be used instead of type=json.',
    ...findings
  ].join('\n'));
});

test('runtime contains untouched-value preservation in addition to ViewDef static guards', () => {
  const source = fs.readFileSync(path.join(ROOT, 'wwwroot/js/runtime/detail_subgrid_edit.js'), 'utf8');
  assert.match(source, /View Round-trip Type Preservation/);
  assert.match(source, /未編集セルは画面上の文字列表現から再構築せず、元JSON値そのものを保持する/);
  assert.match(source, /__studioSubGridOriginalValue/);
});
