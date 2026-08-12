import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import test from 'node:test';
import vm from 'node:vm';

const root = process.cwd();

function readText(relativePath) {
  return fs.readFileSync(path.join(root, relativePath), 'utf8');
}

function readJson(relativePath) {
  return JSON.parse(readText(relativePath));
}

function createFakeDocument() {
  let document;
  const createElement = (tagName='div') => {
    const node = {
      tagName: String(tagName).toUpperCase(),
      dataset: {},
      className: '',
      textContent: '',
      children: [],
      parentNode: null,
      ownerDocument: null,
      isConnected: true,
      style: {},
      get firstChild() { return this.children[0] ?? null; },
      appendChild(child) {
        child.parentNode = this;
        child.ownerDocument = this.ownerDocument;
        this.children.push(child);
        return child;
      },
      removeChild(child) {
        this.children = this.children.filter(x => x !== child);
        child.parentNode = null;
        return child;
      },
      replaceChildren(...children) {
        this.children.forEach(child => { child.parentNode = null; });
        this.children = [];
        children.forEach(child => this.appendChild(child));
      },
      remove() {
        this.parentNode?.removeChild?.(this);
        this.isConnected = false;
      },
      classList: { remove() {} }
    };
    node.ownerDocument = document;
    return node;
  };
  document = { createElement };
  return document;
}

function loadDefinitionPreviewRuntime(extra={}) {
  const document = createFakeDocument();
  const sandbox = {
    console,
    document,
    globalThis: null,
    normalizeArray(value) {
      if (Array.isArray(value)) return value;
      if (value == null || value === '') return [];
      return [value];
    },
    ...extra
  };
  sandbox.globalThis = sandbox;
  vm.createContext(sandbox);

  [
    'wwwroot/js/core/registry.js',
    'wwwroot/js/components/studio_component.js',
    'wwwroot/js/components/editor_component.js',
    'wwwroot/js/components/subgrid_component.js',
    'wwwroot/js/components/derived_subgrid_component.js',
    'wwwroot/js/components/editor_component_registry.js',
    'wwwroot/js/services/definition/definition_verification_common.js',
    'wwwroot/js/services/definition/field_contract_resolver.js',
    'wwwroot/js/services/definition/test_pattern_deriver.js',
    'wwwroot/js/services/definition/expected_resolver.js',
    'wwwroot/js/services/definition/definition_verification_service.js',
    'wwwroot/js/components/definition/definition_verification_derived_subgrid_component.js',
    'wwwroot/js/components/definition/definition_constraint_diff_component.js',
    'wwwroot/js/components/definition/definition_test_preview_component.js'
  ].forEach(relative => vm.runInContext(readText(relative), sandbox, { filename: relative }));

  return { sandbox, document };
}

function findFieldDefinitionSection(viewDef) {
  return viewDef.views
    .flatMap(view => view.sections ?? [])
    .find(section => section.id === 'field_definitions');
}

test('Field Definition ViewDef connects Constraint Diff and Test Preview as readonly Derived Components', () => {
  const viewDef = readJson('defs/fielddefs/frb_fft_measurement_field_definitions_view_def_v0_1.json');
  const section = findFieldDefinitionSection(viewDef);
  assert.ok(section);

  assert.deepEqual(
    section.editorComponents.map(component => component.type),
    ['definition_target_caption', 'definition_constraint_diff', 'definition_test_preview']
  );

  const targetCaption = section.editorComponents.find(component => component.type === 'definition_target_caption');
  assert.equal(targetCaption.placement, 'detailBody');
  assert.equal(targetCaption.readonly, true);
  assert.equal(targetCaption.config.targetViewDefPath, 'frb/frb_fft_field_definition_sample_view_def_v0_1.json');

  section.editorComponents
    .filter(component => ['definition_constraint_diff', 'definition_test_preview'].includes(component.type))
    .forEach(component => {
      assert.equal(component.placement, 'afterChildGrids');
      assert.equal(component.readonly, true);
      assert.equal(component.config.registryDataPath, 'config/validation_type_registry_v0_1.json');
    });
});

test('Definition preview Components use the DerivedSubGrid hierarchy and are registered by type', () => {
  const { sandbox } = loadDefinitionPreviewRuntime();

  assert.equal(vm.runInContext('DefinitionVerificationDerivedSubGridComponent.prototype instanceof DerivedSubGridComponent', sandbox), true);
  assert.equal(vm.runInContext('DefinitionConstraintDiffComponent.prototype instanceof DefinitionVerificationDerivedSubGridComponent', sandbox), true);
  assert.equal(vm.runInContext('DefinitionTestPreviewComponent.prototype instanceof DefinitionVerificationDerivedSubGridComponent', sandbox), true);
  assert.equal(vm.runInContext('EditorComponentRegistry.has("definition_constraint_diff")', sandbox), true);
  assert.equal(vm.runInContext('EditorComponentRegistry.has("definition_test_preview")', sandbox), true);
});

test('Constraint Diff shows Standard / Override / Resolved and marks override rows without mutating Field Definition', async () => {
  const { sandbox, document } = loadDefinitionPreviewRuntime();
  const registry = readJson('data/json/config/validation_type_registry_v0_1.json');
  const field = {
    field_path: '$.sample_rate_hz',
    validation_type: 'studio.integer.positive',
    constraint_overrides: {
      required: true,
      nullable: false,
      maximum: { value: 200000, inclusive: true }
    }
  };
  const original = structuredClone(field);
  sandbox.__registry = registry;
  sandbox.__field = field;
  sandbox.__host = document.createElement('div');

  await vm.runInContext(`
    globalThis.__service = new DefinitionVerificationService({ registry: __registry });
    globalThis.__constraintComponent = new DefinitionConstraintDiffComponent(
      { caption: 'Constraint Diff' },
      { definitionVerificationService: __service }
    );
    __constraintComponent.mount(__host, { row: __field });
    __constraintComponent.refreshVerification();
  `, sandbox);

  const rows = vm.runInContext('__constraintComponent.buildVerificationRows(__constraintComponent.verificationResult)', sandbox);
  const byName = Object.fromEntries(Array.from(rows, row => [row.constraint, { ...row }]));

  assert.equal(byName.minimum.standard, '{"value":1,"inclusive":true}');
  assert.equal(byName.minimum.override, '—');
  assert.equal(byName.minimum.resolved, '{"value":1,"inclusive":true}');
  assert.equal(byName.minimum.status, 'STANDARD');

  assert.equal(byName.maximum.standard, '{"value":9007199254740991,"inclusive":true}');
  assert.equal(byName.maximum.override, '{"value":200000,"inclusive":true}');
  assert.equal(byName.maximum.resolved, '{"value":200000,"inclusive":true}');
  assert.equal(byName.maximum.status, 'OVERRIDE');
  assert.match(vm.runInContext('__constraintComponent.getRowClassName(__constraintComponent.buildVerificationRows(__constraintComponent.verificationResult).find(x => x.constraint === "maximum"))', sandbox), /is-override/);

  assert.deepEqual(field, original);
  assert.throws(() => vm.runInContext('__constraintComponent.commit()', sandbox), /readonly/);
});

test('Test Preview is a direct readonly projection of DefinitionVerificationService Preview result', async () => {
  const { sandbox, document } = loadDefinitionPreviewRuntime();
  const registry = readJson('data/json/config/validation_type_registry_v0_1.json');
  const sample = readJson('fielddefs/samples/frb_fft_measurement_field_definitions_v0_2.json');
  const field = sample.field_definitions.find(item => item.field_path === '$.measurement_sessions[].sample_rate_hz');
  sandbox.__registry = registry;
  sandbox.__field = field;
  sandbox.__host = document.createElement('div');

  await vm.runInContext(`
    globalThis.__service = new DefinitionVerificationService({ registry: __registry });
    globalThis.__expectedPreview = __service.deriveForPreview(__field);
    globalThis.__testComponent = new DefinitionTestPreviewComponent(
      { caption: 'Test Preview' },
      { definitionVerificationService: __service }
    );
    __testComponent.mount(__host, { row: __field });
    __testComponent.refreshVerification();
  `, sandbox);

  const result = vm.runInContext('__testComponent.verificationResult', sandbox);
  const componentRows = vm.runInContext('__testComponent.buildVerificationRows(__testComponent.verificationResult)', sandbox);
  const servicePatterns = vm.runInContext('__expectedPreview.test_patterns', sandbox);

  assert.equal(result.status, 'READY');
  assert.equal(componentRows.length, servicePatterns.length);
  assert.deepEqual(
    Array.from(componentRows, row => row.pattern),
    Array.from(servicePatterns, pattern => pattern.pattern_key)
  );
  assert.deepEqual(
    Array.from(componentRows, row => row.expected),
    Array.from(servicePatterns, pattern => pattern.expected.outcome)
  );
  assert.ok(Array.from(componentRows).some(row => row.pattern === 'minimum_minus_1' && row.expected === 'REJECT'));
  assert.ok(Array.from(componentRows).some(row => row.pattern === 'maximum_plus_1' && row.expected === 'REJECT'));
});



test('two Definition preview Components share one Registry load when Service is not injected', async () => {
  const registry = readJson('data/json/config/validation_type_registry_v0_1.json');
  let fetchCount = 0;
  const { sandbox, document } = loadDefinitionPreviewRuntime({
    async fetchApiJsonWithUrl(kind, name) {
      fetchCount += 1;
      assert.equal(kind, 'data');
      assert.equal(name, 'config/validation_type_registry_v0_1.json');
      return { json: registry, url: '/api/data/config/validation_type_registry_v0_1.json' };
    }
  });
  sandbox.__field = {
    field_path: '$.quality_score',
    validation_type: 'studio.integer.non_negative',
    constraint_overrides: { required: true, nullable: false, maximum: { value: 100, inclusive: true } }
  };
  sandbox.__hostA = document.createElement('div');
  sandbox.__hostB = document.createElement('div');

  await vm.runInContext(`
    globalThis.__a = new DefinitionConstraintDiffComponent({ config: { registryDataPath: 'config/validation_type_registry_v0_1.json' } });
    globalThis.__b = new DefinitionTestPreviewComponent({ config: { registryDataPath: 'config/validation_type_registry_v0_1.json' } });
    __a.mount(__hostA, { row: __field });
    __b.mount(__hostB, { row: __field });
    Promise.all([__a.refreshVerification(), __b.refreshVerification()]);
  `, sandbox);

  assert.equal(fetchCount, 1);
  assert.equal(vm.runInContext('__a.verificationState', sandbox), 'ready');
  assert.equal(vm.runInContext('__b.verificationState', sandbox), 'ready');
});

test('standard Detail Editor stays capability-neutral and generically rebinds the full Detail after F12 apply', () => {
  const detailRuntime = readText('wwwroot/js/runtime/detail_save.js');

  assert.doesNotMatch(detailRuntime, /definition_constraint_diff|definition_test_preview|DefinitionVerificationService|ExpectedResolver|TestPatternDeriver/);
  assert.match(detailRuntime, /rebindDetailAfterCanonicalCommit\(currentRows\[selectedIndex\]/);
});

test('Derived Preview remains outside canonical Field Definition JSON / Copy-Paste field contract', () => {
  const viewDef = readJson('defs/fielddefs/frb_fft_measurement_field_definitions_view_def_v0_1.json');
  const sample = readJson('fielddefs/samples/frb_fft_measurement_field_definitions_v0_2.json');
  const section = findFieldDefinitionSection(viewDef);
  const fields = section.fields.map(field => field.field);

  assert.ok(section.editorComponents.length === 3);
  assert.equal(fields.some(field => /resolved|expected|test_pattern|constraint_diff/i.test(field)), false);
  sample.field_definitions.forEach(field => {
    assert.equal(Object.hasOwn(field, 'resolved_constraints'), false);
    assert.equal(Object.hasOwn(field, 'test_patterns'), false);
    assert.equal(Object.hasOwn(field, 'expected'), false);
  });
});

test('index loads Definition Verification Service and preview Components before the Detail Editor runtime', () => {
  const index = readText('wwwroot/index.html');
  const service = index.indexOf('js/services/definition/definition_verification_service.js?v=definition-verification-service-01842');
  const base = index.indexOf('js/components/definition/definition_verification_derived_subgrid_component.js?v=definition-review-evidence-01846');
  const constraint = index.indexOf('js/components/definition/definition_constraint_diff_component.js?v=definition-review-evidence-01846');
  const preview = index.indexOf('js/components/definition/definition_test_preview_component.js?v=definition-review-evidence-01846');
  const detail = index.indexOf('js/runtime/detail_save.js?v=detail-fieldset-cross-field-01852');

  assert.ok(service >= 0);
  assert.ok(base > service);
  assert.ok(constraint > base);
  assert.ok(preview > constraint);
  assert.ok(detail > preview);
});

test('Definition preview styling includes explicit override emphasis', () => {
  const styles = readText('wwwroot/styles.css');
  assert.match(styles, /definition-constraint-diff-row\.is-override/);
  assert.match(styles, /definition-constraint-override-cell/);
});
