// v0.18.23-thought-evolution-studio-v0-1-generic-graph
// Run from FRBStudio_App root:
//   node --test tests/qa/static/thought_evolution_studio_overlay_static.test.mjs

import fs from 'node:fs';
import path from 'node:path';
import test from 'node:test';
import assert from 'node:assert/strict';

const root = 'studio_overlays/thought_evolution';
const readJson = rel => JSON.parse(fs.readFileSync(path.join(root, rel), 'utf8'));

const manifest = readJson('studio_manifest.json');
const catalog = readJson('data/thought_evolution_graph_catalog_v0_1.json');
const viewDef = readJson('view_defs/thought_evolution_graph_catalog_view_def_v0_1.json');
const pluginIndex = readJson('plugins/plugin_index.json');
const pluginManifest = readJson('plugins/graph_studio/plugin.json');
const pluginSource = fs.readFileSync(path.join(root, 'plugins/graph_studio/plugin.js'), 'utf8');

test('overlay manifest and launcher contract are wired', () => {
  assert.equal(manifest.overlay_id, 'thought_evolution');
  assert.ok(manifest.data_files.includes('data/thought_evolution_graph_catalog_v0_1.json'));
  assert.ok(manifest.view_def_files.includes('view_defs/thought_evolution_graph_catalog_view_def_v0_1.json'));
  assert.ok(manifest.plugin_index_files.includes('plugins/plugin_index.json'));
  assert.equal(viewDef.views[0].toolbar.executeButton.action, 'thought_evolution.open');
  assert.equal(catalog.view_def, 'overlay/thought_evolution/view_defs/thought_evolution_graph_catalog_view_def_v0_1.json');
  assert.equal(pluginIndex.plugins[0].manifest, 'plugins/graph_studio/plugin.json');
  assert.equal(pluginManifest.entry, 'plugin.js');
});

test('all declared graph files exist and GraphData is layout-free', () => {
  assert.ok(catalog.graphs.length >= 2, 'GraphDef差替え確認用に2件以上のサンプルが必要');
  for (const row of catalog.graphs) {
    for (const key of ['graph_def_file', 'graph_data_file', 'layout_state_file']) {
      assert.ok(fs.existsSync(path.join(root, row[key])), `${row[key]} must exist`);
    }
    const graphDef = readJson(row.graph_def_file);
    const graphData = readJson(row.graph_data_file);
    const layout = readJson(row.layout_state_file);
    assert.equal(graphData.graph_id, row.graph_id);
    assert.equal(layout.graph_id, row.graph_id);
    assert.ok(Array.isArray(graphDef.node_types) && graphDef.node_types.length > 0);
    assert.ok(Array.isArray(graphDef.edge_types) && graphDef.edge_types.length > 0);
    assert.ok(graphData.nodes.every(node => !Object.hasOwn(node, 'x') && !Object.hasOwn(node, 'y')), 'GraphData nodes must not contain layout coordinates');
    assert.deepEqual(new Set(Object.keys(layout.positions)), new Set(graphData.nodes.map(node => node.id)));
  }
});

test('plugin is external-library free and provides required v0.1 interactions', () => {
  assert.equal(pluginManifest.external_library, false);
  assert.ok(!/<script[^>]+src=/i.test(pluginSource));
  assert.ok(!/(unpkg|jsdelivr|cdnjs|d3\.js|cytoscape|vis-network)/i.test(pluginSource));
  for (const token of [
    "registerAction(ACTION_ID",
    "addEventListener('wheel'",
    "startNodeDrag",
    "fitGraph",
    "saveLayout",
    "data-role=\"search\"",
    "GraphDef / GraphData / LayoutState"
  ]) {
    assert.ok(pluginSource.includes(token), `plugin source should include ${token}`);
  }
});
