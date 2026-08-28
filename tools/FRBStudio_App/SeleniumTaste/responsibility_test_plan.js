'use strict';

// Responsibility Definition Driven Test -> Selenium execution plan bridge.
// Canonical Responsibility JSON remains the source of truth; this module derives
// the same Generated TestPattern / Expected data used by the Studio preview.

const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const APP_ROOT = path.resolve(__dirname, '..');
const DEFAULT_RESPONSIBILITY_DOCUMENT = 'data/json/03_tests/responsibilities/responsibility_data_v0_2.json';
const DEFAULT_REGISTRY = 'data/json/config/validation_type_registry_v0_1.json';

function readJson(relativePath) {
  const absolute = path.resolve(APP_ROOT, relativePath);
  return JSON.parse(fs.readFileSync(absolute, 'utf8'));
}

function readText(relativePath) {
  return fs.readFileSync(path.resolve(APP_ROOT, relativePath), 'utf8');
}

function loadPreviewSandbox() {
  const sandbox = {
    console,
    structuredClone,
    Date,
    JSON,
    Object,
    Array,
    Map,
    Set,
    Number,
    String,
    Boolean,
    Math,
    RegExp,
  };
  sandbox.globalThis = sandbox;
  vm.createContext(sandbox);
  [
    'wwwroot/js/services/definition/definition_verification_common.js',
    'wwwroot/js/services/definition/field_contract_resolver.js',
    'wwwroot/js/services/definition/definition_value_validator.js',
    'wwwroot/js/services/responsibility/responsibility_test_preview_service.js',
  ].forEach((relativePath) => {
    vm.runInContext(readText(relativePath), sandbox, { filename: relativePath });
  });
  return sandbox;
}

function clone(value) {
  return value === undefined ? undefined : JSON.parse(JSON.stringify(value));
}

function parseActualPath(actualPath) {
  const text = String(actualPath ?? '').trim();
  if (!text.startsWith('$')) throw new Error(`JSON path must start with $: ${text}`);
  const parts = [];
  const pattern = /\.([A-Za-z0-9_\-]+)|\[(\d+)\]/g;
  let match;
  while ((match = pattern.exec(text)) !== null) {
    if (match[1] !== undefined) parts.push(match[1]);
    else parts.push(Number(match[2]));
  }
  return parts;
}

function setByActualPath(root, actualPath, value) {
  const parts = parseActualPath(actualPath);
  if (!parts.length) throw new Error(`Root replacement is not supported: ${actualPath}`);
  let current = root;
  for (let i = 0; i < parts.length - 1; i += 1) {
    current = current[parts[i]];
    if (current === null || current === undefined) {
      throw new Error(`Path does not exist: ${actualPath}`);
    }
  }
  current[parts.at(-1)] = clone(value);
}

function getByActualPath(root, actualPath) {
  let current = root;
  for (const part of parseActualPath(actualPath)) {
    if (current === null || current === undefined) return undefined;
    current = current[part];
  }
  return current;
}

function normalizeRelativePath(value) {
  return String(value ?? '').replace(/\\/g, '/').replace(/^\/+/, '');
}

function relatedGridDefinitions(viewDef) {
  const result = [];
  for (const view of (viewDef?.views ?? [])) {
    const defs = view?.toolbar?.relatedGridViews ?? view?.toolbar?.related_grid_views ?? [];
    defs.forEach((item) => result.push(item));
  }
  return result;
}

function resolveUiTarget(viewDef, dataPath) {
  const target = String(dataPath ?? '').trim();
  const firstView = viewDef?.views?.[0] ?? null;
  const primaryGrid = (firstView?.sections ?? []).find((section) => section?.type === 'grid');
  if (primaryGrid && String(primaryGrid.dataPath ?? '').trim() === target) {
    return {
      mode: 'MAIN_GRID',
      view_id: String(firstView?.id ?? ''),
      section_id: String(primaryGrid?.id ?? ''),
      related_grid_id: '',
    };
  }

  const related = relatedGridDefinitions(viewDef).find((item) => String(item?.dataPath ?? '').trim() === target);
  if (related) {
    return {
      mode: 'RELATED_GRID',
      view_id: String(related?.viewId ?? ''),
      section_id: String(related?.id ?? ''),
      related_grid_id: String(related?.id ?? ''),
    };
  }

  for (const view of (viewDef?.views ?? [])) {
    const section = (view?.sections ?? []).find((candidate) => candidate?.type === 'grid' && String(candidate?.dataPath ?? '').trim() === target);
    if (section) {
      return {
        mode: 'SECONDARY_GRID',
        view_id: String(view?.id ?? ''),
        section_id: String(section?.id ?? ''),
        related_grid_id: '',
      };
    }
  }

  throw new Error(`UI target could not be resolved for ${target}`);
}

function diffJson(expected, actual, basePath='$', out=[]) {
  if (Object.is(expected, actual)) return out;

  const expectedArray = Array.isArray(expected);
  const actualArray = Array.isArray(actual);
  const expectedObject = expected && typeof expected === 'object' && !expectedArray;
  const actualObject = actual && typeof actual === 'object' && !actualArray;

  if (expectedArray && actualArray) {
    const length = Math.max(expected.length, actual.length);
    for (let i = 0; i < length; i += 1) {
      diffJson(expected[i], actual[i], `${basePath}[${i}]`, out);
    }
    return out;
  }

  if (expectedObject && actualObject) {
    const keys = new Set([...Object.keys(expected), ...Object.keys(actual)]);
    for (const key of keys) {
      diffJson(expected[key], actual[key], `${basePath}.${key}`, out);
    }
    return out;
  }

  out.push({ path: basePath, expected: clone(expected), actual: clone(actual) });
  return out;
}

function buildResponsibilityExecutionPlan({
  responsibilityCd='data_update_persist',
  responsibilityDocumentPath=DEFAULT_RESPONSIBILITY_DOCUMENT,
  registryPath=DEFAULT_REGISTRY,
}={}) {
  const responsibilityDocument = readJson(responsibilityDocumentPath);
  const responsibility = (responsibilityDocument?.responsibilities ?? [])
    .find((item) => item?.responsibility_cd === responsibilityCd);
  if (!responsibility) throw new Error(`Responsibility not found: ${responsibilityCd}`);

  const setup = (responsibility?.test_setup ?? []).find((item) => item?.setup_id) ?? null;
  if (!setup) throw new Error(`${responsibilityCd}: test_setup is required.`);

  const inputFile = normalizeRelativePath(setup.input_file);
  const viewDefFile = normalizeRelativePath(setup.view_def_file);
  const fieldDefinitionFile = normalizeRelativePath(setup.field_definition_file);
  const registryFile = normalizeRelativePath(registryPath);

  const inputData = readJson(inputFile);
  const viewDef = readJson(viewDefFile);
  const fieldDefinitionDocument = readJson(fieldDefinitionFile);
  const registry = readJson(registryFile);
  const sandbox = loadPreviewSandbox();
  const service = new sandbox.ResponsibilityTestPreviewService({ registry });
  const preview = JSON.parse(JSON.stringify(service.derive({
    responsibility,
    rootDocument: responsibilityDocument,
    inputData,
    viewDef,
    fieldDefinitionDocument,
    registry,
  })));

  const expectedDocument = clone(inputData);
  const allMutations = [];
  const seenPaths = new Map();
  const patterns = (preview.test_patterns ?? []).map((pattern) => {
    const uiTarget = resolveUiTarget(viewDef, pattern.target_data_path);
    const mutations = (pattern.mutations ?? []).map((mutation) => {
      const prior = seenPaths.get(mutation.actual_path);
      if (prior && !Object.is(prior.after, mutation.after)) {
        throw new Error(`Generated TestPattern conflict: ${mutation.actual_path}`);
      }
      if (!prior) {
        seenPaths.set(mutation.actual_path, mutation);
        setByActualPath(expectedDocument, mutation.actual_path, mutation.after);
        allMutations.push(clone(mutation));
      }
      return clone(mutation);
    });
    return {
      ...clone(pattern),
      ui_target: uiTarget,
      mutations,
    };
  });

  const expectedDiff = allMutations.map((mutation) => [
    `(-) ${mutation.actual_path} = ${JSON.stringify(mutation.before)}`,
    `(+) ${mutation.actual_path} = ${JSON.stringify(mutation.after)}`,
  ].join('\n')).join('\n');

  return {
    schema_version: 'responsibility_selenium_execution_plan_v0_1',
    responsibility_document: responsibilityDocumentPath,
    responsibility_cd: responsibilityCd,
    responsibility_name: String(responsibility?.name ?? ''),
    guarantee_ids: (responsibility?.guarantees ?? []).map((item) => item?.guarantee_id).filter(Boolean),
    expected_def_type: preview.expected_def_type,
    setup: {
      setup_id: String(setup.setup_id ?? ''),
      input_file: inputFile,
      input_approval_status: String(setup.input_approval_status ?? '').toLowerCase(),
      view_def_file: viewDefFile,
      field_definition_file: fieldDefinitionFile,
      registry_file: registryFile,
      execution_scope: String(setup.execution_scope ?? ''),
      load_policy: String(setup.load_policy ?? ''),
      save_policy: String(setup.save_policy ?? ''),
      reload_policy: String(setup.reload_policy ?? ''),
      working_copy_policy: String(setup.working_copy_policy ?? 'COPY_BEFORE_EXECUTION'),
      working_copy_directory: normalizeRelativePath(setup.working_copy_directory ?? 'data/json/99_test_runtime'),
      cleanup_policy: String(setup.cleanup_policy ?? 'DELETE_AFTER_EXECUTION'),
      runner_type: String(setup.runner_type ?? 'SELENIUM_NATIVE_SHELL'),
    },
    execution_ready: preview.execution_ready === true,
    preview_status: preview.status,
    patterns,
    mutations: allMutations,
    expected: {
      diff: expectedDiff,
      unexpected_diff_count: 0,
      document: expectedDocument,
    },
    baseline_document: clone(inputData),
    summary: {
      test_pattern_count: patterns.length,
      mutation_count: allMutations.length,
      invalid_mutation_count: preview.summary?.invalid_mutation_count ?? 0,
      issue_count: preview.summary?.issue_count ?? 0,
      main_grid_pattern_count: patterns.filter((item) => item.ui_target?.mode === 'MAIN_GRID').length,
      related_grid_pattern_count: patterns.filter((item) => item.ui_target?.mode === 'RELATED_GRID').length,
    },
    issues: clone(preview.issues ?? []),
  };
}

function assertExecutionApproved(plan) {
  if (!plan?.execution_ready) {
    const status = plan?.setup?.input_approval_status ?? 'unknown';
    throw new Error(`Responsibility execution is blocked: Test Input approval_status=${status}. Generated Previewで内容確認後、approvedへ変更してください。`);
  }
  if (plan.setup?.execution_scope !== 'DOCUMENT') throw new Error(`Unsupported execution_scope: ${plan.setup?.execution_scope}`);
  if (plan.setup?.load_policy !== 'LOAD_ONCE') throw new Error(`Unsupported load_policy: ${plan.setup?.load_policy}`);
  if (plan.setup?.save_policy !== 'SAVE_ONCE') throw new Error(`Unsupported save_policy: ${plan.setup?.save_policy}`);
  if (plan.setup?.reload_policy !== 'RELOAD_ONCE') throw new Error(`Unsupported reload_policy: ${plan.setup?.reload_policy}`);
  if (plan.setup?.working_copy_policy !== 'COPY_BEFORE_EXECUTION') throw new Error(`Unsupported working_copy_policy: ${plan.setup?.working_copy_policy}`);
}

function formatPlanSummary(plan) {
  const summary = plan?.summary ?? {};
  return [
    `Responsibility: ${plan?.responsibility_cd} / ${plan?.responsibility_name}`,
    `ExpectedDef: ${plan?.expected_def_type}`,
    `Input: ${plan?.setup?.input_file} (${plan?.setup?.input_approval_status})`,
    `Lifecycle: ${plan?.setup?.load_policy} -> ${plan?.setup?.save_policy} -> ${plan?.setup?.reload_policy}`,
    `Generated: Pattern=${summary.test_pattern_count ?? 0} / Mutation=${summary.mutation_count ?? 0} / Invalid=${summary.invalid_mutation_count ?? 0}`,
    `UI Target: Main=${summary.main_grid_pattern_count ?? 0} / Related=${summary.related_grid_pattern_count ?? 0}`,
    `Execution Ready: ${plan?.execution_ready ? 'YES' : 'NO'}`,
  ].join('\n');
}

if (require.main === module) {
  const responsibilityCd = process.argv[2] || 'data_update_persist';
  const plan = buildResponsibilityExecutionPlan({ responsibilityCd });
  console.log(formatPlanSummary(plan));
  if (process.argv.includes('--json')) console.log(JSON.stringify(plan, null, 2));
}

module.exports = {
  APP_ROOT,
  DEFAULT_RESPONSIBILITY_DOCUMENT,
  buildResponsibilityExecutionPlan,
  assertExecutionApproved,
  diffJson,
  formatPlanSummary,
  getByActualPath,
  setByActualPath,
};
