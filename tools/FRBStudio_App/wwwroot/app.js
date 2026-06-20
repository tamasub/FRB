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
let detailMode = 'edit'; // edit | new
let draftRow = null;

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
  input.addEventListener('change', () => { updateFileLabels(); updateViewDefMarkdownButtonState(); });
}


function safeJsonFileName(name) {
  const raw = String(name ?? '').trim();
  if (!raw) return null;

  // API一覧から返る "test_patterns/foo.json" のようなサブフォルダ付きJSONを許可する。
  // ただし、親ディレクトリ移動・絶対パス・URL風の指定は拒否する。
  const n = raw.replace(/\\/g, '/').replace(/^\/+/, '');
  if (!n.toLowerCase().endsWith('.json')) return null;
  if (n.includes('://')) return null;
  if (/^[a-zA-Z]:/.test(n)) return null;

  const parts = n.split('/');
  if (parts.some(part => !part || part === '.' || part === '..')) return null;
  return parts.join('/');
}

function encodeJsonPath(name) {
  const n = safeJsonFileName(name);
  if (!n) return null;
  return n.split('/').map(encodeURIComponent).join('/');
}

function apiJsonUrl(kind, name) {
  const path = encodeJsonPath(name);
  if (!path) throw new Error(`${kind} JSONファイル名が不正です`);
  return `/api/${kind}/${path}`;
}

async function fetchApiJsonWithUrl(kind, name) {
  const n = safeJsonFileName(name);
  if (!n) throw new Error(`${kind} JSONファイル名が不正です`);

  const primaryUrl = apiJsonUrl(kind, n);
  try {
    return { json: await fetchJson(primaryUrl), url: primaryUrl };
  } catch (primaryErr) {
    // datalist は「表示候補」ではあるが、一覧API側が basename だけ返す構成だと、
    // 実体が data/json/foo.json でも foo.json として選択されてしまうことがある。
    // その場合は、代表サブフォルダをフォールバック探索する。
    if (!n.includes('/')) {
      const fallbackDirsByKind = {
        data: ['json'],
        defs: ['json']
      };
      for (const dir of fallbackDirsByKind[kind] ?? []) {
        const fallbackName = `${dir}/${n}`;
        const fallbackUrl = apiJsonUrl(kind, fallbackName);
        try {
          return { json: await fetchJson(fallbackUrl), url: fallbackUrl, correctedName: fallbackName };
        } catch {
          // 次の候補へ
        }
      }
      throw primaryErr;
    }

    // 旧APIが /api/data/<encoded full path> 形式で受けている場合に備えた保険。
    const legacyUrl = `/api/${kind}/${encodeURIComponent(n)}`;
    if (legacyUrl === primaryUrl) throw primaryErr;
    try {
      return { json: await fetchJson(legacyUrl), url: legacyUrl };
    } catch {
      throw primaryErr;
    }
  }
}

async function fetchApiJson(kind, name) {
  return (await fetchApiJsonWithUrl(kind, name)).json;
}


function normalizeExtendsValue(value) {
  if (Array.isArray(value)) return value.map(safeJsonFileName).filter(Boolean);
  const n = safeJsonFileName(value);
  return n ? [n] : [];
}

function resolveRelativeJsonName(name, baseName=null) {
  const n = safeJsonFileName(name);
  if (!n) return null;
  if (n.includes('/') || !baseName) return n;
  const base = safeJsonFileName(baseName);
  if (!base || !base.includes('/')) return n;
  const dir = base.split('/').slice(0, -1).join('/');
  return dir ? `${dir}/${n}` : n;
}

function mergeArrayByKey(parentArr, childArr) {
  if (!Array.isArray(parentArr)) return cloneData(childArr);
  if (!Array.isArray(childArr)) return cloneData(parentArr);

  const keyNames = ['id', 'field', 'name'];
  const key = keyNames.find(k =>
    childArr.some(x => x && typeof x === 'object' && !Array.isArray(x) && x[k] != null)
  );

  // options などの単純配列、またはキーを持たない配列は「子で丸ごと置換」。
  if (!key) return cloneData(childArr);

  const result = cloneData(parentArr);
  const indexByKey = new Map();
  result.forEach((item, i) => {
    if (item && typeof item === 'object' && !Array.isArray(item) && item[key] != null) {
      indexByKey.set(String(item[key]), i);
    }
  });

  childArr.forEach(childItem => {
    if (!childItem || typeof childItem !== 'object' || Array.isArray(childItem) || childItem[key] == null) {
      result.push(cloneData(childItem));
      return;
    }

    const k = String(childItem[key]);
    const remove = childItem.remove === true || childItem.$remove === true || childItem._remove === true;
    if (remove) {
      const idx = indexByKey.get(k);
      if (idx != null) result.splice(idx, 1);
      indexByKey.clear();
      result.forEach((item, i) => {
        if (item && typeof item === 'object' && !Array.isArray(item) && item[key] != null) {
          indexByKey.set(String(item[key]), i);
        }
      });
      return;
    }

    if (indexByKey.has(k)) {
      const idx = indexByKey.get(k);
      result[idx] = mergeViewDefObject(result[idx], childItem);
    } else {
      indexByKey.set(k, result.length);
      result.push(cloneData(childItem));
    }
  });

  return result;
}

function mergeViewDefObject(parentValue, childValue) {
  if (Array.isArray(parentValue) || Array.isArray(childValue)) {
    return mergeArrayByKey(parentValue, childValue);
  }

  if (
    parentValue && typeof parentValue === 'object' &&
    childValue && typeof childValue === 'object'
  ) {
    const result = cloneData(parentValue);
    Object.entries(childValue).forEach(([key, value]) => {
      if (key === 'extends') return;
      result[key] = key in result ? mergeViewDefObject(result[key], value) : cloneData(value);
    });
    return result;
  }

  return cloneData(childValue);
}

async function fetchResolvedViewDef(name, stack=[]) {
  const loaded = await fetchApiJsonWithUrl('defs', name);
  const actualName = loaded.correctedName || jsonNameFromUrl(loaded.url, 'defs') || safeJsonFileName(name);
  return resolveViewDefInheritance(loaded.json, actualName, stack);
}

async function resolveViewDefInheritance(defObj, currentName=null, stack=[]) {
  const parents = normalizeExtendsValue(defObj?.extends);
  if (!parents.length) return cloneData(defObj);

  const current = safeJsonFileName(currentName) || '(dropped view_def)';
  let merged = {};

  for (const parentRaw of parents) {
    const parentName = resolveRelativeJsonName(parentRaw, currentName);
    if (!parentName) throw new Error(`extends の指定が不正です: ${parentRaw}`);
    if (stack.includes(parentName)) {
      throw new Error(`ViewDef継承が循環しています: ${[...stack, parentName].join(' -> ')}`);
    }

    const parentResolved = await fetchResolvedViewDef(parentName, [...stack, current]);
    merged = mergeViewDefObject(merged, parentResolved);
  }

  const child = cloneData(defObj);
  delete child.extends;
  const resolved = mergeViewDefObject(merged, child);
  resolved._resolved_extends = parents;
  return resolved;
}

function jsonNameFromUrl(url, kind=null) {
  try {
    const u = new URL(url, location.href);
    if (kind) {
      const prefix = `/api/${kind}/`;
      if (u.pathname.startsWith(prefix)) {
        return safeJsonFileName(decodeURIComponent(u.pathname.slice(prefix.length)));
      }
    }
    return safeJsonFileName(decodeURIComponent(u.pathname.split('/').pop() ?? ''));
  } catch {
    return null;
  }
}

function extractServerFileNames(payload) {
  if (Array.isArray(payload)) return payload;
  if (Array.isArray(payload?.files)) return payload.files;
  if (Array.isArray(payload?.items)) {
    return payload.items.map(item => {
      if (typeof item === 'string') return item;
      return item?.path || item?.name || item?.file || '';
    });
  }
  return [];
}

function normalizeServerNames(payload) {
  return uniqueNames(extractServerFileNames(payload)).sort((a, b) => a.localeCompare(b));
}

function baseJsonName(name) {
  const n = safeJsonFileName(name);
  return n ? n.split('/').pop() : '';
}

function resolveServerListedName(rawName, serverNames, label) {
  const n = safeJsonFileName(rawName);
  if (!n) return null;

  const names = uniqueNames(serverNames);

  // 一覧APIが使えない環境では、従来どおり安全なJSON名なら許可する。
  if (!names.length) return n;

  if (names.includes(n)) return n;

  // data/json/foo.json のようにサブフォルダ配下へ移動していても、
  // basename が一意なら自動補正する。
  const matches = names.filter(name => baseJsonName(name) === n);
  if (matches.length === 1) return matches[0];

  if (matches.length > 1) {
    throw new Error(`${label}「${n}」は複数候補があります: ${matches.join(' / ')}。フルパスで選択してください`);
  }

  throw new Error(`${label}「${n}」は管理対象一覧にありません。コンボの一覧から選び直すか、Dropしてください`);
}

function setDatalist(id, names) {
  const dl = $(id);
  if (!dl) return;
  dl.innerHTML = '';
  uniqueNames(names).forEach(name => {
    const opt = document.createElement('option');
    opt.value = name;
    // label属性を入れると Chrome / Edge の datalist が
    // 「value + label」の2行表示になるため、1行表示を優先して value のみにする。
    dl.appendChild(opt);
  });
}

function normalizeComboInput(input, serverNames, label) {
  if (!input) return null;
  const raw = String(input.value ?? '').trim();
  if (!raw) return null;
  const resolved = resolveServerListedName(raw, serverNames, label);
  if (resolved && resolved !== raw) {
    input.value = resolved;
    setStatus(`${label}のパスを補正しました: ${raw} → ${resolved}`);
  }
  return resolved;
}

async function refreshServerLists() {
  try {
    const [defs, data] = await Promise.all([
      fetchJson('/api/defs'),
      fetchJson('/api/data')
    ]);
    serverDefNames = normalizeServerNames(defs);
    serverDataNames = normalizeServerNames(data);
    setDatalist('defNameList', serverDefNames);
    setDatalist('dataNameList', serverDataNames);
    setStatus(`一覧を更新しました: defs ${serverDefNames.length}件 / data ${serverDataNames.length}件`);
  } catch (err) {
    console.warn(err);
    setStatus('一覧API未使用: DropまたはURL指定で読み込めます');
  }
}

function selectedDefName() {
  return normalizeComboInput($('defNameInput'), serverDefNames, '画面定義JSON');
}

function selectedDataName() {
  return normalizeComboInput($('dataNameInput'), serverDataNames, '対象JSON');
}

function getDataViewDefName(dataObj) {
  return safeJsonFileName(dataObj?.view_def || dataObj?.viewDef || dataObj?.view_definition || dataObj?.viewDefinition);
}


function mainViewOf(defObj) {
  return defObj?.views?.[0] ?? defObj;
}

function gridDefOf(defObj) {
  return mainViewOf(defObj)?.sections?.find(s => s.type === 'grid') ?? null;
}

function dataArraysAtRoot(dataObj) {
  if (!dataObj || typeof dataObj !== 'object' || Array.isArray(dataObj)) return [];
  return Object.keys(dataObj).filter(key => Array.isArray(dataObj[key]));
}

function defCompatibilityMessage(defName, defObj, dataObj, dataName='') {
  const gd = gridDefOf(defObj);
  const dataLabel = dataName ? `「${dataName}」` : '対象JSON';
  if (!gd) return `画面定義JSON「${defName ?? '(未選択)'}」に grid section がありません`;
  const arrays = dataArraysAtRoot(dataObj);
  const arrayHint = arrays.length ? `対象JSONの配列候補: ${arrays.map(x => '$.' + x).join(', ')}` : '対象JSON直下に配列が見つかりません';
  return `画面定義JSON「${defName ?? '(未選択)'}」と${dataLabel}の形が合いません。mainGrid dataPath ${gd.dataPath} が Array ではありません。${arrayHint}`;
}

function isDefCompatibleWithData(defObj, dataObj) {
  const gd = gridDefOf(defObj);
  if (!gd?.dataPath) return false;
  return Array.isArray(getByPath(dataObj, gd.dataPath));
}

function scoreDefNameForData(name, dataObj, dataName='') {
  const n = String(name ?? '').toLowerCase();
  const dn = String(dataName ?? '').toLowerCase();
  const arrays = dataArraysAtRoot(dataObj).map(x => x.toLowerCase());
  let score = 0;

  if (getDataViewDefName(dataObj) === name) score += 1000;
  if (dn.includes('screen_state') && n.includes('screen_state')) score += 120;
  if (dn.includes('expected') && n.includes('expected')) score += 90;
  if (dn.includes('diff') && n.includes('diff')) score += 70;
  if (dn.includes('constraint') && n.includes('constraint')) score += 80;
  if (dn.includes('view_def') && n.includes('view_def')) score += 40;
  if (arrays.includes('checks') && n.includes('expected')) score += 110;
  if (arrays.includes('checks') && n.includes('screen_state')) score += 80;
  if (arrays.includes('constraints') && n.includes('constraint')) score += 120;
  if ((arrays.includes('test_patterns') || arrays.includes('patterns') || arrays.includes('tests')) && n.includes('test')) score += 60;
  if ((arrays.includes('fields') || arrays.includes('sections') || arrays.includes('views')) && n.includes('view_def')) score += 50;

  // 名前の一部が一致する場合の弱い加点（例: screen_state_xxx.json ↔ screen_state_yyy_view_def.json）
  for (const token of dn.split(/[^a-z0-9]+/).filter(t => t.length >= 4)) {
    if (n.includes(token)) score += 6;
  }
  return score;
}

function uniqueNames(names) {
  const seen = new Set();
  const out = [];
  for (const raw of names) {
    const n = safeJsonFileName(raw);
    if (!n || seen.has(n)) continue;
    seen.add(n);
    out.push(n);
  }
  return out;
}

function inferLikelyDefNames(dataObj, dataName='') {
  const names = [];
  const embedded = getDataViewDefName(dataObj);
  if (embedded) names.push(embedded);

  const arrays = dataArraysAtRoot(dataObj).map(x => x.toLowerCase());
  const dn = String(dataName ?? '').toLowerCase();

  if (arrays.includes('checks')) {
    names.push('screen_state_expected_view_def_v0_1.json');
  }
  if (arrays.includes('constraints')) {
    names.push('ai_constraint_view_def_v0_5_verification_radio.json');
    names.push('ai_constraint_view_def_v0_5_chat.json');
  }
  if (dn.includes('screen_state')) {
    names.push('screen_state_expected_view_def_v0_1.json');
    names.push('screen_state_diff_view_def_v0_2_emphasis.json');
    names.push('screen_state_diff_view_def_v0_1.json');
  }

  const rankedServerDefs = uniqueNames(serverDefNames)
    .map(name => ({ name, score: scoreDefNameForData(name, dataObj, dataName) }))
    .sort((a, b) => b.score - a.score || a.name.localeCompare(b.name))
    .map(x => x.name);

  return uniqueNames([...names, ...rankedServerDefs]);
}

async function findCompatibleDefForData(dataObj, dataName='', excludedNames=[]) {
  const excluded = new Set(uniqueNames(excludedNames));
  const candidates = inferLikelyDefNames(dataObj, dataName).filter(n => !excluded.has(n));

  for (const candidate of candidates) {
    try {
      const defObj = await fetchResolvedViewDef(candidate);
      if (isDefCompatibleWithData(defObj, dataObj)) {
        return { defName: candidate, defObj };
      }
    } catch (err) {
      console.warn('compatible def candidate skipped:', candidate, err);
    }
  }
  return null;
}

async function resolveDefForData(preferredDefName, dataObj, dataName='') {
  const preferred = safeJsonFileName(preferredDefName);
  const embeddedDefName = getDataViewDefName(dataObj);

  // 画面定義JSONを明示選択した場合は、対象JSON内の view_def より優先する。
  // これで「同じデータを別ViewDefで見る」デモが成立する。
  let defName = preferred || embeddedDefName;

  if (defName) {
    const defObj = await fetchResolvedViewDef(defName);
    if (isDefCompatibleWithData(defObj, dataObj)) {
      return { defName, defObj, autoChanged: !preferred && embeddedDefName && embeddedDefName !== preferredDefName };
    }

    const compatible = await findCompatibleDefForData(dataObj, dataName, [defName]);
    if (compatible) {
      return { ...compatible, autoChanged: true, previousDefName: defName };
    }

    throw new Error(defCompatibilityMessage(defName, defObj, dataObj, dataName) + '。画面定義JSONを選び直すか、対象JSONに view_def を入れてください');
  }

  const compatible = await findCompatibleDefForData(dataObj, dataName);
  if (compatible) return { ...compatible, autoChanged: true };

  throw new Error('対象JSONに view_def がありません。画面定義JSONを選択してください');
}

function ensureViewDefNameInData(dataObj, defName) {
  if (!dataObj || typeof dataObj !== 'object' || Array.isArray(dataObj)) return;
  const n = safeJsonFileName(defName);
  if (n) dataObj.view_def = n;
}

async function loadFromServerNames(defName, dataName) {
  // dataコンボから読み込む場合も、対象JSON内の view_def を優先する。
  // これにより「対象JSONだけ選ぶ → 読み込み」で画面定義を自動決定できる。
  defName = resolveServerListedName(defName, serverDefNames, '画面定義JSON');
  dataName = resolveServerListedName(dataName, serverDataNames, '対象JSON');
  if (!dataName) throw new Error('対象JSONを選択してください');

  $('dataNameInput').value = dataName;
  $('defFileName').textContent = 'Drop';
  $('dataFileName').textContent = 'Drop';
  setStatus('API管理ファイルを読み込み中...');

  const loadedData = await fetchApiJsonWithUrl('data', dataName);
  const actualDataName = loadedData.correctedName || jsonNameFromUrl(loadedData.url, 'data');
  if (actualDataName && actualDataName !== dataName) {
    dataName = actualDataName;
    $('dataNameInput').value = dataName;
  }
  const dataObj = loadedData.json;

  const resolved = await resolveDefForData(defName, dataObj, dataName);
  defName = resolved.defName;
  const defObj = resolved.defObj;
  $('defNameInput').value = defName;

  ensureViewDefNameInData(dataObj, defName);
  lastLoadedDefName = defName;
  const autoMsg = resolved.previousDefName
    ? ` / 画面定義を自動補正: ${resolved.previousDefName} → ${defName}`
    : (resolved.autoChanged ? ` / 画面定義を自動選択: ${defName}` : '');
  loadFromObjects(defObj, dataObj, `API管理ファイルを読み込みました: ${dataName}${autoMsg}`, loadedData.url);
}


async function registerDroppedDef(fileName, defObj) {
  const name = safeJsonFileName(fileName);
  if (!name) throw new Error('画面定義JSONファイル名が不正です');

  const res = await fetch('/api/defs/drop', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name, json: defObj })
  });
  if (!res.ok) {
    const text = await res.text().catch(() => '');
    throw new Error(`画面定義JSONの管理対象コピーに失敗しました (${res.status}) ${text}`);
  }
  await refreshServerLists();
  $('defNameInput').value = name;
  updateViewDefMarkdownButtonState();
  return apiJsonUrl('defs', name);
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
  return apiJsonUrl('data', name);
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
  if (dataObj && !defName && getDataViewDefName(dataObj)) {
    defName = getDataViewDefName(dataObj);
    $('defNameInput').value = defName;
  }

  let defObj = null;
  let droppedDefName = null;
  let droppedDefRawObj = null;
  if (defFile) {
    droppedDefName = defFile.name;
    droppedDefRawObj = JSON.parse(await defFile.text());
    defName = safeJsonFileName(defFile.name) || defName || 'dropped_view_def.json';
    $('defNameInput').value = defName;
    defObj = await resolveViewDefInheritance(droppedDefRawObj, defName);
    if (dataObj && !isDefCompatibleWithData(defObj, dataObj)) {
      throw new Error(defCompatibilityMessage(defName, defObj, dataObj, droppedDataName) + '。Dropした画面定義JSONと対象JSONの組み合わせを確認してください');
    }
  } else if (dataObj) {
    const resolved = await resolveDefForData(defName, dataObj, droppedDataName);
    defName = resolved.defName;
    defObj = resolved.defObj;
    $('defNameInput').value = defName;
  } else if (defName) {
    defObj = await fetchResolvedViewDef(defName);
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
  const manageTargets = droppedDefName
    ? `${droppedDefName}  → defsフォルダ\n${droppedDataName}  → dataフォルダ`
    : `${droppedDataName}  → dataフォルダ`;

  if (confirm(`このファイルをFRB Studioで管理しますか？\n\n${manageTargets}\n\n[OK] 管理対象へコピーして上書き保存可能にする\n[キャンセル] 今回は見るだけ（保存は別名保存）`)) {
    if (droppedDefName) {
      await registerDroppedDef(droppedDefName, droppedDefRawObj ?? defObj);
    }
    dataApiUrl = await registerDroppedData(droppedDataName, dataObj, defName);
    const copiedLabel = droppedDefName
      ? `管理対象にコピーして読み込みました: ${droppedDefName} / ${droppedDataName}`
      : `管理対象にコピーして読み込みました: ${droppedDataName}`;
    loadFromObjects(defObj, dataObj, copiedLabel, dataApiUrl);
  } else {
    if (droppedDefName) $('defNameInput').value = '';
    $('dataNameInput').value = '';
    loadFromObjects(defObj, dataObj, `見るだけで読み込みました: ${droppedDataName}`, null);
  }
}


function suppressBrowserAutofillOnComboInputs() {
  [
    { id: 'defNameInput', name: 'frb_def_combo_009' },
    { id: 'dataNameInput', name: 'frb_data_combo_009' }
  ].forEach(({ id, name }) => {
    const input = $(id);
    if (!input) return;
    input.setAttribute('autocomplete', 'off');
    input.setAttribute('autocorrect', 'off');
    input.setAttribute('autocapitalize', 'off');
    input.setAttribute('spellcheck', 'false');
    input.setAttribute('name', name);
  });
}

function setupPageDrop() {
  document.querySelectorAll('.drop-file-box').forEach(setupDropFileBox);
  document.addEventListener('dragover', (e) => e.preventDefault());
  document.addEventListener('drop', (e) => e.preventDefault());
}


function hasViewDefMarkdownTarget() {
  const droppedDefFile = $('defFile')?.files?.[0] ?? null;
  const comboName = safeJsonFileName($('defNameInput')?.value);
  const loadedName = safeJsonFileName(lastLoadedDefName);
  return Boolean(viewDef || droppedDefFile || comboName || loadedName);
}

function updateViewDefMarkdownButtonState() {
  const btn = $('exportViewDefMarkdownBtn');
  if (!btn) return;
  btn.disabled = !hasViewDefMarkdownTarget();
}

function setupViewDefMarkdownButtonState() {
  const defInput = $('defNameInput');
  const defFile = $('defFile');
  if (defInput) {
    defInput.addEventListener('input', updateViewDefMarkdownButtonState);
    defInput.addEventListener('change', updateViewDefMarkdownButtonState);
  }
  if (defFile) defFile.addEventListener('change', updateViewDefMarkdownButtonState);
  updateViewDefMarkdownButtonState();
}

function setupComboClearButtons() {
  const configs = [
    { inputId: 'defNameInput', buttonId: 'clearDefNameBtn', label: '画面定義JSON', names: () => serverDefNames },
    { inputId: 'dataNameInput', buttonId: 'clearDataNameBtn', label: '対象JSON', names: () => serverDataNames }
  ];
  configs.forEach(({ inputId, buttonId, label, names }) => {
    const input = $(inputId);
    const button = $(buttonId);
    if (!input || !button) return;

    const sync = () => {
      button.classList.toggle('visible', String(input.value ?? '').trim().length > 0);
    };

    input.addEventListener('input', sync);
    input.addEventListener('change', () => {
      try {
        normalizeComboInput(input, names(), label);
      } catch (err) {
        console.warn(err);
        setStatus('選択エラー: ' + err.message);
      }
      sync();
    });
    button.addEventListener('click', (e) => {
      e.preventDefault();
      e.stopPropagation();
      input.value = '';
      input.dispatchEvent(new Event('input', { bubbles: true }));
      updateViewDefMarkdownButtonState();
      input.focus();
      setStatus(`${label}の選択をクリアしました`);
    });
    sync();
  });
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


function wantsListBox(field) {
  return field?.edit?.control === 'listbox' || field?.edit?.selectMode === 'listbox' || field?.control === 'listbox';
}

function applySelectDisplayMode(input, field) {
  if (!wantsListBox(field)) return;
  const optionCount = (field.options?.length ?? 0) + 1;
  input.size = Math.max(2, optionCount);
  input.classList.add('listbox-select');
}


function wantsRadioControl(field) {
  return field?.edit?.control === 'radio' || field?.control === 'radio';
}

function createRadioControl(field, value, prefix, readonly=false) {
  const group = document.createElement('div');
  group.className = 'field-radio-group';
  const name = `${prefix}_${field.field}_${selectedIndex}`;
  (field.options ?? []).forEach(opt => {
    const label = document.createElement('label');
    label.className = 'field-radio-option';
    const input = document.createElement('input');
    input.type = 'radio';
    input.name = name;
    input.value = opt;
    input.dataset.field = field.field;
    input.dataset.type = field.type ?? 'select';
    input.dataset.prefix = prefix;
    input.checked = String(value ?? field.defaultValue ?? '') === String(opt);
    if (readonly) input.disabled = true;
    label.appendChild(input);
    const text = document.createElement('span');
    text.textContent = String(opt);
    label.appendChild(text);
    group.appendChild(label);
  });
  return group;
}

function stripReviewOptionLabel(value) {
  return String(value ?? '').replace(/^[◎△×★]\s*/, '');
}

function createEmbeddedChatField(config, row, gd, prefix) {
  const srcField = (gd?.fields ?? []).find(f => f.field === config.field) ?? {};
  const merged = { ...srcField, ...config, edit: { ...(srcField.edit ?? {}), ...(config.edit ?? {}) } };
  const readonly = Boolean(merged.readonly || merged.edit?.readonly);
  const current = getByPath(row, merged.field) ?? merged.defaultValue ?? '';

  const box = document.createElement('div');
  box.className = 'chat-embedded-field';

  if (config.label) {
    const cap = document.createElement('span');
    cap.className = 'chat-embedded-caption';
    cap.textContent = config.label;
    box.appendChild(cap);
  }

  const control = merged.control ?? merged.edit?.control;
  if (control === 'radio') {
    const group = document.createElement('div');
    group.className = 'chat-radio-group';
    const name = `${prefix}_${merged.field}_${selectedIndex}`;
    (merged.options ?? []).forEach(opt => {
      const label = document.createElement('label');
      label.className = 'chat-radio-option';

      const input = document.createElement('input');
      input.type = 'radio';
      input.name = name;
      input.value = opt;
      input.dataset.field = merged.field;
      input.dataset.type = merged.type ?? 'select';
      input.dataset.prefix = prefix;
      input.checked = String(current) === String(opt);
      if (readonly) input.disabled = true;

      label.appendChild(input);

      const text = document.createElement('span');
      text.textContent = stripReviewOptionLabel(opt);
      label.appendChild(text);

      group.appendChild(label);
    });
    box.appendChild(group);
    return box;
  }

  const normal = createInput(merged, current, prefix, readonly, row, gd);
  normal.classList.add('chat-embedded-normal');
  box.appendChild(normal);
  return box;
}

function normalizeChatMessages(field, row, gd) {
  const configured = field?.edit?.messages ?? field?.messages ?? field?.chat?.messages;
  if (Array.isArray(configured) && configured.length) return configured;

  // 既存のAI制約設計書v0.3形式を、専用データ移行なしでチャット表示できる既定マッピング。
  const existing = new Set((gd?.fields ?? []).map(f => f.field));
  const candidates = [
    { role: 'constraint', field: 'statement', label: '制約本文', readonly: true },
    { role: 'user', field: 'user_comment', label: '俺コメント' },
    { role: 'ai', field: 'ai_response', label: 'AI回答', readonly: true },
    { role: 'user', field: 'user_reply', label: '俺追加回答' },
    { role: 'ai', field: 'ai_followup_response', label: 'AI再回答', readonly: true }
  ];
  return candidates.filter(m => existing.has(m.field));
}

function currentDetailRow() {
  if (detailMode === 'new') return draftRow;
  if (selectedIndex >= 0 && Array.isArray(currentRows)) return currentRows[selectedIndex];
  return null;
}

function chatTextValue(row, fieldName) {
  return String(getByPath(row, fieldName) ?? '').trim();
}

function shouldRenderChatMessage(msg, row) {
  const fieldName = msg?.field;
  if (!fieldName) return true;

  // 追加会話は、まだ人間が追記していない間は空の吹き出しを出さない。
  if (fieldName === 'user_reply') {
    return chatTextValue(row, 'user_reply') !== '';
  }

  // AI再回答は、人間の追記が入った時点で「空のAI回答待ち欄」として表示する。
  if (fieldName === 'ai_followup_response') {
    return chatTextValue(row, 'user_reply') !== '' || chatTextValue(row, 'ai_followup_response') !== '';
  }

  return true;
}

function chatInputConfig(field, gd) {
  const cfg = field?.edit?.input ?? field?.input ?? field?.chat?.input ?? {};
  const existing = new Set((gd?.fields ?? []).map(f => f.field));
  const userField = cfg.userField ?? cfg.user_field ?? (existing.has('user_reply') ? 'user_reply' : null);
  const aiField = cfg.aiField ?? cfg.ai_field ?? (existing.has('ai_followup_response') ? 'ai_followup_response' : null);
  return {
    enabled: cfg.enabled !== false && Boolean(userField),
    userField,
    aiField,
    placeholder: cfg.placeholder ?? 'この行へのコメントを追加...',
    sendLabel: (cfg.sendLabel ?? cfg.send_label ?? '送信') || '送信'
  };
}

function createChatComposer(field, row, gd, prefix) {
  const cfg = chatInputConfig(field, gd);
  if (!cfg.enabled) return null;

  const composer = document.createElement('div');
  composer.className = 'chat-composer';

  const plus = document.createElement('div');
  plus.className = 'chat-composer-plus';
  plus.textContent = '+';
  composer.appendChild(plus);

  const input = document.createElement('textarea');
  input.className = 'chat-composer-input';
  input.placeholder = cfg.placeholder;
  input.rows = 1;
  input.dataset.prefix = prefix;
  composer.appendChild(input);

  const send = document.createElement('button');
  send.type = 'button';
  send.className = 'chat-composer-send';
  send.textContent = cfg.sendLabel;
  composer.appendChild(send);

  const submit = () => {
    const text = input.value.trim();
    if (!text) {
      input.focus();
      return;
    }

    const targetRow = currentDetailRow() ?? row;
    if (!targetRow) return;

    // 送信前に画面上の未反映入力を行データへ回収する。
    applyDetailInputsToRow(targetRow);

    const previous = chatTextValue(targetRow, cfg.userField);
    const next = previous ? `${previous}\n\n${text}` : text;
    setByPath(targetRow, cfg.userField, next);

    if (cfg.aiField && getByPath(targetRow, cfg.aiField) == null) {
      setByPath(targetRow, cfg.aiField, '');
    }

    renderDetailForRow(targetRow);
    setStatus('コメントを追加しました。必要に応じてAI再回答欄へ回答を追記してください。');
  };

  send.addEventListener('click', submit);
  input.addEventListener('input', () => {
    input.style.height = 'auto';
    input.style.height = Math.min(input.scrollHeight, 120) + 'px';
  });
  input.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
      e.preventDefault();
      submit();
    }
  });

  return composer;
}

function createChatInput(field, row, gd, prefix) {
  const wrap = document.createElement('div');
  wrap.className = 'field chat-field';

  const label = document.createElement('label');
  label.textContent = field.caption ?? '会話';
  wrap.appendChild(label);

  const timeline = document.createElement('div');
  timeline.className = 'chat-timeline';

  normalizeChatMessages(field, row, gd).forEach(msg => {
    if (!shouldRenderChatMessage(msg, row)) return;

    const srcField = (gd?.fields ?? []).find(f => f.field === msg.field) ?? {};
    const raw = getByPath(row, msg.field);
    const role = String(msg.role ?? '').toLowerCase();
    const isAi = role === 'ai' || role === 'assistant';
    const isUser = role === 'user' || role === 'human' || role === '俺';
    const isConstraint = role === 'constraint' || role === 'system' || role === 'statement';
    const readonly = Boolean(msg.readonly || srcField.readonly || srcField.edit?.readonly);

    const item = document.createElement('div');
    item.className = 'chat-message ' + (isAi ? 'chat-ai' : isUser ? 'chat-user' : isConstraint ? 'chat-constraint' : 'chat-other');

    const meta = document.createElement('div');
    meta.className = 'chat-meta';
    meta.textContent = msg.label ?? srcField.caption ?? msg.field;
    item.appendChild(meta);

    const embeddedFields = msg.embeddedFields ?? msg.embedded_fields ?? [];
    if (Array.isArray(embeddedFields) && embeddedFields.length) {
      const embeddedWrap = document.createElement('div');
      embeddedWrap.className = 'chat-embedded-fields';
      embeddedFields.forEach(ef => embeddedWrap.appendChild(createEmbeddedChatField(ef, row, gd, prefix)));
      item.appendChild(embeddedWrap);
    }

    const bubble = document.createElement('div');
    bubble.className = 'chat-text';
    bubble.textContent = raw == null ? '' : String(raw);
    bubble.dataset.field = msg.field;
    bubble.dataset.type = srcField.type ?? 'textarea';
    bubble.dataset.prefix = prefix;
    bubble.dataset.placeholder = msg.placeholder ?? '';
    bubble.setAttribute('role', 'textbox');
    bubble.setAttribute('aria-label', msg.label ?? srcField.caption ?? msg.field);
    bubble.setAttribute('spellcheck', 'false');
    bubble.contentEditable = readonly ? 'false' : 'true';
    if (readonly) {
      bubble.classList.add('readonly');
      item.classList.add('readonly');
    }
    bubble.addEventListener('keydown', (e) => {
      // contenteditable内ではF12/F7/F8だけ親の詳細操作へ渡す。
      if (e.key === 'F7' || e.key === 'F8' || e.key === 'F12') return;
      // Ctrl+Enter は反映のショートカット。改行は Enter で通常通り入力できる。
      if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        e.preventDefault();
        applyDetail(e);
      }
    });
    item.appendChild(bubble);

    timeline.appendChild(item);
  });

  const composer = createChatComposer(field, row, gd, prefix);
  if (composer) timeline.appendChild(composer);

  wrap.appendChild(timeline);
  return wrap;
}

function createInput(field, value, prefix, readonlyOverride=false, row=null, gd=null) {
  if (field.type === 'chat') return createChatInput(field, row ?? {}, gd ?? gridDef(), prefix);

  const readonly = readonlyOverride || field.readonly || field.edit?.readonly;
  const wrap = document.createElement('div');
  wrap.className = 'field' + (readonly ? ' readonly' : '');
  const label = document.createElement('label');
  const shortcut = field.edit?.shortcut ? ` (${field.edit.shortcut})` : '';
  label.textContent = (field.caption ?? field.field) + shortcut;
  wrap.appendChild(label);

  let input;
  if (wantsRadioControl(field)) {
    input = createRadioControl(field, value, prefix, readonly);
  } else if (field.type === 'select') {
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
    applySelectDisplayMode(input, field);
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
    applySelectDisplayMode(input, field);
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


function detailPlacement(field) {
  return String(
    field?.layout?.placement ??
    field?.edit?.layout?.placement ??
    field?.edit?.placement ??
    field?.placement ??
    ''
  ).trim();
}

function detailAfter(field) {
  return String(
    field?.layout?.after ??
    field?.edit?.layout?.after ??
    field?.edit?.after ??
    field?.after ??
    ''
  ).trim();
}

function isDetailFooterField(field) {
  const placement = detailPlacement(field);
  const after = detailAfter(field);
  return placement === 'detailFooter' || placement === 'afterChildGrids' || after === 'childGrids';
}

function detailVisibleFields(gd) {
  return (gd?.fields ?? []).filter(f => f.edit?.visible !== false);
}

function renderDetailFooterFields(row, gd) {
  const footerFields = detailVisibleFields(gd).filter(isDetailFooterField);
  if (!footerFields.length) return;

  const area = $('childArea');
  const wrap = document.createElement('div');
  wrap.className = 'detail-after-child-fields';

  footerFields.forEach(field => {
    wrap.appendChild(createInput(field, getByPath(row, field.field), 'detail', false, row, gd));
  });

  area.appendChild(wrap);
}



function valueIsFail(value) {
  return value === false || String(value).toLowerCase() === 'false' || String(value).toLowerCase() === 'fail';
}

function valueIsPass(value) {
  return value === true || String(value).toLowerCase() === 'true' || String(value).toLowerCase() === 'pass';
}

function hasMissingItems(value) {
  if (Array.isArray(value)) return value.length > 0;
  const text = String(value ?? '').trim();
  return text !== '' && text !== '[]' && text.toLowerCase() !== 'n/a';
}

function safeCssToken(value) {
  return String(value ?? '')
    .replace(/[^a-zA-Z0-9_-]/g, '-')
    .replace(/-+/g, '-')
    .replace(/^-|-$/g, '')
    .toLowerCase();
}

function applyGridRowEmphasis(tr, row) {
  const passValue = row?.pass;
  const statusValue = row?.status;
  const resultLabel = String(row?.resultLabel ?? '');

  if (valueIsFail(passValue) || valueIsFail(statusValue) || resultLabel.includes('FAIL') || resultLabel.includes('失敗')) {
    tr.classList.add('row-fail');
  } else if (valueIsPass(passValue) || valueIsPass(statusValue) || resultLabel.includes('PASS')) {
    tr.classList.add('row-pass');
  }

  if (hasMissingItems(row?.missing)) tr.classList.add('row-missing');
}

function applyGridCellEmphasis(td, field, row, value) {
  const fieldName = field?.field ?? '';
  const token = safeCssToken(fieldName);
  if (token) td.classList.add('cell-field-' + token);

  if (fieldName === 'pass' || fieldName === 'status') {
    if (valueIsFail(value)) td.classList.add('cell-fail', 'cell-result');
    if (valueIsPass(value)) td.classList.add('cell-pass', 'cell-result');
  }

  if (fieldName === 'missing') {
    td.classList.add('cell-missing-list');
    if (hasMissingItems(value)) td.classList.add('cell-missing');
    else td.classList.add('cell-missing-empty');
  }

  if (row?.pass === false || String(row?.pass).toLowerCase() === 'false') {
    if (fieldName === 'expected') td.classList.add('cell-expected-fail');
    if (fieldName === 'actual') td.classList.add('cell-actual-fail');
    if (fieldName === 'name') td.classList.add('cell-check-fail');
  }
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
    applyGridRowEmphasis(tr, row);
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
      if (f.type) td.classList.add(f.type);
      const value = getByPath(row, f.field);
      td.textContent = formatValue(value, f);
      applyGridCellEmphasis(td, f, row, value);
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
  return assignNewRowKeys(row);
}
function addGridRow() {
  if (!Array.isArray(currentRows)) return;
  applyHeaderEdits();
  const row = createDefaultRow();
  openNewDetail(row, '新規登録画面を開きました（反映するまで行は追加されません）');
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

function nextNumberValue(fieldName) {
  const vals = (currentRows ?? [])
    .map(r => Number(getByPath(r, fieldName)))
    .filter(n => Number.isFinite(n));
  return vals.length ? Math.max(...vals) + 1 : 1;
}

function regexEscape(text) {
  return String(text).replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

function nextUniqueKeyValue(keyField, sourceValue) {
  const existing = new Set((currentRows ?? []).map(r => String(getByPath(r, keyField) ?? '')).filter(Boolean));
  const src = String(sourceValue ?? '').trim();
  const m = src.match(/^(.*?)(\d+)$/);
  if (m) {
    const prefix = m[1];
    const width = m[2].length;
    let maxNo = 0;
    const re = new RegExp('^' + regexEscape(prefix) + '(\\d+)$');
    existing.forEach(v => {
      const mm = v.match(re);
      if (mm) maxNo = Math.max(maxNo, Number(mm[1]));
    });
    let n = maxNo + 1;
    let candidate = prefix + String(n).padStart(width, '0');
    while (existing.has(candidate)) {
      n += 1;
      candidate = prefix + String(n).padStart(width, '0');
    }
    return candidate;
  }
  const base = src || 'row';
  let n = 1;
  let candidate = `${base}_copy_${n}`;
  while (existing.has(candidate)) {
    n += 1;
    candidate = `${base}_copy_${n}`;
  }
  return candidate;
}

function removeCreateExcludedFields(row) {
  const gd = gridDef();
  (gd.fields ?? []).forEach(field => {
    if (field.create?.include === false) {
      const parts = String(field.field ?? '').split('.');
      let cur = row;
      for (let i = 0; i < parts.length - 1; i++) {
        cur = cur?.[parts[i]];
        if (cur == null) return;
      }
      if (cur && Object.prototype.hasOwnProperty.call(cur, parts[parts.length - 1])) {
        delete cur[parts[parts.length - 1]];
      }
    }
  });
}

function assignNewRowKeys(row, sourceRow=null) {
  const gd = gridDef();
  const noField = (gd.fields ?? []).find(f => f.field === 'no' || String(f.field).toLowerCase() === 'no');
  if (noField) setByPath(row, noField.field, nextNumberValue(noField.field));
  if (gd.keyField) {
    const oldKey = sourceRow ? getByPath(sourceRow, gd.keyField) : getByPath(row, gd.keyField);
    setByPath(row, gd.keyField, nextUniqueKeyValue(gd.keyField, oldKey));
  }
  return row;
}

function createRowFromSourceRow(sourceRow) {
  const row = cloneData(sourceRow);
  removeCreateExcludedFields(row);
  return assignNewRowKeys(row, sourceRow);
}

function detailEditableControls() {
  return [...$('detailForm').querySelectorAll('input, select, textarea, [contenteditable][data-field]')];
}

function getControlValue(el) {
  if (el.hasAttribute('contenteditable')) return el.innerText ?? '';
  return el.value;
}

function setControlValue(el, value) {
  const text = value == null ? '' : String(value);
  if (el.hasAttribute('contenteditable')) {
    el.innerText = text;
  } else {
    el.value = text;
  }
}

function isControlReadonly(el) {
  if (el.disabled) return true;
  if (el.hasAttribute('contenteditable')) return el.getAttribute('contenteditable') === 'false';
  return false;
}

function pasteCopiedRowToForm() {
  if (!copiedRow) {
    setStatus('コピー済み行がありません');
    return;
  }
  const gd = gridDef();
  detailEditableControls().forEach(inp => {
    const field = gd.fields.find(f => f.field === inp.dataset.field);
    if (!field || field.edit?.readonly || field.readonly || isControlReadonly(inp)) return;
    const value = getByPath(copiedRow, field.field);
    setControlValue(inp, value);
  });
  setStatus('コピー行の値を詳細ダイアログへ貼り付けました');
}

function addRowFromCopiedRow() {
  if (!copiedRow) {
    setStatus('コピー済み行がありません');
    return;
  }
  applyHeaderEdits();
  const row = createRowFromSourceRow(copiedRow);
  openNewDetail(row, 'コピー行から新規登録画面を開きました（反映するまで行は追加されません）');
}
function hideRowContextMenu() {
  const menu = $('rowContextMenu');
  if (menu) menu.classList.add('hidden');
}

function duplicateRowToNew(index) {
  if (!Array.isArray(currentRows) || index < 0 || !currentRows[index]) {
    setStatus('コピー新規する行を選択してください');
    return;
  }
  applyHeaderEdits();
  copiedRow = cloneData(currentRows[index]);
  const row = createRowFromSourceRow(copiedRow);
  const keyMsg = gridDef()?.keyField ? ` / ${gridDef().keyField}: ${getByPath(row, gridDef().keyField)}` : '';
  openNewDetail(row, `この行をコピーして新規登録画面へ遷移しました${keyMsg}（反映するまで行は追加されません）`);
}

function showRowContextMenu(x, y, index) {
  let menu = $('rowContextMenu');
  if (!menu) return;
  menu.innerHTML = '';

  const duplicateBtn = document.createElement('button');
  duplicateBtn.textContent = 'この行をコピーしてから新規登録画面へ遷移します。';
  duplicateBtn.addEventListener('click', () => { duplicateRowToNew(index); hideRowContextMenu(); });
  menu.appendChild(duplicateBtn);

  menu.style.left = x + 'px';
  menu.style.top = y + 'px';
  menu.classList.remove('hidden');
}
document.addEventListener('click', hideRowContextMenu);
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') hideRowContextMenu();
  if (!$('detailDialog')?.open) return;
  if (e.key === 'F7') { e.preventDefault(); moveDetail(-1); }
  if (e.key === 'F8') { e.preventDefault(); moveDetail(1); }
  if (e.key === 'F12') { e.preventDefault(); applyDetail(e); }
});

function currentFilteredPosition() {
  if (selectedIndex < 0) return -1;
  return filteredRows.findIndex(x => x.index === selectedIndex);
}

function updateDetailNavButtons() {
  const pos = currentFilteredPosition();
  const prevBtn = $('prevDetailBtn');
  const nextBtn = $('nextDetailBtn');
  if (detailMode === 'new') {
    if (prevBtn) prevBtn.disabled = true;
    if (nextBtn) nextBtn.disabled = true;
    return;
  }
  if (prevBtn) prevBtn.disabled = pos <= 0;
  if (nextBtn) nextBtn.disabled = pos < 0 || pos >= filteredRows.length - 1;
}

function applyDetailInputsToRow(row) {
  if (!row) return;
  const gd = gridDef();
  detailEditableControls().forEach(inp => {
    if (!inp.dataset.field) return;
    if (inp.type === 'radio' && !inp.checked) return;
    const field = gd.fields.find(f => f.field === inp.dataset.field);
    if (!field || field.edit?.readonly || field.readonly || isControlReadonly(inp)) return;
    setByPath(row, field.field, convertValue(field.type, getControlValue(inp)));
  });
}

function applyDetailInputsToSelectedRow() {
  if (selectedIndex < 0) return;
  applyDetailInputsToRow(currentRows[selectedIndex]);
}
function moveDetail(delta) {
  if (detailMode === 'new') return;
  const pos = currentFilteredPosition();
  const nextPos = pos + delta;
  if (pos < 0 || nextPos < 0 || nextPos >= filteredRows.length) return;
  applyDetailInputsToSelectedRow();
  selectedIndex = filteredRows[nextPos].index;
  renderGrid();
  openDetail(selectedIndex, true);
}

function markdownEscape(value) {
  return String(value ?? '').replace(/\r?\n/g, '<br>').replace(/\|/g, '\\|');
}

function isConstraintLike(row) {
  return row && (row.constraint_id || row.statement || row.review_check || row.user_comment);
}

function rowToConstraintMarkdown(row, fields, no) {
  const id = row.constraint_id ?? row.id ?? `ROW-${no}`;
  const title = row.title ?? row.caption ?? row.name ?? '';
  const lines = [];
  lines.push(`## ${id}${title ? '：' + title : ''}`);
  if (row.category) lines.push(`- 分類: ${row.category}`);
  if (row.priority) lines.push(`- 優先度: ${row.priority}`);
  if (row.source_type) lines.push(`- 由来: ${row.source_type}`);
  if (row.review_check) lines.push(`- 承認: ${row.review_check}`);
  if (row.statement) lines.push(`\n### 制約\n${row.statement}`);
  if (row.evidence) lines.push(`\n### 根拠\n${row.evidence}`);
  if (row.user_comment) lines.push(`\n### 俺コメント\n${row.user_comment}`);
  if (row.ai_note) lines.push(`\n### AIメモ\n${row.ai_note}`);
  const known = new Set(['no','constraint_id','id','title','caption','name','category','priority','source_type','review_check','statement','evidence','user_comment','ai_note','gap_type']);
  const extras = fields.filter(f => !known.has(f.field)).map(f => [f.caption ?? f.field, getByPath(row, f.field)]).filter(([,v]) => v != null && v !== '');
  if (extras.length) {
    lines.push('\n### その他');
    extras.forEach(([k,v]) => lines.push(`- ${k}: ${formatValue(v)}`));
  }
  return lines.join('\n') + '\n';
}

function rowsToTableMarkdown(rows, fields) {
  const visibleFields = fields.filter(f => f.grid?.visible !== false).slice(0, 8);
  const head = '| ' + visibleFields.map(f => markdownEscape(f.caption ?? f.field)).join(' | ') + ' |';
  const sep = '| ' + visibleFields.map(() => '---').join(' | ') + ' |';
  const body = rows.map(row => '| ' + visibleFields.map(f => markdownEscape(formatValue(getByPath(row, f.field), f))).join(' | ') + ' |');
  return [head, sep, ...body].join('\n');
}

function markdownConfig() {
  return viewDef?.markdown || mainView()?.markdown || gridDef()?.markdown || {};
}

function markdownExportType() {
  return String(markdownConfig()?.type ?? markdownConfig()?.exportType ?? 'auto').trim();
}

function markdownValueBlock(value) {
  if (value == null || value === '') return '';
  if (Array.isArray(value) || (typeof value === 'object' && value !== null)) {
    return '```json\n' + JSON.stringify(value, null, 2) + '\n```';
  }
  return String(value);
}

function pushMarkdownValue(lines, label, value, field=null) {
  if (value == null || value === '') return;
  if (Array.isArray(value) || (typeof value === 'object' && value !== null)) {
    lines.push(`- ${label}:`);
    lines.push(markdownValueBlock(value));
  } else {
    lines.push(`- ${label}: ${formatValue(value, field)}`);
  }
}

function rowsToTableMarkdownWithFields(rows, fields, limit=12) {
  const visibleFields = fields.filter(f => f.grid?.visible !== false).slice(0, limit);
  const head = '| ' + visibleFields.map(f => markdownEscape(f.caption ?? f.field)).join(' | ') + ' |';
  const sep = '| ' + visibleFields.map(() => '---').join(' | ') + ' |';
  const body = rows.map(row => '| ' + visibleFields.map(f => markdownEscape(formatValue(getByPath(row, f.field), f))).join(' | ') + ' |');
  return [head, sep, ...body].join('\n');
}

function buildGenericMarkdown() {
  const gd = gridDef();
  const hd = headerDef();
  const rows = Array.isArray(currentRows) ? currentRows : [];
  const cfg = markdownConfig();
  const title = cfg.title || sourceData?.title || mainView()?.caption || gd?.caption || 'No-Code JSON Studio Export';
  const lines = [];
  lines.push(`# ${title}`);
  lines.push('');
  lines.push(`- 出力日時: ${new Date().toLocaleString('ja-JP')}`);
  if (sourceData?.target) lines.push(`- 対象: ${sourceData.target}`);
  if (sourceData?.schema_version) lines.push(`- schema_version: ${sourceData.schema_version}`);
  if (sourceData?.status) lines.push(`- status: ${sourceData.status}`);
  lines.push(`- 件数: ${rows.length}`);
  if (hd?.fields?.length) {
    lines.push('\n## 基本情報');
    hd.fields.forEach(f => {
      const fullPath = (hd.dataPath === '$' ? '$.' : hd.dataPath + '.') + f.field;
      const v = getByPath(sourceData, fullPath);
      if (v != null && v !== '' && typeof v !== 'object') lines.push(`- ${f.caption ?? f.field}: ${formatValue(v, f)}`);
    });
  }
  lines.push('\n---\n');
  if (rows.length && rows.every(isConstraintLike)) {
    rows.forEach((row, i) => lines.push(rowToConstraintMarkdown(row, gd.fields, i + 1)));
  } else {
    lines.push(`## ${gd.caption ?? '一覧'}`);
    lines.push(rowsToTableMarkdown(rows, gd.fields));
  }
  return lines.join('\n');
}

function buildScreenStateExpectedMarkdown() {
  const gd = gridDef();
  const rows = Array.isArray(currentRows) ? currentRows : [];
  const title = sourceData?.title || sourceData?.testId || 'Screen State Expected';
  const lines = [];
  lines.push(`# ${title}`);
  lines.push('');
  lines.push('## 基本情報');
  pushMarkdownValue(lines, '出力日時', new Date().toLocaleString('ja-JP'));
  pushMarkdownValue(lines, 'Test ID', sourceData?.testId);
  pushMarkdownValue(lines, '画面定義', sourceData?.view_def || lastLoadedDefName);
  pushMarkdownValue(lines, 'チェック数', rows.length);
  if (sourceData?.memo) pushMarkdownValue(lines, 'メモ', sourceData.memo);

  lines.push('\n## チェック定義一覧');
  lines.push(rowsToTableMarkdownWithFields(rows, gd.fields, 8));

  if (rows.length) {
    lines.push('\n## チェック詳細');
    rows.forEach((row, i) => {
      lines.push(`\n### ${i + 1}. ${row.name ?? 'check'}`);
      pushMarkdownValue(lines, 'Type', row.type);
      pushMarkdownValue(lines, 'Target', row.target);
      if (row.expected != null && row.expected !== '') {
        lines.push('\n#### Expected');
        lines.push(markdownValueBlock(row.expected));
      }
      if (row.description) {
        lines.push('\n#### 説明');
        lines.push(String(row.description));
      }
    });
  }
  return lines.join('\n');
}

function buildScreenStateDiffMarkdown() {
  const gd = gridDef();
  const rows = Array.isArray(currentRows) ? currentRows : [];
  const failedRows = rows.filter(row => valueIsFail(row?.pass) || valueIsFail(row?.status));
  const result = sourceData?.resultLabel || sourceData?.status || (failedRows.length ? 'FAIL' : 'PASS');
  const title = sourceData?.title || sourceData?.testId || 'Screen State Diff';
  const lines = [];
  lines.push(`# ${title} — ${result}`);
  lines.push('');
  lines.push('## テスト結果サマリ');
  pushMarkdownValue(lines, '出力日時', new Date().toLocaleString('ja-JP'));
  pushMarkdownValue(lines, '判定', result);
  pushMarkdownValue(lines, 'Test ID', sourceData?.testId);
  pushMarkdownValue(lines, '取得日時', sourceData?.capturedAt);
  pushMarkdownValue(lines, 'URL', sourceData?.url);
  pushMarkdownValue(lines, '失敗件数', sourceData?.failedCount ?? failedRows.length);
  if (sourceData?.summary) {
    lines.push('\n### 差分サマリ');
    lines.push(String(sourceData.summary));
  }
  if (sourceData?.failedChecks?.length) pushMarkdownValue(lines, '失敗チェッカー一覧', sourceData.failedChecks);

  if (sourceData?.firstFailure) {
    lines.push('\n## 初回失敗');
    pushMarkdownValue(lines, 'Check', sourceData.firstFailure.name);
    pushMarkdownValue(lines, 'Expected', sourceData.firstFailure.expected);
    pushMarkdownValue(lines, 'Actual', sourceData.firstFailure.actual);
  }

  lines.push('\n## チェッカー結果一覧');
  lines.push(rowsToTableMarkdownWithFields(rows, gd.fields, 10));

  if (failedRows.length) {
    lines.push('\n## 失敗チェック詳細');
    failedRows.forEach((row, i) => {
      lines.push(`\n### ${i + 1}. ${row.name ?? 'check'}`);
      pushMarkdownValue(lines, 'Type', row.type);
      pushMarkdownValue(lines, 'Target', row.target);
      pushMarkdownValue(lines, 'Message', row.message);
      if (hasMissingItems(row.missing)) pushMarkdownValue(lines, 'Missing', row.missing);
      if (row.expected != null && row.expected !== '') {
        lines.push('\n#### Expected');
        lines.push(markdownValueBlock(row.expected));
      }
      if (row.actual != null && row.actual !== '') {
        lines.push('\n#### Actual');
        lines.push(markdownValueBlock(row.actual));
      }
    });
  }
  return lines.join('\n');
}

function buildScreenStateTestPatternsMarkdown() {
  const gd = gridDef();
  const rows = Array.isArray(currentRows) ? currentRows : [];
  const title = sourceData?.title || sourceData?.suiteId || '画面状態JSON テストパターン台帳';
  const lines = [];
  lines.push(`# ${title}`);
  lines.push('');
  lines.push('## 基本情報');
  pushMarkdownValue(lines, '出力日時', new Date().toLocaleString('ja-JP'));
  pushMarkdownValue(lines, 'Suite ID', sourceData?.suiteId);
  pushMarkdownValue(lines, 'Schema', sourceData?.schema_version);
  pushMarkdownValue(lines, '対象アプリ', sourceData?.targetApp);
  pushMarkdownValue(lines, 'Base URL', sourceData?.baseUrl);
  pushMarkdownValue(lines, 'パターン数', rows.length);
  if (sourceData?.memo) {
    lines.push('\n### メモ');
    lines.push(String(sourceData.memo));
  }

  lines.push('\n## テストパターン一覧');
  const tableFields = (gd.fields ?? []).filter(f => [
    'enabled', 'patternId', 'title', 'category', 'testKind', 'targetUrl', 'expectedFile', 'status', 'priority', 'checksCount', 'my_confirm_status'
  ].includes(f.field));
  lines.push(rowsToTableMarkdownWithFields(rows, tableFields.length ? tableFields : gd.fields, 12));

  if (rows.length) {
    lines.push('\n## パターン詳細');
    rows.forEach((row, i) => {
      lines.push(`\n### ${i + 1}. ${row.patternId ?? 'pattern'}：${row.title ?? ''}`);
      pushMarkdownValue(lines, '有効', row.enabled);
      pushMarkdownValue(lines, 'Category', row.category);
      pushMarkdownValue(lines, 'Kind', row.testKind);
      pushMarkdownValue(lines, 'URL', row.targetUrl);
      pushMarkdownValue(lines, 'Expected JSON', row.expectedFile);
      pushMarkdownValue(lines, 'Status', row.status);
      pushMarkdownValue(lines, 'Priority', row.priority);
      pushMarkdownValue(lines, '確認状態', row.my_confirm_status);
      if (row.notes) {
        lines.push('\n#### メモ');
        lines.push(String(row.notes));
      }
      if (row.user_comment) {
        lines.push('\n#### 俺コメント');
        lines.push(String(row.user_comment));
      }
      if (row.ai_response) {
        lines.push('\n#### AI回答');
        lines.push(String(row.ai_response));
      }
      if (row.user_reply) {
        lines.push('\n#### 俺追加回答');
        lines.push(String(row.user_reply));
      }
      if (row.ai_followup_response) {
        lines.push('\n#### AI再回答');
        lines.push(String(row.ai_followup_response));
      }
      if (Array.isArray(row.checks) && row.checks.length) {
        lines.push('\n#### チェック定義');
        lines.push(markdownValueBlock(row.checks));
      }
    });
  }
  return lines.join('\n');
}


function markdownHeading(level, title) {
  const lv = Math.max(1, Math.min(6, Number(level) || 2));
  return `${'#'.repeat(lv)} ${title}`;
}

function markdownIsBlank(value) {
  if (value == null) return true;
  if (Array.isArray(value)) return value.length === 0;
  if (typeof value === 'object') return Object.keys(value).length === 0;
  return String(value).trim() === '';
}

function markdownFieldConfig(field) {
  if (typeof field === 'string') return { field };
  return field ?? {};
}

function markdownLookupField(fieldName) {
  const gd = gridDef();
  const hd = headerDef();
  return (gd?.fields ?? []).find(f => f.field === fieldName) ||
         (hd?.fields ?? []).find(f => f.field === fieldName) ||
         null;
}

function markdownLabelForField(fieldCfg) {
  const cfg = markdownFieldConfig(fieldCfg);
  const def = markdownLookupField(cfg.field);
  return cfg.caption || cfg.label || def?.caption || cfg.field || '';
}

function markdownFormatDataValue(value, fieldCfg=null) {
  const cfg = markdownFieldConfig(fieldCfg);
  const def = markdownLookupField(cfg.field);
  if (value == null) return '';
  if (Array.isArray(value) || (typeof value === 'object' && value !== null)) {
    return JSON.stringify(value, null, 2);
  }
  return formatValue(value, def || cfg);
}

function markdownBlockquote(value) {
  return String(value ?? '')
    .split(/\r?\n/)
    .map(line => `> ${line}`)
    .join('\n');
}

function markdownApplyTemplate(template, row, index=0) {
  return String(template ?? '')
    .replace(/\{#\}/g, String(index + 1))
    .replace(/\{index\}/g, String(index))
    .replace(/\{no\}/g, String(row?.no ?? index + 1))
    .replace(/\{([^}]+)\}/g, (_, path) => {
      const value = getByPath(row, path.trim());
      return value == null ? '' : String(value);
    })
    .replace(/\s+/g, ' ')
    .trim();
}

function pushGenericMarkdownField(lines, obj, fieldCfg, level=3) {
  const cfg = markdownFieldConfig(fieldCfg);
  if (!cfg.field) return;
  const value = getByPath(obj, cfg.field);
  if (cfg.visible === false) return;
  if (markdownIsBlank(value) && cfg.showEmpty !== true) return;

  const label = markdownLabelForField(cfg);
  const format = cfg.format || cfg.markdownFormat || 'auto';

  if (format === 'heading') {
    lines.push(markdownHeading(level, markdownFormatDataValue(value, cfg)));
    return;
  }

  if (format === 'blockquote') {
    lines.push(`\n${markdownHeading(level, label)}`);
    lines.push('');
    lines.push(markdownBlockquote(markdownFormatDataValue(value, cfg)));
    return;
  }

  if (format === 'paragraph' || format === 'textarea' || String(value).includes('\n')) {
    lines.push(`\n${markdownHeading(level, label)}`);
    lines.push('');
    lines.push(markdownFormatDataValue(value, cfg));
    return;
  }

  if (Array.isArray(value) || (typeof value === 'object' && value !== null)) {
    lines.push(`- ${label}:`);
    lines.push(markdownValueBlock(value));
    return;
  }

  lines.push(`- ${label}: ${markdownEscape(markdownFormatDataValue(value, cfg))}`);
}

function markdownObjectTable(items, fields) {
  const list = Array.isArray(items) ? items : [];
  const fieldCfgs = (fields ?? []).map(markdownFieldConfig).filter(f => f.field);
  if (!fieldCfgs.length) return '';
  const head = '| ' + fieldCfgs.map(f => markdownEscape(markdownLabelForField(f))).join(' | ') + ' |';
  const sep = '| ' + fieldCfgs.map(() => '---').join(' | ') + ' |';
  const body = list.map(item => '| ' + fieldCfgs.map(f => markdownEscape(markdownFormatDataValue(getByPath(item, f.field), f))).join(' | ') + ' |');
  return [head, sep, ...body].join('\n');
}

function renderMarkdownArray(lines, arrayValue, section, level=3) {
  const items = Array.isArray(arrayValue) ? arrayValue : [];
  if (!items.length) {
    if (section.showEmpty === true) lines.push('（なし）');
    return;
  }

  const format = section.format || 'table';
  const fields = section.fields ?? [];

  if (format === 'constraintList' || format === 'detailList') {
    items.forEach((item, index) => {
      const titleTpl = section.itemTitle || (format === 'constraintList' ? '{id}：{title}' : '{#}. {title}');
      const title = markdownApplyTemplate(titleTpl, item, index) || `${index + 1}`;
      lines.push(`\n${markdownHeading(level, title)}`);
      const fieldCfgs = fields.map(markdownFieldConfig).filter(f => f.field);
      if (fieldCfgs.length) {
        fieldCfgs.forEach(f => pushGenericMarkdownField(lines, item, f, level + 1));
      } else {
        lines.push(markdownValueBlock(item));
      }
    });
    return;
  }

  if (format === 'json') {
    lines.push(markdownValueBlock(items));
    return;
  }

  const table = markdownObjectTable(items, fields);
  if (table) lines.push(table);
  else lines.push(markdownValueBlock(items));
}

function renderGenericMarkdownSection(lines, section, context={ data: sourceData, rows: currentRows }, level=2) {
  if (!section || section.visible === false) return;
  const title = section.title || section.caption;
  if (title) {
    lines.push(`\n${markdownHeading(level, title)}`);
    lines.push('');
  }

  const source = section.source || 'root';
  if (source === 'rows' || source === 'currentRows' || source === 'grid') {
    const rows = Array.isArray(context.rows) ? context.rows : [];
    if (section.format === 'table') {
      lines.push(markdownObjectTable(rows, section.fields ?? []));
      return;
    }

    rows.forEach((row, index) => {
      const itemTitle = markdownApplyTemplate(section.itemTitle || '{no}. {group_id}：{title}', row, index) || `${index + 1}`;
      lines.push(`\n${markdownHeading(level + 1, itemTitle)}`);
      (section.fields ?? []).forEach(f => pushGenericMarkdownField(lines, row, f, level + 2));
      (section.sections ?? []).forEach(child => renderGenericMarkdownSection(lines, child, { data: row, rows: context.rows }, level + 2));
    });
    return;
  }

  const obj = context.data ?? sourceData;

  if (section.arrayField) {
    const arrayValue = getByPath(obj, section.arrayField);
    renderMarkdownArray(lines, arrayValue, section, level + 1);
    return;
  }

  (section.fields ?? []).forEach(f => pushGenericMarkdownField(lines, obj, f, level + 1));
  (section.sections ?? []).forEach(child => renderGenericMarkdownSection(lines, child, { data: obj, rows: context.rows }, level + 1));
}

function buildGenericSectionsMarkdown() {
  applyHeaderEdits();
  const cfg = markdownConfig();
  const gd = gridDef();
  const rows = Array.isArray(currentRows) ? currentRows : [];
  const title = cfg.title || sourceData?.title || mainView()?.caption || gd?.caption || 'No-Code JSON Studio Export';
  const lines = [];

  lines.push(`# ${title}`);
  lines.push('');
  lines.push(`- 出力日時: ${new Date().toLocaleString('ja-JP')}`);
  if (sourceData?.target) lines.push(`- 対象: ${sourceData.target}`);
  if (sourceData?.schema_version) lines.push(`- schema_version: ${sourceData.schema_version}`);
  if (sourceData?.status) lines.push(`- status: ${sourceData.status}`);
  lines.push(`- 件数: ${rows.length}`);

  const sections = Array.isArray(cfg.sections) ? cfg.sections : [];
  if (!sections.length) return buildGenericMarkdown();

  sections.forEach(section => renderGenericMarkdownSection(lines, section, { data: sourceData, rows }, 2));
  return lines.join('\n').replace(/\n{4,}/g, '\n\n\n');
}

function buildMarkdownFromCurrentData() {
  applyHeaderEdits();
  const type = markdownExportType();
  if (type === 'screen_state_expected') return buildScreenStateExpectedMarkdown();
  if (type === 'screen_state_diff') return buildScreenStateDiffMarkdown();
  if (type === 'screen_state_test_patterns') return buildScreenStateTestPatternsMarkdown();
  if (type === 'generic_sections') return buildGenericSectionsMarkdown();
  return buildGenericMarkdown();
}

function downloadTextFile(filename, text, type='text/markdown') {
  const blob = new Blob([text], {type});
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = filename;
  a.click();
  URL.revokeObjectURL(a.href);
}

function normalizeMarkdownFileName(name) {
  let n = String(name || '').trim();
  if (!n) n = 'json_studio_export.md';
  n = n.replace(/[\\/:*?"<>|]/g, '_');
  if (!/\.(md|markdown)$/i.test(n)) n += '.md';
  return n;
}

function currentDataNameForExport() {
  const fromCombo = $('dataNameInput')?.value;
  if (fromCombo) return fromCombo.split('/').pop();
  const fromApi = currentDataApiUrl ? jsonNameFromUrl(currentDataApiUrl, 'data') : null;
  if (fromApi) return fromApi.split('/').pop();
  return null;
}

function markdownExportFileName() {
  const cfg = markdownConfig();
  const base =
    sourceData?.export_md_name ||
    sourceData?.markdown_file ||
    cfg.fileName ||
    cfg.filename ||
    cfg.defaultFileName ||
    sourceData?.title ||
    currentDataNameForExport() ||
    'json_studio_export';
  const clean = normalizeMarkdownFileName(String(base).replace(/\.json$/i, ''));
  return clean;
}

async function saveMarkdownToManagedFolder(filename, content) {
  const safeName = normalizeMarkdownFileName(filename);
  const res = await fetch(`/api/markdown/${encodeURIComponent(safeName)}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name: safeName, content })
  });
  if (!res.ok) throw new Error(await res.text());
  return safeName;
}

async function exportMarkdown() {
  if (!sourceData || !viewDef) {
    setStatus('Markdown出力するデータがありません');
    return;
  }
  const md = buildMarkdownFromCurrentData();
  const fileName = markdownExportFileName();
  try {
    const savedName = await saveMarkdownToManagedFolder(fileName, md);
    setStatus(`Markdownを data/markdown/${savedName} に出力しました`);
    location.href = `mdViewer.html?file=${encodeURIComponent(savedName)}`;
  } catch (err) {
    console.warn('管理Markdown保存に失敗。ダウンロードへフォールバックします。', err);
    downloadTextFile(fileName, md);
    setStatus('Markdown API保存に失敗したため、ダウンロード出力しました: ' + err.message);
  }
}

function viewDefMarkdownDisplay(value) {
  if (value == null || value === '') return '';
  if (Array.isArray(value)) return value.length ? value.join(', ') : '[]';
  if (typeof value === 'object') return JSON.stringify(value);
  return String(value);
}

function markdownJsonBlock(value) {
  return '```json\n' + JSON.stringify(value ?? {}, null, 2).replace(/```/g, '`\u200b``') + '\n```';
}

function viewDefViews(defObj) {
  if (Array.isArray(defObj?.views)) return defObj.views;
  return defObj ? [defObj] : [];
}

function viewDefSections(view) {
  return Array.isArray(view?.sections) ? view.sections : [];
}

function viewDefFields(section) {
  return Array.isArray(section?.fields) ? section.fields : [];
}

function viewDefFieldVisibleText(field, area='grid') {
  const areaObj = field?.[area] ?? {};
  if (areaObj.visible === false) return 'false';
  if (areaObj.visible === true) return 'true';
  if (area === 'edit' && field?.readonly === true && areaObj.visible == null) return '';
  return '';
}

function viewDefFieldReadonlyText(field) {
  if (field?.readonly === true || field?.edit?.readonly === true) return 'true';
  if (field?.readonly === false || field?.edit?.readonly === false) return 'false';
  return '';
}

function viewDefFieldSearchText(field) {
  if (!field?.search) return '';
  if (field.search.visible === false) return 'false';
  return field.search.operator ? `true (${field.search.operator})` : 'true';
}

function viewDefFieldOptionsText(field) {
  const options = field?.options;
  if (!Array.isArray(options) || !options.length) return '';
  return options.slice(0, 8).join(', ') + (options.length > 8 ? ` ... +${options.length - 8}` : '');
}

function viewDefFieldTableMarkdown(fields) {
  const header = '| field | caption | type | grid.visible | width | edit.visible | readonly | search | options |';
  const sep = '| --- | --- | --- | --- | ---: | --- | --- | --- | --- |';
  const body = (fields ?? []).map(f => {
    return '| ' + [
      f.field,
      f.caption,
      f.type ?? 'text',
      viewDefFieldVisibleText(f, 'grid'),
      f.grid?.width ?? '',
      viewDefFieldVisibleText(f, 'edit'),
      viewDefFieldReadonlyText(f),
      viewDefFieldSearchText(f),
      viewDefFieldOptionsText(f)
    ].map(markdownEscape).join(' | ') + ' |';
  });
  return [header, sep, ...body].join('\n');
}

function viewDefSummaryTableMarkdown(defObj) {
  const rows = [];
  viewDefViews(defObj).forEach((view, viewIndex) => {
    viewDefSections(view).forEach((section, sectionIndex) => {
      rows.push({
        view: view.id ?? `view[${viewIndex}]`,
        viewCaption: view.caption ?? '',
        section: section.id ?? `section[${sectionIndex}]`,
        sectionCaption: section.caption ?? '',
        type: section.type ?? '',
        dataPath: section.dataPath ?? '',
        keyField: section.keyField ?? '',
        fields: viewDefFields(section).length
      });
    });
  });

  const header = '| View | View Caption | Section | Section Caption | Type | DataPath | KeyField | Fields |';
  const sep = '| --- | --- | --- | --- | --- | --- | --- | ---: |';
  const body = rows.map(r => '| ' + [
    r.view, r.viewCaption, r.section, r.sectionCaption, r.type, r.dataPath, r.keyField, r.fields
  ].map(markdownEscape).join(' | ') + ' |');
  return [header, sep, ...body].join('\n');
}

function viewDefDetailMarkdown(defObj, titlePrefix='') {
  const lines = [];
  viewDefViews(defObj).forEach((view, viewIndex) => {
    const viewTitle = view.caption || view.id || `view[${viewIndex}]`;
    lines.push(`\n## ${titlePrefix}${viewTitle}`);
    lines.push('');
    lines.push(`- view.id: ${viewDefMarkdownDisplay(view.id ?? `view[${viewIndex}]`)}`);
    if (view.layout) lines.push(`- layout: ${viewDefMarkdownDisplay(view.layout)}`);
    if (view.markdown?.type) lines.push(`- markdown.type: ${viewDefMarkdownDisplay(view.markdown.type)}`);
    if (view.markdown?.title) lines.push(`- markdown.title: ${viewDefMarkdownDisplay(view.markdown.title)}`);
    if (view.markdown?.defaultFileName) lines.push(`- markdown.defaultFileName: ${viewDefMarkdownDisplay(view.markdown.defaultFileName)}`);

    viewDefSections(view).forEach((section, sectionIndex) => {
      const sectionTitle = section.caption || section.id || `section[${sectionIndex}]`;
      lines.push(`\n### ${sectionTitle}`);
      lines.push('');
      lines.push(`- section.id: ${viewDefMarkdownDisplay(section.id ?? `section[${sectionIndex}]`)}`);
      if (section.type) lines.push(`- type: ${viewDefMarkdownDisplay(section.type)}`);
      if (section.dataPath) lines.push(`- dataPath: ${viewDefMarkdownDisplay(section.dataPath)}`);
      if (section.keyField) lines.push(`- keyField: ${viewDefMarkdownDisplay(section.keyField)}`);
      const fields = viewDefFields(section);
      lines.push(`- fields: ${fields.length}`);
      if (fields.length) {
        lines.push('');
        lines.push(viewDefFieldTableMarkdown(fields));
      }
    });
  });
  return lines.join('\n');
}

async function loadRawViewDefForMarkdown() {
  const droppedDefFile = $('defFile')?.files?.[0] ?? null;
  if (droppedDefFile) {
    try {
      return {
        name: safeJsonFileName(droppedDefFile.name) || droppedDefFile.name || 'dropped_view_def.json',
        json: JSON.parse(await droppedDefFile.text()),
        source: 'drop'
      };
    } catch (err) {
      console.warn('ViewDef drop read skipped:', err);
    }
  }

  const name = safeJsonFileName(lastLoadedDefName || $('defNameInput')?.value);
  if (!name) return null;
  try {
    const loaded = await fetchApiJsonWithUrl('defs', name);
    return {
      name: loaded.correctedName || jsonNameFromUrl(loaded.url, 'defs') || name,
      json: loaded.json,
      source: 'api'
    };
  } catch (err) {
    console.warn('ViewDef raw load skipped:', err);
    return null;
  }
}


async function resolveViewDefParentsOnly(defObj, currentName=null, stack=[]) {
  const parents = normalizeExtendsValue(defObj?.extends);
  if (!parents.length) return null;

  const current = safeJsonFileName(currentName) || '(dropped view_def)';
  let merged = {};

  for (const parentRaw of parents) {
    const parentName = resolveRelativeJsonName(parentRaw, currentName);
    if (!parentName) throw new Error(`extends の指定が不正です: ${parentRaw}`);
    if (stack.includes(parentName)) {
      throw new Error(`ViewDef継承が循環しています: ${[...stack, parentName].join(' -> ')}`);
    }

    const parentResolved = await fetchResolvedViewDef(parentName, [...stack, current]);
    merged = mergeViewDefObject(merged, parentResolved);
  }

  return merged;
}

function viewDefDiffKey(item, index, fallbackPrefix='item') {
  return String(item?.id ?? item?.field ?? item?.name ?? `${fallbackPrefix}[${index}]`);
}

function viewDefMapByKey(items, fallbackPrefix='item') {
  const map = new Map();
  (items ?? []).forEach((item, index) => map.set(viewDefDiffKey(item, index, fallbackPrefix), item));
  return map;
}

function viewDefDiffValue(value) {
  if (value === undefined) return '（未定義）';
  if (value === null) return 'null';
  if (value === '') return '（空）';
  if (Array.isArray(value)) return value.length ? JSON.stringify(value) : '[]';
  if (typeof value === 'object') return JSON.stringify(value);
  return String(value);
}

function viewDefComparable(value) {
  if (value === undefined) return '__FRB_UNDEFINED__';
  if (Array.isArray(value)) return value.map(viewDefComparable);
  if (value && typeof value === 'object') {
    const out = {};
    Object.keys(value).sort().forEach(key => out[key] = viewDefComparable(value[key]));
    return out;
  }
  return value;
}

function viewDefDeepEqual(a, b) {
  return JSON.stringify(viewDefComparable(a)) === JSON.stringify(viewDefComparable(b));
}

function viewDefDiffGet(obj, path) {
  return String(path).split('.').reduce((cur, key) => cur == null ? undefined : cur[key], obj);
}

function pushViewDefPropDiff(rows, scope, target, propPath, parentObj, childObj) {
  const parentValue = viewDefDiffGet(parentObj, propPath);
  const childValue = viewDefDiffGet(childObj, propPath);
  if (viewDefDeepEqual(parentValue, childValue)) return;
  rows.push({
    kind: '変更',
    scope,
    target,
    item: propPath,
    parent: viewDefDiffValue(parentValue),
    child: viewDefDiffValue(childValue)
  });
}

function viewDefShortSummary(obj) {
  if (!obj) return '';
  const parts = [];
  if (obj.caption) parts.push(`caption=${obj.caption}`);
  if (obj.type) parts.push(`type=${obj.type}`);
  if (obj.dataPath) parts.push(`dataPath=${obj.dataPath}`);
  if (obj.keyField) parts.push(`keyField=${obj.keyField}`);
  if (obj.field) parts.push(`field=${obj.field}`);
  if (obj.grid?.visible != null) parts.push(`grid.visible=${obj.grid.visible}`);
  if (obj.grid?.width != null) parts.push(`width=${obj.grid.width}`);
  if (obj.markdown?.type) parts.push(`markdown.type=${obj.markdown.type}`);
  return parts.length ? parts.join(', ') : JSON.stringify(obj);
}

function pushViewDefAddedRemoved(rows, scope, target, kind, obj) {
  rows.push({
    kind,
    scope,
    target,
    item: '全体',
    parent: kind === '追加' ? '（なし）' : viewDefShortSummary(obj),
    child: kind === '削除' ? '（なし）' : viewDefShortSummary(obj)
  });
}

function viewDefDiffTableMarkdown(rows) {
  const header = '| 種別 | 対象 | 項目 | 親BASE | 子CHILD / 解決済み |';
  const sep = '| --- | --- | --- | --- | --- |';
  const body = rows.map(r => '| ' + [r.kind, r.target, r.item, r.parent, r.child].map(markdownEscape).join(' | ') + ' |');
  return [header, sep, ...body].join('\n');
}

function buildViewDefDiffRows(parentDef, childDef) {
  const rowsByScope = { view: [], section: [], field: [] };
  const parentViews = viewDefMapByKey(viewDefViews(parentDef), 'view');
  const childViews = viewDefMapByKey(viewDefViews(childDef), 'view');
  const viewKeys = new Set([...parentViews.keys(), ...childViews.keys()]);

  viewKeys.forEach(viewKey => {
    const parentView = parentViews.get(viewKey);
    const childView = childViews.get(viewKey);
    const viewTarget = `view:${viewKey}`;

    if (!parentView && childView) {
      pushViewDefAddedRemoved(rowsByScope.view, 'view', viewTarget, '追加', childView);
      return;
    }
    if (parentView && !childView) {
      pushViewDefAddedRemoved(rowsByScope.view, 'view', viewTarget, '削除', parentView);
      return;
    }

    ['caption', 'layout', 'markdown.enabled', 'markdown.type', 'markdown.title', 'markdown.defaultFileName', 'markdown.fileName'].forEach(prop => {
      pushViewDefPropDiff(rowsByScope.view, 'view', viewTarget, prop, parentView, childView);
    });

    const parentSections = viewDefMapByKey(viewDefSections(parentView), 'section');
    const childSections = viewDefMapByKey(viewDefSections(childView), 'section');
    const sectionKeys = new Set([...parentSections.keys(), ...childSections.keys()]);

    sectionKeys.forEach(sectionKey => {
      const parentSection = parentSections.get(sectionKey);
      const childSection = childSections.get(sectionKey);
      const sectionTarget = `${viewKey} / section:${sectionKey}`;

      if (!parentSection && childSection) {
        pushViewDefAddedRemoved(rowsByScope.section, 'section', sectionTarget, '追加', childSection);
        return;
      }
      if (parentSection && !childSection) {
        pushViewDefAddedRemoved(rowsByScope.section, 'section', sectionTarget, '削除', parentSection);
        return;
      }

      ['caption', 'type', 'dataPath', 'keyField', 'role'].forEach(prop => {
        pushViewDefPropDiff(rowsByScope.section, 'section', sectionTarget, prop, parentSection, childSection);
      });

      const parentFields = viewDefMapByKey(viewDefFields(parentSection), 'field');
      const childFields = viewDefMapByKey(viewDefFields(childSection), 'field');
      const fieldKeys = new Set([...parentFields.keys(), ...childFields.keys()]);

      fieldKeys.forEach(fieldKey => {
        const parentField = parentFields.get(fieldKey);
        const childField = childFields.get(fieldKey);
        const fieldTarget = `${viewKey} / ${sectionKey} / field:${fieldKey}`;

        if (!parentField && childField) {
          pushViewDefAddedRemoved(rowsByScope.field, 'field', fieldTarget, '追加', childField);
          return;
        }
        if (parentField && !childField) {
          pushViewDefAddedRemoved(rowsByScope.field, 'field', fieldTarget, '削除', parentField);
          return;
        }

        [
          'caption', 'type', 'readonly', 'format',
          'grid.visible', 'grid.width', 'grid.format', 'grid.align',
          'edit.visible', 'edit.readonly', 'edit.height', 'edit.control', 'edit.placement', 'edit.layout.placement',
          'search.visible', 'search.operator',
          'options'
        ].forEach(prop => {
          pushViewDefPropDiff(rowsByScope.field, 'field', fieldTarget, prop, parentField, childField);
        });
      });
    });
  });

  return rowsByScope;
}

function buildViewDefInheritanceDiffMarkdown(parentDef=null, childDef=null, rawExtends=[]) {
  const lines = [];
  lines.push('\n## 継承差分サマリ');
  lines.push('');

  if (!rawExtends.length) {
    lines.push('このViewDefは extends を持たないため、継承差分はありません。');
    return lines.join('\n');
  }

  lines.push(`- 継承元: ${rawExtends.join(' / ')}`);

  if (!parentDef || !childDef) {
    lines.push('- 継承差分: 親ViewDefまたは解決済みViewDefを取得できなかったため、差分を作成できませんでした。');
    return lines.join('\n');
  }

  const rowsByScope = buildViewDefDiffRows(parentDef, childDef);
  const allRows = [...rowsByScope.view, ...rowsByScope.section, ...rowsByScope.field];
  const changed = allRows.filter(r => r.kind === '変更').length;
  const added = allRows.filter(r => r.kind === '追加').length;
  const removed = allRows.filter(r => r.kind === '削除').length;

  lines.push(`- 差分件数: ${allRows.length}`);
  lines.push(`- 内訳: 変更 ${changed} / 追加 ${added} / 削除 ${removed}`);

  if (!allRows.length) {
    lines.push('');
    lines.push('親BASEとの差分は検出されませんでした。');
    return lines.join('\n');
  }

  if (rowsByScope.view.length) {
    lines.push('\n### View差分');
    lines.push(viewDefDiffTableMarkdown(rowsByScope.view));
  }
  if (rowsByScope.section.length) {
    lines.push('\n### Section差分');
    lines.push(viewDefDiffTableMarkdown(rowsByScope.section));
  }
  if (rowsByScope.field.length) {
    lines.push('\n### Field差分');
    lines.push(viewDefDiffTableMarkdown(rowsByScope.field));
  }

  return lines.join('\n');
}

function viewDefMarkdownExportFileName(rawInfo=null) {
  const sourceName = rawInfo?.name || lastLoadedDefName || $('defNameInput')?.value || mainView()?.id || 'view_def';
  const base = String(sourceName).split('/').pop().replace(/\.json$/i, '') + '_viewdef';
  return normalizeMarkdownFileName(base);
}

function buildViewDefMarkdown(rawInfo=null, resolvedOverride=null, parentResolvedOverride=null) {
  const rawDef = rawInfo?.json ?? null;
  const resolvedDef = resolvedOverride || viewDef || rawDef;
  const baseDef = rawDef || resolvedDef;
  const main = mainViewOf(baseDef);
  const title = main?.caption || rawInfo?.name || lastLoadedDefName || 'ViewDef Definition';
  const rawExtends = normalizeExtendsValue(rawDef?.extends);
  const resolvedExtends = normalizeExtendsValue(resolvedDef?._resolved_extends);
  const lines = [];

  lines.push(`# ViewDef定義レポート — ${title}`);
  lines.push('');
  lines.push('## 基本情報');
  lines.push(`- 出力日時: ${new Date().toLocaleString('ja-JP')}`);
  lines.push(`- 対象ViewDef: ${viewDefMarkdownDisplay(rawInfo?.name || lastLoadedDefName || $('defNameInput')?.value || '(dropped / resolved)')}`);
  if (rawDef?.app?.name || resolvedDef?.app?.name) lines.push(`- app.name: ${viewDefMarkdownDisplay(rawDef?.app?.name || resolvedDef?.app?.name)}`);
  if (rawDef?.app?.version || resolvedDef?.app?.version) lines.push(`- app.version: ${viewDefMarkdownDisplay(rawDef?.app?.version || resolvedDef?.app?.version)}`);
  if (rawExtends.length) lines.push(`- extends(raw): ${rawExtends.join(' / ')}`);
  if (resolvedExtends.length) lines.push(`- extends(resolved): ${resolvedExtends.join(' / ')}`);
  lines.push(`- views: ${viewDefViews(baseDef).length}`);

  lines.push('\n## View / Section 概要');
  lines.push(viewDefSummaryTableMarkdown(baseDef));

  lines.push(buildViewDefInheritanceDiffMarkdown(parentResolvedOverride, resolvedDef, rawExtends));

  lines.push(viewDefDetailMarkdown(baseDef));

  if (rawDef && resolvedDef && rawExtends.length) {
    lines.push('\n---\n');
    lines.push('## 解決済みViewDef概要');
    lines.push('');
    lines.push('このViewDefは extends を持つため、現在画面描画に使っている解決済みViewDefの概要も併記します。');
    lines.push('');
    lines.push(viewDefSummaryTableMarkdown(resolvedDef));
    lines.push(viewDefDetailMarkdown(resolvedDef, 'Resolved: '));
  }

  lines.push('\n---\n');
  lines.push('## ViewDef JSON');
  lines.push('');
  lines.push('<details>');
  lines.push('<summary>元ViewDef JSONを表示</summary>');
  lines.push('');
  lines.push(markdownJsonBlock(rawDef || resolvedDef));
  lines.push('');
  lines.push('</details>');

  if (rawDef && resolvedDef && rawExtends.length) {
    lines.push('');
    lines.push('<details>');
    lines.push('<summary>解決済みViewDef JSONを表示</summary>');
    lines.push('');
    lines.push(markdownJsonBlock(resolvedDef));
    lines.push('');
    lines.push('</details>');
  }

  return lines.join('\n');
}

async function exportViewDefMarkdown() {
  const rawInfo = await loadRawViewDefForMarkdown();
  if (!rawInfo && !viewDef) {
    setStatus('ViewDef Markdown出力する画面定義がありません。画面定義JSONを選択するかDropしてください。');
    return;
  }

  let resolvedForReport = viewDef || null;
  let parentResolvedForReport = null;
  if (rawInfo?.json) {
    try {
      resolvedForReport = await resolveViewDefInheritance(rawInfo.json, rawInfo.name);
      parentResolvedForReport = await resolveViewDefParentsOnly(rawInfo.json, rawInfo.name);
    } catch (err) {
      console.warn('ViewDef resolved markdown skipped:', err);
      resolvedForReport = viewDef || rawInfo.json;
    }
  }

  const md = buildViewDefMarkdown(rawInfo, resolvedForReport, parentResolvedForReport);
  const fileName = viewDefMarkdownExportFileName(rawInfo);
  try {
    const savedName = await saveMarkdownToManagedFolder(fileName, md);
    setStatus(`ViewDef Markdownを data/markdown/${savedName} に出力しました`);
    location.href = `mdViewer.html?file=${encodeURIComponent(savedName)}`;
  } catch (err) {
    console.warn('ViewDef Markdown保存に失敗。ダウンロードへフォールバックします。', err);
    downloadTextFile(fileName, md);
    setStatus('ViewDef Markdown API保存に失敗したため、ダウンロード出力しました: ' + err.message);
  }
}

function renderDetailForRow(row) {
  const gd = gridDef();
  const pasteBtn = $('pasteCopiedBtn');
  if (pasteBtn) pasteBtn.disabled = !copiedRow;
  const form = $('detailForm');
  form.innerHTML = '';

  detailVisibleFields(gd)
    .filter(field => !isDetailFooterField(field))
    .forEach(field => {
      form.appendChild(createInput(field, getByPath(row, field.field), 'detail', false, row, gd));
    });

  renderChildArea(row, gd);
  renderDetailFooterFields(row, gd);
  updateDetailNavButtons();
}

function openDetail(index, keepOpen=false) {
  detailMode = 'edit';
  draftRow = null;
  selectedIndex = index;
  const row = currentRows[index];
  renderDetailForRow(row);
  if (!keepOpen || !$('detailDialog').open) $('detailDialog').showModal();
}

function openNewDetail(row, statusMessage='新規登録画面を開きました') {
  detailMode = 'new';
  draftRow = row;
  selectedIndex = -1;
  renderGrid();
  renderDetailForRow(draftRow);
  setStatus(statusMessage);
  if (!$('detailDialog').open) $('detailDialog').showModal();
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
  if (e) e.preventDefault();

  if (detailMode === 'new') {
    if (!draftRow || !Array.isArray(currentRows)) return;
    applyDetailInputsToRow(draftRow);
    // 反映直前にもNo/Keyを再採番して、開いている間に増えた行との重複を避ける。
    assignNewRowKeys(draftRow, draftRow);
    currentRows.push(draftRow);
    selectedIndex = currentRows.length - 1;
    detailMode = 'edit';
    draftRow = null;
    applySearch();
    renderGrid();
    updateDetailNavButtons();
    setStatus('新規行を追加して詳細を反映しました');
    openDetail(selectedIndex, true);
    return;
  }

  if (selectedIndex < 0) return;
  applyDetailInputsToSelectedRow();
  renderGrid();
  updateDetailNavButtons();
  setStatus('詳細を反映しました（F7/F8で前後移動できます）');
  // 承認作業では連続レビューしたいので、反映では詳細ダイアログを閉じない。
  // 閉じる場合は「閉じる」ボタンまたは右上×を使う。
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
    const prefix = '/api/data/';
    if (!u.pathname.startsWith(prefix)) return null;
    const rel = decodeURIComponent(u.pathname.slice(prefix.length));
    return safeJsonFileName(rel) ? u.pathname : null;
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
setupComboClearButtons();
setupViewDefMarkdownButtonState();

function loadFromObjects(defObj, dataObj, label='読み込み完了', dataApiUrl=null) {
  if (!isDefCompatibleWithData(defObj, dataObj)) {
    throw new Error(defCompatibilityMessage(lastLoadedDefName, defObj, dataObj));
  }
  viewDef = defObj;
  sourceData = dataObj;
  selectedIndex = -1;
  sortState = { field: null, direction: null };
  copiedRow = null;
  detailMode = 'edit';
  draftRow = null;
  currentDataApiUrl = dataApiUrl;
  if (lastLoadedDefName && $('defNameInput')) $('defNameInput').value = lastLoadedDefName;
  renderHeader();
  renderSearch();
  loadRows();
  renderGrid();
  $('saveBtn').disabled = false;
  if ($('exportMarkdownBtn')) $('exportMarkdownBtn').disabled = false;
  updateViewDefMarkdownButtonState();
  if ($('exportViewDefMarkdownBtn')) $('exportViewDefMarkdownBtn').disabled = false;
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
    const [rawDefObj, dataObj] = await Promise.all([fetchJson(viewUrl), fetchJson(dataUrl)]);
    const normalizedDefName = jsonNameFromUrl(viewUrl, 'defs');
    const defObj = await resolveViewDefInheritance(rawDefObj, normalizedDefName || jsonNameFromUrl(viewUrl));
    lastLoadedDefName = normalizedDefName || getDataViewDefName(dataObj) || null;
    if (lastLoadedDefName && $('defNameInput')) $('defNameInput').value = lastLoadedDefName;
    const normalizedDataName = jsonNameFromUrl(dataUrl, 'data');
    if (normalizedDataName && $('dataNameInput')) $('dataNameInput').value = normalizedDataName;
    ensureViewDefNameInData(dataObj, lastLoadedDefName);
    loadFromObjects(defObj, dataObj, 'URLパラメータから読み込み完了', normalizeApiDataUrl(dataUrl));
  } catch (err) {
    console.error(err);
    setStatus('URL読込エラー: ' + err.message + '（file://直開きの場合はローカルサーバ起動が必要な場合があります）');
  }
}

suppressBrowserAutofillOnComboInputs();
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
if ($('pasteCopiedBtn')) $('pasteCopiedBtn').addEventListener('click', pasteCopiedRowToForm);
$('prevDetailBtn').addEventListener('click', () => moveDetail(-1));
$('nextDetailBtn').addEventListener('click', () => moveDetail(1));
$('exportMarkdownBtn').addEventListener('click', exportMarkdown);
if ($('exportViewDefMarkdownBtn')) $('exportViewDefMarkdownBtn').addEventListener('click', exportViewDefMarkdown);
$('saveBtn').addEventListener('click', async () => {
  try {
    await saveOverwriteJson();
  } catch (err) {
    console.error(err);
    setStatus('保存エラー: ' + err.message);
  }
});

refreshServerLists().finally(async () => {
  await autoLoadFromQuery();
  updateViewDefMarkdownButtonState();
});


window.__NCJS_exportScreenState = function () {
  return {
    appTitle: document.title,
    url: location.href,
    headerText: document.body.innerText.includes("No-Code JSON Studio"),
    buttons: Array.from(document.querySelectorAll("button")).map(b => b.innerText.trim()).filter(Boolean),
    selects: Array.from(document.querySelectorAll("select")).map(s => ({
      id: s.id || "",
      value: s.value || "",
      optionCount: s.options.length
    })),
    inputs: Array.from(document.querySelectorAll("input")).map(i => ({
      id: i.id || "",
      type: i.type || "",
      value: i.value || ""
    }))
  };
};
