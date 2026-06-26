// v0.10-folder-hierarchy: Tree style JSON file picker for data/defs lists.
// The server still returns a flat list of relative JSON paths; this UI builds the tree in the browser.

const fileTreePickerStates = new Map();

function fileTreePickerConfigs() {
  return [
    {
      kind: 'defs',
      inputId: 'defNameInput',
      label: '画面定義JSON',
      names: () => (typeof viewDefSelectionNames === 'function' ? viewDefSelectionNames() : serverDefNames)
    },
    {
      kind: 'data',
      inputId: 'dataNameInput',
      label: '対象JSON',
      names: () => serverDataNames
    }
  ];
}

function setupFileTreePickers() {
  fileTreePickerConfigs().forEach(config => setupFileTreePicker(config));

  document.addEventListener('click', (event) => {
    for (const state of fileTreePickerStates.values()) {
      if (!state.wrap?.contains(event.target)) hideFileTreePicker(state);
    }
  });

  document.addEventListener('keydown', (event) => {
    if (event.key !== 'Escape') return;
    for (const state of fileTreePickerStates.values()) hideFileTreePicker(state);
  });
}

function setupFileTreePicker(config) {
  const input = $(config.inputId);
  if (!input) return;

  // Native datalist cannot display folders nicely. Keep the input, replace only the popup UI.
  input.removeAttribute('list');

  const wrap = input.closest('.combo-input-wrap') || input.parentElement;
  if (!wrap) return;
  wrap.classList.add('file-tree-wrap');
  input.closest('.combo-field')?.classList.add('file-tree-field');

  const picker = document.createElement('div');
  picker.className = 'file-tree-picker hidden';
  picker.setAttribute('role', 'listbox');
  picker.setAttribute('aria-label', `${config.label} ツリー選択`);
  picker.innerHTML = `
    <div class="file-tree-hint">
      <span class="file-tree-hint-main">フォルダー階層で選択</span>
      <span class="file-tree-hint-sub">文字を入力すると相対パス検索</span>
    </div>
    <div class="file-tree-list"></div>
  `;
  wrap.appendChild(picker);

  const state = {
    config,
    input,
    wrap,
    picker,
    list: picker.querySelector('.file-tree-list'),
    expanded: new Set()
  };
  fileTreePickerStates.set(config.inputId, state);

  input.addEventListener('focus', () => showFileTreePicker(state));
  input.addEventListener('click', () => showFileTreePicker(state));
  input.addEventListener('input', () => {
    showFileTreePicker(state);
    renderFileTreePicker(state);
  });
  input.addEventListener('keydown', (event) => {
    if (event.key === 'ArrowDown') {
      event.preventDefault();
      showFileTreePicker(state);
      const first = state.list?.querySelector('.file-tree-file');
      first?.focus();
    }
    if (event.key === 'Enter' && !state.picker.classList.contains('hidden')) {
      const first = state.list?.querySelector('.file-tree-file');
      if (first) {
        event.preventDefault();
        selectFileTreePath(state, first.dataset.path);
      }
    }
  });
}

function refreshFileTreePickers() {
  for (const state of fileTreePickerStates.values()) {
    renderFileTreePicker(state);
  }
}

function showFileTreePicker(state) {
  if (!state) return;
  for (const other of fileTreePickerStates.values()) {
    if (other !== state) hideFileTreePicker(other);
  }
  state.picker.classList.remove('hidden');
  renderFileTreePicker(state);
}

function hideFileTreePicker(state) {
  state?.picker?.classList.add('hidden');
}

function selectFileTreePath(state, path) {
  const safe = safeJsonFileName(path);
  if (!safe) return;
  state.input.value = safe;
  state.input.dispatchEvent(new Event('input', { bubbles: true }));
  state.input.dispatchEvent(new Event('change', { bubbles: true }));
  hideFileTreePicker(state);
  updateViewDefMarkdownButtonState();
}

function renderFileTreePicker(state) {
  if (!state?.list) return;
  const names = uniqueNames(state.config.names());
  const query = String(state.input.value ?? '').trim();
  const filtered = filterFileTreeNames(names, query);
  const isFiltering = query.length > 0 && filtered.length !== names.length;

  state.list.innerHTML = '';

  if (!names.length) {
    const empty = document.createElement('div');
    empty.className = 'file-tree-empty';
    empty.textContent = state.config.inputId === 'defNameInput' && currentDataViewDefCandidateMode
      ? 'このData JSONにViewDef候補がありません'
      : '管理対象JSONが見つかりません';
    state.list.appendChild(empty);
    return;
  }

  if (!filtered.length) {
    const empty = document.createElement('div');
    empty.className = 'file-tree-empty';
    empty.textContent = `一致するJSONがありません: ${query}`;
    state.list.appendChild(empty);
    return;
  }

  const root = buildFileTree(filtered);
  renderFileTreeNode(state, root, state.list, '', 0, isFiltering);
}

function filterFileTreeNames(names, query) {
  const tokens = String(query ?? '')
    .trim()
    .toLowerCase()
    .split(/\s+/)
    .filter(Boolean);
  if (!tokens.length) return names;
  return names.filter(name => {
    const haystack = String(name).toLowerCase();
    return tokens.every(token => haystack.includes(token));
  });
}

function buildFileTree(paths) {
  const root = { name: '', path: '', folders: new Map(), files: [] };

  for (const raw of paths) {
    const path = safeJsonFileName(raw);
    if (!path) continue;
    const parts = path.split('/');
    let node = root;
    let currentPath = '';

    for (let i = 0; i < parts.length; i++) {
      const part = parts[i];
      const isFile = i === parts.length - 1;
      currentPath = currentPath ? `${currentPath}/${part}` : part;

      if (isFile) {
        node.files.push({ name: part, path });
      } else {
        if (!node.folders.has(part)) {
          node.folders.set(part, { name: part, path: currentPath, folders: new Map(), files: [] });
        }
        node = node.folders.get(part);
      }
    }
  }

  root.files.sort((a, b) => a.name.localeCompare(b.name));
  return root;
}

function displayFileTreeLabel(name, fallback='(no name)') {
  const text = String(name ?? '').trim();
  return text || fallback;
}

function renderFileTreeNode(state, node, parentEl, parentPath, depth, isFiltering) {
  const folders = [...node.folders.values()].sort((a, b) => a.name.localeCompare(b.name));

  for (const folder of folders) {
    const expanded = isFiltering || depth === 0 || state.expanded.has(folder.path);
    const row = document.createElement('button');
    row.type = 'button';
    row.className = 'file-tree-row file-tree-folder';
    row.style.setProperty('--depth', depth);
    row.innerHTML = `<span class="file-tree-twist">${expanded ? '▾' : '▸'}</span><span class="file-tree-icon">📁</span><span class="file-tree-label file-tree-folder-name"></span>`;
    row.querySelector('.file-tree-label').textContent = displayFileTreeLabel(folder.name, folder.path || '(folder)');
    row.addEventListener('click', (event) => {
      event.preventDefault();
      event.stopPropagation();
      if (state.expanded.has(folder.path)) state.expanded.delete(folder.path);
      else state.expanded.add(folder.path);
      renderFileTreePicker(state);
    });
    parentEl.appendChild(row);

    if (expanded) renderFileTreeNode(state, folder, parentEl, folder.path, depth + 1, isFiltering);
  }

  node.files.sort((a, b) => a.name.localeCompare(b.name));
  for (const file of node.files) {
    const row = document.createElement('button');
    row.type = 'button';
    row.className = 'file-tree-row file-tree-file';
    row.style.setProperty('--depth', depth);
    row.dataset.path = file.path;
    row.title = file.path;

    if (safeJsonFileName(state.input.value) === file.path) row.classList.add('selected');

    row.innerHTML = `<span class="file-tree-twist"></span><span class="file-tree-icon">📄</span><span class="file-tree-label file-tree-file-name"></span>`;
    row.querySelector('.file-tree-label').textContent = displayFileTreeLabel(file.name, file.path || '(file)');
    row.addEventListener('click', (event) => {
      event.preventDefault();
      event.stopPropagation();
      selectFileTreePath(state, file.path);
    });
    parentEl.appendChild(row);
  }
}
