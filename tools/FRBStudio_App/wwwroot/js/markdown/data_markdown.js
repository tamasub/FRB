// v0.18.6-markdown-export-mode-exportdef-rules
// Data JSON -> Markdown export.
// Restores the global exportMarkdown() contract used by:
// - header button #exportMarkdownBtn
// - toolbar.executeButton.action = ExportMarkdown via ActionRegistry

function markdownCurrentDataName() {
  const candidates = [];
  if (typeof launchRuntime !== 'undefined' && launchRuntime?.dataParam) candidates.push(launchRuntime.dataParam);
  if (typeof currentDataViewDefCandidateDataName !== 'undefined' && currentDataViewDefCandidateDataName) candidates.push(currentDataViewDefCandidateDataName);
  const inputValue = $('dataNameInput')?.value;
  if (inputValue) candidates.push(inputValue);
  if (typeof currentDataApiUrl !== 'undefined' && currentDataApiUrl) {
    try {
      if (typeof jsonNameFromUrl === 'function') candidates.push(jsonNameFromUrl(currentDataApiUrl, 'data'));
    } catch { /* ignore */ }
    candidates.push(currentDataApiUrl);
  }
  for (const c of candidates) {
    const base = markdownBaseName(c);
    if (base) return base;
  }
  return 'data.json';
}

function markdownCurrentViewTitle() {
  const view = typeof mainView === 'function' ? mainView() : (viewDef?.views?.[0] ?? viewDef ?? {});
  return String(sourceData?.title ?? view?.caption ?? viewDef?.app?.name ?? 'Studio Export');
}

function markdownSections() {
  const view = typeof mainView === 'function' ? mainView() : (viewDef?.views?.[0] ?? viewDef ?? {});
  return Array.isArray(view?.sections) ? view.sections : [];
}

function markdownCurrentView() {
  return typeof mainView === 'function' ? mainView() : (viewDef?.views?.[0] ?? viewDef ?? {});
}

function markdownExportConfig() {
  const view = markdownCurrentView();
  return view?.markdown ?? viewDef?.markdown ?? {};
}

function markdownDefaultExportModes() {
  return [
    {
      id: 'review_report',
      caption: 'レビュー用Markdown出力',
      type: 'review_report',
      fieldPolicy: 'respect_markdown_export'
    },
    {
      id: 'full_dump',
      caption: '全項目Markdown出力',
      type: 'full_dump',
      fieldPolicy: 'all'
    }
  ];
}

function markdownNormalizeExportMode(mode) {
  if (!mode || typeof mode !== 'object') return null;
  const type = String(mode.type ?? mode.id ?? '').trim() || 'review_report';
  const id = String(mode.id ?? type).trim();
  if (!id) return null;
  return {
    ...mode,
    id,
    type,
    caption: mode.caption ?? mode.label ?? markdownExportModeCaption(type)
  };
}

function markdownExportModeCaption(type) {
  switch (String(type ?? '').toLowerCase()) {
    case 'full_dump': return '全項目Markdown出力';
    case 'document_sections':
    case 'document_rebuild': return '文書Markdown出力';
    case 'review_report':
    default: return 'レビュー用Markdown出力';
  }
}

function markdownAvailableExportModes() {
  const cfg = markdownExportConfig();
  const configured = Array.isArray(cfg?.modes) ? cfg.modes.map(markdownNormalizeExportMode).filter(Boolean) : [];
  const merged = new Map();

  configured.forEach(mode => merged.set(mode.id, mode));
  markdownDefaultExportModes().forEach(mode => {
    if (!merged.has(mode.id)) merged.set(mode.id, markdownNormalizeExportMode(mode));
  });

  if (!configured.length && (cfg?.type === 'document_sections' || cfg?.type === 'document_rebuild')) {
    merged.set('document_rebuild', markdownNormalizeExportMode({ ...cfg, id: 'document_rebuild', caption: '文書Markdown出力' }));
  }
  return [...merged.values()];
}

function markdownDefaultExportModeId() {
  const modes = markdownAvailableExportModes();
  const cfg = markdownExportConfig();
  const configuredDefault = String(cfg?.defaultMode ?? cfg?.default_mode ?? '').trim();
  if (configuredDefault && modes.some(m => m.id === configuredDefault)) return configuredDefault;
  return modes[0]?.id || 'review_report';
}

function markdownSelectedExportModeId() {
  const select = $('exportMarkdownModeSelect');
  const modes = markdownAvailableExportModes();
  if (select?.value && modes.some(m => m.id === select.value)) return select.value;
  return markdownDefaultExportModeId();
}

function markdownExportModeById(modeId) {
  const modes = markdownAvailableExportModes();
  const id = String(modeId ?? '').trim() || markdownDefaultExportModeId();
  return modes.find(m => m.id === id) || modes[0] || markdownNormalizeExportMode({ id: 'review_report', type: 'review_report' });
}

function updateMarkdownExportModeSelect() {
  const select = $('exportMarkdownModeSelect');
  if (!select) return;
  const current = select.value;
  const modes = markdownAvailableExportModes();
  select.innerHTML = '';
  modes.forEach(mode => {
    const option = document.createElement('option');
    option.value = mode.id;
    option.textContent = mode.caption || mode.id;
    option.title = mode.description || markdownExportModeCaption(mode.type);
    select.appendChild(option);
  });
  const desired = current && modes.some(m => m.id === current) ? current : markdownDefaultExportModeId();
  select.value = desired;
  select.disabled = modes.length <= 1 || typeof sourceData === 'undefined' || !sourceData;
  if (typeof syncViewExecuteButtonVisibilityForMarkdownMode === 'function') {
    syncViewExecuteButtonVisibilityForMarkdownMode();
  }
}

function markdownShouldExportDefinition(def) {
  if (!def) return true;
  if (def.markdown?.export === false) return false;
  if (def.markdown?.visible === false) return false;
  if (def.export === false) return false;
  if (def.visible === false) return false;
  return true;
}

function markdownShouldExportSection(section) {
  return markdownShouldExportDefinition(section);
}

function markdownShouldExportField(field) {
  return markdownShouldExportDefinition(field);
}

function markdownFormatFieldValue(value, field=null) {
  if (value == null) return '';
  if (field && typeof formatValue === 'function') {
    try {
      const formatted = formatValue(value, field);
      if (typeof formatted === 'string' && formatted !== '[object Object]') return formatted;
    } catch { /* fallback */ }
  }
  return markdownValueToText(value);
}

function markdownHeaderFields() {
  const lines = [];
  const formSections = markdownSections().filter(s => s.type === 'form' && (s.role ?? '') !== 'detailOnly' && markdownShouldExportSection(s));
  formSections.forEach(section => {
    const base = getByPath(sourceData, section.dataPath || '$') ?? sourceData;
    const fields = Array.isArray(section.fields) ? section.fields : [];
    fields.forEach(field => {
      if (!field?.field || !markdownShouldExportField(field)) return;
      const value = getByPath(base, field.field);
      if (markdownValueIsEmpty(value)) return;
      if (Array.isArray(value) || typeof value === 'object') return;
      const label = field.caption ?? field.field;
      lines.push(`| ${markdownEscapeTableCell(label, 80)} | ${markdownEscapeTableCell(markdownFormatFieldValue(value, field), 240)} |`);
    });
  });
  return lines;
}

function markdownVisibleGridFields(section) {
  return (section?.fields ?? []).filter(f => f?.field && f.grid?.visible !== false && markdownShouldExportField(f));
}

function markdownRowsForSection(section) {
  if (section === (typeof gridDef === 'function' ? gridDef() : null) && Array.isArray(filteredRows) && filteredRows.length) {
    return filteredRows.map(x => x.row);
  }
  const rows = getByPath(sourceData, section.dataPath);
  return Array.isArray(rows) ? rows : [];
}

function markdownGridTable(section) {
  if (!markdownShouldExportSection(section)) return [];
  const fields = markdownVisibleGridFields(section);
  const rows = markdownRowsForSection(section);
  if (!fields.length) return [];

  const lines = [];
  lines.push(`## ${section.caption ?? section.id ?? '一覧'}`);
  lines.push('');
  lines.push(`件数: ${rows.length}`);
  lines.push('');
  lines.push(`| ${fields.map(f => markdownEscapeTableCell(f.caption ?? f.field, 80)).join(' | ')} |`);
  lines.push(`| ${fields.map(() => '---').join(' | ')} |`);
  rows.forEach(row => {
    lines.push(`| ${fields.map(f => markdownEscapeTableCell(markdownFormatFieldValue(getByPath(row, f.field), f))).join(' | ')} |`);
  });
  lines.push('');
  return lines;
}

function markdownRuleTitle(row, index, section) {
  const no = getByPath(row, 'section_no') || getByPath(row, 'no') || (index + 1);
  const title = getByPath(row, 'title') || getByPath(row, section?.keyField) || getByPath(row, 'rule_id') || `Item ${index + 1}`;
  return `${no} ${title}`.trim();
}

function markdownAppendStructuredValue(lines, heading, value) {
  if (markdownValueIsEmpty(value)) return;
  lines.push(`#### ${heading}`);
  lines.push('');
  if (typeof value === 'string') {
    lines.push(value);
  } else if (Array.isArray(value)) {
    value.forEach((item, index) => {
      if (item && typeof item === 'object') {
        const text = item.decision || item.change_type || item.message || item.reason || item.history_id || `item_${index + 1}`;
        lines.push(`- ${markdownValueToText(text)}`);
        const rest = { ...item };
        delete rest.decision;
        delete rest.change_type;
        delete rest.message;
        delete rest.reason;
        if (Object.keys(rest).length) lines.push(markdownFence(JSON.stringify(rest, null, 2), 'json'));
      } else {
        lines.push(`- ${markdownValueToText(item)}`);
      }
    });
  } else {
    lines.push(markdownFence(markdownValueToText(value), 'json'));
  }
  lines.push('');
}

function markdownGridDetails(section) {
  if (!markdownShouldExportSection(section)) return [];
  const rows = markdownRowsForSection(section);
  if (!rows.length) return [];
  const fields = Array.isArray(section.fields) ? section.fields : [];
  const preferred = ['summary', 'body', 'ceremony_phrase', 'user_comment', 'ai_response', 'user_reply', 'ai_followup_response', 'decision_log', 'change_history', 'notes'];
  const preferredFields = preferred
    .map(name => fields.find(f => f.field === name) ?? { field: name, caption: name })
    .filter(f => markdownShouldExportField(f))
    .filter(f => rows.some(row => !markdownValueIsEmpty(getByPath(row, f.field))));

  const lines = [];
  lines.push(`## ${section.caption ?? section.id ?? '詳細'} 詳細`);
  lines.push('');
  rows.forEach((row, index) => {
    lines.push(`### ${markdownRuleTitle(row, index, section)}`);
    lines.push('');

    const meta = ['rule_id', 'category', 'priority', 'review_status', 'verification_status', 'approval_decision', 'introduced_in']
      .map(name => ({ name, field: fields.find(f => f.field === name) ?? { field: name, caption: name } }))
      .filter(x => markdownShouldExportField(x.field))
      .filter(x => !markdownValueIsEmpty(getByPath(row, x.name)));
    if (meta.length) {
      lines.push('| 項目 | 値 |');
      lines.push('|---|---|');
      meta.forEach(({ name, field }) => lines.push(`| ${markdownEscapeTableCell(field.caption ?? name, 80)} | ${markdownEscapeTableCell(markdownFormatFieldValue(getByPath(row, name), field), 240)} |`));
      lines.push('');
    }

    preferredFields.forEach(field => {
      const value = getByPath(row, field.field);
      if (markdownValueIsEmpty(value)) return;
      markdownAppendStructuredValue(lines, field.caption ?? field.field, value);
    });
  });
  return lines;
}

function buildReviewReportMarkdown() {
  if (!viewDef || !sourceData) throw new Error('Markdown出力するData/ViewDefが読み込まれていません');

  const title = markdownCurrentViewTitle();
  const dataName = markdownCurrentDataName();
  const lines = [];
  lines.push(`# ${title}`);
  lines.push('');
  lines.push('<!-- Generated by FRB Studio / JSON Object Studio -->');
  lines.push('');
  lines.push(`- Mode: review_report`);
  lines.push(`- Data: \`${dataName}\``);
  if (typeof lastLoadedDefName !== 'undefined' && lastLoadedDefName) lines.push(`- ViewDef: \`${lastLoadedDefName}\``);
  lines.push(`- Exported At: ${(typeof studioFormatDateTime === 'function' ? studioFormatDateTime() : new Date().toLocaleString('sv-SE').replace(' ', '_'))}`);
  lines.push('');

  const header = markdownHeaderFields();
  if (header.length) {
    lines.push('## 基本情報');
    lines.push('');
    lines.push('| 項目 | 値 |');
    lines.push('|---|---|');
    lines.push(...header);
    lines.push('');
  }

  markdownSections().filter(s => s.type === 'grid').forEach(section => {
    lines.push(...markdownGridTable(section));
  });

  markdownSections().filter(s => s.type === 'grid').forEach(section => {
    lines.push(...markdownGridDetails(section));
  });

  return lines.join('\n').replace(/\n{4,}/g, '\n\n\n');
}

function buildFullDumpMarkdown(mode={}) {
  if (!viewDef || !sourceData) throw new Error('Markdown出力するData/ViewDefが読み込まれていません');
  const title = mode.title || markdownCurrentViewTitle();
  const dataName = markdownCurrentDataName();
  const lines = [];
  lines.push(`# ${title}`);
  lines.push('');
  lines.push('<!-- Generated by FRB Studio / JSON Object Studio -->');
  lines.push('');
  lines.push(`- Mode: full_dump`);
  lines.push(`- Data: \`${dataName}\``);
  if (typeof lastLoadedDefName !== 'undefined' && lastLoadedDefName) lines.push(`- ViewDef: \`${lastLoadedDefName}\``);
  lines.push(`- Exported At: ${(typeof studioFormatDateTime === 'function' ? studioFormatDateTime() : new Date().toLocaleString('sv-SE').replace(' ', '_'))}`);
  lines.push('');
  lines.push('## Data JSON Full Dump');
  lines.push('');
  lines.push(markdownFence(JSON.stringify(sourceData, null, 2), 'json'));
  lines.push('');
  return lines.join('\n');
}

function markdownSourceRowsForMode(mode={}) {
  const source = mode.source ?? mode.rowPath ?? mode.dataPath ?? '$.rules';
  if (source === 'rows' || source === 'currentRows' || source === 'allRows') {
    const section = markdownSections().find(s => s.type === 'grid') || (typeof gridDef === 'function' ? gridDef() : null);
    return section ? markdownRowsForSection(section) : [];
  }
  const value = getByPath(sourceData, source);
  return Array.isArray(value) ? value : [];
}

function markdownSortRowsForMode(rows, mode={}) {
  const sortField = mode.sortField ?? mode.orderField ?? mode.order_field;
  if (!sortField) return rows;
  return [...rows].sort((a, b) => {
    const av = getByPath(a, sortField);
    const bv = getByPath(b, sortField);
    if (av == null && bv == null) return 0;
    if (av == null) return 1;
    if (bv == null) return -1;
    if (typeof av === 'number' && typeof bv === 'number') return av - bv;
    return String(av).localeCompare(String(bv), 'ja');
  });
}

function markdownHeadingLineForRow(row, index, mode={}) {
  const headingMarkdownField = mode.headingMarkdownField ?? mode.heading_markdown_field;
  if (headingMarkdownField) {
    const line = getByPath(row, headingMarkdownField);
    if (!markdownValueIsEmpty(line)) return String(line).trim();
  }
  const headingField = mode.headingField ?? mode.heading_field ?? 'source_heading';
  const levelField = mode.headingLevelField ?? mode.heading_level_field ?? 'source_heading_level';
  const heading = getByPath(row, headingField) || getByPath(row, 'title') || `Item ${index + 1}`;
  const rawLevel = Number(getByPath(row, levelField) ?? mode.headingLevel ?? mode.heading_level ?? 2);
  const level = Math.max(1, Math.min(6, Number.isFinite(rawLevel) ? rawLevel : 2));
  const text = String(heading).trim();
  if (/^#{1,6}\s/.test(text)) return text;
  return `${'#'.repeat(level)} ${text}`;
}


function markdownModeHasExplicitSource(mode={}) {
  return mode && (
    Object.prototype.hasOwnProperty.call(mode, 'source') ||
    Object.prototype.hasOwnProperty.call(mode, 'rowPath') ||
    Object.prototype.hasOwnProperty.call(mode, 'row_path') ||
    Object.prototype.hasOwnProperty.call(mode, 'dataPath') ||
    Object.prototype.hasOwnProperty.call(mode, 'data_path')
  );
}

function markdownDocumentFieldCaption(field={}) {
  return field.caption ?? field.label ?? field.title ?? field.field ?? '';
}

function markdownDocumentFieldList(section={}, mode={}) {
  const fields = Array.isArray(section.fields) ? section.fields : [];
  return fields
    .filter(field => field?.field)
    .filter(field => markdownShouldExportField(field))
    .filter(field => field.markdown?.document !== false && field.markdown?.document_export !== false);
}

function markdownDocumentValueKind(value) {
  if (Array.isArray(value)) return 'array';
  if (value && typeof value === 'object') return 'object';
  return 'scalar';
}

function markdownDocumentCellValue(value, maxLen=360) {
  if (value == null) return '';
  let text;
  if (typeof value === 'object') {
    try { text = JSON.stringify(value); }
    catch { text = String(value); }
  } else {
    text = String(value);
  }
  return markdownEscapeTableCell(text, maxLen);
}

function markdownNormalizeDocumentSubGridColumn(raw) {
  if (typeof raw === 'string') return { field: raw, caption: raw, type: 'text' };
  if (!raw || typeof raw !== 'object') return null;
  const name = raw.field ?? raw.key ?? raw.name ?? raw.column;
  if (!name) return null;
  return {
    ...raw,
    field: String(name),
    caption: raw.caption ?? raw.label ?? raw.title ?? String(name),
    type: raw.type ?? raw.dataType ?? raw.data_type ?? 'text'
  };
}

function markdownDocumentSubGridConfig(field={}) {
  return field?.edit?.subGrid ?? field?.edit?.subgrid ?? field?.subGrid ?? field?.subgrid ?? {};
}

function markdownDocumentSubGridColumns(field={}, rows=[]) {
  const cfg = markdownDocumentSubGridConfig(field);
  const configured = cfg.columns ?? cfg.itemFields ?? cfg.item_fields ?? field?.columns ?? field?.itemFields ?? field?.item_fields ?? [];
  const byName = new Map();
  if (Array.isArray(configured)) {
    configured.map(markdownNormalizeDocumentSubGridColumn).filter(Boolean).forEach(col => byName.set(col.field, col));
  }
  (rows ?? []).forEach(row => {
    if (!row || typeof row !== 'object' || Array.isArray(row)) return;
    Object.keys(row).forEach(key => {
      if (!byName.has(key)) byName.set(key, { field: key, caption: key, type: 'text' });
    });
  });
  if (!byName.size) byName.set('value', { field: 'value', caption: 'value', type: 'text' });
  return [...byName.values()];
}

function markdownAppendDocumentArrayValue(lines, field, rows, level=4) {
  const heading = `${'#'.repeat(Math.max(1, Math.min(6, level)))} ${markdownDocumentFieldCaption(field)}`;
  lines.push(heading);
  lines.push('');

  if (!Array.isArray(rows) || !rows.length) {
    lines.push('(空)');
    lines.push('');
    return;
  }

  const objectRows = rows.every(row => row && typeof row === 'object' && !Array.isArray(row));
  if (!objectRows) {
    rows.forEach(item => lines.push(`- ${markdownValueToText(item)}`));
    lines.push('');
    return;
  }

  const columns = markdownDocumentSubGridColumns(field, rows);
  lines.push(`件数: ${rows.length}`);
  lines.push('');
  lines.push(`| ${columns.map(col => markdownEscapeTableCell(col.caption ?? col.field, 80)).join(' | ')} |`);
  lines.push(`| ${columns.map(() => '---').join(' | ')} |`);
  rows.forEach(row => {
    lines.push(`| ${columns.map(col => markdownDocumentCellValue(getByPath(row, col.field), 420)).join(' | ')} |`);
  });
  lines.push('');
}

function markdownAppendDocumentComplexField(lines, field, value, level=4) {
  if (markdownValueIsEmpty(value)) return;
  if (Array.isArray(value)) {
    markdownAppendDocumentArrayValue(lines, field, value, level);
    return;
  }

  lines.push(`${'#'.repeat(Math.max(1, Math.min(6, level)))} ${markdownDocumentFieldCaption(field)}`);
  lines.push('');
  if (value && typeof value === 'object') {
    lines.push(markdownFence(markdownValueToText(value), 'json'));
  } else {
    lines.push(markdownValueToText(value));
  }
  lines.push('');
}

function markdownDocumentRowTitle(row, index, section={}, mode={}) {
  const headingMarkdownField = mode.headingMarkdownField ?? mode.heading_markdown_field;
  if (headingMarkdownField) {
    const line = getByPath(row, headingMarkdownField);
    if (!markdownValueIsEmpty(line)) return String(line).replace(/^#{1,6}\s*/, '').trim();
  }
  const headingField = mode.headingField ?? mode.heading_field;
  const title = headingField ? getByPath(row, headingField) : (getByPath(row, 'title') ?? getByPath(row, 'name'));
  const keyField = section.keyField ?? section.key_field;
  const key = keyField ? getByPath(row, keyField) : (getByPath(row, 'id') ?? getByPath(row, 'test_pattern_id') ?? getByPath(row, 'rule_id'));
  if (!markdownValueIsEmpty(key) && !markdownValueIsEmpty(title) && String(key) !== String(title)) return `${key} / ${title}`;
  if (!markdownValueIsEmpty(title)) return String(title);
  if (!markdownValueIsEmpty(key)) return String(key);
  return `Item ${index + 1}`;
}

function markdownAppendDocumentRow(lines, row, index, section={}, mode={}) {
  lines.push(`### ${markdownDocumentRowTitle(row, index, section, mode)}`);
  lines.push('');

  const fields = markdownDocumentFieldList(section, mode)
    .filter(field => !markdownValueIsEmpty(getByPath(row, field.field)));

  const scalarFields = fields.filter(field => markdownDocumentValueKind(getByPath(row, field.field)) === 'scalar');
  const complexFields = fields.filter(field => markdownDocumentValueKind(getByPath(row, field.field)) !== 'scalar');

  if (scalarFields.length) {
    lines.push('| 項目 | 値 |');
    lines.push('|---|---|');
    scalarFields.forEach(field => {
      const value = getByPath(row, field.field);
      lines.push(`| ${markdownEscapeTableCell(markdownDocumentFieldCaption(field), 120)} | ${markdownEscapeTableCell(markdownFormatFieldValue(value, field), 420)} |`);
    });
    lines.push('');
  }

  complexFields.forEach(field => {
    markdownAppendDocumentComplexField(lines, field, getByPath(row, field.field), 4);
  });
}

function markdownAppendDocumentFromViewSections(lines, mode={}) {
  const sections = markdownSections().filter(section => markdownShouldExportSection(section));
  sections.forEach(section => {
    if (section.type === 'form') {
      const base = getByPath(sourceData, section.dataPath || '$') ?? sourceData;
      const fields = markdownDocumentFieldList(section, mode)
        .filter(field => !markdownValueIsEmpty(getByPath(base, field.field)));
      if (!fields.length) return;
      lines.push(`## ${section.caption ?? section.id ?? '基本情報'}`);
      lines.push('');
      lines.push('| 項目 | 値 |');
      lines.push('|---|---|');
      fields.forEach(field => {
        const value = getByPath(base, field.field);
        lines.push(`| ${markdownEscapeTableCell(markdownDocumentFieldCaption(field), 120)} | ${markdownEscapeTableCell(markdownFormatFieldValue(value, field), 420)} |`);
      });
      lines.push('');
      return;
    }

    if (section.type !== 'grid') return;
    const rows = markdownSortRowsForMode(markdownRowsForSection(section), mode);
    lines.push(`## ${section.caption ?? section.id ?? '一覧'}`);
    lines.push('');
    lines.push(`件数: ${rows.length}`);
    lines.push('');
    if (!rows.length) return;
    rows.forEach((row, index) => markdownAppendDocumentRow(lines, row, index, section, mode));
  });
}

function buildDocumentRebuildMarkdown(mode={}) {
  if (!viewDef || !sourceData) throw new Error('Markdown出力するData/ViewDefが読み込まれていません');
  const titleField = mode.titleField ?? mode.title_field;
  const title = mode.title || (titleField ? getByPath(sourceData, titleField) : null) || sourceData?.title || markdownCurrentViewTitle();
  const bodyField = mode.bodyField ?? mode.body_field ?? 'body';
  const preambleField = mode.preambleField ?? mode.preamble_field ?? 'preamble';
  const lines = [];

  if (mode.includeTitle !== false && mode.include_title !== false) {
    lines.push(`# ${title}`);
    lines.push('');
  }

  if (mode.includePreamble !== false && mode.include_preamble !== false && preambleField) {
    const preamble = getByPath(sourceData, preambleField);
    if (!markdownValueIsEmpty(preamble)) {
      lines.push(String(preamble).trim());
      lines.push('');
    }
  }

  // v0.18.12-rework-document-markdown-viewdef-sections:
  // 文書Markdownのsource未指定時は $.rules 固定へ落とさず、ViewDef sections を読み直して
  // form/grid/subGrid(objectArray) を文書化する。これにより「タイトルだけ出力」を防ぐ。
  if (!markdownModeHasExplicitSource(mode) && markdownSections().some(s => s.type === 'grid' || s.type === 'form')) {
    markdownAppendDocumentFromViewSections(lines, mode);
    return lines.join('\n').replace(/\n{4,}/g, '\n\n\n').trimEnd() + '\n';
  }

  const rows = markdownSortRowsForMode(markdownSourceRowsForMode(mode), mode);
  const skipEmptyBody = Boolean(mode.skipEmptyBody ?? mode.suppressEmptyBody ?? mode.skip_empty_body ?? mode.suppress_empty_body);
  rows.forEach((row, index) => {
    const body = getByPath(row, bodyField);
    if (skipEmptyBody && markdownValueIsEmpty(body)) return;
    lines.push(markdownHeadingLineForRow(row, index, mode));
    lines.push('');
    if (!markdownValueIsEmpty(body)) {
      lines.push(String(body).trim());
      lines.push('');
    }
  });

  return lines.join('\n').replace(/\n{4,}/g, '\n\n\n').trimEnd() + '\n';
}

function buildDataMarkdown(modeId=null) {
  const mode = markdownExportModeById(modeId);
  const type = String(mode?.type ?? mode?.id ?? 'review_report').toLowerCase();
  switch (type) {
    case 'full_dump':
      return buildFullDumpMarkdown(mode);
    case 'document_sections':
    case 'document_rebuild':
      return buildDocumentRebuildMarkdown(mode);
    case 'review_report':
    default:
      return buildReviewReportMarkdown(mode);
  }
}

function markdownFileNameForMode(mode) {
  const configured = mode?.defaultFileName ?? mode?.fileName ?? mode?.filename;
  if (configured) return markdownNormalizePathName(configured).replace(/^data\/markdown\//, '');
  const base = markdownSafeSlug(markdownBaseNameWithoutExt(markdownCurrentDataName()), 'studio_data_export');
  const modeSuffix = markdownSafeSlug(mode?.id || mode?.type || 'markdown', 'markdown');
  return `00_Common/${base}_${modeSuffix}_${markdownNowStamp()}.md`;
}

async function exportMarkdown(modeId=null) {
  const selectedModeId = modeId || markdownSelectedExportModeId();
  const mode = markdownExportModeById(selectedModeId);
  const content = buildDataMarkdown(mode.id);
  const name = markdownFileNameForMode(mode);
  const result = await markdownSaveManagedFile(name, content, markdownCurrentDataName());
  const saved = result.saved || name;
  if (typeof setStatus === 'function') setStatus(`Markdown出力しました: ${saved} (${mode.caption || mode.id})`);
  if (!result.downloaded) markdownOpenViewer(saved);
  return result;
}
