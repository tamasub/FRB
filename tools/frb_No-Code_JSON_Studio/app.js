let viewDef = null;
let sourceData = null;
let currentRows = [];
let filteredRows = [];
let selectedIndex = -1;

const $ = (id) => document.getElementById(id);

function setStatus(msg) { $('status').textContent = msg; }

function updateFileLabels() {
  const def = $('defFile').files?.[0];
  const data = $('dataFile').files?.[0];
  const defName = $('defFileName');
  const dataName = $('dataFileName');
  if (defName) defName.textContent = def ? def.name : 'Drop or Select';
  if (dataName) dataName.textContent = data ? data.name : 'Drop or Select';
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

function mainView() { return viewDef.views?.[0] ?? viewDef; }
function headerDef() { return mainView().sections.find(s => s.type === 'form' && s.role !== 'detailOnly'); }
function gridDef() { return mainView().sections.find(s => s.type === 'grid'); }

function convertValue(type, value) {
  if (type === 'number') return value === '' ? null : Number(value);
  if (type === 'boolean') return value === 'true' || value === true;
  return value;
}

function formatValue(value) {
  if (value == null) return '';
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
    input.value = formatValue(value);
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
    input.value = (field.type === 'objectArray' || field.type === 'stringArray')
      ? (Array.isArray(value) ? `${value.length} items` : '')
      : (typeof value === 'object' && value !== null ? formatValue(value) : (value ?? ''));
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
}

function renderGrid() {
  const gd = gridDef();
  $('gridCaption').textContent = gd.caption ?? 'Grid';
  $('gridCount').textContent = `${filteredRows.length} / ${currentRows.length}件`;
  const table = $('dataGrid');
  table.innerHTML = '';
  const visibleFields = gd.fields.filter(f => f.grid?.visible !== false);
  const thead = document.createElement('thead');
  const trh = document.createElement('tr');
  visibleFields.forEach(f => {
    const th = document.createElement('th');
    th.textContent = f.caption ?? f.field;
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
    visibleFields.forEach(f => {
      const td = document.createElement('td');
      td.className = f.type ?? '';
      td.textContent = formatValue(getByPath(row, f.field));
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
  renderGrid();
}

function openDetail(index) {
  selectedIndex = index;
  const row = currentRows[index];
  const gd = gridDef();
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

setupPageDrop();

$('loadBtn').addEventListener('click', async () => {
  try {
    viewDef = await readJsonFile($('defFile'));
    sourceData = await readJsonFile($('dataFile'));
    renderHeader();
    renderSearch();
    loadRows();
    renderGrid();
    $('saveBtn').disabled = false;
    updateFileLabels();
    setStatus('読み込み完了');
  } catch (err) {
    console.error(err);
    setStatus('エラー: ' + err.message);
  }
});
$('searchBtn').addEventListener('click', applySearch);
$('clearSearchBtn').addEventListener('click', () => {
  [...$('searchForm').querySelectorAll('input, select, textarea')].forEach(i => i.value = '');
  filteredRows = currentRows.map((row, index) => ({row, index}));
  renderGrid();
});
$('applyDetailBtn').addEventListener('click', applyDetail);
$('saveBtn').addEventListener('click', saveAsJson);
