let viewDef = null;
let sourceData = null;
let currentRows = [];
let filteredRows = [];
let selectedIndex = -1;
let sortState = { field: null, direction: null };
let copiedRow = null;
let currentDataApiUrl = null; // /api/data/xxx.json のときだけ上書き保存可能
let lastLoadedDefName = null;
let serverDefNames = [];
let serverDataNames = [];

const $ = (id) => document.getElementById(id);

function setStatus(msg) { $('status').textContent = msg; }

function updateFileLabels() {
  const def = $('defFile').files?.[0];
  const data = $('dataFile').files?.[0];
  const defName = $('defFileName');
  const dataName = $('dataFileName');
  if (defName) defName.textContent = def ? def.name : 'Drop';
  if (dataName) dataName.textContent = data ? data.name : 'Drop';
}

function setupDropFileBox(box) {
  const input = $(box.dataset.input);
  if (!input) return;
  ['dragenter', 'dragover'].forEach(type => {
    box.addEventListener(type, (e) => {
      e.preventDefault();
      e.stopPropagation();
      box.classList.add('dragover');
    });
  });
  ['dragleave', 'drop'].forEach(type => {
    box.addEventListener(type, (e) => {
      e.preventDefault();
      e.stopPropagation();
      box.classList.remove('dragover');
    });
  });
  box.addEventListener('drop', (e) => {
    const file = e.dataTransfer?.files?.[0];
    if (!file) return;
    const dt = new DataTransfer();
    dt.items.add(file);
    input.files = dt.files;
    updateFileLabels();
    setStatus(`${file.name} を受け取りました`);
  });
  input.addEventListener('change', updateFileLabels);
}


function safeJsonFileName(name) {
  const n = String(name ?? '').trim();
  if (!/^[^\\/]+\.json$/i.test(n)) return null;
  if (n.includes('..')) return null;
  return n;
}

function setDatalist(id, names) {
  const dl = $(id);
  if (!dl) return;
  dl.innerHTML = '';
  names.forEach(name => {
    const opt = document.createElement('option');
    opt.value = name;
    dl.appendChild(opt);
  });
}

async function refreshServerLists() {
  try {
    const [defs, data] = await Promise.all([
      fetchJson('/api/defs'),
      fetchJson('/api/data')
    ]);
    serverDefNames = Array.isArray(defs) ? defs : (defs.files ?? []);
    serverDataNames = Array.isArray(data) ? data : (data.files ?? []);
    setDatalist('defNameList', serverDefNames);
    setDatalist('dataNameList', serverDataNames);
    setStatus(`一覧を更新しました: defs ${serverDefNames.length}件 / data ${serverDataNames.length}件`);
  } catch (err) {
    console.warn(err);
    setStatus('一覧API未使用: DropまたはURL指定で読み込めます');
  }
}

function selectedDefName() {
  return safeJsonFileName($('defNameInput')?.value) || null;
}

function selectedDataName() {
  return safeJsonFileName($('dataNameInput')?.value) || null;
}

function getDataViewDefName(dataObj) {
  return safeJsonFileName(dataObj?.view_def || dataObj?.viewDef || dataObj?.view_definition || dataObj?.viewDefinition);
}

function ensureViewDefNameInData(dataObj, defName) {
  if (!dataObj || typeof dataObj !== 'object' || Array.isArray(dataObj)) return;
  const n = safeJsonFileName(defName);
  if (n) dataObj.view_def = n;
}

async function loadFromServerNames(defName, dataName) {
  // dataコンボから読み込む場合も、対象JSON内の view_def を優先する。
  // これにより「対象JSONだけ選ぶ → 読み込み」で画面定義を自動決定できる。
  defName = safeJsonFileName(defName);
  dataName = safeJsonFileName(dataName);
  if (!dataName) throw new Error('対象JSONを選択してください');

  $('dataNameInput').value = dataName;
  $('defFileName').textContent = 'Drop';
  $('dataFileName').textContent = 'Drop';
  setStatus('API管理ファイルを読み込み中...');

  const dataObj = await fetchJson(`/api/data/${encodeURIComponent(dataName)}`);

  const embeddedDefName = getDataViewDefName(dataObj);
  if (embeddedDefName) {
    defName = embeddedDefName;
    $('defNameInput').value = defName;
  } else {
    if (!defName) throw new Error('対象JSONに view_def がありません。画面定義JSONを選択してください');
    $('defNameInput').value = defName;
  }

  const defObj = await fetchJson(`/api/defs/${encodeURIComponent(defName)}`);
  ensureViewDefNameInData(dataObj, defName);
  lastLoadedDefName = defName;
  loadFromObjects(defObj, dataObj, `API管理ファイルを読み込みました: ${dataName}`, `/api/data/${encodeURIComponent(dataName)}`);
}

async function registerDroppedData(fileName, dataObj, defName) {
  const name = safeJsonFileName(fileName);
  if (!name) throw new Error('JSONファイル名が不正です');
  ensureViewDefNameInData(dataObj, defName);

  const res = await fetch('/api/data/drop', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name, json: dataObj })
  });
  if (!res.ok) {
    const text = await res.text().catch(() => '');
    throw new Error(`管理対象へのコピーに失敗しました (${res.status}) ${text}`);
  }
  await refreshServerLists();
  $('dataNameInput').value = name;
  return `/api/data/${encodeURIComponent(name)}`;
}

async function loadFromDroppedFilesOrServer() {
  const defFile = $('defFile')?.files?.[0] ?? null;
  const dataFile = $('dataFile')?.files?.[0] ?? null;
  const defNameFromInput = selectedDefName();
  const dataNameFromInput = selectedDataName();

  if (!defFile && !dataFile && dataNameFromInput) {
    await loadFromServerNames(defNameFromInput, dataNameFromInput);
    return;
  }

  let dataObj = null;
  let droppedDataName = null;
  if (dataFile) {
    droppedDataName = dataFile.name;
    dataObj = JSON.parse(await dataFile.text());
  }

  let defName = defNameFromInput;
  if (dataObj && getDataViewDefName(dataObj)) {
    defName = getDataViewDefName(dataObj);
    $('defNameInput').value = defName;
  }

  let defObj = null;
  if (defFile) {
    defObj = JSON.parse(await defFile.text());
    defName = safeJsonFileName(defFile.name) || defName || 'dropped_view_def.json';
    $('defNameInput').value = defName;
  } else if (defName) {
    defObj = await fetchJson(`/api/defs/${encodeURIComponent(defName)}`);
  } else {
    throw new Error('画面定義JSONをDropするか、defsから選択してください');
  }

  if (!dataObj) {
    if (!dataNameFromInput) throw new Error('対象JSONをDropするか、dataから選択してください');
    await loadFromServerNames(defName, dataNameFromInput);
    return;
  }

  ensureViewDefNameInData(dataObj, defName);
  lastLoadedDefName = defName;

  let dataApiUrl = null;
  if (confirm(`このファイルをFRB Studioで管理しますか？\n\n${droppedDataName}\n\n[OK] dataフォルダへコピーして上書き保存可能にする\n[キャンセル] 今回は見るだけ（保存は別名保存）`)) {
    dataApiUrl = await registerDroppedData(droppedDataName, dataObj, defName);
    loadFromObjects(defObj, dataObj, `管理対象にコピーして読み込みました: ${droppedDataName}`, dataApiUrl);
  } else {
    $('dataNameInput').value = '';
    loadFromObjects(defObj, dataObj, `見るだけで読み込みました: ${droppedDataName}`, null);
  }
}

function setupPageDrop() {
  document.querySelectorAll('.drop-file-box').forEach(setupDropFileBox);
  document.addEventListener('dragover', (e) => e.preventDefault());
  document.addEventListener('drop', (e) => e.preventDefault());
}

async function readJsonFile(input) {
  const file = input.files?.[0];
  if (!file) throw new Error('ファイルが選択されていません');
  const text = await file.text();
  return JSON.parse(text);
}

function getByPath(obj, path) {
  if (!path || path === '$') return obj;
  const normalized = path.startsWith('$.') ? path.slice(2) : path;
  return normalized.split('.').reduce((cur, key) => cur == null ? undefined : cur[key], obj);
}

function setByPath(obj, path, value) {
  const normalized = path.startsWith('$.') ? path.slice(2) : path;
  const parts = normalized.split('.');
  let cur = obj;
  for (let i = 0; i < parts.length - 1; i++) {
    const key = parts[i];
    if (cur[key] == null || typeof cur[key] !== 'object') cur[key] = {};
    cur = cur[key];
  }
  cur[parts[parts.length - 1]] = value;
}


function cloneData(value) {
  if (value == null) return value;
  return typeof structuredClone === 'function' ? structuredClone(value) : JSON.parse(JSON.stringify(value));
}

function getFieldValue(row, field) {
  return getByPath(row, field.field);
}

function compareValues(a, b, field) {
  if (a == null || a === '') return (b == null || b === '') ? 0 : 1;
  if (b == null || b === '') return -1;
  if (field?.type === 'number') {
    const na = Number(a);
    const nb = Number(b);
    if (Number.isFinite(na) && Number.isFinite(nb)) return na - nb;
  }
  if (field?.type === 'boolean') return String(a).localeCompare(String(b));
  return String(a).localeCompare(String(b), 'ja', {numeric: true, sensitivity: 'base'});
}

function applySortToFilteredRows() {
  if (!sortState.field || !sortState.direction) return;
  const gd = gridDef();
  const field = gd.fields.find(f => f.field === sortState.field);
  if (!field) return;
  const dir = sortState.direction === 'asc' ? 1 : -1;
  filteredRows.sort((x, y) => {
    const c = compareValues(getFieldValue(x.row, field), getFieldValue(y.row, field), field);
    return c === 0 ? x.index - y.index : c * dir;
  });
}

function cycleSort(fieldName) {
  if (sortState.field !== fieldName) {
    sortState = {field: fieldName, direction: 'asc'};
  } else if (sortState.direction === 'asc') {
    sortState.direction = 'desc';
  } else {
    sortState = {field: null, direction: null};
  }
  applySortToFilteredRows();
  renderGrid();
}

function selectedDisplayPosition() {
  if (selectedIndex < 0) return '-';
  const pos = filteredRows.findIndex(x => x.index === selectedIndex);
  return pos >= 0 ? String(pos + 1) : '範囲外';
}

function mainView() { return viewDef.views?.[0] ?? viewDef; }
function headerDef() { return mainView().sections.find(s => s.type === 'form' && s.role !== 'detailOnly'); }
function gridDef() { return mainView().sections.find(s => s.type === 'grid'); }

function convertValue(type, value) {
  if (type === 'number') return value === '' ? null : Number(value);
  if (type === 'boolean') return value === 'true' || value === true;
  return value;
}


function formatNumber(value, pattern) {
  if (value == null || value === '') return '';
  const n = Number(value);
  if (!Number.isFinite(n)) return String(value);
  if (!pattern) return String(value);
  const m = String(pattern).match(/\.([0#]+)/);
  if (!m) return String(value);
  return n.toFixed(m[1].length);
}

function formatValue(value, field=null) {
  if (value == null) return '';
  if (field?.type === 'number') return formatNumber(value, field.format ?? field.grid?.format ?? field.edit?.format);
  if (typeof value === 'object') return JSON.stringify(value);
  return String(value);
}


function createInput(field, value, prefix, readonlyOverride=false) {
  const readonly = readonlyOverride || field.readonly || field.edit?.readonly;
  const wrap = document.createElement('div');
  wrap.className = 'field' + (readonly ? ' readonly' : '');
  const label = document.createElement('label');
  label.textContent = field.caption ?? field.field;
  wrap.appendChild(label);

  let input;
  if (field.type === 'select') {
    input = document.createElement('select');
    const blank = document.createElement('option');
    blank.value = '';
    blank.textContent = '';
    input.appendChild(blank);
    (field.options ?? []).forEach(opt => {
      const o = document.createElement('option');
      o.value = opt;
      o.textContent = opt;
      input.appendChild(o);
    });
    input.value = value ?? '';
  } else if (field.type === 'textarea') {
    input = document.createElement('textarea');
    input.value = formatValue(value, field);
    if (field.edit?.height) input.style.minHeight = field.edit.height + 'px';
  } else if (field.type === 'boolean') {
    input = document.createElement('select');
    ['', 'true', 'false'].forEach(v => {
      const o = document.createElement('option');
      o.value = v; o.textContent = v;
      input.appendChild(o);
    });
    input.value = value === true ? 'true' : value === false ? 'false' : '';
  } else {
    input = document.createElement('input');
    input.type = field.type === 'number' ? 'number' : field.type === 'datetime' ? 'text' : 'text';
    if (field.type === 'number') {
      const step = field.edit?.step ?? field.step;
      const min = field.edit?.min ?? field.min;
      const max = field.edit?.max ?? field.max;
      if (step != null) input.step = String(step);
      if (min != null) input.min = String(min);
      if (max != null) input.max = String(max);
    }
    input.value = (field.type === 'objectArray' || field.type === 'stringArray')
      ? (Array.isArray(value) ? `${value.length} items` : '')
      : (typeof value === 'object' && value !== null ? formatValue(value, field) : (value ?? ''));
  }
  input.dataset.field = field.field;
  input.dataset.type = field.type ?? 'text';
  input.dataset.prefix = prefix;
  if (readonly) input.disabled = true;
  wrap.appendChild(input);
  return wrap;
}

function renderHeader() {
  const def = headerDef();
  if (!def) return;
  $('headerCaption').textContent = def.caption ?? 'Header';
  const form = $('headerForm');
  form.innerHTML = '';
  def.fields.forEach(field => {
    form.appendChild(createInput(field, getByPath(sourceData, (def.dataPath === '$' ? '$.' : def.dataPath + '.') + field.field), 'header'));
  });
  $('headerSection').classList.remove('hidden');
}

function renderSearch() {
  const gd = gridDef();
  const form = $('searchForm');
  form.innerHTML = '';
  gd.fields.filter(f => f.search?.visible).forEach(field => {
    const searchField = {...field, readonly:false, edit:{readonly:false}};
    if (field.type === 'number') {
      form.appendChild(createInput({...searchField, caption:(field.caption ?? field.field) + ' >='}, '', 'search'));
    } else {
      form.appendChild(createInput(searchField, '', 'search'));
    }
  });
  $('searchSection').classList.remove('hidden');
}

function loadRows() {
  const gd = gridDef();
  currentRows = getByPath(sourceData, gd.dataPath);
  if (!Array.isArray(currentRows)) throw new Error('mainGrid dataPath が Array ではありません: ' + gd.dataPath);
  filteredRows = currentRows.map((row, index) => ({row, index}));
  applySortToFilteredRows();
}

function renderGrid() {
  const gd = gridDef();
  $('gridCaption').textContent = gd.caption ?? 'Grid';
  $('gridCount').textContent = `${selectedDisplayPosition()} / ${currentRows.length}行目　表示 ${filteredRows.length} / 全 ${currentRows.length}件`;
  const table = $('dataGrid');
  table.innerHTML = '';
  const visibleFields = gd.fields.filter(f => f.grid?.visible !== false);
  const thead = document.createElement('thead');
  const trh = document.createElement('tr');
  visibleFields.forEach(f => {
    const th = document.createElement('th');
    th.classList.add('sortable');
    th.title = 'クリックでソート';
    const label = document.createElement('span');
    label.textContent = f.caption ?? f.field;
    th.appendChild(label);
    const mark = document.createElement('span');
    mark.className = 'sort-mark';
    mark.textContent = sortState.field === f.field ? (sortState.direction === 'asc' ? '▲' : '▼') : '';
    th.appendChild(mark);
    th.addEventListener('click', () => cycleSort(f.field));
    if (f.grid?.width) th.style.width = f.grid.width + 'px';
    trh.appendChild(th);
  });
  thead.appendChild(trh);
  table.appendChild(thead);
  const tbody = document.createElement('tbody');
  filteredRows.forEach(({row, index}) => {
    const tr = document.createElement('tr');
    if (index === selectedIndex) tr.classList.add('selected');
    tr.addEventListener('click', () => { selectedIndex = index; renderGrid(); });
    tr.addEventListener('dblclick', () => openDetail(index));
    tr.addEventListener('contextmenu', (e) => {
      e.preventDefault();
      selectedIndex = index;
      renderGrid();
      showRowContextMenu(e.clientX, e.clientY, index);
    });
    visibleFields.forEach(f => {
      const td = document.createElement('td');
      td.className = f.type ?? '';
      td.textContent = formatValue(getByPath(row, f.field), f);
      if (f.grid?.width) td.style.maxWidth = f.grid.width + 'px';
      tr.appendChild(td);
    });
    tbody.appendChild(tr);
  });
  table.appendChild(tbody);
  $('gridSection').classList.remove('hidden');
}


function applySearch() {
  const gd = gridDef();
  const inputs = [...$('searchForm').querySelectorAll('input, select, textarea')];
  filteredRows = currentRows.map((row, index) => ({row, index})).filter(({row}) => {
    return inputs.every(inp => {
      const raw = inp.value;
      if (raw === '') return true;
      const field = gd.fields.find(f => f.field === inp.dataset.field);
      const val = getByPath(row, field.field);
      const op = field.search?.operator ?? (field.type === 'number' ? 'gte' : 'contains');
      if (field.type === 'number') {
        const n = Number(raw);
        if (op === 'gte') return Number(val) >= n;
        if (op === 'lte') return Number(val) <= n;
        return Number(val) === n;
      }
      if (field.type === 'boolean') return String(val) === raw;
      if (op === 'equals') return String(val ?? '') === raw;
      return String(val ?? '').toLowerCase().includes(raw.toLowerCase());
    });
  });
  applySortToFilteredRows();
  renderGrid();
}


function cloneDefaultValue(value) {
  if (Array.isArray(value)) return value.map(cloneDefaultValue);
  if (value && typeof value === 'object') return typeof structuredClone === 'function' ? structuredClone(value) : JSON.parse(JSON.stringify(value));
  return value;
}

function defaultForField(field) {
  if ('defaultValue' in field) return cloneDefaultValue(field.defaultValue);
  if (field.type === 'number') return 0;
  if (field.type === 'boolean') return false;
  if (field.type === 'objectArray' || field.type === 'stringArray') return [];
  if (field.type === 'select') return field.options?.[0] ?? '';
  return '';
}

function createDefaultRow() {
  const gd = gridDef();
  const row = {};
  gd.fields.forEach(field => {
    if (field.create?.include === false) return;
    setByPath(row, field.field, defaultForField(field));
  });
  return row;
}

function addGridRow() {
  if (!Array.isArray(currentRows)) return;
  applyHeaderEdits();
  const row = createDefaultRow();
  currentRows.push(row);
  selectedIndex = currentRows.length - 1;
  applySearch();
  setStatus('1行追加しました');
  openDetail(selectedIndex);
}

function deleteSelectedRow() {
  if (!Array.isArray(currentRows) || selectedIndex < 0) {
    setStatus('削除する行を選択してください');
    return;
  }
  if (!confirm(`選択中の1行を削除します。よろしいですか？\nindex: ${selectedIndex}`)) return;
  currentRows.splice(selectedIndex, 1);
  selectedIndex = -1;
  applySearch();
  setStatus('1行削除しました');
}


function copyRow(index) {
  if (!Array.isArray(currentRows) || index < 0) return;
  copiedRow = cloneData(currentRows[index]);
  setStatus(`行をコピーしました: ${index}`);
}

function pasteCopiedRowToForm() {
  if (!copiedRow) {
    setStatus('コピー済み行がありません');
    return;
  }
  const gd = gridDef();
  [...$('detailForm').querySelectorAll('input, select, textarea')].forEach(inp => {
    const field = gd.fields.find(f => f.field === inp.dataset.field);
    if (!field || field.edit?.readonly || field.readonly || inp.disabled) return;
    const value = getByPath(copiedRow, field.field);
    inp.value = value == null ? '' : value;
  });
  setStatus('コピー行の値を詳細ダイアログへ貼り付けました');
}

function addRowFromCopiedRow() {
  if (!copiedRow) {
    setStatus('コピー済み行がありません');
    return;
  }
  applyHeaderEdits();
  const row = cloneData(copiedRow);
  currentRows.push(row);
  selectedIndex = currentRows.length - 1;
  applySearch();
  setStatus('コピー行から1行追加しました');
  openDetail(selectedIndex);
}

function hideRowContextMenu() {
  const menu = $('rowContextMenu');
  if (menu) menu.classList.add('hidden');
}

function showRowContextMenu(x, y, index) {
  let menu = $('rowContextMenu');
  if (!menu) return;
  menu.innerHTML = '';
  const copyBtn = document.createElement('button');
  copyBtn.textContent = 'この行をコピー';
  copyBtn.addEventListener('click', () => { copyRow(index); hideRowContextMenu(); });
  menu.appendChild(copyBtn);

  const addBtn = document.createElement('button');
  addBtn.textContent = 'コピー行から新規追加';
  addBtn.disabled = !copiedRow;
  addBtn.addEventListener('click', () => { addRowFromCopiedRow(); hideRowContextMenu(); });
  menu.appendChild(addBtn);

  menu.style.left = x + 'px';
  menu.style.top = y + 'px';
  menu.classList.remove('hidden');
}

document.addEventListener('click', hideRowContextMenu);
document.addEventListener('keydown', (e) => { if (e.key === 'Escape') hideRowContextMenu(); });

function openDetail(index) {
  selectedIndex = index;
  const row = currentRows[index];
  const gd = gridDef();
  const pasteBtn = $('pasteCopiedBtn');
  if (pasteBtn) pasteBtn.disabled = !copiedRow;
  const form = $('detailForm');
  form.innerHTML = '';
  gd.fields.filter(f => f.edit?.visible !== false).forEach(field => {
    form.appendChild(createInput(field, getByPath(row, field.field), 'detail'));
  });
  renderChildArea(row, gd);
  $('detailDialog').showModal();
}

function renderChildArea(row, gd) {
  const area = $('childArea');
  area.innerHTML = '';
  gd.fields.filter(f => f.type === 'objectArray' || f.type === 'stringArray').forEach(field => {
    const data = getByPath(row, field.field);
    if (!Array.isArray(data)) return;
    const card = document.createElement('div');
    card.className = 'child-card';
    const title = document.createElement('h3');
    title.textContent = field.caption ?? field.field;
    card.appendChild(title);
    const wrap = document.createElement('div');
    wrap.className = 'child-table-wrap';
    const table = document.createElement('table');
    if (field.type === 'stringArray') {
      table.innerHTML = '<thead><tr><th>#</th><th>value</th></tr></thead>';
      const tb = document.createElement('tbody');
      data.forEach((v, i) => {
        const tr = document.createElement('tr');
        tr.innerHTML = `<td>${i+1}</td><td>${formatValue(v)}</td>`;
        tb.appendChild(tr);
      });
      table.appendChild(tb);
    } else {
      const keys = [...new Set(data.flatMap(o => Object.keys(o ?? {})))];
      const thead = document.createElement('thead');
      const trh = document.createElement('tr');
      keys.forEach(k => { const th = document.createElement('th'); th.textContent = k; trh.appendChild(th); });
      thead.appendChild(trh); table.appendChild(thead);
      const tb = document.createElement('tbody');
      data.forEach(o => {
        const tr = document.createElement('tr');
        keys.forEach(k => { const td = document.createElement('td'); td.textContent = formatValue(o?.[k]); tr.appendChild(td); });
        tb.appendChild(tr);
      });
      table.appendChild(tb);
    }
    wrap.appendChild(table); card.appendChild(wrap); area.appendChild(card);
  });
}

function applyDetail(e) {
  e.preventDefault();
  if (selectedIndex < 0) return;
  const row = currentRows[selectedIndex];
  const gd = gridDef();
  [...$('detailForm').querySelectorAll('input, select, textarea')].forEach(inp => {
    const field = gd.fields.find(f => f.field === inp.dataset.field);
    if (!field || field.edit?.readonly || field.readonly || inp.disabled) return;
    setByPath(row, field.field, convertValue(field.type, inp.value));
  });
  renderGrid();
  $('detailDialog').close();
}

function applyHeaderEdits() {
  const def = headerDef();
  if (!def) return;
  [...$('headerForm').querySelectorAll('input, select, textarea')].forEach(inp => {
    const field = def.fields.find(f => f.field === inp.dataset.field);
    if (!field || field.edit?.readonly || field.readonly || inp.disabled) return;
    const fullPath = (def.dataPath === '$' ? '$.' : def.dataPath + '.') + field.field;
    setByPath(sourceData, fullPath, convertValue(field.type, inp.value));
  });
}

function saveAsJson() {
  applyHeaderEdits();
  const blob = new Blob([JSON.stringify(sourceData, null, 2)], {type: 'application/json'});
  const a = document.createElement('a');
  const ts = new Date().toISOString().replace(/[:.]/g, '-');
  a.href = URL.createObjectURL(blob);
  a.download = `json_master_editor_saved_${ts}.json`;
  a.click();
  URL.revokeObjectURL(a.href);
}

function normalizeApiDataUrl(url) {
  if (!url) return null;
  try {
    const u = new URL(url, location.href);
    if (u.origin !== location.origin) return null;
    const m = u.pathname.match(/^\/api\/data\/([^\/]+\.json)$/i);
    return m ? u.pathname : null;
  } catch {
    return null;
  }
}

async function saveOverwriteJson() {
  applyHeaderEdits();
  ensureViewDefNameInData(sourceData, lastLoadedDefName || selectedDefName());

  if (!currentDataApiUrl) {
    setStatus('API読み込みではないため、別名保存します（上書き保存するには /api/data/xxx.json で読み込んでください）');
    saveAsJson();
    return;
  }

  const res = await fetch(currentDataApiUrl, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(sourceData)
  });

  if (!res.ok) {
    const text = await res.text().catch(() => '');
    throw new Error(`保存に失敗しました (${res.status}) ${text}`);
  }

  setStatus(`上書き保存しました: ${currentDataApiUrl}`);
}

setupPageDrop();

function loadFromObjects(defObj, dataObj, label='読み込み完了', dataApiUrl=null) {
  viewDef = defObj;
  sourceData = dataObj;
  selectedIndex = -1;
  sortState = { field: null, direction: null };
  copiedRow = null;
  currentDataApiUrl = dataApiUrl;
  if (lastLoadedDefName && $('defNameInput')) $('defNameInput').value = lastLoadedDefName;
  renderHeader();
  renderSearch();
  loadRows();
  renderGrid();
  $('saveBtn').disabled = false;
  $('saveBtn').textContent = currentDataApiUrl ? '上書き保存' : '別名保存';
  $('addRowBtn').disabled = false;
  $('deleteRowBtn').disabled = false;
  updateFileLabels();
  setStatus(label);
}

async function loadFromFiles() {
  await loadFromDroppedFilesOrServer();
}

async function fetchJson(url) {
  const res = await fetch(url, {cache: 'no-store'});
  if (!res.ok) throw new Error(`${url} の読み込みに失敗しました (${res.status})`);
  return res.json();
}

async function autoLoadFromQuery() {
  const params = new URLSearchParams(location.search);
  const viewUrl = params.get('view') || params.get('def');
  const dataUrl = params.get('data');
  if (!viewUrl || !dataUrl) return;
  try {
    $('defFileName').textContent = viewUrl;
    $('dataFileName').textContent = dataUrl;
    setStatus('URLパラメータから読み込み中...');
    const [defObj, dataObj] = await Promise.all([fetchJson(viewUrl), fetchJson(dataUrl)]);
    const normalizedDefName = new URL(viewUrl, location.href).pathname.split('/').pop();
    lastLoadedDefName = safeJsonFileName(normalizedDefName) || getDataViewDefName(dataObj) || null;
    if (lastLoadedDefName && $('defNameInput')) $('defNameInput').value = lastLoadedDefName;
    const normalizedDataName = new URL(dataUrl, location.href).pathname.split('/').pop();
    if (safeJsonFileName(normalizedDataName) && $('dataNameInput')) $('dataNameInput').value = normalizedDataName;
    ensureViewDefNameInData(dataObj, lastLoadedDefName);
    loadFromObjects(defObj, dataObj, 'URLパラメータから読み込み完了', normalizeApiDataUrl(dataUrl));
  } catch (err) {
    console.error(err);
    setStatus('URL読込エラー: ' + err.message + '（file://直開きの場合はローカルサーバ起動が必要な場合があります）');
  }
}

$('loadBtn').addEventListener('click', async () => {
  try {
    await loadFromFiles();
  } catch (err) {
    console.error(err);
    setStatus('エラー: ' + err.message);
  }
});
$('searchBtn').addEventListener('click', applySearch);
$('addRowBtn').addEventListener('click', addGridRow);
$('deleteRowBtn').addEventListener('click', deleteSelectedRow);
$('clearSearchBtn').addEventListener('click', () => {
  [...$('searchForm').querySelectorAll('input, select, textarea')].forEach(i => i.value = '');
  filteredRows = currentRows.map((row, index) => ({row, index}));
  applySortToFilteredRows();
  renderGrid();
});
$('applyDetailBtn').addEventListener('click', applyDetail);
$('pasteCopiedBtn').addEventListener('click', pasteCopiedRowToForm);
$('saveBtn').addEventListener('click', async () => {
  try {
    await saveOverwriteJson();
  } catch (err) {
    console.error(err);
    setStatus('保存エラー: ' + err.message);
  }
});

refreshServerLists().finally(autoLoadFromQuery);
