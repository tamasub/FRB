// v0.17.1-rule-review-markdown-export-action
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
  const formSections = markdownSections().filter(s => s.type === 'form' && (s.role ?? '') !== 'detailOnly');
  formSections.forEach(section => {
    const base = getByPath(sourceData, section.dataPath || '$') ?? sourceData;
    const fields = Array.isArray(section.fields) ? section.fields : [];
    fields.forEach(field => {
      if (!field?.field) return;
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
  return (section?.fields ?? []).filter(f => f?.field && f.grid?.visible !== false);
}

function markdownRowsForSection(section) {
  if (section === (typeof gridDef === 'function' ? gridDef() : null) && Array.isArray(filteredRows) && filteredRows.length) {
    return filteredRows.map(x => x.row);
  }
  const rows = getByPath(sourceData, section.dataPath);
  return Array.isArray(rows) ? rows : [];
}

function markdownGridTable(section) {
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
  const rows = markdownRowsForSection(section);
  if (!rows.length) return [];
  const fields = Array.isArray(section.fields) ? section.fields : [];
  const preferred = ['summary', 'body', 'ceremony_phrase', 'user_comment', 'ai_response', 'user_reply', 'ai_followup_response', 'decision_log', 'change_history', 'notes'];
  const preferredFields = preferred.map(name => fields.find(f => f.field === name) ?? { field: name, caption: name }).filter(f => rows.some(row => !markdownValueIsEmpty(getByPath(row, f.field))));

  const lines = [];
  lines.push(`## ${section.caption ?? section.id ?? '詳細'} 詳細`);
  lines.push('');
  rows.forEach((row, index) => {
    lines.push(`### ${markdownRuleTitle(row, index, section)}`);
    lines.push('');

    const meta = ['rule_id', 'category', 'priority', 'review_status', 'verification_status', 'approval_decision', 'introduced_in']
      .map(name => ({ name, field: fields.find(f => f.field === name) ?? { field: name, caption: name } }))
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

function buildDataMarkdown() {
  if (!viewDef || !sourceData) throw new Error('Markdown出力するData/ViewDefが読み込まれていません');

  const title = markdownCurrentViewTitle();
  const dataName = markdownCurrentDataName();
  const lines = [];
  lines.push(`# ${title}`);
  lines.push('');
  lines.push('<!-- Generated by FRB Studio / JSON Object Studio -->');
  lines.push('');
  lines.push(`- Data: \`${dataName}\``);
  if (typeof lastLoadedDefName !== 'undefined' && lastLoadedDefName) lines.push(`- ViewDef: \`${lastLoadedDefName}\``);
  lines.push(`- Exported At: ${new Date().toISOString()}`);
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

async function exportMarkdown() {
  const content = buildDataMarkdown();
  const base = markdownSafeSlug(markdownBaseNameWithoutExt(markdownCurrentDataName()), 'studio_data_export');
  const name = `00_Common/${base}_${markdownNowStamp()}.md`;
  const result = await markdownSaveManagedFile(name, content, markdownCurrentDataName());
  const saved = result.saved || name;
  if (typeof setStatus === 'function') setStatus(`Markdown出力しました: ${saved}`);
  if (!result.downloaded) markdownOpenViewer(saved);
  return result;
}
