import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';

const root = process.cwd();

function parseArgs(argv) {
  const values = {
    definitions: 'data/json/03_tests/contracts/definition_driven_search_v0_1/input/search_field_definitions.json',
    searchRegistry: 'data/json/config/search_operator_registry_v0_1.json',
    validationRegistry: 'data/json/config/validation_type_registry_v0_1.json',
    evidenceDir: 'data/json/03_tests/contracts/definition_driven_search_v0_1'
  };
  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];
    if (arg === '--definitions') values.definitions = argv[++i] ?? '';
    else if (arg === '--search-registry') values.searchRegistry = argv[++i] ?? '';
    else if (arg === '--validation-registry') values.validationRegistry = argv[++i] ?? '';
    else if (arg === '--evidence-dir') values.evidenceDir = argv[++i] ?? '';
    else throw new Error(`Unsupported argument: ${arg}`);
  }
  return values;
}

function readText(relativePath) {
  return fs.readFileSync(path.join(root, relativePath), 'utf8');
}

function readJson(relativePath) {
  return JSON.parse(readText(relativePath));
}

function writeJson(relativePath, value) {
  const fullPath = path.join(root, relativePath);
  fs.mkdirSync(path.dirname(fullPath), { recursive: true });
  fs.writeFileSync(fullPath, `${JSON.stringify(value, null, 2)}\n`, 'utf8');
}

function loadRuntime() {
  const sandbox = { console, Date, JSON, RegExp, Number, String, Boolean, Set, Map, Object, globalThis: null };
  sandbox.globalThis = sandbox;
  vm.createContext(sandbox);
  [
    'wwwroot/js/services/search_capability_resolver.js',
    'wwwroot/js/responsibilities/search_filter.js',
    'wwwroot/js/services/search_test_pattern_deriver.js',
    'wwwroot/js/services/search_definition_test_runner.js',
    'wwwroot/js/services/search_definition_test_evidence_builder.js'
  ].forEach(relativePath => vm.runInContext(readText(relativePath), sandbox, { filename: relativePath }));
  return sandbox;
}

function main() {
  const args = parseArgs(process.argv.slice(2));
  const definitions = readJson(args.definitions);
  const searchRegistry = readJson(args.searchRegistry);
  const validationRegistry = readJson(args.validationRegistry);
  const sandbox = loadRuntime();

  sandbox.__definitions = definitions;
  sandbox.__searchRegistry = searchRegistry;
  sandbox.__validationRegistry = validationRegistry;
  sandbox.__definitionPath = args.definitions;

  vm.runInContext(`
    globalThis.__result = new SearchDefinitionTestRunner().runDocument(
      __definitions,
      {
        search_operator_registry: __searchRegistry,
        validation_type_registry: __validationRegistry
      },
      { definition_path: __definitionPath }
    );
  `, sandbox);

  const result = JSON.parse(JSON.stringify(sandbox.__result));
  const base = args.evidenceDir.replace(/[\\/]+$/, '');
  const sourceFiles = {
    definitionFile: args.definitions,
    searchRegistryFile: args.searchRegistry,
    validationRegistryFile: args.validationRegistry,
    expectedFile: `${base}/expected/search_definition_test.expected.json`,
    actualFile: `${base}/actual/search_definition_test.actual.json`,
    diffFile: `${base}/diff/search_definition_test.diff.json`,
    summaryFile: `${base}/summary/search_definition_test.result.json`
  };

  sandbox.__runnerResult = result;
  sandbox.__sourceFiles = sourceFiles;
  vm.runInContext(`
    globalThis.__evidence = new SearchDefinitionTestEvidenceBuilder().buildArtifacts(
      __runnerResult,
      {
        test_id: 'definition_driven_search_v0_1',
        title: 'Definition Driven Search — Text / Number / Date',
        source_files: __sourceFiles
      }
    );
  `, sandbox);

  const evidence = JSON.parse(JSON.stringify(sandbox.__evidence));
  writeJson(sourceFiles.expectedFile, evidence.expected);
  writeJson(sourceFiles.actualFile, evidence.actual);
  writeJson(sourceFiles.diffFile, evidence.diff);
  writeJson(sourceFiles.summaryFile, evidence.summary);

  console.log(
    `[FRBStudio] Search Definition Test: ${result.status}` +
    ` / fields=${result.summary.field_count}` +
    ` patterns=${result.summary.pattern_count}` +
    ` pass=${result.summary.passed_count}` +
    ` fail=${result.summary.failed_count}`
  );
  if (result.status !== 'PASSED') process.exitCode = 1;
}

try {
  main();
} catch (error) {
  console.error(`[FRBStudio] Search Definition Test failed: ${error?.stack ?? error}`);
  process.exitCode = 1;
}
