#!/usr/bin/env node
'use strict';

const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');

const SCHEMA_VERSION = 'fx_batch_entry_result_rows_v0_1';
const KIND = 'fx_batch_entry_result_rows';
const GENERATOR_ID = 'build_entry_result_rows_v0_1';
const DEFAULT_CATALOG_PATH = path.resolve(__dirname, '..', 'fx_simulation_reason_rule_catalog_v0_1.json');
const DEFAULT_SCAN_ROOT = path.resolve(__dirname, '..', '..', 'simulattion_集計');

function readJson(filePath) {
  try {
    return JSON.parse(fs.readFileSync(filePath, 'utf8'));
  } catch (error) {
    throw new Error(`JSON読込に失敗しました: ${filePath}\n${error.message}`);
  }
}

function writeJson(filePath, value) {
  fs.mkdirSync(path.dirname(filePath), { recursive: true });
  fs.writeFileSync(filePath, `${JSON.stringify(value, null, 2)}\n`, 'utf8');
}

function finiteNumber(value) {
  const number = Number(value);
  return Number.isFinite(number) ? number : null;
}

function round(value, digits = 6) {
  const number = finiteNumber(value);
  if (number === null) return null;
  const factor = 10 ** digits;
  const rounded = Math.round((number + Number.EPSILON) * factor) / factor;
  return Object.is(rounded, -0) ? 0 : rounded;
}

function roundJpy(value) {
  return round(value, 6);
}

function cleanText(value) {
  return value === null || value === undefined ? null : String(value).trim() || null;
}

function unique(values) {
  return [...new Set((values || []).filter((value) => value !== null && value !== undefined && value !== ''))];
}

function parseSimulationTime(value) {
  const text = cleanText(value);
  if (!text) return null;
  const match = text.match(/^(\d{4})-(\d{2})-(\d{2})[ T](\d{2}):(\d{2})(?::(\d{2}))?$/);
  if (!match) return null;
  const [, y, mo, d, h, mi, s = '0'] = match;
  return Date.UTC(Number(y), Number(mo) - 1, Number(d), Number(h), Number(mi), Number(s));
}

function durationMinutes(from, to) {
  const start = parseSimulationTime(from);
  const end = parseSimulationTime(to);
  if (start === null || end === null || end < start) return null;
  return Math.round((end - start) / 60000);
}

function sha256(value) {
  const text = typeof value === 'string' ? value : JSON.stringify(value);
  return crypto.createHash('sha256').update(text, 'utf8').digest('hex');
}

function buildCatalogMaps(catalog) {
  const reasonMap = new Map();
  const ruleMap = new Map();
  for (const item of catalog?.reason_codes || []) {
    if (!item || !item.code) continue;
    reasonMap.set(item.code, {
      code: item.code,
      text: item.ja || item.label || item.code,
      category: item.category || '判断理由'
    });
  }
  for (const item of catalog?.rule_ids || []) {
    if (!item || !item.code) continue;
    ruleMap.set(item.code, {
      code: item.code,
      text: item.ja || item.label || item.code,
      category: item.category || '使用ルール'
    });
  }
  return { reasonMap, ruleMap };
}

function mapCodes(codes, codeMap, fallbackText) {
  return unique(codes).map((code) => {
    const mapped = codeMap.get(code);
    if (mapped) return mapped;
    return { code, text: `${fallbackText}: ${code}`, category: '未登録' };
  });
}

function isMechanicalEntryReason(code) {
  return [
    'POSITION_LIFECYCLE_OPENED',
    'ANCHOR_FIRST_ADOPTION',
    'ANCHOR_FIXED',
    'ONE_ENTRY_PER_DOW_CONFIRMATION',
    'OPPORTUNITY',
    'POSITION_LIFECYCLE'
  ].some((token) => String(code || '').includes(token));
}

function entryReasonShort(details) {
  const meaningful = details.filter((item) => !isMechanicalEntryReason(item.code));
  return (meaningful.length ? meaningful : details)
    .slice(0, 6)
    .map((item) => item.text)
    .join(' / ');
}

function eventSequence(event) {
  const step = finiteNumber(event?.case_step_no);
  if (step !== null) return step;
  const time = parseSimulationTime(event?.simulation_time);
  return time === null ? Number.MAX_SAFE_INTEGER : time;
}

function eventPrice(event) {
  return finiteNumber(event?.execution?.price ?? event?.execution?.entry_price ?? event?.price);
}

function eventUnits(event) {
  return finiteNumber(event?.execution?.units ?? event?.execution?.initial_units) || 0;
}

function tradeGroupKey(caseId, event) {
  const lane = cleanText(event?.rule_lane) || cleanText(event?.execution?.rule_lane) || 'UNKNOWN';
  const tradeId = cleanText(event?.trade_id) || cleanText(event?.event_id) || `event_${eventSequence(event)}`;
  return `${caseId}::${lane}::${tradeId}`;
}

function resultFromProfit(profit, hasExit) {
  if (!hasExit) {
    return {
      result_code: 'OPEN',
      result_label: '未決済',
      success: null,
      profit_loss_code: 'UNREALIZED',
      profit_loss_label: '未確定'
    };
  }
  const amount = finiteNumber(profit) || 0;
  if (amount > 0) {
    return {
      result_code: 'SUCCESS',
      result_label: '成功',
      success: true,
      profit_loss_code: 'PROFIT',
      profit_loss_label: '利益'
    };
  }
  if (amount < 0) {
    return {
      result_code: 'FAILURE',
      result_label: '失敗',
      success: false,
      profit_loss_code: 'LOSS',
      profit_loss_label: '損失'
    };
  }
  return {
    result_code: 'BREAK_EVEN',
    result_label: '引分',
    success: null,
    profit_loss_code: 'BREAK_EVEN',
    profit_loss_label: '±0'
  };
}

function weightedAverage(items) {
  let weighted = 0;
  let units = 0;
  for (const item of items) {
    const price = finiteNumber(item.price);
    const amount = finiteNumber(item.units);
    if (price === null || amount === null || amount <= 0) continue;
    weighted += price * amount;
    units += amount;
  }
  return units > 0 ? weighted / units : null;
}

function buildAddOnDetails(events, maps) {
  return events.map((event, index) => {
    const reasonDetails = mapCodes(event.reason_codes || [], maps.reasonMap, '日本語理由未登録');
    const levels = unique(event?.execution?.add_on_levels || event?.execution?.consumed_add_on_levels || []);
    return {
      add_on_no: index + 1,
      event_id: cleanText(event.event_id),
      time: cleanText(event.simulation_time),
      case_step_no: finiteNumber(event.case_step_no),
      level: levels.join(', ') || null,
      side: cleanText(event?.execution?.side),
      units: finiteNumber(event?.execution?.units),
      price: round(eventPrice(event)),
      summary: cleanText(event.summary),
      reason_codes: reasonDetails.map((item) => item.code),
      reason_text: reasonDetails.map((item) => item.text).join(' / ') || null
    };
  });
}

function buildEntryResultRow({ batch, caseData, entryEvent, addOnEvents, exitEvent, rowNo, maps }) {
  const entryExecution = entryEvent.execution || {};
  const exitExecution = exitEvent?.execution || {};
  const lane = cleanText(entryEvent.rule_lane) || cleanText(entryExecution.rule_lane) || 'UNKNOWN';
  const tradeId = cleanText(entryEvent.trade_id) || cleanText(entryEvent.event_id);
  const initialUnits = finiteNumber(entryExecution.units ?? entryExecution.initial_units) || 0;
  const entryPrice = finiteNumber(entryExecution.entry_price ?? entryExecution.price ?? entryEvent.price);
  const addOnDetails = buildAddOnDetails(addOnEvents, maps);
  const addOnUnits = addOnDetails.reduce((sum, item) => sum + (finiteNumber(item.units) || 0), 0);
  const entryLegs = [
    { price: entryPrice, units: initialUnits },
    ...addOnDetails.map((item) => ({ price: item.price, units: item.units }))
  ];
  const totalUnits = initialUnits + addOnUnits;
  const averageEntryPrice = weightedAverage(entryLegs);
  const hasExit = Boolean(exitEvent);
  const realizedProfitJpy = hasExit ? roundJpy(exitExecution.realized_profit_jpy) : null;
  const result = resultFromProfit(realizedProfitJpy, hasExit);
  const entryReasonDetails = mapCodes(entryEvent.reason_codes || [], maps.reasonMap, '日本語理由未登録');
  const entryRuleDetails = mapCodes(entryEvent.rule_ids || [], maps.ruleMap, '日本語ルール未登録');
  const exitReasonDetails = mapCodes(exitEvent?.reason_codes || [], maps.reasonMap, '日本語理由未登録');
  const exitRuleDetails = mapCodes(exitEvent?.rule_ids || [], maps.ruleMap, '日本語ルール未登録');
  const entryStep = finiteNumber(entryEvent.case_step_no);
  const exitStep = finiteNumber(exitEvent?.case_step_no);
  const entryTime = cleanText(entryEvent.simulation_time);
  const exitTime = cleanText(exitEvent?.simulation_time);
  const exitPrice = hasExit ? finiteNumber(exitExecution.price ?? exitEvent.price) : null;
  const closeClass = cleanText(exitExecution.close_class);
  const exitType = cleanText(exitExecution.exit_type) || (exitEvent?.event_type === 'stop_close' ? 'STOP_CLOSE' : closeClass);
  const exitReasonCode = cleanText(exitExecution.exit_reason_code) || exitReasonDetails[0]?.code || null;
  const exitReasonSummary = cleanText(exitEvent?.summary)
    || exitReasonDetails.map((item) => item.text).join(' / ')
    || null;
  const rowKey = `${caseData.case_id || 'case'}::${lane}::${tradeId || entryEvent.event_id || rowNo}`;
  const addOnPricesText = addOnDetails
    .map((item) => `${item.level ? `${item.level} ` : ''}${item.price ?? '-'} × ${item.units ?? 0}`)
    .join(' / ') || null;

  return {
    row_no: rowNo,
    row_id: `entry_result_${sha256(rowKey).slice(0, 16)}`,
    result_code: result.result_code,
    result_label: result.result_label,
    success: result.success,
    profit_loss_code: result.profit_loss_code,
    profit_loss_label: result.profit_loss_label,
    realized_profit_jpy: realizedProfitJpy,
    rule_lane: lane,
    side: cleanText(entryExecution.side),
    entry_time: entryTime,
    exit_time: exitTime,
    entry_reason_short: entryReasonShort(entryReasonDetails) || cleanText(entryEvent.summary),
    entry_reason_summary: entryReasonDetails.map((item) => item.text).join(' / ') || cleanText(entryEvent.summary),
    exit_reason_summary: exitReasonSummary,
    entry_price: round(entryPrice),
    average_entry_price: round(averageEntryPrice),
    exit_price: round(exitPrice),
    entry_level: cleanText(entryExecution.entry_level),
    entry_execution_mode: cleanText(entryExecution.entry_execution_mode),
    target_label: cleanText(entryExecution.target_label ?? exitExecution.target_label),
    target_price: round(entryExecution.target_price ?? exitExecution.target_price),
    stop_basis: cleanText(entryExecution.stop_basis ?? exitExecution.stop_basis),
    stop_price: round(entryExecution.stop_price ?? exitExecution.stop_price),
    initial_units: round(initialUnits),
    add_on_count: addOnDetails.length,
    add_on_units: round(addOnUnits),
    total_units: round(totalUnits),
    closed_units: round(exitExecution.units),
    add_on_prices_text: addOnPricesText,
    close_class: closeClass,
    exit_type: exitType,
    exit_reason_code: exitReasonCode,
    trade_status: hasExit ? 'CLOSED' : 'OPEN',
    holding_minutes: durationMinutes(entryTime, exitTime),
    holding_step_count: entryStep !== null && exitStep !== null ? exitStep - entryStep : null,
    initial_risk_jpy: roundJpy(entryExecution.initial_risk_jpy ?? exitExecution.initial_risk_jpy),
    risk_multiple: round(exitExecution.risk_multiple),
    profit_vs_initial_risk_pct: round(exitExecution.profit_vs_initial_risk_pct),
    batch_run_id: cleanText(batch.batch_run_id),
    case_id: cleanText(caseData.case_id),
    trade_id: tradeId,
    entry_event_id: cleanText(entryEvent.event_id),
    exit_event_id: cleanText(exitEvent?.event_id),
    entry_case_step_no: entryStep,
    exit_case_step_no: exitStep,
    entry_summary: cleanText(entryEvent.summary),
    exit_summary: cleanText(exitEvent?.summary),
    entry_reason_codes_text: entryReasonDetails.map((item) => item.code).join(' / ') || null,
    entry_rule_ids_text: entryRuleDetails.map((item) => item.code).join(' / ') || null,
    exit_reason_codes_text: exitReasonDetails.map((item) => item.code).join(' / ') || null,
    exit_rule_ids_text: exitRuleDetails.map((item) => item.code).join(' / ') || null,
    entry_reason_details: entryReasonDetails,
    entry_rule_details: entryRuleDetails,
    add_on_details: addOnDetails,
    exit_reason_details: exitReasonDetails,
    exit_rule_details: exitRuleDetails
  };
}

function createLaneSummary(rows) {
  const summary = {};
  for (const row of rows) {
    const lane = row.rule_lane || 'UNKNOWN';
    if (!summary[lane]) {
      summary[lane] = {
        entry_count: 0,
        closed_trade_count: 0,
        open_trade_count: 0,
        success_count: 0,
        failure_count: 0,
        break_even_count: 0,
        add_on_count: 0,
        realized_profit_jpy: 0,
        win_rate_pct: null
      };
    }
    const item = summary[lane];
    item.entry_count += 1;
    item.add_on_count += finiteNumber(row.add_on_count) || 0;
    if (row.trade_status === 'OPEN') item.open_trade_count += 1;
    else item.closed_trade_count += 1;
    if (row.result_code === 'SUCCESS') item.success_count += 1;
    if (row.result_code === 'FAILURE') item.failure_count += 1;
    if (row.result_code === 'BREAK_EVEN') item.break_even_count += 1;
    item.realized_profit_jpy += finiteNumber(row.realized_profit_jpy) || 0;
  }
  for (const item of Object.values(summary)) {
    item.realized_profit_jpy = roundJpy(item.realized_profit_jpy);
    const denominator = item.success_count + item.failure_count + item.break_even_count;
    item.win_rate_pct = denominator > 0 ? round((item.success_count / denominator) * 100, 2) : null;
  }
  return summary;
}

function buildEntryResultProjection(batch, catalog, sourceFileName = null, generatedAt = new Date().toISOString()) {
  if (!batch || !Array.isArray(batch.cases)) {
    throw new Error('Batch JSONのcases配列が見つかりません。');
  }
  const maps = buildCatalogMaps(catalog || {});
  const rows = [];
  const warnings = [];
  let sourceEventCount = 0;

  for (const caseData of batch.cases) {
    const caseId = cleanText(caseData.case_id) || 'case_unknown';
    const events = Array.isArray(caseData.execution_events) ? caseData.execution_events : [];
    sourceEventCount += events.length;
    const groups = new Map();

    for (const event of events) {
      if (!['entry', 'add_on', 'close', 'stop_close'].includes(event?.event_type)) continue;
      const key = tradeGroupKey(caseId, event);
      if (!groups.has(key)) groups.set(key, []);
      groups.get(key).push(event);
    }

    for (const [key, groupEvents] of groups) {
      const ordered = [...groupEvents].sort((a, b) => eventSequence(a) - eventSequence(b));
      const entries = ordered.filter((event) => event.event_type === 'entry');
      const addOns = ordered.filter((event) => event.event_type === 'add_on');
      const exits = ordered.filter((event) => ['close', 'stop_close'].includes(event.event_type));

      if (entries.length === 0) {
        warnings.push({ code: 'ENTRY_EVENT_MISSING', group_key: key, event_count: ordered.length });
        continue;
      }
      if (entries.length > 1) {
        warnings.push({ code: 'MULTIPLE_ENTRY_EVENTS', group_key: key, entry_event_count: entries.length });
      }
      if (exits.length > 1) {
        warnings.push({ code: 'MULTIPLE_EXIT_EVENTS', group_key: key, exit_event_count: exits.length });
      }

      rows.push(buildEntryResultRow({
        batch,
        caseData,
        entryEvent: entries[0],
        addOnEvents: addOns,
        exitEvent: exits[exits.length - 1] || null,
        rowNo: 0,
        maps
      }));
    }
  }

  rows.sort((a, b) => {
    const at = parseSimulationTime(a.entry_time) ?? Number.MAX_SAFE_INTEGER;
    const bt = parseSimulationTime(b.entry_time) ?? Number.MAX_SAFE_INTEGER;
    if (at !== bt) return at - bt;
    if ((a.case_id || '') !== (b.case_id || '')) return String(a.case_id || '').localeCompare(String(b.case_id || ''));
    if ((a.rule_lane || '') !== (b.rule_lane || '')) return String(a.rule_lane || '').localeCompare(String(b.rule_lane || ''));
    return String(a.trade_id || '').localeCompare(String(b.trade_id || ''));
  });
  rows.forEach((row, index) => { row.row_no = index + 1; });

  const laneSummary = createLaneSummary(rows);
  const closedRows = rows.filter((row) => row.trade_status === 'CLOSED');
  const summary = {
    case_count: batch.cases.length,
    source_execution_event_count: sourceEventCount,
    entry_result_row_count: rows.length,
    closed_trade_count: closedRows.length,
    open_trade_count: rows.length - closedRows.length,
    success_count: rows.filter((row) => row.result_code === 'SUCCESS').length,
    failure_count: rows.filter((row) => row.result_code === 'FAILURE').length,
    break_even_count: rows.filter((row) => row.result_code === 'BREAK_EVEN').length,
    add_on_count: rows.reduce((sum, row) => sum + (finiteNumber(row.add_on_count) || 0), 0),
    realized_profit_jpy: roundJpy(rows.reduce((sum, row) => sum + (finiteNumber(row.realized_profit_jpy) || 0), 0)),
    win_rate_pct: null,
    lane_summaries: laneSummary,
    warning_count: warnings.length
  };
  const winDenominator = summary.success_count + summary.failure_count + summary.break_even_count;
  summary.win_rate_pct = winDenominator > 0 ? round((summary.success_count / winDenominator) * 100, 2) : null;

  const projectionHash = sha256({ summary, rows });
  return {
    schema_version: SCHEMA_VERSION,
    kind: KIND,
    generator_id: GENERATOR_ID,
    generated_at: generatedAt,
    source_batch_file: sourceFileName,
    source_batch_run_id: cleanText(batch.batch_run_id),
    source_status: cleanText(batch.status),
    source_result_hash: cleanText(batch.result_hash),
    source_rule_version: cleanText(batch.rule_version),
    source_app_version: cleanText(batch.app_version),
    reason_catalog_id: cleanText(catalog?.catalog_id),
    projection_hash: projectionHash,
    summary,
    warnings,
    entry_result_rows: rows
  };
}

function isGeneratedOutput(filePath) {
  return /_entry_results\.json$/i.test(filePath) || /_entry_result_rows\.json$/i.test(filePath);
}

function collectBatchFiles(inputPath) {
  const resolved = path.resolve(inputPath);
  if (!fs.existsSync(resolved)) throw new Error(`入力が見つかりません: ${resolved}`);
  const stat = fs.statSync(resolved);
  if (stat.isFile()) {
    if (!/^batch_.*\.json$/i.test(path.basename(resolved)) || isGeneratedOutput(resolved)) return [];
    return [resolved];
  }
  const results = [];
  const stack = [resolved];
  while (stack.length) {
    const current = stack.pop();
    for (const entry of fs.readdirSync(current, { withFileTypes: true })) {
      const full = path.join(current, entry.name);
      if (entry.isDirectory()) stack.push(full);
      else if (/^batch_.*\.json$/i.test(entry.name) && !isGeneratedOutput(entry.name)) results.push(full);
    }
  }
  return results.sort();
}

function outputPathFor(inputFile, outputDir) {
  const name = path.basename(inputFile, '.json') + '_entry_results.json';
  return outputDir ? path.resolve(outputDir, name) : path.join(path.dirname(inputFile), name);
}

function parseArgs(argv) {
  const options = {
    inputs: [],
    catalogPath: DEFAULT_CATALOG_PATH,
    outputDir: null,
    dryRun: false
  };
  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];
    if (arg === '--catalog') options.catalogPath = path.resolve(argv[++i]);
    else if (arg === '--output-dir') options.outputDir = path.resolve(argv[++i]);
    else if (arg === '--dry-run') options.dryRun = true;
    else if (arg === '--help' || arg === '-h') options.help = true;
    else options.inputs.push(arg);
  }
  if (options.inputs.length === 0) options.inputs.push(DEFAULT_SCAN_ROOT);
  return options;
}

function printHelp() {
  console.log(`Entry Result Rows Builder\n\n` +
    `使い方:\n` +
    `  node build_entry_result_rows_v0_1.cjs [batch JSONまたはフォルダ] [options]\n\n` +
    `Options:\n` +
    `  --catalog <path>     理由・ルールカタログJSON\n` +
    `  --output-dir <path>  出力先フォルダ。省略時は入力JSONと同じ場所\n` +
    `  --dry-run            書き込まず件数だけ確認\n` +
    `  -h, --help           ヘルプ\n\n` +
    `入力省略時は gpt_fx_lab/simulattion_集計 の batch_*.json を処理します。\n` +
    `元のBatch JSONは変更せず、*_entry_results.json を生成します。`);
}

function runCli(argv = process.argv.slice(2)) {
  const options = parseArgs(argv);
  if (options.help) {
    printHelp();
    return 0;
  }
  const catalog = readJson(options.catalogPath);
  const files = unique(options.inputs.flatMap(collectBatchFiles));
  if (files.length === 0) throw new Error('処理対象の batch_*.json が見つかりません。');

  let totalRows = 0;
  for (const inputFile of files) {
    const batch = readJson(inputFile);
    const output = buildEntryResultProjection(batch, catalog, path.basename(inputFile));
    const outputFile = outputPathFor(inputFile, options.outputDir);
    totalRows += output.summary.entry_result_row_count;
    if (!options.dryRun) writeJson(outputFile, output);
    console.log(`${options.dryRun ? '[DRY-RUN] ' : ''}${path.basename(inputFile)} -> ${path.basename(outputFile)} / rows=${output.summary.entry_result_row_count}, closed=${output.summary.closed_trade_count}, open=${output.summary.open_trade_count}, pnl=${output.summary.realized_profit_jpy}`);
  }
  console.log(`完了: files=${files.length}, entry_result_rows=${totalRows}`);
  return 0;
}

if (require.main === module) {
  try {
    process.exitCode = runCli();
  } catch (error) {
    console.error(error.stack || error.message || String(error));
    process.exitCode = 1;
  }
}

module.exports = {
  SCHEMA_VERSION,
  KIND,
  GENERATOR_ID,
  buildCatalogMaps,
  buildEntryResultProjection,
  collectBatchFiles,
  createLaneSummary,
  durationMinutes,
  resultFromProfit,
  runCli,
  weightedAverage
};
