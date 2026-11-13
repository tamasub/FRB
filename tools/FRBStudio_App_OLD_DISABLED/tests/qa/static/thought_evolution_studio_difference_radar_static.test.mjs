// v0.18.25-thought-evolution-studio-v0-3-difference-radar
// Run from FRBStudio_App root:
//   node --test tests/qa/static/thought_evolution_studio_difference_radar_static.test.mjs

import fs from 'node:fs';
import path from 'node:path';
import test from 'node:test';
import assert from 'node:assert/strict';

const root = process.cwd();
const overlayRoot = path.join(root, 'studio_overlays/thought_evolution');
const readJson = rel => JSON.parse(fs.readFileSync(path.join(root, rel), 'utf8'));
const readOverlayJson = rel => JSON.parse(fs.readFileSync(path.join(overlayRoot, rel), 'utf8'));

const catalog = readOverlayJson('data/thought_evolution_graph_catalog_v0_1.json');
const pluginManifest = readOverlayJson('plugins/graph_studio/plugin.json');
const pluginSource = fs.readFileSync(path.join(overlayRoot, 'plugins/graph_studio/plugin.js'), 'utf8');
const profile = readJson('data/json/01_main/thought_difference/thought_difference_analysis_profile_data_v0_1.json');
const qualityResults = readJson('data/json/01_main/thought_difference/thought_difference_result_quality_asset_data_v0_1.json');
const thoughtResults = readJson('data/json/01_main/thought_difference/thought_difference_result_thought_evolution_data_v0_1.json');
const profileView = readJson('defs/analysis/thought_difference_analysis_profile_view_def_v0_1.json');
const resultView = readJson('defs/analysis/thought_difference_result_view_def_v0_1.json');

test('catalog wires AnalysisProfile and DifferenceResult Data for each graph', () => {
  assert.equal(catalog.schema_version, 'thought_evolution_graph_catalog_v0_4');
  for (const row of catalog.graphs) {
    assert.equal(row.analysis_profile_file, 'data/json/01_main/thought_difference/thought_difference_analysis_profile_data_v0_1.json');
    assert.ok(row.difference_result_data_file, `${row.graph_id} must declare difference_result_data_file`);
    assert.ok(fs.existsSync(path.join(root, row.analysis_profile_file)));
    assert.ok(fs.existsSync(path.join(root, row.difference_result_data_file)));
  }
});

test('AnalysisProfile declares required data-driven radar categories and checks', () => {
  const categories = new Set(profile.categories.map(item => item.id));
  for (const id of ['COMMON', 'ASYMMETRY', 'MISSING_LINK', 'CONTRADICTION', 'TRANSFER_CANDIDATE', 'CONCEPT_DRIFT', 'UNEXPLAINED_JUMP']) {
    assert.ok(categories.has(id), `missing category: ${id}`);
  }
  assert.equal(profile.categories.find(item => item.id === 'COMMON').default_visible, false);
  assert.ok(profile.checks.every(item => item.enabled && categories.has(item.result_category)));
  assert.equal(profile.view_def, 'analysis/thought_difference_analysis_profile_view_def_v0_1.json');
  assert.equal(profileView.views[0].sections.find(section => section.id === 'mainGrid').dataPath, 'checks');
});

test('DifferenceResult samples include asymmetry, missing link, concept drift and Relation Proposal', () => {
  const all = [...qualityResults.results, ...thoughtResults.results];
  const categories = new Set(all.map(item => item.category));
  for (const id of ['ASYMMETRY', 'MISSING_LINK', 'TRANSFER_CANDIDATE', 'CONCEPT_DRIFT', 'UNEXPLAINED_JUMP']) {
    assert.ok(categories.has(id), `sample must include ${id}`);
  }
  assert.ok(all.every(item => item.status === 'AI_PROPOSED'));
  assert.ok(all.every(item => Array.isArray(item.node_ids) && item.node_ids.length > 0));
  assert.ok(all.some(item => item.relation_proposal?.source_node_id && item.relation_proposal?.target_node_id));
  assert.equal(resultView.views[0].sections.find(section => section.id === 'mainGrid').dataPath, 'results');
});

test('plugin renders radar filters and transfers proposals through Relation Approval', () => {
  assert.equal(pluginManifest.version, '0.4.0');
  for (const permission of ['read_analysis_profile', 'read_difference_results', 'write_difference_results']) {
    assert.ok(pluginManifest.permissions.includes(permission));
  }
  for (const token of [
    'buildDifferenceFilter',
    'differenceCategoryDefinitions',
    'data-difference-category',
    'radarResultsForNode',
    'Relation Approvalへ送る',
    'transferProposalToRelationApproval',
    'saveDifferenceResults',
    'ThoughtEvolutionStudioV03'
  ]) assert.ok(pluginSource.includes(token), `missing radar token: ${token}`);
});

test('Thought Evolution Studio launches in a dedicated new window', () => {
  for (const token of [
    'openDedicatedStudioWindow',
    "url.searchParams.set('action', ACTION_ID)",
    "url.searchParams.set('tesWindow', '1')",
    "window.open(url, '_blank')",
    'isDedicatedWindowLaunch',
    'Thought Evolution Studioを新規ウィンドウで開きました'
  ]) assert.ok(pluginSource.includes(token), `missing dedicated-window token: ${token}`);
});
