import crypto from 'node:crypto';
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';

const root = process.cwd();

function parseArgs(argv) {
  const values = {
    fieldDefs: 'fielddefs/samples/frb_fft_measurement_field_definitions_v0_2.json',
    registry: 'data/json/config/validation_type_registry_v0_1.json',
    out: '',
    evidenceDir: ''
  };
  for (let index = 0; index < argv.length; index += 1) {
    const argument = argv[index];
    if (argument === '--field-defs') values.fieldDefs = argv[++index] ?? '';
    else if (argument === '--registry') values.registry = argv[++index] ?? '';
    else if (argument === '--out') values.out = argv[++index] ?? '';
    else if (argument === '--evidence-dir') values.evidenceDir = argv[++index] ?? '';
    else throw new Error(`Unsupported argument: ${argument}`);
  }
  return values;
}

function resolveInput(relativePath) {
  const fullPath = path.resolve(root, relativePath);
  if (!fs.existsSync(fullPath)) throw new Error(`Input file not found: ${relativePath}`);
  return fullPath;
}

function readSource(relativePath) {
  return fs.readFileSync(path.join(root, relativePath), 'utf8');
}

function loadRuntime() {
  const sandbox = { console, Date, JSON, RegExp, Number, String, Set, globalThis: null };
  sandbox.globalThis = sandbox;
  vm.createContext(sandbox);
  [
    'wwwroot/js/services/definition/definition_verification_common.js',
    'wwwroot/js/services/definition/field_contract_resolver.js',
    'wwwroot/js/services/definition/test_pattern_deriver.js',
    'wwwroot/js/services/definition/expected_resolver.js',
    'wwwroot/js/services/definition/definition_verification_service.js',
    'wwwroot/js/services/definition/definition_value_validator.js',
    'wwwroot/js/services/definition/cross_field_verification_service.js',
    'wwwroot/js/services/definition/cross_field_relation_evaluator.js',
    'wwwroot/js/services/definition/definition_test_runner_core.js',
    'wwwroot/js/services/definition/definition_test_evidence_builder.js'
  ].forEach(relativePath => vm.runInContext(readSource(relativePath), sandbox, { filename: relativePath }));
  return sandbox;
}

function sha256(buffer) {
  return crypto.createHash('sha256').update(buffer).digest('hex');
}

function writeJson(relativePath, value) {
  const fullPath = path.resolve(root, relativePath);
  fs.mkdirSync(path.dirname(fullPath), { recursive: true });
  fs.writeFileSync(fullPath, `${JSON.stringify(value, null, 2)}\n`, 'utf8');
  return relativePath.replaceAll('\\', '/');
}

function writeEvidence(evidenceDir, result, sandbox) {
  const normalizedDir = evidenceDir.replace(/[\\/]+$/, '');
  const files = {
    expectedFile: `${normalizedDir}/expected/definition_test_runner.expected.json`,
    actualFile: `${normalizedDir}/actual/definition_test_runner.actual.json`,
    diffFile: `${normalizedDir}/diff/definition_test_runner.diff.json`,
    relationsFile: `${normalizedDir}/relations/definition_test_runner_trace_relations.json`,
    summaryFile: `${normalizedDir}/summary/definition_test_runner.result.json`
  };
  sandbox.__runnerResult = result;
  sandbox.__sourceFiles = files;
  vm.runInContext(`
    globalThis.__evidence = new DefinitionTestEvidenceBuilder().buildArtifacts(__runnerResult, { source_files: __sourceFiles });
  `, sandbox);
  const evidence = JSON.parse(JSON.stringify(sandbox.__evidence));

  writeJson(files.expectedFile, evidence.expected);
  writeJson(files.actualFile, evidence.actual);
  writeJson(files.diffFile, evidence.diff);
  writeJson(files.relationsFile, evidence.relations);
  writeJson(files.summaryFile, evidence.summary);
  console.log(`[FRBStudio] Definition Test Evidence written: ${normalizedDir}`);
  return files;
}

function main() {
  const args = parseArgs(process.argv.slice(2));
  const fieldDefsPath = resolveInput(args.fieldDefs);
  const registryPath = resolveInput(args.registry);
  const fieldDefsBytes = fs.readFileSync(fieldDefsPath);
  const registryBytes = fs.readFileSync(registryPath);
  const fieldDefs = JSON.parse(fieldDefsBytes.toString('utf8'));
  const registry = JSON.parse(registryBytes.toString('utf8'));
  const sandbox = loadRuntime();

  sandbox.__fieldDefs = fieldDefs;
  sandbox.__registry = registry;
  sandbox.__metadata = {
    field_definition_path: args.fieldDefs,
    field_definition_sha256: sha256(fieldDefsBytes),
    registry_path: args.registry,
    registry_sha256: sha256(registryBytes)
  };
  vm.runInContext(`
    globalThis.__result = new DefinitionTestRunnerCore().runDocument(__fieldDefs, __registry, { source_metadata: __metadata });
  `, sandbox);
  const result = JSON.parse(JSON.stringify(sandbox.__result));
  const output = `${JSON.stringify(result, null, 2)}\n`;

  if (args.out) {
    const outputPath = path.resolve(root, args.out);
    fs.mkdirSync(path.dirname(outputPath), { recursive: true });
    fs.writeFileSync(outputPath, output, 'utf8');
    console.log(`[FRBStudio] Definition Test Result JSON written: ${outputPath}`);
  } else if (!args.evidenceDir) {
    process.stdout.write(output);
  }

  if (args.evidenceDir) writeEvidence(args.evidenceDir, result, sandbox);

  console.log(
    `[FRBStudio] Definition Test Runner: ${result.status}` +
    ` / fields=${result.summary.field_count}` +
    ` fieldPatterns=${result.summary.field_pattern_count}` +
    ` crossConstraints=${result.summary.cross_field_constraint_count}` +
    ` crossPatterns=${result.summary.cross_field_pattern_count}` +
    ` pass=${result.summary.passed_count}` +
    ` fail=${result.summary.failed_count}` +
    ` unresolved=${result.summary.unresolved_count}`
  );
  if (result.status === 'FAILED' || result.status === 'INVALID') process.exitCode = 1;
}

try {
  main();
} catch (error) {
  console.error(`[FRBStudio] Definition Test Runner failed: ${error?.stack ?? error}`);
  process.exitCode = 1;
}
