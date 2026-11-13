// v0.18.26-thought-evolution-studio-v0-4-evolution-engine
// Run from FRBStudio_App root:
//   node --test tests/qa/static/thought_evolution_studio_evolution_engine_static.test.mjs

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
const profile = readJson('data/json/01_main/thought_difference/thought_evolution_engine_profile_data_v0_1.json');

const requiredStates = new Set(['OBSERVATION','CANDIDATE','PROVISIONAL','APPROVED','VALIDATED','SUPERSEDED']);
const requiredTypes = new Set(['decision_axis_add','constraint_add','applicability_change','relation_change','thought_class_split','baseline_terrain_candidate']);

test('catalog wires Evolution Engine data for every graph', () => {
  assert.equal(catalog.schema_version, 'thought_evolution_graph_catalog_v0_4');
  for (const row of catalog.graphs) {
    assert.equal(row.evolution_enabled, true);
    for (const key of ['evolution_profile_file','evolution_observation_data_file','evolution_proposal_data_file','evolution_version_data_file']) {
      assert.ok(row[key], `${row.graph_id} missing ${key}`);
      assert.ok(fs.existsSync(path.join(root, row[key])), `${row[key]} must exist`);
    }
  }
});

test('Evolution Profile forbids automatic promotion and source mutation', () => {
  assert.equal(profile.promotion_policy.automatic_promotion, false);
  assert.equal(profile.promotion_policy.source_definition_mutation, false);
  assert.ok(profile.promotion_policy.minimum_observations >= 2);
  assert.deepEqual(new Set(profile.proposal_states.map(x => x.id)), requiredStates);
  assert.deepEqual(new Set(profile.proposal_types.map(x => x.id)), requiredTypes);
});

test('Observation and Proposal samples preserve scope, outcome, counterexamples and provenance', () => {
  for (const row of catalog.graphs) {
    const observations = readJson(row.evolution_observation_data_file);
    const proposals = readJson(row.evolution_proposal_data_file);
    const versions = readJson(row.evolution_version_data_file);
    assert.ok(observations.observations.length >= 2);
    assert.ok(observations.observations.every(x => x.reason && x.applicability_scope && Array.isArray(x.candidate_keys)));
    assert.ok(proposals.proposals.length >= 2);
    assert.ok(proposals.proposals.every(x => requiredStates.has(x.state)));
    assert.ok(proposals.proposals.every(x => requiredTypes.has(x.proposal_type)));
    assert.ok(proposals.proposals.every(x => x.supporting_count >= 2 && x.applicability_scope));
    const generated = proposals.proposals.filter(x => x.next_version?.status === 'GENERATED');
    const notGenerated = proposals.proposals.filter(x => x.next_version?.status === 'NOT_GENERATED');
    assert.equal(generated.length + notGenerated.length, proposals.proposals.length);
    assert.ok(generated.every(x => x.state === 'APPROVED'));
    assert.equal(versions.mutation_policy.includes('元定義を上書きしない'), true);
    const snapshotIds = new Set((versions.snapshots ?? []).map(x => x.version_snapshot_id));
    assert.ok(generated.every(x => snapshotIds.has(x.next_version.version_snapshot_id)));
    assert.equal(versions.snapshots.length, generated.length);
  }
});

test('plugin exposes human approval and next-version snapshot workflow', () => {
  assert.equal(pluginManifest.version, '0.4.0');
  for (const permission of ['read_evolution_profile','read_evolution_observations','write_evolution_proposals','write_version_snapshots','generate_next_version_snapshot']) assert.ok(pluginManifest.permissions.includes(permission));
  for (const token of [
    'evolutionEvidenceRecords',
    'generateEvolutionProposals',
    'applyEvolutionDecision',
    'generateNextVersionSnapshot',
    'SOURCE_DEFINITION_NOT_MUTATED',
    'data-tab="evolution"',
    '候補生成・再評価',
    '次版Snapshot生成',
    'ThoughtEvolutionStudioV04'
  ]) assert.ok(pluginSource.includes(token), `missing Evolution token: ${token}`);
  assert.ok(!/(unpkg|jsdelivr|cdnjs|d3\.js|cytoscape|vis-network)/i.test(pluginSource));
});
