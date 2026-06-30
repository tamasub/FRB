// v0.17.1-rule-review-markdown-export-action
// Lightweight helpers for Markdown export scripts.
// This file intentionally keeps the contract small: Data/ViewDef exporters expose
// exportMarkdown() and exportViewDefMarkdown() as global functions for both
// header buttons and toolbar.executeButton ActionRegistry.

function markdownNowStamp() {
  const d = new Date();
  const pad = (n) => String(n).padStart(2, '0');
  return `${d.getFullYear()}${pad(d.getMonth() + 1)}${pad(d.getDate())}_${pad(d.getHours())}${pad(d.getMinutes())}${pad(d.getSeconds())}`;
}

function markdownNormalizePathName(value) {
  return String(value ?? '')
    .trim()
    .replace(/\\/g, '/')
    .replace(/^\/+/, '')
    .replace(/[?#].*$/, '');
}

function markdownBaseName(value) {
  const text = markdownNormalizePathName(value);
  return text.split('/').filter(Boolean).pop() || '';
}

function markdownBaseNameWithoutExt(value) {
  return markdownBaseName(value).replace(/\.[^.]+$/, '');
}

function markdownSafeSlug(value, fallback='studio_export') {
  const raw = String(value ?? '').trim();
  const ascii = raw
    .normalize('NFKC')
    .replace(/\.[^.]+$/, '')
    .replace(/[^A-Za-z0-9._-]+/g, '_')
    .replace(/^_+|_+$/g, '')
    .replace(/_{2,}/g, '_');
  return ascii || fallback;
}

function markdownEscapeTableCell(value, maxLen=160) {
  let text = String(value ?? '');
  if (text.length > maxLen) text = `${text.slice(0, maxLen)}…`;
  return text
    .replace(/\r?\n/g, '<br>')
    .replace(/\|/g, '\\|');
}

function markdownFence(value, lang='') {
  const text = String(value ?? '');
  const fence = text.includes('```') ? '````' : '```';
  return `${fence}${lang}\n${text}\n${fence}`;
}

function markdownValueToText(value) {
  if (value == null) return '';
  if (typeof value === 'string') return value;
  if (typeof value === 'number' || typeof value === 'boolean') return String(value);
  try { return JSON.stringify(value, null, 2); }
  catch { return String(value); }
}

function markdownValueIsEmpty(value) {
  if (value == null) return true;
  if (typeof value === 'string') return value.trim() === '';
  if (Array.isArray(value)) return value.length === 0;
  if (typeof value === 'object') return Object.keys(value).length === 0;
  return false;
}

function markdownDownloadFile(fileName, content, mime='text/markdown;charset=utf-8') {
  const blob = new Blob([content], { type: mime });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = fileName;
  document.body.appendChild(a);
  a.click();
  a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

async function markdownSaveManagedFile(name, content, sourceName='') {
  const cleanName = markdownNormalizePathName(name);
  if (!cleanName || !cleanName.toLowerCase().endsWith('.md')) {
    throw new Error('Markdown保存ファイル名が不正です');
  }

  if (typeof isStaticHostingMode === 'function' && isStaticHostingMode()) {
    markdownDownloadFile(markdownBaseName(cleanName), content);
    return { saved: markdownBaseName(cleanName), downloaded: true };
  }

  const url = `/api/markdown/${cleanName.split('/').map(encodeURIComponent).join('/')}`;
  const res = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ Name: cleanName, Content: content, SourceName: sourceName })
  });
  if (!res.ok) {
    const text = await res.text().catch(() => '');
    throw new Error(text || `Markdown保存に失敗しました: ${res.status}`);
  }
  return await res.json();
}

function markdownOpenViewer(savedName) {
  if (!savedName) return;
  const path = markdownNormalizePathName(savedName);
  const param = path.split('/').map(encodeURIComponent).join('/');
  window.open(`mdViewer.html?file=${param}`, '_blank');
}
