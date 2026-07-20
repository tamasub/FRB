// v0.18.24-thought-evolution-studio-v0-2-relation-approval
// Run from FRBStudio_App root:
//   node --test tests/qa/static/thought_evolution_studio_relation_approval_static.test.mjs

import fs from 'node:fs';
import path from 'node:path';
import test from 'node:test';
import assert from 'node:assert/strict';

const root = process.cwd();
const overlayRoot = path.join(root, 'studio_overlays/thought_evolution');
const readJson = rel => JSON.parse(fs.readFileSync(path.join(root, rel), 'utf8'));
const readOverlayJson = rel => JSON.parse(fs.readFileSync(path.join(overlayRoot, rel), 'utf8'));

const catalog = readOverlayJson('data/thought_evolution_graph_catalog_v0_1.json');
const graph = readOverlayJson('graphs/quality_asset_relation_graph_data_v0_1.json');
const graphDef = readOverlayJson('graph_defs/quality_asset_graph_def_v0_1.json');
const pluginManifest = readOverlayJson('plugins/graph_studio/plugin.json');
const pluginSource = fs.readFileSync(path.join(overlayRoot, 'plugins/graph_studio/plugin.js'), 'utf8');
const loadRuntimeSource = fs.readFileSync(path.join(root, 'wwwroot/js/runtime/load_runtime.js'), 'utf8');

const qualityRow = catalog.graphs.find(row => row.graph_id === 'quality_asset_relation');
const relationPath = qualityRow.relation_data_file;
const relationData = readJson(relationPath);
const relationViewDef = readJson('defs/relation/thought_evolution_relation_approval_view_def_v0_1.json');

test('quality graph declares core RelationData and editable resource refs', () => {
  assert.equal(qualityRow.relation_editable, true);
  assert.equal(relationPath, 'data/json/01_main/thought_evolution_relation_approval_data_v0_1.json');
  assert.equal(relationData.graph_id, qualityRow.graph_id);
  assert.equal(relationData.view_def, 'relation/thought_evolution_relation_approval_view_def_v0_1.json');
  assert.equal(relationViewDef.views[0].sections.find(x => x.id === 'mainGrid').dataPath, 'relations');
  assert.ok(graph.nodes.some(node => node.resource_ref?.data_file && node.resource_ref?.record_field));
  assert.ok(graph.nodes.every(node => !Object.hasOwn(node, 'x') && !Object.hasOwn(node, 'y')));
});

test('RelationData separates AI proposal and human decisions', () => {
  const allowed = new Set(['AI_PROPOSED', 'HUMAN_APPROVED', 'PENDING', 'REJECTED']);
  assert.equal(relationData.relations.length, graph.edges.length);
  assert.ok(relationData.relations.every(item => allowed.has(item.status)));
  assert.ok(relationData.relations.some(item => item.status === 'AI_PROPOSED'));
  assert.ok(relationData.relations.some(item => item.status === 'HUMAN_APPROVED'));
  assert.ok(relationData.relations.every(item => item.reason && Array.isArray(item.evidence_refs)));
  assert.deepEqual(new Set(relationData.relations.map(item => item.relation_id)), new Set(graph.edges.map(item => item.id)));
  assert.equal(graphDef.relation_statuses.length, 4);
});

test('plugin provides core DataBridge, approval actions, and standard editor link', () => {
  assert.equal(pluginManifest.version, '0.4.0');
  for (const permission of ['read_core_data', 'write_core_data', 'open_standard_editor']) {
    assert.ok(pluginManifest.permissions.includes(permission));
  }
  for (const token of [
    'createStudioDataBridge',
    'saveRelations',
    'AI_PROPOSED',
    'HUMAN_APPROVED',
    'data-relation-action="approve"',
    'data-relation-action="reject"',
    'Studio標準エディターで開く',
    "url.searchParams.set('focusField'",
    "window.ThoughtEvolutionStudioV02"
  ]) assert.ok(pluginSource.includes(token), `missing token: ${token}`);
  assert.ok(!/(unpkg|jsdelivr|cdnjs|d3\.js|cytoscape|vis-network)/i.test(pluginSource));
});

test('core URL focus contract selects a record and opens detail', () => {
  for (const token of [
    'applyLaunchFocusFromQuery',
    "params.get('focusField')",
    "params.get('focusValue')",
    "launchBooleanParam(params, 'openDetail'",
    'selectedIndex = index',
    "openDetail(index)"
  ]) assert.ok(loadRuntimeSource.includes(token), `missing core focus token: ${token}`);
});
