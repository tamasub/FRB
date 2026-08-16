import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import test from 'node:test';
import vm from 'node:vm';

const root = process.cwd();
const readText = (relativePath) => fs.readFileSync(path.join(root, relativePath), 'utf8');
const readJson = (relativePath) => JSON.parse(readText(relativePath));
const navigationPath = 'wwwroot/js/ui/section_group_navigation.js';
const incidentPath = 'data/json/01_main/_studio_work_incident_data_v2.json';

function navigationSandbox() {
  const sandbox = { console };
  vm.createContext(sandbox);
  vm.runInContext(readText(navigationPath), sandbox, { filename: navigationPath });
  return sandbox;
}

test('Phase 2 resolves only the Sections pinched by the active sectionGroup without mutating Section definitions', () => {
  const sandbox = navigationSandbox();
  const sample = {
    sections: [
      { id: 'launch_shortcuts', type: 'grid', marker: 'grid-original' },
      { id: 'markdown_settings', type: 'form', marker: 'form-original' },
      { id: 'internal_hidden', type: 'form', marker: 'hidden-original' }
    ],
    sectionGroups: [
      { id: 'launch', caption: 'Shortcut', sectionIds: ['launch_shortcuts'] },
      { id: 'markdown', caption: 'Markdown', sectionIds: ['markdown_settings'] }
    ]
  };
  sandbox.sample = sample;

  const launch = vm.runInContext(`sectionGroupContractForView(sample, 'launch')`, sandbox);
  const markdown = vm.runInContext(`sectionGroupContractForView(sample, 'markdown')`, sandbox);

  assert.equal(launch.enabled, true);
  assert.equal(launch.activeGroup.id, 'launch');
  assert.deepEqual(Array.from(launch.sections, section => section.id), ['launch_shortcuts']);
  assert.deepEqual(Array.from(markdown.sections, section => section.id), ['markdown_settings']);
  assert.equal(launch.sections[0], sample.sections[0], 'Section object must be reused, not copied');
  assert.equal(markdown.sections.some(section => section.id === 'internal_hidden'), false, 'ungrouped Section stays outside the active projection');
});

test('Phase 2 keeps the legacy editor section set unchanged when sectionGroups is absent', () => {
  const sandbox = navigationSandbox();
  const sample = {
    sections: [
      { id: 'header', type: 'form' },
      { id: 'main', type: 'grid' }
    ]
  };
  sandbox.sample = sample;
  const contract = vm.runInContext(`sectionGroupContractForView(sample, '')`, sandbox);
  assert.equal(contract.enabled, false);
  assert.deepEqual(Array.from(contract.sections, section => section.id), ['header', 'main']);
});

test('Phase 2 runtime defensively rejects broken sectionGroups references while allowing shared Sections', () => {
  const sandbox = navigationSandbox();
  sandbox.valid = {
    sections: [{ id: 'shared' }, { id: 'a' }, { id: 'b' }],
    sectionGroups: [
      { id: 'one', caption: 'One', sectionIds: ['shared', 'a'] },
      { id: 'two', caption: 'Two', sectionIds: ['shared', 'b'] }
    ]
  };
  assert.doesNotThrow(() => vm.runInContext(`sectionGroupContractForView(valid, 'two')`, sandbox));

  sandbox.invalid = {
    sections: [{ id: 'a' }],
    sectionGroups: [{ id: 'broken', caption: 'Broken', sectionIds: ['missing'] }]
  };
  assert.throws(
    () => vm.runInContext(`sectionGroupContractForView(invalid, 'broken')`, sandbox),
    /存在しないSection/
  );
});

test('standard Editor delegates header/grid selection to activeSectionsForView and load runtime renders the active Group', () => {
  const fields = readText('wwwroot/js/renderers/field_controls.js');
  const runtime = readText('wwwroot/js/runtime/load_runtime.js');

  assert.match(fields, /function editorSections\(\)/);
  assert.match(fields, /activeSectionsForView\(view\)/);
  assert.match(fields, /headerDef\(\).*editorSections\(\)/);
  assert.match(fields, /gridDef\(\).*editorSections\(\)/);

  assert.match(runtime, /initializeSectionGroupNavigation\(defObj\)/);
  assert.match(runtime, /renderActiveSectionGroup\(\{ resetSelection: false \}\)/);
  assert.match(runtime, /const activeGrid = gridDef\(\)/);
  assert.match(runtime, /!activeGrid \|\| mainGridIsVirtual/);
});

test('JSON Object Studio provides generic Group Navigation UI and loads it before load_runtime', () => {
  const index = readText('wwwroot/index.html');
  const css = readText('wwwroot/css/frb-studio-shell.css');
  const navigation = readText(navigationPath);

  assert.match(index, /id="sectionGroupNavigation"/);
  const navScript = index.indexOf('js/ui/section_group_navigation.js');
  const runtimeScript = index.indexOf('js/runtime/load_runtime.js');
  assert.ok(navScript >= 0 && runtimeScript >= 0 && navScript < runtimeScript, 'navigation runtime must load before load_runtime');

  assert.match(css, /\.json-studio-main-pane\.has-section-groups/);
  assert.match(css, /min-height:calc\(100dvh - var\(--frb-fixed-header-height, 122px\)\)/);
  assert.match(css, /> \.section-group-navigation \{[\s\S]*align-self:stretch;[\s\S]*height:100%/);
  assert.match(css, /\.section-group-navigation-item\.active/);
  assert.match(navigation, /sectionGroupNavigation/);
  assert.match(navigation, /role', 'tab'/);
  assert.match(navigation, /aria-selected/);

  assert.doesNotMatch(navigation, /app_settings|launch_shortcuts|markdown_settings/i, 'Group Navigation must stay Settings-independent');
});

test('studio_work_0195 remains the Phase 2 owner for generic Group Navigation', () => {
  const incident = readJson(incidentPath);
  const item = incident.work_items.find(candidate => candidate.work_item_id === 'studio_work_0195');
  assert.ok(item);
  assert.equal(item.phase, 'v0.18.73-section-group-navigation-phase2');
  assert.match(item.objective, /sectionGroups/);
  assert.match(item.objective, /既存Editor \/ Renderer/);
  assert.match(item.scope, /Settings非依存/);
  assert.equal(item.status, '完了');
  assert.match(item.actual_updated_files, /section_group_navigation\.js/);
  assert.match(item.verification_log, /Phase 2専用Static: 6 \/ 6 PASS/);
});
